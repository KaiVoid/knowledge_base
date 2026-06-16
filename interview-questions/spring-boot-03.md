# Spring Boot — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/14-spring-boot.md](../knowledge-base/14-spring-boot.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](spring-boot-01.md) · [ч.2](spring-boot-02.md) · **ч.3**

---
### Вопрос 41. Как создать кастомный эндпоинт Actuator с помощью @Endpoint? Какие аннотации (@ReadOperation, @WriteOperation, @DeleteOperation) соответствуют каким HTTP-методам? Как контролировать, через какой транспорт (HTTP, JMX) эндпоинт доступен, и что нужно сделать для его экспозиции?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

Если добавить `@Bean`, аннотированный `@Endpoint`, любые методы с аннотациями `@ReadOperation`, `@WriteOperation` или `@DeleteOperation` автоматически будут доступны через JMX, а в веб-приложении — также через HTTP.

Соответствие HTTP-методов:
- `@ReadOperation` → `GET`
- `@WriteOperation` → `POST`
- `@DeleteOperation` → `DELETE`

Коды ответов: если `@ReadOperation` возвращает значение — `200 OK`, если `null` — `404 Not Found`; если `@WriteOperation`/`@DeleteOperation` возвращают значение — `200 OK`, если нет — `204 No Content`; при неверных параметрах — `400 Bad Request`.

Для управления транспортом: `@WebEndpoint` экспонирует эндпоинт только через HTTP, `@JmxEndpoint` — только через JMX. Технологически-специфичные расширения регистрируются через `@EndpointWebExtension` и `@EndpointJmxExtension`. По умолчанию через HTTP доступен только `health`. Управление экспозицией:

```properties
management.endpoints.web.exposure.include=health,info,custom
```

#### Ответ от Claude

**Создание кастомного эндпоинта**

```java
@Component
@Endpoint(id = "features")
public class FeaturesEndpoint {

    private final Map<String, Boolean> features = new ConcurrentHashMap<>();

    @ReadOperation
    public Map<String, Boolean> getFeatures() {
        return features;
    }

    @ReadOperation
    public Boolean getFeature(@Selector String name) {
        return features.get(name);
        // GET /actuator/features/{name}
    }

    @WriteOperation
    public void setFeature(String name, boolean enabled) {
        features.put(name, enabled);
        // POST /actuator/features — тело запроса: {"name":"dark-mode","enabled":true}
    }

    @DeleteOperation
    public void deleteFeature(@Selector String name) {
        features.remove(name);
        // DELETE /actuator/features/{name}
    }
}
```

**Соответствие аннотаций HTTP-методам**

| Аннотация | HTTP-метод | Код при наличии значения | Код при отсутствии значения |
|---|---|---|---|
| `@ReadOperation` | GET | 200 OK | 404 Not Found |
| `@WriteOperation` | POST | 200 OK | 204 No Content |
| `@DeleteOperation` | DELETE | 200 OK | 204 No Content |

Тело для `@WriteOperation` принимается как JSON (`Content-Type: application/json`) и маппится на параметры метода. Параметры обязательны по умолчанию; для опциональности — `@Nullable` (javax/jakarta) или `Optional<T>`.

**Управление транспортом**

| Аннотация | HTTP | JMX |
|---|---|---|
| `@Endpoint` | Да | Да |
| `@WebEndpoint` | Да | Нет |
| `@JmxEndpoint` | Нет | Да |

Для добавления веб-специфичной логики к существующему эндпоинту без изменения JMX-части используется `@EndpointWebExtension`:

```java
@Component
@EndpointWebExtension(endpoint = FeaturesEndpoint.class)
public class FeaturesWebExtension {
    @ReadOperation
    public WebEndpointResponse<Map<String, Boolean>> getFeatures() {
        // Возврат с кастомным HTTP-статусом или заголовками
        return new WebEndpointResponse<>(features, 200);
    }
}
```

**Экспозиция эндпоинтов**

По умолчанию через HTTP (`/actuator/**`) доступен только `health`. Все зарегистрированные эндпоинты можно просмотреть по `/actuator`.

```properties
# Открыть конкретные эндпоинты
management.endpoints.web.exposure.include=health,info,features

# Открыть все (осторожно в production)
management.endpoints.web.exposure.include=*

# Исключить из уже открытых
management.endpoints.web.exposure.exclude=env,beans

# JMX (по умолчанию все включены)
management.endpoints.jmx.exposure.include=health,features
```

Кастомный эндпоинт по умолчанию будет доступен по пути `/actuator/{id}`, где `id` — значение из `@Endpoint(id = "...")`. Компиляция с флагом `-parameters` необходима для корректного маппинга имён параметров (Spring Boot Gradle/Maven плагины добавляют его автоматически).

---

### Вопрос 42. Как настроить graceful shutdown в Spring Boot? Какое свойство включает его, что происходит с новыми входящими запросами в период дренажа, какой таймаут задаётся, и почему при Kubernetes-деплое требуется preStop-хук со sleep?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Graceful Shutdown :: Spring Boot](https://docs.spring.io/spring-boot/reference/web/graceful-shutdown.html)

Graceful shutdown поддерживается всеми тремя встроенными веб-серверами (Jetty, Reactor Netty, Tomcat) и работает как в реактивных, так и в сервлетных приложениях. Происходит в ходе закрытия `ApplicationContext` как наиболее ранняя фаза остановки `SmartLifecycle`-бинов.

Во время graceful shutdown существующие запросы дорабатываются, новые отклоняются на сетевом уровне. Таймаут настраивается:

```properties
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=20s
```

Для немедленного останова: `server.shutdown=immediate`.

#### Ответ от Claude

**Включение graceful shutdown**

```properties
# application.properties
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=20s
```

```yaml
# application.yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: "20s"
```

Свойство `server.shutdown=graceful` включает режим дренажа для встроенного сервера. По умолчанию значение — `immediate` (мгновенный останов). Таймаут `spring.lifecycle.timeout-per-shutdown-phase` задаёт максимальное время ожидания завершения текущих запросов; по умолчанию — `30s`.

**Что происходит с запросами в период дренажа**

- Уже обрабатываемые запросы продолжают выполняться до завершения.
- Новые входящие соединения отклоняются на сетевом уровне (TCP-уровень, до HTTP): сервер перестаёт принимать новые соединения.
- По истечении таймаута оставшиеся незавершённые запросы прерываются принудительно, и процесс завершается.

Поведение у серверов несколько различается: Tomcat, Netty и Jetty перестают принимать новые соединения; Undertow (не встроен по умолчанию) продолжает принимать соединения, но немедленно отвечает `503 Service Unavailable`.

**Почему в Kubernetes нужен preStop-хук со sleep**

В Kubernetes при удалении пода два независимых процесса запускаются **параллельно**:

1. `kubelet` отправляет `SIGTERM` в контейнер (и до этого выполняет `preStop`-хук).
2. Плоскость управления удаляет под из `EndpointSlice` объектов (снимает его из балансировки сервисов).

Проблема состоит в том, что удаление из `EndpointSlice` — распределённая операция: `kube-proxy` на каждой ноде должен обновить правила `iptables`/`ipvs`, а это занимает несколько секунд. Если `SIGTERM` будет отправлен немедленно, приложение начнёт отклонять новые запросы (или завершится), а трафик продолжит приходить, потому что правила маршрутизации ещё не обновились. Результат — ошибки соединения у клиентов.

**Решение:** `preStop`-хук со `sleep` задерживает отправку `SIGTERM` на время, достаточное для распространения обновлений маршрутизации:

```yaml
# deployment.yaml
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: app
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
          # Или с Kubernetes >= 1.29 (Sleep action в GA с 1.30):
          # preStop:
          #   sleep:
          #     seconds: 15
```

`terminationGracePeriodSeconds` должен быть больше `preStop sleep` + `spring.lifecycle.timeout-per-shutdown-phase`, иначе Kubernetes убьёт под (`SIGKILL`) до того, как запросы завершатся.

**Итоговая временная шкала:**

```
t=0   Kubernetes решает завершить под
t=0   preStop-хук запущен (sleep 15s)
t=0   Плоскость управления начинает удалять под из EndpointSlice
t=5   kube-proxy обновил правила — новый трафик перестаёт приходить
t=15  preStop завершён → SIGTERM отправлен в контейнер
t=15  Spring Boot начинает graceful shutdown (дренаж до 20s)
t=35  Все запросы завершены, процесс вышел
t=60  terminationGracePeriodSeconds истёк (SIGKILL не понадобился)
```

Без `preStop sleep` `SIGTERM` приходит на `t=0`, и трафик продолжает поступать ещё несколько секунд — именно в тот момент, когда приложение уже не принимает новых запросов.
### Вопрос 43. Что такое health groups в Spring Boot Actuator? Как настроить группы liveness и readiness для Kubernetes-проб (/actuator/health/liveness и /actuator/health/readiness) и почему liveness не должен включать проверки внешних зависимостей?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

**Health Groups** позволяют объединить индикаторы здоровья в именованные группы. Каждая группа доступна по адресу `/actuator/health/<group-name>`. Состав группы задаётся через `include` / `exclude`:

```properties
management.endpoint.health.group.custom.include=db
```

Spring Boot автоматически создаёт две специальные группы для Kubernetes:
- `/actuator/health/liveness` — управляется `LivenessStateHealthIndicator`
- `/actuator/health/readiness` — управляется `ReadinessStateHealthIndicator`

По умолчанию группы активируются автоматически при запуске в Kubernetes. Чтобы включить их в любой среде:

```properties
management.endpoint.health.probes.enabled=true
```

Пример конфигурации Kubernetes-проб:

```yaml
livenessProbe:
  httpGet:
    path: "/actuator/health/liveness"
    port: 8080
  failureThreshold: 3
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: "/actuator/health/readiness"
    port: 8080
  failureThreshold: 3
  periodSeconds: 10
```

**Liveness vs. Readiness:**

- **Liveness** отвечает на вопрос «жив ли процесс?». При сбое Kubernetes перезапускает под. Именно поэтому liveness НЕ должен проверять внешние зависимости: если база данных недоступна и liveness вернёт DOWN, Kubernetes начнёт перезапускать все поды приложения, что создаст каскадный сбой вместо решения проблемы.
- **Readiness** отвечает на вопрос «может ли экземпляр принимать трафик?». При сбое Kubernetes убирает под из балансировщика, но не перезапускает его. Здесь внешние зависимости подключаются осторожно и только при необходимости.

Жизненный цикл состояний приложения:

| Фаза | LivenessState | ReadinessState |
|------|---------------|----------------|
| Запуск | `BROKEN` | `REFUSING_TRAFFIC` |
| Контекст загружен | `CORRECT` | `REFUSING_TRAFFIC` |
| Готово к работе | `CORRECT` | `ACCEPTING_TRAFFIC` |
| Graceful shutdown | `CORRECT` | `REFUSING_TRAFFIC` |

#### Ответ от Claude

**Health groups** — механизм Spring Boot Actuator, позволяющий сгруппировать произвольный набор `HealthIndicator`-ов под одним именованным эндпоинтом `/actuator/health/<group>`. Группа возвращает агрегированный статус (UP/DOWN/OUT_OF_SERVICE) на основе входящих в неё индикаторов.

**Встроенные группы для Kubernetes**

Spring Boot регистрирует две специальные группы автоматически при обнаружении Kubernetes-окружения (переменные `KUBERNETES_SERVICE_HOST` / `KUBERNETES_SERVICE_PORT`). Принудительно включить в любой среде:

```properties
management.endpoint.health.probes.enabled=true
```

Настройка состава групп:

```yaml
management:
  endpoint:
    health:
      group:
        liveness:
          include: "livenessState"          # только внутреннее состояние приложения
        readiness:
          include: "readinessState,db"      # можно добавить внешние проверки
```

**Экспозиция на основном порту** (когда management-порт отличается):

```properties
management.endpoint.health.probes.add-additional-paths=true
```

Создаёт `/livez` и `/readyz` на основном порту сервера.

**Почему liveness не должен включать проверки внешних зависимостей**

Liveness-проба используется Kubernetes для принятия решения о перезапуске пода. Если в liveness включить проверку базы данных или любого внешнего сервиса, то при их недоступности:

1. Liveness вернёт DOWN для всех экземпляров одновременно.
2. Kubernetes начнёт перезапускать все поды.
3. После перезапуска поды снова не могут подключиться к той же недоступной БД.
4. Возникает каскадный сбой (thundering herd) — все инстансы бесконечно перезапускаются.

При этом сам процесс приложения жив и здоров — проблема во внешней системе, а не в приложении. Kubernetes не может «починить» базу данных перезапуском подов.

**Readiness** безопаснее: при DOWN под просто выводится из балансировщика нагрузки. Как только внешняя зависимость восстановится, readiness вернёт UP, и под снова получит трафик — без перезапуска.

**Итоговые правила:**
- `liveness` = только `livenessState` (и опционально сугубо внутренние проверки, не зависящие от внешних систем).
- `readiness` = `readinessState` + внешние проверки, которые реально блокируют обработку запросов (например, БД без которой приложение не может работать вообще). Использовать осторожно.

---

### Вопрос 44. Что такое @WebMvcTest, @DataJpaTest и @SpringBootTest и чем они принципиально отличаются друг от друга с точки зрения загружаемого контекста и срабатывания автоконфигурации? Когда используется каждый из них?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Testing Spring Boot Applications :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)

**@SpringBootTest** — аналог стандартного `@ContextConfiguration`, но использующий `SpringApplication` для создания контекста. Загружает полный `ApplicationContext` со всеми компонентами и автоконфигурацией. Параметр `webEnvironment` управляет тем, запускается ли реальный сервер:
- `MOCK` (по умолчанию) — mock-среда, реальный сервер не стартует.
- `RANDOM_PORT` / `DEFINED_PORT` — реальный embedded-сервер.
- `NONE` — без web-окружения.

**@WebMvcTest** — «срез» (slice) для тестирования слоя MVC. Загружает только web-инфраструктуру Spring MVC и ограниченный набор бинов: `@Controller`, `@ControllerAdvice`, `@JsonComponent`, `Converter`, `GenericConverter`, `Filter`, `WebMvcConfigurer`, `HandlerMethodArgumentResolver`. Обычные `@Component`-бины не загружаются. Зависимости контроллера необходимо мокировать через `@MockitoBean`.

Автоматически конфигурирует `MockMvc` (и `MockMvcTester` начиная с Spring Boot 3.4).

**@DataJpaTest** — «срез» для тестирования JPA-слоя. Сканирует `@Entity`-классы, конфигурирует Spring Data JPA репозитории, настраивает встроенную базу данных (если доступна H2/HSQL/Derby). Обычные `@Component`-бины не загружаются. Транзакции по умолчанию откатываются после каждого теста. Предоставляет `TestEntityManager`.

**Принципиальные различия:**

| | @SpringBootTest | @WebMvcTest | @DataJpaTest |
|-|-----------------|-------------|--------------|
| Контекст | Полный | Только web-слой | Только JPA-слой |
| Автоконфигурация | Вся | Только MVC | Только JPA/DataSource |
| @Component | Загружаются | Не загружаются | Не загружаются |
| Скорость | Медленно | Быстро | Быстро |
| Embedded server | Опционально | Нет | Нет |

#### Ответ от Claude

Все три аннотации создают Spring `ApplicationContext` для тестов, но с принципиально разным составом и разной областью применения.

**@SpringBootTest**

Создаёт полный контекст приложения, аналогичный продакшн-запуску: срабатывает вся цепочка автоконфигурации, сканируются все `@Component`/`@Service`/`@Repository`/`@Controller`, поднимаются реальные соединения с БД и т.д. Используется для сквозных интеграционных тестов.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OrderIntegrationTest {
    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createOrder_shouldReturn201() { ... }
}
```

Минус — медленный старт: для каждого уникального набора настроек Spring создаёт отдельный контекст.

**@WebMvcTest**

«Срез» web-слоя. Spring Boot применяет только автоконфигурации, связанные с MVC: `WebMvcAutoConfiguration`, `SecurityAutoConfiguration` (если Spring Security в classpath), `MockMvcAutoConfiguration` и т.п. Контроллеры загружаются, но их зависимости (сервисы, репозитории) — нет. Все зависимости нужно подменять моками.

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserService userService;

    @Test
    void getUser_shouldReturn200() throws Exception {
        given(userService.findById(1L)).willReturn(new User(1L, "Alice"));
        mockMvc.perform(get("/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

Применяется для изолированного тестирования логики контроллеров: маппинги, валидация входных данных, сериализация/десериализация JSON, обработка ошибок.

**@DataJpaTest**

«Срез» JPA-слоя. Активируются только автоконфигурации, необходимые для работы с базой данных: `DataSourceAutoConfiguration`, `HibernateJpaAutoConfiguration`, `JpaRepositoriesAutoConfiguration`. Если в classpath есть встроенная БД (H2), она используется автоматически. Каждый тест выполняется в транзакции, которая откатывается по завершении.

```java
@DataJpaTest
class UserRepositoryTest {
    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_shouldReturnUser() {
        entityManager.persistAndFlush(new User("alice@example.com"));
        Optional<User> result = userRepository.findByEmail("alice@example.com");
        assertThat(result).isPresent();
    }
}
```

Применяется для тестирования JPA-запросов, работы репозиториев, маппинга сущностей и поведения при откате транзакций.

**Когда что выбрать:**
- `@WebMvcTest` — тест одного контроллера или нескольких контроллеров с изоляцией от сервисного и data-слоёв.
- `@DataJpaTest` — тест репозитория, кастомных JPQL/Native-запросов, жизненного цикла сущностей.
- `@SpringBootTest` — тест сценария, пересекающего несколько слоёв (controller → service → repository → DB), или тест, требующий полного контекста (например, Kafka consumer + DB в связке).

Совмещать несколько `@...Test`-аннотаций на одном тест-классе нельзя.

---

### Вопрос 45. Что такое ApplicationContextRunner и для чего его используют при написании тестов для кастомных стартеров? Как с его помощью проверить, что автоконфигурация создаёт нужный бин, что пользовательский бин подавляет автоконфигурацию и что без нужного класса в classpath конфигурация не применяется?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

`ApplicationContextRunner` — утилита для тестирования автоконфигураций. Обычно объявляется как поле тест-класса с базовой конфигурацией:

```java
private final ApplicationContextRunner contextRunner = new ApplicationContextRunner()
    .withConfiguration(AutoConfigurations.of(MyServiceAutoConfiguration.class));
```

**Проверка создания бина:**

```java
@Test
void autoConfigurationCreatesBean() {
    this.contextRunner.run((context) -> {
        assertThat(context).hasSingleBean(MyService.class);
    });
}
```

**Проверка, что пользовательский бин подавляет автоконфигурацию:**

```java
@Test
void defaultServiceBacksOff() {
    this.contextRunner.withUserConfiguration(UserConfiguration.class).run((context) -> {
        assertThat(context).hasSingleBean(MyService.class);
        assertThat(context).getBean("myCustomService")
            .isSameAs(context.getBean(MyService.class));
    });
}

@Configuration(proxyBeanMethods = false)
static class UserConfiguration {
    @Bean
    MyService myCustomService() {
        return new MyService("mine");
    }
}
```

**Проверка отсутствия конфигурации при отсутствии класса в classpath:**

```java
@Test
void serviceIsIgnoredIfLibraryIsNotPresent() {
    this.contextRunner
        .withClassLoader(new FilteredClassLoader(MyService.class))
        .run((context) -> assertThat(context).doesNotHaveBean("myService"));
}
```

Для Web-специфичной автоконфигурации используются `WebApplicationContextRunner` (Servlet) и `ReactiveWebApplicationContextRunner` (Reactive). Для отладки условий применения конфигурации подключается:

```java
.withInitializer(ConditionEvaluationReportLoggingListener.forLogLevel(LogLevel.INFO))
```

#### Ответ от Claude

**Что такое ApplicationContextRunner**

`ApplicationContextRunner` — тест-утилита Spring Boot (пакет `org.springframework.boot.test.context`), которая позволяет создавать изолированные `ApplicationContext`-ы без запуска полного Spring Boot-приложения. Это легковесная альтернатива `@SpringBootTest` для сценариев, где нужно проверить только работу автоконфигурации кастомного стартера в различных условиях.

Ключевое отличие от `@SpringBootTest`: `ApplicationContextRunner` не сканирует classpath автоматически — разработчик явно указывает, какие автоконфигурации должны быть применены. Это делает тесты быстрыми, детерминированными и независимыми от состава всего приложения.

**Базовая структура**

Типичный паттерн — объявить runner как поле класса с базовой конфигурацией, а затем дополнять её в каждом тесте:

```java
class MyAutoConfigurationTest {

    private final ApplicationContextRunner contextRunner = new ApplicationContextRunner()
        .withConfiguration(AutoConfigurations.of(MyServiceAutoConfiguration.class));
}
```

**Сценарий 1: автоконфигурация создаёт нужный бин**

Проверяет базовое поведение — что при наличии всех условий бин регистрируется:

```java
@Test
void shouldCreateMyServiceBeanByDefault() {
    contextRunner.run(context -> {
        assertThat(context).hasSingleBean(MyService.class);
        assertThat(context.getBean(MyService.class).getName())
            .isEqualTo("default-name");
    });
}
```

Метод `hasSingleBean` проверяет, что бин ровно один (не ноль, не два). Это важно: если автоконфигурация случайно создаёт несколько экземпляров, тест это поймает.

**Сценарий 2: пользовательский бин подавляет автоконфигурацию**

Классический паттерн `@ConditionalOnMissingBean` в автоконфигурации означает, что если пользователь уже объявил бин того же типа, автоконфигурация должна отступить. Это проверяется через `withUserConfiguration`:

```java
@Test
void userDefinedBeanSuppressesAutoConfiguration() {
    contextRunner
        .withUserConfiguration(CustomServiceConfiguration.class)
        .run(context -> {
            // Бин ровно один — пользовательский, не авто
            assertThat(context).hasSingleBean(MyService.class);
            // Это именно пользовательский бин
            assertThat(context.getBean(MyService.class).getName())
                .isEqualTo("custom");
        });
}

@Configuration(proxyBeanMethods = false)
static class CustomServiceConfiguration {
    @Bean
    MyService myService() {
        return new MyService("custom");
    }
}
```

Если автоконфигурация не использует `@ConditionalOnMissingBean`, в контексте окажется два бина и `hasSingleBean` провалится.

**Сценарий 3: конфигурация не применяется без нужного класса в classpath**

Когда автоконфигурация помечена `@ConditionalOnClass(SomeLibraryClass.class)`, при отсутствии библиотеки она не должна активироваться. `FilteredClassLoader` симулирует отсутствие класса в classpath:

```java
@Test
void shouldNotCreateBeanWhenLibraryIsAbsent() {
    contextRunner
        .withClassLoader(new FilteredClassLoader(MyService.class))
        .run(context -> {
            assertThat(context).doesNotHaveBean(MyService.class);
        });
}
```

`FilteredClassLoader` принимает классы или пакеты, которые нужно «скрыть». При загрузке такого класса будет выброшен `ClassNotFoundException`, что отключит соответствующую `@ConditionalOnClass`-конфигурацию.

**Дополнительные возможности**

Проверка свойств конфигурации:

```java
@Test
void serviceNameCanBeOverriddenByProperty() {
    contextRunner
        .withPropertyValues("myservice.name=overridden")
        .run(context -> {
            assertThat(context.getBean(MyService.class).getName())
                .isEqualTo("overridden");
        });
}
```

Проверка провала контекста (например, конфликт бинов):

```java
@Test
void contextFailsOnMisconfiguration() {
    contextRunner
        .withUserConfiguration(BadConfiguration.class)
        .run(context -> {
            assertThat(context).hasFailed();
            assertThat(context.getStartupFailure())
                .hasMessageContaining("expected message");
        });
}
```

**Web-специализации**

Для автоконфигураций, использующих `@ConditionalOnWebApplication`:
- `WebApplicationContextRunner` — для Servlet-based приложений.
- `ReactiveWebApplicationContextRunner` — для Reactive.

**Отладка условий**

Для диагностики, почему условная конфигурация не применилась:

```java
contextRunner
    .withInitializer(
        ConditionEvaluationReportLoggingListener.forLogLevel(LogLevel.INFO)
    )
    .run(context -> { ... });
```

**Важное ограничение:** `ApplicationContextRunner` не работает в GraalVM native image, поскольку опирается на runtime-рефлексию для построения контекста. Тесты стартеров для native-режима требуют отдельного подхода.

---
### Вопрос 46. Что такое spring.config.import (появился в Spring Boot 2.4)? Какие типы источников он поддерживает (файлы, configtree, optional:)? Как с помощью configtree: прочитать секреты, смонтированные Kubernetes как volume, без переменных окружения?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Config file processing in Spring Boot 2.4](https://spring.io/blog/2020/08/14/config-file-processing-in-spring-boot-2-4/)

В Spring Boot 2.4 появилось свойство `spring.config.import`, которое позволяет подключать дополнительные источники конфигурации непосредственно из `application.properties` или `application.yml`. До версии 2.4 импорт внешних файлов конфигурации был затруднён.

**Поддерживаемые типы источников:**

- **Обычные файлы и директории** — без префикса, указывается путь к `.properties` или `.yaml`-файлу.
- **Конфигурационные деревья (`configtree:`)** — сообщает Spring Boot, что по указанному пути находится иерархия директорий в стиле Kubernetes, где имя файла становится ключом свойства, а содержимое файла — его значением.

Строки расположения полностью расширяемы: сторонние библиотеки смогут в будущем добавлять свои префиксы, например `vault://` или `zookeeper://`.

**Работа `configtree:` с Kubernetes:**

Kubernetes монтирует `ConfigMap` и `Secret` как файловую иерархию. Например, если смонтировать секрет по пути `/etc/config/`, файловая структура будет такой:

```
/etc/config/
  myapp/
    username   <- содержит "admin"
    password   <- содержит "s3cr3t"
```

Настройка:
```properties
spring.config.import=configtree:/etc/config/
```

Spring Boot превратит эту структуру в свойства `myapp.username=admin` и `myapp.password=s3cr3t`, доступные через `Environment` как обычные свойства.

#### Ответ от Claude

**Что такое `spring.config.import`**

Начиная со Spring Boot 2.4, свойство `spring.config.import` позволяет объявлять дополнительные источники конфигурации прямо внутри `application.properties` / `application.yml`. Импортированные файлы обрабатываются в момент обнаружения и вставляются как дополнительные документы сразу после документа, содержащего директиву `import`. Каждый источник импортируется ровно один раз, независимо от количества объявлений.

**Поддерживаемые типы источников**

| Тип | Пример | Описание |
|-----|--------|----------|
| Файл properties/yaml | `file:/etc/app/extra.properties` | Стандартный файл конфигурации |
| Относительный путь | `config/core.properties` | Путь относительно объявляющего файла |
| Конфигурационное дерево | `configtree:/etc/config/` | Иерархия директорий (ключ = имя файла, значение = содержимое) |
| Опциональный источник | `optional:file:./dev.properties` | Не выбрасывает ошибку, если источник отсутствует |

**Префикс `optional:`**

По умолчанию Spring Boot выбрасывает `ConfigDataLocationNotFoundException`, если указанный источник не найден. Чтобы приложение стартовало даже при отсутствии источника, используется префикс `optional:`:

```properties
spring.config.import=optional:configtree:/etc/secrets/
```

**Префикс `configtree:` и чтение секретов Kubernetes**

Kubernetes при монтировании `Secret` как volume создаёт файловую иерархию: каждый ключ секрета становится именем файла, значение — содержимым. Spring Boot c `configtree:` читает эту иерархию и превращает её в свойства окружения без использования переменных окружения (`env`).

Пример монтирования секрета в `pod.yaml`:
```yaml
volumes:
  - name: db-secret
    secret:
      secretName: db-credentials
volumeMounts:
  - name: db-secret
    mountPath: /run/secrets/db
    readOnly: true
```

Структура файлов после монтирования:
```
/run/secrets/db/
  username   <- "dbuser"
  password   <- "Passw0rd!"
```

Конфигурация Spring Boot:
```properties
spring.config.import=optional:configtree:/run/secrets/db/
```

Результат — свойства `username=dbuser` и `password=Passw0rd!` доступны через `@Value("${username}")` или `@ConfigurationProperties`.

**Wildcards**

Для импорта сразу нескольких деревьев одного уровня поддерживается подстановка `*/`:
```properties
spring.config.import=optional:configtree:/run/secrets/*/
```

Это позволяет монтировать несколько Kubernetes-секретов в разные поддиректории и читать их единой директивой.

**Ключевые отличия от переменных окружения:**
- Секреты не попадают в список `env` процесса, что снижает риск случайного логирования.
- Значения могут содержать спецсимволы, переносы строк, бинарные данные.
- Нет ограничений на размер, характерных для переменных окружения.

---

### Вопрос 47. Как наполнить эндпоинт /actuator/info содержательными данными? Какие встроенные InfoContributor существуют (git, build, env, Java), как сгенерировать build-info.properties и git.properties с помощью плагинов сборки и какие свойства нужно включить?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Production-ready Features — Application Information :: Spring Boot 3.2](https://docs.spring.io/spring-boot/docs/3.2.0/reference/html/actuator.html#actuator.application-information)

Эндпоинт `/actuator/info` собирает данные от всех бинов `InfoContributor`, зарегистрированных в `ApplicationContext`. Spring Boot предоставляет несколько авто-сконфигурированных контрибьюторов:

| ID | Класс | Описание | Требования | Включён по умолчанию |
|----|-------|----------|------------|----------------------|
| `build` | `BuildInfoContributor` | Данные сборки | Файл `META-INF/build-info.properties` | Да |
| `git` | `GitInfoContributor` | Git-информация | Файл `git.properties` | Да |
| `env` | `EnvironmentInfoContributor` | Свойства с префиксом `info.` | — | Нет |
| `java` | `JavaInfoContributor` | JVM-информация | — | Нет |
| `os` | `OsInfoContributor` | ОС-информация | — | Нет |

Включение/отключение контрибьюторов через свойства:
```properties
management.info.env.enabled=true
management.info.java.enabled=true
management.info.git.mode=full   # simple (по умолчанию) или full
```

Режимы `git.mode`:
- `simple` — показывает только `git.branch`, `git.commit.id`, `git.commit.time`
- `full` — выводит полное содержимое `git.properties`

#### Ответ от Claude

**Встроенные InfoContributor и управление ими**

Spring Boot Actuator предоставляет следующие авто-сконфигурированные контрибьюторы для `/actuator/info`:

| ID | Включён по умолчанию | Что показывает |
|----|----------------------|---------------|
| `build` | Да (при наличии файла) | Артефакт, версия, время сборки |
| `git` | Да (при наличии файла) | Ветка, commit id, время коммита |
| `env` | Нет | Свойства с префиксом `info.*` |
| `java` | Нет | Версия JVM, вендор, runtime |
| `os` | Нет | Имя ОС, версия, архитектура |

Управление через `application.properties`:
```properties
# Включить env-контрибьютор
management.info.env.enabled=true
# Включить java-контрибьютор
management.info.java.enabled=true
# Отключить все включённые по умолчанию
management.info.defaults.enabled=false
# Режим git: simple (по умолчанию) или full
management.info.git.mode=full
```

**Статические свойства через `env`-контрибьютор**

Когда `env`-контрибьютор включён, все свойства с префиксом `info.` публикуются в `/actuator/info`:
```properties
info.app.name=My Service
info.app.version=2.1.0
info.app.description=Backend API
# Расширение через Maven-переменные:
info.app.encoding=@project.build.sourceEncoding@
```

**Генерация `build-info.properties` (Maven)**

Добавить цель `build-info` в `spring-boot-maven-plugin`:
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals>
                <goal>build-info</goal>
            </goals>
            <configuration>
                <additionalProperties>
                    <encoding.source>UTF-8</encoding.source>
                    <java.version>${java.version}</java.version>
                </additionalProperties>
            </configuration>
        </execution>
    </executions>
</plugin>
```

Плагин создаёт `META-INF/build-info.properties` со свойствами: `build.group`, `build.artifact`, `build.name`, `build.version`, `build.time`. Дополнительные свойства получают префикс `build.`.

**Генерация `build-info.properties` (Gradle)**

В `build.gradle` / `build.gradle.kts`:
```groovy
// Groovy DSL
springBoot {
    buildInfo()
}
```
```kotlin
// Kotlin DSL
springBoot {
    buildInfo()
}
```

Задача `bootBuildInfo` запускается автоматически перед компиляцией и создаёт `META-INF/build-info.properties` в `build/resources/main`. Чтобы сборка была воспроизводимой, рекомендуется исключить нестабильное свойство `time`:
```groovy
springBoot {
    buildInfo {
        excludes = ['time']
    }
}
```

**Генерация `git.properties` (Maven)**

Используется плагин `git-commit-id-maven-plugin`:
```xml
<plugin>
    <groupId>pl.project13.maven</groupId>
    <artifactId>git-commit-id-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals><goal>revision</goal></goals>
        </execution>
    </executions>
    <configuration>
        <generateGitPropertiesFile>true</generateGitPropertiesFile>
        <generateGitPropertiesFilename>
            ${project.build.outputDirectory}/git.properties
        </generateGitPropertiesFilename>
    </configuration>
</plugin>
```

**Генерация `git.properties` (Gradle)**

Используется плагин `com.gorylenko.gradle-git-properties`:
```groovy
plugins {
    id 'com.gorylenko.gradle-git-properties' version '2.4.1'
}
```

**Пользовательский InfoContributor**

Для добавления произвольных данных нужно зарегистрировать бин, реализующий `InfoContributor`:
```java
@Component
public class CustomInfoContributor implements InfoContributor {
    @Override
    public void contribute(Info.Builder builder) {
        builder.withDetail("custom", Map.of("status", "active"));
    }
}
```

**Важно:** Начиная со Spring Boot 3.x эндпоинт `/actuator/info` по умолчанию не экспонируется по HTTP (только по JMX). Для HTTP-доступа необходимо:
```properties
management.endpoints.web.exposure.include=info,health
```

---

### Вопрос 48. Что произошло с форматом файла spring.factories начиная с Spring Boot 2.7 и в Spring Boot 3.x? Какие ключи остались в spring.factories (например, FailureAnalyzer, EnvironmentPostProcessor, ApplicationListener), а что обязательно перенесено в AutoConfiguration.imports?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Spring Boot 3.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)

В Spring Boot 3.0 поддержка регистрации авто-конфигураций через `spring.factories` с ключом `org.springframework.boot.autoconfigure.EnableAutoConfiguration` была удалена в пользу нового файла. Все остальные ключи в `spring.factories` остались без изменений.

Процитируем Migration Guide:

> "Support for registering auto-configurations in `spring.factories` using the `org.springframework.boot.autoconfigure.EnableAutoConfiguration` key has been removed. Other entries in `spring.factories` under other keys are unaffected."

Для библиотек, поддерживающих одновременно Spring Boot 2.x и 3.x, авто-конфигурации можно перечислять как в `spring.factories`, так и в новом файле `AutoConfiguration.imports` — Spring Boot 2.7 дедуплицирует записи.

#### Ответ от Claude

**История изменений**

**Spring Boot до 2.7** — авто-конфигурации регистрировались в `META-INF/spring.factories` под ключом `org.springframework.boot.autoconfigure.EnableAutoConfiguration`:
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.MyAutoConfiguration,\
  com.example.AnotherAutoConfiguration
```

**Spring Boot 2.7** — введён новый механизм (deprecation старого):
- Появился файл `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
- Каждая строка — полное имя авто-конфигурационного класса
- Старый `spring.factories` ещё работает для обратной совместимости, но выдаёт предупреждение
- Введена аннотация `@AutoConfiguration` взамен `@Configuration` для верхнеуровневых авто-конфигураций

Формат нового файла:
```
# META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.mycorp.libx.autoconfigure.LibXAutoConfiguration
com.mycorp.libx.autoconfigure.LibXWebAutoConfiguration
```

**Spring Boot 3.0** — поддержка `EnableAutoConfiguration` в `spring.factories` полностью удалена. Авто-конфигурации работают исключительно через `AutoConfiguration.imports`.

**Что осталось в `spring.factories`**

Следующие ключи в `spring.factories` продолжают работать во всех версиях Spring Boot (включая 3.x):

| Ключ | Назначение |
|------|-----------|
| `org.springframework.boot.diagnostics.FailureAnalyzer` | Пользовательский анализатор ошибок при старте |
| `org.springframework.boot.env.EnvironmentPostProcessor` | Настройка `Environment` до обновления контекста |
| `org.springframework.context.ApplicationListener` | Слушатели событий, загружаемые до создания `ApplicationContext` |
| `org.springframework.boot.SpringApplicationRunListener` | Слушатели жизненного цикла `SpringApplication` |
| `org.springframework.boot.autoconfigure.AutoConfigurationImportFilter` | Фильтры импорта авто-конфигураций |

Пример регистрации `FailureAnalyzer` — в Spring Boot 3.x остаётся через `spring.factories`:
```properties
# META-INF/spring.factories
org.springframework.boot.diagnostics.FailureAnalyzer=\
  com.example.ProjectConstraintViolationFailureAnalyzer
```

Пример регистрации `EnvironmentPostProcessor`:
```properties
# META-INF/spring.factories
org.springframework.boot.env.EnvironmentPostProcessor=\
  com.example.MyEnvironmentPostProcessor
```

**Почему эти ключи остались в `spring.factories`**

`FailureAnalyzer`, `EnvironmentPostProcessor` и `ApplicationListener` должны быть доступны ещё до того, как `ApplicationContext` будет создан. Механизм `AutoConfiguration.imports` работает уже внутри жизненного цикла контекста, поэтому для bootstrap-компонентов `spring.factories` остаётся единственным вариантом.

**Что обязательно перенесено в `AutoConfiguration.imports`**

Только авто-конфигурации (классы, аннотированные `@AutoConfiguration` или `@Configuration` + условные аннотации), регистрировавшиеся ранее под ключом `EnableAutoConfiguration`.

**Стратегия для библиотек с поддержкой нескольких версий**

Чтобы поддерживать Spring Boot 2.6, 2.7 и 3.x одновременно:
1. Перечислить авто-конфигурации в обоих файлах.
2. Spring Boot 2.7+ дедуплицирует записи автоматически.
3. Spring Boot 3.x прочитает только `AutoConfiguration.imports` и проигнорирует `EnableAutoConfiguration`-ключ в `spring.factories`.

```
# Для поддержки Spring Boot < 2.7:
META-INF/spring.factories
  org.springframework.boot.autoconfigure.EnableAutoConfiguration=com.example.MyAutoConfiguration

# Для поддержки Spring Boot >= 2.7:
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
  com.example.MyAutoConfiguration
```

---
### Вопрос 49. Что такое EnvironmentPostProcessor в Spring Boot? Когда он вызывается относительно AutoConfiguration, как его зарегистрировать и для каких задач он используется (например, загрузка секретов из внешнего хранилища до старта контекста)?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How-to Guides — Customize the Environment (docs.spring.io)](https://docs.spring.io/spring-boot/how-to/application.html)

`EnvironmentPostProcessor` позволяет настраивать `Environment` приложения **до обновления (refresh) контекста приложения**. Это важно для свойств вроде `logging.*` и `spring.main.*`, которые считываются раньше, чем происходит refresh.

Чтобы создать собственный `EnvironmentPostProcessor`, нужно реализовать интерфейс и переопределить метод `postProcessEnvironment`:

```java
public class MyEnvironmentPostProcessor implements EnvironmentPostProcessor {

    private final YamlPropertySourceLoader loader = new YamlPropertySourceLoader();

    @Override
    public void postProcessEnvironment(ConfigurableEnvironment environment,
                                       SpringApplication application) {
        Resource path = new ClassPathResource("com/example/myapp/config.yml");
        PropertySource<?> propertySource = loadYaml(path);
        environment.getPropertySources().addLast(propertySource);
    }

    private PropertySource<?> loadYaml(Resource path) {
        Assert.isTrue(path.exists(), () -> "'path' [%s] must exist".formatted(path));
        try {
            return this.loader.load("custom-resource", path).get(0);
        } catch (IOException ex) {
            throw new IllegalStateException(
                "Failed to load yaml configuration from " + path, ex);
        }
    }
}
```

Реализацию необходимо зарегистрировать в `META-INF/spring.factories`:

```properties
org.springframework.boot.EnvironmentPostProcessor=com.example.MyEnvironmentPostProcessor
```

При добавлении источника через `addLast` он получает **наименьший приоритет** (уступает стандартным источникам). Для добавления с наивысшим приоритетом используется `addFirst`.

#### Ответ от Claude

**Что такое EnvironmentPostProcessor**

`EnvironmentPostProcessor` — функциональный интерфейс Spring Boot (пакет `org.springframework.boot.env`), появившийся в версии 1.3.0. Его единственный метод:

```java
void postProcessEnvironment(ConfigurableEnvironment environment, SpringApplication application);
```

Интерфейс позволяет программно изменять `ConfigurableEnvironment` — добавлять, удалять и переупорядочивать `PropertySource`-ы — до того, как Spring создаст и обновит (`refresh`) `ApplicationContext`.

**Момент вызова относительно AutoConfiguration**

Последовательность старта Spring Boot выглядит так:

1. `ApplicationStartingEvent` — регистрация слушателей.
2. **`ApplicationEnvironmentPreparedEvent`** — `Environment` подготовлен, контекст ещё не создан. Именно в этот момент вызываются все зарегистрированные `EnvironmentPostProcessor`-ы.
3. `ApplicationContextInitializedEvent` — контекст создан, вызваны `ApplicationContextInitializer`-ы.
4. `ApplicationPreparedEvent` — bean-определения загружены, до refresh.
5. Refresh контекста — именно здесь применяется **AutoConfiguration**.

Вывод: `EnvironmentPostProcessor` вызывается **до** применения AutoConfiguration и до создания любых бинов. Это гарантирует, что свойства, добавленные постпроцессором, будут доступны аннотациям `@ConditionalOnProperty`, `@Value` и прочим механизмам AutoConfiguration.

**Регистрация**

В Spring Boot 2.x/3.x регистрация выполняется через `META-INF/spring.factories`:

```properties
org.springframework.boot.env.EnvironmentPostProcessor=\
  com.example.SecretsManagerEnvironmentPostProcessor
```

Файл размещается в `src/main/resources/META-INF/spring.factories`. Можно регистрировать несколько реализаций через запятую или с продолжением строки (`\`).

**Упорядочивание**

Несколько постпроцессоров упорядочиваются через `Ordered` или `@Order`. Spring Boot использует это внутри: например, `ConfigDataEnvironmentPostProcessor` (загружает `application.properties`/`application.yml`) выполняется раньше пользовательских постпроцессоров с нейтральным приоритетом. Чтобы вставить свой постпроцессор **после** загрузки конфигурационных файлов, нужно задать приоритет ниже, чем у `ConfigDataEnvironmentPostProcessor` (его значение `Ordered.HIGHEST_PRECEDENCE + 10`).

**Дополнительные параметры конструктора (с версии 2.4)**

С Spring Boot 2.4 конструктор реализации может принимать:
- `DeferredLogFactory` — логгер с отложенным выводом (чтобы уровни логирования из `Environment` применились корректно до первого лог-сообщения).
- `ConfigurableBootstrapContext` (или `BootstrapContext`, `BootstrapRegistry`) — хранилище объектов, дорогих в создании (например, HTTP-клиент к Vault), которые нужно разделить между несколькими постпроцессорами.

**Типичные сценарии использования**

1. **Загрузка секретов из внешнего хранилища до старта контекста.** `EnvironmentPostProcessor` подключается к HashiCorp Vault, AWS Secrets Manager или аналогу и вносит полученные значения в `Environment` как `MapPropertySource` с высоким приоритетом (`addFirst`). После этого бины, DataSource, kafka-продюсеры и т.д. получают реальные пароли через `@Value` или `spring.datasource.password`.

```java
@Order(Ordered.HIGHEST_PRECEDENCE + 11)
public class VaultEnvironmentPostProcessor implements EnvironmentPostProcessor {

    @Override
    public void postProcessEnvironment(ConfigurableEnvironment env,
                                       SpringApplication app) {
        Map<String, Object> secrets = fetchSecretsFromVault();
        env.getPropertySources().addFirst(
            new MapPropertySource("vault-secrets", secrets));
    }
}
```

2. **Декодирование зашифрованных свойств** (например, значений в формате `ENC(...)` из Jasypt).
3. **Нормализация переменных окружения** — преобразование нестандартных имён переменных к виду, ожидаемому Spring.
4. **Загрузка дополнительных YAML/Properties-файлов** из файловой системы контейнера или сети, которые не входят в classpath.
5. **Переопределение свойств в зависимости от среды** без профилей — когда имя окружения берётся из внешней системы.

**Важное замечание (Spring Boot 4.x)**

В Spring Boot 4.0 интерфейс `EnvironmentPostProcessor` помечен как `@Deprecated` с планируемым удалением в 4.2.0. Рекомендуется следить за обновлениями документации и использовать альтернативный механизм, который будет предложен командой Spring.

---

### Вопрос 50. В чём разница между @ConditionalOnProperty с matchIfMissing=true и matchIfMissing=false? Как ведёт себя аннотация, если свойство задано, но без указания havingValue? Приведите пример feature-флага для включения/отключения автоконфигурации.

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ConditionalOnProperty (Spring Boot 3.5 API — docs.spring.io)](https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/condition/ConditionalOnProperty.html)

`@ConditionalOnProperty` — аннотация, которая условно регистрирует бин (или конфигурацию), проверяя наличие и значение свойства в `Environment`.

**Атрибуты и их значения по умолчанию:**

| Атрибут | Тип | По умолчанию | Описание |
|---|---|---|---|
| `value` | `String[]` | `{}` | Псевдоним для `name` |
| `prefix` | `String` | `""` | Префикс, автоматически дополняется точкой |
| `name` | `String[]` | `{}` | Имена проверяемых свойств |
| `havingValue` | `String` | `""` | Ожидаемое значение свойства |
| `matchIfMissing` | `boolean` | `false` | Совпадает ли условие при отсутствии свойства |

**Таблица поведения `havingValue`:**

| Значение свойства | `havingValue=""` | `havingValue="true"` | `havingValue="false"` | `havingValue="foo"` |
|---|---|---|---|---|
| `"true"` | да | да | нет | нет |
| `"false"` | нет | нет | да | нет |
| `"foo"` | да | нет | нет | да |

Поведение по умолчанию (пустой `havingValue`): свойство должно присутствовать и **не** быть равным `"false"`.

Если свойство отсутствует в `Environment`:
- `matchIfMissing=false` (по умолчанию) — условие **не выполняется**, бин не регистрируется.
- `matchIfMissing=true` — условие **выполняется**, бин регистрируется, как если бы свойство было задано с подходящим значением.

#### Ответ от Claude

**Разница между matchIfMissing=true и matchIfMissing=false**

`matchIfMissing` отвечает только на вопрос: «что делать, если свойство вообще не задано?»

- `matchIfMissing=false` (значение по умолчанию): отсутствующее свойство означает «условие не выполнено». Бин/конфигурация **не создаётся**. Это поведение «opt-in» — фича отключена, пока явно не включена.
- `matchIfMissing=true`: отсутствующее свойство означает «условие выполнено». Бин **создаётся**. Это поведение «opt-out» — фича включена по умолчанию, пока явно не отключена.

Если же свойство присутствует в `Environment`, `matchIfMissing` не влияет — проверяется только значение через `havingValue`.

**Поведение без указания havingValue**

Когда `havingValue` не задан (остаётся пустой строкой `""`), Spring Boot проверяет только одно условие: значение свойства **не равно строке `"false"`**.

Примеры:
```properties
# Условие выполнено (не "false"):
my.feature=true
my.feature=enabled
my.feature=yes
my.feature=1
my.feature=anything

# Условие НЕ выполнено:
my.feature=false
```

Это удобно для простых boolean-флагов, где достаточно `@ConditionalOnProperty("my.feature")` без явного `havingValue="true"`. Однако для явности в продакшн-коде рекомендуется указывать `havingValue="true"` — это делает намерение однозначным.

**Полная таблица поведения (сводная)**

| Свойство задано? | Значение | `havingValue` | Условие |
|---|---|---|---|
| Нет | — | любой | `matchIfMissing` (false → нет, true → да) |
| Да | `"false"` | `""` | нет |
| Да | `"true"` | `""` | да |
| Да | `"foo"` | `""` | да (не "false") |
| Да | `"true"` | `"true"` | да |
| Да | `"false"` | `"true"` | нет |
| Да | `"true"` | `"false"` | нет |
| Да | `"false"` | `"false"` | да |

**Пример feature-флага для включения/отключения автоконфигурации**

Сценарий 1: фича **отключена по умолчанию** (opt-in). Включается явной установкой `app.feature.audit=true`:

```java
@Configuration
@ConditionalOnProperty(
    prefix = "app.feature",
    name = "audit",
    havingValue = "true",
    matchIfMissing = false   // без свойства — фича выключена
)
public class AuditAutoConfiguration {

    @Bean
    public AuditService auditService() {
        return new AuditService();
    }
}
```

```properties
# application.properties — включить фичу:
app.feature.audit=true

# Или отсутствие свойства — фича выключена (matchIfMissing=false)
```

Сценарий 2: фича **включена по умолчанию** (opt-out). Отключается явной установкой `app.feature.metrics=false`:

```java
@Configuration
@ConditionalOnProperty(
    prefix = "app.feature",
    name = "metrics",
    havingValue = "true",
    matchIfMissing = true    // без свойства — фича включена
)
public class MetricsAutoConfiguration {

    @Bean
    public MetricsCollector metricsCollector() {
        return new MetricsCollector();
    }
}
```

```properties
# application.properties — отключить фичу:
app.feature.metrics=false

# Или не задавать свойство — фича включена (matchIfMissing=true)
```

**Практические рекомендации**

1. Всегда указывать `havingValue="true"` явно для boolean-флагов — код становится самодокументируемым.
2. Выбирать `matchIfMissing` в зависимости от желаемой семантики: opt-in = `false`, opt-out = `true`.
3. Использовать `prefix` + `name` вместо полного имени в `value` — это удобнее при группировке флагов.
4. Помнить об ограничении: `@ConditionalOnProperty` не работает надёжно с коллекционными свойствами (`list[0]`, `map.key`). Для таких случаев применяется `Condition` с ручной реализацией.

---

### Вопрос 51. Что такое Spring Boot DevTools? Как работает механизм автоматического перезапуска на основе двух класслоадеров? Чем автоперезапуск отличается от «холодного старта» и какие ресурсы по умолчанию исключены из наблюдения?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Developer Tools :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/devtools.html)

Spring Boot DevTools — это модуль для разработки, который предоставляет дополнительные возможности: автоматический перезапуск при изменении classpath, LiveReload, разумные настройки по умолчанию для разработки (например, отключение кешей шаблонов).

**Автоматический перезапуск** использует два класслоадера:
- **Base classloader** — загружает сторонние JAR-зависимости, которые меняются редко. Этот загрузчик сохраняется между перезапусками.
- **Restart classloader** — загружает код самого приложения. Именно он заменяется при каждом перезапуске.

Когда происходит перезапуск, существующий restart classloader выбрасывается и создаётся новый — это значительно быстрее «холодного старта», потому что base classloader со всеми тяжёлыми зависимостями остаётся в памяти.

По умолчанию из наблюдения (и перезапуска) исключаются ресурсы: `/META-INF/maven`, `/META-INF/resources`, `/resources`, `/static`, `/public`, `/templates` — изменения в них вместо перезапуска только инициируют LiveReload. Перечень исключений настраивается через `spring.devtools.restart.exclude`.

#### Ответ от Claude

**Что такое Spring Boot DevTools**

`spring-boot-devtools` — это дополнительный модуль, предназначенный исключительно для разработки. При упаковке в исполняемый JAR (`java -jar`) или развёртывании в production DevTools автоматически отключается. Подключается с `optional = true` в Maven или в конфигурации `developmentOnly` в Gradle.

**Механизм двух класслоадеров**

При обычном Java-запуске один загрузчик классов загружает весь код — и зависимости, и приложение. При перезапуске всё выгружается из памяти и загружается заново. Это «холодный старт».

DevTools разделяет код на два домена:

| Класслоадер | Что загружает | При перезапуске |
|---|---|---|
| **Base classloader** | Сторонние JAR (Spring, Hibernate, Jackson...) | Сохраняется |
| **Restart classloader** | Классы приложения (`target/classes`, `build/classes`) | Заменяется новым |

Благодаря тому что base classloader не пересоздаётся, перезапуск в несколько раз быстрее холодного старта.

**Триггеры перезапуска**

- IntelliJ IDEA: Build → Build Project (Ctrl+F9)
- Eclipse: автоматически при сохранении файла
- Maven: `mvn compile`
- Gradle: `gradle classes`

DevTools наблюдает за изменениями в classpath через File System Watcher. Настройка интервала опроса и тихого периода:

```properties
spring.devtools.restart.poll-interval=2s
spring.devtools.restart.quiet-period=400ms
```

**Что исключено из наблюдения по умолчанию**

Следующие пути не вызывают перезапуск (изменения в них инициируют только LiveReload):

```
/META-INF/maven/**
/META-INF/resources/**
/resources/**
/static/**
/public/**
/templates/**
```

Дополнить список исключений:
```properties
spring.devtools.restart.exclude=static/**,public/**,custom/**
```

Добавить пути, которые тоже должны наблюдаться:
```properties
spring.devtools.restart.additional-paths=src/main/resources
```

Для тонкого управления — файл-триггер: перезапуск происходит только при изменении конкретного файла:
```properties
spring.devtools.restart.trigger-file=.reloadtrigger
```

**Настройки по умолчанию для разработки (property defaults)**

DevTools автоматически применяет ряд свойств, подходящих для разработки:

| Свойство | Значение при DevTools |
|---|---|
| `spring.thymeleaf.cache` | `false` |
| `spring.freemarker.cache` | `false` |
| `spring.web.resources.cache.period` | `0` |
| `spring.h2.console.enabled` | `true` |

Отключить auto-properties: `spring.devtools.add-properties=false`.

**LiveReload**

Встроенный LiveReload-сервер автоматически обновляет браузер при изменении ресурсов. Требуется установить расширение LiveReload для браузера. Отключить: `spring.devtools.livereload.enabled=false`.

**Важные ограничения**

- Не работает в production — автоматически отключается при `java -jar`.
- Не совместим с AspectJ weaving.
- При работе в multi-module проекте может потребоваться тонкая настройка исключений через `META-INF/spring-devtools.properties`.
- LiveReload deprecated начиная с Spring Boot 4.1.0.

---

### Вопрос 52. Чем CommandLineRunner отличается от ApplicationRunner? Когда вызываются оба интерфейса в жизненном цикле Spring Boot-приложения, как упорядочить несколько runners и что даёт ApplicationArguments по сравнению с String[]?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [SpringApplication :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

Оба интерфейса — `CommandLineRunner` и `ApplicationRunner` — позволяют выполнить код сразу после запуска `SpringApplication`. Главное отличие состоит в способе получения аргументов командной строки:

- `CommandLineRunner` — получает аргументы как простой массив `String[]`.
- `ApplicationRunner` — получает аргументы через интерфейс `ApplicationArguments`, который разделяет аргументы на опции (вида `--key=value`) и позиционные аргументы (non-option args).

Если определены несколько бинов `CommandLineRunner` или `ApplicationRunner`, порядок их вызова контролируется через `@Order` или реализацию интерфейса `Ordered`.

#### Ответ от Claude

**Общее**

Оба интерфейса предназначены для выполнения произвольного кода в момент, когда `ApplicationContext` полностью готов, но до того, как `SpringApplication.run()` вернёт управление вызывающему коду. Типичные применения: загрузка начальных данных в БД, прогрев кешей, валидация конфигурации.

**Место в жизненном цикле**

```
ApplicationContext refresh() завершён
        ↓
ApplicationStartedEvent опубликован
        ↓
Вызываются все CommandLineRunner и ApplicationRunner (в порядке @Order)
        ↓
ApplicationReadyEvent опубликован
        ↓
SpringApplication.run() возвращает ApplicationContext
```

**Разница в аргументах**

```java
// CommandLineRunner — сырой String[]
@Component
public class DataLoader implements CommandLineRunner {
    @Override
    public void run(String... args) {
        // args = ["--debug", "logfile.txt"] — всё в одном массиве
        Arrays.stream(args).forEach(System.out::println);
    }
}

// ApplicationRunner — разобранные аргументы через ApplicationArguments
@Component
public class ConfigVerifier implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) {
        // Запуск: java -jar app.jar --debug logfile.txt
        boolean debug = args.containsOption("debug");        // true
        List<String> files = args.getNonOptionArgs();         // ["logfile.txt"]
        List<String> debugValues = args.getOptionValues("debug"); // [] (флаг без значения)
    }
}
```

| Метод | Описание |
|---|---|
| `containsOption(String)` | Проверяет наличие опции `--key` |
| `getOptionValues(String)` | Возвращает значения опции `--key=value` |
| `getNonOptionArgs()` | Позиционные аргументы (не начинающиеся с `--`) |
| `getSourceArgs()` | Исходный массив `String[]` |

**Упорядочивание нескольких runners**

```java
@Component
@Order(1)
public class MigrationRunner implements CommandLineRunner {
    @Override
    public void run(String... args) {
        // Запускается первым
    }
}

@Component
@Order(2)
public class DataSeedRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) {
        // Запускается после MigrationRunner
    }
}
```

Меньшее значение `@Order` = более высокий приоритет = вызывается раньше. `CommandLineRunner` и `ApplicationRunner` упорядочиваются в едином пространстве: если у `CommandLineRunner(@Order(1))` и `ApplicationRunner(@Order(2))` разные значения, первый будет вызван раньше независимо от типа.

**Обработка исключений**

Если `run()` выбрасывает исключение, оно превращается в `ApplicationFailedEvent` и останавливает приложение. Для «мягкой» обработки нужно самостоятельно перехватывать исключения внутри метода.

**Когда что выбирать**

- `CommandLineRunner` — когда аргументы не нужны или достаточно простого массива строк.
- `ApplicationRunner` — когда нужно разбирать опции `--key=value` или использовать `getNonOptionArgs()`.
- Оба — при наличии простых задач инициализации. Разница минимальна; выбор определяется удобством работы с аргументами.

---

### Вопрос 53. Что такое ленивая инициализация бинов (lazy initialization) в Spring Boot? Как включить её глобально и для отдельного бина? Какие выгоды и риски несёт отложенное создание бинов?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [SpringApplication :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

При включении ленивой инициализации бины создаются не при запуске приложения, а при первом обращении к ним. В веб-приложении это означает, что многие web-связанные бины не будут инициализированы до получения первого HTTP-запроса.

Недостаток ленивой инициализации — задержка обнаружения проблем с конфигурацией: ошибки, которые могли бы проявиться при старте, будут обнаружены лишь при первом использовании бина.

Включить глобально:
```properties
spring.main.lazy-initialization=true
```

Или программно:
```java
SpringApplication app = new SpringApplication(MyApplication.class);
app.setLazyInitialization(true);
```

`SmartInitializingSingleton`-бины и инфраструктурные бины автоматически исключаются из ленивой инициализации.

#### Ответ от Claude

**Что такое ленивая инициализация**

По умолчанию Spring Boot создаёт все singleton-бины в момент старта `ApplicationContext` (eager initialization). Ленивая инициализация (`@Lazy`) меняет это поведение: бин создаётся только при первом обращении к нему — через инъекцию зависимости, прямое получение из контекста или вызов.

**Способы включения**

**Глобально через свойство:**
```properties
spring.main.lazy-initialization=true
```

```yaml
spring:
  main:
    lazy-initialization: true
```

**Программно:**
```java
SpringApplication app = new SpringApplication(MyApplication.class);
app.setLazyInitialization(true);
// Или через builder:
new SpringApplicationBuilder(MyApplication.class)
    .lazyInitialization(true)
    .run(args);
```

**Для конкретного бина** с помощью `@Lazy`:

```java
@Component
@Lazy
public class HeavyService {
    // Инициализируется только при первом обращении
}

@Configuration
public class AppConfig {
    @Bean
    @Lazy
    public ReportGenerator reportGenerator() {
        return new ReportGenerator();
    }
}
```

**Исключить конкретный бин из глобальной ленивой инициализации** (т.е. вернуть eager-поведение):

```java
@Component
@Lazy(false)  // явно eager при глобальной lazy-инициализации
public class CriticalService {
    // Всегда создаётся при старте
}
```

**Выгоды ленивой инициализации**

1. **Быстрый старт приложения** — меньше бинов создаётся при запуске. Особенно заметно в монолитах с большим количеством редко используемых компонентов.
2. **Экономия памяти при старте** — бины не занимают память до востребования.
3. **Ускорение тестов** — при тестировании части функциональности не поднимаются неиспользуемые подсистемы.

**Риски и ограничения**

| Риск | Пояснение |
|---|---|
| Задержка обнаружения ошибок конфигурации | Ошибки в `@PostConstruct`, неверные `@Autowired`-зависимости обнаружатся при первом обращении к бину, а не при старте |
| Задержка первого запроса | Первый HTTP-запрос, инициализирующий цепочку бинов, будет значительно медленнее последующих |
| Неопределённость JVM heap | Все бины будут рано или поздно созданы; нужно подбирать размер heap под полную нагрузку, а не только под старт |
| Нарушение порядка инициализации | При ленивой инициализации порядок создания бинов определяется порядком обращения, что сложнее предсказать |

**Какие бины исключены автоматически**

Spring Boot автоматически исключает из ленивой инициализации:
- Бины, реализующие `SmartInitializingSingleton` — их колбэк-метод должен быть вызван после инициализации всех singleton-бинов.
- Инфраструктурные бины (с ролью `ROLE_INFRASTRUCTURE`).

**Рекомендация**

Ленивую инициализацию рекомендуется включать в development-профиле для ускорения цикла разработки, но не в production по умолчанию. В production её применение оправдано только после профилирования и с явным `@Lazy(false)` на критических бинах, чтобы ошибки проявлялись при старте.

---

### Вопрос 54. Как Spring Boot автоматически применяет Flyway и Liquibase? Какой файл является точкой входа для каждого инструмента, как настроить альтернативный DataSource для миграций и как отключить автомиграцию?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Database Initialization :: Spring Boot How-to](https://docs.spring.io/spring-boot/how-to/data-initialization.html)

**Flyway.** При наличии `spring-boot-starter-flyway` (или `org.flywaydb:flyway-core`) в classpath Spring Boot автоматически вызывает `Flyway.migrate()` при старте. По умолчанию скрипты ищутся в `classpath:db/migration`. Скрипты именуются `V<VERSION>__<NAME>.sql` (например, `V1__create_tables.sql`). Flyway использует `@Primary` DataSource, если не задан явный бин с `@FlywayDataSource`. Для полного контроля над процессом можно зарегистрировать бин `FlywayMigrationStrategy`.

**Liquibase.** При наличии `org.liquibase:liquibase-core` Spring Boot автоматически применяет changelogs при старте. Точка входа по умолчанию: `classpath:db/changelog/db.changelog-master.yaml`. Поддерживаются форматы YAML, JSON, XML и SQL. Использует `@Primary` DataSource, если не задан бин с `@LiquibaseDataSource`.

#### Ответ от Claude

**Механизм автоконфигурации**

Spring Boot обнаруживает Flyway и Liquibase через `@ConditionalOnClass`:
- `FlywayAutoConfiguration` — активируется при наличии `org.flywaydb.core.Flyway` в classpath.
- `LiquibaseAutoConfiguration` — активируется при наличии `liquibase.integration.spring.SpringLiquibase` в classpath.

Обе автоконфигурации выполняются как dependency на `DataSourceAutoConfiguration`, поэтому DataSource гарантированно существует к моменту миграции.

**Flyway — ключевые сведения**

Формат скриптов: `V{version}__{description}.sql`, где версия — числа с разделителями `_` или `.`.

```
src/main/resources/
  db/
    migration/
      V1__create_users_table.sql
      V2__add_email_column.sql
      V2_1__add_email_index.sql
      R__refresh_materialized_view.sql   # повторяемые (Repeatable)
```

Ключевые свойства:

```properties
# Расположение скриптов (можно несколько через запятую)
spring.flyway.locations=classpath:db/migration,filesystem:/opt/migrations

# Специфичные для БД скрипты через placeholder {vendor}
spring.flyway.locations=classpath:db/migration/{vendor}

# Отключить Flyway
spring.flyway.enabled=false

# Базовая версия (полезно при добавлении Flyway в существующую схему)
spring.flyway.baseline-on-migrate=true
spring.flyway.baseline-version=1
```

**Liquibase — ключевые сведения**

```
src/main/resources/
  db/
    changelog/
      db.changelog-master.yaml         # точка входа по умолчанию
      changes/
        v1-create-users.yaml
        v2-add-email.yaml
```

Ключевые свойства:

```properties
# Расположение master changelog
spring.liquibase.change-log=classpath:db/changelog/db.changelog-master.yaml

# Отключить Liquibase
spring.liquibase.enabled=false

# Контексты (например, для test-данных)
spring.liquibase.contexts=dev,test
```

**Альтернативный DataSource для миграций**

Иногда нужно запускать миграции через отдельного пользователя БД с расширенными правами:

```java
// Для Flyway
@Bean
@FlywayDataSource
public DataSource flywayDataSource() {
    return DataSourceBuilder.create()
        .url("jdbc:postgresql://localhost:5432/mydb")
        .username("migrationuser")
        .password("migrationpass")
        .build();
}

// Для Liquibase
@Bean
@LiquibaseDataSource
public DataSource liquibaseDataSource() {
    return DataSourceBuilder.create()
        .url("jdbc:postgresql://localhost:5432/mydb")
        .username("liquibaseuser")
        .password("liquibasepass")
        .build();
}
```

Или через свойства (без создания отдельного DataSource-бина):

```properties
# Flyway использует отдельный URL вместо primary DataSource
spring.flyway.url=jdbc:postgresql://localhost:5432/mydb
spring.flyway.user=migrationuser
spring.flyway.password=migrationpass
```

**Отключение автомиграции**

```properties
# Flyway
spring.flyway.enabled=false

# Liquibase
spring.liquibase.enabled=false
```

**Инициализация только в тестах**

Для загрузки тестовых данных после production-миграций:

```
# Flyway: добавить тестовые скрипты в src/test/resources/db/migration/
# Liquibase: использовать контекст test
spring.liquibase.contexts=test
```

**Порядок инициализации**

Spring Boot автоматически выстраивает зависимости: `FlywayMigrationInitializer` (или `SpringLiquibase`) → `EntityManagerFactory` → JPA-репозитории. Это гарантирует, что схема создана до того, как JPA попытается провалидировать маппинг сущностей.

---

### Вопрос 55. Чем @MockitoBean отличается от @MockBean? Какой из них рекомендован начиная с Spring Boot 3.4 и почему прежний @MockBean признан устаревшим? Каковы ограничения @MockitoBean?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Testing Spring Boot Applications :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)

`@MockitoBean` — это аннотация из Spring Framework, позволяющая определить Mockito-мок для бина внутри `ApplicationContext`. В Spring Boot 3.4 аннотации `@MockBean` и `@SpyBean` из `spring-boot-test` помечены как `@Deprecated`, и их заменяют `@MockitoBean` и `@MockitoSpyBean` из Spring Framework.

```java
@SpringBootTest
class MyTests {
    @MockitoBean
    private UserService userService;

    @MockitoSpyBean
    private UserRepository userRepository;

    @Test
    void exampleTest() {
        given(this.userService.getUser("sboot"))
            .willReturn(new User("Spring Boot"));
    }
}
```

#### Ответ от Claude

**История изменений**

`@MockBean` появился в Spring Boot 1.4 как встроенный механизм создания Mockito-моков в контексте Spring-теста. Начиная с Spring Boot 3.4 (и Spring Framework 6.2) аналогичный механизм был перенесён непосредственно в Spring Framework в виде аннотации `@MockitoBean`. `@MockBean` из `spring-boot-test` помечена как deprecated и будет удалена в будущих версиях.

**Сходство**

Обе аннотации:
- Заменяют бин указанного типа (или имени) в `ApplicationContext` на Mockito-мок.
- Мок сбрасывается (reset) после каждого теста.
- Поддерживают поле-уровневую декларацию.

**Различия**

| Аспект | `@MockBean` (устарел) | `@MockitoBean` (актуален) |
|---|---|---|
| Модуль | `spring-boot-test` | `spring-framework` (test) |
| Поддержка на `@Configuration`-классе | Да | Нет |
| Поддержка на `@Component`-классе | Да | Нет |
| Применение к типу класса | Да (type-level) | Нет (только field-level) |
| Производительность | Создаёт прокси в контексте | Прямая Mockito-интеграция |
| Статус в Spring Boot 3.4+ | Deprecated | Рекомендован |

**Пример @MockitoBean (рекомендованный способ)**

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserService userService;   // заменяет бин в контексте

    @Test
    void getUser_shouldReturn200() throws Exception {
        given(userService.findById(1L)).willReturn(new User(1L, "Alice"));

        mockMvc.perform(get("/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

**@MockitoSpyBean — шпион вместо мока**

```java
@SpringBootTest
class OrderServiceTest {

    @MockitoSpyBean
    private EmailService emailService;  // реальная реализация + возможность verify

    @Test
    void placeOrder_shouldSendEmail() {
        orderService.placeOrder(new Order(...));
        then(emailService).should().sendConfirmation(any());
    }
}
```

**Ограничения @MockitoBean**

1. Применяется только к полю теста (field-level), не к классу.
2. Нельзя использовать на `@Configuration`-классе (в отличие от `@MockBean`).
3. Нельзя использовать на `@Component`-классе (если нужно мокировать тип в самом компоненте).
4. Требует Spring Framework 6.2 / Spring Boot 3.4.

**Временная стратегия миграции**

Если проект использует `@MockBean` в type-level или на `@Configuration`, понадобится рефакторинг перед удалением deprecated-аннотации. В остальных случаях замена тривиальна: `@MockBean` → `@MockitoBean`, `@SpyBean` → `@MockitoSpyBean`.

---

### Вопрос 56. Что такое @TestConfiguration и чем она отличается от обычной @Configuration в тестах? Как работает обнаружение @TestConfiguration — когда она обнаруживается автоматически, а когда требует явного @Import?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Testing Spring Boot Applications :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)

`@TestConfiguration` — специализированная форма `@Configuration`, которая может быть использована для определения дополнительных бинов или кастомизации уже существующих бинов для тестов. В отличие от обычного `@Configuration`, классы `@TestConfiguration` не подхватываются стандартным сканированием компонентов при использовании в качестве самостоятельного файла верхнего уровня — они должны быть явно импортированы через `@Import`.

Внутренний статический класс теста, аннотированный `@TestConfiguration`, обнаруживается автоматически.

#### Ответ от Claude

**Что такое @TestConfiguration**

`@TestConfiguration` — аннотация Spring Boot, позволяющая добавить тестовые бины в уже существующий контекст приложения. В отличие от обычного `@Configuration`:

- Тестовая конфигурация **дополняет** продакшн-конфигурацию, а не заменяет её.
- Классы с `@TestConfiguration` по умолчанию **исключены из `@ComponentScan`** (когда они находятся на уровне самостоятельного файла), что защищает от случайного применения тестовых настроек в production.

**Два способа использования**

**Способ 1: Внутренний статический класс — обнаруживается автоматически**

```java
@SpringBootTest
class MyServiceTest {

    @Autowired
    private MyService myService;

    @TestConfiguration
    static class TestConfig {
        @Bean
        public ExternalApiClient mockApiClient() {
            // Переопределяет бин для тестов
            return new FakeApiClient();
        }
    }

    @Test
    void test() { ... }
}
```

Spring Boot автоматически находит и применяет вложенный `@TestConfiguration`-класс.

**Способ 2: Отдельный файл — требует явного @Import**

```java
// src/test/java/com/example/TestInfrastructureConfig.java
@TestConfiguration
public class TestInfrastructureConfig {
    @Bean
    public MockMailService mailService() {
        return new MockMailService();
    }
}

// В тесте — явный импорт
@SpringBootTest
@Import(TestInfrastructureConfig.class)
class OrderServiceTest {
    @Test
    void test() { ... }
}
```

**Чем @TestConfiguration отличается от @Configuration в тестах**

| Аспект | `@Configuration` в тесте | `@TestConfiguration` |
|---|---|---|
| Включается в `@ComponentScan` | Да | Нет (как top-level файл) |
| Риск попасть в production | Да, если scan пакет включает тест | Нет |
| Добавляет бины поверх prod-конфига | Нет — заменяет | Да — дополняет |
| Обнаружение как inner-класс | Автоматически | Автоматически |
| Обнаружение как top-level файл | Автоматически | Только через `@Import` |

**Важный нюанс: порядок обработки**

Импортированная top-level `@TestConfiguration` обрабатывается раньше, чем внутренний `@TestConfiguration`-класс, и раньше, чем конфигурация, найденная через component scanning. Это может иметь значение при наличии нескольких переопределений одного бина.

**Типичные сценарии использования**

1. Подмена внешних зависимостей (mail-сервис, payment-шлюз) на фейковые реализации.
2. Регистрация тестовых `HealthIndicator`-ов.
3. Настройка специфичных `TestRestTemplate` или `WebTestClient`.
4. Предоставление `@Bean`-ов, недоступных в тестовой среде (например, AWS-клиент).

---

### Вопрос 57. Как Spring Boot интегрирует Micrometer для метрик? Как создать кастомный Counter, Timer и Gauge через MeterRegistry? Что такое tags/labels и как они влияют на кардинальность метрик?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Quick Guide to Micrometer — baeldung.com](https://www.baeldung.com/micrometer)

Micrometer — это фасад над клиентами инструментирования для популярных систем мониторинга (Prometheus, Datadog, Atlas, Graphite и др.). Он позволяет переключать мониторинговый бэкенд без изменения кода приложения.

`MeterRegistry` — центральный объект для регистрации метрик. Основные типы измерителей (Meter):
- **Counter** — монотонно возрастающее значение (количество событий).
- **Timer** — измеряет задержку операций и их частоту.
- **Gauge** — текущее значение (размер очереди, использование памяти).
- **DistributionSummary** — распределение значений (размеры запросов, ответов).

Аннотация `@Timed` на контроллере автоматически создаёт Timer для методов-обработчиков.

#### Ответ от Claude

**Интеграция Micrometer в Spring Boot**

При подключении `spring-boot-starter-actuator` Spring Boot автоматически:
- Регистрирует `MeterRegistry` как Spring-бин.
- Настраивает стандартные метрики JVM, пула потоков, кешей, JDBC, HTTP-запросов.
- Подключает backend-реестры по classpath: `micrometer-registry-prometheus` → `PrometheusMeterRegistry` и т.д.

Получить метрики через Actuator:
```properties
management.endpoints.web.exposure.include=metrics,prometheus
```

**Counter — счётчик событий**

```java
@Service
public class OrderService {
    private final Counter orderCounter;

    public OrderService(MeterRegistry registry) {
        this.orderCounter = Counter.builder("orders.created")
            .description("Total number of orders created")
            .tag("region", "eu-west")    // tag = label в Prometheus
            .register(registry);
    }

    public Order createOrder(OrderRequest request) {
        Order order = processOrder(request);
        orderCounter.increment();        // увеличить на 1
        // или: orderCounter.increment(2.0); // увеличить на произвольное значение
        return order;
    }
}
```

**Timer — измерение времени**

```java
@Service
public class PaymentService {
    private final Timer paymentTimer;

    public PaymentService(MeterRegistry registry) {
        this.paymentTimer = Timer.builder("payment.processing.time")
            .description("Time to process payment")
            .publishPercentiles(0.5, 0.95, 0.99)   // перцентили
            .register(registry);
    }

    public PaymentResult processPayment(Payment payment) {
        return paymentTimer.recordCallable(() -> doProcessPayment(payment));
        // Или: Timer.Sample sample = Timer.start(registry);
        //      ...
        //      sample.stop(paymentTimer);
    }
}
```

**Gauge — текущее значение**

```java
@Component
public class QueueMonitor {
    private final Queue<Task> taskQueue = new LinkedBlockingQueue<>();

    public QueueMonitor(MeterRegistry registry) {
        Gauge.builder("task.queue.size", taskQueue, Queue::size)
            .description("Current number of tasks in queue")
            .register(registry);
    }
}
```

**Tags (метки) и их влияние на кардинальность**

Tags позволяют добавить измерения к метрике, сделав её многомерной:

```java
Counter.builder("http.requests")
    .tag("method", "GET")
    .tag("status", "200")
    .tag("endpoint", "/api/users")
    .register(registry)
    .increment();
```

В Prometheus это создаёт метрику `http_requests_total{method="GET", status="200", endpoint="/api/users"}`.

**Кардинальность (cardinality)** — количество уникальных комбинаций значений тегов. Это критически важная концепция:

| Тег | Пример значений | Кардинальность |
|---|---|---|
| `http.method` | GET, POST, PUT, DELETE | 4 — безопасно |
| `http.status` | 200, 404, 500, ... | ~10 — безопасно |
| `user.id` | 1, 2, 3, ..., 10_000_000 | Крайне опасно |
| `request.url` | /api/users/1, /api/users/2, ... | Опасно без нормализации |

**Опасность высокой кардинальности:** каждая уникальная комбинация тегов создаёт отдельный time series в системе мониторинга. Миллионы уникальных `user.id` приведут к миллионам time series, что перегрузит Prometheus или Datadog.

**Правило:** используйте теги только с ограниченным числом значений (enum-подобные значения).

**@Timed для автоматической инструментации**

```java
@RestController
@Timed("api.requests")   // Timer для всех методов контроллера
public class UserController {

    @GetMapping("/users/{id}")
    @Timed(value = "api.users.get", percentiles = {0.5, 0.95})
    public User getUser(@PathVariable Long id) { ... }
}
```

Требует наличия `TimedAspect`-бина (Spring Boot не регистрирует его автоматически — нужна явная регистрация):
```java
@Bean
public TimedAspect timedAspect(MeterRegistry registry) {
    return new TimedAspect(registry);
}
```

---

### Вопрос 58. Что такое BeanDefinitionOverrideException в Spring Boot? Начиная с какой версии переопределение бинов запрещено по умолчанию? Как включить обратно allow-bean-definition-overriding и почему это не рекомендуется в production?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [The BeanDefinitionOverrideException in Spring Boot — baeldung.com](https://www.baeldung.com/spring-boot-bean-definition-override-exception)

`BeanDefinitionOverrideException` возникает, когда в `ApplicationContext` регистрируется бин с тем же именем, что и уже существующий. Это исключение было введено в Spring 5.1, а Spring Boot 2.1 отключил переопределение бинов по умолчанию. Если ваше приложение использует переопределение бинов, после обновления до Spring Boot 2.1 и выше вы, скорее всего, столкнётесь с этим исключением.

Для восстановления прежнего поведения нужно задать свойство:
```properties
spring.main.allow-bean-definition-overriding=true
```

Однако в этом случае сложно предсказать, какой именно бин победит — порядок создания бинов определяется отношениями зависимостей, что делает поведение непредсказуемым.

#### Ответ от Claude

**Что происходит и почему**

В Spring IoC-контейнере каждый бин идентифицируется своим именем. Если два бина имеют одинаковое имя, возникает конфликт.

До Spring 5.1 и Spring Boot 2.1 такой конфликт разрешался молча: последний зарегистрированный бин перезаписывал предыдущий. Это могло маскировать случайные дубликаты и вызывать трудноуловимые баги.

Начиная с **Spring 5.1 / Spring Boot 2.1** поведение изменилось:
- `spring.main.allow-bean-definition-overriding` по умолчанию = `false`.
- При конфликте имён выбрасывается `BeanDefinitionOverrideException`.

**Типичные причины возникновения**

```java
// Конфликт: два метода @Bean с одинаковым именем
@Configuration
public class DataConfig {
    @Bean
    public DataSource dataSource() { ... }
}

@Configuration
public class TestDataConfig {
    @Bean
    public DataSource dataSource() { ... }  // BeanDefinitionOverrideException!
}
```

```java
// Конфликт: @Component и @Bean с одинаковым именем
@Component
public class MyService { ... }  // имя бина: "myService"

@Configuration
public class Config {
    @Bean("myService")  // тот же имя → конфликт
    public MyService myServiceBean() { ... }
}
```

**Включение переопределения (только при крайней необходимости)**

```properties
# application.properties
spring.main.allow-bean-definition-overriding=true
```

```yaml
# application.yml
spring:
  main:
    allow-bean-definition-overriding: true
```

Или программно:
```java
SpringApplication app = new SpringApplication(MyApplication.class);
app.setAllowBeanDefinitionOverriding(true);
```

**Почему это опасно в production**

1. **Непредсказуемый победитель.** Порядок регистрации бинов определяется сложным графом зависимостей — нельзя гарантировать, какой из конкурирующих бинов окажется в контексте.
2. **Маскирует дубликаты.** Случайное дублирование бинов не вызовет ошибки и может привести к неожиданному поведению.
3. **Сложность отладки.** При нескольких модулях, каждый из которых регистрирует бин с одним именем, найти «победителя» крайне сложно.

**Правильные альтернативы**

1. **Переименовать бин** — явно задать уникальное имя:

```java
@Bean("primaryDataSource")
public DataSource primaryDataSource() { ... }

@Bean("testDataSource")
public DataSource testDataSource() { ... }
```

2. **Использовать `@Primary`** — пометить один бин как основной:

```java
@Bean
@Primary
public DataSource mainDataSource() { ... }

@Bean
public DataSource secondaryDataSource() { ... }
```

3. **Профили** — разграничить бины по профилям:

```java
@Bean
@Profile("production")
public DataSource prodDataSource() { ... }

@Bean
@Profile("test")
public DataSource testDataSource() { ... }
```

4. **`@MockitoBean` в тестах** — вместо определения конкурирующего бина с тем же именем использовать аннотацию для замены в тестовом контексте.

---

### Вопрос 59. Что такое GraalVM Native Image в контексте Spring Boot? Как работает AOT-компиляция: что генерирует Spring AOT Engine, какие hint-файлы создаются и каковы ключевые ограничения native image по сравнению с JVM-запуском?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Introducing GraalVM Native Images :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/packaging/native-image/introducing-graalvm-native-images.html)

GraalVM Native Image — это технология AOT-компиляции (ahead-of-time), которая компилирует Java-приложение в нативный исполняемый файл для конкретной платформы. Готовый образ:
- Запускается значительно быстрее JVM-приложения.
- Требует меньше памяти.
- Не требует JVM на хосте.

Spring Boot дополняет GraalVM собственным механизмом AOT-обработки: **Spring AOT Engine** анализирует приложение на этапе сборки и генерирует Java-код и hint-файлы, которые позволяют GraalVM корректно включить в образ все необходимые компоненты.

Hint-файлы генерируются в `META-INF/native-image/{groupId}/{artifactId}/` и автоматически обнаруживаются GraalVM.

#### Ответ от Claude

**Почему нужна AOT-компиляция для Spring**

Spring активно использует рефлексию, динамические прокси и runtime classpath scanning. GraalVM Native Image работает на принципе «замкнутого мира» (closed-world assumption): весь код, используемый в runtime, должен быть известен в момент компиляции. Динамические механизмы без явного указания попросту не попадут в нативный образ.

Spring AOT Engine решает эту проблему: анализирует приложение на этапе сборки и генерирует необходимые конфигурации.

**Что генерирует Spring AOT Engine**

**1. Java-исходники (Source Code)**

AOT-движок трансформирует `@Configuration`-классы и `@Bean`-методы в статический код без рефлексии:

```java
// Оригинал (использует рефлексию при обработке)
@Configuration
public class AppConfig {
    @Bean
    public UserService userService() {
        return new UserService();
    }
}

// AOT-генерированный код (без рефлексии)
public class AppConfig__BeanDefinitions {
    public static BeanDefinition getUserServiceBeanDefinition() {
        RootBeanDefinition beanDefinition = new RootBeanDefinition(UserService.class);
        beanDefinition.setInstanceSupplier(() -> new AppConfig().userService());
        return beanDefinition;
    }
}
```

Расположение: Maven — `target/spring-aot/main/sources/`, Gradle — `build/generated/aotSources/`.

**2. Hint-файлы (JSON)**

Расположение: `META-INF/native-image/{groupId}/{artifactId}/`.

| Файл | Назначение |
|---|---|
| `reflect-config.json` | Классы/методы/поля, доступные через рефлексию в runtime |
| `resource-config.json` | Ресурсные файлы, включаемые в образ |
| `proxy-config.json` | Динамические JDK-прокси, которые должны существовать в образе |
| `serialization-config.json` | Классы, требующие сериализации |
| `jni-config.json` | JNI-вызовы |

Пример `reflect-config.json`:
```json
[
  {
    "name": "com.example.UserRepository",
    "methods": [{"name": "findByEmail", "parameterTypes": ["java.lang.String"]}]
  }
]
```

**3. Proxy-классы**

CGLIB-прокси генерируются в момент сборки, а не в runtime. Расположение: `target/spring-aot/main/classes/`.

**Сборка native image**

```bash
# Maven
mvn -Pnative native:compile

# Gradle
./gradlew nativeCompile
```

Плагины `spring-boot-maven-plugin` / `spring-boot-gradle-plugin` выполняют AOT-обработку автоматически как шаг перед компиляцией нативного образа.

**Ключевые ограничения native image**

| Ограничение | Описание |
|---|---|
| Бины определяются на этапе сборки | Нельзя добавить бины в runtime; `@ConditionalOnProperty` ограниченно работает |
| Нет lazy classloading | Всё загружается при старте |
| Ограниченная рефлексия | Любая незадекларированная рефлексия приведёт к ошибке в runtime |
| Нет динамических прокси без явной регистрации | CGLIB и JDK-прокси должны быть зарегистрированы заранее |
| Профили работают частично | `@Profile` поддерживается, но динамическое переключение невозможно |
| `@RefreshScope` не работает | Динамическое обновление бинов несовместимо с native image |
| Фиксированный classpath | Нельзя добавлять JAR в runtime |

**Регистрация дополнительных hint-ов вручную**

```java
@Configuration
@RegisterReflectionForBinding(MyDto.class)   // для сериализации/десериализации
public class AppConfig {

    @Bean
    public RuntimeHintsRegistrar myHints() {
        return (hints, classLoader) -> {
            hints.reflection().registerType(MySpecialClass.class,
                MemberCategory.INVOKE_DECLARED_METHODS);
            hints.resources().registerPattern("templates/*.html");
        };
    }
}
```

**Трассировочный агент GraalVM**

Для обнаружения незадекларированных динамических операций:
```bash
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image \
     -jar app.jar
```

Агент перехватывает рефлексию, ресурсы и прокси-вызовы в runtime и генерирует hint-файлы автоматически.

---

### Вопрос 60. Какие события Spring Boot публикует в процессе запуска приложения? Перечислите события в хронологическом порядке от ApplicationStartingEvent до ApplicationReadyEvent. Когда регистрировать слушатели через spring.factories, а когда через @EventListener?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [SpringApplication :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

`SpringApplication` публикует несколько `ApplicationEvent`-событий при запуске. Порядок событий:

1. `ApplicationStartingEvent` — сразу после старта, до любой обработки (кроме регистрации слушателей/инициализаторов).
2. `ApplicationEnvironmentPreparedEvent` — когда `Environment` известен, но контекст ещё не создан.
3. `ApplicationContextInitializedEvent` — когда `ApplicationContext` подготовлен и инициализаторы вызваны, но bean-определения ещё не загружены.
4. `ApplicationPreparedEvent` — непосредственно перед началом refresh, после загрузки bean-определений.
5. `ApplicationStartedEvent` — после refresh контекста, до вызова runners.
6. `AvailabilityChangeEvent` (LivenessState.CORRECT) — приложение живо.
7. `ApplicationReadyEvent` — после вызова всех runners.
8. `AvailabilityChangeEvent` (ReadinessState.ACCEPTING_TRAFFIC) — приложение готово к трафику.
9. `ApplicationFailedEvent` — если при запуске возникло исключение.

Некоторые события публикуются до создания `ApplicationContext`, поэтому их слушатели нельзя зарегистрировать как обычные `@Component` — их нужно регистрировать через `META-INF/spring.factories` или `SpringApplication.addListeners()`.

#### Ответ от Claude

**Полная хронология событий при запуске**

```
SpringApplication.run() вызван
    ↓
1. ApplicationStartingEvent          — Environment и Context ещё не созданы
    ↓
2. ApplicationEnvironmentPreparedEvent  — Environment готов, Context не существует
    ↓
3. ApplicationContextInitializedEvent   — Context создан, инициализаторы вызваны,
                                          но BeanDefinition-ы не загружены
    ↓
4. ApplicationPreparedEvent          — BeanDefinition-ы загружены, до refresh
    ↓
5. ContextRefreshedEvent             — Context обновлён (refresh завершён)
    ↓
6. WebServerInitializedEvent         — HTTP-сервер запущен (в web-приложениях)
    ↓
7. ApplicationStartedEvent           — Context обновлён, до вызова runners
    ↓
8. AvailabilityChangeEvent(LivenessState.CORRECT)  — приложение живо
    ↓
9. CommandLineRunner / ApplicationRunner вызваны
    ↓
10. ApplicationReadyEvent             — все runners отработали
    ↓
11. AvailabilityChangeEvent(ReadinessState.ACCEPTING_TRAFFIC) — принимает трафик
```

При ошибке на любом этапе: `ApplicationFailedEvent`.

**Когда и как регистрировать слушателей**

**Способ 1: @EventListener (рекомендован для событий ПОСЛЕ создания Context)**

```java
@Component
public class ApplicationEventListener {

    @EventListener
    public void onApplicationReady(ApplicationReadyEvent event) {
        // Вызывается после запуска, все бины доступны
        System.out.println("App is ready! Context: " + event.getApplicationContext());
    }

    @EventListener
    public void onContextRefreshed(ContextRefreshedEvent event) {
        // После каждого refresh контекста (включая тесты)
    }
}
```

`@EventListener` работает только для событий, публикуемых **после** создания `ApplicationContext` (события 5–11). Для событий 1–4 контекст ещё не существует, поэтому бин-слушатель не может быть зарегистрирован.

**Способ 2: META-INF/spring.factories (для ранних событий 1–4)**

```properties
# src/main/resources/META-INF/spring.factories
org.springframework.context.ApplicationListener=\
  com.example.MyEarlyStartupListener
```

```java
public class MyEarlyStartupListener implements ApplicationListener<ApplicationEnvironmentPreparedEvent> {
    @Override
    public void onApplicationEvent(ApplicationEnvironmentPreparedEvent event) {
        // Вызывается до создания Context
        // Можно читать Environment, добавлять PropertySource-ы
        ConfigurableEnvironment env = event.getEnvironment();
    }
}
```

**Способ 3: Программная регистрация**

```java
SpringApplication app = new SpringApplication(MyApplication.class);
app.addListeners(new MyStartingListener(), new MyEnvironmentListener());
app.run(args);
```

**Способ 4: SpringApplicationBuilder**

```java
new SpringApplicationBuilder(MyApplication.class)
    .listeners(new MyApplicationListener())
    .run(args);
```

**Когда что использовать**

| Событие | Где регистрировать |
|---|---|
| 1–4 (до создания Context) | `spring.factories` или `app.addListeners()` |
| 5–11 (после создания Context) | `@EventListener` на `@Component`-бине |
| `ApplicationReadyEvent` | `@EventListener` — самое популярное место для «после запуска» логики |
| `ApplicationFailedEvent` | `spring.factories` — нужен до того, как Context умер |

**Важные нюансы**

1. `@EventListener`-методы по умолчанию вызываются **синхронно** в потоке публикующего события. Длительные задачи следует выносить в `@Async` или выполнять в `CommandLineRunner`.
2. При наличии иерархии контекстов (parent/child) событие, опубликованное в child-context, доставляется и в parent-context. Чтобы обработать событие только от конкретного контекста, инжектируйте `ApplicationContext` и сравнивайте.
3. `AvailabilityChangeEvent` с `ReadinessState.REFUSING_TRAFFIC` также публикуется при `graceful shutdown` — это сигнал для балансировщика убрать экземпляр из ротации.

