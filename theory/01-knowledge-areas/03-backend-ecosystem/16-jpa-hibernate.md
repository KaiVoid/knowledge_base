# JPA и Hibernate

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по JPA/Hibernate →](../../../interview-questions/jpa-hibernate-01.md)
> **Связанные области:** [[15-databases-sql]], [[13-spring-core]]

## Что это и зачем

JPA (Jakarta Persistence API) — стандарт ORM в Java, Hibernate — его самая популярная реализация.
ORM отображает объекты на таблицы БД и избавляет от рутинного JDBC-кода. Тема критична для backend:
нужно понимать жизненный цикл сущностей, отношения, ленивую загрузку, кэширование и типичные
проблемы (N+1, `LazyInitializationException`).

JPA — это спецификация (интерфейсы + аннотации), Hibernate — реализация. Начиная с Jakarta EE 9
пакеты переименованы с `javax.persistence.*` в `jakarta.persistence.*`. Актуальная версия
спецификации — Jakarta Persistence 3.2 (требует Java SE 17+), актуальная версия Hibernate ORM — 6.6.x.

## Ключевые подтемы

### Требования к классу-сущности и базовый маппинг

Класс должен быть аннотирован `@Entity` и иметь публичный или protected конструктор без аргументов.
Класс, его методы и поля нельзя объявлять `final`. Если объекты передаются как detached через слой
представления — рекомендуется реализовать `Serializable`.

Ключевые аннотации маппинга:

| Аннотация | Назначение |
|---|---|
| `@Entity` | Помечает класс как управляемую сущность |
| `@Table(name="...")` | Задаёт имя таблицы (по умолчанию — имя класса) |
| `@Id` | Помечает поле первичным ключом |
| `@GeneratedValue` | Стратегия генерации PK (AUTO, IDENTITY, SEQUENCE, TABLE, UUID) |
| `@Column(name="...", nullable=false, length=255)` | Маппинг на конкретный столбец |
| `@Basic(fetch=FetchType.LAZY)` | Ленивая загрузка скалярного поля (требует bytecode enhancement) |
| `@Transient` | Поле исключено из маппинга |
| `@Enumerated(EnumType.STRING)` | Хранить enum как строку (рекомендуется) |
| `@Temporal(TemporalType.TIMESTAMP)` | Для устаревших `java.util.Date`; для `java.time.*` аннотация не нужна |
| `@Lob` | Маппинг BLOB/CLOB |

Стратегии генерации идентификатора (`@GeneratedValue(strategy = ...)`):

- `GenerationType.IDENTITY` — автоинкремент БД (MySQL, PostgreSQL SERIAL); Hibernate не может
  использовать batch insert с этой стратегией.
- `GenerationType.SEQUENCE` — последовательность БД (PostgreSQL, Oracle); поддерживает batch
  вставку; рекомендуется `@SequenceGenerator(allocationSize=50)` для снижения числа обращений к БД.
- `GenerationType.TABLE` — эмуляция через отдельную таблицу; медленно, избегать в новых проектах.
- `GenerationType.AUTO` — Hibernate выбирает стратегию сам (в Hibernate 6 по умолчанию — SEQUENCE).
- `GenerationType.UUID` — генерация UUID (доступно с JPA 3.1).

```java
@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE,
                    generator = "order_seq")
    @SequenceGenerator(name = "order_seq",
                       sequenceName = "order_seq",
                       allocationSize = 50)
    private Long id;

    @Column(name = "total_amount", nullable = false)
    private BigDecimal totalAmount;

    @Enumerated(EnumType.STRING)
    @Column(length = 20)
    private OrderStatus status;
}
```

---

### Жизненный цикл сущности и EntityManager

Сущность в течение своей жизни проходит через четыре состояния (определены спецификацией):

```
Transient ──persist()──> Managed ──remove()──> Removed
                 ^             |
              merge()       detach() / close session
                 |             v
             Detached <──── Detached
```

| Состояние | Описание |
|---|---|
| **Transient** | Объект создан (`new`), не связан ни с каким `EntityManager`, нет записи в БД |
| **Managed** | Связан с активным контекстом персистентности; изменения отслеживаются автоматически |
| **Detached** | Был управляемым, контекст закрыт или `detach()` вызван; изменения не отслеживаются |
| **Removed** | Помечен для удаления вызовом `remove()`; DELETE выполнится при flush |

Основные операции `EntityManager` / `Session`:

- `persist(entity)` — переводит transient -> managed; вставка произойдёт при flush.
- `merge(entity)` — копирует состояние detached-объекта в новый (или уже существующий) managed-объект; возвращает managed-копию.
- `remove(entity)` — помечает managed-сущность на удаление.
- `detach(entity)` — исключает сущность из контекста персистентности.
- `refresh(entity)` — перечитывает состояние из БД, отменяя in-memory изменения.
- `find(Class, id)` — поиск по первичному ключу; вначале проверяет кэш первого уровня.
- `getReference(Class, id)` — возвращает lazy-прокси без немедленного SELECT; выбрасывает исключение при обращении, если записи нет.
- `flush()` — немедленно синхронизирует контекст с БД (не коммит!).

**Flush modes** (`FlushModeType`):
- `AUTO` (по умолчанию) — flush перед выполнением запросов и при коммите транзакции.
- `COMMIT` — flush только при коммите.
- `ALWAYS` (Hibernate-специфично) — flush перед каждым запросом.
- `MANUAL` (Hibernate-специфично) — flush только при явном вызове `session.flush()`.

---

### Dirty Checking (обнаружение изменений)

Hibernate автоматически обнаруживает изменения managed-сущностей без явных вызовов `update()`.
Механизм работы:

1. При загрузке сущности Hibernate сохраняет снимок (snapshot) исходного состояния полей в first-level cache.
2. Перед flush'ом сравнивается текущее состояние каждого поля со снимком.
3. Если обнаружено отличие — генерируется UPDATE только для изменившихся столбцов.

В Hibernate 6+ доступен **инлайн dirty tracking** через bytecode enhancement: вместо сравнения
снимков изменения регистрируются непосредственно при присваивании полей, что снижает нагрузку
на GC и ускоряет flush для большого числа сущностей.

---

### Отношения между сущностями

JPA поддерживает четыре вида отношений; каждое может быть однонаправленным или двунаправленным.

#### @ManyToOne / @OneToMany

Самое распространённое отношение. Владелец — сторона с `@ManyToOne` и `@JoinColumn`.

```java
@Entity
public class Order {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;
}

@Entity
public class Customer {
    @OneToMany(mappedBy = "customer",
               cascade = CascadeType.ALL,
               orphanRemoval = true)
    private List<Order> orders = new ArrayList<>();
}
```

`mappedBy` на стороне `@OneToMany` означает «эта сторона не владеет join-столбцом».

#### @OneToOne

Может быть общим PK (`@MapsId`) или отдельным FK. Рекомендуется `fetch = FetchType.LAZY` —
по умолчанию `EAGER`, что часто нежелательно.

#### @ManyToMany

Требует промежуточной таблицы (`@JoinTable`). Владелец — сторона с `@JoinTable`.

```java
@Entity
public class Student {
    @ManyToMany
    @JoinTable(
        name = "student_course",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>();
}

@Entity
public class Course {
    @ManyToMany(mappedBy = "courses")
    private Set<Student> students = new HashSet<>();
}
```

#### Cascade типы

| `CascadeType` | Поведение |
|---|---|
| `PERSIST` | persist() распространяется на связанные сущности |
| `MERGE` | merge() распространяется на связанные сущности |
| `REMOVE` | remove() удаляет связанные сущности |
| `DETACH` | detach() распространяется на связанные сущности |
| `REFRESH` | refresh() распространяется на связанные сущности |
| `ALL` | Все перечисленные выше |

`orphanRemoval = true` — удаляет дочернюю сущность, если она исключена из коллекции родителя
(аналогично `CascadeType.REMOVE` для отдельных элементов, но автоматически).

---

### Ленивая и жадная загрузка. Проблема N+1

**FetchType.EAGER** — связанные данные загружаются сразу вместе с сущностью. По умолчанию для
`@ManyToOne` и `@OneToOne`.

**FetchType.LAZY** — связанные данные загружаются при первом обращении к полю (через proxy/байткод).
По умолчанию для `@OneToMany` и `@ManyToMany`. Настоятельно рекомендуется для `@ManyToOne` тоже.

**LazyInitializationException** возникает при обращении к lazy-ассоциации вне открытой сессии
(например, после закрытия `EntityManager` или в сериализаторе).

#### Проблема N+1

```java
// N+1: для каждого заказа выполняется отдельный SELECT customer
List<Order> orders = em.createQuery("from Order", Order.class).getResultList();
for (Order o : orders) {
    System.out.println(o.getCustomer().getName()); // N дополнительных SELECT
}
```

**Решения:**

1. **JOIN FETCH** в JPQL — самый прямолинейный способ, загружает ассоциацию одним JOIN:

```java
List<Order> orders = em.createQuery(
    "select o from Order o join fetch o.customer", Order.class)
    .getResultList();
```

> Внимание: JOIN FETCH нельзя сочетать с `setMaxResults` / `setFirstResult` при загрузке
> коллекций — Hibernate делает пагинацию в памяти с предупреждением в логе.

2. **@EntityGraph** — задаёт граф загрузки без изменения JPQL; работает корректно с пагинацией
   для `@ManyToOne` / `@OneToOne`:

```java
@EntityGraph(attributePaths = {"customer"})
List<Order> findAll(Pageable pageable);
```

3. **@BatchSize** — загружает N связанных сущностей одним SELECT IN (...):

```java
@Entity
public class Customer {
    @OneToMany(mappedBy = "customer")
    @BatchSize(size = 25)
    private List<Order> orders;
}
```

4. **Fetch Profile** (Hibernate) — именованные профили загрузки, переключаемые в runtime.

---

### JPQL и HQL

HQL (Hibernate Query Language) — расширенное надмножество JPQL (Jakarta Persistence Query Language).
Оба языка работают с сущностями и их полями, а не с таблицами и столбцами.

Официальная документация: [Hibernate 6 Query Language Guide](https://docs.hibernate.org/orm/6.2/querylanguage/html_single/).

Синтаксис запроса:

```java
// Именованные параметры (рекомендуется; НИКОГДА не конкатенировать user input!)
List<Order> result = em.createQuery(
    "select o from Order o where o.status = :status and o.totalAmount > :min",
    Order.class)
    .setParameter("status", OrderStatus.ACTIVE)
    .setParameter("min", BigDecimal.valueOf(100))
    .getResultList();
```

**Ключевые возможности:**
- JOIN / LEFT JOIN / JOIN FETCH / implicit join через навигацию (`o.customer.name`)
- Агрегаты: `count`, `sum`, `avg`, `min`, `max` + GROUP BY / HAVING
- Подзапросы в WHERE и FROM (derived root — Hibernate 6+)
- UPDATE / DELETE (bulk operations — обходят dirty checking, кэш 1-го уровня не обновляется)
- Пагинация: `setFirstResult(offset).setMaxResults(limit)`; в HQL6 также `LIMIT x OFFSET y`
- `@NamedQuery` — запрос проверяется при старте `SessionFactory`, а не при первом вызове

```java
// Bulk update — осторожно: кэш 1-го уровня устаревает
int updated = em.createQuery(
    "update Order o set o.status = :newStatus where o.status = :old")
    .setParameter("newStatus", OrderStatus.CLOSED)
    .setParameter("old", OrderStatus.ACTIVE)
    .executeUpdate();
```

---

### Criteria API

Типобезопасный способ строить запросы программно. Полезен при динамическом построении запроса
(когда условия фильтрации неизвестны на этапе компиляции).

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Order> cq = cb.createQuery(Order.class);
Root<Order> root = cq.from(Order.class);

Predicate statusPred = cb.equal(root.get("status"), OrderStatus.ACTIVE);
Predicate amountPred = cb.gt(root.get("totalAmount"), 100);

cq.select(root)
  .where(cb.and(statusPred, amountPred))
  .orderBy(cb.desc(root.get("totalAmount")));

List<Order> orders = em.createQuery(cq).getResultList();
```

В JPA 3.2 добавлены `CriteriaSelect`, расширенные entity-join и `subquery(EntityType)`.

---

### Кэш первого и второго уровня

#### Кэш первого уровня (First-Level Cache)

Встроен в каждый `Session` / `EntityManager`, включён всегда, отключить нельзя.
В рамках одной сессии повторный `find(Order.class, 1L)` не делает SELECT — возвращается
объект из кэша. Гарантирует repeatable-read семантику внутри транзакции.

Очищается методом `session.evict(entity)` или `session.clear()`.

#### Кэш второго уровня (Second-Level Cache)

Разделяется между сессиями (JVM-уровень или кластер). По умолчанию **выключен**; требует
явной настройки и аннотирования сущностей.

Настройка в `persistence.xml`:
```xml
<property name="hibernate.cache.use_second_level_cache" value="true"/>
<property name="hibernate.cache.region.factory_class"
          value="org.hibernate.cache.jcache.JCacheRegionFactory"/>
```

Аннотирование сущности:
```java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product { ... }
```

**Стратегии конкурентного доступа:**

| Стратегия | Описание | Когда |
|---|---|---|
| `READ_ONLY` | Нет блокировок; данные не меняются | Справочники, конфиги |
| `NONSTRICT_READ_WRITE` | Редкие обновления; небольшой риск stale data | Редко изменяемые данные |
| `READ_WRITE` | Мягкие блокировки; консистентность гарантирована | Часто обновляемые данные |
| `TRANSACTIONAL` | Полная XA-транзакционность; только для JTA | Строгие требования к консистентности |

#### Кэш запросов (Query Cache)

Кэширует результирующие наборы HQL/JPQL-запросов. Хранит только идентификаторы сущностей
(сами сущности — в кэше 2-го уровня). Инвалидируется при любом изменении таблицы.

```xml
<property name="hibernate.cache.use_query_cache" value="true"/>
```

```java
List<Product> products = em.createQuery("from Product where active = true", Product.class)
    .setHint(QueryHints.HINT_CACHEABLE, true)
    .getResultList();
```

**Поставщики кэша 2-го уровня:** Ehcache (через JCache), Infinispan (для кластеров),
Caffeine (локально).

---

### Блокировки: оптимистичная и пессимистичная

#### Оптимистичная блокировка

Предполагает отсутствие конфликтов; проверка выполняется при commit. Реализуется через
поле версии:

```java
@Entity
public class Product {
    @Version
    private int version; // или Long, Instant, LocalDateTime
}
```

При каждом UPDATE Hibernate добавляет `WHERE version = :expected` и инкрементирует version.
Если строк обновлено 0 — выбрасывается `OptimisticLockException`.

Hibernate также поддерживает `@OptimisticLocking(type = OptimisticLockType.DIRTY)` или `ALL` —
вместо версионного поля сравниваются конкретные столбцы.

#### Пессимистичная блокировка

Блокирует строку на уровне БД через `SELECT ... FOR UPDATE / FOR SHARE`:

```java
Order order = em.find(Order.class, 1L, LockModeType.PESSIMISTIC_WRITE);
// SELECT ... FOR UPDATE

// Или при запросе:
em.createQuery("from Order o where o.id = :id", Order.class)
  .setParameter("id", 1L)
  .setLockMode(LockModeType.PESSIMISTIC_WRITE)
  .getSingleResult();
```

| `LockModeType` (JPA) | Hibernate `LockMode` | SQL |
|---|---|---|
| `OPTIMISTIC` | `OPTIMISTIC` | Версионная проверка при commit |
| `OPTIMISTIC_FORCE_INCREMENT` | `OPTIMISTIC_FORCE_INCREMENT` | Принудительный инкремент version |
| `PESSIMISTIC_READ` | `PESSIMISTIC_READ` | SELECT FOR SHARE |
| `PESSIMISTIC_WRITE` | `PESSIMISTIC_WRITE` | SELECT FOR UPDATE |
| `PESSIMISTIC_FORCE_INCREMENT` | `PESSIMISTIC_FORCE_INCREMENT` | SELECT FOR UPDATE + version++ |

Hibernate 6 дополнительно предоставляет `UPGRADE_NOWAIT` и `UPGRADE_SKIP_LOCKED` (не стандарт JPA)
для `SELECT FOR UPDATE NOWAIT / SKIP LOCKED`.

---

### Наследование сущностей

JPA определяет три стратегии наследования (`@Inheritance(strategy = ...)`):

| Стратегия | Описание | Плюсы / минусы |
|---|---|---|
| `SINGLE_TABLE` | Все подклассы — в одной таблице; дискриминатор определяет тип | Быстрые запросы, NULL-столбцы для необязательных полей |
| `JOINED` | Каждый класс — своя таблица; JOIN при выборке | Нормализация, но JOIN на каждый SELECT |
| `TABLE_PER_CLASS` | Каждый конкретный класс — своя таблица с дублированием общих полей | Нет JOIN, но UNION при полиморфных запросах; нельзя использовать SEQUENCE |

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "dtype", discriminatorType = DiscriminatorType.STRING)
public abstract class Payment { ... }

@Entity
@DiscriminatorValue("CARD")
public class CardPayment extends Payment { ... }
```

`@MappedSuperclass` — общий суперкласс, не являющийся сущностью; его таблицы нет, поля
наследуются конкретными `@Entity`.

---

### Embeddable-типы

`@Embeddable` — класс-значение без собственной идентичности; его поля хранятся в таблице владельца.

```java
@Embeddable
public class Address {
    private String street;
    private String city;
    private String zipCode;
}

@Entity
public class Customer {
    @Embedded
    @AttributeOverride(name = "zipCode", column = @Column(name = "postal_code"))
    private Address address;
}
```

Hibernate 6.6 добавил поддержку наследования `@Embeddable`-типов через дискриминатор.
Jakarta Persistence 3.2 разрешает использовать `record` как `@Embeddable`.

---

### Конфигурация persistence unit

`persistence.xml` располагается в `META-INF/`:

```xml
<persistence xmlns="https://jakarta.ee/xml/ns/persistence" version="3.0">
  <persistence-unit name="myPU" transaction-type="RESOURCE_LOCAL">
    <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>
    <properties>
      <property name="jakarta.persistence.jdbc.url"
                value="jdbc:postgresql://localhost/mydb"/>
      <property name="jakarta.persistence.jdbc.user" value="user"/>
      <property name="jakarta.persistence.jdbc.password" value="secret"/>
      <property name="hibernate.dialect"
                value="org.hibernate.dialect.PostgreSQLDialect"/>
      <property name="hibernate.hbm2ddl.auto" value="validate"/>
      <property name="hibernate.show_sql" value="true"/>
      <property name="hibernate.format_sql" value="true"/>
    </properties>
  </persistence-unit>
</persistence>
```

`transaction-type="JTA"` — для управляемых (JavaEE/Jakarta EE) контейнеров;
`RESOURCE_LOCAL` — для standalone / Spring (`EntityManagerFactory` / `EntityManager` создаются приложением).

---

## Достоверные источники

1. **[Jakarta Persistence 3.2 — Specification](https://jakarta.ee/specifications/persistence/3.2/)**
   Официальная спецификация Jakarta EE. Эталонный источник: определяет API, аннотации, поведение,
   жизненный цикл сущностей, JPQL и Criteria API.

2. **[Hibernate ORM 6.6 User Guide](https://docs.hibernate.org/orm/6.6/userguide/html_single/Hibernate_User_Guide.html)**
   Официальная документация реализации. Содержит полное описание маппинга, lifecycle,
   кэширования, fetching, локировки, нативных SQL, схему генерации DDL.

3. **[Hibernate Query Language Guide (6.2)](https://docs.hibernate.org/orm/6.2/querylanguage/html_single/)**
   Отдельный официальный гид по HQL/JPQL: полный синтаксис SELECT/UPDATE/DELETE, JOIN FETCH,
   подзапросы, типы параметров, функции. Актуален для Hibernate 6+.

4. **[Jakarta EE Tutorial — Introduction to Jakarta Persistence](https://jakarta.ee/learn/docs/jakartaee-tutorial/current/persist/persistence-intro/persistence-intro.html)**
   Официальный обучающий материал Jakarta EE: сущности, persistence unit, EntityManager,
   управление транзакциями, container-managed vs application-managed.

5. **[Baeldung — JPA & Hibernate Learning Guide](https://www.baeldung.com/learn-jpa-hibernate)**
   Авторитетный технический ресурс: обширная серия практических статей с примерами кода
   по всем основным темам (N+1, кэш, наследование, блокировки и др.).

6. **[Vlad Mihalcea — High-Performance Java Persistence](https://vladmihalcea.com/tutorials/hibernate/)**
   Блог ведущего Hibernate-контрибьютора; глубокий разбор проблем производительности,
   dirty checking, N+1, блокировок. Факты привязаны к конкретным версиям и тестам.
