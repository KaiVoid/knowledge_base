# Java — Intermediate (HH)

### Вопрос 1. Приведённая ниже программа не компилируется. Какая ошибка допущена?

**Категория:** Java (HH) · **Уровень:** Intermediate

```java
class Printer {
    public static void print(String message) {
        System.out.println(message);
    }
}
public class Example {
    private static void main(String name, int age) { // метод 1
        if (age >= 18) {
            String message = name + " is adult";
        } else {
            String message = name + " is not adult";
        }
        Printer printer = null;
        printer.print(message);
    }
    public static void main(String[] args) { // метод 2
        main("Alex", 18);
    }
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Использование переменной вне её области видимости

#### Ответ от Claude

Переменная `message` объявлена внутри блоков `if` и `else` — она видна только внутри соответствующего блока `{}`. На строке `printer.print(message)` переменная `message` недоступна — она вышла из области видимости. Это ошибка компиляции: `cannot find symbol: variable message`.

Для исправления нужно объявить `message` до блока `if`:

```java
String message;
if (age >= 18) {
    message = name + " is adult";
} else {
    message = name + " is not adult";
}
printer.print(message);
```

Источник: [JLS §6.3 — Scope of a Declaration](https://docs.oracle.com/javase/specs/jls/se21/html/jls-6.html#jls-6.3)

---

### Вопрос 2. Что выведет фрагмент кода?

**Категория:** Java (HH) · **Уровень:** Intermediate

```java
int day = 4;
switch (day) {
    case 1:
        System.out.print("One");
        break;
    case 2:

    case 4:
        System.out.print("Four");
        day = 1;
    case 5:
        System.out.print("Five");
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** FourFive

#### Ответ от Claude

Управление выполнением оператора `switch`:

1. `day = 4` → выполнение начинается с `case 4`.
2. `case 4`: выводит `Four`, устанавливает `day = 1`. Нет `break` — выполнение «проваливается» (fall-through) в следующий `case`.
3. `case 5`: выводит `Five`. Конец блока `switch`.

Итог: `FourFive`. Обновление `day = 1` внутри `switch` не влияет на дальнейший выбор `case` — метка `case` проверяется только при входе в `switch`.

Источник: [JLS §14.11 — The switch Statement](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.11)

---

### Вопрос 3. Что произойдёт в данной программе?

**Категория:** Java (HH) · **Уровень:** Intermediate

```java
System.out.print("Hello");
while (1) {
    System.out.println(" World");
    break;
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Программа не скомпилируется

#### Ответ от Claude

В Java условие цикла `while` обязано быть выражением типа `boolean`. Целочисленный литерал `1` имеет тип `int`, а неявного преобразования `int → boolean` в Java нет (в отличие от C/C++). Компилятор выдаст ошибку:

```
error: incompatible types: int cannot be converted to boolean
```

В C/C++ `while(1)` — стандартный идиом бесконечного цикла, но Java намеренно запрещает такое, требуя явного `while(true)`.

Источник: [JLS §14.12 — The while Statement](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.12)

---

### Вопрос 4. В программе необходимо хранить температуру воды в градусах Цельсия от 0 до 100 (только целые значения). Какой тип данных выбрать?

**Категория:** Java (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** byte

#### Ответ от Claude

Тип `byte` хранит знаковые целые числа в диапазоне от −128 до 127. Диапазон 0–100 полностью укладывается в этот диапазон. `byte` занимает 1 байт — минимально возможный размер для целочисленного примитива в Java.

Для сравнения: `short` (−32 768 .. 32 767, 2 байта), `int` (2 млрд, 4 байта) и `long` (8 байт) избыточны для данной задачи. В большинстве реальных программ всё же используется `int` (стандартный «по умолчанию» целочисленный тип), поскольку `byte` при арифметических операциях автоматически расширяется до `int` и требует явных приведений. Но для минимизации памяти (например, в массиве) `byte` — оптимальный выбор.

Источник: [JLS §4.2.1 — Integral Types and Values](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html#jls-4.2.1)

---

### Вопрос 5. Что такое стирание типов (type erasure) в контексте Generics?

**Категория:** Java (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Процесс, при котором компилятор удаляет информацию о параметрах generic-типа во время компиляции, заменяя их на ограничивающие типы или Object

#### Ответ от Claude

Стирание типов (type erasure) — механизм реализации обобщений (generics) в Java. Во время компиляции компилятор:

1. Заменяет все параметры типа (type parameters) на их верхние границы: `<T extends Number>` → `Number`, `<T>` → `Object`.
2. При необходимости вставляет приведения типов (casts).
3. Генерирует bridge-методы для обеспечения полиморфизма.

В результате в байт-коде не остаётся информации о конкретных параметрах обобщённого типа. Поэтому во время выполнения нельзя сделать `new T()`, `T[]`, или `instanceof List<String>` — тип T уже стёрт.

Это сделано для обратной совместимости с кодом, написанным до появления generics в Java 5.

Источник: [Oracle Java Tutorial — Type Erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)

---

### Вопрос 6. Имеются два параметризованных списка. Какой тип будет у объектов этих списков после стирания типов?

**Категория:** Java (HH) · **Уровень:** Intermediate

```java
List<? extends Number> list1;
List<? super Integer> list2;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Для list1 типом будет Number, для list2 — Object

#### Ответ от Claude

Стирание типов заменяет wildcard-параметры на их **верхние границы (upper bounds)**:

- `List<? extends Number>`: верхняя граница — `Number`. После стирания → `List` (где элемент трактуется как `Number`).
- `List<? super Integer>`: нижняя граница — `Integer`, верхняя — `Object`. После стирания → `List` (где элемент трактуется как `Object`, поскольку нет явного `extends`-ограничения).

Таким образом: `list1` → `Number`, `list2` → `Object`.

Источники: [Oracle Java Tutorial — Erasure of Generic Types](https://docs.oracle.com/javase/tutorial/java/generics/genTypes.html); [JLS §4.6 — Type Erasure](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html#jls-4.6)

---

### Вопрос 7. Что выведет программа?

**Категория:** Java (HH) · **Уровень:** Intermediate

```java
String str1 = "HelloWorld";
String temp = "World";

String str2 = "Hello" + "World";
String str3 = "Hello" + temp;
String str4 = new String("HelloWorld");

System.out.print("str1 == str2: " + (str1 == str2) + "; ");
System.out.print("str1 == str3: " + (str1 == str3) + "; ");
System.out.print("str1 == str4: " + (str1 == str4));
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** str1 == str2: true; str1 == str3: false; str1 == str4: false

#### Ответ от Claude

Разбор по строкам:

- `str1 = "HelloWorld"` — строковый литерал, помещается в пул строк (String pool).
- `str2 = "Hello" + "World"` — конкатенация **двух констант** (compile-time constant folding): компилятор вычисляет результат на этапе компиляции и помещает `"HelloWorld"` в пул. `str1 == str2` → `true` (один и тот же объект из пула).
- `str3 = "Hello" + temp` — `temp` является переменной (не compile-time constant, хотя и `final` не объявлена), поэтому конкатенация происходит в runtime, создаётся новый объект вне пула. `str1 == str3` → `false`.
- `str4 = new String("HelloWorld")` — явный вызов конструктора всегда создаёт новый объект в heap вне пула. `str1 == str4` → `false`.

Источники: [JLS §3.10.5 — String Literals](https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.10.5); [Java SE 21 API — String.intern()](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/String.html#intern())

---

### Вопрос 8. Что выведет программа?

**Категория:** Java (HH) · **Уровень:** Intermediate

```java
public static void main(String[] args) {
    interface A {
        default void foo() {
            System.out.println("A");
        }
    }
    interface B {
        default void foo() {
            System.out.println("B");
        }
    }
    class C implements A, B {
        @Override
        public void foo() {
            System.out.println("Foo");
        }
    }
    A c = new C();
    c.foo();
}
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Foo

#### Ответ от Claude

Класс `C` явно переопределяет метод `foo()` с выводом `"Foo"`. Переменная `c` имеет статический тип `A`, но указывает на объект типа `C`. В Java метод вызывается по динамическому типу объекта (dynamic dispatch / virtual dispatch), а не по статическому типу переменной. Поэтому вызывается `C.foo()`, выводящий `"Foo"`.

В отличие от Вопроса 12 в разделе Advanced, здесь конфликт default-методов разрешён явным переопределением в классе `C` — это и есть обязательное требование Java при наличии нескольких conflicting defaults.

Источник: [JLS §9.4.1 — Inheritance and Overriding](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html#jls-9.4.1)

---

### Вопрос 9. Какое из следующих утверждений об интерфейсах в Java верно? (Java 8+)

**Категория:** Java (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Интерфейс может содержать статические методы с реализацией

#### Ответ от Claude

Начиная с Java 8, интерфейсы могут содержать:
- **`default`-методы** — методы с реализацией, наследуемые реализующими классами.
- **`static`-методы** — статические методы с реализацией, вызываемые только через имя интерфейса (не наследуются).

Утверждение «интерфейс может содержать статические методы с реализацией» — истинно начиная с Java 8.

До Java 8 интерфейсы могли содержать только константы и абстрактные методы. В Java 9 добавлены также `private`-методы в интерфейсах.

Источники: [JLS §9.4 — Abstract Method Declarations](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html#jls-9.4); [Oracle Java Tutorial — Default Methods](https://docs.oracle.com/javase/tutorial/java/IandI/defaultmethods.html)

---

### Вопрос 10. В чём основное отличие между проверяемыми (checked) и непроверяемыми (unchecked) исключениями в Java?

**Категория:** Java (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Проверяемые исключения обязательно должны быть объявлены в сигнатуре метода или обработаны, а непроверяемые нет

#### Ответ от Claude

В Java исключения делятся по иерархии:

- **Checked (проверяемые)**: наследники `Exception` (кроме `RuntimeException`). Компилятор обязывает либо перехватить их в блоке `try-catch`, либо объявить в сигнатуре метода через `throws`. Примеры: `IOException`, `SQLException`.
- **Unchecked (непроверяемые)**: наследники `RuntimeException` и `Error`. Компилятор не требует обработки. Примеры: `NullPointerException`, `ArrayIndexOutOfBoundsException`, `IllegalArgumentException`.

Логика разделения: checked-исключения — ожидаемые, восстановимые ситуации (файл не найден, ошибка сети); unchecked — программные ошибки или критические сбои, от которых обычно нельзя корректно восстановиться.

Источник: [Oracle Java Tutorial — Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/catchOrDeclare.html)

---

### Вопрос 11. В чём преимущество использования `ExecutorService` для управления потоками по сравнению с ручным созданием объектов `Thread`?

**Категория:** Java (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Упрощает управление потоками за счёт их повторного использования и предоставляет встроенные средства для планирования

#### Ответ от Claude

`ExecutorService` (реализации: `ThreadPoolExecutor`, `ScheduledThreadPoolExecutor`) предоставляет пул потоков, что даёт ключевые преимущества:

- **Повторное использование потоков**: создание и уничтожение потоков — дорогостоящие операции (аллокация стека, системные вызовы). Пул позволяет переиспользовать уже существующие потоки, снижая накладные расходы.
- **Управление очередью задач**: задачи ставятся в очередь, если все потоки заняты.
- **Встроенное планирование**: `ScheduledExecutorService` позволяет запускать задачи с задержкой или по расписанию.
- **Корректное завершение**: методы `shutdown()` / `awaitTermination()` обеспечивают ожидание завершения задач.
- **Возврат результатов**: поддерживает `Future<V>` и `Callable<V>` в отличие от `Runnable`.

Источник: [Java SE 21 API — ExecutorService](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/ExecutorService.html); [Oracle Tutorial — Executors](https://docs.oracle.com/javase/tutorial/essential/concurrency/executors.html)

---

### Вопрос 12. Что произойдёт с потоком, если он попытается войти в `synchronized`-блок, который уже занят другим потоком?

**Категория:** Java (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — java/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/java/intermediate.md)

**Правильный ответ:** Заблокируется до тех пор, пока другой поток не освободит монитор, после чего продолжит выполнение

#### Ответ от Claude

`synchronized`-блок в Java защищён **монитором** объекта (object intrinsic lock / monitor lock). Когда поток входит в `synchronized`-блок, он захватывает монитор. Если другой поток уже владеет монитором:

1. Новый поток переходит в состояние **BLOCKED** (отличие от WAITING/TIMED_WAITING, которые вызываются `wait()`/`sleep()`).
2. Поток ждёт в очереди на захват монитора.
3. После того как текущий владелец выйдет из `synchronized`-блока и освободит монитор, JVM выбирает один из ожидающих потоков, он захватывает монитор и продолжает выполнение.

Важно: Java не гарантирует честный порядок (fairness) для intrinsic lock — поток не обязательно получит монитор в порядке FIFO. В отличие от `ReentrantLock(true)`, который поддерживает fair-режим.

Источники: [JLS §17.1 — Synchronization](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.1); [Java SE 21 API — Thread.State](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.State.html)

---
