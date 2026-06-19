# Spring Boot

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по Spring Boot →](../../../interview-questions/spring-boot-01.md)
> **Связанные области:** [[13-spring-core]], [[17-rest-web]], [[20-microservices]]

## Что это и зачем

Spring Boot — надстройка над Spring, упрощающая создание production-ready приложений за счёт
автоконфигурации, стартеров и встроенного сервера. Это основной инструмент для построения
современных микросервисов и REST-API на Java. Нужно понимать механизм автоконфигурации, стартеры,
профили, внешнюю конфигурацию и Actuator для мониторинга.

Ключевая идея Spring Boot: «convention over configuration» — разработчик получает разумные
настройки по умолчанию и переопределяет только то, что отличается от стандарта. Приложение
собирается в исполняемый fat-JAR с встроенным сервером и запускается одной командой `java -jar`.

## Ключевые подтемы

### 1. Автоконфигурация

**Как работает.** Spring Boot анализирует classpath и уже зарегистрированные бины, после чего
применяет классы автоконфигурации через механизм условий (`@Conditional*`). Например, если в
classpath присутствует HSQLDB и не объявлен бин `DataSource`, Spring Boot создаёт бин
in-memory базы данных автоматически.

**Точка входа.** Аннотация `@SpringBootApplication` объединяет три аннотации:
- `@SpringBootConfiguration` — помечает класс как источник конфигурации (специализация `@Configuration`).
- `@EnableAutoConfiguration` — включает механизм автоконфигурации.
- `@ComponentScan` — включает сканирование компонентов в пакете класса и его подпакетах.

```java
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

**Регистрация классов автоконфигурации.** Классы автоконфигурации перечисляются построчно в файле:

```
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

Компонентное сканирование не используется — это намеренное ограничение, предотвращающее случайную
загрузку ненужных конфигураций.

**Условные аннотации (`@Conditional*`).** Каждый класс автоконфигурации управляется условиями:

| Аннотация | Смысл |
|---|---|
| `@ConditionalOnClass` | Класс присутствует в classpath |
| `@ConditionalOnMissingClass` | Класс отсутствует в classpath |
| `@ConditionalOnBean` | Бин данного типа уже зарегистрирован |
| `@ConditionalOnMissingBean` | Бин данного типа ещё не зарегистрирован |
| `@ConditionalOnProperty` | Свойство имеет заданное значение |
| `@ConditionalOnResource` | Ресурс присутствует в classpath |
| `@ConditionalOnWebApplication` | Приложение является веб-приложением |
| `@ConditionalOnExpression` | SpEL-выражение вычисляется в `true` |

```java
@AutoConfiguration
public class MyServiceAutoConfiguration {

    @Configuration(proxyBeanMethods = false)
    @ConditionalOnClass(MyService.class)
    static class MyServiceConfiguration {

        @Bean
        @ConditionalOnMissingBean
        MyService myService() {
            return new MyService();
        }
    }
}
```

**Порядок применения автоконфигураций.** Управляется аннотациями:

```java
@AutoConfiguration(before = WebMvcAutoConfiguration.class)
@AutoConfiguration(after = DataSourceAutoConfiguration.class)
// или через отдельные аннотации:
@AutoConfigureBefore(WebMvcAutoConfiguration.class)
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
```

**Отключение отдельных автоконфигураций.** Три способа:

```java
// 1. Атрибут exclude (если класс есть в classpath)
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class MyApplication { }

// 2. Атрибут excludeName (если класса нет в classpath)
@SpringBootApplication(excludeName =
    "org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration")
public class MyApplication { }
```

```properties
# 3. Через свойство конфигурации
spring.autoconfigure.exclude=org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration
```

**Отладка автоконфигурации.** Запустить приложение с флагом `--debug` — в консоль выводится
отчёт об условиях: какие конфигурации применились и почему, а какие были пропущены.

Источник: [Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html)

---

### 2. Стартеры и управление зависимостями

**Starters** — POM-дескрипторы зависимостей, собирающие в одном артефакте все необходимые
библиотеки для конкретной задачи. Стартер не содержит кода — только транзитивные зависимости с
согласованными версиями.

Соглашение об именовании: `spring-boot-starter-*` — официальные стартеры; для сторонних
библиотек принято `{имя-проекта}-spring-boot-starter`.

**Основные стартеры:**

| Стартер | Что подключает |
|---|---|
| `spring-boot-starter` | Core: auto-configuration, логирование (Logback), YAML |
| `spring-boot-starter-web` / `spring-boot-starter-webmvc` | Spring MVC + встроенный Tomcat |
| `spring-boot-starter-webflux` | Reactive WebFlux + Reactor Netty |
| `spring-boot-starter-data-jpa` | JPA + Hibernate + Spring Data JPA |
| `spring-boot-starter-data-jdbc` | Spring Data JDBC |
| `spring-boot-starter-data-mongodb` | Spring Data MongoDB |
| `spring-boot-starter-data-redis` | Spring Data Redis (Lettuce) |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-actuator` | Spring Boot Actuator |
| `spring-boot-starter-amqp` | Spring AMQP + RabbitMQ |
| `spring-boot-starter-kafka` | Spring for Apache Kafka |
| `spring-boot-starter-batch` | Spring Batch |
| `spring-boot-starter-thymeleaf` | Thymeleaf template engine |
| `spring-boot-starter-test` | JUnit Jupiter, AssertJ, Hamcrest, Mockito |
| `spring-boot-starter-log4j2` | Log4j2 (замена Logback) |

**BOM (Bills of Materials).** Spring Boot поставляет `spring-boot-dependencies` BOM, содержащий
согласованные версии всех поддерживаемых зависимостей. При использовании Spring Boot Maven/Gradle
плагина версии указывать не нужно:

```xml
<!-- Maven: версии управляются через parent или import BOM -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <!-- версия не нужна — управляется BOM -->
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <!-- версия тоже из BOM -->
    </dependency>
</dependencies>
```

```kotlin
// Gradle (build.gradle.kts)
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

Важно: не указывать версию `org.springframework:spring-*` вручную — Spring Boot управляет ею сам.

Источник: [Build Systems :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/build-systems.html)

---

### 3. Встроенные серверы (Embedded Servers)

Spring Boot поддерживает три встроенных servlet-контейнера: **Tomcat** (по умолчанию),
**Jetty** и **Undertow**. Для реактивных приложений (WebFlux) по умолчанию используется
**Reactor Netty**.

**Выбор сервера.** Чтобы переключиться с Tomcat на Jetty, нужно исключить стартер Tomcat и
добавить Jetty:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

**Основные настройки сервера** (`application.properties`/`application.yml`):

```yaml
server:
  port: 8080                     # HTTP-порт (0 = случайный)
  address: 0.0.0.0               # Адрес, на котором слушает сервер
  servlet:
    context-path: /api           # Контекстный путь приложения
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: secret
    key-store-type: PKCS12
  compression:
    enabled: true
    min-response-size: 2KB
```

**Программная настройка.** Для глубокой настройки используется `WebServerFactoryCustomizer`:

```java
@Component
public class MyTomcatCustomizer
        implements WebServerFactoryCustomizer<TomcatServletWebServerFactory> {

    @Override
    public void customize(TomcatServletWebServerFactory factory) {
        factory.setPort(8081);
        factory.addConnectorCustomizers(connector ->
            connector.setMaxPostSize(10 * 1024 * 1024)); // 10 MB
    }
}
```

Источник: [Servlet Web Applications :: Spring Boot](https://docs.spring.io/spring-boot/reference/web/servlet.html)

---

### 4. Внешняя конфигурация

**Порядок приоритетов источников** (позднейший переопределяет более ранний):

1. Свойства по умолчанию (`SpringApplication.setDefaultProperties(...)`)
2. Аннотации `@PropertySource` на `@Configuration`-классах
3. Файлы конфигурации: `application.properties` / `application.yaml`
4. `RandomValuePropertySource` (свойства вида `random.*`)
5. Переменные окружения ОС
6. Java system properties (`-Dkey=value`)
7. JNDI-атрибуты (`java:comp/env`)
8. Параметры `ServletContext` / `ServletConfig`
9. Свойство `SPRING_APPLICATION_JSON`
10. Аргументы командной строки (`--key=value`)
11. Test-аннотации (`@SpringBootTest`, `@TestPropertySource`, `@DynamicPropertySource`)

**Загрузка файлов конфигурации** (в порядке от низшего к высшему приоритету):

1. `classpath:/application.properties`
2. `classpath:/config/application.properties`
3. `./application.properties` (текущий каталог)
4. `./config/application.properties`

Файл `.properties` имеет приоритет над `.yaml` при расположении в одном месте.

**application.properties vs application.yaml.** Обе формы эквивалентны. YAML удобнее для
вложенных структур и списков:

```yaml
# application.yaml
my:
  service:
    enabled: true
    remote-address: 192.168.1.1
    security:
      username: "admin"
      roles:
        - USER
        - ADMIN
```

```properties
# Эквивалентный application.properties
my.service.enabled=true
my.service.remote-address=192.168.1.1
my.service.security.username=admin
my.service.security.roles[0]=USER
my.service.security.roles[1]=ADMIN
```

**Профили.** Профиль активируется через `spring.profiles.active` (свойство, переменная среды,
аргумент командной строки). Профиль-специфичные файлы именуются
`application-{profile}.properties` / `application-{profile}.yaml` и переопределяют базовые
значения.

```bash
# Запуск с профилем prod
java -jar app.jar --spring.profiles.active=prod
```

```yaml
# application.yaml — базовые значения
server:
  port: 8080

---
# application-prod.yaml — переопределение для prod
server:
  port: 443
```

Источник: [Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)

---

### 5. @ConfigurationProperties

Типобезопасная привязка конфигурации к Java-объекту. Предпочтительнее `@Value` для групп
связанных настроек.

**JavaBean-стиль (mutable):**

```java
@ConfigurationProperties("my.service")
public class MyServiceProperties {
    private boolean enabled;
    private InetAddress remoteAddress;
    private final Security security = new Security();

    // геттеры и сеттеры ...

    public static class Security {
        private String username;
        private String password;
        private List<String> roles = new ArrayList<>(List.of("USER"));
        // геттеры и сеттеры ...
    }
}
```

**Constructor binding (immutable, рекомендуется):**

```java
@ConfigurationProperties("my.service")
public class MyServiceProperties {
    private final boolean enabled;
    private final InetAddress remoteAddress;

    public MyServiceProperties(boolean enabled, InetAddress remoteAddress) {
        this.enabled = enabled;
        this.remoteAddress = remoteAddress;
    }
    // геттеры ...
}
```

**Регистрация.** Два способа:

```java
// Способ 1: на уровне @Configuration-класса
@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties(MyServiceProperties.class)
public class AppConfig { }

// Способ 2: сканирование через @SpringBootApplication
@SpringBootApplication
@ConfigurationPropertiesScan("com.example")
public class MyApplication { }
```

**Relaxed binding.** Spring Boot принимает имена свойств в разных форматах:

| Формат | Пример |
|---|---|
| kebab-case (рекомендован) | `my.service.remote-address` |
| camelCase | `my.service.remoteAddress` |
| underscore_notation | `my.service.remote_address` |
| UPPER_CASE (env vars) | `MY_SERVICE_REMOTEADDRESS` |

Префикс в `@ConfigurationProperties` всегда должен быть в kebab-case.

Источник: [Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)

---

### 6. Spring Boot Actuator

Actuator добавляет набор HTTP-эндпоинтов и JMX-бинов для мониторинга и управления
production-приложением.

**Подключение:**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**Основные эндпоинты** (базовый путь `/actuator`):

| Эндпоинт | Метод | Описание |
|---|---|---|
| `health` | GET | Состояние приложения (UP / DOWN) |
| `info` | GET | Произвольная информация о приложении |
| `metrics` | GET | Имена метрик; `metrics/{name}` — конкретная метрика |
| `prometheus` | GET | Метрики в формате Prometheus |
| `env` | GET | Переменные окружения и свойства |
| `beans` | GET | Список всех Spring-бинов |
| `conditions` | GET | Отчёт об условиях автоконфигурации |
| `configprops` | GET | Все `@ConfigurationProperties` |
| `loggers` | GET/POST | Просмотр и изменение уровней логирования |
| `mappings` | GET | Все `@RequestMapping`-маппинги |
| `threaddump` | GET | Thread dump |
| `heapdump` | GET | Heap dump (только HTTP) |
| `shutdown` | POST | Graceful shutdown (по умолчанию отключён) |
| `startup` | GET | Данные о времени старта |
| `flyway` | GET | Применённые Flyway-миграции |
| `httpexchanges` | GET | Последние 100 HTTP-обменов |

По умолчанию через HTTP открыт только `health`. Остальные эндпоинты нужно явно открыть:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
        # include: "*"  # открыть все (с осторожностью)
  endpoint:
    health:
      show-details: when-authorized   # never | always | when-authorized
```

**Безопасность Actuator.** При наличии Spring Security в classpath следует явно настраивать
доступ:

```java
@Configuration(proxyBeanMethods = false)
public class ActuatorSecurityConfig {

    @Bean
    public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
        http.securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(requests -> requests
                .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                .anyRequest().hasRole("ADMIN"))
            .httpBasic(withDefaults());
        return http.build();
    }
}
```

**Кастомный HealthIndicator:**

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    private final DataSource dataSource;

    public DatabaseHealthIndicator(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            conn.isValid(1);
            return Health.up().withDetail("database", "reachable").build();
        } catch (Exception ex) {
            return Health.down(ex).build();
        }
    }
}
```

Имя компонента регистрируется как `database` (суффикс `HealthIndicator` отрезается),
эндпоинт `/actuator/health/database`.

**Health Groups (для Kubernetes-проб):**

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        liveness:
          include: livenessState
        readiness:
          include: readinessState,db
```

Источник: [Production-ready Features :: Spring Boot](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

---

### 7. Кастомная автоконфигурация и стартеры

Для переиспользуемых библиотек создают собственные starter + auto-configuration.

**Структура проекта стартера:**
- `mylib-spring-boot` — содержит классы автоконфигурации и основной код.
- `mylib-spring-boot-starter` — пустой POM, агрегирующий зависимости.

**Класс автоконфигурации:**

```java
@AutoConfiguration
@ConditionalOnClass(MyLibService.class)
@EnableConfigurationProperties(MyLibProperties.class)
public class MyLibAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyLibService myLibService(MyLibProperties props) {
        return new MyLibService(props.getApiKey());
    }
}
```

**Регистрация** в `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`:

```
com.example.mylib.autoconfigure.MyLibAutoConfiguration
```

Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

---

### 8. Тестирование Spring Boot приложений

Spring Boot предоставляет test-срезы (test slices) для изолированного тестирования слоёв:

| Аннотация | Что загружает |
|---|---|
| `@SpringBootTest` | Полный контекст приложения (интеграционные тесты) |
| `@WebMvcTest` | Только MVC-слой: контроллеры, фильтры, ExceptionHandler |
| `@WebFluxTest` | Только WebFlux-слой |
| `@DataJpaTest` | JPA-репозитории + встроенная БД |
| `@DataMongoTest` | MongoDB-репозитории |
| `@JsonTest` | Сериализация/десериализация JSON |

```java
// Полный интеграционный тест
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class OrderControllerIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldReturnOrders() {
        ResponseEntity<String> response = restTemplate.getForEntity("/orders", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }
}

// Тест только MVC-слоя
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Test
    void shouldReturn200() throws Exception {
        given(orderService.findAll()).willReturn(List.of());
        mockMvc.perform(get("/orders"))
               .andExpect(status().isOk());
    }
}
```

`@MockBean` создаёт Mockito-мок и регистрирует его в контексте Spring, заменяя реальный бин.

Источник: [Testing :: Spring Boot](https://docs.spring.io/spring-boot/reference/testing/index.html)

---

## Достоверные источники

1. **[Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/reference/index.html)** —
   официальная документация Spring Boot (актуальная версия). Первичный источник для всех
   характеристик поведения, API и конфигурационных свойств.

2. **[Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html)** —
   официальный раздел о механизме автоконфигурации: `@EnableAutoConfiguration`, отладка,
   исключение конфигураций.

3. **[Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)** —
   официальный раздел о внешней конфигурации: порядок источников, профили, `@ConfigurationProperties`,
   relaxed binding.

4. **[Production-ready Features (Actuator) :: Spring Boot](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)** —
   официальный раздел об Actuator: полный список эндпоинтов, настройка доступа, health indicators,
   Kubernetes probes.

5. **[Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)** —
   официальное руководство по созданию собственных автоконфигураций и стартеров, включая
   `@Conditional*` аннотации и `ApplicationContextRunner` для тестирования.

6. **[Baeldung — Spring Boot](https://www.baeldung.com/spring-boot)** — систематизированные
   практические статьи с примерами кода; авторитетный ресурс сообщества, статьи проходят
   редакционную проверку.
