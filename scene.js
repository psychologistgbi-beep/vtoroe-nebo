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

    portal_1: {
      kind: 'source-performance', sourceMode: 1, actorCount: 84, actorSpin: 0, cycle: 72,
      label: 'вознесение уже вписанного сонма',
      event: 'Фигуры не возникают поверх купола: каждая из них уже находится в исходном Dome Master. Внешний ярус первым теряет вес, затем движение передаётся внутрь, и весь сонм на короткое время тянется к зениту.',
      cues: [
        { at: 0, label: 'вес · сонм удерживается архитектурой' },
        { at: 8, label: 'отрыв · внешний ярус впервые теряет вес' },
        { at: 20, label: 'передача · вознесение входит в следующие регистры' },
        { at: 42, label: 'сонм · разные пути получают общее направление' },
        { at: 58, label: 'порог · окулюс принимает, но не поглощает' },
        { at: 66, label: 'остаток · фигуры помнят пережитую лёгкость' }
      ]
    },
    portal_2: {
      kind: 'source-performance', sourceMode: 2, cycle: 66,
      label: 'дыхание самой конструкции',
      event: 'Новые контуры не рисуются. Двигаются кессоны, рёбра и кольца исходного изображения: внешний пояс набирает давление, волна проходит к окулюсу, затем вся архитектура медленно отдаёт воздух.',
      cues: [
        { at: 0, label: 'задержка · архитектура держит дыхание' },
        { at: 10, label: 'вдох · внешний пояс принимает давление' },
        { at: 24, label: 'глубина · волна входит в кессонные регистры' },
        { at: 40, label: 'выдох · вся конструкция возвращает объём' },
        { at: 54, label: 'послетолчок · камень ещё помнит движение' },
        { at: 62, label: 'покой · тяжесть снова кажется неподвижной' }
      ]
    },
    portal_3: {
      kind: 'layered-procession', actorCount: 64, actorSpin: 1.4,
      label: 'архитектура обнаруживает жизнь',
      event: 'Ничего нового в этом мире не появляется. Шестьдесят четыре существа, уже вписанные в исходный свод, одно за другим пробуют движение: один жест вызывает ответ, ответ собирает весь сонм, а затем звук и движение почти полностью исчезают.',
      cycle: 60,
      cues: [
        { at: 0, label: 'покой · фигуры ещё кажутся орнаментом' },
        { at: 3, label: 'первый жест · внешняя фигура начинает путь' },
        { at: 10, label: 'ответ · сигнал каскадом идёт к центру' },
        { at: 16, label: 'процессия · сонм движется к окулюсу' },
        { at: 38, label: 'признание · окулюс принимает процессию' },
        { at: 50, label: 'цена · ярусы пустеют' },
        { at: 55, label: 'послесловие · одна фигура возвращается' }
      ]
    },
    san_marco: {
      kind: 'source-performance', sourceMode: 4, cycle: 64,
      label: 'память проходит по тессерам',
      event: 'Никакая золотая процессия не добавляется поверх мозаики. Узкий свет находит уже существующие тессеры, расходится по серебряным руслам и на мгновение превращает разрозненные камни в одно вспоминающее поле.',
      cues: [
        { at: 0, label: 'сумрак · золото ещё остаётся веществом' },
        { at: 8, label: 'первый отблеск · одна полоса вспоминает свет' },
        { at: 20, label: 'передача · тессеры отвечают соседям' },
        { at: 42, label: 'русло · серебряные пути собирают память' },
        { at: 52, label: 'угасание · целое снова рассыпается в камни' },
        { at: 60, label: 'след · золото удерживает один тихий отблеск' }
      ]
    },
    muqarnas: {
      kind: 'source-performance', sourceMode: 5, cycle: 70,
      label: 'свет испытывает глубину ярусов',
      event: 'Треугольные ниши исходного свода не получают новых граней. Скользящий свет и малая деформация переходят от яруса к ярусу, так что плоская сетка начинает доказывать собственную глубину.',
      cues: [
        { at: 0, label: 'минерал · ярусы скрывают глубину' },
        { at: 9, label: 'касание · внешний пояс принимает свет' },
        { at: 22, label: 'каскад · свет спускается по родству ниш' },
        { at: 43, label: 'инверсия · пустота на миг становится телом' },
        { at: 56, label: 'затвор · глубина снова закрывается' },
        { at: 65, label: 'послесвечение · одна грань хранит путь' }
      ]
    },
    mandala: {
      kind: 'source-performance', sourceMode: 6, cycle: 68,
      label: 'внимание проходит через существующие кольца',
      event: 'Новые паломники не появляются. Дышат сами линии космограммы: внешний венец передаёт импульс розеткам, их ритмы ненадолго совпадают у центра и затем отпускают взгляд обратно к горизонту.',
      cues: [
        { at: 0, label: 'рассеяние · взгляд ещё принадлежит краю' },
        { at: 8, label: 'вход · внешний венец начинает путь' },
        { at: 20, label: 'приближение · розетки передают импульс внутрь' },
        { at: 40, label: 'совпадение · разные ритмы встречаются у центра' },
        { at: 52, label: 'возвращение · центр отпускает взгляд наружу' },
        { at: 62, label: 'тишина · путь остаётся в теле наблюдателя' }
      ]
    }
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

  /* ── LAYERED PROCESSION (Portal III): base texture + animated figures ── */
  const PORTAL3_ATLAS_URL = 'img/fulldome/portal_3_atlas.json';
  const PORTAL3_BASE_512 = 'img/fulldome/web/portal_3_base_512.webp';
  const PORTAL3_BASE_1024 = 'img/fulldome/web/portal_3_base_1024.webp';

  const portalThreeMovement = (being, t, cycle) => {
    // Dramatic arc: rest(0-3) → gesture(3-8) → continuous procession(5-50) → cost(50-55) → epilogue(55-60)
    // Each being has a unique departure time spread across 5-42s window.
    // This guarantees visible motion in ANY 5-second observation window.
    const actor = being.index;
    const plane = being.plane;
    let progress = 0;

    // Ambient inward drift from t=0 (ensures immediate perceptible motion)
    progress = Math.min(t * 0.009, 0.06);

    // Continuous procession: each being departs at a unique time
    // Outer beings (high plane) leave earlier; golden-ratio spread prevents bunching
    const departureSpread = fract(actor * 0.61803398875); // 0..1 uniform-ish
    const tierOrder = 1 - plane; // inner beings (small plane) depart later
    const departTime = 3 + departureSpread * 18 + tierOrder * 16; // range: 3..37
    const travelTime = 10 + (1 - plane) * 5; // inner beings (smaller r) travel faster: 10-15s

    if (t >= departTime) {
      const journeyT = clamp((t - departTime) / travelTime, 0, 1);
      const target = 0.94 + plane * 0.04; // 0.94-0.98
      progress = Math.max(progress, ease(journeyT) * target);
    }

    // Leader being #55: dramatic early departure
    if (actor === 55 && t >= 3) {
      const leaderT = clamp((t - 3) / 12, 0, 1);
      progress = Math.max(progress, ease(leaderT) * 0.96);
    }

    // Cost phase (50-55): all settled near center, slight final drift
    if (t >= 50 && t < 55) {
      progress = Math.max(progress, 0.94 + (t - 50) / 50);
    }

    // Epilogue (55-60): being #1 returns outward — visible single-figure motion
    if (t >= 55 && actor === 1) {
      const returnT = clamp((t - 55) / 5, 0, 1);
      progress = 0.98 * (1 - ease(returnT) * 0.88);
    } else if (t >= 55) {
      progress = Math.max(progress, 0.98);
    }

    return clamp(progress, 0, 1);
  };

  const drawBeing = (ctx, cx, cy, size, bodyColor, wingColor, hasHalo, wingPhase, alpha) => {
    // size is already in CSS pixels
    const canvasSize = size;
    if (canvasSize < 0.5) return;
    ctx.save();
    ctx.globalAlpha = alpha;

    // Body (ellipse/teardrop shape)
    ctx.fillStyle = bodyColor;
    ctx.beginPath();
    ctx.ellipse(cx, cy, canvasSize * 0.40, canvasSize * 0.62, 0, 0, TAU);
    ctx.fill();

    // Wings
    const spread = 0.42 + 0.24 * Math.sin(wingPhase);
    ctx.fillStyle = wingColor;
    ctx.globalAlpha = alpha * 0.9;
    // Left wing
    ctx.beginPath();
    ctx.moveTo(cx, cy + canvasSize * 0.1);
    ctx.lineTo(cx - canvasSize * 0.95 * spread / 0.42, cy + canvasSize * 0.55);
    ctx.lineTo(cx - canvasSize * 0.28, cy - canvasSize * 0.05);
    ctx.closePath();
    ctx.fill();
    // Right wing
    ctx.beginPath();
    ctx.moveTo(cx, cy + canvasSize * 0.1);
    ctx.lineTo(cx + canvasSize * 0.95 * spread / 0.42, cy + canvasSize * 0.55);
    ctx.lineTo(cx + canvasSize * 0.28, cy - canvasSize * 0.05);
    ctx.closePath();
    ctx.fill();

    // Halo
    if (hasHalo) {
      ctx.globalAlpha = alpha * 0.7;
      ctx.strokeStyle = '#ffe9a8';
      ctx.lineWidth = Math.max(0.5, canvasSize * 0.04);
      ctx.beginPath();
      ctx.arc(cx, cy + canvasSize * 0.82, canvasSize * 0.32, 0, TAU);
      ctx.stroke();
    }
    ctx.restore();
  };

  const prepareLayeredProcession = session => {
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
      session.staticFallback = true;
      return;
    }
    session.layeredReady = false;
    session.layeredBase = null;
    session.layeredAtlas = null;

    // Load base image
    const baseImg = new Image();
    const baseUrl = window.devicePixelRatio > 1 ? PORTAL3_BASE_1024 : PORTAL3_BASE_512;
    baseImg.src = baseUrl;
    baseImg.onload = () => {
      session.layeredBase = baseImg;
      if (session.layeredAtlas) session.layeredReady = true;
      session.canvas.classList.add('world-scene--layered', 'is-ready');
    };
    baseImg.onerror = () => {
      console.warn('portal_3 base image failed, falling back to static');
      session.staticFallback = true;
    };

    // Load atlas JSON
    fetch(PORTAL3_ATLAS_URL)
      .then(r => r.json())
      .then(atlas => {
        session.layeredAtlas = atlas;
        if (session.layeredBase) session.layeredReady = true;
      })
      .catch(() => {
        console.warn('portal_3 atlas failed, falling back to static');
        session.staticFallback = true;
      });

    // Hide the original static image when layered mode activates
    const srcImg = session.shell.querySelector('img');
    if (srcImg) {
      session.sourceImage = srcImg;
      srcImg.classList.add('is-performance-source');
    }
  };

  const renderLayeredProcession = session => {
    if (!session.layeredReady) return;
    const { ctx, size, elapsed, layeredBase, layeredAtlas } = session;
    const cycle = session.scene.cycle || 60;
    const t = elapsed % cycle;

    // Draw base dome
    ctx.drawImage(layeredBase, 0, 0, size, size);

    // Draw beings at their animated positions
    const beings = layeredAtlas.beings;
    const wingTime = elapsed * 2.34;
    for (let i = 0; i < beings.length; i += 1) {
      const b = beings[i];
      const progress = portalThreeMovement(b, t, cycle);
      // Interpolate from original radius to 0 (center)
      const currentR = b.r * (1 - progress);
      // Convert polar to canvas coords (dome is in [-1,1] mapped to [0,size])
      const cx = size * (0.5 + 0.5 * currentR * Math.cos(b.angle));
      const cy = size * (0.5 + 0.5 * currentR * Math.sin(b.angle));
      const beingSize = b.size * size * 0.5; // dome coords → CSS pixels

      // Fade out beings that reached center, except #1 returning
      let alpha = 1;
      if (t >= 48 && t < 55 && b.index !== 1) {
        alpha = Math.max(0.15, 1 - clamp((t - 48) / 5, 0, 1) * 0.7);
      }
      if (t >= 55 && b.index !== 1) {
        alpha = 0.3;
      }

      const wingPhase = wingTime + b.index * 1.176;
      drawBeing(ctx, cx, cy, beingSize, b.bodyColor, b.wingColor, b.hasHalo, wingPhase, alpha);
    }
  };

  const renderers = {
    ascent: renderAscent,
    breath: renderBreath,
    rain: renderRain,
    storm: renderStorm,
    wave: renderWave,
    tracers: renderTracers,
    growth: renderGrowth,
    orbs: renderOrbs,
    facets: renderFacets,
    procession: renderProcession,
    'layered-procession': renderLayeredProcession
  };

  const SOURCE_VERTEX_SHADER = `
    precision highp float;
    attribute vec2 aPosition;
    uniform float uTime;
    uniform float uCycle;
    uniform float uMode;
    uniform float uActorCount;
    uniform vec4 uActors[104];
    varying vec2 vUv;
    varying float vReveal;

    float windowed(float t, float startAt, float endAt, float fade) {
      return smoothstep(startAt, startAt + fade, t) * (1.0 - smoothstep(endAt - fade, endAt, t));
    }

    float responseOrder(float actor) {
      if (abs(actor - 42.0) < 0.25) return 0.0;
      if (abs(actor - 34.0) < 0.25) return 1.0;
      if (abs(actor - 21.0) < 0.25) return 2.0;
      if (abs(actor - 13.0) < 0.25) return 3.0;
      if (abs(actor - 8.0) < 0.25) return 4.0;
      if (abs(actor - 3.0) < 0.25) return 5.0;
      if (abs(actor - 2.0) < 0.25) return 6.0;
      if (abs(actor - 1.0) < 0.25) return 7.0;
      return -1.0;
    }

    float portalThreePerformance(float actor, float t) {
      float action = 0.0;
      if (abs(actor - 55.0) < 0.25) action += windowed(t, 7.0, 14.2, 1.25);
      float order = responseOrder(actor);
      if (order >= 0.0) action += windowed(t, 14.0 + order * 1.16, 26.0, 0.72);
      float delay = fract(actor * 0.61803398875) * 3.6;
      float leave = fract(actor * 0.41421356237) * 2.2;
      action += windowed(t, 25.0 + delay, 47.4 - leave, 1.15) * 0.86;
      if (abs(actor - 1.0) < 0.25) action += windowed(t, 55.0, 59.75, 0.8);
      return clamp(action, 0.0, 1.0);
    }

    float ascentPerformance(float actor, float t) {
      float plane = actor / max(uActorCount, 1.0);
      float startAt = 8.0 + (1.0 - plane) * 24.0 + fract(actor * 0.61803398875) * 2.4;
      float personal = windowed(t, startAt, min(startAt + 17.0, 52.0), 1.4);
      float assembly = windowed(t, 42.0, 59.0, 2.1) * 0.82;
      float threshold = windowed(t, 58.0, 66.5, 1.6) * (0.35 + plane * 0.35);
      return clamp(personal + assembly + threshold, 0.0, 1.0);
    }

    void main() {
      float t = mod(uTime, uCycle);
      vec2 p = aPosition;
      vec2 displacement = vec2(0.0);
      float reveal = 0.0;

      float radius = length(p);
      vec2 radial = radius > 0.0001 ? p / radius : vec2(0.0, 1.0);
      vec2 tangent = vec2(-radial.y, radial.x);

      if (uMode > 1.5 && uMode < 2.5) {
        float inhale = windowed(t, 10.0, 40.0, 3.0);
        float exhale = windowed(t, 36.0, 56.0, 3.0);
        float aftershock = windowed(t, 54.0, 62.5, 1.6);
        float pressure = sin(radius * 18.0 - t * 0.76) * inhale
          - sin(radius * 10.0 + t * 0.48) * exhale * 0.72
          + sin(radius * 27.0 - t * 1.35) * aftershock * 0.24;
        displacement += radial * pressure * (0.0025 + radius * 0.0062);
        reveal = clamp(abs(pressure) * 0.52, 0.0, 1.0);
      } else if (uMode > 4.5 && uMode < 5.5) {
        float cascade = windowed(t, 9.0, 56.0, 3.2);
        float inversion = windowed(t, 41.5, 55.5, 2.0);
        float tier = sin(radius * 48.0 - t * 1.18);
        displacement += radial * tier * cascade * 0.0046;
        displacement += tangent * sin(atan(p.y, p.x) * 12.0 + radius * 19.0 - t * 0.62) * inversion * 0.0018;
        reveal = clamp(abs(tier) * cascade * 0.7, 0.0, 1.0);
      } else if (uMode > 5.5) {
        float inward = windowed(t, 8.0, 42.0, 3.0);
        float meeting = windowed(t, 38.0, 53.0, 2.5);
        float returnWave = windowed(t, 51.0, 63.0, 2.0);
        float pulse = sin(radius * 20.0 - t * 0.7) * inward
          + sin(radius * 14.0 + t * 0.58) * returnWave * 0.78;
        displacement += radial * pulse * (0.0018 + radius * 0.0038);
        displacement += tangent * sin(atan(p.y, p.x) * 6.0 - t * 0.38) * meeting * 0.0017;
        reveal = clamp(abs(pulse) * 0.54 + meeting * (1.0 - radius) * 0.36, 0.0, 1.0);
      }

      for (int j = 0; j < 104; j++) {
        if (float(j) >= uActorCount) continue;
        vec4 actorData = uActors[j];
        vec2 local = p - actorData.xy;
        float size = actorData.z;
        float actor = actorData.w;
        float action = uMode < 1.5 ? ascentPerformance(actor, t) : portalThreePerformance(actor, t);

        float wholeDistance = length(vec2(local.x / (size * 1.25), local.y / (size * 1.38)));
        float whole = 1.0 - smoothstep(0.72, 1.14, wholeDistance);
        float bodyDistance = length(vec2(local.x / (size * 0.53), local.y / (size * 0.84)));
        float body = 1.0 - smoothstep(0.66, 1.12, bodyDistance);
        vec2 wingLocal = vec2(local.x / (size * 1.08), (local.y - size * 0.12) / (size * 0.76));
        float wing = (1.0 - smoothstep(0.56, 1.12, length(wingLocal)))
          * smoothstep(size * 0.14, size * 0.48, abs(local.x));

        float flap = sin(uTime * (uMode < 1.5 ? 1.72 : 2.34) + actor * 1.176);
        float hesitation = sin(uTime * 0.62 + actor * 0.37);
        float uneven = mix(0.42, 1.0, step(0.0, local.x));
        if (uMode < 1.5) {
          vec2 ascent = normalize(actorData.xy + vec2(0.0001));
          displacement -= ascent * whole * size * 0.15 * action * (0.58 + 0.42 * sin(uTime * 0.36 + actor) * sin(uTime * 0.36 + actor));
          displacement.y += wing * size * 0.115 * flap * action;
          displacement.x += body * size * 0.035 * hesitation * action;
        } else {
          displacement.y += wing * size * 0.17 * flap * action * uneven;
          displacement.x += body * size * 0.052 * hesitation * action;
          displacement.y += whole * size * 0.028 * sin(uTime * 0.73 + actor) * action;
        }
        reveal = max(reveal, whole * action);
      }

      vUv = aPosition * 0.5 + 0.5;
      vReveal = reveal;
      gl_Position = vec4(p + displacement, 0.0, 1.0);
    }
  `;

  const SOURCE_FRAGMENT_SHADER = `
    precision highp float;
    uniform sampler2D uTexture;
    uniform float uTime;
    uniform float uCycle;
    uniform float uMode;
    varying vec2 vUv;
    varying float vReveal;

    float windowed(float t, float startAt, float endAt, float fade) {
      return smoothstep(startAt, startAt + fade, t) * (1.0 - smoothstep(endAt - fade, endAt, t));
    }

    void main() {
      vec4 source = texture2D(uTexture, vUv);
      float t = mod(uTime, uCycle);
      float radius = length((vUv - 0.5) * 2.0);
      vec2 p = (vUv - 0.5) * 2.0;
      float angle = atan(p.y, p.x);
      float luminance = dot(source.rgb, vec3(0.2126, 0.7152, 0.0722));

      if (uMode < 1.5) {
        float assembly = windowed(t, 42.0, 66.0, 2.4);
        float oculus = 1.0 - smoothstep(0.04, 0.24, radius);
        source.rgb *= 1.0 + vReveal * 0.075 + assembly * (0.025 + oculus * 0.08);
      } else if (uMode < 2.5) {
        float breath = windowed(t, 10.0, 58.0, 3.0);
        float pressureLight = 0.5 + 0.5 * sin(radius * 17.0 - t * 0.72);
        source.rgb *= 1.0 + vReveal * 0.045 + pressureLight * breath * luminance * 0.075;
      } else if (uMode < 3.5) {
        float turn = windowed(t, 39.2, 48.0, 1.8);
        float oculus = 1.0 - smoothstep(0.025, 0.22, radius);
        float ensemble = windowed(t, 25.0, 47.8, 2.4);
        source.rgb *= 1.0 + vReveal * 0.075 + ensemble * 0.018 + oculus * turn * luminance * 0.15;
      } else if (uMode < 4.5) {
        float firstRay = windowed(t, 8.0, 23.0, 2.2);
        float field = windowed(t, 18.0, 52.0, 3.0);
        float river = windowed(t, 41.0, 53.0, 1.8);
        float sweep = 1.0 - smoothstep(0.05, 0.34, abs(sin(angle * 0.5 - t * 0.095)));
        float tessera = smoothstep(0.12, 0.72, luminance);
        float silver = smoothstep(0.68, 0.92, max(source.b, source.g));
        source.rgb *= 1.0 + tessera * sweep * firstRay * 0.16 + tessera * field * (0.025 + 0.035 * sin(radius * 71.0 + angle * 9.0));
        source.rgb *= 1.0 + silver * river * 0.13;
      } else if (uMode < 5.5) {
        float cascade = windowed(t, 9.0, 56.0, 3.2);
        float inversion = windowed(t, 41.5, 55.5, 2.0);
        float grazing = 0.5 + 0.5 * sin(radius * 49.0 - t * 1.18 + angle * 0.8);
        float line = smoothstep(0.18, 0.66, luminance);
        source.rgb *= 1.0 + line * grazing * cascade * 0.12 + vReveal * 0.025;
        source.rgb *= 1.0 - inversion * (1.0 - radius) * 0.055;
      } else {
        float inward = windowed(t, 8.0, 52.0, 3.0);
        float returning = windowed(t, 50.0, 63.0, 2.0);
        float target = inward * (0.9 - 0.72 * smoothstep(8.0, 40.0, t)) + returning * (0.2 + 0.68 * smoothstep(50.0, 63.0, t));
        float band = (1.0 - smoothstep(0.035, 0.16, abs(radius - target))) * max(inward, returning);
        float line = smoothstep(0.1, 0.6, luminance);
        source.rgb *= 1.0 + line * band * 0.14 + vReveal * 0.04;
      }
      gl_FragColor = source;
    }
  `;

  const compileShader = (gl, type, source) => {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const message = gl.getShaderInfoLog(shader);
      gl.deleteShader(shader);
      throw new Error(message || 'shader compilation failed');
    }
    return shader;
  };

  const sourceActorData = scene => {
    const data = new Float32Array(104 * 4);
    const actorCount = scene.actorCount || 0;
    for (let index = 1; index <= actorCount; index += 1) {
      const plane = index / actorCount;
      const radius = 0.9 * Math.sqrt(plane);
      const angle = index * GOLDEN_ANGLE + (scene.actorSpin || 0);
      const offset = (index - 1) * 4;
      data[offset] = radius * Math.cos(angle);
      data[offset + 1] = radius * Math.sin(angle);
      data[offset + 2] = 0.026 + 0.026 * plane;
      data[offset + 3] = index;
    }
    return data;
  };

  const portalGeometry = (gl, divisions = 112) => {
    const side = divisions + 1;
    const positions = new Float32Array(side * side * 2);
    const indices = new Uint16Array(divisions * divisions * 6);
    let p = 0;
    for (let y = 0; y <= divisions; y += 1) {
      for (let x = 0; x <= divisions; x += 1) {
        positions[p++] = x / divisions * 2 - 1;
        positions[p++] = y / divisions * 2 - 1;
      }
    }
    let q = 0;
    for (let y = 0; y < divisions; y += 1) {
      for (let x = 0; x < divisions; x += 1) {
        const a = y * side + x;
        const b = a + 1;
        const c = a + side;
        const d = c + 1;
        indices[q++] = a; indices[q++] = b; indices[q++] = c;
        indices[q++] = b; indices[q++] = d; indices[q++] = c;
      }
    }
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);
    const indexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
    return { positionBuffer, indexBuffer, indexCount: indices.length };
  };

  const prepareSourcePerformance = session => {
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
      session.staticFallback = true;
      return;
    }
    const gl = session.canvas.getContext('webgl', { alpha: true, antialias: true, premultipliedAlpha: false, preserveDrawingBuffer: true });
    if (!gl || gl.getParameter(gl.MAX_VERTEX_UNIFORM_VECTORS) < 112) {
      session.staticFallback = true;
      return;
    }
    try {
      const vertex = compileShader(gl, gl.VERTEX_SHADER, SOURCE_VERTEX_SHADER);
      const fragment = compileShader(gl, gl.FRAGMENT_SHADER, SOURCE_FRAGMENT_SHADER);
      const program = gl.createProgram();
      gl.attachShader(program, vertex);
      gl.attachShader(program, fragment);
      gl.linkProgram(program);
      gl.deleteShader(vertex);
      gl.deleteShader(fragment);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) || 'shader link failed');

      const geometry = portalGeometry(gl);
      const texture = gl.createTexture();
      gl.useProgram(program);
      gl.bindBuffer(gl.ARRAY_BUFFER, geometry.positionBuffer);
      const positionLocation = gl.getAttribLocation(program, 'aPosition');
      gl.enableVertexAttribArray(positionLocation);
      gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, geometry.indexBuffer);
      gl.uniform4fv(gl.getUniformLocation(program, 'uActors[0]'), sourceActorData(session.scene));
      gl.uniform1f(gl.getUniformLocation(program, 'uMode'), session.scene.sourceMode || 0);
      gl.uniform1f(gl.getUniformLocation(program, 'uCycle'), session.scene.cycle || 60);
      gl.uniform1f(gl.getUniformLocation(program, 'uActorCount'), session.scene.actorCount || 0);
      gl.uniform1i(gl.getUniformLocation(program, 'uTexture'), 0);
      gl.disable(gl.DEPTH_TEST);
      gl.disable(gl.CULL_FACE);

      Object.assign(session, {
        sourceDriven: true,
        gl,
        program,
        geometry,
        texture,
        timeLocation: gl.getUniformLocation(program, 'uTime'),
        sourceImage: session.shell.querySelector('img'),
        textureReady: false
      });

      const upload = () => {
        if (!active || active !== session || !session.sourceImage?.naturalWidth) return;
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, session.sourceImage);
        session.textureReady = true;
        session.canvas.classList.add('world-scene--source', 'is-ready');
        session.sourceImage.classList.add('is-performance-source');
      };
      session.sourceLoadHandler = upload;
      if (session.sourceImage?.complete && session.sourceImage.naturalWidth) upload();
      else session.sourceImage?.addEventListener('load', upload, { once: true });
    } catch (error) {
      console.warn(`${session.world.key} source performance fallback:`, error);
      session.staticFallback = true;
    }
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
    if (session.sourceDriven) session.gl.viewport(0, 0, session.canvas.width, session.canvas.height);
    else session.ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
    session.size = cssSize;
  };

  const renderSourcePerformance = session => {
    if (!session.textureReady) return;
    const { gl, program, geometry } = session;
    gl.useProgram(program);
    gl.uniform1f(session.timeLocation, session.elapsed);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, session.texture);
    gl.bindBuffer(gl.ARRAY_BUFFER, geometry.positionBuffer);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, geometry.indexBuffer);
    gl.drawElements(gl.TRIANGLES, geometry.indexCount, gl.UNSIGNED_SHORT, 0);
  };

  const updateCue = session => {
    if (!session.scene.cues?.length) return;
    const phase = session.elapsed % (session.scene.cycle || 60);
    let cueIndex = 0;
    for (let index = 1; index < session.scene.cues.length; index += 1) {
      if (phase >= session.scene.cues[index].at) cueIndex = index;
    }
    if (cueIndex === session.cueIndex) return;
    session.cueIndex = cueIndex;
    const cue = session.scene.cues[cueIndex];
    if (session.labelNode) {
      session.labelNode.textContent = `сцена ${String(cueIndex + 1).padStart(2, '0')}/${String(session.scene.cues.length).padStart(2, '0')} · ${cue.label}`;
      session.labelNode.dataset.sequence = String(cueIndex + 1);
    }
    document.documentElement.dataset.sceneCue = String(cueIndex + 1);
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
    if (active.sourceDriven) {
      renderSourcePerformance(active);
    } else if (active.scene.kind === 'layered-procession' && !active.staticFallback) {
      const { ctx, size } = active;
      ctx.clearRect(0, 0, size, size);
      ctx.save();
      ctx.beginPath(); ctx.arc(size / 2, size / 2, size / 2, 0, TAU); ctx.clip();
      renderLayeredProcession(active);
      ctx.restore();
    } else if (!active.staticFallback) {
      const { ctx, size } = active;
      ctx.clearRect(0, 0, size, size);
      ctx.save();
      ctx.beginPath(); ctx.arc(size / 2, size / 2, size / 2, 0, TAU); ctx.clip();
      ctx.globalCompositeOperation = 'screen';
      renderers[active.scene.kind](active);
      renderAtmosphere(active);
      ctx.restore();
    }
    updateCue(active);

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
    active.sourceImage?.removeEventListener('load', active.sourceLoadHandler);
    active.sourceImage?.classList.remove('is-performance-source');
    if (active.labelNode) active.labelNode.removeAttribute('data-sequence');
    if (active.gl) {
      active.gl.deleteTexture(active.texture);
      active.gl.deleteBuffer(active.geometry?.positionBuffer);
      active.gl.deleteBuffer(active.geometry?.indexBuffer);
      active.gl.deleteProgram(active.program);
    }
    active.canvas.remove();
    active = null;
    delete document.documentElement.dataset.sceneWorld;
    delete document.documentElement.dataset.sceneKind;
    delete document.documentElement.dataset.sceneBeat;
    delete document.documentElement.dataset.sceneFrame;
    delete document.documentElement.dataset.sceneCue;
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
      ctx: scene.kind === 'source-performance' ? null : canvas.getContext('2d'),
      seed,
      objects,
      epoch,
      timing,
      size: 1,
      elapsed: 0,
      frameCount: 0,
      raf: 0,
      cueIndex: -1,
      labelNode: shell.closest('.dialog-visual')?.querySelector('.scene-label') || null,
      resizeObserver: 'ResizeObserver' in window ? new ResizeObserver(() => active && resize(active)) : null
    };
    if (scene.kind === 'source-performance') prepareSourcePerformance(active);
    if (scene.kind === 'layered-procession') prepareLayeredProcession(active);
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
    cue: Number(document.documentElement.dataset.sceneCue || 0),
    sourceDriven: Boolean(active.sourceDriven || active.staticFallback),
    textureReady: Boolean(active.textureReady),
    elapsed: Number(active.elapsed.toFixed(2))
  } : { active: false };

  const debugSeek = seconds => {
    if (!active) return null;
    // Deterministic time set for testing
    active.elapsed = seconds;
    active.epoch = performance.now() - seconds * 1000;
    // Force one frame render
    resize(active);
    if (active.sourceDriven) {
      renderSourcePerformance(active);
    } else if (active.scene.kind === 'layered-procession' && !active.staticFallback) {
      const { ctx, size } = active;
      ctx.clearRect(0, 0, size, size);
      ctx.save();
      ctx.beginPath(); ctx.arc(size / 2, size / 2, size / 2, 0, TAU); ctx.clip();
      renderLayeredProcession(active);
      ctx.restore();
    } else if (!active.staticFallback) {
      const { ctx, size } = active;
      ctx.clearRect(0, 0, size, size);
      ctx.save();
      ctx.beginPath(); ctx.arc(size / 2, size / 2, size / 2, 0, TAU); ctx.clip();
      ctx.globalCompositeOperation = 'screen';
      renderers[active.scene.kind](active);
      renderAtmosphere(active);
      ctx.restore();
    }
    updateCue(active);
    return {
      elapsed: active.elapsed,
      cue: active.cueIndex,
      kind: active.scene.kind,
      ready: active.scene.kind === 'layered-procession' ? active.layeredReady : (active.textureReady || !active.sourceDriven)
    };
  };

  // Compute average figure radius at given time (for verification)
  const debugMeanRadius = seconds => {
    if (!active || active.scene.kind !== 'layered-procession') return null;
    if (!active.layeredAtlas) return null;
    const cycle = active.scene.cycle || 60;
    const t = seconds % cycle;
    const beings = active.layeredAtlas.beings;
    let sum = 0;
    for (let i = 0; i < beings.length; i += 1) {
      const b = beings[i];
      const progress = portalThreeMovement(b, t, cycle);
      sum += b.r * (1 - progress);
    }
    return sum / beings.length;
  };

  window.WorldScene = { start, stop, presetFor, state, debugSeek, debugMeanRadius };
})();
