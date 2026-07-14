(() => {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  const PHI = (1 + Math.sqrt(5)) / 2;
  const profiles = {
    'self-organizing': { scale: [0, 2, 3, 7, 9], wave: 'triangle', bpm: 52, tone: 1.7, filter: 1550, overtone: 2.01 },
    analytic:          { scale: [0, 2, 5, 7, 11], wave: 'sine',     bpm: 46, tone: 2.3, filter: 2100, overtone: 2.5 },
    surface:           { scale: [0, 2, 4, 7, 9], wave: 'triangle', bpm: 42, tone: 2.8, filter: 1250, overtone: 1.5 },
    observer:          { scale: [0, 2, 5, 7, 10], wave: 'sine',    bpm: 48, tone: 2.1, filter: 1850, overtone: 2 },
    memory:            { scale: [0, 2, 3, 7, 8, 10], wave: 'triangle', bpm: 39, tone: 3.2, filter: 1150, overtone: 2.01 }
  };

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
    } else {
      delete document.documentElement.dataset.soundWorld;
      delete document.documentElement.dataset.soundRule;
      delete document.documentElement.dataset.soundBpm;
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

    session.step += 1;
    return degrees;
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

  const addVoice = (session, degree, voiceIndex, degreeCount) => {
    if (!active || active !== session || !context) return;
    const now = context.currentTime + 0.045;
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

  const schedule = session => {
    if (!active || active !== session) return;
    if (!session.playing || context.state !== 'running') {
      session.timer = window.setTimeout(() => schedule(session), 160);
      return;
    }
    const degrees = nextPattern(session);
    degrees.forEach((degree, index) => addVoice(session, degree, index, degrees.length));
    session.timer = window.setTimeout(() => schedule(session), session.beatSeconds * 1000);
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
    const visualCycle = clamp(Number(world.visualCycle) || Number(world.speed) || 120, 36, 240);
    const targetBeats = Math.max(24, Math.round(visualCycle * profile.bpm / 60));
    const bpm = targetBeats * 60 / visualCycle;
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
      beatSeconds: 60 / bpm,
      rootMidi: 39 + seed % 8,
      step: 0,
      x: 0.25 + random() * 0.45,
      y: 0.18 + random() * 0.34,
      row: (seed | 1) & 0xffff,
      phase: random() * Math.PI * 2,
      cluster: 0,
      playing: true,
      timer: null,
      longNodes: [master, convolver, wet, filter, compressor]
    };

    addDrone(active);
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
    if (active.playing && context.state === 'suspended') context.resume().catch(() => {});
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
    step: active.step
  } : { supported: Boolean(AudioContextClass), playing: false };

  window.WorldSound = { play, toggle, stop, state };
  reflectState();
})();
