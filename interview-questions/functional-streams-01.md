# Функциональное программирование и Stream API — часть 1 из 3

> Вопросы 1–20 (в части: 20). Всего в разделе: 50.
> Область знаний: [../knowledge-base/08-functional-streams.md](../knowledge-base/08-functional-streams.md)
> Правила: [RULES.md](RULES.md)
> Части: **ч.1** · [ч.2](functional-streams-02.md) · [ч.3](functional-streams-03.md)

---
### Вопрос 1. Что такое функциональный интерфейс в Java? Можно ли добавить в него статические методы и default-методы, не нарушив его статуса?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Java Functional Interfaces — jenkov.com](https://jenkov.com/tutorials/java-functional-programming/functional-interfaces.html)

Функциональный интерфейс в Java — это интерфейс, содержащий **ровно один абстрактный (нереализованный) метод**. Этот единственный нереализованный метод является ключевым требованием, отличающим функциональные интерфейсы от обычных. При этом функциональный интерфейс может содержать дополнительные `default`- и `static`-методы — они не нарушают его статус, поскольку имеют реализацию. Пример из документации:

```java
public interface MyFunctionalInterface2 {
    public void execute(); // единственный абстрактный метод

    public default void print(String text) {
        System.out.println(text);
    }

    public static void print(String text, PrintWriter writer) throws IOException {
        writer.write(text);
    }
}
```

«Приведённый выше интерфейс по-прежнему считается функциональным интерфейсом в Java, поскольку содержит только один нереализованный метод.»

#### Ответ от Claude

**Функциональный интерфейс** — это интерфейс, у которого ровно **один абстрактный метод** (Single Abstract Method, SAM). Именно к этому методу привязывается лямбда-выражение или ссылка на метод при использовании интерфейса как типа.

**Можно ли добавлять static и default методы, не нарушив статуса?**

Да, можно. Правило одного абстрактного метода не затрагивает:

- **`default`-методы** — у них есть тело реализации, они не являются абстрактными.
- **`static`-методы** — это методы самого интерфейса, не экземплярные; к подсчёту абстрактных методов не относятся.
- **Методы, переопределяющие `public`-методы `java.lang.Object`** (например, `equals`, `hashCode`, `toString`) — также не учитываются, так как реализация будет получена от `Object`.

Хорошей иллюстрацией служит стандартный `java.util.Comparator<T>`: он объявлен функциональным интерфейсом (один абстрактный метод `compare`), но содержит около 10 `default`- и `static`-методов (`reversed()`, `thenComparing()`, `comparing()` и др.).

Источники: [jenkov.com](https://jenkov.com/tutorials/java-functional-programming/functional-interfaces.html), [docs.oracle.com — Default Methods Tutorial](https://docs.oracle.com/javase/tutorial/java/IandI/defaultmethods.html), [docs.oracle.com — @FunctionalInterface SE 8](https://docs.oracle.com/javase/8/docs/api/java/lang/FunctionalInterface.html)

---

### Вопрос 2. Зачем нужна аннотация @FunctionalInterface? Что произойдёт, если добавить второй абстрактный метод в интерфейс, помеченный этой аннотацией?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [FunctionalInterface (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/lang/FunctionalInterface.html)

`@FunctionalInterface` — информационная аннотация (introduced in Java 8), которая указывает, что интерфейс **предназначен** быть функциональным интерфейсом согласно определению Java Language Specification. Компиляторы обязаны генерировать **ошибку времени компиляции**, если:

- аннотированный тип является не интерфейсом (а классом, enum или аннотацией), **либо**
- аннотированный тип не удовлетворяет требованиям функционального интерфейса (т.е. имеет не ровно один абстрактный метод).

Важное замечание из документации: «Компилятор будет рассматривать любой интерфейс, соответствующий определению функционального интерфейса, как функциональный интерфейс **вне зависимости** от того, присутствует ли на нём аннотация `@FunctionalInterface`». Аннотация опциональна, но обеспечивает проверку на этапе компиляции.

#### Ответ от Claude

**Зачем нужна `@FunctionalInterface`:**

Аннотация решает три задачи:
1. **Защита от случайной поломки** — если разработчик или его коллега попытается добавить второй абстрактный метод, компилятор немедленно выдаст ошибку.
2. **Документирование намерения** — явный сигнал читателям кода, что интерфейс предназначен для использования с лямбдами/ссылками на методы.
3. **Подсказка IDE** — среда разработки покажет предупреждение ещё до компиляции.

**Что произойдёт при добавлении второго абстрактного метода:**

Получится **ошибка компиляции** (`compile-time error`). Пример:

```java
@FunctionalInterface
interface MyInterface {
    void doFirst();
    void doSecond(); // ОШИБКА: Multiple non-overriding abstract methods found
}
```

Компилятор выдаст сообщение вида: `Unexpected @FunctionalInterface annotation: MyInterface is not a functional interface`.

**Важные нюансы:**
- Аннотация является *опциональной*: интерфейс с одним абстрактным методом без `@FunctionalInterface` всё равно является функциональным и работает с лямбдами — но не защищён от случайного добавления второго метода.
- `default`- и `static`-методы не являются абстрактными и не влекут ошибку.
- Метод, переопределяющий `public`-метод `java.lang.Object` (например, `boolean equals(Object)`), не засчитывается в счётчик абстрактных методов.

Источники: [docs.oracle.com — @FunctionalInterface SE 8](https://docs.oracle.com/javase/8/docs/api/java/lang/FunctionalInterface.html), [docs.oracle.com — @FunctionalInterface SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/FunctionalInterface.html)

---

### Вопрос 3. Назовите четыре основных встроенных функциональных интерфейса из пакета java.util.function. Какие у них сигнатуры?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [java.util.function (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/util/function/package-summary.html)

Из описания пакета: «Существует несколько базовых форм функций, включая `Function` (унарная функция из `T` в `R`), `Consumer` (унарная функция из `T` в `void`), `Predicate` (унарная функция из `T` в `boolean`) и `Supplier` (нульарная функция в `R`).»

Функциональные интерфейсы обеспечивают целевые типы для лямбда-выражений и ссылок на методы. Каждый функциональный интерфейс имеет один абстрактный метод — *функциональный метод* — к которому сопоставляются параметры и тип возврата лямбды.

#### Ответ от Claude

Четыре основных функциональных интерфейса пакета `java.util.function`:

| Интерфейс | Тип-параметры | Абстрактный метод | Смысл |
|---|---|---|---|
| `Function<T, R>` | `T` — вход, `R` — выход | `R apply(T t)` | Преобразует значение типа T в значение типа R |
| `Consumer<T>` | `T` — вход | `void accept(T t)` | Принимает значение, ничего не возвращает (побочный эффект) |
| `Predicate<T>` | `T` — вход | `boolean test(T t)` | Проверяет условие, возвращает `true`/`false` |
| `Supplier<T>` | `T` — выход | `T get()` | Не принимает аргументов, поставляет значение |

**Примеры использования:**

```java
// Function: конвертация строки в её длину
Function<String, Integer> strLen = String::length;
strLen.apply("hello"); // → 5

// Consumer: вывод в консоль
Consumer<String> printer = System.out::println;
printer.accept("hi"); // печатает "hi"

// Predicate: проверка на пустоту
Predicate<String> isEmpty = String::isEmpty;
isEmpty.test(""); // → true

// Supplier: ленивое создание объекта
Supplier<List<String>> listFactory = ArrayList::new;
listFactory.get(); // → новый ArrayList
```

**Производные интерфейсы** строятся на тех же четырёх базах:
- `BiFunction<T, U, R>` — `Function` с двумя аргументами
- `UnaryOperator<T>` — частный случай `Function<T, T>` (вход и выход одного типа)
- `BinaryOperator<T>` — частный случай `BiFunction<T, T, T>`
- `IntPredicate`, `LongFunction<R>` и т.д. — примитивные специализации

Источники: [docs.oracle.com — java.util.function SE 8](https://docs.oracle.com/javase/8/docs/api/java/util/function/package-summary.html), [docs.oracle.com — Consumer SE 8](https://docs.oracle.com/javase/8/docs/api/java/util/function/Consumer.html), [docs.oracle.com — Predicate SE 8](https://docs.oracle.com/javase/8/docs/api/java/util/function/Predicate.html)

---

### Вопрос 4. Какие четыре вида ссылок на методы (method references) существуют в Java? Приведите пример каждого.

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Method References — The Java™ Tutorials, docs.oracle.com](https://docs.oracle.com/javase/tutorial/java/javaOO/methodreferences.html)

Документация Oracle описывает четыре вида ссылок на методы:

| Вид | Синтаксис | Пример |
|---|---|---|
| Ссылка на статический метод | `ContainingClass::staticMethodName` | `Person::compareByAge` |
| Ссылка на метод экземпляра конкретного объекта | `containingObject::instanceMethodName` | `myComparisonProvider::compareByName` |
| Ссылка на метод экземпляра произвольного объекта заданного типа | `ContainingType::methodName` | `String::compareToIgnoreCase` |
| Ссылка на конструктор | `ClassName::new` | `HashSet::new` |

«Ссылки на методы — это компактные, легко читаемые лямбда-выражения для методов, у которых уже есть имя.»

#### Ответ от Claude

В Java существует четыре вида ссылок на методы (все используют оператор `::`):

**1. Ссылка на статический метод** — `ClassName::staticMethod`

```java
// Эквивалент: (a, b) -> Integer.compare(a, b)
Comparator<Integer> cmp = Integer::compare;
```

**2. Ссылка на метод экземпляра конкретного объекта** — `instance::instanceMethod`

```java
String prefix = "Hello, ";
// Эквивалент: s -> prefix.concat(s)
Function<String, String> greeter = prefix::concat;
greeter.apply("World"); // → "Hello, World"
```

Объект (`prefix`) зафиксирован в момент создания ссылки.

**3. Ссылка на метод экземпляра произвольного объекта заданного типа** — `ClassName::instanceMethod`

```java
// Эквивалент: (s1, s2) -> s1.compareToIgnoreCase(s2)
// Первый параметр лямбды становится получателем вызова
Comparator<String> cmp = String::compareToIgnoreCase;
Arrays.sort(arr, String::compareToIgnoreCase);
```

Отличие от вида 2: получатель вызова **не фиксирован** — он берётся из первого аргумента лямбды.

**4. Ссылка на конструктор** — `ClassName::new`

```java
// Эквивалент: () -> new ArrayList<>()
Supplier<List<String>> listFactory = ArrayList::new;

// Эквивалент: s -> new StringBuilder(s)
Function<String, StringBuilder> sbFactory = StringBuilder::new;
```

**Итоговая таблица:**

| Вид | Синтаксис | Лямбда-эквивалент |
|---|---|---|
| Статический метод | `Class::staticMethod` | `(args) -> Class.staticMethod(args)` |
| Метод конкретного экземпляра | `obj::method` | `(args) -> obj.method(args)` |
| Метод произвольного экземпляра | `Class::method` | `(obj, args) -> obj.method(args)` |
| Конструктор | `Class::new` | `(args) -> new Class(args)` |

Источники: [docs.oracle.com — Method References Tutorial](https://docs.oracle.com/javase/tutorial/java/javaOO/methodreferences.html)

---
### Вопрос 5. Что такое Stream в Java? Чем Stream отличается от Collection?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [java.util.stream (Java Platform SE 8) — Oracle Documentation](https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html)

Stream — это последовательность элементов, поддерживающая последовательные и параллельные операции агрегирования. Stream не является структурой данных и не хранит элементы: вместо этого он передаёт элементы из источника (коллекции, массива, генератора, I/O-канала) через конвейер вычислительных операций.

Документация Oracle выделяет **пять ключевых отличий** Stream от Collection:

1. **Отсутствие хранилища.** Stream не хранит элементы — он передаёт их из источника через конвейер операций.
2. **Функциональная природа.** Операция над Stream производит результат, но не изменяет источник. Например, фильтрация Stream, полученного из коллекции, создаёт новый Stream без отфильтрованных элементов, а не удаляет их из исходной коллекции.
3. **Ленивость (laziness-seeking).** Многие операции, такие как фильтрация, преобразование или удаление дубликатов, могут выполняться лениво, открывая возможности для оптимизации.
4. **Возможная неограниченность.** Коллекции имеют конечный размер, а Stream — нет. Short-circuit операции, такие как `limit(n)` или `findFirst()`, позволяют вычислениям над бесконечными стримами завершаться за конечное время.
5. **Одноразовость (consumable).** Элементы Stream посещаются только один раз за время его жизни. Подобно `Iterator`, для повторного обхода тех же элементов необходимо создать новый Stream.

#### Ответ от Claude

**Stream** — это интерфейс из пакета `java.util.stream`, представляющий последовательность элементов и поддерживающий функциональные операции агрегирования над ними. Stream не хранит данные — он описывает конвейер преобразований над источником данных.

**Ключевые отличия от Collection:**

| Характеристика | Collection | Stream |
|---|---|---|
| Хранение данных | Да, хранит элементы | Нет, передаёт элементы через конвейер |
| Изменяемость источника | Операции могут изменять коллекцию | Операции никогда не изменяют источник |
| Итерация | Внешняя (explicit for/iterator) | Внутренняя (управляется самим Stream) |
| Повторное использование | Да, можно обходить многократно | Нет, одноразовый — после терминальной операции нельзя переиспользовать |
| Размер | Всегда конечный | Может быть бесконечным (через `Stream.generate`, `Stream.iterate`) |
| Выполнение | Eager — операции выполняются сразу | Lazy — промежуточные операции откладываются до вызова терминальной |
| Параллелизм | Требует внешней синхронизации | Встроенный через `parallelStream()` |

**Пример:**

```java
// Collection — данные хранятся в памяти
List<String> list = Arrays.asList("a", "b", "c");

// Stream — конвейер над данными, ничего не хранит
long count = list.stream()
    .filter(s -> !s.equals("b"))   // промежуточная операция (ленивая)
    .count();                       // терминальная операция (запускает конвейер)
```

Stream создаётся из источника методом `.stream()` (или `.parallelStream()`), затем через цепочку промежуточных операций строится конвейер, который запускается только при вызове терминальной операции.

---

### Вопрос 6. В чём разница между промежуточными (intermediate) и терминальными (terminal) операциями Stream? Приведите по 3 примера каждого вида.

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Stream (Java Platform SE 8) — Oracle Documentation](https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html)

Согласно официальной документации Oracle, операции над Stream делятся на два типа:

**Промежуточные операции** возвращают новый Stream. Они всегда ленивы: выполнение такой операции, как `filter()`, не производит никакой фильтрации — вместо этого создаётся новый Stream, который при обходе будет содержать элементы исходного Stream, соответствующие заданному предикату.

**Терминальные операции** обходят Stream и производят результат или побочный эффект. После выполнения терминальной операции конвейер считается потреблённым и не может быть использован повторно. Терминальные операции являются eager (жадными) и полностью завершают обход источника данных перед тем, как вернуть результат.

Примеры из документации:
- Промежуточные: `filter()`, `map()`, `sorted()`, `distinct()`, `limit()`, `peek()`
- Терминальные: `forEach()`, `reduce()`, `collect()`, `count()`, `anyMatch()`, `findFirst()`

#### Ответ от Claude

**Промежуточные (intermediate) операции:**
- Возвращают новый `Stream<T>` — позволяют строить цепочки.
- Ленивы (lazy): реальная обработка элементов не происходит до вызова терминальной операции.
- Можно вызывать сколько угодно раз в цепочке.

**Терминальные (terminal) операции:**
- Возвращают не-Stream результат (число, коллекцию, `Optional`, `void` и т.д.) или производят побочный эффект.
- Eager (жадные): запускают выполнение всего конвейера.
- После вызова Stream считается потреблённым — его нельзя использовать повторно.

**3 примера промежуточных операций:**

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);

// 1. filter() — отбирает элементы по предикату
Stream<Integer> evenStream = numbers.stream()
    .filter(n -> n % 2 == 0);  // создаёт новый Stream, ничего не выполняет

// 2. map() — преобразует каждый элемент
Stream<String> strStream = numbers.stream()
    .map(n -> "num:" + n);  // новый Stream строк

// 3. sorted() — сортирует элементы (stateful intermediate operation)
Stream<Integer> sortedStream = numbers.stream()
    .sorted(Comparator.reverseOrder());  // новый отсортированный Stream
```

**3 примера терминальных операций:**

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);

// 1. collect() — собирает элементы в коллекцию
List<Integer> evens = numbers.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());  // запускает конвейер, возвращает List

// 2. count() — возвращает количество элементов
long count = numbers.stream()
    .filter(n -> n > 3)
    .count();  // возвращает long: 3

// 3. findFirst() — возвращает первый элемент, соответствующий условию
Optional<Integer> first = numbers.stream()
    .filter(n -> n > 4)
    .findFirst();  // возвращает Optional<Integer> со значением 5
```

**Важное следствие:** так как промежуточные операции ленивы, а терминальные — нет, весь реальный обход элементов происходит ровно один раз — в момент вызова терминальной операции.

---

### Вопрос 7. Что такое ленивые вычисления (lazy evaluation) в стримах и почему это важно с точки зрения производительности?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [java.util.stream (Java Platform SE 8) — Oracle Documentation](https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html)

Согласно официальной документации Oracle, ленивость стримов даёт существенные преимущества производительности:

«Обработка стримов в ленивом режиме допускает значительные оптимизации. В конвейере вида filter–map–sum операции фильтрации, преобразования и суммирования могут быть объединены в один проход по данным с минимальным промежуточным состоянием. Ленивость также позволяет избежать проверки всех данных, когда в этом нет необходимости: для операций типа "найти первую строку длиннее 1000 символов" достаточно проверить лишь столько строк, сколько нужно для нахождения первой подходящей — без проверки всех строк источника.»

Документация также указывает: «Обход источника конвейера не начинается до тех пор, пока не будет вызвана терминальная операция конвейера.»

#### Ответ от Claude

**Ленивые вычисления (lazy evaluation)** в стримах означают, что промежуточные операции (`filter`, `map`, `sorted` и др.) не выполняются в момент их вызова. Они лишь регистрируются как шаги конвейера. Реальная обработка элементов начинается только в момент вызова терминальной операции.

**Механизм работы:**

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve");

// Шаги 1–2 ничего НЕ выполняют — только строят конвейер:
Stream<String> pipeline = names.stream()
    .filter(s -> {
        System.out.println("filter: " + s);  // не выводится сейчас
        return s.length() > 3;
    })
    .map(s -> {
        System.out.println("map: " + s);     // не выводится сейчас
        return s.toUpperCase();
    });

// Только здесь запускается обработка:
Optional<String> result = pipeline.findFirst();
// Вывод: filter: Alice → map: Alice → (остановка, первый найден)
// Bob, Charlie, David, Eve — не обрабатываются вовсе
```

**Преимущества для производительности:**

1. **Слияние операций в один проход (fusion).** Несколько промежуточных операций выполняются за один обход источника, а не за N последовательных обходов.

2. **Short-circuit (короткое замыкание).** Терминальные операции `findFirst()`, `findAny()`, `anyMatch()`, `limit()` останавливают обработку сразу после получения нужного результата. Без ленивости пришлось бы обработать все элементы.

3. **Работа с бесконечными последовательностями.** Ленивость позволяет работать со стримами, не имеющими конца:

```java
// Без ленивых вычислений это зависло бы навсегда:
OptionalInt first = IntStream.iterate(0, n -> n + 1)
    .filter(n -> n % 7 == 0 && n > 100)
    .findFirst();  // вернёт 105 и остановится
```

4. **Экономия памяти.** Промежуточные результаты не материализуются в коллекции — элементы проходят через конвейер по одному.

**Важно:** не все промежуточные операции полностью ленивы. Stateful-операции (`sorted()`, `distinct()`) вынуждены потребить весь стрим перед тем, как передать элементы дальше, что ограничивает эффект ленивости.

---

### Вопрос 8. Для чего предназначен класс Optional? Как правильно создать пустой Optional и Optional со значением?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Optional (Java Platform SE 8) — Oracle Documentation](https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html)

Согласно официальной документации Oracle:

«Optional — это контейнерный объект, который может содержать или не содержать ненулевое значение. Если значение присутствует, `isPresent()` вернёт `true`, а `get()` вернёт значение.»

Дополнительные методы, зависящие от наличия или отсутствия значения: `orElse()` (вернуть значение по умолчанию, если значение отсутствует) и `ifPresent()` (выполнить блок кода, если значение присутствует).

**Статические фабричные методы для создания:**

- `Optional.empty()` — возвращает пустой экземпляр Optional. Для данного Optional значение отсутствует.
- `Optional.of(T value)` — возвращает Optional с указанным ненулевым значением. Выбрасывает `NullPointerException`, если значение равно `null`.
- `Optional.ofNullable(T value)` — возвращает Optional, описывающий указанное значение, если оно ненулевое; в противном случае возвращает пустой Optional.

#### Ответ от Claude

**Назначение Optional:**

`Optional<T>` — это обёрточный контейнер (wrapper), введённый в Java 8 для явного представления значения, которое может отсутствовать. Основная цель — устранить `NullPointerException` и сделать отсутствие значения частью типовой системы, а не скрытым соглашением.

Согласно официальной документации, `Optional` предназначен прежде всего для использования в качестве **возвращаемого типа метода**, когда нужно явно выразить, что результат может отсутствовать.

**Три способа создания Optional:**

```java
// 1. Пустой Optional (значение заведомо отсутствует)
Optional<String> empty = Optional.empty();
System.out.println(empty.isPresent()); // false

// 2. Optional.of() — для заведомо ненулевого значения
// ОСТОРОЖНО: бросает NullPointerException, если передать null
Optional<String> opt1 = Optional.of("Hello");
System.out.println(opt1.get()); // "Hello"

Optional<String> opt2 = Optional.of(null); // NullPointerException!

// 3. Optional.ofNullable() — для значения, которое может быть null
// Безопасный вариант: если null — вернёт empty Optional
String maybeNull = null;
Optional<String> opt3 = Optional.ofNullable(maybeNull);
System.out.println(opt3.isPresent()); // false

Optional<String> opt4 = Optional.ofNullable("World");
System.out.println(opt4.get()); // "World"
```

**Правило выбора метода создания:**
- `Optional.empty()` — когда точно нет значения.
- `Optional.of(value)` — когда значение точно не `null` (например, результат вычисления, которое всегда что-то возвращает).
- `Optional.ofNullable(value)` — когда значение может быть `null` (например, результат обращения к базе данных или внешнему API).

**Правильное использование Optional:**

```java
// Хорошо: Optional как возвращаемый тип
public Optional<User> findUserById(long id) {
    return userRepository.findById(id); // может вернуть empty
}

// Хорошо: безопасная работа с Optional
Optional<User> user = findUserById(42L);
String name = user.map(User::getName).orElse("Unknown");

// Плохо: использование get() без проверки isPresent()
// может бросить NoSuchElementException
String bad = user.get(); // не делайте так без проверки
```

**Чего избегать:** не рекомендуется использовать `Optional` как тип поля класса, параметра метода или в коллекциях — это не соответствует назначению класса и ухудшает производительность.

---
### Вопрос 9. В чём разница между Optional.orElse() и Optional.orElseGet()? В каком случае orElseGet() предпочтительнее?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [HowToDoInJava — Optional.orElse() vs orElseGet()](https://howtodoinjava.com/java8/optional-orelse-and-oreleseget/)

`orElse()` принимает значение-по-умолчанию напрямую и вычисляет его **жадно (eagerly)** — независимо от того, содержит ли Optional значение или нет. `orElseGet()` принимает `Supplier` и вычисляет значение **лениво (lazily)** — только если Optional пуст.

Пример, демонстрирующий разницу:

```java
Optional<String> optional = Optional.of("Hello");

// generateDefaultValue() БУДЕТ вызвана, несмотря на то что Optional не пуст
String result1 = optional.orElse(generateDefaultValue());

// generateDefaultValue() НЕ будет вызвана, т.к. Optional содержит значение
String result2 = optional.orElseGet(() -> generateDefaultValue());
```

Вывод: `orElse()` следует использовать для простых константных значений; `orElseGet()` предпочтительнее, когда вычисление значения по умолчанию требует затратных операций (запрос к БД, вызов внешнего API, сложные вычисления).

#### Ответ от Claude

**Сигнатуры методов** (из официальной документации Oracle — `java.util.Optional`):

```java
public T orElse(T other)
public T orElseGet(Supplier<? extends T> other)
```

**Ключевое различие: способ вычисления аргумента**

| Характеристика | `orElse(T other)` | `orElseGet(Supplier<? extends T> other)` |
|---|---|---|
| Тип аргумента | Готовое значение | Поставщик (`Supplier`) |
| Когда вычисляется | Всегда (до вызова метода) | Только если Optional пуст |
| Стратегия | Жадная (eager) | Ленивая (lazy) |
| Риск | Лишние вычисления | Нет |

**Причина поведения `orElse()`**: Java вычисляет аргументы метода **до** его вызова. Поэтому выражение, переданное в `orElse()`, всегда выполняется, даже если Optional содержит значение.

**Когда `orElseGet()` предпочтительнее:**

1. **Дорогостоящие вычисления**: запрос к базе данных, HTTP-запрос, сложный алгоритм.
2. **Операции с побочными эффектами**: если вычисление значения по умолчанию меняет состояние системы.
3. **Вызовы конструкторов**: создание объектов с ресурсоёмкой инициализацией.

```java
// Плохо: запрос к БД выполнится ВСЕГДА, даже если пользователь найден
User user = findUserById(id).orElse(userRepository.getDefaultUser());

// Хорошо: запрос к БД выполнится только если пользователь НЕ найден
User user = findUserById(id).orElseGet(() -> userRepository.getDefaultUser());
```

**Для константных значений** разницы в поведении нет — обе формы корректны:

```java
String name = optional.orElse("default");       // OK для константы
String name = optional.orElseGet(() -> "default"); // избыточно для константы
```

`orElseGet()` также бросает `NullPointerException`, если значение отсутствует, а переданный `Supplier` равен `null`.

---

### Вопрос 10. Что делает операция map() и чем она отличается от flatMap()? Когда нужно использовать flatMap()?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [HowToDoInJava — Stream map() vs flatMap()](https://howtodoinjava.com/java8/stream-map-vs-flatmap/)

`map()` выполняет преобразование «один к одному»: каждый входной элемент порождает ровно один выходной элемент. `flatMap()` выполняет преобразование «один ко многим» и затем **уплощает** (flattens) результат: каждый входной элемент отображается в поток (`Stream`), а все такие потоки сливаются в один.

Пример с вложенными списками:

```java
List<List<Integer>> nestedLists = Arrays.asList(
    Arrays.asList(1, 2, 3),
    Arrays.asList(4, 5)
);

// map вернёт Stream<List<Integer>> — вложенную структуру
// flatMap вернёт Stream<Integer> — плоский поток
List<Integer> flat = nestedLists.stream()
    .flatMap(list -> list.stream())
    .toList();  // [1, 2, 3, 4, 5]
```

`flatMap()` следует использовать когда нужно преобразовать `Collection<Collection<T>>` в `Collection<T>`, а также при разбиении строк на слова.

#### Ответ от Claude

**Сигнатуры методов** (из официального Javadoc `java.util.stream.Stream`):

```java
// map: функция возвращает одно значение типа R
<R> Stream<R> map(Function<? super T, ? extends R> mapper)

// flatMap: функция возвращает Stream<R>, который затем "разворачивается"
<R> Stream<R> flatMap(Function<? super T, ? extends Stream<? extends R>> mapper)
```

**Сравнение поведения:**

| Характеристика | `map()` | `flatMap()` |
|---|---|---|
| Тип отображения | Один к одному | Один ко многим |
| Функция-маппер возвращает | Значение типа `R` | `Stream<R>` |
| Что происходит с результатом | Оборачивается в Stream | Разворачивается (flatten) в общий Stream |
| Тип результата при `Stream<List<T>>` | `Stream<Stream<T>>` | `Stream<T>` |

**Когда использовать `map()`** — преобразование каждого элемента в одно новое значение:

```java
// Получить список имён сотрудников
List<String> names = employees.stream()
    .map(Employee::getName)
    .toList();
```

**Когда использовать `flatMap()`:**

1. **Вложенные коллекции** — развернуть `List<List<T>>` в `List<T>`:

```java
List<List<String>> matrix = List.of(
    List.of("a", "b"),
    List.of("c", "d")
);
List<String> flat = matrix.stream()
    .flatMap(Collection::stream)
    .toList(); // ["a", "b", "c", "d"]
```

2. **Разбиение строк на части**:

```java
// Из потока строк получить поток всех слов
List<String> words = lines.stream()
    .flatMap(line -> Arrays.stream(line.split(" ")))
    .toList();
```

3. **Плоский обход вложенных структур** (заказы → строки заказа):

```java
// Из Oracle Javadoc: заказы → все позиции заказов
orders.flatMap(order -> order.getLineItems().stream())...
```

4. **`Optional` + `flatMap`** — когда метод возвращает `Optional<Optional<T>>`:

```java
Optional<String> result = optional.flatMap(this::findSomething);
// вместо Optional<Optional<String>>
```

**Ключевое правило**: если маппер возвращает `Stream` (или коллекцию, преобразованную в `Stream`), и вы хотите работать с её элементами как с единым потоком — используйте `flatMap`.

---

### Вопрос 11. Как работает операция reduce()? В чём разница между reduce() и collect()?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Oracle Java Tutorials — Reduction](https://docs.oracle.com/javase/tutorial/collections/streams/reduction.html)

`reduce()` — это терминальная операция общего назначения, которая последовательно применяет **аккумулирующую функцию** к элементам потока, сворачивая их в одно значение. Принимает два параметра: `identity` (начальное/нейтральное значение) и `accumulator` (функция, объединяющая частичный результат с очередным элементом).

```java
Integer totalAge = roster.stream()
    .map(Person::getAge)
    .reduce(0, (a, b) -> a + b);
```

Ключевое различие между `reduce()` и `collect()`:

- `reduce()` **всегда создаёт новое значение** на каждом шаге аккумуляции — это иммутабельная редукция.
- `collect()` **модифицирует существующий контейнер** — это мутабельная редукция.

Если накапливать элементы в коллекцию через `reduce()`, на каждом шаге создавался бы новый список — это неэффективно. `collect()` решает эту проблему.

#### Ответ от Claude

**Три перегрузки `reduce()`** (из `java.util.stream.Stream` Javadoc):

```java
// 1. Без identity — возвращает Optional (поток может быть пуст)
Optional<T> reduce(BinaryOperator<T> accumulator)

// 2. С identity — возвращает T (identity — нейтральный элемент)
T reduce(T identity, BinaryOperator<T> accumulator)

// 3. С identity, accumulator и combiner — для параллельных потоков
// где тип результата U отличается от типа элементов T
<U> U reduce(U identity,
             BiFunction<U, ? super T, U> accumulator,
             BinaryOperator<U> combiner)
```

**Как работает `reduce(identity, accumulator)`** — псевдокод из Javadoc:

```java
T result = identity;
for (T element : stream)
    result = accumulator.apply(result, element);
return result;
```

`identity` — **нейтральный элемент** операции: для суммирования это `0`, для умножения — `1`, для конкатенации строк — `""`.

**Combiner** в третьей перегрузке нужен только для параллельных потоков: разные потоки вычисляют частичные результаты, combiner их объединяет.

**Разница `reduce()` vs `collect()`:**

| Критерий | `reduce()` | `collect()` |
|---|---|---|
| Тип редукции | Иммутабельная | Мутабельная |
| Поведение аккумулятора | Создаёт новое значение на каждом шаге | Модифицирует существующий контейнер |
| Лучше подходит для | Скалярных агрегатов (сумма, max, min) | Сборки коллекций, сложных группировок |
| Эффективность при сборке коллекций | Низкая (O(n²) при копировании) | Высокая |
| Возвращаемый тип | Одно значение / `Optional<T>` | Произвольный контейнер `R` |

**`reduce()` — когда применять:**

```java
// Сумма
int sum = numbers.stream().reduce(0, Integer::sum);

// Максимум
Optional<Integer> max = numbers.stream().reduce(Integer::max);

// Произведение
int product = numbers.stream().reduce(1, (a, b) -> a * b);
```

**`collect()` — когда применять (сборка коллекций):**

```java
// Эффективный сбор в список
List<String> names = employees.stream()
    .map(Employee::getName)
    .collect(Collectors.toList());
```

Попытка собрать коллекцию через `reduce()` неэффективна: каждый шаг создавал бы новый `ArrayList` с копированием всех предыдущих элементов. `collect()` использует один изменяемый контейнер на протяжении всей операции.

---

### Вопрос 12. Что такое Collector? Как работает Collectors.groupingBy() и как с его помощью получить Map<String, List<T>>?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Oracle Javadoc — java.util.stream.Collectors](https://docs.oracle.com/javase/8/docs/api/java/util/stream/Collectors.html)

`Collector` — интерфейс, описывающий операцию мутабельной редукции: накопление элементов потока в изменяемый контейнер-результат. Имеет три типовых параметра: `T` (тип входных элементов), `A` (тип промежуточного контейнера), `R` (тип финального результата).

`groupingBy(classifier)` реализует операцию «группировка по» и возвращает `Map<K, List<T>>`, где ключ — результат применения функции-классификатора к элементу, а значение — список элементов с одинаковым ключом. Эквивалентно `groupingBy(classifier, toList())`.

```java
// Группировка сотрудников по отделу
Map<Department, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment));

// Группировка с downstream collector — сумма зарплат по отделам
Map<Department, Integer> totalByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.summingInt(Employee::getSalary)
    ));
```

#### Ответ от Claude

**Интерфейс `Collector<T, A, R>`** (из `java.util.stream.Collector` Javadoc):

Абстрагирует четыре функции мутабельной редукции:

| Метод интерфейса | Тип | Назначение |
|---|---|---|
| `supplier()` | `Supplier<A>` | Создаёт новый изменяемый контейнер-результат |
| `accumulator()` | `BiConsumer<A, T>` | Добавляет элемент в контейнер |
| `combiner()` | `BinaryOperator<A>` | Объединяет два частичных контейнера (для параллельных потоков) |
| `finisher()` | `Function<A, R>` | Выполняет финальное преобразование контейнера в результат |

Это ключевое отличие от `reduce()`: `Collector` работает с **мутабельным** контейнером типа `A`, поэтому эффективен при сборке коллекций.

**`Collectors.groupingBy()` — три перегрузки:**

```java
// 1. Базовая — возвращает Map<K, List<T>>
static <T,K> Collector<T,?,Map<K,List<T>>> groupingBy(
    Function<? super T,? extends K> classifier)

// 2. С downstream collector — дополнительная обработка каждой группы
static <T,K,A,D> Collector<T,?,Map<K,D>> groupingBy(
    Function<? super T,? extends K> classifier,
    Collector<? super T,A,D> downstream)

// 3. С указанием конкретной реализации Map
static <T,K,D,A,M extends Map<K,D>> Collector<T,?,M> groupingBy(
    Function<? super T,? extends K> classifier,
    Supplier<M> mapFactory,
    Collector<? super T,A,D> downstream)
```

**Получение `Map<String, List<T>>`** — базовая перегрузка:

```java
// Группировка студентов по специальности
Map<String, List<Student>> byMajor = students.stream()
    .collect(Collectors.groupingBy(Student::getMajor));
// Результат: {"Math" -> [s1, s3], "CS" -> [s2, s4, s5], ...}
```

**Примеры с downstream collectors:**

```java
// Количество студентов по специальности (не список, а Long)
Map<String, Long> countByMajor = students.stream()
    .collect(Collectors.groupingBy(
        Student::getMajor,
        Collectors.counting()
    ));

// Только имена студентов по специальности (Map<String, List<String>>)
Map<String, List<String>> namesByMajor = students.stream()
    .collect(Collectors.groupingBy(
        Student::getMajor,
        Collectors.mapping(Student::getName, Collectors.toList())
    ));

// Упорядоченный TreeMap вместо HashMap
Map<String, List<Student>> sorted = students.stream()
    .collect(Collectors.groupingBy(
        Student::getMajor,
        TreeMap::new,
        Collectors.toList()
    ));
```

**Важные детали:**
- По умолчанию `groupingBy()` возвращает `HashMap` — порядок ключей не гарантирован.
- Для многоуровневой группировки можно вкладывать `groupingBy` в downstream: `groupingBy(classifier1, groupingBy(classifier2))`.
- Для параллельных потоков существует `groupingByConcurrent()`, возвращающий `ConcurrentMap`.

---
### Вопрос 13. Чем Collectors.toUnmodifiableList() отличается от Collectors.toList() в Java 10+? Какие гарантии даёт каждый?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Collectors (Java SE 10 & JDK 10) — docs.oracle.com](https://docs.oracle.com/javase/10/docs/api/java/util/stream/Collectors.html)

Согласно официальной документации:

**`Collectors.toList()`** — возвращает `Collector`, который накапливает входные элементы в новый `List`. При этом **не даётся никаких гарантий** относительно типа, изменяемости, сериализуемости или потокобезопасности возвращаемого `List`. Если нужен больший контроль, следует использовать `toCollection(Supplier)`.

**`Collectors.toUnmodifiableList()`** — возвращает `Collector`, который накапливает входные элементы в **неизменяемый** `List` в порядке встречи (encounter order). Возвращаемый `Collector` **запрещает `null`-значения** и выбрасывает `NullPointerException`, если встречает `null`.

Таким образом, ключевые отличия:
- `toList()` — нет гарантий изменяемости (хотя на практике возвращает `ArrayList`)
- `toUnmodifiableList()` — гарантированно неизменяемый список, `null`-значения запрещены

#### Ответ от Claude

**`Collectors.toList()`** (существует с Java 8):
- Спецификация намеренно **не гарантирует** тип, изменяемость, сериализуемость и потокобезопасность результата.
- На практике в текущих реализациях OpenJDK возвращает `ArrayList`, однако это **деталь реализации**, а не контракт API.
- Допускает `null`-элементы в потоке.
- Возвращённый список можно изменять (добавлять/удалять элементы).

**`Collectors.toUnmodifiableList()`** (добавлен в Java 10):
- Гарантирует, что результат **неизменяем**: вызов `add()`, `remove()`, `set()` и т. д. выбросит `UnsupportedOperationException`.
- **Запрещает `null`-значения**: при наличии `null` в потоке выбрасывается `NullPointerException`.
- Реализован через finisher-шаг: собирает элементы во внутренний `ArrayList`, затем оборачивает его через `List.of()` (или аналогичный механизм), делая список неизменяемым. Исходный изменяемый список никуда не утекает.
- До Java 10 тот же эффект достигался вручную: `Collectors.collectingAndThen(Collectors.toList(), Collections::unmodifiableList)`.

**Сравнительная таблица:**

| Свойство | `toList()` | `toUnmodifiableList()` |
|---|---|---|
| Изменяемость | Не гарантируется (на практике мутабелен) | Гарантированно неизменяем |
| Null-элементы | Допускаются | Запрещены, NPE |
| Тип результата | Не гарантируется | Не специфицирован, но неизменяем |
| Добавлено в | Java 8 | Java 10 |

**Когда использовать:** если результат будет только читаться или передаваться в другие компоненты без права изменения — предпочтительнее `toUnmodifiableList()`. Если нужны `null`-элементы или последующая мутация — `toList()`.

---

### Вопрос 14. Как создать параллельный стрим? Какой пул потоков он использует и когда параллельный стрим может ухудшить производительность?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Parallelism — The Java™ Tutorials, docs.oracle.com](https://docs.oracle.com/javase/tutorial/collections/streams/parallelism.html)

Официальная документация описывает два способа создания параллельного стрима:

1. Вызвать метод `Collection.parallelStream()` на коллекции:
```java
double average = roster
    .parallelStream()
    .filter(p -> p.getGender() == Person.Sex.MALE)
    .mapToInt(Person::getAge)
    .average()
    .getAsDouble();
```

2. Вызвать метод `BaseStream.parallel()` на существующем стриме:
```java
stream.parallel()
```

Документация предупреждает: «Параллелизм не обязательно быстрее последовательного выполнения, хотя может быть быстрее при наличии достаточного объёма данных и процессорных ядер». Среди ключевых проблем названы: вмешательство в источник (вызывает `ConcurrentModificationException`), использование lambda с внутренним состоянием (нестабильные результаты), а также то, что при необходимости сохранять порядок следует использовать `forEachOrdered()`, но это снижает эффект параллелизма.

#### Ответ от Claude

**Способы создания параллельного стрима:**

```java
// 1. Из коллекции напрямую
list.parallelStream()

// 2. Из последовательного стрима
stream.parallel()

// 3. Оба метода эквивалентны — parallelStream() это сокращение для stream().parallel()
```

**Используемый пул потоков:**

По умолчанию параллельный стрим использует **`ForkJoinPool.commonPool()`** — общий статический пул JVM, реализованный на базе алгоритма work-stealing. Размер пула по умолчанию равен `Runtime.getRuntime().availableProcessors() - 1`. Этот пул является **общим ресурсом** для всего приложения: его используют все параллельные стримы, а также другие компоненты (например, CompletableFuture). Настроить можно через флаг `-Djava.util.concurrent.ForkJoinPool.common.parallelism=N`.

Для использования **собственного пула** нужно запустить стрим внутри задачи, поданной в кастомный `ForkJoinPool`:
```java
ForkJoinPool customPool = new ForkJoinPool(4);
customPool.submit(() -> list.parallelStream().map(...).collect(...)).get();
```

**Когда параллельный стрим ухудшает производительность:**

1. **Малый объём данных** — накладные расходы на разбивку данных, координацию потоков и агрегацию результатов превышают выигрыш от параллелизма.
2. **I/O-операции и блокирующие вызовы** — `ForkJoinPool.commonPool()` оптимизирован для CPU-задач. Если потоки блокируются на сети, БД или файловой системе, весь общий пул может оказаться занят, лишая ресурсов другие части приложения.
3. **Серверные приложения с высокой нагрузкой** — в веб-сервере, обрабатывающем тысячи запросов, один тяжёлый параллельный стрим может захватить все потоки commonPool, приводя к задержкам в несвязанных запросах.
4. **Stateful операции** — `sorted()`, `distinct()` требуют буферизации всех элементов и синхронизации, нивелируя параллелизм.
5. **Источники с плохой делимостью** — `LinkedList`, `Iterator`-based стримы плохо поддаются разбивке (spliterator с низкой параллелизуемостью).
6. **Конкуренция за commonPool** — несколько одновременных параллельных стримов конкурируют за один пул потоков.

**Правило:** параллельный стрим оправдан для CPU-интенсивных, stateless операций над большими коллекциями (десятки тысяч элементов и более) при наличии нескольких ядер.

---

### Вопрос 15. Что такое stateful и stateless промежуточные операции в Stream? Почему stateful операции проблематичны в параллельных стримах?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [java.util.stream (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html)

Официальная документация Java 8 разделяет промежуточные операции следующим образом:

**Stateless (без состояния)** — операции, которые при обработке нового элемента **не сохраняют состояние** из ранее обработанных элементов. Каждый элемент обрабатывается независимо. Примеры: `filter`, `map`. Могут быть обработаны за один проход как последовательно, так и параллельно, при минимальной буферизации данных.

**Stateful (с состоянием)** — операции, которые **могут использовать состояние** из ранее обработанных элементов при обработке нового элемента. Примеры: `distinct`, `sorted`. Документация поясняет: «Операции с состоянием могут требовать обработки всех входных данных прежде чем выдать результат. Например, нельзя получить результат сортировки стрима, пока не просмотрены все его элементы». При параллельном выполнении конвейер с такими операциями **может потребовать нескольких проходов или значительной буферизации данных**.

#### Ответ от Claude

**Stateless-операции** (без состояния):
- Обрабатывают каждый элемент **независимо** от других.
- Не требуют знания предыдущих или последующих элементов.
- Примеры: `filter()`, `map()`, `flatMap()`, `peek()`, `mapToInt()` и т. д.
- Хорошо масштабируются в параллельном режиме: каждый поток может обрабатывать свой сегмент данных полностью независимо.

**Stateful-операции** (с состоянием):
- Для корректной обработки текущего элемента **необходимо знание других элементов** стрима.
- Примеры: `distinct()`, `sorted()`, `limit()`, `skip()`.
- Для получения правильного результата, как правило, нужно увидеть (или буферизировать) **все элементы**.

**Почему stateful-операции проблематичны в параллельных стримах:**

1. **Необходимость буферизации.** `sorted()` не может выдать ни одного элемента, пока не соберёт и не отсортирует весь входной набор. В параллельном стриме это означает, что каждый сегмент должен быть отсортирован, а затем результаты объединены — двухфазная обработка с накладными расходами.

2. **Необходимость координации и синхронизации.** `distinct()` должен определить глобально уникальные элементы по всем сегментам — требуется общая структура данных с синхронизацией между потоками.

3. **Нарушение порядка.** Параллельный стрим разбивает данные на сегменты и обрабатывает их в произвольном порядке. `skip(N)` и `limit(N)` семантически завязаны на порядок элементов, поэтому требуют дополнительных механизмов упорядочивания, которые снижают эффективность параллелизма.

4. **Недетерминированность при stateful-лямбдах.** Отдельная проблема — когда в stateless-операцию (`filter`, `map`) передаётся lambda, **обращающаяся к изменяемому внешнему состоянию** (например, к счётчику). В параллельном потоке это приводит к гонкам данных и непредсказуемым результатам. Документация рекомендует: избегайте stateful behavioral parameters в операциях над стримами.

**Итого:** stateless-операции в параллельных стримах — безопасны и эффективны. Stateful-операции (`sorted`, `distinct`, `limit`, `skip`) допустимы, но снижают выгоду от параллелизма из-за необходимости буферизации, синхронизации и/или многопроходной обработки.

---

### Вопрос 16. Можно ли использовать стрим повторно после вызова терминальной операции? Что произойдёт при попытке?

**Категория:** Функц. и Stream API · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [«Stream has already been operated upon or closed» Exception in Java — howtodoinjava.com](https://howtodoinjava.com/java/stream/stream-has-already-been-operated-upon-or-closed/)

Стримы Java являются **одноразовыми объектами**. Терминальная операция (такая как `collect()`, `max()`, `min()`) **закрывает стрим после выполнения**. Попытка выполнить ещё одну операцию над закрытым стримом выбрасывает исключение:

```
java.lang.IllegalStateException: stream has already been operated upon or closed
```

Пример ошибки:
```java
Stream<Integer> numberStream = Stream.of(123, 234, 11, 57, 60, -4);
List<Integer> evenNumbers = numberStream.filter(i -> i % 2 == 0).collect(Collectors.toList());
List<Integer> oddNumbers = numberStream.filter(i -> i % 2 == 1).collect(Collectors.toList()); // Ошибка!
```

Решение — использовать `Supplier<Stream<T>>` как фабрику стримов, каждый раз получая новый экземпляр:
```java
Supplier<Stream<Integer>> streamSupplier = () -> Stream.of(123, 234, 11, 57, 60, -4);
List<Integer> evenNumbers = streamSupplier.get().filter(i -> i % 2 == 0).collect(Collectors.toList());
List<Integer> oddNumbers = streamSupplier.get().filter(i -> i % 2 == 1).collect(Collectors.toList());
```

#### Ответ от Claude

**Нет, использовать стрим повторно нельзя.** Это фундаментальное ограничение Java Stream API, задокументированное в спецификации (`java.util.stream` package-info):

> «Элементы стрима посещаются только один раз за время жизни стрима. Как и `Iterator`, для повторного посещения тех же элементов источника необходимо создать новый стрим».

**Что произойдёт при попытке повторного использования:**

При вызове любой операции (промежуточной или терминальной) на уже закрытом стриме будет выброшено:
```
java.lang.IllegalStateException: stream has already been operated upon or closed
```

Это происходит потому, что после выполнения терминальной операции стрим переходит в состояние «закрыт» (`CLOSED`). Реализация проверяет этот флаг при каждой попытке запустить новую операцию.

**Закрывают стрим все терминальные операции:**
`collect()`, `forEach()`, `count()`, `sum()`, `min()`, `max()`, `findFirst()`, `findAny()`, `anyMatch()`, `allMatch()`, `noneMatch()`, `reduce()`, `toArray()` и другие.

**Способы работать с теми же данными повторно:**

1. **Создавать новый стрим каждый раз** из источника данных (коллекции, массива):
```java
List<String> names = List.of("Alice", "Bob", "Charlie");
long count = names.stream().filter(s -> s.length() > 3).count();
List<String> filtered = names.stream().filter(s -> s.length() > 3).collect(Collectors.toList());
```

2. **Использовать `Supplier<Stream<T>>`** как фабрику, если стрим нужно передавать в несколько мест:
```java
Supplier<Stream<String>> supplier = () -> names.stream().filter(s -> s.length() > 3);
long count = supplier.get().count();
List<String> filtered = supplier.get().collect(Collectors.toList());
```

**Важно:** это ограничение — не недостаток, а осознанное проектное решение. Оно позволяет реализациям Stream API выполнять ленивые вычисления, оптимизировать конвейер и не хранить промежуточные результаты. Стрим — это «рецепт обработки», а не контейнер данных.
### Вопрос 17. Что делают операции peek(), sorted() и distinct()? Почему sorted() и distinct() считаются дорогими при обработке больших коллекций?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Stream (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/Stream.html)

**peek()** — промежуточная операция, возвращающая поток, состоящий из тех же элементов исходного потока; при этом для каждого элемента дополнительно выполняется заданное действие по мере того, как элементы потребляются из результирующего потока. Метод существует в первую очередь для поддержки отладки — позволяет наблюдать элементы в процессе их прохождения через конвейер.

**distinct()** — промежуточная операция, возвращающая поток из различных элементов согласно `Object.equals()`. Это **stateful** (с сохранением состояния) операция: при обработке каждого нового элемента она использует состояние из ранее просмотренных элементов. Для упорядоченных потоков порядок стабилен (сохраняется первое вхождение).

**sorted()** — промежуточная операция, возвращающая поток с элементами, отсортированными в естественном порядке (или по переданному `Comparator`). Также является **stateful** операцией.

Почему дорогие: «Stateful-операции могут нуждаться в обработке всего входного потока перед тем, как начнут выдавать результат. Например, невозможно выдать ни одного результата сортировки, пока все элементы потока не будут просмотрены». В параллельных конвейерах это означает необходимость многопроходной обработки или значительной буферизации данных.

#### Ответ от Claude

**peek(action)**

Статeless (без состояния) промежуточная операция. Возвращает поток с теми же элементами, попутно выполняя `action` (типа `Consumer`) для каждого элемента. Предназначена в первую очередь для **отладки** — позволяет «подсмотреть» элементы в середине конвейера, не изменяя их. Важные нюансы:
- Действие может не выполниться вообще, если терминальная операция является short-circuiting (`findFirst`, `limit`).
- Начиная с Java 9, документация предупреждает: не следует полагаться на `peek` в производственном коде для побочных эффектов — реализация может оптимизировать вызовы.

```java
List<String> result = Stream.of("one", "two", "three", "four")
    .filter(e -> e.length() > 3)
    .peek(e -> System.out.println("После filter: " + e))
    .map(String::toUpperCase)
    .peek(e -> System.out.println("После map: " + e))
    .collect(Collectors.toList());
```

**sorted() / sorted(Comparator)**

Stateful промежуточная операция. Возвращает поток с элементами, отсортированными по натуральному порядку (`Comparable`) или по заданному `Comparator`. Для упорядоченных потоков сортировка стабильна.

**distinct()**

Stateful промежуточная операция. Возвращает поток, содержащий только уникальные элементы (сравнение по `equals`/`hashCode`). Для упорядоченных потоков стабильна (сохраняется первое вхождение).

**Почему sorted() и distinct() дороги на больших коллекциях:**

1. **Полная буферизация:** Оба метода — stateful, они обязаны увидеть все элементы перед тем, как отдать первый результат. `sorted` должен собрать весь массив в память и отсортировать его (O(n log n)). `distinct` хранит множество уже встреченных элементов (O(n) памяти).

2. **Потеря ленивости:** Конвейер, состоящий исключительно из stateless-операций (`filter`, `map`), обрабатывается за один проход без промежуточного буфера. Как только в цепочку добавляется `sorted` или `distinct`, ленивость «ломается» в этом месте.

3. **Параллельные потоки — особая проблема.** Для упорядоченных (`ORDERED`) параллельных потоков:
   - `sorted()` требует синхронизации и слияния отсортированных кусков.
   - `distinct()` работает как «полный барьер» (full barrier) — все потоки должны завершить свою часть прежде, чем можно двигаться дальше. Документация Oracle явно называет это «substantial buffering overhead».

**Рекомендации для параллельных потоков:**
```java
// Снять требование упорядоченности — значительно быстрее:
stream.unordered().distinct()
stream.unordered().sorted(comparator)

// Или переключиться на последовательный режим:
stream.sequential().sorted()
```

| Операция  | Тип           | Буферизует | Сложность | Влияние на параллелизм |
|-----------|---------------|------------|-----------|------------------------|
| `peek()`  | Промежуточная (stateless) | Нет | O(1) | Нейтральное |
| `sorted()` | Промежуточная (stateful) | Все элементы | O(n log n) | Дорогое (требует синхронизации) |
| `distinct()` | Промежуточная (stateful) | Все элементы | O(n) | Очень дорогое (full barrier) |

---

### Вопрос 18. Как с помощью Stream API найти все дублирующиеся элементы в списке? Напишите решение.

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java: Finding Duplicate Elements in a Stream — stackabuse.com](https://stackabuse.com/java-finding-duplicate-elements-in-a-stream/)

Три основных подхода:

**1. Set + filter (наиболее эффективный):** Используем `HashSet` для отслеживания уже встреченных элементов. Метод `Set.add()` возвращает `false`, если элемент уже есть, — это и есть признак дубликата:
```java
Set<String> items = new HashSet<>();
stream.filter(n -> !items.add(n))
      .collect(Collectors.toSet())
      .forEach(System.out::println);
```

**2. groupingBy + counting:** Группируем элементы по значению с подсчётом частоты, затем фильтруем те, у которых частота больше 1:
```java
list.stream()
    .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()))
    .entrySet().stream()
    .filter(element -> element.getValue() > 1)
    .collect(Collectors.toList());
```

**3. Collections.frequency():** Для каждого элемента проверяем, встречается ли он более одного раза:
```java
list.stream()
    .filter(i -> Collections.frequency(list, i) > 1)
    .collect(Collectors.toSet());
```

Подход с `Set.add()` является самым быстрым, так как проходит по списку только один раз.

#### Ответ от Claude

Существует несколько подходов, каждый с разной семантикой и производительностью. Важно понимать, что именно нужно: получить **уникальный набор дубликатов** или **сохранить все повторяющиеся вхождения**.

**Подход 1 — Set + filter: самый быстрый, O(n)**

`HashSet.add()` возвращает `false`, если элемент уже присутствует в множестве. Это побочный эффект, который `filter` использует для выявления дубликатов:

```java
public static <T> Set<T> findDuplicates(List<T> list) {
    Set<T> seen = new HashSet<>();
    return list.stream()
               .filter(e -> !seen.add(e))
               .collect(Collectors.toSet());
}

// Пример:
List<Integer> nums = List.of(1, 2, 3, 2, 4, 3, 5);
System.out.println(findDuplicates(nums)); // [2, 3]
```

Внимание: использование изменяемого `seen` внутри лямбды — технически нарушение правила «non-interfering», хотя работает в последовательных потоках. Для параллельного потока нужно заменить на `ConcurrentHashMap.newKeySet()`.

**Подход 2 — groupingBy + counting: дает частоты, O(n)**

Возвращает `Map<T, Long>` с числом вхождений каждого элемента. Удобен, когда нужно знать не только факт дублирования, но и сколько раз:

```java
Map<Integer, Long> frequencies = list.stream()
    .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

// Только дубликаты:
Set<Integer> duplicates = frequencies.entrySet().stream()
    .filter(e -> e.getValue() > 1)
    .map(Map.Entry::getKey)
    .collect(Collectors.toSet());
```

**Подход 3 — Collections.frequency(): самый медленный, O(n²)**

Для каждого из n элементов вызывает `Collections.frequency()`, который делает полный проход по списку. Итоговая сложность O(n²) — не подходит для больших коллекций:

```java
Set<Integer> duplicates = list.stream()
    .filter(e -> Collections.frequency(list, e) > 1)
    .collect(Collectors.toSet());
```

**Сравнительная таблица:**

| Подход | Временная сложность | Получаем частоту | Потокобезопасен |
|--------|---------------------|-----------------|-----------------|
| Set + filter | O(n) | Нет | С `ConcurrentHashMap` |
| groupingBy + counting | O(n) | Да | Да (через collect) |
| Collections.frequency | O(n²) | Нет | Да |

**Рекомендация:** для большинства задач используйте `Set + filter` (скорость) или `groupingBy + counting` (когда нужна частота).

---

### Вопрос 19. Что такое Predicate.and(), Predicate.or() и Predicate.negate()? Как скомпоновать несколько предикатов?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Predicate (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/function/Predicate.html)

`Predicate<T>` — функциональный интерфейс, представляющий предикат (булеву функцию) от одного аргумента. Предоставляет следующие методы композиции:

**and(Predicate other)** — возвращает скомпонованный предикат, представляющий short-circuiting логическое И данного предиката и другого. Если данный предикат равен `false`, второй не вычисляется.

**or(Predicate other)** — возвращает скомпонованный предикат, представляющий short-circuiting логическое ИЛИ. Если данный предикат равен `true`, второй не вычисляется.

**negate()** — возвращает предикат, представляющий логическое отрицание данного предиката.

Дополнительно (Java 11+): статический метод **not(Predicate target)** — возвращает предикат, являющийся отрицанием переданного; удобен для передачи в method reference. Все три метода бросают `NullPointerException`, если другой предикат равен `null`.

#### Ответ от Claude

`Predicate<T>` — функциональный интерфейс из пакета `java.util.function`, чей абстрактный метод — `boolean test(T t)`. Методы `and`, `or`, `negate` являются `default`-методами интерфейса, что позволяет строить сложные логические условия из простых предикатов (паттерн «composition over inheritance»).

**Predicate.and(Predicate<? super T> other)**

Логическое AND с **коротким замыканием** (short-circuit): если `this.test(t)` возвращает `false`, второй предикат не вычисляется вовсе.

```java
Predicate<Integer> isPositive = n -> n > 0;
Predicate<Integer> isEven     = n -> n % 2 == 0;

Predicate<Integer> isPositiveAndEven = isPositive.and(isEven);

isPositiveAndEven.test(4);   // true
isPositiveAndEven.test(-4);  // false (isEven не вычисляется)
isPositiveAndEven.test(3);   // false
```

**Predicate.or(Predicate<? super T> other)**

Логическое OR с **коротким замыканием**: если `this.test(t)` возвращает `true`, второй предикат не вычисляется.

```java
Predicate<String> isEmpty  = String::isEmpty;
Predicate<String> isNull   = s -> s == null;

Predicate<String> isNullOrEmpty = isNull.or(isEmpty);

isNullOrEmpty.test(null);  // true (isEmpty не вычисляется)
isNullOrEmpty.test("");    // true
isNullOrEmpty.test("hi");  // false
```

**Predicate.negate()**

Логическое NOT. Всегда вычисляет исходный предикат (short-circuit неприменимо):

```java
Predicate<String> isBlank    = String::isBlank;
Predicate<String> isNotBlank = isBlank.negate();

isNotBlank.test("hello"); // true
isNotBlank.test("   ");   // false
```

**Predicate.not(Predicate) — статический метод (Java 11+)**

Удобная альтернатива `negate()`, особенно при работе с method reference:

```java
// Без not():
list.stream().filter(s -> !s.isBlank())

// С not():
list.stream().filter(Predicate.not(String::isBlank))
```

**Композиция нескольких предикатов**

Методы можно цепочкой комбинировать для любой сложности:

```java
Predicate<String> startsWithA = s -> s.startsWith("A");
Predicate<String> longerThan3 = s -> s.length() > 3;
Predicate<String> noDigits    = s -> s.chars().noneMatch(Character::isDigit);

Predicate<String> combined = startsWithA
    .and(longerThan3)
    .and(noDigits);

List<String> result = words.stream()
    .filter(combined)
    .collect(Collectors.toList());
```

Также удобно агрегировать динамический список предикатов через `reduce`:

```java
List<Predicate<Integer>> predicates = List.of(
    n -> n > 0,
    n -> n < 100,
    n -> n % 2 == 0
);

Predicate<Integer> combined = predicates.stream()
    .reduce(x -> true, Predicate::and); // identity: всегда true

List<Integer> result = numbers.stream()
    .filter(combined)
    .collect(Collectors.toList());
```

**Таблица short-circuit поведения:**

| Метод | Short-circuit когда | Второй предикат пропускается |
|-------|--------------------|-----------------------------|
| `and(other)` | первый = `false` | Да |
| `or(other)` | первый = `true` | Да |
| `negate()` | — | N/A (один предикат) |
| `not(target)` | — | N/A (обёртка над negate) |

---

### Вопрос 20. В чём разница между findFirst() и findAny()? Как их поведение меняется в параллельном стриме?

**Категория:** Функц. и Stream API · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Stream (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/Stream.html)

**findFirst()** — возвращает `Optional`, описывающий первый элемент потока, или пустой `Optional`, если поток пуст. Если поток не имеет порядка встречаемости (encounter order), может быть возвращён любой элемент.

**findAny()** — возвращает `Optional`, описывающий некий элемент потока, или пустой `Optional`, если поток пуст. Поведение операции явно **недетерминировано**: она свободна в выборе любого элемента потока. «Это сделано для обеспечения максимальной производительности в параллельных операциях; цена — то, что несколько вызовов на одном и том же источнике могут не вернуть одинаковый результат. (Если желателен стабильный результат, используйте вместо неё `findFirst()`.)»

Оба метода являются **short-circuiting terminal operations** и бросают `NullPointerException`, если выбранный элемент равен `null`.

#### Ответ от Claude

Оба метода — **терминальные short-circuiting операции**, возвращающие `Optional<T>`. Разница проявляется в семантике выбора элемента и, как следствие, в производительности при параллельном выполнении.

**findFirst()**

Всегда возвращает **первый** элемент в порядке встречаемости (encounter order). Детерминирован и стабилен:

```java
Optional<String> first = Stream.of("c", "b", "a")
    .filter(s -> s.compareTo("b") >= 0)
    .findFirst();

first.get(); // "c" — всегда, в любом запуске
```

**findAny()**

Поведение явно **недетерминировано** — API-контракт позволяет вернуть любой подходящий элемент. В последовательных потоках на практике обычно возвращает первый элемент (как `findFirst`), но это деталь реализации, на которую нельзя полагаться:

```java
Optional<String> any = Stream.of("c", "b", "a")
    .filter(s -> s.compareTo("b") >= 0)
    .findAny();

any.get(); // "c" или "b" или "a" — не гарантировано
```

**Поведение в параллельном стриме — ключевое различие**

`findFirst()` в параллельном потоке **вынужден сохранять encounter order**: каждый поток-обработчик находит свой «первый» элемент в своём сегменте, но финальный результат должен быть именно первым по исходному порядку. Это требует координации/синхронизации между потоками — существенные накладные расходы.

`findAny()` в параллельном потоке **не обязан соблюдать порядок**: первый поток-обработчик, нашедший подходящий элемент, немедленно его возвращает, не дожидаясь остальных. Это делает `findAny` значительно быстрее в параллельном режиме.

```java
List<Integer> numbers = IntStream.rangeClosed(1, 1_000_000)
    .boxed()
    .collect(Collectors.toList());

// Медленнее — координация для сохранения порядка
Optional<Integer> first = numbers.parallelStream()
    .filter(n -> n % 2 == 0)
    .findFirst();
// Гарантировано: 2

// Быстрее — любой поток возвращает первый найденный
Optional<Integer> any = numbers.parallelStream()
    .filter(n -> n % 2 == 0)
    .findAny();
// Может быть: 2, 100, 42578 — непредсказуемо
```

**Сводная таблица:**

| Аспект | `findFirst()` | `findAny()` |
|--------|--------------|------------|
| Результат | Первый по encounter order | Любой элемент |
| Детерминизм | Всегда стабилен | Нестабилен (особенно в параллельных) |
| Последовательный поток | Первый элемент | Практически первый (не гарантировано) |
| Параллельный поток | Требует координации — медленнее | Без координации — быстрее |
| Когда использовать | Нужен конкретный первый элемент | Нужен любой элемент, важна скорость |

**Практическое правило:** если порядок важен — `findFirst()`; если важна производительность в параллельном стриме и порядок безразличен — `findAny()`.

---
