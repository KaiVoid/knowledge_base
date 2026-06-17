# Урок 2. Установка локали

**Трейл:** Internationalization · **Оригинал:** [Setting the Locale](https://docs.oracle.com/javase/tutorial/i18n/locale/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

Интернационализированная программа может отображать информацию по-разному в разных частях
мира. Например, программа будет показывать разные сообщения в Париже, Токио и Нью-Йорке.
Если процесс локализации тщательно настроен, программа покажет разные сообщения в Нью-Йорке
и Лондоне, учитывая различия между американским и британским английским. Как же
интернационализированная программа определяет подходящие язык и регион своих конечных
пользователей? Очень просто. Она обращается к объекту `Locale`.

Объект `Locale` (локаль) — это идентификатор конкретного сочетания языка и региона. Если
класс меняет своё поведение в зависимости от `Locale`, говорят, что он *чувствителен к
локали* (*locale-sensitive*). Например, класс `NumberFormat` чувствителен к локали: формат
возвращаемого им числа зависит от `Locale`. Так, `NumberFormat` может вернуть число как
902 300 (Франция), или 902.300 (Германия), или 902,300 (США). Объекты `Locale` — это лишь
идентификаторы. Реальную работу (например, форматирование и определение границ слов)
выполняют методы классов, чувствительных к локали.

В следующих разделах объясняется, как работать с объектами `Locale`.

## Создание локали (Creating a Locale)

Существует несколько способов создать объект `Locale`. Независимо от выбранной техники,
создание может быть таким же простым, как указание языкового кода (language code). Однако
вы можете дополнительно уточнить локаль, задав коды региона (region; также называемого
«страной», country) и варианта (variant). Если вы используете выпуск JDK 7 или новее, вы
также можете указать код письменности (script code) и расширения локали Unicode (Unicode
locale extensions).

Четыре способа создать объект `Locale`:

- класс `Locale.Builder`;
- конструкторы `Locale`;
- фабричный метод `Locale.forLanguageTag`;
- константы `Locale`.

---

**Примечание о версии:** Класс `Locale.Builder` и метод `forLanguageTag` были добавлены в
выпуске Java SE 7.

---

### Класс `Locale.Builder`

Вспомогательный класс [`Locale.Builder`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.Builder.html)
можно использовать для конструирования объекта `Locale`, соответствующего синтаксису IETF
BCP 47. Например, чтобы задать французский язык и страну Канаду, вы можете вызвать конструктор
`Locale.Builder`, а затем выстроить цепочку методов-сеттеров:

```java
Locale aLocale = new Locale.Builder().setLanguage("fr").setRegion("CA").build();
```

Следующий пример создаёт объекты `Locale` для английского языка в США и Великобритании:

```java
Locale bLocale = new Locale.Builder().setLanguage("en").setRegion("US").build();
Locale cLocale = new Locale.Builder().setLanguage("en").setRegion("GB").build();
```

Заключительный пример создаёт объект `Locale` для русского языка:

```java
Locale dLocale = new Locale.Builder().setLanguage("ru").setScript("Cyrl").build();
```

### Конструкторы `Locale`

В классе `Locale` доступны три конструктора для создания объекта `Locale`:

- `Locale(String language)`;
- `Locale(String language, String country)`;
- `Locale(String language, String country, String variant)`.

Следующие примеры создают объекты `Locale` для французского языка в Канаде, английского
языка в США и Великобритании, а также для русского языка:

```java
aLocale = new Locale("fr", "CA");
bLocale = new Locale("en", "US");
cLocale = new Locale("en", "GB");
dLocale = new Locale("ru");
```

В выпуске ранее JDK 7 задать код письменности (script code) для объекта `Locale`
невозможно.

### Фабричный метод `forLanguageTag`

Если у вас есть строка языкового тега (language tag), соответствующая стандарту IETF BCP 47,
вы можете воспользоваться фабричным методом [`forLanguageTag(String)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#forLanguageTag-java.lang.String-),
который был введён в выпуске Java SE 7. Например:

```java
Locale aLocale = Locale.forLanguageTag("en-US");
Locale bLocale = Locale.forLanguageTag("ja-JP-u-ca-japanese");
```

### Константы `Locale`

Для вашего удобства класс `Locale` предоставляет [константы](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#field_summary)
для некоторых языков и стран. Например:

```java
cLocale = Locale.JAPAN;
dLocale = Locale.CANADA_FRENCH;
```

Когда вы указываете языковую константу, часть `Locale`, отвечающая за регион, остаётся
неопределённой. Следующие три инструкции создают эквивалентные объекты `Locale`:

```java
j1Locale = Locale.JAPANESE;
j2Locale = new Locale.Builder().setLanguage("ja").build();
j3Locale = new Locale("ja");
```

Объекты `Locale`, создаваемые следующими тремя инструкциями, также эквивалентны:

```java
j4Locale = Locale.JAPAN;
j5Locale = new Locale.Builder().setLanguage("ja").setRegion("JP").build();
j6Locale = new Locale("ja", "JP");
```

### Коды

В следующих разделах рассматриваются языковой код и необязательные коды письменности,
региона и варианта.

#### Языковой код (Language Code)

Языковой код — это две или три строчные буквы, соответствующие стандарту ISO 639. Полный
список кодов ISO 639 можно найти по адресу
[http://www.loc.gov/standards/iso639-2/php/code_list.php](http://www.loc.gov/standards/iso639-2/php/code_list.php).

В следующей таблице перечислены некоторые из языковых кодов.

| Языковой код | Описание |
|--------------|----------|
| `de` | Немецкий |
| `en` | Английский |
| `fr` | Французский |
| `ru` | Русский |
| `ja` | Японский |
| `jv` | Яванский |
| `ko` | Корейский |
| `zh` | Китайский |

#### Код письменности (Script Code)

Код письменности начинается с заглавной буквы, за которой следуют три строчные буквы, и
соответствует стандарту ISO 15924. Полный список кодов ISO 15924 можно найти по адресу
[http://unicode.org/iso15924/iso15924-codes.html](http://unicode.org/iso15924/iso15924-codes.html).

В следующей таблице перечислены некоторые из кодов письменности.

| Код письменности | Описание |
|------------------|----------|
| `Arab` | Арабская |
| `Cyrl` | Кириллица |
| `Kana` | Катакана |
| `Latn` | Латиница |

Существует три метода для получения информации о письменности для `Locale`:

- [`getScript()`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getScript--) —
  возвращает 4-буквенный код письменности для объекта `Locale`. Если для локали письменность
  не определена, возвращается пустая строка.
- [`getDisplayScript()`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getDisplayScript--) —
  возвращает имя письменности локали, пригодное для отображения пользователю. По возможности
  имя будет локализовано для локали по умолчанию. Так, например, если код письменности —
  «Latn», для англоязычной локали отображаемое имя письменности будет строкой «Latin».
- [`getDisplayScript(Locale)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getDisplayScript-java.util.Locale-) —
  возвращает отображаемое имя указанной `Locale`, локализованное, если это возможно, для
  данной локали.

#### Код региона (Region Code)

Код региона (страны) состоит из двух или трёх заглавных букв, соответствующих стандарту
ISO 3166, либо из трёх цифр, соответствующих стандарту UN M.49. Копию кодов можно найти по
адресу [http://www.chemie.fu-berlin.de/diverse/doc/ISO_3166.html](http://www.chemie.fu-berlin.de/diverse/doc/ISO_3166.html).

Следующая таблица содержит несколько примеров кодов стран и регионов.

| Код A-2 | Код A-3 | Числовой код | Описание |
|---------|---------|--------------|----------|
| `AU` | `AUS` | `036` | Австралия |
| `BR` | `BRA` | `076` | Бразилия |
| `CA` | `CAN` | `124` | Канада |
| `CN` | `CHN` | `156` | Китай |
| `DE` | `DEU` | `276` | Германия |
| `FR` | `FRA` | `250` | Франция |
| `IN` | `IND` | `356` | Индия |
| `RU` | `RUS` | `643` | Российская Федерация |
| `US` | `USA` | `840` | Соединённые Штаты |

#### Код варианта (Variant Code)

Необязательный код варианта (`variant`) можно использовать для дальнейшего уточнения вашей
`Locale`. Например, код варианта может применяться для указания диалектных различий, которые
не покрываются кодом региона.

---

**Примечание о версии:** До выпуска Java SE 7 код варианта иногда использовался для
обозначения различий, не связанных с языком или регионом. Например, он мог применяться для
обозначения различий между вычислительными платформами, такими как Windows или UNIX. Согласно
стандарту IETF BCP 47, такое использование не рекомендуется.

Чтобы определить вариации, не связанные с языком, но актуальные для вашей среды, используйте
механизм расширений, как описано в разделе [Расширения BCP 47 (BCP 47 Extensions)](#расширения-bcp-47-bcp-47-extensions).

---

Начиная с выпуска Java SE 7, который соответствует стандарту IETF BCP 47, код варианта
используется специально для обозначения дополнительных вариаций, определяющих язык или его
диалекты. Стандарт IETF BCP 47 накладывает синтаксические ограничения на подтег варианта.
Список кодов вариантов (искать слово *variant*) можно увидеть по адресу
[http://www.iana.org/assignments/language-subtag-registry](http://www.iana.org/assignments/language-subtag-registry).

Например, Java SE использует код варианта для поддержки тайского языка. По соглашению объект
`NumberFormat` для локалей `th` и `th_TH` будет использовать общепринятые арабские цифры
(Arabic digit shapes, или Arabic numerals) для форматирования тайских чисел. Однако
`NumberFormat` для локали `th_TH_TH` использует начертания тайских цифр. Это демонстрирует
фрагмент из файла `ThaiDigits.java`:

```java
String outputString = new String();
Locale[] thaiLocale = {
             new Locale("th"),
             new Locale("th", "TH"),
             new Locale("th", "TH", "TH")
         };

for (Locale locale : thaiLocale) {
    NumberFormat nf = NumberFormat.getNumberInstance(locale);
    outputString = outputString + locale.toString() + ": ";
    outputString = outputString + nf.format(573.34) + "\n";
}
```

Ниже приведён скриншот этого примера (в оригинале — изображение `thaidigits.jpg`), на
котором показан вывод программы: для локали `th` число форматируется как `573.34`, для
`th_TH` — также арабскими цифрами, а для `th_TH_TH` — начертаниями тайских цифр.

## Область действия локали (The Scope of a Locale)

Платформа Java не требует использовать одну и ту же `Locale` на протяжении всей программы.
При желании вы можете назначить отдельную `Locale` каждому чувствительному к локали объекту
в вашей программе. Такая гибкость позволяет разрабатывать многоязычные приложения, которые
могут отображать информацию на нескольких языках.

Тем не менее большинство приложений не являются многоязычными, и их чувствительные к локали
объекты полагаются на `Locale` по умолчанию (default `Locale`). Установленная виртуальной
машиной Java при её запуске, `Locale` по умолчанию соответствует локали хост-платформы.
Чтобы определить `Locale` по умолчанию вашей виртуальной машины Java, вызовите метод
`Locale.getDefault`.

**Примечание:** Можно независимо задать локаль по умолчанию для двух типов использования:
настройка *format* применяется для форматирования ресурсов, а настройка *display* — в меню
и диалоговых окнах. Введённый в выпуске Java SE 7 метод
[`Locale.getDefault(Locale.Category)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getDefault-java.util.Locale.Category-)
принимает параметр [`Locale.Category`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.Category.html).
Передача перечислимой константы `FORMAT` методу `getDefault(Locale.Category)` возвращает
локаль по умолчанию для форматирования ресурсов. Аналогично, передача константы `DISPLAY`
возвращает локаль по умолчанию, используемую интерфейсом (UI). Соответствующий метод
[`setDefault(Locale.Category, Locale)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#setDefault-java.util.Locale.Category-java.util.Locale-)
позволяет задать локаль для нужной категории. Метод `getDefault` без аргументов возвращает
значение по умолчанию для `DISPLAY`.

На платформе Windows эти значения по умолчанию инициализируются в соответствии с настройками
«Стандарты и форматы» (Standards and Formats) и «Язык интерфейса» (Display Language) на
панели управления Windows.

Вам не следует задавать `Locale` по умолчанию программно, поскольку она используется
совместно всеми классами, чувствительными к локали.

Распределённые вычисления порождают ряд интересных вопросов. Например, предположим, вы
проектируете сервер приложений, который будет получать запросы от клиентов из разных стран.
Если `Locale` для каждого клиента различна, какой должна быть `Locale` сервера? Возможно,
сервер многопоточный, и каждый поток настроен на `Locale` клиента, которого он обслуживает.
А может быть, все данные, передаваемые между сервером и клиентами, должны быть
независимыми от локали (locale-independent).

Какой подход к проектированию выбрать? Если это возможно, данные, передаваемые между сервером
и клиентами, должны быть независимыми от локали. Это упрощает проектирование сервера, делая
клиентов ответственными за отображение данных с учётом локали. Однако такой подход не
сработает, если сервер должен хранить данные в форме, зависящей от локали. Например, сервер
может хранить испанскую, английскую и французскую версии одних и тех же данных в разных
столбцах базы данных. В этом случае серверу может потребоваться запросить у клиента его
`Locale`, поскольку `Locale` могла измениться с момента последнего запроса.

## Расширения BCP 47 (BCP 47 Extensions)

Выпуск Java SE 7 соответствует стандарту IETF BCP 47, который поддерживает добавление
расширений (extensions) к `Locale`. Для обозначения расширения может использоваться любой
одиночный символ, но есть два предопределённых кода расширений: `'u'` задаёт *расширение
локали Unicode* (*Unicode locale extension*), а `'x'` задаёт *расширение частного
использования* (*private use extension*).

Расширения локали Unicode определяются проектом Unicode
[Common Locale Data Repository (CLDR)](http://cldr.unicode.org/). Они используются для
указания информации, не связанной с языком, такой как календари или валюта. Расширение
частного использования может применяться для указания любой другой информации, например
платформы (Windows, UNIX или Linux) или сведений о выпуске (например, 6u23 или JDK 7).

Расширение задаётся как пара «ключ/значение», где ключ — это одиночный символ (обычно `'u'`
или `'x'`). Правильно оформленное значение имеет следующий формат:

```
SUBTAG ('-' SUBTAG)*
```

В этом формате:

```
SUBTAG = [0-9a-zA-Z]{2,8}    Для key='u'
SUBTAG = [0-9a-zA-Z]{1,8}    Для key='x'
```

Обратите внимание, что для расширения частного использования допускается одно-символьное
значение. Однако для значений в расширении локали Unicode действует минимум в 2 символа.

Строки расширений нечувствительны к регистру, но класс `Locale` приводит все ключи и значения
к нижнему регистру.

Метод [`getExtensionKeys()`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getExtensionKeys--)
возвращает множество ключей расширений (если они есть) для `Locale`. Метод
[`getExtension(key)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getExtension-char-)
возвращает строку значения для указанного ключа (если оно есть).

### Расширения локали Unicode (Unicode Locale Extensions)

Как упоминалось ранее, расширение локали Unicode задаётся кодом ключа `'u'` или константой
`UNICODE_LOCALE_EXTENSION`. Само значение также задаётся парой «ключ/тип». Допустимые
значения определены в таблице [Key/Type Definitions](http://www.unicode.org/reports/tr35/#Key_Type_Definitions)
на сайте [Unicode](http://www.unicode.org). Код ключа задаётся двумя буквенными символами.
В следующей таблице перечислены ключи расширений локали Unicode.

| Код ключа | Описание |
|-----------|----------|
| ca | алгоритм календаря (calendar algorithm) |
| co | тип сортировки/сопоставления (collation type) |
| ka | параметры сортировки (collation parameters) |
| cu | тип валюты (currency type) |
| nu | тип чисел (number type) |
| va | общий тип варианта (common variant type) |

**Примечание:** Указание расширения локали Unicode (например, формата чисел) не гарантирует,
что службы локали базовой платформы выполнят этот запрос.

В следующей таблице показаны некоторые примеры пар «ключ/тип» для расширения локали Unicode.

| Пара «ключ/тип» | Описание |
|-----------------|----------|
| ca-buddhist | тайский буддийский календарь |
| co-pinyin | упорядочивание пиньинь для латиницы |
| cu-usd | доллары США |
| nu-jpanfin | японские финансовые числа |
| tz-aldav | Европа/Андорра |

Следующая строка представляет локаль немецкого языка для страны Германии с использованием
телефонного (phonebook) стиля упорядочивания для платформы Linux. Этот пример также содержит
атрибут с именем `"email"`:

```
de-DE-u-email-co-phonebk-x-linux
```

Следующие методы `Locale` можно использовать для доступа к информации о расширениях локали
Unicode. Эти методы описаны на примере предыдущей немецкой локали.

- [`getUnicodeLocaleKeys()`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getUnicodeLocaleKeys--) —
  возвращает коды ключей локали Unicode или пустое множество, если у локали их нет. Для
  немецкого примера это вернуло бы множество, содержащее единственную строку `"co"`.
- [`getUnicodeLocaleType(String)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getUnicodeLocaleType-java.lang.String-) —
  возвращает тип локали Unicode, связанный с кодом ключа локали Unicode. Вызов
  `getUnicodeLocaleType("co")` для немецкого примера вернул бы строку `"phonebk"`.
- [`getUnicodeLocaleAttributes()`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#getUnicodeLocaleAttributes--) —
  возвращает множество атрибутов локали Unicode, связанных с этой локалью (если они есть).
  В немецком примере это вернуло бы множество, содержащее единственную строку `"email"`.

### Расширения частного использования (Private Use Extensions)

Расширение частного использования, задаваемое кодом ключа `'x'` или константой
`PRIVATE_USE_EXTENSION`, может быть чем угодно, лишь бы значение было правильно оформлено.

Ниже приведены примеры возможных расширений частного использования:

```
x-jdk-1-7
x-linux
```

## Фильтрация и поиск языковых тегов (Language Tag Filtering and Lookup)

Язык программирования Java содержит средства интернационализации для языковых тегов
(language tags), фильтрации языковых тегов (language tag filtering) и поиска языковых тегов
(language tag lookup). Эти возможности определены стандартом
[IETF BCP 47](http://tools.ietf.org/html/bcp47), который включает
[RFC 5646 «Tags for Identifying Languages»](http://tools.ietf.org/html/rfc5646) и
[RFC 4647 «Matching of Language Tags»](http://tools.ietf.org/html/rfc4647). В этом уроке
описано, как эта поддержка реализована в JDK.

### Что такое языковые теги? (What Are Language Tags?)

Языковые теги — это специально отформатированные строки, предоставляющие информацию о
конкретном языке. Языковой тег может быть чем-то простым (например, «en» для английского),
чем-то сложным (например, «zh-cmn-Hans-CN» для китайского, мандаринского, упрощённой
письменности, используемого в Китае) или чем-то промежуточным (например, «sr-Latn» для
сербского, записанного латиницей). Языковые теги состоят из «подтегов» (subtags),
разделённых дефисами; эта терминология используется на протяжении всей документации API.

Класс [`java.util.Locale`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html)
обеспечивает поддержку языковых тегов. `Locale` содержит несколько различных полей: язык
(language, например «en» для английского или «ja» для японского), письменность (script,
например «Latn» для латиницы или «Cyrl» для кириллицы), страна (country, например «US» для
Соединённых Штатов или «FR» для Франции), вариант (variant, который указывает некоторую
вариацию локали) и расширения (extensions, предоставляющие отображение одно-символьных ключей
в значения `String`, обозначая расширения помимо идентификации языка). Чтобы создать объект
`Locale` из строки языкового тега `String`, вызовите
[`Locale.forLanguageTag(String)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html#forLanguageTag-java.lang.String-),
передав языковой тег в качестве единственного аргумента. Это создаёт и возвращает новый
объект `Locale` для использования в вашем приложении.

Пример 1:

```java
package languagetagdemo;

import java.util.Locale;

public class LanguageTagDemo {
     public static void main(String[] args) {
         Locale l = Locale.forLanguageTag("en-US");
     }
}
```

Обратите внимание, что API `Locale` требует лишь, чтобы ваш языковой тег был синтаксически
корректным. Он не выполняет никакой дополнительной проверки (например, не проверяет, что тег
зарегистрирован в реестре языковых подтегов IANA — IANA Language Subtag Registry).

### Что такое языковые диапазоны? (What Are Language Ranges?)

Языковые диапазоны (language ranges, представленные классом
[`java.util.Locale.LanguageRange`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.LanguageRange.html))
идентифицируют наборы языковых тегов, разделяющих определённые атрибуты. Языковые диапазоны
классифицируются как базовые (basic) или расширенные (extended) и похожи на языковые теги
тем, что состоят из подтегов, разделённых дефисами. Примеры базовых языковых диапазонов:
«en» (английский), «ja-JP» (японский, Япония) и «*» (специальный языковой диапазон, который
соответствует любому языковому тегу). Примеры расширенных языковых диапазонов: «*-CH» (любой
язык, Швейцария), «es-*» (испанский, любые регионы) и «zh-Hant-*» (традиционный китайский,
любой регион).

Кроме того, языковые диапазоны могут храниться в списках языковых приоритетов (Language
Priority Lists), которые позволяют пользователям приоритизировать свои языковые предпочтения
во взвешенном списке. Списки языковых приоритетов выражаются помещением объектов
`LanguageRange` в [`java.util.List`](https://docs.oracle.com/javase/8/docs/api/java/util/List.html),
который затем может быть передан методам `Locale`, принимающим `List` объектов
`LanguageRange`.

### Создание языкового диапазона (Creating a Language Range)

Класс [`Locale.LanguageRange`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.LanguageRange.html)
предоставляет два различных конструктора для создания языковых диапазонов:

- `public Locale.LanguageRange(String range)`;
- `public Locale.LanguageRange(String range, double weight)`.

Единственное различие между ними в том, что вторая версия позволяет указать вес (weight);
этот вес будет учитываться, если диапазон помещён в список языковых приоритетов.

`Locale.LanguageRange` также определяет некоторые константы для использования с этими
конструкторами:

- `public static final double MAX_WEIGHT`;
- `public static final double MIN_WEIGHT`.

Константа `MAX_WEIGHT` содержит значение 1.0, которое указывает, что это хорошее соответствие
для пользователя. Константа `MIN_WEIGHT` содержит значение 0.0, указывающее, что это не так.

Пример 2:

```java
package languagetagdemo;

import java.util.Locale;

public class LanguageTagDemo {

     public static void main(String[] args) {
         // Создать Locale
         Locale l = Locale.forLanguageTag("en-US");

         // Определить несколько объектов LanguageRange
         Locale.LanguageRange range1 = new Locale.LanguageRange("en-US",Locale.LanguageRange.MAX_WEIGHT);
         Locale.LanguageRange range2 = new Locale.LanguageRange("en-GB*",0.5);
         Locale.LanguageRange range3 = new Locale.LanguageRange("fr-FR",Locale.LanguageRange.MIN_WEIGHT);
     }
}
```

Пример 2 создаёт три языковых диапазона: английский (Соединённые Штаты), английский
(Великобритания) и французский (Франция). Эти диапазоны взвешены, чтобы выразить предпочтения
пользователя, в порядке от наиболее предпочтительного к наименее предпочтительному.

### Создание списка языковых приоритетов (Creating a Language Priority List)

Вы можете создать список языковых приоритетов из списка языковых диапазонов с помощью метода
[`LanguageRange.parse(String)`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.LanguageRange.html#parse-java.lang.String-).
Этот метод принимает список языковых диапазонов, разделённых запятыми, выполняет
синтаксическую проверку каждого языкового диапазона в заданных диапазонах, а затем возвращает
вновь созданный список языковых приоритетов.

Подробную информацию о требуемом формате параметра «ranges» см. в спецификации API для этого
метода.

Пример 3:

```java
package languagetagdemo;

import java.util.Locale;

import java.util.List;

public class LanguageTagDemo {

    public static void main(String[] args) {

        // Создать Locale

        Locale l = Locale.forLanguageTag("en-US");

        // Создать список языковых приоритетов

        String ranges = "en-US;q=1.0,en-GB;q=0.5,fr-FR;q=0.0";

        List<Locale.LanguageRange> languageRanges = Locale.LanguageRange.parse(ranges)

    }
}
```

Пример 3 создаёт те же три языковых диапазона, что и Пример 2, но хранит их в объекте
`String`, который передаётся методу `parse(String)`. Возвращённый `List` объектов
`LanguageRange` и есть список языковых приоритетов.

### Фильтрация языковых тегов (Filtering Language Tags)

Фильтрация языковых тегов — это процесс сопоставления набора языковых тегов со списком
языковых приоритетов пользователя. Результатом фильтрации будет полный список всех совпавших
результатов. Класс `Locale` определяет два метода `filter`, возвращающие список объектов
`Locale`. Их сигнатуры таковы:

- `public static List<Locale> filter (List<Locale.LanguageRange> priorityList, Collection<Locale> locales)`;
- `public static List<Locale> filter (List<Locale.LanguageRange> priorityList, Collection<Locale> locales, Locale.FilteringMode mode)`.

В обоих методах первый аргумент задаёт список языковых приоритетов пользователя, как описано
в предыдущем разделе.

Второй аргумент задаёт `Collection` объектов `Locale`, с которыми происходит сопоставление.
Само сопоставление будет проходить согласно правилам, указанным в RFC 4647.

Третий аргумент (если он предоставлен) задаёт используемый «режим фильтрации» (filtering
mode). Перечисление [`Locale.FilteringMode`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.FilteringMode.html)
предоставляет ряд различных значений на выбор, таких как `AUTOSELECT_FILTERING` (для
фильтрации базовых языковых диапазонов) или `EXTENDED_FILTERING` (для фильтрации расширенных
языковых диапазонов).

Пример 4 демонстрирует фильтрацию языковых тегов.

Пример 4:

```java
package languagetagdemo;

import java.util.Locale;
import java.util.Collection;
import java.util.List;
import java.util.ArrayList;

public class LanguageTagDemo {

    public static void main(String[] args) {

        // Создать коллекцию объектов Locale для фильтрации
        Collection<Locale> locales = new ArrayList<>();
        locales.add(Locale.forLanguageTag("en-GB"));
        locales.add(Locale.forLanguageTag("ja"));
        locales.add(Locale.forLanguageTag("zh-cmn-Hans-CN"));
        locales.add(Locale.forLanguageTag("en-US"));

        // Выразить предпочтения пользователя списком языковых приоритетов
        String ranges = "en-US;q=1.0,en-GB;q=0.5,fr-FR;q=0.0";
        List<Locale.LanguageRange> languageRanges = Locale.LanguageRange.parse(ranges);

        // Теперь отфильтровать объекты Locale, возвращая любые совпадения
        List<Locale> results = Locale.filter(languageRanges,locales);

        // Вывести совпадения
        for(Locale l : results){
        System.out.println(l.toString());
        }
    }
}
```

Вывод этой программы:

```
en_US
en_GB
```

Этот возвращённый список упорядочен в соответствии с весами, указанными в списке языковых
приоритетов пользователя.

Класс `Locale` также определяет методы `filterTags` для фильтрации языковых тегов как
объектов `String`.

Сигнатуры методов таковы:

- `public static List<String> filterTags (List<Locale.LanguageRange> priorityList, Collection<String> tags)`;
- `public static List<String> filterTags (List<Locale.LanguageRange> priorityList, Collection<String> tags, Locale.FilteringMode mode)`.

Пример 5 выполняет тот же поиск, что и Пример 4, но использует объекты `String` вместо
объектов `Locale`.

Пример 5:

```java
package languagetagdemo;

import java.util.Locale;
import java.util.Collection;
import java.util.List;
import java.util.ArrayList;

public class LanguageTagDemo {

    public static void main(String[] args) {

        // Создать коллекцию объектов String для сопоставления
        Collection<String> tags = new ArrayList<>();
        tags.add("en-GB");
        tags.add("ja");
        tags.add("zh-cmn-Hans-CN");
        tags.add("en-US");

        // Выразить предпочтения пользователя списком языковых приоритетов
        String ranges = "en-US;q=1.0,en-GB;q=0.5,fr-FR;q=0.0";
        List<Locale.LanguageRange> languageRanges = Locale.LanguageRange.parse(ranges);

        // Теперь найти в локалях наилучшее совпадение
        List<String> results = Locale.filterTags(languageRanges,tags);

        // Вывести совпадения
        for(String s : results){
            System.out.println(s);
        }
    }
}
```

Как и прежде, поиск сопоставит и вернёт «en-US» и «en-GB» (именно в этом порядке).

### Выполнение поиска языкового тега (Performing Language Tag Lookup)

В отличие от фильтрации языковых тегов, поиск языкового тега — это процесс сопоставления
языковых диапазонов с наборами языковых тегов и возврата одного языкового тега, который
наилучшим образом соответствует диапазону. RFC 4647 гласит: «Поиск (Lookup) выдаёт
единственный результат, который наилучшим образом соответствует предпочтениям пользователя
из списка доступных тегов, поэтому он полезен в случаях, когда требуется один элемент (и для
которых может быть возвращён только один элемент). Например, если процесс вставляет
читаемое человеком сообщение об ошибке в заголовок протокола, он может выбрать текст на
основе списка языковых приоритетов пользователя. Поскольку процесс может вернуть только один
элемент, он вынужден выбрать единственный элемент и должен вернуть какой-то элемент, даже
если ни один из языковых тегов содержимого не соответствует списку языковых приоритетов,
предоставленному пользователем».

Пример 6:

```java
package languagetagdemo;

import java.util.Locale;
import java.util.Collection;
import java.util.List;
import java.util.ArrayList;

public class LanguageTagDemo {

    public static void main(String[] args) {

        // Создать коллекцию объектов Locale для поиска
        Collection<Locale> locales = new ArrayList<>();
        locales.add(Locale.forLanguageTag("en-GB"));
        locales.add(Locale.forLanguageTag("ja"));
        locales.add(Locale.forLanguageTag("zh-cmn-Hans-CN"));
        locales.add(Locale.forLanguageTag("en-US"));

        // Выразить предпочтения пользователя списком языковых приоритетов
        String ranges = "en-US;q=1.0,en-GB;q=0.5,fr-FR;q=0.0";
        List<Locale.LanguageRange> languageRanges = Locale.LanguageRange.parse(ranges);

        // Найти НАИЛУЧШЕЕ совпадение и вернуть лишь один результат
        Locale result = Locale.lookup(languageRanges,locales);
        System.out.println(result.toString());
    }
}
```

В отличие от примеров фильтрации, демонстрация поиска в Примере 6 возвращает один объект,
который является наилучшим совпадением (`en-US` в данном случае). Для полноты Пример 7
показывает, как выполнить тот же поиск, используя объекты `String`.

Пример 7:

```java
package languagetagdemo;

import java.util.Locale;
import java.util.Collection;
import java.util.List;
import java.util.ArrayList;

public class LanguageTagDemo {

    public static void main(String[] args) {
        // Создать коллекцию объектов String для сопоставления
        Collection<String> tags = new ArrayList<>();
        tags.add("en-GB");
        tags.add("ja");
        tags.add("zh-cmn-Hans-CN");
        tags.add("en-US");

        // Выразить предпочтения пользователя списком языковых приоритетов
        String ranges = "en-US;q=1.0,en-GB;q=0.5,fr-FR;q=0.0";
        List<Locale.LanguageRange> languageRanges = Locale.LanguageRange.parse(ranges);

        // Найти НАИЛУЧШЕЕ совпадение и вернуть лишь один результат
        String result = Locale.lookupTag(languageRanges, tags);
        System.out.println(result);
    }
}
```

Этот пример возвращает единственный объект, наилучшим образом соответствующий списку
языковых приоритетов пользователя.

## Источник

- [Setting the Locale](https://docs.oracle.com/javase/tutorial/i18n/locale/index.html) — официальное руководство Oracle (индекс урока).
- [Creating a Locale](https://docs.oracle.com/javase/tutorial/i18n/locale/create.html) — официальное руководство Oracle.
- [The Scope of a Locale](https://docs.oracle.com/javase/tutorial/i18n/locale/scope.html) — официальное руководство Oracle.
- [BCP 47 Extensions](https://docs.oracle.com/javase/tutorial/i18n/locale/extensions.html) — официальное руководство Oracle.
- [Language Tag Filtering and Lookup](https://docs.oracle.com/javase/tutorial/i18n/locale/matching.html) — официальное руководство Oracle.
</content>
</invoke>
