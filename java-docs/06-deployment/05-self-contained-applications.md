# Урок 5. Развёртывание самодостаточных приложений

**Трейл:** Deployment · **Оригинал:** [Deploying Self-Contained Applications](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/index.html)
**Связанные области:** [[18-build-tools]] · [[22-containers-devops]] · **Вопросы:** build-tools

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> урока *Deploying Self-Contained Applications*: вводную, *Pre-Requisites for Packaging
> Self-Contained Applications*, *Converting an Existing Application*, *Using File Associations*,
> *Adding an External Library*, *Providing a Default Argument*, *Using a Common Build File for
> All Platforms*, *Using Multiple Entry Points*, а также вопросы и упражнения с ответами.
>
> **Примечание Oracle.** Руководство написано для JDK 8. Примеры и приёмы, описанные здесь,
> не используют улучшений, появившихся в более поздних выпусках, и могут опираться на
> технологии, которые уже недоступны. Актуальные руководства см. на
> [Dev.java](https://dev.java/learn/).

## Что такое самодостаточное приложение

**Самодостаточное приложение** (*self-contained application*) — это единый устанавливаемый
пакет (*bundle*), который содержит как само ваше приложение, так и копию среды выполнения Java
(JRE), необходимую для его запуска. После установки такое приложение ведёт себя так же, как
любое нативное приложение. Поставляя пользователям самодостаточное приложение, вы избавляетесь
от проблем безопасности, связанных с запуском приложения в браузере.

Самодостаточное приложение можно настраивать: например, задать собственные значки (*icons*).
Можно настроить **ассоциации файлов** (*file associations*) — тогда при открытии пользователем
файла, который умеет обрабатывать ваше приложение, оно запускается автоматически. Поддерживаются
**несколько точек входа** (*multiple entry points*), что позволяет доставить целый набор
приложений в одном самодостаточном пакете.

Самодостаточные приложения упаковываются с помощью инструментов упаковки Java
(*Java Packaging tools*). Команда `javapackager` создаёт пакет самодостаточного приложения из
командной строки. Пакеты можно создавать и средствами NetBeans. В этом уроке описывается, как
создавать пакеты с помощью задач Ant (*Ant tasks*).

### Преимущества самодостаточных приложений

- Пользователь устанавливает приложение привычным ему установщиком (*installer*).
- Приложение работает как нативное.
- Вы контролируете версию JRE, которая используется приложением.
- Приложению не требуется браузер для запуска.

Платой за это является больший объём, занимаемый приложением на машине пользователя, поскольку
JRE поставляется в комплекте с приложением.

## Предварительные требования для упаковки

Для компиляции и упаковки приложения необходим комплект разработчика Java (JDK). Устанавливаемый
пакет должен создаваться **на той платформе, на которой будет работать** самодостаточное
приложение. Например, если ваше приложение работает в Windows и Linux, для создания пакета
`.exe` или `.msi` нужно запустить инструмент упаковки в Windows, а для создания файла `.rpm`
или `.deb` — запустить инструмент упаковки в Linux.

Для создания устанавливаемого пакета требуются **сторонние инструменты** (*third party tools*).
В следующей таблице перечислены инструменты для каждой поддерживаемой платформы.

| Платформа | Формат | Инструмент |
|-----------|--------|------------|
| Windows   | EXE    | Inno Setup 5 или новее |
| Windows   | MSI    | WiX Toolset 3.8 или новее |
| Linux     | RPM    | RPMBuild |
| Linux     | DEB    | Инструменты упаковки Debian |
| OS X      | DMG    | — |
| OS X      | PKG    | — |

## Преобразование существующего приложения

Любое самостоятельное (*standalone*) Java-приложение или приложение Java Web Start можно
упаковать как самодостаточное. Если у вас есть Java-апплет, сначала преобразуйте его в приложение
Java Web Start (см. *Re-writing a Java Applet as a Java Web Start Application*), которое затем
можно упаковать как самодостаточное приложение.

Перед преобразованием убедитесь, что для вашей платформы установлены все необходимые
предварительные требования (см. раздел «Предварительные требования для упаковки» выше).

В этом разделе демонстрация *Dynamic Tree Demo* из урока *Deploying a Java Web Start Application*
преобразуется в самодостаточное приложение.

### Подготовка каталогов

Определите и упорядочьте файлы, которые нужны вашему приложению. Простому приложению может
потребоваться только JAR-файл. Более сложному приложению могут понадобиться дополнительные
библиотеки или ресурсы. Самодостаточные приложения могут использовать и пользовательские
ресурсы — например, значки или файлы конфигурации.

Демонстрации *Dynamic Tree Demo* требуется только файл `DynamicTreeDemo.jar`, находящийся в
каталоге `/dist` проекта. HTML- и JNLP-файлы, нужные для версии приложения под Java Web Start,
здесь не требуются и игнорируются упаковщиками (*bundlers*) самодостаточных приложений.

Чтобы задать собственный значок для *Dynamic Tree Demo* (он представляет приложение после
установки на рабочий стол пользователя), для каждой поддерживаемой платформы предоставляется свой
значок. Эти значки помещаются в каталоги `/src/package/platform`. Значок предоставляется в
разном формате для каждой платформы: формат `.ico` для Windows, формат `.png` для Linux и формат
`.icns` для OS X.

В следующем примере показана структура каталогов проекта *Dynamic Tree Demo* **до** создания
самодостаточных пакетов:

```
/packager_DynamicTreeDemo     <--- проект приложения
   /dist
      DynamicTreeDemo.jar
      ...
   /src
      /package                <--- пользовательские ресурсы
         /linux
         /macosx
         /windows
      /webstartComponentArch  <--- исходные файлы приложения
      ...
```

### Подготовка файла сборки

Настройте задачи Ant для нужных задач упаковки. Эти задачи можно добавить в файл `build.xml`
проекта или поместить в отдельный файл, который импортируется файлом `build.xml`.

Для *Dynamic Tree Demo* файл `packager.xml` в корневом каталоге проекта содержит задачи Ant для
генерации пакетов самодостаточного приложения. Исходный текст файла `packager.xml` показан ниже:

```xml
<project name="DynamicTreePackaging" default="default" basedir="." xmlns:fx="javafx:com.sun.javafx.tools.ant">
    <echo>${java.home}/../lib/ant-javafx.jar</echo>
    <target name="package" depends="jar">
        <taskdef resource="com/sun/javafx/tools/ant/antlib.xml"
                 uri="javafx:com.sun.javafx.tools.ant"
                 classpath="${java.home}/../lib/ant-javafx.jar;src"/>

        <fx:deploy outdir="${basedir}/build/packager" 
                   outfile="DynamicTreeDemo"
                   nativeBundles="all"
                   verbose="false">

            <fx:application name="Dynamic Tree Demo"
                        mainClass="webstartComponentArch.DynamicTreeApplication"
                        version="1.0"
            />

            <fx:resources>
                <fx:fileset dir="dist" includes="DynamicTreeDemo.jar"/>
            </fx:resources>

            <fx:info title="Dynamic Tree Demo"
                     vendor="My Company"
                     description="A Demo of a Dynamic Swing Tree"
                     category="Demos"
                     copyright="(c) 2014 My Company"
                     license="3 Clause BSD"
            />

            <fx:bundleArgument arg="linux.bundleName" value="dynamic-tree-demo"/>
            <fx:bundleArgument arg="email" value="maintainer@example.com"/>
            <fx:bundleArgument arg="mac.CFBundleName" value="Java Tree Demo"/>
            <fx:bundleArgument arg="win.menuGroup" value="Java Demos"/>

        </fx:deploy>
    </target>
</project>
```

Для настройки задач Ant используйте следующие сведения:

- В качестве пространства имён используйте `xmlns:fx="javafx:com.sun.javafx.tools.ant"`.

- Задача `taskdef` должна выполняться до задачи `fx:deploy`. Атрибут `classpath` содержит
  расположение файла `ant-javafx.jar` из JDK и каталог с пользовательскими ресурсами. Для
  *Dynamic Tree Demo* атрибут `classpath` включает каталог `/src`, содержащий пользовательские
  значки.

- Поместите задачу `fx:deploy` внутрь нужной цели (*target*). Укажите выходной каталог, в который
  помещаются нативные двоичные файлы, и укажите, какие нативные двоичные файлы вы хотите получить.

  Если для нативных двоичных файлов указано `all`, генерируются все возможные двоичные файлы для
  той платформы, на которой выполняется этот файл задач, включая образ диска (*disk image*).
  Допустимые значения для всех платформ: `all`; `image` — генерирует каталог-файл на Windows и
  Linux и файл `.app` на OS X; `installer` — генерирует только устанавливаемые пакеты для
  платформы, без образа диска. Допустимые значения для двоичных файлов конкретных платформ: `exe`
  и `msi` для Windows; `deb` и `rpm` для Linux; `deb`, `pkg` и `mac.appStore` для OS X. Чтобы
  собрать выбранный двоичный файл, у вас должны быть установлены необходимые инструменты.

  Для *Dynamic Tree Demo* атрибут `outdir` задан как `${basedir}/build/packager`. `basedir`
  определён в элементе `project`, в данном случае это текущий каталог. Атрибут `nativeBundles`
  задан как `all`, поэтому собираются все форматы для платформы, на которой запущена задача
  упаковки.

- Атрибут `verbose` необязателен. Используйте его, чтобы получать диагностическую информацию.

- Укажите информацию о приложении. Имя приложения задаётся в атрибуте `name` элемента
  `fx:application` и атрибуте `title` элемента `fx:info`. Версия приложения задаётся в атрибуте
  `version` элемента `fx:application`. Используйте элемент `fx:info`, чтобы указать описание
  приложения, имя поставщика, лицензионную информацию и другие метаданные.

- Информация о JAR-файле и других ресурсах задаётся в элементе `fx:resources`.

- Информация о запуске задаётся в атрибуте `mainClass` элемента `fx:application`.

  Для *Dynamic Tree Demo* используется простая единственная точка входа —
  `webstartComponentArch.DynamicTreeApplication`, главный класс приложения.

- Прочие специфичные для платформы настройки задаются в элементах `fx:bundleArgument`. Аргументы,
  которые упаковщик не распознаёт, игнорируются, поэтому один файл сборки может содержать
  информацию упаковки для всех платформ.

  Для *Dynamic Tree Demo* применяются следующие настройки:

  - Имя пакета для Linux задано как `dynamic-tree-demo`.
  - Указан адрес электронной почты.
  - Имя, появляющееся в строке меню для OS X, задано как `Java Tree Demo`.
  - Имя группы меню, в которой хранится приложение для Windows, задано как `Java Demos`.

### Генерация пакетов

Запустите созданные задачи упаковки на той платформе, для которой вы хотите собрать пакет
самодостаточного приложения.

Для *Dynamic Tree Demo* выполните следующую команду из корневой папки проекта:

```bash
ant package
```

После завершения задачи упаковки каталог `build/packager/bundles` в проекте приложения содержит
сгенерированные нативные двоичные файлы.

В следующем примере показана структура каталогов проекта *Dynamic Tree Demo* **после** генерации
самодостаточных пакетов для Windows:

```
/packager_DynamicTreeDemo     <--- проект приложения
   /build
      /packager
         /bundles
            Dynamic Tree Demo         <--- образ-папка
            Dynamic Tree Demo-1.0.exe <--- установщик EXE
            Dynamic Tree Demo-1.0.msi <--- установщик MSI
      ...   
   /dist
      DynamicTreeDemo.jar
      ...
   /src
      /package                <--- пользовательские ресурсы
         /linux
         /macosx
         /windows
      /webstartComponentArch  <--- исходные файлы приложения
      ...
```

Обратите внимание: помимо самодостаточных пакетов инструмент упаковки всегда генерирует для
приложения файлы JAR, JNLP и HTML. Эти файлы дают другие варианты распространения вашего
приложения.

## Использование ассоциаций файлов

Одно из преимуществ предоставления пользователям самодостаточного приложения — возможность
настроить **ассоциации файлов** (*file associations*). Файлы определённых типов можно связать с
вашим приложением по MIME-типу или по расширению файла, чтобы для открытия связанного файла
использовалось именно ваше приложение. Например, если ваше приложение редактирует текстовые
файлы, можно настроить ассоциацию, которая запускает приложение, когда пользователь дважды
щёлкает по файлу с расширением `.txt`.

Демонстрация *File Association Demo* читает код на JavaScript и Groovy. Используя одновременно
MIME-типы и расширения файлов, приложение ассоциируется с файлами JavaScript и Groovy.

### Настройка ассоциаций файлов

Задачи Ant для генерации пакетов самодостаточного приложения находятся в файле `build.xml`
демонстрации *File Association Demo*. Элемент Ant `<fx:association>` используется для связывания
расширений файлов или MIME-типов с вашим приложением. Упаковщики Linux требуют MIME-тип,
упаковщики Windows требуют расширение файла, а упаковщики OS X требуют хотя бы одно из этих
свойств. Хорошая практика — использовать оба свойства с взаимно однозначным соответствием между
MIME-типом и расширением файла; это позволяет применять один и тот же файл сборки на нескольких
платформах.

Следующий код показывает, что нужно включить в элемент `fx:deploy`, чтобы связать приложение с
расширениями `.js` и `.groovy` и MIME-типами `text/javascript` и `text/x-groovy`:

```xml
<fx:info title="File Association Demo"
         vendor="MySamples"
         description="A Demo of File Associations for Java Packager"
         category="Demos"
         license="3 Clause BSD">
    <fx:association extension="js" mimetype="text/javascript" description="JavaScript Source"/>
    <fx:association extension="groovy" mimetype="text/x-groovy" description="Groovy Source"/>
</fx:info>
```

Если упаковщик не поддерживает ассоциации файлов, они игнорируются. Начиная с выпуска JDK 8u40,
ассоциации файлов поддерживают упаковщики Windows EXE и MSI, упаковщики Linux DEB и RPM, а также
упаковщик Mac `.app`. Упаковщики OS X PKG и DMG поддерживают ассоциации файлов через
использование упаковщика Mac `.app`.

### Запуск из связанных файлов

Ассоциации файлов настраиваются установщиком при установке пакета самодостаточного приложения в
систему пользователя. После установки приложения открытие связанного с ним файла приводит к
запуску приложения. Действия по запуску зависят от платформы.

#### Запуск в Linux и Windows

В Linux и Windows, когда приложение запускается на основе ассоциации файла, открываемые файлы
передаются как аргументы главному классу, переопределяя аргумент по умолчанию для класса. В
*File Associations Demo* аргументы передаются методу `loadscript` после запуска экземпляра
приложения. Для каждого открываемого файла запускается отдельный экземпляр приложения.

#### Запуск в OS X

В OS X выполняется только один экземпляр приложения. Когда открывается связанный файл, приложению
отправляется событие. Приложение должно иметь зарегистрированный слушатель события (*event
listener*) для его обработки.

В демонстрации *File Association Demo* для OS X есть подкласс с другим методом `main`, чем в
версии для Linux и Windows. Этот метод `main` обрабатывает аргумент по умолчанию так же, как и
метод `main` версии для Linux и Windows, а затем регистрирует в OS X слушатель для
`FileOpenHandler`. Метод-обработчик события этого слушателя вызывается при открытии связанного
файла, а имя файла извлекается из метода `getFiles` объекта `OpenFilesEvent`.

Сборка версии *File Association Demo* для OS X требует доступа к специфичным для OS X классам,
которые поставляются с Oracle JDK. Большинство классов `com.apple.eawt` не включены в файл
символов (*symbols file*), который использует компилятор `javac`. Чтобы указать компилятору
игнорировать файл символов, аргумент `-XDignore.symbol.file=true` передаётся компилятору `javac`
в задаче Ant `-pre-init` файла сборки.

### Подробнее о File Association Demo

Проект *File Association Demo* содержит исходные Java-файлы приложения в каталоге `/src/sample/fa`.
Пользовательские значки находятся в каталоге `/src/package/platform`. Образцы файлов, упаковываемых
вместе с приложением, находятся в каталоге `/src`.

Для обработки кода Groovy *File Association Demo* требуется библиотека Groovy. Процесс сборки
загружает библиотеку Groovy в каталог `/lib` (см. раздел «Добавление внешней библиотеки»).

После генерации JAR-файла процесс сборки копирует каталоги `/src` и `/lib` в каталог `/dist`.
После этого каталог `/dist` содержит все файлы вашего приложения.

*File Association Demo* принимает имя файла в качестве аргумента. Если приложение запущено путём
открытия связанного файла, передаётся имя этого файла. Если приложение запущено напрямую,
передаётся имя образца `sample.js`, поставляемого с приложением (см. раздел «Передача аргумента
по умолчанию»).

Для настройки ассоциаций файлов требуются права администратора. По умолчанию установщик EXE для
Windows не запрашивает права администратора. Чтобы принудительно запросить права администратора
для *File Association Demo*, аргументу пакета `win.exe.systemWide` задано значение `true`. Эта
настройка означает, что выполняется установка в масштабах всей системы (*system-wide*), для чего
требуются права администратора.

*File Association Demo* работает в Linux, OS X и Windows. Демонстрация настроена на использование
единого файла сборки, содержащего информацию для всех платформ (см. раздел «Использование общего
файла сборки для всех платформ»).

## Добавление внешней библиотеки

Самодостаточные приложения включают всё, что нужно приложению для работы. Если вашему приложению
требуется внешняя библиотека, её можно добавить в пакет приложения. Сделать это можно разными
способами.

Демонстрация *File Association Demo*, описанная в разделе «Использование ассоциаций файлов»,
загружает библиотеку Groovy в процессе сборки. Библиотека помещается в каталог `/lib` проекта
приложения. Затем этот каталог копируется в каталог `/dist`, из которого генерируется пакет
самодостаточного приложения.

Следующий код в задаче `-pre-init` файла `build.xml` показывает, как загружается библиотека:

```xml
<!-- загрузка и копирование библиотеки groovy -->
<copy toFile="lib/groovy-all-2.3.8.jar">
    <resources>
      <url url="http://central.maven.org/maven2/org/codehaus/groovy/groovy-all/2.3.8/groovy-all-2.3.8.jar"/>
    </resources>
</copy>
```

## Передача аргумента по умолчанию

Аргументы передаются Java-приложениям при их запуске. Самодостаточные приложения можно настроить
с **аргументом по умолчанию** (*default argument*), который используется, когда аргумент не
указан. Для определения аргумента служит элемент `<fx:argument>`. Можно передать несколько
аргументов, добавив элемент `<fx:argument>` для каждого из них.

Демонстрация *File Association Demo*, описанная в разделе «Использование ассоциаций файлов»,
настроена на использование имени одного из образцовых файлов, поставляемых с приложением, в
качестве аргумента по умолчанию.

Следующий код в задаче `<fx:deploy>` файла `build.xml` показывает, как определяется аргумент по
умолчанию:

```xml
<fx:application id="fileassociationdemo"
                name="File Association Demo"
                mainClass="${main.class}"
                version="1.0">
    <fx:argument>sample.js</fx:argument>
</fx:application>
```

## Использование общего файла сборки для всех платформ

Чтобы сгенерировать пакет самодостаточного приложения для каждой платформы, на которой работает
ваше приложение, инструмент упаковки нужно запустить на каждой платформе. У вас есть выбор:
использовать специфичные для платформы файлы сборки либо настроить один файл сборки, который можно
запускать на всех платформах. Специфичные для платформы файлы могут быть проще в настройке, но
тогда придётся поддерживать несколько файлов.

Демонстрация *File Association Demo* использует единый файл сборки, работающий на всех платформах.

Следующие элементы файла сборки обеспечивают его использование на всех платформах:

- Главный класс приложения — `ScriptRunnerApplication.java` для Linux и Windows и
  `ScriptRunnerApplicationMac.java` для OS X. Следующий код в задаче `-pre-init` определяет, какой
  класс использовать:

  ```xml
  <condition property="main.class" 
             value="sample.fa.ScriptRunnerApplication"
             else="sample.fa.ScriptRunnerApplicationMac">
      <not><os family="mac"/></not>
  </condition>
  ```

- Следующий код в задаче `-pre-init` предотвращает компиляцию главного класса для OS X при запуске
  в Linux или Windows:

  ```xml
  <condition property="excludes" value="**/*Mac.java">
      <not><os family="mac"/></not>
  </condition>
  ```

- Элементы `<fx:bundleArgument>` используются для передачи аргументов различным доступным
  упаковщикам. Аргументы, не используемые упаковщиком, игнорируются, поэтому файл сборки может
  содержать аргументы, нужные всем платформам. Следующий код определяет аргументы для Linux, OS X
  и Windows:

  ```xml
  <fx:bundleArgument arg="classpath" value="FileAssociationsDemo.jar lib/groovy-all-2.3.8.jar"/>

  <fx:bundleArgument arg="win.exe.systemWide" value="true"/>

  <fx:bundleArgument arg="linux.bundleName" value="file-association-demo"/>
  <fx:bundleArgument arg="email" value="maintainer@example.com"/>
  <fx:bundleArgument arg="mac.CFBundleName" value="File Assoc Demo"/>
  <fx:bundleArgument arg="win.menuGroup" value="Java Demos"/>
  ```

## Использование нескольких точек входа

Самодостаточные приложения полезны, когда у вас есть набор связанных приложений, которые вы хотите
дать пользователям для развёртывания. Самодостаточное приложение предоставляет единый
устанавливаемый пакет, который устанавливает все приложения и JRE, нужную для их запуска.

Демонстрация *Multiple Launchers Demo* включает *Dynamic Tree Demo* (описана в разделе
«Преобразование существующего приложения») и *File Association Demo* (описана в разделе
«Использование ассоциаций файлов»). Каталог `/src` проекта содержит исходные файлы обоих
приложений.

**Основная** точка входа самодостаточного приложения определяется атрибутом `mainClass` элемента
`<fx:application>`. В *Multiple Launchers Demo* основная точка входа — это *File Association Demo*.
Главный класс — `sample.fa.ScriptRunnerApplication` для Linux и Windows или
`sample.fa.ScriptRunnerApplicationMac` для OS X (о том, как определяется используемый класс при
едином файле сборки, см. раздел «Использование общего файла сборки для всех платформ»).

Каждая **вторичная** точка входа определяется экземпляром элемента `<fx:secondaryLauncher>`.

В *Multiple Launchers Demo* вторичная точка входа — это *Dynamic Tree Demo*. Следующий код в файле
`build.xml` показывает, как определяется вторая точка входа:

```xml
<fx:secondaryLauncher name="Dynamic Tree Demo"
    mainClass="webstartComponentArch.DynamicTreeApplication"
    version="1.0"
    title="Dynamic Tree Demo"
    vendor="My Company"
    description="A Demo of Multiple Launchers for JavaPackager"
    copyright="(c) 2014 My Company"
     menu="true"
     shortcut="false"
     >
</fx:secondaryLauncher>
```

Когда ваше самодостаточное приложение установлено, *File Association Demo* устанавливается с точкой
входа Multiple Launchers, а *Dynamic Tree Demo* — со своей собственной точкой входа. Например, в
Windows папка `Java Demos` в меню «Пуск» содержит две записи: Dynamic Tree Demo и Multiple
Launchers Demo. Обратите внимание, что ассоциации файлов настроены для точки входа Multiple
Launchers, поэтому открытие файла JavaScript или Groovy запускает Multiple Launchers.

## Вопросы и упражнения

### Вопросы

1. **Что из перечисленного НЕ является преимуществом самодостаточных приложений?**
   - Пользователи устанавливают приложение знакомым им установщиком.
   - Приложение работает как нативное.
   - Приложение требует меньше места на машине пользователя.
   - Вы контролируете версию JRE, используемую приложением.
   - Приложению не требуется браузер для запуска.

   **Ответ:** вариант «Приложение требует меньше места». Приложение требует *больше* места,
   поскольку JRE поставляется в комплекте с приложением.

2. **Верно или неверно: для настройки ассоциации файла всегда необходимо использовать MIME-тип.**

   **Ответ:** **Неверно.** В зависимости от платформы и используемого упаковщика можно
   использовать MIME-тип или расширение файла. Для Linux требуется MIME-тип. Для Windows требуется
   расширение файла. Для OS X требуется либо MIME-тип, либо расширение файла. Хорошая практика —
   указывать и MIME-тип, и расширение файла при настройке ассоциаций, независимо от платформы.

3. **Какие элементы используются для определения точек входа самодостаточных приложений в задаче
   Ant `<fx:deploy>`?**

   **Ответ:** атрибут `mainClass` элемента `<fx:application>` используется для определения основной
   точки входа. Если самодостаточное приложение имеет несколько точек входа, для каждой вторичной
   точки входа используется элемент `<fx:secondaryLauncher>`.

### Упражнения

1. **Напишите задачу Ant `<fx:deploy>` для генерации пакета Windows MSI** для простого приложения
   с именем My Sample App. JAR-файл приложения находится в каталоге `dist`, главный класс —
   `samples.MyApp`, выходные файлы должны записываться в текущий каталог.

   **Ответ:**

   ```xml
   <fx:deploy outdir="."
              outfile="MySampleApp"
              nativeBundles="msi">

       <fx:application name="My Sample Application"
                       mainClass="samples.MyApp"/>

       <fx:resources>
           <fx:fileset dir="dist" includes="*.jar"/>
       </fx:resources>

       <fx:info title="My Sample Application"
                description="A simple sample app"/>
   </fx:deploy>
   ```

2. **Дополните код предыдущего упражнения** так, чтобы создавались пакеты для всех установщиков
   Windows и определялась ассоциация файлов для текстовых файлов.

   **Ответ:**

   ```xml
   <fx:deploy outdir="."
              outfile="MySampleApp"
              nativeBundles="installer">

       <fx:application name="My Sample Application"
                       mainClass="samples.MyApp"/>

       <fx:resources>
           <fx:fileset dir="dist" includes="*.jar"/>
       </fx:resources>

       <fx:info title="My Sample Application"
                description="A simple sample app">
           <fx:association extension="txt" 
                           description="Text files">
            </fx:association>
        </fx:info>
   </fx:deploy>
   ```

   Когда атрибут `nativeBundles` задан как `installer`, упаковщик пытается собрать пакеты для всех
   поддерживаемых установщиков этой платформы. Образ диска не создаётся. Если инструментов,
   необходимых для сборки конкретного пакета, нет, этот тип пакета пропускается. Для определения
   ассоциаций файлов Windows требует только атрибут `extension`.

## Источник

- [Lesson: Deploying Self-Contained Applications](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/index.html) — официальное руководство Oracle (вводная страница урока).
- [Pre-Requisites for Packaging Self-Contained Applications](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/prereqs.html)
- [Converting an Existing Application](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/converting.html)
- [Using File Associations](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/fileassociation.html)
- [Adding an External Library](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/addlibrary.html)
- [Providing a Default Argument](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/defaultarg.html)
- [Using a Common Build File for All Platforms](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/commonbuild.html)
- [Using Multiple Entry Points](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/multiplelaunchers.html)
- [Questions and Exercises: Self-Contained Applications](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/QandE/questions.html)
- [Answers to Questions and Exercises: Self-Contained Applications](https://docs.oracle.com/javase/tutorial/deployment/selfContainedApps/QandE/answers.html)
