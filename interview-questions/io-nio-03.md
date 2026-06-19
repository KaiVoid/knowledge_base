# Ввод-вывод: IO и NIO — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../theory/01-knowledge-areas/01-language-and-platform/07-io-nio.md](../theory/01-knowledge-areas/01-language-and-platform/07-io-nio.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](io-nio-01.md) · [ч.2](io-nio-02.md) · **ч.3**

---
### Вопрос 41. Что такое DatagramChannel в Java NIO? Чем работа с UDP через DatagramChannel отличается от работы с TCP через SocketChannel, и почему DatagramChannel можно использовать без вызова connect()?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java NIO DatagramChannel — jenkov.com](https://jenkov.com/tutorials/java-nio/datagram-channel.html)

`DatagramChannel` — это NIO-канал для работы с UDP-пакетами. В отличие от потоковых каналов, с DatagramChannel нельзя просто читать и писать: вместо этого нужно отправлять и получать датаграммы.

**Открытие канала:**
```java
DatagramChannel channel = DatagramChannel.open();
channel.socket().bind(new InetSocketAddress(9999));
```

**Получение данных (receive):**
```java
ByteBuffer buf = ByteBuffer.allocate(48);
buf.clear();
channel.receive(buf);
```
Если полученная датаграмма содержит больше байт, чем вмещает буфер, лишние байты молча отбрасываются.

**Отправка данных (send):**
```java
ByteBuffer buf = ByteBuffer.wrap("Hello".getBytes());
int bytesSent = channel.send(buf, new InetSocketAddress("jenkov.com", 80));
```

**Опциональный вызов connect():**

DatagramChannel можно подключить к конкретному адресу:
```java
channel.connect(new InetSocketAddress("jenkov.com", 80));
```
Это соединение не является настоящим TCP-соединением. UDP остаётся connectionless-протоколом. Соединение лишь «привязывает» канал к одному адресу: после этого можно использовать `read()` и `write()` вместо `send()`/`receive()`, но гарантий доставки по-прежнему нет.

#### Ответ от Claude

**Что такое DatagramChannel**

`java.nio.channels.DatagramChannel` — это селектируемый (`SelectableChannel`) NIO-канал для работы с протоколом UDP (User Datagram Protocol). Реализует также интерфейс `MulticastChannel`, что позволяет участвовать в IP-мультикасте. Доступен с Java 1.4; существенно расширен в Java 7 (поддержка IPv6, `NetworkChannel`).

**Фундаментальные различия UDP и TCP применительно к каналам**

| Аспект | DatagramChannel (UDP) | SocketChannel (TCP) |
|---|---|---|
| Соединение | Не требуется (connectionless) | Обязательно (`connect()` должен успешно завершиться) |
| Единица данных | Датаграмма (дискретный пакет с границами) | Непрерывный поток байт (границы сообщений отсутствуют) |
| Гарантия доставки | Нет | Да (TCP повторяет пакеты) |
| Порядок пакетов | Не гарантирован | Гарантирован |
| Методы отправки/приёма | `send()` / `receive()` (без соединения) | `write()` / `read()` |
| Использование `read()`/`write()` | Только после `connect()` | Всегда |
| Поддержка мультикаста | Да | Нет |

**Почему connect() необязателен**

Протокол UDP не устанавливает соединение на уровне сети — каждая датаграмма маршрутизируется независимо. Поэтому методы `send()` и `receive()` принимают/возвращают адрес (`SocketAddress`) непосредственно при каждом вызове, что позволяет общаться с произвольными адресатами без предварительного `connect()`.

Вызов `connect()` у DatagramChannel имеет иной смысл, чем у SocketChannel. Согласно Javadoc Oracle (Java 21):

> "A datagram channel need not be connected in order for the send and receive methods to be used. A datagram channel may be connected, in order to avoid the overhead of the security checks otherwise performed as part of every send and receive operation."

То есть `connect()` выполняет две функции:
1. **Оптимизация безопасности**: проверки SecurityManager выполняются один раз при `connect()`, а не при каждом `send()`/`receive()`.
2. **Ограничение адресата**: после `connect()` канал принимает датаграммы только от привязанного адреса и отправляет только на него; это позволяет использовать `read()`/`write()` вместо `send()`/`receive()`.

Реального TCP-handshake при этом не происходит — UDP-стек ОС просто запоминает адрес назначения.

**Пример без connect() (типичный UDP-сервер):**
```java
DatagramChannel server = DatagramChannel.open();
server.bind(new InetSocketAddress(9999));

ByteBuffer buf = ByteBuffer.allocate(1024);
SocketAddress clientAddr = server.receive(buf);  // адрес отправителя возвращается
buf.flip();
server.send(buf, clientAddr);                    // ответ тому же клиенту
```

**Пример с connect() (упрощённый клиент с одним сервером):**
```java
DatagramChannel client = DatagramChannel.open();
client.connect(new InetSocketAddress("server.example.com", 9999));

ByteBuffer buf = ByteBuffer.wrap("ping".getBytes());
client.write(buf);           // эквивалентно send() на подключённый адрес

ByteBuffer resp = ByteBuffer.allocate(1024);
client.read(resp);           // принимает только от подключённого адреса
```

**Ключевой вывод**: DatagramChannel без `connect()` — гибкий инструмент для общения с множеством адресов (DNS-серверы, VoIP-шлюзы, мониторинг); DatagramChannel с `connect()` — удобная форма работы с одним пиром при минимальных накладных расходах на проверку безопасности.

---

### Вопрос 42. Почему Files.lines() может вызвать утечку ресурсов, если не использовать try-with-resources? Чем Files.lines() отличается от Files.readAllLines() с точки зрения потребления памяти при чтении большого файла?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Files (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/nio/file/Files.html)

Метод `Files.lines(Path path)` читает все строки файла в виде `Stream<String>`. Поток заполняется лениво (lazy) — строки читаются по мере потребления. Поскольку поток открывает ресурсы файловой системы, его **необходимо закрывать** после использования. Если закрытие не выполнено, ресурс остаётся открытым до завершения JVM или GC-финализации, что является утечкой дескриптора файла.

Рекомендуемый паттерн из документации Oracle:
```java
try (Stream<String> lines = Files.lines(path, StandardCharsets.UTF_8)) {
    lines.forEach(System.out::println);
}
```

Метод `Files.readAllLines(Path path)` читает все строки и немедленно возвращает `List<String>`. Ресурсы закрываются внутри метода до его возврата — явное закрытие не требуется. Однако весь файл загружается в память сразу, что делает этот метод непригодным для больших файлов.

#### Ответ от Claude

**Механизм утечки ресурсов в Files.lines()**

`Files.lines()` внутренне открывает `FileChannel` (через `Files.newInputStream()`), оборачивает его в `BufferedReader` и создаёт `Stream<String>`, связанный с этим reader'ом как ресурсом. `Stream<String>` реализует `AutoCloseable`: при закрытии потока закрывается и reader, и FileChannel.

Если поток не закрыт, `FileChannel` остаётся открытым. В Linux это означает, что файловый дескриптор (fd) не возвращается ОС. При достаточном количестве таких утечек процесс достигнет лимита открытых дескрипторов (`ulimit -n`) и получит `IOException: Too many open files`.

Финализатор может в конечном счёте закрыть канал, но: (а) GC не гарантирует время срабатывания, (б) в современных JVM (Java 9+) финализация помечена устаревшей.

**Сравнение Files.lines() и Files.readAllLines()**

| Аспект | Files.lines() | Files.readAllLines() |
|---|---|---|
| Возвращаемый тип | `Stream<String>` | `List<String>` |
| Стратегия чтения | Ленивая (lazy): строки читаются по мере итерации | Жадная (eager): весь файл читается немедленно |
| Потребление памяти | Минимальное: в памяти одна строка (или небольшой буфер) в каждый момент | Пропорционально размеру файла: все строки одновременно в heap |
| Управление ресурсами | Требует явного закрытия (try-with-resources) | Закрывает ресурсы автоматически до возврата |
| Риск утечки ресурсов | Да, если забыть закрыть | Нет |
| Применимость к большим файлам | Да (файл в десятки ГБ можно обрабатывать построчно) | Нет (OutOfMemoryError для файлов, превышающих доступный heap) |

**Правильное использование Files.lines():**
```java
// Безопасно: try-with-resources гарантирует закрытие Stream
try (Stream<String> lines = Files.lines(Path.of("/var/log/app.log"))) {
    long errorCount = lines
        .filter(line -> line.contains("ERROR"))
        .count();
    System.out.println("Errors: " + errorCount);
}
// Здесь FileChannel уже закрыт
```

**Опасный антипаттерн:**
```java
// Утечка! Stream не закрывается при выбросе исключения или по завершению
Stream<String> lines = Files.lines(Path.of("/data/huge.csv"));
lines.forEach(this::process);
// FileChannel может остаться открытым
```

**Когда что выбирать:**

- `Files.lines()` с try-with-resources — для больших файлов, для потоковой обработки (filter/map/count), когда важна экономия памяти.
- `Files.readAllLines()` — для небольших конфигурационных файлов или когда нужен случайный доступ к строкам (по индексу через `List`).

**Расхождение источников**: Javadoc Java 8 говорит просто «the returned stream encapsulates a Reader», тогда как Javadoc Java 11+ явно добавляет: «The returned stream contains a reference to an open file. The file is closed by closing the stream.» Суть не изменилась, но Java 11+ документирует требование закрытия более явно.
### Вопрос 43. Что такое Charset, CharsetEncoder и CharsetDecoder в пакете java.nio.charset? Какие действия при ошибках кодирования/декодирования поддерживает CodingErrorAction и как их настроить?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CharsetEncoder (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/charset/CharsetEncoder.html)

`CharsetEncoder` — движок, преобразующий последовательности 16-битных Unicode-символов в байтовые последовательности в конкретной кодировке. Типовой цикл работы:

1. `reset()` — сброс внутреннего состояния.
2. Вызов `encode(CharBuffer in, ByteBuffer out, false)` — ноль или более раз для промежуточных данных.
3. Финальный вызов `encode(CharBuffer in, ByteBuffer out, true)` — с признаком окончания ввода.
4. `flush(ByteBuffer out)` — вывод оставшегося внутреннего состояния.

Два вида ошибок при кодировании:
- **Malformed-input** — входная последовательность символов не является допустимой 16-битной Unicode-последовательностью.
- **Unmappable-character** — символ является корректным Unicode, но не может быть отображён в байтовую последовательность целевой кодировки.

Действия при ошибках задаются константами `CodingErrorAction`:

| Константа | Поведение |
|-----------|-----------|
| `IGNORE`  | Молча пропустить ошибочный ввод |
| `REPLACE` | Заменить ошибочный ввод байтами замены (по умолчанию `{(byte)'?'}`) |
| `REPORT`  | Вернуть объект `CoderResult` с описанием ошибки (действие по умолчанию) |

Настройка через fluent-API:

```java
CharsetEncoder encoder = StandardCharsets.UTF_8.newEncoder();
encoder.onMalformedInput(CodingErrorAction.REPLACE)
       .onUnmappableCharacter(CodingErrorAction.IGNORE)
       .replaceWith(new byte[]{(byte)'?'});
```

`CharsetDecoder` — зеркальный движок: преобразует байты в Unicode-символы. Замена для декодера по умолчанию — строка `"�"` (символ Unicode replacement character). Настройка аналогична:

```java
CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
decoder.onMalformedInput(CodingErrorAction.REPLACE)
       .onUnmappableCharacter(CodingErrorAction.REPLACE)
       .replaceWith("�");
```

`Charset` — абстрактный класс, фабрика для энкодера и декодера. Lookup производится через `Charset.forName("UTF-8")` или через константы `StandardCharsets.UTF_8`. Метод `newEncoder()` возвращает `CharsetEncoder`, `newDecoder()` — `CharsetDecoder`.

#### Ответ от Claude

**Charset** (`java.nio.charset.Charset`) — абстрактный класс, представляющий именованное отображение между Unicode code unit и байтовыми последовательностями. Является потокобезопасной фабрикой:

```java
Charset utf8 = Charset.forName("UTF-8");       // по имени или псевдониму
Charset latin1 = StandardCharsets.ISO_8859_1;  // через константы (Java 7+)
CharsetEncoder enc = utf8.newEncoder();
CharsetDecoder dec = utf8.newDecoder();
```

Вспомогательные методы: `Charset.isSupported(name)`, `Charset.availableCharsets()`, `Charset.defaultCharset()`.

---

**CharsetEncoder** преобразует `CharBuffer` → `ByteBuffer`. Каждый экземпляр не является потокобезопасным (stateful). Методы конфигурации возвращают `this`, поддерживая chaining:

```java
CharsetEncoder encoder = StandardCharsets.UTF_8.newEncoder()
    .onMalformedInput(CodingErrorAction.REPORT)
    .onUnmappableCharacter(CodingErrorAction.REPLACE)
    .replaceWith(new byte[]{0x3F}); // '?'
```

Метод `encode(CharBuffer in, ByteBuffer out, boolean endOfInput)` возвращает `CoderResult`:
- `CoderResult.UNDERFLOW` — ввод исчерпан, всё обработано.
- `CoderResult.OVERFLOW` — выходной буфер заполнен, нужен flush и новый буфер.
- Ошибочный результат — если `CodingErrorAction.REPORT` и обнаружена ошибка.

---

**CharsetDecoder** преобразует `ByteBuffer` → `CharBuffer`. Три вида ошибок декодирования совпадают с кодировщиком. Замена по умолчанию — строка `"�"` (U+FFFD, Unicode Replacement Character).

```java
CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder()
    .onMalformedInput(CodingErrorAction.IGNORE)
    .onUnmappableCharacter(CodingErrorAction.REPLACE);
```

Удобный метод для одноразового декодирования: `decoder.decode(ByteBuffer)` бросает `CharacterCodingException` при `CodingErrorAction.REPORT`.

---

**CodingErrorAction** — не enum, а класс с тремя публичными статическими константами:

| Константа | Encoder | Decoder |
|-----------|---------|---------|
| `IGNORE`  | Пропустить ошибочные байты/символы без замены | То же |
| `REPLACE` | Вставить `replacement` (байты для enc, строку для dec) | То же |
| `REPORT`  | Вернуть `CoderResult` / бросить `CharacterCodingException` | То же |

**Значения по умолчанию** (подтверждено официальной документацией): оба действия — `REPORT` для `CharsetEncoder`; для `CharsetDecoder` — тоже `REPORT`. Замена у `CharsetEncoder` по умолчанию — `{(byte)'?'}`, у `CharsetDecoder` — `"�"`.

**Практический паттерн** — «мягкое» декодирование произвольных байт:

```java
String safeDecodeBytes(byte[] raw) throws IOException {
    CharsetDecoder dec = StandardCharsets.UTF_8.newDecoder()
        .onMalformedInput(CodingErrorAction.REPLACE)
        .onUnmappableCharacter(CodingErrorAction.REPLACE);
    return dec.decode(ByteBuffer.wrap(raw)).toString();
}
```

**Расхождение между источниками:** официальная документация Oracle называет REPORT действием по умолчанию для обоих типов ошибок. Ряд учебных ресурсов (GeeksforGeeks) умалчивает о дефолте или неверно указывает REPLACE — это ошибка; приоритет — официальная документация.

---

### Вопрос 44. В чём опасность десериализации данных из ненадёжного источника через ObjectInputStream? Что такое «gadget chain» в контексте уязвимостей Java-десериализации и какие реальные CVE связаны с этой проблемой?

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Deserialization of untrusted data — OWASP Foundation](https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data)

При десериализации ненадёжных данных через `ObjectInputStream` возникают три категории угроз:

1. **Атаки на доступность (DoS).** Десериализация может быть направлена на исчерпание ресурсов. Например, `ArrayList` с размером `Integer.MAX_VALUE` вызовет `OutOfMemoryError` ещё до обработки элементов. Рекурсивные графы объектов или бесконечные потоки данных могут завесить JVM.

2. **Выполнение произвольного кода (RCE).** Злоумышленники используют объекты, чей собственный десериализационный код (`readObject()`) злоупотребляет логикой существующих классов приложения. Исследователи показали, что сложные графы объектов позволяют достичь RCE на большинстве Java-приложений.

3. **Обход авторизации.** Десериализованные объекты могут содержать атрибуты, влияющие на проверки авторизации, — злоумышленник подменяет состояние объекта.

Как конкретный исторический пример упомянут **CVE-2011-2092** (Adobe BlazeDS): уязвимость позволяла указывать произвольные классы для десериализации, что использовалось для создания объектов типа `JFrame` с командой выхода из JVM. Среди известных жертв — WebLogic, WebSphere, JBoss, Jenkins, OpenNMS.

Концепция «gadget» аналогична гаджетам Return-Oriented-Programming: это существующие классы JVM, которые при цепочном вызове в процессе десериализации выполняют нежелательные действия без единой строчки явно вредоносного кода.

#### Ответ от Claude

**Механизм угрозы**

Java-десериализация через `ObjectInputStream.readObject()` восстанавливает граф объектов из байтового потока. Процесс не проверяет источник данных и не валидирует типы заранее — он доверяет потоку безоговорочно. Когда поток поступает от злоумышленника, открываются следующие векторы атак:

- **RCE через gadget chain** — наиболее опасный вектор.
- **DoS** — через `OutOfMemoryError`, Stack Overflow, бесконечные циклы.
- **Обход авторизации** — через подмену полей объектов (роли, флаги, идентификаторы).

---

**Gadget chain (цепочка гаджетов)**

Гаджет — это serializable-класс из classpath, метод которого (чаще всего `readObject()`, `hashCode()`, `equals()`, `compareTo()`) имеет «полезные для злоумышленника» побочные эффекты: рефлексивный вызов метода, выполнение команды ОС, запись в файловую систему.

Атака строится так:
1. Злоумышленник формирует сериализованный байтовый поток вручную (без запуска приложения).
2. В корне графа объектов — serializable-класс из стандартной библиотеки или известной зависимости (`PriorityQueue`, `HashMap`, `AnnotationInvocationHandler`), который в `readObject()` вызывает метод на дочернем объекте.
3. Дочерний объект — следующий гаджет, вызывающий следующий, и так до «последнего звена» — объекта, исполняющего произвольный код.

**Пример: CommonsCollections1 (Apache Commons Collections 3.x)**

```
readObject() на PriorityQueue
  → compareTo() на TransformingComparator
    → transform() на ChainedTransformer
      → InvokerTransformer.transform() #1: Runtime.class.getMethod("exec")
        → InvokerTransformer.transform() #2: method.invoke(Runtime.getRuntime())
          → InvokerTransformer.transform() #3: runtime.exec("calc.exe")
```

`InvokerTransformer` из `commons-collections` позволяет рефлексивно вызывать произвольный метод на произвольном объекте. Именно это делает его опасным гаджетом.

---

**Реальные CVE**

| CVE | Продукт | CVSS | Суть |
|-----|---------|------|------|
| CVE-2015-4852 | Oracle WebLogic Server (10.3.6, 12.1.x, 12.2.x) | 9.8 Critical | Гаджет-цепочка через Commons Collections в T3-протоколе, порт 7001. Удалённый RCE без аутентификации. |
| CVE-2015-7501 | JBoss / Red Hat | 9.8 Critical | Аналогичная цепочка через Commons Collections в EAP. |
| CVE-2015-8103 | Jenkins | 9.8 Critical | Удалённый RCE через десериализацию в CLI-интерфейсе. |
| CVE-2015-7450 | IBM WebSphere | 9.8 Critical | RCE через gadget chain в Commons Collections. |
| CVE-2015-5254 | Apache ActiveMQ | 9.8 Critical | Небезопасная десериализация в OpenWire-протоколе. |
| CVE-2018-2628 | Oracle WebLogic | 9.8 Critical | Новая цепочка через T3; обход чёрного списка патча CVE-2015-4852. |
| CVE-2020-2555 | Oracle WebLogic | 9.8 Critical | Обход фильтра через gadget в `coherence.jar`. |
| CVE-2011-2092 | Adobe BlazeDS | N/A | Первая публично известная Java-десериализация: произвольный класс через AMF. |

Инструмент **ysoserial** (Frohoff, 2015) автоматизирует генерацию эксплойт-пейлоадов для 34+ различных gadget chain: CommonsCollections 1–7, Spring, Hibernate, Groovy, AspectJWeaver и др.

---

**Причины широкого распространения**

- `ObjectInputStream` не поддерживает allowlist классов «из коробки» (до JEP 290 / Java 9).
- Библиотеки с уязвимыми гаджетами (commons-collections, spring-core, groovy) транзитивно присутствуют в большинстве enterprise Java-проектов.
- Разработчики исторически не считали десериализацию поверхностью атаки.

**Защитные меры**

1. Включить `ObjectInputFilter` (JEP 290, Java 9+) с allowlist только известных классов.
2. Полностью отказаться от нативной Java-сериализации — использовать JSON (Jackson, Gson) или Protobuf.
3. Обновить уязвимые зависимости (commons-collections 3.2.2+, 4.1+).
4. Изолировать сервисы, принимающие сериализованные данные, сетевыми правилами.
5. Применять статический анализ (SpotBugs с плагином find-sec-bugs, Semgrep).

---

### Вопрос 45. Что такое ObjectInputFilter (JEP 290, Java 9+) и как он помогает защититься от атак через десериализацию? Объясни разницу между pattern-based фильтром и custom-реализацией интерфейса ObjectInputFilter.

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Serialization Filtering — Java SE 8 Serialization Specification (backport guide), docs.oracle.com](https://docs.oracle.com/javase/8/docs/technotes/guides/serialization/filters/serialization-filtering.html)

`ObjectInputFilter` — интерфейс механизма фильтрации входящих потоков сериализованных объектов. Добавлен в Java 9 через JEP 290, затем бэкпортирован в Java 6, 7 и 8 (через обновления безопасности). Фильтр вызывается **до** материализации объекта — т.е. до выполнения любого прикладного кода.

Интерфейс определяет единственный метод:

```java
public interface ObjectInputFilter {
    Status checkInput(FilterInfo filterInfo);

    enum Status { UNDECIDED, ALLOWED, REJECTED }

    interface FilterInfo {
        Class<?> serialClass();   // класс объекта (null — при проверке лимитов)
        long arrayLength();        // длина массива, -1 если не массив
        long depth();              // глубина вложенности (начиная с 1)
        long references();         // число ссылок на уже прочитанные объекты
        long streamBytes();        // байт прочитано из потока
    }
}
```

**Pattern-based фильтры** задаются строкой — без изменения кода приложения.

Синтаксис:
- Паттерны разделяются `;`.
- Пробелы значимы (являются частью паттерна).
- `!pattern` — отклонить класс, соответствующий паттерну.
- `pkg.*` — классы пакета `pkg` (без подпакетов).
- `pkg.**` — классы `pkg` и всех подпакетов.
- Лимит-паттерны: `maxarray=N`, `maxdepth=N`, `maxrefs=N`, `maxbytes=N`.
- Лимиты вычисляются первыми, независимо от порядка в строке.
- Первое совпадение определяет результат.

Примеры:
```
# Разрешить только java.time и java.util, запретить остальное
maxdepth=20;maxarray=100000;java.time.*;java.util.*;!*

# Запретить конкретный класс, разрешить пакет
!com.evil.Exploit;com.example.*;!*
```

Установка через системное свойство:
```bash
java -Djdk.serialFilter=maxdepth=10;com.example.*;!* MyApp
```

Установка через Security Property (глобально для JVM):
```properties
# $JAVA_HOME/conf/security/java.security
jdk.serialFilter=maxdepth=10;com.example.*;!*
```

Установка через API для конкретного потока:
```java
ObjectInputStream ois = new ObjectInputStream(inputStream);
ois.setObjectInputFilter(
    ObjectInputFilter.Config.createFilter("java.time.*;!*")
);
```

**Custom-реализация** позволяет то, что недоступно pattern-фильтру: проверка по суперклассу/интерфейсу, сохранение состояния между вызовами, комбинирование нескольких условий.

```java
class FilterNumber implements ObjectInputFilter {
    @Override
    public Status checkInput(FilterInfo info) {
        Class<?> clazz = info.serialClass();
        if (clazz != null) {
            return Number.class.isAssignableFrom(clazz)
                ? Status.ALLOWED
                : Status.REJECTED;
        }
        return Status.UNDECIDED;  // проверка лимитов — пропустить
    }
}
ois.setObjectInputFilter(new FilterNumber());
```

Глобальная установка (один раз на JVM):
```java
ObjectInputFilter.Config.setSerialFilter(info ->
    info.depth() > 10 ? Status.REJECTED : Status.UNDECIDED
);
```

#### Ответ от Claude

**JEP 290 и ObjectInputFilter: суть**

JEP 290 (интегрирован в Java 9, бэкпортирован в 6u141, 7u131, 8u121) вводит механизм фильтрации входящих сериализационных потоков. Цель — дать разработчику инструмент для ограничения того, **какие классы** могут быть десериализованы, а также для контроля **ресурсов**: размеров массивов, глубины вложенности, числа ссылок, объёма потока. Фильтр вызывается JVM **до инстанциирования объекта** и до выполнения пользовательского `readObject()`, что блокирует gadget chains ещё на входе.

---

**Интерфейс ObjectInputFilter**

```java
// java.io.ObjectInputFilter (Java 9+)
public interface ObjectInputFilter {
    Status checkInput(FilterInfo filterInfo);

    enum Status {
        UNDECIDED,  // нет решения — продолжить к следующему фильтру
        ALLOWED,    // объект принят
        REJECTED    // объект отклонён: бросается InvalidClassException
    }

    interface FilterInfo {
        Class<?> serialClass();  // null при проверке только метрик
        long arrayLength();       // -1 если не массив
        long depth();             // глубина вложенности, начиная с 1
        long references();        // число уже прочитанных ссылок
        long streamBytes();       // прочитано байт из потока
    }
}
```

Фильтр вызывается:
- Для каждого нового **уникального класса** (не для каждого экземпляра).
- Для каждого **суперкласса и интерфейса** десериализуемого объекта.
- Для каждого **массива** (с указанием длины).
- При каждой проверке **метрик** (depth, references, streamBytes).
- **Не вызывается** для примитивов и строк, закодированных непосредственно в потоке.

---

**Pattern-based фильтр**

Строковый паттерн преобразуется в `ObjectInputFilter` через `ObjectInputFilter.Config.createFilter(String pattern)`. Удобен, когда набор допустимых классов известен заранее и не требует логических условий.

Полный синтаксис:

```
<filter> ::= <item> (';' <item>)*
<item>   ::= <limit> | [!]<class-pattern>
<limit>  ::= 'maxarray=' N | 'maxdepth=' N | 'maxrefs=' N | 'maxbytes=' N

<class-pattern> ::=
    '*'             # любой класс
    'pkg.*'         # классы в пакете pkg (без подпакетов)
    'pkg.**'        # классы в pkg и всех подпакетах
    'ClassName'     # точное имя класса
    'module/pkg.*'  # с указанием модуля (JPMS)
```

Правила вычисления:
1. Лимиты проверяются **всегда первыми**, независимо от позиции в строке.
2. Паттерны классов — слева направо, первое совпадение — победитель.
3. Результат первого совпадения: `!pattern` → REJECTED, иначе → ALLOWED.
4. Если ни один паттерн не совпал — UNDECIDED.

Пример строгого allowlist:

```java
// Разрешить только LocalDateTime из java.time, запретить всё остальное
String pattern = "maxdepth=5;maxarray=1000;java.time.LocalDateTime;!*";
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(pattern);

ObjectInputStream ois = new ObjectInputStream(in);
ois.setObjectInputFilter(filter);
LocalDateTime dt = (LocalDateTime) ois.readObject();
```

**Ограничения pattern-based фильтра:**
- Нельзя проверять по суперклассу/интерфейсу (только по точному имени класса).
- Нельзя менять решение в зависимости от **других уже прочитанных объектов** (нет состояния).
- Нельзя комбинировать условия (например, «разрешить массив длиной до 100 только если класс — `String`»).

---

**Custom ObjectInputFilter**

Реализация интерфейса вручную снимает все ограничения pattern-фильтра.

```java
// Пример: разрешить только подклассы Number; при превышении depth > 3 — REJECTED
public class StrictNumberFilter implements ObjectInputFilter {
    @Override
    public Status checkInput(FilterInfo info) {
        if (info.depth() > 3) return Status.REJECTED;

        Class<?> clazz = info.serialClass();
        if (clazz == null) return Status.UNDECIDED;  // вызов только для метрик

        if (Number.class.isAssignableFrom(clazz)) return Status.ALLOWED;
        return Status.REJECTED;
    }
}

// Применение к потоку
ois.setObjectInputFilter(new StrictNumberFilter());
```

Кастомный фильтр **через лямбду**:

```java
ObjectInputFilter.Config.setSerialFilter(info -> {
    if (info.depth() > 10) return Status.REJECTED;
    if (info.references() > 500) return Status.REJECTED;
    Class<?> c = info.serialClass();
    if (c != null && c.getClassLoader() != ClassLoader.getSystemClassLoader()) {
        return Status.REJECTED; // запретить классы не из bootstrap/system CL
    }
    return Status.UNDECIDED;
});
```

---

**Разница между pattern-based и custom фильтром**

| Критерий | Pattern-based | Custom ObjectInputFilter |
|----------|--------------|--------------------------|
| Настройка | Строка (системное свойство, файл конфигурации) | Код Java |
| Проверка по суперклассу/интерфейсу | Нет | Да |
| Сохранение состояния между вызовами | Нет | Да |
| Комбинирование нескольких условий | Ограниченно (AND через несколько паттернов) | Произвольная логика |
| Применение без изменения кода | Да (`-Djdk.serialFilter=...`) | Нет |
| Гибкость | Низкая | Полная |

---

**Уровни применения фильтров**

1. **JVM-wide (глобальный)** — через `ObjectInputFilter.Config.setSerialFilter(filter)` или свойство `jdk.serialFilter`. Применяется ко всем `ObjectInputStream` в JVM.
2. **Per-stream (потоковый)** — через `ois.setObjectInputFilter(filter)`. Устанавливается **до** первого `readObject()`. Переопределяет глобальный фильтр для данного потока.

**Объединение фильтров** (Java 17+, JEP 415):

```java
ObjectInputFilter merged = ObjectInputFilter.merge(globalFilter, streamFilter);
ois.setObjectInputFilter(merged);
```

`merge()` возвращает REJECTED, если хоть один из двух фильтров вернул REJECTED; ALLOWED — если хоть один вернул ALLOWED и ни один — REJECTED; UNDECIDED — если оба UNDECIDED.

---

**Лучшие практики**

- Всегда завершать pattern-строку `!*` — это явный запрет всего, что не попало в allowlist.
- Устанавливать фильтр **сразу после создания** `ObjectInputStream`, до первого `readObject()`.
- Для production-систем предпочитать allowlist (ALLOWED для явно известных классов + `!*`) вместо denylist.
- Не полагаться только на `ObjectInputFilter`: в идеале отказаться от нативной сериализации полностью.

---
### Вопрос 46. Почему нативная Java-сериализация считается проблематичной для продакшн-систем, и какие альтернативы (Kryo, Protobuf, Avro) её заменяют? По каким критериям выбирать между ними?

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [An Introduction and Comparison of Several Common Java Serialization Frameworks — Alibaba Cloud Community](https://www.alibabacloud.com/blog/an-introduction-and-comparison-of-several-common-java-serialization-frameworks_597900)

**Производительность (10 млн итераций на одном объекте):**

| Фреймворк | Время (мс) | Размер (байт) |
|-----------|-----------|--------------|
| Native Java | 38 952 | 432 |
| Protobuf | 14 235 | 192 |
| Kryo (оптимизир.) | 11 799 | 120 |
| Avro | 26 565 | 111 |

**Характеристики фреймворков:**

| Фреймворк | Схема | Кросс-языковой | Простота |
|-----------|-------|----------------|---------|
| Kryo | Нет | Только JVM | Простой API |
| Protobuf | Обязательна (IDL) | Отличная (10+ языков) | Средняя |
| Avro | Обязательна (JSON) | Хорошая (6+ языков) | Сложная |
| Native Java | Нет | Только Java | Сложная |

**Рекомендации по выбору:**
- Приоритет скорости — Kryo (или FST).
- Критичен размер сообщения — Avro или Kryo с pre-registration.
- Нужна межъязыковая совместимость — Protobuf.

#### Ответ от Claude

**Проблемы нативной Java-сериализации в продакшне**

1. **Безопасность (главная причина отказа).** Механизм десериализации Java реконструирует произвольные объектные графы до того, как приложение получает над ними контроль. Это открывает вектор атак через «гаджет-цепочки» — последовательности вызовов методов существующих классов в classpath (Apache Commons Collections, Spring, Groovy и др.), которые при специально сформированном потоке приводят к Remote Code Execution (RCE). Уязвимость фигурирует в OWASP Top 10 (A08:2025 — Software and Data Integrity Failures). Исторически пострадали WebLogic, WebSphere, JBoss, Jenkins. OWASP прямо рекомендует заменять нативную десериализацию на JSON или другие структурированные форматы, которые воссоздают только данные, но не произвольный код.

2. **Производительность.** По замерам из авторитетных источников нативная сериализация работает в 3–4 раза медленнее Protobuf и в ~3,3 раза медленнее Kryo. Размер потока у нативного механизма наибольший (432 байта против 120 у Kryo), что увеличивает нагрузку на сеть и I/O. DZone фиксирует разницу в ~4 000 раз по времени доступа по сравнению с прямым обращением к памяти.

3. **Хрупкость версионирования.** Любое изменение сигнатуры класса (добавление/удаление поля, переименование) при отсутствии явного `serialVersionUID` приводит к `InvalidClassException` при попытке прочитать старые данные. Поддерживать совместимость форматов вручную крайне неудобно.

4. **Отсутствие кросс-языковой поддержки.** Формат жёстко привязан к JVM и не позволяет читать данные из других языков (Go, Python, C++).

5. **Скрытая сериализация транзитивных зависимостей.** Все объекты в графе должны реализовывать `Serializable`; иначе — `NotSerializableException`. Это проникает в архитектуру и создаёт нежелательные связи.

---

**Альтернативы и критерии выбора**

**Kryo**
- Самый быстрый на JVM, минимальный размер потока.
- Не требует схемы; регистрация классов опциональна (но рекомендуется для безопасности и производительности).
- Только JVM — нет межъязыковой совместимости.
- Нет встроенной поддержки эволюции схемы (необходима осторожность при изменении классов).
- **Применять:** кэши в памяти (Hazelcast, Apache Spark, Flink), сессионные данные, JVM-to-JVM RPC.

**Protocol Buffers (Protobuf)**
- Схема описывается в `.proto`-файле; из неё генерируется код для 10+ языков.
- Отличная поддержка эволюции схемы (поля нумерованы; добавление/удаление опциональных полей совместимо).
- Компактный бинарный формат, хорошая скорость.
- Требует этап кодогенерации, сложнее внедрить в существующий код.
- **Применять:** межсервисное взаимодействие (gRPC), REST API с бинарным телом, публичные контракты между командами.

**Apache Avro**
- Схема описывается в JSON; схема хранится вместе с данными или в Schema Registry.
- Лучшая интеграция с экосистемой Apache (Kafka, Hadoop, Spark): Confluent Schema Registry, Kafka Avro SerDe.
- Наименьший размер потока при наличии схемы на стороне чтения.
- Поддерживает backward/forward compatibility.
- Сложнее в настройке, требует Schema Registry для production-использования с Kafka.
- **Применять:** потоковая обработка данных (Kafka topics), data pipelines в Hadoop/Spark, системы event sourcing с долгосрочным хранением.

**Сводная таблица критериев выбора:**

| Критерий | Kryo | Protobuf | Avro |
|----------|------|----------|------|
| Максимальная скорость | ✓ лучший | хорошо | медленнее |
| Минимальный размер | ✓ (с регистрацией) | хорошо | ✓ лучший |
| Кросс-языковой | нет | ✓ отлично | хорошо |
| Эволюция схемы | слабая | ✓ хорошая | ✓ отличная |
| Kafka/Big Data | нет | возможно | ✓ нативно |
| Простота старта | высокая | средняя | сложная |

**Вывод:** нативную Java-сериализацию в продакшне рекомендуется не использовать по соображениям безопасности и производительности. Джошуа Блох в Effective Java (3-е издание) прямо советует рассматривать альтернативные механизмы для всех новых систем.

---

### Вопрос 47. Что такое writeReplace() в механизме сериализации Java? Чем он отличается от writeObject()? Приведи практический сценарий, где writeReplace() незаменим.

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Java Object Serialization Specification — Output Classes (Oracle, Java SE 11)](https://docs.oracle.com/en/java/javase/11/docs/specs/serialization/output.html)

**Сигнатуры методов:**

```java
// writeReplace — любой модификатор доступа
ANY-ACCESS-MODIFIER Object writeReplace() throws ObjectStreamException;

// writeObject — только private
private void writeObject(ObjectOutputStream stream) throws IOException;
```

**Порядок выполнения при сериализации объекта:**

1. `writeReplace()` вызывается первым (шаг 8.1 в спецификации).
2. `writeObject()` вызывается позднее (шаг 13.1) для записи содержимого объекта.

**Ключевые отличия:**

| Аспект | writeReplace() | writeObject() |
|--------|----------------|---------------|
| Цель | Заменить объект до сериализации | Управлять записью полей объекта |
| Возвращаемое значение | Объект-замена | void |
| Момент вызова | До сериализации | Во время сериализации |
| Ответственность | Выбрать, ЧТО сериализовать | Описать, КАК сериализовать |

**Важное ограничение `writeReplace()`:** возвращаемый объект должен быть совместим по типу со всеми ссылками на исходный; иначе при десериализации возникнет `ClassCastException`.

#### Ответ от Claude

**writeReplace()**

Метод `writeReplace()` перехватывает процесс сериализации на самом раннем этапе — до того как `ObjectOutputStream` начинает записывать класс и поля. Он позволяет объекту указать «заместителя» (proxy), который будет записан в поток вместо него. Спецификация определяет сигнатуру:

```java
ANY-ACCESS-MODIFIER Object writeReplace() throws ObjectStreamException;
```

Метод может иметь любой модификатор доступа (`private`, `protected`, `public`, package-private). Если он объявлен в суперклассе, подклассы наследуют его, если не переопределят.

**writeObject()**

```java
private void writeObject(ObjectOutputStream stream) throws IOException;
```

Вызывается на том же объекте после записи метаданных класса. Управляет тем, *как* пишутся поля: можно вызвать `defaultWriteObject()` для стандартного поведения, а затем дописать дополнительные данные. Метод должен быть `private` и не возвращает объект-замену.

**Разница:** `writeReplace()` отвечает на вопрос «*что* сериализовать», `writeObject()` — «*как* сериализовать поля того же объекта».

---

**Практический сценарий: Serialization Proxy Pattern (Effective Java, Item 90)**

Это самый важный сценарий применения `writeReplace()`, описанный Джошуа Блохом. Паттерн незаменим для классов с инвариантами, которые должны проверяться при каждом создании объекта.

**Проблема:** стандартная десериализация создаёт объект в обход конструктора («внеязыковой» механизм). Проверки инвариантов, прописанные в конструкторе, не выполняются. Злоумышленник может подать поддельный поток байт и получить объект в недопустимом состоянии.

**Решение:**

```java
public final class Period implements Serializable {
    private final Date start;
    private final Date end;

    public Period(Date start, Date end) {
        // Инвариант: start < end
        if (start.compareTo(end) > 0)
            throw new IllegalArgumentException("start > end");
        this.start = new Date(start.getTime());
        this.end   = new Date(end.getTime());
    }

    // 1. writeReplace подменяет Period на SerializationProxy
    private Object writeReplace() {
        return new SerializationProxy(this);
    }

    // 2. Прямая десериализация Period запрещена
    private void readObject(ObjectInputStream s) throws InvalidObjectException {
        throw new InvalidObjectException("Proxy required");
    }

    // Внутренний прокси-класс
    private static class SerializationProxy implements Serializable {
        private static final long serialVersionUID = 1L;
        private final Date start;
        private final Date end;

        SerializationProxy(Period p) {
            this.start = p.start;
            this.end   = p.end;
        }

        // 3. readResolve создаёт Period через конструктор — инварианты проверяются
        private Object readResolve() {
            return new Period(start, end);
        }
    }
}
```

**Почему `writeReplace()` здесь незаменим:**
- Именно он переключает поток записи с `Period` на `SerializationProxy` — без него прокси-паттерн невозможен.
- `writeObject()` не подходит: он работает с тем же объектом и не может заменить его другим типом в потоке.
- Атака через подложный поток `Period` заблокирована `readObject()`, который бросает исключение.
- При десериализации `SerializationProxy.readResolve()` вызывает конструктор `Period`, поэтому все проверки инвариантов гарантированно выполняются.

**Другие сценарии применения `writeReplace()`:**
- **Singleton:** `writeReplace()` возвращает специальный токен, `readResolve()` возвращает единственный экземпляр, предотвращая появление клонов через десериализацию.
- **EnumSet:** реализация возвращает `RegularEnumSet` или `JumboEnumSet` в зависимости от числа элементов; `writeReplace()` позволяет при десериализации выбрать правильную конкретную реализацию через фабричный метод.
- **Сжатие/шифрование данных:** `writeReplace()` возвращает обёртку, содержащую зашифрованные или сжатые байты вместо оригинального объекта.

---

### Вопрос 48. Что такое serialPersistentFields и для чего используется массив ObjectStreamField[]? Как с его помощью можно сериализовать поле под другим именем или типом по сравнению с реальным полем класса?

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Java Object Serialization Specification — Example of Serializable Fields (Oracle, Java SE 17)](https://docs.oracle.com/en/java/javase/17/docs/specs/serialization/examples.html)

Спецификация описывает `serialPersistentFields` как механизм явного управления тем, какие поля попадают в поток сериализации. Объявление:

```java
private static final ObjectStreamField[] serialPersistentFields = { ... };
```

**Пример из спецификации — класс `File` с альтернативным внутренним представлением:**

Реальное поле класса — `String[] pathcomponents` (массив). Сериализованное поле — `path` типа `String` (одна строка с разделителями). Имена и типы полностью различаются.

```java
class File implements java.io.Serializable {
    private String[] pathcomponents;

    /** @serialField path String Path components separated by separator. */
    private static final ObjectStreamField[] serialPersistentFields
        = { new ObjectStreamField("path", String.class) };

    private void writeObject(ObjectOutputStream s) throws IOException {
        ObjectOutputStream.PutField fields = s.putFields();
        StringBuffer str = new StringBuffer();
        for (int i = 0; i < pathcomponents.length; i++) {
            str.append(separator);
            str.append(pathcomponents[i]);
        }
        fields.put("path", str.toString());
        s.writeFields();
        s.writeChar(separatorChar);
    }

    private void readObject(ObjectInputStream s) throws IOException {
        ObjectInputStream.GetField fields = s.readFields();
        String path = (String) fields.get("path", null);
        char sep = s.readChar();
        // разбираем path по разделителю и заполняем pathcomponents
    }
}
```

Этот паттерн позволяет изменить внутреннее представление класса, сохраняя совместимость сериализованного формата.

#### Ответ от Claude

**Что такое `serialPersistentFields`**

`serialPersistentFields` — специальное поле класса, которое явно задаёт «сериализованную форму» (serialized form) — описание того, что именно попадает в поток байт. Без него механизм сериализации автоматически использует все нестатические нетранзитные поля.

Требования к объявлению (Oracle Spec § 1.5):
- модификаторы: `private static final` (обязательно все три);
- тип: `ObjectStreamField[]`;
- если хоть одно условие нарушено — поле игнорируется и применяется поведение по умолчанию.

```java
private static final ObjectStreamField[] serialPersistentFields = {
    new ObjectStreamField("fieldName", FieldType.class),
    new ObjectStreamField("anotherField", int.class, true) // unshared
};
```

**Класс `ObjectStreamField`**

Конструкторы (из `java.io.ObjectStreamField`, начиная с Java 1.2):

```java
public ObjectStreamField(String name, Class<?> type)
public ObjectStreamField(String name, Class<?> type, boolean unshared)
```

- `name` — имя поля **в потоке сериализации** (не обязано совпадать с именем реального поля);
- `type` — тип поля **в потоке** (не обязан совпадать с реальным типом);
- `unshared = true` — значение пишется/читается как unshared-объект (`writeUnshared`/`readUnshared`), то есть без обмена ссылками.

**Главная возможность:** поскольку имя и тип в `ObjectStreamField` — это имя и тип *в потоке*, а не в классе, их можно произвольно отличать от реальных полей. Связь между реальными полями и сериализованными полями устанавливается вручную в `writeObject`/`readObject` через API `PutField`/`GetField`.

---

**Как сериализовать поле под другим именем**

Предположим, в версии 1 класс содержал `String userName`, а в версии 2 поле переименовано в `String login`. Нужно сохранить совместимость потока (старый код писал `"userName"`, новый должен читать его).

```java
public class UserAccount implements Serializable {
    private static final long serialVersionUID = 1L;

    // Реальное поле — "login"
    private String login;

    // В потоке поле называется "userName" (старое имя)
    private static final ObjectStreamField[] serialPersistentFields = {
        new ObjectStreamField("userName", String.class)
    };

    private void writeObject(ObjectOutputStream out) throws IOException {
        ObjectOutputStream.PutField fields = out.putFields();
        fields.put("userName", login); // реальное поле "login" → поток "userName"
        out.writeFields();
    }

    private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
        ObjectInputStream.GetField fields = in.readFields();
        this.login = (String) fields.get("userName", null); // поток "userName" → поле "login"
    }
}
```

---

**Как сериализовать поле под другим типом**

Аналогично примеру из спецификации Oracle: внутри класс хранит `String[] pathcomponents`, а в потоке этот массив представлен одной строкой `String path`:

```java
private static final ObjectStreamField[] serialPersistentFields = {
    new ObjectStreamField("path", String.class) // String, а не String[]
};

private void writeObject(ObjectOutputStream s) throws IOException {
    ObjectOutputStream.PutField fields = s.putFields();
    // Склеиваем массив в строку
    fields.put("path", String.join(separator, pathcomponents));
    s.writeFields();
}

private void readObject(ObjectInputStream s) throws IOException {
    ObjectInputStream.GetField fields = s.readFields();
    String path = (String) fields.get("path", null);
    // Разбиваем строку обратно в массив
    this.pathcomponents = path.split(Pattern.quote(separator));
}
```

---

**Что происходит с полями, отсутствующими в `serialPersistentFields`**

Если реальное поле класса не объявлено в `serialPersistentFields`, оно не попадает в поток — даже если оно не помечено `transient`. Таким образом, `serialPersistentFields` является альтернативой массовым пометкам `transient`: можно разрешить сериализацию только явно перечисленных полей.

**Применение в эволюции схемы**

Этот механизм позволяет менять внутреннее представление класса (например, заменить `Hashtable` на `HashMap`), сохраняя сериализованную форму неизменной. Связь «реальные поля ↔ поток» полностью описывается парой `writeObject`/`readObject`, а `serialPersistentFields` фиксирует публичный контракт сериализованного формата независимо от реализации.

**Расхождение между источниками:** спецификация Oracle (Java SE 11 и Java SE 17) последовательна в описании механизма. Некоторые статьи ошибочно утверждают, что `serialPersistentFields` позволяет переименовать поле «автоматически» — это неверно: без явных `writeObject`/`readObject` с использованием `PutField`/`GetField` механизм переименования не работает; `serialPersistentFields` лишь объявляет контракт, а отображение пишется разработчиком вручную.
### Вопрос 49. Почему постоянная регистрация канала на SelectionKey.OP_WRITE в Selector является антипаттерном? Как правильно реализовать запись в неблокирующий SocketChannel, чтобы избежать busy-loop в цикле select()?

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Rox Java NIO Tutorial (rox-xmlrpc.sourceforge.net)](https://rox-xmlrpc.sourceforge.net/niotut/index.html)

Типичная ошибка — включить OP_WRITE в набор интересов ключа и оставить его там постоянно. Это приводит к тому, что поток, вызывающий select(), начинает крутиться вхолостую, потому что в 99% случаев сокетный канал готов к записи. Единственные исключения — момент установки соединения или ситуация, когда буфер отправки операционной системы заполнен. Если OP_WRITE всегда активен, Selector постоянно возвращает управление, обнаруживая ключ как «готовый к записи», и впустую тратит циклы процессора.

Правильный подход — **регистрировать OP_WRITE только тогда, когда есть данные для отправки**, а после успешной записи снова переключать канал обратно на OP_READ:

```java
// Поток-отправитель (не-selector-поток):
public void send(SocketChannel socket, byte[] data) {
    synchronized (changeRequests) {
        changeRequests.add(new ChangeRequest(
            socket, ChangeRequest.CHANGEOPS, SelectionKey.OP_WRITE));
        synchronized (pendingData) {
            List<ByteBuffer> queue = pendingData.computeIfAbsent(
                socket, k -> new ArrayList<>());
            queue.add(ByteBuffer.wrap(data));
        }
    }
    selector.wakeup(); // разбудить selector-поток
}

// В selector-потоке, после завершения записи:
if (queue.isEmpty()) {
    key.interestOps(SelectionKey.OP_READ); // снять OP_WRITE
}
```

Схема работы:
1. Данные для отправки помещаются в очередь `pendingData` (синхронизировано).
2. В список изменений `changeRequests` добавляется запрос на переключение интересов канала на OP_WRITE.
3. Вызывается `selector.wakeup()`, чтобы вывести selector-поток из блокировки.
4. Selector-поток читает `changeRequests`, устанавливает OP_WRITE, записывает данные.
5. Когда очередь опустела — устанавливает обратно OP_READ.

Это исключает холостой спин, поскольку OP_WRITE активен только в краткий период реальной передачи данных.

#### Ответ от Claude

**Почему постоянный OP_WRITE — антипаттерн**

`SelectionKey.OP_WRITE` сигнализирует, что канал готов принять данные (в буфер отправки ОС). Сокет почти всегда готов к записи: буфер отправки заполняется лишь при перегрузке сети или медленном получателе. Если OP_WRITE постоянно включён в interest set, `Selector.select()` немедленно возвращается на каждой итерации, не блокируясь вовсе. Результат — цикл превращается в busy-loop, который потребляет 100% CPU без полезной работы.

Это подтверждает и официальная документация Oracle (`SelectionKey` javadoc): канал попадает в ready-set по OP_WRITE, когда он «готов к записи, удалённая сторона закрыла соединение для записи или есть ожидающая ошибка». Первое условие выполняется почти всегда.

**Правильная реализация: регистрация OP_WRITE по требованию**

Ключевой принцип: **OP_WRITE регистрируется только при наличии данных в очереди, и снимается сразу после того, как очередь опустела.**

```java
// --- Selector-поток ---
while (true) {
    // Применяем накопленные изменения интересов
    synchronized (changeRequests) {
        for (ChangeRequest change : changeRequests) {
            SelectionKey key = change.socket.keyFor(selector);
            key.interestOps(change.ops);
        }
        changeRequests.clear();
    }

    selector.select(); // блокируется, пока нет событий

    Iterator<SelectionKey> keys = selector.selectedKeys().iterator();
    while (keys.hasNext()) {
        SelectionKey key = keys.next();
        keys.remove();

        if (key.isReadable()) {
            read(key);
        } else if (key.isWritable()) {
            write(key);
        }
    }
}

private void write(SelectionKey key) throws IOException {
    SocketChannel channel = (SocketChannel) key.channel();
    synchronized (pendingData) {
        List<ByteBuffer> queue = pendingData.get(channel);
        while (!queue.isEmpty()) {
            ByteBuffer buf = queue.get(0);
            channel.write(buf);
            if (buf.remaining() > 0) {
                // Буфер ОС заполнен — выходим, ждём следующего OP_WRITE
                break;
            }
            queue.remove(0);
        }
        if (queue.isEmpty()) {
            // Все данные отправлены — убираем OP_WRITE
            key.interestOps(SelectionKey.OP_READ);
        }
    }
}
```

**Обработка частичной записи**

`SocketChannel.write(ByteBuffer)` в неблокирующем режиме может записать меньше байт, чем запрошено (вернёт значение < `buf.remaining()` до вызова). В этом случае нужно сохранить остаток в буфере и вернуть управление: Selector разбудит поток снова, когда буфер ОС освободится, и запись продолжится.

**Итоговые правила**

| Ситуация | Действие |
|---|---|
| Появились данные для отправки | Добавить в очередь, запросить OP_WRITE, вызвать `selector.wakeup()` |
| `channel.write()` записал все данные | Снять OP_WRITE, переключить на OP_READ |
| `channel.write()` записал часть данных | Оставить OP_WRITE, ждать следующего события |
| Очередь пуста при входе в обработчик | Снять OP_WRITE немедленно |

Именно такую модель реализуют Netty, Apache Mina и другие высокопроизводительные NIO-фреймворки: OP_WRITE включается только при реальной необходимости, что позволяет `select()` блокироваться и не тратить CPU.

---

### Вопрос 50. Как Java NIO2 (java.nio.file) работает с символическими ссылками? Что происходит при вызове Files.delete(), Files.copy() и Files.readAttributes() на символической ссылке, и как управлять поведением через LinkOption.NOFOLLOW_LINKS?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Files (Java Platform SE 8) — Oracle JavaDoc](https://docs.oracle.com/javase/8/docs/api/java/nio/file/Files.html)

**Files.delete(Path path)**

> «If the file is a symbolic link then the symbolic link itself, not the final target of the link, is deleted.»

Метод не принимает `LinkOption` — поведение фиксировано: удаляется всегда сама ссылка, а не её цель.

**Files.copy(Path source, Path target, CopyOption... options)**

По умолчанию символическая ссылка разыменовывается и копируется файл-цель. При передаче `LinkOption.NOFOLLOW_LINKS`:

> «Symbolic links are not followed. If the file is a symbolic link, then the symbolic link itself, not the target of the link, is copied. It is implementation specific if file attributes can be copied to the new link. In other words, the COPY_ATTRIBUTES option may be ignored when copying a symbolic link.»

**Files.readAttributes(Path path, Class\<A\> type, LinkOption... options)**

По умолчанию символическая ссылка разыменовывается и возвращаются атрибуты конечного файла-цели. При передаче `LinkOption.NOFOLLOW_LINKS` возвращаются атрибуты самой ссылки (например, тип файла будет `isSymbolicLink() == true`, а размер — размер самой ссылки).

#### Ответ от Claude

**Общий принцип NIO2: link-aware API**

Пакет `java.nio.file` изначально спроектирован как «осведомлённый о ссылках» (link-aware). Большинство методов класса `Files` по умолчанию разыменовывают (следуют по) символические ссылки — аналогично поведению POSIX-системных вызовов (`stat` вместо `lstat`). Управление осуществляется через `LinkOption.NOFOLLOW_LINKS` — единственное значение перечисления `LinkOption`, которое реализует одновременно `OpenOption` и `CopyOption`.

**Files.delete(Path path)**

Всегда удаляет саму символическую ссылку, а не файл-цель. Метод не принимает `LinkOption` — поведение нельзя изменить. Это безопасно: невозможно случайно удалить реальный файл вместо ссылки.

```java
Path link = Path.of("/tmp/mylink"); // символическая ссылка на /data/real.txt
Files.delete(link); // удалит /tmp/mylink, файл /data/real.txt останется
```

Исключения: `NoSuchFileException` (путь не существует), `DirectoryNotEmptyException` (путь — непустая директория), `IOException` (проблемы с правами доступа).

**Files.copy(Path source, Path target, CopyOption... options)**

| Режим | Поведение |
|---|---|
| По умолчанию (без `NOFOLLOW_LINKS`) | Разыменовывает ссылку, копирует содержимое файла-цели |
| С `LinkOption.NOFOLLOW_LINKS` | Копирует саму символическую ссылку (новая ссылка указывает на тот же путь) |

```java
Path link = Path.of("/tmp/mylink");   // -> /data/real.txt
Path dest = Path.of("/tmp/copy");

// Копирует содержимое real.txt в /tmp/copy (обычный файл)
Files.copy(link, dest);

// Создаёт /tmp/copy как символическую ссылку на /data/real.txt
Files.copy(link, dest, LinkOption.NOFOLLOW_LINKS);
```

Важно: при копировании символической ссылки с `NOFOLLOW_LINKS` опция `COPY_ATTRIBUTES` может быть проигнорирована — это платформозависимое поведение.

**Files.readAttributes(Path path, Class\<A\> type, LinkOption... options)**

| Режим | Возвращает атрибуты |
|---|---|
| По умолчанию | Атрибуты файла-цели (конечного после разыменования) |
| С `LinkOption.NOFOLLOW_LINKS` | Атрибуты самой символической ссылки |

```java
Path link = Path.of("/tmp/mylink"); // -> /data/real.txt (5000 байт)

// Атрибуты цели: size=5000, isSymbolicLink=false, isRegularFile=true
BasicFileAttributes targetAttrs = Files.readAttributes(
    link, BasicFileAttributes.class);

// Атрибуты самой ссылки: isSymbolicLink=true, isRegularFile=false
BasicFileAttributes linkAttrs = Files.readAttributes(
    link, BasicFileAttributes.class, LinkOption.NOFOLLOW_LINKS);

System.out.println(linkAttrs.isSymbolicLink()); // true
System.out.println(targetAttrs.isSymbolicLink()); // false
```

**Сводная таблица поведения**

| Метод | Принимает LinkOption | Поведение по умолчанию | С NOFOLLOW_LINKS |
|---|---|---|---|
| `Files.delete()` | Нет | Удаляет саму ссылку | — |
| `Files.copy()` | Да (CopyOption) | Копирует содержимое цели | Копирует саму ссылку |
| `Files.readAttributes()` | Да | Атрибуты цели | Атрибуты самой ссылки |
| `Files.exists()` | Да | Проверяет цель | Проверяет саму ссылку |
| `Files.isSymbolicLink()` | Нет | Всегда проверяет саму ссылку | — |

**Практические рекомендации**

- Для определения типа файла (ссылка или нет) всегда используйте `Files.isSymbolicLink(path)`.
- Если нужно прочитать путь назначения ссылки — `Files.readSymbolicLink(path)`.
- Чтобы избежать случайного изменения данных при работе с ненадёжными путями (path traversal-уязвимости), используйте `NOFOLLOW_LINKS`.
- `Files.delete()` безопасен по умолчанию: никогда не удалит файл-цель через ссылку.

---

### Вопрос 51. Как работает Files.walkFileTree() и зачем нужен интерфейс FileVisitor? Объясни назначение методов preVisitDirectory, visitFile, postVisitDirectory и visitFileFailed, а также значения FileVisitResult (CONTINUE, TERMINATE, SKIP_SUBTREE, SKIP_SIBLINGS).

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Walking the File Tree — The Java Tutorials (docs.oracle.com)](https://docs.oracle.com/javase/tutorial/essential/io/walk.html)

`Files.walkFileTree()` обходит файловое дерево в глубину (depth-first). API требует передать реализацию `FileVisitor<Path>` — интерфейса с четырьмя методами:

- **`preVisitDirectory(dir, attrs)`** — вызывается перед посещением содержимого директории.
- **`visitFile(file, attrs)`** — вызывается для каждого файла.
- **`visitFileFailed(file, exc)`** — вызывается, если файл не удалось посетить (нет прав доступа, IO-ошибка).
- **`postVisitDirectory(dir, exc)`** — вызывается после посещения всего содержимого директории.

`SimpleFileVisitor<Path>` — готовая реализация, где все методы возвращают `CONTINUE`; удобно расширять, переопределяя только нужные.

Возвращаемые значения `FileVisitResult`:
- `CONTINUE` — продолжить обход.
- `TERMINATE` — немедленно прекратить обход.
- `SKIP_SUBTREE` — пропустить поддиректорию и её потомков (только из `preVisitDirectory`).
- `SKIP_SIBLINGS` — пропустить оставшихся «соседей» в текущей директории.

Пример — рекурсивное удаление директории:
```java
Files.walkFileTree(startingDir, new SimpleFileVisitor<Path>() {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
        Files.delete(file);
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
        if (exc == null) {
            Files.delete(dir);
            return FileVisitResult.CONTINUE;
        }
        throw exc;
    }
});
```

#### Ответ от Claude

**Files.walkFileTree() — обзор**

`Files.walkFileTree(Path start, FileVisitor<? super Path> visitor)` — статический метод класса `Files` (Java 7+), обходящий дерево файловой системы в глубину (depth-first, сначала директория, потом её содержимое). Существует перегрузка с дополнительными параметрами:

```java
Files.walkFileTree(Path start,
                   Set<FileVisitOption> options,  // например FOLLOW_LINKS
                   int maxDepth,                  // максимальная глубина
                   FileVisitor<? super Path> visitor)
```

**Методы FileVisitor и порядок вызова**

| Метод | Когда вызывается | Что возвращает при ошибке |
|---|---|---|
| `preVisitDirectory(dir, attrs)` | Перед входом в директорию | Если `SKIP_SUBTREE` — содержимое не посещается |
| `visitFile(file, attrs)` | Для каждого файла (не директории) | — |
| `visitFileFailed(file, exc)` | При ошибке доступа к файлу | Должен решить: пробросить или `CONTINUE` |
| `postVisitDirectory(dir, exc)` | После посещения всех потомков | `exc != null` если была IO-ошибка в теле |

**Значения FileVisitResult**

| Константа | Эффект |
|---|---|
| `CONTINUE` | Продолжить нормальный обход |
| `TERMINATE` | Прервать весь обход немедленно |
| `SKIP_SUBTREE` | Пропустить директорию и всё её содержимое; только из `preVisitDirectory` — из других методов эквивалентен `CONTINUE` |
| `SKIP_SIBLINGS` | Пропустить оставшихся «соседей» (файлы/директории на том же уровне) |

**Практические сценарии**

```java
// Поиск файла с остановкой
class FindFirst extends SimpleFileVisitor<Path> {
    private final String target;
    private Path found;

    FindFirst(String target) { this.target = target; }

    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
        if (file.getFileName().toString().equals(target)) {
            found = file;
            return FileVisitResult.TERMINATE; // нашли — прекращаем
        }
        return FileVisitResult.CONTINUE;
    }
}

// Пропуск служебных директорий
@Override
public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
    String name = dir.getFileName().toString();
    if (name.equals(".git") || name.equals("node_modules")) {
        return FileVisitResult.SKIP_SUBTREE;
    }
    return FileVisitResult.CONTINUE;
}
```

**Обработка символических ссылок**

По умолчанию `walkFileTree` не следует по символическим ссылкам. Чтобы следовать, нужно явно передать `FileVisitOption.FOLLOW_LINKS`. При циклических ссылках (loop) будет вызван `visitFileFailed` с исключением `FileSystemLoopException`.

**Files.walkFileTree() vs Files.walk()**

`Files.walk(Path start, ...)` (Java 8+) возвращает `Stream<Path>` и не требует реализации `FileVisitor`. Это удобнее для простых операций (filter/map), но не даёт раздельных хуков для pre/post-посещения директорий и не позволяет управлять обходом через `FileVisitResult`.

---

### Вопрос 52. Что такое SeekableByteChannel? Чем он отличается от FileChannel? Как создать SeekableByteChannel через Files.newByteChannel() и какие операции с позицией и усечением файла он поддерживает?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [SeekableByteChannel (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/channels/SeekableByteChannel.html)

`SeekableByteChannel` — интерфейс, расширяющий `ByteChannel`. Он представляет байтовый канал, соединённый с сущностью (обычно файлом), содержащей последовательность байт переменной длины, которую можно читать и записывать. Текущая позиция может быть запрошена и изменена.

Ключевые методы:

| Метод | Описание |
|-------|---------|
| `long position()` | Возвращает текущую позицию канала |
| `SeekableByteChannel position(long newPosition)` | Устанавливает новую позицию; поддерживает method chaining |
| `long size()` | Возвращает текущий размер сущности в байтах |
| `SeekableByteChannel truncate(long size)` | Усекает сущность до заданного размера; если `size >= current size`, сущность не меняется |
| `int read(ByteBuffer dst)` | Читает байты начиная с текущей позиции |
| `int write(ByteBuffer src)` | Пишет байты начиная с текущей позиции |

`SeekableByteChannel` создаётся через `Files.newByteChannel(Path, OpenOption...)`.

#### Ответ от Claude

**Что такое SeekableByteChannel**

`java.nio.channels.SeekableByteChannel` — интерфейс, добавленный в Java 7 (NIO.2). Он расширяет `ByteChannel` (который, в свою очередь, расширяет и `ReadableByteChannel`, и `WritableByteChannel`) и добавляет поддержку позиционирования. Это позволяет реализовать произвольный доступ к содержимому файла.

```
Channel
  └── ReadableByteChannel
  └── WritableByteChannel
        └── ByteChannel
              └── SeekableByteChannel   ← позиция + truncate
                    └── FileChannel     ← + map, lock, force, transfer
```

**SeekableByteChannel vs FileChannel**

`FileChannel` реализует `SeekableByteChannel`, но является конкретным классом с богатым набором дополнительных возможностей (memory-mapped файлы, блокировки, zero-copy transfer). `SeekableByteChannel` — это минимальный контракт для «позиционируемого» канала.

| Характеристика | SeekableByteChannel | FileChannel |
|---|---|---|
| Тип | Интерфейс | Абстрактный класс |
| Позиция | `position()`, `position(long)` | То же |
| Усечение | `truncate(long)` | То же |
| Memory-mapped I/O | Нет | `map()` |
| FileLock | Нет | `lock()`, `tryLock()` |
| Zero-copy | Нет | `transferTo()`, `transferFrom()` |
| Неблокирующий режим | Нет | Нет (FileChannel всегда блокирующий) |

**Создание через Files.newByteChannel()**

`Files.newByteChannel()` — фабричный метод, возвращающий `SeekableByteChannel`. На практике реализацией является `FileChannel`, но API не раскрывает этот детали:

```java
// Открыть только для чтения
try (SeekableByteChannel ch = Files.newByteChannel(
        Path.of("data.bin"), StandardOpenOption.READ)) {

    ByteBuffer buf = ByteBuffer.allocate(64);
    ch.read(buf);  // читаем с позиции 0

    ch.position(100);  // перемещаемся к байту 100
    buf.clear();
    ch.read(buf);  // читаем с позиции 100
}

// Открыть для записи с созданием
try (SeekableByteChannel ch = Files.newByteChannel(
        Path.of("output.bin"),
        StandardOpenOption.WRITE,
        StandardOpenOption.CREATE,
        StandardOpenOption.TRUNCATE_EXISTING)) {

    ByteBuffer buf = ByteBuffer.wrap(new byte[]{1, 2, 3, 4, 5});
    ch.write(buf);

    // Усечение: файл теперь будет содержать только 3 байта
    ch.truncate(3);
    System.out.println(ch.size()); // 3
}
```

**Поведение truncate()**

- `truncate(size)` при `size < currentSize`: файл обрезается до `size` байт, все данные после позиции `size` теряются. Если `position() > size`, позиция устанавливается в `size`.
- `truncate(size)` при `size >= currentSize`: файл не изменяется.

**Когда использовать SeekableByteChannel вместо FileChannel**

`Files.newByteChannel()` предпочтителен, когда нужна гибкость: API возвращает интерфейс, что упрощает тестирование (можно подставить mock-реализацию) и делает код более переносимым между разными файловыми системами (например, ZIP-файловая система через `FileSystems.newFileSystem()`).

---

### Вопрос 53. Как работает FileLock в Java NIO? В чём разница между shared и exclusive блокировкой? Почему FileLock не подходит для синхронизации потоков внутри одной JVM и каковы платформенные ограничения?

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [FileLock (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/channels/FileLock.html)

`FileLock` — токен, представляющий блокировку региона файла. Создаётся методами `lock()` или `tryLock()` класса `FileChannel`.

**Типы блокировок:**

- **Shared (общая)** — предотвращает получение другими программами перекрывающей **exclusive**-блокировки; позволяет одновременно получать shared-блокировки.
- **Exclusive (исключительная)** — предотвращает получение другими программами **любой** блокировки (shared или exclusive) на перекрывающейся области.

**Важные платформенные ограничения (из документации):**

1. Механизм блокировки может быть **advisory** (рекомендательным) или **mandatory** (принудительным) в зависимости от ОС. API рекомендует использовать блокировки как advisory.
2. На некоторых системах заблокированный регион нельзя одновременно отобразить в память (`mmap`).
3. Закрытие одного из каналов JVM может освободить все блокировки этого файла, полученные через другие каналы той же JVM.
4. Блокировка действительна до: вызова `release()`, закрытия канала или завершения JVM.

**Не предназначен для межпоточной синхронизации внутри JVM** — для этого используются `synchronized`, `ReentrantLock` и другие примитивы java.util.concurrent.

#### Ответ от Claude

**Получение FileLock**

`FileLock` получается через два метода `FileChannel`:

```java
// Блокирующий вызов — ждёт, пока блокировка не будет получена
FileLock lock(long position, long size, boolean shared) throws IOException;
FileLock lock() throws IOException; // весь файл, exclusive

// Неблокирующий вызов — возвращает null, если блокировка недоступна
FileLock tryLock(long position, long size, boolean shared) throws IOException;
FileLock tryLock() throws IOException; // весь файл, exclusive
```

Параметр `shared = true` — shared-блокировка; `shared = false` — exclusive.

**Shared vs Exclusive**

| Аспект | Shared | Exclusive |
|---|---|---|
| Цель | Чтение | Запись |
| Совместима с другими shared | Да | Нет |
| Совместима с exclusive | Нет | Нет |
| Аналог в POSIX | `flock(LOCK_SH)` / `fcntl` с `F_RDLCK` | `flock(LOCK_EX)` / `F_WRLCK` |

**Пример: межпроцессная блокировка файла**

```java
try (FileChannel channel = FileChannel.open(
        Path.of("/var/lock/app.lock"),
        StandardOpenOption.WRITE,
        StandardOpenOption.CREATE)) {

    FileLock lock = channel.tryLock(); // exclusive, весь файл
    if (lock == null) {
        System.out.println("Файл заблокирован другим процессом");
        return;
    }

    try {
        // Критическая секция: только один процесс здесь
        doWork();
    } finally {
        lock.release();
    }
}
```

**Почему FileLock не подходит для синхронизации потоков внутри JVM**

Официальная документация (`FileLock` Javadoc) явно указывает:

> «File locks are held on behalf of the entire Java virtual machine. They are not suitable for controlling access to a file by multiple threads within the same virtual machine.»

Причины:
1. Блокировки файловой системы работают на уровне ОС — они отслеживают процессы (PID), но не потоки.
2. Попытка получить уже заблокированную блокировку из того же JVM-процесса может привести к зависанию или исключению в зависимости от платформы.
3. Для синхронизации потоков используйте `synchronized`, `ReentrantLock`, `ReadWriteLock` и другие примитивы `java.util.concurrent`.

**Платформенные ограничения (подтверждено Javadoc)**

| Ограничение | Описание |
|---|---|
| Advisory vs mandatory | POSIX: advisory (другие процессы могут игнорировать). Windows: closer to mandatory |
| Закрытие канала | На некоторых ОС освобождает все блокировки файла в JVM, включая другие каналы |
| Сетевые FS | Ненадёжны; семантика блокировок зависит от реализации NFS/SMB |
| Shared на Windows | На Windows shared-блокировка может автоматически повышаться до exclusive |

**Освобождение блокировки**

`FileLock` реализует `AutoCloseable`, поэтому предпочтительно использовать try-with-resources:

```java
try (FileLock lock = channel.lock()) {
    // критическая секция
} // lock.release() вызывается автоматически
```

**Расхождение между источниками:** Baeldung описывает FileLock как инструмент для «предотвращения доступа нескольких приложений». Официальный Javadoc добавляет важную оговорку: «Exactly whether or not a lock is advisory or mandatory depends on the operating system» — это делает portable-использование FileLock ненадёжным без тестирования на целевой ОС.

---

### Вопрос 54. Чем PrintStream отличается от PrintWriter? Почему System.out и System.err являются PrintStream, а не PrintWriter? Как они обрабатывают кодировку символов?

**Категория:** IO/NIO · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [PrintStream vs PrintWriter in Java — Baeldung](https://www.baeldung.com/java-printstream-vs-printwriter)

**PrintStream** — подкласс `OutputStream`, обрабатывает данные байт за байтом. Предоставляет удобные методы `print()`, `println()`, `printf()` и `format()`. Не выбрасывает `IOException` — вместо этого внутренний флаг ошибки проверяется через `checkError()`.

**PrintWriter** — подкласс `Writer`, обрабатывает данные посимвольно. Предоставляет те же удобные методы печати, но работает с символами в Unicode.

**Автоматическая очистка буфера (auto-flush):**

`PrintStream` сбрасывает буфер автоматически при записи массивов байт, вызове `println()` или при записи символа новой строки (`\n`). `PrintWriter` сбрасывает буфер только при вызове `println()`, `printf()` или `format()`.

**Кодировка:** `PrintStream` по умолчанию использует кодировку платформы; указать кодировку можно через конструктор. `PrintWriter` с Java 10+ принимает кодировку через параметр-конструктор.

#### Ответ от Claude

**Иерархия классов**

```
OutputStream
  └── FilterOutputStream
        └── PrintStream  ← байтовый поток

Writer
  └── PrintWriter        ← символьный поток
```

**Ключевые различия**

| Характеристика | PrintStream | PrintWriter |
|---|---|---|
| Базовый класс | `OutputStream` (байтовый) | `Writer` (символьный) |
| Единица данных | Байт | Символ Unicode |
| Обработка кодировки | Кодирует символы в байты (с Java 1.4 — явная кодировка) | Работает с символами напрямую |
| Auto-flush | При `println()`, `byte[]`, `\n` | Только при `println()`, `printf()`, `format()` |
| Исключения | Не бросает `IOException`; `checkError()` | Не бросает `IOException`; `checkError()` |
| Применение | System.out, System.err, mixed content | Текстовый вывод, web-ответы (Servlet), файлы |

**Почему System.out и System.err — PrintStream**

`System.out` и `System.err` были введены в Java 1.0 (1995 год), когда `PrintWriter` ещё не существовал. `PrintWriter` появился в Java 1.1. Изменение типа `System.out` на `PrintWriter` нарушило бы обратную совместимость с существующим кодом. Поэтому они остаются `PrintStream`.

```java
// System.out — это PrintStream
public static final PrintStream out = null; // инициализируется JVM
public static final PrintStream err = null;
```

**Кодировка символов**

До Java 1.4: `PrintStream` использовал только кодировку платформы. С Java 1.4 добавлены конструкторы с явным `Charset` или именем кодировки:

```java
// Создание PrintStream с конкретной кодировкой
PrintStream ps = new PrintStream(new FileOutputStream("out.txt"), true, StandardCharsets.UTF_8);

// PrintWriter оборачивает Writer, кодировку задаёт Writer
PrintWriter pw = new PrintWriter(
    new OutputStreamWriter(new FileOutputStream("out.txt"), StandardCharsets.UTF_8),
    true // autoFlush
);
```

**Когда что использовать**

- `PrintStream` — для бинарных данных с текстовым форматированием (смешанный контент), для совместимости с legacy-кодом.
- `PrintWriter` — для чисто текстового вывода с корректной обработкой Unicode, веб-приложения (`HttpServletResponse.getWriter()` возвращает `PrintWriter`).

**Опасный антипаттерн:** использовать `PrintWriter` для бинарных данных (изображений, PDF) — `Writer` интерпретирует байты как символы и может их исказить.

---

### Вопрос 55. Для чего предназначен PushbackInputStream? Как работает метод unread() и какой размер pushback-буфера используется по умолчанию? Приведи практический сценарий, где этот класс незаменим.

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [PushbackInputStream (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/io/PushbackInputStream.html)

`PushbackInputStream` добавляет функциональность входному потоку, позволяя «вернуть» (push back) уже прочитанные байты. Это полезно, когда код читает неопределённое количество байт, ограниченных определённым значением: прочитав граничный байт, код может вернуть его обратно в поток, чтобы следующий вызов `read()` снова прочитал его.

По умолчанию `PushbackInputStream(InputStream in)` создаёт pushback-буфер размером 1 байт. Для буфера большего размера используется конструктор `PushbackInputStream(InputStream in, int size)`.

Три метода `unread()`:
- `unread(int b)` — возвращает один байт в начало pushback-буфера.
- `unread(byte[] b)` — возвращает массив байт: следующим будет прочитан `b[0]`.
- `unread(byte[] b, int off, int len)` — возвращает часть массива.

Если pushback-буфер заполнен, вызов `unread()` бросает `IOException` («Push back buffer is full»).

#### Ответ от Claude

**Назначение PushbackInputStream**

`PushbackInputStream` — декоратор над `InputStream` (паттерн Decorator). Он добавляет внутренний pushback-буфер (массив байт) и позволяет «откатить» уже прочитанные байты обратно в поток. Следующий вызов `read()` сначала отдаёт байты из pushback-буфера (в обратном порядке записи через `unread()`), и только когда буфер пуст — читает из исходного потока.

**Размер буфера по умолчанию и конструкторы**

```java
// Буфер размером 1 байт — самый распространённый случай
PushbackInputStream pis = new PushbackInputStream(inputStream);

// Буфер произвольного размера
PushbackInputStream pis = new PushbackInputStream(inputStream, 8);
```

Если попытаться вернуть байт при полном буфере — `IOException: Push back buffer is full`.

**Механизм unread()**

Данные помещаются в конец внутреннего буфера и читаются из него в обратном порядке (LIFO), но `unread(byte[])` обеспечивает, что `b[0]` будет прочитан первым:

```java
PushbackInputStream pis = new PushbackInputStream(
    new ByteArrayInputStream(new byte[]{'A', 'B', 'C'}), 4);

int first = pis.read();  // A
pis.unread(first);       // возвращаем A в поток
int again = pis.read();  // снова A
// B, C читаются далее
```

**Практический сценарий: парсер, определяющий формат данных по первым байтам**

Парсеры текста часто нуждаются в «заглядывании вперёд» (lookahead) — прочитать несколько байт, определить тип данных, и обработать их с начала:

```java
PushbackInputStream pis = new PushbackInputStream(inputStream, 3);

// Читаем первые 3 байта для определения кодировки (BOM)
byte[] bom = new byte[3];
int bytesRead = pis.read(bom);

if (bytesRead == 3
        && bom[0] == (byte) 0xEF
        && bom[1] == (byte) 0xBB
        && bom[2] == (byte) 0xBF) {
    // BOM UTF-8 обнаружен, потребляем его
    System.out.println("UTF-8 with BOM");
} else {
    // BOM отсутствует — возвращаем прочитанные байты
    pis.unread(bom, 0, bytesRead);
    System.out.println("No BOM, treating as plain bytes");
}
// Дальше читаем поток с самого начала (или после BOM)
```

**Другие сценарии применения**

- **Лексический анализ (лексер):** прочитать следующий символ, определить тип токена и вернуть символ, если он относится к следующему токену.
- **Протоколы с маркерами:** прочитать заголовок, определить тип сообщения и передать весь поток (с заголовком) обработчику.
- **Детектирование магических чисел форматов:** определить формат файла по первым байтам без потери данных.

**Альтернатива: BufferedInputStream.mark()/reset()**

`BufferedInputStream` с `mark(n)` и `reset()` решает аналогичную задачу без явного управления pushback-буфером. Разница: `mark()/reset()` позволяет «перемотать» произвольное число байт назад, тогда как `PushbackInputStream` позволяет вернуть только фиксированное число байт (размер буфера).

---

### Вопрос 56. Для чего предназначен класс SequenceInputStream? Как он объединяет несколько потоков в один? Какой порядок чтения данных гарантирует этот класс?

**Категория:** IO/NIO · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [SequenceInputStream (Java SE 21 & JDK 21) — docs.oracle.com](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/SequenceInputStream.html)

`SequenceInputStream` представляет логическую конкатенацию других входных потоков. Он начинает читать первый поток до конца файла, затем переходит ко второму и так далее, пока не будет достигнут конец последнего из содержащихся потоков.

Конструкторы:

1. `SequenceInputStream(InputStream s1, InputStream s2)` — объединяет два потока; сначала читается `s1`, затем `s2`.
2. `SequenceInputStream(Enumeration<? extends InputStream> e)` — принимает перечисление потоков; после исчерпания каждого потока автоматически вызывает на нём `close()`.

#### Ответ от Claude

**Что такое SequenceInputStream**

`java.io.SequenceInputStream` — специализированный `InputStream`, который прозрачно объединяет несколько потоков в один логический поток. С точки зрения потребителя это выглядит как единый непрерывный источник данных.

**Два конструктора и их использование**

```java
// 1. Два потока
InputStream s1 = new FileInputStream("part1.bin");
InputStream s2 = new FileInputStream("part2.bin");
try (SequenceInputStream sis = new SequenceInputStream(s1, s2)) {
    byte[] buf = new byte[1024];
    int n;
    while ((n = sis.read(buf)) != -1) {
        // обрабатываем данные из обоих файлов без разрыва
    }
}

// 2. Несколько потоков через Enumeration
List<InputStream> parts = List.of(
    new FileInputStream("chunk1.dat"),
    new FileInputStream("chunk2.dat"),
    new FileInputStream("chunk3.dat")
);
// Enumeration требует, т.к. API появился в Java 1.0 до Collections Framework
SequenceInputStream sis = new SequenceInputStream(
    Collections.enumeration(parts)
);
```

**Порядок чтения**

Порядок строго последовательный:
1. Читается из первого потока до получения `-1` (EOF).
2. Первый поток закрывается (`close()` вызывается автоматически).
3. Читается из второго потока, и так далее.
4. Когда исчерпан последний поток — `SequenceInputStream.read()` возвращает `-1`.

**Поведение available()**

Метод `available()` возвращает количество байт, доступных только в **текущем** (активном) потоке, а не суммарно по всем. Это нужно учитывать, чтобы не принимать решения о завершении на основе `available()`.

**Обработка исключений и закрытие**

Если `close()` вызывается на `SequenceInputStream`, он закрывает текущий поток и все оставшиеся потоки из `Enumeration`. Если во время чтения возникает `IOException` — она пробрасывается как обычно.

**Практические сценарии**

- Чтение нескольких файлов (например, частей разбитого файла) как одного потока без загрузки всего содержимого в память.
- Добавление заголовка или подписи к потоку данных: `new SequenceInputStream(headerStream, dataStream)`.
- Сборка HTTP-тела из нескольких буферов без копирования в единый массив.
- Объединение результатов нескольких запросов в один ответ.

**Ограничения**

`SequenceInputStream` не поддерживает `mark()/reset()` — `markSupported()` возвращает `false`. Он также не поддерживает произвольный доступ. Для более гибкой работы с несколькими источниками данных в современном Java можно использовать `InputStream.nullInputStream()` как плейсхолдер или `Files.walk()` + `Stream<InputStream>`.

---

### Вопрос 57. Что такое AsynchronousSocketChannel и AsynchronousServerSocketChannel в Java NIO2? Объясни, чем эти каналы отличаются от SocketChannel и ServerSocketChannel, и как с их помощью реализовать неблокирующий echo-сервер через CompletionHandler.

**Категория:** IO/NIO · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [A Guide to NIO2 Asynchronous Socket Channel — Baeldung](https://www.baeldung.com/java-nio2-async-socket-channel)

`AsynchronousServerSocketChannel` и `AsynchronousSocketChannel` — ключевые классы для асинхронного сетевого взаимодействия в Java NIO2 (Java 7+). Они аналогичны `ServerSocketChannel` и `SocketChannel`, но все операции I/O возвращают результаты асинхронно — либо через `Future<V>`, либо через `CompletionHandler<V,A>`.

Создание сервера:
```java
AsynchronousServerSocketChannel server =
    AsynchronousServerSocketChannel.open()
        .bind(new InetSocketAddress("127.0.0.1", 4321));
```

Принятие соединений через CompletionHandler:
```java
server.accept(null, new CompletionHandler<AsynchronousSocketChannel, Object>() {
    @Override
    public void completed(AsynchronousSocketChannel client, Object attachment) {
        server.accept(null, this); // принять следующее соединение
        // работать с client
    }

    @Override
    public void failed(Throwable exc, Object attachment) {
        // обработка ошибки
    }
});
```

Связь между клиентом и сервером ведётся через `ByteBuffer`, а чтение и запись выполняются через методы `read(ByteBuffer, attachment, CompletionHandler)` и `write(ByteBuffer, attachment, CompletionHandler)`.

#### Ответ от Claude

**Сравнение с синхронными каналами**

| Характеристика | SocketChannel / ServerSocketChannel | AsynchronousSocketChannel / AsynchronousServerSocketChannel |
|---|---|---|
| Модель I/O | Синхронная (может быть неблокирующей через Selector) | Полностью асинхронная |
| Возврат вызова | После завершения I/O (блокирующий) или немедленно (неблокирующий с 0) | Немедленно; результат через Future или CompletionHandler |
| Multiplexing | Через Selector | Через пул потоков (AsynchronousChannelGroup) |
| Сложность кода | Умеренная | Выше (callbacks или Future) |
| Введён в | Java 1.4 | Java 7 (NIO.2) |

**AsynchronousChannelGroup**

Оба асинхронных канала работают с `AsynchronousChannelGroup` — пулом потоков, в котором выполняются `CompletionHandler`. Если группа не указана явно, используется системная:

```java
// Явный пул потоков для CompletionHandler
ExecutorService pool = Executors.newFixedThreadPool(4);
AsynchronousChannelGroup group = AsynchronousChannelGroup.withThreadPool(pool);

AsynchronousServerSocketChannel server =
    AsynchronousServerSocketChannel.open(group)
        .bind(new InetSocketAddress(4321));
```

**Реализация простого echo-сервера через CompletionHandler**

```java
AsynchronousServerSocketChannel server =
    AsynchronousServerSocketChannel.open()
        .bind(new InetSocketAddress(4321));

// Принимаем соединения бесконечно
server.accept(null, new CompletionHandler<AsynchronousSocketChannel, Void>() {
    @Override
    public void completed(AsynchronousSocketChannel client, Void attachment) {
        // Принять следующее соединение до обработки текущего
        server.accept(null, this);

        ByteBuffer buf = ByteBuffer.allocate(1024);
        // Читаем данные от клиента
        client.read(buf, buf, new CompletionHandler<Integer, ByteBuffer>() {
            @Override
            public void completed(Integer bytesRead, ByteBuffer buf) {
                if (bytesRead == -1) {
                    try { client.close(); } catch (IOException e) { /* ignore */ }
                    return;
                }
                buf.flip();
                // Отправляем данные обратно (echo)
                client.write(buf, buf, new CompletionHandler<Integer, ByteBuffer>() {
                    @Override
                    public void completed(Integer bytesWritten, ByteBuffer buf) {
                        buf.clear();
                        client.read(buf, buf, this); // ждём следующие данные
                    }

                    @Override
                    public void failed(Throwable exc, ByteBuffer buf) {
                        try { client.close(); } catch (IOException e) { /* ignore */ }
                    }
                });
            }

            @Override
            public void failed(Throwable exc, ByteBuffer buf) {
                try { client.close(); } catch (IOException e) { /* ignore */ }
            }
        });
    }

    @Override
    public void failed(Throwable exc, Void attachment) {
        // Ошибка при принятии соединения
    }
});

// Главный поток не завершается — ждём
Thread.currentThread().join();
```

**Важные нюансы**

- `CompletionHandler` вызывается в потоке пула `AsynchronousChannelGroup`. Тяжёлая работа в обработчике блокирует пул для других I/O-операций — выносите обработку в отдельный `ExecutorService`.
- Асинхронные каналы **не работают с Selector** — они используют другую модель конкурентности.
- `Future<V>` подход (через `channel.read(buf).get()`) фактически синхронизирует выполнение и теряет смысл асинхронности.

---

### Вопрос 58. Как реализовать произвольный доступ к файлу через FileChannel.position()? Чем этот подход отличается от использования RandomAccessFile? Какие проблемы возникают при конкурентном доступе к FileChannel из нескольких потоков?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [FileChannel (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/nio/channels/FileChannel.html)

`FileChannel` поддерживает позицию для чтения и записи. Текущая позиция запрашивается через `position()` и устанавливается через `position(long newPosition)`. Если позиция установлена за пределы файла и выполняется чтение — метод `read()` вернёт `-1`. Если позиция за пределами файла и выполняется запись — файл расширится, а байты между предыдущим концом файла и новыми данными не определены.

Методы `read(ByteBuffer, long position)` и `write(ByteBuffer, long position)` принимают явную позицию и не изменяют текущую позицию канала. Документация прямо указывает, что `FileChannel` **безопасен для использования несколькими потоками** — конкурентные вызовы гарантируют, что каждый `write()` или `read()` будет сохранён или завершён полностью.

#### Ответ от Claude

**Произвольный доступ через FileChannel.position()**

```java
try (FileChannel channel = FileChannel.open(
        Path.of("records.dat"),
        StandardOpenOption.READ, StandardOpenOption.WRITE)) {

    int recordSize = 100; // фиксированная длина записи

    // Чтение записи #5 (нумерация с 0)
    long offset = 5L * recordSize;
    ByteBuffer buf = ByteBuffer.allocate(recordSize);
    channel.read(buf, offset); // позиционированное чтение
    buf.flip();
    // ... обработка buf ...

    // Запись обновлённой записи #5
    buf.clear();
    // ... заполнить buf ...
    buf.flip();
    channel.write(buf, offset); // позиционированная запись
}
```

**FileChannel vs RandomAccessFile**

| Характеристика | FileChannel | RandomAccessFile |
|---|---|---|
| API | NIO (Buffer-ориентированный) | Потоковый (read/write байт/массив) |
| Поддержка ByteBuffer | Да | Нет |
| Memory-mapped I/O | Да (`map()`) | Нет |
| Интеграция с NIO.2 | Полная (`StandardOpenOption`, `Path`) | Нет (только `File`) |
| Zero-copy transfer | Да (`transferTo`) | Нет |
| Потокобезопасность | Безопасен для concurrent read/write | Нет (требует синхронизации) |
| Открытие | `FileChannel.open(Path, options...)` | `new RandomAccessFile(file, mode)` |

**Конкурентный доступ из нескольких потоков**

`FileChannel` является потокобезопасным на уровне методов: конкурентные вызовы `read()` и `write()` не нарушат целостности данных. Однако есть важное ограничение для **позиционированных операций с изменением текущей позиции**:

```java
// ОПАСНО: race condition между position() и read()
channel.position(offset);    // поток A
// поток B может изменить позицию здесь
channel.read(buffer);        // поток A читает не с того места

// БЕЗОПАСНО: позиционированные методы
channel.read(buffer, offset);  // атомарно; не меняет position()
channel.write(buffer, offset); // атомарно; не меняет position()
```

Из документации Oracle:

> «File channels are safe for use by multiple concurrent threads. The close method may be invoked at any time. [...] Operations that involve changing the file's position will observe each other's changes if they are not synchronized.»

**Рекомендации при конкурентном доступе:**

1. Использовать позиционированные методы `read(buf, position)` и `write(buf, position)` — они атомарны и не меняют общий position канала.
2. Разделять обработку записей между потоками по диапазонам позиций (каждый поток работает со своим диапазоном).
3. При необходимости изменить `position()` синхронизировать доступ явно.
4. Для полного контроля над параллельным доступом с гарантиями — рассматривать `AsynchronousFileChannel`, который принимает позицию как аргумент каждого метода.

---

### Вопрос 59. Что делают методы ByteBuffer.slice() и ByteBuffer.duplicate()? Разделяют ли они backing array с оригинальным буфером? Чем эти методы полезны при реализации протоколов с составными сообщениями?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ByteBuffer (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/nio/ByteBuffer.html)

**`slice()`** — создаёт новый байт-буфер, содержимое которого является общей подпоследовательностью оригинального. Новый буфер начинается с текущей позиции оригинала. Его `position` равна нулю, а `capacity` и `limit` равны числу оставшихся байт в оригинале. Изменения в содержимом нового буфера отразятся в оригинале и наоборот, так как они разделяют одни и те же данные. Позиция, лимит и метка нового буфера независимы от оригинала.

**`duplicate()`** — создаёт новый байт-буфер, разделяющий содержимое с оригиналом. Содержимое нового буфера идентично содержимому оригинала. Изменения содержимого видны в обоих буферах. Начальные значения `position`, `limit` и `mark` нового буфера совпадают с оригиналом. Позиция, лимит и метка нового буфера независимы.

#### Ответ от Claude

**slice() — срез буфера от текущей позиции**

`slice()` создаёт «вид» (view) оставшейся части буфера:

```java
ByteBuffer original = ByteBuffer.allocate(10);
original.put(new byte[]{0,1,2,3,4,5,6,7,8,9});
original.position(3);  // смещаемся на 3

ByteBuffer slice = original.slice();
// slice: position=0, limit=7, capacity=7
// slice содержит байты [3,4,5,6,7,8,9] — от позиции оригинала до его конца

// Изменения разделяются:
slice.put(0, (byte) 99);
// original.get(3) == 99 — изменение видно в оригинале
```

**duplicate() — полная копия состояния (с разделяемыми данными)**

```java
ByteBuffer original = ByteBuffer.allocate(10);
original.put(new byte[]{0,1,2,3,4,5,6,7,8,9});
original.position(5);

ByteBuffer dup = original.duplicate();
// dup: position=5, limit=10, capacity=10 — то же состояние

// Изменения данных разделяются:
dup.put(5, (byte) 42);
// original.get(5) == 42

// Но позиции независимы:
dup.position(0);  // не влияет на original.position()
```

**Разделение backing array**

| Метод | Разделяют ли данные с оригиналом | Разделяют ли position/limit/mark |
|---|---|---|
| `slice()` | Да (один и тот же массив байт) | Нет (независимы) |
| `duplicate()` | Да (один и тот же массив байт) | Нет (независимы) |
| `asReadOnlyBuffer()` | Да | Нет |

Важно: ни `slice()`, ни `duplicate()` не копируют байты. Это лёгкие операции O(1), создающие новый объект-заголовок с теми же данными.

**Применение при реализации протоколов**

При разборе бинарных протоколов (например, TLV — Type-Length-Value) часто нужно передать «подпоток» данных в отдельный обработчик:

```java
// Пример: разбор пакета с заголовком и телом
ByteBuffer packet = ByteBuffer.wrap(receivedBytes);

// Читаем заголовок (фиксированный, 8 байт)
ByteBuffer header = packet.slice(); // view с позиции 0
header.limit(8);
processHeader(header);

// Перемещаемся к телу
packet.position(8);
ByteBuffer body = packet.slice(); // view от байта 8 до конца
processBody(body);
// Оба view разделяют backing array — нет копирования

// duplicate() полезен, когда несколько потоков читают из одного буфера независимо
ByteBuffer reader1 = sharedBuffer.duplicate();
ByteBuffer reader2 = sharedBuffer.duplicate();
reader1.position(0);
reader2.position(sharedBuffer.limit() / 2); // каждый читает свою половину
```

**Расхождение источников:** Javadoc Java 8 не упоминает `slice(int index, int length)` — этот метод появился только в Java 13. Код, рассчитанный на Java 8, должен использовать комбинацию `position()` + `slice()`.

---

### Вопрос 60. Чем Files.walk() отличается от Files.walkFileTree()? Когда использование Files.walk() со Stream API предпочтительнее, а когда лучше подходит walkFileTree() с FileVisitor? Как с Files.walk() правильно обрабатывать ошибки доступа?

**Категория:** IO/NIO · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Files (Java SE 21 & JDK 21) — docs.oracle.com](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html)

Метод `Files.walk(Path start, int maxDepth, FileVisitOption... options)` возвращает `Stream<Path>`, обходящий дерево файловой системы в глубину. Если `maxDepth` не указан, используется `Integer.MAX_VALUE`. Поток включает стартовую директорию.

Если во время доступа к файлу возникает `IOException` (например, `AccessDeniedException`), это исключение оборачивается в `UncheckedIOException` и пробрасывается из терминального оператора потока. Чтобы избежать прерывания обхода при ошибках доступа, необходимо явно обрабатывать исключения.

Поток должен быть закрыт после использования, поскольку он удерживает открытый дескриптор директории. Рекомендуемый паттерн — try-with-resources.

#### Ответ от Claude

**Основные различия**

| Критерий | Files.walk() | Files.walkFileTree() |
|---|---|---|
| Введён | Java 8 | Java 7 |
| Возвращаемый тип | `Stream<Path>` | `void` (возвращает стартовый Path) |
| API стиль | Функциональный (filter, map, collect) | Объектный (переопределение методов) |
| Pre/Post обработка директорий | Нет раздельных хуков | `preVisitDirectory` / `postVisitDirectory` |
| Управление обходом | Нельзя прервать/пропустить через API | `FileVisitResult.TERMINATE/SKIP_*` |
| Обработка ошибок | `UncheckedIOException`, пробрасывается в терминал | `visitFileFailed()` — решаете сами |
| Ресурс | Требует закрытия (AutoCloseable) | Нет |

**Files.walk() — функциональный подход**

```java
// Найти все .java файлы не глубже 5 уровней
try (Stream<Path> stream = Files.walk(srcDir, 5)) {
    List<Path> javaFiles = stream
        .filter(Files::isRegularFile)
        .filter(p -> p.toString().endsWith(".java"))
        .sorted()
        .collect(Collectors.toList());
}

// Подсчёт суммарного размера файлов
try (Stream<Path> stream = Files.walk(dataDir)) {
    long totalSize = stream
        .filter(Files::isRegularFile)
        .mapToLong(p -> {
            try { return Files.size(p); }
            catch (IOException e) { return 0L; }
        })
        .sum();
}
```

**Обработка ошибок доступа в Files.walk()**

По умолчанию `AccessDeniedException` оборачивается в `UncheckedIOException` и прерывает обработку потока. Для продолжения при ошибках используют `Files.walkFileTree()` или фильтрацию через `filter(Files::isReadable)`:

```java
// Вариант 1: пропускать недоступные файлы через isReadable
try (Stream<Path> stream = Files.walk(root)) {
    stream.filter(p -> Files.isReadable(p) && Files.isRegularFile(p))
          .forEach(p -> process(p));
}

// Вариант 2: обернуть в try-catch внутри forEach
try (Stream<Path> stream = Files.walk(root)) {
    stream.forEach(p -> {
        try {
            if (Files.isRegularFile(p)) process(p);
        } catch (UncheckedIOException e) {
            System.err.println("Ошибка доступа: " + p + " — " + e.getCause());
        }
    });
}
```

**walkFileTree() — когда он предпочтительнее**

Используйте `Files.walkFileTree()` когда необходимо:

1. Выполнять действия **после** обхода всего содержимого директории (например, удалить пустую директорию после удаления её файлов — `postVisitDirectory`).
2. **Управлять обходом** — пропустить поддерево (`SKIP_SUBTREE`) или прервать (`TERMINATE`).
3. **Обрабатывать ошибки** по каждому файлу индивидуально через `visitFileFailed` без прерывания всего обхода.

```java
// Рекурсивное удаление: сначала файлы, затем директории
Files.walkFileTree(dirToDelete, new SimpleFileVisitor<>() {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs)
            throws IOException {
        Files.delete(file);
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult postVisitDirectory(Path dir, IOException exc)
            throws IOException {
        if (exc != null) throw exc;
        Files.delete(dir); // директория уже пуста
        return FileVisitResult.CONTINUE;
    }
});
```

**Итог:** `Files.walk()` предпочтителен для простых задач сбора/фильтрации файлов в стиле Stream API. `Files.walkFileTree()` незаменим при сложной логике с управлением обходом и обработкой ошибок на уровне каждого узла дерева.

---
