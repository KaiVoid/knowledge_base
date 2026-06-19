# Урок 2. Разработка и развёртывание приложений Java Web Start

**Трейл:** Deployment · **Оригинал:** [Java Web Start](https://docs.oracle.com/javase/tutorial/deployment/webstart/index.html)
**Связанные области:** [[18-build-tools]] · **Вопросы:** build-tools

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет
> страницы *Developing a Java Web Start Application*, *Retrieving Resources*,
> *Deploying a Java Web Start Application*, *Setting Up a Web Server*,
> *Running a Java Web Start Application*, *Java Web Start and Security*,
> *Common Java Web Start Problems* и *Questions and Exercises*.
>
> **Примечание о неактуальности технологии.** Java Web Start была удалена из платформы
> начиная с **Java 11** (JDK 11, 2018 г.); вместе с ней удалён и протокол JNLP, и
> подключаемый модуль браузера Java Plug-In. Этот материал сохранён как перевод
> исторического руководства Oracle для JDK 8 и описывает технологию, недоступную в
> современных версиях Java. Для развёртывания самодостаточных приложений Oracle
> рекомендует инструмент `jlink`/`jpackage`.

Программное обеспечение Java Web Start даёт возможность запускать полнофункциональные
приложения одним щелчком мыши. Пользователи могут загружать и запускать приложения —
например, полноценный табличный процессор или интернет-чат — не проходя долгих процедур
установки.

С помощью Java Web Start пользователь запускает Java-приложение, щёлкнув по ссылке на
веб-странице. Ссылка указывает на файл **протокола сетевого запуска Java** (Java Network
Launch Protocol, JNLP), который предписывает программе Java Web Start загрузить, кэшировать
и запустить приложение.

Java Web Start даёт разработчикам и пользователям множество преимуществ при развёртывании:

- С помощью Java Web Start вы можете разместить единственное Java-приложение на
  веб-сервере для развёртывания на самые разные платформы, включая Windows, Linux и Solaris.
- Java Web Start поддерживает несколько одновременно установленных версий платформы Java.
  Приложение может запросить конкретную версию исполняющей среды Java (Java Runtime
  Environment, JRE), не вступая в конфликт с потребностями других приложений.
- Пользователи могут создать ярлык на рабочем столе для запуска приложения Java Web Start
  вне браузера.
- Java Web Start использует встроенную безопасность платформы Java. По умолчанию приложения
  имеют ограниченный доступ к локальному диску и сетевым ресурсам.
- Приложения, запущенные через Java Web Start, кэшируются локально, что повышает
  производительность.
- Обновления приложения Java Web Start загружаются автоматически при запуске приложения как
  отдельной программы с рабочего стола пользователя.

Java Web Start устанавливается как часть JRE. Пользователям не нужно устанавливать Java Web
Start отдельно или выполнять дополнительные действия, чтобы пользоваться приложениями
Java Web Start.

## Разработка приложения Java Web Start

Программу, спроектированную по компонентной архитектуре (component-based architecture), легко
разрабатывать и развёртывать как приложение Java Web Start. Рассмотрим пример приложения
Java Web Start с графическим интерфейсом на основе Swing. При компонентном проектировании
графический интерфейс (GUI) собирается из меньших строительных блоков, или компонентов. Для
создания GUI приложения используют такие общие шаги:

- Создайте класс `MyTopJPanel` — подкласс `JPanel`. Разместите компоненты GUI вашего
  приложения в конструкторе класса `MyTopJPanel`.
- Создайте класс `MyApplication` — подкласс класса `JFrame`.
- В методе `main` класса `MyApplication` создайте экземпляр класса `MyTopJPanel` и установите
  его как панель содержимого (content pane) объекта `JFrame`.

Следующие разделы рассматривают эти шаги подробнее на примере приложения Dynamic Tree Demo.
Если вы не знакомы со Swing, обратитесь к руководству *Creating a GUI with Swing*, чтобы
узнать больше о компонентах Swing GUI.

> **Примечание.** Если пример у вас не запускается, возможно, нужно включить интерпретатор
> JavaScript в браузере, чтобы скрипт Deployment Toolkit мог работать корректно.

### Создание верхнего класса `JPanel`

Создайте класс — подкласс `JPanel`. Эта верхняя `JPanel` служит контейнером для всех остальных
компонентов интерфейса. В следующем примере класс `DynamicTreePanel` является самой верхней
`JPanel`. Конструктор класса `DynamicTreePanel` вызывает другие методы, чтобы создать и
правильно разместить элементы управления интерфейса.

```java
public class DynamicTreePanel extends JPanel implements ActionListener {
    private int newNodeSuffix = 1;
    private static String ADD_COMMAND = "add";
    private static String REMOVE_COMMAND = "remove";
    private static String CLEAR_COMMAND = "clear";

    private DynamicTree treePanel;

    public DynamicTreePanel() {
        super(new BorderLayout());

        // Создаём компоненты.
        treePanel = new DynamicTree();
        populateTree(treePanel);

        JButton addButton = new JButton("Add");
        addButton.setActionCommand(ADD_COMMAND);
        addButton.addActionListener(this);

        JButton removeButton = new JButton("Remove");
        ....

        JButton clearButton = new JButton("Clear");
        ...

        // Размещаем всё по местам.
        treePanel.setPreferredSize(
            new Dimension(300, 150));
        add(treePanel, BorderLayout.CENTER);

        JPanel panel = new JPanel(new GridLayout(0,3));
        panel.add(addButton);
        panel.add(removeButton);
        panel.add(clearButton);
        add(panel, BorderLayout.SOUTH);
    }
    // ...
}
```

### Создание приложения

Для приложения с интерфейсом на основе Swing создайте класс — подкласс `javax.swing.JFrame`.

Создайте экземпляр вашего верхнего класса `JPanel` и установите его как панель содержимого
объекта `JFrame` в методе `main` приложения. Метод `main` класса `DynamicTreeApplication`
вызывает метод `createGUI` в потоке диспетчеризации событий AWT (AWT Event Dispatcher thread).

```java
package webstartComponentArch;

import javax.swing.JFrame;

public class DynamicTreeApplication extends JFrame {
    public static void main(String [] args) {
        DynamicTreeApplication app = new DynamicTreeApplication();
        app.createGUI();
    }

    private void createGUI() {
        // Создаём и настраиваем панель содержимого.
        DynamicTreePanel newContentPane = new DynamicTreePanel();
        newContentPane.setOpaque(true);
        setContentPane(newContentPane);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        pack();
        setVisible(true);
    }
}
```

### Преимущества отделения основной функциональности от механизма развёртывания

Приложение можно создать и иначе — убрать слой абстракции (отдельную верхнюю `JPanel`) и
разместить все элементы управления прямо в методе `main`. Недостаток построения GUI
непосредственно в методе `main` в том, что приложение будет труднее развернуть как апплет,
если позже вы решите это сделать.

В примере Dynamic Tree Demo основная функциональность вынесена в класс `DynamicTreePanel`.
Теперь тривиально поместить класс `DynamicTreePanel` в `JApplet` и развернуть его как апплет.

Таким образом, чтобы сохранить переносимость и оставить открытыми варианты развёртывания,
следуйте компонентному проектированию, описанному в этом разделе.

Загрузите исходный код примера *Dynamic Tree Demo*, чтобы поэкспериментировать дальше.

## Получение ресурсов

Используйте метод `getResource`, чтобы читать ресурсы из JAR-файла. Например, следующий код
извлекает изображения из JAR-файла.

```java
// Получаем текущий загрузчик классов
ClassLoader cl = this.getClass().getClassLoader();
// Создаём значки
Icon saveIcon  = new ImageIcon(cl.getResource("images/save.gif"));
Icon cutIcon   = new ImageIcon(cl.getResource("images/cut.gif"));
```

В примере предполагается, что в JAR-файле приложения присутствуют следующие записи:

- `images/save.gif`
- `images/cut.gif`

> **Примечание.** The Java Tutorials написаны для JDK 8. Примеры и приёмы, описанные на
> этой странице, не используют улучшений, появившихся в более поздних выпусках, и могут
> опираться на технологию, которая больше недоступна.

## Развёртывание приложения Java Web Start

Чтобы развернуть приложение Java Web Start, сначала скомпилируйте исходный код, упакуйте его
в JAR-файл и подпишите JAR-файл.

Приложения Java Web Start запускаются с помощью протокола сетевого запуска Java (Java Network
Launch Protocol, JNLP). Поэтому для развёртывания приложения вы должны создать JNLP-файл.

Скрипт Deployment Toolkit содержит полезные функции на JavaScript, которые можно использовать
для развёртывания приложений Java Web Start на веб-странице.

Если эти технологии развёртывания вам незнакомы, изучите урок *Deployment In-Depth*, прежде
чем продолжить.

Ниже приведены пошаговые инструкции по упаковке и развёртыванию приложения. Развёртывание
приложений Java Web Start показано на примере Dynamic Tree Demo. Возможно, вы захотите
оформить некоторые из следующих шагов в виде сборочных скриптов.

> **Примечание.** Если пример у вас не запускается, возможно, нужно включить интерпретатор
> JavaScript в браузере, чтобы скрипт Deployment Toolkit мог работать корректно.

1. Скомпилируйте Java-код приложения и убедитесь, что все файлы классов и ресурсы (например,
   изображения) находятся в отдельном каталоге.

   В приложении Dynamic Tree Demo скомпилированные классы помещаются в каталог
   `build/classes/webstartComponentArch`.

2. Создайте текстовый файл, содержащий любые атрибуты манифеста JAR-файла, которые нужны
   вашему апплету.

   Для апплета DynamicTree Demo создайте файл с именем `mymanifest.txt` в каталоге
   `build/classes` и добавьте атрибуты `Permissions`, `Codebase` и `Application-Name`.
   Апплету не требуется доступ к системным ресурсам пользователя, поэтому для прав используйте
   `sandbox`. В качестве базы кода (code base) укажите домен, с которого вы будете загружать
   пример, например `myserver.com`. Добавьте в файл `mymanifest.txt` следующие атрибуты.

   ```
   Permissions: sandbox
   Codebase: myserver.com
   Application-Name: Dynamic Tree Demo
   ```

   Доступны и другие атрибуты манифеста — для ограничения апплета доверенным кодом и для
   обеспечения безопасности апплетов, которым нужно вызывать переходы между привилегированным
   Java-кодом и Java-кодом из песочницы или у которых есть JavaScript-код, вызывающий апплет.
   Подробнее об доступных атрибутах манифеста — в уроке *Enhancing Security with Manifest
   Attributes*.

3. Создайте JAR-файл, содержащий файлы классов и ресурсы приложения. Включите атрибуты
   манифеста из файла `mymanifest.txt`, созданного на предыдущем шаге.

   Например, следующая команда создаёт JAR-файл с файлами классов из каталога
   `build/classes/webstartComponentArch` и файлом манифеста из каталога `build/classes`.

   ```
   % cd build/classes
   % jar cvfm  DynamicTreeDemo.jar  mymanifest.txt webstartComponentArch
   ```

   Подробнее о создании и использовании JAR-файлов — в уроке *Packaging Programs in JAR Files*.

4. Подпишите JAR-файл вашего апплета и проставьте метку времени для подписи. Используйте
   действительный актуальный сертификат подписи кода (code signing certificate), выданный
   доверенным удостоверяющим центром, чтобы дать пользователям гарантию, что запускать
   апплет безопасно.

   Дополнительная информация — в уроке *Signing JAR Files*.

   Если вы хотите использовать для безопасности подписанный JNLP-файл, создайте JNLP-файл,
   как описано в следующем шаге, и включите его в JAR-файл до подписания JAR-файла. См.
   *Signed JNLP Files* в руководстве *Java Platform, Standard Edition Deployment Guide*.

5. Создайте JNLP-файл, описывающий, как должно запускаться ваше приложение.

   Вот JNLP-файл, который используется для запуска приложения Dynamic Tree Demo. Для этого
   приложения права не запрашиваются, поэтому оно работает в песочнице безопасности. Исходный
   код `dynamictree_webstart.jnlp` следует ниже.

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <jnlp spec="1.0+" codebase=
   "https://docs.oracle.com/javase/tutorialJWS/samples/deployment/webstart_ComponentArch_DynamicTreeDemo"
       href="dynamictree_webstart.jnlp">
       <information>
           <title>Dynamic Tree Demo</title>
           <vendor>Dynamic Team</vendor>
       </information>
       <resources>
           <!-- Ресурсы приложения -->
           <j2se version="1.7+"
                 href="http://java.sun.com/products/autodl/j2se"/>
           <jar href="DynamicTreeDemo.jar"
               main="true" />

       </resources>
       <application-desc
            name="Dynamic Tree Demo Application"
            main-class=
              "webstartComponentArch.DynamicTreeApplication"
            width="300"
            height="300">
        </application-desc>
        <update check="background"/>
   </jnlp>
   ```

   Синтаксис и параметры JNLP-файла описаны в *Structure of the JNLP File*.

   > **Примечание.** Атрибуты `codebase` и `href` необязательны при развёртывании приложений
   > Java Web Start, которые будут работать как минимум на выпуске Java SE 6 update 18 или
   > более позднем. Вы обязаны указывать атрибуты `codebase` и `href` при развёртывании
   > приложений Java Web Start, которые будут работать с предыдущими выпусками исполняющей
   > среды Java.

6. Создайте HTML-страницу, с которой будет запускаться ваше приложение. Вызовите функции
   Deployment Toolkit, чтобы развернуть приложение Java Web Start.

   В примере приложение Dynamic Tree Demo развёрнуто в `JavaWebStartAppPage.html`.

   ```html
   <body>
       <!-- ... -->
       <script src=
         "https://www.java.com/js/deployJava.js"></script>
       <script>
           // используем JavaScript, чтобы получить расположение JNLP-файла
           // относительно HTML-страницы
           var dir = location.href.substring(0,
               location.href.lastIndexOf('/')+1);
           var url = dir + "dynamictree_webstart.jnlp";
           deployJava.createWebStartLaunchButton(url, '1.7.0');
       </script>
       <!-- ... -->
   </body>
   ```

   Если вы не уверены, будет ли у конечных пользователей включён интерпретатор JavaScript в
   браузере, вы можете развернуть приложение Java Web Start напрямую, создав ссылку на
   JNLP-файл следующим образом.

   ```html
   <a href="/абсолютный путь к JNLP-файлу/dynamictree_webstart.jnlp">Launch Notepad Application</a>
   ```

   Если вы развёртываете приложение Java Web Start через прямую ссылку, вы не сможете
   воспользоваться дополнительными проверками, которые предоставляют функции Deployment
   Toolkit. Подробнее — в разделе *Deploying a Java Web Start Application* урока
   *Deployment In-Depth*.

7. Поместите JAR-файл, JNLP-файл и HTML-страницу приложения в соответствующие папки.

   Для этого примера поместите `DynamicTreeDemo.jar`, `dynamictree_webstart.jnlp` и
   `JavaWebStartAppPage.html` в один и тот же каталог на локальной машине или веб-сервере.
   Предпочтительнее веб-сервер. Чтобы запустить с локальной машины, нужно добавить приложение
   в список исключений сайтов (exception site list), который управляется на вкладке Security
   панели управления Java (Java Control Panel).

8. Откройте HTML-страницу приложения в браузере, чтобы увидеть приложение. Согласитесь
   запустить приложение, когда появится запрос. Проверьте журнал Java Console на наличие
   сообщений об ошибках и отладочных сообщений.

## Настройка веб-сервера

Возможно, вам понадобится настроить веб-сервер для обработки файлов протокола сетевого
запуска Java (Java Network Launch Protocol, JNLP). Если веб-сервер настроен неправильно,
приложение Java Web Start не запустится при щелчке по ссылке на JNLP-файл.

Настройте веб-сервер так, чтобы файлам с расширением `.jnlp` соответствовал MIME-тип
`application/x-java-jnlp-file`.

Конкретные шаги настройки MIME-типа JNLP различаются в зависимости от веб-сервера. Например,
чтобы настроить веб-сервер Apache, нужно добавить следующую строку в файл `mime.types`.

```
application/x-java-jnlp-file JNLP
```

Для других веб-серверов смотрите инструкции по установке MIME-типов в их документации.

## Запуск приложения Java Web Start

Пользователи могут запускать приложения Java Web Start следующими способами:

- запуск приложения Java Web Start из браузера;
- запуск приложения Java Web Start из средства просмотра кэша Java (Java Cache Viewer);
- запуск приложения Java Web Start с рабочего стола.

> **Примечание.** Чтобы запускать приложения, развёрнутые с помощью технологии Java Web
> Start, у вас должна быть совместимая версия исполняющей среды Java (JRE). Полный комплект
> разработчика Java (Java Development Kit, JDK) не требуется.

### Запуск приложения Java Web Start из браузера

Вы можете запустить приложение Java Web Start из браузера, щёлкнув по ссылке на JNLP-файл
приложения. Следующий текст — пример ссылки на JNLP-файл.

```html
<a href="/some/path/Notepad.jnlp">Launch Notepad Application</a>
```

Java Web Start загружает и запускает приложение согласно инструкциям в JNLP-файле.

### Запуск приложения Java Web Start из средства просмотра кэша Java (Java Cache Viewer)

Если вы используете как минимум Java Platform, Standard Edition 6 или более позднюю версию,
вы можете запускать приложение Java Web Start через средство просмотра кэша Java (Java Cache
Viewer).

Когда Java Web Start впервые загружает приложение, информация из JNLP-файла приложения
сохраняется в локальном средстве просмотра кэша Java. Чтобы запустить приложение снова, вам
не нужно возвращаться на веб-страницу, с которой вы его впервые запустили; вы можете запустить
его из средства просмотра кэша Java.

Чтобы открыть средство просмотра кэша Java:

1. Откройте Панель управления (Control Panel).
2. Дважды щёлкните по значку Java. Откроется панель управления Java (Java Control Panel).
3. Выберите вкладку General.
4. Нажмите View. Откроется средство просмотра кэша Java.

Приложение указано на экране средства просмотра кэша Java.

Чтобы запустить приложение, выберите его и нажмите кнопку Run или дважды щёлкните по
приложению. Приложение запускается так же, как и с веб-страницы.

### Запуск приложения Java Web Start с рабочего стола

Вы можете добавить ярлык приложения Java Web Start на рабочий стол. Выберите приложение в
средстве просмотра кэша Java. Щёлкните правой кнопкой мыши и выберите Install Shortcuts или
нажмите кнопку Install.

На рабочий стол добавляется ярлык.

После этого вы можете запускать приложение Java Web Start так же, как любое нативное
приложение.

## Java Web Start и безопасность

В этом разделе описаны основы безопасности приложений, развёрнутых через Java Web Start.

Приложения, запущенные с помощью Java Web Start, по умолчанию работают в ограниченной среде,
известной как *песочница* (sandbox). В этой песочнице Java Web Start:

- защищает пользователей от вредоносного кода, который мог бы воздействовать на локальные
  файлы;
- защищает предприятия от кода, который мог бы попытаться получить доступ к данным в сетях
  или уничтожить их.

Приложения-песочницы (sandbox applications), запускаемые Java Web Start, остаются в этой
песочнице, то есть не могут получить доступ к локальным файлам или сети. Информацию см. в
разделе *Security in Rich Internet Applications*.

### Динамическая загрузка сертификатов HTTPS

Java Web Start динамически импортирует сертификаты, как это обычно делают браузеры. Для этого
Java Web Start устанавливает собственный обработчик `https`, используя системное свойство
`java.protocol.handler.pkgs`, чтобы инициализировать значения по умолчанию для
`SSLSocketFactory` и `HostnameVerifier`. Значения по умолчанию устанавливаются методами
`HttpsURLConnection.setDefaultSSLSocketFactory` и
`HttpsURLConnection.setDefaultHostnameVerifier`.

Если ваше приложение использует эти два метода, убедитесь, что они вызываются *после* того,
как Java Web Start инициализирует обработчик `https`, иначе ваш пользовательский обработчик
будет заменён обработчиком `https` по умолчанию от Java Web Start.

Вы можете гарантировать использование собственных `SSLSocketFactory` и `HostnameVerifier`,
сделав одно из следующего:

- установите собственный обработчик `https`, заменив обработчик `https` от Java Web Start;
- в вашем приложении вызывайте `HttpsURLConnection.setDefaultSSLSocketFactory` или
  `HttpsURLConnection.setDefaultHostnameVerifier` только после того, как создан первый объект
  URL вида `https`, что сначала выполнит код инициализации обработчика `https` от Java Web
  Start.

## Типичные проблемы с Java Web Start

В этом разделе рассмотрены некоторые типичные проблемы, с которыми вы можете столкнуться при
разработке и развёртывании приложений Java Web Start. После каждой проблемы приведён список
возможных причин и решений.

**Проблема.** Мой браузер показывает файл протокола сетевого запуска Java (JNLP) для моего
приложения как обычный текст.

Скорее всего, ваш веб-сервер не знает правильный MIME-тип для JNLP-файлов. Подробнее — в
разделе «Настройка веб-сервера».

Кроме того, если вы используете прокси-сервер, убедитесь, что возвращаются обновлённые версии
файлов: обновите метку времени ресурсов на веб-сервере, чтобы прокси обновили свои кэши.

**Проблема.** Когда я пытаюсь запустить свой JNLP-файл, я получаю следующую ошибку:

```
MissingFieldException[ The following required field is missing from the launch
  file: (<application-desc>|<applet-desc>|<installer-desc>|<component-desc>)]
        at com.sun.javaws.jnl.XMLFormat.parse(Unknown Source)
        at com.sun.javaws.jnl.LaunchDescFactory.buildDescriptor(Unknown Source)
        at com.sun.javaws.jnl.LaunchDescFactory.buildDescriptor(Unknown Source)
        at com.sun.javaws.jnl.LaunchDescFactory.buildDescriptor(Unknown Source)
        at com.sun.javaws.Main.launchApp(Unknown Source)
        at com.sun.javaws.Main.continueInSecureThread(Unknown Source)
        at com.sun.javaws.Main.run(Unknown Source)
        at java.lang.Thread.run(Unknown Source)
```

Часто эта ошибка возникает, когда ваш XML некорректно сформирован. Можно вглядываться в код,
пока не найдёте причину, но проще прогнать по файлу проверку синтаксиса XML. (Среды NetBeans
IDE и jEdit обе предоставляют средства проверки синтаксиса XML.)

Однако эта ошибка может возникать и в других ситуациях, и в данном случае она была вызвана
следующей строкой в остальном корректно сформированного XML-файла:

```xml
<description kind="short">Demonstrates choosing the drop location in the target <code>TransferHandler</code></description>
```

Ошибка была вызвана недопустимыми встроенными тегами `code`.

## Вопросы и упражнения

### Вопросы

1. В ссылке, которая должна запускать приложение Java Web Start, какой файл указывается как
   атрибут `href` тега `a`?

2. Какой MIME-тип должен распознавать веб-сервер, чтобы размещать приложения Java Web Start?

3. Какие два элемента должны быть указаны внутри элемента `resources` в JNLP-файле приложения?

4. Какой интерфейс даёт возможность управлять тем, как кэшируются ресурсы приложения Java
   Web Start?
   1. `BasicService`
   2. `DownloadService`
   3. `PersistenceService`
   4. `ExtendedService`

5. Верно или неверно: приложения Java Web Start по умолчанию работают в защищённой песочнице.

6. Верно или неверно: если приложение Java Web Start работает в защищённой песочнице,
   JAR-файлы приложения могут располагаться на разных серверах.

7. Что нужно сделать, чтобы приложение Java Web Start поддерживало операции вне защищённой
   песочницы?

### Упражнения

1. Напишите XML-код, который вы добавили бы в JNLP-файл, чтобы запросить для приложения полный
   доступ к клиентской системе.

2. Для приложения Java Web Start у вас есть два значка, `one.gif` и `two.gif`, в каталоге
   `images` внутри JAR-файла. Напишите код приложения, который вы использовали бы для доступа
   к этим изображениям.

## Источник

- [Lesson: Java Web Start](https://docs.oracle.com/javase/tutorial/deployment/webstart/index.html) — официальное руководство Oracle (The Java Tutorials, JDK 8).
- [Developing a Java Web Start Application](https://docs.oracle.com/javase/tutorial/deployment/webstart/developing.html)
- [Retrieving Resources](https://docs.oracle.com/javase/tutorial/deployment/webstart/retrievingResources.html)
- [Deploying a Java Web Start Application](https://docs.oracle.com/javase/tutorial/deployment/webstart/deploying.html)
- [Setting Up a Web Server](https://docs.oracle.com/javase/tutorial/deployment/webstart/settingUpWebServerMimeType.html)
- [Running a Java Web Start Application](https://docs.oracle.com/javase/tutorial/deployment/webstart/running.html)
- [Java Web Start and Security](https://docs.oracle.com/javase/tutorial/deployment/webstart/security.html)
- [Common Java Web Start Problems](https://docs.oracle.com/javase/tutorial/deployment/webstart/problems.html)
- [Questions and Exercises: Java Web Start](https://docs.oracle.com/javase/tutorial/deployment/webstart/QandE/questions.html)
