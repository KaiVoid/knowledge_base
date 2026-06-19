# Spring Framework (Core, IoC, AOP) — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../theory/01-knowledge-areas/03-backend-ecosystem/13-spring-core.md](../theory/01-knowledge-areas/03-backend-ecosystem/13-spring-core.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](spring-01.md) · [ч.2](spring-02.md) · **ч.3**

---
### Вопрос 41. Что такое Spring Profiles (@Profile)? Как активировать профиль (аннотация, переменная окружения, свойство spring.profiles.active) и как они соотносятся с абстракцией Environment? Можно ли задать профиль по умолчанию?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Bean Definition Profiles — Spring Framework Reference (Environment Abstraction)](https://docs.spring.io/spring-framework/reference/core/beans/environment.html)

Профили — это именованные логические группы определений бинов, которые регистрируются в контейнере только при активации соответствующего профиля. Они позволяют определять разные конфигурации для разных окружений (dev, qa, prod) в одном приложении.

**Аннотация `@Profile`** применяется к классам с `@Component` / `@Configuration` или к отдельным `@Bean`-методам:

```java
@Configuration
@Profile("development")
public class StandaloneDataConfig {
    @Bean
    public DataSource dataSource() { ... }
}

@Configuration
@Profile("production")
public class JndiDataConfig {
    @Bean
    public DataSource dataSource() throws Exception { ... }
}
```

**Профильные выражения** поддерживают логические операторы: `!` (NOT), `&` (AND), `|` (OR). Пример: `@Profile("production & (us-east | eu-central)")`.

**Активация профилей — способы:**

1. Программно через `Environment`:
```java
AnnotationConfigApplicationContext ctx = new AnnotationConfigApplicationContext();
ctx.getEnvironment().setActiveProfiles("development");
ctx.register(AppConfig.class, StandaloneDataConfig.class, JndiDataConfig.class);
ctx.refresh();
```

2. Через JVM-свойство: `-Dspring.profiles.active="profile1,profile2"`

3. Через переменную окружения ОС (в Spring Boot): `SPRING_PROFILES_ACTIVE=dev,hsqldb`

4. Через системное свойство в `web.xml`, JNDI-запись, параметр Servlet-контекста.

5. В тестах: аннотация `@ActiveProfiles`.

**Профиль по умолчанию:** если ни один профиль не активирован, включается профиль с именем `default`. Имя дефолтного профиля можно изменить через `environment.setDefaultProfiles("myDefault")` или свойство `-Dspring.profiles.default=myDefault`.

**Связь с `Environment`:** активные профили управляют поведением аннотации `@Profile` — контейнер спрашивает у `Environment`, активен ли нужный профиль, прежде чем регистрировать определение бина.

#### Ответ от Claude

**Spring Profiles** — механизм условной регистрации бинов, позволяющий держать несколько вариантов конфигурации в одном приложении и активировать нужный в зависимости от окружения (dev / test / staging / prod).

**Аннотация `@Profile`** может быть применена к:
- классу `@Configuration` — тогда весь класс со всеми его `@Bean`-методами регистрируется только при активном профиле;
- отдельному `@Bean`-методу — для альтернативных вариантов одного и того же бина;
- любому `@Component`-классу (включая `@Service`, `@Repository` и т.д.);
- классу `@ConfigurationProperties`, если он сканируется компонент-сканом (при регистрации через `@EnableConfigurationProperties` профиль ставится на `@Configuration`, а не на сам класс свойств).

**Способы активации профилей:**

| Способ | Пример |
|---|---|
| JVM system property | `-Dspring.profiles.active=dev` |
| Переменная окружения ОС (Spring Boot) | `SPRING_PROFILES_ACTIVE=dev,hsqldb` |
| `application.properties` / `application.yaml` | `spring.profiles.active=dev` |
| Аргумент командной строки Spring Boot | `--spring.profiles.active=dev` |
| Программно через `ConfigurableEnvironment` | `ctx.getEnvironment().setActiveProfiles("dev")` |
| `SpringApplication.setAdditionalProfiles(...)` | добавляет профили поверх уже активных |
| `@ActiveProfiles` в тестах | `@ActiveProfiles("test")` |

**Связь с абстракцией `Environment`:**

`Environment` — центральный интерфейс, который моделирует два аспекта среды выполнения: **профили** и **свойства** (property sources). Именно `Environment` хранит список активных и дефолтных профилей. При инициализации контейнера каждое определение бина проверяется через `Environment.acceptsProfiles(...)`: если условие профиля не выполнено — бин не регистрируется. Программный доступ: `environment.getActiveProfiles()`, `environment.getDefaultProfiles()`, `environment.acceptsProfiles(Profiles.of("dev", "!prod"))`.

**Профиль по умолчанию:**

Имя `default` — зарезервированное имя дефолтного профиля. Если ни один профиль явно не активирован, Spring считает активным профиль `default`. Бины, помеченные `@Profile("default")`, регистрируются только тогда, когда нет ни одного другого активного профиля. Переименовать дефолтный профиль можно через свойство `spring.profiles.default` (например, `spring.profiles.default=none`) или программно через `environment.setDefaultProfiles(...)`.

**Дополнительные возможности Spring Boot:**
- `spring.profiles.include` — добавляет профили поверх активных (не заменяет).
- `spring.profiles.group.<name>` — группировка: активация одного логического имени активирует несколько реальных профилей.

**Расхождений между источниками не выявлено.** Документация Spring Framework и Spring Boot согласуются, расширяя друг друга.

---

### Вопрос 42. Что такое @Conditional и интерфейс Condition в Spring? Чем @ConditionalOnMissingBean, @ConditionalOnProperty и @ConditionalOnClass отличаются от базового @Conditional, и как они используются в механизме Spring Boot Auto-Configuration?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration — Spring Boot Reference (v2.0.6)](https://docs.spring.io/spring-boot/docs/2.0.6.RELEASE/reference/html/boot-features-developing-auto-configuration.html)

Авто-конфигурация реализуется с помощью стандартных `@Configuration`-классов и дополнительных аннотаций `@Conditional`, которые ограничивают, когда данная авто-конфигурация должна применяться.

**`@ConditionalOnClass` / `@ConditionalOnMissingClass`** — конфигурация включается или исключается в зависимости от наличия или отсутствия определённых классов в classpath. Метаданные аннотаций разбираются через ASM, что позволяет ссылаться на реальный класс через атрибут `value`, даже если он отсутствует в classpath во время выполнения; альтернативно используется атрибут `name` с именем класса в виде строки.

**`@ConditionalOnMissingBean`** — совпадает только тогда, когда в `BeanFactory` ещё нет бинов, удовлетворяющих заданным требованиям. Чаще всего используется, чтобы разработчик мог переопределить авто-конфигурацию по умолчанию.

**`@ConditionalOnProperty`** — включает конфигурацию на основе свойства Spring `Environment`. Атрибуты `prefix` и `name` задают проверяемое свойство; `havingValue` задаёт конкретное ожидаемое значение; `matchIfMissing` определяет поведение при отсутствии свойства.

**Типичный паттерн авто-конфигурации:**
```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
public class DataSourceAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource() { ... }
}
```

Авто-конфигурации регистрируются в `META-INF/spring.factories` (Spring Boot 2.x) или `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Spring Boot 3.x).

#### Ответ от Claude

**Базовый `@Conditional` и интерфейс `Condition`:**

`@Conditional` — аннотация Spring Framework (пакет `org.springframework.context.annotation`), которая делает регистрацию бина или `@Configuration`-класса условной. Принимает один параметр — массив классов, реализующих интерфейс `Condition`:

```java
@Conditional(MyCondition.class)
@Bean
public MyService myService() { ... }
```

Интерфейс `Condition` — функциональный, содержит единственный метод:
```java
boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata);
```

- `ConditionContext` предоставляет доступ к `BeanDefinitionRegistry`, `ConfigurableListableBeanFactory`, `Environment`, `ResourceLoader` и `ClassLoader` — то есть всему необходимому для принятия решения.
- `AnnotatedTypeMetadata` предоставляет метаданные аннотаций проверяемого класса или метода.
- Условие вычисляется непосредственно перед регистрацией определения бина.
- `@Conditional` не поддерживает наследование: условия суперкласса или переопределённых методов не учитываются.

**Специализированные аннотации Spring Boot** (`org.springframework.boot.autoconfigure.condition`) являются мета-аннотациями, построенными поверх `@Conditional` с готовой реализацией `Condition` внутри:

| Аннотация | Условие срабатывания | Ключевые атрибуты |
|---|---|---|
| `@ConditionalOnClass` | Класс присутствует в classpath | `value` (Class), `name` (String) |
| `@ConditionalOnMissingClass` | Класс отсутствует в classpath | `value` (String имя класса) |
| `@ConditionalOnBean` | Бин заданного типа/имени уже зарегистрирован | `value`, `type`, `name`, `annotation`, `search` |
| `@ConditionalOnMissingBean` | Бин заданного типа/имени ещё не зарегистрирован | `value`, `type`, `name`, `annotation`, `ignored`, `search` |
| `@ConditionalOnProperty` | Свойство в `Environment` соответствует условию | `prefix`, `name`, `havingValue`, `matchIfMissing` |
| `@ConditionalOnExpression` | SpEL-выражение вернуло `true` | `value` |
| `@ConditionalOnWebApplication` | Приложение является веб-приложением | `type` (SERVLET / REACTIVE / ANY) |
| `@ConditionalOnResource` | Ресурс существует по заданному пути | `resources` |

**Ключевые отличия от базового `@Conditional`:**

1. Не нужно писать собственный класс `Condition` — логика уже реализована внутри Spring Boot.
2. `@ConditionalOnClass` использует разбор через ASM (а не через classloader), поэтому можно безопасно ссылаться на класс, который может отсутствовать в classpath — именно это позволяет авто-конфигурациям не ломаться при отсутствии опциональных зависимостей.
3. `@ConditionalOnMissingBean` проверяет уже зарегистрированные определения бинов на момент вычисления условия, поэтому порядок загрузки важен: аннотацию нужно использовать только в авто-конфигурационных классах (которые загружаются после пользовательских `@Configuration`-классов), иначе поведение непредсказуемо.

**Роль в механизме Spring Boot Auto-Configuration:**

При старте Spring Boot собирает список классов авто-конфигурации из `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot 3.x) или `META-INF/spring.factories` (Boot 2.x). Каждый такой класс — это `@Configuration` с набором `@ConditionalOn*`-аннотаций. Типичный паттерн:

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)        // только если JDBC-драйвер есть в classpath
@ConditionalOnMissingBean(DataSource.class)  // только если пользователь не определил свой DataSource
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {
    // ...
}
```

Это обеспечивает принцип «convention over configuration»: Spring Boot предоставляет разумные умолчания, но пользователь всегда может переопределить поведение, объявив собственный бин — и тогда `@ConditionalOnMissingBean` предотвратит регистрацию дефолтного.

Порядок выполнения авто-конфигураций регулируется аннотациями `@AutoConfigureAfter`, `@AutoConfigureBefore` и `@AutoConfigureOrder`.

**Расхождений между источниками не выявлено.** Javadoc Spring Boot и официальная документация Spring Boot Reference согласуются в описании всех перечисленных аннотаций.
### Вопрос 43. Как @ConditionalOnMissingBean работает при наличии нескольких ApplicationContext или при использовании @Import? Почему порядок регистрации BeanDefinition важен для корректной работы этой аннотации, и какие подводные камни связаны с её использованием вне Spring Boot Auto-Configuration?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [ConditionalOnMissingBean (Spring Boot API)](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/autoconfigure/condition/ConditionalOnMissingBean.html)

`@ConditionalOnMissingBean` — условная аннотация Spring Boot, которая разрешает регистрацию бина только в том случае, если в `BeanFactory` ещё нет бина, удовлетворяющего заданным требованиям. Ни одно из требований не должно быть выполнено, чтобы условие считалось истинным; при этом требования не обязаны удовлетворяться одним и тем же бином.

Ключевое предупреждение из официальной документации:

> «Условие может соответствовать только тем определениям бинов, которые уже были обработаны контекстом приложения на данный момент. По этой причине настоятельно рекомендуется использовать данное условие только на классах авто-конфигурации.»

Атрибут `search` управляет тем, в какой части иерархии контекстов ищется бин:
- `SearchStrategy.ALL` (по умолчанию) — поиск по всей иерархии контекстов (текущий контекст + все предки);
- `SearchStrategy.ANCESTORS` — только в родительских контекстах, без текущего;
- `SearchStrategy.CURRENT` — только в текущем контексте.

Бины, у которых `Bean.autowireCandidate() = false` или `AbstractBeanDefinition.isDefaultCandidate() = false`, автоматически игнорируются при поиске.

При использовании в качестве мета-аннотации следует применять только атрибут `type` (строковое имя класса), а не `value` (Class-объект), чтобы избежать проблем с загрузкой байт-кода.

#### Ответ от Claude

**Как работает оценка условия**

`@ConditionalOnMissingBean` проверяет наличие бина в `BeanFactory` в момент обработки `BeanDefinition` конфигурационного класса, где она используется. Проверяется только то, что уже зарегистрировано на этот момент. Если бин пользователя будет зарегистрирован позже — аннотация его «не увидит» и создаст дефолтный бин, после чего в контексте окажется два бина вместо одного.

**Почему порядок BeanDefinition принципиален**

Spring Boot обрабатывает конфигурации в строго определённом порядке:
1. Сначала — пользовательские классы `@Configuration` и `@Component`, найденные при сканировании пакетов.
2. Затем — авто-конфигурации из `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Spring Boot 2.7+) или `spring.factories` (старые версии).

Именно поэтому авто-конфигурация надёжно «видит» пользовательские бины: к моменту её обработки они уже зарегистрированы. При использовании `@ConditionalOnMissingBean` в обычных `@Configuration`-классах (не авто-конфигурациях) такой гарантии нет, и порядок обработки зависит от порядка сканирования пакетов, что непредсказуемо.

**Проблемы при использовании @Import**

`@Import` подключает конфигурационный класс непосредственно в процессе парсинга текущего класса. Импортируемая конфигурация обрабатывается немедленно, до того как будут зарегистрированы другие бины. Это означает:
- Если `@Import` подключает класс с `@ConditionalOnMissingBean`, а бин пользователя зарегистрирован в другой конфигурации, которая обрабатывается позже, условие будет оценено некорректно.
- Порядок `@Import`-ов имеет значение: бины из первого `@Import` видны при оценке условия второго.

**Проблемы при нескольких ApplicationContext**

В иерархии контекстов (например, Spring MVC: корневой контекст + контекст диспетчера, или Spring Boot + контекст тестов) параметр `search` по умолчанию равен `SearchStrategy.ALL`, то есть поиск идёт по всей иерархии снизу вверх. Это может привести к тому, что бин, определённый в родительском контексте, «скроет» необходимость регистрации дефолтного бина в дочернем — даже если в дочернем контексте он нужен. И наоборот: при `SearchStrategy.CURRENT` бин из родителя не будет виден, и дефолтный бин зарегистрируется дважды.

**Подводные камни вне авто-конфигурации**

1. Использование `@ConditionalOnMissingBean` на `@Component`-классах, найденных через сканирование — ненадёжно; порядок сканирования не гарантирован.
2. Использование внутри обычных `@Configuration`-классов в одном модуле создаёт неочевидную зависимость от порядка инициализации.
3. При применении на уровне класса `@Configuration` весь класс не регистрируется как бин, если условие ложно; при применении на уровне метода `@Bean` — класс создаётся, но метод не вызывается. Это разное поведение.
4. Официальная документация прямо указывает: «настоятельно рекомендуется использовать только в авто-конфигурационных классах».

**Правильный паттерн использования**

```java
// В авто-конфигурации — безопасно:
@AutoConfiguration
public class MyServiceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean  // тип выводится из возвращаемого типа метода
    public MyService myService() {
        return new DefaultMyService();
    }
}
```

Для управления порядком авто-конфигураций используются `@AutoConfigureBefore` / `@AutoConfigureAfter`.

---

### Вопрос 44. Что делает @Lazy на уровне точки внедрения (поля или параметра конструктора), в отличие от @Lazy на определении бина? Как Spring генерирует прокси-заглушку при @Lazy-инжекции и когда реальный бин создаётся?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Lazy (Spring Framework API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Lazy.html)

`@Lazy` на точке внедрения, помеченной `@Autowired` или `@Inject`, имеет иную семантику по сравнению с `@Lazy` на определении бина:

> «Приводит к созданию прокси-объекта с ленивым разрешением зависимости для затронутой зависимости, кешируя её при первом обращении (для синглтона) или повторно разрешая при каждом обращении (для остальных областей видимости).»

Таким образом, при `@Lazy` на точке внедрения Spring инжектирует не реальный бин, а прокси-заглушку. Реальный бин создаётся только при первом вызове любого метода на прокси.

Важное предупреждение из официальной документации:

> «Такой прокси с ленивым разрешением всегда будет инжектирован; если целевая зависимость не существует, вы узнаете об этом только через исключение при вызове.»

Для более гибкой работы с необязательными зависимостями рекомендуется использовать `ObjectProvider<T>`.

#### Ответ от Claude

**@Lazy на определении бина**

Когда `@Lazy` указан на `@Bean`-методе или `@Component`-классе, Spring не создаёт этот бин при старте контейнера. Бин будет создан только тогда, когда на него впервые появится спрос: другой бин запросит его через зависимость, или код явно вызовет `BeanFactory.getBean(...)`. Это относится к самому объекту бина.

**@Lazy на точке внедрения**

Когда `@Lazy` размещён на поле или параметре конструктора (совместно с `@Autowired`), Spring не откладывает создание зависимого бина. Он немедленно создаёт прокси-заглушку и инжектирует именно её. Реальный бин создаётся при первом вызове метода на прокси.

Принципиальное отличие: класс, в который инжектируется зависимость, создаётся полностью и без задержки. Ленивость касается только зависимости.

**Механизм генерации прокси**

Spring использует класс `ContextAnnotationAutowireCandidateResolver`, который обнаруживает `@Lazy` на точке внедрения. Для генерации прокси применяется CGLIB-подклассирование целевого бина (создаётся подкласс на лету). Прокси-объект реализует тот же интерфейс или является подклассом того же типа, что и реальный бин.

Поведение прокси зависит от области видимости (scope) целевого бина:
- **Синглтон**: реальный бин создаётся ровно один раз при первом вызове метода и затем кешируется внутри прокси.
- **Прототип или другие не-синглтонные scopes**: реальный бин разрешается заново при каждом вызове метода через прокси.

**Пример сравнения**

```java
// @Lazy на определении: сам бин создаётся лениво
@Component
@Lazy
public class HeavyService { ... }

// @Lazy на точке внедрения: HeavyService создаётся лениво,
// но MyController создаётся немедленно с прокси-заглушкой
@Component
public class MyController {

    @Autowired
    @Lazy
    private HeavyService heavyService; // здесь лежит CGLIB-прокси

    public void handle() {
        heavyService.doWork(); // только здесь создаётся реальный HeavyService
    }
}
```

**Подводные камни**

1. Если целевой бин не существует в контексте, исключение `NoSuchBeanDefinitionException` возникнет только при первом вызове метода на прокси, а не при старте контейнера. Это затрудняет раннее обнаружение ошибок конфигурации.
2. `@Lazy` на точке внедрения имеет реальный эффект только для синглтон-зависимостей. Для прототипных бинов Spring и без того создаёт новый экземпляр при каждом запросе.
3. Для необязательных зависимостей предпочтительнее `ObjectProvider<T>`: он позволяет явно проверить наличие бина перед использованием через методы `getIfAvailable()` и `getIfUnique()`.
4. Прокси создаётся через CGLIB, поэтому класс не должен быть `final` и должен иметь доступный конструктор без аргументов (или конструктор, доступный для CGLIB).

---

### Вопрос 45. Что такое TransactionSynchronizationManager и как с его помощью выполнить код строго после успешного коммита транзакции? Почему нельзя просто вызвать код после метода с @Transactional и быть уверенным, что транзакция уже зафиксирована?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [TransactionSynchronization (Spring Framework API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/support/TransactionSynchronization.html)

`TransactionSynchronization` — интерфейс Spring для колбэков жизненного цикла транзакции, поддерживаемый `AbstractPlatformTransactionManager`. Метод `afterCommit()` вызывается после успешного коммита транзакции:

> «Вызывается после коммита транзакции. Может выполнять дальнейшие операции непосредственно после успешного завершения основной транзакции — например, отправку подтверждений или электронных писем.»

Важное замечание из документации:

> «Транзакция к этому моменту уже зафиксирована, однако транзакционные ресурсы могут всё ещё быть активны и доступны. Следовательно, любой код доступа к данным, вызванный в этой точке, всё ещё будет "участвовать" в исходной транзакции, если только явно не объявит, что требует выполнения в отдельной транзакции. Для этого следует использовать `PROPAGATION_REQUIRES_NEW`.»

Порядок вызовов колбэков жизненного цикла:
1. `beforeCommit(boolean readOnly)` — перед попыткой коммита;
2. `beforeCompletion()` — перед завершением (коммит или откат);
3. `afterCommit()` — только при успешном коммите;
4. `afterCompletion(int status)` — после любого завершения (коммит или откат).

#### Ответ от Claude

**Что такое TransactionSynchronizationManager**

`TransactionSynchronizationManager` — центральный вспомогательный класс Spring, который управляет ресурсами и синхронизациями транзакций в привязке к текущему потоку. Для хранения состояния он использует `ThreadLocal`-переменные:
- карта ресурсов (например, соединения JDBC, сессии Hibernate);
- список зарегистрированных `TransactionSynchronization`-объектов;
- метаданные транзакции (имя, флаг readOnly, уровень изоляции).

Жизненным циклом `TransactionSynchronizationManager` управляет `AbstractPlatformTransactionManager` автоматически: вызывает `initSynchronization()` при старте транзакции и `clearSynchronization()` при её завершении. Приложение не должно вызывать эти методы напрямую.

**Почему код после @Transactional-метода не гарантирует коммит**

`@Transactional` работает через AOP-прокси. Вызов `service.doSomething()` в действительности выполняется так:

```
Caller --> TransactionInterceptor.invoke()
               --> начало транзакции
               --> service.doSomething()  // реальный метод
               --> коммит / откат
               --> возврат результата
Caller <-- получает управление
```

Caller получает управление только после того, как `TransactionInterceptor` вернул результат. К этому моменту коммит уже произошёл. Однако есть ситуации, когда это не так:

1. **Вложенные транзакции и пропагация**: если `doSomething()` вызывается из другого `@Transactional`-метода, то внутренний метод участвует во внешней транзакции (при `REQUIRED`). Коммит произойдёт только при завершении внешнего метода, а не при возврате из внутреннего.
2. **Реактивные транзакции**: в реактивном стеке транзакция привязана к контексту Reactor, а не к потоку; сигналы завершения асинхронны.
3. **Двухфазный коммит (XA)**: при распределённых транзакциях коммит выполняется в несколько шагов и может завершиться неудачно после возврата метода.

Таким образом, для кода, вызванного непосредственно снаружи `@Transactional`-метода в случае простой одиночной транзакции, коммит действительно уже произошёл. Но при вложенных транзакциях это не так. `TransactionSynchronizationManager.registerSynchronization()` решает задачу правильно в любом сценарии.

**Как выполнить код строго после коммита**

```java
@Transactional
public void createOrder(Order order) {
    orderRepository.save(order);

    // Регистрируем колбэк; он выполнится только после коммита всей транзакции
    TransactionSynchronizationManager.registerSynchronization(
        new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                // Гарантировано: заказ уже в базе
                kafkaTemplate.send("orders", order.getId().toString());
            }
        }
    );
}
```

Перед регистрацией рекомендуется проверить, активна ли транзакция:

```java
if (TransactionSynchronizationManager.isSynchronizationActive()) {
    TransactionSynchronizationManager.registerSynchronization(...);
} else {
    // Транзакции нет — выполняем немедленно или обрабатываем иначе
    kafkaTemplate.send("orders", order.getId().toString());
}
```

**afterCommit() vs afterCompletion()**

| Аспект | `afterCommit()` | `afterCompletion(int status)` |
|---|---|---|
| Когда вызывается | Только при успешном коммите | После любого завершения (коммит или откат) |
| Параметр статуса | Нет | `STATUS_COMMITTED`, `STATUS_ROLLED_BACK`, `STATUS_UNKNOWN` |
| Исключения | Пробрасываются вызывающему | Логируются, не пробрасываются |
| Основное применение | Побочные эффекты (отправка событий, email) | Очистка ресурсов |

**Важные ограничения afterCommit()**

Транзакционные ресурсы (соединения, сессии) в момент вызова `afterCommit()` ещё могут быть активны, но коммит уже выполнен. Если в `afterCommit()` выполнить операцию с базой данных без явного указания `Propagation.REQUIRES_NEW`, она присоединится к уже зафиксированной транзакции и изменения не будут сохранены (или поведение будет неопределённым).

**Альтернатива: @TransactionalEventListener**

Spring 4.2+ предоставляет более декларативный способ:

```java
// В транзакционном методе публикуем событие
eventPublisher.publishEvent(new OrderCreatedEvent(order));

// Слушатель выполняется после коммита
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onOrderCreated(OrderCreatedEvent event) {
    kafkaTemplate.send("orders", event.getOrderId());
}
```

`@TransactionalEventListener` внутри использует тот же `TransactionSynchronizationManager.registerSynchronization()`, но предоставляет декларативный API без шаблонного кода.
### Вопрос 46. Что такое @Transactional(readOnly = true)? Какой эффект оказывает этот флаг на уровне JDBC (Connection.setReadOnly), на уровне Hibernate (FlushMode.MANUAL / Session.setDefaultReadOnly) и на уровне базы данных? Когда readOnly = true действительно даёт прирост производительности, а когда не даёт?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Spring read-only transaction Hibernate optimization — Vlad Mihalcea](https://vladmihalcea.com/spring-read-only-transaction-hibernate-optimization/)

Когда метод помечен `@Transactional(readOnly = true)`, Spring сигнализирует менеджеру транзакций о намерении только читать данные.

**До Spring 5.1** единственным эффектом на уровне Hibernate была установка режима сброса в `FlushType.MANUAL`. Это отключало автоматическую проверку изменений (dirty checking), но флаг `readOnly` не проникал глубже — в сам объект `Session` Hibernate.

**После Spring 5.1** (исправление SPR-16956) поведение было расширено: флаг `readOnly` теперь передаётся непосредственно в `Session` Hibernate через вызов `session.setDefaultReadOnly(true)`. Это приводит к тому, что при загрузке сущностей Hibernate немедленно отбрасывает «загруженное состояние» (loaded state) — снимок данных, который обычно хранится весь жизненный цикл `PersistenceContext` и используется для dirty checking. Экономия памяти при чтении большого числа сущностей может быть существенной.

**Механизм оптимизации:** при обычной транзакции чтения-записи Hibernate сохраняет снимок каждой загруженной сущности. При `readOnly = true` снимок формируется, но сразу же удаляется, поскольку изменения отслеживать не нужно.

---

#### Ответ от Claude

**Три уровня воздействия флага `readOnly = true`:**

**1. Уровень JDBC — `Connection.setReadOnly(true)`**

Spring передаёт флаг `readOnly` в JDBC-соединение через вызов `Connection.setReadOnly(true)`. Это подсказка драйверу и пулу соединений — семантика зависит от драйвера. По умолчанию `DataSourceTransactionManager` и `JpaTransactionManager` вызывают `Connection.setReadOnly(true)`, а при завершении транзакции сбрасывают его обратно.

Практически важный сценарий — **маршрутизация соединений**: при использовании `AbstractRoutingDataSource` или `LazyConnectionDataSourceProxy` метод `TransactionSynchronizationManager.isCurrentTransactionReadOnly()` позволяет перенаправить запрос на read-реплику вместо primary-узла. Это один из наиболее ощутимых эффектов флага в продакшен-системах.

**2. Уровень Hibernate**

- **До Spring 5.1:** устанавливается только `FlushMode.MANUAL`. Hibernate не выполняет автоматический flush перед запросами, что исключает лишние `UPDATE`/`INSERT` в БД. Сам `Session` при этом не переходит в read-only режим — снимки сущностей (loaded state) по-прежнему хранятся в `PersistenceContext`.
- **После Spring 5.1:** Spring вызывает `session.setDefaultReadOnly(true)`. Hibernate загружает сущности сразу в режиме `readOnly`: loaded state (снимок) отбрасывается немедленно после загрузки, а не хранится до конца транзакции. Это снижает потребление памяти и устраняет overhead dirty checking при флаше.

Таким образом, начиная с Spring 5.1 действуют одновременно оба механизма: `FlushMode.MANUAL` (нет flush) и `session.setDefaultReadOnly(true)` (нет снимков).

**3. Уровень базы данных**

Поведение зависит от СУБД:
- **MySQL (InnoDB):** при получении соединения с `readOnly = true` и при явном `SET TRANSACTION READ ONLY` ядро может пропускать формирование undo-записей для выборок, снижая нагрузку на undo-log. Попытка записи в таком режиме вызывает ошибку.
- **PostgreSQL:** принимает `SET TRANSACTION READ ONLY` и запрещает DML-операции, однако оптимизации на уровне WAL минимальны — PostgreSQL и так не пишет в WAL для чисто читающих транзакций.
- В целом: большинство СУБД не применяют значительных внутренних оптимизаций только по факту флага от JDBC-драйвера; основной эффект — логическая защита от случайных записей и возможность маршрутизации на реплику.

**Когда `readOnly = true` даёт реальный прирост производительности:**

1. **Маршрутизация на реплику** — самый ощутимый эффект: read-трафик снимается с primary.
2. **Загрузка большого числа сущностей через Hibernate** — экономия памяти за счёт отсутствия снимков (Spring 5.1+).
3. **Исключение автоматического flush** — устраняет лишние SQL-запросы, которые Hibernate мог бы выполнить перед JPQL-запросом.
4. **Упрощение пула соединений** — некоторые пулы (HikariCP) могут оптимизировать работу с read-only соединениями.

**Когда `readOnly = true` НЕ даёт значимого прироста:**

1. **Простой Spring JDBC без Hibernate** — нет dirty checking, нет снимков, флаг служит лишь подсказкой.
2. **Длинные транзакции с бизнес-логикой после запроса** — транзакция держит соединение открытым на всё время выполнения метода, что может вызвать нехватку соединений в пуле. Аннотацию лучше ставить на репозиторный, а не сервисный слой.
3. **Отсутствие read-реплик** — маршрутизация невозможна, и основной выигрыш теряется.
4. **Единичные запросы, возвращающие небольшое число сущностей** — экономия на снимках незначительна.

**Расхождения между источниками:** Baeldung и Vlad Mihalcea согласуются в описании поведения начиная с Spring 5.1. Ряд статей на Medium не учитывает разницу между поведением до и после Spring 5.1 — это важно для проектов на старых версиях.

---

### Вопрос 47. Что такое exposeProxy = true в @EnableAspectJAutoProxy? В каком сценарии оно необходимо и как им пользоваться через AopContext.currentProxy()? Почему документация Spring не рекомендует использовать этот подход в production-коде?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Proxying Mechanisms — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)

Атрибут `exposeProxy` в аннотации `@EnableAspectJAutoProxy` указывает, что текущий прокси-объект должен быть доступен через `ThreadLocal`-переменную в классе `AopContext`. По умолчанию значение `false` — прокси не раскрывается.

**Сценарий необходимости — самовызов (self-invocation):**

При использовании Spring AOP на основе прокси (JDK-прокси или CGLIB) вызов метода из того же класса через `this` обходит прокси и, следовательно, обходит все применённые советы (advice). Пример:

```java
public class SimplePojo implements Pojo {
    public void foo() {
        // this.bar() обходит прокси — аспект не применяется!
        this.bar();
    }
    public void bar() { /* логика */ }
}
```

Для вызова `bar()` через прокси необходимо:

1. Включить `exposeProxy`:
```java
@Configuration
@EnableAspectJAutoProxy(exposeProxy = true)
public class AppConfig { }
```

2. Использовать `AopContext.currentProxy()`:
```java
public class SimplePojo implements Pojo {
    public void foo() {
        // Вызов через прокси — аспект применяется
        ((Pojo) AopContext.currentProxy()).bar();
    }
}
```

**Почему Spring не рекомендует этот подход в production-коде:**

Документация описывает его как «highly discouraged» и указывает две причины:
1. **Связывание с фреймворком:** код бизнес-логики становится зависим от `AopContext` (класс Spring AOP), что нарушает разделение ответственности.
2. **Потеря прозрачности AOP:** одно из главных преимуществ AOP — незаметное применение сквозной функциональности. Явное обращение к прокси из бизнес-кода это преимущество уничтожает.

Дополнительно: хранение прокси в `ThreadLocal` имеет небольшой performance-cost, что является ещё одной причиной, по которой функция отключена по умолчанию.

**Рекомендуемые альтернативы (в порядке предпочтительности):**
1. Рефакторинг: вынести `bar()` в отдельный бин (самый чистый подход).
2. Self-injection: внедрить сам бин в себя через `@Autowired private MyService self;` и вызывать `self.bar()`.
3. `AopContext.currentProxy()` — только если первые два невозможны.

---

#### Ответ от Claude

**Что такое `exposeProxy = true`**

`@EnableAspectJAutoProxy(exposeProxy = true)` — это флаг уровня конфигурации контейнера Spring, добавленный в Spring Framework 4.3.1. Когда он включён, AOP-фреймворк сохраняет ссылку на текущий прокси-объект в `ThreadLocal`-переменной перед каждым вызовом advised-метода. Эта ссылка доступна через статический метод `AopContext.currentProxy()`.

Без этого флага попытка вызвать `AopContext.currentProxy()` бросает `IllegalStateException`, даже если бин является прокси.

**Единственный сценарий, когда это необходимо — самовызов через `this`**

Spring AOP реализован через прокси: когда внешний код вызывает метод бина, вызов проходит через прокси-объект (CGLIB или JDK Proxy), и все аспекты (транзакции, кэширование, безопасность) применяются. Однако вызов метода внутри того же класса через `this` обходит прокси:

```java
@Service
public class OrderService {

    @Transactional
    public void placeOrder() {
        // Этот вызов обходит прокси — @Transactional на processPayment НЕ работает
        this.processPayment();
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processPayment() { ... }
}
```

Решение через `AopContext.currentProxy()`:

```java
@Configuration
@EnableAspectJAutoProxy(exposeProxy = true)
public class AppConfig { }

@Service
public class OrderService {

    @Transactional
    public void placeOrder() {
        // Вызов через прокси — @Transactional на processPayment РАБОТАЕТ
        ((OrderService) AopContext.currentProxy()).processPayment();
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processPayment() { ... }
}
```

**Почему документация не рекомендует это в production**

Официальная документация Spring называет подход «highly discouraged» по следующим причинам:

1. **Coupling с инфраструктурой:** бизнес-класс импортирует `org.springframework.aop.framework.AopContext` — он знает о том, что работает в AOP-контексте Spring. Это нарушает принцип прозрачности AOP.
2. **Нарушение тестируемости:** при юнит-тестировании без Spring-контекста `AopContext.currentProxy()` бросает `IllegalStateException`, что усложняет тестирование.
3. **Накладные расходы:** каждый вызов advised-метода обновляет `ThreadLocal`, что создаёт небольшой, но постоянный overhead — именно поэтому флаг отключён по умолчанию.
4. **Ложное ощущение корректности:** если `exposeProxy` не установлен (например, в тестовом профиле), код упадёт в рантайме без очевидной причины.

**Корректные альтернативы:**

- **Рефакторинг (лучший вариант):** выделить `processPayment()` в отдельный Spring-бин — самовызов исчезнет, аспекты применятся через обычный механизм прокси.
- **Self-injection:** `@Autowired private OrderService self;` и вызов `self.processPayment()`. Менее инвазивно, не требует `exposeProxy`.
- **AspectJ (compile-time / load-time weaving):** изменяет байт-код напрямую, проблемы самовызова не существует в принципе.

**Важное замечание:** `exposeProxy = true` применяется глобально ко всем прокси в контексте. Это значит, что overhead затрагивает каждый вызов каждого advised-метода, а не только проблемные места.

---

### Вопрос 48. Что такое InstantiationAwareBeanPostProcessor и чем его метод postProcessBeforeInstantiation отличается от BeanPostProcessor.postProcessBeforeInitialization? Что произойдёт, если postProcessBeforeInstantiation вернёт не null?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [InstantiationAwareBeanPostProcessor — Spring Framework 6.2 API](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/config/InstantiationAwareBeanPostProcessor.html)

`InstantiationAwareBeanPostProcessor` — это подинтерфейс `BeanPostProcessor`, добавляющий callback **перед инстанциированием** бина, а также callback после инстанциирования, но до установки явных свойств или autowiring.

Обычно применяется для подавления стандартного инстанциирования для конкретных целевых бинов — например, для создания прокси со специальными `TargetSource` (пул объектов, ленивая инициализация) или для реализации дополнительных стратегий инъекций (например, field injection).

**Метод `postProcessBeforeInstantiation`:**

```java
@Nullable
default Object postProcessBeforeInstantiation(Class<?> beanClass, String beanName)
        throws BeansException
```

Применяется **до того, как целевой бин был инстанциирован**. Возвращённый объект может быть прокси вместо целевого бина, что фактически подавляет стандартное инстанциирование целевого бина.

**Если метод возвращает не-`null`:** процесс создания бина **прерывается (short-circuit)**. Единственная дальнейшая обработка — вызов `BeanPostProcessor.postProcessAfterInitialization` из настроенных `BeanPostProcessor`-ов. Никакой дальнейшей обработки инстанциирования или инициализации не происходит.

Возвращает: объект бина, который будет использоваться вместо стандартного инстанциирования, или `null` для продолжения стандартного инстанциирования.

**Важное замечание:** этот интерфейс является специализированным и предназначен главным образом для внутреннего использования фреймворком. Рекомендуется реализовывать простой интерфейс `BeanPostProcessor`, где это возможно.

---

#### Ответ от Claude

**Что такое `InstantiationAwareBeanPostProcessor`**

`InstantiationAwareBeanPostProcessor` (IABPP) — расширение интерфейса `BeanPostProcessor`, добавляющее точки расширения **до и после инстанциирования** бина. В отличие от базового `BeanPostProcessor`, который работает с уже созданными объектами, IABPP может вмешиваться в сам процесс создания экземпляра.

Интерфейс добавляет три метода:
- `postProcessBeforeInstantiation(Class<?> beanClass, String beanName)` — до вызова конструктора
- `postProcessAfterInstantiation(Object bean, String beanName)` — после конструктора, до установки свойств
- `postProcessProperties(PropertyValues pvs, Object bean, String beanName)` — во время установки свойств

**Сравнение `postProcessBeforeInstantiation` и `postProcessBeforeInitialization`**

| Характеристика | `postProcessBeforeInstantiation` (IABPP) | `postProcessBeforeInitialization` (BeanPostProcessor) |
|---|---|---|
| **Момент вызова** | До вызова конструктора бина | После инстанциирования и установки свойств, до `@PostConstruct` / `afterPropertiesSet()` |
| **Состояние бина** | Бина ещё не существует; доступен только `Class<?>` | Бин полностью создан, свойства проставлены |
| **Параметр** | `Class<?> beanClass` | `Object bean` (готовый экземпляр) |
| **Прерывание цикла** | Да — возврат не-`null` прерывает создание бина | Нет — возврат `null` только пропускает последующие BPP |
| **Типичное применение** | Создание прокси, подмена инстанциирования | Применение аннотаций, инициализация полей, логирование |

**Полный жизненный цикл бина с обоими интерфейсами:**

```
1. IABPP.postProcessBeforeInstantiation()
      - Если не null -> SHORT-CIRCUIT (переход к шагу 8)
2. Вызов конструктора (инстанциирование)
3. IABPP.postProcessAfterInstantiation()
      - Если false -> пропуск установки свойств
4. IABPP.postProcessProperties()
5. Установка свойств (autowiring)
6. BPP.postProcessBeforeInitialization()    <-- базовый BeanPostProcessor
7. Инициализация (@PostConstruct, afterPropertiesSet(), init-method)
8. BPP.postProcessAfterInitialization()
```

**Что происходит, если `postProcessBeforeInstantiation` возвращает не-`null`**

Возврат не-`null` из `postProcessBeforeInstantiation` вызывает **short-circuit**: Spring полностью пропускает стандартный механизм создания бина. Конкретно:

- Конструктор бина **не вызывается**
- `postProcessAfterInstantiation` **не вызывается**
- `postProcessProperties` **не вызывается**
- Установка свойств и autowiring **не выполняются**
- `postProcessBeforeInitialization` **не вызывается**
- Методы инициализации (`@PostConstruct`, `afterPropertiesSet()`, `init-method`) **не вызываются**

Единственный шаг, который всё равно выполняется — `BeanPostProcessor.postProcessAfterInitialization()`. Это позволяет другим зарегистрированным процессорам (например, AOP-прокси-ориентированным) при необходимости обернуть возвращённый объект.

Возвращённый объект используется как финальный бин для данного имени (`beanName`) в контексте.

**Практический пример применения**

`AbstractAutoProxyCreator` (основа Spring AOP) реализует `InstantiationAwareBeanPostProcessor`. Для бинов, у которых уже заготовлен `TargetSource` (например, пул объектов), он возвращает готовый прокси из `postProcessBeforeInstantiation`, не создавая обычный бин вообще. Для большинства бинов возвращает `null` — нормальное инстанциирование продолжается, а прокси создаётся в `postProcessAfterInitialization`.

**Почему это интерфейс для внутреннего использования**

Официальная документация Spring характеризует IABPP как «special-purpose interface, primarily for internal use within the framework» и рекомендует использовать простой `BeanPostProcessor` везде, где это возможно. Причины:

1. Возврат не-`null` полностью обходит механизм жизненного цикла Spring, включая DI — результирующий бин может оказаться неинициализированным.
2. Высокая вероятность непредвиденных побочных эффектов при взаимодействии с другими процессорами.
3. API достаточно низкоуровневый: неправильная реализация может нарушить работу всего контекста.

Встроенные реализации IABPP в Spring: `AbstractAutoProxyCreator`, `AutowiredAnnotationBeanPostProcessor`, `CommonAnnotationBeanPostProcessor`.
### Вопрос 49. Почему в Spring Boot 2.0+ по умолчанию используется CGLIB-прокси (spring.aop.proxy-target-class=true) вместо JDK Dynamic Proxy? Какую конкретную проблему это решило и какие новые ограничения вносит (например, при использовании классов из java.base-модуля)?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Spring Boot 2.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-2.0-Migration-Guide)

Spring Boot теперь использует CGLIB-проксирование по умолчанию, включая поддержку AOP. Если вам нужны прокси на основе интерфейсов (JDK Dynamic Proxy), необходимо установить `spring.aop.proxy-target-class=false`.

До Spring Boot 2.0 ситуация была непоследовательной: начиная с версии 1.4 Spring Boot уже применял CGLIB-прокси для транзакций, но для общих AOP-настроек по-прежнему использовался JDK Dynamic Proxy. Это приводило к тому, что один и тот же приложенческий компонент мог получать разные типы прокси в зависимости от того, какая функция его оборачивала. Изменение в 2.0 выровняло поведение: отныне весь Spring Boot-стек использует CGLIB единообразно.

#### Ответ от Claude

**Предыстория: почему было две стратегии**

До Spring Boot 2.0 Spring Framework по умолчанию предпочитал JDK Dynamic Proxy: если бин реализует хотя бы один интерфейс — создаётся JDK-прокси, иначе — CGLIB. Это поведение описано в `DefaultAopProxyFactory`. Spring Boot 1.x, однако, уже переключился на CGLIB для транзакций (`@EnableTransactionManagement`) начиная с 1.4, оставив AOP в целом на JDK-прокси. Непоследовательность порождала трудно диагностируемые баги: разработчик мог получить JDK-прокси в одном месте и CGLIB в другом.

**Конкретная проблема, которую решил переход на CGLIB**

Главная проблема JDK Dynamic Proxy — он проксирует только методы интерфейса. Бин, не реализующий никакого интерфейса, не мог быть проксирован JDK Dynamic Proxy вообще. С широким распространением component-scan и Spring Boot auto-configuration конкретных классов без интерфейсов стало много. CGLIB создаёт прокси путём порождения подкласса целевого класса в runtime, не требуя интерфейса.

Дополнительная историческая проблема CGLIB — обязательный конструктор без аргументов. Она была снята в Spring 4 за счёт интеграции библиотеки Objenesis: теперь CGLIB-прокси создаётся без вызова конструктора целевого класса вообще, что делает CGLIB пригодным для классов с constructor injection.

В итоге в Spring Boot 2.0 приняли решение: раз CGLIB теперь технически безопасен и уже используется для транзакций — сделать его единственным дефолтом для единообразия. Это устраняло класс проблем, при которых явно выставленные аннотации `@EnableAspectJAutoProxy(proxyTargetClass=false)` игнорировались из-за конфликта глобального Boot-умолчания.

**Ограничения CGLIB**

Официальная документация Spring Framework перечисляет следующие ограничения CGLIB-прокси:

1. `final`-классы не могут быть проксированы — их нельзя унаследовать.
2. `final`-методы не могут быть перехвачены — их нельзя переопределить.
3. `private`-методы не могут быть перехвачены.
4. Методы с доступом уровня package из родительского класса из другого пакета фактически недоступны для переопределения.
5. **Ограничение Java Module System**: нельзя создать CGLIB-прокси для класса из пакета `java.lang` (модуль `java.base`) при развёртывании на module path. В таком случае требуется JVM-флаг `--add-opens=java.base/java.lang=ALL-UNNAMED`. Это актуально, например, при попытке проксировать классы стандартной библиотеки или при использовании сторонних библиотек с классами из закрытых модулей.
6. Конструктор целевого класса не вызывается дважды — Objenesis обходит его для создания прокси-экземпляра.

**Как вернуться к JDK Dynamic Proxy**

```properties
spring.aop.proxy-target-class=false
```

При этом бины, не реализующие интерфейс, по-прежнему получат CGLIB-прокси — это поведение `DefaultAopProxyFactory`, не изменяемое данной настройкой.

**Расхождение между источниками**: часть документации Spring Framework описывает JDK Dynamic Proxy как «дефолт фреймворка», тогда как Spring Boot явно переопределяет этот дефолт. Важно понимать, что `spring.aop.proxy-target-class` — это Boot-специфичная настройка, отсутствующая в чистом Spring Framework.

---

### Вопрос 50. Можно ли поставить @Transactional на метод интерфейса? Гарантирует ли это, что реализация получит транзакционное поведение? Как это зависит от типа используемого прокси (JDK Dynamic Proxy vs CGLIB) и изменилось ли поведение в Spring 6?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Using @Transactional — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

Аннотацию `@Transactional` можно ставить на определение интерфейса, метод интерфейса, определение класса или метод класса. Однако Spring-команда рекомендует аннотировать методы конкретных классов, а не интерфейсов — даже несмотря на то, что начиная со Spring 5.0 это работает и для interface-based, и для target-class прокси.

Причина рекомендации: поскольку Java-аннотации не наследуются из интерфейсов, аннотации на уровне интерфейса не распознаются инфраструктурой AspectJ-weaving. При использовании режима `AdviceMode.ASPECTJ` транзакционные аннотации на интерфейсе будут молча проигнорированы.

Критичное ограничение: транзакционные методы в interface-based прокси (JDK) обязаны быть `public` и объявлены в проксируемом интерфейсе.

Начиная со Spring 6.0 `protected` и package-visible методы тоже могут быть транзакционными — но только для class-based прокси (CGLIB). Для JDK Dynamic Proxy по-прежнему поддерживаются только `public`-методы.

#### Ответ от Claude

**Можно ли технически поставить @Transactional на метод интерфейса?**

Да, синтаксически это допустимо. Spring понимает такую аннотацию и в большинстве случаев применяет транзакционное поведение. Но поведение зависит от ряда факторов.

**Поведение в зависимости от типа прокси**

_JDK Dynamic Proxy (interface-based)_:
- Прокси реализует тот же интерфейс, что и бин.
- Аннотация `@Transactional` на методе интерфейса видна прокси-механизму через рефлексию интерфейса.
- Транзакционное поведение применяется корректно при вызове метода через интерфейс.
- Ограничение: метод должен быть `public`.

_CGLIB (class-based)_:
- Прокси является подклассом конкретного класса.
- До Spring 5.0 аннотация `@Transactional` на интерфейсном методе при CGLIB-прокси могла игнорироваться: поиск цепочки советов давал пустой результат, и транзакция не создавалась (баг SPR-14322, исправлен к Spring 5.0 RC1).
- Начиная со Spring 5.0 CGLIB-прокси также учитывает `@Transactional` на методах интерфейса — аннотация читается из интерфейса через `AnnotationUtils`.
- Ограничение: несмотря на поддержку, рекомендуется аннотировать конкретный класс, а не интерфейс.

**Изменения в Spring 6**

Spring 6.0 расширил видимость транзакционных методов для class-based прокси:

| Видимость метода | JDK Dynamic Proxy | CGLIB (до Spring 6) | CGLIB (Spring 6+) |
|---|---|---|---|
| `public` | Поддерживается | Поддерживается | Поддерживается |
| `protected` | Не поддерживается | Не поддерживается | Поддерживается |
| package-private | Не поддерживается | Не поддерживается | Поддерживается |
| `private` | Не поддерживается | Не поддерживается | Не поддерживается |

Таким образом, Spring 6 снял ограничение «только public» для CGLIB, но JDK Dynamic Proxy по-прежнему работает только с `public`-методами интерфейса.

**Почему @Transactional на интерфейсе не гарантирует транзакцию при AspectJ-режиме**

Java-аннотации не наследуются из интерфейсов (это ограничение спецификации JVM). При использовании AspectJ load-time или compile-time weaving (`@EnableTransactionManagement(mode = AdviceMode.ASPECTJ)`) байткод-инфраструктура ищет аннотацию непосредственно на классе и его методах. Аннотация на интерфейсе в этом режиме не обнаруживается, и транзакция не применяется — причём без каких-либо ошибок (silent failure).

**Важное ограничение для обоих типов прокси: self-invocation**

Независимо от типа прокси, вызов `@Transactional`-метода через `this` внутри того же класса обходит прокси и не создаёт транзакцию:

```java
public class OrderService {
    public void process() {
        this.save(); // транзакция НЕ будет создана — вызов минует прокси
    }

    @Transactional
    public void save() { ... }
}
```

Решения: рефакторинг, self-injection через `@Autowired`, или переход на `AdviceMode.ASPECTJ`.

**Рекомендация Spring-команды**

Аннотировать методы конкретных классов (`@Transactional` на implementation, а не на интерфейсе), чтобы поведение было предсказуемым при любом типе прокси и при любом режиме advice.

**Расхождения между источниками**: в ряде блогов встречается утверждение, что `@Transactional` на интерфейсе «не работает с CGLIB» — это было справедливо до Spring 5.0, но начиная с 5.0 Spring исправил это поведение (SPR-14322). Официальная документация Spring 6 подтверждает, что оба типа прокси поддерживают аннотацию на интерфейсе, но AspectJ-режим по-прежнему является исключением.

### Вопрос 51. Code review: найдите минимум 8 проблем в этом Spring-сервисе оплаты заказа.

```java
@Service
public class OrderService {
    @Autowired
    private OrderRepository repo;
    @Autowired
    private PaymentClient paymentClient;

    @Transactional
    public void pay(Long orderId, double amount) {
        Order order = repo.findAll().stream()
                .filter(o -> o.getId().equals(orderId))
                .findFirst().get();
        System.out.println("Paying order " + orderId);
        PaymentResult r = paymentClient.charge(amount);
        order.setStatus(new OrderStatus("PAID"));
        repo.save(order);
    }
}
```

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Habr — Java-собеседование 2025: разбор вопросов](https://habr.com/ru/articles/1043906/)

Согласно разбору в статье, типичные проблемы такого сервиса: внедрение зависимостей через поле (`@Autowired` на поле) вместо конструктора; вывод в `System.out` вместо логгера; использование `double` для денег; выборка `findAll()` с фильтрацией в памяти вместо `findById`; вызов `Optional.get()` без проверки; `@Transactional` без осмысленных параметров; создание объекта через `new` вместо управляемого бина/enum; обращение к внешнему сервису без таймаута.

#### Ответ от Claude

Проблемы и как исправить:

1. **Field injection** (`@Autowired` на поле) — мешает тестированию. Используйте внедрение через конструктор (`final`-поля). См. [Baeldung — Constructor Injection](https://www.baeldung.com/constructor-injection-in-spring).
2. **`double` для денег** — потеря точности; используйте `java.math.BigDecimal`.
3. **`repo.findAll().stream().filter(...)`** — выгружает всю таблицу в память; нужно `repo.findById(orderId)`.
4. **`Optional.get()` без проверки** — `NoSuchElementException`; используйте `orElseThrow(...)`.
5. **`System.out.println`** вместо логгера (SLF4J).
6. **Внешний вызов `paymentClient.charge()` внутри `@Transactional`** — удерживает соединение с БД на время сетевого запроса (риск исчерпания пула). Платёж выносят за транзакцию; вызов должен иметь **таймаут**.
7. **`@Transactional` без параметров** — нет `timeout`, не задан `rollbackFor`, для чтения забывают `readOnly`.
8. **`new OrderStatus("PAID")`** — «магическая строка»; статус лучше моделировать `enum`.
9. Дополнительно: результат `PaymentResult r` игнорируется; нет идемпотентности повторной оплаты и обработки ошибок.

---

### Вопрос 52. Что такое FactoryBean? Как работают методы getObject(), getObjectType() и isSingleton()? Как получить из контейнера сам объект FactoryBean, а не продукт, который он производит?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Customizing Instantiation Logic with a FactoryBean — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html#beans-factory-extension-factorybean)

`FactoryBean` — интерфейс Spring, предоставляющий точку расширения логики инстанциирования IoC-контейнера. Он полезен, когда сложную инициализацию объекта лучше выразить в Java-коде, а не в громоздкой XML-конфигурации.

Интерфейс `FactoryBean<T>` содержит три метода:

- **`T getObject()`** — возвращает экземпляр объекта, создаваемого этой фабрикой. Экземпляр может быть разделяемым (синглтон) или новым (прототип) — в зависимости от значения `isSingleton()`.
- **`Class<?> getObjectType()`** — возвращает тип объекта, производимого методом `getObject()`. Если тип неизвестен заранее, возвращает `null`. Контейнер использует это при разрешении зависимостей по типу.
- **`boolean isSingleton()`** — если `true` (по умолчанию), `getObject()` возвращает общий экземпляр; если `false` — новый экземпляр при каждом обращении.

Чтобы получить из контейнера сам объект `FactoryBean`, а не его продукт, нужно при обращении к `getBean(...)` указать имя бина с префиксом `&`:

```java
// Возвращает продукт фабрики
MyBean product = context.getBean("myBean", MyBean.class);

// Возвращает сам объект FactoryBean
FactoryBean<?> factory = context.getBean("&myBean", FactoryBean.class);
```

В самом Spring более 50 встроенных реализаций `FactoryBean`.

#### Ответ от Claude

**Что такое FactoryBean**

`FactoryBean<T>` (пакет `org.springframework.beans.factory`) — специальный интерфейс, который сообщает Spring IoC-контейнеру: «этот бин не является конечным объектом, а представляет собой фабрику, производящую объекты». Контейнер автоматически вызывает `getObject()` и использует возвращаемое значение как реальный бин.

**Три метода интерфейса:**

| Метод | Назначение |
|---|---|
| `T getObject()` | Возвращает объект, который Spring предоставит как бин потребителям |
| `Class<?> getObjectType()` | Тип возвращаемого объекта; используется контейнером для autowiring по типу |
| `boolean isSingleton()` | Управляет кешированием: `true` — результат `getObject()` кешируется и повторно используется; `false` — вызывается при каждом обращении |

**Пример реализации:**

```java
public class ConnectionFactoryBean implements FactoryBean<Connection> {

    private String url;

    @Override
    public Connection getObject() throws Exception {
        return DriverManager.getConnection(url);
    }

    @Override
    public Class<?> getObjectType() {
        return Connection.class;
    }

    @Override
    public boolean isSingleton() {
        return true; // соединение кешируется
    }
}
```

После регистрации этого бина под именем `connection` — `context.getBean("connection")` вернёт `Connection`, а не `ConnectionFactoryBean`.

**Как получить сам FactoryBean**

Когда контейнер видит запрос `getBean("myBean")`, он автоматически вызывает `getObject()`. Чтобы вместо этого получить сам объект фабрики, используется специальный префикс `&`:

```java
context.getBean("&myBean", ConnectionFactoryBean.class);
```

Это же работает при autowiring через `@Qualifier("&myBean")` (нестандартный случай) или через прямой вызов `BeanFactory.getBean("&beanName")`.

**Разница между FactoryBean и @Bean:**

| Аспект | @Bean | FactoryBean |
|---|---|---|
| Место | Метод в @Configuration | Отдельный класс |
| Тип объекта | Явно задан типом метода | Задаётся через `getObjectType()` |
| isSingleton | Управляется scope | Управляется методом `isSingleton()` |
| Когда применять | Большинство случаев | Сложная инициализация, интеграция с чужими API |

Типичные встроенные реализации в Spring: `SqlSessionFactoryBean` (MyBatis), `LocalContainerEntityManagerFactoryBean` (JPA), `EhCacheManagerFactoryBean`.

**Расхождений между источниками не выявлено.**

---

### Вопрос 53. Что такое ObjectProvider в Spring и чем он отличается от прямого @Autowired (required=false)? Какие методы он предоставляет (getIfAvailable, getIfUnique, stream, orderedStream) и когда правильно использовать каждый?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ObjectProvider (Spring Framework 6.1 API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/ObjectProvider.html)

`ObjectProvider<T>` — вариант `ObjectFactory<T>`, разработанный специально для точек инжекции, требующих программной необязательности и гибкого разрешения бина. Интерфейс расширяет `ObjectFactory<T>` и `Iterable<T>`.

Ключевые методы:

- **`T getObject()`** — возвращает бин или бросает `NoSuchBeanDefinitionException`; при нескольких кандидатах бросает `NoUniqueBeanDefinitionException`.
- **`T getIfAvailable()`** — возвращает бин или `null`, если ни одного нет; при нескольких — `NoUniqueBeanDefinitionException`.
- **`T getIfAvailable(Supplier<T> defaultSupplier)`** — то же, но с fallback-значением вместо `null`.
- **`T getIfUnique()`** — возвращает бин, только если он уникален; при нескольких кандидатах или при отсутствии бина — `null`.
- **`void ifAvailable(Consumer<T>)`** — выполняет действие, если бин доступен.
- **`Stream<T> stream()`** — все бины данного типа в произвольном порядке.
- **`Stream<T> orderedStream()`** — то же, но упорядоченные по `@Order` / `Ordered`.

#### Ответ от Claude

**В чём проблема @Autowired(required=false)**

```java
@Autowired(required = false)
private MetricsCollector metricsCollector; // может быть null
```

Поле может остаться `null`, и при каждом использовании нужно проверять: `if (metricsCollector != null) { ... }`. Это шумно и легко забыть.

Дополнительная проблема: если бинов подходящего типа несколько и ни один не помечен `@Primary`, Spring всё равно выбросит `NoUniqueBeanDefinitionException` — флаг `required=false` помогает только при полном отсутствии бина.

**ObjectProvider как решение**

```java
@Autowired
private ObjectProvider<MetricsCollector> metricsCollectorProvider;

public void doWork() {
    metricsCollectorProvider.ifAvailable(mc -> mc.record("event"));
}
```

Поле всегда не-`null` (это провайдер), бин разрешается лениво при вызове метода провайдера.

**Основные методы и сценарии применения:**

| Метод | Возвращает | Когда использовать |
|---|---|---|
| `getObject()` | Бин или исключение | Требуется ровно один бин (аналог обычного autowired) |
| `getIfAvailable()` | Бин или `null` | Необязательная одиночная зависимость |
| `getIfAvailable(Supplier)` | Бин или default | С фолбэком вместо `null` |
| `getIfUnique()` | Бин, `null` если 0 или >1 | Нужен ровно один, но при нескольких — игнорировать |
| `ifAvailable(Consumer)` | void | Условное использование без проверки `null` |
| `stream()` | Все бины типа | Обработать все зарегистрированные реализации |
| `orderedStream()` | Все бины по @Order | Обработать реализации в заданном порядке |

**Пример с множеством бинов:**

```java
@Component
public class EventBus {
    private final ObjectProvider<EventHandler> handlers;

    public EventBus(ObjectProvider<EventHandler> handlers) {
        this.handlers = handlers;
    }

    public void publish(Event event) {
        handlers.orderedStream().forEach(h -> h.handle(event));
    }
}
```

**Ключевые отличия от @Autowired(required=false):**

1. **Ленивое разрешение** — бин создаётся только в момент вызова метода провайдера, а не при инициализации содержащего бина.
2. **Безопасность при множестве бинов** — `getIfUnique()` возвращает `null` вместо исключения.
3. **Итерация** — `stream()` / `orderedStream()` позволяют работать с несколькими бинами одного типа.
4. **Функциональный стиль** — `ifAvailable`, `ifUnique` убирают явные `null`-проверки.

**Расхождений между источниками не выявлено.**

---

### Вопрос 54. Как работает @Lookup (метод-инжекция)? Какую проблему он решает по сравнению с прямым @Autowired, какие ограничения накладывает CGLIB и почему @Lookup не работает в @Bean-методах @Configuration?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Method Injection — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-method-injection.html)

Предположим, что singleton-бин A нуждается в non-singleton (prototype) бине B и требует новый экземпляр B при каждом вызове метода A. Контейнер создаёт singleton-бин A единожды и, следовательно, только раз получает возможность установить свойства: не может предоставить бину A новый экземпляр B при каждом обращении.

Метод-инжекция через `@Lookup` решает эту задачу: Spring использует CGLIB для динамической генерации подкласса, который переопределяет аннотированный метод так, чтобы при каждом вызове выполнялся `getBean()` в контейнере:

```java
public abstract class CommandManager {
    public Object process(Object commandState) {
        Command command = createCommand();
        command.setState(commandState);
        return command.execute();
    }

    @Lookup
    protected abstract Command createCommand();
}
```

Ограничения, которые накладывает CGLIB:

1. Класс, содержащий `@Lookup`-метод, не может быть `final`.
2. Сам `@Lookup`-метод не может быть `final`.
3. Юнит-тестирование абстрактного класса требует ручной реализации подкласса.
4. `@Lookup` не работает с `@Bean`-методами в `@Configuration`-классах: «Lookup methods do not work with factory methods and in particular not with `@Bean` methods in configuration classes.»

#### Ответ от Claude

**Проблема: prototype-бин в singleton**

При обычном `@Autowired` Spring инжектирует prototype-бин единожды — при создании singleton. Все дальнейшие вызовы используют тот же экземпляр:

```java
@Component
public class OrderProcessor {
    @Autowired
    private OrderCommand orderCommand; // singleton получает один экземпляр prototype навсегда

    public void process() {
        orderCommand.execute(); // всегда один и тот же объект!
    }
}
```

**Решение: @Lookup**

```java
@Component
public abstract class OrderProcessor {

    public void process(OrderData data) {
        OrderCommand command = createCommand(); // новый экземпляр при каждом вызове
        command.init(data);
        command.execute();
    }

    @Lookup
    protected abstract OrderCommand createCommand();
    // или с явным именем: @Lookup("orderCommand")
}
```

Spring через CGLIB создаёт подкласс `OrderProcessor` и переопределяет `createCommand()` так, что каждый вызов эквивалентен `applicationContext.getBean(OrderCommand.class)`. Класс может быть как `abstract` (тогда метод тоже `abstract`), так и конкретным (метод может иметь stub-реализацию):

```java
// Вариант с конкретным классом (stub-тело игнорируется Spring)
@Lookup
protected OrderCommand createCommand() {
    return null; // Spring перегрузит этот метод через CGLIB
}
```

**Ограничения CGLIB:**

1. Класс-контейнер не должен быть `final` — CGLIB создаёт подкласс.
2. `@Lookup`-метод не должен быть `final` — метод должен быть переопределяем.
3. Не работает с `static` методами.
4. Не работает в `@Bean`-методах `@Configuration`-класса: `@Bean`-метод — это фабричный метод, вызываемый один раз; CGLIB не может вмешаться в логику его переопределения так же, как при component-scan. Для `@Bean`-классов нужно использовать `ObjectProvider<T>` как параметр метода.

**Альтернативы @Lookup:**

| Решение | Достоинства | Недостатки |
|---|---|---|
| `@Lookup` | Чистый код, нет зависимости от контейнера | Требует CGLIB, класс не `final` |
| `ObjectProvider<T>` | Гибкость, работает везде | Немного больше кода |
| `ApplicationContext.getBean()` | Просто | Связывает бизнес-код с контейнером |
| Scoped proxy | Прозрачно для потребителя | Нужна явная настройка `@Scope(proxyMode=...)` |

**Расхождений между источниками не выявлено.**

---

### Вопрос 55. Что такое @ComponentScan и как работают его фильтры (includeFilters, excludeFilters)? Перечислите типы фильтров (ANNOTATION, ASSIGNABLE_TYPE, REGEX, CUSTOM) и объясните роль useDefaultFilters.

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Using Filters to Customize Scanning — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html#beans-scanning-filters)

По умолчанию Spring обнаруживает классы, аннотированные `@Component`, `@Repository`, `@Service`, `@Controller`, `@RestController`, `@Configuration`. Это поведение — «фильтры по умолчанию» — можно расширить или заменить с помощью атрибутов `includeFilters` и `excludeFilters` аннотации `@ComponentScan`.

Поддерживаемые типы фильтров:

| Тип фильтра | Выражение | Описание |
|---|---|---|
| `annotation` (по умолчанию) | `org.example.SomeAnnotation` | Аннотация присутствует или мета-присутствует на уровне типа |
| `assignable` | `org.example.SomeClass` | Класс/интерфейс, которому целевой компонент assignable (наследует/реализует) |
| `aspectj` | `org.example..*Service+` | Выражение типа AspectJ |
| `regex` | `org\.example\.Default.*` | Регулярное выражение по имени класса |
| `custom` | `org.example.MyTypeFilter` | Реализация интерфейса `org.springframework.core.type.TypeFilter` |

Пример — исключить `@Repository` и включить «Stub»-реализации:

```java
@Configuration
@ComponentScan(basePackages = "org.example",
    includeFilters = @Filter(type = FilterType.REGEX, pattern = ".*Stub.*Repository"),
    excludeFilters = @Filter(Repository.class))
public class AppConfig { }
```

Атрибут `useDefaultFilters = false` полностью отключает стандартное распознавание стереотипных аннотаций, оставляя только явно заданные фильтры.

#### Ответ от Claude

**Что такое @ComponentScan**

`@ComponentScan` указывает контейнеру, в каких пакетах искать компоненты-кандидаты (классы, которые нужно зарегистрировать как бины). В паре с `@Configuration` заменяет XML-элемент `<context:component-scan>`.

**useDefaultFilters**

По умолчанию `useDefaultFilters = true`: Spring автоматически регистрирует классы с любой из следующих аннотаций (или их метааннотаций): `@Component`, `@Repository`, `@Service`, `@Controller`, `@RestController`, `@Configuration`.

При `useDefaultFilters = false` Spring не регистрирует ничего автоматически — только то, что явно включено через `includeFilters`. Это полезно, когда нужен полный ручной контроль над сканированием (например, в тестах или при конфигурации отдельного слоя).

**Типы фильтров с примерами:**

```java
// 1. ANNOTATION — по наличию аннотации (или мета-аннотации)
@ComponentScan(
    includeFilters = @Filter(type = FilterType.ANNOTATION, classes = MyCustomAnnotation.class)
)

// 2. ASSIGNABLE_TYPE — по типу (наследует или реализует)
@ComponentScan(
    includeFilters = @Filter(type = FilterType.ASSIGNABLE_TYPE, classes = BaseRepository.class)
)

// 3. REGEX — по регулярному выражению на полном имени класса
@ComponentScan(
    excludeFilters = @Filter(type = FilterType.REGEX, pattern = ".*Test.*")
)

// 4. ASPECTJ — по выражению AspectJ
@ComponentScan(
    includeFilters = @Filter(type = FilterType.ASPECTJ, pattern = "com.example..*ServiceImpl")
)

// 5. CUSTOM — собственная реализация TypeFilter
@ComponentScan(
    includeFilters = @Filter(type = FilterType.CUSTOM, classes = MyTypeFilter.class)
)
```

**Реализация кастомного фильтра:**

```java
public class MyTypeFilter implements TypeFilter {
    @Override
    public boolean match(MetadataReader metadataReader,
                         MetadataReaderFactory metadataReaderFactory) throws IOException {
        ClassMetadata classMetadata = metadataReader.getClassMetadata();
        return classMetadata.getClassName().endsWith("Handler");
    }
}
```

**Приоритет excludeFilters над includeFilters:** если класс попадает под оба фильтра, он исключается.

**Типичные сценарии:**

- `excludeFilters` с `ASSIGNABLE_TYPE = BaseTestConfig.class` — исключить тестовую конфигурацию из production-скана.
- `includeFilters` с `ANNOTATION = WebController.class` + `useDefaultFilters = false` — регистрировать только контроллеры для веб-слоя.
- `REGEX` с `.*Stub.*` — включить заглушки в тестовый контекст.

**Расхождений между источниками не выявлено.**

---

### Вопрос 56. Что такое @Value в Spring? Объясните разницу между синтаксисом ${...} (property placeholder) и #{...} (SpEL-выражение), как задать значение по умолчанию и что происходит, если свойство не найдено?

**Категория:** Spring · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Using @Value — Spring Framework Reference](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/value-annotations.html)

`@Value` используется для инъекции значений в Spring-бины из различных источников.

**Property placeholder `${...}`** — ищет значение по имени ключа в зарегистрированных `PropertySource`-ах (файлы свойств, переменные окружения, system properties):

```java
@Component
public class MovieRecommender {
    private final String catalog;

    public MovieRecommender(@Value("${catalog.name}") String catalog) {
        this.catalog = catalog;
    }
}
```

**Значение по умолчанию** задаётся через двоеточие:

```java
@Value("${catalog.name:defaultCatalog}")
private String catalogName;
```

**SpEL-выражение `#{...}`** — вычисляется Spring Expression Language:

```java
@Value("#{systemProperties['user.catalog'] + 'Catalog'}")
private String catalog;
```

Можно инжектировать сложные структуры:

```java
@Value("#{{'Thriller': 100, 'Comedy': 300}}")
private Map<String, Integer> countOfMoviesPerCatalog;
```

Spring автоматически конвертирует простые типы (`int`, `boolean`, `String[]`) при инжекции через `@Value`.

#### Ответ от Claude

**@Value — два режима синтаксиса:**

| Синтаксис | Тип | Когда вычисляется | Пример |
|---|---|---|---|
| `${key}` | Property placeholder | Разрешается из PropertySource | `${server.port}` |
| `#{expr}` | SpEL | Вычисляется как Java-выражение | `#{T(Math).PI}` |

**${...} — property placeholder**

Работает через `PropertySourcesPlaceholderConfigurer` (или `PropertyPlaceholderConfigurer` в старых версиях), который является `BeanFactoryPostProcessor`. Он ищет значение по ключу в иерархии `PropertySource`-ов, зарегистрированных в `Environment`.

```java
@Value("${server.port:8080}")
private int port; // 8080, если свойство не задано

@Value("${app.features}")
private String[] features; // автоматически парсит "feat1,feat2" → массив
```

**Что происходит, если свойство не найдено:**

- При `PropertySourcesPlaceholderConfigurer` с дефолтными настройками: если нет значения по умолчанию и свойство отсутствует — в поле подставится строка-«заглушка» `${key}` буквально (не `null`!), что обычно является ошибкой конфигурации.
- Если явно создать `PropertySourcesPlaceholderConfigurer` с вызовом `setIgnoreUnresolvablePlaceholders(false)` — будет брошен `BeanDefinitionStoreException` при старте контейнера.
- В Spring Boot по умолчанию неразрешённый placeholder вызывает ошибку при старте.

**#{...} — SpEL-выражение**

Вычисляется движком Spring Expression Language и позволяет:

```java
// Обращение к системным свойствам
@Value("#{systemProperties['java.version']}")
private String javaVersion;

// Вызов статических методов
@Value("#{T(java.lang.Math).random()}")
private double randomValue;

// Обращение к другому бину
@Value("#{configBean.maxRetries}")
private int maxRetries;

// Тернарный оператор
@Value("#{systemEnvironment['ENV'] == 'prod' ? 'strict' : 'lenient'}")
private String mode;
```

**Комбинирование синтаксисов:**

```java
// SpEL читает свойство из Environment
@Value("#{environment.getProperty('catalog.name')}")
private String catalogName;

// Или сокращённо через ${} внутри #{}
@Value("#{${timeout.seconds} * 1000}")
private long timeoutMs;
```

**Практические рекомендации:**

- Для простых свойств конфигурации предпочитайте `${...}` — это читаемо и явно указывает источник.
- Используйте `#{...}` только когда нужны вычисления: Math, String-операции, обращение к другим бинам.
- Всегда задавайте значение по умолчанию (`${key:default}`) для необязательных свойств — это устраняет хрупкость конфигурации.
- В Spring Boot предпочитайте `@ConfigurationProperties` для группы связанных свойств — это типобезопасно и удобнее для тестирования.

**Расхождений между источниками не выявлено.**

---

### Вопрос 57. Как работает абстракция PropertySource в Spring? Какие источники свойств включены по умолчанию в StandardEnvironment, каков их приоритет, и как добавить собственный PropertySource через @PropertySource или программно?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [PropertySource Abstraction — Spring Framework Reference (Environment Abstraction)](https://docs.spring.io/spring-framework/reference/core/beans/environment.html#beans-property-source-abstraction)

`PropertySource` — простая абстракция над любым источником пар ключ-значение. Абстракция `Environment` обеспечивает поиск по конфигурируемой иерархии источников свойств.

**Источники по умолчанию в `StandardEnvironment`:**

1. JVM system properties (`System.getProperties()`)
2. System environment variables (`System.getenv()`)

Для веб-приложений (`StandardServletEnvironment`) добавляются:

3. `ServletConfig` parameters
4. `ServletContext` parameters
5. JNDI environment variables (`java:comp/env/`)

**Приоритет:** более ранние (верхние) записи переопределяют нижние.

**Добавление кастомного PropertySource через `@PropertySource`:**

```java
@Configuration
@PropertySource("classpath:/com/myco/app.properties")
public class AppConfig {
    @Autowired
    Environment env;

    @Bean
    public TestBean testBean() {
        TestBean testBean = new TestBean();
        testBean.setName(env.getProperty("testbean.name"));
        return testBean;
    }
}
```

**Программное добавление:**

```java
ConfigurableApplicationContext ctx = new GenericApplicationContext();
MutablePropertySources sources = ctx.getEnvironment().getPropertySources();
sources.addFirst(new MyPropertySource());
```

#### Ответ от Claude

**Архитектура PropertySource и Environment**

`Environment` — центральный интерфейс Spring, моделирующий среду выполнения приложения через два аспекта: **профили** и **свойства**. Для свойств `Environment` предоставляет доступ к упорядоченному стеку `PropertySource`-ов через `MutablePropertySources`.

При поиске значения по ключу Spring обходит источники по порядку (сверху вниз) и возвращает первое найденное значение. Семантика — переопределение, а не слияние.

**Источники в StandardEnvironment (порядок по убыванию приоритета):**

1. **JVM system properties** (`System.getProperties()`) — устанавливаются через `-Dkey=value` при запуске JVM. Имеют наивысший приоритет из двух стандартных источников.
2. **OS environment variables** (`System.getenv()`) — переменные окружения операционной системы.

В `StandardServletEnvironment` (Spring MVC) дополнительно:

3. **`ServletConfig` init params** — параметры инициализации из `web.xml` для конкретного сервлета.
4. **`ServletContext` init params** — параметры контекста из `web.xml` (`<context-param>`).
5. **JNDI** — `java:comp/env/` записи.

Затем идут стандартные:

6. JVM system properties
7. OS environment variables

**@PropertySource — декларативное добавление:**

`@PropertySource` добавляет файл свойств в `Environment`. По умолчанию новый источник добавляется в конец очереди (наименьший приоритет, после системных источников):

```java
@Configuration
@PropertySource("classpath:application.properties")
@PropertySource("classpath:override.properties") // переопределяет значения из application.properties
public class AppConfig { }
```

Поддержка плейсхолдеров в пути:

```java
@PropertySource("classpath:${env:default}/app.properties")
```

**Программное управление приоритетом:**

```java
ConfigurableEnvironment env = applicationContext.getEnvironment();
MutablePropertySources sources = env.getPropertySources();

// Добавить с наивысшим приоритетом (перекроет всё, включая системные свойства)
sources.addFirst(new MapPropertySource("mySource", Map.of("key", "value")));

// Добавить с наименьшим приоритетом
sources.addLast(new MapPropertySource("mySource", Map.of("key", "default")));

// Добавить перед конкретным источником
sources.addBefore("systemProperties", new MapPropertySource("mySource", Map.of()));
```

**Сводная таблица приоритетов в Spring Boot (для справки):**

В Spring Boot `PropertySource`-ов значительно больше; по убыванию приоритета (от наивысшего): аргументы командной строки → `@TestPropertySource` (в тестах) → JNDI → `System.getProperties()` → `System.getenv()` → `@PropertySource`-аннотации → `application.properties` → дефолты `SpringApplication`.

**Расхождений между источниками не выявлено.**

---

### Вопрос 58. Что делает @Import? Объясните разницу между импортом @Configuration-класса, реализацией ImportSelector (selectImports) и реализацией ImportBeanDefinitionRegistrar. Когда применять каждый из трёх вариантов?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Import (Spring Framework API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Import.html)

`@Import` указывает один или несколько классов компонентов для импорта: обычно `@Configuration`-классы, а также реализации `ImportSelector`, `ImportBeanDefinitionRegistrar` и `BeanRegistrar`.

**`ImportSelector`** — интерфейс для определения того, какие `@Configuration`-классы следует импортировать, на основе заданных критериев. Как правило, обрабатывается так же, как обычные `@Import`, но поддерживается и отложенное выполнение (через `DeferredImportSelector`) — выбор откладывается до обработки всех `@Configuration`-классов.

**`ImportBeanDefinitionRegistrar`** — интерфейс для регистрации дополнительных `BeanDefinition`-ов при обработке `@Configuration`-классов. Используется, когда нужен доступ на уровне определений бинов, а не экземпляров.

#### Ответ от Claude

**Три варианта @Import:**

```java
@Import({ConfigA.class, MySelector.class, MyRegistrar.class})
@Configuration
public class MainConfig { }
```

**Вариант 1: импорт @Configuration-класса**

Самый простой способ — подключить другой `@Configuration`-класс как модуль конфигурации. Все `@Bean`-методы из импортируемого класса становятся частью контекста:

```java
@Import(DatabaseConfig.class)
@Configuration
public class AppConfig { }
```

Применяется для модульной организации конфигурации: каждый модуль (web, data, security) — отдельный `@Configuration`-класс, а главный `AppConfig` импортирует нужные.

**Вариант 2: ImportSelector**

```java
public class MySelector implements ImportSelector {
    @Override
    public String[] selectImports(AnnotationMetadata importingClassMetadata) {
        // Можно читать аннотации на классе, который использует @Import
        boolean useFast = importingClassMetadata
            .isAnnotated(EnableFastMode.class.getName());
        return useFast
            ? new String[]{"com.example.FastConfig"}
            : new String[]{"com.example.DefaultConfig"};
    }
}
```

`selectImports()` возвращает массив полных имён классов (`@Configuration` или компонентов), которые Spring должен зарегистрировать. Это позволяет условно выбирать конфигурацию на основе аннотаций или окружения.

`DeferredImportSelector` — подвариант, у которого выбор откладывается до обработки всех `@Configuration`-классов текущей волны. Используется в Spring Boot Auto-Configuration для корректного порядка условных проверок.

**Вариант 3: ImportBeanDefinitionRegistrar**

```java
public class MyRegistrar implements ImportBeanDefinitionRegistrar {
    @Override
    public void registerBeanDefinitions(
            AnnotationMetadata importingClassMetadata,
            BeanDefinitionRegistry registry) {

        RootBeanDefinition beanDef = new RootBeanDefinition(MyService.class);
        registry.registerBeanDefinition("myService", beanDef);
    }
}
```

Предоставляет прямой доступ к `BeanDefinitionRegistry` — позволяет программно создавать и регистрировать `BeanDefinition`-объекты. Используется, когда нужны бины, которые невозможно описать через `@Configuration` (например, динамически генерируемые прокси-классы или бины со специфичными метаданными).

**Сравнение трёх вариантов:**

| Аспект | @Configuration | ImportSelector | ImportBeanDefinitionRegistrar |
|---|---|---|---|
| Что делает | Подключает готовый модуль конфигурации | Выбирает, какие классы импортировать | Напрямую регистрирует BeanDefinition |
| Уровень | Высокий (экземпляры бинов) | Средний (имена классов) | Низкий (BeanDefinition) |
| Когда | Модульная конфигурация | Условный выбор реализации | Динамическая/программная регистрация |
| Примеры в Spring | Любые `@Enable*`-конфигурации | `AsyncConfigurationSelector` | `AutoConfigurationPackages.Registrar` |

**Расхождений между источниками не выявлено.**

---

### Вопрос 59. Что такое SmartInitializingSingleton и метод afterSingletonsInstantiated()? Чем он отличается от @PostConstruct и от подписки на ContextRefreshedEvent, и зачем нужен именно этот интерфейс?

**Категория:** Spring · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [SmartInitializingSingleton (Spring Framework 6.1 API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/SmartInitializingSingleton.html)

`SmartInitializingSingleton` — колбэк-интерфейс, вызываемый в конце фазы предварительной инстанциации синглтонов при загрузке `BeanFactory`. Метод `afterSingletonsInstantiated()` вызывается сразу после того, как все обычные синглтон-бины уже созданы.

Ключевые характеристики:

> «Вызывается сразу в конце фазы предварительной инстанциации синглтонов, с гарантией того, что все обычные синглтон-бины уже созданы.»

Вызовы `ListableBeanFactory.getBeansOfType(Class)` внутри этого метода не провоцируют случайных побочных эффектов при начальной загрузке. Колбэк не вызывается для синглтонов с ленивой инициализацией, загружаемых по требованию после завершения загрузки BeanFactory, и не вызывается для бинов других скоупов.

#### Ответ от Claude

**Зачем нужен SmartInitializingSingleton**

`@PostConstruct` у конкретного бина вызывается в момент создания этого бина. Но что если бину нужно обратиться к другому бину, который ещё не создан? Порядок создания синглтонов не всегда предсказуем. `SmartInitializingSingleton` решает эту задачу: его метод вызывается гарантированно **после** того, как все синглтоны полностью инициализированы.

**Порядок в жизненном цикле контейнера:**

```
Для каждого бина:
  конструктор → DI → @PostConstruct → afterPropertiesSet → init-method

↓ Все синглтоны созданы

SmartInitializingSingleton.afterSingletonsInstantiated()  ← здесь

↓

ContextRefreshedEvent публикуется
```

**Сравнение трёх механизмов:**

| Механизм | Момент вызова | Гарантия наличия других бинов | Зависимость от контекста |
|---|---|---|---|
| `@PostConstruct` | При создании конкретного бина | Нет (другие могут быть не готовы) | Нет (только `beans`-пакет) |
| `SmartInitializingSingleton` | После создания ВСЕХ синглтонов | Да | Нет (только `beans`-пакет) |
| `ContextRefreshedEvent` | После полного refresh контекста | Да | Да (требует `context`-пакет) |

**Когда использовать SmartInitializingSingleton:**

```java
@Component
public class CacheWarmer implements SmartInitializingSingleton {

    @Autowired
    private List<CachingRepository> repositories; // все бины типа уже созданы

    @Override
    public void afterSingletonsInstantiated() {
        // Безопасно: все CachingRepository уже полностью инициализированы
        repositories.forEach(CachingRepository::warmUp);
    }
}
```

Если попробовать сделать то же самое в `@PostConstruct`, существует риск, что какой-то `CachingRepository` ещё не создан, особенно при сложных графах зависимостей.

**Преимущества перед ContextRefreshedEvent:**

1. Более лёгкая зависимость: `SmartInitializingSingleton` — в пакете `org.springframework.beans.factory`, `ApplicationListener` — в `org.springframework.context`. Первый работает даже в standalone `ListableBeanFactory` без полноценного `ApplicationContext`.
2. Не нужно реализовывать `ApplicationListener<ContextRefreshedEvent>` и проверять тип события.
3. Вызывается до публикации `ContextRefreshedEvent` — позволяет завершить инициализацию инфраструктуры до того, как приложение считается «запущенным».

**Встроенные реализации в Spring:** `AnnotationAwareAspectJAutoProxyCreator`, `CacheAspectSupport`, `ScheduledAnnotationBeanPostProcessor`, `EventListenerMethodProcessor` — все они используют `afterSingletonsInstantiated()` для завершения своей конфигурации.

**Расхождений между источниками не выявлено.**

---

### Вопрос 60. Что такое AOP pointcut expression? Разберите синтаксис designator-ов: execution, within, @annotation, @within, bean, args. Как комбинировать выражения операторами &&, || и !, и чем runtime-проверка args отличается от signature-проверки в execution?

**Категория:** Spring · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Declaring a Pointcut — Spring Framework Reference (AOP Pointcuts)](https://docs.spring.io/spring-framework/reference/core/aop/ataspectj/pointcuts.html)

Spring AOP поддерживает следующие pointcut-designator-ы AspectJ:

- **`execution`** — сопоставляет с выполнением метода (основной designator для Spring AOP). Синтаксис: `execution(модификаторы? тип-возврата объявляющий-тип? имя(параметры) throws?)`.
- **`within`** — ограничивает сопоставление точками соединения в типах из заданного пакета.
- **`@annotation`** — сопоставляет методы, у которых есть заданная аннотация.
- **`@within`** — сопоставляет методы, объявленные в типе, имеющем заданную аннотацию.
- **`args`** — сопоставляет, если аргументы метода в runtime являются экземплярами заданных типов.
- **`bean`** — специфичный для Spring designator; сопоставляет по имени бина (или wildcard-паттерну).

Рекомендация из документации: «в целях производительности следует включать в выражения как можно более специфичные designator-ы типа `kinded` (например, `execution`) в сочетании со scope-ограничениями».

#### Ответ от Claude

**Основные designator-ы:**

**`execution` — главный designator**

```
execution(модификаторы? возвращаемый-тип объявляющий-тип? имя-метода(параметры) throws?)
```

```java
execution(public * *(..))                       // любой public-метод
execution(* set*(..))                           // методы, начинающиеся с "set"
execution(* com.example.service.*.*(..))        // все методы в пакете service
execution(* com.example..*.*(..))              // пакет service и все подпакеты
execution(* com.example.OrderService.place(..)) // метод place() класса OrderService
```

**`within` — по классу/пакету**

```java
within(com.example.service.*)         // все методы в классах пакета service
within(com.example.service..*)        // пакет и все подпакеты
```

Отличие от `execution`: `within` проверяет, **в каком классе объявлен** метод; `execution` — полную сигнатуру метода.

**`@annotation` — по аннотации на методе**

```java
@annotation(org.springframework.transaction.annotation.Transactional)
// все методы, помеченные @Transactional
```

**`@within` — по аннотации на классе**

```java
@within(org.springframework.stereotype.Service)
// все методы в классах, помеченных @Service
```

Разница между `@annotation` и `@within`: первый ищет аннотацию непосредственно на методе, второй — на классе, объявляющем метод.

**`args` — проверка аргументов в runtime**

```java
args(java.io.Serializable)     // метод получает один аргумент типа Serializable в runtime
args(Long, ..)                 // первый аргумент Long, остальные — любые
```

Ключевое отличие от `execution`: `execution(* *(java.io.Serializable))` проверяет **сигнатуру** (тип параметра в объявлении метода), тогда как `args(java.io.Serializable)` проверяет **фактический тип объекта** в рантайме. Если метод объявлен с параметром `Object`, но передаётся `String`, `execution(* *(Object))` сработает, а `args(String)` — тоже сработает (потому что String — фактический тип), а `args(Object)` — сработает всегда.

**`bean` — Spring-специфичный designator**

```java
bean(userService)              // конкретный бин по имени
bean(*Service)                 // все бины с именем, оканчивающимся на "Service"
```

`bean` — единственный designator, специфичный для Spring AOP. В нативном AspectJ недоступен.

**Комбинирование выражений:**

```java
@Pointcut("execution(public * *(..)) && within(com.example.service.*)")
public void publicServiceMethod() {}

@Pointcut("@annotation(com.example.Auditable) || @within(com.example.Auditable)")
public void auditableOperation() {}

@Pointcut("execution(* *(..)) && !within(com.example.test.*)")
public void notInTest() {}
```

**Именованные pointcut-ы и переиспользование:**

```java
public class CommonPointcuts {
    @Pointcut("within(com.example.service..*)") public void inServiceLayer() {}
    @Pointcut("within(com.example.dao..*)") public void inDaoLayer() {}

    @Pointcut("inServiceLayer() || inDaoLayer()")
    public void inApplicationCore() {}
}

// Использование в аспекте:
@Before("com.example.CommonPointcuts.inServiceLayer()")
public void logServiceCall(JoinPoint jp) { ... }
```

**Рекомендации по производительности:**

Spring обрабатывает pointcut-ы в три стадии: статическая часть (проверка по классу/методу без выполнения), динамическая часть (проверка аргументов в runtime — для `args`, `@args`). Чем больше статической фильтрации, тем меньше runtime-накладных расходов. Поэтому `execution() && @annotation()` предпочтительнее одного только `@annotation()` для часто вызываемых методов.

**Расхождений между источниками не выявлено.**

---
