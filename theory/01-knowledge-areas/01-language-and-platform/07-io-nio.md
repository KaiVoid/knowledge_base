# Ввод-вывод: IO и NIO

> **Уровень:** Middle
> **Связанные вопросы:** [Вопросы по IO/NIO →](../interview-questions/io-nio-01.md)
> **Связанные области:** [[06-exceptions]], [[04-concurrency]]

## Что это и зачем

Работа с потоками данных, файлами и сетью. Классический `java.io` (потоки байтов и символов,
буферизация, сериализация) и более новый `java.nio` (буферы, каналы, селекторы, неблокирующий ввод-вывод,
файловый API `java.nio.file`). Понимание различий блокирующего и неблокирующего ввода-вывода важно
для написания производительных и масштабируемых приложений, в т.ч. серверов.

Пакет `java.io` появился в Java 1.0 и строится на абстракции потока (stream) — последовательного
считывания или записи данных. Пакет `java.nio` введён в Java 1.4, а `java.nio.file` (NIO.2) — в Java 7.
NIO строится на других абстракциях: буферах, каналах и селекторах, что открывает возможности
для неблокирующего и асинхронного ввода-вывода.

## Ключевые подтемы

### Байтовые потоки: InputStream / OutputStream

Базовый уровень — чтение и запись сырых байтов. Все классы наследуются от абстрактных
[`InputStream`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/InputStream.html) и
[`OutputStream`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/OutputStream.html).

**Иерархия `InputStream`:**

| Класс | Назначение |
|---|---|
| `FileInputStream` | Чтение байтов из файла |
| `ByteArrayInputStream` | Чтение из байтового массива в памяти |
| `BufferedInputStream` | Буферизация поверх другого потока |
| `DataInputStream` | Чтение примитивных типов (int, long, double …) |
| `ObjectInputStream` | Десериализация объектов |
| `SequenceInputStream` | Конкатенация нескольких потоков |
| `PushbackInputStream` | Возврат прочитанных байтов обратно в поток |

**Иерархия `OutputStream`:** симметрична — `FileOutputStream`, `ByteArrayOutputStream`,
`BufferedOutputStream`, `DataOutputStream`, `ObjectOutputStream`, `PrintStream`.

Ключевой контракт: метод `read()` возвращает значение `0–255` либо `-1` при достижении конца потока.
Потоки реализуют `Closeable`, поэтому правильный шаблон использования — `try-with-resources`:

```java
try (InputStream in = new FileInputStream("data.bin");
     OutputStream out = new FileOutputStream("copy.bin")) {
    byte[] buf = new byte[8192];
    int n;
    while ((n = in.read(buf)) != -1) {
        out.write(buf, 0, n);
    }
}
```

Читать побайтово без буферизации крайне неэффективно: каждый вызов `read()` превращается в системный
вызов. Поэтому сырые потоки почти всегда оборачивают в `BufferedInputStream` / `BufferedOutputStream`.

### Символьные потоки: Reader / Writer

Символьные потоки построены поверх байтовых и выполняют автоматическое перекодирование между
внутренним Unicode (UTF-16) и указанной кодировкой. Базовые классы —
[`Reader`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/Reader.html) и
[`Writer`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/Writer.html).

**Важные реализации:**

| Класс | Назначение |
|---|---|
| `FileReader` / `FileWriter` | Текстовые файлы (кодировка платформы по умолчанию) |
| `BufferedReader` / `BufferedWriter` | Буферизация + построчное чтение `readLine()` |
| `InputStreamReader` / `OutputStreamWriter` | Мост «байтовый поток → символьный», кодировка задаётся явно |
| `StringReader` / `StringWriter` | Чтение/запись в строку |
| `PrintWriter` | Форматированный вывод `print`, `println`, `format` |

`InputStreamReader` и `OutputStreamWriter` — ключевые классы-мосты. Именно через них нужно
указывать кодировку явно, а не полагаться на `FileReader` (он берёт кодировку ОС):

```java
// Правильно: явная кодировка UTF-8
try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(new FileInputStream("text.txt"), StandardCharsets.UTF_8))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
```

Метод `read()` у `Reader` возвращает значение `0–65535` (char) или `-1` при EOF.

### Буферизация

Без буферизации каждый `read()` / `write()` транслируется в системный вызов ОС — операцию,
дорогостоящую по времени. Буфер накапливает данные в памяти и взаимодействует с ОС блоками.

**Классы буферизации (`java.io`):**

- `BufferedInputStream` / `BufferedOutputStream` — для байтовых потоков (буфер по умолчанию 8 192 байт).
- `BufferedReader` / `BufferedWriter` — для символьных потоков.

```java
// Без буферизации: крайне медленно на больших файлах
InputStream raw = new FileInputStream("file.dat");

// С буферизацией: один системный вызов читает ~8 КБ за раз
InputStream buffered = new BufferedInputStream(raw, 16384);
```

`PrintWriter` с параметром `autoFlush = true` сбрасывает буфер автоматически при вызове
`println()` или `format()`. В остальных случаях нужно вызывать `flush()` явно или полагаться
на `close()`.

### Сериализация: Serializable, ObjectOutputStream, transient

Сериализация — механизм преобразования объекта в байтовый поток (и обратно) для сохранения
или передачи по сети. Задействует пакет `java.io`.

**Ключевые понятия:**

- Класс должен реализовывать маркерный интерфейс
  [`Serializable`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/Serializable.html).
- `ObjectOutputStream.writeObject(obj)` обходит весь граф ссылок объекта и записывает все
  достижимые объекты. Если один объект записывается дважды в один поток — записывается только
  первая копия, второй вызов сохраняет ссылку (экономия места).
- `ObjectInputStream.readObject()` бросает `ClassNotFoundException`, если класс не найден в classpath.
- Поле, помеченное `transient`, не включается в сериализованный поток (пароли, кэши, IO-ресурсы).
- `serialVersionUID` — явный идентификатор версии класса; без него JVM генерирует его автоматически
  на основе сигнатуры класса, что может привести к `InvalidClassException` при изменении класса.

```java
public class User implements Serializable {
    private static final long serialVersionUID = 1L;

    private String name;
    private transient String password; // не сериализуется

    // ...
}

// Сериализация
try (ObjectOutputStream oos = new ObjectOutputStream(
        new BufferedOutputStream(new FileOutputStream("user.ser")))) {
    oos.writeObject(user);
}

// Десериализация
try (ObjectInputStream ois = new ObjectInputStream(
        new BufferedInputStream(new FileInputStream("user.ser")))) {
    User restored = (User) ois.readObject();
}
```

**Риски сериализации:** объект десериализуется без вызова конструктора — инварианты класса
могут быть нарушены. Встроенная сериализация Java считается устаревшим механизмом и не
рекомендуется к использованию в новых проектах. Предпочтительны JSON/Protobuf/Avro.

### java.nio: Buffer, Channel — основы NIO

NIO строится на трёх ключевых абстракциях:

1. **Buffer** — контейнер данных фиксированного размера в памяти.
2. **Channel** — двунаправленное соединение с I/O-источником (файл, сокет).
3. **Selector** — мультиплексор каналов для неблокирующего ввода-вывода.

#### Buffer

[`Buffer`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/Buffer.html) —
абстрактный класс с четырьмя состояниями:

| Свойство | Смысл |
|---|---|
| `capacity` | Максимальное число элементов (задаётся при создании, не меняется) |
| `limit` | Первый элемент, который нельзя читать/писать |
| `position` | Индекс следующего элемента для чтения/записи |
| `mark` | Сохранённое значение `position` для возврата через `reset()` |

Инвариант: `0 <= mark <= position <= limit <= capacity`.

Конкретные реализации: `ByteBuffer`, `CharBuffer`, `IntBuffer`, `LongBuffer`, `FloatBuffer`,
`DoubleBuffer`, `ShortBuffer`.

**Ключевые операции:**

```java
ByteBuffer buf = ByteBuffer.allocate(1024); // position=0, limit=1024

// Запись данных в буфер
buf.put((byte) 42);      // position=1
buf.put(new byte[]{1,2,3});

// Переключение в режим чтения
buf.flip();              // limit=position, position=0

// Чтение данных из буфера
while (buf.hasRemaining()) {
    byte b = buf.get(); // position++
}

// Очистка буфера для повторной записи
buf.clear();            // position=0, limit=capacity

// compact() — сохраняет непрочитанные данные и готовит к дозаписи
buf.compact();          // непрочитанное → начало, position за последним непрочитанным
```

`ByteBuffer.allocateDirect(size)` выделяет прямой буфер за пределами кучи JVM. JVM старается
использовать нативные операции ввода-вывода без промежуточного копирования, что ускоряет
обмен с каналами. Цена — медленное выделение и сборка мусора.

#### Channel

[`Channel`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/Channel.html) —
интерфейс, представляющий открытое соединение. Основные реализации:

| Класс | Назначение |
|---|---|
| `FileChannel` | Файловый ввод-вывод, memory-mapped I/O, блокировки |
| `SocketChannel` | TCP-клиент |
| `ServerSocketChannel` | TCP-сервер (принимает соединения) |
| `DatagramChannel` | UDP |
| `AsynchronousFileChannel` | Асинхронный файловый ввод-вывод |
| `AsynchronousSocketChannel` | Асинхронный TCP-клиент |

Паттерн работы с каналом и буфером:

```java
try (FileChannel fc = FileChannel.open(Path.of("data.bin"),
        StandardOpenOption.READ)) {
    ByteBuffer buf = ByteBuffer.allocate(4096);
    while (fc.read(buf) != -1) {
        buf.flip();
        // обработка данных из buf
        buf.clear();
    }
}
```

`FileChannel` поддерживает **memory-mapped I/O** через `map()` — отображение части файла
в виртуальную память процесса. Это самый быстрый способ доступа к большим файлам:

```java
try (FileChannel fc = FileChannel.open(Path.of("large.bin"), StandardOpenOption.READ)) {
    MappedByteBuffer mapped = fc.map(FileChannel.MapMode.READ_ONLY, 0, fc.size());
    // работаем с mapped как с обычным ByteBuffer
}
```

### Selector — неблокирующий мультиплексный ввод-вывод

[`Selector`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/Selector.html)
позволяет одному потоку обслуживать множество каналов. Канал регистрируется в Selector с
набором интересующих событий (`OP_ACCEPT`, `OP_CONNECT`, `OP_READ`, `OP_WRITE`).

**Алгоритм работы:**

1. Создать `Selector`.
2. Переключить каналы в неблокирующий режим (`configureBlocking(false)`).
3. Зарегистрировать каналы с нужными операциями.
4. В цикле вызывать `selector.select()` — метод блокируется до появления готового канала.
5. Обработать готовые ключи из `selector.selectedKeys()`.

```java
Selector selector = Selector.open();
ServerSocketChannel server = ServerSocketChannel.open();
server.bind(new InetSocketAddress(8080));
server.configureBlocking(false);
server.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select(); // блокируется
    Set<SelectionKey> keys = selector.selectedKeys();
    Iterator<SelectionKey> it = keys.iterator();
    while (it.hasNext()) {
        SelectionKey key = it.next();
        it.remove();
        if (key.isAcceptable()) {
            SocketChannel client = server.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            // читаем данные из (SocketChannel) key.channel()
        }
    }
}
```

Важно: готовность ключа — подсказка, а не гарантия. Код должен быть готов к ситуации,
когда операция всё равно блокируется.

### Асинхронный ввод-вывод (AIO)

В Java 7 появились `AsynchronousFileChannel` и `AsynchronousSocketChannel`. Операции не
блокируют поток — результат доставляется через один из двух паттернов:

**Future (блокирующее ожидание результата):**

```java
AsynchronousFileChannel afc = AsynchronousFileChannel.open(
    Path.of("data.bin"), StandardOpenOption.READ);
ByteBuffer buf = ByteBuffer.allocate(1024);
Future<Integer> future = afc.read(buf, 0);
int bytesRead = future.get(); // ждём
```

**CompletionHandler (колбэк-подход):**

```java
afc.read(buf, 0, null, new CompletionHandler<Integer, Void>() {
    @Override
    public void completed(Integer bytesRead, Void attachment) {
        buf.flip();
        // обработка
    }

    @Override
    public void failed(Throwable exc, Void attachment) {
        // обработка ошибки
    }
});
```

`AsynchronousFileChannel` не имеет текущей позиции — позицию нужно указывать явно в каждом
вызове `read`/`write`. Один и тот же `ByteBuffer` нельзя использовать в нескольких
одновременных операциях.

### Файловый API NIO.2: Path, Files, Paths

NIO.2 (`java.nio.file`, Java 7+) — современный API для работы с файловой системой,
заменяющий устаревший `java.io.File`.

#### Path

[`Path`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html) —
интерфейс, представляющий путь в файловой системе. Создаётся через `Path.of(...)` (Java 11+)
или `Paths.get(...)`:

```java
Path p1 = Path.of("/home/user/docs/report.txt");
Path p2 = Path.of("relative", "path", "file.txt");

p1.getFileName();         // report.txt
p1.getParent();           // /home/user/docs
p1.getRoot();             // /
p1.toAbsolutePath();      // абсолютный путь
p1.normalize();           // убирает . и ..
p1.relativize(other);     // относительный путь от p1 до other
p1.resolve("sibling.txt");// /home/user/docs/sibling.txt
```

`Path` не проверяет существование файла — это чисто синтаксическая операция.

#### Files

[`Files`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html) —
статический класс-утилита с методами для всех файловых операций.

**Чтение файлов:**

```java
// Полное содержимое (только для небольших файлов)
byte[] bytes = Files.readAllBytes(path);
List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);

// Потоковое чтение через BufferedReader
try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
    reader.lines().forEach(System.out::println);
}

// Stream<String> строк (Java 8+) — ленивое чтение
try (Stream<String> lines = Files.lines(path, StandardCharsets.UTF_8)) {
    lines.filter(l -> l.contains("ERROR")).forEach(System.out::println);
}
```

**Запись файлов:**

```java
// Запись байтов / строк (создаёт или заменяет файл)
Files.write(path, bytes);
Files.write(path, linesList, StandardCharsets.UTF_8);

// BufferedWriter
try (BufferedWriter w = Files.newBufferedWriter(path, StandardCharsets.UTF_8,
        StandardOpenOption.APPEND)) {
    w.write("new line");
    w.newLine();
}
```

**StandardOpenOption — ключевые флаги:**

| Опция | Описание |
|---|---|
| `READ` | Открыть для чтения |
| `WRITE` | Открыть для записи |
| `APPEND` | Дописать в конец |
| `TRUNCATE_EXISTING` | Обнулить существующий файл |
| `CREATE` | Создать, если не существует |
| `CREATE_NEW` | Создать; исключение если уже есть |
| `DELETE_ON_CLOSE` | Удалить при закрытии |
| `SYNC` | Синхронизировать содержимое и метаданные с диском |
| `DSYNC` | Синхронизировать только содержимое |

**Управление файлами и директориями:**

```java
Files.createFile(path);                  // атомарное создание
Files.createDirectory(path);
Files.createDirectories(path);           // mkdir -p
Files.delete(path);                      // исключение если не существует
Files.deleteIfExists(path);
Files.copy(src, dst, StandardCopyOption.REPLACE_EXISTING);
Files.move(src, dst, StandardCopyOption.ATOMIC_MOVE);
Files.exists(path);
Files.isRegularFile(path);
Files.isDirectory(path);
Files.size(path);
Files.getLastModifiedTime(path);

// Перечисление содержимого директории
try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*.java")) {
    for (Path entry : ds) {
        System.out.println(entry.getFileName());
    }
}
```

#### Обход файлового дерева: FileVisitor

[`FileVisitor`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/FileVisitor.html)
реализует паттерн «посетитель» для обхода дерева директорий. Удобно расширять
`SimpleFileVisitor`, переопределяя только нужные методы:

| Метод | Когда вызывается |
|---|---|
| `preVisitDirectory` | Перед посещением содержимого директории |
| `visitFile` | При посещении файла |
| `visitFileFailed` | Если файл недоступен |
| `postVisitDirectory` | После обхода всего содержимого директории |

Возвращаемый `FileVisitResult` управляет обходом: `CONTINUE`, `TERMINATE`, `SKIP_SUBTREE`,
`SKIP_SIBLINGS`.

```java
Files.walkFileTree(startDir, new SimpleFileVisitor<Path>() {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
        System.out.println(file);
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
        if (dir.getFileName().toString().equals("target")) {
            return FileVisitResult.SKIP_SUBTREE; // не заходить в target/
        }
        return FileVisitResult.CONTINUE;
    }
});
```

Для простых задач можно использовать `Files.walk(path)` — возвращает `Stream<Path>`:

```java
try (Stream<Path> stream = Files.walk(startDir)) {
    stream.filter(Files::isRegularFile)
          .filter(p -> p.toString().endsWith(".java"))
          .forEach(System.out::println);
}
```

Обход производится в глубину (depth-first). По умолчанию символические ссылки не
разворачиваются (во избежание циклов).

### WatchService — мониторинг директорий

[`WatchService`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/WatchService.html)
позволяет приложению реагировать на события файловой системы (создание, изменение, удаление)
без опроса. Использует нативные механизмы ОС там, где они доступны.

```java
WatchService watcher = FileSystems.getDefault().newWatchService();

Path dir = Path.of("/watched-dir");
dir.register(watcher,
    StandardWatchEventKinds.ENTRY_CREATE,
    StandardWatchEventKinds.ENTRY_DELETE,
    StandardWatchEventKinds.ENTRY_MODIFY);

for (;;) {
    WatchKey key = watcher.take(); // блокируется
    for (WatchEvent<?> event : key.pollEvents()) {
        if (event.kind() == StandardWatchEventKinds.OVERFLOW) continue;
        Path changed = (Path) event.context();
        System.out.println(event.kind() + ": " + changed);
    }
    if (!key.reset()) break; // ключ перевести в состояние Ready
}
```

Вызов `key.reset()` обязателен: без него ключ остаётся в состоянии Signaled и новые события
не поступают.

### Кодировки символов (Charset)

[`java.nio.charset.Charset`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/charset/Charset.html)
описывает соответствие между байтами и Unicode-символами. Стандартные кодировки доступны
через константы `StandardCharsets`:

| Константа | Кодировка |
|---|---|
| `StandardCharsets.UTF_8` | UTF-8 (предпочтительная) |
| `StandardCharsets.UTF_16` | UTF-16 (с BOM) |
| `StandardCharsets.ISO_8859_1` | Latin-1 |
| `StandardCharsets.US_ASCII` | 7-битный ASCII |

Всегда указывайте кодировку явно при работе с `InputStreamReader`, `OutputStreamWriter`,
`Files.newBufferedReader/Writer` и `Files.readAllLines`. Зависимость от системной кодировки
по умолчанию ведёт к непереносимым программам.

### Блокирующий, неблокирующий и асинхронный ввод-вывод: сравнение

| Режим | Поток при ожидании | Классы | Применение |
|---|---|---|---|
| Блокирующий (BIO) | Заблокирован | `java.io`, `FileChannel` | Простые задачи, один поток на соединение |
| Неблокирующий (NIO) | Свободен, опрашивает Selector | `SocketChannel` + `Selector` | Серверы с тысячами соединений |
| Асинхронный (AIO) | Свободен, получает колбэк | `AsynchronousFileChannel`, `AsynchronousSocketChannel` | Высоконагруженные файловые операции |

Неблокирующий NIO значительно масштабируемее блокирующего: один поток с `Selector` может
обслуживать тысячи соединений, тогда как модель «один поток на соединение» упирается в
ресурсы при высоком числе клиентов.

### Миграция с java.io.File на Path/Files

`java.io.File` не бросает содержательных исключений (например, `delete()` возвращает `boolean`
вместо исключения), не поддерживает символические ссылки и атрибуты файлов. NIO.2 исправляет
эти недостатки. Метод `File.toPath()` позволяет постепенно переходить на новый API:

```java
File legacyFile = new File("/path/to/file");
Path modernPath = legacyFile.toPath(); // конвертация

// Или обратно
File back = modernPath.toFile();
```

## Достоверные источники

1. **[The Java Tutorials — Basic I/O](https://docs.oracle.com/javase/tutorial/essential/io/index.html)** —
   официальный учебник Oracle по `java.io` и NIO.2; охватывает потоки, сериализацию, файловый API.

2. **[Java SE 21 API — java.nio.file](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/package-summary.html)** —
   официальная Javadoc: `Path`, `Files`, `FileVisitor`, `WatchService`, исключения — первичный
   источник для точных контрактов классов.

3. **[Java SE 21 API — java.nio.channels](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/channels/package-summary.html)** —
   официальная Javadoc: `FileChannel`, `SocketChannel`, `Selector`, `AsynchronousFileChannel`;
   описание неблокирующего и асинхронного ввода-вывода.

4. **[Java SE 21 API — java.nio](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/package-summary.html)** —
   официальная Javadoc: `Buffer` и его подклассы (`ByteBuffer`, `MappedByteBuffer`), `Charset`;
   точные инварианты position/limit/capacity.

5. **[Jenkov — Java NIO Tutorial](https://jenkov.com/tutorials/java-nio/index.html)** —
   авторитетный ресурс: детальный разбор Buffer, Channel, Selector с иллюстрациями и примерами.

6. **[Baeldung — Java IO vs NIO](https://www.baeldung.com/java-io-vs-nio)** —
   практическое сравнение подходов java.io и java.nio с примерами кода; хорошо дополняет
   официальную документацию конкретными сценариями применения.
