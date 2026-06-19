# Урок 3. Массивы и перечисления (рефлексия)

**Трейл:** Reflection · **Оригинал:** [Arrays and Enumerated Types](https://docs.oracle.com/javase/tutorial/reflect/special/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

С точки зрения виртуальной машины Java (Java virtual machine) массивы (arrays) и перечислимые
типы (enumerated types, или enum'ы) — это просто классы. Многие методы класса `Class` применимы
и к ним. Рефлексия (reflection) предоставляет несколько специальных API для массивов и
перечислений. В этом уроке на серии примеров кода показано, как отличить такие объекты от прочих
классов и как с ними работать. Заодно разбираются и различные ошибки.

## Массивы

У массива есть тип компонентов (component type) и длина (length), причём длина не входит в тип.
Массивами можно манипулировать как целиком, так и покомпонентно. Для покомпонентной работы
рефлексия предоставляет класс `java.lang.reflect.Array`.

Подтемы:

- [Определение типов массивов](#определение-типов-массивов) — как узнать, является ли член
  класса полем типа массива.
- [Создание новых массивов](#создание-новых-массивов) — как создавать новые экземпляры массивов
  с простыми и сложными типами компонентов.
- [Получение и установка массивов и их компонентов](#получение-и-установка-массивов-и-их-компонентов)
  — как обращаться к полям типа массива и к отдельным элементам массива.
- [Устранение неполадок (массивы)](#устранение-неполадок-массивы) — типичные ошибки и
  заблуждения при программировании.

### Определение типов массивов

Типы массивов можно распознать вызовом
[`Class.isArray()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#isArray--).
Чтобы получить объект [`Class`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html),
воспользуйтесь одним из методов, описанных в разделе
[Получение объектов Class](https://docs.oracle.com/javase/tutorial/reflect/class/classNew.html)
этого трейла.

Пример `ArrayFind` находит в указанном классе поля, имеющие тип массива, и сообщает тип
компонентов для каждого из них.

```java
import java.lang.reflect.Field;
import java.lang.reflect.Type;
import static java.lang.System.out;

public class ArrayFind {
    public static void main(String... args) {
	boolean found = false;
 	try {
	    Class<?> cls = Class.forName(args[0]);
	    Field[] flds = cls.getDeclaredFields();
	    for (Field f : flds) {
 		Class<?> c = f.getType();
		if (c.isArray()) {
		    found = true;
		    out.format("%s%n"
                               + "           Field: %s%n"
			       + "            Type: %s%n"
			       + "  Component Type: %s%n",
			       f, f.getName(), c, c.getComponentType());
		}
	    }
	    if (!found) {
		out.format("No array fields%n");
	    }

        // в рабочем коде это исключение следует обрабатывать аккуратнее
 	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

Синтаксис значения, возвращаемого методами `Class.get*Type()`, описан в документации
[`Class.getName()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getName--).
Количество символов «`[`» в начале имени типа указывает на число измерений (то есть глубину
вложенности) массива.

Ниже приведены образцы вывода. Ввод пользователя выделен курсивом. Массив примитивного типа
`byte`:

```
$ java ArrayFind java.nio.ByteBuffer
final byte[] java.nio.ByteBuffer.hb
           Field: hb
            Type: class [B
  Component Type: byte
```

Массив ссылочного типа
[`StackTraceElement`](https://docs.oracle.com/javase/8/docs/api/java/lang/StackTraceElement.html):

```
$ java ArrayFind java.lang.Throwable
private java.lang.StackTraceElement[] java.lang.Throwable.stackTrace
           Field: stackTrace
            Type: class [Ljava.lang.StackTraceElement;
  Component Type: class java.lang.StackTraceElement
```

`predefined` — одномерный массив ссылочного типа
[`java.awt.Cursor`](https://docs.oracle.com/javase/8/docs/api/java/awt/Cursor.html), а
`cursorProperties` — двумерный массив ссылочного типа
[`String`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html):

```
$ java ArrayFind java.awt.Cursor
protected static java.awt.Cursor[] java.awt.Cursor.predefined
           Field: predefined
            Type: class [Ljava.awt.Cursor;
  Component Type: class java.awt.Cursor
static final java.lang.String[][] java.awt.Cursor.cursorProperties
           Field: cursorProperties
            Type: class [[Ljava.lang.String;
  Component Type: class [Ljava.lang.String;
```

### Создание новых массивов

Как и в нерефлективном коде, рефлексия позволяет динамически создавать массивы произвольного типа
и размерности через `java.lang.reflect.Array.newInstance()`. Рассмотрим `ArrayCreator` —
простейший интерпретатор, способный динамически создавать массивы. Разбираемый им синтаксис
таков:

```
fully_qualified_class_name variable_name[] = 
     { val1, val2, val3, ... }
```

Предполагается, что `fully_qualified_class_name` (полностью квалифицированное имя класса)
обозначает класс, у которого есть конструктор с единственным аргументом типа `String`. Размер
массива определяется числом переданных значений. Следующий пример сконструирует экземпляр массива
типа `fully_qualified_class_name` и заполнит его значениями, заданными `val1`, `val2` и т. д.
(Этот пример предполагает знакомство с `Class.getConstructor()` и
`java.lang.reflect.Constructor.newInstance()`. Обсуждение API рефлексии для `Constructor`
см. в разделе «Создание новых экземпляров классов» этого трейла.)

```java
import java.lang.reflect.Array;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
import java.util.Arrays;
import static java.lang.System.out;

public class ArrayCreator {
    private static String s = "java.math.BigInteger bi[] = { 123, 234, 345 }";
    private static Pattern p = Pattern.compile("^\\s*(\\S+)\\s*\\w+\\[\\].*\\{\\s*([^}]+)\\s*\\}");

    public static void main(String... args) {
        Matcher m = p.matcher(s);

        if (m.find()) {
            String cName = m.group(1);
            String[] cVals = m.group(2).split("[\\s,]+");
            int n = cVals.length;

            try {
                Class<?> c = Class.forName(cName);
                Object o = Array.newInstance(c, n);
                for (int i = 0; i < n; i++) {
                    String v = cVals[i];
                    Constructor ctor = c.getConstructor(String.class);
                    Object val = ctor.newInstance(v);
                    Array.set(o, i, val);
                }

                Object[] oo = (Object[])o;
                out.format("%s[] = %s%n", cName, Arrays.toString(oo));

            // в рабочем коде эти исключения следует обрабатывать аккуратнее
            } catch (ClassNotFoundException x) {
                x.printStackTrace();
            } catch (NoSuchMethodException x) {
                x.printStackTrace();
            } catch (IllegalAccessException x) {
                x.printStackTrace();
            } catch (InstantiationException x) {
                x.printStackTrace();
            } catch (InvocationTargetException x) {
                x.printStackTrace();
            }
        }
    }
}
```

```
$ java ArrayCreator
java.math.BigInteger [] = [123, 234, 345]
```

Пример выше показывает один из случаев, когда создание массива через рефлексию может быть
желательным, — а именно когда тип компонентов неизвестен до момента выполнения. Здесь код
использует `Class.forName()`, чтобы получить класс нужного типа компонентов, а затем вызывает
конкретный конструктор для инициализации каждого компонента массива перед установкой
соответствующего значения массива.

### Получение и установка массивов и их компонентов

Как и в нерефлективном коде, поле типа массива можно установить или прочитать целиком либо
покомпонентно. Чтобы установить весь массив сразу, используйте
`java.lang.reflect.Field.set(Object obj, Object value)`. Чтобы прочитать весь массив, используйте
`Field.get(Object)`. Отдельные компоненты можно устанавливать или читать методами класса
`java.lang.reflect.Array`.

Класс `Array` предоставляет методы вида `set_Foo_()` и `get_Foo_()` для установки и чтения
компонентов любого примитивного типа. Например, компонент массива `int` можно установить методом
`Array.setInt(Object array, int index, int value)`, а прочитать — методом
`Array.getInt(Object array, int index)`.

Эти методы поддерживают автоматическое расширение (widening) типов данных. Поэтому метод
`Array.getShort()` можно использовать для установки значений массива `int`, так как 16-битный
`short` может быть расширен до 32-битного `int` без потери данных; с другой стороны, вызов
`Array.setLong()` для массива `int` приведёт к выбросу `IllegalArgumentException`, поскольку
64-битный `long` нельзя сузить (narrow) для хранения в 32-битном `int` без потери информации.
Это верно независимо от того, могли бы фактически передаваемые значения быть точно представлены
в целевом типе данных. Полное обсуждение расширяющих и сужающих преобразований содержится в
спецификации языка Java (The Java Language Specification, Java SE 7 Edition), разделы «Widening
Primitive Conversion» (Расширяющее преобразование примитивов) и «Narrowing Primitive Conversion»
(Сужающее преобразование примитивов).

Компоненты массивов ссылочных типов (включая массивы массивов) устанавливаются и читаются методами
`Array.set(Object array, int index, int value)` и `Array.get(Object array, int index)`.

#### Установка поля типа массив

Пример `GrowBufferedReader` показывает, как заменить значение поля типа массив. В данном случае
код заменяет внутренний (backing) массив объекта `java.io.BufferedReader` на больший по размеру.
(Предполагается, что исходный `BufferedReader` создаётся в коде, который нельзя изменить; иначе
было бы тривиально просто воспользоваться альтернативным конструктором
`BufferedReader(java.io.Reader in, int size)`, принимающим размер входного буфера.)

```java
import java.io.BufferedReader;
import java.io.CharArrayReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.Arrays;
import static java.lang.System.out;

public class GrowBufferedReader {
    private static final int srcBufSize = 10 * 1024;
    private static char[] src = new char[srcBufSize];
    static {
	src[srcBufSize - 1] = 'x';
    }
    private static CharArrayReader car = new CharArrayReader(src);

    public static void main(String... args) {
	try {
	    BufferedReader br = new BufferedReader(car);

	    Class<?> c = br.getClass();
	    Field f = c.getDeclaredField("cb");

	    // cb — приватное поле
	    f.setAccessible(true);
	    char[] cbVal = char[].class.cast(f.get(br));

	    char[] newVal = Arrays.copyOf(cbVal, cbVal.length * 2);
	    if (args.length > 0 && args[0].equals("grow"))
		f.set(br, newVal);

	    for (int i = 0; i < srcBufSize; i++)
		br.read();

	    // проверяем, используется ли новый внутренний массив
	    if (newVal[srcBufSize - 1] == src[srcBufSize - 1])
		out.format("Using new backing array, size=%d%n", newVal.length);
	    else
		out.format("Using original backing array, size=%d%n", cbVal.length);

        // в рабочем коде эти исключения следует обрабатывать аккуратнее
	} catch (FileNotFoundException x) {
	    x.printStackTrace();
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (IOException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java GrowBufferedReader grow
Using new backing array, size=16384
$ java GrowBufferedReader
Using original backing array, size=8192
```

Обратите внимание, что в примере выше используется вспомогательный метод для массивов
`java.util.Arrays.copyOf()`. Класс `java.util.Arrays` содержит множество методов, удобных при
работе с массивами.

#### Доступ к элементам многомерного массива

Многомерные массивы — это просто вложенные массивы. Двумерный массив — это массив массивов.
Трёхмерный массив — это массив двумерных массивов и так далее. Пример `CreateMatrix` показывает,
как создать и инициализировать многомерный массив с помощью рефлексии.

```java
import java.lang.reflect.Array;
import static java.lang.System.out;

public class CreateMatrix {
    public static void main(String... args) {
        Object matrix = Array.newInstance(int.class, 2, 2);
        Object row0 = Array.get(matrix, 0);
        Object row1 = Array.get(matrix, 1);

        Array.setInt(row0, 0, 1);
        Array.setInt(row0, 1, 2);
        Array.setInt(row1, 0, 3);
        Array.setInt(row1, 1, 4);

        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++)
                out.format("matrix[%d][%d] = %d%n", i, j, ((int[][])matrix)[i][j]);
    }
}
```

```
$ java CreateMatrix
matrix[0][0] = 1
matrix[0][1] = 2
matrix[1][0] = 3
matrix[1][1] = 4
```

Тот же результат можно получить с помощью следующего фрагмента кода:

```java
Object matrix = Array.newInstance(int.class, 2);
Object row0 = Array.newInstance(int.class, 2);
Object row1 = Array.newInstance(int.class, 2);

Array.setInt(row0, 0, 1);
Array.setInt(row0, 1, 2);
Array.setInt(row1, 0, 3);
Array.setInt(row1, 1, 4);

Array.set(matrix, 0, row0);
Array.set(matrix, 1, row1);
```

Метод с переменным числом аргументов `Array.newInstance(Class<?> componentType, int... dimensions)`
предоставляет удобный способ создания многомерных массивов, но компоненты всё равно нужно
инициализировать, исходя из принципа, что многомерные массивы — это вложенные массивы. (Рефлексия
не предоставляет для этой цели методов `get`/`set` с несколькими индексами.)

### Устранение неполадок (массивы)

Следующие примеры демонстрируют типичные ошибки, которые могут возникнуть при работе с массивами.

#### IllegalArgumentException из-за непреобразуемых типов

Пример `ArrayTroubleAgain` сгенерирует `IllegalArgumentException`. Метод `Array.setInt()`
вызывается для установки компонента ссылочного типа `Integer` значением примитивного типа `int`.
В нерефлективном эквиваленте `ary[0] = 1` компилятор преобразовал бы (упаковал, boxing) значение
`1` в ссылочный тип как `new Integer(1)`, чтобы проверка типов приняла этот оператор. При
использовании рефлексии проверка типов происходит только во время выполнения, поэтому возможности
упаковать значение нет.

```java
import java.lang.reflect.Array;
import static java.lang.System.err;

public class ArrayTroubleAgain {
    public static void main(String... args) {
	Integer[] ary = new Integer[2];
	try {
	    Array.setInt(ary, 0, 1);  // IllegalArgumentException

        // в рабочем коде эти исключения следует обрабатывать аккуратнее
	} catch (IllegalArgumentException x) {
	    err.format("Unable to box%n");
	} catch (ArrayIndexOutOfBoundsException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java ArrayTroubleAgain
Unable to box
```

Чтобы устранить это исключение, проблемную строку следует заменить следующим вызовом
`Array.set(Object array, int index, Object value)`:

```java
Array.set(ary, 0, new Integer(1));
```

> **Совет.** При использовании рефлексии для установки или чтения компонента массива у компилятора
> нет возможности выполнить упаковку (boxing). Он может преобразовывать только типы, связанные так,
> как описано в спецификации метода `Class.isAssignableFrom()`. Ожидается, что этот пример завершится
> ошибкой, поскольку `isAssignableFrom()` вернёт `false` в следующей проверке, которую можно
> использовать программно, чтобы убедиться, возможно ли конкретное преобразование:
>
> ```java
> Integer.class.isAssignableFrom(int.class) == false
> ```
>
> Аналогично, автоматическое преобразование из примитивного типа в ссылочный в рефлексии также
> невозможно.
>
> ```java
> int.class.isAssignableFrom(Integer.class) == false
> ```

#### ArrayIndexOutOfBoundsException для пустых массивов

Пример `ArrayTrouble` иллюстрирует ошибку, которая произойдёт при попытке обратиться к элементам
массива нулевой длины:

```java
import java.lang.reflect.Array;
import static java.lang.System.out;

public class ArrayTrouble {
    public static void main(String... args) {
        Object o = Array.newInstance(int.class, 0);
        int[] i = (int[])o;
        int[] j = new int[0];
        out.format("i.length = %d, j.length = %d, args.length = %d%n",
                   i.length, j.length, args.length);
        Array.getInt(o, 0);  // ArrayIndexOutOfBoundsException
    }
}
```

```
$ java ArrayTrouble
i.length = 0, j.length = 0, args.length = 0
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException
        at java.lang.reflect.Array.getInt(Native Method)
        at ArrayTrouble.main(ArrayTrouble.java:11)
```

> **Совет.** Массивы без элементов (пустые массивы) допустимы. В обычном коде они встречаются лишь
> в немногих случаях, но в рефлексии могут возникнуть непреднамеренно. Разумеется, установить или
> прочитать значения пустого массива невозможно, так как будет выброшено
> `ArrayIndexOutOfBoundsException`.

#### IllegalArgumentException при попытке сужения

Пример `ArrayTroubleToo` содержит код, который завершается ошибкой, потому что пытается выполнить
операцию, способную привести к потере данных:

```java
import java.lang.reflect.Array;
import static java.lang.System.out;

public class ArrayTroubleToo {
    public static void main(String... args) {
        Object o = new int[2];
        Array.setShort(o, 0, (short)2);  // расширение, успешно
        Array.setLong(o, 1, 2L);         // сужение, неудача
    }
}
```

```
$ java ArrayTroubleToo
Exception in thread "main" java.lang.IllegalArgumentException: argument type
  mismatch
        at java.lang.reflect.Array.setLong(Native Method)
        at ArrayTroubleToo.main(ArrayTroubleToo.java:9)
```

> **Совет.** Методы `Array.set*()` и `Array.get*()` выполняют автоматическое расширяющее
> преобразование, но выбрасывают `IllegalArgumentException`, если предпринимается попытка сужающего
> преобразования. Полное обсуждение расширяющих и сужающих преобразований см. в спецификации языка
> Java (The Java Language Specification, Java SE 7 Edition), разделы «Widening Primitive Conversion»
> (Расширяющее преобразование примитивов) и «Narrowing Primitive Conversion» (Сужающее
> преобразование примитивов) соответственно.

## Перечислимые типы

Enum'ы в коде рефлексии трактуются практически как обычные классы. Метод `Class.isEnum()` сообщает,
представляет ли объект `Class` перечисление (enum). Метод `Class.getEnumConstants()` извлекает
константы перечисления, определённые в enum'е. Метод `java.lang.reflect.Field.isEnumConstant()`
указывает, является ли поле элементом перечислимого типа.

Подтемы:

- [Исследование перечислений](#исследование-перечислений) — как извлечь константы перечисления и
  любые другие поля, конструкторы и методы.
- [Получение и установка полей перечислимых типов](#получение-и-установка-полей-перечислимых-типов)
  — как устанавливать и читать поля со значением-константой перечисления.
- [Устранение неполадок (перечисления)](#устранение-неполадок-перечисления) — типичные ошибки,
  связанные с перечислениями.

### Исследование перечислений

Рефлексия предоставляет три специфичных для enum'ов API:

**`Class.isEnum()`**
Указывает, представляет ли данный класс перечислимый тип (enum type).

**`Class.getEnumConstants()`**
Извлекает список констант перечисления, определённых в enum'е, в порядке их объявления.

**`java.lang.reflect.Field.isEnumConstant()`**
Указывает, представляет ли данное поле элемент перечислимого типа.

Иногда необходимо динамически получить список констант перечисления; в нерефлективном коде это
делается вызовом неявно объявленного статического метода `values()` у перечисления. Если экземпляр
enum-типа недоступен, единственный способ получить список возможных значений — вызвать
`Class.getEnumConstants()`, поскольку создать экземпляр enum-типа невозможно.

Имея полностью квалифицированное имя, пример `EnumConstants` показывает, как извлечь упорядоченный
список констант перечисления с помощью `Class.getEnumConstants()`.

```java
import java.util.Arrays;
import static java.lang.System.out;

enum Eon { HADEAN, ARCHAEAN, PROTEROZOIC, PHANEROZOIC }

public class EnumConstants {
    public static void main(String... args) {
	try {
	    Class<?> c = (args.length == 0 ? Eon.class : Class.forName(args[0]));
	    out.format("Enum name:  %s%nEnum constants:  %s%n",
		       c.getName(), Arrays.asList(c.getEnumConstants()));
	    if (c == Eon.class)
		out.format("  Eon.values():  %s%n",
			   Arrays.asList(Eon.values()));

        // в рабочем коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

Ниже приведены образцы вывода. Ввод пользователя выделен курсивом.

```
$ java EnumConstants java.lang.annotation.RetentionPolicy
Enum name:  java.lang.annotation.RetentionPolicy
Enum constants:  [SOURCE, CLASS, RUNTIME]

$ java EnumConstants java.util.concurrent.TimeUnit
Enum name:  java.util.concurrent.TimeUnit
Enum constants:  [NANOSECONDS, MICROSECONDS, 
                  MILLISECONDS, SECONDS, 
                  MINUTES, HOURS, DAYS]
```

Этот пример также показывает, что значение, возвращаемое `Class.getEnumConstants()`, идентично
значению, возвращаемому вызовом `values()` у enum-типа.

```
$ java EnumConstants
Enum name:  Eon
Enum constants:  [HADEAN, ARCHAEAN, 
                  PROTEROZOIC, PHANEROZOIC]
Eon.values():  [HADEAN, ARCHAEAN, 
                PROTEROZOIC, PHANEROZOIC]
```

Поскольку перечисления — это классы, прочую информацию можно получить теми же API рефлексии,
которые описаны в разделах «Поля» (Fields), «Методы» (Methods) и «Конструкторы» (Constructors)
этого трейла. Код `EnumSpy` иллюстрирует, как с помощью этих API получить дополнительные сведения
об объявлении enum'а. Пример использует `Class.isEnum()`, чтобы ограничить набор исследуемых
классов. Он также использует `Field.isEnumConstant()`, чтобы отличить константы перечисления от
прочих полей в объявлении enum'а (не все поля являются константами перечисления).

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Member;
import java.util.List;
import java.util.ArrayList;
import static java.lang.System.out;

public class EnumSpy {
    private static final String fmt = "  %11s:  %s %s%n";

    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    if (!c.isEnum()) {
		out.format("%s is not an enum type%n", c);
		return;
	    }
	    out.format("Class:  %s%n", c);

	    Field[] flds = c.getDeclaredFields();
	    List<Field> cst = new ArrayList<Field>();  // константы перечисления
	    List<Field> mbr = new ArrayList<Field>();  // обычные поля-члены
	    for (Field f : flds) {
		if (f.isEnumConstant())
		    cst.add(f);
		else
		    mbr.add(f);
	    }
	    if (!cst.isEmpty())
		print(cst, "Constant");
	    if (!mbr.isEmpty())
		print(mbr, "Field");

	    Constructor[] ctors = c.getDeclaredConstructors();
	    for (Constructor ctor : ctors) {
		out.format(fmt, "Constructor", ctor.toGenericString(),
			   synthetic(ctor));
	    }

	    Method[] mths = c.getDeclaredMethods();
	    for (Method m : mths) {
		out.format(fmt, "Method", m.toGenericString(),
			   synthetic(m));
	    }

        // в рабочем коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }

    private static void print(List<Field> lst, String s) {
	for (Field f : lst) {
 	    out.format(fmt, s, f.toGenericString(), synthetic(f));
	}
    }

    private static String synthetic(Member m) {
	return (m.isSynthetic() ? "[ synthetic ]" : "");
    }
}
```

```
$ java EnumSpy java.lang.annotation.RetentionPolicy
Class:  class java.lang.annotation.RetentionPolicy
     Constant:  public static final java.lang.annotation.RetentionPolicy
                  java.lang.annotation.RetentionPolicy.SOURCE 
     Constant:  public static final java.lang.annotation.RetentionPolicy
                  java.lang.annotation.RetentionPolicy.CLASS 
     Constant:  public static final java.lang.annotation.RetentionPolicy 
                  java.lang.annotation.RetentionPolicy.RUNTIME 
        Field:  private static final java.lang.annotation.RetentionPolicy[] 
                  java.lang.annotation.RetentionPolicy. [ synthetic ]
  Constructor:  private java.lang.annotation.RetentionPolicy() 
       Method:  public static java.lang.annotation.RetentionPolicy[]
                  java.lang.annotation.RetentionPolicy.values() 
       Method:  public static java.lang.annotation.RetentionPolicy
                  java.lang.annotation.RetentionPolicy.valueOf(java.lang.String) 
```

Вывод показывает, что объявление `java.lang.annotation.RetentionPolicy` содержит только три
константы перечисления. Константы перечисления представлены как поля `public static final`. Поле,
конструктор и методы сгенерированы компилятором. Поле `$VALUES` связано с реализацией метода
`values()`.

> **Примечание.** По разным причинам, включая поддержку эволюции enum-типа, порядок объявления
> констант перечисления важен. Методы `Class.getFields()` и `Class.getDeclaredFields()` не
> гарантируют, что порядок возвращаемых значений совпадает с порядком в исходном коде объявления.
> Если приложению нужен порядок, используйте `Class.getEnumConstants()`.

Вывод для `java.util.concurrent.TimeUnit` показывает, что возможны и гораздо более сложные enum'ы.
Этот класс включает несколько методов, а также дополнительные поля, объявленные как `static final`,
которые не являются константами перечисления.

```
$ java EnumSpy java.util.concurrent.TimeUnit
Class:  class java.util.concurrent.TimeUnit
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.NANOSECONDS
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.MICROSECONDS
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.MILLISECONDS
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.SECONDS
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.MINUTES
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.HOURS
     Constant:  public static final java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.DAYS
        Field:  static final long java.util.concurrent.TimeUnit.C0
        Field:  static final long java.util.concurrent.TimeUnit.C1
        Field:  static final long java.util.concurrent.TimeUnit.C2
        Field:  static final long java.util.concurrent.TimeUnit.C3
        Field:  static final long java.util.concurrent.TimeUnit.C4
        Field:  static final long java.util.concurrent.TimeUnit.C5
        Field:  static final long java.util.concurrent.TimeUnit.C6
        Field:  static final long java.util.concurrent.TimeUnit.MAX
        Field:  private static final java.util.concurrent.TimeUnit[] 
                  java.util.concurrent.TimeUnit. [ synthetic ]
  Constructor:  private java.util.concurrent.TimeUnit()
  Constructor:  java.util.concurrent.TimeUnit
                  (java.lang.String,int,java.util.concurrent.TimeUnit)
                  [ synthetic ]
       Method:  public static java.util.concurrent.TimeUnit
                  java.util.concurrent.TimeUnit.valueOf(java.lang.String)
       Method:  public static java.util.concurrent.TimeUnit[] 
                  java.util.concurrent.TimeUnit.values()
       Method:  public void java.util.concurrent.TimeUnit.sleep(long) 
                  throws java.lang.InterruptedException
       Method:  public long java.util.concurrent.TimeUnit.toNanos(long)
       Method:  public long java.util.concurrent.TimeUnit.convert
                  (long,java.util.concurrent.TimeUnit)
       Method:  abstract int java.util.concurrent.TimeUnit.excessNanos
                  (long,long)
       Method:  public void java.util.concurrent.TimeUnit.timedJoin
                  (java.lang.Thread,long) throws java.lang.InterruptedException
       Method:  public void java.util.concurrent.TimeUnit.timedWait
                  (java.lang.Object,long) throws java.lang.InterruptedException
       Method:  public long java.util.concurrent.TimeUnit.toDays(long)
       Method:  public long java.util.concurrent.TimeUnit.toHours(long)
       Method:  public long java.util.concurrent.TimeUnit.toMicros(long)
       Method:  public long java.util.concurrent.TimeUnit.toMillis(long)
       Method:  public long java.util.concurrent.TimeUnit.toMinutes(long)
       Method:  public long java.util.concurrent.TimeUnit.toSeconds(long)
       Method:  static long java.util.concurrent.TimeUnit.x(long,long,long)
```

### Получение и установка полей перечислимых типов

Поля, хранящие enum'ы, устанавливаются и читаются как любой другой ссылочный тип — с помощью
`Field.set()` и `Field.get()`. Дополнительные сведения о доступе к полям см. в разделе «Поля»
(Fields) этого трейла.

Рассмотрим приложение, которому нужно динамически изменить уровень трассировки (trace level) в
серверном приложении, которое обычно не допускает такое изменение во время выполнения.
Предположим, что экземпляр объекта сервера доступен. Пример `SetTrace` показывает, как код может
преобразовать строковое (`String`) представление enum'а в enum-тип, а также прочитать и установить
значение поля, хранящего enum.

```java
import java.lang.reflect.Field;
import static java.lang.System.out;

enum TraceLevel { OFF, LOW, MEDIUM, HIGH, DEBUG }

class MyServer {
    private TraceLevel level = TraceLevel.OFF;
}

public class SetTrace {
    public static void main(String... args) {
	TraceLevel newLevel = TraceLevel.valueOf(args[0]);

	try {
	    MyServer svr = new MyServer();
	    Class<?> c = svr.getClass();
	    Field f = c.getDeclaredField("level");
	    f.setAccessible(true);
	    TraceLevel oldLevel = (TraceLevel)f.get(svr);
	    out.format("Original trace level:  %s%n", oldLevel);

	    if (oldLevel != newLevel) {
 		f.set(svr, newLevel);
		out.format("    New  trace level:  %s%n", f.get(svr));
	    }

        // в рабочем коде эти исключения следует обрабатывать аккуратнее
	} catch (IllegalArgumentException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	}
    }
}
```

Поскольку константы перечисления являются синглтонами (singletons), для сравнения констант
перечисления одного типа можно использовать операторы `==` и `!=`.

```
$ java SetTrace OFF
Original trace level:  OFF
$ java SetTrace DEBUG
Original trace level:  OFF
    New  trace level:  DEBUG
```

### Устранение неполадок (перечисления)

Следующие примеры демонстрируют проблемы, которые могут возникнуть при использовании перечислимых
типов.

#### IllegalArgumentException при попытке создать экземпляр enum-типа

Как уже упоминалось, создание экземпляров enum-типов запрещено. Пример `EnumTrouble` пытается это
сделать.

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import static java.lang.System.out;

enum Charge {
    POSITIVE, NEGATIVE, NEUTRAL;
    Charge() {
	out.format("under construction%n");
    }
}

public class EnumTrouble {

    public static void main(String... args) {
	try {
	    Class<?> c = Charge.class;

 	    Constructor[] ctors = c.getDeclaredConstructors();
 	    for (Constructor ctor : ctors) {
		out.format("Constructor: %s%n",  ctor.toGenericString());
 		ctor.setAccessible(true);
 		ctor.newInstance();
 	    }

        // в рабочем коде эти исключения следует обрабатывать аккуратнее
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java EnumTrouble
Constructor: private Charge()
Exception in thread "main" java.lang.IllegalArgumentException: Cannot
  reflectively create enum objects
        at java.lang.reflect.Constructor.newInstance(Constructor.java:511)
        at EnumTrouble.main(EnumTrouble.java:22)
```

> **Совет.** Явная попытка создать экземпляр enum'а является ошибкой времени компиляции, поскольку
> это нарушило бы уникальность определённых констант перечисления. Это ограничение действует и в
> рефлективном коде. Код, который пытается создавать экземпляры классов через их конструкторы по
> умолчанию, должен сначала вызвать `Class.isEnum()`, чтобы определить, является ли класс enum'ом.

#### IllegalArgumentException при установке поля несовместимым enum-типом

Поля, хранящие enum'ы, устанавливаются соответствующим enum-типом. (По сути, поля любого типа
должны устанавливаться совместимыми типами.) Пример `EnumTroubleToo` производит ожидаемую ошибку.

```java
import java.lang.reflect.Field;

enum E0 { A, B }
enum E1 { A, B }

class ETest {
    private E0 fld = E0.A;
}

public class EnumTroubleToo {
    public static void main(String... args) {
	try {
	    ETest test = new ETest();
	    Field f = test.getClass().getDeclaredField("fld");
	    f.setAccessible(true);
 	    f.set(test, E1.A);  // IllegalArgumentException

        // в рабочем коде эти исключения следует обрабатывать аккуратнее
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java EnumTroubleToo
Exception in thread "main" java.lang.IllegalArgumentException: Can not set E0
  field ETest.fld to E1
        at sun.reflect.UnsafeFieldAccessorImpl.throwSetIllegalArgumentException
          (UnsafeFieldAccessorImpl.java:146)
        at sun.reflect.UnsafeFieldAccessorImpl.throwSetIllegalArgumentException
          (UnsafeFieldAccessorImpl.java:150)
        at sun.reflect.UnsafeObjectFieldAccessorImpl.set
          (UnsafeObjectFieldAccessorImpl.java:63)
        at java.lang.reflect.Field.set(Field.java:657)
        at EnumTroubleToo.main(EnumTroubleToo.java:16)
```

> **Совет.** Строго говоря, любая попытка установить поле типа `X` значением типа `Y` может
> завершиться успешно только если выполняется следующее условие:
>
> ```java
> X.class.isAssignableFrom(Y.class) == true
> ```
>
> Код можно изменить, добавив следующую проверку совместимости типов:
>
> ```java
> if (f.getType().isAssignableFrom(E0.class))
>     // совместимо
> else
>     // ожидаем IllegalArgumentException
> ```

## Источник

- [Lesson: Arrays and Enumerated Types](https://docs.oracle.com/javase/tutorial/reflect/special/index.html) — официальное руководство Oracle (The Java Tutorials, JDK 8).
- [Identifying Array Types](https://docs.oracle.com/javase/tutorial/reflect/special/arrayComponents.html) — Oracle.
- [Creating New Arrays](https://docs.oracle.com/javase/tutorial/reflect/special/arrayInstance.html) — Oracle.
- [Getting and Setting Arrays and Their Components](https://docs.oracle.com/javase/tutorial/reflect/special/arraySetGet.html) — Oracle.
- [Troubleshooting (Arrays)](https://docs.oracle.com/javase/tutorial/reflect/special/arrayTrouble.html) — Oracle.
- [Examining Enums](https://docs.oracle.com/javase/tutorial/reflect/special/enumMembers.html) — Oracle.
- [Getting and Setting Fields with Enum Types](https://docs.oracle.com/javase/tutorial/reflect/special/enumSetGet.html) — Oracle.
- [Troubleshooting (Enums)](https://docs.oracle.com/javase/tutorial/reflect/special/enumTrouble.html) — Oracle.
</content>
</invoke>
