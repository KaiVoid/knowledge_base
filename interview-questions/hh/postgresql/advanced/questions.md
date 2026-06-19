# PostgreSQL — Advanced (HH)

### Вопрос 1. В базе есть enum-тип `permission` (`read`/`write`/`execute`) и таблица `role` с колонкой `permissions permission[]`. Какое выражение на месте `[…]` в `INSERT` создаст запись с массивом разрешений, содержащим `read`?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
create type permission as enum ('read', 'write', 'execute');
create table role (
    -- …
    permissions permission[]
    -- …
);
insert into role(/* … */) values (/* …, [ … ], … */);
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** `array['read']::permission[]`

#### Ответ от Claude

Колонка `permissions` имеет тип «массив enum» (`permission[]`). Чтобы вставить в неё
массив с одним элементом, нужен конструктор массива с приведением к типу элемента:
`ARRAY['read']::permission[]`. Конструктор `ARRAY[...]` строит массив, а приведение
`::permission[]` гарантирует, что элементы интерпретируются как значения enum
`permission`, а не как `text`. Эквивалентен строковый литерал `'{read}'::permission[]`,
но в квизе верный вариант — именно конструктор `ARRAY[...]` с приведением.

Источники: PostgreSQL — [Arrays, §8.15](https://www.postgresql.org/docs/current/arrays.html)
и [Enumerated Types, §8.7](https://www.postgresql.org/docs/current/datatype-enum.html).

---

### Вопрос 2. Какое утверждение относительно генерируемых колонок является ложью?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Генерируемые колонки могут ссылаться на другие генерируемые колонки

#### Ответ от Claude

Это утверждение является ложью: генерируемые колонки в PostgreSQL **не могут** ссылаться на другие генерируемые колонки. Согласно официальной документации (§5.4 «Generated Columns»), выражение генерации может обращаться к другим столбцам таблицы, но не к другим генерируемым столбцам. Это сделано, чтобы исключить циклические зависимости и гарантировать детерминированное вычисление значений.

Прочие реальные ограничения генерируемых колонок:
- выражение должно использовать только иммутабельные (immutable) функции;
- нельзя использовать подзапросы и обращения к другим строкам;
- нельзя одновременно задавать явное значение DEFAULT;
- не могут быть частью ключа секционирования.

Источник: [PostgreSQL §5.4 Generated Columns](https://www.postgresql.org/docs/current/ddl-generated-columns.html).

---

### Вопрос 3. Имеется таблица `role` с колонкой `permissions permission[]`. Во все существующие записи нужно добавить пермиссию `'read'`, не создавая дубликатов. Как этого достичь?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE TYPE permission AS ENUM ('read','write','execute','transfer','download');
CREATE TABLE role (
    -- …
    permissions permission[],
    -- …
);
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:**
```sql
UPDATE role
SET permissions = array_append(permissions, 'read')
WHERE array_position(permissions, 'read') IS NULL;
```

#### Ответ от Claude

Решение использует две встроенные функции для работы с массивами:

- `array_append(anyarray, anyelement)` — возвращает новый массив с добавленным в конец элементом; документация: [§9.19 Array Functions](https://www.postgresql.org/docs/current/functions-array.html).
- `array_position(anyarray, anyelement)` — возвращает индекс первого вхождения элемента (NULL, если элемент не найден); также §9.19.

Условие `WHERE array_position(permissions, 'read') IS NULL` гарантирует, что мы обновляем только строки, в которых `'read'` ещё отсутствует — таким образом дубликаты исключаются.

Замечание по источнику: в оригинальном тексте источника в условии `WHERE` написано `array_position(permission, 'read')` (без `s`), что является опечаткой — верное имя колонки `permissions`.

---

### Вопрос 4. Вы создаёте временную таблицу `temp_data`, объединяя результаты двух запросов с несовместимыми типами данных (integer и text). Требования: автоматически принимать структуру первого запроса и сохранять дублирующиеся строки. Какой подход использовать?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE TEMPORARY TABLE temp_data AS
<оператор> SELECT id, data FROM source1
<оператор> SELECT id, info FROM source2;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Использовать `UNION ALL`, чтобы сохранить дубликаты и автоматически привести типы данных

#### Ответ от Claude

`UNION ALL` — правильный выбор по двум причинам:

1. **Сохранение дубликатов.** `UNION` убирает дубликаты (как `DISTINCT`), тогда как `UNION ALL` возвращает все строки обоих запросов без дедупликации.
2. **Автоматическое приведение типов.** PostgreSQL применяет правила приведения типов для операндов `UNION`/`UNION ALL`: если столбцы имеют разные типы, система пытается найти общий тип-«резолюцию». Тип итогового столбца определяется по правилам из §10.5 документации.

Важная оговорка: PostgreSQL **не всегда** может привести `integer` и `text` автоматически — эти типы не имеют неявного преобразования из одного в другой. На практике такой `UNION ALL` выдаст ошибку типов, и потребуется явное приведение (`CAST`). Вопрос HH подразумевает учебный сценарий, где типы совместимы или приводятся неявно.

Источники: [PostgreSQL §7.4 Combining Queries](https://www.postgresql.org/docs/current/queries-union.html); [§10.5 Type Resolution for UNION](https://www.postgresql.org/docs/current/typeconv-union-case.html).

---

### Вопрос 5. Есть две связанные таблицы: `t2` использует значение из последовательности по умолчанию при обновлении ссылочной записи (`ON DELETE SET DEFAULT`). Какие проблемы могут возникнуть при удалении записей из `t1`?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE SEQUENCE seq START WITH 1 INCREMENT BY 1;
CREATE TABLE t1 (
    id SERIAL PRIMARY KEY
);
CREATE TABLE t2 (
    id INTEGER DEFAULT nextval('seq') REFERENCES t1(id) ON DELETE SET DEFAULT
);
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Удаление записи из `t1` приведёт к изменению ссылающихся записей в `t2` на значение по умолчанию из последовательности, что может нарушать логику приложения

#### Ответ от Claude

При `ON DELETE SET DEFAULT` PostgreSQL при удалении строки из `t1` устанавливает в ссылающихся строках `t2.id` значение DEFAULT столбца, то есть вызывает `nextval('seq')`. Это порождает несколько проблем:

1. Каждое удаление из `t1` будет **инкрементировать последовательность** `seq`, расходуя её значения.
2. Новое значение `nextval('seq')` используется как внешний ключ и должно ссылаться на существующую запись в `t1`. Если такой строки в `t1` нет — нарушение ограничения FK, и операция DELETE завершится ошибкой.
3. Если ключ случайно совпал с реальной записью в `t1`, строки `t2` получат другой родительский объект — **скрытая ошибка логики приложения**.

Источники: [PostgreSQL §5.5 Constraints — Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK); [§9.17 Sequence Functions](https://www.postgresql.org/docs/current/functions-sequence.html).

---

### Вопрос 6. В таблице `some_table` 1 миллион записей. На `id` — B-Tree индекс, на `name` — GIN-индекс для полнотекстового поиска. Выборка данных составляет менее 0.1% от общего объёма. Какой запрос будет оптимально использовать индексы?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE TABLE some_table (
    id   SERIAL,
    name VARCHAR(30),
    description TEXT
);
CREATE INDEX some_table_id_index ON some_table USING btree(id);
CREATE INDEX some_table_name_gin_index ON some_table USING gin(to_tsvector('english', name));
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:**
```sql
SELECT * FROM some_table
WHERE to_tsvector('english', name) @@ to_tsquery('example');
```

#### Ответ от Claude

GIN-индекс `some_table_name_gin_index` создан над выражением `to_tsvector('english', name)`. PostgreSQL сможет использовать его только если в запросе присутствует **то же самое выражение** с оператором `@@` (полнотекстовое совпадение). Именно это и делает правильный вариант.

Почему остальные варианты хуже:
- Запрос по `id` с фильтром высокой кардинальности будет использовать B-Tree, а не GIN.
- Запрос с `LIKE '%example%'` не может использовать ни B-Tree, ни GIN-индекс по `tsvector`.

При выборке < 0.1% строк планировщик предпочтёт Index Scan / Bitmap Index Scan поверх GIN, а не Sequential Scan.

Источники: [PostgreSQL §12. Full Text Search](https://www.postgresql.org/docs/current/textsearch.html); [§12.9 GIN Indexes for Full Text Search](https://www.postgresql.org/docs/current/textsearch-indexes.html).

---

### Вопрос 7. Таблица `logs` содержит миллиарды записей. Частый запрос выбирает записи по `user_id` и фильтрует по диапазону `event_time`. Какой индекс лучше всего подходит для ускорения?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE TABLE logs (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    event_time TIMESTAMP NOT NULL,
    action     TEXT
);
-- Часто используемый запрос
SELECT * FROM logs
WHERE user_id = 12345
  AND event_time BETWEEN '2024-01-01' AND '2024-01-31';
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:**
```sql
CREATE INDEX logs_user_event_index ON logs(user_id, event_time);
```

#### Ответ от Claude

Составной индекс `(user_id, event_time)` оптимален по следующим причинам:

1. **Равенство по первому столбцу (`user_id = 12345`)** позволяет планировщику перейти непосредственно к нужному диапазону в B-Tree.
2. **Диапазонный фильтр по второму столбцу (`event_time BETWEEN …`)** обрабатывается внутри уже выбранного поддерева индекса, без дополнительного сканирования.

Порядок столбцов важен: столбец с предикатом равенства должен стоять первым, столбец с предикатом диапазона — вторым. Инвертированный порядок `(event_time, user_id)` приведёт к сканированию большего диапазона.

Источники: [PostgreSQL §11.3 Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html); [§14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).

---

### Вопрос 8. Запускаются две транзакции `t1` и `t2`, каждая читает SUM одного класса и вставляет строку в другой класс. Какой уровень изоляции НЕ позволит выполнить commit?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
-- t1
SELECT SUM(value) FROM some_table WHERE class = 1;
INSERT INTO some_table(class, value) VALUES (2, 30);
COMMIT;
-- t2
SELECT SUM(value) FROM some_table WHERE class = 2;
INSERT INTO some_table(class, value) VALUES (1, 300);
COMMIT;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Serializable

#### Ответ от Claude

Это классический пример **аномалии записи (write skew)** / **сериализационного конфликта**. Транзакции `t1` и `t2` читают данные, на которые влияют записи друг друга:

- `t1` читает `SUM` класса 1, пишет в класс 2;
- `t2` читает `SUM` класса 2, пишет в класс 1.

При любом последовательном порядке результаты были бы разными, чем при параллельном выполнении — это нарушение сериализуемости.

На уровне `SERIALIZABLE` PostgreSQL использует механизм **SSI (Serializable Snapshot Isolation)**, который отслеживает зависимости чтение-запись между транзакциями. Обнаружив цикл зависимостей (read-write anti-dependency cycle), PostgreSQL откажет одной из транзакций с ошибкой `ERROR: could not serialize access due to read/write dependencies among transactions` (SQLSTATE 40001). Транзакция должна быть повторена.

На уровнях `READ COMMITTED` и `REPEATABLE READ` обе транзакции успешно завершатся, хотя результат может не соответствовать ни одному последовательному порядку.

Источники: [PostgreSQL §13.2.3 Serializable Isolation Level](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-SERIALIZABLE); [§13.5 Serialization Failure Handling](https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html).

---

### Вопрос 9. В PostgreSQL вы создаёте индекс в транзакции на таблице `users`. Какая команда из второй транзакции выполнится без конфликтов?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
-- Первая транзакция
BEGIN;
CREATE INDEX idx_users_name ON users(name);
-- Вторая транзакция
<выбранная команда>
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** `SELECT * FROM users;`

#### Ответ от Claude

`CREATE INDEX` (без `CONCURRENTLY`) внутри транзакции захватывает блокировку уровня **SHARE** на таблицу. Эта блокировка:

- **конфликтует** с `INSERT`, `UPDATE`, `DELETE` (которые требуют `ROW EXCLUSIVE`) — они будут ждать;
- **совместима** с `ACCESS SHARE`, который захватывает обычный `SELECT` без `FOR UPDATE / FOR SHARE`.

Поэтому `SELECT * FROM users;` выполнится без ожидания: блокировка `SHARE` не конфликтует с `ACCESS SHARE`.

Источник: [PostgreSQL §13.3 Explicit Locking — Table-Level Locks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-TABLES); [CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html).

---

### Вопрос 10. Какие утверждения о следующем запросе создания материализованного представления правдивы?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE MATERIALIZED VIEW some_view AS
SELECT * FROM some_table ORDER BY id DESC
WITH NO DATA;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Для представления `some_view` можно создать индекс

#### Ответ от Claude

`WITH NO DATA` означает, что при создании представление не заполняется данными и не может быть запрошено (помечается как «несканируемое») до вызова `REFRESH MATERIALIZED VIEW some_view`. Однако **создать индекс на него можно** — PostgreSQL хранит определение структуры столбцов даже для пустого материализованного представления, и `CREATE INDEX` на нём допустим.

Это особенно полезно для `REFRESH MATERIALIZED VIEW CONCURRENTLY`: он требует наличия уникального индекса на представлении до первого наполнения данными.

Источники: [PostgreSQL CREATE MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-creatematerializedview.html); [§39.3 Materialized Views](https://www.postgresql.org/docs/current/rules-materializedviews.html).

---

### Вопрос 11. У вас есть рабочая база данных с высокой нагрузкой и её копия. Вы хотите проанализировать производительность запроса, исключив влияние нагрузки. Какую команду следует использовать на копии?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** `EXPLAIN (ANALYZE, BUFFERS)`

#### Ответ от Claude

`EXPLAIN (ANALYZE, BUFFERS)` — наиболее полный инструмент анализа производительности запроса:

- **`ANALYZE`** — фактически выполняет запрос и показывает реальное время выполнения каждого узла плана, а не только оценочные стоимости.
- **`BUFFERS`** — выводит информацию об операциях с буферным кешем: количество обращений к shared/local/temp буферам (hits, reads, dirtied, written). Это позволяет определить, какие узлы плана наиболее «тяжёлые» по вводу-выводу.

Использование на **копии** базы (а не на продакшн-сервере) оправдано: `EXPLAIN ANALYZE` реально выполняет запрос, что при долгих запросах или `DELETE`/`UPDATE` может повлиять на данные и создать дополнительную нагрузку.

Источник: [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html); [§14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).

---

### Вопрос 12. В таблице `orders` 1 миллион записей, на `customer_id` — B-Tree индекс. Запрос выбирает 90% строк по `customer_id`. Какой тип сканирования выберет планировщик?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE TABLE orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INTEGER NOT NULL,
    order_date    DATE,
    total_amount  NUMERIC
);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
-- Запрос
EXPLAIN SELECT * FROM orders WHERE customer_id < 900000;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Seq Scan

#### Ответ от Claude

При выборке ~90% строк таблицы планировщик PostgreSQL выбирает **Sequential Scan** (последовательное сканирование), а не Index Scan. Причина — стоимостная модель планировщика:

- **Index Scan** при большой доле возвращаемых строк порождает огромное количество случайных обращений к страницам таблицы (random I/O), что медленнее, чем линейное чтение всех страниц.
- **Sequential Scan** читает страницы таблицы линейно, что в разы быстрее на дисковых и даже SSD-системах при высокой доле выборки.

Как правило, планировщик предпочитает Index Scan при выборке менее нескольких процентов строк (зависит от `random_page_cost`, `seq_page_cost` и размера таблицы). При 90% выборке Seq Scan заведомо дешевле.

Источники: [PostgreSQL §14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html); [§11.1 Introduction — When do indexes help?](https://www.postgresql.org/docs/current/indexes-intro.html).

---

### Вопрос 13. Частота вставок с `action='login'` выросла в 10 раз. Оперативно откатить релиз невозможно. Нужно временно не вставлять записи с `action='login'`, сохранив уже существующие. Как это сделать?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

```sql
CREATE TABLE action_log (
    id          SERIAL,
    action      VARCHAR,
    description TEXT
);
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Создать BEFORE INSERT триггер, запрещающий `'login'`

#### Ответ от Claude

BEFORE INSERT триггер — правильный подход: он перехватывает вставку **до** того, как строка появится в таблице, и может отменить её, вернув `NULL`.

Пример реализации:

```sql
CREATE OR REPLACE FUNCTION block_login_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.action = 'login' THEN
        RETURN NULL;  -- подавляет вставку строки
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_block_login
BEFORE INSERT ON action_log
FOR EACH ROW EXECUTE FUNCTION block_login_insert();
```

Согласно документации, если строковый триггер `BEFORE` возвращает `NULL`, менеджер триггеров пропускает операцию для данной строки (вставка не происходит). Уже существующие строки с `action='login'` остаются нетронутыми.

Когда проблема будет устранена, триггер удаляется командой `DROP TRIGGER`.

Источники: [PostgreSQL §37.1 Overview of Trigger Behavior](https://www.postgresql.org/docs/current/trigger-definition.html); [§41.10 Trigger Functions in PL/pgSQL](https://www.postgresql.org/docs/current/plpgsql-trigger.html).

---

### Вопрос 14. Пользователь `manuel` должен получить полный доступ к таблице `kinds`. Команда `GRANT` выполнена пользователем, который не является суперпользователем и не является владельцем таблицы. Каков результат?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Команда завершится ошибкой, так как исполнитель команды не является владельцем таблицы

#### Ответ от Claude

В PostgreSQL право выдавать привилегии на объект имеют:

1. **Владелец объекта** — может выдавать любые привилегии на свои объекты.
2. **Суперпользователь** — действует как владелец любого объекта.
3. **Пользователь с `GRANT OPTION`** — может делегировать только те привилегии, которые ему явно переданы с опцией `WITH GRANT OPTION`.

Если ни одно из условий не выполнено, PostgreSQL возвращает ошибку: `ERROR: permission denied for table kinds`.

Источники: [PostgreSQL GRANT](https://www.postgresql.org/docs/current/sql-grant.html); [§5.8 Privileges](https://www.postgresql.org/docs/current/ddl-priv.html).

---

### Вопрос 15. Количество запросов на запись возросло в несколько раз при том же уровне запросов на чтение; также повысились требования к отказоустойчивости. Большинство запросов — по ключу. Какими методиками можно воспользоваться?

**Категория:** PostgreSQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — postgresql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/postgresql/advanced.md)

**Правильный ответ:** Репликация вместе с горизонтальным шардированием

#### Ответ от Claude

Решение объединяет две взаимодополняющих стратегии:

**Горизонтальное шардирование (Horizontal Sharding / Data Partitioning)**
Данные разбиваются на фрагменты (шарды) по ключу, каждый шард живёт на отдельном узле-мастере. Это масштабирует **запись**: нагрузка на запись распределяется между несколькими первичными узлами. Поскольку большинство запросов идёт по ключу, маршрутизация запросов к нужному шарду происходит эффективно.

**Репликация (Replication)**
Каждый шард-мастер реплицируется на один или несколько реплик. Репликация обеспечивает:
- **Отказоустойчивость**: при выходе из строя мастера реплика принимает трафик.
- **Масштабирование чтения**: реплики могут обслуживать read-запросы.

Одна лишь репликация не решает проблему роста записи (все записи идут только на мастер). Одно лишь шардирование без репликации не даёт отказоустойчивости. Вместе — они покрывают оба требования.

Источник: [PostgreSQL §26 High Availability, Load Balancing, and Replication](https://www.postgresql.org/docs/current/high-availability.html).

---
