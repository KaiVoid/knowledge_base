# Урок 9. Написание обработчиков событий

**Трейл:** Creating a GUI with Swing · **Оригинал:** [Writing Event Listeners](https://docs.oracle.com/javase/tutorial/uiswing/events/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок собран из страниц
> раздела *Writing Event Listeners*: введение, общая информация, таблица слушателей по компонентам,
> страницы «How to Write a … Listener» (Action, Caret, Change, Component, Container, Document, Focus,
> Item, Key, List Selection, Mouse, Mouse-Motion, Mouse-Wheel, Property Change, Window),
> итоговая таблица Listener API и раздел решения типичных проблем. Полный перечень источников —
> в конце файла.

Этот урок подробно объясняет, как писать обработчики событий (*event listeners*). Возможно, читать
этот раздел целиком вам и не понадобится: первым источником информации о событиях должен служить
раздел «How to» для конкретного компонента — там показан код обработки самых частых для этого
компонента событий. Например, страница [How to Use Check Boxes](https://docs.oracle.com/javase/tutorial/uiswing/components/button.html#checkbox)
показывает обработку щелчков мышью по флажкам через слушатель элементов (*item listener*).

Если вы хотите строить GUI на JavaFX, см. [Handling JavaFX Events](https://docs.oracle.com/javase/8/javafx/events-tutorial/events.htm).

## Введение в обработчики событий

Если вы читали какую-нибудь из страниц «How to» по компонентам, основы обработчиков событий вам
уже знакомы.

### Простой пример: «бипер»

Пример **Beeper** содержит кнопку, которая издаёт звуковой сигнал при щелчке. Вот код, реализующий
обработку события кнопки:

```java
public class Beeper ... implements ActionListener {
    ...
    // там, где происходит инициализация:
        button.addActionListener(this);
    ...
    public void actionPerformed(ActionEvent e) {
        ...// Издать звуковой сигнал...
    }
}
```

Класс `Beeper` реализует интерфейс `ActionListener`, в котором всего один метод — `actionPerformed`.
Поскольку `Beeper` реализует `ActionListener`, объект `Beeper` может зарегистрироваться слушателем
событий-действий (*action events*), которые порождают кнопки. После регистрации с помощью метода
кнопки `addActionListener` метод `actionPerformed` объекта `Beeper` вызывается при каждом щелчке по
кнопке.

### Более сложный пример

Модель событий мощная и гибкая. Любое число объектов-слушателей может слушать любые виды событий
от любого числа объектов-источников. Например:

- программа может создавать по одному слушателю на каждый источник событий;
- программа может иметь единственного слушателя для всех событий от всех источников;
- программа может иметь более одного слушателя для одного вида событий от одного источника.

Несколько слушателей могут зарегистрироваться, чтобы получать уведомления о событиях определённого
типа от определённого источника. Один и тот же слушатель может слушать уведомления от разных объектов.

Каждое событие представлено объектом, который сообщает информацию о событии и идентифицирует его
источник. Источниками часто являются компоненты или модели, но ими могут быть и другие объекты.

Пример **MultiListener** показывает, что слушателей событий можно регистрировать на нескольких объектах
и что одно и то же событие может рассылаться нескольким слушателям. В примере два источника событий
(экземпляры `JButton`) и два слушателя:

```java
public class MultiListener ... implements ActionListener {
    ...
    // там, где происходит инициализация:
        button1.addActionListener(this);
        button2.addActionListener(this);

        button2.addActionListener(new Eavesdropper(bottomTextArea));
    }

    public void actionPerformed(ActionEvent e) {
        topTextArea.append(e.getActionCommand() + newline);
    }
}

class Eavesdropper implements ActionListener {
    ...
    public void actionPerformed(ActionEvent e) {
        myTextArea.append(e.getActionCommand() + newline);
    }
}
```

Один слушатель (`MultiListener`) слушает события от обеих кнопок. Получив событие, он добавляет
«команду действия» события (*action command*, которая равна тексту на ярлыке кнопки) в верхнюю
текстовую область. Второй слушатель (`Eavesdropper`) слушает события только одной кнопки и добавляет
команду действия в нижнюю текстовую область. Оба класса реализуют интерфейс `ActionListener` и
регистрируются методом `addActionListener`.

## Общая информация о написании обработчиков событий

### Соображения по проектированию

Самое важное правило: обработчики событий должны **выполняться очень быстро**. Поскольку всё
рисование и прослушивание событий выполняется в одном и том же потоке (*thread*), медленный метод
слушателя делает программу неотзывчивой и медленной в перерисовке. Если в ответ на событие нужно
выполнить длительную операцию, запустите для неё отдельный поток (или каким-то образом отправьте
запрос другому потоку). См. [Concurrency in Swing](https://docs.oracle.com/javase/tutorial/uiswing/concurrency/index.html).

Способов реализовать слушателя много, и единого рекомендуемого подхода нет — одно решение не
подходит для всех ситуаций. Несколько подсказок:

- можно реализовать отдельные классы для разных видов слушателей — это легко сопровождать, но много
  классов может снижать производительность;
- слушателей можно делать не публичными, а более «скрытыми»: приватная реализация безопаснее;
- для очень простого слушателя иногда можно вообще обойтись без отдельного класса, применив класс
  `EventHandler`.

### Получение информации о событии: объекты событий

Каждый метод слушателя получает **единственный аргумент** — объект, унаследованный от класса
[`EventObject`](https://docs.oracle.com/javase/8/docs/api/java/util/EventObject.html). Хотя аргумент
всегда происходит от `EventObject`, его тип обычно указан точнее. Например, аргумент методов обработки
событий мыши — экземпляр `MouseEvent` (косвенный подкласс `EventObject`).

Класс `EventObject` определяет один очень полезный метод:

| Метод | Назначение |
|-------|------------|
| `Object getSource()` | Возвращает объект, породивший событие. |

Обратите внимание: `getSource` возвращает `Object`. Классы событий иногда определяют методы, похожие
на `getSource`, но с более узким типом возврата. Например, класс `ComponentEvent` определяет метод
`getComponent`, который, как и `getSource`, возвращает источник события, но всегда типа `Component`.
На каждой странице «How to» указано, использовать `getSource` или другой метод. Часто класс события
определяет методы, возвращающие информацию о событии: у `MouseEvent` можно узнать, где произошло
событие, сколько было щелчков, какие клавиши-модификаторы были нажаты, и т. д.

### Низкоуровневые и семантические события

События делятся на две группы: **низкоуровневые** (*low-level*) и **семантические** (*semantic*).
Низкоуровневые представляют события оконной системы или низкоуровневый ввод; всё остальное —
семантические события.

Примеры низкоуровневых событий — события мыши и клавиатуры (прямой результат пользовательского
ввода). Примеры семантических — события-действия (*action*) и события элементов (*item*). Семантическое
событие может запускаться пользовательским вводом (кнопка порождает action-событие при щелчке, текстовое
поле — при нажатии *Enter*), но не обязательно: событие модели таблицы может породиться, когда модель
получит новые данные из базы данных.

**По возможности слушайте семантические события, а не низкоуровневые.** Так код будет надёжнее и
переносимее. Например, слушая action-события на кнопках, а не события мыши, вы получаете правильную
реакцию и при активации кнопки с клавиатуры, и при специфичном для внешнего вида жесте. Для составных
компонентов (например, комбинированного списка) семантические события обязательны: нет надёжного
способа зарегистрировать слушателей на все зависящие от look-and-feel внутренние компоненты.

### Адаптеры событий

Некоторые интерфейсы-слушатели содержат больше одного метода. Например, `MouseListener` содержит пять:
`mousePressed`, `mouseReleased`, `mouseEntered`, `mouseExited`, `mouseClicked`. Даже если вам интересны
только щелчки, при прямой реализации `MouseListener` нужно реализовать все пять методов (ненужные — с
пустым телом):

```java
// Пример, реализующий интерфейс-слушатель напрямую.
public class MyClass implements MouseListener {
    ...
        someObject.addMouseListener(this);
    ...
    /* Пустое определение метода. */
    public void mousePressed(MouseEvent e) {
    }

    /* Пустое определение метода. */
    public void mouseReleased(MouseEvent e) {
    }

    /* Пустое определение метода. */
    public void mouseEntered(MouseEvent e) {
    }

    /* Пустое определение метода. */
    public void mouseExited(MouseEvent e) {
    }

    public void mouseClicked(MouseEvent e) {
        ...// Здесь реализация слушателя...
    }
}
```

Множество пустых тел методов ухудшает читаемость и сопровождение кода. Чтобы этого избежать, API
обычно включает **класс-адаптер** (*adapter*) для каждого интерфейса-слушателя с более чем одним
методом (см. [таблицу Listener API](#итоговая-таблица-listener-api)). Например, класс `MouseAdapter`
реализует интерфейс `MouseListener`. Адаптер реализует пустые версии всех методов интерфейса. Чтобы
им воспользоваться, создают подкласс и переопределяют только нужные методы:

```java
/*
 * Пример наследования от класса-адаптера вместо
 * прямой реализации интерфейса-слушателя.
 */
public class MyClass extends MouseAdapter {
    ...
        someObject.addMouseListener(this);
    ...
    public void mouseClicked(MouseEvent e) {
        ...// Здесь реализация слушателя...
    }
}
```

### Внутренние и анонимные внутренние классы

А если адаптер нужен, но вы не хотите, чтобы ваш публичный класс наследовался от адаптера? Например,
вы пишете апплет и хотите, чтобы ваш подкласс `Applet` содержал обработку событий мыши. Множественного
наследования в Java нет, поэтому класс не может наследоваться одновременно от `Applet` и `MouseAdapter`.
Решение — **внутренний класс** (*inner class*) внутри подкласса `Applet`, наследующий `MouseAdapter`.
Внутренние классы полезны и для слушателей, реализующих один или несколько интерфейсов напрямую.

```java
// Пример использования внутреннего класса.
public class MyClass extends Applet {
    ...
        someObject.addMouseListener(new MyAdapter());
    ...
    class MyAdapter extends MouseAdapter {
        public void mouseClicked(MouseEvent e) {
            ...// Здесь реализация слушателя...
        }
    }
}
```

**Замечание о производительности.** Время старта приложения и объём памяти обычно прямо пропорциональны
числу загружаемых классов. Чем больше классов вы создаёте, тем дольше старт и больше памяти. Баланс с
прочими ограничениями проектирования — за вами; превращать приложение в один монолитный класс ради
старта и памяти не нужно — это лишь добавит головной боли и затруднит сопровождение.

Внутренний класс можно создать без имени — это **анонимный внутренний класс** (*anonymous inner class*).
Поначалу это выглядит странно, но такой класс делает код читабельнее, ведь класс определяется там же,
где используется. Удобство нужно взвешивать с возможным влиянием на производительность из-за роста
числа классов.

```java
// Пример использования анонимного внутреннего класса.
public class MyClass extends Applet {
    ...
        someObject.addMouseListener(new MouseAdapter() {
            public void mouseClicked(MouseEvent e) {
                ...// Здесь реализация слушателя...
            }
        });
    ...
    }
}
```

**Примечание.** Недостаток анонимных внутренних классов: их «не видит» механизм долговременной
сохраняемости (*long-term persistence*). Подробнее см. документацию пакета
[JavaBeans](https://docs.oracle.com/javase/8/docs/api/java/beans/package-summary.html#package_description)
и урок [Bean Persistence](https://docs.oracle.com/javase/tutorial/javabeans/advanced/persistence.html).

Внутренние классы работают, даже если слушателю нужен доступ к приватным полям внешнего класса. Пока
внутренний класс не объявлен `static`, он может ссылаться на поля и методы экземпляра, как если бы его
код находился в содержащем классе. Чтобы локальная переменная стала доступной внутреннему классу,
сохраните её копию в локальной переменной `final`. Для ссылки на охватывающий экземпляр используйте
`ИмяВнешнегоКласса.this`. Подробнее — [Nested Classes](https://docs.oracle.com/javase/tutorial/java/javaOO/nested.html).

### Класс EventHandler

Класс [`EventHandler`](https://docs.oracle.com/javase/8/docs/api/java/beans/EventHandler.html)
поддерживает динамическое создание простых слушателей «в одно выражение». Он полезен лишь для крайне
простых слушателей, но заслуживает упоминания: он позволяет (1) создать слушателя, видимого механизму
сохраняемости и не засоряющего ваши классы интерфейсами слушателей; (2) не увеличивать число классов
приложения (это помогает производительности).

Создавать `EventHandler` вручную трудно: при ошибке вы узнаете о ней не во время компиляции, а через
непонятное исключение во время выполнения. Поэтому `EventHandler` лучше создавать GUI-построителем и
тщательно документировать. Класс предназначен для интерактивных инструментов (построителей приложений),
связывающих бины: обычно связь идёт от бина пользовательского интерфейса (источник события) к бину
бизнес-логики (цель). Внутренние классы — более общий способ; `EventHandler` покрывает лишь подмножество
их возможностей, но лучше работает с долговременной сохраняемостью и в больших приложениях, где один
интерфейс реализуется многократно, экономит память и место на диске.

```java
// Простейшее применение: вызвать метод цели без аргументов.
myButton.addActionListener(
    (ActionListener)EventHandler.create(ActionListener.class, frame, "toFront"));
```

При нажатии `myButton` выполнится `frame.toFront()`. Эквивалент через внутренний класс (с дополнительной
проверкой типов при компиляции):

```java
// Эквивалентный код с внутренним классом вместо EventHandler.
myButton.addActionListener(new ActionListener() {
    public void actionPerformed(ActionEvent e) {
        frame.toFront();
    }
});
```

Можно извлечь значение свойства из первого аргумента метода (обычно объекта события) и присвоить его
свойству цели:

```java
EventHandler.create(ActionListener.class, myButton, "nextFocusableComponent", "source")
```

```java
// Эквивалент с внутренним классом.
new ActionListener() {
    public void actionPerformed(ActionEvent e) {
        myButton.setNextFocusableComponent((Component)e.getSource());
    }
}
```

Можно передать целевому методу сам объект события — для этого четвёртый аргумент `create` делают пустой
строкой:

```java
EventHandler.create(ActionListener.class, target, "doActionEvent", "")
```

```java
// Эквивалент с внутренним классом.
new ActionListener() {
    public void actionPerformed(ActionEvent e) {
        target.doActionEvent(e);
    }
}
```

Самое частое применение — извлечь значение свойства из источника события и присвоить его свойству цели:

```java
EventHandler.create(ActionListener.class, myButton, "label", "source.text")
```

```java
// Эквивалент с внутренним классом.
new ActionListener {
    public void actionPerformed(ActionEvent e) {
        myButton.setLabel(((JTextField)e.getSource()).getText());
    }
}
```

## Слушатели, поддерживаемые компонентами Swing

Узнать, какие события может порождать компонент, можно по тому, какие слушатели на нём можно
зарегистрировать. Например, `JComboBox` определяет методы регистрации `addActionListener`,
`addItemListener`, `addPopupMenuListener` — значит, комбинированный список поддерживает слушателей
действий, элементов и контекстного меню (плюс унаследованные от `JComponent`).

### Слушатели, поддерживаемые всеми компонентами Swing

Поскольку все компоненты Swing происходят от класса AWT `Component`, на любом из них можно
зарегистрировать следующих слушателей:

| Слушатель | За чем следит |
|-----------|---------------|
| Слушатель компонента (*Component Listener*) | Изменения размера, положения или видимости компонента. |
| Слушатель фокуса (*Focus Listener*) | Получил или потерял компонент фокус ввода с клавиатуры. |
| Слушатель клавиатуры (*Key Listener*) | Нажатия клавиш; события порождает только компонент, владеющий фокусом. |
| Слушатель мыши (*Mouse Listener*) | Щелчки, нажатия и отпускания кнопок мыши, вход/выход курсора в область компонента. |
| Слушатель движения мыши (*Mouse-Motion Listener*) | Изменения положения курсора над компонентом. |
| Слушатель колеса мыши (*Mouse-Wheel Listener*) | Прокрутку колеса мыши над компонентом. |
| Слушатель иерархии (*Hierarchy Listener*) | Изменения иерархии вложенности компонента (события «changed»). |
| Слушатель границ иерархии (*Hierarchy Bounds Listener*) | Изменения иерархии вложенности (события «moved» и «resized»). |

Все компоненты Swing происходят и от AWT-класса `Container`, но многие из них контейнерами не
используются. Формально любой компонент Swing может порождать события контейнера (добавление/удаление
компонента), но реально их обычно порождают только контейнеры (панели, фреймы) и составные компоненты
(комбинированные списки).

`JComponent` добавляет ещё три типа слушателей:

| Слушатель | За чем следит |
|-----------|---------------|
| Слушатель предков (*Ancestor Listener*) | Добавление/удаление, скрытие, показ или перемещение контейнеров-предков компонента. |
| Слушатель изменения свойств (*Property Change Listener*) | Изменения связанных свойств (*bound properties*); используется, например, форматированными текстовыми полями. |
| Слушатель вето-изменений (*Vetoable Change Listener*) | Используется инструментами-построителями для отслеживания изменений ограниченных свойств (*constrained properties*). |

### Таблица: какие компоненты какие события порождают

В таблице «✓» означает, что компонент поддерживает данного слушателя.

| Компонент | Action | Caret | Change | Document / Undoable Edit | Item | List Selection | Window | Прочие типы слушателей |
|-----------|:------:|:-----:|:------:|:------------------------:|:----:|:--------------:|:------:|------------------------|
| Button (кнопка) | ✓ | | ✓ | | ✓ | | | |
| Check Box (флажок) | ✓ | | ✓ | | ✓ | | | |
| Color Chooser (выбор цвета) | | | ✓ | | | | | |
| Combo Box (комб. список) | ✓ | | | | ✓ | | | |
| Dialog (диалог) | | | | | | | ✓ | |
| Editor Pane | | ✓ | | ✓ | | | | Hyperlink |
| File Chooser (выбор файла) | ✓ | | | | | | | |
| Formatted Text Field | ✓ | ✓ | | ✓ | | | | |
| Frame (фрейм) | | | | | | | ✓ | |
| Internal Frame | | | | | | | | Internal Frame Listener |
| List (список) | | | | | | ✓ | | List Data Listener |
| Menu (меню) | | | | | | | | Menu Listener |
| Menu Item (пункт меню) | ✓ | | ✓ | | ✓ | | | Menu Key Listener, Menu Drag Mouse Listener |
| Option Pane | | | | | | | | |
| Password Field | ✓ | ✓ | | ✓ | | | | |
| Popup Menu | | | | | | | | Popup Menu Listener |
| Progress Bar | | | ✓ | | | | | |
| Radio Button (переключатель) | ✓ | | ✓ | | ✓ | | | |
| Slider (ползунок) | | | ✓ | | | | | |
| Spinner | | | ✓ | | | | | |
| Tabbed Pane | | | ✓ | | | | | |
| Table (таблица) | | | | | | ✓ | | Table Model Listener, Table Column Model Listener, Cell Editor Listener |
| Text Area | | ✓ | | ✓ | | | | |
| Text Field | ✓ | ✓ | | ✓ | | | | |
| Text Pane | | ✓ | | ✓ | | | | Hyperlink Listener |
| Toggle Button | ✓ | | ✓ | | ✓ | | | |
| Tree (дерево) | | | | | | | | Tree Expansion Listener, Tree Will Expand Listener, Tree Model Listener, Tree Selection Listener |
| Viewport (в ScrollPane) | | | ✓ | | | | | |

## Реализация слушателей часто обрабатываемых событий

Ниже — подробности по конкретным видам слушателей. Раздел охватывает не все возможные слушатели, а
самые нужные. Сведения об остальных — в [итоговой таблице Listener API](#итоговая-таблица-listener-api).
Полный набор страниц оригинала (для каждой даны переводы или ссылки): Action, Caret, Change, Component,
Container, Document, Focus, Internal Frame, Item, Key, List Data, List Selection, Mouse, Mouse-Motion,
Mouse-Wheel, Property Change, Table Model, Tree Expansion, Tree Model, Tree Selection, Tree-Will-Expand,
Undoable Edit, Window.

### Как написать слушатель действий (Action Listener)

Слушатели действий — пожалуй, самые простые и частые. Action-событие происходит, когда пользователь
выполняет действие: щёлкает кнопку, выбирает пункт меню, нажимает *Enter* в текстовом поле. В итоге всем
зарегистрированным слушателям отправляется сообщение `actionPerformed`. Шаги написания слушателя:

1. Объявите класс-обработчик, реализующий `ActionListener` (или наследующий класс, который его реализует):
   ```java
   public class MyClass implements ActionListener {
   ```
2. Зарегистрируйте экземпляр обработчика слушателем на одном или нескольких компонентах:
   ```java
   someComponent.addActionListener(instanceOfMyClass);
   ```
3. Реализуйте методы интерфейса:
   ```java
   public void actionPerformed(ActionEvent e) {
       ...// код, реагирующий на действие...
   }
   ```

Единственный аргумент метода — объект `ActionEvent` с информацией о событии и его источнике. Полный
пример `AL.java` (считает число щелчков по кнопке):

```java
import java.awt.*;
import java.awt.event.*;

public class AL extends Frame implements WindowListener, ActionListener {
        TextField text = new TextField(20);
        Button b;
        private int numClicks = 0;

        public static void main(String[] args) {
                AL myWindow = new AL("My first window");
                myWindow.setSize(350, 100);
                myWindow.setVisible(true);
        }

        public AL(String title) {

                super(title);
                setLayout(new FlowLayout());
                addWindowListener(this);
                b = new Button("Click me");
                add(b);
                add(text);
                b.addActionListener(this);
        }

        public void actionPerformed(ActionEvent e) {
                numClicks++;
                text.setText("Button Clicked " + numClicks + " times");
        }

        public void windowClosing(WindowEvent e) {
                dispose();
                System.exit(0);
        }

        public void windowOpened(WindowEvent e) {}
        public void windowActivated(WindowEvent e) {}
        public void windowIconified(WindowEvent e) {}
        public void windowDeiconified(WindowEvent e) {}
        public void windowDeactivated(WindowEvent e) {}
        public void windowClosed(WindowEvent e) {}

}
```

**Интерфейс `ActionListener`** (адаптера нет — метод один):

| Метод | Назначение |
|-------|------------|
| `actionPerformed(ActionEvent)` | Вызывается сразу после того, как пользователь выполнил действие. |

**Класс `ActionEvent`:**

| Метод | Назначение |
|-------|------------|
| `String getActionCommand()` | Возвращает строку, связанную с действием. Большинство объектов, порождающих action-события, поддерживают метод `setActionCommand` для её установки. |
| `int getModifiers()` | Возвращает целое — клавиши-модификаторы, нажатые во время события. Константы `ActionEvent`: `SHIFT_MASK`, `CTRL_MASK`, `META_MASK`, `ALT_MASK`. Например, при Shift-выборе пункта меню выражение `actionEvent.getModifiers() & ActionEvent.SHIFT_MASK` ненулевое. |
| `Object getSource()` (из `java.util.EventObject`) | Возвращает объект, породивший событие. |

### Как написать слушатель каретки (Caret Listener)

События каретки (*caret* — курсор, указывающий точку вставки) происходят, когда каретка в текстовом
компоненте перемещается или когда меняется выделение. Документ компонента может инициировать caret-события,
например, при вставке или удалении текста. Caret-слушателя присоединяют к любому подклассу
`JTextComponent` методом `addCaretListener`.

**Примечание.** Альтернатива — присоединить слушателя прямо к объекту каретки, а не к текстовому
компоненту. Каретка порождает события изменения (*change*, а не *caret*), поэтому понадобится
change-слушатель, а не caret-слушатель.

Пример из приложения `TextComponentDemo`:

```java
// там, где происходит инициализация
CaretListenerLabel caretListenerLabel =
    new CaretListenerLabel("Caret Status");
...
textPane.addCaretListener(caretListenerLabel);
...
protected class CaretListenerLabel extends JLabel
                                   implements CaretListener
{
    ...
    // Может вызываться не из потока диспетчеризации событий.
    public void caretUpdate(CaretEvent e) {
        displaySelectionInfo(e.getDot(), e.getMark());
    }

    // Этот метод можно вызывать из любого потока. Он вызывает
    // setText и modelToView, которые должны выполняться в потоке
    // диспетчеризации событий. Поэтому через invokeLater
    // планируем код на выполнение в этом потоке.
    protected void displaySelectionInfo(final int dot,
                                        final int mark) {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                if (dot == mark) {  // нет выделения
                    ...
                }
            });
        }
    }
}
```

**Примечание.** Метод `caretUpdate` не гарантированно вызывается в потоке диспетчеризации событий. Любой
код внутри него, обновляющий GUI, нужно выполнять в этом потоке — обернув в `Runnable` и вызвав
`SwingUtilities.invokeLater`.

**Интерфейс `CaretListener`** (адаптера нет):

| Метод | Назначение |
|-------|------------|
| `caretUpdate(CaretEvent)` | Вызывается при перемещении каретки или изменении выделения в прослушиваемом компоненте. |

**Класс `CaretEvent`:**

| Метод | Назначение |
|-------|------------|
| `int getDot()` | Текущее положение каретки. Если текст выделен, каретка отмечает один конец выделения. |
| `int getMark()` | Другой конец выделения. Если ничего не выделено, равно значению `getDot`. Заметьте: dot не обязательно меньше mark. |
| `Object getSource()` (из `java.util.EventObject`) | Возвращает объект, породивший событие. |

### Как написать слушатель изменений (Change Listener)

Change-слушатель похож на слушателя изменения свойств, но уведомляется только о том, что объект-источник
**изменился**, без указания, что именно. Он полезен, когда достаточно знать сам факт изменения. На
change-события опираются несколько компонентов: `JTabbedPane`, `JViewPort`, ползунки, выбор цвета,
спиннеры. Чтобы узнать об изменении значения ползунка, регистрируют change-слушателя; аналогично — для
выбора цвета и спиннера.

```java
//...там, где происходит инициализация:
framesPerSecond.addChangeListener(new SliderListener());
...
class SliderListener implements ChangeListener {
    public void stateChanged(ChangeEvent e) {
        JSlider source = (JSlider)e.getSource();
        if (!source.getValueIsAdjusting()) {
            int fps = (int)source.getValue();
            ...
        }
    }
}
```

**Интерфейс `ChangeListener`** (адаптера нет):

| Метод | Назначение |
|-------|------------|
| `stateChanged(ChangeEvent)` | Вызывается при изменении состояния прослушиваемого компонента. |

**Класс `ChangeEvent`:**

| Метод | Назначение |
|-------|------------|
| `Object getSource()` (из `java.util.EventObject`) | Возвращает объект, породивший событие. |

### Как написать слушатель компонента (Component Listener)

Component-слушатель получает события компонента. Один или несколько таких событий порождаются объектом
`Component` сразу после того, как компонент был скрыт, показан, перемещён или изменил размер. Класс,
заинтересованный в этих событиях, реализует интерфейс `ComponentListener` целиком либо наследует
абстрактный `ComponentAdapter`, переопределяя нужные методы; затем регистрируется через
`addComponentListener`.

События component-hidden и component-shown происходят только как результат вызова метода `setVisible`.
Например, окно может быть свёрнуто в значок (iconified) без порождения события component-hidden.

```java
public class ComponentEventDemo ... implements ComponentListener {
    static JFrame frame;
    JLabel label;
    ...
    public ComponentEventDemo() {
        ...
        JPanel panel = new JPanel(new BorderLayout());
        label = new JLabel("This is a label", JLabel.CENTER);
        label.addComponentListener(this);
        panel.add(label, BorderLayout.CENTER);

        JCheckBox checkbox = new JCheckBox("Label visible", true);
        checkbox.addComponentListener(this);
        panel.add(checkbox, BorderLayout.PAGE_END);
        panel.addComponentListener(this);
        ...
        frame.addComponentListener(this);
    }
    ...
    public void componentHidden(ComponentEvent e) {
        displayMessage(e.getComponent().getClass().getName() + " --- Hidden");
    }

    public void componentMoved(ComponentEvent e) {
        displayMessage(e.getComponent().getClass().getName() + " --- Moved");
    }

    public void componentResized(ComponentEvent e) {
        displayMessage(e.getComponent().getClass().getName() + " --- Resized ");
    }

    public void componentShown(ComponentEvent e) {
        displayMessage(e.getComponent().getClass().getName() + " --- Shown");
    }

    public static void main(String[] args) {
        ...
        // Создаём и настраиваем окно.
        frame = new JFrame("ComponentEventDemo");
        ...
        JComponent newContentPane = new ComponentEventDemo();
        frame.setContentPane(newContentPane);
        ...
    }
}
```

**Интерфейс `ComponentListener`** (адаптер `ComponentAdapter` содержит все эти методы):

| Метод | Назначение |
|-------|------------|
| `componentHidden(ComponentEvent)` | Вызывается после того, как компонент скрыт вызовом `setVisible`. |
| `componentMoved(ComponentEvent)` | Вызывается после перемещения компонента относительно контейнера. Например, при перемещении окна событие порождает окно, но не компоненты внутри него. |
| `componentResized(ComponentEvent)` | Вызывается после изменения размера (прямоугольных границ) компонента. |
| `componentShown(ComponentEvent)` | Вызывается после того, как компонент стал видимым вызовом `setVisible`. |

**Класс `ComponentEvent`:**

| Метод | Назначение |
|-------|------------|
| `Component getComponent()` | Возвращает компонент, породивший событие. Можно использовать вместо `getSource`. |

### Как написать слушатель контейнера (Container Listener)

Container-события порождаются контейнером сразу после добавления компонента в контейнер или удаления из
него. Эти события только уведомляют — для успешного добавления/удаления компонентов слушатель не нужен.

```java
public class ContainerEventDemo ... implements ContainerListener ... {
    ...// там, где происходит инициализация:
        buttonPanel = new JPanel(new GridLayout(1,1));
        buttonPanel.addContainerListener(this);
    ...
    public void componentAdded(ContainerEvent e) {
        displayMessage(" added to ", e);
    }

    public void componentRemoved(ContainerEvent e) {
        displayMessage(" removed from ", e);
    }

    void displayMessage(String action, ContainerEvent e) {
        display.append(((JButton)e.getChild()).getText()
                       + " was"
                       + action
                       + e.getContainer().getClass().getName()
                       + newline);
    }
    ...
}
```

**Интерфейс `ContainerListener`** (адаптер `ContainerAdapter`):

| Метод | Назначение |
|-------|------------|
| `componentAdded(ContainerEvent)` | Вызывается сразу после добавления компонента в прослушиваемый контейнер. |
| `componentRemoved(ContainerEvent)` | Вызывается сразу после удаления компонента из прослушиваемого контейнера. |

**Класс `ContainerEvent`:**

| Метод | Назначение |
|-------|------------|
| `Component getChild()` | Возвращает компонент, добавление или удаление которого вызвало событие. |
| `Container getContainer()` | Возвращает контейнер, породивший событие. Можно использовать вместо `getSource`. |

### Как написать слушатель документа (Document Listener)

Текстовый компонент Swing использует объект `Document` для представления содержимого. Document-события
происходят при любом изменении содержимого документа. Слушателя присоединяют к **документу** текстового
компонента, а не к самому компоненту.

```java
public class DocumentEventDemo ... {
    //...там, где происходит инициализация:
    textField = new JTextField(20);
    textField.addActionListener(new MyTextActionListener());
    textField.getDocument().addDocumentListener(new MyDocumentListener());
    textField.getDocument().putProperty("name", "Text Field");

    textArea = new JTextArea();
    textArea.getDocument().addDocumentListener(new MyDocumentListener());
    textArea.getDocument().putProperty("name", "Text Area");
    ...

class MyDocumentListener implements DocumentListener {
    String newline = "\n";

    public void insertUpdate(DocumentEvent e) {
        updateLog(e, "inserted into");
    }

    public void removeUpdate(DocumentEvent e) {
        updateLog(e, "removed from");
    }

    public void changedUpdate(DocumentEvent e) {
        // Простые текстовые компоненты эти события не порождают
    }

    public void updateLog(DocumentEvent e, String action) {
        Document doc = (Document)e.getDocument();
        int changeLength = e.getLength();
        displayArea.append(
            changeLength + " character" +
            ((changeLength == 1) ? " " : "s ") +
            action + doc.getProperty("name") + "." + newline +
            "  Text length = " + doc.getLength() + newline);
    }
}
```

**Важно.** Слушатели документа не должны изменять содержимое документа: к моменту уведомления изменение
уже завершено. Вместо этого напишите собственный документ, переопределяющий методы `insertString` и/или
`remove`.

**Интерфейс `DocumentListener`** (адаптера нет):

| Метод | Назначение |
|-------|------------|
| `changedUpdate(DocumentEvent)` | Вызывается при изменении стиля части текста. Порождается только из `StyledDocument`; `PlainDocument` такие события не порождает. |
| `insertUpdate(DocumentEvent)` | Вызывается при вставке текста в прослушиваемый документ. |
| `removeUpdate(DocumentEvent)` | Вызывается при удалении текста из прослушиваемого документа. |

**Интерфейс `DocumentEvent`** (обычно экземпляр `DefaultDocumentEvent` из `AbstractDocument`):

| Метод | Назначение |
|-------|------------|
| `Document getDocument()` | Возвращает документ, породивший событие. Интерфейс `DocumentEvent` не наследует `EventObject`, поэтому метода `getSource` у него нет. |
| `int getLength()` | Длина изменения. |
| `int getOffset()` | Позиция первого изменённого символа в документе. |
| `ElementChange getChange(Element)` | Подробности о том, какие элементы документа изменились и как. `ElementChange` — интерфейс, определённый внутри `DocumentEvent`. |
| `EventType getType()` | Тип изменения. `EventType` — класс внутри `DocumentEvent`, перечисляющий возможные изменения: вставка текста, удаление текста, изменение стиля текста. |

### Как написать слушатель фокуса (Focus Listener)

Focus-события порождаются при получении или потере компонентом фокуса ввода с клавиатуры — независимо
от того, мышью, клавиатурой или программно это произошло. Чтобы получать focus-события конкретного
компонента, регистрируют `FocusListener`. Для фокуса только окна реализуют `WindowFocusListener`. Чтобы
отслеживать состояние фокуса многих компонентов, реализуют `PropertyChangeListener` на классе
`KeyboardFocusManager`.

```java
public class FocusEventDemo ... implements FocusListener ... {
    public FocusEventDemo() {
        ...
        JTextField textField = new JTextField("A TextField");
        textField.addFocusListener(this);
        ...
        JLabel label = new JLabel("A Label");
        label.addFocusListener(this);
        ...
        JComboBox comboBox = new JComboBox(vector);
        comboBox.addFocusListener(this);
        ...
        JButton button = new JButton("A Button");
        button.addFocusListener(this);
        ...
        JList list = new JList(listVector);
        list.setSelectedIndex(1); // Легче заметить смену фокуса,
                                  // если элемент выделен.
        list.addFocusListener(this);
        JScrollPane listScrollPane = new JScrollPane(list);

        ...

        // Область, сообщающая о событиях focus-gained и focus-lost.
        display = new JTextArea();
        display.setEditable(false);
        // setRequestFocusEnabled не даёт компоненту получать фокус
        // щелчком мыши, но он по-прежнему может получить фокус
        // с клавиатуры — это обеспечивает доступность.
        display.setRequestFocusEnabled(false);
        display.addFocusListener(this);
        JScrollPane displayScrollPane = new JScrollPane(display);

        ...
    }
    ...
    public void focusGained(FocusEvent e) {
        displayMessage("Focus gained", e);
    }

    public void focusLost(FocusEvent e) {
        displayMessage("Focus lost", e);
    }

    void displayMessage(String prefix, FocusEvent e) {
        display.append(prefix
                       + (e.isTemporary() ? " (temporary):" : ":")
                       +  e.getComponent().getClass().getName()
                       + "; Opposite component: "
                       + (e.getOppositeComponent() != null ?
                          e.getOppositeComponent().getClass().getName() : "null")
                       + newline);
    }
    ...
}
```

**Интерфейс `FocusListener`** (адаптер `FocusAdapter`):

| Метод | Назначение |
|-------|------------|
| `focusGained(FocusEvent)` | Вызывается сразу после того, как компонент получил фокус. |
| `focusLost(FocusEvent)` | Вызывается сразу после того, как компонент потерял фокус. |

**Класс `FocusEvent`:**

| Метод | Назначение |
|-------|------------|
| `boolean isTemporary()` | `true`, если событие потери/получения фокуса временное. |
| `Component getComponent()` (из `java.awt.event.ComponentEvent`) | Компонент, породивший focus-событие. |
| `Component getOppositeComponent()` | Другой компонент, участвующий в смене фокуса. Для `FOCUS_GAINED` — компонент, потерявший фокус; для `FOCUS_LOST` — получивший. Если задействовано нативное приложение, Java-приложение в другой VM/контексте или другого компонента нет — возвращает `null`. |

### Как написать слушатель элементов (Item Listener)

Item-события порождаются компонентами, реализующими интерфейс `ItemSelectable`. Обычно такие компоненты
хранят состояние «вкл./выкл.» для одного или нескольких элементов. Среди компонентов Swing item-события
порождают кнопки (флажки, флажковые пункты меню, переключатели-кнопки и т. п.) и комбинированные списки.

```java
// там, где происходит инициализация
checkbox.addItemListener(this);
...
public void itemStateChanged(ItemEvent e) {
    if (e.getStateChange() == ItemEvent.SELECTED) {
        label.setVisible(true);
        ...
    } else {
        label.setVisible(false);
    }
}
```

**Интерфейс `ItemListener`** (адаптера нет):

| Метод | Назначение |
|-------|------------|
| `itemStateChanged(ItemEvent)` | Вызывается сразу после изменения состояния прослушиваемого компонента. |

**Класс `ItemEvent`:**

| Метод | Назначение |
|-------|------------|
| `Object getItem()` | Возвращает специфичный для компонента объект элемента, чьё состояние изменилось. Часто это `String` с текстом выбранного элемента. |
| `ItemSelectable getItemSelectable()` | Возвращает компонент, породивший item-событие. Можно использовать вместо `getSource`. |
| `int getStateChange()` | Новое состояние элемента. Класс `ItemEvent` определяет два состояния: `SELECTED` и `DESELECTED`. |

### Как написать слушатель клавиатуры (Key Listener)

Key-события сообщают о наборе на клавиатуре. Их порождает компонент, владеющий фокусом, при нажатии или
отпускании клавиш.

**Примечание.** Для особых реакций на конкретные клавиши используйте привязки клавиш (*key bindings*),
а не key-слушателя (см. *How to Use Key Bindings*).

Уведомления приходят о двух основных видах событий:

- ввод символа Unicode — событие **key-typed**;
- нажатие или отпускание клавиши — событие **key-pressed** или **key-released**.

Как правило, реагируют только на key-typed, если не нужно знать о нажатии клавиш, не соответствующих
символам. Например, чтобы узнать о вводе символа Unicode (одной клавишей 'a' или последовательностью),
обрабатывают key-typed; чтобы узнать о нажатии F1 или клавиши '3' на цифровом блоке — key-pressed.

**Примечание.** Для порождения событий клавиатуры компонент **обязан** владеть фокусом. Чтобы компонент
получал фокус: (1) убедитесь, что `isFocusable` возвращает `true` (например, для `JLabel` вызовите
`setFocusable(true)`); (2) убедитесь, что компонент запрашивает фокус при необходимости — для
пользовательских компонентов реализуют слушателя мыши, вызывающего `requestFocusInWindow` по щелчку.

**Замечание о версии.** Подсистема фокуса потребляет клавиши обхода фокуса (Tab, Shift+Tab). Чтобы они
не потреблялись, вызовите на компоненте `component.setFocusTraversalKeysEnabled(false)` — тогда обход
фокуса придётся обрабатывать самостоятельно. Альтернатива — `KeyEventDispatcher` для предварительного
прослушивания всех событий клавиатуры.

Можно получить подробности о key-pressed: была ли это клавиша-действие (*action key* — Copy, Paste, Page
Up, Undo, стрелки, функциональные клавиши), а также расположение клавиши (левый/правый Shift, '2' на
основной клавиатуре или на цифровом блоке). Для key-typed можно получить значение символа и модификаторы.

**Примечание.** Не полагайтесь на значение `getKeyChar`, кроме как для события key-typed.

```java
public class KeyEventDemo ... implements KeyListener ... {
    //...там, где происходит инициализация:
    typingArea = new JTextField(20);
    typingArea.addKeyListener(this);

    // Раскомментируйте, чтобы отключить обход фокуса.
    // Подсистема фокуса потребляет клавиши обхода, такие как
    // Tab и Shift+Tab. Если раскомментировать строку ниже,
    // обход фокуса отключится и события Tab станут доступны
    // слушателю клавиатуры.
    //typingArea.setFocusTraversalKeysEnabled(false);
    ...

    /** Обработать событие key-typed от текстового поля. */
    public void keyTyped(KeyEvent e) {
        displayInfo(e, "KEY TYPED: ");
    }

    /** Обработать событие key-pressed от текстового поля. */
    public void keyPressed(KeyEvent e) {
        displayInfo(e, "KEY PRESSED: ");
    }

    /** Обработать событие key-released от текстового поля. */
    public void keyReleased(KeyEvent e) {
        displayInfo(e, "KEY RELEASED: ");
    }
    ...
    private void displayInfo(KeyEvent e, String keyStatus){

        // На символ клавиши стоит полагаться, только если
        // событие — key-typed.
        int id = e.getID();
        String keyString;
        if (id == KeyEvent.KEY_TYPED) {
            char c = e.getKeyChar();
            keyString = "key character = '" + c + "'";
        } else {
            int keyCode = e.getKeyCode();
            keyString = "key code = " + keyCode
                    + " ("
                    + KeyEvent.getKeyText(keyCode)
                    + ")";
        }

        int modifiersEx = e.getModifiersEx();
        String modString = "extended modifiers = " + modifiersEx;
        String tmpString = KeyEvent.getModifiersExText(modifiersEx);
        if (tmpString.length() > 0) {
            modString += " (" + tmpString + ")";
        } else {
            modString += " (no extended modifiers)";
        }

        String actionString = "action key? ";
        if (e.isActionKey()) {
            actionString += "YES";
        } else {
            actionString += "NO";
        }

        String locationString = "key location: ";
        int location = e.getKeyLocation();
        if (location == KeyEvent.KEY_LOCATION_STANDARD) {
            locationString += "standard";
        } else if (location == KeyEvent.KEY_LOCATION_LEFT) {
            locationString += "left";
        } else if (location == KeyEvent.KEY_LOCATION_RIGHT) {
            locationString += "right";
        } else if (location == KeyEvent.KEY_LOCATION_NUMPAD) {
            locationString += "numpad";
        } else { // (location == KeyEvent.KEY_LOCATION_UNKNOWN)
            locationString += "unknown";
        }

        //...Отобразить информацию о KeyEvent...
    }
}
```

**Интерфейс `KeyListener`** (адаптер `KeyAdapter`):

| Метод | Назначение |
|-------|------------|
| `keyTyped(KeyEvent)` | Вызывается сразу после ввода пользователем символа Unicode в прослушиваемый компонент. |
| `keyPressed(KeyEvent)` | Вызывается сразу после нажатия клавиши, пока компонент владеет фокусом. |
| `keyReleased(KeyEvent)` | Вызывается сразу после отпускания клавиши, пока компонент владеет фокусом. |

**Класс `KeyEvent`** (наследует много методов от `InputEvent`, например `getModifiersEx`, и пару от
`ComponentEvent`/`AWTEvent` — полный список см. в таблице `InputEvent` на странице слушателя мыши):

| Метод | Назначение |
|-------|------------|
| `int getKeyChar()` | Символ Unicode, связанный с событием. Полагаться на него можно только для key-typed. |
| `int getKeyCode()` | Код клавиши, идентифицирующий нажатую/отпущенную клавишу. `KeyEvent` определяет множество констант, например `VK_A` (клавиша A) и `VK_ESCAPE` (Escape). |
| `String getKeyText(int)` / `String getKeyModifiersText(int)` | Текстовые описания кода клавиши и клавиш-модификаторов соответственно. |
| `int getModifiersEx()` / `String getModifiersExText(int)` | Расширенная маска модификаторов события (методы унаследованы от `InputEvent`). Представляют состояние всех модальных клавиш. Предпочтительнее `getKeyText`/`getKeyModifiersText`, так как дают больше информации. |
| `boolean isActionKey()` | `true`, если клавиша — клавиша-действие (Cut, Copy, Paste, Page Up, Caps Lock, стрелки, функциональные). Действительно только для key-pressed и key-released. |
| `int getKeyLocation()` | Расположение клавиши, породившей событие; различает клавиши, встречающиеся несколько раз (два Shift и т. п.). Значения: `KEY_LOCATION_STANDARD`, `KEY_LOCATION_LEFT`, `KEY_LOCATION_RIGHT`, `KEY_LOCATION_NUMPAD`, `KEY_LOCATION_UNKNOWN`. Для key-typed всегда `KEY_LOCATION_UNKNOWN`. |

### Как написать слушатель выбора в списке (List Selection Listener)

События выбора в списке происходят, когда выделение в списке или таблице меняется или только что
изменилось. Они порождаются объектом, реализующим интерфейс `ListSelectionModel`. У таблицы модель
выбора получают через `getSelectionModel` или `getColumnModel().getSelectionModel()`. Слушателя
регистрируют на объекте модели выбора; `JList` также позволяет регистрировать слушателя прямо на самом
списке.

```java
// где определены поля-члены
JList list;
    // в методе init:
    listSelectionModel = list.getSelectionModel();
    listSelectionModel.addListSelectionListener(
                            new SharedListSelectionHandler());
```

```java
class SharedListSelectionHandler implements ListSelectionListener {
    public void valueChanged(ListSelectionEvent e) {
        ListSelectionModel lsm = (ListSelectionModel)e.getSource();

        int firstIndex = e.getFirstIndex();
        int lastIndex = e.getLastIndex();
        boolean isAdjusting = e.getValueIsAdjusting();
        output.append("Event for indexes "
                      + firstIndex + " - " + lastIndex
                      + "; isAdjusting is " + isAdjusting
                      + "; selected indexes:");

        if (lsm.isSelectionEmpty()) {
            output.append(" <none>");
        } else {
            // Узнаём, какие индексы выделены.
            int minIndex = lsm.getMinSelectionIndex();
            int maxIndex = lsm.getMaxSelectionIndex();
            for (int i = minIndex; i <= maxIndex; i++) {
                if (lsm.isSelectedIndex(i)) {
                    output.append(" " + i);
                }
            }
        }
        output.append(newline);
    }
}
```

Первый и последний индексы события задают включительный диапазон элементов, для которых выделение
изменилось. При режиме множественного интервального выделения некоторые элементы внутри диапазона могли
не измениться. Флаг `isAdjusting` равен `true`, пока пользователь ещё меняет выделение, и `false`, когда
закончил. Объект `ListSelectionEvent` сообщает только о факте изменения, не о текущем выделении —
поэтому метод опрашивает модель.

**Интерфейс `ListSelectionListener`** (адаптера нет):

| Метод | Назначение |
|-------|------------|
| `valueChanged(ListSelectionEvent)` | Вызывается в ответ на изменения выделения. |

**Класс `ListSelectionEvent`:**

| Метод | Назначение |
|-------|------------|
| `Object getSource()` (из `java.util.EventObject`) | Объект, породивший событие. Если слушатель зарегистрирован прямо на списке — источник список, иначе — модель выбора. |
| `int getFirstIndex()` | Индекс первого элемента, чьё значение выделения изменилось. При множественном интервальном выделении гарантированно изменились первый и последний, промежуточные — не обязательно. |
| `int getLastIndex()` | Индекс последнего изменённого элемента (см. примечание выше). |
| `boolean getValueIsAdjusting()` | `true`, если выделение ещё меняется. Многих слушателей интересует только финальное состояние, и они могут игнорировать события, когда метод возвращает `true`. |

### Как написать слушатель мыши (Mouse Listener)

Mouse-события сообщают о действиях пользователя мышью (или похожим устройством). Они происходят при
входе/выходе курсора в область компонента и при нажатии/отпускании кнопок мыши. Отслеживание движения
курсора заметно затратнее, поэтому mouse-motion-события вынесены в отдельный тип слушателя.

Если нужны и mouse-, и mouse-motion-события, используйте класс `MouseInputAdapter` — он реализует
удобный интерфейс `MouseInputListener`, объединяющий `MouseListener` и `MouseMotionListener` (но не
`MouseWheelListener`). Альтернативно — AWT-класс `MouseAdapter`, реализующий `MouseListener`,
`MouseMotionListener` и `MouseWheelListener`.

```java
public class MouseEventDemo ... implements MouseListener {
        // там, где происходит инициализация:
        // Регистрируемся на события мыши для blankArea и панели.
        blankArea.addMouseListener(this);
        addMouseListener(this);
    ...

    public void mousePressed(MouseEvent e) {
       saySomething("Mouse pressed; # of clicks: "
                    + e.getClickCount(), e);
    }

    public void mouseReleased(MouseEvent e) {
       saySomething("Mouse released; # of clicks: "
                    + e.getClickCount(), e);
    }

    public void mouseEntered(MouseEvent e) {
       saySomething("Mouse entered", e);
    }

    public void mouseExited(MouseEvent e) {
       saySomething("Mouse exited", e);
    }

    public void mouseClicked(MouseEvent e) {
       saySomething("Mouse clicked (# of clicks: "
                    + e.getClickCount() + ")", e);
    }

    void saySomething(String eventDescription, MouseEvent e) {
        textArea.append(eventDescription + " detected on "
                        + e.getComponent().getClass().getName()
                        + "." + newline);
    }
}
```

**Интерфейс `MouseListener`** (адаптеры `MouseAdapter`, `MouseInputAdapter`):

| Метод | Назначение |
|-------|------------|
| `mouseClicked(MouseEvent)` | Вызывается сразу после щелчка по прослушиваемому компоненту. |
| `mouseEntered(MouseEvent)` | Вызывается сразу после входа курсора в границы компонента. |
| `mouseExited(MouseEvent)` | Вызывается сразу после выхода курсора за границы компонента. |
| `mousePressed(MouseEvent)` | Вызывается сразу после нажатия кнопки мыши над компонентом. |
| `mouseReleased(MouseEvent)` | Вызывается сразу после отпускания кнопки мыши после нажатия над компонентом. |

**Класс `MouseEvent`:**

| Метод | Назначение |
|-------|------------|
| `int getClickCount()` | Число быстрых последовательных щелчков (включая данный); 2 — для двойного щелчка. |
| `int getX()` / `int getY()` / `Point getPoint()` | Позиция (x, y) события относительно компонента-источника. |
| `int getXOnScreen()` / `int getYOnScreen()` / `Point getLocationOnScreen()` | Абсолютная позиция события (относительно виртуальной системы координат в многоэкранной среде, иначе — системы координат конфигурации графики компонента). |
| `int getButton()` | Какая кнопка мыши изменила состояние: `NOBUTTON`, `BUTTON1`, `BUTTON2` или `BUTTON3`. |
| `boolean isPopupTrigger()` | `true`, если событие должно вызвать всплывающее меню. Триггеры зависят от платформы — вызывайте для всех событий mouse-pressed и mouse-released. |
| `String getMouseModifiersText(int)` | Строка с описанием клавиш-модификаторов и кнопок мыши, активных во время события («Shift», «Ctrl+Shift»). |

**Класс `InputEvent`** (от него `MouseEvent` наследует методы; плюс пара от `ComponentEvent`/`AWTEvent`):

| Метод | Назначение |
|-------|------------|
| `int getID()` (из `java.awt.AWTEvent`) | Тип события (конкретное действие): `MOUSE_PRESSED`, `MOUSE_RELEASED`, `MOUSE_CLICKED` и т. д. |
| `Component getComponent()` (из `ComponentEvent`) | Компонент, породивший событие. Можно вместо `getSource`. |
| `int getWhen()` | Временная метка события. Чем больше, тем недавнее событие. |
| `boolean isAltDown()` / `isControlDown()` / `isMetaDown()` / `isShiftDown()` | Состояние отдельных клавиш-модификаторов в момент события. |
| `int getModifiers()` | Состояние всех модификаторов и кнопок мыши. Константы: `ALT_MASK`, `BUTTON1_MASK`, `BUTTON2_MASK`, `BUTTON3_MASK`, `CTRL_MASK`, `META_MASK`, `SHIFT_MASK`. |
| `int getModifiersEx()` | Расширенная маска модификаторов. Битовые маски: `SHIFT_DOWN_MASK`, `CTRL_DOWN_MASK`, `META_DOWN_MASK`, `ALT_DOWN_MASK`, `BUTTON1_DOWN_MASK`, `BUTTON2_DOWN_MASK`, `BUTTON3_DOWN_MASK`, `ALT_GRAPH_DOWN_MASK`. |
| `int getModifiersExText(int)` | Строка с описанием расширенных модификаторов и кнопок («Shift», «Button1», «Ctrl+Shift»). |

**Класс `MouseInfo`** (информация о положении указателя в любой момент):

| Метод | Назначение |
|-------|------------|
| `getPointerInfo()` | Возвращает `PointerInfo` — текущее положение указателя мыши. |
| `getNumberOfButtons()` | Число кнопок мыши или `-1`, если мышь не поддерживается. |

### Как написать слушатель движения мыши (Mouse-Motion Listener)

Mouse-motion-события сообщают о перемещении курсора мышью. Если нужны и обычные mouse-события, и
mouse-motion-события, используйте `MouseInputAdapter` (реализует `MouseInputListener`, объединяющий
`MouseListener` и `MouseMotionListener`). Альтернатива — AWT-класс `MouseAdapter`.

```java
public class MouseMotionEventDemo extends JPanel
                                  implements MouseMotionListener {
    //...в коде инициализации:
    // Регистрируемся на события мыши для blankArea и панели.
    blankArea.addMouseMotionListener(this);
    addMouseMotionListener(this);
    ...
}

public void mouseMoved(MouseEvent e) {
   saySomething("Mouse moved", e);
}

public void mouseDragged(MouseEvent e) {
   saySomething("Mouse dragged", e);
}

void saySomething(String eventDescription, MouseEvent e) {
    textArea.append(eventDescription
                    + " (" + e.getX() + "," + e.getY() + ")"
                    + " detected on "
                    + e.getComponent().getClass().getName()
                    + newline);
}
```

Пример `SelectionDemo` (один слушатель для mouse- и mouse-motion-событий через `MouseInputAdapter`):

```java
//...там, где происходит инициализация:
MyListener myListener = new MyListener();
addMouseListener(myListener);
addMouseMotionListener(myListener);
...
private class MyListener extends MouseInputAdapter {
    public void mousePressed(MouseEvent e) {
        int x = e.getX();
        int y = e.getY();
        currentRect = new Rectangle(x, y, 0, 0);
        updateDrawableRect(getWidth(), getHeight());
        repaint();
    }

    public void mouseDragged(MouseEvent e) {
        updateSize(e);
    }

    public void mouseReleased(MouseEvent e) {
        updateSize(e);
    }

    void updateSize(MouseEvent e) {
        int x = e.getX();
        int y = e.getY();
        currentRect.setSize(x - currentRect.x,
                            y - currentRect.y);
        updateDrawableRect(getWidth(), getHeight());
        Rectangle totalRepaint = rectToDraw.union(previouseRectDrawn);
        repaint(totalRepaint.x, totalRepaint.y,
                totalRepaint.width, totalRepaint.height);
    }
}
```

**Интерфейс `MouseMotionListener`** (адаптеры `MouseMotionAdapter`, `MouseAdapter`):

| Метод | Назначение |
|-------|------------|
| `mouseDragged(MouseEvent)` | Вызывается при перемещении мыши с зажатой кнопкой. Порождается компонентом, породившим последнее событие mouse-pressed, даже если курсор уже не над ним. |
| `mouseMoved(MouseEvent)` | Вызывается при перемещении мыши без нажатых кнопок. Порождается компонентом, находящимся под курсором. |

У каждого метода mouse-motion-события единственный параметр — и это **не** `MouseMotionEvent`, а
`MouseEvent`. См. таблицу `MouseEvent` выше.

### Как написать слушатель колеса мыши (Mouse-Wheel Listener)

Mouse-wheel-события сообщают о вращении колеса мыши. Не на всех мышах есть колесо; программно определить
его наличие нельзя. Обычно реализовывать такого слушателя не нужно: панели прокрутки (*scroll panes*)
автоматически регистрируют mouse-wheel-слушателей. Но при создании пользовательского компонента для
панели прокрутки может понадобиться настроить поведение прокрутки (единичный и блочный шаги). Для
порождения mouse-wheel-событий курсор должен быть **над** зарегистрированным компонентом. Тип прокрутки
(`WHEEL_UNIT_SCROLL` или `WHEEL_BLOCK_SCROLL`) и её величина зависят от платформы.

```java
public class MouseWheelEventDemo ... implements MouseWheelListener ... {
    public MouseWheelEventDemo() {
        // там, где происходит инициализация:
        // Регистрируемся на события колеса мыши для текстовой области.
        textArea.addMouseWheelListener(this);
        ...
    }

    public void mouseWheelMoved(MouseWheelEvent e) {
       String message;
       int notches = e.getWheelRotation();
       if (notches < 0) {
           message = "Mouse wheel moved UP "
                        + -notches + " notch(es)" + newline;
       } else {
           message = "Mouse wheel moved DOWN "
                        + notches + " notch(es)" + newline;
       }
       if (e.getScrollType() == MouseWheelEvent.WHEEL_UNIT_SCROLL) {
           message += "    Scroll type: WHEEL_UNIT_SCROLL" + newline;
           message += "    Scroll amount: " + e.getScrollAmount()
                   + " unit increments per notch" + newline;
           message += "    Units to scroll: " + e.getUnitsToScroll()
                   + " unit increments" + newline;
           message += "    Vertical unit increment: "
               + scrollPane.getVerticalScrollBar().getUnitIncrement(1)
               + " pixels" + newline;
       } else { // тип прокрутки == MouseWheelEvent.WHEEL_BLOCK_SCROLL
           message += "    Scroll type: WHEEL_BLOCK_SCROLL" + newline;
           message += "    Vertical block increment: "
               + scrollPane.getVerticalScrollBar().getBlockIncrement(1)
               + " pixels" + newline;
       }
       saySomething(message, e);
    }
    ...
}
```

**Интерфейс `MouseWheelListener`.** Хотя метод один, у него есть соответствующий адаптер — `MouseAdapter`.
Это позволяет иметь один экземпляр адаптера, обрабатывающий все типы событий указателя мыши:

| Метод | Назначение |
|-------|------------|
| `mouseWheelMoved(MouseWheelEvent)` | Вызывается при вращении колеса мыши. |

**Класс `MouseWheelEvent`:**

| Метод | Назначение |
|-------|------------|
| `int getScrollType()` | Тип прокрутки: `WHEEL_BLOCK_SCROLL` или `WHEEL_UNIT_SCROLL` (определяется платформой). |
| `int getWheelRotation()` | Число «щелчков» поворота колеса. К пользователю (вниз) — положительное, от пользователя (вверх) — отрицательное. |
| `int getScrollAmount()` | Число единиц прокрутки на щелчок. Всегда положительное; действительно только при `WHEEL_UNIT_SCROLL`. |
| `int getUnitsToScroll()` | Число единиц прокрутки (со знаком) для текущего события. Действительно только при `WHEEL_UNIT_SCROLL`. |

### Как написать слушатель изменения свойств (Property Change Listener)

Property-change-события происходят при изменении значения **связанного свойства** (*bound property*)
бина — компонента, соответствующего спецификации JavaBeans. Все компоненты Swing являются бинами.
Свойство JavaBeans доступно через методы *get* и *set* (например, `getFont`/`setFont`). Связанное
свойство при изменении значения порождает property-change-событие.

Частые случаи применения: отслеживание ввода нового значения в форматированном текстовом поле (свойство
*value*); реакция на нажатие кнопки диалога или смену выбора; уведомление о смене компонента-владельца
фокуса (свойство *focusOwner* у `KeyboardFocusManager`).

Зарегистрировать слушателя можно двумя способами. Первый — `addPropertyChangeListener(PropertyChangeListener)`:
вы получаете уведомления о любом изменении любого связанного свойства; имя изменившегося свойства узнают
через `getPropertyName`:

```java
KeyboardFocusManager focusManager =
   KeyboardFocusManager.getCurrentKeyboardFocusManager();
focusManager.addPropertyChangeListener(new FocusManagerListener());
...
public FocusManagerListener implements PropertyChangeListener {
    public void propertyChange(PropertyChangeEvent e) {
        String propertyName = e.getPropertyName();
        if ("focusOwner".equals(propertyName) {
            ...
        } else if ("focusedWindow".equals(propertyName) {
            ...
        }
    }
    ...
}
```

Второй — `addPropertyChangeListener(String, PropertyChangeListener)`: уведомления приходят только при
изменении указанного свойства:

```java
aComponent.addPropertyChangeListener("font",
                                     new FontListener());
```

Пример регистрации на свойство *value* форматированного текстового поля:

```java
//...там, где происходит инициализация:
double amount;
JFormattedTextField amountField;
...
amountField.addPropertyChangeListener("value",
                                      new FormattedTextFieldListener());
...
class FormattedTextFieldListener implements PropertyChangeListener {
    public void propertyChanged(PropertyChangeEvent e) {
        Object source = e.getSource();
        if (source == amountField) {
            amount = ((Number)amountField.getValue()).doubleValue();
            ...
        }
        //...пересчитать платёж и обновить поле...
    }
}
```

**Регистрация `PropertyChangeListener`:**

| Метод | Назначение |
|-------|------------|
| `addPropertyChangeListener(PropertyChangeListener)` | Добавляет слушателя в список. Уведомляет обо всех связанных свойствах. |
| `addPropertyChangeListener(String, PropertyChangeListener)` | Добавляет слушателя для конкретного свойства — вызывается только при его изменении. |

**Интерфейс `PropertyChangeListener`** (адаптера нет):

| Метод | Назначение |
|-------|------------|
| `propertyChange(PropertyChangeEvent)` | Вызывается при изменении связанного свойства прослушиваемого бина. |

**Класс `PropertyChangeEvent`:**

| Метод | Назначение |
|-------|------------|
| `Object getNewValue()` | Новое значение свойства. |
| `Object getOldValue()` | Старое значение свойства. |
| `String getPropertyName()` | Имя изменившегося свойства. |
| `void setPropagationId()` | Получает/устанавливает значение propagation ID. Зарезервировано на будущее. |

### Как написать слушатели окна (Window Listeners)

Раздел объясняет три вида обработчиков, связанных с окном: `WindowListener`, `WindowFocusListener`,
`WindowStateListener`. Все три работают с объектами `WindowEvent`, и методы всех трёх реализованы
абстрактным классом `WindowAdapter`. После регистрации соответствующего слушателя на окне (фрейме или
диалоге) window-события порождаются сразу после соответствующей активности или смены состояния окна.
Окно считается «владельцем фокуса», если получает ввод с клавиатуры.

Window-событию могут предшествовать активности/состояния:

- **Открытие окна** — первый показ.
- **Закрытие окна** — удаление окна с экрана.
- **Свёртывание в значок** (iconify) — окно становится значком на рабочем столе.
- **Развёртывание из значка** (deiconify) — восстановление исходного размера.
- **Окно в фокусе** — окно, содержащее «владельца фокуса».
- **Активированное окно (фрейм/диалог)** — окно в фокусе либо владеющее окном в фокусе.
- **Деактивированное окно** — потеряло фокус.
- **Максимизация окна** — увеличение до максимального размера по вертикали, горизонтали или обоим.

`WindowListener` обрабатывает большинство window-событий (открытие/закрытие, активация/деактивация,
свёртывание/развёртывание). `WindowFocusListener` определяет, когда окно становится владельцем фокуса
или теряет этот статус. `WindowStateListener` имеет единственный метод для обнаружения смены состояния
окна (свёрнуто, развёрнуто, максимизировано или возвращено в норму). Хотя некоторые состояния (например,
свёртывание) можно ловить и через `WindowListener`, `WindowStateListener` предпочтительнее: у него один
метод и есть поддержка максимизации.

```java
public class WindowEventDemo extends JFrame implements WindowListener,
                                            WindowFocusListener,
                                            WindowStateListener {
    ...
    static WindowEventDemo frame = new WindowEventDemo("WindowEventDemo");
    JTextArea display;
    ...

    private void addComponentsToPane() {
        display = new JTextArea();
        display.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(display);
        scrollPane.setPreferredSize(new Dimension(500, 450));
        getContentPane().add(scrollPane, BorderLayout.CENTER);

        addWindowListener(this);
        addWindowFocusListener(this);
        addWindowStateListener(this);

        checkWM();
    }

    public WindowEventDemo(String name) {
        super(name);
    }

    // Некоторые оконные менеджеры поддерживают не все состояния окна.

    public void checkWM() {
        Toolkit tk = frame.getToolkit();
        if (!(tk.isFrameStateSupported(Frame.ICONIFIED))) {
            displayMessage(
                    "Your window manager doesn't support ICONIFIED.");
        }  else displayMessage(
                "Your window manager supports ICONIFIED.");
        if (!(tk.isFrameStateSupported(Frame.MAXIMIZED_VERT))) {
            displayMessage(
                    "Your window manager doesn't support MAXIMIZED_VERT.");
        }  else displayMessage(
                "Your window manager supports MAXIMIZED_VERT.");
        if (!(tk.isFrameStateSupported(Frame.MAXIMIZED_HORIZ))) {
            displayMessage(
                    "Your window manager doesn't support MAXIMIZED_HORIZ.");
        } else displayMessage(
                "Your window manager supports MAXIMIZED_HORIZ.");
        if (!(tk.isFrameStateSupported(Frame.MAXIMIZED_BOTH))) {
            displayMessage(
                    "Your window manager doesn't support MAXIMIZED_BOTH.");
        } else {
            displayMessage(
                    "Your window manager supports MAXIMIZED_BOTH.");
        }
    }

    public void windowClosing(WindowEvent e) {
        displayMessage("WindowListener method called: windowClosing.");
        // Пауза, чтобы пользователь увидел сообщение
        // до фактического закрытия окна.
        ActionListener task = new ActionListener() {
            boolean alreadyDisposed = false;
            public void actionPerformed(ActionEvent e) {
                if (frame.isDisplayable()) {
                    alreadyDisposed = true;
                    frame.dispose();
                }
            }
        };
        Timer timer = new Timer(500, task); // срабатывать каждые полсекунды
        timer.setInitialDelay(2000);        // первая задержка 2 секунды
        timer.setRepeats(false);
        timer.start();
    }

    public void windowClosed(WindowEvent e) {
        // Будет видно только в стандартном выводе.
        displayMessage("WindowListener method called: windowClosed.");
    }

    public void windowOpened(WindowEvent e) {
        displayMessage("WindowListener method called: windowOpened.");
    }

    public void windowIconified(WindowEvent e) {
        displayMessage("WindowListener method called: windowIconified.");
    }

    public void windowDeiconified(WindowEvent e) {
        displayMessage("WindowListener method called: windowDeiconified.");
    }

    public void windowActivated(WindowEvent e) {
        displayMessage("WindowListener method called: windowActivated.");
    }

    public void windowDeactivated(WindowEvent e) {
        displayMessage("WindowListener method called: windowDeactivated.");
    }

    public void windowGainedFocus(WindowEvent e) {
        displayMessage("WindowFocusListener method called: windowGainedFocus.");
    }

    public void windowLostFocus(WindowEvent e) {
        displayMessage("WindowFocusListener method called: windowLostFocus.");
    }

    public void windowStateChanged(WindowEvent e) {
        displayStateMessage(
          "WindowStateListener method called: windowStateChanged.", e);
    }

    void displayMessage(String msg) {
        display.append(msg + newline);
        System.out.println(msg);
    }

    void displayStateMessage(String prefix, WindowEvent e) {
        int state = e.getNewState();
        int oldState = e.getOldState();
        String msg = prefix
                   + newline + space
                   + "New state: "
                   + convertStateToString(state)
                   + newline + space
                   + "Old state: "
                   + convertStateToString(oldState);
        displayMessage(msg);
    }

    String convertStateToString(int state) {
        if (state == Frame.NORMAL) {
            return "NORMAL";
        }
        String strState = " ";
        if ((state & Frame.ICONIFIED) != 0) {
            strState += "ICONIFIED";
        }
        // MAXIMIZED_BOTH — конкатенация двух битов, поэтому
        // проверяем точное совпадение.
        if ((state & Frame.MAXIMIZED_BOTH) == Frame.MAXIMIZED_BOTH) {
            strState += "MAXIMIZED_BOTH";
        } else {
            if ((state & Frame.MAXIMIZED_VERT) != 0) {
                strState += "MAXIMIZED_VERT";
            }
            if ((state & Frame.MAXIMIZED_HORIZ) != 0) {
                strState += "MAXIMIZED_HORIZ";
            }
            if (" ".equals(strState)){
                strState = "UNKNOWN";
            }
        }
        return strState.trim();
    }
}
```

**Интерфейс `WindowListener`** (адаптер `WindowAdapter`):

| Метод | Назначение |
|-------|------------|
| `windowOpened(WindowEvent)` | Вызывается сразу после первого показа окна. |
| `windowClosing(WindowEvent)` | Вызывается в ответ на запрос пользователя закрыть окно. Чтобы действительно закрыть окно, слушатель должен вызвать `dispose` или `setVisible(false)`. |
| `windowClosed(WindowEvent)` | Вызывается сразу после закрытия окна. |
| `windowIconified(WindowEvent)` | Вызывается сразу после свёртывания окна в значок. |
| `windowDeiconified(WindowEvent)` | Вызывается сразу после развёртывания окна из значка. |
| `windowActivated(WindowEvent)` | Вызывается сразу после активации окна. |
| `windowDeactivated(WindowEvent)` | Вызывается сразу после деактивации окна. Эти методы не отправляются окнам, не являющимся фреймами или диалогами; поэтому для определения получения/потери фокуса предпочтительны `windowGainedFocus` и `windowLostFocus`. |

**Интерфейс `WindowFocusListener`** (адаптер `WindowAdapter`):

| Метод | Назначение |
|-------|------------|
| `windowGainedFocus(WindowEvent)` | Вызывается сразу после получения окном фокуса. |
| `windowLostFocus(WindowEvent)` | Вызывается сразу после потери окном фокуса. |

**Интерфейс `WindowStateListener`** (адаптер `WindowAdapter`):

| Метод | Назначение |
|-------|------------|
| `windowStateChanged(WindowEvent)` | Вызывается сразу после смены состояния окна (свёртывание, развёртывание, максимизация, возврат в норму). Состояние доступно как битовая маска. Значения из `java.awt.Frame`: `NORMAL` (ни один бит не установлен), `ICONIFIED`, `MAXIMIZED_HORIZ`, `MAXIMIZED_VERT`, `MAXIMIZED_BOTH` (конкатенация двух предыдущих). Оконный менеджер может поддерживать `MAXIMIZED_BOTH`, не поддерживая по отдельности горизонтальную/вертикальную максимизацию. Проверить поддержку можно методом `java.awt.Toolkit.isFrameStateSupported(int)`. |

**Класс `WindowEvent`:**

| Метод | Назначение |
|-------|------------|
| `Window getWindow()` | Окно, породившее событие. Можно вместо `getSource`. |
| `Window getOppositeWindow()` | Другое окно, участвующее в смене фокуса/активации. Для `WINDOW_ACTIVATED`/`WINDOW_GAINED_FOCUS` — окно, потерявшее активацию/фокус; для `WINDOW_DEACTIVATED`/`WINDOW_LOST_FOCUS` — получившее. Иначе `null`. |
| `int getOldState()` | Для событий `WINDOW_STATE_CHANGED` — предыдущее состояние окна (битовая маска). |
| `int getNewState()` | Для событий `WINDOW_STATE_CHANGED` — новое состояние окна (битовая маска). |

Слушатели окна обычно применяют для: (1) реализации собственного поведения при закрытии (сохранить
данные перед закрытием, выйти из программы при закрытии последнего окна); (2) управления ресурсами
(останавливать потоки и освобождать ресурсы при свёртывании окна, запускать снова при развёртывании,
чтобы не тратить ресурсы зря). Не все оконные менеджеры поддерживают все состояния окна — проверяйте
через `isFrameStateSupported(int)`.

## Итоговая таблица Listener API

Быстрая справочная таблица: для каждого слушателя — его адаптер (если есть) и методы.

| Интерфейс-слушатель | Класс-адаптер | Методы слушателя |
|---------------------|---------------|------------------|
| `ActionListener` | нет | `actionPerformed(ActionEvent)` |
| `AncestorListener` | нет | `ancestorAdded(AncestorEvent)`; `ancestorMoved(AncestorEvent)`; `ancestorRemoved(AncestorEvent)` |
| `CaretListener` | нет | `caretUpdate(CaretEvent)` |
| `CellEditorListener` | нет | `editingStopped(ChangeEvent)`; `editingCanceled(ChangeEvent)` |
| `ChangeListener` | нет | `stateChanged(ChangeEvent)` |
| `ComponentListener` | `ComponentAdapter` | `componentHidden(ComponentEvent)`; `componentMoved(ComponentEvent)`; `componentResized(ComponentEvent)`; `componentShown(ComponentEvent)` |
| `ContainerListener` | `ContainerAdapter` | `componentAdded(ContainerEvent)`; `componentRemoved(ContainerEvent)` |
| `DocumentListener` | нет | `changedUpdate(DocumentEvent)`; `insertUpdate(DocumentEvent)`; `removeUpdate(DocumentEvent)` |
| `ExceptionListener` | нет | `exceptionThrown(Exception)` |
| `FocusListener` | `FocusAdapter` | `focusGained(FocusEvent)`; `focusLost(FocusEvent)` |
| `HierarchyBoundsListener` | `HierarchyBoundsAdapter` | `ancestorMoved(HierarchyEvent)`; `ancestorResized(HierarchyEvent)` |
| `HierarchyListener` | нет | `hierarchyChanged(HierarchyEvent)` |
| `HyperlinkListener` | нет | `hyperlinkUpdate(HyperlinkEvent)` |
| `InputMethodListener` | нет | `caretPositionChanged(InputMethodEvent)`; `inputMethodTextChanged(InputMethodEvent)` |
| `InternalFrameListener` | `InternalFrameAdapter` | `internalFrameActivated`; `internalFrameClosed`; `internalFrameClosing`; `internalFrameDeactivated`; `internalFrameDeiconified`; `internalFrameIconified`; `internalFrameOpened` (все — `(InternalFrameEvent)`) |
| `ItemListener` | нет | `itemStateChanged(ItemEvent)` |
| `KeyListener` | `KeyAdapter` | `keyPressed(KeyEvent)`; `keyReleased(KeyEvent)`; `keyTyped(KeyEvent)` |
| `ListDataListener` | нет | `contentsChanged(ListDataEvent)`; `intervalAdded(ListDataEvent)`; `intervalRemoved(ListDataEvent)` |
| `ListSelectionListener` | нет | `valueChanged(ListSelectionEvent)` |
| `MenuDragMouseListener` | нет | `menuDragMouseDragged`; `menuDragMouseEntered`; `menuDragMouseExited`; `menuDragMouseReleased` (все — `(MenuDragMouseEvent)`) |
| `MenuKeyListener` | нет | `menuKeyPressed(MenuKeyEvent)`; `menuKeyReleased(MenuKeyEvent)`; `menuKeyTyped(MenuKeyEvent)` |
| `MenuListener` | нет | `menuCanceled(MenuEvent)`; `menuDeselected(MenuEvent)`; `menuSelected(MenuEvent)` |
| `MouseInputListener` (расширяет `MouseListener` и `MouseMotionListener`) | `MouseInputAdapter`, `MouseAdapter` | `mouseClicked`; `mouseEntered`; `mouseExited`; `mousePressed`; `mouseReleased`; `mouseDragged`; `mouseMoved` (все — `(MouseEvent)`) |
| `MouseListener` | `MouseAdapter`, `MouseInputAdapter` | `mouseClicked(MouseEvent)`; `mouseEntered(MouseEvent)`; `mouseExited(MouseEvent)`; `mousePressed(MouseEvent)`; `mouseReleased(MouseEvent)` |
| `MouseMotionListener` | `MouseMotionAdapter`, `MouseInputAdapter` | `mouseDragged(MouseEvent)`; `mouseMoved(MouseEvent)` |
| `MouseWheelListener` | `MouseAdapter` | `mouseWheelMoved(MouseWheelEvent)` |
| `PopupMenuListener` | нет | `popupMenuCanceled(PopupMenuEvent)`; `popupMenuWillBecomeInvisible(PopupMenuEvent)`; `popupMenuWillBecomeVisible(PopupMenuEvent)` |
| `PropertyChangeListener` | нет | `propertyChange(PropertyChangeEvent)` |
| `TableColumnModelListener` | нет | `columnAdded(TableColumnModelEvent)`; `columnMoved(TableColumnModelEvent)`; `columnRemoved(TableColumnModelEvent)`; `columnMarginChanged(ChangeEvent)`; `columnSelectionChanged(ListSelectionEvent)` |
| `TableModelListener` | нет | `tableChanged(TableModelEvent)` |
| `TreeExpansionListener` | нет | `treeCollapsed(TreeExpansionEvent)`; `treeExpanded(TreeExpansionEvent)` |
| `TreeModelListener` | нет | `treeNodesChanged(TreeModelEvent)`; `treeNodesInserted(TreeModelEvent)`; `treeNodesRemoved(TreeModelEvent)`; `treeStructureChanged(TreeModelEvent)` |
| `TreeSelectionListener` | нет | `valueChanged(TreeSelectionEvent)` |
| `TreeWillExpandListener` | нет | `treeWillCollapse(TreeExpansionEvent)`; `treeWillExpand(TreeExpansionEvent)` |
| `UndoableEditListener` | нет | `undoableEditHappened(UndoableEditEvent)` |
| `VetoableChangeListener` | нет | `vetoableChange(PropertyChangeEvent)` |
| `WindowFocusListener` | `WindowAdapter` | `windowGainedFocus(WindowEvent)`; `windowLostFocus(WindowEvent)` |
| `WindowListener` | `WindowAdapter` | `windowActivated`; `windowClosed`; `windowClosing`; `windowDeactivated`; `windowDeiconified`; `windowIconified`; `windowOpened` (все — `(WindowEvent)`) |
| `WindowStateListener` | `WindowAdapter` | `windowStateChanged(WindowEvent)` |

## Решение типичных проблем обработки событий

**Проблема: компонент не порождает события, которые должен.**

- Сначала убедитесь, что зарегистрировали слушателя нужного вида. Проверьте, не подойдёт ли другой вид
  слушателя для нужных событий.
- Убедитесь, что зарегистрировали слушателя на правильном объекте.
- Правильно ли реализован обработчик? Например, при наследовании от адаптера проверьте сигнатуру метода:
  каждый метод-обработчик должен быть `public void`, имя — без опечаток, тип аргумента — верный.

**Проблема: мой комбинированный список не порождает низкоуровневые события (например, focus-события).**

- Комбинированные списки — составные компоненты (реализованы несколькими компонентами), поэтому они не
  порождают низкоуровневые события, которые порождают простые компоненты. Подробнее см.
  [Handling Events on a Combo Box](https://docs.oracle.com/javase/tutorial/uiswing/components/combobox.html#listeners).

**Проблема: документ editor pane (или text pane) не порождает document-события.**

- При загрузке текста из URL объект-документ editor pane / text pane может смениться, и ваши слушатели
  окажутся прослушивающими неиспользуемый документ. Например, при загрузке HTML в компонент, ранее
  содержавший простой текст, документ сменится на экземпляр `HTMLDocument`. Если программа динамически
  загружает текст, учтите возможную смену документа (заново регистрируйте document-слушателей на новом
  документе и т. п.).

## Источник

- [Writing Event Listeners](https://docs.oracle.com/javase/tutorial/uiswing/events/index.html) — индексная страница урока, официальное руководство Oracle.
- [Introduction to Event Listeners](https://docs.oracle.com/javase/tutorial/uiswing/events/intro.html)
- [General Information about Writing Event Listeners](https://docs.oracle.com/javase/tutorial/uiswing/events/generalrules.html)
- [Listeners Supported by Swing Components](https://docs.oracle.com/javase/tutorial/uiswing/events/eventsandcomponents.html)
- [Implementing Listeners for Commonly Handled Events](https://docs.oracle.com/javase/tutorial/uiswing/events/handling.html)
- [How to Write an Action Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/actionlistener.html)
- [How to Write a Caret Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/caretlistener.html)
- [How to Write a Change Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/changelistener.html)
- [How to Write a Component Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/componentlistener.html)
- [How to Write a Container Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/containerlistener.html)
- [How to Write a Document Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/documentlistener.html)
- [How to Write a Focus Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/focuslistener.html)
- [How to Write an Internal Frame Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/internalframelistener.html)
- [How to Write an Item Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/itemlistener.html)
- [How to Write a Key Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/keylistener.html)
- [How to Write a List Data Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/listdatalistener.html)
- [How to Write a List Selection Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/listselectionlistener.html)
- [How to Write a Mouse Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/mouselistener.html)
- [How to Write a Mouse-Motion Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/mousemotionlistener.html)
- [How to Write a Mouse-Wheel Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/mousewheellistener.html)
- [How to Write a Property Change Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/propertychangelistener.html)
- [How to Write a Table Model Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/tablemodellistener.html)
- [How to Write a Tree Expansion Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/treeexpansionlistener.html)
- [How to Write a Tree Model Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/treemodellistener.html)
- [How to Write a Tree Selection Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/treeselectionlistener.html)
- [How to Write a Tree-Will-Expand Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/treewillexpandlistener.html)
- [How to Write an Undoable Edit Listener](https://docs.oracle.com/javase/tutorial/uiswing/events/undoableeditlistener.html)
- [How to Write Window Listeners](https://docs.oracle.com/javase/tutorial/uiswing/events/windowlistener.html)
- [Listener API Table](https://docs.oracle.com/javase/tutorial/uiswing/events/api.html)
- [Solving Common Event-Handling Problems](https://docs.oracle.com/javase/tutorial/uiswing/events/problems.html)
