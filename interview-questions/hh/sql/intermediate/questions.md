# SQL — Intermediate (HH)

### Вопрос 1. Получите список имён и фамилий сотрудников с зарплатой до 50 000 рублей из таблицы Employees.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Employees`: `employee_id` (Integer), `first_name` (String), `last_name` (String), `department` (String), `job_title` (String), `salary` (Integer).

**Правильный ответ:** `SELECT first_name, last_name FROM Employees WHERE salary < 50000;`

#### Ответ от Claude

Запрос выбирает только два столбца (`first_name`, `last_name`) и фильтрует строки условием `salary < 50000` (строго меньше). Условие «до 50 000 рублей» означает, что граница не включается, поэтому используется `<`, а не `<=`. Если бы формулировка была «не более 50 000», корректным был бы `<=`.

Источник: [SQL Standard — WHERE Clause (PostgreSQL docs §7.2.2)](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-WHERE).

---

### Вопрос 2. Переименуйте столбец `new_email` в `email` в существующей таблице `Clients`.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

**Правильный ответ:** `ALTER TABLE Clients RENAME COLUMN new_email TO email;`

#### Ответ от Claude

Команда `ALTER TABLE ... RENAME COLUMN` переименовывает столбец в уже существующей таблице. Синтаксис стандартизирован и поддерживается во всех основных СУБД (PostgreSQL, MySQL 8.0+, Oracle, SQL Server). В PostgreSQL операция выполняется с блокировкой уровня `ACCESS EXCLUSIVE` на таблицу, но не перестраивает данные — переименование мгновенно.

Источник: [PostgreSQL ALTER TABLE — RENAME COLUMN](https://www.postgresql.org/docs/current/sql-altertable.html).

---

### Вопрос 3. Каким будет результат выполнения следующего INSERT для таблицы `Cars`, если `car_id` — первичный ключ с автоинкрементом?

**Категория:** SQL (HH) · **Уровень:** Intermediate

```sql
INSERT INTO Cars (distributor_id, car_model) VALUES (5, 'BMW X5 M50d');
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Cars`: `car_id` (Integer, PK auto-increment), `distributor_id` (Integer), `car_model` (String), `number` (Integer).

Существующие записи:

| car_id | distributor_id | car_model             | number |
|--------|----------------|-----------------------|--------|
| 1      | 1              | BMW X5 M50d           | 10     |
| 2      | 2              | Mercedez-Benz C-Class | 7      |
| 3      | 3              | Lexus LX              | 7      |

**Правильный ответ:** Добавится новая запись `(4, 5, 'BMW X5 M50d', NULL)`

#### Ответ от Claude

`car_id` не указан в `INSERT` — значение генерируется автоматически; следующий идентификатор равен 4. `distributor_id = 5` и `car_model = 'BMW X5 M50d'` берутся из значений запроса. Столбец `number` не указан и не имеет DEFAULT, поэтому получает значение `NULL`. Итоговая строка: `(4, 5, 'BMW X5 M50d', NULL)`.

Источник: [PostgreSQL §6.1 Inserting Data](https://www.postgresql.org/docs/current/dml-insert.html); [§8.1.4 Serial Types / GENERATED ALWAYS AS IDENTITY](https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-SERIAL).

---

### Вопрос 4. Отсортируйте все покупки от последней к первой, а по каждому дню — от меньшей суммы продаж к большей в таблице `Sales`.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Sales`: `sale_id` (Integer), `employee_id` (Integer), `sale_title` (String), `date` (Date), `sale_amount` (Double).

**Правильный ответ:** `SELECT * FROM Sales ORDER BY date DESC, sale_amount ASC;`

#### Ответ от Claude

`ORDER BY date DESC` сортирует покупки от самой поздней к самой ранней (убывание по дате). Внутри каждой даты `sale_amount ASC` сортирует от меньшей к большей суммы — что соответствует формулировке задачи. При наличии нескольких ключей сортировки каждый следующий применяется только для строк с одинаковым предыдущим ключом.

Источник: [PostgreSQL §7.5 Sorting Rows (ORDER BY)](https://www.postgresql.org/docs/current/queries-order.html).

---

### Вопрос 5. Найдите модуль разницы между средней и максимальной заработной платой сотрудников в таблице `Employees`.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Employees`: `employee_id` (Integer), `first_name` (String), `last_name` (String), `department` (String), `job_title` (String), `salary` (Integer).

**Правильный ответ:** `SELECT ABS(AVG(salary) - MAX(salary)) FROM Employees;`

#### Ответ от Claude

`AVG(salary)` возвращает среднюю зарплату, `MAX(salary)` — максимальную. Разность всегда отрицательна или равна нулю (среднее ≤ максимума), поэтому `ABS(...)` возвращает модуль. Обе агрегатные функции применяются ко всем строкам таблицы (без `GROUP BY`).

Источники: [PostgreSQL §9.3 Mathematical Functions — ABS](https://www.postgresql.org/docs/current/functions-math.html); [§9.21 AVG, MAX](https://www.postgresql.org/docs/current/functions-aggregate.html).

---

### Вопрос 6. Найдите численность населения городов, оканчивающихся на `-burg`, по регионам в таблице `Cities`.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Cities`: `city_id` (Integer), `city_name` (String), `region_id` (Integer), `population` (Double), `rating` (Double).

**Правильный ответ:** `SELECT region_id, SUM(population) FROM Cities WHERE city_name LIKE '%burg' GROUP BY region_id;`

#### Ответ от Claude

`WHERE city_name LIKE '%burg'` фильтрует только города, название которых оканчивается на `burg` (шаблон `%` соответствует любому префиксу). `GROUP BY region_id` группирует строки по региону. `SUM(population)` суммирует население в каждой группе. Порядок важен: `WHERE` применяется **до** группировки, поэтому суммируются только отфильтрованные строки.

Источник: [PostgreSQL §9.7 Pattern Matching — LIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE); [§7.2.4 GROUP BY and HAVING](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP).

---

### Вопрос 7. Получите список сотрудников с названиями их отделов и полным именем в столбце `employees_list` из таблиц `Employees` и `Departments` (общий столбец — `dep_id`).

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Employees`: `emp_id` (Integer), `dep_id` (Integer), `first_name` (String), `second_name` (String), `job_title` (String).
Таблица `Departments`: `dep_id` (Integer), `dep_name` (String).

**Правильный ответ:** `SELECT dep_name, CONCAT(first_name, ' ', second_name) AS employees_list FROM Employees INNER JOIN Departments ON Employees.dep_id = Departments.dep_id;`

#### Ответ от Claude

`INNER JOIN ... ON Employees.dep_id = Departments.dep_id` объединяет строки, у которых совпадает `dep_id` в обеих таблицах (сотрудники без отдела и отделы без сотрудников не попадают в результат). `CONCAT(first_name, ' ', second_name)` собирает полное имя; псевдоним `AS employees_list` присваивает столбцу нужное название. В источнике для фамилии используется `second_name` (не `last_name` — следует взять из схемы задачи).

Источник: [PostgreSQL §2.6 Joins Between Tables](https://www.postgresql.org/docs/current/tutorial-join.html); [§9.4 String Functions — CONCAT](https://www.postgresql.org/docs/current/functions-string.html).

---

### Вопрос 8. Найдите имена сотрудников, зарплата которых больше средней зарплаты всех сотрудников в таблице `Employees`.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Employees`: `employee_id` (Integer), `first_name` (String), `last_name` (String), `department` (String), `job_title` (String), `salary` (Integer).

**Правильный ответ:** `SELECT first_name, last_name FROM Employees WHERE salary > (SELECT AVG(salary) FROM Employees);`

#### Ответ от Claude

Скалярный подзапрос `(SELECT AVG(salary) FROM Employees)` вычисляется один раз и возвращает среднюю зарплату по всей таблице. Основной запрос фильтрует строки, у которых `salary` строго превышает это значение. Самостоятельный подзапрос в `WHERE` — стандартный паттерн для сравнения строк с агрегатом по всей таблице (агрегат нельзя использовать напрямую в `WHERE`).

Источник: [PostgreSQL §9.23 Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html); [§7.2.2 The WHERE Clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-WHERE).

---

### Вопрос 9. Какая ошибка допущена в запросе создания или замены представления `PeopleView`?

**Категория:** SQL (HH) · **Уровень:** Intermediate

```sql
CREATE VIEW PeopleView OR REPLACE
AS SELECT Respondents.age, Respondents.city, Info.phone_number, Info.address
FROM Respondents, Info WHERE Respondents.respondent_id = Info.respondent_id;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

Таблица `Respondents`: `respondent_id` (Integer), `city` (String), `age` (Integer), `phone_number` (String), `know_languages` (Array).
Таблица `Info`: `info_id` (Integer), `respondent_id` (Integer), `phone_number` (String), `address` (String).

**Правильный ответ:** Вместо `CREATE VIEW PeopleView OR REPLACE` нужно написать `CREATE OR REPLACE VIEW PeopleView`

#### Ответ от Claude

Правильный синтаксис команды — `CREATE OR REPLACE VIEW имя AS ...`. Ключевые слова `OR REPLACE` должны стоять сразу после `CREATE`, перед `VIEW`. В коде задания они ошибочно помещены после имени представления (`CREATE VIEW PeopleView OR REPLACE`), что является синтаксической ошибкой.

Источник: [PostgreSQL CREATE VIEW](https://www.postgresql.org/docs/current/sql-createview.html).

---

### Вопрос 10. Индексацию какого столбца следует рассмотреть в первую очередь для повышения производительности запросов?

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

**Правильный ответ:** Столбец с большим количеством уникальных значений

#### Ответ от Claude

Индексы наиболее эффективны на столбцах с высокой кардинальностью (selectivity) — большим числом уникальных значений. При высокой кардинальности индекс позволяет быстро сузить выборку до небольшого числа строк. На столбцах с низкой кардинальностью (например, булев флаг или статус с 2–3 значениями) индекс часто не используется планировщиком: дешевле последовательное сканирование.

Источник: [PostgreSQL §11.1 Introduction to Indexes](https://www.postgresql.org/docs/current/indexes-intro.html); [§14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).

---

### Вопрос 11. Выберите ОШИБОЧНОЕ утверждение об обработке транзакций в SQL.

**Категория:** SQL (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

**Правильный ответ:** При исполнении транзакции можно выбрать, какие операции внутри неё должны быть выполнены, а какие — нет

#### Ответ от Claude

Это утверждение действительно является ошибочным: транзакция — неделимая единица работы. Принцип атомарности (свойство A из ACID) означает, что транзакция либо выполняется полностью, либо откатывается целиком. Нельзя зафиксировать «часть» операций внутри одной транзакции.

Замечание: `SAVEPOINT` позволяет откатиться к промежуточной точке внутри транзакции, но при этом всё равно нужно либо зафиксировать (`COMMIT`) оставшуюся часть, либо откатить всё (`ROLLBACK`). Частичная фиксация транзакции (commit части операций) не предусмотрена стандартом SQL.

Источник: [PostgreSQL §13.1 Introduction to Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html); [§13.3.4 SAVEPOINT](https://www.postgresql.org/docs/current/sql-savepoint.html).

---

### Вопрос 12. Какой фактор следует учитывать в первую очередь для повышения производительности запроса с несколькими объединениями?

**Категория:** SQL (HH) · **Уровень:** Intermediate

```sql
SELECT * FROM table1
INNER JOIN table2 ON table2.id = table1.order_id
INNER JOIN table3 ON table3.id = table2.client_id;
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — sql/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/sql/intermediate.md)

**Правильный ответ:** Порядок соединения таблиц

#### Ответ от Claude

⚠️ Ответ HH вызывает сомнения. Итог квиза — 11 из 12; вероятно, именно этот вопрос содержит неверный ответ.

Согласно официальной документации PostgreSQL и общепринятой практике оптимизации, **наличие индексов на столбцах соединения** (`table1.order_id`, `table2.client_id`, `table2.id`, `table3.id`) является первостепенным фактором производительности при JOIN. Без индексов СУБД вынуждена выполнять полное сканирование таблиц на каждом шаге объединения.

Порядок соединения таблиц важен и действительно влияет на производительность, однако:
1. Современные оптимизаторы запросов (в том числе PostgreSQL) **самостоятельно** перебирают варианты порядка JOIN (join reordering) и выбирают оптимальный, если включён `join_collapse_limit > 1` (по умолчанию 8).
2. При отсутствии индексов никакой порядок JOIN не спасёт от полного сканирования.

Таким образом, правильный ответ — **наличие индексов на столбцах соединения**, а не порядок таблиц. Порядок соединения в подавляющем большинстве случаев подбирает оптимизатор автоматически.

Источник: [PostgreSQL §14.3 Controlling the Planner with Explicit JOIN Clauses](https://www.postgresql.org/docs/current/explicit-joins.html); [§14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html); [§11.3 Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html).

---
