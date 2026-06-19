# SOLID, чистый код и рефакторинг

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по SOLID и чистому коду →](../interview-questions/solid-clean-code-01.md)
> **Связанные области:** [[10-design-patterns]], [[19-testing]]

## Что это и зачем

Принципы проектирования и культура написания поддерживаемого кода. SOLID — пять принципов
объектно-ориентированного дизайна, снижающих связанность и повышающих гибкость. Сюда же относятся
DRY, KISS, YAGNI, code smells и техники рефакторинга. Это то, что отличает Middle/Senior:
способность писать код, который легко читать, тестировать и изменять.

Все эти принципы решают одну корневую проблему — **технический долг**: накопленная хаотичность
кода замедляет разработку экспоненциально. Рефакторинг (термин систематизировал Мартин Фаулер)
— это процесс улучшения внутренней структуры кода **без изменения его внешнего поведения**.
Цель: сделать код очевидным для других программистов, без дублирования, с минимальным количеством
движущихся частей, покрытым тестами и удобным для сопровождения.

---

## Ключевые подтемы

### SOLID: пять принципов объектно-ориентированного дизайна

Принципы сформулированы Робертом Мартином («Uncle Bob») и описаны в его книге
«Clean Architecture» (2017) и статьях начала 2000-х.

---

#### SRP — Single Responsibility Principle (Принцип единственной ответственности)

**Определение:** У класса должна быть только одна причина для изменения.

Иными словами, каждый класс решает ровно одну задачу. Если класс изменяется по двум разным
причинам (например, изменилась бизнес-логика И изменился способ уведомления), значит, у него
две ответственности.

**Нарушение:**
```java
public class Employee {
    public String getDesignation(int employeeId) { ... }
    public void updateSalary(int employeeId) { ... }
    public void sendMail() { ... }  // не относится к сущности Employee
}
```

**Исправление:**
```java
public class Employee {
    public String getDesignation(int employeeId) { ... }
    public void updateSalary(int employeeId) { ... }
}

public class NotificationService {
    public void sendMail(Employee employee) { ... }
}
```

**Что даёт:** меньше тест-кейсов на класс, меньше зависимостей, проще навигация по коду.

---

#### OCP — Open/Closed Principle (Принцип открытости/закрытости)

**Определение:** Программные сущности должны быть **открыты для расширения**, но **закрыты для
изменения**.

Новая функциональность добавляется через создание новых классов/реализаций, а не через правку
существующего кода. Достигается через зависимость от абстракций (интерфейсов, абстрактных
классов).

**Нарушение:**
```java
public class AreaCalculator {
    public double area(Shape shape) {
        if (shape instanceof Square) {
            // площадь квадрата
        } else if (shape instanceof Circle) {
            // площадь круга
        }
        // при добавлении Triangle нужно менять этот метод
        return area;
    }
}
```

**Исправление:**
```java
public interface Shape {
    double area();
}

public class Square implements Shape {
    private double side;
    @Override
    public double area() { return side * side; }
}

public class Circle implements Shape {
    private double radius;
    @Override
    public double area() { return Math.PI * radius * radius; }
}

// Новая фигура добавляется без изменения AreaCalculator
public class Triangle implements Shape {
    ...
    @Override
    public double area() { ... }
}
```

---

#### LSP — Liskov Substitution Principle (Принцип подстановки Лисков)

**Определение:** Объекты подкласса должны полностью заменять объекты базового класса, не нарушая
корректности программы. Формально: если `S` — подтип `T`, то объекты типа `T` можно заменить
объектами типа `S` без изменения желаемых свойств программы.

**Классическое нарушение (прямоугольник/квадрат):**
```java
class Rectangle {
    protected int width, height;
    public void setWidth(int w)  { this.width = w; }
    public void setHeight(int h) { this.height = h; }
    public int area() { return width * height; }
}

class Square extends Rectangle {
    @Override
    public void setWidth(int w)  { this.width = w; this.height = w; }
    @Override
    public void setHeight(int h) { this.width = h; this.height = h; }
}

// Нарушение LSP:
Rectangle r = new Square();
r.setWidth(5);
r.setHeight(3);
// ожидаем area() == 15, получаем 9
```

**Признаки нарушения LSP:**
- Подкласс выбрасывает `UnsupportedOperationException` для методов родителя.
- Подкласс ужесточает предусловия или ослабляет постусловия контракта.
- Код клиента делает `instanceof`-проверки, чтобы по-разному обработать подтипы.

**Исправление:** перестроить иерархию так, чтобы подтипы действительно являлись разновидностями
базового типа:
```java
abstract class Bird { ... }

abstract class FlyingBird extends Bird {
    public abstract void fly();
}

abstract class NonFlyingBird extends Bird { ... }

class Eagle extends FlyingBird {
    @Override public void fly() { ... }
}

class Ostrich extends NonFlyingBird { ... }
```

---

#### ISP — Interface Segregation Principle (Принцип разделения интерфейсов)

**Определение:** Клиенты не должны зависеть от методов, которые они не используют. Лучше много
маленьких специализированных интерфейсов, чем один «толстый».

**Нарушение:**
```java
interface IShapeCalculator {
    double calculateArea();
    double calculateVolume();  // плоская фигура не имеет объёма
}

class Square implements IShapeCalculator {
    @Override public double calculateArea() { ... }
    @Override public double calculateVolume() { return 0; }  // мусорная реализация
}
```

**Исправление:**
```java
interface IAreaCalculator {
    double calculateArea();
}

interface IVolumeCalculator {
    double calculateVolume();
}

class Square implements IAreaCalculator {
    @Override public double calculateArea() { ... }
}

class Cube implements IAreaCalculator, IVolumeCalculator {
    @Override public double calculateArea() { ... }
    @Override public double calculateVolume() { ... }
}
```

**Связь с LSP:** нарушения ISP часто провоцируют нарушения LSP (пустые/бросающие исключение
реализации).

---

#### DIP — Dependency Inversion Principle (Принцип инверсии зависимостей)

**Определение:**
1. Модули верхнего уровня не должны зависеть от модулей нижнего уровня. Оба должны зависеть от
   абстракций.
2. Абстракции не должны зависеть от деталей. Детали должны зависеть от абстракций.

**Нарушение:**
```java
public class Employee {
    private EmailNotification emailNotification = new EmailNotification(); // конкретная реализация
    public void notifyUser() {
        emailNotification.notify();
    }
}
```

**Исправление:**
```java
public interface Notification {
    void notify();
}

public class Employee {
    private final Notification notification;

    public Employee(Notification notification) {  // внедрение зависимости
        this.notification = notification;
    }

    public void notifyUser() {
        notification.notify();
    }
}

public class EmailNotification implements Notification {
    @Override public void notify() { ... }
}

public class SmsNotification implements Notification {
    @Override public void notify() { ... }
}

// Использование:
Notification n = new EmailNotification();
Employee e = new Employee(n);
```

DIP — фундамент для **Dependency Injection (DI)** и IoC-контейнеров (Spring, CDI). Класс
`Employee` теперь можно тестировать с mock-объектом `Notification` без реальной почты.

---

### DRY, KISS, YAGNI — вспомогательные принципы

| Принцип | Расшифровка | Суть |
|---------|-------------|------|
| **DRY** | Don't Repeat Yourself | Каждая часть знания должна иметь единственное, авторитетное представление в системе. Дублирование — это не только копирование кода, но и дублирование логики в разных формах. |
| **KISS** | Keep It Simple, Stupid | Простые решения предпочтительнее сложных. Не добавляй сложность без необходимости. |
| **YAGNI** | You Ain't Gonna Need It | Реализуй функциональность, только когда она действительно нужна, а не когда предполагаешь, что она понадобится. Принцип из Extreme Programming. |

**DRY:** при изменении бизнес-правила достаточно исправить одно место — риск ошибок снижается.
Дублирование не ограничивается copy-paste: одна логика, реализованная в двух разных классах, тоже
нарушение DRY.

**YAGNI** снижает overengineering: не нужно строить систему плагинов, если сейчас есть только
один тип обработчика.

**Принцип наименьшего удивления (Principle of Least Astonishment):** поведение кода должно
соответствовать интуитивным ожиданиям. Метод `getUser()` не должен удалять пользователя.

---

### Связанность (coupling) и связность (cohesion)

Две фундаментальные метрики качества модульного дизайна.

| Метрика | Желаемое значение | Описание |
|---------|--------------------|----------|
| **Cohesion (связность)** | Высокая | Насколько сильно связаны элементы внутри модуля/класса. Высокая — все методы работают с одними данными ради одной цели. |
| **Coupling (связанность)** | Низкая | Степень зависимости между модулями. Низкая — изменение в одном модуле не ломает другие. |

**Виды связанности (от плохой к лучшей):**
- *Content coupling* — один модуль напрямую изменяет данные другого.
- *Common coupling* — несколько модулей используют глобальные данные.
- *Control coupling* — один модуль управляет потоком выполнения другого флагом.
- *Data coupling* — модули общаются только через параметры. Наилучший вид.

**Связь с SOLID:** SRP обеспечивает высокую cohesion; DIP и ISP снижают coupling.

---

### Code smells — признаки проблемного кода

Термин ввёл Кент Бек, популяризировал Мартин Фаулер в книге «Refactoring».

#### Bloaters (раздутый код)

| Запах | Описание |
|-------|----------|
| **Long Method** | Метод длиннее 10–15 строк — сигнал к декомпозиции. |
| **Large Class** | Класс накопил слишком много полей и методов, нарушает SRP. |
| **Primitive Obsession** | Использование примитивов вместо маленьких объектов (например, `String` вместо `Email`, `int` вместо `Money`). |
| **Long Parameter List** | Более 3–4 параметров метода — сигнал к введению объекта-параметра. |
| **Data Clumps** | Группы переменных, которые всегда ходят вместе (например, `host`, `port`, `user`, `password`), — кандидат в отдельный класс. |

#### Object-Orientation Abusers (нарушение ОО-принципов)

| Запах | Описание |
|-------|----------|
| **Switch Statements** | Разветвлённые `switch`/`if-instanceof` — признак отсутствия полиморфизма. |
| **Refused Bequest** | Подкласс не использует методы/поля родителя — нарушение LSP. |
| **Temporary Field** | Поле класса заполнено только при определённых условиях. |

#### Change Preventers (мешают изменениям)

| Запах | Описание |
|-------|----------|
| **Divergent Change** | Один класс приходится менять по разным причинам — нарушение SRP. |
| **Shotgun Surgery** | Одно логическое изменение требует правок во многих классах. |
| **Parallel Inheritance Hierarchies** | Добавление подкласса в одной иерархии вынуждает добавлять подкласс в другой. |

#### Dispensables (лишнее)

| Запах | Описание |
|-------|----------|
| **Duplicate Code** | Одинаковый или очень похожий код в нескольких местах. |
| **Dead Code** | Код, который никогда не выполняется. |
| **Speculative Generality** | Абстракции и параметры «на будущее» без реального использования (нарушение YAGNI). |
| **Data Class** | Класс только с полями, геттерами/сеттерами и никакой логики. |

#### Couplers (чрезмерное зацепление)

| Запах | Описание |
|-------|----------|
| **Feature Envy** | Метод больше работает с данными чужого класса, чем своего — логику надо переместить. |
| **Inappropriate Intimacy** | Класс знает о внутренней реализации другого класса. |
| **Message Chains** | Цепочки `a.getB().getC().doSomething()` — нарушение Закона Деметры. |
| **Middle Man** | Класс только делегирует вызовы другому — лишний уровень абстракции. |

---

### Техники рефакторинга

Классифицированы по книге «Refactoring» (Мартин Фаулер, 2-е изд. 2018).

#### Composing Methods (декомпозиция методов)

| Техника | Когда применять |
|---------|-----------------|
| **Extract Method** | Фрагмент логики можно выделить в отдельный метод с понятным именем. |
| **Inline Method** | Тело метода очевиднее его имени — убираем лишний уровень. |
| **Extract Variable** | Сложное выражение — присваиваем самодокументирующей переменной. |
| **Replace Temp with Query** | Локальная переменная с вычисленным значением — заменяем вызовом метода. |
| **Replace Method with Method Object** | Метод с кучей локальных переменных — делаем отдельный класс. |
| **Substitute Algorithm** | Есть более ясный/эффективный алгоритм для той же задачи. |

**Пример Extract Method:**
```java
// До
void printInvoice() {
    System.out.println("Клиент: " + customer.getName());
    double total = 0;
    for (Order o : orders) total += o.getAmount();
    System.out.println("Итого: " + total);
}

// После
void printInvoice() {
    printCustomer();
    printTotal();
}

private void printCustomer() {
    System.out.println("Клиент: " + customer.getName());
}

private void printTotal() {
    double total = orders.stream().mapToDouble(Order::getAmount).sum();
    System.out.println("Итого: " + total);
}
```

#### Moving Features between Objects (перемещение функциональности)

| Техника | Описание |
|---------|----------|
| **Move Method / Move Field** | Метод/поле находится не в том классе — перемещаем ближе к данным. |
| **Extract Class** | Часть класса выполняет самостоятельную роль — выделяем в отдельный класс. |
| **Inline Class** | Класс почти ничего не делает — сливаем с другим. |
| **Hide Delegate** | Скрываем цепочку `a.getB().doSomething()` за методом `a.doSomethingViaB()`. |

#### Simplifying Conditionals (упрощение условий)

| Техника | Описание |
|---------|----------|
| **Decompose Conditional** | Сложное `if-else` — разбиваем на методы с говорящими именами. |
| **Replace Conditional with Polymorphism** | Набор `instanceof` или `switch` по типу — заменяем переопределением метода. |
| **Replace Nested Conditional with Guard Clauses** | Вместо глубокой вложенности — ранние `return`. |
| **Introduce Null Object** | Убираем проверки `if (obj == null)` — вводим объект-заглушку. |

**Пример Guard Clauses:**
```java
// До
double getPayAmount() {
    if (isDead) {
        return deadAmount();
    } else {
        if (isSeparated) {
            return separatedAmount();
        } else {
            return normalPayAmount();
        }
    }
}

// После
double getPayAmount() {
    if (isDead)      return deadAmount();
    if (isSeparated) return separatedAmount();
    return normalPayAmount();
}
```

#### Organizing Data (организация данных)

| Техника | Описание |
|---------|----------|
| **Replace Primitive with Object** | Примитив обретает поведение — оборачиваем в класс. |
| **Replace Magic Number with Symbolic Constant** | `3.14` → `Math.PI`. |
| **Encapsulate Collection** | Коллекция не возвращается напрямую — через методы доступа. |
| **Introduce Parameter Object** | Группа параметров → класс-параметр. |

---

### Чистый код: практические правила

По книге «Clean Code» (Robert C. Martin, 2008).

#### Именование

- Имена **раскрывают намерение**: `daysSinceCreation` лучше, чем `d`.
- Имена **произносимы**: `generationTimestamp` лучше, чем `genymdhms`.
- Имена **удобны для поиска**: константа `MAX_CLASSES_PER_STUDENT` лучше, чем число `7`.
- Не используй префиксы типов (`strName`, `iCount`) — IDE справится сама.
- Классы — существительные, методы — глаголы.
- Длина имени переменной пропорциональна размеру области видимости.

#### Функции

- Функция должна делать **одно** и делать это хорошо.
- Максимальная длина — 20 строк (идеал — 5–10).
- Уровень абстракции внутри функции — **один**.
- Аргументов — **не более трёх**; при большем числе — объект-параметр.
- Нет флаговых параметров (`doSomething(true)`) — создай два метода.
- Нет побочных эффектов: функция `checkPassword()` не должна инициализировать сессию.

#### Комментарии

- Хороший код **не нуждается** в комментариях — имена говорят сами за себя.
- Допустимые комментарии: пояснение намерения, предупреждение о последствиях, `TODO`, Javadoc
  для публичного API.
- Недопустимые: закомментированный код, переформулировка кода, дата и автор.

```java
// Плохо: комментарий дублирует код
// increment i by 1
i++;

// Хорошо: комментарий объясняет неочевидное решение
// Используем Bloch's enum singleton вместо double-checked locking
// из соображений thread safety и сериализации
public enum Registry { INSTANCE; ... }
```

#### Обработка ошибок

- Используй исключения вместо кодов ошибок.
- Не возвращай `null` — используй `Optional<T>` или Null Object.
- Не передавай `null` в аргументах метода.
- Каждое исключение должно предоставлять достаточный контекст для диагностики.

#### Классы

- Классы должны быть маленькими — метрика: количество **ответственностей**, не строк.
- Инкапсуляция: поля `private`, публичный интерфейс минимален.
- Правило бойскаута: «Оставь код чище, чем нашёл».

---

## Достоверные источники

1. **[Refactoring.Guru — Code Smells](https://refactoring.guru/refactoring/smells)** —
   исчерпывающий каталог запахов кода с описанием причин и способов устранения. Ресурс основан
   на книге Мартина Фаулера «Refactoring».

2. **[Refactoring.Guru — Refactoring Techniques](https://refactoring.guru/refactoring/techniques)** —
   структурированный справочник по техникам рефакторинга (Composing Methods, Moving Features,
   Simplifying Conditionals и др.).

3. **[FreeCodeCamp — Introduction to SOLID Principles](https://www.freecodecamp.org/news/introduction-to-solid-principles/)** —
   разбор всех пяти принципов с примерами нарушений и исправлений на Java; редакционно
   проверяемый контент.

4. **Книга «Clean Code» (Robert C. Martin, Prentice Hall, 2008)** — канон по культуре написания
   читаемого и поддерживаемого кода; первоисточник правил именования, функций, комментариев.
   ISBN: 978-0-13-235088-4.

5. **Книга «Refactoring: Improving the Design of Existing Code» (Martin Fowler, 2nd ed., 2018)** —
   классика по технике рефакторинга; первоисточник термина «code smells» и каталога приёмов.
   ISBN: 978-0-13-468599-1.

6. **[Refactoring.Guru — What is Refactoring](https://refactoring.guru/refactoring/what-is-refactoring)** —
   чёткое определение рефакторинга, его отличие от других изменений кода, связь с техническим
   долгом.
