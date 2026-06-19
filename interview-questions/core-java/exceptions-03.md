# Исключения (checked/unchecked, try-with-resources) — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../../theory/01-knowledge-areas/01-language-and-platform/06-exceptions.md](../../theory/01-knowledge-areas/01-language-and-platform/06-exceptions.md)
> Правила: [../RULES.md](../RULES.md)
> Части: [ч.1](exceptions-01.md) · [ч.2](exceptions-02.md) · **ч.3**

---
### Вопрос 41. Что такое «exception translation» (трансляция исключений) и «exception abstraction»? Как этот паттерн применяется в многоуровневой архитектуре (Repository → Service → Controller)? Какой механизм использует Spring @Repository для автоматической трансляции?

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Effective Java: Throw Exceptions Appropriate To The Abstraction — DEV Community](https://dev.to/kylec32/effective-java-throw-exceptions-appropriate-to-the-abstraction-1d4e)

**Exception translation** — это практика перехвата исключений нижнего уровня и оборачивания их в исключения более высокого уровня, соответствующие текущей абстракции. Основная мотивация — не допустить утечки деталей реализации в публичный API, что ограничивало бы возможность рефакторинга внутреннего кода.

**Exception abstraction** — принцип (Item 73 в Effective Java Джошуа Блоха: «Throw exceptions appropriate to the abstraction»): каждый слой должен выбрасывать исключения, понятные в контексте его собственной абстракции, а не исключения, специфичные для слоя ниже.

Пример: `AbstractSequentialList.get()` перехватывает `NoSuchElementException` (детали реализации итератора) и перебрасывает `IndexOutOfBoundsException` (язык List-абстракции):

```java
try {
    return i.next();
} catch (NoSuchElementException e) {
    throw new IndexOutOfBoundsException("Index: " + index);
}
```

**Exception chaining** — расширенный вариант: оригинальное исключение передаётся как cause, чтобы не потерять контекст для диагностики:

```java
try {
    // нижний уровень
} catch (LowerLevelException cause) {
    throw new HigherLevelException("...", cause);
}
```

В многоуровневой архитектуре это означает:
- Repository ловит `SQLException` / `PersistenceException` и перебрасывает `DataAccessException`
- Service ловит `DataAccessException` и перебрасывает доменное исключение (`OrderNotFoundException`, `PaymentFailedException`)
- Controller ловит доменное исключение и отвечает нужным HTTP-статусом

#### Ответ от Claude

**Exception translation (трансляция исключений)** — паттерн, при котором исключение, выброшенное на одном уровне архитектуры, перехватывается и заменяется исключением, семантически подходящим для уровня выше. Это одно из проявлений принципа **exception abstraction**: каждый слой «говорит» на языке собственной предметной области, не обнажая технические детали реализации нижних слоёв.

Источник принципа — Effective Java, Item 73 (Joshua Bloch): «Higher layers should catch lower-level exceptions and, in their place, throw exceptions that can be explained in terms of the higher-level abstraction».

**Применение в многоуровневой архитектуре:**

```
Repository
  └─ ловит: SQLException, PersistenceException, HibernateException
  └─ бросает: DataAccessException (или своё доменное DataNotFoundException)

Service
  └─ ловит: DataAccessException / доменные исключения Repository
  └─ бросает: OrderNotFoundException, UserAlreadyExistsException и т.п.

Controller / @ExceptionHandler
  └─ ловит: доменные исключения Service
  └─ отдаёт: HTTP 404, 409, 500 и т.д.
```

Каждый слой прячет внутреннюю реализацию: Service не знает, что под ним JPA или JDBC; Controller не знает, что под ним конкретный ORM.

**Механизм Spring `@Repository`:**

Spring автоматизирует трансляцию для слоя Repository через два компонента:

1. **`PersistenceExceptionTranslationPostProcessor`** — `BeanPostProcessor`, который сканирует все бины, аннотированные `@Repository`, и оборачивает их AOP-прокси с `PersistenceExceptionTranslationAdvisor`.
2. **`PersistenceExceptionTranslator`** — интерфейс, реализованный всеми фабриками ресурсов Spring (например, `LocalContainerEntityManagerFactoryBean`). Именно он содержит логику перевода нативных исключений JPA/Hibernate/JDBC в иерархию `DataAccessException`.

Когда метод репозитория выбрасывает нативное исключение (например, `javax.persistence.PersistenceException`), AOP-перехватчик вызывает зарегистрированные `PersistenceExceptionTranslator`-бины, которые переводят исключение в соответствующий подкласс `DataAccessException` (например, `DataIntegrityViolationException`).

В Spring Boot `PersistenceExceptionTranslationPostProcessor` регистрируется автоматически через `PersistenceExceptionTranslationAutoConfiguration` — явно объявлять его bean не нужно.

```java
@Repository
public class UserRepository {
    @PersistenceContext
    private EntityManager em;

    public User findById(Long id) {
        // JPA-исключение будет автоматически транслировано в DataAccessException
        return em.find(User.class, id);
    }
}
```

**Расхождений между источниками не выявлено.** Все источники (Effective Java, Spring Javadoc, Spring Reference) согласованы: `@Repository` активирует AOP-трансляцию через `PersistenceExceptionTranslationPostProcessor`.

---

### Вопрос 42. Что изменилось в сообщениях NullPointerException начиная с Java 14 (JEP 358)? Что именно теперь содержит сообщение NPE и в какой версии JDK эта функциональность стала включённой по умолчанию?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [JEP 358: Helpful NullPointerExceptions — OpenJDK](https://openjdk.org/jeps/358)

JEP 358 улучшает удобство отладки `NullPointerException`, генерируемых JVM: теперь сообщение об ошибке точно описывает, какая именно переменная или выражение оказалось `null`.

JVM анализирует байткод инструкции, вызвавшей NPE, и формирует null-detail message. Сообщение включает:
- что пытались сделать («Cannot invoke», «Cannot read field», «Cannot store to array» и т.п.);
- почему операция не выполнима — какая именно переменная или возвращаемое значение было `null`.

Примеры сообщений:
- `Cannot invoke "String.length()" because "<local1>" is null`
- `Cannot read field "c" because "a.b" is null`
- `Cannot store to int array because "ia" is null`
- `Cannot invoke "Object.hashCode()" because the return value of "java.util.List.get(int)" is null`

В JDK 14 функциональность была введена, но отключена по умолчанию; для её активации требовался флаг `-XX:+ShowCodeDetailsInExceptionMessages`.

#### Ответ от Claude

**До JEP 358** (Java 13 и ранее) `NullPointerException` содержала пустое сообщение (`getMessage()` возвращало `null`) или лишь указание на строку в стектрейсе — никакой информации о том, какое именно выражение было `null`.

**С JEP 358 (Java 14+)** JVM анализирует байткод инструкции, вызвавшей NPE, и добавляет к исключению текстовое сообщение с двумя элементами:
1. **Что не удалось сделать** — в форме «Cannot invoke ...», «Cannot read field ...», «Cannot load from ... array», «Cannot throw exception», «Cannot enter synchronized block», «Cannot unbox»;
2. **Почему** — какая переменная, поле или возвращаемое значение метода оказалось `null`.

Примеры сообщений:
```
Cannot invoke "String.length()" because "str" is null
Cannot read field "name" because "user" is null
Cannot invoke "Object.hashCode()" because the return value of "java.util.List.get(int)" is null
Cannot store to int array because "numbers" is null
```

Если код скомпилирован без отладочной информации (`javac` без флага `-g`), вместо имён локальных переменных JVM подставляет синтетические имена вида `<local0>`, `<local1>`.

**Хронология включения по умолчанию:**

| JDK | Статус |
|-----|--------|
| Java 14 | Введено (JEP 358), но **отключено по умолчанию**; требовался флаг `-XX:+ShowCodeDetailsInExceptionMessages` |
| **Java 15** | Флаг `ShowCodeDetailsInExceptionMessages` **изменён на `true` по умолчанию** (JDK-8233014); подробные сообщения NPE печатаются автоматически |

Начиная с Java 15 флаг можно явно отключить: `-XX:-ShowCodeDetailsInExceptionMessages` (актуально, например, если сообщение NPE может раскрывать чувствительные данные во внешних error-ответах).

**Расхождений между источниками не выявлено.** OpenJDK JEP 358, Oracle Release Notes JDK 15 и независимые публикации (Marx Software, Java Code Geeks) единогласно называют JDK 15 версией, в которой функция стала включённой по умолчанию.

---

### Вопрос 43. Что изменилось в синтаксисе try-with-resources в Java 9? Что означает понятие effectively final применительно к ресурсу, объявленному вне блока try-with-resources?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Try with Resources — Oracle Java SE 13 Language Guide](https://docs.oracle.com/en/java/javase/13/language/try-resources.html)

До Java 9 ресурс, который должен был автоматически закрываться, **обязательно объявлялся внутри** скобок оператора `try`. Если ресурс был создан заранее, приходилось вводить дополнительную переменную-обёртку:

```java
// Java 7-8: требовалась лишняя переменная
final Resource resource1 = new Resource("resource1");
Resource resource2 = new Resource("resource2");

try (Resource r1 = resource1;
     Resource r2 = resource2) {
    // ...
}
```

Начиная с Java 9, можно использовать уже объявленную переменную напрямую, если она является `final` или **effectively final**:

```java
// Java 9+: переменные используются напрямую
final Resource resource1 = new Resource("resource1");
Resource resource2 = new Resource("resource2");

try (resource1; resource2) {
    // ...
}
```

Переменная является **effectively final**, если её значение не изменяется после первого присвоения, даже при отсутствии явного ключевого слова `final`.

#### Ответ от Claude

**До Java 9 (Java 7–8):**

Спецификация требовала, чтобы ресурс в `try`-with-resources был объявлен непосредственно в заголовке блока. Даже если объект уже существовал в переменной, нужна была повторная локальная переменная:

```java
BufferedReader br = new BufferedReader(new FileReader(file));
try (BufferedReader reader = br) {  // обязательная "лишняя" переменная
    String line = reader.readLine();
}
```

**С Java 9:**

Синтаксис расширен: в скобках `try` допускается указывать ссылку на **уже объявленную** переменную без повторного её объявления — при условии, что переменная является `final` или **effectively final**:

```java
BufferedReader br = new BufferedReader(new FileReader(file));
try (br) {  // напрямую — без лишней переменной
    String line = br.readLine();
}
```

Несколько ресурсов через точку с запятой:

```java
DatagramChannel udpServer = DatagramChannel.open().bind(port);
Selector selector = Selector.open();
try (udpServer; selector) {
    // ...
}
```

**Понятие effectively final применительно к ресурсу вне try:**

Переменная считается **effectively final**, если:
- она не объявлена с явным ключевым словом `final`, но
- ей ни разу не присваивается новое значение после инициализации.

Это те же правила, которые действуют для переменных, захватываемых в лямбдах и анонимных классах (JLS §4.12.4). Компилятор проверяет это статически: если переменная переприсваивается где-либо в коде между объявлением и использованием в `try`, компиляция завершится ошибкой.

```java
BufferedReader br = new BufferedReader(new FileReader("a.txt"));
// br = new BufferedReader(new FileReader("b.txt")); // если раскомментировать — ошибка компиляции
try (br) {
    // br effectively final — компилируется
}
```

**Семантика закрытия не изменилась:** ресурс всё так же закрывается в блоке `finally`, сгенерированном компилятором, при выходе из `try` — как при нормальном завершении, так и при исключении. Нет риска того, что внешняя переменная будет переиспользована после закрытия: компилятор запрещает присваивание effectively-final-переменной внутри блока `try`.

**Расхождений между источниками не выявлено.** Oracle Java SE 13 Language Guide, Jenkov.com, GeeksForGeeks и Tutorialspoint описывают изменение одинаково: Java 9 позволяет использовать final и effectively final переменные, объявленные вне блока, напрямую в заголовке try-with-resources.

---
### Вопрос 44. Как правильно обрабатывать InterruptedException? Почему запрещено просто поглощать это исключение в пустом catch-блоке? Что означает «восстановить флаг прерывания»?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Interrupts — The Java Tutorials (docs.oracle.com)](https://docs.oracle.com/javase/tutorial/essential/concurrency/interrupt.html)

Прерывание — это сигнал потоку о том, что ему следует остановить выполнение текущей работы и переключиться на другую задачу. Механизм прерывания реализован через внутренний флаг, называемый **interrupt status** (статус прерывания):

- `Thread.interrupt()` — устанавливает флаг прерывания.
- `Thread.interrupted()` (статический) — возвращает `true`, если поток прерван, и **сбрасывает флаг**.
- `Thread.isInterrupted()` (нестатический) — запрашивает статус другого потока **без сброса флага**.

По соглашению, любой метод, завершающийся выбросом `InterruptedException`, **сбрасывает флаг прерывания** в момент выброса исключения. Это означает, что после поимки `InterruptedException` информация о прерывании потока теряется, если её не восстановить явно.

Существует два рекомендуемых подхода к обработке `InterruptedException`:

**Подход 1: пробросить исключение выше**
Если метод позволяет объявить `throws InterruptedException` — это предпочтительный вариант, так как позволяет вышестоящему коду самому принять решение о реакции на прерывание.

**Подход 2: восстановить флаг прерывания**
Если пробросить `InterruptedException` нельзя (например, при реализации метода без соответствующего объявления исключений), нужно восстановить флаг вызовом `Thread.currentThread().interrupt()`:

```java
try {
    Thread.sleep(4000);
} catch (InterruptedException e) {
    // Восстанавливаем флаг, чтобы вышестоящий код мог узнать о прерывании
    Thread.currentThread().interrupt();
}
```

Пустой `catch`-блок — антипаттерн: он уничтожает информацию о прерывании. После него ни текущий код, ни вышестоящий не могут узнать, что поток был прерван. Это нарушает кооперативную модель отмены потоков в Java.

#### Ответ от Claude

**Модель прерывания в Java**

Прерывание в Java — кооперативный механизм: один поток сигнализирует другому о необходимости остановиться, но второй поток сам решает, когда и как реагировать. Технически это флаг (interrupt status) внутри объекта `Thread`.

- `Thread.interrupt()` — устанавливает флаг прерывания целевого потока.
- `Thread.isInterrupted()` — проверяет флаг без его сброса (нестатический).
- `Thread.interrupted()` — проверяет флаг и сбрасывает его (статический).

**Ключевое свойство `InterruptedException`**

По спецификации Java (Oracle Javadoc), любой метод, завершающийся выбросом `InterruptedException` (например, `Thread.sleep()`, `Object.wait()`, `BlockingQueue.take()`), **автоматически сбрасывает флаг прерывания** перед выбросом исключения. Это означает: после входа в `catch (InterruptedException e)` флаг уже равен `false`.

**Почему пустой `catch`-блок недопустим**

```java
// НЕПРАВИЛЬНО — информация о прерывании уничтожена безвозвратно
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    // пусто
}
```

1. Флаг сброшен автоматически при выбросе исключения.
2. Пустой `catch` не восстанавливает флаг и не пробрасывает исключение.
3. Вышестоящий код никогда не узнает, что поток был прерван.
4. Если поток управляет жизненным циклом ресурсов или входит в пул потоков — нарушается возможность его корректного завершения.

**Два правильных способа обработки**

*Способ 1 — пробросить исключение (предпочтительный):*

```java
public void doWork() throws InterruptedException {
    Thread.sleep(1000); // просто не ловим — исключение поднимается выше
}
```

*Способ 2 — восстановить флаг:*
Применяется, когда метод не может объявить `throws InterruptedException` (например, реализация `Runnable.run()` или переопределение метода без данного checked-исключения):

```java
@Override
public void run() {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt(); // восстанавливаем флаг
        // при необходимости — завершаем работу gracefully
    }
}
```

**Что означает «восстановить флаг прерывания»**

Вызов `Thread.currentThread().interrupt()` повторно устанавливает флаг прерывания текущего потока. После этого:
- вышестоящий код может проверить `Thread.isInterrupted()` и корректно среагировать;
- следующий вызов блокирующего метода (`sleep`, `wait`, `take` и т.д.) немедленно выбросит новый `InterruptedException`;
- контейнер потоков (например, `ExecutorService`) сможет корректно завершить поток.

**Типичный паттерн для долгих операций**

```java
while (!Thread.currentThread().isInterrupted()) {
    try {
        doUnitOfWork();
        Thread.sleep(100);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt(); // восстанавливаем
        break; // завершаем цикл
    }
}
```

---

### Вопрос 45. Что такое Thread.UncaughtExceptionHandler? Чем отличается установка обработчика через Thread.setUncaughtExceptionHandler() от установки через Thread.setDefaultUncaughtExceptionHandler()? В каких случаях эти обработчики применяются?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Thread (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/lang/Thread.html)

`Thread.UncaughtExceptionHandler` — функциональный интерфейс (появился в Java 1.5), определяющий обработчик, вызываемый JVM, когда поток аварийно завершается из-за непойманного исключения.

Когда поток собирается завершиться из-за непойманного исключения, JVM запрашивает у потока его `UncaughtExceptionHandler` через `Thread.getUncaughtExceptionHandler()` и вызывает метод `uncaughtException(Thread t, Throwable e)`. Любое исключение, выброшенное самим обработчиком, игнорируется JVM.

**`Thread.setUncaughtExceptionHandler(UncaughtExceptionHandler eh)`**

Устанавливает обработчик, который будет вызван при аварийном завершении **данного конкретного потока** из-за непойманного исключения. Если передать `null` — у потока не будет явного обработчика. Выбрасывает `SecurityException`, если текущий поток не имеет права модифицировать целевой поток.

**`Thread.setDefaultUncaughtExceptionHandler(UncaughtExceptionHandler eh)`** (статический)

Устанавливает **глобальный** обработчик по умолчанию для всех потоков, у которых нет явно установленного обработчика и чья `ThreadGroup` не обрабатывает исключение самостоятельно. Применяется, когда нужно изменить стандартное поведение JVM для непойманных исключений (например, централизованное логирование).

**Порядок поиска обработчика (приоритет убывает):**
1. Обработчик конкретного потока (`setUncaughtExceptionHandler`).
2. Объект `ThreadGroup` потока (и родительские группы).
3. Глобальный обработчик по умолчанию (`setDefaultUncaughtExceptionHandler`).

#### Ответ от Claude

**Что такое `Thread.UncaughtExceptionHandler`**

`Thread.UncaughtExceptionHandler` — вложенный функциональный интерфейс в классе `Thread`, введённый в Java 5. Содержит единственный метод:

```java
void uncaughtException(Thread t, Throwable e);
```

Вызывается JVM, когда поток завершается из-за непойманного исключения (`RuntimeException`, `Error` или любой `Throwable`). Заметно, что обработчик получает `Throwable`, то есть перехватывает в том числе `Error` (например, `OutOfMemoryError`, `StackOverflowError`).

**Различие между двумя методами установки**

| Характеристика | `setUncaughtExceptionHandler()` | `setDefaultUncaughtExceptionHandler()` |
|---|---|---|
| Область действия | Конкретный поток | Все потоки (глобально) |
| Тип метода | Метод экземпляра `Thread` | Статический метод `Thread` |
| Приоритет | Высший (1-й в иерархии) | Низший (3-й, запасной) |
| Типичное применение | Специфическая обработка для одного потока | Централизованное логирование, мониторинг |

**Полная иерархия поиска обработчика**

Когда поток завершается с непойманным исключением, JVM выполняет следующее:

1. Проверяет, установлен ли обработчик непосредственно на этом потоке (`setUncaughtExceptionHandler`). Если да — вызывает его.
2. Если нет — вызывает `ThreadGroup.uncaughtException()`. `ThreadGroup` по умолчанию делегирует в родительскую группу, пока не достигнет корневой группы.
3. Корневая `ThreadGroup`, если у неё нет специальной логики, делегирует вызов в глобальный обработчик по умолчанию (`setDefaultUncaughtExceptionHandler`), если он установлен.
4. Если глобального обработчика нет — JVM выводит стек исключения в `System.err` (стандартное поведение).

**Важное предупреждение из Javadoc:** глобальный обработчик по умолчанию **не должен** делегировать вызов обратно в `ThreadGroup` потока — это вызовет бесконечную рекурсию.

**Когда применяются обработчики**

`setUncaughtExceptionHandler` (на конкретный поток):
- Поток выполняет критически важную задачу и при сбое должен предпринять специфические действия (например, уведомить систему мониторинга, перезапустить только эту задачу).
- Реализация собственного `ThreadFactory` с нестандартной политикой обработки ошибок.

`setDefaultUncaughtExceptionHandler` (глобальный):
- Централизованное логирование всех непойманных исключений в приложении (особенно важно в приложениях без контейнера вроде standalone Java-приложений).
- Интеграция с системами мониторинга и алертинга (Sentry, Datadog и т.п.).
- В многопоточных приложениях с `ExecutorService`: при задачах, отправленных через `execute()` (не `submit()`), исключения не оборачиваются в `Future` и могут быть обработаны только через `UncaughtExceptionHandler`.

**Пример использования:**

```java
// Глобальный обработчик
Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
    System.err.println("Непойманное исключение в потоке: " + thread.getName());
    throwable.printStackTrace();
    // логирование, алертинг и т.п.
});

// Обработчик на конкретный поток
Thread t = new Thread(task);
t.setUncaughtExceptionHandler((thread, throwable) -> {
    log.error("Сбой в потоке {}", thread.getName(), throwable);
    restartTask(); // специфическое восстановление
});
t.start();
```

**Расхождение источников:** документация Oracle SE 8 и SE 21 одинаково описывают порядок поиска обработчика. Разночтений между версиями не обнаружено.

---

### Вопрос 46. Когда уместно использовать Optional вместо выбрасывания исключения? В чём принципиальная разница между «ожидаемым отсутствием значения» и «исключительной ситуацией»? Почему Oracle не рекомендует использовать Optional как замену любого null?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Optional (Java SE 11 & JDK 11) — docs.oracle.com](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/Optional.html)

`Optional<T>` — контейнерный объект, который может содержать или не содержать ненулевое значение. Если значение присутствует, `isPresent()` возвращает `true`; если отсутствует — объект считается пустым и `isPresent()` возвращает `false`.

Из API Note официальной документации:

> `Optional` предназначен прежде всего для использования в качестве **возвращаемого типа метода**, когда существует явная необходимость представить «нет результата» и когда использование `null` с высокой вероятностью приведёт к ошибкам. Переменная, тип которой `Optional`, никогда не должна сама быть `null`; она всегда должна указывать на экземпляр `Optional`.

Методы `orElse()` и `orElseGet()` в целом предпочтительнее `orElseThrow()`: они возвращают замещающее значение при отсутствии, вместо выброса исключения. Это подчёркивает, что `Optional` спроектирован для **ожидаемого** отсутствия значения, а не для исключительных ситуаций.

При этом документация предупреждает: следует избегать проверки пустоты объекта через сравнение с `==` с результатом `Optional.empty()` — нет гарантии, что это синглтон. Вместо этого нужно использовать `isPresent()` или `isEmpty()`.

#### Ответ от Claude

**Принципиальное различие: ожидаемое отсутствие vs исключительная ситуация**

*Ожидаемое отсутствие значения* — это нормальный, предвиденный исход в рамках бизнес-логики. Отсутствие результата входит в контракт метода и не свидетельствует об ошибке.

Примеры:
- `userRepository.findById(id)` — пользователь может просто не существовать в базе.
- `map.get(key)` — ключ может отсутствовать в словаре.
- `stream.findFirst()` — поток может быть пустым.

*Исключительная ситуация* — это нарушение инварианта или контракта, которое является ошибкой: некорректный ввод, недоступный ресурс, нарушение бизнес-правил.

Примеры:
- `findById(null)` — передан недопустимый аргумент (лучше `NullPointerException` или `IllegalArgumentException`).
- Файл, который обязан существовать по контракту системы, не найден.
- Нарушение целостности данных в базе.

**Когда использовать `Optional`**

`Optional` уместен, когда:
1. Метод возвращает результат, и отсутствие результата — нормальный вариант выполнения.
2. Возвращаемый тип является ссылочным и `null` неоднозначен или опасен.
3. Хочется явно сигнализировать вызывающей стороне: «обработай оба случая».

```java
// Уместно: пользователь может не существовать
public Optional<User> findUserByEmail(String email) { ... }

// Вызов
findUserByEmail("a@b.com")
    .map(User::getRole)
    .orElse(Role.GUEST);
```

**Когда бросать исключение**

Исключение уместно, когда:
1. Отсутствие значения означает ошибку (нарушение предусловия, бизнес-правила).
2. Вызывающая сторона не должна продолжать работу без значения — нужно явно прервать поток выполнения.
3. Необходимо передать диагностическое сообщение и контекст ошибки.

```java
// Уместно: заказ обязан существовать, иначе это ошибка
public Order getOrderById(Long id) {
    return orderRepository.findById(id)
        .orElseThrow(() -> new OrderNotFoundException("Заказ не найден: " + id));
}
```

**Почему Oracle не рекомендует использовать `Optional` как замену любого `null`**

Из официального API Note (`Optional`, Java SE 11+): `Optional` **предназначен прежде всего для возвращаемых типов методов**, а не как универсальная замена `null`.

Конкретные причины:

1. **Накладные расходы.** Каждый `Optional` — дополнительный объект в куче. Массовое применение (поля класса, параметры методов, коллекции) создаёт лишний мусор для GC.

2. **Поля и параметры.** Использование `Optional` как типа поля или параметра метода ухудшает читаемость и нарушает принцип минимального удивления. `Optional`-поле само может быть `null`, создавая двойную неопределённость.

3. **Сериализация.** `Optional` не реализует `Serializable`. Использование его в полях сериализуемых классов вызовет ошибку во время выполнения.

4. **Коллекции.** `Optional` внутри коллекций (`List<Optional<T>>`) — почти всегда антипаттерн; лучше просто хранить только непустые значения.

5. **`Optional<Optional<T>>`.** Вложенные `Optional` — признак неправильного проектирования API.

**Правило из документации Oracle:** переменная типа `Optional` никогда не должна сама быть `null` — это обессмысливает её применение. Если она может быть `null`, значит, `Optional` применён неуместно.

**Итоговая таблица выбора**

| Ситуация | Инструмент |
|---|---|
| Поиск объекта, который может не существовать | `Optional` |
| Метод с несколькими возможными результатами, один из которых «пусто» | `Optional` |
| Нарушение предусловий или бизнес-правил | Проверяемое / непроверяемое исключение |
| Ресурс недоступен или операция невозможна | Исключение |
| Поле класса | `null` (с Javadoc) или отдельное поле-признак |
| Параметр метода | `null` (с документацией) или перегрузка метода |
### Вопрос 47. Что означают понятия «swallowing exception» (поглощение исключения) и «exception masking»? Приведите три примера кода, реализующих эти антипаттерны, и объясните их последствия для диагностики.

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Swallowed Exceptions: The Silent Killer of Java Applications (Harness Blog)](https://www.harness.io/blog/swallowed-exceptions-java-applications)

**Exception swallowing (поглощение исключения)** — это практика перехвата исключения в пустом `catch`-блоке без каких-либо действий: без логирования, без повторного выброса, без уведомления вызывающего кода. Анализ 16 миллионов Java `catch`-блоков показал, что примерно 20% из них не содержат никакого действия.

Последствия для диагностики:
- **Скрытые сбои**: ошибка не попадает в логи, и при разборе инцидента в production найти её корень практически невозможно.
- **Release-day хаос**: при появлении проблемы разработчики перебирают огромные логи и обнаруживают, что сама ошибка в них попросту отсутствует.
- **Удар по пользователям**: без видимости исключений проблема обнаруживается слишком поздно — уже после того, как она затронула большое число пользователей.

Пример пустого `catch`-блока:

```java
try {
    riskyOperation();
} catch (Exception e) {
    // пусто — исключение поглощено
}
```

#### Ответ от Claude

**Поглощение исключения (exception swallowing)** — это антипаттерн, при котором исключение перехватывается, но никак не обрабатывается: не логируется, не пробрасывается вызывающему коду и не конвертируется в другое исключение с сохранением первопричины.

**Exception masking (маскировка исключения)** — более широкое понятие: исходное исключение скрывается за счёт другого исключения или действия. Чаще всего это происходит в `finally`-блоке или при обёртывании в новое исключение без передачи оригинального в качестве `cause`.

---

**Антипаттерн 1 — Пустой catch-блок (чистое поглощение)**

```java
try {
    connection = dataSource.getConnection();
    connection.execute(sql);
} catch (SQLException e) {
    // ничего не делаем
}
```

Последствие: любая ошибка БД (потеря соединения, синтаксическая ошибка SQL, дедлок) исчезает бесследно. В логах нет ни строки, и команда даже не узнает, что операция провалилась.

---

**Антипаттерн 2 — Маскировка исключением в finally-блоке**

```java
// Источник: eclipsesource.com/blogs/2013/04/25/when-an-exception-gets-lost/
try {
    while (!done) {
        processRequest(); // здесь выброшен Error (например, OutOfMemoryError)
    }
} finally {
    cleanup(); // если cleanup() бросает NullPointerException,
               // исходный Error теряется навсегда
}
```

Последствие: вызывающий код (и вся цепочка логирования) видит только `NullPointerException` из `cleanup()`, а критический `OutOfMemoryError`, ставший реальной причиной сбоя, полностью скрыт. Это классический случай **exception masking**: одно исключение «перекрывает» другое.

---

**Антипаттерн 3 — Деструктивное обёртывание (потеря cause)**

```java
try {
    parseConfiguration(file);
} catch (IOException e) {
    // оригинальное исключение e не передаётся как cause!
    throw new ConfigurationException("Не удалось загрузить конфигурацию");
}
```

Последствие: стектрейс исходного `IOException` (с именем файла, номером строки и реальным сообщением об ошибке) теряется. В логах появляется только `ConfigurationException` без указания первопричины. Правильный вариант:

```java
throw new ConfigurationException("Не удалось загрузить конфигурацию", e);
```

---

**Итоговые последствия для диагностики**

| Антипаттерн | Что теряется |
|---|---|
| Пустой catch | Всё: тип, сообщение, стектрейс |
| Маскировка в finally | Исходное исключение полностью скрыто за новым |
| Деструктивное обёртывание | Стектрейс и тип первопричины |

Инструменты защиты: lint-правила IDE (IntelliJ: «Empty catch block»), SpotBugs (детектор `DE_MIGHT_IGNORE`), code review-гайдлайны. При осознанном подавлении необходимо хотя бы логировать: `log.warn("Ожидаемое исключение, игнорируем", e)`.

> Источники для проверки: [eclipsesource.com — When an exception gets lost](https://eclipsesource.com/blogs/2013/04/25/when-an-exception-gets-lost/), [Medium — Java Exception Anti-Patterns 101](https://davidhodges-kiwi.medium.com/java-exception-anti-patterns-101-2761fb1754c4), [Harness Blog](https://www.harness.io/blog/swallowed-exceptions-java-applications)

---

### Вопрос 48. Как исключения взаимодействуют с транзакциями в Spring? Почему по умолчанию откат транзакции происходит только при RuntimeException, но не при checked-исключении? Как изменить это поведение через @Transactional?

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Rolling Back a Declarative Transaction — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html)

По умолчанию инфраструктура транзакций Spring помечает транзакцию на откат **только при runtime-исключениях (непроверяемых)**: то есть когда брошенное исключение является экземпляром `RuntimeException` или его подклассом. Экземпляры `Error` также вызывают откат по умолчанию. Checked-исключения, выброшенные из транзакционного метода, в конфигурации по умолчанию **не вызывают откат**.

Это поведение следует **конвенции EJB**: EJB-контейнер автоматически откатывает транзакцию при «системном исключении» (system exception — обычно runtime exception), но не откатывает автоматически при «прикладном исключении» (application exception — checked exception, отличное от `java.rmi.RemoteException`). Spring воспроизводит эту же семантику для декларативного управления транзакциями.

Изменить поведение можно через атрибуты аннотации `@Transactional`:

```java
// Откат при конкретном checked-исключении
@Transactional(rollbackFor = NoProductInStockException.class)
public void processOrder(Order order) throws NoProductInStockException {
    // ...
}

// Запрет отката для конкретного исключения
@Transactional(noRollbackFor = InstrumentNotFoundException.class)
public void updateStock() {
    // ...
}

// Откат при любом исключении (включая все checked)
@Transactional(rollbackFor = Exception.class)
public void criticalOperation() throws Exception {
    // ...
}
```

#### Ответ от Claude

**Стандартное поведение Spring @Transactional**

Spring AOP-прокси оборачивает транзакционный метод. При выходе из метода (нормальном или через исключение) `TransactionInterceptor` принимает решение: зафиксировать (commit) или откатить (rollback) транзакцию.

Правило по умолчанию:
- `RuntimeException` и его подклассы → **rollback**
- `Error` → **rollback**
- `Checked Exception` (любой подкласс `Exception`, но не `RuntimeException`) → **commit**

**Почему именно так: причина в EJB-конвенции**

Философия разграничения восходит к EJB (Enterprise JavaBeans):

- **Checked exception = «прикладное исключение»** (application exception): ожидаемая ситуация, часть бизнес-логики (например, `InsufficientFundsException`). Предполагается, что вызывающий код знает об этой возможности и способен её обработать. Транзакция может оставаться в силе, потому что состояние БД консистентно — просто операция не выполнена по бизнес-правилу.
- **RuntimeException = «системное исключение»** (system exception): непредвиденный сбой инфраструктуры (например, `NullPointerException`, `DataAccessException`). Состояние транзакции непредсказуемо, поэтому откат обязателен.

На практике эта граница размыта: бизнес-разработчики нередко используют `RuntimeException` для бизнес-ошибок, что соответствует современному подходу (например, вся иерархия исключений Spring Data является непроверяемой).

**Настройка через @Transactional**

```java
// 1. Rollback при конкретном checked-исключении
@Transactional(rollbackFor = OrderProcessingException.class)
public void processOrder(Order order) throws OrderProcessingException {
    inventoryService.reserve(order);   // может бросить OrderProcessingException
    paymentService.charge(order);
}

// 2. Запрет отката для RuntimeException-подкласса
@Transactional(noRollbackFor = OptimisticLockingFailureException.class)
public void updateWithRetry(Entity entity) {
    repository.save(entity);  // логика повторит попытку — откат не нужен
}

// 3. Rollback для всех исключений (наиболее строгий режим)
@Transactional(rollbackFor = Exception.class)
public void fullyGuardedOperation() throws Exception {
    // любое исключение откатит транзакцию
}
```

**Программный откат (крайний случай)**

Если нужно откатить транзакцию без выброса исключения:

```java
@Transactional
public void conditionalRollback() {
    try {
        doWork();
    } catch (BusinessException e) {
        // Помечаем транзакцию на откат, не пробрасывая исключение
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}
```

**Важные оговорки**

1. `@Transactional` работает только через AOP-прокси: вызов транзакционного метода из того же класса (self-invocation) не создаёт прокси и транзакция не применяется.
2. Если checked-исключение перехвачено внутри метода и не пробрасывается наружу, Spring не увидит его и зафиксирует транзакцию.
3. Атрибут `rollbackFor` поддерживает массив классов: `rollbackFor = {IOException.class, SQLException.class}`.

> Источники для проверки: [Spring Framework Reference — Rolling Back](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html), [Cloudflight Engineering Blog](https://engineering.cloudflight.io/springs-transactional-does-not-rollback-on-checked-exceptions), [DZone — Spring @Transactional & Exceptions](https://dzone.com/articles/spring-transactional-amp-exceptions)

---

### Вопрос 49. Что произойдёт, если выбросить исключение из конструктора? В каком состоянии окажется создаваемый объект? Почему это может привести к утечке ресурсов в конструкторе, использующем try-with-resources?

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Can Constructors Throw Exceptions in Java — Rollbar Blog](https://rollbar.com/blog/can-constructors-throw-exceptions-in-java/)

Когда исключение выброшено из конструктора, объект **не инстанциируется** и, как правило, сразу становится доступным для сборщика мусора. Однако в ряде случаев он может быть **частично сконструирован** и не будет немедленно утилизирован — это происходит, когда конструктор успел обратиться к каким-либо ресурсам до возникновения исключения.

Частично сконструированные объекты создают уязвимости безопасности и тратят системные ресурсы, если последние не освобождены должным образом.

Рекомендуемые подходы:
1. **Ранняя валидация**: проверять данные и выбрасывать исключения до обращения к ресурсам.
2. **Явное освобождение**: использовать `try-catch-finally` или `try-with-resources` внутри конструктора для гарантированной очистки.

```java
public class Student {
    private String name;
    private int age;

    public Student(String name, int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age must be greater than zero");
        }
        this.name = name;
        this.age = age;
    }
}
```

#### Ответ от Claude

**Состояние объекта при исключении из конструктора**

При выбросе исключения из конструктора:
- Память под объект уже выделена JVM (заголовок объекта + поля со значениями по умолчанию).
- Конструктор прерван: поля, инициализируемые после точки выброса, остаются в состоянии по умолчанию (`null`, `0`, `false`).
- Ссылка на объект **не возвращается** вызывающему коду: оператор `new` не завершается успешно, поэтому переменная остаётся неинициализированной.
- Объект недоступен из кода, но JVM всё ещё держит на него ссылку до завершения GC.

**Утечка ресурсов в конструкторе**

Если конструктор открывает несколько ресурсов последовательно и исключение возникает после открытия первого, но до открытия второго, `try-with-resources` на уровне **вызывающего кода** не поможет — объект не создан, а значит, его `close()` не будет вызван.

```java
// ПРОБЛЕМНЫЙ КОД
class CompositeResource implements AutoCloseable {
    private final InputStream input;
    private final OutputStream output;

    public CompositeResource(String inPath, String outPath) throws IOException {
        this.input = new FileInputStream(inPath);     // открыт успешно
        this.output = new FileOutputStream(outPath);  // выброшен IOException
        // input НЕ закрыт! CompositeResource не создан,
        // вызывающий try-with-resources не вызовет close()
    }

    @Override
    public void close() throws IOException {
        input.close();
        output.close();
    }
}
```

Вызывающий код с `try-with-resources`:

```java
try (CompositeResource r = new CompositeResource("in.txt", "out.txt")) {
    r.process();
} // close() вызывается только если r != null,
  // т.е. только если конструктор завершился успешно
```

Если `new FileOutputStream(outPath)` бросает исключение, `CompositeResource` не создан, `close()` не вызывается, и `FileInputStream` утекает.

**Правильный подход: защита ресурсов внутри конструктора**

```java
class CompositeResource implements AutoCloseable {
    private final InputStream input;
    private final OutputStream output;

    public CompositeResource(String inPath, String outPath) throws IOException {
        InputStream tmpInput = new FileInputStream(inPath);
        try {
            this.output = new FileOutputStream(outPath);
        } catch (IOException e) {
            tmpInput.close();  // явное освобождение при сбое
            throw e;
        }
        this.input = tmpInput;
    }

    @Override
    public void close() throws IOException {
        try {
            input.close();
        } finally {
            output.close();
        }
    }
}
```

**Почему try-with-resources на уровне вызывающего кода не спасает**

Согласно спецификации Java (JLS §14.20.3) и документации Oracle, ресурс регистрируется для автоматического закрытия только после **успешного завершения** выражения-инициализатора в заголовке `try`. Если конструктор бросает исключение, ресурс не добавляется в список «к закрытию» — `close()` просто не будет вызван.

Аналогично, при цепочке ресурсов в одном `try`:

```java
try (A a = new A(); B b = new B()) { ... }
```

Если `new B()` бросает исключение, `a.close()` будет вызван (A успешно создан). Но если `new A()` бросает — ни `a.close()`, ни `b.close()` не вызываются.

**Уязвимость finalizer attack**

Частично сконструированный объект нефинального класса создаёт уязвимость: злоумышленник может унаследоваться, переопределить `finalize()` и получить ссылку на неполностью инициализированный объект через GC-финализатор, обходя проверки безопасности в конструкторе. Защита:
- объявить класс `final`;
- добавить `final void finalize() {}` (пустой финализатор, не допускающий переопределения);
- `finalize()` депрецирован в Java 9 и удалён в Java 18+ (`--finalization=disabled` по умолчанию).

> Источники для проверки: [Rollbar — Can Constructors Throw Exceptions in Java](https://rollbar.com/blog/can-constructors-throw-exceptions-in-java/), [Oracle — The try-with-resources Statement](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html), [SEI CERT OBJ11-J](https://cmu-sei.github.io/secure-coding-standards/sei-cert-oracle-coding-standard-for-java/rules/object-orientation-obj/obj11-j), [Jenkov — Try-with-Resources](https://jenkov.com/tutorials/java-exception-handling/try-with-resources.html)

---
### Вопрос 50. Можно ли в Java объявить метод, который бросает обобщённое (generic) исключение? Что такое параметризованное исключение вида &lt;E extends Exception&gt;? Каковы ограничения дженериков при работе с исключениями?

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Restrictions on Generics — The Java Tutorials (Oracle)](https://docs.oracle.com/javase/tutorial/java/generics/restrictions.html)

В официальном руководстве Oracle по дженерикам описаны три ключевых ограничения, связанных с исключениями.

**1. Generic-класс не может расширять Throwable (ни прямо, ни косвенно):**

```java
// Ошибка компиляции — косвенное расширение Throwable
class MathException<T> extends Exception { }

// Ошибка компиляции — прямое расширение Throwable
class QueueFullException<T> extends Throwable { }
```

**2. Нельзя перехватывать экземпляр type-параметра в catch-блоке:**

```java
public static <T extends Exception, J> void execute(List<J> jobs) {
    try {
        for (J job : jobs) { /* ... */ }
    } catch (T e) { // ошибка компиляции
        // ...
    }
}
```

**3. Использование type-параметра в throws-clause разрешено:**

```java
class Parser<T extends Exception> {
    public void parse(File file) throws T { // OK
        // ...
    }
}
```

Причина ограничений — **type erasure**: во время выполнения информация о type-параметрах стирается, и JVM не может корректно разрешать обработчики исключений для параметризованных типов.

#### Ответ от Claude

**Что такое параметризованное исключение вида `<E extends Exception>`**

Это ситуация, когда сам *метод* (не класс) объявлен с type-параметром, ограниченным `Exception`:

```java
public <E extends Exception> void throwIt(E exception) throws E {
    throw exception;
}
```

Здесь `E` — type-параметр метода. Вызывающий код передаёт конкретный тип исключения, а компилятор выводит тип и проверяет throws-контракт. Например:

```java
throwIt(new IOException("ошибка ввода-вывода")); // компилируется, если вызывающий объявляет throws IOException
```

**Три ограничения дженериков при работе с исключениями**

| Ограничение | Пример | Причина |
|---|---|---|
| Generic-класс не может наследовать Throwable | `class Foo<T> extends Exception` — ошибка | JVM не поддерживает параметризованные типы исключений в таблицах исключений bytecode |
| Нельзя ловить type-параметр в catch | `catch (T e)` — ошибка | После erasure тип T заменяется на его bound (Exception), и различать разные T в runtime невозможно |
| Можно использовать type-параметр в throws | `throws T` — OK | Компилятор проверяет контракт на этапе компиляции; erasure в данном случае безопасна |

**Практический паттерн: exception chaining с generic-параметром**

```java
// Метод "бросает то, что дал вызывающий", сохраняя тип checked-исключения
public <E extends Exception> void process(ThrowingRunnable<E> action) throws E {
    action.run();
}

@FunctionalInterface
interface ThrowingRunnable<E extends Exception> {
    void run() throws E;
}
```

Это позволяет написать pipeline, где компилятор *знает* конкретный тип checked-исключения:

```java
process(() -> Files.readString(Path.of("file.txt"))); // throws IOException — компилятор видит тип
```

**Внутренний класс внутри generic-класса тоже не может расширять Exception:**

```java
class Outer<T> {
    class Inner extends Exception { } // ошибка компиляции
}
```

Это ограничение зафиксировано в JLS §8.1.2 и пояснено в Oracle Tutorials: "catch mechanism of the Java Virtual Machine works only with non-generic classes".

**Итог:** в Java можно объявить метод с type-параметром `<E extends Exception>` и указать `throws E` — это рабочая и иногда полезная конструкция. Однако *классы* исключений не могут быть параметризованными, а перехват по type-параметру в catch невозможен из-за type erasure.

---

### Вопрос 51. Как работает механизм обработки исключений в потоках Java Stream API? Почему stream-пайплайн прерывается при первом исключении? Как корректно обработать исключения внутри операций stream, не нарушая цепочку?

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Repackaging Exceptions in Streams — nipafx.dev (Nicolai Parlog)](https://nipafx.dev/java-repackaging-exceptions-streams/)

Stream API использует функциональные интерфейсы (`Function`, `Predicate`, `Consumer` и др.), которые не объявляют checked-исключений. Когда в операции потока вызывается метод, бросающий checked-исключение (например, `IOException`), компилятор отвергает код:

```java
// Не компилируется: User::parse бросает ParseException (checked)
List<User> users = lines.stream()
    .map(User::parse)
    .collect(toList());
```

Автор выделяет три стратегии «переупаковки» исключений:

**1. Оборачивание в unchecked-исключение**
```java
lines.stream()
    .map(line -> {
        try {
            return User.parse(line);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    })
    .collect(toList());
```
Просто, но скрывает checked-природу исключения от вызывающего кода.

**2. Sneaky-throw**
Через generic-трюк с erasure: метод `<E extends Exception> void sneakyThrow(Exception e) throws E` позволяет пробросить checked-исключение без объявления. Минус — вызывающий код не может поймать конкретный тип, не объявленный в сигнатуре.

**3. Lifting (подъём исключения на уровень стрима)**
Обернуть вызов в вспомогательный метод, который сам объявляет `throws ParseException`, и использовать его с соответствующим функциональным интерфейсом, допускающим checked:

```java
@FunctionalInterface
interface ThrowingFunction<T, R, E extends Exception> {
    R apply(T t) throws E;
}
```

**Ключевой вывод автора:** все три подхода прерывают пайплайн при первом исключении, потому что исключение разрывает ленивую цепочку вычислений, и дальнейшие элементы не обрабатываются.

#### Ответ от Claude

**Почему Stream API не поддерживает checked-исключения нативно**

Функциональные интерфейсы JDK (`java.util.function.*`) не объявляют checked-исключений по контракту. Лямбды, передаваемые в `map`, `filter`, `forEach` и т.д., обязаны соответствовать этим интерфейсам. Это архитектурное решение — сохранить чистоту функционального стиля — влечёт за собой необходимость явно обрабатывать любые исключения прямо внутри лямбды.

**Почему пайплайн прерывается при первом исключении**

Stream выполняется лениво: элементы проходят через операторы один за другим (или батчами в parallel stream) только при вызове терминальной операции. Когда исключение (unchecked или sneaky-thrown checked) вылетает из любой промежуточной операции, оно распространяется вверх по стеку вызовов через терминальную операцию к вызывающему коду. Стрим не предоставляет механизма «пропустить элемент с ошибкой и продолжить» — нет отдельного канала для ошибок.

В параллельном стриме исключения из рабочих потоков ForkJoinPool оборачиваются в `java.util.concurrent.CompletionException` и перебрасываются в вызывающий поток через терминальную операцию.

**Паттерны корректной обработки**

**Паттерн 1: try-catch внутри лямбды (минимальный, но засоряет код)**

```java
List<String> contents = paths.stream()
    .map(path -> {
        try {
            return Files.readString(path);
        } catch (IOException e) {
            return null; // или пустая строка, или дефолтное значение
        }
    })
    .filter(Objects::nonNull)
    .toList();
```

Недостаток: логика обработки ошибок смешана с логикой трансформации.

**Паттерн 2: вспомогательный wrapper-метод (рекомендуемый)**

```java
static String safeReadString(Path path) {
    try {
        return Files.readString(path);
    } catch (IOException e) {
        // логируем или возвращаем дефолт
        return null;
    }
}

List<String> contents = paths.stream()
    .map(MyUtils::safeReadString)
    .filter(Objects::nonNull)
    .toList();
```

**Паттерн 3: возврат Optional из wrapper-метода**

```java
static Optional<String> tryReadString(Path path) {
    try {
        return Optional.of(Files.readString(path));
    } catch (IOException e) {
        return Optional.empty();
    }
}

List<String> contents = paths.stream()
    .map(MyUtils::tryReadString)
    .flatMap(Optional::stream)
    .toList();
```

Этот вариант явно разделяет успешные и неуспешные элементы без `null`.

**Паттерн 4: ThrowingFunction / wrapper для unchecked (если нужно пробросить исключение выше)**

```java
@FunctionalInterface
interface ThrowingFunction<T, R> {
    R apply(T t) throws Exception;
}

static <T, R> Function<T, R> wrap(ThrowingFunction<T, R> f) {
    return t -> {
        try {
            return f.apply(t);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    };
}

// Использование:
paths.stream()
    .map(wrap(Files::readString))
    .toList(); // бросит RuntimeException(IOException) при первой ошибке
```

**Паттерн 5: Either/Result тип для агрегации ошибок без прерывания**

Если нужно обработать *все* элементы и собрать и результаты, и ошибки:

```java
record Result<T>(T value, Exception error) {
    static <T> Result<T> of(ThrowingSupplier<T> s) {
        try { return new Result<>(s.get(), null); }
        catch (Exception e) { return new Result<>(null, e); }
    }
    boolean isSuccess() { return error == null; }
}

List<Result<String>> results = paths.stream()
    .map(p -> Result.of(() -> Files.readString(p)))
    .toList();

List<String> successes = results.stream()
    .filter(Result::isSuccess)
    .map(Result::value)
    .toList();

List<Exception> errors = results.stream()
    .filter(r -> !r.isSuccess())
    .map(Result::error)
    .toList();
```

**Сводная таблица подходов**

| Подход | Прерывает пайплайн | Checked-safe | Сложность |
|---|---|---|---|
| try-catch в лямбде | нет (при возврате дефолта) | да | низкая |
| wrapper-метод с Optional | нет | да | низкая |
| wrap() в RuntimeException | да | нет | низкая |
| Either/Result тип | нет | да | средняя |
| Sneaky-throw | да | нет | высокая (рискованно) |

**Расхождение между источниками:** nipafx.dev и howtodoinjava.com единогласны в том, что stream прерывается при любом непойманном исключении. Baeldung дополнительно указывает на библиотечные решения (Vavr `Try`, Apache Commons `FailableStream`), которые предоставляют готовые Either-подобные абстракции, но требуют внешней зависимости.

---

### Вопрос 52. Почему нельзя использовать исключения для управления обычным потоком выполнения? Какие последствия это имеет для производительности и дизайна API?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Effective Java: Use Exceptions for Only Exceptional Circumstances — dev.to/kylec32](https://dev.to/kylec32/effective-java-use-exceptions-for-only-exceptional-circumstances-1el6)

Исключения спроектированы для исключительных ситуаций — их никогда не следует применять для обычного управления потоком выполнения (control flow).

**Антипаттерн** — использование `ArrayIndexOutOfBoundsException` вместо явной проверки границ массива:

```java
// НЕПРАВИЛЬНО: исключение вместо проверки
try {
    int i = 0;
    while (true) {
        range[i++].climb(); // бросает AIOOBE, когда индекс выходит за границу
    }
} catch (ArrayIndexOutOfBoundsException e) {
    // «нормальное» завершение цикла
}
```

Правильный эквивалент — стандартный цикл `for-each`, который работает в разы быстрее.

Причины, по которым JVM не оптимизирует такой код:
- разработчики JVM не стремятся делать исключения быстрыми, так как они предназначены для редких случаев;
- блоки `try-catch` ограничивают оптимизации JIT-компилятора.

**Импликации для дизайна API:** хорошо спроектированный API не должен принуждать клиентов к использованию исключений в обычном потоке. Если класс имеет «state-dependent» метод (который можно вызывать только в определённых условиях), должен существовать отдельный «state-testing» метод. Пример: `Iterator.hasNext()` — state-testing, `Iterator.next()` — state-dependent.

#### Ответ от Claude

**Почему исключения нельзя использовать для управления потоком**

Исключения в Java предназначены исключительно для исключительных условий (Effective Java, Item 69, Joshua Bloch). Использование их для control flow нарушает ожидания как JVM, так и читателей кода.

**Три причины, по которым это плохо:**

1. **Производительность.** Поскольку исключения предназначены для редких случаев, JVM-имплементаторы не оптимизируют их выполнение. Создание объекта исключения с `fillInStackTrace()` (нативный вызов) стоит значительно дороже простой проверки условия. Блоки `try-catch` также препятствуют ряду JIT-оптимизаций.

2. **Скрытие ошибок.** Широкий `catch (Exception e)` или `catch (IndexOutOfBoundsException e)`, используемый как механизм выхода из цикла, может случайно подавить реальную ошибку, возникшую внутри цикла. Такой код практически невозможно отлаживать.

3. **Читаемость и поддержка.** Применение исключений для flow control нарушает принцип наименьшего удивления — разработчики не ожидают, что исключение является «штатной» ситуацией.

**Правильная замена:**

```java
// ПРАВИЛЬНО: стандартный цикл вместо exception-based idiom
for (Mountain m : range) {
    m.climb();
}
```

**Импликации для дизайна API:**

Хорошо спроектированный API не должен принуждать клиентов использовать исключения в обычном потоке. Если метод работает только при определённом состоянии объекта, следует предоставить «state-testing» метод:

| Паттерн | State-testing | State-dependent |
|---|---|---|
| `Iterator` | `hasNext()` | `next()` |
| `BlockingQueue` | `peek()` (возвращает `null`) | `remove()` |
| Пользовательский стек | `isEmpty()` | `pop()` |

Альтернативой state-testing методу может быть возврат `Optional` или специального значения (sentinel value), сигнализирующего о невозможности выполнить операцию.

**Расхождений между источниками не выявлено.** Effective Java Item 69 и другие источники единогласны: exception-based control flow — это антипаттерн, снижающий производительность и усложняющий диагностику.

---

### Вопрос 53. Почему следует отдавать предпочтение стандартным исключениям JDK (IllegalArgumentException, IllegalStateException и др.) вместо собственных? Когда всё же нужно создавать собственное исключение?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Effective Java: Favor The Use of Standard Exceptions — dev.to/kylec32](https://dev.to/kylec32/effective-java-favor-the-use-of-standard-exceptions-2aej)

Повторное использование стандартных исключений даёт несколько преимуществ: API легче изучать и использовать, поскольку он соответствует устоявшимся конвенциям; программы, использующие API, легче читать — в них нет незнакомых типов исключений; меньше классов означает меньший объём памяти и меньше времени на загрузку классов.

Наиболее часто повторно используемые исключения:

| Исключение | Когда применять |
|---|---|
| `IllegalArgumentException` | Переданный аргумент недопустим |
| `IllegalStateException` | Состояние объекта недопустимо для вызова данного метода |
| `NullPointerException` | Передан `null`, где это запрещено |
| `IndexOutOfBoundsException` | Индекс вышел за допустимые границы |
| `ConcurrentModificationException` | Обнаружена недопустимая конкурентная модификация |
| `UnsupportedOperationException` | Объект не поддерживает вызванную операцию |

Принцип выбора между `IllegalArgumentException` и `IllegalStateException`: если для любого значения аргумента вызов был бы невозможен — это `IllegalStateException`; если только для конкретного аргумента — `IllegalArgumentException`.

#### Ответ от Claude

**Преимущества стандартных исключений**

Использование стандартных исключений JDK рекомендовано в Effective Java (Item 72, Joshua Bloch) по трём причинам:

1. **Читаемость.** Разработчики уже знают стандартные исключения — код без незнакомых типов легче воспринимается.
2. **Согласованность.** API следует устоявшимся конвенциям Java-экосистемы.
3. **Производительность.** Меньше пользовательских классов → меньше нагрузки на ClassLoader.

**Таблица стандартных исключений и их применения**

| Исключение | Когда использовать |
|---|---|
| `IllegalArgumentException` | Недопустимое значение параметра (например, отрицательный размер коллекции) |
| `IllegalStateException` | Состояние объекта несовместимо с вызовом метода (например, вызов `next()` до `hasNext()`) |
| `NullPointerException` | Параметр равен `null`, где это запрещено (специализация `IllegalArgumentException`) |
| `IndexOutOfBoundsException` | Индекс вне допустимых границ (специализация `IllegalArgumentException`) |
| `ConcurrentModificationException` | Коллекция изменена во время итерации |
| `UnsupportedOperationException` | Метод интерфейса не поддерживается реализацией (`add()` у неизменяемой коллекции) |
| `ArithmeticException` | Недопустимая арифметическая операция (деление на ноль) |

**Важные конвенции:**
- Если параметр равен `null` там, где `null` запрещён — бросайте `NullPointerException`, а не `IllegalArgumentException`.
- Если индекс вышел за границы — бросайте `IndexOutOfBoundsException`, а не `IllegalArgumentException`.
- Никогда не выбрасывайте напрямую `Exception`, `RuntimeException`, `Throwable`, `Error` — они слишком абстрактны и затрудняют обработку.

**Когда создавать собственное исключение:**
- Нужно передать дополнительный контекст (бизнес-специфичные поля: `orderId`, `errorCode`).
- Нужна типизированная обработка в `catch` для нескольких независимых классов ошибок.
- Исключение является частью публичного API библиотеки — своя иерархия упрощает обработку на стороне клиента.
- Стандартное исключение плохо описывает ситуацию семантически.

**Расхождений между источниками не выявлено.** Effective Java Item 72, Baeldung и другие источники согласны: стандартные исключения предпочтительны, собственные — только при наличии веской причины.

---

### Вопрос 54. Как правильно документировать исключения в Javadoc? В чём разница между документированием checked и unchecked исключений? Почему не следует объявлять throws Exception в сигнатуре метода?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Effective Java: Document All Exceptions Thrown By Each Method — dev.to/kylec32](https://dev.to/kylec32/effective-java-document-all-exceptions-thrown-by-each-method-oad)

Исключения — и checked, и unchecked — являются частью контракта метода и должны быть документированы. Java предоставляет тег `@throws` в Javadoc для этой цели.

Ключевые рекомендации:
- Использовать тег `@throws` для документирования каждого исключения, которое может бросить метод, и не указывать `throws` в сигнатуре для unchecked-исключений.
- Документировать каждое исключение отдельно, максимально конкретно описывая условия, при которых оно возникает.
- Если несколько методов класса бросают одно и то же исключение по одной причине, можно задокументировать его в комментарии к классу, а не повторять для каждого метода.

Хорошо задокументированный список unchecked-исключений фактически описывает предусловия успешного вызова метода.

#### Ответ от Claude

**Почему документировать исключения обязательно**

Исключения являются частью публичного контракта метода (Effective Java, Item 74, Joshua Bloch). Вызывающий код должен знать, какие исключения ожидать, чтобы корректно их обработать.

**Инструмент: тег `@throws` в Javadoc**

```java
/**
 * Загружает пользователя по идентификатору.
 *
 * @param id идентификатор пользователя; не должен быть {@code null} или отрицательным
 * @return найденный пользователь
 * @throws UserNotFoundException если пользователь с указанным id не существует
 * @throws IllegalArgumentException если {@code id} равен {@code null} или отрицательный
 * @throws DataAccessException если произошла ошибка при обращении к базе данных (unchecked)
 */
public User findById(Long id) throws UserNotFoundException { ... }
```

**Разница в документировании checked и unchecked исключений**

| Аспект | Checked-исключения | Unchecked-исключения |
|---|---|---|
| Используется `throws` в сигнатуре | Да (обязательно или обработать) | Нет (не рекомендуется) |
| Используется `@throws` в Javadoc | Да | Да (рекомендуется) |
| Назначение `@throws` | Документировать условия восстанавливаемых сбоев | Документировать предусловия метода |

Тег `@throws` следует использовать для обоих видов. При этом **не** следует добавлять `throws SomeUncheckedException` в сигнатуру — это вводит в заблуждение, намекая на checked-природу исключения.

**Почему нельзя объявлять `throws Exception` в сигнатуре:**

1. Потеря информации: вызывающий код не знает, какие конкретные исключения ожидать.
2. Принуждение к широкому `catch (Exception e)` или к декларации `throws Exception` во всей цепочке вызовов.
3. Нарушение принципа минимального удивления: вызывающий ожидает конкретных, хорошо задокументированных условий ошибки.
4. Ухудшение API: клиент не может выполнить точную, специфическую обработку ошибок.

**Консолидация документации:** если несколько методов класса бросают одно исключение по одной причине, его достаточно один раз задокументировать в Javadoc класса.

**Расхождений между источниками не выявлено.** Effective Java Item 74 и рекомендации Oracle Javadoc согласованы.

---

### Вопрос 55. Что такое «failure-capture information» (информация о сбое) в сообщении исключения? Почему важно включать значения проблемных параметров в сообщение? Как это реализовано в IndexOutOfBoundsException в Java 9?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Effective Java, 3rd Edition, Chapter 10 Exceptions — oreilly.com](https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/ch10.xhtml)

Когда программа падает с непойманным исключением, система автоматически печатает stack trace, содержащий строковое представление исключения (результат `toString()`). Часто это единственная информация, которую разработчики имеют при расследовании сбоя, особенно если его сложно воспроизвести.

**Ключевая рекомендация (Item 75):** сообщение исключения должно содержать значения всех параметров и полей, которые способствовали возникновению исключения.

Пример: для `IndexOutOfBoundsException` сообщение должно содержать нижнюю границу, верхнюю границу и значение индекса, который оказался вне диапазона. Это позволяет диагностировать проблему без воспроизведения ошибки.

**Исключение:** безопасность — не включайте пароли, ключи шифрования и другую чувствительную информацию в сообщения исключений.

Разница от сообщений для пользователя: сообщения исключений предназначены для разработчиков, а не конечных пользователей — они не обязаны быть локализованы, но должны содержать максимум диагностической информации.

#### Ответ от Claude

**Что такое failure-capture information**

«Информация о сбое» (failure-capture information) — это принцип из Effective Java Item 75 (Joshua Bloch): сообщение (`getMessage()`) исключения должно содержать все значения, непосредственно участвовавшие в возникновении ошибки. Это критично, поскольку stack trace часто является единственной информацией доступной при расследовании production-инцидента.

**Почему это важно**

```java
// Плохое сообщение — нет контекста
throw new IndexOutOfBoundsException("Index out of bounds");

// Хорошее сообщение — есть все нужные значения
throw new IndexOutOfBoundsException(
    "Index: " + index + ", Size: " + size);
```

При плохом сообщении разработчик видит только факт ошибки. При хорошем — точные значения, с которыми возникла ошибка, без необходимости воспроизводить её.

**Практика: встраивание контекста в конструктор исключения**

```java
public class OrderNotFoundException extends RuntimeException {
    private final long orderId;

    public OrderNotFoundException(long orderId) {
        super("Order not found: id=" + orderId);
        this.orderId = orderId;
    }

    public long getOrderId() {
        return orderId;
    }
}
```

Хранение значений в отдельных полях (а не только в строке сообщения) позволяет обработчику программно работать с ними через геттеры.

**Реализация в IndexOutOfBoundsException (Java 9+)**

Начиная с Java 9, `IndexOutOfBoundsException` получил конструктор с параметром `int index`:

```java
// Java 9+: конструктор с индексом
throw new IndexOutOfBoundsException(index);
// сообщение автоматически: "Index out of range: <index>"
```

Аналогично, помощные NPE-сообщения в Java 14+ (JEP 358) следуют тому же принципу — они содержат точную информацию о том, какая именно переменная или поле равно `null`.

**Важное предостережение:** не включайте в сообщения исключений чувствительные данные (пароли, токены, персональные данные). Сообщения исключений часто попадают в логи, которые могут быть доступны широкому кругу лиц.

**Расхождений между источниками не выявлено.** Effective Java Item 75 и дополнения в Java 9+ (`IndexOutOfBoundsException(int)`) согласуются в подходе.

---

### Вопрос 56. Что такое принцип «failure atomicity» (атомарность при сбое) применительно к исключениям? Перечислите основные подходы к его достижению для методов, работающих с изменяемыми объектами.

**Категория:** Исключения · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Effective Java! Strive for Failure Atomicity — dev.to/kylec32](https://dev.to/kylec32/effective-java-strive-for-failure-atomicity-4agd)

**Failure atomicity** (Effective Java, Item 76): после того как метод выбросил исключение, объект, как правило, должен оставаться в том же состоянии, что и до вызова метода. Метод с таким свойством называется *failure-atomic* (атомарным при сбое). Это особенно важно для checked-исключений: вызывающий код ожидает возможности восстановиться после них.

**Основные подходы к достижению failure atomicity:**

1. **Неизменяемые объекты** — атомарность «бесплатна»: при сбое существующий объект не меняется, а новый просто не создаётся.

2. **Проверка параметров перед изменением состояния** — наиболее распространённый подход для методов с изменяемыми объектами: выбросить исключение до начала любых изменений.

3. **Упорядочивание операций** — переместить части, которые могут завершиться сбоем, до частей, изменяющих состояние объекта.

4. **Работа с временной копией** — выполнить операцию на копии объекта и заменить оригинал только при успешном завершении.

5. **Код восстановления (recovery code)** — перехватить сбой и откатить состояние объекта к исходному (редко применяется).

#### Ответ от Claude

**Что такое failure atomicity**

Принцип failure atomicity (Effective Java Item 76, Joshua Bloch) гласит: если метод завершился исключением, объект должен оставаться в том же корректном состоянии, в котором он находился до вызова метода. Нарушение этого принципа оставляет объект в «повреждённом» состоянии, что делает любое дальнейшее его использование непредсказуемым.

**Почему это важно:** вызывающий код, поймав исключение, может попытаться продолжить работу. Если объект испорчен — это приводит к трудноуловимым ошибкам «вниз по течению».

**Пять подходов к достижению failure atomicity**

**1. Неизменяемые объекты** (наипростейший)

Для immutable-объектов проблема не существует в принципе: при создании нового объекта либо он создаётся корректно, либо не создаётся вовсе. Исходный объект не затронут.

**2. Проверка параметров перед изменением (наиболее распространённый)**

```java
// Пример из JDK: Stack.pop()
public Object pop() {
    if (size == 0) {
        throw new EmptyStackException(); // исключение ДО изменения состояния
    }
    Object result = elements[--size];    // изменение только после успешной проверки
    elements[size] = null;
    return result;
}
```

**3. Упорядочивание операций** — фазы, способные завершиться сбоем, выполняются до фаз, изменяющих состояние:

```java
public void transfer(Account source, Account destination, BigDecimal amount) {
    // Сначала вычисления (могут завершиться сбоем при overflow)
    BigDecimal newSource = source.getBalance().subtract(amount);      // может бросить ArithmeticException
    BigDecimal newDest = destination.getBalance().add(amount);        // до любых изменений
    // Только после успешного вычисления — изменение состояния
    source.setBalance(newSource);
    destination.setBalance(newDest);
}
```

**4. Работа с временной копией**

```java
public void sortList(List<String> list) {
    List<String> temp = new ArrayList<>(list); // временная копия
    Collections.sort(temp);                    // если sort бросит исключение — оригинал не тронут
    list.clear();
    list.addAll(temp);
}
```

**5. Recovery code (откат)** — используется редко, характерен для постоянного хранилища (диск, БД). По сути, реализует транзакционную семантику вручную.

**Когда failure atomicity недостижима**

Если два объекта взаимодействуют и один из них находится в несогласованном состоянии из-за сбоя конкурентного кода — достичь failure atomicity без синхронизации невозможно. В таких случаях документируйте, в каком состоянии объект окажется после исключения.

**Расхождений между источниками не выявлено.** Effective Java Item 76, qtips.github.io и другие источники согласуются в описании подходов.

---

### Вопрос 57. Чем ClassNotFoundException отличается от NoClassDefFoundError? В каких ситуациях возникает каждое из них? Почему одно является checked-исключением, а другое — Error?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ClassNotFoundException vs NoClassDefFoundError | Baeldung](https://www.baeldung.com/java-classnotfoundexception-and-noclassdeffounderror)

**ClassNotFoundException** — это checked-исключение, возникающее при попытке динамически загрузить класс во время выполнения через рефлексию, когда класс не найден в classpath. Возникает при вызовах:
- `Class.forName()`
- `ClassLoader.loadClass()`
- `ClassLoader.findSystemClass()`

Типичный пример — попытка загрузить JDBC-драйвер (`Class.forName("oracle.jdbc.driver.OracleDriver")`), когда соответствующий JAR отсутствует в classpath.

**NoClassDefFoundError** — это `Error` (подкласс `LinkageError`), возникающий когда класс был доступен в момент компиляции, но JVM не может найти его файл во время выполнения. Также возникает, если статический инициализатор класса завершился с исключением — тогда попытка создать экземпляр или обратиться к классу вызовет `NoClassDefFoundError`.

#### Ответ от Claude

**Принципиальное различие**

| Характеристика | `ClassNotFoundException` | `NoClassDefFoundError` |
|---|---|---|
| Тип | Checked Exception (наследует `ReflectiveOperationException`) | Error (наследует `LinkageError → Error`) |
| Когда возникает | Динамическая загрузка класса через рефлексию — класс не найден | Класс был при компиляции, но отсутствует при выполнении; или статический инициализатор класса завершился с исключением |
| Точка возникновения | `Class.forName()`, `ClassLoader.loadClass()` | `new ClassName()`, вызов статического метода/поля |
| Можно ли восстановиться | Да (пользователь может обработать и предложить альтернативу) | Как правило нет — неустранимый сбой среды |

**ClassNotFoundException — сценарии:**

```java
// Типичный пример: загрузка JDBC-драйвера
try {
    Class.forName("com.mysql.cj.jdbc.Driver"); // JAR не в classpath
} catch (ClassNotFoundException e) {
    System.out.println("Драйвер не найден: " + e.getMessage());
    // можно сообщить пользователю, предложить исправление
}
```

**NoClassDefFoundError — сценарии:**

```java
// Сценарий 1: класс был при компиляции, но удалён из JAR
MyClass obj = new MyClass(); // → NoClassDefFoundError: MyClass

// Сценарий 2: статический инициализатор завершился с исключением
class BadConfig {
    static final int VALUE = Integer.parseInt("invalid"); // NumberFormatException
}
// Первый вызов: ExceptionInInitializerError (cause: NumberFormatException)
// Последующие вызовы: NoClassDefFoundError (класс помечен как «ошибочный»)
```

**Почему именно такие типы в иерархии:**

- `ClassNotFoundException` — checked, потому что разработчик сознательно использует динамическую загрузку и должен явно обработать отсутствие класса.
- `NoClassDefFoundError` — Error, потому что это нарушение контракта среды выполнения: класс, скомпилированный и присутствовавший при сборке, внезапно недоступен. Это системная аномалия, восстановление от которой обычно невозможно.

**Практический совет для отладки:** если вы видите `NoClassDefFoundError` и classpath, по вашему мнению, корректен — ищите в логах предшествующий `ExceptionInInitializerError`. Это часто реальная причина.

**Расхождений между источниками не выявлено.** Baeldung, Javarevisited и GeeksforGeeks описывают различие одинаково.

---

### Вопрос 58. Что такое ConcurrentModificationException и fail-fast итераторы? Как работает механизм modCount? В каких случаях это исключение выбрасывается в однопоточном коде?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ConcurrentModificationException (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/util/ConcurrentModificationException.html)

`ConcurrentModificationException` — исключение времени выполнения, которое сигнализирует о том, что объект был изменён конкурентно, когда такая модификация недопустима.

Обнаружить такую модификацию полностью невозможно, поэтому fail-fast итераторы бросают это исключение «из лучших побуждений» (best-effort basis), а не по строгой гарантии:

> «Fail-fast iterators throw `ConcurrentModificationException` on a best-effort basis. Therefore, it would be wrong to write a program that depends on this exception for its correctness.»

Это исключение следует использовать только для обнаружения ошибок (bugs), а не как механизм обеспечения корректности программы.

#### Ответ от Claude

**Что такое ConcurrentModificationException**

`ConcurrentModificationException` — непроверяемое исключение, выбрасываемое итератором при обнаружении структурной модификации коллекции, произошедшей после его создания. Несмотря на слово «Concurrent» в названии, оно может возникать и в однопоточном коде.

**Механизм modCount (как реализованы fail-fast итераторы)**

Большинство коллекций JDK (`ArrayList`, `HashMap`, `HashSet` и т.д.) содержат внутреннее поле `modCount` (modification count) — счётчик структурных изменений:

```java
// Внутри ArrayList (упрощённо):
protected transient int modCount = 0;

// При каждом add(), remove(), clear() и т.д.:
modCount++;
```

Когда создаётся итератор, он запоминает текущее значение:

```java
// Внутри ArrayList.Itr:
int expectedModCount = modCount;
```

При каждом вызове `next()` итератор проверяет:

```java
if (modCount != expectedModCount) {
    throw new ConcurrentModificationException();
}
```

**ConcurrentModificationException в однопоточном коде**

Наиболее частая однопоточная причина — прямое изменение коллекции через методы самой коллекции во время итерации:

```java
List<String> list = new ArrayList<>(Arrays.asList("a", "b", "c"));

// НЕПРАВИЛЬНО: прямое удаление через list во время итерации
for (String s : list) {
    if (s.equals("b")) {
        list.remove(s); // → ConcurrentModificationException
    }
}
```

**Правильные способы удаления во время итерации:**

```java
// Способ 1: Iterator.remove()
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if (it.next().equals("b")) {
        it.remove(); // безопасно — не меняет expectedModCount
    }
}

// Способ 2: Collection.removeIf() (Java 8+)
list.removeIf(s -> s.equals("b"));

// Способ 3: Stream + collect
list = list.stream()
           .filter(s -> !s.equals("b"))
           .collect(Collectors.toList());
```

**Важное предупреждение из Javadoc:** fail-fast поведение не является строгой гарантией. Не пишите код, корректность которого зависит от этого исключения — используйте его только для обнаружения ошибок.

**Расхождений между источниками не выявлено.** Oracle Javadoc и Baeldung единогласно описывают fail-fast-механизм и его ограничения.

---

### Вопрос 59. Что такое StackOverflowError? Каковы типичные причины его возникновения? Что такое размер стека потока и как на него влияет JVM-опция -Xss?

**Категория:** Исключения · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [StackOverflowError (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/lang/StackOverflowError.html)

`StackOverflowError` — подкласс `VirtualMachineError` (который наследует `Error`), выбрасываемый при переполнении стека вызовов потока из-за слишком глубокой рекурсии.

Иерархия: `Object → Throwable → Error → VirtualMachineError → StackOverflowError`.

Существует с JDK 1.0. Конструкторы: без параметров и с `String`-сообщением.

#### Ответ от Claude

**Что такое StackOverflowError**

`StackOverflowError` — это `Error` (подкласс `VirtualMachineError`), сигнализирующий, что поток исчерпал выделенное ему стековое пространство. Каждый поток в Java имеет собственный стек вызовов (call stack); при вызове каждого нового метода на стек добавляется фрейм. При бесконечной или слишком глубокой рекурсии фреймы накапливаются до исчерпания стека.

**Иерархия:**
```
Throwable → Error → VirtualMachineError → StackOverflowError
```

**Типичные причины**

1. **Бесконечная рекурсия** — метод вызывает себя без правильного базового случая:

```java
// Ошибка: нет базового случая
int factorial(int n) {
    return n * factorial(n - 1); // → StackOverflowError
}

// Правильно: с базовым случаем
int factorial(int n) {
    if (n <= 1) return 1;       // базовый случай
    return n * factorial(n - 1);
}
```

2. **Взаимная рекурсия** — два метода вызывают друг друга без условия выхода:

```java
void methodA() { methodB(); }
void methodB() { methodA(); } // → StackOverflowError
```

3. **Слишком глубокая корректная рекурсия** — базовый случай есть, но входные данные настолько большие, что стек исчерпывается раньше достижения базового случая.

4. **Циклические зависимости в `equals()`/`hashCode()`/`toString()`** — объект A ссылается на B, B ссылается на A, оба вызывают методы друг друга.

**Размер стека потока и опция `-Xss`**

Каждый поток Java получает собственный стек. Размер стека по умолчанию зависит от JVM и ОС:

| Конфигурация | Размер стека по умолчанию |
|---|---|
| 64-битная JVM (HotSpot) | ~512 КБ – 1 МБ |
| 32-битная JVM | ~256 – 320 КБ |

Опция `-Xss` позволяет изменить размер стека каждого потока:

```
java -Xss2m MyApp       # 2 МБ на поток
java -Xss512k MyApp     # 512 КБ на поток
```

При `-Xss2m` (против дефолтного ~1 МБ) количество допустимых рекурсивных вызовов увеличивается примерно пропорционально.

**Предостережение:** увеличение `-Xss` означает бо́льшее потребление нативной памяти на каждый поток. В приложениях с большим числом потоков это может привести к исчерпанию нативной памяти (`OutOfMemoryError: unable to create new native thread`).

**Правильное решение:** рефакторинг рекурсии в итерацию (с явным стеком данных) — надёжнее и эффективнее, чем увеличение `-Xss`.

**Расхождений между источниками не выявлено.** Oracle Javadoc, Baeldung (java-call-stack-max-depth) и DZone описывают механизм одинаково.

---

### Вопрос 60. В чём разница между IllegalArgumentException и IllegalStateException? Как выбрать правильное исключение и почему конвенция предписывает использовать NullPointerException, а не IllegalArgumentException, при передаче null?

**Категория:** Исключения · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [IllegalArgumentException (Java SE) — docs.oracle.com](https://docs.oracle.com/javame/config/cdc/ref-impl/fp1.1.2/jsr219/java/lang/IllegalArgumentException.html)

`IllegalArgumentException` — непроверяемое исключение, сигнализирующее, что методу или конструктору передан недопустимый или несоответствующий аргумент.

> Источник: [IllegalStateException (Java SE) — docs.oracle.com](https://docs.oracle.com/javame/config/cdc/ref-impl/cdc1.1.2/jsr218/java/lang/IllegalStateException.html)

`IllegalStateException` — сигнализирует, что метод вызван в недопустимое время. Другими словами, Java-среда или Java-приложение находятся не в том состоянии, которое требуется для запрошенной операции.

#### Ответ от Claude

**Ключевое различие**

Оба исключения являются непроверяемыми (unchecked, наследники `RuntimeException`), но различаются по семантике:

| | `IllegalArgumentException` | `IllegalStateException` |
|---|---|---|
| Причина | Проблема с **аргументом** метода | Проблема с **состоянием** объекта |
| Вопрос | «Что передали?» | «Когда вызвали?» |
| Пример | `setAge(-5)` — отрицательный возраст | `iterator.remove()` до `next()` |

**Когда применять каждое**

`IllegalArgumentException` — аргумент недопустим независимо от состояния объекта:

```java
public void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Age cannot be negative: " + age);
    }
    this.age = age;
}
```

`IllegalStateException` — аргумент мог бы быть корректным, но текущее состояние объекта не позволяет выполнить операцию:

```java
public void start() {
    if (isRunning) {
        throw new IllegalStateException("Already started");
    }
    // запуск
}
```

**Правило выбора (Effective Java, Item 72):**

> Если при любом значении аргумента вызов метода был бы неуспешным — это `IllegalStateException`. Если только при конкретном значении аргумента — `IllegalArgumentException`.

**Почему `NullPointerException`, а не `IllegalArgumentException` при null**

По конвенции Java (Effective Java Item 49, 72 и Oracle API Guide), если параметр равен `null` там, где это запрещено — следует бросать `NullPointerException`, а **не** `IllegalArgumentException`. Причины:

1. **Специализация:** `NullPointerException` — более конкретный тип, точнее описывающий проблему.
2. **Инструменты:** IDE, анализаторы кода (SpotBugs, SonarQube) и аннотации (`@NonNull`, `@NotNull`) работают именно с `NullPointerException`.
3. **Единообразие:** JDK-методы (`Objects.requireNonNull()`) при обнаружении `null` бросают именно `NullPointerException`.

```java
public void process(String name) {
    Objects.requireNonNull(name, "name must not be null"); // бросает NPE
    // или: if (name == null) throw new NullPointerException("name");
}
```

**Итог:** `NullPointerException` — для null-аргументов; `IndexOutOfBoundsException` — для индексов вне диапазона; `IllegalArgumentException` — для всех остальных недопустимых значений параметров; `IllegalStateException` — для вызовов в неподходящем состоянии объекта.

**Расхождений между источниками не выявлено.** Oracle Javadoc, Effective Java и Tutorialspoint единогласны в описании конвенций.

---
