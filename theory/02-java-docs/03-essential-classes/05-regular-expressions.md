# Урок 5. Регулярные выражения

**Трейл:** Essential Java Classes · **Оригинал:** [Regular Expressions](https://docs.oracle.com/javase/tutorial/essential/regex/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет
> все страницы урока *Regular Expressions* трейла *Essential Java Classes*: *Introduction*,
> *Test Harness*, *String Literals*, *Character Classes*, *Predefined Character Classes*,
> *Quantifiers*, *Capturing Groups*, *Boundary Matchers*, *Methods of the Pattern Class*,
> *Methods of the Matcher Class*, *Methods of the PatternSyntaxException Class*,
> *Unicode Support* и *Additional Resources*.

Этот урок объясняет, как использовать API `java.util.regex` для сопоставления текста с шаблоном
с помощью регулярных выражений (*regular expressions*). Хотя синтаксис, принимаемый этим пакетом,
похож на синтаксис языка [Perl](http://www.perl.com), знание Perl не требуется. Урок начинается
с основ и постепенно переходит к более продвинутым приёмам.

## Введение (Introduction)

### Что такое регулярные выражения?

**Регулярные выражения** — это способ описать множество строк по общим признакам, которые
разделяет каждая строка из этого множества. Их можно использовать для поиска, редактирования и
обработки текста и данных. Чтобы создавать регулярные выражения, нужно изучить особый синтаксис —
выходящий за пределы обычного синтаксиса языка Java. Регулярные выражения бывают разной сложности,
но, освоив основы их построения, вы сможете расшифровать (или создать) любое регулярное выражение.

Этот трейл обучает синтаксису регулярных выражений, поддерживаемому API
[`java.util.regex`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/package-summary.html),
и приводит несколько рабочих примеров, иллюстрирующих, как взаимодействуют различные объекты.
В мире регулярных выражений существует множество разновидностей («диалектов») — grep, Perl, Tcl,
Python, PHP, awk. Синтаксис регулярных выражений в API `java.util.regex` наиболее близок к тому,
который используется в Perl.

### Как регулярные выражения представлены в этом пакете?

Пакет `java.util.regex` в основном состоит из трёх классов:
[`Pattern`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html),
[`Matcher`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html) и
[`PatternSyntaxException`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html).

- Объект **`Pattern`** (шаблон) — это скомпилированное представление регулярного выражения. Класс
  `Pattern` не предоставляет публичных конструкторов. Чтобы создать шаблон, нужно сначала вызвать
  один из его публичных статических методов `compile`, который вернёт объект `Pattern`. Эти методы
  принимают регулярное выражение в качестве первого аргумента; первые уроки этого трейла научат вас
  необходимому синтаксису.
- Объект **`Matcher`** (сопоставитель) — это движок, который интерпретирует шаблон и выполняет
  операции сопоставления над входной строкой. Как и класс `Pattern`, `Matcher` не определяет
  публичных конструкторов. Объект `Matcher` получают вызовом метода `matcher` у объекта `Pattern`.
- Объект **`PatternSyntaxException`** — это непроверяемое исключение (*unchecked exception*),
  сигнализирующее о синтаксической ошибке в шаблоне регулярного выражения.

Последние уроки трейла рассматривают каждый класс подробно. Но сначала нужно понять, как на самом
деле строятся регулярные выражения. Поэтому следующий раздел представляет простой тестовый стенд
(*test harness*), который будет неоднократно использоваться для изучения синтаксиса.

## Тестовый стенд (Test Harness)

В этом разделе определяется многоразовый тестовый стенд `RegexTestHarness.java` для изучения
конструкций регулярных выражений, поддерживаемых этим API. Команда запуска —
`java RegexTestHarness`; аргументы командной строки не принимаются. Приложение в цикле снова и снова
запрашивает у пользователя регулярное выражение и входную строку. Использование стенда необязательно,
но оно может оказаться удобным для проверки тестовых случаев, рассматриваемых на следующих страницах.

```java
import java.io.Console;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class RegexTestHarness {

    public static void main(String[] args){
        Console console = System.console();
        if (console == null) {
            System.err.println("No console.");
            System.exit(1);
        }
        while (true) {

            Pattern pattern = 
            Pattern.compile(console.readLine("%nEnter your regex: "));

            Matcher matcher = 
            pattern.matcher(console.readLine("Enter input string to search: "));

            boolean found = false;
            while (matcher.find()) {
                console.format("I found the text" +
                    " \"%s\" starting at " +
                    "index %d and ending at index %d.%n",
                    matcher.group(),
                    matcher.start(),
                    matcher.end());
                found = true;
            }
            if(!found){
                console.format("No match found.%n");
            }
        }
    }
}
```

Прежде чем переходить к следующему разделу, сохраните и скомпилируйте этот код, чтобы убедиться,
что ваша среда разработки поддерживает требуемые пакеты.

## Строковые литералы (String Literals)

Самая базовая форма сопоставления, поддерживаемая этим API, — совпадение со строковым литералом.
Например, если регулярное выражение — `foo`, а входная строка — `foo`, сопоставление будет успешным,
потому что строки идентичны. Попробуйте это в тестовом стенде:

```
Enter your regex: foo
Enter input string to search: foo
I found the text foo starting at index 0 and ending at index 3.
```

Сопоставление прошло успешно. Обратите внимание: хотя длина входной строки 3 символа, начальный
индекс равен 0, а конечный — 3. По соглашению диапазоны включают начальный индекс и исключают
конечный. Каждый символ строки занимает собственную **ячейку** (*cell*), а позиции индексов
указывают на промежутки между ячейками. Строка `"foo"` начинается с индекса 0 и заканчивается на
индексе 3, хотя сами символы занимают только ячейки 0, 1 и 2.

При последующих сопоставлениях вы заметите перекрытие: начальный индекс следующего совпадения
совпадает с конечным индексом предыдущего:

```
Enter your regex: foo
Enter input string to search: foofoofoo
I found the text foo starting at index 0 and ending at index 3.
I found the text foo starting at index 3 and ending at index 6.
I found the text foo starting at index 6 and ending at index 9.
```

### Метасимволы (Metacharacters)

Этот API также поддерживает ряд специальных символов, влияющих на способ сопоставления шаблона.
Измените регулярное выражение на `cat.`, а входную строку — на `cats`. Вывод будет таким:

```
Enter your regex: cat.
Enter input string to search: cats
I found the text cats starting at index 0 and ending at index 4.
```

Сопоставление по-прежнему успешно, хотя точки `.` нет во входной строке. Оно успешно, потому что
точка — это **метасимвол** (*metacharacter*): символ со специальным значением, интерпретируемый
сопоставителем. Метасимвол `.` означает «любой символ», поэтому совпадение в этом примере успешно.

Метасимволы, поддерживаемые этим API: `<([{\^-=$!|]})?*+.>`

> **Примечание.** В некоторых ситуациях перечисленные выше специальные символы *не* будут
> трактоваться как метасимволы. Вы столкнётесь с этим, изучая построение регулярных выражений.
> Однако этим списком можно пользоваться, чтобы проверить, может ли конкретный символ вообще
> считаться метасимволом. Например, символы `@` и `#` никогда не несут специального значения.

Есть два способа заставить метасимвол трактоваться как обычный символ:

- предварить метасимвол обратным слешем (*backslash*), либо
- заключить его между `\Q` (начало цитирования) и `\E` (конец цитирования).

При использовании этого приёма `\Q` и `\E` можно поместить в любом месте выражения — при условии,
что `\Q` идёт первым.

## Классы символов (Character Classes)

Если просмотреть спецификацию класса
[`Pattern`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html), вы увидите
таблицы, обобщающие поддерживаемые конструкции регулярных выражений. В разделе «Character Classes»
приведено следующее:

| Конструкция | Описание |
|-------------|----------|
| `[abc]` | a, b или c (простой класс) |
| `[^abc]` | любой символ, кроме a, b или c (отрицание) |
| `[a-zA-Z]` | от a до z или от A до Z включительно (диапазон) |
| `[a-d[m-p]]` | от a до d или от m до p: `[a-dm-p]` (объединение) |
| `[a-z&&[def]]` | d, e или f (пересечение) |
| `[a-z&&[^bc]]` | от a до z, кроме b и c: `[ad-z]` (вычитание) |
| `[a-z&&[^m-p]]` | от a до z, но не от m до p: `[a-lq-z]` (вычитание) |

Левый столбец задаёт конструкции регулярного выражения, а правый описывает условия, при которых
каждая конструкция даёт совпадение.

> **Примечание.** Слово «класс» в словосочетании «класс символов» (*character class*) не имеет
> отношения к `.class`-файлу. В контексте регулярных выражений **класс символов** — это набор
> символов, заключённый в квадратные скобки. Он задаёт символы, которые успешно совпадут с одним
> символом из входной строки.

### Простые классы (Simple Classes)

Самая базовая форма класса символов — просто перечислить набор символов рядом внутри квадратных
скобок. Например, регулярное выражение `[bcr]at` совпадёт со словами `"bat"`, `"cat"` или `"rat"`,
потому что оно определяет класс символов (принимающий `"b"`, `"c"` или `"r"`) в качестве первого
символа.

```
Enter your regex: [bcr]at
Enter input string to search: bat
I found the text "bat" starting at index 0 and ending at index 3.

Enter your regex: [bcr]at
Enter input string to search: cat
I found the text "cat" starting at index 0 and ending at index 3.

Enter your regex: [bcr]at
Enter input string to search: rat
I found the text "rat" starting at index 0 and ending at index 3.

Enter your regex: [bcr]at
Enter input string to search: hat
No match found.
```

В приведённых примерах общее сопоставление успешно только тогда, когда первая буква совпадает с
одним из символов, заданных классом символов.

### Отрицание (Negation)

Чтобы совпали все символы, *кроме* перечисленных, вставьте метасимвол `^` в начало класса символов.
Этот приём называется **отрицанием** (*negation*).

```
Enter your regex: [^bcr]at
Enter input string to search: bat
No match found.

Enter your regex: [^bcr]at
Enter input string to search: cat
No match found.

Enter your regex: [^bcr]at
Enter input string to search: rat
No match found.

Enter your regex: [^bcr]at
Enter input string to search: hat
I found the text "hat" starting at index 0 and ending at index 3.
```

Сопоставление успешно только в том случае, если первый символ входной строки *не* содержится среди
символов, заданных классом символов.

### Диапазоны (Ranges)

Иногда нужно задать класс символов, включающий диапазон значений, например буквы «от a до h» или
числа «от 1 до 5». Чтобы задать диапазон, просто вставьте метасимвол `-` между первым и последним
символами, например `[1-5]` или `[a-h]`. Можно также располагать разные диапазоны рядом внутри
класса, расширяя варианты совпадения. Например, `[a-zA-Z]` совпадёт с любой буквой алфавита: от a
до z (строчные) или от A до Z (прописные).

Несколько примеров диапазонов и отрицания:

```
Enter your regex: [a-c]
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.

Enter your regex: [a-c]
Enter input string to search: b
I found the text "b" starting at index 0 and ending at index 1.

Enter your regex: [a-c]
Enter input string to search: c
I found the text "c" starting at index 0 and ending at index 1.

Enter your regex: [a-c]
Enter input string to search: d
No match found.

Enter your regex: foo[1-5]
Enter input string to search: foo1
I found the text "foo1" starting at index 0 and ending at index 4.

Enter your regex: foo[1-5]
Enter input string to search: foo5
I found the text "foo5" starting at index 0 and ending at index 4.

Enter your regex: foo[1-5]
Enter input string to search: foo6
No match found.

Enter your regex: foo[^1-5]
Enter input string to search: foo1
No match found.

Enter your regex: foo[^1-5]
Enter input string to search: foo6
I found the text "foo6" starting at index 0 and ending at index 4.
```

### Объединения (Unions)

Можно также использовать **объединения** (*unions*), чтобы создать один класс символов из двух или
более отдельных классов. Чтобы создать объединение, просто вложите один класс в другой, например
`[0-4[6-8]]`. Это объединение создаёт единый класс символов, совпадающий с числами 0, 1, 2, 3, 4, 6,
7 и 8.

```
Enter your regex: [0-4[6-8]]
Enter input string to search: 0
I found the text "0" starting at index 0 and ending at index 1.

Enter your regex: [0-4[6-8]]
Enter input string to search: 5
No match found.

Enter your regex: [0-4[6-8]]
Enter input string to search: 6
I found the text "6" starting at index 0 and ending at index 1.

Enter your regex: [0-4[6-8]]
Enter input string to search: 8
I found the text "8" starting at index 0 and ending at index 1.

Enter your regex: [0-4[6-8]]
Enter input string to search: 9
No match found.
```

### Пересечения (Intersections)

Чтобы создать единый класс символов, совпадающий только с символами, общими для всех вложенных
классов, используйте `&&`, как в `[0-9&&[345]]`. Это пересечение создаёт класс символов, совпадающий
только с числами, общими для обоих классов: 3, 4 и 5.

```
Enter your regex: [0-9&&[345]]
Enter input string to search: 3
I found the text "3" starting at index 0 and ending at index 1.

Enter your regex: [0-9&&[345]]
Enter input string to search: 4
I found the text "4" starting at index 0 and ending at index 1.

Enter your regex: [0-9&&[345]]
Enter input string to search: 5
I found the text "5" starting at index 0 and ending at index 1.

Enter your regex: [0-9&&[345]]
Enter input string to search: 2
No match found.

Enter your regex: [0-9&&[345]]
Enter input string to search: 6
No match found.
```

А вот пример, показывающий пересечение двух диапазонов:

```
Enter your regex: [2-8&&[4-6]]
Enter input string to search: 3
No match found.

Enter your regex: [2-8&&[4-6]]
Enter input string to search: 4
I found the text "4" starting at index 0 and ending at index 1.

Enter your regex: [2-8&&[4-6]]
Enter input string to search: 5
I found the text "5" starting at index 0 and ending at index 1.

Enter your regex: [2-8&&[4-6]]
Enter input string to search: 6
I found the text "6" starting at index 0 and ending at index 1.

Enter your regex: [2-8&&[4-6]]
Enter input string to search: 7
No match found.
```

### Вычитание (Subtraction)

Наконец, можно использовать **вычитание** (*subtraction*), чтобы исключить один или несколько
вложенных классов символов, например `[0-9&&[^345]]`. Этот пример создаёт единый класс символов,
совпадающий со всем от 0 до 9, *кроме* чисел 3, 4 и 5.

```
Enter your regex: [0-9&&[^345]]
Enter input string to search: 2
I found the text "2" starting at index 0 and ending at index 1.

Enter your regex: [0-9&&[^345]]
Enter input string to search: 3
No match found.

Enter your regex: [0-9&&[^345]]
Enter input string to search: 4
No match found.

Enter your regex: [0-9&&[^345]]
Enter input string to search: 5
No match found.

Enter your regex: [0-9&&[^345]]
Enter input string to search: 6
I found the text "6" starting at index 0 and ending at index 1.

Enter your regex: [0-9&&[^345]]
Enter input string to search: 9
I found the text "9" starting at index 0 and ending at index 1.
```

## Предопределённые классы символов (Predefined Character Classes)

API [`Pattern`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html) содержит ряд
полезных **предопределённых классов символов** (*predefined character classes*) — удобных сокращений
для часто используемых регулярных выражений:

| Конструкция | Описание |
|-------------|----------|
| `.` | любой символ (может совпадать или не совпадать с символами завершения строки) |
| `\d` | цифра: `[0-9]` |
| `\D` | не-цифра: `[^0-9]` |
| `\s` | пробельный символ: `[ \t\n\x0B\f\r]` |
| `\S` | не-пробельный символ: `[^\s]` |
| `\w` | словесный символ: `[a-zA-Z_0-9]` |
| `\W` | не-словесный символ: `[^\w]` |

В таблице выше каждая конструкция в левом столбце — это сокращение для класса символов из правого
столбца. Например, `\d` означает диапазон цифр (0–9), а `\w` означает словесный символ (любая
строчная буква, любая прописная буква, символ подчёркивания или любая цифра). Используйте
предопределённые классы там, где это возможно: они делают код легче для чтения и устраняют ошибки,
вызванные неправильно построенными классами символов.

Конструкции, начинающиеся с обратного слеша, называются **экранированными конструкциями**
(*escaped constructs*). Мы упоминали их в разделе [Строковые литералы](#строковые-литералы-string-literals),
где речь шла об использовании обратного слеша, а также `\Q` и `\E` для цитирования. Если вы
используете экранированную конструкцию внутри строкового литерала, то перед обратным слешем нужно
поставить ещё один обратный слеш, чтобы строка скомпилировалась. Например:

```java
private final String REGEX = "\\d"; // одна цифра
```

В этом примере `\d` — это регулярное выражение; дополнительный обратный слеш необходим, чтобы код
скомпилировался. Однако тестовый стенд читает выражения напрямую из `Console`, поэтому
дополнительный обратный слеш не требуется.

Следующие примеры демонстрируют использование предопределённых классов символов.

```
Enter your regex: .
Enter input string to search: @
I found the text "@" starting at index 0 and ending at index 1.

Enter your regex: .
Enter input string to search: 1
I found the text "1" starting at index 0 and ending at index 1.

Enter your regex: .
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.

Enter your regex: \d
Enter input string to search: 1
I found the text "1" starting at index 0 and ending at index 1.

Enter your regex: \d
Enter input string to search: a
No match found.

Enter your regex: \D
Enter input string to search: 1
No match found.

Enter your regex: \D
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.

Enter your regex: \s
Enter input string to search:  
I found the text " " starting at index 0 and ending at index 1.

Enter your regex: \s
Enter input string to search: a
No match found.

Enter your regex: \S
Enter input string to search:  
No match found.

Enter your regex: \S
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.

Enter your regex: \w
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.

Enter your regex: \w
Enter input string to search: !
No match found.

Enter your regex: \W
Enter input string to search: a
No match found.

Enter your regex: \W
Enter input string to search: !
I found the text "!" starting at index 0 and ending at index 1.
```

В первых трёх примерах регулярное выражение — это просто `.` (метасимвол «точка»), означающий «любой
символ». Поэтому сопоставление успешно во всех трёх случаях (случайно выбранный символ `@`, цифра и
буква). Остальные примеры используют по одной конструкции из таблицы предопределённых классов
символов. По этой таблице можно понять логику каждого совпадения:

- `\d` совпадает со всеми цифрами;
- `\s` совпадает с пробелами;
- `\w` совпадает со словесными символами.

И наоборот, заглавная буква означает противоположное:

- `\D` совпадает с не-цифрами;
- `\S` совпадает с не-пробелами;
- `\W` совпадает с не-словесными символами.

## Квантификаторы (Quantifiers)

**Квантификаторы** (*quantifiers*) позволяют задать число вхождений, с которым нужно сопоставлять.
Для удобства ниже представлены три раздела спецификации Pattern API, описывающие жадные (*greedy*),
ленивые (*reluctant*) и сверхжадные (*possessive*) квантификаторы. На первый взгляд может
показаться, что квантификаторы `X?`, `X??` и `X?+` делают одно и то же, ведь все они обещают
совпасть с «`X`, один раз или вовсе ни разу». Однако существуют тонкие различия в реализации,
которые будут объяснены в конце этого раздела.

| Жадный | Ленивый | Сверхжадный | Значение |
|--------|---------|-------------|----------|
| `X?` | `X??` | `X?+` | `X`, один раз или ни разу |
| `X*` | `X*?` | `X*+` | `X`, ноль или более раз |
| `X+` | `X+?` | `X++` | `X`, один или более раз |
| `X{n}` | `X{n}?` | `X{n}+` | `X`, ровно `n` раз |
| `X{n,}` | `X{n,}?` | `X{n,}+` | `X`, не менее `n` раз |
| `X{n,m}` | `X{n,m}?` | `X{n,m}+` | `X`, не менее `n`, но не более `m` раз |

Начнём знакомство с жадными квантификаторами, создав три разных регулярных выражения: буква «a», за
которой следует `?`, `*` или `+`. Посмотрим, что произойдёт при проверке этих выражений против
пустой входной строки `""`:

```
Enter your regex: a?
Enter input string to search: 
I found the text "" starting at index 0 and ending at index 0.

Enter your regex: a*
Enter input string to search: 
I found the text "" starting at index 0 and ending at index 0.

Enter your regex: a+
Enter input string to search: 
No match found.
```

### Совпадения нулевой длины (Zero-Length Matches)

В примере выше сопоставление успешно в первых двух случаях, потому что выражения `a?` и `a*`
допускают ноль вхождений буквы `a`. Вы также заметите, что начальный и конечный индексы оба равны
нулю — в отличие от всех ранее рассмотренных примеров. Пустая входная строка `""` не имеет длины,
поэтому тест просто совпадает с «ничем» в позиции индекса 0. Такие совпадения называются
**совпадениями нулевой длины** (*zero-length matches*). Совпадение нулевой длины может произойти в
нескольких случаях: в пустой входной строке, в начале входной строки, после последнего символа
входной строки или между любыми двумя символами входной строки. Совпадения нулевой длины легко
распознать: они всегда начинаются и заканчиваются на одной и той же позиции индекса.

Рассмотрим совпадения нулевой длины на ещё нескольких примерах. Замените входную строку на одну
букву «a» — и вы заметите кое-что интересное:

```
Enter your regex: a?
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.
I found the text "" starting at index 1 and ending at index 1.

Enter your regex: a*
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.
I found the text "" starting at index 1 and ending at index 1.

Enter your regex: a+
Enter input string to search: a
I found the text "a" starting at index 0 and ending at index 1.
```

Все три квантификатора нашли букву «a», но первые два также нашли совпадение нулевой длины на индексе
1, то есть после последнего символа входной строки. Помните: сопоставитель видит символ «a»
расположенным в ячейке между индексом 0 и индексом 1, а наш тестовый стенд работает в цикле, пока
способен находить совпадения. В зависимости от используемого квантификатора наличие «ничего» в
позиции после последнего символа может вызывать совпадение, а может и не вызывать.

Теперь замените входную строку на букву «a», повторённую пять раз подряд:

```
Enter your regex: a?
Enter input string to search: aaaaa
I found the text "a" starting at index 0 and ending at index 1.
I found the text "a" starting at index 1 and ending at index 2.
I found the text "a" starting at index 2 and ending at index 3.
I found the text "a" starting at index 3 and ending at index 4.
I found the text "a" starting at index 4 and ending at index 5.
I found the text "" starting at index 5 and ending at index 5.

Enter your regex: a*
Enter input string to search: aaaaa
I found the text "aaaaa" starting at index 0 and ending at index 5.
I found the text "" starting at index 5 and ending at index 5.

Enter your regex: a+
Enter input string to search: aaaaa
I found the text "aaaaa" starting at index 0 and ending at index 5.
```

Выражение `a?` находит отдельное совпадение для каждого символа, поскольку оно совпадает, когда «a»
встречается ноль или один раз. Выражение `a*` находит два отдельных совпадения: все буквы «a» в
первом совпадении, затем совпадение нулевой длины после последнего символа на индексе 5. Наконец,
`a+` совпадает со всеми вхождениями буквы «a», игнорируя наличие «ничего» на последнем индексе.

В этот момент вы можете задаться вопросом: что будет, если первые два квантификатора встретят букву,
отличную от «a»? Например, что произойдёт, если встретится буква «b», как в строке `"ababaaaab"`?

Выясним:

```
Enter your regex: a?
Enter input string to search: ababaaaab
I found the text "a" starting at index 0 and ending at index 1.
I found the text "" starting at index 1 and ending at index 1.
I found the text "a" starting at index 2 and ending at index 3.
I found the text "" starting at index 3 and ending at index 3.
I found the text "a" starting at index 4 and ending at index 5.
I found the text "a" starting at index 5 and ending at index 6.
I found the text "a" starting at index 6 and ending at index 7.
I found the text "a" starting at index 7 and ending at index 8.
I found the text "" starting at index 8 and ending at index 8.
I found the text "" starting at index 9 and ending at index 9.

Enter your regex: a*
Enter input string to search: ababaaaab
I found the text "a" starting at index 0 and ending at index 1.
I found the text "" starting at index 1 and ending at index 1.
I found the text "a" starting at index 2 and ending at index 3.
I found the text "" starting at index 3 and ending at index 3.
I found the text "aaaa" starting at index 4 and ending at index 8.
I found the text "" starting at index 8 and ending at index 8.
I found the text "" starting at index 9 and ending at index 9.

Enter your regex: a+
Enter input string to search: ababaaaab
I found the text "a" starting at index 0 and ending at index 1.
I found the text "a" starting at index 2 and ending at index 3.
I found the text "aaaa" starting at index 4 and ending at index 8.
```

Хотя буква «b» появляется в ячейках 1, 3 и 8, в этих местах вывод сообщает о совпадении нулевой
длины. Регулярное выражение `a?` не ищет конкретно букву «b»; оно лишь ищет наличие (или отсутствие)
буквы «a». Если квантификатор допускает совпадение «a» ноль раз, то всё во входной строке, что не
является «a», отобразится как совпадение нулевой длины. Остальные «a» совпадают по правилам,
рассмотренным в предыдущих примерах.

Чтобы совпасть с шаблоном ровно `n` раз, просто укажите число внутри фигурных скобок:

```
Enter your regex: a{3}
Enter input string to search: aa
No match found.

Enter your regex: a{3}
Enter input string to search: aaa
I found the text "aaa" starting at index 0 and ending at index 3.

Enter your regex: a{3}
Enter input string to search: aaaa
I found the text "aaa" starting at index 0 and ending at index 3.
```

Здесь регулярное выражение `a{3}` ищет три вхождения буквы «a» подряд. Первый тест проваливается,
потому что во входной строке недостаточно «a» для совпадения. Второй тест содержит ровно 3 «a»,
что вызывает совпадение. Третий тест тоже даёт совпадение, потому что в начале входной строки ровно
3 «a». Всё, что идёт после, несущественно для первого совпадения. Если шаблон встретится снова после
этой точки, он вызовет последующие совпадения:

```
Enter your regex: a{3}
Enter input string to search: aaaaaaaaa
I found the text "aaa" starting at index 0 and ending at index 3.
I found the text "aaa" starting at index 3 and ending at index 6.
I found the text "aaa" starting at index 6 and ending at index 9.
```

Чтобы требовать появления шаблона не менее `n` раз, добавьте запятую после числа:

```
Enter your regex: a{3,}
Enter input string to search: aaaaaaaaa
I found the text "aaaaaaaaa" starting at index 0 and ending at index 9.
```

С той же входной строкой этот тест находит только одно совпадение, потому что 9 «a» подряд
удовлетворяют требованию «не менее» 3 «a».

Наконец, чтобы задать верхний предел числа вхождений, добавьте второе число внутри фигурных скобок:

```
Enter your regex: a{3,6} // найти не менее 3 (но не более 6) "a" подряд
Enter input string to search: aaaaaaaaa
I found the text "aaaaaa" starting at index 0 and ending at index 6.
I found the text "aaa" starting at index 6 and ending at index 9.
```

Здесь первое совпадение вынужденно останавливается на верхнем пределе в 6 символов. Второе совпадение
включает то, что осталось, а именно три «a» — минимальное число символов, допустимое для этого
совпадения. Если бы входная строка была на один символ короче, второго совпадения не было бы,
поскольку осталось бы лишь две «a».

### Захватывающие группы и классы символов с квантификаторами

До сих пор мы проверяли квантификаторы только на входных строках, содержащих один символ. На самом
деле квантификаторы могут присоединяться лишь к одному символу за раз, поэтому регулярное выражение
`abc+` означает «a, за которым следует b, за которым следует c один или более раз». Оно *не*
означает «abc» один или более раз. Однако квантификаторы могут также присоединяться к
[классам символов](#классы-символов-character-classes) и
[захватывающим группам](#захватывающие-группы-capturing-groups), например `[abc]+` (a, b или c, один
или более раз) или `(abc)+` (группа «abc», один или более раз).

Проиллюстрируем это, задав группу `(dog)` три раза подряд:

```
Enter your regex: (dog){3}
Enter input string to search: dogdogdogdogdogdog
I found the text "dogdogdog" starting at index 0 and ending at index 9.
I found the text "dogdogdog" starting at index 9 and ending at index 18.

Enter your regex: dog{3}
Enter input string to search: dogdogdogdogdogdog
No match found.
```

В первом примере находятся три совпадения, поскольку квантификатор применяется ко всей захватывающей
группе. Уберите скобки — и совпадение провалится, потому что квантификатор `{3}` теперь применяется
только к букве «g».

Аналогично можно применить квантификатор ко всему классу символов:

```
Enter your regex: [abc]{3}
Enter input string to search: abccabaaaccbbbc
I found the text "abc" starting at index 0 and ending at index 3.
I found the text "cab" starting at index 3 and ending at index 6.
I found the text "aaa" starting at index 6 and ending at index 9.
I found the text "ccb" starting at index 9 and ending at index 12.
I found the text "bbc" starting at index 12 and ending at index 15.

Enter your regex: abc{3}
Enter input string to search: abccabaaaccbbbc
No match found.
```

Здесь в первом примере квантификатор `{3}` применяется ко всему классу символов, а во втором — только
к букве «c».

### Различия между жадными, ленивыми и сверхжадными квантификаторами

Между жадными, ленивыми и сверхжадными квантификаторами есть тонкие различия.

Жадные квантификаторы считаются «жадными», потому что они заставляют сопоставитель сначала прочитать,
или «съесть», всю входную строку, прежде чем пытаться выполнить первое совпадение. Если первая
попытка совпадения (вся входная строка) проваливается, сопоставитель отступает на один символ назад
и пробует снова, повторяя процесс, пока совпадение не будет найдено или пока не закончатся символы,
от которых можно отступать. В зависимости от используемого квантификатора последнее, что он
попытается сопоставить, — это 1 или 0 символов.

Ленивые квантификаторы, напротив, действуют противоположным образом: они начинают с начала входной
строки, а затем неохотно «съедают» по одному символу за раз в поисках совпадения. Последнее, что они
пробуют, — вся входная строка.

Наконец, сверхжадные квантификаторы всегда «съедают» всю входную строку, пробуя совпадение один раз
(и только один раз). В отличие от жадных, сверхжадные квантификаторы никогда не отступают назад —
даже если это позволило бы общему совпадению быть успешным.

Для иллюстрации рассмотрим входную строку `xfooxxxxxxfoo`.

```
Enter your regex: .*foo  // жадный квантификатор
Enter input string to search: xfooxxxxxxfoo
I found the text "xfooxxxxxxfoo" starting at index 0 and ending at index 13.

Enter your regex: .*?foo  // ленивый квантификатор
Enter input string to search: xfooxxxxxxfoo
I found the text "xfoo" starting at index 0 and ending at index 4.
I found the text "xxxxxxfoo" starting at index 4 and ending at index 13.

Enter your regex: .*+foo // сверхжадный квантификатор
Enter input string to search: xfooxxxxxxfoo
No match found.
```

В первом примере используется жадный квантификатор `.*`, чтобы найти «что угодно» ноль или более раз,
за чем следуют буквы `"f" "o" "o"`. Поскольку квантификатор жадный, часть `.*` выражения сначала
поглощает всю входную строку. На этом этапе всё выражение не может быть успешным, потому что
последние три буквы (`"f" "o" "o"`) уже поглощены. Поэтому сопоставитель медленно отступает по одной
букве за раз, пока не «отрыгнёт» самое правое вхождение «foo», и тогда совпадение становится
успешным, а поиск завершается.

Второй пример, однако, ленивый, поэтому он начинает с поглощения «ничего». Поскольку «foo» не
появляется в начале строки, он вынужден проглотить первую букву (это «x»), что вызывает первое
совпадение на 0 и 4. Наш тестовый стенд продолжает процесс, пока входная строка не будет исчерпана.
Он находит ещё одно совпадение на 4 и 13.

Третий пример не находит совпадения, потому что квантификатор сверхжадный. В этом случае вся входная
строка поглощается `.*+`, и не остаётся ничего, чтобы удовлетворить «foo» в конце выражения.
Используйте сверхжадный квантификатор в ситуациях, когда вы хотите захватить всё целиком, ни разу не
отступая; он превзойдёт по производительности эквивалентный жадный квантификатор в случаях, когда
совпадение не находится сразу.

## Захватывающие группы (Capturing Groups)

В [предыдущем разделе](#квантификаторы-quantifiers) мы видели, как квантификаторы присоединяются по
одному символу, классу символов или захватывающей группе за раз. Но до сих пор мы не обсуждали
понятие захватывающих групп подробно.

**Захватывающие группы** (*capturing groups*) — это способ трактовать несколько символов как единое
целое. Они создаются заключением группируемых символов в круглые скобки. Например, регулярное
выражение `(dog)` создаёт единую группу, содержащую буквы `"d" "o"` и `"g"`. Часть входной строки,
совпавшая с захватывающей группой, сохраняется в памяти для последующего обращения через обратные
ссылки (*backreferences*) — как обсуждается ниже в подразделе [Обратные ссылки](#обратные-ссылки-backreferences).

### Нумерация (Numbering)

Как описано в API [`Pattern`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html),
захватывающие группы нумеруются подсчётом их открывающих круглых скобок слева направо. Например, в
выражении `((A)(B(C)))` есть четыре такие группы:

1. `((A)(B(C)))`
2. `(A)`
3. `(B(C))`
4. `(C)`

Чтобы узнать, сколько групп присутствует в выражении, вызовите метод `groupCount` у объекта matcher.
Метод `groupCount` возвращает `int`, показывающий число захватывающих групп в шаблоне сопоставителя.
В этом примере `groupCount` вернул бы число `4`, показывая, что шаблон содержит 4 захватывающие
группы.

Существует также особая группа — группа 0, которая всегда представляет всё выражение целиком. Эта
группа не учитывается в общем количестве, возвращаемом `groupCount`. Группы, начинающиеся с `(?`, —
это чистые **незахватывающие группы** (*non-capturing groups*), которые не захватывают текст и не
учитываются в общем числе групп. (Примеры незахватывающих групп вы увидите позже в разделе
[Методы класса Pattern](#методы-класса-pattern-methods-of-the-pattern-class).)

Важно понимать, как нумеруются группы, потому что некоторые методы `Matcher` принимают `int`,
задающий номер конкретной группы, в качестве параметра:

- [`public int start(int group)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#start-int-):
  возвращает начальный индекс подпоследовательности, захваченной заданной группой при предыдущей
  операции сопоставления.
- [`public int end (int group)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#end-int-):
  возвращает индекс последнего символа плюс один для подпоследовательности, захваченной заданной
  группой при предыдущей операции сопоставления.
- [`public String group (int group)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#group-int-):
  возвращает подпоследовательность входных данных, захваченную заданной группой при предыдущей
  операции сопоставления.

### Обратные ссылки (Backreferences)

Участок входной строки, совпавший с захватывающей группой(-ами), сохраняется в памяти для
последующего обращения через **обратную ссылку** (*backreference*). Обратная ссылка задаётся в
регулярном выражении как обратный слеш (`\`), за которым следует цифра, указывающая номер вызываемой
группы. Например, выражение `(\d\d)` определяет одну захватывающую группу, совпадающую с двумя
цифрами подряд, к которой позже в выражении можно обратиться через обратную ссылку `\1`.

Чтобы совпасть с любыми 2 цифрами, за которыми следуют ровно те же две цифры, используйте `(\d\d)\1`
в качестве регулярного выражения:

```
Enter your regex: (\d\d)\1
Enter input string to search: 1212
I found the text "1212" starting at index 0 and ending at index 4.
```

Если изменить последние две цифры, совпадение провалится:

```
Enter your regex: (\d\d)\1
Enter input string to search: 1234
No match found.
```

Для вложенных захватывающих групп обратные ссылки работают точно так же: укажите обратный слеш, за
которым следует номер вызываемой группы.

## Граничные маркеры (Boundary Matchers)

До сих пор нас интересовало лишь то, найдено ли совпадение *где-либо* в конкретной входной строке.
Нас никогда не волновало, *где именно* в строке происходит совпадение.

Можно сделать сопоставление более точным, задав такую информацию с помощью **граничных маркеров**
(*boundary matchers*). Например, может быть, вы хотите найти конкретное слово, но только если оно
появляется в начале или в конце строки. Или, может быть, вы хотите узнать, происходит ли совпадение
на границе слова или в конце предыдущего совпадения.

В следующей таблице перечислены и объяснены все граничные маркеры.

| Граничная конструкция | Описание |
|------------------------|----------|
| `^` | начало строки |
| `$` | конец строки |
| `\b` | граница слова |
| `\B` | не-граница слова |
| `\A` | начало входных данных |
| `\G` | конец предыдущего совпадения |
| `\Z` | конец входных данных, не считая финального символа завершения строки, если он есть |
| `\z` | конец входных данных |

Следующие примеры демонстрируют использование граничных маркеров `^` и `$`. Как отмечено выше, `^`
совпадает с началом строки, а `$` — с концом.

```
Enter your regex: ^dog$
Enter input string to search: dog
I found the text "dog" starting at index 0 and ending at index 3.

Enter your regex: ^dog$
Enter input string to search:       dog
No match found.

Enter your regex: \s*dog$
Enter input string to search:             dog
I found the text "            dog" starting at index 0 and ending at index 15.

Enter your regex: ^dog\w*
Enter input string to search: dogblahblah
I found the text "dogblahblah" starting at index 0 and ending at index 11.
```

Первый пример успешен, потому что шаблон занимает всю входную строку. Второй пример проваливается,
потому что во входной строке есть лишние пробелы в начале. Третий пример задаёт выражение,
допускающее неограниченное число пробелов, за которыми следует «dog» в конце строки. Четвёртый пример
требует, чтобы «dog» присутствовал в начале строки, за ним — неограниченное число словесных символов.

Чтобы проверить, начинается и заканчивается ли шаблон на границе слова (а не является подстрокой
внутри более длинной строки), просто используйте `\b` с обеих сторон; например, `\bdog\b`:

```
Enter your regex: \bdog\b
Enter input string to search: The dog plays in the yard.
I found the text "dog" starting at index 4 and ending at index 7.

Enter your regex: \bdog\b
Enter input string to search: The doggie plays in the yard.
No match found.
```

Чтобы сопоставить выражение на не-границе слова, используйте вместо этого `\B`:

```
Enter your regex: \bdog\B
Enter input string to search: The dog plays in the yard.
No match found.

Enter your regex: \bdog\B
Enter input string to search: The doggie plays in the yard.
I found the text "dog" starting at index 4 and ending at index 7.
```

Чтобы требовать, чтобы совпадение происходило только в конце предыдущего совпадения, используйте `\G`:

```
Enter your regex: dog 
Enter input string to search: dog dog
I found the text "dog" starting at index 0 and ending at index 3.
I found the text "dog" starting at index 4 and ending at index 7.

Enter your regex: \Gdog 
Enter input string to search: dog dog
I found the text "dog" starting at index 0 and ending at index 3.
```

Здесь второй пример находит только одно совпадение, потому что второе вхождение «dog» не начинается в
конце предыдущего совпадения.

## Методы класса Pattern (Methods of the Pattern Class)

До сих пор мы использовали тестовый стенд лишь для создания объектов `Pattern` в их самой базовой
форме. Этот раздел рассматривает продвинутые приёмы — создание шаблонов с флагами и использование
встроенных флаговых выражений. Он также рассматривает несколько полезных методов, которые мы ещё не
обсуждали.

### Создание шаблона с флагами (Creating a Pattern with Flags)

Класс `Pattern` определяет альтернативный метод `compile`, который принимает набор флагов, влияющих
на способ сопоставления шаблона. Параметр флагов — это битовая маска, которая может включать любые из
следующих публичных статических полей:

- [`Pattern.CANON_EQ`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#CANON_EQ) —
  включает каноническую эквивалентность. Когда этот флаг задан, два символа считаются совпадающими
  тогда и только тогда, когда совпадают их полные канонические разложения. Например, выражение
  `"å"` совпадёт со строкой `"å"`, если этот флаг задан. По умолчанию сопоставление не
  учитывает каноническую эквивалентность. Задание этого флага может повлечь снижение
  производительности.
- [`Pattern.CASE_INSENSITIVE`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#CASE_INSENSITIVE) —
  включает сопоставление без учёта регистра. По умолчанию сопоставление без учёта регистра
  предполагает, что сопоставляются только символы из набора US-ASCII. Сопоставление без учёта
  регистра с учётом Unicode можно включить, задав флаг `UNICODE_CASE` вместе с этим флагом.
  Сопоставление без учёта регистра можно также включить через встроенное флаговое выражение `(?i)`.
  Задание этого флага может повлечь небольшое снижение производительности.
- [`Pattern.COMMENTS`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#COMMENTS) —
  разрешает пробелы и комментарии в шаблоне. В этом режиме пробелы игнорируются, а встроенные
  комментарии, начинающиеся с `#`, игнорируются до конца строки. Режим комментариев можно также
  включить через встроенное флаговое выражение `(?x)`.
- [`Pattern.DOTALL`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#DOTALL) —
  включает режим dotall. В режиме dotall выражение `.` совпадает с любым символом, включая символ
  завершения строки. По умолчанию это выражение не совпадает с символами завершения строки. Режим
  dotall можно также включить через встроенное флаговое выражение `(?s)`. (Буква s — мнемоника для
  режима «single-line» («однострочный»), как это называется в Perl.)
- [`Pattern.LITERAL`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#LITERAL) —
  включает буквальный разбор шаблона. Когда этот флаг задан, входная строка, задающая шаблон,
  трактуется как последовательность буквальных символов. Метасимволы или escape-последовательности
  во входной последовательности не получат специального значения. Флаги `CASE_INSENSITIVE` и
  `UNICODE_CASE` сохраняют своё влияние на сопоставление при использовании вместе с этим флагом.
  Остальные флаги становятся излишними. Встроенного флагового символа для включения буквального
  разбора не существует.
- [`Pattern.MULTILINE`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#MULTILINE) —
  включает многострочный режим. В многострочном режиме выражения `^` и `$` совпадают соответственно
  сразу после или непосредственно перед символом завершения строки либо концом входной
  последовательности. По умолчанию эти выражения совпадают только в начале и в конце всей входной
  последовательности. Многострочный режим можно также включить через встроенное флаговое выражение
  `(?m)`.
- [`Pattern.UNICODE_CASE`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#UNICODE_CASE) —
  включает свёртку регистра с учётом Unicode. Когда этот флаг задан, сопоставление без учёта регистра
  (включённое флагом `CASE_INSENSITIVE`) выполняется согласованно со стандартом Unicode. По умолчанию
  сопоставление без учёта регистра предполагает, что сопоставляются только символы из набора
  US-ASCII. Свёртку регистра с учётом Unicode можно также включить через встроенное флаговое
  выражение `(?u)`. Задание этого флага может повлечь снижение производительности.
- [`Pattern.UNIX_LINES`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#UNIX_LINES) —
  включает режим UNIX-строк. В этом режиме в поведении `.`, `^` и `$` распознаётся только символ
  завершения строки `'\n'`. Режим UNIX-строк можно также включить через встроенное флаговое выражение
  `(?d)`.

На следующих шагах мы изменим тестовый стенд `RegexTestHarness.java`, чтобы создать шаблон с
сопоставлением без учёта регистра.

Сначала измените код, чтобы вызвать альтернативную версию `compile`:

```java
Pattern pattern = 
Pattern.compile(console.readLine("%nEnter your regex: "),
Pattern.CASE_INSENSITIVE);
```

Затем скомпилируйте и запустите тестовый стенд, чтобы получить следующие результаты:

```
Enter your regex: dog
Enter input string to search: DoGDOg
I found the text "DoG" starting at index 0 and ending at index 3.
I found the text "DOg" starting at index 3 and ending at index 6.
```

Как видно, строковый литерал «dog» совпадает с обоими вхождениями, независимо от регистра. Чтобы
скомпилировать шаблон с несколькими флагами, разделите включаемые флаги побитовым оператором ИЛИ
(`|`). Для наглядности в следующих примерах кода регулярное выражение задано жёстко, а не считывается
из `Console`:

```java
pattern = Pattern.compile("[az]$", Pattern.MULTILINE | Pattern.UNIX_LINES);
```

Можно также указать переменную типа `int`:

```java
final int flags = Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE;
Pattern pattern = Pattern.compile("aa", flags);
```

### Встроенные флаговые выражения (Embedded Flag Expressions)

Различные флаги можно также включать с помощью **встроенных флаговых выражений** (*embedded flag
expressions*). Встроенные флаговые выражения — это альтернатива двухаргументной версии `compile`, и
они задаются прямо в самом регулярном выражении. В следующем примере используется исходный тестовый
стенд `RegexTestHarness.java` со встроенным флаговым выражением `(?i)` для включения сопоставления
без учёта регистра.

```
Enter your regex: (?i)foo
Enter input string to search: FOOfooFoOfoO
I found the text "FOO" starting at index 0 and ending at index 3.
I found the text "foo" starting at index 3 and ending at index 6.
I found the text "FoO" starting at index 6 and ending at index 9.
I found the text "foO" starting at index 9 and ending at index 12.
```

И снова все совпадения успешны независимо от регистра.

Встроенные флаговые выражения, соответствующие публично доступным полям `Pattern`, представлены в
следующей таблице:

| Константа | Эквивалентное встроенное флаговое выражение |
|-----------|---------------------------------------------|
| `Pattern.CANON_EQ` | нет |
| `Pattern.CASE_INSENSITIVE` | `(?i)` |
| `Pattern.COMMENTS` | `(?x)` |
| `Pattern.MULTILINE` | `(?m)` |
| `Pattern.DOTALL` | `(?s)` |
| `Pattern.LITERAL` | нет |
| `Pattern.UNICODE_CASE` | `(?u)` |
| `Pattern.UNIX_LINES` | `(?d)` |

### Использование метода `matches(String,CharSequence)`

Класс `Pattern` определяет удобный метод
[`matches`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#matches-java.lang.String-java.lang.CharSequence-),
позволяющий быстро проверить, присутствует ли шаблон в заданной входной строке. Как и все публичные
статические методы, `matches` следует вызывать по имени класса, например `Pattern.matches("\\d","1");`.
В этом примере метод возвращает `true`, потому что цифра «1» совпадает с регулярным выражением `\d`.

### Использование метода `split(String)`

Метод [`split`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#split-java.lang.CharSequence-) —
отличный инструмент для сбора текста, лежащего по обе стороны от совпавшего шаблона. Как показано ниже
в `SplitDemo.java`, метод `split` мог бы извлечь слова «`one two three four five`» из строки
«`one:two:three:four:five`»:

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class SplitDemo {

    private static final String REGEX = ":";
    private static final String INPUT =
        "one:two:three:four:five";
    
    public static void main(String[] args) {
        Pattern p = Pattern.compile(REGEX);
        String[] items = p.split(INPUT);
        for(String s : items) {
            System.out.println(s);
        }
    }
}
```

ВЫВОД:

```
one
two
three
four
five
```

Для простоты мы сопоставили строковый литерал — двоеточие (`:`) — вместо сложного регулярного
выражения. Поскольку мы по-прежнему используем объекты `Pattern` и `Matcher`, можно применять `split`
для получения текста, лежащего по обе стороны от любого регулярного выражения. Вот тот же пример,
`SplitDemo2.java`, изменённый для разбиения по цифрам:

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class SplitDemo2 {

    private static final String REGEX = "\\d";
    private static final String INPUT =
        "one9two4three7four1five";

    public static void main(String[] args) {
        Pattern p = Pattern.compile(REGEX);
        String[] items = p.split(INPUT);
        for(String s : items) {
            System.out.println(s);
        }
    }
}
```

ВЫВОД:

```
one
two
three
four
five
```

### Прочие служебные методы (Other Utility Methods)

Вам также могут пригодиться следующие методы:

- [`public static String quote(String s)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#quote-java.lang.String-) —
  возвращает буквальный шаблон `String` для заданной строки `String`. Этот метод создаёт `String`,
  который можно использовать для создания `Pattern`, совпадающего со строкой `String s` так, как если
  бы это был буквальный шаблон. Метасимволы или escape-последовательности во входной
  последовательности не получат специального значения.
- [`public String toString()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html#toString--) —
  возвращает строковое представление этого шаблона. Это регулярное выражение, из которого был
  скомпилирован шаблон.

### Аналоги методов Pattern в `java.lang.String`

Поддержка регулярных выражений также существует в `java.lang.String` через несколько методов,
имитирующих поведение `java.util.regex.Pattern`. Для удобства ниже приведены ключевые выдержки из их
API.

- [`public boolean matches(String regex)`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#matches-java.lang.String-):
  сообщает, совпадает ли эта строка с заданным регулярным выражением. Вызов этого метода вида
  `str.matches(regex)` даёт точно такой же результат, как и выражение `Pattern.matches(regex, str)`.
- [`public String[] split(String regex, int limit)`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#split-java.lang.String-int-):
  разбивает эту строку вокруг совпадений с заданным регулярным выражением. Вызов этого метода вида
  `str.split(regex, n)` даёт тот же результат, что и выражение `Pattern.compile(regex).split(str, n)`.
- [`public String[] split(String regex)`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#split-java.lang.String-):
  разбивает эту строку вокруг совпадений с заданным регулярным выражением. Этот метод работает так же,
  как если бы вы вызвали двухаргументный метод split с заданным выражением и аргументом limit, равным
  нулю. Завершающие пустые строки не включаются в результирующий массив.

Существует также метод replace, заменяющий одну `CharSequence` на другую:

- [`public String replace(CharSequence target,CharSequence replacement)`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#replace-java.lang.CharSequence-java.lang.CharSequence-):
  заменяет каждую подстроку этой строки, совпадающую с буквальной целевой последовательностью, на
  заданную буквальную заменяющую последовательность. Замена идёт от начала строки к концу: например,
  замена «aa» на «b» в строке «aaa» даст «ba», а не «ab».

## Методы класса Matcher (Methods of the Matcher Class)

Этот раздел описывает несколько дополнительных полезных методов класса `Matcher`. Для удобства
перечисленные ниже методы сгруппированы по функциональности.

### Индексные методы (Index Methods)

**Индексные методы** (*index methods*) дают полезные значения индексов, показывающие точно, где во
входной строке было найдено совпадение:

- [`public int start()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#start--):
  возвращает начальный индекс предыдущего совпадения.
- [`public int start(int group)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#start-int-):
  возвращает начальный индекс подпоследовательности, захваченной заданной группой при предыдущей
  операции сопоставления.
- [`public int end()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#end--):
  возвращает смещение после последнего совпавшего символа.
- [`public int end(int group)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#end-int-):
  возвращает смещение после последнего символа подпоследовательности, захваченной заданной группой при
  предыдущей операции сопоставления.

### Изучающие методы (Study Methods)

**Изучающие методы** (*study methods*) просматривают входную строку и возвращают `boolean`,
указывающий, найден ли шаблон.

- [`public boolean lookingAt()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#lookingAt--):
  пытается сопоставить входную последовательность с шаблоном, начиная с начала региона.
- [`public boolean find()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#find--):
  пытается найти следующую подпоследовательность входной последовательности, совпадающую с шаблоном.
- [`public boolean find(int start)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#find-int-):
  сбрасывает этот сопоставитель и затем пытается найти следующую подпоследовательность входной
  последовательности, совпадающую с шаблоном, начиная с заданного индекса.
- [`public boolean matches()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#matches--):
  пытается сопоставить весь регион с шаблоном.

### Методы замены (Replacement Methods)

**Методы замены** (*replacement methods*) — это полезные методы для замены текста во входной строке.

- [`public Matcher appendReplacement(StringBuffer sb, String replacement)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#appendReplacement-java.lang.StringBuffer-java.lang.String-):
  реализует нетерминальный шаг «добавить-и-заменить».
- [`public StringBuffer appendTail(StringBuffer sb)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#appendTail-java.lang.StringBuffer-):
  реализует терминальный шаг «добавить-и-заменить».
- [`public String replaceAll(String replacement)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#replaceAll-java.lang.String-):
  заменяет каждую подпоследовательность входной последовательности, совпадающую с шаблоном, на
  заданную заменяющую строку.
- [`public String replaceFirst(String replacement)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#replaceFirst-java.lang.String-):
  заменяет первую подпоследовательность входной последовательности, совпадающую с шаблоном, на
  заданную заменяющую строку.
- [`public static String quoteReplacement(String s)`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html#quoteReplacement-java.lang.String-):
  возвращает буквальную заменяющую строку `String` для заданной строки `String`. Этот метод создаёт
  `String`, который будет работать как буквальная замена `s` в методе `appendReplacement` класса
  `Matcher`. Создаваемая `String` совпадёт с последовательностью символов в `s`, трактуемой как
  буквальная последовательность. Слешам (`'\'`) и знакам доллара (`'$'`) не будет придано специального
  значения.

### Использование методов `start` и `end`

Вот пример `MatcherDemo.java`, который подсчитывает, сколько раз слово «dog» встречается во входной
строке.

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class MatcherDemo {

    private static final String REGEX =
        "\\bdog\\b";
    private static final String INPUT =
        "dog dog dog doggie dogg";

    public static void main(String[] args) {
       Pattern p = Pattern.compile(REGEX);
       //  получаем объект matcher
       Matcher m = p.matcher(INPUT);
       int count = 0;
       while(m.find()) {
           count++;
           System.out.println("Match number "
                              + count);
           System.out.println("start(): "
                              + m.start());
           System.out.println("end(): "
                              + m.end());
      }
   }
}
```

**ВЫВОД:**

```
Match number 1
start(): 0
end(): 3
Match number 2
start(): 4
end(): 7
Match number 3
start(): 8
end(): 11
```

Как видите, этот пример использует границы слов, чтобы гарантировать, что буквы `"d" "o" "g"` не
являются просто подстрокой в более длинном слове. Он также даёт полезную информацию о том, где во
входной строке произошло совпадение. Метод `start` возвращает начальный индекс подпоследовательности,
захваченной заданной группой при предыдущей операции сопоставления, а `end` возвращает индекс
последнего совпавшего символа плюс один.

### Использование методов `matches` и `lookingAt`

Методы `matches` и `lookingAt` оба пытаются сопоставить входную последовательность с шаблоном.
Разница, однако, в том, что `matches` требует совпадения всей входной последовательности, а
`lookingAt` — нет. Оба метода всегда начинают с начала входной строки. Вот полный код
`MatchesLooking.java`:

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class MatchesLooking {

    private static final String REGEX = "foo";
    private static final String INPUT =
        "fooooooooooooooooo";
    private static Pattern pattern;
    private static Matcher matcher;

    public static void main(String[] args) {
   
        // Инициализация
        pattern = Pattern.compile(REGEX);
        matcher = pattern.matcher(INPUT);

        System.out.println("Current REGEX is: "
                           + REGEX);
        System.out.println("Current INPUT is: "
                           + INPUT);

        System.out.println("lookingAt(): "
            + matcher.lookingAt());
        System.out.println("matches(): "
            + matcher.matches());
    }
}
```

**ВЫВОД:**

```
Current REGEX is: foo
Current INPUT is: fooooooooooooooooo
lookingAt(): true
matches(): false
```

### Использование `replaceFirst(String)` и `replaceAll(String)`

Методы `replaceFirst` и `replaceAll` заменяют текст, совпадающий с заданным регулярным выражением.
Как следует из их названий, `replaceFirst` заменяет первое вхождение, а `replaceAll` — все вхождения.
Вот код `ReplaceDemo.java`:

```java
import java.util.regex.Pattern; 
import java.util.regex.Matcher;

public class ReplaceDemo {
 
    private static String REGEX = "dog";
    private static String INPUT =
        "The dog says meow. All dogs say meow.";
    private static String REPLACE = "cat";
 
    public static void main(String[] args) {
        Pattern p = Pattern.compile(REGEX);
        // получаем объект matcher
        Matcher m = p.matcher(INPUT);
        INPUT = m.replaceAll(REPLACE);
        System.out.println(INPUT);
    }
}
```

**ВЫВОД:** `The cat says meow. All cats say meow.`

В этой первой версии все вхождения `dog` заменены на `cat`. Но зачем останавливаться на этом? Вместо
замены простого литерала вроде `dog` можно заменять текст, совпадающий с *любым* регулярным
выражением. API этого метода гласит, что «при регулярном выражении `a*b`, входной строке
`aabfooaabfooabfoob` и заменяющей строке `-` вызов этого метода для сопоставителя данного выражения
дал бы строку `-foo-foo-foo-`».

Вот код `ReplaceDemo2.java`:

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;
 
public class ReplaceDemo2 {
 
    private static String REGEX = "a*b";
    private static String INPUT =
        "aabfooaabfooabfoob";
    private static String REPLACE = "-";
 
    public static void main(String[] args) {
        Pattern p = Pattern.compile(REGEX);
        // получаем объект matcher
        Matcher m = p.matcher(INPUT);
        INPUT = m.replaceAll(REPLACE);
        System.out.println(INPUT);
    }
}
```

**ВЫВОД:** `-foo-foo-foo-`

Чтобы заменить только первое вхождение шаблона, просто вызовите `replaceFirst` вместо `replaceAll`.
Он принимает тот же параметр.

### Использование `appendReplacement(StringBuffer,String)` и `appendTail(StringBuffer)`

Класс `Matcher` также предоставляет методы `appendReplacement` и `appendTail` для замены текста.
Следующий пример, `RegexDemo.java`, использует эти два метода, чтобы достичь того же эффекта, что и
`replaceAll`.

```java
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class RegexDemo {
 
    private static String REGEX = "a*b";
    private static String INPUT = "aabfooaabfooabfoob";
    private static String REPLACE = "-";
 
    public static void main(String[] args) {
        Pattern p = Pattern.compile(REGEX);
        Matcher m = p.matcher(INPUT); // получаем объект matcher
        StringBuffer sb = new StringBuffer();
        while(m.find()){
            m.appendReplacement(sb,REPLACE);
        }
        m.appendTail(sb);
        System.out.println(sb.toString());
    }
}
```

**ВЫВОД:** `-foo-foo-foo-`

### Аналоги методов Matcher в `java.lang.String`

Для удобства класс `String` также имитирует пару методов `Matcher`:

- [`public String replaceFirst(String regex, String replacement)`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#replaceFirst-java.lang.String-java.lang.String-):
  заменяет первую подстроку этой строки, совпадающую с заданным регулярным выражением, на заданную
  замену. Вызов этого метода вида `str.replaceFirst(regex, repl)` даёт точно такой же результат, как
  и выражение `Pattern.compile(regex).matcher(str).replaceFirst(repl)`.
- [`public String replaceAll(String regex, String replacement)`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#replaceAll-java.lang.String-java.lang.String-):
  заменяет каждую подстроку этой строки, совпадающую с заданным регулярным выражением, на заданную
  замену. Вызов этого метода вида `str.replaceAll(regex, repl)` даёт точно такой же результат, как и
  выражение `Pattern.compile(regex).matcher(str).replaceAll(repl)`.

## Методы класса PatternSyntaxException (Methods of the PatternSyntaxException Class)

[`PatternSyntaxException`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html) —
это непроверяемое исключение, сигнализирующее о синтаксической ошибке в шаблоне регулярного
выражения. Класс `PatternSyntaxException` предоставляет следующие методы, помогающие определить, что
пошло не так:

- [`public String getDescription()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html#getDescription--):
  получает описание ошибки.
- [`public int getIndex()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html#getIndex--):
  получает индекс ошибки.
- [`public String getPattern()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html#getPattern--):
  получает ошибочный шаблон регулярного выражения.
- [`public String getMessage()`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html#getMessage--):
  возвращает многострочную строку, содержащую описание синтаксической ошибки и её индекс, ошибочный
  шаблон регулярного выражения и визуальное указание индекса ошибки внутри шаблона.

Следующий исходный код, `RegexTestHarness2.java`, обновляет наш тестовый стенд для проверки
неправильно сформированных регулярных выражений:

```java
import java.io.Console;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
import java.util.regex.PatternSyntaxException;

public class RegexTestHarness2 {

    public static void main(String[] args){
        Pattern pattern = null;
        Matcher matcher = null;

        Console console = System.console();
        if (console == null) {
            System.err.println("No console.");
            System.exit(1);
        }
        while (true) {
            try{
                pattern = 
                Pattern.compile(console.readLine("%nEnter your regex: "));

                matcher = 
                pattern.matcher(console.readLine("Enter input string to search: "));
            }
            catch(PatternSyntaxException pse){
                console.format("There is a problem" +
                               " with the regular expression!%n");
                console.format("The pattern in question is: %s%n",
                               pse.getPattern());
                console.format("The description is: %s%n",
                               pse.getDescription());
                console.format("The message is: %s%n",
                               pse.getMessage());
                console.format("The index is: %s%n",
                               pse.getIndex());
                System.exit(0);
            }
            boolean found = false;
            while (matcher.find()) {
                console.format("I found the text" +
                    " \"%s\" starting at " +
                    "index %d and ending at index %d.%n",
                    matcher.group(),
                    matcher.start(),
                    matcher.end());
                found = true;
            }
            if(!found){
                console.format("No match found.%n");
            }
        }
    }
}
```

Чтобы провести этот тест, введите `?i)foo` в качестве регулярного выражения. Эта ошибка — типичный
сценарий, когда программист забыл открывающую круглую скобку во встроенном флаговом выражении `(?i)`.
В этом случае будут получены следующие результаты:

```
Enter your regex: ?i)
There is a problem with the regular expression!
The pattern in question is: ?i)
The description is: Dangling meta character '?'
The message is: Dangling meta character '?' near index 0
?i)
^
The index is: 0
```

Из этого вывода видно, что синтаксическая ошибка — это «висячий» метасимвол (знак вопроса) на индексе
0. Виновата отсутствующая открывающая круглая скобка.

## Поддержка Unicode (Unicode Support)

Начиная с выпуска JDK 7, сопоставление с шаблоном для регулярных выражений получило расширенную
функциональность с поддержкой Unicode 6.0.

### Сопоставление конкретной кодовой точки (Matching a Specific Code Point)

Конкретную кодовую точку Unicode (*code point*) можно сопоставить, используя escape-последовательность
вида `￿`, где `FFFF` — шестнадцатеричное значение кодовой точки, которую нужно сопоставить.
Например, `東` совпадает с китайским иероглифом (хань) «восток».

Кроме того, кодовую точку можно задать с помощью шестнадцатеричной нотации в стиле Perl, `\x{...}`.
Например:

```java
String hexPattern = "\\x{" + Integer.toHexString(codePoint) + "}";
```

### Свойства символов Unicode (Unicode Character Properties)

Каждый символ Unicode, помимо своего значения, имеет определённые атрибуты, или свойства. Один символ,
принадлежащий к определённой категории, можно сопоставить выражением `\p{prop}`. Один символ, *не*
принадлежащий к определённой категории, можно сопоставить выражением `\P{prop}`.

Три поддерживаемых типа свойств — это письменности (*scripts*), блоки (*blocks*) и «общая» категория
(*general category*).

#### Письменности (Scripts)

Чтобы определить, принадлежит ли кодовая точка к конкретной письменности, можно использовать либо
ключевое слово `script`, либо короткую форму `sc`, например `\p{script=Hiragana}`. Кроме того, можно
предварить имя письменности строкой `Is`, например `\p{IsHiragana}`.

Допустимые имена письменностей, поддерживаемые `Pattern`, — это те, которые принимает
`UnicodeScript.forName()`.

#### Блоки (Blocks)

Блок можно задать с помощью ключевого слова `block` или короткой формы `blk`, например
`\p{block=Mongolian}`. Кроме того, можно предварить имя блока строкой `In`, например
`\p{InMongolian}`.

Допустимые имена блоков, поддерживаемые `Pattern`, — это те, которые принимает
`UnicodeBlock.forName()`.

#### Общая категория (General Category)

Категории можно задавать с необязательным префиксом `Is`. Например, `IsL` сопоставляет категорию букв
Unicode. Категории можно также задавать с помощью ключевого слова `general_category` или короткой
формы `gc`. Например, прописную букву можно сопоставить с помощью `general_category=Lu` или `gc=Lu`.

Поддерживаемые категории — это категории стандарта Unicode в версии, заданной классом `Character`.

## Дополнительные ресурсы (Additional Resources)

Теперь, когда вы завершили этот урок по регулярным выражениям, вы, вероятно, обнаружите, что вашими
основными справочниками станут документация API для следующих классов:
[`Pattern`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html),
[`Matcher`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Matcher.html) и
[`PatternSyntaxException`](https://docs.oracle.com/javase/8/docs/api/java/util/regex/PatternSyntaxException.html).

Для более точного описания поведения конструкций регулярных выражений рекомендуется прочитать книгу
[*Mastering Regular Expressions*](http://www.amazon.com/exec/obidos/ASIN/0596002890/javasoftsunmicroA/)
за авторством Джеффри Э. Ф. Фридла (Jeffrey E. F. Friedl).

## Источник

- [Regular Expressions (Lesson index)](https://docs.oracle.com/javase/tutorial/essential/regex/index.html) — официальное руководство Oracle.
- [Introduction](https://docs.oracle.com/javase/tutorial/essential/regex/intro.html)
- [Test Harness](https://docs.oracle.com/javase/tutorial/essential/regex/test_harness.html)
- [String Literals](https://docs.oracle.com/javase/tutorial/essential/regex/literals.html)
- [Character Classes](https://docs.oracle.com/javase/tutorial/essential/regex/char_classes.html)
- [Predefined Character Classes](https://docs.oracle.com/javase/tutorial/essential/regex/pre_char_classes.html)
- [Quantifiers](https://docs.oracle.com/javase/tutorial/essential/regex/quant.html)
- [Capturing Groups](https://docs.oracle.com/javase/tutorial/essential/regex/groups.html)
- [Boundary Matchers](https://docs.oracle.com/javase/tutorial/essential/regex/bounds.html)
- [Methods of the Pattern Class](https://docs.oracle.com/javase/tutorial/essential/regex/pattern.html)
- [Methods of the Matcher Class](https://docs.oracle.com/javase/tutorial/essential/regex/matcher.html)
- [Methods of the PatternSyntaxException Class](https://docs.oracle.com/javase/tutorial/essential/regex/pse.html)
- [Unicode Support](https://docs.oracle.com/javase/tutorial/essential/regex/unicode.html)
- [Additional Resources](https://docs.oracle.com/javase/tutorial/essential/regex/resources.html)
