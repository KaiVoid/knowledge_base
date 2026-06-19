# Реляционные базы данных и SQL

> **Уровень:** Junior / Middle / Senior
> **Связанные вопросы:** [Вопросы по БД и SQL →](../../../interview-questions/databases-sql-01.md)
> **Связанные области:** [[16-jpa-hibernate]], [[17-rest-web]]

## Что это и зачем

Подавляющее большинство backend-приложений работают с реляционными СУБД. Java-разработчик должен
уверенно писать SQL, понимать нормализацию, индексы, транзакции и их уровни изоляции, а также работать
с БД из Java через JDBC. Это фундамент, поверх которого работают JPA/Hibernate.

Реляционная модель хранит данные в таблицах (отношениях), связанных ключами. SQL — декларативный язык
запросов: программист описывает *что* нужно получить, а СУБД выбирает *как* это сделать (план выполнения).
Понимание того, как оптимизатор строит план, позволяет писать запросы, которые эффективно работают при
больших объёмах данных.

---

## Ключевые подтемы

### Порядок выполнения SELECT

Понимание логического порядка обработки предотвращает ошибки с алиасами и фильтрацией.
Согласно [документации PostgreSQL по SELECT](https://www.postgresql.org/docs/current/sql-select.html),
логическая последовательность такова:

1. `WITH` — вычисляются CTE
2. `FROM` + `JOIN` — формируется декартово произведение, затем применяются условия соединения
3. `WHERE` — фильтрация строк *до* группировки
4. `GROUP BY` — строки объединяются в группы
5. `HAVING` — фильтрация групп *после* группировки
6. `SELECT` — вычисляются выражения в списке столбцов
7. `DISTINCT` — удаление дублей
8. Операции над множествами: `UNION`, `INTERSECT`, `EXCEPT`
9. `ORDER BY` — сортировка
10. `LIMIT` / `OFFSET` — ограничение результата

Практический вывод: псевдоним из `SELECT` нельзя использовать в `WHERE` (они вычисляются позже),
но можно — в `ORDER BY`.

---

### Типы JOIN

```sql
-- Только совпадающие строки из обеих таблиц
SELECT * FROM orders o INNER JOIN customers c ON o.customer_id = c.id;

-- Все строки левой таблицы + совпадающие из правой (NULL, если нет совпадения)
SELECT * FROM customers c LEFT JOIN orders o ON c.id = o.customer_id;

-- Все строки правой таблицы + совпадающие из левой
SELECT * FROM orders o RIGHT JOIN customers c ON o.customer_id = c.id;

-- Все строки обеих таблиц; несовпадающие дополняются NULL
SELECT * FROM customers c FULL OUTER JOIN orders o ON c.id = o.customer_id;

-- Декартово произведение (каждая строка первой × каждая строка второй)
SELECT * FROM colors CROSS JOIN sizes;
```

`NATURAL JOIN` автоматически соединяет по столбцам с одинаковыми именами — использовать с осторожностью,
поскольку добавление нового столбца с совпадающим именем изменяет семантику запроса.

---

### GROUP BY, HAVING и агрегатные функции

`WHERE` фильтрует строки *до* группировки; `HAVING` — *после*. Это принципиально:

```sql
-- Правильно: фильтр по итогу группы — в HAVING
SELECT department, COUNT(*) AS cnt
FROM employees
WHERE hire_date > '2020-01-01'   -- отбрасываем строки до группировки
GROUP BY department
HAVING COUNT(*) > 5;             -- оставляем только группы с нужным итогом
```

Стандартные агрегатные функции: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

PostgreSQL поддерживает расширения `GROUP BY`:

| Расширение | Что генерирует |
|---|---|
| `ROLLUP(a, b)` | Подытоги для (a, b), (a) и () |
| `CUBE(a, b)` | Все комбинации: (a, b), (a), (b), () |
| `GROUPING SETS(...)` | Произвольный набор группировок |

---

### Оконные функции

Оконные функции вычисляются после `WHERE`, `GROUP BY`, `HAVING` и позволяют получить
агрегат без схлопывания строк в группы. Подробнее в
[PostgreSQL Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html).

```sql
SELECT
    employee_id,
    department,
    salary,
    RANK()        OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
    SUM(salary)   OVER (PARTITION BY department)                      AS dept_total,
    LAG(salary)   OVER (ORDER BY hire_date)                          AS prev_salary
FROM employees;
```

Основные функции: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()`, `LEAD()`,
`FIRST_VALUE()`, `LAST_VALUE()`, `SUM/AVG/COUNT OVER (...)`.

---

### CTE (Common Table Expressions)

```sql
-- Обычный CTE: улучшает читаемость, может быть материализован
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT * FROM ranked WHERE rn = 1;  -- топ-1 по зарплате в каждом отделе

-- Рекурсивный CTE: обход иерархий
WITH RECURSIVE org AS (
    SELECT id, name, manager_id FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id
    FROM employees e
    JOIN org ON e.manager_id = org.id
)
SELECT * FROM org;
```

Ключевые модификаторы PostgreSQL: `MATERIALIZED` (запрещает инлайнинг, гарантирует
однократное выполнение), `NOT MATERIALIZED` (разрешает оптимизатору встроить CTE в план).

---

### Нормализация и нормальные формы

Нормализация устраняет избыточность и аномалии обновления/вставки/удаления.

| Форма | Требование |
|---|---|
| 1NF | Атомарные значения, нет повторяющихся групп, есть первичный ключ |
| 2NF | 1NF + нет частичных зависимостей от составного ключа |
| 3NF | 2NF + нет транзитивных зависимостей от не-ключевых атрибутов |
| BCNF | Усиленная 3NF: каждый детерминант является ключом-кандидатом |

На практике большинство схем нормализуют до 3NF; денормализацию применяют осознанно
для оптимизации чтения.

---

### Ограничения (Constraints)

Документация: [PostgreSQL DDL Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html).

```sql
CREATE TABLE order_items (
    id          BIGSERIAL PRIMARY KEY,               -- NOT NULL + UNIQUE
    order_id    INTEGER NOT NULL
                REFERENCES orders(id) ON DELETE CASCADE,
    product_id  INTEGER NOT NULL
                REFERENCES products(id) ON DELETE RESTRICT,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    price       NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    UNIQUE (order_id, product_id)
);
```

Поведение внешнего ключа при удалении родительской записи (`ON DELETE`):

| Действие | Поведение |
|---|---|
| `NO ACTION` (умолчание) | Ошибка в конце транзакции, если есть ссылающиеся строки |
| `RESTRICT` | Немедленная ошибка; нельзя отложить до конца транзакции |
| `CASCADE` | Удаляет зависимые строки |
| `SET NULL` | Устанавливает столбец FK в NULL |
| `SET DEFAULT` | Устанавливает столбец FK в значение по умолчанию |

Те же опции доступны для `ON UPDATE`. `CHECK`-ограничение считается выполненным,
если выражение даёт `TRUE` или `NULL` — т.е. оно не запрещает `NULL` само по себе.

---

### Индексы

#### Типы индексов PostgreSQL

Документация: [PostgreSQL Index Types](https://www.postgresql.org/docs/current/indexes-types.html).

| Тип | Когда использовать | Поддерживаемые операторы |
|---|---|---|
| **B-tree** (умолчание) | Равенство, диапазоны, сортировка | `<`, `<=`, `=`, `>=`, `>`, `BETWEEN`, `IN`, `LIKE 'foo%'` |
| **Hash** | Только равенство | `=` |
| **GIN** | Массивы, JSONB, полнотекстовый поиск | `@>`, `<@`, `&&`, `@@` |
| **GiST** | Геометрические типы, ближайший сосед | `<<`, `>>`, `&&`, `<->` |
| **SP-GiST** | kd-деревья, квадродеревья, радиксные деревья | `<<`, `>>`, `~=`, `<@` |
| **BRIN** | Большие таблицы с физически упорядоченными данными (timestamp, serial) | `<`, `<=`, `=`, `>=`, `>` |

#### Специальные виды индексов

```sql
-- Частичный (partial) индекс — индексирует только подмножество строк
CREATE INDEX idx_active_users ON users (email) WHERE is_active = true;

-- Индекс по выражению — ускоряет запросы с функциями
CREATE INDEX idx_lower_email ON users ((lower(email)));

-- Составной (multicolumn) индекс — порядок столбцов важен
CREATE INDEX idx_dept_salary ON employees (department_id, salary DESC);

-- Покрывающий (covering) индекс с INCLUDE — index-only scan без обращения к таблице
CREATE UNIQUE INDEX idx_title ON films (title) INCLUDE (director, rating);

-- Создание индекса без блокировки записи
CREATE INDEX CONCURRENTLY idx_orders_created ON orders (created_at);
```

`CONCURRENTLY` требует двух проходов по таблице и не работает внутри явной транзакции,
но не блокирует `INSERT`/`UPDATE`/`DELETE` во время построения.

#### Цена индексов

Каждый индекс увеличивает стоимость операций `INSERT`, `UPDATE`, `DELETE`
(необходимо обновлять структуру индекса). Узкоспециальные частичные индексы и
индексы типа BRIN минимизируют накладные расходы. Правило: не создавайте индексы
«на всякий случай» — добавляйте их под конкретные запросы с доказанной выгодой.

---

### Транзакции и ACID

**ACID** — набор свойств, гарантирующих надёжность транзакций:

| Свойство | Значение |
|---|---|
| **Atomicity** (Атомарность) | Транзакция выполняется целиком или не выполняется вовсе |
| **Consistency** (Согласованность) | Транзакция переводит БД из одного корректного состояния в другое |
| **Isolation** (Изолированность) | Одновременные транзакции не видят незафиксированных изменений друг друга (в зависимости от уровня) |
| **Durability** (Долговечность) | Зафиксированные данные сохраняются даже после сбоя |

---

### Уровни изоляции транзакций

Документация: [PostgreSQL Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html).

PostgreSQL реализует четыре уровня изоляции SQL-стандарта, но благодаря MVCC
(Multiversion Concurrency Control) фактически обеспечивает более строгие гарантии,
чем требует стандарт.

#### Аномалии чтения

| Аномалия | Описание |
|---|---|
| **Dirty read** | Транзакция читает незафиксированные изменения другой транзакции |
| **Non-repeatable read** | Повторное чтение той же строки в рамках одной транзакции возвращает другое значение |
| **Phantom read** | Повторный запрос возвращает другой набор строк (появились/исчезли строки) |
| **Serialization anomaly** | Группа транзакций приводит к результату, невозможному при любом последовательном порядке их выполнения |

#### Таблица уровней изоляции в PostgreSQL

| Уровень | Dirty read | Non-repeatable read | Phantom read | Serialization anomaly |
|---|---|---|---|---|
| Read Uncommitted | Невозможен* | Возможен | Возможен | Возможен |
| **Read Committed** (умолчание) | Невозможен | Возможен | Возможен | Возможен |
| Repeatable Read | Невозможен | Невозможен | Невозможен* | Возможен |
| Serializable | Невозможен | Невозможен | Невозможен | Невозможен |

*PostgreSQL Read Uncommitted ведёт себя как Read Committed из-за MVCC.
*PostgreSQL Repeatable Read дополнительно запрещает фантомные чтения, хотя стандарт это не требует.

```sql
-- Установить уровень для текущей транзакции
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- ... запросы ...
COMMIT;

-- Или сразу при открытии
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

**Read Committed** (умолчание): каждый оператор видит снимок данных на момент *начала этого оператора*.
Подходит для большинства случаев, но внутри одной транзакции разные операторы могут видеть разные данные.

**Repeatable Read**: все операторы транзакции видят один снимок, зафиксированный на момент
первого не-управляющего оператора. При конфликте транзакция получает ошибку сериализации и
должна быть перезапущена приложением.

**Serializable**: использует SSI (Serializable Snapshot Isolation) с предикатными блокировками.
Гарантирует результат, идентичный последовательному выполнению транзакций. Требует обработки
`ERROR: could not serialize access` с повторными попытками.

---

### JDBC: работа с базой данных из Java

Документация: [The Java Tutorials — JDBC Basics](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html).

#### Connection и DataSource

```java
// DriverManager — простой способ, подходит для скриптов/тестов
// JDBC 4.0+: драйвер загружается автоматически через ServiceLoader
Connection conn = DriverManager.getConnection(
    "jdbc:postgresql://localhost:5432/mydb",
    "user", "password"
);

// DataSource — рекомендуемый способ в продакшене (поддерживает пул соединений)
// Обычно настраивается через контейнер (Spring, Jakarta EE) или вручную:
HikariDataSource ds = new HikariDataSource();
ds.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
ds.setUsername("user");
ds.setPassword("password");
Connection conn = ds.getConnection();
```

#### Statement vs PreparedStatement

`PreparedStatement` — предпочтительный вариант:
- SQL компилируется **один раз** при создании, далее только исполняется повторно
- Параметры всегда трактуются как данные, а не как SQL-код — **предотвращает SQL-инъекции**
- Более чистый код при работе с параметрами

```java
// Statement (только для запросов без параметров)
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM products");

// PreparedStatement (с параметрами — всегда)
String sql = "UPDATE products SET price = ? WHERE id = ?";
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.setBigDecimal(1, newPrice);  // параметр 1
    ps.setLong(2, productId);       // параметр 2
    int affected = ps.executeUpdate();
}
```

Методы выполнения:
- `executeQuery()` — для `SELECT`, возвращает `ResultSet`
- `executeUpdate()` — для `INSERT`/`UPDATE`/`DELETE`, возвращает количество строк
- `execute()` — универсальный, когда тип результата неизвестен

#### Транзакции в JDBC

По умолчанию соединение находится в режиме **auto-commit**: каждый оператор автоматически фиксируется.
Для группировки операторов в транзакцию нужно отключить auto-commit.

```java
conn.setAutoCommit(false);
try {
    // Несколько операторов — атомарный блок
    ps1.executeUpdate();
    ps2.executeUpdate();
    conn.commit();
} catch (SQLException e) {
    conn.rollback();  // Отменить все изменения транзакции
    throw e;
} finally {
    conn.setAutoCommit(true);
}
```

Savepoints позволяют выполнять частичный откат:

```java
Savepoint sp = conn.setSavepoint();
try {
    ps3.executeUpdate();
} catch (SQLException e) {
    conn.rollback(sp);  // откат только до savepoint, не всей транзакции
}
```

Установка уровня изоляции из JDBC:

```java
conn.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
```

Константы `Connection.TRANSACTION_*` соответствуют четырём стандартным уровням.
Поддержку конкретного уровня можно проверить через `DatabaseMetaData.supportsTransactionIsolationLevel()`.

#### Пулы соединений

Создание нового соединения к PostgreSQL — дорогостоящая операция (аутентификация, выделение
backend-процесса). Пул соединений переиспользует уже открытые соединения.

Популярные реализации:
- **HikariCP** — самый быстрый пул, рекомендован в Spring Boot по умолчанию
- **Apache DBCP2** — зрелое решение из экосистемы Apache Commons
- **c3p0** — старый, но всё ещё встречается в legacy-проектах

Ключевые параметры пула: `maximumPoolSize`, `minimumIdle`, `connectionTimeout`, `idleTimeout`,
`maxLifetime`.

---

### Оптимизация запросов и EXPLAIN

Документация: [Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).

`EXPLAIN` показывает план выполнения без запуска запроса; `EXPLAIN ANALYZE` выполняет
запрос и сравнивает оценки с реальными значениями.

```sql
EXPLAIN ANALYZE
SELECT o.id, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.created_at > '2024-01-01';
```

Пример вывода и его интерпретация:

```
Nested Loop  (cost=4.65..118.50 rows=10 width=488)
             (actual time=0.017..0.051 rows=10 loops=1)
  ->  Bitmap Heap Scan on orders o  (cost=4.36..39.38 rows=10 width=244)
        Recheck Cond: (created_at > '2024-01-01')
        ->  Bitmap Index Scan on idx_orders_created  (actual time=0.009..0.009 rows=40 loops=1)
  ->  Index Scan using customers_pkey on customers c  (cost=0.29..7.90 rows=1 width=244)
        Index Cond: (id = o.customer_id)
Planning Time: 0.5 ms
Execution Time: 1.2 ms
```

Поля в скобках:
- `cost=start..total` — стоимость в условных единицах (seq_page_cost = 1.0 по умолчанию)
- `rows` — ожидаемое число строк на выходе узла
- `width` — средний размер строки в байтах
- `actual time=start..end` — реальное время в мс; `loops` — число повторных выполнений

Основные узлы плана:

| Узел | Значение |
|---|---|
| `Seq Scan` | Полное последовательное сканирование таблицы |
| `Index Scan` | Чтение через индекс в порядке индекса |
| `Index Only Scan` | Данные берутся прямо из индекса (без обращения к таблице) |
| `Bitmap Index Scan` + `Bitmap Heap Scan` | Сначала строится битовая карта позиций, затем читается таблица |
| `Nested Loop` | Для каждой строки внешней стороны сканируется внутренняя |
| `Hash Join` | Строит хэш-таблицу из меньшего набора, затем зондирует её |
| `Merge Join` | Соединяет два отсортированных потока |

Признак плохого плана: большое расхождение между `rows` (оценка) и `actual rows` (факт).
Причины: устаревшая статистика — исправляется `ANALYZE tablename`; некорректные
оценки кардинальности после нескольких JOIN.

---

## Достоверные источники

1. **[PostgreSQL Documentation — SQL Commands](https://www.postgresql.org/docs/current/sql-commands.html)** —
   полный справочник по синтаксису SQL в PostgreSQL; официальная документация проекта,
   поддерживается командой разработчиков PostgreSQL.

2. **[PostgreSQL Documentation — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)** —
   исчерпывающее описание уровней изоляции, MVCC и аномалий чтения с примерами; официальный источник.

3. **[PostgreSQL Documentation — Index Types](https://www.postgresql.org/docs/current/indexes-types.html)** —
   описание B-tree, Hash, GIN, GiST, SP-GiST, BRIN с примерами создания и областями применения; официальный источник.

4. **[PostgreSQL Documentation — Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)** —
   объяснение всех полей вывода EXPLAIN/EXPLAIN ANALYZE, интерпретация планов; официальный источник.

5. **[The Java Tutorials — JDBC Basics](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html)** —
   официальный учебник Oracle по JDBC: Connection, PreparedStatement, транзакции, пулы соединений.

6. **[Use The Index, Luke!](https://use-the-index-luke.com/)** —
   авторитетный независимый ресурс Маркуса Винанда по индексам и производительности SQL,
   охватывает PostgreSQL, Oracle, MySQL; рекомендован разработчиками СУБД.
