# SOLID, чистый код и рефакторинг — часть 1 из 3

> Вопросы 1–20 (в части: 20). Всего в разделе: 50.
> Область знаний: [../knowledge-base/11-solid-clean-code.md](../knowledge-base/11-solid-clean-code.md)
> Правила: [RULES.md](RULES.md)
> Части: **ч.1** · [ч.2](solid-clean-code-02.md) · [ч.3](solid-clean-code-03.md)

---
### Вопрос 1. Что такое принцип единственной ответственности (SRP)? Приведите пример класса, который его нарушает, и объясните, как его исправить.

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [SOLID Design Principles Explained: Building Better Software Architecture | DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)

Принцип единственной ответственности (SRP) гласит: «Класс должен иметь одну и только одну причину для изменения, то есть класс должен выполнять только одну работу».

Нарушение демонстрируется на примере класса `AreaCalculator`, который одновременно вычисляет площади фигур и форматирует вывод результатов. Такой класс имеет две причины для изменения: одна — если меняется алгоритм вычисления площади, другая — если меняется формат вывода.

Исправление выполняется в два шага:
1. Логика вычисления выносится в сами фигуры — каждый класс фигуры реализует метод `area()` и сам знает, как посчитать свою площадь.
2. Логика форматирования выносится в отдельный класс `SumCalculatorOutputter`, единственная ответственность которого — форматировать и отображать результат.

После рефакторинга: `AreaCalculator` меняется только при изменении логики суммирования площадей, а `SumCalculatorOutputter` — только при изменении формата вывода.

#### Ответ от Claude

**Определение.**
SRP — первый из принципов SOLID. Его формулировка по Роберту Мартину: «У класса должна быть только одна причина для изменения». Смысл в том, что каждый класс должен отвечать за одну конкретную область функциональности.

Якоб Дженков уточняет: строгое толкование «одной ответственности» бывает затруднено, потому что ответственности рекурсивно делимы — практичнее говорить о «узкой ответственности».

**Пример нарушения.**

```java
// Нарушение SRP: класс хранит данные о книге И занимается печатью текста
public class Book {
    private String name;
    private String author;
    private String text;

    // Методы, связанные с данными книги
    public String replaceWordInText(String word, String replacement) {
        return text.replace(word, replacement);
    }

    // Нарушение: вывод в консоль — это отдельная ответственность
    public void printTextToConsole() {
        System.out.println(text);
    }
}
```

Класс `Book` имеет две причины для изменения: (1) изменение структуры/логики хранения данных книги; (2) изменение способа вывода текста.

**Исправление: разделение ответственностей.**

```java
// Ответственность 1: хранение данных книги
public class Book {
    private String name;
    private String author;
    private String text;

    public String getText() { return text; }
    public String replaceWordInText(String word, String replacement) {
        return text.replace(word, replacement);
    }
}

// Ответственность 2: печать / вывод текста
public class BookPrinter {
    public void printTextToConsole(String text) {
        System.out.println(text);
    }

    public void printTextToAnotherMedium(String text) {
        // Email, файл, лог и т.д.
    }
}
```

**Практические преимущества:**
- Меньше тест-кейсов для каждого класса.
- Меньше зависимостей — класс с узкой ответственностью реже требует сторонних импортов.
- Код проще искать, читать и понимать.
- Класс `BookPrinter` можно переиспользовать для вывода любого текста, а не только книжного.

**Частая ошибка при понимании SRP:** не следует доводить принцип до абсурда и создавать класс из одного метода. Ключевой вопрос — «сколько у этого класса несвязанных причин измениться?». Если причина одна — SRP соблюдён.

---

### Вопрос 2. В чём разница между принципом открытости/закрытости (OCP) и обычным наследованием? Почему «закрыт для изменений» не означает нельзя трогать файл?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Open/Closed Principle | Object Oriented Design](https://www.oodesign.com/open-closed-principle)

OCP требует, чтобы «программные сущности (классы, модули, функции) были открыты для расширения, но закрыты для модификации».

Нарушение принципа демонстрируется на примере класса `GraphicEditor`:

```java
class GraphicEditor {
    public void drawShape(Shape s) {
        if (s.m_type == 1)
            drawRectangle(s);
        else if (s.m_type == 2)
            drawCircle(s);
    }
}
```

При добавлении новой фигуры придётся менять уже проверенный `GraphicEditor`, что нарушает принцип.

Исправление через полиморфный OCP:

```java
class GraphicEditor {
    public void drawShape(Shape s) {
        s.draw(); // не нужно знать о конкретном типе
    }
}

abstract class Shape {
    abstract void draw();
}

class Rectangle extends Shape {
    public void draw() { /* рисуем прямоугольник */ }
}
```

Теперь для добавления фигуры `Triangle` достаточно создать новый класс `Triangle extends Shape` — `GraphicEditor` не трогаем. Однако авторы отмечают: «Создание гибкого дизайна требует дополнительного времени и усилий, поэтому принцип следует применять в тех областях, которые с наибольшей вероятностью будут меняться».

#### Ответ от Claude

**Определение OCP.**
Принцип открытости/закрытости (Бертран Мейер, 1988): программная сущность должна быть:
- **открыта для расширения** — можно добавлять новое поведение,
- **закрыта для модификации** — существующий, уже протестированный код не переписывается.

**OCP vs. обычное наследование — в чём разница?**

Обычное наследование — это языковой механизм: класс `B extends A` получает поля и методы `A`. Наследование само по себе не гарантирует соблюдение OCP и даже может его нарушать.

| Аспект | Обычное наследование | OCP |
|--------|---------------------|-----|
| Цель | Повторное использование кода | Защита существующего кода от изменений при добавлении нового поведения |
| Инструмент | Языковая конструкция `extends` | Архитектурный принцип; реализуется через абстрактные классы, интерфейсы, паттерны (Strategy, Decorator) |
| Направление зависимости | Подкласс зависит от суперкласса | Клиент зависит от абстракции; конкретики добавляются без изменения клиента |
| Нарушение OCP | Возможно: если добавление подкласса требует изменения суперкласса или клиентского кода | Нарушается, когда новый функционал достигается правкой существующих классов |

**Почему «закрыт для модификации» не значит «нельзя трогать файл»?**

«Закрыт для модификации» — это не буквальный запрет на редактирование файла. Смысл в следующем: при появлении **нового требования** не нужно переписывать уже работающий и протестированный код. Файл можно:
- исправлять при обнаружении **бага** в уже существующей логике,
- рефакторить ради улучшения читаемости без изменения поведения.

Нарушение OCP происходит тогда, когда **добавление новой функциональности** (нового типа фигуры, нового способа оплаты, нового формата отчёта) вынуждает идти и менять уже существующий класс.

**Два пути реализации OCP (по Дженкову):**
1. **Подклассирование (наследование полиморфное)** — новый класс расширяет абстрактный базовый класс.
2. **Подстановка зависимостей** — компонент принимает интерфейс, конкретная реализация инжектируется снаружи (Dependency Injection).

**Практический пример (интерфейс + стратегия):**

```java
// Интерфейс — абстракция, стабильный контракт
public interface DiscountPolicy {
    double apply(double price);
}

// Существующие реализации — не трогаем
public class NoDiscount implements DiscountPolicy {
    public double apply(double price) { return price; }
}

public class TenPercentDiscount implements DiscountPolicy {
    public double apply(double price) { return price * 0.9; }
}

// Добавляем новую политику без изменения OrderService
public class BlackFridayDiscount implements DiscountPolicy {
    public double apply(double price) { return price * 0.5; }
}

public class OrderService {
    private final DiscountPolicy policy;
    public OrderService(DiscountPolicy policy) { this.policy = policy; }
    public double calculateTotal(double price) { return policy.apply(price); }
}
```

`OrderService` закрыт для модификации — при добавлении `BlackFridayDiscount` его файл не трогают. При этом система открыта для расширения — новый класс `BlackFridayDiscount` добавляется свободно.

**Ключевой вывод:** OCP не запрещает менять файлы — он требует проектировать систему так, чтобы добавление нового функционала выражалось в написании новых классов, а не в правке старых.

---

### Вопрос 3. Что такое принцип подстановки Лисков (LSP)? Почему классический пример «квадрат наследует прямоугольник» нарушает LSP?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Liskov's Substitution Principle | Object Oriented Design](https://www.oodesign.com/liskov-s-substitution-principle)

«Производные типы должны быть полностью взаимозаменяемы со своими базовыми типами».

Нарушение через пример Rectangle / Square:

```java
class Rectangle {
    protected int m_width, m_height;

    public void setWidth(int width)   { m_width = width; }
    public void setHeight(int height) { m_height = height; }
    public int  getArea()             { return m_width * m_height; }
}

class Square extends Rectangle {
    // Квадрат вынужден поддерживать m_width == m_height
    public void setWidth(int width)   { m_width = m_height = width; }
    public void setHeight(int height) { m_width = m_height = height; }
}
```

Фабричный метод возвращает `Rectangle` (которым может оказаться `Square`). Если клиент делает:

```java
Rectangle r = factory.getRect(); // на самом деле Square
r.setWidth(5);
r.setHeight(10);
// Ожидается: 5 * 10 = 50
// Реально:   10 * 10 = 100 (Square сравнял стороны!)
```

Результат неожиданный: клиентский код, работающий с базовым типом `Rectangle`, получает неверный результат при подстановке `Square`.

Решение: использовать композицию или общий интерфейс `Shape`, который оба класса реализуют независимо, без наследования.

#### Ответ от Claude

**Определение LSP.**
Принцип подстановки Лисков (Барбара Лисков, 1987): «Если `S` — подтип `T`, то объекты типа `T` в программе можно заменить на объекты типа `S` без изменения корректности программы».

Упрощённо (по Дженкову): «Везде, где требуется экземпляр суперкласса `A`, должен работать и экземпляр подкласса `B` — без каких-либо сюрпризов».

**Почему «квадрат наследует прямоугольник» нарушает LSP?**

Математически квадрат — частный случай прямоугольника (все стороны равны). Интуиция подсказывает оформить это наследованием. Но в объектной модели это ломает поведенческий контракт:

*Инвариант прямоугольника:* ширина и высота независимы — установка одной не меняет другую.

```java
class Rectangle {
    protected int width, height;
    public void setWidth(int w)  { this.width  = w; }   // не трогает height
    public void setHeight(int h) { this.height = h; }   // не трогает width
    public int  getArea()        { return width * height; }
}
```

`Square` не может соблюсти этот инвариант: у квадрата стороны всегда равны, поэтому setWidth неизбежно меняет height:

```java
class Square extends Rectangle {
    @Override
    public void setWidth(int w)  { this.width = this.height = w; }
    @Override
    public void setHeight(int h) { this.width = this.height = h; }
}
```

Клиентский код, написанный под `Rectangle`, нарушается:

```java
void testArea(Rectangle r) {
    r.setWidth(5);
    r.setHeight(10);
    // Контракт Rectangle: площадь должна быть 5 * 10 = 50
    assert r.getArea() == 50; // ПАДАЕТ, если r — это Square (100)
}
```

При передаче `Square` вместо `Rectangle` утверждение `assert` не выполняется. LSP нарушен — подстановка ломает корректность программы.

**Правила «Проектирования по контракту» (Design by Contract), которые нарушает Square:**
- Предусловия подкласса не должны быть **строже** предусловий суперкласса.
- Постусловия подкласса не должны быть **слабее** постусловий суперкласса.
- **Инварианты** суперкласса должны соблюдаться в подклассе.

`Square` нарушает инвариант `Rectangle`: независимость ширины и высоты.

**Распространённые признаки нарушения LSP:**
1. Подкласс бросает `UnsupportedOperationException` из унаследованного метода.
2. Переопределённый метод делает что-то принципиально иное (меняет смысл, а не детали реализации).
3. Клиентский код вынужден проверять `instanceof`, чтобы обработать подкласс особым образом.

**Способы исправления:**

*Вариант 1 — Общий интерфейс без наследования:*

```java
public interface Shape {
    int getArea();
}

public class Rectangle implements Shape {
    private int width, height;
    public Rectangle(int w, int h) { this.width = w; this.height = h; }
    public int getArea() { return width * height; }
}

public class Square implements Shape {
    private int side;
    public Square(int side) { this.side = side; }
    public int getArea() { return side * side; }
}
```

Каждый класс реализует собственный контракт; ни один не нарушает инвариант другого.

*Вариант 2 — Неизменяемые объекты:*
Сделать `Rectangle` неизменяемым (immutable): запретить сеттеры, принимать размеры только через конструктор. Тогда `Square` может наследовать `Rectangle`, не нарушая контракта, потому что менять стороны после создания в принципе нельзя.

**Ключевой вывод:** LSP — это не о синтаксисе наследования, а о поведенческом контракте. Наследование оправдано только тогда, когда подкласс **расширяет** поведение суперкласса, не нарушая ни одного из его инвариантов и гарантий.
### Вопрос 4. Объясните принцип разделения интерфейсов (ISP). Что плохого в интерфейсе Worker с методами work(), eat(), sleep(), если роботы используют только work()?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Interface Segregation Principle — reflectoring.io](https://reflectoring.io/interface-segregation-principle/)

ISP гласит: «Клиенты не должны зависеть от интерфейсов, которые они не используют». Если интерфейс `Worker` содержит методы `work()`, `eat()` и `sleep()`, то класс `Robot`, реализующий этот интерфейс, вынужден предоставить реализации `eat()` и `sleep()`, даже если роботы не едят и не спят. Обычно это приводит к «заглушкам» вида `throw new UnsupportedOperationException(...)`, что вводит в заблуждение и нарушает контракт. Решение — разбить «толстый» интерфейс на узкоспециализированные: `Workable`, `Eatable`, `Sleepable`. Тогда `Robot` реализует только `Workable`, а `Human` — все три.

#### Ответ от Claude

**Определение.** Принцип разделения интерфейсов (Interface Segregation Principle, ISP) — четвёртый из принципов SOLID, сформулированный Робертом Мартином (Robert C. Martin) во время консалтинга в Xerox. Формулировка: *«Клиенты не должны зависеть от методов, которые они не используют»* (Wikipedia). Иными словами, вместо одного «жирного» интерфейса следует создавать несколько узких, клиентско-ориентированных.

**Что плохого в интерфейсе Worker с work(), eat(), sleep()?**

1. **Принудительная реализация бессмысленных методов.** Класс `Robot` вынужден реализовывать `eat()` и `sleep()`, хотя семантически роботы этого не делают. Единственный вариант — заглушка или `throw new UnsupportedOperationException()`.

2. **Нарушение контракта Liskov (LSP).** Если метод `eat()` выбрасывает исключение во время выполнения там, где ожидается нормальная работа, это нарушает принцип подстановки Лисков.

3. **Ненужная связанность.** Изменение сигнатуры `eat()` или `sleep()` потребует перекомпиляции и возможной правки `Robot`, хотя тот никогда не использует эти методы.

4. **Снижение читаемости.** Разработчик, смотрящий на `Robot implements Worker`, будет ожидать, что робот умеет есть и спать, — что вводит в заблуждение.

**Правильное решение — разбить интерфейс:**

```java
interface Workable {
    void work();
}

interface Eatable {
    void eat();
}

interface Sleepable {
    void sleep();
}

class Robot implements Workable {
    @Override
    public void work() { /* рабочая логика */ }
}

class HumanWorker implements Workable, Eatable, Sleepable {
    @Override public void work() { /* ... */ }
    @Override public void eat()  { /* ... */ }
    @Override public void sleep(){ /* ... */ }
}
```

**Связь с другими принципами.** Применение ISP автоматически поддерживает SRP: каждый «маленький» интерфейс несёт единственную ответственность. Соблюдение ISP также упрощает тестирование — количество методов для мокирования минимально.

**Исторический контекст.** Мартин обнаружил проблему в системе принтеров Xerox: единственный класс `Job` обслуживал все операции (печать, скрепление, факс), что приводило к часовым циклам перекомпиляции при любом изменении. Введение отдельных интерфейсов (`PrintJob`, `StapleJob` и т.д.) устранило ненужные зависимости.

---

### Вопрос 5. Что такое принцип инверсии зависимостей (DIP)? Чем он отличается от Dependency Injection, и является ли DI единственным способом реализовать DIP?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Dependency Injection vs Dependency Inversion Principle — TU Delft OCW](https://ocw.tudelft.nl/course-readings/4-4-4-dependency-injection-vs-dependency-inversion-principle/)

DIP — это принцип проектирования: высокоуровневые модули не должны зависеть от низкоуровневых; оба должны зависеть от абстракций. DI — это конкретная техника: объекты получают свои зависимости извне (через конструктор, сеттер или интерфейс), вместо того чтобы создавать их самостоятельно. DI помогает реализовать DIP, но это разные понятия: DIP описывает цель (развязка через абстракции), а DI — один из механизмов её достижения.

#### Ответ от Claude

**Принцип инверсии зависимостей (DIP)** — пятый из принципов SOLID, сформулированный Робертом Мартином. Он состоит из двух утверждений (Wikipedia):

1. *Высокоуровневые модули не должны импортировать ничего из низкоуровневых модулей. Оба должны зависеть от абстракций (например, от интерфейсов).*
2. *Абстракции не должны зависеть от деталей. Детали (конкретные реализации) должны зависеть от абстракций.*

**Пример нарушения DIP:**

```java
// Нарушение: высокоуровневый класс напрямую зависит от низкоуровневого
class OrderService {
    private MySQLOrderRepository repository = new MySQLOrderRepository(); // конкретика

    public void placeOrder(Order order) {
        repository.save(order);
    }
}
```

**Соблюдение DIP:**

```java
interface OrderRepository {
    void save(Order order);
}

class OrderService {
    private final OrderRepository repository; // зависимость от абстракции

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}

class MySQLOrderRepository implements OrderRepository {
    @Override
    public void save(Order order) { /* ... */ }
}
```

**Чем DIP отличается от Dependency Injection (DI)?**

| Аспект | DIP | DI |
|---|---|---|
| Что это | Принцип проектирования | Паттерн/техника реализации |
| Что описывает | Архитектурную цель: зависеть от абстракций | Механизм: передавать зависимости извне |
| Уровень | Концептуальный | Технический |

DIP — это «что строить» (система, в которой модули связаны через интерфейсы). DI — это «как строить» (один из способов передать нужную реализацию).

**Является ли DI единственным способом реализовать DIP?**

Нет. DI — наиболее популярный и удобный способ, но не единственный. Альтернативы (по Wikipedia и TU Delft):

- **Service Locator** — центральный реестр, из которого код запрашивает нужную реализацию по типу или имени.
- **Factory/Abstract Factory** — фабрика создаёт нужную реализацию, скрывая конкретный класс от вызывающей стороны.
- **Plugin-архитектура** — компоненты загружаются динамически (например, через `ServiceLoader` в Java).
- **Adapter-паттерн** — адаптер создаёт слой абстракции между компонентами.

Все перечисленные подходы соблюдают DIP, обеспечивая зависимость от абстракций, а не от конкретных реализаций. Spring Framework реализует DI через IoC-контейнер, что является самым распространённым практическим воплощением DIP в экосистеме Java.

---

### Вопрос 6. Объясните принципы DRY, KISS и YAGNI своими словами. Приведите по одному примеру нарушения каждого из них.

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Crafting Cleaner Java Code: Exploring DRY, KISS and YAGNI Principles — alxkm.github.io](https://alxkm.github.io/posts/dry_kiss_yagni/)

**DRY (Don't Repeat Yourself):** «Каждый фрагмент знания должен иметь единственное, однозначное, авторитетное представление в системе.» Пример нарушения — дублирование логики валидации email в методах `createUser()` и `updateUser()`. Решение — вынести в приватный метод `validateEmail()`.

**KISS (Keep It Simple, Stupid):** Предпочитай простые решения сложным. Пример нарушения — избыточная иерархия: интерфейс `DataProcessor` → абстрактный класс `AbstractDataProcessor` → конкретная реализация `SimpleProcessor` для элементарной задачи, решаемой одним классом.

**YAGNI (You Aren't Gonna Need It):** Не реализуй то, что пока не нужно. Пример нарушения — класс `OrderProcessor` с полями `Logger`, `MetricsCollector`, `CacheManager`, `NotificationService`, ни одно из которых реально не используется.

#### Ответ от Claude

**DRY — Don't Repeat Yourself («Не повторяйся»)**

Принцип введён Эндрю Хантом и Дэвидом Томасом в книге «The Pragmatic Programmer» (1999): *«Каждый фрагмент знания должен иметь единственное, однозначное, авторитетное представление в системе.»*

Суть: любая повторяющаяся логика должна быть вынесена в одно место. Нарушение DRY — не только copy-paste кода, но и дублирование бизнес-логики в разных слоях (например, одна и та же проверка в контроллере и в сервисе).

**Пример нарушения DRY в Java:**

```java
// Нарушение: логика валидации дублируется
public class UserService {
    public void createUser(String email) {
        if (email == null || email.isEmpty()) {
            throw new IllegalArgumentException("Email обязателен");
        }
        // создание пользователя
    }

    public void updateUser(String email) {
        if (email == null || email.isEmpty()) {  // точная копия
            throw new IllegalArgumentException("Email обязателен");
        }
        // обновление пользователя
    }
}

// Решение: единый метод validateEmail()
private void validateEmail(String email) {
    if (email == null || email.isEmpty()) {
        throw new IllegalArgumentException("Email обязателен");
    }
}
```

---

**KISS — Keep It Simple, Stupid («Делай проще»)**

Принцип разработан в ВМС США в 1960-х. Идея: большинство систем работают лучше, если они остаются простыми, а не усложняются. Сложность — враг понятности и сопровождаемости.

Важное уточнение: KISS не означает «пиши примитивный код». Он означает «не добавляй сложность там, где она не оправдана требованиями».

**Пример нарушения KISS в Java:**

```java
// Нарушение: избыточная абстракция для тривиальной задачи
public interface DataProcessor {
    void process();
}

public abstract class AbstractDataProcessor implements DataProcessor {
    protected abstract void validate();
    protected abstract void transform();
    protected abstract void persist();

    @Override
    public void process() {
        validate();
        transform();
        persist();
    }
}

public class SimpleReportProcessor extends AbstractDataProcessor {
    @Override protected void validate() { /* одна строка */ }
    @Override protected void transform() { /* одна строка */ }
    @Override protected void persist() { /* одна строка */ }
}

// Решение: простой класс без ненужной иерархии
public class ReportProcessor {
    public void process() {
        validate();
        transform();
        persist();
    }
    private void validate()  { /* ... */ }
    private void transform() { /* ... */ }
    private void persist()   { /* ... */ }
}
```

---

**YAGNI — You Aren't Gonna Need It («Тебе это не понадобится»)**

Принцип из методологии Extreme Programming (XP), сформулированный Роном Джеффрисом. Суть: не реализуй функциональность до тех пор, пока она действительно не нужна. Преждевременная реализация «про запас» увеличивает кодовую базу, усложняет поддержку и нередко оказывается невостребованной.

YAGNI не противоречит хорошей архитектуре — он против спекулятивной разработки фич, которые «возможно понадобятся».

**Пример нарушения YAGNI в Java:**

```java
// Нарушение: класс нагружен функциональностью, которой нет в требованиях
public class UserManager {
    public void createUser(String name) { /* реализовано и нужно */ }
    public void deleteUser(String id)   { /* реализовано и нужно */ }

    // Никто не просил — «может пригодится»:
    public void exportUsersToXML()      { /* 150 строк кода */ }
    public void syncWithCRM()           { /* 200 строк кода */ }
    public void generateActivityReport(){ /* 100 строк кода */ }
}

// Решение: только то, что нужно сейчас
public class UserManager {
    public void createUser(String name) { /* ... */ }
    public void deleteUser(String id)   { /* ... */ }
}
```

**Как три принципа соотносятся между собой:**

- **DRY** борется с дублированием знаний.
- **KISS** борется с излишней сложностью.
- **YAGNI** борется с излишней функциональностью.

Они дополняют, а не заменяют друг друга: код может быть без дублирования (DRY), но чрезмерно запутанным (нарушение KISS), или простым и без повторений, но перегруженным ненужными фичами (нарушение YAGNI).
### Вопрос 7. Что означает «высокая связность (high cohesion)» и «слабое зацепление (low coupling)»? Как они соотносятся с принципом SRP?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Single Responsibility Principle - Spring Framework Guru](https://springframework.guru/principles-of-object-oriented-design/single-responsibility-principle/)

**Связность (Cohesion)** — мера того, насколько тесно связаны сегменты кода внутри модуля (методы класса, классы пакета). Чем выше связность, тем лучше: «высокая связность подразумевает более простое сопровождение и отладку, большую функциональность и возможность повторного использования кода».

**Зацепление (Coupling)** — степень взаимозависимости между модулями. В статье отмечается: «слабое зацепление модулей связано с высокой связностью».

SRP напрямую поддерживает оба понятия. Ограничивая класс одной ответственностью, вы добиваетесь:
- **Высокой связности**: связанный функционал концентрируется в одном классе.
- **Слабого зацепления**: классы зависят от меньшего количества внешних концернов.

Пример из статьи — класс `Text`, нарушающий SRP смешением текстовых операций и вывода:

```java
// Нарушение SRP
class Text {
    void allLettersToUpperCase() { ... }
    void findSubTextAndDelete(String s) { ... }
    void printText() { ... }  // лишняя ответственность
}

// После рефакторинга — высокая связность, слабое зацепление
class Text {
    void allLettersToUpperCase() { ... }
    void findSubTextAndDelete(String s) { ... }
}

class Printer {
    void printText() { ... }
}
```

#### Ответ от Claude

**Определения**

- **Высокая связность (High Cohesion)** — все элементы класса (поля, методы) служат единой, чётко выраженной цели. Класс делает одну вещь хорошо. Метрика: если убрать любой метод, класс перестаёт выполнять свою задачу — значит, все методы на своём месте.

- **Слабое зацепление (Low Coupling)** — класс минимально зависит от деталей реализации других классов. Изменение в одном модуле не вызывает каскадных правок в других. Зацепление бывает нескольких видов: зацепление по данным (Content Coupling) — худшее, зацепление через интерфейс (Interface Coupling) — приемлемое.

**Связь с SRP**

SRP (Single Responsibility Principle) Роберта Мартина гласит: «Класс должен иметь только одну причину для изменения». Это определение является операциональным следствием двух метрик:

| Свойство | Без SRP | С SRP |
|---|---|---|
| Cohesion | Низкая: методы служат разным целям | Высокая: все методы — одна цель |
| Coupling | Высокое: один класс знает про DB, email, PDF | Низкое: каждый класс — одна зависимость |

**Важный нюанс**: Мартин определял «ответственность» не как «один метод» или «одна функция», а как **один актор** (один стейкхолдер, у которого есть причина просить об изменении). Например, бухгалтерия и IT-отдел — два разных актора, и их требования не должны менять один класс.

**Практическое правило обнаружения**:
- Если описание класса содержит союз «и» — скорее всего, нарушен SRP.
- Если при добавлении новой функциональности нужно менять класс, который уже работает — нарушено OCP и, возможно, SRP.

**Пример на Java**:

```java
// Плохо: низкая связность, высокое зацепление
class UserService {
    User findById(long id) { /* SQL */ }
    void sendWelcomeEmail(User user) { /* SMTP */ }
    String exportToCsv(List<User> users) { /* CSV */ }
}

// Хорошо: каждый класс — одна причина для изменения
class UserRepository {
    User findById(long id) { /* только SQL */ }
}

class UserEmailService {
    void sendWelcomeEmail(User user) { /* только SMTP */ }
}

class UserExportService {
    String exportToCsv(List<User> users) { /* только CSV */ }
}
```

Высокая связность и слабое зацепление — это **цель**, а SRP — **инструмент** её достижения на уровне отдельного класса.

---

### Вопрос 8. Назовите 3–5 известных «запахов кода» (code smells). Как вы их обнаруживаете в реальном коде?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Code Smells — Refactoring Guru](https://refactoring.guru/refactoring/smells)

Refactoring Guru классифицирует запахи кода по пяти категориям:

1. **Bloaters («Раздутые»)** — код, методы и классы, разросшиеся до гигантских размеров. Включают: Long Method, Large Class, Primitive Obsession, Long Parameter List, Data Clumps.

2. **Object-Orientation Abusers («Нарушители ООП»)** — неполное или неправильное применение принципов ООП: Switch Statements, Temporary Field, Refused Bequest, Alternative Classes with Different Interfaces.

3. **Change Preventers («Блокирующие изменения»)** — «если нужно изменить что-то в одном месте, приходится менять во многих других». Сюда входят Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies.

4. **Dispensables («Ненужное»)** — бесполезный код, удаление которого сделает код чище: Comments, Duplicate Code, Dead Code, Lazy Class, Data Class, Speculative Generality.

5. **Couplers («Цепляльщики»)** — избыточное зацепление между классами: Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man.

#### Ответ от Claude

Термин «code smell» ввёл Мартин Фаулер в книге «Refactoring: Improving the Design of Existing Code» (1999). Запах кода — не баг и не ошибка компиляции, а признак того, что структура кода нуждается в рефакторинге.

Ниже — пять наиболее распространённых запахов с примерами на Java и методами обнаружения.

---

**1. Long Method (Длинный метод)**

Метод, содержащий слишком много строк (эвристика Фаулера: больше 10 строк — повод задуматься). Признак: внутри метода нужны комментарии, объясняющие блоки кода.

```java
// Плохо: один метод делает всё
public void processOrder(Order order) {
    // валидация
    if (order.getItems().isEmpty()) throw new IllegalArgumentException();
    if (order.getCustomer() == null) throw new IllegalArgumentException();
    // расчёт скидки
    double discount = 0;
    if (order.getCustomer().isPremium()) discount = 0.1;
    if (order.getTotal() > 1000) discount += 0.05;
    // сохранение
    orderRepository.save(order);
    // отправка email
    emailService.send(order.getCustomer().getEmail(), "Order confirmed");
}

// Хорошо: Extract Method
public void processOrder(Order order) {
    validateOrder(order);
    applyDiscount(order);
    orderRepository.save(order);
    notifyCustomer(order);
}
```

*Обнаружение*: статический анализ (PMD-правило `ExcessiveMethodLength`), метрика цикломатической сложности в IntelliJ IDEA (Analyze → Calculate Metrics).

---

**2. God Class / Large Class (Класс-бог)**

Класс, взявший на себя слишком много ответственностей. Признаки: сотни строк кода, десятки полей, методы из совершенно разных доменов.

```java
// Плохо: UserManager делает всё
class UserManager {
    void createUser(...) { }
    void sendEmail(...) { }
    void generateReport(...) { }
    void updatePermissions(...) { }
    void exportToCsv(...) { }
    // ещё 30 методов...
}
```

*Обнаружение*: SonarQube (правило `ClassCouplingCheck`), MetricsReloaded в IntelliJ — смотрим на LCOM (Lack of Cohesion of Methods): значение близкое к 1 = God Class.

---

**3. Duplicate Code (Дублирование кода)**

Одинаковый или почти одинаковый код в двух и более местах. Это самый распространённый запах и самый дорогостоящий при поддержке: баг надо исправлять в нескольких местах.

```java
// Плохо: одна логика в двух классах
class OrderService {
    double calcTax(double amount) { return amount * 0.2; }
}
class InvoiceService {
    double calcTax(double amount) { return amount * 0.2; }
}

// Хорошо: Extract Method / Extract Class
class TaxCalculator {
    double calcTax(double amount) { return amount * 0.2; }
}
```

*Обнаружение*: PMD Copy-Paste Detector (CPD), IntelliJ IDEA — Analyze → Locate Duplicates.

---

**4. Feature Envy (Завидущие методы)**

Метод обращается к данным и методам другого класса чаще, чем к собственным. Это признак того, что метод находится не в том классе.

```java
// Плохо: OrderPrinter «завидует» Order
class OrderPrinter {
    void print(Order order) {
        System.out.println(order.getCustomer().getName());
        System.out.println(order.getTotal());
        System.out.println(order.getDiscount());
        System.out.println(order.getItems().size());
        // только чужие данные, ни одного своего поля
    }
}

// Хорошо: метод переносим в Order
class Order {
    void print() {
        System.out.println(this.customer.getName());
        // ...
    }
}
```

*Обнаружение*: Code review — ищем методы, у которых большинство вызовов идут через объект-параметр; IntelliJ IDEA подсвечивает это через Code Inspections.

---

**5. Primitive Obsession (Одержимость примитивами)**

Использование примитивных типов (`String`, `int`, `double`) вместо небольших объектов для представления доменных концепций.

```java
// Плохо: телефон — это просто строка
class Customer {
    private String phone; // "+79001234567" — никакой валидации
    private String email; // тоже строка
    private double price; // без валюты
}

// Хорошо: выделяем типы
class PhoneNumber {
    private final String value;
    public PhoneNumber(String value) {
        if (!value.matches("\\+\\d{11}")) throw new IllegalArgumentException();
        this.value = value;
    }
}

class Money {
    private final BigDecimal amount;
    private final Currency currency;
}
```

*Обнаружение*: ревью кода — ищем поля типа `String`/`int`/`double`, несущие семантику (деньги, email, телефон, координаты); SonarQube правило `ReplaceStringWithEnum`.

---

**Инструменты обнаружения запахов в реальном коде**:

| Инструмент | Что находит |
|---|---|
| IntelliJ IDEA Inspections | Long method, duplicate code, unused code |
| SonarQube / SonarLint | God Class, Feature Envy, Cyclomatic Complexity |
| PMD + CPD | Duplicate code, Long method, Switch statements |
| SpotBugs | Более низкоуровневые проблемы (null, ресурсы) |
| Checkstyle | Стилистические нарушения, длина методов/классов |

---

### Вопрос 9. У вас есть класс OrderService, который читает данные из БД, считает скидки, отправляет email и генерирует PDF-отчёт. Какие принципы SOLID нарушены и как это исправить?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Single Responsibility Principle in Java — nkamphoa.com](https://nkamphoa.com/single-responsibility-principle-in-java/)

Статья демонстрирует нарушение SRP на примере сервиса, совмещающего несколько независимых обязанностей. Ключевой тезис: «каждый из этих концернов может меняться независимо». Сервис, обрабатывающий заказы, обновляющий инвентарь и отправляющий уведомления, имеет несколько причин для изменения.

**До рефакторинга (нарушение):**
```java
class OrderService {
    void createOrder(...) { /* логика БД */ }
    void sendConfirmationEmail(...) { /* логика email */ }
    void updateInventory(...) { /* логика склада */ }
}
```

**После рефакторинга (соответствие SRP):**
```java
class OrderProcessor { /* только бизнес-логика */ }
class InventoryUpdater { /* только управление складом */ }
class NotificationService { /* только email/уведомления */ }

class OrderService {
    void createOrder(...) {
        processor.process(...);
        inventory.update(...);
        mailer.send(...);
    }
}
```

Преимущества: изолированное тестирование, гибкость изменений — замена провайдера email или добавление PDF не требует модификации `OrderService`.

#### Ответ от Claude

**Анализ исходного класса**

```java
// Антипаттерн: всё в одном классе
class OrderService {
    // 1. Читает данные из БД
    public Order findById(long id) {
        Connection conn = DriverManager.getConnection("jdbc:mysql://...");
        // ...
    }
    // 2. Считает скидки
    public double calculateDiscount(Order order) {
        if (order.getTotal() > 1000) return 0.1;
        if (order.getCustomer().isPremium()) return 0.15;
        return 0;
    }
    // 3. Отправляет email
    public void sendConfirmationEmail(Order order) {
        Properties props = new Properties();
        Session session = Session.getDefaultInstance(props);
        // ...
    }
    // 4. Генерирует PDF
    public byte[] generatePdfReport(Order order) {
        Document doc = new Document();
        // ...
    }
}
```

---

**Нарушенные принципы SOLID**

**S — Single Responsibility Principle (нарушен)**

У класса четыре причины для изменения:
- Меняется структура БД — меняем `OrderService`.
- Меняется бизнес-правило скидок — меняем `OrderService`.
- Меняется шаблон email — меняем `OrderService`.
- Меняется формат PDF — меняем `OrderService`.

Это классический пример God Class с низкой связностью внутри.

**D — Dependency Inversion Principle (нарушен)**

Класс напрямую создаёт (`new`) или получает конкретные реализации (`DriverManager.getConnection`, `Session.getDefaultInstance`). Он зависит от низкоуровневых модулей вместо абстракций. Это делает невозможным мок-тестирование и затрудняет замену реализаций.

**O — Open/Closed Principle (нарушен косвенно)**

Если добавить новый способ скидки или новый тип уведомления (SMS вместо email), придётся менять существующий класс вместо расширения через новую реализацию. Нарушение OCP — следствие нарушения SRP.

*(Принципы L и I в данном примере явно не затронуты, так как это класс, а не иерархия интерфейсов.)*

---

**Как исправить: декомпозиция по ответственностям**

**Шаг 1: Выделить слой доступа к данным**

```java
// Абстракция (DIP)
public interface OrderRepository {
    Order findById(long id);
    void save(Order order);
}

// Конкретная реализация (зависит от конкретной БД)
public class JpaOrderRepository implements OrderRepository {
    private final EntityManager em;
    public Order findById(long id) { return em.find(Order.class, id); }
    public void save(Order order) { em.persist(order); }
}
```

**Шаг 2: Выделить бизнес-логику скидок**

```java
public interface DiscountStrategy {
    double calculate(Order order);
}

public class VolumeDiscountStrategy implements DiscountStrategy {
    public double calculate(Order order) {
        return order.getTotal() > 1000 ? 0.1 : 0.0;
    }
}

public class PremiumCustomerDiscountStrategy implements DiscountStrategy {
    public double calculate(Order order) {
        return order.getCustomer().isPremium() ? 0.15 : 0.0;
    }
}
```

**Шаг 3: Выделить уведомления**

```java
public interface NotificationService {
    void notify(Order order);
}

public class EmailNotificationService implements NotificationService {
    private final MailSender mailSender;
    public void notify(Order order) {
        mailSender.send(order.getCustomer().getEmail(), buildMessage(order));
    }
}
```

**Шаг 4: Выделить генерацию PDF**

```java
public interface ReportService {
    byte[] generateReport(Order order);
}

public class PdfReportService implements ReportService {
    public byte[] generateReport(Order order) { /* только PDF */ }
}
```

**Шаг 5: Тонкий оркестрирующий OrderService**

```java
// Теперь OrderService — только оркестратор (одна причина изменения:
// изменение бизнес-процесса обработки заказа)
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final List<DiscountStrategy> discountStrategies;
    private final NotificationService notificationService;
    private final ReportService reportService;

    // Внедрение через конструктор (DIP)
    public OrderService(OrderRepository orderRepository,
                        List<DiscountStrategy> discountStrategies,
                        NotificationService notificationService,
                        ReportService reportService) {
        this.orderRepository = orderRepository;
        this.discountStrategies = discountStrategies;
        this.notificationService = notificationService;
        this.reportService = reportService;
    }

    public Order processOrder(long orderId) {
        Order order = orderRepository.findById(orderId);
        double discount = discountStrategies.stream()
            .mapToDouble(s -> s.calculate(order))
            .sum();
        order.applyDiscount(discount);
        orderRepository.save(order);
        notificationService.notify(order);
        return order;
    }

    public byte[] getOrderReport(long orderId) {
        return reportService.generateReport(orderRepository.findById(orderId));
    }
}
```

---

**Итоговая таблица нарушений и исправлений**

| Нарушение | Принцип | Исправление |
|---|---|---|
| Один класс: БД + скидки + email + PDF | SRP | Разделить на `OrderRepository`, `DiscountStrategy`, `NotificationService`, `ReportService` |
| Прямая зависимость от конкретных реализаций (`DriverManager`, `Session`) | DIP | Зависеть от интерфейсов, внедрять через конструктор |
| Добавление нового правила скидки требует изменения класса | OCP | Стратегии скидок как отдельные реализации `DiscountStrategy` |

**Бонус: тестируемость после рефакторинга**

```java
@Test
void processOrder_appliesPremiumDiscount() {
    // Можно мокать любую зависимость
    OrderRepository repo = mock(OrderRepository.class);
    when(repo.findById(1L)).thenReturn(premiumOrder());

    NotificationService notif = mock(NotificationService.class);
    ReportService report = mock(ReportService.class);

    OrderService service = new OrderService(repo,
        List.of(new PremiumCustomerDiscountStrategy()),
        notif, report);

    Order result = service.processOrder(1L);
    assertEquals(0.15, result.getDiscount());
    verify(notif).notify(result);
}
```

После рефакторинга каждый класс можно тестировать изолированно, менять реализацию (например, заменить email на Kafka-событие) без изменения `OrderService`, а новые правила скидок добавлять без правки существующего кода.
### Вопрос 10. Чем отличается рефакторинг от переписывания кода? Когда рефакторинг необходим, а когда лучше не трогать работающий код?

**Категория:** SOLID/чистый код · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [What Refactoring Is and What It Isn't According to Kent Beck and Martin Fowler](https://dzone.com/articles/what-refactoring-and-what-it-0)

Рефакторинг — это «изменение внутренней структуры программного обеспечения с целью облегчить понимание и удешевить модификацию без изменения наблюдаемого поведения» (определение Фаулера и Бека). Практика предполагает небольшие безопасные шаги с запуском тестов после каждого изменения, чтобы убедиться, что поведение осталось прежним.

Рефакторингом **не являются**: исправление ошибок, оптимизация производительности, улучшение обработки ошибок, полное переписывание или перепроектирование. Ключевой принцип: «Вы не решаете заниматься рефакторингом — вы рефакторите, потому что хотите сделать что-то другое, и рефакторинг помогает это сделать». Рефакторинг должен быть встроен в повседневную разработку, а не выделяться в отдельный проект.

Не следует трогать код, который вы не изменяете и не готовитесь изменить. Масштабные архитектурные перепроектирования — даже если они технически сохраняют бизнес-логику — являются переписыванием, а не рефакторингом. Они требуют явного выделения времени и несут значительный технический риск, в отличие от непрерывного, малорискового характера настоящего рефакторинга.

#### Ответ от Claude

**Рефакторинг** — это дисциплинированная техника изменения внутренней структуры кода *без изменения его внешнего (наблюдаемого) поведения*. Мартин Фаулер определяет его как серию небольших, сохраняющих поведение трансформаций. Каждая трансформация сама по себе незначительна, но их последовательность может привести к существенной реструктуризации.

**Переписывание** — замена кода более существенным образом: изменение API, высокоуровневой структуры или полного подхода к решению задачи. Переписывание — это не рефакторинг.

**Отличия по ключевым признакам:**

| Признак | Рефакторинг | Переписывание |
|---|---|---|
| Внешнее поведение | Не изменяется | Может изменяться |
| Размер шага | Маленький, инкрементальный | Большой |
| Тесты | Проходят на каждом шаге | Могут потребовать обновления |
| Риск | Низкий | Высокий |
| Цель | Улучшить структуру для дальнейших изменений | Создать новое решение |

**Когда рефакторинг необходим:**
- Перед добавлением новой функциональности — чтобы код легче поддавался расширению (preparatory refactoring по Фаулеру).
- При обнаружении «запахов кода» (code smells): дублирование, слишком длинные методы, глубокая вложенность, неочевидные имена.
- Когда нужно углубить понимание кода — рефакторинг как инструмент изучения.
- После написания тестов — чтобы улучшить дизайн при наличии страховочной сети.

**Когда лучше не трогать работающий код:**
- Если код стабильно работает в продакшене и вы не планируете его менять или расширять в ближайшее время — изменения несут риск без пользы.
- Если отсутствует тестовое покрытие — рефакторинг без тестов опасен: нет способа убедиться, что поведение сохранено.
- Если код — опубликованный API (библиотека, публичный контракт) — изменение внутренней структуры может сломать клиентов.
- Если вы работаете в режиме жёстких дедлайнов и нет бизнес-обоснования — Фаулер подчёркивает: рефакторинг оправдан экономически только тогда, когда он позволяет быстрее поставлять функциональность.

**Компромиссный подход** (по Фаулеру): если крупный модуль требует переосмысления, разбейте систему на компоненты с чёткой инкапсуляцией, а затем принимайте решение «рефакторинг vs переписывание» для каждого компонента отдельно.

**Ключевое правило-мнемоника**: код должен работать корректно *до* начала рефакторинга. Если код сломан — сначала чините баг, потом рефакторите.

---

### Вопрос 11. Есть абстрактный класс Bird с методом fly(). Класс Penguin extends Bird и бросает UnsupportedOperationException в fly(). Какой принцип нарушен и как правильно спроектировать иерархию?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Liskov Substitution Principle in Java with Example](https://www.javaguides.net/2018/02/liskov-substitution-principle.html)

Класс Penguin нарушает принцип подстановки Лисков (LSP), потому что «изменяет поведение метода fly, выбрасывая исключение». Это нарушает ключевое правило: «объекты суперкласса должны быть заменяемы объектами подкласса без влияния на корректность программы».

Проблемный код:
```java
class Bird {
    public void fly() {
        System.out.println("Bird is flying");
    }
}

class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Penguins can't fly");
    }
}
```

Правильное решение — реструктурировать иерархию так, чтобы класс Bird не содержал метод fly(), а поведение полёта было вынесено отдельно:

```java
abstract class Bird {
    public abstract void eat();
}

class Sparrow extends Bird {
    public void eat() { /* ... */ }
    public void fly() { /* ... */ }
}

class Penguin extends Bird {
    public void eat() { /* ... */ }
    public void swim() { /* ... */ }
}
```

Это гарантирует, что каждый подкласс реализует только те поведения, которыми реально обладает, позволяя подстановку без неожиданных ошибок времени выполнения.

#### Ответ от Claude

**Нарушенный принцип — LSP (принцип подстановки Лисков, буква L в SOLID).**

Формулировка Барбары Лисков (1987): «Если S является подтипом T, то объекты типа T в программе могут быть заменены объектами типа S без изменения каких-либо желательных свойств этой программы».

Практическое следствие: подкласс не должен ужесточать предусловия, ослаблять постусловия или бросать новые исключения, которых нет в контракте суперкласса.

**Почему это нарушение LSP:**

```java
// Проблемный код
abstract class Bird {
    public abstract void fly();
}

class Sparrow extends Bird {
    @Override
    public void fly() {
        System.out.println("Sparrow is flying");
    }
}

class Penguin extends Bird {
    @Override
    public void fly() {
        // Нарушение LSP: контракт Bird обещает умение летать,
        // Penguin ломает этот контракт через исключение
        throw new UnsupportedOperationException("Penguins can't fly");
    }
}

// Клиентский код ломается при подстановке Penguin вместо Bird:
void makeBirdFly(Bird bird) {
    bird.fly(); // UnsupportedOperationException для Penguin!
}
```

Нарушение LSP здесь проявляется сразу в двух аспектах:
1. Метод бросает непредусмотренное контрактом исключение.
2. Метод не выполняет заявленное поведение («полёт»).

**Правильное проектирование иерархии — вариант 1 (интерфейс Flyable):**

```java
// Базовый класс содержит только общее для всех птиц поведение
abstract class Bird {
    public abstract void eat();
    public abstract void makeSound();
}

// Отдельный интерфейс для умения летать
interface Flyable {
    void fly();
}

// Летающие птицы реализуют Flyable
class Sparrow extends Bird implements Flyable {
    @Override
    public void eat() { System.out.println("Sparrow eating"); }
    @Override
    public void makeSound() { System.out.println("Tweet"); }
    @Override
    public void fly() { System.out.println("Sparrow flying"); }
}

// Пингвин — птица, но не Flyable
class Penguin extends Bird {
    @Override
    public void eat() { System.out.println("Penguin eating fish"); }
    @Override
    public void makeSound() { System.out.println("Squawk"); }
    public void swim() { System.out.println("Penguin swimming"); }
}
```

**Вариант 2 (разделение иерархии):**

```java
abstract class Bird { /* общие методы */ }
abstract class FlyingBird extends Bird {
    public abstract void fly();
}
abstract class FlightlessBird extends Bird { }

class Eagle extends FlyingBird {
    @Override public void fly() { /* ... */ }
}

class Penguin extends FlightlessBird {
    public void swim() { /* ... */ }
}
```

**Практическое правило (из Tom Dalling):** если переопределённый метод ничего не делает или бросает исключение — это сигнал нарушения LSP. Нарушение LSP автоматически ведёт к нарушению OCP: клиентский код вынужден добавлять проверки типа `instanceof`, чтобы обработать «сломанные» подклассы.

**Итог:** Bird не должен содержать метод fly() в базовом классе, если не все птицы умеют летать. Способность летать выносится в отдельный интерфейс (Flyable) или промежуточный абстрактный класс (FlyingBird). Penguin extends Bird, но не реализует Flyable — это честный и правильный контракт.

---

### Вопрос 12. Как принцип OCP реализуется через паттерн «Стратегия»? Приведите пример: есть метод calculateDiscount с цепочкой if/else для разных типов клиентов — как его переписать.

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Strategy Design Pattern in Java with Examples](https://www.codekatha.com/2026/02/strategy-design-pattern-java-example.html)

Проблемный код без паттерна Стратегия нарушает OCP из-за большой условной логики:

```java
class DiscountService {
    public double calculateDiscount(String type, double price) {
        if (type.equals("FESTIVAL")) {
            return price * 0.20;
        } else if (type.equals("NEWUSER")) {
            return price * 0.10;
        } else if (type.equals("PREMIUM")) {
            return price * 0.30;
        }
        return 0;
    }
}
```

Недостатки: большая условная логика, сложно добавлять новые типы скидок, нарушение OCP, сложно тестировать.

Решение через паттерн Стратегия:

```java
// Интерфейс стратегии
interface DiscountStrategy {
    double applyDiscount(double price);
}

// Конкретные реализации
class FestivalDiscount implements DiscountStrategy {
    public double applyDiscount(double price) { return price * 0.20; }
}
class PremiumUserDiscount implements DiscountStrategy {
    public double applyDiscount(double price) { return price * 0.30; }
}

// Контекст
class PriceCalculator {
    private DiscountStrategy discountStrategy;
    public PriceCalculator(DiscountStrategy discountStrategy) {
        this.discountStrategy = discountStrategy;
    }
    public double calculateFinalPrice(double price) {
        return price - discountStrategy.applyDiscount(price);
    }
}
```

Такой подход позволяет «изменять поведение динамически без изменения существующего кода» и поддерживает расширяемость.

#### Ответ от Claude

**OCP (принцип открытости/закрытости):** программные сущности должны быть открыты для расширения, но закрыты для модификации. Новая функциональность добавляется через расширение (новый класс/реализация), а не через правку существующего кода.

**Проблема — код, нарушающий OCP:**

```java
// Каждый новый тип клиента = правка этого метода = нарушение OCP
public class DiscountCalculator {
    public double calculateDiscount(String customerType, double price) {
        if ("REGULAR".equals(customerType)) {
            return price * 0.05;
        } else if ("PREMIUM".equals(customerType)) {
            return price * 0.15;
        } else if ("VIP".equals(customerType)) {
            return price * 0.30;
        } else if ("NEWUSER".equals(customerType)) {
            return price * 0.10;
        }
        return 0.0;
    }
}
```

Проблемы этого кода:
- Добавление нового типа клиента требует редактирования класса `DiscountCalculator`.
- Нарушается принцип единственной ответственности (SRP): класс знает о всех типах клиентов.
- Сложно тестировать изолированно каждую стратегию.
- Велик риск регрессии при изменении.

**Решение через паттерн «Стратегия»:**

```java
// 1. Интерфейс стратегии — контракт для всех алгоритмов скидки
public interface DiscountStrategy {
    double calculate(double price);
}

// 2. Конкретные стратегии — каждый тип клиента = отдельный класс
public class RegularCustomerDiscount implements DiscountStrategy {
    @Override
    public double calculate(double price) {
        return price * 0.05;
    }
}

public class PremiumCustomerDiscount implements DiscountStrategy {
    @Override
    public double calculate(double price) {
        return price * 0.15;
    }
}

public class VipCustomerDiscount implements DiscountStrategy {
    @Override
    public double calculate(double price) {
        return price * 0.30;
    }
}

// Новый тип — просто новый класс, без правки существующих:
public class NewUserDiscount implements DiscountStrategy {
    @Override
    public double calculate(double price) {
        return price * 0.10;
    }
}

// 3. Контекст — использует стратегию через интерфейс
public class DiscountCalculator {
    private final DiscountStrategy strategy;

    // Стратегия внедряется через конструктор (или сеттер)
    public DiscountCalculator(DiscountStrategy strategy) {
        this.strategy = strategy;
    }

    public double calculateFinalPrice(double price) {
        double discount = strategy.calculate(price);
        return price - discount;
    }
}

// 4. Использование
DiscountCalculator calc = new DiscountCalculator(new VipCustomerDiscount());
double finalPrice = calc.calculateFinalPrice(1000.0); // 700.0
```

**Как именно реализуется OCP:**

- **Закрыт для модификации:** класс `DiscountCalculator` и существующие стратегии не меняются при добавлении нового типа клиента.
- **Открыт для расширения:** чтобы поддержать новый тип клиента (например, корпоративный), достаточно создать `CorporateDiscount implements DiscountStrategy` — и всё.

**Выбор стратегии в реальном приложении** часто выносится в фабрику или Map:

```java
public class DiscountStrategyFactory {
    private static final Map<String, DiscountStrategy> strategies = Map.of(
        "REGULAR", new RegularCustomerDiscount(),
        "PREMIUM", new PremiumCustomerDiscount(),
        "VIP",     new VipCustomerDiscount(),
        "NEWUSER", new NewUserDiscount()
    );

    public static DiscountStrategy getStrategy(String customerType) {
        return strategies.getOrDefault(customerType, price -> 0.0);
    }
}

// Использование:
DiscountStrategy strategy = DiscountStrategyFactory.getStrategy(customerType);
DiscountCalculator calc = new DiscountCalculator(strategy);
```

**Связь OCP и паттерна Стратегия** (по DZone): «Все классы стратегий реализуют конкретный интерфейс стратегии. Контекстный класс привязан не к конкретным классам стратегий, а к интерфейсу стратегии. Это и есть реализация OCP: контекст инкапсулирует стратегию, которая может быть подставлена разными способами без изменения контекста».

**Итог:** паттерн «Стратегия» — это один из самых прямых способов выразить OCP в коде: интерфейс фиксирует контракт (закрытость), а новые классы-реализации обеспечивают расширяемость без модификации существующего кода.
### Вопрос 13. Что такое «God Object» и чем он опасен? Как постепенно разбить его без остановки разработки?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [How to refactor the God object class antipattern | TheServerSide](https://www.theserverside.com/tip/How-to-refactor-the-God-object-antipattern)

God Object — это единственный класс, нарушающий принцип единственной ответственности: он выполняет множество несвязанных задач, объявляет несвязанные поля и содержит «коллекцию методов, не имеющих логической связи друг с другом». Такой антипаттерн обычно появляется, когда разработчики отдают приоритет скорости в ущерб правильному проектированию.

Предлагается пятишаговый подход к рефакторингу:
1. **Сначала покрыть тестами** — создать исчерпывающий набор юнит-тестов, чтобы рефакторить уверенно, не ломая функциональность.
2. **Определить зависимости клиентов** — выяснить, какие компоненты наиболее активно вызывают методы God Object, чтобы расставить приоритеты и найти естественные границы декомпозиции.
3. **Вынести статические методы** — переместить статические методы в утилитные классы, оставив инстансный код для дальнейшего рефакторинга.
4. **Сгруппировать связанные методы** — реорганизовать оставшиеся поля и методы в сфокусированные объекты, используя наследование, агрегацию и ассоциацию при сохранении слабой связанности.
5. **Удалить или заменить** — удалить исходный God Object или превратить его в фасад, делегирующий вновь созданным небольшим объектам; пометить методы как deprecated.

#### Ответ от Claude

**Что такое God Object**

God Object (также «God Class») — антипаттерн, при котором один класс знает слишком много и делает слишком много. Он нарушает принцип единственной ответственности (SRP): вместо одной чёткой задачи такой класс охватывает бизнес-логику, работу с БД, форматирование, отправку уведомлений и прочее — всё в одном файле. Типичные признаки: тысячи строк кода, десятки полей без видимой связи, методы вроде `processEverything()`, `handleAll()`, высокая цикломатическая сложность.

**Чем он опасен**

- **Высокая связанность** — любое изменение рискует затронуть несвязанные части системы; баги в God Object влияют на множество подсистем.
- **Сложность тестирования** — для тестирования одного метода нужно мокировать десятки зависимостей.
- **Узкое место команды** — весь код сосредоточен в одном файле, что порождает постоянные merge-конфликты.
- **Трудность понимания** — новый разработчик не может понять, за что отвечает класс, без длительного изучения.
- **Блокировка роста** — система становится хрупкой: чем больше функций добавляется в God Object, тем дороже каждая последующая правка.
- **Нарушение инкапсуляции** — класс часто вынужден знать детали реализации других компонентов.

**Как разбивать постепенно без остановки разработки**

Ключевой принцип — incremental strangling (постепенное «удушение»): не переписывать с нуля, а методично вытаскивать ответственности по одной.

1. **Покрыть тестами перед началом** — без надёжного test suite рефакторинг God Object слишком рискован. Минимально необходимо: интеграционные тесты на публичный API класса.

2. **Определить зоны ответственности** — проанализировать класс и выделить логические группы методов и полей (например: «работа с заказами», «отправка email», «расчёт скидок»). Инструменты статического анализа (SonarQube, IntelliJ IDEA) помогают выявить cohesion-метрики.

3. **Вынести статические утилиты** — статические методы без состояния переносятся в утилитные классы первыми: это безопасно и не меняет поведение.

4. **Extract Class по одной ответственности за итерацию** — вырезать одну ответственность в новый класс, внедрить его через зависимость (DI), оставив в God Object делегирующий вызов. Фиче-разработка продолжается параллельно.

5. **Превратить God Object в Facade** — на переходном этапе God Object становится фасадом, делегируя работу новым классам. Это сохраняет обратную совместимость для клиентского кода.

6. **Постепенно deprecate** — помечать методы God Object как `@Deprecated`, направляя клиентов к новым классам. После перехода всех клиентов — удалить.

7. **Использовать feature flags** — для крупных изменений новую декомпозированную реализацию можно скрыть за флагом и переключать постепенно.

**Паттерны, помогающие при рефакторинге:** Facade, Strategy, Observer, Composite. Рефакторинги Мартина Фаулера: *Extract Class*, *Move Method*, *Move Field*, *Extract Method*.

---

### Вопрос 14. Объясните разницу между Feature Envy и Inappropriate Intimacy как code smells. Какие техники рефакторинга применяются для каждого?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Feature Envy | Refactoring.Guru](https://refactoring.guru/smells/feature-envy)

**Feature Envy** — запах кода, при котором метод обращается к данным другого объекта чаще, чем к собственным данным. Это часто возникает после рефакторинга, когда поля переносятся в отдельный data-класс, а связанные операции остаются на прежнем месте.

Основной принцип устранения: держать данные и функции, работающие с ними, в одном месте — они обычно изменяются вместе.

Техники рефакторинга:
- **Move Method** — если метод явно принадлежит другому месту, перенести его целиком в подходящий класс.
- **Extract Method** — если только часть метода обращается к данным другого объекта, вынести эту часть, затем переместить.
- Если метод использует данные нескольких классов — определить, данные какого класса используются больше всего, и поместить метод туда; либо разбить метод на части по каждому классу через Extract Method.

**Inappropriate Intimacy** (источник: [refactoring.guru/smells/inappropriate-intimacy](https://refactoring.guru/smells/inappropriate-intimacy)) — запах, при котором один класс использует внутренние поля и методы другого класса. Классы «знают» слишком много о внутреннем устройстве друг друга; хорошие классы должны знать о других как можно меньше.

Техники рефакторинга:
- **Move Method / Move Field** — переместить методы или поля в тот класс, где они реально используются.
- **Extract Class + Hide Delegate** — формализовать отношение, выделив общую функциональность в отдельный класс и скрыв делегирование за интерфейсом.
- **Change Bidirectional Association to Unidirectional** — если классы взаимозависимы, перевести в одностороннюю зависимость.
- **Replace Delegation with Inheritance** — когда интимность существует между подклассом и суперклассом.

#### Ответ от Claude

**Ключевое различие между запахами**

Оба запаха относятся к категории «связывателей» (Couplers) и описывают избыточную связь между классами, но природа этой связи разная:

| Критерий | Feature Envy | Inappropriate Intimacy |
|---|---|---|
| Направление | Односторонняя: метод класса A чрезмерно обращается к классу B | Двусторонняя или: класс A знает приватные детали класса B |
| Что нарушается | Принцип размещения логики рядом с данными | Принцип инкапсуляции |
| Уровень доступа | Использует публичный API чужого класса | Обращается к приватным/protected полям и методам |
| Симптом | Метод «завидует» данным соседа | Классы «слишком близки» — знают детали реализации друг друга |

**Feature Envy — подробнее**

Признак: метод содержит длинные цепочки вида `order.getCustomer().getAddress().getCity()`, активно вызывает геттеры чужого объекта, но почти не работает со своими полями.

Причина: чаще всего — результат разделения данных и логики при рефакторинге. Например, поля вынесены в `CustomerData`, а методы расчёта остались в `OrderService`.

Техники рефакторинга:
- **Move Method** — перенести метод целиком туда, чьи данные он использует.
- **Extract Method + Move Method** — если только часть метода «завидует», сначала выделить её, затем переместить.
- Если метод использует несколько классов — применить **Extract Method** для каждой части и переместить каждую к своим данным.

Исключение: паттерны Strategy и Visitor намеренно нарушают это правило — они должны работать с данными разных объектов.

**Inappropriate Intimacy — подробнее**

Признак: класс напрямую читает или модифицирует приватные поля другого класса (через рефлексию, package-private доступ или нарушение инкапсуляции); двустороннее навигационное отношение там, где достаточно одностороннего.

Причина: отсутствие чётких границ модулей, разрастание связей в legacy-коде, «удобные» временные решения, которые закрепились.

Техники рефакторинга:
- **Move Method / Move Field** — переместить то, что реально принадлежит другому классу.
- **Extract Class** — если оба класса тянутся к общей ответственности, вынести её в третий класс.
- **Hide Delegate** — скрыть прямой доступ к внутренностям за методами-делегатами.
- **Change Bidirectional Association to Unidirectional** — убрать ссылку в одну из сторон, использовав lookup или DI.
- **Replace Delegation with Inheritance** — когда подкласс слишком зависит от суперкласса через делегирование.

**Практическое правило для различения:** если метод просто «много вызывает» публичные методы другого класса — это Feature Envy (логика не там, где данные). Если класс знает о том, что скрыто за публичным API, — это Inappropriate Intimacy (нарушена инкапсуляция).

---

### Вопрос 15. Когда строгое следование OCP может привести к избыточной абстракции (over-engineering)? Как найти баланс?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Open-Closed Principle: Smart Use, No Overkill | ByteCrafted](https://bytecrafted.dev/series/solid/open-closed-principle-without-overengineering/)

Статья выделяет несколько сценариев, когда применение OCP создаёт излишнюю сложность:

**Преждевременная абстракция** — «сделать каждую строку настраиваемой» или «создавать интерфейсы для DTO» — примеры абстракции ради абстракции. Расширяемость не стоит строить раньше, чем она действительно нужна.

**Проблема таймирования** — вместо того чтобы вводить абстракции с самого начала, рекомендуется подход «жди второго случая»: не создавать интерфейсы, пока не появятся минимум две различающиеся реализации.

Три практических стратегии для поиска баланса:
1. **Следи за сигналами изменений** — если файл регулярно меняется по схожим причинам, это сигнал о реальной необходимости точки расширения.
2. **Правило трёх** — «когда видишь один и тот же паттерн трижды — тогда стоит вводить абстракцию». Это предотвращает over-engineering, не упуская настоящего повторения.
3. **Знай, где не применять OCP** — для базовых преобразований данных, настроек, задаваемых один раз, и кода, который редко меняется.

Главная идея: OCP — инструмент для управления неизбежными изменениями, а не универсальный мандат. Реальное мастерство — понять, где гибкость действительно важна, а где создаёт лишнюю нагрузку на поддержку.

#### Ответ от Claude

**Суть OCP и откуда берётся over-engineering**

Open/Closed Principle (Бертран Мейер, 1988; переосмыслен Робертом Мартином через полиморфизм) гласит: программные сущности должны быть открыты для расширения, но закрыты для модификации. Идея правильная: изолируй то, что меняется, от того, что стабильно. Проблема возникает, когда разработчик пытается сделать «закрытым» всё подряд — заранее, без реальных требований на расширение.

**Когда строгое следование OCP приводит к over-engineering**

1. **«Interface explosion»** — создание интерфейса для каждого класса, даже когда существует и будет существовать только одна реализация. Например, `UserService` + `UserServiceImpl` без какой-либо второй реализации — это OCP «на всякий случай», который только добавляет слои без пользы.

2. **Абстракция для YAGNI-сценариев** — добавление Strategy, Plugin или extensibility points для требований, которые «возможно понадобятся». Если это изменение не запланировано — интерфейс будет угадываться, а угаданные интерфейсы обычно неверны.

3. **Глубокие иерархии наследования ради расширяемости** — классический пример из Java EE: AbstractBeanFactoryAwareAdvisorAutoProxyCreator. Пять уровней наследования ради одного метода — наследие чрезмерного OCP.

4. **Generic-абстракции, сложные в понимании** — когда абстракция настолько обобщённая (`Processor<T, R, C>` с тремя параметрами типа), что её назначение непонятно без контекста.

5. **Преждевременная параметризация конфигурации** — вынесение в extension points того, что меняется раз в год при деплое, а не при добавлении новой функции.

**Как найти баланс**

*Правило трёх (Rule of Three, Фаулер/Мартин):* первый раз — пиши конкретно; второй раз — замечай повторение; третий раз — рефактори в абстракцию. Не вводи OCP-точку расширения до второго реального случая использования.

*Принцип «OCP как вектор, не цель»:* Применяй OCP там, где изменения уже происходили или где требование на расширение явно задокументировано. Не строй шлюзы, которые никто не будет проходить.

*Практические вопросы перед введением абстракции:*
- Есть ли сейчас две разные реализации, или только одна предполагаемая?
- Изменялся ли этот код несколько раз по схожей причине?
- Усложнит ли абстракция onboarding нового разработчика?
- Есть ли требование в backlog или это мой прогноз?

*Сочетать OCP с другими принципами:*
- SRP подсказывает правильные границы — сначала выдели ответственности, потом думай о расширяемости.
- ISP помогает не создавать «жирные» интерфейсы с методами на все случаи.
- DIP обеспечивает инверсию зависимостей без лишних уровней наследования.

*Когда OCP применять обязательно:*
- Код публичной библиотеки / API: пользователи не могут менять ваш код, только расширять.
- Места, которые изменялись 3+ раз по одному типу причины.
- Интеграционные точки со сторонними системами (провайдеры платежей, каналы уведомлений).

*Когда можно обойтись без OCP:*
- Внутренний код с единственной командой — рефакторинг доступен всегда.
- DTO, value objects, конфигурационные классы.
- Функции без состояния и без предполагаемого полиморфизма.

**Итог:** OCP ценен там, где расширяемость — реальная потребность, а не предположение. Сигнал к введению точки расширения — повторяющееся изменение по одной причине, а не абстрактный страх будущих правок.
### Вопрос 16. Как принцип DIP улучшает тестируемость кода? Покажите на примере: класс UserService напрямую создаёт new UserRepository() — что поменяется после применения DIP?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [SOLID — Dependency Inversion Principle (Part 5) by Matthias Schenk | Medium](https://medium.com/@inzuael/solid-dependency-inversion-principle-part-5-f5bec43ab22e)

DIP гласит: модули высокого уровня не должны зависеть от модулей низкого уровня; оба должны зависеть от абстракций. До применения принципа `UserService` напрямую создаёт конкретный репозиторий:

```kotlin
class UserService {
    private val userRepository: ConcreteUserRepository = ConcreteUserRepository()
}
```

Поскольку репозиторий инстанциируется внутри класса, тестировать `UserService` можно только вместе с реальной реализацией — то есть с реальной базой данных. После применения DIP `UserService` зависит от интерфейса `UserRepository`, который передаётся через конструктор:

```kotlin
class UserService(private val userRepository: UserRepository) {
    fun authenticateUser(username: String, password: String): Boolean {
        val existingUser = userRepository.findUserBy(username)
        // ...
    }
}
```

В тесте подставляется фейковая реализация — без базы данных:

```kotlin
class FakeUserRepository : UserRepository {
    override fun findUserBy(username: String): User? = User(username)
}

class UserServiceTest {
    val userService = UserService(FakeUserRepository())
    // быстрые, изолированные юнит-тесты
}
```

Это делает тесты быстрее и предсказуемее: исчезает риск отказа внешних компонентов (база недоступна, нарушения ограничений).

#### Ответ от Claude

**Суть проблемы до DIP**

Когда `UserService` делает `new UserRepository()` внутри себя, между классами возникает жёсткая связь (tight coupling). Это означает:

1. Невозможно подменить `UserRepository` без изменения `UserService`.
2. Любой юнит-тест `UserService` автоматически тянет реальную базу данных — тест превращается в интеграционный.
3. Изменение конкретного репозитория (например, смена драйвера БД) вынуждает трогать высокоуровневый код сервиса.

**Было (нарушение DIP):**

```java
public class UserService {
    // UserService сам создаёт зависимость — высокий уровень зависит от низкого
    private final UserRepository userRepository = new UserRepository();

    public User findById(long id) {
        return userRepository.findById(id);
    }
}
```

**Шаг 1 — вводим абстракцию:**

```java
public interface UserRepository {
    User findById(long id);
    void save(User user);
}

public class JpaUserRepository implements UserRepository {
    @Override
    public User findById(long id) { /* работа с БД */ }

    @Override
    public void save(User user) { /* работа с БД */ }
}
```

**Шаг 2 — инжектируем зависимость через конструктор:**

```java
public class UserService {
    // Зависимость от абстракции, не от конкретики
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User findById(long id) {
        return userRepository.findById(id);
    }
}
```

**Что меняется в тестах:**

```java
// Тест до DIP: нельзя, нужна реальная БД
// Тест после DIP: подставляем mock или stub
class UserServiceTest {
    @Test
    void findById_returnsUser() {
        UserRepository mockRepo = Mockito.mock(UserRepository.class);
        Mockito.when(mockRepo.findById(1L)).thenReturn(new User(1L, "Alice"));

        UserService service = new UserService(mockRepo);
        User user = service.findById(1L);

        assertEquals("Alice", user.getName());
        // Никакой БД, никакого Spring-контекста — чистый юнит-тест
    }
}
```

**Что конкретно улучшается:**

| Аспект | До DIP | После DIP |
|---|---|---|
| Скорость тестов | Медленно (I/O к БД) | Быстро (всё в памяти) |
| Изоляция | Нет (интеграционный тест) | Полная (юнит-тест) |
| Надёжность | Зависит от состояния БД | Детерминировано |
| Замена реализации | Требует правки UserService | Только новый класс |

В экосистеме Spring DIP реализуется автоматически через `@Autowired`/`@Inject`: Spring сам создаёт конкретную реализацию и подставляет её, а `UserService` остаётся неизменным при любой смене репозитория.

---

### Вопрос 17. Что такое Shotgun Surgery и Divergent Change как code smells? Чем они противоположны друг другу и как связаны с SRP?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Shotgun Surgery | refactoring.guru](https://refactoring.guru/smells/shotgun-surgery)

**Shotgun Surgery** — это запах кода, при котором одно изменение логики приходится вносить сразу в несколько классов одновременно. Если одно небольшое изменение требует правок в множестве разных мест, то риск что-то пропустить и допустить ошибку существенно возрастает.

Это противоположность **Divergent Change**: при Divergent Change вы вносите много несвязанных правок в один и тот же класс; при Shotgun Surgery одно изменение разбросано по многим классам.

Лечение — консолидация: перенести поведение в один класс с помощью Move Method и Move Field (или создать новый класс), а опустевшие после этого классы убрать через Inline Class.

#### Ответ от Claude

**Divergent Change**

Divergent Change — «расходящиеся изменения»: один класс приходится менять по нескольким несвязанным причинам. Например, класс `OrderProcessor` хранит логику валидации, расчёта скидок и отправки уведомлений. Когда меняется правило валидации — редактируем `OrderProcessor`. Когда меняется формат уведомлений — снова редактируем `OrderProcessor`. Разные причины изменений сосредоточены в одном месте.

```
До:  OrderProcessor {
         validateOrder()     // меняется по причине A
         calculateDiscount() // меняется по причине B
         sendNotification()  // меняется по причине C
     }
```

**Shotgun Surgery**

Shotgun Surgery — «хирургия дробовиком»: одно логическое изменение приходится вносить в несколько классов одновременно. Например, формат даты захардкожен в `OrderService`, `ReportService`, `EmailService` и `AuditService`. Смена формата требует правки во всех четырёх.

```
До:  OrderService.formatDate()   // меняется
     ReportService.formatDate()  // меняется
     EmailService.formatDate()   // меняется
     AuditService.formatDate()   // меняется
     — все по одной и той же причине
```

**Противоположность запахов**

| Свойство | Divergent Change | Shotgun Surgery |
|---|---|---|
| Структура | 1 класс, N причин изменения | 1 причина изменения, N классов |
| Нарушение | Слишком много ответственностей в классе | Ответственность раздроблена по классам |
| Проблема | Нарушена целостность класса | Нарушена локализация изменений |
| Источник | Недостаточное деление | Избыточное дробление |

Интересно, что Shotgun Surgery нередко возникает как результат чрезмерно агрессивного лечения Divergent Change: разбивая класс «до атомов», разработчик рассеивает связанное поведение по нескольким классам.

**Связь с SRP**

Оба запаха — это симптомы нарушения принципа единственной ответственности, но с разных сторон:

- **Divergent Change** = у класса слишком много ответственностей (SRP нарушен явно: класс меняется по нескольким несвязанным причинам).
- **Shotgun Surgery** = одна ответственность размазана по нескольким классам (SRP нарушен неявно: ни один класс не «владеет» этой ответственностью полностью).

SRP требует идеального баланса: каждый класс — одна причина изменения, каждая причина изменения — один класс. Любое отклонение в одну сторону ведёт к Divergent Change, в другую — к Shotgun Surgery.

**Рефакторинг**

- *Divergent Change* лечится через **Extract Class**: выделяем каждую ответственность в отдельный класс.
- *Shotgun Surgery* лечится через **Move Method / Move Field**: собираем разбросанное поведение в один класс; затем применяем **Inline Class** к опустевшим «осколкам».

---

### Вопрос 18. Как применить Extract Method, Extract Class и Move Method при рефакторинге длинного метода (Long Method)? В каком порядке и по каким критериям?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Long Method | refactoring.guru](https://refactoring.guru/smells/long-method)

Любой метод длиннее десяти строк должен вызывать вопросы. Код постепенно накапливается в методах, но никогда из них не удаляется — как в «Отеле Калифорния». Разработчику психологически проще дописать строку в существующий метод, чем создать новый.

Главное лечение — **Extract Method**: если вы чувствуете необходимость прокомментировать что-то внутри метода, вынесите этот код в новый метод и дайте ему имя, объясняющее назначение. Даже однострочный код стоит выделить в метод, если он нуждается в пояснении.

Когда Extract Method мешают локальные переменные и параметры, используют вспомогательные приёмы: Replace Temp with Query, Introduce Parameter Object, Preserve Whole Object. Если метод всё равно не поддаётся извлечению — применяют Replace Method with Method Object: метод целиком переносится в отдельный объект, где все локальные переменные становятся полями.

Условные выражения и циклы — хорошие кандидаты для выделения: применяют Decompose Conditional и Extract Method к телу цикла.

#### Ответ от Claude

**Что такое Long Method и почему это проблема**

Long Method — метод, содержащий слишком много строк. Чем длиннее метод, тем сложнее понять его назначение, сложнее тестировать отдельные части и сложнее переиспользовать логику. Неформальный ориентир: метод длиннее 20–30 строк или требующий пояснительных комментариев — кандидат на рефакторинг.

**Три инструмента и критерии их применения**

**1. Extract Method** — первый и основной инструмент

*Когда:* фрагмент кода внутри метода делает одну логически завершённую вещь (валидация, форматирование, вычисление, работа с одной коллекцией). Хороший признак — место, где хочется написать комментарий.

*Критерий выбора имени:* имя нового метода должно описывать «что» (намерение), а не «как» (реализацию). `validateAge()` лучше, чем `checkIfAgeGreaterThanZero()`.

*Как:* выделяем фрагмент, определяем входные (параметры) и выходные (возвращаемое значение или изменяемые поля) данные, создаём метод.

```java
// До
public void processOrder(Order order) {
    // валидация
    if (order.getAmount() <= 0) throw new IllegalArgumentException("...");
    if (order.getCustomer() == null) throw new IllegalArgumentException("...");
    // расчёт скидки
    double discount = 0;
    if (order.getCustomer().isPremium()) discount = 0.1;
    if (order.getAmount() > 1000) discount += 0.05;
    // сохранение
    order.setFinalAmount(order.getAmount() * (1 - discount));
    orderRepository.save(order);
}

// После Extract Method
public void processOrder(Order order) {
    validateOrder(order);
    double discount = calculateDiscount(order);
    applyAndSave(order, discount);
}

private void validateOrder(Order order) { ... }
private double calculateDiscount(Order order) { ... }
private void applyAndSave(Order order, double discount) { ... }
```

**2. Extract Class** — второй шаг, когда выделенных методов становится много

*Когда применять:* несколько выделенных методов работают с одним и тем же подмножеством данных и концептуально образуют отдельную ответственность. Например, все методы расчёта скидок работают с полями `customerType`, `orderAmount`, `promoCode` — это признак, что нужен класс `DiscountCalculator`.

*Критерий:* если группа методов и полей имеет единое смысловое имя — их стоит вынести в класс.

```java
// После Extract Class
public class DiscountCalculator {
    public double calculate(Order order) {
        double discount = 0;
        if (order.getCustomer().isPremium()) discount = 0.1;
        if (order.getAmount() > 1000) discount += 0.05;
        return discount;
    }
}

public class OrderService {
    private final DiscountCalculator discountCalculator;

    public void processOrder(Order order) {
        validateOrder(order);
        double discount = discountCalculator.calculate(order);
        applyAndSave(order, discount);
    }
}
```

**3. Move Method** — третий шаг, исправляем Feature Envy

*Когда применять:* выделенный метод больше работает с данными другого класса, чем со своим собственным. Это запах Feature Envy — метод «завидует» чужим данным.

*Критерий:* если метод `A.foo()` вызывает несколько методов или полей объекта `B`, он, вероятно, принадлежит классу `B`.

```java
// До: OrderService.calculateDiscount() обращается к полям Customer
private double calculateDiscount(Order order) {
    Customer c = order.getCustomer();
    if (c.getMembershipYears() > 5 && c.getTotalPurchases() > 10000) {
        return 0.15;
    }
    return 0.05;
}

// После Move Method: логика переехала в Customer
public class Customer {
    public double getDiscountRate() {
        if (membershipYears > 5 && totalPurchases > 10000) return 0.15;
        return 0.05;
    }
}
```

**Рекомендуемый порядок**

```
1. Extract Method
   — разбиваем длинный метод на небольшие именованные части
   — цель: каждый метод делает одно дело

2. Extract Class
   — группируем связанные методы и поля в отдельный класс
   — применяем, когда видим несколько методов с общей тематикой
   — используем Move Field для данных, которые идут вместе с методами

3. Move Method
   — исправляем Feature Envy: перемещаем методы туда,
     где находятся нужные им данные
   — начинаем с приватных методов, чтобы минимизировать
     количество ошибок компиляции при переносе
```

**Практический принцип:** после каждого шага запускаем тесты. Рефакторинг без тестов — хождение по минному полю. Если тестов нет, сначала пишем характеризующие тесты (characterization tests), фиксирующие текущее поведение, и только потом рефакторим.
### Вопрос 19. Может ли нарушение LSP приводить к ошибкам только в runtime, а не в compile time? Приведите конкретный Java-пример с коллекциями или дженериками.

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [9 out of 10 developers miss this subtle violation of the Liskov Substitution Principle in Java's unmodifiable collections](https://medium.com/@pantiru.cosmin4rolletechnology/9-out-of-10-developers-are-not-aware-of-this-liskov-substituion-principle-violation-65ccb6385f1f)

LSP-нарушение с unmodifiable-коллекциями в Java является классическим примером ошибки времени выполнения. Когда разработчик оборачивает список через `Collections.unmodifiableList()`, результат реализует интерфейс `List`, у которого объявлен метод `add()`. Компилятор не видит проблемы — код проходит type-checking. Но при попытке вызвать `add()` или `remove()` в runtime выбрасывается `UnsupportedOperationException`. Это нарушает LSP: разработчик ожидает, что любая реализация `List` поддерживает операции, заявленные контрактом интерфейса. Unmodifiable-список подменяет поведение без предупреждения на этапе компиляции.

```java
List<String> modifiableList = new ArrayList<>();
modifiableList.add("Item1");

List<String> unmodifiableList = Collections.unmodifiableList(modifiableList);
unmodifiableList.add("Item2"); // компилируется, но бросает UnsupportedOperationException в runtime
```

#### Ответ от Claude

**Да, нарушение LSP может быть исключительно runtime-проблемой.**

LSP формулируется как: объект подтипа должен быть подставляем вместо объекта супертипа без изменения корректности программы. Java-компилятор проверяет только структурную совместимость типов (наличие методов с нужными сигнатурами), но не поведенческие контракты. Именно поэтому LSP-нарушения часто "проскальзывают" на этап выполнения.

**Пример 1: `Collections.unmodifiableList` и `Collections.singletonList`**

```java
List<String> list = Collections.unmodifiableList(new ArrayList<>(List.of("a", "b")));
// Компилируется без ошибок — List<String> объявляет add()
list.add("c"); // UnsupportedOperationException в runtime
```

`Collections.unmodifiableList` возвращает объект типа `Collections$UnmodifiableList`, который реализует `List<E>`, но переопределяет все мутирующие методы (`add`, `remove`, `set`, `clear`) так, что они бросают `UnsupportedOperationException`. Это нарушение поведенческого postcondition: клиент, работающий с `List`, ожидает, что коллекция изменяема.

**Пример 2: `Arrays.asList` — фиксированный размер**

```java
List<String> fixed = Arrays.asList("x", "y", "z");
fixed.add("w");    // UnsupportedOperationException — изменение размера запрещено
fixed.set(0, "X"); // OK — замена элемента разрешена

// Но если передать в метод, ожидающий полноценный List:
void process(List<String> items) {
    items.add("extra"); // взрывается в runtime, если пришёл Arrays.asList
}
process(fixed); // компилируется, падает в runtime
```

`Arrays.asList` возвращает внутренний класс `Arrays$ArrayList`, который НЕ поддерживает структурную модификацию (add/remove), но поддерживает `set`. Это частичное нарушение LSP.

**Пример 3: ковариантность массивов (классический)**

```java
String[] strings = {"hello"};
Object[] objects = strings; // компилируется — массивы ковариантны в Java
objects[0] = 42;            // ArrayStoreException в runtime
```

Java-массивы ковариантны (`String[] extends Object[]`), что позволяет компилятору пропустить присваивание, но JVM проверяет фактический тип элемента при записи.

**Почему компилятор не поможет**

Java реализует инвариантность обобщённых типов (`List<String>` не является подтипом `List<Object>`), что защищает от многих LSP-нарушений через дженерики. Однако поведенческие контракты интерфейсов (что метод не бросит исключение, что он действительно изменит коллекцию) компилятор не может верифицировать — они описаны только в Javadoc и концептуально.

**Вывод:** LSP-нарушение — это семантическое нарушение контракта, а не синтаксическое. Компилятор Java гарантирует сигнатурную совместимость, но не поведенческую. Все примеры выше компилируются успешно и падают только при исполнении.

---

### Вопрос 20. Как принципы SOLID соотносятся с микросервисной архитектурой? Можно ли говорить о SRP и ISP на уровне сервисов, а не классов?

**Категория:** SOLID/чистый код · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [microservices are solid | ArchConf (Matt Stine)](https://archconf.com/blog/matt_stine/2014/06/microservices_are_solid_1)

Автор утверждает, что микросервисная архитектура является прямым воплощением SOLID-принципов на уровне сервисов. SRP на уровне сервиса — это разбиение монолита по границам бизнес-возможностей (bounded contexts из DDD). Каждый микросервис реализует одну бизнес-возможность, владеет собственным сегментом данных и экспонирует его через API. Это разделяет циклы изменений и снижает риск при деплое.

ISP на уровне сервисов: монолитные архитектуры не могут соблюдать ISP, поскольку добавление функциональности для одной группы клиентов требует передеплоя всего приложения для всех. Хорошо спроектированные микросервисы принудительно применяют ISP через жёсткие границы: каждый независимо развёртываемый сервис экспонирует только свой специфический интерфейс, API сервиса становится механизмом принудительного соблюдения принципа.

#### Ответ от Claude

**Да — SOLID применимо на уровне сервисов, это не метафора, а точная аналогия.**

Суть перехода: те же проблемы проектирования, что в ООП решаются на уровне классов и модулей, в распределённых системах воспроизводятся на уровне сервисов. Изменился масштаб, но не природа задач.

**SRP на уровне сервисов**

"Один актор — одна причина для изменения" в контексте сервисов означает: сервис изменяется по запросу одного бизнес-домена или одной команды. Признаки нарушения SRP на уровне сервиса:
- несколько команд вносят изменения в один сервис
- API сервиса естественно разделяется на несвязанные концептуальные группы
- сервис обслуживает принципиально разные типы клиентов (например, пользователей и администраторов)
- внутри сервиса есть изолированные модули с плотными внутренними связями и слабыми внешними

DDD-ориентир: сервис должен быть не меньше агрегата и не больше ограниченного контекста (bounded context).

```
// Нарушение SRP на уровне сервиса:
UserService:
  - registerUser()
  - sendWelcomeEmail()
  - writeAuditLog()
  - generateReport()

// Исправление:
UserRegistrationService  — регистрация пользователей
UserNotificationService  — email-уведомления
UserAuditService         — аудит действий
```

**ISP на уровне сервисов**

"Клиент не должен зависеть от интерфейсов, которые он не использует" в контексте микросервисов означает: API сервиса не должен содержать методов, нерелевантных для конкретного потребителя.

Паттерны реализации:
- **BFF (Backend For Frontend)**: отдельный сервис-фасад для каждого типа клиента (мобильный, веб, партнёрский API)
- **API Gateway с маршрутизацией**: клиент получает только тот срез API, который ему нужен
- Разделение интерфейсов по consumer-ролям: `AdminOrderAPI` и `CustomerOrderAPI` вместо единого `OrderAPI`

**Остальные принципы SOLID на уровне сервисов**

| Принцип | Проявление на уровне сервисов |
|---------|-------------------------------|
| OCP | Новая функциональность — новый сервис, а не правка существующего |
| LSP | Совместимость версий API: v2 должна принимать запросы, написанные для v1 |
| DIP | Сервисы зависят от абстракций (контрактов API, message-схем), а не от конкретных реализаций друг друга |

**Ограничения аналогии**

SOLID сформулирован для ООП и описывает отношения между классами в рамках одного процесса. В распределённых системах возникают дополнительные измерения: сетевые сбои, eventual consistency, независимое версионирование. Поэтому ряд авторов предлагает расширенный набор принципов для микросервисов (IDEALS: Interface, Deployability, Event-driven, Availability over consistency, Loose coupling, Single responsibility).

**Вывод:** SRP и ISP применимы на уровне сервисов буквально, а не метафорически. SRP задаёт границы сервиса по принципу единого актора изменений, ISP требует сегментации API по типам потребителей. Это не "похоже на SOLID" — это тот же принцип, применённый к более крупной единице декомпозиции.

---

