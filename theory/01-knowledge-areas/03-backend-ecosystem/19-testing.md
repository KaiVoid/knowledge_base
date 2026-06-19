# Тестирование

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по тестированию →](../../../interview-questions/testing-01.md)
> **Связанные области:** [[11-solid-clean-code]], [[14-spring-boot]]

## Что это и зачем

Автоматическое тестирование — обязательная часть промышленной разработки. Нужно уметь писать
модульные (unit) тесты с JUnit и Mockito, понимать пирамиду тестирования, отличать виды тестов
(unit, integration, e2e) и тестировать Spring-приложения. Хорошие тесты обеспечивают надёжность
и возможность безопасного рефакторинга.

Тесты также служат живой документацией: по ним видно, какое поведение системы считается корректным.
В современных Java-проектах стек де-факто — JUnit 5 (Jupiter) + Mockito 5 + Spring Test;
для интеграционных тестов с реальными базами данных всё чаще применяется Testcontainers.

## Ключевые подтемы

### Пирамида тестирования

Концепция Майка Кона описывает три слоя автотестов:

| Уровень | Скорость | Стоимость | Доля в проекте |
|---------|----------|-----------|----------------|
| Unit (модульные) | Очень быстро (мс) | Дёшево | ~70% |
| Integration (интеграционные) | Медленнее (секунды) | Дороже | ~20% |
| End-to-end (сквозные) | Медленно (десятки секунд) | Дорого | ~10% |

**Модульные тесты** проверяют один класс или метод в изоляции; все зависимости заменяются
тест-дублёрами. **Интеграционные** поднимают несколько компонентов вместе — например, Spring
контекст с реальной базой или HTTP-клиент. **End-to-end** прогоняют сценарий через всю систему
от UI/API до базы данных.

### Виды тест-дублёров

| Вид | Определение |
|-----|-------------|
| **Stub** | Возвращает заранее заданный ответ, не проверяет вызовы |
| **Mock** | Записывает вызовы; в конце теста проверяют, что методы вызывались с нужными аргументами |
| **Spy** | Оборачивает реальный объект; реальные методы вызываются, но взаимодействия фиксируются |
| **Fake** | Упрощённая работающая реализация (например, HashMap-репозиторий вместо JPA) |
| **Dummy** | Объект, который передаётся, но никогда не используется |

Термины введены Джерардом Месарошем в книге *xUnit Test Patterns* (2007).

---

### JUnit 5 (Jupiter)

JUnit 5 = Platform + Vintage + Jupiter. В повседневной работе используется **Jupiter** —
новый API для написания тестов, вошедший в JUnit 5.0 (сентябрь 2017).

Документация: [docs.junit.org/current/user-guide/](https://docs.junit.org/current/user-guide/)

#### Основные аннотации

| Аннотация | Пакет | Назначение |
|-----------|-------|------------|
| `@Test` | `org.junit.jupiter.api` | Помечает метод как тест |
| `@BeforeEach` | `org.junit.jupiter.api` | Выполняется перед каждым тестом |
| `@AfterEach` | `org.junit.jupiter.api` | Выполняется после каждого теста |
| `@BeforeAll` | `org.junit.jupiter.api` | Один раз перед всеми тестами класса (статический метод или PER_CLASS) |
| `@AfterAll` | `org.junit.jupiter.api` | Один раз после всех тестов класса |
| `@Disabled` | `org.junit.jupiter.api` | Отключает тест или класс |
| `@DisplayName` | `org.junit.jupiter.api` | Произвольное читаемое имя теста |
| `@Tag` | `org.junit.jupiter.api` | Тег для фильтрации тестов при запуске |
| `@Nested` | `org.junit.jupiter.api` | Вложенный тестовый класс (группировка) |
| `@RepeatedTest` | `org.junit.jupiter.api` | Повторяет тест N раз |
| `@ParameterizedTest` | `org.junit.jupiter.params` | Параметризованный тест |
| `@TestMethodOrder` | `org.junit.jupiter.api` | Порядок выполнения тестов в классе |
| `@TestInstance` | `org.junit.jupiter.api` | Жизненный цикл экземпляра теста |
| `@ExtendWith` | `org.junit.jupiter.api.extension` | Подключение расширений |
| `@Timeout` | `org.junit.jupiter.api` | Ограничение времени выполнения |
| `@TempDir` | `org.junit.jupiter.api.io` | Временная директория для теста |

#### Жизненный цикл экземпляра теста

По умолчанию JUnit создаёт **новый экземпляр** тестового класса для каждого тест-метода
(`Lifecycle.PER_METHOD`). Это изолирует тесты друг от друга.

При аннотации `@TestInstance(Lifecycle.PER_CLASS)` один экземпляр используется для всех тестов
класса. Это позволяет:
- объявить `@BeforeAll` / `@AfterAll` на нестатических методах;
- использовать нестатические поля в `@MethodSource`-методах.

```java
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class OrderServiceTest {

    private OrderService service;

    @BeforeAll
    void initService() {             // не статический!
        service = new OrderService();
    }

    @Test
    void shouldCreateOrder() { /* ... */ }
}
```

#### Assertions (утверждения)

Класс `org.junit.jupiter.api.Assertions` — API: [docs.junit.org/.../Assertions.html](https://docs.junit.org/5.14.0/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html)

```java
// базовые проверки
assertEquals(42, result);
assertNotNull(obj);
assertTrue(list.isEmpty());
assertArrayEquals(expected, actual);

// проверка исключений — возвращает объект исключения для дальнейших проверок
IllegalArgumentException ex =
    assertThrows(IllegalArgumentException.class, () -> service.process(null));
assertEquals("arg must not be null", ex.getMessage());

// все утверждения выполняются, даже если первое упало
assertAll("user fields",
    () -> assertEquals("Ivan", user.getName()),
    () -> assertEquals("ivan@example.com", user.getEmail())
);

// ограничение по времени; тест прерывается при превышении
assertTimeout(Duration.ofMillis(100), () -> service.heavyOperation());
```

#### Assumptions (предположения)

Если условие не выполнено, тест помечается как *aborted* (не как failed):

```java
assumeTrue("CI".equals(System.getenv("ENV")));
// код ниже выполнится только в CI-окружении
```

#### Параметризованные тесты

Требуют зависимости `junit-jupiter-params`. Источники данных:

```java
@ParameterizedTest
@ValueSource(strings = {"racecar", "radar", "level"})
void isPalindrome(String word) {
    assertTrue(StringUtils.isPalindrome(word));
}

@ParameterizedTest
@CsvSource({"1, 1, 2", "2, 3, 5", "10, 20, 30"})
void addition(int a, int b, int expected) {
    assertEquals(expected, a + b);
}

@ParameterizedTest
@MethodSource("provideUsers")        // фабричный метод
void userValidation(User user) { /* ... */ }

static Stream<User> provideUsers() {
    return Stream.of(new User("Alice"), new User("Bob"));
}

@ParameterizedTest
@EnumSource(value = DayOfWeek.class, names = {"SATURDAY", "SUNDAY"})
void weekendsAreNotWorkDays(DayOfWeek day) { /* ... */ }
```

Также есть `@NullSource`, `@EmptySource`, `@NullAndEmptySource`, `@CsvFileSource`,
`@ArgumentsSource` для кастомных провайдеров.

#### Вложенные тесты (@Nested)

```java
class AccountTest {

    @Nested
    @DisplayName("когда счёт пустой")
    class WhenEmpty {
        @Test void balanceIsZero() { assertEquals(0, account.getBalance()); }
        @Test void withdrawThrows() { assertThrows(InsufficientFundsException.class, () -> account.withdraw(10)); }
    }

    @Nested
    @DisplayName("когда счёт пополнен")
    class WhenFunded {
        @BeforeEach void deposit() { account.deposit(100); }
        @Test void canWithdraw() { assertDoesNotThrow(() -> account.withdraw(50)); }
    }
}
```

#### Условные аннотации

Расположены в пакете `org.junit.jupiter.api.condition`:

```java
@EnabledOnOs(OS.LINUX)
@DisabledOnJre(JRE.JAVA_8)
@EnabledIfEnvironmentVariable(named = "CI", matches = "true")
@EnabledIfSystemProperty(named = "test.mode", matches = "full")
```

#### Расширения (@ExtendWith)

JUnit 5 использует единый Extension API вместо Runner/Rule. Расширения подключаются:

```java
@ExtendWith(MockitoExtension.class)   // пример из Mockito
class MyTest { }
```

Собственное расширение реализует один или несколько интерфейсов: `BeforeEachCallback`,
`AfterEachCallback`, `ParameterResolver`, `TestExecutionExceptionHandler` и др.

---

### Mockito

Mockito — библиотека для создания тест-дублёров в Java.
Актуальная версия 5.x требует Java 11+.
Javadoc: [site.mockito.org/javadoc/current/](https://site.mockito.org/javadoc/current/org/mockito/Mockito.html)

#### Интеграция с JUnit 5

Для JUnit Jupiter добавляется отдельный артефакт `mockito-junit-jupiter`:

```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>5.14.2</version>
    <scope>test</scope>
</dependency>
```

```java
@ExtendWith(MockitoExtension.class)    // автоматически инициализирует @Mock и т.д.
class PaymentServiceTest {

    @Mock
    PaymentGateway gateway;

    @Spy
    AuditLog auditLog = new AuditLog();

    @Captor
    ArgumentCaptor<PaymentRequest> requestCaptor;

    @InjectMocks                       // внедряет gateway и auditLog
    PaymentService service;

    @Test
    void shouldChargeCorrectAmount() {
        when(gateway.charge(any())).thenReturn(new PaymentResult("OK"));

        service.pay(new Order(100));

        verify(gateway).charge(requestCaptor.capture());
        assertEquals(100, requestCaptor.getValue().getAmount());
    }
}
```

Без расширения — ручная инициализация:

```java
AutoCloseable mocks = MockitoAnnotations.openMocks(this);
// после теста:
mocks.close();
```

#### Stubbing

```java
// базовый стаб
when(repo.findById(1L)).thenReturn(Optional.of(user));

// исключение
when(repo.findById(-1L)).thenThrow(new IllegalArgumentException("bad id"));

// последовательные ответы
when(clock.now()).thenReturn(t1).thenReturn(t2).thenReturn(t3);

// динамический ответ
when(formatter.format(any())).thenAnswer(inv -> inv.getArgument(0).toString().toUpperCase());

// для void-методов и spy — семейство do*
doThrow(new IOException()).when(fileWriter).write(anyString());
doReturn(42).when(spy).heavyCalc();
doNothing().when(mock).doSomething();
```

#### Проверка вызовов (verify)

```java
verify(gateway).charge(any());                  // ровно один раз
verify(cache, times(2)).put(any(), any());
verify(logger, never()).error(anyString());
verify(dao, atLeastOnce()).save(any());
verify(dao, atMost(3)).save(any());

// проверка отсутствия других вызовов
verifyNoMoreInteractions(gateway);
verifyNoInteractions(auditLog);
```

#### Порядок вызовов (InOrder)

```java
InOrder inOrder = inOrder(step1, step2, step3);
inOrder.verify(step1).execute();
inOrder.verify(step2).execute();
inOrder.verify(step3).execute();
```

#### ArgumentMatchers

```java
// встроенные матчеры из ArgumentMatchers
any(), any(User.class)
anyInt(), anyLong(), anyString()
eq("exact"), isNull(), isNotNull()
startsWith("prefix"), endsWith("suffix"), contains("part")

// кастомный матчер
argThat(user -> user.getAge() >= 18)
```

Важно: если хотя бы один аргумент в `when`/`verify` — матчер, все остальные тоже должны
быть матчерами (нельзя смешивать литерал и `any()`).

#### ArgumentCaptor

Используется для захвата аргументов, переданных в мок, когда нужно проверить сложный объект:

```java
ArgumentCaptor<User> captor = ArgumentCaptor.forClass(User.class);
verify(repo).save(captor.capture());

User saved = captor.getValue();
assertEquals("Alice", saved.getName());
assertEquals(30, saved.getAge());
```

#### Spy (частичное мокирование)

Spy оборачивает реальный объект: незастабленные методы вызываются по-настоящему.

```java
List<String> real = new ArrayList<>();
List<String> spy  = spy(real);

spy.add("one");           // реальный вызов
when(spy.size()).thenReturn(100);  // переопределяем только size()

assertEquals("one", spy.get(0));  // реальный вызов
assertEquals(100, spy.size());    // застабленный

// Важно: не используй when() со spy для void-методов —
// реальный метод вызывается ДО stubbing. Используй doReturn():
doReturn("val").when(spy).protectedMethod();
```

#### BDD-стиль (BDDMockito)

```java
import static org.mockito.BDDMockito.*;

// given
given(seller.askForBread()).willReturn(new Bread());

// when
person.buy(bread);

// then
then(seller).should(times(1)).askForBread();
then(seller).shouldHaveNoMoreInteractions();
```

#### Строгость (Strictness) и STRICT_STUBS

По умолчанию `MockitoExtension` использует `Strictness.STRICT_STUBS`. Это означает:
- лишние стабы (заданные, но не вызванные) вызывают ошибку → тесты DRY;
- несоответствие аргументов при вызове застабленного метода немедленно сообщается;
- автоматически вызывается `verifyNoMoreInteractions` на всех моках после теста.

Изменить строгость для класса:

```java
@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class LenientTest { }
```

---

### Тестирование Spring

#### @SpringBootTest

Загружает **полный** ApplicationContext:

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class FullIntegrationTest {

    @Autowired
    TestRestTemplate restTemplate;

    @Test
    void healthCheck() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/actuator/health", String.class);
        assertEquals(HttpStatus.OK, resp.getStatusCode());
    }
}
```

`WebEnvironment` может быть `MOCK` (по умолчанию, MockMvc), `RANDOM_PORT`, `DEFINED_PORT`,
`NONE` (без web-слоя).

#### @WebMvcTest — срез веб-слоя

Загружает только MVC-компоненты (`@Controller`, `@ControllerAdvice`, `@JsonComponent`,
`Filter`, `WebMvcConfigurer`). Сервисный слой нужно мокировать через `@MockBean`:

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    UserService userService;

    @Test
    void shouldReturnUser() throws Exception {
        given(userService.findById(1L)).willReturn(new User(1L, "Alice"));

        mockMvc.perform(get("/users/1").accept(MediaType.APPLICATION_JSON))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

#### @DataJpaTest — срез JPA-слоя

Загружает только JPA-компоненты, подставляет встроенную H2 (если не настроено иное),
оборачивает каждый тест в транзакцию, которая откатывается после теста.

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    UserRepository userRepository;

    @Test
    void shouldFindByEmail() {
        userRepository.save(new User("bob@example.com"));
        Optional<User> found = userRepository.findByEmail("bob@example.com");
        assertTrue(found.isPresent());
    }
}
```

Чтобы использовать реальную БД (например, PostgreSQL через Testcontainers):

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class UserRepositoryRealDbTest { }
```

#### @MockBean и @SpyBean

`@MockBean` заменяет бин в ApplicationContext моком Mockito.
`@SpyBean` оборачивает реальный бин шпионом.

Важно: при использовании `@MockBean`/`@SpyBean` контекст Spring **перезапускается**
(кеш инвалидируется), что замедляет тесты. По возможности выносите их в общий
базовый класс теста.

#### MockMvc

MockMvc позволяет тестировать HTTP-слой без поднятия реального сервера.
Доступны интеграции с Hamcrest (`.andExpect(jsonPath(...).value(...))`),
AssertJ и HtmlUnit.

```java
mockMvc.perform(post("/orders")
           .contentType(MediaType.APPLICATION_JSON)
           .content("{\"item\":\"book\",\"qty\":2}"))
       .andExpect(status().isCreated())
       .andExpect(header().string("Location", containsString("/orders/")))
       .andDo(print());
```

Документация MockMvc: [docs.spring.io/.../testing/mockmvc.html](https://docs.spring.io/spring-framework/reference/testing/mockmvc.html)

#### TestContext Framework и кэширование контекста

Spring кэширует `ApplicationContext` по набору параметров конфигурации
(`@ContextConfiguration`, `@ActiveProfiles`, `@TestPropertySource` и др.).
Если два тестовых класса используют одинаковую конфигурацию, контекст создаётся один раз —
это критически ускоряет прогон тестов.

`@DirtiesContext` сигнализирует, что тест модифицирует контекст — после него контекст
пересоздаётся. Режимы: `AFTER_CLASS` (по умолчанию для класса), `AFTER_EACH_TEST_METHOD`.

Максимальный размер кеша контекстов: `spring.test.context.cache.maxSize=32` (по умолчанию).

```java
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = "app.feature.enabled=true")
class FeatureToggleTest { }
```

`@DynamicPropertySource` — для динамической регистрации свойств (например, URL
Testcontainers-контейнера):

```java
@DynamicPropertySource
static void dbProps(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
}
```

---

### Testcontainers

Testcontainers запускает Docker-контейнеры из тестов, обеспечивая реальное окружение
для интеграционных тестов (PostgreSQL, Redis, Kafka и др.).

Документация JUnit 5 интеграции: [java.testcontainers.org/test_framework_integration/junit_5/](https://java.testcontainers.org/test_framework_integration/junit_5/)

#### Зависимости

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers-junit-jupiter</artifactId>
    <version>1.20.4</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <version>1.20.4</version>
    <scope>test</scope>
</dependency>
```

#### Жизненный цикл контейнера

- **Статическое поле (`static`)** — контейнер запускается один раз для всего тестового
  класса и останавливается после последнего теста. Экономит время.
- **Поле экземпляра** — контейнер запускается и останавливается для каждого тест-метода.
  Максимальная изоляция.

```java
@Testcontainers
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class UserRepositoryPostgresTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void overrideProps(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url",      postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    UserRepository repo;

    @Test
    void savesAndFinds() {
        repo.save(new User("alice@example.com"));
        assertTrue(repo.findByEmail("alice@example.com").isPresent());
    }
}
```

---

### TDD (разработка через тестирование)

TDD — цикл Red → Green → Refactor:

1. **Red** — пишем тест, который заведомо проваливается (фича ещё не реализована).
2. **Green** — пишем минимальный код, чтобы тест прошёл.
3. **Refactor** — улучшаем код без изменения поведения; тесты должны оставаться зелёными.

Преимущества: дизайн API появляется через тесты, высокое покрытие «бесплатно»,
безопасный рефакторинг.

### Покрытие кода

Инструменты: **JaCoCo** (наиболее распространён в Maven/Gradle), IntelliJ IDEA Coverage.
Покрытие бывает:
- **Line coverage** — сколько строк исполнено;
- **Branch coverage** — сколько ветвей (if/else/switch) пройдено;
- **Instruction coverage** (байт-код) — самое детальное.

100% покрытие не гарантирует корректность; важнее покрыть граничные случаи
и нетривиальную логику. Цель в большинстве проектов — 70–80% branch coverage для
бизнес-логики.

---

## Достоверные источники

1. **[JUnit 5 User Guide](https://docs.junit.org/current/user-guide/)** — официальное руководство
   JUnit 5 от команды JUnit. Авторитетный первичный источник по всем аннотациям, расширениям,
   параметризации и жизненному циклу.

2. **[JUnit 5 Assertions API](https://docs.junit.org/5.14.0/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html)** — официальный Javadoc
   класса `Assertions` с полным списком методов.

3. **[Mockito Javadoc (site.mockito.org)](https://site.mockito.org/javadoc/current/org/mockito/Mockito.html)** — официальный Javadoc
   основного класса `Mockito`; содержит 42 пронумерованных раздела с примерами использования
   каждого паттерна. Единственный первичный источник по API Mockito.

4. **[MockitoExtension Javadoc (5.10.0)](https://javadoc.io/static/org.mockito/mockito-junit-jupiter/5.10.0/org/mockito/junit/jupiter/MockitoExtension.html)** — официальный Javadoc
   JUnit Jupiter-интеграции Mockito; описывает `@MockitoSettings`, `Strictness` и
   `openMocks`.

5. **[Spring Framework — Testing Reference](https://docs.spring.io/spring-framework/reference/testing.html)** — официальная документация
   Spring по тестированию: TestContext Framework, MockMvc, аннотации `@ActiveProfiles`,
   `@DirtiesContext`, `@Sql`, транзакции в тестах.

6. **[Testcontainers for Java — JUnit 5 Integration](https://java.testcontainers.org/test_framework_integration/junit_5/)** — официальная
   документация Testcontainers по интеграции с JUnit Jupiter: аннотации `@Testcontainers`,
   `@Container`, жизненный цикл контейнеров.
