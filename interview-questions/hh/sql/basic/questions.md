# SQL — Basic (HH)

### Вопрос 1. Какая команда применяется для удаления таблицы из базы данных в SQL?

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `DROP TABLE`

#### Ответ от Claude

`DROP TABLE имя_таблицы` полностью удаляет таблицу вместе со всеми данными и определением структуры. Команда необратима без резервной копии. Для удаления только данных (сохраняя структуру) используется `DELETE FROM` или `TRUNCATE`. Для удаления отдельного столбца — `ALTER TABLE ... DROP COLUMN`.

Источник: [PostgreSQL DROP TABLE](https://www.postgresql.org/docs/current/sql-droptable.html).

---

### Вопрос 2. Удалите столбец `old_email` из таблицы `Clients`.

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `ALTER TABLE Clients DROP COLUMN old_email;`

#### Ответ от Claude

`ALTER TABLE ... DROP COLUMN` удаляет столбец из существующей таблицы вместе со всеми данными в нём. Операция необратима. В PostgreSQL добавление опции `CASCADE` позволяет автоматически удалить зависимые объекты (индексы, ограничения, представления, ссылающиеся на этот столбец).

Источник: [PostgreSQL ALTER TABLE — DROP COLUMN](https://www.postgresql.org/docs/current/sql-altertable.html).

---

### Вопрос 3. Получите список имён и фамилий сотрудников с должностью «аналитик» (Analyst) из таблицы `Employees`.

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `SELECT first_name, last_name FROM Employees WHERE job_title = 'Analyst';`

#### Ответ от Claude

В оригинальном источнике ответ записан как `WHERE job_title = 'Analyst"'` — со смешанными кавычками (`'` открывает, `"` закрывает), что является OCR-опечаткой. Корректный запрос использует единообразные одинарные кавычки: `WHERE job_title = 'Analyst'`. Строковые литералы в стандартном SQL заключаются в одинарные кавычки.

Источник: [PostgreSQL §4.1.2.1 String Constants](https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-STRINGS); [§7.2.2 The WHERE Clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-WHERE).

---

### Вопрос 4. Что возвращает следующий запрос?

**Категория:** SQL (HH) · **Уровень:** Basic

```sql
SELECT MAX(salary), MIN(salary), COUNT(*) FROM Employees;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** Самую высокую и самую низкую заработную плату, а также общее количество сотрудников

#### Ответ от Claude

- `MAX(salary)` — максимальное значение `salary` по всей таблице.
- `MIN(salary)` — минимальное значение `salary`.
- `COUNT(*)` — количество всех строк в таблице, включая строки с `NULL` в `salary` (в отличие от `COUNT(salary)`, который не считает `NULL`).

Запрос без `GROUP BY` агрегирует все строки в одну итоговую строку. Это стандартный способ получить сводную статистику по столбцу.

Источник: [PostgreSQL §9.21 Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html).

---

### Вопрос 5. Что из перечисленного является примером первичного ключа в SQL?

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** Уникальный id посетителя сайта

#### Ответ от Claude

Первичный ключ (PRIMARY KEY) — столбец или набор столбцов, значения которых однозначно идентифицируют каждую строку таблицы. Требования: уникальность и отсутствие `NULL`. Уникальный идентификатор посетителя (`user_id`) классически используется в качестве первичного ключа: каждый посетитель имеет ровно один уникальный `id`, значения не повторяются и не могут быть `NULL`.

Источник: [PostgreSQL §5.4.2 Primary Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-PRIMARY-KEYS).

---

### Вопрос 6. Выберите вариант, в котором указаны ТОЛЬКО существующие в SQL типы соединения.

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `INNER JOIN`, `OUTER JOIN`, `LEFT OUTER JOIN`, `RIGHT OUTER JOIN`

#### Ответ от Claude

⚠️ Формулировка HH неточна: `OUTER JOIN` сам по себе не является самостоятельным типом — необходимо указывать `LEFT`/`RIGHT`/`FULL OUTER JOIN`.

Стандарт SQL определяет следующие типы соединений: `INNER JOIN` (только совпадающие строки), `LEFT [OUTER] JOIN`, `RIGHT [OUTER] JOIN` (все строки левой/правой таблицы плюс совпадающие из другой), `FULL [OUTER] JOIN` (все строки обеих таблиц), `CROSS JOIN` (декартово произведение). Слово `OUTER` в `LEFT`/`RIGHT`/`FULL` JOIN является необязательным и синонимичным. Синтаксис `OUTER JOIN` без уточнения (`LEFT`/`RIGHT`/`FULL`) сам по себе не является самостоятельным типом.

Источник: [PostgreSQL §7.2.1.1 Joined Tables](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOIN).

---

### Вопрос 7. Отсортируйте все покупки от последней к первой, а по каждому дню — от большей суммы продаж к меньшей в таблице `Sales`.

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `SELECT * FROM Sales ORDER BY date DESC, sale_amount DESC;`

#### Ответ от Claude

`ORDER BY date DESC` сортирует от последней даты к первой (убывание). Внутри одной даты `sale_amount DESC` сортирует от большей суммы к меньшей (убывание). Обратите внимание: это вопрос начального уровня, в котором сортировка по сумме задана **по убыванию** (`DESC`) — в отличие от аналогичного вопроса среднего уровня (Intermediate Q4), где та же сортировка задана по возрастанию (`ASC`).

Источник: [PostgreSQL §7.5 Sorting Rows (ORDER BY)](https://www.postgresql.org/docs/current/queries-order.html).

---

### Вопрос 8. Какое утверждение верно о разнице между `WHERE` и `HAVING`?

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `WHERE` сначала выбирает строки, затем группирует их и вычисляет агрегатные функции, а `HAVING` — сначала группирует строки, вычисляет агрегатные функции и только потом выбирает строки

#### Ответ от Claude

Порядок логической обработки SQL-запроса: `FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`. Таким образом:

- `WHERE` фильтрует **строки** до группировки; агрегатные функции (`SUM`, `COUNT` и т.д.) в нём недоступны.
- `HAVING` фильтрует **группы** после группировки и вычисления агрегатов; в нём можно использовать агрегатные функции.

Источник: [PostgreSQL §7.2.4 HAVING Clauses](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP).

---

### Вопрос 9. Найдите регионы со средним рейтингом городов выше 3,0 в таблице `Cities`.

**Категория:** SQL (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** `SELECT region_id, AVG(rating) FROM Cities GROUP BY region_id HAVING AVG(rating) > 3.0;`

#### Ответ от Claude

В оригинальном источнике ответ записан с опечаткой: `GROUP BY region_d` вместо `GROUP BY region_id` — пропущена буква `i`. Это OCR-артефакт. Правильный запрос: `SELECT region_id, AVG(rating) FROM Cities GROUP BY region_id HAVING AVG(rating) > 3.0;`. `GROUP BY region_id` группирует города по регионам, `AVG(rating)` вычисляет средний рейтинг в каждой группе, `HAVING AVG(rating) > 3.0` оставляет только регионы со средним рейтингом выше 3.0.

Источник: [PostgreSQL §7.2.4 HAVING Clauses](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP).

---

### Вопрос 10. Что вы получите, запустив следующий код?

**Категория:** SQL (HH) · **Уровень:** Basic

```sql
SELECT * FROM Food ORDER BY price DESC LIMIT 10;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/basic.md)

**Правильный ответ:** Первые 10 записей из таблицы `Food`, отсортированных по столбцу `price` в порядке убывания

#### Ответ от Claude

`ORDER BY price DESC` сортирует все строки таблицы `Food` от наибольшей цены к наименьшей. `LIMIT 10` возвращает только первые 10 строк из этого отсортированного набора — то есть 10 самых дорогих позиций. `LIMIT` обрабатывается после `ORDER BY`, поэтому возвращаются именно строки с наибольшим `price`.

Источник: [PostgreSQL §7.6 LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html).

---
