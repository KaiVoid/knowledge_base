# Spring Framework (Core, IoC, AOP) — часть 2 из 3

> Вопросы 21–40 (в части: 20). Всего в разделе: 51.
> Область знаний: [../theory/01-knowledge-areas/03-backend-ecosystem/13-spring-core.md](../theory/01-knowledge-areas/03-backend-ecosystem/13-spring-core.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](spring-01.md) · **ч.2** · [ч.3](spring-03.md)

---
### Вопрос 21. В чём разница между BeanFactory и ApplicationContext? Почему ApplicationContext расширяет BeanFactory, и какие дополнительные возможности он даёт (регистрация BeanPostProcessor, события, i18n, AOP-интеграция)?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [The BeanFactory API :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/beanfactory.html)

`BeanFactory` предоставляет базовую инфраструктуру IoC-контейнера: создание, конфигурирование и связывание бинов. `ApplicationContext` является подинтерфейсом `BeanFactory` и добавляет возможности корпоративного уровня.

Принципиальное отличие при использовании голого `DefaultListableBeanFactory`: он не знает ни о каких «специальных» бинах — `BeanPostProcessor` и `BeanFactoryPostProcessor` нужно регистрировать вручную через `factory.addBeanPostProcessor(...)` или вызывать `cfg.postProcessBeanFactory(factory)` явно. `ApplicationContext` выполняет обнаружение и регистрацию автоматически по типу бина в контексте.

Официальная документация прямо указывает: для большинства приложений рекомендуется использовать `ApplicationContext`.

#### Ответ от Claude

**Архитектурная связь:**
`ApplicationContext` расширяет `BeanFactory` (а точнее `HierarchicalBeanFactory` и `ListableBeanFactory`), добавляя к нему несколько интерфейсов: `MessageSource`, `ApplicationEventPublisher`, `ResourcePatternResolver` и другие. Таким образом, `ApplicationContext` — это полноценный контейнер корпоративного уровня, тогда как `BeanFactory` — минимальный IoC-контейнер.

**Ключевые различия:**

| Возможность | BeanFactory | ApplicationContext |
|---|---|---|
| Создание и связывание бинов | да | да |
| Ленивая загрузка бинов | да (по умолчанию) | только с `@Lazy` |
| Eager-загрузка singleton-ов при старте | нет | да |
| Автоматическая регистрация `BeanPostProcessor` | нет | да |
| Автоматическая регистрация `BeanFactoryPostProcessor` | нет | да |
| Интернационализация (i18n, MessageSource) | нет | да |
| Публикация событий (ApplicationEvent) | нет | да |
| Интеграция с AOP | ограничена | полная |
| Доступ к ресурсам (ResourceLoader) | нет | да |

**Детали дополнительных возможностей ApplicationContext:**

1. **Автоматическая регистрация пост-процессоров.** `ApplicationContext` при старте сканирует контекст и автоматически регистрирует все бины, реализующие `BeanPostProcessor` и `BeanFactoryPostProcessor`. При использовании `DefaultListableBeanFactory` напрямую это нужно делать вручную — ошибочно забыть добавить `AutowiredAnnotationBeanPostProcessor`, и `@Autowired` перестанет работать.

2. **Интернационализация (i18n).** `ApplicationContext` реализует `MessageSource`. Достаточно объявить бин `messageSource`, и можно получать локализованные строки через `context.getMessage("key", null, Locale.ENGLISH)`. `BeanFactory` не имеет этого интерфейса.

3. **События (ApplicationEvent / ApplicationListener).** `ApplicationContext` является `ApplicationEventPublisher`. Бины могут публиковать события через `publisher.publishEvent(event)` и подписываться через `@EventListener` или `ApplicationListener<T>`. Встроенные события: `ContextRefreshedEvent`, `ContextClosedEvent` и др. В `BeanFactory` этого механизма нет.

4. **AOP-интеграция.** При использовании `ApplicationContext` `BeanPostProcessor`-ы, создающие прокси (например, `AbstractAutoProxyCreator` для Spring AOP, `@Transactional`, `@Async`), регистрируются автоматически. Через голый `BeanFactory` для получения AOP-прокси пришлось бы всё настраивать вручную.

5. **Стратегия загрузки бинов.** `BeanFactory` по своей природе lazy — бин создаётся в момент первого обращения через `getBean()`. `ApplicationContext` при старте инстанцирует все singleton-бины сразу (eager), что позволяет обнаружить ошибки конфигурации немедленно при запуске приложения, а не при первом запросе.

**Практический вывод:** `BeanFactory` используется в редких случаях, когда нужен полный ручной контроль над обработкой бинов (например, в resource-constrained окружениях). Для всех стандартных Spring-приложений, включая Spring Boot, следует использовать `ApplicationContext` (как правило, `AnnotationConfigApplicationContext` или его Boot-обёртку).
### Вопрос 22. Какие три вида внедрения зависимостей поддерживает Spring (constructor, setter, field)? Почему constructor injection считается предпочтительным с точки зрения неизменяемости и тестируемости?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Dependency Injection :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)

Официальная документация Spring описывает два основных варианта внедрения зависимостей — через конструктор и через сеттер — и отдельно упоминает внедрение через поле (@Autowired на поле).

**Constructor-based DI**: контейнер вызывает конструктор с аргументами, каждый из которых представляет зависимость. Позволяет объявлять поля как `final`, гарантирует, что зависимости не равны `null`, и возвращает объект уже в полностью инициализированном состоянии.

**Setter-based DI**: контейнер вызывает setter-методы после создания бина через конструктор без аргументов. Рекомендуется для необязательных зависимостей, которым можно назначить разумные значения по умолчанию. Такие объекты поддаются реконфигурации и повторному внедрению.

**Field-based DI**: зависимость инжектируется напрямую в поле через `@Autowired`. В официальной документации этот вариант не перечисляется среди рекомендуемых. Он использует рефлексию, что дороже по накладным расходам, чем конструктор или сеттер.

Рекомендация команды Spring:

> «Команда Spring в целом рекомендует constructor injection, поскольку это позволяет реализовывать компоненты как неизменяемые объекты и гарантирует, что обязательные зависимости не равны null.»

Правило: используйте конструктор для обязательных зависимостей и сеттеры — для необязательных.

#### Ответ от Claude

**Три вида внедрения зависимостей в Spring:**

**1. Constructor Injection (внедрение через конструктор)**

```java
@Component
public class OrderService {
    private final PaymentGateway paymentGateway;

    // Начиная со Spring 4.3 @Autowired необязателен при единственном конструкторе
    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }
}
```

**2. Setter Injection (внедрение через сеттер)**

```java
@Component
public class OrderService {
    private PaymentGateway paymentGateway;

    @Autowired
    public void setPaymentGateway(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }
}
```

**3. Field Injection (внедрение через поле)**

```java
@Component
public class OrderService {
    @Autowired
    private PaymentGateway paymentGateway;
}
```

---

**Почему constructor injection считается предпочтительным:**

1. **Неизменяемость (Immutability)**. Поле можно объявить `final`, что делает зависимость неизменяемой после создания объекта. Field injection и setter injection не позволяют использовать `final`.

2. **Гарантия ненулевых зависимостей**. При конструкторном внедрении объект не может быть создан без всех обязательных зависимостей — NullPointerException исключён структурно. Field injection допускает `null` в момент создания бина (если зависимость не найдена).

3. **Тестируемость**. В unit-тестах не нужен Spring-контейнер и рефлексия — достаточно вызвать конструктор напрямую:

   ```java
   // Тест без Spring
   OrderService service = new OrderService(new FakePaymentGateway());
   ```

   При field injection без контейнера нужно либо поднимать ApplicationContext, либо использовать рефлексию (`ReflectionTestUtils.setField`).

4. **Явные зависимости**. Конструктор документирует все зависимости как часть публичного API класса. Field injection скрывает зависимости внутри реализации — это называют «hidden dependencies».

5. **Обнаружение циклических зависимостей**. Spring падает с ошибкой при старте, если конструкторные зависимости образуют цикл, что помогает выявить проблему ранно. Setter injection скрывает цикл до рантайма.

6. **Код-смелл при большом числе зависимостей**. Конструктор с 7+ параметрами сигнализирует о нарушении принципа единственной ответственности, тогда как field injection «прячет» эту проблему.

**Когда использовать setter injection**: для действительно необязательных зависимостей, которые имеют разумное значение по умолчанию, или когда класс — JMX MBean, требующий реконфигурации в рантайме.

**Field injection** не рекомендуется в продакшн-коде: он нарушает принцип явных зависимостей, не поддерживает `final`-поля и затрудняет тестирование.

---

### Вопрос 23. Что происходит, если в контексте есть два бина одного типа, а @Autowired не знает, какой выбрать? Как работают @Primary и @Qualifier, и есть ли между ними приоритет?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Fine-tuning Annotation-based Autowiring with @Primary or @Fallback :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired-primary.html)

Если в контексте есть несколько бинов одного типа, а точка внедрения не уточняет, какой именно нужен, Spring бросает исключение `NoUniqueBeanDefinitionException`.

**@Primary** помечает один бин как предпочтительного кандидата при внедрении по типу. Если среди нескольких бинов одного типа ровно один помечен `@Primary`, именно он будет выбран при `@Autowired` без дополнительных указаний.

Начиная со Spring 6.2, существует зеркальная аннотация **@Fallback**: она отмечает бин как резервный, то есть используемый только тогда, когда нет обычного (не-fallback) кандидата.

**@Qualifier** позволяет уточнить конкретный бин по имени или пользовательскому квалификатору прямо в точке внедрения:

```java
@Autowired
@Qualifier("secondMovieCatalog")
private MovieCatalog movieCatalog;
```

Приоритет (от наивысшего к наименьшему):

1. **@Qualifier** — наиболее специфичное указание, всегда побеждает
2. **@Primary** — используется, когда квалификатор не задан
3. **@Fallback** — последний резерв (Spring 6.2+)
4. Совпадение имени поля/параметра с именем бина — самый слабый фолбэк

#### Ответ от Claude

**Что происходит при неоднозначности**

Если в контексте зарегистрированы два или более бина одного типа и `@Autowired` не получает дополнительных подсказок, Spring при старте бросает:

```
org.springframework.beans.factory.NoUniqueBeanDefinitionException:
No qualifying bean of type 'com.example.PaymentGateway' available:
expected single matching bean but found 2: stripeGateway, paypalGateway
```

---

**@Primary — предпочтительный кандидат по умолчанию**

```java
@Component
@Primary
public class StripePaymentGateway implements PaymentGateway { ... }

@Component
public class PaypalPaymentGateway implements PaymentGateway { ... }

// Внедряется StripePaymentGateway без каких-либо дополнительных аннотаций
@Autowired
private PaymentGateway paymentGateway;
```

`@Primary` работает на уровне определения бина и действует для всех точек внедрения, где не задан более специфичный квалификатор. Аналог в XML: атрибут `primary="true"` у тега `<bean>`.

---

**@Qualifier — явный выбор конкретного бина**

```java
@Autowired
@Qualifier("paypalGateway")
private PaymentGateway paymentGateway;  // Инжектируется PaypalPaymentGateway
```

`@Qualifier` применяется непосредственно в точке внедрения (поле, параметр конструктора, параметр сеттера) и указывает имя бина или пользовательское значение квалификатора. По умолчанию имя бина совпадает с именем класса с маленькой буквы.

Можно создать собственную аннотацию-квалификатор:

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Qualifier
public @interface Stripe { }

@Autowired
@Stripe
private PaymentGateway paymentGateway;
```

---

**Приоритет между @Primary и @Qualifier**

`@Qualifier` имеет более высокий приоритет, чем `@Primary`. Если в точке внедрения стоит `@Qualifier`, Spring ищет бин с указанным квалификатором и игнорирует `@Primary` полностью. `@Primary` используется только тогда, когда квалификатор не задан.

Полная таблица приоритетов (от высшего к низшему):

| Приоритет | Механизм | Описание |
|-----------|----------|----------|
| 1 | `@Qualifier` | Явное указание бина в точке внедрения |
| 2 | `@Primary` | Маркер предпочтительного бина по умолчанию |
| 3 | `@Fallback` (Spring 6.2+) | Резервный бин, если нет обычного кандидата |
| 4 | Совпадение имени поля с именем бина | Слабый фолбэк без аннотаций |

**Важное различие**: `@Primary` задаётся один раз на определении бина и распространяется на все точки внедрения. `@Qualifier` задаётся в каждой точке внедрения отдельно и обеспечивает более точный контроль.

---

### Вопрос 24. Опишите полный жизненный цикл Spring-бина: от чтения BeanDefinition до вызова destroy-метода. На каком шаге подключаются BeanFactoryPostProcessor и BeanPostProcessor?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Container Extension Points :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html)

Документация Spring описывает два ключевых расширения контейнера:

**BeanFactoryPostProcessor** работает с метаданными конфигурации бинов. IoC-контейнер позволяет ему прочитать конфигурацию и при необходимости изменить её до того, как контейнер создаёт какие-либо бины (кроме самих экземпляров `BeanFactoryPostProcessor`). `BeanFactoryPostProcessor` может взаимодействовать с определениями бинов и изменять их, но никогда — с экземплярами бинов.

**BeanPostProcessor** предоставляет хуки в жизненный цикл Spring-бина для изменения его конфигурации. Интерфейс определяет два callback-метода:
- `postProcessBeforeInitialization()` — вызывается перед инициализационными callback-ами (такими как `@PostConstruct`, `InitializingBean.afterPropertiesSet()`, кастомный `init-method`)
- `postProcessAfterInitialization()` — вызывается после инициализационных callback-ов, когда бин уже заполнен значениями свойств

Порядок инициализационных callback-ов при совмещении нескольких механизмов:
1. `@PostConstruct`-метод
2. `InitializingBean.afterPropertiesSet()`
3. Кастомный `init-method`

Порядок destruction callback-ов:
1. `@PreDestroy`-метод
2. `DisposableBean.destroy()`
3. Кастомный `destroy-method`

#### Ответ от Claude

**Полный жизненный цикл Spring-бина**

```
[1] Чтение и регистрация BeanDefinition
         |
[2] BeanFactoryPostProcessor.postProcessBeanFactory()
         |
[3] Инстанциирование бина (конструктор / factory-method)
         |
[4] Внедрение зависимостей (свойства, конструктор, сеттеры)
         |
[5] Вызов Aware-интерфейсов
         |
[6] BeanPostProcessor.postProcessBeforeInitialization()
         |
[7] @PostConstruct
         |
[8] InitializingBean.afterPropertiesSet()
         |
[9] Кастомный init-method (@Bean(initMethod=...) / XML init-method)
         |
[10] BeanPostProcessor.postProcessAfterInitialization()
         |
[11] Бин готов к использованию
         |
     ... работа приложения ...
         |
[12] @PreDestroy
         |
[13] DisposableBean.destroy()
         |
[14] Кастомный destroy-method
```

---

**Шаг 1: Чтение BeanDefinition**

При старте контейнера читаются все источники конфигурации (`@Configuration`-классы, XML, classpath-сканирование). Каждый бин представляется объектом `BeanDefinition`, содержащим: имя класса, скоуп, имена init/destroy методов, зависимости, ленивость инициализации и прочие метаданные. Экземпляры бинов ещё не создаются.

**Шаг 2: BeanFactoryPostProcessor**

Вызывается **до создания каких-либо обычных бинов**. Получает доступ к `ConfigurableListableBeanFactory` и может читать и модифицировать `BeanDefinition`-объекты: менять значения свойств, классы, скоупы. Классический пример — `PropertySourcesPlaceholderConfigurer`, который заменяет `${...}` заглушки реальными значениями из `.properties`-файлов ещё до инстанциирования бинов.

Важно: `BeanFactoryPostProcessor` работает с определениями, но не с экземплярами бинов.

**Шаги 3–4: Инстанциирование и внедрение зависимостей**

Контейнер создаёт экземпляр через конструктор или фабричный метод, затем заполняет свойства через сеттеры или напрямую (в случае field injection — через рефлексию).

**Шаг 5: Aware-интерфейсы**

Если бин реализует специальные интерфейсы, контейнер вызывает соответствующие сеттеры:
- `BeanNameAware.setBeanName()`
- `BeanFactoryAware.setBeanFactory()`
- `ApplicationContextAware.setApplicationContext()`

**Шаг 6: BeanPostProcessor.postProcessBeforeInitialization()**

Вызывается для каждого бина перед его инициализационными callback-ами. Именно здесь работает, например, `CommonAnnotationBeanPostProcessor`, который обрабатывает `@PostConstruct` (то есть технически `@PostConstruct` выполняется внутри этого шага, а не после него).

**Шаги 7–9: Инициализационные callback-и**

При наличии нескольких механизмов порядок фиксированный:
1. `@PostConstruct`
2. `InitializingBean.afterPropertiesSet()`
3. Кастомный `init-method`

Если одному методу назначены сразу несколько механизмов (например, метод называется `init` и он же указан в `initMethod`), метод выполнится только один раз.

**Шаг 10: BeanPostProcessor.postProcessAfterInitialization()**

Вызывается после всех инициализационных callback-ов. Здесь Spring AOP создаёт прокси-объекты (CGLIB / JDK dynamic proxy). Именно поэтому бин, полученный из контекста, может быть оберткой над оригинальным объектом.

**Шаги 12–14: Destruction callback-и**

При закрытии контейнера (`context.close()` или регистрация `shutdown hook`) для singleton-бинов вызываются:
1. `@PreDestroy`
2. `DisposableBean.destroy()`
3. Кастомный `destroy-method`

Для prototype-скоупа destroy-методы Spring не вызывает — ответственность за уничтожение лежит на клиенте.

---

**Ключевое различие между BeanFactoryPostProcessor и BeanPostProcessor**

| Аспект | BeanFactoryPostProcessor | BeanPostProcessor |
|--------|--------------------------|-------------------|
| Когда вызывается | До создания бинов | После создания каждого бина |
| Работает с | BeanDefinition (метаданные) | Экземплярами бинов |
| Может изменять | Конфигурацию бина | Поведение/состояние бина |
| Типичные представители | PropertySourcesPlaceholderConfigurer | AutowiredAnnotationBeanPostProcessor, AOP-прокси |

Оба типа должны регистрироваться как `static @Bean`-методы в `@Configuration`-классах, чтобы контейнер создал их раньше обычных бинов и они не спровоцировали преждевременную инициализацию конфигурационных классов.
### Вопрос 25. Что такое скоупы бинов? Чем prototype отличается от singleton с точки зрения управления жизненным циклом — почему Spring не вызывает @PreDestroy у prototype-бинов?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Spring Boot: Lifecycle of Prototype Bean Scope (Medium)](https://medium.com/@saiteja-erwa/bean-scope-prototype-in-spring-boot-443b740f964f)

Spring управляет полным жизненным циклом singleton-бинов, однако для prototype-бинов контейнер передаёт бин клиенту сразу после инициализации и больше не отслеживает этот экземпляр. Коллбэки инициализации (`@PostConstruct`) вызываются для бинов обоих скоупов, а вот деструктор (`@PreDestroy`) для prototype-бинов Spring не вызывает: «уничтожение и очистка prototype-бинов находятся за пределами ответственности Spring». Разработчик обязан самостоятельно управлять освобождением ресурсов. В качестве решения статья предлагает реализовать кастомный `PrototypeBeanPostProcessor`, который имплементирует `BeanPostProcessor`, `DisposableBean` и `ApplicationContextAware`, хранит список созданных prototype-экземпляров и вызывает их `destroy()` при уничтожении контекста.

#### Ответ от Claude

**Скоупы бинов** определяют, сколько экземпляров бина будет создано и как долго они живут. Основные скоупы Spring:

| Скоуп | Где работает | Описание |
|---|---|---|
| `singleton` | Любой контекст | Один экземпляр на контейнер (по умолчанию) |
| `prototype` | Любой контекст | Новый экземпляр при каждом обращении |
| `request` | Web-контекст | Один экземпляр на HTTP-запрос |
| `session` | Web-контекст | Один экземпляр на HTTP-сессию |
| `application` | Web-контекст | Один экземпляр на `ServletContext` |
| `websocket` | Web-контекст | Один экземпляр на WebSocket-сессию |

**Разница в управлении жизненным циклом: singleton vs prototype**

Для **singleton**-бина Spring управляет полным жизненным циклом:
1. Создание и инстанциация.
2. Внедрение зависимостей.
3. Вызов `@PostConstruct` / `InitializingBean.afterPropertiesSet()`.
4. Бин используется клиентским кодом.
5. При закрытии контекста — вызов `@PreDestroy` / `DisposableBean.destroy()`.

Для **prototype**-бина Spring управляет только первой половиной:
1. Создание нового экземпляра при каждом запросе.
2. Внедрение зависимостей.
3. Вызов `@PostConstruct`.
4. Бин передаётся клиенту — **контейнер теряет ссылку на экземпляр**.
5. `@PreDestroy` **не вызывается никогда**.

**Почему @PreDestroy не вызывается у prototype-бинов**

Официальная документация Spring формулирует это так:

> «Контейнер инстанциирует, конфигурирует и собирает prototype-объект, после чего передаёт его клиенту, не сохраняя никакой записи об этом экземпляре. Поэтому, хотя коллбэки инициализации вызываются для всех объектов вне зависимости от скоупа, в случае prototype-бинов настроенные коллбэки уничтожения не вызываются.»

Технически причина проста: Spring не хранит ссылку на prototype-экземпляр после его передачи клиенту. Внутренняя карта `singletonObjects` (где хранятся singleton-бины и откуда Spring знает, что нужно уничтожить при `close()`) для prototype-бинов никогда не заполняется. Без ссылки на объект невозможно позвонить его деструктивному методу.

**Ответственность за очистку лежит на клиентском коде.** Если prototype-бин удерживает дорогостоящие ресурсы (соединения, файловые дескрипторы), разработчик должен освобождать их вручную. Один из официально рекомендованных подходов — кастомный `BeanPostProcessor`, который держит слабые ссылки на все созданные prototype-экземпляры и уничтожает их при остановке контекста.

**Важно:** `@PostConstruct` вызывается для prototype-бинов всегда — Spring вызывает все коллбэки инициализации независимо от скоупа. Только деструктивная часть жизненного цикла не управляется контейнером.

---

### Вопрос 26. Как Spring разрешает циклические зависимости? Объясните механизм трёхуровневого кэша (singletonObjects, earlySingletonObjects, singletonFactories). Почему constructor injection не спасает от циклической зависимости?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Analysis of Spring Source Code (Part 2) — How to resolve circular dependencies (Medium)](https://medium.com/@wyr95626_29886/analysis-of-spring-source-code-part-2-how-to-resolve-circular-dependencies-cb8d713d4086)

Spring поддерживает три уровня кэша для управления singleton-бинами. **singletonObjects** хранит полностью созданные singleton-бины, прошедшие весь жизненный цикл. **earlySingletonObjects** содержит объекты, раскрытые заранее («early exposed»): они уже инстанциированы, но ещё не полностью инициализированы. **singletonFactories** хранит фабрики объектов (`ObjectFactory`), позволяющие получить бин до завершения его инициализации. При запросе бина Spring последовательно проверяет сначала первый уровень, затем второй и третий. Когда вызывается `ObjectFactory.getObject()` из третьего кэша, результат помещается во второй кэш, а запись из третьего удаляется. Третий уровень кэша необходим для поддержки AOP: без него все бины получали бы AOP-прокси немедленно при инстанциации, а не по требованию. Constructor injection не разрешает циклические зависимости, так как инстанциация происходит до помещения бина в какой-либо кэш — бин невозможно закэшировать незавершённым, если его конструктор ещё не выполнился.

#### Ответ от Claude

**Что такое циклическая зависимость**

Циклическая зависимость возникает, когда бин A зависит от бина B, а бин B — от бина A (или через цепочку: A → B → C → A).

**Трёхуровневый кэш Spring**

Spring использует три структуры данных в классе `DefaultSingletonBeanRegistry`:

```java
// Уровень 1: полностью инициализированные singleton-бины
Map<String, Object> singletonObjects;

// Уровень 2: «ранние» объекты — инстанциированы, но ещё не инициализированы полностью
Map<String, Object> earlySingletonObjects;

// Уровень 3: фабрики, которые могут вернуть ранний (возможно, проксированный) объект
Map<String, ObjectFactory<?>> singletonFactories;
```

**Механизм разрешения (шаг за шагом на примере A → B → A)**

1. Spring начинает создавать бин A: вызывает конструктор, получает «голый» объект A.
2. В `singletonFactories` (уровень 3) регистрируется `ObjectFactory` для A — лямбда, которая вызывает `getEarlyBeanReference(A)`.
3. Spring переходит к внедрению зависимостей в A и обнаруживает, что нужен бин B.
4. Spring начинает создавать бин B: вызывает конструктор, регистрирует фабрику для B в уровне 3.
5. Spring переходит к внедрению зависимостей в B и обнаруживает, что нужен бин A.
6. Spring ищет A: уровень 1 пуст, уровень 2 пуст, но в уровне 3 есть фабрика.
7. Вызывается `ObjectFactory.getObject()` — возвращается ранняя ссылка на A (при необходимости — уже обёрнутая в AOP-прокси).
8. Ранняя ссылка на A перемещается из уровня 3 в уровень 2, бин B получает её и завершает инициализацию.
9. Полностью инициализированный B помещается в уровень 1.
10. Возврат к созданию A: внедрение B завершено, A проходит полную инициализацию, перемещается из уровня 2 в уровень 1.

**Зачем нужен именно третий уровень (а не два)?**

Это ключевой вопрос. Если бин A должен быть обёрнут в AOP-прокси, в другие бины нужно внедрить именно прокси, а не исходный объект. Третий уровень позволяет отложить создание прокси до момента, когда он реально понадобится (при обнаружении циклической зависимости). Если бы Spring создавал AOP-прокси сразу (в уровне 2), это нарушало бы принцип: прокси создаётся в `BeanPostProcessor` после полной инициализации, а не в момент инстанциации. `ObjectFactory` в уровне 3 вызывает `SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference()`, что позволяет корректно создать прокси именно в этот момент.

**Почему constructor injection не решает проблему**

При constructor injection Spring не может создать объект до выполнения конструктора. Весь смысл трёхуровневого кэша — в том, что «голый» объект, созданный через конструктор, помещается в кэш ещё до внедрения зависимостей. При constructor injection бин A ещё не существует как объект (конструктор не завершился), а значит, нечего помещать в `singletonFactories`. Попытка создать A требует B, создание B требует A — Spring бросает `BeanCurrentlyInCreationException`.

При setter/field injection объект создаётся в два этапа: сначала `new A()` (конструктор без аргументов), потом внедрение полей. Именно после первого этапа объект и регистрируется в кэше уровня 3.

**Ограничения механизма**

- Работает только для **singleton**-бинов. Для prototype-бинов циклические зависимости не разрешаются (Spring не хранит ранние ссылки на prototype-экземпляры).
- Не работает при **constructor injection** (см. выше).
- В Spring Boot 2.6+ циклические зависимости через setter/field injection **запрещены по умолчанию** и вызывают ошибку при старте. Включить их можно через `spring.main.allow-circular-references=true`, но это антипаттерн и сигнал о плохой архитектуре.

---

### Вопрос 27. В чём разница между JDK Dynamic Proxy и CGLIB-прокси в Spring AOP? Когда Spring выбирает один из них, и какие ограничения у каждого (final-классы, private-методы, отсутствие интерфейса)?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Proxying Mechanisms — Spring Framework Documentation](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)

Spring AOP автоматически выбирает механизм проксирования в зависимости от целевого объекта. Если объект реализует хотя бы один интерфейс — используется JDK Dynamic Proxy, при этом проксируются все интерфейсы целевого типа. Если объект не реализует никаких интерфейсов — создаётся CGLIB-прокси (динамически сгенерированный подкласс). CGLIB переупакован в модуль `spring-core`. Ограничения CGLIB: final-классы не могут быть проксированы (невозможно унаследоваться), final-методы не могут быть заadvice-ованы (невозможно переопределить), private-методы также не перехватываются. Принудительно использовать CGLIB можно через `@EnableAspectJAutoProxy(proxyTargetClass = true)`. Критическое ограничение обоих механизмов — проблема self-invocation: если метод объекта вызывает другой метод через `this`, вызов обходит прокси и аспект не применяется.

#### Ответ от Claude

**JDK Dynamic Proxy**

Механизм, встроенный в JDK (`java.lang.reflect.Proxy`). Создаёт объект-прокси, реализующий те же интерфейсы, что и целевой класс. Все вызовы методов делегируются через `InvocationHandler`, который применяет advice и перенаправляет вызов к реальному объекту.

Технически: прокси-класс генерируется в рантайме, наследуется от `java.lang.reflect.Proxy` и имплементирует заданные интерфейсы. Вызов любого метода интерфейса проходит через `InvocationHandler.invoke()`.

**CGLIB Proxy**

Использует библиотеку CGLIB (Code Generation Library), встроенную в `spring-core`. Создаёт динамический подкласс целевого класса в рантайме, переопределяя его методы. Перехват вызовов осуществляется через `MethodInterceptor`.

Технически: генерируется байткод нового класса, наследующегося от целевого. Переопределённые методы вызывают interceptor, который применяет advice, а затем вызывает `super.method()`.

**Как Spring выбирает прокси**

| Условие | Тип прокси |
|---|---|
| Целевой класс реализует хотя бы один интерфейс | JDK Dynamic Proxy |
| Целевой класс не реализует интерфейсов | CGLIB |
| Явно задано `proxyTargetClass = true` | CGLIB (принудительно) |
| Spring Boot 2.x (без явной настройки) | CGLIB (изменено по умолчанию) |

В Spring Boot 2.0 поведение по умолчанию изменилось в пользу CGLIB: `spring.aop.proxy-target-class=true`. Это решило ряд проблем с внедрением бинов через тип класса, а не интерфейса. Вернуть JDK Dynamic Proxy можно, явно указав `spring.aop.proxy-target-class=false`.

**Ограничения JDK Dynamic Proxy**

- Требует наличия интерфейса: невозможно проксировать класс без интерфейса.
- Перехватывает только методы, объявленные в интерфейсе. Публичные методы класса, не вошедшие в интерфейс, advice не получат.
- Прокси-объект нельзя привести к типу исходного класса (`ClassCastException`) — только к интерфейсу.

**Ограничения CGLIB**

- **`final`-классы** не могут быть проксированы — подкласс от `final`-класса создать невозможно.
- **`final`-методы** не могут быть перехвачены — их невозможно переопределить в подклассе.
- **`private`-методы** не перехватываются — переопределение недоступно вне класса.
- **Методы с пакетной видимостью** из родительского класса в другом пакете эффективно недоступны для переопределения.
- Ограничения модульной системы Java (JPMS): для классов из `java.base` и других системных модулей требуется флаг `--add-opens`.

**Общее ограничение обоих механизмов: self-invocation**

Если метод `foo()` класса вызывает `this.bar()`, вызов идёт напрямую к объекту-мишени, минуя прокси. Аспект на `bar()` не сработает. Решения:
1. Рефакторинг (предпочтительно): вынести `bar()` в отдельный бин.
2. Self-injection: внедрить бин сам в себя и вызывать `self.bar()`.
3. `AopContext.currentProxy()` — работает, но жёстко связывает код со Spring AOP.

**Сравнительная таблица**

| Критерий | JDK Dynamic Proxy | CGLIB |
|---|---|---|
| Требует интерфейс | Да | Нет |
| `final`-классы | Не применимо | Не поддерживается |
| `final`-методы | Не применимо | Не поддерживается |
| `private`-методы | Не перехватываются | Не перехватываются |
| Механизм | `java.lang.reflect.Proxy` | Генерация подкласса |
| Зависимость | JDK (встроено) | `spring-core` |
| Default в Spring Boot 2.x | Нет | Да |
### Вопрос 28. Почему @Transactional не работает при вызове метода внутри того же класса (self-invocation)? Каков механизм — и как это правильно исправить (AopContext.currentProxy(), self-injection, рефакторинг)?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Proxying Mechanisms :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)

Spring AOP основан на прокси-объектах. Когда внешний код вызывает метод бина, вызов идёт через прокси, который применяет advice (в том числе транзакционный). Однако при self-invocation метод вызывает другой метод через ссылку `this`, минуя прокси:

```java
public class SimplePojo implements Pojo {
    public void foo() {
        this.bar(); // вызов идёт напрямую, прокси обходится
    }
    public void bar() { ... }
}
```

Официальная документация явно указывает: «self-invocation (in effect, a method within the target object calling another method of the target object) does not lead to an actual transaction at runtime even if the invoked method is marked with @Transactional».

**Рекомендуемые решения (по убыванию предпочтительности):**

1. **Рефакторинг** — вынести транзакционный метод в отдельный бин. Самый чистый подход, не привязывает код к Spring AOP.
2. **Self-injection** — ввести в класс зависимость на самого себя через `@Autowired` (с `@Lazy` для Spring Boot):
   ```java
   @Autowired @Lazy private MyService self;
   // ...
   self.bar(); // вызов идёт через прокси
   ```
3. **AopContext.currentProxy()** — крайняя мера, привязывает код к Spring AOP:
   ```java
   ((MyService) AopContext.currentProxy()).bar();
   // Требует: @EnableAspectJAutoProxy(exposeProxy = true)
   ```

#### Ответ от Claude

**Корневая причина.** Spring реализует `@Transactional` через AOP-прокси (по умолчанию — CGLIB, создающий подкласс целевого класса; либо JDK dynamic proxy на основе интерфейса). Прокси-объект перехватывает вызовы, поступающие снаружи: добавляет advice (открытие/закрытие транзакции), а затем делегирует реальному объекту. Когда метод бина вызывает другой метод через `this`, он обращается напрямую к реальному объекту, а не к прокси-обёртке, поэтому `TransactionInterceptor` не срабатывает.

```
Внешний код --> [ Прокси (TransactionInterceptor) ] --> [ Реальный объект ]
                                                              |
                                                         this.bar()  <-- прокси обходится
```

**Эта проблема затрагивает не только `@Transactional`**, но и любые Spring AOP аннотации: `@Cacheable`, `@Async`, `@Secured`, пользовательские аспекты.

**Три способа исправления:**

**1. Рефакторинг (предпочтительно)** — выделить транзакционный метод в отдельный Spring-бин:
```java
@Service
public class BarService {
    @Transactional
    public void bar() { ... }
}

@Service
public class FooService {
    @Autowired private BarService barService;

    public void foo() {
        barService.bar(); // внешний вызов через прокси — работает
    }
}
```

**2. Self-injection** — Spring создаёт прокси-обёртку и внедряет её в сам же бин. `@Lazy` нужен, чтобы избежать ошибки циклической зависимости при загрузке контекста:
```java
@Service
public class MyService {
    @Autowired @Lazy private MyService self;

    public void foo() {
        self.bar(); // вызов идёт через прокси
    }

    @Transactional
    public void bar() { ... }
}
```

**3. AopContext.currentProxy()** — явно получить текущий прокси из ThreadLocal-хранилища. Использовать только как последнее средство, так как это жёстко привязывает код к Spring AOP:
```java
// Требуется включить: @EnableAspectJAutoProxy(exposeProxy = true)
public void foo() {
    ((MyService) AopContext.currentProxy()).bar();
}
```
Если `exposeProxy = true` не установлено, метод `AopContext.currentProxy()` бросит `IllegalStateException`.

**4. AspectJ weaving (compile-time или load-time)** — при использовании режима `@EnableTransactionManagement(mode = AdviceMode.ASPECTJ)` прокси не создаётся вовсе: байткод целевого класса модифицируется напрямую, и self-invocation работает корректно. Однако это требует дополнительной настройки сборки/загрузки классов.

**Итог:** Официальная документация Spring явно называет рефакторинг «лучшим, наименее инвазивным подходом». `AopContext.currentProxy()` документация категорически не рекомендует для production-кода.

---

### Вопрос 29. Что произойдёт, если пометить @Transactional private-метод? Почему Spring молча проигнорирует аннотацию, и как это связано с прокси-механизмом?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Using @Transactional :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

Официальная документация Spring Framework явно указывает:

> «In proxy mode (which is the default), only external method calls coming in through the proxy are intercepted. Self-invocation (in effect, a method within the target object calling another method of the target object) does not lead to an actual transaction at runtime even if the invoked method is marked with @Transactional.»

По поводу видимости методов документация Spring 6.0+ сообщает следующее:

- **До Spring 6.0**: аннотация `@Transactional` должна была применяться только к методам с `public` видимостью. Аннотирование `protected`, `private` или методов с видимостью пакета не вызывало ошибку, но аннотированный метод не проявлял сконфигурированного транзакционного поведения.
- **С Spring 6.0**: для прокси на основе классов (CGLIB) поддерживаются также `protected` и package-private методы. Для прокси на основе интерфейсов (JDK dynamic proxy) по-прежнему требуется `public` видимость.
- **Private методы**: не поддерживаются ни в какой версии Spring.

Ошибка при этом не бросается — Spring молча игнорирует аннотацию.

#### Ответ от Claude

**Что происходит технически.** Когда Spring создаёт прокси-объект, он может перехватывать только те методы, к которым имеет доступ:

- **CGLIB-прокси** создаёт подкласс целевого класса. Подкласс в Java может переопределить (override) только `public`, `protected` и методы с видимостью пакета. `private` методы **не наследуются и не могут быть переопределены**, поэтому CGLIB не способен их перехватить.
- **JDK dynamic proxy** работает на основе интерфейсов. `private` методы не могут присутствовать в интерфейсе по определению языка Java.

Таким образом, в обоих случаях `private` метод остаётся в целевом объекте «невидимым» для прокси — вызов всегда идёт напрямую, минуя `TransactionInterceptor`.

**Важная особенность: Spring не бросает исключение.** Это является источником трудно обнаруживаемых багов: разработчик добавляет `@Transactional` на `private` метод, приложение запускается без ошибок, но транзакция не создаётся. Данные могут записываться вне транзакции или не записываться вовсе в зависимости от логики.

**Изменения в Spring 6.0:**
```
До Spring 6.0:
  public    → работает (CGLIB и JDK proxy)
  protected → не работает
  package   → не работает
  private   → не работает

Spring 6.0+:
  public    → работает (CGLIB и JDK proxy)
  protected → работает только для CGLIB
  package   → работает только для CGLIB
  private   → не работает ни при каких условиях
```

**Три способа решения:**

1. **Сделать метод `public`** — простейший вариант. При необходимости скрыть от внешнего API использовать пакетную структуру.

2. **Использовать AspectJ weaving** — при `@EnableTransactionManagement(mode = AdviceMode.ASPECTJ)` байткод класса изменяется на этапе компиляции или загрузки, прокси не нужен, и `private` методы становятся доступны для advice. Требует дополнительной настройки (aspectj-maven-plugin или агент загрузки классов).

3. **Вынести логику в отдельный бин** — `public` метод нового `@Service`-бина будет корректно перехватываться прокси.

**Практическое правило:** применяйте `@Transactional` только к `public` методам, если не используете CGLIB и Spring 6.0+ (для `protected`/package) или AspectJ (для любой видимости). Никогда — к `private` методам.

---

### Вопрос 30. Объясните все режимы распространения транзакций (REQUIRED, REQUIRES_NEW, NESTED, SUPPORTS, MANDATORY, NOT_SUPPORTED, NEVER). Чем NESTED отличается от REQUIRES_NEW с точки зрения savepoint?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Transaction Propagation :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

Официальная документация Spring Framework описывает режимы распространения следующим образом:

**PROPAGATION_REQUIRED** (по умолчанию): применяет физическую транзакцию локально, если её нет, либо присоединяется к существующей внешней транзакции. Создаёт логические области транзакции для каждого метода, все они отображаются на одну физическую транзакцию. Если внутренняя область устанавливает флаг rollback-only, внешняя транзакция не может быть зафиксирована и бросает `UnexpectedRollbackException`.

**PROPAGATION_REQUIRES_NEW**: всегда использует независимую физическую транзакцию для каждой области, никогда не участвует в существующей. Внутренняя и внешняя транзакции могут фиксироваться и откатываться независимо. Требует пула соединений, размер которого превышает количество одновременных потоков минимум на 1.

**PROPAGATION_NESTED**: использует одну физическую транзакцию с несколькими savepoint'ами. Внутренняя область может откатываться к savepoint без отмены внешней транзакции. Работает только с JDBC resource transactions (например, `DataSourceTransactionManager`).

**PROPAGATION_SUPPORTS**: участвует в транзакции, если она существует; в противном случае выполняется нетранзакционно.

**PROPAGATION_MANDATORY**: требует существующей транзакции; бросает исключение, если её нет.

**PROPAGATION_NOT_SUPPORTED**: приостанавливает любую существующую транзакцию и выполняется нетранзакционно.

**PROPAGATION_NEVER**: должен выполняться без транзакции; бросает исключение, если транзакция существует.

#### Ответ от Claude

Режим распространения (propagation) сообщает Spring, что делать с транзакцией при вызове метода, помеченного `@Transactional`.

**REQUIRED** (значение по умолчанию)
- Если внешняя транзакция существует — присоединяется к ней (logical transaction scope).
- Если не существует — открывает новую физическую транзакцию.
- Все вложенные вызовы делят одну физическую транзакцию. Если любой вложенный метод выставит rollback-only, при коммите внешней транзакции будет брошен `UnexpectedRollbackException`.
- Применение: сервисный слой, большинство бизнес-операций.

**REQUIRES_NEW**
- Всегда создаёт **новую независимую физическую транзакцию** (новое соединение с БД).
- Текущая внешняя транзакция **приостанавливается** (suspended) до завершения внутренней.
- Внутренняя транзакция может зафиксироваться или откатиться независимо от внешней.
- После завершения внутренней транзакции внешняя возобновляется.
- Риск: исчерпание пула соединений при глубокой вложенности.
- Применение: аудит-лог, который нужно сохранить даже при откате основной операции.

**NESTED**
- Если внешняя транзакция существует — создаёт **savepoint** внутри неё (одна физическая транзакция).
- Если внутренняя операция откатывается — откат происходит **до savepoint**, внешняя транзакция продолжается.
- Если внешняя транзакция откатывается полностью — вся работа, включая NESTED-участок, также отменяется.
- Требует поддержки JDBC savepoints базой данных (PostgreSQL, Oracle, H2, MySQL 5.0.3+).
- Работает только с `DataSourceTransactionManager`, не работает с JPA/Hibernate TransactionManager напрямую.
- Применение: частичная запись в рамках одной большой операции (пакетная обработка с частичными откатами).

**SUPPORTS**
- Если транзакция существует — участвует в ней.
- Если нет — выполняется **нетранзакционно**.
- Применение: методы чтения, которые работают корректно и с транзакцией, и без неё.

**MANDATORY**
- Если транзакция существует — участвует в ней.
- Если нет — бросает `IllegalTransactionStateException`.
- Применение: методы, которые **обязаны** вызываться в контексте уже открытой транзакции (защита от случайного вызова без транзакции).

**NOT_SUPPORTED**
- Всегда выполняется **нетранзакционно**.
- Если транзакция существует — **приостанавливает** её на время вызова.
- Применение: операции, несовместимые с транзакцией (например, вызов хранимой процедуры, несовместимой с активной транзакцией).

**NEVER**
- Всегда выполняется нетранзакционно.
- Если транзакция существует — бросает `IllegalTransactionStateException`.
- Применение: явный запрет транзакций; строже, чем NOT_SUPPORTED.

**Ключевое различие NESTED vs REQUIRES_NEW:**

| Аспект | NESTED | REQUIRES_NEW |
|---|---|---|
| Физических транзакций (соединений) | Одна | Две (или более) |
| Механизм изоляции | JDBC savepoint | Отдельная транзакция |
| Откат внутренней части | Только до savepoint | Полный откат независимой транзакции |
| Откат внешней транзакции | Отменяет всё, включая NESTED | Не влияет на уже зафиксированную внутреннюю |
| Блокировки БД | Удерживаются до конца внешней TX | Освобождаются после завершения внутренней TX |
| Ресурсы пула соединений | Одно соединение | Дополнительное соединение |
| Поддержка ORM (JPA/Hibernate) | Ограничена, требует DataSourceTM | Полная поддержка |
| Поддержка БД | Только JDBC savepoint-capable | Любые транзакционные БД |

**Практическая мнемоника:**
- `REQUIRES_NEW` — «я хочу свою полностью независимую транзакцию».
- `NESTED` — «я хочу иметь возможность частичного отката, но оставаться частью внешней транзакции».

**Сводная таблица:**

| Режим | Нет внешней TX | Есть внешняя TX |
|---|---|---|
| REQUIRED | Создаёт новую | Присоединяется |
| REQUIRES_NEW | Создаёт новую | Приостанавливает, создаёт свою |
| NESTED | Создаёт новую | Создаёт savepoint |
| SUPPORTS | Нетранзакционно | Присоединяется |
| MANDATORY | Исключение | Присоединяется |
| NOT_SUPPORTED | Нетранзакционно | Приостанавливает |
| NEVER | Нетранзакционно | Исключение |
### Вопрос 31. По умолчанию @Transactional откатывается только на RuntimeException и Error. Что будет, если выброшено checked IOException? Как изменить поведение через rollbackFor/noRollbackFor?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Rolling Back a Declarative Transaction :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html)

Инфраструктура транзакций Spring по умолчанию помечает транзакцию для отката только в случае непроверяемых (runtime) исключений — то есть когда выброшенное исключение является экземпляром или наследником `RuntimeException`. Ошибки (`Error`) также вызывают откат. Проверяемые (checked) исключения, выброшенные из транзакционного метода, по умолчанию **не вызывают откат**: транзакция фиксируется (commit).

Поведение можно изменить через правила отката. Атрибут `rollbackFor` позволяет указать типы исключений, которые должны вызывать откат:

```xml
<tx:method name="get*" read-only="true" rollback-for="NoProductInStockException"/>
```

или через аннотацию:

```java
@Transactional(rollbackFor = IOException.class)
public void processOrder() throws IOException { ... }
```

Атрибут `noRollbackFor` запрещает откат при определённых исключениях (даже если они являются `RuntimeException`):

```java
@Transactional(noRollbackFor = InstrumentNotFoundException.class)
public void updateStock() { ... }
```

Если несколько правил применимы одновременно, побеждает наиболее специфичное совпадение (наименее удалённый предок в иерархии). Помимо типобезопасных атрибутов `rollbackFor`/`noRollbackFor` существуют строковые варианты `rollbackForClassName`/`noRollbackForClassName` — они работают на основе подстрочного совпадения имени класса, что несёт риск случайных совпадений (например, шаблон `"Exception"` покроет почти все исключения).

Программный откат через `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()` тоже возможен, но документация настоятельно рекомендует декларативный подход.

#### Ответ от Claude

**Дефолтное поведение**

Аннотация `@Transactional` следует соглашению EJB: откат происходит автоматически только при:
- `RuntimeException` и любых её подклассах (непроверяемые исключения);
- `Error` (критические ошибки JVM).

Проверяемое исключение `IOException` (наследник `Exception`, но не `RuntimeException`) по умолчанию **не вызывает откат**. Транзакция будет зафиксирована (commit), даже если метод завершился с `IOException`. Это может привести к частичным изменениям в БД, если в методе перед выбросом исключения уже были выполнены DML-операции.

**Изменение поведения через rollbackFor**

```java
@Transactional(rollbackFor = IOException.class)
public void importData() throws IOException {
    repository.save(entity); // выполнится
    throw new IOException(); // теперь вызовет откат
}
```

Указывать можно несколько классов:

```java
@Transactional(rollbackFor = {IOException.class, SQLException.class})
```

Правило распространяется и на подклассы: `rollbackFor = IOException.class` охватит также `FileNotFoundException`, `SocketException` и другие наследники `IOException`.

**Изменение поведения через noRollbackFor**

Запрещает откат для конкретного непроверяемого исключения, которое по умолчанию его вызвало бы:

```java
@Transactional(noRollbackFor = OptimisticLockingFailureException.class)
public void update() { ... }
```

**Строковые варианты (rollbackForClassName / noRollbackForClassName)**

Работают по подстрочному совпадению с именем класса исключения:

```java
@Transactional(rollbackForClassName = "IOException")
// Покроет IOException и все подклассы с такой подстрокой в имени
```

Использовать с осторожностью: широкие паттерны вроде `"Exception"` совпадут практически с любым исключением.

**Приоритет правил**

При конфликте нескольких правил побеждает наиболее специфичное (ближайшее по иерархии исключений). Например, если задано `rollbackFor = Throwable.class` и `noRollbackFor = IOException.class`, то для `IOException` откат не произойдёт, так как `IOException` ближе по иерархии, чем `Throwable`.

**Программный откат как крайний вариант**

```java
@Transactional
public void process() {
    try {
        // логика
    } catch (IOException ex) {
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}
```

Документация рекомендует избегать этого подхода и использовать декларативные атрибуты аннотации.

---

### Вопрос 32. Чем BeanPostProcessor отличается от BeanFactoryPostProcessor? Приведите примеры встроенных реализаций Spring (AutowiredAnnotationBeanPostProcessor, ConfigurationClassPostProcessor) и объясните, на каком этапе они вызываются.

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Container Extension Points :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html)

`BeanFactoryPostProcessor` работает с **метаданными конфигурации** (определениями бинов) и вызывается до того, как контейнер создаёт какие-либо экземпляры бинов (кроме самих постпроцессоров). Он позволяет читать и изменять `BeanDefinition` — «чертежи» бинов. Типичный пример встроенной реализации — `PropertySourcesPlaceholderConfigurer`, который подставляет значения `${...}` в определениях бинов.

`BeanPostProcessor` работает с **экземплярами бинов** и вызывается после того, как бин был создан (инстанциирован). Интерфейс содержит два метода:
- `postProcessBeforeInitialization(Object bean, String beanName)` — вызывается до инициализационных callback-ов (`@PostConstruct`, `afterPropertiesSet()`, `init-method`);
- `postProcessAfterInitialization(Object bean, String beanName)` — вызывается после них.

Процессоры можно упорядочить через интерфейс `Ordered`. Если необходимо взаимодействовать с экземплярами бинов — следует использовать `BeanPostProcessor`, а не `BeanFactoryPostProcessor`, чтобы не вызвать преждевременную инстанциацию бинов.

#### Ответ от Claude

**Ключевое различие**

| Характеристика | BeanFactoryPostProcessor | BeanPostProcessor |
|---|---|---|
| Работает с | Метаданными (BeanDefinition) | Экземплярами бинов |
| Когда вызывается | До инстанциации бинов | После инстанциации, вокруг инициализации |
| Цель | Модифицировать «чертежи» бинов | Модифицировать или оборачивать готовые объекты |

**Порядок этапов в жизненном цикле контейнера**

```
1. Загрузка конфигурации (XML / аннотации / Java-config)
2. Регистрация BeanDefinition-ов
3. → BeanDefinitionRegistryPostProcessor.postProcessBeanDefinitionRegistry()
4. → BeanFactoryPostProcessor.postProcessBeanFactory()
5. Инстанциация бинов
6. → BeanPostProcessor.postProcessBeforeInitialization()
7. Инициализационные callback-и (@PostConstruct, afterPropertiesSet, init-method)
8. → BeanPostProcessor.postProcessAfterInitialization()
9. Бин готов к использованию
```

**ConfigurationClassPostProcessor (BeanFactoryPostProcessor / BeanDefinitionRegistryPostProcessor)**

Это центральный постпроцессор фабрики, реализующий также `BeanDefinitionRegistryPostProcessor` (расширение `BeanFactoryPostProcessor`) и `PriorityOrdered` с наивысшим приоритетом.

Этапы работы:
1. `postProcessBeanDefinitionRegistry()` — сканирует `@Configuration`-классы, находит и регистрирует `BeanDefinition`-ы из `@Bean`-методов, обрабатывает `@ComponentScan`, `@Import`, `@ImportResource`.
2. `postProcessBeanFactory()` — оборачивает `@Configuration`-классы CGLIB-прокси, чтобы вызовы одного `@Bean`-метода из другого возвращали синглтон из контейнера, а не создавали новый объект.

Автоматически регистрируется при использовании `<context:annotation-config/>`, `<context:component-scan/>` или `AnnotationConfigApplicationContext`.

**AutowiredAnnotationBeanPostProcessor (BeanPostProcessor)**

Реализует `BeanPostProcessor` и `MergedBeanDefinitionPostProcessor`. Вызывается на этапах до и после инициализации каждого бина.

Что делает:
1. В `postProcessMergedBeanDefinition()` — находит поля и методы, помеченные `@Autowired`, `@Value`, `@Inject`, и кэширует эту информацию.
2. В `postProcessProperties()` (Spring 5.1+) — выполняет фактическую инжекцию зависимостей в поля и setter-методы экземпляра бина.

Поддерживает `@Autowired`, `@Value` и стандартные JSR-330 аннотации (`@Inject`). Автоматически регистрируется вместе с `ConfigurationClassPostProcessor`.

**Особенности регистрации в @Configuration**

Оба типа постпроцессоров рекомендуется объявлять как `static @Bean`-методы, чтобы избежать преждевременной инстанциации конфигурационного класса:

```java
@Configuration
public class AppConfig {
    @Bean
    public static BeanFactoryPostProcessor myBfpp() {
        return new MyBeanFactoryPostProcessor();
    }

    @Bean
    public static BeanPostProcessor myBpp() {
        return new MyBeanPostProcessor();
    }
}
```

**Другие встроенные примеры**

- `BeanFactoryPostProcessor`: `PropertySourcesPlaceholderConfigurer` (подстановка `${...}`), `CustomScopeConfigurer` (регистрация кастомных скоупов).
- `BeanPostProcessor`: `CommonAnnotationBeanPostProcessor` (обработка `@Resource`, `@PostConstruct`, `@PreDestroy`), `AbstractAdvisorAutoProxyCreator` (создание AOP-прокси).

---

### Вопрос 33. Что такое AspectJ weaving и чем compile-time / load-time weaving отличается от Spring AOP runtime proxy? Когда Spring AOP недостаточно и нужен полноценный AspectJ?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Using AspectJ with Spring Applications :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/using-aspectj.html)

**Weaving (связывание)** — процесс встраивания аспектов в целевой код. Spring AOP выполняет связывание во время выполнения (runtime) путём создания прокси-объектов. AspectJ предоставляет два других варианта:

**Compile-time weaving (CTW)** — аспекты встраиваются на этапе компиляции компилятором `ajc` (AspectJ Compiler). На выходе получаются уже «прошитые» class-файлы. Требует интеграции `ajc` в сборку.

**Load-time weaving (LTW)** — аспекты встраиваются в момент загрузки классов в JVM с помощью Java-агента (`-javaagent:spring-instrument.jar`) и трансформаторов, реализующих `java.lang.instrument.ClassFileTransformer`. Конфигурируется через `META-INF/aop.xml`.

Spring поддерживает LTW через:
```java
@Configuration
@EnableLoadTimeWeaving
public class ApplicationConfiguration {}
```

Пример аспекта с LTW использует стандартный `@Aspect` + конфигурацию в `aop.xml`:
```xml
<aspectj>
    <weaver>
        <include within="com.xyz..*"/>
    </weaver>
    <aspects>
        <aspect name="com.xyz.ProfilingAspect"/>
    </aspects>
</aspectj>
```

Документация рекомендует: если нужно применять аспекты к объектам, не управляемым контейнером Spring, — использовать AspectJ.

#### Ответ от Claude

**Что такое weaving**

Weaving (связывание, «вплетение») — процесс интеграции кода аспекта в целевой код приложения для создания advice-поведения. Существует три момента, когда это может происходить:

**1. Compile-time weaving (CTW) — связывание во время компиляции**

- Аспекты и исходный код компилируются совместно компилятором `ajc`.
- Результат — уже модифицированные `.class`-файлы, содержащие вплетённый код аспектов.
- Требования: `ajc` в цепочке сборки (Maven plugin `aspectj-maven-plugin` или Gradle аналог).
- Преимущество: нулевые накладные расходы в рантайме; максимальная производительность.
- Ограничение: необходим исходный код классов для компиляции.

**2. Load-time weaving (LTW) — связывание при загрузке классов**

- Аспекты встраиваются в момент загрузки `.class`-файлов JVM с помощью Java Instrumentation API.
- Требует запуска JVM с флагом `-javaagent:path/to/spring-instrument.jar` (или `aspectjweaver.jar`).
- Не нужен исходный код целевых классов — работает на байткоде.
- Конфигурируется через `META-INF/aop.xml` в classpath.
- Удобен для библиотечных классов и фреймворков, исходник которых недоступен.

**3. Runtime proxy weaving — связывание во время выполнения (Spring AOP)**

- Spring создаёт прокси-объекты при инстанциации бинов.
- Используется JDK Dynamic Proxy (если бин реализует интерфейс) или CGLIB (если нет).
- Аспекты применяются только к вызовам, проходящим через прокси-объект.
- Нет необходимости в компиляторе аспектов или агентах JVM.

**Сравнительная таблица**

| Характеристика | Spring AOP (runtime) | AspectJ CTW | AspectJ LTW |
|---|---|---|---|
| Момент связывания | Runtime | Compile-time | Class loading |
| Инструменты | Нет доп. инструментов | ajc compiler | Java agent |
| Join points | Только выполнение методов | Любые | Любые |
| Объекты вне Spring | Нет | Да | Да |
| final методы/классы | Нет | Да | Да |
| Self-invocation | Нет | Да | Да |
| Производительность | Накладные расходы прокси | Максимальная | Небольшой overhead при загрузке |
| Сложность настройки | Минимальная | Средняя | Средняя |

**Когда Spring AOP недостаточно и нужен AspectJ**

1. **Self-invocation (вызов метода через `this`)**

   ```java
   @Component
   public class OrderService {
       @Transactional
       public void createOrder() {
           this.notifyListeners(); // аспект НЕ применится!
       }

       @Transactional
       public void notifyListeners() { ... }
   }
   ```
   При вызове `this.notifyListeners()` обращение идёт напрямую к объекту, минуя прокси. С AspectJ (CTW или LTW) аспект вплетён прямо в байткод и вызовется при любом обращении.

2. **Advise объектов вне Spring-контейнера**

   ```java
   // Создан через new или ORM, не управляется Spring
   Account account = new Account();
   account.transfer(funds); // Spring AOP не перехватит
   ```
   AspectJ перехватит вызов, так как аспект вплетён в байткод класса `Account`.

3. **Перехват final методов и final классов**

   CGLIB создаёт подклассы, а `final` запрещает наследование. AspectJ weaving модифицирует байткод напрямую без создания подклассов.

4. **Join points кроме выполнения методов**

   Spring AOP поддерживает исключительно `execution()`. AspectJ поддерживает:
   - `get()` / `set()` — чтение и запись полей;
   - `call()` — место вызова метода (а не его тело);
   - `initialization()` / `preinitialization()` — конструкторы;
   - `handler()` — блоки catch;
   - `staticinitialization()` — статические инициализаторы;
   - `cflow()` / `cflowbelow()` — управление потоком исполнения.

5. **Производительность**

   AspectJ CTW не имеет рантаймовых накладных расходов (бенчмарки показывают разницу в 8–35 раз в пользу AspectJ). Критичные в производительности участки кода выигрывают от CTW.

**Аннотация @Configurable — мост между Spring и AspectJ**

Spring предоставляет `@Configurable` для внедрения зависимостей в объекты, созданные вне контейнера (через `new` или ORM):

```java
@Configurable
public class Account {
    @Autowired
    private FundsTransferService fundsTransferService;
}
```

Требует AspectJ LTW или CTW и `@EnableSpringConfigured` в конфигурации.

**Рекомендация из документации Spring**

> «Используйте Spring AOP, если нужно применять аспекты только к методам бинов Spring-контейнера. Если нужно применять аспекты к объектам не под управлением Spring (например, доменным объектам) — используйте AspectJ.»

Таким образом, Spring AOP покрывает большинство практических задач (транзакции, безопасность, логирование на уровне сервисов). Полноценный AspectJ требуется в случаях тонкой инструментации байткода, работы с не-Spring-объектами или перехвата конструкторов/полей.
### Вопрос 34. Если у вас два @Aspect, которые применяются к одному joinpoint, в каком порядке они выполнятся? Как управлять порядком через @Order и Ordered, и что будет, если порядок не задан?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Declaring Advice :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/ataspectj/advice.html)

Когда несколько советов из разных аспектов должны выполниться на одном joinpoint, Spring AOP следует правилам приоритетов AspectJ. При движении «на входе» (before-фаза) совет с наивысшим приоритетом выполняется первым. При движении «на выходе» (after-фаза) совет с наивысшим приоритетом выполняется последним.

Управлять порядком можно двумя способами:
1. Аннотация `@Order` на классе аспекта.
2. Реализация интерфейса `org.springframework.core.Ordered` в классе аспекта.

Более низкое числовое значение `Ordered.getOrder()` или значения `@Order` означает более высокий приоритет. Если порядок явно не задан — порядок выполнения нескольких аспектов на одном joinpoint **не определён**.

#### Ответ от Claude

**Базовая ситуация: порядок не задан**

Если два `@Aspect`-класса применяются к одному joinpoint и ни один из них не задаёт порядок, Spring AOP гарантирует лишь то, что оба совета выполнятся, но относительный порядок их выполнения **не определён** (undefined). Это прямо закреплено в документации Spring: «Unless you specify otherwise, the execution order is undefined». Полагаться на неявный порядок нельзя.

**Управление через @Order**

Аннотация `@Order` ставится на класс аспекта:

```java
@Aspect
@Order(1)
public class SecurityAspect { ... }

@Aspect
@Order(2)
public class LoggingAspect { ... }
```

Правила приоритета:
- Меньшее числовое значение = более высокий приоритет.
- Аспект без явного `@Order` получает приоритет `Ordered.LOWEST_PRECEDENCE` (Integer.MAX_VALUE) и выполняется после всех явно упорядоченных аспектов.

**Управление через интерфейс Ordered**

Альтернативно класс аспекта может реализовать `org.springframework.core.Ordered`:

```java
@Aspect
public class SecurityAspect implements Ordered {
    @Override
    public int getOrder() {
        return 1;
    }
}
```

Семантика та же, что и у `@Order`.

**Порядок выполнения при заданных приоритетах**

Поведение описывается метафорой «на входе / на выходе» (on the way in / on the way out):

- **«На входе»** (before-фаза, начало @Around до вызова proceed): аспект с **наивысшим приоритетом** (наименьшее число) выполняется **первым**. Если `@Order(1)` у `AspectA` и `@Order(2)` у `AspectB`, то `AspectA.before` → `AspectB.before` → целевой метод.
- **«На выходе»** (after-фаза, после вызова proceed или возврата из метода): аспект с **наивысшим приоритетом** выполняется **последним**. То есть `AspectB.after` → `AspectA.after`.

Аналогия — вложенные обёртки: аспект с наименьшим `@Order` — внешняя обёртка. Он первым «входит» и последним «выходит».

**Порядок советов внутри одного @Aspect**

Если два совета одного типа (например, два `@Before`) определены в одном классе `@Aspect`, их порядок также не определён (в Java нет гарантированного порядка объявления методов через reflection). Решение — разнести советы в разные классы `@Aspect` и использовать `@Order`.

**Резюме**

| Ситуация | Порядок |
|---|---|
| Два @Aspect, порядок не задан | Не определён |
| @Order(N) — меньшее N | Выполняется первым «на входе», последним «на выходе» |
| Два совета одного типа в одном @Aspect | Не определён |
| Без @Order | Приоритет Ordered.LOWEST_PRECEDENCE |

---

### Вопрос 35. Как работает @Around advice: что такое ProceedingJoinPoint.proceed(), что будет, если не вызвать proceed(), и как @Around соотносится с @Before/@After по порядку выполнения?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Declaring Advice :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/aop/ataspectj/advice.html)

Around advice объявляется аннотацией `@Around` и «оборачивает» выполнение подходящего метода. Метод совета должен:
- возвращать `Object`;
- принимать первым параметром `ProceedingJoinPoint`.

Вызов `pjp.proceed()` передаёт управление следующему совету в цепочке или самому целевому методу. Существует перегрузка `proceed(Object[])` — для передачи изменённых аргументов. Метод `proceed()` может быть вызван один раз, несколько раз или не вызван вовсе — все варианты допустимы. Значение, возвращённое around advice, является значением, которое увидит вызывающий код.

#### Ответ от Claude

**Что такое @Around advice**

`@Around` — самый мощный тип advice в Spring AOP. Он полностью оборачивает выполнение joinpoint: может выполнять код до и после целевого метода, изменять аргументы, перехватывать возвращаемое значение или исключение, и даже полностью заменять вызов метода.

```java
@Aspect
public class ProfilingAspect {

    @Around("execution(* com.example.service.*.*(..))")
    public Object profile(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();          // вызов целевого метода
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("Elapsed: " + elapsed + "ms");
        return result;
    }
}
```

**ProceedingJoinPoint.proceed()**

`ProceedingJoinPoint` — подкласс `JoinPoint`, доступный только в `@Around` advice. Метод `proceed()` передаёт управление:
1. Следующему advice в цепочке (если таковой есть).
2. Целевому методу (если больше нет advice).

Перегрузка `proceed(Object[] args)` позволяет передать изменённые аргументы:

```java
String modified = preProcess(originalArg);
return pjp.proceed(new Object[]{ modified });
```

**Что будет, если не вызвать proceed()**

Если `proceed()` не вызван, целевой метод **не выполнится вовсе**. Around advice возвращает то, что вернул сам (или `null`). Это легальное поведение, используемое, например, в кешировании:

```java
@Around("execution(* findUser(..))")
public Object cachedFind(ProceedingJoinPoint pjp) throws Throwable {
    Object cached = cache.get(pjp.getArgs()[0]);
    if (cached != null) {
        return cached;   // proceed() не вызван — метод не выполняется
    }
    Object result = pjp.proceed();
    cache.put(pjp.getArgs()[0], result);
    return result;
}
```

Важно: если объявить возвращаемый тип advice как `void` вместо `Object`, вызывающий код всегда получит `null`, даже если целевой метод возвращает значение. Документация Spring рекомендует всегда возвращать `Object`.

**Соотношение @Around с @Before и @After по порядку выполнения**

Внутри одного `@Aspect` Spring 5.2.7+ устанавливает строгий приоритет типов advice (от высшего к низшему):

1. `@Around`
2. `@Before`
3. `@After`
4. `@AfterReturning`
5. `@AfterThrowing`

На практике это означает следующую последовательность для одного аспекта при успешном выполнении метода:

```
@Around (до proceed())
  → @Before
    → целевой метод
  → @AfterReturning
  → @After        ← выполняется как "finally", после @AfterReturning
@Around (после proceed())
```

`@After` следует семантике «after finally» в AspectJ — он выполняется всегда независимо от исхода, как блок `finally`. `@AfterReturning` — только при успехе, `@AfterThrowing` — только при исключении. При этом `@AfterThrowing` не получает исключения, брошенные самим `@After`-методом — только исключения из целевого joinpoint.

**Практическая рекомендация**

Документация Spring прямо советует использовать наименее мощный тип advice, достаточный для задачи: если достаточно `@Before` — не используйте `@Around`. Это снижает риск случайно не вызвать `proceed()` или вернуть неверное значение.

---

### Вопрос 36. Что такое BeanDefinition и как ApplicationContext строит граф зависимостей перед созданием бинов? Как @DependsOn влияет на порядок инициализации?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Bean Overview :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/beans/definition.html)

`BeanDefinition` — объект, содержащий метаданные бина: имя класса реализации, поведенческие настройки (scope, lifecycle-коллбэки), ссылки на зависимости (collaborators), а также другие параметры конфигурации — режим autowiring, lazy-init, методы инициализации и уничтожения, аргументы конструктора и свойства. ApplicationContext читает конфигурационные метаданные (XML, Java-конфиг, аннотации) и создаёт `BeanDefinition`-объекты для каждого бина. Зависимости между бинами выражаются через свойства, аргументы конструктора или аргументы фабричного метода. Синглтоны по умолчанию создаются при старте контейнера (eager pre-instantiation), что позволяет обнаружить ошибки конфигурации немедленно.

#### Ответ от Claude

**Что такое BeanDefinition**

`BeanDefinition` (интерфейс `org.springframework.beans.factory.config.BeanDefinition`) — внутреннее представление метаданных бина в контейнере Spring. Он описывает **как** контейнер должен создать и настроить конкретный бин.

Ключевые свойства `BeanDefinition`:

| Свойство | Назначение |
|---|---|
| `beanClassName` | Полное имя класса реализации |
| `scope` | singleton / prototype / request / session и др. |
| `constructorArgumentValues` | Аргументы конструктора |
| `propertyValues` | Значения свойств (setter injection) |
| `autowireMode` | Режим автосвязывания |
| `lazyInit` | Создавать ли бин по требованию |
| `initMethodName` | Метод инициализации |
| `destroyMethodName` | Метод уничтожения |
| `dependsOn` | Явные зависимости (для @DependsOn) |

Конкретные реализации: `RootBeanDefinition`, `ChildBeanDefinition`, `GenericBeanDefinition`, `ScannedGenericBeanDefinition` и др. Все они хранятся в `DefaultListableBeanFactory` (реализует `BeanDefinitionRegistry`).

**Как ApplicationContext строит граф зависимостей**

Процесс состоит из двух этапов: **фаза регистрации** и **фаза создания**.

1. **Фаза регистрации (parsing)** — происходит при старте `ApplicationContext`:
   - Считывается конфигурация (XML / `@Configuration`-классы / `@ComponentScan`).
   - Для каждого обнаруженного бина создаётся `BeanDefinition` и регистрируется в `BeanDefinitionRegistry`.
   - На этом этапе контейнер проверяет ссылки: если `ref="nonExistentBean"`, ошибка обнаруживается сразу.

2. **Фаза создания (instantiation)** — для singleton-бинов происходит сразу после регистрации (eager pre-instantiation по умолчанию):
   - Контейнер обходит зарегистрированные `BeanDefinition` и для каждого разрешает зависимости.
   - Граф зависимостей строится рекурсивно: если бин A зависит от B, сначала полностью создаётся B (со всеми его зависимостями), затем B инжектируется в A.
   - Создание бина: конструктор → установка свойств → `@PostConstruct` / `InitializingBean.afterPropertiesSet()` → `init-method`.
   - Если обнаружена циклическая зависимость через конструкторы — выбрасывается `BeanCurrentlyInCreationException` на этапе создания.

Важный нюанс: конфигурационные ошибки (отсутствующие бины, неверные типы) Spring выявляет **при создании контекста** (для singleton), а не при первом обращении — это ключевое преимущество eager pre-instantiation.

**Как @DependsOn влияет на порядок инициализации**

`@DependsOn` используется, когда между бинами существует **неявная** зависимость, не выраженная через `@Autowired` / конструктор. Типичные случаи: статические инициализаторы, регистрация JDBC-драйвера, глобальный кеш, который должен быть инициализирован до других бинов.

```java
@Component
@DependsOn("databaseInitializer")
public class UserRepository { ... }

@Component("databaseInitializer")
public class DatabaseInitializer {
    @PostConstruct
    public void init() { /* создание схемы */ }
}
```

Что гарантирует `@DependsOn`:
- Бины, перечисленные в аннотации, будут **полностью созданы и инициализированы** до создания текущего бина.
- При уничтожении контекста порядок **обратный**: зависимый бин (`UserRepository`) уничтожается **первым**, а бин-зависимость (`databaseInitializer`) — последним. Это позволяет использовать `@DependsOn` для управления порядком shutdown.

Отличие от `@Autowired`: `@DependsOn` не инжектирует зависимость как свойство — он только управляет порядком инициализации. Бин-зависимость остаётся недоступной через поле.

**Отличие @DependsOn от прямых зависимостей**

| Механизм | Когда используется |
|---|---|
| `@Autowired` / конструктор | Прямая структурная зависимость (бин нужен для работы) |
| `@DependsOn` | Косвенная зависимость (побочный эффект инициализации) |

`@DependsOn` применяется редко и является «запахом» — если зависимость структурная, лучше выразить её явно через инжекцию. Тем не менее в интеграционных сценариях (инициализация инфраструктуры) он незаменим.

---
### Вопрос 37. Что такое «lite mode» у @Configuration (proxyBeanMethods = false)? Как Spring использует CGLIB для перехвата @Bean-методов в полном режиме, и почему вызов одного @Bean-метода из другого без прокси создаёт новый экземпляр вместо синглтона?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Configuration (Spring Framework 7.0.7 API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Configuration.html)

Атрибут `proxyBeanMethods` задаёт, должны ли `@Bean`-методы проксироваться для обеспечения жизненного цикла бинов — например, чтобы возвращать общий экземпляр синглтона даже при прямом вызове `@Bean`-метода из кода.

**Полный режим (proxyBeanMethods = true, по умолчанию):**
Функциональность требует перехвата методов, реализованного через сгенерированный в рантайме CGLIB-подкласс. Это накладывает ограничения: класс конфигурации и его методы не могут быть объявлены `final`. В полном режиме поддерживаются «inter-bean references» — прямые вызовы `@Bean`-методов внутри класса конфигурации, а также внешние вызовы из другого класса конфигурации. Такие вызовы перехватываются CGLIB-прокси, которая делегирует получение экземпляра через `getBean()` контейнера, гарантируя соблюдение scope-семантики.

**Lite mode (proxyBeanMethods = false):**
Если каждый `@Bean`-метод самодостаточен и предназначен только как фабричный метод для контейнера, следует установить `false`, чтобы избежать CGLIB-обработки. Отключение перехвата методов фактически приравнивает поведение к классам, аннотированным не `@Configuration`, а, например, `@Component`. В lite mode вызов одного `@Bean`-метода из другого — это обычный Java-вызов без перехвата: каждый раз создаётся новый экземпляр объекта, а не возвращается синглтон из контейнера.

#### Ответ от Claude

**Полный режим (`proxyBeanMethods = true`)**

При загрузке контекста Spring обнаруживает классы, аннотированные `@Configuration`, и с помощью CGLIB генерирует подкласс (прокси) поверх оригинального класса конфигурации. В этот подкласс внедряется перехватчик `BeanMethodInterceptor`. Когда один `@Bean`-метод вызывает другой `@Bean`-метод напрямую (например, `return new ServiceA(repositoryA())`), CGLIB перехватывает этот вызов и вместо выполнения тела метода делает вызов `applicationContext.getBean("repositoryA")`. Это гарантирует возврат уже зарегистрированного экземпляра нужного scope — синглтона, прототипа и т.д.

Ограничения полного режима:
- Класс конфигурации не может быть `final` (CGLIB не может создать подкласс финального класса).
- `@Bean`-методы не могут быть `final` (CGLIB не может переопределить финальный метод).
- Небольшой overhead при старте контейнера из-за генерации подкласса.

**Lite mode (`proxyBeanMethods = false`)**

В lite mode CGLIB-подкласс не создаётся. Класс конфигурации регистрируется как обычный бин без прокси. Когда один `@Bean`-метод вызывает другой, происходит обычный Java-вызов: тело вызываемого метода выполняется полностью, создаётся новый объект с `new`. Spring не перехватывает этот вызов и не смотрит в контейнер. Следовательно, каждый такой вызов возвращает новый экземпляр, даже если бин зарегистрирован как синглтон.

Пример:

```java
// Полный режим (proxyBeanMethods = true — по умолчанию)
@Configuration
public class FullConfig {
    @Bean
    public RepositoryA repositoryA() { return new RepositoryA(); }

    @Bean
    public ServiceA serviceA() {
        return new ServiceA(repositoryA()); // CGLIB перехватит вызов -> вернёт синглтон
    }
}

// Lite mode (proxyBeanMethods = false)
@Configuration(proxyBeanMethods = false)
public class LiteConfig {
    @Bean
    public RepositoryA repositoryA() { return new RepositoryA(); }

    @Bean
    public ServiceA serviceA() {
        return new ServiceA(repositoryA()); // обычный Java-вызов -> новый RepositoryA()!
    }
}
```

**Когда использовать lite mode:**
- Конфигурационные классы, где `@Bean`-методы не вызывают друг друга (каждый метод самодостаточен).
- Для ускорения старта приложения и снижения overhead — CGLIB-проксирование не выполняется.
- В большинстве `@Configuration`-классов Spring Boot Autoconfigure (они используют `proxyBeanMethods = false` именно по этой причине).

**Важно:** Если в lite mode нужна зависимость одного бина от другого, следует инжектировать зависимость через параметр метода, а не через прямой вызов другого `@Bean`-метода:

```java
@Configuration(proxyBeanMethods = false)
public class LiteConfig {
    @Bean
    public RepositoryA repositoryA() { return new RepositoryA(); }

    @Bean
    public ServiceA serviceA(RepositoryA repositoryA) { // правильно: Spring inject
        return new ServiceA(repositoryA);
    }
}
```

---

### Вопрос 38. Почему при использовании PROPAGATION_REQUIRED внутренний транзакционный метод, поймавший и «проглотивший» исключение, может всё равно привести к UnexpectedRollbackException во внешнем методе? Как Spring помечает транзакцию как rollback-only и что происходит при попытке коммита?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Transaction Propagation :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

При `PROPAGATION_REQUIRED` все области транзакции (transaction scopes) отображаются на одну физическую транзакцию. Если внутренняя область устанавливает маркер rollback-only, внешняя транзакция ещё не приняла решение об откате — поэтому откат, инициированный внутренней областью, является «неожиданным». В этом случае выбрасывается `UnexpectedRollbackException`.

Это ожидаемое поведение: вызывающая сторона транзакции никогда не должна быть введена в заблуждение предположением о том, что коммит был выполнен, когда на самом деле это не так. Если внутренняя транзакция молча помечает транзакцию как rollback-only, а внешний вызывающий всё равно вызывает `commit`, внешний вызывающий должен получить `UnexpectedRollbackException` — явное указание на то, что вместо коммита был выполнен откат.

#### Ответ от Claude

**Механизм работы PROPAGATION_REQUIRED**

`PROPAGATION_REQUIRED` — пропагация по умолчанию в Spring. При её использовании:
- Если активная транзакция уже есть — метод присоединяется к ней (участвует в той же физической транзакции).
- Если активной транзакции нет — создаётся новая.

С точки зрения физических транзакций: одна физическая транзакция, несколько логических (transaction scopes). Spring управляет ими через `TransactionSynchronizationManager` — в `ThreadLocal` хранится состояние текущей транзакции, включая флаг `rollbackOnly`.

**Сценарий: внутренний метод «проглотил» исключение**

```java
@Service
public class OuterService {
    @Autowired InnerService inner;

    @Transactional  // PROPAGATION_REQUIRED
    public void outerMethod() {
        // ... логика ...
        try {
            inner.innerMethod(); // присоединяется к той же физической транзакции
        } catch (RuntimeException e) {
            // исключение поймано и "проглочено" — внешний метод продолжает работу
            log.warn("Inner failed, continuing...");
        }
        // outerMethod завершается нормально — вызывается commit
    }
}

@Service
public class InnerService {
    @Transactional  // PROPAGATION_REQUIRED — участвует в той же транзакции
    public void innerMethod() {
        // ... что-то упало ...
        throw new RuntimeException("Something went wrong");
        // Spring перехватывает исключение -> помечает транзакцию как rollback-only
    }
}
```

**Что происходит шаг за шагом:**

1. `outerMethod` стартует транзакцию (физическую). `TransactionSynchronizationManager` фиксирует её в `ThreadLocal`.
2. `innerMethod` присоединяется к той же физической транзакции (новый logical scope, но не новая physical).
3. Внутри `innerMethod` выбрасывается `RuntimeException`.
4. Spring AOP-прокси `innerMethod` перехватывает исключение на выходе из метода (в `AbstractPlatformTransactionManager`). Поскольку тип исключения подпадает под правила отката (по умолчанию — любой `RuntimeException` и `Error`), вызывается `doSetRollbackOnly()`: на физической транзакции устанавливается флаг `rollbackOnly = true`.
5. Исключение проброшено дальше и поймано в `outerMethod` блоком `try-catch`. Внешний код считает, что всё в порядке.
6. `outerMethod` завершается нормально. Spring AOP-прокси внешнего метода пытается выполнить `commit`.
7. `AbstractPlatformTransactionManager.commit()` проверяет флаг `rollbackOnly`. Обнаружив его, выполняет `rollback` и выбрасывает `UnexpectedRollbackException`.

**Почему это именно UnexpectedRollbackException, а не тихий откат?**

Это намеренное проектное решение Spring. Если бы откат происходил молча, внешний вызывающий (или ещё выше по стеку) мог бы посчитать, что данные сохранены, хотя на самом деле нет. `UnexpectedRollbackException` явно сигнализирует: «ты пытался совершить коммит, но физическая транзакция была помечена как rollback-only».

**Решения:**

1. **PROPAGATION_REQUIRES_NEW** — внутренний метод создаёт независимую физическую транзакцию. Её откат не затрагивает внешнюю.

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void innerMethod() { ... }
```

2. **PROPAGATION_NESTED** — использует savepoint внутри одной физической транзакции. Откат внутренней части откатывает только до savepoint, внешняя транзакция может продолжиться. Поддерживается не всеми JDBC-драйверами.

3. **Не глотать исключение** — если поймал, перебрось, чтобы Spring мог корректно обработать ситуацию.

**Ключевой вывод:** при `PROPAGATION_REQUIRED` все участники разделяют одну физическую транзакцию и один флаг `rollbackOnly`. Как только любой участник устанавливает этот флаг (даже если исключение поймано «снаружи»), коммит становится невозможен.

---

### Вопрос 39. Что такое @TransactionalEventListener? Чем он отличается от обычного @EventListener с точки зрения фазы выполнения (AFTER_COMMIT, AFTER_ROLLBACK, BEFORE_COMMIT)? Что произойдёт, если обработчик попытается сохранить данные в БД внутри фазы AFTER_COMMIT?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Transaction-bound Events :: Spring Framework](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)

Начиная со Spring 4.2, слушатель событий может быть привязан к определённой фазе транзакции. Типичный пример — обработка события после успешного завершения транзакции. Это позволяет использовать события более гибко, когда результат текущей транзакции действительно важен для слушателя.

Аннотация `@TransactionalEventListener` открывает атрибут `phase`, позволяющий настроить фазу транзакции, к которой привязан слушатель. Допустимые фазы: `BEFORE_COMMIT`, `AFTER_COMMIT` (по умолчанию), `AFTER_ROLLBACK`, а также `AFTER_COMPLETION`, которая агрегирует завершение транзакции (как при коммите, так и при откате).

Если транзакция не выполняется, слушатель не вызывается вообще, поскольку соблюдение требуемой семантики невозможно. Однако это поведение можно переопределить, установив атрибут `fallbackExecution` в `true`.

**Предупреждение (из Javadoc `@TransactionalEventListener`):** если `TransactionPhase` установлен в `AFTER_COMMIT` (по умолчанию), `AFTER_ROLLBACK` или `AFTER_COMPLETION`, транзакция уже будет зафиксирована или откачена, но транзакционные ресурсы могут всё ещё быть активны и доступны. Как следствие, любой код доступа к данным, инициированный в этот момент, всё ещё «участвует» в исходной транзакции, но изменения не будут зафиксированы в транзакционном ресурсе.

#### Ответ от Claude

**Что такое @TransactionalEventListener**

`@TransactionalEventListener` — это специализированный вариант `@EventListener`, привязывающий вызов обработчика к конкретной фазе транзакции, в рамках которой было опубликовано событие. Появился в Spring 4.2.

Обычный `@EventListener` вызывается синхронно в момент публикации события (`ApplicationEventPublisher.publishEvent()`), независимо от состояния транзакции — до, во время или после неё.

`@TransactionalEventListener` регистрирует обработчик как `TransactionSynchronization` и вызывает его только в указанную фазу текущей транзакции.

**Фазы выполнения**

| Фаза | Момент вызова |
|---|---|
| `BEFORE_COMMIT` | До выполнения коммита; транзакция ещё активна |
| `AFTER_COMMIT` (по умолчанию) | После успешного коммита |
| `AFTER_ROLLBACK` | После отката транзакции |
| `AFTER_COMPLETION` | После любого завершения (коммит или откат) |

Если в момент публикации события нет активной транзакции — обработчик не вызывается (если не установлен `fallbackExecution = true`).

**Что происходит при попытке сохранить данные в БД в фазе AFTER_COMMIT**

Это ключевая ловушка. Официальная документация (`TransactionalEventListener` Javadoc) прямо предупреждает:

> «если фаза установлена в `AFTER_COMMIT`, `AFTER_ROLLBACK` или `AFTER_COMPLETION`, транзакция уже будет зафиксирована или откачена, но транзакционные ресурсы могут всё ещё быть активны и доступны. Как следствие, любой код доступа к данным, инициированный в этот момент, всё ещё "участвует" в исходной транзакции, но изменения не будут зафиксированы в транзакционном ресурсе.»

Иными словами:
- Соединение с БД и `EntityManager` могут быть ещё живы.
- Вызов `repository.save(entity)` технически выполнится без исключения...
- ...но `INSERT`/`UPDATE` не будет зафиксирован в БД, потому что физическая транзакция уже завершена.
- Данные будут потеряны.

**Правильный подход: REQUIRES_NEW**

Чтобы обработчик в `AFTER_COMMIT` мог сохранять данные, нужно явно открыть новую транзакцию с помощью `Propagation.REQUIRES_NEW`:

```java
@Component
public class OrderEventListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void handleOrderCreated(OrderCreatedEvent event) {
        // Выполняется в новой, независимой транзакции
        auditRepository.save(new AuditEntry(event.getOrderId()));
    }
}
```

При этом:
- `@TransactionalEventListener` гарантирует вызов только после коммита исходной транзакции.
- `@Transactional(propagation = REQUIRES_NEW)` открывает новую физическую транзакцию специально для обработчика.
- Изменения в обработчике будут зафиксированы независимо.

**Поведение в BEFORE_COMMIT**

В фазе `BEFORE_COMMIT` исходная транзакция ещё активна. Запись в БД в этой фазе будет зафиксирована вместе с основной транзакцией. Однако если обработчик бросит исключение — основная транзакция тоже откатится.

**Практические рекомендации:**

- `BEFORE_COMMIT` — для валидации или дополнительных записей, которые должны быть атомарны с основной транзакцией.
- `AFTER_COMMIT` + `REQUIRES_NEW` — для side effects (отправка email, запись в аудит-лог, публикация в очередь сообщений), которые должны произойти только при успешном коммите основной транзакции.
- `AFTER_ROLLBACK` — для компенсирующих действий (например, освобождение зарезервированных ресурсов).
- Никогда не полагаться на то, что запись в БД в `AFTER_COMMIT` без `REQUIRES_NEW` сохранится.

---
### Вопрос 40. Как работает механизм ApplicationEvent / ApplicationEventPublisher в Spring? Опишите жизненный цикл события: кто публикует, как доставляется слушателям, синхронно или асинхронно по умолчанию, и как сделать доставку асинхронной?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Additional Capabilities of the ApplicationContext — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/context-introduction.html#context-functionality-events)

Обработка событий в `ApplicationContext` построена на классе `ApplicationEvent` и интерфейсе `ApplicationListener`. Когда бин, реализующий `ApplicationListener`, регистрируется в контексте, он получает уведомление каждый раз, когда публикуется `ApplicationEvent` соответствующего типа — классический паттерн Observer.

Начиная со Spring 4.2 поддерживается аннотационная модель через `@EventListener`, а публиковать можно произвольные объекты (Spring сам обернёт их в событие).

**Жизненный цикл события:**

1. **Публикация.** Компонент, желающий опубликовать событие, реализует `ApplicationEventPublisherAware` (или вставляет `ApplicationEventPublisher` через `@Autowired`) и вызывает `publisher.publishEvent(event)`. По умолчанию роль `ApplicationEventPublisher` выполняет сам `ApplicationContext`.

2. **Маршрутизация.** `ApplicationContext` делегирует рассылку внутреннему `ApplicationEventMulticaster` (реализация по умолчанию — `SimpleApplicationEventMulticaster`). Мультикастер перебирает всех зарегистрированных слушателей и вызывает их.

3. **Доставка слушателям.** Слушатель либо реализует `ApplicationListener<E>`, либо помечает метод аннотацией `@EventListener`. Тип события определяется из обобщённого параметра или из параметра метода.

**По умолчанию доставка синхронная:** метод `publishEvent()` блокирует вызывающий поток до тех пор, пока все слушатели не завершат обработку. Это позволяет слушателям участвовать в транзакции издателя.

**Как сделать доставку асинхронной — два способа:**

Способ 1 — `@Async` на методе слушателя (точечная асинхронность; требует `@EnableAsync` на конфигурации):
```java
@EventListener
@Async
public void handle(MyEvent event) {
    // выполняется в отдельном потоке
}
```
Ограничения: исключения не пробрасываются вызывающему; нельзя публиковать следующие события через возвращаемое значение.

Способ 2 — настройка `ApplicationEventMulticaster` с исполнителем (глобальная асинхронность для всех событий):
```java
@Bean
ApplicationEventMulticaster applicationEventMulticaster() {
    SimpleApplicationEventMulticaster multicaster = new SimpleApplicationEventMulticaster();
    multicaster.setTaskExecutor(new SimpleAsyncTaskExecutor());
    multicaster.setErrorHandler(TaskUtils.LOG_AND_SUPPRESS_ERROR_HANDLER);
    return multicaster;
}
```

#### Ответ от Claude

**Ключевые участники механизма:**

| Компонент | Роль |
|---|---|
| `ApplicationEvent` | Базовый класс для пользовательских событий |
| `ApplicationEventPublisher` | Интерфейс публикации; реализован самим `ApplicationContext` |
| `ApplicationEventPublisherAware` | Callback для инъекции издателя в бин |
| `ApplicationListener<E>` | Интерфейс-слушатель |
| `@EventListener` | Аннотация для метода-слушателя (с Spring 4.2) |
| `ApplicationEventMulticaster` | Внутренний компонент рассылки событий |
| `SimpleApplicationEventMulticaster` | Реализация по умолчанию |

**Жизненный цикл события:**

1. Бин-издатель вызывает `applicationEventPublisher.publishEvent(event)`.
2. `ApplicationContext` (он сам реализует `ApplicationEventPublisher`) передаёт событие в `ApplicationEventMulticaster`.
3. `SimpleApplicationEventMulticaster` находит все слушатели, чей тип совпадает с типом события (через generics), и вызывает их один за другим.
4. **По умолчанию всё происходит синхронно в том же потоке**, что и вызов `publishEvent()`. Вызов возвращается только после того, как все слушатели завершили работу.

**Преимущество синхронности:** слушатель работает внутри транзакционного контекста издателя — это важно при использовании `@TransactionalEventListener` (слушатель может быть привязан к фазе `AFTER_COMMIT` и т.д.). Следует отметить, что `@TransactionalEventListener` не проходит через `ApplicationEventMulticaster` — он регистрирует callback синхронизации транзакции.

**Два способа сделать доставку асинхронной:**

Способ 1 — аннотация `@Async` на конкретном методе-слушателе. Требует `@EnableAsync` в конфигурации и наличия `TaskExecutor`-а. Подходит для точечной асинхронности. Ограничение: исключения не пробрасываются обратно издателю (нужен `AsyncUncaughtExceptionHandler`); чтобы опубликовать следующее событие из такого слушателя, нужно вручную вызвать `publisher.publishEvent()`.

Способ 2 — переопределить бин `applicationEventMulticaster` и установить `TaskExecutor`. Это делает **все** события в контексте асинхронными. Рекомендуется также явно задать `ErrorHandler`, иначе исключения в слушателях будут молча проглочены.

**Стандартные события Spring** (публикуются контейнером автоматически):
- `ContextRefreshedEvent` — контекст инициализирован или обновлён
- `ContextStartedEvent` / `ContextStoppedEvent` — вызов `start()` / `stop()`
- `ContextClosedEvent` — контекст закрыт, синглтоны уничтожены
- `RequestHandledEvent` — HTTP-запрос обработан (только в веб-контексте)

**Расхождений между источниками не выявлено.** Официальная документация Spring и описание Javadoc согласуются во всех ключевых аспектах.

---

