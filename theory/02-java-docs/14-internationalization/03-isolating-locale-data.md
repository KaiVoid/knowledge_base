# Урок 3. Изоляция локалезависимых данных

**Трейл:** Internationalization · **Оригинал:** [Isolating Locale-Specific Data](https://docs.oracle.com/javase/tutorial/i18n/resbundle/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

Локалезависимые данные (locale-specific data) должны быть адаптированы под соглашения языка
и региона конечного пользователя. Самый очевидный пример таких данных — текст, отображаемый
пользовательским интерфейсом. Например, у приложения, имеющего в США кнопку Cancel,
в Германии будет кнопка Abbrechen. В других странах эта кнопка получит иные надписи.
Очевидно, что надпись на кнопке не следует жёстко зашивать в код (hardcode). Разве не было бы
удобно автоматически получать правильную надпись для заданной локали (`Locale`)? К счастью,
это возможно — при условии, что вы изолируете локалезависимые объекты в пакете ресурсов
(`ResourceBundle`).

В этом уроке вы узнаете, как создавать объекты `ResourceBundle` и обращаться к ним. Если вам
не терпится посмотреть примеры кода, переходите сразу к последним двум разделам урока. После
этого можно вернуться к первым двум разделам за концептуальной информацией об объектах
`ResourceBundle`.

## Разделы урока

- **[О классе ResourceBundle](#о-классе-resourcebundle)** — объекты `ResourceBundle` содержат
  локалезависимые объекты. Когда вам нужен локалезависимый объект, вы получаете его из
  `ResourceBundle`, который возвращает объект, соответствующий локали конечного пользователя.
  Этот раздел объясняет, как `ResourceBundle` связан с `Locale`, и описывает подклассы
  `ResourceBundle`.
- **[Подготовка к использованию ResourceBundle](#подготовка-к-использованию-resourcebundle)** —
  прежде чем создавать объекты `ResourceBundle`, стоит немного спланировать. Сначала найдите
  в программе локалезависимые объекты. Затем разбейте их на категории и разложите по разным
  объектам `ResourceBundle`.
- **[Хранение ResourceBundle в файлах свойств](#хранение-resourcebundle-в-файлах-свойств-properties-files)** —
  если приложение содержит объекты `String`, которые нужно переводить на разные языки, эти
  строки можно хранить в `PropertyResourceBundle`, который опирается на набор файлов свойств
  (properties files). Поскольку файлы свойств — это простые текстовые файлы, их могут создавать
  и сопровождать ваши переводчики. Менять исходный код не требуется.
- **[Использование ListResourceBundle](#использование-listresourcebundle)** — класс
  `ListResourceBundle`, подкласс `ResourceBundle`, управляет локалезависимыми объектами с
  помощью списка. `ListResourceBundle` опирается на файл класса (class file), а значит, для
  поддержки каждой дополнительной локали приходится писать и компилировать новый исходный файл.
  Тем не менее объекты `ListResourceBundle` полезны, потому что, в отличие от файлов свойств,
  могут хранить локалезависимые объекты любого типа.
- **[Настройка загрузки пакетов ресурсов](#настройка-загрузки-пакетов-ресурсов)** — этот раздел
  описывает новые возможности, повышающие гибкость фабрики `ResourceBundle.getBundle`. Класс
  `ResourceBundle.Control` взаимодействует с фабричными методами при загрузке пакетов ресурсов.
  Это позволяет рассматривать каждый существенный шаг процесса загрузки пакета ресурсов и
  управление его кэшем как отдельный метод.

## О классе ResourceBundle

### Как ResourceBundle связан с Locale

Концептуально каждый `ResourceBundle` — это набор связанных подклассов с общим базовым именем
(base name). В списке ниже показан набор связанных подклассов. `ButtonLabel` — базовое имя.
Символы, следующие за базовым именем, обозначают код языка, код страны и вариант локали
(`Locale`). Например, `ButtonLabel_en_GB` соответствует локали, заданной кодом языка для
английского (`en`) и кодом страны для Великобритании (`GB`).

```
ButtonLabel
ButtonLabel_de
ButtonLabel_en_GB
ButtonLabel_fr_CA_UNIX
```

Чтобы выбрать подходящий `ResourceBundle`, вызовите метод `ResourceBundle.getBundle`. В
следующем примере выбирается `ResourceBundle` `ButtonLabel` для локали, соответствующей
французскому языку, стране Канада и платформе UNIX.

```java
Locale currentLocale = new Locale("fr", "CA", "UNIX");
ResourceBundle introLabels = ResourceBundle.getBundle(
                                 "ButtonLabel", currentLocale);
```

Если класса `ResourceBundle` для указанной локали не существует, `getBundle` пытается найти
ближайшее соответствие. Например, если нужен класс `ButtonLabel_fr_CA_UNIX`, а локаль по
умолчанию — `en_US`, то `getBundle` будет искать классы в следующем порядке:

```
ButtonLabel_fr_CA_UNIX
ButtonLabel_fr_CA
ButtonLabel_fr
ButtonLabel_en_US
ButtonLabel_en
ButtonLabel
```

Обратите внимание, что `getBundle` ищет классы на основе локали по умолчанию, прежде чем выбрать
базовый класс (`ButtonLabel`). Если `getBundle` не находит соответствия в приведённом списке
классов, он выбрасывает исключение `MissingResourceException`. Чтобы избежать этого исключения,
всегда предоставляйте базовый класс без суффиксов.

### Подклассы ListResourceBundle и PropertyResourceBundle

У абстрактного класса `ResourceBundle` есть два подкласса: `PropertyResourceBundle` и
`ListResourceBundle`.

`PropertyResourceBundle` опирается на файл свойств (properties file). Файл свойств — это
обычный текстовый файл, содержащий переводимый текст. Файлы свойств не являются частью исходного
кода Java и могут содержать значения только для объектов `String`. Если нужно хранить объекты
других типов, используйте вместо него `ListResourceBundle`. Раздел
[Хранение ResourceBundle в файлах свойств](#хранение-resourcebundle-в-файлах-свойств-properties-files)
показывает, как пользоваться `PropertyResourceBundle`.

Класс `ListResourceBundle` управляет ресурсами с помощью удобного списка. Каждый
`ListResourceBundle` опирается на файл класса (class file). В `ListResourceBundle` можно хранить
локалезависимый объект любого типа. Чтобы добавить поддержку дополнительной локали, вы создаёте
ещё один исходный файл и компилируете его в файл класса. В разделе
[Использование ListResourceBundle](#использование-listresourcebundle) есть пример кода, который
может оказаться полезным.

Класс `ResourceBundle` гибок. Если вы сначала поместили локалезависимые объекты `String` в
`PropertyResourceBundle`, а затем решили использовать вместо него `ListResourceBundle`, это
никак не повлияет на ваш код. Например, следующий вызов `getBundle` извлечёт `ResourceBundle`
для подходящей локали независимо от того, чем обеспечивается `ButtonLabel` — классом или файлом
свойств:

```java
ResourceBundle introLabels = ResourceBundle.getBundle(
                                 "ButtonLabel", currentLocale);
```

### Пары «ключ — значение»

Объекты `ResourceBundle` содержат массив пар «ключ — значение» (key-value pairs). Вы указываете
ключ, который обязательно должен быть `String`, когда хотите извлечь значение из
`ResourceBundle`. Значение — это локалезависимый объект. Ключами в следующем примере являются
строки `OkKey` и `CancelKey`:

```java
class ButtonLabel_en extends ListResourceBundle {
    // Английская версия
    public Object[][] getContents() {
        return contents;
    }
    static final Object[][] contents = {
        {"OkKey", "OK"},
        {"CancelKey", "Cancel"},
    };
}
```

Чтобы извлечь строку `OK` из `ResourceBundle`, нужно указать соответствующий ключ при вызове
`getString`:

```java
String okLabel = ButtonLabel.getString("OkKey");
```

Файл свойств содержит пары «ключ — значение». Ключ находится слева от знака равенства, а
значение — справа. Каждая пара — на отдельной строке. Значения могут представлять только объекты
`String`. Следующий пример показывает содержимое файла свойств с именем `ButtonLabel.properties`:

```properties
OkKey = OK
CancelKey = Cancel
```

## Подготовка к использованию ResourceBundle

### Выявление локалезависимых объектов

Если у вашего приложения есть пользовательский интерфейс, оно содержит множество локалезависимых
объектов. Для начала пройдитесь по исходному коду и поищите объекты, которые меняются вместе с
локалью (`Locale`). Ваш список может включать объекты, созданные на основе следующих классов:

- `String`
- `Image`
- `Color`
- `AudioClip`

Заметьте, что в этом списке нет объектов, представляющих числа, даты, время или денежные суммы.
Формат отображения этих объектов меняется с локалью, но сами объекты — нет. Например, вы
форматируете `Date` в соответствии с локалью, но используете один и тот же объект `Date`
независимо от локали. Вместо того чтобы изолировать такие объекты в `ResourceBundle`, вы
форматируете их специальными локалечувствительными (locale-sensitive) классами форматирования.
Как это делается, вы узнаете в разделе
[Даты и время](https://docs.oracle.com/javase/tutorial/i18n/format/dateintro.html) урока
[Форматирование](https://docs.oracle.com/javase/tutorial/i18n/format/index.html).

В общем случае объекты, хранящиеся в `ResourceBundle`, предопределены и поставляются вместе с
продуктом. Эти объекты не изменяются во время работы программы. Например, надпись меню (`Menu`)
следует хранить в `ResourceBundle`, потому что она локалезависима и не изменится в течение сеанса
программы. Однако не стоит изолировать в `ResourceBundle` объект `String`, который конечный
пользователь вводит в текстовое поле (`TextField`). Данные вроде этой строки могут меняться изо
дня в день. Они специфичны для сеанса программы, а не для локали, в которой работает программа.

Обычно большинство объектов, которые нужно изолировать в `ResourceBundle`, — это объекты
`String`. Однако не все объекты `String` локалезависимы. Например, если `String` — это элемент
протокола, используемый для межпроцессного взаимодействия, его не нужно локализовать, потому что
конечные пользователи его никогда не видят.

Решение о том, локализовывать ли некоторые объекты `String`, не всегда очевидно. Хороший пример —
файлы журналов (log files). Если файл журнала пишется одной программой, а читается другой, обе
программы используют его как буфер для обмена данными. Предположим, что конечные пользователи
изредка проверяют содержимое такого файла журнала. Не следует ли его локализовать? С другой
стороны, если пользователи редко заглядывают в файл журнала, затраты на перевод могут не
оправдаться. Решение локализовать этот файл журнала зависит от ряда факторов: архитектуры
программы, удобства использования, стоимости перевода и поддерживаемости.

### Организация объектов ResourceBundle

Объекты `ResourceBundle` можно организовывать по категории содержащихся в них объектов.
Например, можно загрузить все GUI-надписи окна ввода заказов в `ResourceBundle` под названием
`OrderLabelsBundle`. Использование нескольких объектов `ResourceBundle` даёт ряд преимуществ:

- ваш код проще читать и сопровождать;
- вы избежите огромных объектов `ResourceBundle`, загрузка которых в память может занимать
  слишком много времени;
- вы можете снизить расход памяти, загружая каждый `ResourceBundle` только при необходимости.

## Хранение ResourceBundle в файлах свойств (properties files)

В этом разделе пошагово разбирается пример программы под названием `PropertiesDemo`.

### 1. Создайте файл свойств по умолчанию

Файл свойств — это простой текстовый файл. Создать и сопровождать файл свойств можно практически
любым текстовым редактором.

Файл свойств по умолчанию следует создавать всегда. Имя этого файла начинается с базового имени
вашего `ResourceBundle` и заканчивается суффиксом `.properties`. В программе `PropertiesDemo`
базовое имя — `LabelsBundle`. Поэтому файл свойств по умолчанию называется
`LabelsBundle.properties`. Этот файл содержит следующие строки:

```properties
# Это файл LabelsBundle.properties по умолчанию
s1 = computer
s2 = disk
s3 = monitor
s4 = keyboard
```

Обратите внимание, что в приведённом выше файле строки комментариев начинаются со знака решётки
(#). Остальные строки содержат пары «ключ — значение». Ключ находится слева от знака равенства,
а значение — справа. Например, `s2` — это ключ, соответствующий значению `disk`. Ключ
произвольный. Мы могли бы назвать `s2` как-то иначе, например `msg5` или `diskID`. Однако,
будучи однажды определён, ключ не должен меняться, поскольку на него ссылаются в исходном коде.
Значения изменять можно. Более того, когда ваши локализаторы создают новые файлы свойств для
поддержки дополнительных языков, они переводят значения на разные языки.

### 2. Создайте дополнительные файлы свойств по мере необходимости

Чтобы поддержать дополнительную локаль, ваши локализаторы создадут новый файл свойств, содержащий
переведённые значения. Изменения в исходном коде не требуются, потому что ваша программа
ссылается на ключи, а не на значения.

Например, чтобы добавить поддержку немецкого языка, ваши локализаторы переведут значения из
`LabelsBundle.properties` и поместят их в файл с именем `LabelsBundle_de.properties`. Обратите
внимание, что имя этого файла, как и имя файла по умолчанию, начинается с базового имени
`LabelsBundle` и заканчивается суффиксом `.properties`. Однако, поскольку этот файл предназначен
для конкретной локали, за базовым именем следует код языка (`de`). Содержимое
`LabelsBundle_de.properties` таково:

```properties
# Это файл LabelsBundle_de.properties
s1 = Computer
s2 = Platte
s3 = Monitor
s4 = Tastatur
```

Пример программы `PropertiesDemo` поставляется с тремя файлами свойств:

- LabelsBundle.properties
- LabelsBundle_de.properties
- LabelsBundle_fr.properties

### 3. Укажите локаль

Программа `PropertiesDemo` создаёт объекты `Locale` следующим образом:

```java
Locale[] supportedLocales = {
    Locale.FRENCH,
    Locale.GERMAN,
    Locale.ENGLISH
};
```

Эти объекты `Locale` должны соответствовать файлам свойств, созданным на двух предыдущих шагах.
Например, объект `Locale.FRENCH` соответствует файлу `LabelsBundle_fr.properties`. Для
`Locale.ENGLISH` нет соответствующего файла `LabelsBundle_en.properties`, поэтому будет
использован файл по умолчанию.

### 4. Создайте ResourceBundle

Этот шаг показывает, как связаны между собой `Locale`, файлы свойств и `ResourceBundle`. Чтобы
создать `ResourceBundle`, вызовите метод `getBundle`, указав базовое имя и локаль:

```java
ResourceBundle labels = ResourceBundle.getBundle("LabelsBundle", currentLocale);
```

Метод `getBundle` сначала ищет файл класса, соответствующий базовому имени и локали. Если файла
класса найти не удаётся, он проверяет наличие файлов свойств. В программе `PropertiesDemo` мы
обеспечиваем `ResourceBundle` файлами свойств, а не файлами классов. Когда метод `getBundle`
находит нужный файл свойств, он возвращает объект `PropertyResourceBundle`, содержащий пары
«ключ — значение» из этого файла свойств.

### 5. Получите локализованный текст

Чтобы извлечь переведённое значение из `ResourceBundle`, вызовите метод `getString` так:

```java
String value = labels.getString(key);
```

Строка `String`, возвращённая методом `getString`, соответствует указанному ключу. Строка — на
нужном языке при условии, что для указанной локали существует файл свойств.

### 6. Перебор всех ключей

Этот шаг необязателен. При отладке программы вам может понадобиться получить значения для всех
ключей в `ResourceBundle`. Метод `getKeys` возвращает перечисление (`Enumeration`) всех ключей в
`ResourceBundle`. Вы можете пройтись по этому `Enumeration` и получить каждое значение методом
`getString`. Следующие строки кода из программы `PropertiesDemo` показывают, как это делается:

```java
ResourceBundle labels = ResourceBundle.getBundle("LabelsBundle", currentLocale);
Enumeration bundleKeys = labels.getKeys();

while (bundleKeys.hasMoreElements()) {
    String key = (String)bundleKeys.nextElement();
    String value = labels.getString(key);
    System.out.println("key = " + key + ", " + "value = " + value);
}
```

### 7. Запустите демонстрационную программу

Запуск программы `PropertiesDemo` даёт следующий вывод. Первые три строки показывают значения,
возвращённые методом `getString` для различных объектов `Locale`. Последние четыре строки
программа выводит при переборе ключей методом `getKeys`.

```
Locale = fr, key = s2, value = Disque dur
Locale = de, key = s2, value = Platte
Locale = en, key = s2, value = disk

key = s4, value = Clavier
key = s3, value = Moniteur
key = s2, value = Disque dur
key = s1, value = Ordinateur
```

## Использование ListResourceBundle

В этом разделе использование объекта `ListResourceBundle` иллюстрируется на примере программы
под названием `ListDemo`. Текст ниже объясняет каждый шаг создания программы `ListDemo`, а также
подклассы `ListResourceBundle`, которые её поддерживают.

### 1. Создайте подклассы ListResourceBundle

`ListResourceBundle` опирается на файл класса. Поэтому первый шаг — создать файл класса для каждой
поддерживаемой локали. В программе `ListDemo` базовое имя `ListResourceBundle` — `StatsBundle`.
Поскольку `ListDemo` поддерживает три объекта `Locale`, ей требуются три следующих файла класса:

```
StatsBundle_en_CA.class
StatsBundle_fr_FR.class
StatsBundle_ja_JP.class
```

Класс `StatsBundle` для Японии определён в исходном коде ниже. Обратите внимание, что имя класса
формируется добавлением кодов языка и страны к базовому имени `ListResourceBundle`. Внутри класса
двумерный массив `contents` инициализируется парами «ключ — значение». Ключи — это первый элемент
в каждой паре: `GDP`, `Population` и `Literacy`. Ключи должны быть объектами `String` и должны
быть одинаковыми в каждом классе из набора `StatsBundle`. Значения могут быть объектами любого
типа. В этом примере значения — два объекта `Integer` и один объект `Double`.

```java
import java.util.*;
public class StatsBundle_ja_JP extends ListResourceBundle {
    public Object[][] getContents() {
        return contents;
    }

    private Object[][] contents = {
        { "GDP", new Integer(21300) },
        { "Population", new Integer(125449703) },
        { "Literacy", new Double(0.99) },
    };
}
```

### 2. Укажите локаль

Программа `ListDemo` определяет объекты `Locale` следующим образом:

```java
Locale[] supportedLocales = {
    new Locale("en", "CA"),
    new Locale("ja", "JP"),
    new Locale("fr", "FR")
};
```

Каждый объект `Locale` соответствует одному из классов `StatsBundle`. Например, японская локаль,
определённая кодами `ja` и `JP`, соответствует `StatsBundle_ja_JP.class`.

### 3. Создайте ResourceBundle

Чтобы создать `ListResourceBundle`, вызовите метод `getBundle`. Следующая строка кода указывает
базовое имя класса (`StatsBundle`) и локаль:

```java
ResourceBundle stats = ResourceBundle.getBundle("StatsBundle", currentLocale);
```

Метод `getBundle` ищет класс, имя которого начинается с `StatsBundle` и за которым следуют коды
языка и страны указанной локали. Если, например, `currentLocale` создана с кодами `ja` и `JP`,
то `getBundle` возвращает `ListResourceBundle`, соответствующий классу `StatsBundle_ja_JP`.

### 4. Получите локализованные объекты

Теперь, когда у программы есть `ListResourceBundle` для подходящей локали, она может получать
локализованные объекты по их ключам. Следующая строка кода извлекает уровень грамотности, вызывая
`getObject` с параметром-ключом `Literacy`. Поскольку `getObject` возвращает `Object`, приведите
его к `Double`:

```java
Double lit = (Double)stats.getObject("Literacy");
```

### 5. Запустите демонстрационную программу

Программа `ListDemo` печатает данные, полученные методом `getBundle`:

```
Locale = en_CA
GDP = 24400
Population = 28802671
Literacy = 0.97

Locale = ja_JP
GDP = 21300
Population = 125449703
Literacy = 0.99

Locale = fr_FR
GDP = 20200
Population = 58317450
Literacy = 0.99
```

## Настройка загрузки пакетов ресурсов

Ранее в этом уроке вы узнали, как создавать объекты класса `ResourceBundle` и обращаться к ним.
Этот раздел расширяет ваши знания и объясняет, как воспользоваться возможностями класса
[`ResourceBundle.Control`](https://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.Control.html).

Класс `ResourceBundle.Control` был создан для того, чтобы указывать, как находить и создавать
экземпляры пакетов ресурсов. Он определяет набор методов обратного вызова (callback methods),
которые вызываются фабричными методами
[`ResourceBundle.getBundle`](https://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.html#getBundle-java.lang.String-java.util.Locale-java.util.ResourceBundle.Control-)
в процессе загрузки пакета.

В отличие от метода
[`ResourceBundle.getBundle`](https://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.html#getBundle-java.lang.String-java.util.Locale-),
описанного ранее, этот метод `ResourceBundle.getBundle` определяет пакет ресурсов по указанному
базовому имени, локали по умолчанию и указанному объекту control.

```java
public static final ResourceBundle getBundle(
    String baseName,
    ResourceBundle.Control cont
    // ...
```

Указанный объект control предоставляет информацию для процесса загрузки пакета ресурсов.

Следующая пример-программа под названием
[`RBControl.java`](https://docs.oracle.com/javase/tutorial/i18n/resbundle/examples/RBControl.java)
показывает, как определить собственные пути поиска для китайских локалей.

### 1. Создайте файлы свойств (properties)

Как было описано ранее, ресурсы можно загружать либо из классов, либо из файлов свойств. Эти
файлы содержат описания для следующих локалей:

- `RBControl.properties` — глобальная (Global);
- `RBControl_zh.properties` — только язык: упрощённый китайский (Simplified Chinese);
- `RBControl_zh_cn.properties` — только регион: Китай;
- `RBControl_zh_hk.properties` — только регион: Гонконг;
- `RBControl_zh_tw.properties` — Тайвань.

В этом примере приложение создаёт новую локаль для региона Гонконг.

### 2. Создайте экземпляр ResourceBundle

Как и в примере из предыдущего раздела, это приложение создаёт экземпляр `ResourceBundle`,
вызывая метод `getBundle`:

```java
private static void test(Locale locale) {
    ResourceBundle rb = ResourceBundle.getBundle(
                            "RBControl",
                            locale,
                            new ResourceBundle.Control() {
                                    // ...
                            }
                        );
```

Метод `getBundle` ищет файлы свойств с префиксом `RBControl`. Однако этот метод содержит параметр
`Control`, который управляет процессом поиска китайских локалей.

### 3. Вызовите метод getCandidateLocales

Метод `getCandidateLocales` возвращает список объектов `Locale` в качестве локалей-кандидатов
для базового имени и локали.

```java
new ResourceBundle.Control() {
    @Override
    public List<Locale> getCandidateLocales(
                            String baseName,
                            Locale locale) {
                // ...                                        
    }
}
```

Реализация по умолчанию возвращает список объектов `Locale` следующего вида: Locale(language,
country).

Однако этот метод переопределён для реализации следующего конкретного поведения:

```java
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
```

Обратите внимание, что последним элементом последовательности локалей-кандидатов должна быть
корневая локаль (root locale).

### 4. Вызовите класс test

Вызовите класс `test` для следующих четырёх различных локалей:

```java
public static void main(String[] args) {
    test(Locale.CHINA);
    test(new Locale("zh", "HK"));
    test(Locale.TAIWAN);
    test(Locale.CANADA);
}
```

### 5. Запустите пример-программу

Вы увидите вывод программы следующего вида:

```
locale: zh_CN
        region: China
        language: Simplified Chinese
locale: zh_HK
        region: Hong Kong
        language: Traditional Chinese
locale: zh_TW
        region: Taiwan
        language: Traditional Chinese
locale: en_CA
        region: global
        language: English
```

Обратите внимание, что вновь созданной локали был назначен регион Гонконг, потому что он был
указан в соответствующем файле свойств. Для локали Тайваня в качестве языка был назначен
традиционный китайский (Traditional Chinese).

Два других интересных метода класса `ResourceBundle.Control` не были использованы в примере
`RBControl`, но заслуживают упоминания. Метод `getTimeToLive` используется для определения того,
как долго пакет ресурсов может находиться в кэше. Если срок хранения пакета ресурсов в кэше истёк,
вызывается метод `needsReload`, чтобы определить, нужно ли перезагрузить пакет ресурсов.

## Источник

- [Isolating Locale-Specific Data](https://docs.oracle.com/javase/tutorial/i18n/resbundle/index.html) — официальное руководство Oracle (индекс урока).
- [About the ResourceBundle Class](https://docs.oracle.com/javase/tutorial/i18n/resbundle/concept.html) — официальное руководство Oracle.
- [Preparing to Use a ResourceBundle](https://docs.oracle.com/javase/tutorial/i18n/resbundle/prepare.html) — официальное руководство Oracle.
- [Backing a ResourceBundle with Properties Files](https://docs.oracle.com/javase/tutorial/i18n/resbundle/propfile.html) — официальное руководство Oracle.
- [Using a ListResourceBundle](https://docs.oracle.com/javase/tutorial/i18n/resbundle/list.html) — официальное руководство Oracle.
- [Customizing Resource Bundle Loading](https://docs.oracle.com/javase/tutorial/i18n/resbundle/control.html) — официальное руководство Oracle.
