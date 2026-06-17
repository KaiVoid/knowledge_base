# Урок 2. Работа с URL

**Трейл:** Custom Networking · **Оригинал:** [Working With URLs](https://docs.oracle.com/javase/tutorial/networking/urls/index.html)
**Связанные области:** [[17-rest-web]] · **Вопросы:** rest-web

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

> URL — это аббревиатура от *Uniform Resource Locator* (единообразный указатель ресурса).
> Это ссылка (адрес) на ресурс в Интернете. Вы передаёте URL своему любимому веб-браузеру,
> чтобы он мог найти файлы в Интернете, — точно так же, как вы пишете адрес на письме,
> чтобы почта могла найти ваших адресатов.
>
> Java-программы, взаимодействующие с Интернетом, тоже могут использовать URL, чтобы находить
> нужные им ресурсы в сети. Для представления URL-адреса в Java-программах служит класс `URL`
> из пакета `java.net`.

> **Замечание о терминологии.** Термин *URL* может быть неоднозначным: он способен обозначать
> как интернет-адрес, так и объект `URL` в Java-программе. Там, где требуется уточнение, в этом
> тексте используется «URL-адрес» для обозначения интернет-адреса и «объект `URL`» — для
> обозначения экземпляра класса `URL` в программе.

## Что такое URL?

> Если вы пользовались Всемирной паутиной, то наверняка слышали термин URL и применяли URL для
> доступа к HTML-страницам.

Чаще всего проще всего (хотя и не вполне точно) воспринимать URL как имя файла во Всемирной
паутине, потому что большинство URL ссылаются именно на файл на какой-либо машине в сети. Однако
помните, что URL могут указывать и на другие ресурсы сети — например, на запросы к базе данных
или на вывод команды.

> **Определение.** URL — это аббревиатура от *Uniform Resource Locator* (единообразный указатель
> ресурса) и представляет собой ссылку (адрес) на ресурс в Интернете.

URL состоит из двух основных частей:

- **Идентификатор протокола** (*protocol identifier*): для URL `http://example.com`
  идентификатор протокола — это `http`.
- **Имя ресурса** (*resource name*): для URL `http://example.com` имя ресурса — это `example.com`.

Обратите внимание, что идентификатор протокола и имя ресурса разделены двоеточием и двумя
прямыми слешами. Идентификатор протокола указывает имя протокола, который нужно использовать
для получения ресурса. В примере используется протокол передачи гипертекста
(Hypertext Transfer Protocol, HTTP), которым обычно отдают гипертекстовые документы. HTTP — лишь
один из множества протоколов, применяемых для доступа к разным типам ресурсов в сети. Среди
других протоколов — File Transfer Protocol (FTP), Gopher, File и News.

Имя ресурса — это полный адрес ресурса. Формат имени ресурса полностью зависит от используемого
протокола, но для многих протоколов, включая HTTP, имя ресурса содержит один или несколько
следующих компонентов:

- **Имя хоста** (*Host Name*) — имя машины, на которой расположен ресурс.
- **Имя файла** (*Filename*) — путь к файлу на машине.
- **Номер порта** (*Port Number*) — номер порта, к которому подключаться (как правило,
  необязателен).
- **Ссылка/якорь** (*Reference*) — ссылка на именованный якорь внутри ресурса; обычно указывает
  конкретное место внутри файла (как правило, необязательна).

Для многих протоколов имя хоста и имя файла обязательны, а номер порта и ссылка необязательны.
Например, имя ресурса для HTTP-URL обязано указывать сервер в сети (имя хоста) и путь к документу
на этой машине (имя файла); дополнительно оно может задавать номер порта и ссылку.

## Создание URL

Проще всего создать объект `URL` из строки `String`, представляющей URL-адрес в
удобочитаемой для человека форме. Обычно именно в такой форме другой человек и записывает URL.
В Java-программе можно использовать строку `String` с этим текстом, чтобы создать объект `URL`:

```java
URL myURL = new URL("http://example.com/");
```

Созданный выше объект `URL` представляет *абсолютный URL* (*absolute URL*). Абсолютный URL
содержит всю информацию, необходимую для доступа к нужному ресурсу. Объекты `URL` можно также
создавать из *относительного URL* (*relative URL*).

### Создание URL относительно другого

Относительный URL содержит лишь столько информации, сколько нужно, чтобы добраться до ресурса
относительно (или в контексте) другого URL.

Спецификации относительных URL часто применяются внутри HTML-файлов. Например, предположим, вы
пишете HTML-файл `JoesHomePage.html`. На этой странице есть ссылки на другие страницы,
`PicturesOfMe.html` и `MyKids.html`, расположенные на той же машине и в том же каталоге, что и
`JoesHomePage.html`. Ссылки на `PicturesOfMe.html` и `MyKids.html` из `JoesHomePage.html` можно
указать просто как имена файлов:

```html
<a href="PicturesOfMe.html">Pictures of Me</a>
<a href="MyKids.html">Pictures of My Kids</a>
```

Эти URL-адреса являются *относительными*. То есть URL заданы относительно файла, в котором они
содержатся, — `JoesHomePage.html`.

В Java-программах можно создать объект `URL` из спецификации относительного URL. Например,
предположим, вы знаете два URL на сайте `example.com`:

```
http://example.com/pages/page1.html
http://example.com/pages/page2.html
```

Вы можете создать объекты `URL` для этих страниц относительно их общего базового URL
`http://example.com/pages/` так:

```java
URL myURL = new URL("http://example.com/pages/");
URL page1URL = new URL(myURL, "page1.html");
URL page2URL = new URL(myURL, "page2.html");
```

В этом фрагменте используется конструктор `URL`, позволяющий создать объект `URL` из другого
объекта `URL` (базового) и спецификации относительного URL. Общая форма этого конструктора:

```java
URL(URL baseURL, String relativeURL)
```

Первый аргумент — это объект `URL`, задающий базу нового `URL`. Второй аргумент — это строка
`String`, задающая остальную часть имени ресурса относительно базы. Если `baseURL` равен `null`,
то этот конструктор трактует `relativeURL` как спецификацию абсолютного URL. И наоборот, если
`relativeURL` является спецификацией абсолютного URL, то конструктор игнорирует `baseURL`.

Этот конструктор также полезен для создания объектов `URL` для именованных якорей (также
называемых ссылками) внутри файла. Например, предположим, в файле `page1.html` внизу есть
именованный якорь `BOTTOM`. С помощью конструктора относительного URL можно создать для него
объект `URL` так:

```java
URL page1BottomURL = new URL(page1URL, "#BOTTOM");
```

### Другие конструкторы URL

Класс `URL` предоставляет ещё два конструктора для создания объекта `URL`. Они полезны при работе
с URL (например, HTTP-URL), у которых в части имени ресурса есть компоненты «имя хоста», «имя
файла», «номер порта» и «ссылка». Эти два конструктора удобны, когда у вас нет строки с полной
спецификацией URL, но известны отдельные его компоненты.

Например, предположим, вы проектируете панель просмотра сети, аналогичную панели просмотра
файлов, которая позволяет пользователям выбрать протокол, имя хоста, номер порта и имя файла.
Объект `URL` можно собрать из компонентов панели. Первый конструктор создаёт объект `URL` из
протокола, имени хоста и имени файла. Следующий фрагмент создаёт `URL` для файла `page1.html` на
сайте `example.com`:

```java
new URL("http", "example.com", "/pages/page1.html");
```

Это эквивалентно:

```java
new URL("http://example.com/pages/page1.html");
```

Первый аргумент — протокол, второй — имя хоста, последний — путь к файлу. Обратите внимание, что
имя файла начинается с прямого слеша. Это означает, что имя файла задаётся от корня хоста.

Последний конструктор `URL` добавляет к списку аргументов предыдущего конструктора номер порта:

```java
URL gamelan = new URL("http", "example.com", 80, "pages/page1.html");
```

Так создаётся объект `URL` для следующего URL:

```
http://example.com:80/pages/page1.html
```

Если вы создали объект `URL` одним из этих конструкторов, то получить строку `String` с полным
URL-адресом можно с помощью метода `toString` объекта `URL` или эквивалентного метода
`toExternalForm`.

### URL-адреса со специальными символами

Некоторые URL-адреса содержат специальные символы, например символ пробела:

```
http://example.com/hello world/
```

Чтобы сделать такие символы допустимыми, их нужно закодировать перед передачей в конструктор
`URL`:

```java
URL url = new URL("http://example.com/hello%20world");
```

В этом примере закодировать специальный символ легко, поскольку кодирования требует лишь один
символ. Но для URL-адресов с несколькими такими символами или если при написании кода вы заранее
не знаете, к каким URL-адресам потребуется обращаться, можно использовать многоаргументные
конструкторы класса [`java.net.URI`](https://docs.oracle.com/javase/8/docs/api/java/net/URI.html),
которые автоматически выполнят кодирование за вас:

```java
URI uri = new URI("http", "example.com", "/hello world/", "");
```

А затем преобразовать `URI` в `URL`:

```java
URL url = uri.toURL();
```

### MalformedURLException

Каждый из четырёх конструкторов `URL` выбрасывает исключение `MalformedURLException`, если его
аргументы ссылаются на `null` или неизвестный протокол. Обычно это исключение перехватывают и
обрабатывают, помещая операторы конструктора URL в пару `try`/`catch`:

```java
try {
    URL myURL = new URL(...);
}
catch (MalformedURLException e) {
    // здесь код обработчика исключения
    // ...
}
```

О работе с исключениями см. урок
[Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/index.html).

> **Примечание.** Объекты `URL` доступны для записи только один раз («write-once»). После того
> как объект `URL` создан, ни один из его атрибутов (протокол, имя хоста, имя файла или номер
> порта) изменить нельзя.

## Разбор URL

Класс `URL` предоставляет несколько методов, позволяющих опрашивать объекты `URL`. С помощью
этих методов-аксессоров можно получить из URL протокол, авторитет, имя хоста, номер порта, путь,
строку запроса, имя файла и ссылку:

- **`getProtocol`** — возвращает компонент «идентификатор протокола» URL.
- **`getAuthority`** — возвращает компонент «авторитет» (*authority*) URL.
- **`getHost`** — возвращает компонент «имя хоста» URL.
- **`getPort`** — возвращает компонент «номер порта» URL. Метод `getPort` возвращает целое число —
  номер порта. Если порт не задан, `getPort` возвращает `-1`.
- **`getPath`** — возвращает компонент «путь» данного URL.
- **`getQuery`** — возвращает компонент «строка запроса» данного URL.
- **`getFile`** — возвращает компонент «имя файла» URL. Метод `getFile` возвращает то же, что и
  `getPath`, плюс конкатенацию со значением `getQuery`, если оно есть.
- **`getRef`** — возвращает компонент «ссылка» URL.

> **Примечание.** Помните, что не все URL-адреса содержат эти компоненты. Класс `URL`
> предоставляет эти методы потому, что HTTP-URL действительно содержат данные компоненты и,
> пожалуй, являются самыми распространёнными. Класс `URL` в известной степени ориентирован на
> HTTP («HTTP-центричен»).

Эти методы `getXXX` можно использовать, чтобы получить информацию об URL независимо от того, каким
конструктором был создан объект `URL`.

Класс `URL` вместе с этими методами-аксессорами избавляет вас от необходимости когда-либо снова
разбирать URL вручную! Имея любую строковую спецификацию URL, просто создайте новый объект `URL`
и вызовите любой из методов-аксессоров, чтобы получить нужную информацию. Эта небольшая программа
создаёт `URL` из строковой спецификации, а затем с помощью методов-аксессоров объекта `URL`
разбирает его:

```java
import java.net.*;
import java.io.*;

public class ParseURL {
    public static void main(String[] args) throws Exception {

        URL aURL = new URL("http://example.com:80/docs/books/tutorial"
                           + "/index.html?name=networking#DOWNLOADING");

        System.out.println("protocol = " + aURL.getProtocol());
        System.out.println("authority = " + aURL.getAuthority());
        System.out.println("host = " + aURL.getHost());
        System.out.println("port = " + aURL.getPort());
        System.out.println("path = " + aURL.getPath());
        System.out.println("query = " + aURL.getQuery());
        System.out.println("filename = " + aURL.getFile());
        System.out.println("ref = " + aURL.getRef());
    }
}
```

Вот вывод этой программы:

```
protocol = http
authority = example.com:80
host = example.com
port = 80
path = /docs/books/tutorial/index.html
query = name=networking
filename = /docs/books/tutorial/index.html?name=networking
ref = DOWNLOADING
```

## Чтение напрямую из URL

После того как объект `URL` успешно создан, можно вызвать его метод `openStream()`, чтобы получить
поток, из которого читается содержимое URL. Метод `openStream()` возвращает объект
[`java.io.InputStream`](https://docs.oracle.com/javase/8/docs/api/java/io/InputStream.html),
поэтому читать из URL так же легко, как из входного потока.

Следующая небольшая Java-программа использует `openStream()`, чтобы получить входной поток на URL
`http://www.oracle.com/`. Затем она открывает `BufferedReader` поверх входного потока и читает из
него, тем самым читая из URL. Всё прочитанное копируется в стандартный поток вывода:

```java
import java.net.*;
import java.io.*;

public class URLReader {
    public static void main(String[] args) throws Exception {

        URL oracle = new URL("http://www.oracle.com/");
        BufferedReader in = new BufferedReader(
        new InputStreamReader(oracle.openStream()));

        String inputLine;
        while ((inputLine = in.readLine()) != null)
            System.out.println(inputLine);
        in.close();
    }
}
```

Когда вы запустите программу, в окне команд должны прокручиваться HTML-команды и текстовое
содержимое HTML-файла, расположенного по адресу `http://www.oracle.com/`. В качестве альтернативы
программа может зависнуть, либо вы можете увидеть трассировку стека исключения. Если происходит
одно из двух последних событий, возможно, вам потребуется
[задать прокси-хост](https://docs.oracle.com/javase/tutorial/networking/urls/_setProxy.html),
чтобы программа смогла найти сервер Oracle.

## Подключение к URL

После того как объект `URL` успешно создан, можно вызвать его метод `openConnection`, чтобы
получить объект `URLConnection` или один из его специфичных для протокола подклассов — например,
[`java.net.HttpURLConnection`](https://docs.oracle.com/javase/8/docs/api/java/net/HttpURLConnection.html).

Этот объект `URLConnection` можно использовать для настройки параметров и общих свойств запроса,
которые могут понадобиться перед подключением. Само соединение с удалённым объектом, представленным
URL, инициируется только при вызове метода `URLConnection.connect`. При этом вы устанавливаете
канал связи между своей Java-программой и URL по сети. Например, следующий код открывает соединение
с сайтом `example.com`:

```java
try {
    URL myURL = new URL("http://example.com/");
    URLConnection myURLConnection = myURL.openConnection();
    myURLConnection.connect();
}
catch (MalformedURLException e) {
    // вызов new URL() завершился неудачей
    // ...
}
catch (IOException e) {
    // вызов openConnection() завершился неудачей
    // ...
}
```

Новый объект `URLConnection` создаётся каждый раз при вызове метода `openConnection` обработчика
протокола (*protocol handler*) для данного URL.

Не всегда требуется явно вызывать метод `connect`, чтобы инициировать соединение. Операции,
зависящие от наличия соединения, — такие как `getInputStream`, `getOutputStream` и т. п. — при
необходимости выполнят подключение неявно.

Теперь, когда вы успешно подключились к своему URL, объект `URLConnection` можно использовать для
выполнения таких действий, как чтение из соединения или запись в него. Следующий раздел показывает,
как это делается.

## Чтение из URLConnection и запись в него

Класс `URLConnection` содержит множество методов, позволяющих взаимодействовать с URL по сети.
`URLConnection` — HTTP-центричный класс, то есть многие его методы полезны лишь при работе с
HTTP-URL. Однако большинство URL-протоколов позволяют читать из соединения и записывать в него.
Этот раздел описывает обе функции.

### Чтение из URLConnection

Следующая программа выполняет ту же функцию, что и программа `URLReader` из раздела
[Чтение напрямую из URL](#чтение-напрямую-из-url).

Однако вместо того чтобы получать входной поток напрямую из URL, эта программа явно извлекает
объект `URLConnection` и получает входной поток из соединения. Соединение открывается неявно при
вызове `getInputStream`. Затем, как и `URLReader`, эта программа создаёт `BufferedReader` поверх
входного потока и читает из него. Выделенные операторы подчёркивают отличия этого примера от
предыдущего:

```java
import java.net.*;
import java.io.*;

public class URLConnectionReader {
    public static void main(String[] args) throws Exception {
        URL oracle = new URL("http://www.oracle.com/");
        URLConnection yc = oracle.openConnection();
        BufferedReader in = new BufferedReader(new InputStreamReader(
                                    yc.getInputStream()));
        String inputLine;
        while ((inputLine = in.readLine()) != null)
            System.out.println(inputLine);
        in.close();
    }
}
```

Вывод этой программы идентичен выводу программы, которая открывает поток напрямую из URL. Читать из
URL можно любым из этих способов. Однако чтение из `URLConnection` вместо чтения напрямую из URL
может оказаться полезнее, потому что объект `URLConnection` одновременно можно применять и для
других задач (например, для записи в URL).

И снова: если программа зависает или вы видите сообщение об ошибке, возможно, вам потребуется
задать прокси-хост, чтобы программа смогла найти сервер Oracle.

### Запись в URLConnection

Многие HTML-страницы содержат *формы* (*forms*) — текстовые поля и другие элементы графического
интерфейса, позволяющие ввести данные для отправки на сервер. После того как вы вводите нужную
информацию и инициируете запрос нажатием кнопки, ваш веб-браузер записывает данные в URL по сети.
На другом конце сервер получает данные, обрабатывает их и затем отправляет вам ответ — обычно в
виде новой HTML-страницы.

Многие из этих HTML-форм используют HTTP-метод POST для отправки данных на сервер. Поэтому запись
в URL часто называют *публикацией (постингом) в URL* (*posting to a URL*). Сервер распознаёт
запрос POST и читает данные, присланные клиентом.

Чтобы Java-программа могла взаимодействовать с серверным процессом, ей просто нужно уметь
записывать в URL, тем самым предоставляя данные серверу. Сделать это можно, выполнив следующие
шаги:

1. Создать `URL`.
2. Получить объект `URLConnection`.
3. Включить у `URLConnection` возможность вывода (записи).
4. Открыть соединение с ресурсом.
5. Получить выходной поток из соединения.
6. Записать в выходной поток.
7. Закрыть выходной поток.

Вот небольшой `servlet` под названием
[`ReverseServlet`](https://docs.oracle.com/javase/tutorial/networking/urls/examples/ReverseServlet.java)
(или, если хотите, [cgi-bin](https://docs.oracle.com/javase/tutorial/networking/urls/examples/backwards)-скрипт).
Этим сервлетом можно протестировать следующую программу-пример.

Сервлет, работающий в контейнере, читает из своего `InputStream`, переворачивает строку и
записывает её в свой `OutputStream`. Сервлету требуется ввод вида `string=string_to_reverse`, где
`string_to_reverse` — строка, символы которой вы хотите вывести в обратном порядке.

Вот пример программы, которая запускает `ReverseServlet` по сети через `URLConnection`:

```java
import java.io.*;
import java.net.*;

public class Reverse {
    public static void main(String[] args) throws Exception {

        if (args.length != 2) {
            System.err.println("Usage:  java Reverse "
                + "http://<location of your servlet/script>"
                + " string_to_reverse");
            System.exit(1);
        }

        String stringToReverse = URLEncoder.encode(args[1], "UTF-8");

        URL url = new URL(args[0]);
        URLConnection connection = url.openConnection();
        connection.setDoOutput(true);

        OutputStreamWriter out = new OutputStreamWriter(
                                         connection.getOutputStream());
        out.write("string=" + stringToReverse);
        out.close();

        BufferedReader in = new BufferedReader(
                                    new InputStreamReader(
                                    connection.getInputStream()));
        String decodedString;
        while ((decodedString = in.readLine()) != null) {
            System.out.println(decodedString);
        }
        in.close();
    }
}
```

Разберём программу и посмотрим, как она работает. Сначала программа обрабатывает аргументы
командной строки:

```java
if (args.length != 2) {
    System.err.println("Usage:  java Reverse "
        + "http://<location of your servlet/script>"
        + " string_to_reverse");
    System.exit(1);
}

String stringToReverse = URLEncoder.encode(args[1], "UTF-8");
```

Эти операторы гарантируют, что пользователь передаст программе ровно два аргумента командной
строки. Аргументы командной строки — это расположение `ReverseServlet` и строка, которая будет
перевёрнута. Она может содержать пробелы или другие неалфавитно-цифровые символы. Эти символы нужно
закодировать, поскольку строка обрабатывается по пути к серверу. Кодированием символов занимаются
методы класса `URLEncoder`.

Далее программа создаёт объект `URL` и настраивает соединение так, чтобы в него можно было
записывать:

```java
URL url = new URL(args[0]);
URLConnection connection = url.openConnection();
connection.setDoOutput(true);
```

Затем программа создаёт выходной поток на соединении и открывает поверх него `OutputStreamWriter`:

```java
OutputStreamWriter out = new OutputStreamWriter(connection.getOutputStream());
```

Если URL не поддерживает вывод, метод `getOutputStream` выбрасывает `UnknownServiceException`.
Если URL поддерживает вывод, то этот метод возвращает выходной поток, который соединён с входным
потоком URL на стороне сервера, — вывод клиента является вводом сервера.

Далее программа записывает необходимую информацию в выходной поток и закрывает поток:

```java
out.write("string=" + stringToReverse);
out.close();
```

Этот код записывает в выходной поток методом `write`. Как видите, записывать данные в URL так же
легко, как записывать данные в поток. Данные, записанные в выходной поток на стороне клиента,
являются вводом для сервлета на стороне сервера. Программа `Reverse` формирует ввод в требуемой
скриптом форме, добавляя `string=` перед кодированной строкой, которую нужно перевернуть.

Сервлет читает записанную вами информацию, выполняет над строковым значением операцию переворота,
а затем отправляет результат обратно вам. Теперь вам нужно прочитать строку, которую вернул сервер.
Программа `Reverse` делает это так:

```java
BufferedReader in = new BufferedReader(
                            new InputStreamReader(
                            connection.getInputStream()));
String decodedString;
while ((decodedString = in.readLine()) != null) {
    System.out.println(decodedString);
}
in.close();
```

Если ваш `ReverseServlet` расположен по адресу `http://example.com/servlet/ReverseServlet`, то при
запуске программы `Reverse` с аргументом

```
http://example.com/servlet/ReverseServlet "Reverse Me"
```

(включая двойные кавычки) вы должны увидеть такой вывод:

```
Reverse Me
 reversed is:
eM esreveR
```

## Источник

- [Lesson: Working with URLs](https://docs.oracle.com/javase/tutorial/networking/urls/index.html) — официальное руководство Oracle (обзор урока).
- [What Is a URL?](https://docs.oracle.com/javase/tutorial/networking/urls/definition.html) — официальное руководство Oracle.
- [Creating a URL](https://docs.oracle.com/javase/tutorial/networking/urls/creatingUrls.html) — официальное руководство Oracle.
- [Parsing a URL](https://docs.oracle.com/javase/tutorial/networking/urls/urlInfo.html) — официальное руководство Oracle.
- [Reading Directly from a URL](https://docs.oracle.com/javase/tutorial/networking/urls/readingURL.html) — официальное руководство Oracle.
- [Connecting to a URL](https://docs.oracle.com/javase/tutorial/networking/urls/connecting.html) — официальное руководство Oracle.
- [Reading from and Writing to a URLConnection](https://docs.oracle.com/javase/tutorial/networking/urls/readingWriting.html) — официальное руководство Oracle.
