# Урок 6. Поставщики служб интернационализации

**Трейл:** Internationalization · **Оригинал:** [Service Providers for Internationalization](https://docs.oracle.com/javase/tutorial/i18n/serviceproviders/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

## Обзор

> Поставщики служб интернационализации (service providers for internationalization)
> позволяют подключать локалезависимые данные и службы. Поскольку локалезависимые
> данные и службы можно подключать извне, сторонние разработчики могут предоставлять
> собственные реализации большинства чувствительных к локали классов из пакетов
> `java.text` и `java.util`.

> **Служба** (service) — это набор программных интерфейсов и классов, дающих доступ к
> конкретной функциональности или возможности приложения. **Интерфейс поставщика службы**
> (service provider interface, SPI) — это набор открытых интерфейсов и абстрактных классов,
> которые определяет служба. **Поставщик службы** (service provider) реализует SPI.
> Поставщики служб позволяют создавать расширяемые приложения, которые можно дополнять
> без изменения исходной кодовой базы. Их функциональность можно наращивать новыми
> подключаемыми модулями (plug-ins). Подробнее о поставщиках служб и расширяемых
> приложениях см. в разделе «Создание расширяемых приложений» (Creating Extensible
> Applications).

> Поставщики служб интернационализации можно использовать, чтобы предоставить
> собственные реализации следующих чувствительных к локали классов:

- объекты `BreakIterator`;
- объекты `Collator`;
- код языка, код страны и имя варианта (variant) для класса `Locale`;
- имена часовых поясов (time zone names);
- символы валют (currency symbols);
- объекты `DateFormat`;
- объекты `DateFormatSymbols`;
- объекты `NumberFormat`;
- объекты `DecimalFormatSymbols`.

> Соответствующие SPI содержатся в пакетах `java.text.spi` и `java.util.spi`:

**java.util.spi**
- `CurrencyNameProvider`
- `LocaleServiceProvider`
- `TimeZoneNameProvider`

**java.text.spi**
- `BreakIteratorProvider`
- `CollatorProvider`
- `DateFormatProvider`
- `DateFormatSymbolsProvider`
- `DecimalFormatSymbolsProvider`
- `NumberFormatProvider`

> Например, если вы хотите предоставить объект `NumberFormat` для новой локали,
> реализуйте класс `java.text.spi.NumberFormatProvider` и определите в нём следующие методы:

- `getCurrencyInstance(Locale locale)`
- `getIntegerInstance(Locale locale)`
- `getNumberInstance(Locale locale)`
- `getPercentInstance(Locale locale)`

```java
Locale loc = new Locale("da", "DK");
NumberFormat nf = NumberFormatProvider.getNumberInstance(loc);
```

> Эти методы сначала проверяют, поддерживает ли запрошенную локаль среда выполнения Java
> (Java runtime environment); если поддерживает — используют эту встроенную поддержку.
> В противном случае методы вызывают методы `getAvailableLocales` у установленных
> поставщиков соответствующего интерфейса, чтобы найти поставщика, который поддерживает
> запрошенную локаль.

> Развёрнутый пример использования поставщиков служб интернационализации приведён в разделе
> «Установка пользовательского пакета ресурсов в качестве расширения» (Installing a Custom
> Resource Bundle as an Extension). Там показано, как реализовать интерфейс
> `ResourceBundleControlProvider`, который позволяет использовать любые собственные классы
> `ResourceBundle.Control` без каких-либо дополнительных изменений в исходном коде приложения.

## Установка пользовательского пакета ресурсов в качестве расширения

> В разделе «Настройка загрузки пакетов ресурсов» (Customizing Resource Bundle Loading)
> показано, как изменить способ загрузки пакетов ресурсов (resource bundles). Для этого
> создаётся новый класс, производный от класса
> [`ResourceBundle.Control`](https://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.Control.html),
> а затем пакет ресурсов извлекается вызовом следующего метода:

```java
ResourceBundle getBundle(
  String baseName,
  Locale targetLocale,
  ResourceBundle.Control control)
```

> Параметр `control` — это ваша реализация `ResourceBundle.Control`.

> Интерфейс
> [`java.util.spi.ResourceBundleControlProvider`](https://docs.oracle.com/javase/8/docs/api/java/util/spi/ResourceBundleControlProvider.html)
> позволяет изменить, как пакеты ресурсов загружает следующий метод:

```java
ResourceBundle getBundle(
  String baseName,
  Locale targetLocale)
```

> Обратите внимание, что этой версии метода
> [`ResourceBundle.getBundle`](https://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.html#getBundle-java.lang.String-java.util.Locale-)
> не требуется экземпляр класса `ResourceBundle.Control`.
> `ResourceBundleControlProvider` — это интерфейс поставщика службы (SPI). SPI позволяют
> создавать расширяемые приложения, которые легко дополнять без изменения исходной кодовой
> базы. Подробнее см. в разделе «Создание расширяемых приложений» (Creating Extensible
> Applications).

> Чтобы использовать SPI, вы сначала создаёте поставщика службы, реализуя SPI вроде
> `ResourceBundleControlProvider`. Реализуя SPI, вы задаёте, как именно он будет
> предоставлять службу. Служба, которую предоставляет SPI `ResourceBundleControlProvider`, —
> это получение подходящего экземпляра `ResourceBundle.Control`, когда ваше приложение
> вызывает метод `ResourceBundle.getBundle(String baseName, Locale targetLocale)`. Поставщик
> службы упаковывается с помощью механизма расширений Java (Java Extension Mechanism) как
> установленное расширение (installed extension). При запуске приложения вы не указываете
> свои расширения в пути к классам (class path); среда выполнения находит и загружает эти
> расширения сама.

> Установленная реализация SPI `ResourceBundleControlProvider` замещает класс
> `ResourceBundle.Control` по умолчанию (который определяет стандартный процесс загрузки
> пакетов). Следовательно, интерфейс `ResourceBundleControlProvider` позволяет использовать
> любые собственные классы `ResourceBundle.Control` без каких-либо дополнительных изменений
> в исходном коде приложения. Кроме того, этот интерфейс позволяет писать приложения, не
> ссылаясь ни на один из ваших пользовательских классов `ResourceBundle.Control`.

> Пример `RBCPTest.java` показывает, как реализовать интерфейс
> `ResourceBundleControlProvider` и как упаковать его в виде установленного расширения. Этот
> пример упакован в zip-файл `RBCPTest.zip` и состоит из следующих файлов:

- `src`
  - `java.util.spi.ResourceBundleControlProvider`
  - `RBCPTest.java`
  - `rbcp`
    - `PropertiesResourceBundleControl.java`
    - `PropertiesResourceBundleControlProvider.java`
    - `XMLResourceBundleControl.java`
    - `XMLResourceBundleControlProvider.java`
  - `resources`
    - `RBControl.properties`
    - `RBControl_zh.properties`
    - `RBControl_zh_CN.properties`
    - `RBControl_zh_HK.properties`
    - `RBControl_zh_TW.properties`
    - `XmlRB.xml`
    - `XmlRB_ja.xml`
- `lib`
  - `rbcontrolprovider.jar`
- `build`: содержит все файлы, упакованные в `rbcontrolprovider.jar`, а также class-файл `RBCPTest.class`
- `build.xml`

> Следующие шаги показывают, как заново воссоздать содержимое файла `RBCPTest.zip`, как
> работает пример `RBCPTest` и как его запустить:

1. Создать реализации класса `ResourceBundle.Control`.
2. Реализовать интерфейс `ResourceBundleControlProvider`.
3. В своём приложении вызвать метод `ResourceBundle.getBundle`.
4. Зарегистрировать поставщика службы, создав файл конфигурации.
5. Упаковать поставщика, его необходимые классы и файл конфигурации в JAR-файл.
6. Запустить программу `RBCPTest`.

### Шаг 1. Создание реализаций класса `ResourceBundle.Control`

> Пример `RBCPTest.java` использует две реализации `ResourceBundle.Control`:

- **`PropertiesResourceBundleControl.java`**: это та же реализация `ResourceBundle.Control`,
  что определена в разделе «Настройка загрузки пакетов ресурсов» (Customizing Resource
  Bundle Loading).
- **`XMLResourceBundleControl.java`**: эта реализация `ResourceBundle.Control` загружает
  пакеты на основе XML с помощью метода
  [`Properties.loadFromXML`](https://docs.oracle.com/javase/8/docs/api/java/util/Properties.html#loadFromXML-java.io.InputStream-).

Реализация `PropertiesResourceBundleControl`:

```java
/*
 * Copyright (c) 2013, Oracle and/or its affiliates. All rights reserved.
 * [текст лицензии BSD сохранён в оригинале]
 */

package rbcp;

import java.io.*;
import java.net.*;
import java.util.*;
import static java.util.ResourceBundle.Control.*;

public class PropertiesResourceBundleControl extends ResourceBundle.Control {

    @Override
    public List<Locale> getCandidateLocales(String baseName, Locale locale) {
         if (baseName == null)
       throw new NullPointerException();
         if (locale.equals(new Locale("zh", "HK"))) {
       return Arrays.asList(
           locale,
           Locale.TAIWAN,
           // здесь нет Locale.CHINESE
           Locale.ROOT);
         } else if (locale.equals(Locale.TAIWAN)) {
       return Arrays.asList(
           locale,
           // здесь нет Locale.CHINESE
           Locale.ROOT);
         }
         return super.getCandidateLocales(baseName, locale);
     }

}
```

Реализация `XMLResourceBundleControl`:

```java
/*
 * Copyright (c) 2013, Oracle and/or its affiliates. All rights reserved.
 * [текст лицензии BSD сохранён в оригинале]
 */

package rbcp;

import java.io.*;
import java.net.*;
import java.util.*;
import static java.util.ResourceBundle.Control.*;

public class XMLResourceBundleControl extends ResourceBundle.Control {
    @Override
    public List<String> getFormats(String baseName) {
        if (baseName == null) {
            throw new NullPointerException();
        }
        return Arrays.asList("xml");
    }

    @Override
    public ResourceBundle newBundle(String baseName, Locale locale,
                                    String format,
                                    ClassLoader loader,
                                    boolean reload)
        throws IllegalAccessException,
               InstantiationException, IOException {
        if (baseName == null || locale == null
            || format == null || loader == null) {
            throw new NullPointerException();
        }
        ResourceBundle bundle = null;
        if (format.equals("xml")) {
            String bundleName = toBundleName(baseName, locale);
            String resourceName = toResourceName(bundleName, format);
            URL url = loader.getResource(resourceName);
            if (url != null) {
                URLConnection connection = url.openConnection();
                if (connection != null) {
                    if (reload) {
                        // при перезагрузке отключаем кэширование
                        connection.setUseCaches(false);
                    }
                    try (InputStream stream = connection.getInputStream()) {
                        if (stream != null) {
                            BufferedInputStream bis =
                                new BufferedInputStream(stream);
                            bundle = new XMLResourceBundle(bis);
                        }
                    }
                }
            }
        }
        return bundle;
    }

    private static class XMLResourceBundle extends ResourceBundle {
        private Properties props;

        XMLResourceBundle(InputStream stream) throws IOException {
            props = new Properties();
            props.loadFromXML(stream);
        }

        protected Object handleGetObject(String key) {
            if (key == null) {
                throw new NullPointerException();
            }
            return props.get(key);
        }

        public Enumeration<String> getKeys() {
            // Не реализовано
            return null;
        }
    }
}
```

#### XML-файлы свойств

> Как описано в разделе «Использование файлов свойств для пакета ресурсов» (Backing a
> ResourceBundle with Properties Files), файлы свойств (properties files) — это простые
> текстовые файлы. Они содержат одну пару «ключ-значение» в каждой строке. XML-файлы свойств
> устроены так же, как файлы свойств: они содержат пары «ключ-значение», но имеют XML-структуру.
> Ниже приведён XML-файл свойств `XmlRB.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>

<!DOCTYPE properties [
<!ELEMENT properties ( comment?, entry* ) >
<!ATTLIST properties version CDATA #FIXED "1.0">
<!ELEMENT comment (#PCDATA) >
<!ELEMENT entry (#PCDATA) >
<!ATTLIST entry key CDATA #REQUIRED>
]>

<properties>
    <comment>Тестовые данные для RBCPTest.java</comment>
    <entry key="type">XML</entry>
</properties>
```

> Эквивалентный текстовый файл свойств:

```properties
# Тестовые данные для RBCPTest.java
type = XML
```

> Все XML-файлы свойств имеют одинаковую структуру:

- **Объявление DOCTYPE**, задающее определение типа документа (Document Type Definition, DTD):
  DTD определяет структуру XML-файла.

  > **Примечание**: вместо этого в XML-файле свойств можно использовать следующее объявление
  > DOCTYPE:

  ```xml
  <!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
  ```

  > Системный URI (`http://java.sun.com/dtd/properties.dtd`) не запрашивается при экспорте или
  > импорте свойств; это просто строка, однозначно идентифицирующая DTD XML-файлов свойств.

- **Корневой элемент `<properties>`**: содержит все остальные элементы.
- **Любое число элементов `<comment>`**: используются для комментариев.
- **Любое число элементов `<entry>`**: с помощью атрибута `key` задаётся ключ; значение ключа
  указывается между тегами `<entry>`.

> Подробнее об XML-файлах свойств см. в описании класса
> [`Properties`](https://docs.oracle.com/javase/8/docs/api/java/util/Properties.html).

### Шаг 2. Реализация интерфейса `ResourceBundleControlProvider`

> Этот интерфейс содержит один метод —
> [`ResourceBundle.Control getControl(String baseName)`](https://docs.oracle.com/javase/8/docs/api/java/util/spi/ResourceBundleControlProvider.html#getControl-java.lang.String-).
> Параметр `baseName` — это имя пакета ресурсов. В определении метода `getControl` укажите,
> какой экземпляр `ResourceBundle.Control` должен возвращаться для данного имени пакета
> ресурсов.

> Пример `RBCPTest` содержит две реализации интерфейса `ResourceBundleControlProvider`:
> `PropertiesResourceBundleControlProvider.java` и `XMLResourceBundleControlProvider.java`.
> Метод `PropertiesResourceBundleControlProvider.getControl` возвращает экземпляр
> `PropertiesResourceBundleControl`, если базовое имя пакета ресурсов начинается с
> `resources.RBControl` (в этом примере все файлы ресурсов содержатся в пакете `resources`):

```java
package rbcp;

import java.util.ResourceBundle;
import java.util.spi.ResourceBundleControlProvider;

public class PropertiesResourceBundleControlProvider
    implements ResourceBundleControlProvider {
    static final ResourceBundle.Control PROPERTIESCONTROL =
        new PropertiesResourceBundleControl();

    public ResourceBundle.Control getControl(String baseName) {
        System.out.println("Class: " + getClass().getName() + ".getControl");
        System.out.println("    called for " + baseName);

        // Бросает NPE, если baseName равен null.
        if (baseName.startsWith("resources.RBControl")) {
            System.out.println("    returns " + PROPERTIESCONTROL);
            return PROPERTIESCONTROL;
        }
        System.out.println("    returns null");
        System.out.println();
        return null;
    }
}
```

> Аналогично, метод `XMLResourceBundleControlProvider.getControl` возвращает экземпляр
> `XMLResourceBundleControl`, если базовое имя пакета ресурсов начинается с `resources.Xml`.

> **Примечание**: можно создать одну реализацию интерфейса `ResourceBundleControlProvider`,
> которая в зависимости от базового имени возвращает либо экземпляр
> `PropertiesResourceBundleControl`, либо `XMLResourceBundleControl`.

### Шаг 3. Вызов метода `ResourceBundle.getBundle` в приложении

> Класс `RBCPTest` извлекает пакеты ресурсов с помощью метода
> [`ResourceBundle.getBundle`](https://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.html#getBundle-java.lang.String-java.util.Locale-):

```java
import java.io.*;
import java.net.*;
import java.util.*;

public class RBCPTest {
    public static void main(String[] args) {
        ResourceBundle rb = ResourceBundle.getBundle(
            "resources.XmlRB", Locale.ROOT);
        String type = rb.getString("type");
        System.out.println("Root locale. Key, type: " + type);
        System.out.println();

        rb = ResourceBundle.getBundle("resources.XmlRB", Locale.JAPAN);
        type = rb.getString("type");
        System.out.println("Japan locale. Key, type: " + type);
        System.out.println();

        test(Locale.CHINA);
        test(new Locale("zh", "HK"));
        test(Locale.TAIWAN);
        test(Locale.CANADA);
    }

    private static void test(Locale locale) {
        ResourceBundle rb = ResourceBundle.getBundle(
            "resources.RBControl", locale);
        System.out.println("locale: " + locale);
        System.out.println("    region: " + rb.getString("region"));
        System.out.println("    language: " + rb.getString("language"));
        System.out.println();
    }
}
```

> Обратите внимание, что в этом классе не упоминаются никакие реализации
> `ResourceBundle.Control` или `ResourceBundleControlProvider`. Поскольку интерфейс
> `ResourceBundleControlProvider` использует механизм расширений Java, среда выполнения
> находит и загружает эти реализации сама. Однако реализации `ResourceBundleControlProvider`
> и другие поставщики служб, установленные через механизм расширений Java, загружаются с
> помощью класса
> [`ServiceLoader`](https://docs.oracle.com/javase/8/docs/api/java/util/ServiceLoader.html).
> Использование этого класса означает, что поставщика службы необходимо зарегистрировать
> файлом конфигурации, что описано на следующем шаге.

### Шаг 4. Регистрация поставщика службы через файл конфигурации

> Имя файла конфигурации — это полное (fully qualified) имя интерфейса или класса, который
> реализует поставщик. Файл конфигурации содержит полное имя класса вашего поставщика.
> Файл `java.util.spi.ResourceBundleControlProvider` содержит полные имена
> `PropertiesResourceBundleControlProvider` и `XMLResourceBundleControlProvider`, по одному
> имени на строку:

```
rbcp.XMLResourceBundleControlProvider
rbcp.PropertiesResourceBundleControlProvider
```

### Шаг 5. Упаковка поставщика, необходимых классов и файла конфигурации в JAR-файл

> Скомпилируйте исходные файлы. Из каталога, содержащего файл `build.xml`, выполните следующую
> команду:

```
javac -d build src/java.* src/rbcp/*.java
```

> Эта команда скомпилирует исходные файлы из каталога `src` и поместит class-файлы в каталог
> `build`. В Windows для разделения имён каталогов и файлов используйте обратную косую черту
> (`\`).

> Создайте JAR-файл, содержащий скомпилированные class-файлы, файлы ресурсов и файл
> конфигурации в следующей структуре каталогов:

- `META-INF`
  - `services`
    - `java.util.spi.ResourceBundleControlProvider`
- `rbcp`
  - `PropertiesResourceBundleControl.class`
  - `PropertiesResourceBundleControlProvider.class`
  - `XMLResourceBundleControl.class`
  - `XMLResourceBundleControlProvider.class`
- `resources`
  - `RBControl.properties`
  - `RBControl_zh.properties`
  - `RBControl_zh_CN.properties`
  - `RBControl_zh_HK.properties`
  - `RBControl_zh_TW.properties`
  - `XmlRB.xml`
  - `XmlRB_ja.xml`

> Обратите внимание, что файл конфигурации `java.util.spi.ResourceBundleControlProvider`
> должен быть упакован в каталог `/META-INF/services`. В этом примере перечисленные файлы
> упакованы в JAR-файл `rbcontrolprovider.jar` в каталоге `lib`.

> Подробнее о создании JAR-файлов см. в разделе «Упаковка программ в JAR-файлы» (Packaging
> Programs in JAR Files).

> В качестве альтернативы загрузите и установите
> [Apache Ant](http://ant.apache.org/) — инструмент, позволяющий автоматизировать процессы
> сборки, такие как компиляция Java-файлов и создание JAR-файлов. Убедитесь, что исполняемый
> файл Apache Ant находится в переменной окружения `PATH`, чтобы запускать его из любого
> каталога. После установки Apache Ant выполните следующие шаги:

1. Отредактируйте файл `build.xml` и замените `${JAVAC}` на полный путь к вашему компилятору
   Java `javac`, а `${JAVA}` — на полный путь к исполняемому файлу среды выполнения Java
   `java`.
2. Выполните следующую команду из того же каталога, что содержит файл `build.xml`:

   ```
   ant jar
   ```

   > Эта команда компилирует исходные Java-файлы и упаковывает их вместе с необходимыми
   > файлами ресурсов и конфигурации в JAR-файл `rbcontrolprovider.jar` в каталоге `lib`.

### Шаг 6. Запуск программы `RBCPTest`

> В командной строке выполните следующую команду из каталога, содержащего файл `build.xml`:

```
java -Djava.ext.dirs=lib -cp build RBCPTest
```

> Эта команда предполагает следующее:

- JAR-файл со скомпилированным кодом примера `RBCPTest` находится в каталоге `lib`.
- Скомпилированный класс `RBCPTest.class` находится в каталоге `build`.

> В качестве альтернативы используйте Apache Ant и выполните следующую команду из каталога,
> содержащего файл `build.xml`:

```
ant run
```

> Когда вы устанавливаете расширение Java, JAR-файл расширения обычно помещают в каталог
> `lib/ext` вашей JRE. Однако эта команда задаёт каталог с расширениями Java через системное
> свойство `java.ext.dirs`.

> Программа `RBCPTest` сначала пытается получить пакеты ресурсов с базовым именем
> `resources.XmlRB` и локалями `Locale.ROOT` и `Locale.JAPAN`. Вывод программы при получении
> этих пакетов ресурсов выглядит примерно так:

```
Class: rbcp.XMLResourceBundleControlProvider.getControl
    called for resources.XmlRB
    returns rbcp.XMLResourceBundleControl@16c1857
Root locale. Key, type: XML

Class: rbcp.XMLResourceBundleControlProvider.getControl
    called for resources.XmlRB
    returns rbcp.XMLResourceBundleControl@16c1857
Japan locale. Key, type: Value from Japan locale
```

> Программа успешно получает экземпляр `XMLResourceBundleControl` и обращается к файлам
> свойств `XmlRB.xml` и `XmlRB_ja.xml`.

> Когда программа `RBCPTest` пытается получить пакет ресурсов, она вызывает все классы,
> определённые в файле конфигурации `java.util.spi.ResourceBundleControlProvider`. Например,
> когда программа получает пакет ресурсов с базовым именем `resources.RBControl` и локалью
> `Locale.CHINA`, она печатает следующий вывод:

```
Class: rbcp.XMLResourceBundleControlProvider.getControl
    called for resources.RBControl
    returns null

Class: rbcp.PropertiesResourceBundleControlProvider.getControl
    called for resources.RBControl
    returns rbcp.PropertiesResourceBundleControl@1ad2911
locale: zh_CN
    region: China
    language: Simplified Chinese
```

## Источник

- [Service Providers for Internationalization](https://docs.oracle.com/javase/tutorial/i18n/serviceproviders/index.html) — официальное руководство Oracle (индекс урока).
- [Installing a Custom Resource Bundle as an Extension](https://docs.oracle.com/javase/tutorial/i18n/serviceproviders/resourcebundlecontrolprovider.html) — официальное руководство Oracle (развёрнутый пример).
- [PropertiesResourceBundleControl.java](https://docs.oracle.com/javase/tutorial/i18n/serviceproviders/examples/rbcpsample/src/rbcp/PropertiesResourceBundleControl.java) — исходный код примера Oracle.
- [XMLResourceBundleControl.java](https://docs.oracle.com/javase/tutorial/i18n/serviceproviders/examples/rbcpsample/src/rbcp/XMLResourceBundleControl.java) — исходный код примера Oracle.
