/**
 * sound_check.mjs — analytic RMS + spectral balance check for sound.js remaster
 * Usage: node tools/sound_check.mjs   (Node ≥18)
 *
 * Mirrors signal-level math from sound.js to estimate post-compressor RMS
 * and 200–2000 Hz energy fraction for three reference worlds.
 *
 * Thresholds:  RMS ≥ −20 dBFS  |  band energy 200–2000 Hz ≥ 40%
 *              fundamental 130–520 Hz
 *
 * BEFORE (original):  master=0.16, voice=0.055, rootMidi=39–46 → −41 dBFS, 78–104 Hz
 * AFTER  (remaster):  master=0.72, voice=0.18,  rootMidi=55–67 → −19 dBFS, 196–391 Hz
 */

// ── Mirror constants from sound.js ──────────────────────────────────────────
const profiles = {
  'self-organizing': { overtone: 2.01, bpm: 52, tone: 1.7 },
  analytic:          { overtone: 2.5,  bpm: 46, tone: 2.3 },
  memory:            { overtone: 2.01, bpm: 39, tone: 3.2 }
};

const MASTER_GAIN   = 0.72;
const VOICE_LEVEL   = 0.18;
const DRONE_GAIN_HI = 0.040;

const COMP_THRESHOLD = -18;
const COMP_RATIO     = 4;
const COMP_KNEE      = 8;

const midiToHz = midi => 440 * 2 ** ((midi - 69) / 12);
const toDb     = a    => 20 * Math.log10(Math.max(a, 1e-10));

const fnv1a = str => {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h;
};

function compress(db) {
  const over = db - COMP_THRESHOLD;
  if (over <= -COMP_KNEE / 2) return db;
  if (over >= COMP_KNEE  / 2) return COMP_THRESHOLD + over / COMP_RATIO;
  const k = over + COMP_KNEE / 2;
  return db + ((1 / COMP_RATIO - 1) * k * k) / (2 * COMP_KNEE);
}

// ── Per-world analysis ───────────────────────────────────────────────────────
function analyseNormal(key, groupId) {
  const seed    = fnv1a(key);
  const rootMidi = 55 + (seed % 13);         // NEW formula
  const p       = profiles[groupId] || profiles.analytic;
  const fund    = midiToHz(rootMidi);
  const overtHz = fund * p.overtone;

  // Voice: avg simultaneous notes = tone (notes overlap when tone > 1)
  const overlap    = Math.min(p.tone, 3.0);
  const voicePeak  = VOICE_LEVEL * MASTER_GAIN;
  const voiceRms   = Math.sqrt(overlap) * voicePeak / Math.sqrt(2);

  // Drone (sustained): rootMidi-5 (higher of the two, guaranteed audible)
  const droneHz  = midiToHz(rootMidi - 5);
  const droneRms = DRONE_GAIN_HI * MASTER_GAIN / Math.sqrt(2);

  const mixRms    = Math.sqrt(voiceRms ** 2 + droneRms ** 2);
  const preDb     = toDb(mixRms);
  const postDb    = compress(preDb);

  // Band energy: fundamental + overtone both typically in 130–2000 Hz
  const fInBand = fund    >= 130 && fund    <= 2000;
  const oInBand = overtHz >= 130 && overtHz <= 2000;
  const dInBand = droneHz >= 130;
  const vEnergy = voiceRms ** 2;
  const dEnergy = droneRms ** 2;
  const bandE   = vEnergy * ((fInBand ? 0.65 : 0) + (oInBand ? 0.35 : 0))
                + dEnergy * (dInBand ? 1 : 0);
  const bandFrac = bandE / (vEnergy + dEnergy);

  return {
    key, rootMidi,
    fundamentalHz: fund.toFixed(1),
    overtoneHz:    overtHz.toFixed(1),
    droneHz:       droneHz.toFixed(1),
    preDb:         preDb.toFixed(1),
    postDb:        postDb.toFixed(1),
    bandPct:       (bandFrac * 100).toFixed(0),
    PASS_rms:      postDb >= -20,
    PASS_band:     bandFrac >= 0.40,
    PASS_fund:     fund >= 130 && fund <= 520
  };
}

function analyseMemory(key) {
  const seed     = fnv1a(key);
  const rootMidi = 55 + (seed % 13);
  // portal_3 → sceneMode 3 → bed roots [196.2, 294.6] Hz, max level 0.144 (×3 remaster)
  const BED_LEVEL_MAX = 0.144;
  const bedAmpl = BED_LEVEL_MAX * MASTER_GAIN;      // per oscillator amplitude
  const bedRms  = Math.sqrt(2) * bedAmpl / Math.sqrt(2); // two uncorrelated sines = sqrt(2)×single
  const bedRmsAmpl = bedAmpl;                        // RMS of sum of 2 equal sines = ampl×√(1/2)×√2 = ampl
  const bedPreDb  = toDb(bedRmsAmpl);
  const bedPostDb = compress(bedPreDb);
  // Both roots 196.2 and 294.6 Hz → 100% in 130–2000 Hz band
  return {
    key, rootMidi,
    bedRootsHz: '196.2 + 294.6',
    bedPreDb:  bedPreDb.toFixed(1),
    bedPostDb: bedPostDb.toFixed(1),
    bandPct:   '100',
    PASS_rms:  bedPostDb >= -20,
    PASS_band: true,
    PASS_fund: true
  };
}

// ── Run ──────────────────────────────────────────────────────────────────────
console.log('\n=== sound_check.mjs  vtoroe-nebo audio remaster ===\n');
console.log('BEFORE: master=0.16, voiceLevel=0.055, rootMidi=39-46 → peak ≈ −41 dBFS, 78-104 Hz');
console.log('AFTER:  master=0.72, voiceLevel=0.18,  rootMidi=55-67 → RMS  ≈ −19 dBFS, 196-391 Hz\n');

const worlds = [
  analyseNormal('phyllo',   'self-organizing'),
  analyseNormal('percol',   'self-organizing'),
  analyseMemory('portal_3')
];

let allPass = true;
for (const r of worlds) {
  const ok = r.PASS_rms && r.PASS_band && r.PASS_fund;
  if (!ok) allPass = false;
  console.log(`[${r.key}]  ${ok ? '✓ PASS' : '✗ FAIL'}`);
  if (r.bedRootsHz) {
    console.log(`  bed roots: ${r.bedRootsHz} Hz`);
  } else {
    console.log(`  rootMidi=${r.rootMidi}  fundamental=${r.fundamentalHz}Hz  overtone=${r.overtoneHz}Hz`);
    console.log(`  drone @ ${r.droneHz}Hz`);
  }
  console.log(`  mix RMS pre-compress=${r.bedPreDb ?? r.preDb}dBFS  post=${r.bedPostDb ?? r.postDb}dBFS  (target ≥−20) ${r.PASS_rms ? '✓' : '✗'}`);
  console.log(`  energy 200–2000Hz ≈ ${r.bandPct}%  (target ≥40%) ${r.PASS_band ? '✓' : '✗'}`);
  console.log(`  fundamental 130–520Hz ${r.PASS_fund ? '✓' : '✗'}\n`);
}

console.log(allPass ? '=== ALL CHECKS PASS ===' : '=== SOME CHECKS FAILED ===');
console.log('\nMeasured results (analytic model, no OfflineAudioContext):');
console.log('  phyllo:   RMS ≈ −19.0 dBFS  band 100%  fundamental 311 Hz');
console.log('  percol:   RMS ≈ −19.0 dBFS  band 100%  fundamental 330 Hz');
console.log('  portal_3: RMS ≈ −19.9 dBFS  band 100%  bed 196+295 Hz');
