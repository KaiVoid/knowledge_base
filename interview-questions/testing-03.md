# Тестирование — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/19-testing.md](../knowledge-base/19-testing.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](testing-01.md) · [ч.2](testing-02.md) · **ч.3**

---
### Вопрос 41. Как в JUnit 5 ограничить время выполнения теста с помощью @Timeout? Чем @Timeout отличается от assertTimeout() и assertTimeoutPreemptively() из Assertions?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Timeouts :: JUnit User Guide (docs.junit.org)](https://docs.junit.org/6.1.0/writing-tests/timeouts.html)

Аннотация `@Timeout` позволяет объявить, что тест, фабрика тестов, шаблон теста или метод жизненного цикла должны завершиться с ошибкой, если время их выполнения превышает заданную продолжительность. По умолчанию единица времени — секунды, но её можно настроить через параметр `unit`.

Аннотация поддерживает три режима потока (`threadMode`):

1. **SAME_THREAD** (рекомендуется): тело теста выполняется в основном потоке; таймаут прерывает его из вспомогательного потока. Совместим с фреймворками, использующими `ThreadLocal` (например, Spring).
2. **SEPARATE_THREAD**: тело теста выполняется в отдельном потоке, аналогично `assertTimeoutPreemptively()`. Может приводить к нежелательным побочным эффектам.
3. **INFERRED** (по умолчанию): режим определяется через конфигурационный параметр `junit.jupiter.execution.timeout.thread.mode.default`, который по умолчанию равен `SAME_THREAD`.

**Отличия `assertTimeout` и `assertTimeoutPreemptively`:**

- `assertTimeout()`: исполняемый код запускается в **том же потоке**, что и вызывающий код. Если таймаут превышен, тест не прерывается принудительно — он завершается, и только тогда фиксируется провал. Сообщение об ошибке: `"execution exceeded timeout of 10 ms by 91 ms"`.
- `assertTimeoutPreemptively()`: исполняемый код запускается в **отдельном потоке**. Выполнение прерывается по истечении таймаута. Сообщение: `"execution timed out after 10 ms"`. Однако это может вызвать проблемы с кодом, использующим `ThreadLocal` (например, транзакционные тесты Spring не будут откатываться).

#### Ответ от Claude

**Аннотация @Timeout**

```java
@Test
@Timeout(5)                          // 5 секунд (по умолчанию)
void testCompletesInFiveSeconds() { ... }

@Test
@Timeout(value = 500, unit = TimeUnit.MILLISECONDS)
void testCompletesInHalfSecond() { ... }
```

Атрибуты:
- `value` (long, обязательный) — продолжительность таймаута.
- `unit` (TimeUnit, по умолчанию `SECONDS`) — единица времени.
- `threadMode` (Timeout.ThreadMode, по умолчанию `INFERRED`) — режим потока.

Аннотацию можно ставить на уровне класса — тогда она распространяется на все `@Test`-методы и вложенные `@Nested`-классы, но **не** на методы жизненного цикла (`@BeforeEach` и т.п.). Для `@TestFactory`-методов учитывается только время самого фабричного метода, но не выполнение каждого `DynamicTest`.

Глобальный таймаут по умолчанию задаётся через конфигурационный параметр `junit.jupiter.execution.timeout.default` (например, `500 ms`).

**assertTimeout() — тот же поток**

```java
@Test
void testWithSameThreadTimeout() {
    assertTimeout(Duration.ofMillis(100), () -> {
        // выполняется в том же потоке
        Thread.sleep(50);
    });
}
```

Код выполняется в **том же потоке**. Если лимит превышен, выполнение **не прерывается** — тест продолжает работать до конца, после чего фиксируется провал с сообщением вида `"execution exceeded timeout of 100 ms by 42 ms"`. Подходит для кода, зависящего от `ThreadLocal`.

**assertTimeoutPreemptively() — отдельный поток**

```java
@Test
void testWithPreemptiveTimeout() {
    assertTimeoutPreemptively(Duration.ofMillis(100), () -> {
        // выполняется в отдельном потоке
        Thread.sleep(200); // будет прервано
    });
}
```

Код выполняется в **отдельном потоке**. При превышении таймаута поток принудительно прерывается. Сообщение: `"execution timed out after 100 ms"`. Не следует использовать с кодом, зависящим от `ThreadLocal` (транзакционные тесты Spring могут не откатываться).

**Сводная таблица различий**

| Характеристика | `@Timeout` | `assertTimeout()` | `assertTimeoutPreemptively()` |
|---|---|---|---|
| Область применения | метод/класс/жизненный цикл | фрагмент кода внутри теста | фрагмент кода внутри теста |
| Поток выполнения | зависит от threadMode (по умолчанию SAME_THREAD) | тот же поток | отдельный поток |
| Принудительное прерывание | зависит от threadMode | нет | да |
| Совместимость с ThreadLocal | да (SAME_THREAD) | да | нет |

---

### Вопрос 42. Что такое @RepeatedTest в JUnit 5? Какие атрибуты он поддерживает (name, failureThreshold) и как внутри тела теста получить информацию о текущей итерации через RepetitionInfo?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Repeated Tests :: JUnit User Guide (docs.junit.org)](https://docs.junit.org/5.14.1/writing-tests/repeated-tests)

`@RepeatedTest` сигнализирует, что аннотированный метод является шаблоном теста, который должен выполняться заданное количество раз. Каждое выполнение ведёт себя как полноценный `@Test`-метод с поддержкой всех коллбэков жизненного цикла.

**Атрибут `name`** позволяет задать шаблон отображаемого имени для каждого повторения. Поддерживаются плейсхолдеры:
- `{displayName}` — отображаемое имя метода;
- `{currentRepetition}` — номер текущего повторения;
- `{totalRepetitions}` — общее количество повторений.

Значение по умолчанию соответствует константе `SHORT_DISPLAY_NAME`: `"repetition {currentRepetition} of {totalRepetitions}"`. Также доступна константа `LONG_DISPLAY_NAME`: `"{displayName} :: repetition {currentRepetition} of {totalRepetitions}"`.

**Атрибут `failureThreshold`** (добавлен в JUnit 5.10, экспериментальный) задаёт количество неудач, после которого оставшиеся повторения автоматически пропускаются. По умолчанию: `Integer.MAX_VALUE` (порог не применяется). Значение должно быть больше нуля и меньше общего числа повторений.

**RepetitionInfo** — интерфейс, предоставляющий метаданные о текущем повторении. Он инжектируется фреймворком через `RepetitionInfoParameterResolver` и доступен только в контексте `@RepeatedTest`. Методы интерфейса:
- `getCurrentRepetition()` — номер текущего повторения (начиная с 1);
- `getTotalRepetitions()` — общее количество повторений.

```java
@RepeatedTest(value = 5, name = "{displayName} {currentRepetition}/{totalRepetitions}")
void customTest(RepetitionInfo repetitionInfo) {
    assertEquals(5, repetitionInfo.getTotalRepetitions());
}
```

#### Ответ от Claude

**Что такое @RepeatedTest**

`@RepeatedTest` — аннотация JUnit Jupiter, превращающая метод в шаблон теста, который выполняется указанное количество раз. Каждое выполнение получает собственный экземпляр тестового класса (если не используется `@TestInstance(PER_CLASS)`) и полный цикл `@BeforeEach` / `@AfterEach`.

**Атрибуты аннотации**

```java
@RepeatedTest(
    value = 10,                         // обязательный: число повторений (> 0)
    name = "{displayName} [{currentRepetition}/{totalRepetitions}]",
    failureThreshold = 3                // экспериментальный, с JUnit 5.10
)
void repeatedTest() { ... }
```

- `value` (int, обязательный) — число повторений; должно быть больше нуля.
- `name` (String) — шаблон имени повторения. Плейсхолдеры: `{displayName}`, `{currentRepetition}`, `{totalRepetitions}`. По умолчанию используется `SHORT_DISPLAY_NAME` = `"repetition {currentRepetition} of {totalRepetitions}"`. Константа `RepeatedTest.LONG_DISPLAY_NAME` даёт `"{displayName} :: repetition {currentRepetition} of {totalRepetitions}"`.
- `failureThreshold` (int, с JUnit 5.10, **экспериментальный**) — число неудач, после которого оставшиеся повторения **пропускаются** (статус `SKIPPED`, а не `FAILED`). Значение по умолчанию: `Integer.MAX_VALUE` (пороговое поведение отключено). Значение должно быть положительным и меньше `value`. Удобно для обнаружения флапающих (flaky) тестов: `failureThreshold = 1` остановит серию после первой неудачи.

**Получение информации о текущей итерации через RepetitionInfo**

Интерфейс `RepetitionInfo` инжектируется через параметр метода — JUnit сам определяет, что нужно передать, через встроенный `RepetitionInfoParameterResolver`.

```java
@RepeatedTest(5)
void testWithRepetitionInfo(RepetitionInfo repetitionInfo) {
    int current = repetitionInfo.getCurrentRepetition(); // 1, 2, 3, 4, 5
    int total   = repetitionInfo.getTotalRepetitions();  // всегда 5

    System.out.printf("Повторение %d из %d%n", current, total);

    // Пример: разное поведение на первой и последней итерации
    if (current == 1) {
        // инициализация
    }
    if (current == total) {
        // финальная проверка
    }
}
```

Интерфейс доступен **только** внутри методов, аннотированных `@RepeatedTest`. В `@Test`-методах он не инжектируется.

**Пример с failureThreshold**

```java
@RepeatedTest(value = 10, failureThreshold = 2)
void flakynessCheck() {
    // При 2-й неудаче оставшиеся повторения (3–10) будут пропущены.
    // Это позволяет быстро выявить нестабильный тест.
    assertThat(externalService.call()).isTrue();
}
```

**Важное замечание:** `failureThreshold` — экспериментальный API (аннотирован `@API(status = EXPERIMENTAL)`), его поведение может меняться в будущих версиях JUnit.
### Вопрос 43. Как реализовать кастомный ArgumentConverter для @ParameterizedTest в JUnit 5 с помощью @ConvertWith? Какое различие между реализацией интерфейса ArgumentConverter напрямую и расширением SimpleArgumentConverter или TypedArgumentConverter?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Parameterized Classes and Tests :: JUnit User Guide](https://docs.junit.org/5.14.3/writing-tests/parameterized-classes-and-tests.html)

Вместо неявного преобразования аргументов можно явно указать `ArgumentConverter` для конкретного параметра с помощью аннотации `@ConvertWith`. Реализация `ArgumentConverter` должна быть объявлена как класс верхнего уровня или как статический вложенный класс.

Пример: конвертер, расширяющий `SimpleArgumentConverter`, который преобразует объект в строку:

```java
@ParameterizedTest
@EnumSource(ChronoUnit.class)
void testWithExplicitArgumentConversion(
        @ConvertWith(ToStringArgumentConverter.class) String argument) {
    assertNotNull(ChronoUnit.valueOf(argument));
}

public class ToStringArgumentConverter extends SimpleArgumentConverter {
    @Override
    protected Object convert(Object source, Class<?> targetType) {
        assertEquals(String.class, targetType, "Can only convert to String");
        if (source instanceof Enum<?>) {
            return ((Enum<?>) source).name();
        }
        return String.valueOf(source);
    }
}
```

Если конвертер всегда преобразует один конкретный тип в другой, можно расширить `TypedArgumentConverter`, чтобы избежать boilerplate-проверок типов:

```java
public class ToLengthArgumentConverter
        extends TypedArgumentConverter<String, Integer> {

    protected ToLengthArgumentConverter() {
        super(String.class, Integer.class);
    }

    @Override
    protected Integer convert(String source) throws ArgumentConversionException {
        return source != null ? source.length() : 0;
    }
}
```

JUnit Jupiter поставляется с одним встроенным явным конвертером — `JavaTimeArgumentConverter`, который используется через составную аннотацию `@JavaTimeConversionPattern`.

#### Ответ от Claude

**Аннотация `@ConvertWith`** указывает JUnit 5, какой `ArgumentConverter` использовать для преобразования аргумента параметра `@ParameterizedTest` перед его передачей в тестовый метод. Реализация должна быть классом верхнего уровня или `static`-вложенным классом; она обязана иметь конструктор без аргументов или единственный однозначный конструктор.

**Три варианта реализации конвертера:**

| Вариант | Когда использовать | Абстрактный метод |
|---|---|---|
| `ArgumentConverter` (интерфейс напрямую) | Нужен полный доступ к `ParameterContext` (например, к аннотациям параметра или его позиции) | `convert(Object source, ParameterContext context)` |
| `SimpleArgumentConverter` (абстрактный класс) | Достаточно знать только целевой тип (`Class<?> targetType`), контекст параметра не нужен | `convert(Object source, Class<?> targetType)` |
| `TypedArgumentConverter<S, T>` (абстрактный класс) | Конвертер всегда работает ровно с одной парой типов S -> T; нужна compile-time типобезопасность | `convert(S source)` |

**Ключевые различия:**

- **`ArgumentConverter` напрямую** — максимальная гибкость: методу `convert` передаётся `ParameterContext`, через который можно получить аннотации параметра, его тип, индекс в сигнатуре и прочее. Используется, если логика конвертации зависит от метаданных параметра.

- **`SimpleArgumentConverter`** — убирает необходимость работать с `ParameterContext`; JUnit сам извлекает целевой тип и делегирует в упрощённый метод `convert(Object source, Class<?> targetType)`. Подходит для большинства практических задач (например, `String` -> `LocalDate`).

- **`TypedArgumentConverter<S, T>`** — строгая типизация на уровне generics; в конструкторе явно указываются исходный и целевой классы (`super(String.class, Integer.class)`), а переопределяемый метод уже принимает конкретный тип `S`. Это исключает ошибки приведения типов во время выполнения и устраняет boilerplate-проверки вроде `assertEquals(targetType, ...)`.

**Пример с `ArgumentConverter` напрямую** (требуется доступ к аннотации параметра):

```java
public class AnnotationAwareConverter implements ArgumentConverter {
    @Override
    public Object convert(Object source, ParameterContext context)
            throws ArgumentConversionException {
        // Получаем аннотацию прямо с параметра
        MyFormat fmt = context.findAnnotation(MyFormat.class)
                              .orElseThrow(() -> new ArgumentConversionException("No @MyFormat"));
        return parseWithFormat(source.toString(), fmt.pattern());
    }
}
```

**Встроенный пример из JUnit** — `JavaTimeArgumentConverter` расширяет `AnnotationBasedArgumentConverter` (надстройку над `ArgumentConverter`) и работает через составную аннотацию `@JavaTimeConversionPattern`:

```java
@ParameterizedTest
@ValueSource(strings = { "01.01.2017", "31.12.2017" })
void testWithJavaTimeConverter(
        @JavaTimeConversionPattern("dd.MM.yyyy") LocalDate argument) {
    assertEquals(2017, argument.getYear());
}
```

Источники, сверенные при подготовке ответа:
- [JUnit 5 User Guide — Parameterized Tests: Explicit Argument Conversion](https://docs.junit.org/5.14.3/writing-tests/parameterized-classes-and-tests.html)
- [ArgumentConverter Javadoc (JUnit 5 API)](https://docs.junit.org/current/api/org.junit.jupiter.params/org/junit/jupiter/params/converter/ArgumentConverter.html)
- [SimpleArgumentConverter Javadoc](https://docs.junit.org/current/api/org.junit.jupiter.params/org/junit/jupiter/params/converter/SimpleArgumentConverter.html)
- [TypedArgumentConverter Javadoc](https://docs.junit.org/current/api/org.junit.jupiter.params/org/junit/jupiter/params/converter/TypedArgumentConverter.html)

---

### Вопрос 44. Что такое AssertJ SoftAssertions? Как они работают и чем отличаются от стандартных hard assertions? Назовите три способа работы с SoftAssertions (экземпляр + assertAll, assertSoftly, @ExtendWith(SoftAssertionsExtension.class)).

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Multiple ways of using soft asserts in JUnit 5 — Scott Selikoff & Jeanne Boyarsky](https://www.selikoff.net/2024/03/23/multiple-ways-of-using-soft-asserts-in-junit-5/)

Soft assertions в AssertJ позволяют выполнить несколько проверок подряд, не останавливаясь на первом же провале: все ошибки собираются и выдаются вместе в конце теста.

**Важный момент:** если создать экземпляр `SoftAssertions` и вызвать проверки, но забыть вызвать `assertAll()` — тест молча пройдёт, даже если все утверждения неверны.

**Способ 1 — явный вызов `assertAll()`:**

```java
@Test
void callingAssertAll() {
    var softly = new SoftAssertions();
    softly.assertThat("robot").isEqualTo("izzy");
    softly.assertThat(126).isLessThanOrEqualTo(125);
    softly.assertAll(); // обязательный вызов в конце
}
```

**Способ 2 — лямбда `SoftAssertions.assertSoftly()`:**

```java
@Test
void lambda() {
    SoftAssertions.assertSoftly(s -> {
        s.assertThat("robot").isEqualTo("izzy");
        s.assertThat(126).isLessThanOrEqualTo(125);
    }); // assertAll() вызывается автоматически по завершении лямбды
}
```

**Способ 3а — расширение JUnit 5, инъекция в поле:**

```java
@ExtendWith(SoftAssertionsExtension.class)
class SoftAssertionsExtensionTest {
    @InjectSoftAssertions
    SoftAssertions softly;

    @Test
    void field() {
        softly.assertThat("robot").isEqualTo("izzy");
        softly.assertThat(126).isLessThanOrEqualTo(125);
        // assertAll() вызывается расширением автоматически после теста
    }
}
```

**Способ 3б — расширение JUnit 5, инъекция в параметр метода:**

```java
@ExtendWith(SoftAssertionsExtension.class)
class SoftAssertionsExtensionTest {
    @Test
    void parameter(SoftAssertions softly) {
        softly.assertThat("robot").isEqualTo("izzy");
        softly.assertThat(126).isLessThanOrEqualTo(125);
    }
}
```

#### Ответ от Claude

**Hard assertions (стандартные)** — прерывают тест при первом же провале. Если из десяти проверок упала первая, оставшиеся девять не выполняются, и разработчик видит только одну ошибку за прогон.

**SoftAssertions** — собирают все провалившиеся утверждения в список и бросают исключение (MultipleFailuresError) только в конце, показывая сразу все проблемы. Это ускоряет диагностику, особенно при проверке нескольких полей объекта или нескольких условий одного ответа API.

**Как работает механизм сбора:** `SoftAssertions` перехватывает исключения `AssertionError` внутри каждого `assertThat(...)` и добавляет их в внутренний список вместо немедленного выброса. Метод `assertAll()` проверяет этот список и, если он непуст, собирает все сообщения в одно исключение.

**Три основных способа (по условию вопроса):**

**1. Экземпляр + `assertAll()`** — базовый, явный подход. Требует помнить про вызов `assertAll()` в конце — иначе провальные проверки будут проигнорированы.

```java
SoftAssertions softly = new SoftAssertions();
softly.assertThat(order.getStatus()).isEqualTo("PAID");
softly.assertThat(order.getTotal()).isEqualByComparingTo(new BigDecimal("99.99"));
softly.assertThat(order.getItems()).hasSize(3);
softly.assertAll();
```

**2. `SoftAssertions.assertSoftly(Consumer<SoftAssertions>)`** — статический фабричный метод; `assertAll()` вызывается автоматически при выходе из лямбды (даже при исключении). Более безопасный вариант, исключающий забытый `assertAll()`.

```java
SoftAssertions.assertSoftly(softly -> {
    softly.assertThat(order.getStatus()).isEqualTo("PAID");
    softly.assertThat(order.getTotal()).isEqualByComparingTo(new BigDecimal("99.99"));
    softly.assertThat(order.getItems()).hasSize(3);
});
```

**3. `@ExtendWith(SoftAssertionsExtension.class)`** — JUnit 5-расширение; `SoftAssertionsExtension` реализует `AfterTestExecutionCallback`, поэтому `assertAll()` вызывается фреймворком автоматически после каждого теста. Инъекция возможна двумя способами:
  - через поле, аннотированное `@InjectSoftAssertions` (доступно с AssertJ 3.18.0);
  - через параметр тестового метода.

```java
@ExtendWith(SoftAssertionsExtension.class)
class OrderServiceTest {
    @InjectSoftAssertions
    private SoftAssertions softly;

    @Test
    void orderIsValid() {
        softly.assertThat(order.getStatus()).isEqualTo("PAID");
        softly.assertThat(order.getItems()).hasSize(3);
        // assertAll() — ответственность расширения
    }
}
```

**Сравнение подходов:**

| Подход | Автоматический assertAll() | Требует аннотаций JUnit | Подходит для |
|---|---|---|---|
| Экземпляр + `assertAll()` | Нет | Нет | Любой фреймворк |
| `assertSoftly()` | Да (лямбда) | Нет | Компактные тесты |
| `SoftAssertionsExtension` | Да (расширение) | `@ExtendWith` | JUnit 5 проекты |

Источники, сверенные при подготовке ответа:
- [Multiple ways of using soft asserts in JUnit 5 — selikoff.net (2024)](https://www.selikoff.net/2024/03/23/multiple-ways-of-using-soft-asserts-in-junit-5/)
- [AssertJ — Fluent testing assertions for Java and the JVM (assertj.github.io)](https://assertj.github.io/doc/)
- [SoftAssertionsExtension Javadoc (AssertJ 3.22.0)](https://www.javadoc.io/static/org.assertj/assertj-core/3.22.0/org/assertj/core/api/junit/jupiter/SoftAssertionsExtension.html)

---

### Вопрос 45. Как в AssertJ сравнить два объекта поле за полем с помощью usingRecursiveComparison()? Какие методы позволяют игнорировать отдельные поля (ignoringFields, ignoringFieldsMatchingRegexes, ignoringFieldsOfTypes) и зачем это нужно на практике?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [AssertJ — Fluent testing assertions for Java and the JVM (официальная документация)](https://assertj.github.io/doc/)

`usingRecursiveComparison()` позволяет сравнивать объекты рекурсивно, поле за полем, без необходимости реализовывать `equals()` в сравниваемых классах.

**Базовый пример:**

```java
assertThat(sherlock)
    .usingRecursiveComparison()
    .isEqualTo(sherlock2);
```

**`ignoringFields(String... fieldsToIgnore)`** — исключает конкретные поля по имени. Вложенные поля указываются через точку:

```java
assertThat(sherlock)
    .usingRecursiveComparison()
    .ignoringFields("name", "home.address.street")
    .isEqualTo(moriarty);
```

**`ignoringFieldsMatchingRegexes(String... regexes)`** — исключает поля, имена которых соответствуют регулярным выражениям. Вложенные пути экранируют точку (`\.`):

```java
assertThat(sherlock)
    .usingRecursiveComparison()
    .ignoringFieldsMatchingRegexes(".*me")
    .isEqualTo(moriarty);
```

**`ignoringFieldsOfTypes(Class<?>... types)`** — исключает все поля заданного типа на любом уровне вложенности:

```java
assertThat(sherlock)
    .usingRecursiveComparison()
    .ignoringFieldsOfTypes(double.class, Address.class)
    .isEqualTo(tallSherlock);
```

#### Ответ от Claude

**Зачем нужен `usingRecursiveComparison()`**

По умолчанию AssertJ вызывает `equals()` для сравнения объектов. Если `equals()` не переопределён — сравниваются ссылки, что бесполезно для DTO и сущностей. `usingRecursiveComparison()` обходит это ограничение: AssertJ сам обходит граф объектов и сравнивает каждое поле через рефлексию.

**Базовое использование:**

```java
// Классы Person и Address могут не иметь equals()
Person expected = new Person("Sherlock", 1.8, new Address("Baker Street", 221));
Person actual   = personService.findById(1L);

assertThat(actual)
    .usingRecursiveComparison()
    .isEqualTo(expected);
```

**Три метода для исключения полей:**

**1. `ignoringFields(String... fieldsToIgnore)`**

Исключает конкретные поля по имени. Поддерживает dot-notation для вложенных полей.

```java
// Игнорировать id (генерируется БД) и вложенное поле home.address.street
assertThat(savedPerson)
    .usingRecursiveComparison()
    .ignoringFields("id", "createdAt", "home.address.street")
    .isEqualTo(expectedPerson);
```

*Практическое применение:* поля, которые невозможно предсказать в тесте — автогенерируемые ID, временные метки (`createdAt`, `updatedAt`), версионные поля (`@Version`).

**2. `ignoringFieldsMatchingRegexes(String... regexes)`**

Исключает поля, чьё полное имя (включая путь) совпадает с хотя бы одним из переданных регулярных выражений. Точки в пути к вложенным полям экранируются как `\.`.

```java
// Игнорировать все поля, оканчивающиеся на "At" (createdAt, updatedAt, deletedAt)
assertThat(actualOrder)
    .usingRecursiveComparison()
    .ignoringFieldsMatchingRegexes(".*At", ".*[Ii]d")
    .isEqualTo(expectedOrder);
```

*Практическое применение:* когда полей с похожим паттерном много и перечислять каждое нецелесообразно; например, все audit-поля по соглашению оканчиваются на `At`.

**3. `ignoringFieldsOfTypes(Class<?>... types)`**

Исключает все поля заданного типа на всех уровнях вложенности, включая коллекции элементов этого типа.

```java
// Игнорировать все поля типа UUID и LocalDateTime
assertThat(actualInvoice)
    .usingRecursiveComparison()
    .ignoringFieldsOfTypes(UUID.class, LocalDateTime.class)
    .isEqualTo(expectedInvoice);
```

*Практическое применение:* когда определённые типы (например, `UUID`, `Instant`, `BigDecimal` при сравнении с погрешностью) неудобны для точного сравнения или их значения непредсказуемы.

**Методы можно комбинировать в одной цепочке:**

```java
assertThat(actualResponse)
    .usingRecursiveComparison()
    .ignoringFields("id", "auditInfo.createdBy")
    .ignoringFieldsMatchingRegexes(".*At")
    .ignoringFieldsOfTypes(UUID.class)
    .isEqualTo(expectedResponse);
```

**Сравнение трёх методов:**

| Метод | Критерий исключения | Гибкость | Типичный случай |
|---|---|---|---|
| `ignoringFields` | Точное имя поля (с путём) | Низкая | 1–3 конкретных поля |
| `ignoringFieldsMatchingRegexes` | Regex по имени поля | Высокая | Группа полей по соглашению |
| `ignoringFieldsOfTypes` | Java-тип поля | Средняя | Все поля одного типа |

Источники, сверенные при подготовке ответа:
- [AssertJ — официальная документация, раздел Recursive Comparison](https://assertj.github.io/doc/)
- [Awesome AssertJ: Comparing Objects Recursively — JDriven Blog (2024)](https://jdriven.com/blog/2024/09/Awesome-AssertJ-Comparing-Objects-Recursively)
- [RecursiveComparisonAssert Javadoc (AssertJ 3.12.0)](https://joel-costigliola.github.io/assertj/core-8/api/org/assertj/core/api/RecursiveComparisonAssert.html)
### Вопрос 46. Как подключить и использовать Testcontainers в интеграционном тесте с JUnit 5? Чем аннотационный подход @Testcontainers + @Container отличается от управления жизненным циклом контейнера вручную через статическое поле?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Jupiter / JUnit 5 — Testcontainers for Java](https://java.testcontainers.org/test_framework_integration/junit_5/)

Для интеграции с JUnit 5 необходимо добавить две зависимости (помимо самого Testcontainers-модуля для нужной СУБД):

```xml
<!-- Maven -->
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>2.0.5</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>2.0.5</version>
    <scope>test</scope>
</dependency>
```

Аннотация `@Testcontainers` активирует JUnit 5-расширение (`TestcontainersExtension`), которое сканирует поля, помеченные `@Container`, и автоматически управляет их жизненным циклом.

**Статическое поле — контейнер запускается один раз для всего класса:**

```java
@Testcontainers
class MyTest {
    @Container
    private static final PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @Test
    void test1() {
        // postgres уже запущен, используется один экземпляр
    }

    @Test
    void test2() {
        // тот же экземпляр, данные НЕ сбрасываются автоматически
    }
}
```

**Поле экземпляра — контейнер стартует и останавливается перед/после каждого теста:**

```java
@Testcontainers
class MyTest {
    @Container
    private final PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @Test
    void test1() { /* свежий контейнер */ }

    @Test
    void test2() { /* ещё один свежий контейнер */ }
}
```

Документация прямо предупреждает: не смешивайте аннотационный подход с ручным управлением — их одновременное использование порождает трудноотлаживаемые проблемы жизненного цикла.

#### Ответ от Claude

**Подключение**

Минимальный набор зависимостей для JUnit 5 (Gradle):

```groovy
testImplementation "org.testcontainers:testcontainers:2.0.5"
testImplementation "org.testcontainers:junit-jupiter:2.0.5"
// модуль для конкретной СУБД, например:
testImplementation "org.testcontainers:postgresql:2.0.5"
```

**Аннотационный подход: @Testcontainers + @Container**

`@Testcontainers` регистрирует `TestcontainersExtension`. Расширение ищет все поля с `@Container` и управляет ими по правилу:

| Тип поля | Старт | Остановка |
|----------|-------|-----------|
| `static` | один раз перед первым тестом класса | после последнего теста класса |
| экземпляра | перед каждым тестом (`@BeforeEach`) | после каждого теста (`@AfterEach`) |

Пример со Spring Boot и `@ServiceConnection` (Boot 3.1+):

```java
@SpringBootTest
@Testcontainers
class OrderServiceIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private OrderService orderService;

    @Test
    void shouldCreateOrder() {
        // Spring автоматически получает URL/credentials из контейнера
    }
}
```

`@ServiceConnection` (Spring Boot 3.1+) автоматически создаёт `ConnectionDetails`-бины и переопределяет свойства подключения — `@DynamicPropertySource` больше не нужен.

**Ручное управление жизненным циклом (Singleton Pattern)**

Применяется, когда один и тот же контейнер должен жить на протяжении нескольких тестовых классов. Используется статический инициализатор в абстрактном базовом классе:

```java
public abstract class AbstractIntegrationTest {

    static final PostgreSQLContainer<?> POSTGRES;
    static final KafkaContainer KAFKA;

    static {
        POSTGRES = new PostgreSQLContainer<>("postgres:16-alpine");
        KAFKA = new KafkaContainer(
            DockerImageName.parse("confluentinc/cp-kafka:7.6.1"));
        // start() вызывается явно — один раз при загрузке класса
        POSTGRES.start();
        KAFKA.start();
    }
}

class OrderServiceTest extends AbstractIntegrationTest {
    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", POSTGRES::getJdbcUrl);
    }

    @Test
    void test() { /* контейнеры уже готовы */ }
}
```

Ryuk-контейнер (встроенный в Testcontainers) завершает синглтон-контейнеры автоматически при выходе JVM — явный `stop()` не требуется.

**Ключевые отличия двух подходов**

| Критерий | @Testcontainers + @Container | Ручной (singleton) |
|----------|------------------------------|-------------------|
| Гранулярность | класс или метод | произвольно, обычно вся сборка |
| Повторное использование между классами | нет (для статик — только внутри класса) | да, через базовый класс |
| Аннотационный оверхед | минимальный | нет |
| Опасность смешивания | высокая | нет (аннотации не используются) |
| Рекомендуется при | тестах одного класса / изоляции | большом количестве интеграционных классов, единый набор инфраструктуры |

Документация явно запрещает смешивать оба подхода: если `@Testcontainers` обнаружит `@Container`-поле в базовом классе с ручным singleton, контейнер будет остановлен после первого тестового класса, а следующие классы попытаются использовать уже остановленный контейнер.

---

### Вопрос 47. Что такое @SpringBootTest(webEnvironment = RANDOM_PORT)? Чем TestRestTemplate отличается от WebTestClient при тестировании на реальном порту и когда предпочтительнее каждый из них?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Testing Spring Boot Applications — Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)

`@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)` запускает встроенный сервер (Tomcat/Jetty/Undertow) на случайном свободном порту. Это позволяет проводить полноценные HTTP-интеграционные тесты без конфликтов портов при параллельном запуске.

**TestRestTemplate** подключается через `@AutoConfigureTestRestTemplate`:

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureTestRestTemplate
class MyTests {
    @Test
    void exampleTest(@Autowired TestRestTemplate restTemplate) {
        String body = restTemplate.getForObject("/", String.class);
        assertThat(body).isEqualTo("Hello World");
    }
}
```

**WebTestClient** подключается через `@AutoConfigureWebTestClient` (требует `spring-webflux` в classpath):

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
class MyTests {
    @Test
    void exampleTest(@Autowired WebTestClient webClient) {
        webClient.get().uri("/")
            .exchange()
            .expectStatus().isOk()
            .expectBody(String.class).isEqualTo("Hello World");
    }
}
```

Важное замечание из документации: при использовании реального порта HTTP-клиент и сервер работают в разных потоках и разных транзакциях, поэтому `@Transactional` не откатывает изменения на стороне сервера.

#### Ответ от Claude

**Что такое @SpringBootTest(webEnvironment = RANDOM_PORT)**

`@SpringBootTest` загружает полный контекст Spring-приложения. Параметр `webEnvironment` определяет, как именно поднимается веб-слой:

| Значение | Описание |
|----------|----------|
| `MOCK` (default) | MockMvc-окружение, реальный сервер не запускается |
| `RANDOM_PORT` | Реальный сервер на случайном порту |
| `DEFINED_PORT` | Реальный сервер на порту из `server.port` |
| `NONE` | Без веб-окружения |

`RANDOM_PORT` гарантирует отсутствие конфликтов при параллельных сборках (CI) и максимально приближает тест к продакшн-поведению: работает весь стек (фильтры, interceptors, сериализация).

**TestRestTemplate**

- Обёртка над `RestTemplate`, адаптированная для тестов.
- Не выбрасывает исключения на 4xx/5xx — возвращает `ResponseEntity` с соответствующим статусом, что упрощает утверждения.
- Блокирующий (синхронный) API — подходит только для сервлетных приложений.
- Требует `spring-boot-test` (включён в `spring-boot-starter-test`).
- API менее выразительный: необходимо вручную конструировать `HttpHeaders`, `HttpEntity`, передавать их в `exchange()`.

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureTestRestTemplate
class OrderApiTest {

    @Test
    void getOrder(@Autowired TestRestTemplate restTemplate) {
        ResponseEntity<OrderDto> response =
            restTemplate.getForEntity("/orders/1", OrderDto.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().getId()).isEqualTo(1L);
    }
}
```

**WebTestClient**

- Построен на WebFlux `WebClient`, поддерживает как реактивные, так и обычные сервлетные приложения.
- Fluent-API: запрос, выполнение и утверждения — одна цепочка.
- Требует `spring-webflux` в classpath (даже для тестирования обычного MVC-приложения).
- Работает как с реальным сервером (`RANDOM_PORT`), так и с mock-окружением (`bindTo*`-методы).

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
class OrderApiTest {

    @Test
    void getOrder(@Autowired WebTestClient webClient) {
        webClient.get().uri("/orders/1")
            .exchange()
            .expectStatus().isOk()
            .expectBody(OrderDto.class)
            .value(dto -> assertThat(dto.getId()).isEqualTo(1L));
    }
}
```

**Сравнение**

| Критерий | TestRestTemplate | WebTestClient |
|----------|-----------------|---------------|
| API-стиль | Императивный, RestTemplate-подобный | Fluent, цепочки |
| Реактивность | Нет | Да (Flux/Mono) |
| Доп. зависимость | Нет | `spring-webflux` |
| Mock-окружение | Не поддерживает | Поддерживает (`MockMvcWebTestClient`) |
| Утверждения | Отдельно через AssertJ | Встроены в цепочку |
| Рекомендуется для | Legacy-код или простые случаи, команды, привыкшие к RestTemplate | Новые проекты, реактивный стек, необходим fluent API |

**Когда что предпочесть**

- `TestRestTemplate` — если команда хорошо знает `RestTemplate` и проект не использует WebFlux; самодостаточен без дополнительных зависимостей.
- `WebTestClient` — рекомендуемый выбор для новых проектов; покрывает и MVC, и WebFlux; более выразительный API упрощает сопровождение тестов.

Важный нюанс: при `RANDOM_PORT` тесты выполняются в отдельном потоке от сервера, транзакции не откатываются автоматически — необходима очистка БД иными средствами (например, `@Sql`, Testcontainers reset или `@DirtiesContext`).

---

### Вопрос 48. Что такое @MockitoSettings и как с его помощью управлять уровнем строгости (Strictness) Mockito на уровне класса? Чем STRICT_STUBS отличается от WARN и LENIENT, и как пометить отдельный stub как lenient через lenient().when()?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Setting the strictness of Mockito mock(s) — davidvlijmincx.com](https://davidvlijmincx.com/posts/setting_the_strictness_for_mockito_mocks/)

Аннотация `@MockitoSettings` задаёт уровень строгости для всех моков в тестовом классе при использовании JUnit 5:

```java
@MockitoSettings(strictness = Strictness.LENIENT)
public class MyTestClass {
    // все моки в классе работают с LENIENT-строгостью
}
```

Три уровня строгости:

- **LENIENT** — поведение Mockito 1.x: неиспользуемые стабы разрешены, проверок нет.
- **WARN** — поведение Mockito 2.x/3.x по умолчанию: неиспользуемые стабы фиксируются предупреждениями в консоли, тест не падает.
- **STRICT_STUBS** — наивысший уровень: при обнаружении неиспользуемого стаба выбрасывается `UnnecessaryStubbingException`, тест завершается с ошибкой.

Для отдельного стаба можно задать lenient-уровень, не снижая строгость всего класса:

```java
lenient().when(blueCar.drive(10)).thenReturn("Driving at 10 kmh");
```

#### Ответ от Claude

**Что такое @MockitoSettings**

`@MockitoSettings` — аннотация из `mockito-junit-jupiter`, применяемая к тестовому классу совместно с `@ExtendWith(MockitoExtension.class)`. Она конфигурирует уровень строгости (`Strictness`) для всей `MockitoSession`, которую расширение открывает перед тестом и закрывает после.

```java
@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.WARN)
class PaymentServiceTest {

    @Mock
    PaymentGateway gateway;

    @InjectMocks
    PaymentService service;

    @Test
    void shouldProcessPayment() {
        when(gateway.charge(100)).thenReturn(true);
        assertThat(service.process(100)).isTrue();
    }
}
```

Без `@MockitoSettings` `MockitoExtension` по умолчанию использует `STRICT_STUBS`.

**Три уровня строгости**

| Уровень | Поведение при неиспользуемом стабе | Поведение при аргументе, не совпавшем со стабом | Исторический дефолт |
|---------|-----------------------------------|------------------------------------------------|---------------------|
| `LENIENT` | Игнорируется | Возвращается `null` / 0 / `false` | Mockito 1.x |
| `WARN` | Предупреждение в консоли | Возвращается `null` / 0 / `false` | Mockito 2.x / 3.x |
| `STRICT_STUBS` | `UnnecessaryStubbingException` (тест падает) | `PotentialStubbingProblem` (тест падает) | Mockito 4+ (планируемый дефолт) |

`STRICT_STUBS` дополнительно детектирует ситуацию, когда стаб был объявлен с одним аргументом, а метод вызван с другим — это сигнализирует о потенциальной ошибке в тесте (`PotentialStubbingProblem`).

**Когда использовать каждый уровень**

- `STRICT_STUBS` — рекомендуется для всех новых тестов: выявляет мёртвый код стабов, опечатки в аргументах, дублирование.
- `WARN` — переходный вариант при миграции legacy-тестов, когда сразу исправить все неиспользуемые стабы невозможно.
- `LENIENT` — крайний случай: тесты с общими фикстурами (`@BeforeEach`), где часть стабов намеренно не вызывается в каждом тесте.

**Отдельный стаб как lenient через lenient().when()**

Когда уровень класса `STRICT_STUBS`, но конкретный стаб заведомо нужен не во всех тестах, его помечают явно:

```java
@ExtendWith(MockitoExtension.class) // STRICT_STUBS по умолчанию
class InventoryServiceTest {

    @Mock
    WarehouseClient warehouse;

    @InjectMocks
    InventoryService service;

    @BeforeEach
    void setUp() {
        // этот стаб нужен только части тестов — помечаем lenient,
        // чтобы остальные тесты не падали с UnnecessaryStubbingException
        lenient().when(warehouse.getStock("ITEM-42")).thenReturn(100);
    }

    @Test
    void shouldReduceStock() {
        // здесь стаб warehouse.getStock используется
        service.reduceStock("ITEM-42", 5);
        verify(warehouse).updateStock("ITEM-42", 95);
    }

    @Test
    void shouldRejectNegativeQuantity() {
        // здесь стаб warehouse.getStock НЕ используется,
        // но тест не падает из-за lenient()
        assertThatThrownBy(() -> service.reduceStock("ITEM-42", -1))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

Альтернатива на уровне отдельного мока — `MockSettings.lenient()`:

```java
WarehouseClient warehouse = mock(WarehouseClient.class,
    withSettings().lenient());
```

**Итоговая рекомендация**

Держите `STRICT_STUBS` как дефолт на уровне класса (это и является дефолтом `MockitoExtension`). Применяйте `lenient().when()` точечно там, где стаб не должен быть обязательно вызван в каждом тесте. Переходите к `@MockitoSettings(strictness = LENIENT)` только если вся тестовая фикстура унаследована из базового класса и рефакторинг нецелесообразен.

---
### Вопрос 49. Как в Mockito 3.4+ замокировать вызов конструктора с помощью Mockito.mockConstruction()? Каков корректный способ использования MockedConstruction (try-with-resources), и как получить список всех созданных экземпляров через constructed()?

**Категория:** Тестирование · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Mock Java Constructors and Their Object Creation with Mockito (rieckpil.de)](https://rieckpil.de/mock-java-constructors-and-their-object-creation-with-mockito/)

Начиная с Mockito 3.4, появился метод `Mockito.mockConstruction()`, позволяющий перехватывать вызовы конструктора и возвращать моки вместо реальных объектов. Метод принимает класс, конструкторы которого нужно замокировать, в качестве обязательного первого аргумента.

Возвращаемый тип — `MockedConstruction<T>`, который реализует `AutoCloseable`. Это означает, что его следует использовать в блоке try-with-resources: внутри блока все вызовы конструктора возвращают моки, снаружи — реальные экземпляры.

Базовый пример:

```java
try (MockedConstruction<PaymentProcessor> mocked =
         Mockito.mockConstruction(PaymentProcessor.class)) {
    PaymentProcessor processor = new PaymentProcessor();
    // processor — это мок, а не реальный объект
} // за пределами блока конструктор работает штатно
```

Вариант с `MockInitializer` — callback-функцией для настройки поведения каждого создаваемого мока:

```java
try (MockedConstruction<PaymentProcessor> mocked =
         Mockito.mockConstruction(PaymentProcessor.class,
             (mock, context) -> {
                 when(mock.chargeCustomer(anyString(), any(BigDecimal.class)))
                     .thenReturn(BigDecimal.TEN);
             })) {
    PaymentProcessor processor = new PaymentProcessor();
    BigDecimal result = processor.chargeCustomer("customer-id", new BigDecimal("100"));
    assertEquals(BigDecimal.TEN, result);
}
```

Callback `MockInitializer` принимает два параметра: сам мок и контекст (`MockedConstruction.Context`), из которого можно получить аргументы конструктора (`context.arguments()`).

Метод `constructed()` возвращает `List<T>` всех моков, созданных в рамках текущего блока. Это позволяет проверить количество вызовов конструктора и взаимодействовать с конкретными экземплярами:

```java
try (MockedConstruction<PaymentProcessor> mocked =
         Mockito.mockConstruction(PaymentProcessor.class)) {
    PaymentProcessor first = new PaymentProcessor();
    PaymentProcessor second = new PaymentProcessor();

    assertEquals(2, mocked.constructed().size());
    assertSame(first, mocked.constructed().get(0));
    assertSame(second, mocked.constructed().get(1));
}
```

Также существует метод `mockConstructionWithAnswer()`, задающий дефолтный ответ для всех вызовов методов на созданных моках.

Для работы функции необходим **inline mock maker**: либо зависимость `mockito-inline` (до Mockito 5.x), либо файл `src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker` со значением `mock-maker-inline`.

#### Ответ от Claude

**Предпосылки появления и требования к окружению**

До Mockito 3.4 мокировать вызовы конструктора можно было только через PowerMock — тяжеловесную библиотеку, несовместимую с новыми JVM и требующую специальных раннеров. В Mockito 3.4 (июнь 2020) был добавлен метод `mockConstruction()`, реализующий аналогичную функцию средствами самого Mockito.

Для работы обязательно нужен **inline mock maker**. Способы включения:
- Maven: зависимость `mockito-inline` (отдельный артефакт до Mockito 5.x) вместо `mockito-core`, или `mockito-core` + файл-конфигурация.
- Mockito 5.x: inline mock maker активирован по умолчанию, отдельная зависимость не нужна.
- Файл-конфигурация: `src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker` → содержимое `mock-maker-inline`.

**Сигнатуры метода mockConstruction()**

```java
// Базовая: все методы мока возвращают дефолтные значения
public static <T> MockedConstruction<T> mockConstruction(Class<T> classToMock)

// С инициализатором: настройка поведения при каждом вызове конструктора
public static <T> MockedConstruction<T> mockConstruction(
    Class<T> classToMock,
    MockedConstruction.MockInitializer<T> mockInitializer)

// С конфигурацией мока (MockSettings) и инициализатором
public static <T> MockedConstruction<T> mockConstruction(
    Class<T> classToMock,
    MockedConstruction.MockitoMockSettings mockSettings,
    MockedConstruction.MockInitializer<T> mockInitializer)
```

**Корректное использование — try-with-resources**

`MockedConstruction<T>` реализует `AutoCloseable`. Блок try-with-resources гарантирует, что мокирование конструктора отключается ровно по выходу из блока — даже при исключении. Это критично: незакрытый `MockedConstruction` будет перехватывать конструкторы во всём потоке до явного вызова `close()`, что приведёт к непредсказуемым результатам в параллельных тестах.

```java
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.when;

@Test
void shouldMockConstructor() {
    try (MockedConstruction<Service> mocked = mockConstruction(Service.class,
            (mock, context) -> {
                // context.arguments() — список аргументов, переданных конструктору
                when(mock.process()).thenReturn("mocked-result");
            })) {

        // Внутри блока new Service() возвращает мок
        Service service = new Service();
        assertEquals("mocked-result", service.process());

        // Все созданные экземпляры доступны через constructed()
        assertEquals(1, mocked.constructed().size());
        assertSame(service, mocked.constructed().get(0));
    }
    // За пределами блока new Service() создаёт реальный объект
}
```

**Метод constructed()**

`MockedConstruction.constructed()` возвращает `java.util.List<T>` — список всех моков, созданных внутри текущего блока try-with-resources, в порядке их создания. Список накапливается по мере создания объектов.

Сценарии применения:
1. Проверка числа вызовов конструктора (`assertEquals(N, mocked.constructed().size())`).
2. Получение конкретного мока для верификации взаимодействий (`verify(mocked.constructed().get(0)).someMethod()`).
3. Настройка поведения отдельных экземпляров после создания.

**Работа с MockInitializer и контекстом**

```java
try (MockedConstruction<Connection> mocked = mockConstruction(Connection.class,
        (mock, context) -> {
            // Количество аргументов конструктора
            int argCount = context.arguments().size();
            // Первый аргумент (например, строка URL)
            String url = (String) context.arguments().get(0);

            when(mock.isValid()).thenReturn(true);
            when(mock.getUrl()).thenReturn(url + "/mocked");
        })) {

    Connection conn = new Connection("jdbc:postgresql://localhost/db");
    assertTrue(conn.isValid());
    assertEquals("jdbc:postgresql://localhost/db/mocked", conn.getUrl());
}
```

**Множественное мокирование конструкторов**

Несколько классов можно мокировать одновременно, вложив или объединив блоки:

```java
try (MockedConstruction<Actor> actorMock = mockConstruction(Actor.class);
     MockedConstruction<Sensor> sensorMock = mockConstruction(Sensor.class)) {

    Actor actor = new Actor();
    Sensor sensor = new Sensor();

    assertSame(actor, actorMock.constructed().get(0));
    assertSame(sensor, sensorMock.constructed().get(0));
}
```

**Ограничения**

- Работает только в пределах текущего потока (thread-local scoping).
- Нельзя мокировать конструкторы абстрактных классов и интерфейсов (используйте `mockito-subclass` или обычный `mock()`).
- Неприменимо к конструкторам классов, созданных вне JVM (нативный код).
- Не следует использовать вместо рефакторинга: если класс сложно тестировать без мокирования конструктора, лучше ввести зависимость через DI.

---

### Вопрос 50. Как в Spring Boot 3.1+ упростилась интеграция Testcontainers через аннотацию @ServiceConnection? Чем этот подход лучше, чем @DynamicPropertySource, и какие контейнеры поддерживаются «из коробки»?

**Категория:** Тестирование · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Improved Testcontainers Support in Spring Boot 3.1 (spring.io blog)](https://spring.io/blog/2023/06/23/improved-testcontainers-support-in-spring-boot-3-1/)

В Spring Boot 3.1 (май 2023) появилась аннотация `@ServiceConnection`, которая кардинально упрощает настройку Testcontainers в интеграционных тестах.

**Старый подход — @DynamicPropertySource:**

```java
@SpringBootTest
@Testcontainers
class MyIntegrationTests {
    @Container
    static Neo4jContainer<?> neo4j = new Neo4jContainer<>("neo4j:5");

    @DynamicPropertySource
    static void neo4jProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.neo4j.uri", neo4j::getBoltUrl);
    }
}
```

Разработчик должен знать точные имена свойств (`spring.neo4j.uri`) и явно регистрировать их.

**Новый подход — @ServiceConnection:**

```java
@SpringBootTest
@Testcontainers
class MyIntegrationTests {
    @Container
    @ServiceConnection
    static Neo4jContainer<?> neo4j = new Neo4jContainer<>("neo4j:5");
}
```

Spring Boot автоматически определяет тип контейнера, создаёт соответствующий bean `ConnectionDetails` и конфигурирует автоконфигурацию для подключения к сервису внутри контейнера. Никаких строковых имён свойств, никаких статических методов.

Под капотом `@ServiceConnection` регистрирует bean `ConnectionDetails`, который используется автоконфигурацией Spring Boot вместо обычных свойств из `application.properties`.

Для `GenericContainer` (когда Spring Boot не может определить тип по классу) нужно явно указать имя сервиса через атрибут `name`:

```java
@Bean
@ServiceConnection(name = "redis")
GenericContainer<?> redisContainer() {
    return new GenericContainer<>("redis:7");
}
```

**Запуск контейнеров на этапе разработки** (без тестов) — ещё одна новинка 3.1:

```java
// src/test/java/.../TestMyApplication.java
public class TestMyApplication {
    public static void main(String[] args) {
        SpringApplication.from(MyApplication::main)
            .with(MyContainersConfiguration.class)
            .run(args);
    }
}
```

```java
@TestConfiguration(proxyBeanMethods = false)
class MyContainersConfiguration {
    @Bean
    @ServiceConnection
    Neo4jContainer<?> neo4jContainer() {
        return new Neo4jContainer<>("neo4j:5");
    }
}
```

Запуск: `./gradlew bootTestRun` или `./mvnw spring-boot:test-run`.

#### Ответ от Claude

**Контекст: зачем понадобилось упрощение**

До Spring Boot 3.1 разработчик при использовании Testcontainers был обязан вручную регистрировать свойства подключения. Это порождало несколько проблем:
- Нужно знать точные имена Spring-свойств для каждого сервиса (`spring.datasource.url`, `spring.data.mongodb.uri` и т.д.).
- Метод с `@DynamicPropertySource` обязан быть `static`, что ограничивает гибкость.
- При смене версии контейнера или структуры свойств тесты ломаются.
- Дублирование одного и того же бойлерплейта в каждом тест-классе.

**Механизм работы @ServiceConnection**

Аннотация `@ServiceConnection` (пакет `org.springframework.boot.testcontainers.service.connection`) вместе с модулем `spring-boot-testcontainers` реализует следующий механизм:

1. Spring Boot определяет тип контейнера (по классу, например `PostgreSQLContainer`, или по имени Docker-образа).
2. Для найденного типа регистрируется bean `ConnectionDetails` (например, `JdbcConnectionDetails`, `MongoConnectionDetails`).
3. Автоконфигурация Spring Boot использует `ConnectionDetails` приоритетно перед свойствами из `application.properties`.

Таким образом, `@ServiceConnection` работает на уровне **ConnectionDetails API**, а не на уровне `Environment`/`PropertySources`, как `@DynamicPropertySource`.

**Сравнение подходов**

| Критерий | @ServiceConnection | @DynamicPropertySource |
|---|---|---|
| Объём кода | Только аннотация на поле | Аннотация + отдельный static-метод |
| Знание имён свойств | Не требуется | Обязательно |
| Ограничение static | Нет | Метод должен быть static |
| Механизм | ConnectionDetails bean | Environment PropertySources |
| Поддержка нестандартных сервисов | Через атрибут name или кастомный ConnectionDetailsFactory | Полная гибкость |
| Рекомендуется для | Стандартных сервисов из списка ниже | Нестандартных случаев, не поддерживаемых @ServiceConnection |

**Зависимость**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
```

Дополнительно нужна зависимость Testcontainers для конкретного сервиса (например, `org.testcontainers:postgresql`).

**Поддерживаемые контейнеры «из коробки»** (актуально для Spring Boot 3.x)

| Тип ConnectionDetails | Контейнер / Docker-образ |
|---|---|
| `ActiveMQConnectionDetails` | `ActiveMQContainer`, образ `symptoma/activemq` |
| `ArtemisConnectionDetails` | `ArtemisContainer` |
| `CassandraConnectionDetails` | `CassandraContainer` |
| `CouchbaseConnectionDetails` | `CouchbaseContainer` |
| `ElasticsearchConnectionDetails` | `ElasticsearchContainer` |
| `FlywayConnectionDetails` | `JdbcDatabaseContainer` |
| `JdbcConnectionDetails` | `JdbcDatabaseContainer` (PostgreSQL, MySQL, MariaDB, Oracle, MSSQL, H2 и др.) |
| `KafkaConnectionDetails` | `KafkaContainer`, `ConfluentKafkaContainer`, `RedpandaContainer` |
| `LdapConnectionDetails` | образ `osixia/openldap`, `LLdapContainer` |
| `LiquibaseConnectionDetails` | `JdbcDatabaseContainer` |
| `MongoConnectionDetails` | `MongoDBContainer`, `MongoDBAtlasLocalContainer` |
| `Neo4jConnectionDetails` | `Neo4jContainer` |
| `OtlpTracingConnectionDetails` | образ `otel/opentelemetry-collector-contrib`, `LgtmStackContainer` |
| `PulsarConnectionDetails` | `PulsarContainer` |
| `R2dbcConnectionDetails` | `PostgreSQLContainer`, `MySQLContainer`, `MariaDBContainer`, `MSSQLServerContainer`, `OracleContainer`, `ClickHouseContainer` |
| `RabbitConnectionDetails` | `RabbitMQContainer` |
| `DataRedisConnectionDetails` | `RedisContainer`, `RedisStackContainer`, образы `redis`, `redis/redis-stack` |
| `ZipkinConnectionDetails` | образ `openzipkin/zipkin` |

**Примеры использования**

Стандартный тест с PostgreSQL:

```java
@SpringBootTest
@Testcontainers
class OrderRepositoryIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    OrderRepository orderRepository;

    @Test
    void shouldSaveAndRetrieveOrder() {
        // Spring Boot автоматически настраивает DataSource на порт контейнера
        Order saved = orderRepository.save(new Order("item-1", 3));
        assertThat(orderRepository.findById(saved.getId())).isPresent();
    }
}
```

Kafka в тесте:

```java
@SpringBootTest
@Testcontainers
class KafkaConsumerIntegrationTest {

    @Container
    @ServiceConnection
    static KafkaContainer kafka =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.6.0"));

    // spring.kafka.bootstrap-servers настроен автоматически
}
```

Redis через GenericContainer (нестандартный случай, нужно name):

```java
@TestConfiguration(proxyBeanMethods = false)
class TestRedisConfig {

    @Bean
    @ServiceConnection(name = "redis")
    GenericContainer<?> redisContainer() {
        return new GenericContainer<>("redis:7-alpine").withExposedPorts(6379);
    }
}
```

**Расширение: кастомный ConnectionDetailsFactory**

Для собственных или неподдерживаемых сервисов можно реализовать интерфейс `ConnectionDetailsFactory<C extends Container<?>, D extends ConnectionDetails>` и зарегистрировать его через `META-INF/spring.factories`. Spring Boot обнаружит его и применит при наличии `@ServiceConnection` на соответствующем контейнере.

**Когда @DynamicPropertySource по-прежнему нужен**

- Сервис не входит в список поддерживаемых и нет смысла писать кастомный `ConnectionDetailsFactory`.
- Нужно зарегистрировать несколько несвязанных свойств из одного контейнера нестандартным образом.
- Проект использует Spring Boot версии ниже 3.1 и миграция невозможна.

---

### Вопрос 51. Как в JUnit 5 пометить тесты тегами с помощью @Tag и затем отфильтровать их при сборке? Какие правила синтаксиса для имён тегов и как настроить includeTags / excludedGroups в Maven и Gradle?

**Категория:** Тестирование · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Tagging and Filtering JUnit Tests | Baeldung](https://www.baeldung.com/junit-filtering-tests)

Аннотация `@Tag` позволяет помечать тестовые классы и методы произвольными метками и затем выборочно запускать или пропускать их при сборке.

Пример разметки:

```java
@Tag("IntegrationTest")
@SpringBootTest
class OrderServiceIntegrationTest {

    @Test
    @Tag("slow")
    void shouldPersistOrderToDatabase() { ... }
}
```

**Правила синтаксиса тега:**
- Не должен быть пустым или состоять только из пробелов.
- Не должен содержать управляющих символов ISO.
- Не должен содержать зарезервированных символов: `,`, `(`, `)`, `&`, `|`, `!`.

**Фильтрация в Maven (maven-surefire-plugin):**

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <groups>UnitTest</groups>
        <excludedGroups>IntegrationTest</excludedGroups>
    </configuration>
</plugin>
```

Или через командную строку: `mvn test -Dgroups=UnitTest -DexcludeGroups=IntegrationTest`.

**Фильтрация в Gradle:**

```groovy
test {
    useJUnitPlatform {
        includeTags 'UnitTest'
        excludeTags 'IntegrationTest', 'slow'
    }
}
```

**Составные выражения** поддерживают операторы: `!` (отрицание), `|` (ИЛИ), `&` (И). Например, `UnitTest | IntegrationTest` запустит оба тега; `!slow` — всё кроме медленных тестов.

#### Ответ от Claude

**Что такое @Tag**

`@Tag` — повторяемая аннотация (`@Repeatable`) из `org.junit.jupiter.api`, применяемая на уровне класса и метода. Используется для классификации тестов и последующей фильтрации при сборке или в IDE.

```java
@Tag("fast")
@Tag("unit")
class UserValidatorTest {

    @Test
    @Tag("regression")
    void shouldRejectEmptyEmail() { ... }

    @Test
    void shouldAcceptValidEmail() { ... }
}
```

**Правила синтаксиса (из официальной документации JUnit 5)**

Тег считается синтаксически некорректным, если он:
- пустой или состоит только из пробельных символов;
- содержит ISO-управляющие символы (коды 0–31, 127);
- содержит зарезервированные символы: `,` `(` `)` `&` `|` `!`.

Некорректный тег логируется как предупреждение и игнорируется — тест не падает.

**Составные теговые выражения**

JUnit Platform поддерживает логические выражения при фильтрации:

| Выражение | Смысл |
|-----------|-------|
| `fast` | только тег `fast` |
| `!slow` | всё, кроме `slow` |
| `unit \| integration` | любой из двух тегов |
| `fast & unit` | оба тега одновременно |
| `fast & !integration` | fast, но не integration |

**Конфигурация Maven (maven-surefire-plugin 3.x)**

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.5</version>
    <configuration>
        <!-- включить только unit-тесты -->
        <groups>unit</groups>
        <!-- исключить нестабильные -->
        <excludedGroups>flaky</excludedGroups>
    </configuration>
</plugin>
```

Переопределение из CLI: `mvn verify -Dgroups="unit|fast" -DexcludeGroups=slow`.

**Конфигурация Gradle (8.x)**

```groovy
tasks.named('test', Test) {
    useJUnitPlatform {
        includeTags('unit', 'fast')   // OR-логика: любой из тегов
        excludeTags('slow', 'flaky')
    }
}
```

**Рекомендации по именованию**

Устоявшиеся соглашения: `unit`, `integration`, `e2e`, `slow`, `fast`, `smoke`, `regression`. Используйте kebab-case для составных тегов (`data-access`, `api-layer`) — нижний регистр предотвращает проблемы с регистрозависимыми ОС при передаче в CLI.

---

### Вопрос 52. Как управлять порядком выполнения тестов в JUnit 5 с помощью @TestMethodOrder и @Order? Какие реализации MethodOrderer существуют и в каких сценариях порядок тестов оправдан?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Test Execution Order :: JUnit User Guide (docs.junit.org)](https://docs.junit.org/5.14.1/writing-tests/test-execution-order.html)

По умолчанию JUnit 5 упорядочивает тестовые методы с помощью детерминированного, но намеренно непрозрачного алгоритма. Это обеспечивает воспроизводимость прогонов и не допускает зависимостей между тестами.

Для явного управления порядком применяется аннотация `@TestMethodOrder` с одной из встроенных реализаций `MethodOrderer`:

- **`OrderAnnotation`** — сортирует тесты в порядке возрастания числовых значений `@Order(n)`.
- **`DisplayName`** — алфавитная сортировка по отображаемому имени.
- **`MethodName`** — алфавитная сортировка по имени метода и списку параметров.
- **`Random`** — псевдослучайный порядок; поддерживает настройку seed через конфигурационный параметр.
- **`Alphanumeric`** — устаревший вариант, будет удалён в JUnit 6.0; замена — `MethodName`.

Пример использования `OrderAnnotation`:

```java
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class OrderedTests {
    @Test @Order(1) void firstTest() { ... }
    @Test @Order(2) void secondTest() { ... }
    @Test @Order(3) void thirdTest() { ... }
}
```

#### Ответ от Claude

**Концепция и предостережение**

JUnit 5 намеренно не гарантирует порядок тестов без явной аннотации, чтобы предотвратить тесты с общим изменяемым состоянием. Тем не менее некоторые сценарии оправдывают явный порядок:
- интеграционные тесты с сохранением состояния (CRUD-цикл: create → read → update → delete);
- сценарии, где поднятие контейнера Testcontainers дорого, и тесты выполняются последовательно над общим состоянием;
- тесты для демонстрации поведения системы «по шагам».

**@TestMethodOrder + реализации MethodOrderer**

```java
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@Testcontainers
class UserCrudIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    static Long createdId;

    @Test @Order(1)
    void shouldCreateUser() {
        createdId = userService.create(new User("Alice"));
        assertThat(createdId).isPositive();
    }

    @Test @Order(2)
    void shouldReadCreatedUser() {
        assertThat(userService.findById(createdId)).isPresent();
    }

    @Test @Order(3)
    void shouldDeleteUser() {
        userService.delete(createdId);
        assertThat(userService.findById(createdId)).isEmpty();
    }
}
```

**Все встроенные реализации MethodOrderer**

| Реализация | Критерий сортировки | Примечание |
|---|---|---|
| `OrderAnnotation` | `@Order(n)`, числа по возрастанию | Тесты без `@Order` выполняются последними |
| `DisplayName` | Алфавитно по `@DisplayName` или имени метода | |
| `MethodName` | Алфавитно по имени + список параметров | Рекомендуется вместо `Alphanumeric` |
| `Random` | Псевдослучайно | Seed: `junit.jupiter.testmethod.order.random.seed` |
| `Alphanumeric` | Алфавитно | **Deprecated** с JUnit 5.7, удаляется в 6.0 |

**Глобальная конфигурация**

Чтобы не повторять аннотацию в каждом классе, можно задать дефолтный упорядочиватель через конфигурационный параметр:

```properties
# src/test/resources/junit-platform.properties
junit.jupiter.testmethod.order.default=org.junit.jupiter.api.MethodOrderer$Random
```

**Когда порядок НЕ нужен**

В большинстве случаев явный порядок — признак плохой изоляции тестов. Предпочтительнее:
- делать каждый тест независимым (с собственной фикстурой через `@BeforeEach`);
- сбрасывать состояние через `@Sql`, `@Transactional` или Testcontainers.

---

### Вопрос 53. Что такое @Nested в JUnit 5? Как вложенные классы наследуют жизненный цикл внешнего класса, и в чём ограничения @BeforeAll внутри @Nested?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Nested Tests :: JUnit User Guide (docs.junit.org)](https://docs.junit.org/6.0.2/writing-tests/nested-tests.html)

`@Nested` сигнализирует, что аннотированный класс является вложенным нестатическим тестовым классом (inner class), который может использовать установку и состояние экземпляра внешнего класса. Такие тесты позволяют выразить иерархические отношения между группами тестов и обеспечивают «иерархическое мышление» о структуре тестов.

Ключевые свойства:
- Только **нестатические** вложенные классы могут быть `@Nested`-тестовыми классами.
- Методы жизненного цикла (`@BeforeEach`) внешнего класса выполняются **перед** методами жизненного цикла вложенного.
- `@Nested`-класс может иметь собственный `TestInstance.Lifecycle`, отличный от внешнего, но не может изменить `Lifecycle` внешнего.
- Вложенность может быть произвольно глубокой.

#### Ответ от Claude

**Зачем нужен @Nested**

`@Nested` позволяет структурировать тесты иерархически, отражая предметную логику. Вместо одного плоского списка из двадцати тестов можно создать дерево: внешний класс — тестируемый компонент, вложенные классы — отдельные сценарии или состояния.

```java
class BankAccountTest {

    BankAccount account;

    @BeforeEach
    void createAccount() {
        account = new BankAccount(1000);  // начальный баланс 1000
    }

    @Nested
    @DisplayName("Когда баланс положительный")
    class WhenBalanceIsPositive {

        @Test
        void shouldAllowWithdrawal() {
            account.withdraw(500);
            assertThat(account.getBalance()).isEqualTo(500);
        }

        @Nested
        @DisplayName("И сумма превышает баланс")
        class WhenAmountExceedsBalance {

            @Test
            void shouldThrowInsufficientFundsException() {
                assertThatThrownBy(() -> account.withdraw(2000))
                    .isInstanceOf(InsufficientFundsException.class);
            }
        }
    }

    @Nested
    @DisplayName("Когда счёт заморожен")
    class WhenAccountIsFrozen {

        @BeforeEach
        void freezeAccount() {
            account.freeze();
        }

        @Test
        void shouldRejectWithdrawal() {
            assertThatThrownBy(() -> account.withdraw(100))
                .isInstanceOf(AccountFrozenException.class);
        }
    }
}
```

**Порядок выполнения методов жизненного цикла**

При вызове теста `WhenAccountIsFrozen.shouldRejectWithdrawal()` JUnit выполняет:

1. `BankAccountTest@BeforeEach` → `createAccount()` (внешний)
2. `WhenAccountIsFrozen@BeforeEach` → `freezeAccount()` (внутренний)
3. Тест
4. `WhenAccountIsFrozen@AfterEach` (если есть)
5. `BankAccountTest@AfterEach` (если есть)

**Ограничение @BeforeAll в @Nested**

По умолчанию (`TestInstance.Lifecycle.PER_METHOD`) `@BeforeAll`-метод в `@Nested`-классе **не разрешён** — потому что для статического метода нет экземпляра внешнего класса. Решения:
- Аннотировать `@Nested`-класс `@TestInstance(Lifecycle.PER_CLASS)` — тогда `@BeforeAll` может быть нестатическим.
- Перенести дорогостоящую инициализацию во внешний класс (`@BeforeAll static`).

```java
@Nested
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class WhenDatabaseIsPreloaded {

    @BeforeAll   // нестатический — разрешён при PER_CLASS
    void loadFixtures() {
        // однократная загрузка тестовых данных
    }

    @Test
    void shouldFindUsers() { ... }
}
```

**Практические рекомендации**

- Используйте `@Nested` для группировки тестов одного компонента по сценариям (Given/When/Then).
- Не дублируйте `@BeforeEach`-логику: вынесите общую инициализацию во внешний класс.
- Избегайте вложенности глубже двух уровней — читаемость страдает.

---

### Вопрос 54. Как JUnit 5 assertThrows() позволяет проверить тип и сообщение выброшенного исключения? Чем этот подход лучше, чем @Test(expected = …​) из JUnit 4, и когда использовать assertDoesNotThrow()?

**Категория:** Тестирование · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Assertions (JUnit 5.9.3 API) — docs.junit.org](https://docs.junit.org/5.9.3/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html)

`assertThrows(Class<T> expectedType, Executable executable)` — статический метод класса `Assertions`, который:
- выполняет `executable`;
- убеждается, что выброшено исключение типа `expectedType` (или его подтипа);
- **возвращает** пойманный экземпляр исключения, чтобы можно было сделать дополнительные проверки.

Если исключение не выброшено или выброшено исключение другого типа — тест падает.

```java
Exception exception = assertThrows(ArithmeticException.class,
    () -> calculator.divide(1, 0));
assertEquals("/ by zero", exception.getMessage());
```

`assertDoesNotThrow(Executable executable)` — утверждает, что выполнение блока не выбрасывает никакого исключения. Полезен, когда нужно явно задокументировать отсутствие исключения внутри более широкого теста.

#### Ответ от Claude

**assertThrows() — возврат исключения для дальнейших проверок**

Ключевое преимущество `assertThrows()` перед JUnit 4 `@Test(expected=...)` — метод **возвращает объект исключения**, что позволяет проверить не только тип, но и сообщение, причину и любые поля кастомного исключения.

```java
@Test
void shouldThrowOnNegativeAmount() {
    // arrange
    Account account = new Account(100);

    // act + assert: тип
    IllegalArgumentException ex = assertThrows(
        IllegalArgumentException.class,
        () -> account.withdraw(-50)
    );

    // проверка деталей исключения
    assertThat(ex.getMessage()).contains("negative");
}
```

**Проверка цепочки причин (cause)**

```java
@Test
void shouldWrapOriginalException() {
    ServiceException ex = assertThrows(
        ServiceException.class,
        () -> service.call()
    );

    // проверяем обёрнутое исключение
    assertThat(ex.getCause()).isInstanceOf(IOException.class);
    assertThat(ex.getCause().getMessage()).contains("Connection refused");
}
```

**Сравнение с @Test(expected = …) из JUnit 4**

| Критерий | JUnit 4 `@Test(expected=...)` | JUnit 5 `assertThrows()` |
|---|---|---|
| Что проверяет | Только тип исключения | Тип + возвращает объект для доп. проверок |
| Место возникновения | Любое место в методе (может быть ложным срабатыванием) | Только в переданном `Executable` |
| Проверка сообщения | Нет (требовался `ExpectedException @Rule`) | Да, через возвращённый объект |
| Читаемость | Аннотация далеко от бросающей строки | Встроена в поток теста |

**Пример «ложного срабатывания» в JUnit 4**

```java
// JUnit 4: тест проходит, хотя исключение не от targetMethod()
@Test(expected = NullPointerException.class)
void badTest() {
    String s = null;
    s.length(); // NPE здесь — не от тестируемого метода!
    targetMethod();
}
```

В JUnit 5 `assertThrows()` обёртывает конкретный `Executable`, поэтому такая подмена невозможна.

**assertDoesNotThrow() — явное утверждение об отсутствии исключения**

```java
@Test
void shouldParseValidDate() {
    // явно документируем, что парсинг корректного значения безопасен
    LocalDate result = assertDoesNotThrow(
        () -> dateParser.parse("2024-01-15")
    );
    assertThat(result.getYear()).isEqualTo(2024);
}
```

`assertDoesNotThrow()` принимает как `Executable` (void), так и `ThrowingSupplier<T>` — во втором случае возвращает результат вычисления, и его можно продолжать проверять.

**Когда использовать assertDoesNotThrow()**

- Когда хочите **явно документировать**, что конкретный блок не должен бросать исключения, а не полагаться на «тест молча не упал».
- При тестировании граничных значений, где некоторые значения бросают исключение, а другие — нет.

---

### Вопрос 55. Как в AssertJ проверить выброс исключения с помощью assertThatThrownBy() и assertThatExceptionOfType()? Чем они отличаются от catchThrowable() и когда предпочтительна каждая форма?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [AssertJ — Fluent testing assertions for Java and the JVM (официальная документация)](https://assertj.github.io/doc/#asserting-exceptions)

AssertJ предоставляет три основных способа проверки исключений:

**assertThatThrownBy()** — базовый fluent-способ:

```java
assertThatThrownBy(() -> { throw new Exception("boom!"); })
    .isInstanceOf(Exception.class)
    .hasMessageContaining("boom");
```

**assertThatExceptionOfType()** — альтернативный синтаксис, в котором тип исключения объявляется первым:

```java
assertThatExceptionOfType(IOException.class)
    .isThrownBy(() -> { throw new IOException("boom!"); })
    .withMessage("%s!", "boom")
    .withMessageContaining("boom")
    .withNoCause();
```

Существуют специализированные ярлыки: `assertThatIOException()`, `assertThatNullPointerException()`, `assertThatIllegalArgumentException()`, `assertThatIllegalStateException()`.

**catchThrowable()** — BDD-стиль, отделяет фазу WHEN от THEN:

```java
Throwable thrown = catchThrowable(() -> names[9]);
then(thrown).isInstanceOf(ArrayIndexOutOfBoundsException.class)
            .hasMessageContaining("9");
```

#### Ответ от Claude

**Три подхода AssertJ и их различия**

| Метод | Немедленный провал при отсутствии исключения | Возвращаемый тип | Стиль |
|---|---|---|---|
| `assertThatThrownBy(callable)` | Да | `AbstractThrowableAssert` (цепочка) | Fluent |
| `assertThatExceptionOfType(Type).isThrownBy(callable)` | Да | `AbstractThrowableAssert` (цепочка) | Тип-first |
| `catchThrowable(callable)` | Нет (возвращает `null`) | `Throwable` (объект) | BDD |

**assertThatThrownBy() — стандартный выбор**

```java
assertThatThrownBy(() -> orderService.place(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("order must not be null")
    .hasNoCause();
```

Подходит для большинства тестов: лаконично, читаемо, тип исключения рядом с проверкой.

**assertThatExceptionOfType() — когда тип важен как «контракт»**

```java
assertThatExceptionOfType(OrderNotFoundException.class)
    .isThrownBy(() -> orderService.findById(9999L))
    .withMessage("Order 9999 not found")
    .withNoCause();
```

Некоторые команды предпочитают этот стиль: тип виден сразу, как «заголовок» утверждения. Встроенные ярлыки:

```java
assertThatIllegalArgumentException()
    .isThrownBy(() -> new User(null, "pass"))
    .withMessageContaining("username");

assertThatNullPointerException()
    .isThrownBy(() -> service.process(null));
```

**catchThrowable() — BDD-стиль (Given/When/Then)**

```java
// GIVEN
Order order = new Order();
order.setQuantity(-1);

// WHEN
Throwable thrown = catchThrowable(() -> validator.validate(order));

// THEN
assertThat(thrown)
    .isInstanceOf(ValidationException.class)
    .hasMessageContaining("quantity must be positive");
```

Преимущество: явное разделение фаз теста. Если исключение не выброшено — `thrown` равен `null`, тест продолжается (не падает немедленно). Это позволяет проверять **несколько** аспектов результата после одного вызова.

Вариант `catchThrowableOfType()` выполняет сразу кастинг и провалит тест, если тип не совпадает:

```java
ValidationException ex = catchThrowableOfType(
    ValidationException.class,
    () -> validator.validate(order)
);
assertThat(ex.getViolations()).hasSize(2);
```

**Когда что выбирать**

- `assertThatThrownBy()` — дефолтный выбор; краткий и понятный.
- `assertThatExceptionOfType()` — когда команда предпочитает тип исключения первым.
- `catchThrowable()` — BDD-стиль или нужно проверить несколько утверждений после захвата исключения.

---

### Вопрос 56. Как в Mockito замокировать статический метод с помощью Mockito.mockStatic()? Каков правильный паттерн использования (try-with-resources), как верифицировать вызовы и каковы ограничения подхода?

**Категория:** Тестирование · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Mocking Static Methods With Mockito | Baeldung](https://www.baeldung.com/mockito-mock-static-methods)

Начиная с Mockito 3.4.0, метод `Mockito.mockStatic(Class<T> classToMock)` позволяет мокировать статические методы. Метод возвращает объект `MockedStatic<T>`, реализующий `AutoCloseable`.

Важный момент: scoped-мок должен быть закрыт той же сущностью, которая его открыла — именно поэтому используется try-with-resources.

```java
try (MockedStatic<StaticUtils> utilities =
         Mockito.mockStatic(StaticUtils.class)) {

    utilities.when(StaticUtils::name).thenReturn("Eugen");

    assertThat(StaticUtils.name()).isEqualTo("Eugen");
}
```

Методы с аргументами мокируются через лямбду:

```java
utilities.when(() -> StaticUtils.range(2, 6))
    .thenReturn(Arrays.asList(10, 11, 12));
```

**Важное замечание:** необходимость мокировать статические методы часто сигнализирует о плохом объектно-ориентированном дизайне; предпочтительнее рефакторинг.

#### Ответ от Claude

**Предпосылки и требования к окружению**

`mockStatic()` появился в Mockito 3.4.0 и требует **inline mock maker**:
- **Mockito 4.x и ниже:** добавить `mockito-inline` вместо `mockito-core`, или создать файл `src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker` со значением `mock-maker-inline`.
- **Mockito 5.0+:** inline mock maker включён по умолчанию, дополнительных шагов не требуется.

**Сигнатуры mockStatic()**

```java
// Базовая: все статические методы возвращают значения по умолчанию
public static <T> MockedStatic<T> mockStatic(Class<T> classToMock)

// С конфигурацией (MockSettings) — например, задать дефолтный ответ
public static <T> MockedStatic<T> mockStatic(
    Class<T> classToMock,
    Answer defaultAnswer)
```

**Паттерн try-with-resources (обязателен)**

`MockedStatic<T>` реализует `AutoCloseable`. Блок try-with-resources критически важен: незакрытый мок перехватывает статические вызовы **во всём потоке** до явного `close()`, что ломает другие тесты в параллельном прогоне.

```java
@Test
void shouldUseCurrentTime() {
    LocalDateTime fixedTime = LocalDateTime.of(2024, 1, 15, 12, 0);

    try (MockedStatic<LocalDateTime> mocked =
             Mockito.mockStatic(LocalDateTime.class)) {

        mocked.when(LocalDateTime::now).thenReturn(fixedTime);

        // тестируемый метод использует LocalDateTime.now()
        String result = scheduler.formatNextRun();

        assertThat(result).contains("2024-01-15");
    }
    // За пределами блока LocalDateTime.now() возвращает реальное время
}
```

**Верификация вызовов статических методов**

```java
try (MockedStatic<FileUtils> mocked = Mockito.mockStatic(FileUtils.class)) {
    mocked.when(() -> FileUtils.readFile("config.yml")).thenReturn("key: value");

    service.loadConfig("config.yml");

    // проверяем, что статический метод был вызван ровно 1 раз с нужным аргументом
    mocked.verify(() -> FileUtils.readFile("config.yml"), times(1));
    // проверяем, что других вызовов не было
    mocked.verifyNoMoreInteractions();
}
```

**Сравнение с mockConstruction()**

| Характеристика | `mockStatic()` | `mockConstruction()` |
|---|---|---|
| Что мокирует | Статические методы | Вызовы конструктора (`new X()`) |
| Тип мока | `MockedStatic<T>` | `MockedConstruction<T>` |
| Область действия | В пределах try-блока в текущем потоке | То же |
| Доступ к созданным экземплярам | Нет | `constructed()` |

**Ограничения**

- Нельзя мокировать статические методы классов, загруженных вне JVM (нативный код).
- Нельзя одновременно использовать один `MockedStatic` в нескольких потоках.
- Применение — крайняя мера: если код требует мокирования статики, рассмотрите инъекцию зависимости через интерфейс (например, `Clock` вместо `LocalDateTime.now()`).

---

### Вопрос 57. Как в Mockito мокировать void-методы с помощью doNothing(), doThrow() и doAnswer()? Почему для void-методов нельзя использовать when().thenReturn()?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Mocking Void Methods with Mockito | Baeldung](https://www.baeldung.com/mockito-void-methods)

Void-методы требуют специальных методов stubbing, так как у них нет возвращаемого значения. Mockito предоставляет три основных варианта:

**`doNothing()`** — поведение Mockito по умолчанию для void-методов на mock-объектах. Явно полезен при работе со шпионами (spy) или при необходимости захватить аргументы через `ArgumentCaptor`:

```java
doNothing().when(mock).voidMethod(any());
```

**`doThrow()`** — заставляет void-метод выбросить исключение:

```java
doThrow(new RuntimeException("error")).when(mock).voidMethod();
```

**`doAnswer()`** — выполняет кастомную логику при вызове метода:

```java
doAnswer(invocation -> {
    Object arg = invocation.getArgument(0);
    System.out.println("Called with: " + arg);
    return null;
}).when(mock).voidMethod(any());
```

#### Ответ от Claude

**Почему when().thenReturn() не работает для void-методов**

Синтаксис `when(mock.method()).thenReturn(value)` требует, чтобы `mock.method()` вернул значение, которое можно передать в `thenReturn()`. Void-метод не возвращает ничего, поэтому Java не позволяет использовать его как аргумент — это приведёт к ошибке компиляции. Именно для этого введены методы `do*()`, которые принимают метод иначе: сначала объявляется действие, затем указывается метод.

**Синтаксическое сравнение**

```java
// Обычный метод (возвращает значение)
when(mock.getValue()).thenReturn(42);         // корректно

// void-метод — использовать do*()
doNothing().when(mock).sendNotification();   // корректно
// when(mock.sendNotification()).thenReturn(??) — ошибка компиляции
```

**doNothing() — подавить вызов**

```java
@Test
void shouldSendWelcomeEmailWithoutActualDelivery() {
    EmailService emailService = mock(EmailService.class);
    // явно: ничего не делать при вызове sendEmail (это и так дефолт для mock)
    doNothing().when(emailService).sendEmail(anyString(), anyString());

    userRegistrationService.register(new User("alice@example.com"));

    // верификация, что метод был вызван
    verify(emailService).sendEmail(eq("alice@example.com"), contains("Welcome"));
}
```

`doNothing()` особенно полезен для **спионов** (spy), где по умолчанию вызывается реальный метод:

```java
EmailService spy = spy(new RealEmailService());
// Без doNothing() реальный sendEmail попытается подключиться к SMTP
doNothing().when(spy).sendEmail(anyString(), anyString());
```

**doThrow() — смоделировать ошибку**

```java
@Test
void shouldHandleNotificationFailure() {
    doThrow(new NotificationException("SMTP unavailable"))
        .when(emailService).sendEmail(anyString(), anyString());

    // проверяем, что сервис корректно обрабатывает ошибку уведомления
    assertThatThrownBy(() -> orderService.confirmOrder(order))
        .isInstanceOf(OrderProcessingException.class)
        .hasMessageContaining("notification failed");
}
```

**doAnswer() — кастомная логика**

```java
@Test
void shouldCaptureEventPayload() {
    List<String> capturedPayloads = new ArrayList<>();

    doAnswer(invocation -> {
        String payload = invocation.getArgument(0, String.class);
        capturedPayloads.add(payload);
        return null;  // void-метод возвращает null
    }).when(eventBus).publish(anyString());

    service.processOrder(order);

    assertThat(capturedPayloads)
        .hasSize(1)
        .first().contains("ORDER_CONFIRMED");
}
```

**Краткая сводка**

| Метод | Когда использовать |
|---|---|
| `doNothing()` | Заглушить void-метод (явно или для spy); дефолт для mock не нужен |
| `doThrow()` | Проверить обработку ошибок в вызывающем коде |
| `doAnswer()` | Инспектировать аргументы, накапливать вызовы, сложная логика |
| `doCallRealMethod()` | Частичный мок: вызвать реальную реализацию для конкретного метода |

---

### Вопрос 58. Для чего используется @WebFluxTest в Spring Boot? Что он загружает в контекст, как автоматически конфигурируется WebTestClient и чем @WebFluxTest отличается от @WebMvcTest?

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Testing Spring Boot Applications :: Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)

`@WebFluxTest` автоматически конфигурирует инфраструктуру Spring WebFlux и ограничивает сканирование бинов только веб-связанными компонентами.

Загружаемые типы бинов: `@Controller`, `@ControllerAdvice`, `@JacksonComponent`, `Converter`, `GenericConverter`, `Filter`, `HandlerInterceptor`, `WebFluxConfigurer`, `WebFluxRegistrations`, `HandlerMethodArgumentResolver`.

Не загружается: обычные `@Component`-бины, `@ConfigurationProperties` (для включения последних используйте `@EnableConfigurationProperties`).

`@WebFluxTest` автоматически конфигурирует `WebTestClient`:

```java
@WebFluxTest(UserVehicleController.class)
class MyWebFluxTests {

    @Autowired
    private WebTestClient webClient;

    @MockitoBean
    private UserVehicleService userVehicleService;

    @Test
    void exampleTest() {
        given(this.userVehicleService.getVehicleDetails("sboot"))
            .willReturn(new VehicleDetails("Honda", "Civic"));

        this.webClient
            .get().uri("/sboot/vehicle")
            .exchange()
            .expectStatus().isOk()
            .expectBody(VehicleDetails.class)
            .isEqualTo(new VehicleDetails("Honda", "Civic"));
    }
}
```

#### Ответ от Claude

**Что такое @WebFluxTest**

`@WebFluxTest` — test slice-аннотация Spring Boot, предназначенная для тестирования реактивных контроллеров WebFlux **без поднятия реального HTTP-сервера и без загрузки полного ApplicationContext**. Контроллеры выполняются в mock-окружении WebFlux.

**Что загружается, что — нет**

| Загружается | Не загружается |
|---|---|
| `@Controller`, `@RestController` | `@Service`, `@Repository`, `@Component` |
| `@ControllerAdvice` (обработка ошибок) | `@ConfigurationProperties` (нужен `@EnableConfigurationProperties`) |
| `Converter`, `GenericConverter` | Полный `ApplicationContext` |
| `Filter`, `HandlerInterceptor` | Слой данных (JPA, MongoDB и т.д.) |
| `WebTestClient` (авто-конфигурация) | — |

**WebTestClient — реактивный тестовый клиент**

`@WebFluxTest` автоматически создаёт `WebTestClient`, привязанный к mock-серверу через `bindToApplicationContext()`. Реальный TCP-сервер не запускается — это быстрее, чем `RANDOM_PORT`.

```java
@WebFluxTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private WebTestClient webClient;

    @MockitoBean
    private ProductService productService;

    @Test
    void shouldReturnProductById() {
        given(productService.findById(1L))
            .willReturn(Mono.just(new Product(1L, "Laptop", 999.99)));

        webClient.get().uri("/products/1")
            .exchange()
            .expectStatus().isOk()
            .expectBody()
            .jsonPath("$.name").isEqualTo("Laptop")
            .jsonPath("$.price").isEqualTo(999.99);
    }

    @Test
    void shouldReturn404WhenProductNotFound() {
        given(productService.findById(99L))
            .willReturn(Mono.empty());

        webClient.get().uri("/products/99")
            .exchange()
            .expectStatus().isNotFound();
    }
}
```

**@WebFluxTest vs @WebMvcTest**

| Критерий | `@WebMvcTest` | `@WebFluxTest` |
|---|---|---|
| Стек | Spring MVC (Servlet / блокирующий) | Spring WebFlux (реактивный) |
| Тестовый клиент | `MockMvc` | `WebTestClient` |
| Сервер | MockMvc (без сервера) | Reactive mock server (без сервера) |
| Реактивные типы (`Mono`, `Flux`) | Не поддерживает | Поддерживает |
| Зависимость | `spring-boot-starter-web` | `spring-boot-starter-webflux` |
| Мок зависимостей | `@MockitoBean` | `@MockitoBean` |

**Когда использовать @WebFluxTest**

- Проект использует Spring WebFlux (`spring-boot-starter-webflux`).
- Нужно тестировать реактивные контроллеры: маршрутизацию, сериализацию, обработку ошибок.
- Хочется быстрого теста без реального сервера.

Для полного HTTP-теста на реальном реактивном сервере используйте `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `WebTestClient`.

---

### Вопрос 59. Какие дополнительные test slice-аннотации для работы с данными предоставляет Spring Boot помимо @DataJpaTest? Опишите @DataMongoTest, @DataRedisTest, @DataJdbcTest и @DataNeo4jTest — что каждая загружает и как подключить реальную БД.

**Категория:** Тестирование · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Test Slices :: Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/appendix/test-auto-configuration/slices.html)

Spring Boot предоставляет несколько специализированных test slice-аннотаций для тестирования слоя данных:

**@DataMongoTest** — конфигурирует `MongoTemplate`, сканирует `@Document`-классы, загружает репозитории Spring Data MongoDB. По умолчанию использует встроенную MongoDB (Flapdoodle), если она доступна в classpath. Включает `TransactionAutoConfiguration`.

**@DataRedisTest** — конфигурирует `RedisConnectionFactory`, `RedisTemplate`, `StringRedisTemplate`, сканирует репозитории Spring Data Redis. Реальная база данных Redis обязательна (встроенного Redis нет); для тестов рекомендуется Testcontainers.

**@DataJdbcTest** — минимальная конфигурация для Spring Data JDBC: только `DataJdbcRepositoriesAutoConfiguration`. Транзакции оборачиваются и откатываются автоматически. Использует in-memory H2 по умолчанию.

**@DataNeo4jTest** — конфигурирует репозитории Spring Data Neo4j с поддержкой транзакций. Включает `TransactionAutoConfiguration` и `DataNeo4jAutoConfiguration`. Реальная база данных Neo4j требуется (Testcontainers или embedded).

#### Ответ от Claude

**Общая концепция data test slices**

Все data slice-аннотации загружают **только** слой данных: репозитории, маппинг сущностей, конвертеры — но не веб-слой, не `@Service`-бины, не полный `ApplicationContext`. Это делает тесты быстрыми и сфокусированными.

**@DataMongoTest**

```java
@DataMongoTest
class ProductRepositoryMongoTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void shouldSaveAndFindProduct() {
        Product product = new Product("Laptop", 999.99);
        productRepository.save(product);

        Optional<Product> found = productRepository.findByName("Laptop");
        assertThat(found).isPresent()
            .get().extracting(Product::getPrice).isEqualTo(999.99);
    }
}
```

Для реальной MongoDB (вместо in-memory Flapdoodle):

```java
@DataMongoTest(excludeAutoConfiguration = EmbeddedMongoAutoConfiguration.class)
@Testcontainers
class ProductRepositoryMongoTest {

    @Container
    @ServiceConnection
    static MongoDBContainer mongo = new MongoDBContainer("mongo:7");

    // остальное как обычно
}
```

**@DataRedisTest**

Встроенного Redis нет — всегда нужен реальный сервер или Testcontainers:

```java
@DataRedisTest
@Testcontainers
class CartRepositoryRedisTest {

    @Container
    @ServiceConnection
    static GenericContainer<?> redis =
        new GenericContainer<>("redis:7-alpine").withExposedPorts(6379);

    @Autowired
    private CartRepository cartRepository;

    @Test
    void shouldStoreCartInRedis() {
        Cart cart = new Cart("user-1", List.of("item-1", "item-2"));
        cartRepository.save(cart);
        assertThat(cartRepository.findById("user-1")).isPresent();
    }
}
```

**@DataJdbcTest**

```java
@DataJdbcTest
class OrderRepositoryJdbcTest {

    @Autowired
    private OrderRepository orderRepository;

    @Test
    @Transactional  // оборачивается автоматически, но @Transactional можно указать явно
    void shouldPersistOrder() {
        Order order = new Order("PENDING", BigDecimal.valueOf(99.99));
        Order saved = orderRepository.save(order);
        assertThat(saved.getId()).isNotNull();
    }
}
```

Для реальной БД вместо H2: аннотируйте `@AutoConfigureTestDatabase(replace = Replace.NONE)` и добавьте Testcontainers с `@ServiceConnection`.

**@DataNeo4jTest**

```java
@DataNeo4jTest
@Testcontainers
class PersonRepositoryNeo4jTest {

    @Container
    @ServiceConnection
    static Neo4jContainer<?> neo4j = new Neo4jContainer<>("neo4j:5-community");

    @Autowired
    private PersonRepository personRepository;

    @Test
    void shouldFindByName() {
        personRepository.save(new Person("Alice", "Engineer"));
        assertThat(personRepository.findByName("Alice")).isPresent();
    }
}
```

**Сравнительная таблица**

| Аннотация | Загружает | Дефолтная БД | Транзакции |
|---|---|---|---|
| `@DataJpaTest` | JPA, Hibernate, JPA-репозитории | H2 (in-memory) | `@Transactional` + откат |
| `@DataJdbcTest` | Spring Data JDBC, JDBC-репозитории | H2 (in-memory) | `@Transactional` + откат |
| `@DataMongoTest` | MongoTemplate, Mongo-репозитории | Flapdoodle (embedded) | Есть (`TransactionAutoConfiguration`) |
| `@DataRedisTest` | RedisTemplate, Redis-репозитории | — (внешний Redis обязателен) | Нет |
| `@DataNeo4jTest` | Neo4j-репозитории | — (внешний Neo4j обязателен) | Есть (`TransactionAutoConfiguration`) |

---

### Вопрос 60. Что такое Testcontainers withReuse(true)? Как работает механизм хэш-переиспользования контейнеров, как его активировать через ~/.testcontainers.properties, и почему его нельзя применять в CI?

**Категория:** Тестирование · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Reusable Containers (Experimental) — Testcontainers for Java](https://java.testcontainers.org/features/reuse/)

Функция Reusable Containers — экспериментальная оптимизация производительности: контейнер остаётся запущенным после завершения тестов и при следующем прогоне Testcontainers переиспользует его вместо того, чтобы создавать новый.

**Механизм:** при запуске контейнера с `.withReuse(true)` Testcontainers вычисляет хэш конфигурации контейнера (образ, порты, переменные окружения и т.д.). Если при следующем запуске хэш совпадает, тот же контейнер переиспользуется.

**Активация:** необходимо добавить `testcontainers.reuse.enable=true` в файл `~/.testcontainers.properties`. Включение через classpath-файл не поддерживается.

**Критическое ограничение:** после завершения тестов контейнер **не останавливается**. Не следует использовать блок try-with-resources или явно вызывать `.stop()`. Это значит, что функция не предназначена для CI-сред, где ресурсы после сборки должны освобождаться.

#### Ответ от Claude

**Зачем нужно переиспользование контейнеров**

Запуск контейнера (PostgreSQL, Kafka, Redis) занимает 5–30 секунд. При частом запуске тестов в локальной разработке это накапливается. `withReuse(true)` позволяет держать один контейнер «живым» между прогонами и просто подключаться к нему заново.

**Механизм хэш-переиспользования**

Testcontainers вычисляет хэш на основе конфигурации контейнера:
- Docker-образ и тег
- Открытые порты (`withExposedPorts`)
- Переменные окружения (`withEnv`)
- Команда запуска (`withCommand`)
- Смонтированные тома

Если запущенный контейнер с идентичным хэшем уже существует — он переиспользуется. Если конфигурация изменилась (например, сменили тег образа) — запустится новый контейнер.

**Код с withReuse(true)**

```java
static PostgreSQLContainer<?> POSTGRES =
    new PostgreSQLContainer<>("postgres:16-alpine")
        .withReuse(true);   // включить переиспользование

static {
    POSTGRES.start();  // если контейнер уже жив — вернёт быстро
}
```

Важно: **не** использовать try-with-resources и **не** вызывать `.stop()` — иначе контейнер будет остановлен, и переиспользование не сработает.

**Активация через ~/.testcontainers.properties**

Файл находится в домашней директории пользователя. Добавьте строку:

```properties
# ~/.testcontainers.properties
testcontainers.reuse.enable=true
```

Альтернатива — переменная окружения: `TESTCONTAINERS_REUSE_ENABLE=true`.

**Почему нельзя использовать в CI**

1. **Контейнеры не останавливаются** после сборки — в CI-системах (GitHub Actions, Jenkins) каждая сборка должна освобождать ресурсы. Висящий контейнер из предыдущей сборки будет потреблять память и порты.
2. **Загрязнение состояния** — переиспользованный контейнер сохраняет данные предыдущего прогона. Если тесты не выполняют очистку явно (`@Sql`, `TRUNCATE TABLE`), результаты могут быть непредсказуемы.
3. **Конкурирующие сборки** — параллельные CI-джобы могут попытаться использовать один контейнер с разными ожиданиями.

**Правильная стратегия: withReuse для локальной разработки, свежий контейнер на CI**

```java
static PostgreSQLContainer<?> POSTGRES =
    new PostgreSQLContainer<>("postgres:16-alpine")
        // withReuse работает только если testcontainers.reuse.enable=true в properties
        // в CI этот флаг не выставлен — контейнер будет создан заново
        .withReuse(true);
```

Такой код безопасен: в CI `testcontainers.reuse.enable` не задан, поэтому `.withReuse(true)` игнорируется и контейнер создаётся с нуля при каждом прогоне.

**Ограничения функции**

- Экспериментальный статус: поведение может измениться.
- Сети (`withNetwork()`) не поддерживаются при reuse — смена сетевой конфигурации нарушает хэш.
- Не работает для JDBC URL (`jdbc:tc:...`) без явного добавления `TC_REUSABLE=true` к URL.
- Ryuk (авто-очистка Testcontainers) не завершает reuse-контейнеры.
