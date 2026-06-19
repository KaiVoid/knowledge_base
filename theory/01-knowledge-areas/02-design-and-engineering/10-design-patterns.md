# Паттерны проектирования

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по паттернам →](../interview-questions/design-patterns-01.md)
> **Связанные области:** [[11-solid-clean-code]], [[13-spring-core]]

## Что это и зачем

Паттерны проектирования — типовые проверенные решения часто встречающихся задач проектирования.
Знание классических паттернов (GoF) помогает писать гибкий, расширяемый код и понимать архитектуру
фреймворков (например, Spring построен на множестве паттернов). На собеседованиях паттерны — частая
тема, особенно Singleton, Factory, Builder, Strategy, Observer, Proxy.

Книга «Design Patterns: Elements of Reusable Object-Oriented Software» (Gamma, Helm, Johnson, Vlissides,
1994) описывает **23 паттерна**, разбитых на три категории: порождающие (creational), структурные
(structural) и поведенческие (behavioral). Официальной документации Oracle по GoF-паттернам не
существует — первоисточником является книга GoF и авторитетные ресурсы (refactoring.guru, Baeldung).

Паттерны различаются по сложности, уровню детализации и масштабу применения. Их знание позволяет:
- говорить с коллегами на общем языке («здесь Strategy», «это Facade»);
- распознавать готовые решения в JDK и фреймворках;
- избегать overengineering — паттерн уместен только тогда, когда решает реальную проблему.

## Ключевые подтемы

---

### Порождающие паттерны (Creational)

Отвечают за создание объектов, повышая гибкость и переиспользуемость существующего кода.

#### Singleton

**Проблема:** гарантировать, что класс имеет единственный экземпляр, и предоставить глобальную точку доступа к нему.

**Решение:** скрыть конструктор (`private`), хранить экземпляр в статическом поле, возвращать его через статический метод.

Наивная реализация (не потокобезопасна):

```java
public final class Singleton {
    private static Singleton instance;
    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```

Потокобезопасная реализация с двойной проверкой (double-checked locking):

```java
public final class Singleton {
    // volatile обязателен: без него JIT может нарушить видимость
    private static volatile Singleton instance;
    private Singleton() {}

    public static Singleton getInstance() {
        Singleton result = instance;
        if (result != null) return result;
        synchronized (Singleton.class) {
            if (instance == null) {
                instance = new Singleton();
            }
            return instance;
        }
    }
}
```

Ещё более лаконичный вариант — через enum (потокобезопасен, защищён от десериализации и рефлексии):

```java
public enum Singleton {
    INSTANCE;
    public void doSomething() { ... }
}
```

**В JDK:** `java.lang.Runtime#getRuntime()`, `java.awt.Desktop#getDesktop()`, `java.lang.System#getSecurityManager()`.

**Минусы:** нарушает модульность, усложняет юнит-тестирование (скрытая глобальная зависимость). В Spring
роль Singleton берут на себя бины со scope `singleton` (по умолчанию) — один экземпляр на контейнер IoC.

---

#### Factory Method (Фабричный метод)

**Проблема:** код знает, *что* нужно создать, но не должен знать *как именно* — тип объекта может
меняться в зависимости от конфигурации или подкласса.

**Решение:** определить в базовом классе абстрактный метод создания объекта; подклассы переопределяют
этот метод и решают, экземпляр какого класса возвращать.

```java
// Интерфейс продукта
public interface Button {
    void render();
}

// Абстрактный создатель
public abstract class Dialog {
    public void renderWindow() {
        Button btn = createButton(); // фабричный метод
        btn.render();
    }
    protected abstract Button createButton();
}

// Конкретный создатель
public class WebDialog extends Dialog {
    @Override
    protected Button createButton() {
        return new HtmlButton();
    }
}
```

**В JDK:** `Calendar.getInstance()`, `ResourceBundle.getBundle()`, `java.util.Iterator` (возвращается
через `collection.iterator()`).

**Отличие от Abstract Factory:** Factory Method создаёт *один* продукт; Abstract Factory — *семейство*
взаимосвязанных продуктов.

---

#### Abstract Factory (Абстрактная фабрика)

**Проблема:** необходимо создавать семейства взаимосвязанных объектов, не привязываясь к их конкретным
классам. Например, набор GUI-виджетов для Windows и macOS должен быть взаимозаменяем.

**Решение:** интерфейс фабрики объявляет методы создания каждого продукта семейства; конкретные фабрики
реализуют интерфейс для нужной платформы/конфигурации.

```java
public interface GUIFactory {
    Button createButton();
    Checkbox createCheckbox();
}

public class MacOSFactory implements GUIFactory {
    public Button createButton()   { return new MacOSButton(); }
    public Checkbox createCheckbox() { return new MacOSCheckbox(); }
}

public class WindowsFactory implements GUIFactory {
    public Button createButton()   { return new WindowsButton(); }
    public Checkbox createCheckbox() { return new WindowsCheckbox(); }
}
```

Клиентский код работает только с `GUIFactory`, `Button`, `Checkbox` — без привязки к платформе.

---

#### Builder (Строитель)

**Проблема:** объект имеет много параметров (часть необязательна). Конструктор с 10 аргументами
нечитаем; набор перегруженных конструкторов (telescoping constructor) неудобен.

**Решение:** выделить отдельный объект-строитель с fluent-методами; опционально — Director, который
инкапсулирует конкретные рецепты построения.

```java
// Классический Builder с Director
public interface HouseBuilder {
    HouseBuilder setWalls(int count);
    HouseBuilder setRoof(String type);
    HouseBuilder setGarage(boolean has);
    House build();
}

// Fluent-вариант (часто используется без интерфейса)
public class Pizza {
    private final String crust;
    private final String sauce;
    private final List<String> toppings;

    private Pizza(Builder b) {
        this.crust    = b.crust;
        this.sauce    = b.sauce;
        this.toppings = List.copyOf(b.toppings);
    }

    public static class Builder {
        private String crust = "thin";
        private String sauce = "tomato";
        private final List<String> toppings = new ArrayList<>();

        public Builder crust(String c)   { this.crust = c; return this; }
        public Builder sauce(String s)   { this.sauce = s; return this; }
        public Builder topping(String t) { toppings.add(t); return this; }
        public Pizza build()             { return new Pizza(this); }
    }
}

// Использование:
Pizza pizza = new Pizza.Builder()
    .crust("thick")
    .topping("cheese")
    .topping("mushrooms")
    .build();
```

**В JDK:** `StringBuilder`, `Stream.Builder`, `HttpClient.Builder` (Java 11+).
**В библиотеках:** Lombok `@Builder`, Guava `ImmutableList.Builder`.

---

#### Prototype (Прототип)

**Проблема:** создание объекта «с нуля» дорого (сложная инициализация, обращение к БД); нужна копия
уже существующего объекта.

**Решение:** клонировать существующий объект вместо создания нового. В Java — через интерфейс
`Cloneable` и метод `clone()`, либо через конструктор копирования, либо через сериализацию.

```java
public class Shape implements Cloneable {
    private int x, y;
    @Override
    public Shape clone() throws CloneNotSupportedException {
        return (Shape) super.clone(); // shallow copy
    }
}
```

Важно: `Object.clone()` делает *поверхностную* копию. Для глубокого клонирования нужно переопределить
метод вручную или использовать сериализацию / copy-constructor.

---

### Структурные паттерны (Structural)

Описывают, как компоновать объекты и классы в более крупные структуры, сохраняя их гибкость.

---

#### Adapter (Адаптер)

**Проблема:** два компонента с несовместимыми интерфейсами не могут взаимодействовать напрямую.

**Решение:** обёртка-адаптер реализует нужный интерфейс и внутри вызывает методы адаптируемого класса.

```java
// Целевой интерфейс
public interface RoundPeg {
    double getRadius();
}

// Несовместимый класс
public class SquarePeg {
    private double width;
    public double getWidth() { return width; }
}

// Адаптер
public class SquarePegAdapter extends RoundPeg {
    private final SquarePeg peg;
    public SquarePegAdapter(SquarePeg peg) { this.peg = peg; }

    @Override
    public double getRadius() {
        // вписанная окружность квадрата со стороной w имеет радиус w*sqrt(2)/2
        return Math.sqrt(Math.pow(peg.getWidth() / 2, 2) * 2);
    }
}
```

**В JDK:** `java.util.Arrays#asList()`, `java.io.InputStreamReader(InputStream)`,
`java.io.OutputStreamWriter(OutputStream)`, `javax.xml.bind.annotation.adapters.XmlAdapter`.

---

#### Decorator (Декоратор)

**Проблема:** нужно добавлять поведение объекту динамически, не меняя его класс и не создавая взрывной
рост подклассов.

**Решение:** декоратор реализует тот же интерфейс, что и обёртываемый объект, хранит ссылку на него
и добавляет своё поведение до/после вызова.

```java
public interface DataSource {
    void writeData(String data);
    String readData();
}

// Базовый компонент
public class FileDataSource implements DataSource { ... }

// Базовый декоратор
public class DataSourceDecorator implements DataSource {
    private final DataSource wrappee;
    public DataSourceDecorator(DataSource source) { this.wrappee = source; }

    @Override public void writeData(String data) { wrappee.writeData(data); }
    @Override public String readData()            { return wrappee.readData(); }
}

// Конкретный декоратор — шифрование
public class EncryptionDecorator extends DataSourceDecorator {
    @Override
    public void writeData(String data) {
        super.writeData(encrypt(data));
    }
}

// Стекирование декораторов:
DataSource source = new CompressionDecorator(
    new EncryptionDecorator(
        new FileDataSource("file.txt")));
source.writeData("Hello");
```

**В JDK (самый известный пример):** вся иерархия `java.io` — `BufferedInputStream`,
`GZIPOutputStream`, `DataInputStream` — построена на Decorator. Каждый класс принимает в
конструктор объект собственного базового типа и добавляет поведение.

---

#### Proxy (Заместитель)

**Проблема:** нужно добавить к объекту дополнительное поведение (кэширование, контроль доступа,
логирование, ленивая инициализация), не меняя его код и не нарушая контракт.

**Решение:** прокси реализует тот же интерфейс, что и реальный объект, и перехватывает вызовы.

```java
public interface Service {
    String fetch(String url);
}

public class RealService implements Service {
    public String fetch(String url) { /* HTTP-запрос */ return "data"; }
}

public class CachingProxy implements Service {
    private final Service service;
    private final Map<String, String> cache = new HashMap<>();

    public CachingProxy(Service service) { this.service = service; }

    @Override
    public String fetch(String url) {
        return cache.computeIfAbsent(url, service::fetch);
    }
}
```

**В JDK:** `java.lang.reflect.Proxy` — динамический прокси на основе интерфейса;
`java.rmi.*` — удалённый прокси.

**В Spring AOP:** Spring по умолчанию создаёт JDK-прокси (если бин реализует интерфейс)
или CGLIB-прокси (если нет). Все аннотации `@Transactional`, `@Cacheable`, `@Async` работают
именно через прокси, перехватывая вызовы методов.

Важное ограничение: **self-invocation** — вызов метода внутри того же бина обходит прокси и
аспекты не срабатывают. Решение — инжектировать бин в себя или использовать `AopContext.currentProxy()`.

---

#### Facade (Фасад)

**Проблема:** подсистема сложна; клиент вынужден знать о множестве её классов и их взаимодействии.

**Решение:** фасад предоставляет простой интерфейс к сложной подсистеме, скрывая детали реализации.

```java
public class VideoConverter {
    public File convert(String filename, String format) {
        VideoFile file     = new VideoFile(filename);
        Codec     codec    = CodecFactory.extract(file);
        BitrateReader reader = new BitrateReader(file, codec);
        BitrateReader buffer = BitrateReader.read(reader, codec);
        return new AudioMixer().fix(buffer);
    }
}
// Клиент вызывает один метод вместо пяти классов
```

**В Spring:** `JdbcTemplate`, `RestTemplate`, `HibernateTemplate` — классические фасады над
сложными API.

---

#### Composite (Компоновщик)

**Проблема:** нужно работать с деревьями объектов единообразно — один объект и группа объектов
должны поддерживать одинаковый интерфейс.

**Решение:** и листовые объекты, и контейнеры реализуют общий интерфейс `Component`. Контейнер
делегирует операцию всем своим дочерним элементам рекурсивно.

**В JDK:** `java.awt.Container extends Component` — классическая реализация. `javax.faces.component.UIComponent`.

---

#### Bridge (Мост)

**Проблема:** абстракция и реализация сильно связаны; изменение одной стороны ломает другую.

**Решение:** разделить на две независимые иерархии — абстракцию и реализацию — и связать их
через композицию, а не наследование.

| Паттерн | Цель | Связь |
|---------|------|-------|
| Bridge | Разделить абстракцию и реализацию | Заранее спроектирована |
| Adapter | Совместить несовместимые интерфейсы | Постфактум (legacy) |
| Decorator | Добавить поведение динамически | Тот же интерфейс |
| Proxy | Контролировать доступ | Тот же интерфейс |

---

#### Flyweight (Приспособленец)

**Проблема:** создание огромного числа мелких объектов с общим состоянием расходует много памяти.

**Решение:** разделить состояние объекта на *внутреннее* (неизменяемое, разделяемое) и *внешнее*
(передаётся контекстом). Хранить только уникальные внутренние состояния.

**В JDK:** `Integer.valueOf(-128..127)` кэшируется (пул интернирования), `String.intern()`.

---

### Поведенческие паттерны (Behavioral)

Определяют алгоритмы и распределение ответственностей между объектами.

---

#### Strategy (Стратегия)

**Проблема:** несколько вариантов алгоритма выбираются в рантайме; жёсткий `if/switch` на каждый
вариант нарушает OCP.

**Решение:** инкапсулировать каждый алгоритм в отдельный класс с общим интерфейсом; контекст
хранит ссылку на стратегию и делегирует ей работу.

```java
public interface SortStrategy {
    void sort(int[] data);
}

public class QuickSort implements SortStrategy {
    public void sort(int[] data) { /* ... */ }
}

public class MergeSort implements SortStrategy {
    public void sort(int[] data) { /* ... */ }
}

public class Sorter {
    private SortStrategy strategy;
    public Sorter(SortStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(SortStrategy strategy) { this.strategy = strategy; }
    public void sort(int[] data) { strategy.sort(data); }
}
```

**Java 8+:** простые стратегии заменяются лямбдами или ссылками на методы — интерфейс стратегии
становится `@FunctionalInterface`. `Comparator<T>` — канонический пример Strategy в JDK.

---

#### Observer (Наблюдатель)

**Проблема:** несколько объектов должны реагировать на изменение состояния другого объекта без
жёсткой привязки к нему.

**Решение:** субъект (Publisher) хранит список подписчиков (Subscriber/Listener) и уведомляет
их при изменении состояния.

```java
public interface EventListener {
    void onEvent(String type, Object payload);
}

public class EventManager {
    private final Map<String, List<EventListener>> listeners = new HashMap<>();

    public void subscribe(String type, EventListener listener) {
        listeners.computeIfAbsent(type, k -> new ArrayList<>()).add(listener);
    }

    public void unsubscribe(String type, EventListener listener) {
        listeners.getOrDefault(type, List.of()).remove(listener);
    }

    public void notify(String type, Object payload) {
        listeners.getOrDefault(type, List.of())
                 .forEach(l -> l.onEvent(type, payload));
    }
}
```

**В JDK:** `java.util.Observer` / `Observable` (deprecated Java 9), `java.util.EventListener`,
Swing-слушатели (`ActionListener`, `MouseListener`).

**В Spring:** `ApplicationEvent` / `ApplicationListener`, аннотация `@EventListener` — Observer
поверх IoC-контейнера.

**Важный нюанс:** забытая отписка — распространённая причина утечки памяти. Слушатель держит
ссылку на себя в субъекте и не собирается GC.

---

#### Template Method (Шаблонный метод)

**Проблема:** несколько классов реализуют похожий алгоритм, отличаясь только отдельными шагами;
дублирование структуры.

**Решение:** определить *скелет* алгоритма в базовом классе (`final`-метод), вынести изменяемые
шаги в абстрактные (или переопределяемые) методы.

```java
public abstract class DataMiner {
    // шаблонный метод — скелет алгоритма
    public final void mine(String path) {
        String raw  = extractData(path);   // шаг 1 — переопределяется
        String data = parseData(raw);      // шаг 2 — переопределяется
        analyzeData(data);                 // шаг 3 — общий
        reportResults();                   // шаг 4 — общий
    }
    protected abstract String extractData(String path);
    protected abstract String parseData(String raw);
    // ... общие методы
}

public class PDFMiner extends DataMiner {
    protected String extractData(String path) { /* читаем PDF */ return ""; }
    protected String parseData(String raw)    { /* парсим PDF */ return ""; }
}
```

**В JDK:** `java.util.AbstractList#indexOf()`, `java.io.InputStream#read(byte[], int, int)`,
`javax.servlet.http.HttpServlet#service()` (вызывает `doGet`/`doPost`).

**В Spring:** `JdbcTemplate#execute()` — шаблонный метод, где пользователь передаёт только
`PreparedStatementCallback`.

---

#### Command (Команда)

**Проблема:** нужно параметризовать объекты операциями, ставить операции в очередь, поддерживать
отмену (undo/redo).

**Решение:** инкапсулировать запрос в объект-команду с методами `execute()` и `undo()`.

```java
public interface Command {
    void execute();
    void undo();
}

public class CopyCommand implements Command {
    private final Editor editor;
    private String backup;

    public void execute() {
        backup = editor.getSelection();
        editor.copyToClipboard();
    }
    public void undo() { /* восстановить backup */ }
}
```

**В JDK:** `java.lang.Runnable`, `java.util.concurrent.Callable`, `java.swing.Action`.

---

#### Iterator (Итератор)

**Проблема:** нужен единый способ обхода различных коллекций без раскрытия их внутреннего устройства.

**Решение:** итератор инкапсулирует логику обхода и предоставляет интерфейс `hasNext()` / `next()`.

**В JDK:** `java.util.Iterator<E>` — краеугольный камень Collections Framework. Все коллекции,
реализующие `Iterable<E>`, поддерживают `for-each`. `java.util.ListIterator` добавляет обход в
обе стороны.

---

#### State (Состояние)

**Проблема:** поведение объекта зависит от его состояния; огромный `if/switch` по состояниям нарушает OCP.

**Решение:** каждое состояние — отдельный класс, реализующий общий интерфейс. Контекст делегирует
поведение текущему объекту-состоянию.

```java
public interface TrafficLightState {
    void handle(TrafficLight light);
}

public class GreenState implements TrafficLightState {
    public void handle(TrafficLight light) {
        System.out.println("GO");
        light.setState(new YellowState());
    }
}
```

**В JDK:** `java.util.Iterator` сам по себе stateful; `Thread.State`-переходы в JVM.

---

#### Chain of Responsibility (Цепочка обязанностей)

**Проблема:** запрос должен пройти через несколько обработчиков; отправитель не должен знать,
кто именно обработает запрос.

**Решение:** обработчики выстраиваются в цепочку; каждый либо обрабатывает запрос, либо передаёт
следующему.

**В Java EE / Jakarta EE:** `javax.servlet.Filter` — цепочка фильтров в Servlet API.
**В Spring Security:** `SecurityFilterChain` — набор фильтров безопасности.
**В JDK:** `java.util.logging` — иерархия `Logger` → `Handler`.

---

#### Mediator (Посредник)

**Проблема:** компоненты тесно связаны между собой; изменение одного требует изменения других.

**Решение:** посредник централизует взаимодействие; компоненты знают только о посреднике, не о
друг друге.

**В Spring MVC:** `DispatcherServlet` — классический Mediator между контроллерами, view-resolver,
handler-mapper и прочими компонентами.

---

#### Memento (Снимок)

**Проблема:** нужно сохранять и восстанавливать состояние объекта, не нарушая инкапсуляцию.

**Решение:** объект создаёт снимок своего состояния (`Memento`), передаёт его хранителю; при
необходимости восстанавливается из снимка.

**В JDK:** `java.io.Serializable` — фактическая реализация идеи снимка через сериализацию.

---

#### Visitor (Посетитель)

**Проблема:** нужно добавить новую операцию к иерархии классов, не изменяя их.

**Решение:** операция выносится в отдельный класс-посетитель; каждый элемент иерархии реализует
метод `accept(Visitor v)`.

**В JDK:** `java.nio.file.FileVisitor`, `javax.lang.model.element.ElementVisitor`,
`javax.annotation.processing.AbstractProcessor`.

---

### Антипаттерны и ограничения

**Когда паттерн избыточен:**
- Singleton — если объект не должен быть глобальным или единственным; в Spring предпочтительнее
  бин с инжекцией зависимости.
- Factory Method — если иерархия классов проста, прямой `new` читаемее.
- Observer — при необходимости строгой последовательности уведомлений или синхронного управления потоком.

**Типичные антипаттерны:**
- **God Object** — класс, знающий/делающий слишком много; нарушает SRP.
- **Anemic Domain Model** — доменные объекты без поведения; вся логика размазана по сервисам.
- **Premature Optimization** — выбор паттерна ради паттерна без реальной проблемы.
- **Overengineering** — применение Abstract Factory там, где достаточно `new`.

---

### Паттерны в Spring Framework

| Паттерн | Где используется в Spring |
|---------|--------------------------|
| Singleton | Все бины с `scope=singleton` (по умолчанию) — один экземпляр на ApplicationContext |
| Factory Method | `BeanFactory#getBean()`, `@Bean`-методы в `@Configuration` |
| Abstract Factory | `ApplicationContext` как абстрактная фабрика бинов |
| Proxy | Spring AOP: JDK-прокси (если есть интерфейс) или CGLIB-прокси (без интерфейса); `@Transactional`, `@Cacheable`, `@Async` |
| Decorator | `BeanDefinitionDecorator`; `HttpServletRequestWrapper` |
| Template Method | `JdbcTemplate`, `RestTemplate`, `HibernateTemplate` |
| Observer | `ApplicationEvent` / `ApplicationListener` / `@EventListener` |
| Mediator | `DispatcherServlet` в Spring MVC |
| Facade | `JdbcTemplate`, `RestTemplate` скрывают сложные API |
| Composite | `CompositeXxx`-классы (напр. `CompositeCacheManager`) |

---

## Достоверные источники

1. **[Refactoring.Guru — Design Patterns](https://refactoring.guru/design-patterns)** — наглядный
   каталог всех 23 паттернов GoF с диаграммами UML и примерами кода на Java. Считается эталонным
   онлайн-ресурсом; авторы ссылаются на книгу GoF как на первоисточник.

2. **[Refactoring.Guru — Design Patterns Catalog](https://refactoring.guru/design-patterns/catalog)** —
   сводный каталог паттернов по категориям с прямыми ссылками на Java-примеры для каждого паттерна.

3. **Книга «Design Patterns: Elements of Reusable Object-Oriented Software»** — Gamma, Helm,
   Johnson, Vlissides (GoF), Addison-Wesley, 1994. Первоисточник всех 23 классических паттернов;
   официальной документации Oracle по GoF-паттернам не существует — книга GoF является канонической.

4. **Книга «Head First Design Patterns» (2nd ed., 2020)** — Freeman, Robson, O'Reilly. Доступное
   введение с примерами на Java; хороша для первого знакомства, но не заменяет GoF.

5. **[Baeldung — Design Patterns Series](https://www.baeldung.com/design-patterns-series)** —
   серия практических статей по паттернам с кодом на Java; авторитетный ресурс для Java-разработчиков,
   регулярно обновляется.

6. **[Baeldung — Design Patterns in the Spring Framework](https://www.baeldung.com/spring-framework-design-patterns)** —
   подробный разбор того, как GoF-паттерны применяются внутри Spring; полезно для понимания
   архитектуры фреймворка.
