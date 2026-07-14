(() => {
  const TAU = Math.PI * 2;
  const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const fract = value => value - Math.floor(value);
  const ease = value => value * value * (3 - 2 * value);

  const SCENES = {
    phyllo: { kind: 'growth', label: 'прорастание световых семян', event: 'Иногда золотые семена начинают подниматься из общего рисунка. Их спираль не ломает порядок — она показывает, что порядок всё это время был способом роста.', colors: ['#f7dd83', '#e86e45'], count: 34 },
    reaction: { kind: 'wave', label: 'живая мембрана', event: 'Поверхность медленно собирается в мембрану: светлые области расширяются, встречаются и отступают, будто небо пробует на вкус собственные границы.', colors: ['#8edbe2', '#b878d4'], count: 7 },
    percol: { kind: 'storm', label: 'пороговый пробой', event: 'Большую часть времени связи остаются разрозненными. Затем несколько открытых путей внезапно находят друг друга, и через весь свод проходит короткий электрический мост.', colors: ['#fff2a3', '#77d8f2'], period: 31 },
    vitel: { kind: 'tracers', label: 'течение невидимой воды', event: 'Тонкие свидетели течения появляются ненадолго. Они огибают скрытые вихри и исчезают, прежде чем вода успевает стать картой.', colors: ['#8ee8e5', '#d7fff3'], count: 28 },
    frost: { kind: 'growth', label: 'приход холодного сада', event: 'От горизонта медленно проступают новые ветви инея. Каждое касание остаётся в памяти мира и меняет дорогу следующего кристалла.', colors: ['#dff7ff', '#8bb8dd'], count: 42 },
    mayatnik: { kind: 'tracers', label: 'расхождение судеб', event: 'Два световых следа начинают почти вместе. Несколько мгновений спустя они уже описывают разные небеса — без ошибки и без случайности.', colors: ['#ffcb77', '#e96d8a'], count: 16, chaos: true },
    nabor: { kind: 'rain', label: 'двоичный фронт', event: 'От зенита проходит сухой цифровой фронт. Где правило говорит «нет», остаётся тишина; где говорит «да», вспыхивает следующая строка памяти.', colors: ['#e8f0a4', '#82b96b'], count: 38, period: 29 },
    chern: { kind: 'storm', label: 'доменная гроза', event: 'Тёмные и светлые области на несколько мгновений перестают быть соседями и становятся материками. По их границам проходит гроза коллективного решения.', colors: ['#e9efff', '#9a76dd'], period: 37 },

    beam: { kind: 'wave', label: 'дыхание дифракции', event: 'Из зенита расходится кольцо различимости. За ясной полосой следует тишина, потом ещё один слабый ответ — как если бы сам инструмент проверял слух.', colors: ['#e6f7ff', '#80b8d8'], count: 9 },
    chladni: { kind: 'wave', label: 'сбор узловой пыли', event: 'Световая пыль отступает от одних линий и собирается у других. На короткое время становится видно, где поверхность совершенно неподвижна.', colors: ['#f0dca1', '#97c3c9'], count: 12 },
    apollon: { kind: 'orbs', label: 'рождение вложенных миров', event: 'В пустых промежутках появляются меньшие круги, затем ещё меньшие. Пространство не заполняется — оно обнаруживает всё новые места для целого мира.', colors: ['#f2c96d', '#ef8e72'], count: 18 },
    caustic: { kind: 'storm', label: 'звёздный световой шквал', event: 'Лучевые складки сходятся в ослепительный гребень и проходят по своду, словно далёкая звезда на мгновение направила сюда всю геометрию своего света.', colors: ['#fff5bf', '#ff936b'], period: 43, fierce: true },
    chrono: { kind: 'storm', label: 'причинные искры', event: 'Редкие искры соединяют события, которые ещё секунду назад казались независимыми. Их путь всегда направлен, но никогда не объясняет себя до конца.', colors: ['#c0e6ff', '#e3a6ff'], period: 34 },
    superfluid: { kind: 'storm', label: 'смертельная магнитная буря', event: 'Фазовые вихри стягивают небо в поле заряженных дуг. Буря проходит близко и бесшумно; её красота не обещает человеку безопасности.', colors: ['#91eaff', '#e35cff'], period: 47, fierce: true },

    tyaga: { kind: 'breath', label: 'перенос общего усилия', event: 'Тонкие тяги у горизонта по очереди напрягаются, и волна нагрузки идёт к зениту. Большая форма оказывается не властью центра, а суммой малых поддержек.', colors: ['#e6cb88', '#b48351'], mode: 5 },
    equal_area: { kind: 'breath', label: 'равное дыхание ячеек', event: 'Ячейки расширяются и сжимаются не одинаково на картинке, но одинаково по площади сферы. Купол словно проверяет собственное обещание равенства.', colors: ['#cfddb0', '#e9b875'], mode: 8 },
    conformal: { kind: 'breath', label: 'конформная волна', event: 'По кессонной сети проходит мягкая деформация. Масштаб меняется, но углы сохраняют родство, будто архитектура умеет дышать и не терять грамматику.', colors: ['#b7d6e8', '#d2b5ef'], mode: 6 },
    light_muqarnas: { kind: 'facets', label: 'свет, сходящий по нишам', event: 'Свет начинается у окулюса и ярус за ярусом входит в минеральные ниши. Каждая грань принимает его на мгновение и передаёт соседней.', colors: ['#fff0b5', '#c88948'], count: 32 },

    parallax_covenant: { kind: 'tracers', label: 'маяки несводимых взглядов', event: 'Три семейства маяков смещаются независимо. Цельный образ появляется только из одного места, а затем распадается, приглашая зрителя изменить положение.', colors: ['#83d7ef', '#f1af7c'], count: 21 },
    hopf_covenant: { kind: 'orbs', label: 'связанные орбиты', event: 'Световые орбиты проходят друг сквозь друга без столкновения. Каждая остаётся отдельной, но ни одна уже не может быть понята без остальных.', colors: ['#9ddff2', '#d5a1ee'], count: 16, linked: true },
    three_suns: { kind: 'procession', label: 'три прохода света', event: 'Три солнца по очереди находят свою дорогу по оболочке. Утро, полдень и вечер не перекрашивают один мир — они собирают три разных пространства.', colors: ['#ffd98a', '#ef735c'], count: 15 },
    mutual_horizons: { kind: 'storm', label: 'встреча больших кругов', event: 'По небу проходят дуги взаимных горизонтов. Там, где две связи пересекаются, возникает короткий знак: отношение стало общим фактом.', colors: ['#b9e7f5', '#f0c07e'], period: 41 },
    common_pulse: { kind: 'wave', label: 'общая пауза', event: 'Несколько волн продолжают собственный путь и внезапно гасят друг друга. В эту секунду тишина становится не пустотой, а точной формой встречи.', colors: ['#9bd9df', '#c3a5e8'], count: 8 },
    habitable_boundary: { kind: 'rain', label: 'серный дождь на границе света', event: 'Над сумеречной полосой собирается жёлтое облако. Серный дождь проходит к горизонту, оставляя короткие едкие следы, а затем тёплая граница снова становится обитаемой.', colors: ['#e6ef63', '#c88a35'], count: 54, period: 39, sulfur: true },

    portal_1: { kind: 'ascent', label: 'вознесение сущностей', event: 'Небесные сущности покидают золотые ярусы и поднимаются к зениту. Чем выше они оказываются, тем меньше в их движении веса и тем больше общего света.', colors: ['#fff0b5', '#f0b95d'], count: 13 },
    portal_2: { kind: 'breath', label: 'дыхание земли и архитектуры', event: 'Кольца, контуры здания и его иерархии начинают едва заметно шевелиться. Это не землетрясение: огромная глубина под сводом делает медленный вдох.', colors: ['#d7e8f0', '#819eb5'], mode: 7, deep: true },
    portal_3: { kind: 'swimmers', label: 'неловкая жизнь у поверхности', event: 'Причудливые существа плавают по оболочке, запаздывают с поворотом и упрямо машут одной ластой. Они немного похожи на бактерий и совершенно не умеют быть величественными.', colors: ['#f2ce91', '#d98270'], count: 9 },
    san_marco: { kind: 'procession', label: 'золотая процессия памяти', event: 'Фигуры неторопливо обходят весь горизонт. Свет задерживается на каждой, словно мозаика вспоминает присутствия не сразу, а одно за другим.', colors: ['#f6d681', '#bd7746'], count: 24 },
    muqarnas: { kind: 'facets', label: 'свет в малых небесах', event: 'В нишах по очереди зажигаются маленькие небеса. Каскад идёт не сверху вниз, а по родству соседних граней — как передаваемая шёпотом весть.', colors: ['#f0d9a2', '#9e744e'], count: 40 },
    mandala: { kind: 'procession', label: 'паломничество колец', event: 'Небольшие световые знаки идут от горизонта к центру, задерживаются у зенита и возвращаются. Путь повторяется, но возвращение уже звучит иначе.', colors: ['#e4c57b', '#b883c7'], count: 18 }
  };

  let active = null;

  const hash = text => {
    let value = 2166136261;
    for (let i = 0; i < text.length; i += 1) {
      value ^= text.charCodeAt(i);
      value = Math.imul(value, 16777619);
    }
    return value >>> 0;
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

  const point = (rho, phi, size) => ({
    x: size * (0.5 + 0.5 * rho * Math.cos(phi)),
    y: size * (0.5 + 0.5 * rho * Math.sin(phi))
  });

  const eventEnvelope = (elapsed, period = 36, duration = 10, offset = 0.18) => {
    const p = fract(elapsed / period + offset);
    if (p > duration / period) return 0;
    return Math.sin(Math.PI * p * period / duration) ** 2;
  };

  const strokePolar = (ctx, size, rhoFor, color, alpha = 1, width = 1, segments = 150) => {
    ctx.beginPath();
    for (let index = 0; index <= segments; index += 1) {
      const phi = index / segments * TAU;
      const p = point(clamp(rhoFor(phi), 0, 1.05), phi, size);
      if (index === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
  };

  const drawEntity = (ctx, x, y, size, angle, color, wingPhase, alpha) => {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = Math.max(0.8, size * 0.08);
    ctx.shadowColor = color;
    ctx.shadowBlur = size * 0.75;
    ctx.beginPath();
    ctx.ellipse(0, 0, size * 0.12, size * 0.33, 0, 0, TAU);
    ctx.fill();
    const spread = 0.42 + 0.24 * Math.sin(wingPhase);
    [-1, 1].forEach(side => {
      ctx.beginPath();
      ctx.moveTo(0, -size * 0.1);
      ctx.bezierCurveTo(side * size * spread, -size * 0.55, side * size * 0.7, size * 0.08, 0, size * 0.18);
      ctx.stroke();
    });
    ctx.restore();
  };

  const renderAscent = session => {
    const { ctx, size, scene, elapsed, seed } = session;
    for (let i = 0; i < scene.count; i += 1) {
      const duration = 14 + (i % 5) * 2.7;
      const progress = fract(elapsed / duration + i / scene.count + fract(seed * 0.000001));
      const rise = ease(progress);
      const rho = 0.94 * (1 - rise) + 0.025;
      const phi = i * GOLDEN_ANGLE + rise * (0.8 + (i % 3) * 0.26) + 0.05 * Math.sin(elapsed * 0.7 + i);
      const p = point(rho, phi, size);
      const scale = size * (0.028 + 0.018 * rho);
      const alpha = Math.sin(progress * Math.PI) * (0.5 + 0.5 * eventEnvelope(elapsed, 32, 18));
      drawEntity(ctx, p.x, p.y, scale, phi - Math.PI / 2, scene.colors[i % 2], elapsed * 4.2 + i, alpha);
    }
  };

  const renderBreath = session => {
    const { ctx, size, scene, elapsed } = session;
    const phase = elapsed * TAU / (scene.deep ? 16 : 12);
    const pulse = 0.5 + 0.5 * Math.sin(phase);
    const mode = scene.mode || 6;
    for (let ring = 1; ring <= 8; ring += 1) {
      const base = 0.08 + ring * 0.105;
      strokePolar(ctx, size, phi => base * (1 + (0.012 + ring * 0.0025) * Math.sin(phase - ring * 0.45 + mode * phi)), scene.colors[ring % 2], 0.16 + pulse * 0.24, 0.8 + pulse * 1.35);
    }
    ctx.globalAlpha = 0.14 + pulse * 0.18;
    ctx.strokeStyle = scene.colors[0];
    ctx.lineWidth = 0.8 + pulse;
    for (let spoke = 0; spoke < mode * 2; spoke += 1) {
      const phi = spoke / (mode * 2) * TAU + 0.018 * Math.sin(phase + spoke);
      const inner = point(0.09, phi, size);
      const outer = point(0.94, phi + 0.022 * Math.sin(phase - spoke * 0.4), size);
      ctx.beginPath(); ctx.moveTo(inner.x, inner.y); ctx.lineTo(outer.x, outer.y); ctx.stroke();
    }
    session.shell.style.setProperty('--scene-breath', String((0.985 + pulse * 0.025).toFixed(4)));
  };

  const drawSwimmer = (ctx, x, y, scale, angle, color, flap, alpha) => {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = color;
    ctx.strokeStyle = color;
    ctx.lineWidth = Math.max(0.8, scale * 0.065);
    ctx.shadowColor = color;
    ctx.shadowBlur = scale * 0.35;
    ctx.beginPath();
    ctx.ellipse(0, 0, scale * 0.48, scale * 0.23, 0, 0, TAU);
    ctx.fill();
    ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath(); ctx.arc(scale * 0.2, -scale * 0.055, scale * 0.045, 0, TAU); ctx.fill();
    ctx.globalCompositeOperation = 'source-over';
    ctx.beginPath();
    ctx.moveTo(-scale * 0.38, 0);
    ctx.quadraticCurveTo(-scale * (0.7 + 0.22 * flap), -scale * 0.35, -scale * (0.82 + 0.13 * flap), scale * 0.06);
    ctx.quadraticCurveTo(-scale * 0.58, scale * 0.16, -scale * 0.38, 0);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(scale * 0.03, scale * 0.12);
    ctx.quadraticCurveTo(scale * 0.1, scale * (0.48 + flap * 0.16), scale * 0.35, scale * 0.22);
    ctx.stroke();
    ctx.restore();
  };

  const renderSwimmers = session => {
    const { ctx, size, scene, elapsed, objects } = session;
    objects.slice(0, scene.count).forEach((object, index) => {
      const hesitancy = Math.sin(elapsed * (0.19 + object.r * 0.08) + object.phase);
      const phi = object.phi + object.direction * elapsed * (0.035 + object.r * 0.025) + 0.15 * Math.sin(elapsed * 0.37 + index);
      const rho = clamp(0.36 + object.r * 0.52 + 0.055 * hesitancy, 0.18, 0.94);
      const p = point(rho, phi, size);
      const flap = Math.sin(elapsed * (2.2 + object.r) + object.phase * 2);
      drawSwimmer(ctx, p.x, p.y, size * (0.032 + object.r * 0.025), phi + object.direction * Math.PI / 2 + hesitancy * 0.28, scene.colors[index % 2], flap, 0.32 + object.r * 0.38);
    });
  };

  const renderRain = session => {
    const { ctx, size, scene, elapsed, objects } = session;
    const envelope = eventEnvelope(elapsed, scene.period || 34, scene.sulfur ? 13 : 9, 0.08);
    if (envelope < 0.002) return;
    ctx.lineCap = 'round';
    objects.slice(0, scene.count).forEach((drop, index) => {
      const p = fract(elapsed * (0.19 + drop.r * 0.22) + drop.phase);
      const rho = 0.08 + p * 0.98;
      const phi = drop.phi + elapsed * (scene.sulfur ? 0.025 : -0.018) + 0.08 * Math.sin(p * Math.PI);
      const a = point(rho, phi, size);
      const b = point(clamp(rho - 0.035 - drop.r * 0.055, 0, 1), phi - 0.012, size);
      ctx.globalAlpha = envelope * (0.12 + drop.r * 0.48) * Math.sin(p * Math.PI);
      ctx.strokeStyle = scene.colors[index % 2];
      ctx.lineWidth = 0.7 + drop.r * 1.5;
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    });
  };

  const renderStorm = session => {
    const { ctx, size, scene, elapsed, objects } = session;
    const envelope = eventEnvelope(elapsed, scene.period || 38, scene.fierce ? 11 : 7, 0.24);
    if (envelope < 0.002) return;
    ctx.lineCap = 'round';
    objects.slice(0, scene.fierce ? 14 : 9).forEach((arc, index) => {
      const onset = clamp(envelope * 2.4 - index * 0.06, 0, 1);
      if (!onset) return;
      const phi0 = arc.phi + 0.15 * Math.sin(elapsed * 0.7 + arc.phase);
      ctx.beginPath();
      for (let step = 0; step <= 38; step += 1) {
        const u = step / 38;
        const phi = phi0 + (u - 0.5) * (1.3 + arc.r * 1.7);
        const rho = clamp(0.14 + arc.r * 0.62 + 0.18 * Math.sin(u * Math.PI) + 0.018 * Math.sin(u * 31 + index), 0.03, 0.98);
        const p = point(rho, phi, size);
        if (!step) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
      }
      ctx.globalAlpha = onset * (0.08 + arc.r * 0.35);
      ctx.strokeStyle = scene.colors[index % 2];
      ctx.lineWidth = (scene.fierce ? 1.1 : 0.75) + arc.r * 1.5;
      ctx.shadowColor = scene.colors[index % 2];
      ctx.shadowBlur = scene.fierce ? 11 : 6;
      ctx.stroke();
    });
    ctx.shadowBlur = 0;
  };

  const renderWave = session => {
    const { ctx, size, scene, elapsed } = session;
    for (let index = 0; index < scene.count; index += 1) {
      const p = fract(elapsed / (9 + index * 0.16) + index / scene.count);
      const rho = ease(p) * 0.98;
      const alpha = Math.sin(p * Math.PI) * (index % 3 === 0 ? 0.42 : 0.19);
      strokePolar(ctx, size, phi => rho + 0.012 * Math.sin(phi * (3 + index % 5) + elapsed * 0.6), scene.colors[index % 2], alpha, 0.8 + (1 - p) * 1.5, 100);
    }
  };

  const renderTracers = session => {
    const { ctx, size, scene, elapsed, objects } = session;
    objects.slice(0, scene.count).forEach((tracer, index) => {
      const speed = 0.055 + tracer.r * 0.045;
      const phi = tracer.phi + elapsed * speed * tracer.direction + (scene.chaos ? 0.42 * Math.sin(elapsed * 0.8 + tracer.phase) : 0.12 * Math.sin(elapsed * 0.25 + tracer.phase));
      const rho = clamp(0.12 + tracer.r * 0.79 + 0.07 * Math.sin(phi * 3 + elapsed * 0.31), 0.05, 0.96);
      const p = point(rho, phi, size);
      ctx.globalAlpha = 0.18 + tracer.r * 0.42;
      ctx.fillStyle = scene.colors[index % 2];
      ctx.shadowColor = ctx.fillStyle;
      ctx.shadowBlur = 5;
      ctx.beginPath(); ctx.arc(p.x, p.y, 0.7 + tracer.r * 1.8, 0, TAU); ctx.fill();
    });
    ctx.shadowBlur = 0;
  };

  const renderGrowth = session => {
    const { ctx, size, scene, elapsed, objects } = session;
    const reveal = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(elapsed * TAU / 23));
    ctx.lineCap = 'round';
    objects.slice(0, scene.count).forEach((branch, index) => {
      const depth = index / scene.count;
      if (depth > reveal) return;
      const phi = branch.phi + depth * (scene === SCENES.phyllo ? GOLDEN_ANGLE : 0.42 * Math.sin(index));
      const outer = point(0.96 - depth * 0.66, phi, size);
      const inner = point(0.98 - Math.max(0, depth - 0.055) * 0.68, phi - 0.035 * branch.direction, size);
      ctx.globalAlpha = 0.12 + (1 - depth) * 0.38;
      ctx.strokeStyle = scene.colors[index % 2];
      ctx.lineWidth = 0.55 + (1 - depth) * 1.25;
      ctx.beginPath(); ctx.moveTo(inner.x, inner.y); ctx.quadraticCurveTo((inner.x + outer.x) / 2 + Math.sin(phi) * 5, (inner.y + outer.y) / 2 - Math.cos(phi) * 5, outer.x, outer.y); ctx.stroke();
    });
  };

  const renderOrbs = session => {
    const { ctx, size, scene, elapsed, objects } = session;
    objects.slice(0, scene.count).forEach((orb, index) => {
      const phi = orb.phi + elapsed * 0.018 * orb.direction;
      const rho = 0.08 + orb.r * 0.82;
      const p = point(rho, phi, size);
      const radius = size * (0.006 + 0.019 * (1 - orb.r)) * (0.86 + 0.14 * Math.sin(elapsed * 0.7 + orb.phase));
      ctx.globalAlpha = 0.18 + (1 - orb.r) * 0.33;
      ctx.strokeStyle = scene.colors[index % 2];
      ctx.lineWidth = 0.7 + (scene.linked ? 0.5 : 0);
      ctx.beginPath(); ctx.arc(p.x, p.y, radius, 0, TAU); ctx.stroke();
      if (scene.linked && index > 0 && index % 3 === 0) {
        const previous = objects[index - 1];
        const q = point(0.08 + previous.r * 0.82, previous.phi - elapsed * 0.014, size);
        ctx.globalAlpha *= 0.42;
        ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.quadraticCurveTo(size / 2, size / 2, q.x, q.y); ctx.stroke();
      }
    });
  };

  const renderFacets = session => {
    const { ctx, size, scene, elapsed } = session;
    const head = fract(elapsed / 15);
    for (let index = 0; index < scene.count; index += 1) {
      const address = index / scene.count;
      const distance = Math.min(Math.abs(address - head), 1 - Math.abs(address - head));
      const glow = Math.max(0, 1 - distance * 11);
      if (!glow) continue;
      const rho = 0.12 + 0.82 * Math.sqrt(address);
      const phi = index * GOLDEN_ANGLE;
      const p = point(rho, phi, size);
      ctx.globalAlpha = glow * 0.55;
      ctx.fillStyle = scene.colors[index % 2];
      ctx.beginPath();
      ctx.moveTo(p.x, p.y - size * 0.012);
      ctx.lineTo(p.x + size * 0.013, p.y + size * 0.009);
      ctx.lineTo(p.x - size * 0.013, p.y + size * 0.009);
      ctx.closePath(); ctx.fill();
    }
  };

  const renderProcession = session => {
    const { ctx, size, scene, elapsed } = session;
    for (let index = 0; index < scene.count; index += 1) {
      const orbit = index % 3;
      const rho = 0.28 + orbit * 0.25 + 0.025 * Math.sin(elapsed * 0.3 + index);
      const phi = index / scene.count * TAU + elapsed * (0.018 + orbit * 0.005) * (orbit === 1 ? -1 : 1);
      const p = point(rho, phi, size);
      drawEntity(ctx, p.x, p.y, size * (0.012 + orbit * 0.003), phi + Math.PI / 2, scene.colors[index % 2], elapsed * 1.4 + index, 0.2 + 0.25 * Math.sin(index + 2) ** 2);
    }
  };

  const renderers = {
    ascent: renderAscent,
    breath: renderBreath,
    swimmers: renderSwimmers,
    rain: renderRain,
    storm: renderStorm,
    wave: renderWave,
    tracers: renderTracers,
    growth: renderGrowth,
    orbs: renderOrbs,
    facets: renderFacets,
    procession: renderProcession
  };

  const resize = session => {
    const rect = session.shell.getBoundingClientRect();
    const cssSize = Math.max(1, Math.min(rect.width, rect.height));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (session.canvas.width !== Math.round(cssSize * dpr)) {
      session.canvas.width = Math.round(cssSize * dpr);
      session.canvas.height = Math.round(cssSize * dpr);
      session.canvas.style.width = `${cssSize}px`;
      session.canvas.style.height = `${cssSize}px`;
    }
    session.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    session.size = cssSize;
  };

  const renderAtmosphere = session => {
    const { ctx, size, scene, elapsed } = session;
    const intensity = eventEnvelope(elapsed, scene.period || 40, 11, 0.17);
    const gradient = ctx.createRadialGradient(size * 0.44, size * 0.38, size * 0.05, size * 0.5, size * 0.5, size * 0.5);
    gradient.addColorStop(0, 'rgba(255,255,255,0.025)');
    gradient.addColorStop(0.72, 'rgba(20,28,44,0.015)');
    gradient.addColorStop(1, scene.kind === 'rain' ? `rgba(190,174,44,${0.07 + intensity * 0.08})` : 'rgba(3,6,13,0.24)');
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
  };

  const frame = now => {
    if (!active) return;
    resize(active);
    const elapsed = Math.max(0, (now - active.epoch) / 1000);
    active.elapsed = elapsed;
    const { ctx, size } = active;
    ctx.clearRect(0, 0, size, size);
    ctx.save();
    ctx.beginPath(); ctx.arc(size / 2, size / 2, size / 2, 0, TAU); ctx.clip();
    ctx.globalCompositeOperation = 'screen';
    renderers[active.scene.kind](active);
    renderAtmosphere(active);
    ctx.restore();

    const beat = active.timing?.beatSeconds ? Math.floor(elapsed / active.timing.beatSeconds) : 0;
    document.documentElement.dataset.sceneWorld = active.world.key;
    document.documentElement.dataset.sceneKind = active.scene.kind;
    document.documentElement.dataset.sceneBeat = String(beat);
    document.documentElement.dataset.sceneFrame = String(active.frameCount += 1);
    active.raf = requestAnimationFrame(frame);
  };

  const stop = () => {
    if (!active) return;
    cancelAnimationFrame(active.raf);
    active.resizeObserver?.disconnect();
    active.shell.style.removeProperty('--scene-breath');
    active.canvas.remove();
    active = null;
    delete document.documentElement.dataset.sceneWorld;
    delete document.documentElement.dataset.sceneKind;
    delete document.documentElement.dataset.sceneBeat;
    delete document.documentElement.dataset.sceneFrame;
  };

  const start = ({ world, shell, epoch = performance.now(), timing }) => {
    stop();
    const scene = SCENES[world.key] || SCENES.beam;
    const canvas = document.createElement('canvas');
    canvas.className = 'world-scene';
    canvas.setAttribute('aria-hidden', 'true');
    const seed = hash(world.key);
    const random = randomFrom(seed);
    const objects = Array.from({ length: 64 }, (_, index) => ({
      r: random(),
      phi: random() * TAU,
      phase: random() * TAU + index * 0.11,
      direction: random() > 0.5 ? 1 : -1
    }));
    shell.append(canvas);
    active = {
      world,
      shell,
      scene,
      canvas,
      ctx: canvas.getContext('2d'),
      seed,
      objects,
      epoch,
      timing,
      size: 1,
      elapsed: 0,
      frameCount: 0,
      raf: 0,
      resizeObserver: 'ResizeObserver' in window ? new ResizeObserver(() => active && resize(active)) : null
    };
    active.resizeObserver?.observe(shell);
    active.raf = requestAnimationFrame(frame);
    return scene;
  };

  const presetFor = key => SCENES[key] || SCENES.beam;
  const state = () => active ? {
    key: active.world.key,
    kind: active.scene.kind,
    label: active.scene.label,
    frameCount: active.frameCount,
    beat: Number(document.documentElement.dataset.sceneBeat || 0),
    elapsed: Number(active.elapsed.toFixed(2))
  } : { active: false };

  window.WorldScene = { start, stop, presetFor, state };
})();
