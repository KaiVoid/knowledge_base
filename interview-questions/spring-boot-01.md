# Spring Boot — часть 1 из 3

> Вопросы 1–20 (в части: 20). Всего в разделе: 50.
> Область знаний: [../knowledge-base/14-spring-boot.md](../knowledge-base/14-spring-boot.md)
> Правила: [RULES.md](RULES.md)
> Части: **ч.1** · [ч.2](spring-boot-02.md) · [ч.3](spring-boot-03.md)

---
### Вопрос 1. Что такое автоконфигурация в Spring Boot и как она работает?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html)

Автоконфигурация Spring Boot пытается автоматически настроить Spring-приложение на основе jar-зависимостей, добавленных в classpath. Например, если HSQLDB присутствует в classpath и вы не настроили вручную никаких бинов подключения к БД, Spring Boot автоматически конфигурирует базу данных в памяти.

Для включения автоконфигурации необходимо добавить аннотацию `@EnableAutoConfiguration` или `@SpringBootApplication` к одному из `@Configuration`-классов. При этом следует добавлять только одну из этих аннотаций к основному конфигурационному классу.

Автоконфигурация спроектирована как невмешивающаяся (non-invasive): вы в любой момент можете начать определять собственные бины, которые заменят конкретные части автоконфигурации. Например, если добавить собственный бин `DataSource`, встроенная поддержка базы данных отступает.

Для отладки применённых автоконфигураций можно запустить приложение с флагом `--debug` — в консоль будет выведен отчёт об условиях (Conditions Report).

#### Ответ от Claude

**Что такое автоконфигурация**

Автоконфигурация (auto-configuration) — механизм Spring Boot, который автоматически регистрирует бины в контексте приложения на основе того, какие jar-зависимости находятся в classpath, какие бины уже определены пользователем и какие свойства установлены в `application.properties`/`application.yml`. Цель — убрать рутинную конфигурацию: разработчик добавил зависимость — Spring Boot сам догадался, что нужно настроить.

**Как это работает — пошагово**

1. **Аннотация `@EnableAutoConfiguration`** (входит в `@SpringBootApplication`) активирует механизм загрузки классов автоконфигурации.

2. **Реестр автоконфигураций.** Spring Boot читает файл-манифест внутри артефакта `spring-boot-autoconfigure.jar`:
   - В Spring Boot 3.x (современный подход): `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
   - В Spring Boot до 2.7 (устаревший подход, удалён в 3.0): `META-INF/spring.factories`
   
   Файл содержит перечень полных имён классов-автоконфигураций, по одному на строку.

3. **Оценка условий.** Каждый класс автоконфигурации помечен аннотацией `@AutoConfiguration` (мета-аннотация поверх `@Configuration`) и набором `@Conditional`-аннотаций, которые решают, применять ли данную конфигурацию:
   - `@ConditionalOnClass(DataSource.class)` — применить, только если класс присутствует в classpath;
   - `@ConditionalOnMissingBean(DataSource.class)` — применить, только если пользователь ещё не определил такой бин;
   - `@ConditionalOnProperty(name = "spring.datasource.url")` — применить, если свойство задано;
   - `@ConditionalOnWebApplication` — применить, если контекст является веб-приложением.

4. **Регистрация бинов.** Бины из конфигурационных классов, условия которых выполнились, добавляются в контекст приложения.

5. **Невмешивающийся принцип.** Как только пользователь объявляет собственный бин того же типа, условие `@ConditionalOnMissingBean` перестаёт выполняться и автоконфигурированный бин не создаётся. Пользователь всегда имеет приоритет.

**Отключение автоконфигурации**

```java
// через атрибут аннотации
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })

// через application.properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

**Отладка**

Запуск с `--debug` или `logging.level.org.springframework.boot.autoconfigure=DEBUG` выведет в консоль отчёт условий (Conditions Report): список применённых и отклонённых автоконфигураций с причинами.

---

### Вопрос 2. Из каких трёх аннотаций состоит @SpringBootApplication и что каждая из них делает?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Using the @SpringBootApplication Annotation :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/using-the-springbootapplication-annotation.html)

Аннотация `@SpringBootApplication` является удобной мета-аннотацией, объединяющей три аннотации Spring Boot в одно объявление:

1. **`@EnableAutoConfiguration`** — включает механизм автоконфигурации Spring Boot, который автоматически настраивает приложение на основе jar-зависимостей в classpath.

2. **`@ComponentScan`** — включает сканирование компонентов (`@Component` и производных) в пакете, где расположен класс приложения. Также обнаруживает классы, помеченные `@ConfigurationProperties`.

3. **`@SpringBootConfiguration`** — позволяет регистрировать дополнительные бины в контексте и импортировать дополнительные конфигурационные классы. Является альтернативой стандартной аннотации Spring `@Configuration` и помогает обнаруживать конфигурацию в интеграционных тестах.

Три аннотации не являются обязательными в составе `@SpringBootApplication`. При необходимости более тонкого управления их можно использовать по отдельности — например, отключить сканирование компонентов, сохранив автоконфигурацию.

#### Ответ от Claude

`@SpringBootApplication` — мета-аннотация-удобство (convenience annotation), которая заменяет собой одновременно три аннотации. Её исходный код выглядит примерно так:

```java
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = { ... })
public @interface SpringBootApplication { ... }
```

**1. `@SpringBootConfiguration`**

Специализация аннотации `@Configuration` из Spring Framework. Говорит Spring, что данный класс является источником определений бинов (через методы с `@Bean`). Отличие от обычной `@Configuration` — семантическая: пометка "это главная конфигурация Spring Boot приложения". Это также помогает механизму обнаружения конфигурации в интеграционных тестах (`@SpringBootTest` ищет класс с `@SpringBootConfiguration` как точку входа).

**2. `@EnableAutoConfiguration`**

Активирует механизм автоконфигурации Spring Boot. Читает реестр `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`, загружает перечисленные там классы и применяет те из них, условия которых (`@ConditionalOnClass`, `@ConditionalOnMissingBean` и т.д.) выполнились. Именно эта аннотация является ключевой «магией» Spring Boot.

**3. `@ComponentScan`**

Включает автоматическое сканирование пакетов для обнаружения компонентов. По умолчанию сканирует пакет самого класса-приложения и все его подпакеты. Обнаруживает классы с аннотациями `@Component`, `@Service`, `@Repository`, `@Controller`, `@RestController`, `@Configuration`, `@ConfigurationProperties` и регистрирует их как бины в контексте.

**Пример использования**

```java
// Использование мета-аннотации (рекомендуется)
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}

// Эквивалентная запись без мета-аннотации
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan
public class MyApplication { ... }
```

**Частичное использование**

Можно использовать аннотации по отдельности для тонкой настройки — например, ограничить сканирование определёнными пакетами или отключить автоконфигурацию для конкретного класса через атрибут `exclude` у `@SpringBootApplication`.

---

### Вопрос 3. Что такое Spring Boot Starter? Приведи примеры стартеров и объясни, зачем они нужны.

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Build Systems :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/build-systems.html)

Spring Boot Starters — это удобные дескрипторы зависимостей (convenient dependency descriptors), которые упрощают настройку проекта, объединяя связанные зависимости вместе. Они предоставляют решение в одном месте для включения всех необходимых Spring и сопутствующих технологий без необходимости вручную искать и конфигурировать отдельные зависимости.

Все официальные стартеры следуют соглашению об именовании: `spring-boot-starter-*`. Это помогает IDE предлагать автодополнение при поиске стартеров. Сторонние стартеры не должны начинаться с `spring-boot` и обычно следуют шаблону `thirdpartyproject-spring-boot-starter`.

Примеры стартеров:
- `spring-boot-starter` — базовый стартер: автоконфигурация, логирование, YAML
- `spring-boot-starter-web` — Spring MVC и встроенный Tomcat
- `spring-boot-starter-webflux` — реактивный веб с Reactor Netty
- `spring-boot-starter-data-jpa` — Spring Data JPA с Hibernate
- `spring-boot-starter-security` — Spring Security
- `spring-boot-starter-test` — тестирование с JUnit Jupiter, Hamcrest и Mockito
- `spring-boot-starter-actuator` — production-ready функции: мониторинг и управление

#### Ответ от Claude

**Что такое Spring Boot Starter**

Spring Boot Starter — это артефакт Maven/Gradle, который является исключительно агрегатором зависимостей: он не содержит собственного Java-кода, а только `pom.xml` (или `build.gradle`) с набором транзитивных зависимостей, нужных для конкретной технологии или задачи. Вместо того чтобы добавлять в проект 5–10 отдельных библиотек с подобранными совместимыми версиями, вы добавляете один стартер.

**Зачем нужны стартеры**

До появления стартеров разработчику нужно было вручную:
1. Найти все нужные зависимости (например, для JPA: hibernate-core, jakarta.persistence-api, spring-data-jpa, HikariCP и т.д.);
2. Подобрать совместимые версии (что само по себе нетривиально);
3. Добавить каждую в pom.xml и следить за обновлениями.

Стартеры решают эти проблемы:
- **Единая точка подключения** — одна строка в зависимостях;
- **Управляемые версии** — все транзитивные зависимости выверены на совместимость командой Spring;
- **Согласованность** — стандартный, поддерживаемый набор библиотек в экосистеме;
- **Синергия с автоконфигурацией** — стартер добавляет нужные классы в classpath, а автоконфигурация обнаруживает их через `@ConditionalOnClass` и настраивает бины.

**Примеры стартеров и что они включают**

| Стартер | Назначение | Ключевые зависимости |
|---|---|---|
| `spring-boot-starter` | Базовый (ядро) | spring-core, spring-boot-autoconfigure, logback, snakeyaml |
| `spring-boot-starter-web` | Веб-приложение (MVC) | spring-webmvc, spring-web, tomcat-embed, jackson-databind |
| `spring-boot-starter-webflux` | Реактивный веб | spring-webflux, reactor-netty |
| `spring-boot-starter-data-jpa` | Работа с БД через JPA | spring-data-jpa, hibernate-core, spring-jdbc |
| `spring-boot-starter-data-mongodb` | MongoDB | spring-data-mongodb, mongodb-driver |
| `spring-boot-starter-security` | Безопасность | spring-security-web, spring-security-config |
| `spring-boot-starter-test` | Тестирование | junit-jupiter, mockito, spring-test, assertj |
| `spring-boot-starter-actuator` | Мониторинг | spring-boot-actuator, micrometer |
| `spring-boot-starter-validation` | Валидация Bean | hibernate-validator, jakarta.validation-api |
| `spring-boot-starter-amqp` | Очереди сообщений | spring-amqp, spring-rabbit |

**Соглашение об именовании**

- Официальные стартеры Spring: `spring-boot-starter-{name}`
- Сторонние стартеры: `{name}-spring-boot-starter` (например, `mybatis-spring-boot-starter`)

Такое разделение позволяет избежать конфликта имён с официальными стартерами.

**Пример подключения в Maven**

```xml
<!-- Добавляет Spring MVC + встроенный Tomcat + Jackson -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Версия не указывается явно — она управляется через `spring-boot-starter-parent` или BOM `spring-boot-dependencies`.

---
### Вопрос 4. Чем Spring Boot отличается от классического Spring Framework? Что добавляет Boot поверх Spring?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Spring Boot — официальная документация (docs.spring.io)](https://docs.spring.io/spring-boot/)

Spring Boot помогает создавать **самостоятельные (stand-alone), production-ready** приложения на базе Spring, которые запускаются командой `java -jar` или разворачиваются как традиционный WAR. Главные цели:

- Обеспечить радикально более быстрый и доступный старт разработки на Spring.
- Предоставить разумные опinionated-умолчания, от которых легко отступить.
- Добавить нефункциональные возможности, востребованные в любых крупных проектах: встроенные серверы, метрики, health-checks, вынесенная конфигурация.
- Не требовать генерации кода и XML-конфигурации.

#### Ответ от Claude

**Spring Framework** — фундаментальный DI/IoC-контейнер и набор модулей (MVC, Data, Security и др.). При использовании классического Spring разработчик вручную:
- объявляет каждый бин через `@Configuration`-классы или XML;
- управляет версиями зависимостей в pom.xml/build.gradle;
- настраивает DispatcherServlet, DataSource, TransactionManager и т.д.;
- разворачивает WAR на внешний сервер приложений.

**Spring Boot** — расширение поверх Spring Framework, реализующее принцип "convention over configuration". Что добавляет:

| Возможность | Описание |
|---|---|
| **Auto-configuration** | Аннотация `@EnableAutoConfiguration` (входит в `@SpringBootApplication`) автоматически конфигурирует бины на основе jar-зависимостей в classpath. Например, если в classpath есть `spring-data-jpa` и JDBC-драйвер — Boot сам создаст `DataSource`, `EntityManagerFactory` и `TransactionManager`. Конфигурация реализована через `@Conditional`-бины и не применяется, если разработчик объявил собственный бин. |
| **Starter-зависимости** | Curated-наборы совместимых зависимостей: `spring-boot-starter-web`, `spring-boot-starter-data-jpa` и т.д. Устраняют необходимость вручную подбирать версии. |
| **Встроенный сервер** | Tomcat, Jetty или Undertow поставляются внутри fat-JAR; приложение запускается без внешнего сервера. |
| **Spring Boot Actuator** | Готовые HTTP-эндпоинты для мониторинга: `/actuator/health`, `/actuator/metrics`, `/actuator/info` и др. |
| **Externalized Configuration** | Поддержка `application.properties`/`application.yml`, переменных окружения, профилей и command-line аргументов с чётким порядком приоритетов. |
| **Developer Tools** | Модуль `spring-boot-devtools` обеспечивает hot reload при разработке. |
| **Native Image** | Поддержка GraalVM AOT-компиляции в нативный бинарник (Spring Boot 3+). |

Ключевой принцип: `@SpringBootApplication` = `@Configuration` + `@ComponentScan` + `@EnableAutoConfiguration`. Одна аннотация заменяет типичный XML-бойлерплейт классического Spring.

Отключить конкретную авто-конфигурацию можно явно:
```java
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
```

---

### Вопрос 5. Что такое встроенный (embedded) сервер в Spring Boot? Какие серверы поддерживаются и как заменить Tomcat на Jetty?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Embedded Web Servers — Spring Boot Reference Documentation (docs.spring.io)](https://docs.spring.io/spring-boot/3.5/how-to/webserver.html)

Spring Boot поддерживает встроенные веб-серверы. По умолчанию `spring-boot-starter-web` включает Tomcat. Чтобы переключиться на Jetty, нужно исключить Tomcat и добавить стартер Jetty.

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
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

Gradle:
```gradle
dependencies {
    implementation('org.springframework.boot:spring-boot-starter-web') {
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-tomcat'
    }
    implementation 'org.springframework.boot:spring-boot-starter-jetty'
}
```

#### Ответ от Claude

**Встроенный (embedded) сервер** — это HTTP-сервер, упакованный непосредственно в fat-JAR приложения. Приложение запускается как обычная Java-программа (`java -jar app.jar`) без предварительной установки и настройки внешнего сервера приложений (Tomcat/JBoss/WebLogic). Это упрощает деплой, контейнеризацию и CI/CD.

**Поддерживаемые серверы** (актуально для Spring Boot 3.x):

| Стек | Сервер по умолчанию | Альтернативы |
|---|---|---|
| Servlet (`spring-boot-starter-web`) | **Tomcat** | Jetty, Undertow |
| Reactive (`spring-boot-starter-webflux`) | **Reactor Netty** | Tomcat, Jetty, Undertow |

Для каждого сервера предусмотрены отдельные factory-классы (`TomcatServletWebServerFactory`, `JettyServletWebServerFactory`, `UndertowServletWebServerFactory`, `NettyReactiveWebServerFactory`), через которые выполняется тонкая настройка через `WebServerFactoryCustomizer`.

**Замена Tomcat на Jetty (Maven):**
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

**Замена Tomcat на Jetty (Gradle):**
```gradle
dependencies {
    implementation('org.springframework.boot:spring-boot-starter-web') {
        exclude group: 'org.springframework.boot', module: 'spring-boot-starter-tomcat'
    }
    implementation 'org.springframework.boot:spring-boot-starter-jetty'
}
```

**Важные нюансы:**
- Если приложение использует `WebClient` (реактивный клиент), зависимость `spring-boot-starter-reactor-netty` может потребоваться в classpath даже при использовании Undertow/Jetty в качестве серверного контейнера.
- Для WAR-деплоя на внешний сервер стартер встроенного сервера помечается как `provided`, чтобы не попасть в финальный WAR.
- Undertow обычно показывает лучшую производительность при высокой конкурентности за счёт неблокирующей архитектуры на основе XNIO.

---

### Вопрос 6. Какой файл конфигурации использует Spring Boot по умолчанию? В чём разница между application.properties и application.yml?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration — Spring Boot Reference Documentation (docs.spring.io)](https://docs.spring.io/spring-boot/reference/features/external-config.html)

Spring Boot автоматически находит и загружает файлы `application.properties` и `application.yaml` из следующих мест (в порядке возрастания приоритета):

1. Корень classpath
2. Пакет `config/` в classpath
3. Текущая директория файловой системы
4. Поддиректория `config/` текущей директории
5. Непосредственные дочерние директории `config/`

Значения из позиций с более высоким приоритетом переопределяют значения из более ранних. Если в одном месте присутствуют и `.properties`, и `.yaml` — **`.properties` имеет приоритет**.

> "It is recommended to stick with one format for your entire application. If you have configuration files with both `.properties` and YAML format in the same location, `.properties` takes precedence."

#### Ответ от Claude

**Файл по умолчанию:** `application.properties` (или `application.yml`) в директории `src/main/resources/`. Spring Boot загружает его автоматически без какой-либо аннотации.

**Сравнение форматов:**

| Характеристика | application.properties | application.yml |
|---|---|---|
| Синтаксис | Плоские ключ-значение с точечной нотацией | Иерархический YAML с отступами |
| Читаемость | Простой для коротких конфигов | Нагляднее при глубокой вложенности |
| Типы данных | Все значения — строки (явное приведение) | Сохраняет типы: boolean, integer, list и др. |
| Профили | Отдельные файлы: `application-dev.properties` | Все профили в одном файле через разделитель `---` |
| Поддержка `@PropertySource` | Да | Нет (YAML не поддерживается `@PropertySource`) |
| Списки | `key[0]=val` / `key=a,b,c` | `-` нотация YAML |
| Многоязычность | Только Java/JVM | Широко используется в разных экосистемах |

**Пример одной конфигурации в двух форматах:**

application.properties:
```properties
spring.application.name=myapp
spring.datasource.url=jdbc:postgresql://localhost/db
spring.datasource.username=admin
server.port=8080
```

application.yml:
```yaml
spring:
  application:
    name: myapp
  datasource:
    url: jdbc:postgresql://localhost/db
    username: admin
server:
  port: 8080
```

**Профили в YAML (в одном файле):**
```yaml
spring:
  application:
    name: myapp
---
spring:
  config:
    activate:
      on-profile: dev
server:
  port: 8081
---
spring:
  config:
    activate:
      on-profile: prod
server:
  port: 80
```

**Приоритет при одновременном использовании:** если оба файла присутствуют в одном месте, `application.properties` переопределяет `application.yml`. Официальная документация рекомендует придерживаться одного формата во всём проекте, чтобы избежать путаницы.

**Порядок загрузки источников конфигурации** (по убыванию приоритета, частичный список):
1. Аргументы командной строки
2. Переменные окружения OS
3. Профильные файлы (`application-{profile}.properties`)
4. Стандартный `application.properties` / `application.yml`
5. Значения по умолчанию (`SpringApplication.setDefaultProperties`)
### Вопрос 7. Что такое профили (profiles) в Spring Boot? Как активировать конкретный профиль?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Profiles :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/profiles.html)

Spring-профили — это механизм, позволяющий разделять конфигурацию приложения и делать её доступной только в определённых окружениях. Любой компонент `@Component`, `@Configuration` или `@ConfigurationProperties` можно пометить аннотацией `@Profile`, и он будет загружаться только при активном соответствующем профиле.

Активировать профиль можно несколькими способами:
- В `application.properties`: `spring.profiles.active=dev,hsqldb`
- В командной строке: `java -jar app.jar --spring.profiles.active=dev`
- Программно через `SpringApplication.setAdditionalProfiles("dev")`

Для профиль-специфичных конфигурационных файлов используется соглашение об именовании `application-{profile}.properties` (или `.yaml`). Помимо этого, можно группировать профили с помощью `spring.profiles.group`.

#### Ответ от Claude

**Что такое профили**

Spring Boot профили — это способ разделить конфигурацию приложения по окружениям (dev, test, staging, prod) и активировать только нужную её часть. Профиль — это именованный логический контекст, который влияет на то, какие бины и настройки будут загружены.

**Определение компонентов для конкретного профиля**

```java
@Configuration(proxyBeanMethods = false)
@Profile("production")
public class ProductionConfiguration {
    // Загружается только при активном профиле "production"
}
```

**Способы активации профиля**

1. **application.properties / application.yaml**
   ```properties
   spring.profiles.active=dev,hsqldb
   ```
   Позволяет задать несколько активных профилей через запятую.

2. **Переменная окружения ОС**
   ```bash
   export SPRING_PROFILES_ACTIVE=production
   ```

3. **Аргумент командной строки**
   ```bash
   java -jar app.jar --spring.profiles.active=production
   ```
   Командная строка имеет наивысший приоритет и перекрывает настройки из файлов.

4. **Системное свойство JVM**
   ```bash
   java -Dspring.profiles.active=production -jar app.jar
   ```

5. **Программный способ**
   ```java
   SpringApplication app = new SpringApplication(MyApplication.class);
   app.setAdditionalProfiles("dev", "hsqldb");
   app.run(args);
   ```

6. **В тестах — аннотация `@ActiveProfiles`**
   ```java
   @SpringBootTest
   @ActiveProfiles("test")
   public class MyApplicationTests { ... }
   ```

**Профиль-специфичные файлы конфигурации**

При активном профиле `dev` Spring Boot автоматически загружает `application-dev.properties` (или `application-dev.yaml`) поверх базового `application.properties`. Это позволяет переопределять отдельные свойства без дублирования всего файла.

**Профиль по умолчанию**

Если не активирован ни один профиль, применяется профиль с именем `default`. Его можно переопределить свойством `spring.profiles.default`.

**Группировка профилей (Spring Boot 2.4+)**

```properties
spring.profiles.group.production[0]=proddb
spring.profiles.group.production[1]=prodmq
```

Активация `production` автоматически активирует `proddb` и `prodmq`.

**Важное ограничение:** `spring.profiles.active` и `spring.profiles.default` нельзя использовать внутри профиль-специфичных файлов конфигурации — только в основных.

---

### Вопрос 8. Что такое Spring Boot Actuator и какие эндпоинты он предоставляет из коробки?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

Spring Boot Actuator предоставляет готовые к production эндпоинты для мониторинга и управления приложением. По умолчанию все эндпоинты кроме `shutdown` включены (`enabled`), однако по HTTP и JMX из коробки экспонируется только эндпоинт `health`. Дополнительные эндпоинты открываются через свойство `management.endpoints.web.exposure.include`.

Среди встроенных эндпоинтов: `beans`, `caches`, `conditions`, `configprops`, `env`, `flyway`, `health`, `info`, `loggers`, `liquibase`, `metrics`, `mappings`, `scheduledtasks`, `sessions`, `shutdown`, `threaddump` и веб-специфичные: `heapdump`, `logfile`, `prometheus`.

#### Ответ от Claude

**Что такое Spring Boot Actuator**

Spring Boot Actuator — это модуль, добавляющий в приложение набор готовых эндпоинтов для мониторинга, управления и диагностики в production-среде. Подключается добавлением зависимости:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

После добавления все эндпоинты доступны по префиксу `/actuator` (например, `/actuator/health`).

**Полный список встроенных technology-agnostic эндпоинтов**

| ID | Описание |
|----|----------|
| `auditevents` | Информация об аудит-событиях (требует `AuditEventRepository`) |
| `beans` | Список всех Spring-бинов в контексте |
| `caches` | Доступные кэши |
| `conditions` | Отчёт об условиях применения авто-конфигурации |
| `configprops` | Все `@ConfigurationProperties` |
| `env` | Свойства из `ConfigurableEnvironment` |
| `flyway` | Применённые Flyway-миграции |
| `health` | Информация о состоянии приложения |
| `httpexchanges` | Последние HTTP-обмены (требует `HttpExchangeRepository`) |
| `info` | Произвольная информация о приложении |
| `integrationgraph` | Граф Spring Integration |
| `loggers` | Просмотр и изменение уровней логирования |
| `liquibase` | Применённые Liquibase-миграции |
| `metrics` | Метрики приложения (Micrometer) |
| `mappings` | Все `@RequestMapping`-пути |
| `quartz` | Задачи Quartz Scheduler |
| `scheduledtasks` | Запланированные задачи |
| `sessions` | Управление пользовательскими сессиями (требует Spring Session) |
| `shutdown` | Graceful-остановка приложения |
| `startup` | Данные о шагах запуска |
| `threaddump` | Thread dump |

**Дополнительные веб-специфичные эндпоинты**

| ID | Описание |
|----|----------|
| `heapdump` | Heap dump в формате HPROF |
| `logfile` | Содержимое лог-файла |
| `prometheus` | Метрики в формате Prometheus |

**Что включено и что экспонировано по умолчанию**

- **Включены (`enabled`):** все эндпоинты, кроме `shutdown` (он выключен из соображений безопасности).
- **Экспонированы по HTTP:** только `health`.
- **Экспонированы по JMX:** только `health` (начиная с Spring Boot 3.x; в 2.x по JMX экспонировалось большинство эндпоинтов).

**Расширение экспозиции**

```properties
# Открыть все эндпоинты по HTTP
management.endpoints.web.exposure.include=*

# Открыть только конкретные
management.endpoints.web.exposure.include=health,info,metrics

# Включить эндпоинт shutdown
management.endpoint.shutdown.enabled=true
```

**Важно:** перед открытием эндпоинтов в production убедитесь, что они защищены Spring Security, так как некоторые (например, `env`, `configprops`) могут раскрывать чувствительные данные.

---

### Вопрос 9. Как отключить конкретную автоконфигурацию, если она мешает работе приложения?

**Категория:** Spring Boot · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html)

Spring Boot предоставляет три способа исключить нежелательную авто-конфигурацию.

1. Атрибут `exclude` аннотации `@SpringBootApplication` (или `@EnableAutoConfiguration`) — передаётся ссылка на класс:
```java
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class MyApplication { }
```

2. Атрибут `excludeName` — используется, когда класс недоступен в classpath, передаётся полное имя класса строкой.

3. Свойство `spring.autoconfigure.exclude` в `application.properties`:
```properties
spring.autoconfigure.exclude=org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration
```

Можно комбинировать аннотационный и property-подходы одновременно.

#### Ответ от Claude

**Почему может потребоваться отключение авто-конфигурации**

Spring Boot авто-конфигурация срабатывает по условиям (`@ConditionalOnClass`, `@ConditionalOnMissingBean` и т.д.). Иногда наличие нужной библиотеки в classpath запускает конфигурацию, которая конфликтует с кастомной настройкой или просто не нужна в данном контексте.

**Способ 1: атрибут `exclude` аннотации (рекомендуемый)**

```java
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

Если не используется `@SpringBootApplication`, то же самое работает через `@EnableAutoConfiguration`:

```java
@Configuration
@EnableAutoConfiguration(exclude = { DataSourceAutoConfiguration.class })
public class MyConfiguration { }
```

Преимущество: IDE сигнализирует об ошибке, если класс не существует (compile-time safety).

**Способ 2: атрибут `excludeName`**

Используется, когда нужный класс авто-конфигурации отсутствует в classpath (например, при условном включении зависимости):

```java
@SpringBootApplication(
    excludeName = {
        "org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration"
    }
)
public class MyApplication { }
```

**Способ 3: свойство `spring.autoconfigure.exclude`**

Позволяет управлять исключениями без изменения кода — удобно для разных окружений:

```properties
# application.properties
spring.autoconfigure.exclude=\
  org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration,\
  org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration
```

Или в YAML:
```yaml
spring:
  autoconfigure:
    exclude:
      - org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration
      - org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration
```

**Как узнать, какая авто-конфигурация применяется**

Перед отключением полезно посмотреть, что именно применяется и почему. Эндпоинт Actuator `/actuator/conditions` (или старый `/actuator/autoconfig`) показывает полный отчёт о применённых и не применённых авто-конфигурациях с указанием условий.

**Совет:** прежде чем исключать авто-конфигурацию, проверьте, не решается ли проблема объявлением собственного бина — многие авто-конфигурации применяют `@ConditionalOnMissingBean` и автоматически отступают, если вы определили свой бин.
### Вопрос 10. Как Spring Boot определяет, какие автоконфигурации нужно применить? Какой файл (или механизм) отвечает за регистрацию автоконфигурационных классов?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Spring Boot проверяет наличие файла `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` внутри опубликованного JAR. В этом файле перечислены автоконфигурационные классы — по одному полностью квалифицированному имени класса на строку. Комментарии поддерживаются через символ `#`. Автоконфигурационные классы обнаруживаются с помощью механизма `ImportCandidates`, который читает этот файл.

До Spring Boot 3 аналогичную роль выполнял файл `META-INF/spring.factories`, где классы регистрировались под ключом `org.springframework.boot.autoconfigure.EnableAutoConfiguration`. Этот механизм считается устаревшим (deprecated) начиная со Spring Boot 2.7, а в Spring Boot 3 поддержка через `spring.factories` для автоконфигураций полностью убрана в пользу нового файла `.imports`.

Автоконфигурационные классы помечаются аннотацией `@AutoConfiguration` (мета-аннотирована через `@Configuration`, всегда с `proxyBeanMethods = false`). Для управления порядком применения используются атрибуты `before`, `after`, `beforeName`, `afterName` аннотации `@AutoConfiguration` либо отдельные аннотации `@AutoConfigureBefore` / `@AutoConfigureAfter`.

#### Ответ от Claude

**Механизм обнаружения автоконфигураций в Spring Boot**

При запуске приложения аннотация `@SpringBootApplication` включает `@EnableAutoConfiguration`, которая через `AutoConfigurationImportSelector` запускает процесс загрузки автоконфигураций.

**Регистрирующий файл (Spring Boot 3.x и новее):**
```
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```
Формат — обычный текст, одно полностью квалифицированное имя класса на строку:
```
com.mycorp.libx.autoconfigure.LibXAutoConfiguration
com.mycorp.libx.autoconfigure.LibXWebAutoConfiguration
```
Классы читаются утилитой `ImportCandidates` через `ClassLoader.getResources()`.

**Легаси-механизм (Spring Boot 2.x и старше):**
```
META-INF/spring.factories
```
Формат properties-файла:
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.mycorp.libx.autoconfigure.LibXAutoConfiguration,\
  com.mycorp.libx.autoconfigure.LibXWebAutoConfiguration
```
Начиная со Spring Boot 2.7 этот способ помечен как deprecated; в Spring Boot 3.0 для автоконфигураций он уже не поддерживается.

**Порядок применения автоконфигураций:**

1. Spring Boot сканирует classpath на наличие `META-INF/spring/…AutoConfiguration.imports` во всех JAR-файлах.
2. Формирует список кандидатов из всех найденных файлов.
3. Для каждого класса вычисляет условия (`@Conditional*`): если все условия выполнены — класс применяется.
4. Применяет конфигурации в определённом порядке с учётом `before`/`after` зависимостей.

**Аннотация автоконфигурационного класса:**
```java
@AutoConfiguration(after = DataSourceAutoConfiguration.class)
@ConditionalOnClass(JdbcTemplate.class)
public class JdbcTemplateAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}
```

**Важно:** автоконфигурационные классы не должны попадать под `@ComponentScan`, иначе они будут загружены дважды. Файл `.imports` обеспечивает изолированную регистрацию.

---

### Вопрос 11. Какие условные аннотации (@Conditional*) используются в автоконфигурации? Приведи примеры @ConditionalOnClass, @ConditionalOnMissingBean и объясни их поведение.

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ConditionalOnMissingBean (Spring Boot API)](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/autoconfigure/condition/ConditionalOnMissingBean.html)

`@ConditionalOnMissingBean` — условие, которое выполняется только тогда, когда в `BeanFactory` ещё нет бинов, удовлетворяющих указанным требованиям. Когда аннотация размещена на методе `@Bean` и не указаны атрибуты `value()`, `type()`, `name()` или `annotation()`, тип бина для проверки по умолчанию берётся из возвращаемого типа метода `@Bean`. Условие можно считать совпавшим, если ни одно из требований не выполнено. Настоятельно рекомендуется использовать эту аннотацию только в автоконфигурационных классах — порядок обработки бин-определений принципиально важен.

`@ConditionalOnClass` использует **ASM** для разбора метаданных аннотаций без загрузки класса в JVM — это позволяет безопасно ссылаться на класс через атрибут `value`, даже если он отсутствует в classpath. При использовании на методе `@Bean` следует помнить, что JVM загрузит тип возвращаемого значения до вычисления условия — поэтому рекомендуется выносить такой `@Bean` во вложенный `@Configuration` класс.

#### Ответ от Claude

**Основные условные аннотации Spring Boot**

Все они являются частью пакета `org.springframework.boot.autoconfigure.condition` и реализованы через механизм `@Conditional` из Spring Framework.

**1. `@ConditionalOnClass` / `@ConditionalOnMissingClass`**

Условие выполняется, если указанный класс **присутствует** (или **отсутствует**) в classpath.

Ключевая деталь: Spring использует ASM (Apache Commons Bytecode) для чтения метаданных аннотаций без реальной загрузки класса. Поэтому атрибут `value` безопасно принимает `SomeClass.class`, даже если этого класса нет в classpath.

```java
// Применяет конфигурацию только если Jackson есть в classpath
@AutoConfiguration
@ConditionalOnClass(ObjectMapper.class)
public class JacksonAutoConfiguration {
    // ...
}
```

**Осторожно с @Bean-методами:** JVM загружает тип возвращаемого значения до вычисления условия, что вызовет `ClassNotFoundException`. Решение — вложенный конфигурационный класс:

```java
@AutoConfiguration
public class MyAutoConfiguration {
    @Configuration(proxyBeanMethods = false)
    @ConditionalOnClass(SomeService.class)
    static class SomeServiceConfig {
        @Bean
        @ConditionalOnMissingBean
        SomeService someService() {
            return new SomeService();
        }
    }
}
```

**2. `@ConditionalOnMissingBean` / `@ConditionalOnBean`**

`@ConditionalOnMissingBean` — условие выполняется, если бин указанного типа **ещё не зарегистрирован** в `ApplicationContext`. `@ConditionalOnBean` — обратное.

```java
@Bean
@ConditionalOnMissingBean  // тип для проверки = возвращаемый тип метода = DataSource
public DataSource dataSource() {
    return new EmbeddedDatabaseBuilder().build();
}
```

```java
// Явное указание типа
@Bean
@ConditionalOnMissingBean(CacheManager.class)
public CacheManager cacheManager() {
    return new ConcurrentMapCacheManager();
}
```

**Важное ограничение:** условие оценивается относительно уже обработанных определений бинов. Поэтому рекомендуется применять только в автоконфигурационных классах, которые загружаются **после** пользовательского кода.

**3. `@ConditionalOnProperty`**

```java
@Bean
@ConditionalOnProperty(name = "myapp.feature.enabled", havingValue = "true", matchIfMissing = false)
public FeatureService featureService() { ... }
```

**4. `@ConditionalOnWebApplication` / `@ConditionalOnNotWebApplication`**

Условие на тип приложения: SERVLET, REACTIVE или ANY.

**5. `@ConditionalOnExpression`**

Использует SpEL-выражение:
```java
@ConditionalOnExpression("${myapp.enabled:true} and ${myapp.debug:false}")
```

**6. `@ConditionalOnResource`**

```java
@ConditionalOnResource(resources = "classpath:application.properties")
```

**Типичный паттерн в автоконфигурации:**
```java
@AutoConfiguration
@ConditionalOnClass(RedisOperations.class)      // Redis в classpath?
@ConditionalOnProperty(name = "spring.data.redis.host")  // свойство задано?
public class RedisAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean(RedisConnectionFactory.class)  // нет кастомного бина?
    public RedisConnectionFactory redisConnectionFactory(...) { ... }
}
```

---

### Вопрос 12. В чём разница между @ConfigurationProperties и @Value? Когда предпочтительнее использовать @ConfigurationProperties?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)

Использование аннотации `@Value("${property}")` для инъекции конфигурационных свойств может быть неудобным, особенно при работе с множеством свойств или иерархическими данными. Spring Boot предоставляет альтернативный подход — строго типизированные бины, управляющие конфигурацией приложения.

`@ConfigurationProperties` поддерживает **relaxed binding** (гибкое сопоставление имён): одно свойство `my.main-project.person.first-name` из источника может быть связано с полем `firstName` через camelCase, `first-name` через kebab-case, `first_name` через underscore, либо через переменную окружения `MY_MAINPROJECT_PERSON_FIRSTNAME`. `@Value`, в отличие от этого, требует точного совпадения имени.

Также `@ConfigurationProperties` поддерживает валидацию через `@Validated` и аннотации JSR-303, а SpEL-выражения в значениях свойств **не вычисляются** — это сделано намеренно, так как конфигурация должна быть внешней. `@Value` же полностью поддерживает SpEL.

#### Ответ от Claude

**Сравнение `@ConfigurationProperties` и `@Value`**

| Характеристика | `@ConfigurationProperties` | `@Value` |
|---|---|---|
| Число свойств | Группа связанных свойств | Одно свойство |
| Типобезопасность | Строгая (POJO) | Слабая (строки с конвертацией) |
| Relaxed binding | Да (kebab, camelCase, UPPER_SNAKE) | Нет (точное совпадение) |
| Валидация (JSR-303) | Да (`@Validated` + `@NotNull` и др.) | Нет |
| SpEL-выражения | Нет | Да |
| Иерархические данные | Отлично (вложенные объекты, List, Map) | Неудобно |
| IDE автодополнение | Да (через `spring-configuration-metadata.json`) | Ограничено |
| Применимость | Класс или метод `@Bean` | Поле, параметр, метод |

**`@ConfigurationProperties` — пример:**
```java
@ConfigurationProperties(prefix = "app.mail")
@Validated
public class MailProperties {
    @NotEmpty
    private String host;
    private int port = 25;
    private String username;
    private String password;
    private List<String> defaultRecipients = new ArrayList<>();
    private Map<String, String> additionalHeaders = new HashMap<>();

    // getters/setters или record-стиль в Spring Boot 3+
}
```
```yaml
# application.yml
app:
  mail:
    host: smtp.example.com
    port: 587
    default-recipients:
      - admin@example.com
    additional-headers:
      X-Priority: "1"
```
```java
@Service
public class MailService {
    private final MailProperties props;
    public MailService(MailProperties props) { this.props = props; }
}
```

Для активации `@ConfigurationProperties` нужно либо пометить класс `@Component`, либо использовать `@EnableConfigurationProperties(MailProperties.class)` на конфигурационном классе.

**`@Value` — пример:**
```java
@Component
public class AppInfo {
    @Value("${app.name}")
    private String name;

    @Value("${app.timeout:30}")          // значение по умолчанию
    private int timeout;

    @Value("#{T(Math).PI}")              // SpEL-выражение
    private double pi;

    @Value("${app.feature.enabled:false}")
    private boolean featureEnabled;
}
```

**Когда предпочтительнее `@ConfigurationProperties`:**

1. **Группа связанных свойств** — несколько полей одного раздела конфигурации логично объединить в один POJO.
2. **Иерархические и коллекционные данные** — List, Map, вложенные объекты.
3. **Нужна валидация** — `@Validated` + аннотации JSR-303 (`@NotNull`, `@Min`, `@Email`).
4. **Переиспользование** — один объект `MailProperties` инжектируется в несколько сервисов.
5. **IDE-поддержка** — модуль `spring-boot-configuration-processor` генерирует метаданные для автодополнения в `application.yml`.
6. **Строгость** — relaxed binding упрощает конфигурирование через переменные окружения в Docker/Kubernetes.

**Когда `@Value` допустим:**

1. Одно простое скалярное свойство.
2. Нужно SpEL-выражение (`@Value("#{systemProperties['user.home']}")`).
3. Быстрый прототип или легаси-код, где создавать POJO избыточно.

**Рекомендация Spring:** использовать `@ConfigurationProperties` как основной подход и прибегать к `@Value` только для единичных свойств или там, где нужен SpEL.
### Вопрос 13. Как работает @ConfigurationProperties: как привязать группу свойств из application.yml к Java-объекту? Что нужно сделать, чтобы она заработала?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)

`@ConfigurationProperties` — аннотация Spring Boot для типобезопасного связывания внешней конфигурации с Java-объектом. Вместо множества `@Value`-аннотаций она позволяет сгруппировать связанные свойства в единый объект.

**Шаги для использования:**

1. Объявить класс-носитель и пометить его `@ConfigurationProperties("prefix")`, где `prefix` — общий префикс свойств в файле конфигурации.
2. Зарегистрировать класс в контексте одним из двух способов:
   - `@EnableConfigurationProperties(MyProperties.class)` — в `@Configuration`-классе (явная регистрация конкретных классов);
   - `@ConfigurationPropertiesScan` — на главном классе приложения (автосканирование пакета).
3. В самом классе-носителе добавить геттеры и сеттеры (JavaBean-binding) **или** написать конструктор (constructor binding — начиная с Spring Boot 2.2+).

**Пример:**

`application.yml`:
```yaml
my:
  service:
    enabled: true
    remote-address: 192.168.1.1
    security:
      username: "admin"
      password: "secret"
      roles:
        - "USER"
        - "ADMIN"
```

```java
@ConfigurationProperties("my.service")
public class MyProperties {
    private boolean enabled;
    private InetAddress remoteAddress;
    private final Security security = new Security();

    // getters + setters для enabled, remoteAddress
    public Security getSecurity() { return this.security; }

    public static class Security {
        private String username;
        private String password;
        private List<String> roles = new ArrayList<>(Collections.singleton("USER"));
        // getters + setters
    }
}
```

```java
@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties(MyProperties.class)
public class AppConfig {}
```

После этого `MyProperties` доступен для инъекции через `@Autowired` или конструктор.

#### Ответ от Claude

`@ConfigurationProperties` — механизм типобезопасной привязки (type-safe binding) свойств из `application.yml` / `application.properties` к полям Java-объекта. Он является предпочтительной альтернативой `@Value`, когда нужно работать с группой связанных настроек.

**Что происходит под капотом:** Spring Boot считывает файл конфигурации, выстраивает иерархическое дерево свойств и затем «расслабленно» (relaxed binding) сопоставляет ключи с полями класса. Расслабленное связывание означает, что `remote-address` в YAML совпадёт с полем `remoteAddress` в Java, а `REMOTE_ADDRESS` в переменной окружения — тоже совпадёт с тем же полем.

**Необходимые шаги:**

1. **Создать класс-носитель** с аннотацией `@ConfigurationProperties("prefix")`:
   ```java
   @ConfigurationProperties("my.service")
   public class MyServiceProperties {
       private boolean enabled;
       private String remoteAddress;
       // геттеры + сеттеры (для JavaBean-binding)
   }
   ```

2. **Зарегистрировать класс как бин** — одним из трёх способов:

   | Способ | Как использовать |
   |--------|-----------------|
   | `@EnableConfigurationProperties(MyServiceProperties.class)` | Добавить на `@Configuration`-класс; явно перечисляет нужные классы |
   | `@ConfigurationPropertiesScan` | Добавить на `@SpringBootApplication`; сканирует пакет автоматически |
   | `@Component` на самом классе-носителе | Наиболее простой вариант, но не рекомендуется в библиотеках |

3. **Настроить файл** `application.yml` с нужным префиксом:
   ```yaml
   my:
     service:
       enabled: true
       remote-address: 192.168.1.1
   ```

**Два стиля привязки:**

- **JavaBean binding** (Spring Boot 1.x+): класс с конструктором без аргументов + геттеры/сеттеры. Обязателен сеттер для каждого простого поля.
- **Constructor binding** (Spring Boot 2.2+): неизменяемый (immutable) класс. Поля `final`, связывание происходит через конструктор. Не требует сеттеров. Не может быть помечен `@Component`.

  ```java
  @ConfigurationProperties("my.service")
  public class MyServiceProperties {
      private final boolean enabled;
      private final String remoteAddress;

      public MyServiceProperties(boolean enabled, String remoteAddress) {
          this.enabled = enabled;
          this.remoteAddress = remoteAddress;
      }
      // только геттеры
  }
  ```

**Валидация:** класс можно пометить `@Validated` и использовать аннотации JSR-380 (`@NotNull`, `@Min`, `@Max` и т.д.) — при неверных значениях приложение не запустится:
```java
@ConfigurationProperties("my.service")
@Validated
public class MyServiceProperties {
    @NotNull
    private String remoteAddress;
    @Min(1) @Max(65535)
    private int port;
    // ...
}
```

**Поддержка IDE:** при наличии зависимости `spring-boot-configuration-processor` в `pom.xml` / `build.gradle` IDE генерирует автодополнение и документацию для свойств в `application.yml`.

---

### Вопрос 14. Как реализовать конфигурацию, специфичную для профиля, с помощью файлов application-{profile}.yml? Как Spring Boot выбирает нужный файл?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Profiles :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/profiles.html)

Spring Boot загружает профильные варианты конфигурационных файлов по шаблону `application-{profile}.properties` / `application-{profile}.yaml`. Активный профиль задаётся через свойство `spring.profiles.active`. Если ни один профиль не активирован явно, Spring Boot включает профиль по умолчанию с именем `default`.

Задать активный профиль можно несколькими способами:
- в `application.properties`: `spring.profiles.active=dev,hsqldb`
- в `application.yaml`: через ключ `spring.profiles.active: "dev,hsqldb"`
- через аргумент командной строки: `--spring.profiles.active=dev,hsqldb`
- через переменную окружения: `SPRING_PROFILES_ACTIVE=dev`

Профильные файлы всегда переопределяют базовые: свойства из `application-dev.yaml` имеют приоритет над свойствами из `application.yaml` при одном и том же ключе.

Spring Boot также поддерживает группы профилей:
```yaml
spring:
  profiles:
    group:
      production:
        - "proddb"
        - "prodmq"
```
Активация `production` автоматически активирует `proddb` и `prodmq`.

#### Ответ от Claude

**Принцип работы:**

При старте Spring Boot ищет файлы конфигурации по двум шаблонам:
- `application.yml` — базовая конфигурация (всегда загружается)
- `application-{profile}.yml` — профильная конфигурация (загружается, если профиль активен)

Оба файла загружаются и мерджатся; профильный файл имеет более высокий приоритет и переопределяет одноимённые ключи из базового.

**Как активировать профиль (5 способов, от наивысшего к наинизшему приоритету):**

| Способ | Пример |
|--------|--------|
| Аргумент командной строки | `--spring.profiles.active=prod` |
| Переменная окружения | `SPRING_PROFILES_ACTIVE=prod` |
| Java системное свойство | `-Dspring.profiles.active=prod` |
| В `application.yml` | `spring.profiles.active: prod` |
| По умолчанию (если ничего не задано) | Профиль `default` |

**Пример структуры файлов:**

```
src/main/resources/
  application.yml          # общие настройки
  application-dev.yml      # переопределения для разработки
  application-prod.yml     # переопределения для продакшн
  application-test.yml     # переопределения для тестов
```

`application.yml`:
```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
server:
  port: 8080
logging:
  level:
    root: INFO
```

`application-dev.yml`:
```yaml
server:
  port: 8081
logging:
  level:
    root: DEBUG
```

При запуске с `--spring.profiles.active=dev` результирующая конфигурация: порт `8081`, уровень логирования `DEBUG`, источник данных остаётся `h2` из базового файла.

**Несколько активных профилей:** можно активировать несколько профилей одновременно: `--spring.profiles.active=dev,feature-x`. Если оба файла определяют один и тот же ключ, побеждает **последний** в списке (в данном случае `feature-x`).

**Порядок загрузки файлов конфигурации** (от наинизшего к наивысшему приоритету):

1. `application.yml` внутри JAR-файла
2. `application-{profile}.yml` внутри JAR-файла
3. `application.yml` вне JAR-файла (например, рядом с JAR в файловой системе)
4. `application-{profile}.yml` вне JAR-файла

Файлы вне JAR всегда побеждают файлы внутри JAR — это позволяет переопределять конфигурацию при деплое без пересборки артефакта.

**Альтернатива — multi-document YAML:** несколько профильных конфигураций можно хранить в одном файле, разделяя документы `---` и используя `spring.config.activate.on-profile`:
```yaml
server:
  port: 8080
---
spring:
  config:
    activate:
      on-profile: "dev"
server:
  port: 8081
```

**Ограничение:** свойства `spring.profiles.active` и `spring.profiles.default` нельзя использовать внутри профильно-активируемых документов (секций с `spring.config.activate.on-profile`).

---

### Вопрос 15. Каков порядок приоритетов источников конфигурации в Spring Boot (аргументы командной строки, переменные окружения, application.yml и т.д.)?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Externalized Configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/external-config.html)

Spring Boot использует строго определённый порядок источников свойств (PropertySource order). Источники с более высоким номером в списке переопределяют источники с более низким номером. Полный список (от наинизшего к наивысшему приоритету):

1. Свойства по умолчанию (`SpringApplication.setDefaultProperties(Map)`)
2. Аннотации `@PropertySource` на `@Configuration`-классах
3. Данные конфигурации (`application.properties` / YAML)
4. `RandomValuePropertySource` (только свойства `random.*`)
5. Переменные окружения ОС
6. Java системные свойства (`System.getProperties()`)
7. JNDI-атрибуты из `java:comp/env`
8. `ServletContext` init parameters
9. `ServletConfig` init parameters
10. `SPRING_APPLICATION_JSON` (inline JSON в переменной окружения или системном свойстве)
11. Аргументы командной строки
12. Атрибут `properties` в тестах (`@SpringBootTest`)
13. Аннотации `@DynamicPropertySource` в тестах
14. Аннотации `@TestPropertySource` в тестах
15. Devtools-настройки в `$HOME/.config/spring-boot` (только при активном Devtools)

Внутри пункта 3 («данные конфигурации») действует собственная иерархия приоритетов:
1. Профильные файлы вне JAR (`application-{profile}.properties` / YAML)
2. Базовые файлы вне JAR (`application.properties` / YAML)
3. Профильные файлы внутри JAR
4. Базовые файлы внутри JAR

#### Ответ от Claude

Spring Boot реализует принцип «переопределяемой конфигурации»: каждый последующий источник в списке приоритетов может переопределить предыдущий. Это позволяет хранить разумные значения по умолчанию в JAR-файле, переопределять их переменными окружения на сервере, а в срочных ситуациях — аргументами командной строки.

**Полный порядок приоритетов** (по возрастанию — последующий переопределяет предыдущий):

| # | Источник | Типичное применение |
|---|---------|---------------------|
| 1 | `SpringApplication.setDefaultProperties()` | Встроенные умолчания приложения |
| 2 | `@PropertySource` на `@Configuration`-классах | Статические дополнительные файлы свойств |
| 3 | **Config data** (`application.yml` и др.) | Основная конфигурация (см. подпорядок ниже) |
| 4 | `RandomValuePropertySource` (`random.*`) | Генерация случайных значений |
| 5 | Переменные окружения ОС | Конфигурация в контейнерах / CI/CD |
| 6 | Java системные свойства (`-D...`) | Передача через JVM |
| 7 | JNDI-атрибуты (`java:comp/env`) | Java EE / Jakarta EE окружения |
| 8 | `ServletContext` init parameters | Параметры веб-контейнера |
| 9 | `ServletConfig` init parameters | Параметры сервлета |
| 10 | `SPRING_APPLICATION_JSON` | Inline JSON в переменной окружения |
| 11 | **Аргументы командной строки** (`--key=value`) | Быстрое ситуативное переопределение |
| 12 | `properties` в `@SpringBootTest` | Тесты |
| 13 | `@DynamicPropertySource` | Тесты (динамические свойства) |
| 14 | `@TestPropertySource` | Тесты (статические свойства) |
| 15 | Devtools `$HOME/.config/spring-boot` | Локальная разработка с Devtools |

**Подпорядок внутри Config data** (пункт 3, от наинизшего к наивысшему):

```
application.yml  внутри JAR
application-{profile}.yml  внутри JAR
application.yml  вне JAR
application-{profile}.yml  вне JAR
```

Это означает, что файл `application-prod.yml`, лежащий рядом с запускаемым JAR в файловой системе, имеет наивысший приоритет среди всех конфигурационных файлов.

**Практические следствия:**

- Аргументы командной строки (`--server.port=9090`) переопределяют **всё**, кроме тестовых механизмов и Devtools — это самый высокий «боевой» приоритет.
- Переменные окружения (`SERVER_PORT=9090`) переопределяют `application.yml`, что используется в Docker/Kubernetes для конфигурации без пересборки образа.
- `application.yml` внутри JAR — последний рубеж, базовые значения по умолчанию.
- `@PropertySource` обрабатывается **до** `application.yml`, поэтому он не может переопределить конфигурационные файлы — распространённое заблуждение.

**Важный момент про переменные окружения:** Spring Boot автоматически применяет relaxed binding для переменных окружения: `SPRING_DATASOURCE_URL` соответствует свойству `spring.datasource.url`. Разделитель `.` заменяется на `_`, имя приводится к верхнему регистру.
### Вопрос 16. Как закрыть (защитить) чувствительные эндпоинты Actuator? Как выборочно включить только нужные эндпоинты?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Endpoints :: Spring Boot](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)

По умолчанию, в Spring Boot, только эндпоинт `/health` доступен по HTTP без ограничений. Все остальные эндпоинты либо не раскрыты, либо защищены. Если Spring Security присутствует в classpath и не задан ни один кастомный `SecurityFilterChain`, то все эндпоинты, кроме `/health`, автоматически защищаются механизмами безопасности Spring Boot. Управление раскрытием эндпоинтов выполняется через свойства `management.endpoints.web.exposure.include` и `management.endpoints.web.exposure.exclude`. Свойство `exclude` имеет приоритет над `include`. Для тонкой настройки используется `management.endpoint.<id>.access`, где возможны значения `unrestricted`, `read-only` и `none`. Глобально ограничить максимальный уровень доступа для всех эндпоинтов можно через `management.endpoints.access.max-permitted`. Spring Boot предоставляет удобный класс `EndpointRequest` для создания `RequestMatcher` при настройке `SecurityFilterChain` — например, `EndpointRequest.toAnyEndpoint()` соответствует всем эндпоинтам Actuator. Для чувствительных значений (env, configprops) предусмотрено свойство `show-values` со значениями `never`, `always` и `when-authorized`.

#### Ответ от Claude

**Проблема безопасности Actuator**

Spring Boot Actuator предоставляет эндпоинты, раскрывающие внутреннее состояние приложения: переменные среды (`/env`), бины Spring-контекста (`/beans`), конфигурацию (`/configprops`), дамп кучи (`/heapdump`), логи (`/logfile`), управление логгерами (`/loggers`), остановку приложения (`/shutdown`). Компрометация этих эндпоинтов может привести к утечке секретов или удалённому управлению приложением.

---

**1. Управление раскрытием эндпоинтов (exposure)**

По умолчанию по HTTP доступен только `/health`. Все остальные эндпоинты не раскрыты:

```yaml
# Включить только конкретные эндпоинты
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics"

# Включить все, кроме особо чувствительных
management:
  endpoints:
    web:
      exposure:
        include: "*"
        exclude: "env,beans,heapdump,threaddump,shutdown"
```

Свойство `exclude` имеет приоритет над `include`. Символ `*` в YAML необходимо брать в кавычки.

---

**2. Управление доступом на уровне отдельных эндпоинтов**

Начиная со Spring Boot 3.4, введены более тонкие настройки доступа:

```yaml
management:
  # Запретить всё по умолчанию (стратегия deny-by-default)
  endpoints:
    access:
      default: none
  endpoint:
    health:
      access: unrestricted     # полный доступ
    metrics:
      access: read-only        # только GET-запросы
    loggers:
      access: unrestricted     # GET и POST (изменение уровней)
    shutdown:
      access: none             # полностью отключён
```

Глобальное ограничение максимального уровня:
```yaml
management:
  endpoints:
    access:
      max-permitted: read-only  # ни один эндпоинт не может иметь уровень выше read-only
```

---

**3. Защита через Spring Security**

Если Spring Security есть в classpath, но не задан кастомный `SecurityFilterChain`, Spring Boot применяет автоконфигурацию безопасности. Для полного контроля определяют собственный бин:

```java
@Configuration(proxyBeanMethods = false)
public class ActuatorSecurityConfig {

    @Bean
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        // EndpointRequest.toAnyEndpoint() — матчер для всех эндпоинтов Actuator
        http.securityMatcher(EndpointRequest.toAnyEndpoint());
        http.authorizeHttpRequests(requests -> requests
            .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
            .anyRequest().hasRole("ACTUATOR_ADMIN")
        );
        http.httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
```

Доступные матчеры:
- `EndpointRequest.toAnyEndpoint()` — все эндпоинты
- `EndpointRequest.to("health", "metrics")` — конкретные эндпоинты
- `EndpointRequest.toAnyEndpoint().excluding("env")` — все кроме указанных

---

**4. Вынос Actuator на отдельный порт**

Наиболее надёжный способ изоляции — отдельный порт, закрытый на уровне сети/firewall:

```yaml
management:
  server:
    port: 8081          # отдельный порт для Actuator
    address: 127.0.0.1  # только localhost (не доступен снаружи)
```

---

**5. Скрытие чувствительных значений**

Эндпоинты `/env` и `/configprops` могут раскрывать пароли и токены:

```yaml
management:
  endpoint:
    env:
      show-values: when-authorized  # never | always | when-authorized
      roles: "ADMIN"
    configprops:
      show-values: never
```

---

**6. Отключение discovery-страницы**

```yaml
management:
  endpoints:
    web:
      discovery:
        enabled: false  # скрыть /actuator (список доступных эндпоинтов)
```

---

**Рекомендованная production-конфигурация:**

```yaml
management:
  server:
    port: 8081
    address: 127.0.0.1
  endpoints:
    web:
      exposure:
        include: "health,info"
    access:
      default: none
  endpoint:
    health:
      access: unrestricted
      show-details: when-authorized
    info:
      access: unrestricted
```

> Важно: CSRF-защита Spring Security по умолчанию включена. Это означает, что POST/PUT/DELETE запросы к эндпоинтам (shutdown, loggers) будут возвращать 403 Forbidden при использовании стандартной конфигурации. Для не-браузерных клиентов (мониторинг, DevOps-инструменты) CSRF отключают в рамках `SecurityFilterChain`, ограниченного матчером `EndpointRequest`.

---

### Вопрос 17. Как создать собственный Spring Boot Starter? Что должно быть в META-INF/spring/ и как написать свой автоконфигурационный класс?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Согласно официальной документации Spring Boot 4.x, для регистрации автоконфигурации необходимо создать файл `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` в ресурсах JAR-файла. В файле указываются полностью квалифицированные имена классов автоконфигурации — по одному на строку. Поддерживаются комментарии через `#`. Для вложенных классов используется синтаксис с `$`. Классы автоконфигурации аннотируются `@AutoConfiguration` (мета-аннотация над `@Configuration`). Дополнительно используются `@Conditional`-аннотации для ограничения применения конфигурации: `@ConditionalOnClass` (класс присутствует в classpath), `@ConditionalOnMissingBean` (бин ещё не определён), `@ConditionalOnProperty` (свойство задано). Рекомендуется разделять библиотеку на два модуля: модуль автоконфигурации (`acme-spring-boot`) и модуль стартера (`acme-spring-boot-starter`), который является простым агрегатором зависимостей. До Spring Boot 2.7 вместо `AutoConfiguration.imports` использовался файл `META-INF/spring.factories`, который в Spring Boot 3.0 больше не поддерживается для регистрации автоконфигурации.

#### Ответ от Claude

**Концепция Spring Boot Starter**

Starter — это набор зависимостей и автоконфигурации, позволяющий добавить функциональность в Spring Boot приложение простым включением одной зависимости в `pom.xml`/`build.gradle`. Пример: `spring-boot-starter-data-redis` автоматически конфигурирует `RedisTemplate`, `RedisConnectionFactory` и т.д.

---

**Рекомендуемая структура модулей**

```
my-library-spring-boot-starter/          ← агрегатор зависимостей
my-library-spring-boot-autoconfigure/   ← автоконфигурация и бизнес-логика
```

Разделение обязательно, если автоконфигурация и стартер публикуются отдельно. Для небольших библиотек допустимо объединить в один модуль.

---

**Шаг 1. Файл регистрации автоконфигурации**

Путь: `src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

```
# Регистрация автоконфигурационных классов
com.example.mylib.autoconfigure.MyLibAutoConfiguration
com.example.mylib.autoconfigure.MyLibWebAutoConfiguration
```

> Это правило для Spring Boot 2.7+ и Spring Boot 3.x. В Spring Boot до 2.7 использовался файл `META-INF/spring.factories`:
> ```properties
> org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
>   com.example.mylib.autoconfigure.MyLibAutoConfiguration
> ```
> В Spring Boot 3.0 поддержка `spring.factories` для регистрации автоконфигурации была удалена.

---

**Шаг 2. Свойства конфигурации**

```java
@ConfigurationProperties(prefix = "mylib")
public class MyLibProperties {

    /** Включить ли библиотеку. По умолчанию true. */
    private boolean enabled = true;

    /** Таймаут подключения. */
    private Duration connectionTimeout = Duration.ofSeconds(5);

    /** URL сервиса. */
    private String serviceUrl = "http://localhost:8080";

    // getters и setters
}
```

---

**Шаг 3. Класс автоконфигурации**

```java
@AutoConfiguration
@ConditionalOnClass(MyLibClient.class)           // применять только если класс есть в classpath
@ConditionalOnProperty(
    prefix = "mylib",
    name = "enabled",
    havingValue = "true",
    matchIfMissing = true                         // применять если свойство не задано
)
@EnableConfigurationProperties(MyLibProperties.class)
public class MyLibAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean                     // не создавать если бин уже определён пользователем
    public MyLibClient myLibClient(MyLibProperties properties) {
        return new MyLibClient(
            properties.getServiceUrl(),
            properties.getConnectionTimeout()
        );
    }

    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnBean(MyLibClient.class)          // только если MyLibClient создан
    public MyLibService myLibService(MyLibClient client) {
        return new MyLibService(client);
    }
}
```

---

**Основные @Conditional аннотации**

| Аннотация | Условие активации |
|---|---|
| `@ConditionalOnClass` | Указанный класс присутствует в classpath |
| `@ConditionalOnMissingClass` | Указанный класс отсутствует в classpath |
| `@ConditionalOnBean` | Бин указанного типа уже создан |
| `@ConditionalOnMissingBean` | Бин указанного типа ещё не создан |
| `@ConditionalOnProperty` | Заданное свойство имеет нужное значение |
| `@ConditionalOnWebApplication` | Приложение является web-приложением |
| `@ConditionalOnNotWebApplication` | Приложение не является web-приложением |
| `@ConditionalOnExpression` | SpEL-выражение вычисляется в true |

---

**Шаг 4. pom.xml модуля автоконфигурации**

```xml
<dependencies>
    <!-- Обязательно: API для написания автоконфигурации -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-autoconfigure</artifactId>
    </dependency>

    <!-- Опционально: генерация метаданных для IDE-подсказок -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-configuration-processor</artifactId>
        <optional>true</optional>
    </dependency>

    <!-- Зависимость библиотеки как optional — не транзитивная -->
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>my-library</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

---

**Шаг 5. pom.xml модуля стартера (агрегатор)**

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>my-library-spring-boot-autoconfigure</artifactId>
    </dependency>
    <!-- Другие необходимые зависимости -->
</dependencies>
```

---

**Шаг 6. Тестирование автоконфигурации**

Spring Boot предоставляет `ApplicationContextRunner` для юнит-тестирования:

```java
class MyLibAutoConfigurationTest {

    private final ApplicationContextRunner contextRunner = new ApplicationContextRunner()
        .withConfiguration(AutoConfigurations.of(MyLibAutoConfiguration.class));

    @Test
    void clientIsCreatedByDefault() {
        contextRunner.run(context ->
            assertThat(context).hasSingleBean(MyLibClient.class)
        );
    }

    @Test
    void clientIsNotCreatedWhenDisabled() {
        contextRunner
            .withPropertyValues("mylib.enabled=false")
            .run(context ->
                assertThat(context).doesNotHaveBean(MyLibClient.class)
            );
    }

    @Test
    void userDefinedClientTakesPrecedence() {
        contextRunner
            .withUserConfiguration(UserConfig.class)
            .run(context ->
                assertThat(context).hasSingleBean(MyLibClient.class)
            );
    }

    @Configuration
    static class UserConfig {
        @Bean
        MyLibClient customClient() { return new MyLibClient("custom-url", Duration.ZERO); }
    }
}
```

---

**Именование модулей**

- Не называйте модули с префиксом `spring-boot-` — это зарезервировано для официальных стартеров Spring.
- Используйте схему: `{library-name}-spring-boot-starter` и `{library-name}-spring-boot-autoconfigure`.
- Не используйте пространство имён `org.springframework.boot` для своих пакетов.

---

### Вопрос 18. Можно ли запустить Spring Boot приложение как WAR-файл на внешнем сервере? Что нужно изменить по сравнению со стандартным JAR?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Traditional Deployment :: Spring Boot](https://docs.spring.io/spring-boot/how-to/deployment/traditional-deployment.html)

Официальная документация Spring Boot описывает следующий процесс развёртывания в виде WAR-файла. Первый шаг: главный класс приложения должен расширять `SpringBootServletInitializer` и переопределять метод `configure`. Этот класс использует поддержку Servlet 3.0 от Spring Framework и позволяет настроить приложение при запуске внешним контейнером сервлетов. Второй шаг: в `pom.xml` нужно изменить `<packaging>` с `jar` (значение по умолчанию) на `war`. Третий шаг: зависимость `spring-boot-starter-tomcat` должна быть помечена как `provided`, чтобы встроенный Tomcat не попал в WAR-файл. При использовании Gradle используется конфигурация `providedRuntime` вместо `implementation`. Важное ограничение: развёртывание WAR поддерживается только для Servlet-приложений; Spring WebFlux не поддерживает WAR-развёртывание, поскольку не основан на Servlet API.

#### Ответ от Claude

**Стандартный JAR vs WAR**

По умолчанию Spring Boot собирает «fat JAR» — исполняемый архив с встроенным сервером (Tomcat/Jetty/Undertow) и всеми зависимостями. Приложение запускается командой `java -jar app.jar`. При развёртывании в виде WAR на внешнем сервере (Tomcat, WildFly, WebLogic) встроенный сервер должен быть исключён — управление жизненным циклом приложения берёт на себя контейнер.

---

**Необходимые изменения**

**1. Расширить SpringBootServletInitializer**

`SpringBootServletInitializer` — это реализация `WebApplicationInitializer` из Spring, использующая Servlet 3.0 API. Именно через неё внешний контейнер загружает Spring-контекст без `web.xml`:

```java
@SpringBootApplication
public class MyApplication extends SpringBootServletInitializer {

    // Метод для запуска внешним контейнером сервлетов
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(MyApplication.class);
    }

    // Метод для запуска как исполняемого JAR (оба метода можно оставить)
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

Если нежелательно изменять главный класс, можно создать отдельный класс:

```java
public class ServletInitializer extends SpringBootServletInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(MyApplication.class);
    }
}
```

---

**2. Изменить packaging в pom.xml**

```xml
<packaging>war</packaging>
```

По умолчанию `<packaging>jar</packaging>` (можно не указывать).

---

**3. Пометить встроенный Tomcat как provided**

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <!-- spring-boot-starter-tomcat транзитивно подтягивается отсюда -->
    </dependency>

    <!-- Исключаем встроенный Tomcat из WAR — он предоставляется сервером -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-tomcat</artifactId>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

Зависимости с `scope=provided` включаются в компиляцию и тесты, но не в финальный артефакт. В WAR они попадают в `WEB-INF/lib-provided` (доступны при запуске через `java -jar`, но игнорируются при деплое).

---

**4. Для Gradle**

```groovy
plugins {
    id 'war'
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    providedRuntime 'org.springframework.boot:spring-boot-starter-tomcat'
}
```

---

**Сравнительная таблица изменений**

| Что меняется | Стандартный JAR | WAR для внешнего сервера |
|---|---|---|
| `<packaging>` | `jar` (по умолчанию) | `war` |
| Встроенный Tomcat | `compile`-зависимость | `provided`-зависимость |
| Точка входа для контейнера | `main` метод | `SpringBootServletInitializer.configure()` |
| Запуск | `java -jar app.jar` | Деплой в `webapps/` сервера |
| `web.xml` | Не нужен | Не нужен (Servlet 3.0) |

---

**Особенности и ограничения**

- **Двойной запуск**: Оставив `main`-метод, можно собрать «executable WAR» — файл, работающий и как `java -jar`, и как WAR-деплой.
- **WebFlux не поддерживается**: Реактивные приложения на Spring WebFlux (Netty) нельзя развернуть как WAR, поскольку они не используют Servlet API.
- **Контекстный путь**: При деплое WAR контекстный путь приложения определяется именем файла. Например, `myapp.war` → `http://server/myapp/`. Для деплоя в root context нужно назвать файл `ROOT.war`.
- **Версия Servlet API**: Сервер должен поддерживать Servlet 3.0+. Tomcat 7+, WildFly 8+, WebLogic 12.1.3+ — совместимы.
- **Конфигурация**: `application.properties`/`application.yml` и другие ресурсы из `src/main/resources` упаковываются в `WEB-INF/classes` и по-прежнему работают.

---

**Пример структуры WAR**

```
myapp.war
├── META-INF/
├── WEB-INF/
│   ├── classes/          ← application.properties, скомпилированные классы
│   ├── lib/              ← зависимости (без встроенного Tomcat)
│   └── lib-provided/     ← provided-зависимости (Tomcat) для executable WAR
└── (статические ресурсы из src/main/webapp/)
```
### Вопрос 19. Что конкретно делает аннотация @SpringBootApplication? Какие три аннотации она заменяет и какие дефолтные параметры каждой из них использует?

**Категория:** Spring Boot · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Using the @SpringBootApplication Annotation :: Spring Boot](https://docs.spring.io/spring-boot/reference/using/using-the-springbootapplication-annotation.html)

`@SpringBootApplication` — это аннотация-удобство, которая эквивалентна одновременному объявлению `@SpringBootConfiguration`, `@EnableAutoConfiguration` и `@ComponentScan`. Она позволяет объявить все три аннотации одной строкой. Ни одна из этих возможностей не является обязательной — при необходимости можно заменить `@SpringBootApplication` на отдельные аннотации и настроить каждую индивидуально. Атрибут `proxyBeanMethods` (по умолчанию `true`) управляет CGLIB-проксированием `@Bean`-методов. Атрибуты `scanBasePackages` и `scanBasePackageClasses` — алиасы для `@ComponentScan`, по умолчанию сканируется пакет класса-точки входа.

#### Ответ от Claude

`@SpringBootApplication` — это мета-аннотация (composite annotation), которая объединяет три аннотации:

**1. `@SpringBootConfiguration`**
- Специализированная версия `@Configuration` из Spring Boot.
- Помечает класс как источник определений бинов (bean definitions) Spring-контекста.
- Отличие от `@Configuration`: поддерживает автоматическое обнаружение конфигурации в интеграционных тестах (`@SpringBootTest` находит точку входа именно по `@SpringBootConfiguration`).
- Ключевой дефолтный параметр: `proxyBeanMethods = true` — методы `@Bean` проксируются через CGLIB, что обеспечивает singleton-семантику при прямых вызовах `@Bean`-методов из кода.

**2. `@EnableAutoConfiguration`**
- Включает механизм автоконфигурации Spring Boot.
- Заставляет Spring Boot сканировать classpath и автоматически применять подходящие `@AutoConfiguration`-классы.
- Дефолтные параметры:
  - `exclude = {}` — список классов автоконфигурации, которые нужно явно исключить (пустой по умолчанию).
  - `excludeName = {}` — то же самое, но по имени класса (пустой по умолчанию).

**3. `@ComponentScan`**
- Включает автоматическое сканирование компонентов (`@Component`, `@Service`, `@Repository`, `@Controller` и т. д.).
- Дефолтные параметры:
  - `basePackages = {}` — по умолчанию пустой массив, что означает сканирование пакета, в котором находится аннотированный класс, и всех его подпакетов.
  - `basePackageClasses = {}` — пустой массив (альтернатива через type-safe ссылку на класс).
  - `nameGenerator = BeanNameGenerator.class` — стандартный генератор имён бинов (`AnnotationBeanNameGenerator`).

**Итог:** `@SpringBootApplication` на главном классе приложения является стандартной точкой входа. Заменяет три аннотации с разумными defaults, подходящими для большинства приложений. При необходимости тонкой настройки (`exclude`, `scanBasePackages`) можно передавать параметры прямо в `@SpringBootApplication` — они делегируются соответствующим составляющим аннотациям.

```java
// Эти два объявления эквивалентны:

@SpringBootApplication
public class MyApplication { ... }

// --- эквивалент ---

@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan
public class MyApplication { ... }
```

---

### Вопрос 20. Опишите механизм автоконфигурации Spring Boot изнутри: как JVM находит классы автоконфигурации при старте? Какой файл использовался до Spring Boot 2.7 и что заменило spring.factories в Spring Boot 3.x?

**Категория:** Spring Boot · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Creating Your Own Auto-configuration :: Spring Boot](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)

Spring Boot проверяет наличие файла `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` в опубликованном JAR. В этом файле перечислены классы автоконфигурации — по одному на строку. До Spring Boot 2.7 использовался файл `META-INF/spring.factories` с ключом `org.springframework.boot.autoconfigure.EnableAutoConfiguration`. В Spring Boot 2.7 новый формат `.imports` был представлен как замена с сохранением обратной совместимости с `spring.factories`. В Spring Boot 3.0 поддержка регистрации через `spring.factories` для автоконфигурации была полностью удалена.

#### Ответ от Claude

**Эволюция механизма: три эпохи**

**До Spring Boot 2.7 — `META-INF/spring.factories`**

Использовался стандартный Java SPI-подобный механизм через файл `META-INF/spring.factories` (формат Properties):

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.LibXAutoConfiguration,\
  com.example.LibYAutoConfiguration
```

Spring Boot читал этот файл через `SpringFactoriesLoader` — утилиту из `spring-core`, которая сканирует все JAR в classpath и агрегирует записи по ключу. Это позволяло нескольким библиотекам вносить вклад в один и тот же ключ.

**Spring Boot 2.7 — введение нового формата с обратной совместимостью**

Был введён новый файл: `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

Формат — просто список FQCN (полных имён классов), по одному на строку:

```
com.example.LibXAutoConfiguration
com.example.LibYAutoConfiguration
```

Вместе с этим введена аннотация `@AutoConfiguration` как замена `@Configuration` для классов автоконфигурации. Она поддерживает атрибуты `before`, `after` и другие — устраняя необходимость в отдельных `@AutoConfigureBefore`/`@AutoConfigureAfter`.

В Spring Boot 2.7 `spring.factories` ещё работал, но был помечен как deprecated.

**Spring Boot 3.x — полное удаление `spring.factories` для автоконфигурации**

В Spring Boot 3.0 поддержка ключа `org.springframework.boot.autoconfigure.EnableAutoConfiguration` в `spring.factories` полностью убрана. Единственный поддерживаемый механизм — файл `.imports`.

**Как именно Spring Boot находит классы при старте**

1. `SpringApplication.run()` создаёт `SpringApplication` и запускает `refreshContext()`.
2. В процессе вызывается `AutoConfigurationImportSelector`, который реализует `DeferredImportSelector` (загружается на последнем этапе обработки конфигурации, после всех пользовательских `@Configuration`).
3. `AutoConfigurationImportSelector` использует `ImportCandidates.load()` (в Spring Boot 3.x), который читает все файлы `META-INF/spring/<имя-аннотации>.imports` из classpath через `ClassLoader.getResources()`.
4. Для оптимизации стартового времени существует файл `META-INF/spring-autoconfigure-metadata.properties` — он содержит предвычисленные метаданные об условиях автоконфигурации. Это позволяет отфильтровать неподходящие конфигурации ещё до загрузки их классов, что критично для производительности и поддержки GraalVM native image.
5. Оставшиеся кандидаты проходят проверку `@Conditional`-условий (`@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty` и т. д.).
6. Подошедшие классы регистрируются в `BeanFactory`.

**Почему сменили формат**

- Новый `.imports` файл более конкретен (имя файла = имя аннотации), что упрощает обнаружение и устраняет ошибки.
- `spring.factories` был общим реестром для многих вещей (не только автоконфигурации), что затрудняло понимание.
- Формат лучше совместим с GraalVM native image и AOT-компиляцией (статический анализ предпочитает явные списки).

---

