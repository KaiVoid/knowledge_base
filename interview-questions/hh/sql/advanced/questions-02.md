# SQL — Advanced (HH), часть 2 (вопросы 16–27)

### Вопрос 16. Почему этот запрос вызовет ошибку?

**Категория:** SQL (HH) · **Уровень:** Advanced

```sql
SELECT department, COUNT(*), salary
FROM employees
GROUP BY department;
```

**Варианты ответа:**
- Нельзя группировать по строковым полям
- salary не включён в `GROUP BY` и не агрегирован
- department нельзя использовать в `GROUP BY`
- `COUNT` не может сочетаться с `GROUP BY`
- `SELECT` должен содержать только агрегатные функции

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** salary не включён в `GROUP BY` и не агрегирован

#### Ответ от Claude

В SQL (и в PostgreSQL в частности) при использовании `GROUP BY` каждый столбец в `SELECT`, не являющийся аргументом агрегатной функции, обязан присутствовать в предложении `GROUP BY`. В запросе `department` входит в `GROUP BY`, `COUNT(*)` — агрегатная функция, а `salary` — ни то, ни другое. PostgreSQL выбросит ошибку:

```
ERROR: column "employees.salary" must appear in the GROUP BY clause
or be used in an aggregate function
```

Исправление — либо добавить `salary` в `GROUP BY`, либо применить к нему агрегатную функцию (`MAX(salary)`, `AVG(salary)` и т.д.).

Источник: [PostgreSQL docs — GROUP BY Clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP).

---

### Вопрос 17. В чём причина, по которой AVG(price) может вернуть NULL, даже если столбец price существует?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Все значения price — NULL
- Все значения price равны нулю
- В запросе нет `GROUP BY`
- В таблице только одна строка
- `AVG` не работает с типом `string`

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Все значения price — NULL

#### Ответ от Claude

Агрегатные функции в SQL игнорируют `NULL` при вычислении. `AVG` суммирует ненулевые значения и делит на их количество. Если **все** значения в столбце равны `NULL`, то нет ни одного ненулевого значения для усреднения — и функция возвращает `NULL`.

Разбор остальных вариантов:
- **Все значения равны нулю**: `AVG` вернёт `0.0`, а не `NULL`.
- **Нет `GROUP BY`**: отсутствие `GROUP BY` не влияет на возможность возврата `NULL` — `AVG` без `GROUP BY` работает над всей таблицей.
- **Одна строка**: `AVG` с одной ненулевой строкой вернёт это значение.
- **`AVG` не работает с `string`**: `AVG` действительно не работает со строковыми типами, но это будет ошибка типов, а не NULL.

Источник: [PostgreSQL docs — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html).

---

### Вопрос 18. Какая особенность FULL OUTER JOIN отличает его от LEFT и RIGHT JOIN?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Объединяет все строки из обеих таблиц, даже без совпадений
- Быстрее INNER JOIN
- Не может использовать ON
- Фильтрует строки, не попавшие в оба JOIN
- Всегда требует агрегатных функций

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Объединяет все строки из обеих таблиц, даже без совпадений

#### Ответ от Claude

`FULL OUTER JOIN` объединяет поведение `LEFT JOIN` и `RIGHT JOIN` одновременно:
- Все строки из **левой** таблицы присутствуют в результате (как в `LEFT JOIN`), даже если нет совпадений в правой — в таком случае колонки правой таблицы заполняются `NULL`.
- Все строки из **правой** таблицы присутствуют в результате (как в `RIGHT JOIN`), даже если нет совпадений в левой — колонки левой заполняются `NULL`.

Разбор ложных вариантов:
- **Быстрее INNER JOIN**: `FULL OUTER JOIN` сложнее и, как правило, медленнее.
- **Не может использовать ON**: все JOIN-операции (кроме `CROSS JOIN`) используют `ON` или `USING`.
- **Фильтрует строки, не попавшие**: напротив, `FULL OUTER JOIN` **включает** строки без совпадений.
- **Всегда требует агрегатных функций**: нет такого требования.

Источник: [PostgreSQL docs — Joined Tables](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOIN).

---

### Вопрос 19. Какой подзапрос вызовет ошибку при выполнении основного запроса?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- `select * from employees where department in (select department from employees)`
- `select * from employees where salary > all (select salary from employees)`
- `select * from employees where salary > (select department, max(salary) from employees group by department)`
- `select * from employees where exists (select 1 from employees where salary > 100000)`
- `select * from employees where salary > (select max(salary) from employees)`

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `select * from employees where salary > (select department, max(salary) from employees group by department)`

#### Ответ от Claude

Подзапрос `(select department, max(salary) from employees group by department)` возвращает **две колонки** (`department` и `max(salary)`). В контексте `salary > (subquery)` ожидается **скалярный** подзапрос — ровно одна строка, одна колонка. PostgreSQL выбросит ошибку:

```
ERROR: subquery must return only one column
```

Разбор остальных вариантов:
- `IN (subquery)` — корректно; подзапрос возвращает один столбец.
- `> ALL (subquery)` — корректно; `ALL` сравнивает значение с каждой строкой одностолбцового подзапроса.
- `EXISTS (select 1 ...)` — корректно; `EXISTS` не проверяет содержимое строк.
- `> (select max(salary) ...)` — корректно; скалярный подзапрос возвращает одну строку и одну колонку.

Источник: [PostgreSQL docs — Scalar Subqueries](https://www.postgresql.org/docs/current/sql-expressions.html#SQL-SYNTAX-SCALAR-SUBQUERIES); [PostgreSQL docs — Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html).

---

### Вопрос 20. Вы работаете с большим отчётом на основе таблицы transactions. Чтобы ускорить работу, вы хотите сохранить его результат в виде материального представления mv_report, но при этом понимаете, что данные будут обновляться не автоматически. Какой шаг нужно выполнять регулярно, чтобы в отчёте отражались свежие данные?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Выполнять `REFRESH MATERIALIZED VIEW mv_report`
- Выполнять `VACUUM ANALYZE` перед каждым `SELECT`
- Использовать `CREATE OR REPLACE MATERIALIZED VIEW` каждый раз
- Удалять и пересоздавать представление
- Перезапускать сервер баз данных

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Выполнять `REFRESH MATERIALIZED VIEW mv_report`

#### Ответ от Claude

Материализованное представление (`MATERIALIZED VIEW`) в PostgreSQL хранит результат запроса на диске. Данные не обновляются автоматически при изменении базовых таблиц — необходимо явно запустить перестройку командой:

```sql
REFRESH MATERIALIZED VIEW mv_report;
```

По умолчанию `REFRESH` блокирует чтение представления на время обновления. Для обновления без блокировки (но с требованием уникального индекса) используется:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_report;
```

Разбор ложных вариантов:
- `VACUUM ANALYZE` обновляет статистику планировщика и убирает «мёртвые» строки, но не перестраивает содержимое материализованного представления.
- `CREATE OR REPLACE MATERIALIZED VIEW` — DDL-команда для пересоздания определения, а не обновления данных.
- Удаление и пересоздание — неэффективно и влечёт потерю объекта и зависимых объектов.
- Перезапуск сервера — не обновляет данные и крайне разрушителен для работы.

Источник: [PostgreSQL docs — REFRESH MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html).

---

### Вопрос 21. Почему может быть опасно преобразовывать varchar-даты без валидации?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Строки нельзя использовать в фильтрах
- Потому что они всегда в формате ISO
- Можно получить ошибку, если формат не соответствует ожидаемому
- varchar не подходит для дат — они всегда NULL
- В некоторых СУБД нельзя преобразовать строку в дату

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Можно получить ошибку, если формат не соответствует ожидаемому

#### Ответ от Claude

При преобразовании `varchar` в тип `date` или `timestamp` (через `CAST`, `::date`, `TO_DATE()`) PostgreSQL ожидает, что строка соответствует определённому формату. Если данные содержат различные форматы (`2024-01-15`, `15/01/2024`, `January 15, 2024`), то часть значений вызовет ошибку:

```
ERROR: invalid input syntax for type date: "15/01/2024"
```

Это особенно критично в production-данных, которые вводились пользователями в свободной форме или импортировались из разных источников. Правильный подход — использовать `TO_DATE(value, 'DD/MM/YYYY')` с явным форматом или заранее валидировать значения.

Разбор ложных вариантов:
- Строки можно использовать в фильтрах (`WHERE column = 'value'`).
- Varchar-даты **не всегда** в формате ISO — в этом и состоит проблема.
- `varchar` не возвращает NULL при преобразовании — он вызывает ошибку.
- PostgreSQL умеет преобразовывать строки в даты, но требует корректного формата.

Источник: [PostgreSQL docs — Data Type Formatting Functions](https://www.postgresql.org/docs/current/functions-formatting.html).

---

### Вопрос 22. Почему следующий запрос может вернуть неверный ранг пользователя в пределах месяца?

**Категория:** SQL (HH) · **Уровень:** Advanced

```sql
rank() over (partition by date_trunc('month', order_date) order by sum(amount) over (partition by user_id))
```

**Варианты ответа:**
- `date_trunc` нельзя использовать в `partition by`
- Он возвращает одинаковый ранг для всех
- Он группирует по `user_id`, а не по месяцу
- Он использует оконную функцию внутри другой оконной функции
- `rank()` требует `group by`

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Он использует оконную функцию внутри другой оконной функции

#### Ответ от Claude

В SQL (и в PostgreSQL в частности) оконные функции **не могут** быть вложены друг в друга. Выражение `sum(amount) over (partition by user_id)` является оконной функцией, а `rank() over (... order by <оконная функция>)` пытается использовать её как аргумент `ORDER BY` другой оконной функции. PostgreSQL выбросит ошибку:

```
ERROR: window function calls cannot be nested
```

Корректный подход — вычислить `sum(amount)` в подзапросе или CTE, а затем применить `rank()` к результату:

```sql
WITH monthly_totals AS (
    SELECT user_id,
           date_trunc('month', order_date) AS month,
           sum(amount) AS total_amount
    FROM orders
    GROUP BY user_id, date_trunc('month', order_date)
)
SELECT user_id, month, total_amount,
       rank() OVER (PARTITION BY month ORDER BY total_amount DESC) AS user_rank
FROM monthly_totals;
```

Источник: [PostgreSQL docs — Window Function Calls](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).

---

### Вопрос 23. Вы хотите удалить колонку temp_flag из таблицы sessions. Какой SQL-запрос это реализует?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- `alter table sessions drop column temp_flag`
- `drop column temp_flag from sessions`
- `remove column temp_flag in sessions`
- `delete temp_flag from sessions`
- `alter sessions remove column temp_flag`

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `alter table sessions drop column temp_flag`

#### Ответ от Claude

Для удаления столбца из таблицы в PostgreSQL используется команда:

```sql
ALTER TABLE sessions DROP COLUMN temp_flag;
```

Это DDL-операция, изменяющая структуру таблицы. Ключевые слова: `ALTER TABLE` — модификация таблицы, `DROP COLUMN` — удаление столбца.

Разбор ложных вариантов:
- `DROP COLUMN temp_flag FROM sessions` — несуществующий синтаксис; `DROP COLUMN` требует `ALTER TABLE`.
- `REMOVE COLUMN temp_flag IN sessions` — `REMOVE` не является SQL-командой для управления столбцами.
- `DELETE temp_flag FROM sessions` — `DELETE` работает со строками данных, а не со столбцами.
- `ALTER SESSIONS REMOVE COLUMN temp_flag` — `REMOVE COLUMN` не является SQL-синтаксисом.

Источник: [PostgreSQL docs — ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html).

---

### Вопрос 24. Как можно ускорить отчёт, построенный на ресурсоёмком SQL-запросе к таблице logs, не изменяя сам запрос и его логику?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Удалить неиспользуемые поля из таблицы
- Сохранить результат запроса в отдельную таблицу и переиспользовать при построении отчёта
- Использовать кэш на клиентской стороне
- Разбить таблицу logs на подтаблицы по месяцам
- Заменить JOIN на агрегатные функции

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Сохранить результат запроса в отдельную таблицу и переиспользовать при построении отчёта

#### Ответ от Claude

Если нельзя изменять сам запрос, стандартное решение — кешировать его результат. В PostgreSQL для этого есть несколько подходов:

1. **Материализованное представление** (`MATERIALIZED VIEW`): результат запроса сохраняется на диске и обновляется по команде `REFRESH MATERIALIZED VIEW`. Отчёт читает из представления, а не выполняет тяжёлый запрос каждый раз.
2. **Временная или обычная таблица**: результат сохраняется в `CREATE TABLE report_cache AS SELECT ...` и используется повторно.

Разбор ложных вариантов:
- Удаление неиспользуемых полей меняет структуру таблицы (это изменение логики).
- Клиентский кэш помогает только при повторных идентичных запросах с одного клиента.
- Партиционирование по месяцам — это изменение структуры таблицы и требует адаптации запроса.
- Замена `JOIN` на агрегатные функции — изменение логики запроса.

Источник: [PostgreSQL docs — CREATE MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-creatematerializedview.html); [PostgreSQL docs — CREATE TABLE AS](https://www.postgresql.org/docs/current/sql-createtableas.html).

---

### Вопрос 25. В чём ключевое различие между `ANY` и `EXISTS`?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- `ANY` используется только с `WHERE IN`
- `EXISTS` работает только с числами
- `EXISTS` проверяет наличие строк, `ANY` — сравнивает значения
- `EXISTS` поддерживает только подзапросы без `WHERE`
- `ANY` быстрее, чем `EXISTS`

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** `EXISTS` проверяет наличие строк, `ANY` — сравнивает значения

#### Ответ от Claude

Ключевое различие между `EXISTS` и `ANY`:

- **`EXISTS (subquery)`** — булев предикат, который возвращает `TRUE`, если подзапрос вернул хотя бы одну строку. Содержимое строк не имеет значения. Используется как самостоятельный предикат в `WHERE`.
- **`value op ANY (subquery)`** — сравнивает значение с каждой строкой из подзапроса с помощью оператора `op` (`=`, `>`, `<` и т.д.). Возвращает `TRUE`, если хотя бы одно сравнение успешно. Требует оператора сравнения.

Примеры:
```sql
-- EXISTS: есть ли хоть один заказ у клиента?
WHERE EXISTS (SELECT 1 FROM orders WHERE orders.client_id = clients.id)

-- ANY: чья зарплата выше хотя бы одного сотрудника из IT?
WHERE salary > ANY (SELECT salary FROM employees WHERE department = 'IT')
```

Разбор ложных вариантов: `ANY` не ограничен `WHERE IN` (он работает с любым оператором сравнения); `EXISTS` работает с любыми типами данных; `EXISTS` может содержать подзапросы с `WHERE`; производительность зависит от конкретного плана выполнения.

Источник: [PostgreSQL docs — Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html).

---

### Вопрос 26. Что делает `UNION ALL` по сравнению с `UNION`?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Выполняет объединение без удаления дубликатов
- Автоматически сортирует результат
- Объединяет только числовые колонки
- Фильтрует строки по ключу
- Использует индекс для объединения

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Выполняет объединение без удаления дубликатов

#### Ответ от Claude

`UNION` объединяет результаты двух запросов и **удаляет дубликаты** (аналогично `DISTINCT`). Это требует сортировки или хеширования, что добавляет накладные расходы.

`UNION ALL` объединяет результаты **без удаления дубликатов**: все строки из обоих запросов включаются в результат. Это быстрее, поскольку не требует шага дедупликации.

Когда использовать `UNION ALL`:
- Когда гарантировано отсутствие дубликатов.
- Когда дубликаты допустимы или нужны.
- Для повышения производительности в аналитических запросах.

Разбор ложных вариантов: ни `UNION`, ни `UNION ALL` не сортируют результат автоматически (для сортировки нужен явный `ORDER BY`); оба работают с любыми типами столбцов (при совместимости типов); ни один не фильтрует строки по ключу и не использует индекс для объединения.

Источник: [PostgreSQL docs — Combining Queries (UNION, INTERSECT, EXCEPT)](https://www.postgresql.org/docs/current/queries-union.html).

---

### Вопрос 27. Что делает оператор `DROP TABLE`?

**Категория:** SQL (HH) · **Уровень:** Advanced

**Варианты ответа:**
- Переименовывает таблицу
- Создаёт копию таблицы
- Очищает таблицу от всех строк
- Обнуляет индексы таблицы
- Удаляет таблицу и все данные в ней

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/advanced.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/advanced.md)

**Правильный ответ:** Удаляет таблицу и все данные в ней

#### Ответ от Claude

`DROP TABLE` — DDL-команда, которая **полностью удаляет таблицу** из базы данных: удаляется и структура (определение таблицы), и все данные в ней, и связанные объекты (индексы, триггеры). Операция необратима.

```sql
DROP TABLE sessions;
-- или с защитой от ошибки, если таблицы нет:
DROP TABLE IF EXISTS sessions;
-- с каскадным удалением зависимых объектов (внешних ключей, представлений):
DROP TABLE sessions CASCADE;
```

Разбор ложных вариантов:
- **Переименование**: `ALTER TABLE sessions RENAME TO new_name`.
- **Копия таблицы**: `CREATE TABLE new_table AS SELECT * FROM sessions`.
- **Очистка строк без удаления таблицы**: `TRUNCATE TABLE sessions` или `DELETE FROM sessions`.
- **Обнуление индексов**: не существует как отдельная операция; `REINDEX TABLE sessions` перестраивает индексы.

Источник: [PostgreSQL docs — DROP TABLE](https://www.postgresql.org/docs/current/sql-droptable.html).

---
