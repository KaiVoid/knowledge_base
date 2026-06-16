# Современные возможности Java — часть 2 из 2

> Вопросы 21–40 (в части: 20). Всего в разделе: 40.
> Область знаний: [../knowledge-base/09-modern-java-features.md](../knowledge-base/09-modern-java-features.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](modern-java-01.md) · **ч.2**

---
### Вопрос 21. В чём разница между Period и Duration в java.time? Почему добавление Period.ofDays(1) к ZonedDateTime может дать результат, отличный от прибавления Duration.ofHours(24)?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Period and Duration (The Java™ Tutorials > Date Time > Standard Calendar)](https://docs.oracle.com/javase/tutorial/datetime/iso/period.html)

`Duration` измеряет количество времени, используя временны́е единицы (секунды, наносекунды). Это машинное представление времени, удобное для работы с `Instant`. `Period` измеряет количество времени, используя единицы дат (годы, месяцы, дни). Это «человеческое» представление промежутка.

Ключевое различие проявляется при прибавлении к `ZonedDateTime`:

> «Duration одного дня — это ровно 24 часа. Period одного дня, добавленный к ZonedDateTime, может варьироваться в зависимости от часового пояса — например, если это происходит в первый или последний день перехода на летнее/зимнее время.»

Практический пример из документации Oracle:

> «Рассмотрим добавление периода одного дня и продолжительности одного дня к 18:00 накануне перехода на летнее время (DST-gap). `Period` добавит концептуальный день и результатом будет `ZonedDateTime` в 18:00 следующего дня. Напротив, `Duration` добавит ровно 24 часа, и результатом будет `ZonedDateTime` в 19:00 следующего дня (при условии перехода в 1 час).»

Пример расчёта возраста с помощью `Period`:

```java
LocalDate today = LocalDate.now();
LocalDate birthday = LocalDate.of(1960, Month.JANUARY, 1);
Period p = Period.between(birthday, today);
System.out.println("Вам " + p.getYears() + " лет, "
    + p.getMonths() + " месяцев и "
    + p.getDays() + " дней.");
```

#### Ответ от Claude

**Фундаментальное различие в семантике**

| Аспект | `Period` | `Duration` |
|---|---|---|
| Что измеряет | Дата-ориентированный промежуток: годы, месяцы, дни | Время-ориентированный промежуток: секунды, наносекунды |
| Строковое представление | `P2Y3M10D` | `PT24H` / `PT86400S` |
| Типичное применение | «Следующий месяц», «через год», «два дня спустя» | «Через 30 секунд», «ровно 2 часа» |
| Связь с часовым поясом | Учитывает локальный календарь и DST | Добавляет фиксированное количество секунд |

**Почему Period.ofDays(1) != Duration.ofHours(24) на ZonedDateTime**

`Duration.ofHours(24)` прибавляет ровно 86 400 секунд к таймлайну — независимо от часового пояса и перехода на летнее/зимнее время. `Period.ofDays(1)` прибавляет один «концептуальный» календарный день, пытаясь сохранить локальное время суток.

Сценарий: переход на летнее время (DST spring-forward, сдвиг +1 час):

```java
ZoneId zone = ZoneId.of("Europe/Moscow"); // или "America/New_York"
// Допустим, в ночь с 26 на 27 марта часы переводят вперёд на 1 час
ZonedDateTime before = ZonedDateTime.of(
    LocalDateTime.of(2025, 3, 29, 18, 0), // 18:00 накануне перехода
    ZoneId.of("Europe/Paris")              // Париж: переход в эту ночь
);

ZonedDateTime plusPeriod   = before.plus(Period.ofDays(1));
ZonedDateTime plusDuration = before.plus(Duration.ofHours(24));

System.out.println(plusPeriod);   // 2025-03-30T18:00+02:00[Europe/Paris]
System.out.println(plusDuration); // 2025-03-30T19:00+02:00[Europe/Paris]
```

`Period.ofDays(1)` сохранил локальное время 18:00 — переход DST компенсирован автоматически (добавлен 21 час реального времени вместо 24). `Duration.ofHours(24)` добавил ровно 24 часа реального времени, поэтому локальное время стало 19:00.

Аналогичная разница возникает в обратную сторону (DST fall-back, сдвиг −1 час): `Period.ofDays(1)` даст 18:00 следующего дня, а `Duration.ofHours(24)` — 17:00.

**Источник разницы на уровне реализации**

Метод `ZonedDateTime.plus(Period)` конвертирует к `LocalDateTime`, прибавляет дни/месяцы/годы в локальном времени, а затем снова применяет правила зоны. Метод `ZonedDateTime.plus(Duration)` конвертирует к `Instant`, прибавляет секунды, конвертирует обратно — смещение пересчитывается по новому моменту.

**Практические рекомендации**

- Используйте `Period`, когда важно «то же время завтра» или «тот же день следующего месяца» — например, при расписаниях встреч, напоминаниях, расчёте дат истечения.
- Используйте `Duration`, когда нужен точный интервал времени — тайм-ауты, кэш TTL, измерение производительности.
- `Period` работает только с датами (`LocalDate`, `ZonedDateTime`), но не с `Instant`. `Duration` — с `Instant` и `ZonedDateTime`, но не с `LocalDate` напрямую.

**Расхождения между источниками:** Oracle Tutorial и Javadoc SE 25 согласованны в описании поведения. Jenkov.com рекомендует `Period` для расчётов через DST-границы с `ZonedDateTime`, что соответствует позиции Oracle.

---

### Вопрос 22. Как text block обрабатывает leading whitespace (отступы)? Что такое «incidental whitespace» и как позиция закрывающих кавычек (""") влияет на результирующую строку?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Programmer's Guide to Text Blocks (Oracle Java SE 18)](https://docs.oracle.com/en/java/javase/18/text-blocks/index.html)

Text block автоматически различает **incidental whitespace** («случайные» отступы, добавленные для выравнивания кода) и **essential whitespace** («существенные» пробелы, являющиеся частью строки).

**Алгоритм повторного выравнивания (re-indentation algorithm)**

Алгоритм прост: весь контент текст-блока сдвигается влево до тех пор, пока строка с наименьшим количеством ведущих пробелов не окажется в позиции 0. Строки с наименьшим отступом задают «левую границу» — всё что левее считается incidental и удаляется.

Пример:

```java
void writeHTML() {
    String html = """
        <html>
            <body>
                <p>Hello World.</p>
            </body>
        </html>
        """;
    writeOutput(html);
}
```

Строки `<html>` и `</html>` имеют наименьший отступ (8 пробелов). После удаления 8 incidental пробелов результат:

```
<html>
    <body>
        <p>Hello World.</p>
    </body>
</html>
```

Относительный отступ `<body>` по отношению к `<html>` сохраняется как essential whitespace.

**Влияние позиции закрывающих `"""`**

1. **Закрывающие `"""` на отдельной строке на уровне кода** (стандарт): они сами участвуют в определении минимального отступа. Строка с `"""` считается строкой с отступом равным позиции кавычек.

2. **Закрывающие `"""` на последней строке контента** (без переноса строки):

   ```java
   String name = """
       red
       green
       blue""";
   ```

   Результат: `"red\ngreen\nblue"` — итоговая строка не заканчивается `\n`.

3. **Закрывающие `"""` в первой колонке (позиция 0)**: отключают удаление incidental whitespace — все ведущие пробелы сохраняются:

   ```java
   String html = """
                 <html>
                     <body>
                     </body>
                 </html>
""";
   ```

   Результат сохранит все 17 ведущих пробелов перед `<html>`.

#### Ответ от Claude

**Что такое incidental whitespace**

Когда text block форматируется с отступами в соответствии с кодом Java, часть пробелов оказывается технической необходимостью, а не частью строки. Эти «лишние» пробелы называются **incidental whitespace**. Компилятор автоматически их удаляет при компиляции.

**Алгоритм strip-indent (JEP 378 / Java 15+)**

Компилятор выполняет следующие шаги:

1. Разбивает контент на строки.
2. Определяет **минимальный общий отступ** (common leading whitespace) — наименьшее количество ведущих пробелов среди всех непустых строк контента **и** строки с закрывающими `"""`, если та стоит отдельно.
3. Удаляет этот минимальный отступ с начала каждой строки.
4. Удаляет trailing whitespace с конца каждой строки (тоже считается incidental).
5. Нормализует переносы строк к `\n`.

Этот алгоритм реализован в методе `String.stripIndent()`, доступном программно с Java 15.

**Как позиция `"""` управляет результатом**

| Позиция `"""` | Эффект |
|---|---|
| На отдельной строке, выровнено с кодом | Стандартное поведение: её отступ участвует в определении минимума, итоговая строка заканчивается `\n` |
| На отдельной строке, сдвинуто левее контента | Уменьшает минимальный отступ → в результирующей строке появляются ведущие пробелы |
| В позиции 0 (первая колонка) | Минимальный отступ = 0, весь leading whitespace контента сохраняется |
| На последней строке контента (без переноса) | Убирает завершающий `\n` из строки |

**Детальный пример с разными позициями `"""`**

```java
// Вариант A: """ на уровне кода (8 пробелов)
String a = """
        line1
        line2
        """;
// Результат: "line1\nline2\n"  (8 incidental пробелов удалены)

// Вариант B: """ сдвинуто на 4 пробела влево
String b = """
        line1
        line2
    """;
// Минимум = 4 (позиция """), результат: "    line1\n    line2\n"

// Вариант C: """ в позиции 0
String c = """
        line1
        line2
""";
// Минимум = 0, результат: "        line1\n        line2\n"

// Вариант D: """ на последней строке контента
String d = """
        line1
        line2""";
// Результат: "line1\nline2"  (нет завершающего \n)
```

**Trailing whitespace и escape-последовательности**

Trailing whitespace (пробелы в конце строки) тоже удаляется компилятором автоматически. Если trailing пробелы нужны, используется escape-последовательность `\s` (добавлена в Java 14):

```java
String s = """
    red  \s
    green\s
    """;
// Каждая строка сохраняет один пробел в конце
```

Для подавления неявного `\n` в конце строки используется `\<line-terminator>`:

```java
String noNewline = """
    first \
    second
    """;
// Результат: "first second\n"
```

**Важные нюансы**

- Позиция **открывающих** `"""` на результат не влияет — алгоритм смотрит только на контент и закрывающий делимитер.
- Смешивание табуляции и пробелов при определении отступа даёт непредсказуемые результаты: компилятор предупреждает при флаге `-Xlint:text-blocks`.
- `String.stripIndent()` позволяет применить тот же алгоритм к обычной строке программно.

**Расхождения между источниками:** Oracle Programmer's Guide (SE 18) и документация SE 26 описывают алгоритм идентично. JEP 378 содержит то же описание с акцентом на мотивацию дизайна. Расхождений в техническом описании между источниками не обнаружено.

---

### Вопрос 23. Что такое switch-выражение (switch expression) в Java 14? В чём его отличия от switch-оператора? Что делает ключевое слово yield?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Switch Expressions — docs.oracle.com (Java SE 14)](https://docs.oracle.com/en/java/javase/14/language/switch-expressions.html)

Switch-выражение вычисляет одно значение и может быть использовано непосредственно в выражениях. Оно поддерживает новый синтаксис стрелки (`case L ->`), который устраняет необходимость в `break` и предотвращает падение (fall-through):

```java
System.out.println(
    switch (day) {
        case MONDAY, FRIDAY, SUNDAY -> 6;
        case TUESDAY                -> 7;
        case THURSDAY, SATURDAY     -> 8;
        case WEDNESDAY              -> 9;
        default -> throw new IllegalStateException("Invalid day: " + day);
    }
);
```

Ключевое слово `yield` задаёт значение, которое возвращает switch-выражение, когда требуется блок с несколькими операторами:

```java
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> {
        System.out.println(6);
        yield 6;
    }
    default -> 1;
};
```

Switch-выражение обязано быть **исчерпывающим** (exhaustive): все возможные значения должны быть покрыты, иначе ошибка компиляции. В switch-операторе `default` необязателен.

#### Ответ от Claude

**Switch-выражение** (JEP 361, финализировано в Java 14) — это конструкция, вычисляющая одно значение. В отличие от switch-оператора, его результат можно присвоить переменной или передать в метод.

**Ключевые отличия от switch-оператора:**

| Аспект | Switch-оператор | Switch-выражение |
|---|---|---|
| Результат | Нет (void) | Одно значение |
| Fall-through | Есть (нужен `break`) | Нет (при `case ->`) |
| Исчерпываемость | Необязательна | Обязательна |
| `break` | Завершает ветку | Запрещён внутри выражения |
| `yield` | Не применим | Возвращает значение из блока |

**Синтаксис стрелки (`case L ->`):**
- Одна ветка = одно выражение (или блок с `yield`, или `throw`)
- Нет fall-through по умолчанию
- Несколько констант через запятую: `case MON, FRI, SUN -> 6`

**Ключевое слово `yield`:**
Применяется только в switch-выражениях. Используется внутри блока `{}`, когда нужно выполнить несколько операторов перед возвратом значения:

```java
String result = switch (code) {
    case 1 -> "ONE";
    case 2 -> {
        String s = "TWO";
        System.out.println("Processing: " + s);
        yield s;  // без yield — ошибка компиляции
    }
    default -> "OTHER";
};
```

`yield` — не ключевое слово в полном смысле (это контекстное ключевое слово), поэтому `int yield = 5;` по-прежнему компилируется как локальная переменная.

**Исчерпываемость:** switch-выражение обязано покрывать все возможные значения. Для enum это все константы (или `default`), для `int`/`String` — обязателен `default`. Без этого — ошибка компиляции.

**Расхождения:** JEP 361 и официальная документация Oracle SE 14 согласованы. Важный нюанс из JEP 354 (Second Preview): синтаксис `break <значение>` был заменён на `yield` перед финализацией.

---

### Вопрос 24. Как в Java 21 switch-выражение обрабатывает null? Почему классический switch бросал NullPointerException и как это изменилось с pattern matching?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Pattern Matching with switch — docs.oracle.com (Java SE 24)](https://docs.oracle.com/en/java/javase/24/language/pattern-matching-switch.html)

До Java 21 switch бросал `NullPointerException`, если значение selector-выражения было `null`. Теперь доступна метка `case null`:

```java
static void test(Object obj) {
    switch (obj) {
        case null     -> System.out.println("null!");
        case String s -> System.out.println("String");
        default       -> System.out.println("Something else");
    }
}
```

Метку `null` можно комбинировать **только** с `default`:

```java
static void testStringOrNull(Object obj) {
    switch (obj) {
        case String s      -> System.out.println("String: " + s);
        case null, default -> System.out.println("null или не строка");
    }
}
```

Недопустима комбинация `case null, String s` — это ошибка компиляции. Если `null`-метки нет, а значение равно `null`, switch по-прежнему бросает `NullPointerException`.

#### Ответ от Claude

**Почему классический switch бросал NPE**

В Java до 21 switch работал с примитивными типами и их обёртками, `String` и `enum`. Ни один из этих типов не предусматривал явной обработки `null`: JVM разыменовывала значение при сравнении с константами, что приводило к `NullPointerException`. Это поведение сохраняется в классических switch-операторах без паттернов.

**Что изменилось в Java 21 (JEP 441)**

Pattern-matching switch поддерживает явную метку `case null`:

```java
static String describe(Object obj) {
    return switch (obj) {
        case null      -> "null";
        case Integer i -> "целое: " + i;
        case String s  -> "строка: " + s;
        default        -> "другой тип";
    };
}
```

**Правила для `case null`:**

1. `case null` может стоять в любом месте switch, но по соглашению его помещают первым.
2. Единственная допустимая комбинация с другими метками: `case null, default`.
3. Комбинация `case null, <паттерн>` (например, `case null, String s`) — ошибка компиляции.
4. Если `null`-метки нет и значение `null` — `NullPointerException`, как раньше.

**Связь с `instanceof`:** `instanceof` с паттерном всегда возвращает `false` для `null`, то есть не бросает исключение. Switch с pattern-matching переносит ту же семантику на `case`-метки — `null` не совпадает ни с одним типовым паттерном, если только нет явного `case null`.

**Практическое применение:**

```java
// Обработка REST-запроса, где payload может быть null
String process(Object payload) {
    return switch (payload) {
        case null               -> "400 Bad Request: body missing";
        case String s when s.isBlank() -> "400 Bad Request: empty body";
        case String s           -> handleString(s);
        case Map<?,?> m         -> handleMap(m);
        default                 -> "415 Unsupported Media Type";
    };
}
```

**Расхождения:** документация Oracle SE 24 и JEP 441 согласованы. Baeldung дополнительно подчёркивает, что `null` не совпадает ни с одним паттерном типа, что симметрично поведению `instanceof`.

---

### Вопрос 25. Какие методы добавлены в класс String начиная с Java 11? Что делают strip(), isBlank(), lines(), repeat() и чем strip() отличается от trim()?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [String (Java SE 11 & JDK 11) — docs.oracle.com](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html)

В Java 11 в класс `String` добавлены следующие методы:

- **`strip()`** — удаляет ведущие и завершающие пробельные символы (whitespace) согласно определению Unicode (`Character.isWhitespace(int)`). Возвращает строку без пробельных символов в начале и в конце.
- **`stripLeading()`** — удаляет только ведущие пробельные символы.
- **`stripTrailing()`** — удаляет только завершающие пробельные символы.
- **`isBlank()`** — возвращает `true`, если строка пуста или содержит только пробельные символы.
- **`repeat(int count)`** — возвращает новую строку, являющуюся результатом повторения данной строки `count` раз. Например, `"abc".repeat(3)` возвращает `"abcabcabc"`.
- **`lines()`** — возвращает `Stream<String>` строк, на которые разбивается исходная строка по терминаторам строк.

#### Ответ от Claude

**Новые методы String в Java 11:**

| Метод | Описание |
|---|---|
| `strip()` | Удаляет leading + trailing whitespace (Unicode-aware) |
| `stripLeading()` | Удаляет только leading whitespace |
| `stripTrailing()` | Удаляет только trailing whitespace |
| `isBlank()` | `true`, если строка пуста или состоит только из whitespace |
| `repeat(int)` | Повторяет строку N раз |
| `lines()` | `Stream<String>` строк, разбитых по `\n`, `\r`, `\r\n` |

**Ключевое отличие `strip()` от `trim()`:**

`trim()` (Java 1.0) считает пробелом любой символ с кодом `<= ' '` (пробел ASCII и управляющие символы). `strip()` использует `Character.isWhitespace()`, который охватывает весь Unicode-диапазон пробельных символов:

```java
String s = " Hello ";  // Unicode Em Space
System.out.println(s.trim());    // " Hello " — не удалил
System.out.println(s.strip());   // "Hello" — удалил Unicode-пробел
```

**Примеры использования:**

```java
// isBlank()
"   ".isBlank();   // true
"  a".isBlank();   // false
"".isBlank();      // true

// repeat()
"ha".repeat(3);    // "hahaha"
"".repeat(5);      // ""

// lines()
"a\nb\nc".lines()  // Stream["a", "b", "c"]
    .collect(Collectors.toList());
```

**Дополнительные методы в Java 12–15:**
- Java 12: `indent(int n)` — добавляет/удаляет N пробелов в начале каждой строки.
- Java 15: `formatted(Object... args)` — аналог `String.format()`, вызываемый на экземпляре; `translateEscapes()` — обрабатывает escape-последовательности как в строковом литерале; `stripIndent()` — применяет алгоритм удаления incidental whitespace (тот же, что у text block).

**Расхождения:** документация Oracle SE 11 и SE 17 согласованы. Java 12–15 методы описаны в соответствующих Javadoc.

---

### Вопрос 26. Как работают фабричные методы List.of(), Set.of(), Map.of() в Java 9? Чем они отличаются от Collections.unmodifiableList()? Какие ограничения?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Creating Immutable Lists, Sets, and Maps — docs.oracle.com (Java SE 9)](https://docs.oracle.com/javase/9/core/creating-immutable-lists-sets-and-maps.htm)

Java 9 добавила удобные статические фабричные методы на интерфейсах `List`, `Set` и `Map`. Любая попытка добавить, заменить или удалить элементы бросает `UnsupportedOperationException`. Ключевые характеристики:

- `List.of(e1, e2, ...)` — поддерживает перегруженные формы до 10 элементов плюс varargs.
- `Set.of(e1, e2, ...)` — дублирующиеся элементы вызывают `IllegalArgumentException`.
- `Map.of(k1, v1, k2, v2, ...)` — поддерживает до 10 пар; для большего числа используется `Map.ofEntries(Map.entry(...), ...)`.
- **Null-значения запрещены** — попытка передать `null` бросает `NullPointerException`.
- Реализации пространственно эффективны, потребляют значительно меньше памяти, чем изменяемые аналоги.
- Если коллекция содержит только неизменяемые объекты, она автоматически является потокобезопасной.

#### Ответ от Claude

**List.of(), Set.of(), Map.of() (JEP 269, Java 9)** — фабричные методы для создания по-настоящему неизменяемых (truly immutable) коллекций. Введены для устранения многословности кода Java 8 и ранее.

**Сравнение с `Collections.unmodifiableList()`:**

| Аспект | `Collections.unmodifiableList()` | `List.of()` |
|---|---|---|
| Тип | Обёртка (view) над исходным списком | Независимая структура |
| Изменяемость через оригинал | Да — изменения оригинала видны | Нет — данные не разделяются |
| Null-элементы | Разрешены | Запрещены (`NullPointerException`) |
| Потребление памяти | Выше (обёртка + оригинал) | Ниже (оптимизированная реализация) |
| Порядок итерации | Определён | Для List — да; для Set/Map — нет гарантий |

```java
// unmodifiableList — изменения через оригинал видны!
List<String> mutable = new ArrayList<>(List.of("a", "b"));
List<String> unmod = Collections.unmodifiableList(mutable);
mutable.add("c");
System.out.println(unmod); // [a, b, c] — изменился!

// List.of — настоящая неизменяемость
List<String> immutable = List.of("a", "b");
immutable.add("c");        // UnsupportedOperationException
```

**Ограничения:**

1. `null`-элементы запрещены: `List.of("a", null)` — `NullPointerException`.
2. `Set.of()` с дублями: `Set.of("a", "a")` — `IllegalArgumentException`.
3. `Map.of()` с дублирующимися ключами: `IllegalArgumentException`.
4. `Map.of()` поддерживает максимум 10 пар; больше — `Map.ofEntries(Map.entry(k,v), ...)`.
5. Порядок итерации `Set.of()` и `Map.of()` намеренно **не специфицирован** и может меняться между запусками (для защиты от зависимости от порядка).

**Расхождения:** Oracle Tutorial (Java 9) и Javadoc SE 21 согласованы. Важная деталь: конкретные реализации `List.of()` для 0–2 элементов используют оптимизированные классы (без массива), что подтверждается исходниками OpenJDK.

---

### Вопрос 27. Что такое Stream.ofNullable() в Java 9? Чем он отличается от Stream.of() и как используется совместно с flatMap() для фильтрации null-значений?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java Null-Safe Streams from Collections — Baeldung](https://www.baeldung.com/java-null-safe-streams-from-collections)

Метод `Stream.ofNullable()`, добавленный в Java 9, возвращает последовательный поток с одним элементом, если элемент не равен `null`, или пустой поток, если элемент равен `null`. Это позволяет безопасно работать с потенциально нулевыми значениями без явных проверок.

Типичный сценарий использования — совместно с `flatMap()` для фильтрации `null`-значений внутри потока:

```java
collection.stream()
    .flatMap(s -> Stream.ofNullable(map.get(s)))
    .collect(Collectors.toList());
```

Это более элегантное решение по сравнению с тернарным оператором из Java 8:

```java
// Java 8 — тернарный оператор
collection == null ? Stream.empty() : collection.stream()
```

Метод обеспечивает функциональный подход к обработке `null`-значений внутри потока.

#### Ответ от Claude

**Сигнатура метода (Java 9, JDK 9):**

```java
static <T> Stream<T> ofNullable(T t)
```

Возвращает последовательный поток (`Stream<T>`), содержащий один элемент `t`, если `t != null`, или пустой поток (`Stream.empty()`), если `t == null`.

**Сравнение с `Stream.of()`:**

| Аспект | `Stream.of(T t)` | `Stream.ofNullable(T t)` |
|---|---|---|
| Значение `null` | Бросает `NullPointerException` | Возвращает пустой поток |
| Результат при не-null | Одноэлементный поток | Одноэлементный поток |
| Назначение | Создание потока из известных значений | Безопасная работа с потенциально null |

```java
Stream.of(null);           // NullPointerException
Stream.ofNullable(null);   // Stream.empty() — без исключения
Stream.ofNullable("hello"); // Stream["hello"]
```

**Паттерн с `flatMap()` — фильтрация null при обходе Map:**

Классическая задача: получить значения из `Map` по ключам из коллекции, пропустив ключи, которых в Map нет (значение `null`).

```java
Map<String, String> map = Map.of("a", "Alpha", "b", "Beta");
List<String> keys = List.of("a", "c", "b", "d");

// До Java 9: явная проверка
List<String> result = keys.stream()
    .filter(k -> map.get(k) != null)
    .map(map::get)
    .collect(Collectors.toList());

// Java 9+: Stream.ofNullable + flatMap
List<String> result = keys.stream()
    .flatMap(k -> Stream.ofNullable(map.get(k)))
    .collect(Collectors.toList());
// [Alpha, Beta]
```

**Почему flatMap, а не map?**

`map(k -> Stream.ofNullable(map.get(k)))` даст `Stream<Stream<String>>` — поток потоков. `flatMap()` «разворачивает» каждый вложенный поток, пустые потоки (от null) просто исчезают.

**Полезность при работе с optional-значениями:**

```java
// Преобразование nullable в поток для дальнейшей обработки
String value = possiblyNullSource();

Stream.ofNullable(value)
    .map(String::trim)
    .filter(s -> !s.isEmpty())
    .findFirst()
    .ifPresent(System.out::println);
```

**Расхождения:** Javadoc Oracle SE 21 и Baeldung описывают поведение одинаково. Важный нюанс: `Stream.ofNullable()` введён в Java 9 как часть JEP 269 (Convenience Factory Methods for Collections), хотя непосредственно к фабричным методам коллекций не относится — он добавлен в тот же цикл улучшений Stream API Java 9 вместе с методами `takeWhile()`, `dropWhile()` и `iterate()`.

---

### Вопрос 28. Какие методы добавила Java 9 в Optional: or(), ifPresentOrElse(), stream()? Что добавила Java 11 (isEmpty())?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Guide To Java Optional — Baeldung](https://www.baeldung.com/java-optional)

**Java 9 добавила три метода:**

- **`or(Supplier<? extends Optional<? extends T>>)`** — если Optional пуст, возвращает другой Optional, поставляемый Supplier-ом. В отличие от `orElseGet()`, возвращает `Optional`, а не голое значение.
- **`ifPresentOrElse(Consumer<T>, Runnable)`** — выполняет `Consumer`, если значение присутствует, или `Runnable`, если Optional пуст.
- **`stream()`** — конвертирует Optional в `Stream<T>`: одноэлементный поток, если значение есть, или пустой поток.

**Java 11 добавила:**
- **`isEmpty()`** — инверсия `isPresent()`; возвращает `true`, если Optional не содержит значения.

#### Ответ от Claude

**Optional.or() (Java 9)**

Позволяет «цепочкой» предлагать альтернативные Optional. В отличие от `orElseGet()`, не разворачивает Optional:

```java
Optional<String> found = primarySource.findUser(id)
    .or(() -> secondarySource.findUser(id))
    .or(() -> cacheService.findUser(id));
// Возвращает первый непустой Optional из цепочки
```

Ключевое: лямбды вычисляются **лениво** — следующий источник запрашивается только если предыдущий вернул пустой Optional.

**Optional.ifPresentOrElse() (Java 9)**

Заменяет паттерн `if/else` вокруг `isPresent()`:

```java
// До Java 9
if (opt.isPresent()) {
    process(opt.get());
} else {
    handleAbsent();
}

// Java 9+
opt.ifPresentOrElse(
    value -> process(value),
    () -> handleAbsent()
);
```

**Optional.stream() (Java 9)**

Интеграция с Stream API. Удобен при фильтрации потока Optional-ов:

```java
// Flatmap потока Optional в поток реальных значений (только присутствующих)
List<String> results = ids.stream()
    .map(id -> repository.findById(id))   // Stream<Optional<User>>
    .flatMap(Optional::stream)             // Stream<User> — только непустые
    .map(User::getName)
    .collect(Collectors.toList());
```

До Java 9 нужен был `filter(Optional::isPresent).map(Optional::get)`.

**Optional.isEmpty() (Java 11)**

Семантически чище, чем `!isPresent()`:

```java
Optional<String> opt = Optional.empty();
opt.isEmpty();   // true — читается естественно
!opt.isPresent(); // то же самое, но менее читаемо
```

Часто удобен в `assert` или в потоковых условиях: `stream.filter(Optional::isEmpty)`.

**Расхождения:** Baeldung и официальный Javadoc SE 21 описывают эти методы одинаково. Нюанс: `or()` возвращает `Optional<T>`, а не `T` — это принципиальное отличие от `orElseGet()`, где нет вложения Optional.

---

### Вопрос 29. Как создать виртуальный поток в Java 21? Чем Thread.ofVirtual() отличается от Executors.newVirtualThreadPerTaskExecutor()? Почему виртуальные потоки не следует помещать в пул?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Virtual Threads — docs.oracle.com (Java SE 21)](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)

Для создания виртуальных потоков доступны два основных API:

**Thread.ofVirtual() — Thread.Builder:**
```java
Thread thread = Thread.ofVirtual().start(() -> System.out.println("Hello"));
thread.join();
```

**Executors.newVirtualThreadPerTaskExecutor():**
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    Future<?> future = executor.submit(() -> System.out.println("Running"));
    future.get();
}
```

Проверить, является ли поток виртуальным: `Thread.currentThread().isVirtual()`.

#### Ответ от Claude

**Два основных способа создания виртуальных потоков:**

**1. `Thread.ofVirtual()` — прямое создание:**

```java
// Запустить и ждать
Thread t = Thread.ofVirtual().start(() -> doWork());
t.join();

// С именем
Thread t2 = Thread.ofVirtual().name("worker-", 0).start(task);

// Через Thread.Builder (переиспользование настроек)
Thread.Builder builder = Thread.ofVirtual().name("task-", 0);
Thread t3 = builder.start(task1);
Thread t4 = builder.start(task2);  // "task-1"
```

**2. `Executors.newVirtualThreadPerTaskExecutor()` — через ExecutorService:**

```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    var f1 = executor.submit(() -> fetchFromDB());
    var f2 = executor.submit(() -> callExternalAPI());
    // Оба запроса выполняются параллельно
    return combine(f1.get(), f2.get());
}
```

**Различия:**

| Аспект | `Thread.ofVirtual()` | `newVirtualThreadPerTaskExecutor()` |
|---|---|---|
| Абстракция | Низкоуровневая | Высокоуровневая (ExecutorService) |
| Управление | Ручное (`join()`) | Автоматическое через `Future` |
| Интеграция | Любой код | `ExecutorService`-совместимый код |
| Применение | Ad hoc задачи | Массовый параллелизм, fanout |

**Почему виртуальные потоки нельзя помещать в пул:**

Смысл пула платформенных потоков — дорогостоящее создание и разрушение OS-потоков амортизируется повторным использованием. Виртуальный поток создаётся почти бесплатно (не OS-ресурс), поэтому:

1. Пул виртуальных потоков не даёт выигрыша в производительности.
2. Повторное использование виртуального потока может перенести `ThreadLocal`-значения между не связанными задачами — нарушение изоляции.
3. Семантика виртуального потока: «один поток — одна задача». Именно поэтому `newVirtualThreadPerTaskExecutor()` создаёт **новый поток на каждую задачу**, а не переиспользует.

**Расхождения:** JEP 444 и документация Oracle SE 21 согласованы. Baeldung добавляет рекомендацию использовать `Semaphore` вместо ограниченного пула для ограничения параллелизма (например, числа одновременных соединений с БД).

---

### Вопрос 30. Что такое Stream.toList() в Java 16? Чем он отличается от collect(Collectors.toList())? Допускает ли Stream.toList() null-элементы?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Collecting Stream Elements into a List in Java — Baeldung](https://www.baeldung.com/java-stream-to-list-collecting)

`Stream.toList()` — это новый терминальный метод, добавленный в Java 16. Он возвращает **неизменяемый** список (`List` без поддержки мутаций). В отличие от него, `Collectors.toList()` (Java 8) возвращает **изменяемый** `ArrayList`.

Ключевые различия:

- `Stream.toList()` создаёт неизменяемый список — попытка добавить элемент бросает `UnsupportedOperationException`.
- `Collectors.toList()` возвращает изменяемый список, допускающий `add()`, `remove()` и т.д.
- **Null-элементы:** `Stream.toList()` **допускает** null-элементы (в отличие от `Collectors.toUnmodifiableList()`, который запрещает null); `Collectors.toList()` также допускает null.

#### Ответ от Claude

**Stream.toList() (Java 16)** — упрощённый способ завершить поток списком, не требующий вызова `collect()`:

```java
// До Java 16
List<String> list1 = stream.collect(Collectors.toList());

// Java 16+
List<String> list2 = stream.toList();
```

**Сравнительная таблица:**

| Аспект | `stream.toList()` | `collect(Collectors.toList())` | `collect(Collectors.toUnmodifiableList())` |
|---|---|---|---|
| Java-версия | 16+ | 8+ | 10+ |
| Изменяемость | Неизменяемый | Изменяемый (`ArrayList`) | Неизменяемый |
| Null-элементы | Допускает | Допускает | Запрещает (`NPE`) |
| Краткость | Максимальная | Многословная | Многословная |

**Поведение с null:**

```java
// Stream.toList() — null разрешён
List<String> list = Stream.of("a", null, "b").toList();
// [a, null, b] — OK

// Collectors.toUnmodifiableList() — null запрещён
List<String> list2 = Stream.of("a", null, "b")
    .collect(Collectors.toUnmodifiableList());
// NullPointerException!
```

**Когда использовать:**

- `stream.toList()` — предпочтителен в Java 16+ коде, когда нужен список только для чтения.
- `collect(Collectors.toList())` — когда нужен изменяемый список или совместимость с Java 8–15.
- `collect(Collectors.toUnmodifiableList())` — когда нужна неизменяемость **и** гарантия отсутствия null.

**Расхождения:** Baeldung и Javadoc SE 21 согласованы. Важный нюанс: спецификация `Stream.toList()` гарантирует только `List`-контракт, не `ArrayList` — реализация может меняться между версиями JDK.

---

### Вопрос 31. Что такое локальные записи (local records) в Java 16? Для чего они применяются и почему локальный record неявно статический?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Record Classes — docs.oracle.com (Java SE 22)](https://docs.oracle.com/en/java/javase/22/language/records.html)

**Локальный record** — это record-класс, объявленный внутри тела метода. Локальные record-классы **неявно статические**: их методы не могут обращаться к переменным объемлющего метода. Это отличает их от локальных классов, которые не являются статическими и могут захватывать переменные метода.

```java
List<Merchant> findTopMerchants(List<Sale> sales, List<Merchant> merchants, int year, Month month) {
    // Локальный record — вспомогательная структура данных для метода
    record MerchantSales(Merchant merchant, double sales) {}

    return merchants.stream()
        .map(merchant -> new MerchantSales(merchant, computeSales(sales, merchant, year, month)))
        .sorted((m1, m2) -> Double.compare(m2.sales(), m1.sales()))
        .map(MerchantSales::merchant)
        .collect(Collectors.toList());
}
```

#### Ответ от Claude

**Что такое локальный record**

Локальный record — это record-класс, объявленный в теле метода, конструктора или блока инициализатора. Подобно локальным классам, он виден только внутри содержащего блока. Введён в Java 16 вместе с финализацией record-классов.

**Для чего применяется**

Основное применение — агрегирование промежуточных данных в потоковых вычислениях без загрязнения пространства имён класса:

```java
double findMaxRatio(List<Product> products) {
    // Локальный record для промежуточного агрегата
    record ProductRatio(Product product, double ratio) {}

    return products.stream()
        .map(p -> new ProductRatio(p, (double) p.profit() / p.cost()))
        .max(Comparator.comparingDouble(ProductRatio::ratio))
        .map(pr -> pr.ratio())
        .orElse(0.0);
}
```

Без локального record пришлось бы либо создавать вспомогательный класс на уровне файла, либо использовать `Map.Entry`, либо делать двойной проход по потоку.

**Почему локальный record неявно статический**

Обычные локальные классы могут захватывать переменные и поля объемлющего контекста, потому что они нестатические (хранят ссылку на внешний экземпляр). Record же спроектирован как прозрачный носитель данных — его состояние полностью определяется компонентами. Захват произвольных переменных из объемлющего метода нарушил бы эту семантику. Поэтому локальный record:

- неявно статический — не хранит ссылку на объемлющий экземпляр;
- не может обращаться к нестатическим членам объемлющего класса через `this`;
- но может обращаться к `static`-членам объемлющего класса напрямую.

**Практические выводы:**
- Локальный record идеален для временных агрегатов в методах с потоковой обработкой.
- Он получает все автоматически генерируемые методы: `equals`, `hashCode`, `toString`, аксессоры.
- Создание локального record — более читаемая альтернатива `Object[]` или `Map.Entry` для хранения нескольких значений.

**Расхождения:** Документация Oracle SE 22 и JLS согласованы. Baeldung добавляет, что с введением record-паттернов (Java 21) локальные records стали ещё удобнее — их можно деконструировать прямо в `switch`.

---

### Вопрос 32. Что такое unnamed variables и unnamed patterns (JEP 456, Java 22)? Как использовать символ _ и где он допустим?

**Категория:** Современная Java · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [JEP 456: Unnamed Variables & Patterns — openjdk.org](https://openjdk.org/jeps/456)

**Unnamed variable** (`_`) — объявление переменной без имени. Декларация неименованной переменной не помещает имя в область видимости, поэтому переменную нельзя прочитать или записать после инициализации.

Обе конструкции обозначаются символом `_`. Основные места использования:
- Локальные переменные, параметры лямбд, catch-параметры, переменные try-with-resources, переменные цикла `for` и расширенного `for`.
- Вложенные паттерны в record-паттернах и switch.

В Java 8 `_` был предупреждением; в Java 9 — ошибкой компиляции как одиночный идентификатор. JEP 456 переосмыслил его как особую конструкцию.

#### Ответ от Claude

**Мотивация**

До Java 22 при использовании переменной паттерна или catch-параметра, если значение не нужно, приходилось придумывать имя: `e`, `ignored`, `unused`. Это загрязняло код и вводило в заблуждение. JEP 456 (Java 22) вводит `_` как явный сигнал «это значение намеренно не используется».

**Unnamed variable — примеры:**

```java
// 1. Catch-параметр — исключение не нужно
try {
    int n = Integer.parseInt(s);
} catch (NumberFormatException _) {
    return -1;  // _ не используем
}

// 2. Лямбда-параметр — второй аргумент не нужен
map.forEach((k, _) -> System.out.println(k));

// 3. Enhanced for — только счётчик итераций
int count = 0;
for (var _ : list) count++;

// 4. Try-with-resources — ресурс не нужен напрямую
try (var _ = ScopedValue.where(KEY, value).open()) {
    // работаем в контексте, сам ресурс не нужен
}
```

**Unnamed pattern — примеры:**

```java
// 5. В record-паттерне — компонент не нужен
if (point instanceof Point(int x, _)) {  // y игнорируется
    System.out.println(x);
}

// 6. В switch — компоненты не нужны
static String describe(Object obj) {
    return switch (obj) {
        case Point(_, _)    -> "точка";   // компоненты не важны
        case Circle(_, _)   -> "круг";
        default             -> "другой объект";
    };
}
```

**Правила:**

1. Несколько `_` в одной области видимости допустимы — каждое объявление независимо.
2. `_` нельзя ни читать, ни присваивать ему значения после объявления.
3. `_` как часть идентификатора (например, `_age`) по-прежнему допустим.
4. Только одиночный `_` без других символов становится unnamed-конструкцией.

**Расхождения:** JEP 456 и JEP 443 (preview) описывают поведение одинаково. Единственное расхождение — в Java 21 `_` в паттернах был preview; в Java 22 стал стабильным (JEP 456).

---

### Вопрос 33. Что такое SequencedCollection, SequencedSet и SequencedMap в Java 21 (JEP 431)? Какие методы они вводят и зачем понадобились эти интерфейсы?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [JEP 431: Sequenced Collections — openjdk.org](https://openjdk.org/jeps/431)

Новые интерфейсы определяют **порядок встречи** (encounter order) элементов с операциями обращения к первому и последнему элементам, а также получением обратного (reversed) представления. До Java 21 не существовало единого способа получить последний элемент из `List`, `SortedSet` или `Deque` — у каждой коллекции был свой несвязанный API.

Интерфейсы, введённые JEP 431:
- **`SequencedCollection<E>`** добавляет: `addFirst(E)`, `addLast(E)`, `getFirst()`, `getLast()`, `removeFirst()`, `removeLast()`, `reversed()`.
- **`SequencedSet<E> extends SequencedCollection<E>, Set<E>`** — то же для множеств с упорядочением.
- **`SequencedMap<K,V>`** добавляет: `putFirst(K,V)`, `putLast(K,V)`, `firstEntry()`, `lastEntry()`, `pollFirstEntry()`, `pollLastEntry()`, `reversed()`, `sequencedKeySet()`, `sequencedValues()`, `sequencedEntrySet()`.

#### Ответ от Claude

**Проблема, которую решает JEP 431**

До Java 21 получение первого и последнего элемента выглядело по-разному для каждого типа коллекции:

```java
// Получить последний элемент — у каждой коллекции по-своему
list.get(list.size() - 1);            // List
sortedSet.last();                     // SortedSet
deque.peekLast();                     // Deque
linkedHashMap.entrySet().iterator()... // LinkedHashMap — боль
```

Не было единого полиморфного API. `SequencedCollection` унифицировал это.

**Иерархия новых интерфейсов:**

```
SequencedCollection
    ├── List
    ├── Deque
    └── SequencedSet
            ├── SortedSet
            └── LinkedHashSet

SequencedMap
    ├── SortedMap
    └── LinkedHashMap
```

**Ключевые методы `SequencedCollection`:**

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
list.getFirst();     // "a"
list.getLast();      // "c"
list.removeFirst();  // удаляет "a", возвращает его
list.addFirst("z");  // добавляет "z" в начало

List<String> rev = list.reversed(); // ["c", "b", "a"] — view
```

**`reversed()` — обратное представление:**

`reversed()` возвращает **view** (не копию) коллекции с обратным порядком итерации. Изменения в оригинале видны через reversed view и наоборот:

```java
LinkedHashSet<String> set = new LinkedHashSet<>(Set.of("a", "b", "c"));
// Порядок в LinkedHashSet определён порядком вставки
set.reversed().forEach(System.out::println); // итерация в обратном порядке
```

**Зачем понадобились:**
- Унифицированный API для работы с упорядоченными коллекциями.
- Возможность писать полиморфный код, принимающий `SequencedCollection` вместо конкретного типа.
- Устранение «неловких» обходных путей вроде `list.get(list.size()-1)`.

**Расхождения:** Документация JEP 431 и Javadoc SE 21 согласованы. `reversed()` для `ArrayList` и `LinkedList` реализован по-разному, но контракт одинаков.

---

### Вопрос 34. Как record может реализовывать интерфейс? Можно ли использовать record как реализацию sealed interface? Приведите пример.

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java Record Keyword — Baeldung](https://www.baeldung.com/java-record-keyword)

Record-класс может реализовывать интерфейсы точно так же, как обычный класс:

```java
public sealed interface Vehicle permits Car, Truck {
    String getRegistrationNumber();
}

public record Car(int numberOfSeats, String registrationNumber) implements Vehicle {
    @Override
    public String getRegistrationNumber() {
        return registrationNumber;
    }
}
```

Record может реализовать метод интерфейса через аксессор компонента (если имена совпадают):

```java
public interface WithXCoordinate {
    int x();
}

public record Point(int x, int y) implements WithXCoordinate {}
// Компилятор принимает: метод x() уже генерируется как аксессор компонента x
```

#### Ответ от Claude

**Реализация интерфейсов в record**

Record может реализовывать любое количество интерфейсов. Ограничения:
- Record **не может расширять** (extends) другой класс, кроме `java.lang.Record`.
- Record **не может быть расширен** (неявно final), но может быть разрешённым подтипом в sealed-иерархии.

**Пример — record как листовой тип sealed-иерархии:**

```java
sealed interface Shape permits Circle, Rectangle, Triangle {}

record Circle(double radius) implements Shape {}
record Rectangle(double width, double height) implements Shape {}
record Triangle(double a, double b, double c) implements Shape {}

// Исчерпывающий switch — default не нужен
static double area(Shape shape) {
    return switch (shape) {
        case Circle(var r)          -> Math.PI * r * r;
        case Rectangle(var w, var h) -> w * h;
        case Triangle(var a, var b, var c) -> {
            double s = (a + b + c) / 2;
            yield Math.sqrt(s * (s-a) * (s-b) * (s-c));
        }
    };
}
```

**Совмещение аксессора компонента с методом интерфейса:**

Если имя метода интерфейса совпадает с именем компонента, аксессор удовлетворяет требованию интерфейса автоматически:

```java
interface Identifiable {
    String id();
}

record User(String id, String name) implements Identifiable {
    // Метод id() генерируется автоматически как аксессор компонента
    // и одновременно реализует Identifiable.id() — явный override не нужен
}
```

**Переопределение методов Object:**

Сгенерированные `equals`, `hashCode`, `toString` можно переопределить явно. Это допустимо и для методов интерфейса:

```java
interface Printable {
    String print();
}

record Product(String name, double price) implements Printable {
    @Override
    public String print() {  // явная реализация
        return String.format("%s — %.2f руб.", name, price);
    }
}
```

**Расхождения:** Документация Oracle SE 22 и Baeldung согласованы. Важный нюанс: record, реализующий `Serializable`, автоматически является сериализуемым — дополнительного кода не нужно, если все компоненты сериализуемы.

---

### Вопрос 35. Что такое «exhaustive switch» (исчерпывающий switch) и когда он обязателен? Что произойдёт, если switch-выражение не исчерпывающее?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Switch Expressions — docs.oracle.com (Java SE 14)](https://docs.oracle.com/en/java/javase/14/language/switch-expressions.html)

Switch-выражение обязано быть **исчерпывающим**: все возможные значения selector-выражения должны иметь соответствующую ветку. Если это требование не выполнено — **ошибка компиляции**.

Для `enum`-типа switch-выражение, покрывающее все константы enum без `default`, считается корректным. Компилятор вставляет синтетический `default`, который выбрасывает исключение при добавлении новой константы enum без перекомпиляции switch.

```java
// Ошибка компиляции — не все дни недели покрыты:
int i = switch (day) {
    case MONDAY -> 1;
    // TUESDAY, WEDNESDAY и т.д. не покрыты
};
```

#### Ответ от Claude

**Когда exhaustiveness обязателен:**

1. **Всегда для switch-выражений.** Поскольку switch-выражение обязано вернуть значение, компилятор должен убедиться, что для каждого возможного входного значения существует ветка.

2. **Для switch-операторов с pattern matching** (Java 21+). Стандартный switch-оператор без паттернов не требует исчерпываемости.

**Правила исчерпываемости:**

```java
// 1. С `default` — всегда exhaustive
int x = switch (value) {
    case 1  -> 10;
    case 2  -> 20;
    default -> 0;  // покрывает всё остальное
};

// 2. Enum без default — exhaustive, если все константы покрыты
Day day = Day.MONDAY;
String s = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY -> "начало";
    case THURSDAY, FRIDAY           -> "конец";
    case SATURDAY, SUNDAY           -> "выходной";
    // default не нужен — все 7 констант перечислены
};

// 3. Sealed-тип — exhaustive, если все permitted-подтипы покрыты
sealed interface Expr permits Num, Add {}
record Num(int v) implements Expr {}
record Add(Expr l, Expr r) implements Expr {}

int eval(Expr e) {
    return switch (e) {
        case Num(var v)       -> v;
        case Add(var l, var r) -> eval(l) + eval(r);
        // default не нужен — Expr имеет только Num и Add
    };
}
```

**Что происходит при нарушении:**

- Отсутствие exhaustiveness в switch-**выражении** → **ошибка компиляции**.
- При отдельной компиляции (sealed-иерархия расширена без перекомпиляции switch) → компилятор вставляет синтетический `default`, бросающий **`MatchException`** в runtime.

**Практическое значение:** требование exhaustiveness — это статическая гарантия того, что при добавлении нового подтипа sealed-класса разработчик получит ошибку компиляции, а не молчаливое неверное поведение. Это одно из главных преимуществ sealed-классов над обычными иерархиями.

**Расхождения:** JEP 361 (switch expressions) и JEP 441 (pattern matching for switch) согласованы в требованиях к exhaustiveness. Класс исключения изменился: до Java 21 синтетический default бросал `IncompatibleClassChangeError`, с Java 21 — `MatchException`.

---

### Вопрос 36. Как работает Optional.flatMap() в сравнении с Optional.map()? В каких ситуациях flatMap необходим?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Guide To Java Optional — Baeldung](https://www.baeldung.com/java-optional)

В отличие от обычного `map()`, метод `Optional.flatMap()` принимает функцию, возвращающую `Optional`, и возвращает результат как есть, без дополнительного оборачивания. Это позволяет избежать вложенных `Optional<Optional<T>>`:

```java
Optional<String> opt = Optional.of("value");
Optional<Optional<String>> wrong = opt.map(s -> Optional.of(s.toUpperCase()));
// Результат: Optional[Optional[VALUE]] — вложение!

Optional<String> correct = opt.flatMap(s -> Optional.of(s.toUpperCase()));
// Результат: Optional[VALUE] — без вложения
```

`flatMap()` применяет функцию только если Optional содержит значение; если Optional пуст — возвращает пустой Optional.

#### Ответ от Claude

**Сравнение map() и flatMap():**

| Аспект | `map(Function<T, R>)` | `flatMap(Function<T, Optional<R>>)` |
|---|---|---|
| Функция возвращает | `R` (любое значение) | `Optional<R>` |
| Результат метода | `Optional<R>` | `Optional<R>` (без двойного оборачивания) |
| При пустом Optional | Возвращает `Optional.empty()` | Возвращает `Optional.empty()` |
| Применение | Трансформация значения | Цепочка методов, возвращающих Optional |

**Когда flatMap необходим:**

Ситуация 1 — цепочка методов, каждый из которых возвращает Optional:

```java
class Address {
    Optional<String> getCity() { ... }
}
class User {
    Optional<Address> getAddress() { ... }
}

// С map() — получаем Optional<Optional<String>>
Optional<Optional<String>> wrong = user.getAddress()
    .map(a -> a.getCity());

// С flatMap() — получаем Optional<String>
Optional<String> city = user.getAddress()
    .flatMap(a -> a.getCity());
```

Ситуация 2 — парсинг с возможной ошибкой:

```java
Optional<Integer> parseId(String s) {
    try { return Optional.of(Integer.parseInt(s)); }
    catch (NumberFormatException e) { return Optional.empty(); }
}

Optional<Integer> id = Optional.of("42").flatMap(s -> parseId(s));
// Optional[42]

Optional<Integer> id2 = Optional.of("abc").flatMap(s -> parseId(s));
// Optional.empty
```

**Правило выбора:**
- `map()` — когда функция возвращает обычное значение (не Optional).
- `flatMap()` — когда функция возвращает Optional (иначе получается `Optional<Optional<T>>`).

**Расхождения:** Baeldung и официальный Javadoc SE 21 согласованы. Нюанс: `flatMap()` не допускает `null` в качестве возвращаемого значения функции (бросает `NullPointerException`), в отличие от `map()`, где null превращается в `Optional.empty()`.

---

### Вопрос 37. Какие escape-последовательности специфичны для text blocks в Java (\\s и \\ в конце строки)? Для чего они нужны?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [JEP 378: Text Blocks — openjdk.org](https://openjdk.org/jeps/378)

Компилятор text blocks при обработке контента выполняет три шага: нормализацию переносов строк, удаление incidental whitespace, интерпретацию escape-последовательностей. Два новых escape-символа, специфичных для text blocks:

- **`\s`** — явный пробел (U+0020). Так как trailing whitespace автоматически удаляется при обработке text block, `\s` позволяет сохранить пробел в конце строки или предотвратить удаление пробелов левее него. Переводится в один символ пробела.
- **`\<line-terminator>`** (обратный слеш в конце строки) — подавляет неявный перенос строки, объединяя текущую строку со следующей. Позволяет разбить длинную строку на несколько физических строк без добавления `\n` в результат.

#### Ответ от Claude

**Контекст:** при компиляции text block выполняется автоматическое удаление trailing whitespace (пробелов в конце строк) и leading whitespace (incidental). Это полезно в большинстве случаев, но иногда пробелы в конце строки являются частью нужного контента. Для этого введены специальные escape-последовательности.

**`\s` — явный пробел:**

```java
// БЕЗ \s: trailing пробелы после "red", "green", "blue" удалены
String colors = """
    red
    green
    blue
    """;
// "red\ngreen\nblue\n"

// С \s: каждая строка сохраняет один пробел в конце
String colors = """
    red  \s
    green\s
    blue \s
    """;
// "red   \ngreen \nblue  \n" (пробелы сохранены, \s → ' ')
```

`\s` работает как «забор»: всё пространство **левее** `\s` тоже не удаляется.

**`\` в конце строки — подавление переноса строки:**

```java
// Без \: длинная строка — перенос строки в результате
String text = """
    Lorem ipsum dolor sit amet, \
    consectetur adipiscing elit.
    """;
// "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
// Строки объединены, \n между ними не добавлен
```

Это особенно полезно для длинных JSON-строк или SQL-запросов, которые хочется форматировать вертикально в исходном коде, но без реальных переносов в результате:

```java
String sql = """
    SELECT u.id, u.name, u.email \
    FROM users u \
    WHERE u.active = true \
    ORDER BY u.name
    """;
// Одна строка без внутренних \n
```

**Порядок обработки:**
1. Нормализация переносов строк → `\n`
2. Удаление incidental whitespace (strip-indent)
3. Интерпретация escape-последовательностей (в т.ч. `\s` и `\`)

`\s` и `\<line-terminator>` обрабатываются на шаге 3 — после удаления whitespace. Поэтому `\s` служит защитой от шага 2, а не от шага 3.

**Расхождения:** JEP 378 и Programmer's Guide (Oracle SE 18) согласованы. Важная деталь: `\s` разрешён и в обычных строковых литералах начиная с Java 15, а не только в text blocks.

---

### Вопрос 38. Что такое Collectors.toUnmodifiableList/Set/Map() (Java 10)? Чем они отличаются от List.copyOf() и как работают совместно с Stream API?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Collectors (Java SE 10 & JDK 10) — docs.oracle.com](https://docs.oracle.com/javase/10/docs/api/java/util/stream/Collectors.html)

В Java 10 добавлены три новых коллектора для создания неизменяемых коллекций из потоков:

- **`Collectors.toUnmodifiableList()`** — возвращает `Collector`, накапливающий элементы в неизменяемый `List` в порядке встречи.
- **`Collectors.toUnmodifiableSet()`** — возвращает `Collector`, накапливающий элементы в неизменяемый `Set`. Не гарантирует порядок.
- **`Collectors.toUnmodifiableMap(keyMapper, valueMapper)`** — возвращает `Collector`, накапливающий элементы в неизменяемый `Map`. Дублирующиеся ключи бросают `IllegalStateException`.

Ни один из этих коллекторов не допускает **null**-элементы: попытка включить `null` бросает `NullPointerException`.

#### Ответ от Claude

**Collectors.toUnmodifiableList/Set/Map() — назначение**

До Java 10 для получения неизменяемого результата из потока приходилось оборачивать:

```java
// До Java 10 — многословно
List<String> list = Collections.unmodifiableList(
    stream.collect(Collectors.toList())
);

// Java 10+ — лаконично
List<String> list = stream.collect(Collectors.toUnmodifiableList());
```

**Сравнение с `List.copyOf()` (тоже Java 10):**

| Аспект | `Collectors.toUnmodifiableList()` | `List.copyOf(collection)` |
|---|---|---|
| Работает с | `Stream<T>` | Существующей `Collection<T>` |
| Применение | Терминальная операция потока | Создание копии уже готовой коллекции |
| Null | Запрещены (`NPE`) | Запрещены (`NPE`) |
| Результат | Неизменяемый `List` | Неизменяемый `List` |

```java
// Stream → неизменяемый List через коллектор
List<Integer> squares = IntStream.range(1, 6)
    .map(i -> i * i)
    .boxed()
    .collect(Collectors.toUnmodifiableList());
// [1, 4, 9, 16, 25] — неизменяемый

// Существующая коллекция → неизменяемая копия
List<String> original = new ArrayList<>(List.of("a", "b"));
List<String> copy = List.copyOf(original);
original.add("c");
// copy по-прежнему ["a", "b"] — независимая копия
```

**Ключевое отличие от `Collectors.toList()` (Java 8):**

```java
// toList() — изменяемый ArrayList
List<String> mutable = stream.collect(Collectors.toList());
mutable.add("new");  // OK

// toUnmodifiableList() — неизменяемый
List<String> immutable = stream.collect(Collectors.toUnmodifiableList());
immutable.add("new");  // UnsupportedOperationException
```

**Null-обработка:**

```java
Stream.of("a", null, "b").collect(Collectors.toList());             // OK — [a, null, b]
Stream.of("a", null, "b").collect(Collectors.toUnmodifiableList()); // NPE
Stream.of("a", "b").toList();                                       // OK — null разрешён в Stream.toList()
```

**Рекомендация:** в Java 16+ `stream.toList()` заменяет `collect(Collectors.toUnmodifiableList())` для большинства случаев — короче и читаемее, при этом оба возвращают неизменяемый список.

**Расхождения:** Javadoc Java 10 и SE 21 согласованы. Детали реализации различаются (`toUnmodifiableList()` делегирует в `List.of()` через `Collections.unmodifiableList()` в OpenJDK), но публичный контракт стабилен.

---

### Вопрос 39. Что такое HttpClient в Java 11 (пакет java.net.http)? Как создать клиент, отправить синхронный и асинхронный запрос? Чем он лучше HttpURLConnection?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [java.net.http (Java SE 11) — docs.oracle.com](https://docs.oracle.com/en/java/javase/11/docs/api/java.net.http/java/net/http/package-summary.html)

Пакет `java.net.http` предоставляет HTTP-клиент и WebSocket API. Основные классы:

- **`HttpClient`** — неизменяемый клиент, отправляющий запросы и получающий ответы. Настраивается через `HttpClient.Builder` и может использоваться повторно для множества запросов.
- **`HttpRequest`** — HTTP-запрос, создаётся через `HttpRequest.Builder`. Поддерживает различные тела запроса через `HttpRequest.BodyPublishers`.
- **`HttpResponse`** — HTTP-ответ, предоставляет доступ к статус-коду, заголовкам и телу. Обработка тела настраивается через `HttpResponse.BodyHandler` и `HttpResponse.BodySubscribers`.

Клиент поддерживает HTTP/1.1 и HTTP/2, использует `CompletableFuture` для асинхронных операций, а также обеспечивает синхронный (`send`) и асинхронный (`sendAsync`) режимы отправки запросов.

#### Ответ от Claude

**Создание HttpClient:**

```java
// Быстрое создание с настройками по умолчанию
HttpClient client = HttpClient.newHttpClient();

// Полная конфигурация через Builder
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)          // предпочтительная версия протокола
    .followRedirects(HttpClient.Redirect.NORMAL) // автоматическое следование редиректам
    .connectTimeout(Duration.ofSeconds(10))
    .build();
```

**Построение запроса (`HttpRequest`):**

```java
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Accept", "application/json")
    .timeout(Duration.ofSeconds(30))
    .GET()
    .build();

// POST с телом
HttpRequest postRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("{\"name\":\"Alice\"}"))
    .build();
```

**Синхронная отправка (`send`)** — блокирует поток до получения ответа:

```java
HttpResponse<String> response =
    client.send(request, HttpResponse.BodyHandlers.ofString());

System.out.println(response.statusCode()); // 200
System.out.println(response.body());       // тело ответа
```

**Асинхронная отправка (`sendAsync`)** — возвращает `CompletableFuture` немедленно:

```java
client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
    .thenApply(HttpResponse::body)
    .thenAccept(System.out::println)
    .join(); // ждать завершения (если нужно)
```

**Параллельные запросы через `sendAsync`:**

```java
CompletableFuture<HttpResponse<String>> f1 =
    client.sendAsync(req1, HttpResponse.BodyHandlers.ofString());
CompletableFuture<HttpResponse<String>> f2 =
    client.sendAsync(req2, HttpResponse.BodyHandlers.ofString());

CompletableFuture.allOf(f1, f2).join();
System.out.println(f1.get().body());
System.out.println(f2.get().body());
```

**Преимущества над `HttpURLConnection`:**

| Аспект | `HttpURLConnection` | `HttpClient` (Java 11) |
|---|---|---|
| HTTP/2 | Нет | Да (нативная поддержка) |
| Асинхронность | Нет | Да (`CompletableFuture`) |
| API стиль | Громоздкий, mutable | Fluent Builder, immutable |
| WebSocket | Нет | Да |
| Настройка | Сложная, многошаговая | Через Builder, лаконично |
| Сторонние зависимости | Нет | Нет (встроен в JDK) |

**`BodyHandlers` — типовые обработчики тела ответа:**

```java
HttpResponse.BodyHandlers.ofString()          // String
HttpResponse.BodyHandlers.ofByteArray()       // byte[]
HttpResponse.BodyHandlers.ofFile(path)        // сохранить в файл
HttpResponse.BodyHandlers.discarding()        // игнорировать тело
```

**Расхождения:** Javadoc Oracle SE 11 и SE 21 согласованы в описании API. Baeldung отмечает, что HTTP/2 включается по умолчанию как предпочтительная версия, но клиент автоматически деградирует до HTTP/1.1, если сервер не поддерживает HTTP/2.

---

### Вопрос 40. Что такое Helpful NullPointerExceptions (JEP 358, Java 14)? Какую информацию добавляет JVM в сообщение NPE и как это поведение включается?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Helpful NullPointerExceptions in Java — Baeldung](https://www.baeldung.com/java-14-nullpointerexception)

До Java 14 `NullPointerException` содержал только стек вызовов без указания, какая именно переменная равна `null`:

```
Exception in thread "main" java.lang.NullPointerException
  at com.example.Main.main(Main.java:10)
```

С Java 14 (JEP 358) JVM анализирует байткод и добавляет в сообщение точное описание причины:

```
Exception in thread "main" java.lang.NullPointerException:
  Cannot invoke "String.toLowerCase()" because the return value of
  "PersonalDetails.getEmailAddress()" is null
  at com.example.Main.main(Main.java:10)
```

Для строки `employee.getPersonalDetails().getEmailAddress().toLowerCase()` JVM точно укажет, какое именно звено в цепочке вернуло `null`. Детальное сообщение вычисляется **лениво** — только при печати исключения, а не в момент его создания. Улучшенные сообщения генерирует только JVM; NPE, явно созданные через `throw new NullPointerException()` в коде, остаются без детального описания.

#### Ответ от Claude

**Суть JEP 358**

До Java 14 отладка `NullPointerException` в цепочке вызовов требовала добавления логирования или разбивки выражения на части. С Java 14 JVM анализирует байткод упавшей инструкции и формирует структурированное сообщение из двух частей: **что пытались выполнить** и **почему получили null**.

**Структура сообщения:**

> «[Выполняемая операция] because [причина null]»

Примеры:

```java
// 1. Разыменование цепочки
a.b.c.i = 99;
// "Cannot read field "c" because "a.b" is null"

// 2. Вызов метода на null-объекте
employee.getPersonalDetails().getEmailAddress().toLowerCase();
// "Cannot invoke "String.toLowerCase()" because the return value of
//  "PersonalDetails.getEmailAddress()" is null"

// 3. Обращение к элементу null-массива
int[] arr = null;
int x = arr[0];
// "Cannot load from int array because "arr" is null"

// 4. Null в позиции длины массива
int[] arr2 = new int[obj.size];
// "Cannot read field "size" because "obj" is null"
```

**Когда JVM добавляет детальное сообщение:**

- Только для NPE, сгенерированных самой JVM (при разыменовании ссылки, вызове метода на null и т.д.).
- Для явно созданных `throw new NullPointerException()` или `new NullPointerException("msg")` — детали не добавляются (это код разработчика, не JVM).

**Имена переменных в сообщении:**

```java
// С отладочной информацией (-g или стандартная компиляция javac)
String name = user.getName();  // "user" is null
// → "Cannot invoke "String getName()" because "user" is null"

// Без отладочной информации — компилятор использует индексы
// → "Cannot invoke "String getName()" because "<local1>" is null"
```

**Версии и конфигурация:**

| Версия Java | Поведение по умолчанию |
|---|---|
| Java 14 | Выключено; включается флагом `-XX:+ShowCodeDetailsInExceptionMessages` |
| Java 15 | Включено по умолчанию |
| Java 15+ | Выключить можно флагом `-XX:-ShowCodeDetailsInExceptionMessages` |

**Ленивое вычисление:** сообщение формируется не при возникновении исключения, а при первом вызове `getMessage()` или `toString()` — это снижает накладные расходы в продуктивной среде, где NPE часто перехватываются и не логируются.

**Расхождения:** Baeldung и JEP 358 согласованы. Важный нюанс: JEP 358 явно указывает, что флаг `-XX:+ShowCodeDetailsInExceptionMessages` был необходим в Java 14 из соображений безопасности (детальное сообщение может раскрыть имена полей и методов в окружениях с ограниченным доступом к исходному коду). В Java 15 команда решила, что польза перевешивает риск, и включила функцию по умолчанию.
