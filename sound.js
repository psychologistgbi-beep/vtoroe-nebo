(() => {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  const PHI = (1 + Math.sqrt(5)) / 2;
  const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
  const profiles = {
    'self-organizing': { scale: [0, 2, 3, 7, 9], wave: 'triangle', bpm: 52, tone: 1.7, filter: 1550, overtone: 2.01 },
    analytic:          { scale: [0, 2, 5, 7, 11], wave: 'sine',     bpm: 46, tone: 2.3, filter: 2100, overtone: 2.5 },
    surface:           { scale: [0, 2, 4, 7, 9], wave: 'triangle', bpm: 42, tone: 2.8, filter: 1250, overtone: 1.5 },
    observer:          { scale: [0, 2, 5, 7, 10], wave: 'sine',    bpm: 48, tone: 2.1, filter: 1850, overtone: 2 },
    memory:            { scale: [0, 2, 3, 7, 8, 10], wave: 'triangle', bpm: 39, tone: 3.2, filter: 1150, overtone: 2.01 }
  };

  const PORTAL_PERFORMANCE_EVENTS = new Map([
    [5,  { actors: [55], strength: 0.72 }],
    [7,  { actors: [55], strength: 0.9 }],
    [9,  { actors: [42], strength: 0.64 }],
    [10, { actors: [34], strength: 0.62 }],
    [12, { actors: [21], strength: 0.6 }],
    [13, { actors: [13], strength: 0.58 }],
    [14, { actors: [8], strength: 0.56 }],
    [15, { actors: [3], strength: 0.54 }],
    [16, { actors: [2], strength: 0.52 }],
    [17, { actors: [1], strength: 0.5 }],
    [18, { actors: [63, 31], strength: 0.48 }],
    [20, { actors: [50, 37], strength: 0.52 }],
    [22, { actors: [60, 45], strength: 0.56 }],
    [24, { actors: [57, 40, 32], strength: 0.58 }],
    [26, { actors: [62, 49, 41], strength: 0.62, oculus: true }],
    [28, { actors: [64, 56, 48], strength: 0.54 }],
    [30, { actors: [59, 51, 43], strength: 0.4 }],
    [36, { actors: [1], strength: 0.46, coda: true }]
  ]);

  let context;
  let active;

  const reflectState = () => {
    document.documentElement.dataset.soundEngine = AudioContextClass ? 'ready' : 'unsupported';
    document.documentElement.dataset.soundPlayback = active ? (active.playing ? 'playing' : 'paused') : 'stopped';
    document.documentElement.dataset.soundContext = context?.state || 'uninitialized';
    if (active) {
      document.documentElement.dataset.soundWorld = active.key;
      document.documentElement.dataset.soundRule = active.rule;
      document.documentElement.dataset.soundBpm = String(Number(active.bpm.toFixed(2)));
      document.documentElement.dataset.soundScene = active.scene;
    } else {
      delete document.documentElement.dataset.soundWorld;
      delete document.documentElement.dataset.soundRule;
      delete document.documentElement.dataset.soundBpm;
      delete document.documentElement.dataset.soundScene;
      delete document.documentElement.dataset.soundBeat;
    }
  };

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const fract = value => value - Math.floor(value);
  const hash = value => {
    let result = 2166136261;
    for (let i = 0; i < value.length; i += 1) {
      result ^= value.charCodeAt(i);
      result = Math.imul(result, 16777619);
    }
    return result >>> 0;
  };
  const randomFrom = seed => {
    let state = seed >>> 0;
    return () => {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ value >>> 15, value | 1);
      value ^= value + Math.imul(value ^ value >>> 7, value | 61);
      return ((value ^ value >>> 14) >>> 0) / 4294967296;
    };
  };
  const popcount = value => {
    let n = value >>> 0;
    let count = 0;
    while (n) { n &= n - 1; count += 1; }
    return count;
  };
  const trailingZeros = value => {
    let n = Math.max(1, value | 0);
    let count = 0;
    while ((n & 1) === 0) { count += 1; n >>>= 1; }
    return count;
  };
  const midiToFrequency = midi => 440 * 2 ** ((midi - 69) / 12);
  const degreeToSemitones = (degree, scale) => {
    const octave = Math.floor(degree / scale.length);
    const index = ((degree % scale.length) + scale.length) % scale.length;
    return scale[index] + octave * 12;
  };

  const timing = world => {
    const profile = profiles[world.group] || profiles.analytic;
    const visualCycle = clamp(Number(world.visualCycle) || Number(world.speed) || 120, 36, 240);
    const beatCount = Math.max(24, Math.round(visualCycle * profile.bpm / 60));
    const bpm = beatCount * 60 / visualCycle;
    return { visualCycle, beatCount, bpm, beatSeconds: 60 / bpm };
  };

  const eventEnvelope = (elapsed, period, duration, offset) => {
    const phase = fract(elapsed / period + offset);
    if (phase > duration / period) return 0;
    return Math.sin(Math.PI * phase * period / duration) ** 2;
  };

  const rule30 = row => {
    const left = ((row << 1) | (row >>> 15)) & 0xffff;
    const right = ((row >>> 1) | ((row & 1) << 15)) & 0xffff;
    return (left ^ (row | right)) & 0xffff;
  };

  const nextPattern = session => {
    const { rule, profile } = session;
    const i = session.step;
    const length = profile.scale.length;
    let degrees = [];

    switch (rule) {
      case 'golden': {
        const address = Math.floor(fract(i / PHI) * length);
        degrees = [address + (Math.floor(i / length) % 2) * length];
        break;
      }
      case 'reaction': {
        const reaction = session.x * session.y * session.y;
        session.x = clamp(session.x + 0.18 * (0.055 * (1 - session.x) - reaction), 0.03, 0.97);
        session.y = clamp(session.y + 0.18 * (reaction - (0.055 + 0.062) * session.y), 0.03, 0.97);
        degrees = [Math.floor(session.x * length) + Math.floor(session.y * 3)];
        if (i % 4 === 2) degrees.push(Math.floor(session.y * length) - length);
        break;
      }
      case 'threshold': {
        const open = session.random() < 0.5927;
        if (open) {
          session.cluster += 1;
          degrees = [(session.cluster + popcount(session.cluster)) % (length * 2)];
        }
        break;
      }
      case 'flow': {
        const flow = Math.sin(i * 0.73 + session.phase) + Math.cos(i * 0.31 - session.phase);
        degrees = [Math.round((flow + 2) * 0.25 * (length * 2 - 1))];
        break;
      }
      case 'branch': {
        const depth = popcount(i + 1);
        degrees = [depth - 1];
        if (((i + 1) & i) === 0) degrees.push(depth + length - 1);
        break;
      }
      case 'chaos': {
        session.x = 3.91 * session.x * (1 - session.x);
        degrees = [Math.floor(session.x * length * 2) - 2];
        break;
      }
      case 'automaton': {
        const sounding = (session.row & 1) === 1;
        if (sounding) degrees = [popcount(session.row) % (length * 2)];
        session.row = rule30(session.row);
        break;
      }
      case 'critical': {
        const boundaries = popcount((session.row ^ (session.row >>> 1)) & 0xffff);
        if (boundaries % 3 !== 0) degrees = [boundaries % (length * 2) - 2];
        session.row = ((session.row << 1) ^ (session.random() * 0xffff | 0) ^ (session.row >>> 2)) & 0xffff;
        break;
      }
      case 'radial': {
        const radius = Math.abs(Math.sin(i * 0.61));
        degrees = [Math.round(radius * (length * 2 - 1)) - length];
        if (i % 5 === 0) degrees.push(0);
        break;
      }
      case 'modes':
        degrees = [(i * 7) % (length * 2), (i * 3) % (length * 2) - length];
        break;
      case 'recursive': {
        const depth = popcount(i + 1);
        degrees = [depth, depth + (i % 3 === 0 ? length : 0)];
        break;
      }
      case 'mirror': {
        const degree = (i * 3 + session.seed) % length;
        degrees = [degree, length - 1 - degree];
        break;
      }
      case 'causal': {
        if (i % 3 !== 2) degrees = [(i + Math.floor(i / 3) * 2) % (length * 2) - 2];
        break;
      }
      case 'phase': {
        const a = i % length;
        const b = Math.floor(i * Math.SQRT2 + session.phase) % length;
        degrees = a === b ? [a, b + length] : [a - length, b];
        break;
      }
      case 'load': {
        const level = trailingZeros(i + 1);
        degrees = [length - level - 1 - length];
        if (level > 2) degrees.push(0);
        break;
      }
      case 'equal':
        degrees = [i % length];
        break;
      case 'conformal': {
        const register = Math.floor((i % 12) / 4) - 1;
        degrees = [(i % length) + register * length];
        break;
      }
      case 'tiers': {
        const counts = [4, 8, 16, 32];
        const tier = Math.floor(i / 4) % counts.length;
        degrees = [(i % counts[tier]) % length + tier];
        if (i % 8 === 0) degrees.push(tier - length);
        break;
      }
      case 'parallax':
        degrees = [i % length - length, (i + 2) % length, (i + 4) % length + length];
        break;
      case 'linked':
        degrees = [(i * 2) % (length + 2) - 2, (i * 3 + 1) % (length + 3) - length];
        break;
      case 'triad': {
        const sun = i % 3;
        degrees = [sun * 2 - length, sun * 2, sun * 2 + length];
        break;
      }
      case 'relations': {
        const a = (i * 3 + session.seed) % 15 + 1;
        const b = (i * 7 + session.seed) % 15 + 1;
        const relation = popcount(a & b) + Math.abs(a - b);
        degrees = [a % length - length, relation % length];
        break;
      }
      case 'interference': {
        const sum = Math.sin(i * 0.67) + Math.sin(i * 0.43 + session.phase);
        if (Math.abs(sum) > 0.28) degrees = [Math.round((sum + 2) * 0.25 * length * 2) - length];
        break;
      }
      case 'boundary': {
        const distance = Math.abs((i % 10) - 5);
        degrees = [i % 2 === 0 ? -distance : distance];
        if (distance === 0) degrees.push(0);
        break;
      }
      case 'registers':
        degrees = [(i % 7) - length, (i % 7 === 0) ? length : 0];
        break;
      case 'procession':
        degrees = [(i * 2) % (length + 1) - length, (i * 3 + 2) % (length + 2)];
        break;
      case 'cells': {
        const ring = i % 10 + 1;
        const cellCount = 4 + ring * 2;
        degrees = [(i % cellCount) % length + Math.floor(ring / 4)];
        break;
      }
      case 'rings': {
        const ring = i % 11;
        const returning = Math.floor(i / 11) % 2;
        degrees = [ring % length + returning * length];
        break;
      }
      default:
        degrees = [i % length];
    }

    const elapsed = i * session.beatSeconds;
    if (session.scene === 'ascent' && i % 4 === 3) {
      degrees.push(length + Math.floor(i / 4) % (length + 1));
    } else if (session.scene === 'rain') {
      const rain = eventEnvelope(elapsed, session.scenePeriod || 39, session.sceneSulfur ? 13 : 9, 0.08);
      if (rain > 0.2 && i % 2 === 0) degrees.push(length + (i % length));
    } else if (session.scene === 'storm') {
      const storm = eventEnvelope(elapsed, session.scenePeriod || 38, session.sceneFierce ? 11 : 7, 0.24);
      if (storm > 0.52 && i % 4 === 0) degrees.push(-length, length + 1, length + 3);
    }

    session.step += 1;
    return degrees;
  };

  const resetPattern = (session, targetStep = 0) => {
    session.random = randomFrom(session.seed);
    session.x = 0.25 + session.random() * 0.45;
    session.y = 0.18 + session.random() * 0.34;
    session.row = (session.seed | 1) & 0xffff;
    session.phase = session.random() * Math.PI * 2;
    session.cluster = 0;
    session.step = 0;
    if (session.scene === 'source-performance') {
      session.step = targetStep;
      return;
    }
    for (let step = 0; step < targetStep; step += 1) nextPattern(session);
  };

  const ensureContext = () => {
    if (!AudioContextClass) return null;
    if (!context) {
      context = new AudioContextClass();
      context.onstatechange = reflectState;
    }
    return context;
  };

  const makeImpulse = (audioContext, seed) => {
    const duration = 3.4;
    const length = Math.floor(audioContext.sampleRate * duration);
    const buffer = audioContext.createBuffer(2, length, audioContext.sampleRate);
    const random = randomFrom(seed ^ 0x9e3779b9);
    for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
      const data = buffer.getChannelData(channel);
      for (let i = 0; i < length; i += 1) {
        const envelope = (1 - i / length) ** 2.8;
        data[i] = (random() * 2 - 1) * envelope;
      }
    }
    return buffer;
  };

  const releaseSession = (fade = 0.5) => {
    if (!active || !context) return;
    const old = active;
    active = null;
    reflectState();
    window.clearTimeout(old.timer);
    const now = context.currentTime;
    old.master.gain.cancelScheduledValues(now);
    old.master.gain.setTargetAtTime(0.0001, now, Math.max(0.02, fade / 4));
    window.setTimeout(() => {
      old.longNodes.forEach(node => {
        try { if (typeof node.stop === 'function') node.stop(); } catch (_) {}
        try { node.disconnect(); } catch (_) {}
      });
    }, fade * 1000 + 180);
  };

  const addVoice = (session, degree, voiceIndex, degreeCount, startTime) => {
    if (!active || active !== session || !context) return;
    const now = Math.max(context.currentTime + 0.012, startTime || context.currentTime + 0.045);
    const semitones = degreeToSemitones(degree, session.profile.scale);
    const frequency = midiToFrequency(session.rootMidi + semitones);
    const duration = session.beatSeconds * session.profile.tone;
    const level = 0.055 / Math.sqrt(Math.max(1, degreeCount));
    const voiceGain = context.createGain();
    const voiceFilter = context.createBiquadFilter();
    const dryPanner = context.createStereoPanner ? context.createStereoPanner() : context.createGain();
    const oscillator = context.createOscillator();
    const overtone = context.createOscillator();

    oscillator.type = session.profile.wave;
    oscillator.frequency.setValueAtTime(frequency, now);
    overtone.type = 'sine';
    overtone.frequency.setValueAtTime(frequency * session.profile.overtone, now);
    overtone.detune.setValueAtTime((session.random() - 0.5) * 7, now);
    voiceFilter.type = 'lowpass';
    voiceFilter.frequency.setValueAtTime(session.profile.filter + session.random() * 420, now);
    voiceFilter.Q.setValueAtTime(0.7, now);
    if ('pan' in dryPanner) {
      dryPanner.pan.setValueAtTime(clamp(((voiceIndex + 1) / (degreeCount + 1)) * 1.6 - 0.8, -0.8, 0.8), now);
    }

    voiceGain.gain.setValueAtTime(0.0001, now);
    voiceGain.gain.exponentialRampToValueAtTime(level, now + 0.12);
    voiceGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    oscillator.connect(voiceGain);
    overtone.connect(voiceGain);
    voiceGain.connect(voiceFilter);
    voiceFilter.connect(dryPanner);
    dryPanner.connect(session.master);
    dryPanner.connect(session.convolver);
    oscillator.start(now);
    overtone.start(now);
    oscillator.stop(now + duration + 0.08);
    overtone.stop(now + duration + 0.08);
  };

  const noiseBuffer = (duration, seed) => {
    const length = Math.max(1, Math.floor(context.sampleRate * duration));
    const buffer = context.createBuffer(1, length, context.sampleRate);
    const data = buffer.getChannelData(0);
    const random = randomFrom(seed >>> 0);
    let memory = 0;
    for (let index = 0; index < length; index += 1) {
      memory = memory * 0.82 + (random() * 2 - 1) * 0.18;
      data[index] = memory;
    }
    return buffer;
  };

  const sourceActorPan = (session, actor) => {
    const count = Math.max(1, session.sceneActorCount || 64);
    const radius = 0.9 * Math.sqrt(actor / count);
    const angle = actor * GOLDEN_ANGLE + (session.sceneActorSpin || 0);
    return clamp(radius * Math.cos(angle), -0.88, 0.88);
  };

  const addSourceActorGesture = (session, actor, startTime, strength = 0.6, coda = false) => {
    if (!active || active !== session || !context) return;
    const now = Math.max(context.currentTime + 0.012, startTime);
    const plane = actor / Math.max(1, session.sceneActorCount || 64);
    const duration = coda ? 1.65 : 0.58 + plane * 0.72;
    const air = context.createBufferSource();
    const airFilter = context.createBiquadFilter();
    const airGain = context.createGain();
    const body = context.createOscillator();
    const bodyGain = context.createGain();
    const panner = context.createStereoPanner ? context.createStereoPanner() : context.createGain();

    air.buffer = noiseBuffer(duration + 0.08, session.seed ^ (actor * 2654435761) ^ session.step);
    airFilter.type = 'bandpass';
    airFilter.frequency.setValueAtTime(190 + plane * 690, now);
    airFilter.Q.setValueAtTime(2.6 + (1 - plane) * 1.7, now);
    body.type = 'sine';
    body.frequency.setValueAtTime(36 + plane * 61, now);
    body.frequency.exponentialRampToValueAtTime(31 + plane * 47, now + duration);
    if ('pan' in panner) panner.pan.setValueAtTime(sourceActorPan(session, actor), now);

    const airLevel = 0.022 * strength;
    airGain.gain.setValueAtTime(0.0001, now);
    airGain.gain.exponentialRampToValueAtTime(airLevel, now + 0.035);
    airGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    bodyGain.gain.setValueAtTime(0.0001, now);
    bodyGain.gain.exponentialRampToValueAtTime(0.011 * strength, now + 0.06);
    bodyGain.gain.exponentialRampToValueAtTime(0.0001, now + duration * 0.82);

    air.connect(airFilter);
    airFilter.connect(airGain);
    airGain.connect(panner);
    body.connect(bodyGain);
    bodyGain.connect(panner);
    panner.connect(session.master);
    panner.connect(session.convolver);
    air.start(now);
    body.start(now);
    air.stop(now + duration + 0.1);
    body.stop(now + duration + 0.1);
  };

  const addSourceOculus = (session, startTime) => {
    if (!active || active !== session || !context) return;
    const now = Math.max(context.currentTime + 0.012, startTime);
    const duration = 6.4;
    const bus = context.createGain();
    const filter = context.createBiquadFilter();
    const first = context.createOscillator();
    const second = context.createOscillator();
    first.type = 'sine';
    second.type = 'sine';
    first.frequency.setValueAtTime(41.2, now);
    second.frequency.setValueAtTime(42.7, now);
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(260, now);
    filter.Q.setValueAtTime(1.1, now);
    bus.gain.setValueAtTime(0.0001, now);
    bus.gain.exponentialRampToValueAtTime(0.027, now + 1.4);
    bus.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    first.connect(bus);
    second.connect(bus);
    bus.connect(filter);
    filter.connect(session.master);
    filter.connect(session.convolver);
    first.start(now);
    second.start(now);
    first.stop(now + duration + 0.1);
    second.stop(now + duration + 0.1);
  };

  const addArchitecturalGesture = (session, event, startTime) => {
    if (!active || active !== session || !context) return;
    const now = Math.max(context.currentTime + 0.012, startTime);
    const mode = session.sceneMode;
    const settings = {
      2: { duration: 1.8, noise: 115, body: 31, q: 1.2 },
      4: { duration: 0.64, noise: 1450, body: 238, q: 4.8 },
      5: { duration: 1.15, noise: 520, body: 78, q: 3.2 },
      6: { duration: 1.42, noise: 330, body: 55, q: 2.4 }
    }[mode] || { duration: 1.1, noise: 240, body: 48, q: 2 };
    const duration = settings.duration * (event.long ? 1.8 : 1);
    const air = context.createBufferSource();
    const airFilter = context.createBiquadFilter();
    const airGain = context.createGain();
    const body = context.createOscillator();
    const bodyGain = context.createGain();
    const panner = context.createStereoPanner ? context.createStereoPanner() : context.createGain();
    air.buffer = noiseBuffer(duration + 0.08, session.seed ^ (session.step * 2246822519));
    airFilter.type = 'bandpass';
    airFilter.frequency.setValueAtTime(settings.noise * (0.88 + event.strength * 0.24), now);
    airFilter.Q.setValueAtTime(settings.q, now);
    body.type = 'sine';
    body.frequency.setValueAtTime(settings.body * (0.94 + event.strength * 0.15), now);
    body.frequency.exponentialRampToValueAtTime(settings.body * 0.82, now + duration);
    if ('pan' in panner) panner.pan.setValueAtTime(event.pan || 0, now);
    airGain.gain.setValueAtTime(0.0001, now);
    airGain.gain.exponentialRampToValueAtTime(0.019 * event.strength, now + 0.035);
    airGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    bodyGain.gain.setValueAtTime(0.0001, now);
    bodyGain.gain.exponentialRampToValueAtTime(0.009 * event.strength, now + 0.08);
    bodyGain.gain.exponentialRampToValueAtTime(0.0001, now + duration * 0.88);
    air.connect(airFilter);
    airFilter.connect(airGain);
    airGain.connect(panner);
    body.connect(bodyGain);
    bodyGain.connect(panner);
    panner.connect(session.master);
    panner.connect(session.convolver);
    air.start(now);
    body.start(now);
    air.stop(now + duration + 0.1);
    body.stop(now + duration + 0.1);
  };

  const sourceBedLevel = (session, phase) => {
    switch (session.sceneMode) {
      case 1:
        if (phase < 8) return 0.007;
        if (phase < 58) return 0.014 + phase / 58 * 0.018;
        if (phase < 66) return 0.019;
        return 0.004;
      case 2:
        if (phase < 10) return 0.006;
        if (phase < 40) return 0.018 + (phase - 10) / 30 * 0.017;
        if (phase < 54) return 0.032;
        if (phase < 62) return 0.009;
        return 0.003;
      case 3:
        if (phase < 7) return 0.012;
        if (phase < 25) return 0.012 + (phase - 7) / 18 * 0.012;
        if (phase < 40) return 0.024 + (phase - 25) / 15 * 0.012;
        if (phase < 48) return 0.036 + (phase - 40) / 8 * 0.012;
        if (phase < 55) return 0.0001;
        return 0.009 * (1 - (phase - 55) / 5);
      case 4:
        if (phase < 8) return 0.005;
        if (phase < 52) return 0.015 + (phase - 8) / 44 * 0.018;
        if (phase < 60) return 0.0001;
        return 0.006;
      case 5:
        if (phase < 9) return 0.004;
        if (phase < 56) return 0.014 + (phase - 9) / 47 * 0.02;
        if (phase < 65) return 0.0001;
        return 0.006;
      case 6:
        if (phase < 8) return 0.004;
        if (phase < 52) return 0.014 + (phase - 8) / 44 * 0.016;
        if (phase < 62) return 0.01;
        return 0.0001;
      default:
        return 0.01;
    }
  };

  const addSourceBed = session => {
    const bus = context.createGain();
    const filter = context.createBiquadFilter();
    const first = context.createOscillator();
    const second = context.createOscillator();
    const air = context.createBufferSource();
    first.type = 'sine';
    second.type = 'sine';
    const roots = {
      1: [29.1, 43.6],
      2: [23.4, 37.2],
      3: [32.7, 49.1],
      4: [54.0, 81.3],
      5: [31.4, 46.2],
      6: [45.2, 67.6]
    }[session.sceneMode] || [32.7, 49.1];
    first.frequency.setValueAtTime(roots[0], context.currentTime);
    second.frequency.setValueAtTime(roots[1], context.currentTime);
    first.detune.setValueAtTime(-4, context.currentTime);
    second.detune.setValueAtTime(3, context.currentTime);
    air.buffer = noiseBuffer(2.7, session.seed ^ 0x51f15e);
    air.loop = true;
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(session.sceneMode === 4 ? 540 : 132, context.currentTime);
    filter.Q.setValueAtTime(0.8, context.currentTime);
    bus.gain.setValueAtTime(0.0001, context.currentTime);
    first.connect(bus);
    second.connect(bus);
    air.connect(filter);
    filter.connect(bus);
    bus.connect(session.master);
    bus.connect(session.convolver);
    first.start();
    second.start();
    air.start();
    session.sourceBed = bus;
    session.sourceBedFilter = filter;
    session.longNodes.push(first, second, air, bus, filter);
  };

  const sourceEventMap = session => {
    const map = new Map();
    const add = (seconds, event) => {
      const beat = Math.round(seconds / session.beatSeconds) % session.beatCount;
      if (!map.has(beat)) map.set(beat, []);
      map.get(beat).push(event);
    };
    if (session.sceneMode === 1) {
      [[8,84],[13,79],[20,67],[25,55],[30,43],[35,31],[42,72],[46,58],[50,44],[54,26],[58,12],[66,1]]
        .forEach(([seconds, actor], index) => add(seconds, { actor, strength: 0.48 + index * 0.025, coda: seconds === 66 }));
      add(58, { oculus: true });
    } else if (session.sceneMode === 3) {
      PORTAL_PERFORMANCE_EVENTS.forEach((event, beat) => map.set(beat, [{ ...event, portal: true }]));
    } else {
      const times = {
        2: [10, 16, 24, 30, 36, 40, 46, 54, 62],
        4: [8, 13, 20, 27, 34, 42, 47, 52, 60],
        5: [9, 15, 22, 28, 35, 43, 49, 56, 65],
        6: [8, 14, 20, 27, 34, 40, 46, 52, 58, 62]
      }[session.sceneMode] || [];
      times.forEach((seconds, index) => add(seconds, {
        strength: 0.42 + (index % 5) * 0.08,
        pan: clamp(Math.sin(index * GOLDEN_ANGLE) * 0.78, -0.82, 0.82),
        long: index === Math.floor(times.length * 0.55)
      }));
    }
    return map;
  };

  const scheduleSourcePerformance = (session, at) => {
    const beat = session.step % session.beatCount;
    const events = session.sourceEvents.get(beat) || [];
    events.forEach(event => {
      if (event.portal) {
        event.actors.forEach((actor, index) => addSourceActorGesture(session, actor, at + index * 0.075, event.strength, event.coda));
        if (event.oculus) addSourceOculus(session, at + 0.18);
      } else if (event.actor) addSourceActorGesture(session, event.actor, at, event.strength, event.coda);
      else if (event.oculus) addSourceOculus(session, at);
      else addArchitecturalGesture(session, event, at);
    });
    session.step += 1;
  };

  const schedule = session => {
    if (!active || active !== session) return;
    if (!session.playing || context.state !== 'running') {
      session.timer = window.setTimeout(() => schedule(session), 80);
      return;
    }
    const horizon = context.currentTime + 0.16;
    while (session.nextNoteTime < horizon) {
      if (session.scene === 'source-performance') {
        scheduleSourcePerformance(session, session.nextNoteTime);
      } else {
        const degrees = nextPattern(session);
        const scenePhase = session.step * session.beatSeconds;
        if (session.scene === 'breath') {
          const openness = 0.5 + 0.5 * Math.sin(scenePhase * Math.PI / (session.sceneDeep ? 8 : 6));
          session.filter.frequency.setValueAtTime(session.profile.filter * (0.72 + openness * 0.78), session.nextNoteTime);
        }
        degrees.forEach((degree, index) => addVoice(session, degree, index, degrees.length, session.nextNoteTime));
      }
      session.nextNoteTime += session.beatSeconds;
    }
    if (session.sourceBed) {
      const phase = fract((performance.now() - session.epoch) / 1000 / session.visualCycle) * session.visualCycle;
      const level = sourceBedLevel(session, phase);
      session.sourceBed.gain.setTargetAtTime(level, context.currentTime, level < 0.001 ? 0.12 : 0.45);
      session.sourceBedFilter.frequency.setTargetAtTime((session.sceneMode === 4 ? 420 : 112) + level * 1900, context.currentTime, 0.55);
    }
    document.documentElement.dataset.soundBeat = String(session.step);
    session.timer = window.setTimeout(() => schedule(session), 40);
  };

  const addDrone = session => {
    const frequencies = [midiToFrequency(session.rootMidi - 12), midiToFrequency(session.rootMidi - 5)];
    frequencies.forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = index ? 'sine' : session.profile.wave;
      oscillator.frequency.setValueAtTime(frequency, context.currentTime);
      oscillator.detune.setValueAtTime(index ? 3 : -3, context.currentTime);
      gain.gain.setValueAtTime(index ? 0.010 : 0.014, context.currentTime);
      oscillator.connect(gain);
      gain.connect(session.master);
      gain.connect(session.convolver);
      oscillator.start();
      session.longNodes.push(oscillator, gain);
    });
  };

  const play = world => {
    const audioContext = ensureContext();
    if (!audioContext) return Promise.resolve(false);
    releaseSession(0.12);
    const resumeRequest = audioContext.resume().catch(() => false);

    const seed = hash(world.key);
    const profile = profiles[world.group] || profiles.analytic;
    const clock = timing(world);
    const { visualCycle, beatCount: targetBeats, bpm, beatSeconds } = clock;
    const epoch = Number.isFinite(Number(world.epoch)) ? Number(world.epoch) : performance.now();
    const elapsedAtStart = Math.max(0, (performance.now() - epoch) / 1000);
    const targetStep = Math.floor(elapsedAtStart / beatSeconds);
    const beatRemainder = elapsedAtStart % beatSeconds;
    const random = randomFrom(seed);
    const master = audioContext.createGain();
    const filter = audioContext.createBiquadFilter();
    const compressor = audioContext.createDynamicsCompressor();
    const convolver = audioContext.createConvolver();
    const wet = audioContext.createGain();

    master.gain.setValueAtTime(0.0001, audioContext.currentTime);
    master.gain.exponentialRampToValueAtTime(0.16, audioContext.currentTime + 0.8);
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(profile.filter * 1.35, audioContext.currentTime);
    compressor.threshold.setValueAtTime(-26, audioContext.currentTime);
    compressor.knee.setValueAtTime(18, audioContext.currentTime);
    compressor.ratio.setValueAtTime(4, audioContext.currentTime);
    compressor.attack.setValueAtTime(0.035, audioContext.currentTime);
    compressor.release.setValueAtTime(0.55, audioContext.currentTime);
    convolver.buffer = makeImpulse(audioContext, seed);
    wet.gain.setValueAtTime(0.22, audioContext.currentTime);

    master.connect(filter);
    filter.connect(compressor);
    compressor.connect(audioContext.destination);
    convolver.connect(wet);
    wet.connect(filter);

    active = {
      key: world.key,
      rule: world.soundRule || 'golden',
      profile,
      seed,
      random,
      master,
      convolver,
      wet,
      filter,
      compressor,
      visualCycle,
      beatCount: targetBeats,
      bpm,
      beatSeconds,
      epoch,
      scene: world.scene || 'wave',
      sceneMode: Number(world.sceneMode) || 0,
      sceneActorCount: Number(world.sceneActorCount) || 0,
      sceneActorSpin: Number(world.sceneActorSpin) || 0,
      scenePeriod: Number(world.scenePeriod) || 0,
      sceneSulfur: Boolean(world.sceneSulfur),
      sceneFierce: Boolean(world.sceneFierce),
      sceneDeep: Boolean(world.sceneDeep),
      rootMidi: 39 + seed % 8,
      step: 0,
      x: 0.25 + random() * 0.45,
      y: 0.18 + random() * 0.34,
      row: (seed | 1) & 0xffff,
      phase: random() * Math.PI * 2,
      cluster: 0,
      playing: true,
      timer: null,
      nextNoteTime: audioContext.currentTime + (elapsedAtStart < 0.14 ? 0.055 : Math.max(0.045, beatSeconds - beatRemainder)),
      longNodes: [master, convolver, wet, filter, compressor]
    };

    active.sourceEvents = active.scene === 'source-performance' ? sourceEventMap(active) : new Map();
    resetPattern(active, targetStep);
    if (active.scene === 'source-performance') addSourceBed(active);
    else addDrone(active);
    schedule(active);
    reflectState();
    resumeRequest.then(reflectState);
    return Promise.race([
      resumeRequest,
      new Promise(resolve => window.setTimeout(resolve, 180))
    ]).then(() => {
      if (audioContext.state === 'running') return 'playing';
      if (active) {
        active.playing = false;
        active.master.gain.setTargetAtTime(0.0001, audioContext.currentTime, 0.05);
        reflectState();
      }
      return 'ready';
    });
  };

  const toggle = () => {
    if (!active || !context) return false;
    active.playing = !active.playing;
    const now = context.currentTime;
    active.master.gain.cancelScheduledValues(now);
    active.master.gain.setTargetAtTime(active.playing ? 0.16 : 0.0001, now, active.playing ? 0.18 : 0.08);
    if (active.playing) {
      const elapsed = Math.max(0, (performance.now() - active.epoch) / 1000);
      const remainder = elapsed % active.beatSeconds;
      resetPattern(active, Math.floor(elapsed / active.beatSeconds));
      active.nextNoteTime = now + Math.max(0.045, active.beatSeconds - remainder);
      if (context.state === 'suspended') context.resume().catch(() => {});
    }
    reflectState();
    return active.playing;
  };

  const stop = () => releaseSession(0.65);
  const state = () => active ? {
    supported: true,
    context: context?.state,
    key: active.key,
    rule: active.rule,
    playing: active.playing,
    bpm: Number(active.bpm.toFixed(2)),
    visualCycle: active.visualCycle,
    beatCount: active.beatCount,
    step: active.step,
    scene: active.scene,
    sceneMode: active.sceneMode,
    epoch: active.epoch
  } : { supported: Boolean(AudioContextClass), playing: false };

  window.WorldSound = { play, toggle, stop, state, timing };
  reflectState();
})();
