# Java — Advanced (HH)

### Вопрос 1. Что выведет программа?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
public class Main {
    public static void foo(Integer i) {
        System.out.println("foo(Integer)");
    }
    public static void foo(short i) {
        System.out.println("foo(short)");
    }
    public static void foo(long i) {
        System.out.println("foo(long)");
    }
    public static void foo(Object i) {
        System.out.println("foo(object)");
    }
    public static void foo(int... i) {
        System.out.println("foo(int...)");
    }
    public static void main(String[] args) {
        foo(10);
    }
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** foo(long)

#### Ответ от Claude

Литерал `10` имеет тип `int`. При выборе перегрузки Java применяет правила приоритета из JLS §15.12.2 в три фазы:

1. **Первая фаза** — только расширяющие преобразования примитивов (widening), без боксинга и varargs. Метод `foo(long)` доступен через расширение `int → long`. Метод `foo(short)` недоступен: `int` не сужается до `short` автоматически. Метод `foo(int...)` — varargs, не рассматривается в первой фазе.
2. Поскольку в первой фазе найдено единственное подходящее расширение (`foo(long)`), оно выбирается без перехода к следующим фазам.

`foo(Integer)` требовал бы боксинга (вторая фаза), а `foo(int...)` — varargs (третья фаза); оба имеют более низкий приоритет, чем расширение примитива.

Источник: [JLS §15.12.2 — Compile-Time Step 2: Determine Method Signature](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.12.2)

---

### Вопрос 2. Что будет выведено при исполнении данного кода?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
public class Main {
    static boolean foo(char a) {
        System.out.print(a);
        return true;
    }
    public static void main(String[] args) {
        int i = 0;
        for (foo('A'); foo('B') && (i < 2); foo('C')) {
            i++;
            foo('D');
        }
    }
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** ABDCBDCB

#### Ответ от Claude

Пошаговый разбор цикла `for (init; condition; update)`:

| Шаг | Действие | Вывод | `i` |
|-----|----------|-------|-----|
| init | `foo('A')` | A | 0 |
| cond | `foo('B')` → true, `0 < 2` → true | AB | 0 |
| body | `i++`, `foo('D')` | ABD | 1 |
| update | `foo('C')` | ABDC | 1 |
| cond | `foo('B')` → true, `1 < 2` → true | ABDCB | 1 |
| body | `i++`, `foo('D')` | ABDCBD | 2 |
| update | `foo('C')` | ABDCBDC | 2 |
| cond | `foo('B')` → true, `2 < 2` → **false** | ABDCBDCB | 2 |

Итог: `ABDCBDCB`. Условие вычисляется через `&&` (короткое замыкание): `foo('B')` всегда вызывается, но `(i < 2)` проверяется только если `foo('B')` вернул true.

Источник: [JLS §14.14.1 — The basic for Statement](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.14.1)

---

### Вопрос 3. Каким будет результат выполнения данного кода?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
Integer a = 100;
Integer b = 100;
Integer c = 200;
Integer d = 200;
Integer e = Integer.valueOf(100);
Integer f = Integer.valueOf(200);
System.out.println(a == b);
System.out.println(c == d);
System.out.println(e == a);
System.out.println(f == c);
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** true false true false

#### Ответ от Claude

`Integer.valueOf(int)` кэширует объекты для значений от −128 до 127 (включительно). Боксинг (`Integer a = 100`) использует тот же `Integer.valueOf` под капотом.

- `a == b`: оба 100 — из кэша, один и тот же объект → `true`
- `c == d`: оба 200 — вне диапазона кэша, разные объекты → `false`
- `e == a`: `Integer.valueOf(100)` возвращает кэшированный объект, тот же, что `a` → `true`
- `f == c`: `Integer.valueOf(200)` — новый объект, отличный от `c` → `false`

Источники: [Java SE 21 API — Integer.valueOf(int)](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Integer.html#valueOf(int)); [JLS §5.1.7 — Boxing Conversion](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html#jls-5.1.7)

---

### Вопрос 4. Каков результат работы этого кода?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
public class SomeClass {
    static int i = 1;
}

public class ExceptionTest {
    public static void main(String[] args) {
        System.out.println(foo());
    }

    static int foo() {
        try {
            SomeClass someClass = null;
            return someClass.i;
        } catch (Exception e) {
            return 2;
        } catch (Throwable e) {
            return 3;
        } finally {
            return 4;
        }
    }
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** 4

#### Ответ от Claude

Ключевой момент: `someClass.i` — обращение к **статическому** полю через переменную-ссылку. В Java обращение к статическому полю через null-ссылку **не бросает `NullPointerException`**: компилятор переписывает это как `SomeClass.i`, не разыменовывая ссылку. Таким образом, `try`-блок возвращает `1` без исключения.

Однако блок `finally` всегда выполняется и **перекрывает** любой `return` из `try` или `catch`. Если `finally` содержит собственный `return`, именно он становится итоговым результатом метода.

Итог: метод `foo()` возвращает `4`.

Источник: [JLS §14.20.2 — Execution of try-finally and try-catch-finally](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.20.2)

---

### Вопрос 5. У вас есть 10 потоков, одновременно обращающихся к очереди задач на основе `BlockingQueue`. Нужно гарантировать, что не более 5 потоков одновременно обрабатывают задачи. Какой способ НЕ подходит?

**Категория:** Java (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Использовать `CountDownLatch` с начальным значением 5 и каждый раз перед получением задачи из очереди вызывать метод `await()` у `CountDownLatch`. Когда поток заканчивает обработку задачи, он вызывает `countDown()`
- Использовать `ExecutorService` с фиксированным размером пула потоков, равным 5
- Использовать `ReentrantLock` с проверкой счётчика внутри блокировки
- Создать класс-посредник, запускающий обработку только для 5 потоков одновременно
- Использовать `Semaphore` с начальным значением 5, вызывая `acquire()` перед получением задачи и `release()` после обработки

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Использовать `CountDownLatch` с начальным значением 5 и вызывать `await()` / `countDown()`

#### Ответ от Claude

`CountDownLatch` предназначен для одноразовой синхронизации: после того как счётчик достигает нуля, `await()` перестаёт блокировать навсегда — защёлку нельзя сбросить. Сценарий из вопроса требует **повторно используемого** механизма ограничения параллелизма, поэтому `CountDownLatch` не подходит.

Правильный инструмент для такой задачи — `Semaphore(5)`: он позволяет ограничить количество одновременно работающих потоков и многократно переиспользуется (`acquire()` / `release()`).

Источники: [Java SE 21 API — CountDownLatch](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/CountDownLatch.html); [Java SE 21 API — Semaphore](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/Semaphore.html)

---

### Вопрос 6. Какая структура данных из перечисленных НЕ является lock-free?

**Категория:** Java (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** AtomicInteger

#### Ответ от Claude

⚠️ HH-источник отмечает `AtomicInteger` как «не lock-free», однако это неверно. `AtomicInteger` является **lock-free** структурой: внутри она использует операцию CAS (Compare-And-Swap) — аппаратно-атомарную инструкцию, которая не требует блокировок (мьютексов). Все классы из пакета `java.util.concurrent.atomic` построены на CAS и являются lock-free.

Примечание: в исходном квизе другие варианты ответа не сохранились (возможно, утеряны при передаче). Среди типичных вариантов для подобного вопроса не-lock-free структурами являются `Vector`, `Hashtable`, `Stack`, `StringBuffer` — они используют `synchronized`. Среди всего, что обычно предлагается в таких вопросах, `AtomicInteger` выделяется как наиболее очевидно lock-free.

Вероятно, правильным ответом в исходном тесте был один из синхронизированных классов (`Vector` или `Hashtable`), а не `AtomicInteger`.

Источники: [Java SE 21 API — AtomicInteger](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html); [Baeldung — Introduction to Lock-Free Data Structures](https://www.baeldung.com/lock-free-programming)

---

### Вопрос 7. Что из перечисленных функциональных ограничений синхронизации в Java является ЛОЖЬЮ?

**Категория:** Java (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Volatile-переменная гарантирует атомарность последовательности читать-модифицировать-читать

#### Ответ от Claude

Это высказывание является ложью, и HH верно его отмечает. `volatile` даёт два вида гарантий:

1. **Видимость**: запись в `volatile`-переменную немедленно видна всем потокам.
2. **Запрет переупорядочивания** (happens-before): запись happens-before любое последующее чтение той же переменной.

Однако `volatile` **не обеспечивает атомарность составных операций**. Например, `x++` (read-modify-write: прочитать → прибавить 1 → записать) — не атомарна даже для `volatile`-переменной: два потока могут прочитать одно и то же значение одновременно, что приведёт к потере одного инкремента. Для таких операций нужен `AtomicInteger` или `synchronized`.

Источники: [Java SE 21 API — Package java.util.concurrent.atomic](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/package-summary.html); [JLS §17.4 — Memory Model](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4)

---

### Вопрос 8. Какие структуры данных требуют, чтобы данные реализовывали интерфейс `Comparable`?

**Категория:** Java (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** TreeMap

#### Ответ от Claude

`TreeMap` хранит ключи в отсортированном порядке. По умолчанию сортировка основана на естественном порядке ключей, то есть ключи должны реализовывать `Comparable<K>`. Если ключи не реализуют `Comparable` и не передан `Comparator`, при первой попытке вставки будет выброшен `ClassCastException`.

Альтернатива: передать `Comparator` в конструктор `TreeMap` — тогда `Comparable` не обязателен.

Аналогично устроен `TreeSet` (требует `Comparable` у элементов или принимает `Comparator`).

Источники: [Java SE 21 API — TreeMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/TreeMap.html); [Java SE 21 API — Comparable](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Comparable.html)

---

### Вопрос 9. Может ли цикличная ссылка между объектами стать причиной утечки памяти при использовании ParallelGC?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
class Node {
    private Node edge = null;
    public Node getEdge() {
        return edge;
    }
    public void setEdge(Node edge) {
        this.edge = edge;
    }
}
public void createAndDelete() {
    final var node1 = new Node();
    final var node2 = new Node();
    node1.setEdge(node2);
    node2.setEdge(node1);
}
```

**Варианты ответа:**
- Да. ParallelGC не умеет работать с циклическими ссылками, поэтому каждый вызов createAndDelete() увеличивает количество неуничтожаемых объектов.
- Нет. Данные объекты не аллоцируются на куче при такой логике и тем самым не вызывают утечку.
- Да. Так как у объектов с циклическими ссылками надо вызывать метод finalize() чтобы он очистился. Иначе GC не может их удалить.
- Да. Из-за цикличности ссылок объекты не могут быть перемещены из молодого поколения в старое

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Нет. Данные объекты не аллоцируются на куче при такой логике и тем самым не вызывают утечку.

#### Ответ от Claude

⚠️ HH-источник отмечает правильным вариант «объекты не аллоцируются на куче», однако обоснование неверно. Объекты `new Node()` **всегда аллоцируются на куче** (heap). Правильный ответ — «утечки нет», но по другой причине:

Java GC (включая ParallelGC) использует **трассирующую сборку мусора (tracing GC / reachability analysis)**, а не подсчёт ссылок. После завершения метода `createAndDelete()` локальные переменные `node1` и `node2` выходят из области видимости и больше не достижимы от GC-корней (GC roots: стек, статические поля, и т.д.). Поскольку оба объекта недостижимы, GC их соберёт — вне зависимости от того, что они ссылаются друг на друга. Циклические ссылки — проблема только для GC на основе подсчёта ссылок (например, CPython), но не для Java.

Итог: утечки памяти нет, но объяснение HH некорректно.

Источники: [Oracle — Java Garbage Collection Basics](https://www.oracle.com/webfolder/technetwork/tutorials/obe/java/gc01/index.html); [Baeldung — Understanding Memory Leaks in Java](https://www.baeldung.com/java-memory-leaks)

---

### Вопрос 10. Какой способ итерирования по `ArrayList` приведёт к `ConcurrentModificationException`, если во время итерирования происходит модификация коллекции?

**Категория:** Java (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Итератор и метод remove()
- ListIterator и метод remove()
- Цикл for с доступом по индексу
- Цикл for-each
- Стримы и метод forEach()

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Цикл for-each

#### Ответ от Claude

Цикл `for-each` над `ArrayList` компилируется в вызов `iterator()`, а затем последовательные вызовы `hasNext()` / `next()`. Внутри итератора `ArrayList` хранится `modCount` — счётчик структурных изменений коллекции. При каждом вызове `next()` итератор сравнивает текущий `modCount` с ожидаемым (`expectedModCount`). Если коллекция была структурно изменена снаружи (добавлен или удалён элемент), счётчики расходятся и выбрасывается `ConcurrentModificationException`.

`iterator.remove()` и `ListIterator.remove()` обновляют `expectedModCount` синхронно — удаление через сам итератор безопасно. Цикл `for` по индексу не использует итератор и не проверяет `modCount`, поэтому `ConcurrentModificationException` не бросает. `Stream.forEach()` для `ArrayList` работает через `Spliterator`, который также проверяет `modCount` и тоже может бросить `ConcurrentModificationException` при структурной модификации; однако это поведение специфично для реализации, тогда как механизм `Iterator.next()` → `checkForComodification()` → `ConcurrentModificationException` описан в контракте `Iterator` явно. Ответ HH — `for-each` — корректен: именно этот способ гарантированно бросает CME при структурной модификации коллекции во время итерирования.

Источники: [Java SE 17 API — ConcurrentModificationException](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ConcurrentModificationException.html); [Java SE 21 API — ArrayList](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayList.html)

---

### Вопрос 11. Какой вариант инициализации переменной приведёт к ошибке компиляции?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
class Box<T> {
    T value;
    public Box(T value) {
        this.value = value;
    }
}

public static void main(String[] args) {
    Box<? super String> b1 = new Box<>(123);
    Box<? extends String> b2 = new Box<>("123");
    Box<? extends Number> b3 = new Box<>(123);
    Box<? super Number> b4 = new Box<>(123L);
}
```

**Варианты ответа:**
- b1
- b2
- b3
- b4
- Никакой из перечисленных

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Никакой из перечисленных

#### Ответ от Claude

Вопрос касается вывода типов компилятором Java при использовании оператора diamond `<>` совместно с wildcards. Все четыре строки компилируются без ошибок.

Проверено компиляцией: `javac 25.0.2` компилирует все четыре строки без ошибок. Ответ HH («ни один не приведёт к ошибке компиляции») верен.

При использовании оператора diamond `<>` компилятор определяет тип через **poly expression type inference** (JLS §18, §15.9): он выводит аргумент типа T, при котором созданный объект совместим с целевым типом переменной.

- `b1 = new Box<>(123)` → целевой тип `Box<? super String>`; компилятор выводит `T = Object` (единственный тип, совместимый с wildcard `? super String` и допускающий `Integer` в качестве значения); компилируется.
- `b2 = new Box<>("123")` → целевой тип `Box<? extends String>`; выводится `T = String`; компилируется.
- `b3 = new Box<>(123)` → целевой тип `Box<? extends Number>`; выводится `T = Integer` (Integer extends Number); компилируется.
- `b4 = new Box<>(123L)` → целевой тип `Box<? super Number>`; выводится `T = Object`; `Long` совместим через Object; компилируется.

Если бы тип указывался явно (например, `new Box<Integer>(123)` для `b1`), то `Box<Integer>` несовместим с `Box<? super String>` — была бы ошибка компиляции. Diamond-инференс позволяет обойти это, выводя совместимый тип автоматически.

Источники: [JLS §18 — Type Inference](https://docs.oracle.com/javase/specs/jls/se17/html/jls-18.html); [JLS §15.9 — Class Instance Creation Expressions](https://docs.oracle.com/javase/specs/jls/se17/html/jls-15.html#jls-15.9)

---

### Вопрос 12. Что выведет код?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
interface A {
    default void method() {
        System.out.println("A");
    }
}

interface B {
    default void method() {
        System.out.println("B");
    }
}

class C implements A, B {
}

public class Main {
    public static void main(String[] args) {
        new C().method();
    }
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Ошибка компиляции

#### Ответ от Claude

Класс `C` реализует оба интерфейса `A` и `B`, у каждого из которых есть `default`-метод `method()` с одинаковой сигнатурой. Согласно JLS §9.4.1.3, если класс наследует несколько `default`-методов с одинаковой сигнатурой и ни один из них не является более конкретным (более специфичным) переопределением, класс обязан явно переопределить этот метод, иначе компиляция завершится ошибкой:

```
error: class C inherits unrelated defaults for method() from types A and B
```

Это сделано намеренно: Java не выбирает один из методов произвольно, чтобы избежать непредсказуемого поведения (аналог «проблемы ромба»).

Источник: [JLS §9.4.1.3 — Inheriting Methods with Override-Equivalent Signatures](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html#jls-9.4.1.3)

---

### Вопрос 13. Что выведет код?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
import java.util.*;
import java.util.stream.*;

public class Test {
    public static void main(String[] args) {
        List<String> list = Arrays.asList("one", "two", "three");
        list.stream()
            .filter(s -> s.length() > 3)
            .map(String::toUpperCase)
            .forEach(System.out::print);
    }
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** THREE

#### Ответ от Claude

Разбор по шагам:

1. `filter(s -> s.length() > 3)`: `"one"` (3) — нет, `"two"` (3) — нет, `"three"` (5) — да.
2. `map(String::toUpperCase)`: `"three"` → `"THREE"`.
3. `forEach(System.out::print)`: выводит `THREE` без переноса строки.

Итог: `THREE`.

Источник: [Java SE 21 API — Stream](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/Stream.html)

---

### Вопрос 14. Что выведет код?

**Категория:** Java (HH) · **Уровень:** Advanced

```java
ByteBuffer buffer = ByteBuffer.allocate(10);
buffer.put((byte) 1);
buffer.put((byte) 2);
buffer.flip();

System.out.print(buffer.get());
System.out.print(" ");
System.out.println(buffer.get());
```

**Варианты ответа:**
- 1 1
- 2 1
- 2 2
- 258 0
- 1 2

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** 1 2

#### Ответ от Claude

Разбор последовательности операций с `ByteBuffer`:

1. `allocate(10)` — создаёт буфер ёмкостью 10 байт; `position = 0`, `limit = 10`.
2. `put((byte) 1)` — записывает 1 в позицию 0; `position = 1`.
3. `put((byte) 2)` — записывает 2 в позицию 1; `position = 2`.
4. `flip()` — переключает буфер в режим чтения: `limit = position (2)`, `position = 0`.
5. `get()` — читает байт из позиции 0 → **1**; `position = 1`.
6. `get()` — читает байт из позиции 1 → **2**; `position = 2`.

Вывод: `1 2`.

Источник: [Java SE 21 API — ByteBuffer](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/ByteBuffer.html)

---

### Вопрос 15. Какая гарантия отсутствует в `volatile`?

**Категория:** Java (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Видимость изменений для других потоков
- Отношение happens-before между записью и последующими чтениями
- Консистентные обновления для всех потоков
- Предотвращение переупорядочивания инструкций
- Атомарность инкремента (x++)

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/advanced.md)

**Правильный ответ:** Атомарность инкремента (x++)

#### Ответ от Claude

Ключевое слово `volatile` гарантирует:
- **Видимость**: запись в `volatile`-поле немедленно видна всем потокам (flush в основную память).
- **Happens-before**: запись в `volatile` happens-before любое последующее чтение того же поля из другого потока.
- **Запрет переупорядочивания** чтений и записей относительно `volatile`-операции.

Чего `volatile` **не гарантирует**: атомарность составных (read-modify-write) операций, таких как `x++`. Это операция из трёх шагов: (1) прочитать `x`, (2) прибавить 1, (3) записать результат. Между шагами 1 и 3 другой поток может изменить `x`, и инкремент будет потерян. Для атомарного инкремента используют `AtomicInteger.incrementAndGet()` или `synchronized`.

Источник: [JLS §17.4.4 — Synchronization Order](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4.4); [Baeldung — Guide to the Volatile Keyword in Java](https://www.baeldung.com/java-volatile)

---
