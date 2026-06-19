# Урок 2. Создание компонентов JavaBeans

**Трейл:** JavaBeans · **Оригинал:** [Writing JavaBeans Components](https://docs.oracle.com/javase/tutorial/javabeans/writing/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок объединяет
> страницы *Writing JavaBeans Components*, *Properties* (включая разделы Indexed, Bound,
> Constrained), *Methods*, *Events* и *Using a BeanInfo*.

Создавать компоненты JavaBeans на удивление просто. Вам не нужен специальный инструмент и
не требуется реализовывать какие-либо интерфейсы. Написание бинов (*beans*) сводится лишь к
следованию определённым соглашениям по оформлению кода. Всё, что от вас требуется, — сделать
так, чтобы ваш класс *выглядел* как бин; тогда инструменты, *использующие* бины, смогут
распознать и применить ваш бин.

Тем не менее NetBeans предоставляет ряд возможностей, упрощающих написание бинов. Кроме того,
в Java SE API входят вспомогательные классы, помогающие решать типовые задачи.

Примеры кода в этом уроке основаны на простом графическом компоненте `FaceBean`.

- Только исходный код `FaceBean`: [`FaceBean.java`](https://docs.oracle.com/javase/tutorial/javabeans/writing/examples/FaceBean/src/facebean/FaceBean.java)
- Целиком проект NetBeans, включающий исходный код `FaceBean`: [`FaceBean.zip`](https://docs.oracle.com/javase/tutorial/javabeans/writing/examples/zipfiles/FaceBean.zip)

Бин (*bean*) — это Java-класс, имена методов которого следуют рекомендациям JavaBeans.
Инструмент-сборщик бинов (*bean builder tool*) применяет **интроспекцию** (*introspection*),
чтобы изучить класс бина. На основе этого исследования инструмент-сборщик способен определить
свойства (*properties*), методы (*methods*) и события (*events*) бина.

В следующих разделах описаны рекомендации JavaBeans для **свойств**, **методов** и **событий**.
Наконец, раздел про `BeanInfo` показывает, как можно настроить то, как разработчик работает с
вашим бином.

## Свойства (Properties)

Чтобы определить свойство (*property*) в классе бина, нужно предоставить публичные методы-геттер
(*getter*) и метод-сеттер (*setter*). Например, следующие методы определяют свойство типа `int`
с именем `mouthWidth`:

```java
public class FaceBean {
    private int mMouthWidth = 90;

    public int getMouthWidth() {
        return mMouthWidth;
    }
    
    public void setMouthWidth(int mw) {
        mMouthWidth = mw;
    }
}
```

Инструмент-сборщик, такой как NetBeans, распознаёт имена методов и показывает свойство
`mouthWidth` в своём списке свойств. Он также распознаёт тип `int` и предоставляет подходящий
редактор, позволяющий изменять свойство на этапе проектирования (*design time*).

В этом примере показано свойство, которое можно и читать, и записывать. Возможны и другие
сочетания. Например, свойство только для чтения (*read-only*) имеет метод-геттер, но не имеет
сеттера. Свойство только для записи (*write-only*) имеет только метод-сеттер.

Особый случай — свойства типа `boolean`: для них метод-аксессор (*accessor*) можно определять с
помощью `is` вместо `get`. Например, аксессор для `boolean`-свойства `running` может выглядеть так:

```java
public boolean isRunning() {
    // ...
}
```

Доступны различные специализации базовых свойств, описанные в следующих разделах.

### Сводка видов свойств

| Вид свойства | Что предоставляет класс бина | Особенности |
| --- | --- | --- |
| Чтение-запись (*read-write*) | геттер и сеттер | значение можно читать и записывать |
| Только для чтения (*read-only*) | только геттер | сеттера нет |
| Только для записи (*write-only*) | только сеттер | геттера нет |
| Логическое (*boolean*) | геттер вида `is...` (или `get...`) и сеттер | для `boolean` аксессор можно начинать с `is` |
| Индексированное (*indexed*) | геттер/сеттер для всего массива и для отдельного элемента | свойство — массив, а не одно значение |
| Связанное (*bound*) | геттер, сеттер + `addPropertyChangeListener()` / `removePropertyChangeListener()` | уведомляет слушателей об изменении значения |
| Ограниченное (*constrained*) | геттер, сеттер + `addVetoableChangeListener()` / `removeVetoableChangeListener()` | слушатели могут наложить вето на изменение |

### Индексированные свойства (Indexed Properties)

**Индексированное** (*indexed*) свойство представляет собой массив, а не одиночное значение. В этом
случае класс бина предоставляет метод для получения и установки всего массива целиком. Вот пример
для свойства типа `int[]` с именем `testGrades`:

```java
public int[] getTestGrades() {
    return mTestGrades;
}

public void setTestGrades(int[] tg) {
    mTestGrades = tg;
}
```

Для индексированных свойств класс бина также предоставляет методы для получения и установки
конкретного элемента массива.

```java
public int getTestGrades(int index) {
    return mTestGrades[index];
}

public void setTestGrades(int index, int grade) {
    mTestGrades[index] = grade;
}
```

### Связанные свойства (Bound Properties)

**Связанное** (*bound*) свойство уведомляет слушателей (*listeners*) об изменении своего значения.
Из этого следуют два момента:

1. Класс бина включает методы `addPropertyChangeListener()` и `removePropertyChangeListener()`
   для управления слушателями бина.
2. При изменении связанного свойства бин отправляет событие `PropertyChangeEvent` своим
   зарегистрированным слушателям.

Классы `PropertyChangeEvent` и `PropertyChangeListener` находятся в пакете `java.beans`.

Пакет `java.beans` также содержит класс `PropertyChangeSupport`, который берёт на себя бо́льшую
часть работы со связанными свойствами. Этот удобный класс отслеживает слушателей свойств и включает
вспомогательный метод, рассылающий события об изменении свойства всем зарегистрированным слушателям.

Следующий пример показывает, как можно сделать свойство `mouthWidth` связанным с помощью
`PropertyChangeSupport`. Необходимые дополнения для связанного свойства в оригинале выделены
жирным.

```java
import java.beans.*;

public class FaceBean {
    private int mMouthWidth = 90;
    private PropertyChangeSupport mPcs =
        new PropertyChangeSupport(this);

    public int getMouthWidth() {
        return mMouthWidth;
    }
    
    public void setMouthWidth(int mw) {
        int oldMouthWidth = mMouthWidth;
        mMouthWidth = mw;
        mPcs.firePropertyChange("mouthWidth",
                                   oldMouthWidth, mw);
    }

    public void
    addPropertyChangeListener(PropertyChangeListener listener) {
        mPcs.addPropertyChangeListener(listener);
    }
    
    public void
    removePropertyChangeListener(PropertyChangeListener listener) {
        mPcs.removePropertyChangeListener(listener);
    }
}
```

Связанные свойства можно напрямую привязывать к другим свойствам бинов с помощью инструмента-сборщика,
такого как NetBeans. Можно, например, взять свойство `value` компонента-ползунка (*slider*) и привязать
его к свойству `mouthWidth` из примера. NetBeans позволяет сделать это без написания кода.

### Ограниченные свойства (Constrained Properties)

**Ограниченное** (*constrained*) свойство — это особый вид связанного свойства. Для ограниченного
свойства бин ведёт учёт набора слушателей **вето** (*veto listeners*). Когда ограниченное свойство
вот-вот изменится, со слушателями советуются относительно этого изменения. Любой из слушателей
имеет возможность наложить вето на изменение, и в этом случае свойство остаётся неизменным.

Слушатели вето отделены от слушателей изменения свойства. К счастью, пакет `java.beans` содержит
класс `VetoableChangeSupport`, который значительно упрощает работу с ограниченными свойствами.

Изменения в примере `mouthWidth` в оригинале выделены жирным:

```java
import java.beans.*;

public class FaceBean {
    private int mMouthWidth = 90;
    private PropertyChangeSupport mPcs =
        new PropertyChangeSupport(this);
    private VetoableChangeSupport mVcs =
        new VetoableChangeSupport(this);

    public int getMouthWidth() {
        return mMouthWidth;
    }
    
    public void
    setMouthWidth(int mw) throws PropertyVetoException {
        int oldMouthWidth = mMouthWidth;
        mVcs.fireVetoableChange("mouthWidth",
                                    oldMouthWidth, mw);
        mMouthWidth = mw;
        mPcs.firePropertyChange("mouthWidth",
                                 oldMouthWidth, mw);
    }

    public void
    addPropertyChangeListener(PropertyChangeListener listener) {
        mPcs.addPropertyChangeListener(listener);
    }
    
    public void
    removePropertyChangeListener(PropertyChangeListener listener) {
        mPcs.removePropertyChangeListener(listener);
    }

    public void
    addVetoableChangeListener(VetoableChangeListener listener) {
        mVcs.addVetoableChangeListener(listener);
    }
    
    public void
    removeVetoableChangeListener(VetoableChangeListener listener) {
        mVcs.removeVetoableChangeListener(listener);
    }
}
```

### Поддержка разработки в NetBeans

Шаблоны кода для создания свойств бина просты, но иногда трудно понять, всё ли вы делаете правильно.
В NetBeans есть поддержка шаблонов свойств, так что результат виден сразу по мере написания кода.

Чтобы воспользоваться этой возможностью, посмотрите на панель **Navigator**, которая обычно находится
в нижнем левом углу окна NetBeans. Как правило, эта панель работает в режиме **Members View**, который
показывает все методы и поля, определённые в текущем классе.

Щёлкните по выпадающему списку, чтобы переключиться в режим **Bean Patterns**. Вы увидите список
свойств, которые NetBeans смог вывести из ваших определений методов. NetBeans обновляет этот список
по мере набора текста, что делает его удобным способом проверить свою работу.

В следующем примере NetBeans обнаружил свойство `mouthWidth` (чтение-запись) и индексированное
свойство `testGrades` (чтение-запись). Кроме того, NetBeans распознал, что `FaceBean` допускает
регистрацию как слушателей `PropertyChangeListener`, так и слушателей `VetoableChangeListener`.

> *(В оригинале здесь изображение панели Navigator NetBeans в режиме Bean Patterns:
> `nb-bean-patterns.png`.)*

## Методы (Methods)

**Методы** (*methods*) бина — это то, что он может делать. Любой публичный метод, не являющийся
частью определения свойства, является методом бина. Когда вы используете бин в контексте
инструмента-сборщика, такого как NetBeans, методы бина можно использовать как часть вашего
приложения. Например, можно связать нажатие кнопки с вызовом одного из методов вашего бина.

## События (Events)

Класс бина может генерировать любой тип событий, включая пользовательские (*custom*) события. Как и
свойства, события распознаются по определённому шаблону имён методов.

```
public void add<Event>Listener(<Event>Listener a)
public void remove<Event>Listener(<Event>Listener a)
```

Тип слушателя (*listener*) должен быть потомком `java.util.EventListener`.

Например, кнопка Swing `JButton` — это бин, который генерирует события `action`, когда пользователь
по ней щёлкает. `JButton` включает следующие методы (фактически унаследованные от `AbstractButton`),
которые являются шаблоном бина для события:

```java
public void addActionListener(ActionListener l);
public void removeActionListener(ActionListener l);
```

События бина распознаются инструментами-сборщиками и могут использоваться для связывания компонентов
друг с другом. Например, можно связать событие `action` кнопки с каким-либо действием — скажем, с
вызовом метода другого бина.

## Использование BeanInfo (Using a BeanInfo)

Бины, особенно графические компоненты, могут иметь головокружительное количество свойств. Если ваш
класс наследуется от `Component`, `JComponent` или других классов Swing, у него уже будет более сотни
свойств. Хотя инструмент-сборщик, такой как NetBeans, упрощает редактирование свойств бина, бывает
трудно найти нужные свойства для редактирования, особенно неопытным программистам.

### Обзор BeanInfo

`BeanInfo` — это класс, который изменяет то, как ваш бин выглядит в инструменте-сборщике.
Инструмент-сборщик может опросить `BeanInfo`, чтобы выяснить, какие свойства следует отображать в
первую очередь, а какие нужно скрыть.

Класс `BeanInfo` для вашего бина должен иметь то же имя, что и класс бина, с добавленным суффиксом
`BeanInfo`. Например, классу `FaceBean` соответствует описывающий его класс `FaceBeanBeanInfo`.

Хотя реализовать класс `BeanInfo` можно и «вручную», вы обнаружите, что гораздо проще использовать
для редактирования `BeanInfo` такой инструмент, как NetBeans.

### Создание BeanInfo в NetBeans

В панели **Projects** щёлкните по имени класса вашего бина с зажатой клавишей Control и выберите в
контекстном меню пункт **BeanInfo Editor...**.

NetBeans замечает, что у вас нет `BeanInfo`, и спрашивает, хотите ли вы его создать. Нажмите **Yes**.

NetBeans создаёт новый класс и помещает вас в редактор исходного кода. Щёлкните **Designer**, чтобы
переключиться в визуальный редактор.

Выберите свойства из списка в левой части визуального редактора, затем отредактируйте их атрибуты в
правой части. Если вы не хотите, чтобы какое-либо свойство было видно разработчику, использующему
инструмент-сборщик, нажмите **Hidden**. Чтобы указать, что свойство должно отображаться раньше
других, нажмите **Preferred**. Вы также можете указать, является ли свойство связанным (*bound*)
или ограниченным (*constrained*).

Аналогичную информацию можно предоставить и для источников событий и методов бина.

Когда инструмент-сборщик загружает класс вашего бина, чтобы добавить его на палитру, он
автоматически находит соответствующий `BeanInfo` и использует его, чтобы решить, как представить
ваш бин разработчику.

## Источник

- [Writing JavaBeans Components](https://docs.oracle.com/javase/tutorial/javabeans/writing/index.html) — официальное руководство Oracle (индекс урока).
- [Properties](https://docs.oracle.com/javase/tutorial/javabeans/writing/properties.html) — свойства, включая разделы Indexed, Bound, Constrained и поддержку в NetBeans.
- [Methods](https://docs.oracle.com/javase/tutorial/javabeans/writing/methods.html) — методы бина.
- [Events](https://docs.oracle.com/javase/tutorial/javabeans/writing/events.html) — события бина.
- [Using a BeanInfo](https://docs.oracle.com/javase/tutorial/javabeans/writing/beaninfo.html) — настройка представления бина через `BeanInfo`.
