# JPA и Hibernate — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/16-jpa-hibernate.md](../knowledge-base/16-jpa-hibernate.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](jpa-hibernate-01.md) · [ч.2](jpa-hibernate-02.md) · **ч.3**

---
### Вопрос 41. Что такое кэш запросов (Query Cache) в Hibernate? Как он связан с кэшем второго уровня, почему по умолчанию отключён и какую проблему порождает выполнение нативных DML-запросов (UPDATE/DELETE) при включённом Query Cache?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How does Hibernate Query Cache work — Vlad Mihalcea](https://vladmihalcea.com/how-does-hibernate-query-cache-work/)

**Что такое Query Cache**

Query Cache (кэш запросов) — специальный кэш Hibernate, который хранит результаты выполненных JPQL/HQL-запросов. В отличие от кэша второго уровня (L2 Cache), который кэширует сущности по первичному ключу, Query Cache хранит ассоциацию: «параметры запроса → список идентификаторов сущностей».

**Связь с L2 Cache**

Query Cache не хранит сами данные сущностей. Он хранит только список идентификаторов (entity IDs), соответствующих критериям запроса. При повторном выполнении запроса:
1. Hibernate проверяет Query Cache — если есть попадание, получает список ID.
2. Для каждого ID загружает сущность из кэша второго уровня.
3. Если сущность не найдена в L2, обращается к базе данных.

Таким образом, Query Cache имеет смысл только при включённом L2 Cache.

**Почему отключён по умолчанию**

Query Cache отключён по умолчанию (`hibernate.cache.use_query_cache=false`), потому что:
- Он подвержен проблемам консистентности.
- Без надлежащего управления памятью может неконтролируемо вырасти.
- Большинство запросов не выигрывают от кэширования результатов.
- Накладные расходы на управление инвалидацией нередко превышают выгоду.

Дополнительно каждый запрос должен быть явно помечен как кэшируемый через `.setCacheable(true)`, даже при включённом Query Cache глобально.

**Проблема нативных DML-запросов**

При обычных операциях Hibernate точно знает, какие таблицы были изменены, и инвалидирует только связанные регионы Query Cache. Но при выполнении нативного SQL (через `createNativeQuery()`):

> «When it comes to native SQL DML statements, Hibernate can't guess what's being updated, so it invalidates all regions of the second-level cache, regardless of the relationships between the entity been updated and the others.»

Hibernate не может определить, какие таблицы затронул нативный запрос, поэтому инвалидирует **все** регионы кэша второго уровня и Query Cache — даже те, которые не имеют отношения к изменённым данным. Это ведёт к резкому падению hit rate кэша.

**Решение**: сообщить Hibernate об изменяемых таблицах через `addSynchronizedEntityClass()`:

```java
session.createNativeQuery(
    "UPDATE post SET status = 'PUBLISHED' WHERE id = :id")
    .addSynchronizedEntityClass(Post.class)
    .setParameter("id", postId)
    .executeUpdate();
```

Это ограничивает инвалидацию только регионами, связанными с `Post`.

#### Ответ от Claude

**Query Cache: механизм работы**

Query Cache — это отдельный регион кэша, который хранит пары «ключ запроса → список идентификаторов результата». Ключ включает текст запроса, его параметры и позицию (первая/максимальное количество строк).

Включение:
```properties
hibernate.cache.use_query_cache=true
```
И явная пометка каждого запроса:
```java
List<Post> posts = em.createQuery("FROM Post p WHERE p.status = :s", Post.class)
    .setParameter("s", Status.PUBLISHED)
    .setHint("org.hibernate.cacheable", true)
    .getResultList();
```

**Связь с L2 Cache**

Query Cache и L2 Cache — взаимосвязанные, но разные слои:

| Слой | Что хранит | Ключ |
|------|-----------|------|
| L2 Cache | Состояние сущностей | Тип + PK |
| Query Cache | Список ID результатов | Текст запроса + параметры |

Query Cache сам по себе бесполезен без L2 Cache: получив из него список ID, Hibernate всё равно должен загрузить сущности — либо из L2 Cache, либо из БД.

Также Hibernate ведёт вспомогательный регион `default-update-timestamps-region`, где для каждой таблицы хранится временная метка последнего изменения. При проверке Query Cache Hibernate сравнивает метку кэшированного результата с меткой таблицы — если таблица изменилась позже, результат считается устаревшим и кэш инвалидируется.

**Почему отключён по умолчанию**

1. **Накладные расходы на инвалидацию**: каждое изменение сущности (persist/merge/remove) приводит к инвалидации всех кэшированных запросов по соответствующей таблице, даже если изменение не влияет на результат конкретного запроса.
2. **Бесполезность для большинства запросов**: Query Cache полезен только для часто повторяющихся запросов с одинаковыми параметрами и редко изменяемыми данными (например, справочники).
3. **Риск неконтролируемого роста памяти**: без ограничений размер кэша может расти.
4. **Консистентность**: сложность обеспечения согласованности между кэшем и БД в конкурентных сценариях.

**Проблема нативных DML-запросов**

Когда Hibernate выполняет JPQL/HQL, он точно знает, какие сущности (и таблицы) затронуты, и инвалидирует только соответствующие регионы. При нативном SQL через `createNativeQuery()` Hibernate не парсит запрос и не может определить список затронутых таблиц.

Поведение по умолчанию: **инвалидация всех регионов** кэша второго уровня и Query Cache. Это означает, что один нативный `UPDATE post SET ...` полностью сбрасывает кэши для `Author`, `Comment`, `Tag` и всех других сущностей — даже если они не имеют отношения к изменению.

**Решения:**

1. **addSynchronizedEntityClass / addSynchronizedQuerySpace** — явно указать Hibernate затронутые таблицы:
```java
// Инвалидирует только Post-регион
session.createNativeQuery("UPDATE post SET status = 'PUBLISHED' WHERE id = :id")
    .addSynchronizedEntityClass(Post.class)
    .setParameter("id", 1L)
    .executeUpdate();
```

2. **Использовать JPQL/HQL вместо нативного SQL** там, где это возможно — Hibernate сам управляет инвалидацией.

3. **Отключить Query Cache** для таблиц, которые часто изменяются нативными запросами.

*Расхождение между источниками:* Vladmihalcea.com и официальная документация Hibernate (глава Caching) описывают проблему одинаково. Документация Hibernate 5.x и 6.x не изменила поведение нативного DML в части инвалидации кэша.

---

### Вопрос 42. Чем интерфейсные проекции (Interface Projections) отличаются от проекций на основе класса (DTO / Constructor Expression) в Spring Data JPA? В чём разница между fetchgraph и loadgraph при использовании EntityGraph?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Projections — Spring Data JPA Reference Documentation](https://docs.spring.io/spring-data/jpa/reference/repositories/projections.html)

**Интерфейсные проекции (Interface Projections)**

Интерфейсные проекции определяются как Java-интерфейс с геттерами, соответствующими полям сущности:

```java
interface NamesOnly {
    String getFirstname();
    String getLastname();
}

interface PersonRepository extends Repository<Person, UUID> {
    Collection<NamesOnly> findByLastname(String lastname);
}
```

Spring Data создаёт прокси-объекты, реализующие этот интерфейс, в рантайме. Для *закрытых проекций* (closed projections), где все геттеры соответствуют полям сущности, Spring Data может оптимизировать запрос и выбрать только нужные колонки. *Открытые проекции* (open projections) используют `@Value` со SpEL-выражениями и не позволяют оптимизировать запрос.

Поддерживаются вложенные проекции через возврат другого интерфейса-проекции.

**Проекции на основе класса (DTO Projections)**

DTO-проекции используют реальные классы или Java Records:

```java
record NamesOnly(String firstname, String lastname) {}
```

JPA использует constructor expression в JPQL: `SELECT new com.example.NamesOnly(u.firstname, u.lastname) FROM User u`. Spring Data JPA может автоматически переписывать запрос для добавления конструкторного выражения.

Ключевые отличия:
- Прокси не создаётся — создаются реальные экземпляры.
- Вложенные проекции не поддерживаются.
- Требуется единственный конструктор (или `@PersistenceCreator` для выбора нужного).
- Java Records идеальны: компактный синтаксис, автоматические `equals`/`hashCode`/`toString`.

**Разница fetchgraph и loadgraph**

Тип задаётся атрибутом `type` на аннотации `@EntityGraph`:

```java
@EntityGraph(value = "GroupInfo.detail", type = EntityGraphType.LOAD)
GroupInfo getByGroupName(String name);
```

Различие определено в спецификации JPA 2.1 (раздел 3.7.4):
- `FETCH` (fetchgraph): загружаются **только** атрибуты, явно указанные в графе. Остальные атрибуты, даже помеченные `FetchType.EAGER`, обрабатываются как `LAZY`.
- `LOAD` (loadgraph): загружаются атрибуты из графа **плюс** все атрибуты, статически помеченные `FetchType.EAGER` в маппинге.

#### Ответ от Claude

**Interface Projections vs DTO (Class) Projections**

| Характеристика | Interface Projections | DTO / Class Projections |
|---------------|----------------------|------------------------|
| Механизм | Прокси-объект в рантайме | Реальный экземпляр класса (constructor expression) |
| Вложенные проекции | Поддерживаются | Не поддерживаются |
| equals / hashCode | Не реализуемы кастомно | Полный контроль (особенно в Records) |
| Оптимизация запроса | Для closed projections (только нужные колонки) | Всегда — конструктор определяет выбираемые поля |
| Open projections (@Value + SpEL) | Поддерживаются | Не поддерживаются |
| Синтаксис | Интерфейс с геттерами | Класс/Record с конструктором |
| Применимость | Быстрый прототип, read-only | Сложная логика, сериализация, тесты на равенство |

**Детали интерфейсных проекций:**
- *Closed projection* — все методы интерфейса однозначно отображаются на поля сущности. Spring Data может оптимизировать SQL (выбирать только нужные колонки).
- *Open projection* — хотя бы один метод использует `@Value("#{target.firstname + ' ' + target.lastname}")`. Оптимизация SQL невозможна, загружается вся сущность.
- Прокси создаётся JDK dynamic proxy; нельзя добавить кастомную реализацию `equals`/`hashCode`, что ограничивает использование в коллекциях (`Set`, `Map`).

**Детали DTO-проекций:**
- Spring Data JPA автоматически добавляет constructor expression в JPQL на основе параметров конструктора.
- Java Records — рекомендуемый подход: `private final` поля, автоматические `equals`/`hashCode`/`toString`, компактный синтаксис.
- Требуется единственный конструктор или `@PersistenceCreator` для указания нужного.

**fetchgraph vs loadgraph в EntityGraph**

EntityGraph позволяет управлять стратегией загрузки ассоциаций на уровне конкретного запроса, не меняя маппинг сущности.

*Определение графа:*
```java
@Entity
@NamedEntityGraph(name = "Post.withComments",
    attributeNodes = @NamedAttributeNode("comments"))
public class Post {
    @OneToMany(fetch = FetchType.LAZY)
    private List<Comment> comments;

    @ManyToOne(fetch = FetchType.EAGER)
    private Author author;
}
```

*Использование в Spring Data JPA:*
```java
// fetchgraph — загружает ТОЛЬКО comments; author будет LAZY (несмотря на EAGER в маппинге)
@EntityGraph(value = "Post.withComments", type = EntityGraphType.FETCH)
List<Post> findByStatus(Status status);

// loadgraph — загружает comments (из графа) + author (EAGER из маппинга)
@EntityGraph(value = "Post.withComments", type = EntityGraphType.LOAD)
List<Post> findByStatus(Status status);
```

| Тип | Атрибуты из графа | Атрибуты вне графа с EAGER | Атрибуты вне графа с LAZY |
|-----|------------------|---------------------------|--------------------------|
| FETCH (fetchgraph) | Загружаются EAGER | Становятся LAZY | LAZY |
| LOAD (loadgraph) | Загружаются EAGER | Остаются EAGER | LAZY |

**Практические рекомендации:**
- Используйте `FETCH` для переопределения `FetchType.EAGER` на `LAZY` в legacy-коде или для точного контроля загрузки — только то, что нужно.
- Используйте `LOAD` для добавления дополнительных eager-загрузок поверх уже существующих настроек маппинга.
- Предпочитайте `FETCH` в новом коде: он позволяет явно задать список загружаемых ассоциаций и избежать N+1 запросов без неожиданных побочных эффектов от EAGER-маппинга.

*Источники:* JPA 2.1 Specification §3.7.4; Spring Data JPA Reference Documentation (Projections); Oracle Java EE 7 Tutorial §43.1; Vladmihalcea.com (fetchgraph vs loadgraph).
### Вопрос 43. Что такое versionless optimistic locking в Hibernate (@OptimisticLocking с типом DIRTY или ALL)? Чем он отличается от стандартного @Version, и в каком сценарии он не способен защитить от потерянных обновлений (lost update)?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How to prevent OptimisticLockException with Hibernate versionless optimistic locking — Vlad Mihalcea](https://vladmihalcea.com/how-to-prevent-optimisticlockexception-using-hibernate-versionless-optimistic-locking/)

Versionless optimistic locking — это механизм оптимистичной блокировки без выделенного столбца версии. Он управляется аннотацией `@OptimisticLocking`, которая принимает одно из четырёх значений типа `OptimisticLockType`:

- `VERSION` (по умолчанию) — стандартное поведение, версия контролируется через `@Version`.
- `NONE` — оптимистичная блокировка отключена.
- `ALL` — в предложение WHERE оператора UPDATE/DELETE включаются **все** поля сущности.
- `DIRTY` — в предложение WHERE включаются только **изменённые (dirty)** поля.

Вместо поддержки суррогатного счётчика версии Hibernate формирует расширенный WHERE-clause, который содержит исходные значения полей, считанных из базы. Если при обновлении ни одна строка не попала под условие (UPDATE вернул 0 затронутых строк), Hibernate делает вывод, что другая транзакция уже изменила данные, и выбрасывает `OptimisticLockException`.

Пример SQL для сущности `Product` с `OptimisticLockType.DIRTY`, когда изменилось поле `quantity`:

```sql
UPDATE product SET quantity = ? WHERE id = ? AND quantity = ?
```

Тип `DIRTY` требует совместного применения с `@DynamicUpdate` (чтобы Hibernate формировал UPDATE только изменённых столбцов) и `@SelectBeforeUpdate`.

**Ограничение — detached-сущности.** Versionless locking принципиально работает только при открытом Persistence Context (в рамках одной сессии). Когда сессия закрывается и сущность становится detached, Hibernate теряет исходный снимок состояния (snapshot). При последующем merge() или reattach() в новой сессии Hibernate вынужден сначала загрузить текущее состояние из БД — и именно с ним сравнивает изменения. Исходный снимок, который нужен для WHERE-clause, безвозвратно утрачен. В результате изменения Alice могут перезаписать более свежие изменения Bob, то есть lost update не предотвращается. Цитата из источника: «once the original Session is gone, we have no way of including the original entity state in the UPDATE WHERE clause».

**Отличия от `@Version`:**

| Аспект | `@Version` | `@OptimisticLocking ALL/DIRTY` |
|---|---|---|
| Выделенный столбец | Да (`version` / `timestamp`) | Нет |
| Поддержка legacy-схем | Нет (нужно добавить столбец) | Да |
| Работа с detached-сущностями | Да (версия хранится в объекте) | Нет (теряется snapshot) |
| SQL WHERE при UPDATE | `WHERE id=? AND version=?` | `WHERE id=? AND col1=? AND col2=?` |
| Гранулярность | Вся сущность | ALL — всё; DIRTY — только грязные поля |

#### Ответ от Claude

**Что такое versionless optimistic locking.** Hibernate поддерживает два семейства оптимистичной блокировки. Первое — стандартное JPA: поле, помеченное `@Version`, хранит инкрементируемый счётчик (или timestamp). При каждом UPDATE Hibernate добавляет `AND version = <старое_значение>` и инкрементирует версию. Если UPDATE затронул 0 строк, выбрасывается `OptimisticLockException`. Второе семейство — versionless: аннотация `@OptimisticLocking(type = OptimisticLockType.ALL|DIRTY)` без какого-либо поля-счётчика. Механизм защиты от конфликтов — расширенный WHERE-clause с исходными значениями полей.

**`ALL` vs `DIRTY`.** При `ALL` WHERE-clause включает все поля сущности (кроме тех, что помечены `@OptimisticLock(excluded=true)`). При `DIRTY` — только те поля, которые были изменены в рамках текущей сессии. `DIRTY` снижает вероятность ложных конфликтов (двое редактируют разные поля), тогда как `ALL` конфликтует при любом параллельном изменении. `DIRTY` требует `@DynamicUpdate` и `@SelectBeforeUpdate`.

**Когда versionless locking не защищает от lost update.** Единственный сценарий, в котором versionless locking принципиально бессилен — работа с detached-сущностями (паттерн session-per-request). Алгоритм merge():

1. Hibernate загружает текущую версию сущности из БД в новый Persistence Context.
2. Копирует состояние detached-объекта поверх загруженного.
3. При flush выполняет UPDATE.

На шаге 3 Hibernate сравнивает состояние "до" и "после" в рамках **новой** сессии — и "до" совпадает с текущим состоянием БД (только что загруженным). Исходный снимок из первой сессии утрачен. WHERE-clause будет содержать актуальные (не исходные) значения, так что UPDATE успешно пройдёт, даже если другая транзакция уже обновила данные. Потерянное обновление не обнаруживается.

С `@Version` этот сценарий безопасен, потому что номер версии хранится непосредственно в объекте и не зависит от сессии.

**Итог: когда применять versionless locking.** Исключительно для legacy-схем, где нельзя добавить столбец версии, и только при паттерне "один long-lived Persistence Context" (не session-per-request). Для типичных веб-приложений с detached-сущностями правильный выбор — `@Version`.

---

### Вопрос 44. Как работает оптимистичная блокировка через @Version при операции merge() с detached-сущностью? Что происходит, если версия detached-объекта устарела по сравнению с версией в БД, и какое исключение бросается в Spring?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Optimistic locking with JPA and Hibernate — Vlad Mihalcea](https://vladmihalcea.com/optimistic-locking-version-property-jpa-hibernate/)

При наличии поля `@Version` Hibernate включает версию в UPDATE-запрос:

```sql
UPDATE product SET quantity = 0, version = 2 WHERE id = 1 AND version = 1
```

Когда сущность становится detached и впоследствии возвращается через `merge()`, Hibernate выполняет следующую последовательность:

1. Загружает текущую запись из БД (получает актуальную версию, например `version = 2`).
2. Копирует состояние detached-объекта (у которого, например, `version = 1`) на загруженный managed-объект.
3. Обнаруживает несоответствие версий в момент копирования состояния и немедленно выбрасывает `OptimisticLockException` — ещё до выполнения UPDATE.

Цитата из источника: «When Alice tries to merge the detached Product entity, an OptimisticLockException will be thrown because the Product version has changed. When copying the detached entity state onto the newly loaded Product entity, Hibernate detects that the version has changed, hence it throws the OptimisticLockException right away, therefore skipping the UPDATE which would have failed with the same exception.»

В основе — `StaleStateException` из Hibernate, которая оборачивается в JPA-исключение `jakarta.persistence.OptimisticLockException`.

#### Ответ от Claude

**Механизм merge() при `@Version`.** Операция `merge()` в JPA не возвращает переданный объект в managed-состояние — она возвращает **новый** managed-объект, загруженный из БД, на который скопировано состояние detached-аргумента. Ключевой момент: поле `@Version` является частью этого состояния. При копировании Hibernate сравнивает версию detached-объекта с версией только что загруженной записи:

- Если версии совпадают — копирование продолжается, при flush Hibernate выполнит `UPDATE ... WHERE id=? AND version=?`.
- Если версии не совпадают — Hibernate немедленно бросает исключение, не дожидаясь flush/commit.

**Что происходит пошагово (версия устарела).**

```
Шаг 1: Alice загрузила Product(id=1, version=1) -> сессия закрыта, объект detached
Шаг 2: Bob обновил Product(id=1), version стала 2 -> commit
Шаг 3: Alice вызывает merge(detachedProduct) в новой сессии
  -> Hibernate выполняет SELECT: Product(id=1, version=2) из БД
  -> Hibernate пытается скопировать detached.version=1 на managed.version=2
  -> Несоответствие! -> выброс исключения до любого UPDATE
```

**Цепочка исключений.**

Hibernate (внутри): `org.hibernate.StaleObjectStateException` (подкласс `StaleStateException`).

JPA-слой (если Hibernate поднят через JPA): `jakarta.persistence.OptimisticLockException` (обёртка над Hibernate-исключением).

Spring (через `EntityManagerFactoryUtils.convertJpaAccessExceptionIfPossible()`): `org.springframework.orm.jpa.JpaOptimisticLockingFailureException`.

Полная иерархия Spring-исключения:
```
DataAccessException
  -> TransientDataAccessException
    -> ConcurrencyFailureException
      -> OptimisticLockingFailureException
        -> ObjectOptimisticLockingFailureException
          -> JpaOptimisticLockingFailureException   <- бросается Spring
```

`JpaOptimisticLockingFailureException` появился в Spring Framework 2.0. Его конструктор принимает `jakarta.persistence.OptimisticLockException` и делает его доступным через `getCause()`.

**Расхождение между источниками.** Vlad Mihalcea указывает, что исключение бросается в момент копирования состояния (до flush). Официальная документация Hibernate допускает, что в некоторых сценариях (например, при bulk-операциях через JPQL) `OptimisticLockException` может быть выброшен позже — при flush или commit. Для merge() с detached-сущностью и явным `@Version`-полем поведение однозначное: исключение возникает до flush.

**Рекомендуемая обработка.** После `JpaOptimisticLockingFailureException` следует перечитать сущность в новой транзакции (`find()`/`refresh()`), показать пользователю актуальное состояние и предложить повторить операцию.

---

### Вопрос 45. Чем пессимистичная блокировка (LockModeType.PESSIMISTIC_WRITE / PESSIMISTIC_READ) отличается от оптимистичной? Какой SQL генерирует Hibernate для каждого типа и в каких сценариях пессимистичная блокировка предпочтительнее?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How do LockModeType.PESSIMISTIC_READ and LockModeType.PESSIMISTIC_WRITE work in JPA and Hibernate — Vlad Mihalcea](https://vladmihalcea.com/hibernate-locking-patterns-how-do-pessimistic_read-and-pessimistic_write-work/)

`PESSIMISTIC_READ` устанавливает разделяемую (shared) блокировку: несколько транзакций могут одновременно удерживать такую блокировку, но запись в заблокированные строки блокируется. `PESSIMISTIC_WRITE` устанавливает эксклюзивную блокировку: только одна транзакция удерживает её, все прочие блокировки (в т. ч. `PESSIMISTIC_READ`) — несовместимы.

Генерируемый SQL зависит от диалекта БД:

| Lock mode | PostgreSQL | MySQL | Oracle |
|---|---|---|---|
| `PESSIMISTIC_READ` | `SELECT ... FOR SHARE` | `SELECT ... LOCK IN SHARE MODE` | `SELECT ... FOR UPDATE` |
| `PESSIMISTIC_WRITE` | `SELECT ... FOR UPDATE` | `SELECT ... FOR UPDATE` | `SELECT ... FOR UPDATE` |

Примечание: Oracle не поддерживает разделяемые блокировки на уровне строк, поэтому для `PESSIMISTIC_READ` Oracle применяет `FOR UPDATE` (эксклюзивная блокировка). Если база данных не поддерживает shared-блокировки, Hibernate автоматически переходит на `PESSIMISTIC_WRITE`.

Все пессимистичные блокировки удерживаются до завершения транзакции (commit или rollback).

Матрица совместимости блокировок:
- `PESSIMISTIC_READ` + `PESSIMISTIC_READ` — совместимы (обе транзакции продолжают работу).
- `PESSIMISTIC_READ` + `PESSIMISTIC_WRITE` — несовместимы (одна из транзакций блокируется).
- `PESSIMISTIC_WRITE` + любая — несовместимы.

#### Ответ от Claude

**Принципиальное отличие от оптимистичной блокировки.**

Оптимистичная блокировка не устанавливает никаких блокировок на уровне СУБД. Транзакция читает данные, выполняет бизнес-логику, а конфликт обнаруживается только в момент записи (по полю `@Version` или по расширенному WHERE-clause). Если конфликт обнаружен — транзакция откатывается. Подходит для сценариев с низкой вероятностью конфликтов.

Пессимистичная блокировка захватывает блокировку на уровне СУБД немедленно при чтении строки. Другие транзакции, пытающиеся получить несовместимую блокировку, будут ждать (или немедленно получат ошибку при использовании `PESSIMISTIC_NO_WAIT`). Конфликт предотвращается, а не обнаруживается постфактум.

**Как применяется в JPA/Hibernate.**

Блокировка задаётся через:
- `entityManager.find(Entity.class, id, LockModeType.PESSIMISTIC_WRITE)`
- `entityManager.lock(entity, LockModeType.PESSIMISTIC_WRITE)`
- `query.setLockMode(LockModeType.PESSIMISTIC_READ)`
- Аннотация `@Lock` в Spring Data JPA на методе репозитория.

**SQL, генерируемый Hibernate (PostgreSQL).**

`PESSIMISTIC_READ`:
```sql
SELECT p.id, p.title, p.quantity
FROM product p
WHERE p.id = 1
FOR SHARE
```

`PESSIMISTIC_WRITE`:
```sql
SELECT p.id, p.title, p.quantity
FROM product p
WHERE p.id = 1
FOR UPDATE
```

**Дополнительный режим:** `PESSIMISTIC_FORCE_INCREMENT` — работает как `PESSIMISTIC_WRITE`, но дополнительно инкрементирует поле `@Version`. Полезно, когда нужно зафиксировать факт чтения в журнале версий.

**Когда пессимистичная блокировка предпочтительнее.**

1. Высокая конкуренция за одни и те же строки. Если конфликты оптимистичных блокировок происходят часто (много пессимистичных retry), пессимистичная блокировка устраняет накладные расходы на откат и повтор транзакции.
2. Длинные бизнес-транзакции, в ходе которых нельзя допустить изменения данных третьей стороной.
3. Сценарии, где немедленный отказ критичен. `PESSIMISTIC_NO_WAIT` (hint `javax.persistence.lock.timeout = 0`) позволяет получить ошибку немедленно, а не ждать.
4. Операции "прочитать — изменить — записать" с гарантированной целостностью, например, снятие средств с банковского счёта.

**Ограничения пессимистичной блокировки.**

- Риск дедлоков при неправильном порядке захвата блокировок.
- Снижение параллелизма и пропускной способности.
- Блокировки удерживаются до конца транзакции, что при длинных транзакциях приводит к длительному ожиданию других клиентов.
- Не работают через границу HTTP-запроса (блокировки нельзя держать между запросами — транзакция должна завершаться внутри одного запроса).

**Расхождение между источниками.** Vlad Mihalcea и официальная документация Hibernate согласны в том, что Oracle не поддерживает `FOR SHARE` и использует `FOR UPDATE` для обоих режимов. Baeldung описывает MySQL как использующий `LOCK IN SHARE MODE` для `PESSIMISTIC_READ`, тогда как в MySQL 8+ синтаксис изменился на `FOR SHARE` — Hibernate использует актуальный вариант в зависимости от версии диалекта.
### Вопрос 46. Что такое StatelessSession в Hibernate? Чем она отличается от обычной Session с точки зрения кэширования, dirty checking и каскадирования, и когда её использование оправдано?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Chapter 13. Batch processing — Hibernate ORM 3.3 Reference Documentation](https://docs.hibernate.org/orm/3.3/reference/en-US/html/batch.html)

`StatelessSession` — это командно-ориентированный API Hibernate, предназначенный для потоковой передачи данных в базу данных и из неё в виде отсоединённых объектов. Он является абстракцией более низкого уровня, гораздо более близкой к базовому JDBC.

Ключевые характеристики `StatelessSession`:
- **Нет кэша первого уровня**: `StatelessSession` не реализует кэш первого уровня и не взаимодействует ни с кэшем второго уровня, ни с кэшем запросов.
- **Нет dirty checking**: `StatelessSession` не реализует автоматическую проверку изменённых данных.
- **Нет каскадирования**: операции, выполняемые через `StatelessSession`, никогда не каскадируют к связанным экземплярам.
- **Коллекции игнорируются**: коллекции сущностей игнорируются `StatelessSession`.
- **Обход инфраструктуры Hibernate**: операции обходят модель событий Hibernate и перехватчики (interceptors).
- **Уязвимость к data aliasing**: из-за отсутствия кэша первого уровня возможны эффекты подмены данных (data aliasing effects).

Для определённых типов транзакций `StatelessSession` может работать несколько быстрее, чем обычная `Session`.

#### Ответ от Claude

`StatelessSession` — это альтернативный интерфейс Hibernate для работы с базой данных, существующий более 20 лет. В отличие от стандартной `Session`, у неё **нет контекста персистентности** (Persistence Context), что радикально меняет её поведение.

**Сравнение с Session по ключевым аспектам:**

| Характеристика | Session | StatelessSession |
|---|---|---|
| Persistence Context | Есть | Отсутствует |
| Кэш первого уровня | Да | Нет |
| Взаимодействие со 2-м уровнем кэша | Да | Нет |
| Dirty Checking | Автоматический | Отсутствует |
| Каскадирование | Работает | Не работает |
| Коллекции сущностей | Управляются | Игнорируются |
| Перехватчики и события | Задействованы | Обходятся |

**Кэширование.** Обычная `Session` автоматически помещает загруженные сущности в кэш первого уровня и возвращает один и тот же экземпляр объекта при повторных обращениях. `StatelessSession` этого не делает: каждый вызов `get()` или `find()` идёт напрямую в базу данных и возвращает новый объект, даже если запись та же самая.

**Dirty Checking.** В стандартной `Session` Hibernate при вызове `flush()` автоматически сравнивает текущее состояние каждой управляемой сущности с её снимком (snapshot), сделанным при загрузке, и генерирует `UPDATE` для изменённых полей. `StatelessSession` этого не делает совсем: если нужно сохранить изменения, нужно явно вызвать `session.update(entity)`.

**Каскадирование.** Базовые операции `StatelessSession` не имеют соответствующих cascade-типов. Если у сущности есть связанные объекты с `cascade = CascadeType.PERSIST`, в обычной `Session` они сохранятся автоматически. В `StatelessSession` каждый связанный объект нужно сохранять явно отдельным вызовом.

**Когда использование оправдано:**
- **Массовые операции (bulk INSERT/UPDATE/DELETE)**: не нужно платить за формирование и поддержку Persistence Context. Начиная с Hibernate 6-7 `StatelessSession` поддерживает `insertMultiple()` и `updateMultiple()` для пакетной отправки запросов одним batch.
- **Потоковая загрузка или выгрузка больших объёмов данных**: ETL-процессы, импорт/экспорт, репликация.
- **Сценарии без каскадных зависимостей**: когда приложение явно управляет жизненным циклом каждого объекта.
- **Высоконагруженные системы с предсказуемым доступом к данным**: где накладные расходы на кэш первого уровня и dirty checking недопустимы.

**Не подходит для:**
- Работы с объектным графом, требующим автоматического каскадирования.
- Сценариев, где нужно «прочитать-изменить-сохранить» без явного вызова `update()`.
- Кода, полагающегося на перехватчики или слушатели событий Hibernate.

Создаётся через `SessionFactory`:
```java
StatelessSession session = sessionFactory.withStatelessOptions()
    .openStatelessSession();
```

Источники: [Hibernate ORM Batch Processing Docs](https://docs.hibernate.org/orm/3.3/reference/en-US/html/batch.html), [Vladmihalcea — Hibernate StatelessSession JDBC Batching](https://vladmihalcea.com/hibernate-statelesssession-jdbc-batching/), [StatelessSession Javadoc (Hibernate ORM 7)](https://docs.hibernate.org/stable/orm/javadocs/org/hibernate/StatelessSession.html)

---

### Вопрос 47. Как стратегия наследования JOINED влияет на производительность полиморфных запросов? Какой SQL генерирует Hibernate при запросе к базовому типу иерархии, и в чём проблема с глубокими иерархиями?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Inheritance — Hibernate ORM 5.2 User Guide](https://docs.hibernate.org/orm/5.2/userguide/html_single/chapters/domain/inheritance.html)

Стратегия «joined table» (или «table-per-subclass») предполагает, что каждый подкласс в иерархии получает собственную таблицу в базе данных. Унаследованное состояние извлекается путём объединения таблицы суперкласса с таблицами подклассов.

Ключевая особенность: дискриминаторный столбец для этой стратегии необязателен. Первичный ключ подкласса одновременно является внешним ключом к таблице суперкласса.

При выполнении полиморфного запроса Hibernate использует множественные `LEFT OUTER JOIN` для соединения таблиц всех подклассов:

```sql
SELECT *
FROM Account jointablet0_
LEFT OUTER JOIN DebitAccount jointablet0_1_
    ON jointablet0_.id = jointablet0_1_.id
LEFT OUTER JOIN CreditAccount jointablet0_2_
    ON jointablet0_.id = jointablet0_2_.id
```

Документация прямо предупреждает: «Полиморфные запросы с joined table inheritance могут использовать несколько JOIN, что может повлиять на производительность при извлечении большого числа сущностей».

#### Ответ от Claude

**Структура таблиц при JOINED.**
При стратегии `JOINED` (`@Inheritance(strategy = InheritanceType.JOINED)`) для каждого класса иерархии создаётся отдельная таблица. Поля базового класса хранятся в базовой таблице, поля каждого подкласса — в собственной таблице подкласса. Первичный ключ подкласса одновременно является внешним ключом (FK), ссылающимся на базовую таблицу.

**SQL при полиморфном запросе.**
Когда приложение запрашивает сущности базового типа (`SELECT e FROM Animal e`), Hibernate не знает заранее, к какому подтипу относится каждая строка. Поэтому генерируется запрос с `LEFT OUTER JOIN` ко всем таблицам подклассов и `CASE`-выражение для определения конкретного типа:

```sql
SELECT
    a.id,
    a.name,
    d.extra_field_dog,
    c.extra_field_cat,
    CASE
        WHEN d.id IS NOT NULL THEN 1
        WHEN c.id IS NOT NULL THEN 2
        WHEN a.id IS NOT NULL THEN 0
    END AS clazz_
FROM Animal a
LEFT OUTER JOIN Dog d ON a.id = d.id
LEFT OUTER JOIN Cat c ON a.id = c.id
```

`clazz_` — псевдодискриминатор, вычисляемый Hibernate на лету; он определяет, в какой Java-класс гидратировать строку.

**Проблема с глубокими иерархиями.**
Количество `LEFT OUTER JOIN` в полиморфном запросе равно **числу подклассов в иерархии**. При глубокой или широкой иерархии это приводит к следующим проблемам:

1. **Рост числа JOIN**: для иерархии с N подклассами Hibernate генерирует N `LEFT OUTER JOIN`. При N = 10–20 и более запрос становится очень дорогим для оптимизатора СУБД.
2. **Неэффективность планировщика запросов**: СУБД вынуждена рассматривать все таблицы подклассов, даже если нужные строки сосредоточены в одном подклассе.
3. **Запросы к конкретному подтипу** (`SELECT e FROM Dog e`) генерируют `INNER JOIN` только между базовой и одной таблицей подкласса — это эффективно. Проблема возникает именно при полиморфных запросах через базовый тип.
4. **Индексирование FK**: каждый `LEFT OUTER JOIN` требует индекса по FK-столбцу в таблице подкласса. Без индексов производительность деградирует на больших наборах данных.

**Сравнение с альтернативными стратегиями:**
- `SINGLE_TABLE`: все данные в одной таблице, полиморфный запрос — `SELECT` без JOIN, максимальная производительность чтения, но нет NOT NULL-ограничений для полей подклассов.
- `TABLE_PER_CLASS`: отдельная полная таблица для каждого конкретного класса, полиморфный запрос — `UNION ALL` по всем таблицам, нет JOIN, но нет общего FK и сложно делать `@ManyToOne` на базовый тип.
- `JOINED`: лучшая нормализация и целостность данных, поддержка NOT NULL-ограничений, но наиболее дорогие полиморфные запросы.

**Рекомендации:**
- Избегать `JOINED` при необходимости частых полиморфных запросов и широких/глубоких иерархиях.
- Если иерархия неглубокая (2–3 уровня) и полиморфные запросы редки, `JOINED` вполне пригоден и обеспечивает хорошую нормализацию.
- Для полиморфных `@ManyToOne`-ассоциаций на базовый тип `JOINED` — приемлемый вариант, поскольку там join идёт к одной строке, а не к целой таблице.

Источники: [Hibernate ORM 5.2 Inheritance User Guide](https://docs.hibernate.org/orm/5.2/userguide/html_single/chapters/domain/inheritance.html), [Vladmihalcea — The best way to use entity inheritance with JPA and Hibernate](https://vladmihalcea.com/the-best-way-to-use-entity-inheritance-with-jpa-and-hibernate/), [Vladmihalcea — The best way to map SINGLE_TABLE inheritance](https://vladmihalcea.com/the-best-way-to-map-the-single_table-inheritance-with-jpa-and-hibernate/)

---

### Вопрос 48. Что такое bytecode enhancement в Hibernate? Как оно изменяет механизм dirty checking по сравнению со стандартным snapshot-сравнением, и как включить эту оптимизацию в проекте?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How to enable bytecode enhancement dirty checking in Hibernate — Vlad Mihalcea](https://vladmihalcea.com/how-to-enable-bytecode-enhancement-dirty-checking-in-hibernate/)

Bytecode enhancement — это механизм инструментирования байт-кода сущностей после их компиляции. При включении dirty tracking Hibernate модифицирует каждый setter-метод, добавляя в него вызов трекера изменений:

```java
// Исходный код
public void setTitle(String title) {
    this.title = title;
}

// После enhancement
public void setTitle(String title) {
    if (!EqualsHelper.areEqual(this.title, title)) {
        this.$$_hibernate_trackChange("title");
    }
    this.title = title;
}
```

Класс начинает отслеживать изменения через встроенный атрибут `$$_hibernate_tracker` типа `DirtyTracker`. При flush-операции Hibernate вызывает:

```java
public boolean $$_hibernate_hasDirtyAttributes() {
    return $$_hibernate_tracker != null && !$$_hibernate_tracker.isEmpty();
}

public String[] $$_hibernate_getDirtyAttributes() {
    if ($$_hibernate_tracker == null) {
        $$_hibernate_tracker = new SimpleFieldTracker();
    }
    return $$_hibernate_tracker.get();
}
```

Это позволяет определить конкретно, какие поля изменились, без обхода всех свойств через Java Reflection.

Включается через Maven-плагин:
```xml
<plugin>
    <groupId>org.hibernate.orm.tooling</groupId>
    <artifactId>hibernate-enhance-maven-plugin</artifactId>
    <version>${hibernate.version}</version>
    <executions>
        <execution>
            <configuration>
                <enableDirtyTracking>true</enableDirtyTracking>
            </configuration>
            <goals>
                <goal>enhance</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

#### Ответ от Claude

**Что такое bytecode enhancement.**
Bytecode enhancement — это процесс модификации скомпилированных `.class`-файлов сущностей (или их инструментирования при загрузке в JVM) для добавления дополнительной функциональности без изменения исходного кода разработчика. Hibernate поддерживает четыре типа enhancement:

1. **In-line Dirty Tracking** — встроенное отслеживание изменённых атрибутов.
2. **Lazy Attribute Loading** — загрузка отдельных полей сущности по требованию (fetch = LAZY на уровне поля).
3. **Bidirectional Association Management** — автоматическая синхронизация обеих сторон двусторонней ассоциации.
4. **Extended Enhancement** — инструментирование пользовательских методов помимо getter/setter.

**Стандартный механизм dirty checking (snapshot-подход).**
В стандартной `Session` при загрузке сущности Hibernate создаёт полную копию (snapshot) всех значений полей и сохраняет её в Persistence Context. При вызове `flush()` Hibernate обходит все управляемые сущности и сравнивает каждое поле текущего состояния со значением в snapshot через Java Reflection:

```
проверок = sum(количество_полей_i) для каждой управляемой сущности i
```

Это означает: даже если не изменилось ни одно поле, Hibernate всё равно обходит все поля всех сущностей. При большом Persistence Context это создаёт существенную нагрузку на CPU и дополнительный расход памяти (двойное хранение состояния).

**Как bytecode enhancement меняет dirty checking.**
С включённым `enableDirtyTracking` каждый setter-метод сущности после компиляции модифицируется так, чтобы при изменении значения сразу же регистрировать имя изменённого поля во встроенном трекере. Сущность реализует интерфейс `SelfDirtinessTracker` и сама знает, какие поля были изменены.

При `flush()` Hibernate вместо полного обхода всех полей просто спрашивает сущность: «Есть ли у тебя грязные атрибуты?» (`$$_hibernate_hasDirtyAttributes()`) и «Какие именно?» (`$$_hibernate_getDirtyAttributes()`). Результат — только изменённые поля попадают в `UPDATE`-запрос, и не требуется полный проход через Reflection.

**Важное замечание:** snapshot всё равно сохраняется в Persistence Context (для rollback и других нужд). Bytecode enhancement устраняет накладные расходы на *проверку* изменений, но не на *хранение* снимка.

**Включение в проекте.**

Maven:
```xml
<plugin>
    <groupId>org.hibernate.orm.tooling</groupId>
    <artifactId>hibernate-enhance-maven-plugin</artifactId>
    <version>${hibernate.version}</version>
    <executions>
        <execution>
            <phase>compile</phase>
            <goals>
                <goal>enhance</goal>
            </goals>
            <configuration>
                <enableLazyInitialization>true</enableLazyInitialization>
                <enableDirtyTracking>true</enableDirtyTracking>
                <enableAssociationManagement>true</enableAssociationManagement>
                <enableExtendedEnhancement>false</enableExtendedEnhancement>
            </configuration>
        </execution>
    </executions>
</plugin>
```

Gradle (Hibernate 6+):
```gradle
plugins {
    id "org.hibernate.orm" version "${hibernateVersion}"
}

hibernate {
    enhancement {
        enableLazyInitialization = true
        enableDirtyTracking = true
        enableAssociationManagement = true
        enableExtendedEnhancement = false
    }
}
```

По умолчанию все параметры установлены в `false`. Enhancement работает на этапе сборки (build-time): плагин обрабатывает `.class`-файлы после их генерации компилятором Java. Существует также вариант runtime enhancement через Java agent, но build-time подход предпочтительнее, так как не добавляет накладных расходов при старте приложения.

**Когда enhancement даёт заметный эффект:**
- Большой Persistence Context (много управляемых сущностей).
- Сущности с большим числом полей.
- Частые flush-операции.
- Если Persistence Context относительно небольшой, прирост производительности будет незначительным.

Источники: [Vladmihalcea — How to enable bytecode enhancement dirty checking in Hibernate](https://vladmihalcea.com/how-to-enable-bytecode-enhancement-dirty-checking-in-hibernate/), [Vladmihalcea — Maven and Gradle Hibernate Enhance Plugin](https://vladmihalcea.com/maven-gradle-hibernate-enhance-plugin/), [Hibernate ORM 6.6 User Guide — Bytecode Enhancement](https://docs.hibernate.org/orm/6.6/userguide/html_single/Hibernate_User_Guide.html#BytecodeEnhancement), [Vladmihalcea — The anatomy of Hibernate dirty checking mechanism](https://vladmihalcea.com/the-anatomy-of-hibernate-dirty-checking/)

---
### Вопрос 49. Что такое @DynamicUpdate и @DynamicInsert в Hibernate? В каких условиях они улучшают производительность, а когда могут её снизить? Как Hibernate без этих аннотаций формирует UPDATE-запрос?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [How to update only a subset of entity attributes using JPA and Hibernate @DynamicUpdate — Vlad Mihalcea](https://vladmihalcea.com/how-to-update-only-a-subset-of-entity-attributes-using-jpa-and-hibernate/)

По умолчанию Hibernate генерирует UPDATE-запросы, включающие **все столбцы** сущности в секцию SET, вне зависимости от того, какие атрибуты фактически изменились. Например, если у сущности `Post` изменилось только поле `score`, Hibernate всё равно формирует запрос вида:

```sql
UPDATE post
SET score = 12,
    title = 'High-Performance Java Persistence'
WHERE id = 1
```

Аннотация `@DynamicUpdate`, размещённая на классе сущности, инструктирует Hibernate генерировать UPDATE-оператор динамически при каждом сбросе контекста персистентности (flush), включая в него только реально изменённые столбцы:

```java
@Entity(name = "Post")
@Table(name = "post")
@DynamicUpdate
public class Post { ... }
```

Результирующий SQL:

```sql
UPDATE post
SET score = 12
WHERE id = 1
```

**Когда помогает:** Если таблица содержит много индексов, исключение неизменившихся столбцов из UPDATE позволяет избежать лишних операций по обновлению индексных структур и снизить нагрузку на БД. Особенно эффективно для сущностей с крупными JSON-полями: без аннотации весь JSON-объект передаётся на сервер при каждом изменении любого другого поля.

**Когда снижает производительность:** При включённом кешировании подготовленных запросов (JDBC prepared statement caching) статический SQL реиспользуется для всех UPDATE-вызовов, а динамический SQL каждый раз уникален по составу столбцов, что снижает эффективность кеша.

#### Ответ от Claude

**Поведение без аннотаций (по умолчанию)**

Hibernate при старте приложения строит для каждой сущности один статический SQL-шаблон UPDATE, перечисляющий все столбцы таблицы. При flush он подставляет текущие значения всех атрибутов, даже тех, что не менялись. Это позволяет переиспользовать один и тот же подготовленный оператор для всех UPDATE по данной сущности.

**@DynamicUpdate**

Аннотируется на уровне класса. Hibernate сравнивает снимок состояния (loaded state) с текущим состоянием сущности и включает в UPDATE только изменившиеся столбцы. SQL формируется в момент flush, а не при запуске приложения.

```java
@Entity
@DynamicUpdate
public class Book {
    private String title;
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> properties;
}
```

Если изменился только `title`, в БД уйдёт:
```sql
UPDATE book SET title = ? WHERE id = ?
```

**Важное ограничение:** при работе с открепёнными (detached) сущностями и вызове `Session.update()` для @DynamicUpdate необходимо также добавить `@SelectBeforeUpdate` — иначе Hibernate не знает, какие поля изменились, и аннотация не даёт эффекта (источник: Hibernate Javadocs 6.6).

**@DynamicInsert**

Аналогична @DynamicUpdate, но для оператора INSERT. Исключает из INSERT-запроса столбцы, значение которых равно null, позволяя БД применить свои DEFAULT-выражения (например, `created_at DEFAULT NOW()`). Без аннотации Hibernate вставляет явный NULL, подавляя дефолт.

**Когда аннотации улучшают производительность:**
- Сущность содержит большие поля (JSON, BLOB/CLOB), которые меняются редко.
- Таблица имеет много индексов: обновление только изменившихся столбцов снижает нагрузку на индексные структуры.
- Используется версионный оптимистичный локинг без поля version (versionless optimistic locking) — динамический UPDATE снижает количество ложных OptimisticLockException при непересекающихся изменениях.

**Когда аннотации снижают производительность (источник: Hibernate Forum / Vlad Mihalcea):**

1. **Кеш подготовленных запросов (JDBC/server-side prepared statement cache):** статический SQL переиспользуется для всех UPDATE одной сущности, а динамический уникален для каждого набора изменённых полей — hit-rate кеша резко падает.
2. **Пакетная обработка (JDBC batch):** при batch-insert/update Hibernate группирует одинаковые SQL-операторы. Если у разных экземпляров сущности меняются разные наборы полей, операторы не совпадают и не объединяются в один пакет.
3. **Сущности с преимущественно ненулевыми полями:** затраты на сравнение снимков состояния и динамическую генерацию SQL не окупаются.

**Итог:** обе аннотации по умолчанию отключены именно потому, что нет универсально лучшего варианта — выбор зависит от профиля нагрузки конкретного приложения.

---

### Вопрос 50. Какие типы проекций поддерживает Spring Data JPA (интерфейс, DTO-класс, динамическая проекция)? Когда интерфейсная проекция порождает дополнительный SELECT вместо ожидаемой оптимизированной выборки, и как это диагностировать?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Projections :: Spring Data JPA — docs.spring.io](https://docs.spring.io/spring-data/jpa/reference/repositories/projections.html)

Spring Data JPA поддерживает три группы проекций.

**1. Интерфейсные проекции**

*Закрытая проекция (Closed Projection)* — все методы интерфейса соответствуют свойствам агрегата. Spring Data знает все нужные атрибуты заранее и может оптимизировать запрос, выбирая только нужные столбцы:

```java
interface NamesOnly {
    String getFirstname();
    String getLastname();
}
```

*Открытая проекция (Open Projection)* — методы помечены `@Value` со SpEL-выражением. Spring Data не может применить оптимизацию, так как выражение потенциально обращается к любому атрибуту агрегата:

```java
interface NamesOnly {
    @Value("#{target.firstname + ' ' + target.lastname}")
    String getFullName();
}
```

В этом случае загружается вся сущность целиком. Альтернатива — default-метод интерфейса, который сохраняет оптимизацию:

```java
interface NamesOnly {
    String getFirstname();
    String getLastname();
    default String getFullName() {
        return getFirstname() + " " + getLastname();
    }
}
```

**2. DTO-проекции (class-based)**

Обычный класс или Java-запись, чьи поля и конструктор определяют перечень выбираемых атрибутов. Spring Data генерирует constructor expression в JPQL. Прокси не создаётся. Вложенные проекции не поддерживаются:

```java
record NamesOnly(String firstname, String lastname) {}
```

**3. Динамические проекции**

Тип проекции определяется в момент вызова через параметр `Class<T>`:

```java
<T> Collection<T> findByLastname(String lastname, Class<T> type);
```

**Когда закрытая проекция загружает лишние данные:** если интерфейс объявляет метод, возвращающий вложенный объект (`getAddress()`), Spring Data вынужден выбрать все атрибуты вложенного объекта целиком, что порождает полный JOIN.

#### Ответ от Claude

**Типы проекций в Spring Data JPA**

| Тип | Оптимизация запроса | Вложенные проекции | Прокси |
|---|---|---|---|
| Закрытая интерфейсная | Да | Да | Да |
| Открытая интерфейсная (@Value SpEL) | Нет | Да | Да |
| DTO / Java Record | Да (через constructor expression) | Нет | Нет |
| Динамическая | Зависит от переданного типа | Да (если интерфейс) | Зависит |

**Закрытая интерфейсная проекция**

Все геттеры интерфейса напрямую соответствуют полям сущности. Spring Data при derived-запросе (без `@Query`) генерирует SELECT только с нужными столбцами. Для каждой строки результата создаётся JDK-прокси, делегирующий вызовы к данным проекции.

**Открытая интерфейсная проекция — когда возникает проблема**

SpEL-выражение в `@Value("#{target.field}")` вычисляется после загрузки объекта `target`. Spring Data не может статически определить, какие поля нужны, поэтому загружает полную сущность (SELECT *). Это нивелирует смысл проекции как оптимизации. Официальная документация прямо указывает: "Spring Data cannot apply query execution optimizations in this case."

Альтернатива без потери оптимизации — default-методы (вычисление на стороне Java после оптимизированной выборки) или делегирование в Spring-бин через `@Value("#{@myBean.method(target)}")`.

**DTO / Java Record проекция**

Spring Data формирует JPQL-запрос с constructor expression:
```jpql
SELECT new com.example.NamesOnly(u.firstname, u.lastname) FROM User u WHERE ...
```
Работает эффективно. При наличии нескольких конструкторов нужный маркируется `@PersistenceCreator`. Вложенные объекты не поддерживаются — при необходимости нужно использовать вручную написанный `@Query`.

**Динамическая проекция**

```java
<T> Collection<T> findByLastname(String lastname, Class<T> type);
```

Оптимизация применяется, если переданный тип является закрытым интерфейсом или DTO; не применяется, если тип — открытая проекция. Важный нюанс из документации: если параметр `Class<T>` совпадает с generic-типом возвращаемого значения, он недоступен для оптимизации запроса — в таком случае следует использовать `Class<?>`.

**Когда интерфейсная проекция порождает дополнительный SELECT**

Два основных сценария:

1. **Открытая проекция со SpEL** — вместо оптимизированного SELECT загружается полная сущность (один запрос, но со всеми столбцами). Строго говоря, это не отдельный SELECT, а отсутствие оптимизации в существующем запросе.

2. **Вложенные свойства (nested properties)** — если метод проекции возвращает связанную сущность (`getAddress()`), Spring Data выбирает весь связанный объект целиком. При LAZY-ассоциациях это может привести к дополнительному SELECT на каждую строку результата (проблема N+1).

**Диагностика**

Включить логирование SQL Hibernate и параметров:
```properties
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.orm.jdbc.bind=TRACE
```

Признаки проблемы в логах:
- `SELECT *` вместо перечисления конкретных столбцов — признак открытой проекции или неоптимизированного derived query.
- Повторяющийся SELECT для одного и того же типа на каждую строку результата — N+1 из-за LAZY вложенного объекта в проекции.
- Количество SQL-запросов в логе значительно превышает количество объектов в результате.

Для production-диагностики удобно использовать библиотеку [datasource-proxy](https://github.com/ttddyy/datasource-proxy) или [P6Spy](https://github.com/p6spy/p6spy), которые позволяют считать количество запросов в тесте и упасть, если оно превышает ожидаемое.

---

### Вопрос 51. Почему класс-сущность (Entity) в JPA/Hibernate, а также его геттеры, не следует объявлять `final`?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Hibernate ORM User Guide — Entity](https://docs.hibernate.org/orm/current/userguide/html_single/Hibernate_User_Guide.html#entity)

Согласно документации Hibernate, для подстановки прокси вместо реального класса класс-сущность должен быть не-`final` (или реализовывать интерфейс со всеми публичными методами). Hibernate во время выполнения генерирует подкласс-прокси для ленивой загрузки; `final`-класс расширить нельзя, поэтому прокси создать не получится, и ленивая загрузка ломается.

#### Ответ от Claude

Hibernate реализует ленивую загрузку (и `getReference()`/`getOne()`) через **прокси — динамически сгенерированный подкласс** сущности (CGLIB/ByteBuddy), который перехватывает обращения к полям и подгружает данные по требованию. Прокси обязан удовлетворять связи IS-A: он либо `extends` класс сущности, либо `implements` интерфейс.

- `final class` **нельзя унаследовать** → прокси не создать → ленивые ассоциации и `getReference()` не работают (приходится грузить eager, больше запросов к БД).
- `final` у геттеров/сеттеров — прокси не сможет их переопределить, перехват не сработает.

Обходные пути: сделать сущность реализующей интерфейс со всеми публичными методами, либо использовать **bytecode enhancement** (статическая инструментация во время сборки) вместо рантайм-прокси. См. [Thorben Janssen — Hibernate Proxies](https://thorben-janssen.com/hibernate-proxies/).

---

### Вопрос 52. Что такое FlushMode в Hibernate? Чем отличается поведение AUTO в нативном Hibernate от поведения AUTO в JPA, и почему нативные SQL-запросы могут возвращать устаревшие данные при Hibernate AUTO?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How do JPA and Hibernate define the AUTO flush mode — Vlad Mihalcea](https://vladmihalcea.com/how-do-jpa-and-hibernate-define-the-auto-flush-mode/)

JPA определяет только два режима сброса: `AUTO` и `COMMIT`. Hibernate расширяет их, добавляя `ALWAYS` и `MANUAL`.

**JPA AUTO**: сессия сбрасывается перед коммитом транзакции, а также перед выполнением **любого** запроса, чтобы гарантировать актуальность данных.

**Hibernate AUTO (нативный режим)**: сессия сбрасывается перед коммитом и, в отличие от JPA, **только перед теми запросами**, которые могут столкнуться с незафиксированными изменениями. Hibernate анализирует, затрагивает ли запрос таблицы с отложенными INSERT/UPDATE/DELETE. Если запрос обращается к другим таблицам — сброс не происходит.

Проблема с нативным SQL: Hibernate не парсит нативные SQL-запросы и не может определить, какие таблицы они используют. Поэтому при использовании нативной `Session` нативные SQL-запросы **не вызывают автоматического сброса** — даже если обращаются к таблицам с отложенными изменениями. При работе через `EntityManager` нативные запросы вызывают сброс, как диктует JPA-спецификация.

**COMMIT**: сессия сбрасывается только при коммите транзакции, никогда — перед запросами.

**ALWAYS** (только нативный Hibernate): сессия сбрасывается перед каждой операцией, включая нативные SQL-запросы.

**MANUAL**: сессия сбрасывается только при явном вызове `Session.flush()`.

#### Ответ от Claude

**Все режимы FlushMode в Hibernate:**

| Режим | Когда сбрасывается | Доступен в |
|-------|-------------------|-----------|
| `AUTO` | Перед коммитом + перед JPQL/HQL-запросами, затрагивающими изменённые таблицы | JPA и Hibernate |
| `COMMIT` | Только перед коммитом | JPA и Hibernate |
| `ALWAYS` | Перед каждым запросом (включая нативный SQL) | Только нативный Hibernate |
| `MANUAL` | Только при явном `flush()` | JPA и Hibernate |

**Ключевое различие: JPA AUTO vs Hibernate AUTO**

JPA-спецификация требует, чтобы в режиме AUTO сессия сбрасывалась перед **любым** запросом — JPQL, Criteria, нативным SQL. Это максимально безопасный подход, гарантирующий отсутствие stale reads.

Нативный Hibernate использует оптимизацию: перед выполнением JPQL/HQL-запроса он анализирует, пересекаются ли таблицы запроса с таблицами отложенных операций. Если нет — сброс пропускается. Это повышает производительность, но создаёт ловушку: нативные SQL-запросы через `Session` не получают автоматического сброса вообще, потому что Hibernate не может проанализировать их SQL-текст.

```java
// Пример потенциально устаревших данных (нативная Session, Hibernate AUTO)
session.persist(new Product("Widget", 100));
// нативный запрос — сброс НЕ происходит в Hibernate AUTO
List<Object[]> result = session.createNativeQuery(
    "SELECT * FROM product WHERE name = 'Widget'").getResultList();
// result может быть пустым — изменения ещё не сброшены!
```

**Решения для нативного SQL:**
1. Явный `session.flush()` перед нативным запросом.
2. Добавление `addSynchronizedEntityClass(Product.class)` — Hibernate принудительно сбросит изменения для указанного класса.
3. Использование `EntityManager` (JPA API) вместо нативной `Session` — тогда нативный SQL тоже вызывает flush.
4. Установка `FlushMode.ALWAYS` для сессии.

**Настройка FlushMode:**
```java
// Spring JPA
entityManager.setFlushMode(FlushModeType.COMMIT);

// Нативный Hibernate
session.setHibernateFlushMode(FlushMode.ALWAYS);

// Для конкретного запроса
session.createQuery("FROM Product p", Product.class)
    .setHibernateFlushMode(FlushMode.COMMIT)
    .getResultList();
```

**Расхождение между источниками:** Vladmihalcea описывает, что начиная с Hibernate 5.2, если приложение загружается через JPA (`persistence.xml` / Spring Boot), то даже нативная `Session` ведёт себя как JPA AUTO и сбрасывает перед нативными запросами. Документация Hibernate 6.x подтверждает это поведение при JPA-буустрэпе. Если приложение использует нативный бутстрэп (`hibernate.cfg.xml`), прежнее поведение Hibernate AUTO сохраняется.

---

### Вопрос 53. Что такое @Embeddable и @Embedded в JPA? Как они маппятся на базу данных, чем отличаются от @Entity, и когда стоит использовать вложенный тип вместо @OneToMany?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Jpa @Embedded and @Embeddable — Baeldung](https://www.baeldung.com/jpa-embedded-embeddable)

`@Embeddable` объявляет класс, поля которого будут встроены в другую сущность. `@Embedded` применяется в сущности для включения `@Embeddable`-класса как поля.

```java
@Embeddable
public class ContactPerson {
    private String firstName;
    private String lastName;
    private String phone;
}

@Entity
public class Company {
    @Id
    @GeneratedValue
    private Integer id;

    @Embedded
    private ContactPerson contactPerson;
}
```

В отличие от `@Entity`, `@Embeddable`-класс не имеет собственной таблицы и не требует первичного ключа. Все его поля хранятся в таблице родительской сущности. Это позволяет избежать лишних таблиц для value-объектов.

Для разрешения конфликтов имён столбцов используется `@AttributeOverrides`:
```java
@Embedded
@AttributeOverrides({
    @AttributeOverride(name = "firstName",
        column = @Column(name = "contact_first_name")),
    @AttributeOverride(name = "lastName",
        column = @Column(name = "contact_last_name"))
})
private ContactPerson contactPerson;
```

Embeddable подходит для value-объектов, принадлежащих только одной родительской сущности. `@OneToMany` используется, когда объектам нужен независимый жизненный цикл.

#### Ответ от Claude

**Что такое Embeddable-тип**

`@Embeddable` — это JPA-механизм для моделирования value objects (объектов-значений) в терминологии Domain-Driven Design. Экземпляр `@Embeddable` не имеет собственной идентичности, не может быть сохранён, обновлён или удалён независимо от родительской сущности. Его поля физически хранятся в таблице родителя.

**Маппинг на базу данных**

```
Класс Company (@Entity) → таблица company
  - id
  - name
  - contactPerson.firstName → колонка firstName (или contact_first_name с @AttributeOverride)
  - contactPerson.lastName  → колонка lastName
  - contactPerson.phone     → колонка phone
```

Таблица `contact_person` **не создаётся**. Все поля встроены напрямую в таблицу `company`.

**Отличия от @Entity**

| Характеристика | @Entity | @Embeddable |
|----------------|---------|-------------|
| Собственная таблица | Да | Нет (поля в таблице родителя) |
| Первичный ключ | Обязателен (@Id) | Отсутствует |
| Независимый жизненный цикл | Да | Нет (только через родителя) |
| Кэш второго уровня | Да | Только через родителя |
| JPQL-запросы к нему | Да | Нет (нельзя запросить напрямую) |
| @OneToMany / @ManyToMany ссылки | Да | Нет |

**@AttributeOverride для переиспользования**

Один и тот же `@Embeddable` тип можно встроить в несколько разных сущностей, переопределяя имена колонок:

```java
@Entity
public class Employee {
    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "home_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "home_city"))
    })
    private Address homeAddress;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "work_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "work_city"))
    })
    private Address workAddress;
}
```

**@Embeddable vs @OneToMany — когда что выбирать**

Использовать `@Embeddable`, если:
- Тип является истинным value object (нет смысла существовать отдельно от родителя).
- Данные всегда запрашиваются вместе с родительской сущностью.
- Нет необходимости в независимом CRUD-цикле (persist/merge/remove отдельно).
- Количество вложенных объектов фиксировано (один на сущность).

Использовать `@OneToMany` с `@Entity`, если:
- Объектам нужен независимый жизненный цикл.
- Необходимо запрашивать дочерние объекты отдельно от родителя.
- Один объект может принадлежать нескольким родителям.
- Нужна пагинация, сортировка или фильтрация по дочерним объектам.
- Количество дочерних объектов заранее не известно (коллекция).

**Важные нюансы:**
- `@Embeddable`-класс должен реализовывать `equals()` и `hashCode()` по значению полей, поскольку JPA сравнивает их по содержимому.
- Нельзя использовать `@Embeddable` в `@ManyToOne` или `@OneToMany` коллекциях непосредственно — для этого используется `@ElementCollection`.

---

### Вопрос 54. Что такое @MappedSuperclass? Чем он отличается от @Inheritance, когда его применять и какую DDL-схему он порождает?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [How to inherit properties from a base class entity using @MappedSuperclass with JPA and Hibernate — Vlad Mihalcea](https://vladmihalcea.com/how-to-inherit-properties-from-a-base-class-entity-using-mappedsuperclass-with-jpa-and-hibernate/)

`@MappedSuperclass` — аннотация JPA, которая позволяет сущностям наследовать свойства базового класса без того, чтобы сам базовый класс становился сущностью. Это означает, что базовый класс не отображается на собственную таблицу, а его поля (включая `@Id` и `@Version`) переносятся непосредственно в таблицы каждого класса-наследника.

Пример: `BaseEntity` с полями `id` и `version` наследуется `Post` и `Tag`. В результате оба класса получают собственные независимые таблицы `post` и `tag`, каждая из которых содержит колонки `id` и `version` — без какой-либо таблицы `base_entity`.

В отличие от `@Inheritance`, `@MappedSuperclass` только моделирует наследование на уровне OOP. Нельзя выполнить полиморфный запрос к базовому классу, нет JOIN-операций при загрузке и нет полиморфных ассоциаций.

#### Ответ от Claude

**Что такое @MappedSuperclass**

`@MappedSuperclass` — это механизм переиспользования маппинга полей, аналог абстрактного Java-класса для ORM. Базовый класс с этой аннотацией:
- **не является сущностью** — не имеет таблицы в БД;
- **не может быть аргументом** `entityManager.find()`, `entityManager.persist()` или JPQL-запроса;
- **не участвует в полиморфных запросах** и не поддерживает полиморфные ассоциации (`@OneToMany` на тип `BaseEntity`);
- **передаёт маппинг** своих полей (@Id, @Version, @Column и т.д.) каждому конкретному классу-наследнику.

```java
@MappedSuperclass
public abstract class BaseEntity {
    @Id
    @GeneratedValue
    private Long id;

    @Version
    private int version;

    @CreationTimestamp
    private LocalDateTime createdAt;
}

@Entity
public class Post extends BaseEntity {
    private String title;
}

@Entity
public class Tag extends BaseEntity {
    private String name;
}
```

**Порождаемая DDL-схема:**

```sql
CREATE TABLE post (
    id BIGINT PRIMARY KEY,
    version INT,
    created_at TIMESTAMP,
    title VARCHAR(255)
);

CREATE TABLE tag (
    id BIGINT PRIMARY KEY,
    version INT,
    created_at TIMESTAMP,
    name VARCHAR(255)
);
```

Таблица `base_entity` отсутствует. Каждая дочерняя сущность получает собственную независимую таблицу со всеми унаследованными колонками.

**Сравнение с @Inheritance**

| Характеристика | @MappedSuperclass | @Inheritance |
|----------------|-------------------|--------------|
| Таблица для базового класса | Нет | Зависит от стратегии |
| Полиморфные запросы | Невозможны | Поддерживаются |
| Полиморфные ассоциации | Невозможны | Поддерживаются |
| Базовый класс как сущность JPA | Нет | Да |
| Цель | Переиспользование маппинга | Моделирование OOP-иерархии в БД |
| JPQL-запрос к базовому типу | Ошибка | Работает (LEFT OUTER JOIN / UNION) |

**Когда применять @MappedSuperclass**

Типичный use case — технические базовые классы:

```java
@MappedSuperclass
public abstract class AuditableEntity {
    @Id @GeneratedValue
    private Long id;

    @Version
    private int version;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

Этот класс наследуют все доменные сущности проекта (`Product`, `Order`, `Customer`), не связанные полиморфным отношением, — каждая получает аудит-поля без дублирования кода. Полиморфный запрос «все AuditableEntity» при этом не нужен и не имеет смысла.

Если же нужна именно полиморфная выборка — следует использовать `@Inheritance` с одной из стратегий (`SINGLE_TABLE`, `JOINED`, `TABLE_PER_CLASS`).

---

### Вопрос 55. Что такое @NaturalId в Hibernate? Как он интегрируется с кэшем первого и второго уровня, какие методы предоставляет для поиска сущностей и почему это лучше, чем findByUsername() через JPQL?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [@NaturalId — A good way to persist natural IDs with Hibernate? — Thorben Janssen](https://thorben-janssen.com/naturalid-good-way-persist-natural-ids-hibernate/)

`@NaturalId` — Hibernate-специфичная аннотация, позволяющая пометить поле как бизнес-ключ сущности. Реальные примеры: ISBN для книги, идентификационный номер налогоплательщика, slug URL записи в блоге.

Hibernate кэширует отображение «natural ID → primary key» на уровне сессии (L1). Это означает, что в рамках одной транзакции повторный поиск по тому же natural ID не выполняет SQL — результат берётся из кэша сессии. При включении L2-кэша через аннотацию `@NaturalIdCache` отображение сохраняется между сессиями, и SQL не выполняется вообще.

Методы поиска:
- `session.bySimpleNaturalId(Entity.class).load(value)` — для одного natural ID поля.
- `session.byNaturalId(Entity.class).using("fieldName", value).load()` — для составного natural ID.
- `loadOptional()` — возвращает `Optional<Entity>`.

Hibernate 5.5+ выполняет один SQL-запрос при поиске по natural ID, более ранние версии — два (сначала PK, потом сущность).

Natural ID по умолчанию иммутабелен. Если значение может изменяться — нужно `@NaturalId(mutable = true)`.

#### Ответ от Claude

**Что такое @NaturalId**

`@NaturalId` — Hibernate-аннотация для обозначения бизнес-ключа сущности — атрибута (или набора атрибутов), который уникально идентифицирует сущность с точки зрения предметной области. Бизнес-ключ используется пользователями и внешними системами, в отличие от суррогатного `@Id` (auto-generated Long), который является техническим деталем.

```java
@Entity
public class User {
    @Id
    @GeneratedValue
    private Long id;

    @NaturalId
    @Column(nullable = false, unique = true)
    private String email;

    // equals и hashCode — по email, а не по id
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User)) return false;
        User other = (User) o;
        return Objects.equals(email, other.email);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(email);
    }
}
```

**Поиск по natural ID**

```java
// Поиск по одному полю
User user = session.bySimpleNaturalId(User.class)
    .load("alice@example.com");

// Составной natural ID
Order order = session.byNaturalId(Order.class)
    .using("orderNumber", "ORD-2024-001")
    .using("region", "EU")
    .load();

// Через Optional
Optional<User> opt = session.bySimpleNaturalId(User.class)
    .loadOptional("alice@example.com");
```

**Интеграция с кэшем первого уровня (L1)**

Hibernate хранит в Persistence Context не только сами сущности по `(тип, id)`, но и карту `natural_id → surrogate_id`. После загрузки сущности по ID она автоматически добавляется в этот маппинг. При последующем вызове `bySimpleNaturalId().load("alice@example.com")` в той же сессии SQL не выполняется — ответ берётся из кэша сессии.

**Интеграция с кэшем второго уровня (L2) — @NaturalIdCache**

```java
@Entity
@Cacheable
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@NaturalIdCache  // кэширует маппинг natural_id → PK в L2
public class User { ... }
```

С `@NaturalIdCache` Hibernate при первой загрузке помещает маппинг в L2-кэш. При следующем запросе из другой сессии SQL-запросы не выполняются совсем — нулевая задержка к БД.

**Почему @NaturalId лучше, чем JPQL findByEmail()**

| Критерий | `bySimpleNaturalId()` | JPQL `findByEmail()` |
|---|---|---|
| Кэш L1 (в сессии) | Используется | Не используется (JPQL всегда идёт в БД) |
| Кэш L2 | Используется с @NaturalIdCache | Используется только с Query Cache |
| Повторный поиск в сессии | Нулевой SQL | SQL выполняется повторно |
| API | Типобезопасный | Строковая JPQL |
| Оптимизация Hibernate 5.5+ | 1 SQL-запрос | 1 SQL-запрос |

Ключевое преимущество: при использовании `@NaturalId` Hibernate отслеживает маппинг `natural_id → PK` и интегрирует его в Persistence Context Identity Map — повторные обращения по бизнес-ключу в рамках одной сессии не нагружают БД.

---

### Вопрос 56. Что такое @ElementCollection в JPA? Чем он отличается от @OneToMany, какую таблицу создаёт Hibernate и когда его использование предпочтительно?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Element collection Vs One to Many in JPA and Hibernate — Medium / CodeX](https://medium.com/codex/element-collection-vs-one-to-many-in-jpa-andhibernate-e4ae83642d99)

Главное различие между `@ElementCollection` и `@OneToMany`:
- `@ElementCollection` предназначен для коллекций **не-сущностей** — базовых типов (`String`, `Integer`) или `@Embeddable`-классов.
- `@OneToMany` предназначен для коллекций **сущностей** (`@Entity`).

Элементы `@ElementCollection` полностью принадлежат содержащей их сущности: они изменяются вместе с ней, удаляются при удалении родителя. У них нет собственного жизненного цикла.

`@ElementCollection` проще в использовании при прототипировании. Однако если впоследствии понадобится запрашивать или редактировать элементы коллекции независимо, `@OneToMany` с полноценными сущностями будет правильным выбором. Embeddable-объекты имеют ряд ограничений: их нельзя запрашивать напрямую, нельзя persist/merge/remove без родителя.

#### Ответ от Claude

**Что такое @ElementCollection**

`@ElementCollection` — JPA-аннотация для маппинга коллекций базовых типов (`String`, `Integer`, перечислений) или `@Embeddable`-классов на отдельную таблицу коллекции, без создания самостоятельных сущностей.

```java
@Entity
public class Employee {
    @Id @GeneratedValue
    private Long id;

    private String name;

    @ElementCollection
    @CollectionTable(
        name = "employee_phone",
        joinColumns = @JoinColumn(name = "employee_id"))
    @Column(name = "phone_number")
    private List<String> phoneNumbers;

    @ElementCollection
    @CollectionTable(name = "employee_address")
    private List<Address> addresses;  // Address — @Embeddable
}
```

**DDL-схема, создаваемая Hibernate:**

```sql
CREATE TABLE employee (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE employee_phone (
    employee_id BIGINT NOT NULL,       -- FK на employee.id
    phone_number VARCHAR(255),
    FOREIGN KEY (employee_id) REFERENCES employee(id)
);

CREATE TABLE employee_address (
    employee_id BIGINT NOT NULL,
    street VARCHAR(255),
    city VARCHAR(255),
    ...
);
```

Таблица коллекции не имеет собственного первичного ключа (по умолчанию). При любом изменении коллекции Hibernate удаляет все строки для данного `employee_id` и вставляет заново — это важный недостаток при больших коллекциях.

**Сравнение @ElementCollection и @OneToMany:**

| Характеристика | @ElementCollection | @OneToMany |
|---|---|---|
| Тип элементов | Базовые типы / @Embeddable | @Entity |
| Собственный @Id у элементов | Нет | Да |
| Независимый жизненный цикл | Нет | Да |
| Каскадирование | Всегда (неявное) | Настраивается через CascadeType |
| JPQL-запросы к элементам | Нет | Да |
| Изменение одного элемента | Hibernate удаляет и перевставляет всю коллекцию | Обновляет только изменённую строку |
| Использование | Простые value-листы | Сложные объекты с ID и бизнес-логикой |

**Когда @ElementCollection предпочтительнее:**
- Список телефонов, тегов, псевдонимов — простые строковые значения без самостоятельного смысла.
- Адреса, периоды времени (`@Embeddable`) без потребности в независимом управлении.
- Быстрое прототипирование без необходимости CRUD-интерфейса к элементам.

**Когда нужен @OneToMany:**
- Элементы имеют бизнес-идентичность и могут существовать независимо.
- Необходим JPQL-поиск по элементам коллекции (`WHERE c.email = :email`).
- Нужно обновлять отдельные элементы без перезаписи всей коллекции.
- Элементы реферируются из других сущностей.

---

### Вопрос 57. Как реализовать мягкое удаление (soft delete) в Hibernate с помощью @SQLDelete и @Where? Что происходит при вызове entityManager.find() без дополнительной настройки, и почему @Filter является более гибким решением?

**Категория:** JPA/Hibernate · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [The best way to soft delete with Hibernate — Vlad Mihalcea](https://vladmihalcea.com/the-best-way-to-soft-delete-with-hibernate/)

Мягкое удаление (soft delete) — паттерн, при котором вместо физического `DELETE` запись помечается как удалённая флагом `deleted = true`. Hibernate поддерживает это через аннотации:

- **`@SQLDelete`** — переопределяет SQL, выполняемый при `entityManager.remove()`. Вместо `DELETE` выполняется `UPDATE`:
```java
@SQLDelete(sql = "UPDATE tag SET deleted = true WHERE id = ?")
```
- **`@Where`** — добавляет условие `WHERE deleted = false` ко всем JPQL-запросам и загрузке коллекций. Но `entityManager.find()` по умолчанию может возвращать удалённые сущности, если `@Where` не применяется к прямым выборкам по ID.

В Hibernate 5.2+ для корректной фильтрации при `find()` требуется добавить `@Loader` с `@NamedQuery`:
```java
@Loader(namedQuery = "findTagById")
@NamedQuery(name = "findTagById",
    query = "SELECT t FROM Tag t WHERE t.id = ?1 AND t.deleted = false")
```

`@Filter` / `@FilterDef` является более гибким решением: фильтр может быть включён или отключён на уровне сессии, что позволяет, например, администраторам видеть удалённые записи.

#### Ответ от Claude

**Базовая реализация с @SQLDelete и @Where**

```java
@Entity
@SQLDelete(sql = "UPDATE article SET deleted = true WHERE id = ?")
@Where(clause = "deleted = false")
public class Article {
    @Id @GeneratedValue
    private Long id;

    private String title;

    private boolean deleted = false;
}
```

При вызове `entityManager.remove(article)` Hibernate выполняет:
```sql
UPDATE article SET deleted = true WHERE id = ?
```
вместо `DELETE FROM article WHERE id = ?`.

Все JPQL-запросы (`FROM Article`, `WHERE article.status = :s`) автоматически получают дополнительное условие `AND deleted = false`.

**Проблема с entityManager.find()**

`@Where` применяется к JPQL-запросам и загрузке коллекций, но `entityManager.find(Article.class, id)` использует прямой `SELECT` по первичному ключу — `@Where` к нему **не применяется**. Это означает, что мягко удалённая запись будет возвращена через `find()`.

**Решение для Hibernate 5.x — @Loader:**
```java
@Loader(namedQuery = "findArticleById")
@NamedQuery(
    name = "findArticleById",
    query = "SELECT a FROM Article a WHERE a.id = ?1 AND a.deleted = false")
```

**Hibernate 6.x** вводит аннотацию `@SoftDelete` (Hibernate 6.4+), которая решает проблему комплексно:
```java
@Entity
@SoftDelete  // Hibernate 6.4+
public class Article { ... }
```

**Почему @Filter гибче, чем @Where**

`@Where` — статический фильтр, всегда активный. `@Filter` + `@FilterDef` — динамический фильтр, управляемый на уровне сессии:

```java
@FilterDef(name = "deletedFilter",
    parameters = @ParamDef(name = "deleted", type = Boolean.class))
@Filter(name = "deletedFilter", condition = "deleted = :deleted")
@Entity
public class Article { ... }
```

Применение фильтра:
```java
// Включить фильтр (обычный пользователь видит только неудалённые)
session.enableFilter("deletedFilter").setParameter("deleted", false);

// Не включать (администратор видит все записи)
// session.enableFilter("deletedFilter") не вызывается
```

| Характеристика | @Where | @Filter |
|---|---|---|
| Активация | Всегда | Явная на уровне сессии |
| Отключение | Невозможно | `session.disableFilter(name)` |
| Применение к find() | Нет (нужен @Loader) | Нет |
| Параметры | Нет | Да (параметризуемые условия) |
| Применение к коллекциям | Да | Да (через @Filter на поле) |

**Ограничения soft delete в ассоциациях:**
- `@ManyToOne` на мягко удалённую сущность — `@Where` не применяется к прямой загрузке по FK.
- При `@ManyToMany` через bridge-таблицу — мягко удалённые сущности могут попасть в коллекцию.
- Рекомендуется тщательно тестировать поведение ассоциаций при soft delete.

---

### Вопрос 58. Что такое JPA AttributeConverter? Как его реализовать и зарегистрировать, для каких типов атрибутов он применяется, и чем отличается от Hibernate UserType?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [JPA AttributeConverter — A Beginner's Guide — Vlad Mihalcea](https://vladmihalcea.com/jpa-attributeconverter/)

`AttributeConverter` — интерфейс JPA 2.1, позволяющий преобразовывать значение атрибута сущности в тип данных JDBC-столбца и обратно. Интерфейс содержит два метода:

- `convertToDatabaseColumn(X attribute)` — вызывается при INSERT/UPDATE, преобразует Java-тип в тип БД.
- `convertToEntityAttribute(Y dbData)` — вызывается при SELECT, преобразует тип БД в Java-тип.

Пример — маппинг `java.time.MonthDay` на `java.sql.Date`:
```java
@Converter(autoApply = true)
public class MonthDayDateAttributeConverter
    implements AttributeConverter<MonthDay, java.sql.Date> {

    @Override
    public java.sql.Date convertToDatabaseColumn(MonthDay attribute) {
        return attribute == null ? null :
            java.sql.Date.valueOf(attribute.atYear(1970));
    }

    @Override
    public MonthDay convertToEntityAttribute(java.sql.Date dbData) {
        return dbData == null ? null :
            MonthDay.from(dbData.toLocalDate());
    }
}
```

С `autoApply = true` конвертер применяется ко всем атрибутам соответствующего типа автоматически. Без него — через `@Convert(converter = MonthDayDateAttributeConverter.class)` на конкретном поле. Нельзя применять к `@Id`, `@Version`, полям с `@Temporal` или `@Enumerated`.

#### Ответ от Claude

**Что такое AttributeConverter**

`AttributeConverter<X, Y>` — стандартный JPA-интерфейс (появился в JPA 2.1) для преобразования между Java-типом атрибута сущности (X) и типом JDBC-столбца (Y). Механизм прозрачен для кода сущности: разработчик работает с Java-типом, Hibernate автоматически вызывает конвертер при записи и чтении.

**Реализация**

```java
// Маппинг Money (пользовательский тип) -> BigDecimal (в БД)
@Converter(autoApply = true)
public class MoneyConverter implements AttributeConverter<Money, BigDecimal> {

    @Override
    public BigDecimal convertToDatabaseColumn(Money money) {
        return money == null ? null : money.getAmount();
    }

    @Override
    public Money convertToEntityAttribute(BigDecimal amount) {
        return amount == null ? null : Money.of(amount, Currency.getInstance("USD"));
    }
}
```

**Регистрация конвертера**

Способ 1 — `@Convert` на атрибуте:
```java
@Entity
public class Product {
    @Convert(converter = MoneyConverter.class)
    private Money price;
}
```

Способ 2 — `@Converter(autoApply = true)`: конвертер автоматически применяется ко всем атрибутам типа `Money` во всём приложении без аннотации `@Convert` на полях.

Способ 3 — отключение: `@Convert(disableConversion = true)` на конкретном поле.

**Ограничения: где нельзя использовать**

Согласно JPA-спецификации (JSR-338), `AttributeConverter` **не применяется** к:
- Атрибутам, помеченным `@Id` или являющимся частью `@EmbeddedId`.
- Атрибутам `@Version`.
- Атрибутам с аннотацией `@Temporal` (используйте `LocalDate`/`LocalDateTime` вместо `java.util.Date` — Hibernate 5+ поддерживает их нативно).
- Атрибутам с `@Enumerated` — используйте конвертер вместо `@Enumerated` для маппинга enum на произвольную строку/код.
- Коллекциям (`@ElementCollection`, `@OneToMany`).
- Нативным SQL-запросам (конвертер не применяется к результатам `createNativeQuery()`).

**Сравнение с Hibernate UserType**

| Критерий | AttributeConverter | Hibernate UserType |
|---|---|---|
| Стандарт | JPA 2.1 (переносимо) | Hibernate-специфично |
| Уровень доступа | Значение атрибута | JDBC PreparedStatement / ResultSet |
| Поддержка многоколоночных типов | Нет (один столбец) | Да |
| Поддержка null | Ручная обработка в методах | Через интерфейс |
| Применение к коллекциям | Нет | Да |
| Простота реализации | Высокая | Низкая (интерфейс сложнее) |

`AttributeConverter` покрывает большинство случаев (пользовательские типы-обёртки, enum в произвольный код, JSON-поля). `UserType` нужен, когда требуется контроль на уровне JDBC или маппинг на несколько колонок.

---

### Вопрос 59. Что такое @Formula в Hibernate? Как аннотация влияет на генерируемый SQL, каковы её ограничения и чем она отличается от @ColumnTransformer?

**Категория:** JPA/Hibernate · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [How to map calculated properties with JPA and Hibernate @Formula annotation — Vlad Mihalcea](https://vladmihalcea.com/how-to-map-calculated-properties-with-jpa-and-hibernate-formula-annotation/)

`@Formula` — аннотация Hibernate, которая позволяет объявить атрибут сущности как производное (вычисляемое) значение, определяемое нативным SQL-выражением. Hibernate не хранит это значение в отдельном столбце, а включает SQL-фрагмент непосредственно в SELECT-запрос.

Пример: поле `dollars` вычисляется из столбца `cents`:

```java
@Formula("cents::numeric / 100")
private double dollars;
```

Сложный пример с функцией:

```java
@Formula("""
    round((interestRate::numeric / 100) * cents *
    date_part('month', age(now(), createdOn)) / 12)
    """)
private long interestCents;
```

Hibernate генерирует SELECT, включающий SQL-выражение как псевдоколонку:

```sql
SELECT a.id, a.cents, a.interestRate,
    a.cents::numeric / 100 AS formula0_0_,
    round(...) AS formula1_0_
FROM account a WHERE a.id = 1
```

#### Ответ от Claude

**Что такое @Formula**

`@Formula` — Hibernate-специфичная аннотация (`org.hibernate.annotations.Formula`), которая задаёт производный атрибут сущности. Значение атрибута вычисляется нативным SQL-выражением при каждой загрузке сущности из базы данных. Столбец с таким значением в таблице отсутствует.

```java
@Entity
public class Author {
    @Id
    private Long id;

    @Column
    private LocalDate dateOfBirth;

    @Formula("date_part('year', age(dateOfBirth))")
    private int age;
}
```

**Как @Formula влияет на генерируемый SQL**

Hibernate встраивает SQL-фрагмент формулы прямо в SELECT-запрос как подвыражение (inline expression). Каждый SELECT для данной сущности содержит этот фрагмент, вне зависимости от того, нужно ли поле текущему коду. Поле является read-only: при INSERT и UPDATE Hibernate полностью игнорирует атрибут с `@Formula` — никакого `SET formula_field = ?` не генерируется.

Пример генерируемого SQL для сущности с несколькими формулами:

```sql
SELECT
    a.id,
    a.cents,
    a.interest_rate,
    a.cents::numeric / 100          AS col_0_0_,
    round((a.interest_rate / 100.0) * a.cents * ...) AS col_1_0_
FROM account a
WHERE a.id = ?
```

**Ключевые ограничения**

1. **Только нативный SQL**: формула — это фрагмент SQL конкретного диалекта (`PostgreSQL`, `MySQL`, `Oracle`). Переносимость между СУБД нарушается. JPQL или HQL внутри `@Formula` не поддерживаются.

2. **Read-only**: атрибут невозможно установить напрямую и сохранить в БД. Попытка сделать `author.setAge(30)` допустима в Java, но при flush Hibernate проигнорирует это значение.

3. **Загружается всегда (нет lazy на уровне формулы)**: SQL-фрагмент включается в каждый SELECT для данной сущности. Нельзя настроить lazy-загрузку для `@Formula`-поля средствами стандартной конфигурации — только через bytecode enhancement с `@Basic(fetch = LAZY)`, и только если провайдер поддерживает ленивую загрузку скалярных атрибутов.

4. **Кэш второго уровня**: значение формулы кэшируется в L2 вместе с остальными атрибутами сущности. Если зависимые данные (например, в другой таблице или функция от системного времени) изменяются независимо, кэш может содержать устаревшее значение до его инвалидации.

5. **Ограниченный scope таблиц**: формула может ссылаться на столбцы основной таблицы сущности или одной вторичной таблицы (`@SecondaryTable`), но не может произвольно JOIN-ить другие таблицы без явного указания этого в SQL-подзапросе.

6. **Не является стандартом JPA**: `@Formula` входит в Hibernate ORM API, а не в Jakarta Persistence. При смене провайдера на EclipseLink аннотация перестанет работать.

**Сравнение с @ColumnTransformer**

| Аспект | @Formula | @ColumnTransformer |
|---|---|---|
| Операции | Только чтение (SELECT) | Чтение и запись (SELECT + INSERT/UPDATE) |
| Назначение | Производный (вычисляемый) атрибут | Трансформация при записи/чтении (шифрование, единицы измерения) |
| Пример | `"cents / 100.0"` | `read = "decrypt(secret)"`, `write = "encrypt(?)"` |
| Собственный столбец в БД | Нет | Да (реальный столбец с трансформацией) |

Если нужно и читать, и записывать атрибут с преобразованием — `@ColumnTransformer`. Если нужно только отобразить результат вычисления — `@Formula`.

**Когда использовать @Formula**

- Вычисление значений из нескольких столбцов сущности (сумма, процент, конкатенация).
- Агрегация из связанной таблицы через подзапрос: `"(SELECT COUNT(*) FROM orders WHERE orders.customer_id = id)"`.
- Конвертация единиц или форматирование при чтении (если запись не требуется).
- Денормализованные поля ради производительности, когда пересчёт на уровне БД предпочтительнее логики в `@PostLoad`.

---

### Вопрос 60. Что такое @NamedQuery в JPA/Hibernate? В чём преимущества перед createQuery() и когда предпочтительнее использовать программные запросы?

**Категория:** JPA/Hibernate · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Chapter 13. HQL and JPQL — Hibernate ORM 5.0 User Guide](https://docs.jboss.org/hibernate/orm/5.0/userguide/en-US/html/ch13.html)

`@NamedQuery` — статический JPQL-запрос, определённый на уровне класса сущности. Hibernate компилирует и валидирует именованные запросы при старте приложения, а не в момент выполнения. Это означает, что ошибки в JPQL (опечатки, несуществующие поля) обнаруживаются при запуске, а не в рантайме под нагрузкой. Для нативного SQL используется `@NamedNativeQuery`.

Особенности:
- Именованные запросы хранятся в метаданных Hibernate и могут переиспользоваться из нескольких мест по имени.
- Параметры задаются только именованными (`:param`) — не позиционными (для JPQL).
- Тип возвращаемого значения задаётся через `resultClass` или `resultSetMapping`.

Именованные запросы не поддерживают динамическое построение условий — для динамических WHERE-клауз используется Criteria API.

#### Ответ от Claude

**Что такое @NamedQuery**

`@NamedQuery` — аннотация для объявления статического, заранее определённого JPQL-запроса на уровне класса сущности:

```java
@Entity
@NamedQuery(
    name = "Product.findByCategory",
    query = "SELECT p FROM Product p WHERE p.category = :category AND p.active = true"
)
public class Product {
    @Id @GeneratedValue
    private Long id;
    private String category;
    private boolean active;
}
```

Несколько именованных запросов:
```java
@NamedQueries({
    @NamedQuery(name = "Product.findByCategory",
        query = "SELECT p FROM Product p WHERE p.category = :category"),
    @NamedQuery(name = "Product.findAllActive",
        query = "SELECT p FROM Product p WHERE p.active = true")
})
```

Использование:
```java
List<Product> products = entityManager
    .createNamedQuery("Product.findByCategory", Product.class)
    .setParameter("category", "Electronics")
    .getResultList();
```

**Преимущества @NamedQuery перед createQuery()**

1. **Валидация при старте**: Hibernate компилирует и проверяет JPQL в момент инициализации `EntityManagerFactory`. Ошибки (`typo` в имени поля, несуществующая сущность) выявляются при деплое, а не под нагрузкой.

2. **Кэширование плана запроса**: Hibernate кэширует скомпилированный план выполнения (query plan) именованного запроса. Для `createQuery()` план строится при каждом вызове (хотя Hibernate 5+ также кэширует планы для повторяющихся JPQL-строк через `QueryPlanCache`).

3. **Централизация**: запрос определён один раз рядом с сущностью и переиспользуется из разных частей приложения. Нет дублирования JPQL-строк в коде.

4. **Читаемость**: код вызова чище — вместо длинной JPQL-строки — мнемоническое имя.

**Ограничения @NamedQuery:**
- Запрос статический: нельзя динамически добавлять условия `WHERE`, сортировку или JOIN.
- Немного затрудняет навигацию: запрос объявлен на сущности, а вызывается из совершенно другого места.
- В Spring Data JPA репозитории именованные запросы автоматически находятся по соглашению `EntityName.methodName` — это удобная интеграция.

**Когда что использовать:**

| Сценарий | Рекомендация |
|---|---|
| Фиксированный запрос, используется многократно | `@NamedQuery` |
| Простой запрос в Spring Data JPA | Derived query (`findByCategory`) |
| Статический запрос с аннотацией | `@Query` в репозитории (менее verbose) |
| Динамические условия WHERE | Criteria API или Specification (Spring Data) |
| Сложный запрос один раз | `createQuery()` в репозитории |

В современном Spring Data JPA именованные запросы частично вытеснены аннотацией `@Query` на методах репозитория — она также проверяется при старте (начиная со Spring Data JPA 2.4+) и удобнее с точки зрения локализации запроса рядом с его использованием.

---
