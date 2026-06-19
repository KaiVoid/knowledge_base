# Урок 5. Работа с текстом

**Трейл:** Internationalization · **Оригинал:** [Working with Text](https://docs.oracle.com/javase/tutorial/i18n/text/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок собран из
> страницы-индекса и всех её подстраниц: проверка свойств символов, сравнение строк
> (`Collator`), Unicode, определение границ текста (`BreakIterator`), преобразование латинских
> цифр, преобразование не-Unicode текста, нормализация и работа с двунаправленным текстом.

Почти все программы с пользовательским интерфейсом работают с текстом. На международном рынке
текст, который отображают ваши программы, должен соответствовать правилам языков со всего мира.
Язык программирования Java предоставляет ряд классов, помогающих обрабатывать текст
локале-независимым образом.

## Проверка свойств символов

Символы можно классифицировать по их свойствам. Например, `X` — это заглавная буква, а `4` —
десятичная цифра. Проверка свойств символов — распространённый способ контроля данных, введённых
конечным пользователем. Если вы, к примеру, продаёте книги онлайн, экран ввода заказа должен
проверять, что символы в поле количества — все цифры.

Разработчики, не привыкшие писать глобальное (рассчитанное на все языки) ПО, могут определять
свойства символа, сравнивая его с символьными константами. Например, они могут написать такой код:

```java
char ch;
//...

// Этот код НЕВЕРЕН!

// проверка, является ли ch буквой
if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z'))
    // ...

// проверка, является ли ch цифрой
if (ch >= '0' && ch <= '9')
    // ...

// проверка, является ли ch пробельным символом
if ((ch == ' ') || (ch =='\n') || (ch == '\t'))
    // ...
```

Приведённый код *неверен*, потому что работает только с английским и ещё несколькими языками.
Чтобы интернационализировать предыдущий пример, замените его следующими инструкциями:

```java
char ch;
// ...

// Этот код ВЕРЕН!

if (Character.isLetter(ch))
    // ...

if (Character.isDigit(ch))
    // ...

if (Character.isSpaceChar(ch))
    // ...
```

Методы класса `Character` опираются на стандарт Unicode при определении свойств символа.
Unicode — это 16-битная кодировка символов, поддерживающая основные языки мира. В языке Java
значения типа `char` представляют символы Unicode. Если вы проверяете свойства `char`
подходящим методом `Character`, ваш код будет работать со всеми основными языками. Например,
метод `Character.isLetter` возвращает `true`, если символ — буква в китайском, немецком,
арабском или другом языке.

Вот некоторые из наиболее полезных методов сравнения класса `Character`:

- `isDigit`
- `isLetter`
- `isLetterOrDigit`
- `isLowerCase`
- `isUpperCase`
- `isSpaceChar`
- `isDefined`

Метод `Character.getType` возвращает Unicode-категорию символа. Каждой категории соответствует
константа, определённая в классе `Character`. Например, для символа `A` метод `getType`
возвращает константу `Character.UPPERCASE_LETTER`. Следующий пример показывает, как использовать
`getType` и константы-категории класса `Character`. Все выражения в этих `if` истинны:

```java
if (Character.getType('a') == Character.LOWERCASE_LETTER)
    // ...

if (Character.getType('R') == Character.UPPERCASE_LETTER)
    // ...

if (Character.getType('>') == Character.MATH_SYMBOL)
    // ...

if (Character.getType('_') == Character.CONNECTOR_PUNCTUATION)
    // ...
```

## Сравнение строк

Приложения, сортирующие текст, выполняют частые сравнения строк. Например, генератор отчётов
сравнивает строки при сортировке списка в алфавитном порядке.

Если аудитория вашего приложения ограничена людьми, говорящими по-английски, вы, вероятно,
можете выполнять сравнение строк методом `String.compareTo`. Метод `String.compareTo` выполняет
двоичное (бинарное) сравнение символов Unicode внутри двух строк. Однако для большинства языков
на это двоичное сравнение нельзя полагаться при сортировке строк, потому что значения Unicode не
соответствуют относительному порядку символов.

К счастью, класс [`Collator`](https://docs.oracle.com/javase/8/docs/api/java/text/Collator.html)
позволяет приложению выполнять сравнение строк для разных языков. В этом разделе вы узнаете, как
использовать класс `Collator` при сортировке текста.

### Локале-независимые сравнения

Правила сопоставления (collation rules) определяют порядок сортировки строк. Эти правила
различаются в зависимости от локали (locale), поскольку разные естественные языки сортируют
слова по-разному. Используя предопределённые правила сопоставления, предоставляемые классом
`Collator`, можно сортировать строки локале-независимым образом.

Чтобы получить экземпляр класса `Collator`, вызовите метод `getInstance`. Обычно `Collator`
создают для локали по умолчанию, как в примере:

```java
Collator myDefaultCollator = Collator.getInstance();
```

Можно также указать конкретную локаль (`Locale`) при создании `Collator`:

```java
Collator myFrenchCollator = Collator.getInstance(Locale.FRENCH);
```

Метод `getInstance` возвращает `RuleBasedCollator` — конкретный подкласс `Collator`.
`RuleBasedCollator` содержит набор правил, определяющих порядок сортировки строк для указанной
локали. Эти правила предопределены для каждой локали. Поскольку правила инкапсулированы внутри
`RuleBasedCollator`, вашей программе не нужны специальные процедуры для обработки того, как
правила сопоставления различаются между языками.

Для локале-независимого сравнения строк вызывается метод `Collator.compare`. Метод `compare`
возвращает целое число меньше нуля, равное нулю или больше нуля, когда первый строковый аргумент
соответственно меньше, равен или больше второго. Несколько примеров вызовов `Collator.compare`:

| Пример | Возвращаемое значение | Пояснение |
|--------|----------------------|-----------|
| `myCollator.compare("abc", "def")` | `-1` | `"abc"` меньше, чем `"def"` |
| `myCollator.compare("rtf", "rtf")` | `0` | две строки равны |
| `myCollator.compare("xyz", "abc")` | `1` | `"xyz"` больше, чем `"abc"` |

Метод `compare` используется при выполнении сортировки. Пример программы `CollatorDemo`
использует `compare` для сортировки массива английских и французских слов. Эта программа
показывает, что может произойти при сортировке одного и того же списка слов двумя разными
коллаторами:

```java
Collator fr_FRCollator = Collator.getInstance(new Locale("fr","FR"));
Collator en_USCollator = Collator.getInstance(new Locale("en","US"));
```

Метод сортировки `sortStrings` можно использовать с любым `Collator`. Обратите внимание, что
`sortStrings` вызывает метод `compare`:

```java
public static void sortStrings(Collator collator, String[] words) {
    String tmp;
    for (int i = 0; i < words.length; i++) {
        for (int j = i + 1; j < words.length; j++) {
            if (collator.compare(words[i], words[j]) > 0) {
                tmp = words[i];
                words[i] = words[j];
                words[j] = tmp;
            }
        }
    }
}
```

Английский `Collator` сортирует слова так:

```
peach
péché
pêche
sin
```

Согласно правилам сопоставления французского языка приведённый список упорядочен неправильно.
Во французском `péché` должно следовать после `pêche` в отсортированном списке. Французский
`Collator` сортирует массив слов корректно:

```
peach
pêche
péché
sin
```

### Настройка правил сопоставления

Если предопределённые правила сопоставления вам не подходят, можно разработать собственные
правила и присвоить их объекту `RuleBasedCollator`. Например, может потребоваться отсортировать
строки на языке, локаль которого не поддерживается классом `Collator`.

Пользовательские правила сопоставления хранятся в объекте `String`, который передаётся в
конструктор `RuleBasedCollator`. Простой пример:

```java
String simpleRule = "< a < b < c < d";
RuleBasedCollator simpleCollator =  new RuleBasedCollator(simpleRule);
```

Для объекта `simpleCollator` из примера `a` меньше `b`, который меньше `c`, и так далее. Метод
`simpleCollator.compare` ссылается на эти правила при сравнении строк. Полный синтаксис
построения правила сопоставления более гибкий и сложный, чем в этом простом примере. Полное
описание синтаксиса — в документации API класса
[`RuleBasedCollator`](https://docs.oracle.com/javase/8/docs/api/java/text/RuleBasedCollator.html).

Следующий пример сортирует список испанских слов двумя коллаторами. Программа `RulesDemo`
начинается с определения правил сопоставления для английского и испанского языков. Программа
сортирует испанские слова традиционным образом. При традиционной сортировке буквосочетания `ch`
и `ll` и их заглавные эквиваленты имеют собственные позиции в порядке сортировки. Эти пары
символов сравниваются так, будто они один символ. Например, `ch` сортируется как одна буква,
следуя после `cz`. Обратите внимание, чем различаются правила двух коллаторов:

```java
String englishRules = (
    "< a,A < b,B < c,C < d,D < e,E < f,F " +
    "< g,G < h,H < i,I < j,J < k,K < l,L " +
    "< m,M < n,N < o,O < p,P < q,Q < r,R " +
    "< s,S < t,T < u,U < v,V < w,W < x,X " +
    "< y,Y < z,Z");

String smallnTilde = new String("ñ");    // ñ
String capitalNTilde = new String("Ñ");  // Ñ

String traditionalSpanishRules = (
    "< a,A < b,B < c,C " +
    "< ch, cH, Ch, CH " +
    "< d,D < e,E < f,F " +
    "< g,G < h,H < i,I < j,J < k,K < l,L " +
    "< ll, lL, Ll, LL " +
    "< m,M < n,N " +
    "< " + smallnTilde + "," + capitalNTilde + " " +
    "< o,O < p,P < q,Q < r,R " +
    "< s,S < t,T < u,U < v,V < w,W < x,X " +
    "< y,Y < z,Z");
```

Следующие строки кода создают коллаторы и вызывают процедуру сортировки:

```java
try {
    RuleBasedCollator enCollator = new RuleBasedCollator(englishRules);
    RuleBasedCollator spCollator =
        new RuleBasedCollator(traditionalSpanishRules);

    sortStrings(enCollator, words);
    printStrings(words);
    System.out.println();

    sortStrings(spCollator, words);
    printStrings(words);
} catch (ParseException pe) {
    System.out.println("Parse exception for rules");
}
```

Процедура сортировки `sortStrings` универсальна — она отсортирует любой массив слов по правилам
любого объекта `Collator`:

```java
public static void sortStrings(Collator collator, String[] words) {
    String tmp;
    for (int i = 0; i < words.length; i++) {
        for (int j = i + 1; j < words.length; j++) {
            if (collator.compare(words[i], words[j]) > 0) {
                tmp = words[i];
                words[i] = words[j];
                words[j] = tmp;
            }
        }
    }
}
```

При сортировке по английским правилам массив слов выглядит так:

```
chalina
curioso
llama
luz
```

Сравните предыдущий список со следующим, отсортированным по традиционным испанским правилам
сопоставления:

```
curioso
chalina
luz
llama
```

### Повышение производительности сопоставления

Сортировка длинных списков строк часто занимает много времени. Если ваш алгоритм сортировки
многократно сравнивает строки, ускорить процесс можно с помощью класса `CollationKey`.

Объект [`CollationKey`](https://docs.oracle.com/javase/8/docs/api/java/text/CollationKey.html)
представляет ключ сортировки для заданных `String` и `Collator`. Сравнение двух объектов
`CollationKey` сводится к побитовому сравнению ключей сортировки и выполняется быстрее, чем
сравнение объектов `String` методом `Collator.compare`. Однако создание объектов `CollationKey`
требует времени. Поэтому, если строку нужно сравнить лишь один раз, `Collator.compare` даёт
лучшую производительность.

Программа `KeysDemo` создаёт массив объектов `CollationKey` в методе `main`. Чтобы создать
`CollationKey`, вызывают метод `getCollationKey` на объекте `Collator`. Нельзя сравнивать два
объекта `CollationKey`, если они получены из разных `Collator`. Метод `main`:

```java
static public void main(String[] args) {
    Collator enUSCollator = Collator.getInstance(new Locale("en","US"));
    String [] words = {
        "peach",
        "apricot",
        "grape",
        "lemon"
    };

    CollationKey[] keys = new CollationKey[words.length];

    for (int k = 0; k < keys.length; k ++) {
        keys[k] = enUSCollator.getCollationKey(words[k]);
    }

    sortArray(keys);
    printArray(keys);
}
```

Метод `sortArray` вызывает `CollationKey.compareTo`. Метод `compareTo` возвращает целое число
меньше нуля, равное нулю или больше нуля, если объект `keys[i]` соответственно меньше, равен или
больше объекта `keys[j]`. Обратите внимание, что программа сравнивает объекты `CollationKey`, а
не объекты `String` из исходного массива слов:

```java
public static void sortArray(CollationKey[] keys) {
    CollationKey tmp;

    for (int i = 0; i < keys.length; i++) {
        for (int j = i + 1; j < keys.length; j++) {
            if (keys[i].compareTo(keys[j]) > 0) {
                tmp = keys[i];
                keys[i] = keys[j];
                keys[j] = tmp;
            }
        }
    }
}
```

Программа `KeysDemo` сортирует массив объектов `CollationKey`, но исходной целью была сортировка
массива объектов `String`. Чтобы получить строковое представление каждого `CollationKey`,
программа вызывает `getSourceString` в методе `displayWords`:

```java
static void displayWords(CollationKey[] keys) {
    for (int i = 0; i < keys.length; i++) {
        System.out.println(keys[i].getSourceString());
    }
}
```

Метод `displayWords` печатает следующие строки:

```
apricot
grape
lemon
peach
```

## Unicode

*Unicode* — это отраслевой стандарт вычислительной техники, предназначенный для согласованного и
однозначного кодирования символов, используемых в письменных языках по всему миру. Стандарт
Unicode выражает символ в шестнадцатеричной форме. Например, значение `0x0041` представляет
латинский символ `A`. Изначально стандарт Unicode проектировался с использованием 16 бит для
кодирования символов, поскольку основными машинами тогда были 16-разрядные ПК.

Когда создавалась спецификация языка Java, стандарт Unicode был принят, и примитив `char` был
определён как 16-битный тип данных с символами в шестнадцатеричном диапазоне от `0x0000` до
`0xFFFF`.

Поскольку 16-битная кодировка поддерживает 2^16 (65 536) символов, чего недостаточно для всех
символов мира, стандарт Unicode был расширен до `0x10FFFF`, что даёт поддержку более миллиона
символов. Определение символа в языке Java нельзя было изменить с 16 на 32 бита, не нарушив
работу миллионов Java-приложений. Чтобы исправить определение, разработали схему обработки
символов, которые невозможно закодировать в 16 битах.

Символы со значениями вне 16-битного диапазона, в пределах от `0x10000` до `0x10FFFF`,
называются *дополнительными символами* (supplementary characters) и определяются как пара
значений `char`.

### Терминология

*Символ* (character) — минимальная единица текста, имеющая семантическое значение.

*Набор символов* (character set) — коллекция символов, которая может использоваться несколькими
языками. Например, латинский набор символов используется английским и большинством европейских
языков, тогда как греческий набор символов используется только греческим языком.

*Кодированный набор символов* (coded character set) — набор символов, в котором каждому символу
присвоено уникальное число.

*Кодовая позиция* (code point) — значение, которое может использоваться в кодированном наборе
символов. Кодовая позиция — это 32-битный тип данных `int`, где младшие 21 бит представляют
допустимое значение кодовой позиции, а старшие 11 бит равны 0.

*Кодовая единица* (code unit) Unicode — это 16-битное значение `char`. Например, представьте
`String`, содержащую буквы `"abc"`, за которыми следует символ дезеретского алфавита LONG I,
представленный двумя значениями `char`. Эта строка содержит четыре символа, четыре кодовые
позиции, но пять кодовых единиц.

Чтобы выразить символ в Unicode, к шестнадцатеричному значению добавляют префикс `U+`.
Допустимый диапазон кодовых позиций стандарта Unicode — от `U+0000` до `U+10FFFF` включительно.
Значение кодовой позиции латинского символа `A` — `U+0041`. Символ `€`, обозначающий валюту
евро, имеет кодовую позицию `U+20AC`. Первая буква дезеретского алфавита, LONG I, имеет кодовую
позицию `U+10400`.

В следующей таблице показаны значения кодовых позиций для нескольких символов:

| Символ | Кодовая позиция Unicode |
|--------|-------------------------|
| Латинская A | `U+0041` |
| Латинская острая S (ß) | `U+00DF` |
| Иероглиф «Восток» | `U+6771` |
| Дезеретская LONG I | `U+10400` |

Как описано ранее, символы в диапазоне от `U+10000` до `U+10FFFF` называются дополнительными
символами. Множество символов от `U+0000` до `U+FFFF` иногда называют *базовой многоязычной
плоскостью* (Basic Multilingual Plane, BMP).

### Дополнительные символы как суррогаты

Чтобы поддержать дополнительные символы, не меняя примитивный тип `char` и не вызывая
несовместимости с прежними Java-программами, дополнительные символы определяются парой значений
кодовых позиций, называемых *суррогатами* (surrogates). Первая кодовая позиция — из диапазона
*верхних суррогатов* (high surrogates) от `U+D800` до `U+DBFF`, вторая — из диапазона *нижних
суррогатов* (low surrogates) от `U+DC00` до `U+DFFF`. Например, дезеретский символ LONG I,
`U+10400`, определяется такой парой суррогатных значений: `U+D801` и `U+DC00`.

### API классов Character и String

Класс `Character` инкапсулирует тип данных `char`. В выпуске J2SE 5 в класс `Character` было
добавлено множество методов для поддержки дополнительных символов. Этот API делится на две
категории: методы, преобразующие между `char` и значениями кодовых позиций, и методы, проверяющие
допустимость или отображающие (mapping) кодовые позиции. Полный список — в спецификации класса
[`Character`](https://docs.oracle.com/javase/8/docs/api/java/lang/Character.html).

**Методы преобразования класса `Character`.** Методы `codePointAt` и `codePointBefore включены в
список, поскольку текст обычно встречается в последовательности (например, `String`), и эти
методы можно использовать для извлечения нужной подстроки.

| Метод(ы) | Описание |
|----------|----------|
| `toChars(int codePoint, char[] dst, int dstIndex)`, `toChars(int codePoint)` | Преобразует указанную кодовую позицию Unicode в её представление UTF-16 и помещает в массив `char`. Пример: `Character.toChars(0x10400)` |
| `toCodePoint(char high, char low)` | Преобразует указанную суррогатную пару в значение дополнительной кодовой позиции. |
| `codePointAt(char[] a, int index)`, `codePointAt(char[] a, int index, int limit)`, `codePointAt(CharSequence seq, int index)` | Возвращает кодовую позицию Unicode по указанному индексу. Третий метод принимает `CharSequence`, второй задаёт верхнюю границу индекса. |
| `codePointBefore(char[] a, int index)`, `codePointBefore(char[] a, int index, int start)`, `codePointBefore(CharSequence seq, int index)` | Возвращает кодовую позицию Unicode перед указанным индексом. |
| `charCount(int codePoint)` | Возвращает 1 для символов, представимых одним `char`, и 2 для дополнительных символов, требующих двух `char`. |

**Методы проверки и отображения класса `Character`.** Некоторые прежние методы, использующие
примитив `char` (например, `isLowerCase(char)` и `isDigit(char)`), были заменены методами,
поддерживающими дополнительные символы (например, `isLowerCase(int)` и `isDigit(int)`). Прежние
методы поддерживаются, но не работают с дополнительными символами. Для глобального приложения
рекомендуется использовать новые формы этих методов. По соображениям производительности
большинство методов, принимающих кодовую позицию, не проверяют её допустимость; для этого
используйте метод `isValidCodePoint`.

| Метод(ы) | Описание |
|----------|----------|
| `isValidCodePoint(int codePoint)` | `true`, если кодовая позиция в диапазоне от `0x0000` до `0x10FFFF` включительно. |
| `isSupplementaryCodePoint(int codePoint)` | `true`, если кодовая позиция в диапазоне от `0x10000` до `0x10FFFF` включительно. |
| `isHighSurrogate(char)` | `true`, если `char` в диапазоне верхних суррогатов от `\uD800` до `\uDBFF` включительно. |
| `isLowSurrogate(char)` | `true`, если `char` в диапазоне нижних суррогатов от `\uDC00` до `\uDFFF` включительно. |
| `isSurrogatePair(char high, char low)` | `true`, если указанные верхнее и нижнее суррогатные значения образуют допустимую суррогатную пару. |
| `codePointCount(CharSequence, int, int)`, `codePointCount(char[], int, int)` | Возвращает число кодовых позиций Unicode в `CharSequence` или массиве `char`. |
| `isLowerCase(int)`, `isUpperCase(int)` | `true`, если кодовая позиция — строчный или прописной символ. |
| `isDefined(int)` | `true`, если кодовая позиция определена в стандарте Unicode. |
| `isJavaIdentifierStart(char)`, `isJavaIdentifierStart(int)` | `true`, если символ или кодовая позиция допустимы как первый символ Java-идентификатора. |
| `isLetter(int)`, `isDigit(int)`, `isLetterOrDigit(int)` | `true`, если кодовая позиция — буква, цифра, либо буква или цифра. |
| `getDirectionality(int)` | Возвращает свойство направленности (directionality) Unicode для кодовой позиции. |
| `Character.UnicodeBlock.of(int codePoint)` | Возвращает объект блока Unicode, содержащего кодовую позицию, или `null`, если позиция не входит в определённый блок. |

**Методы классов строк.** Классы `String`, `StringBuffer` и `StringBuilder` также имеют
конструкторы и методы для работы с дополнительными символами, в их числе:

| Конструктор или метод | Описание |
|-----------------------|----------|
| `String(int[] codePoints, int offset, int count)` | Создаёт новый `String` из подмассива массива кодовых позиций Unicode. |
| `String/StringBuffer/StringBuilder.codePointAt(int index)` | Возвращает кодовую позицию Unicode по указанному индексу. |
| `String/StringBuffer/StringBuilder.codePointBefore(int index)` | Возвращает кодовую позицию Unicode перед указанным индексом. |
| `String/StringBuffer/StringBuilder.codePointCount(int beginIndex, int endIndex)` | Возвращает число кодовых позиций Unicode в указанном диапазоне. |
| `StringBuffer/StringBuilder.appendCodePoint(int codePoint)` | Добавляет строковое представление указанной кодовой позиции в последовательность. |
| `String/StringBuffer/StringBuilder.offsetByCodePoints(int index, int codePointOffset)` | Возвращает индекс, смещённый от заданного на указанное число кодовых позиций. |

### Примеры использования

Несколько распространённых сценариев работы с кодовыми позициями.

**Создание `String` из кодовой позиции:**

```java
String newString(int codePoint) {
    return new String(Character.toChars(codePoint));
}
```

**Создание `String` из кодовой позиции — оптимизация для BMP-символов.** Метод
`Character.toChars` создаёт временный массив, который используется один раз и затем
отбрасывается. Если это отрицательно влияет на производительность, используйте подход,
оптимизированный для BMP-символов (представимых одним `char`); здесь `toChars` вызывается только
для дополнительных символов:

```java
String newString(int codePoint) {
    if (Character.charCount(codePoint) == 1) {
        return String.valueOf(codePoint);
    } else {
        return new String(Character.toChars(codePoint));
    }
}
```

**Массовое создание объектов `String`.** Эта версия переиспользует массив, используемый методом
`toChars`, и оптимизирована для BMP-символов:

```java
String[] newStrings(int[] codePoints) {
    String[] result = new String[codePoints.length];
    char[] codeUnits = new char[2];
    for (int i = 0; i < codePoints.length; i++) {
        int count = Character.toChars(codePoints[i], codeUnits, 0);
        result[i] = new String(codeUnits, 0, count);
    }
    return result;
}
```

**Формирование сообщений.** API форматирования поддерживает дополнительные символы. Следующий
способ прост и избегает конкатенации, которая усложняет локализацию (не все языки вставляют
числовые значения в строку в том же порядке, что и английский):

```java
// рекомендуется
System.out.printf("Character %c is invalid.%n", codePoint);
```

```java
// не рекомендуется
System.out.println("Character " + String.valueOf(char) + " is invalid.");
```

### Замечания по проектированию

Чтобы код работал безупречно для любого языка и любой письменности, держите в уме несколько
моментов:

| Рекомендация | Причина |
|--------------|---------|
| Избегайте методов, использующих тип `char`. | Код, использующий примитив `char`, не работает с дополнительными символами. Для методов с параметром `char` по возможности используйте соответствующий метод с `int`, например `Character.isDigit(int)` вместо `Character.isDigit(char)`. |
| Используйте `isValidCodePoint` для проверки значений кодовых позиций. | Кодовая позиция определена как `int`, что допускает значения вне допустимого диапазона от `0x0000` до `0x10FFFF`. По соображениям производительности методы, принимающие кодовую позицию, не проверяют её допустимость — для этого используйте `isValidCodePoint`. |
| Используйте `codePointCount` для подсчёта символов. | Метод `String.length()` возвращает число кодовых единиц (16-битных `char`). При наличии дополнительных символов счёт может вводить в заблуждение, поскольку не отражает истинное число кодовых позиций. Для точного подсчёта используйте `codePointCount`. |
| Используйте `String.toUpperCase`/`String.toLowerCase`, а не `Character.toUpperCase(int)`/`Character.toLowerCase(int)`. | Некоторые символы нельзя преобразовать «один к одному». Например, строчная немецкая `ß` при переводе в верхний регистр становится двумя символами `SS`, а малая греческая сигма различается в зависимости от позиции в строке. Методы класса `Character` не справляются с такими случаями, а методы класса `String` — справляются. |
| Будьте осторожны при удалении символов. | При вызове `StringBuilder.deleteCharAt(int index)` или `StringBuffer.deleteCharAt(int index)`, когда индекс указывает на дополнительный символ, удаляется только первая половина (первый `char`). Сначала вызовите `Character.charCount`, чтобы определить, удалять один или два `char`. |
| Будьте осторожны при обращении (reverse) последовательности символов. | При вызове `StringBuffer.reverse()` или `StringBuilder.reverse()` на тексте с дополнительными символами верхние и нижние суррогатные пары меняются местами, что даёт неверные и, возможно, недопустимые суррогатные пары. |

### Дополнительная информация

- [Supplementary Characters in the Java Platform](http://www.oracle.com/technetwork/articles/javase/supplementary-142654.html)
- [Unicode Consortium](http://unicode.org/)
- [Glossary of Unicode Terms](http://unicode.org/glossary/)

## Определение границ текста

Приложениям, работающим с текстом, нужно находить границы внутри текста. Например, рассмотрите
типичные функции текстового процессора: выделение символа, вырезание слова, перемещение курсора
к следующему предложению, перенос слова на границе строки. Чтобы выполнить каждую из этих
функций, текстовый процессор должен уметь обнаруживать логические границы в тексте. К счастью,
вам не нужно писать собственные процедуры анализа границ — можно воспользоваться методами класса
[`BreakIterator`](https://docs.oracle.com/javase/8/docs/api/java/text/BreakIterator.html).

### О классе BreakIterator

Класс `BreakIterator` чувствителен к локали, поскольку границы текста зависят от языка. Например,
синтаксические правила переноса строк неодинаковы для всех языков. Чтобы определить, какие локали
поддерживает `BreakIterator`, вызовите метод `getAvailableLocales`:

```java
Locale[] locales = BreakIterator.getAvailableLocales();
```

С помощью `BreakIterator` можно анализировать четыре вида границ: символьные, словные,
предложений и потенциальных переносов строк. При создании экземпляра `BreakIterator` вызывают
соответствующий фабричный метод:

- `getCharacterInstance`
- `getWordInstance`
- `getSentenceInstance`
- `getLineInstance`

Каждый экземпляр `BreakIterator` обнаруживает только один тип границ. Если, например, вам нужны
и символьные, и словные границы, создайте два отдельных экземпляра.

У `BreakIterator` есть воображаемый курсор, указывающий на текущую границу в строке текста.
Перемещать курсор по тексту можно методами `previous` и `next`. Например, если вы создали
`BreakIterator` через `getWordInstance`, курсор перемещается к следующей словной границе каждый
раз при вызове `next`. Методы перемещения курсора возвращают целое число — позицию границы.
Это позиция — индекс символа в строке, следующего за границей. Как и индексы строк, границы
отсчитываются от нуля. Первая граница — на 0, последняя — длина строки.

`BreakIterator` следует использовать только с текстом на естественном языке. Для разбиения
(токенизации) языка программирования используйте класс `StreamTokenizer`. Примеры кода ниже
взяты из исходного файла `BreakIteratorDemo.java`.

### Символьные границы

Символьные границы нужно находить, если приложение позволяет выделять отдельные символы или
перемещать курсор по тексту посимвольно. Чтобы создать `BreakIterator`, находящий символьные
границы, вызовите `getCharacterInstance`:

```java
BreakIterator characterIterator =
    BreakIterator.getCharacterInstance(currentLocale);
```

Этот тип `BreakIterator` обнаруживает границы между *пользовательскими* символами, а не только
символами Unicode. Пользовательский символ может состоять более чем из одного символа Unicode.
Например, символ `ü` можно составить, комбинируя символы Unicode `u` (u) и `¨` (¨).
Впрочем, это не лучший пример, поскольку `ü` может также представляться одним символом `ü`.
Возьмём более реалистичный пример из арабского языка.

Арабское слово «дом» содержит три пользовательских символа, но состоит из шести символов Unicode:

```java
String house = "ب" + "َ" + "ي" + "ْ" + "ٺ" + "ُ";
```

Символы Unicode на позициях 1, 3 и 5 в строке `house` — диакритические знаки. Арабский язык
требует диакритики, поскольку она может менять значения слов. Диакритические знаки в примере —
непробельные (nonspacing) символы, так как располагаются над базовыми символами. В арабском
текстовом процессоре нельзя перемещать курсор по экрану по одному разу на каждый символ Unicode.
Вместо этого нужно перемещать его по одному разу на каждый пользовательский символ, который может
состоять из нескольких символов Unicode. Поэтому для сканирования пользовательских символов в
строке необходим `BreakIterator`.

Программа `BreakIteratorDemo` создаёт `BreakIterator` для сканирования арабских символов и
передаёт его вместе со строкой в метод `listPositions`:

```java
BreakIterator arCharIterator = BreakIterator.getCharacterInstance(
                                   new Locale ("ar","SA"));
listPositions (house, arCharIterator);
```

Метод `listPositions` использует `BreakIterator` для нахождения символьных границ. Текст
назначается итератору методом `setText`. Программа получает первую границу методом `first`, затем
вызывает `next`, пока не вернётся константа `BreakIterator.DONE`:

```java
static void listPositions(String target, BreakIterator iterator) {

    iterator.setText(target);
    int boundary = iterator.first();

    while (boundary != BreakIterator.DONE) {
        System.out.println (boundary);
        boundary = iterator.next();
    }
}
```

Метод `listPositions` печатает следующие позиции границ пользовательских символов в строке
`house`. Обратите внимание, что позиции диакритик (1, 3, 5) не перечислены:

```
0
2
4
6
```

### Словные границы

Чтобы создать `BreakIterator`, обнаруживающий словные границы, вызовите `getWordInstance`:

```java
BreakIterator wordIterator =
    BreakIterator.getWordInstance(currentLocale);
```

Такой `BreakIterator` нужен, когда приложению необходимо выполнять операции над отдельными
словами — выделение, вырезание, вставку, копирование. Или приложение ищет слова и должно
отличать целые слова от простых строк. Анализируя словные границы, `BreakIterator` различает
слова и символы, не являющиеся частью слов (пробелы, табуляции, знаки препинания, большинство
символов) — у таких символов словные границы с обеих сторон.

Пример из программы `BreakIteratorDemo` отмечает словные границы в тексте. Программа создаёт
`BreakIterator` и вызывает метод `markBoundaries`:

```java
Locale currentLocale = new Locale ("en","US");

BreakIterator wordIterator =
    BreakIterator.getWordInstance(currentLocale);

String someText = "She stopped. " +
    "She said, \"Hello there,\" and then went " +
    "on.";

markBoundaries(someText, wordIterator);
```

Метод `markBoundaries` отмечает границы, печатая знаки «^» под целевой строкой. Обратите внимание
на цикл `while`, где `markBoundaries` сканирует строку, вызывая `next`:

```java
static void markBoundaries(String target, BreakIterator iterator) {

    StringBuffer markers = new StringBuffer();
    markers.setLength(target.length() + 1);
    for (int k = 0; k < markers.length(); k++) {
        markers.setCharAt(k,' ');
    }

    iterator.setText(target);
    int boundary = iterator.first();

    while (boundary != BreakIterator.DONE) {
        markers.setCharAt(boundary,'^');
        boundary = iterator.next();
    }

    System.out.println(target);
    System.out.println(markers);
}
```

Вывод метода `markBoundaries`. Обратите внимание, где «^» располагаются относительно знаков
препинания и пробелов:

```
She stopped.  She said, "Hello there," and then
^  ^^      ^^ ^  ^^   ^^^^    ^^    ^^^^  ^^   ^

went on.
^   ^^ ^^
```

Класс `BreakIterator` упрощает выбор слов из текста — вам не нужно писать собственные процедуры
обработки правил пунктуации различных языков. Метод `extractWords` извлекает и печатает слова
заданной строки. Он использует `Character.isLetterOrDigit`, чтобы не печатать «слова», содержащие
пробелы:

```java
static void extractWords(String target, BreakIterator wordIterator) {

    wordIterator.setText(target);
    int start = wordIterator.first();
    int end = wordIterator.next();

    while (end != BreakIterator.DONE) {
        String word = target.substring(start,end);
        if (Character.isLetterOrDigit(word.charAt(0))) {
            System.out.println(word);
        }
        start = end;
        end = wordIterator.next();
    }
}
```

Метод `extractWords` печатает следующий список слов:

```
She
stopped
She
said
Hello
there
and
then
went
on
```

### Границы предложений

С помощью `BreakIterator` можно определять границы предложений. Создаётся он методом
`getSentenceInstance`:

```java
BreakIterator sentenceIterator =
    BreakIterator.getSentenceInstance(currentLocale);
```

Чтобы показать границы предложений, программа использует метод `markBoundaries` (см. раздел
«Словные границы»), печатающий знаки «^» под строкой. Несколько примеров:

```
She stopped.  She said, "Hello there," and then went on.
^             ^                                         ^

He's vanished!  What will we do?  It's up to us.
^               ^                 ^             ^

Please add 1.5 liters to the tank.
^                                 ^
```

Определение границ предложений может быть проблематичным из-за неоднозначного использования
завершающих знаков предложения во многих письменных языках (обратите внимание на пример с `1.5`,
где точка не завершает предложение).

### Границы строк

Приложениям, форматирующим текст или выполняющим перенос строк, нужно находить потенциальные
переносы. Их можно найти с помощью `BreakIterator`, созданного методом `getLineInstance`:

```java
BreakIterator lineIterator =
    BreakIterator.getLineInstance(currentLocale);
```

Этот `BreakIterator` определяет позиции в строке, где текст можно перенести на следующую строку.
Обнаруженные позиции — *потенциальные* переносы; фактические переносы на экране могут отличаться.

По правилам `BreakIterator`, граница строки возникает после завершения последовательности
пробельных символов (пробел, табуляция, новая строка). В следующем примере перенос возможен на
любой из обнаруженных границ:

```
She stopped.  She said, "Hello there," and then went on.
^   ^         ^   ^     ^      ^     ^ ^   ^    ^    ^  ^
```

Потенциальные переносы строк также возникают сразу после дефиса:

```
There are twenty-four hours in a day.
^     ^   ^      ^    ^     ^  ^ ^   ^
```

Следующий пример разбивает длинную строку текста на строки фиксированной длины методом
`formatLines`, который использует `BreakIterator` для нахождения потенциальных переносов. Метод
короткий, простой и, благодаря `BreakIterator`, локале-независимый:

```java
static void formatLines(
    String target, int maxLength,
    Locale currentLocale) {

    BreakIterator boundary = BreakIterator.
        getLineInstance(currentLocale);
    boundary.setText(target);
    int start = boundary.first();
    int end = boundary.next();
    int lineLength = 0;

    while (end != BreakIterator.DONE) {
        String word = target.substring(start,end);
        lineLength = lineLength + word.length();
        if (lineLength >= maxLength) {
            System.out.println();
            lineLength = word.length();
        }
        System.out.print(word);
        start = end;
        end = boundary.next();
    }
}
```

Программа `BreakIteratorDemo` вызывает `formatLines`, передавая `maxLength` равным 30. Вывод:

```
She said, "Hello there," and
then went on down the
street. When she stopped to
look at the fur coats in a
shop window, her dog
growled. "Sorry Jake," she
said. "I didn't know you
would take it personally."
```

## Преобразование латинских цифр в другие цифры Unicode

По умолчанию, когда текст содержит числовые значения, они отображаются латинскими (европейскими)
цифрами. Когда предпочтительны другие начертания цифр Unicode, используйте класс
[`java.awt.font.NumericShaper`](https://docs.oracle.com/javase/8/docs/api/java/awt/font/NumericShaper.html).
API `NumericShaper` позволяет отображать числовое значение, внутренне представленное как
ASCII-значение, в любом начертании цифр Unicode.

Следующий фрагмент из примера `ArabicDigits` показывает, как с помощью экземпляра
`NumericShaper` преобразовать латинские цифры в арабские. Строка, определяющая действие
преобразования начертания, выделена в комментарии:

```java
ArabicDigitsPanel(String fontname) {
    HashMap map = new HashMap();
    Font font = new Font(fontname, Font.PLAIN, 60);
    map.put(TextAttribute.FONT, font);
    // вот эта строка задаёт преобразование начертания цифр:
    map.put(TextAttribute.NUMERIC_SHAPING,
        NumericShaper.getShaper(NumericShaper.ARABIC));

    FontRenderContext frc = new FontRenderContext(null, false, false);
    layout = new TextLayout(text, map, frc);
}

// ...

public void paint(Graphics g) {
    Graphics2D g2d = (Graphics2D)g;
    layout.draw(g2d, 10, 50);
}
```

Экземпляр `NumericShaper` для арабских цифр помещается в `HashMap` по ключу-атрибуту
`TextAttribute.NUMERIC_SHAPING`. Хеш-карта передаётся в экземпляр `TextLayout`. После отрисовки
текста в методе `paint` цифры отображаются в нужной письменности — в данном примере латинские
цифры от 0 до 9 рисуются как арабские.

Предыдущий пример использует константу `NumericShaper.ARABIC`, но класс `NumericShaper`
предоставляет константы для многих языков. Эти константы определены как битовые маски и называются
*константами на основе битовых масок*.

### Константы-диапазоны на основе перечисления (enum)

Альтернативный способ задать конкретный набор цифр — использовать перечисляемый тип
[`NumericShaper.Range`](https://docs.oracle.com/javase/8/docs/api/java/awt/font/NumericShaper.Range.html),
введённый в выпуске Java SE 7. Хотя константы определены разными механизмами, битовая маска
`NumericShaper.ARABIC` функционально эквивалентна enum-у `NumericShaper.Range.ARABIC`, и для
каждого типа константы есть соответствующий метод `getShaper`:

- `getShaper(int singleRange)`
- `getShaper(NumericShaper.Range singleRange)`

Пример `ArabicDigitsEnum` идентичен примеру `ArabicDigits`, но использует enum
`NumericShaper.Range` для указания письменности:

```java
ArabicDigitsEnumPanel(String fontname) {
    HashMap map = new HashMap();
    Font font = new Font(fontname, Font.PLAIN, 60);
    map.put(TextAttribute.FONT, font);
    map.put(TextAttribute.NUMERIC_SHAPING,
        NumericShaper.getShaper(NumericShaper.Range.ARABIC));
    FontRenderContext frc = new FontRenderContext(null, false, false);
    layout = new TextLayout(text, map, frc);
}
```

Оба метода `getShaper` принимают параметр `singleRange`. С любым типом констант можно задать
диапазон специфичных для письменности цифр. Константы-битовые маски можно комбинировать
оператором `OR`, а из enum-ов можно создать множество `NumericShaper.Range`. Определение
диапазона каждым из типов констант:

```java
NumericShaper.MONGOLIAN | NumericShaper.THAI |
NumericShaper.TIBETAN
```

```java
EnumSet.of(
    NumericShaper.Range.MONGOLIAN,
    NumericShaper.Range.THAI,
    NumericShaper.Range.TIBETAN)
```

Запросить у объекта `NumericShaper`, какие диапазоны он поддерживает, можно методом `getRanges`
(для шейперов на основе битовых масок) или `getRangeSet` (для enum-шейперов).

**Замечание.** Можно использовать как традиционные константы-битовые маски, так и enum-константы
`Range`. Соображения при выборе:

- API `Range` требует JDK 7 или новее.
- API `Range` охватывает больше диапазонов Unicode, чем API на битовых масках.
- API на битовых масках немного быстрее, чем API `Range`.

### Отрисовка цифр в зависимости от языкового контекста

Иногда цифры должны отображаться в соответствии с языковым контекстом. Например, если
предшествующий цифрам текст использует тайскую письменность, предпочтительны тайские цифры; если
текст отображается на тибетском — тибетские. Этого можно добиться одним из методов
`getContextualShaper`:

- `getContextualShaper(int ranges)`
- `getContextualShaper(int ranges, int defaultContext)`
- `getContextualShaper(Set<NumericShaper.Range> ranges)`
- `getContextualShaper(Set<NumericShaper.Range> ranges, NumericShaper.Range defaultContext)`

Первые два метода используют константы-битовые маски, последние два — enum-константы. Методы с
параметром `defaultContext` позволяют задать начальный шейпер, применяемый, когда числовые
значения отображаются перед текстом. Если контекст по умолчанию не задан, ведущие цифры
отображаются латинскими начертаниями.

Пример `ShapedDigits` показывает работу шейперов. Отображаются пять текстовых раскладок:

1. Первая — без шейпера; все цифры латинские.
2. Вторая — все цифры арабские, независимо от языкового контекста.
3. Третья — контекстный шейпер с арабскими цифрами; контекст по умолчанию — арабский.
4. Четвёртая — контекстный шейпер с арабскими цифрами, но без контекста по умолчанию.
5. Пятая — контекстный шейпер с битовой маской `ALL_RANGES`, без контекста по умолчанию.

Определение соответствующих шейперов:

```java
// 1. Шейпер не используется.
// 2.
NumericShaper arabic = NumericShaper.getShaper(NumericShaper.ARABIC);
// 3.
NumericShaper contextualArabic =
    NumericShaper.getContextualShaper(NumericShaper.ARABIC, NumericShaper.ARABIC);
// 4.
NumericShaper contextualArabicASCII =
    NumericShaper.getContextualShaper(NumericShaper.ARABIC);
// 5.
NumericShaper contextualAll =
    NumericShaper.getContextualShaper(NumericShaper.ALL_RANGES);
```

## Преобразование не-Unicode текста

В языке Java значения `char` представляют символы Unicode. Различные компьютерные системы по
всему миру хранят текст в разнообразных схемах кодирования. Поскольку ваша программа ожидает
символы в Unicode, текстовые данные, получаемые от системы, должны преобразовываться в Unicode
и обратно.

Немногие текстовые редакторы поддерживают ввод текста Unicode. Чтобы указать символы Unicode,
не представимые в ASCII (например, `ö`), используют управляющую последовательность `\uXXXX`, где
каждый `X` — шестнадцатеричная цифра:

```java
String str = "ö";
char c = 'ö';
Character letter = new Character('ö');
```

Данные в текстовых файлах автоматически преобразуются в Unicode, когда их кодировка совпадает с
кодировкой файлов по умолчанию (default file encoding) виртуальной машины Java. Кодировку по
умолчанию можно узнать, создав `OutputStreamWriter` с ней и запросив её каноническое имя:

```java
OutputStreamWriter out = new OutputStreamWriter(new ByteArrayOutputStream());
System.out.println(out.getEncoding());
```

Если кодировка по умолчанию отличается от кодировки обрабатываемых данных, преобразование нужно
выполнить самостоятельно — например, при обработке текста из другой страны или с другой платформы.
Перед использованием соответствующих API убедитесь, что нужная кодировка поддерживается (список
поддерживаемых кодировок не входит в спецификацию языка и может зависеть от платформы; см.
документ [Supported Encodings](https://docs.oracle.com/javase/8/docs/technotes/guides/intl/encoding.doc.html)).
Есть два приёма преобразования: между не-Unicode массивами байт и объектами `String` и между
потоками символов Unicode и байтовыми потоками не-Unicode текста.

### Байтовые кодировки и строки

Если массив байт содержит не-Unicode текст, его можно преобразовать в Unicode одним из
конструкторов `String`. И наоборот, объект `String` можно преобразовать в массив байт
не-Unicode символов методом `String.getBytes`. При вызове любого из методов идентификатор
кодировки указывается одним из параметров.

Следующий пример преобразует символы между UTF-8 и Unicode. UTF-8 — формат передачи Unicode,
безопасный для файловых систем UNIX. Программа `StringConverter` начинается с создания `String`
с символами Unicode:

```java
String original = new String("A" + "ê" + "ñ" + "ü" + "C");
```

При печати `String` по имени `original` выглядит так:

```
AêñüC
```

Чтобы преобразовать объект `String` в UTF-8, вызывают `getBytes`, указывая идентификатор
кодировки. Метод `getBytes` возвращает массив байт в формате UTF-8. Чтобы создать `String` из
массива не-Unicode байт, вызывают конструктор `String` с параметром кодировки. Код заключён в
блок `try` на случай, если кодировка не поддерживается:

```java
try {
    byte[] utf8Bytes = original.getBytes("UTF8");
    byte[] defaultBytes = original.getBytes();

    String roundTrip = new String(utf8Bytes, "UTF8");
    System.out.println("roundTrip = " + roundTrip);
    System.out.println();
    printBytes(utf8Bytes, "utf8Bytes");
    System.out.println();
    printBytes(defaultBytes, "defaultBytes");
}
catch (UnsupportedEncodingException e) {
    e.printStackTrace();
}
```

Программа печатает значения массивов `utf8Bytes` и `defaultBytes`, демонстрируя важный момент:
длина преобразованного текста может не совпадать с длиной исходного. Некоторые символы Unicode
переводятся в один байт, другие — в пары или тройки байт. Метод `printBytes` выводит массивы
байт, вызывая `byteToHex` (определён в `UnicodeFormatter.java`):

```java
public static void printBytes(byte[] array, String name) {
    for (int k = 0; k < array.length; k++) {
        System.out.println(name + "[" + k + "] = " + "0x" +
            UnicodeFormatter.byteToHex(array[k]));
    }
}
```

Вывод `printBytes`. Обратите внимание, что только первый и последний байты (символы `A` и `C`)
совпадают в обоих массивах:

```
utf8Bytes[0] = 0x41
utf8Bytes[1] = 0xc3
utf8Bytes[2] = 0xaa
utf8Bytes[3] = 0xc3
utf8Bytes[4] = 0xb1
utf8Bytes[5] = 0xc3
utf8Bytes[6] = 0xbc
utf8Bytes[7] = 0x43
defaultBytes[0] = 0x41
defaultBytes[1] = 0xea
defaultBytes[2] = 0xf1
defaultBytes[3] = 0xfc
defaultBytes[4] = 0x43
```

### Потоки символов и байт

Пакет `java.io` предоставляет классы для преобразования между потоками символов Unicode и
байтовыми потоками не-Unicode текста. Класс
[`InputStreamReader`](https://docs.oracle.com/javase/8/docs/api/java/io/InputStreamReader.html)
преобразует байтовые потоки в потоки символов, а
[`OutputStreamWriter`](https://docs.oracle.com/javase/8/docs/api/java/io/OutputStreamWriter.html) —
потоки символов в байтовые.

При создании `InputStreamReader` и `OutputStreamWriter` указывают байтовую кодировку для
преобразования. Например, чтобы перевести текстовый файл в кодировке UTF-8 в Unicode, создают
`InputStreamReader` так:

```java
FileInputStream fis = new FileInputStream("test.txt");
InputStreamReader isr = new InputStreamReader(fis, "UTF8");
```

Если опустить идентификатор кодировки, `InputStreamReader` и `OutputStreamWriter` опираются на
кодировку по умолчанию. Узнать используемую кодировку можно методом `getEncoding`:

```java
InputStreamReader defaultReader = new InputStreamReader(fis);
String defaultEncoding = defaultReader.getEncoding();
```

Программа `StreamConverter` преобразует последовательность символов Unicode из `String` в
`FileOutputStream` байт, закодированных в UTF-8. Метод преобразования называется `writeOutput`:

```java
static void writeOutput(String str) {
    try {
        FileOutputStream fos = new FileOutputStream("test.txt");
        Writer out = new OutputStreamWriter(fos, "UTF8");
        out.write(str);
        out.close();
    }
    catch (IOException e) {
        e.printStackTrace();
    }
}
```

Метод `readInput` читает байты UTF-8 из созданного файла. Объект `InputStreamReader`
преобразует байты из UTF-8 в Unicode и возвращает результат в `String`:

```java
static String readInput() {
    StringBuffer buffer = new StringBuffer();
    try {
        FileInputStream fis = new FileInputStream("test.txt");
        InputStreamReader isr = new InputStreamReader(fis, "UTF8");
        Reader in = new BufferedReader(isr);
        int ch;
        while ((ch = in.read()) > -1) {
            buffer.append((char)ch);
        }
        in.close();
        return buffer.toString();
    }
    catch (IOException e) {
        e.printStackTrace();
        return null;
    }
}
```

Метод `main` программы `StreamConverter` вызывает `writeOutput`, чтобы создать файл байт UTF-8,
а затем `readInput`, чтобы прочитать тот же файл, преобразовав байты обратно в Unicode:

```java
public static void main(String[] args) {
    String jaString = new String("日本語文字列");
    writeOutput(jaString);
    String inputString = readInput();
    String displayString = jaString + " " + inputString;
    new ShowString(displayString, "Conversion Demo");
}
```

Исходная строка (`jaString`) должна быть идентична вновь созданной (`inputString`). Чтобы
показать, что строки совпадают, программа конкатенирует их и отображает объектом `ShowString`,
который выводит строку методом `Graphics.drawString`.

## Нормализация текста

*Нормализация* (normalization) — процесс, посредством которого можно выполнять определённые
преобразования текста, делая его сопоставимым (reconcilable) там, где он не был сопоставим ранее.
Например, при поиске или сортировке текста его нужно нормализовать, чтобы учесть кодовые позиции,
которые должны представляться как один и тот же текст. Нормализация обрабатывает такие
преобразования, как символы с диакритическими знаками, изменение регистра, разложение лигатур,
преобразование полуширинных символов в полноширинные.

В соответствии с [Unicode Standard Annex #15](http://www.unicode.org/reports/tr15/) API
`Normalizer` поддерживает все четыре формы нормализации текста Unicode, определённые в
[`java.text.Normalizer.Form`](https://docs.oracle.com/javase/8/docs/api/java/text/Normalizer.Form.html):

- **NFD** (Normalization Form D): каноническая декомпозиция (Canonical Decomposition).
- **NFC** (Normalization Form C): каноническая декомпозиция, за которой следует каноническая
  композиция (Canonical Decomposition, followed by Canonical Composition).
- **NFKD** (Normalization Form KD): декомпозиция совместимости (Compatibility Decomposition).
- **NFKC** (Normalization Form KC): декомпозиция совместимости, за которой следует каноническая
  композиция (Compatibility Decomposition, followed by Canonical Composition).

Например, для слова «schön» результаты нормализации таковы:

| Исходное | NFC | NFD | NFKC | NFKD |
|----------|-----|-----|------|------|
| `"schön"` | `"schön"` | `"schön"` | `"schön"` | `"schön"` |

Исходное слово остаётся неизменным в NFC и NFKC. Это связано с тем, что в NFD и NFKD составные
(композитные) символы отображаются на их канонические декомпозиции, а в NFC и NFKC
последовательности комбинирующих символов отображаются на композиты, если это возможно. Для
диерезиса (¨) композита нет, поэтому в NFC и NFKC он остаётся декомпозированным.

Чтобы убедиться, что текст действительно требует нормализации, используйте метод `isNormalized`,
проверяющий, нормализована ли заданная последовательность значений `char`:

```java
Normalizer.isNormalized(target_chars, Normalizer.Form.NFD);
```

Чтобы преобразовать текст в каноническую декомпозированную форму, используйте метод `normalize`:

```java
normalized_string = Normalizer.normalize(target_chars, Normalizer.Form.NFD);
```

Метод `normalize` автоматически переупорядочивает акценты (диакритику) в правильном каноническом
порядке, избавляя от необходимости вручную переставлять акценты. Полный пример — в файле
`NormSample.java`.

## Работа с двунаправленным текстом с помощью класса JTextComponent

Этот раздел рассматривает работу с двунаправленным текстом с помощью класса
[`JTextComponent`](https://docs.oracle.com/javase/8/docs/api/javax/swing/text/JTextComponent.html).
*Двунаправленный* (bidirectional) текст — это текст, содержащий фрагменты, идущие в двух
направлениях: слева направо и справа налево. Пример — арабский текст (идёт справа налево) с
числами (идут слева направо). Отображать двунаправленный текст и управлять им сложнее, однако
`JTextComponent` берёт эти задачи на себя. Рассматриваются темы: определение направленности,
отображение и перемещение каретки, проверка попадания (hit testing), подсветка выделений и
установка ориентации компонента.

### Определение направленности двунаправленного текста

Пример `BidiTextComponentDemo.java`, основанный на `TextComponentDemo.java`, отображает
двунаправленный текст в объекте
[`JTextPane`](https://docs.oracle.com/javase/8/docs/api/javax/swing/JTextPane.html). В
большинстве случаев платформа Java может сама определить направленность двунаправленного текста
Unicode.

**Явное указание направления текстового потока.** Можно указать направление потока (run
direction) объекта
[`Document`](https://docs.oracle.com/javase/8/docs/api/javax/swing/text/Document.html) объекта
`JTextComponent`. Например, следующая инструкция задаёт направление текста в `JTextPane` справа
налево:

```java
textPane.getDocument().putProperty(
    TextAttribute.RUN_DIRECTION,
    TextAttribute.RUN_DIRECTION_RTL);
```

Либо можно задать ориентацию компонента на основе локали. Следующие инструкции задают ориентацию
объекта `textPane` на основе локали `ar-SA`:

```java
Locale arabicSaudiArabia =
    new Locale.Builder().setLanguage("ar").setRegion("SA").build();

textPane.setComponentOrientation(
    ComponentOrientation.getOrientation(arabicSaudiArabia));
```

Поскольку направление арабского языка — справа налево, направление потока текста в `textPane`
также будет справа налево.

### Отображение и перемещение каретки

В редактируемом тексте *каретка* (caret) графически представляет текущую точку вставки — позицию,
куда будут вставлены новые символы. В примере `BidiTextComponentDemo.java` каретка содержит
небольшой треугольник, указывающий в направлении, где будет отображён вставленный символ.

По умолчанию `JTextComponent` создаёт карту клавиш (тип
[`Keymap`](https://docs.oracle.com/javase/8/docs/api/javax/swing/text/Keymap.html)), общую для
всех экземпляров `JTextComponent`. Карта клавиш позволяет привязывать нажатия клавиш к действиям.
Карта по умолчанию (для компонентов, поддерживающих перемещение каретки) включает привязку
перемещения каретки вперёд и назад к клавишам стрелок влево и вправо, что обеспечивает
перемещение каретки по двунаправленному тексту.

### Проверка попадания (hit testing)

Часто позицию в пространстве устройства нужно преобразовать в смещение в тексте (text offset).
Например, когда пользователь щёлкает мышью по выделяемому тексту, позиция мыши преобразуется в
смещение и используется как один конец диапазона выделения. Логически это операция, обратная
позиционированию каретки.

К экземпляру `JTextComponent` можно присоединить слушатель каретки (caret listener), который
позволяет обрабатывать события каретки, возникающие при её перемещении или изменении выделения.
Слушатель присоединяется методом `addCaretListener`.

### Подсветка выделений

Выделенный диапазон символов графически представлен областью подсветки — областью, где глифы
отображаются инверсным видео или на другом цвете фона. Объекты `JTextComponent` реализуют
*логическую* подсветку: выделенные символы всегда непрерывны в текстовой модели, а область
подсветки может быть прерывистой.

### Установка ориентации компонента

Менеджеры компоновки (layout managers) Swing понимают, как локаль влияет на интерфейс; не нужно
создавать новую компоновку для каждой локали. Например, в локали, где текст идёт справа налево,
менеджер компоновки расположит компоненты в той же ориентации.

Пример `InternationalizedMortgageCalculator.java` локализован для английского (США),
английского (Великобритания), французского (Франция), французского (Канада) и арабского
(Саудовская Аравия). Он вызывает методы `applyComponentOrientation` и `getOrientation`, чтобы
задать направление компонентов в зависимости от локали:

```java
private static JFrame frame;

// ...

private static void createAndShowGUI(Locale currentLocale) {

    // Создать и настроить окно.
    // ...
    // Добавить содержимое в окно.
    // ...
    frame.applyComponentOrientation(
        ComponentOrientation.getOrientation(currentLocale));
    // ...
}
```

> Для более полного контроля над двунаправленным текстом см. раздел
> [Working with Bidirectional Text](https://docs.oracle.com/javase/tutorial/2d/text/textlayoutbidirectionaltext.html)
> трейла 2D Graphics.

## Источник

- [Working with Text (индекс урока)](https://docs.oracle.com/javase/tutorial/i18n/text/index.html) — официальное руководство Oracle.
- [Checking Character Properties](https://docs.oracle.com/javase/tutorial/i18n/text/charintro.html)
- [Comparing Strings](https://docs.oracle.com/javase/tutorial/i18n/text/collationintro.html)
- [Performing Locale-Independent Comparisons](https://docs.oracle.com/javase/tutorial/i18n/text/locale.html)
- [Customizing Collation Rules](https://docs.oracle.com/javase/tutorial/i18n/text/rule.html)
- [Improving Collation Performance](https://docs.oracle.com/javase/tutorial/i18n/text/perform.html)
- [Unicode](https://docs.oracle.com/javase/tutorial/i18n/text/unicode.html)
- [Terminology](https://docs.oracle.com/javase/tutorial/i18n/text/terminology.html)
- [Supplementary Characters as Surrogates](https://docs.oracle.com/javase/tutorial/i18n/text/supplementaryChars.html)
- [Character and String APIs](https://docs.oracle.com/javase/tutorial/i18n/text/characterClass.html)
- [Sample Usage](https://docs.oracle.com/javase/tutorial/i18n/text/usage.html)
- [Design Considerations](https://docs.oracle.com/javase/tutorial/i18n/text/design.html)
- [More Information](https://docs.oracle.com/javase/tutorial/i18n/text/info.html)
- [Detecting Text Boundaries](https://docs.oracle.com/javase/tutorial/i18n/text/boundaryintro.html)
- [About the BreakIterator Class](https://docs.oracle.com/javase/tutorial/i18n/text/about.html)
- [Character Boundaries](https://docs.oracle.com/javase/tutorial/i18n/text/char.html)
- [Word Boundaries](https://docs.oracle.com/javase/tutorial/i18n/text/word.html)
- [Sentence Boundaries](https://docs.oracle.com/javase/tutorial/i18n/text/sentence.html)
- [Line Boundaries](https://docs.oracle.com/javase/tutorial/i18n/text/line.html)
- [Converting Latin Digits to Other Unicode Digits](https://docs.oracle.com/javase/tutorial/i18n/text/shapedDigits.html)
- [Converting Non-Unicode Text](https://docs.oracle.com/javase/tutorial/i18n/text/convertintro.html)
- [Byte Encodings and Strings](https://docs.oracle.com/javase/tutorial/i18n/text/string.html)
- [Character and Byte Streams](https://docs.oracle.com/javase/tutorial/i18n/text/stream.html)
- [Normalizing Text](https://docs.oracle.com/javase/tutorial/i18n/text/normalizerapi.html)
- [Working with Bidirectional Text with the JTextComponent Class](https://docs.oracle.com/javase/tutorial/i18n/text/bidi.html)
