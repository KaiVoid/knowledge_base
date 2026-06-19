# Spring Framework (Core, IoC, AOP) — часть 1 из 3

> Вопросы 1–20 (в части: 20). Всего в разделе: 51.
> Область знаний: [../theory/01-knowledge-areas/03-backend-ecosystem/13-spring-core.md](../theory/01-knowledge-areas/03-backend-ecosystem/13-spring-core.md)
> Правила: [RULES.md](RULES.md)
> Части: **ч.1** · [ч.2](spring-02.md) · [ч.3](spring-03.md)

---
### Вопрос 1. Что такое IoC (Inversion of Control) и как Spring реализует этот принцип?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Introduction to the Spring IoC Container and Beans — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/introduction.html)

IoC (Inversion of Control, инверсия управления) — принцип проектирования, при котором управление созданием объектов и управление зависимостями передаётся от самого объекта внешнему контейнеру (фреймворку). Специализированной формой IoC является внедрение зависимостей (Dependency Injection, DI): объекты объявляют свои зависимости через аргументы конструктора, аргументы фабричного метода или свойства (сеттеры), устанавливаемые после создания экземпляра; контейнер инжектирует эти зависимости при создании бина.

Такой подход является полной инверсией традиционного подхода, при котором бин сам управляет созданием или поиском своих зависимостей с помощью прямого конструирования классов или паттерна Service Locator.

Spring реализует IoC через два ключевых пакета: `org.springframework.beans` и `org.springframework.context`. Центральным интерфейсом является `BeanFactory`, а его расширением — `ApplicationContext`, который добавляет поддержку AOP, интернационализацию, публикацию событий и контексты уровня приложения (например, `WebApplicationContext`).

Объекты, которые составляют основу приложения и управляются IoC-контейнером Spring, называются **бинами** (beans). Бин — это объект, который создаётся, собирается (получает зависимости) и управляется IoC-контейнером Spring.

#### Ответ от Claude

**IoC (Inversion of Control)** — принцип, согласно которому управление созданием объектов и их жизненным циклом передаётся от самого кода приложения внешнему контейнеру или фреймворку. До IoC код сам создавал нужные зависимости через `new`. При IoC код лишь объявляет, что ему нужно, а контейнер сам создаёт и передаёт эти зависимости.

**Dependency Injection (DI)** — конкретная реализация принципа IoC, при которой зависимости «вталкиваются» (inject) в объект снаружи, а не создаются им самостоятельно.

**Как Spring реализует IoC:**

1. **IoC-контейнер** — ядро Spring. Он читает метаданные конфигурации (XML, аннотации `@Bean`/`@Component`, Java-конфигурация `@Configuration`) и на их основе создаёт, настраивает и собирает бины.
2. **BeanFactory** (`org.springframework.beans.factory.BeanFactory`) — базовый интерфейс контейнера: умеет создавать и возвращать бины по имени/типу.
3. **ApplicationContext** (`org.springframework.context.ApplicationContext`) — расширение `BeanFactory` с дополнительными возможностями: AOP, события, интернационализация, поддержка веб-контекстов.
4. **Бин (Bean)** — любой объект, зарегистрированный в контейнере и управляемый им (создание, настройка, уничтожение).

**Преимущества:**
- Слабая связанность (loose coupling) — объект не знает, как создаётся его зависимость.
- Тестируемость — можно подменить реальную зависимость моком.
- Гибкость конфигурации — реализации можно менять без изменения потребляющего кода.

**Пример:** без IoC класс `OrderService` создаёт `PaymentService` сам: `new PaymentService()`. С IoC Spring сам создаёт `PaymentService` и передаёт его в конструктор `OrderService` — объект получает зависимость готовой.

---

### Вопрос 2. Какие три вида внедрения зависимостей поддерживает Spring? Какой из них считается предпочтительным и почему?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Dependency Injection — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)

Официальная документация Spring описывает два основных механизма внедрения зависимостей:

1. **Constructor-based DI (внедрение через конструктор)** — контейнер вызывает конструктор с аргументами, каждый из которых представляет нужную зависимость. Позволяет создавать неизменяемые (immutable) объекты и гарантирует, что обязательные зависимости не будут `null`.

2. **Setter-based DI (внедрение через сеттер)** — контейнер вызывает сеттеры объекта после создания экземпляра. Подходит для опциональных зависимостей, которым можно задать значение по умолчанию.

Команда Spring рекомендует **внедрение через конструктор**, поскольку оно позволяет реализовывать компоненты как неизменяемые объекты и гарантирует, что обязательные зависимости не окажутся `null`. Компонент, использующий конструкторное внедрение, всегда возвращается клиентскому коду в полностью инициализированном состоянии.

Внедрение через сеттер следует применять главным образом для опциональных зависимостей. При этом документация оговаривает: если конструктор принимает слишком много аргументов — это сигнал, что у класса слишком много обязанностей и его стоит разбить.

#### Ответ от Claude

Spring поддерживает **три вида** внедрения зависимостей (хотя официальная документация Spring 6+ явно описывает два — конструктор и сеттер — полевое внедрение реализуется через инфраструктуру `@Autowired` и широко используется на практике):

**1. Constructor Injection (через конструктор)**
```java
@Component
public class OrderService {
    private final PaymentService paymentService;

    @Autowired // необязательно при одном конструкторе в Spring 4.3+
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**2. Setter Injection (через сеттер)**
```java
@Component
public class OrderService {
    private PaymentService paymentService;

    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**3. Field Injection (через поле, с `@Autowired`)**
```java
@Component
public class OrderService {
    @Autowired
    private PaymentService paymentService;
}
```

**Предпочтительный способ: Constructor Injection.**

Причины (из официальной документации Spring и широко принятой практики):

| Критерий | Constructor | Setter | Field |
|---|---|---|---|
| Immutability (поле `final`) | Да | Нет | Нет |
| Null safety | Да (NPE при старте) | Нет | Нет |
| Явная декларация зависимостей | Да | Частично | Нет |
| Тестируемость без контейнера | Да (чистый `new`) | Да | Нет (нужен рефлексия/контейнер) |
| Обнаружение циклических зависимостей | При старте (fail-fast) | Позже | Позже |

**Почему field injection не рекомендован:**
- Зависит от рефлексии — нарушает инкапсуляцию.
- Нельзя объявить поле `final` — объект изменяем.
- Невозможно использовать класс без IoC-контейнера (сложно юнит-тестировать).
- IntelliJ IDEA и Spring Team показывают предупреждение на field injection.

**Практическое правило:** constructor injection — для обязательных зависимостей; setter injection — для опциональных (с разумными дефолтами); field injection — избегать в production-коде.

---

### Вопрос 3. В чём разница между BeanFactory и ApplicationContext? Когда уместно использовать BeanFactory?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [The BeanFactory API — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/beanfactory.html)

`BeanFactory` предоставляет базовый механизм конфигурирования для управления любыми объектами. `ApplicationContext` является подинтерфейсом `BeanFactory` и добавляет:

- встроенное управление жизненным циклом;
- автоматическую регистрацию `BeanPostProcessor` и `BeanFactoryPostProcessor`;
- удобный доступ к `MessageSource` (интернационализация);
- встроенную публикацию `ApplicationEvent`.

Документация настоятельно рекомендует использовать `ApplicationContext` для большинства сценариев:

> «You should use an ApplicationContext unless you have a good reason for not doing so, with GenericApplicationContext and its subclass AnnotationConfigApplicationContext as the common implementations for custom bootstrapping.»

Если используется голый `BeanFactory` (например, `DefaultListableBeanFactory`), пост-процессоры нужно регистрировать вручную:

```java
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();
// ... заполняем определениями бинов
factory.addBeanPostProcessor(new AutowiredAnnotationBeanPostProcessor());
factory.addBeanPostProcessor(new MyBeanPostProcessor());
```

Применять `BeanFactory` напрямую стоит только тогда, когда нужен **полный ручной контроль над обработкой бинов** — например, при интеграции со сторонними фреймворками или в ресурсно-ограниченных средах.

#### Ответ от Claude

**BeanFactory** — базовый интерфейс IoC-контейнера Spring. Обеспечивает создание, настройку и получение бинов по имени или типу. Это «низкоуровневый» контейнер с минимальным функционалом.

**ApplicationContext** — расширение `BeanFactory` (субинтерфейс). Добавляет возможности уровня предприятия.

**Сравнительная таблица:**

| Функция | BeanFactory | ApplicationContext |
|---|---|---|
| Создание и настройка бинов | Да | Да |
| Lazy loading (по требованию) | Да (по умолчанию) | Нет (eager по умолчанию) |
| Eager loading при старте | Нет | Да (все синглтоны) |
| Автоматическая регистрация `BeanPostProcessor` | Нет (вручную) | Да |
| Автоматическая регистрация `BeanFactoryPostProcessor` | Нет (вручную) | Да |
| Интернационализация (`MessageSource`) | Нет | Да |
| Публикация событий (`ApplicationEvent`) | Нет | Да |
| Поддержка AOP | Ограничена | Полная |
| Поддержка `@Transactional`, `@Async`, `@Scheduled` | Нет | Да |
| Поддержка веб-контекстов (`WebApplicationContext`) | Нет | Да |
| Поддержка всех scope-ов бинов | Только Singleton, Prototype | Все (включая Request, Session) |

**Когда уместно использовать BeanFactory:**

Практически никогда в современных приложениях. Официальная документация Spring говорит: «Используйте `ApplicationContext`, если нет веских причин не делать этого». Единственные обоснованные случаи для `BeanFactory` (`DefaultListableBeanFactory`):
- Крайне ресурсо-ограниченные среды (embedded-устройства, апплеты — исторически), где важна экономия памяти.
- Встраивание Spring в сторонний фреймворк с полным ручным контролем над обработкой бинов.
- Специализированные интеграционные сценарии, требующие точного управления порядком регистрации пост-процессоров.

**Вывод:** в любом стандартном Spring/Spring Boot приложении всегда используется `ApplicationContext` (чаще всего `AnnotationConfigApplicationContext` или `AnnotationConfigWebApplicationContext`). `BeanFactory` — это деталь реализации, которую разработчик обычно не трогает напрямую.
### Вопрос 4. Что такое Spring-бин? Какие способы объявить бин в Spring-приложении вы знаете?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Bean Overview :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/definition.html)

Spring-бин — это объект, который создаётся, собирается и управляется Spring IoC-контейнером. Внутри контейнер представляет каждый бин как объект `BeanDefinition`, содержащий метаданные: имя класса реализации, конфигурацию поведения (скоуп, lifecycle-коллбэки), ссылки на зависимости и прочие настройки.

Существуют три основных способа объявить бин:

1. **XML-конфигурация** — определение через элемент `<bean/>` в XML-файле:
   ```xml
   <bean id="exampleBean" class="examples.ExampleBean"/>
   ```

2. **Аннотация `@Bean`** — метод в классе, помеченном `@Configuration`, возвращает экземпляр бина:
   ```java
   @Configuration
   public class AppConfig {
       @Bean
       public MyService myService() {
           return new MyServiceImpl();
       }
   }
   ```
   Имя бина по умолчанию совпадает с именем метода.

3. **Стереотипные аннотации + classpath-сканирование** — классы, помеченные `@Component` (и его специализациями), автоматически регистрируются как бины при включённом `@ComponentScan`:
   ```java
   @Service
   public class UserService { }
   ```

#### Ответ от Claude

**Что такое Spring-бин**

Spring-бин — это объект, жизненным циклом которого управляет Spring IoC-контейнер (`ApplicationContext` / `BeanFactory`). Контейнер создаёт бин, внедряет в него зависимости, вызывает lifecycle-коллбэки и при завершении работы уничтожает его. Внутренне описание каждого бина хранится в объекте `BeanDefinition`.

**Способы объявить бин**

| Способ | Механизм | Когда использовать |
|---|---|---|
| XML-конфигурация | `<bean id="..." class="..."/>` в XML, загружается через `ClassPathXmlApplicationContext` | Легаси-проекты, интеграция со сторонними фреймворками |
| Java-конфигурация (`@Bean`) | Метод в `@Configuration`-классе, аннотированный `@Bean` | Создание бинов из сторонних классов (нет доступа к исходникам), программная конфигурация |
| Стереотипные аннотации | `@Component`, `@Service`, `@Repository`, `@Controller` на классе + `@ComponentScan` | Собственные классы приложения |
| `@Import` | Подключение другого `@Configuration`-класса или `ImportSelector` | Модульная конфигурация |
| Программная регистрация | `BeanDefinitionRegistry.registerBeanDefinition(...)` | Динамическая регистрация во время старта |

**Детали стереотипных аннотаций**

`@Service`, `@Repository`, `@Controller` — это составные аннотации, каждая из которых мета-аннотирована `@Component`. Они несут дополнительную семантику: `@Repository` активирует трансляцию исключений Spring Data; `@Controller` делает класс обработчиком HTTP-запросов в MVC.

Имя бина по умолчанию при автосканировании — имя класса с первой строчной буквой (`UserService` → `userService`). Явное имя задаётся через атрибут: `@Service("myUserService")`.

**Способы с `@Bean`**

Метод `@Bean` может принимать параметры — Spring автоматически разрешит их как зависимости. `initMethod` и `destroyMethod` задают коллбэки жизненного цикла. Если бин реализует публичные методы `close()` или `shutdown()`, Spring автоматически зарегистрирует их как destroy-коллбэки (поведение можно отключить: `@Bean(destroyMethod = "")`).

---

### Вопрос 5. Перечислите скоупы бинов в Spring. Чем singleton отличается от prototype?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Bean Scopes :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html)

Spring поддерживает шесть скоупов. Четыре из них доступны только в web-aware контексте (`WebApplicationContext`):

| Скоуп | Описание |
|---|---|
| `singleton` | (по умолчанию) Один общий экземпляр на Spring IoC-контейнер |
| `prototype` | Новый экземпляр при каждом запросе из контейнера |
| `request` | Один экземпляр на HTTP-запрос (только web) |
| `session` | Один экземпляр на HTTP-сессию (только web) |
| `application` | Один экземпляр на `ServletContext` (только web) |
| `websocket` | Один экземпляр на WebSocket-сессию (только web) |

Ключевое различие singleton и prototype: при singleton контейнер кеширует единственный экземпляр и возвращает его при каждом обращении; при prototype создаётся новый объект. Важно: контейнер вызывает destroy-коллбэки только для singleton-бинов. Для prototype-бинов Spring вызывает init-коллбэки, но не destroy — клиентский код сам отвечает за освобождение ресурсов.

#### Ответ от Claude

**Полный перечень скоупов**

| Скоуп | Аннотация | Описание |
|---|---|---|
| `singleton` | (по умолчанию) | Один экземпляр на ApplicationContext; кешируется и повторно используется |
| `prototype` | `@Scope("prototype")` | Новый экземпляр при каждом `getBean()` или инжекции зависимости |
| `request` | `@RequestScope` | Один экземпляр на HTTP-запрос; живёт от начала до конца запроса |
| `session` | `@SessionScope` | Один экземпляр на HTTP-сессию |
| `application` | `@ApplicationScope` | Один экземпляр на `ServletContext`; практически синглтон, но привязан к lifecycle веб-контекста |
| `websocket` | `@Scope("websocket")` | Один экземпляр на WebSocket-сессию |

Кастомный скоуп можно реализовать, имплементировав интерфейс `org.springframework.beans.factory.config.Scope` и зарегистрировав его через `ConfigurableBeanFactory.registerScope()`.

**Singleton vs Prototype: подробное сравнение**

| Аспект | Singleton | Prototype |
|---|---|---|
| Количество экземпляров | Один на контейнер | Новый при каждом запросе |
| Кеширование | Да, экземпляр хранится в контейнере | Нет |
| Вызов init-коллбэков (`@PostConstruct`, `afterPropertiesSet`) | Да | Да |
| Вызов destroy-коллбэков (`@PreDestroy`, `destroy`) | Да | **Нет** |
| Ответственность за освобождение ресурсов | Spring | Клиентский код |
| Потокобезопасность | Требует от бина быть stateless или потокобезопасным | Каждый поток получает свой экземпляр |
| Рекомендуемое применение | Stateless-сервисы, DAO, утилиты | Stateful-объекты (например, командные объекты) |

**Проблема инжекции prototype в singleton**

Если singleton-бин зависит от prototype-бина, Spring инжектирует prototype-экземпляр **ровно один раз** при создании singleton. После этого singleton всегда использует один и тот же экземпляр, что нивелирует смысл prototype-скоупа.

Решения:
- **Method Injection** (абстрактный метод + CGLIB-прокси от Spring).
- **`ApplicationContext.getBean()`** вызывать каждый раз явно (нарушает IoC, не рекомендуется).
- **`ObjectProvider<T>`** или **`Provider<T>`** (javax/jakarta inject) — рекомендуемый современный способ.
- **Scoped Proxy** (`@Scope(value="prototype", proxyMode=ScopedProxyMode.TARGET_CLASS)`).

**Объявление скоупа**

```java
// Java-конфигурация
@Bean
@Scope("prototype")
public Command command() { return new Command(); }

// Стереотип
@Component
@Scope("prototype")
public class Command { }

// XML
// <bean id="command" class="Command" scope="prototype"/>
```

---

### Вопрос 6. Опишите жизненный цикл бина в Spring: от создания до уничтожения. Какие callback-методы и интерфейсы можно использовать на каждом этапе?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Customizing the Nature of a Bean :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html)

Spring поддерживает три механизма для инициализационных и деструктивных коллбэков. Они выполняются в следующем порядке:

Инициализация:
1. Методы, аннотированные `@PostConstruct`
2. Метод `afterPropertiesSet()` интерфейса `InitializingBean`
3. Кастомный метод, заданный через `init-method` (XML) или `@Bean(initMethod = "...")`

Уничтожение:
1. Методы, аннотированные `@PreDestroy`
2. Метод `destroy()` интерфейса `DisposableBean`
3. Кастомный метод, заданный через `destroy-method` (XML) или `@Bean(destroyMethod = "...")`

`@PostConstruct` и `@PreDestroy` — рекомендуемый подход: они являются стандартом JSR-250 (пакет `jakarta.annotation`) и не привязывают код к Spring. Использование `InitializingBean` не рекомендуется, поскольку создаёт связность с Spring. Для расширенной обработки всех бинов применяется интерфейс `BeanPostProcessor`, методы которого вызываются до и после инициализационных коллбэков каждого бина.

#### Ответ от Claude

**Полная схема жизненного цикла бина**

```
1. Загрузка метаданных (BeanDefinition)
        |
2. Создание экземпляра (instantiation)
        |
3. Внедрение зависимостей (dependency injection)
   — setter injection, field injection, constructor injection
        |
4. Обработка Aware-интерфейсов
   — BeanNameAware.setBeanName()
   — BeanClassLoaderAware.setBeanClassLoader()
   — BeanFactoryAware.setBeanFactory()
   — ApplicationContextAware.setApplicationContext()
        |
5. BeanPostProcessor.postProcessBeforeInitialization()
   (вызывается для КАЖДОГО бина всеми зарегистрированными BeanPostProcessor)
        |
6. Инициализационные коллбэки (в порядке приоритета):
   a) @PostConstruct (JSR-250, обрабатывается CommonAnnotationBeanPostProcessor)
   b) InitializingBean.afterPropertiesSet()
   c) init-method / @Bean(initMethod="...")
        |
7. BeanPostProcessor.postProcessAfterInitialization()
        |
8. Бин готов к использованию
        |
   (контейнер работает)
        |
9. Деструктивные коллбэки (только для singleton; для prototype НЕ вызываются):
   a) @PreDestroy (JSR-250)
   b) DisposableBean.destroy()
   c) destroy-method / @Bean(destroyMethod="...")
```

**Callback-механизмы: детали**

| Механизм | Интерфейс / аннотация | Пакет | Привязка к Spring | Рекомендация |
|---|---|---|---|---|
| `@PostConstruct` | аннотация метода | `jakarta.annotation` | Нет (JSR-250) | Рекомендуется |
| `InitializingBean` | `afterPropertiesSet()` | `org.springframework.beans.factory` | Да | Не рекомендуется |
| `init-method` | атрибут XML / `@Bean(initMethod)` | — | Минимальная | Допустимо |
| `@PreDestroy` | аннотация метода | `jakarta.annotation` | Нет (JSR-250) | Рекомендуется |
| `DisposableBean` | `destroy()` | `org.springframework.beans.factory` | Да | Не рекомендуется |
| `destroy-method` | атрибут XML / `@Bean(destroyMethod)` | — | Минимальная | Допустимо |

**BeanPostProcessor**

`BeanPostProcessor` — ключевой интерфейс для перехвата и модификации экземпляров бинов до и после их инициализации. Применяется Spring внутренне для AOP-проксирования, валидации зависимостей и т.д.

```java
public interface BeanPostProcessor {
    // вызывается ПЕРЕД @PostConstruct и afterPropertiesSet
    Object postProcessBeforeInitialization(Object bean, String beanName);

    // вызывается ПОСЛЕ @PostConstruct и afterPropertiesSet
    Object postProcessAfterInitialization(Object bean, String beanName);
}
```

Если метод возвращает не null, контейнер заменяет оригинальный экземпляр возвращённым объектом (так работает CGLIB/JDK-проксирование в Spring AOP).

**Aware-интерфейсы**

Позволяют бину получить доступ к инфраструктуре контейнера:

- `BeanNameAware` — получить имя бина в контейнере
- `BeanFactoryAware` — получить ссылку на `BeanFactory`
- `ApplicationContextAware` — получить ссылку на `ApplicationContext`
- `EnvironmentAware` — получить `Environment` (properties, profiles)
- `ResourceLoaderAware`, `MessageSourceAware`, `ApplicationEventPublisherAware`

**Lifecycle и SmartLifecycle**

Для управления запуском и остановкой компонентов (не только инициализацией):

```java
public interface Lifecycle {
    void start();
    void stop();
    boolean isRunning();
}
```

`SmartLifecycle` дополнительно позволяет задать фазу запуска/остановки через `getPhase()` (меньшее значение — раньше стартует, позже останавливается) и поддерживает асинхронную остановку через `stop(Runnable callback)`.

**Важные нюансы**

- **Prototype-бины**: Spring вызывает init-коллбэки, но **не вызывает** destroy-коллбэки. Клиентский код сам должен освобождать ресурсы.
- **Graceful shutdown** в не-web приложениях: нужно явно зарегистрировать shutdown hook через `context.registerShutdownHook()`, иначе destroy-коллбэки не будут вызваны.
- **Порядок BeanPostProcessor**: если несколько `BeanPostProcessor` зарегистрированы, порядок их выполнения определяется интерфейсом `Ordered` / `PriorityOrdered`. Бины, реализующие `BeanPostProcessor`, создаются раньше обычных бинов и не подвергаются обработке другими `BeanPostProcessor`.
- **`@PostConstruct` и deadlock**: метод выполняется внутри блокировки создания синглтона. Длительные операции следует переносить в `SmartInitializingSingleton.afterSingletonsInstantiated()` или обработчик `ContextRefreshedEvent`.
### Вопрос 7. Как работает @Autowired? По какому критерию Spring выбирает бин для внедрения — по типу или по имени?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Using @Autowired :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html)

Аннотация `@Autowired` помечает конструктор, поле, сеттер-метод или конфигурационный метод как кандидат для внедрения зависимостей средствами Spring. Фактическое внедрение выполняется через `BeanPostProcessor` — конкретно через `AutowiredAnnotationBeanPostProcessor`. По умолчанию аннотированные поля и методы трактуются как обязательные зависимости; это поведение можно изменить атрибутом `required = false`.

Стратегия разрешения при нескольких кандидатах одного типа (в порядке приоритета):
1. Бин, помеченный `@Primary`, выбирается автоматически при отсутствии более точных указаний.
2. `@Qualifier` позволяет явно указать имя конкретного бина.
3. Если ни `@Primary`, ни `@Qualifier` не указаны, Spring выполняет **откат к сопоставлению по имени поля/параметра** с именем бина.

При внедрении в коллекции (`Array`, `List`, `Set`, `Map`) Spring инжектирует **все** подходящие по типу бины; для упорядочивания применяется `@Order`.

#### Ответ от Claude

`@Autowired` работает по принципу **«тип прежде всего, имя как запасной вариант»**.

**Как обрабатывается аннотация.**
Spring регистрирует `AutowiredAnnotationBeanPostProcessor`, который во время фазы `postProcessProperties` сканирует класс бина, находит все точки внедрения (`@Autowired`-поля, конструкторы, методы) и разрешает их из контекста.

**Алгоритм разрешения зависимости (шаги по убыванию приоритета):**

1. **Сопоставление по типу.** Spring собирает все бины, совместимые с объявленным типом поля/параметра. Если кандидат ровно один — он внедряется.
2. **`@Primary`.** Если кандидатов несколько, выбирается тот, что помечен `@Primary`.
3. **`@Qualifier`.** Если на точке внедрения указан `@Qualifier("name")`, Spring фильтрует кандидатов по этому имени — это самый высокоприоритетный явный способ.
4. **Откат по имени поля/параметра (name fallback).** Если тип дал несколько кандидатов и ни `@Primary`, ни `@Qualifier` не применимы, Spring сравнивает имя поля (или имя параметра конструктора/метода) с именами бинов. Совпадение разрешает неоднозначность. Начиная со Spring 6.1 для параметров конструктора/метода требуется флаг компилятора `-parameters`.
5. **Исключение `NoUniqueBeanDefinitionException`.** Если ни один из шагов 2–4 не устранил неоднозначность, Spring бросает исключение.

**Важные нюансы.**
- Если бин не найден вообще и `required = true` (по умолчанию), бросается `NoSuchBeanDefinitionException`.
- `@Autowired` можно поставить на конструктор (начиная со Spring 4.3, если конструктор единственный — аннотация необязательна).
- При внедрении `List<T>`, `Set<T>` или `Map<String, T>` Spring собирает все бины типа `T`; `@Qualifier` на коллекции фильтрует их по квалификатору.
- Специальные типы Spring-инфраструктуры (`ApplicationContext`, `Environment`, `BeanFactory` и др.) разрешаются автоматически без явной регистрации бина.

```java
// Поле: тип MovieCatalog → ищем бины типа MovieCatalog
@Autowired
private MovieCatalog movieCatalog;

// Откат по имени: если movieCatalogA — имя зарегистрированного бина, внедряется именно он
@Autowired
private MovieCatalog movieCatalogA;
```

---

### Вопрос 8. Для чего нужны аннотации @Qualifier и @Primary? В чём между ними разница и когда каждая из них применяется?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Fine-tuning Annotation-based Autowiring with @Primary or @Fallback :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired-primary.html)

Когда в контексте зарегистрировано несколько бинов одного типа, `@Autowired` не может выбрать один из них самостоятельно. `@Primary` решает эту проблему на уровне определения бина: бин, помеченный этой аннотацией, получает приоритет при autowiring на всех точках внедрения, где не указан `@Qualifier`. Например, если `firstMovieCatalog` помечен `@Primary`, любое поле `MovieCatalog` без дополнительных аннотаций получит именно его.

`@Qualifier("name")` указывается непосредственно на точке внедрения и адресует конкретный бин по имени или метке-квалификатору. Если одновременно присутствуют и `@Primary`, и `@Qualifier`, побеждает `@Qualifier`.

Начиная со Spring 6.2, есть симметричная `@Fallback` — помечает бин как «резервный», т. е. он используется только когда нет ни одного «обычного» кандидата.

#### Ответ от Claude

Обе аннотации решают проблему неоднозначности при наличии нескольких бинов одного типа, но делают это на разных уровнях абстракции.

**@Primary — глобальный «дефолт».**
Помечается на определении бина (`@Bean` или `@Component`). Говорит Spring: «если нет более конкретных инструкций, предпочти меня». Действует сразу на все точки внедрения типа. Удобен, когда одна реализация является основной, а остальные — специализированными или тестовыми.

```java
@Component
@Primary
public class DefaultPaymentService implements PaymentService { ... }

@Component
public class PaypalPaymentService implements PaymentService { ... }

// В любом классе без @Qualifier получим DefaultPaymentService:
@Autowired
private PaymentService paymentService;
```

**@Qualifier — точечный выбор.**
Указывается на точке внедрения (поле, параметр конструктора или метода). Позволяет разным потребителям получать разные бины одного типа. Значение по умолчанию совпадает с именем бина; можно задать произвольный квалификатор через XML-атрибут `<qualifier>` или одноимённую аннотацию на классе.

```java
@Autowired
@Qualifier("paypalPaymentService")
private PaymentService paymentService; // всегда PaypalPaymentService
```

**Приоритет: `@Qualifier` > `@Primary` > откат по имени.**

| Критерий | @Primary | @Qualifier |
|---|---|---|
| Место использования | На бине (определении) | На точке внедрения |
| Область действия | Глобальная (все точки без квалификатора) | Локальная (конкретная точка) |
| Гибкость | Низкая (один дефолт) | Высокая (разные бины в разных местах) |
| Типичный сценарий | Одна основная реализация | Несколько реализаций, нужна точная адресация |

**Когда что применять.**
- Используйте `@Primary`, когда у вас есть одна очевидно «основная» реализация и все (или большинство) потребителей должны получать именно её.
- Используйте `@Qualifier`, когда разным потребителям нужны разные реализации, или когда вы хотите явно задокументировать, какой именно бин внедряется.
- Если нужна максимальная читаемость, создайте собственную аннотацию-квалификатор (`@interface`), мета-аннотированную `@Qualifier` — это избавит от magic strings.

---

### Вопрос 9. Что произойдёт, если в контексте окажется два бина одного типа, а @Qualifier не указан — Spring выбросит исключение или разрешит конфликт?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [NoUniqueBeanDefinitionException (Spring Framework API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/NoUniqueBeanDefinitionException.html)

`NoUniqueBeanDefinitionException` — исключение, выбрасываемое, когда `BeanFactory` запрашивает бин по типу, но находит несколько подходящих кандидатов, тогда как ожидался ровно один. Доступны вспомогательные методы: `getNumberOfBeansFound()` возвращает количество найденных бинов, `getBeanNamesFound()` — их имена. Класс существует начиная со Spring 3.2.1.

#### Ответ от Claude

**Spring не всегда выбрасывает исключение сразу — он сначала пытается разрешить конфликт самостоятельно.**

Полный алгоритм при двух (и более) бинах одного типа без `@Qualifier`:

1. **Проверка `@Primary`.** Если ровно один из кандидатов помечен `@Primary` — он выбирается, исключения нет.

2. **Откат по имени (name fallback).** Если `@Primary` не задан, Spring сравнивает имя поля (или имя параметра при флаге `-parameters` в Spring 6.1+) с именами зарегистрированных бинов. Совпадение — бин выбирается, исключения нет.

   ```java
   // Есть бины: fooFormatter (FooFormatter) и barFormatter (BarFormatter)
   @Autowired
   private Formatter fooFormatter; // Совпадает с именем бина → внедряется FooFormatter
   ```

3. **`NoUniqueBeanDefinitionException`.** Если ни шаг 1, ни шаг 2 не смогли устранить неоднозначность, Spring выбрасывает `NoUniqueBeanDefinitionException` с сообщением вида:
   `expected single matching bean but found 2: beanA,beanB`.

**Итог:** исключение — это финальный исход, но Spring предпринимает попытки автоматического разрешения (через `@Primary` и name fallback) прежде, чем сдаться.

**Как избежать исключения (варианты устранения):**

| Способ | Когда применять |
|---|---|
| Пометить один бин `@Primary` | Есть очевидный «главный» бин |
| Добавить `@Qualifier` на точку внедрения | Нужна точная адресация разных бинов |
| Назвать поле/параметр как имя нужного бина | Быстрое решение без доп. аннотаций (не рекомендуется как постоянная практика) |
| Внедрить `List<T>` или `Map<String, T>` | Нужны все бины типа сразу |

**Тонкость с `@Autowired(required = false)`.** Даже при `required = false` неоднозначность (два кандидата) всё равно приводит к `NoUniqueBeanDefinitionException` — `required = false` лишь подавляет исключение при полном отсутствии бина нужного типа.
### Вопрос 10. Что такое AOP в Spring? Объясните понятия: аспект (aspect), совет (advice), срез (pointcut), точка соединения (joinpoint).

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [AOP Concepts :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/introduction-defn.html)

AOP (Aspect-Oriented Programming, аспектно-ориентированное программирование) дополняет ООП, предоставляя иной способ мышления о структуре программы. Если ООП делает основной единицей модульности класс, то в AOP такой единицей является аспект. Аспекты позволяют модуляризовать сквозные задачи (crosscutting concerns) — такие как управление транзакциями — которые охватывают несколько типов и объектов.

Ключевые понятия:

- **Аспект (Aspect)** — модуляризация сквозной задачи, затрагивающей несколько классов. Управление транзакциями — классический пример. В Spring реализуется обычными классами (schema-based) или классами с аннотацией `@Aspect`.

- **Совет (Advice)** — действие, выполняемое аспектом в конкретной точке соединения. Типы advice: "around", "before" и "after". Многие AOP-фреймворки, включая Spring, моделируют advice как перехватчик (interceptor) и поддерживают цепочку перехватчиков вокруг точки соединения.

- **Срез (Pointcut)** — предикат, сопоставляемый с точками соединения. Advice привязывается к выражению pointcut и запускается в каждой точке соединения, соответствующей этому выражению. Spring по умолчанию использует язык выражений pointcut из AspectJ.

- **Точка соединения (Join Point)** — момент выполнения программы, например выполнение метода или обработка исключения. В Spring AOP точка соединения **всегда** представляет выполнение метода.

#### Ответ от Claude

**Что такое AOP**

AOP — это парадигма программирования, которая дополняет объектно-ориентированный подход. Её цель — выделить сквозные задачи (logging, security, transaction management, caching) в отдельные модули — аспекты — вместо того чтобы дублировать их в каждом классе.

Spring AOP реализован на основе прокси-объектов и поддерживает только один вид точек соединения — выполнение метода. Для более широкой поддержки (поля, конструкторы и т.д.) используется полноценный AspectJ через weaving.

**Основные понятия:**

| Понятие | Определение |
|---|---|
| **Aspect (аспект)** | Модуль, инкапсулирующий сквозную задачу. Аннотируется `@Aspect`. Содержит pointcut'ы и advice. |
| **Join Point (точка соединения)** | Конкретный момент выполнения программы, к которому можно применить advice. В Spring AOP — **всегда метод**. |
| **Pointcut (срез)** | Выражение-предикат, описывающее, к каким join point'ам применяется advice. Использует язык AspectJ (`execution(...)`, `within(...)`, `@annotation(...)` и др.). |
| **Advice (совет)** | Код, который выполняется в момент, соответствующий pointcut. Типы: `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing`, `@Around`. |
| **Weaving (связывание)** | Процесс применения аспектов к целевым объектам. Spring выполняет его во время создания бина (runtime через proxy). |

**Пример:**

```java
@Aspect
@Component
public class LoggingAspect {

    // Pointcut: все методы в пакете service
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}

    // Advice: выполнить до вызова метода (join point)
    @Before("serviceLayer()")
    public void logBefore(JoinPoint jp) {
        System.out.println("Вызов: " + jp.getSignature().getName());
    }
}
```

**Важная особенность Spring AOP:** так как механизм основан на прокси, advice не срабатывает при вызове метода внутри того же объекта через `this` — такой вызов обходит прокси.

---

### Вопрос 11. Какие виды advice существуют в Spring AOP (@Before, @After, @Around и др.)? Чем @Around принципиально отличается от остальных?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Declaring Advice :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/ataspectj/advice.html)

Spring AOP поддерживает пять типов advice:

- **@Before** — выполняется до точки соединения. Не может предотвратить выполнение метода, если только не выбросит исключение.

- **@AfterReturning** — выполняется после нормального (без исключения) завершения метода. Через атрибут `returning` можно получить доступ к возвращаемому значению.

- **@AfterThrowing** — выполняется, если метод завершился исключением. Через атрибут `throwing` можно ограничиться конкретным типом исключения.

- **@After (finally)** — выполняется при любом исходе (нормальном завершении или исключении). Аналог блока `finally`. Должен быть готов обработать оба случая.

- **@Around** — наиболее мощный тип. Оборачивает вызов метода целиком. Первым параметром должен принимать `ProceedingJoinPoint`. Может выполнять логику до и после вызова, а также решать: вызвать ли вообще оригинальный метод через `proceed()`, заменить возвращаемое значение или выбросить исключение.

Официальная рекомендация: использовать наименее мощный тип advice, достаточный для решения задачи (например, предпочитать `@AfterReturning` вместо `@Around` там, где не нужен контроль над потоком выполнения).

#### Ответ от Claude

**Сводная таблица типов advice:**

| Аннотация | Когда выполняется | Параметр JoinPoint | Доступ к результату/исключению |
|---|---|---|---|
| `@Before` | До вызова метода | `JoinPoint` | Нет |
| `@AfterReturning` | После нормального возврата | `JoinPoint` | Да (атрибут `returning`) |
| `@AfterThrowing` | После выброса исключения | `JoinPoint` | Да (атрибут `throwing`) |
| `@After` | Всегда (аналог `finally`) | `JoinPoint` | Нет |
| `@Around` | Вокруг всего вызова | **`ProceedingJoinPoint`** | Да (полный контроль) |

**Чем @Around принципиально отличается от остальных:**

1. **Контроль над выполнением.** Только `@Around` решает, будет ли вообще вызван оригинальный метод. Остальные advice не могут этого предотвратить (кроме выброса исключения из `@Before`).

2. **`ProceedingJoinPoint` вместо `JoinPoint`.** Только `@Around` получает `ProceedingJoinPoint`, у которого есть метод `proceed()`. Без его явного вызова оригинальный метод не выполнится.

3. **Модификация аргументов и результата.** `@Around` может передать в `proceed(newArgs)` изменённые аргументы и вернуть любое значение вместо оригинального.

4. **Перехват и трансформация исключений.** `@Around` может поймать исключение и вернуть fallback-значение — или выбросить другое исключение.

**Пример @Around:**

```java
@Around("execution(* com.example.service.*.*(..))")
public Object measureTime(ProceedingJoinPoint pjp) throws Throwable {
    long start = System.currentTimeMillis();
    try {
        Object result = pjp.proceed(); // обязательный вызов
        return result;
    } finally {
        long elapsed = System.currentTimeMillis() - start;
        System.out.println(pjp.getSignature() + " took " + elapsed + "ms");
    }
}
```

**Порядок выполнения нескольких advice на одном join point (Spring 5.2.7+):**

```
@Around (вход) → @Before → [метод] → @AfterReturning/@AfterThrowing → @After → @Around (выход)
```

При наличии нескольких аспектов порядок их применения определяется аннотацией `@Order` (меньше значение — выше приоритет).

**Практический совет:** применяйте `@Around` только тогда, когда реально нужен контроль над потоком выполнения или возвращаемым значением. Для простого логирования достаточно `@Before` + `@AfterReturning`.

---

### Вопрос 12. Чем JDK dynamic proxy отличается от CGLIB proxy? При каких условиях Spring выбирает каждый из них?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Proxying Mechanisms :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)

Spring AOP может использовать два механизма создания прокси:

- **JDK dynamic proxy** — встроен в JDK. Создаёт прокси, реализующий те же интерфейсы, что и целевой объект. Используется по умолчанию, если целевой объект реализует хотя бы один интерфейс.

- **CGLIB proxy** — генерирует подкласс целевого класса во время выполнения. Используется, если целевой объект не реализует ни одного интерфейса.

Ограничения CGLIB: финальные классы (`final`) не могут быть проксированы (нельзя создать подкласс), финальные методы не могут быть перехвачены (нельзя переопределить). Начиная с Spring 3.2, CGLIB включён в `spring-core` и не требует отдельной зависимости. С версии Spring 4.0 конструктор проксированного объекта больше не вызывается дважды благодаря Objenesis.

Можно явно принудить к CGLIB через `@EnableAspectJAutoProxy(proxyTargetClass = true)`.

#### Ответ от Claude

**Принципиальное различие механизмов:**

| Характеристика | JDK Dynamic Proxy | CGLIB Proxy |
|---|---|---|
| **Основа** | Реализует интерфейсы | Создаёт подкласс (наследование) |
| **Требование к цели** | Должна реализовывать интерфейс | Класс не должен быть `final` |
| **Проксируемые методы** | Только методы интерфейса | Все не-`final`, не-`private` методы |
| **Пакет** | `java.lang.reflect.Proxy` (JDK) | `spring-core` (встроен с 3.2) |
| **Двойной вызов конструктора** | Нет | Нет (с Spring 4.0 через Objenesis) |

**Правило выбора в Spring:**

```
Цель реализует интерфейс? 
  ДА  → JDK dynamic proxy (по умолчанию)
  НЕТ → CGLIB proxy
```

Кроме того, если явно указано `proxyTargetClass = true` — всегда используется CGLIB, даже если интерфейсы есть.

**Как принудительно включить CGLIB:**

```java
@EnableAspectJAutoProxy(proxyTargetClass = true)
@Configuration
public class AppConfig { }
```

или для транзакций:

```java
@EnableTransactionManagement(proxyTargetClass = true)
```

**Ограничения CGLIB:**

- Нельзя проксировать `final`-классы.
- Нельзя перехватить `final`-методы и `private`-методы (Spring предупредит, но прокси создаст).
- Ограничения Java Module System: нельзя проксировать классы из закрытых модулей (например, классы `java.lang.*`) без соответствующего `--add-opens`.

**Ограничения JDK proxy:**

- Если код работает с конкретным классом (а не с интерфейсом), инжекция прокси завершится ошибкой `ClassCastException` — прокси реализует интерфейс, но не является экземпляром конкретного класса.

**Общая проблема обоих механизмов — самовызов (self-invocation):**

```java
@Service
public class OrderService {
    public void placeOrder() {
        this.validateOrder(); // вызов через 'this' — прокси обходится, @Transactional не сработает
    }

    @Transactional
    public void validateOrder() { ... }
}
```

Оба типа прокси основаны на оборачивании объекта снаружи, поэтому внутренний вызов `this.method()` всегда идёт напрямую к целевому объекту, минуя прокси. Решение — инжектировать сам бин себе (`@Autowired private OrderService self`) или переструктурировать код.

**Практическая рекомендация:** с Spring Boot 2.0+ CGLIB используется по умолчанию (`spring.aop.proxy-target-class=true`), что позволяет избежать `ClassCastException` при использовании конкретных типов. Это поведение изменило умолчание по сравнению с ранними версиями Spring.
### Вопрос 13. Почему вызов @Transactional-метода из другого метода того же класса (self-invocation) не работает? Как это исправить?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Using @Transactional :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

В режиме прокси (используемом по умолчанию) перехватываются только внешние вызовы, поступающие через прокси-объект. Это означает, что self-invocation — вызов метода целевого объекта из другого метода того же объекта — не приводит к созданию реальной транзакции во время выполнения, даже если вызываемый метод помечен аннотацией `@Transactional`. Иными словами, когда метод `getFoo()` вызывает `updateFoo()` на `this`, вызов обходит прокси-обёртку, и транзакционный совет (`advice`) никогда не срабатывает.

Для решения проблемы документация предлагает переключиться с прокси-режима на режим AspectJ (`mode = AdviceMode.ASPECTJ`): в этом случае байт-код целевого класса модифицируется напрямую, поэтому self-invocation корректно перехватывается вне зависимости от того, проходит ли вызов через прокси. Второй вариант — вынести транзакционную логику в отдельный Spring-бин.

#### Ответ от Claude

**Корневая причина проблемы**

Spring по умолчанию реализует `@Transactional` через proxy-based AOP (JDK Dynamic Proxy или CGLIB). Когда другой бин инжектирует ваш сервис, он получает ссылку не на сам объект, а на прокси-обёртку. Прокси перехватывает входящий вызов, открывает транзакцию, а затем делегирует вызов на реальный объект. Однако при вызове внутри самого объекта (`this.method()`) мы работаем непосредственно с целевым экземпляром, минуя прокси, — транзакционный совет не применяется.

```java
@Service
public class OrderService {

    // Транзакция НЕ откроется: вызов через this, прокси обойдён
    public void processOrder(Order order) {
        saveOrder(order);  // this.saveOrder(order)
    }

    @Transactional
    public void saveOrder(Order order) { /* ... */ }
}
```

**Способы исправления**

1. **Вынести метод в отдельный бин (рекомендуется)**
   Самый чистый подход: метод, требующий транзакции, переносится в другой Spring-управляемый компонент. Вызов через инжектированный бин проходит через прокси.

   ```java
   @Service
   public class OrderService {
       @Autowired
       private OrderPersistenceService persistenceService;

       public void processOrder(Order order) {
           persistenceService.saveOrder(order); // идёт через прокси
       }
   }

   @Service
   public class OrderPersistenceService {
       @Transactional
       public void saveOrder(Order order) { /* ... */ }
   }
   ```

2. **Self-injection (получить ссылку на свой прокси)**
   Бин инжектирует сам себя через `@Autowired` или `@Lazy` и вызывает метод через эту ссылку.

   ```java
   @Service
   public class OrderService {
       @Autowired
       @Lazy
       private OrderService self; // Spring инжектирует прокси-обёртку

       public void processOrder(Order order) {
           self.saveOrder(order); // вызов через прокси — транзакция работает
       }

       @Transactional
       public void saveOrder(Order order) { /* ... */ }
   }
   ```

   `@Lazy` нужен, чтобы разорвать циклическую зависимость при создании бина.

3. **Переключиться на AspectJ (compile-time или load-time weaving)**
   При AspectJ байт-код целевого класса модифицируется напрямую, прокси не нужен, поэтому self-invocation тоже перехватывается.

   ```java
   @Configuration
   @EnableTransactionManagement(mode = AdviceMode.ASPECTJ)
   public class AppConfig { }
   ```

   Требует подключения `spring-aspects` и настройки тканья (weaving). Наиболее «тяжёлый» вариант, редко используется в типичных Spring Boot приложениях.

**Дополнительный нюанс**

До Spring 6.0 `@Transactional` на `protected`- и package-private-методах в CGLIB-прокси формально игнорировалась. Начиная со Spring 6.0, CGLIB-прокси поддерживает `public`, `protected` и package-visible методы. Для interface-based JDK-прокси по-прежнему работают только `public`-методы, объявленные в интерфейсе.

---

### Вопрос 14. Что такое распространение транзакций (transaction propagation)? В чём разница между REQUIRED, REQUIRES_NEW и NESTED?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Transaction Propagation :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

Распространение транзакций определяет, что происходит с транзакцией при вызове одного транзакционного метода из другого.

**REQUIRED** (умолчание) принудительно обеспечивает наличие физической транзакции: либо создаёт новую, если транзакции нет, либо присоединяется к существующей внешней транзакции. Все логические области видимости отображаются на одну физическую транзакцию. Важное следствие: если внутренний метод помечает транзакцию как «только откат» (`rollback-only`), а внешний этого не знает, будет брошено `UnexpectedRollbackException`.

**REQUIRES_NEW** всегда создаёт независимую физическую транзакцию, никогда не участвуя в существующей внешней. Ресурсные транзакции полностью раздельны: могут коммититься и откатываться независимо. Блокировки внутренней транзакции освобождаются сразу после её завершения. Предупреждение: требует тщательной настройки пула соединений — одновременно может понадобиться более одного соединения.

**NESTED** использует единую физическую транзакцию с несколькими точками сохранения (savepoint). Это позволяет делать частичный откат: внутренняя транзакция может откатиться к своей точке сохранения, не затрагивая внешнюю. Реализован через JDBC savepoints и поддерживается преимущественно `DataSourceTransactionManager`. Если транзакции нет, поведение аналогично REQUIRED.

#### Ответ от Claude

**Что такое transaction propagation**

Propagation — атрибут аннотации `@Transactional`, определяющий, как транзакционный метод должен взаимодействовать с уже существующей транзакцией в текущем потоке. Значение по умолчанию — `REQUIRED`.

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method() { /* ... */ }
```

**REQUIRED**

- Присоединяется к существующей транзакции; если транзакции нет — создаёт новую.
- Внешний и внутренний методы работают в рамках **одной физической транзакции**.
- Если внутренний метод выбрасывает исключение и Spring помечает транзакцию как `rollback-only`, внешний метод не сможет её закоммитить — будет брошено `UnexpectedRollbackException`.
- Подходит для большинства случаев: сервис вызывает несколько репозиториев в одной транзакции.

```
[Outer TX] ──── метод A (REQUIRED) ──── вызывает ──── метод B (REQUIRED)
                          \____________ одна физическая транзакция ___________/
```

**REQUIRES_NEW**

- Всегда создаёт **новую независимую физическую транзакцию**, приостанавливая (suspend) текущую.
- Внутренняя транзакция может закоммититься или откатиться **независимо** от внешней.
- После завершения внутренней транзакции внешняя возобновляется.
- Важно: требует двух физических соединений с БД одновременно. При недостаточном пуле соединений возможен дедлок.
- Подходит: аудит-лог, который нужно сохранить даже при откате основной операции.

```
[Outer TX] --- suspend ---> [New Inner TX] --- commit/rollback ---> resume [Outer TX]
```

**NESTED**

- Создаёт **вложенную транзакцию** внутри существующей, используя JDBC savepoint.
- Если внутренний метод откатывается — происходит откат только до savepoint, внешняя транзакция продолжается.
- Если откатывается внешняя транзакция — откатывается и вложенная.
- **Ключевое отличие от REQUIRES_NEW**: используется одно физическое соединение, нет независимого коммита вложенной транзакции без внешней.
- Работает только с `DataSourceTransactionManager` (JDBC savepoints); с JPA/Hibernate нативно не поддерживается.
- Если транзакции нет, поведение аналогично REQUIRED.

```
[Outer TX] ──── savepoint ──── [Nested TX] ──── rollback to savepoint OR continue ──── [Outer TX commit]
```

**Сравнительная таблица**

| Характеристика         | REQUIRED        | REQUIRES_NEW           | NESTED                    |
|------------------------|-----------------|------------------------|---------------------------|
| Физических транзакций  | 1 (общая)       | 2 (независимые)        | 1 (с savepoint)           |
| Присоединяется к outer | Да              | Нет (suspend)          | Нет (savepoint)           |
| Независимый коммит     | Нет             | Да                     | Нет (зависит от outer)    |
| Независимый откат      | Нет             | Да                     | Частичный (до savepoint)  |
| Соединений с БД        | 1               | 2+                     | 1                         |
| Поддержка JPA          | Да              | Да                     | Ограниченно (не JPA)      |

---

### Вопрос 15. По умолчанию при каких исключениях @Transactional откатывает транзакцию? Как настроить откат для checked-исключений?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Rolling Back a Declarative Transaction :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html)

Инфраструктура транзакций Spring по умолчанию помечает транзакцию для отката только при runtime-исключениях (непроверяемых), то есть когда выброшенное исключение является экземпляром `RuntimeException` или его подклассом. Экземпляры `Error` также вызывают откат. Checked-исключения, выброшенные из транзакционного метода, по умолчанию **не** приводят к откату.

Для настройки отката для checked-исключений можно использовать XML-атрибут `rollback-for` или аннотационные атрибуты `rollbackFor` / `noRollbackFor`. Если одновременно совпадают и правило отката, и правило неотката, побеждает наиболее конкретное (ближайшее по иерархии).

Также поддерживается программный откат через `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()`, однако документация рекомендует придерживаться декларативного подхода.

#### Ответ от Claude

**Поведение по умолчанию**

Spring следует соглашению EJB CMT: транзакция откатывается автоматически только при **unchecked-исключениях**:

- `RuntimeException` и все его подклассы — откат
- `Error` — откат  
- `Exception` (checked) и его подклассы — **откат не производится**

```
Throwable
├── Error                        ← откат (по умолчанию)
└── Exception
    ├── RuntimeException         ← откат (по умолчанию)
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   └── ...
    └── IOException              ← НЕТ отката (по умолчанию, checked)
        ├── FileNotFoundException
        └── ...
```

Типичный пример-ловушка: если метод объявлен как `throws SQLException` (checked) и выбрасывает его, транзакция **не откатится** без явной настройки.

**Настройка через аннотацию**

Атрибут `rollbackFor` — указать, какие исключения должны вызывать откат (включая checked):

```java
@Transactional(rollbackFor = IOException.class)
public void importData() throws IOException {
    // IOException теперь вызовет откат
}

// Несколько типов
@Transactional(rollbackFor = {IOException.class, SQLException.class})
public void processData() throws IOException, SQLException { /* ... */ }
```

Атрибут `noRollbackFor` — исключить из откатов даже unchecked-исключения:

```java
@Transactional(noRollbackFor = IllegalArgumentException.class)
public void update(String id) {
    // IllegalArgumentException не вызовет откат
}
```

Совместное использование — побеждает наиболее специфичное правило (ближайшее по иерархии к выброшенному исключению):

```java
@Transactional(
    rollbackFor = Exception.class,
    noRollbackFor = BusinessValidationException.class
)
public void process() throws Exception {
    // Exception и его подклассы -> откат
    // BusinessValidationException -> откат НЕ производится (более специфичное правило)
}
```

**Строковые варианты атрибутов**

`rollbackForClassName` / `noRollbackForClassName` принимают строки с именами классов. Официальная документация предупреждает: паттерн работает как подстрока, что может привести к нежелательным совпадениям. Например, паттерн `"CustomException"` совпадёт с `CustomExceptionV2` и вложенным `CustomException$Inner`. Рекомендуется использовать полное имя класса или предпочитать типизированные атрибуты.

```java
// Нежелательно — подстрочное совпадение может быть неожиданным
@Transactional(rollbackForClassName = "Exception")

// Лучше — тип безопасен
@Transactional(rollbackFor = IOException.class)
```

**XML-конфигурация (для проектов без аннотаций)**

```xml
<tx:advice id="txAdvice" transaction-manager="txManager">
    <tx:attributes>
        <tx:method name="save*" rollback-for="NoProductInStockException"/>
        <tx:method name="update*" no-rollback-for="InstrumentNotFoundException"/>
        <tx:method name="*"/>
    </tx:attributes>
</tx:advice>
```

**Программный откат (крайний случай)**

Если по архитектурным причинам нельзя дать исключению всплыть (например, оно перехвачено внутри), можно пометить транзакцию вручную:

```java
@Transactional
public void doWork() {
    try {
        riskyOperation();
    } catch (CheckedException e) {
        // Помечаем транзакцию для отката, не перебрасывая исключение
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}
```

Документация рекомендует избегать этого подхода: он смешивает транзакционную инфраструктуру с бизнес-кодом.
### Вопрос 16. Что такое циклические зависимости между бинами? Как Spring разрешает их для singleton-бинов и почему они невозможны при инъекции через конструктор?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Dependency Injection :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)

Циклическая зависимость возникает, когда два или более бина зависят друг от друга, образуя циклическую цепочку ссылок. Если класс A требует экземпляр класса B через инъекцию через конструктор, а класс B требует экземпляр класса A через инъекцию через конструктор — Spring не может создать ни один из них и выбрасывает `BeanCurrentlyInCreationException`.

При инъекции через конструктор проблема принципиально неразрешима: аргументы конструктора должны быть предоставлены в момент создания объекта, а «проблема курицы и яйца» не оставляет выхода — A нельзя создать без B, а B нельзя создать без A.

Для setter-инъекции Spring использует механизм **трёхуровневого кеша** («early bean references»):

- **Уровень 1 (singletonObjects):** полностью инициализированные бины
- **Уровень 2 (earlySingletonObjects):** ранние ссылки на бины, ещё находящиеся в процессе инициализации
- **Уровень 3 (singletonFactories):** фабрики, создающие ранние ссылки на бины

Процесс разрешения (бин A зависит от B через setter, B зависит от A через setter):
1. Spring начинает создание бина A, добавляет его в «beans in creation» и помещает фабрику раннего объекта в третий уровень кеша.
2. Во время setter-инъекции A обнаруживается зависимость от B — вызывается `getBean(B)`.
3. Spring начинает создание B, ему нужен A — обращается к кешу.
4. Через `ObjectFactory` из третьего уровня получается ранняя (неполностью инициализированная) ссылка на A; она перемещается в второй уровень кеша.
5. B завершает инициализацию и помещается в первый уровень.
6. A получает готовый B, завершает инициализацию, перемещается в первый уровень.

Три уровня нужны из-за AOP: если у бина есть прокси, ObjectFactory в третьем уровне позволяет отложить создание прокси-объекта до момента его реальной необходимости, а не принудительно проксировать всё при создании.

#### Ответ от Claude

**Что такое циклическая зависимость**

Циклическая зависимость (circular dependency) возникает, когда бин A зависит от B, а B — от A (или через цепочку: A→B→C→A). Spring должен создать хотя бы один из них раньше, но ни один не может существовать без другого.

**Почему конструкторная инъекция не может разрешить цикл**

При инъекции через конструктор Spring обязан передать все зависимости в момент вызова конструктора — до того, как объект вообще будет создан. Это делает ситуацию тупиковой:
- Чтобы создать A, нужен готовый экземпляр B.
- Чтобы создать B, нужен готовый экземпляр A.
- Spring выбрасывает `BeanCurrentlyInCreationException` ещё при загрузке контекста.

**Как Spring разрешает циклы для singleton-бинов (setter/field инъекция)**

Механизм — трёхуровневый кеш в `DefaultSingletonBeanRegistry`:

| Кеш | Тип | Содержимое |
|-----|-----|------------|
| `singletonObjects` | `Map<String, Object>` | Полностью инициализированные бины |
| `earlySingletonObjects` | `Map<String, Object>` | Бины, созданные (конструктор вызван), но ещё не прошедшие post-processing |
| `singletonFactories` | `Map<String, ObjectFactory<?>>` | Фабрики, возвращающие ранний (possibly proxied) объект |

Пошаговый сценарий (A ←setter→ B):

1. Spring начинает создание A: вызывает конструктор, получает «сырой» объект. Помещает `ObjectFactory<A>` в `singletonFactories`.
2. Переходит к setter-инъекции A: обнаруживает зависимость B, вызывает `getBean("B")`.
3. Начинает создание B: вызывает конструктор, помещает `ObjectFactory<B>` в `singletonFactories`.
4. Setter-инъекция B требует A. `getSingleton("a", false)` находит фабрику в третьем уровне, вызывает `getObject()`, получает раннюю ссылку на A (уже «живой» объект в памяти, хотя не до конца настроенный). Ранняя ссылка переносится в `earlySingletonObjects`.
5. B получает раннюю ссылку на A, завершает инициализацию (вкл. BeanPostProcessor), перемещается в `singletonObjects`.
6. A получает готовый B, завершает инициализацию, перемещается в `singletonObjects`.

**Зачем три уровня, а не два**

Если бин обёрнут AOP-прокси, `ObjectFactory.getObject()` возвращает прокси-объект, а не «сырой» экземпляр. Двухуровневого кеша не хватило бы: пришлось бы проксировать каждый бин сразу при создании, даже если цикла нет. Третий уровень позволяет отложить создание прокси до момента, когда он реально нужен.

**Важные ограничения**

- Механизм работает **только для singleton-бинов**. Для prototype-бинов Spring не кеширует ранние ссылки и не разрешает циклы — выбрасывается исключение.
- Spring Boot начиная с версии 2.6 **запрещает цикличные зависимости по умолчанию** (`spring.main.allow-circular-references=false`). Наличие цикла — признак проблемы в архитектуре.
- Рекомендуемое решение при обнаружении цикла — рефакторинг: выделение общей зависимости в третий бин.

---

### Вопрос 17. Что происходит при размещении @Transactional на private-методе? Почему Spring AOP не может его перехватить?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Using @Transactional :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

Аннотация `@Transactional` типично используется на методах с модификатором `public`. Начиная со Spring 6.0, `protected` и package-visible методы также поддерживаются для class-based прокси (CGLIB). Методы в interface-based прокси (JDK dynamic proxy) должны быть `public` и объявлены в проксируемом интерфейсе.

Прокси-механизм Spring AOP перехватывает только **внешние вызовы** через прокси-объект. Когда метод внутри целевого объекта вызывает другой метод того же объекта (self-invocation через `this`), транзакционная семантика не применяется, даже если вызванный метод помечен `@Transactional`.

Для сценариев, требующих поддержки self-invocation, рекомендуется переключиться на AspectJ-режим (`@EnableTransactionManagement(mode = AdviceMode.ASPECTJ)`), при котором аспекты внедряются непосредственно в байт-код, а не через прокси.

Документация также рекомендует аннотировать методы конкретных классов, а не интерфейсов.

#### Ответ от Claude

**Что происходит с `@Transactional` на private-методе**

Аннотация на private-методе **игнорируется**. Никакой ошибки компиляции или ошибки при запуске не возникает — Spring просто не создаёт транзакционный перехват. Метод выполняется без транзакционной семантики, даже если на нём есть `@Transactional`.

**Механизм Spring AOP и почему private-методы недостижимы**

Spring AOP работает через **прокси-объект**, оборачивающий реальный бин. Существует два типа прокси:

- **JDK Dynamic Proxy** — создаётся только для классов, реализующих хотя бы один интерфейс; проксирует только методы, объявленные в интерфейсе; требует `public`-видимости.
- **CGLIB Proxy** — создаётся как подкласс целевого класса; переопределяет методы, чтобы добавить логику перехвата.

Для обоих типов **private-методы принципиально недостижимы**:
1. Private-метод не наследуется и не может быть переопределён в подклассе (CGLIB).
2. Private-метод не виден за пределами класса, поэтому JDK-прокси не может создать делегирующий метод.
3. Даже если каким-то образом вызов дошёл до прокси, он не знает о существовании private-метода.

Кроме того, вызов `this.privateMethod()` внутри класса происходит напрямую на реальном объекте, **минуя прокси** — перехватить его невозможно в принципе.

**Поддерживаемые уровни видимости (актуально для Spring 6.x)**

| Видимость | JDK Dynamic Proxy | CGLIB |
|-----------|:-----------------:|:-----:|
| `public` | Да | Да |
| `protected` | Нет | Да (с Spring 6.0) |
| package-private | Нет | Да (с Spring 6.0) |
| `private` | Нет | Нет |

**Решения**

1. **Сделать метод `public`** — самое простое и рекомендуемое. Если инкапсуляция критична, вынести транзакционную логику в отдельный Spring-бин с публичным методом.

2. **Самоинъекция (self-injection)** — внедрить бин сам в себя и вызывать методы через прокси:
   ```java
   @Service
   public class OrderService {
       @Autowired
       private OrderService self; // ссылка на прокси

       public void process() {
           self.doTransactionalWork(); // вызов через прокси
       }

       @Transactional
       public void doTransactionalWork() { ... }
   }
   ```

3. **`AopContext.currentProxy()`** — получить текущий прокси внутри метода (требует `exposeProxy = true`). Применяется редко из-за связности с инфраструктурой.

4. **AspectJ-режим** — при `@EnableTransactionManagement(mode = AdviceMode.ASPECTJ)` аспекты внедряются в байт-код на этапе компиляции или загрузки. Позволяет перехватывать private-методы и self-invocation, но требует дополнительной настройки (`spring-aspects.jar`, load-time или compile-time weaving).

**Итог**

`@Transactional` на private-методе молча не работает. Это следствие архитектурного решения Spring AOP — использовать прокси вместо байт-кодового инструментирования по умолчанию. Обнаружить проблему без тестов сложно, поэтому рекомендуется покрывать транзакционную логику интеграционными тестами.

---

### Вопрос 18. Как работают скоупы request и session? Как внедрить request-scoped бин в singleton-бин и какие проблемы это создаёт?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Bean Scopes :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html)

**Request scope** создаёт новый экземпляр бина для каждого HTTP-запроса. Когда запрос завершается, бин уничтожается. Используется через аннотацию `@RequestScope` или `@Scope("request")`.

**Session scope** создаёт новый экземпляр бина для каждой HTTP-сессии. Бин живёт на протяжении всей сессии и уничтожается вместе с ней. Используется через `@SessionScope` или `@Scope("session")`.

**Проблема инъекции в singleton.** Если напрямую внедрить request- или session-scoped бин в singleton, инъекция происходит один раз при создании singleton. В результате singleton на протяжении всей своей жизни будет держать единственный экземпляр request/session-бина — тот, который был активен при первом создании singleton.

**Решение — scoped proxy.** При объявлении бина с `proxyMode = ScopedProxyMode.TARGET_CLASS` (или `ScopedProxyMode.INTERFACES`) Spring внедряет не сам бин, а прокси-объект. При каждом вызове метода прокси обращается к актуальному экземпляру из текущего HTTP-запроса или сессии. Атрибут `proxyMode` обязателен, поскольку в момент создания ApplicationContext нет активного HTTP-запроса.

```java
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestScopedBean { ... }
```

#### Ответ от Claude

**Скоуп `request`**

При каждом входящем HTTP-запросе Spring создаёт новый экземпляр бина. Экземпляр привязан к потоку, обрабатывающему запрос (через `RequestContextHolder`). После завершения запроса и отправки ответа бин уничтожается. Это означает: у двух одновременных запросов будут два независимых экземпляра одного request-scoped бина.

Предварительное условие — наличие в веб-приложении `RequestContextListener` или `RequestContextFilter` (в Spring Boot регистрируется автоматически через `DispatcherServlet`).

Объявление:
```java
@Component
@RequestScope  // эквивалент @Scope("request")
public class LoginAction { ... }
```

**Скоуп `session`**

Бин создаётся один раз на HTTP-сессию пользователя и живёт всё время жизни сессии. Разные пользователи получают разные экземпляры. Уничтожается при инвалидации сессии.

```java
@Component
@SessionScope  // эквивалент @Scope("session")
public class UserCart { ... }
```

**Проблема инъекции в singleton-бин**

Singleton создаётся один раз при старте контекста приложения. Если в него напрямую внедрить request-scoped бин:

```java
@Service // singleton
public class OrderService {
    @Autowired
    private LoginAction loginAction; // request-scoped
    // ...
}
```

Spring выполнит инъекцию **один раз** при создании `OrderService`. Переменная `loginAction` будет всегда указывать на один и тот же объект — тот, что был создан при первом запросе (или вообще не существующий в момент создания контекста). Это прямой баг: разные HTTP-запросы будут использовать чужой `LoginAction`.

**Решение: scoped proxy**

`proxyMode = ScopedProxyMode.TARGET_CLASS` заставляет Spring внедрять в singleton **прокси-объект** вместо реального бина. Прокси реализует тот же интерфейс/расширяет тот же класс. При каждом вызове метода прокси делегирует вызов актуальному экземпляру из текущего RequestAttributes (для request) или HttpSession (для session):

```java
@Component
@Scope(
    value = WebApplicationContext.SCOPE_REQUEST,
    proxyMode = ScopedProxyMode.TARGET_CLASS
)
public class LoginAction { ... }
```

Атрибут `proxyMode` обязателен потому, что в момент запуска контекста нет активного HTTP-запроса, и реальный бин ещё не может быть создан. Без прокси Spring выбросит исключение.

Для классов, реализующих интерфейс, можно использовать `ScopedProxyMode.INTERFACES` (JDK dynamic proxy). Для классов без интерфейса — только `ScopedProxyMode.TARGET_CLASS` (CGLIB).

**Проблемы, которые создаёт такой подход**

1. **Скрытая сложность.** Singleton «не знает», что держит прокси. Неаккуратное использование (например, сравнение через `==` или передача ссылки вовне) может привести к неожиданному поведению.

2. **Сериализация.** Scoped proxy не сериализуется напрямую. Если singleton нужно сериализовать, это станет проблемой.

3. **Тестирование.** В unit-тестах нет HTTP-контекста. Необходимо явно мокировать `RequestContextHolder` или использовать `MockHttpServletRequest`.

4. **Многопоточность.** Прокси корректно работает только при наличии активного HTTP-запроса в текущем потоке. При асинхронной обработке (`@Async`, `CompletableFuture`) контекст запроса может быть недоступен — нужно явно передавать `RequestAttributes` через `RequestContextHolder.setRequestAttributes()`.

**Альтернатива: `ObjectFactory` / `ObjectProvider`**

```java
@Service
public class OrderService {
    @Autowired
    private ObjectFactory<LoginAction> loginActionFactory;

    public void process() {
        LoginAction action = loginActionFactory.getObject(); // всегда текущий экземпляр
        // ...
    }
}
```

`ObjectProvider` (расширение `ObjectFactory`) также поддерживает ленивую инициализацию и опциональность, что делает его предпочтительным в современном коде.

---
### Вопрос 19. Что такое BeanPostProcessor и BeanFactoryPostProcessor? В чём их различие и на каком этапе жизненного цикла они выполняются?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Container Extension Points :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html)

`BeanPostProcessor` предоставляет колбэк-методы, позволяющие настраивать экземпляры бинов после того, как Spring их создал. Он запускается в двух точках жизненного цикла каждого бина: до вызова методов инициализации (`postProcessBeforeInitialization`) и после их завершения (`postProcessAfterInitialization`). Таким образом, он работает непосредственно с объектами-бинами.

`BeanFactoryPostProcessor` позволяет читать и изменять метаданные конфигурации бинов (bean definitions) до того, как контейнер вообще приступит к созданию экземпляров. Он запускается на ранней фазе старта контейнера — после загрузки всех bean definitions, но до инстанцирования обычных бинов. Типичный пример — `PropertySourcesPlaceholderConfigurer`, который подставляет значения из `.properties`-файлов в `${...}`-плейсхолдеры прямо в определениях бинов.

Ключевое правило: оба типа объявляются через статический (`static`) `@Bean`-метод, чтобы исключить их преждевременную инициализацию и нежелательные побочные эффекты.

#### Ответ от Claude

**BeanFactoryPostProcessor** — точка расширения, работающая с **метаданными** (bean definitions). Вызывается один раз на старте контейнера, когда все `BeanDefinition` уже загружены, но ни один обычный бин ещё не создан. Позволяет изменить класс бина, его scope, свойства — всё то, что записано в `BeanDefinition`. Нельзя получать или модифицировать экземпляры бинов: это вызовет их преждевременное создание. Пример из Spring: `PropertySourcesPlaceholderConfigurer`, `ConfigurationClassPostProcessor`.

Интерфейс:
```java
public interface BeanFactoryPostProcessor {
    void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory);
}
```

**BeanPostProcessor** — точка расширения, работающая с **экземплярами** бинов. Вызывается для каждого создаваемого бина дважды:
1. `postProcessBeforeInitialization(Object bean, String beanName)` — до вызова `@PostConstruct` / `afterPropertiesSet()`;
2. `postProcessAfterInitialization(Object bean, String beanName)` — после вызова инициализирующих методов.

Может вернуть обёртку (прокси) вместо оригинального объекта. Именно на этом механизме строится Spring AOP (`AbstractAutoProxyCreator`) и обработка аннотаций (`AutowiredAnnotationBeanPostProcessor`, `CommonAnnotationBeanPostProcessor`).

**Сравнительная таблица:**

| Характеристика | BeanFactoryPostProcessor | BeanPostProcessor |
|---|---|---|
| Работает с | Bean definitions (метаданные) | Bean instances (объекты) |
| Момент выполнения | До создания бинов | После создания каждого бина |
| Вызывается | Один раз за контейнер | По два раза на каждый бин |
| Типичное применение | Подстановка placeholder-ов, изменение scope | AOP-прокси, обработка аннотаций |

**Порядок в жизненном цикле контейнера (упрощённо):**
1. Загрузка конфигурации → создание `BeanDefinition`;
2. Запуск всех `BeanFactoryPostProcessor` → модификация `BeanDefinition`;
3. Для каждого бина: создание экземпляра → внедрение зависимостей → `postProcessBeforeInitialization` → `@PostConstruct` / `afterPropertiesSet()` → `postProcessAfterInitialization` → бин готов.

`ApplicationContext` регистрирует оба типа автоматически по наличию в контексте. При использовании голого `BeanFactory` их нужно регистрировать вручную.

---

### Вопрос 20. Как уровень изоляции транзакции (isolation) связан с аннотацией @Transactional? Какой уровень используется по умолчанию и что он означает?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Isolation (Spring Framework 7.0.7 API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/annotation/Isolation.html)

Аннотация `@Transactional` принимает атрибут `isolation` типа `Isolation` (enum). По умолчанию используется `Isolation.DEFAULT`, что означает применение уровня изоляции, установленного по умолчанию в используемой базе данных. Все остальные значения (`READ_UNCOMMITTED`, `READ_COMMITTED`, `REPEATABLE_READ`, `SERIALIZABLE`) соответствуют стандартным уровням JDBC.

- `READ_UNCOMMITTED` — допускает «грязное» чтение, неповторяемое чтение и фантомное чтение.
- `READ_COMMITTED` — предотвращает грязное чтение; неповторяемое и фантомное чтение возможны.
- `REPEATABLE_READ` — предотвращает грязное и неповторяемое чтение; фантомное чтение возможно.
- `SERIALIZABLE` — предотвращает все три аномалии; наиболее строгий уровень.

#### Ответ от Claude

Атрибут `isolation` аннотации `@Transactional` задаёт уровень изоляции транзакции:

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void updateAccount(Account account) { ... }
```

**Уровень по умолчанию — `Isolation.DEFAULT`.**
Это означает, что Spring делегирует выбор уровня изоляции самой СУБД. Большинство реляционных баз данных (PostgreSQL, Oracle, SQL Server) используют по умолчанию `READ_COMMITTED`; MySQL InnoDB — `REPEATABLE_READ`.

**Три классические аномалии параллельных транзакций:**

| Аномалия | Описание |
|---|---|
| Dirty read (грязное чтение) | Транзакция читает незафиксированные изменения другой транзакции |
| Non-repeatable read (неповторяемое чтение) | Повторный SELECT в той же транзакции возвращает другое значение строки, потому что другая транзакция её изменила и зафиксировала |
| Phantom read (фантомное чтение) | Повторный SELECT возвращает новые строки, потому что другая транзакция вставила и зафиксировала их |

**Все уровни и их гарантии:**

| Уровень | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| `READ_UNCOMMITTED` | возможен | возможно | возможно |
| `READ_COMMITTED` | невозможен | возможно | возможно |
| `REPEATABLE_READ` | невозможен | невозможно | возможно |
| `SERIALIZABLE` | невозможен | невозможно | невозможно |

**Важные нюансы:**

1. Атрибут `isolation` применяется только при значениях propagation `REQUIRED` или `REQUIRES_NEW`. При `SUPPORTS`, `MANDATORY`, `NESTED` и других, присоединяющихся к существующей транзакции, уровень изоляции уже устанавлен и не может быть изменён — Spring выбросит исключение, если запрошенный уровень отличается.

2. Не все СУБД поддерживают все уровни. Например, Oracle не поддерживает `READ_UNCOMMITTED` и `REPEATABLE_READ` в стандартном смысле.

3. Более высокий уровень изоляции снижает количество аномалий, но увеличивает contention (соперничество за блокировки) и может снизить производительность.

---

