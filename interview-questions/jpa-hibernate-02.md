# JPA и Hibernate — часть 2 из 3

> Вопросы 21–40 (в части: 20). Всего в разделе: 51.
> Область знаний: [../knowledge-base/16-jpa-hibernate.md](../knowledge-base/16-jpa-hibernate.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](jpa-hibernate-01.md) · **ч.2** · [ч.3](jpa-hibernate-03.md)

---
### Вопрос 21. Как Hibernate реализует dirty checking внутри? Что такое snapshot и когда он создаётся? Как @Transactional(readOnly=true) влияет на dirty checking?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Spring read-only transaction Hibernate optimization — Vlad Mihalcea](https://vladmihalcea.com/spring-read-only-transaction-hibernate-optimization/)

При загрузке сущности в Persistence Context Hibernate сохраняет **снапшот (hydrated state)** — копию всех значений полей на момент загрузки. Этот снапшот хранится отдельно от самого объекта, что удваивает расход памяти на каждую управляемую сущность.

При flush Hibernate сравнивает текущее состояние каждого managed-объекта с его снапшотом. Если хотя бы одно поле изменилось — генерируется UPDATE-запрос.

**Влияние `@Transactional(readOnly=true)`:**
- До Spring 5.1: аннотация только устанавливала `FlushMode.MANUAL` для сессии, что предотвращало автоматический flush и, следовательно, грязную проверку.
- Начиная со Spring Framework 5.1: флаг `readOnly` напрямую передаётся в Hibernate Session. Hibernate переводит загружаемые сущности в read-only режим и **немедленно сбрасывает снапшот** после загрузки объекта, а не хранит его до конца транзакции.

Результат: значительная экономия памяти (снапшоты не накапливаются) и экономия CPU (dirty checking не выполняется при flush). Особенно заметно при загрузке большого числа сущностей в read-only транзакции.

#### Ответ от Claude

**Как Hibernate реализует dirty checking внутри:**

Механизм основан на хранении **снапшота (loaded state / hydrated state)** — полной копии значений всех полей сущности на момент её загрузки в Persistence Context. Реализован через внутренний класс `EntityEntry` в `PersistenceContext`.

**Жизненный цикл снапшота:**
1. Сущность загружается из БД (через `find()`, JPQL, Criteria API и т.д.).
2. Hibernate гидрирует (десериализует) строку результата в объект **и одновременно** сохраняет копию всех значений полей в `EntityEntry.loadedState` — это и есть снапшот.
3. Снапшот хранится в `PersistenceContext` (в `StatefulPersistenceContext`) на протяжении всей жизни сессии/транзакции.
4. Также снапшот создаётся при вызове `persist()` (для новых объектов) и `merge()` (для managed-копии).

**Алгоритм dirty checking при flush:**
1. Hibernate итерирует все managed-сущности в `PersistenceContext`.
2. Для каждой сущности вызывается `EntityPersister.findDirty()`, который сравнивает текущие значения полей объекта с сохранёнными в снапшоте.
3. Стратегия по умолчанию — **полное сравнение всех полей** (`DefaultFlushEntityEventListener`): даже если изменилось одно поле, проверяются все. Это O(N × P), где N — число сущностей, P — среднее число полей.
4. При обнаружении расхождений генерируется SQL UPDATE только для изменённых колонок (если включён `@DynamicUpdate`) или для всех non-lazy полей.

**Альтернатива: байткод-инструментация (Hibernate 5+)**
Через `@org.hibernate.annotations.DynamicUpdate` + bytecode enhancement Hibernate может отслеживать изменения в момент присваивания (`setXxx()`), не делая полного сравнения при flush. Грязные поля помечаются сразу, что снижает нагрузку на CPU при большом числе сущностей.

**Влияние `@Transactional(readOnly=true)` на dirty checking:**

| Аспект | readOnly=false (по умолчанию) | readOnly=true |
|---|---|---|
| Снапшот при загрузке | Создаётся и хранится до конца сессии | Создаётся, но **немедленно сбрасывается** (Spring 5.1+) |
| Flush mode | AUTO | MANUAL |
| Dirty checking при flush | Выполняется для всех managed-сущностей | Не выполняется (нет снапшота, нет автофлуша) |
| Расход памяти | ~2× от размера данных сущностей | ~1× (снапшоты не хранятся) |
| SQL UPDATE на commit | Генерируется при наличии изменений | Не генерируется |

**Важные уточнения:**
- До Spring 5.1: `readOnly=true` только устанавливал `FlushMode.MANUAL`, снапшоты всё равно создавались — экономии памяти не было.
- Начиная со Spring 5.1 (`HibernateJpaDialect`): флаг передаётся напрямую в `Session.setDefaultReadOnly(true)`, что заставляет Hibernate удалять снапшот сразу после гидрации — экономия памяти существенная.
- `readOnly=true` не гарантирует запрет записи на уровне БД — это оптимизация Hibernate, а не database-level constraint.
- Hibernate также поддерживает `@QueryHint(name = "org.hibernate.readOnly", value = "true")` на уровне отдельных запросов и `session.setReadOnly(entity, true)` для отдельных сущностей — поведение аналогичное.
### Вопрос 22. Объясните проблему N+1. Назовите как минимум 3 разных способа её решения в JPA/Hibernate и чем они отличаются друг от друга.

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Solving the N+1 Query Problem in Hibernate & JPA — DEV Community](https://dev.to/devcorner/solving-the-n1-query-problem-in-hibernate-jpa-1ijj)

Проблема N+1 — распространённая проблема производительности в ORM-фреймворках. Она возникает, когда при получении коллекции записей выполняется 1 начальный запрос, а затем ещё N отдельных запросов для получения связанных данных каждой записи.

Четыре решения:

1. **JOIN FETCH** — объединяет связанные сущности в одном SQL-запросе через явный JOIN в JPQL. `SELECT u FROM User u JOIN FETCH u.orders` выполняет один запрос. Минус: может загружать избыточные данные при больших наборах.

2. **@EntityGraph** — аннотационный подход, автоматически оптимизирующий запросы без изменения JPQL. Работает с пагинацией, в отличие от JOIN FETCH. Код чище, запрос гибче.

3. **@BatchSize** — группирует несколько lazy-load запросов вместо отдельных. Вместо N запросов Hibernate выполняет пакетные загрузки (например, batch size=10). Подходит для больших наборов, где немедленная загрузка всего потребует много памяти.

4. **@Fetch(FetchMode.SUBSELECT)** — использует стратегию подзапроса: один запрос для родительских записей и один общий запрос для получения всех дочерних записей через подзапрос.

#### Ответ от Claude

**Суть проблемы N+1**

Проблема N+1 возникает, когда ORM для получения N связанных объектов выполняет 1 запрос на загрузку основного списка и затем ещё по 1 запросу на каждый элемент для подгрузки его ассоциации — итого 1 + N запросов. Например: загружаем 100 пользователей (1 SELECT), а затем для каждого отдельно загружаем его заказы (100 SELECT) — итого 101 запрос вместо одного.

Чаще всего проблема возникает при стратегии LAZY на ассоциации (`@OneToMany`, `@ManyToOne`) и обходе коллекции в коде.

---

**Решение 1: JOIN FETCH (JPQL)**

```java
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

Hibernate генерирует один SQL JOIN-запрос, возвращающий и пользователей, и заказы в одном ResultSet.

- Плюсы: один запрос к БД, минимальная задержка.
- Минусы: декартово произведение строк может быть большим; несовместим с пагинацией (`Pageable`) для коллекций (см. вопрос №23); нельзя применить к нескольким коллекциям одновременно без `DISTINCT` и осторожности.

---

**Решение 2: @EntityGraph (JPA 2.1+)**

```java
@EntityGraph(attributePaths = {"orders"})
@Query("SELECT u FROM User u")
List<User> findAllWithOrders();
```

EntityGraph декларативно указывает, какие ассоциации загрузить жадно для данного запроса. Hibernate генерирует JOIN в SQL.

- Плюсы: не требует изменения JPQL; совместим с пагинацией (Spring Data JPA добавляет COUNT-запрос отдельно); можно настраивать через `@NamedEntityGraph` или динамически.
- Минусы: при коллекциях также порождает JOIN, но Spring Data корректно обрабатывает пагинацию через разделение запросов.
- Отличие от JOIN FETCH: EntityGraph — это подсказка для провайдера, не меняющая структуру JPQL-запроса; JOIN FETCH — явная директива в запросе.

---

**Решение 3: @BatchSize**

```java
@Entity
public class User {
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    @BatchSize(size = 25)
    private List<Order> orders;
}
```

При первом обращении к `orders` у любого пользователя Hibernate не загружает только эту одну коллекцию, а отправляет один IN-запрос для всех уже загруженных прокси: `SELECT * FROM orders WHERE user_id IN (1, 2, 3, ..., 25)`.

- Плюсы: остаётся LAZY (гибко); количество запросов сокращается с N до ceil(N / batch_size); хорошо работает с пагинацией.
- Минусы: не устраняет проблему полностью (несколько запросов всё равно выполняется); требует правильно подобранного `size`.
- Отличие: работает на уровне аннотации, не требует изменения запросов; применяется также на уровне класса через `@BatchSize` на самом `@Entity`.

---

**Решение 4: FetchMode.SUBSELECT**

```java
@OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
@Fetch(FetchMode.SUBSELECT)
private List<Order> orders;
```

При первом обращении к коллекции любого пользователя Hibernate выполняет один подзапрос: `SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE <original condition>)`.

- Плюсы: всегда ровно 2 запроса (один для родителей, один для всех коллекций); не нужно задавать batch_size.
- Минусы: применимо только к коллекциям; подзапрос может быть тяжёлым, если оригинальный запрос сложный; вся коллекция загружается полностью.
- Отличие от @BatchSize: SUBSELECT всегда загружает все коллекции за один раз, тогда как @BatchSize может дробить на несколько пакетов.

---

**Сравнительная таблица**

| Способ | Кол-во SQL | Совместим с пагинацией | Изменение запроса |
|---|---|---|---|
| JOIN FETCH | 1 | Нет (для коллекций) | Да (JPQL) |
| EntityGraph | 1 (+ COUNT) | Да | Нет |
| @BatchSize | ceil(N/size) + 1 | Да | Нет |
| SUBSELECT | 2 | Да | Нет |

---

### Вопрос 23. Почему JOIN FETCH несовместим с пагинацией (Pageable) для коллекций? Что Hibernate реально делает в этом случае и какое предупреждение пишет в лог?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How to fix Hibernate's Warning "HHH000104: firstResult/maxResults specified with collection fetch" — Thorben Janssen](https://thorben-janssen.com/hibernate-warning-firstresult-maxresults/)

Когда используется JOIN FETCH вместе с пагинацией (`setFirstResult()` / `setMaxResults()`), Hibernate не может применить LIMIT/OFFSET на уровне БД, поскольку SQL оперирует строками декартова произведения, а не сущностями. Если бы LIMIT применялся к результату JOIN, он ограничивал бы строки (комбинации турнир-игрок), а не количество родительских сущностей, что приводило бы к неполным данным.

Вместо этого Hibernate:
1. Выполняет запрос **без** LIMIT/OFFSET.
2. Загружает **весь** ResultSet из БД в память.
3. Применяет пагинацию **в памяти** после разбора результатов.

Предупреждение в логе:
> `HHH000104: firstResult/maxResults specified with collection fetch; applying in memory!`

Рекомендуемое решение — два отдельных запроса: сначала получить paginated первичные ключи, затем по этим ключам загрузить сущности с JOIN FETCH.

#### Ответ от Claude

**Техническая причина несовместимости**

JOIN FETCH на коллекцию (`@OneToMany`, `@ManyToMany`) порождает в SQL Cartesian Product — для каждой родительской строки появляется столько строк в ResultSet, сколько элементов в дочерней коллекции. Например:

- 3 пользователя с 5 заказами каждый → 15 строк в ResultSet.

Если СУБД получает `LIMIT 2 OFFSET 0`, она возвращает **первые 2 строки из 15** — то есть две строки одного (и, возможно, частично второго) пользователя. Hibernate собрал бы 1 пользователя с 2 заказами вместо 2 пользователей с 5 заказами каждый. Данные были бы **некорректными**.

**Что Hibernate делает реально**

Чтобы не отдавать некорректные данные, Hibernate:
1. Генерирует SQL **без** `LIMIT` и `OFFSET` клауз.
2. Отправляет в БД запрос, возвращающий **все** строки.
3. Получает весь ResultSet (может быть гигантским).
4. Разбирает строки в граф объектов в памяти JVM.
5. Применяет `firstResult`/`maxResults` к уже построенному списку сущностей **в памяти**.

При масштабе это катастрофично: 10 000 заказов × 10 позиций = 100 000 строк в памяти ради пагинации по 20 заказов.

**Точное предупреждение в логе**

В Hibernate 5.x и старше:
```
HHH000104: firstResult/maxResults specified with collection fetch; applying in memory!
```

В Hibernate 6.x это предупреждение сменило код:
```
HHH90003004: firstResult/maxResults specified with collection fetch; applying in memory!
```

Предупреждение пишется на уровне `WARN` через логгер `org.hibernate.hql.internal.ast.QueryTranslatorImpl` (Hibernate 5) или `org.hibernate.query.sqm.sql.BaseSqmToSqlAstConverter` (Hibernate 6).

Существует конфигурационное свойство, заставляющее Hibernate падать с исключением вместо предупреждения:
```properties
spring.jpa.properties.hibernate.query.fail_on_pagination_over_collection_fetch=true
```

**Рекомендуемые решения**

1. **Два запроса (основной подход):**
   ```java
   // Запрос 1: пагинированные ID
   @Query("SELECT u.id FROM User u WHERE ...")
   Page<Long> findPagedIds(Pageable pageable);

   // Запрос 2: загрузка с JOIN FETCH по ID
   @Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id IN :ids")
   List<User> findByIdsWithOrders(@Param("ids") List<Long> ids);
   ```

2. **@EntityGraph вместо JOIN FETCH** — Spring Data JPA автоматически разделяет запрос данных и COUNT-запрос, а при `@EntityGraph` JOIN применяется корректно.

3. **@BatchSize на коллекции** — страница загружается без JOIN FETCH, а коллекции подтягиваются пакетами. Два-три запроса вместо одного, но без in-memory фильтрации.

4. **Hibernate 6.4+ / 7.4+** — начиная с Hibernate 7.4 (по данным блога JetBrains Idea, май 2026) фреймворк научился самостоятельно определять набор ID через подзапрос и потом делать JOIN FETCH только для них, что позволяет корректную пагинацию с единым запросом.

**Почему именно коллекций — принципиальный момент**

Несовместимость касается исключительно JOIN FETCH на коллекции (`*ToMany`). JOIN FETCH на единственный объект (`@ManyToOne`, `@OneToOne`) не умножает строки и с пагинацией работает корректно.

---

### Вопрос 24. Чем отличаются стратегии генерации id: IDENTITY, SEQUENCE, TABLE? Почему IDENTITY отключает JDBC batching в Hibernate, и когда это критично?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [JDBC batching — Hibernate ORM 5.2 User Guide](https://docs.hibernate.org/orm/5.2/userguide/html_single/chapters/batch/Batching.html)

Документация Hibernate прямо указывает: «Hibernate disables insert batching at the JDBC level transparently if you use an identity identifier generator» («Hibernate прозрачно отключает пакетную вставку на уровне JDBC, если используется генератор идентификаторов типа identity»).

Причина: при IDENTITY-столбцах единственный способ узнать присвоенный идентификатор — выполнить оператор INSERT. Поскольку Hibernate нуждается в идентификаторе сущности для размещения её в Persistence Context (контексте сохраняемости), каждый INSERT должен выполняться немедленно и индивидуально, что исключает группировку операторов в пакет.

#### Ответ от Claude

**IDENTITY**

Использует автоинкрементный столбец БД (`AUTO_INCREMENT` в MySQL, `GENERATED ALWAYS AS IDENTITY` в PostgreSQL/Oracle/SQL Server). Значение ID **генерирует база данных в момент выполнения INSERT**.

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```

- Плюсы: простота, нативная поддержка в большинстве СУБД, нет дополнительных объектов.
- Минусы: **отключает JDBC batching** (см. ниже); ID неизвестен до момента вставки, что усложняет ряд сценариев.

**SEQUENCE**

Использует объект sequence базы данных (PostgreSQL, Oracle, H2, MariaDB 10.3+). ID генерируется **до выполнения INSERT** вызовом `NEXT VALUE FOR seq`.

```java
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_seq")
@SequenceGenerator(name = "user_seq", sequenceName = "user_id_seq", allocationSize = 50)
private Long id;
```

- Плюсы: поддерживает JDBC batching; `allocationSize` позволяет резервировать диапазон ID одним вызовом к БД (например, allocationSize=50 означает 1 вызов к sequence на каждые 50 INSERT'ов).
- Минусы: не поддерживается MySQL < 8.0 (и не поддерживался до MariaDB 10.3).

**TABLE**

Хранит счётчик ID в отдельной таблице (`hibernate_sequence`), получает следующее значение через `SELECT FOR UPDATE`.

```java
@Id
@GeneratedValue(strategy = GenerationType.TABLE)
private Long id;
```

- Плюсы: переносимость — работает на любой реляционной СУБД; технически не блокирует JDBC batching.
- Минусы: крайне медленно — требует отдельной транзакции с `SELECT FOR UPDATE` (пессимистическая блокировка на строке счётчика) для каждого нового ID, что создаёт bottleneck в многопоточной среде. Это **отдельная транзакция**, которая должна закоммититься до основной. Владимир Михалча (vladmihalcea.com) называет TABLE «наихудшим из возможных вариантов».

---

**Почему IDENTITY отключает JDBC batching — механизм**

JDBC batching работает так: драйвер накапливает несколько `PreparedStatement.addBatch()` и отправляет их на сервер одним сетевым пакетом через `executeBatch()`. Это резко сокращает количество round-trip'ов к БД.

Проблема с IDENTITY: спецификация JPA требует, чтобы после вызова `EntityManager.persist(entity)` на объекте **был установлен сгенерированный ID**. Поскольку IDENTITY генерирует ID только при фактическом выполнении INSERT, Hibernate вынужден:
1. Немедленно выполнить INSERT (flush).
2. Прочитать сгенерированный ID (`Statement.getGeneratedKeys()`).
3. Присвоить ID объекту.

Шаги 1-3 нужно повторить **для каждой сущности отдельно** — накапливать их в batch невозможно. Как пояснил мэйнтейнер Hibernate в официальном форуме: «JPA requires that EntityManager#persist sets the generated identifier on the entity, so Hibernate ORM has to do an insert when the IDENTITY strategy is used».

С SEQUENCE ситуация иная: `NEXT VALUE FOR seq` возвращает ID **до** INSERT. Hibernate получает N значений из sequence (за 1-2 round-trip'а благодаря `allocationSize`), присваивает их сущностям, накапливает N INSERT-операторов в batch и отправляет одним пакетом.

---

**Когда отключение batching критично**

Критично при:
- **Массовых вставках**: импорт данных, ETL, создание тысяч и более записей за одну транзакцию.
- **Высоконагруженных write-heavy сервисах**: событийный лог, временные ряды, аналитика.
- **Каскадных вставках**: сохранение графа объектов (User + его Orders + их Items) — без batching каждый INSERT отдельный round-trip.

Не критично при:
- Единичных или редких вставках (CRUD-формы, административные операции).
- Использовании MySQL/MariaDB без поддержки sequences, где IDENTITY — единственный простой вариант, а объём вставок невелик.
- Bulk-операциях через `INSERT INTO ... SELECT` или `EntityManager.createNativeQuery()` — они обходят ORM-механизм целиком.

**Рекомендация**: для приложений с интенсивными вставками использовать SEQUENCE с `allocationSize`, кратным `hibernate.jdbc.batch_size`.

```properties
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

`order_inserts=true` заставляет Hibernate группировать INSERT'ы по типу сущности, что увеличивает эффективность batching при смешанном графе объектов.

---
### Вопрос 25. Что такое кэш первого уровня в Hibernate? Каков его scope? Когда он сбрасывается и как принудительно очистить его без закрытия сессии?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Hibernate ORM 6.1 — Session JavaDocs](https://docs.hibernate.org/orm/6.1/javadocs/org/hibernate/Session.html)

Кэш первого уровня (persistence context) включён по умолчанию и действует на уровне одного `Session` / `EntityManager`. Как только сущность становится управляемой, она добавляется во внутренний кэш текущего контекста персистентности. Для управления этим кэшем доступны следующие методы:

- `void evict(Object object)` — удаляет конкретный экземпляр из кэша сессии. Изменения этого объекта больше не будут синхронизироваться с БД. Каскадируется на ассоциированные объекты с `CascadeType.DETACH`.
- `void clear()` — полностью очищает сессию, удаляя все загруженные экземпляры.
- `void flush()` — принудительно синхронизирует состояние persistence context с базой данных (генерирует INSERT/UPDATE/DELETE), но не очищает кэш.

Метод `detach(Object)` является синонимом `evict()` в терминологии JPA.

#### Ответ от Claude

**Что такое кэш первого уровня**

Кэш первого уровня (L1-кэш) — это persistence context, то есть встроенный кэш, ассоциированный с конкретным экземпляром `Session` (Hibernate) или `EntityManager` (JPA). Он включён всегда и не может быть отключён. Его роль — хранить «живые» управляемые (managed) сущности в памяти в рамках одной транзакции/сессии.

**Scope**

Область видимости L1-кэша — один `Session` / `EntityManager`. Никакие другие сессии не видят его содержимое. Как только сессия закрыта (`session.close()`) или EntityManager уничтожен, кэш полностью освобождается. В Spring-приложениях с `@Transactional` время жизни persistence context по умолчанию совпадает с границами транзакции.

**Когда кэш сбрасывается автоматически**

Понятие «сброс» (flush) означает синхронизацию состояния кэша с БД, а не его очистку. Flush происходит:
- Перед выполнением JPQL/HQL-запроса (если FlushMode = AUTO, что является значением по умолчанию).
- При явном вызове `session.flush()` / `entityManager.flush()`.
- Перед фиксацией транзакции (`commit`).

После flush кэш не очищается — сущности остаются управляемыми.

**Как принудительно очистить кэш без закрытия сессии**

```java
// Удалить одну сущность из кэша (detach):
session.evict(entity);          // Hibernate API
entityManager.detach(entity);   // JPA API

// Удалить все сущности из кэша:
session.clear();
entityManager.clear();
```

После вызова `evict()` / `detach()` объект переходит в состояние detached — его изменения не отслеживаются. После `clear()` все объекты становятся detached.

**Типичный кейс применения**

При пакетной обработке (batch processing) больших наборов данных рекомендуется периодически вызывать `flush()` + `clear()`, чтобы не допустить накопления тысяч объектов в памяти:

```java
for (int i = 0; i < list.size(); i++) {
    session.persist(list.get(i));
    if (i % 50 == 0) {
        session.flush();
        session.clear();
    }
}
```

---

### Вопрос 26. Чем отличается кэш второго уровня от первого? Какие провайдеры он поддерживает? Как настроить стратегию конкурентного доступа (READ_ONLY, NONSTRICT_READ_WRITE, READ_WRITE, TRANSACTIONAL) и когда какую выбирать?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Hibernate ORM 5.2 — Caching (User Guide)](https://docs.hibernate.org/orm/5.2/userguide/html_single/chapters/caching/Caching.html)

Кэш первого уровня (persistence context) включён по умолчанию и работает на уровне одной сессии. Кэш второго уровня (L2) опционален и работает на уровне `SessionFactory` / `EntityManagerFactory`, то есть разделяется между всеми сессиями и может быть настроен отдельно для каждого класса сущности или коллекции.

Поддерживаемые провайдеры: JCache (JSR-107), Ehcache, Infinispan. Конфигурируется через `hibernate.cache.region.factory_class`.

Стратегии конкурентного доступа:
- `read-only` — для иммутабельных данных; простейшая и наиболее производительная стратегия, безопасна в кластере.
- `read-write` — гарантирует согласованный доступ к отдельным сущностям с помощью «мягких» блокировок (soft locks). Не поддерживает сериализуемую изоляцию транзакций.
- `nonstrict-read-write` — без блокировок; допускает редкие устаревшие чтения. Подходит, когда одновременное обновление одних и тех же данных крайне маловероятно.
- `transactional` — полноценные транзакционные обновления кэша через XA-транзакции. Требует JTA-окружения и провайдера с поддержкой транзакций (например, Infinispan).

#### Ответ от Claude

**Ключевые отличия L1 от L2**

| Характеристика | L1 (Session/EntityManager) | L2 (SessionFactory) |
|---|---|---|
| Scope | Одна сессия / транзакция | Все сессии одного SessionFactory |
| По умолчанию | Всегда включён | Отключён, требует явной настройки |
| Управление | Нет выбора провайдера | Подключаемые провайдеры |
| Видимость | Изолирован в сессии | Общий для всего приложения (или кластера) |
| Риск устаревших данных | Нет | Есть; управляется стратегией конкурентного доступа |

**Поддерживаемые провайдеры (Hibernate 5.x / 6.x)**

- **Ehcache** — самый популярный выбор для одиночного JVM; поддерживает хранение на диске, TTL, eviction-политики.
- **Infinispan** — распределённый кэш от Red Hat; поддерживает кластерный режим и стратегию TRANSACTIONAL.
- **JCache (JSR-107)** — стандартный адаптер, позволяет подключить любой JCache-совместимый провайдер (Caffeine, Hazelcast и др.).
- Устаревшие (Hibernate 3.x): EHCache, OSCache, SwarmCache, JBoss Cache — большинство заменены JCache-адаптером.

**Включение L2-кэша**

```properties
# persistence.xml / application.properties
hibernate.cache.use_second_level_cache=true
hibernate.cache.region.factory_class=org.hibernate.cache.ehcache.EhCacheRegionFactory
# или для JCache:
# hibernate.cache.region.factory_class=org.hibernate.cache.jcache.JCacheRegionFactory
```

**Аннотирование сущности**

```java
@Entity
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product { ... }
```

**Стратегии конкурентного доступа**

**READ_ONLY**
- Использовать для: справочников, enum-подобных сущностей, данных, которые никогда не обновляются.
- Принцип: данные помещаются в кэш при первом чтении и никогда не инвалидируются обновлениями.
- Безопасна в кластере. Максимальная производительность.
- Попытка обновить сущность с READ_ONLY вызовет исключение.

**NONSTRICT_READ_WRITE**
- Использовать для: данных, которые обновляются редко; допустимы кратковременные устаревшие чтения.
- Принцип: при обновлении кэш инвалидируется (без блокировок). В промежутке между инвалидацией и загрузкой новых данных другие транзакции могут прочитать старое значение.
- Нет накладных расходов на блокировки — выше пропускная способность.

**READ_WRITE**
- Использовать для: данных с умеренной частотой обновлений, когда важна согласованность чтения.
- Принцип: при обновлении на запись выставляется «мягкая» блокировка (soft lock). Другие транзакции, встретив soft lock, идут напрямую в БД. После commit блокировка снимается и кэш обновляется.
- Не поддерживает уровень изоляции SERIALIZABLE. Не работает корректно в кластере без поддержки со стороны провайдера.

**TRANSACTIONAL**
- Использовать для: критичных данных, где необходима полная согласованность между кэшем и БД в рамках одной XA-транзакции.
- Принцип: изменения в кэше и БД фиксируются или откатываются атомарно через JTA.
- Требования: JTA-окружение + провайдер с поддержкой транзакций (Infinispan transactional; EhCache — только для Hibernate 3.x через JBoss Cache).
- Максимальные накладные расходы; применять только при реальной необходимости.

**Рекомендации по выбору**

1. Данные никогда не меняются → `READ_ONLY`.
2. Данные меняются редко, допустим небольшой lag → `NONSTRICT_READ_WRITE`.
3. Данные меняются, важна согласованность, нет XA → `READ_WRITE`.
4. Данные критичны, есть JTA, нужна ACID-согласованность кэша → `TRANSACTIONAL`.

---

### Вопрос 27. В чём причина LazyInitializationException? Как её решить правильно — и почему ответ «сделать eager» является неправильным решением?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [The best way to handle the LazyInitializationException — Vlad Mihalcea](https://vladmihalcea.com/the-best-way-to-handle-the-lazyinitializationexception/)

`LazyInitializationException` возникает, когда код пытается инициализировать ленивую ассоциацию (LAZY proxy) после того, как `EntityManager` уже закрыт. Ленивая ассоциация представлена в виде прокси-объекта, и когда к ней обращаются вне контекста открытой сессии, Hibernate не может выполнить запрос к БД — отсюда исключение.

Почему `EAGER` — неправильное решение:
1. **N+1 проблема**: если JPQL-запрос не использует `JOIN FETCH`, Hibernate выполняет отдельный SELECT для каждой EAGER-ассоциации каждой загруженной сущности.
2. **Одностороннее решение**: пометив ассоциацию как EAGER, её нельзя сделать LAZY для конкретного запроса — нет глобальной стратегии, подходящей для всех use case.
3. **Лишняя нагрузка**: EAGER заставляет загружать данные даже там, где они не нужны.

Правильные решения:
- **JOIN FETCH** в JPQL-запросе: явно загружает нужную ассоциацию в той же транзакции.
- **DTO-проекции**: JPQL `SELECT NEW ...` возвращает только нужные поля без прокси — проблема LazyInitializationException вообще не возникает.

#### Ответ от Claude

**Причина LazyInitializationException**

По умолчанию ассоциации (`@OneToMany`, `@ManyToMany`, а в Hibernate и `@ManyToOne`/`@OneToOne` с явным `fetch = LAZY`) загружаются лениво. Hibernate заменяет объект прокси-классом. Прокси инициализируется (то есть делает SELECT) только при первом обращении к данным — но только пока `Session` открыта.

Если обращение к ассоциации происходит после закрытия сессии (транзакции), Hibernate не может открыть новое соединение в рамках того же контекста и бросает:

```
org.hibernate.LazyInitializationException:
  could not initialize proxy - no Session
```

Типичные сценарии:
- Загрузили сущность в сервисном методе, вернули контроллеру, и там обратились к ленивой коллекции (транзакция уже закрыта).
- Использование паттерна Open Session In View (OSIV) отключено, а сущность покидает слой сервиса.

**Почему «сделать EAGER» — неправильное решение**

1. **N+1 проблема.** При запросе списка сущностей (`SELECT p FROM Post p`) с EAGER-ассоциацией Hibernate выполнит 1 запрос для получения постов + N отдельных SELECT для загрузки ассоциаций каждого поста. Это критически снижает производительность.

2. **Декартово произведение.** При нескольких EAGER-коллекциях SQL JOIN порождает декартово произведение строк — результирующий набор данных может быть многократно избыточен.

3. **Нет гибкости.** EAGER — глобальная настройка на уровне маппинга. Нельзя «отключить» её для конкретного запроса. В разных use case нужны разные наборы данных; глобальная стратегия EAGER не оптимальна ни для одного из них.

4. **Маскирует архитектурную проблему.** EAGER не решает причину — доступ к данным за пределами транзакции — а лишь откладывает момент возникновения проблемы.

**Правильные решения**

**1. JOIN FETCH в JPQL (рекомендуется для сущностей)**

Явно загружает ассоциацию в рамках одного SQL-запроса внутри транзакции:

```java
List<Post> posts = em.createQuery(
    "SELECT p FROM Post p JOIN FETCH p.comments WHERE p.id = :id",
    Post.class)
    .setParameter("id", postId)
    .getResultList();
```

**2. Entity Graph (JPA 2.1+)**

Позволяет описать граф загрузки декларативно, не меняя маппинг:

```java
@NamedEntityGraph(
    name = "Post.withComments",
    attributeNodes = @NamedAttributeNode("comments")
)
@Entity
public class Post { ... }

// Использование:
EntityGraph<?> graph = em.getEntityGraph("Post.withComments");
Map<String, Object> hints = Map.of("javax.persistence.fetchgraph", graph);
Post post = em.find(Post.class, id, hints);
```

**3. DTO-проекции (наиболее эффективно)**

Вместо возврата сущностей возвращать DTO с нужными полями — прокси-объектов нет в принципе:

```java
List<PostDTO> result = em.createQuery(
    "SELECT new com.example.PostDTO(p.id, p.title, c.body) " +
    "FROM Post p JOIN p.comments c WHERE p.id = :id",
    PostDTO.class)
    .setParameter("id", id)
    .getResultList();
```

**4. @Transactional на уровне сервиса**

Убедиться, что весь код, обращающийся к ленивым ассоциациям, выполняется внутри транзакции. Сессия остаётся открытой на протяжении метода:

```java
@Transactional(readOnly = true)
public PostDTO getPost(Long id) {
    Post post = postRepository.findById(id).orElseThrow();
    post.getComments().size(); // OK — сессия ещё открыта
    return mapper.toDto(post);
}
```

**Антипаттерны, которых следует избегать**

- `hibernate.enable_lazy_load_no_trans=true` — открывает новую сессию для каждой инициализации прокси, порождает N+1 проблему и скрытые транзакции.
- Open Session In View (OSIV) — удерживает сессию на протяжении всего HTTP-запроса (включая рендеринг вью). Удобно, но влечёт долгое удержание соединений с БД и скрытые N+1 запросы.
### Вопрос 28. Какие стратегии маппинга наследования есть в JPA (SINGLE_TABLE, TABLE_PER_CLASS, JOINED)? Каковы плюсы и минусы каждой с точки зрения производительности запросов и нормализации?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Entity Inheritance Mapping Strategies — Java EE 7 Tutorial (Oracle)](https://docs.oracle.com/javaee/7/tutorial/persistence-intro002.htm)

JPA поддерживает три стратегии маппинга наследования:

**SINGLE_TABLE** — все классы иерархии хранятся в одной таблице. Используется дискриминаторный столбец (`DTYPE`) для различения типов записей. Стратегия выбирается по умолчанию, если аннотация `@Inheritance` не указана явно. Обеспечивает отличную поддержку полиморфных запросов и связей, так как не требует JOIN-операций. Недостаток: столбцы, специфичные для подклассов, обязаны быть `nullable`, что нарушает нормализацию и создаёт разреженные таблицы.

**TABLE_PER_CLASS** — каждый конкретный класс маппится в отдельную таблицу, содержащую все поля (включая унаследованные). Нет общей родительской таблицы. Плюс: отсутствие `nullable`-столбцов. Серьёзный минус: полиморфные запросы требуют `SQL UNION`, что делает эту стратегию самой медленной для запросов по базовому типу. Поддерживается не всеми провайдерами (например, GlassFish не поддерживает).

**JOINED** — корневой класс хранится в родительской таблице, каждый подкласс — в отдельной таблице только с собственными полями; связь осуществляется через внешний ключ к PK родителя. Это наиболее нормализованная схема. Минус: для получения экземпляра подкласса необходим JOIN (один и более), что замедляет запросы относительно SINGLE_TABLE.

Итоговое сравнение по производительности: SINGLE_TABLE > JOINED > TABLE_PER_CLASS. По нормализации: JOINED > TABLE_PER_CLASS > SINGLE_TABLE.

#### Ответ от Claude

JPA определяет три стратегии маппинга наследования через аннотацию `@Inheritance(strategy = InheritanceType.XXX)`.

---

**SINGLE_TABLE (стратегия по умолчанию)**

Все сущности иерархии хранятся в одной таблице. Тип записи определяется дискриминаторным столбцом (`@DiscriminatorColumn`, по умолчанию `DTYPE`).

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "DTYPE")
public abstract class Employee { @Id Long id; String name; }

@Entity
@DiscriminatorValue("FT")
public class FullTimeEmployee extends Employee { Integer salary; }

@Entity
@DiscriminatorValue("PT")
public class PartTimeEmployee extends Employee { Float hourlyWage; }
```

Схема таблицы:
```
EMPLOYEE: | id | DTYPE | name | salary | hourly_wage |
           | 1  | FT    | Ann  | 50000  | NULL        |
           | 2  | PT    | Bob  | NULL   | 25.5        |
```

Плюсы:
- Лучшая производительность: чтение любого типа — простой `SELECT` без JOIN.
- Простота DDL: одна таблица на всю иерархию.
- Отличная поддержка полиморфных запросов (`SELECT e FROM Employee e`).

Минусы:
- Поля подклассов обязаны быть `nullable` — нельзя поставить `NOT NULL` на уровне БД.
- Разреженная таблица (много `NULL` в каждой строке) — плохая нормализация.
- При большой иерархии таблица становится очень широкой.

---

**JOINED**

Корневой класс хранится в одной таблице; каждый подкласс — в отдельной таблице только с собственными полями. PK подкласса одновременно является FK на PK родителя.

```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Employee { @Id Long id; String name; }

@Entity
public class FullTimeEmployee extends Employee { Integer salary; }
```

Схема:
```
EMPLOYEE:          | id | name |
FULLTIMEEMPLOYEE:  | id | salary |   (id -> FK -> EMPLOYEE.id)
PARTTIMEEMPLOYEE:  | id | hourly_wage |
```

SQL для выборки подкласса:
```sql
SELECT e.*, ft.* FROM EMPLOYEE e JOIN FULLTIMEEMPLOYEE ft ON e.id = ft.id
```

Плюсы:
- Наиболее нормализованная схема: нет `NULL`-полей, нет дублирования данных.
- Хорошая поддержка полиморфных запросов (через LEFT JOIN).
- Легко добавлять новые подклассы без изменения существующих таблиц.

Минусы:
- Каждый запрос на подкласс требует JOIN (минимум один), что замедляет выборку.
- Вставка требует нескольких `INSERT` (в каждую таблицу уровня иерархии).
- Глубокие иерархии дают цепочку JOIN-операций, сильно снижающих производительность.

---

**TABLE_PER_CLASS**

Каждый конкретный (non-abstract) класс маппится в отдельную таблицу, которая содержит все поля — и унаследованные, и собственные. Общей родительской таблицы нет.

```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public abstract class Employee { @Id Long id; String name; }
```

Схема:
```
FULLTIMEEMPLOYEE:  | id | name | salary |
PARTTIMEEMPLOYEE:  | id | name | hourly_wage |
```

SQL для полиморфного запроса по базовому типу:
```sql
SELECT * FROM FULLTIMEEMPLOYEE
UNION ALL
SELECT * FROM PARTTIMEEMPLOYEE
```

Плюсы:
- Нет `NULL`-столбцов — каждая таблица содержит только нужные поля.
- Прямые запросы к конкретному типу — простой `SELECT` без JOIN.

Минусы:
- Полиморфные запросы требуют `UNION (ALL)` по всем таблицам — самая низкая производительность для запросов через базовый тип.
- Плохая поддержка полиморфных ассоциаций (JPA-провайдер вынужден делать UNION).
- Дублирование столбцов общих полей во всех таблицах — нарушение нормализации.
- Спецификация JPA помечает поддержку этой стратегии как опциональную; не все провайдеры её реализуют корректно.

---

**Сводная таблица**

| Критерий                | SINGLE_TABLE | JOINED       | TABLE_PER_CLASS |
|-------------------------|--------------|--------------|-----------------|
| Производительность чтения | Лучшая     | Средняя      | Плохая (UNION)  |
| Производительность записи | Лучшая     | Хуже (multi-INSERT) | Средняя  |
| Нормализация            | Плохая       | Лучшая       | Средняя         |
| NOT NULL на подполях    | Невозможно   | Возможно     | Возможно        |
| Полиморфные запросы     | Отлично      | Хорошо       | Плохо           |
| Поддержка провайдерами  | Обязательная | Обязательная | Опциональная    |

**Рекомендации по выбору:**
- `SINGLE_TABLE` — когда иерархия неглубокая, запросы часто полиморфные, производительность критична.
- `JOINED` — когда важна нормализация БД, используются ограничения целостности, иерархия небольшая по глубине.
- `TABLE_PER_CLASS` — избегать; применимо лишь если запросы всегда к конкретному типу и полиморфные ассоциации не используются.

---

### Вопрос 29. Что произойдёт при двунаправленном @OneToMany/@ManyToOne, если вы добавите child только в коллекцию родителя, но не установите поле parent у дочерней сущности? Как Hibernate определяет владельца связи (owning side)?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Chapter 24. Example: Parent/Child — Hibernate Core 3.6 Reference](https://docs.hibernate.org/core/3.6/reference/en-US/html/example-parentchild.html)

В документации Hibernate рассматривается именно этот сценарий. Без двунаправленного маппинга (когда у Child нет ссылки на Parent) Hibernate при сохранении коллекции вынужден сначала вставить запись дочерней сущности без внешнего ключа (`INSERT` без `parent_id`), а затем отдельным `UPDATE` проставить FK — «the link (the foreign key `parent_id`) from `p` to `c` is not considered part of the state of the `Child` object and is therefore not created in the `INSERT`».

Решение: добавить `@ManyToOne` на стороне Child и пометить коллекцию родителя атрибутом `inverse="true"` (в XML) или `mappedBy` (в аннотациях). Тогда ответственность за управление FK переходит на сторону Child, и лишний `UPDATE` исчезает.

#### Ответ от Claude

**Концепция owning side (владеющей стороны)**

В двунаправленной ассоциации `@OneToMany` / `@ManyToOne` JPA/Hibernate всегда выделяет:
- **Owning side (владелец)** — сторона, которая физически управляет столбцом внешнего ключа в БД. Именно изменения на этой стороне влекут SQL-операции.
- **Inverse side (обратная сторона)** — зеркальная, только навигационная; изменения на ней игнорируются Hibernate при генерации SQL.

В паре `@OneToMany` / `@ManyToOne` **владельцем всегда является сторона `@ManyToOne`** (дочерняя сущность), поскольку именно в её таблице физически находится столбец FK. Обратная сторона помечается атрибутом `mappedBy`:

```java
@Entity
public class Post {
    @Id Long id;

    @OneToMany(mappedBy = "post")  // inverse side — только навигация
    List<Comment> comments = new ArrayList<>();
}

@Entity
public class Comment {
    @Id Long id;
    String text;

    @ManyToOne                     // owning side — управляет FK
    @JoinColumn(name = "post_id")
    Post post;
}
```

**Что произойдёт, если добавить child только в коллекцию родителя?**

```java
Post post = entityManager.find(Post.class, 1L);
Comment comment = new Comment("Hello");
post.getComments().add(comment);  // только это
// comment.setPost(post);         // НЕ СДЕЛАНО
entityManager.persist(comment);
```

Поскольку `@OneToMany` с `mappedBy` — это **обратная (inverse) сторона**, Hibernate игнорирует изменения в этой коллекции при синхронизации с БД. Результат: `comment.post` остаётся `null`, и в таблице `COMMENT` будет вставлена запись с `post_id = NULL`. Связь не будет установлена в базе данных, несмотря на то что объект добавлен в коллекцию в памяти.

Hibernate отслеживает состояние FK через поле `post` на стороне `Comment` (owning side). Если оно `null` — FK будет `NULL`.

**Что будет без `mappedBy` (коллекция — owning side)?**

Если коллекция `@OneToMany` объявлена без `mappedBy` (что превращает её в owning side), Hibernate будет управлять FK через эту коллекцию. В этом случае добавление только в коллекцию родителя сработает, но Hibernate вынужден:
1. Сделать `INSERT` для child без FK (`post_id = NULL`).
2. Затем выполнить отдельный `UPDATE` для простановки FK.

Это неэффективно и порождает лишний `UPDATE`.

**Правильный подход — синхронизировать обе стороны:**

```java
// В классе Post
public void addComment(Comment comment) {
    comments.add(comment);
    comment.setPost(this);   // синхронизация owning side
}

public void removeComment(Comment comment) {
    comments.remove(comment);
    comment.setPost(null);
}
```

Только при установке `comment.setPost(post)` Hibernate запишет корректный FK при flush, выполнив единственный `INSERT`.

**Как Hibernate определяет owning side:**

Hibernate смотрит на атрибут `mappedBy` в аннотации `@OneToMany`. Значение `mappedBy = "post"` означает: «поле `post` в классе `Comment` управляет этой ассоциацией». Сторона без `mappedBy` (или с `@JoinColumn`) является owning side и отвечает за SQL. Если `mappedBy` отсутствует на обеих сторонах — обе считаются независимыми и создаётся промежуточная join-таблица.

---

### Вопрос 30. Чем отличается orphanRemoval=true от CascadeType.REMOVE? В каком сценарии они ведут себя по-разному?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Orphan Removal in Relationships — Java EE 6 Tutorial (Oracle)](https://docs.oracle.com/cd/E19798-01/821-1841/giqxy/index.html)

Документация Oracle описывает `orphanRemoval` следующим образом: когда дочерняя сущность в отношении `@OneToOne` или `@OneToMany` удаляется из связи, нередко желательно каскадировать операцию `remove` на эту сущность. Такие сущности считаются «сиротами» (orphans), и атрибут `orphanRemoval` позволяет указать, что осиротевшие сущности должны быть удалены автоматически.

Пример из документации:
```java
@OneToMany(mappedBy="customer", orphanRemoval="true")
public List<Order> getOrders() { ... }
```

Если строка заказа удалена из коллекции `orders` объекта `Customer`, она будет автоматически удалена из БД.

В отличие от этого, `CascadeType.REMOVE` применяется только при явном удалении родительской сущности (`entityManager.remove(parent)`), а не при удалении дочернего объекта из коллекции.

#### Ответ от Claude

**CascadeType.REMOVE**

Каскадирует операцию `remove` с родительской сущности на дочерние. Срабатывает **только тогда, когда родитель явно удаляется** через `EntityManager.remove(parent)`.

```java
@Entity
public class Post {
    @OneToMany(cascade = CascadeType.REMOVE, mappedBy = "post")
    List<Comment> comments;
}
```

При `entityManager.remove(post)` Hibernate сначала удалит все связанные `Comment`, потом `Post`. Но если сделать:

```java
post.getComments().remove(comment);  // удаление из коллекции
```

Запись `comment` **останется в БД**. `CascadeType.REMOVE` здесь не задействован.

---

**orphanRemoval = true**

Удаляет дочернюю сущность, если она была **исключена из коллекции родителя** или **отвязана от родителя** (т.е. стала «сиротой»). Является отдельным механизмом, независимым от каскадирования.

```java
@Entity
public class Post {
    @OneToMany(mappedBy = "post", orphanRemoval = true)
    List<Comment> comments;
}
```

При:
```java
post.getComments().remove(comment);
```
Hibernate выполнит `DELETE` для `comment` при следующем flush. Запись будет удалена из БД.

---

**Сценарий, где поведение различается**

Именно удаление дочернего объекта из коллекции родителя — тот сценарий, где механизмы ведут себя по-разному:

| Действие | CascadeType.REMOVE | orphanRemoval=true |
|---|---|---|
| `entityManager.remove(parent)` | Удаляет parent + все children | Удаляет parent + все children |
| `parent.getChildren().remove(child)` | Child **остаётся** в БД | Child **удаляется** из БД |
| `child.setParent(null)` | Child **остаётся** в БД | Child **удаляется** из БД |

Поведение при удалении родителя идентично: `orphanRemoval=true` имплицитно включает каскадное удаление при удалении родителя.

---

**Практический сценарий с разным поведением:**

```java
// ТОЛЬКО CascadeType.REMOVE — без orphanRemoval
Invoice invoice = em.find(Invoice.class, 1L);
LineItem item = invoice.getItems().get(0);
invoice.getItems().remove(item);
em.merge(invoice);
// item НЕ будет удалён из БД — в таблице останется запись с FK=NULL или ошибка FK

// С orphanRemoval=true
Invoice invoice = em.find(Invoice.class, 1L);
LineItem item = invoice.getItems().get(0);
invoice.getItems().remove(item);
em.merge(invoice);
// item БУДЕТ удалён из БД автоматически
```

---

**Важные нюансы:**

1. `orphanRemoval` доступен только для `@OneToOne` и `@OneToMany`. `CascadeType.REMOVE` применим к любому типу отношений.
2. Если сущность имеет несколько родителей (ссылается из нескольких мест), `orphanRemoval` может удалить её неожиданно при отвязке от одного из родителей — это нужно учитывать при проектировании.
3. Использовать `orphanRemoval=true` вместе с `CascadeType.REMOVE` (или `CascadeType.ALL`) является избыточным, но не ошибкой: поведение корректно объединяется.
4. Vlad Mihalcea подтверждает: при `orphanRemoval=false` удаление из коллекции генерирует `UPDATE` (FK -> NULL), а не `DELETE`; при `orphanRemoval=true` — `DELETE`.

---
### Вопрос 31. Что такое @Version в JPA? Как реализована оптимистичная блокировка под капотом — какой SQL генерируется при update? Что происходит при конфликте версий?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Locking — Hibernate ORM 5.2 User Guide](https://docs.hibernate.org/orm/5.2/userguide/html_single/chapters/locking/Locking.html)

Аннотация `@Version` реализует оптимистичную блокировку путём хранения версионных данных в выделенном столбце таблицы. Hibernate автоматически включает значение версии в предложение WHERE при каждом UPDATE. Если обновление не затронуло ни одной строки (потому что версия уже изменилась другой транзакцией), Hibernate фиксирует конфликт и откатывает транзакцию с выбросом `OptimisticLockException`. Разработчикам запрещено вручную изменять поле версии — это исключительная ответственность провайдера персистентности.

#### Ответ от Claude

**Что такое @Version**

`@Version` — аннотация JPA, которая включает механизм оптимистичной блокировки для сущности. Она помечает поле, в котором Hibernate будет хранить счётчик версий (или временную метку). Оптимистичная блокировка не удерживает блокировку в БД, а лишь проверяет при записи, что данные не были изменены с момента чтения.

Допустимые типы поля `@Version`: `int`, `Integer`, `long`, `Long`, `short`, `Short`, `java.sql.Timestamp`, а также `java.time.Instant` (расширение Hibernate).

Пример объявления:
```java
@Entity
public class Product {
    @Id
    private Long id;

    private String name;

    @Version
    private int version;
}
```

**Какой SQL генерируется при UPDATE**

При каждом обновлении сущности Hibernate добавляет в WHERE условие проверки текущей версии и одновременно инкрементирует её в SET:

```sql
UPDATE product
SET    name = ?, version = 2
WHERE  id = ? AND version = 1
```

Значение `version` в WHERE — то, что было прочитано в начале транзакции. Значение в SET — версия + 1.

**Что происходит при конфликте версий**

Если между чтением и записью другая транзакция уже успела обновить строку, версия в БД стала `2`, а текущая транзакция пытается обновить с `version = 1`. Hibernate выполняет UPDATE, БД сообщает, что обновлено 0 строк — Hibernate интерпретирует это как конфликт и выбрасывает `jakarta.persistence.OptimisticLockException` (или `org.hibernate.StaleStateException` на уровне Hibernate API). Транзакция откатывается.

**Важные нюансы**

- Поле версии нельзя изменять вручную — провайдер управляет им сам.
- При `merge()` детачнутой сущности версия также проверяется и обновляется.
- При удалении (`DELETE`) Hibernate также добавляет версию в WHERE: `DELETE FROM product WHERE id=? AND version=?`.
- Для сущностей с `@Inheritance(strategy=JOINED)` версионный столбец создаётся только в корневой таблице.
- Оптимистичная блокировка эффективна в сценариях «читается часто, изменяется редко»; для высококонкурентной записи лучше рассмотреть пессимистичную блокировку (`LockModeType.PESSIMISTIC_WRITE`).

---

### Вопрос 32. Когда использовать JPQL, а когда Criteria API? В чём принципиальная разница с точки зрения типобезопасности, компилируемости и поддержки динамических запросов?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Chapter 22. Creating Queries Using the Criteria API — The Java EE 6 Tutorial](https://docs.oracle.com/cd/E19226-01/820-7627/gjitv/index.html)

Criteria API предназначен для построения динамических типобезопасных запросов с помощью Java-объектов. Он позволяет программно добавлять условия, соединения и сортировки во время выполнения, не прибегая к конкатенации строк. JPQL является строковым языком запросов; его синтаксис проверяется только во время выполнения, что делает его уязвимым к опечаткам и ошибкам в именах атрибутов. Criteria API совместно с классами метамодели даёт проверку корректности запроса на этапе компиляции.

#### Ответ от Claude

**JPQL (Java Persistence Query Language)**

JPQL — текстовый язык запросов, синтаксически похожий на SQL, но оперирующий именами сущностей и их полей, а не именами таблиц и колонок. Пример:

```java
TypedQuery<Product> q = em.createQuery(
    "SELECT p FROM Product p WHERE p.price > :min", Product.class);
q.setParameter("min", BigDecimal.TEN);
```

Преимущества JPQL:
- Лаконичен и читаем, особенно для статичных запросов.
- Знаком всем, кто знает SQL.
- Подходит для именованных запросов (`@NamedQuery`), которые предварительно парсятся при старте приложения.

Недостатки:
- Строки не проверяются компилятором — опечатка в имени поля или сущности обнаружится только в runtime.
- Построение динамических запросов требует конкатенации строк, что ухудшает читаемость и повышает риск ошибок.

**Criteria API**

Criteria API — программный объектный способ построения запросов через Java API. Пример:

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Product> cq = cb.createQuery(Product.class);
Root<Product> root = cq.from(Product.class);
cq.select(root).where(cb.gt(root.get(Product_.price), BigDecimal.TEN));
TypedQuery<Product> q = em.createQuery(cq);
```

Преимущества:
- **Типобезопасность** — использует обобщённые типы (generics) и метамодель (`Product_`), атрибуты проверяются компилятором.
- **Компилируемость** — ошибки (неверное имя поля, несовместимые типы) выявляются на этапе компиляции, а не в runtime.
- **Динамические запросы** — условия можно добавлять программно через `Predicate`, что гораздо безопаснее строковой конкатенации:
  ```java
  List<Predicate> predicates = new ArrayList<>();
  if (minPrice != null) predicates.add(cb.gt(root.get(Product_.price), minPrice));
  if (name != null)     predicates.add(cb.like(root.get(Product_.name), "%" + name + "%"));
  cq.where(predicates.toArray(new Predicate[0]));
  ```

Недостатки:
- Verbose: тот же запрос занимает значительно больше строк кода.
- Сложные запросы с несколькими JOIN и подзапросами становятся трудночитаемыми.
- Требует генерации классов метамодели (через annotation processor, например `hibernate-jpamodelgen`).

**Итоговое правило выбора**

| Критерий | JPQL | Criteria API |
|---|---|---|
| Типобезопасность | Нет (runtime) | Да (compile-time) |
| Компилируемость | Нет | Да |
| Динамические запросы | Плохо (строки) | Хорошо (объекты) |
| Читаемость простых запросов | Высокая | Низкая |
| Сложные запросы | Хорошо | Трудночитаемо |

Используйте **JPQL** для статичных, хорошо известных запросов — в `@NamedQuery`, репозиториях Spring Data или простых `createQuery`. Используйте **Criteria API**, когда набор условий формируется динамически (фильтры на форме поиска, опциональные параметры) — именно для этого он и проектировался.

---

### Вопрос 33. Что такое FlushMode в Hibernate? Чем FlushMode.AUTO отличается от FlushMode.COMMIT, и когда Hibernate автоматически выполняет flush до выполнения запроса?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [FlushMode — Hibernate ORM 6.6 Javadoc](https://docs.hibernate.org/orm/6.6/javadocs/org/hibernate/FlushMode.html)

`FlushMode` определяет, когда `Session` синхронизирует состояние первого уровня кэша с базой данных. Hibernate предоставляет четыре режима: `MANUAL` (только явный вызов `flush()`), `COMMIT` (при коммите транзакции), `AUTO` (при коммите и иногда перед выполнением запроса, чтобы гарантировать актуальность данных) и `ALWAYS` (при каждом запросе). Ключевое различие `AUTO` и `COMMIT` — в том, что `AUTO` может выполнить flush перед JPQL/HQL-запросом, если в сессии есть незафиксированные изменения, потенциально влияющие на результат этого запроса, тогда как `COMMIT` этого не делает никогда.

#### Ответ от Claude

**Что такое flush и FlushMode**

Flush — это операция синхронизации состояния Persistence Context (first-level cache) с базой данных: Hibernate формирует и выполняет SQL INSERT/UPDATE/DELETE, соответствующие накопленным изменениям сущностей. Flush **не** означает коммит транзакции — данные попадают в БД, но остаются в рамках незавершённой транзакции.

`FlushMode` управляет тем, _когда_ Hibernate выполняет эту синхронизацию автоматически.

**Четыре режима**

| FlushMode | Когда происходит flush |
|---|---|
| `MANUAL` | Только при явном вызове `session.flush()` / `em.flush()` |
| `COMMIT` | При коммите транзакции. Перед запросами — никогда |
| `AUTO` (по умолчанию) | При коммите + иногда перед выполнением запроса |
| `ALWAYS` | При коммите + перед каждым запросом (расточительно) |

**Детали FlushMode.AUTO — когда именно flush перед запросом**

`AUTO` не делает flush перед каждым запросом подряд — это было бы неэффективно. Hibernate анализирует, пересекается ли таблица целевого запроса с таблицами сущностей, имеющих незафиксированные изменения в Persistence Context:

- Если в сессии есть новый (но не сохранённый) объект `Product`, а запрос обращается к таблице `product` — Hibernate выполнит flush перед запросом, чтобы запрос увидел актуальные данные.
- Если запрос обращается к таблице `order`, а в сессии изменён только `Product` — flush не выполняется (таблицы не пересекаются).

Для нативных SQL-запросов (`createNativeQuery`) Hibernate не может автоматически определить пересечение таблиц, поэтому в `AUTO` режиме нативные запросы вызывают flush всегда (если не зарегистрирована синхронизация через `addSynchronizedEntityClass`).

**FlushMode.COMMIT — поведение и риски**

В режиме `COMMIT` Hibernate откладывает все flush до момента коммита. Это означает:

```java
// COMMIT mode
Product p = em.find(Product.class, 1L);
p.setPrice(BigDecimal.valueOf(999));

// Этот запрос вернёт СТАРУЮ цену (flush ещё не было)
List<Product> expensive = em.createQuery(
    "SELECT p FROM Product p WHERE p.price > 900", Product.class
).getResultList(); // может не включить изменённый p!

em.getTransaction().commit(); // только здесь flush
```

Это повышает производительность (меньше round-trip к БД), но создаёт риск чтения устаревших данных внутри той же транзакции.

**Как установить FlushMode**

```java
// На уровне Session/EntityManager
em.setFlushMode(FlushModeType.COMMIT); // JPA API
session.setHibernateFlushMode(FlushMode.COMMIT); // Hibernate API

// На уровне конкретного запроса
Query q = em.createQuery("...");
q.setFlushMode(FlushModeType.COMMIT);
```

В Spring Data JPA методы репозитория, помеченные `@Transactional(readOnly = true)`, выставляют `FlushMode.MANUAL` через `HibernateJpaDialect`, что предотвращает случайные flush в read-only транзакциях.

**Практический вывод**

- `AUTO` — правильный выбор по умолчанию для write-транзакций: баланс между консистентностью и производительностью.
- `COMMIT` — полезен при batch-обработке или когда вы уверены, что не будете читать изменённые данные до коммита.
- `MANUAL` — для read-only сценариев, где flush вообще не нужен.
- `ALWAYS` — почти никогда не нужен на практике; использовался для обходов проблем с детекцией overlap в старых версиях Hibernate.
### Вопрос 34. Что такое @EntityGraph? Чем он отличается от JOIN FETCH в JPQL, и какой из подходов корректно работает вместе с пагинацией?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [43.1 Entity Graph Basics — Java EE 7 Tutorial (docs.oracle.com)](https://docs.oracle.com/javaee/7/tutorial/persistence-entitygraphs001.htm)

Entity Graph — это механизм JPA, позволяющий явно определить, какие поля и связи сущности должны быть загружены («eagerly fetched») при выполнении операции `find()` или запроса. Граф создаётся либо статически через аннотацию `@NamedEntityGraph`, либо динамически через `EntityManager.createEntityGraph()`. Граф применяется к запросу в виде хинта:

- `jakarta.persistence.fetchgraph` — загружаются **только** атрибуты, явно перечисленные в графе (плюс PK и поле версии).
- `jakarta.persistence.loadgraph` — загружаются атрибуты из графа **плюс** все поля, помеченные `fetch=EAGER` в самой сущности.

Таким образом, Entity Graph позволяет централизованно описывать план загрузки, повторно использовать его в разных запросах и избегать жёсткой привязки стратегии загрузки к определению сущности.

#### Ответ от Claude

**Что такое @EntityGraph**

`@EntityGraph` — аннотация Spring Data JPA (и JPA-хинт как такового), позволяющая переопределить стратегию загрузки ассоциаций прямо на уровне метода репозитория. Под капотом она транслируется в JPA-хинт `fetchgraph` или `loadgraph` и передаётся в запрос через провайдер (Hibernate).

```java
@NamedEntityGraph(
    name = "Post.withTags",
    attributeNodes = @NamedAttributeNode("tags")
)
@Entity
public class Post { ... }

// В репозитории:
@EntityGraph(value = "Post.withTags", type = EntityGraph.EntityGraphType.FETCH)
List<Post> findAll();
```

Можно объявлять граф и прямо в аннотации репозитория без `@NamedEntityGraph`:

```java
@EntityGraph(attributePaths = {"tags", "author"})
List<Post> findByStatus(String status);
```

**Отличия от JOIN FETCH в JPQL**

| Аспект | @EntityGraph | JOIN FETCH (JPQL) |
|---|---|---|
| Определение | Отдельная аннотация или динамический API | Встроен в тело JPQL-запроса |
| Переиспользование | Можно применить к нескольким методам | Привязан к конкретному запросу |
| Контроль | Управляется хинтами `fetchgraph`/`loadgraph` | Явный `LEFT JOIN FETCH` в запросе |
| SQL-результат | Hibernate может использовать JOIN или отдельный SELECT | Всегда JOIN в основном запросе |
| Дублирование строк | Аналогично JOIN FETCH (при коллекциях) | Возможны дубли строк без `DISTINCT` |

Принципиально оба подхода решают одну задачу — загрузить ассоциации без N+1 запросов. Разница — в уровне абстракции: `@EntityGraph` декларативен и не меняет JPQL, `JOIN FETCH` — часть самого запроса.

**Пагинация: ключевая проблема**

Ни `@EntityGraph` с коллекциями, ни `JOIN FETCH` с коллекциями **не работают корректно с SQL-пагинацией** (`LIMIT`/`OFFSET`). Когда Hibernate видит `maxResults`/`firstResult` вместе с JOIN по коллекции, он выдаёт предупреждение:

```
HHH000104: firstResult/maxResults specified with collection fetch; applying in memory!
```

Это означает, что Hibernate загружает **все** строки из базы, а затем обрезает результат в памяти на стороне приложения — что катастрофично для больших таблиц.

**Причина:** JOIN по коллекции умножает количество строк результата (каждая запись родителя повторяется для каждого дочернего элемента), и база данных не может корректно применить `LIMIT` на уровне «родительских» сущностей.

**Корректные подходы при пагинации:**

1. **Двухшаговый запрос (рекомендуемый):** сначала пагинированный запрос идентификаторов родительских сущностей, затем отдельный запрос с `JOIN FETCH` или `@EntityGraph` по этим ID.

```java
// Шаг 1: получаем страницу ID
Page<Long> ids = postRepository.findAllIds(pageable);
// Шаг 2: загружаем сущности с ассоциациями
List<Post> posts = postRepository.findAllWithTagsByIdIn(ids.getContent());
```

2. **@BatchSize на коллекции:** Hibernate загружает родителей с пагинацией (чистый SQL LIMIT), а потом подтягивает коллекции пакетами через IN-запросы. Пагинация работает корректно на уровне SQL.

3. **@Fetch(FetchMode.SUBSELECT):** коллекции загружаются подзапросом, пагинация родителей работает корректно.

**Итог:** `@EntityGraph` и `JOIN FETCH` с коллекциями несовместимы с корректной SQL-пагинацией. Для пагинации предпочтительны `@BatchSize`, `SUBSELECT` или двухшаговый подход.

---

### Вопрос 35. Как настроить @ManyToMany в JPA? Почему не рекомендуется использовать List вместо Set для коллекций в @ManyToMany, и что такое «Hibernate delete all + re-insert» проблема?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Best way to map the @ManyToMany relationship (vladmihalcea.com)](https://vladmihalcea.com/the-best-way-to-use-the-manytomany-annotation-with-jpa-and-hibernate/)

Статья объясняет, что при использовании `List` в `@ManyToMany`-ассоциации Hibernate демонстрирует неэффективное поведение при удалении одного элемента из коллекции. Вместо точечного удаления одной записи в таблице связи генерируется:

1. `DELETE FROM post_tag WHERE post_id = 1` — удаление **всех** связей
2. Серия `INSERT` — повторная вставка оставшихся связей

При использовании `Set` вместо `List` Hibernate генерирует точечный запрос:

```sql
DELETE FROM post_tag WHERE post_id = 1 AND tag_id = 3
```

Это намного эффективнее: меньше операций, нет лишней перестройки индексов.

Рекомендации по маппингу: использовать `HashSet`, каскадировать только `PERSIST` и `MERGE` (но не `REMOVE`), поддерживать синхронизацию двунаправленной связи через вспомогательные методы `addTag()`/`removeTag()`.

#### Ответ от Claude

**Базовая настройка @ManyToMany**

```java
@Entity
public class Post {
    @Id
    @GeneratedValue
    private Long id;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "post_tag",
        joinColumns = @JoinColumn(name = "post_id"),
        inverseJoinColumns = @JoinColumn(name = "tag_id")
    )
    private Set<Tag> tags = new HashSet<>();

    // Вспомогательные методы для синхронизации обеих сторон
    public void addTag(Tag tag) {
        tags.add(tag);
        tag.getPosts().add(this);
    }

    public void removeTag(Tag tag) {
        tags.remove(tag);
        tag.getPosts().remove(this);
    }
}

@Entity
public class Tag {
    @Id
    @GeneratedValue
    private Long id;

    @ManyToMany(mappedBy = "tags")
    private Set<Post> posts = new HashSet<>();
}
```

**Ключевые правила маппинга:**
- `@JoinTable` объявляется на **владеющей** стороне (owning side)
- Вторая сторона использует `mappedBy`
- `CascadeType.REMOVE` **не применять** — удаление одного поста не должно удалять теги
- Обязательно реализовать `equals()`/`hashCode()` на основе бизнес-ключа (не `id`)

**Проблема «delete all + re-insert» с List**

Когда коллекция объявлена как `List` (или любой `Bag` — неупорядоченный список без уникальности), Hibernate не умеет точечно вычислять разницу между старым и новым состоянием коллекции. Причина: `List` допускает дубликаты и использует позиционное равенство, а Hibernate при слиянии или при удалении одного элемента не может однозначно определить, какие строки в таблице связи изменились.

Следствие: при любом изменении коллекции Hibernate:

1. Удаляет **все** строки таблицы связи для данного родителя
2. Вставляет оставшиеся строки заново

**Пример (List — проблемное поведение):**

```sql
-- Удаляем один тег из поста с 5 тегами:
DELETE FROM post_tag WHERE post_id = 1   -- удаляет все 5
INSERT INTO post_tag (post_id, tag_id) VALUES (1, 10)  -- вставляет 4
INSERT INTO post_tag (post_id, tag_id) VALUES (1, 20)
INSERT INTO post_tag (post_id, tag_id) VALUES (1, 30)
INSERT INTO post_tag (post_id, tag_id) VALUES (1, 40)
```

**Пример (Set — корректное поведение):**

```sql
-- Удаляем один тег:
DELETE FROM post_tag WHERE post_id = 1 AND tag_id = 50
```

**Почему Set решает проблему:**

`Set` гарантирует уникальность и использует семантику равенства (`equals`/`hashCode`). Hibernate может точно вычислить дифференциал между старым и новым состоянием коллекции и сгенерировать минимальный набор DML-операций.

**Дополнительные соображения:**

- `List` с `@OrderColumn` частично решает проблему (Hibernate знает позицию), но добавляет служебную колонку порядка и не является полным решением для `@ManyToMany`
- Для сортировки с `Set` используют `@SortNatural` (в памяти) или `@OrderBy` (через SQL ORDER BY)
- `equals`/`hashCode` должны быть основаны на **натуральном ключе** бизнес-объекта, а не на `id`, который неизвестен до сохранения

---

### Вопрос 36. Что делает @BatchSize в Hibernate? Чем он отличается от JOIN FETCH и когда его применение предпочтительнее?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [@BatchSize — Hibernate ORM 6.6 Javadocs (docs.hibernate.org)](https://docs.hibernate.org/orm/6.6/javadocs/org/hibernate/annotations/BatchSize.html)

`@BatchSize` — аннотация Hibernate, которая позволяет загружать несколько неинициализированных прокси-объектов или коллекций в одном обращении к базе данных. Принимает единственный параметр `size` — максимальный размер батча (строго положительное целое число). Применяется к:

- **Типам (классам сущностей)** — для пакетной загрузки прокси сущности
- **Методам и полям (коллекциям/ассоциациям)** — для пакетной загрузки коллекций

**Пример на классе:**
```java
@Entity
@BatchSize(size = 100)
class Product { ... }
```

**Пример на коллекции:**
```java
@OneToMany
@BatchSize(size = 5)
Set<Product> getProducts() { ... }
```

#### Ответ от Claude

**Как работает @BatchSize**

`@BatchSize` — это оптимизация стратегии **lazy-загрузки**. Без неё каждое обращение к ленивой коллекции или прокси генерирует отдельный SQL-запрос (классическая проблема N+1). С `@BatchSize` Hibernate группирует несколько ещё-не-загруженных прокси в один запрос с условием `IN (...)`.

**Пример работы (N+1 без BatchSize):**

```sql
-- Загружаем 25 департаментов, затем для каждого читаем сотрудников:
SELECT * FROM department
SELECT * FROM employee WHERE department_id = 1
SELECT * FROM employee WHERE department_id = 2
-- ... 25 запросов итого = 1 + 25
```

**С @BatchSize(size = 10) на коллекции `employees`:**

```sql
SELECT * FROM department
-- Hibernate группирует первые 10 департаментов:
SELECT * FROM employee WHERE department_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
-- Следующие 10:
SELECT * FROM employee WHERE department_id IN (11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
-- Оставшиеся 5:
SELECT * FROM employee WHERE department_id IN (21, 22, 23, 24, 25)
-- Итого: 1 + 3 запроса вместо 26
```

**Сравнение с JOIN FETCH**

| Критерий | @BatchSize | JOIN FETCH |
|---|---|---|
| Количество SQL-запросов | Несколько (N/size + 1) | Один |
| Декартово произведение | Нет — отдельные SELECT | Есть при нескольких коллекциях |
| Пагинация | **Совместима** (корректный SQL LIMIT) | **Несовместима** с коллекциями |
| Дублирование строк | Нет | Возможно (нужен DISTINCT) |
| Применение | Аннотация на сущности/поле | Явная конструкция в JPQL |
| Тип загрузки | Lazy (по требованию) | Eager (сразу) |
| Несколько коллекций | Хорошо работает для каждой | Только одна коллекция без MultiBagFetchException |

**Когда @BatchSize предпочтительнее JOIN FETCH:**

1. **Пагинация** — главный сценарий. `@BatchSize` не мешает `LIMIT`/`OFFSET` на уровне SQL, а `JOIN FETCH` с коллекцией вызывает загрузку всех результатов в память.

2. **Несколько коллекций** — если сущность имеет несколько `@OneToMany`/`@ManyToMany` ассоциаций, JOIN FETCH по всем сразу вызывает `MultiBagFetchException` или декартово произведение. `@BatchSize` на каждой коллекции работает независимо.

3. **Не все связи нужны всегда** — `@BatchSize` сохраняет lazy-поведение и загружает данные только при реальном обращении, тогда как `JOIN FETCH` всегда тянет данные.

4. **Глобальная настройка** — можно задать `spring.jpa.properties.hibernate.default_batch_fetch_size=25` в `application.properties` и применить батчинг ко всем ленивым ассоциациям без изменения кода.

**Когда JOIN FETCH предпочтительнее @BatchSize:**

- Нужна одна коллекция и пагинация не используется — один запрос эффективнее
- Важна предсказуемость: ровно один SQL-запрос, а не переменное количество
- Используются DTO-проекции с явными JOIN

**Глобальная настройка в Spring Boot:**

```properties
spring.jpa.properties.hibernate.default_batch_fetch_size=25
```

Это наиболее практичный способ устранить N+1 проблемы в реальных приложениях без изменения аннотаций на каждой сущности.
### Вопрос 37. Чем отличается em.find() от em.getReference() (getOne() / getReferenceById() в Spring Data JPA)? Когда getReference() выбрасывает EntityNotFoundException и почему его предпочтительно использовать при установке связей?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [How do find and getReference EntityManager methods work when using JPA and Hibernate — Vlad Mihalcea](https://vladmihalcea.com/entitymanager-find-getreference-jpa/)

`EntityManager.find()` немедленно выполняет SQL-запрос SELECT и возвращает полностью инициализированный объект сущности. Если запись не найдена — возвращает `null`.

`EntityManager.getReference()` не обращается к базе данных немедленно. Он возвращает прокси-объект, у которого заполнен только идентификатор. Фактическая загрузка данных происходит лениво — при первом обращении к любому полю сущности внутри активной транзакции.

Когда используется `find()` для установки связи `@ManyToOne`, Hibernate выполняет лишний SELECT:
```sql
SELECT p.id, p.title FROM post p WHERE p.id = 1
INSERT INTO post_comment ...
```

При использовании `getReference()` SELECT отсутствует — только INSERT:
```sql
INSERT INTO post_comment ...
```

Это возможно потому, что прокси уже содержит нужное значение идентификатора для заполнения колонки внешнего ключа, и инициализировать весь объект не требуется.

`LazyInitializationException` может возникнуть, если попытаться обратиться к прокси после закрытия `EntityManager`.

#### Ответ от Claude

**Различия между `find()` и `getReference()`**

| Аспект | `find()` | `getReference()` |
|--------|----------|-----------------|
| Обращение к БД | Немедленно (при вызове метода) | Лениво (при первом доступе к полю) |
| Возвращаемый тип | Полностью инициализированная сущность или `null` | Прокси-объект (никогда не `null`, если метод завершился без исключения) |
| Поведение при отсутствии записи | Возвращает `null` | Выбрасывает `EntityNotFoundException` |

**Когда `getReference()` выбрасывает `EntityNotFoundException`**

Согласно спецификации JPA (Jakarta Persistence 3.x), исключение `EntityNotFoundException` выбрасывается **в момент первого обращения к состоянию сущности**, если запись в БД не существует. При этом провайдер вправе выбросить исключение и раньше — непосредственно при вызове `getReference()`.

Поведение Hibernate по умолчанию: исключение откладывается до инициализации прокси (lazy). При включённом параметре `hibernate.jpa.compliance.proxy=true` Hibernate выполняет SELECT уже при вызове `getReference()`, полностью следуя спецификации.

В Spring Data JPA метод `getOne()` устарел (deprecated) начиная с Spring Data 2.5 и заменён на `getReferenceById()`, который делегирует вызов `EntityManager.getReference()`.

**Почему `getReference()` предпочтительнее при установке связей**

При создании дочерней сущности (например, `PostComment`) и установке ссылки на родителя (`Post`) реальные данные родителя не нужны — достаточно значения первичного ключа для колонки внешнего ключа. Использование `find()` в этом случае порождает лишний SQL SELECT, что особенно заметно в batch-операциях (N+1 проблема). `getReference()` исключает этот запрос, поскольку прокси уже содержит идентификатор.

**Важное замечание:** `findById` в Spring Data JPA не гарантирует отсутствие гонки данных — родительская запись может быть удалена другой транзакцией в промежутке между проверкой и вставкой, что приведёт к нарушению ограничения внешнего ключа в любом случае.

---

### Вопрос 38. Что такое MultipleBagFetchException в Hibernate? Почему он возникает при попытке загрузить две коллекции через JOIN FETCH одновременно, и каковы два основных способа его устранения?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [The best way to fix the Hibernate MultipleBagFetchException — Vlad Mihalcea](https://vladmihalcea.com/hibernate-multiplebagfetchexception/)

`MultipleBagFetchException` — исключение Hibernate, которое выбрасывается при попытке одновременно загрузить несколько неупорядоченных коллекций (bag) через один JPQL-запрос с `JOIN FETCH`.

Причина: при объединении нескольких коллекций через JOIN результирующий набор строк представляет собой декартово произведение. Например, 50 сущностей `Post`, каждая с 20 комментариями и 10 тегами, дают 50 × 20 × 10 = 10 000 строк вместо 50. Поскольку bag (неупорядоченный `List`) не удаляет дубликаты, Hibernate не может корректно собрать объекты из такого результата.

**Решение 1 — несколько отдельных запросов:**
Каждая коллекция загружается отдельным JPQL-запросом в рамках одной транзакции. Контекст персистентности (первый уровень кэша) автоматически объединяет результаты, так как одна и та же сущность не может быть представлена двумя разными объектами в одном контексте:
```java
List<Post> posts = entityManager.createQuery(
    "select p from Post p left join fetch p.comments " +
    "where p.id between :minId and :maxId", Post.class)
    .getResultList();

posts = entityManager.createQuery(
    "select distinct p from Post p left join fetch p.tags " +
    "where p in :posts", Post.class)
    .getResultList();
```

**Решение 2 — MULTISET:**
Использование Blaze Persistence или jOOQ с поддержкой оператора `MULTISET`, который позволяет загружать несколько коллекций в одном SQL-запросе без декартового произведения.

Замена `List` на `Set` — распространённый, но неверный способ «устранения» проблемы: Hibernate перестаёт выбрасывать исключение, однако неявное декартово произведение никуда не исчезает и по-прежнему негативно влияет на производительность.

#### Ответ от Claude

**Что такое `MultipleBagFetchException`**

`MultipleBagFetchException` — исключение из пакета `org.hibernate.loader`, наследник `HibernateException`. Hibernate выбрасывает его, когда JPQL-запрос пытается одновременно загрузить (`JOIN FETCH`) две или более коллекции типа «bag» (неупорядоченный `List`, допускающий дубликаты).

Метод `getBagRoles()` исключения возвращает список ролей проблемных коллекций для диагностики.

**Почему возникает**

Каждый `JOIN FETCH` для коллекции «один ко многим» или «многие ко многим» умножает число строк в результате. При двух одновременных `JOIN FETCH` образуется декартово произведение обеих коллекций:

- `Post` (N строк) + `PostComment` (M записей на пост) + `Tag` (K тегов на пост) = N × M × K строк.

Hibernate не в состоянии корректно собрать объектный граф из такого результата для неупорядоченных коллекций, поэтому превентивно выбрасывает исключение на этапе разбора запроса.

**Два основных способа устранения**

1. **Разделение на несколько запросов (рекомендуется).** Каждая коллекция загружается отдельным запросом в рамках одной транзакции и одного контекста персистентности. Hibernate автоматически объединяет результаты через первый уровень кэша, поскольку управляет единственным экземпляром каждой сущности в рамках контекста. Это единственный способ, полностью устраняющий декартово произведение.

2. **MULTISET (через Blaze Persistence или jOOQ).** Позволяет загрузить несколько коллекций одним SQL-запросом без декартового произведения за счёт специальной конструкции, возвращающей вложенные результирующие наборы.

**Почему замена `List` на `Set` — не решение**

При замене типа коллекций на `Set` Hibernate не выбрасывает исключение, однако продолжает формировать декартово произведение на уровне SQL. Дубликаты отфильтровываются только на уровне Java после получения избыточного числа строк, что приводит к излишней нагрузке на базу данных и сеть.

---

### Вопрос 39. Чем @MappedSuperclass отличается от @Inheritance и от @Embeddable? В каком случае следует выбирать каждый из этих механизмов для переиспользования полей между сущностями?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Entity Inheritance — The Java EE 6 Tutorial (Oracle)](https://docs.oracle.com/javaee/6/tutorial/doc/bnbqn.html)

**`@MappedSuperclass`** — суперкласс, не являющийся сущностью, который содержит персистентное состояние и маппинг, разделяемые несколькими классами-сущностями. Суперкласс не помечается `@Entity`, не имеет собственной таблицы в базе данных, не может быть мишенью ассоциаций и не поддаётся полиморфным запросам. Каждый класс-наследник получает собственную таблицу, в которую копируются все унаследованные поля.

**`@Inheritance`** используется на корневом классе иерархии сущностей и поддерживает три стратегии:
- `SINGLE_TABLE` — все классы иерархии в одной таблице с дискриминаторной колонкой;
- `JOINED` — корневой класс и каждый подкласс в отдельных таблицах, связанных внешним ключом;
- `TABLE_PER_CLASS` — каждый конкретный класс в отдельной таблице со всеми унаследованными полями.

`@Inheritance` поддерживает полиморфные запросы: запрос к базовому типу возвращает объекты всех подтипов.

`@MappedSuperclass` следует выбирать, когда нужно разделить общее состояние или маппинг между несвязанными сущностями без полиморфных запросов. `@Inheritance` — когда требуется моделировать отношение IS-A с возможностью полиморфных запросов.

#### Ответ от Claude

**Сравнение трёх механизмов**

| Механизм | Является `@Entity` | Таблица в БД | Полиморфные запросы | Тип отношения |
|---|---|---|---|---|
| `@MappedSuperclass` | Нет | Нет (поля копируются в таблицы потомков) | Нет | Переиспользование полей (OOP-наследование) |
| `@Inheritance` | Да (корень и потомки) | Да (стратегия определяет количество) | Да | IS-A (реальная иерархия сущностей) |
| `@Embeddable` | Нет (встраиваемый тип) | Нет (поля хранятся в таблице владельца) | Нет | HAS-A (композиция, value object) |

**`@MappedSuperclass`**

Служит для выноса общих полей (идентификатор, версия, поля аудита) в базовый абстрактный класс. Базовый класс не имеет таблицы: при генерации DDL его поля добавляются в таблицы каждого наследника. Класс не может быть участником ассоциаций (`@OneToMany`, `@ManyToOne`) и не поддаётся запросу `from BaseEntity`.

Пример типичного использования — абстрактный `BaseEntity` с полями `@Id`, `@Version`, `createdAt`, `updatedAt`, от которого наследуются `Post`, `PostComment`, `Tag`.

**`@Inheritance`**

Предназначен для реальных иерархий сущностей, которые нужно запрашивать полиморфно. Аннотация размещается на корневом классе иерархии.

Стратегии:
- `SINGLE_TABLE` — наиболее производительная для полиморфных запросов (нет JOIN), но требует nullable-колонок для полей подклассов. Подходит для небольших иерархий.
- `JOINED` — нормализованная схема, нет избыточных столбцов, но каждый запрос требует JOIN. Подходит для глубоких иерархий с большим числом специфических полей.
- `TABLE_PER_CLASS` — редко используется; полиморфные запросы требуют UNION, поддержка опциональна.

**Важно:** `@MappedSuperclass` и `@Inheritance` нельзя использовать одновременно на одном классе.

**`@Embeddable`**

Описывает value object — тип без собственной идентичности, жизненный цикл которого полностью зависит от родительской сущности. Поля встраиваемого типа хранятся в таблице владельца (или в отдельной таблице при использовании `@ElementCollection`). Один и тот же `@Embeddable` можно повторно встроить в несколько разных сущностей с переопределением колонок через `@AttributeOverride`.

Начиная с Hibernate ORM 6.6 поддерживается наследование внутри `@Embeddable`-типов с использованием `@DiscriminatorColumn`.

**Когда выбирать каждый механизм**

- `@MappedSuperclass` — когда несколько несвязанных сущностей разделяют технические поля (PK, версия, аудит), но не нужна полиморфная адресация.
- `@Inheritance` — когда моделируется предметная IS-A иерархия и требуется возможность запрашивать базовый тип (`from Animal` возвращает `Dog` и `Cat`).
- `@Embeddable` — когда поля логически представляют единый value object (адрес, денежная сумма, период), не имеющий смысла вне контекста родительской сущности; предпочтительна композиция вместо наследования.

---
### Вопрос 40. Как реализовать мягкое удаление (soft delete) в Hibernate с помощью @SQLDelete и @SQLRestriction (ранее @Where)? Чем @SoftDelete (Hibernate 6.4+) упрощает эту задачу и какие ограничения сохраняются при работе с кэшем и каскадными ассоциациями?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [The best way to soft delete with Hibernate — Vlad Mihalcea](https://vladmihalcea.com/the-best-way-to-soft-delete-with-hibernate/)

Мягкое удаление (soft delete) означает пометку записи как удалённой вместо физического удаления строки из таблицы. Классическая реализация на Hibernate использует два аннотации:

**@SQLDelete** переопределяет SQL, который Hibernate выполняет при вызове `delete()`. Вместо `DELETE FROM post WHERE id = ?` выполняется `UPDATE post SET deleted = true WHERE id = ?`:

```java
@Entity
@SQLDelete(sql = "UPDATE post SET deleted = true WHERE id = ?")
@Where(clause = "deleted = false")  // устаревший способ (Hibernate < 6.3)
public class Post {
    @Id
    private Long id;
    private boolean deleted = false;
    // ...
}
```

С Hibernate 6.3 аннотация `@Where` была заменена на `@SQLRestriction`:

```java
@Entity
@SQLDelete(sql = "UPDATE post SET deleted = true WHERE id = ?")
@SQLRestriction("deleted = false")
public class Post { ... }
```

Для того чтобы прямая загрузка по ID (`em.find()`) тоже учитывала soft-delete, необходимо дополнительно добавить `@Loader` с именованным запросом:

```java
@Loader(namedQuery = "findPostById")
@NamedQuery(name = "findPostById",
    query = "SELECT p FROM Post p WHERE p.id = ?1 AND p.deleted = false")
```

**Ключевые ограничения @SQLRestriction:**
- Ограничение применяется всегда и не может быть отключено в рантайме.
- Нельзя передавать параметры — условие статично.
- Значительно менее гибко, чем `@Filter`, который поддерживает включение/отключение на уровне сессии.

**Кэш второго уровня**: при использовании `@SQLDelete` Hibernate выполняет кастомный UPDATE через нативный SQL. Hibernate не всегда может определить, какие таблицы затронул нативный запрос, и может инвалидировать избыточно много регионов кэша.

**Каскадные ассоциации**: дочерние сущности в коллекциях `@OneToMany` также должны иметь собственный `@SQLRestriction`, иначе при загрузке коллекции они будут включены в результат. Управление каскадом требует отдельной проработки.

#### Ответ от Claude

**Реализация через @SQLDelete + @SQLRestriction**

Soft delete — паттерн, при котором строка не удаляется физически, а помечается флагом (например, `deleted = true` или `deleted_at = NOW()`). Hibernate предоставляет два механизма для его реализации:

1. **@SQLDelete** — переопределяет SQL, генерируемый при вызове `EntityManager.remove()` / `Session.delete()`. Вместо `DELETE` выполняется `UPDATE`.

2. **@SQLRestriction** (Hibernate 6.3+, замена устаревшей `@Where`) — добавляет статический SQL-предикат ко всем автоматически генерируемым запросам для данной сущности или коллекции.

```java
@Entity
@Table(name = "post")
@SQLDelete(sql = "UPDATE post SET deleted = true WHERE id = ?")
@SQLRestriction("deleted = false")
public class Post {
    @Id
    @GeneratedValue
    private Long id;

    private boolean deleted = false;

    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL)
    @SQLRestriction("deleted = false")   // нужно повторить для коллекции
    private List<Comment> comments = new ArrayList<>();
}
```

**Важно**: `@SQLRestriction` не применяется при загрузке сущности напрямую по идентификатору (`em.find()`), если не добавить `@Loader` с именованным запросом (Hibernate 5/6 без `@SoftDelete`).

**@SoftDelete (Hibernate 6.4+)**

Аннотация `@SoftDelete` унифицирует всю вышеперечисленную конфигурацию в одной декларации:

```java
@Entity
@Table(name = "tag")
@SoftDelete
public class Tag { ... }
```

Hibernate автоматически:
- Генерирует `UPDATE ... SET deleted = true WHERE id = ? AND deleted = false` вместо `DELETE`.
- Добавляет предикат `deleted = false` во все JPQL/Criteria-запросы.
- Корректно обрабатывает загрузку по первичному ключу (`em.find()`).

Настраиваемые параметры `@SoftDelete`:
- `strategy` — `SoftDeleteType.DELETED` (хранит `true` для удалённых, по умолчанию) или `SoftDeleteType.ACTIVE` (хранит `true` для активных).
- `columnName` — имя столбца-индикатора (по умолчанию `deleted`).
- `converter` — конвертер для нестандартных типов индикатора.

**Ограничения, сохраняющиеся в обоих подходах**

*Кэш второго уровня:*
- При soft delete Hibernate выполняет UPDATE вместо DELETE. Для `@SQLDelete` этот UPDATE является нативным SQL. Hibernate не знает, какие таблицы затрагивает нативный запрос, и может инвалидировать все регионы кэша второго уровня — это избыточно и снижает производительность.
- Решение: использовать `addSynchronizedEntityClass()` при работе с нативными запросами, чтобы ограничить инвалидацию конкретными сущностями. Для `@SoftDelete` ситуация лучше, поскольку Hibernate управляет UPDATE сам и правильно отслеживает изменения.
- После мягкого удаления запись с `deleted = true` может оставаться в кэше второго уровня как «живая» запись, пока кэш не будет инвалидирован. Необходимо явно выгонять (evict) сущность из кэша после soft delete.

*Каскадные ассоциации:*
- Ассоциации `@OneToMany` и `@ManyToMany` требуют **собственного** `@SQLRestriction` / `@SQLDelete` на уровне коллекции, иначе при загрузке коллекции мягко удалённые дочерние сущности попадут в результат.
- При использовании `@SoftDelete` с `@ManyToOne` и lazy-загрузкой необходимо добавить `@NotFound(action = NotFoundAction.IGNORE)`, так как внешний ключ может ссылаться на мягко удалённую запись — её физически нет в результатах запроса, но FK существует в БД.
- Каскадное soft delete автоматически не работает: если удалить родителя с `cascade = CascadeType.REMOVE`, дочерние записи Hibernate попытается тоже удалить через `@SQLDelete`-механизм, но только если у них настроен аналогичный soft delete. Иначе они будут физически удалены.

*Различие между источниками:*
- Vladmihalcea.com и документация Hibernate сходятся в том, что `@SQLRestriction` всегда применяется и не параметризуется. Baeldung описывает более старый подход с `@Where`, который устарел в Hibernate 6.3.

---

