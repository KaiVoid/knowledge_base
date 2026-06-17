# Урок 1. Классы (рефлексия)

**Трейл:** Reflection · **Оригинал:** [Classes](https://docs.oracle.com/javase/tutorial/reflect/class/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · [[09-modern-java-features]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> *Lesson: Classes*, *Retrieving Class Objects*, *Examining Class Modifiers and Types*,
> *Discovering Class Members* и *Troubleshooting*.

Любой тип — это либо ссылочный тип (*reference type*), либо примитивный (*primitive*). Классы,
перечисления (*enums*) и массивы (все они наследуются от `java.lang.Object`), а также интерфейсы —
всё это ссылочные типы. Примеры ссылочных типов: `java.lang.String`, все классы-обёртки для
примитивных типов (например, `java.lang.Double`), интерфейс `java.io.Serializable` и перечисление
`javax.swing.SortOrder`. Множество примитивных типов фиксировано: `boolean`, `byte`, `short`, `int`,
`long`, `char`, `float` и `double`.

Для каждого типа объектов виртуальная машина Java создаёт неизменяемый (*immutable*) экземпляр
класса `java.lang.Class`, который предоставляет методы для изучения свойств объекта во время
выполнения (*runtime*), включая его члены (*members*) и информацию о типе. `Class` также даёт
возможность создавать новые классы и объекты. И, что особенно важно, это точка входа во все
API рефлексии. Данный урок охватывает наиболее часто используемые операции рефлексии, связанные
с классами:

- [Получение объектов Class](#получение-объектов-class) — описывает способы получить `Class`;
- [Изучение модификаторов и типов класса](#изучение-модификаторов-и-типов-класса) — показывает,
  как получить доступ к сведениям из объявления класса;
- [Обнаружение членов класса](#обнаружение-членов-класса) — иллюстрирует, как перечислить
  конструкторы, поля, методы и вложенные классы внутри класса;
- [Устранение неполадок](#устранение-неполадок) — описывает типичные ошибки при работе с `Class`.

## Получение объектов Class

Точка входа во все операции рефлексии — `java.lang.Class`. За исключением
`java.lang.reflect.ReflectPermission`, ни один из классов пакета `java.lang.reflect` не имеет
публичных конструкторов. Чтобы добраться до этих классов, необходимо вызывать соответствующие
методы на `Class`. Получить `Class` можно несколькими способами — в зависимости от того, есть ли у
кода доступ к объекту, к имени класса, к типу или к уже существующему `Class`.

### Object.getClass()

Если доступен экземпляр объекта, то простейший способ получить его `Class` — вызвать
`Object.getClass()`. Разумеется, это работает только для ссылочных типов, которые все наследуются
от `Object`. Несколько примеров.

```java
Class c = "foo".getClass();
```

Возвращает `Class` для `String`.

```java
Class c = System.console().getClass();
```

С виртуальной машиной связана единственная консоль, которую возвращает `static`-метод
`System.console()`. Значение, возвращаемое `getClass()`, — это `Class`, соответствующий
`java.io.Console`.

```java
enum E { A, B }
Class c = A.getClass();
```

`A` — это экземпляр перечисления `E`; таким образом, `getClass()` возвращает `Class`,
соответствующий типу перечисления `E`.

```java
byte[] bytes = new byte[1024];
Class c = bytes.getClass();
```

Поскольку массивы — это `Object`-ы, у экземпляра массива тоже можно вызвать `getClass()`.
Возвращённый `Class` соответствует массиву с типом компонентов `byte`.

```java
import java.util.HashSet;
import java.util.Set;

Set<String> s = new HashSet<String>();
Class c = s.getClass();
```

В этом случае `java.util.Set` — это интерфейс к объекту типа `java.util.HashSet`. Значение,
возвращаемое `getClass()`, — это класс, соответствующий `java.util.HashSet`.

### Синтаксис .class

Если тип доступен, но экземпляра нет, то получить `Class` можно, дописав `".class"` к имени типа.
Это также самый простой способ получить `Class` для примитивного типа.

```java
boolean b;
Class c = b.getClass();   // ошибка на этапе компиляции
```

```java
Class c = boolean.class;  // правильно
```

Обратите внимание: выражение `boolean.getClass()` привело бы к ошибке компиляции, потому что
`boolean` — примитивный тип и его нельзя разыменовать. Синтаксис `.class` возвращает `Class`,
соответствующий типу `boolean`.

```java
Class c = java.io.PrintStream.class;
```

Переменная `c` будет содержать `Class`, соответствующий типу `java.io.PrintStream`.

```java
Class c = int[][][].class;
```

Синтаксис `.class` можно применять для получения `Class`, соответствующего многомерному массиву
заданного типа.

### Class.forName()

Если доступно полностью квалифицированное имя (*fully-qualified name*) класса, то соответствующий
`Class` можно получить с помощью статического метода `Class.forName()`. Этот способ нельзя
применять к примитивным типам. Синтаксис имён классов-массивов описан в `Class.getName()`. Этот
синтаксис применим как к ссылочным, так и к примитивным типам.

```java
Class c = Class.forName("com.duke.MyLocaleServiceProvider");
```

Этот оператор создаёт класс по заданному полностью квалифицированному имени.

```java
Class cDoubleArray = Class.forName("[D");
```

```java
Class cStringArray = Class.forName("[[Ljava.lang.String;");
```

Переменная `cDoubleArray` будет содержать `Class`, соответствующий массиву примитивного типа
`double` (то есть то же самое, что и `double[].class`). Переменная `cStringArray` будет содержать
`Class`, соответствующий двумерному массиву `String` (то есть идентичный `String[][].class`).

### Поле TYPE у классов-обёрток примитивных типов

Синтаксис `.class` удобнее и является предпочтительным способом получить `Class` для примитивного
типа; однако существует и другой способ. У каждого из примитивных типов и у `void` есть
класс-обёртка (*wrapper class*) в пакете `java.lang`, который используется для упаковки (*boxing*)
примитивных типов в ссылочные. Каждый класс-обёртка содержит поле с именем `TYPE`, которое равно
`Class` для упаковываемого примитивного типа.

```java
Class c = Double.TYPE;
```

Существует класс `java.lang.Double`, который используется для упаковки примитивного типа `double`
всякий раз, когда требуется `Object`. Значение `Double.TYPE` идентично значению `double.class`.

```java
Class c = Void.TYPE;
```

`Void.TYPE` идентичен `void.class`.

### Методы, возвращающие классы

Существует несколько API рефлексии, которые возвращают классы, но обратиться к ним можно лишь
после того, как `Class` уже был получен — напрямую или косвенно.

**`Class.getSuperclass()`**

Возвращает суперкласс данного класса.

```java
Class c = javax.swing.JButton.class.getSuperclass();
```

Суперкласс `javax.swing.JButton` — это `javax.swing.AbstractButton`.

**`Class.getClasses()`**

Возвращает все публичные классы, интерфейсы и перечисления, которые являются членами класса,
включая унаследованные члены.

```java
Class<?> [] c = Character.class.getClasses();
```

`Character` содержит два класса-члена: `Character.Subset` и `Character.UnicodeBlock`.

**`Class.getDeclaredClasses()`**

Возвращает все классы, интерфейсы и перечисления, явно объявленные в этом классе.

```java
Class<?> [] c = Character.class.getDeclaredClasses();
```

`Character` содержит два публичных класса-члена — `Character.Subset` и `Character.UnicodeBlock` —
и один приватный класс `Character.CharacterCache`.

**`Class.getDeclaringClass()`**
**`java.lang.reflect.Field.getDeclaringClass()`**
**`java.lang.reflect.Method.getDeclaringClass()`**
**`java.lang.reflect.Constructor.getDeclaringClass()`**

Возвращает `Class`, в котором были объявлены эти члены. У объявлений анонимных классов нет
объявляющего класса (*declaring class*), но есть охватывающий класс (*enclosing class*).

```java
import java.lang.reflect.Field;

Field f = System.class.getField("out");
Class c = f.getDeclaringClass();
```

Поле `out` объявлено в `System`.

```java
public class MyClass {
    static Object o = new Object() {
        public void m() {}
    };
    static Class<c> = o.getClass().getEnclosingClass();
}
```

Объявляющий класс анонимного класса, определённого через `o`, — `null`.

**`Class.getEnclosingClass()`**

Возвращает непосредственно охватывающий класс данного класса.

```java
Class c = Thread.State.class().getEnclosingClass();
```

Охватывающий класс перечисления `Thread.State` — это `Thread`.

```java
public class MyClass {
    static Object o = new Object() {
        public void m() {}
    };
    static Class<c> = o.getClass().getEnclosingClass();
}
```

Анонимный класс, определённый через `o`, охватывается классом `MyClass`.

## Изучение модификаторов и типов класса

Класс может быть объявлен с одним или несколькими модификаторами, влияющими на его поведение во
время выполнения:

- модификаторы доступа: `public`, `protected` и `private`;
- модификатор, требующий переопределения: `abstract`;
- модификатор, ограничивающий одним экземпляром: `static`;
- модификатор, запрещающий изменение значения: `final`;
- модификатор, принудительно включающий строгое поведение с плавающей точкой: `strictfp`;
- аннотации.

Не все модификаторы допустимы для всех классов: например, интерфейс не может быть `final`, а
перечисление не может быть `abstract`. Класс `java.lang.reflect.Modifier` содержит объявления для
всех возможных модификаторов. Он также содержит методы, которые можно использовать для
декодирования набора модификаторов, возвращаемого `Class.getModifiers()`.

Пример `ClassDeclarationSpy` показывает, как получить компоненты объявления класса, включая
модификаторы, обобщённые параметры типа (*generic type parameters*), реализуемые интерфейсы и путь
наследования. Поскольку `Class` реализует интерфейс `java.lang.reflect.AnnotatedElement`, можно
также запросить аннотации времени выполнения (*runtime annotations*).

```java
import java.lang.annotation.Annotation;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;
import java.lang.reflect.TypeVariable;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import static java.lang.System.out;

public class ClassDeclarationSpy {
    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    out.format("Class:%n  %s%n%n", c.getCanonicalName());
	    out.format("Modifiers:%n  %s%n%n",
		       Modifier.toString(c.getModifiers()));

	    out.format("Type Parameters:%n");
	    TypeVariable[] tv = c.getTypeParameters();
	    if (tv.length != 0) {
		out.format("  ");
		for (TypeVariable t : tv)
		    out.format("%s ", t.getName());
		out.format("%n%n");
	    } else {
		out.format("  -- No Type Parameters --%n%n");
	    }

	    out.format("Implemented Interfaces:%n");
	    Type[] intfs = c.getGenericInterfaces();
	    if (intfs.length != 0) {
		for (Type intf : intfs)
		    out.format("  %s%n", intf.toString());
		out.format("%n");
	    } else {
		out.format("  -- No Implemented Interfaces --%n%n");
	    }

	    out.format("Inheritance Path:%n");
	    List<Class> l = new ArrayList<Class>();
	    printAncestor(c, l);
	    if (l.size() != 0) {
		for (Class<?> cl : l)
		    out.format("  %s%n", cl.getCanonicalName());
		out.format("%n");
	    } else {
		out.format("  -- No Super Classes --%n%n");
	    }

	    out.format("Annotations:%n");
	    Annotation[] ann = c.getAnnotations();
	    if (ann.length != 0) {
		for (Annotation a : ann)
		    out.format("  %s%n", a.toString());
		out.format("%n");
	    } else {
		out.format("  -- No Annotations --%n%n");
	    }

        // в реальном коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }

    private static void printAncestor(Class<?> c, List<Class> l) {
	Class<?> ancestor = c.getSuperclass();
 	if (ancestor != null) {
	    l.add(ancestor);
	    printAncestor(ancestor, l);
 	}
    }
}
```

Несколько примеров вывода. Ввод пользователя выделен курсивом.

```
$ java ClassDeclarationSpy java.util.concurrent.ConcurrentNavigableMap
Class:
  java.util.concurrent.ConcurrentNavigableMap

Modifiers:
  public abstract interface

Type Parameters:
  K V

Implemented Interfaces:
  java.util.concurrent.ConcurrentMap<K, V>
  java.util.NavigableMap<K, V>

Inheritance Path:
  -- No Super Classes --

Annotations:
  -- No Annotations --
```

Так выглядит фактическое объявление `java.util.concurrent.ConcurrentNavigableMap` в исходном коде:

```java
public interface ConcurrentNavigableMap<K,V>
    extends ConcurrentMap<K,V>, NavigableMap<K,V>
```

Обратите внимание: поскольку это интерфейс, он неявно (*implicitly*) `abstract`. Компилятор
добавляет этот модификатор для каждого интерфейса. Также в этом объявлении есть два обобщённых
параметра типа — `K` и `V`. Пример просто печатает имена этих параметров, но можно получить и
дополнительную информацию о них с помощью методов из `java.lang.reflect.TypeVariable`. Интерфейсы
тоже могут реализовывать другие интерфейсы, как показано выше.

```
$ java ClassDeclarationSpy "[Ljava.lang.String;"
Class:
  java.lang.String[]

Modifiers:
  public abstract final

Type Parameters:
  -- No Type Parameters --

Implemented Interfaces:
  interface java.lang.Cloneable
  interface java.io.Serializable

Inheritance Path:
  java.lang.Object

Annotations:
  -- No Annotations --
```

Поскольку массивы — это объекты времени выполнения, вся информация о типе определяется
виртуальной машиной Java. В частности, массивы реализуют `Cloneable` и `java.io.Serializable`, а
их непосредственный суперкласс — всегда `Object`.

```
$ java ClassDeclarationSpy java.io.InterruptedIOException
Class:
  java.io.InterruptedIOException

Modifiers:
  public

Type Parameters:
  -- No Type Parameters --

Implemented Interfaces:
  -- No Implemented Interfaces --

Inheritance Path:
  java.io.IOException
  java.lang.Exception
  java.lang.Throwable
  java.lang.Object

Annotations:
  -- No Annotations --
```

Из пути наследования можно сделать вывод, что `java.io.InterruptedIOException` —
проверяемое исключение (*checked exception*), потому что в пути отсутствует `RuntimeException`.

```
$ java ClassDeclarationSpy java.security.Identity
Class:
  java.security.Identity

Modifiers:
  public abstract

Type Parameters:
  -- No Type Parameters --

Implemented Interfaces:
  interface java.security.Principal
  interface java.io.Serializable

Inheritance Path:
  java.lang.Object

Annotations:
  @java.lang.Deprecated()
```

Этот вывод показывает, что `java.security.Identity` — устаревший (*deprecated*) API — снабжён
аннотацией `java.lang.Deprecated`. Это можно использовать в рефлексивном коде для обнаружения
устаревших API.

> **Примечание.** Не все аннотации доступны через рефлексию. Доступны только те, у которых политика
> хранения `java.lang.annotation.RetentionPolicy` равна `RUNTIME`. Из трёх аннотаций, заранее
> определённых в языке, — `@Deprecated`, `@Override` и `@SuppressWarnings` — во время выполнения
> доступна только `@Deprecated`.

## Обнаружение членов класса

В классе `Class` предусмотрены две категории методов для доступа к полям, методам и конструкторам:
методы, которые перечисляют (*enumerate*) эти члены, и методы, которые ищут (*search*) конкретные
члены. Кроме того, есть отдельные методы для доступа к членам, объявленным непосредственно в
классе, и методы, которые ищут унаследованные члены в суперинтерфейсах и суперклассах. В таблицах
ниже приведена сводка всех методов, отыскивающих члены, и их характеристик.

### Методы Class для поиска полей

| API `Class` | Список членов? | Унаследованные члены? | Приватные члены? |
|---|---|---|---|
| `getDeclaredField()` | нет | нет | да |
| `getField()` | нет | да | нет |
| `getDeclaredFields()` | да | нет | да |
| `getFields()` | да | да | нет |

### Методы Class для поиска методов

| API `Class` | Список членов? | Унаследованные члены? | Приватные члены? |
|---|---|---|---|
| `getDeclaredMethod()` | нет | нет | да |
| `getMethod()` | нет | да | нет |
| `getDeclaredMethods()` | да | нет | да |
| `getMethods()` | да | да | нет |

### Методы Class для поиска конструкторов

| API `Class` | Список членов? | Унаследованные члены? | Приватные члены? |
|---|---|---|---|
| `getDeclaredConstructor()` | нет | н/д¹ | да |
| `getConstructor()` | нет | н/д¹ | нет |
| `getDeclaredConstructors()` | да | н/д¹ | да |
| `getConstructors()` | да | н/д¹ | нет |

¹ Конструкторы не наследуются.

Получив имя класса и указание, какие члены представляют интерес, пример `ClassSpy` использует
методы `get*s()`, чтобы определить список всех публичных элементов, включая унаследованные.

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Member;
import static java.lang.System.out;

enum ClassMember { CONSTRUCTOR, FIELD, METHOD, CLASS, ALL }

public class ClassSpy {
    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    out.format("Class:%n  %s%n%n", c.getCanonicalName());

	    Package p = c.getPackage();
	    out.format("Package:%n  %s%n%n",
		       (p != null ? p.getName() : "-- No Package --"));

	    for (int i = 1; i < args.length; i++) {
		switch (ClassMember.valueOf(args[i])) {
		case CONSTRUCTOR:
		    printMembers(c.getConstructors(), "Constructor");
		    break;
		case FIELD:
		    printMembers(c.getFields(), "Fields");
		    break;
		case METHOD:
		    printMembers(c.getMethods(), "Methods");
		    break;
		case CLASS:
		    printClasses(c);
		    break;
		case ALL:
		    printMembers(c.getConstructors(), "Constuctors");
		    printMembers(c.getFields(), "Fields");
		    printMembers(c.getMethods(), "Methods");
		    printClasses(c);
		    break;
		default:
		    assert false;
		}
	    }

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }

    private static void printMembers(Member[] mbrs, String s) {
	out.format("%s:%n", s);
	for (Member mbr : mbrs) {
	    if (mbr instanceof Field)
		out.format("  %s%n", ((Field)mbr).toGenericString());
	    else if (mbr instanceof Constructor)
		out.format("  %s%n", ((Constructor)mbr).toGenericString());
	    else if (mbr instanceof Method)
		out.format("  %s%n", ((Method)mbr).toGenericString());
	}
	if (mbrs.length == 0)
	    out.format("  -- No %s --%n", s);
	out.format("%n");
    }

    private static void printClasses(Class<?> c) {
	out.format("Classes:%n");
	Class<?>[] clss = c.getClasses();
	for (Class<?> cls : clss)
	    out.format("  %s%n", cls.getCanonicalName());
	if (clss.length == 0)
	    out.format("  -- No member interfaces, classes, or enums --%n");
	out.format("%n");
    }
}
```

Этот пример сравнительно компактен; однако метод `printMembers()` получился слегка неуклюжим из-за
того, что интерфейс `java.lang.reflect.Member` существует с самых первых реализаций рефлексии, и
его нельзя было изменить, добавив более удобный метод `getGenericString()`, когда появились
обобщения (*generics*). Единственные альтернативы — проверять тип и приводить (*cast*), как
показано выше, заменить этот метод на `printConstructors()`, `printFields()` и `printMethods()` или
довольствоваться более скудными результатами `Member.getName()`.

Примеры вывода и их толкование приведены далее. Ввод пользователя выделен курсивом.

```
$ java ClassSpy java.lang.ClassCastException CONSTRUCTOR
Class:
  java.lang.ClassCastException

Package:
  java.lang

Constructor:
  public java.lang.ClassCastException()
  public java.lang.ClassCastException(java.lang.String)
```

Поскольку конструкторы не наследуются, конструкторы механизма сцепления исключений (*exception
chaining*) — те, что имеют параметр `Throwable`, — определённые в непосредственном суперклассе
`RuntimeException` и других суперклассах, не находятся.

```
$ java ClassSpy java.nio.channels.ReadableByteChannel METHOD
Class:
  java.nio.channels.ReadableByteChannel

Package:
  java.nio.channels

Methods:
  public abstract int java.nio.channels.ReadableByteChannel.read
    (java.nio.ByteBuffer) throws java.io.IOException
  public abstract void java.nio.channels.Channel.close() throws
    java.io.IOException
  public abstract boolean java.nio.channels.Channel.isOpen()
```

Интерфейс `java.nio.channels.ReadableByteChannel` определяет `read()`. Остальные методы
унаследованы от суперинтерфейса. Этот код легко изменить так, чтобы он перечислял только те методы,
которые действительно объявлены в классе, заменив `get*s()` на `getDeclared*s()`.

```
$ java ClassSpy ClassMember FIELD METHOD
Class:
  ClassMember

Package:
  -- No Package --

Fields:
  public static final ClassMember ClassMember.CONSTRUCTOR
  public static final ClassMember ClassMember.FIELD
  public static final ClassMember ClassMember.METHOD
  public static final ClassMember ClassMember.CLASS
  public static final ClassMember ClassMember.ALL

Methods:
  public static ClassMember ClassMember.valueOf(java.lang.String)
  public static ClassMember[] ClassMember.values()
  public final int java.lang.Enum.hashCode()
  public final int java.lang.Enum.compareTo(E)
  public int java.lang.Enum.compareTo(java.lang.Object)
  public final java.lang.String java.lang.Enum.name()
  public final boolean java.lang.Enum.equals(java.lang.Object)
  public java.lang.String java.lang.Enum.toString()
  public static <T> T java.lang.Enum.valueOf
    (java.lang.Class<T>,java.lang.String)
  public final java.lang.Class<E> java.lang.Enum.getDeclaringClass()
  public final int java.lang.Enum.ordinal()
  public final native java.lang.Class<?> java.lang.Object.getClass()
  public final native void java.lang.Object.wait(long) throws
    java.lang.InterruptedException
  public final void java.lang.Object.wait(long,int) throws
    java.lang.InterruptedException
  public final void java.lang.Object.wait() throws java.lang.InterruptedException
  public final native void java.lang.Object.notify()
  public final native void java.lang.Object.notifyAll()
```

В разделе полей этих результатов перечислены константы перечисления (*enum constants*). Хотя
формально это поля, иногда бывает полезно отличать их от остальных полей. Этот пример можно
изменить, чтобы использовать `java.lang.reflect.Field.isEnumConstant()` для этой цели. Пример
`EnumSpy` в более позднем разделе этого трейла — [Examining Enums](https://docs.oracle.com/javase/tutorial/reflect/special/enumMembers.html) —
содержит возможную реализацию.

В разделе методов вывода обратите внимание, что имя метода включает имя объявляющего класса. Так,
метод `toString()` реализован в `Enum`, а не унаследован от `Object`. Код можно дополнить, чтобы
сделать это нагляднее, с помощью `Field.getDeclaringClass()`. Следующий фрагмент иллюстрирует часть
возможного решения.

```java
if (mbr instanceof Field) {
    Field f = (Field)mbr;
    out.format("  %s%n", f.toGenericString());
    out.format("  -- declared in: %s%n", f.getDeclaringClass());
}
```

## Устранение неполадок

Следующие примеры показывают типичные ошибки, которые могут возникнуть при рефлексии над классами.

### Предупреждение компилятора: «Note: ... uses unchecked or unsafe operations»

При вызове метода типы значений-аргументов проверяются и, возможно, преобразуются. `ClassWarning`
вызывает `getMethod()`, чтобы спровоцировать типичное предупреждение о непроверяемом преобразовании
(*unchecked conversion*):

```java
import java.lang.reflect.Method;

public class ClassWarning {
    void m() {
	try {
	    Class c = ClassWarning.class;
	    Method m = c.getMethod("m");  // предупреждение

        // в реальном коде это исключение следует обрабатывать аккуратнее
	} catch (NoSuchMethodException x) {
    	    x.printStackTrace();
    	}
    }
}
```

```
$ javac ClassWarning.java
Note: ClassWarning.java uses unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
$ javac -Xlint:unchecked ClassWarning.java
ClassWarning.java:6: warning: [unchecked] unchecked call to getMethod
  (String,Class<?>...) as a member of the raw type Class
Method m = c.getMethod("m");  // warning
                      ^
1 warning
```

Многие методы библиотеки были дополнены обобщёнными объявлениями (*generic declarations*), включая
несколько методов в `Class`. Поскольку `c` объявлена как «сырой» (*raw*) тип (без параметров типа),
а соответствующий параметр `getMethod()` — параметризованный тип, происходит непроверяемое
преобразование. Компилятор обязан сгенерировать предупреждение. (См. *The Java Language
Specification, Java SE 7 Edition*, разделы *Unchecked Conversion* и *Method Invocation Conversion*.)

Есть два возможных решения. Предпочтительнее изменить объявление `c`, добавив подходящий обобщённый
тип. В этом случае объявление должно быть таким:

```java
Class<?> c = warn.getClass();
```

Или же предупреждение можно явно подавить с помощью предопределённой аннотации `@SuppressWarnings`,
поставленной перед проблемным оператором.

```java
Class c = ClassWarning.class;
@SuppressWarnings("unchecked")
Method m = c.getMethod("m");
// предупреждения больше нет
```

> **Совет.** Как общий принцип, предупреждения не следует игнорировать, поскольку они могут
> указывать на наличие ошибки. Следует использовать параметризованные объявления там, где это
> уместно. Если это невозможно (например, потому что приложение должно взаимодействовать с кодом
> стороннего поставщика библиотек), снабдите проблемную строку аннотацией `@SuppressWarnings`.

### InstantiationException, когда конструктор недоступен

`Class.newInstance()` выбросит `InstantiationException`, если предпринимается попытка создать новый
экземпляр класса, а конструктор без аргументов не виден. Пример `ClassTrouble` иллюстрирует
получающуюся трассировку стека (*stack trace*).

```java
class Cls {
    private Cls() {}
}

public class ClassTrouble {
    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName("Cls");
	    c.newInstance();  // InstantiationException

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java ClassTrouble
java.lang.IllegalAccessException: Class ClassTrouble can not access a member of
  class Cls with modifiers "private"
        at sun.reflect.Reflection.ensureMemberAccess(Reflection.java:65)
        at java.lang.Class.newInstance0(Class.java:349)
        at java.lang.Class.newInstance(Class.java:308)
        at ClassTrouble.main(ClassTrouble.java:9)
```

`Class.newInstance()` ведёт себя очень похоже на ключевое слово `new` и завершится неудачей по тем
же причинам, по которым завершился бы `new`. Типичное решение в рефлексии — воспользоваться
классом `java.lang.reflect.AccessibleObject`, который даёт возможность подавлять проверки контроля
доступа; однако этот подход не сработает, потому что `java.lang.Class` не расширяет
`AccessibleObject`. Единственное решение — изменить код так, чтобы использовать
`Constructor.newInstance()`, который действительно расширяет `AccessibleObject`.

> **Совет.** В общем случае предпочтительнее использовать `Constructor.newInstance()` по причинам,
> описанным в разделе [Creating New Class Instances](https://docs.oracle.com/javase/tutorial/reflect/member/ctorInstance.html)
> урока [Members](https://docs.oracle.com/javase/tutorial/reflect/member/index.html).

Дополнительные примеры возможных проблем при использовании `Constructor.newInstance()` можно найти
в разделе [Constructor Troubleshooting](https://docs.oracle.com/javase/tutorial/reflect/member/ctorTrouble.html)
урока [Members](https://docs.oracle.com/javase/tutorial/reflect/member/index.html).

## Источник

- [Lesson: Classes](https://docs.oracle.com/javase/tutorial/reflect/class/index.html) — официальное руководство Oracle.
- [Retrieving Class Objects](https://docs.oracle.com/javase/tutorial/reflect/class/classNew.html)
- [Examining Class Modifiers and Types](https://docs.oracle.com/javase/tutorial/reflect/class/classModifiers.html)
- [Discovering Class Members](https://docs.oracle.com/javase/tutorial/reflect/class/classMembers.html)
- [Troubleshooting](https://docs.oracle.com/javase/tutorial/reflect/class/classTrouble.html)
</content>
</invoke>
