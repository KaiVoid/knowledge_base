# Урок 5. Прочие возможности Swing

**Трейл:** Creating a GUI with Swing · **Оригинал:** [Using Other Swing Features](https://docs.oracle.com/javase/tutorial/uiswing/misc/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок объединяет набор
> практических страниц («How to…»), помогающих использовать различные дополнительные возможности
> Swing: интеграцию с рабочим столом, полупрозрачные и фигурные окна, декоратор `JLayer`, действия
> (`Action`), таймеры Swing, поддержку вспомогательных технологий, подсистему фокуса, привязки
> клавиш, модальность диалогов, печать таблиц и текста, заставку (splash screen) и системный
> лоток (system tray).

Этот урок содержит коллекцию страниц-инструкций, помогающих использовать разнообразные возможности
Swing, не покрытые в других уроках трейла.

## Интеграция с классом Desktop (Desktop Class)

Java SE 6 ввела API рабочего стола — класс `java.awt.Desktop`, — чтобы сократить разрыв между
интеграцией нативных и Java-приложений. Этот API позволяет Java-приложению взаимодействовать с
приложениями, назначенными по умолчанию для определённых типов файлов на хост-платформе.

API рабочего стола позволяет приложению:

- запускать браузер хост-системы по умолчанию с указанным идентификатором ресурса (URI);
- запускать почтовый клиент хост-системы по умолчанию;
- запускать приложения для открытия, редактирования или печати файлов, ассоциированных с этими
  приложениями.

Каждое действие представлено элементом перечисления (enum) `Desktop.Action`:

- **BROWSE** — просмотр (открытие URI в браузере по умолчанию);
- **MAIL** — почта (запуск почтового клиента по умолчанию);
- **OPEN** — открытие файла приложением, ассоциированным с данным типом;
- **EDIT** — редактирование файла ассоциированным редактором;
- **PRINT** — печать файла ассоциированным приложением.

API рабочего стола опирается на файловые ассоциации хост-операционной системы. Например, если
расширение `.odt` ассоциировано с OpenOffice Writer, Java-приложение сможет открыть, отредактировать
или напечатать такой файл через OpenOffice Writer. В зависимости от системы разные приложения могут
быть назначены для разных действий над одним и тем же типом файла.

Перед использованием нужно проверить доступность API и поддержку конкретного действия:

```java
// Проверяем, доступен ли API рабочего стола
if (Desktop.isDesktopSupported()) {
    Desktop desktop = Desktop.getDesktop();
}
```

`isDesktopSupported()` проверяет доступность API рабочего стола (на Solaris и Linux он зависит от
библиотек Gnome). `getDesktop()` возвращает экземпляр `Desktop`; в «безголовом» (headless) окружении —
без клавиатуры, мыши и монитора — выбрасывается `java.awt.HeadlessException`.

```java
// Включаем только те элементы интерфейса, чьи действия поддерживаются платформой
private void enableSupportedActions() {
    if (desktop.isSupported(Desktop.Action.BROWSE)) {
        txtBrowserURI.setEnabled(true);
        btnLaunchBrowser.setEnabled(true);
    }
    if (desktop.isSupported(Desktop.Action.MAIL)) {
        txtMailTo.setEnabled(true);
        btnLaunchEmail.setEnabled(true);
    }
    if (desktop.isSupported(Desktop.Action.OPEN)) {
        rbOpen.setEnabled(true);
    }
    if (desktop.isSupported(Desktop.Action.EDIT)) {
        rbEdit.setEnabled(true);
    }
    if (desktop.isSupported(Desktop.Action.PRINT)) {
        rbPrint.setEnabled(true);
    }
}
```

Запуск браузера для отображения URI:

```java
private void onLaunchBrowser(ActionEvent evt) {
    URI uri = null;
    try {
        uri = new URI(txtBrowserURI.getText());
        desktop.browse(uri);
    } catch (IOException ioe) {
        System.out.println("Система не может найти указанный файл " + uri);
    } catch (URISyntaxException use) {
        System.out.println("Недопустимый символ в пути");
    }
}
```

Запуск почтового клиента. URI вида `mailto:` может задавать поля CC, BCC, SUBJECT, BODY
(например, `duke@example.com?SUBJECT=Hello Duke!`):

```java
private void onLaunchMail(ActionEvent evt) {
    String mailTo = txtMailTo.getText();
    URI uriMailTo = null;
    try {
        if (mailTo.length() > 0) {
            uriMailTo = new URI("mailto", mailTo, null);
            desktop.mail(uriMailTo);
        } else {
            desktop.mail();
        }
    } catch (IOException ioe) {
        ioe.printStackTrace();
    } catch (URISyntaxException use) {
        use.printStackTrace();
    }
}
```

Операции над файлами — открытие, редактирование, печать:

```java
private void onLaunchDefaultApplication(ActionEvent evt) {
    String fileName = txtFile.getText();
    File file = new File(fileName);
    try {
        switch (action) {
            case OPEN:
                desktop.open(file);
                break;
            case EDIT:
                desktop.edit(file);
                break;
            case PRINT:
                desktop.print(file);
                break;
        }
    } catch (IOException ioe) {
        System.out.println("Невозможно выполнить операцию над файлом " + file);
    }
}
```

Сводка методов класса `Desktop`: `isDesktopSupported()`, `getDesktop()`,
`isSupported(Desktop.Action)`, `browse(URI)`, `mail(URI)`, `open(File)`, `edit(File)`, `print(File)`.

## Полупрозрачные и фигурные окна (Translucent and Shaped Windows)

Начиная с Java SE 6 Update 10, в Swing-приложения можно добавлять полупрозрачные и фигурные окна.
В JDK 7 и новее эта функциональность входит в публичный пакет AWT. Поддерживаются три возможности:

1. **Равномерная полупрозрачность (uniform translucency)** — у всех пикселей окна одинаковое значение
   прозрачности (альфа). Всё окно, включая компоненты, становится равномерно прозрачным.
2. **Попиксельная полупрозрачность (per-pixel translucency)** — у каждого пикселя своё значение
   альфа; позволяет создавать окна с плавным переходом (например, градиентом от полной прозрачности
   к полной непрозрачности).
3. **Фигурные окна (shaped windows)** — окно может иметь форму любого объекта `Shape`. Фигурное окно
   может быть непрозрачным либо использовать равномерную или попиксельную полупрозрачность.

Не все платформы поддерживают все возможности. Проверка выполняется через
`GraphicsDevice.isWindowTranslucencySupported()` с одним из значений перечисления
`GraphicsDevice.WindowTranslucency`:

```java
import static java.awt.GraphicsDevice.WindowTranslucency.*;

GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
GraphicsDevice gd = ge.getDefaultScreenDevice();

boolean isUniformTranslucencySupported =
    gd.isWindowTranslucencySupported(TRANSLUCENT);
boolean isPerPixelTranslucencySupported =
    gd.isWindowTranslucencySupported(PERPIXEL_TRANSLUCENT);
boolean isShapedWindowSupported =
    gd.isWindowTranslucencySupported(PERPIXEL_TRANSPARENT);
```

- `TRANSLUCENT` — поддержка равномерной полупрозрачности;
- `PERPIXEL_TRANSLUCENT` — поддержка попиксельной полупрозрачности (нужна для эффекта затухания);
- `PERPIXEL_TRANSPARENT` — поддержка фигурных окон.

Метод `GraphicsConfiguration.isTranslucencyCapable()` проверяет поддержку `PERPIXEL_TRANSLUCENT`
для конкретной графической конфигурации. Эти возможности не работают в полноэкранном режиме —
при попытке выбрасывается `IllegalComponentStateException`.

### Равномерная полупрозрачность

Вызовите `setOpacity(float)` для окна со значением от 0 до 1 включительно; меньшее значение —
больше прозрачности. Равномерная полупрозрачность затрагивает всё окно, включая все компоненты.

```java
import java.awt.*;
import javax.swing.*;
import static java.awt.GraphicsDevice.WindowTranslucency.*;

public class TranslucentWindowDemo extends JFrame {
    public TranslucentWindowDemo() {
        super("TranslucentWindow");
        setLayout(new GridBagLayout());
        setSize(300, 200);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        add(new JButton("I am a Button"));
    }

    public static void main(String[] args) {
        // Определяем, поддерживает ли GraphicsDevice полупрозрачность
        GraphicsEnvironment ge =
            GraphicsEnvironment.getLocalGraphicsEnvironment();
        GraphicsDevice gd = ge.getDefaultScreenDevice();

        // Если полупрозрачные окна не поддерживаются — выходим
        if (!gd.isWindowTranslucencySupported(TRANSLUCENT)) {
            System.err.println("Полупрозрачность не поддерживается");
            System.exit(0);
        }

        JFrame.setDefaultLookAndFeelDecorated(true);

        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                TranslucentWindowDemo tw = new TranslucentWindowDemo();
                // Делаем окно непрозрачным на 55 % (45 % прозрачности)
                tw.setOpacity(0.55f);
                tw.setVisible(true);
            }
        });
    }
}
```

### Попиксельная полупрозрачность

Попиксельная полупрозрачность использует значения альфа от 0 (полностью прозрачно) до 255
(полностью непрозрачно). Удобный способ интерполяции между значениями альфа даёт класс
`GradientPaint`. Шаги: вызвать `setBackground(new Color(0,0,0,0))` у окна; создать `JPanel`,
переопределяющий `paintComponent()`; задать значения альфа через `GradientPaint`.

```java
import java.awt.*;
import javax.swing.*;
import static java.awt.GraphicsDevice.WindowTranslucency.*;

public class GradientTranslucentWindowDemo extends JFrame {
    public GradientTranslucentWindowDemo() {
        super("GradientTranslucentWindow");

        // Включаем попиксельную полупрозрачность
        setBackground(new Color(0, 0, 0, 0));
        setSize(new Dimension(300, 200));
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        // Панель с градиентной полупрозрачностью
        JPanel panel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                if (g instanceof Graphics2D) {
                    final int R = 240;
                    final int G = 240;
                    final int B = 240;

                    // Градиент: сверху прозрачно, снизу непрозрачно
                    Paint p = new GradientPaint(
                        0.0f, 0.0f, new Color(R, G, B, 0),          // верх: прозрачно
                        0.0f, getHeight(), new Color(R, G, B, 255), true); // низ: непрозрачно
                    Graphics2D g2d = (Graphics2D) g;
                    g2d.setPaint(p);
                    g2d.fillRect(0, 0, getWidth(), getHeight());
                }
            }
        };
        setContentPane(panel);
        setLayout(new GridBagLayout());
        add(new JButton("I am a Button"));
    }
    // main() аналогичен предыдущему примеру, но проверяет PERPIXEL_TRANSLUCENT
}
```

Попиксельная полупрозрачность затрагивает только фоновые пиксели, компоненты не изменяются.

### Фигурное окно

Используйте `setShape(Shape)` для задания формы окна. Форму следует устанавливать в обработчике
события `componentResized`, чтобы она пересчитывалась при изменении размеров окна. Оконные
украшения (декорации) не изменяют форму, поэтому фигурные окна лучше делать без декораций
(`setUndecorated(true)`).

```java
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.awt.geom.Ellipse2D;
import static java.awt.GraphicsDevice.WindowTranslucency.*;

public class ShapedWindowDemo extends JFrame {
    public ShapedWindowDemo() {
        super("ShapedWindow");
        setLayout(new GridBagLayout());

        // Рекомендуется задавать форму в обработчике componentResized:
        // при изменении размеров форма пересчитывается здесь
        addComponentListener(new ComponentAdapter() {
            @Override
            public void componentResized(ComponentEvent e) {
                // Придаём окну форму эллипса
                setShape(new Ellipse2D.Double(0, 0, getWidth(), getHeight()));
            }
        });

        setUndecorated(true);  // рекомендуется для фигурных окон
        setSize(300, 200);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        add(new JButton("I am a Button"));
    }
    // в main() проверяется PERPIXEL_TRANSPARENT; форму можно комбинировать с полупрозрачностью
}
```

Соответствие приватного API из Java SE 6 Update 10 публичному API JDK 7+: `AWTUtilities` →
`GraphicsDevice.isWindowTranslucencySupported`, `GraphicsConfiguration.isTranslucencyCapable`,
`Window.setOpacity`, `Window.setShape`, `Window.setBackground`.

## Декорирование компонентов классом JLayer

Класс `JLayer` — гибкий и мощный **декоратор** (decorator) для Swing-компонентов. Он позволяет
рисовать поверх компонента и реагировать на его события, не изменяя сам компонент. `JLayer`
работает в паре с классом `javax.swing.plaf.LayerUI`: `JLayer` оборачивает целевой компонент,
а `LayerUI` отвечает за оформление и обработку событий.

```java
JFrame f = new JFrame();
JPanel panel = createPanel();
LayerUI<JPanel> layerUI = new MyLayerUISubclass();
JLayer<JPanel> jlayer = new JLayer<JPanel>(panel, layerUI);
f.add(jlayer);
```

`JLayer` параметризуется (generics) точным типом отображаемого компонента; `LayerUI` рассчитан на
работу с `JLayer` своего типа-параметра или его предков. Класс `JLayer` объявлен `final` — всё
пользовательское поведение помещается в подкласс `LayerUI`.

`LayerUI` наследуется от `ComponentUI`. Основные переопределяемые методы: `paint(Graphics, JComponent)`
(вызывайте `super.paint(g, c)` для обычной отрисовки), `installUI(JComponent)` (инициализация при
связывании; передаётся объект `JLayer`, целевой компонент получают через `JLayer.getView()`),
`uninstallUI(JComponent)` (очистка при разрыве связи).

Простейший случай — изменить отрисовку компонента, например наложить градиент:

```java
class WallpaperLayerUI extends LayerUI<JComponent> {
    @Override
    public void paint(Graphics g, JComponent c) {
        super.paint(g, c);  // сначала рисуем содержимое компонента

        Graphics2D g2 = (Graphics2D) g.create();
        int w = c.getWidth();
        int h = c.getHeight();
        g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, .5f));
        g2.setPaint(new GradientPaint(0, 0, Color.yellow, 0, h, Color.red));
        g2.fillRect(0, 0, w, h);
        g2.dispose();
    }
}
```

### Реакция на события

`LayerUI` может получать все события своего компонента. Для этого экземпляр `JLayer` должен указать
интересующие типы событий через `setLayerEventMask()` (обычно в `installUI()`):

```java
public void installUI(JComponent c) {
    super.installUI(c);
    JLayer jlayer = (JLayer) c;
    jlayer.setLayerEventMask(
        AWTEvent.MOUSE_EVENT_MASK |
        AWTEvent.MOUSE_MOTION_EVENT_MASK);
}
```

События маршрутизируются в методы-обработчики по типу: `processMouseEvent(MouseEvent, JLayer)`,
`processMouseMotionEvent(MouseEvent, JLayer)` и т. п. Пример эффекта «прожектора» (spotlight):

```java
class SpotlightLayerUI extends LayerUI<JPanel> {
    private boolean mActive;
    private int mX, mY;

    @Override
    public void installUI(JComponent c) {
        super.installUI(c);
        JLayer jlayer = (JLayer) c;
        jlayer.setLayerEventMask(
            AWTEvent.MOUSE_EVENT_MASK | AWTEvent.MOUSE_MOTION_EVENT_MASK);
    }

    @Override
    public void uninstallUI(JComponent c) {
        JLayer jlayer = (JLayer) c;
        jlayer.setLayerEventMask(0);
        super.uninstallUI(c);
    }

    @Override
    public void paint(Graphics g, JComponent c) {
        Graphics2D g2 = (Graphics2D) g.create();
        super.paint(g2, c);  // рисуем содержимое
        if (mActive) {
            // Радиальный градиент: прозрачный в центре, тёмный по краям
            Point2D center = new Point2D.Float(mX, mY);
            float radius = 72;
            float[] dist = {0.0f, 1.0f};
            Color[] colors = {new Color(0.0f, 0.0f, 0.0f, 0.0f), Color.BLACK};
            RadialGradientPaint p = new RadialGradientPaint(center, radius, dist, colors);
            g2.setPaint(p);
            g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, .6f));
            g2.fillRect(0, 0, c.getWidth(), c.getHeight());
        }
        g2.dispose();
    }

    @Override
    protected void processMouseEvent(MouseEvent e, JLayer l) {
        if (e.getID() == MouseEvent.MOUSE_ENTERED) mActive = true;
        if (e.getID() == MouseEvent.MOUSE_EXITED) mActive = false;
        l.repaint();
    }

    @Override
    protected void processMouseMotionEvent(MouseEvent e, JLayer l) {
        Point p = SwingUtilities.convertPoint(e.getComponent(), e.getPoint(), l);
        mX = p.x;
        mY = p.y;
        l.repaint();
    }
}
```

`JLayer` поддерживает анимацию (через таймеры) и может уведомлять об изменениях свойств через
`firePropertyChange()`, что вызывает перерисовку. Один подкласс `LayerUI` можно повторно
использовать с несколькими экземплярами `JLayer`.

## Использование действий (Actions)

Объект **действия** (`Action`) позволяет отделить функциональность и состояние от компонента. Если
два или более компонента выполняют одну и ту же функцию, разумно реализовать её через `Action`.
`Action` — это слушатель действий (action listener), который обеспечивает не только обработку
события действия, но и централизованное управление состоянием порождающих событие компонентов
(кнопок панели инструментов, пунктов меню, обычных кнопок, текстовых полей). Управляемое состояние
включает текст, значок, мнемонику, признаки «включено» и «выбрано».

Обычно действие присоединяют к компоненту методом `setAction`. При его вызове:

- состояние компонента приводится в соответствие со состоянием `Action` (например, текст и значок);
- `Action` регистрируется как слушатель действий компонента;
- при изменении состояния `Action` состояние компонента обновляется (например, при изменении
  признака «включено» все присоединённые компоненты меняют его одновременно).

Создание панельной кнопки и пункта меню, выполняющих одну функцию:

```java
Action leftAction = new LeftAction(); // код LeftAction приведён ниже
...
button = new JButton(leftAction);
...
menuItem = new JMenuItem(leftAction);
```

Обычно создают подкласс `AbstractAction` и реализуют метод `actionPerformed`:

```java
leftAction = new LeftAction("Go left", anIcon,
             "This is the left button.",
             new Integer(KeyEvent.VK_L));
...
class LeftAction extends AbstractAction {
    public LeftAction(String text, ImageIcon icon,
                      String desc, Integer mnemonic) {
        super(text, icon);
        putValue(SHORT_DESCRIPTION, desc);   // краткое описание (для подсказки)
        putValue(MNEMONIC_KEY, mnemonic);    // мнемоника
    }
    public void actionPerformed(ActionEvent e) {
        displayResult("Action for first button/menu item", e);
    }
}
```

Кнопка и пункт меню отобразят текст и значок действия, мнемонику `L`, а текст подсказки (tool tip)
будет составлен из строки `SHORT_DESCRIPTION` и представления мнемоники.

Отключение действия (и одновременно всех присоединённых компонентов):

```java
boolean selected = ...; // true — действие включено, false — выключено
leftAction.setEnabled(selected);
```

После создания компонентов их можно донастроить, например убрать значок или текст:

```java
menuItem = new JMenuItem();
menuItem.setAction(leftAction);
menuItem.setIcon(null);   // в меню решили не использовать значок
...
button = new JButton();
button.setAction(leftAction);
button.setText("");       // кнопка только со значком
```

> **Примечание.** При изменении свойства `Action` компонент может снова сбросить значок и текст из
> `Action`.

Действие можно напрямую назначить компонентам `AbstractButton`, `JComboBox`, `JTextField` (и их
подклассам) через `setAction`. Конструкторы `AbstractAction`: без аргументов, `(String)`,
`(String, Icon)`. Методы: `setEnabled(boolean)`/`isEnabled()`, `putValue(String, Object)`/`getValue(String)`.

Стандартные свойства действия: `ACCELERATOR_KEY` (акселератор `KeyStroke` для `JMenuItem`),
`ACTION_COMMAND_KEY` (командная строка `ActionEvent`), `LONG_DESCRIPTION` (длинное описание,
например для контекстной справки), `MNEMONIC_KEY` (мнемоника), `NAME` (имя/текст),
`SHORT_DESCRIPTION` (краткое описание, обычно подсказка), `SMALL_ICON` (значок для панели/кнопки).

## Таймеры Swing (Swing Timers)

Таймер Swing (`javax.swing.Timer`) генерирует одно или несколько событий действия после заданной
задержки. Не путайте его с универсальным таймером из пакета `java.util`. Таймеры Swing рекомендуются
для задач, связанных с GUI, потому что все они используют один общий поток таймера, а сама задача
автоматически выполняется в **потоке диспетчеризации событий** (event dispatch thread, EDT). Если
из таймера не предполагается обращаться к GUI или требуется длительная обработка, лучше взять
универсальный таймер.

Два основных способа применения: выполнить задачу **однократно** после задержки (например, менеджер
подсказок решает, когда показать и скрыть подсказку) и выполнять задачу **многократно** (например,
анимация или обновление индикатора прогресса).

При создании таймера задают слушателя действий (его метод `actionPerformed` содержит код задачи) и
число миллисекунд между срабатываниями:

```java
timer = new Timer(speed, this);   // speed — задержка в мс, this — ActionListener
timer.setInitialDelay(pause);     // задержка перед первым срабатыванием
timer.setRepeats(false);          // сработать только один раз
timer.start();                    // запуск
timer.stop();                     // приостановка
timer.restart();                  // перезапуск
```

> **Важно.** Задача таймера выполняется в EDT, поэтому может безопасно изменять компоненты, но должна
> выполняться быстро. Для долгих операций используйте `SwingWorker` вместо таймера или вместе с ним.

Пример из апплета `TumbleItem` (анимация): таймер создаётся и запускается с задержкой первого
события, обработчик `actionPerformed` на каждом срабатывании обновляет индекс кадра и смещение,
вызывает перерисовку, а в конце цикла перезапускает таймер для короткой паузы перед повтором.

```java
public void actionPerformed(ActionEvent e) {
    // Пока идёт загрузка, анимировать нельзя
    if (!worker.isDone()) {
        return;
    }
    loopslot++;
    if (loopslot >= nimgs) {
        loopslot = 0;
        off += offset;
        if (off < 0) {
            off = width - maxWidth;
        } else if (off + maxWidth > width) {
            off = 0;
        }
    }
    animator.repaint();
    if (loopslot == nimgs - 1) {
        timer.restart();
    }
}
```

## Поддержка вспомогательных технологий (Assistive Technologies)

Вспомогательные технологии (assistive technologies) — голосовые интерфейсы, программы чтения с
экрана, альтернативные устройства ввода — позволяют людям с ограниченными возможностями эффективно
работать за компьютером (а также полезны, например, для голосового доступа к почте за рулём). Они
получают сведения о компонентах через **API доступности** (Accessibility API) из пакета
`javax.accessibility`.

Ключевой принцип: Swing-компоненты уже имеют встроенную поддержку API доступности, поэтому программа,
скорее всего, заработает со вспомогательными технологиями автоматически. Однако соблюдение правил
заметно улучшает опыт пользователя.

Правила поддержки доступности:

1. **Задавайте имена компонентам** без видимого текста (кнопки-картинки, панели, текстовые области)
   через `setAccessibleName()`.
2. **Задавайте осмысленные подсказки** (tool tips): `aJComponent.setToolTipText("...")`.
3. **Если подсказки нет — задавайте описание явно:**
   `aJComponent.getAccessibleContext().setAccessibleDescription("...")`.
4. **Поддерживайте навигацию с клавиатуры** (спрячьте мышь и проверьте): мнемоники `setMnemonic()`,
   акселераторы меню, привязки клавиш для прочих компонентов.
5. **Описывайте значки-картинки** (`ImageIcon`), например задавая описание в конструкторе:
   `createImageIcon("images/flyingBee.jpg", "Фотография летящей пчелы.")`.
6. **Группируйте связанные компоненты** в контейнеры вроде `JPanel`.
7. **Связывайте метки с компонентами** через `label.setLabelFor(textField)`.
8. **Делайте доступными пользовательские компоненты** — прямые подклассы `JComponent` должны явно
   реализовывать доступность.
9. **Тестируйте** доступность утилитами (например, Monkey).
10. **Не ломайте унаследованную доступность** — не создавайте недоступные контейнеры, скрывающие
    вложенные компоненты.

Архитектура доступности опирается на три понятия. Компонент реализует интерфейс `Accessible` с
единственным методом:

```java
public AccessibleContext getAccessibleContext();
```

`AccessibleContext` — абстрактный класс, дающий минимум сведений (имя, описание, роль, набор
состояний). У каждого Swing-компонента контекст называется `ИмяКомпонента.AccessibleИмяКомпонента`
(например, `JButton.AccessibleJButton`). Контекст может реализовывать специализированные интерфейсы:
`AccessibleAction`, `AccessibleComponent`, `AccessibleText`, `AccessibleValue`, `AccessibleSelection`.

Поскольку `JComponent` не реализует `Accessible`, его прямые подклассы должны делать это явно:

```java
public class Corner extends JComponent implements Accessible {

    protected void paintComponent(Graphics g) {
        g.setColor(new Color(230, 163, 4));
        g.fillRect(0, 0, getWidth(), getHeight());
    }

    public AccessibleContext getAccessibleContext() {
        if (accessibleContext == null) {
            accessibleContext = new AccessibleCorner();
        }
        return accessibleContext;
    }

    // Наследуем всё от AccessibleJComponent
    protected class AccessibleCorner extends AccessibleJComponent {
    }
}
```

Для нестандартной роли и состояний переопределяют `getAccessibleRole()` и `getAccessibleStateSet()`,
а при необходимости создают собственные подклассы `AccessibleRole` и `AccessibleState`.

## Подсистема фокуса (Focus Subsystem)

Подсистема фокуса управляет тем, какой компонент получает ввод с клавиатуры. В каждый момент в окне
фокус клавиатуры есть только у одного компонента. **Владелец фокуса** (focus owner) — компонент,
получающий ввод; **окно с фокусом** (focused window) — содержащее его окно; всем управляет
`KeyboardFocusManager`. Компонент получает фокус по щелчку, по клавише Tab, программно через
`requestFocusInWindow()` или когда его окно становится активным.

Установка начального фокуса (вызывать после `pack()`, до `setVisible()`):

```java
JFrame frame = new JFrame("Test");
JButton button = new JButton("I am first");
panel.add(button);
frame.getContentPane().add(panel);
frame.pack();
button.requestFocusInWindow();  // после pack(), перед setVisible()
frame.setVisible(true);
```

**Цикл фокуса** (focus cycle) — набор компонентов с общим предком; **корень цикла** — корневой
контейнер (по умолчанию `JWindow`, `JInternalFrame`, `JFrame`, `JDialog` и т. п.). Порядок обхода
задаёт **политика обхода фокуса** (`FocusTraversalPolicy`); по умолчанию Swing использует
`LayoutFocusTraversalPolicy`, упорядочивающую компоненты по факторам компоновки (размер,
расположение, ориентация). Клавиши обхода по умолчанию: вперёд — Tab, Ctrl+Tab; назад — Shift+Tab,
Ctrl+Shift+Tab.

```java
// Добавляем Enter к клавишам обхода «вперёд»
Set forwardKeys = getFocusTraversalKeys(
    KeyboardFocusManager.FORWARD_TRAVERSAL_KEYS);
Set newForwardKeys = new HashSet(forwardKeys);
newForwardKeys.add(KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, 0));
setFocusTraversalKeys(KeyboardFocusManager.FORWARD_TRAVERSAL_KEYS, newForwardKeys);
```

Своя политика обхода: `frame.setFocusTraversalPolicy(newPolicy)` (передача `null` восстанавливает
стандартную). Исключить компонент из цикла фокуса: `setFocusable(false)`.

**Проверка ввода** перед передачей фокуса выполняется через `InputVerifier`: метод `verify(JComponent)`
проверяет корректность без побочных эффектов, `shouldYieldFocus(JComponent)` может иметь побочные
эффекты (диалоги, исправления) и возвращает разрешение на передачу фокуса. Устанавливается через
`amountField.setInputVerifier(verifier)`.

Чтобы пользовательский компонент мог получать фокус, он должен быть видимым, включённым и фокусируемым
(`setFocusable(true)`), как правило, с запросом фокуса по щелчку (`requestFocusInWindow()`).

> **Важно.** Передача фокуса асинхронна. Запрашивайте фокус **после** изменений, которые могут на него
> повлиять (отключение компонента, скрытие, удаление). Например, сначала `start.setEnabled(false)`,
> затем `cancel.requestFocusInWindow()`.

## Привязки клавиш (Key Bindings)

Класс `JComponent` поддерживает **привязки клавиш** (key bindings) как способ реагировать на нажатие
отдельных клавиш. Они уместны, когда нужно: добавить клавиатурный доступ к пользовательскому
компоненту; переопределить поведение существующей привязки; назначить новую комбинацию для
существующего действия. За кулисами привязки клавиш используются мнемониками (все кнопки, вкладки,
`JLabel`) и акселераторами (пункты меню).

Альтернатива — слушатели клавиш (key listeners), низкоуровневый интерфейс к вводу. Привязки клавиш
предпочтительнее: они самодокументируемы, учитывают иерархию вложенности, поощряют повторно
используемые фрагменты кода (объекты `Action`), позволяют легко удалять, настраивать и разделять
действия и менять назначенную клавишу. Дополнительное преимущество `Action` — состояние «включено»,
позволяющее отключить действие, не отслеживая, к какому компоненту оно присоединено.

Привязки опираются на классы `InputMap` и `ActionMap`: карта ввода связывает комбинации клавиш
(key strokes) с именами действий, а карта действий — имена с самими действиями. Технически в качестве
«ключа» можно использовать любой объект, но по соглашению берут строку с именем действия. У каждой
`InputMap`/`ActionMap` есть родитель (обычно от внешнего вида — look and feel), который сбрасывается
при смене look and feel, поэтому заданные разработчиком привязки не теряются.

У каждого `JComponent` одна карта действий и три карты ввода, соответствующие ситуациям фокуса:

- **`JComponent.WHEN_FOCUSED`** — компонент имеет фокус клавиатуры. Применяется для компонентов без
  потомков (например, кнопки привязывают пробел через эту карту).
- **`JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT`** — компонент содержит фокусируемый компонент (или
  сам им является). Применяется для составных компонентов (например, `JTable` делает все привязки
  через эту карту, чтобы стрелки работали даже при редактировании ячейки).
- **`JComponent.WHEN_IN_FOCUSED_WINDOW`** — окно компонента имеет фокус или содержит фокусируемый
  компонент. Применяется для мнемоник и акселераторов, активных независимо от места фокуса в окне.

При нажатии клавиши код обработки `JComponent` ищет действительную привязку в картах ввода в порядке:
1) `WHEN_FOCUSED` фокусируемого компонента; 2) его `WHEN_ANCESTOR_OF_FOCUSED_COMPONENT`; 3) такие же
карты его предков вверх по иерархии (карты отключённых компонентов пропускаются); 4) карты
`WHEN_IN_FOCUSED_WINDOW` всех включённых компонентов окна. Если привязок несколько, используется
первая действительная; **избегайте дублирующихся привязок `WHEN_IN_FOCUSED_WINDOW`** — порядок
обхода компонентов непредсказуем. Если найденное действие отключено, поиск продолжается.

Назначение реакции на клавишу F2:

```java
component.getInputMap().put(KeyStroke.getKeyStroke("F2"), "doSomething");
component.getActionMap().put("doSomething", anAction);
// где anAction — это javax.swing.Action
```

Карта действий — через `getActionMap()`, карта ввода — через `getInputMap(int)` с одной из констант
`JComponent.WHEN_*` (без аргументов — `WHEN_FOCUSED`). Комбинация клавиш задаётся через
`KeyStroke.getKeyStroke(String)`. Реакция на нажатие и отпускание пробела (как щелчок мыши):

```java
component.getInputMap().put(KeyStroke.getKeyStroke("SPACE"), "pressed");
component.getInputMap().put(KeyStroke.getKeyStroke("released SPACE"), "released");
component.getActionMap().put("pressed", pressedAction);
component.getActionMap().put("released", releasedAction);
```

Чтобы компонент игнорировал клавишу, используют специальное имя действия `"none"`:

```java
component.getInputMap().put(KeyStroke.getKeyStroke("F2"), "none");
```

> **Примечание.** `"none"` не препятствует поиску F2 в картах `WHEN_ANCESTOR_OF_FOCUSED_COMPONENT` и
> `WHEN_IN_FOCUSED_WINDOW`. Чтобы полностью подавить реакцию, привяжите действительное действие,
> ничего не делающее (`AbstractAction` с пустым `actionPerformed`).

## Модальность диалогов (Modality in Dialogs)

Java SE 6 ввела улучшенную модель модальности, позволяющую ограничивать область блокировки
диалогового окна. **Диалоговое окно** — всплывающее окно верхнего уровня с заголовком и рамкой,
обычно принимающее ввод. **Модальное** окно блокирует ввод в некоторые другие окна верхнего уровня
приложения (кроме окон, для которых оно является владельцем), удерживая фокус до закрытия.
**Немодальное** (modeless) окно позволяет работать с другими окнами. В Java SE 6 и модальные, и
немодальные окна всегда отображаются поверх своих родителей и всех заблокированных окон.

Типы модальности (`Dialog.ModalityType`):

- **Немодальный (MODELESS)** — не блокирует никакие окна.
- **Документ-модальный (DOCUMENT_MODAL)** — блокирует все окна одного документа, кроме окон своей
  дочерней иерархии. Документ — иерархия окон с общим предком (корнем документа), то есть ближайшим
  окном-предком без владельца.
- **Приложение-модальный (APPLICATION_MODAL)** — блокирует все окна приложения, кроме дочерней
  иерархии.
- **Тулкит-модальный (TOOLKIT_MODAL)** — блокирует все окна, работающие в одном тулките (toolkit),
  кроме дочерней иерархии.

Любое окно верхнего уровня можно пометить как **не блокируемое** модальными диалогами через режим
исключения (`Dialog.ModalExclusionType`): `NO_EXCLUDE` (по умолчанию), `APPLICATION_EXCLUDE`,
`TOOLKIT_EXCLUDE`. Системная модальность (блокировка всех приложений рабочего стола) новой моделью
не реализуется.

```java
// Родительский фрейм
f1 = new JFrame("Book 1 (parent frame)");
// Немодальный диалог
d2 = new JDialog(f1);
// Документ-модальный диалог
d3 = new JDialog(d2, "", Dialog.ModalityType.DOCUMENT_MODAL);
...
// Исключённый фрейм
f7 = new JFrame("Classics (excluded frame)");
f7.setModalityExclusionType(Dialog.ModalExclusionType.APPLICATION_EXCLUDE);
```

Метод `setModalityType(Dialog.ModalityType)` задаёт тип модальности (если он не поддерживается,
применяется `MODELESS`; для проверки вызовите `getModalityType()` после установки). В Java SE 6
можно создать документ-модальный диалог без родителя: так как `Dialog` — подкласс `Window`, без
владельца он становится корнем документа, его область блокировки пуста, и он ведёт себя как
немодальный.

## Печать таблиц (Printing Tables)

Класс `JTable` обеспечивает поддержку печати через метод `print()`. Простейший вызов без параметров
показывает диалог печати и печатает интерактивно в режиме `FIT_WIDTH` без колонтитулов:

```java
try {
    boolean complete = table.print();
    if (complete) {
        /* показать сообщение об успехе */
    } else {
        /* сообщить, что печать отменена */
    }
} catch (PrinterException pe) {
    /* печать не удалась — сообщить пользователю */
}
```

Полная сигнатура даёт расширенный контроль:

```java
boolean complete = table.print(JTable.PrintMode printMode,
                               MessageFormat headerFormat,
                               MessageFormat footerFormat,
                               boolean showPrintDialog,
                               PrintRequestAttributeSet attr,
                               boolean interactive,
                               PrintService service);
```

Режимы печати: **`PrintMode.NORMAL`** — таблица печатается в текущем размере, не помещающиеся столбцы
переносятся на дополнительные страницы; **`PrintMode.FIT_WIDTH`** — таблица при необходимости
масштабируется, чтобы все столбцы умещались по ширине страницы (с сохранением пропорций), строки
распределяются по страницам.

Колонтитулы (header/footer) задаются объектами `MessageFormat` и центрируются; номер страницы
вставляется через `{0}`:

```java
MessageFormat footer = new MessageFormat("Page - {0}");
```

> **Примечание.** Общее число страниц до печати неизвестно, поэтому формат «Page 1 of 5» невозможен.

В **интерактивном** режиме показывается модальный диалог прогресса с возможностью отмены; в
**неинтерактивном** печать сразу выполняется в EDT, полностью блокируя события GUI (рекомендуется лишь
для невидимых GUI-приложений). Переопределение `getPrintable(...)` позволяет настроить печать, обернув
стандартный `Printable`. Метод `JComponent.isPaintingForPrint()` позволяет рисовать иначе для печати,
чем для экрана.

## Печать текста (Printing Text)

Класс `JTextComponent` поддерживает печать текстовых документов (HTML, RTF, обычный текст). Простейший
вызов `print()` без параметров показывает диалог печати и печатает интерактивно без колонтитулов:

```java
try {
    boolean complete = textComponent.print();
    if (complete) {
        /* показать сообщение об успехе */
    } else {
        /* сообщить, что печать отменена */
    }
} catch (PrinterException pe) {
    /* печать не удалась — сообщить пользователю */
}
```

Полная сигнатура с контролем колонтитулов, диалога, службы печати, атрибутов и интерактивности:

```java
boolean complete = textComponent.print(MessageFormat headerFormat,
                                       MessageFormat footerFormat,
                                       boolean showPrintDialog,
                                       PrintService service,
                                       PrintRequestAttributeSet attributes,
                                       boolean interactive);
```

Колонтитулы задаются через `MessageFormat`, номер страницы — `{0}`; «Page X of Y» невозможен.
Интерактивный режим показывает диалог прогресса (модальный в EDT). Для больших документов печать
выполняют в фоновом потоке через `SwingWorker`:

```java
private class PrintingTask extends SwingWorker<Object, Object> {
    @Override
    protected Object doInBackground() {
        try {
            complete = text.print(headerFormat, footerFormat,
                    true, null, null, interactive);
        } catch (PrinterException ex) {
            // обработка ошибки
        }
        return null;
    }
}
...
PrintingTask task = new PrintingTask(header, footer, interactive);
task.execute();
```

На время печати документ должен оставаться неизменным; метод `print()` отключает компонент на время
печати. Если служба печати (`PrintService`) не указана, используется принтер по умолчанию.

## Создание заставки (Splash Screen)

Почти все современные приложения показывают **заставку** (splash screen): для рекламы продукта,
индикации запуска при долгой инициализации или однократного сообщения. Java SE 6+ предоставляет
нативное решение, отображающее заставку **до** полной инициализации JVM, что минимизирует задержку.
Поддерживаются изображения `gif`, `png`, `jpeg` с прозрачностью, полупрозрачностью и анимацией.

Заставкой управляет класс `SplashScreen`. Приложение не может создать его экземпляр напрямую:
существует единственный экземпляр, доступный через статический метод `getSplashScreen()` (возвращает
`null`, если заставка при старте не создавалась). Методы: `createGraphics()` (создаёт `Graphics2D` для
рисования поверх заставки), `getBounds()` (границы окна как `Rectangle`), `close()` (закрытие и
освобождение ресурсов).

```java
final SplashScreen splash = SplashScreen.getSplashScreen();
if (splash == null) {
    System.out.println("SplashScreen.getSplashScreen() вернул null");
    return;
}
Graphics2D g = splash.createGraphics();
if (g == null) {
    System.out.println("g равно null");
    return;
}
// Рисуем поверх заставки динамическую информацию
```

Поверхность заставки имеет альфа-канал, доступный через обычный интерфейс `Graphics2D`. Задать
заставку можно двумя способами. Через опцию запуска `-splash:`:

```bash
java -splash:images/splash.gif misc.SplashDemo
```

Или через манифест JAR-файла (атрибут `SplashScreen-Image`):

```manifest
Manifest-Version: 1.0
Main-Class: misc.SplashDemo
SplashScreen-Image: images/splash.gif
```

Заставка появляется значительно раньше Swing-аналогов, поскольку загрузчик приложения декодирует и
показывает изображение ещё до полной инициализации JVM. Фиксированные координаты для вывода
накладываемой информации зависят от изображения и рассчитываются индивидуально.

## Системный лоток (System Tray)

Системный лоток (system tray) — специальная область рабочего стола для доступа к запущенным
программам. На разных ОС он называется по-разному: «область уведомлений панели задач» (Windows),
«область уведомлений» (GNOME), «системный лоток» (KDE). Лоток общий для всех приложений рабочего стола.

Класс `java.awt.SystemTray` (с Java SE 6) представляет системный лоток. Приложение не может создать
его экземпляр — существует единственный, получаемый через `getSystemTray()`. Перед доступом следует
проверить поддержку статическим методом `isSupported()`; иначе `getSystemTray()` выбросит
`java.lang.UnsupportedOperationException`.

```java
// Проверяем поддержку системного лотка
if (!SystemTray.isSupported()) {
    System.out.println("SystemTray не поддерживается");
    return;
}
final SystemTray tray = SystemTray.getSystemTray();
```

Класс `TrayIcon` представляет значок в лотке. У значка могут быть изображение (автоматически
масштабируется), текстовая подсказка, всплывающее меню и слушатели событий мыши.

```java
final TrayIcon trayIcon = new TrayIcon(createImage("images/bulb.gif", "tray icon"));
try {
    tray.add(trayIcon);   // добавляем значок в лоток
} catch (AWTException e) {
    System.out.println("Не удалось добавить TrayIcon.");
}
...
tray.remove(trayIcon);    // удаляем значок, когда он больше не нужен
```

Метод `add()` может выбросить `AWTException`, если значок нельзя добавить (например, в X-Window
лоток отсутствует). Всплывающее меню создаётся средствами AWT (`PopupMenu`, а **не** Swing-овский
`JPopupMenu`):

```java
final PopupMenu popup = new PopupMenu();
MenuItem aboutItem = new MenuItem("About");
CheckboxMenuItem cb1 = new CheckboxMenuItem("Set auto size");
...
popup.add(aboutItem);
popup.addSeparator();
popup.add(cb1);
...
trayIcon.setPopupMenu(popup);   // привязываем меню к значку
```

По умолчанию правый щелчок показывает меню, двойной щелчок порождает `ActionEvent`. Прочие методы:
`setToolTip(String)` (подсказка), `setImageAutoSize(boolean)` (авторазмер, по умолчанию `false`),
`addActionListener(ActionListener)`. `TrayIcon` поддерживает «всплывающие» сообщения-баллоны
(error, warning, info или обычные).

> **Ограничение.** Текущая реализация `TrayIcon` поддерживает только AWT-меню (`PopupMenu`), но не
> Swing-аналог `JPopupMenu`; нельзя использовать `JMenuItem` со значками, `JRadioButtonMenuItem`,
> `JCheckBoxMenuItem` (см. Bug ID 6285881).

## Решение типичных проблем

**Приложение не показывает запрошенный внешний вид (look and feel).** Вероятно, задан недопустимый
look and feel либо он установлен после того, как UI-менеджер загрузил вид по умолчанию. Если вид
корректен и устанавливается первым делом (в начале `main`), проверьте, нет ли статического поля,
ссылающегося на Swing-класс: такая ссылка может вызвать загрузку вида по умолчанию.

**Компонент не получает фокус.** Если это пользовательский компонент (прямой подкласс `JComponent`),
ему может потребоваться карта ввода и слушатель мыши. Если компонент находится внутри `JWindow`, для
получения фокуса его компонентами нужно, чтобы окно-владелец `JWindow` было видимым; решение — задать
видимый фокусируемый фрейм-владелец либо использовать `JDialog`/`JFrame`.

**Диалог не получает событие клавиши Escape.** Если диалог содержит текстовое поле, оно может
поглощать событие. Чтобы получить Escape независимо от поглощения, используйте `KeyEventDispatcher`;
чтобы получить только непоглощённое — зарегистрируйте привязку клавиши на любом `JComponent` диалога
в карте `WHEN_IN_FOCUSED_WINDOW`.

**Нельзя применить Swing-компоненты к значку лотка.** Текущая реализация `TrayIcon` поддерживает
`PopupMenu`, но не Swing-аналог `JPopupMenu`. Пока нет класса `JTrayIcon`, используйте AWT-компоненты
для пунктов меню, флажков и подменю.

## Источник

- [Lesson: Using Other Swing Features](https://docs.oracle.com/javase/tutorial/uiswing/misc/index.html) — официальное руководство Oracle.
- [How to Integrate with the Desktop Class](https://docs.oracle.com/javase/tutorial/uiswing/misc/desktop.html)
- [How to Create Translucent and Shaped Windows](https://docs.oracle.com/javase/tutorial/uiswing/misc/trans_shaped_windows.html)
- [How to Decorate Components with the JLayer Class](https://docs.oracle.com/javase/tutorial/uiswing/misc/jlayer.html)
- [How to Use Actions](https://docs.oracle.com/javase/tutorial/uiswing/misc/action.html)
- [How to Use Swing Timers](https://docs.oracle.com/javase/tutorial/uiswing/misc/timer.html)
- [How to Support Assistive Technologies](https://docs.oracle.com/javase/tutorial/uiswing/misc/access.html)
- [How to Use the Focus Subsystem](https://docs.oracle.com/javase/tutorial/uiswing/misc/focus.html)
- [How to Use Key Bindings](https://docs.oracle.com/javase/tutorial/uiswing/misc/keybinding.html)
- [How to Use Modality in Dialogs](https://docs.oracle.com/javase/tutorial/uiswing/misc/modality.html)
- [How to Print Tables](https://docs.oracle.com/javase/tutorial/uiswing/misc/printtable.html)
- [How to Print Text](https://docs.oracle.com/javase/tutorial/uiswing/misc/printtext.html)
- [How to Create a Splash Screen](https://docs.oracle.com/javase/tutorial/uiswing/misc/splashscreen.html)
- [How to Use the System Tray](https://docs.oracle.com/javase/tutorial/uiswing/misc/systemtray.html)
- [Solving Common Problems Using Other Swing Features](https://docs.oracle.com/javase/tutorial/uiswing/misc/problems.html)
