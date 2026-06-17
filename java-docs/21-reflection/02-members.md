# Урок 2. Члены класса (поля, методы, конструкторы)

**Трейл:** Reflection · **Оригинал:** [Members](https://docs.oracle.com/javase/tutorial/reflect/member/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок объединяет
> страницы трейла *The Reflection API → Members*: обзорную страницу и подразделы о полях
> (*Fields*), методах (*Methods*) и конструкторах (*Constructors*).

Рефлексия определяет интерфейс [`java.lang.reflect.Member`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Member.html), который реализуют классы [`java.lang.reflect.Field`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html), [`java.lang.reflect.Method`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html) и [`java.lang.reflect.Constructor`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html). Эти объекты и обсуждаются в данном уроке. Для каждого члена класса (*member*) урок описывает связанные API для получения информации об объявлении и о типах, операции, уникальные для конкретного члена (например, установка значения поля или вызов метода), а также часто встречающиеся ошибки. Каждое понятие проиллюстрировано примерами кода и соответствующим выводом, которые приближённо отражают типичные сценарии использования рефлексии.

> **Примечание.** Согласно *The Java Language Specification, Java SE 7 Edition*, **членами** (*members*) класса являются наследуемые компоненты тела класса, включая поля, методы, вложенные классы, интерфейсы и перечислимые типы. Поскольку конструкторы не наследуются, они не являются членами. Это отличается от набора классов, реализующих [`java.lang.reflect.Member`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Member.html).

---

## Поля (Fields)

У полей есть тип и значение. Класс [`java.lang.reflect.Field`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html) предоставляет методы для доступа к информации о типе, а также для установки и получения значений поля у заданного объекта.

### Получение типов поля

Поле может иметь либо примитивный (*primitive*), либо ссылочный (*reference*) тип. Существует восемь примитивных типов: `boolean`, `byte`, `short`, `int`, `long`, `char`, `float` и `double`. Ссылочный тип — это всё, что является прямым или косвенным подклассом [`java.lang.Object`](https://docs.oracle.com/javase/8/docs/api/java/lang/Object.html), включая интерфейсы, массивы и перечислимые типы.

Пример `FieldSpy` выводит тип поля и его обобщённый тип (*generic type*), получая на вход полностью квалифицированное двоичное имя класса и имя поля.

```java
import java.lang.reflect.Field;
import java.util.List;

public class FieldSpy<T> {
    public boolean[][] b = {{ false, false }, { true, true } };
    public String name  = "Alice";
    public List<Integer> list;
    public T val;

    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    Field f = c.getField(args[1]);
	    System.out.format("Type: %s%n", f.getType());
	    System.out.format("GenericType: %s%n", f.getGenericType());

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	}
    }
}
```

Ниже приведён пример вывода для получения типов трёх public-полей этого класса (`b`, `name` и параметризованного поля `list`). Ввод пользователя выделен курсивом в оригинале.

```
$ java FieldSpy FieldSpy b
Type: class [[Z
GenericType: class [[Z
$ java FieldSpy FieldSpy name
Type: class java.lang.String
GenericType: class java.lang.String
$ java FieldSpy FieldSpy list
Type: interface java.util.List
GenericType: java.util.List<java.lang.Integer>
$ java FieldSpy FieldSpy val
Type: class java.lang.Object
GenericType: T
```

Тип поля `b` — двумерный массив `boolean`. Синтаксис имени типа описан в документации [`Class.getName()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getName--).

Тип поля `val` сообщается как `java.lang.Object`, потому что обобщения (*generics*) реализованы через **стирание типов** (*type erasure*), которое удаляет всю информацию об обобщённых типах во время компиляции. Таким образом, `T` заменяется на верхнюю границу (*upper bound*) переменной типа — в данном случае на `java.lang.Object`.

Метод [`Field.getGenericType()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#getGenericType--) обращается к атрибуту сигнатуры (*Signature Attribute*) в файле класса, если он присутствует. Если атрибут недоступен, метод возвращается к [`Field.getType()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#getType--), который не изменился с появлением обобщений. Остальные методы рефлексии с именем вида `getGenericFoo` (для некоторого значения *Foo*) реализованы аналогично.

### Получение и разбор модификаторов поля

В объявлении поля могут присутствовать несколько модификаторов:

- Модификаторы доступа: `public`, `protected` и `private`.
- Модификаторы, определяющие поведение во время выполнения: `transient` и `volatile`.
- Модификатор, ограничивающий поле одним экземпляром: `static`.
- Модификатор, запрещающий изменение значения: `final`.
- Аннотации.

Метод [`Field.getModifiers()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#getModifiers--) можно использовать для получения целого числа, представляющего набор объявленных модификаторов поля. Биты, представляющие модификаторы в этом целом числе, определены в классе [`java.lang.reflect.Modifier`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Modifier.html).

Пример `FieldModifierSpy` иллюстрирует, как искать поля с заданным модификатором. Он также определяет, является ли найденное поле синтетическим (*synthetic*, сгенерированным компилятором) или константой перечисления (*enum constant*), вызывая [`Field.isSynthetic()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#isSynthetic--) и [`Field.isEnumConstant()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#isEnumConstant--) соответственно.

```java
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import static java.lang.System.out;

enum Spy { BLACK , WHITE }

public class FieldModifierSpy {
    volatile int share;
    int instance;
    class Inner {}

    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    int searchMods = 0x0;
	    for (int i = 1; i < args.length; i++) {
		searchMods |= modifierFromString(args[i]);
	    }

	    Field[] flds = c.getDeclaredFields();
	    out.format("Fields in Class '%s' containing modifiers:  %s%n",
		       c.getName(),
		       Modifier.toString(searchMods));
	    boolean found = false;
	    for (Field f : flds) {
		int foundMods = f.getModifiers();
		// Требуем, чтобы присутствовали все запрошенные модификаторы
		if ((foundMods & searchMods) == searchMods) {
		    out.format("%-8s [ synthetic=%-5b enum_constant=%-5b ]%n",
			       f.getName(), f.isSynthetic(),
			       f.isEnumConstant());
		    found = true;
		}
	    }

	    if (!found) {
		out.format("No matching fields%n");
	    }

        // в реальном коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }

    private static int modifierFromString(String s) {
	int m = 0x0;
	if ("public".equals(s))           m |= Modifier.PUBLIC;
	else if ("protected".equals(s))   m |= Modifier.PROTECTED;
	else if ("private".equals(s))     m |= Modifier.PRIVATE;
	else if ("static".equals(s))      m |= Modifier.STATIC;
	else if ("final".equals(s))       m |= Modifier.FINAL;
	else if ("transient".equals(s))   m |= Modifier.TRANSIENT;
	else if ("volatile".equals(s))    m |= Modifier.VOLATILE;
	return m;
    }
}
```

Пример вывода:

```
$ java FieldModifierSpy FieldModifierSpy volatile
Fields in Class 'FieldModifierSpy' containing modifiers:  volatile
share    [ synthetic=false enum_constant=false ]

$ java FieldModifierSpy Spy public
Fields in Class 'Spy' containing modifiers:  public
BLACK    [ synthetic=false enum_constant=true  ]
WHITE    [ synthetic=false enum_constant=true  ]

$ java FieldModifierSpy FieldModifierSpy$Inner final
Fields in Class 'FieldModifierSpy$Inner' containing modifiers:  final
this$0   [ synthetic=true  enum_constant=false ]

$ java FieldModifierSpy Spy private static final
Fields in Class 'Spy' containing modifiers:  private static final
$VALUES  [ synthetic=true  enum_constant=false ]
```

Обратите внимание, что некоторые поля выводятся, хотя они не были объявлены в исходном коде. Это происходит потому, что компилятор генерирует некоторые **синтетические поля** (*synthetic fields*), необходимые во время выполнения. Чтобы проверить, является ли поле синтетическим, в примере вызывается [`Field.isSynthetic()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#isSynthetic--). Набор синтетических полей зависит от компилятора; однако к часто используемым относятся `this$0` — для внутренних классов (то есть вложенных классов, не являющихся статическими членами-классами), чтобы ссылаться на самый внешний охватывающий класс, — и `$VALUES`, используемое перечислениями для реализации неявно определённого статического метода `values()`. Имена синтетических членов класса не специфицированы и могут отличаться в разных реализациях или выпусках компилятора. Эти и другие синтетические поля будут включены в массив, возвращаемый методом [`Class.getDeclaredFields()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getDeclaredFields--), но не будут видны через [`Class.getField()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getField-java.lang.String-), поскольку синтетические члены обычно не являются `public`.

Поскольку класс [`Field`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html) реализует интерфейс [`java.lang.reflect.AnnotatedElement`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AnnotatedElement.html), можно получить любую аннотацию времени выполнения с политикой удержания [`java.lang.annotation.RetentionPolicy.RUNTIME`](https://docs.oracle.com/javase/8/docs/api/java/lang/annotation/RetentionPolicy.html#RUNTIME). Пример получения аннотаций см. в разделе *Examining Class Modifiers and Types* (см. урок 1).

### Получение и установка значений поля

Имея экземпляр класса, можно с помощью рефлексии устанавливать значения полей этого класса. Обычно это делается лишь в особых обстоятельствах, когда установить значения привычным способом невозможно. Поскольку такой доступ, как правило, нарушает проектные намерения класса, использовать его следует с максимальной осторожностью.

Класс `Book` иллюстрирует, как устанавливать значения для полей типа `long`, массива и перечисления. Методы для получения и установки других примитивных типов описаны в документации класса [`Field`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#method_summary).

```java
import java.lang.reflect.Field;
import java.util.Arrays;
import static java.lang.System.out;

enum Tweedle { DEE, DUM }

public class Book {
    public long chapters = 0;
    public String[] characters = { "Alice", "White Rabbit" };
    public Tweedle twin = Tweedle.DEE;

    public static void main(String... args) {
	Book book = new Book();
	String fmt = "%6S:  %-12s = %s%n";

	try {
	    Class<?> c = book.getClass();

	    Field chap = c.getDeclaredField("chapters");
	    out.format(fmt, "before", "chapters", book.chapters);
  	    chap.setLong(book, 12);
	    out.format(fmt, "after", "chapters", chap.getLong(book));

	    Field chars = c.getDeclaredField("characters");
	    out.format(fmt, "before", "characters",
		       Arrays.asList(book.characters));
	    String[] newChars = { "Queen", "King" };
	    chars.set(book, newChars);
	    out.format(fmt, "after", "characters",
		       Arrays.asList(book.characters));

	    Field t = c.getDeclaredField("twin");
	    out.format(fmt, "before", "twin", book.twin);
	    t.set(book, Tweedle.DUM);
	    out.format(fmt, "after", "twin", t.get(book));

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

Соответствующий вывод:

```
$ java Book
BEFORE:  chapters     = 0
 AFTER:  chapters     = 12
BEFORE:  characters   = [Alice, White Rabbit]
 AFTER:  characters   = [Queen, King]
BEFORE:  twin         = DEE
 AFTER:  twin         = DUM
```

> **Примечание.** Установка значения поля через рефлексию связана с определёнными накладными расходами на производительность, поскольку должны выполняться различные операции, например проверка прав доступа. С точки зрения среды выполнения эффект тот же, и операция настолько же атомарна, как если бы значение было изменено непосредственно в коде класса.

Использование рефлексии может приводить к потере некоторых оптимизаций времени выполнения. Например, следующий код с большой вероятностью будет оптимизирован виртуальной машиной Java:

```java
int x = 1;
x = 2;
x = 3;
```

Эквивалентный код, использующий `Field.set*()`, может оптимизирован не быть.

### Решение проблем (поля)

Ниже приведены несколько распространённых проблем, с которыми сталкиваются разработчики, с объяснением причин их возникновения и способов решения.

#### IllegalArgumentException из-за непреобразуемых типов

Пример `FieldTrouble` порождает исключение [`IllegalArgumentException`](https://docs.oracle.com/javase/8/docs/api/java/lang/IllegalArgumentException.html). Метод [`Field.setInt()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#setInt-java.lang.Object-int-) вызывается для установки поля ссылочного типа `Integer` значением примитивного типа. В нерефлективном эквиваленте `Integer val = 42` компилятор преобразовал бы (упаковал, *box*) примитивное значение `42` в ссылочный тип как `new Integer(42)`, чтобы проверка типов приняла оператор. При использовании рефлексии проверка типов происходит только во время выполнения, поэтому возможности упаковать значение нет.

```java
import java.lang.reflect.Field;

public class FieldTrouble {
    public Integer val;

    public static void main(String... args) {
	FieldTrouble ft = new FieldTrouble();
	try {
	    Class<?> c = ft.getClass();
	    Field f = c.getDeclaredField("val");
  	    f.setInt(ft, 42);               // IllegalArgumentException

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
 	} catch (IllegalAccessException x) {
 	    x.printStackTrace();
	}
    }
}
```

```
$ java FieldTrouble
Exception in thread "main" java.lang.IllegalArgumentException: Can not set
  java.lang.Object field FieldTrouble.val to (long)42
        at sun.reflect.UnsafeFieldAccessorImpl.throwSetIllegalArgumentException
          (UnsafeFieldAccessorImpl.java:146)
        at sun.reflect.UnsafeFieldAccessorImpl.throwSetIllegalArgumentException
          (UnsafeFieldAccessorImpl.java:174)
        at sun.reflect.UnsafeObjectFieldAccessorImpl.setLong
          (UnsafeObjectFieldAccessorImpl.java:102)
        at java.lang.reflect.Field.setLong(Field.java:831)
        at FieldTrouble.main(FieldTrouble.java:11)
```

Чтобы устранить это исключение, проблемную строку следует заменить следующим вызовом [`Field.set(Object obj, Object value)`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Field.html#set-java.lang.Object-java.lang.Object-):

```java
f.set(ft, new Integer(43));
```

> **Совет.** При использовании рефлексии для установки или получения значения поля компилятор не имеет возможности выполнить упаковку (*boxing*). Он может преобразовывать только типы, связанные так, как описано в спецификации метода [`Class.isAssignableFrom()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#isAssignableFrom-java.lang.Class-). Ожидается, что пример завершится с ошибкой, поскольку `isAssignableFrom()` вернёт `false` в этой проверке; данную проверку можно использовать программно, чтобы убедиться в возможности конкретного преобразования:
>
> ```java
> Integer.class.isAssignableFrom(int.class) == false
> ```
>
> Аналогично автоматическое преобразование из примитивного типа в ссылочный также невозможно в рефлексии:
>
> ```java
> int.class.isAssignableFrom(Integer.class) == false
> ```

#### NoSuchFieldException для непубличных полей

Внимательный читатель может заметить, что если приведённый ранее пример `FieldSpy` использовать для получения информации о непубличном поле, он завершится с ошибкой:

```
$ java FieldSpy java.lang.String count
java.lang.NoSuchFieldException: count
        at java.lang.Class.getField(Class.java:1519)
        at FieldSpy.main(FieldSpy.java:12)
```

> **Совет.** Методы [`Class.getField()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getField-java.lang.String-) и [`Class.getFields()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getFields--) возвращают **public**-поля класса, перечисления или интерфейса, представленного объектом `Class`. Чтобы получить все поля, объявленные (но не унаследованные) в `Class`, используйте метод [`Class.getDeclaredFields()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getDeclaredFields--).

#### IllegalAccessException при изменении final-полей

Исключение [`IllegalAccessException`](https://docs.oracle.com/javase/8/docs/api/java/lang/IllegalAccessException.html) может быть выброшено при попытке получить или установить значение `private`-поля либо иного недоступного поля, а также при попытке установить значение `final`-поля (независимо от его модификаторов доступа).

Пример `FieldTroubleToo` иллюстрирует трассировку стека, возникающую при попытке установить final-поле.

```java
import java.lang.reflect.Field;

public class FieldTroubleToo {
    public final boolean b = true;

    public static void main(String... args) {
	FieldTroubleToo ft = new FieldTroubleToo();
	try {
	    Class<?> c = ft.getClass();
	    Field f = c.getDeclaredField("b");
// 	    f.setAccessible(true);  // решение
	    f.setBoolean(ft, Boolean.FALSE);   // IllegalAccessException

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	} catch (IllegalArgumentException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java FieldTroubleToo
java.lang.IllegalAccessException: Can not set final boolean field
  FieldTroubleToo.b to (boolean)false
        at sun.reflect.UnsafeFieldAccessorImpl.
          throwFinalFieldIllegalAccessException(UnsafeFieldAccessorImpl.java:55)
        at sun.reflect.UnsafeFieldAccessorImpl.
          throwFinalFieldIllegalAccessException(UnsafeFieldAccessorImpl.java:63)
        at sun.reflect.UnsafeQualifiedBooleanFieldAccessorImpl.setBoolean
          (UnsafeQualifiedBooleanFieldAccessorImpl.java:78)
        at java.lang.reflect.Field.setBoolean(Field.java:686)
        at FieldTroubleToo.main(FieldTroubleToo.java:12)
```

> **Совет.** Существует ограничение доступа, которое не позволяет устанавливать `final`-поля после инициализации класса. Однако `Field` объявлен как расширяющий [`AccessibleObject`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AccessibleObject.html), который предоставляет возможность подавить эту проверку.
>
> Если вызов [`AccessibleObject.setAccessible()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AccessibleObject.html#setAccessible-boolean-) завершается успешно, то последующие операции со значением этого поля не будут давать сбой из-за указанной проблемы. Это может иметь неожиданные побочные эффекты; например, иногда исходное значение будет продолжать использоваться некоторыми частями приложения, хотя значение уже было изменено. Вызов [`AccessibleObject.setAccessible()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AccessibleObject.html#setAccessible-boolean-) завершится успешно только в том случае, если операция разрешена контекстом безопасности.

---

## Методы (Methods)

У методов есть возвращаемые значения, параметры, и они могут выбрасывать исключения. Класс [`java.lang.reflect.Method`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html) предоставляет методы для получения информации о типах параметров и возвращаемого значения. Он также может использоваться для вызова методов у заданного объекта.

### Получение информации о типах метода

Объявление метода включает имя, модификаторы, параметры, тип возвращаемого значения и список выбрасываемых исключений. Класс [`java.lang.reflect.Method`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html) предоставляет способ получить эту информацию.

Пример `MethodSpy` иллюстрирует, как перечислить все методы, объявленные в заданном классе, и получить типы возвращаемого значения, параметров и исключений для всех методов с заданным именем.

```java
import java.lang.reflect.Method;
import java.lang.reflect.Type;
import static java.lang.System.out;

public class MethodSpy {
    private static final String  fmt = "%24s: %s%n";

    // для особо любопытных
    <E extends RuntimeException> void genericThrow() throws E {}

    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    Method[] allMethods = c.getDeclaredMethods();
	    for (Method m : allMethods) {
		if (!m.getName().equals(args[1])) {
		    continue;
		}
		out.format("%s%n", m.toGenericString());

		out.format(fmt, "ReturnType", m.getReturnType());
		out.format(fmt, "GenericReturnType", m.getGenericReturnType());

		Class<?>[] pType  = m.getParameterTypes();
		Type[] gpType = m.getGenericParameterTypes();
		for (int i = 0; i < pType.length; i++) {
		    out.format(fmt,"ParameterType", pType[i]);
		    out.format(fmt,"GenericParameterType", gpType[i]);
		}

		Class<?>[] xType  = m.getExceptionTypes();
		Type[] gxType = m.getGenericExceptionTypes();
		for (int i = 0; i < xType.length; i++) {
		    out.format(fmt,"ExceptionType", xType[i]);
		    out.format(fmt,"GenericExceptionType", gxType[i]);
		}
	    }

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

Вот вывод для метода [`Class.getConstructor()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getConstructor-java.lang.Class...-) — примера метода с параметризованными типами и переменным числом параметров.

```
$ java MethodSpy java.lang.Class getConstructor
public java.lang.reflect.Constructor<T> java.lang.Class.getConstructor
  (java.lang.Class<?>[]) throws java.lang.NoSuchMethodException,
  java.lang.SecurityException
              ReturnType: class java.lang.reflect.Constructor
       GenericReturnType: java.lang.reflect.Constructor<T>
           ParameterType: class [Ljava.lang.Class;
    GenericParameterType: java.lang.Class<?>[]
           ExceptionType: class java.lang.NoSuchMethodException
    GenericExceptionType: class java.lang.NoSuchMethodException
           ExceptionType: class java.lang.SecurityException
    GenericExceptionType: class java.lang.SecurityException
```

Вот фактическое объявление этого метода в исходном коде:

```java
public Constructor<T> getConstructor(Class<?>... parameterTypes)
```

Сначала обратите внимание, что типы возвращаемого значения и параметров являются обобщёнными. Метод [`Method.getGenericReturnType()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#getGenericReturnType--) обращается к атрибуту сигнатуры (*Signature Attribute*) в файле класса, если он присутствует. Если атрибут недоступен, метод возвращается к [`Method.getReturnType()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#getReturnType--), который не изменился с появлением обобщений. Остальные методы рефлексии с именем вида `getGenericFoo()` реализованы аналогично.

Затем обратите внимание, что последний (и единственный) параметр `parameterType` имеет переменную арность (*variable arity*, переменное число параметров) типа `java.lang.Class`. Он представлен как одномерный массив типа `java.lang.Class`. Это можно отличить от параметра, который явно является массивом `java.lang.Class`, вызвав [`Method.isVarArgs()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#isVarArgs--). Синтаксис возвращаемых значений `Method.get*Types()` описан в [`Class.getName()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getName--).

Следующий пример иллюстрирует метод с обобщённым типом возвращаемого значения.

```
$ java MethodSpy java.lang.Class cast
public T java.lang.Class.cast(java.lang.Object)
              ReturnType: class java.lang.Object
       GenericReturnType: T
           ParameterType: class java.lang.Object
    GenericParameterType: class java.lang.Object
```

Обобщённый тип возвращаемого значения метода [`Class.cast()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#cast-java.lang.Object-) сообщается как `java.lang.Object`, потому что обобщения реализованы через **стирание типов** (*type erasure*), которое удаляет всю информацию об обобщённых типах во время компиляции. Стирание `T` определяется объявлением класса [`Class`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html):

```java
public final class Class<T> implements ...
```

Таким образом, `T` заменяется на верхнюю границу переменной типа — в данном случае на `java.lang.Object`.

Последний пример иллюстрирует вывод для метода с несколькими перегрузками (*overloads*).

```
$ java MethodSpy java.io.PrintStream format
public java.io.PrintStream java.io.PrintStream.format
  (java.util.Locale,java.lang.String,java.lang.Object[])
              ReturnType: class java.io.PrintStream
       GenericReturnType: class java.io.PrintStream
           ParameterType: class java.util.Locale
    GenericParameterType: class java.util.Locale
           ParameterType: class java.lang.String
    GenericParameterType: class java.lang.String
           ParameterType: class [Ljava.lang.Object;
    GenericParameterType: class [Ljava.lang.Object;
public java.io.PrintStream java.io.PrintStream.format
  (java.lang.String,java.lang.Object[])
              ReturnType: class java.io.PrintStream
       GenericReturnType: class java.io.PrintStream
           ParameterType: class java.lang.String
    GenericParameterType: class java.lang.String
           ParameterType: class [Ljava.lang.Object;
    GenericParameterType: class [Ljava.lang.Object;
```

Если обнаружено несколько перегрузок метода с одним именем, все они возвращаются методом [`Class.getDeclaredMethods()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getDeclaredMethods--). Поскольку у `format()` две перегрузки (с параметром [`Locale`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html) и без него), обе показаны `MethodSpy`.

> **Примечание.** Метод [`Method.getGenericExceptionTypes()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#getGenericExceptionTypes--) существует потому, что на самом деле возможно объявить метод с обобщённым типом исключения. Однако это используется редко, поскольку перехватить обобщённый тип исключения невозможно.

### Получение имён параметров метода

Имена формальных параметров любого метода или конструктора можно получить с помощью метода [`java.lang.reflect.Executable.getParameters`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Executable.html#getParameters--). (Классы [`Method`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html) и [`Constructor`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Executable.html) расширяют класс [`Executable`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Executable.html) и потому наследуют метод `Executable.getParameters`.) Однако `.class`-файлы по умолчанию не хранят имена формальных параметров. Это связано с тем, что многие инструменты, создающие и потребляющие файлы классов, могут не быть рассчитаны на больший статический и динамический объём `.class`-файлов, содержащих имена параметров. В частности, такие инструменты должны были бы обрабатывать `.class`-файлы большего размера, а виртуальная машина Java (JVM) использовала бы больше памяти. Кроме того, некоторые имена параметров, такие как `secret` или `password`, могут раскрывать информацию о методах, чувствительных к безопасности.

Чтобы сохранять имена формальных параметров в конкретном `.class`-файле и тем самым позволить Reflection API извлекать их, скомпилируйте исходный файл с опцией `-parameters` компилятора `javac`.

Пример `MethodParameterSpy` иллюстрирует, как получить имена формальных параметров всех конструкторов и методов заданного класса. Пример также выводит другую информацию о каждом параметре.

Следующая команда выводит имена формальных параметров конструкторов и методов класса `ExampleMethods`. **Примечание.** Не забудьте скомпилировать пример `ExampleMethods` с опцией компилятора `-parameters`:

*java MethodParameterSpy ExampleMethods*

Эта команда выводит следующее:

```
Number of constructors: 1

Constructor #1
public ExampleMethods()

Number of declared constructors: 1

Declared constructor #1
public ExampleMethods()

Number of methods: 4

Method #1
public boolean ExampleMethods.simpleMethod(java.lang.String,int)
             Return type: boolean
     Generic return type: boolean
         Parameter class: class java.lang.String
          Parameter name: stringParam
               Modifiers: 0
            Is implicit?: false
        Is name present?: true
           Is synthetic?: false
         Parameter class: int
          Parameter name: intParam
               Modifiers: 0
            Is implicit?: false
        Is name present?: true
           Is synthetic?: false

Method #2
public int ExampleMethods.varArgsMethod(java.lang.String...)
             Return type: int
     Generic return type: int
         Parameter class: class [Ljava.lang.String;
          Parameter name: manyStrings
               Modifiers: 0
            Is implicit?: false
        Is name present?: true
           Is synthetic?: false

Method #3
public boolean ExampleMethods.methodWithList(java.util.List<java.lang.String>)
             Return type: boolean
     Generic return type: boolean
         Parameter class: interface java.util.List
          Parameter name: listParam
               Modifiers: 0
            Is implicit?: false
        Is name present?: true
           Is synthetic?: false

Method #4
public <T> void ExampleMethods.genericMethod(T[],java.util.Collection<T>)
             Return type: void
     Generic return type: void
         Parameter class: class [Ljava.lang.Object;
          Parameter name: a
               Modifiers: 0
            Is implicit?: false
        Is name present?: true
           Is synthetic?: false
         Parameter class: interface java.util.Collection
          Parameter name: c
               Modifiers: 0
            Is implicit?: false
        Is name present?: true
           Is synthetic?: false
```

Пример `MethodParameterSpy` использует следующие методы класса [`Parameter`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html):

- [`getType`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html#getType--): возвращает объект [`Class`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html), идентифицирующий объявленный тип параметра.

- [`getName`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html#getName--): возвращает имя параметра. Если имя параметра присутствует, то этот метод возвращает имя, указанное в `.class`-файле. В противном случае метод синтезирует имя вида `argN`, где *N* — индекс параметра в дескрипторе объявляющего его метода.

  Например, предположим, что вы скомпилировали класс `ExampleMethods` без указания опции компилятора `-parameters`. Тогда пример `MethodParameterSpy` вывел бы для метода `ExampleMethods.simpleMethod` следующее:

  ```
  public boolean ExampleMethods.simpleMethod(java.lang.String,int)
               Return type: boolean
       Generic return type: boolean
           Parameter class: class java.lang.String
            Parameter name: arg0
                 Modifiers: 0
              Is implicit?: false
          Is name present?: false
             Is synthetic?: false
           Parameter class: int
            Parameter name: arg1
                 Modifiers: 0
              Is implicit?: false
          Is name present?: false
             Is synthetic?: false
  ```

- [`getModifiers`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html#getModifiers--): возвращает целое число, представляющее различные характеристики формального параметра. Это значение является суммой следующих величин, если они применимы к формальному параметру:

  | Значение (десятичное) | Значение (шестнадцатеричное) | Описание |
  |---|---|---|
  | 16 | 0x0010 | Формальный параметр объявлен как `final` |
  | 4096 | 0x1000 | Формальный параметр синтетический. Альтернативно можно вызвать метод `isSynthetic`. |
  | 32768 | 0x8000 | Параметр неявно объявлен в исходном коде. Альтернативно можно вызвать метод `isImplicit`. |

- [`isImplicit`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html#isImplicit--): возвращает `true`, если этот параметр неявно объявлен в исходном коде. Подробнее см. раздел «Неявные и синтетические параметры».

- [`isNamePresent`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html#isNamePresent--): возвращает `true`, если параметр имеет имя согласно `.class`-файлу.

- [`isSynthetic`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Parameter.html#isSynthetic--): возвращает `true`, если этот параметр не объявлен ни неявно, ни явно в исходном коде. Подробнее см. раздел «Неявные и синтетические параметры».

#### Неявные и синтетические параметры

Некоторые конструкции неявно объявляются в исходном коде, если они не написаны явно. Например, пример `ExampleMethods` не содержит конструктора. Для него неявно объявляется конструктор по умолчанию. Пример `MethodParameterSpy` выводит информацию о неявно объявленном конструкторе `ExampleMethods`:

```
Number of declared constructors: 1
public ExampleMethods()
```

Рассмотрим следующий фрагмент из `MethodParameterExamples`:

```java
public class MethodParameterExamples {
    public class InnerClass { }
}
```

Класс `InnerClass` является нестатическим [вложенным классом](https://docs.oracle.com/javase/tutorial/java/javaOO/nested.html), или внутренним классом. Конструктор для внутренних классов также объявляется неявно. Однако этот конструктор будет содержать параметр. Когда компилятор Java компилирует `InnerClass`, он создаёт `.class`-файл, представляющий код, подобный следующему:

```java
public class MethodParameterExamples {
    public class InnerClass {
        final MethodParameterExamples parent;
        InnerClass(final MethodParameterExamples this$0) {
            parent = this$0; 
        }
    }
}
```

Конструктор `InnerClass` содержит параметр, тип которого — класс, охватывающий `InnerClass`, то есть `MethodParameterExamples`. Следовательно, пример `MethodParameterExamples` выводит следующее:

```
public MethodParameterExamples$InnerClass(MethodParameterExamples)
         Parameter class: class MethodParameterExamples
          Parameter name: this$0
               Modifiers: 32784
            Is implicit?: true
        Is name present?: true
           Is synthetic?: false
```

Поскольку конструктор класса `InnerClass` объявлен неявно, его параметр также является неявным.

> **Примечание.**
>
> - Компилятор Java создаёт формальный параметр для конструктора внутреннего класса, чтобы иметь возможность передать ссылку (представляющую непосредственно охватывающий экземпляр) из выражения создания в конструктор класса-члена.
> - Значение 32784 означает, что параметр конструктора `InnerClass` является одновременно `final` (16) и неявным (32768).
> - Язык программирования Java допускает имена переменных со знаками доллара (`$`); однако по соглашению знаки доллара в именах переменных не используются.

Конструкции, генерируемые компилятором Java, помечаются как **синтетические** (*synthetic*), если они не соответствуют конструкции, объявленной явно или неявно в исходном коде, — за исключением методов инициализации класса. Синтетические конструкции — это артефакты, генерируемые компиляторами, которые различаются между реализациями. Рассмотрим следующий фрагмент из `MethodParameterExamples`:

```java
public class MethodParameterExamples {
    enum Colors {
        RED, WHITE;
    }
}
```

Когда компилятор Java встречает конструкцию `enum`, он создаёт несколько методов, совместимых со структурой `.class`-файла и обеспечивающих ожидаемую функциональность конструкции `enum`. Например, компилятор Java создал бы для конструкции `enum` `Colors` `.class`-файл, представляющий код, подобный следующему:

```java
final class Colors extends java.lang.Enum<Colors> {
    public final static Colors RED = new Colors("RED", 0);
    public final static Colors BLUE = new Colors("WHITE", 1);
 
    private final static values = new Colors[]{ RED, BLUE };
 
    private Colors(String name, int ordinal) {
        super(name, ordinal);
    }
 
    public static Colors[] values(){
        return values;
    }
 
    public static Colors valueOf(String name){
        return (Colors)java.lang.Enum.valueOf(Colors.class, name);
    }
}
```

Компилятор Java создаёт три конструктора и метода для этой конструкции `enum`: `Colors(String name, int ordinal)`, `Colors[] values()` и `Colors valueOf(String name)`. Методы `values` и `valueOf` объявлены неявно. Следовательно, имена их формальных параметров тоже объявлены неявно.

Конструктор перечисления `Colors(String name, int ordinal)` является конструктором по умолчанию и объявлен неявно. Однако формальные параметры этого конструктора (`name` и `ordinal`) **не** объявлены неявно. Поскольку эти формальные параметры не объявлены ни явно, ни неявно, они синтетические. (Формальные параметры конструктора по умолчанию конструкции `enum` не объявлены неявно, потому что разные компиляторы не обязаны соглашаться о форме этого конструктора; другой компилятор Java мог бы задать для него иные формальные параметры. Компилируя выражения, использующие константы `enum`, компиляторы полагаются только на public-static-поля конструкции `enum`, которые объявлены неявно, а не на её конструкторы или способ инициализации этих констант.)

Следовательно, пример `MethodParameterExample` выводит о конструкции `enum` `Colors` следующее:

```
enum Colors:

Number of constructors: 0

Number of declared constructors: 1

Declared constructor #1
private MethodParameterExamples$Colors()
         Parameter class: class java.lang.String
          Parameter name: $enum$name
               Modifiers: 4096
            Is implicit?: false
        Is name present?: true
           Is synthetic?: true
         Parameter class: int
          Parameter name: $enum$ordinal
               Modifiers: 4096
            Is implicit?: false
        Is name present?: true
           Is synthetic?: true

Number of methods: 2

Method #1
public static MethodParameterExamples$Colors[]
    MethodParameterExamples$Colors.values()
             Return type: class [LMethodParameterExamples$Colors;
     Generic return type: class [LMethodParameterExamples$Colors;

Method #2
public static MethodParameterExamples$Colors
    MethodParameterExamples$Colors.valueOf(java.lang.String)
             Return type: class MethodParameterExamples$Colors
     Generic return type: class MethodParameterExamples$Colors
         Parameter class: class java.lang.String
          Parameter name: name
               Modifiers: 32768
            Is implicit?: true
        Is name present?: true
           Is synthetic?: false
```

Подробнее о неявно объявленных конструкциях, включая параметры, которые в Reflection API выглядят как неявные, см. [Java Language Specification](https://docs.oracle.com/javase/specs/).

### Получение и разбор модификаторов метода

В объявлении метода могут присутствовать несколько модификаторов:

- Модификаторы доступа: `public`, `protected` и `private`.
- Модификатор, ограничивающий метод одним экземпляром: `static`.
- Модификатор, запрещающий изменение значения: `final`.
- Модификатор, требующий переопределения: `abstract`.
- Модификатор, предотвращающий повторный вход (*reentrancy*): `synchronized`.
- Модификатор, указывающий на реализацию на другом языке программирования: `native`.
- Модификатор, принуждающий к строгому поведению чисел с плавающей точкой: `strictfp`.
- Аннотации.

Пример `MethodModifierSpy` перечисляет модификаторы метода с заданным именем. Он также показывает, является ли метод синтетическим (*synthetic*, сгенерированным компилятором), с переменной арностью или мостовым (*bridge*) методом (сгенерированным компилятором для поддержки обобщённых интерфейсов).

```java
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import static java.lang.System.out;

public class MethodModifierSpy {

    private static int count;
    private static synchronized void inc() { count++; }
    private static synchronized int cnt() { return count; }

    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    Method[] allMethods = c.getDeclaredMethods();
	    for (Method m : allMethods) {
		if (!m.getName().equals(args[1])) {
		    continue;
		}
		out.format("%s%n", m.toGenericString());
		out.format("  Modifiers:  %s%n",
			   Modifier.toString(m.getModifiers()));
		out.format("  [ synthetic=%-5b var_args=%-5b bridge=%-5b ]%n",
			   m.isSynthetic(), m.isVarArgs(), m.isBridge());
		inc();
	    }
	    out.format("%d matching overload%s found%n", cnt(),
		       (cnt() == 1 ? "" : "s"));

        // в реальном коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

Несколько примеров вывода `MethodModifierSpy`:

```
$ java MethodModifierSpy java.lang.Object wait
public final void java.lang.Object.wait() throws java.lang.InterruptedException
  Modifiers:  public final
  [ synthetic=false var_args=false bridge=false ]
public final void java.lang.Object.wait(long,int)
  throws java.lang.InterruptedException
  Modifiers:  public final
  [ synthetic=false var_args=false bridge=false ]
public final native void java.lang.Object.wait(long)
  throws java.lang.InterruptedException
  Modifiers:  public final native
  [ synthetic=false var_args=false bridge=false ]
3 matching overloads found

$ java MethodModifierSpy java.lang.StrictMath toRadians
public static double java.lang.StrictMath.toRadians(double)
  Modifiers:  public static strictfp
  [ synthetic=false var_args=false bridge=false ]
1 matching overload found

$ java MethodModifierSpy MethodModifierSpy inc
private synchronized void MethodModifierSpy.inc()
  Modifiers: private synchronized
  [ synthetic=false var_args=false bridge=false ]
1 matching overload found

$ java MethodModifierSpy java.lang.Class getConstructor
public java.lang.reflect.Constructor<T> java.lang.Class.getConstructor
  (java.lang.Class<T>[]) throws java.lang.NoSuchMethodException,
  java.lang.SecurityException
  Modifiers: public transient
  [ synthetic=false var_args=true bridge=false ]
1 matching overload found

$ java MethodModifierSpy java.lang.String compareTo
public int java.lang.String.compareTo(java.lang.String)
  Modifiers: public
  [ synthetic=false var_args=false bridge=false ]
public int java.lang.String.compareTo(java.lang.Object)
  Modifiers: public volatile
  [ synthetic=true  var_args=false bridge=true  ]
2 matching overloads found
```

Обратите внимание, что [`Method.isVarArgs()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#isVarArgs--) возвращает `true` для [`Class.getConstructor()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getConstructor-java.lang.Class...-). Это означает, что объявление метода выглядит так:

```java
public Constructor<T> getConstructor(Class<?>... parameterTypes)
```

а не так:

```java
public Constructor<T> getConstructor(Class<?> [] parameterTypes)
```

Заметьте, что вывод для [`String.compareTo()`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#compareTo-java.lang.String-) содержит два метода. Метод, объявленный в `String.java`:

```java
public int compareTo(String anotherString);
```

и второй **синтетический**, или сгенерированный компилятором, **мостовой** (*bridge*) метод. Это происходит потому, что [`String`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html) реализует параметризованный интерфейс [`Comparable`](https://docs.oracle.com/javase/8/docs/api/java/lang/Comparable.html). При стирании типов тип аргумента унаследованного метода [`Comparable.compareTo()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Comparable.html#compareTo-T-) меняется с `java.lang.Object` на `java.lang.String`. Поскольку после стирания типы параметров методов `compareTo` в `Comparable` и `String` больше не совпадают, переопределение (*overriding*) не может произойти. При любых других обстоятельствах это привело бы к ошибке компиляции, поскольку интерфейс оказался бы не реализован. Добавление мостового метода устраняет эту проблему.

Класс [`Method`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html) реализует [`java.lang.reflect.AnnotatedElement`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AnnotatedElement.html). Таким образом, можно получить любые аннотации времени выполнения с политикой удержания [`java.lang.annotation.RetentionPolicy.RUNTIME`](https://docs.oracle.com/javase/8/docs/api/java/lang/annotation/RetentionPolicy.html#RUNTIME). Пример получения аннотаций см. в разделе *Examining Class Modifiers and Types* (см. урок 1).

### Вызов методов

Рефлексия предоставляет средство для вызова методов класса. Обычно это требуется только в том случае, когда в нерефлективном коде невозможно привести экземпляр класса к нужному типу. Методы вызываются с помощью [`java.lang.reflect.Method.invoke()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#invoke-java.lang.Object-java.lang.Object...-). Первый аргумент — это экземпляр объекта, у которого вызывается данный метод. (Если метод `static`, первым аргументом должен быть `null`.) Последующие аргументы — это параметры метода. Если базовый метод выбрасывает исключение, оно будет обёрнуто в [`java.lang.reflect.InvocationTargetException`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationTargetException.html). Исходное исключение метода можно получить с помощью механизма цепочек исключений — метода [`InvocationTargetException.getCause()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationTargetException.html#getCause--).

#### Поиск и вызов метода с конкретным объявлением

Рассмотрим набор тестов, который использует рефлексию для вызова приватных тестовых методов заданного класса. Пример `Deet` ищет `public`-методы класса, которые начинаются со строки «`test`», имеют тип возвращаемого значения `boolean` и единственный параметр типа [`Locale`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html). Затем он вызывает каждый подходящий метод.

```java
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Type;
import java.util.Locale;
import static java.lang.System.out;
import static java.lang.System.err;

public class Deet<T> {
    private boolean testDeet(Locale l) {
	// getISO3Language() может выбросить MissingResourceException
	out.format("Locale = %s, ISO Language Code = %s%n", l.getDisplayName(), l.getISO3Language());
	return true;
    }

    private int testFoo(Locale l) { return 0; }
    private boolean testBar() { return true; }

    public static void main(String... args) {
	if (args.length != 4) {
	    err.format("Usage: java Deet <classname> <langauge> <country> <variant>%n");
	    return;
	}

	try {
	    Class<?> c = Class.forName(args[0]);
	    Object t = c.newInstance();

	    Method[] allMethods = c.getDeclaredMethods();
	    for (Method m : allMethods) {
		String mname = m.getName();
		if (!mname.startsWith("test")
		    || (m.getGenericReturnType() != boolean.class)) {
		    continue;
		}
 		Type[] pType = m.getGenericParameterTypes();
 		if ((pType.length != 1)
		    || Locale.class.isAssignableFrom(pType[0].getClass())) {
 		    continue;
 		}

		out.format("invoking %s()%n", mname);
		try {
		    m.setAccessible(true);
		    Object o = m.invoke(t, new Locale(args[1], args[2], args[3]));
		    out.format("%s() returned %b%n", mname, (Boolean) o);

		// Обрабатываем любые исключения, выброшенные вызываемым методом.
		} catch (InvocationTargetException x) {
		    Throwable cause = x.getCause();
		    err.format("invocation of %s failed: %s%n",
			       mname, cause.getMessage());
		}
	    }

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

`Deet` вызывает [`getDeclaredMethods()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getDeclaredMethods--), который возвращает все методы, явно объявленные в классе. Кроме того, [`Class.isAssignableFrom()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#isAssignableFrom-java.lang.Class-) используется для проверки совместимости параметров найденного метода с желаемым вызовом. Технически код мог бы проверить, истинно ли следующее выражение, поскольку [`Locale`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html) является `final`:

```java
Locale.class == pType[0].getClass()
```

Однако [`Class.isAssignableFrom()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#isAssignableFrom-java.lang.Class-) более универсален.

```
$ java Deet Deet ja JP JP
invoking testDeet()
Locale = Japanese (Japan,JP), 
ISO Language Code = jpn
testDeet() returned true

$ java Deet Deet xx XX XX
invoking testDeet()
invocation of testDeet failed: 
Couldn't find 3-letter language code for xx
```

Во-первых, обратите внимание, что только `testDeet()` удовлетворяет ограничениям объявления, накладываемым кодом. Во-вторых, когда `testDeet()` получает недопустимый аргумент, он выбрасывает непроверяемое (*unchecked*) исключение [`java.util.MissingResourceException`](https://docs.oracle.com/javase/8/docs/api/java/util/MissingResourceException.html). В рефлексии нет различия в обработке проверяемых (*checked*) и непроверяемых исключений. Все они обёртываются в [`InvocationTargetException`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationTargetException.html).

#### Вызов методов с переменным числом аргументов

Метод [`Method.invoke()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#invoke-java.lang.Object-java.lang.Object...-) можно использовать для передачи переменного числа аргументов методу. Ключевая идея, которую нужно понять, состоит в том, что методы с переменной арностью реализованы так, как если бы переменные аргументы были упакованы в массив.

Пример `InvokeMain` иллюстрирует, как вызвать точку входа `main()` в любом классе и передать набор аргументов, определяемых во время выполнения.

```java
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Arrays;

public class InvokeMain {
    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    Class[] argTypes = new Class[] { String[].class };
	    Method main = c.getDeclaredMethod("main", argTypes);
  	    String[] mainArgs = Arrays.copyOfRange(args, 1, args.length);
	    System.out.format("invoking %s.main()%n", c.getName());
	    main.invoke(null, (Object)mainArgs);

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	}
    }
}
```

Сначала, чтобы найти метод `main()`, код ищет метод с именем «main» с единственным параметром, который является массивом [`String`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html). Поскольку `main()` является `static`, первый аргумент [`Method.invoke()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#invoke-java.lang.Object-java.lang.Object...-) — `null`. Второй аргумент — это массив передаваемых аргументов.

```
$ java InvokeMain Deet Deet ja JP JP
invoking Deet.main()
invoking testDeet()
Locale = Japanese (Japan,JP), 
ISO Language Code = jpn
testDeet() returned true
```

### Решение проблем (методы)

Этот раздел содержит примеры проблем, с которыми разработчики могут столкнуться, используя рефлексию для поиска, вызова или получения информации о методах.

#### NoSuchMethodException из-за стирания типов

Пример `MethodTrouble` иллюстрирует, что происходит, когда стирание типов не учитывается кодом, который ищет конкретный метод в классе.

```java
import java.lang.reflect.Method;

public class MethodTrouble<T>  {
    public void lookup(T t) {}
    public void find(Integer i) {}

    public static void main(String... args) {
	try {
	    String mName = args[0];
	    Class cArg = Class.forName(args[1]);
	    Class<?> c = (new MethodTrouble<Integer>()).getClass();
	    Method m = c.getMethod(mName, cArg);
	    System.out.format("Found:%n  %s%n", m.toGenericString());

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java MethodTrouble lookup java.lang.Integer
java.lang.NoSuchMethodException: MethodTrouble.lookup(java.lang.Integer)
        at java.lang.Class.getMethod(Class.java:1605)
        at MethodTrouble.main(MethodTrouble.java:12)

$ java MethodTrouble lookup java.lang.Object
Found:
  public void MethodTrouble.lookup(T)
```

Когда метод объявлен с обобщённым типом параметра, компилятор заменяет обобщённый тип его верхней границей — в данном случае верхняя граница `T` есть `Object`. Поэтому когда код ищет `lookup(Integer)`, метод не находится, несмотря на то что экземпляр `MethodTrouble` был создан так:

```java
Class<?> c = (new MethodTrouble<Integer>()).getClass();
```

Поиск `lookup(Object)` ожидаемо завершается успехом.

```
$ java MethodTrouble find java.lang.Integer
Found:
  public void MethodTrouble.find(java.lang.Integer)
$ java MethodTrouble find java.lang.Object
java.lang.NoSuchMethodException: MethodTrouble.find(java.lang.Object)
        at java.lang.Class.getMethod(Class.java:1605)
        at MethodTrouble.main(MethodTrouble.java:12)
```

В этом случае у `find()` нет обобщённых параметров, поэтому типы параметров, искомые `getMethod()`, должны совпадать точно.

> **Совет.** Всегда передавайте верхнюю границу параметризованного типа при поиске метода.

#### IllegalAccessException при вызове метода

Исключение `IllegalAccessException` выбрасывается при попытке вызвать `private` или иной недоступный метод.

Пример `MethodTroubleAgain` показывает типичную трассировку стека, возникающую при попытке вызвать приватный метод в другом классе.

```java
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

class AnotherClass {
    private void m() {}
}

public class MethodTroubleAgain {
    public static void main(String... args) {
	AnotherClass ac = new AnotherClass();
	try {
	    Class<?> c = ac.getClass();
 	    Method m = c.getDeclaredMethod("m");
//  	    m.setAccessible(true);      // решение
 	    Object o = m.invoke(ac);    // IllegalAccessException

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

Трассировка стека для выброшенного исключения:

```
$ java MethodTroubleAgain
java.lang.IllegalAccessException: Class MethodTroubleAgain can not access a
  member of class AnotherClass with modifiers "private"
        at sun.reflect.Reflection.ensureMemberAccess(Reflection.java:65)
        at java.lang.reflect.Method.invoke(Method.java:588)
        at MethodTroubleAgain.main(MethodTroubleAgain.java:15)
```

> **Совет.** Существует ограничение доступа, которое предотвращает рефлективный вызов методов, обычно недоступных при прямом вызове. (Сюда входят, но не ограничиваются этим, `private`-методы в отдельном классе и public-методы в отдельном приватном классе.) Однако `Method` объявлен как расширяющий `AccessibleObject`, который даёт возможность подавить эту проверку с помощью `AccessibleObject.setAccessible()`. Если вызов завершается успешно, то последующие вызовы данного объекта-метода не будут давать сбой из-за этой проблемы.

#### IllegalArgumentException из Method.invoke()

Метод `Method.invoke()` был переработан так, чтобы быть методом с переменной арностью. Это огромное удобство, однако оно может приводить к неожиданному поведению. Пример `MethodTroubleToo` показывает различные способы, которыми `Method.invoke()` может давать сбивающие с толку результаты.

```java
import java.lang.reflect.Method;

public class MethodTroubleToo {
    public void ping() { System.out.format("PONG!%n"); }

    public static void main(String... args) {
	try {
	    MethodTroubleToo mtt = new MethodTroubleToo();
	    Method m = MethodTroubleToo.class.getMethod("ping");

 	    switch(Integer.parseInt(args[0])) {
	    case 0:
  		m.invoke(mtt);                 // работает
		break;
	    case 1:
 		m.invoke(mtt, null);           // работает (ожидается предупреждение компилятора)
		break;
	    case 2:
		Object arg2 = null;
		m.invoke(mtt, arg2);           // IllegalArgumentException
		break;
	    case 3:
		m.invoke(mtt, new Object[0]);  // работает
		break;
	    case 4:
		Object arg4 = new Object[0];
		m.invoke(mtt, arg4);           // IllegalArgumentException
		break;
	    default:
		System.out.format("Test not found%n");
	    }

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (Exception x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java MethodTroubleToo 0
PONG!
```

Поскольку все параметры `Method.invoke()`, кроме первого, необязательны, их можно опустить, когда у вызываемого метода нет параметров.

```
$ java MethodTroubleToo 1
PONG!
```

В этом случае код порождает предупреждение компилятора, потому что `null` неоднозначен.

```
$ javac MethodTroubleToo.java
MethodTroubleToo.java:16: warning: non-varargs call of varargs method with
  inexact argument type for last parameter;
 		m.invoke(mtt, null);           // works (expect compiler warning)
 		              ^
  cast to Object for a varargs call
  cast to Object[] for a non-varargs call and to suppress this warning
1 warning
```

Невозможно определить, представляет ли `null` пустой массив аргументов или первый аргумент, равный `null`.

```
$ java MethodTroubleToo 2
java.lang.IllegalArgumentException: wrong number of arguments
        at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at sun.reflect.NativeMethodAccessorImpl.invoke
          (NativeMethodAccessorImpl.java:39)
        at sun.reflect.DelegatingMethodAccessorImpl.invoke
          (DelegatingMethodAccessorImpl.java:25)
        at java.lang.reflect.Method.invoke(Method.java:597)
        at MethodTroubleToo.main(MethodTroubleToo.java:21)
```

Это завершается с ошибкой несмотря на то, что аргумент равен `null`, потому что его тип — `Object`, а `ping()` вообще не ожидает аргументов.

```
$ java MethodTroubleToo 3
PONG!
```

Это работает, потому что `new Object[0]` создаёт пустой массив, а для метода с переменной арностью это эквивалентно непередаче ни одного из необязательных аргументов.

```
$ java MethodTroubleToo 4
java.lang.IllegalArgumentException: wrong number of arguments
        at sun.reflect.NativeMethodAccessorImpl.invoke0
          (Native Method)
        at sun.reflect.NativeMethodAccessorImpl.invoke
          (NativeMethodAccessorImpl.java:39)
        at sun.reflect.DelegatingMethodAccessorImpl.invoke
          (DelegatingMethodAccessorImpl.java:25)
        at java.lang.reflect.Method.invoke(Method.java:597)
        at MethodTroubleToo.main(MethodTroubleToo.java:28)
```

В отличие от предыдущего примера, если пустой массив хранится в `Object`, то он трактуется как `Object`. Это завершается с ошибкой по той же причине, что и случай 2: `ping()` не ожидает аргумента.

> **Совет.** Когда объявлен метод `foo(Object... o)`, компилятор помещает все переданные `foo()` аргументы в массив типа `Object`. Реализация `foo()` такая же, как если бы он был объявлен `foo(Object[] o)`. Понимание этого может помочь избежать показанных выше типов проблем.

#### InvocationTargetException при сбое вызываемого метода

`InvocationTargetException` оборачивает все исключения (проверяемые и непроверяемые), порождённые при вызове объекта-метода. Пример `MethodTroubleReturns` показывает, как получить исходное исключение, выброшенное вызванным методом.

```java
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

public class MethodTroubleReturns {
    private void drinkMe(int liters) {
	if (liters < 0)
	    throw new IllegalArgumentException("I can't drink a negative amount of liquid");
    }

    public static void main(String... args) {
	try {
	    MethodTroubleReturns mtr  = new MethodTroubleReturns();
 	    Class<?> c = mtr.getClass();
   	    Method m = c.getDeclaredMethod("drinkMe", int.class);
	    m.invoke(mtr, -1);

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (InvocationTargetException x) {
	    Throwable cause = x.getCause();
	    System.err.format("drinkMe() failed: %s%n", cause.getMessage());
	} catch (Exception x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java MethodTroubleReturns
drinkMe() failed: I can't drink a negative amount of liquid
```

> **Совет.** Если выброшено `InvocationTargetException`, то метод был вызван. Диагностика проблемы будет такой же, как если бы метод был вызван напрямую и выбросил исключение, которое извлекается через `getCause()`. Это исключение не указывает на проблему с пакетом рефлексии или его использованием.

---

## Конструкторы (Constructors)

Reflection API для конструкторов определены в [`java.lang.reflect.Constructor`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html) и похожи на API для методов с двумя основными исключениями: во-первых, у конструкторов нет возвращаемых значений; во-вторых, вызов конструктора создаёт новый экземпляр объекта для заданного класса.

### Поиск конструкторов

Объявление конструктора включает имя, модификаторы, параметры и список выбрасываемых исключений. Класс [`java.lang.reflect.Constructor`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html) предоставляет способ получить эту информацию.

Пример `ConstructorSift` иллюстрирует, как искать среди объявленных конструкторов класса тот, у которого есть параметр заданного типа.

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Type;
import static java.lang.System.out;

public class ConstructorSift {
    public static void main(String... args) {
	try {
	    Class<?> cArg = Class.forName(args[1]);

	    Class<?> c = Class.forName(args[0]);
	    Constructor[] allConstructors = c.getDeclaredConstructors();
	    for (Constructor ctor : allConstructors) {
		Class<?>[] pType  = ctor.getParameterTypes();
		for (int i = 0; i < pType.length; i++) {
		    if (pType[i].equals(cArg)) {
			out.format("%s%n", ctor.toGenericString());

			Type[] gpType = ctor.getGenericParameterTypes();
			for (int j = 0; j < gpType.length; j++) {
			    char ch = (pType[j].equals(cArg) ? '*' : ' ');
			    out.format("%7c%s[%d]: %s%n", ch,
				       "GenericParameterType", j, gpType[j]);
			}
			break;
		    }
		}
	    }

        // в реальном коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }
}
```

Метод [`Method.getGenericParameterTypes()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Method.html#getGenericParameterTypes--) обращается к атрибуту сигнатуры в файле класса, если он присутствует. Если атрибут недоступен, метод возвращается к `Method.getParameterType()`, который не изменился с появлением обобщений. Остальные методы рефлексии с именем вида `getGenericFoo()` реализованы аналогично. Синтаксис возвращаемых значений `Method.get*Types()` описан в [`Class.getName()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getName--).

Вот вывод для всех конструкторов [`java.util.Formatter`](https://docs.oracle.com/javase/8/docs/api/java/util/Formatter.html), имеющих аргумент типа [`Locale`](https://docs.oracle.com/javase/8/docs/api/java/util/Locale.html).

```
$ java ConstructorSift java.util.Formatter java.util.Locale
public
java.util.Formatter(java.io.OutputStream,java.lang.String,java.util.Locale)
throws java.io.UnsupportedEncodingException
       GenericParameterType[0]: class java.io.OutputStream
       GenericParameterType[1]: class java.lang.String
      *GenericParameterType[2]: class java.util.Locale
public java.util.Formatter(java.lang.String,java.lang.String,java.util.Locale)
throws java.io.FileNotFoundException,java.io.UnsupportedEncodingException
       GenericParameterType[0]: class java.lang.String
       GenericParameterType[1]: class java.lang.String
      *GenericParameterType[2]: class java.util.Locale
public java.util.Formatter(java.lang.Appendable,java.util.Locale)
       GenericParameterType[0]: interface java.lang.Appendable
      *GenericParameterType[1]: class java.util.Locale
public java.util.Formatter(java.util.Locale)
      *GenericParameterType[0]: class java.util.Locale
public java.util.Formatter(java.io.File,java.lang.String,java.util.Locale)
throws java.io.FileNotFoundException,java.io.UnsupportedEncodingException
       GenericParameterType[0]: class java.io.File
       GenericParameterType[1]: class java.lang.String
      *GenericParameterType[2]: class java.util.Locale
```

Следующий пример вывода иллюстрирует, как искать параметр типа `char[]` в [`String`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html).

```
$ java ConstructorSift java.lang.String "[C"
java.lang.String(int,int,char[])
       GenericParameterType[0]: int
       GenericParameterType[1]: int
      *GenericParameterType[2]: class [C
public java.lang.String(char[],int,int)
      *GenericParameterType[0]: class [C
       GenericParameterType[1]: int
       GenericParameterType[2]: int
public java.lang.String(char[])
      *GenericParameterType[0]: class [C
```

Синтаксис выражения массивов ссылочных и примитивных типов, приемлемый для [`Class.forName()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#forName-java.lang.String-), описан в [`Class.getName()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getName--). Обратите внимание, что первый из перечисленных конструкторов имеет доступ `package-private`, а не `public`. Он возвращается потому, что код примера использует [`Class.getDeclaredConstructors()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getDeclaredConstructors--), а не [`Class.getConstructors()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getConstructors--), который возвращает только `public`-конструкторы.

Этот пример показывает, что поиск аргументов переменной арности (имеющих переменное число параметров) требует использования синтаксиса массивов:

```
$ java ConstructorSift java.lang.ProcessBuilder "[Ljava.lang.String;"
public java.lang.ProcessBuilder(java.lang.String[])
      *GenericParameterType[0]: class [Ljava.lang.String;
```

Вот фактическое объявление конструктора [`ProcessBuilder`](https://docs.oracle.com/javase/8/docs/api/java/lang/ProcessBuilder.html#ProcessBuilder-java.lang.String...-) в исходном коде:

```java
public ProcessBuilder(String... command)
```

Параметр представлен как одномерный массив типа `java.lang.String`. Это можно отличить от параметра, который явно является массивом `java.lang.String`, вызвав [`Constructor.isVarArgs()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#isVarArgs--).

Последний пример показывает вывод для конструктора, объявленного с обобщённым типом параметра:

```
$ java ConstructorSift java.util.HashMap java.util.Map
public java.util.HashMap(java.util.Map<? extends K, ? extends V>)
      *GenericParameterType[0]: java.util.Map<? extends K, ? extends V>
```

Типы исключений могут быть получены для конструкторов так же, как и для методов. Подробнее см. пример `MethodSpy`, описанный в разделе «Получение информации о типах метода».

### Получение и разбор модификаторов конструктора

Из-за роли конструкторов в языке значимых модификаторов для них меньше, чем для методов:

- Модификаторы доступа: `public`, `protected` и `private`.
- Аннотации.

Пример `ConstructorAccess` ищет конструкторы заданного класса с указанным модификатором доступа. Он также показывает, является ли конструктор синтетическим (сгенерированным компилятором) или с переменной арностью.

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;
import static java.lang.System.out;

public class ConstructorAccess {
    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName(args[0]);
	    Constructor[] allConstructors = c.getDeclaredConstructors();
	    for (Constructor ctor : allConstructors) {
		int searchMod = modifierFromString(args[1]);
		int mods = accessModifiers(ctor.getModifiers());
		if (searchMod == mods) {
		    out.format("%s%n", ctor.toGenericString());
		    out.format("  [ synthetic=%-5b var_args=%-5b ]%n",
			       ctor.isSynthetic(), ctor.isVarArgs());
		}
	    }

        // в реальном коде это исключение следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	}
    }

    private static int accessModifiers(int m) {
	return m & (Modifier.PUBLIC | Modifier.PRIVATE | Modifier.PROTECTED);
    }

    private static int modifierFromString(String s) {
	if ("public".equals(s))               return Modifier.PUBLIC;
	else if ("protected".equals(s))       return Modifier.PROTECTED;
	else if ("private".equals(s))         return Modifier.PRIVATE;
	else if ("package-private".equals(s)) return 0;
	else return -1;
    }
}
```

Не существует явной константы `Modifier`, соответствующей доступу «package-private», поэтому необходимо проверять отсутствие всех трёх модификаторов доступа, чтобы идентифицировать package-private-конструктор.

Этот вывод показывает приватные конструкторы в `java.io.File`:

```
$ java ConstructorAccess java.io.File private
private java.io.File(java.lang.String,int)
  [ synthetic=false var_args=false ]
private java.io.File(java.lang.String,java.io.File)
  [ synthetic=false var_args=false ]
```

Синтетические конструкторы редки; однако пример `SyntheticConstructor` иллюстрирует типичную ситуацию, в которой это может произойти:

```java
public class SyntheticConstructor {
    private SyntheticConstructor() {}
    class Inner {
	// Компилятор сгенерирует синтетический конструктор, поскольку
	// SyntheticConstructor() является private.
	Inner() { new SyntheticConstructor(); }
    }
}
```

```
$ java ConstructorAccess SyntheticConstructor package-private
SyntheticConstructor(SyntheticConstructor$1)
  [ synthetic=true  var_args=false ]
```

Поскольку конструктор внутреннего класса ссылается на приватный конструктор охватывающего класса, компилятор должен сгенерировать package-private-конструктор. Тип параметра `SyntheticConstructor$1` произволен и зависит от реализации компилятора. Код, зависящий от наличия каких-либо синтетических или непубличных членов класса, может оказаться непереносимым.

Конструкторы реализуют `java.lang.reflect.AnnotatedElement`, который предоставляет методы для получения аннотаций времени выполнения с политикой удержания `java.lang.annotation.RetentionPolicy.RUNTIME`. Пример получения аннотаций см. в разделе *Examining Class Modifiers and Types*.

### Создание новых экземпляров класса

Существуют два рефлективных метода для создания экземпляров классов: [`java.lang.reflect.Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) и [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--). Первый предпочтительнее и поэтому используется в этих примерах, потому что:

- [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--) может вызвать только конструктор без аргументов, тогда как [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) может вызвать любой конструктор, независимо от числа параметров.
- [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--) выбрасывает любое исключение, выброшенное конструктором, независимо от того, проверяемое оно или непроверяемое. [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) всегда оборачивает выброшенное исключение в [`InvocationTargetException`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationTargetException.html).
- [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--) требует, чтобы конструктор был видимым; [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) при определённых обстоятельствах может вызывать `private`-конструкторы.

Иногда может быть желательно извлечь внутреннее состояние объекта, которое устанавливается только после конструирования. Рассмотрим сценарий, в котором необходимо получить внутреннюю кодировку (*character set*), используемую [`java.io.Console`](https://docs.oracle.com/javase/8/docs/api/java/io/Console.html). (Кодировка `Console` хранится в приватном поле и не обязательно совпадает с кодировкой виртуальной машины Java по умолчанию, возвращаемой [`java.nio.charset.Charset.defaultCharset()`](https://docs.oracle.com/javase/8/docs/api/java/nio/charset/Charset.html#defaultCharset--).) Пример `ConsoleCharset` показывает, как этого можно достичь:

```java
import java.io.Console;
import java.nio.charset.Charset;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import static java.lang.System.out;

public class ConsoleCharset {
    public static void main(String... args) {
	Constructor[] ctors = Console.class.getDeclaredConstructors();
	Constructor ctor = null;
	for (int i = 0; i < ctors.length; i++) {
	    ctor = ctors[i];
	    if (ctor.getGenericParameterTypes().length == 0)
		break;
	}

	try {
	    ctor.setAccessible(true);
 	    Console c = (Console)ctor.newInstance();
	    Field f = c.getClass().getDeclaredField("cs");
	    f.setAccessible(true);
	    out.format("Console charset         :  %s%n", f.get(c));
	    out.format("Charset.defaultCharset():  %s%n",
		       Charset.defaultCharset());

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (InstantiationException x) {
	    x.printStackTrace();
 	} catch (InvocationTargetException x) {
 	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (NoSuchFieldException x) {
	    x.printStackTrace();
	}
    }
}
```

> **Примечание.** [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--) будет успешен только в том случае, если конструктор имеет нуль аргументов и уже доступен. В противном случае необходимо использовать [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-), как в приведённом выше примере.

Пример вывода для UNIX-системы:

```
$ java ConsoleCharset
Console charset          :  ISO-8859-1
Charset.defaultCharset() :  ISO-8859-1
```

Пример вывода для Windows-системы:

```
C:\> java ConsoleCharset
Console charset          :  IBM437
Charset.defaultCharset() :  windows-1252
```

Ещё одно распространённое применение [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) — вызов конструкторов, принимающих аргументы. Пример `RestoreAliases` находит конкретный конструктор с одним аргументом и вызывает его:

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import static java.lang.System.out;

class EmailAliases {
    private Set<String> aliases;
    private EmailAliases(HashMap<String, String> h) {
	aliases = h.keySet();
    }

    public void printKeys() {
	out.format("Mail keys:%n");
	for (String k : aliases)
	    out.format("  %s%n", k);
    }
}

public class RestoreAliases {

    private static Map<String, String> defaultAliases = new HashMap<String, String>();
    static {
	defaultAliases.put("Duke", "duke@i-love-java");
	defaultAliases.put("Fang", "fang@evil-jealous-twin");
    }

    public static void main(String... args) {
	try {
	    Constructor ctor = EmailAliases.class.getDeclaredConstructor(HashMap.class);
	    ctor.setAccessible(true);
	    EmailAliases email = (EmailAliases)ctor.newInstance(defaultAliases);
	    email.printKeys();

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	}
    }
}
```

Этот пример использует [`Class.getDeclaredConstructor()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#getDeclaredConstructor-java.lang.Class...-) для поиска конструктора с единственным аргументом типа [`java.util.HashMap`](https://docs.oracle.com/javase/8/docs/api/java/util/HashMap.html). Обратите внимание, что достаточно передать `HashMap.class`, поскольку параметр любого метода `get*Constructor()` требует класс только для целей типизации. Из-за [стирания типов](https://docs.oracle.com/javase/specs/jls/se7/html/jls-4.html#jls-4.6) следующее выражение вычисляется как `true`:

```java
HashMap.class == defaultAliases.getClass()
```

Затем пример создаёт новый экземпляр класса, используя этот конструктор с [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-).

```
$ java RestoreAliases
Mail keys:
  Duke
  Fang
```

### Решение проблем (конструкторы)

Следующие проблемы иногда возникают у разработчиков при попытке вызывать конструкторы через рефлексию.

#### InstantiationException из-за отсутствия конструктора без аргументов

Пример `ConstructorTrouble` иллюстрирует, что происходит, когда код пытается создать новый экземпляр класса с помощью [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--), а доступного конструктора без аргументов нет:

```java
public class ConstructorTrouble {
    private ConstructorTrouble(int i) {}

    public static void main(String... args){
	try {
	    Class<?> c = Class.forName("ConstructorTrouble");
	    Object o = c.newInstance();  // InstantiationException

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java ConstructorTrouble
java.lang.InstantiationException: ConstructorTrouble
        at java.lang.Class.newInstance0(Class.java:340)
        at java.lang.Class.newInstance(Class.java:308)
        at ConstructorTrouble.main(ConstructorTrouble.java:7)
```

> **Совет.** Существует ряд различных причин, по которым может возникнуть [`InstantiationException`](https://docs.oracle.com/javase/8/docs/api/java/lang/InstantiationException.html). В данном случае проблема в том, что наличие конструктора с аргументом `int` не позволяет компилятору сгенерировать конструктор по умолчанию (без аргументов), а явного конструктора без аргументов в коде нет. Помните, что [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--) ведёт себя очень похоже на ключевое слово `new` и будет давать сбой всякий раз, когда дал бы сбой `new`.

#### Class.newInstance() выбрасывает неожиданное исключение

Пример `ConstructorTroubleToo` показывает неустранимую проблему в [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--). А именно: он распространяет любое исключение — проверяемое или непроверяемое, — выброшенное конструктором.

```java
import java.lang.reflect.InvocationTargetException;
import static java.lang.System.err;

public class ConstructorTroubleToo {
    public ConstructorTroubleToo() {
 	throw new RuntimeException("exception in constructor");
    }

    public static void main(String... args) {
	try {
	    Class<?> c = Class.forName("ConstructorTroubleToo");
	    // Метод распространяет любое исключение, выброшенное конструктором
	    // (включая проверяемые исключения).
	    if (args.length > 0 && args[0].equals("class")) {
		Object o = c.newInstance();
	    } else {
		Object o = c.getConstructor().newInstance();
	    }

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	    err.format("%n%nCaught exception: %s%n", x.getCause());
	}
    }
}
```

```
$ java ConstructorTroubleToo class
Exception in thread "main" java.lang.RuntimeException: exception in constructor
        at ConstructorTroubleToo.<init>(ConstructorTroubleToo.java:6)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance
          (NativeConstructorAccessorImpl.java:39)
        at sun.reflect.DelegatingConstructorAccessorImpl.newInstance
          (DelegatingConstructorAccessorImpl.java:27)
        at java.lang.reflect.Constructor.newInstance(Constructor.java:513)
        at ConstructorTroubleToo.main(ConstructorTroubleToo.java:15)
```

Эта ситуация уникальна для рефлексии. Обычно невозможно написать код, который игнорирует проверяемое исключение, потому что он не скомпилировался бы. Можно обернуть любое исключение, выброшенное конструктором, используя [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) вместо [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--).

```
$ java ConstructorTroubleToo
java.lang.reflect.InvocationTargetException
        at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance
          (NativeConstructorAccessorImpl.java:39)
        at sun.reflect.DelegatingConstructorAccessorImpl.newInstance
          (DelegatingConstructorAccessorImpl.java:27)
        at java.lang.reflect.Constructor.newInstance(Constructor.java:513)
        at ConstructorTroubleToo.main(ConstructorTroubleToo.java:17)
Caused by: java.lang.RuntimeException: exception in constructor
        at ConstructorTroubleToo.<init>(ConstructorTroubleToo.java:6)
        ... 5 more


Caught exception: java.lang.RuntimeException: exception in constructor
```

Если выброшено [`InvocationTargetException`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationTargetException.html), то метод был вызван. Диагностика проблемы будет такой же, как если бы конструктор был вызван напрямую и выбросил исключение, которое извлекается через [`InvocationTargetException.getCause()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationTargetException.html#getCause--). Это исключение не указывает на проблему с пакетом рефлексии или его использованием.

> **Совет.** Предпочтительнее использовать [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) вместо [`Class.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/Class.html#newInstance--), потому что первый API позволяет исследовать и обрабатывать произвольные исключения, выброшенные конструкторами.

#### Проблемы с поиском или вызовом нужного конструктора

Класс `ConstructorTroubleAgain` иллюстрирует различные способы, которыми некорректный код может не найти или не вызвать ожидаемый конструктор.

```java
import java.lang.reflect.InvocationTargetException;
import static java.lang.System.out;

public class ConstructorTroubleAgain {
    public ConstructorTroubleAgain() {}

    public ConstructorTroubleAgain(Integer i) {}

    public ConstructorTroubleAgain(Object o) {
	out.format("Constructor passed Object%n");
    }

    public ConstructorTroubleAgain(String s) {
	out.format("Constructor passed String%n");
    }

    public static void main(String... args){
	String argType = (args.length == 0 ? "" : args[0]);
	try {
	    Class<?> c = Class.forName("ConstructorTroubleAgain");
	    if ("".equals(argType)) {
		// IllegalArgumentException: неверное число аргументов
		Object o = c.getConstructor().newInstance("foo");
	    } else if ("int".equals(argType)) {
		// NoSuchMethodException - ищем int, а есть Integer
		Object o = c.getConstructor(int.class);
	    } else if ("Object".equals(argType)) {
		// newInstance() не выполняет разрешение методов
		Object o = c.getConstructor(Object.class).newInstance("foo");
	    } else {
		assert false;
	    }

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (ClassNotFoundException x) {
	    x.printStackTrace();
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java ConstructorTroubleAgain
Exception in thread "main" java.lang.IllegalArgumentException: wrong number of
  arguments
        at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at sun.reflect.NativeConstructorAccessorImpl.newInstance
          (NativeConstructorAccessorImpl.java:39)
        at sun.reflect.DelegatingConstructorAccessorImpl.newInstance
          (DelegatingConstructorAccessorImpl.java:27)
        at java.lang.reflect.Constructor.newInstance(Constructor.java:513)
        at ConstructorTroubleAgain.main(ConstructorTroubleAgain.java:23)
```

Исключение [`IllegalArgumentException`](https://docs.oracle.com/javase/8/docs/api/java/lang/IllegalArgumentException.html) выбрасывается потому, что был запрошен конструктор без аргументов, а попытались передать аргумент. То же исключение было бы выброшено, если бы конструктору передали аргумент неверного типа.

```
$ java ConstructorTroubleAgain int
java.lang.NoSuchMethodException: ConstructorTroubleAgain.<init>(int)
        at java.lang.Class.getConstructor0(Class.java:2706)
        at java.lang.Class.getConstructor(Class.java:1657)
        at ConstructorTroubleAgain.main(ConstructorTroubleAgain.java:26)
```

Это исключение может возникнуть, если разработчик ошибочно полагает, что рефлексия выполнит автоупаковку или распаковку типов. Упаковка (преобразование примитива в ссылочный тип) происходит только во время компиляции. В рефлексии нет возможности для выполнения этой операции, поэтому при поиске конструктора нужно использовать конкретный тип.

```
$ java ConstructorTroubleAgain Object
Constructor passed Object
```

Здесь можно было бы ожидать, что будет вызван конструктор, принимающий аргумент [`String`](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html), поскольку `newInstance()` был вызван с более конкретным типом `String`. Однако уже слишком поздно! Найденный конструктор — это уже конструктор с аргументом [`Object`](https://docs.oracle.com/javase/8/docs/api/java/lang/Object.html). `newInstance()` не делает попыток выполнить разрешение методов (*method resolution*); он просто работает с существующим объектом-конструктором.

> **Совет.** Важное отличие между `new` и [`Constructor.newInstance()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Constructor.html#newInstance-java.lang.Object...-) состоит в том, что `new` выполняет проверку типов аргументов метода, упаковку и разрешение методов. Ничего из этого не происходит в рефлексии, где явный выбор должен быть сделан вручную.

#### IllegalAccessException при попытке вызвать недоступный конструктор

Исключение [`IllegalAccessException`](https://docs.oracle.com/javase/8/docs/api/java/lang/IllegalAccessException.html) может быть выброшено при попытке вызвать приватный или иной недоступный конструктор. Пример `ConstructorTroubleAccess` иллюстрирует получающуюся трассировку стека.

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;

class Deny {
    private Deny() {
	System.out.format("Deny constructor%n");
    }
}

public class ConstructorTroubleAccess {
    public static void main(String... args) {
	try {
	    Constructor c = Deny.class.getDeclaredConstructor();
//  	    c.setAccessible(true);   // решение
	    c.newInstance();

        // в реальном коде эти исключения следует обрабатывать аккуратнее
	} catch (InvocationTargetException x) {
	    x.printStackTrace();
	} catch (NoSuchMethodException x) {
	    x.printStackTrace();
	} catch (InstantiationException x) {
	    x.printStackTrace();
	} catch (IllegalAccessException x) {
	    x.printStackTrace();
	}
    }
}
```

```
$ java ConstructorTroubleAccess
java.lang.IllegalAccessException: Class ConstructorTroubleAccess can not access
  a member of class Deny with modifiers "private"
        at sun.reflect.Reflection.ensureMemberAccess(Reflection.java:65)
        at java.lang.reflect.Constructor.newInstance(Constructor.java:505)
        at ConstructorTroubleAccess.main(ConstructorTroubleAccess.java:15)
```

> **Совет.** Существует ограничение доступа, которое предотвращает рефлективный вызов конструкторов, обычно недоступных при прямом вызове. (Сюда входят, но не ограничиваются этим, приватные конструкторы в отдельном классе и public-конструкторы в отдельном приватном классе.) Однако `Constructor` объявлен как расширяющий [`AccessibleObject`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AccessibleObject.html), который даёт возможность подавить эту проверку с помощью [`AccessibleObject.setAccessible()`](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/AccessibleObject.html#setAccessible-boolean-).

---

## Источник

- [Lesson: Members (обзор)](https://docs.oracle.com/javase/tutorial/reflect/member/index.html) — официальное руководство Oracle.
- [Obtaining Field Types](https://docs.oracle.com/javase/tutorial/reflect/member/fieldTypes.html)
- [Retrieving and Parsing Field Modifiers](https://docs.oracle.com/javase/tutorial/reflect/member/fieldModifiers.html)
- [Getting and Setting Field Values](https://docs.oracle.com/javase/tutorial/reflect/member/fieldValues.html)
- [Troubleshooting (Fields)](https://docs.oracle.com/javase/tutorial/reflect/member/fieldTrouble.html)
- [Obtaining Method Type Information](https://docs.oracle.com/javase/tutorial/reflect/member/methodType.html)
- [Obtaining Names of Method Parameters](https://docs.oracle.com/javase/tutorial/reflect/member/methodparameterreflection.html)
- [Retrieving and Parsing Method Modifiers](https://docs.oracle.com/javase/tutorial/reflect/member/methodModifiers.html)
- [Invoking Methods](https://docs.oracle.com/javase/tutorial/reflect/member/methodInvocation.html)
- [Troubleshooting (Methods)](https://docs.oracle.com/javase/tutorial/reflect/member/methodTrouble.html)
- [Finding Constructors](https://docs.oracle.com/javase/tutorial/reflect/member/ctorLocation.html)
- [Retrieving and Parsing Constructor Modifiers](https://docs.oracle.com/javase/tutorial/reflect/member/ctorModifiers.html)
- [Creating New Class Instances](https://docs.oracle.com/javase/tutorial/reflect/member/ctorInstance.html)
- [Troubleshooting (Constructors)](https://docs.oracle.com/javase/tutorial/reflect/member/ctorTrouble.html)
</content>
</invoke>
