# Системы сборки: Maven и Gradle

> **Уровень:** Junior / Middle
> **Связанные вопросы:** [Вопросы по Maven и Gradle →](../../../interview-questions/build-tools-01.md)
> **Связанные области:** [[14-spring-boot]], [[19-testing]]

## Что это и зачем

Системы сборки автоматизируют компиляцию, управление зависимостями, тестирование и упаковку проекта.
Maven и Gradle — два доминирующих инструмента в Java-экосистеме. Разработчик должен уметь читать и
писать build-файлы, управлять зависимостями (включая конфликты версий) и понимать жизненный цикл
сборки.

Maven придерживается принципа «convention over configuration»: структура каталогов, фазы сборки
и поведение плагинов фиксированы по умолчанию. Gradle более гибок — логика сборки выражается
программно на Groovy или Kotlin DSL, что позволяет описывать нестандартные сценарии, но требует
дисциплины, чтобы скрипты оставались понятными.

---

## Ключевые подтемы

### Maven: структура POM и координаты артефакта

POM (Project Object Model) — XML-файл `pom.xml`, являющийся фундаментальной единицей Maven.
Каждый артефакт однозначно идентифицируется тремя координатами:

| Координата   | Описание                                      | Пример                 |
|--------------|-----------------------------------------------|------------------------|
| `groupId`    | Организация / группа проекта                  | `org.springframework`  |
| `artifactId` | Имя конкретного модуля                        | `spring-core`          |
| `version`    | Версия; суффикс `-SNAPSHOT` — нестабильная    | `6.1.0`                |

Полный ключ: `groupId:artifactId:version` (GAV-координаты).

Минимальный `pom.xml` ([официальная документация](https://maven.apache.org/guides/introduction/introduction-to-the-pom.html)):

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0.0</version>
</project>
```

По умолчанию `<packaging>jar</packaging>`. Тип `pom` используется для родительских и BOM-проектов.

**Super POM.** Все POM неявно наследуют Super POM — встроенный POM Maven, который задаёт
репозиторий Maven Central (`https://repo.maven.apache.org/maven2`), стандартные директории
(`src/main/java`, `src/test/java`, `target`) и настройки плагинов по умолчанию.

### Maven: наследование и агрегация

**Наследование (parent POM)** позволяет вынести общие зависимости, версии и настройки плагинов
в один родительский модуль:

```xml
<!-- pom.xml дочернего модуля -->
<parent>
  <groupId>com.example</groupId>
  <artifactId>parent-project</artifactId>
  <version>1.0.0</version>
</parent>
<artifactId>child-module</artifactId>
<!-- groupId и version наследуются от parent -->
```

Дочерний модуль наследует: `dependencies`, `dependencyManagement`, `plugins`, `pluginManagement`,
`properties`, `build` и другие элементы.

**Агрегация (multi-module build)** — родительский POM с `<packaging>pom</packaging>` объявляет
дочерние модули, и команда `mvn install` выполняется для каждого из них:

```xml
<packaging>pom</packaging>
<modules>
  <module>core</module>
  <module>web</module>
  <module>api</module>
</modules>
```

### Maven: жизненный цикл сборки

Maven определяет три встроенных жизненных цикла
([документация](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)):

- **default** — основной цикл: компиляция, тестирование, упаковка, публикация.
- **clean** — удаление артефактов предыдущей сборки.
- **site** — генерация документации проекта.

Каждый цикл состоит из фаз, выполняемых **последовательно**. Вызов любой фазы автоматически
запускает все предшествующие ей фазы.

**Ключевые фазы цикла default:**

| Фаза                  | Описание                                                          |
|-----------------------|-------------------------------------------------------------------|
| `validate`            | Проверка корректности POM и доступности необходимой информации    |
| `compile`             | Компиляция исходного кода (`src/main/java`)                       |
| `test-compile`        | Компиляция тестового кода (`src/test/java`)                       |
| `test`                | Запуск unit-тестов (Surefire); сборка не прерывается при неудаче только с флагом `-DskipTests` |
| `package`             | Упаковка в JAR/WAR/EAR согласно `<packaging>`                    |
| `verify`              | Интеграционные тесты и проверки качества (Failsafe)               |
| `install`             | Установка артефакта в локальный репозиторий `~/.m2/repository`    |
| `deploy`              | Публикация в удалённый репозиторий                                |

Фазы цикла **clean**: `pre-clean` → `clean` → `post-clean`.

Типичные команды:

```bash
mvn compile          # компилировать
mvn test             # скомпилировать + прогнать тесты
mvn package          # скомпилировать + тесты + упаковать
mvn verify           # + интеграционные тесты
mvn install          # + положить в ~/.m2
mvn clean install    # полная чистая сборка
mvn deploy           # опубликовать в удалённый репозиторий
```

### Maven: плагины и их привязка к фазам

Реальную работу выполняют **плагины**, каждый из которых содержит одну или несколько **целей (goals)**.
При упаковке `jar` Maven автоматически привязывает стандартные цели к фазам:

| Фаза                    | Плагин:цель                     |
|-------------------------|---------------------------------|
| `process-resources`     | `resources:resources`           |
| `compile`               | `compiler:compile`              |
| `process-test-resources`| `resources:testResources`       |
| `test-compile`          | `compiler:testCompile`          |
| `test`                  | `surefire:test`                 |
| `package`               | `jar:jar`                       |
| `install`               | `install:install`               |
| `deploy`                | `deploy:deploy`                 |

Дополнительные плагины конфигурируются в секции `<build><plugins>`. Пример — запуск цели
на конкретной фазе:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-checkstyle-plugin</artifactId>
  <version>3.3.1</version>
  <executions>
    <execution>
      <phase>verify</phase>
      <goals><goal>check</goal></goals>
    </execution>
  </executions>
</plugin>
```

Для управления версиями плагинов во всём проекте используется `<pluginManagement>` в parent POM —
аналог `<dependencyManagement>` для зависимостей.

### Maven: управление зависимостями

**Scope (область видимости)** определяет, в каком classpath доступна зависимость
([документация](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)):

| Scope       | Компиляция | Тесты | Runtime | Транзитивна | Типичное использование         |
|-------------|-----------|-------|---------|-------------|-------------------------------|
| `compile`   | да        | да    | да      | да          | основные зависимости (по умолч.) |
| `provided`  | да        | да    | нет     | нет         | Servlet API, Lombok            |
| `runtime`   | нет       | да    | да      | нет         | JDBC-драйверы                  |
| `test`      | нет       | да    | нет     | нет         | JUnit, Mockito                 |
| `system`    | да        | да    | нет     | нет         | устаревший, не рекомендуется   |
| `import`    | —         | —     | —       | —           | только в `<dependencyManagement>` для BOM |

**Транзитивные зависимости.** Maven автоматически подтягивает зависимости зависимостей. При
конфликте версий применяется правило **Nearest Definition**: выигрывает версия с наименьшей
глубиной в дереве зависимостей. Если глубины одинаковы, победит та, что объявлена первой в POM.

Для явного исключения транзитивных зависимостей:

```xml
<dependency>
  <groupId>org.apache.logging.log4j</groupId>
  <artifactId>log4j-core</artifactId>
  <version>2.21.0</version>
  <exclusions>
    <exclusion>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-api</artifactId>
    </exclusion>
  </exclusions>
</dependency>
```

**`<dependencyManagement>`** — централизованное управление версиями без фактического добавления
зависимости. Дочерние модули ссылаются на артефакт без указания версии:

```xml
<!-- В parent POM: фиксируем версию -->
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.17.0</version>
    </dependency>
  </dependencies>
</dependencyManagement>

<!-- В дочернем модуле: версия не указывается -->
<dependencies>
  <dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
  </dependency>
</dependencies>
```

### Maven: BOM (Bill of Materials)

BOM — специальный POM-артефакт (`<packaging>pom</packaging>`) с только `<dependencyManagement>`.
Позволяет импортировать согласованный набор версий без наследования. Используется через
`<scope>import</scope>`:

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>3.2.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

После этого все зависимости, управляемые Spring Boot BOM, можно подключать без версии.

### Maven: репозитории

Maven последовательно ищет артефакт:
1. Локальный репозиторий `~/.m2/repository`.
2. Удалённые репозитории из POM и `settings.xml`.
3. Maven Central (`https://repo.maven.apache.org/maven2`) — определён в Super POM.

Структура любого репозитория: `groupId/artifactId/version/artifactId-version.jar`.

Кастомный репозиторий в `pom.xml`:

```xml
<repositories>
  <repository>
    <id>company-nexus</id>
    <url>https://nexus.example.com/repository/maven-releases/</url>
  </repository>
</repositories>
```

Учётные данные хранятся в `~/.m2/settings.xml` (не в pom.xml!) через `<servers>` с тем же `id`.

---

### Gradle: основные концепции

Gradle — гибкая система сборки на базе JVM. Скрипт сборки пишется на **Groovy DSL** (`build.gradle`)
или **Kotlin DSL** (`build.gradle.kts`). Kotlin DSL обеспечивает статическую типизацию и лучшую
поддержку IDE; Groovy DSL более лаконичен, но динамически типизирован.

Минимальный `build.gradle.kts` для Java-проекта:

```kotlin
plugins {
    java
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}

tasks.test {
    useJUnitPlatform()
}
```

### Gradle: жизненный цикл сборки

Gradle выполняет каждую сборку в три фазы
([документация](https://docs.gradle.org/current/userguide/build_lifecycle.html)):

1. **Initialization (Инициализация).** Выполняются init-скрипты, обрабатывается `settings.gradle(.kts)`,
   создаются объекты `Project` для корневого и всех подпроектов.

2. **Configuration (Конфигурация).** Выполняются build-скрипты всех проектов, регистрируются задачи
   и формируется **граф задач (Task DAG)** — ориентированный ациклический граф зависимостей между
   задачами. Незапрошенные задачи не конфигурируются (ленивая конфигурация).

3. **Execution (Выполнение).** Gradle запускает выбранные задачи в порядке, определённом DAG.
   Независимые задачи могут выполняться параллельно.

Ключевое отличие от Maven: **нет фиксированного порядка фаз**, сборка определяется графом задач,
зависимостями между ними (`dependsOn`, `finalizedBy`, `mustRunAfter`).

### Gradle: конфигурации зависимостей (Java Library Plugin)

Java Library Plugin вводит следующие конфигурации
([документация](https://docs.gradle.org/current/userguide/java_library_plugin.html)):

| Конфигурация        | Compile classpath потребителя | Runtime classpath потребителя | Типичное применение                     |
|---------------------|:---:|:---:|------------------------------------------|
| `api`               | да  | да  | публичное API библиотеки                 |
| `implementation`    | нет | да  | внутренние зависимости (рекомендуется)   |
| `compileOnly`       | нет | нет | аннотации (Lombok), Servlet API          |
| `runtimeOnly`       | нет | да  | JDBC-драйверы                            |
| `testImplementation`| —   | —   | JUnit, Mockito (только в тестах)         |
| `testCompileOnly`   | —   | —   | аннотации только для компиляции тестов   |
| `testRuntimeOnly`   | —   | —   | только в runtime тестов                  |

**Важно:** предпочитайте `implementation` вместо `api`. Использование `api` «утекает» зависимость
в compile classpath всех потребителей, что замедляет инкрементальную сборку и создаёт нежелательные
транзитивные зависимости.

### Gradle: инкрементальная сборка и кеш

Ключевые механизмы ускорения сборки
([документация](https://docs.gradle.org/current/userguide/incremental_build.html)):

**Up-to-Date Checks.** Каждая задача декларирует входные (`@Input`, `@InputFiles`) и выходные
(`@OutputFile`, `@OutputDirectory`) данные. Если хэши входов и выходов не изменились с последнего
запуска, задача помечается `UP-TO-DATE` и пропускается.

**Инкрементальная компиляция Java** (Gradle 4.10+). Анализирует граф классов и перекомпилирует
только те классы, чей ABI (публичный API) затронут изменением. Изменение тела метода без изменения
сигнатуры не приводит к перекомпиляции зависимых классов.

**Build Cache.** Результаты задач сохраняются по ключу (хэш входных данных). При совпадении ключа
выходы восстанавливаются из кеша без повторного выполнения. Работает как локально
(`~/.gradle/caches`), так и через удалённый сервер кеша (например, Gradle Build Cache Node или
Develocity). Включается через `--build-cache` или `org.gradle.caching=true` в `gradle.properties`.

**Configuration Cache.** Кэширует результат фазы конфигурации целиком. При повторном запуске
с теми же входными данными фаза конфигурации пропускается полностью, что даёт ощутимый выигрыш
в многомодульных проектах.

**Gradle Daemon** включён по умолчанию (с Gradle 3.0): процесс JVM остаётся запущенным между
вызовами, что исключает накладные расходы на старт JVM и прогрев JIT.

Настройки производительности в `gradle.properties`:

```properties
org.gradle.parallel=true        # параллельная сборка подпроектов
org.gradle.caching=true         # включить Build Cache
org.gradle.daemon=true          # включить Daemon (по умолчанию)
org.gradle.jvmargs=-Xmx2g       # увеличить память Daemon
```

### Сравнение Maven и Gradle

| Критерий                    | Maven                                   | Gradle                                     |
|-----------------------------|-----------------------------------------|--------------------------------------------|
| Конфигурация                | Декларативный XML (`pom.xml`)           | Программный Groovy/Kotlin DSL              |
| Жизненный цикл              | Фиксированные фазы                      | Граф задач (DAG), произвольный порядок     |
| Производительность          | Нет встроенного кеша задач              | Инкрементальная сборка, Build Cache, Daemon |
| Расширяемость               | Только через плагины                    | Произвольная логика в скриптах             |
| Мультимодульность           | Хорошая поддержка (`<modules>`)         | Отличная поддержка (`settings.gradle`)     |
| Конфигурация зависимостей   | Один scope per dependency               | Гранулярные конфигурации (api/impl/…)      |
| Экосистема                  | Очень широкая, много плагинов           | Широкая, активно растёт                    |
| Порог вхождения             | Низкий (стандартизированный XML)        | Чуть выше (нужно знать DSL)                |
| Воспроизводимость           | Высокая (строгий lifecycle)             | Зависит от качества скриптов               |

**Когда выбирать Maven:** стандартные Java EE / Jakarta EE проекты, строгие корпоративные требования,
команда не готова к DSL, проект уже на Maven.

**Когда выбирать Gradle:** Android-разработка (единственный официальный инструмент), сложные
кастомные сборки, критична скорость CI/CD, проект на Spring Boot (стартеры поддерживают оба).

### Разрешение конфликтов версий зависимостей

Конфликт возникает, когда два пути в дереве зависимостей ведут к разным версиям одного артефакта.

**Maven** применяет правило **Nearest Definition**: побеждает версия с меньшей глубиной. Для
принудительного управления: добавить зависимость явно в корневой POM или использовать `<exclusions>`.

**Gradle** по умолчанию выбирает **максимальную версию** (optimistic upgrade). Для явного контроля:

```kotlin
configurations.all {
    resolutionStrategy {
        // принудительно зафиксировать версию
        force("com.fasterxml.jackson.core:jackson-databind:2.15.0")
        // запретить динамические версии
        failOnDynamicVersions()
        // запретить изменяемые версии (-SNAPSHOT)
        failOnChangingVersions()
    }
}
```

Также Gradle поддерживает **Dependency Locking** — фиксацию разрешённых версий в файле
`gradle.lockfile` для воспроизводимых сборок.

---

## Достоверные источники

1. **[Maven — Introduction to the Build Lifecycle](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)** —
   официальная документация Apache Maven по жизненному циклу: три цикла, все фазы, привязка плагинов.
   Первичный источник.

2. **[Maven — Introduction to the Dependency Mechanism](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)** —
   официальная документация Apache Maven: scope зависимостей, транзитивность, `dependencyManagement`,
   BOM, правило Nearest Definition. Первичный источник.

3. **[Maven — Introduction to the POM](https://maven.apache.org/guides/introduction/introduction-to-the-pom.html)** —
   официальная документация по структуре POM: минимальный POM, Super POM, наследование, агрегация,
   интерполяция свойств. Первичный источник.

4. **[Gradle User Manual — Build Lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html)** —
   официальное руководство Gradle: три фазы (Initialization / Configuration / Execution), Task DAG,
   ленивая конфигурация. Первичный источник.

5. **[Gradle User Manual — Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html)** —
   официальная документация по конфигурациям зависимостей (`api`, `implementation`, `compileOnly` и др.),
   разница между `api` и `implementation`. Первичный источник.

6. **[Gradle User Manual — Incremental Build](https://docs.gradle.org/current/userguide/incremental_build.html)** —
   официальная документация Gradle: Up-to-Date checks, аннотации задач, Build Cache (локальный
   и удалённый), Configuration Cache. Первичный источник.
