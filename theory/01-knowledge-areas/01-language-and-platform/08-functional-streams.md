# Функциональное программирование и Stream API

> **Уровень:** Middle
> **Связанные вопросы:** [Вопросы по лямбдам и Stream API →](../interview-questions/functional-streams-01.md)
> **Связанные области:** [[03-collections]], [[09-modern-java-features]]

## Что это и зачем

С Java 8 язык получил элементы функционального программирования: лямбда-выражения, функциональные
интерфейсы, ссылки на методы и Stream API для декларативной обработки коллекций. Это стандарт
современного Java-кода: потоки делают обработку данных компактной и читаемой, а понимание ленивости
и отличий промежуточных/терминальных операций нужно для корректности и производительности.

Stream API реализует паттерн «конвейер»: источник данных -> цепочка промежуточных операций ->
терминальная операция. Поток не хранит данные сам по себе — он описывает вычисление, которое
запускается только при вызове терминальной операции. Это принципиально отличает стримы от коллекций.

## Ключевые подтемы

### Лямбда-выражения и функциональные интерфейсы

Лямбда — это анонимная функция вида `(параметры) -> тело`. Компилятор выводит целевой тип из
контекста: лямбда должна соответствовать ровно одному функциональному интерфейсу (интерфейс с
единственным абстрактным методом, SAM).

Аннотация `@FunctionalInterface` необязательна, но рекомендована: она запрещает добавление второго
абстрактного метода в интерфейс.

Пакет [`java.util.function`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html)
содержит 43 готовых функциональных интерфейса, сгруппированных по четырём базовым формам:

| Форма | Интерфейс | Абстрактный метод | Смысл |
|---|---|---|---|
| Function | `Function<T,R>` | `R apply(T t)` | T -> R |
| Consumer | `Consumer<T>` | `void accept(T t)` | T -> void |
| Predicate | `Predicate<T>` | `boolean test(T t)` | T -> boolean |
| Supplier | `Supplier<T>` | `T get()` | () -> T |

Бинарные варианты: `BiFunction<T,U,R>`, `BiConsumer<T,U>`, `BiPredicate<T,U>`.

Операторы: `UnaryOperator<T>` (расширяет `Function<T,T>`) и `BinaryOperator<T>` (расширяет
`BiFunction<T,T,T>`). Удобны для операций, сохраняющих тип: `String::concat`, `Integer::sum`.

#### Примитивные специализации

Чтобы избежать autoboxing, в пакете есть специализации для `int`, `long`, `double`:
`IntFunction<R>`, `IntConsumer`, `IntPredicate`, `IntSupplier`, `IntBinaryOperator`,
`IntUnaryOperator` и их аналоги для `long`/`double`. Кроме того, есть конвертирующие формы:
`IntToLongFunction`, `LongToDoubleFunction` и т.д. (6 cross-type пар), а также
`ToIntFunction<T>`, `ToLongFunction<T>`, `ToDoubleFunction<T>` для приведения объекта к
примитиву.

#### Default-методы для композиции

```java
// Function: compose (сначала g, потом f), andThen (сначала f, потом g)
Function<String, Integer> len = String::length;
Function<Integer, String> hex = Integer::toHexString;
Function<String, String> lenHex = len.andThen(hex); // "hello" -> "5"

// Predicate: and, or, negate
Predicate<String> notEmpty = ((Predicate<String>) String::isEmpty).negate();
Predicate<String> longWord = s -> s.length() > 5;
Predicate<String> longNotEmpty = notEmpty.and(longWord);

// Consumer: andThen — цепочка действий
Consumer<String> log = System.out::println;
Consumer<String> logUpper = log.andThen(s -> System.out.println(s.toUpperCase()));
```

### Ссылки на методы (Method References)

Синтаксический сахар для лямбд, которые просто делегируют вызов существующему методу.
Компилятор выводит, какой функциональный интерфейс должна удовлетворять ссылка.

| Форма | Пример | Эквивалентная лямбда |
|---|---|---|
| Статический метод | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| Метод экземпляра конкретного объекта | `System.out::println` | `x -> System.out.println(x)` |
| Метод экземпляра произвольного объекта типа | `String::toUpperCase` | `s -> s.toUpperCase()` |
| Конструктор | `ArrayList::new` | `() -> new ArrayList<>()` |

### Optional

[`java.util.Optional<T>`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html)
— контейнер, который может содержать значение или быть пустым. Цель: явно выразить на уровне
типа, что метод может не вернуть результат, и устранить неявные `null`-возвраты.

**Создание:**

```java
Optional<String> a = Optional.of("hello");       // NPE если null
Optional<String> b = Optional.ofNullable(value); // безопасно, может быть пустым
Optional<String> c = Optional.empty();
```

**Извлечение значения:**

| Метод | Поведение при пустом Optional |
|---|---|
| `get()` | throws `NoSuchElementException` (лучше не использовать) |
| `orElse(T other)` | возвращает `other` (вычисляется всегда!) |
| `orElseGet(Supplier<T>)` | вызывает поставщика лениво |
| `orElseThrow()` | throws `NoSuchElementException` (Java 10, предпочтительнее `get()`) |
| `orElseThrow(Supplier<X>)` | throws исключение от поставщика |

**Важно:** `orElse(heavyComputation())` выполняет `heavyComputation()` всегда, даже если
значение присутствует. Для ленивых вычислений используйте `orElseGet`.

**Трансформации (монадический стиль):**

```java
Optional<String> name = findUser(id)
    .filter(u -> u.isActive())
    .map(User::getName);          // Optional<String>
    // .flatMap возвращает Optional<T> без двойной обёртки

// Java 9: ifPresentOrElse
opt.ifPresentOrElse(
    v -> System.out.println("Found: " + v),
    () -> System.out.println("Not found")
);

// Java 9: or — вернуть другой Optional если пустой
Optional<User> result = findInCache(id).or(() -> findInDb(id));

// Java 9: stream() — интеграция с Stream API
Stream<String> names = optName.stream(); // 0 или 1 элемент
```

**Правила использования:**
- `Optional` предназначен как **возвращаемый тип метода**. Не используйте его как поле класса,
  параметр метода или ключ/значение в коллекции.
- Переменная типа `Optional` никогда не должна быть `null` сама по себе.

### Stream API: архитектура конвейера

Официальная документация: [`java.util.stream`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html).

Конвейер состоит из трёх частей:
1. **Источник** — коллекция, массив, генератор, I/O-канал.
2. **Промежуточные операции** (ноль или больше) — ленивые, возвращают новый `Stream`.
3. **Терминальная операция** — запускает вычисление, возвращает результат или производит
   побочный эффект.

После вызова терминальной операции поток считается **потреблённым** и повторное использование
вызывает `IllegalStateException`.

```java
int sum = widgets.stream()              // источник
    .filter(w -> w.getColor() == RED)   // промежуточная (ленивая)
    .mapToInt(Widget::getWeight)         // промежуточная (ленивая)
    .sum();                              // терминальная — запускает всё
```

#### Создание потоков

```java
// Из коллекции
list.stream();
list.parallelStream();

// Из массива
Arrays.stream(arr);
Arrays.stream(arr, 0, 5); // срез

// Фабричные методы Stream
Stream.of("a", "b", "c");
Stream.empty();
Stream.ofNullable(maybeNull);        // Java 9: 0 или 1 элемент
Stream.concat(stream1, stream2);

// Бесконечные потоки
Stream.iterate(0, n -> n + 1);                          // 0, 1, 2, ...
Stream.iterate(0, n -> n < 100, n -> n + 1);            // Java 9: с предикатом остановки
Stream.generate(Math::random);

// Из других источников
Files.lines(path);
BufferedReader.lines();
Pattern.compile(",").splitAsStream(str);
IntStream.range(0, 10);      // 0..9
IntStream.rangeClosed(1, 5); // 1..5
```

### Промежуточные операции

Делятся на **stateless** (не зависят от других элементов) и **stateful** (требуют обработки всего
потока или его части перед передачей элементов дальше).

**Stateless:**

| Операция | Подпись | Что делает |
|---|---|---|
| `filter` | `Stream<T> filter(Predicate<T> p)` | отфильтровывает элементы |
| `map` | `<R> Stream<R> map(Function<T,R> f)` | преобразует каждый элемент |
| `mapToInt/Long/Double` | `IntStream mapToInt(ToIntFunction<T> f)` | преобразует в примитивный поток |
| `flatMap` | `<R> Stream<R> flatMap(Function<T, Stream<R>> f)` | «разворачивает» вложенные потоки |
| `mapMulti` | `<R> Stream<R> mapMulti(BiConsumer<T, Consumer<R>> m)` | Java 16, замена flatMap для малого числа элементов |
| `peek` | `Stream<T> peek(Consumer<T> action)` | для отладки; не гарантирует выполнение |

**Stateful:**

| Операция | Что делает | Замечание |
|---|---|---|
| `distinct()` | убирает дубликаты (по `equals`) | может буферизовать все элементы |
| `sorted()` | сортировка по естественному порядку | полностью буферизует поток |
| `sorted(Comparator)` | сортировка по компаратору | то же |
| `limit(long n)` | обрезает до n элементов | short-circuit для источника |
| `skip(long n)` | пропускает первые n элементов | stateful для параллельных потоков |
| `takeWhile(Predicate)` | Java 9: берёт элементы пока предикат истинен, затем останавливается | |
| `dropWhile(Predicate)` | Java 9: пропускает элементы пока предикат истинен, затем берёт всё | |

Пример `flatMap` — типичный кейс «список списков в один поток»:

```java
List<List<String>> nested = List.of(List.of("a","b"), List.of("c"));
List<String> flat = nested.stream()
    .flatMap(Collection::stream)  // Stream<String>
    .collect(Collectors.toList());
// ["a","b","c"]
```

`mapMulti` (Java 16) эффективнее `flatMap` когда для каждого элемента генерируется малое
фиксированное число результатов, так как не создаёт промежуточный `Stream` на каждый элемент:

```java
List<Integer> nums = List.of(1, 2, 3);
List<Integer> doubled = nums.stream()
    .<Integer>mapMulti((n, consumer) -> {
        consumer.accept(n);
        consumer.accept(n * 10);
    })
    .toList(); // [1, 10, 2, 20, 3, 30]
```

### Терминальные операции

Терминальные операции запускают выполнение конвейера. После их вызова поток нельзя переиспользовать.

**Поиск и проверка (short-circuit):**

```java
boolean any   = stream.anyMatch(predicate);  // true если хоть один совпал
boolean all   = stream.allMatch(predicate);  // true если все совпали
boolean none  = stream.noneMatch(predicate); // true если ни один не совпал

Optional<T> first = stream.findFirst(); // первый в encounter order
Optional<T> any2  = stream.findAny();   // любой (недетерминированно в parallel)
```

**Свёртка (reduce):**

```java
// С identity — всегда возвращает T
T result = stream.reduce(identity, BinaryOperator<T>);

// Без identity — Optional, если поток пуст
Optional<T> result = stream.reduce(BinaryOperator<T>);

// Трёхаргументная форма для разнотипных свёрток (нужен combiner для parallel)
U result = stream.reduce(identity, BiFunction<U,T,U> accumulator, BinaryOperator<U> combiner);
```

Требования к функциям свёртки: `identity` должен быть нейтральным элементом для `combiner`,
`combiner` и `accumulator` должны быть ассоциативными (для корректной параллельной свёртки).

**Коллекция (collect):**

```java
List<String> list = stream.collect(Collectors.toList());
List<String> immutable = stream.toList(); // Java 16: неизменяемый список
```

**Агрегаты для примитивных потоков (`IntStream`, `LongStream`, `DoubleStream`):**

```java
IntStream is = IntStream.of(1, 2, 3, 4, 5);
int sum   = is.sum();
OptionalInt min  = is.min();
OptionalInt max  = is.max();
OptionalDouble avg = is.average();
IntSummaryStatistics stats = is.summaryStatistics(); // count, sum, min, max, average
```

### Ленивость вычислений и оптимизации

Промежуточные операции ленивы: ни одна из них не выполняется до вызова терминальной операции.
JVM может применять **fusion** (слияние) смежных операций в один проход по данным.

Short-circuit операции (`limit`, `findFirst`, `anyMatch` и др.) позволяют завершить обработку
бесконечного источника в конечное время:

```java
// Первое простое число > 1000
int prime = IntStream.iterate(1001, n -> n + 2)
    .filter(n -> BigInteger.valueOf(n).isProbablePrime(10))
    .findFirst()
    .getAsInt();
```

`peek` предназначен для **отладки**. На результат вычислений он не влияет, но выполнение
не гарантировано: если терминальная операция не запросит элемент (short-circuit), `peek`
для него не выполнится.

### Collectors: сборка результатов

[`java.util.stream.Collectors`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Collectors.html)
— класс статических фабрик для создания объектов `Collector`.

**Базовая сборка:**

```java
List<T>     list   = stream.collect(Collectors.toList());
List<T>     imm    = stream.collect(Collectors.toUnmodifiableList()); // Java 10
Set<T>      set    = stream.collect(Collectors.toSet());
String      joined = stream.collect(Collectors.joining(", ", "[", "]"));
long        count  = stream.collect(Collectors.counting());
```

**Сборка в Map:**

```java
// Дубликаты ключей -> IllegalStateException без mergeFunction
Map<String, User> byName = users.stream()
    .collect(Collectors.toMap(User::getName, u -> u));

// С разрешением дубликатов
Map<String, String> phones = people.stream()
    .collect(Collectors.toMap(
        Person::getName,
        Person::getPhone,
        (existing, replacement) -> existing + ", " + replacement
    ));
```

**Группировка и разбиение:**

```java
// groupingBy — Map<K, List<T>> по умолчанию
Map<Department, List<Employee>> byDept =
    employees.stream().collect(Collectors.groupingBy(Employee::getDepartment));

// groupingBy с downstream-коллектором
Map<Department, Long> countByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.counting()
    ));

// partitioningBy — Map<Boolean, List<T>>
Map<Boolean, List<Student>> passFail = students.stream()
    .collect(Collectors.partitioningBy(s -> s.getGrade() >= 60));
```

**Числовые агрегаты:**

```java
IntSummaryStatistics stats = employees.stream()
    .collect(Collectors.summarizingInt(Employee::getSalary));
// stats.getCount(), getSum(), getMin(), getMax(), getAverage()

double avg = employees.stream()
    .collect(Collectors.averagingInt(Employee::getSalary));
```

**Адаптеры (Java 9+):**

```java
// filtering — фильтрация внутри downstream-коллектора
Map<Dept, List<Employee>> highEarners = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.filtering(e -> e.getSalary() > 100_000, Collectors.toList())
    ));

// flatMapping
Map<City, Set<String>> lastNamesByCity = people.stream()
    .collect(Collectors.groupingBy(
        Person::getCity,
        Collectors.flatMapping(p -> p.getChildren().stream(), Collectors.toSet())
    ));
```

**`teeing` (Java 12)** — одновременная сборка двумя коллекторами с объединением результатов:

```java
record Stats(long count, int sum) {}

Stats stats = IntStream.rangeClosed(1, 10).boxed()
    .collect(Collectors.teeing(
        Collectors.counting(),
        Collectors.summingInt(Integer::intValue),
        (count, sum) -> new Stats(count, sum)
    ));
```

### Параллельные потоки

Параллельный поток разбивает источник на части с помощью `Spliterator` и обрабатывает их
в потоках `ForkJoinPool.commonPool()` (по умолчанию). Количество потоков ≈ числу процессоров.

```java
int sum = list.parallelStream()
    .filter(x -> x > 0)
    .mapToInt(Integer::intValue)
    .sum();
```

**Когда параллельный поток реально ускоряет:**
- Данных много (тысячи и более элементов).
- Операции вычислительно дорогие (CPU-bound).
- Источник хорошо делится (`ArrayList`, массивы — да; `LinkedList` — плохо).
- Нет внешних зависимостей / блокировок.

**Ловушки параллельных потоков:**

1. **Stateful-лямбды** — приводят к недетерминированным результатам. Запрещены.
2. **Изменение источника** во время выполнения (non-concurrent источники) — поведение
   не определено.
3. **`forEach` не гарантирует порядок** в параллельном режиме. Используйте `forEachOrdered`
   если порядок важен (но это снижает параллелизм).
4. **`findAny` vs `findFirst`**: `findFirst` в параллельном потоке сохраняет encounter order
   (дорого), `findAny` — нет.
5. **Overhead**: для небольших коллекций параллельный поток медленнее из-за затрат на разбиение
   и синхронизацию.
6. **`Collectors.groupingByConcurrent`** вместо `groupingBy` для параллельных потоков без
   ограничений на порядок — даёт реальный прирост.

```java
// Плохо: stateful, не потокобезопасно
List<Integer> result = new ArrayList<>();
list.parallelStream().forEach(result::add); // гонка данных!

// Хорошо: потокобезопасный сборщик
List<Integer> result = list.parallelStream().collect(Collectors.toList());
```

**`encounter order` и `unordered()`:** Если порядок не важен, вызов `.unordered()` позволяет
рантайму пропустить операции сохранения порядка и тем самым повысить параллелизм.

```java
list.parallelStream()
    .unordered()
    .filter(...)
    .collect(Collectors.toCollection(HashSet::new));
```

### Характеристики Spliterator

`Spliterator` — итератор с поддержкой параллельного разбиения. Характеристики описывают
свойства источника и используются JVM для оптимизации операций:

| Характеристика | Смысл |
|---|---|
| `ORDERED` | порядок элементов определён |
| `DISTINCT` | нет дубликатов |
| `SORTED` | элементы отсортированы |
| `SIZED` | размер известен |
| `NONNULL` | элементы не null |
| `IMMUTABLE` | источник нельзя изменить |
| `CONCURRENT` | источник поддерживает конкурентную модификацию |
| `SUBSIZED` | дочерние сплитераторы тоже знают свой размер |

Оптимальный `Spliterator` даёт балансированные сплиты с известными размерами — это критично
для эффективного параллелизма.

### Ограничения и важные правила

- **Не переиспользовать поток**: после терминальной операции он потреблён.
- **Не изменять источник** (List, array и т.п.) во время выполнения пайплайна.
- **Избегать побочных эффектов** в промежуточных операциях; `forEach` и `peek` — для
  явных side-effect сценариев.
- **`reduce` требует ассоциативности** накапливающей функции для корректного параллельного
  поведения.
- **`sorted` буферизует весь поток** перед передачей дальше — для параллельного потока это
  особенно дорого.

## Достоверные источники

1. **[Oracle Javadoc — java.util.stream (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html)** —
   официальная документация пакета; содержит исчерпывающее описание модели, ленивости,
   характеристик и требований к поведенческим параметрам. Первичный авторитет.

2. **[Oracle Javadoc — java.util.function (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html)** —
   полный перечень 43 функциональных интерфейсов с правилами именования и соглашениями
   о примитивных специализациях.

3. **[Oracle Javadoc — java.util.stream.Collectors (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Collectors.html)** —
   документация всех фабричных методов `Collectors`, включая `teeing` (Java 12),
   `filtering` и `flatMapping` (Java 9).

4. **[Oracle Javadoc — java.util.Optional (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html)** —
   официальное API `Optional`; содержит предупреждения о назначении класса и
   ограничениях использования.

5. **[Dev.java — Streams (официальный обучающий портал Oracle)](https://dev.java/learn/api/streams/)** —
   структурированный учебный курс Oracle по Stream API от базового до продвинутого уровня,
   включая Gatherer API для Java 22+.

6. **[Baeldung — The Java 8 Stream API Tutorial](https://www.baeldung.com/java-8-streams)** —
   авторитетный практический разбор всех операций Stream API с примерами кода; постоянно
   обновляется под актуальные версии Java.
