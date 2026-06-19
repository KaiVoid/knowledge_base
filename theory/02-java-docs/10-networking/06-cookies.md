# Урок 6. Работа с cookie

**Трейл:** Custom Networking · **Оригинал:** [Working With Cookies](https://docs.oracle.com/javase/tutorial/networking/cookies/index.html)
**Связанные области:** [[17-rest-web]] · **Вопросы:** rest-web

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

Хотя вы, скорее всего, уже знакомы с cookie, вы можете не знать, как использовать их
преимущества в своём Java-приложении. Этот урок проводит вас через само понятие cookie и
объясняет, как установить обработчик cookie (*cookie handler*), чтобы ваши HTTP-соединения
по URL использовали его.

Java SE предоставляет один основной класс для этой функциональности —
[`java.net.CookieHandler`](https://docs.oracle.com/javase/8/docs/api/java/net/CookieHandler.html),
а также следующие вспомогательные классы и интерфейсы:
[`java.net.CookieManager`](https://docs.oracle.com/javase/8/docs/api/java/net/CookieManager.html),
[`java.net.CookiePolicy`](https://docs.oracle.com/javase/8/docs/api/java/net/CookiePolicy.html),
[`java.net.CookieStore`](https://docs.oracle.com/javase/8/docs/api/java/net/CookieStore.html) и
[`java.net.HttpCookie`](https://docs.oracle.com/javase/8/docs/api/java/net/HttpCookie.html).

Урок состоит из следующих подтем:

- **Управление состоянием HTTP с помощью cookie** — что такое cookie и как они обеспечивают сессии.
- **Механизм обратного вызова CookieHandler** — как обработчик cookie вызывается при обращении
  к веб-сайту и как его установить.
- **CookieManager по умолчанию** — стандартная реализация обработчика cookie, которой в
  большинстве случаев достаточно и которая хорошо настраивается.
- **Настраиваемый CookieManager** — примеры настройки политики cookie и написания собственного
  хранилища cookie.

## Управление состоянием HTTP с помощью cookie

Механизм управления состоянием HTTP (*HTTP state management mechanism*) задаёт способ создания
сессии с сохранением состояния (*stateful session*) на основе HTTP-запросов и ответов.

Как правило, пары «запрос/ответ» HTTP независимы друг от друга. Однако механизм управления
состоянием позволяет клиентам и серверам, способным обмениваться информацией о состоянии,
поместить эти пары в более широкий контекст, который называется **сессией** (*session*).
Информация о состоянии, используемая для создания и поддержания сессии, называется
**cookie** (*cookie*).

Cookie — это фрагмент данных, который может храниться в кеше браузера. Если вы посещаете
веб-сайт, а затем заходите на него повторно, данные cookie могут использоваться для того,
чтобы опознать вас как вернувшегося посетителя. Cookie позволяют запоминать информацию о
состоянии, например содержимое онлайн-корзины покупок. Cookie может быть краткосрочным,
хранящим данные в течение одной веб-сессии — то есть пока вы не закроете браузер, — а может
быть долгосрочным, хранящим данные в течение недели или года.

Дополнительную информацию об управлении состоянием HTTP см. в документе
[RFC 2965: HTTP State Management Mechanism](http://www.ietf.org/rfc/rfc2965.txt).

## Механизм обратного вызова CookieHandler

Управление состоянием HTTP реализовано в Java SE через класс
[`java.net.CookieHandler`](https://docs.oracle.com/javase/8/docs/api/java/net/CookieHandler.html).
Объект `CookieHandler` предоставляет механизм обратного вызова (*callback mechanism*) для
реализации политики управления состоянием HTTP в обработчике протокола HTTP. То есть URL,
использующие HTTP в качестве протокола — например, `new URL("http://example.com")`, — будут
использовать обработчик протокола HTTP. Этот обработчик протокола обращается с обратным
вызовом к объекту `CookieHandler` (если он установлен) для управления состоянием.

Класс `CookieHandler` — абстрактный, и у него есть две пары связанных методов. Первая пара,
`getDefault()` и `setDefault(cookieHandler)`, — это статические методы, которые позволяют
узнать, какой обработчик установлен в данный момент, и установить свой собственный обработчик.

Обработчик по умолчанию не установлен, и установка обработчика выполняется в масштабах всей
системы (*system-wide*). Для приложений, работающих в защищённой среде — то есть с установленным
менеджером безопасности (*security manager*), — необходимо иметь специальное разрешение, чтобы
получать и устанавливать обработчик. Дополнительную информацию см. в
[`java.net.CookieHandler.getDefault`](https://docs.oracle.com/javase/8/docs/api/java/net/CookieHandler.html#getDefault--).

Вторая пара связанных методов, `put(uri, responseHeaders)` и `get(uri, requestHeaders)`,
позволяет, соответственно, устанавливать и получать все применимые cookie в кеш cookie и из него
для указанного URI в заголовках ответа/запроса. Эти методы абстрактны, и конкретная реализация
`CookieHandler` должна предоставить их реализацию.

Java Web Start и Java Plug-in имеют установленный по умолчанию `CookieHandler`. Однако если вы
запускаете автономное (*stand-alone*) приложение и хотите включить управление состоянием HTTP,
вы должны установить общесистемный обработчик. Следующие две страницы этого урока показывают,
как это сделать.

## CookieManager по умолчанию

`java.net.CookieManager` предоставляет конкретную реализацию `CookieHandler` и для большинства
пользователей достаточен для управления состоянием HTTP. `CookieManager` отделяет хранение
cookie от политики их принятия и отклонения. `CookieManager` инициализируется хранилищем
`java.net.CookieStore` и политикой `java.net.CookiePolicy`. `CookieStore` управляет хранением
cookie. `CookiePolicy` принимает решения о принятии и отклонении cookie согласно политике.

Следующий код показывает, как создать и установить общесистемный `CookieManager`:

```java
java.net.CookieManager cm = new java.net.CookieManager();
java.net.CookieHandler.setDefault(cm);
```

Первая строка вызывает конструктор `CookieManager` по умолчанию, чтобы создать экземпляр.
Вторая строка вызывает статический метод `setDefault` класса `CookieHandler`, чтобы установить
общесистемный обработчик.

Конструктор `CookieManager` по умолчанию создаёт новый экземпляр `CookieManager` с хранилищем
cookie по умолчанию и политикой принятия по умолчанию. `CookieStore` — это место, где хранится
любой принятый HTTP-cookie. Если при создании оно не указано, экземпляр `CookieManager` будет
использовать внутреннюю реализацию хранения в памяти (*in-memory*). Эта реализация не
персистентна и существует только в течение времени жизни виртуальной машины Java. Пользователи,
которым требуется персистентное хранилище, должны реализовать своё собственное хранилище.

Политика cookie по умолчанию, используемая `CookieManager`, — это
`CookiePolicy.ACCEPT_ORIGINAL_SERVER`, которая принимает cookie только от исходного сервера.
Поэтому в ответе `Set-Cookie` от сервера должен быть установлен атрибут «domain», и он должен
совпадать с доменом хоста в URL. Дополнительную информацию см. в
`java.net.HttpCookie.domainMatches`. Пользователи, которым требуется иная политика, должны
реализовать интерфейс `CookiePolicy` и передать его конструктору `CookieManager` либо установить
его уже созданному экземпляру `CookieManager` с помощью метода `setCookiePolicy(cookiePolicy)`.

При извлечении cookie из хранилища cookie `CookieManager` также применяет правило совпадения пути
(*path-match rule*) из раздела 3.3.4 RFC 2965. Поэтому у cookie также должен быть установлен
атрибут «path», чтобы правило совпадения пути можно было применить перед извлечением cookie из
хранилища.

Итак, `CookieManager` предоставляет каркас (*framework*) для работы с cookie и хорошую реализацию
`CookieStore` по умолчанию. `CookieManager` хорошо настраивается, позволяя вам установить
собственное хранилище `CookieStore`, политику `CookiePolicy` или и то, и другое.

## Настраиваемый CookieManager

Можно настроить два аспекта класса `CookieManager` — политику `CookiePolicy` и хранилище
`CookieStore`.

### CookiePolicy

Для удобства `CookiePolicy` определяет следующие предопределённые политики принятия cookie:

- `CookiePolicy.ACCEPT_ORIGINAL_SERVER` принимает cookie только от исходного сервера.
- `CookiePolicy.ACCEPT_ALL` принимает все cookie.
- `CookiePolicy.ACCEPT_NONE` не принимает ни одного cookie.
- Вы также можете определить собственную политику cookie, реализовав метод `shouldAccept`
  интерфейса `CookiePolicy`. Затем эту `CookiePolicy` можно использовать, передав её
  многоаргументному конструктору `CookieManager` или вызвав метод
  `setCookiePolicy(cookiePolicy)`, чтобы изменить уже существующий менеджер cookie.

Ниже приведён пример политики cookie, которая отклоняет cookie от доменов, находящихся в
чёрном списке (*blacklist*), прежде чем применить политику
`CookiePolicy.ACCEPT_ORIGINAL_SERVER`:

```java
import java.net.*;

public class BlacklistCookiePolicy implements CookiePolicy {
    String[] blacklist;

    public BlacklistCookiePolicy(String[] list) {
        blacklist = list;
    }

    public boolean shouldAccept(URI uri, HttpCookie cookie)  {
        String host;
        try {
            host =  InetAddress.getByName(uri.getHost()).getCanonicalHostName();
        } catch (UnknownHostException e) {
            host = uri.getHost();
        }

        for (int i = 0; i<blacklist.length; i++) {
	    if (HttpCookie.domainMatches(blacklist[i], host)) {
                return false;
            }
        }

        return CookiePolicy.ACCEPT_ORIGINAL_SERVER.shouldAccept(uri, cookie);
    }
}
```

Когда вы создаёте экземпляр `BlacklistCookiePolicy`, вы передаёте ему массив строк,
представляющих домены, от которых вы не хотите принимать cookie. Затем вы устанавливаете этот
экземпляр `BlacklistCookiePolicy` как политику cookie для вашего `CookieManager`. Например:

```java
String[] list = new String[]{ ".example.com" };
CookieManager cm = new CookieManager(null, new BlacklistCookiePolicy(list));
CookieHandler.setDefault(cm);
```

Этот пример кода не будет принимать cookie от таких хостов, как:

- host.example.com
- domain.example.com

Однако этот же пример кода будет принимать cookie от таких хостов, как:

- example.com
- example.org
- myhost.example.org

### CookieStore

`CookieStore` — это интерфейс, представляющий область хранения cookie. `CookieManager` добавляет
cookie в `CookieStore` для каждого HTTP-ответа и извлекает cookie из `CookieStore` для каждого
HTTP-запроса.

Вы можете реализовать этот интерфейс, чтобы предоставить собственное хранилище `CookieStore`, и
передать его `CookieManager` при создании. Установить `CookieStore` после того, как экземпляр
`CookieManager` уже создан, нельзя. Однако вы можете получить ссылку на хранилище cookie,
вызвав `CookieManager.getCookieStore()`. Это бывает полезно, поскольку позволяет вам
задействовать реализацию хранилища `CookieStore` в памяти по умолчанию, предоставляемую Java SE,
и дополнить её функциональность.

Например, вы можете захотеть создать персистентное хранилище cookie, которое сохраняло бы cookie,
чтобы их можно было использовать даже после перезапуска виртуальной машины Java. Ваша реализация
работала бы примерно так:

1. Любые ранее сохранённые cookie считываются.
2. Во время выполнения cookie сохраняются и извлекаются из памяти.
3. Перед выходом cookie записываются в персистентное хранилище.

Ниже приведён неполный пример такого хранилища cookie. Этот пример показывает, как задействовать
хранилище cookie в памяти по умолчанию из Java SE и как можно расширить его функциональность:

```java
import java.net.*;
import java.util.*;

public class PersistentCookieStore implements CookieStore, Runnable {
    CookieStore store;

    public PersistentCookieStore() {
        // получить хранилище cookie в памяти по умолчанию
        store = new CookieManager().getCookieStore();

        // todo: считать cookie из персистентного хранилища
        // и добавить их в store

        // добавить хук завершения работы, чтобы записать cookie из памяти
        Runtime.getRuntime().addShutdownHook(new Thread(this)); 
    }

    public void run() {
        // todo: записать cookie из store в персистентное хранилище
    }

    public void	add(URI uri, HttpCookie cookie) {
        store.add(uri, cookie);
    }

    public List<HttpCookie> get(URI uri) {
        return store.get(uri);
    }

    public List<HttpCookie> getCookies() {
        return store.getCookies();
    }
    
    public List<URI> getURIs() {
        return store.getURIs();
    }

    public boolean remove(URI uri, HttpCookie cookie) {
        return store.remove(uri, cookie);
    }

    public boolean removeAll()  {
        return store.removeAll();
    }
}
```

## Источник

- [Working With Cookies (индекс урока)](https://docs.oracle.com/javase/tutorial/networking/cookies/index.html) — официальное руководство Oracle.
- [HTTP State Management With Cookies](https://docs.oracle.com/javase/tutorial/networking/cookies/definition.html) — официальное руководство Oracle.
- [CookieHandler Callback Mechanism](https://docs.oracle.com/javase/tutorial/networking/cookies/cookiehandler.html) — официальное руководство Oracle.
- [Default CookieManager](https://docs.oracle.com/javase/tutorial/networking/cookies/cookiemanager.html) — официальное руководство Oracle.
- [Custom CookieManager](https://docs.oracle.com/javase/tutorial/networking/cookies/custom.html) — официальное руководство Oracle.
