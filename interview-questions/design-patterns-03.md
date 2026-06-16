# Паттерны проектирования — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/10-design-patterns.md](../knowledge-base/10-design-patterns.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](design-patterns-01.md) · [ч.2](design-patterns-02.md) · **ч.3**

---
### Вопрос 41. Что такое паттерн Memento? Опишите роли Originator, Caretaker и Memento. Как Memento взаимодействует с паттерном Command при реализации undo/redo?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Memento — refactoring.guru](https://refactoring.guru/design-patterns/memento)

Memento — поведенческий паттерн, позволяющий сохранять и восстанавливать прошлые состояния объекта, не раскрывая деталей его реализации.

**Originator** — объект, состояние которого нужно сохранить. Он умеет создавать снимки своего состояния и восстанавливать его из снимков. В примере с текстовым редактором класс Editor является Originator — он создаёт снимок перед выполнением каждой операции.

**Memento** — объект-значение (value object), являющийся снимком состояния Originator. Он принимает данные только через конструктор и не имеет сеттеров, то есть неизменяем. Содержимое Memento недоступно никому, кроме создавшего его Originator.

**Caretaker** — отвечает за жизненный цикл Memento: решает, когда сохранять состояние и когда восстанавливать его. Это может быть стек истории команд или отдельный объект истории. Caretaker не может изменять содержимое снимка.

**Memento и Command для undo/redo.** Паттерны дополняют друг друга: команды отвечают за выполнение операций над целевым объектом, а Memento сохраняет состояние этого объекта непосредственно перед выполнением команды. При запросе отмены приложение извлекает последнюю команду из истории и вызывает её метод `undo()`, который восстанавливает ранее сохранённое состояние.

#### Ответ от Claude

**Три роли паттерна**

- **Originator** — хранитель бизнес-логики и внутреннего состояния. Предоставляет методы `save()` / `createMemento()` для создания снимка и `restore(memento)` для восстановления. Только Originator знает, как упаковать своё состояние в снимок и как его распаковать обратно.

- **Memento** — иммутабельный контейнер состояния. Принимает данные через конструктор, предоставляет только геттеры (или вообще не предоставляет публичного API для Caretaker). Является «чёрным ящиком» для всех, кроме Originator.

- **Caretaker** — управляет коллекцией снимков (обычно стек или список). Знает, *когда* нужно сохранять и восстанавливать состояние, но не знает и не должен знать, *что* именно хранится внутри Memento.

**Интеграция Memento и Command для undo/redo**

Command и Memento решают разные задачи и естественно дополняют друг друга:

1. Перед выполнением каждой команды она вызывает `editor.saveBackup()` — Originator создаёт Memento и сохраняет его внутри объекта команды (или в общем стеке истории).
2. Команда выполняет операцию, изменяя состояние Originator.
3. При вызове `undo()` команда передаёт сохранённый Memento обратно Originator для восстановления предыдущего состояния.

Такое разделение обязанностей позволяет командам не содержать обратную (инверсную) логику — достаточно просто восстановить сохранённый снимок. Redo реализуется аналогично: при повторном выполнении команды сохраняется новый снимок.

**Типичная структура в коде:**

```java
// Originator
public class Editor {
    private String content;

    public Memento save() {
        return new Memento(content);
    }

    public void restore(Memento m) {
        this.content = m.getState();
    }
}

// Command с хранением снимка
public class PasteCommand implements Command {
    private Editor editor;
    private Memento backup;

    public void execute() {
        backup = editor.save();
        // выполнить вставку
    }

    public void undo() {
        editor.restore(backup);
    }
}

// Caretaker
public class CommandHistory {
    private Deque<Command> history = new ArrayDeque<>();

    public void push(Command c) { history.push(c); }

    public void undo() {
        if (!history.isEmpty()) history.pop().undo();
    }
}
```

---

### Вопрос 42. Почему объект Memento должен быть непрозрачным (opaque) для Caretaker? Как реализовать это ограничение в Java: через вложенный класс, пакетную видимость или интерфейс без методов?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Memento — refactoring.guru](https://refactoring.guru/design-patterns/memento)

Паттерн Memento решает фундаментальную проблему: если раскрыть внутреннее состояние объекта, чтобы другие могли его сохранять, классы станут слишком хрупкими. Если же ограничить доступ к состоянию — создать снимок не получится.

Решение заключается в том, чтобы сделать Originator ответственным за создание снимков своего состояния. Никакой другой объект не может прочитать снимок, что делает данные о состоянии исходного объекта безопасными и надёжно защищёнными.

Caretaker взаимодействует с Memento через ограниченный интерфейс, который может позволять получать метаданные снимка (время создания, название операции и т.д.), но не само состояние объекта. Originator при этом имеет полный доступ ко всем полям Memento, что позволяет восстанавливать предыдущее состояние по своему усмотрению.

Классическая реализация опирается на вложенные классы, доступные во многих популярных языках программирования, в том числе в Java. Если вложенные классы недоступны, нужно извлечь пустой интерфейс из класса Memento и заставить все остальные объекты использовать именно его.

#### Ответ от Claude

**Почему Memento должен быть непрозрачным для Caretaker**

Это требование вытекает из принципа инкапсуляции. Если Caretaker сможет читать или изменять содержимое Memento, то:

- Внутренняя структура Originator перестанет быть деталью реализации — она «вытечет» наружу через публичный API Memento.
- Caretaker может случайно или намеренно изменить сохранённое состояние, нарушив корректность undo/redo.
- Добавление нового поля в Originator потребует изменений в Caretaker — нарушается принцип единственной ответственности.

Caretaker должен уметь только хранить Memento и передавать его обратно Originator — не более.

**Три способа реализации непрозрачности в Java**

**1. Вложенный (inner/static nested) класс — рекомендованный способ**

Memento объявляется как `private static` вложенный класс внутри Originator. Caretaker ссылается на него через публичный интерфейс-маркер или через тип `Originator.Memento`, но не может получить доступ к приватным полям.

```java
public class Originator {
    private String state;

    public Memento save() {
        return new Memento(state);
    }

    public void restore(Memento m) {
        this.state = m.state; // доступно: вложенный класс виден Originator
    }

    public static final class Memento {
        private final String state; // приватное — Caretaker не видит

        private Memento(String state) { // приватный конструктор
            this.state = state;
        }
    }
}

// Caretaker работает с типом Originator.Memento, но не может прочитать state
public class Caretaker {
    private final Deque<Originator.Memento> history = new ArrayDeque<>();

    public void save(Originator o) { history.push(o.save()); }
    public void undo(Originator o) { if (!history.isEmpty()) o.restore(history.pop()); }
}
```

Caretaker может хранить и передавать `Originator.Memento`, но обращаться к полю `state` не вправе — оно приватное. Originator как внешний класс имеет доступ к приватным членам своего вложенного класса.

**2. Пакетная видимость (package-private)**

Класс Memento и его конструктор объявляются с видимостью по умолчанию (без модификатора). Caretaker, находящийся в другом пакете, не может создать Memento самостоятельно. Originator, находящийся в том же пакете, имеет полный доступ.

```java
// пакет com.example.editor
class EditorMemento {          // package-private: снаружи пакета — только как Object
    final String content;      // package-private поле

    EditorMemento(String content) { // package-private конструктор
        this.content = content;
    }
}
```

Минус подхода: Caretaker тоже должен быть в другом пакете — иначе он получит доступ к полям Memento.

**3. Интерфейс-маркер (пустой интерфейс)**

Если вложенные классы неудобны, вводится пустой публичный интерфейс `IMemento`. Caretaker работает только с этим интерфейсом и не может вызывать никаких методов. Реальная реализация остаётся приватной или package-private.

```java
public interface IMemento { /* маркер — без методов */ }

public class Originator {
    private String state;

    public IMemento save() { return new MementoImpl(state); }

    public void restore(IMemento m) {
        this.state = ((MementoImpl) m).state; // downcast внутри Originator
    }

    private static class MementoImpl implements IMemento {
        private final String state;
        MementoImpl(String state) { this.state = state; }
    }
}
```

Caretaker хранит `IMemento` и не может вызвать ни одного метода, кроме унаследованных от `Object`.

**Сравнение подходов**

| Подход | Степень защиты | Удобство | Применимость |
|---|---|---|---|
| Вложенный класс | Высокая | Высокое | Рекомендован GoF и refactoring.guru |
| Пакетная видимость | Средняя | Среднее | Если Caretaker в другом пакете |
| Интерфейс-маркер | Средняя | Среднее | Резервный вариант, когда вложенность неудобна |

**Расхождение источников:** howtodoinjava.com и refactoring.guru оба упоминают все три подхода, но приоритет расставляют по-разному. refactoring.guru считает вложенный класс каноническим решением из GoF; howtodoinjava.com отмечает, что на практике широко применяется и пакетная видимость, особенно когда Memento должен быть виден внутри пакета нескольким классам. Интерфейс-маркер оба источника позиционируют как запасной вариант для языков или архитектур без удобной поддержки вложенных классов.
### Вопрос 43. Паттерн State реализует конечный автомат (FSM). Как правильно организовать переходы между состояниями: кто должен инициировать переход — Context или сам объект-State? Какие плюсы и минусы каждого подхода?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [State — refactoring.guru](https://refactoring.guru/design-patterns/state)

Паттерн State не предписывает, кто именно должен инициировать переход: и Context, и конкретные объекты-State могут устанавливать следующее состояние в контексте. На практике State-объекты хранят обратную ссылку на Context и через неё вызывают `context.setState(new NextState())`. Именно это отличает State от Strategy: конкретные состояния могут знать друг о друге и сами инициировать переходы, тогда как стратегии об этом не ведают. Традиционный подход с огромными условными операторами, которые выбирают поведение в зависимости от текущего состояния, превращается в объектно-ориентированную конструкцию: при каждом переходе ссылка на объект текущего состояния в Context просто заменяется.

#### Ответ от Claude

В GoF-паттерне State переходы между состояниями могут инициироваться двумя способами. Расхождений между источниками нет, оба подхода легитимны — разница в архитектурных компромиссах.

**Подход 1. Переход инициирует сам объект-State (наиболее распространён)**

Конкретный State-объект сам решает, когда и в какое состояние перейти, и вызывает `context.setState(new AnotherState(context))`:

```java
public class NoCoinState implements VendingMachineState {
    private final VendingMachine machine; // обратная ссылка на Context

    public NoCoinState(VendingMachine machine) {
        this.machine = machine;
    }

    @Override
    public void insertCoin() {
        System.out.println("Монета принята");
        machine.setState(machine.getContainsCoinState()); // State инициирует переход
    }

    @Override
    public void pressButton() {
        System.out.println("Сначала вставьте монету");
        // переход не инициируется — остаёмся в текущем состоянии
    }
}
```

Плюсы:
- Каждый класс несёт единственную ответственность: описывает поведение и условия выхода из одного конкретного состояния (SRP).
- Context освобождается от сложных условных конструкций и просто хранит ссылку на текущее состояние.
- Новое состояние добавляется созданием нового класса без изменения Context (OCP).
- Логика переходов явная и локализована рядом с самим поведением.

Минусы:
- Классы-состояния могут знать друг о друге и создавать друг друга — возникает связность между State-классами.
- Общий граф переходов автомата разбросан по разным классам, его сложнее увидеть целиком.

**Подход 2. Переход инициирует Context**

Context сам решает, в какое состояние перейти, на основе возвращённого результата или наблюдаемого условия — обычно через `switch`/`if-else`:

```java
public class VendingMachine { // Context
    private State currentState;

    public void insertCoin() {
        currentState.insertCoin();
        // Context сам решает следующий переход
        if (currentState instanceof NoCoinState) {
            setState(containsCoinState);
        }
    }
}
```

Плюсы:
- Весь граф переходов сосредоточен в одном месте — Context. Проще видеть автомат целиком.
- State-классы не знают друг о друге — нет перекрёстных зависимостей.

Минусы:
- Context разрастается: появляются условные конструкции для каждого перехода — именно то, от чего паттерн призван избавить.
- Добавление нового состояния требует изменения Context (нарушение OCP).

**Практическая рекомендация.** В большинстве реальных реализаций используют первый подход: State-объект сам вызывает `context.setState(...)`. Это максимально приближено к оригинальному примеру из GoF и к коду Spring Statemachine. Второй подход оправдан, когда переходы определяются внешними условиями (событиями из окружения), которые State-объект не может наблюдать сам.

---

### Вопрос 44. Как паттерн State применяется в Spring Statemachine или в реализации жизненного цикла бина (BeanFactory)? Чем это отличается от прямой реализации FSM через перечисление (enum) с switch?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Spring Statemachine — Reference Documentation](https://docs.spring.io/spring-statemachine/docs/current/reference/)

Spring Statemachine реализует конечный автомат как декларативную конфигурацию поверх IoC-контейнера Spring. Состояния и события задаются как перечисления; конфигурация переходов описывается через `StateMachineTransitionConfigurer`:

```java
@Configuration
@EnableStateMachine
public class StateMachineConfig
        extends EnumStateMachineConfigurerAdapter<States, Events> {

    @Override
    public void configure(StateMachineStateConfigurer<States, Events> states)
            throws Exception {
        states.withStates()
              .initial(States.SI)
              .end(States.SF)
              .states(EnumSet.allOf(States.class));
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<States, Events> transitions)
            throws Exception {
        transitions
            .withExternal()
                .source(States.S1).target(States.S2).event(Events.E1)
                .guard(guard()).action(action())
                .and()
            .withInternal()
                .source(States.S2).event(Events.E2);
    }
}
```

Фреймворк предоставляет три типа переходов: `external` (смена состояния), `internal` (без смены), `local` (между подсостояниями). Поддерживаются иерархические состояния (substates), регионы (параллельные подавтоматы), guard-условия, actions, extended state (переменные без создания лишних состояний), персистентность, интеграция со Spring Security и реактивная модель на Reactor.

#### Ответ от Claude

**Spring Statemachine и паттерн State**

Spring Statemachine — это полноценный фреймворк для конечных автоматов, построенный поверх IoC-контейнера Spring. Паттерн State здесь реализован в инфраструктуре фреймворка: каждое состояние является объектом (`State<S,E>`), контекст перехода представлен `StateContext`, а сам автомат (`StateMachine<S,E>`) играет роль Context из GoF. Разработчик описывает только граф переходов в декларативной конфигурации — фреймворк управляет жизненным циклом State-объектов сам.

Ключевые возможности, недоступные при ручной реализации:
- Иерархические состояния (substates) — устраняют дублирование поведения.
- Регионы (orthogonal states) — несколько параллельных подавтоматов в одном родительском состоянии.
- Guard-условия — условные переходы через `context.getExtendedState()`.
- Extended state — переменные, хранящиеся в контексте без умножения числа состояний.
- Персистентность состояния между сессиями.
- Интеграция со Spring Security: доступ к переходу контролируется правами пользователя.
- Реактивные переходы (Reactor) и поддержка распределённых машин (Zookeeper).

**Жизненный цикл бина в BeanFactory**

Жизненный цикл Spring-бина является конечным автоматом, хотя и не реализованным через явный GoF-паттерн State. Бин проходит через фиксированную последовательность фаз (состояний):

1. Загрузка `BeanDefinition` (метаданные).
2. Инстанциирование (`Constructor`).
3. Внедрение зависимостей (Setter/Field injection).
4. Обработка `BeanPostProcessor#postProcessBeforeInitialization`.
5. Инициализация (`@PostConstruct`, `InitializingBean#afterPropertiesSet`, custom `init-method`).
6. Обработка `BeanPostProcessor#postProcessAfterInitialization` (здесь создаются AOP-прокси).
7. Бин готов к использованию (Ready).
8. Уничтожение (`@PreDestroy`, `DisposableBean#destroy`, custom `destroy-method`).

Каждый переход контролируется контейнером (Context), а не самим бином — это противоположный подход по сравнению с классическим GoF State. Тем не менее каждая фаза инкапсулирует специфическое поведение и переход к следующей происходит строго в определённом порядке — принцип FSM соблюдается.

**Сравнение с enum + switch**

| Критерий | enum + switch | Spring Statemachine / OOP State |
|---|---|---|
| Простота для 3–5 состояний | Высокая | Избыточна |
| Расширяемость (OCP) | Плохая: надо менять enum и switch | Хорошая: новый класс/состояние без изменения существующих |
| Обнаружение незаполненных случаев | Слабое: компилятор не гарантирует полноту | Сильное: абстрактные методы в enum или интерфейс State |
| Иерархия, регионы | Нет | Да (Spring Statemachine) |
| Actions, Guards | Ручной код | Декларативно |
| Персистентность | Ручной код | Встроена |
| Читаемость графа переходов | Сосредоточена в одном switch | Распределена по классам (но есть визуализация) |
| Сложность настройки | Нулевая | Средняя — высокая |

Enum + switch — правильный выбор для плоского, неизменяемого автомата с малым числом состояний (4–6). При росте сложности (условные переходы, иерархия, параллелизм, персистентность) это решение превращается в «спагетти»: большой switch разрастается, добавление нового состояния требует правки в нескольких местах, компилятор не страхует от пропуска ветвей. Spring Statemachine или ручной GoF State решают эту проблему ценой большего объёма инфраструктурного кода.

**Расхождение источников.** Java Code Geeks (2011) описывает enum-подход как продвинутую технику, тогда как документация Spring Statemachine и refactoring.guru указывают на его ограниченную масштабируемость. Оба утверждения верны на своём уровне сложности: enum хорош для небольших FSM, объектный/фреймворковый подход — для enterprise-уровня.

---

### Вопрос 45. Что такое паттерн Chain of Responsibility? Чем он отличается от простого цикла по списку обработчиков? Приведите реальный пример из Java EE / Jakarta EE (Servlet Filter) или Spring Security (FilterChainProxy).

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Chain of Responsibility — refactoring.guru](https://refactoring.guru/design-patterns/chain-of-responsibility)

Chain of Responsibility — поведенческий паттерн, позволяющий передавать запросы последовательно по цепочке обработчиков. Каждый обработчик решает: обработать запрос самостоятельно или передать его дальше по цепи. Ключевое отличие от простого цикла по списку: элемент цепи может изменять порядок проверок — например, выполнить проверку до всех остальных или после. Это даёт несравнимо большую гибкость, чем простой перебор. Обработчик хранит ссылку на следующий элемент цепи и сам решает, вызывать ли `checkNext()`. Цепочку можно собирать и изменять в runtime. Паттерн следует SRP (каждый обработчик — одна ответственность) и OCP (новые обработчики не требуют изменения существующих). Недостаток — запрос может остаться необработанным, если ни один обработчик не взял его.

#### Ответ от Claude

**Что такое Chain of Responsibility**

Chain of Responsibility (Цепочка обязанностей) — поведенческий паттерн проектирования из книги GoF. Запрос передаётся по цепочке объектов-обработчиков; каждый обработчик либо обрабатывает его сам, либо передаёт следующему. Отправитель запроса не знает, кто именно его обработает.

Типичная структура:

```java
public abstract class Handler {
    private Handler next;

    public Handler setNext(Handler next) {
        this.next = next;
        return next;
    }

    public abstract boolean handle(Request request);

    protected boolean handleNext(Request request) {
        if (next == null) return true;
        return next.handle(request);
    }
}

public class AuthHandler extends Handler {
    @Override
    public boolean handle(Request request) {
        if (!request.isAuthenticated()) {
            System.out.println("Отказ: не аутентифицирован");
            return false; // цепь прервана
        }
        return handleNext(request); // передаём дальше
    }
}
```

**Чем Chain of Responsibility отличается от простого цикла по списку**

| Аспект | Простой цикл | Chain of Responsibility |
|---|---|---|
| Управление потоком | Всегда обходит весь список | Обработчик сам решает — продолжать цепь или прервать |
| Раннее завершение | Только через `break` в цикле | Естественно: не вызвал `next` — цепь остановлена |
| Порядок вызова `next` | Фиксирован — всегда после тела цикла | Гибкий: `next` можно вызвать в начале, середине или конце обработчика |
| Изменение запроса | Сложно — надо передавать результат между итерациями | Просто — обработчик модифицирует объект запроса до/после вызова `next` |
| Динамическая сборка | Перебирается готовый список | Цепочка собирается и перестраивается в runtime |
| Ответственность | Логика «кому передать» в одном месте (в цикле) | Логика «передавать ли дальше» инкапсулирована в каждом обработчике |

Именно возможность обработчика прервать цепь или выполнить логику до/после вызова следующего звена — главное качественное отличие от цикла.

**Пример: Servlet Filter в Jakarta EE**

`javax.servlet.Filter` / `jakarta.servlet.Filter` — классический пример Chain of Responsibility из спецификации Java EE:

```java
public class LoggingFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request,
                         ServletResponse response,
                         FilterChain chain)       // chain — ссылка на остаток цепочки
            throws IOException, ServletException {

        System.out.println("До обработки");
        chain.doFilter(request, response); // передаём управление следующему фильтру
        System.out.println("После обработки"); // выполняется на обратном пути
    }
}
```

`FilterChain` — объект, предоставляемый контейнером (Tomcat, Jetty); вызов `chain.doFilter()` передаёт запрос следующему фильтру или конечному сервлету. Если фильтр не вызывает `chain.doFilter()` — цепь прерывается и запрос до сервлета не доходит. Это и есть механизм раннего завершения, недоступный в простом цикле.

JavaDoc `FilterChain` (Java EE 7):
> "A FilterChain is an object provided by the servlet container to the developer giving a view into the invocation chain of a filtered request. Filters use the FilterChain to invoke the next filter in the chain, or if the calling filter is the last filter in the chain, to invoke the resource at the end of the chain."
>
> — [FilterChain (Java EE 7)](https://docs.oracle.com/javaee/7/api/javax/servlet/FilterChain.html)

**Пример: Spring Security FilterChainProxy**

Spring Security расширяет идею Servlet Filter через `FilterChainProxy` — центральный диспетчер безопасности:

```
HTTP-запрос
    → DelegatingFilterProxy (мост между Servlet-контейнером и Spring)
    → FilterChainProxy (Spring Bean)
    → выбирает первую подходящую SecurityFilterChain по RequestMatcher
    → выполняет цепочку Security-фильтров:
        1. CsrfFilter
        2. UsernamePasswordAuthenticationFilter
        3. BasicAuthenticationFilter
        4. AuthorizationFilter
        ...
```

Ключевые особенности `FilterChainProxy` как Chain of Responsibility:
- **First-match wins**: итерация по `List<SecurityFilterChain>` прекращается на первой совпавшей цепочке — последующие не проверяются.
- Каждый фильтр в цепочке независим и может прервать обработку (например, `UsernamePasswordAuthenticationFilter` не вызывает `chain.doFilter()` при неуспешной аутентификации).
- `HttpFirewall` применяется до передачи запроса в цепочку — ещё один слой «до вызова next».
- Разные URL-паттерны могут обслуживаться разными `SecurityFilterChain` с разными наборами фильтров.

Таким образом, оба примера (Servlet Filter и Spring Security) демонстрируют одну идею Chain of Responsibility: каждый обработчик инкапсулирует решение «обработать и/или передать дальше», что недостижимо простым `for`-циклом.
### Вопрос 46. Как Spring Security реализует Chain of Responsibility через SecurityFilterChain и FilterChainProxy? Почему фильтры зарегистрированы в FilterChainProxy, а не напрямую в контейнере сервлетов, и какие это даёт преимущества?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Architecture :: Spring Security](https://docs.spring.io/spring-security/reference/servlet/architecture.html)

Spring Security's Servlet support is based on Servlet Filters. The client sends a request to the application, and the container creates a FilterChain which contains the Filter instances and Servlet that should process the HttpServletRequest based on the path of the request URI.

FilterChainProxy is a special Filter provided by Spring Security that allows delegating to many Filter instances through SecurityFilterChain. Since FilterChainProxy is a Bean, it is typically wrapped in a DelegatingFilterProxy.

SecurityFilterChain is used by FilterChainProxy to determine which Spring Security Filter instances should be invoked for the current request. The Security Filters in SecurityFilterChain are typically Beans, but they are registered with FilterChainProxy instead of DelegatingFilterProxy. FilterChainProxy provides a number of advantages to registering directly with the Servlet container or DelegatingFilterProxy:

- It provides a starting point for all of Spring Security's Servlet support. For this reason, if you try to troubleshoot Spring Security's Servlet support, adding a debug point in FilterChainProxy is a great place to start.
- Since FilterChainProxy is central to Spring Security usage, it can perform tasks that are not viewed as optional. For example, it clears out the SecurityContext to avoid memory leaks. It also applies Spring Security's HttpFirewall to protect applications against certain types of attacks.
- It provides more flexibility in determining when a SecurityFilterChain should be invoked. In a Servlet container, Filter instances are invoked based upon the URL alone. However, FilterChainProxy can determine invocation based upon anything in the HttpServletRequest by using the RequestMatcher interface.
- FilterChainProxy can be used to determine which SecurityFilterChain should be used. This allows providing a completely separate configuration for different slices of your application, for example /api/** vs /web/**.

Перевод: Spring Security строит поддержку сервлетов полностью на стандартных фильтрах. Контейнер создаёт FilterChain из фильтров и сервлета для обработки запроса. FilterChainProxy — специальный фильтр Spring Security, делегирующий работу нескольким Filter-экземплярам через SecurityFilterChain. Поскольку FilterChainProxy является бином Spring, он обычно оборачивается DelegatingFilterProxy. SecurityFilterChain используется FilterChainProxy для определения, какие фильтры безопасности должны быть вызваны для текущего запроса. Фильтры внутри SecurityFilterChain регистрируются именно в FilterChainProxy, а не в DelegatingFilterProxy или контейнере напрямую — это даёт ряд преимуществ: централизованная точка отладки, очистка SecurityContext во избежание утечек памяти, применение HttpFirewall, гибкий выбор цепочки по произвольным атрибутам запроса (не только по URL), возможность иметь независимые конфигурации для /api/** и /web/**.

#### Ответ от Claude

**Структура компонентов (по убыванию уровня абстракции):**

```
Servlet Container (Tomcat/Jetty)
    └── DelegatingFilterProxy  (стандартный javax.servlet.Filter)
            └── FilterChainProxy  (Spring Bean, реализует Filter)
                    ├── SecurityFilterChain #0  (pattern: /api/**)
                    │       └── [Filter1, Filter2, Filter3]
                    ├── SecurityFilterChain #1  (pattern: /admin/**)
                    │       └── [Filter1, Filter4, Filter5, Filter6]
                    └── SecurityFilterChain #N  (pattern: /**)
                            └── [полный набор фильтров безопасности]
```

**DelegatingFilterProxy** — мост между жизненным циклом контейнера сервлетов и Spring ApplicationContext. Он регистрируется в web.xml (или через ServletInitializer) как обычный фильтр, но при первом запросе лениво находит в контексте Spring бин с именем `springSecurityFilterChain` (то есть FilterChainProxy) и делегирует ему выполнение. Это решает проблему порядка инициализации: контейнер регистрирует фильтры до того, как Spring поднимает ApplicationContext.

**FilterChainProxy** принимает запрос и перебирает список SecurityFilterChain в порядке объявления. Первая цепочка, чей RequestMatcher совпадает с запросом, выполняется — остальные игнорируются. Каждая цепочка — это отдельный список Security Filter-бинов Spring.

**Паттерн Chain of Responsibility реализован на двух уровнях:**

1. На уровне FilterChainProxy: запрос передаётся первой подходящей SecurityFilterChain (каждая цепочка — потенциальный обработчик, первое совпадение — победитель).
2. На уровне SecurityFilterChain: фильтры внутри цепочки вызывают друг друга через стандартный механизм `chain.doFilter(request, response)`. Каждый фильтр может обработать запрос и передать его дальше, либо прервать цепочку (не вызвав `chain.doFilter`), вернув ответ напрямую (например, при ошибке аутентификации).

Стандартный порядок фильтров внутри SecurityFilterChain (из документации):

```
DisableEncodeUrlFilter
WebAsyncManagerIntegrationFilter
SecurityContextHolderFilter
HeaderWriterFilter
CsrfFilter
LogoutFilter
UsernamePasswordAuthenticationFilter
BasicAuthenticationFilter
RequestCacheAwareFilter
SecurityContextHolderAwareRequestFilter
AnonymousAuthenticationFilter
ExceptionTranslationFilter
AuthorizationFilter
```

**Почему фильтры регистрируются в FilterChainProxy, а не в контейнере напрямую:**

| Причина | Детали |
|---|---|
| Гибкий матчинг | Контейнер матчит фильтры только по URL-паттерну. FilterChainProxy использует `RequestMatcher` — можно матчить по заголовкам, методу HTTP, параметрам и т.д. |
| Множественные независимые цепочки | Для `/api/**` и `/web/**` можно настроить принципиально разные наборы фильтров и механизмы аутентификации |
| Централизованная безопасность | FilterChainProxy в любом случае очищает SecurityContext (предотвращение утечек) и применяет HttpFirewall (защита от path traversal, parameter pollution) |
| Один entry point в web.xml | Вместо десятков `<filter>` — один DelegatingFilterProxy |
| Spring-lifecycle для фильтров | Фильтры получают DI, `@Autowired`, участвуют в жизненном цикле бинов |
| Единая точка отладки | Брейкпоинт в FilterChainProxy позволяет отлаживать всю безопасность централизованно |

**Пример конфигурации (Spring Boot / Spring Security 6):**

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/api/**")
            .csrf(AbstractHttpConfigurer::disable)
            .httpBasic(Customizer.withDefaults())
            .authorizeHttpRequests(auth -> auth.anyRequest().authenticated());
        return http.build();
    }

    @Bean
    @Order(2)
    public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
        http
            .formLogin(Customizer.withDefaults())
            .authorizeHttpRequests(auth ->
                auth.requestMatchers("/public/**").permitAll()
                    .anyRequest().authenticated());
        return http.build();
    }
}
```

Здесь FilterChainProxy будет хранить два SecurityFilterChain. Запрос к `/api/users` попадёт в первую цепочку (Bearer-аутентификация без CSRF), запрос к `/login` — во вторую (форма входа с CSRF).

---

### Вопрос 47. Что такое паттерн Flyweight? Чем внутреннее (intrinsic) состояние отличается от внешнего (extrinsic)? Как String pool и кэш Integer.valueOf(-128..127) в JDK реализуют этот паттерн?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Flyweight — Refactoring.Guru](https://refactoring.guru/design-patterns/flyweight)

Flyweight is a structural design pattern that lets you fit more objects into the available amount of RAM by sharing common parts of state between multiple objects instead of keeping all of the data in each object.

The constant data of an object is usually called the intrinsic state. It lives within the object; other objects can only read it, not change it. The rest of the object's state, often altered "from the outside" by other objects, is called the extrinsic state.

The Flyweight pattern suggests that you stop storing the extrinsic state inside the object. Instead, you should pass this state to specific methods which rely on it. Only the intrinsic state stays within the object, letting you reuse it in different contexts. As a result, you'd need fewer of these objects since they only differ in the intrinsic state, which has much fewer variations than the extrinsic.

The flyweight object's state is made up of two parts:
- **Intrinsic** — an invariant component shared with other similar objects (immutable, stored inside the flyweight).
- **Extrinsic** — a variant component which can be manipulated by the client code (passed as parameters, not stored in flyweight).

Flyweight can be spotted all over the Number classes in Java, where the valueOf methods used to create an object of any data type's wrapper class are designed to cache values and return them when required.

Перевод: Flyweight («Легковес») — структурный паттерн проектирования, позволяющий уместить в памяти больше объектов за счёт разделения общих частей состояния между несколькими объектами вместо хранения всех данных в каждом отдельном объекте. Неизменяемые данные объекта называются внутренним (intrinsic) состоянием — они живут внутри объекта, другие объекты могут их только читать. Остальная часть — внешнее (extrinsic) состояние — изменяется извне и передаётся в методы flyweight в качестве параметров, не хранясь в самом объекте. Паттерн встречается повсюду в классах-обёртках Java, где методы valueOf кэшируют и повторно возвращают уже созданные объекты.

#### Ответ от Claude

**Суть паттерна.** Flyweight применяется, когда приложение создаёт огромное количество однотипных объектов, большинство данных в которых одинаковы. Паттерн предлагает вынести повторяющиеся (внутренние) данные в отдельный разделяемый объект-flyweight, а уникальные (внешние) данные передавать в методы при каждом вызове.

**Intrinsic state (внутреннее состояние):**
- Неизменяемые данные, одинаковые для группы объектов.
- Хранятся внутри flyweight-объекта.
- Инициализируются один раз при создании.
- Безопасны для совместного использования, так как доступны только на чтение.

**Extrinsic state (внешнее состояние):**
- Уникальные данные, различающиеся у каждого «контекста».
- Не хранятся в flyweight; передаются как аргументы методов.
- Управляются клиентским кодом.

**Классический пример — отрисовка леса:**

```java
// Flyweight: хранит intrinsic state (разделяется многими деревьями)
public final class TreeType {
    private final String name;    // intrinsic
    private final Color color;    // intrinsic
    private final String texture; // intrinsic

    public TreeType(String name, Color color, String texture) {
        this.name = name;
        this.color = color;
        this.texture = texture;
    }

    // extrinsic state (x, y) передаётся снаружи — не хранится в flyweight
    public void draw(Graphics g, int x, int y) {
        // рисуем дерево в позиции (x, y) с нашим цветом и текстурой
    }
}

// Контекст: хранит extrinsic state + ссылку на flyweight
public class Tree {
    private final int x;          // extrinsic
    private final int y;          // extrinsic
    private final TreeType type;  // ссылка на разделяемый flyweight

    public void draw(Graphics g) {
        type.draw(g, this.x, this.y);
    }
}

// Flyweight Factory
public class TreeFactory {
    private static final Map<String, TreeType> cache = new HashMap<>();

    public static TreeType getTreeType(String name, Color color, String texture) {
        return cache.computeIfAbsent(name, k -> new TreeType(name, color, texture));
    }
}
```

При рендеринге 1 000 000 деревьев двух видов (дуб и берёза) в памяти будут лишь два объекта TreeType, а не миллион копий.

**Flyweight в JDK — String pool.**

Строковые литералы в Java автоматически интернируются (interned): JVM помещает их в специальную область памяти — String Pool (с Java 7 — в Heap, до этого — в PermGen). При встрече одинакового литерала JVM возвращает ссылку на уже существующий объект.

```java
String a = "hello";
String b = "hello";
System.out.println(a == b); // true — один объект из пула

String c = new String("hello"); // явно создаём в Heap, минуя пул
System.out.println(a == c);     // false

String d = c.intern(); // помещаем в пул и возвращаем ссылку на пулный объект
System.out.println(a == d); // true
```

Строка — неизменяемый объект, её содержимое — intrinsic state (разделяется). Контекст использования (переменная, позиция в коде) — extrinsic (у каждого вызывающего свой).

**Flyweight в JDK — Integer.valueOf(-128..127).**

Согласно спецификации (`Integer.valueOf` в Java SE 21), метод всегда кэширует значения от -128 до 127 включительно (верхняя граница может быть увеличена через JVM-флаг `-XX:AutoBoxCacheMax`):

```java
Integer a = Integer.valueOf(100);
Integer b = Integer.valueOf(100);
System.out.println(a == b); // true — один кэшированный объект (intrinsic: значение 100)

Integer c = Integer.valueOf(200);
Integer d = Integer.valueOf(200);
System.out.println(c == d); // false — за пределами кэша, разные объекты
```

Внутри `IntegerCache` хранится массив из 256 заранее созданных Integer-объектов. Числовое значение — intrinsic state (неизменяемо, разделяется). То, кто держит ссылку и зачем — extrinsic context, управляемый клиентом.

Аналогично работают `Boolean.valueOf`, `Byte.valueOf`, `Short.valueOf(-128..127)`, `Long.valueOf(-128..127)`, `Character.valueOf(0..127)`.

**Аналогия в структуре:**

| Элемент | Flyweight | String Pool | Integer Cache |
|---|---|---|---|
| Flyweight-объект | TreeType | String | Integer |
| Фабрика | TreeFactory | JVM intern | IntegerCache |
| Intrinsic state | name, color, texture | символы строки | числовое значение |
| Extrinsic state | координаты x, y | переменная, позиция | контекст использования |

---

### Вопрос 48. Чем паттерн Flyweight отличается от Object Pool? Какие ограничения накладывает Flyweight на изменяемость объектов, и почему нарушение этого требования приводит к гонкам данных в многопоточном окружении?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Flyweight — Refactoring.Guru](https://refactoring.guru/design-patterns/flyweight)

A flyweight should initialize its state just once, via constructor parameters. It shouldn't expose any setters or public fields to other objects.

Flyweight saves RAM by sharing heavy state between multiple objects. Object Pool saves RAM by reusing the same objects instead of creating them each time some client code needs an object with the same properties.

At first glance, these patterns are very similar because of the reuse of objects. But there's one crucial difference in the intention:

- The Pool manages a collection of reusable objects. Each such object is used by only one client at the same time, and after usage, it's returned to the Pool.
- The Flyweight provides a reference to the same object to multiple clients simultaneously. Since the same Flyweight can be used by multiple clients at the same time, all Flyweights must be immutable and be able to be read by many at the same time.

Перевод: Flyweight должен инициализировать своё состояние один раз — через параметры конструктора. Он не должен предоставлять сеттеры или публичные поля. Flyweight экономит RAM за счёт разделения тяжёлого состояния между несколькими объектами, а Object Pool экономит RAM за счёт повторного использования одних и тех же объектов вместо создания новых при каждом запросе клиента. На первый взгляд паттерны похожи из-за переиспользования объектов, но есть принципиальное различие в намерении: Pool управляет коллекцией объектов, каждый из которых используется только одним клиентом одновременно и после использования возвращается в пул. Flyweight, напротив, предоставляет ссылку на один объект сразу многим клиентам одновременно — поэтому все flyweight-объекты должны быть неизменяемыми.

#### Ответ от Claude

**Сравнение паттернов Flyweight и Object Pool:**

| Критерий | Flyweight | Object Pool |
|---|---|---|
| Цель | Снизить потребление памяти за счёт разделения состояния | Снизить затраты на создание дорогостоящих объектов |
| Тип паттерна | Структурный (GoF) | Порождающий |
| Одновременный доступ | Один flyweight используется МНОГИМИ клиентами одновременно | Один объект из пула используется ОДНИМ клиентом одновременно |
| Изменяемость объекта | Обязательно неизменяемый (immutable) | Может быть изменяемым; возвращается в пул после сброса состояния |
| Жизненный цикл | Объект существует всё время работы приложения | Объект «берётся» из пула (acquire) и «возвращается» (release) |
| Типичные примеры в Java | String pool, Integer cache, Character cache | Connection pool (HikariCP), Thread pool (ExecutorService), ByteBuffer pool (Netty) |
| Проблема, которую решает | Память: тысячи/миллионы экземпляров с одинаковыми данными | Производительность: дорогая инициализация (соединение с БД, создание потока) |

**Ограничение изменяемости во Flyweight.**

Flyweight-объект ДОЛЖЕН быть неизменяемым. Это требование не является опциональным советом — это структурное ограничение паттерна. Причина: один и тот же flyweight-объект одновременно используется несколькими клиентами. Если позволить изменять его состояние, одно изменение от одного клиента затронет всех остальных.

**Почему нарушение ведёт к гонкам данных.**

Гонка данных (data race) возникает, когда два или более потока обращаются к одной ячейке памяти, причём хотя бы один из них выполняет запись, и при этом отсутствует синхронизация. Результат операций становится недетерминированным — зависит от порядка выполнения потоков.

Сценарий нарушения требования неизменяемости Flyweight:

```java
// НЕПРАВИЛЬНО: изменяемый flyweight
public class MutableTreeType {
    private String name;     // intrinsic, но изменяемое!
    private Color color;

    // Есть сеттер — flyweight стал изменяемым
    public void setColor(Color color) {
        this.color = color;
    }

    public void draw(Graphics g, int x, int y) {
        // использует this.color
    }
}
```

В многопоточном окружении:

```
Thread-1:  treeType.setColor(RED)      // Поток 1 меняет цвет на RED
Thread-2:  treeType.draw(g, 10, 20)    // Поток 2 рисует — какой цвет он видит?
Thread-1:  treeType.draw(g, 50, 70)    // Поток 1 рисует — возможно, уже другой цвет
```

Проблемы в данном сценарии:
1. **Видимость (visibility):** без `volatile` или синхронизации поток 2 может видеть устаревшее значение цвета из своего кэша ядра процессора.
2. **Атомарность:** если `Color` — составной объект (RGB-поля), частичное обновление может привести к чтению «полуобновлённого» объекта.
3. **Упорядоченность:** JIT-компилятор и процессор вправе переставлять инструкции, нарушая ожидаемый порядок операций.

**Правильное применение Flyweight — только immutable:**

```java
// ПРАВИЛЬНО: неизменяемый flyweight
public final class ImmutableTreeType {
    private final String name;    // final — нельзя изменить после конструктора
    private final Color color;    // final
    private final String texture; // final

    public ImmutableTreeType(String name, Color color, String texture) {
        this.name = name;
        this.color = color;
        this.texture = texture;
    }

    // Только геттеры, нет сеттеров
    public String getName() { return name; }
    public Color getColor() { return color; }

    // extrinsic state (x, y) приходит как параметр
    public void draw(Graphics g, int x, int y) {
        // безопасно для любого количества потоков
    }
}
```

Неизменяемые объекты в Java безопасны для многопоточного использования без какой-либо синхронизации: поскольку их состояние не меняется после публикации, гарантированной инициализацией через `final`-поля (Java Memory Model, JLS 17.5), любой поток всегда видит корректные значения.

**Различие на практике (Object Pool с мутацией vs Flyweight):**

Object Pool явно управляет эксклюзивным владением: объект нельзя использовать двумя клиентами одновременно, что позволяет безопасно мутировать его состояние перед возвратом в пул. Пример — HikariCP сбрасывает состояние соединения (autoCommit, transactionIsolation) при возврате в пул.

Flyweight не имеет механизма «взять / вернуть». Объект просто существует и доступен всем одновременно. Именно поэтому неизменяемость — не рекомендация, а обязательное условие корректности паттерна.

---
### Вопрос 49. Что такое антипаттерн «God Object» («Всемогущий объект»)? Какие признаки указывают на его наличие в коде, и какие паттерны проектирования помогают его разбить (Facade, Mediator, Command)?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [How to refactor the God object class antipattern — TheServerSide](https://www.theserverside.com/tip/How-to-refactor-the-God-object-antipattern)

God Object — это единственный Java-класс, который нарушает принцип единственной ответственности (SRP), поскольку выполняет множество задач, объявляет многочисленные несвязанные поля и содержит методы, не имеющие логической связи друг с другом, кроме той, что они в совокупности обеспечивают работу приложения.

**Признаки God Object:**
- Выполняет разнообразные несвязанные задачи.
- Содержит поля, которые не принадлежат логически к одной концепции.
- Включает методы без единой чёткой ответственности.
- Отсутствует понятная единственная цель класса.

Такая ситуация возникает, когда разработчики ставят скорость доставки выше качества проектирования, особенно в условиях коротких Agile-спринтов.

**Стратегия рефакторинга (5 шагов):**
1. Создать исчерпывающий набор юнит-тестов, чтобы безопасно валидировать функциональность в процессе рефакторинга.
2. Выявить зависимости клиентов — понять, какие компоненты полагаются на God Object.
3. Перенести статические методы в утилитарные классы, убрав непринадлежащую экземпляру функциональность.
4. Сгруппировать связанные методы и поля в небольшие классы с единственной ответственностью.
5. Удалить или объявить устаревшим оригинальный God Object после завершения рефакторинга.

**Фасад как переходная стратегия:** Если удаление God Object вызывает проблемы компиляции, можно временно превратить его в фасад, где методы делегируют вызовы во вновь созданные специализированные объекты. Методы помечаются как `@Deprecated`, чтобы направить дальнейшую разработку в нужное русло.

#### Ответ от Claude

**Определение**

God Object («Всемогущий объект», «Класс-Бог») — антипаттерн, при котором один класс берёт на себя слишком много ответственностей, знает слишком много о других частях системы и контролирует слишком много аспектов её работы. Это прямое нарушение принципа единственной ответственности (SRP) из SOLID.

**Признаки God Object в коде**

Структурные и метрические:
- Высокое значение WMC (Weighted Methods per Class) — очень много методов в одном классе.
- Высокое значение CBO (Coupling Between Objects) — класс связан с большим числом других классов.
- Низкое значение LCOM (Lack of Cohesion in Methods) — методы класса не связаны единой концепцией.
- Класс охватывает несколько слоёв приложения (бизнес-логику, работу с данными, представление) одновременно.

Поведенческие:
- Класс невозможно протестировать изолированно — у него слишком много зависимостей.
- Изменение в одном месте класса ломает несвязанную функциональность в другом.
- Другие классы в системе почти не содержат логики и лишь перекладывают работу на God Object.
- Невозможно дать классу единственное краткое название, отражающее его суть.

**Причины возникновения**

- Отсутствие чётких границ доменных областей при проектировании.
- Практика добавлять новую функциональность в уже существующий класс для удобства («здесь уже всё есть»).
- Игнорирование принципов Domain-Driven Design (DDD).
- Технический долг, накопленный при интенсивных итерациях без рефакторинга.

**Паттерны проектирования для разбиения God Object**

**Facade (Фасад)**
Фасад используется как переходная стратегия при рефакторинге. God Object превращается в тонкий фасад: его методы начинают делегировать вызовы во вновь созданные специализированные классы. Клиентский код при этом не меняется. Постепенно, по мере стабилизации новых классов, клиенты переводятся на прямое использование специализированных классов, а фасад удаляется. Это позволяет рефакторить инкрементально, не ломая систему на каждом шаге.

```java
// До: God Object
class ApplicationManager {
    void processOrder(Order o) { ... }
    void sendEmail(String to, String body) { ... }
    void generateReport(ReportType type) { ... }
    void authenticateUser(String login, String pass) { ... }
}

// После: Facade + специализированные классы
class ApplicationManager { // временный фасад
    private OrderService orderService = new OrderService();
    private EmailService emailService = new EmailService();
    private ReportService reportService = new ReportService();
    private AuthService authService = new AuthService();

    @Deprecated
    void processOrder(Order o) { orderService.process(o); }
    @Deprecated
    void sendEmail(String to, String body) { emailService.send(to, body); }
}
```

**Mediator (Посредник)**
Когда God Object выступает координатором взаимодействия множества компонентов, его роль можно выделить в явный Mediator. Mediator принимает на себя оркестрацию взаимодействий между компонентами, устраняя прямые зависимости между ними. Важное предостережение из официальной документации (refactoring.guru): «со временем Mediator может сам превратиться в God Object» — поэтому зона ответственности посредника должна быть чётко ограничена координацией, но не бизнес-логикой.

**Command (Команда)**
Если God Object содержит разнородные операции, вызываемые из разных мест, каждую такую операцию можно инкапсулировать в отдельный объект-команду (Command). Это позволяет:
- вынести каждый сценарий использования в самостоятельный класс;
- легко добавлять новые операции без изменения существующего кода (Open/Closed Principle);
- поддерживать очереди команд, логирование и отмену операций (Undo).

**Стратегия безопасного рефакторинга**

1. Покрыть God Object тестами перед любыми изменениями.
2. Выявить связные группы методов и полей (кандидаты на отдельные классы).
3. Применить Facade как «строительные леса» — реализовать делегирование.
4. Постепенно переводить клиентов на новые классы.
5. Удалить фасад и оригинальный God Object.

**Расхождения между источниками:** TheServerSide акцентирует внимание на пяти практических шагах рефакторинга с Facade как главным инструментом перехода. Refactoring.guru указывает на риск того, что сам Mediator может стать God Object, если не ограничивать его ответственность. Dev.to и SoftwarePatternLexicon делают упор на DDD-подходе с Bounded Contexts. В целом все источники сходятся: корень проблемы — нарушение SRP, а Facade является наиболее безопасным инструментом инкрементального рефакторинга.

---

### Вопрос 50. Что такое антипаттерн «Анемичная доменная модель» (Anemic Domain Model) и почему Мартин Фаулер считает его антипаттерном? Чем она отличается от правильно спроектированной доменной модели с поведением?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Anemic Domain Model — Martin Fowler's bliki](https://martinfowler.com/bliki/AnemicDomainModel.html)

Анемичная доменная модель на первый взгляд выглядит законно: она содержит объекты, названные в соответствии с доменными концепциями, с правильными связями и структурой. Однако при ближайшем рассмотрении обнаруживается критический изъян: эти объекты лишены значимого поведения и функционируют лишь как «мешки геттеров и сеттеров» (bags of getters and setters). Вся доменная логика перемещена в отдельные сервисные объекты, а классы домена остаются пустыми контейнерами данных.

**Почему Фаулер считает это антипаттерном:**

Нарушение принципов ООП: «Фундаментальный ужас этого антипаттерна состоит в том, что он противоречит базовой идее объектно-ориентированного проектирования — объединять данные и поведение вместе» (Fowler). Такой подход — это, по существу, процедурный стиль проектирования, замаскированный под объектно-ориентированный.

Ложная экономия: Паттерн «несёт все издержки доменной модели, не давая ни одного из её преимуществ». Разработчики вынуждены управлять сложным объектно-реляционным маппингом, не получая взамен организующей силы, которую предоставляет богатая доменная модель.

Подмена понятий: Вынося всё поведение в сервисы, разработчики фактически создают Transaction Scripts («Сценарии транзакций»), замаскированные под объекты, — и теряют все преимущества доменной модели.

**Важный нюанс от Фаулера:** Это не означает, что нужно переместить всю функциональность в доменную модель и полностью убрать сервисный слой. Такие задачи, как управление транзакциями и персистентность, должны находиться в отдельных компонентах, а не в доменной модели. Сервисный слой должен существовать, но оставаться тонким. «Чем больше поведения вы находите в сервисах, тем вероятнее, что вы лишаете себя преимуществ доменной модели».

#### Ответ от Claude

**Определение**

Анемичная доменная модель (Anemic Domain Model, ADM) — архитектурный антипаттерн, при котором объекты домена являются простыми контейнерами данных (полями с геттерами и сеттерами) и не содержат бизнес-логики. Вся логика — валидация, бизнес-правила, вычисления — выносится в отдельный сервисный слой, работающий поверх домена.

Термин введён Мартином Фаулером и Эриком Эвансом. Фаулер описал его в своём блики (bliki) как антипаттерн ещё в 2003 году. Эванс в книге «Domain-Driven Design» (2003) формирует концепцию богатой доменной модели как основу DDD.

**Сравнение: Анемичная vs. Богатая доменная модель**

Анемичная модель (антипаттерн):

```java
// Доменный объект — только данные
public class Order {
    private List<OrderItem> items;
    private OrderStatus status;
    private BigDecimal totalAmount;

    // только геттеры и сеттеры
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal amount) { this.totalAmount = amount; }
}

// Вся логика — в сервисе
public class OrderService {
    public void addItem(Order order, OrderItem item) {
        if (order.getStatus() != OrderStatus.DRAFT) {
            throw new IllegalStateException("Cannot add items to non-draft order");
        }
        order.getItems().add(item);
        // пересчитываем сумму вручную
        BigDecimal total = order.getItems().stream()
            .map(i -> i.getPrice().multiply(BigDecimal.valueOf(i.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        order.setTotalAmount(total);
    }

    public void confirm(Order order) {
        if (order.getItems().isEmpty()) {
            throw new IllegalStateException("Cannot confirm empty order");
        }
        order.setStatus(OrderStatus.CONFIRMED);
    }
}
```

Богатая доменная модель (правильный подход):

```java
// Доменный объект содержит и данные, и поведение
public class Order {
    private final List<OrderItem> items = new ArrayList<>();
    private OrderStatus status = OrderStatus.DRAFT;

    public void addItem(OrderItem item) {
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException("Cannot add items to non-draft order");
        }
        items.add(item);
    }

    public BigDecimal calculateTotal() {
        return items.stream()
            .map(i -> i.getPrice().multiply(BigDecimal.valueOf(i.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public void confirm() {
        if (items.isEmpty()) {
            throw new IllegalStateException("Cannot confirm empty order");
        }
        this.status = OrderStatus.CONFIRMED;
    }

    // геттеры без сеттеров — состояние меняется только через методы
    public OrderStatus getStatus() { return status; }
    public List<OrderItem> getItems() { return Collections.unmodifiableList(items); }
}

// Сервис остаётся тонким — координирует, не содержит бизнес-логики
public class OrderService {
    private final OrderRepository repository;

    public void addItem(Long orderId, OrderItem item) {
        Order order = repository.findById(orderId);
        order.addItem(item); // логика внутри Order
        repository.save(order);
    }
}
```

**Почему Фаулер считает ADM антипаттерном**

1. Противоречит ООП. Основная идея объектно-ориентированного программирования — объединение данных и поведения. ADM искусственно разрывает эту связь, фактически возвращаясь к процедурному программированию в disguise.

2. Все издержки, ноль выгоды. Разработчик платит цену за ORM-маппинг, объектный граф, управление транзакциями — но не получает взамен того, ради чего создавалась доменная модель: выразительности, инкапсуляции, защиты инвариантов.

3. Размытие знаний. Бизнес-логика распределена по многочисленным сервисам. Понять, «как работает заказ», невозможно, глядя только на класс `Order` — нужно изучать `OrderService`, `OrderValidator`, `OrderCalculator` и т.д.

4. Инварианты не защищены. Публичные сеттеры позволяют перевести объект в невалидное состояние. Логика валидации, рассеянная по сервисам, легко дублируется и рассинхронизируется.

5. По сути — Transaction Script. Фаулер указывает, что ADM — это «Сценарии транзакций» (паттерн из его же книги «Patterns of Enterprise Application Architecture»), притворяющиеся доменной моделью.

**Ключевые различия**

| Критерий | Анемичная модель | Богатая доменная модель |
|---|---|---|
| Бизнес-логика | В сервисах | В объектах домена |
| Инкапсуляция | Слабая (публичные сеттеры) | Сильная (состояние меняется через методы) |
| Защита инвариантов | На стороне сервиса | Внутри объекта |
| Сервисный слой | Толстый (содержит логику) | Тонкий (координирует) |
| Обнаруживаемость | Низкая (нужно искать логику) | Высокая (объект описывает себя) |
| Дублирование логики | Высокий риск | Минимален |

**Важный нюанс**

Фаулер не требует полного отказа от сервисного слоя. Управление транзакциями, оркестрация нескольких агрегатов, работа с внешними системами (email, очереди, файлы) — всё это правомерно находится в сервисах. Главное правило: сервис должен координировать, а не содержать бизнес-логику самих доменных объектов.

**Расхождения между источниками:** Ряд авторов (Edinburgh SAPM blog) считают ADM не антипаттерном, а вполне применимым подходом — особенно в контексте принципов SOLID (где SRP может требовать разделения данных и поведения). Фаулер и сторонники DDD с этим не согласны. Baeldung и Setronica однозначно относятся к лагерю Фаулера: ADM нарушает инкапсуляцию и размывает доменное знание. Консенсус практиков: ADM приемлем для простых CRUD-систем, но становится проблемой в сложных доменах с нетривиальными бизнес-правилами.

---

### Вопрос 51. Что такое паттерн Visitor? В чём суть механизма «двойной диспетчеризации» (double dispatch) и почему он позволяет добавлять операции без изменения классов элементов?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Visitor — refactoring.guru](https://refactoring.guru/design-patterns/visitor)

Visitor — поведенческий паттерн проектирования, позволяющий отделить алгоритмы от объектов, над которыми они работают. Это особенно полезно при работе со сложными структурами данных, когда нужно добавить новые операции без изменения классов элементов.

Ключевые участники:
- **Element** — интерфейс, объявляющий метод `accept(Visitor visitor)` для принятия посетителя.
- **ConcreteElement** — конкретные классы, реализующие `accept()`.
- **Visitor** — интерфейс с методами посещения для каждого типа элемента (`visitCircle(Circle)`, `visitRectangle(Rectangle)` и т.д.).
- **ConcreteVisitor** — конкретные реализации алгоритмов для разных элементов.

Суть double dispatch: вместо того чтобы клиент сам определял тип объекта и вызывал нужный метод, объект «принимает» посетителя через `accept()`, а внутри вызывает правильный метод посетителя: `visitor.visitCircle(this)`. Первый вызов — полиморфный `accept()` на элементе; второй — полиморфный `visitXxx()` на посетителе.

```java
shape.accept(visitor); // объект сам выбирает правильный метод посетителя
```

Паттерн позволяет добавлять неограниченное количество операций (новых ConcreteVisitor) без изменения классов элементов.

#### Ответ от Claude

**Что такое Visitor**

Visitor — поведенческий паттерн из книги GoF. Он решает задачу добавления новых операций к иерархии классов без изменения самих классов. Это особенно ценно, когда иерархия стабильна (элементы добавляются редко), но операции над ней меняются часто.

**Механизм double dispatch**

В Java метод выбирается на основе типа объекта-получателя (одиночная диспетчеризация / single dispatch). Это означает, что вызов `element.doSomething()` выбирает реализацию по типу `element`, но не по типу параметра. Visitor обходит это ограничение с помощью двух последовательных полиморфных вызовов:

1. Клиент вызывает `element.accept(visitor)` — тип `element` определяет, какой `accept()` будет вызван.
2. Внутри `accept()` элемент вызывает `visitor.visitConcreteElement(this)` — тип `visitor` определяет, какой `visitXxx()` будет вызван.

В результате метод посетителя выбирается на основе обоих типов: типа элемента и типа посетителя.

```java
// Интерфейс элемента
interface Shape {
    void accept(Visitor visitor);
}

// Конкретные элементы
class Circle implements Shape {
    double radius;
    public void accept(Visitor visitor) {
        visitor.visitCircle(this); // 2-й dispatch: тип visitor
    }
}

class Rectangle implements Shape {
    double width, height;
    public void accept(Visitor visitor) {
        visitor.visitRectangle(this);
    }
}

// Интерфейс посетителя
interface Visitor {
    void visitCircle(Circle circle);
    void visitRectangle(Rectangle rectangle);
}

// Конкретный посетитель — экспорт в XML
class XMLExportVisitor implements Visitor {
    public void visitCircle(Circle c) {
        System.out.println("<circle radius=\"" + c.radius + "\"/>");
    }
    public void visitRectangle(Rectangle r) {
        System.out.println("<rect width=\"" + r.width + "\" height=\"" + r.height + "\"/>");
    }
}

// Использование
List<Shape> shapes = List.of(new Circle(), new Rectangle());
Visitor exporter = new XMLExportVisitor();
shapes.forEach(s -> s.accept(exporter)); // 1-й dispatch: тип shape
```

**Почему операции можно добавлять без изменения элементов**

Каждая новая операция — это новый ConcreteVisitor. Классы `Circle` и `Rectangle` не меняются. Цена этого: при добавлении нового типа элемента (нового `ConcreteElement`) нужно добавить метод в интерфейс `Visitor` и реализовать его во всех конкретных посетителях. То есть паттерн хорошо масштабируется по операциям, но плохо — по типам элементов.

**Практическое применение в Java**

- Компиляторы и анализаторы кода (обход AST — Abstract Syntax Tree).
- `javax.lang.model.element.ElementVisitor` в Java Annotation Processing.
- `com.sun.source.tree.TreeVisitor` в javac.
- Сочетание с Composite: обход дерева через Iterator + применение операции через Visitor.

**Когда применять Visitor**

- Иерархия классов стабильна, но над ней нужно выполнять разнообразные независимые операции.
- Нужно избежать загромождения классов элементов несвязанными методами.
- Операции должны работать с несколькими разными классами иерархии по-разному.

---

### Вопрос 52. Как паттерн Iterator реализован в Java Collections Framework? Почему интерфейс Iterable<T> и цикл for-each являются примером паттерна Iterator, и что происходит при модификации коллекции во время итерации?

**Категория:** Паттерны · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Iterator — refactoring.guru](https://refactoring.guru/design-patterns/iterator)

Iterator — поведенческий паттерн проектирования, позволяющий обходить элементы коллекции, не раскрывая её базовую структуру (список, стек, дерево и т.д.).

Основные участники паттерна:
- **Iterator** — интерфейс, объявляющий операции обхода коллекции: получение следующего элемента (`next()`), проверка наличия элементов (`hasNext()`).
- **ConcreteIterator** — реализует конкретный алгоритм обхода, отслеживает текущую позицию независимо от других итераторов.
- **IterableCollection** — интерфейс для получения совместимых итераторов.
- **ConcreteCollection** — возвращает экземпляры конкретных классов итераторов при запросе клиента.

Паттерн следует принципу единственной ответственности: извлекая объёмные алгоритмы обхода в отдельные классы, он отделяет логику итерации от основной ответственности коллекции — эффективного хранения данных. Это позволяет поддерживать несколько независимых обходов одной коллекции одновременно.

#### Ответ от Claude

**Реализация Iterator в Java Collections Framework**

Java воплощает паттерн Iterator через два интерфейса:

- `java.util.Iterator<E>` — содержит методы `hasNext()`, `next()` и опциональный `remove()`. Соответствует роли Iterator из GoF.
- `java.lang.Iterable<T>` — объявляет единственный метод `iterator()`, возвращающий `Iterator<T>`. Соответствует роли IterableCollection из GoF. Все коллекции JCF реализуют `Iterable`.

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));

// Явное использование Iterator
Iterator<String> it = list.iterator(); // вызывает Iterable.iterator()
while (it.hasNext()) {
    String s = it.next();
    System.out.println(s);
}

// For-each — синтаксический сахар над Iterator
// Компилятор транслирует это в явный вызов iterator() + hasNext() + next()
for (String s : list) {
    System.out.println(s);
}
```

Компилятор Java транслирует `for (T x : collection)` в эквивалентный код с явным итератором. Поэтому любой класс, реализующий `Iterable<T>`, автоматически поддерживает for-each.

**Fail-fast итераторы и ConcurrentModificationException**

Итераторы большинства коллекций JCF (ArrayList, HashMap, HashSet и др.) являются **fail-fast**: при любом структурном изменении коллекции после создания итератора (добавление, удаление через коллекцию, а не через сам итератор) они выбрасывают `ConcurrentModificationException`.

Механизм: коллекция хранит счётчик структурных изменений `modCount`. При создании итератора он запоминает текущее значение `expectedModCount`. При каждом вызове `next()` сравниваются `modCount` и `expectedModCount`; если они различаются — выбрасывается `ConcurrentModificationException`.

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
for (String s : list) {
    if (s.equals("b")) {
        list.remove(s); // ConcurrentModificationException!
    }
}

// Правильно: удалять через iterator
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if (it.next().equals("b")) {
        it.remove(); // безопасно: обновляет оба счётчика
    }
}

// Или через Collection.removeIf (Java 8+)
list.removeIf(s -> s.equals("b")); // безопасно
```

Fail-fast — это соглашение, а не жёсткая гарантия: документация JDK явно указывает, что `ConcurrentModificationException` не гарантирован во всех случаях и не должен использоваться как механизм синхронизации.

**Fail-safe итераторы** (в concurrent-коллекциях) работают на снимке коллекции или без блокировки по иным алгоритмам: `CopyOnWriteArrayList`, `ConcurrentHashMap`. Они никогда не бросают `ConcurrentModificationException`, но могут не отражать изменения, сделанные после создания итератора.

**Несколько итераторов** могут существовать одновременно для одной коллекции — каждый независимо отслеживает свою позицию.

---

### Вопрос 53. Что такое паттерн Bridge? Как он разделяет «абстракцию» и «реализацию» на две независимые иерархии, и в чём его отличие от паттерна Adapter?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Bridge — refactoring.guru](https://refactoring.guru/design-patterns/bridge)

Bridge — структурный паттерн проектирования, позволяющий разделить большой класс или набор связанных классов на две отдельные иерархии: абстракцию и реализацию, которые могут развиваться независимо друг от друга.

Основные компоненты:
- **Abstraction** — высокоуровневый контрольный слой, делегирующий работу объекту реализации.
- **RefinedAbstraction** — варианты управляющей логики, расширяющие базовую абстракцию.
- **Implementation** — интерфейс, объявляющий методы, общие для всех конкретных реализаций.
- **ConcreteImplementation** — платформенно-специфичный код, реализующий интерфейс.

Ключевое отличие от Adapter: Bridge создаётся заранее (проектируется для разделения иерархий), тогда как Adapter применяется к уже существующему несовместимому коду для обеспечения совместимости. Bridge разделяет монолитный класс на две независимые иерархии; Adapter преобразует один интерфейс в другой.

#### Ответ от Claude

**Проблема, которую решает Bridge**

Без паттерна Bridge иерархия классов растёт «взрывообразно» при добавлении новых измерений изменчивости. Например, если есть фигуры (Circle, Square) и цвета (Red, Blue), наивный подход приводит к 4 классам: `RedCircle`, `BlueCircle`, `RedSquare`, `BlueSquare`. При добавлении третьего цвета нужно 2 новых класса; при добавлении третьей фигуры — ещё 3. Bridge решает это через композицию.

**Структура и пример**

```java
// Implementation — иерархия реализации (платформа/устройство)
interface Device {
    void enable();
    void disable();
    int getVolume();
    void setVolume(int percent);
}

class Tv implements Device {
    private boolean on = false;
    private int volume = 30;
    public void enable() { on = true; }
    public void disable() { on = false; }
    public int getVolume() { return volume; }
    public void setVolume(int percent) { volume = percent; }
}

class Radio implements Device {
    private boolean on = false;
    private int volume = 20;
    public void enable() { on = true; }
    public void disable() { on = false; }
    public int getVolume() { return volume; }
    public void setVolume(int percent) { volume = percent; }
}

// Abstraction — иерархия абстракции (пульты)
class RemoteControl {
    protected Device device; // мост (bridge) — ссылка на реализацию

    public RemoteControl(Device device) {
        this.device = device;
    }

    public void togglePower() {
        // не знаем, TV это или Radio — вызываем через интерфейс Device
        device.enable();
    }

    public void volumeUp() {
        device.setVolume(device.getVolume() + 10);
    }
}

// RefinedAbstraction — расширенный пульт с новыми функциями
class AdvancedRemote extends RemoteControl {
    public AdvancedRemote(Device device) { super(device); }

    public void mute() {
        device.setVolume(0);
    }
}

// Использование: любая комбинация без умножения классов
RemoteControl tvRemote = new RemoteControl(new Tv());
AdvancedRemote radioRemote = new AdvancedRemote(new Radio());
```

Теперь добавление нового устройства (Projector) требует только одного нового класса `Projector implements Device`. Добавление нового типа пульта (SmartRemote) требует только одного нового подкласса `RemoteControl`. Классы не перемножаются.

**Ключевые отличия от Adapter**

| Критерий | Bridge | Adapter |
|---|---|---|
| Цель | Разделить абстракцию и реализацию для независимого развития | Обеспечить совместимость двух несовместимых интерфейсов |
| Когда применяется | На этапе проектирования, превентивно | После написания кода, когда нужна интеграция |
| Направление | Две параллельные иерархии, разработанные вместе | Одна существующая иерархия + адаптируемый класс |
| Количество изменяемых осей | Две (абстракция и реализация) | Одна (преобразование интерфейса) |

**Реальные примеры**

- `java.util.logging.Handler` + `java.util.logging.Formatter`: `Handler` (абстракция) делегирует форматирование `Formatter` (реализация). Оба развиваются независимо.
- JDBC: `java.sql.Driver` — реализация; `java.sql.Connection` — абстракция. Клиент работает через `Connection`, не зная о конкретном драйвере (MySQL, PostgreSQL).

---

### Вопрос 54. Что такое паттерн Composite? Как он позволяет работать с деревьями объектов единообразно? Приведите пример из Java (javax.swing.JComponent или java.awt.Component).

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Composite — refactoring.guru](https://refactoring.guru/design-patterns/composite)

Composite — структурный паттерн проектирования, который позволяет компоновать объекты в древовидные структуры и работать с ними как с отдельными объектами. Паттерн имеет смысл, только когда ядро приложения может быть представлено в виде дерева.

Структура:
- **Component** — интерфейс, описывающий общие операции для простых и сложных элементов дерева.
- **Leaf** — базовый элемент дерева без подэлементов, выполняющий основную работу.
- **Composite** (Container) — элемент, содержащий подэлементы (листья или другие контейнеры), делегирующий работу подэлементам через интерфейс Component.
- **Client** — работает со всеми элементами через интерфейс Component.

Паттерн применяется, когда необходимо, чтобы клиентский код одинаково обрабатывал простые и сложные элементы.

#### Ответ от Claude

**Суть паттерна**

Composite позволяет строить деревья объектов, где каждый узел — либо «лист» (простой элемент), либо «ветвь» (контейнер, содержащий другие узлы). Ключевая идея: клиент работает с любым узлом через единый интерфейс Component — он не обязан знать, лист это или контейнер. Вызов метода на контейнере автоматически рекурсивно распространяется на все его дочерние элементы.

**Классический пример — файловая система**

```java
// Component — общий интерфейс
interface FileComponent {
    String getName();
    int getSize();
    void display(String indent);
}

// Leaf — файл (нет дочерних элементов)
class File implements FileComponent {
    private final String name;
    private final int size;

    public File(String name, int size) {
        this.name = name;
        this.size = size;
    }

    public String getName() { return name; }
    public int getSize() { return size; }
    public void display(String indent) {
        System.out.println(indent + "- " + name + " (" + size + " bytes)");
    }
}

// Composite — директория (содержит другие компоненты)
class Directory implements FileComponent {
    private final String name;
    private final List<FileComponent> children = new ArrayList<>();

    public Directory(String name) { this.name = name; }

    public void add(FileComponent component) { children.add(component); }
    public String getName() { return name; }
    public int getSize() {
        return children.stream().mapToInt(FileComponent::getSize).sum(); // рекурсия
    }
    public void display(String indent) {
        System.out.println(indent + "+ " + name + "/");
        children.forEach(c -> c.display(indent + "  ")); // рекурсия
    }
}

// Клиент работает через Component — не знает, Directory или File
FileComponent root = new Directory("root");
Directory src = new Directory("src");
src.add(new File("Main.java", 1024));
src.add(new File("Utils.java", 512));
root.add(src);
root.add(new File("pom.xml", 256));

root.display(""); // выводит всё дерево
System.out.println(root.getSize()); // 1792 (рекурсивная сумма)
```

**Пример из Java — java.awt.Component и javax.swing.JComponent**

`java.awt.Container extends Component` — классический Composite в AWT/Swing:
- `Component` — роль Component (общий интерфейс для всех элементов GUI).
- `Button`, `Label`, `TextField` — роль Leaf (не содержат дочерних элементов).
- `Container` (и его подклассы: `Panel`, `Frame`, `JPanel`, `JFrame`) — роль Composite: содержит список `Component`-ов, методы `add(Component)` / `remove(Component)`, а `paint()` рекурсивно вызывает `paint()` у всех дочерних компонентов.

`javax.swing.JComponent extends Container` — поэтому каждый Swing-виджет одновременно является и Component (может быть дочерним), и Composite (может содержать дочерние).

**Когда применять Composite**

- Данные образуют иерархическую (древовидную) структуру: файловые системы, UI-дерево, XML/HTML-документы, структура заказа (товар vs. набор товаров).
- Клиент должен одинаково обращаться с отдельными объектами и с их группами.

**Расхождений между источниками нет:** refactoring.guru и GoF описывают паттерн идентично. Практическое замечание: в некоторых реализациях методы управления дочерними элементами (`add`, `remove`) объявлены в `Component`, что упрощает работу с деревом, но нарушает принцип единственной ответственности для листьев (Leaf-объектам приходится реализовывать методы, которые им не нужны, например бросать `UnsupportedOperationException`).

---

### Вопрос 55. Что такое паттерн Mediator? Чем он отличается от Observer, и какую роль играет Spring MVC DispatcherServlet как пример медиатора?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Mediator — refactoring.guru](https://refactoring.guru/design-patterns/mediator)

Mediator — поведенческий паттерн проектирования, который позволяет снизить хаотичные зависимости между объектами. Паттерн принуждает компоненты взаимодействовать косвенно через объект-посредник вместо прямого обмена данными.

Основные участники:
- **Mediator (интерфейс)** — объявляет методы коммуникации с компонентами. Интерфейс критически важен, когда требуется переиспользовать классы компонентов в разных контекстах.
- **ConcreteMediator** — инкапсулирует отношения между компонентами, хранит ссылки на управляемые элементы и координирует их взаимодействие.
- **Component** — содержит бизнес-логику, имеет ссылку на объект-посредник. Компоненты уведомляют медиатора о событиях вместо прямого взаимодействия друг с другом.

Ключевое различие с Observer: Mediator **централизует общение** между компонентами через единый объект, тогда как Observer устанавливает **динамические односторонние связи** между издателем и подписчиками. Mediator исключает взаимные зависимости; Observer позволяет динамическую подписку.

#### Ответ от Claude

**Что такое Mediator**

Mediator («Посредник») — поведенческий паттерн, который устраняет прямые зависимости между компонентами системы, направляя всё их взаимодействие через единый объект-посредник. Без медиатора N компонентов могут иметь N×(N-1) связей; с медиатором — только N связей (каждый знает только о посреднике).

**Пример — UI-диалог**

```java
interface Mediator {
    void notify(Component sender, String event);
}

// Конкретный медиатор — управляет диалогом
class AuthenticationDialog implements Mediator {
    private TextField loginField;
    private CheckBox guestCheckBox;
    private Button loginButton;

    public void notify(Component sender, String event) {
        if (sender == guestCheckBox && event.equals("check")) {
            // если выбран гость — отключаем поле логина
            loginField.setEnabled(!guestCheckBox.isChecked());
        }
        if (sender == loginButton && event.equals("click")) {
            // медиатор знает, как провалидировать форму
            String login = loginField.getText();
            // ...
        }
    }
}

// Компонент — знает только о медиаторе
class CheckBox extends Component {
    private Mediator mediator;
    private boolean checked;

    public void setChecked(boolean checked) {
        this.checked = checked;
        mediator.notify(this, "check"); // не знает о других компонентах
    }

    public boolean isChecked() { return checked; }
}
```

**Mediator vs Observer**

| Критерий | Mediator | Observer |
|---|---|---|
| Направление связи | Все компоненты → один Mediator | Один Publisher → многие Subscriber |
| Знание об участниках | Mediator знает всех, компоненты — только медиатора | Subscriber не знает о других Subscriber |
| Характер взаимодействия | Многие-ко-многим через посредника | Один-ко-многим |
| Добавление компонента | Нужно обновить медиатор | Просто подписать |
| Риск «God Object» | Медиатор может разрастись | Издатель остаётся простым |

**Spring MVC DispatcherServlet как медиатор**

`DispatcherServlet` в Spring MVC — классический пример паттерна Mediator:
- Получает HTTP-запрос от контейнера сервлетов.
- Делегирует определение обработчика `HandlerMapping` (не знает о конкретных контроллерах).
- Вызывает найденный `HandlerAdapter`, который адаптирует конкретный контроллер.
- Получает `ModelAndView`, передаёт его `ViewResolver`.
- Контроллер, ViewResolver и HandlerMapping не знают друг о друге — все взаимодействуют только через `DispatcherServlet`.

Таким образом, DispatcherServlet централизует весь поток обработки запроса, устраняя прямые зависимости между компонентами Spring MVC.

**Когда применять Mediator**

- Компоненты тесно связаны: изменение одного требует изменений других.
- Нельзя переиспользовать компонент отдельно, потому что он зависит от других.
- Логика взаимодействия сложна и разбросана по множеству классов.

Предостережение (refactoring.guru): со временем медиатор сам может стать God Object. Нужно следить, чтобы он занимался только координацией, не содержа бизнес-логику компонентов.

---

### Вопрос 56. Что такое паттерн Interpreter? Где он применяется в Java-экосистеме (java.util.Pattern, SpEL, JPQL)? Чем AST связан с паттернами Composite и Interpreter?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Interpreter Design Pattern in Java — Baeldung](https://www.baeldung.com/java-interpreter-pattern)

Паттерн Interpreter определяет грамматику конкретного языка объектно-ориентированным способом, который может быть оценён интерпретатором.

Структура:
- **AbstractExpression** — базовый интерфейс, определяющий метод `interpret(Context ctx)`, принимающий контекст и влияющий на его состояние.
- **TerminalExpression** — завершающее выражение, которое возвращает результат и завершает процесс интерпретации без дальнейшей обработки.
- **NonTerminalExpression** — промежуточное выражение, которое может содержать одно или более других выражений и рекурсивно интерпретироваться. Является композитным паттерном.
- **Context** — контейнер глобального состояния обработки, переиспользуемый на протяжении всего процесса интерпретации.

Паттерн применяется для относительно простой грамматики, которая не требует постоянного расширения. При усложнении грамматики поддерживать код становится сложнее. Паттерн используется в JDK в `java.util.Pattern`, `java.text.Format` и `java.text.Normalizer`.

#### Ответ от Claude

**Что такое Interpreter**

Interpreter («Интерпретатор») — поведенческий паттерн из книги GoF, предназначенный для интерпретации предложений некоторого языка. Паттерн предлагает строить абстрактное синтаксическое дерево (AST — Abstract Syntax Tree) из объектов-выражений и затем вычислять его.

**Минимальный пример — булево выражение**

```java
// AbstractExpression
interface Expression {
    boolean interpret(Map<String, Boolean> context);
}

// TerminalExpression — переменная
class Variable implements Expression {
    private final String name;
    public Variable(String name) { this.name = name; }

    public boolean interpret(Map<String, Boolean> context) {
        return context.getOrDefault(name, false);
    }
}

// NonTerminalExpression — AND
class AndExpression implements Expression {
    private final Expression left, right;
    public AndExpression(Expression left, Expression right) {
        this.left = left;
        this.right = right;
    }

    public boolean interpret(Map<String, Boolean> context) {
        return left.interpret(context) && right.interpret(context); // рекурсия
    }
}

// NonTerminalExpression — NOT
class NotExpression implements Expression {
    private final Expression expr;
    public NotExpression(Expression expr) { this.expr = expr; }

    public boolean interpret(Map<String, Boolean> context) {
        return !expr.interpret(context);
    }
}

// Построение AST и вычисление: (A AND (NOT B))
Expression exp = new AndExpression(
    new Variable("A"),
    new NotExpression(new Variable("B"))
);

Map<String, Boolean> ctx = Map.of("A", true, "B", false);
System.out.println(exp.interpret(ctx)); // true
```

**Связь AST с паттернами Composite и Interpreter**

AST — это дерево, в котором каждый узел является либо терминальным (листом), либо нетерминальным (ветвью с дочерними узлами). Это в точности структура паттерна Composite:
- `TerminalExpression` — роль Leaf из Composite.
- `NonTerminalExpression` — роль Composite (содержит другие Expression).
- Метод `interpret(Context)` — это операция, применяемая рекурсивно ко всему дереву.

Таким образом, Interpreter — это специализированный Composite, в котором рекурсивная операция называется «интерпретацией», а контекст передаётся через дерево.

**Применение в Java-экосистеме**

- **`java.util.Pattern`** — регулярные выражения: паттерн парсит строку-регулярку и строит внутреннее AST из узлов (CharProperty, Loop, Branch и т.д.), которые затем интерпретируются при вызове `Matcher.matches()`.
- **Spring Expression Language (SpEL)** — `ExpressionParser` разбирает строковое выражение в AST (`SpelExpression`), которое вычисляется через `evaluate(EvaluationContext)`.
- **JPQL/HQL** — Hibernate/EclipseLink парсят строки запросов в AST, которое затем транслируется в SQL.
- **`javax.el` (EL в JSP/JSF)** — Unified Expression Language: `ExpressionFactory` строит AST из EL-выражений.

**Когда применять Interpreter, а когда нет**

Interpreter подходит для простых, стабильных грамматик. При сложных или часто меняющихся грамматиках паттерн становится тяжёлым: добавление новой грамматической конструкции требует нового класса-выражения и изменений в клиентском коде, строящем AST. В таких случаях предпочтительнее использовать генераторы парсеров (ANTLR, JavaCC) или библиотеки (Calcite для SQL).

---

### Вопрос 57. Почему для расширения поведения объектов предпочтительнее использовать Decorator вместо наследования? В чём проблема «взрыва подклассов», и как Decorator её решает?

**Категория:** Паттерны · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Decorator — refactoring.guru](https://refactoring.guru/design-patterns/decorator)

Decorator — структурный паттерн проектирования, позволяющий присоединять новые обязанности к объектам, помещая их внутри специальных объектов-оболочек.

Наследование имеет существенные ограничения:
- **Статичность** — невозможно менять поведение объекта во время выполнения программы.
- **Единственный родитель** — класс не может наследовать поведение от нескольких классов одновременно (в Java нет множественного наследования).

Decorator решает эти проблемы через **композицию**: вместо расширения класса новый функционал оборачивается вокруг исходного объекта, позволяя комбинировать различные поведения динамически.

Структура:
- **Component** — интерфейс для обёрток и оборачиваемых объектов.
- **ConcreteComponent** — класс с базовым поведением.
- **BaseDecorator** — хранит ссылку на оборачиваемый объект, делегирует ему операции.
- **ConcreteDecorators** — добавляют дополнительное поведение до или после вызова родительского метода.

#### Ответ от Claude

**Проблема «взрыва подклассов» при наследовании**

Предположим, есть уведомитель (`Notifier`) и нужно поддержать несколько каналов: Email, SMS, Slack. При наследовании:

```
Notifier
├── EmailNotifier
├── SMSNotifier
├── SlackNotifier
├── EmailAndSMSNotifier
├── EmailAndSlackNotifier
├── SMSAndSlackNotifier
└── EmailAndSMSAndSlackNotifier
```

7 классов для 3 каналов. При 4 каналах — 15 классов. При N каналах — 2^N - 1 классов. Это и есть «взрыв подклассов». Кроме того, добавить или убрать канал для конкретного объекта в runtime невозможно — классы статичны.

**Decorator устраняет эту проблему**

```java
// Component
interface Notifier {
    void send(String message);
}

// ConcreteComponent — базовый уведомитель (Email)
class EmailNotifier implements Notifier {
    private final String email;
    public EmailNotifier(String email) { this.email = email; }
    public void send(String message) {
        System.out.println("Email to " + email + ": " + message);
    }
}

// BaseDecorator — абстрактная обёртка
abstract class NotifierDecorator implements Notifier {
    protected final Notifier wrapped;
    public NotifierDecorator(Notifier wrapped) { this.wrapped = wrapped; }
    public void send(String message) { wrapped.send(message); } // делегирование
}

// ConcreteDecorators — добавляют каналы
class SMSDecorator extends NotifierDecorator {
    private final String phone;
    public SMSDecorator(Notifier wrapped, String phone) {
        super(wrapped);
        this.phone = phone;
    }
    public void send(String message) {
        super.send(message);
        System.out.println("SMS to " + phone + ": " + message);
    }
}

class SlackDecorator extends NotifierDecorator {
    private final String channel;
    public SlackDecorator(Notifier wrapped, String channel) {
        super(wrapped);
        this.channel = channel;
    }
    public void send(String message) {
        super.send(message);
        System.out.println("Slack #" + channel + ": " + message);
    }
}

// Использование — комбинируем в runtime через оборачивание
Notifier notifier = new EmailNotifier("admin@example.com");
notifier = new SMSDecorator(notifier, "+7-999-000-0000");
notifier = new SlackDecorator(notifier, "alerts");

notifier.send("Server is down!"); // отправит во все три канала
```

3 декоратора вместо 7 классов наследования. Новый канал — один новый `ConcreteDecorator`. Комбинации собираются динамически в рантайме.

**Когда наследование лучше**

Decorator избыточен, когда:
- Есть единственная, заранее известная вариация поведения — один подкласс проще одного декоратора.
- Нужен доступ к полям базового класса, которые не доступны через интерфейс Component.
- Нужна работа с конкретным типом, а не с интерфейсом (декоратор скрывает конкретный тип).

**Примеры в JDK**

`java.io.FilterInputStream` — базовый декоратор для потоков:
- `BufferedInputStream` — добавляет буферизацию.
- `DataInputStream` — добавляет чтение примитивов.
- `GZIPInputStream` — добавляет распаковку.

Можно вкладывать произвольно: `new DataInputStream(new BufferedInputStream(new FileInputStream("data.bin")))`.

---

### Вопрос 58. Что такое паттерн Specification в контексте DDD? Как он реализован в Spring Data JPA через интерфейс Specification<T>, и чем это лучше, чем написание JPQL-запросов вручную?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [REST Query Language with Spring Data JPA Specifications — Baeldung](https://www.baeldung.com/rest-api-search-language-spring-data-specifications)

Specification — паттерн проектирования, позволяющий инкапсулировать бизнес-правила и критерии, которым объект должен соответствовать. В Spring Data JPA это интерфейс, используемый для создания сложных критериев поиска и фильтрации сущностей.

Основной метод интерфейса `Specification<T>`:

```java
public Predicate toPredicate(Root<T> root, CriteriaQuery<?> query,
  CriteriaBuilder builder)
```

Параметры: `Root<T>` — корневая сущность; `CriteriaQuery<?>` — объект критерия запроса; `CriteriaBuilder` — построитель условий.

Репозиторий должен расширять `JpaSpecificationExecutor<T>`:

```java
public interface UserRepository
  extends JpaRepository<User, Long>,
  JpaSpecificationExecutor<User> {}
```

Это позволяет использовать метод `findAll(Specification<T>)` для выполнения специализированных запросов с динамическими критериями фильтрации.

#### Ответ от Claude

**Паттерн Specification в DDD**

Specification — паттерн из книги Эрика Эванса и Мартина Фаулера, предназначенный для инкапсуляции бизнес-правил в отдельные объекты. Спецификация проверяет, удовлетворяет ли объект некоторому критерию (`isSatisfiedBy(T candidate): boolean`). Спецификации можно комбинировать через `and()`, `or()`, `not()` — это позволяет декларативно выражать сложные бизнес-правила.

**Реализация в Spring Data JPA**

Spring Data JPA адаптирует паттерн для работы с JPA Criteria API. `Specification<T>` — функциональный интерфейс, создающий `javax.persistence.criteria.Predicate`.

```java
// Спецификация для поиска активных пользователей с именем
public class UserSpecifications {

    public static Specification<User> hasFirstName(String firstName) {
        return (root, query, builder) ->
            builder.equal(root.get("firstName"), firstName);
    }

    public static Specification<User> isActive() {
        return (root, query, builder) ->
            builder.isTrue(root.get("active"));
    }

    public static Specification<User> olderThan(int age) {
        return (root, query, builder) ->
            builder.greaterThan(root.get("age"), age);
    }
}

// Репозиторий
public interface UserRepository extends JpaRepository<User, Long>,
    JpaSpecificationExecutor<User> {}

// Использование — комбинирование через and/or
Specification<User> spec = UserSpecifications.isActive()
    .and(UserSpecifications.hasFirstName("Ivan"))
    .and(UserSpecifications.olderThan(18));

List<User> users = userRepository.findAll(spec);
```

**Почему Specification лучше JPQL-запросов вручную**

| Критерий | JPQL / Native SQL строкой | Specification |
|---|---|---|
| Безопасность типов | Нет: ошибки обнаруживаются в runtime | Да: ошибки в атрибутах — в compile-time |
| Динамические условия | Сложно: конкатенация строк | Легко: `and()`, `or()`, условное добавление |
| Тестируемость | Сложно: нужна БД или mock | Легко: Specification — обычный объект, можно тестировать |
| Переиспользование | Дублирование SQL-фрагментов | Спецификации — самостоятельные объекты, переиспользуются |
| Поддержка | SQL-инъекции при ручной конкатенации | Параметры — безопасны по определению |
| Читаемость | Запросы в строках | Декларативный код: `isActive().and(olderThan(18))` |

**Расхождения между источниками:** Baeldung и java-design-patterns.com рекомендуют Specification как мощный инструмент. Ряд авторов (Vlad Mihalcea) указывает, что `JpaSpecificationExecutor` с Criteria API — многословен для простых случаев: JPQL через `@Query` или даже Querydsl удобнее. Для динамических фильтров REST API Specification остаётся наиболее идиоматичным решением в Spring.

---

### Вопрос 59. Что такое паттерн CQRS (Command Query Responsibility Segregation)? В чём суть разделения на Command- и Query-сторону, и как он реализован в Spring через Axon Framework?

**Категория:** Паттерны · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [CQRS and Event Sourcing in Java — Baeldung](https://www.baeldung.com/cqrs-event-sourcing-java)

CQRS (Command Query Responsibility Segregation) — архитектурный паттерн, основанный на принципе разделения операций на две категории:
- **Команды** — операции, которые изменяют состояние системы, но не обязательно возвращают значение.
- **Запросы** — операции, которые возвращают результат и не изменяют видимое состояние системы.

Паттерн позволяет создавать отдельные доменные модели, оптимизированные под конкретные операции: высокая пропускная способность для записи, низкая задержка для чтения. Репозитории для чтения и записи могут различаться.

```java
// Команда создания пользователя (изменяет состояние, не возвращает данные)
public class CreateUserCommand {
    private String userId;
    private String firstName;
    private String lastName;
}

// Запрос (не изменяет состояние, возвращает данные)
public class ContactByTypeQuery {
    private String userId;
    private String contactType;
}
```

#### Ответ от Claude

**Суть паттерна CQRS**

CQRS — архитектурный паттерн, сформулированный Грегом Янгом на основе принципа CQS (Command-Query Separation) Бертрана Мейера. CQS утверждает, что метод должен либо выполнять действие (команда), либо возвращать данные (запрос) — но не оба действия одновременно. CQRS поднимает эту идею на уровень архитектуры: Command- и Query-стороны получают разные модели данных, разные репозитории и, при необходимости, разные базы данных.

**Ключевое разделение**

```
Запрос (HTTP)
    ├── Command (POST/PUT/DELETE)
    │       ↓
    │   CommandHandler (изменяет агрегат, сохраняет события)
    │       ↓
    │   Write Model / EventStore
    │
    └── Query (GET)
            ↓
        QueryHandler (читает из оптимизированного read-хранилища)
            ↓
        Read Model / Projection (денормализованный вид для быстрого чтения)
```

**Реализация с Axon Framework**

Axon Framework — Java-фреймворк для CQRS и Event Sourcing. Аннотации определяют роль метода:

```java
// Агрегат — обрабатывает команды и порождает события
@Aggregate
public class UserAggregate {

    @AggregateIdentifier
    private String userId;
    private String name;

    @CommandHandler
    public UserAggregate(CreateUserCommand command) {
        // применяем событие — не меняем состояние напрямую
        AggregateLifecycle.apply(
            new UserCreatedEvent(command.getUserId(), command.getName())
        );
    }

    @EventSourcingHandler
    public void on(UserCreatedEvent event) {
        this.userId = event.getUserId();
        this.name = event.getName();
    }
}

// Query-сторона — проекция для чтения
@Component
public class UserProjection {

    private final UserReadRepository readRepository;

    @EventHandler
    public void on(UserCreatedEvent event) {
        // обновляем read-модель при получении события
        readRepository.save(new UserView(event.getUserId(), event.getName()));
    }

    @QueryHandler
    public UserView handle(FindUserQuery query) {
        return readRepository.findById(query.getUserId());
    }
}
```

**Преимущества CQRS**

- Write и Read модели оптимизированы независимо: write — нормализованная БД, read — денормализованные проекции для быстрых запросов.
- Write-сторона может масштабироваться отдельно от Read-стороны.
- Read-модели могут иметь разные форматы (SQL, Redis, Elasticsearch) для разных типов запросов.
- В сочетании с Event Sourcing — полная история изменений и возможность «перемотки».

**Недостатки и когда не использовать**

- Eventual consistency: запрос после команды может вернуть устаревшие данные (синхронизация read/write задержана).
- Значительная сложность инфраструктуры: два хранилища, обработчики событий, обработка ошибок синхронизации.
- CQRS оправдан только для сложных доменов с высокой нагрузкой. Для простых CRUD-приложений это избыточно.

**Расхождение источников:** Baeldung описывает базовую реализацию без Axon. Axon документация показывает полный Event Sourcing. Мартин Фаулер в своём bliki предупреждает: CQRS подходит только для части системы, где это реально нужно, и не должен применяться повсеместно.

---

### Вопрос 60. Паттерн Null Object: в чём его суть, как он устраняет проверки на null, и чем он отличается от Optional<T> в Java 8+?

**Категория:** Паттерны · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Introduce Null Object — refactoring.guru](https://refactoring.guru/introduce-null-object)

Вместо возврата `null` следует возвращать null-объект, демонстрирующий поведение по умолчанию. Ключевая цель использования null-объекта — избегать условных операторов разных видов, что приводит к коду, более сфокусированному и быстрому для чтения и понимания — то есть к улучшению читаемости.

Null-объект реализует тот же интерфейс, что и реальный объект, но методы выполняют нулевую или нейтральную операцию. Это означает, что клиентский код может использовать null-объект так же, как реальный объект, без каких-либо проверок на `null`.

#### Ответ от Claude

**Что такое Null Object**

Null Object — поведенческий паттерн (иногда называемый идиомой), предлагающий заменить `null`-ссылки объектами, реализующими тот же интерфейс, что и реальные объекты, но с «пустой» или нейтральной реализацией методов. Клиентский код перестаёт проверять `null` — он просто вызывает методы, и если объект является Null Object, вызов «ничего не делает» или возвращает нейтральное значение.

**Пример — логирование**

```java
// Интерфейс
interface Logger {
    void log(String message);
    void error(String message);
}

// Реальный логгер
class ConsoleLogger implements Logger {
    public void log(String message) { System.out.println("[INFO] " + message); }
    public void error(String message) { System.err.println("[ERROR] " + message); }
}

// Null Object — «пустой» логгер, делает ничего
class NullLogger implements Logger {
    public void log(String message) {}   // нейтральная реализация
    public void error(String message) {} // нейтральная реализация
}

// Клиент — без единой проверки на null
class OrderService {
    private final Logger logger;

    public OrderService(Logger logger) {
        this.logger = logger; // может быть NullLogger — клиент не знает
    }

    public void placeOrder(Order order) {
        logger.log("Placing order: " + order.getId()); // безопасно всегда
        // бизнес-логика...
        logger.log("Order placed successfully");
    }
}

// Использование
OrderService prodService = new OrderService(new ConsoleLogger());
OrderService testService = new OrderService(new NullLogger()); // в тестах — без вывода
```

**Отличие Null Object от Optional\<T\>**

| Критерий | Null Object | Optional\<T\> |
|---|---|---|
| Суть | Реализует интерфейс, предоставляет нейтральное поведение | Контейнер для значения, которое может отсутствовать |
| Устраняет | Проверки `if (obj != null)` перед вызовом методов | Проверки `if (result != null)` после получения результата |
| Вызов методов | Вызываются напрямую — Null Object обрабатывает их нейтрально | Нельзя: нужно `optional.ifPresent(...)` или `optional.get()` |
| Где хранится | В полях объектов, как обычная зависимость | В возвращаемых значениях методов |
| Полиморфизм | Да: клиент работает через интерфейс | Нет: обёртка не реализует интерфейс значения |
| Типичное применение | Зависимости (логгер, слушатель событий) | Возвращаемые значения: результат поиска, парсинг |

**Когда применять Null Object**

- Зависимость (стратегия, слушатель, логгер) может быть не задана, и в этом случае нужно нейтральное поведение.
- Клиент не должен знать об отсутствии объекта.
- Хочется избавиться от множества проверок `if (logger != null) logger.log(...)`.

**Когда применять Optional**

- Метод может не найти результат (поиск по ключу, парсинг).
- Нужно явно сигнализировать о возможном отсутствии значения в сигнатуре метода.
- `Optional` — это соглашение для API: «этот метод может вернуть пустоту».

**Ограничения Null Object:** нейтральное поведение не всегда возможно. Если метод возвращает `int`, что вернуть в Null Object? 0? -1? Это создаёт неоднозначность. В таких случаях `Optional` или специальный тип-результат (`Result<T>`) предпочтительнее.
