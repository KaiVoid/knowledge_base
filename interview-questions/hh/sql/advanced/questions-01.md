# SQL — Advanced (HH), часть 1 (вопросы 1–15)

### Вопрос 1. Что произойдёт, если при использовании GROUP BY указаны колонки, но не указаны агрегирующие функции?

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** запрос вернёт уникальные значения по колонкам, которые прописаны и в GROUP BY, и в SELECT

#### Ответ от Claude

`GROUP BY` без агрегатных функций возвращает одну строку на каждую уникальную комбинацию значений в перечисленных колонках — семантически это аналог `SELECT DISTINCT`. В стандартном SQL (и PostgreSQL) каждый столбец в `SELECT`, не входящий в агрегатную функцию, обязан присутствовать в `GROUP BY`; если это условие нарушено, СУБД вернёт ошибку. Таким образом, при корректном запросе результат — уникальные комбинации значений по колонкам из `GROUP BY`.

Источник: [PostgreSQL docs — GROUP BY Clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP).

---

### Вопрос 2. Что произойдёт, если при использовании GROUP BY применить агрегирующую функцию MAX к колонке, содержащей строковые значения?

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** для каждого уникального значения в GROUP BY вернётся последняя строка по алфавиту

#### Ответ от Claude

`MAX` над текстовым столбцом работает по правилам сортировки (collation) соответствующего типа. В PostgreSQL строки сравниваются лексикографически (в соответствии с заданным collation, по умолчанию — локаль базы данных). `MAX` возвращает строку, которая стоит последней в этом порядке сортировки — то есть «наибольшую» в алфавитном порядке. Для каждой группы, выделенной `GROUP BY`, возвращается своя «максимальная» строка.

Источник: [PostgreSQL docs — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html).

---

### Вопрос 3. Есть две таблицы из одной колонки; в них содержатся NULL-значения. В левой таблице — пять значений NULL, в правой — семь. Сколько строк вернётся с NULL при выполнении различных типов соединений?

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** INNER — 0, LEFT — 5, RIGHT — 7, FULL — 12

#### Ответ от Claude

NULL не равен NULL (`NULL = NULL` возвращает `UNKNOWN`, а не `TRUE`), поэтому при соединении по условию `ON left.col = right.col` ни одна строка из левой таблицы не совпадёт ни с одной строкой из правой — INNER JOIN не вернёт ни одной строки с NULL.

- **INNER JOIN:** 0 строк (NULL не соединяется с NULL).
- **LEFT JOIN:** все 5 строк левой таблицы сохраняются, колонка правой таблицы содержит NULL.
- **RIGHT JOIN:** все 7 строк правой таблицы сохраняются, колонка левой таблицы содержит NULL.
- **FULL JOIN:** 5 + 7 = 12 строк — все строки из обеих таблиц без совпадений.

Источник: [PostgreSQL docs — Joined Tables](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOIN); [PostgreSQL docs — NULL handling](https://www.postgresql.org/docs/current/functions-comparison.html).

---

### Вопрос 4. Какой будет результат, если значение в колонке таблицы подходит под несколько условий в CASE?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- вернутся все значения THEN, подходящие под условия
- вернётся NULL
- ошибка
- вернётся значение THEN первого условия
- вернётся значение THEN последнего условия

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** вернётся значение THEN первого условия

#### Ответ от Claude

Выражение `CASE` в SQL работает по принципу «первое совпадение выигрывает»: ветки проверяются слева направо (сверху вниз) в том порядке, в котором они записаны. Как только первое условие `WHEN` вычисляется в `TRUE`, возвращается соответствующее значение `THEN`, и дальнейшие ветки не проверяются. Ошибки не возникает; NULL возвращается только если ни одна ветка не совпала и нет `ELSE`.

Источник: [PostgreSQL docs — Conditional Expressions — CASE](https://www.postgresql.org/docs/current/functions-conditional.html#FUNCTIONS-CASE).

---

### Вопрос 5. В этом SQL-запросе допущено несколько ошибок (в данных при этом ошибок нет). Выберите вариант со всеми перечисленными ошибками.

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** один из подзапросов в WHERE возвращает две колонки; для двух подзапросов нет алиаса; JOIN происходит по полю, которого нет в подзапросе

#### Ответ от Claude

⚠️ Вопрос ссылается на изображение («в данном SQL-запросе»), которого нет в репозитории. Ответ восстановлен по тексту единственного варианта.

Перечисленные ошибки типичны для многоуровневых SQL-запросов с подзапросами:

1. **Подзапрос в WHERE возвращает две колонки**: скалярный контекст (например, `column = (subquery)`) требует ровно одной колонки; при двух колонках PostgreSQL выбросит ошибку `ERROR: subquery must return only one column`.
2. **Отсутствие алиасов у подзапросов во FROM**: в PostgreSQL каждый подзапрос во `FROM` обязан иметь псевдоним (`AS alias`); иначе — `ERROR: subquery in FROM must have an alias`.
3. **JOIN по полю, которого нет в подзапросе**: если в `ON` или `USING` указано поле, не выбранное в подзапросе, запрос завершится с ошибкой `column does not exist`.

Источники: [PostgreSQL docs — Subqueries as Table Expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-SUBQUERIES); [PostgreSQL docs — Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html).

---

### Вопрос 6. У вас есть уже существующее материальное представление test_view. Вы хотите добавить в него новый столбец num_purchases. Как сделать это синтаксически верно?

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `delete materialized view test_view; create or replace materialized_view test_view as select user_id, min(dt) as first_payed, sum(price) as revenue, count(*) as num_purchases group by user_id`

#### Ответ от Claude

⚠️ HH отмечает этот вариант, но в нём содержится синтаксическая ошибка: используется `DELETE MATERIALIZED VIEW`, которого в PostgreSQL не существует. Правильная команда для удаления материализованного представления — `DROP MATERIALIZED VIEW`. Кроме того, `CREATE OR REPLACE MATERIALIZED VIEW` в PostgreSQL не поддерживается (синтаксис `OR REPLACE` есть только у обычных `VIEW`); чтобы добавить столбец в материализованное представление, его нужно пересоздать через `DROP MATERIALIZED VIEW` + `CREATE MATERIALIZED VIEW`.

Корректная последовательность для добавления столбца в материализованное представление в PostgreSQL:

```sql
DROP MATERIALIZED VIEW test_view;
CREATE MATERIALIZED VIEW test_view AS
    SELECT user_id,
           min(dt)    AS first_payed,
           sum(price) AS revenue,
           count(*)   AS num_purchases
    GROUP BY user_id;
```

Ни `ALTER MATERIALIZED VIEW ... ADD COLUMN`, ни прямое изменение структуры материализованного представления без пересоздания в PostgreSQL не поддерживается. Единственный способ добавить столбец — пересоздать представление через `DROP` + `CREATE`.

Ответ HH верен по смыслу (пересоздание через удаление и создание заново), но содержит опечатку `DELETE` вместо `DROP`. В реальном запросе нужно использовать `DROP MATERIALIZED VIEW`.

Источник: [PostgreSQL docs — CREATE MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-creatematerializedview.html); [PostgreSQL docs — DROP MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-dropmaterializedview.html).

---

### Вопрос 7. Укажите запрос, который выберет все фильмы, связанные со словами bad, good, angry. В названиях фильмов могут содержаться эти слова в разном виде, например в разных регистрах (Badboys) или в изменённой форме (goodspeed).

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `select movie_name from movies where lower(movie_name) like '%bad%' or lower(movie_name) like '%angry%' or lower(movie_name) like '%good%'`

#### Ответ от Claude

Для регистронезависимого поиска подстроки в PostgreSQL используется `lower()` + `LIKE '%паттерн%'` (или оператор `ILIKE`). Подход `lower(movie_name) like '%bad%'` приводит значение колонки к нижнему регистру и ищет подстроку `bad` в любой позиции — это покроет `Badboys`, `BADMINTON`, `badass` и т.д.

Альтернативный, более лаконичный вариант на PostgreSQL:
```sql
SELECT movie_name FROM movies
WHERE movie_name ILIKE '%bad%'
   OR movie_name ILIKE '%good%'
   OR movie_name ILIKE '%angry%';
```
`ILIKE` — регистронезависимый аналог `LIKE` в PostgreSQL.

Источник: [PostgreSQL docs — Pattern Matching](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE).

---

### Вопрос 8. Выберите вариант, где для каждого запроса указана ошибка, из-за которой запрос либо не сработает, либо вернёт неверные значения.

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `regexp_replace возвращает некорректное значение для CAST`

#### Ответ от Claude

⚠️ Вопрос ссылается на изображение с несколькими запросами, которого нет в репозитории. Ответ восстановлен по тексту единственного варианта.

`regexp_replace` в PostgreSQL возвращает значение типа `text`. Если результат функции содержит символы, несовместимые с целевым типом при `CAST` (например, в строке после замены остались нецифровые символы, а `CAST` пытается преобразовать в `integer` или `numeric`), запрос завершится ошибкой вида `ERROR: invalid input syntax for type integer`. Это типичная ошибка при обработке «грязных» данных: `regexp_replace` удаляет часть символов, но не гарантирует, что результат будет валидным представлением нужного типа.

Источник: [PostgreSQL docs — String Functions — regexp_replace](https://www.postgresql.org/docs/current/functions-string.html#FUNCTION-REGEXP-REPLACE); [PostgreSQL docs — Type Casting](https://www.postgresql.org/docs/current/sql-expressions.html#SQL-SYNTAX-TYPE-CASTS).

---

### Вопрос 9. Какой будет результат, если в запросе неправильно рассчитаны показатели?

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** скользящая сумма заказов, разница во времени между заказами, ранг пользователя по сумме заказов

#### Ответ от Claude

⚠️ Вопрос ссылается на изображение с конкретным SQL-запросом, которого нет в репозитории. Ответ восстановлен по тексту единственного варианта.

Судя по ответу, в задаче фигурирует запрос, вычисляющий три оконных показателя:
- **Скользящая сумма заказов** — `SUM(...) OVER (...)` с оконным фреймом.
- **Разница во времени между заказами** — вычитание значений через `LAG()` или разность дат.
- **Ранг пользователя по сумме заказов** — `RANK()` или `DENSE_RANK() OVER (ORDER BY sum(...))`.

Если в оконном фрейме (`ROWS BETWEEN` / `RANGE BETWEEN`) допущена ошибка или в `PARTITION BY` / `ORDER BY` указаны неверные колонки, все три показателя окажутся некорректными. Именно это и является «неправильным результатом».

Источник: [PostgreSQL docs — Window Functions](https://www.postgresql.org/docs/current/functions-window.html); [PostgreSQL docs — Window Function Calls](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).

---

### Вопрос 10. Выберите синтаксически корректный запрос.

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `alter table public.table_1 modify (user_id int, salary float, department_id int)`

#### Ответ от Claude

⚠️ HH отмечает этот вариант, однако синтаксис `ALTER TABLE ... MODIFY (...)` относится к **Oracle** и **MySQL**, но **не является корректным в PostgreSQL**.

В PostgreSQL для изменения типа столбца используется:
```sql
ALTER TABLE public.table_1
    ALTER COLUMN user_id TYPE int,
    ALTER COLUMN salary TYPE float,
    ALTER COLUMN department_id TYPE int;
```

Ключевое слово `MODIFY` в PostgreSQL отсутствует и вызовет `ERROR: syntax error at or near "MODIFY"`.

Если вопрос составлен в контексте Oracle или MySQL, то указанный вариант синтаксически верен для этих СУБД. Однако весь остальной набор вопросов в этом квизе ориентирован на PostgreSQL, поэтому ответ HH следует считать некорректным для PostgreSQL-контекста.

Источники: [PostgreSQL docs — ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html); [Oracle docs — ALTER TABLE MODIFY](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/ALTER-TABLE.html).

---

### Вопрос 11. Какой из следующих индексов будет наиболее оптимальным для ускорения запросов, фильтрующих данные по user_id и сортирующих их по created_at?

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `create index payments_user_id_created_at_idx on payments using btree (user_id, created_at);`

#### Ответ от Claude

Составной индекс `(user_id, created_at)` по методу B-tree идеально покрывает этот паттерн запросов:

1. **Фильтрация по `user_id`**: B-tree индекс поддерживает точный поиск по первому ключу; все строки нужного пользователя будут найдены без полного сканирования таблицы.
2. **Сортировка по `created_at`**: внутри каждого значения `user_id` данные в индексе уже хранятся в порядке `created_at`, поэтому СУБД не нужно выполнять дополнительную сортировку.

Порядок колонок в составном индексе критически важен: колонка равенства (`user_id`) должна идти первой, колонка диапазона/сортировки (`created_at`) — второй. Обратный порядок снизит эффективность.

Источник: [PostgreSQL docs — Indexes and ORDER BY](https://www.postgresql.org/docs/current/indexes-ordering.html); [PostgreSQL docs — Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html).

---

### Вопрос 12. Определите список разрешений, на который можно выдать или отозвать права с помощью операторов GRANT, REVOKE.

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- INSERT, SELECT, JOIN, CREATE
- IF, SELECT, JOIN, UNION
- GRANT, INSERT, UPDATE, EXCEPT
- CREATE, TRUNCATE, DELETE, TRIGGER
- INTERSECT, DROP, SELECT, ALL

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `CREATE, TRUNCATE, DELETE, TRIGGER`

#### Ответ от Claude

В PostgreSQL операторы `GRANT` и `REVOKE` работают с привилегиями, которые могут быть выданы на объекты базы данных. Для таблиц поддерживаются следующие привилегии: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`. На уровне схемы — `CREATE`, `USAGE`. На уровне базы данных — `CREATE`, `CONNECT`, `TEMPORARY`.

Из предложенного списка `CREATE, TRUNCATE, DELETE, TRIGGER`:
- `TRUNCATE` — привилегия на таблицу
- `DELETE` — привилегия на таблицу
- `TRIGGER` — привилегия на таблицу
- `CREATE` — привилегия на схему или базу данных

Элементы из других вариантов, которые **не являются** привилегиями GRANT/REVOKE: `JOIN`, `UNION`, `IF`, `INTERSECT`, `EXCEPT`, `ALL` (как ключевое слово вне контекста) — это SQL-операторы/клаузы, а не привилегии.

Источник: [PostgreSQL docs — GRANT](https://www.postgresql.org/docs/current/sql-grant.html).

---

### Вопрос 13. Выберите верное утверждение относительно операторов EXISTS и ANY в SQL.

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `EXISTS` проверяет, содержит ли подзапрос хотя бы одну строку, и возвращает TRUE, если строка есть

#### Ответ от Claude

`EXISTS (subquery)` возвращает `TRUE`, если подзапрос возвращает хотя бы одну строку, иначе — `FALSE`. Содержимое строк при этом не имеет значения; СУБД прекращает выполнение подзапроса при нахождении первой строки.

`ANY (subquery)` используется в связке с оператором сравнения: `value op ANY (subquery)`. Выражение возвращает `TRUE`, если хотя бы для одной строки из подзапроса выполняется условие сравнения. Например: `salary > ANY (SELECT salary FROM employees WHERE department = 'IT')`.

Ключевые различия:
- `EXISTS` — булев предикат, проверяет **факт наличия** строк.
- `ANY` — сравнивает **значение** с набором значений из подзапроса.

Источник: [PostgreSQL docs — Subquery Expressions — EXISTS](https://www.postgresql.org/docs/current/functions-subquery.html#FUNCTIONS-SUBQUERY-EXISTS); [PostgreSQL docs — ANY/ALL](https://www.postgresql.org/docs/current/functions-subquery.html#FUNCTIONS-SUBQUERY-ANY-SOME).

---

### Вопрос 14. Выберите верное утверждение относительно операторов INTERSECT, EXCEPT, UNION и т.д.

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Смена порядка запросов для EXCEPT поменяет выводимые данные

#### Ответ от Claude

`EXCEPT` — не коммутативный оператор: `A EXCEPT B` возвращает строки, которые есть в A, но отсутствуют в B. При смене порядка (`B EXCEPT A`) результат будет другим — строки из B, которых нет в A. Это принципиальное отличие от `UNION` и `INTERSECT`, которые коммутативны (порядок операндов не меняет результирующий набор, только возможный порядок строк).

Примеры поведения операторов множеств в PostgreSQL:
- `UNION` / `UNION ALL` — объединение двух результирующих наборов.
- `INTERSECT` — пересечение (строки, присутствующие в обоих результатах).
- `EXCEPT` — разность (строки первого результата, отсутствующие во втором).

Источник: [PostgreSQL docs — Combining Queries (UNION, INTERSECT, EXCEPT)](https://www.postgresql.org/docs/current/queries-union.html).

---

### Вопрос 15. Выберите операторы, относящиеся только к DDL.

**Категория:** SQL (HH) · **Уровень:** Advanced

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `DROP, ALTER, CREATE, RENAME`

#### Ответ от Claude

DDL (Data Definition Language) — подмножество SQL для определения и изменения структуры объектов базы данных. Стандартные DDL-операторы:

- `CREATE` — создание объекта (таблица, индекс, представление и т.д.)
- `ALTER` — изменение структуры объекта
- `DROP` — удаление объекта
- `RENAME` — переименование объекта (в PostgreSQL реализуется через `ALTER TABLE ... RENAME TO ...`)
- `TRUNCATE` — некоторые источники относят его к DDL (в PostgreSQL он имеет DDL-семантику, т.к. сбрасывает внутренние счётчики)

`INSERT`, `UPDATE`, `DELETE`, `SELECT` — это DML (Data Manipulation Language). `GRANT`, `REVOKE` — DCL (Data Control Language). `COMMIT`, `ROLLBACK` — TCL (Transaction Control Language).

Источник: [PostgreSQL docs — SQL Commands](https://www.postgresql.org/docs/current/sql-commands.html).

---
