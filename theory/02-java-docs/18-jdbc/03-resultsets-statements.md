# Урок 3. Result Set, подготовленные операторы, транзакции

**Трейл:** JDBC Database Access · **Оригинал:** [JDBC Basics](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html)
**Связанные области:** [[15-databases-sql]] · **Вопросы:** databases-sql

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> *Retrieving and Modifying Values from Result Sets*, *Using Prepared Statements*,
> *Using Transactions*, *Using Stored Procedures* и *Using Large Objects*.
> Все примеры кода и SQL сохранены как в оригинале; комментарии переведены на русский.

Этот урок охватывает основные приёмы работы с результатами запросов и операторами JDBC:
чтение и изменение строк из набора результатов (result set), параметризованные запросы
через подготовленные операторы (prepared statement), управление транзакциями, вызов
хранимых процедур (stored procedure) и работу с большими объектами (BLOB/CLOB).

## Чтение и изменение значений из набора результатов (Result Set)

### Интерфейс ResultSet

Объект `ResultSet` представляет собой таблицу данных — результат выполнения SQL-запроса.
Он поддерживает **курсор** (cursor), указывающий на текущую строку данных. Изначально
курсор расположен перед первой строкой. Поведение объекта `ResultSet` определяется тремя
характеристиками: типом (type), параллелизмом/изменяемостью (concurrency) и сохраняемостью
курсора (cursor holdability). Эти характеристики задаются при создании объекта `Statement`,
который порождает данный `ResultSet`.

### Типы ResultSet (ResultSet Types)

Тип объекта `ResultSet` определяет уровень функциональности по двум направлениям:
можно ли перемещать курсор (прокручиваемость) и видит ли набор результатов изменения,
сделанные в источнике данных параллельно.

| Тип | Описание |
|---|---|
| `TYPE_FORWARD_ONLY` | Набор результатов нельзя прокручивать; его курсор движется только вперёд — от позиции перед первой строкой до позиции после последней. Какие строки попадают в набор, зависит от того, как СУБД формирует результаты: он содержит строки, удовлетворяющие запросу либо на момент выполнения запроса, либо по мере извлечения строк. |
| `TYPE_SCROLL_INSENSITIVE` | Набор результатов можно прокручивать; его курсор может двигаться как вперёд, так и назад относительно текущей позиции, а также переходить на абсолютную позицию. Набор **нечувствителен** к изменениям, внесённым в источник данных, пока он остаётся открытым. Содержит строки, удовлетворяющие запросу на момент его выполнения либо по мере извлечения строк. |
| `TYPE_SCROLL_SENSITIVE` | Набор результатов можно прокручивать; его курсор может двигаться как вперёд, так и назад относительно текущей позиции, а также переходить на абсолютную позицию. Набор **отражает** изменения, внесённые в источник данных, пока остаётся открытым. |

По умолчанию используется тип `TYPE_FORWARD_ONLY`.

### Параллелизм/изменяемость ResultSet (ResultSet Concurrency)

Параллелизм объекта `ResultSet` определяет, какие уровни обновления он поддерживает.

| Уровень | Описание |
|---|---|
| `CONCUR_READ_ONLY` | Объект `ResultSet` нельзя обновлять через интерфейс `ResultSet`. |
| `CONCUR_UPDATABLE` | Объект `ResultSet` можно обновлять через интерфейс `ResultSet`. |

По умолчанию используется `CONCUR_READ_ONLY`.

### Сохраняемость курсора (Cursor Holdability)

Когда транзакция фиксируется (commit) или откатывается (rollback), связанные с ней объекты
`ResultSet` могут быть закрыты или оставлены открытыми. Это поведение задаётся
константами **сохраняемости курсора** (cursor holdability):

- `HOLD_CURSORS_OVER_COMMIT` — объекты `ResultSet` остаются открытыми после фиксации
  транзакции;
- `CLOSE_CURSORS_AT_COMMIT` — объекты `ResultSet` закрываются при фиксации транзакции.
  Это может повысить производительность приложения.

Значение по умолчанию зависит от СУБД.

### Чтение значений столбцов из строк

Интерфейс `ResultSet` объявляет **методы-геттеры** (getter), например `getBoolean`,
`getLong` и т. п., для чтения значений из текущей строки. Значение извлекается либо по
**индексу столбца** (нумерация с 1), либо по **имени столбца**. Как правило, обращение по
индексу эффективнее.

Метод `CoffeesTable.viewTable` ниже читает каждый столбец по его имени:

```java
public static void viewTable(Connection con) throws SQLException {
  String query = "select COF_NAME, SUP_ID, PRICE, SALES, TOTAL from COFFEES";
  try (Statement stmt = con.createStatement()) {
    ResultSet rs = stmt.executeQuery(query);
    while (rs.next()) {
      String coffeeName = rs.getString("COF_NAME");
      int supplierID = rs.getInt("SUP_ID");
      float price = rs.getFloat("PRICE");
      int sales = rs.getInt("SALES");
      int total = rs.getInt("TOTAL");
      System.out.println(coffeeName + ", " + supplierID + ", " + price +
                         ", " + sales + ", " + total);
    }
  } catch (SQLException e) {
    JDBCTutorialUtilities.printSQLException(e);
  }
}
```

То же самое можно сделать через индексы столбцов вместо их имён:

```java
public static void alternateViewTable(Connection con) throws SQLException {
  String query = "select COF_NAME, SUP_ID, PRICE, SALES, TOTAL from COFFEES";
  try (Statement stmt = con.createStatement()) {
    ResultSet rs = stmt.executeQuery(query);
    while (rs.next()) {
      String coffeeName = rs.getString(1);
      int supplierID = rs.getInt(2);
      float price = rs.getFloat(3);
      int sales = rs.getInt(4);
      int total = rs.getInt(5);
      System.out.println(coffeeName + ", " + supplierID + ", " + price +
                         ", " + sales + ", " + total);
    }
  } catch (SQLException e) {
    JDBCTutorialUtilities.printSQLException(e);
  }
}
```

### Курсоры (Cursors)

Цикл `while (rs.next())` повторяется, пока курсор перемещается по всем строкам набора.
Поскольку тип по умолчанию — `TYPE_FORWARD_ONLY`, для прокручиваемого набора курсор можно
двигать и в других направлениях. Основные методы перемещения курсора:

| Метод | Описание |
|---|---|
| `next` | Перемещает курсор вперёд на одну строку. Возвращает `true`, если курсор теперь стоит на строке, и `false`, если он оказался после последней строки. |
| `previous` | Перемещает курсор назад на одну строку. Возвращает `true`, если курсор теперь стоит на строке, и `false`, если он оказался перед первой строкой. |
| `first` | Перемещает курсор на первую строку набора `ResultSet`. Возвращает `true`, если курсор стоит на первой строке, и `false`, если набор не содержит строк. |
| `last` | Перемещает курсор на последнюю строку набора. Возвращает `true`, если курсор стоит на последней строке, и `false`, если набор не содержит строк. |
| `beforeFirst` | Ставит курсор перед первой строкой набора. Если набор не содержит строк, метод не имеет эффекта. |
| `afterLast` | Ставит курсор после последней строки набора. Если набор не содержит строк, метод не имеет эффекта. |
| `relative(int rows)` | Перемещает курсор относительно его текущей позиции. |
| `absolute(int row)` | Ставит курсор на строку, указанную параметром `row`. |

Чтобы создать объект `ResultSet`, поддерживающий прокрутку и/или обновление, нужно при
создании `Statement` передать соответствующие константы типа и параллелизма.

### Обновление строк в объектах ResultSet

Чтобы изменять данные через сам `ResultSet`, его необходимо создать с типом
`TYPE_SCROLL_SENSITIVE` (или `TYPE_SCROLL_INSENSITIVE`) и параллелизмом `CONCUR_UPDATABLE`.
Изменения вносятся **методами-апдейтерами** (updater), например `updateFloat`,
`updateString` и т. п., после чего вызывается `updateRow`, чтобы зафиксировать их в базе.

Метод `CoffeesTable.modifyPrices` умножает цену каждого сорта кофе на заданный коэффициент:

```java
public void modifyPrices(float percentage) throws SQLException {
  try (Statement stmt =
    con.createStatement(ResultSet.TYPE_SCROLL_SENSITIVE, ResultSet.CONCUR_UPDATABLE)) {
    ResultSet uprs = stmt.executeQuery("SELECT * FROM COFFEES");
    while (uprs.next()) {
      float f = uprs.getFloat("PRICE");
      uprs.updateFloat("PRICE", f * percentage);
      uprs.updateRow();
    }
  } catch (SQLException e) {
    JDBCTutorialUtilities.printSQLException(e);
  }
}
```

### Использование объектов Statement для пакетных обновлений (Batch Updates)

**Пакетное обновление** (batch update) — это набор операторов, отправляемых на выполнение
СУБД как единая группа. Передача нескольких операторов за один раз бывает эффективнее, чем
по одному. Методы `Statement`, `PreparedStatement` и `CallableStatement` — `addBatch` и
`executeBatch` — добавляют команды в пакет и выполняют его целиком.

Перед началом пакета рекомендуется отключить режим автофиксации (auto-commit), чтобы при
ошибке можно было откатить все операторы пакета. Метод `executeBatch` возвращает массив
`int` — количество затронутых строк по каждой команде. При сбое выбрасывается
`BatchUpdateException`.

```java
public void batchUpdate() throws SQLException {
  con.setAutoCommit(false);
  try (Statement stmt = con.createStatement()) {

    stmt.addBatch("INSERT INTO COFFEES " +
                  "VALUES('Amaretto', 49, 9.99, 0, 0)");
    stmt.addBatch("INSERT INTO COFFEES " +
                  "VALUES('Hazelnut', 49, 9.99, 0, 0)");
    stmt.addBatch("INSERT INTO COFFEES " +
                  "VALUES('Amaretto_decaf', 49, 10.99, 0, 0)");
    stmt.addBatch("INSERT INTO COFFEES " +
                  "VALUES('Hazelnut_decaf', 49, 10.99, 0, 0)");

    int[] updateCounts = stmt.executeBatch();
    con.commit();
  } catch (BatchUpdateException b) {
    JDBCTutorialUtilities.printBatchUpdateException(b);
  } catch (SQLException ex) {
    JDBCTutorialUtilities.printSQLException(ex);
  } finally {
    con.setAutoCommit(true);
  }
}
```

Аналогичный пакет можно собрать из параметризованных вставок через `PreparedStatement`:

```java
con.setAutoCommit(false);
PreparedStatement pstmt = con.prepareStatement(
                            "INSERT INTO COFFEES VALUES( " +
                            "?, ?, ?, ?, ?)");
pstmt.setString(1, "Amaretto");
pstmt.setInt(2, 49);
pstmt.setFloat(3, 9.99);
pstmt.setInt(4, 0);
pstmt.setInt(5, 0);
pstmt.addBatch();

pstmt.setString(1, "Hazelnut");
pstmt.setInt(2, 49);
pstmt.setFloat(3, 9.99);
pstmt.setInt(4, 0);
pstmt.setInt(5, 0);
pstmt.addBatch();

int[] updateCounts = pstmt.executeBatch();
con.commit();
con.setAutoCommit(true);
```

### Вставка строк в объекты ResultSet

В обновляемый `ResultSet` можно вставить новую строку. Для этого курсор переводится в
специальную **строку вставки** (insert row) методом `moveToInsertRow`, затем апдейтерами
задаются значения столбцов, после чего вызывается `insertRow`:

```java
public void insertRow(String coffeeName, int supplierID, float price,
                      int sales, int total) throws SQLException {

  try (Statement stmt =
        con.createStatement(ResultSet.TYPE_SCROLL_SENSITIVE, ResultSet.CONCUR_UPDATABLE))
  {
    ResultSet uprs = stmt.executeQuery("SELECT * FROM COFFEES");
    uprs.moveToInsertRow();
    uprs.updateString("COF_NAME", coffeeName);
    uprs.updateInt("SUP_ID", supplierID);
    uprs.updateFloat("PRICE", price);
    uprs.updateInt("SALES", sales);
    uprs.updateInt("TOTAL", total);

    uprs.insertRow();
    uprs.beforeFirst();

  } catch (SQLException e) {
    JDBCTutorialUtilities.printSQLException(e);
  }
}
```

## Использование подготовленных операторов (Prepared Statements)

### Обзор подготовленных операторов

Иногда удобнее использовать объект `PreparedStatement` вместо `Statement`. Его главные
преимущества:

- **Производительность.** Если один и тот же или похожий SQL-оператор выполняется
  многократно, `PreparedStatement` обычно работает быстрее: при создании объекта указанный
  SQL отправляется в СУБД и заранее компилируется.
- **Параметризация.** В тексте оператора можно использовать заполнители `?` — параметры,
  значения которых подставляются перед каждым выполнением. Это также помогает защититься от
  внедрения SQL-кода (SQL injection), так как клиентские данные трактуются как значения
  параметров, а не как часть SQL.

### Создание объекта PreparedStatement

Заполнители `?` обозначают позиции параметров:

```java
String updateString =
  "update COFFEES " + "set SALES = ? where COF_NAME = ?";
// ...
PreparedStatement updateSales = con.prepareStatement(updateString);
```

### Подстановка значений параметров

Перед выполнением каждому заполнителю `?` присваивается значение **методом-сеттером**
(setter), определённым в классе `PreparedStatement`. Первый аргумент сеттера — позиция
заполнителя (нумерация с 1), второй — значение:

```java
updateSales.setInt(1, e.getValue().intValue());
updateSales.setString(2, e.getKey());
```

Параметры сохраняют свои значения между выполнениями, пока их не переустановят или пока не
вызовут `clearParameters`. Поэтому при повторном выполнении достаточно изменить только те
параметры, которые отличаются:

```java
// меняет столбец SALES строки French Roast на 100
updateSales.setInt(1, 100);
updateSales.setString(2, "French_Roast");
updateSales.executeUpdate();

// меняет столбец SALES строки Espresso на 100
// (первый параметр остался равным 100, а второй переустановлен на "Espresso")
updateSales.setString(2, "Espresso");
updateSales.executeUpdate();
```

### Использование циклов для установки значений

Сеттеры и выполнение оператора часто удобно вызывать в цикле. Метод
`updateCoffeeSales` обновляет столбцы `SALES` и `TOTAL` таблицы `COFFEES` для каждой записи
из словаря недельных продаж:

```java
public void updateCoffeeSales(HashMap<String, Integer> salesForWeek) throws SQLException {
    String updateString =
      "update COFFEES set SALES = ? where COF_NAME = ?";
    String updateStatement =
      "update COFFEES set TOTAL = TOTAL + ? where COF_NAME = ?";

    try (PreparedStatement updateSales = con.prepareStatement(updateString);
         PreparedStatement updateTotal = con.prepareStatement(updateStatement))

    {
      con.setAutoCommit(false);
      for (Map.Entry<String, Integer> e : salesForWeek.entrySet()) {
        updateSales.setInt(1, e.getValue().intValue());
        updateSales.setString(2, e.getKey());
        updateSales.executeUpdate();

        updateTotal.setInt(1, e.getValue().intValue());
        updateTotal.setString(2, e.getKey());
        updateTotal.executeUpdate();
        con.commit();
      }
    } catch (SQLException e) {
      JDBCTutorialUtilities.printSQLException(e);
      if (con != null) {
        try {
          System.err.print("Transaction is being rolled back");
          con.rollback();
        } catch (SQLException excep) {
          JDBCTutorialUtilities.printSQLException(excep);
        }
      }
    }
  }
```

### Выполнение объектов PreparedStatement

Как и у `Statement`, у `PreparedStatement` есть три метода выполнения:

- `executeQuery` — если запрос возвращает ровно один `ResultSet` (например, `SELECT`);
- `executeUpdate` — если оператор не возвращает `ResultSet` (например, `UPDATE`, `INSERT`,
  `DELETE`, а также DDL-операторы);
- `execute` — если запрос может вернуть более одного объекта `ResultSet`.

У `PreparedStatement` эти методы вызываются без аргументов, поскольку SQL уже задан при
создании объекта.

### Возвращаемые значения метода executeUpdate

Метод `executeUpdate` возвращает значение типа `int` — количество обновлённых строк
таблицы:

```java
updateSales.setInt(1, 50);
updateSales.setString(2, "Espresso");
int n = updateSales.executeUpdate();
// n = 1, потому что изменилась одна строка
```

Для DDL-операторов (например, создания таблицы) `executeUpdate` возвращает `0`:

```java
// n = 0
int n = executeUpdate(createTableCoffees);
```

То есть значение `0` означает одно из двух: либо оператор обновления не затронул ни одной
строки, либо это был DDL-оператор.

## Использование транзакций (Transactions)

**Транзакция** (transaction) — это один или несколько операторов, выполняемых, завершаемых
(commit) или отменяемых (rollback) как единое целое: либо выполняются все операторы, либо
ни один. Транзакции гарантируют целостность и согласованность данных.

### Отключение режима автофиксации (Auto-Commit)

Когда соединение создаётся, оно по умолчанию работает в режиме **автофиксации**
(auto-commit): каждый отдельный SQL-оператор трактуется как самостоятельная транзакция и
автоматически фиксируется сразу после завершения. Чтобы сгруппировать несколько операторов
в одну транзакцию, режим автофиксации отключают:

```java
con.setAutoCommit(false);
```

### Фиксация транзакций (Committing Transactions)

После отключения автофиксации операторы не фиксируются, пока явно не вызван метод `commit`.
Все операторы, выполненные после предыдущей фиксации, фиксируются вместе как одна единица.
Пример `updateCoffeeSales` (см. выше) демонстрирует группировку двух обновлений в одну
транзакцию: автофиксация отключается, выполняются оба `executeUpdate`, и только потом
вызывается `con.commit()`.

### Уровни изоляции транзакций (Transaction Isolation Levels)

Если СУБД поддерживает обработку транзакций, она управляет тем, как параллельные транзакции
видят данные друг друга. **Уровень изоляции** (isolation level) определяет, какие из
аномалий допускаются:

- **«грязное» чтение** (dirty read) — чтение незафиксированных изменений другой транзакции;
- **неповторяющееся чтение** (non-repeatable read) — повторное чтение той же строки даёт
  другое значение, потому что другая транзакция изменила и зафиксировала её;
- **фантомное чтение** (phantom read) — повторный запрос возвращает дополнительные строки,
  добавленные другой транзакцией.

| Уровень изоляции | Транзакции | «Грязное» чтение | Неповторяющееся чтение | Фантомное чтение |
|---|---|---|---|---|
| `TRANSACTION_NONE` | Не поддерживаются | Неприменимо | Неприменимо | Неприменимо |
| `TRANSACTION_READ_UNCOMMITTED` | Поддерживаются | Допускается | Допускается | Допускается |
| `TRANSACTION_READ_COMMITTED` | Поддерживаются | Предотвращается | Допускается | Допускается |
| `TRANSACTION_REPEATABLE_READ` | Поддерживаются | Предотвращается | Предотвращается | Допускается |
| `TRANSACTION_SERIALIZABLE` | Поддерживаются | Предотвращается | Предотвращается | Предотвращается |

Уровень изоляции задаётся методом `Connection.setTransactionIsolation`. Если попытаться
установить уровень, не поддерживаемый драйвером или СУБД, поведение определяется драйвером:
он может выбрать ближайший подходящий уровень или выбросить `SQLException`.

### Установка и откат к точкам сохранения (Savepoints)

Метод `Connection.setSavepoint` устанавливает **точку сохранения** (savepoint) внутри
текущей транзакции и возвращает объект `Savepoint`. Метод `Connection.rollback(Savepoint)`
отменяет все изменения, сделанные после установки этой точки. Метод
`modifyPricesByPercentage` повышает цену сорта кофе, но откатывается к точке сохранения,
если новая цена превышает заданный максимум:

```java
public void modifyPricesByPercentage(
    String coffeeName,
    float priceModifier,
    float maximumPrice) throws SQLException {
    con.setAutoCommit(false);
    ResultSet rs = null;
    String priceQuery = "SELECT COF_NAME, PRICE FROM COFFEES " +
                        "WHERE COF_NAME = ?";
    String updateQuery = "UPDATE COFFEES SET PRICE = ? " +
                         "WHERE COF_NAME = ?";
    try (PreparedStatement getPrice = con.prepareStatement(priceQuery, ResultSet.TYPE_SCROLL_INSENSITIVE, ResultSet.CONCUR_READ_ONLY);
         PreparedStatement updatePrice = con.prepareStatement(updateQuery))
    {
      Savepoint save1 = con.setSavepoint();
      getPrice.setString(1, coffeeName);
      if (!getPrice.execute()) {
        System.out.println("Could not find entry for coffee named " + coffeeName);
      } else {
        rs = getPrice.getResultSet();
        rs.first();
        float oldPrice = rs.getFloat("PRICE");
        float newPrice = oldPrice + (oldPrice * priceModifier);
        System.out.printf("Old price of %s is $%.2f%n", coffeeName, oldPrice);
        System.out.printf("New price of %s is $%.2f%n", coffeeName, newPrice);
        System.out.println("Performing update...");
        updatePrice.setFloat(1, newPrice);
        updatePrice.setString(2, coffeeName);
        updatePrice.executeUpdate();
        System.out.println("\nCOFFEES table after update:");
        CoffeesTable.viewTable(con);
        if (newPrice > maximumPrice) {
          System.out.printf("The new price, $%.2f, is greater " +
                            "than the maximum price, $%.2f. " +
                            "Rolling back the transaction...%n",
                            newPrice, maximumPrice);
          con.rollback(save1);
          System.out.println("\nCOFFEES table after rollback:");
          CoffeesTable.viewTable(con);
        }
        con.commit();
      }
    } catch (SQLException e) {
      JDBCTutorialUtilities.printSQLException(e);
    } finally {
      con.setAutoCommit(true);
    }
  }
```

### Освобождение точек сохранения (Releasing Savepoints)

Метод `Connection.releaseSavepoint` принимает объект `Savepoint` и удаляет его из текущей
транзакции. После удаления точку сохранения нельзя использовать в `rollback` — иначе будет
выброшено `SQLException`. Все точки сохранения, установленные в транзакции, автоматически
освобождаются и становятся недействительными при её фиксации или полном откате.

### Когда вызывать метод rollback

Если при выполнении транзакции возникает `SQLException`, метод `rollback` следует вызвать,
чтобы прервать транзакцию и вернуть базу в состояние, бывшее до её начала. Поэтому в блоках
`catch`, обрабатывающих `SQLException` внутри транзакции, обычно вызывают `con.rollback()`,
чтобы не использовать потенциально некорректные данные.

## Использование хранимых процедур (Stored Procedures)

**Хранимая процедура** (stored procedure) — это группа SQL-операторов, образующих логическую
единицу и выполняющих определённую задачу. Процедуры применяются, чтобы инкапсулировать
набор операций или запросов, выполняемых на сервере базы данных.

### Режимы параметров (Parameter Modes)

Способ передачи значений в процедуру и обратно задаётся **режимом параметра** (parameter
mode). Есть три режима:

| Режим | Описание |
|---|---|
| `IN` | Передаёт значение в процедуру. Формальный параметр ведёт себя как константа, ему нельзя присвоить значение. Фактический параметр может быть константой, инициализированной переменной, литералом или выражением. Указывать в определении процедуры не обязательно; если режим опущен — он считается `IN` (используется по умолчанию). |
| `OUT` | Возвращает значение вызывающей стороне. Формальный параметр ведёт себя как неинициализированная переменная; его нельзя использовать в выражении, ему нужно присвоить значение. Фактический параметр должен быть переменной. Режим указывать обязательно. |
| `INOUT` | И передаёт начальное значение в процедуру, и возвращает обновлённое значение вызывающей стороне. Формальный параметр ведёт себя как инициализированная переменная, ему нужно присвоить значение. Фактический параметр должен быть переменной. Режим указывать обязательно. |

### Создание хранимых процедур в Java DB

В Java DB хранимая процедура — это обёртка над публичным статическим методом Java. Процедура
объявляется командой `CREATE PROCEDURE` с указанием стиля параметров (`PARAMETER STYLE JAVA`),
языка (`LANGUAGE JAVA`), числа динамических наборов результатов (`DYNAMIC RESULT SETS`) и
полного имени Java-метода (`EXTERNAL NAME`).

Процедура `SHOW_SUPPLIERS` (выводит поставщиков и их сорта кофе) возвращает один набор
результатов:

```sql
CREATE PROCEDURE SHOW_SUPPLIERS()
PARAMETER STYLE JAVA
LANGUAGE JAVA
DYNAMIC RESULT SETS 1
EXTERNAL NAME
'com.oracle.tutorial.jdbc.
StoredProcedureJavaDBSample.
showSuppliers'
```

Процедура `GET_SUPPLIER_OF_COFFEE` принимает имя кофе (`IN`) и возвращает имя поставщика
(`OUT`), наборов результатов не возвращает:

```sql
CREATE PROCEDURE GET_SUPPLIER_OF_COFFEE(
    IN coffeeName varchar(32),
    OUT supplierName
    varchar(40))
    PARAMETER STYLE JAVA
    LANGUAGE JAVA
    DYNAMIC RESULT SETS 0
    EXTERNAL NAME 'com.oracle.tutorial.jdbc.
        StoredProcedureJavaDBSample.
        getSupplierOfCoffee'
```

Процедура `RAISE_PRICE` имеет параметр `INOUT` (`newPrice`), который и принимает, и
возвращает значение:

```sql
CREATE PROCEDURE RAISE_PRICE(
    IN coffeeName varchar(32),
    IN maximumPercentage float,
    INOUT newPrice float)
    PARAMETER STYLE JAVA
    LANGUAGE JAVA
    DYNAMIC RESULT SETS 0
    EXTERNAL NAME 'com.oracle.tutorial.jdbc.
        StoredProcedureJavaDBSample.raisePrice'
```

В реализующем Java-методе соединение получают через URL `jdbc:default:connection`. Объекты
`Statement`, созданные внутри метода, закрывать не следует; набор результатов присваивается
элементу массива `ResultSet[]`, переданного методу. Java-класс упаковывается в JAR-файл и
регистрируется в базе процедурой `sqlj.install_jar`.

### Создание хранимых процедур в MySQL

В MySQL хранимые процедуры пишутся на самом SQL; тело процедуры заключается в блок
`BEGIN ... END`. При определении процедуры обычно меняют разделитель операторов (delimiter).
Значения параметрам `OUT` присваиваются через `SELECT ... INTO`.

`SHOW_SUPPLIERS` (MySQL):

```sql
SELECT 'Creating procedure SHOW_SUPPLIERS' AS ' '|
create procedure SHOW_SUPPLIERS()
    begin
        select SUPPLIERS.SUP_NAME,
        COFFEES.COF_NAME
        from SUPPLIERS, COFFEES
        where SUPPLIERS.SUP_ID = COFFEES.SUP_ID
        order by SUP_NAME;
    end|
```

`GET_SUPPLIER_OF_COFFEE` (MySQL):

```sql
create procedure GET_SUPPLIER_OF_COFFEE(IN coffeeName varchar(32), OUT supplierName varchar(40))
  begin
    select SUPPLIERS.SUP_NAME into supplierName
      from SUPPLIERS, COFFEES
      where SUPPLIERS.SUP_ID = COFFEES.SUP_ID
      and coffeeName = COFFEES.COF_NAME;
    select supplierName;
  end
```

`RAISE_PRICE` (MySQL):

```sql
create procedure RAISE_PRICE(IN coffeeName varchar(32), IN maximumPercentage float, INOUT newPrice numeric(10,2))
  begin
    main: BEGIN
      declare maximumNewPrice numeric(10,2);
      declare oldPrice numeric(10,2);
      select COFFEES.PRICE into oldPrice
        from COFFEES
        where COFFEES.COF_NAME = coffeeName;
      set maximumNewPrice = oldPrice * (1 + maximumPercentage);
      if (newPrice > maximumNewPrice)
        then set newPrice = maximumNewPrice;
      end if;
      if (newPrice <= oldPrice)
        then set newPrice = oldPrice;
        leave main;
      end if;
      update COFFEES
        set COFFEES.PRICE = newPrice
        where COFFEES.COF_NAME = coffeeName;
      select newPrice;
    END main;
  end
```

### Вызов хранимых процедур из JDBC

Для вызова хранимой процедуры используется объект `CallableStatement`, создаваемый методом
`Connection.prepareCall`. SQL записывается в **escape-синтаксисе** вида `{call ИМЯ(?, ?)}`.
Этот код одинаков для Java DB и MySQL.

Процедура без параметров, возвращающая набор результатов, вызывается через `executeQuery`:

```java
cs = this.con.prepareCall("{call SHOW_SUPPLIERS()}");
ResultSet rs = cs.executeQuery();

while (rs.next()) {
    String supplier = rs.getString("SUP_NAME");
    String coffee = rs.getString("COF_NAME");
    System.out.println(supplier + ": " + coffee);
}
```

Для процедуры с `IN`- и `OUT`-параметрами входное значение задаётся сеттером, а выходной
параметр предварительно регистрируется методом `registerOutParameter` с указанием
SQL-типа; после выполнения его значение читается геттером:

```java
cs = this.con.prepareCall("{call GET_SUPPLIER_OF_COFFEE(?, ?)}");
cs.setString(1, coffeeNameArg);
cs.registerOutParameter(2, Types.VARCHAR);
cs.executeQuery();

String supplierName = cs.getString(2);
```

Для `INOUT`-параметра нужно и установить значение сеттером, и зарегистрировать его как
выходной:

```java
cs = this.con.prepareCall("{call RAISE_PRICE(?,?,?)}");
cs.setString(1, coffeeNameArg);
cs.setFloat(2, maximumPercentageArg);
cs.registerOutParameter(3, Types.NUMERIC);
cs.setFloat(3, newPriceArg);

cs.execute();
```

## Использование больших объектов (BLOB/CLOB)

Важная особенность Java-объектов `Blob`, `Clob` и `NClob` в том, что ими можно
манипулировать, не перенося все данные с сервера базы на клиентскую машину. Некоторые
реализации представляют экземпляр такого типа **локатором** (locator) — логическим
указателем на объект в базе данных. Поскольку SQL-объекты `BLOB`, `CLOB` или `NCLOB` могут
быть очень большими, использование локаторов способно значительно ускорить работу. Другие
реализации, наоборот, полностью материализуют большой объект на клиенте.

### Добавление большого объекта в базу данных

В примере ниже создаётся объект `Clob` методом `Connection.createClob`, в него пишется текст
из файла через `Writer`, полученный методом `setCharacterStream`, и затем объект
сохраняется в столбец через `PreparedStatement.setClob`:

```java
public void addRowToCoffeeDescriptions(String coffeeName,
                                       String fileName) throws SQLException {
  String sql = "INSERT INTO COFFEE_DESCRIPTIONS VALUES(?,?)";
  Clob myClob = this.con.createClob();
  try (PreparedStatement pstmt = this.con.prepareStatement(sql);
    Writer clobWriter = myClob.setCharacterStream(1);){
    String str = this.readFile(fileName, clobWriter);
    System.out.println("Wrote the following: " + clobWriter.toString());
    if (this.settings.dbms.equals("mysql")) {
      System.out.println("MySQL, setting String in Clob object with setString method");
      myClob.setString(1, str);
    }
    System.out.println("Length of Clob: " + myClob.length());
    pstmt.setString(1, coffeeName);
    pstmt.setClob(2, myClob);
    pstmt.executeUpdate();
  } catch (SQLException sqlex) {
    JDBCTutorialUtilities.printSQLException(sqlex);
  } catch (Exception ex) {
    System.out.println("Unexpected exception: " + ex.toString());
  }
}
```

### Чтение значений CLOB

`CLOB`-значение читается из набора результатов методом `ResultSet.getClob`. Часть текста
извлекается методом `Clob.getSubString(position, length)` (позиция — нумерация с 1):

```java
public String retrieveExcerpt(String coffeeName,
                              int numChar) throws SQLException {

  String description = null;
  Clob myClob = null;
  String sql = "select COF_DESC from COFFEE_DESCRIPTIONS where COF_NAME = ?";

  try (PreparedStatement pstmt = this.con.prepareStatement(sql)) {
    pstmt.setString(1, coffeeName);
    ResultSet rs = pstmt.executeQuery();
    if (rs.next()) {
      myClob = rs.getClob(1);
      System.out.println("Length of retrieved Clob: " + myClob.length());
    }
    description = myClob.getSubString(1, numChar);
  } catch (SQLException sqlex) {
    JDBCTutorialUtilities.printSQLException(sqlex);
  } catch (Exception ex) {
    System.out.println("Unexpected exception: " + ex.toString());
  }
  return description;
}
```

### Добавление и чтение объектов BLOB

Добавление и чтение SQL-объектов `BLOB` аналогично работе с `CLOB`. Чтобы записать в
`Blob`-объект двоичные данные, у него вызывают метод `Blob.setBinaryStream`, возвращающий
объект `OutputStream` для записи значения `BLOB`.

### Освобождение ресурсов, удерживаемых большими объектами

Java-объекты `Blob`, `Clob` и `NClob` остаются действительными как минимум на протяжении
транзакции, в которой они созданы. Чтобы не исчерпать ресурсы при длительных транзакциях,
приложение может освободить их методом `free`:

```java
Clob aClob = con.createClob();
int numWritten = aClob.setString(1, val);
aClob.free();
```

## Источник

- [Retrieving and Modifying Values from Result Sets](https://docs.oracle.com/javase/tutorial/jdbc/basics/retrieving.html) — официальное руководство Oracle.
- [Using Prepared Statements](https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html) — официальное руководство Oracle.
- [Using Transactions](https://docs.oracle.com/javase/tutorial/jdbc/basics/transactions.html) — официальное руководство Oracle.
- [Using Stored Procedures](https://docs.oracle.com/javase/tutorial/jdbc/basics/storedprocedures.html) — официальное руководство Oracle.
- [Using Large Objects](https://docs.oracle.com/javase/tutorial/jdbc/basics/blob.html) — официальное руководство Oracle.
- [JDBC Basics (индекс урока)](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html) — официальное руководство Oracle.
