# База вопросов для собеседования на Java-разработчика

Вопросы собраны из реальных интернет-источников (подборки вопросов с собеседований), переведены на русский, дедуплицированы. У каждого вопроса — две секции: **«Оригинальный ответ из интернета»** (со ссылкой на источник) и **«Ответ от Claude»** (выверенная по нескольким источникам версия). Правила формирования вопросов и шаблон — в [`RULES.md`](RULES.md).

> **Всего: 1816 вопросов в 44 разделах.** Каждый файл содержит не более 20 вопросов; разделы разбиты на части `<раздел>-NN.md` со сквозной нумерацией.

## Фундамент языка и платформы

| Раздел | Части (по ≤20 вопросов) | Всего |
|--------|--------------------------|------:|
| Core Java (основы + ООП + generics + исключения) | [core-java/](core-java/README.md) | 240 |
| Collections Framework | [ч.1](collections-01.md) · [ч.2](collections-02.md) · [ч.3](collections-03.md) | 60 |
| Многопоточность и concurrency | [ч.1](concurrency-01.md) · [ч.2](concurrency-02.md) · [ч.3](concurrency-03.md) · [ч.4](concurrency-04.md) | 80 |
| JVM, память и сборка мусора | [ч.1](jvm-gc-01.md) · [ч.2](jvm-gc-02.md) · [ч.3](jvm-gc-03.md) | 60 |
| Функциональное программирование и Stream API | [ч.1](functional-streams-01.md) · [ч.2](functional-streams-02.md) · [ч.3](functional-streams-03.md) | 60 |
| Современные возможности Java | [ч.1](modern-java-01.md) · [ч.2](modern-java-02.md) | 40 |
| Ввод-вывод: IO и NIO | [ч.1](io-nio-01.md) · [ч.2](io-nio-02.md) · [ч.3](io-nio-03.md) | 60 |

## Проектирование и инженерная культура

| Раздел | Части (по ≤20 вопросов) | Всего |
|--------|--------------------------|------:|
| Паттерны проектирования | [ч.1](design-patterns-01.md) · [ч.2](design-patterns-02.md) · [ч.3](design-patterns-03.md) | 60 |
| SOLID, чистый код и рефакторинг | [ч.1](solid-clean-code-01.md) · [ч.2](solid-clean-code-02.md) · [ч.3](solid-clean-code-03.md) | 60 |
| Алгоритмы и структуры данных | [ч.1](algorithms-01.md) · [ч.2](algorithms-02.md) · [ч.3](algorithms-03.md) | 60 |
| Задачи LeetCode | [ч.1](leetcode-01.md) · [ч.2](leetcode-02.md) · [ч.3](leetcode-03.md) · [ч.4](leetcode-04.md) | 58 |

## Backend-экосистема

| Раздел | Части (по ≤20 вопросов) | Всего |
|--------|--------------------------|------:|
| Spring Framework (Core, IoC, AOP) | [ч.1](spring-01.md) · [ч.2](spring-02.md) · [ч.3](spring-03.md) | 60 |
| Spring Boot | [ч.1](spring-boot-01.md) · [ч.2](spring-boot-02.md) · [ч.3](spring-boot-03.md) | 60 |
| Реляционные базы данных и SQL | [ч.1](databases-sql-01.md) · [ч.2](databases-sql-02.md) · [ч.3](databases-sql-03.md) · [ч.4](databases-sql-04.md) | 80 |
| PostgreSQL (специфика) | [ч.1](postgresql-01.md) · [ч.2](postgresql-02.md) · [ч.3](postgresql-03.md) | 60 |
| Redis (кеш, структуры данных, кластер) | [ч.1](redis-01.md) | 15 |
| Apache Cassandra (NoSQL, wide-column) | [ч.1](cassandra-01.md) | 15 |
| ClickHouse (колоночная OLAP-СУБД) | [ч.1](clickhouse-01.md) | 15 |
| JPA и Hibernate | [ч.1](jpa-hibernate-01.md) · [ч.2](jpa-hibernate-02.md) · [ч.3](jpa-hibernate-03.md) | 60 |
| jOOQ (типобезопасный SQL на Java) | [ч.1](jooq-01.md) | 15 |
| REST, HTTP и веб-слой | [ч.1](rest-web-01.md) · [ч.2](rest-web-02.md) · [ч.3](rest-web-03.md) | 60 |
| Системы сборки: Maven и Gradle | [ч.1](build-tools-01.md) · [ч.2](build-tools-02.md) | 40 |
| Тестирование | [ч.1](testing-01.md) · [ч.2](testing-02.md) · [ч.3](testing-03.md) | 60 |

## Распределённые системы и эксплуатация

| Раздел | Части (по ≤20 вопросов) | Всего |
|--------|--------------------------|------:|
| Распределённые системы (основы: CAP, консенсус, согласованность) | [ч.1](distributed-systems-01.md) | 18 |
| Микросервисная архитектура | [ч.1](microservices-01.md) · [ч.2](microservices-02.md) · [ч.3](microservices-03.md) | 60 |
| Quarkus (cloud-native Java) | [ч.1](quarkus-01.md) | 15 |
| Брокеры сообщений (Kafka, RabbitMQ) | [ч.1](messaging-01.md) · [ч.2](messaging-02.md) · [ч.3](messaging-03.md) | 60 |
| Контейнеры и DevOps | [ч.1](containers-devops-01.md) · [ч.2](containers-devops-02.md) · [ч.3](containers-devops-03.md) | 60 |
| Безопасность приложений | [ч.1](security-01.md) · [ч.2](security-02.md) · [ч.3](security-03.md) | 60 |

Шаблон новых задач LeetCode — [docs/templates/leetcode-task-template.md](../docs/templates/leetcode-task-template.md).

## Вопросы с HH

Перенесены из репозитория квизов проверки навыков HeadHunter
([Londeren/hh-skill-verifications-quizzes](https://github.com/Londeren/hh-skill-verifications-quizzes)).
Группа верхнего уровня в просмотрщике; внутри — темы, внутри тем — уровни
(Advanced / Intermediate / Basic). Раскладка: `hh/<тема>/<уровень>/questions.md`.

| Тема | Уровни (вопросов) | Всего |
|------|-------------------|------:|
| PostgreSQL | Advanced (15) | 15 |
| Java | Advanced (15) · Intermediate (12) | 27 |
| Docker | Advanced (15) · Intermediate (12) · Basic (10) | 37 |
| OOP | Advanced (15) · Intermediate (12) · Basic (10) | 37 |
| SQL | Advanced (27) · Intermediate (12) · Basic (10) | 49 |

Шаблон вопросов раздела — [`../docs/templates/hh-question-template.md`](../docs/templates/hh-question-template.md).

---

→ База знаний по предметным областям: [`../knowledge-base/README.md`](../knowledge-base/README.md)
