# Урок 3. Расширенные возможности Java RIA

**Трейл:** Deployment · **Оригинал:** [Doing More With Java Rich Internet Applications](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/index.html)
**Связанные области:** [[18-build-tools]] · **Вопросы:** build-tools

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок объединяет страницы
> *Doing More With Java Rich Internet Applications*, *Setting Trusted Arguments and Secure
> Properties*, *System Properties*, *JNLP API*, *Accessing the Client Using JNLP API*, *Cookies*,
> *Accessing Cookies*, *Security in Rich Internet Applications*, *Guidelines for Securing Rich
> Internet Applications* и *Questions and Exercises*.
>
> **Примечание.** Технология RIA (богатые интернет-приложения) — апплеты (*applets*) и Java Web
> Start — **устарела**. Подключаемый модуль браузера Java Plug-In и Java Web Start удалены из
> современных версий Java. Руководство написано для JDK 8 и сохраняется здесь как исторический
> справочный материал; в новых проектах эти механизмы не применяются.

Апплеты, запускаемые с помощью протокола сетевого запуска Java (Java Network Launch Protocol,
JNLP), обладают возможностями, схожими с возможностями приложений Java Web Start. Этот урок
охватывает темы, общие для разработки и развёртывания апплетов и приложений Java Web Start
(вместе они называются **богатыми интернет-приложениями**, rich Internet applications, RIA).
Если вы не знакомы с апплетами или приложениями Java Web Start, изучите соответствующие уроки
руководства Java:

- О разработке и развёртывании апплетов — урок *Java Applets*.
- О разработке и развёртывании приложений Java Web Start — урок *Java Web Start*.

> **Примечание (оригинала).** Перед тем как продолжить, убедитесь, что на клиентской машине
> установлен как минимум Java SE Development Kit (JDK) 6 update 10. Это необходимо, чтобы
> просматривать примеры богатых интернет-приложений и читать последующие разделы без помех.

## Установка доверенных аргументов и защищённых свойств

Для своего богатого интернет-приложения (RIA) можно задать некоторые аргументы виртуальной
машины Java (Java Virtual Machine) и защищённые свойства (*secure properties*) в файле JNLP
этого приложения. Для апплетов аргументы можно также задавать в параметре `java_arguments`
тега `<applet>`. Помимо предопределённого набора защищённых свойств, можно объявлять новые
защищённые свойства, добавляя к имени свойства префикс `jnlp.` или `javaws.`. Свойства
извлекаются в приложении методом `System.getProperty`.

Рассмотрим апплет «Properties and Arguments Demo». В его файле JNLP `appletpropsargs.jnlp`
заданы следующие аргументы виртуальной машины Java и свойства:

- `-Xmx` — защищённый аргумент со значением `256M`;
- `sun.java2d.noddraw` — предопределённое защищённое свойство со значением `true`;
- `jnlp.myProperty` — пользовательское защищённое свойство со значением «a user-defined property».

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jnlp spec="1.0+" codebase="" href="">
    <information>
        <title>Properties and Arguments Demo Applet</title>
        <vendor>Dynamic Team</vendor>
    </information>
    <resources>
        <!-- Ресурсы приложения -->
        <j2se version="1.6+"
              href="http://java.sun.com/products/autodl/j2se"
              <!-- защищённый аргумент виртуальной машины Java -->
              java-vm-args="-Xmx256M"/>
        <jar href="applet_PropertiesAndVMArgs.jar"
            main="true" />
            <!-- защищённые свойства -->
        <property name="sun.java2d.noddraw"
            value="true"/>
        <property name="jnlp.myProperty"
            value="a user-defined property"/>
    </resources>
    <applet-desc
         name="Properties and Arguments Demo Applet"
         main-class="PropertiesArgsDemoApplet"
         width="800"
         height="50">
     </applet-desc>
     <update check="background"/>
</jnlp>
```

Класс `PropertiesArgsDemoApplet` использует метод `System.getProperty` для извлечения свойства
`java.version` и других свойств, заданных в файле JNLP, а затем отображает эти свойства.

```java
import javax.swing.JApplet;
import javax.swing.SwingUtilities;
import javax.swing.JLabel;

public class PropertiesArgsDemoApplet extends JApplet {
    public void init() {
        final String javaVersion = System.getProperty("java.version");
        final String  swing2dNoDrawProperty = System.getProperty("sun.java2d.noddraw");
        final String  jnlpMyProperty = System.getProperty("jnlp.myProperty");

        try {
            SwingUtilities.invokeAndWait(new Runnable() {
                public void run() {
                    createGUI(javaVersion, swing2dNoDrawProperty, jnlpMyProperty);
                }
            });
        } catch (Exception e) {
            System.err.println("createGUI didn't successfully complete");
        }
    }
    private void createGUI(String javaVersion, String swing2dNoDrawProperty, String jnlpMyProperty) {
        String text = "Properties: java.version = " + javaVersion +
                ",  sun.java2d.noddraw = " + swing2dNoDrawProperty +
                ",   jnlp.myProperty = " + jnlpMyProperty;
        JLabel lbl = new JLabel(text);
        add(lbl);
    }
}
```

## Системные свойства

Этот раздел перечисляет системные свойства, доступные богатым интернет-приложениям (RIA),
которые ограничены песочницей безопасности (*security sandbox*) и запускаются с использованием
JNLP или без него. Некоторые системные свойства недоступны приложениям из песочницы.

### Защищённые системные свойства, доступные всем RIA

Все приложения могут извлекать следующие защищённые системные свойства:

- `java.class.version`
- `java.vendor`
- `java.vendor.url`
- `java.version`
- `os.name`
- `os.arch`
- `os.version`
- `file.separator`
- `path.separator`
- `line.separator`

### Защищённые системные свойства, доступные RIA, запущенным с помощью JNLP

Приложения, запущенные с помощью JNLP, могут устанавливать и извлекать следующие защищённые
свойства:

- `awt.useSystemAAFontSettings`
- `http.agent`
- `http.keepAlive`
- `java.awt.syncLWRequests`
- `java.awt.Window.locationByPlatform`
- `javaws.cfg.jauthenticator`
- `javax.swing.defaultlf`
- `sun.awt.noerasebackground`
- `sun.awt.erasebackgroundonresize`
- `sun.java2d.d3d`
- `sun.java2d.dpiaware`
- `sun.java2d.noddraw`
- `sun.java2d.opengl`
- `swing.boldMetal`
- `swing.metalTheme`
- `swing.noxp`
- `swing.useSystemFontSettings`

### Запрещённые системные свойства

Приложения из песочницы **не могут** обращаться к следующим системным свойствам:

- `java.class.path`
- `java.home`
- `user.dir`
- `user.home`
- `user.name`

## JNLP API

Богатые интернет-приложения (RIA) могут использовать программный интерфейс протокола сетевого
запуска Java (JNLP API) для выполнения обширных операций в окружении пользователя. При запуске
с помощью JNLP даже **неподписанные** приложения могут выполнять следующие операции **с
разрешения пользователя**:

- использовать API `FileOpenService` и `FileSaveService` для доступа к файловой системе
  пользователя;
- использовать API `ClipboardService` для доступа к общесистемному буферу обмена
  (*clipboard*);
- использовать API `PrintService` для доступа к функциям печати;
- использовать API `PersistenceService` для доступа к постоянному хранилищу
  (*persistence storage*);
- использовать API `DownloadService`, чтобы управлять тем, как приложение загружается и
  кэшируется;
- использовать API `DownloadServiceListener`, чтобы отслеживать ход загрузки приложения;
- использовать API `SingleInstanceService`, чтобы решать, как обрабатывать аргументы при
  запуске нескольких экземпляров приложения;
- использовать API `ExtendedService`, чтобы запросить разрешение на открытие определённых
  файлов, которые ранее не открывались.

Полный список возможностей, доступных приложениям, запущенным с помощью JNLP, приведён в
документации [JNLP API](https://docs.oracle.com/javase/8/docs/jre/api/javaws/jnlp/javax/jnlp/package-summary.html).

## Доступ к клиенту через JNLP API

При запуске с помощью JNLP богатые интернет-приложения (RIA) могут обращаться к клиенту с
разрешения пользователя. Чтобы понять, как пользоваться службами JNLP API, рассмотрим пример
апплета-текстового редактора (Text Editor). Текстовый редактор содержит текстовую область и
кнопки «Open» (Открыть), «Save» (Сохранить) и «SaveAs» (Сохранить как). С его помощью можно
открыть существующий текстовый файл, отредактировать его и сохранить обратно на диск.

Основные классы:

- `TextEditor` — формирует пользовательский интерфейс;
- `TextEditorApplet` — отображает редактор в виде апплета;
- `FileHandler` — содержит основную функциональность, связанную с использованием служб JNLP API.

Помните: описанные здесь приёмы применимы и к приложениям Java Web Start.

### Получение ссылок на службы

Чтобы воспользоваться службой JNLP, сначала нужно получить ссылку на неё. Метод `initialize`
класса `FileHandler` получает ссылки на службы JNLP, как показано в следующем фрагменте кода:

```java
private static synchronized void initialize() {
    ...
    try {
        fos = (FileOpenService)
            ServiceManager.lookup("javax.jnlp.FileOpenService");
        fss = (FileSaveService)
            ServiceManager.lookup("javax.jnlp.FileSaveService");
    } catch (UnavailableServiceException e) {
        ...
    }
}
```

### Вызов методов службы

Получив ссылку на нужные службы, вызывайте их методы для выполнения требуемых операций. Метод
`open` класса `FileHandler` вызывает метод `openFileDialog` класса `FileOpenService`, чтобы
показать диалог выбора файла. Метод `open` возвращает содержимое выбранного файла.

```java
public static String open() {
    initialize();
    try {
        fc = fos.openFileDialog(null, null);
        return readFromFile(fc);
    } catch (IOException ioe) {
        ioe.printStackTrace(System.out);
        return null;
    }
}
```

Аналогично методы `save` и `saveAs` класса `FileHandler` вызывают соответствующие методы класса
`FileSaveService`, чтобы пользователь мог выбрать имя файла и сохранить содержимое текстовой
области на диск.

```java
public static void saveAs(String txt) {
    initialize();
    try {
        if (fc == null) {
            // Если ещё не сохранён.
            // «Сохранить как» работает как «Сохранить»
            save(txt);
        } else {
            fc = fss.saveAsFileDialog(null, null,
                                       fc);
            save(txt);
        }
    } catch (IOException ioe) {
        ioe.printStackTrace(System.out);
    }
}
```

Во время выполнения, когда приложение пытается открыть или сохранить файл, пользователь видит
диалог безопасности с вопросом, разрешить ли это действие. Операция продолжится, только если
пользователь разрешит приложению доступ к своему окружению.

Полный исходный код класса `FileHandler`:

```java
// добавьте javaws.jar в classpath при компиляции
import javax.jnlp.FileOpenService;
import javax.jnlp.FileSaveService;
import javax.jnlp.FileContents;
import javax.jnlp.ServiceManager;
import javax.jnlp.UnavailableServiceException;
import java.io.*;

public class FileHandler {

    static private FileOpenService fos = null;
    static private FileSaveService fss = null;
    static private FileContents fc = null;

    // получает ссылки на службы JNLP
    private static synchronized void initialize() {
        if (fss != null) {
            return;
        }
        try {
            fos = (FileOpenService) ServiceManager.lookup("javax.jnlp.FileOpenService");
            fss = (FileSaveService) ServiceManager.lookup("javax.jnlp.FileSaveService");
        } catch (UnavailableServiceException e) {
            fos = null;
            fss = null;
        }
    }

    // показывает диалог открытия файла и читает выбранный файл через FileOpenService
    public static String open() {
        initialize();
        try {
            fc = fos.openFileDialog(null, null);
            return readFromFile(fc);
        } catch (IOException ioe) {
            ioe.printStackTrace(System.out);
            return null;
        }
    }

    // показывает диалог сохранения файла и сохраняет файл через FileSaveService
    public static void save(String txt) {
        initialize();
        try {
            // Показать диалог сохранения, если имя ещё не задано
            if (fc == null) {
                fc = fss.saveFileDialog(null, null,
                        new ByteArrayInputStream(txt.getBytes()), null);
                // файл сохранён, готово
                return;
            }
            // использовать только когда имя файла известно
            if (fc != null) {
                writeToFile(txt, fc);
            }
        } catch (IOException ioe) {
            ioe.printStackTrace(System.out);
        }
    }

    // показывает диалог «Сохранить как» и сохраняет файл через FileSaveService
    public static void saveAs(String txt) {
        initialize();
        try {
            if (fc == null) {
                // Если ещё не сохранён. «Сохранить как» работает как «Сохранить»
                save(txt);
            } else {
                fc = fss.saveAsFileDialog(null, null, fc);
                save(txt);
            }
        } catch (IOException ioe) {
            ioe.printStackTrace(System.out);
        }
    }

    private static void writeToFile(String txt, FileContents fc) throws IOException {
        int sizeNeeded = txt.length() * 2;
        if (sizeNeeded > fc.getMaxLength()) {
            fc.setMaxLength(sizeNeeded);
        }
        BufferedWriter os = new BufferedWriter(new OutputStreamWriter(fc.getOutputStream(true)));
        os.write(txt);
        os.close();
    }

    private static String readFromFile(FileContents fc) throws IOException {
        if (fc == null) {
            return null;
        }
        BufferedReader br = new BufferedReader(new InputStreamReader(fc.getInputStream()));
        StringBuffer sb = new StringBuffer((int) fc.getLength());
        String line = br.readLine();
        while (line != null) {
            sb.append(line);
            sb.append("\n");
            line = br.readLine();
        }
        br.close();
        return sb.toString();
    }
}
```

> **Примечание о компиляции.** Чтобы скомпилировать Java-код, ссылающийся на классы пакета
> `javax.jnlp`, включите в свой classpath файл `<путь к вашему JDK>/jre/lib/javaws.jar`. Во
> время выполнения среда Java Runtime Environment автоматически делает эти классы доступными
> приложениям.

## Cookie-файлы

Веб-приложения обычно представляют собой серию запросов и ответов протокола передачи гипертекста
(Hypertext Transfer Protocol, HTTP). Поскольку HTTP — протокол без сохранения состояния
(*stateless*), информация между HTTP-запросами автоматически не сохраняется. Чтобы хранить
информацию о состоянии на стороне клиента, веб-приложения используют **cookie-файлы**. Cookie
позволяют хранить сведения о пользователе, о его корзине покупок и тому подобное.

### Типы cookie-файлов

Бывают два типа cookie:

- **Сеансовые cookie** (*session cookies*) — хранятся в памяти и доступны, пока пользователь
  работает с веб-приложением. Сеансовые cookie теряются при выходе пользователя из приложения.
  Такие cookie идентифицируются по идентификатору сеанса (*session ID*) и чаще всего
  используются для хранения сведений о корзине покупок.
- **Постоянные cookie** (*permanent cookies*) — используются для хранения долговременной
  информации, например пользовательских настроек и данных идентификации пользователя.
  Постоянные cookie хранятся в постоянном хранилище и не теряются при выходе из приложения.
  Постоянные cookie теряются по истечении срока их действия.

### Поддержка cookie-файлов в богатых интернет-приложениях

Богатые интернет-приложения (апплеты и приложения Java Web Start) поддерживают сеансовые и
постоянные cookie. Конкретное хранилище cookie зависит от браузера и операционной системы на
клиенте.

Подробнее о cookie:

- урок *Working With Cookies* в руководстве Java;
- документация API для класса `CookieManager` и связанных классов.

## Доступ к cookie-файлам

В своём богатом интернет-приложении (RIA) можно устанавливать и извлекать cookie. Cookie могут
расширять возможности приложения. Например, представьте, что у вас есть апплеты на разных
веб-страницах. Апплет на одной странице не может напрямую обращаться к апплету на другой
странице или делиться с ним информацией. В этом случае cookie обеспечивают важную связь между
апплетами и помогают одному апплету передавать информацию другому апплету на другой веб-странице.
Приложения Java Web Start также могут использовать cookie для хранения информации на клиенте.

В примере «Cookie Applet» есть класс `CookieAccessor`, который извлекает и устанавливает cookie.

### Извлечение cookie-файлов

Следующий фрагмент кода показывает метод `getCookieUsingCookieHandler` класса `CookieAccessor`:

```java
public void getCookieUsingCookieHandler() {
    try {
        // Создаём экземпляр CookieManager;
        // обязательно задаём CookiePolicy
        CookieManager manager = new CookieManager();
        manager.setCookiePolicy(CookiePolicy.ACCEPT_ALL);
        CookieHandler.setDefault(manager);

        // получаем содержимое через URLConnection;
        // cookie устанавливаются веб-сайтом
        URL url = new URL("http://host.example.com");
        URLConnection connection = url.openConnection();
        connection.getContent();

        // получаем cookie из нижележащего
        // CookieStore
        CookieStore cookieJar =  manager.getCookieStore();
        List <HttpCookie> cookies =
            cookieJar.getCookies();
        for (HttpCookie cookie: cookies) {
          System.out.println("CookieHandler retrieved cookie: " + cookie);
        }
    } catch(Exception e) {
        System.out.println("Unable to get cookie using CookieHandler");
        e.printStackTrace();
    }
}
```

Класс `CookieManager` — главная точка входа для управления cookie. Создайте экземпляр класса
`CookieManager` и задайте его `CookiePolicy`. Установите этот экземпляр `CookieManager` как
обработчик cookie по умолчанию (`CookieHandler`).

Откройте соединение `URLConnection` с выбранным веб-сайтом.

Затем извлеките cookie из нижележащего хранилища `CookieStore` методом `getCookies`.

### Установка cookie-файлов

Следующий фрагмент кода показывает метод `setCookieUsingCookieHandler` класса `CookieAccessor`:

```java
public void setCookieUsingCookieHandler() {
    try {
        // создаём экземпляр CookieManager
        CookieManager manager = new CookieManager();
        CookieHandler.setDefault(manager);
        CookieStore cookieJar =  manager.getCookieStore();

        // создаём cookie
        HttpCookie cookie = new HttpCookie("UserName", "John Doe");

        // добавляем cookie в CookieStore для
        // конкретного URL
        URL url = new URL("http://host.example.com");
        cookieJar.add(url.toURI(), cookie);
        System.out.println("Added cookie using cookie handler");
    } catch(Exception e) {
        System.out.println("Unable to set cookie using CookieHandler");
        e.printStackTrace();
    }
}
```

Как показано в разделе «Извлечение cookie-файлов», класс `CookieManager` — главная точка входа
для управления cookie. Создайте экземпляр класса `CookieManager` и установите его как обработчик
cookie по умолчанию (`CookieHandler`).

Создайте нужный `HttpCookie` с необходимой информацией. В примере создаётся новый `HttpCookie`,
который задаёт `UserName` равным `John Doe`.

Затем добавьте cookie в нижележащее хранилище cookie.

### Запуск примера «Cookie Applet»

Чтобы получить доступ к cookie, нужно подписать JAR-файл приложения и запросить разрешение на
работу за пределами песочницы безопасности. О том, как подписывать JAR-файлы, см. документацию
инструмента `jarsigner`. О запросе разрешений см. раздел «Безопасность богатых
интернет-приложений».

## Безопасность богатых интернет-приложений

Модель безопасности богатых интернет-приложений (RIA) призвана защитить пользователя от
вредоносных интернет-приложений. Этот раздел рассматривает аспекты безопасности, общие для
апплетов и приложений Java Web Start. Дополнительные сведения см. в темах:

- *What Applets Can and Cannot Do* (Что апплеты могут и чего не могут делать);
- *Java Web Start and Security* (Java Web Start и безопасность).

Приложения могут быть ограничены песочницей безопасности Java или запрашивать разрешение на
доступ к ресурсам за её пределами. При первом запуске приложения пользователю предлагается дать
разрешение на запуск. Отображаемый диалог содержит сведения о сертификате подписавшего и
указывает, запрашивает ли приложение разрешение на работу за пределами песочницы. На основе этого
пользователь может осознанно решить, запускать ли приложение.

Применяйте следующие рекомендации, чтобы повысить безопасность своих приложений.

- Подписывайте JAR-файл приложения сертификатом признанного центра сертификации (*certificate
  authority*). Подробнее см. тему *Signing and Verifying JAR Files*.
- Если приложению требуется доступ за пределами песочницы безопасности, укажите элемент
  `all-permissions` в файле JNLP приложения. Иначе оставьте приложение работать в песочнице по
  умолчанию. Следующий фрагмент показывает элемент `all-permissions` в файле JNLP приложения.

  ```xml
  <security>
     <all-permissions/>
  </security>
  ```

  Если используется тег `<applet>`, сведения о настройке уровня разрешений см. в теме
  *Deploying With the Applet Tag*.
- Файл JNLP может включать только JAR-файлы, подписанные одним и тем же сертификатом. Если у вас
  есть JAR-файлы, подписанные разными сертификатами, укажите их в отдельных файлах JNLP. В
  основном файле JNLP приложения укажите элемент `component-desc`, чтобы включить другие файлы
  JNLP как компонентные расширения. См. тему *Structure of the JNLP File*.
- Модель безопасности приложений не позволяет коду JavaScript с веб-страницы вызывать
  чувствительный к безопасности код в подписанном JAR-файле, пока вы явно это не разрешите. В
  подписанном JAR-файле оберните участок кода, который должен вызываться из JavaScript, в блок
  `AccessController.doPrivileged`. Это позволяет коду JavaScript выполняться с повышенными
  правами при выполнении кода внутри блока `doPrivileged`.
- По возможности избегайте смешивания привилегированных и песочничных компонентов в одном
  приложении, так как это может вызывать предупреждения безопасности о смешанном коде. Подробнее
  см. *Mixing Privileged Code and Sandbox Code*.
- Включайте атрибуты `Permissions` и `Codebase` в манифест JAR-файла, чтобы приложение
  запрашивало только указанные вами разрешения и обращалось из правильного расположения. См.
  *JAR File Manifest Attributes for Security*.
- Атрибуты манифеста JAR-файла позволяют ограничить доступ к приложению и помогают убедиться,
  что код не был подменён. Сведения обо всех доступных атрибутах манифеста см. в теме
  *Enhancing Security with Manifest Attributes*.

## Рекомендации по защите богатых интернет-приложений

Следующие рекомендации описывают шаги, которые можно предпринять, чтобы снизить уязвимость
богатых интернет-приложений (RIA), предоставляемых пользователям.

- Следуйте рекомендациям по безопасному кодированию.
- Тестируйте на последней версии JRE.
- Включайте атрибуты манифеста.
- Используйте подписанный файл JNLP.
- Подписывайте JAR-файлы и ставьте метку времени.
- Используйте протокол HTTPS.
- Избегайте локальных RIA.

### Следуйте рекомендациям по безопасному кодированию

Следуйте рекомендациям документа *Secure Coding Guidelines for the Java Programming Language*.
Раздел 4 «Accessibility and Extensibility» (Доступность и расширяемость) описывает, как
ограничить доступность классов и пакетов, что снижает уязвимость кода.

Код JavaScript считается небезопасным и по умолчанию ограничен песочницей безопасности. Сводите
к минимуму взаимодействие между приложением и кодом JavaScript. Используйте блок
`AccessController.doPrivileged` с осторожностью, поскольку он открывает доступ из любой
HTML-страницы или кода JavaScript.

### Тестируйте на последней версии JRE

Убедитесь, что приложение работает на последней, защищённой версии JRE. Платформа Java позволяет
приложениям указывать версию Java, необходимую для их работы, однако требовать от пользователей
поддерживать более одной версии JRE — особенно старых, небезопасных версий — это риск для
безопасности пользователя.

Одно из преимуществ приложений в том, что обновлённые версии автоматически загружаются в систему
пользователя. Тестируйте своё приложение с каждым обновлением JRE и убеждайтесь, что оно
работает. Если нужны изменения, обновите приложение на сервере, чтобы пользователи могли
установить последнюю версию JRE и продолжать пользоваться приложением.

### Включайте атрибуты манифеста

Добавляйте в манифест JAR-файла атрибуты, описывающие свойства приложения. Значения в файле JNLP
или в теге `<applet>` сравниваются со значениями в манифесте, чтобы проверить, что запускается
правильный код.

Запрашивайте разрешения песочницы, когда приложению не требуется доступ за её пределы. Песочница
Java обеспечивает дополнительную защиту пользователей, и они могут отказаться запускать
привилегированное приложение, если не понимают, почему оно запрашивает неограниченный доступ к их
системе.

Атрибуты манифеста также можно использовать для указания расположений, из которых можно
обращаться к приложению. Сюда входят расположения, из которых код JavaScript может вызывать
приложение, и расположения файлов JNLP или тегов `<applet>`, способных запустить приложение.

### Используйте подписанный файл JNLP

Если приложению нужен доступ к незащищённым системным свойствам или аргументам JVM, используйте
подписанный файл JNLP. Если требуется некоторое расхождение между внешним и внутренним файлами
JNLP, используйте шаблоны JNLP (*JNLP templates*).

Чтобы получить доступ к незащищённым системным свойствам или аргументам JVM, включите это
свойство или аргумент в файл JNLP.

### Подписывайте JAR-файлы и ставьте метку времени

Получите сертификат подписи кода (*code signing certificate*) у доверенного центра сертификации
и используйте его для подписи JAR-файлов приложения. Предоставляйте пользователям только
приложения, подписанные действительным сертификатом.

Подписывая JAR-файл, ставьте также метку времени (*time stamp*) на подпись. Метка времени
подтверждает, что сертификат был действителен в момент подписи JAR, поэтому приложение не
блокируется автоматически по истечении срока действия сертификата.

Самоподписанные и неподписанные приложения считаются небезопасными, и их запуск не разрешён, если
не настроен список сайтов-исключений (*exception site list*) или набор правил развёртывания
(*deployment rule set*) для конкретных приложений. Тем не менее самоподписание может быть полезно
для тестирования. Чтобы протестировать самоподписанное приложение, можно импортировать
самоподписанный сертификат в доверенное хранилище ключей (*trusted keystore*).

### Используйте протокол HTTPS

Используйте протокол HTTPS для веб-сервера, с которого пользователи получают ваше приложение.
Протокол HTTPS шифруется и проверяется сервером, что затрудняет подмену вашего приложения.

### Избегайте локальных RIA

Локальные приложения не предназначены для использования в продакшене. Чтобы пользователи
запускали именно тот код, который вы для них предназначили, размещайте своё приложение на сервере
приложений.

Для тестирования рекомендуется использовать веб-сервер. Другой вариант — добавить приложение в
список сайтов-исключений, который управляется на вкладке «Security» (Безопасность) Java Control
Panel.

## Вопросы и упражнения

### Вопросы

1. Верно или неверно: богатые интернет-приложения (RIA) могут устанавливать защищённые свойства,
   добавляя к имени свойства префикс `jnlp.`.
2. Верно или неверно: только подписанные приложения могут использовать JNLP API для доступа к
   файлам на клиенте.

### Упражнения

1. В следующий файл JNLP добавьте защищённое свойство с именем `jnlp.foo` и значением `true`.

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <jnlp spec="1.0+" codebase="" href="">
       <information>
           <title>Dynamic Tree Demo</title>
           <vendor>Dynamic Team</vendor>

       </information>
       <resources>
           <!-- Ресурсы приложения -->
           <j2se version="1.6+" href=
               "http://java.sun.com/products/autodl/j2se" />
           <jar href="DynamicTreeDemo.jar" main="true" />
       </resources>
       <applet-desc
          name="Dynamic Tree Demo Applet"
          main-class="components.DynamicTreeApplet"
          width="300"
          height="300">
        </applet-desc>
        <update check="background"/>
   </jnlp>
   ```

## Источник

- [Doing More With Java Rich Internet Applications](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/index.html) — официальное руководство Oracle (обзор урока).
- [Setting Trusted Arguments and Secure Properties](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/settingArgsProperties.html)
- [System Properties](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/properties.html)
- [JNLP API](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/jnlpAPI.html)
- [Accessing the Client Using JNLP API](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/usingJNLPAPI.html)
- [Cookies](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/cookies.html)
- [Accessing Cookies](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/accessingCookies.html)
- [Security in Rich Internet Applications](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/security.html)
- [Guidelines for Securing Rich Internet Applications](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/devGuidelines.html)
- [Questions and Exercises: Doing More With Java Rich Internet Applications](https://docs.oracle.com/javase/tutorial/deployment/doingMoreWithRIA/QandE/questions.html)
