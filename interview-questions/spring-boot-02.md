# Spring Boot — часть 2 из 3

> Вопросы 21–40 (в части: 20). Всего в разделе: 50.
> Область знаний: [../theory/01-knowledge-areas/03-backend-ecosystem/14-spring-boot.md](../theory/01-knowledge-areas/03-backend-ecosystem/14-spring-boot.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](spring-boot-01.md) · **ч.2** · [ч.3](spring-boot-03.md)

---
### Вопрос 21. Чем @ConditionalOnMissingBean отличается от @ConditionalOnBean? Почему @ConditionalOnMissingBean опасно использовать в обычном @Configuration-классе приложения, а не в классе автоконфигурации?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Документация Spring Boot предупреждает: «Вы должны быть очень осторожны с порядком, в котором добавляются определения бинов, так как эти условия вычисляются на основе того, что уже было обработано. По этой причине мы рекомендуем использовать аннотации `@ConditionalOnBean` и `@ConditionalOnMissingBean` только на классах автоконфигурации (поскольку они гарантированно загружаются после того, как все пользовательские определения бинов уже добавлены).»

#### Ответ от Claude

**Базовое отличие**

| Аннотация | Условие срабатывания |
|---|---|
| `@ConditionalOnBean` | Бин **присутствует** в `ApplicationContext` |
| `@ConditionalOnMissingBean` | Бин **отсутствует** в `ApplicationContext` |

Обе аннотации могут принимать параметры: `value` (тип бина), `name` (имя бина), `annotation` (присутствие аннотации на бине) и другие.

**Типичный use case `@ConditionalOnMissingBean` в автоконфигурации**

```java
@AutoConfiguration
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean(DataSource.class)
    public DataSource defaultDataSource() {
        // создаётся только если пользователь не объявил свой DataSource
        return new EmbeddedDatabaseBuilder().build();
    }
}
```

Паттерн: «дай дефолт, если пользователь не переопределил».

**Почему `@ConditionalOnMissingBean` опасен в пользовательском `@Configuration`**

Ключевая проблема — **недетерминированный порядок обработки** пользовательских `@Configuration`-классов.

1. **Нет гарантии порядка.** Пользовательские `@Configuration`-классы обрабатываются на основе результатов `@ComponentScan`. Порядок сканирования файловой системы не гарантирован. Два класса в разных пакетах могут загружаться в любом порядке.

2. **Условие вычисляется «здесь и сейчас».** `@ConditionalOnMissingBean` проверяет только те бины, которые уже зарегистрированы в контексте на момент обработки данного класса. Если бин `MyService` будет зарегистрирован позже (в другом `@Configuration`-классе, который ещё не обработан), условие ошибочно вернёт `true` — и будет создан «лишний» бин.

3. **Результат: дублирование бинов или неожиданное поведение.** В зависимости от classpath, порядка JAR, изменений в структуре пакетов поведение может меняться от запуска к запуску или между средами.

**Почему в автоконфигурации это безопасно**

Автоконфигурационные классы (из `AutoConfiguration.imports`) загружаются через `DeferredImportSelector` — **после** того, как все пользовательские `@Configuration`-классы уже обработаны. Это гарантирует, что при вычислении условия `@ConditionalOnMissingBean` в контексте уже присутствуют все пользовательские бины. Порядок самих автоконфигураций управляется атрибутами `before`/`after` аннотации `@AutoConfiguration`.

**Итог**

```
Пользовательские @Configuration → обрабатываются в непредсказуемом порядке
        ↓
Автоконфигурации (@AutoConfiguration) → гарантированно ПОСЛЕ всех пользовательских
```

Поэтому официальная рекомендация: `@ConditionalOnBean` и `@ConditionalOnMissingBean` — только в классах автоконфигурации. В пользовательских `@Configuration`-классах для управления созданием бинов следует использовать явные зависимости (`@DependsOn`) или стандартные механизмы Spring (`@Primary`, `@Qualifier`).
### Вопрос 22. В каком порядке Spring Boot обрабатывает источники конфигурации? Перечислите хотя бы 5 уровней приоритета (от наименьшего к наибольшему) и объясните, как переменная окружения может перезаписать значение из application.yml.

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)

Spring Boot использует строго определённый порядок `PropertySource`, позволяющий разумно переопределять значения: источник с более высоким приоритетом перекрывает источник с более низким. Полный список из 15 уровней (от наименьшего к наибольшему приоритету):

1. Свойства по умолчанию (`SpringApplication.setDefaultProperties`)
2. Аннотации `@PropertySource` на `@Configuration`-классах
3. Данные конфигурации (например, файлы `application.properties` / `application.yml`)
4. `RandomValuePropertySource` (свойства вида `random.*`)
5. Переменные окружения ОС
6. Системные свойства Java (`System.getProperties()`)
7. JNDI-атрибуты из `java:comp/env`
8. Параметры инициализации `ServletContext`
9. Параметры инициализации `ServletConfig`
10. Свойства из `SPRING_APPLICATION_JSON`
11. Аргументы командной строки
12. Атрибут `properties` в тестах (`@SpringBootTest`)
13. `@DynamicPropertySource` в тестах
14. `@TestPropertySource` в тестах
15. Глобальные настройки Devtools (`$HOME/.config/spring-boot`)

Переменная окружения (уровень 5) перезаписывает `application.yml` (уровень 3), поскольку имеет более высокий приоритет. Spring Boot использует «relaxed binding»: `MY_SERVICE_ENABLED=true` соответствует свойству `my.service.enabled`.

#### Ответ от Claude

**Порядок источников конфигурации (от наименьшего к наибольшему приоритету)**

Spring Boot выстраивает `Environment` из набора `PropertySource`, каждый последующий может перекрывать предыдущий. Согласно актуальной документации (Spring Boot 3.x), полный список:

| # | Источник | Пример |
|---|----------|--------|
| 1 | Свойства по умолчанию | `SpringApplication.setDefaultProperties(Map)` |
| 2 | `@PropertySource` на `@Configuration`-классах | `@PropertySource("classpath:extra.properties")` |
| 3 | Файлы конфигурации (config data) | `application.yml`, `application.properties`, profile-файлы |
| 4 | `RandomValuePropertySource` | `random.int`, `random.uuid` |
| 5 | Переменные окружения ОС | `SPRING_DATASOURCE_URL=jdbc:...` |
| 6 | Системные свойства JVM | `-Dserver.port=9090` |
| 7 | JNDI-атрибуты `java:comp/env` | типично для WAR-деплоя |
| 8 | Параметры инициализации `ServletContext` | `web.xml` init-params |
| 9 | Параметры инициализации `ServletConfig` | servlet init-params |
| 10 | `SPRING_APPLICATION_JSON` | JSON в переменной окружения или системном свойстве |
| 11 | Аргументы командной строки | `--server.port=8081` |
| 12 | `properties` в `@SpringBootTest` | тестовая среда |
| 13 | `@DynamicPropertySource` в тестах | динамические тест-свойства |
| 14 | `@TestPropertySource` в тестах | статические тест-свойства |
| 15 | Настройки Devtools | `$HOME/.config/spring-boot/spring-boot-devtools.properties` |

**Как переменная окружения перезаписывает application.yml**

`application.yml` находится на уровне 3, переменные окружения ОС — на уровне 5. Так как 5 > 3, переменная окружения всегда выигрывает.

```yaml
# application.yml
my:
  service:
    enabled: false
    remote-address: 192.168.1.1
```

```bash
export MY_SERVICE_ENABLED=true
export MY_SERVICE_REMOTE_ADDRESS=10.0.0.1
```

При старте приложения будут использованы значения `true` и `10.0.0.1`.

**Relaxed binding** позволяет Spring Boot автоматически преобразовывать имена переменных окружения (UPPER_SNAKE_CASE) в имена свойств (kebab-case / camelCase):

- `MY_SERVICE_ENABLED` → `my.service.enabled`
- `SPRING_DATASOURCE_URL` → `spring.datasource.url`

**Важные детали:**

- Профильные файлы (`application-prod.yml`) перекрывают базовый `application.yml`, но оба находятся на уровне 3 — профильный просто обрабатывается позже внутри этого уровня.
- `@PropertySource` (уровень 2) не поддерживает YAML из коробки — только `.properties`-файлы; для YAML нужен кастомный `PropertySourceFactory`.
- Аргументы командной строки (уровень 11) имеют наивысший приоритет среди «рантаймовых» источников, что удобно для временного переопределения без изменения конфигурационных файлов.
- Чтобы отключить переопределение из командной строки: `SpringApplication.setAddCommandLineProperties(false)`.

---

### Вопрос 23. Что такое Spring Boot Starter? Что находится внутри стартера — только pom.xml с зависимостями или ещё что-то? Как создать собственный стартер для переиспользования между командами?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Spring Boot starter — это паттерн «композиция двух модулей»:

1. **Autoconfigure-модуль** (`acme-spring-boot`) — содержит весь автоконфигурационный код, `@ConfigurationProperties`, опциональные зависимости библиотеки.
2. **Starter-модуль** (`acme-spring-boot-starter`) — «пустой jar», который тянет autoconfigure-модуль, базовый `spring-boot-starter` и все нужные транзитивные зависимости.

Авто-конфигурация регистрируется в файле:
`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` — по одному классу в строке. Устаревший способ (до Spring Boot 2.7) — через `META-INF/spring.factories`.

Для улучшения времени старта используется annotation processor `spring-boot-autoconfigure-processor`, генерирующий `META-INF/spring-autoconfigure-metadata.properties`, который позволяет отсеивать неподходящие конфигурации ещё до их загрузки.

#### Ответ от Claude

**Что такое Spring Boot Starter**

Starter — это удобный дескриптор зависимостей, который объединяет в себе всё необходимое для интеграции некоторой технологии (библиотеки, инфраструктуры) в Spring Boot-приложение. Например, `spring-boot-starter-data-jpa` добавляет Hibernate, Spring Data JPA и пул соединений одним объявлением.

**Что находится внутри стартера**

Стартер — это НЕ просто pom.xml. Полноценный стартер состоит из двух модулей:

**Модуль 1 — Autoconfigure (`acme-spring-boot`)**

Содержит реальный код:
- Классы `@AutoConfiguration` (или `@Configuration` в старых версиях)
- `@ConfigurationProperties`-классы для описания настраиваемых свойств
- Conditional-аннотации (`@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty` и др.)
- Дополнительные бины, кастомайзеры, фабрики
- Регистрационный файл: `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
- (опционально) `META-INF/spring-autoconfigure-metadata.properties` — генерируется annotation processor'ом для ускорения старта

**Модуль 2 — Starter (`acme-spring-boot-starter`)**

По сути пустой jar (`<packaging>jar</packaging>` без исходников), содержащий только `pom.xml` с зависимостями:
- Зависимость на autoconfigure-модуль
- Зависимость на `spring-boot-starter`
- Все транзитивные зависимости целевой библиотеки

Если библиотека простая и не нужно разделять два модуля — допустимо объединить всё в один модуль `acme-spring-boot-starter`.

**Как создать собственный стартер**

**Шаг 1. Autoconfigure-модуль**

```java
// src/main/java/com/acme/autoconfigure/AcmeProperties.java
@ConfigurationProperties(prefix = "acme")
public class AcmeProperties {
    private boolean enabled = true;
    private String endpoint = "https://api.acme.com";
    // getters/setters
}

// src/main/java/com/acme/autoconfigure/AcmeAutoConfiguration.java
@AutoConfiguration
@EnableConfigurationProperties(AcmeProperties.class)
@ConditionalOnClass(AcmeClient.class)
@ConditionalOnProperty(prefix = "acme", name = "enabled", havingValue = "true", matchIfMissing = true)
public class AcmeAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public AcmeClient acmeClient(AcmeProperties properties) {
        return new AcmeClient(properties.getEndpoint());
    }
}
```

**Шаг 2. Регистрация автоконфигурации**

Для Spring Boot 2.7+:
```
# src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.acme.autoconfigure.AcmeAutoConfiguration
```

Для Spring Boot до 2.7 (устаревший способ, поддерживается для обратной совместимости):
```properties
# src/main/resources/META-INF/spring.factories
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.acme.autoconfigure.AcmeAutoConfiguration
```

**Шаг 3. pom.xml autoconfigure-модуля**

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-autoconfigure</artifactId>
        <optional>true</optional>
    </dependency>
    <!-- Зависимость на саму библиотеку — тоже optional -->
    <dependency>
        <groupId>com.acme</groupId>
        <artifactId>acme-client</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
<!-- Annotation processor для метаданных -->
```

**Шаг 4. Starter-модуль (pom.xml)**

```xml
<dependencies>
    <dependency>
        <groupId>com.acme</groupId>
        <artifactId>acme-spring-boot</artifactId> <!-- autoconfigure модуль -->
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
    <!-- Обязательные зависимости библиотеки (не optional) -->
    <dependency>
        <groupId>com.acme</groupId>
        <artifactId>acme-client</artifactId>
    </dependency>
</dependencies>
```

**Ключевые правила при создании стартера:**

- Называть модули `<name>-spring-boot` и `<name>-spring-boot-starter`, **не** начинать с `spring-boot-` (это пространство имён Spring)
- Использовать `optional = true` для зависимостей в autoconfigure-модуле, чтобы не навязывать их всем потребителям
- Добавлять `@ConditionalOnMissingBean` на все бины — это позволяет потребителям переопределять их
- Использовать уникальный префикс для `@ConfigurationProperties` (избегать `spring`, `server`, `management`)
- Упорядочивать автоконфигурации через `@AutoConfiguration(before=..., after=...)`

---

### Вопрос 24. Как Spring Boot встраивает сервер (Tomcat/Jetty/Undertow)? Чем TomcatServletWebServerFactory отличается от обычного WAR-деплоя? Как переключиться с Tomcat на Undertow и что при этом происходит с автоконфигурацией?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Embedded Web Servers :: Spring Boot](https://docs.spring.io/spring-boot/how-to/webserver.html)

Spring Boot по умолчанию встраивает Tomcat через `spring-boot-starter-web`, который транзитивно включает `spring-boot-starter-tomcat`. Чтобы переключиться на другой сервер, нужно исключить дефолтную зависимость и добавить нужную:

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
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

Автоконфигурация определяет наличие сервера по classpath: вместо `TomcatServletWebServerFactory` будет инстанциирован `UndertowServletWebServerFactory`. Каждый сервер имеет свой namespace свойств: `server.tomcat.*`, `server.undertow.*`, `server.jetty.*`.

#### Ответ от Claude

**Как Spring Boot встраивает сервер**

Spring Boot запускает сервер прямо внутри JVM-процесса приложения — это называется embedded (встроенным) сервером. Механизм работает следующим образом:

1. `spring-boot-starter-web` тянет `spring-boot-starter-tomcat` (или Jetty/Undertow).
2. `EmbeddedWebServerFactoryCustomizerAutoConfiguration` (и `ServletWebServerFactoryAutoConfiguration`) обнаруживают на classpath классы Tomcat (`org.apache.catalina.startup.Tomcat`) через `@ConditionalOnClass`.
3. Создаётся бин `TomcatServletWebServerFactory`.
4. В момент обновления `ApplicationContext` вызывается `factory.getWebServer(...)` — возвращается `TomcatWebServer`, который запускается (`.start()`).
5. Сервер начинает принимать входящие соединения.

Весь процесс управляется через цепочку: `SpringApplication` → `refresh()` → `onRefresh()` → `createWebServer()`.

**TomcatServletWebServerFactory vs обычный WAR-деплой**

| Аспект | TomcatServletWebServerFactory (embedded) | Традиционный WAR-деплой |
|--------|------------------------------------------|--------------------------|
| Упаковка | Исполняемый JAR (`java -jar app.jar`) | WAR-файл, развёртывается в контейнере |
| Жизненный цикл сервера | Управляется самим приложением | Управляется внешним контейнером |
| Конфигурация | `application.properties` / Java-код | `server.xml`, `context.xml`, `web.xml` |
| `SpringBootServletInitializer` | Не нужен | Нужен (реализует `WebApplicationInitializer` для Servlet 3.0+) |
| Зависимость Tomcat | `compile` (встроена в JAR) | `provided` (предоставляется контейнером) |
| Инициализация контекста | `TomcatServletWebServerFactory.getWebServer()` | Контейнер вызывает `SpringBootServletInitializer.configure()` |
| Поддержка Reactive (WebFlux) | Да (через `TomcatReactiveWebServerFactory`) | Нет — WAR не поддерживается для реактивных приложений |

**Как переключиться с Tomcat на Undertow**

Maven:
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
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

Gradle:
```gradle
configurations {
    implementation.exclude group: 'org.springframework.boot', module: 'spring-boot-starter-tomcat'
}
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-undertow'
}
```

**Что происходит с автоконфигурацией при переключении**

1. `@ConditionalOnClass(Tomcat.class)` на `TomcatServletWebServerFactory` — перестаёт выполняться (Tomcat убран с classpath).
2. `@ConditionalOnClass(Undertow.class, SslClientAuthMode.class)` — начинает выполняться.
3. Spring Boot автоматически создаёт `UndertowServletWebServerFactory` вместо `TomcatServletWebServerFactory`.
4. Настройки `server.tomcat.*` игнорируются; вместо них применяются `server.undertow.*`.
5. Кастомайзеры через `WebServerFactoryCustomizer<UndertowServletWebServerFactory>` начинают работать.
6. Код приложения (контроллеры, фильтры, сервлеты) не требует изменений — абстракция `WebServer` / `WebServerFactory` скрывает реализацию.

**Таблица соответствия фабрик по серверу:**

| Сервер | Servlet-стек | Reactive-стек |
|--------|--------------|---------------|
| Tomcat | `TomcatServletWebServerFactory` | `TomcatReactiveWebServerFactory` |
| Jetty | `JettyServletWebServerFactory` | `JettyReactiveWebServerFactory` |
| Undertow | `UndertowServletWebServerFactory` | `UndertowReactiveWebServerFactory` |
| Reactor Netty | — | `NettyReactiveWebServerFactory` |

**Programmatic кастомизация Undertow:**
```java
@Bean
public WebServerFactoryCustomizer<UndertowServletWebServerFactory> undertowCustomizer() {
    return factory -> {
        factory.addBuilderCustomizers(builder -> builder.setIoThreads(4));
        factory.setPort(8080);
    };
}
```
### Вопрос 25. Чем @ConfigurationProperties лучше @Value для группы связанных настроек? Что такое relaxed binding и как он позволяет писать my-server.max-connections в yml и получать поле maxConnections в Java-классе?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration :: Spring Boot (docs.spring.io)](https://docs.spring.io/spring-boot/docs/2.1.7.RELEASE/reference/html/boot-features-external-config.html#boot-features-external-config-typesafe-configuration-properties)

Документация Spring Boot содержит явную таблицу сравнения возможностей двух аннотаций:

| Возможность | @ConfigurationProperties | @Value |
|---|---|---|
| Relaxed binding | Да | Нет |
| Поддержка метаданных (IDE) | Да | Нет |
| Вычисление SpEL-выражений | Нет | Да |

`@ConfigurationProperties` позволяет группировать связанные свойства в типобезопасный POJO с иерархической структурой, поддерживает проверку через JSR-303 и генерирует метаданные для автодополнения в IDE. `@Value` подходит только для точечного внедрения одного свойства или когда нужно вычисление SpEL-выражения.

Relaxed binding — это механизм гибкого сопоставления имён свойств окружения с полями Java-класса. Для класса с полем `firstName` (под префиксом `acme.my-project.person`) допустимы все следующие варианты написания ключа в конфигурации:

- `acme.my-project.person.first-name` — kebab-case (рекомендуется для `.properties` и `.yml`)
- `acme.myProject.person.firstName` — camelCase
- `acme.my_project.person.first_name` — underscore-нотация
- `ACME_MYPROJECT_PERSON_FIRSTNAME` — верхний регистр с подчёркиванием (для переменных окружения)

Правила по источнику свойства:

| Источник | Простые свойства | Списки |
|---|---|---|
| `.properties`-файлы | camelCase, kebab-case, underscore | `[index]` или через запятую |
| YAML-файлы | camelCase, kebab-case, underscore | Стандартный YAML-список или через запятую |
| Переменные окружения | UPPER_CASE с `_` как разделитель | Числа в окружении `_` |
| Системные свойства | camelCase, kebab-case, underscore | `[index]` или через запятую |

Важно: значение `prefix` в аннотации `@ConfigurationProperties` должно всегда быть в kebab-case.

#### Ответ от Claude

**Чем @ConfigurationProperties лучше @Value для группы настроек**

`@Value("${property}")` внедряет одно свойство прямо в поле или параметр. При наличии 10–15 связанных настроек (например, параметры пула соединений) это ведёт к рассеиванию аннотаций по всему классу, отсутствию структуры и сложности с рефакторингом. `@ConfigurationProperties` собирает все настройки в один POJO-класс с префиксом, предоставляя пять ключевых преимуществ перед `@Value`:

1. **Типобезопасность и иерархия.** Вложенные объекты, списки, Map — всё нативно поддерживается через вложенные Java-классы.
2. **Relaxed binding.** Нет необходимости в точном совпадении имён (подробнее ниже).
3. **Валидация JSR-303.** Достаточно добавить `@Validated` на класс и аннотации ограничений на поля.
4. **Метаданные для IDE.** `spring-boot-configuration-processor` генерирует `META-INF/spring-configuration-metadata.json`, благодаря чему IntelliJ IDEA и VS Code показывают автодополнение в `application.yml`.
5. **Поддержка конструкторного связывания** (с Java 16+ record или с `@ConstructorBinding`) — позволяет создавать immutable-конфигурацию.

Именно эти возможности делают `@ConfigurationProperties` предпочтительным выбором для всех групп связанных настроек. `@Value` остаётся полезным только для одиночных свойств или SpEL-выражений (например, `@Value("#{${timeout} * 1000}")`).

**Что такое relaxed binding и как он работает**

Relaxed binding — это встроенный механизм Spring Boot, который при связывании Environment-свойств с `@ConfigurationProperties`-бинами применяет нормализацию имён. Все четыре варианта записи приводятся к одной каноническй форме (lowercase без разделителей), поэтому Spring может сопоставить их с camelCase-полем Java.

Пример. Класс `ServerProperties` с префиксом `my-server`:

```java
@ConfigurationProperties(prefix = "my-server")
public class ServerProperties {
    private int maxConnections;

    public int getMaxConnections() { return maxConnections; }
    public void setMaxConnections(int maxConnections) { this.maxConnections = maxConnections; }
}
```

В `application.yml` можно писать любой из вариантов:

```yaml
my-server:
  max-connections: 100   # kebab-case — рекомендуется
  # maxConnections: 100  # camelCase — тоже сработает
  # max_connections: 100 # underscore — тоже сработает
```

Через переменную окружения: `MY_SERVER_MAX_CONNECTIONS=100`.

Все четыре формы однозначно привязываются к полю `maxConnections`.

**Важные ограничения:**
- `@Value` relaxed binding не поддерживает — при использовании `@Value("${my-server.maxConnections}")` нужно точно угадать, в каком формате написан ключ.
- Префикс в `@ConfigurationProperties` обязан быть в kebab-case (`my-server`, а не `myServer`).
- Для переменных окружения точки и дефисы заменяются на `_`, а имя переводится в UPPER_CASE.

**Регистрация бина.** Начиная со Spring Boot 2.2, достаточно добавить `@ConfigurationPropertiesScan` или `@EnableConfigurationProperties(ServerProperties.class)` на класс конфигурации. С Spring Boot 2.2+ и аннотацией `@ConfigurationProperties` вместе с `@Component` регистрация происходит автоматически при включённом сканировании.

---

### Вопрос 26. Как работает @ConfigurationProperties с валидацией (JSR-303)? Что нужно добавить в класс и в зависимости, чтобы при старте приложения упасть с понятной ошибкой, если обязательное свойство не задано или не проходит ограничение?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration :: Spring Boot (docs.spring.io)](https://docs.spring.io/spring-boot/docs/2.1.7.RELEASE/reference/html/boot-features-external-config.html#boot-features-external-config-typesafe-configuration-properties)

Spring Boot пытается валидировать классы `@ConfigurationProperties` всякий раз, когда они аннотированы Spring-аннотацией `@Validated`. Чтобы это работало, нужно обеспечить наличие JSR-303-совместимой реализации в classpath, а затем добавить аннотации ограничений прямо на поля:

```java
@ConfigurationProperties(prefix = "acme")
@Validated
public class AcmeProperties {

    @NotNull
    private InetAddress remoteAddress;

    @Valid
    private final Security security = new Security();

    public static class Security {
        @NotEmpty
        public String username;
        // геттеры и сеттеры
    }
}
```

Чтобы валидация всегда срабатывала для вложенных свойств (даже если в конфигурации нет ни одного вложенного ключа), соответствующее поле должно быть аннотировано `@Valid`. Также можно добавить кастомный `Spring Validator`, создав статический `@Bean`-метод с именем `configurationPropertiesValidator`. Метод должен быть статическим, так как валидатор создаётся очень рано в жизненном цикле приложения.

#### Ответ от Claude

**Что нужно добавить в зависимости**

В Maven (`pom.xml`):

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

В Gradle (`build.gradle`):

```groovy
implementation 'org.springframework.boot:spring-boot-starter-validation'
```

Этот стартер транзитивно подключает `hibernate-validator` — эталонную реализацию Jakarta Bean Validation (JSR-380, преемник JSR-303).

**Что нужно добавить в класс**

1. Аннотация `@Validated` на уровне класса — сообщает Spring, что данный бин должен быть провалидирован при создании.
2. Аннотации ограничений из пакета `jakarta.validation.constraints` на полях.

Минимальный пример:

```java
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@ConfigurationProperties(prefix = "my-server")
@Validated
public class ServerProperties {

    @NotBlank
    private String host;           // обязательная строка

    @NotNull
    @Min(1)
    private Integer maxConnections; // обязательное число >= 1

    // геттеры и сеттеры
}
```

**Как это работает при старте**

1. При запуске приложения Spring Boot создаёт бин `ServerProperties` и связывает с ним значения из `application.yml`.
2. После связывания, поскольку класс помечен `@Validated`, запускается цикл валидации через Hibernate Validator.
3. Если ограничение нарушено (поле `host` не задано, `maxConnections` равен 0 или отсутствует), Spring Boot бросает `BindValidationException`, оборачивает её в `BeanCreationException` и останавливает запуск с читаемым сообщением в лог:

```
***************************
APPLICATION FAILED TO START
***************************

Description:

Binding to target org.springframework.boot.context.properties.bind.BindException:
Failed to bind properties under 'my-server' to ...ServerProperties failed:

    Property: my-server.host
    Value: ""
    Reason: must not be blank

    Property: my-server.max-connections
    Value: null
    Reason: must not be null

Action:

Update your application's configuration
```

**Валидация вложенных объектов**

Для каскадной проверки вложенных объектов недостаточно просто добавить аннотации на поля вложенного класса — нужно пометить само поле-ссылку аннотацией `@Valid`:

```java
@ConfigurationProperties(prefix = "acme")
@Validated
public class AcmeProperties {

    @Valid                          // каскад валидации вглубь
    private final Security security = new Security();

    public static class Security {
        @NotEmpty
        private String username;    // будет проверен
        // ...
    }
}
```

Без `@Valid` поле `username` проверено не будет, даже если `@Validated` стоит на внешнем классе.

**Отличие @Validated от @Valid**

- `@Validated` (Spring) — ставится на класс `@ConfigurationProperties`; инициирует механизм валидации всего бина при его создании.
- `@Valid` (Jakarta) — ставится на поле вложенного объекта; включает каскадную валидацию внутрь.

**Кастомный валидатор**

Если стандартных ограничений недостаточно, можно добавить `configurationPropertiesValidator`-бин:

```java
@Bean
public static Validator configurationPropertiesValidator() {
    return new MyCustomValidator();
}
```

Метод обязательно должен быть `static`: валидатор конфигурационных свойств создаётся очень рано (до инициализации самого `@Configuration`-класса), и нестатический метод приведёт к проблемам раннего инстанцирования.

---

### Вопрос 27. Как управляется порядок применения классов автоконфигурации? Для чего служат @AutoConfigureBefore, @AutoConfigureAfter и @AutoConfigureOrder? Приведите пример, когда порядок критичен.

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot (docs.spring.io)](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Spring Boot предоставляет аннотации для управления порядком применения автоконфигураций. Можно использовать атрибуты `before`, `beforeName`, `after`, `afterName` прямо на аннотации `@AutoConfiguration` или отдельные аннотации `@AutoConfigureBefore` и `@AutoConfigureAfter`. Если нужно упорядочить автоконфигурации, не имеющие прямой зависимости друг от друга, используется `@AutoConfigureOrder` — семантически эквивалентный обычному `@Order`, но предназначенный исключительно для автоконфигурационных классов.

**Критически важное замечание документации:** порядок применения классов автоконфигурации влияет только на порядок, в котором определяются бины. Порядок их последующего создания не зависит от этих аннотаций и определяется зависимостями каждого бина и отношениями `@DependsOn`.

Практический пример:

```java
@AutoConfiguration
@AutoConfigureAfter(WebMvcAutoConfiguration.class)
public class CustomWebAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    CustomWebFilter customWebFilter() {
        return new CustomWebFilter();
    }
}
```

#### Ответ от Claude

**Механизм упорядочивания автоконфигураций**

Spring Boot загружает классы автоконфигурации из файла `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (до Spring Boot 2.7 — из `META-INF/spring.factories`). Порядок их обработки управляется тремя специализированными аннотациями.

**@AutoConfigureAfter**

Указывает, что данная автоконфигурация должна быть обработана после указанных классов. Используется, когда конфигурация зависит от бинов, определённых в другой автоконфигурации.

```java
@AutoConfiguration
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
public class JpaAutoConfiguration {

    @Bean
    @ConditionalOnBean(DataSource.class)   // сработает только если DataSource уже определён
    public EntityManagerFactory entityManagerFactory(DataSource ds) {
        // ...
    }
}
```

**@AutoConfigureBefore**

Указывает, что данная автоконфигурация должна быть обработана до указанных классов. Применяется, когда нужно подготовить инфраструктуру, которую другие конфигурации рассчитывают найти готовой.

```java
@AutoConfiguration
@AutoConfigureBefore(DataSourceAutoConfiguration.class)
public class CustomPropertySourceAutoConfiguration {
    // Регистрирует дополнительный PropertySource до того,
    // как DataSourceAutoConfiguration начнёт читать свойства
}
```

Обе аннотации имеют атрибуты `value` (массив Class) и `name` (массив String). Атрибут `name` предпочтителен в meta-аннотациях, так как не требует загрузки байткода целевого класса.

**@AutoConfigureOrder**

Аналог `@Order` для автоконфигурационных классов. Применяется, когда нужно установить относительный порядок между конфигурациями, не имеющими прямых зависимостей. Меньшее значение = более высокий приоритет. Не влияет на обычные `@Configuration`-классы.

```java
@AutoConfiguration
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
public class EarlyInfrastructureAutoConfiguration {
    // Будет обработана одной из первых среди автоконфигураций
}
```

**Критическое разграничение: порядок определения vs порядок создания бинов**

Это самая важная тонкость, которую необходимо понимать: аннотации `@AutoConfigureBefore`, `@AutoConfigureAfter` и `@AutoConfigureOrder` управляют только порядком регистрации определений бинов (bean definitions), но не порядком их инстанцирования. Фактический порядок создания объектов определяется:
- граф зависимостей (constructor injection, setter injection);
- явными аннотациями `@DependsOn` на бинах.

Это означает: если класс `B` внедряет `DataSource` в конструктор, Spring создаст `DataSource` раньше `B` независимо от того, в каком порядке были обработаны конфигурационные классы.

**Пример, когда порядок критичен**

Рассмотрим сценарий с `@ConditionalOnBean`. Если `SecurityAutoConfiguration` использует `@ConditionalOnBean(DataSource.class)`, она должна быть обработана после `DataSourceAutoConfiguration` — иначе на момент проверки условия бин `DataSource` ещё не зарегистрирован, и условие не выполнится:

```java
// Без @AutoConfigureAfter бин DataSource может быть ещё не определён
// при проверке @ConditionalOnBean — условие даст false
@AutoConfiguration
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
public class SecurityAutoConfiguration {

    @Bean
    @ConditionalOnBean(DataSource.class)
    public SecurityManager securityManager(DataSource dataSource) {
        return new JdbcSecurityManager(dataSource);
    }
}
```

Другой критичный случай — регистрация кастомного `PropertySource` до того, как другие автоконфигурации начнут читать свойства. Если `VaultAutoConfiguration` должна загрузить секреты из HashiCorp Vault и сделать их доступными как свойства, она обязана завершить работу до `DataSourceAutoConfiguration`:

```java
@AutoConfiguration
@AutoConfigureBefore({DataSourceAutoConfiguration.class,
                       DataSourceTransactionManagerAutoConfiguration.class})
public class VaultAutoConfiguration {
    // Загружает секреты (пароль БД) в Environment
    // до того, как DataSourceAutoConfiguration попытается создать DataSource
}
```

**Современная форма записи (Spring Boot 2.7+)**

Начиная с Spring Boot 2.7, атрибуты `before`/`after` можно указывать прямо на `@AutoConfiguration`:

```java
@AutoConfiguration(after = DataSourceAutoConfiguration.class)
public class JpaAutoConfiguration { ... }
```

Это семантически эквивалентно использованию `@AutoConfigureAfter`, но более лаконично.

---
### Вопрос 28. Профили Spring: чем @Profile на бине отличается от именования файлов application-{profile}.yml? Как активировать несколько профилей одновременно и что произойдёт, если одно и то же свойство задано и в application.yml, и в application-prod.yml?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Profiles :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/profiles.html)

**@Profile на бине** применяется к классам `@Component`, `@Configuration` или `@ConfigurationProperties` и контролирует, какие бины будут инстанциированы в контексте Spring при активном профиле:

```java
@Configuration(proxyBeanMethods = false)
@Profile("production")
public class ProductionConfiguration {
    // загружается только при активном профиле "production"
}
```

**Файлы application-{profile}.yml** содержат значения свойств, специфичных для окружения, и загружаются автоматически при активации соответствующего профиля. Это механизм внешней конфигурации, а не управления бинами.

**Активация нескольких профилей** — через `spring.profiles.active`:

```yaml
spring:
  profiles:
    active: "dev,hsqldb"
```

Или через командную строку: `--spring.profiles.active=dev,hsqldb`.

При добавлении профилей поверх существующих используется `spring.profiles.include`.

**Приоритет свойств:** profile-specific файлы всегда переопределяют non-specific файлы на том же уровне. Если одно свойство задано в `application.yml` и `application-prod.yml`, при активном профиле `prod` побеждает значение из `application-prod.yml`.

#### Ответ от Claude

**Разница между @Profile на бине и application-{profile}.yml**

Это два разных механизма, действующих на разных уровнях:

| Механизм | Что контролирует | Уровень |
|---|---|---|
| `@Profile` | Создание и регистрацию бинов в контексте | Код (bean instantiation) |
| `application-{profile}.yml` | Значения конфигурационных свойств | Конфигурация (property values) |

`@Profile` — это условная аннотация, которая говорит Spring: «создай этот бин только если активен такой-то профиль». Применяется к `@Component`, `@Configuration`, `@Bean`-методам, `@ConfigurationProperties`:

```java
@Configuration
@Profile("production")
public class ProductionDataSourceConfig {
    @Bean
    public DataSource dataSource() { ... }
}

@Configuration
@Profile("!production")  // все профили, кроме production
public class DevDataSourceConfig {
    @Bean
    public DataSource dataSource() { ... }
}
```

Можно использовать операторы `!` (not), `&` (and), `|` (or) внутри строки профиля.

`application-{profile}.yml` — это файл с переопределёнными значениями свойств. Не создаёт/удаляет бины, только подменяет значения:

```yaml
# application-prod.yml
spring:
  datasource:
    url: jdbc:postgresql://prod-host:5432/db
server:
  port: 8443
```

**Как активировать несколько профилей**

1. Через `spring.profiles.active` (основной способ):
```properties
spring.profiles.active=dev,hsqldb
```
```bash
java -jar app.jar --spring.profiles.active=dev,hsqldb
```

2. Через `spring.profiles.include` — добавляет профили поверх уже активных, не заменяя их. Полезно для составных конфигураций:
```yaml
spring:
  profiles:
    include:
      - "common"
      - "logging-json"
```

3. Через Profile Groups (Spring Boot 2.4+) — логическое объединение нескольких профилей под одним именем:
```yaml
spring:
  profiles:
    group:
      production:
        - "proddb"
        - "prodmq"
        - "prodlogging"
```
Теперь `--spring.profiles.active=production` активирует сразу три профиля.

4. Программно: `SpringApplication.setAdditionalProfiles("dev", "hsqldb")`.

**Что произойдёт, если свойство задано и в application.yml, и в application-prod.yml**

При активном профиле `prod` значение из `application-prod.yml` **переопределит** значение из `application.yml`. Это часть общего порядка приоритетов PropertySource:

```
(низший приоритет) application.yml (внутри JAR)
                   application-prod.yml (внутри JAR)  ← победит
                   application.yml (внешний, рядом с JAR)
                   application-prod.yml (внешний)      ← наивысший среди файлов
(высший приоритет) аргументы командной строки
```

Пример:
```yaml
# application.yml
server.port: 8080
app.name: MyApp

# application-prod.yml
server.port: 443
```

При активном профиле `prod`: `server.port=443` (из prod-файла), `app.name=MyApp` (из базового, т.к. в prod-файле не задан).

**Важный нюанс:** если активны несколько профилей (`prod,live`), применяется стратегия «последний выигрывает» — `application-live.yml` переопределит `application-prod.yml`. Порядок определяется порядком перечисления в `spring.profiles.active`.

**Ограничение:** свойства `spring.profiles.active`, `spring.profiles.include` и `spring.profiles.group` нельзя использовать внутри профиль-специфичных файлов или в документах с `spring.config.activate.on-profile`.

---

### Вопрос 29. Что такое Spring Boot Actuator? Какие эндпоинты открыты по умолчанию по HTTP, а какие только через JMX? Почему /env и /beans закрыты по умолчанию и как их безопасно открыть в production?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

Spring Boot Actuator предоставляет production-ready функции мониторинга и управления приложением. Эндпоинты позволяют взаимодействовать с приложением и получать информацию о нём.

**По умолчанию по HTTP** открыт только эндпоинт `/actuator/health`. Эндпоинт `/actuator/info` начиная с Spring Boot 2.6 также закрыт по умолчанию.

**По умолчанию через JMX** также открыт только `health`.

Конфигурация:
```
management.endpoints.web.exposure.include=health
management.endpoints.jmx.exposure.include=health
```

`/env` и `/beans` закрыты по умолчанию, потому что содержат чувствительные данные: `/env` показывает все переменные окружения и системные свойства (включая пароли и API-ключи), `/beans` раскрывает внутреннюю структуру Spring-контекста.

Для безопасного открытия в production рекомендуется использовать Spring Security с ограничением по ролям, либо вынести actuator на отдельный management-порт, закрытый файрволом.

#### Ответ от Claude

**Что такое Spring Boot Actuator**

Spring Boot Actuator — это подмодуль Spring Boot, который добавляет в приложение набор production-ready эндпоинтов для мониторинга, управления и диагностики. Подключается зависимостью:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**Какие эндпоинты открыты по умолчанию**

В Spring Boot 3.x существуют два понятия: «включён» (enabled) и «открыт» (exposed).

Все стандартные эндпоинты **включены** по умолчанию (кроме `/shutdown`). Но «включён» не значит «доступен через HTTP».

**Открыты по HTTP по умолчанию:** только `health`.

**Открыты через JMX по умолчанию:** только `health`.

Полный список встроенных эндпоинтов (все требуют явного открытия кроме health):

| Эндпоинт | Описание |
|---|---|
| `health` | Состояние приложения |
| `info` | Информация о приложении |
| `metrics` | Метрики (Micrometer) |
| `env` | Все переменные окружения и свойства |
| `beans` | Все Spring-бины в контексте |
| `mappings` | Все @RequestMapping маппинги |
| `conditions` | Условия автоконфигурации |
| `configprops` | Все @ConfigurationProperties |
| `loggers` | Управление уровнями логирования |
| `threaddump` | Дамп потоков JVM |
| `heapdump` | Heap dump JVM |
| `shutdown` | Graceful shutdown (отключён) |

**Почему /env и /beans закрыты по умолчанию**

`/env` — возвращает все `PropertySource` из `ConfigurableEnvironment`, включая переменные окружения, системные свойства, значения application.yml. Это означает потенциальную утечку паролей БД, секретов OAuth, API-ключей. Даже несмотря на то, что Spring Boot **санирует** значения с именами, содержащими `password`, `secret`, `key` и т.п. (заменяет их на `******`), кастомные названия секретных свойств санации не подвергаются.

`/beans` — раскрывает полную структуру Spring-контекста: все бины, их типы, зависимости, scope. Эта информация помогает атакующему понять архитектуру приложения и найти точки атаки.

**Как безопасно открыть в production**

**Вариант 1: Отдельный management-порт + файрвол (рекомендован)**

```yaml
management:
  server:
    port: 9090        # отдельный порт, закрытый снаружи
  endpoints:
    web:
      exposure:
        include: "health,env,beans,metrics"
```

Порт 9090 доступен только внутри сети (правило файрвола / security group).

**Вариант 2: Spring Security с ограничением по ролям**

```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(requests -> requests
                .requestMatchers(EndpointRequest.to("health")).permitAll()
                .anyRequest().hasRole("ACTUATOR_ADMIN")
            )
            .httpBasic(withDefaults());
        return http.build();
    }
}
```

**Вариант 3: Контроль санации /env**

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,env"
  endpoint:
    env:
      show-values: when-authorized   # NEVER / ALWAYS / WHEN_AUTHORIZED
      roles: "ROLE_ACTUATOR_ADMIN"
```

`show-values: when-authorized` — несанированные значения показываются только пользователям с нужной ролью; остальные видят `******`.

**Никогда не делайте в production:**

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"   # открывает ВСЕ эндпоинты без защиты
```

---

### Вопрос 30. Как реализовать кастомный HealthIndicator? Какова разница между статусами UP, DOWN, OUT_OF_SERVICE и UNKNOWN? Как агрегируются статусы нескольких HealthIndicator'ов в итоговый /actuator/health?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot (actuator health)](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

Для создания кастомного HealthIndicator нужно реализовать интерфейс `HealthIndicator` и зарегистрировать класс как Spring-бин. Имя бина без суффикса `HealthIndicator` становится ключом в ответе `/actuator/health`.

```java
@Component
public class MyHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        int errorCode = check();
        if (errorCode != 0) {
            return Health.down()
                .withDetail("Error Code", errorCode)
                .build();
        }
        return Health.up().build();
    }

    private int check() {
        return 0;
    }
}
```

Агрегация статусов выполняется через `StatusAggregator`. По умолчанию порядок приоритетов: `DOWN > OUT_OF_SERVICE > UNKNOWN > UP`. Итоговый статус — наиболее «тяжёлый» из всех индикаторов. Порядок настраивается через `management.endpoint.health.status.order`.

#### Ответ от Claude

**Реализация кастомного HealthIndicator**

Spring Boot предоставляет интерфейс `HealthIndicator` с единственным методом `health()`:

```java
@Component
public class ExternalApiHealthIndicator implements HealthIndicator {

    private final ExternalApiClient apiClient;

    public ExternalApiHealthIndicator(ExternalApiClient apiClient) {
        this.apiClient = apiClient;
    }

    @Override
    public Health health() {
        try {
            boolean available = apiClient.ping();
            if (available) {
                return Health.up()
                    .withDetail("url", apiClient.getBaseUrl())
                    .withDetail("responseTime", apiClient.getLastResponseTimeMs() + "ms")
                    .build();
            } else {
                return Health.down()
                    .withDetail("url", apiClient.getBaseUrl())
                    .withDetail("reason", "ping returned false")
                    .build();
            }
        } catch (Exception ex) {
            return Health.down(ex)
                .withDetail("url", apiClient.getBaseUrl())
                .build();
        }
    }
}
```

Имя ключа в JSON-ответе формируется из имени бина: `ExternalApiHealthIndicator` → `externalApi`. То есть в `/actuator/health` появится:

```json
{
  "status": "UP",
  "components": {
    "externalApi": {
      "status": "UP",
      "details": {
        "url": "https://api.example.com",
        "responseTime": "42ms"
      }
    }
  }
}
```

Для асинхронных проверок можно реализовать `ReactiveHealthIndicator` (возвращает `Mono<Health>`).

**Разница между статусами**

| Статус | Смысл | HTTP-код по умолчанию | Когда использовать |
|---|---|---|---|
| `UP` | Компонент работает нормально | 200 | Все проверки прошли успешно |
| `DOWN` | Компонент не работает | 503 | Критический сбой: БД недоступна, сервис упал |
| `OUT_OF_SERVICE` | Компонент намеренно выведен из эксплуатации | 503 | Плановое обслуживание, graceful shutdown, Circuit Breaker OPEN |
| `UNKNOWN` | Статус не удаётся определить | 200 | Нет данных для оценки, промежуточное состояние |

Семантическая разница между `DOWN` и `OUT_OF_SERVICE` принципиальна: `DOWN` означает непредвиденную аварию, `OUT_OF_SERVICE` — осознанное отключение. Load balancer может использовать это различие для принятия решений о маршрутизации.

`UNKNOWN` возвращает HTTP 200, потому что отсутствие информации не является признаком неисправности — в отличие от `DOWN`.

**Агрегация статусов через StatusAggregator**

`CompositeHealth` (итоговый `/actuator/health`) агрегируется через `StatusAggregator`. Реализация по умолчанию — `SimpleStatusAggregator`, которая выбирает наиболее «тяжёлый» статус по предопределённому порядку:

```
DOWN > OUT_OF_SERVICE > UNKNOWN > UP
```

Алгоритм: собрать все статусы от всех `HealthIndicator`, отсортировать по приоритету, взять первый (наиболее серьёзный).

Пример агрегации:
```
db          → UP
diskSpace   → UP
externalApi → DOWN
redis       → OUT_OF_SERVICE

Итог: DOWN  (наиболее тяжёлый статус)
```

**Настройка порядка статусов** (например, для кастомного статуса `FATAL`):

```yaml
management:
  endpoint:
    health:
      status:
        order: "fatal,down,out-of-service,unknown,up"
        http-mapping:
          fatal: 503
          down: 503
          out-of-service: 503
```

**Настройка видимости компонентов:**

```yaml
management:
  endpoint:
    health:
      show-details: when-authorized   # never / always / when-authorized
      show-components: always
      roles: "ROLE_ACTUATOR"
```

По умолчанию `show-details: never` — в ответе виден только итоговый `status`, без раскрытия отдельных компонентов.

**Health Groups** (Spring Boot 2.2+) — позволяют объединить индикаторы в именованные группы с независимой агрегацией и отдельными эндпоинтами (`/actuator/health/liveness`, `/actuator/health/readiness`):

```yaml
management:
  endpoint:
    health:
      group:
        liveness:
          include: "livenessstate"
        readiness:
          include: "readinessstate,db,redis"
```

Это критически важно для Kubernetes: liveness probe и readiness probe должны проверять разные наборы индикаторов.

---
### Вопрос 31. Как Spring Security взаимодействует с Actuator? Что происходит с защитой эндпоинтов, если вы определяете собственный SecurityFilterChain-бин? Почему автоконфигурация Actuator «отступает» и как вернуть защиту правильно?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

Если Spring Security присутствует в classpath и не определён ни один другой бин `SecurityFilterChain`, то все эндпоинты Actuator, кроме `/health`, защищаются автоконфигурацией Spring Boot. Если же пользователь определяет собственный бин `SecurityFilterChain`, автоконфигурация полностью отступает, и пользователь обязан самостоятельно контролировать правила доступа к эндпоинтам Actuator. Spring Boot предоставляет вспомогательный класс `EndpointRequest`, который создаёт `RequestMatcher` на основе свойства `management.endpoints.web.base-path`. CSRF-защита включена по умолчанию, поэтому эндпоинты, требующие POST (например, shutdown, loggers), PUT или DELETE, при стандартной конфигурации безопасности будут получать ответ 403 Forbidden.

#### Ответ от Claude

**Архитектура взаимодействия по умолчанию**

Spring Boot регистрирует два отдельных класса автоконфигурации безопасности:

- `SecurityAutoConfiguration` — базовая безопасность для всего веб-приложения (Form Login / HTTP Basic).
- `ManagementWebSecurityAutoConfiguration` — отдельная цепочка фильтров (`SecurityFilterChain`) специально для эндпоинтов Actuator.

По умолчанию `ManagementWebSecurityAutoConfiguration` регистрирует `SecurityFilterChain` с условием `@ConditionalOnDefaultWebSecurity` и разрешает доступ к `/actuator/health` без аутентификации, а все остальные эндпоинты Actuator защищает.

**Что происходит при определении собственного `SecurityFilterChain`**

Когда разработчик объявляет хотя бы один бин `SecurityFilterChain`, аннотация `@ConditionalOnDefaultWebSecurity` становится ложной (default web security больше не действует). Это запускает механизм отступания («backing off»):

1. `ManagementWebSecurityAutoConfiguration` полностью отступает и не регистрирует свою цепочку фильтров.
2. Пользовательский `SecurityFilterChain` становится единственным активным, но в нём нет правил для эндпоинтов Actuator.
3. Итог: эндпоинты Actuator либо полностью открыты (если в цепочке `anyRequest().permitAll()`), либо попадают под общие правила, что может давать неожиданный результат.

При этом бин `UserDetailsService` **не** отключается автоматически — он по-прежнему работает, если только разработчик не определил собственный `UserDetailsService`, `AuthenticationProvider` или `AuthenticationManager`.

**Почему автоконфигурация «отступает»**

Это принципиальный дизайн Spring Boot («opinionated defaults»): автоконфигурация активируется только тогда, когда разработчик не выразил собственного намерения. Условие `@ConditionalOnDefaultWebSecurity` реализовано через `@ConditionalOnMissingBean(SecurityFilterChain.class)` (по сути), поэтому как только появляется пользовательский бин `SecurityFilterChain` — Boot отступает целиком, избегая конфликта двух конкурирующих цепочек фильтров.

**Как правильно вернуть защиту Actuator**

Используйте класс `EndpointRequest` из пакета `org.springframework.boot.security.autoconfigure.actuate.web.servlet` (Boot 3.x), который учитывает значение `management.endpoints.web.base-path` и строит корректный `RequestMatcher`:

```java
@Configuration(proxyBeanMethods = false)
public class SecurityConfiguration {

    // Цепочка для эндпоинтов Actuator (отдельный бин с высоким порядком)
    @Bean
    @Order(1)
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        http.securityMatcher(EndpointRequest.toAnyEndpoint());
        http.authorizeHttpRequests(requests ->
            requests.anyRequest().hasRole("ENDPOINT_ADMIN")
        );
        http.httpBasic(Customizer.withDefaults());
        return http.build();
    }

    // Цепочка для остального приложения
    @Bean
    @Order(2)
    public SecurityFilterChain appSecurityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(requests ->
            requests.anyRequest().authenticated()
        );
        http.formLogin(Customizer.withDefaults());
        return http.build();
    }
}
```

Альтернатива — одна цепочка с явными правилами для обоих пространств URL:

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(requests -> requests
        .requestMatchers(EndpointRequest.to(HealthEndpoint.class, InfoEndpoint.class)).permitAll()
        .requestMatchers(EndpointRequest.toAnyEndpoint()).hasRole("ADMIN")
        .anyRequest().authenticated()
    );
    http.formLogin(Customizer.withDefaults());
    return http.build();
}
```

**Ключевые тонкости**

- `EndpointRequest.toAnyEndpoint()` включает все субпути (`/actuator/endpoint/**`), а не только корень.
- CSRF по умолчанию включён: для POST-эндпоинтов (shutdown, loggers) нужно либо отключить CSRF для пути Actuator, либо отправлять CSRF-токен.
- Если Actuator работает на отдельном management-порту (`management.server.port`), применяется отдельный контекст (`ChildManagementContext`), и правила безопасности для него задаются независимо.
- Класс `ManagementWebSecurityAutoConfiguration` можно явно исключить через `@SpringBootApplication(exclude = ManagementWebSecurityAutoConfiguration.class)`, если защита Actuator не нужна вообще.

---

### Вопрос 32. Назовите принципиальные отличия Spring Boot от «чистого» Spring: что именно вам пришлось бы настраивать вручную без Boot (DispatcherServlet, DataSource, TransactionManager и т.д.)?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [A Comparison Between Spring and Spring Boot — baeldung.com](https://www.baeldung.com/spring-vs-spring-boot)

В «чистом» Spring необходимо вручную настроить `DispatcherServlet` через `web.xml` или реализацию `WebApplicationInitializer`. DataSource конфигурируется как явный бин с указанием `driverClassName`, `url`, `username`, `password`. Для управления транзакциями нужно добавить `@EnableTransactionManagement` в конфигурационный класс и вручную объявить бин `PlatformTransactionManager`. Spring Boot устраняет весь этот шаблонный код: он автоматически регистрирует `DispatcherServlet`, создаёт `DataSource` на основе свойств `spring.datasource.*` и автоматически включает управление транзакциями при наличии зависимостей `spring-data-*` или `spring-tx`.

#### Ответ от Claude

**Концептуальная разница**

«Чистый» Spring — это набор модулей (Core, MVC, Data, Security и др.), который предоставляет механизмы, но не принимает решений за разработчика. Spring Boot добавляет три слоя поверх Spring:

1. **Starter-зависимости** — курируемые наборы совместимых версий библиотек.
2. **Автоконфигурация** — классы с `@ConditionalOn*`, которые регистрируют бины только при отсутствии пользовательских.
3. **Встроенный сервер** — Tomcat/Jetty/Undertow прямо в JAR-файле.

**Что нужно настраивать вручную без Boot**

| Компонент | Plain Spring (ручная настройка) | Spring Boot (автоматически) |
|---|---|---|
| **DispatcherServlet** | Регистрация через `web.xml` или `WebApplicationInitializer.onStartup()`, маппинг на `"/"` | `DispatcherServletAutoConfiguration` регистрирует и маппирует автоматически |
| **WebApplicationContext** | Создание `AnnotationConfigWebApplicationContext`, регистрация конфигурационных классов | `SpringApplication` создаёт нужный тип контекста по classpath |
| **DataSource** | Явный бин `DataSource` с JDBC-параметрами (или настройка пула, например HikariCP) | `DataSourceAutoConfiguration` создаёт пул HikariCP из `spring.datasource.*` |
| **EntityManagerFactory** | Явный бин `LocalContainerEntityManagerFactoryBean` с указанием persistenceUnit, JPA-провайдера, маппинга пакетов | `HibernateJpaAutoConfiguration` настраивает Hibernate автоматически |
| **TransactionManager** | `@EnableTransactionManagement` + явный бин `JpaTransactionManager` или `DataSourceTransactionManager` | `TransactionAutoConfiguration` включает `@EnableTransactionManagement` и регистрирует `JpaTransactionManager` |
| **ViewResolver** | Явный бин `InternalResourceViewResolver` или `ThymeleafViewResolver` с настройкой prefix/suffix | `ThymeleafAutoConfiguration`/`FreeMarkerAutoConfiguration` регистрируют resolver по classpath |
| **MessageSource** | Явный бин `ResourceBundleMessageSource` | `MessageSourceAutoConfiguration` настраивает автоматически |
| **Сервер** | WAR-файл + внешний Tomcat/Jetty; или `EmbeddedWebApplicationContext` с ручной настройкой | Встроенный сервер из `spring-boot-starter-web`, конфигурируется через `server.*` |
| **Packaging и запуск** | Нужен контейнер сервлетов; `main()`-метод требует дополнительной работы | Исполняемый fat JAR с `SpringApplication.run()` |
| **Profiles и externalized config** | Ручная настройка `PropertySourcesPlaceholderConfigurer`, `@PropertySource` | `application.properties`/`application.yml`, иерархия источников конфигурации |
| **Component scanning** | `@ComponentScan` или `<context:component-scan>` с явным указанием пакетов | `@SpringBootApplication` включает `@ComponentScan` от пакета главного класса |

**Пример ручной настройки DispatcherServlet (plain Spring)**

```java
public class WebAppInitializer implements WebApplicationInitializer {
    @Override
    public void onStartup(ServletContext container) {
        AnnotationConfigWebApplicationContext ctx = new AnnotationConfigWebApplicationContext();
        ctx.register(AppConfig.class);
        ctx.setServletContext(container);

        ServletRegistration.Dynamic servlet =
            container.addServlet("dispatcher", new DispatcherServlet(ctx));
        servlet.setLoadOnStartup(1);
        servlet.addMapping("/");
    }
}
```

В Spring Boot этот код полностью заменяется автоконфигурацией — достаточно добавить `spring-boot-starter-web` в зависимости.

**Пример ручной настройки DataSource и TransactionManager (plain Spring)**

```java
@Configuration
@EnableTransactionManagement
public class PersistenceConfig {

    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
        ds.setUsername("user");
        ds.setPassword("pass");
        return ds;
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory() {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource());
        em.setPackagesToScan("com.example.domain");
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        return em;
    }

    @Bean
    public PlatformTransactionManager transactionManager(EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }
}
```

В Spring Boot весь этот блок заменяется несколькими строками в `application.properties`.

**Итог**

Spring Boot не меняет механику Spring — он предоставляет разумные умолчания для 90% случаев. При необходимости любой автоконфигурированный бин можно переопределить, объявив собственный бин того же типа: Boot увидит его и отступит (`@ConditionalOnMissingBean`).

---

### Вопрос 33. Можно ли использовать Spring Boot без встроенного сервера (например, для batch-приложения или CLI-утилиты)? Как это сделать и какой тип ApplicationContext будет создан?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Embedded Web Servers :: Spring Boot — docs.spring.io](https://docs.spring.io/spring-boot/how-to/webserver.html)

Чтобы отключить встроенный веб-сервер, нужно установить свойство `spring.main.web-application-type=none` в файле конфигурации (application.properties или application.yml). При этом Spring Boot создаёт стандартный не-веб `ApplicationContext` вместо `WebApplicationContext`. Это подходит для batch-приложений, CLI-утилит и приложений с периодическими задачами. Альтернативно можно задать `server.port=-1` — тогда создаётся `WebApplicationContext`, но HTTP-сервер не запускается ни на каком порту.

#### Ответ от Claude

**Да, Spring Boot отлично работает без встроенного сервера.**

**Механизм определения типа приложения**

`SpringApplication` при запуске автоматически определяет тип приложения (`WebApplicationType`) по classpath:

| Условие | `WebApplicationType` | Создаваемый `ApplicationContext` |
|---|---|---|
| Spring MVC (`DispatcherServlet`) в classpath | `SERVLET` | `AnnotationConfigServletWebServerApplicationContext` |
| Spring WebFlux, но не Spring MVC | `REACTIVE` | `AnnotationConfigReactiveWebServerApplicationContext` |
| Ни MVC, ни WebFlux | `NONE` | `AnnotationConfigApplicationContext` |

Если `spring-boot-starter-web` присутствует в зависимостях, Spring Boot по умолчанию запустит Tomcat. Для batch/CLI-приложений это нежелательно.

**Способы отключить веб-сервер**

**Способ 1: application.properties / application.yml**

```properties
spring.main.web-application-type=none
```

```yaml
spring:
  main:
    web-application-type: "none"
```

**Способ 2: программно через `SpringApplication`**

```java
@SpringBootApplication
public class BatchApplication {
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(BatchApplication.class);
        app.setWebApplicationType(WebApplicationType.NONE);
        app.run(args);
    }
}
```

**Способ 3: через `SpringApplicationBuilder`** (удобно для иерархических контекстов)

```java
new SpringApplicationBuilder(BatchApplication.class)
    .web(WebApplicationType.NONE)
    .run(args);
```

**Способ 4: убрать web-стартер из зависимостей**

Если использовать `spring-boot-starter` вместо `spring-boot-starter-web`, Tomcat просто не попадёт в classpath, и `SpringApplication` сам выберет `WebApplicationType.NONE`.

**Что создаётся при `WebApplicationType.NONE`**

Создаётся `AnnotationConfigApplicationContext` — стандартный контекст Spring без поддержки веб-сервера. Он:

- Поддерживает `@Configuration`, `@Bean`, `@Component`, `@Autowired` и весь IoC-контейнер Spring.
- Не запускает Tomcat/Jetty/Undertow.
- Не регистрирует `DispatcherServlet`.
- Не слушает HTTP-порт.
- Поддерживает Spring Batch, Spring Integration, планировщики (`@Scheduled`), `CommandLineRunner`, `ApplicationRunner` и т.д.

**Типичная структура batch-приложения**

```java
@SpringBootApplication
@EnableBatchProcessing
public class BatchApplication {
    public static void main(String[] args) {
        SpringApplication.run(BatchApplication.class, args);
    }
}
```

```properties
spring.main.web-application-type=none
# Spring Batch: выполнить конкретный job при старте
spring.batch.job.name=myJob
```

**Интерфейсы для логики запуска CLI-утилиты**

```java
@Component
public class MyCliRunner implements CommandLineRunner {
    @Override
    public void run(String... args) throws Exception {
        // args — аргументы командной строки
        System.out.println("Running with args: " + Arrays.toString(args));
    }
}
```

Или `ApplicationRunner` (получает `ApplicationArguments` вместо `String[]`):

```java
@Component
public class MyAppRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) throws Exception {
        List<String> files = args.getOptionValues("file");
        // ...
    }
}
```

**Важные нюансы**

- Даже при `web-application-type=none` можно оставить `spring-boot-starter-web` в зависимостях — Spring Boot не запустит сервер, но сервлетные API останутся доступны (полезно для тестов или использования отдельных классов).
- Spring Boot Actuator в режиме `NONE` не поднимает HTTP-эндпоинты, но JMX-эндпоинты остаются доступны (если включены).
- Для Spring Batch в Boot 3.x аннотация `@EnableBatchProcessing` по-прежнему нужна (или настройка через `spring.batch.job.enabled`), а автоконфигурация Batch работает при наличии `spring-boot-starter-batch`.
### Вопрос 34. Что произойдёт, если в classpath есть и spring-boot-starter-web, и spring-boot-starter-webflux одновременно? Как Spring Boot решает, какой стек поднимать, и как это поведение можно переопределить явно?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Reactive Web Applications :: Spring Boot](https://docs.spring.io/spring-boot/reference/web/reactive.html)

Добавление обоих модулей — `spring-boot-starter-web` и `spring-boot-starter-webflux` — приводит к тому, что Spring Boot автоматически конфигурирует Spring MVC, а не WebFlux. Такое поведение выбрано намеренно: многие разработчики добавляют `spring-boot-starter-webflux` в уже существующее MVC-приложение, чтобы воспользоваться реактивным клиентом `WebClient` для исходящих запросов, не переходя полностью на реактивный стек. Переопределить поведение можно, вызвав `SpringApplication.setWebApplicationType(WebApplicationType.REACTIVE)` или задав свойство `spring.main.web-application-type=reactive`.

#### Ответ от Claude

**Механизм выбора стека**

При старте приложения `SpringApplication` вызывает метод `WebApplicationType.deduceFromClasspath()`, который проверяет наличие ключевых классов в classpath по следующей логике:

1. Если в classpath присутствует `org.springframework.web.servlet.DispatcherServlet` (поставляется со `spring-boot-starter-web`) — выбирается `WebApplicationType.SERVLET`.
2. Если `DispatcherServlet` отсутствует, но присутствует `org.springframework.web.reactive.DispatcherHandler` (из `spring-boot-starter-webflux`) — выбирается `WebApplicationType.REACTIVE`.
3. Иначе — `WebApplicationType.NONE` (не поднимается встроенный сервер).

Из этого следует: **при наличии обоих стартеров SERVLET имеет приоритет**, так как `DispatcherServlet` окажется в classpath первым по условию. Соответственно, Spring Boot поднимает `AnnotationConfigServletWebServerApplicationContext` со встроенным Tomcat/Jetty/Undertow, а не реактивный Netty.

Это поведение задокументировано явно и обосновано распространённым сценарием: разработчики подключают `spring-boot-starter-webflux` только ради `WebClient` (реактивный HTTP-клиент), оставляя серверную часть на Servlet-стеке.

**Как переопределить явно**

Способ 1 — через `application.properties` / `application.yml` (рекомендуется):
```properties
spring.main.web-application-type=reactive
```
```yaml
spring:
  main:
    web-application-type: reactive
```

Способ 2 — программно в `main`-методе:
```java
SpringApplication app = new SpringApplication(MyApplication.class);
app.setWebApplicationType(WebApplicationType.REACTIVE);
app.run(args);
```

Допустимые значения `WebApplicationType`: `SERVLET`, `REACTIVE`, `NONE`.

**Что происходит при явном выборе REACTIVE**

Spring Boot поднимает `AnnotationConfigReactiveWebServerApplicationContext` со встроенным Netty (по умолчанию) вместо Tomcat. `DispatcherHandler` заменяет `DispatcherServlet`. Автоконфигурация `WebFluxAutoConfiguration` становится активной вместо `WebMvcAutoConfiguration`.

**Важный нюанс с автоконфигурацией**

`WebFluxAutoConfiguration` аннотирован условием `@ConditionalOnWebApplication(type = Type.REACTIVE)`, а `WebMvcAutoConfiguration` — `@ConditionalOnWebApplication(type = Type.SERVLET)`. Поэтому при смене типа через свойство автоматически переключается и набор применяемых автоконфигураций — вручную ничего дополнительно отключать не нужно.

**Практическая рекомендация**

Если вам нужен только `WebClient` без перехода на реактивный стек — оставьте оба стартера без изменений: Spring Boot правильно поднимет MVC и позволит использовать `WebClient` для исходящих вызовов. Если же нужен полный переход на WebFlux — задайте `spring.main.web-application-type=reactive`.

---

### Вопрос 35. Как отлаживать автоконфигурацию? Какое свойство или флаг запуска позволяет увидеть, какие автоконфигурации применились, а какие были отклонены и почему? Что показывает /actuator/conditions?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Conditions Evaluation Report (conditions) :: Spring Boot](https://docs.spring.io/spring-boot/api/rest/actuator/conditions.html)

Для получения отчёта об автоконфигурации необходимо выполнить GET-запрос к `/actuator/conditions`. Ответ содержит три раздела:

- **positiveMatches** — конфигурации и методы, чьи условия **выполнились** (автоконфигурация применена). Пример: `"EndpointAutoConfiguration#propertiesEndpointAccessResolver"` с пояснением `"@ConditionalOnMissingBean did not find any beans"`.
- **negativeMatches** — конфигурации, чьи условия **не выполнились** (автоконфигурация отклонена). Содержит подразделы `notMatched` (условия, из-за которых конфигурация отклонена) и `matched` (условия, которые прошли, но не спасли конфигурацию). Пример: `"GsonHttpMessageConvertersConfiguration"` с причиной `"@ConditionalOnClass did not find required class 'com.google.gson.Gson'"`.
- **unconditionalClasses** — классы автоконфигурации, загружаемые **всегда**, без условий (например, `PropertyPlaceholderAutoConfiguration`).

#### Ответ от Claude

**Способы включить отчёт об оценке условий (Condition Evaluation Report)**

**1. Флаг `--debug` при запуске JAR:**
```bash
java -jar myapp.jar --debug
```

**2. Системное свойство JVM:**
```bash
java -Ddebug=true -jar myapp.jar
```

**3. Свойство в `application.properties`:**
```properties
debug=true
```

При любом из этих вариантов в консоль после старта выводится раздел `CONDITIONS EVALUATION REPORT` (в старых версиях — `AUTO-CONFIGURATION REPORT`) уровня DEBUG через `ConditionEvaluationReportLoggingListener`. Внешне он выглядит так:

```
============================
CONDITIONS EVALUATION REPORT
============================

Positive matches:
-----------------
   DispatcherServletAutoConfiguration matched:
      - @ConditionalOnClass found required class
        'org.springframework.web.servlet.DispatcherServlet'
        (OnClassCondition)

Negative matches:
-----------------
   GsonAutoConfiguration:
      Did not match:
         - @ConditionalOnClass did not find required class
           'com.google.gson.Gson' (OnClassCondition)
```

**Что означает каждый раздел:**

| Раздел | Смысл |
|---|---|
| **Positive matches** | Условие (`@ConditionalOn*`) выполнено, автоконфигурация применена, бины зарегистрированы |
| **Negative matches** | Хотя бы одно условие не выполнено, автоконфигурация **пропущена**; указывается, какое именно условие не прошло |
| **Unconditional classes** | Конфигурация применяется безусловно, без каких-либо `@Conditional` аннотаций |
| **Exclusions** | Классы, явно исключённые через `@SpringBootApplication(exclude=...)` или `spring.autoconfigure.exclude` |

**Что показывает `/actuator/conditions`**

Эндпоинт требует наличия `spring-boot-starter-actuator` и экспозиции:
```properties
management.endpoints.web.exposure.include=conditions
```

GET `/actuator/conditions` возвращает тот же отчёт в формате JSON, что удобно при работе с несколькими контекстами (например, при иерархии контекстов) или для интеграции с инструментами мониторинга. Структура ответа:

```json
{
  "contexts": {
    "application": {
      "positiveMatches": { ... },
      "negativeMatches": { ... },
      "unconditionalClasses": [ ... ]
    }
  }
}
```

Ключевое преимущество `/actuator/conditions` перед логом — доступность **на живом экземпляре** без перезапуска и без включения режима отладки.

**Альтернатива — включить DEBUG-логирование только для класса репортера:**
```properties
logging.level.org.springframework.boot.autoconfigure.logging.ConditionEvaluationReportLoggingListener=DEBUG
```

Это позволяет видеть отчёт без включения глобального режима `debug=true`, что полезно в production-среде, где глобальный DEBUG может быть слишком шумным.

**Spring Boot DevTools**

При наличии `spring-boot-devtools` при каждом hot-restart в лог выводится **дельта** отчёта условий — только изменения по сравнению с предыдущим запуском, что ускоряет диагностику при разработке.

---

### Вопрос 36. Как работает @RefreshScope в связке с Spring Cloud Config и Actuator? Какие бины пересоздаются при вызове /actuator/refresh, а какие — нет? Какие есть подводные камни при использовании @RefreshScope с singleton-зависимостями?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Spring Cloud Context: Application Context Services :: Spring Cloud Commons](https://docs.spring.io/spring-cloud-commons/reference/spring-cloud-commons/application-context-services.html)

`@RefreshScope` — ленивые прокси, которые инициализируются при первом обращении (при вызове метода), а область видимости выступает кешем инициализированных значений. При вызове `/actuator/refresh` выполняется перезагрузка всех источников свойств `Environment`, после чего публикуется `EnvironmentChangeEvent`. `RefreshScope` очищает кеш всех бинов в этой области видимости. При следующем обращении бины переинициализируются с новыми значениями свойств. `@ConfigurationProperties`-бины перепривязываются автоматически. Бины с явным singleton-скоупом через `/refresh` обновить нельзя — для них нужно либо реализовать отдельный эндпоинт для разрушения и пересоздания, либо обрабатывать перезагрузку внутри самого бина. `HikariDataSource` по умолчанию находится в списке `spring.cloud.refresh.never-refreshable` и обновлению не подлежит. Java Records с `@ConfigurationProperties` не могут быть обновлены (immutable).

#### Ответ от Claude

**Как работает @RefreshScope**

`@RefreshScope` реализован через стандартный механизм Spring-скоупов. Все бины, помеченные этой аннотацией, оборачиваются в **ленивый CGLIB-прокси**. Фактический объект не создаётся при старте контейнера — он инициализируется при первом вызове любого метода на прокси. `RefreshScope` ведёт внутренний кеш (`Map<String, Object>`): при обращении к бину прокси ищет его в кеше и возвращает закешированный экземпляр, если он уже был создан.

**Что происходит при вызове POST `/actuator/refresh` (пошагово)**

1. HTTP POST на `/actuator/refresh` принимается `RefreshEndpoint`.
2. Вызывается `ContextRefresher.refresh()`.
3. `Environment` перезагружается: Spring Cloud повторно обращается к Config Server (или другому источнику) и обновляет `PropertySource`.
4. Публикуется `EnvironmentChangeEvent` со списком изменённых ключей.
5. Все `@ConfigurationProperties`-бины автоматически **перепривязываются** (`ConfigurationPropertiesRebinder` слушает `EnvironmentChangeEvent`).
6. Вызывается `RefreshScope.refreshAll()` — кеш всех `@RefreshScope`-бинов очищается.
7. При следующем обращении к каждому из них прокси создаёт **новый экземпляр** с актуальными значениями свойств.
8. Уровни логирования (`logging.level.*`) также обновляются.
9. Эндпоинт возвращает JSON-массив с именами изменившихся ключей.

Для работы эндпоинта необходимо:
```properties
management.endpoints.web.exposure.include=refresh
```

**Что обновляется, а что нет**

| Тип бина | Обновляется? |
|---|---|
| Бин с `@RefreshScope` | Да — при следующем обращении |
| `@ConfigurationProperties`-бин (mutable) | Да — перепривязывается автоматически |
| Уровни логирования | Да |
| Обычный singleton (`@Bean` без аннотации) | Нет |
| `@Configuration`-класс с `@RefreshScope` | Нет (сам класс обновляется, его `@Bean`-методы — нет) |
| Java Record с `@ConfigurationProperties` | Нет (immutable) |
| `HikariDataSource` | Нет (в списке `never-refreshable`) |

**Подводные камни с singleton-зависимостями**

**Проблема "застывшей ссылки" (stale reference):**

```java
@Service  // singleton
public class ReportService {

    private final MailConfig mailConfig; // @RefreshScope bean

    public ReportService(MailConfig mailConfig) {
        this.mailConfig = mailConfig; // ссылка на прокси зафиксирована
    }
}
```

На первый взгляд кажется, что всё нормально: `mailConfig` — это прокси, и при обновлении скоупа прокси делегирует вызовы новому экземпляру. Однако проблема возникает, когда **singleton сохраняет не сам прокси, а вытащенное из него значение**:

```java
@Service
public class BadService {
    private final String smtpHost;

    public BadService(MailConfig mailConfig) {
        // сохраняем примитивное значение, а не прокси
        this.smtpHost = mailConfig.getSmtpHost();
    }
    // после @RefreshScope smtpHost по-прежнему содержит старое значение
}
```

В этом случае singleton навсегда "заморозил" старое значение. Решения:
- Обращаться к `mailConfig.getSmtpHost()` при каждом вызове метода (не кешировать в поле).
- Пометить `BadService` тоже как `@RefreshScope`.

**Проблема с `@Configuration` и `@RefreshScope`:**

```java
@Configuration
@RefreshScope  // НЕ РАБОТАЕТ как ожидается
public class DataConfig {
    @Bean
    public DataSource dataSource(DbProps props) {
        return new DriverManagerDataSource(props.getUrl());
    }
}
```

`@RefreshScope` на `@Configuration`-классе не распространяется на `@Bean`-методы внутри него. Бины остаются singleton'ами. Нужно аннотировать каждый `@Bean` по отдельности.

**HikariDataSource и never-refreshable:**

```properties
# Значение по умолчанию в Spring Cloud
spring.cloud.refresh.never-refreshable=com.zaxxer.hikari.HikariDataSource
```

Попытка поставить `@RefreshScope` на `HikariDataSource` не даёт эффекта: Spring Cloud явно блокирует обновление этого бина. Причина — HikariCP управляет пулом соединений и его пересоздание во время работы приложения чревато потерей активных соединений. Если обновление DataSource необходимо, нужно использовать другой пул (например, Apache DBCP2) или реализовать кастомное управление жизненным циклом.

**Immutable records:**

```java
@ConfigurationProperties(prefix = "app")
public record AppConfig(String host, int port) {}
// Невозможно перепривязать — запись неизменяема по определению
```

Для динамически обновляемых свойств используйте обычный mutable класс с геттерами/сеттерами или `@Getter @Setter` (Lombok).

**Дополнительные свойства для тонкой настройки:**

```properties
# Добавить бины, которые должны обновляться (помимо стандартных)
spring.cloud.refresh.extra-refreshable=com.example.MySpecialBean

# Полностью отключить RefreshScope (нужно для AOT/GraalVM)
spring.cloud.refresh.enabled=false

# Отключить обновление при рестарте контекста
spring.cloud.refresh.on-restart.enabled=false
```

**Spring Cloud Bus**

Для обновления конфигурации во всех экземплярах приложения одновременно используется Spring Cloud Bus (`spring-cloud-starter-bus-amqp` или `spring-cloud-starter-bus-kafka`). При вызове `/actuator/busrefresh` на одном экземпляре сообщение рассылается по шине всем остальным, и каждый выполняет `/refresh` локально.
### Вопрос 37. Как работает @ConditionalOnSingleCandidate? Чем он отличается от @ConditionalOnBean и в каких сценариях его применяют в автоконфигурации?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [ConditionalOnSingleCandidate (Spring Boot 3.5.7 API)](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/autoconfigure/condition/ConditionalOnSingleCandidate.html)

`@ConditionalOnSingleCandidate` — аннотация, которая срабатывает только тогда, когда бин указанного типа уже зарегистрирован в `BeanFactory` **и** может быть однозначно определён единственный кандидат для autowiring. Условие считается выполненным в двух случаях:

1. В контексте зарегистрирован ровно один бин указанного класса.
2. Зарегистрировано несколько бинов указанного класса, но один из них помечен как `@Primary` (или объявлен через `Bean.defaultCandidate` / `BeanDefinition.isDefaultCandidate()`).

Таким образом, условие выполняется тогда и только тогда, когда autowiring по типу завершился бы успехом без ошибки `NoUniqueBeanDefinitionException`.

Аннотация доступна с версии Spring Boot 1.3.0. Реализована через тот же `OnBeanCondition`, что и `@ConditionalOnBean`. Поддерживаемые атрибуты:

- `value` (Class<?>) — тип проверяемого бина; нельзя использовать одновременно с `type`.
- `type` (String) — имя типа в виде строки; используется, когда аннотация является мета-аннотацией.
- `search` (SearchStrategy, по умолчанию `ALL`) — определяет, учитывать ли родительские контексты.

Ключевое ограничение, общее с `@ConditionalOnBean`: условие видит только те бины, которые уже были обработаны к текущему моменту, поэтому аннотацию следует применять исключительно в классах автоконфигурации. Если бин-кандидат создаётся другой автоконфигурацией, та конфигурация должна выполняться раньше (`@AutoConfigureAfter`).

#### Ответ от Claude

**Механизм работы**

`@ConditionalOnSingleCandidate` реализован на базе `OnBeanCondition` и при вычислении условия выполняет следующие шаги:

1. Ищет в `BeanFactory` все зарегистрированные бины (и определения бинов) указанного типа.
2. Если бинов нет — условие не выполнено.
3. Если бин ровно один — условие выполнено.
4. Если бинов несколько — проверяется, есть ли среди них единственный «первичный» кандидат (помечен `@Primary`, `autowireCandidate = true`, `defaultCandidate = true`, либо не является fallback-кандидатом). Если такой кандидат один — условие выполнено; если кандидатов ноль или несколько — условие не выполнено.

Иными словами, условие имитирует логику autowiring по типу: если Spring смог бы выбрать бин без двусмысленности — условие истинно.

**Отличие от @ConditionalOnBean**

| Критерий | `@ConditionalOnBean` | `@ConditionalOnSingleCandidate` |
|---|---|---|
| Что проверяет | Наличие хотя бы одного бина указанного типа | Наличие ровно одного autowire-кандидата (или @Primary среди нескольких) |
| Несколько бинов без @Primary | Условие ВЫПОЛНЕНО | Условие НЕ выполнено |
| Несколько бинов, один @Primary | Условие ВЫПОЛНЕНО | Условие ВЫПОЛНЕНО |
| Использование | Достаточно убедиться, что бин существует | Нужна однозначная инъекция |

**Типичные сценарии применения в автоконфигурации**

Аннотация применяется, когда автоконфигурация должна создать «надстройку» над бином, полагаясь на успешный autowiring:

```java
// Пример из Spring Boot: автоконфигурация JdbcTemplate
@AutoConfiguration
@ConditionalOnClass({ DataSource.class, JdbcTemplate.class })
@ConditionalOnSingleCandidate(DataSource.class)  // срабатывает только если DataSource однозначен
public class JdbcTemplateAutoConfiguration {
    @Bean
    @Primary
    @ConditionalOnMissingBean(JdbcOperations.class)
    public JdbcTemplate jdbcTemplate(DataSource dataSource, JdbcProperties properties) {
        // dataSource гарантированно инжектируется без двусмысленности
        return new JdbcTemplate(dataSource);
    }
}
```

Если пользователь определил два `DataSource` без `@Primary`, автоконфигурация `JdbcTemplateAutoConfiguration` не активируется совсем, вместо того чтобы упасть с `NoUniqueBeanDefinitionException` при попытке создать `JdbcTemplate`. Это делает поведение предсказуемым: автоконфигурация либо настраивает всё корректно, либо полностью уступает контроль пользователю.

**Важное предупреждение**: поскольку условие оценивается по уже обработанным определениям бинов, порядок загрузки автоконфигураций имеет значение. Если `DataSource` создаётся другой автоконфигурацией (например, `DataSourceAutoConfiguration`), класс, использующий `@ConditionalOnSingleCandidate(DataSource.class)`, обязан быть аннотирован `@AutoConfigureAfter(DataSourceAutoConfiguration.class)`.

---

### Вопрос 38. Объясните, почему @ConditionalOnClass использует ASM для разбора метаданных аннотаций вместо Class.forName(). Что произошло бы без этого и что это означает при размещении @ConditionalOnClass на методе @Bean?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Аннотации `@ConditionalOnClass` и `@ConditionalOnMissingClass` позволяют включать классы `@Configuration` в зависимости от наличия или отсутствия конкретных классов. Поскольку метаданные аннотаций разбираются с помощью ASM, можно использовать атрибут `value` для ссылки на реальный класс, даже если он фактически не присутствует в classpath запущенного приложения. Кроме того, можно использовать атрибут `name`, если предпочтительно указывать имя класса в виде строки.

Этот механизм не работает таким же образом для методов `@Bean`, где, как правило, возвращаемый тип является целью условия: до того как условие для метода применяется, JVM уже загрузит класс и потенциально обработает ссылки на методы, что завершится ошибкой, если класс отсутствует. Для обработки этого сценария следует использовать отдельный класс `@Configuration` для изоляции условия.

Пример корректного подхода:

```java
@AutoConfiguration
public final class MyAutoConfiguration {

    @Configuration(proxyBeanMethods = false)
    @ConditionalOnClass(SomeService.class)
    static class SomeServiceConfiguration {

        @Bean
        @ConditionalOnMissingBean
        SomeService someService() {
            return new SomeService();
        }
    }
}
```

#### Ответ от Claude

**Почему нельзя использовать Class.forName()**

Метод `Class.forName(String className)` производит полную загрузку класса в JVM: выполняется поиск `.class`-файла, загрузка байткода, верификация, линковка и инициализация (если не используется `initialize = false`). Если класс отсутствует в classpath — бросается `ClassNotFoundException` или `NoClassDefFoundError`.

Условная аннотация `@ConditionalOnClass` существует именно для того, чтобы определённый блок конфигурации активировался только при наличии нужной библиотеки. Если бы проверка выполнялась через `Class.forName()`, то само вычисление условия немедленно упало бы с исключением при отсутствующем классе — что полностью нивелирует смысл условия.

**Как работает разбор через ASM**

Spring Framework использует библиотеку [ASM](https://asm.ow2.io/) (объект — байткод JVM) для чтения метаданных аннотаций непосредственно из `.class`-файлов конфигурационных классов, не загружая их в JVM. ASM — это легковесный парсер байткода, работающий на уровне байтового потока.

Когда Spring обрабатывает класс-кандидат на автоконфигурацию, он читает атрибут `value` аннотации `@ConditionalOnClass` из байткода через `ASM AnnotationVisitor`. Имена классов в байткоде хранятся как строки (дескрипторы типов вида `Lcom/example/SomeService;`), поэтому ASM извлекает их без загрузки самих классов. После этого Spring проверяет наличие указанных классов в classpath через `ClassLoader.getResource()` (или аналог), что не вызывает загрузку класса.

Таким образом:
- Класс конфигурации (`@ConditionalOnClass(SomeService.class)`) разбирается через ASM — `SomeService` не загружается.
- Если `SomeService` найден в classpath — конфигурация подключается, классы загружаются уже штатным образом.
- Если не найден — конфигурация молча пропускается, никаких исключений нет.

**Что происходит при размещении @ConditionalOnClass на методе @Bean**

Здесь возникает фундаментальная проблема: ASM-разбор работает на уровне метаданных аннотаций класса-конфигурации, но к моменту вычисления условия на `@Bean`-методе JVM уже загрузила сам класс конфигурации. При загрузке класса JVM также разрешает все сигнатуры методов, включая тип возврата `@Bean`-метода. Если тип возврата — это `SomeService`, а класс `SomeService` отсутствует, загрузка класса конфигурации завершится `NoClassDefFoundError` ещё до того, как Spring успеет проверить условие.

Порядок событий при некорректном коде:

```java
// НЕПРАВИЛЬНО: класс конфигурации загружается JVM -> разрешается сигнатура метода ->
// NoClassDefFoundError если SomeService нет в classpath
@Configuration
public class MyAutoConfiguration {
    @Bean
    @ConditionalOnClass(SomeService.class)  // условие вычисляется ПОСЛЕ загрузки класса
    SomeService someService() { ... }
}
```

**Правильный паттерн — вложенный @Configuration**

```java
@AutoConfiguration
public final class MyAutoConfiguration {

    @Configuration(proxyBeanMethods = false)
    @ConditionalOnClass(SomeService.class)  // условие на уровне класса — ASM работает корректно
    static class SomeServiceConfiguration {

        @Bean
        @ConditionalOnMissingBean
        SomeService someService() {         // тип возврата загружается лишь если условие выполнено
            return new SomeService();
        }
    }
}
```

Вложенный статический класс загружается JVM лениво — только при первом обращении к нему. Spring сначала читает аннотацию `@ConditionalOnClass` на `SomeServiceConfiguration` через ASM, и только в случае выполнения условия инициирует загрузку этого класса JVM. Тогда и только тогда разрешается сигнатура метода `someService()` — когда `SomeService` гарантированно есть в classpath.

**Итог**

| | Class.forName() | ASM |
|---|---|---|
| Загружает класс в JVM | Да (немедленно) | Нет (только байткод) |
| Исключение при отсутствии класса | ClassNotFoundException / NoClassDefFoundError | Нет |
| Возможность использования в условиях | Нет | Да |
| Применимость к @Bean-методам | Не применимо | Только через вложенный @Configuration |

---

### Вопрос 39. Что такое файл META-INF/spring-autoconfigure-metadata.properties? Кто его генерирует, какие данные хранит и каким образом он ускоряет старт приложения при обычном запуске и при компиляции в GraalVM native image?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Spring Boot использует процессор аннотаций для сбора условий на автоконфигурации в файл метаданных (`META-INF/spring-autoconfigure-metadata.properties`). Если этот файл присутствует, он используется для опережающей фильтрации автоконфигураций, которые не подходят, что улучшает время запуска.

Для использования процессора необходимо добавить зависимость на `spring-boot-autoconfigure-processor`. С Gradle это выглядит так:

```gradle
dependencies {
    annotationProcessor "org.springframework.boot:spring-boot-autoconfigure-processor"
}
```

Файл хранит предвычисленные метаданные условий из классов автоконфигурации. Пример содержимого файла:

```
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration=
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration.AutoConfigureAfter=org.springframework.boot.autoconfigure.jmx.JmxAutoConfiguration
org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration.ConditionalOnClass=com.rabbitmq.client.Connection,org.springframework.amqp.rabbit.core.RabbitTemplate
```

#### Ответ от Claude

**Что это такое**

`META-INF/spring-autoconfigure-metadata.properties` — файл метаданных условий, генерируемый на этапе компиляции. Он содержит предвычисленную информацию об условных аннотациях (`@ConditionalOnClass`, `@ConditionalOnBean`, `@AutoConfigureAfter`, `@AutoConfigureBefore` и др.) для всех классов автоконфигурации, упакованных в данный JAR-артефакт.

**Кто генерирует**

Файл создаётся аннотационным процессором `spring-boot-autoconfigure-processor` во время компиляции (`javac`). Это стандартный Java Annotation Processing Tool (APT), который:

1. Сканирует исходный код на наличие классов, аннотированных `@AutoConfiguration` (в современных версиях) или перечисленных в `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
2. Читает все условные аннотации этих классов.
3. Записывает извлечённые данные в `META-INF/spring-autoconfigure-metadata.properties` внутри скомпилированного JAR.

Зависимость для подключения процессора:

```xml
<!-- Maven -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-autoconfigure-processor</artifactId>
    <optional>true</optional>
</dependency>
```

```gradle
// Gradle
dependencies {
    annotationProcessor "org.springframework.boot:spring-boot-autoconfigure-processor"
}
```

**Формат и содержимое файла**

Ключ строится по схеме:
```
{полное.имя.КлассаАвтоконфигурации}[.ИмяУсловия]={значение}
```

Примеры реальных записей из Spring Boot:

```properties
# Запись без значения — факт наличия класса как автоконфигурации
org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration=

# ConditionalOnClass: перечень классов через запятую
org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration.ConditionalOnClass=\
  com.rabbitmq.client.Connection,\
  org.springframework.amqp.rabbit.core.RabbitTemplate

# Порядок загрузки
org.springframework.boot.autoconfigure.jdbc.JdbcTemplateAutoConfiguration.AutoConfigureAfter=\
  org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration

# ConditionalOnBean
org.springframework.boot.autoconfigure.jdbc.JdbcTemplateAutoConfiguration.ConditionalOnSingleCandidate=\
  javax.sql.DataSource
```

**Как файл ускоряет старт при обычном запуске на JVM**

При старте Spring Boot загружает список всех зарегистрированных автоконфигураций (из `AutoConfiguration.imports`). Без файла метаданных для фильтрации неподходящих конфигураций пришлось бы:

1. Загрузить каждый класс автоконфигурации в JVM.
2. Прочитать его аннотации через рефлексию.
3. Вычислить условия (например, проверить наличие классов в classpath).

В типичном проекте зарегистрировано более 130 автоконфигураций. Загрузка каждого класса — это IO (чтение `.class` из JAR), верификация байткода и занятие памяти PermGen/Metaspace.

При наличии `spring-autoconfigure-metadata.properties` Spring Boot выполняет **опережающую фильтрацию**:

1. Файл свойств читается как простой текстовый файл — мгновенно, без загрузки каких-либо классов.
2. Для каждой автоконфигурации проверяются условия `ConditionalOnClass` по данным из файла: достаточно проверить наличие ресурса в classpath через `ClassLoader.getResource()`.
3. Конфигурации, чьи классы-условия не найдены, исключаются из дальнейшей обработки — они **никогда не загружаются в JVM**.
4. Только прошедшие фильтрацию классы загружаются и подвергаются полной оценке условий.

Это сокращает количество реально загружаемых классов на этапе старта в несколько раз для типичного Spring Boot-приложения.

**Роль файла при компиляции в GraalVM Native Image**

GraalVM Native Image работает на принципе «замкнутого мира» (closed-world assumption): всё, что попадает в исполняемый файл, должно быть известно в момент компиляции. Динамические механизмы (рефлексия, динамическая загрузка классов) требуют явной регистрации через hint-файлы.

Spring Boot AOT-движок (Spring AOT Engine) при сборке native image выполняет следующее:

1. Запускает `BeanFactory` в режиме AOT-обработки и наполняет его `BeanDefinition`-объектами.
2. Вычисляет все условные аннотации **в момент сборки**, а не в момент запуска образа.
3. Генерирует Java-код (источники), заменяющий динамическую обработку `@Configuration`-классов.
4. Генерирует hint-файлы в `META-INF/native-image/` (reflect-config.json, resource-config.json и др.) для GraalVM.

Файл `spring-autoconfigure-metadata.properties` участвует в этом процессе как источник предвычисленных условий для опережающей фильтрации на шаге 2: автоконфигурации, которые заведомо не подходят (их `ConditionalOnClass` не выполнен при сборке), исключаются ещё до старта AOT-анализа, что:

- Уменьшает объём кода, который AOT-движок должен проанализировать и сконвертировать в статический код.
- Сокращает размер native image: классы исключённых автоконфигураций и их транзитивные зависимости не попадают в граф достижимости GraalVM и не включаются в бинарник.
- Ускоряет время компиляции native image (шаг `native-image` компилятора GraalVM).

Отличие от обычного JVM-запуска состоит в том, что для native image фильтрация является **окончательной и необратимой**: исключённые классы физически отсутствуют в скомпилированном бинарнике, тогда как при JVM-запуске они просто не загружаются, но остаются доступными в classpath.

**Итоговая схема**

```
Компиляция
  javac + spring-boot-autoconfigure-processor
    -> META-INF/spring-autoconfigure-metadata.properties (в JAR)

JVM-запуск
  Чтение .properties (без загрузки классов)
    -> Опережающая фильтрация по ConditionalOnClass
      -> Загрузка только подходящих автоконфигураций
        -> Полная оценка оставшихся условий

GraalVM native image (mvn -Pnative package / gradle nativeCompile)
  Spring AOT Engine читает .properties
    -> Вычисляет условия на этапе сборки
      -> Генерирует статический Java-код + hint-файлы
        -> GraalVM компилирует только достижимый код
          -> Минимальный бинарный образ
```

---
### Вопрос 40. Как работает AutoConfigurationImportSelector как DeferredImportSelector? Почему автоконфигурации загружаются именно через DeferredImportSelector, а не обычный ImportSelector, и что это даёт для порядка обработки пользовательских бинов?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

`AutoConfigurationImportSelector` реализует `DeferredImportSelector` — это разновидность `ImportSelector`, которая запускается **после того, как все обычные `@Configuration`-классы полностью обработаны**. Такая отложенная обработка критически важна: она гарантирует, что пользовательские бины уже зарегистрированы к тому моменту, когда начинают применяться автоконфигурации. Именно поэтому `@ConditionalOnMissingBean` работает корректно — условие проверяется после регистрации пользовательских бинов, и автоконфигурация отступает, если нужный бин уже определён пользователем.

Автоконфигурации регистрируются в файле `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (в старых версиях — `META-INF/spring.factories`). `AutoConfigurationImportSelector` читает этот файл, загружает список кандидатов, отфильтровывает исключения (`spring.autoconfigure.exclude` или атрибут `exclude` у `@EnableAutoConfiguration`) и применяет дополнительные фильтры (`OnClassCondition` и т.д.) ещё до создания экземпляров конфигурационных классов.

Для упорядочивания автоконфигураций друг относительно друга используются аннотации `@AutoConfigureBefore`, `@AutoConfigureAfter`, `@AutoConfigureOrder` (или атрибуты `before`/`after` аннотации `@AutoConfiguration`). Важно: порядок влияет только на порядок **определения бинов**, но не на порядок их **создания**.

#### Ответ от Claude

**ImportSelector vs DeferredImportSelector: ключевое различие**

| Характеристика | ImportSelector | DeferredImportSelector |
|---|---|---|
| Момент запуска | В ходе обработки `@Configuration`-классов, сразу | После того, как все `@Configuration`-классы обработаны |
| Видимость пользовательских бинов | Ограничена — пользовательские классы могут ещё не быть разобраны | Полная — все пользовательские бины уже зарегистрированы |
| Подходит для условной логики на основе существующих бинов | Ненадёжно | Да, именно для этого и предназначен |

**Двухфазная регистрация бинов**

Использование `DeferredImportSelector` создаёт чёткие две фазы обработки контекста:

1. **Фаза пользовательской конфигурации.** Spring разбирает все `@Configuration`-классы приложения, регистрирует все `@Bean`-методы, обрабатывает `@Import` с обычными `ImportSelector`.

2. **Фаза автоконфигурации (отложенная).** `DeferredImportSelector.Group` собирает результаты всех отложенных селекторов, выполняет их групповую обработку. `AutoConfigurationImportSelector` читает `AutoConfiguration.imports`, исключает запрещённые классы, применяет фильтры по условиям (`@ConditionalOnClass` проверяется на уровне метаданных без загрузки классов), сортирует оставшихся кандидатов и передаёт их на импорт.

**Роль интерфейса Group**

`DeferredImportSelector` предоставляет метод `getImportGroup()`, возвращающий реализацию `DeferredImportSelector.Group`. Это позволяет координировать несколько отложенных селекторов: группировать их результаты, выполнять совместную сортировку и фильтрацию. `AutoConfigurationImportSelector` возвращает собственный внутренний класс `AutoConfigurationGroup`, который и агрегирует весь процесс: вызов `getAutoConfigurationEntry()` для каждого `@EnableAutoConfiguration`, дедупликацию, сортировку и финальный вызов `selectImports()`.

**Почему это важно на практике**

Именно отложенность и даёт возможность механизму `@ConditionalOnMissingBean` работать правильно. Если бы автоконфигурации загружались обычным `ImportSelector`, они могли бы применяться ещё до того, как пользовательский `@Configuration`-класс был разобран, и условие `@ConditionalOnMissingBean(DataSource.class)` проверялось бы при отсутствии пользовательского бина — даже если он будет определён чуть позже. `DeferredImportSelector` устраняет эту проблему структурно.

**Реализация `AutoConfigurationImportSelector` также:**
- реализует `BeanFactoryAware`, `EnvironmentAware`, `ResourceLoaderAware`, `BeanClassLoaderAware` для доступа к контексту при проверке условий;
- реализует `Ordered` (значение `LOWEST_PRECEDENCE - 1`) для контроля приоритета относительно других `DeferredImportSelector`;
- поддерживает наследование — класс можно расширить для создания собственного варианта `@EnableAutoConfiguration`.

---

