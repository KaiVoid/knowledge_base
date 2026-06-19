# Generics (обобщения)

> **Уровень:** Middle
> **Связанные вопросы:** [Вопросы по generics →](../../../interview-questions/core-java/generics-01.md)
> **Связанные области:** [[01-core-java-syntax-oop]], [[03-collections]]

## Что это и зачем

Обобщения дают типобезопасность на этапе компиляции и избавляют от явных приведений типов.
Понимание generics необходимо для корректной работы с коллекциями, проектирования переиспользуемых
API и чтения сложных сигнатур. Отдельно важна тема стирания типов (type erasure), объясняющая
ограничения generics во время выполнения.

Generics были введены в Java 5 (JSR 14). До этого коллекции хранили `Object`, и любое получение
элемента требовало явного приведения типа — ошибки обнаруживались лишь в рантайме. С generics
компилятор проверяет корректность типов сразу, до запуска программы.

Три ключевых выгоды от generics ([Why Use Generics?](https://docs.oracle.com/javase/tutorial/java/generics/why.html)):
1. **Сильная проверка типов на этапе компиляции** — ошибки типов становятся compile-time, а не runtime.
2. **Устранение явных приведений** — код без generics требует `(String) list.get(0)`, с generics приведение не нужно.
3. **Переиспользуемые алгоритмы** — один метод или класс корректно работает с разными типами.

---

## Ключевые подтемы

### Обобщённые классы и интерфейсы

Обобщённый класс объявляется с секцией параметров типа в угловых скобках сразу после имени класса:

```java
class Box<T> {
    private T value;

    public void set(T value) { this.value = value; }
    public T get() { return value; }
}
```

Интерфейсы параметризуются точно так же:

```java
public interface Pair<K, V> {
    K getKey();
    V getValue();
}
```

Классы могут иметь несколько параметров типа:

```java
public class OrderedPair<K, V> implements Pair<K, V> {
    private final K key;
    private final V value;

    public OrderedPair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    @Override public K getKey()   { return key; }
    @Override public V getValue() { return value; }
}

// Использование:
Pair<String, Integer> p = new OrderedPair<>("age", 30);
```

Параметром типа может быть другой параметризованный тип:

```java
OrderedPair<String, Box<Integer>> nested = new OrderedPair<>("count", new Box<>());
```

Документация: [Generic Types](https://docs.oracle.com/javase/tutorial/java/generics/types.html)

---

### Соглашения об именовании параметров типа

По договорённости параметры типа именуются **одной заглавной буквой**. Это отличает их от обычных
имён классов и интерфейсов:

| Буква | Назначение |
|-------|-----------|
| `T`   | Type — произвольный тип |
| `E`   | Element — элемент коллекции (используется в Java Collections Framework) |
| `K`   | Key — ключ в словаре |
| `V`   | Value — значение в словаре |
| `N`   | Number — числовой тип |
| `S`, `U`, `V` | 2-й, 3-й, 4-й тип в многопараметрических объявлениях |

---

### Обобщённые методы

Обобщённый метод вводит свои собственные параметры типа. Их область видимости ограничена
методом. Секция параметров типа размещается **перед возвращаемым типом**:

```java
public static <K, V> boolean compare(Pair<K, V> p1, Pair<K, V> p2) {
    return p1.getKey().equals(p2.getKey())
        && p1.getValue().equals(p2.getValue());
}
```

Вызов с явным указанием типа и с выводом типов (предпочтительно):

```java
// Явное указание:
boolean r1 = Util.<Integer, String>compare(p1, p2);

// Вывод типов компилятором:
boolean r2 = Util.compare(p1, p2);
```

Правило: обобщённый метод предпочтительнее обобщённого класса, если только один метод
нуждается в типовой гибкости, а не весь класс.

Документация: [Generic Methods](https://docs.oracle.com/javase/tutorial/java/generics/methods.html)

---

### Ограниченные параметры типа (Bounded Type Parameters)

`extends` в объявлении параметра типа означает «является подтипом» — работает и для классов,
и для интерфейсов:

```java
// Только Number и его подклассы (Integer, Double, Long, ...)
public <T extends Number> double sum(List<T> list) {
    double s = 0;
    for (T t : list) s += t.doubleValue(); // метод Number доступен
    return s;
}
```

**Множественные ограничения** разделяются `&`. Если среди границ есть класс, он должен стоять первым:

```java
// Правильно: класс первым, затем интерфейсы
class Processor<T extends Serializable & Comparable<T> & Cloneable> { }

// Ошибка компиляции: интерфейс перед классом, если класс присутствует
```

Множественные ограничения позволяют вызывать методы всех перечисленных типов внутри метода/класса.

Документация: [Bounded Type Parameters](https://docs.oracle.com/javase/tutorial/java/generics/bounded.html)

---

### Подтипизация с generics и почему `List<Integer>` не является `List<Number>`

Это одно из самых важных и неочевидных свойств generics. Хотя `Integer` является подтипом
`Number`, **`List<Integer>` не является подтипом `List<Number>`**. Между ними нет отношения
наследования — их общий предок только `Object`.

```java
// Ошибка компиляции:
List<Number> nums = new ArrayList<Integer>(); // incompatible types

// Почему это правильно? Иначе был бы возможен:
List<Integer> ints = new ArrayList<>();
List<Number> nums2 = ints;          // если бы разрешалось
nums2.add(3.14);                    // Double в список Integer!
```

Отношение подтипизации сохраняется, когда параметры типа совпадают:

```java
ArrayList<String>   -- подтип --> List<String>   -- подтип --> Collection<String>
```

Wildcards позволяют создать «ковариантное» отношение:

```java
List<? extends Number> covariant = new ArrayList<Integer>(); // OK
```

Документация: [Generics, Inheritance, and Subtypes](https://docs.oracle.com/javase/tutorial/java/generics/inheritance.html)

---

### Wildcards (подстановочные символы)

Wildcard `?` обозначает неизвестный тип. Используется в позициях параметров метода, полей
и локальных переменных (но не в аргументах при создании экземпляра).

#### Upper Bounded Wildcard (`? extends T`)

Принимает тип `T` и любой его подтип. Используется для **чтения** (producer):

```java
public static double sumOfList(List<? extends Number> list) {
    double s = 0.0;
    for (Number n : list) s += n.doubleValue();
    return s;
}

sumOfList(List.of(1, 2, 3));       // List<Integer> — OK
sumOfList(List.of(1.5, 2.5));      // List<Double>  — OK
```

Нельзя добавлять элементы в такой список (кроме `null`), поскольку компилятор не знает точный тип.

Документация: [Upper Bounded Wildcards](https://docs.oracle.com/javase/tutorial/java/generics/upperBounded.html)

#### Lower Bounded Wildcard (`? super T`)

Принимает тип `T` и любой его супертип. Используется для **записи** (consumer):

```java
public static void addNumbers(List<? super Integer> list) {
    for (int i = 1; i <= 10; i++) list.add(i);
}

addNumbers(new ArrayList<Integer>()); // OK
addNumbers(new ArrayList<Number>());  // OK
addNumbers(new ArrayList<Object>());  // OK
```

Документация: [Lower Bounded Wildcards](https://docs.oracle.com/javase/tutorial/java/generics/lowerBounded.html)

#### Unbounded Wildcard (`?`)

Используется, когда функциональность не зависит от параметра типа либо работает только
через методы `Object`:

```java
public static void printList(List<?> list) {
    for (Object elem : list) System.out.print(elem + " ");
}
```

---

### Принцип PECS (Producer Extends, Consumer Super)

Правило Джошуа Блоха (Effective Java, Item 31), подтверждённое официальной документацией Oracle:

> **Producer Extends, Consumer Super (PECS)**

| Роль параметра | Wildcard | Пример |
|----------------|----------|--------|
| Производитель (из него читают) | `? extends T` | `src` в `copy(src, dest)` |
| Потребитель (в него пишут) | `? super T` | `dest` в `copy(src, dest)` |
| Только методы Object | `?` | `printList(List<?>)` |
| Одновременно читают и пишут | без wildcard | `List<T>` |

```java
// Копирует из src (producer) в dest (consumer)
public static <T> void copy(List<? extends T> src, List<? super T> dest) {
    for (T elem : src) dest.add(elem);
}
```

Не следует использовать wildcards в возвращаемом типе метода — это усложняет API для вызывающей стороны.

Документация: [Guidelines for Wildcard Use](https://docs.oracle.com/javase/tutorial/java/generics/wildcardGuidelines.html)

---

### Вывод типов (Type Inference)

Компилятор Java определяет аргументы типа автоматически, анализируя контекст вызова, аргументы
и целевой тип присваивания.

**Оператор diamond `<>`** (Java 7+) — позволяет не повторять аргументы типа при создании экземпляра:

```java
// Без diamond (многословно):
Map<String, List<String>> map = new HashMap<String, List<String>>();

// С diamond (компилятор выводит аргументы):
Map<String, List<String>> map = new HashMap<>();
```

Если diamond опустить полностью (`new HashMap()`), компилятор выдаст предупреждение
`unchecked conversion`.

**Target type inference (Java 8+)** — компилятор выводит тип из целевого контекста:

```java
// Java 7: нужен явный type witness
processStringList(Collections.<String>emptyList());

// Java 8+: компилятор сам выводит T=String
processStringList(Collections.emptyList());
```

Документация: [Type Inference](https://docs.oracle.com/javase/tutorial/java/generics/genTypeInference.html)

---

### Raw Types (сырые типы)

Raw type — это использование обобщённого класса без параметра типа. Существует для обратной
совместимости с кодом до Java 5:

```java
// Raw type (не рекомендуется):
Box rawBox = new Box();
rawBox.set("anything"); // unchecked warning

// Правильно:
Box<String> typedBox = new Box<>();
```

Присваивание параметризованного типа raw type разрешено, но обратное присваивание
генерирует предупреждение `unchecked conversion`:

```java
Box<String> stringBox = new Box<>();
Box rawBox = stringBox;          // OK (backward compat)
Box<Integer> intBox = rawBox;    // warning: unchecked conversion
```

Просмотр всех unchecked-предупреждений: `javac -Xlint:unchecked`. Подавление в коде: `@SuppressWarnings("unchecked")`.

**Raw types следует избегать в новом коде** — они обходят все проверки generics.

Документация: [Raw Types](https://docs.oracle.com/javase/tutorial/java/generics/rawTypes.html)

---

### Стирание типов (Type Erasure)

Generics в Java реализованы через **стирание типов**: во время компиляции параметры типа
заменяются их ограничениями (или `Object` для неограниченных), вставляются необходимые
приведения типов, и генерируется обычный байткод без параметризованных типов.
Никаких новых классов при этом не создаётся — нет накладных расходов в рантайме.

Компилятор выполняет три действия:

1. **Замена параметров типа**: `T` без ограничений → `Object`; `T extends Number` → `Number`.
2. **Вставка приведений**: при получении элементов из generic-коллекции компилятор добавляет
   соответствующий cast.
3. **Генерация bridge-методов**: при наследовании generic-класса компилятор может создавать
   синтетические методы-мосты для корректной работы полиморфизма.

```java
// Исходный код:
public class Box<T> {
    private T value;
    public T get() { return value; }
}

// После стирания (в байткоде):
public class Box {
    private Object value;
    public Object get() { return value; }
}
```

**Non-reifiable types** — типы, информация о которых недоступна в рантайме. `List<String>`
является non-reifiable: в рантайме это просто `List`. Reifiable — только raw types, unbounded
wildcard types (`List<?>`) и примитивы.

Документация: [Type Erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)

---

### Ограничения generics

Все ограничения являются следствием стирания типов или требований JVM:

| Ограничение | Пример ошибки | Причина / Обходной путь |
|-------------|---------------|-------------------------|
| Нельзя использовать примитивы как аргумент типа | `List<int>` | Нет boxing в байткоде; используйте `List<Integer>` |
| Нельзя создавать экземпляры параметра типа | `new T()` | Тип неизвестен в рантайме; используйте `Class<T>` + reflection |
| Нельзя объявлять статические поля типа-параметра | `static T field` | Одно поле на класс, тип неоднозначен |
| Нельзя применять `instanceof` к параметризованным типам | `obj instanceof List<String>` | Тип стёрт; допустимо `obj instanceof List<?>` |
| Нельзя создавать массивы параметризованных типов | `new List<String>[2]` | Опасная несовместимость с проверкой элементов массива |
| Нельзя создавать, ловить или бросать объекты параметризованного Throwable | `class E<T> extends Exception` | Запрещено компилятором |
| Нельзя перегружать методы с одинаковой сигнатурой после стирания | два метода `print(Set<String>)` и `print(Set<Integer>)` | После стирания обе сигнатуры → `print(Set)` |

```java
// Нельзя: создание массива параметризованного типа
List<String>[] arr = new List<String>[10]; // compile-time error

// Можно: создание через обходной путь с приведением (с предупреждением)
@SuppressWarnings("unchecked")
List<String>[] arr2 = (List<String>[]) new List[10];

// Нельзя: instanceof с параметризованным типом
if (obj instanceof List<String>) { } // compile-time error

// Можно: с unbounded wildcard
if (obj instanceof List<?>) { } // OK
```

Документация: [Restrictions on Generics](https://docs.oracle.com/javase/tutorial/java/generics/restrictions.html)

---

## Достоверные источники

1. **[The Java Tutorials — Generics (Oracle)](https://docs.oracle.com/javase/tutorial/java/generics/index.html)** —
   официальный учебник Oracle по generics; охватывает все темы от базовых типов до стирания
   и ограничений. Первичный авторитетный источник.

2. **[Why Use Generics? (Oracle)](https://docs.oracle.com/javase/tutorial/java/generics/why.html)** —
   официальная страница с обоснованием введения generics и тремя ключевыми преимуществами.

3. **[Restrictions on Generics (Oracle)](https://docs.oracle.com/javase/tutorial/java/generics/restrictions.html)** —
   официальный список всех ограничений generics с примерами кода.

4. **[Wildcards Guidelines (Oracle)](https://docs.oracle.com/javase/tutorial/java/generics/wildcardGuidelines.html)** —
   официальные рекомендации по применению wildcards (принцип PECS).

5. **[Baeldung — The Basics of Java Generics](https://www.baeldung.com/java-generics)** —
   авторитетный ресурс с практическими примерами; статьи проходят техническое рецензирование.

6. **Книга «Effective Java» 3-е изд. (Joshua Bloch), Items 26–33** —
   признанный стандарт best practices; Item 31 вводит принцип PECS,
   Items 26–28 — рекомендации по raw types и параметризованным типам.
