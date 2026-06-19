# Урок 2. Основы JDBC: подключение и таблицы

**Трейл:** JDBC Database Access · **Оригинал:** [JDBC Basics](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html)
**Связанные области:** [[15-databases-sql]] · **Вопросы:** databases-sql

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> *Getting Started*, *Processing SQL Statements with JDBC*, *Establishing a Connection*,
> *Connecting with DataSource Objects*, *Handling SQLExceptions* и *Setting Up Tables*
> урока *JDBC Basics*.

В этом уроке вы изучите основы JDBC API.

## Обзор урока «Основы JDBC»

Урок Oracle охватывает следующие темы (в этом файле переведены первые шесть):

- **Getting Started** (с чего начать) — настройка базового окружения для разработки с базой
  данных, компиляция и запуск примеров из руководства.
- **Processing SQL Statements with JDBC** (обработка SQL-выражений) — шаги, необходимые для
  обработки любого SQL-выражения. Последующие страницы описывают эти шаги подробнее:
  - **Establishing a Connection** (установка соединения) — подключение к базе данных.
  - **Connecting with DataSource Objects** (подключение через объекты DataSource) — подключение
    к базе данных при помощи объектов `DataSource` — предпочтительного способа получить
    соединение с источником данных.
  - **Handling SQLExceptions** (обработка SQLException) — как обрабатывать исключения,
    вызванные ошибками базы данных.
  - **Setting Up Tables** (подготовка таблиц) — описание всех таблиц, которые используются в
    примерах руководства, и того, как создавать и наполнять их через JDBC API и SQL-скрипты.
  - **Retrieving and Modifying Values from Result Sets** — извлечение и изменение значений из
    наборов результатов.
  - **Using Prepared Statements** — более гибкий способ создания запросов к базе данных.
  - **Using Transactions** — управление тем, когда запрос фактически выполняется.
- **Using RowSet Objects** — объекты `RowSet`, хранящие табличные данные более гибким и удобным
  образом, чем наборы результатов (`JdbcRowSet`, `CachedRowSet`, `JoinRowSet`, `FilteredRowSet`,
  `WebRowSet`).
- **Using Advanced Data Types** — расширенные типы данных (большие объекты, `SQLXML`, `Array`,
  `DISTINCT`, структурированные объекты, пользовательские отображения типов, `Datalink`, `RowId`).
- **Using Stored Procedures** — создание и использование хранимых процедур.
- **Using JDBC with GUI API** — интеграция JDBC со Swing API.

> Примеры кода, поставляемые с этим руководством, создают базу данных небольшой кофейни
> «The Coffee Break», где кофейные зёрна продают на фунты, а готовый кофе — чашками.

## С чего начать (Getting Started)

Следующие шаги настраивают окружение для разработки с JDBC, в котором можно компилировать и
запускать примеры руководства:

1. Установить на компьютер последнюю версию Java SE SDK.
2. При необходимости установить систему управления базами данных (СУБД, *DBMS*).
3. Установить JDBC-драйвер от поставщика вашей базы данных.
4. Установить Apache Ant.
5. Установить Apache Xalan.
6. Скачать примеры кода.
7. Изменить файл `build.xml`.
8. Изменить файл свойств руководства (*properties file*).
9. Скомпилировать и упаковать примеры.
10. Создать базы данных, таблицы и наполнить таблицы данными.
11. Запустить примеры.

### Установка Java SE SDK

Установите на компьютер последнюю версию Java SE SDK. Убедитесь, что полный путь к каталогу
`bin` этого SDK добавлен в переменную окружения `PATH` — тогда компилятор Java и загрузчик
приложений можно будет запускать из любого каталога.

### Установка СУБД

Руководство протестировано на следующих СУБД:

- **Java DB.**

  > Примечание: Java DB больше не входит в недавние версии JDK. Java DB — это переименованная
  > Apache Derby. Чтобы использовать Java DB, скачайте последнюю версию из проекта The Apache
  > DB Project.

- **MySQL.**

Если вы используете другую СУБД, код примеров, возможно, придётся изменить.

### Установка JDBC-драйвера от поставщика базы данных

Если вы используете Java DB, JDBC-драйвер уже входит в её состав. Для MySQL установите последнюю
версию JDBC-драйвера — Connector/J. За драйвером для вашей СУБД обращайтесь к её поставщику.

Существует множество реализаций JDBC-драйверов. Их разделяют на следующие типы:

- **Тип 1.** Драйверы, реализующие JDBC API как отображение на другой API доступа к данным —
  например, ODBC (Open Database Connectivity). Драйверы этого типа обычно зависят от нативной
  библиотеки, что ограничивает их переносимость. Пример — мост JDBC-ODBC.

  > Примечание: мост JDBC-ODBC следует рассматривать как переходное решение. Oracle его не
  > поддерживает. Используйте его, только если ваша СУБД не предлагает чисто Java-драйвера JDBC.

- **Тип 2.** Драйверы, написанные частично на языке Java и частично в нативном коде. Они
  используют нативную клиентскую библиотеку, специфичную для источника данных. Из-за нативного
  кода переносимость ограничена. Пример — клиентский драйвер Oracle OCI (Oracle Call Interface).
- **Тип 3.** Драйверы с чистым Java-клиентом, общающиеся с промежуточным сервером (*middleware*)
  по протоколу, не зависящему от базы данных. Промежуточный сервер передаёт запросы клиента
  источнику данных.
- **Тип 4.** Чисто Java-драйверы, реализующие сетевой протокол конкретного источника данных.
  Клиент подключается к источнику данных напрямую.

Проверьте, какие типы драйверов поставляются с вашей СУБД. В Java DB входят два драйвера типа 4:
встраиваемый (*Embedded*) и сетевой клиентский (*Network Client*). MySQL Connector/J — драйвер
типа 4.

Установка JDBC-драйвера обычно состоит в копировании драйвера на компьютер и добавлении его
расположения в путь к классам (*class path*). Кроме того, многие драйверы (кроме типа 4) требуют
установки клиентского API. Иной особой настройки, как правило, не требуется.

### Установка Apache Ant

Эти шаги используют Apache Ant — инструмент на основе Java — для сборки, компиляции и запуска
примеров. Скачать его можно по адресу `https://ant.apache.org/`. Убедитесь, что исполняемый файл
Apache Ant добавлен в `PATH`, чтобы запускать его из любого каталога.

### Установка Apache Xalan

Пример `RSSFeedsTable.java` (описан в разделе *Using SQLXML Objects*) требует Apache Xalan, если
ваша СУБД — Java DB. Пример использует Apache Xalan-Java. Скачать его можно по адресу
`https://xml.apache.org/xalan-j/`.

### Загрузка примеров кода

Примеры кода `JDBCTutorial.zip` состоят из файлов:

- `properties` — `javadb-build-properties.xml`, `javadb-sample-properties.xml`,
  `mysql-build-properties.xml`, `mysql-sample-properties.xml`;
- `sql/javadb` и `sql/mysql` — `create-procedures.sql`, `create-tables.sql`, `drop-tables.sql`,
  `populate-tables.sql`;
- `src/com/oracle/tutorial/jdbc` — Java-классы примеров (`CoffeesTable.java`,
  `SuppliersTable.java`, `JDBCTutorialUtilities.java`, `JdbcRowSetSample.java` и др.);
- `txt/colombian-description.txt`;
- `xml/rss-coffee-industry-news.xml`, `xml/rss-the-coffee-break-blog.xml`;
- `build.xml`.

Создайте каталог для всех файлов примера (далее — `<каталог руководства JDBC>`) и распакуйте в
него содержимое `JDBCTutorial.zip`.

### Изменение файла build.xml

`build.xml` — это файл сборки, который Apache Ant использует для компиляции и выполнения примеров.
Файлы `properties/javadb-build-properties.xml` и `properties/mysql-build-properties.xml` содержат
дополнительные свойства Ant для Java DB и MySQL соответственно. Файлы
`properties/javadb-sample-properties.xml` и `properties/mysql-sample-properties.xml` содержат
свойства, требуемые самим примером.

В `build.xml` измените свойство `ANTPROPERTIES`, чтобы оно ссылалось на
`properties/javadb-build-properties.xml` или `properties/mysql-build-properties.xml` — в
зависимости от вашей СУБД. Например, для Java DB:

```xml
<property
  name="ANTPROPERTIES"
  value="properties/javadb-build-properties.xml"/>

  <import file="${ANTPROPERTIES}"/>
```

Аналогично для MySQL:

```xml
<property
  name="ANTPROPERTIES"
  value="properties/mysql-build-properties.xml"/>

  <import file="${ANTPROPERTIES}"/>
```

В файле свойств сборки (`javadb-build-properties.xml` или `mysql-build-properties.xml`) измените
следующие свойства:

| Свойство | Описание |
|----------|----------|
| `JAVAC` | Полный путь к компилятору Java (`javac`). |
| `JAVA` | Полный путь к исполняемому файлу среды выполнения Java (`java`). |
| `PROPERTIESFILE` | Имя файла свойств: `properties/javadb-sample-properties.xml` или `properties/mysql-sample-properties.xml`. |
| `MYSQLDRIVER` | Полный путь к драйверу MySQL. Для Connector/J это обычно `<каталог установки Connector/J>/mysql-connector-java-<версия>.jar`. |
| `JAVADBDRIVER` | Полный путь к драйверу Java DB. Обычно `<каталог установки Java DB>/lib/derby.jar`. |
| `XALANDIRECTORY` | Полный путь к каталогу с Apache Xalan. |
| `CLASSPATH` | Путь к классам, который использует руководство. *Менять не нужно.* |
| `XALAN` | Полный путь к файлу `xalan.jar`. |
| `DB.VENDOR` | Значение `derby` или `mysql` в зависимости от СУБД. Руководство использует его для построения URL подключения и выбора кода/SQL, специфичных для СУБД. |
| `DB.DRIVER` | Полностью квалифицированное имя класса JDBC-драйвера. Для Java DB — `org.apache.derby.jdbc.EmbeddedDriver`, для MySQL — `com.mysql.cj.jdbc.Driver`. |
| `DB.HOST` | Имя хоста компьютера с СУБД. |
| `DB.PORT` | Номер порта компьютера с СУБД. |
| `DB.SID` | Имя базы данных, которую создаёт и использует руководство. |
| `DB.URL.NEWDATABASE` | URL подключения к СУБД при создании новой базы данных. *Менять не нужно.* |
| `DB.URL` | URL подключения к СУБД. *Менять не нужно.* |
| `DB.USER` | Имя пользователя, имеющего право создавать базы данных в СУБД. |
| `DB.PASSWORD` | Пароль пользователя из `DB.USER`. |
| `DB.DELIMITER` | Символ-разделитель SQL-выражений. *Не менять* — это точка с запятой (`;`). |

### Изменение файла свойств руководства

Примеры используют значения из `properties/javadb-sample-properties.xml` или
`properties/mysql-sample-properties.xml` (в зависимости от СУБД) для подключения к СУБД и
инициализации баз данных и таблиц:

| Свойство | Описание |
|----------|----------|
| `dbms` | `derby` или `mysql` в зависимости от СУБД. |
| `jar_file` | Полный путь к JAR-файлу со всеми class-файлами руководства. |
| `driver` | Полностью квалифицированное имя класса драйвера (`org.apache.derby.jdbc.EmbeddedDriver` или `com.mysql.cj.jdbc.Driver`). |
| `database_name` | Имя базы данных, создаваемой и используемой руководством. |
| `user_name` | Имя пользователя с правом создавать базы данных. |
| `password` | Пароль пользователя из `user_name`. |
| `server_name` | Имя хоста компьютера с СУБД. |
| `port_number` | Номер порта компьютера с СУБД. |

> Примечание: для простоты демонстрации JDBC API пример не выполняет управление паролями так, как
> это обычно делается в развёрнутой системе. В производственной среде следуйте рекомендациям
> Oracle по управлению паролями и отключайте любые тестовые учётные записи. См. раздел *Securing
> Passwords in Application Design* в *Oracle Database Security Guide*.

### Компиляция и упаковка примеров

В командной строке перейдите в каталог `<каталог руководства JDBC>` и выполните команду, которая
компилирует примеры и упаковывает их в JAR-файл:

```
ant jar
```

### Создание баз данных и таблиц и их наполнение

Для MySQL создайте базу данных командой:

```
ant create-mysql-database
```

> Примечание: для Java DB соответствующей Ant-цели в `build.xml` нет. URL базы данных Java DB,
> используемый для установки соединения, включает опцию создания базы (если она ещё не
> существует). См. раздел *Establishing a Connection*.

Для Java DB или MySQL из того же каталога выполните команду, которая удаляет существующие таблицы,
пересоздаёт их и наполняет. Для Java DB она также создаёт базу данных, если её ещё нет:

```
ant setup
```

> Примечание: команду `ant setup` следует выполнять каждый раз перед запуском любого из
> Java-классов примера. Многие примеры рассчитывают на конкретные данные в таблицах.

### Запуск примеров

Каждая цель в `build.xml` соответствует Java-классу или SQL-скрипту примеров. Например, чтобы
запустить класс `CoffeesTable`, перейдите в `<каталог руководства JDBC>` и выполните:

```
ant runct
```

Среди других целей: `run` (`JDBCTutorialUtilities`), `runst` (`SuppliersTable`),
`runjrs` (`JdbcRowSetSample`), `runcrs` (`CachedRowSetSample`), `runjoin` (`JoinSample`),
`runfrs` (`FilteredRowSetSample`), `runwrs` (`WebRowSetSample`), `runclob` (`ClobSample`),
`runrss` (`RSSFeedsTable`), `rundl` (`DatalinkSample`),
`runspjavadb`/`runspmysql` (хранимые процедуры), `runframe` (`CoffeesFrame`).

## Обработка SQL-выражений в JDBC (Processing SQL Statements with JDBC)

В общем случае для обработки любого SQL-выражения в JDBC выполняются такие шаги:

1. Установить соединение (*establishing a connection*).
2. Создать выражение (*statement*).
3. Выполнить запрос.
4. Обработать объект `ResultSet`.
5. Закрыть соединение.

Эти шаги показаны на методе `CoffeesTable.viewTable` из примера руководства. Метод выводит
содержимое таблицы `COFFEES`:

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

### Установка соединений

Сначала установите соединение с нужным источником данных. Источником данных может быть СУБД,
устаревшая файловая система или другой источник данных с соответствующим JDBC-драйвером.
Соединение представлено объектом `Connection`. Подробнее — в разделе об установке соединения.

### Создание выражений (Statement)

`Statement` — это интерфейс, представляющий SQL-выражение. Объекты `Statement` выполняют и
порождают объекты `ResultSet` — таблицу данных, представляющую результат запроса к базе. Для
создания объекта `Statement` нужен объект `Connection`. Например:

```java
stmt = con.createStatement();
```

Существует три вида выражений:

- `Statement` — для простых SQL-выражений без параметров.
- `PreparedStatement` (расширяет `Statement`) — для предварительной компиляции SQL-выражений,
  которые могут содержать входные параметры. См. раздел *Using Prepared Statements*.
- `CallableStatement` (расширяет `PreparedStatement`) — для вызова хранимых процедур, которые
  могут содержать как входные, так и выходные параметры. См. раздел *Stored Procedures*.

### Выполнение запросов

Чтобы выполнить запрос, вызовите один из методов `execute` интерфейса `Statement`:

- `execute` — возвращает `true`, если первый объект, который возвращает запрос, является объектом
  `ResultSet`. Используйте этот метод, если запрос может вернуть один или несколько объектов
  `ResultSet`. Получайте их повторными вызовами `Statement.getResultSet`.
- `executeQuery` — возвращает один объект `ResultSet`.
- `executeUpdate` — возвращает целое число — количество строк, затронутых SQL-выражением.
  Используйте его для выражений `INSERT`, `DELETE` или `UPDATE`.

Например:

```java
ResultSet rs = stmt.executeQuery(query);
```

### Обработка объектов ResultSet

Доступ к данным объекта `ResultSet` осуществляется через курсор (*cursor*). Заметьте: это не
курсор базы данных, а указатель на одну строку данных в объекте `ResultSet`. Изначально курсор
расположен перед первой строкой. Чтобы перемещать курсор, вызываются различные методы `ResultSet`.

Например, `CoffeesTable.viewTable` повторно вызывает `ResultSet.next`, чтобы сдвинуть курсор
вперёд на одну строку. При каждом вызове `next` метод выводит данные той строки, на которой сейчас
стоит курсор:

```java
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
// ...
```

### Закрытие соединений

Закончив работу с объектом `Connection`, `Statement` или `ResultSet`, вызывайте его метод `close`,
чтобы немедленно освободить занятые ресурсы.

Как вариант, используйте выражение `try`-with-resources, которое автоматически закрывает объекты
`Connection`, `Statement` и `ResultSet` независимо от того, было ли выброшено исключение
`SQLException`. (JDBC выбрасывает `SQLException` при ошибке во время взаимодействия с источником
данных — см. раздел об обработке исключений.) Например, метод `CoffeesTable.viewTable`
автоматически закрывает свой объект `Statement`:

```java
try (Statement stmt = con.createStatement()) {
  // ...
}
```

Это выражение `try`-with-resources объявляет один ресурс — `stmt`, — который автоматически
закрывается при завершении блока `try`. Подробнее — в разделе *The try-with-resources Statement*
трейла *Essential Classes*.

## Установка соединения (Establishing a Connection)

Сначала нужно установить соединение с источником данных. JDBC-приложение обычно подключается к
целевому источнику данных одним из двух классов:

- `DriverManager` — полностью реализованный класс, соединяющий приложение с источником данных,
  заданным URL базы данных. При первой попытке установить соединение он автоматически загружает
  все JDBC-драйверы версии 4.0, найденные в пути к классам. Драйверы версий ниже 4.0 приложение
  должно загружать вручную.
- `DataSource` — интерфейс, предпочтительный по сравнению с `DriverManager`, поскольку он скрывает
  от приложения детали используемого источника данных. Свойства объекта `DataSource` настраиваются
  так, чтобы он представлял конкретный источник данных. См. раздел *Connecting with DataSource
  Objects*. О разработке приложений с `DataSource` см. *The Java EE Tutorial*.

> Примечание: примеры этого руководства используют класс `DriverManager`, а не `DataSource`, так
> как он проще и возможности `DataSource` примерам не нужны.

Эта страница охватывает темы: использование класса `DriverManager` и задание URL подключения к
базе данных.

### Использование класса DriverManager

Подключение к СУБД через `DriverManager` сводится к вызову метода `DriverManager.getConnection`.
Метод `JDBCTutorialUtilities.getConnection` устанавливает соединение:

```java
public Connection getConnection() throws SQLException {

    Connection conn = null;
    Properties connectionProps = new Properties();
    connectionProps.put("user", this.userName);
    connectionProps.put("password", this.password);

    if (this.dbms.equals("mysql")) {
        conn = DriverManager.getConnection(
                   "jdbc:" + this.dbms + "://" +
                   this.serverName +
                   ":" + this.portNumber + "/",
                   connectionProps);
    } else if (this.dbms.equals("derby")) {
        conn = DriverManager.getConnection(
                   "jdbc:" + this.dbms + ":" +
                   this.dbName +
                   ";create=true",
                   connectionProps);
    }
    System.out.println("Connected to database");
    return conn;
}
```

Метод `DriverManager.getConnection` требует URL базы данных, который зависит от СУБД. Примеры URL:

1. **MySQL:** `jdbc:mysql://localhost:3306/`, где `localhost` — имя сервера с базой данных,
   а `3306` — номер порта.
2. **Java DB:** `jdbc:derby:testdb;create=true`, где `testdb` — имя базы данных, к которой
   подключаемся, а `create=true` указывает СУБД создать базу.

   > Примечание: этот URL устанавливает соединение через встраиваемый драйвер Java DB (Embedded
   > Driver). В Java DB есть и сетевой клиентский драйвер (Network Client Driver) с другим URL.

Метод задаёт имя пользователя и пароль для доступа к СУБД через объект `Properties`.

> Примечания:
>
> - Обычно в URL базы данных также указывают имя существующей базы, к которой нужно подключиться.
>   Например, URL `jdbc:mysql://localhost:3306/mysql` представляет базу MySQL с именем `mysql`.
>   Примеры руководства используют URL без конкретной базы, так как сами её создают.
> - В прежних версиях JDBC, чтобы получить соединение, сначала требовалось инициализировать
>   драйвер вызовом `Class.forName`. Это требовало объект типа `java.sql.Driver`. Каждый
>   JDBC-драйвер содержит один или несколько классов, реализующих интерфейс `java.sql.Driver`.
>   Драйверы Java DB — `org.apache.derby.jdbc.EmbeddedDriver` и
>   `org.apache.derby.jdbc.ClientDriver`, для MySQL Connector/J — `com.mysql.cj.jdbc.Driver`.
>   Все JDBC-драйверы версии 4.0, найденные в пути к классам, загружаются автоматически. (Драйверы
>   версий ниже 4.0 нужно загружать вручную через `Class.forName`.)

Метод возвращает объект `Connection`, представляющий соединение с СУБД или конкретной базой
данных. Запросы к базе делаются через этот объект.

### Задание URL подключения к базе данных

URL подключения к базе данных — это строка, которую JDBC-драйвер СУБД использует для подключения.
Она может содержать сведения о том, где искать базу, имя базы данных и свойства конфигурации.
Точный синтаксис URL определяется вашей СУБД.

**URL подключения Java DB:**

```
jdbc:derby:[subsubprotocol:][databaseName][;attribute=value]*
```

- `subsubprotocol` указывает, где Java DB должна искать базу: в каталоге, в памяти, в пути к
  классам или в JAR-файле. Обычно опускается.
- `databaseName` — имя базы данных, к которой подключаемся.
- `attribute=value` — необязательный список атрибутов через точку с запятой. Они позволяют
  указать Java DB выполнить разные задачи: создать базу из URL, зашифровать её, задать каталоги
  для логов и трассировки, указать имя пользователя и пароль.

См. *Java DB Developer's Guide* и *Java DB Reference Manual* в *Java DB Technical Documentation*.

**URL подключения MySQL Connector/J:**

```
jdbc:mysql://[host][,failoverhost...]
    [:port]/[database]
    [?propertyName1][=propertyValue1]
    [&propertyName2][=propertyValue2]...
```

- `host:port` — имя хоста и номер порта компьютера с базой данных. По умолчанию `host` —
  `127.0.0.1`, `port` — `3306`.
- `database` — имя базы данных. Если не указано, соединение устанавливается без базы по умолчанию.
- `failover` — имя резервной (standby) базы данных (MySQL Connector/J поддерживает отказоустойчивое
  переключение).
- `propertyName=propertyValue` — необязательный список свойств через амперсанд.

См. *MySQL Reference Manual*.

## Подключение через объекты DataSource (Connecting with DataSource Objects)

Объекты `DataSource` — предпочтительный способ получить соединение с источником данных. Они
обеспечивают пул соединений (*connection pooling*) и распределённые транзакции (*distributed
transactions*), необходимые для корпоративной работы с базами данных. Объекты, создаваемые
классами, которые реализуют `DataSource`, представляют конкретную СУБД или иной источник данных
(например, файл). Интерфейс `DataSource` реализуется поставщиками драйверов.

**Кто разворачивает DataSource.** Объекты `DataSource` разворачивают (*deploy*) системные
администраторы с помощью инструментов (например, Apache Tomcat, Oracle WebLogic Server). Способ
развёртывания зависит от типа `DataSource`.

**Регистрация в JNDI.** Объекты `DataSource` регистрируются в службе именования через JNDI (Java
Naming and Directory Interface). Логические имена связываются (*bind*) с экземплярами `DataSource`,
чтобы программисты могли находить их по имени. Подконтекст `jdbc` зарезервирован для логических
имён `DataSource` (например, `jdbc/billingDB`).

**Преимущества перед DriverManager:**

- Не нужно жёстко прописывать в коде имена драйверов и URL JDBC — приложения становятся более
  переносимыми.
- Свойства упрощают сопровождение: администратор может обновить свойства источника данных, не
  меняя приложение.
- Можно предоставить пул соединений и поддержку распределённых транзакций.
- Лучшая производительность.

### Три типа реализаций DataSource

1. **Базовая реализация (basic).** Порождает стандартные объекты `Connection`, которые не
   объединяются в пул и не участвуют в распределённых транзакциях. Эквивалентны соединениям из
   `DriverManager`.
2. **С поддержкой пула соединений (connection pooling).** Порождает объекты `Connection`,
   участвующие в пуле соединений: соединения можно переиспользовать.
3. **С поддержкой распределённых транзакций (distributed transactions).** Порождает объекты
   `Connection`, пригодные для распределённых транзакций, которые обращаются к двум и более
   серверам СУБД. Обычно такая реализация также поддерживает пул соединений.

Примеры реализаций: для Java DB — `org.apache.derby.jdbc.ClientDataSource`, для MySQL —
`com.mysql.jdbc.jdbc2.optional.MysqlDataSource`.

### Развёртывание базовых объектов DataSource

Свойства базового объекта `DataSource`:

| Свойство | Значение |
|----------|----------|
| `serverName` | Имя сервера, на котором установлена база данных. |
| `databaseName` | Имя базы данных. |
| `description` | Описание источника данных. |

Системный администратор создаёт экземпляр и задаёт свойства:

```java
com.dbaccess.BasicDataSource ds = new com.dbaccess.BasicDataSource();
ds.setServerName("grinder");
ds.setDatabaseName("CUSTOMER_ACCOUNTS");
ds.setDescription("База данных клиентских счетов для биллинга");
```

Затем регистрирует объект в службе именования JNDI:

```java
Context ctx = new InitialContext();
ctx.bind("jdbc/billingDB", ds);
```

Логическое имя `jdbc/billingDB` связывается с объектом `DataSource`. Подконтекст `jdbc`
зарезервирован для объектов `DataSource`; последняя часть (`billingDB`) — логическое имя.

Программист находит объект `DataSource` по логическому имени и приводит его к типу `DataSource`:

```java
Context ctx = new InitialContext();
DataSource ds = (DataSource)ctx.lookup("jdbc/billingDB");
```

Затем получает соединение:

```java
Connection con = ds.getConnection("fernanda", "brewed");
```

Метод `getConnection` требует только имя пользователя и пароль, потому что свойства объекта
`DataSource` уже содержат имя и расположение базы данных.

### Развёртывание других реализаций DataSource

#### DataSource с пулом соединений

Пул соединений (*connection pool*) — это кэш объектов соединений, представляющих физические
соединения с базой. Во время работы приложение запрашивает соединение из пула; если свободное
есть — возвращается соединение из пула, иначе создаётся новое. Закончив, приложение возвращает
соединение в пул для повторного использования. Это значительно повышает производительность
приложений, активно работающих с базой, снижая стоимость создания объектов соединения.

Разворачиваются два объекта: объект `ConnectionPoolDataSource` (его свойства задают источник
данных, для которого порождаются соединения) и объект `DataSource`, настроенный на работу с ним
(через логическое имя JNDI объекта `ConnectionPoolDataSource`).

```java
// Шаг 1. Развернуть объект ConnectionPoolDataSource
com.dbaccess.ConnectionPoolDS cpds = new com.dbaccess.ConnectionPoolDS();
cpds.setServerName("creamer");
cpds.setDatabaseName("COFFEEBREAK");
cpds.setPortNumber(9040);
cpds.setDescription("Пул соединений для СУБД COFFEEBREAK");

// Зарегистрировать в JNDI (подконтекст jdbc/pool)
Context ctx = new InitialContext();
ctx.bind("jdbc/pool/fastCoffeeDB", cpds);

// Шаг 2. Развернуть объект DataSource, настроенный на пул
com.applogic.PooledDataSource ds = new com.applogic.PooledDataSource();
ds.setDescription("порождает пулированные соединения к COFFEEBREAK");
ds.setDataSourceName("jdbc/pool/fastCoffeeDB");
ctx = new InitialContext();
ctx.bind("jdbc/fastCoffeeDB", ds);
```

Использование пулированного соединения:

```java
ctx = new InitialContext();
ds = (DataSource)ctx.lookup("jdbc/fastCoffeeDB");

try {
    Connection con = ds.getConnection(username, password);
    // ... код, использующий пулированное соединение con
} catch (Exception ex) {
    // ... обработка исключений
} finally {
    if (con != null) con.close();
}
```

Ключевые правила для пулированных соединений:

1. Получайте соединение через объект `DataSource`, а не через `DriverManager`.
2. Закрывайте пулированное соединение в блоке `finally` — чтобы оно гарантированно вернулось в
   пул для повторного использования.

Пример с EJB:

```java
import java.sql.*;
import javax.sql.*;
import javax.ejb.*;
import javax.naming.*;

public class ConnectionPoolingBean implements SessionBean {

    public void ejbCreate() throws CreateException {
        ctx = new InitialContext();
        ds = (DataSource)ctx.lookup("jdbc/fastCoffeeDB");
    }

    public void updatePrice(float price, String cofName,
                            String username, String password)
        throws SQLException {

        Connection con;
        PreparedStatement pstmt;
        try {
            con = ds.getConnection(username, password);
            con.setAutoCommit(false);
            pstmt = con.prepareStatement("UPDATE COFFEES " +
                        "SET PRICE = ? " +
                        "WHERE COF_NAME = ?");
            pstmt.setFloat(1, price);
            pstmt.setString(2, cofName);
            pstmt.executeUpdate();

            con.commit();
            pstmt.close();

        } finally {
            if (con != null) con.close();
        }
    }

    private DataSource ds = null;
    private Context ctx = null;
}
```

#### DataSource с распределёнными транзакциями

Соединения такого источника можно использовать в распределённых транзакциях — обращающихся к двум
и более серверам СУБД. Разворачиваются два объекта: объект `XADataSource` и объект `DataSource`,
настроенный на работу с ним. Классы `DataSource` от поставщиков EJB обычно поддерживают и пул
соединений, и распределённые транзакции.

```java
// Шаг 1. Развернуть объект XADataSource
com.dbaccess.XATransactionalDS xads = new com.dbaccess.XATransactionalDS();
xads.setServerName("creamer");
xads.setDatabaseName("COFFEEBREAK");
xads.setPortNumber(9040);
xads.setDescription("Распределённые транзакции для СУБД COFFEEBREAK");

// Зарегистрировать в JNDI (подконтекст jdbc/xa)
Context ctx = new InitialContext();
ctx.bind("jdbc/xa/distCoffeeDB", xads);

// Шаг 2. Развернуть объект DataSource, настроенный на распределённые транзакции
com.applogic.TransactionalDS ds = new com.applogic.TransactionalDS();
ds.setDescription("Порождает соединения для распределённых транзакций к COFFEEBREAK");
ds.setDataSourceName("jdbc/xa/distCoffeeDB");
ctx = new InitialContext();
ctx.bind("jdbc/distCoffeeDB", ds);
```

Получение соединения:

```java
Context ctx = new InitialContext();
DataSource ds = (DataSource)ctx.lookup("jdbc/distCoffeesDB");
Connection con = ds.getConnection();
```

> Внимание: для соединения, участвующего в распределённой транзакции, **нельзя** вызывать
> следующие методы — границами транзакции управляет менеджер транзакций:
>
> - `Connection.commit()`;
> - `Connection.rollback()`;
> - `Connection.setAutoCommit(true)`.
>
> Новое соединение, созданное в области распределённой транзакции, по умолчанию имеет
> отключённый режим автофиксации (auto-commit). Эти ограничения действуют **только** когда
> соединение участвует в распределённой транзакции; вне её ограничений нет.

Пример с EJB (код явно не вызывает commit/rollback — областью распределённой транзакции управляет
инфраструктура промежуточного сервера; блок `finally` гарантирует закрытие соединения и его
возврат в пул):

```java
import java.sql.*;
import javax.sql.*;
import javax.ejb.*;
import javax.naming.*;

public class DistributedTransactionBean implements SessionBean {

    public void ejbCreate() throws CreateException {
        ctx = new InitialContext();
        ds = (DataSource)ctx.lookup("jdbc/distCoffeesDB");
    }

    public void updateTotal(int incr, String cofName, String username,
                            String password)
        throws SQLException {

        Connection con;
        PreparedStatement pstmt;

        try {
            con = ds.getConnection(username, password);
            pstmt = con.prepareStatement("UPDATE COFFEES " +
                        "SET TOTAL = TOTAL + ? " +
                        "WHERE COF_NAME = ?");
            pstmt.setInt(1, incr);
            pstmt.setString(2, cofName);
            pstmt.executeUpdate();
            pstmt.close();
        } finally {
            if (con != null) con.close();
        }
    }

    private DataSource ds = null;
    private Context ctx = null;
}
```

## Обработка SQLException (Handling SQLExceptions)

### Обзор SQLException

При ошибке во время взаимодействия с источником данных JDBC выбрасывает экземпляр `SQLException`
(а не просто `Exception`). Этот экземпляр содержит сведения, помогающие установить причину ошибки:

- **Описание ошибки.** Объект `String` с описанием возвращает метод `SQLException.getMessage`.
- **Код SQLState.** Эти коды и их значения стандартизированы ISO/ANSI и Open Group (X/Open); часть
  кодов зарезервирована для определения поставщиками СУБД. Это строка из пяти буквенно-цифровых
  символов. Возвращается методом `SQLException.getSQLState`.
- **Код ошибки.** Целое число, идентифицирующее ошибку, вызвавшую `SQLException`. Его значение и
  смысл зависят от реализации и могут совпадать с фактическим кодом ошибки источника данных.
  Возвращается методом `SQLException.getErrorCode`.
- **Причина (cause).** У `SQLException` может быть причинная связь — один или несколько объектов
  `Throwable`, вызвавших исключение. Чтобы пройти цепочку причин, рекурсивно вызывайте
  `SQLException.getCause`, пока он не вернёт `null`.
- **Ссылка на сцепленные (chained) исключения.** Если произошло несколько ошибок, исключения
  связаны в цепочку. Получайте их методом `SQLException.getNextException` на выброшенном исключении.

### Получение исключений

Метод `JDBCTutorialUtilities.printSQLException` выводит SQLState, код ошибки, описание и причину
(если есть) из `SQLException`, а также все сцепленные с ним исключения:

```java
public static void printSQLException(SQLException ex) {

    for (Throwable e : ex) {
        if (e instanceof SQLException) {
            if (ignoreSQLException(
                ((SQLException)e).
                getSQLState()) == false) {

                e.printStackTrace(System.err);
                System.err.println("SQLState: " +
                    ((SQLException)e).getSQLState());

                System.err.println("Error Code: " +
                    ((SQLException)e).getErrorCode());

                System.err.println("Message: " + e.getMessage());

                Throwable t = ex.getCause();
                while(t != null) {
                    System.out.println("Cause: " + t);
                    t = t.getCause();
                }
            }
        }
    }
}
```

Например, если вызвать метод `CoffeesTable.dropTable` с Java DB, когда таблицы `COFFEES` не
существует, *и* убрать вызов `JDBCTutorialUtilities.ignoreSQLException`, вывод будет примерно
таким:

```
SQLState: 42Y55
Error Code: 30000
Message: 'DROP TABLE' cannot be performed on
'TESTDB.COFFEES' because it does not exist.
```

Вместо печати сведений о `SQLException` можно сначала получить `SQLState` и обработать исключение
соответственно. Например, метод `JDBCTutorialUtilities.ignoreSQLException` возвращает `true`, если
`SQLState` равен `42Y55` (при использовании Java DB), благодаря чему `printSQLException`
игнорирует это исключение:

```java
public static boolean ignoreSQLException(String sqlState) {

    if (sqlState == null) {
        System.out.println("The SQL state is not defined!");
        return false;
    }

    // X0Y32: JAR-файл уже существует в схеме
    if (sqlState.equalsIgnoreCase("X0Y32"))
        return true;

    // 42Y55: таблица уже существует в схеме
    if (sqlState.equalsIgnoreCase("42Y55"))
        return true;

    return false;
}
```

### Получение предупреждений (Warnings)

Объекты `SQLWarning` — подкласс `SQLException`, относящийся к предупреждениям доступа к базе.
Предупреждения, в отличие от исключений, не останавливают выполнение приложения — они лишь
сообщают, что что-то прошло не так, как планировалось. Например, предупреждение может сообщить,
что отзываемая привилегия не была отозвана, или что при запрошенном отключении произошла ошибка.

Предупреждение может сообщаться на объекте `Connection`, `Statement` (включая `PreparedStatement`
и `CallableStatement`) или `ResultSet`. У каждого из этих классов есть метод `getWarnings`,
который надо вызвать, чтобы увидеть первое предупреждение на вызывающем объекте. Если `getWarnings`
вернул предупреждение, вызовом `getNextWarning` на нём можно получить дополнительные. Выполнение
выражения автоматически очищает предупреждения предыдущего, поэтому они не накапливаются. Значит,
если нужно получить предупреждения по выражению, делать это надо до выполнения следующего.

Следующие методы из `JDBCTutorialUtilities.java` показывают, как получить полную информацию о
предупреждениях на объектах `Statement` или `ResultSet`:

```java
public static void getWarningsFromResultSet(ResultSet rs)
    throws SQLException {
    JDBCTutorialUtilities.printWarnings(rs.getWarnings());
}

public static void getWarningsFromStatement(Statement stmt)
    throws SQLException {
    JDBCTutorialUtilities.printWarnings(stmt.getWarnings());
}

public static void printWarnings(SQLWarning warning)
    throws SQLException {

    if (warning != null) {
        System.out.println("\n---Warning---\n");

    while (warning != null) {
        System.out.println("Message: " + warning.getMessage());
        System.out.println("SQLState: " + warning.getSQLState());
        System.out.print("Vendor error code: ");
        System.out.println(warning.getErrorCode());
        System.out.println("");
        warning = warning.getNextWarning();
    }
}
```

Самое частое предупреждение — `DataTruncation`, подкласс `SQLWarning`. У всех объектов
`DataTruncation` `SQLState` равен `01004`, что означает проблему при чтении или записи данных.
Методы `DataTruncation` позволяют узнать, в каком столбце или параметре данные были усечены,
произошло ли усечение при чтении или записи, сколько байтов должно было быть передано и сколько
фактически передано.

### Категоризированные SQLException

JDBC-драйвер может выбрасывать подкласс `SQLException`, соответствующий распространённому
`SQLState` или общему состоянию ошибки, не связанному с конкретным классом значений `SQLState`.
Это позволяет писать более переносимый код обработки ошибок. Такие исключения — подклассы одного
из классов:

- `SQLNonTransientException`;
- `SQLTransientException`;
- `SQLRecoverableException`.

Подробнее — в актуальном Javadoc пакета `java.sql` или в документации вашего драйвера.

### Другие подклассы SQLException

Также могут выбрасываться следующие подклассы `SQLException`:

- `BatchUpdateException` — выбрасывается при ошибке во время пакетного обновления (*batch update*).
  Помимо сведений из `SQLException`, предоставляет счётчики обновлений для всех выражений,
  выполненных до возникновения ошибки.
- `SQLClientInfoException` — выбрасывается, когда одно или несколько клиентских информационных
  свойств не удалось установить на `Connection`. Помимо сведений из `SQLException`, предоставляет
  список клиентских свойств, которые не были заданы.

## Подготовка таблиц (Setting Up Tables)

Эта страница описывает все таблицы, используемые в руководстве, и способы их создания: таблицы
`COFFEES`, `SUPPLIERS`, `COF_INVENTORY`, `MERCH_INVENTORY`, `COFFEE_HOUSES`, `DATA_REPOSITORY`,
а также создание и наполнение таблиц.

### Таблица COFFEES

Таблица `COFFEES` хранит сведения о сортах кофе, доступных для продажи в «The Coffee Break»:

| COF_NAME | SUP_ID | PRICE | SALES | TOTAL |
|----------|--------|-------|-------|-------|
| Colombian | 101 | 7.99 | 0 | 0 |
| French_Roast | 49 | 8.99 | 0 | 0 |
| Espresso | 150 | 9.99 | 0 | 0 |
| Colombian_Decaf | 101 | 8.99 | 0 | 0 |
| French_Roast_Decaf | 49 | 9.99 | 0 | 0 |

Столбцы таблицы `COFFEES`:

- `COF_NAME` — название кофе. SQL-тип `VARCHAR`, максимальная длина 32 символа. Так как названия
  у всех сортов разные, имя однозначно определяет конкретный кофе и служит первичным ключом
  (*primary key*).
- `SUP_ID` — число, идентифицирующее поставщика кофе. SQL-тип `INTEGER`. Определён как внешний
  ключ (*foreign key*), ссылающийся на столбец `SUP_ID` таблицы `SUPPLIERS`. Поэтому СУБД следит
  за тем, чтобы каждое значение в этом столбце совпадало с одним из значений соответствующего
  столбца в `SUPPLIERS`.
- `PRICE` — цена кофе за фунт. SQL-тип `FLOAT`, так как нужны значения с десятичной точкой.
  (Обычно денежные суммы хранят в SQL-типе `DECIMAL` или `NUMERIC`, но из-за различий между СУБД
  и во избежание несовместимости с ранними версиями JDBC руководство использует более стандартный
  тип `FLOAT`.)
- `SALES` — число фунтов кофе, проданных за текущую неделю. SQL-тип `INTEGER`.
- `TOTAL` — число фунтов кофе, проданных на текущий момент. SQL-тип `INTEGER`.

### Таблица SUPPLIERS

Таблица `SUPPLIERS` хранит сведения о каждом поставщике:

| SUP_ID | SUP_NAME | STREET | CITY | STATE | ZIP |
|--------|----------|--------|------|-------|-----|
| 101 | Acme, Inc. | 99 Market Street | Groundsville | CA | 95199 |
| 49 | Superior Coffee | 1 Party Place | Mendocino | CA | 95460 |
| 150 | The High Ground | 100 Coffee Lane | Meadows | CA | 93966 |

Столбцы таблицы `SUPPLIERS`:

- `SUP_ID` — число, идентифицирующее поставщика кофе. SQL-тип `INTEGER`. Первичный ключ этой
  таблицы.
- `SUP_NAME` — название поставщика кофе.
- `STREET`, `CITY`, `STATE`, `ZIP` — адрес поставщика кофе.

### Таблица COF_INVENTORY

Таблица `COF_INVENTORY` хранит сведения о количестве кофе на каждом складе:

| WAREHOUSE_ID | COF_NAME | SUP_ID | QUAN | DATE_VAL |
|--------------|----------|--------|------|----------|
| 1234 | House_Blend | 49 | 0 | 2006_04_01 |
| 1234 | House_Blend_Decaf | 49 | 0 | 2006_04_01 |
| 1234 | Colombian | 101 | 0 | 2006_04_01 |
| 1234 | French_Roast | 49 | 0 | 2006_04_01 |
| 1234 | Espresso | 150 | 0 | 2006_04_01 |
| 1234 | Colombian_Decaf | 101 | 0 | 2006_04_01 |

Столбцы таблицы `COF_INVENTORY`:

- `WAREHOUSE_ID` — число, идентифицирующее склад.
- `COF_NAME` — название конкретного сорта кофе.
- `SUP_ID` — число, идентифицирующее поставщика.
- `QUAN` — число, указывающее доступное количество товара.
- `DATE` — отметка времени (*timestamp*) последнего обновления строки.

### Таблица MERCH_INVENTORY

Таблица `MERCH_INVENTORY` хранит сведения о количестве некофейных товаров на складе:

| ITEM_ID | ITEM_NAME | SUP_ID | QUAN | DATE |
|---------|-----------|--------|------|------|
| 00001234 | Cup_Large | 00456 | 28 | 2006_04_01 |
| 00001235 | Cup_Small | 00456 | 36 | 2006_04_01 |
| 00001236 | Saucer | 00456 | 64 | 2006_04_01 |
| 00001287 | Carafe | 00456 | 12 | 2006_04_01 |
| 00006931 | Carafe | 00927 | 3 | 2006_04_01 |
| 00006935 | PotHolder | 00927 | 88 | 2006_04_01 |
| 00006977 | Napkin | 00927 | 108 | 2006_04_01 |
| 00006979 | Towel | 00927 | 24 | 2006_04_01 |
| 00004488 | CofMaker | 08732 | 5 | 2006_04_01 |
| 00004490 | CofGrinder | 08732 | 9 | 2006_04_01 |
| 00004495 | EspMaker | 08732 | 4 | 2006_04_01 |
| 00006914 | Cookbook | 00927 | 12 | 2006_04_01 |

Столбцы таблицы `MERCH_INVENTORY`:

- `ITEM_ID` — число, идентифицирующее товар.
- `ITEM_NAME` — название товара.
- `SUP_ID` — число, идентифицирующее поставщика.
- `QUAN` — число, указывающее доступное количество товара.
- `DATE` — отметка времени последнего обновления строки.

### Таблица COFFEE_HOUSES

Таблица `COFFEE_HOUSES` хранит расположения кофеен:

| STORE_ID | CITY | COFFEE | MERCH | TOTAL |
|----------|------|--------|-------|-------|
| 10023 | Mendocino | 3450 | 2005 | 5455 |
| 33002 | Seattle | 4699 | 3109 | 7808 |
| 10040 | SF | 5386 | 2841 | 8227 |
| 32001 | Portland | 3147 | 3579 | 6726 |
| 10042 | SF | 2863 | 1874 | 4710 |
| 10024 | Sacramento | 1987 | 2341 | 4328 |
| 10039 | Carmel | 2691 | 1121 | 3812 |
| 10041 | LA | 1533 | 1007 | 2540 |
| 33005 | Olympia | 2733 | 1550 | 4283 |
| 33010 | Seattle | 3210 | 2177 | 5387 |
| 10035 | SF | 1922 | 1056 | 2978 |
| 10037 | LA | 2143 | 1876 | 4019 |
| 10034 | San_Jose | 1234 | 1032 | 2266 |
| 32004 | Eugene | 1356 | 1112 | 2468 |

Столбцы таблицы `COFFEE_HOUSES`:

- `STORE_ID` — число, идентифицирующее кофейню. Среди прочего, оно указывает штат расположения
  кофейни: значение, начинающееся с 10, означает Калифорнию; начинающееся с 32 — Орегон;
  начинающееся с 33 — штат Вашингтон.
- `CITY` — название города, где расположена кофейня.
- `COFFEE` — число, указывающее объём проданного кофе.
- `MERCH` — число, указывающее объём проданных товаров.
- `TOTAL` — общий объём проданных кофе и товаров.

### Таблица DATA_REPOSITORY

Таблица `DATA_REPOSITORY` хранит URL-адреса, ссылающиеся на документы и другие данные, интересные
«The Coffee Break». Скрипт `populate_tables.sql` не добавляет данные в эту таблицу. Столбцы:

- `DOCUMENT_NAME` — строка, идентифицирующая URL.
- `URL` — сам URL.

### Создание таблиц

Создавать таблицы можно через Apache Ant или через JDBC API.

#### Создание таблиц через Apache Ant

Чтобы создать таблицы для примеров, выполните в каталоге `<каталог руководства JDBC>`:

```
ant setup
```

Эта команда запускает несколько Ant-целей, включая `build-tables` (из `build.xml`):

```xml
<target name="build-tables"
  description="Create database tables">
  <sql
    driver="${DB.DRIVER}"
    url="${DB.URL}"
    userid="${DB.USER}"
    password="${DB.PASSWORD}"
    classpathref="CLASSPATH"
    delimiter="${DB.DELIMITER}"
    autocommit="false" onerror="abort">
    <transaction src=
  "./sql/${DB.VENDOR}/create-tables.sql"/>
  </sql>
</target>
```

Пример задаёт значения для следующих параметров Ant-задачи `sql`:

| Параметр | Описание |
|----------|----------|
| `driver` | Полностью квалифицированное имя класса JDBC-драйвера (`org.apache.derby.jdbc.EmbeddedDriver` для Java DB и `com.mysql.cj.jdbc.Driver` для MySQL Connector/J). |
| `url` | URL подключения к базе данных, который использует драйвер. |
| `userid` | Имя действительного пользователя в СУБД. |
| `password` | Пароль пользователя из `userid`. |
| `classpathref` | Полный путь к JAR-файлу с классом из `driver`. |
| `delimiter` | Строка или символ, разделяющий SQL-выражения. Здесь — точка с запятой (`;`). |
| `autocommit` | Булево значение; если `false`, все SQL-выражения выполняются как одна транзакция. |
| `onerror` | Действие при сбое выражения; возможные значения — `continue`, `stop`, `abort`. Значение `abort` означает, что при ошибке транзакция прерывается. |

Значения этих параметров хранятся в отдельном файле; `build.xml` подключает их задачей `import`:

```xml
<import file="${ANTPROPERTIES}"/>
```

Элемент `transaction` указывает файл с SQL-выражениями для выполнения. Файл `create-tables.sql`
содержит выражения, создающие все таблицы этой страницы. Например, его фрагмент создаёт таблицы
`SUPPLIERS` и `COFFEES`:

```sql
create table SUPPLIERS
    (SUP_ID integer NOT NULL,
    SUP_NAME varchar(40) NOT NULL,
    STREET varchar(40) NOT NULL,
    CITY varchar(20) NOT NULL,
    STATE char(2) NOT NULL,
    ZIP char(5),
    PRIMARY KEY (SUP_ID));

create table COFFEES
    (COF_NAME varchar(32) NOT NULL,
    SUP_ID int NOT NULL,
    PRICE numeric(10,2) NOT NULL,
    SALES integer NOT NULL,
    TOTAL integer NOT NULL,
    PRIMARY KEY (COF_NAME),
    FOREIGN KEY (SUP_ID)
        REFERENCES SUPPLIERS (SUP_ID));
```

> Примечание: в `build.xml` есть ещё цель `drop-tables`, удаляющая таблицы руководства. Цель
> `setup` запускает `drop-tables` перед `build-tables`.

#### Создание таблиц через JDBC API

Метод `SuppliersTable.createTable` создаёт таблицу `SUPPLIERS`:

```java
  public void createTable() throws SQLException {
    String createString =
      "create table SUPPLIERS " + "(SUP_ID integer NOT NULL, " +
      "SUP_NAME varchar(40) NOT NULL, " + "STREET varchar(40) NOT NULL, " +
      "CITY varchar(20) NOT NULL, " + "STATE char(2) NOT NULL, " +
      "ZIP char(5), " + "PRIMARY KEY (SUP_ID))";

    try (Statement stmt = con.createStatement()) {
      stmt.executeUpdate(createString);
    } catch (SQLException e) {
      JDBCTutorialUtilities.printSQLException(e);
    }
  }
```

Метод `CoffeesTable.createTable` создаёт таблицу `COFFEES`:

```java
  public void createTable() throws SQLException {
    String createString =
      "create table COFFEES " + "(COF_NAME varchar(32) NOT NULL, " +
      "SUP_ID int NOT NULL, " + "PRICE numeric(10,2) NOT NULL, " +
      "SALES integer NOT NULL, " + "TOTAL integer NOT NULL, " +
      "PRIMARY KEY (COF_NAME), " +
      "FOREIGN KEY (SUP_ID) REFERENCES SUPPLIERS (SUP_ID))";
    try (Statement stmt = con.createStatement()) {
      stmt.executeUpdate(createString);
    } catch (SQLException e) {
      JDBCTutorialUtilities.printSQLException(e);
    }
  }
```

В обоих методах `con` — объект `Connection`, а `dbName` — имя базы, в которой создаётся таблица.

Чтобы выполнить SQL-запрос (например, заданный строкой `createString`), используйте объект
`Statement`. Создайте его вызовом `Connection.createStatement` на существующем объекте
`Connection`, а для выполнения запроса вызовите `Statement.executeUpdate`.

Все объекты `Statement` закрываются при закрытии создавшего их соединения. Тем не менее хорошей
практикой считается явно закрывать объекты `Statement`, как только они больше не нужны — это
немедленно освобождает внешние ресурсы. Закрывайте выражение вызовом `Statement.close`. Размещайте
его в блоке `finally`, чтобы оно закрылось даже при прерывании обычного хода программы исключением
(например, `SQLException`).

> Примечание: таблицу `SUPPLIERS` нужно создать раньше `COFFEES`, потому что `COFFEES` содержит
> внешний ключ `SUP_ID`, ссылающийся на `SUPPLIERS`.

### Наполнение таблиц

Вставлять данные в таблицы тоже можно через Apache Ant или через JDBC API.

#### Наполнение таблиц через Apache Ant

Помимо создания таблиц, команда `ant setup` также наполняет их. Она запускает Ant-цель
`populate-tables`, выполняющую SQL-скрипт `populate-tables.sql`. Его фрагмент, наполняющий таблицы
`SUPPLIERS` и `COFFEES`:

```sql
insert into SUPPLIERS values(
    49, 'Superior Coffee', '1 Party Place',
    'Mendocino', 'CA', '95460');
insert into SUPPLIERS values(
    101, 'Acme, Inc.', '99 Market Street',
    'Groundsville', 'CA', '95199');
insert into SUPPLIERS values(
    150, 'The High Ground',
    '100 Coffee Lane', 'Meadows', 'CA', '93966');
insert into COFFEES values(
    'Colombian', 00101, 7.99, 0, 0);
insert into COFFEES values(
    'French_Roast', 00049, 8.99, 0, 0);
insert into COFFEES values(
    'Espresso', 00150, 9.99, 0, 0);
insert into COFFEES values(
    'Colombian_Decaf', 00101, 8.99, 0, 0);
insert into COFFEES values(
    'French_Roast_Decaf', 00049, 9.99, 0, 0);
```

#### Наполнение таблиц через JDBC API

Метод `SuppliersTable.populateTable` вставляет данные в таблицу:

```java
  public void populateTable() throws SQLException {
    try (Statement stmt = con.createStatement()) {
      stmt.executeUpdate("insert into SUPPLIERS " +
                         "values(49, 'Superior Coffee', '1 Party Place', " +
                         "'Mendocino', 'CA', '95460')");
      stmt.executeUpdate("insert into SUPPLIERS " +
                         "values(101, 'Acme, Inc.', '99 Market Street', " +
                         "'Groundsville', 'CA', '95199')");
      stmt.executeUpdate("insert into SUPPLIERS " +
                         "values(150, 'The High Ground', '100 Coffee Lane', " +
                         "'Meadows', 'CA', '93966')");
    } catch (SQLException e) {
      JDBCTutorialUtilities.printSQLException(e);
    }
  }
```

Метод `CoffeesTable.populateTable` вставляет данные в таблицу:

```java
  public void populateTable() throws SQLException {
    try (Statement stmt = con.createStatement()) {
      stmt.executeUpdate("insert into COFFEES " +
                         "values('Colombian', 00101, 7.99, 0, 0)");
      stmt.executeUpdate("insert into COFFEES " +
                         "values('French_Roast', 00049, 8.99, 0, 0)");
      stmt.executeUpdate("insert into COFFEES " +
                         "values('Espresso', 00150, 9.99, 0, 0)");
      stmt.executeUpdate("insert into COFFEES " +
                         "values('Colombian_Decaf', 00101, 8.99, 0, 0)");
      stmt.executeUpdate("insert into COFFEES " +
                         "values('French_Roast_Decaf', 00049, 9.99, 0, 0)");
    } catch (SQLException e) {
      JDBCTutorialUtilities.printSQLException(e);
    }
  }
```

## Источник

- [Lesson: JDBC Basics](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html) — официальное руководство Oracle.
- [Getting Started](https://docs.oracle.com/javase/tutorial/jdbc/basics/gettingstarted.html) — официальное руководство Oracle.
- [Processing SQL Statements with JDBC](https://docs.oracle.com/javase/tutorial/jdbc/basics/processingsqlstatements.html) — официальное руководство Oracle.
- [Establishing a Connection](https://docs.oracle.com/javase/tutorial/jdbc/basics/connecting.html) — официальное руководство Oracle.
- [Connecting with DataSource Objects](https://docs.oracle.com/javase/tutorial/jdbc/basics/sqldatasources.html) — официальное руководство Oracle.
- [Handling SQLExceptions](https://docs.oracle.com/javase/tutorial/jdbc/basics/sqlexception.html) — официальное руководство Oracle.
- [Setting Up Tables](https://docs.oracle.com/javase/tutorial/jdbc/basics/tables.html) — официальное руководство Oracle.
