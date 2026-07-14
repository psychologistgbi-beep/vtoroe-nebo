(() => {
  const groups = [
    {
      id: 'self-organizing',
      number: 'I',
      title: 'Поля, которые растут сами',
      label: 'итерация · порог · самоорганизация',
      text: 'Здесь изображение не рисуется по контуру. Мы задаём начальное состояние, локальное правило и границу — затем поле само выращивает собственную погоду.'
    },
    {
      id: 'analytic',
      number: 'II',
      title: 'Следы невидимых законов',
      label: 'уравнение · узел · топология',
      text: 'Эти миры возникают как видимый след аналитического отношения: волны Бесселя, касания окружностей, причинность, линзирование или оборот фазы.'
    },
    {
      id: 'surface',
      number: 'III',
      title: 'Поверхность становится конструкцией',
      label: 'сфера · ячейка · грань · усилие',
      text: 'Рисунок перестаёт быть покрытием. Он задаёт площадь, угол, передачу усилия или реальную ориентацию граней и потому уже содержит зачаток архитектуры.'
    },
    {
      id: 'observer',
      number: 'IV',
      title: 'Наблюдатель входит в уравнение',
      label: 'направление · взгляд · связь · время',
      text: 'Полусфера здесь считается из положения человека, направления света или отношения между точками. Мир меняется вместе с местом, временем и собранием.'
    },
    {
      id: 'memory',
      number: 'V',
      title: 'Память свода',
      label: 'кессон · мозаика · мукарна · космограмма',
      text: 'Исторические языки не копируются как стиль. Их конструктивная грамматика — регистр, ярус, процессия, ниша, центр — переводится в вычислимую полярную систему.'
    }
  ];

  const worlds = [
    {
      key: 'phyllo', group: 'self-organizing', name: 'Филлотаксис', family: 'ботанический алгоритм',
      line: 'Каждое зерно получает собственный угловой адрес, а целое возникает без оси симметрии.',
      inspiration: 'Спиральное расположение семян подсолнечника и листьев вокруг стебля — природная задача плотной упаковки без центрального архитектора.',
      method: 'Зерно i получает радиус √(i/N) и золотоугольный поворот i·π(3−√5). Радиальный адрес переводится в угол от зенита.',
      unique: 'Нет повторяющегося сектора и главного меридиана: порядок узнаваем, хотя ни одна часть не является модулем для копирования.',
      state: 'Над собранием возникает вращающийся лес адресов: каждый занимает своё место, не образуя ни центра власти, ни периферийного остатка.',
      speed: 118, direction: 1
    },
    {
      key: 'reaction', group: 'self-organizing', name: 'Живая кожа', family: 'реакция–диффузия',
      line: 'Поверхность ведёт себя как ткань, на которой вещества одновременно питают и подавляют друг друга.',
      inspiration: 'Морфогенез Алана Тьюринга, пятна животных и лабораторная модель Gray–Scott: сложный рисунок рождается из простых локальных обменов.',
      method: 'Два поля диффундируют с разной скоростью и реагируют при фиксированных Du, Dv, feed и kill. Состояние поля переносится в угловые координаты полусферы.',
      unique: 'Орнамент не повторяется и не сочиняется: складки являются остановленным моментом процесса, который способен продолжаться.',
      state: 'Свод кажется живой оболочкой — не декором над людьми, а медленно меняющейся общей кожей.',
      speed: 154, direction: -1
    },
    {
      key: 'percol', group: 'self-organizing', name: 'Перколь', family: 'критическая перколяция',
      line: 'Связность возникает не постепенно, а почти мгновенно — когда поле достигает критического порога.',
      inspiration: 'Теория протекания: как вода, огонь или сигнал впервые находят непрерывный путь через случайную среду.',
      method: 'Детерминированная решётка заполняется при p=0,5927; сохраняются только кластеры, действительно связанные с границей.',
      unique: 'Цвет означает не украшение и не плотность, а доказанную достижимость — возможность пройти сквозь неоднородный мир.',
      state: 'Люди оказываются внутри карты возможности: соседство ещё ничего не гарантирует, важна непрерывная цепь отношений.',
      speed: 136, direction: 1
    },
    {
      key: 'vitel', group: 'self-organizing', name: 'Витель', family: 'вихревое поле',
      line: 'Линии не изображают ветер — они являются траекториями внутри рассчитанного поля скоростей.',
      inspiration: 'Динамика точечных вихрей, течения в воде и старые научные рисунки, где невидимое становилось видимым через линии тока.',
      method: 'Восемь подписанных вихрей создают векторное поле; численное интегрирование выпускает из разных адресов линии тока.',
      unique: 'Ни одна линия не проведена ради композиционного баланса: красота является совокупной биографией локальных сил.',
      state: 'Собрание чувствует себя не под статическим потолком, а внутри общего медленного вращения без единственного центра.',
      speed: 96, direction: -1
    },
    {
      key: 'frost', group: 'self-organizing', name: 'Изморозь', family: 'агрегация, ограниченная диффузией',
      line: 'Мир растёт от горизонта к зениту, присоединяя частицы только там, куда их приводит случайное блуждание.',
      inspiration: 'Иней на стекле, дендриты минералов и diffusion-limited aggregation — рост, в котором история пути остаётся в форме ветви.',
      method: 'Частицы блуждают до касания существующего кластера; фиксированный seed делает результат воспроизводимым, но не регулярным.',
      unique: 'Пустота участвует в построении наравне с ветвью: каждый новый отросток экранирует одни пути и открывает другие.',
      state: 'Полусфера становится зимней атмосферой, медленно захватывающей пространство над людьми от края к центру.',
      speed: 171, direction: 1
    },
    {
      key: 'mayatnik', group: 'self-organizing', name: 'Маятник', family: 'детерминированный хаос',
      line: 'Почти одинаковые начала расходятся в несовместимые траектории, хотя подчиняются одному уравнению.',
      inspiration: 'Двойной маятник как яснейшая модель чувствительности к начальным условиям и невозможности долгого предсказания.',
      method: 'Восемь близких состояний интегрируются методом RK4 с малым временным шагом; траектории укладываются в полярное поле.',
      unique: 'Различие миров возникает без случайного генератора: его производит сама нелинейная динамика.',
      state: 'Над собранием висит архив разошедшихся судеб — напоминание, что близкое начало не обещает общего финала.',
      speed: 128, direction: -1
    },
    {
      key: 'nabor', group: 'self-organizing', name: 'Набор', family: 'клеточный автомат',
      line: 'Одна короткая строка правила последовательно разворачивается в целое небо.',
      inspiration: 'Rule 30 Стивена Вольфрама: элементарный автомат, способный породить визуальную сложность из бинарного соседства.',
      method: 'Новое состояние каждой клетки зависит только от трёх предыдущих; поколения записываются не строками, а полярными кольцами.',
      unique: 'Линейное время автомата превращено в высоту полусферы: история вычисления становится архитектурным разрезом.',
      state: 'Свод читается как машина памяти — настоящее у горизонта несёт в себе все предыдущие кольца.',
      speed: 142, direction: 1
    },
    {
      key: 'chern', group: 'self-organizing', name: 'Чернь-домен', family: 'критическое поле Изинга',
      line: 'Малые и большие домены существуют одновременно: у критической точки мир теряет привычный масштаб.',
      inspiration: 'Модель Изинга и поведение ферромагнетика около фазового перехода, где локальное согласие внезапно становится дальним.',
      method: 'Дискретные спины эволюционируют около Tc=2,269; изображение кодирует образовавшиеся домены и их границы.',
      unique: 'Узору нельзя назначить один размер модуля — структура статистически самоподобна на нескольких масштабах.',
      state: 'Люди находятся под небом коллективного решения, ещё не ставшего ни порядком, ни хаосом.',
      speed: 164, direction: -1
    },

    {
      key: 'beam', group: 'analytic', name: 'Автопортрет слуха', family: 'дифракционная функция',
      line: 'Инструмент показывает не внешний мир, а собственную способность различать направление и частоту.',
      inspiration: 'Диск Эйри, диаграммы направленности антенн и сходство между оптической апертурой и слушающим отверстием.',
      method: 'Интенсивность задаётся jinc-функцией (2J₁(11r)/(11r))²; радиальная координата становится угловым расстоянием от зенита.',
      unique: 'Это портрет не предмета, а измерительного ограничения: мир рисуется тем, как система умеет принимать сигнал.',
      state: 'Под куполом слышание ощущается как пространство концентрических зон внимания и выпадения.',
      speed: 190, direction: 1
    },
    {
      key: 'chladni', group: 'analytic', name: 'Камертон', family: 'собственные волновые моды',
      line: 'Золотые линии показывают места покоя внутри продолжающегося колебания.',
      inspiration: 'Фигуры Хладни и экспериментальная традиция, в которой песок обнаруживает невидимые узлы звучащей поверхности.',
      method: 'Складываются две моды круглой мембраны на функциях Бесселя J₇ и J₃; нулевые уровни становятся световым скелетом.',
      unique: 'Тишина впервые является не пустотой между звуками, а геометрией, которая организует весь звук.',
      state: 'Собрание оказывается внутри колебания, удерживаемого неподвижными руслами общей паузы.',
      speed: 112, direction: -1
    },
    {
      key: 'apollon', group: 'analytic', name: 'Апейрон', family: 'рекурсивная геометрия касаний',
      line: 'Пустое место никогда не остаётся остатком: каждый просвет получает следующий круг.',
      inspiration: 'Аполлониева упаковка и теорема Декарта о четырёх взаимно касающихся окружностях.',
      method: 'Кривизна и центр нового круга вычисляются из тройки соседей; рекурсия продолжается до объявленного масштаба.',
      unique: 'Бесконечность не изображена далёкой перспективой — она материально присутствует в каждом локальном промежутке.',
      state: 'Мир становится обществом касаний: большие и малые формы равноправно продолжают одно отношение.',
      speed: 148, direction: 1
    },
    {
      key: 'caustic', group: 'analytic', name: 'Небо каустик', family: 'тонколинзовое отображение',
      line: 'Невидимое тело читается по тому, как оно искривляет чужой свет.',
      inspiration: 'Гравитационное линзирование, дуги далёких галактик и каустики как следы предельной концентрации отображения.',
      method: 'Бинарная тонкая линза переводит координаты источника в несколько изображений; критическая кривая отмечает det(A)=0.',
      unique: 'Центральный объект почти отсутствует: его величие измеряется изменёнными траекториями вокруг него.',
      state: 'Собрание учится видеть присутствие косвенно — по изгибам путей, а не по монументу в центре.',
      speed: 104, direction: -1
    },
    {
      key: 'chrono', group: 'analytic', name: 'Хроносвод', family: 'причинный порядок',
      line: 'События связаны не сходством, а возможностью успеть повлиять друг на друга.',
      inspiration: 'Диаграммы Минковского и causal-set мысль: пространство-время можно читать как частичный порядок событий.',
      method: 'Для событий в 1+1 измерении проверяется условие dt>|dx|, затем удаляются транзитивно избыточные связи.',
      unique: 'Граф показывает минимальный скелет влияния: связь существует только там, где без неё причинная история изменилась бы.',
      state: 'Под сводом совместность становится временным достижением — редкой областью, где голоса ещё способны менять продолжение.',
      speed: 132, direction: 1
    },
    {
      key: 'superfluid', group: 'analytic', name: 'Сверхтекучее небо', family: 'топологическая фаза',
      line: 'Вращение существует отдельными целыми оборотами вокруг тёмных ядер.',
      inspiration: 'Квантованные вихри сверхтекучей жидкости и фазовые поля комплексного параметра порядка.',
      method: 'Фаза складывается из atan2 вокруг решётки одноимённых вихрей; цвет кодирует угол, линии следуют его градиенту.',
      unique: 'Движение хранится не скоростью поверхности, а топологическим числом, которое нельзя убрать малой деформацией.',
      state: 'Над людьми возникает спокойная материя, внутри которой память о вращении закреплена множеством узлов.',
      speed: 88, direction: -1
    },

    {
      key: 'tyaga', group: 'surface', name: 'Тяга', family: 'иерархия передачи усилия',
      line: 'Малые периферийные линии сходятся и утолщаются, потому что каждая несёт сумму предыдущих.',
      inspiration: 'Готические нервюры, ветвящиеся деревья и конструкции, в которых форма позволяет буквально прочитать путь нагрузки.',
      method: 'Пограничные адреса попарно агрегируются через несколько полярных уровней; толщина кодирует накопленное усилие.',
      unique: 'Центр не раздаёт силу наружу — он обязан своим существованием множеству малых тяг с горизонта.',
      state: 'Величие переживается как способность нести друг друга, а не как масса, подавляющая снизу.',
      speed: 176, direction: 1
    },
    {
      key: 'equal_area', group: 'surface', name: 'Собор равных ячеек', family: 'равновеликая сферическая мозаика',
      line: 'Очертания различаются, но физическая площадь каждой ячейки на сфере одинакова.',
      inspiration: 'Равновеликие картографические проекции и идея собрания, где визуальный размер не превращается в ранг.',
      method: 'Границы по θ получены равными приращениями cos(θ); сектора дают равные сферические площади.',
      unique: 'Равенство достигается не одинаковой картинкой, а намеренной деформацией очертания ради сохранения реальной площади.',
      state: 'Каждому присутствию принадлежит равная часть общего неба, даже если с пола она выглядит иначе.',
      speed: 186, direction: -1
    },
    {
      key: 'conformal', group: 'surface', name: 'Конформное небо', family: 'углосохраняющая сеть',
      line: 'Масштаб меняется по высоте, но локальный прямой угол остаётся договором частей.',
      inspiration: 'Кессоны Пантеона и сферические координаты Меркатора — соединение архитектурной памяти с математикой сохранения угла.',
      method: 'Пояса строятся равными шагами u=ln tan(θ/2) и v=φ; обратное отображение возвращает их на полусферу.',
      unique: 'Система разрешает элементам уменьшаться, не теряя локального родства и ориентации.',
      state: 'Человек проходит от плотной памяти к свободному зениту, сохраняя чувство порядка при изменении масштаба.',
      speed: 166, direction: 1
    },
    {
      key: 'light_muqarnas', group: 'surface', name: 'Световая мукарна', family: 'план, поднятый в глубину',
      line: 'Радиальный чертёж становится нишами, а свет возникает из реальных ориентаций граней.',
      inspiration: 'Мукарны и Topkapı Scroll: двухмерная конструктивная грамматика, способная порождать пространственные ярусы.',
      method: 'Счёт ячеек растёт 4→8→16→32; точки плана поднимаются в 112 ниш и 448 фасеток, освещённых по нормалям.',
      unique: 'Тень не нарисована поверх орнамента: она является доказательством того, что плоскость действительно получила глубину.',
      state: 'Над собранием возникает минеральное облако, дробящее единый свет на множество пространственных свидетельств.',
      speed: 124, direction: -1
    },

    {
      key: 'parallax_covenant', group: 'observer', name: 'Свод несводимых взглядов', family: 'обратная проекция',
      line: 'Одна оболочка несёт разные цельные образы для разных мест человека.',
      inspiration: 'Архитектурный анаморфоз, квадратура и современная view-dependent fabrication, где глаз входит в геометрию объекта.',
      method: 'Лучи из трёх заданных позиций пересекают полусферу и обратной проекцией записывают три семейства линий.',
      unique: 'Ни один взгляд не объявлен универсальным, но каждый остаётся математически проверяемым из собственного места.',
      state: 'Понимание требует движения: человек покидает свой цельный образ, чтобы увидеть правду другого положения.',
      speed: 108, direction: 1
    },
    {
      key: 'hopf_covenant', group: 'observer', name: 'Собор неразрывных связей', family: 'волокна Хопфа в объёме',
      line: 'Пути нигде не пересекаются, но каждый топологически зацеплен с каждым.',
      inspiration: 'Расслоение Хопфа — редкая математическая модель близости без слияния и связи без общего узла.',
      method: 'Волокна вычисляются в S³, стереографически переходят в R³ и компактно размещаются в объёме купола.',
      unique: 'Главным телом становится не оболочка, а связанная пустота между нею и людьми.',
      state: 'Собрание находится внутри доказуемого отношения: отдельность сохраняется, но изъять одну связь без изменения целого нельзя.',
      speed: 92, direction: -1
    },
    {
      key: 'three_suns', group: 'observer', name: 'Свод трёх времён', family: 'обратная геометрическая оптика',
      line: 'Одна кожа исполняет разные световые программы утром, днём и вечером.',
      inspiration: 'Гелиостаты, солнечные часы и inverse design — проектирование поверхности от желаемого светового события.',
      method: 'Для каждой микрофасетки решается нормаль, отражающая один из трёх солнечных векторов в заданную точку пола.',
      unique: 'Время не меняет готовую архитектуру подсветкой; оно является соавтором самой ориентации элементов.',
      state: 'Собрание проживает путь, круг и схождение как три разных состояния одного физического неба.',
      speed: 158, direction: 1
    },
    {
      key: 'mutual_horizons', group: 'observer', name: 'Собор взаимных горизонтов', family: 'нативное геодезическое поле',
      line: 'Каждая связь между двумя адресами проходит через общее небо и встречает другие связи.',
      inspiration: 'Большие окружности навигации, геодезические сети и идея обещания, которое становится общественным фактом.',
      method: 'Пятнадцать плоскостей через центр сферы задают great circles; пересечения вычислены точно из cross(nᵢ,nⱼ).',
      unique: 'Линии не проецировались с плоского листа: каждый пиксель изначально знает собственное направление на полусфере.',
      state: 'Горизонт перестаёт быть границей — он становится адресной книгой отношений, проходящих над всем собранием.',
      speed: 78, direction: -1
    },
    {
      key: 'common_pulse', group: 'observer', name: 'Свод совместной паузы', family: 'нативные сферические волны',
      line: 'Разные пульсы не обязаны совпасть фазой, чтобы на мгновение образовать общую нулевую линию.',
      inspiration: 'Интерференция волн, дыхание группы и пауза как активное совместное событие, а не отсутствие голоса.',
      method: 'Источники заданы направлениями на сфере; расстояние δ=acos(s·d) питает когерентную суперпозицию на каждом пикселе master.',
      unique: 'Общность возникает из продолжающихся различий: отдельные волны не гасятся, хотя их сумма локально равна нулю.',
      state: 'Полусфера становится дыхательной мембраной, где собрание впервые видит форму своей общей паузы.',
      speed: 68, direction: 1
    },
    {
      key: 'habitable_boundary', group: 'observer', name: 'Собор обитаемой границы', family: 'нативная сферическая диффузия',
      line: 'Мир живёт не в вечном дне и не в вечной ночи, а в полосе обмена между ними.',
      inspiration: 'Приливно захваченные экзопланеты, терминатор и климатическая мысль об обитаемости как балансе крайностей.',
      method: 'Полусферическое освещение max(d·star,0) сглаживается оператором сферической диффузии через ряд Лежандра.',
      unique: 'Граница не разделяет две готовые области: именно передача через неё создаёт единственное пригодное для жизни состояние.',
      state: 'Люди собираются вдоль световой климатической полосы — пространства переговоров между двумя необитаемыми абсолютами.',
      speed: 214, direction: -1
    },

    {
      key: 'portal_1', group: 'memory', name: 'Портал I', family: 'барочная полярная квадратура',
      line: 'Кессонные регистры превращают конечный потолок в тёплый золотой провал.',
      inspiration: 'Квадратура Андреа Поццо и барочная практика продолжать реальную архитектуру иллюзорной системой над ней.',
      method: 'Семь полярных регистров строят перспективу к окулюсу; фигуры получают адреса по золотоугольной последовательности.',
      unique: 'Барочная глубина переведена из единственной фронтальной перспективы в окружной язык Dome Master.',
      state: 'Собрание входит под открывающийся вверх церемониальный космос тёплого света.',
      speed: 122, direction: 1
    },
    {
      key: 'portal_2', group: 'memory', name: 'Портал II', family: 'серебряная полярная квадратура',
      line: 'Та же грамматика теряет золото и становится холодной архитектурой дистанции.',
      inspiration: 'Барочная квадратура, прочитанная через металлический свет планетария и серебряный экран проекции.',
      method: 'Ярусы, кессоны и фигуры сохраняют общий алгоритм первого портала, но другой световой прогон меняет иерархию глубины.',
      unique: 'Вариант показывает, что палитра в вычислимом своде способна менять социальную температуру, не меняя геометрии.',
      state: 'Полусфера ощущается как холодный зал ожидания перед неизвестным небом.',
      speed: 138, direction: -1
    },
    {
      key: 'portal_3', group: 'memory', name: 'Портал III', family: 'процессуальная полярная квадратура',
      line: 'Фигуры сходят с регистров, и архитектурная память превращается в процесс движения.',
      inspiration: 'Купольные процессии, театральная машина барокко и изображение небесного порядка как события, а не фона.',
      method: 'Третий детерминированный прогон изменяет фазы регистров, свет и распределение фигур внутри той же полярной системы.',
      unique: 'Вместо идеальной симметрии появляется направленное течение — небо начинает иметь хореографию.',
      state: 'Люди чувствуют над собой медленное переселение образов от горизонта к зениту.',
      speed: 106, direction: 1
    },
    {
      key: 'san_marco', group: 'memory', name: 'Сан-Марко', family: 'мозаичное поле памяти',
      line: 'Золотой фон перестаёт быть пустотой и становится веществом общей памяти.',
      inspiration: 'Византийские мозаики Сан-Марко, процессуальные регистры и свет, который отражается от тессер, а не изображается краской.',
      method: 'Полярная тесселяция образует фон; две окружные процессии фигур получают независимые ритмы и масштабы.',
      unique: 'Память распределена по оболочке и не сводится к центральной иконе: взгляд должен обходить весь горизонт.',
      state: 'Полусфера становится золотым архивом присутствий, где человек находится внутри памяти, а не перед ней.',
      speed: 184, direction: -1
    },
    {
      key: 'muqarnas', group: 'memory', name: 'Мукарны', family: 'адаптивные полярные ярусы',
      line: 'Единая оболочка дробится на множество малых ниш, сохраняя родство всех ярусов.',
      inspiration: 'Исламские мукарны как переход от квадратного основания к куполу через счёт, повторение и контролируемое дробление.',
      method: 'Десять вложенных ярусов получают адаптивное число ячеек; профиль каждой ниши вычисляется из положения в кольце.',
      unique: 'Алгоритм сохраняет идею мукарны как операции перехода, не копируя конкретный исторический памятник.',
      state: 'Над людьми возникает пористая минеральная толща, в которой большое небо состоит из множества малых небес.',
      speed: 146, direction: 1
    },
    {
      key: 'mandala', group: 'memory', name: 'Мандала', family: 'вычислимая космограмма',
      line: 'Центр, кольца и меридианы превращают полусферу в карту пути внимания.',
      inspiration: 'Мандалы и космограммы как не изображения предмета, а инструкции движения от внешнего мира к центру и обратно.',
      method: 'Одиннадцать угловых колец, меридианы и три регистра розеток строятся как точные полярные отношения.',
      unique: 'Симметрия используется не как декор, а как интерфейс медленного чтения пространства телом и взглядом.',
      state: 'Собрание получает общее внутреннее направление, не требующее сцены или фигуры над центром.',
      speed: 202, direction: -1
    }
  ];

  const editorial = window.VTOROE_NEBO_COPY || {};
  groups.forEach(group => Object.assign(group, editorial.groups?.[group.id] || {}));
  worlds.forEach(world => Object.assign(world, editorial.worlds?.[world.key] || {}));

  const byKey = new Map(worlds.map(world => [world.key, world]));
  const byGroup = new Map(groups.map(group => [group.id, group]));
  const root = document.getElementById('world-groups');
  const dialog = document.getElementById('world-dialog');
  const soundButton = dialog.querySelector('[data-sound-toggle]');
  const soundLabel = dialog.querySelector('[data-sound-label]');
  let openedKey = null;
  let openedEpoch = 0;
  let userMuted = false;
  let lastTrigger = null;

  const driftMotions = new Map([
    ['reaction',          { path: 'drift',         speed: 64, direction: 'normal',  delay: -19 }],
    ['percol',            { path: 'drift-lateral', speed: 72, direction: 'reverse', delay: -31 }],
    ['vitel',             { path: 'drift',         speed: 58, direction: 'normal',  delay: -27 }],
    ['frost',             { path: 'drift-lateral', speed: 86, direction: 'reverse', delay: -43 }],
    ['mayatnik',          { path: 'drift-lateral', speed: 68, direction: 'normal',  delay: -36 }],
    ['chern',             { path: 'drift',         speed: 76, direction: 'reverse', delay: -14 }],
    ['caustic',           { path: 'drift-lateral', speed: 62, direction: 'normal',  delay: -47 }],
    ['chrono',            { path: 'drift-lateral', speed: 81, direction: 'reverse', delay: -23 }],
    ['superfluid',        { path: 'drift',         speed: 54, direction: 'normal',  delay: -38 }],
    ['parallax_covenant', { path: 'drift-lateral', speed: 66, direction: 'reverse', delay: -29 }],
    ['hopf_covenant',     { path: 'drift',         speed: 74, direction: 'normal',  delay: -51 }],
    ['mutual_horizons',   { path: 'drift-lateral', speed: 57, direction: 'reverse', delay: -17 }],
    ['common_pulse',      { path: 'drift',         speed: 60, direction: 'normal',  delay: -42 }],
    ['habitable_boundary',{ path: 'drift-lateral', speed: 78, direction: 'reverse', delay: -34 }]
  ]);

  const motionFor = world => driftMotions.get(world.key);

  const setSoundUI = state => {
    const labels = {
      starting: 'мир настраивает звучание…',
      ready: 'нажмите, чтобы услышать этот мир',
      playing: 'звучание включено · нажмите для паузы',
      paused: 'звучание на паузе · нажмите, чтобы продолжить',
      unavailable: 'звучание недоступно в этом браузере'
    };
    soundButton.dataset.state = state;
    soundButton.disabled = state === 'starting' || state === 'unavailable';
    soundButton.setAttribute('aria-pressed', String(state === 'playing'));
    soundLabel.textContent = labels[state];
  };

  const planet = (world, modal = false) => {
    const drift = motionFor(world);
    const motion = drift
      ? `data-motion="${drift.path}" style="--drift-speed:${drift.speed}s;--drift-delay:${drift.delay}s;--drift-direction:${drift.direction}"`
      : `data-motion="spin" style="--spin:${world.speed}s;--spin-end:${world.direction * 360}deg"`;
    const base = `img/fulldome/web/${world.key}_domemaster`;
    const sizes = modal ? '(max-width:700px) 72vw, 480px' : '(max-width:700px) 44vw, (max-width:980px) 30vw, 300px';
    return `
    <span class="planet-shell${modal ? ' modal-planet' : ''}" ${motion}>
      <picture>
        <source type="image/webp" srcset="${base}_512.webp 512w, ${base}_1024.webp 1024w" sizes="${sizes}">
        <img src="${base}_1024.png?v=17" ${modal ? 'decoding="async"' : 'loading="lazy" decoding="async"'} alt="" onerror="this.closest('.planet-shell').classList.add('img-missing')">
      </picture>
      <span class="planet-glint" aria-hidden="true"></span>
    </span>`;
  };

  root.innerHTML = `
    <nav class="group-index" aria-label="Методы создания миров">
      ${groups.map(group => `<a href="#group-${group.id}"><span>${group.number}</span>${group.title}</a>`).join('')}
    </nav>
    ${groups.map(group => {
      const groupWorlds = worlds.filter(world => world.group === group.id);
      return `
        <section class="world-group" id="group-${group.id}" data-reveal>
          <header class="group-head">
            <div class="group-number">Метод ${group.number}</div>
            <h3>${group.title}</h3>
            <div class="group-method">${group.label}</div>
            <p>${group.text}</p>
          </header>
          <div class="world-grid">
            ${groupWorlds.map((world, index) => `
              <article class="world-card${index === 0 ? ' world-card--lead' : ''}" data-reveal style="--delay:${(index % 6) * 55}ms">
                <button class="planet-button" type="button" data-world="${world.key}" aria-haspopup="dialog" aria-label="Открыть мир «${world.name}»">
                  ${planet(world)}
                </button>
                <div class="world-card-copy">
                  <span class="world-family">${world.family}</span>
                  <h4>${world.name}</h4>
                  <p>${world.line}</p>
                  <button class="read-world" type="button" data-world="${world.key}" aria-haspopup="dialog" aria-label="Войти в мир «${world.name}»">войти в мир <span aria-hidden="true">↗</span></button>
                </div>
              </article>`).join('')}
          </div>
        </section>`;
    }).join('')}`;

  const hashWorld = () => { const m = location.hash.match(/^#world-(.+)$/); return m && byKey.has(m[1]) ? m[1] : null; };
  if (location.hash && !hashWorld()) {
    requestAnimationFrame(() => document.querySelector(location.hash)?.scrollIntoView({ behavior: 'instant' }));
  }

  const openWorld = (key, push = true) => {
    const world = byKey.get(key);
    if (!world) return;
    if (dialog.open && openedKey === world.key) return;
    if (dialog.open) dialog.close();
    const group = byGroup.get(world.group);
    const drift = motionFor(world);
    const scene = window.WorldScene?.presetFor(world.key) || { kind: 'wave', label: 'движение мира', event: 'Мир меняется в собственном темпе.' };
    openedKey = world.key;
    openedEpoch = performance.now();
    dialog.classList.remove('immersive');
    dialog.querySelector('.dialog-visual').innerHTML = `${planet(world, true)}
      <div class="scene-console">
        <span class="scene-label">событие · ${scene.label}</span>
        <button class="immersion-toggle" type="button" data-immersion-toggle aria-pressed="false">развернуть под купол</button>
      </div>`;
    dialog.querySelector('.dialog-group').textContent = `${group.title} · ${world.family}`;
    dialog.querySelector('.dialog-title').textContent = world.name;
    dialog.querySelector('.dialog-lede').textContent = world.line;
    dialog.querySelector('[data-field="event"]').textContent = scene.event;
    dialog.querySelector('[data-field="inspiration"]').textContent = world.inspiration;
    dialog.querySelector('[data-field="method"]').textContent = world.method;
    dialog.querySelector('[data-field="unique"]').textContent = world.unique;
    dialog.querySelector('[data-field="state"]').textContent = world.state;
    dialog.querySelector('[data-field="sound"]').textContent = world.sound || 'Звучание следует тому же правилу, что и изображение, и каждый раз собирается заново в вашем браузере.';
    dialog.querySelector('[data-motion-note]').textContent = drift
      ? 'У этого поля нет одного центра, поэтому оно не закручивается, а медленно сползает по оболочке.'
      : 'Здесь центр важен: мир неторопливо поворачивается вокруг зенита и сохраняет свою полярную форму.';
    dialog.querySelector('[data-link="master"]').href = `img/fulldome/${world.key}_domemaster_4k.png`;
    dialog.querySelector('[data-link="preview"]').href = `img/fulldome/previews/${world.key}_front_35.png`;
    dialog.showModal();
    dialog.scrollTop = 0;
    document.body.classList.add('modal-open');
    if (push) history.pushState({ world: world.key }, '', '#world-' + world.key);
    const soundWorld = { ...world, visualCycle: drift?.speed || world.speed, motion: drift?.path || 'spin', scene: scene.kind, scenePeriod: scene.period, sceneSulfur: scene.sulfur, sceneFierce: scene.fierce, sceneDeep: scene.deep, epoch: openedEpoch };
    const timing = window.WorldSound?.timing?.(soundWorld) || { visualCycle: soundWorld.visualCycle, beatSeconds: 1.25 };
    window.WorldScene?.start({ world, shell: dialog.querySelector('.modal-planet'), epoch: openedEpoch, timing });
    if (userMuted) { setSoundUI('ready'); return; }
    setSoundUI('starting');
    Promise.resolve(window.WorldSound?.play(soundWorld) ?? false)
      .then(started => {
        if (!dialog.open || openedKey !== world.key) {
          window.WorldSound?.stop();
          return;
        }
        setSoundUI(started === 'playing' ? 'playing' : started === 'ready' ? 'ready' : 'unavailable');
      })
      .catch(() => setSoundUI('unavailable'));
  };

  const startCurrentSound = () => {
    const world = byKey.get(openedKey);
    if (!world) return;
    const drift = motionFor(world);
    const scene = window.WorldScene?.presetFor(world.key) || { kind: 'wave' };
    userMuted = false;
    setSoundUI('starting');
    Promise.resolve(window.WorldSound?.play({ ...world, visualCycle: drift?.speed || world.speed, motion: drift?.path || 'spin', scene: scene.kind, scenePeriod: scene.period, sceneSulfur: scene.sulfur, sceneFierce: scene.fierce, sceneDeep: scene.deep, epoch: openedEpoch }) ?? false)
      .then(started => setSoundUI(started === 'playing' ? 'playing' : started === 'ready' ? 'ready' : 'unavailable'))
      .catch(() => setSoundUI('unavailable'));
  };

  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-world]');
    if (trigger) { lastTrigger = trigger; openWorld(trigger.dataset.world); }
  });

  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  soundButton.addEventListener('click', () => {
    if (soundButton.dataset.state === 'ready') { startCurrentSound(); return; }
    const playing = window.WorldSound?.toggle();
    userMuted = !playing;
    setSoundUI(playing ? 'playing' : 'paused');
  });
  dialog.addEventListener('click', event => {
    const immersionButton = event.target.closest('[data-immersion-toggle]');
    if (immersionButton) {
      const immersive = dialog.classList.toggle('immersive');
      immersionButton.setAttribute('aria-pressed', String(immersive));
      immersionButton.textContent = immersive ? 'вернуться к описанию' : 'развернуть под купол';
      requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
      return;
    }
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => {
    openedKey = null;
    openedEpoch = 0;
    window.WorldSound?.stop();
    window.WorldScene?.stop();
    dialog.classList.remove('immersive');
    document.body.classList.remove('modal-open');
    if (location.hash.startsWith('#world-')) history.replaceState(null, '', location.pathname + location.search);
    lastTrigger?.focus?.();
  });
  window.addEventListener('popstate', () => {
    const k = hashWorld();
    if (k) { if (openedKey !== k) openWorld(k, false); }
    else if (dialog.open) dialog.close();
  });
  if (hashWorld()) requestAnimationFrame(() => openWorld(hashWorld(), false));

  const hero = document.querySelector('.hero');
  requestAnimationFrame(() => requestAnimationFrame(() => hero.classList.add('in')));
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        observer.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -10% 0px' });
  document.querySelectorAll('[data-reveal]').forEach(element => observer.observe(element));

  const motionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.target.classList.toggle('card-visible', entry.isIntersecting));
  }, { rootMargin: '160px 0px' });
  document.querySelectorAll('.world-card').forEach(card => motionObserver.observe(card));
})();
