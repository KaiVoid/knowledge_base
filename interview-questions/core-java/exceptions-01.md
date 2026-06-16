# Исключения (checked/unchecked, try-with-resources) — часть 1 из 3

> Вопросы 1–20 (в части: 20). Всего в разделе: 60.
> Область знаний: [../../knowledge-base/06-exceptions.md](../../knowledge-base/06-exceptions.md)
> Правила: [../RULES.md](../RULES.md)
> Части: **ч.1** · [ч.2](exceptions-02.md) · [ч.3](exceptions-03.md)

---
### Вопрос 1. Опишите иерархию классов исключений в Java. Чем Error отличается от Exception?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Chapter 11. Exceptions — Java Language Specification SE 13](https://docs.oracle.com/javase/specs/jls/se13/html/jls-11.html)

Иерархия исключений в Java строится от корневого класса `Throwable`, который является прямым наследником `Object`. Его непосредственными подклассами являются `Exception` и `Error`.

- **Exception** — суперкласс исключений, из которых обычные программы могут попытаться восстановиться. Содержит подкласс `RuntimeException`.
- **RuntimeException** — прямой подкласс `Exception`; суперкласс исключений, которые могут быть выброшены в ходе вычислений, но от которых потенциально возможно восстановление.
- **Error** — суперкласс исключений, от которых обычные программы **не ожидаются** восстанавливаться. Представляет серьёзные проблемы: внутренние ошибки JVM или нехватку ресурсов.

Непроверяемые (unchecked) исключения — это `RuntimeException` и его подклассы, а также `Error` и его подклассы. Все остальные классы исключений являются проверяемыми (checked).

Класс `Error` выделен в отдельную ветку иерархии намеренно: это позволяет использовать конструкцию `catch (Exception e)` для перехвата всех исключений, от которых возможно восстановление, не захватывая при этом ошибки (`Error`), от которых восстановление, как правило, невозможно.

#### Ответ от Claude

Иерархия классов исключений в Java выглядит следующим образом:

```
java.lang.Object
  └── java.lang.Throwable
        ├── java.lang.Exception
        │     └── java.lang.RuntimeException
        │           ├── NullPointerException
        │           ├── IllegalArgumentException
        │           ├── ArithmeticException
        │           └── ...
        └── java.lang.Error
              ├── OutOfMemoryError
              ├── StackOverflowError
              └── ...
```

**Ключевые факты:**

- **`Throwable`** — корень всей иерархии. Только объекты этого класса (или его подклассов) можно бросать оператором `throw` и перехватывать в блоке `catch`.
- **`Exception`** — суперкласс исключительных ситуаций, от которых программа предположительно может восстановиться. Все его подклассы, кроме `RuntimeException` и его потомков, являются **checked (проверяемыми)** исключениями.
- **`RuntimeException`** — подкласс `Exception`. Вместе со своими подклассами составляет группу **unchecked (непроверяемых)** исключений. Как правило, свидетельствует об ошибке в логике программы.
- **`Error`** — отдельная ветка, предназначенная для серьёзных сбоев, выходящих за рамки контроля программы (ошибки JVM, нехватка памяти, переполнение стека). Является **unchecked**.

**Главное отличие `Error` от `Exception`:**

| Критерий | `Error` | `Exception` |
|---|---|---|
| Ветка иерархии | Прямой подкласс `Throwable` | Прямой подкласс `Throwable` |
| Тип | Всегда unchecked | Checked (кроме `RuntimeException`) |
| Смысл | Неустранимый сбой JVM/среды | Исключительная ситуация в программе |
| Ожидаемое поведение | Не перехватывать, не восстанавливаться | Можно и нужно обрабатывать (checked) |
| Примеры | `OutOfMemoryError`, `StackOverflowError` | `IOException`, `SQLException` |

Конструкция `catch (Exception e)` перехватит все `Exception` (включая `RuntimeException`), но **не перехватит** `Error` — это намеренное архитектурное решение JLS.

---

### Вопрос 2. Что такое checked и unchecked исключения? Приведите по 2–3 примера каждого вида.

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Unchecked Exceptions — The Controversy (The Java™ Tutorials)](https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html)

Непроверяемые (unchecked) исключения — это исключения, которые компилятор Java не обязывает методы перехватывать или объявлять. К ним относятся `RuntimeException` и его подклассы, а также `Error` и его подклассы.

Разработчики Java сделали `RuntimeException` непроверяемыми по двум причинам:

1. **Проблемы программирования vs. восстанавливаемые ситуации.** «Исключения времени выполнения представляют собой проблемы, являющиеся следствием ошибки программирования, и от клиентского кода API нельзя разумно ожидать восстановления от них». Примеры: деление на ноль (`ArithmeticException`), обращение через `null` (`NullPointerException`), выход за границы массива (`ArrayIndexOutOfBoundsException`).

2. **Ясность кода.** Требование объявлять все возможные `RuntimeException` в каждом методе значительно засорило бы код.

Основное правило: «Если от клиента разумно ожидать восстановления от исключения — сделайте его checked. Если клиент не может ничего сделать для восстановления — сделайте его unchecked».

#### Ответ от Claude

**Checked (проверяемые) исключения** — подклассы `Exception`, которые не являются подклассами `RuntimeException`. Компилятор обязывает либо перехватить их в блоке `try-catch`, либо объявить в сигнатуре метода через `throws`. Как правило, отражают внешние условия, на которые программа не может повлиять.

Примеры checked исключений:
- `IOException` — ошибка ввода-вывода (чтение файла, работа с сетью)
- `FileNotFoundException` — файл не найден (подкласс `IOException`)
- `SQLException` — ошибка при работе с базой данных
- `ParseException` — ошибка разбора текста (например, `SimpleDateFormat`)

**Unchecked (непроверяемые) исключения** — подклассы `RuntimeException` и подклассы `Error`. Компилятор не требует их обработки или объявления. Как правило, означают ошибку в логике программы или неустранимый сбой среды.

Примеры unchecked исключений:
- `NullPointerException` — обращение к методу/полю через `null`-ссылку
- `ArrayIndexOutOfBoundsException` — выход за границы массива
- `IllegalArgumentException` — передан недопустимый аргумент
- `OutOfMemoryError` (Error) — JVM не хватает памяти

**Краткое сравнение:**

| | Checked | Unchecked |
|---|---|---|
| Суперкласс | `Exception` (не `RuntimeException`) | `RuntimeException` или `Error` |
| Проверка компилятором | Да | Нет |
| Требует `try-catch` или `throws` | Да | Нет |
| Типичная причина | Внешние условия (файл, сеть, БД) | Ошибка логики программы |

---

### Вопрос 3. Что произойдёт, если не обработать checked-исключение и не объявить его в сигнатуре метода через throws?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [The Catch or Specify Requirement (The Java™ Tutorials)](https://docs.oracle.com/javase/tutorial/essential/exceptions/catchOrDeclare.html)

В Java действует правило **«Catch or Specify Requirement»** («поймай или объяви»). Код, который может выбросить определённые виды исключений, должен быть оформлен одним из двух способов:

1. **Catch** — обернуть код в `try`-блок с подходящим обработчиком `catch`.
2. **Specify** — объявить исключение в `throws`-клозе сигнатуры метода.

Согласно официальной документации: «Код, не соответствующий требованию Catch or Specify, **не скомпилируется**».

Это правило распространяется на checked-исключения. Ошибки (`Error`) и `RuntimeException` (и их подклассы) ему **не подчиняются** — они являются unchecked.

#### Ответ от Claude

Если checked-исключение не обработано в блоке `try-catch` **и** не объявлено в `throws`-клозе метода, произойдёт **ошибка компиляции**. Программа не будет скомпилирована.

Это поведение определено правилом **«Catch or Specify Requirement»** Java Language Specification. Согласно JLS: «Это ошибка времени компиляции, если тело метода или конструктора **может выбросить** некоторый класс исключений `E`, когда `E` является checked-классом исключений и `E` не является подклассом какого-либо класса, объявленного в `throws`-клозе метода или конструктора».

Пример кода, который **не скомпилируется**:
```java
public void readFile() {
    new FileInputStream("file.txt"); // FileInputStream бросает FileNotFoundException (checked)
    // Ошибка компиляции: unhandled exception FileNotFoundException
}
```

Варианты исправления:

**Вариант 1 — перехватить (catch):**
```java
public void readFile() {
    try {
        new FileInputStream("file.txt");
    } catch (FileNotFoundException e) {
        // обработка
    }
}
```

**Вариант 2 — объявить (throws):**
```java
public void readFile() throws FileNotFoundException {
    new FileInputStream("file.txt");
}
```

**Важные нюансы:**
- Ошибка именно **компиляции**, а не выполнения — программа не запустится вовсе.
- Правило действует только для checked-исключений. `NullPointerException`, `IllegalArgumentException` и другие `RuntimeException` можно не объявлять и не перехватывать — компилятор это допускает.
- Объявление через `throws` лишь перекладывает ответственность на вызывающий код — там исключение снова нужно поймать или пробросить дальше.

---

### Вопрос 4. В чём разница между ключевыми словами throw и throws?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [How to Throw Exceptions (The Java™ Tutorials)](https://docs.oracle.com/javase/tutorial/essential/exceptions/throwing.html)

Ключевое слово `throw` используется для явного выброса исключения из кода. Оператор `throw` требует единственного аргумента — объект, являющийся экземпляром `Throwable` (или его подкласса).

Синтаксис: `throw someThrowableObject;`

Пример из документации (метод `pop()` для стека):
```java
public Object pop() {
    Object obj;
    if (size == 0) {
        throw new EmptyStackException();
    }
    obj = objectAt(size - 1);
    setObjectAt(size - 1, null);
    size--;
    return obj;
}
```

Документация также указывает: «Обратите внимание, что объявление метода `pop` не содержит `throws`-клозы. `EmptyStackException` не является checked-исключением, поэтому `pop` не обязан объявлять, что оно может быть выброшено». Это иллюстрирует ключевое различие: `throws` нужен только для checked-исключений, тогда как `throw` используется для любых `Throwable`.

#### Ответ от Claude

`throw` и `throws` — разные языковые конструкции, решающие разные задачи.

**`throw`** — оператор внутри тела метода, который **фактически выбрасывает** экземпляр исключения в момент выполнения. После `throw` поток выполнения прерывается и управление передаётся ближайшему подходящему `catch`-блоку (или завершает программу, если обработчик не найден).

```java
public void checkAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Возраст не может быть отрицательным: " + age);
    }
}
```

**`throws`** — часть **сигнатуры метода**, которая объявляет, какие checked-исключения метод **может** выбросить. Это информация для компилятора и вызывающего кода — сам `throws` ничего не выбрасывает.

```java
public void readFile(String path) throws IOException {
    // метод может выбросить IOException
}
```

**Сводная таблица различий:**

| Критерий | `throw` | `throws` |
|---|---|---|
| Где используется | Внутри тела метода | В сигнатуре метода |
| Что делает | Фактически выбрасывает исключение | Объявляет возможное исключение |
| Аргумент | Экземпляр `Throwable` | Класс (тип) исключения |
| Количество | Одно исключение за раз | Несколько через запятую |
| Обязательность | Зависит от логики | Обязателен для checked при отсутствии catch |
| Применение к типам | Любой `Throwable` | Преимущественно checked (для unchecked — опционально) |

Пример с обоими ключевыми словами вместе:
```java
public void loadConfig(String path) throws IOException {
    if (path == null) {
        throw new IllegalArgumentException("Путь не может быть null"); // unchecked, throws не нужен
    }
    Files.readAllBytes(Paths.get(path)); // может бросить IOException (checked) — объявлено в throws
}
```

Итог: `throws` — это **декларация** (обещание компилятору и вызывающему коду), `throw` — это **действие** (реальный выброс объекта исключения в runtime).
### Вопрос 5. Всегда ли выполняется блок finally? В каких случаях он может не выполниться?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [The finally Block — The Java™ Tutorials (docs.oracle.com)](https://docs.oracle.com/javase/tutorial/essential/exceptions/finally.html)

Блок `finally` всегда выполняется при выходе из блока `try`. Это гарантирует его выполнение даже в случае непредвиденного исключения. Однако существует одно исключение из этого правила: блок `finally` может не выполниться, если JVM завершит работу в то время, пока выполняется код блоков `try` или `catch`.

#### Ответ от Claude

Блок `finally` выполняется практически всегда — как при нормальном завершении `try`, так и при любом исключении или операторе `return`/`break`/`continue`. Однако есть конкретные случаи, когда он **не** выполнится:

1. **`System.exit()`** — вызов немедленно завершает JVM, блок `finally` не исполняется.
2. **`Runtime.getRuntime().halt()`** — принудительная остановка JVM без запуска shutdown hooks и без выполнения `finally`.
3. **Убийство процесса JVM извне** — сигнал `SIGKILL` (Unix) или `TerminateProcess` (Windows) обрывает процесс немедленно.
4. **Бесконечный цикл или дедлок в `try`/`catch`** — управление никогда не дойдёт до `finally`.
5. **Поток-демон (daemon thread)** — если все не-демонные потоки завершились до того, как демон дошёл до блока `finally`, JVM завершается, не ожидая его выполнения.
6. **Фатальная ошибка JVM** — повреждение внутренних структур данных виртуальной машины (например, из нативного кода) может прервать выполнение.

Важно: `StackOverflowError` и другие `Error` не гарантируют пропуск `finally` — JVM попытается его выполнить, но при нехватке стека это может не получиться.

```java
try {
    System.exit(0); // finally НЕ будет выполнен
} finally {
    System.out.println("Это не напечатается");
}
```

---

### Вопрос 6. Что вернёт метод, если в блоке try есть return, а в блоке finally тоже есть return?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Why You Should Avoid Return Statements in Finally Blocks (w3tutorials.net)](https://www.w3tutorials.net/blog/return-in-the-finally-block-why-not/)

Когда в блоке `try` есть `return`, JVM временно сохраняет возвращаемое значение, затем выполняет блок `finally`. Если `finally` тоже содержит `return`, он переопределяет ранее сохранённое значение. Пример:

```java
public static int getValue() {
    try {
        System.out.println("Executing try block");
        return 10; // значение временно сохраняется
    } finally {
        System.out.println("Executing finally block");
        return 20; // переопределяет return из try
    }
}
// Результат: 20 (НЕ 10!)
```

Статья подчёркивает: `finally` нужно использовать только для освобождения ресурсов, но не для управления потоком выполнения.

#### Ответ от Claude

Метод вернёт значение из блока `finally`. Это определено в спецификации Java (JLS §14.20.2): если блок `finally` завершается внезапно (abrupt completion) — например, через `return` — то именно это завершение становится результатом всего оператора `try`, а причина завершения из блока `try` или `catch` **отбрасывается**.

Механизм работы:
1. JVM вычисляет значение `return` в блоке `try` и временно его запоминает.
2. Управление передаётся в блок `finally`.
3. `return` в `finally` завершает метод с новым значением — сохранённое значение из `try` игнорируется.

```java
public static int example() {
    try {
        return 10;
    } finally {
        return 20; // вернёт 20
    }
}

public static int withException() {
    try {
        throw new RuntimeException("ошибка");
    } finally {
        return 42; // вернёт 42, исключение подавляется!
    }
}
```

Во втором примере `return` в `finally` также **подавляет исключение** из `try` — оно будет полностью проигнорировано, что делает отладку очень сложной.

Это поведение считается **антипаттерном**: блок `finally` должен использоваться исключительно для освобождения ресурсов, не для возврата значений.

---

### Вопрос 7. Что такое try-with-resources? Какой интерфейс должен реализовывать ресурс, используемый в этой конструкции?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [The try-with-resources Statement — The Java™ Tutorials (docs.oracle.com)](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)

Оператор `try`-with-resources — это оператор `try`, объявляющий один или несколько ресурсов. Ресурс — это объект, который должен быть закрыт после того, как программа завершила с ним работу. Оператор гарантирует закрытие каждого ресурса по завершении оператора. Любой объект, реализующий `java.lang.AutoCloseable` (включая все объекты, реализующие `java.io.Closeable`), может использоваться как ресурс.

Пример:
```java
static String readFirstLineFromFile(String path) throws IOException {
    try (FileReader fr = new FileReader(path);
         BufferedReader br = new BufferedReader(fr)) {
        return br.readLine();
    }
}
```

Если исключение выброшено из блока `try`, а также из оператора `try`-with-resources, исключения из закрытия ресурсов подавляются (suppressed), и именно исключение из блока является результирующим. Получить подавленные исключения можно через метод `Throwable.getSuppressed()`.

#### Ответ от Claude

**try-with-resources** — конструкция, введённая в Java 7 (JEP 334), которая автоматически закрывает ресурсы при выходе из блока `try` — вне зависимости от того, произошло ли исключение.

Ресурс должен реализовывать интерфейс **`java.lang.AutoCloseable`**:

```java
public interface AutoCloseable {
    void close() throws Exception;
}
```

Также допустимо реализовывать **`java.io.Closeable`** (расширяет `AutoCloseable`), у которого метод `close()` объявлен как `throws IOException`.

**Синтаксис:**
```java
try (ResourceType resource = new ResourceType()) {
    // использование ресурса
} // close() вызывается автоматически
```

**Несколько ресурсов** (закрываются в порядке, обратном объявлению):
```java
try (FileInputStream fis = new FileInputStream("in.txt");
     FileOutputStream fos = new FileOutputStream("out.txt")) {
    // работа с обоими ресурсами
}
```

**Подавленные исключения (suppressed exceptions):** если исключение выброшено и в блоке `try`, и при вызове `close()`, приоритет получает исключение из `try`, а исключение из `close()` сохраняется как подавленное и доступно через `e.getSuppressed()`.

**Java 9+**: переменная ресурса может быть объявлена за пределами блока, если она effectively final:
```java
FileReader fr = new FileReader("file.txt");
try (fr) { // допустимо с Java 9
    // ...
}
```

**Отличие от традиционного try-finally:** при использовании `finally` для закрытия ресурсов исключение из `finally` подавляло бы исключение из `try`; `try`-with-resources решает эту проблему корректно.

---

### Вопрос 8. Можно ли поймать несколько исключений в одном блоке catch? Как это записывается синтаксически?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Catching Multiple Exception Types and Rethrowing Exceptions (docs.oracle.com)](https://docs.oracle.com/javase/8/docs/technotes/guides/language/catch-multiple.html)

В Java SE 7 и более поздних версиях один блок `catch` может обрабатывать несколько типов исключений. В предложении `catch` укажите типы исключений, которые блок должен обрабатывать, разделяя каждый тип вертикальной чертой (`|`):

```java
catch (IOException|SQLException ex) {
    logger.log(ex);
    throw ex;
}
```

Если блок `catch` обрабатывает более одного типа исключений, параметр `catch` является неявно финальным (`final`). В данном примере параметр `ex` является `final`, и поэтому нельзя присваивать ему значения внутри блока `catch`.

#### Ответ от Claude

Да, начиная с **Java 7** (multi-catch, JEP 334) можно поймать несколько исключений в одном блоке `catch` с помощью оператора `|` (вертикальная черта):

```java
try {
    // код, который может выбросить разные исключения
} catch (IOException | SQLException ex) {
    logger.log(ex);
    throw ex;
}
```

**Ключевые правила:**

1. **Параметр неявно final** — переменную исключения нельзя переприсвоить внутри блока:
   ```java
   catch (IOException | SQLException ex) {
       ex = new IOException(); // ОШИБКА КОМПИЛЯЦИИ
   }
   ```

2. **Типы не должны быть в отношении наследования** — нельзя написать `catch (Exception | IOException ex)`, так как `IOException` является подклассом `Exception`; компилятор выдаст ошибку.

3. **Генерируемый байткод эффективнее** — компилятор создаёт один обработчик вместо дублирующихся блоков.

4. **Порядок типов не имеет значения** для multi-catch (в отличие от раздельных блоков `catch`, где порядок важен — более конкретные идут первыми).

**До Java 7** приходилось писать повторяющийся код:
```java
// До Java 7 — дублирование
catch (IOException ex) {
    logger.log(ex);
    throw ex;
} catch (SQLException ex) {
    logger.log(ex);
    throw ex;
}
```

Multi-catch устраняет дублирование и снижает соблазн использовать чрезмерно широкий тип (`catch (Exception e)`).

---
### Вопрос 9. Как создать собственное исключение? Когда стоит наследоваться от Exception, а когда — от RuntimeException?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Implement Custom Exceptions in Java: Why, When and How — Stackify](https://stackify.com/java-custom-exceptions/)

Создать пользовательское исключение просто: нужно унаследоваться от `Exception` (для checked) или от `RuntimeException` (для unchecked). Главный принцип: создавайте собственное исключение только тогда, когда оно даёт реальное преимущество над стандартными исключениями Java — например, добавляет бизнес-контекст, дополнительные поля или полезные методы.

**Checked (наследование от Exception):**
```java
public class MyBusinessException extends Exception {
    private final ErrorCode code;

    public MyBusinessException(String message, Throwable cause, ErrorCode code) {
        super(message, cause);
        this.code = code;
    }

    public ErrorCode getCode() {
        return this.code;
    }
}
```

**Unchecked (наследование от RuntimeException):**
```java
public class MyUncheckedBusinessException extends RuntimeException {
    private final ErrorCode code;

    public MyUncheckedBusinessException(String message, Throwable cause, ErrorCode code) {
        super(message, cause);
        this.code = code;
    }
}
```

Checked-исключение используется тогда, когда вызывающий код обязан его обработать. Unchecked — когда восстановление не предполагается или обработка не обязательна.

#### Ответ от Claude

**Как создать собственное исключение**

Для создания пользовательского исключения достаточно унаследоваться от нужного базового класса и предоставить конструкторы. Минимальный пример:

```java
// Checked исключение
public class IncorrectFileNameException extends Exception {
    public IncorrectFileNameException(String message) {
        super(message);
    }

    public IncorrectFileNameException(String message, Throwable cause) {
        super(message, cause);
    }
}

// Unchecked исключение
public class ProductNotFoundException extends RuntimeException {
    private final int productId;

    public ProductNotFoundException(String message, int productId) {
        super(message);
        this.productId = productId;
    }

    public int getProductId() {
        return productId;
    }
}
```

**Когда наследоваться от `Exception` (checked)**

- Ситуация вне контроля программы (файл не найден, сеть недоступна), но вызывающий код **может и должен** её обработать: повторить попытку, предложить альтернативу, показать сообщение пользователю.
- Исключение является частью публичного API метода и его наличие важно отразить в сигнатуре через `throws`.
- Правило Oracle: *«Если клиент может разумно ожидать восстановления после исключения — сделайте его checked»*.

**Когда наследоваться от `RuntimeException` (unchecked)**

- Исключение сигнализирует об **ошибке в коде** (неверный аргумент, нарушение контракта метода, null там, где он недопустим).
- Вызывающий код всё равно не может ничего сделать, кроме как залогировать ошибку и прервать операцию.
- Исключение будет использоваться в контексте, где принудительный `try/catch` создаёт лишний шум (например, в лямбдах или stream-пайплайнах).

**Практические рекомендации**

1. Всегда предоставляйте конструктор с `Throwable cause` — это сохраняет исходный стек вызовов при оборачивании исключений.
2. Придерживайтесь суффикса `Exception` в имени класса.
3. Не создавайте собственное исключение ради исключения — если `IllegalArgumentException` или `IllegalStateException` точно описывает ситуацию, используйте их.
4. В современных проектах (особенно со Spring) принято использовать unchecked-исключения по умолчанию, переходя к checked только там, где обработка действительно обязательна и значима.

---

### Вопрос 10. Почему NullPointerException и ArrayIndexOutOfBoundsException являются unchecked-исключениями, а IOException — checked?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Unchecked Exceptions — The Controversy (The Java™ Tutorials)](https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html)

Согласно официальной документации Oracle, разграничение основано на принципе **возможности восстановления**:

> «Если клиент может разумно ожидать восстановления после исключения — сделайте его checked. Если клиент не может ничего предпринять для восстановления — сделайте его unchecked.»

`NullPointerException` и `ArrayIndexOutOfBoundsException` — это **ошибки программирования** (неверная логика кода), после которых вызывающий код не может разумно восстановиться — он должен исправить сам код. Поэтому они unchecked.

`IOException` представляет **внешние условия** (проблемы с сетью, файловой системой), которые могут возникнуть несмотря на корректный код, и вызывающий код *может* принять меры: повторить попытку, использовать другой источник данных, уведомить пользователя. Поэтому он checked.

Документация также поясняет: обязательное объявление runtime-исключений во всех сигнатурах методов снизило бы читаемость программ, не давая практической пользы.

#### Ответ от Claude

**Иерархия исключений Java**

```
Throwable
├── Error              (JVM-ошибки: OutOfMemoryError, StackOverflowError)
└── Exception
    ├── IOException    ← checked
    ├── SQLException   ← checked
    └── RuntimeException  ← unchecked (и все наследники)
        ├── NullPointerException
        ├── ArrayIndexOutOfBoundsException
        ├── IllegalArgumentException
        └── ...
```

**Почему `NullPointerException` и `ArrayIndexOutOfBoundsException` — unchecked**

Оба исключения являются прямыми наследниками `RuntimeException` и сигнализируют об **ошибках в логике программы**:

- `NullPointerException` — попытка обратиться к члену объекта через `null`-ссылку. Это программный дефект; корректный код не должен допускать такой ситуации.
- `ArrayIndexOutOfBoundsException` — обращение по индексу за пределами массива. Тоже программная ошибка: граница массива известна и должна проверяться заранее.

Вызывающий код не может «обработать» эти исключения в рантайме и продолжить работу — он может лишь залогировать их. Принудительный `try/catch` вокруг каждого обращения к объекту или массиву сделал бы код нечитаемым.

**Почему `IOException` — checked**

`IOException` сигнализирует о **внешних, непредсказуемых условиях**: файл может быть удалён другим процессом, сетевое соединение может прерваться в любой момент — и это не ошибка программы. Вызывающий код вполне способен разумно отреагировать: повторить операцию, попросить пользователя указать другой файл, переключиться на резервный источник.

**Ключевое правило**

| Вид исключения | Причина | Восстановление | Пример |
|---|---|---|---|
| Unchecked (RuntimeException) | Ошибка программиста | Невозможно/бессмысленно | NPE, AIOOBE |
| Checked (Exception) | Внешнее условие | Возможно и осмысленно | IOException, SQLException |

Этот дизайн отражает намерение Java-авторов: компилятор заставляет разработчика явно обдумывать ситуации, которые реально могут произойти в корректной программе, и не засоряет код обработкой логических ошибок.

---

### Вопрос 11. Что такое подавленные исключения (suppressed exceptions) в try-with-resources? Как их получить программно?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [The try-with-resources Statement — Oracle Java 8 Language Guide](https://docs.oracle.com/javase/8/docs/technotes/guides/language/try-with-resources.html)

Если в блоке `try` выброшено исключение и одновременно метод `close()` ресурса тоже выбрасывает исключение, то исключение из `close()` **подавляется (suppressed)**, а наружу пропагируется исключение из тела `try`. Это принципиальное отличие от старого шаблона с `finally`, где исключение из `finally` **перекрывало** исходное.

Подавленные исключения можно получить вызовом `Throwable.getSuppressed()`, который возвращает массив `Throwable[]`:

```java
} catch (IOException e) {
    Throwable[] suppressed = e.getSuppressed();
    for (Throwable t : suppressed) {
        System.out.println("Suppressed: " + t);
    }
}
```

Начиная с Java 7, класс `Throwable` предоставляет два метода: `addSuppressed(Throwable)` для добавления подавленного исключения и `getSuppressed()` для его получения.

#### Ответ от Claude

**Что такое подавленные исключения**

Подавленное (suppressed) исключение — это исключение, которое было выброшено во время закрытия ресурса (в методе `close()`) в тот момент, когда уже распространяется другое исключение из тела блока `try`. Чтобы не потерять первичное исключение, Java «прячет» исключение из `close()` внутрь первичного.

Механизм появился в Java 7 вместе с `try-with-resources` и методами `Throwable.addSuppressed()` / `Throwable.getSuppressed()`.

**Проблема, которую это решает**

До Java 7 при использовании `finally` исключение из блока `finally` полностью перекрывало исходное:

```java
// Старый код — исключение из close() скрывает исходное!
InputStream in = new FileInputStream("file.txt");
try {
    // ... throws IOException A
} finally {
    in.close(); // throws IOException B — A теряется навсегда
}
```

**Как работает try-with-resources**

```java
try (MyResource res = new MyResource()) {
    throw new Exception("исключение из тела try");  // это — первичное
    // res.close() тоже бросает исключение — оно будет suppressed
}
```

JVM автоматически вызывает `primaryException.addSuppressed(closeException)` и пробрасывает первичное исключение.

**Как получить подавленные исключения программно**

```java
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // ... работа с базой данных
} catch (SQLException e) {
    System.out.println("Основное: " + e.getMessage());

    // Получаем все подавленные исключения
    Throwable[] suppressed = e.getSuppressed();
    for (Throwable t : suppressed) {
        System.out.println("Подавленное: " + t.getMessage());
    }
}
```

**Добавление подавленных исключений вручную**

В редких случаях, когда вы строите собственные механизмы управления ресурсами вне `try-with-resources`, можно добавлять suppressed-исключения вручную:

```java
Exception primary = new Exception("основное");
primary.addSuppressed(new Exception("подавленное 1"));
primary.addSuppressed(new Exception("подавленное 2"));
throw primary;
```

**Особенности**

- `getSuppressed()` возвращает `Throwable[]`; если подавленных исключений нет — возвращает пустой массив (не `null`).
- Порядок в массиве соответствует порядку вызовов `addSuppressed()`.
- Suppression можно отключить, вызвав в конструкторе `Throwable` специальный защищённый конструктор с параметром `enableSuppression = false`, но на практике это почти никогда не нужно.

---

### Вопрос 12. В каком порядке закрываются ресурсы, объявленные в блоке try-with-resources, если их несколько?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [The try-with-resources Statement (The Java™ Tutorials)](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)

Ресурсы закрываются в **обратном порядке** относительно их объявления. Официальная документация явно указывает:

> «Note that the `close` methods of resources are called in the _opposite_ order of their creation.»

Пример из документации:

```java
try (
    java.util.zip.ZipFile zf = new java.util.zip.ZipFile(zipFileName);
    java.io.BufferedWriter writer =
        java.nio.file.Files.newBufferedWriter(outputFilePath, charset)
) {
    // код
}
// Закрывается: сначала writer, потом zf
```

`BufferedWriter` объявлен вторым — он закрывается первым. `ZipFile` объявлен первым — он закрывается последним.

#### Ответ от Claude

**Порядок закрытия: LIFO (Last In, First Out)**

При наличии нескольких ресурсов в одном блоке `try-with-resources` они закрываются в **обратном порядке объявления** — то есть последний объявленный ресурс закрывается первым.

```java
try (
    Connection conn   = dataSource.getConnection();       // открывается 1-м
    PreparedStatement ps = conn.prepareStatement(sql);    // открывается 2-м
    ResultSet rs      = ps.executeQuery()                 // открывается 3-м
) {
    // работа с rs, ps, conn
}
// Закрытие:
// 1. rs.close()   — закрывается 1-м (объявлен последним)
// 2. ps.close()   — закрывается 2-м
// 3. conn.close() — закрывается 3-м (объявлен первым)
```

**Почему именно LIFO**

Это логично с точки зрения зависимостей: `ResultSet` зависит от `PreparedStatement`, который зависит от `Connection`. Закрывать их нужно от «листьев» к «корню» дерева зависимостей — именно это и обеспечивает обратный порядок.

**Что происходит при исключениях во время закрытия**

Если несколько `close()`-методов бросают исключения, JVM продолжает закрывать оставшиеся ресурсы (пропуск не происходит), а все исключения из `close()`, кроме первого, становятся suppressed-исключениями первого:

```java
try (
    ResourceA a = new ResourceA();   // close() бросит ExceptionA
    ResourceB b = new ResourceB()    // close() бросит ExceptionB
) {
    // нормальное завершение (нет исключения из тела try)
}
// Результат: ExceptionB бросается наружу (закрыт первым),
//            ExceptionA добавляется как suppressed к ExceptionB
```

Если же исключение было и в теле `try`, и в `close()`:

```java
try (ResourceA a = new ResourceA()) {
    throw new MainException();   // это первичное исключение
    // a.close() тоже бросает CloseException
}
// Результат: MainException бросается наружу,
//            CloseException добавляется как suppressed к MainException
```

**Начиная с Java 9: несколько ресурсов через точку с запятой**

```java
// Обе формы эквивалентны по семантике закрытия:
try (A a = new A(); B b = new B()) { ... }

// Java 9+: ранее объявленная effectively-final переменная
A a = new A();
B b = new B();
try (a; b) { ... }  // закрывается: b первым, a вторым
```

**Итог**

| Порядок объявления | Порядок открытия | Порядок закрытия |
|---|---|---|
| Первый | Первым | Последним |
| Второй | Вторым | Предпоследним |
| N-й (последний) | Последним | Первым |

Это поведение гарантировано спецификацией языка Java и не зависит от реализации JVM.

---
### Вопрос 13. Что такое цепочка исключений (exception chaining)? Как правильно передать исходное исключение при выбрасывании нового?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Chained Exceptions — The Java™ Tutorials (docs.oracle.com)](https://docs.oracle.com/javase/tutorial/essential/exceptions/chained.html)

Цепочка исключений позволяет зафиксировать момент, когда одно исключение стало причиной другого. Это помогает понять последовательность и взаимосвязь исключений в приложении.

Приложение нередко реагирует на исключение тем, что выбрасывает другое исключение. По сути, первое исключение _является причиной_ второго. Класс `Throwable` предоставляет следующий API для управления цепочками:

| Метод / Конструктор | Назначение |
|---|---|
| `Throwable getCause()` | Возвращает исключение, вызвавшее текущее |
| `Throwable initCause(Throwable)` | Устанавливает причину текущего исключения |
| `Throwable(String, Throwable)` | Конструктор: создаёт исключение с сообщением и причиной |
| `Throwable(Throwable)` | Конструктор: создаёт исключение с причиной |

Пример использования:

```java
try {
    // код, бросающий IOException
} catch (IOException e) {
    throw new SampleException("Other IOException", e);
}
```

Здесь исходный `IOException` перехватывается, и создаётся новое `SampleException`, которому передаётся оригинальное исключение как причина. Цепочка исключений передаётся следующему обработчику. Метод `printStackTrace()` автоматически выводит всю цепочку причин.

#### Ответ от Claude

**Цепочка исключений (exception chaining)** — механизм, позволяющий при выбрасывании нового исключения сохранить ссылку на исходное (причину). Это обеспечивает полное представление о том, что именно пошло не так: и высокоуровневый контекст, и низкоуровневая причина.

**Зачем нужно.** Без цепочки при конструкции `throw new MyException()` информация об исходной ошибке теряется безвозвратно, что серьёзно затрудняет отладку. Унифицированный механизм был введён в Java 1.4 (JEP описан в [Chained Exception Facility](https://docs.oracle.com/javase/8/docs/technotes/guides/lang/chained-exceptions.html)).

**Два способа передать причину:**

1. **Через конструктор (предпочтительный способ)** — если класс исключения принимает `cause` в конструкторе:

```java
try {
    // низкоуровневая операция
} catch (IOException e) {
    throw new ServiceException("Не удалось загрузить конфигурацию", e);
}
```

2. **Через `initCause()`** — для старых или сторонних классов исключений, у которых нет конструктора с `Throwable`:

```java
MyLegacyException ex = new MyLegacyException("Сообщение");
ex.initCause(originalException);
throw ex;
```

Важно: `initCause()` можно вызвать не более одного раза. Если исключение создано через `Throwable(Throwable)` или `Throwable(String, Throwable)`, повторный вызов `initCause()` бросит `IllegalStateException`.

**Чтение цепочки:**

```java
catch (ServiceException e) {
    Throwable cause = e.getCause(); // исходный IOException
    // ...
}
```

**Автоматическая печать цепочки** — `e.printStackTrace()` выводит всю цепочку причин, помечая каждый следующий элемент `Caused by:`.

**Правила правильного использования:**
- Всегда передавайте исходное исключение при перебрасывании — не теряйте причину.
- При создании собственных классов исключений обязательно добавляйте конструктор `(String message, Throwable cause)`.
- Не глушите исключение пустым `catch` — минимум залогируйте его или передайте как причину нового.

---

### Вопрос 14. Можно ли объявить метод с сигнатурой, которая бросает более широкое проверяемое исключение, чем метод родительского класса? Что будет при переопределении?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Exception Handling with Method Overriding — beginnersbook.com](https://beginnersbook.com/2014/01/exception-handling-in-method-overriding-with-example/)

Переопределяющий метод не должен объявлять проверяемые исключения, которые являются новыми или более широкими, чем те, что объявлены в переопределяемом методе. Однако переопределяющий метод может объявлять любые непроверяемые (unchecked) исключения вне зависимости от того, объявляет ли их переопределяемый метод.

Что разрешено:
- Бросать непроверяемые исключения (`RuntimeException` и подклассы) — без ограничений.
- Бросать то же самое проверяемое исключение, что и родительский метод.
- Бросать более узкое проверяемое исключение (подкласс исключения родителя).
- Не объявлять исключений вовсе.

Что вызывает ошибку компиляции:
- Если родительский метод объявляет `IOException`, дочерний не может объявить `Exception` (более широкий суперкласс).
- Если родительский метод не объявляет проверяемых исключений, дочерний не может добавить новое проверяемое исключение.

Пример ошибки:
```java
class Building { void color() { } }
class Room extends Building {
    void color() throws IOException { } // Ошибка компиляции
}
```

Пример допустимого сужения:
```java
class Building { void color() throws IOException { } }
class Room extends Building {
    void color() throws FileNotFoundException { } // OK — FileNotFoundException extends IOException
}
```

#### Ответ от Claude

**Нет, нельзя.** При переопределении метода дочерний класс **не вправе** объявлять проверяемые исключения, которые шире (являются суперклассами) или вовсе новые по отношению к тем, что объявлены в родительском методе. Нарушение этого правила вызывает **ошибку компиляции**.

**Почему это так.** Правило вытекает из принципа подстановки Лисков (LSP) и полиморфизма. Если клиентский код работает с переменной типа `Parent` и обрабатывает объявленные исключения, подменённый объект `Child` не должен «неожиданно» выбрасывать исключения, о которых клиент не предупреждён. Это закреплено в JLS §8.4.8.3.

**Полная таблица правил:**

| Ситуация | Проверяемые исключения | Непроверяемые исключения |
|---|---|---|
| Родитель не объявляет исключений | Нельзя добавить новое checked | Можно добавить любое unchecked |
| Родитель объявляет `IOException` | Можно: то же / подкласс / ничего. Нельзя: `Exception`, новое checked | Можно добавить любое unchecked |
| Интерфейс без throws | Реализация не может добавить checked | Можно добавить любое unchecked |

**Примеры:**

```java
class Parent {
    void process() throws IOException { }
}

class Child extends Parent {
    // OK — более узкое исключение
    void process() throws FileNotFoundException { }
}

class BrokenChild extends Parent {
    // Ошибка компиляции — Exception шире IOException
    void process() throws Exception { }
}

class AnotherBroken extends Parent {
    // Ошибка компиляции — SQLException не является подклассом IOException
    void process() throws SQLException { }
}
```

**Непроверяемые исключения** (`RuntimeException`, `Error` и их подклассы) этими ограничениями не связаны — их можно добавлять при переопределении без ограничений, даже если родительский метод их не объявлял.

**Практический вывод:** при проектировании иерархий выбирайте checked-исключения в родительском методе с запасом или используйте unchecked — это даёт больше свободы реализациям.

---

### Вопрос 15. Что произойдёт, если исключение возникнет внутри блока finally — как это повлияет на исходное исключение из блока try?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Did You Know? A finally Block Can Quietly Swallow Exceptions in Java — Medium (@vishal_13_)](https://medium.com/@vishal_13_/did-you-know-a-finally-block-can-quietly-swallow-exceptions-in-java-57c3a729cbed)

Если в блоке `finally` выброшено исключение, оно **заменяет** исходное исключение из блока `try` или `catch`. Исходное исключение при этом **теряется безвозвратно**.

Опасный пример:

```java
public void doWork() {
    try {
        throw new RuntimeException("Исходное исключение");
    } finally {
        throw new RuntimeException("Исключение в finally");
    }
}
```

В результате вызывающий код видит только `"Исключение в finally"`, а корневая причина исчезает, что делает отладку крайне затруднительной.

Для сохранения обоих исключений (начиная с Java 7) используется метод `addSuppressed()`:

```java
} catch (Throwable t) {
    if (primary != null) {
        primary.addSuppressed(t);
    } else {
        throw t;
    }
}
```

Лучшая практика — избегать выброса исключений в блоке `finally` и использовать `try-with-resources`.

#### Ответ от Claude

**Исходное исключение из `try` будет потеряно.** Если блок `finally` выбрасывает исключение, оно полностью вытесняет оригинальное: управление передаётся вызывающему стеку с новым исключением, а старое не сохраняется нигде автоматически.

**Механика:**

```java
void riskyMethod() {
    try {
        throw new RuntimeException("Ошибка в бизнес-логике"); // (1)
    } finally {
        throw new RuntimeException("Ошибка при закрытии ресурса"); // (2) подавляет (1)
    }
}
```

Вызывающий код поймает только исключение `(2)`. Исключение `(1)` не попадёт ни в стек-трейс, ни в `getCause()`.

**Исторический контекст и решение.** До Java 7 единственный способ избежать потери — явно перехватывать исключение `finally` и сохранять его вручную. Java 7 решила эту проблему двумя инструментами:

**1. `try-with-resources` (рекомендуется).** JVM сама управляет цепочкой: исключение из `close()` не заменяет основное, а добавляется к нему через `addSuppressed()`.

```java
try (Connection conn = dataSource.getConnection()) {
    // если здесь исключение, и conn.close() тоже бросит — close() уйдёт в suppressed
    conn.prepareStatement("...").execute();
}
```

**2. Ручное использование `addSuppressed()`.** Если `try-with-resources` не подходит:

```java
Exception primary = null;
try {
    throw new RuntimeException("Ошибка бизнес-логики");
} catch (Exception e) {
    primary = e;
    throw e;
} finally {
    try {
        closeResource();
    } catch (Exception finallyEx) {
        if (primary != null) {
            primary.addSuppressed(finallyEx); // цепочка сохранена
        } else {
            throw finallyEx;
        }
    }
}
```

Прочитать подавленные исключения можно через `e.getSuppressed()` — возвращает массив `Throwable[]`.

**Правила хорошего тона:**
- Никогда не выбрасывайте исключения из `finally` без обработки.
- Используйте `try-with-resources` для всех `AutoCloseable` ресурсов.
- Если `finally` выполняет логирование — оберните его в `try-catch` внутри `finally`, чтобы ошибка логирования не подавила основное исключение.
- Оператор `return` в блоке `finally` тоже подавляет исключение — это ещё одна ловушка.

---

### Вопрос 16. Чем отличается перехват исключения типа Exception от перехвата Throwable? Когда оправдано ловить Throwable?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Why Catching Throwable or Error is Bad Idea in Java? — javarevisited.blogspot.com](https://javarevisited.blogspot.com/2014/02/why-catching-throwable-or-error-is-bad.html)

При перехвате `Throwable` никто не знает, какой именно тип ошибки будет поймана — это нарушает принцип точности обработки исключений. `Throwable` охватывает в том числе `Error`-исключения (например, `OutOfMemoryError`, `StackOverflowError`), которые сигнализируют о фундаментальных сбоях JVM, а не о прикладных ошибках.

Перехват `Throwable` маскирует программные ошибки (`NullPointerException` и подобные), которые должны всплывать, а не подавляться. Кроме того, системные исключения вроде `OutOfMemoryError` должны распространяться до специальных обработчиков, предназначенных именно для них.

Оправданные сценарии для `catch (Throwable t)`:
- Приложения, которые должны работать непрерывно при любых сбоях (never-stop systems).
- Системы обработки данных, где сбой одной задачи не должен останавливать весь поток.
- Только как «защитная сетка» последнего уровня, а не как основная стратегия обработки.

Даже `catch (Exception e)` почти так же проблематично — оно объединяет несовместимые случаи: `NullPointerException`, `InterruptedException` и многое другое. Лучше использовать multi-catch (Java 7+) для явной обработки конкретных типов.

#### Ответ от Claude

**Иерархия:**

```
java.lang.Object
  └── java.lang.Throwable
        ├── java.lang.Exception
        │     ├── RuntimeException (unchecked)
        │     └── IOException, SQLException, ... (checked)
        └── java.lang.Error
              ├── OutOfMemoryError
              ├── StackOverflowError
              ├── AssertionError
              └── ...
```

`catch (Exception e)` перехватывает всё, что является `Exception` и её подклассами — то есть всё, кроме `Error`.  
`catch (Throwable t)` перехватывает абсолютно всё: и `Exception`, и `Error`.

**Ключевое различие — класс `Error`.**  
`Error` представляет серьёзные проблемы, от которых приложение, как правило, не может восстановиться: нехватка памяти (`OutOfMemoryError`), переполнение стека (`StackOverflowError`), внутренние ошибки JVM (`InternalError`), ошибки загрузки класса (`NoClassDefFoundError`). Перехватив такую ошибку, приложение не знает, в каком состоянии находится JVM, и любые дальнейшие действия могут дать непредсказуемый результат.

**Почему `catch (Throwable)` опасно:**
1. Маскирует фундаментальные сбои JVM — программа «видит» работу там, где её нет.
2. Скрывает баги в коде: `NullPointerException` из-за ошибки разработчика будет тихо поглощён.
3. Препятствует корректному завершению работы — JVM может находиться в нестабильном состоянии после `OutOfMemoryError`.
4. Нарушает принцип минимальной зоны перехвата (catch as specific as possible).

**Когда `catch (Throwable)` оправдано (редкие случаи):**

| Сценарий | Обоснование |
|---|---|
| Фреймворки и контейнеры (Spring, Tomcat, JUnit) | Необходимо изолировать сбой одного компонента/теста от остальных |
| Обработчик верхнего уровня потока (`Thread.setUncaughtExceptionHandler`) | Логирование перед завершением потока |
| Plugin/classloader архитектуры | Сбой плагина не должен убивать хост-приложение |
| Системы непрерывной обработки (очереди, batch-процессоры) | Одна задача не должна останавливать весь конвейер |

**Обязательные условия при использовании `catch (Throwable)`:**
- Залогировать полный стек-трейс.
- Если пойман `Error` — как правило, следует перевыбросить или немедленно завершить процесс.
- Не «глотать» молча: минимум логирование с уровнем `ERROR`/`FATAL`.

**Практическая рекомендация:** в прикладном коде используйте конкретные типы исключений или, в крайнем случае, `catch (Exception e)`. `catch (Throwable)` — только на границах компонентов (точка входа потока, верхний уровень задачи), и всегда с явной обработкой `Error`-случая.
### Вопрос 17. Что означает понятие «re-throw» (повторное выбрасывание исключения)? Сохраняется ли при этом исходный stack trace?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Rethrowing Exceptions in Java — javaplanet.io](https://javaplanet.io/java-core/java-exception-handling/rethrowing-exceptions/)

Re-throw (повторное выбрасывание) — это техника, при которой исключение перехватывается в блоке `catch`, а затем выбрасывается снова. Это полезно, когда нужно частично обработать исключение (например, залогировать) и при этом позволить ему распространяться вверх по стеку вызовов. При простом `throw e;` исходный stack trace сохраняется. Однако вызов `e.fillInStackTrace()` перезаписывает трассировку: новой точкой происхождения становится место повторного выбрасывания, а не исходная ошибка. Если же в блоке `catch` создаётся и бросается совершенно новое исключение — исходный stack trace теряется полностью.

#### Ответ от Claude

**Re-throw** — это техника обработки исключений, при которой исключение перехватывается в блоке `catch`, но не поглощается, а выбрасывается снова с помощью ключевого слова `throw`. Применяется, когда нужно выполнить промежуточное действие (логирование, очистка ресурсов) и передать исключение обработчику более высокого уровня.

**Три сценария и поведение stack trace:**

1. **`throw e;` — повтор того же объекта.**
   Stack trace полностью сохраняется: он был сформирован в момент создания исключения (`new SomeException(...)`) и не изменяется при последующих `throw`.
   ```java
   try {
       riskyOperation();
   } catch (IOException e) {
       log.warn("Ошибка при операции", e);
       throw e; // stack trace указывает на riskyOperation(), а не сюда
   }
   ```

2. **`throw new WrapperException("context", e);` — обёртка (wrapping) с сохранением причины.**
   Создаётся новый объект исключения, у которого будет *новый* stack trace (начиная с места `throw new`). Исходное исключение передаётся как `cause`, поэтому при выводе через `printStackTrace()` будет видна вся цепочка: `Caused by: ...`. Stack trace оригинальной ошибки **не теряется**, но к нему добавляется новый контекст.

3. **`throw new OtherException("msg");` — выброс нового без cause.**
   Исходный stack trace **теряется полностью**. Новое исключение не знает об исходном. Это наиболее опасный вариант, которого следует избегать.

**Особый случай — `fillInStackTrace()`.**
Метод `fillInStackTrace()` (унаследованный от `Throwable`) перезаписывает трассировку в уже существующем объекте исключения, делая точкой происхождения место повторного выброса:
```java
throw (IOException) e.fillInStackTrace(); // stack trace теперь указывает СЮДА
```
Это нестандартный приём; в production-коде используется редко.

**Вывод:**
- `throw e` → stack trace исходный (рекомендуется при простом re-throw).
- `throw new Wrapper(msg, e)` → новый trace + исходный как `cause` (рекомендуется при смене типа или добавлении контекста).
- `throw new Exception(msg)` без cause → исходный trace потерян (антипаттерн).
- `throw (T) e.fillInStackTrace()` → trace перезаписан на текущее место (специальный сценарий).

---

### Вопрос 18. Почему не рекомендуется использовать исключения для управления потоком выполнения (control flow)?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Avoid exceptions for control flow — the performance argument (berrueta.net)](https://berrueta.net/software/2024/09/10/exceptions-performance.html)

Статья демонстрирует измеримые потери производительности при использовании исключений для управления потоком. В тесте, который вызывал метод 10 миллионов раз, подход на основе исключений занял **4 400 мс**, вариант с регулярным выражением — **620 мс** (в 7 раз быстрее), а вариант с `NumberUtils.isNumeric` — **30 мс** (в 146 раз быстрее). Причины замедления: создание исключения требует захвата полного стека вызовов, что дорогостояще само по себе; кроме того, непредсказуемый поток выполнения не позволяет JVM и процессору применять оптимизации (branch prediction, JIT-оптимизации). Вывод: исключения предназначены для по-настоящему исключительных ситуаций; для стандартной логики (например, валидации пользовательского ввода) следует использовать условные проверки.

#### Ответ от Claude

Использование исключений для управления потоком выполнения — признанный антипаттерн, зафиксированный в книге Джошуа Блоха «Effective Java» (Item 69: «Use exceptions only for exceptional conditions»). Причины:

**1. Производительность.**
Когда JVM создаёт объект исключения, она захватывает полный снимок стека вызовов (`fillInStackTrace()`). Это значительно дороже, чем простая проверка `if/else` или вызов вспомогательного метода. Сравнительные бенчмарки показывают разницу в десятки и сотни раз (примеры: 4 400 мс против 30 мс на 10 млн итераций). Исключения также нарушают предсказуемость потока, из-за чего JIT-компилятор и процессор не могут эффективно применять оптимизации.

**2. Читаемость и ясность намерений.**
Исключения несут семантику «что-то пошло не так». Если исключение используется для обычной логики — например, выход из цикла или сигнал об отсутствии элемента — это скрывает намерение автора от читателя кода. Из сигнатуры метода не видно, что бросание исключения является частью нормального сценария.

**3. Хрупкость (brittleness).**
Код, полагающийся на исключения в нормальном потоке, легко сломать: добавление нового метода в иерархию вызовов может неожиданно изменить поведение, если он тоже бросает исключение того же типа.

**4. Нарушение принципа наименьшего удивления.**
Разработчики, читающие код, ожидают, что `catch`-блоки обрабатывают ошибки. Когда `catch` является частью обычной логики, это вводит в заблуждение и затрудняет отладку.

**Правильная альтернатива:**
- Использовать `if`-проверки для предсказуемых ситуаций (пустой список, `null`, невалидный ввод).
- Применять методы-предикаты (`contains()`, `isPresent()`, `isEmpty()`).
- Использовать `Optional<T>` для явного представления отсутствия значения.

Исключения должны использоваться исключительно для ситуаций, которые: а) не являются частью нормального потока, б) трудно предсказать заранее, в) действительно требуют особой обработки.

---

### Вопрос 19. Как правильно логировать исключения, чтобы не потерять stack trace? Какие ошибки чаще всего допускают при логировании?

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Enhances logging of exceptions by including the full stack trace — OpenRewrite Docs](https://docs.openrewrite.org/recipes/java/logging/slf4j/completeexceptionlogging)

Документация OpenRewrite описывает типичную ошибку: вызов `Exception.getMessage()` при передаче исключения в метод логирования. Как сказано в документации: *«Not all exception types have useful messages, and even if the message is useful this omits the stack trace»*. Неправильный вариант — `logger.error(e.getMessage())` — захватывает только текстовое сообщение, теряя трассировку стека. Правильный — `logger.error("msg", e)` — передаёт объект исключения последним аргументом, и фреймворк логирования самостоятельно выводит полный stack trace. Рецепт CompleteExceptionLogging автоматически исправляет этот антипаттерн, обнаруживая вызовы `getMessage()` / `getLocalizedMessage()` без объекта исключения.

#### Ответ от Claude

**Правильное логирование исключений** — передавать объект исключения последним аргументом метода логирования. Все популярные фреймворки (SLF4J, Log4j 2, java.util.logging) обнаруживают исключение в этой позиции и автоматически выводят полный stack trace.

**Правильные паттерны:**

```java
// SLF4J — рекомендуемый фасад
logger.error("Ошибка при обработке запроса: {}", requestId, e);

// Log4j 2
logger.error("Операция завершилась неудачей", e);

// java.util.logging
logger.log(Level.SEVERE, "Критическая ошибка", e);
```

**Частые ошибки при логировании:**

1. **Логирование только сообщения вместо исключения.**
   ```java
   // ПЛОХО — stack trace теряется навсегда
   logger.error(e.getMessage());
   logger.error("Ошибка: " + e.getMessage());
   ```
   Не у всех исключений есть информативное сообщение (например, `NullPointerException` часто возвращает `null`). Без стека невозможно понять, где именно возникла ошибка.

2. **Вызов `e.printStackTrace()` вместо логгера.**
   ```java
   // ПЛОХО — выводит в System.err, игнорирует конфигурацию логирования
   e.printStackTrace();
   ```
   Вывод попадает в stderr, а не в лог-файлы, и не несёт метаданных (уровень, время, имя потока).

3. **Двойное логирование (duplicate logging).**
   ```java
   // ПЛОХО — исключение будет залогировано дважды
   logger.error("Ошибка", e);
   throw e; // и будет поймано и залогировано выше
   ```
   Это засоряет логи повторяющимися записями. Логировать нужно в одном месте — либо там, где обрабатываете, либо там, где пробрасываете.

4. **Поглощение исключения (swallowing).**
   ```java
   // ПЛОХО — исключение полностью скрыто
   try { ... } catch (Exception e) { /* ничего */ }
   ```

5. **Потеря cause при создании нового исключения.**
   ```java
   // ПЛОХО — исходный stack trace уничтожен
   throw new ServiceException("Ошибка");
   // ХОРОШО — исходная причина сохранена
   throw new ServiceException("Ошибка", e);
   ```

6. **Использование неподходящего уровня логирования.** `ERROR` для бизнес-валидации или `DEBUG` для критических системных ошибок — оба варианта затрудняют мониторинг.

**Итоговые рекомендации:**
- Всегда передавать объект исключения последним аргументом: `logger.error("сообщение", e)`.
- Использовать SLF4J как фасад для независимости от реализации.
- Не логировать и не выбрасывать одновременно — выбрать одно место.
- Добавлять контекст (идентификатор операции, пользователя, входные данные).
- Не использовать `e.getMessage()` как замену полному исключению.

---

### Вопрос 20. Опишите иерархию Throwable. Чем Error отличается от Exception, и почему не рекомендуется перехватывать Error?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Throwable (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/lang/Throwable.html)

Официальная документация Oracle: класс `Throwable` — суперкласс всех ошибок и исключений в Java. Только объекты, являющиеся экземплярами `Throwable` или его подклассов, могут быть выброшены JVM или перехвачены в блоке `catch`. `Throwable` содержит снимок стека выполнения на момент создания, строку с детальным сообщением, причину (другой `Throwable`), что обеспечивает цепочку исключений, а также подавленные исключения (из конструкций try-with-resources). Метод `fillInStackTrace()` записывает текущие фреймы стека в объект; он автоматически вызывается конструкторами. Метод `initCause()` позволяет установить причину и может быть вызван только один раз. Класс `Error` обозначает серьёзные проблемы, которые «reasonable application should not try to catch» — это сбои на уровне JVM. `Exception` обозначает условия, которые «a reasonable application might want to catch».

#### Ответ от Claude

**Иерархия Throwable:**

```
java.lang.Object
    └── java.lang.Throwable
            ├── java.lang.Error
            │       ├── OutOfMemoryError
            │       ├── StackOverflowError
            │       ├── VirtualMachineError
            │       └── AssertionError
            └── java.lang.Exception
                    ├── IOException          ← checked
                    ├── SQLException         ← checked
                    ├── ClassNotFoundException ← checked
                    └── RuntimeException     ← unchecked
                            ├── NullPointerException
                            ├── IllegalArgumentException
                            ├── ArrayIndexOutOfBoundsException
                            └── ClassCastException
```

**Throwable** — корень иерархии. Содержит:
- снимок стека вызовов на момент создания,
- опциональное текстовое сообщение (`getMessage()`),
- опциональную причину (`getCause()`) для цепочки исключений,
- подавленные исключения (`getSuppressed()`, используются в try-with-resources).

**Exception** — исключения, которые приложение должно обрабатывать. Делятся на два вида:
- **Checked** (проверяемые): прямые наследники `Exception`, кроме `RuntimeException`. Компилятор требует их явной обработки (`try/catch` или `throws`). Примеры: `IOException`, `SQLException`.
- **Unchecked** (непроверяемые): наследники `RuntimeException`. Не требуют объявления. Обычно сигнализируют об ошибках программирования. Примеры: `NullPointerException`, `IllegalArgumentException`.

**Error** — ошибки уровня JVM, которые приложение, как правило, не может исправить:
- `OutOfMemoryError` — JVM не может выделить память.
- `StackOverflowError` — переполнение стека (бесконечная рекурсия).
- `VirtualMachineError` — сбой самой виртуальной машины.
- `AssertionError` — нарушение утверждения (`assert`).

Все `Error` являются unchecked: компилятор не требует их обработки.

**Почему не следует перехватывать Error:**

1. **Нет смысла**: `OutOfMemoryError` означает, что JVM не может выделить память. Попытка продолжить работу почти наверняка завершится следующим `OOM` или непредсказуемым поведением.

2. **Маскировка критических проблем**: перехват `Error` скрывает системные сбои вместо того, чтобы дать им завершить программу и попасть в мониторинг.

3. **Ненадёжность catch-блока при OOM**: сам блок `catch` при `OutOfMemoryError` может не выполниться из-за нехватки памяти для создания новых объектов.

4. **Ошибочная диагностика**: если `StackOverflowError` поглощён, первопричина (бесконечная рекурсия) остаётся незамеченной.

**Правило на практике:**
- `catch (Exception e)` — допустимо в точках верхнего уровня (контроллеры, обработчики запросов).
- `catch (Throwable t)` — только в самых верхних уровнях фреймворков (thread uncaught exception handler, `main`) и только для логирования перед завершением.
- `catch (Error e)` — практически никогда не следует использовать в прикладном коде.
