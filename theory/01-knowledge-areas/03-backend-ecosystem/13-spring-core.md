# Spring Framework (Core, IoC, AOP)

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по Spring →](../interview-questions/spring-01.md)
> **Связанные области:** [[14-spring-boot]], [[10-design-patterns]], [[16-jpa-hibernate]]

## Что это и зачем

Spring Framework — стандарт де-факто для разработки backend-приложений на Java. Его ядро —
инверсия управления (IoC) и внедрение зависимостей (DI) через контейнер бинов, а также
аспектно-ориентированное программирование (AOP). Понимание жизненного цикла бинов, скоупов,
конфигурации и механизма AOP обязательно для любого Java-разработчика в энтерпрайзе.

IoC означает, что объекты не создают зависимости самостоятельно — их предоставляет контейнер.
Это делает код легко тестируемым, слабо связанным и легко заменяемым без изменения бизнес-логики.
AOP дополняет IoC, вынося сквозную функциональность (логирование, транзакции, безопасность) в
отдельные модули — аспекты.

---

## Ключевые подтемы

### 1. IoC-контейнер: BeanFactory и ApplicationContext

Оба интерфейса являются IoC-контейнерами, но отличаются возможностями.

**`BeanFactory`** — базовый низкоуровневый интерфейс. Поддерживает только ленивую инициализацию
бинов и минимальный набор функций. Использовать напрямую практически не приходится.

**`ApplicationContext`** — расширение `BeanFactory` с дополнительными возможностями:
- интеграция с AOP и публикация событий приложения;
- поддержка интернационализации (`MessageSource`);
- загрузка ресурсов из файловой системы и classpath;
- автоматическая регистрация `BeanPostProcessor` и `BeanFactoryPostProcessor`.

Типичные реализации `ApplicationContext`:
- `ClassPathXmlApplicationContext` — XML-конфигурация из classpath;
- `AnnotationConfigApplicationContext` — Java-конфигурация;
- `WebApplicationContext` / `AnnotationConfigWebApplicationContext` — для web-приложений.

Источник: [docs.spring.io — The IoC Container](https://docs.spring.io/spring-framework/reference/core/beans.html)

---

### 2. Способы конфигурации контейнера

Spring поддерживает три подхода, которые можно совмещать в одном приложении.

#### XML-конфигурация (классический подход)
```xml
<bean id="userService" class="com.example.UserService">
    <constructor-arg ref="userRepository"/>
    <property name="timeout" value="30"/>
</bean>
```

#### Аннотации + component scanning
```java
@Configuration
@ComponentScan("com.example")
public class AppConfig { }

@Service
public class UserService {
    private final UserRepository repository;
    // конструктор автоматически используется для DI
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

#### Java-конфигурация (`@Configuration` + `@Bean`)
```java
@Configuration
public class AppConfig {
    @Bean
    public UserService userService(UserRepository repo) {
        return new UserService(repo);
    }
}
```

`@Configuration` гарантирует, что повторные вызовы `@Bean`-методов внутри класса возвращают
один и тот же singleton-экземпляр (CGLIB-прокси). `@Component` такого поведения не даёт.

Источник: [docs.spring.io — Java-based Container Configuration](https://docs.spring.io/spring-framework/reference/core/beans/java.html)

---

### 3. Внедрение зависимостей (DI)

Spring поддерживает три способа внедрения зависимостей.

#### Через конструктор (рекомендуется)
```java
@Service
public class OrderService {
    private final PaymentService paymentService;
    private final InventoryService inventoryService;

    // @Autowired не нужен если конструктор один (Spring 4.3+)
    public OrderService(PaymentService paymentService,
                        InventoryService inventoryService) {
        this.paymentService = paymentService;
        this.inventoryService = inventoryService;
    }
}
```
Преимущества: поля можно объявить `final`, зависимости явны, тестирование без Spring.

#### Через сеттер
```java
@Service
public class ReportService {
    private DataSource dataSource;

    @Autowired
    public void setDataSource(DataSource dataSource) {
        this.dataSource = dataSource;
    }
}
```
Подходит для опциональных зависимостей или зависимостей, которые можно переназначить.

#### Через поле (field injection)
```java
@Service
public class CatalogService {
    @Autowired
    private ProductRepository repository;
}
```
Официальная документация Spring не рекомендует этот подход: скрывает зависимости, усложняет
тестирование, делает невозможным объявление `final`.

#### Разрешение неоднозначностей

| Аннотация | Назначение |
|-----------|-----------|
| `@Primary` | Отмечает предпочтительный бин при наличии нескольких кандидатов |
| `@Qualifier("name")` | Выбирает конкретный бин по имени |
| `@Resource(name="name")` | JSR-250, внедряет по имени бина |

```java
@Bean @Primary
public DataSource primaryDataSource() { ... }

@Bean("auditDs")
public DataSource auditDataSource() { ... }

// В месте внедрения:
@Autowired @Qualifier("auditDs")
private DataSource auditDs;
```

Источник: [docs.spring.io — Dependencies](https://docs.spring.io/spring-framework/reference/core/beans/dependencies.html)

---

### 4. Жизненный цикл бина

Полный порядок событий при создании singleton-бина:

1. **Инстанцирование** — вызов конструктора;
2. **Внедрение зависимостей** — заполнение полей/сеттеров;
3. **Обработка Aware-интерфейсов** — вызов `setBeanName()`, `setApplicationContext()` и т.д.;
4. **`BeanPostProcessor.postProcessBeforeInitialization()`**;
5. **Инициализация:**
   - методы с `@PostConstruct` (JSR-250),
   - `InitializingBean.afterPropertiesSet()`,
   - кастомный `initMethod` из `@Bean(initMethod="...")`;
6. **`BeanPostProcessor.postProcessAfterInitialization()`** — здесь создаются AOP-прокси;
7. **Использование бина**;
8. **Уничтожение (при закрытии контекста):**
   - методы с `@PreDestroy` (JSR-250),
   - `DisposableBean.destroy()`,
   - кастомный `destroyMethod`.

Если несколько механизмов инициализации настроены одновременно, они выполняются именно в
порядке, указанном выше. Аналогично для уничтожения.

```java
@Component
public class CacheService implements InitializingBean, DisposableBean {

    @PostConstruct
    public void onPostConstruct() { /* вызывается первым */ }

    @Override
    public void afterPropertiesSet() { /* вызывается вторым */ }

    @Override
    public void destroy() { /* при закрытии контекста */ }

    @PreDestroy
    public void onPreDestroy() { /* вызывается перед destroy() */ }
}
```

**Предупреждение**: `@PostConstruct` выполняется внутри блокировки создания singleton-а. Долгие
или блокирующие операции в нём могут вызвать дедлок. Для таких случаев используйте
`SmartInitializingSingleton.afterSingletonsInstantiated()` или
`@EventListener(ContextRefreshedEvent.class)`.

Источник: [docs.spring.io — Customizing the Nature of a Bean](https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html)

---

### 5. Скоупы бинов

| Скоуп | Создаётся | Уничтожается | `@PreDestroy` | Применение |
|-------|-----------|--------------|---------------|-----------|
| `singleton` | При инициализации контекста | При закрытии контекста | Вызывается | Stateless-сервисы (по умолчанию) |
| `prototype` | При каждом запросе | Контейнер не управляет | Не вызывается | Stateful-объекты |
| `request` | На каждый HTTP-запрос | После завершения запроса | Вызывается | Данные конкретного запроса |
| `session` | На каждую HTTP-сессию | По истечении сессии | Вызывается | Состояние пользователя |
| `application` | На ServletContext | При остановке приложения | Вызывается | Глобальные настройки |
| `websocket` | На каждую WebSocket-сессию | При закрытии соединения | Вызывается | Реал-тайм данные |

Удобные аннотации для web-скоупов: `@RequestScope`, `@SessionScope`, `@ApplicationScope`.

#### Проблема: singleton с зависимостью на prototype

Если singleton-бин содержит поле с prototype-бином, Spring инжектирует prototype один раз при
создании singleton-а — все последующие вызовы используют тот же экземпляр. Решения:

```java
// Решение 1: ObjectProvider (рекомендуется)
@Service
public class ReportGenerator {
    @Autowired
    private ObjectProvider<ReportContext> contextProvider;

    public Report generate() {
        ReportContext ctx = contextProvider.getObject(); // новый экземпляр каждый раз
        return ctx.build();
    }
}

// Решение 2: scoped proxy
@Component
@Scope(value = "prototype", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ReportContext { ... }
```

Источник: [docs.spring.io — Bean Scopes](https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html)

---

### 6. ApplicationContext: события и расширения

#### Встроенные события

| Событие | Когда публикуется |
|---------|------------------|
| `ContextRefreshedEvent` | После полной инициализации контекста |
| `ContextStartedEvent` | После вызова `context.start()` |
| `ContextStoppedEvent` | После вызова `context.stop()` |
| `ContextClosedEvent` | При закрытии контекста |
| `RequestHandledEvent` | После обработки HTTP-запроса (только web) |

#### Пользовательские события

```java
// Событие
public class OrderPlacedEvent extends ApplicationEvent {
    private final Long orderId;
    public OrderPlacedEvent(Object source, Long orderId) {
        super(source);
        this.orderId = orderId;
    }
    public Long getOrderId() { return orderId; }
}

// Публикация
@Service
public class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher;

    public void placeOrder(Order order) {
        // ... сохранение
        publisher.publishEvent(new OrderPlacedEvent(this, order.getId()));
    }
}

// Слушатель
@Component
public class NotificationListener {
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        // отправка уведомления
    }

    @EventListener
    @Async  // асинхронная обработка
    public void onOrderPlacedAsync(OrderPlacedEvent event) { ... }
}
```

#### Aware-интерфейсы

| Интерфейс | Что внедряется |
|-----------|---------------|
| `ApplicationContextAware` | `ApplicationContext` |
| `ApplicationEventPublisherAware` | `ApplicationEventPublisher` |
| `BeanNameAware` | Имя бина в контейнере |
| `EnvironmentAware` | `Environment` |
| `MessageSourceAware` | `MessageSource` |
| `ResourceLoaderAware` | `ResourceLoader` |

Источник: [docs.spring.io — Additional Capabilities of the ApplicationContext](https://docs.spring.io/spring-framework/reference/core/beans/context-introduction.html)

---

### 7. AOP: аспекты, advice, pointcut

Spring AOP работает через проксирование и перехватывает вызовы методов управляемых бинов.

#### Основные понятия

- **Aspect** — модуль, инкапсулирующий сквозную логику (`@Aspect`).
- **Join point** — конкретная точка выполнения (в Spring AOP — всегда вызов метода).
- **Pointcut** — выражение, отбирающее join points.
- **Advice** — действие, выполняемое в выбранных точках.
- **Weaving** — связывание аспектов с основным кодом (в Spring — во время выполнения через прокси).

#### Типы advice

| Тип | Аннотация | Описание |
|-----|-----------|---------|
| Before | `@Before` | Выполняется до метода |
| After (finally) | `@After` | После метода в любом случае |
| After returning | `@AfterReturning` | После успешного возврата |
| After throwing | `@AfterThrowing` | При исключении |
| Around | `@Around` | Полный контроль над вызовом |

```java
@Aspect
@Component
public class AuditAspect {

    // Pointcut: все public-методы в пакете service
    @Pointcut("execution(public * com.example.service.*.*(..))")
    public void serviceLayer() {}

    @Before("serviceLayer()")
    public void logCall(JoinPoint jp) {
        log.info("Calling {}", jp.getSignature());
    }

    @AfterReturning(pointcut = "serviceLayer()", returning = "result")
    public void logResult(Object result) {
        log.info("Result: {}", result);
    }

    @AfterThrowing(pointcut = "serviceLayer()", throwing = "ex")
    public void logException(Exception ex) {
        log.error("Exception: {}", ex.getMessage());
    }

    @Around("serviceLayer()")
    public Object measureTime(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed();
        } finally {
            log.info("Duration: {}ms", System.currentTimeMillis() - start);
        }
    }
}
```

Включение AspectJ auto proxy:
```java
@Configuration
@EnableAspectJAutoProxy
public class AopConfig {}
```

#### Механизмы проксирования

| Механизм | Когда используется | Требование |
|----------|--------------------|-----------|
| **JDK Dynamic Proxy** | Бин реализует хотя бы один интерфейс | Прокси реализует тот же интерфейс |
| **CGLIB** | Бин не реализует интерфейс или `proxyTargetClass=true` | Класс не должен быть `final` |

```java
// Принудительное использование CGLIB для всех бинов:
@EnableAspectJAutoProxy(proxyTargetClass = true)
```

Spring Boot начиная с версии 2.0 по умолчанию использует CGLIB (`spring.aop.proxy-target-class=true`).

#### Ограничения Spring AOP

1. **Только public-методы** — private и package-private не перехватываются.
2. **Self-invocation** — вызов метода внутри того же класса обходит прокси:
   ```java
   @Service
   public class InvoiceService {
       @Transactional
       public void processAll() {
           process(); // AOP НЕ сработает — вызов идёт напрямую, минуя прокси
       }
       @Transactional(propagation = REQUIRES_NEW)
       public void process() { ... }
   }
   ```
   Решение: вынести метод в отдельный бин, либо использовать AspectJ compile-time weaving.
3. **Только бины Spring** — объекты, созданные через `new`, не проксируются.
4. **`final`-классы и методы** — CGLIB не может создать подкласс.

Источник: [docs.spring.io — Aspect Oriented Programming with Spring](https://docs.spring.io/spring-framework/reference/core/aop.html)

---

### 8. Управление транзакциями (`@Transactional`)

Spring реализует декларативное управление транзакциями через AOP. `@Transactional` может быть
применена на уровне метода или класса (применяется ко всем public-методам класса).

#### Атрибуты по умолчанию

| Атрибут | По умолчанию | Описание |
|---------|-------------|---------|
| `propagation` | `REQUIRED` | Поведение при наличии/отсутствии активной транзакции |
| `isolation` | `DEFAULT` | Уровень изоляции (берётся из СУБД) |
| `readOnly` | `false` | Подсказка для оптимизации |
| `timeout` | -1 (нет) | Таймаут в секундах |
| `rollbackFor` | `RuntimeException`, `Error` | Классы исключений для rollback |
| `noRollbackFor` | — | Исключения, при которых rollback НЕ делается |

#### Уровни propagation

| Propagation | Поведение |
|-------------|-----------|
| `REQUIRED` (по умолчанию) | Присоединяется к существующей транзакции; создаёт новую, если нет |
| `REQUIRES_NEW` | Всегда создаёт новую физическую транзакцию; приостанавливает текущую |
| `NESTED` | Вложенная транзакция через savepoint (только JDBC) |
| `SUPPORTS` | Участвует в транзакции если она есть; без транзакции если её нет |
| `MANDATORY` | Требует существующей транзакции; бросает исключение если нет |
| `NOT_SUPPORTED` | Всегда выполняется без транзакции; приостанавливает текущую |
| `NEVER` | Запрещает транзакцию; бросает исключение если она есть |

```java
@Service
@Transactional(readOnly = true)  // по умолчанию для всех методов класса
public class OrderQueryService {

    public List<Order> findAll() { ... }  // унаследует readOnly = true

    @Transactional(
        propagation = Propagation.REQUIRES_NEW,
        rollbackFor = PaymentException.class,
        timeout = 30
    )
    public void placeOrder(Order order) { ... }  // переопределяет настройки класса
}
```

#### Важные ограничения

- `@Transactional` работает только на бинах Spring (через AOP-прокси).
- **Self-invocation** обходит транзакционный прокси — то же ограничение, что и у AOP.
- По умолчанию checked-исключения НЕ вызывают rollback. Нужно явно указывать
  `rollbackFor = MyCheckedException.class` если нужно.
- `REQUIRES_NEW` создаёт отдельное соединение с БД — при высокой нагрузке может исчерпать пул.

Источник: [docs.spring.io — Using @Transactional](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

---

### 9. BeanPostProcessor и расширение контейнера

`BeanPostProcessor` — ключевой механизм расширения Spring. Все AOP-прокси, валидация аннотаций,
обработка `@Autowired` и `@Value` реализованы через встроенные `BeanPostProcessor`-ы.

```java
@Component
public class LoggingBeanPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        // вызывается до @PostConstruct
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        // вызывается после @PostConstruct — здесь создаются AOP-прокси
        log.info("Bean ready: {}", beanName);
        return bean; // можно вернуть обёртку
    }
}
```

`BeanFactoryPostProcessor` позволяет изменять метаданные бинов до их создания (например,
`PropertySourcesPlaceholderConfigurer` обрабатывает `${...}`-плейсхолдеры).

---

## Достоверные источники

1. **[Spring Framework Reference — Core (IoC Container)](https://docs.spring.io/spring-framework/reference/core/beans.html)** —
   официальная документация: BeanFactory, ApplicationContext, DI, жизненный цикл, скоупы.
   Первичный источник истины для всего, что касается IoC в Spring.

2. **[Spring Framework Reference — AOP](https://docs.spring.io/spring-framework/reference/core/aop.html)** —
   официальная документация по AOP: аспекты, advice, pointcut, проксирование (JDK vs CGLIB),
   ограничения Spring AOP vs полноценного AspectJ.

3. **[Spring Framework Reference — Declarative Transaction Management](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)** —
   официальная документация по `@Transactional`: все атрибуты, уровни propagation, правила rollback.

4. **[Spring Framework Reference — Bean Scopes](https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html)** —
   официальная документация по скоупам: описание всех шести скоупов, особенности prototype,
   решение проблемы singleton + prototype через ObjectProvider.

5. **[Baeldung — Spring Tutorial](https://www.baeldung.com/spring-tutorial)** —
   крупнейшая база практических статей по Spring. Каждая статья снабжена рабочими примерами
   и ссылками на официальную документацию; статьи регулярно обновляются.

6. **[Spring Guides](https://spring.io/guides)** —
   официальные пошаговые руководства от команды Spring. Показывают рекомендуемые паттерны
   использования фреймворка в актуальных версиях.
