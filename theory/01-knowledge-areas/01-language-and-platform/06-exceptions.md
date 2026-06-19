# Исключения и обработка ошибок

> **Уровень:** Junior / Middle
> **Связанные вопросы:** [Вопросы по исключениям →](../interview-questions/core-java/exceptions-01.md)
> **Связанные области:** [[01-core-java-syntax-oop]], [[07-io-nio]]

## Что это и зачем

Механизм исключений — стандартный способ обработки ошибочных и нештатных ситуаций в Java.
Нужно понимать иерархию исключений, различие проверяемых и непроверяемых исключений, корректное
использование `try`/`catch`/`finally` и `try-with-resources`, а также практики проектирования
надёжного кода (не «глотать» исключения, осмысленно оборачивать и логировать).

Исключение (exception) — это событие, возникающее во время выполнения программы и нарушающее
нормальный ход выполнения инструкций. Когда ошибка происходит внутри метода, он создаёт объект
исключения и передаёт его среде выполнения — это называется «выбросить исключение» (throw).
Runtime ищет подходящий обработчик, двигаясь назад по стеку вызовов (call stack). Если
обработчик не найден, программа завершается с выводом stack trace.

Исключения дают три ключевых преимущества перед традиционными кодами возврата:
отделение кода обработки ошибок от основной логики, автоматическое распространение ошибки вверх
по стеку через промежуточные методы, иерархическая группировка типов ошибок.

## Ключевые подтемы

### Иерархия Throwable

Корень иерархии — класс `java.lang.Throwable`, реализующий `Serializable`. От него
наследуются два ветви:

```
Object
  └── Throwable
      ├── Error
      │     ├── OutOfMemoryError
      │     ├── StackOverflowError
      │     └── AssertionError
      └── Exception
            ├── IOException
            ├── SQLException
            ├── CloneNotSupportedException
            └── RuntimeException
                  ├── NullPointerException
                  ├── IllegalArgumentException
                  ├── IndexOutOfBoundsException
                  └── ClassCastException
```

**`Error`** — серьёзные системные ошибки, от которых приложение, как правило, не может
восстановиться (нехватка памяти, переполнение стека, ошибки JVM). Ловить `Error` допустимо
только в редких случаях — например, чтобы аккуратно завершить работу и уведомить пользователя.

**`Exception`** — ошибки, с которыми приложение может и должно работать. Делятся на два
подвида (см. следующий раздел).

Ключевые методы `Throwable`, актуальные для всех потомков:

| Метод | Описание |
|---|---|
| `String getMessage()` | Детальное сообщение об ошибке |
| `String toString()` | Короткое описание: `ClassName: message` |
| `void printStackTrace()` | Печатает стек вызовов в stderr |
| `StackTraceElement[] getStackTrace()` | Программный доступ к стеку |
| `Throwable getCause()` | Исключение-причина (или `null`) |
| `Throwable initCause(Throwable)` | Устанавливает причину (однократно) |
| `Throwable[] getSuppressed()` | Подавленные исключения (см. try-with-resources) |

Источник: [Javadoc Throwable (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Throwable.html)

---

### Checked vs Unchecked исключения

Oracle делит все исключения на три категории по принципу «Catch or Specify Requirement»
([официальный раздел](https://docs.oracle.com/javase/tutorial/essential/exceptions/catchOrDeclare.html)):

| Категория | Базовый класс | Нужна обработка? | Типичные примеры |
|---|---|---|---|
| Checked exception | `Exception` (не `RuntimeException`) | Да — компилятор требует | `IOException`, `SQLException`, `FileNotFoundException` |
| Unchecked exception | `RuntimeException` | Нет | `NullPointerException`, `IllegalArgumentException`, `ArrayIndexOutOfBoundsException` |
| Error | `Error` | Нет | `OutOfMemoryError`, `StackOverflowError` |

**Правило выбора** (из официальной документации Oracle):
> «If a client can reasonably be expected to recover from an exception, make it a checked
> exception. If a client cannot do anything to recover from the exception, make it an
> unchecked exception.»

Иными словами: checked исключение сигнализирует, что вызывающий код должен явно принять
решение об обработке; unchecked — что произошла ошибка программиста или неустранимое условие.

**Чего не стоит делать:** Oracle прямо предостерегает от использования `RuntimeException`
только для того, чтобы не писать `throws` в сигнатуре метода. Это нарушает контракт API
и лишает клиентов информации о возможных исключениях.

---

### try / catch / finally — синтаксис и правила

Официальный туториал: [Catching and Handling Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/handling.html)

#### Базовый синтаксис

```java
try {
    // код, который может выбросить исключение
} catch (IOException e) {
    // обработчик IOException
} catch (Exception e) {
    // обработчик всех остальных Exception
} finally {
    // выполняется в любом случае
}
```

**Порядок catch-блоков важен:** более специфичные типы должны идти перед более общими.
Если расположить `catch (Exception e)` первым, компилятор сообщит об ошибке — нижние блоки
никогда не будут достигнуты (`unreachable catch block`).

#### Multi-catch (Java 7+)

Один `catch`-блок может перехватывать несколько не связанных иерархией типов:

```java
try {
    // ...
} catch (IOException | SQLException ex) {
    logger.log(ex);
    throw ex;
}
```

Важный нюанс: переменная `ex` в multi-catch неявно становится `final` — переприсвоить её
нельзя. Это позволяет компилятору точно отследить типы при повторном выбросе (`rethrow`).

#### finally — гарантированное выполнение

Блок `finally` выполняется **при любом** способе выхода из `try`: нормальном завершении,
выбросе исключения, выполнении `return`, `break`, `continue`. Исключение — аварийное
завершение JVM (`System.exit()`, аппаратный сбой).

```java
try {
    return doSomething(); // finally выполнится даже здесь
} finally {
    cleanup();            // всегда
}
```

**Ловушка:** если `finally` сам выбрасывает исключение или содержит `return`, исходное
исключение из `try` теряется. Именно поэтому Oracle рекомендует использовать
`try-with-resources` вместо ручного закрытия ресурсов в `finally`.

---

### try-with-resources и AutoCloseable

Источник: [The try-with-resources Statement](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)

Введён в Java 7. Позволяет автоматически закрывать ресурсы, реализующие
`java.lang.AutoCloseable` (и его подинтерфейс `java.io.Closeable`).

#### Синтаксис

```java
try (ResourceType res1 = new ResourceType();
     ResourceType res2 = new ResourceType()) {
    // работа с ресурсами
} catch (IOException e) {
    // опционально
} finally {
    // опционально
}
```

После блока `try` все ресурсы закрываются **в порядке, обратном объявлению**: последний
открытый закрывается первым. `catch` и `finally` выполняются уже после закрытия ресурсов.

#### Пример: чтение файла

```java
static String readFirstLine(String path) throws IOException {
    try (FileReader fr = new FileReader(path);
         BufferedReader br = new BufferedReader(fr)) {
        return br.readLine();
    }
    // br и fr закроются автоматически
}
```

#### Подавленные исключения (Suppressed Exceptions)

Если в блоке `try` возникло исключение, а при закрытии ресурса — ещё одно, первичным
считается исключение из `try`. Исключение из `close()` не теряется — оно добавляется как
«подавленное» и доступно через `Throwable.getSuppressed()`:

```java
try {
    // ...
} catch (Exception e) {
    Throwable[] suppressed = e.getSuppressed();
    for (Throwable t : suppressed) {
        System.err.println("Suppressed: " + t);
    }
}
```

До Java 7 при использовании `finally` вторичное исключение из `close()` полностью
затирало первичное — это была распространённая ловушка.

#### Пользовательский AutoCloseable

```java
public class DatabaseConnection implements AutoCloseable {
    public DatabaseConnection(String url) { /* открыть соединение */ }

    @Override
    public void close() throws Exception {
        // закрыть соединение
    }
}

try (DatabaseConnection conn = new DatabaseConnection(url)) {
    conn.query("SELECT 1");
}
```

---

### throw и throws

Источник: [How to Throw Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/throwing.html)

| | `throw` | `throws` |
|---|---|---|
| Место использования | Тело метода | Сигнатура метода |
| Назначение | Явно выбросить исключение | Объявить, что метод может выбросить checked-исключение |
| Тип | Любой `Throwable` | Только checked-исключения (unchecked можно, но не обязательно) |

```java
// throw — выбросить исключение немедленно
public Object pop() {
    if (size == 0) {
        throw new EmptyStackException();
    }
    // ...
}

// throws — объявить возможное checked-исключение
public void readFile(String path) throws IOException {
    // ...
}
```

Для `RuntimeException` и его потомков `throws` в сигнатуре не требуется, хотя добавить
его для документирования допустимо.

---

### Chained Exceptions (цепочки исключений)

Источник: [Chained Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/chained.html)

Позволяет сохранить первопричину при оборачивании исключений, что критически важно для
диагностики. Без цепочки оригинальный stack trace теряется.

Конструкторы `Throwable` с поддержкой причины:

```java
Throwable(Throwable cause)
Throwable(String message, Throwable cause)
```

Метод `initCause(Throwable)` позволяет установить причину для исключений, у которых
нет соответствующего конструктора, но вызвать его можно **только один раз**.

```java
try {
    readConfigFile();
} catch (IOException e) {
    // Оборачиваем IOException в бизнес-исключение, сохраняя причину
    throw new ConfigurationException("Не удалось загрузить конфигурацию", e);
}

// При выводе стека видно:
// ConfigurationException: Не удалось загрузить конфигурацию
//     at ...
// Caused by: java.io.FileNotFoundException: config.properties (No such file or directory)
//     at ...
```

**Антипаттерн** — потеря причины:
```java
// ПЛОХО: первопричина потеряна
catch (IOException e) {
    throw new ConfigurationException("Ошибка");  // e не передан!
}
```

---

### Создание собственных исключений

Источник: [Creating Exception Classes](https://docs.oracle.com/javase/tutorial/essential/exceptions/creating.html)

Собственный класс исключения стоит создавать, если:
- в стандартной библиотеке нет подходящего типа;
- нужно отличить ваши исключения от чужих;
- требуется выбрасывать несколько связанных типов исключений;
- пользователи пакета должны иметь возможность обрабатывать их независимо.

**Рекомендации Oracle:**
- Расширяйте `Exception` (а не `Error`) для исключений приложения.
- Давайте имена с суффиксом `Exception`: `PaymentException`, `UserNotFoundException`.
- Предоставляйте как минимум два конструктора: без аргументов и с `(String message, Throwable cause)`.

```java
public class InsufficientFundsException extends Exception {

    private final double amount;

    public InsufficientFundsException(double amount) {
        super("Недостаточно средств: требуется " + amount);
        this.amount = amount;
    }

    public InsufficientFundsException(String message, Throwable cause) {
        super(message, cause);
        this.amount = 0;
    }

    public double getAmount() {
        return amount;
    }
}
```

Иерархия для связанных исключений:

```
PaymentException (extends Exception)
  ├── InsufficientFundsException
  ├── CardExpiredException
  └── PaymentDeclinedException
```

Такая структура позволяет ловить либо конкретный тип, либо всю группу одним `catch (PaymentException e)`.

---

### Хорошие практики

**1. Не «глотать» исключения**

```java
// ПЛОХО: исключение скрыто, ошибка не видна
try {
    process();
} catch (Exception e) {
    // ничего
}

// ХОРОШО: минимум — залогировать
try {
    process();
} catch (Exception e) {
    logger.error("Ошибка при обработке", e);
    throw e; // или обработать
}
```

**2. Не использовать исключения для управления потоком**

Исключения дорого стоят (заполнение stack trace при создании). Код вида
`try { Integer.parseInt(s) } catch (NumberFormatException e) { ... }` для проверки
каждого элемента в цикле из миллиона строк нагружает GC и замедляет программу.
Вместо этого используйте предварительные проверки (`if`, регулярные выражения).

**3. Перехватывать максимально конкретный тип**

Широкий `catch (Exception e)` затрудняет отладку и может случайно поглотить
`InterruptedException`, нарушив работу многопоточного кода.

**4. Всегда передавать cause при оборачивании**

```java
throw new ServiceException("Ошибка сервиса", originalException); // не потерять причину
```

**5. Документировать через `@throws` в Javadoc**

```java
/**
 * Читает пользователя по идентификатору.
 *
 * @throws UserNotFoundException если пользователь не найден
 * @throws DatabaseException     при ошибке доступа к БД
 */
User findUser(long id) throws UserNotFoundException, DatabaseException;
```

**6. Не объявлять `throws Exception` или `throws Throwable`** в публичном API — это
лишает клиентов возможности точечно обработать исключения.

---

## Достоверные источники

1. **[The Java Tutorials — Exceptions (Oracle)](https://docs.oracle.com/javase/tutorial/essential/exceptions/index.html)**
   Официальный учебник Oracle. Охватывает все аспекты: иерархию, checked/unchecked,
   try/catch/finally, try-with-resources, chained exceptions, создание собственных классов.
   Первичный источник — всё остальное вторично.

2. **[Javadoc: java.lang.Throwable (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Throwable.html)**
   Спецификация корневого класса иерархии. Точные сигнатуры методов, контракты, описание
   suppressed exceptions. Актуально для Java 21 LTS.

3. **[JLS §11 — Exceptions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-11.html)**
   Java Language Specification — формальное определение семантики исключений, checked/unchecked
   разделения, правил `throws`. Необходим для понимания граничных случаев.

4. **[Baeldung — Exception Handling in Java](https://www.baeldung.com/java-exceptions)**
   Авторитетный ресурс с практическими примерами. Хорошо дополняет официальную документацию
   разбором типичных сценариев и антипаттернов.

5. **[Jenkov — Java Exception Handling](https://jenkov.com/tutorials/java-exception-handling/index.html)**
   Системный разбор механизма от простого к сложному. Полезен для Junior-разработчиков:
   понятный язык, много примеров кода.

6. **Книга «Effective Java» (Joshua Bloch, 3-е издание), глава 10 «Exceptions»**
   Содержит 9 пунктов-рекомендаций по проектированию API с исключениями (Items 69–77):
   когда использовать checked vs unchecked, как документировать, как избегать ошибок.
   Признана стандартом отрасли; Bloch — бывший главный архитектор Java в Sun/Google.
