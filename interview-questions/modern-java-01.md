# Современные возможности Java — часть 1 из 2

> Вопросы 1–20 (в части: 20). Всего в разделе: 22.
> Область знаний: [../knowledge-base/09-modern-java-features.md](../knowledge-base/09-modern-java-features.md)
> Правила: [RULES.md](RULES.md)
> Части: **ч.1** · [ч.2](modern-java-02.md)

---
### Вопрос 1. Что такое record в Java и какие методы он генерирует автоматически?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Record (Java SE 21 & JDK 21) — docs.oracle.com](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Record.html)

Record-класс — это поверхностно неизменяемый (shallowly immutable), прозрачный носитель фиксированного набора значений, называемых компонентами записи. Компилятор автоматически синтезирует следующие члены:

1. **Канонический конструктор** — имеет ту же доступность, что и сам record-класс; инициализирует поля-компоненты из соответствующих аргументов.
2. **Приватные финальные поля** — по одному на каждый компонент, с тем же именем и типом.
3. **Публичные методы-аксессоры** — по одному на каждый компонент, с тем же именем, что и компонент (например, `x()` и `y()` для `record Point(int x, int y)`).
4. **`equals(Object)`** — возвращает `true`, если аргумент является экземпляром того же record-класса и все компоненты равны соответствующим компонентам аргумента.
5. **`hashCode()`** — формируется комбинированием хешей всех компонентов; точный алгоритм не специфицирован и может меняться.
6. **`toString()`** — возвращает строку формата `ClassName[component1=value1, component2=value2, ...]`.

#### Ответ от Claude

**Record** (запись) — это специальный вид класса, введённый в Java 16 (preview с Java 14), предназначенный для создания классов-носителей данных с минимумом шаблонного кода. Объявляется ключевым словом `record`:

```java
record Point(int x, int y) { }
```

Компилятор автоматически генерирует для каждого компонента:

| Член | Описание |
|------|----------|
| `private final` поле | Хранит значение компонента |
| Публичный аксессор `имяКомпонента()` | Возвращает значение поля (не `getX()`, а `x()`) |
| Канонический конструктор | Принимает все компоненты и присваивает их полям |
| `equals(Object)` | Сравнивает тип и все компоненты |
| `hashCode()` | Хеш по всем компонентам |
| `toString()` | Строка вида `Point[x=1, y=2]` |

**Важные особенности:**
- Record неявно является `final` — его нельзя расширить.
- Record неявно расширяет `java.lang.Record` — нельзя указать другой `extends`.
- Все поля-компоненты неявно `private final`.
- Нельзя объявлять нестатические поля-экземпляры (instance fields) и инициализаторы экземпляра.
- Статические поля, методы и вложенные классы — разрешены.
- Сеттеры не генерируются (запись неизменяема).

```java
record Rectangle(double length, double width) { }

// Автоматически доступно:
Rectangle r = new Rectangle(3.0, 4.0);
r.length();            // аксессор
r.width();             // аксессор
r.equals(other);       // сравнение по компонентам
r.hashCode();          // хеш по компонентам
r.toString();          // "Rectangle[length=3.0, width=4.0]"
```

---

### Вопрос 2. Чем отличается канонический конструктор record от компактного конструктора? Когда использовать компактный?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Record Classes — docs.oracle.com (Java SE 22)](https://docs.oracle.com/en/java/javase/22/language/records.html)

**Канонический конструктор** имеет явно перечисленные параметры, совпадающие с компонентами записи, и требует явного присваивания полей (`this.length = length`).

**Компактный конструктор** имеет неявную сигнатуру, автоматически выводимую из компонентов; параметры не перечисляются в скобках. Присваивание полей (`this.length = length`) происходит неявно в конце его тела. Компактный конструктор предназначен для валидации и нормализации аргументов без необходимости вручную повторять присваивания. Нельзя объявить оба варианта одновременно — это вызовет ошибку компиляции.

```java
// Компактный конструктор
record Rectangle(double length, double width) {
    public Rectangle {
        if (length <= 0 || width <= 0) {
            throw new IllegalArgumentException(
                String.format("Invalid dimensions: %f, %f", length, width));
        }
        // this.length = length; и this.width = width; — неявно в конце
    }
}
```

#### Ответ от Claude

**Канонический конструктор** — стандартный конструктор, чья сигнатура полностью совпадает со списком компонентов записи. В явном каноническом конструкторе нужно вручную присваивать все поля:

```java
record Rectangle(double length, double width) {
    public Rectangle(double length, double width) {
        if (length <= 0 || width <= 0) throw new IllegalArgumentException("...");
        this.length = length;   // явное присваивание обязательно
        this.width = width;
    }
}
```

**Компактный конструктор** — синтаксический сахар, доступный **только в record-классах**. Параметры не перечисляются (нет скобок после имени); присваивание `this.поле = параметр` для каждого компонента выполняется компилятором неявно **в конце** тела конструктора:

```java
record Rectangle(double length, double width) {
    public Rectangle {                // нет скобок с параметрами
        if (length <= 0 || width <= 0) throw new IllegalArgumentException("...");
        length = Math.abs(length);    // можно модифицировать параметр ДО неявного присваивания
        // this.length = length; и this.width = width; — добавляются компилятором неявно
    }
}
```

**Ключевые отличия:**

| Аспект | Канонический | Компактный |
|--------|-------------|------------|
| Сигнатура | Явная, повторяет компоненты | Неявная (нет скобок) |
| Присваивание полей | Вручную (`this.x = x`) | Автоматически в конце |
| Доступность | Любой класс | Только record |
| Можно ли совмещать оба | Нет (ошибка компиляции) | Нет |

**Когда использовать компактный конструктор:**
- Для валидации входных значений (наиболее частый сценарий).
- Для нормализации данных перед присваиванием (например, `length = Math.abs(length)`).
- Когда хочется избежать повторения списка параметров и ручных присваиваний.

**Когда использовать канонический:**
- Когда нужно полное управление над порядком и логикой присваивания.
- Когда компактный конструктор неудобен из-за сложной логики инициализации.

---

### Вопрос 3. Можно ли наследоваться от record или добавить в него изменяемые поля? Почему?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Record Classes — docs.oracle.com (Java SE 22)](https://docs.oracle.com/en/java/javase/22/language/records.html)

Record-класс неявно является `final`, поэтому нельзя явно расширить record-класс. Также нельзя объявлять нестатические поля-экземпляры (non-static fields) и инициализаторы экземпляра в теле record-класса. Все компоненты неявно объявляются как `private final`. Цель этих ограничений — сохранить семантику record как простого, предсказуемого носителя данных с гарантией неизменяемости состояния.

#### Ответ от Claude

**Наследование от record невозможно** по двум независимым причинам:

1. **Record неявно `final`** — никакой класс не может его расширить. Попытка написать `class MyPoint extends Point {}` (где `Point` — record) вызовет ошибку компиляции.
2. **Record неявно расширяет `java.lang.Record`** — а Java не поддерживает множественное наследование классов. Даже если бы record не был `final`, он уже "занял" свой единственный слот `extends`.

**Изменяемые (нестатические) поля добавить нельзя.** Следующий код не компилируется:

```java
record Point(int x, int y) {
    String label;           // ❌ ошибка: instance field запрещён
    { label = "default"; }  // ❌ ошибка: instance initializer запрещён
}
```

Разрешены только **статические** поля и инициализаторы:

```java
record Point(int x, int y) {
    static int instanceCount = 0;  // ✅ статическое поле — можно
    static { instanceCount = 0; }  // ✅ статический инициализатор — можно
}
```

**Почему так спроектировано:**
- Все компоненты record неявно `private final` — они неизменяемы после создания объекта.
- Это обеспечивает **семантическую прозрачность**: состояние объекта полностью описывается его компонентами.
- Гарантируется **инвариант копирования**: `new R(r.c1(), r.c2(), ...).equals(r)` всегда `true`.
- Нестатические изменяемые поля нарушили бы этот инвариант и сделали бы `equals`/`hashCode` непредсказуемыми.

**Что допустимо в теле record:**
- Статические поля, методы и инициализаторы.
- Переопределение сгенерированных `equals`, `hashCode`, `toString`.
- Переопределение аксессоров.
- Дополнительные instance-методы (не поля).
- Вложенные классы и интерфейсы.
- Дополнительные конструкторы (должны делегировать каноническому через `this(...)`).

---

### Вопрос 4. Что такое sealed-класс и зачем нужен модификатор non-sealed у разрешённого подкласса?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Sealed Classes and Interfaces — docs.oracle.com (Java SE 17)](https://docs.oracle.com/en/java/javase/17/language/sealed-classes-and-interfaces.html)

Sealed-класс ограничивает, какие другие классы или интерфейсы могут его расширять или реализовывать. Для создания используется модификатор `sealed` и клауза `permits`:

```java
public sealed class Shape
    permits Circle, Square, Rectangle { }
```

Каждый разрешённый подкласс обязан объявить ровно один из трёх модификаторов: `final` (не может быть расширен), `sealed` (может быть расширен только своими разрешёнными подклассами), или `non-sealed` (может быть расширен неизвестными подклассами — «разрывает цепочку запечатывания»):

```java
public non-sealed class Square extends Shape { }
// Теперь любой класс может расширить Square
```

Модификатор `non-sealed` даёт гибкость: одни ветви иерархии остаются закрытыми, другие — открытыми для произвольного расширения.

#### Ответ от Claude

**Sealed-класс** (запечатанный класс) — класс с модификатором `sealed`, который явно ограничивает набор своих допустимых подклассов с помощью клаузы `permits`. Введён в Java 17 (preview с Java 15).

```java
public sealed class Shape permits Circle, Square, Rectangle { }
```

**Основные цели:**
- **Моделирование предметной области** — явно выразить, что множество подтипов закрыто и известно.
- **Поддержка pattern matching** — компилятор знает полный список подтипов и может предупреждать о неполных `switch`-выражениях.
- **Безопасность API библиотек** — сторонний код не может добавить произвольный подкласс.

**Требования к разрешённым подклассам:**

Каждый класс из `permits` обязан объявить ровно один из трёх модификаторов:

| Модификатор | Смысл |
|-------------|-------|
| `final` | Класс не может быть расширен вообще |
| `sealed` | Класс сам является sealed и контролирует свои подклассы |
| `non-sealed` | Класс открыт для произвольного наследования — «разрывает печать» |

**Зачем нужен `non-sealed`:**

Без `non-sealed` любой разрешённый подкласс обязан быть либо `final`, либо `sealed` — то есть иерархия остаётся полностью контролируемой. Модификатор `non-sealed` позволяет **сознательно открыть одну ветвь** иерархии для расширения внешним кодом, при этом другие ветви остаются закрытыми:

```java
public sealed class Shape permits Circle, Square, Rectangle { }

public final class Circle extends Shape { }        // нельзя расширить

public sealed class Rectangle extends Shape
    permits FilledRectangle { }                    // расширяется только FilledRectangle

public final class FilledRectangle extends Rectangle { }

public non-sealed class Square extends Shape { }   // любой может расширить Square
// class ColoredSquare extends Square { }  // ✅ допустимо
```

**Ключевое отличие от обычного класса:** `non-sealed` — явный, осознанный сигнал того, что разработчик намеренно открывает ветвь иерархии. Это делает намерение видимым в коде в отличие от обычного (открытого по умолчанию) класса, где намерение неочевидно.

**Связь с record:** Record-классы неявно `final`, поэтому они идеально подходят в качестве `final`-листьев sealed-иерархии — компактно и без лишних модификаторов:

```java
public sealed interface Expr permits Num, Add, Mul { }
record Num(int value) implements Expr { }
record Add(Expr left, Expr right) implements Expr { }
record Mul(Expr left, Expr right) implements Expr { }
```

---
### Вопрос 5. Что такое pattern matching для instanceof (Java 16)? Чем он отличается от классической проверки + приведения типа?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Pattern Matching for the instanceof Operator — Oracle Java SE 16 Documentation](https://docs.oracle.com/en/java/javase/16/language/pattern-matching-instanceof-operator.html)

Pattern matching для `instanceof` — это языковое улучшение, позволяющее компактнее и безопаснее выражать условное извлечение данных из объектов. Функциональность финализирована в JDK 16 (JEP 394).

**Классический подход (до Java 16)** требует трёх шагов:
1. Проверка типа через `instanceof`
2. Явное приведение типа (cast)
3. Извлечение данных из объекта

```java
// Классический подход
if (shape instanceof Rectangle) {
    Rectangle r = (Rectangle) shape;
    return 2 * r.length() + 2 * r.width();
} else if (shape instanceof Circle) {
    Circle c = (Circle) shape;
    return 2 * c.radius() * Math.PI;
}
```

**С pattern matching** шаг приведения типа устраняется: если `shape` соответствует паттерну `Rectangle r`, то переменная `r` сразу инициализируется значением `shape`, приведённым к `Rectangle`:

```java
// С pattern matching (Java 16+)
if (shape instanceof Rectangle r) {
    return 2 * r.length() + 2 * r.width();
} else if (shape instanceof Circle c) {
    return 2 * c.radius() * Math.PI;
}
```

**Область видимости (scope) переменной паттерна** строго определена — переменная доступна только там, где компилятор гарантирует истинность условия `instanceof`:

```java
// Допустимо: оператор && гарантирует, что instanceof был true
if (shape instanceof Rectangle r && r.length() > 5) { ... }

// Недопустимо: оператор || позволяет достичь r.length() при false
if (shape instanceof Rectangle r || r.length() > 0) { ... } // ошибка компиляции
```

Также поддерживается паттерн с отрицанием для ранних выходов:

```java
if (!(s instanceof Rectangle r)) {
    return false;
}
// r доступна здесь, так как ранний return отсеял все не-Rectangle
return r.length() > 5;
```

#### Ответ от Claude

**Pattern matching для `instanceof`** (Java 16, JEP 394) — это возможность одновременно проверить тип объекта и ввести переменную паттерна (pattern variable) нужного типа в одном выражении, без ручного приведения типа.

**Сравнение подходов:**

```java
// ДО Java 16: три отдельных шага
if (obj instanceof String) {
    String s = (String) obj;  // явный cast — избыточен, может забыться при рефакторинге
    System.out.println(s.toUpperCase());
}

// Java 16+: один шаг
if (obj instanceof String s) {
    System.out.println(s.toUpperCase());  // s уже String, cast не нужен
}
```

**Ключевые отличия от классического подхода:**

| Аспект | Классический instanceof + cast | Pattern matching |
|--------|-------------------------------|-----------------|
| Количество шагов | 3 (проверка → cast → использование) | 1 (проверка + привязка) |
| Риск ошибки | Cast может ошибиться при рефакторинге | Cast выполняется компилятором гарантированно |
| Дублирование типа | Тип указывается дважды | Тип указывается один раз |
| Читаемость | Шаблонный код | Лаконично |

**Правила области видимости переменной паттерна** определяются анализом потока выполнения (definite assignment):

```java
// 1. Область видимости ограничена блоком истинного условия
if (obj instanceof String s) {
    // s доступна здесь
}
// s здесь НЕ доступна

// 2. Расширенная область с &&
if (obj instanceof String s && s.length() > 3) {
    // s доступна: && гарантирует, что instanceof = true
}

// 3. НЕ работает с ||
// if (obj instanceof String s || s.length() > 3) { }  // ошибка компиляции

// 4. Паттерн с отрицанием — «ранний выход»
if (!(obj instanceof String s)) return;
// После этой строки s доступна и гарантированно String
System.out.println(s.toUpperCase());
```

**Важно:** переменная паттерна — это новая локальная переменная, не просто псевдоним. Её можно переопределить в подблоках, но это считается плохой практикой.

Фича финализирована в Java 16 как постоянная возможность языка. До этого прошла два preview: Java 14 (JEP 305) и Java 15 (JEP 375).

---

### Вопрос 6. Что такое guard-условие (when-clause) в pattern matching для switch? Приведите пример.

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Pattern Matching for switch Expressions and Statements — Oracle Java SE 21 Documentation](https://docs.oracle.com/en/java/javase/21/language/pattern-matching-switch.html)

**When-clause** (охраняемая метка паттерна, guarded pattern label) позволяет добавить булево выражение к метке `case` с паттерном. Значение соответствует охраняемому паттерну только если: (1) оно совпадает с паттерном **и** (2) булево выражение в `when` возвращает `true`.

**До when-clause** — вложенный `if` внутри `case`:
```java
static void test(Object obj) {
    switch (obj) {
        case String s:
            if (s.length() == 1) {
                System.out.println("Short: " + s);
            } else {
                System.out.println(s);
            }
            break;
        default:
            System.out.println("Not a string");
    }
}
```

**С when-clause** — более чистый код:
```java
static void test(Object obj) {
    switch (obj) {
        case String s when s.length() == 1 -> System.out.println("Short: " + s);
        case String s                      -> System.out.println(s);
        default                            -> System.out.println("Not a string");
    }
}
```

Переменная паттерна `s` находится в области видимости внутри выражения `when`. Важное ограничение: охраняемые паттерны не применяются к константным меткам — нельзя написать `case "Hello" when someCondition()`.

#### Ответ от Claude

**Guard-условие (when-clause)** — необязательное дополнительное булево условие в метке `case` switch-выражения или оператора, позволяющее уточнить совпадение сверх простой проверки типа. Синтаксис:

```
case <паттерн> when <булево-выражение> -> <результат>
```

Финализировано в Java 21 как часть JEP 441 (Pattern Matching for switch).

**Мотивация.** Без `when` пришлось бы писать вложенный `if` внутри `case`, что ухудшает читаемость. `when` выносит уточняющее условие в заголовок метки.

**Развёрнутый пример:**

```java
sealed interface Shape permits Circle, Rectangle, Triangle {}
record Circle(double radius) implements Shape {}
record Rectangle(double width, double height) implements Shape {}
record Triangle(double base, double height) implements Shape {}

static String classify(Shape shape) {
    return switch (shape) {
        case Circle c when c.radius() == 0    -> "Вырожденная окружность (точка)";
        case Circle c when c.radius() < 0     -> "Недопустимый радиус";
        case Circle c                          -> "Окружность, радиус = " + c.radius();
        case Rectangle r when r.width() == r.height() -> "Квадрат, сторона = " + r.width();
        case Rectangle r                       -> "Прямоугольник";
        case Triangle t when t.base() <= 0 || t.height() <= 0 -> "Вырожденный треугольник";
        case Triangle t                        -> "Треугольник";
    };
}
```

**Пример с числами и `null`:**

```java
static String describe(Integer val) {
    return switch (val) {
        case null              -> "null";
        case 0                 -> "ноль";
        case Integer i when i < 0  -> "отрицательное: " + i;
        case Integer i when i > 100 -> "большое: " + i;
        case Integer i         -> "обычное: " + i;
    };
}
```

**Ключевые правила:**

1. **Область видимости:** переменная паттерна (например, `c`, `r`, `i`) находится в области видимости как в самом `when`-выражении, так и в теле `case`.

2. **Только для паттернов:** `when` нельзя применить к константным меткам. `case "Hello" when condition()` — ошибка компиляции.

3. **Порядок имеет значение:** более специфичные (охраняемые) паттерны должны идти **раньше** более общих. Компилятор проверяет доминирование: если менее специфичный паттерн без `when` стоит перед паттерном с `when` того же типа, это ошибка компиляции.

   ```java
   // ОШИБКА: case Integer i доминирует над case Integer i when i > 0
   case Integer i         -> "любое";
   case Integer i when i > 0 -> "положительное";  // недостижимо
   ```

4. **Совместимость с arrow и colon формами:** `when` работает в обоих синтаксисах switch (`->` и `:`).

---

### Вопрос 7. Как работает deconstruction pattern (record pattern) в switch? Напишите пример, где извлекаются компоненты record внутри case.

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Sip of Java: Record Patterns in Java 21 — Inside.java](https://inside.java/2023/11/06/sip087/)

Record patterns позволяют сопоставлять тип Record и одновременно деконструировать его компоненты. Они работают как «обратные конструкторы»: вместо извлечения полей через методы-аксессоры компоненты распаковываются прямо в теле паттерна.

Переменные паттерна могут иметь имена, отличные от имён компонентов record (это позволяет избежать конфликтов имён). Поддерживается как явное указание типов, так и `var` для вывода типа.

**Пример с вложенными record:**

```java
record Name(String first, String last, String middle) {}
record Address(String street, String city) {}
record Person(Name name, Address address) {}

if (person instanceof Person(
        Name(var first, var last, var middle),
        Address(var street, var city))) {
    String printName = last + ", " + first;
}
```

**В switch:**

```java
return switch (person) {
    case Person(Name(var fName, var lName, var mName), var address) ->
        lName + ", " + fName;
    default -> "unknown";
};
```

#### Ответ от Claude

**Record pattern (паттерн деконструкции)** — возможность сопоставить record по типу и одновременно извлечь его компоненты в переменные прямо в заголовке `case`. Финализировано в Java 21 (JEP 440).

**Базовый принцип.** Record pattern является «обратным» к конструктору: если конструктор `Point(int x, int y)` принимает компоненты и создаёт объект, то паттерн `Point(int x, int y)` принимает объект и связывает его компоненты с переменными.

**Пример 1 — простая деконструкция в switch:**

```java
record Point(int x, int y) {}
record Circle(Point center, double radius) {}
record Rectangle(Point topLeft, Point bottomRight) {}

sealed interface Shape permits Circle, Rectangle {}

static double area(Shape shape) {
    return switch (shape) {
        case Circle(Point(var cx, var cy), var r) ->
            Math.PI * r * r;
        case Rectangle(Point(var x1, var y1), Point(var x2, var y2)) ->
            Math.abs(x2 - x1) * Math.abs(y2 - y1);
    };
}
```

Здесь `Circle(Point(var cx, var cy), var r)` — это **вложенный паттерн**: сначала деконструируется `Circle`, получая `center` (типа `Point`) и `radius`, затем `center` деконструируется дополнительно, извлекая `cx` и `cy`.

**Пример 2 — с `when`-условием:**

```java
record Order(String product, int quantity, double price) {}

static String describe(Object obj) {
    return switch (obj) {
        case Order(var p, var q, var price) when price * q > 1000 ->
            "Крупный заказ: " + p + ", сумма=" + (price * q);
        case Order(var p, var q, var price) when q == 0 ->
            "Нулевой заказ: " + p;
        case Order(var p, var q, var price) ->
            "Заказ: " + p + " x" + q;
        default -> "Не заказ";
    };
}
```

**Пример 3 — сочетание с sealed interface и `instanceof`:**

```java
sealed interface Expr permits Num, Add, Mul {}
record Num(int value) implements Expr {}
record Add(Expr left, Expr right) implements Expr {}
record Mul(Expr left, Expr right) implements Expr {}

static int eval(Expr expr) {
    return switch (expr) {
        case Num(var v)              -> v;
        case Add(var l, var r)       -> eval(l) + eval(r);
        case Mul(Num(var v), var r)  -> v * eval(r);   // вложенный паттерн
        case Mul(var l, var r)       -> eval(l) * eval(r);
    };
}
```

**Ключевые правила:**

1. **Соответствие арности:** количество переменных в паттерне должно точно соответствовать количеству компонентов record.
2. **Типовая безопасность:** компилятор проверяет, что типы переменных совместимы с типами компонентов. С `var` тип выводится автоматически.
3. **null-безопасность:** если значение `null`, паттерн не совпадает (нет NPE при деконструкции).
4. **Вложенность:** паттерны могут быть произвольно вложены — это мощный инструмент для обхода иерархий данных.
5. **Именованные переменные паттерна** могут отличаться от имён компонентов record.
6. **Unnamed patterns (`_`)**: начиная с Java 21 (preview) и финально с Java 22, неиспользуемые компоненты можно заменять `_`.

---

### Вопрос 8. Что такое var в Java? Является ли он ключевым словом? Где его нельзя использовать (поля, параметры методов, возвращаемый тип)?

**Категория:** Современная Java · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [var Keyword (JEP 286) — javaalmanac.io](https://javaalmanac.io/features/var/)

`var` — это **зарезервированное имя типа** (reserved type name), а не ключевое слово в традиционном смысле. Это означает, что `var` можно использовать как имя переменной, пакета или метода, но нельзя как имя класса или интерфейса.

**Где `var` можно использовать:**
- Объявление локальной переменной с инициализацией
- Переменная цикла `for` (классический и расширенный варианты)
- Блок `try-with-resources`
- Параметры лямбды (Java 11+, JEP 323) — в том числе для добавления аннотаций
- Локальные `final`-переменные (комбинируется с `final`)

**Где `var` нельзя использовать:**
- Неинициализированные локальные переменные
- Переменные, инициализированные `null`
- Переменные там, где тип не может быть выведен (изолированные лямбды и method references)
- Поля класса или экземпляра
- Параметры методов или возвращаемые типы
- Блоки `catch`

#### Ответ от Claude

**`var`** — конструкция вывода типа локальных переменных, введённая в Java 10 (JEP 286). Позволяет не указывать тип явно, если он однозначно выводится из выражения инициализации.

**Является ли `var` ключевым словом?**

`var` — это **зарезервированное имя типа** (reserved type name), а **не** ключевое слово (keyword). Практические следствия:
- Нельзя использовать `var` как имя **класса** или **интерфейса** (ошибка компиляции)
- **Можно** использовать `var` как имя **переменной**, **метода** или **пакета** (хотя это крайне нежелательно для читаемости)

```java
int var = 5;        // допустимо (но плохой стиль)
void var() {}       // допустимо (но плохой стиль)
class var {}        // ОШИБКА компиляции
```

Такое решение принято для обратной совместимости: код, использующий `var` как имя переменной до Java 10, не сломается.

**Где `var` можно использовать:**

```java
// 1. Локальная переменная с инициализатором
var list = new ArrayList<String>();   // тип: ArrayList<String>
var map = new HashMap<String, Integer>();

// 2. Классический for-цикл
for (var i = 0; i < 10; i++) { ... }

// 3. Enhanced for-цикл
for (var item : list) { ... }

// 4. try-with-resources
try (var reader = new BufferedReader(new FileReader("file.txt"))) { ... }

// 5. Параметры лямбд (Java 11+) — позволяет добавлять аннотации
var result = list.stream()
    .filter((@NonNull var s) -> s.length() > 3)
    .collect(toList());
```

**Где `var` нельзя использовать:**

```java
// НЕЛЬЗЯ: поле класса
class Foo {
    var field = "hello";     // ОШИБКА: var не разрешён для полей
}

// НЕЛЬЗЯ: параметр метода
void process(var input) { } // ОШИБКА

// НЕЛЬЗЯ: возвращаемый тип
var getResult() { ... }     // ОШИБКА

// НЕЛЬЗЯ: без инициализатора
var x;                      // ОШИБКА: нечего выводить

// НЕЛЬЗЯ: инициализация null
var x = null;               // ОШИБКА: тип не определён

// НЕЛЬЗЯ: лямбда без контекста
var f = () -> "hello";      // ОШИБКА: целевой тип не известен

// НЕЛЬЗЯ: инициализатор — массивный литерал
var arr = {1, 2, 3};        // ОШИБКА

// НЕЛЬЗЯ: catch-параметр
try { ... } catch (var e) { ... }  // ОШИБКА
```

**Важный нюанс — выведенный тип фиксируется:**

```java
var list = new ArrayList<String>(); // тип — ArrayList<String>, не List<String>
List<String> lst = list;            // OK
list = new LinkedList<>();          // ОШИБКА: несовместимые типы
```

Это может быть неожиданным, когда вместо интерфейса выводится конкретный класс. Рекомендуется использовать `var` там, где тип очевиден из правой части и не нужна гибкость полиморфной переменной.
### Вопрос 9. Как record ведёт себя при сериализации? Нужно ли объявлять serialVersionUID? Что происходит при десериализации, если компоненты record изменились?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Record Serialization — docs.oracle.com](https://docs.oracle.com/en/java/javase/16/docs/specs/records-serialization.html)

Сериализованная форма объекта-record — это последовательность значений компонентов записи. Десериализация использует только канонический конструктор: JVM находит его по сигнатуре, совпадающей с компонентами, и вызывает с теми значениями, которые были прочитаны из потока.

**serialVersionUID.** Значение по умолчанию — `0L`. Требование совпадения `serialVersionUID` для record-классов снято: JVM не выбрасывает `InvalidClassException` из-за несоответствия UID.

**Нельзя кастомизировать.** Методы `writeObject`, `readObject`, `readObjectNoData`, `writeExternal`, `readExternal`, объявленные в record-классе, игнорируются при сериализации и десериализации. Единственные разрешённые хуки — `writeReplace` и `readResolve`.

**Поведение при изменении компонентов.**

Сопоставление компонентов при десериализации происходит по имени:

- Добавлен новый компонент: компонент не найден в потоке — в канонический конструктор передаётся значение по умолчанию для его типа (`0`, `false`, `null`).
- Удалён компонент: поле из потока не совпадает ни с одним компонентом — оно молча отбрасывается.
- Переименован компонент: старое поле из потока не совпадает с новым именем; компонент получает значение по умолчанию, старые данные теряются.
- Изменён тип компонента: конкретный тип значения из потока должен быть присваиваем (`Class::isAssignableFrom`) типу компонента; иначе бросается `ClassCastException`.

**Несовместимость с обычными классами.** Если существующий `Serializable`-POJO преобразован в record, байты, сериализованные старым классом, не десериализуются новым record-классом: старый поток содержит присваивания полей, новый ожидает аргументы конструктора — форматы структурно несовместимы.

**Циклические ссылки.** Запись handle для record-объекта происходит только после вызова канонического конструктора, поэтому циклические ссылки не восстанавливаются: вместо ссылки на сам объект компонент получит `null`.

#### Ответ от Claude

Record реализует `Serializable` точно так же, как обычный класс — простым объявлением: `record Point(int x, int y) implements Serializable {}`. Никакого дополнительного кода не нужно.

**Механизм сериализации** отличается от обычных классов принципиально:

| Аспект | Обычный Serializable-класс | Record |
|---|---|---|
| `serialVersionUID` | Должен совпадать | Требование снято; по умолчанию `0L` |
| Вызов конструктора при десериализации | Не вызывается | Канонический конструктор обязательно вызывается |
| Кастомизация (`writeObject` / `readObject`) | Поддерживается | Игнорируется |
| `serialPersistentFields` | Поддерживается | Игнорируется |
| Циклические ссылки | Сохраняются | Не сохраняются |
| Разрешённые хуки | Любые | Только `writeReplace` / `readResolve` |

**Нужно ли объявлять `serialVersionUID`?** Нет — это необязательно и практически не имеет смысла, поскольку проверка UID отключена для record-классов. Указать UID можно явно только в целях документирования или совместимости при миграции с legacy-классов.

**Что происходит при изменении компонентов** (сопоставление по имени):

```java
// Было:
record Person(String name, int age) implements Serializable {}

// Стало — добавлен компонент:
record Person(String name, int age, String email) implements Serializable {}
// email при чтении старого потока → null (значение по умолчанию для ссылочного типа)

// Стало — удалён компонент:
record Person(String name) implements Serializable {}
// поле age из потока молча отбрасывается

// Стало — изменён тип:
record Person(String name, String age) implements Serializable {}
// int-значение age из потока несовместимо с String → ClassCastException при десериализации
```

**Важное следствие вызова канонического конструктора:** любые проверки, помещённые в compact-конструктор, выполняются при каждой десериализации, что делает record-сериализацию безопаснее обычной (нельзя обойти инварианты объекта через поток).

**Расхождение между источниками.** Официальная спецификация (`records-serialization.html`, Java 16) и документация Java 25 (`language/records.html`) согласованы по всем ключевым пунктам. Ресурс Java Code Geeks добавляет практическое замечание о несовместимости проводного формата при конвертации POJO → record, что подтверждается спецификацией.

---

### Вопрос 10. Можно ли объявить generic record? Какие ограничения накладываются на параметры типа? Как record-паттерн работает с generic record в switch?

**Категория:** Современная Java · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Record Patterns — docs.oracle.com, Java 22](https://docs.oracle.com/en/java/javase/22/language/record-patterns.html)

Да, record может быть generic. Объявление полностью аналогично обычному generic-классу:

```java
record Box<T>(T t) { }
```

**Ограничения при использовании в паттернах.** Нельзя применить record-паттерн, если это потребует непроверяемого (unchecked) приведения типа:

```java
static void uncheckedConversion(Box bo) {
    // ошибка компиляции: Box нельзя безопасно привести к Box<String>
    if (bo instanceof Box<String>(var s)) {
        System.out.println("String " + s);
    }
}
```

Допустимый вариант — когда тип уже параметризован:

```java
static void printBoxContents(Box<String> bo) {
    if (bo instanceof Box<String>(String s)) {  // OK
        System.out.println("Box contains: " + s);
    }
}
```

**Вывод типов.** Компилятор выводит аргументы типа во всех конструкциях, принимающих паттерны — `instanceof`, `switch`-выражения и `switch`-операторы:

```java
static void printBoxContentsAgain(Box<String> bo) {
    // Box(var s) выводится как Box<String>(String s)
    if (bo instanceof Box(var s)) {
        System.out.println("Box contains: " + s);
    }
}
```

Вложенные generic record также поддерживают вывод типов:

```java
static void nestedBox(Box<Box<String>> bo) {
    // Box(Box(var s)) выводится как Box<Box<String>>(Box(String s))
    if (bo instanceof Box(Box(var s))) {
        System.out.println("String " + s);
    }
}
```

#### Ответ от Claude

**Можно ли объявить generic record?** Да. Generic record объявляется стандартным образом — параметры типа идут сразу после имени, перед заголовком компонентов:

```java
record Pair<A, B>(A first, B second) {}
record Triangle<C extends Coordinate>(C top, C left, C right) {}
```

**Ограничения на параметры типа при объявлении record:**

1. Применяются те же правила, что для обычных generic-классов (JLS §8.1.2): допустимы верхние ограничения (`extends`), множественные ограничения (`extends I1 & I2`), параметры без ограничений (`<T>`).
2. Record не может быть `abstract` (compile-time error), поэтому параметры типа не могут быть использованы в `abstract`-методах через дополнительное ограничение.
3. Вайлдкарды (`?`) запрещены в объявлениях компонентов record, поскольку компоненты — это поля; вайлдкарды допустимы только как аргументы типа во вложенных generic-типах.
4. Область видимости параметра типа включает весь заголовок record (список компонентов), что закреплено в JLS.
5. Вложенные record неявно являются `static`, поэтому ссылаться на параметр типа внешнего класса из вложенного record нельзя.

**Record-паттерн с generic record в switch:**

Паттерн проверяет экземпляр и деструктурирует компоненты за один шаг. Для generic record действуют два правила:

- **Unchecked conversion запрещён.** Если тип переменной — raw или несовместимый параметризованный тип, использование конкретного параметра типа в паттерне приведёт к ошибке компиляции.
- **Вывод типов.** Если достаточно контекста, компилятор сам выводит аргументы типа.

```java
record Box<T>(T t) {}

// switch с generic record и явным типом
static String describe(Object obj) {
    return switch (obj) {
        case Box<String>(String s) -> "строка: " + s;
        case Box<Integer>(Integer i) -> "число: " + i;
        default -> "другое";
    };
}

// switch с выводом типов через var
static void printBox(Box<String> box) {
    switch (box) {
        case Box(var s) -> System.out.println(s); // s имеет тип String
    }
}

// ОШИБКА: unchecked conversion — raw Box нельзя проверить как Box<String>
static void broken(Box raw) {
    switch (raw) {
        case Box<String>(var s) -> {} // compile-time error
    }
}
```

**Exhaustiveness и generic record в switch.** Компилятор анализирует полноту переключателя с учётом типов. Для sealed-иерархий с параметрами типа это может привести к нетривиальным случаям:

```java
sealed interface I<T> permits A, B {}
final class A<X> implements I<String> {}
final class B<Y> implements I<Y> {}

static int test(I<Integer> i) {
    return switch (i) {
        case B<Integer> bi -> 42;
        // default не нужен: A никогда не реализует I<Integer>
    };
}
```

**Вывод.** Generic record — полноценный инструмент, без дополнительных ограничений на объявление помимо стандартных правил generics. Основное ограничение при использовании в паттернах — запрет unchecked conversion; вывод типов снимает необходимость явно указывать аргументы там, где контекст достаточен.

---

### Вопрос 11. Что такое «доминирование» (dominance) паттернов в switch? Почему компилятор запрещает размещать более общий паттерн перед более специфичным?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Pattern Matching for switch — docs.oracle.com, Java 21](https://docs.oracle.com/en/java/javase/21/language/pattern-matching-switch.html)

Метка switch называется **доминированной**, если для каждого значения, которое она могла бы обработать, одна из предшествующих меток тоже подошла бы. Наличие доминированной метки — ошибка компиляции.

**Доминирование типовых паттернов:**

```java
static void error(Object obj) {
    switch (obj) {
        case CharSequence cs ->          // более общий тип
            System.out.println("Длина: " + cs.length());
        case String s ->                 // ошибка: String — подтип CharSequence
            System.out.println("Строка: " + s);
        default -> { break; }
    }
}
```

**Доминирование над константами:**

```java
static void error2(Integer value) {
    switch (value) {
        case Integer i ->
            System.out.println("Integer: " + i);
        case -1, 1 ->           // ошибка: оба значения уже покрыты паттерном Integer
            System.out.println("The number");
        default -> { break; }
    }
}
```

**Охраняемые паттерны не доминируют** (guards в compile-time не анализируются):

```java
static void testInteger(Integer value) {
    switch (value) {
        case Integer i when i > 0 ->    // охраняемый: не доминирует
            System.out.println("Положительное");
        case 1 ->                        // допустимо
            System.out.println("Значение 1");
        case -1 ->
            System.out.println("Значение -1");
        case Integer i ->
            System.out.println("Целое");
    }
}
```

#### Ответ от Claude

**Что такое доминирование паттернов.**

В switch-выражении (и switch-операторе) метки проверяются сверху вниз. Паттерн P1 **доминирует** над паттерном P2, если каждое значение, совпадающее с P2, совпадает и с P1. Если P2 стоит после P1 — она недостижима. Компилятор рассматривает это как ошибку программиста и отвергает такой switch с compile-time error.

Формальное определение из JLS (§14.30.3): метка доминирована, если для каждого возможного значения, к которому она применима, найдётся предшествующая метка, также применимая к этому значению.

**Почему запрещено.** Недостижимый case — признак логической ошибки (перепутан порядок) или мёртвого кода. Раннее обнаружение на этапе компиляции предотвращает трудноуловимые баги в runtime.

**Случаи доминирования:**

1. **Суперитп доминирует над подтипом:**

```java
switch (obj) {
    case Number n  -> ...;   // Number — суперитп Integer
    case Integer i -> ...;   // ошибка: Integer ⊂ Number, паттерн недостижим
}
```

2. **Паттерн доминирует над константой:**

```java
Integer val = ...;
switch (val) {
    case Integer i -> ...;   // покрывает всё
    case 42        -> ...;   // ошибка: 42 — частный случай Integer
}
```

3. **Паттерн доминирует над константой enum:**

```java
switch (color) {
    case Color c -> ...;    // покрывает все значения enum
    case RED     -> ...;    // ошибка: RED ⊂ Color
}
```

4. **Не охраняемый паттерн доминирует над тем же охраняемым:**

```java
switch (str) {
    case String s            -> ...;   // без guard
    case String s when s.isEmpty() -> ...;   // ошибка: предыдущий покрывает всё
}
```

**Охраняемые паттерны (`when`) и доминирование.**

Guard — это произвольное булево выражение, которое компилятор не может вычислить в compile-time. Поэтому:

- Охраняемый паттерн **не доминирует** ни над чем (guard может оказаться `false`).
- Над охраняемым паттерном **не может доминировать** другой охраняемый паттерн с тем же основным паттерном.
- Исключение: guard является константным выражением `true` — тогда охраняемый паттерн `case P when true` доминирует над `case P`.

```java
switch (value) {
    case Integer i when i > 0 -> ...;  // guard: НЕ доминирует
    case 1                    -> ...;  // допустимо (1 > 0, но guard runtime)
    case Integer i            -> ...;  // покрывает оставшееся
}
```

**Рекомендуемый порядок меток (по возрастанию общности):**
1. Константы (`case 42`, `case RED`)
2. Охраняемые паттерны (`case Integer i when i > 0`)
3. Неохраняемые паттерны (`case Integer i`)

**Доминирование и sealed-типы.** Для sealed-иерархии компилятор знает полное множество подтипов и использует это для анализа exhaustiveness и доминирования:

```java
sealed interface Shape permits Circle, Rectangle {}

static double area(Shape s) {
    return switch (s) {
        case Circle c    -> Math.PI * c.r() * c.r();
        case Rectangle r -> r.w() * r.h();
        // default не нужен: все подтипы перечислены
    };
}

// Ошибка: Shape покрывает и Circle, и Rectangle
static void broken(Shape s) {
    switch (s) {
        case Shape sh    -> {};   // доминирует
        case Circle c    -> {};   // ошибка: недостижимо
    }
}
```

**Итог.** Доминирование — статическая гарантия достижимости каждой ветки switch. Компилятор применяет отношение «P1 доминирует P2 ⟺ тип P1 является супертипом типа P2 (или тип P1 == тип P2 и P1 не охраняемый)» и отклоняет код, где недостижимые ветки обнаруживаются до выполнения.
### Вопрос 12. Как sealed-интерфейс влияет на exhaustiveness проверку switch-выражения? Что произойдёт на стадии компиляции и на стадии выполнения, если добавить новый permitted-подтип к sealed-иерархии без обновления switch?

**Категория:** Современная Java · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Pattern Matching for switch — docs.oracle.com (Java SE 21)](https://docs.oracle.com/en/java/javase/21/language/pattern-matching-switch.html)

Если тип selector-выражения в switch — sealed-интерфейс (или sealed-класс), компилятор анализирует его `permits`-список и определяет, покрыты ли все permitted-подтипы существующими ветками. Если покрыты все — switch считается exhaustive и ветка `default` не требуется.

Пример исчерпывающего switch:

```java
sealed interface S permits A, B, C {}
final class A implements S {}
final class B implements S {}
record C(int i) implements S {}

static int testSealedCoverage(S s) {
    return switch (s) {
        case A a -> 1;
        case B b -> 2;
        case C c -> 3;
        // default не нужен — все permitted-подтипы покрыты
    };
}
```

**Отдельная компиляция и runtime.** Поскольку класс, содержащий switch, и sealed-иерархия могут компилироваться независимо, возможна ситуация, когда в runtime иерархия содержит больше подтипов, чем было известно компилятору. Именно для защиты от этого компилятор вставляет синтетическую ветку `default`, которая выбрасывает исключение. Если sealed-иерархия на runtime содержит `permits A, B, C`, но switch был скомпилирован против `permits A, B`, при поступлении значения типа `C` будет выброшен `java.lang.MatchException` — исключение, введённое в Java 21. Это называется separate compilation anomaly.

#### Ответ от Claude

**Как sealed-интерфейс влияет на exhaustiveness-проверку**

Sealed-иерархия даёт компилятору исчерпывающий список разрешённых подтипов через `permits`. Когда switch-выражение (или switch-statement с pattern matching) использует sealed-тип в качестве selector, компилятор проводит exhaustiveness-анализ: он проверяет, что каждый permitted-подтип покрывается хотя бы одной веткой. Если это условие выполнено, ветка `default` не нужна — её отсутствие не является ошибкой компиляции. Если какой-то подтип не покрыт, компилятор выдаёт ошибку `the switch expression does not cover all possible input values`.

Компилятор также учитывает generic-параметры: если `sealed interface I<T> permits A, B` и selector имеет тип `I<Integer>`, а `A` реализует только `I<String>`, то ветка для `A` не нужна — компилятор это понимает.

**Стадия компиляции при добавлении нового permitted-подтипа**

Допустим, в иерархии добавляется новый подтип `C`, а класс со switch не перекомпилируется:

- При повторной компиляции класса со switch — компилятор немедленно выдаст ошибку: switch больше не исчерпывающий, ветка `C` не покрыта.
- Если класс со switch НЕ перекомпилируется — компилятор ошибку не видит, бинарник остаётся «старым».

**Стадия выполнения**

Для обработки сценария раздельной компиляции (separate compilation anomaly) компилятор при генерации exhaustive switch над sealed-типом вставляет синтетическую ветку `default`, которая выбрасывает `java.lang.MatchException`. Эта ветка невидима в исходном коде, но присутствует в байткоде.

Если в runtime JVM загружает новый подтип `C`, а в switch нет соответствующей ветки, управление попадает в синтетический `default` и программа завершается с:

```
Exception in thread "main" java.lang.MatchException
    at com.example.Main.main(Main.java:10)
```

`MatchException` — наследник `RuntimeException`, введён в Java 21 (JEP 441). Он также выбрасывается при несоответствии на enum-типах (если enum получил новую константу без перекомпиляции switch) и при некоторых вырожденных случаях с null в record-паттернах.

**Итог: сравнительная таблица**

| Сценарий | Поведение |
|---|---|
| Switch покрывает все `permits` при компиляции | Компилируется без `default`, exhaustive |
| `permits` расширен, класс со switch перекомпилирован | Ошибка компиляции — добавьте ветку для нового типа |
| `permits` расширен, класс со switch НЕ перекомпилирован | Компиляция успешна (старый бинарник), `MatchException` в runtime |

**Рекомендация:** sealed-иерархии в публичном API библиотек следует использовать с осторожностью: добавление нового подтипа является бинарно несовместимым изменением для клиентов, которые используют exhaustive switch без `default`.

---

### Вопрос 13. Чем отличаются exports и opens в module-info.java? В каких случаях необходим opens вместо exports и почему фреймворки (Spring, Hibernate) требуют opens?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Qualified exports and opens — dev.java](https://dev.java/learn/modules/qualified-exports-opens/)

Директива `exports` делает пакет доступным для других модулей на этапе компиляции и выполнения, но только для обращения к public-типам и их public-членам.

Директива `opens` предоставляет доступ к пакету исключительно на этапе выполнения через рефлексию. При этом `opens` разрешает «глубокую рефлексию» (deep reflection) — доступ к non-public типам и членам (private-полям, закрытым конструкторам и т.п.). На этапе компиляции пакет, указанный в `opens`, остаётся закрытым.

Фреймворки, выполняющие рефлексию над пользовательскими классами, должны получать доступ именно через `opens`, а не `exports`. Ключевое требование: пакет должен быть открыт тому модулю, который фактически выполняет рефлексию. Например, для Hibernate:

```java
module com.example.app {
    opens com.example.app.entity to hibernate.core;
}
```

#### Ответ от Claude

**Ключевые различия exports и opens**

| Характеристика | `exports` | `opens` |
|---|---|---|
| Доступность на этапе компиляции | Да (public-типы и public-члены) | Нет |
| Доступность на этапе выполнения | Да (public-типы и public-члены) | Да (через рефлексию) |
| Глубокая рефлексия (private-члены) | Нет | Да |
| Прямое использование кода (вызов методов) | Да | Нет |

`exports` — это стандартный механизм публикации API: другой модуль может импортировать типы из экспортированного пакета и использовать их в коде напрямую.

`opens` — это механизм разрешения рефлексии: другой модуль не может использовать типы из открытого пакета в коде напрямую, но может вызывать `Class.forName()`, `getDeclaredField()`, `setAccessible(true)` и т.п.

Допустимо совмещать оба: `exports com.example.model; opens com.example.model to hibernate.core;` — тогда пакет доступен и для обычного кода, и для рефлексии Hibernate.

Существует также модификатор `open module` (без указания пакетов), который открывает для рефлексии все пакеты модуля разом.

**Когда необходим opens вместо exports**

`opens` обязателен, когда сторонний код должен выполнять рефлексию над типами пакета — в частности:
- читать или записывать private-поля;
- вызывать private-конструкторы или методы через `setAccessible(true)`;
- генерировать прокси-классы или манипулировать байткодом на основе структуры класса.

До Java 9 рефлексия была всесильна и не уважала модификаторы доступа. С появлением JPMS сильная инкапсуляция распространилась и на рефлексию: попытка вызвать `setAccessible(true)` на членах закрытого пакета завершается `InaccessibleObjectException`.

**Почему Spring и Hibernate требуют opens**

Spring использует рефлексию для:
- инъекции зависимостей в поля, помеченные `@Autowired` (в том числе private);
- создания CGLIB-прокси на основе структуры класса;
- чтения аннотаций на private-методах и полях.

Hibernate использует рефлексию для:
- доступа к private-полям JPA-сущностей (field-based access);
- построения маппинга на основе аннотаций `@Column`, `@Id` и т.п.;
- генерации прокси для ленивой загрузки (lazy loading).

Без соответствующих `opens` обращение к private-членам вызывает `java.lang.reflect.InaccessibleObjectException` в Java 9+ (до Java 16 выводилось предупреждение `WARNING: An illegal reflective access operation has occurred`; с Java 16 поведение стало жёстким).

Пример корректного module-info.java для Spring-приложения:

```java
module com.example.app {
    requires spring.context;
    requires spring.beans;
    requires hibernate.core;
    requires jakarta.persistence;

    // Spring нужен доступ к рефлексии сервисов
    opens com.example.app.service to spring.beans, spring.context;
    // Hibernate нужен доступ к entity-классам
    opens com.example.app.entity to hibernate.core;
    // Публичный API
    exports com.example.app.api;
}
```

**Важное уточнение:** открывать пакет нужно именно тому модулю, который фактически выполняет рефлексию. Если открыть только API-модуль фреймворка (например, `jakarta.persistence`), а сама рефлексия происходит в реализации (`hibernate.core`), доступ будет отклонён.

---

### Вопрос 14. Что такое automatic module и unnamed module в JPMS? Чем они отличаются друг от друга и от named module? Почему нельзя опубликовать библиотеку как automatic module?

**Категория:** Современная Java · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Java SE 9 — JPMS automatic modules — blog.joda.org (Stephen Colebourne)](https://blog.joda.org/2017/05/java-se-9-jpms-automatic-modules.html)

Automatic module — это обычный JAR-файл без `module-info.class`, помещённый на modulepath (а не classpath). JPMS автоматически назначает ему имя (из `Automatic-Module-Name` в `MANIFEST.MF` или выводит из имени JAR-файла), экспортирует все его пакеты и неявно объявляет зависимость на все остальные модули.

Unnamed module — это всё, что загружено через classpath. У него нет имени, поэтому на него нельзя сослаться в `module-info.java` через `requires`.

**Почему нельзя публиковать библиотеку в Maven Central как automatic module (то есть modular JAR, зависящий от automatic module):** любой JAR, который выражает зависимость (`requires`) на имя, производное от имени файла, станет причиной «Module Hell». Когда зависимая библиотека позднее станет named module, её имя изменится — и все потребители, зависящие от старого автоматического имени, сломаются. Решение: добавить в `MANIFEST.MF` запись `Automatic-Module-Name` с корректным именем ещё до появления `module-info.java`, чтобы имя оставалось стабильным при переходе.

#### Ответ от Claude

**Три типа модулей в JPMS**

**Named module (явный / explicit module)**

JAR с файлом `module-info.class` в корне. Явно объявляет:
- имя модуля;
- зависимости (`requires`);
- экспортируемые пакеты (`exports`);
- открытые для рефлексии пакеты (`opens`).

Помещается на modulepath. Имеет строгую инкапсуляцию: неэкспортированные пакеты не видны извне даже через рефлексию.

**Automatic module**

Обычный JAR без `module-info.class`, помещённый на **modulepath** (не на classpath). JPMS обрабатывает его автоматически:
- имя берётся из `Automatic-Module-Name` в `MANIFEST.MF`; если записи нет — выводится из имени JAR-файла (удаляется расширение и версия, дефисы заменяются точками, например `guava-31.0.jar` → `guava`);
- все пакеты автоматически экспортируются;
- неявно читает (requires) все остальные модули на modulepath;
- может читать unnamed module (classpath).

**Unnamed module**

Всё, что загружено через **classpath** (старый механизм). Не имеет имени. Особенности:
- читает все модули, но на него нельзя сослаться через `requires` в `module-info.java` (нет имени);
- named module не может явно зависеть от unnamed module;
- automatic module может читать unnamed module — именно это обеспечивает совместимость: смешанные classpath/modulepath-конфигурации работают через automatic modules как посредников.

**Сравнительная таблица**

| Характеристика | Named module | Automatic module | Unnamed module |
|---|---|---|---|
| Наличие module-info.class | Да | Нет | Нет |
| Расположение | modulepath | modulepath | classpath |
| Имя | Явное | Из MANIFEST или имени JAR | Нет имени |
| Экспорт пакетов | Явный (только указанные) | Все пакеты | Все (нет инкапсуляции) |
| Чтение других модулей | Только через requires | Все named + unnamed | Все |
| Может быть указан в requires | Да | Да | Нет |
| Может читать unnamed module | Нет | Да | — |

**Почему нельзя публиковать библиотеку как automatic module**

Речь идёт о следующем анти-паттерне: библиотека A публикует в Maven Central modular JAR (с `module-info.class`), который содержит `requires guava` — при этом Guava ещё не имеет `module-info.class` и является automatic module с именем `guava` (из имени файла).

Проблема («Module Hell»): когда Guava выпустит named module с именем, например, `com.google.common`, все библиотеки, которые зависят от имени `guava`, сломаются — такого модуля больше не существует. Починить это без изменения `module-info.java` потребителей невозможно.

Mitigation: добавить в `MANIFEST.MF` запись:

```
Automatic-Module-Name: com.google.common
```

Это стабилизирует имя automatic module до появления настоящего `module-info.java`. Когда библиотека добавит `module-info.java` с тем же именем — потребители не сломаются.

**Правило** (сформулированное Stephen Colebourne и принятое в сообществе): не выпускать в Maven Central modular JAR (с `module-info.class`), зависящий от automatic module без `Automatic-Module-Name`. Исключение — если automatic module находится под вашим контролем и вы можете синхронизировать переход.

Дополнительная причина: named module не может `requires` unnamed module в принципе — unnamed module не имеет имени. Это означает, что полностью модулярное приложение не может напрямую зависеть от библиотек, оставшихся только на classpath, без промежуточного automatic module.

---
### Вопрос 15. Что такое split package в JPMS и почему модульная система запрещает его даже если пакет не экспортируется?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java 9 modules — JPMS basics (Stephen Colebourne's blog)](https://blog.joda.org/2017/04/java-9-modules-jpms-basics.html)

**Split package** (разделённый пакет) — ситуация, когда один и тот же пакет (одно и то же имя пакета) присутствует более чем в одном модуле. Модульная система Java (JPMS) полностью запрещает это: «два модуля не могут содержать один и тот же пакет». Это кажется очевидным, пока не осознаёшь, что ограничение распространяется и на **скрытые (не экспортированные) пакеты**.

Поскольку скрытые пакеты не появляются в `module-info.class` напрямую как экспортируемые, разработчики не видят их задокументированными. Возникает неожиданное ограничение: инструмент вроде Maven должен распаковывать JAR-файл, чтобы обнаружить скрытые пакеты и предупредить о конфликтах.

В отличие от старых систем модулей (OSGi, JBoss Modules), которые запускали каждый модуль в отдельном ClassLoader, JPMS интегрирован непосредственно в JVM и использует единое пространство имён пакетов для всех модулей. Это значит, что нет изоляции ClassLoader, которая скрывала бы дублирование имён пакетов — всё проверяется на уровне модульного разрешения при старте JVM.

#### Ответ от Claude

**Split package** — ситуация, когда одно и то же имя пакета присутствует в двух или более модулях одновременно. Например, если `module-a` содержит класс `com.example.util.Foo`, а `module-b` — класс `com.example.util.Bar`, оба модуля «претендуют» на пакет `com.example.util`. JPMS запрещает это безоговорочно.

**Технические причины запрета, включая неэкспортируемые пакеты:**

1. **Единый ClassLoader для всех модулей одного слоя.** В JPMS все именованные модули загружаются через единый ClassLoader приложения (или через ClassLoader соответствующего слоя модулей). ClassLoader ведёт внутреннюю таблицу «имя пакета → модуль», и одному пакету может соответствовать только одна запись. Если два модуля объявляют один пакет, уже при загрузке модулей (до любых экспортов) возникает неразрешимый конфликт. JVM завершает работу с ошибкой при старте.

2. **Видимость в пределах одного модуля.** Даже если пакет не экспортирован, классы внутри него видны другим классам *того же модуля*. Если пакет разделён между двумя модулями, то классы из `module-a` в пакете `com.example.util` не могут «увидеть» классы из `module-b` в том же пакете без явного экспорта. Это нарушает принцип целостности пакета: пакет в Java традиционно является единицей видимости (package-private доступ), и разделение этой единицы между модулями делает семантику доступа непредсказуемой.

3. **Безопасность и предсказуемость.** Разрешение split packages открыло бы вектор атаки: вредоносный JAR мог бы подмешать класс в доверенный пакет (например, `java.lang`), добавив его в свой модуль. Запрет на уровне разрешения модулей закрывает эту уязвимость полностью.

4. **Детерминированность разрешения модулей.** При старте JVM граф модулей должен быть разрешён однозначно. Алгоритм разрешения модулей (module resolution) строит направленный граф зависимостей. Если один пакет принадлежит двум модулям, граф содержит неустранимую неопределённость: из какого модуля брать класс при загрузке? Запрет split packages делает разрешение детерминированным.

**Отличие от classpath.** До JPMS classpath позволял одному пакету присутствовать в нескольких JAR-файлах — загрузчик класса находил первое вхождение и использовал его, что приводило к трудно отлаживаемым проблемам («classpath hell»). JPMS устраняет эту проблему, гарантируя, что каждый пакет принадлежит ровно одному модулю.

**Практические следствия:**
- Если используется не-модульная библиотека (automatic module или unnamed module) и она содержит пакет, присутствующий в именованном модуле — это тоже split package, и JVM откажется загружаться.
- Решения: переименование пакетов, слияние модулей, использование «fat JAR» как единого unnamed-модуля, или ожидание перехода библиотеки на JPMS.

---

### Вопрос 16. Что такое «pinning» виртуального потока? В каких ситуациях в Java 21 виртуальный поток оказывается прикреплён к carrier-потоку? Как это изменилось в Java 24?

**Категория:** Современная Java · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Virtual Threads (Oracle Java 21 Documentation)](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)

**Pinning (прикрепление)** виртуального потока — ситуация, когда виртуальный поток не может быть отмонтирован (unmounted) от своего carrier-потока (платформенного потока-носителя) во время блокирующей операции.

Виртуальный поток оказывается прикреплён к carrier-потоку в следующих случаях:
- Виртуальный поток выполняет код внутри блока `synchronized` или `synchronized`-метода.
- Виртуальный поток выполняет нативный метод или иностранную функцию (Foreign Function).

Pinning не делает программу некорректной, но может ухудшить её масштабируемость. Частое и длительное pinning вредит, поскольку carrier-поток оказывается заблокирован вместо того, чтобы выполнять другие виртуальные потоки.

Для диагностики pinning используется:
- JVM-флаг: `-Djdk.tracePinnedThreads=full` или `-Djdk.tracePinnedThreads=short` — выводит стектрейсы при закреплении.
- JFR-событие `jdk.VirtualThreadPinned` — включено по умолчанию с порогом 20 мс.

Рекомендуемое решение для Java 21: заменить `synchronized` на `ReentrantLock` в блоках с длительными блокирующими операциями.

#### Ответ от Claude

**Pinning (прикрепление) виртуального потока** — ситуация, когда виртуальный поток не может быть отмонтирован от carrier-потока (платформенного OS-потока) в момент блокирующей операции. В норме виртуальный поток при блокировке «паркуется» и unmount-ится, освобождая carrier для выполнения других виртуальных потоков. При pinning carrier остаётся заблокированным вместе с виртуальным потоком, что уничтожает преимущество масштабируемости.

**Ситуации pinning в Java 21:**

1. **Блок `synchronized` или `synchronized`-метод, содержащий блокирующую операцию.**
   Технически причина архитектурная: в Java 21 монитор объекта (object monitor) записывает в качестве владельца блокировки OS-поток (carrier thread), а не виртуальный поток. Когда виртуальный поток входит в `synchronized`-блок и затем выполняет блокирующую операцию (I/O, `Thread.sleep()`, `Object.wait()`), JVM вынужден оставить его прикреплённым к carrier — иначе при unmount другой виртуальный поток оказался бы на carrier, который «держит» монитор, никогда его не захватывая. Это нарушило бы взаимное исключение. Поэтому JVM не имеет безопасного выбора, кроме как держать виртуальный поток прикреплённым до выхода из `synchronized`.

2. **Нативный метод или вызов через JNI / Foreign Function and Memory API.**
   Виртуальный поток не может быть отмонтирован в середине выполнения нативного кода, потому что JVM не умеет сохранить состояние нативного стека как continuation. Carrier должен оставаться привязанным на всё время выполнения нативного кода.

**Последствия pinning в Java 21:**
- Если все carrier-потоки заняты прикреплёнными виртуальными потоками, планировщик не может назначить новые виртуальные потоки. При полном исчерпании JVM создаёт временные дополнительные carrier-потоки, но в крайнем случае (deadlock по pinning) система может зависнуть.
- Реальный случай: Netflix обнаружил зависание после включения виртуальных потоков — библиотека Brave/Zipkin вызывала `RealSpan.finish()`, содержавший `synchronized`-блок с блокирующими операциями, что исчерпывало все carrier-потоки.

**Изменения в Java 24 (JEP 491 — «Synchronize Virtual Threads without Pinning»):**

JEP 491 кардинально изменил реализацию мониторов. Фундаментальный сдвиг: **владение монитором теперь ассоциировано с виртуальным потоком, а не с carrier-потоком.** Виртуальные потоки могут захватывать, удерживать и освобождать мониторы независимо от carrier. При блокировке внутри `synchronized`-блока виртуальный поток теперь свободно unmount-ится, а монитор «путешествует» вместе с виртуальным потоком между carrier-потоками.

Практический результат:
- Блок `synchronized` с блокирующими I/O-операциями больше **не вызывает pinning**.
- `ConcurrentHashMap.computeIfAbsent()` и другие стандартные конструкции, использующие `synchronized` внутри, стали безопасными.
- Флаг `-Djdk.tracePinnedThreads=full` удалён как ненужный.
- Замена `synchronized` на `ReentrantLock` больше не требуется в качестве workaround.

**Что остаётся pinned в Java 24+:**
Только нативные методы и вызовы через JNI/Foreign Function по-прежнему вызывают pinning — это фундаментальное ограничение, связанное с невозможностью сохранить нативный стек как continuation. Для серверных приложений, где нативный код не находится на пути обработки запросов, это ограничение практически незначимо.

| Ситуация | Java 21–23 | Java 24+ |
|---|---|---|
| `synchronized` с блокирующей операцией | Pinning | Нет pinning (JEP 491) |
| Нативный метод / JNI | Pinning | Pinning (остаётся) |
| `ReentrantLock` с блокирующей операцией | Нет pinning | Нет pinning |

---

### Вопрос 17. В чём разница между StructuredTaskScope.ShutdownOnFailure и ShutdownOnSuccess? Когда применяется каждый из них? Как реализован паттерн «первый успешный ответ из нескольких источников»?

**Категория:** Современная Java · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [StructuredTaskScope.ShutdownOnFailure (Java SE 21 & JDK 21, Oracle Docs)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/StructuredTaskScope.ShutdownOnFailure.html)

`ShutdownOnFailure` — реализация `StructuredTaskScope`, реализующая политику «invoke all». Захватывает исключение первой провалившейся подзадачи и завершает (shutdown) область задач, прерывая незавершённые потоки и пробуждая владельца области. Предназначен для случаев, когда нужны результаты **всех** подзадач: если одна подзадача провалилась, результаты остальных незавершённых подзадач больше не нужны.

Ключевые методы: `join()` — ждёт завершения всех подзадач или провала первой; `throwIfFailed()` — выбрасывает `ExecutionException`, если хотя бы одна подзадача провалилась.

`ShutdownOnSuccess` (из документации Oracle) — реализует политику «invoke any». Захватывает результат первой успешно завершившейся подзадачи и завершает область задач, прерывая незавершённые потоки. Предназначен для случаев, когда достаточно результата **любой** подзадачи. Ключевой метод: `result()` — возвращает результат первой успешной подзадачи.

#### Ответ от Claude

`StructuredTaskScope` (preview API в Java 21, стабилизировано в последующих версиях) — базовый класс для структурированного параллелизма. Он обеспечивает управление жизненным циклом группы подзадач как единого блока. Два встроенных класса-политики реализуют два классических паттерна параллельного выполнения:

**ShutdownOnFailure — паттерн «invoke all» (нужны все результаты):**
- Ждёт завершения **всех** подзадач.
- Если **хотя бы одна** подзадача проваливается — немедленно прерывает все остальные (shutdown) и пробуждает владельца области.
- После `join()` вызывается `throwIfFailed()` — если был провал, выбрасывается `ExecutionException` с причиной первого провала.
- Применяется: параллельное получение данных из нескольких источников, когда все данные необходимы для формирования ответа (например, одновременный запрос к нескольким микросервисам для сборки агрегированного ответа).

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User> userTask     = scope.fork(() -> userService.fetchUser(userId));
    Subtask<Order> orderTask   = scope.fork(() -> orderService.fetchOrder(orderId));
    Subtask<Price> priceTask   = scope.fork(() -> pricingService.getPrice(itemId));

    scope.join();           // ждём всех или первого сбоя
    scope.throwIfFailed();  // пробрасываем исключение при сбое

    // все три задачи завершились успешно
    return new Response(userTask.get(), orderTask.get(), priceTask.get());
}
```

**ShutdownOnSuccess — паттерн «invoke any» (достаточно одного результата):**
- Ждёт **первой успешно завершившейся** подзадачи.
- Как только одна подзадача возвращает результат — немедленно прерывает остальные (shutdown).
- `result()` возвращает результат первой успешной подзадачи; если ни одна не завершилась успешно, а хотя бы одна провалилась — выбрасывает `ExecutionException`.
- Применяется: запрос к нескольким равноценным источникам данных (несколько реплик, несколько CDN, несколько геолокационных серверов), где нужен самый быстрый ответ.

**Паттерн «первый успешный ответ из нескольких источников»:**

```java
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<VerificationResult>()) {
    scope.fork(() -> verificationServiceA.verify(request));
    scope.fork(() -> verificationServiceB.verify(request));
    scope.fork(() -> verificationServiceC.verify(request));

    scope.join(); // ждём первого успеха или завершения всех

    return scope.result(); // результат самого быстрого сервиса
}
```

Как только один из сервисов возвращает результат, остальные два запроса автоматически прерываются (через interruption виртуального потока). Это реализует семантику «гонки» (race) без ручного управления прерываниями.

**Ключевые различия:**

| Аспект | ShutdownOnFailure | ShutdownOnSuccess |
|---|---|---|
| Паттерн | invoke all | invoke any |
| Условие завершения | Все успешны ИЛИ первый провал | Первый успех |
| Результат | Все результаты через `subtask.get()` | Один результат через `scope.result()` |
| При провале | Прерывает остальных, выбрасывает исключение | Продолжает ждать остальных |
| Применение | Сборка агрегированного ответа | Дублирование запросов, выбор самого быстрого |

**Расхождение источников:** Medium-статья перечисляет `lock.lock()` и `ThreadLocal` как дополнительные причины pinning в Java 21 — это неточность. Официальная документация Oracle (docs.oracle.com) и JEP 491 называют только два случая: `synchronized` и нативные методы/JNI. `ReentrantLock` специально спроектирован совместимым с виртуальными потоками и pinning не вызывает.

**Эволюция API:** В Java 25 API структурированного параллелизма претерпело изменения: вместо классов `ShutdownOnFailure`/`ShutdownOnSuccess` вводится новый подход через `StructuredTaskScope.open(Joiner)`, где `Joiner.anySuccessfulResultOrThrow()` реализует семантику `ShutdownOnSuccess`, а `scope.join()` напрямую возвращает результат без отдельного вызова `result()`.
### Вопрос 18. Чем отличается вывод типа у var при объявлении через интерфейс vs конкретный класс? Почему var list = new ArrayList<String>() фиксирует тип как ArrayList, а не List, и к каким проблемам это может привести?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [FAQ for JEP 286 (Local Variable Type Inference)](https://cr.openjdk.org/~briangoetz/jep-286/lvti-faq.html)

Компилятор вычисляет тип переменной, объявленной через `var`, исключительно на основе типа инициализирующего выражения — «we compute the type of x based solely on the type of the initializer». Никакого «чтения мыслей» относительно намерений разработчика не происходит. Поэтому `var list = new ArrayList<String>()` даёт тип `ArrayList<String>`, а не `List<String>`.

Альтернативный подход — вывод наименьшего общего супертипа по всем присваиваниям — был намеренно отвергнут, поскольку «likely to cause more problems that it solves». Такие типы нередко оказываются сложными и неожиданными — например, пересечёнными типами вида `Comparable & Serializable` — и порождают «action at a distance» ошибки: изменение в одном месте кода незаметно меняет выведенный тип переменной, вызывая ошибки компиляции совсем в другом месте.

#### Ответ от Claude

**Механизм вывода типа у `var`**

Ключевое правило: `var` фиксирует **статический тип правой части** выражения как тип переменной. Компилятор не знает, какой интерфейс «имел в виду» разработчик.

```java
// Явная типизация — переменная имеет тип List<String>
List<String> list1 = new ArrayList<>();

// var — переменная имеет тип ArrayList<String>
var list2 = new ArrayList<String>();
```

Разница принципиальная: `list1` — ссылка типа `List<String>`, `list2` — ссылка типа `ArrayList<String>`.

**Что фиксируется в каждом случае**

| Объявление | Выведенный тип |
|---|---|
| `var x = new ArrayList<String>()` | `ArrayList<String>` |
| `var x = List.of("a", "b")` | `List<String>` (т.к. `List.of` возвращает `List<E>`) |
| `var x = Collections.unmodifiableList(list)` | `List<String>` |

**К каким проблемам приводит фиксация конкретного типа**

1. **Доступ к методам конкретного класса, нарушающий принцип программирования к интерфейсу.** Когда тип переменной — `ArrayList<String>`, становятся доступны методы, отсутствующие в интерфейсе `List`: `ensureCapacity(int)`, `trimToSize()`, `removeRange(int, int)`. Код начинает зависеть от деталей реализации.

   ```java
   var list = new ArrayList<String>();
   list.ensureCapacity(100);  // компилируется — тип ArrayList<String>
   // Если позже поменять на LinkedList — не скомпилируется
   ```

2. **Хрупкость при рефакторинге.** Если инициализатор изменится (например, фабричный метод вернёт другой тип), выведенный тип переменной незаметно изменится, что может породить ошибки в последующем коде. Именно это OpenJDK называет «action at a distance».

3. **Нарушение инкапсуляции в цепочках вызовов.** Если такая `var`-переменная передаётся в метод, её конкретный тип «просачивается» через API, затрудняя смену реализации.

**Когда конкретный тип через `var` оправдан**

Согласно официальным Style Guidelines (OpenJDK), `var` с конкретным классом уместен, когда конкретный тип действительно нужен — например, для вызова методов, специфичных для реализации:

```java
var arrayDeque = new ArrayDeque<String>();
arrayDeque.addFirst("first");  // метод Deque, но явно нужна конкретная структура
```

**Правило из Style Guidelines**: применяйте `var` там, где тип очевиден из контекста или избыточен; если важен тип-интерфейс — пишите его явно.

**Вывод.** `var` инферирует конкретный тип потому, что компилятор использует только тип инициализирующего выражения. При `new ArrayList<String>()` этот тип — `ArrayList<String>`. Это противоречит принципу «программирования к интерфейсу» (Effective Java, Item 64) и может привести к зависимости от деталей реализации и хрупкости кода при рефакторинге.

---

### Вопрос 19. Как работают takeWhile() и dropWhile() в Stream API (Java 9) на неупорядоченных (unordered) потоках? В чём их принципиальное отличие от filter()?

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Stream (Java SE 21 & JDK 21) — официальный Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html)

**takeWhile(Predicate)** — если поток упорядочен, возвращает наидлиннейший префикс элементов, удовлетворяющих предикату: первый элемент последовательности — первый элемент потока, элемент сразу за последним — не удовлетворяет предикату. Если поток неупорядочен и некоторые (но не все) элементы удовлетворяют предикату, поведение операции **нестабильно (nondeterministic)**: операции разрешено взять любое подмножество подходящих элементов, в том числе пустое.

**dropWhile(Predicate)** — если поток упорядочен, отбрасывает наидлиннейший префикс элементов, удовлетворяющих предикату, и возвращает оставшиеся. Если поток неупорядочен, поведение также нестабильно: операции разрешено отбросить любое подмножество подходящих элементов.

`takeWhile` — короткозамкнутая (short-circuiting) операция; `dropWhile` — нет. Обе — stateful intermediate операции. На упорядоченных параллельных пайплайнах могут быть дорогостоящими, так как требуют соблюдения порядка встречи элементов. Использование `.unordered()` может дать существенный прирост производительности в параллельных пайплайнах.

#### Ответ от Claude

**takeWhile() и dropWhile() — операции на префиксе**

Обе операции появились в Java 9 (JEP 269 «Convenience Factory Methods for Collections» не связан; методы добавлены в рамках расширения Stream API в том же релизе). Их суть — работа с **непрерывным префиксом** потока, а не со всеми элементами.

**Поведение на упорядоченных потоках**

```java
// takeWhile — берём, пока условие выполняется, останавливаемся на первом нарушении
List<Integer> result1 = Stream.of(1, 2, 3, 4, 1, 2)
    .takeWhile(n -> n < 4)
    .collect(Collectors.toList());
// [1, 2, 3] — элемент 4 нарушил предикат, всё после него игнорируется

// dropWhile — пропускаем, пока условие выполняется, отдаём остаток
List<Integer> result2 = Stream.of(1, 2, 3, 4, 1, 2)
    .dropWhile(n -> n < 4)
    .collect(Collectors.toList());
// [4, 1, 2] — отброшен префикс [1, 2, 3], начиная с 4 — остаток
```

**Принципиальное отличие от filter()**

| Характеристика | `filter()` | `takeWhile()` / `dropWhile()` |
|---|---|---|
| Область действия | Все элементы потока | Только префикс (для ordered) |
| Короткое замыкание | Нет — все элементы обходятся | `takeWhile` — да; `dropWhile` — нет |
| Стационарность | Stateless | Stateful |
| Семантика | «Оставить/удалить подходящие» | «Взять/пропустить начало» |
| Зависимость от порядка | Нет | Критическая для ordered потоков |

```java
// filter() проверяет КАЖДЫЙ элемент независимо
Stream.of(1, 2, 3, 4, 1, 2).filter(n -> n < 4)
// → [1, 2, 3, 1, 2]  — элемент 4 удалён, но после него снова берёт 1 и 2

// takeWhile() останавливается на первом нарушении
Stream.of(1, 2, 3, 4, 1, 2).takeWhile(n -> n < 4)
// → [1, 2, 3]  — остановился на 4, элементы 1, 2 в конце не попали
```

**Поведение на неупорядоченных (unordered) потоках**

Это ключевая ловушка. Если в потоке нет порядка встречи (encounter order), поведение при частичном совпадении предиката становится **нестабильным**:

```java
// HashSet — неупорядоченный источник
Set<Integer> set = new HashSet<>(Arrays.asList(1, 2, 3, 4, 5));
List<Integer> res = set.stream()
    .takeWhile(n -> n < 4)
    .collect(Collectors.toList());
// Результат непредсказуем: может быть [], [1], [2, 3], [1, 2] и т.д.
// Это не баг — это задокументированное поведение
```

Согласно Javadoc, реализация «свободна взять любое подмножество подходящих элементов, включая пустое». Два крайних случая остаются стабильными:
- Если **все** элементы удовлетворяют предикату — возвращаются все элементы (для `takeWhile`).
- Если **ни один** не удовлетворяет — возвращается пустой поток (для `takeWhile`).

**Практическое правило**: применяйте `takeWhile`/`dropWhile` только к потокам с гарантированным порядком — `List`, отсортированным потоку, `Stream.of(...)`. На `HashSet`, `HashMap.values()` и им подобных результат непредсказуем.

**Производительность на параллельных пайплайнах**

На упорядоченных параллельных потоках операции дорогостоящи, так как требуют возврата наидлиннейшего префикса именно в encounter order — частичные результаты приходится координировать. Снятие ограничения порядка через `.unordered()` даёт существенный прирост скорости.

---

### Вопрос 20. Что делает Collectors.teeing() (Java 12)? Приведите практический пример, где он позволяет избежать двойного прохода по потоку.

**Категория:** Современная Java · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Collectors (Java SE 12 & JDK 12) — официальный Javadoc Oracle](https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/util/stream/Collectors.html)

`teeing()` — статический метод класса `Collectors`, добавленный в Java 12. Возвращает `Collector`, являющийся композитом двух нижестоящих коллекторов (downstream collectors). Каждый элемент, переданный результирующему коллектору, обрабатывается обоими нижестоящими коллекторами; затем их результаты объединяются с помощью указанной функции слияния (merge function).

Сигнатура:

```java
public static <T, R1, R2, R> Collector<T, ?, R> teeing(
    Collector<? super T, ?, R1> downstream1,
    Collector<? super T, ?, R2> downstream2,
    BiFunction<? super R1, ? super R2, R> merger)
```

- `T` — тип входных элементов потока;
- `R1` — тип результата первого коллектора;
- `R2` — тип результата второго коллектора;
- `R` — тип итогового результата (возвращаемый `merger`).

#### Ответ от Claude

**Что такое Collectors.teeing()**

`Collectors.teeing()` — коллектор-тройник (название отсылает к электротехническому T-образному разветвителю). Он направляет каждый элемент потока одновременно в два независимых коллектора, а затем объединяет их результаты через `BiFunction`. Весь поток проходится ровно **один раз**.

**Проблема, которую решает teeing()**

До Java 12 для получения двух агрегатных значений из потока требовалось либо дважды итерировать источник, либо сохранять промежуточные данные в изменяемые переменные:

```java
// До Java 12 — двойной проход (или буферизация всех элементов)
List<Integer> numbers = List.of(1, 2, 3, 4, 5);

double sum   = numbers.stream().mapToInt(Integer::intValue).sum();
long   count = numbers.stream().count();
double avg   = sum / count;
```

Если источник данных — однопроходный (например, `Stream` из файла, сетевого буфера, генератора), второй проход невозможен в принципе.

**Решение с teeing()**

```java
double avg = Stream.of(1, 2, 3, 4, 5)
    .collect(Collectors.teeing(
        Collectors.summingDouble(Integer::doubleValue),  // downstream1: сумма
        Collectors.counting(),                            // downstream2: количество
        (sum, count) -> sum / count                      // merger: среднее
    ));
// avg = 3.0
```

Поток проходится один раз; каждый элемент параллельно поступает в оба коллектора.

**Практический пример: одновременный поиск минимума и максимума**

```java
record MinMax(Optional<Integer> min, Optional<Integer> max) {}

MinMax result = Stream.of(5, 2, 9, 1, 7, 3)
    .collect(Collectors.teeing(
        Collectors.minBy(Integer::compareTo),   // downstream1: минимум
        Collectors.maxBy(Integer::compareTo),   // downstream2: максимум
        MinMax::new                              // merger: записываем в record
    ));

// result.min() = Optional[1]
// result.max() = Optional[9]
```

До Java 12 нашлось бы два варианта: два раздельных `.stream().collect()` (двойной проход) или ручная редукция с изменяемым состоянием. `teeing()` делает это за один проход читаемым функциональным кодом.

**Ещё один практический пример: разбиение на категории с подсчётом**

```java
record Stats(List<String> passed, long failedCount) {}

Stats stats = employees.stream()
    .collect(Collectors.teeing(
        Collectors.filtering(
            e -> e.score() >= 60,
            Collectors.mapping(Employee::name, Collectors.toList())
        ),
        Collectors.filtering(
            e -> e.score() < 60,
            Collectors.counting()
        ),
        Stats::new
    ));
```

**Важные ограничения**

- `teeing()` не предназначен для трёх и более коллекторов — для этого нужно вкладывать `teeing()` друг в друга (быстро становится нечитаемым) или использовать `Collectors.groupingBy`.
- Оба downstream-коллектора получают **все** элементы, поэтому если один из них делает тяжёлую аккумуляцию (например, собирает в список миллион элементов), экономии памяти нет — только экономия числа проходов.
- Доступен начиная с Java 12; до этой версии аналога в стандартной библиотеке нет.

**Вывод.** `Collectors.teeing()` устраняет необходимость двойного прохода по потоку при вычислении двух независимых агрегатов. Метод особенно ценен при работе с однопроходными или затратными источниками данных.
