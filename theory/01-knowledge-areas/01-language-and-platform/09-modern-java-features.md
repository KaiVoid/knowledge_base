# Современные возможности Java (8 → 25)

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по новым фичам Java →](../interview-questions/modern-java-01.md)
> **Связанные области:** [[08-functional-streams]], [[04-concurrency]], [[01-core-java-syntax-oop]]

## Что это и зачем

Java активно развивается: с переходом на шестимесячный цикл релизов каждые полгода появляются новые
возможности. Современный разработчик должен знать ключевые нововведения от Java 8 до актуальных
LTS-версий (11, 17, 21, 25): они меняют стиль написания кода и часто встречаются на собеседованиях.

Релизный цикл регулируется [JEP 322 (Time-Based Release Versioning)](https://openjdk.org/jeps/322):
каждые 6 месяцев выходит feature-релиз (март и сентябрь). LTS-версии выходят каждые 2 года —
Java 8, 11, 17, 21, 25 (сентябрь 2025). Java 25 поддерживается Oracle как минимум до сентября 2033.

## Ключевые подтемы

---

### Java 8 — фундаментальный сдвиг в сторону функциональности

**JEP 126 (Lambda + Default Methods), JSR 335** — самый масштабный релиз с точки зрения
изменения языка. Четыре ключевых нововведения:

#### Лямбда-выражения и функциональные интерфейсы

Лямбда — анонимная функция вида `(параметры) -> тело`. Работает только там, где ожидается
функциональный интерфейс (интерфейс с одним абстрактным методом, аннотируется `@FunctionalInterface`).

```java
// До Java 8
Comparator<String> c = new Comparator<String>() {
    @Override public int compare(String a, String b) { return a.compareTo(b); }
};

// Java 8+
Comparator<String> c = (a, b) -> a.compareTo(b);
// или ссылка на метод
Comparator<String> c2 = String::compareTo;
```

Пакет `java.util.function` содержит стандартные функциональные интерфейсы:
`Function<T,R>`, `Predicate<T>`, `Consumer<T>`, `Supplier<T>`, `BiFunction<T,U,R>` и другие.

#### Default-методы в интерфейсах

Позволяют добавлять реализацию в интерфейс без нарушения обратной совместимости. Именно они
позволили расширить `Collection`, добавив `forEach`, `stream`, `spliterator` без ломки существующих реализаций.

```java
interface Greeter {
    String greet(String name);
    default String greetLoud(String name) {
        return greet(name).toUpperCase();
    }
}
```

#### Stream API

Ленивые конвейеры обработки данных. Промежуточные операции (`filter`, `map`, `sorted`, `flatMap`)
не вычисляются до вызова терминальной (`collect`, `forEach`, `reduce`, `findFirst` и т.д.).
Подробнее — в области [[08-functional-streams]].

#### `Optional<T>`

Контейнер, явно выражающий возможное отсутствие значения. Документация:
[`java.util.Optional` (Javadoc SE 8)](https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html).

```java
Optional<String> opt = Optional.ofNullable(getValue());
String result = opt
    .filter(s -> !s.isBlank())
    .map(String::trim)
    .orElse("default");
```

#### `java.time` (JSR 310)

Полная замена устаревших `java.util.Date`/`Calendar`. Ключевые классы:
`LocalDate`, `LocalTime`, `LocalDateTime`, `ZonedDateTime`, `Instant`, `Duration`, `Period`.
Все объекты неизменяемы и потокобезопасны.

---

### `var` — локальный вывод типов (Java 10, JEP 286)

[JEP 286](https://openjdk.org/jeps/286) вводит контекстное ключевое слово `var` для локальных
переменных с инициализатором. Тип выводится компилятором статически — это не динамическая типизация.

```java
var list = new ArrayList<String>();    // тип: ArrayList<String>
var map = new HashMap<Integer, List<String>>();
for (var entry : map.entrySet()) {     // Map.Entry<Integer, List<String>>
    System.out.println(entry.getKey());
}
```

**Ограничения** (нельзя применять):
- поля класса
- параметры методов и возвращаемые типы
- переменные без инициализатора: `var x;` — ошибка компиляции
- несколько объявлений: `var a = 1, b = 2;` — ошибка

Java 11 расширил применение `var` на параметры лямбд ([JEP 323](https://openjdk.org/jeps/323)),
что позволяет аннотировать их: `(@NonNull var s) -> s.length()`.

Официальное руководство по стилю: [LVTI Style Guidelines](https://openjdk.org/projects/amber/guides/lvti-style-guide).

---

### Switch Expressions (Java 14, финал — JEP 361)

[JEP 361](https://openjdk.org/jeps/361) (финализирован в Java 14) расширяет `switch`:
теперь он может быть **выражением** (возвращать значение), а не только оператором.

Два новшества:
1. **Стрелочные метки** `case L ->` — без fall-through, правая часть выполняется и всё.
2. **`yield`** — возвращает значение из блочной ветки switch-выражения.

```java
// switch-выражение со стрелками
String season = switch (month) {
    case JANUARY, FEBRUARY, DECEMBER -> "Winter";
    case MARCH, APRIL, MAY           -> "Spring";
    case JUNE, JULY, AUGUST          -> "Summer";
    default                          -> "Autumn";
};

// yield в блочной ветке
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY                -> 7;
    default -> {
        String s = day.toString();
        yield s.length();   // <-- возвращает значение
    }
};
```

---

### Text Blocks (Java 15, JEP 378)

[JEP 378](https://openjdk.org/jeps/378) — многострочные строковые литералы без экранирования.
Открывающий разделитель: `"""` + перевод строки. Закрывающий: `"""` (его отступ определяет
«базовую линию» — общий отступ убирается автоматически).

```java
String json = """
        {
            "name": "Alice",
            "age": 30
        }
        """;

String html = """
        <html>
            <body>
                <p>Hello, World!</p>
            </body>
        </html>
        """;
```

Специальные escape-последовательности text blocks:
- `\<line-terminator>` — подавляет перевод строки (конкатенация строк без `\n`)
- `\s` — явный пробел (предотвращает обрезку trailing-пробелов)

Документация: [Programmer's Guide to Text Blocks](https://openjdk.org/projects/amber/guides/text-blocks-guide).

---

### Records (Java 16, JEP 395)

[JEP 395](https://openjdk.org/jeps/395) — неизменяемые классы-носители данных с минимальным
синтаксисом. Компилятор автоматически генерирует: канонический конструктор, аксессоры (имя = имя компонента),
`equals`, `hashCode`, `toString`. Record неявно `final`, не может расширять другие классы,
но может реализовывать интерфейсы.

```java
record Point(double x, double y) {}

// Использование
Point p = new Point(1.0, 2.0);
System.out.println(p.x());   // 1.0  — аксессор, не getX()
System.out.println(p);        // Point[x=1.0, y=2.0]
```

**Компактный конструктор** — для валидации без явного присваивания полей:

```java
record Range(int lo, int hi) {
    Range {   // нет параметров — это компактный конструктор
        if (lo > hi) throw new IllegalArgumentException("lo > hi");
        // неявное: this.lo = lo; this.hi = hi;
    }
}
```

**Кастомные аксессоры** и дополнительные методы разрешены:

```java
record Name(String first, String last) {
    // переопределение аксессора
    @Override public String first() { return first.trim(); }
    // дополнительный метод
    public String full() { return first() + " " + last; }
}
```

Records хорошо сочетаются с sealed-классами и pattern matching: запись можно деконструировать
прямо в `switch` или `instanceof`.

Официальная документация: [Records (Java SE 17)](https://docs.oracle.com/en/java/javase/17/language/records.html).

---

### Sealed Classes и интерфейсы (Java 17, JEP 409)

[JEP 409](https://openjdk.org/jeps/409) ограничивает иерархию наследования: автор класса/интерфейса
явно указывает допустимых наследников через `permits`. Это делает иерархию **закрытой и исчерпываемой**,
что критично для паттерн-матчинга.

```java
sealed interface Shape permits Circle, Rectangle, Triangle {}

final class Circle    implements Shape { double radius; }
final class Rectangle implements Shape { double w, h; }
non-sealed class Triangle implements Shape { /* можно расширять */ }
```

Допустимые модификаторы для разрешённых подклассов:
- `final` — дальнейшее наследование запрещено
- `sealed` — разрешает следующий уровень иерархии с ограничениями
- `non-sealed` — снимает ограничения (открыт для произвольного наследования)

Компилятор проверяет, что `permits` указывает только на классы в том же пакете/модуле,
что и `sealed`-тип. Если все разрешённые подтипы находятся в том же компиляционном юните,
`permits` можно не писать — компилятор выведет список сам.

---

### Pattern Matching для `instanceof` (Java 16, JEP 394)

[JEP 394](https://openjdk.org/jeps/394) устраняет шаблонный каст:

```java
// До Java 16
if (obj instanceof String) {
    String s = (String) obj;  // явный каст
    System.out.println(s.length());
}

// Java 16+
if (obj instanceof String s) {
    System.out.println(s.length());  // s уже типизирован
}

// можно комбинировать с условием
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.toUpperCase());
}
```

---

### Pattern Matching для `switch` (Java 21, JEP 441)

[JEP 441](https://openjdk.org/jeps/441) финализирует расширение `switch` на тип-паттерны.
Прошёл четыре preview-итерации (JEP 406, 420, 427, 433).

Документация: [Pattern Matching for switch — Oracle](https://docs.oracle.com/en/java/javase/21/language/pattern-matching-switch.html).

#### Тип-паттерны в switch

```java
static String describe(Object obj) {
    return switch (obj) {
        case null              -> "null";
        case Integer i         -> "int: " + i;
        case String s          -> "string of length " + s.length();
        case int[] arr         -> "int array, len=" + arr.length;
        default                -> "other: " + obj.getClass().getSimpleName();
    };
}
```

#### Guarded patterns (охранные условия, `when`)

```java
static void categorize(Object obj) {
    switch (obj) {
        case String s when s.isEmpty()    -> System.out.println("empty string");
        case String s when s.length() < 5 -> System.out.println("short: " + s);
        case String s                     -> System.out.println("long: " + s);
        default                           -> System.out.println("not a string");
    }
}
```

#### Работа с sealed-классами (exhaustive switch)

```java
sealed interface Shape permits Circle, Rectangle {}
record Circle(double r)     implements Shape {}
record Rectangle(double w, double h) implements Shape {}

static double area(Shape s) {
    return switch (s) {
        case Circle c       -> Math.PI * c.r() * c.r();
        case Rectangle r    -> r.w() * r.h();
        // default не нужен — switch exhaustive по sealed-иерархии
    };
}
```

#### Обработка `null`

До Java 21 `switch` бросал `NullPointerException` на `null`. Теперь допускается явный `case null`:

```java
switch (value) {
    case null    -> System.out.println("null!");
    case String s -> System.out.println("string: " + s);
    default      -> System.out.println("other");
}
```

---

### Record Patterns (Java 21, JEP 440)

[JEP 440](https://openjdk.org/jeps/440) позволяет деконструировать record прямо в паттерне,
извлекая компоненты без явных вызовов аксессоров.

```java
record Point(int x, int y) {}
record Rect(Point topLeft, Point bottomRight) {}

// Деконструкция record в instanceof
if (obj instanceof Point(int x, int y)) {
    System.out.println("Point at " + x + "," + y);
}

// Вложенные паттерны
static String describeRect(Object obj) {
    return switch (obj) {
        case Rect(Point(var x1, var y1), Point(var x2, var y2))
            -> "Rect from (%d,%d) to (%d,%d)".formatted(x1, y1, x2, y2);
        default -> "not a rect";
    };
}
```

---

### Unnamed Variables & Patterns (Java 22, JEP 456)

[JEP 456](https://openjdk.org/jeps/456) — `_` как «нет имени». Используется для переменных
и компонентов паттернов, которые нужны синтаксически, но не используются.

```java
// В catch — игнорируем исключение
try { riskyCall(); } catch (IOException _) { fallback(); }

// В for-each — счётчик без имени
int count = 0;
for (var _ : collection) count++;

// В record pattern — не нужен второй компонент
if (obj instanceof Point(int x, _)) { use(x); }

// В switch
switch (event) {
    case OrderPlaced(var id, _) -> process(id);
    case OrderCancelled(var id, _) -> cancel(id);
}
```

Документация: [Unnamed Variables and Patterns](https://docs.oracle.com/en/java/javase/22/language/unnamed-variables-and-patterns.html).

---

### Sequenced Collections (Java 21, JEP 431)

[JEP 431](https://openjdk.org/jeps/431) добавляет три новых интерфейса в Collections Framework
для коллекций с **определённым порядком обхода**:

| Интерфейс | Extends | Реализации |
|---|---|---|
| `SequencedCollection<E>` | `Collection<E>` | `List`, `Deque`, `LinkedHashSet`, `SortedSet` |
| `SequencedSet<E>` | `SequencedCollection<E>`, `Set<E>` | `LinkedHashSet`, `SortedSet` |
| `SequencedMap<K,V>` | `Map<K,V>` | `LinkedHashMap`, `SortedMap` |

Ключевые методы `SequencedCollection`: `getFirst()`, `getLast()`, `addFirst(E)`, `addLast(E)`,
`removeFirst()`, `removeLast()`, `reversed()`.

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
System.out.println(list.getFirst());   // "a"
System.out.println(list.getLast());    // "c"
List<String> reversed = list.reversed(); // [c, b, a] (view)
```

Документация: [Creating Sequenced Collections](https://docs.oracle.com/en/java/javase/21/core/creating-sequenced-collections-sets-and-maps.html).

---

### Виртуальные потоки (Java 21, JEP 444)

[JEP 444](https://openjdk.org/jeps/444) — легковесные потоки, реализованные JVM, а не ОС.
Решают проблему масштабируемости модели «один поток — один OS-поток».

#### Platform Threads vs. Virtual Threads

| Аспект | Platform Thread | Virtual Thread |
|---|---|---|
| Реализация | Обёртка над OS-потоком | Управляется JVM-шедулером |
| Привязка к OS-потоку | Весь жизненный цикл | Только во время CPU-работы |
| Максимальное количество | ~Тысячи | Миллионы |
| Стоимость создания | Высокая (стек ~1 МБ) | Очень низкая |
| Блокирующий I/O | OS-поток блокируется | OS-поток освобождается |

#### Создание виртуальных потоков

```java
// 1. Thread.ofVirtual()
Thread vt = Thread.ofVirtual().name("my-vt").start(() -> {
    System.out.println("Hello from virtual thread");
});
vt.join();

// 2. ExecutorService (рекомендуется для серверного кода)
try (ExecutorService exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10_000; i++) {
        exec.submit(() -> handleRequest());
    }
}  // ожидает завершения всех задач
```

#### Pinning — главное ограничение

Виртуальный поток **прикрепляется (pinned)** к OS-потоку и не может быть вытеснен в двух случаях:
1. Код внутри `synchronized`-блока/метода.
2. Вызов native-метода или foreign function.

Pinning сводит на нет преимущества виртуальных потоков при I/O внутри synchronized-блоков.
**Решение**: заменить `synchronized` на `ReentrantLock`.

```java
// Проблема — виртуальный поток pinned во время I/O
synchronized (lock) {
    result = callDatabase();  // <-- pinned здесь
}

// Решение
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    result = callDatabase();
} finally {
    lock.unlock();
}
```

Начиная с Java 24 ([JEP 491](https://openjdk.org/jeps/491)) проблема с `synchronized` устранена —
виртуальные потоки больше не pinned при синхронизированных блоках.

Диагностика pinning: `java -Djdk.tracePinnedThreads=full MyApp`.

Документация: [Virtual Threads (Oracle Core Guide)](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html).

---

### Structured Concurrency (Java 25, preview — JEP 505)

[JEP 505](https://openjdk.org/jeps/505) — API для структурированного параллелизма. Группа связанных
задач в разных потоках трактуется как **единица работы**: если одна задача завершилась с ошибкой,
остальные отменяются автоматически.

```java
try (var scope = StructuredTaskScope.open()) {
    Subtask<String> user   = scope.fork(() -> fetchUser(id));
    Subtask<Order>  order  = scope.fork(() -> fetchOrder(id));
    scope.join();             // ждём оба fork-а
    return new Response(user.get(), order.get());
}
// При выходе из блока: все незавершённые задачи отменяются
```

В Java 25 конструктор заменён статическим фабричным методом `StructuredTaskScope.open()`.

---

### Scoped Values (Java 25, JEP 506)

[JEP 506](https://openjdk.org/jeps/506) — замена `ThreadLocal` для виртуальных потоков.
`ScopedValue` — неизменяемое значение, видимое внутри области (`where`-блока), автоматически
передаётся дочерним потокам `StructuredTaskScope`.

```java
static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

// Привязка значения к контексту
ScopedValue.where(CURRENT_USER, user).run(() -> {
    handleRequest();   // и все вызываемые методы видят CURRENT_USER.get()
});

// В дочернем методе
void handleRequest() {
    User u = CURRENT_USER.get();  // работает внутри where-блока
}
```

Преимущества перед `ThreadLocal`:
- Неизменяемость исключает скрытое состояние.
- Нет утечек памяти при использовании с виртуальными потоками.
- Автоматическое наследование дочерними потоками в `StructuredTaskScope`.

---

### Обзорная таблица: ключевые фичи по версиям

| Версия | Фича | JEP | Статус |
|---|---|---|---|
| Java 8 | Lambda, Stream, Optional, java.time | JEP 126 | Финал |
| Java 10 | Local-Variable Type Inference (`var`) | JEP 286 | Финал |
| Java 11 | `var` в лямбда-параметрах | JEP 323 | Финал |
| Java 14 | Switch Expressions | JEP 361 | Финал |
| Java 15 | Text Blocks | JEP 378 | Финал |
| Java 16 | Records | JEP 395 | Финал |
| Java 16 | Pattern Matching для `instanceof` | JEP 394 | Финал |
| Java 17 | Sealed Classes | JEP 409 | Финал |
| Java 21 | Pattern Matching для `switch` | JEP 441 | Финал |
| Java 21 | Record Patterns | JEP 440 | Финал |
| Java 21 | Virtual Threads | JEP 444 | Финал |
| Java 21 | Sequenced Collections | JEP 431 | Финал |
| Java 22 | Unnamed Variables & Patterns | JEP 456 | Финал |
| Java 24 | Синхронизация без pinning | JEP 491 | Финал |
| Java 25 | Scoped Values | JEP 506 | Финал |
| Java 25 | Structured Concurrency | JEP 505 | Preview |

---

## Достоверные источники

1. **[OpenJDK JEP Index](https://openjdk.org/jeps/0)** — первоисточник по всем нововведениям
   (JDK Enhancement Proposals). Каждый JEP содержит мотивацию, описание и спецификацию изменения.

2. **[Oracle Java SE Language Updates (Java 21)](https://docs.oracle.com/en/java/javase/21/language/index.html)** —
   официальное описание языковых изменений по версиям: records, sealed, pattern matching, text blocks, var.

3. **[Oracle Java SE Core Libraries Guide — Virtual Threads](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)** —
   официальное руководство по виртуальным потокам: API, паттерны использования, отладка, ограничения.

4. **[Dev.java — официальный учебный портал Oracle](https://dev.java/learn/)** —
   актуальные материалы по новым возможностям языка, поддерживается командой Oracle.

5. **[OpenJDK Project Amber — Design Notes](https://openjdk.org/projects/amber/)** —
   Project Amber отвечает за эволюцию языка (records, sealed, pattern matching, text blocks, var).
   Содержит design notes и style guides.

6. **[Oracle Java SE Support Roadmap](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)** —
   официальный список LTS-версий и сроков поддержки. Достоверен как первоисточник по политике поддержки.
