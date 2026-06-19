# Урок 6. Продвинутые темы Java 2D API

**Трейл:** 2D Graphics · **Оригинал:** [Advanced topics in the Java 2D API](https://docs.oracle.com/javase/tutorial/2d/advanced/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> *Advanced Topics in Java2D*, *Transforming Shapes, Text, and Images*, *Clipping the Drawing Region*,
> *Compositing Graphics*, *Controlling Rendering Quality*, *Constructing Complex Shapes from Geometry
> Primitives* и *Supporting User Interaction*.

Этот урок показывает, как использовать `Graphics2D` для отображения графики с эффектными стилями
контура (outline) и заливки (fill), как преобразовывать графику при отрисовке (rendering), как
ограничивать отрисовку заданной областью и как в целом управлять видом графики при её выводе.
Вы также научитесь создавать сложные объекты `Shape`, комбинируя простые, и определять, когда
пользователь щёлкает по отображённому графическому примитиву. Эти темы рассматриваются в следующих
разделах.

## Преобразование фигур, текста и изображений

Чтобы при отрисовке перемещать, поворачивать, масштабировать и наклонять (move, rotate, scale,
shear) графические примитивы, можно изменить атрибут преобразования (transform attribute) в
контексте `Graphics2D`. Атрибут преобразования задаётся экземпляром класса
[`AffineTransform`](https://docs.oracle.com/javase/8/docs/api/java/awt/geom/AffineTransform.html).
Аффинное преобразование (affine transform) — это такое преобразование, как сдвиг (translate),
поворот (rotate), масштабирование (scale) или наклон (shear), при котором параллельные прямые
остаются параллельными и после преобразования.

Класс [`Graphics2D`](https://docs.oracle.com/javase/8/docs/api/java/awt/Graphics2D.html)
предоставляет несколько методов для изменения атрибута преобразования. Вы можете создать новый
`AffineTransform` и изменить атрибут преобразования `Graphics2D`, вызвав `transform`.

`AffineTransform` определяет следующие фабричные методы (factory methods), упрощающие создание
новых преобразований:

* `getRotateInstance`
* `getScaleInstance`
* `getShearInstance`
* `getTranslateInstance`

Также можно использовать один из методов преобразования `Graphics2D` для изменения текущего
преобразования. Когда вы вызываете один из этих удобных методов, результирующее преобразование
конкатенируется (concatenated) с текущим преобразованием и применяется во время отрисовки:

* `rotate` — задаёт угол поворота в радианах;
* `scale` — задаёт коэффициент масштабирования по осям *x* и *y*;
* `shear` — задаёт коэффициент наклона по осям *x* и *y*;
* `translate` — задаёт смещение сдвига по осям *x* и *y*.

Кроме того, можно напрямую создать объект `AffineTransform` и конкатенировать его с текущим
преобразованием, вызвав метод `transform`.

Метод `drawImage` также перегружен (overloaded) так, что позволяет задать `AffineTransform`,
применяемый к изображению при его отрисовке. Указание преобразования при вызове `drawImage`
не влияет на атрибут преобразования `Graphics2D`.

### Пример: Transform

Следующая программа аналогична `StrokeandFill`, но дополнительно позволяет пользователю выбрать
преобразование, применяемое к выбранному объекту при его отрисовке.

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этого апплета содержится в файле `Transform.java`.

Когда из меню Transform выбирается преобразование, оно конкатенируется с `AffineTransform` `at`:

```java
public void setTrans(int transIndex) {
    // Задаёт AffineTransform.
    switch ( transIndex ) {
    case 0 :
        at.setToIdentity();
        at.translate(w/2, h/2);
        break;
    case 1 :
        at.rotate(Math.toRadians(45));
        break;
    case 2 :
        at.scale(0.5, 0.5);
        break;
    case 3 :
        at.shear(0.5, 0.0);
        break;
    }
}
```

Перед отображением фигуры, соответствующей выбору в меню, приложение сначала извлекает текущее
преобразование из объекта `Graphics2D`:

```java
AffineTransform saveXform = g2.getTransform();
```

Это преобразование будет восстановлено в `Graphics2D` после отрисовки.

После извлечения текущего преобразования создаётся ещё один `AffineTransform` — `toCenterAt`,
благодаря которому фигуры отрисовываются в центре панели. `AffineTransform` `at`
конкатенируется с `toCenterAt`:

```java
AffineTransform toCenterAt = new AffineTransform();
toCenterAt.concatenate(at);
toCenterAt.translate(-(r.width/2), -(r.height/2));
```

Преобразование `toCenterAt` конкатенируется с преобразованием `Graphics2D` с помощью метода
`transform`:

```java
g2.transform(toCenterAt);
```

После завершения отрисовки исходное преобразование восстанавливается методом `setTransform`:

```java
g2.setTransform(saveXform);
```

> **Примечание.** Никогда не используйте метод `setTransform` для того, чтобы конкатенировать
> координатное преобразование с уже существующим. Метод `setTransform` перезаписывает текущее
> преобразование объекта `Graphics2D`, которое может быть нужно для других целей — например, для
> позиционирования Swing- и легковесных (lightweight) компонентов в окне. Чтобы выполнять
> преобразования, используйте следующие шаги:
>
> 1. Методом `getTransform` получите текущее преобразование.
> 2. Методами `transform`, `translate`, `scale`, `shear` или `rotate` конкатенируйте преобразование.
> 3. Выполните отрисовку.
> 4. Восстановите исходное преобразование методом `setTransform`.

## Ограничение области отрисовки (clipping)

Любой объект `Shape` можно использовать как путь отсечения (clipping path), ограничивающий ту часть
области рисования, которая будет отрисована. Путь отсечения является частью контекста `Graphics2D`;
чтобы задать атрибут отсечения (clip attribute), вызовите `Graphics2D.setClip` и передайте `Shape`,
определяющий нужный путь отсечения. Сузить путь отсечения можно вызовом метода `clip` с передачей
другого `Shape`; в этом случае отсечение устанавливается равным пересечению (intersection) текущего
отсечения и заданного `Shape`.

### Пример: ClipImage

Этот пример анимирует путь отсечения, открывая разные части изображения.

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этого апплета содержится в файле `ClipImage.java`. Апплету требуется файл изображения
`clouds.jpg`.

Путь отсечения определяется пересечением эллипса и прямоугольника, размеры которых задаются
случайным образом. Эллипс передаётся в метод `setClip`, затем вызывается `clip`, чтобы установить
путь отсечения равным пересечению эллипса и прямоугольника.

```java
private Ellipse2D ellipse = new Ellipse2D.Float();
private Rectangle2D rect = new Rectangle2D.Float();
...
ellipse.setFrame(x, y, ew, eh);
g2.setClip(ellipse);
rect.setRect(x+5, y+5, ew-10, eh-10);
g2.clip(rect);
```

### Пример: Starry

Область отсечения можно также создать из текстовой строки. В следующем примере создаётся
`TextLayout` со строкой *The Starry Night*. Затем берётся контур (outline) этого `TextLayout`.
Метод `TextLayout.getOutline` возвращает объект `Shape`, и из границ (bounds) этого объекта `Shape`
создаётся `Rectangle`. Эти границы содержат все пиксели, которые может нарисовать раскладка
(layout). Цвет в графическом контексте устанавливается синим, и рисуется фигура-контур, как
показано на следующем изображении и фрагменте кода.

```java
FontRenderContext frc = g2.getFontRenderContext();
Font f = new Font("Helvetica", 1, w/10);
String s = new String("The Starry Night");
TextLayout textTl = new TextLayout(s, f, frc);
AffineTransform transform = new AffineTransform();
Shape outline = textTl.getOutline(null);
Rectangle r = outline.getBounds();
transform = g2.getTransform();
transform.translate(w/2-(r.width/2), h/2+(r.height/2));
g2.transform(transform);
g2.setColor(Color.blue);
g2.draw(outline);
```

Далее на графическом контексте устанавливается область отсечения с помощью объекта `Shape`,
созданного методом `getOutline`. Изображение `starry.gif` — знаменитая картина Ван Гога
*Звёздная ночь* (*The Starry Night*) — рисуется в этой области отсечения, начиная с левого нижнего
угла объекта `Rectangle`.

```java
g2.setClip(outline);
g2.drawImage(img, r.x, r.y, r.width, r.height, this);
```

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этой программы содержится в файле `Starry.java`. Этому апплету требуется файл изображения
`Starry.gif`.

## Композиция графики (compositing)

Класс [`AlphaComposite`](https://docs.oracle.com/javase/8/docs/api/java/awt/AlphaComposite.html)
инкапсулирует различные стили композиции (compositing styles), которые определяют, как отрисовываются
перекрывающиеся объекты. У `AlphaComposite` также может быть значение альфа (alpha), задающее степень
прозрачности: alpha = 1.0 — полностью непрозрачно (opaque), alpha = 0.0 — полностью прозрачно
(transparent, clear). `AlphaComposite` поддерживает большинство стандартных правил композиции
Портера—Даффа (Porter-Duff), показанных в следующей таблице.

| Правило композиции | Описание |
|---|---|
| Источник поверх (`SRC_OVER`) | Если пиксели отрисовываемого объекта (источника, source) расположены там же, где ранее отрисованные пиксели (приёмника, destination), пиксели источника рисуются поверх пикселей приёмника. |
| Источник внутри (`SRC_IN`) | Если пиксели источника и приёмника перекрываются, отрисовываются только пиксели источника в области перекрытия. |
| Источник вне (`SRC_OUT`) | Если пиксели источника и приёмника перекрываются, отрисовываются только пиксели источника вне области перекрытия. Пиксели в области перекрытия очищаются (cleared). |
| Приёмник поверх (`DST_OVER`) | Если пиксели источника и приёмника перекрываются, отрисовываются только пиксели источника вне области перекрытия. Пиксели в области перекрытия не изменяются. |
| Приёмник внутри (`DST_IN`) | Если пиксели источника и приёмника перекрываются, альфа источника применяется к пикселям приёмника в области перекрытия. Если alpha = 1.0, пиксели в области перекрытия не изменяются; если alpha = 0.0, пиксели в области перекрытия очищаются. |
| Приёмник вне (`DST_OUT`) | Если пиксели источника и приёмника перекрываются, альфа источника применяется к пикселям приёмника в области перекрытия. Если alpha = 1.0, пиксели в области перекрытия очищаются; если alpha = 0.0, пиксели в области перекрытия не изменяются. |
| Очистка (`CLEAR`) | Если пиксели источника и приёмника перекрываются, пиксели в области перекрытия очищаются. |

Чтобы изменить стиль композиции, используемый классом
[`Graphics2D`](https://docs.oracle.com/javase/8/docs/api/java/awt/Graphics2D.html), создайте объект
`AlphaComposite` и передайте его в метод `setComposite`.

### Пример: Composite

Эта программа иллюстрирует эффекты различных сочетаний стиля композиции и значения альфа.

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этого апплета содержится в файле `Composite.java`.

Новый объект `AlphaComposite` *ac* создаётся вызовом `AlphaComposite.getInstance` с указанием
нужного правила композиции.

```java
AlphaComposite ac =
  AlphaComposite.getInstance(AlphaComposite.SRC);
```

Когда выбирается другое правило композиции или значение альфа, `AlphaComposite.getInstance`
вызывается снова, и новый `AlphaComposite` присваивается *ac*. Выбранное значение альфа применяется
в дополнение к попиксельному (per-pixel) значению альфа и передаётся вторым параметром в
`AlphaComposite.getInstance`.

```java
ac = AlphaComposite.getInstance(getRule(rule), alpha);
```

Атрибут композиции изменяется передачей объекта `AlphaComposite` в метод `setComposite` класса
`Graphics2D`. Объекты отрисовываются в `BufferedImage` и затем копируются на экран, поэтому атрибут
композиции устанавливается на контексте `Graphics2D` для `BufferedImage`:

```java
BufferedImage buffImg = new BufferedImage(w, h,
                        BufferedImage.TYPE_INT_ARGB);
Graphics2D gbi = buffImg.createGraphics();
...
gbi.setComposite(ac);
```

## Управление качеством отрисовки

Используйте атрибут подсказок отрисовки (rendering hints) класса `Graphics2D`, чтобы указать, хотите
ли вы отрисовывать объекты как можно быстрее или же предпочитаете максимально высокое качество
отрисовки.

Чтобы задать или изменить атрибут подсказок отрисовки в контексте `Graphics2D`, создайте объект
`RenderingHints` и передайте его в `Graphics2D` методом `setRenderingHints`. Если нужно задать
лишь одну подсказку, можно вызвать `setRenderingHint` класса `Graphics2D` и указать пару
«ключ—значение» (key-value pair) для задаваемой подсказки. (Пары «ключ—значение» определены в классе
`RenderingHints`.)

Например, чтобы задать предпочтение использовать сглаживание (antialiasing), если это возможно,
можно воспользоваться `setRenderingHint`:

```java
public void paint (graphics g){
    Graphics2D g2 = (Graphics2D)g;
    RenderingHints rh = new RenderingHints(
             RenderingHints.KEY_TEXT_ANTIALIASING,
             RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
    g2.setRenderingHints(rh);
...
}
```

> **Примечание.** Не все платформы поддерживают изменение режима отрисовки, поэтому указание
> подсказок отрисовки не гарантирует, что они будут использованы.

`RenderingHints` поддерживает следующие типы подсказок:

| Подсказка | Ключ | Значения |
|---|---|---|
| **Сглаживание (Antialiasing)** | `KEY_ANTIALIASING` | `VALUE_ANTIALIAS_ON`<br>`VALUE_ANTIALIAS_OFF`<br>`VALUE_ANTIALIAS_DEFAULT` |
| **Интерполяция альфа (Alpha Interpolation)** | `KEY_ALPHA_INTERPOLATION` | `VALUE_ALPHA_INTERPOLATION_QUALITY`<br>`VALUE_ALPHA_INTERPOLATION_SPEED`<br>`VALUE_ALPHA_INTERPOLATION_DEFAULT` |
| **Отрисовка цвета (Color Rendering)** | `KEY_COLOR_RENDERING` | `VALUE_COLOR_RENDER_QUALITY`<br>`VALUE_COLOR_RENDER_SPEED`<br>`VALUE_COLOR_RENDER_DEFAULT` |
| **Дизеринг (Dithering)** | `KEY_DITHERING` | `VALUE_DITHER_DISABLE`<br>`VALUE_DITHER_ENABLE`<br>`VALUE_DITHER_DEFAULT` |
| **Дробные метрики текста (Fractional Text Metrics)** | `KEY_FRACTIONALMETRICS` | `VALUE_FRACTIONALMETRICS_ON`<br>`VALUE_FRACTIONALMETRICS_OFF`<br>`VALUE_FRACTIONALMETRICS_DEFAULT` |
| **Интерполяция изображения (Image Interpolation)** | `KEY_INTERPOLATION` | `VALUE_INTERPOLATION_BICUBIC`<br>`VALUE_INTERPOLATION_BILINEAR`<br>`VALUE_INTERPOLATION_NEAREST_NEIGHBOR` |
| **Отрисовка (Rendering)** | `KEY_RENDERING` | `VALUE_RENDER_QUALITY`<br>`VALUE_RENDER_SPEED`<br>`VALUE_RENDER_DEFAULT` |
| **Управление нормализацией штриха (Stroke Normalization Control)** | `KEY_STROKE_CONTROL` | `VALUE_STROKE_NORMALIZE`<br>`VALUE_STROKE_DEFAULT`<br>`VALUE_STROKE_PURE` |
| **Сглаживание текста (Text Antialiasing)** | `KEY_TEXT_ANTIALIASING` | `VALUE_TEXT_ANTIALIAS_ON`<br>`VALUE_TEXT_ANTIALIAS_OFF`<br>`VALUE_TEXT_ANTIALIAS_DEFAULT`<br>`VALUE_TEXT_ANTIALIAS_GASP`<br>`VALUE_TEXT_ANTIALIAS_LCD_HRGB`<br>`VALUE_TEXT_ANTIALIAS_LCD_HBGR`<br>`VALUE_TEXT_ANTIALIAS_LCD_VRGB`<br>`VALUE_TEXT_ANTIALIAS_LCD_VBGR` |
| **Контраст LCD-текста (LCD Text Contrast)** | `KEY_TEXT_LCD_CONTRAST` | Значения должны быть положительным целым числом в диапазоне от 100 до 250. Меньшее значение (например, 100) соответствует более контрастному тексту при отображении тёмного текста на светлом фоне. Большее значение (например, 200) соответствует менее контрастному тексту при отображении тёмного текста на светлом фоне. Типичное полезное значение — в узком диапазоне 140–180. Если значение не задано, применяется системное или реализационное значение по умолчанию. |

Когда подсказка установлена в значение по умолчанию (default), используется платформенное значение
отрисовки по умолчанию.

## Построение сложных фигур из геометрических примитивов

Конструктивная геометрия областей (constructive area geometry, CAG) — это процесс создания новых
геометрических фигур путём выполнения булевых операций (boolean operations) над существующими.
В Java 2D API класс
[`Area`](https://docs.oracle.com/javase/8/docs/api/java/awt/geom/Area.html) реализует интерфейс
[`Shape`](https://docs.oracle.com/javase/8/docs/api/java/awt/Shape.html) и поддерживает следующие
булевы операции:

* объединение (union);
* вычитание (subtraction);
* пересечение (intersection);
* исключающее ИЛИ (exclusive-or, `XOR`).

### Пример: Areas

В этом примере объекты `Area` строят фигуру груши из нескольких эллипсов.

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этого апплета содержится в файле `Pear.java`.

Каждый из листьев создаётся выполнением пересечения (intersection) двух перекрывающихся окружностей.

```java
leaf = new Ellipse2D.Double();
...
leaf1 = new Area(leaf);
leaf2 = new Area(leaf);
...
leaf.setFrame(ew-16, eh-29, 15.0, 15.0);
leaf1 = new Area(leaf);
leaf.setFrame(ew-14, eh-47, 30.0, 30.0);
leaf2 = new Area(leaf);
leaf1.intersect(leaf2);
g2.fill(leaf1);
...
leaf.setFrame(ew+1, eh-29, 15.0, 15.0);
leaf1 = new Area(leaf);
leaf2.intersect(leaf1);
g2.fill(leaf2);
```

Перекрывающиеся окружности также используются для построения стебля посредством операции вычитания
(subtraction).

```java
stem = new Ellipse2D.Double();
...
stem.setFrame(ew, eh-42, 40.0, 40.0);
st1 = new Area(stem);
stem.setFrame(ew+3, eh-47, 50.0, 50.0);
st2 = new Area(stem);
st1.subtract(st2);
g2.fill(st1);
```

Тело груши строится выполнением операции объединения (union) над окружностью и овалом.

```java
circle = new Ellipse2D.Double();
oval = new Ellipse2D.Double();
circ = new Area(circle);
ov = new Area(oval);
...
circle.setFrame(ew-25, eh, 50.0, 50.0);
oval.setFrame(ew-19, eh-20, 40.0, 70.0);
circ = new Area(circle);
ov = new Area(oval);
circ.add(ov);
g2.fill(circ);
```

## Поддержка взаимодействия с пользователем

Чтобы пользователь мог взаимодействовать с отображаемой графикой, нужно уметь определять, когда
пользователь щёлкает по одному из объектов. Метод `hit` класса
[`Graphics2D`](https://docs.oracle.com/javase/8/docs/api/java/awt/Graphics2D.html) даёт простой
способ узнать, произошёл ли щелчок мышью над конкретным объектом
[`Shape`](https://docs.oracle.com/javase/8/docs/api/java/awt/Shape.html). В качестве альтернативы
можно получить местоположение щелчка мышью и вызвать `contains` у `Shape`, чтобы определить, попал
ли щелчок в пределы границ (bounds) `Shape`.

Если вы используете примитивный текст (primitive text), можно выполнять простое определение попадания
(hit testing), получив контур (outline) `Shape`, соответствующий тексту, а затем вызвав `hit` или
`contains` с этим `Shape`. Поддержка редактирования текста требует гораздо более сложного определения
попадания. Если вы хотите позволить пользователю редактировать текст, в общем случае следует
использовать один из редактируемых текстовых компонентов Swing. Если вы работаете с примитивным
текстом и используете класс
[`TextLayout`](https://docs.oracle.com/javase/8/docs/api/java/awt/font/TextLayout.html) для управления
формированием (shaping) и позиционированием текста, вы также можете использовать `TextLayout` для
определения попадания при редактировании текста. Подробнее см. главу *Text and Fonts* в
[Java 2D Programmer's Guide](https://docs.oracle.com/javase/8/docs/technotes/guides/2d/spec/j2d-bookTOC.html)
или приведённый ниже пример HitTestSample, в котором `TextLayout` используется для простого
определения попадания.

### Пример: ShapeMover

Этот апплет позволяет пользователю перетаскивать `Shape` в пределах окна апплета. `Shape`
перерисовывается при каждом положении мыши, обеспечивая обратную связь по мере перетаскивания.

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этого апплета содержится в файле `ShapeMover.java`.

Метод `contains` вызывается, чтобы определить, находится ли курсор в пределах границ прямоугольника
при нажатии кнопки мыши. Если это так, местоположение прямоугольника обновляется.

```java
public void mousePressed(MouseEvent e){
    last_x = rect.x - e.getX();
    last_y = rect.y - e.getY();
    if(rect.contains(e.getX(),
        e.getY())) updateLocation(e);
    ...

public void updateLocation(MouseEvent e){
    rect.setLocation(last_x + e.getX(),
        last_y + e.getY());
    ...
    repaint();
```

Вы можете заметить, что перерисовка `Shape` при каждом положении мыши работает медленно, потому что
залитый прямоугольник перерисовывается каждый раз при перемещении. Использование двойной буферизации
(double buffering) устраняет эту проблему. Если вы используете Swing, рисование будет буферизоваться
дважды автоматически; менять код отрисовки вообще не придётся. Код Swing-версии этой программы —
`SwingShapeMover.java`.

### Пример: HitTestSample

Это приложение иллюстрирует определение попадания, рисуя каретку (caret) по умолчанию там, где
пользователь щёлкает по `TextLayout`, как показано на следующем рисунке.

> **Примечание.** Если апплет не запускается, нужно установить как минимум выпуск
> Java SE Development Kit (JDK) 7.

Полный код этого апплета содержится в файле `HitTestSample.java`.

Метод `mouseClicked` использует `TextLayout.hitTestChar`, чтобы вернуть объект
`java.awt.font.TextHitInfo`, содержащий местоположение щелчка мышью (индекс вставки, insertion index)
в объекте `TextLayout`.

Информация, возвращаемая методами `getAscent`, `getDescent` и `getAdvance` класса `TextLayout`,
используется для вычисления местоположения начала координат (origin) объекта `TextLayout` так, чтобы
он был центрирован по горизонтали и вертикали.

```java
...

private Point2D computeLayoutOrigin() {
  Dimension size = getPreferredSize();
  Point2D.Float origin = new Point2D.Float();
     
  origin.x = (float) (size.width -
             textLayout.getAdvance()) / 2;   
  origin.y = 
    (float) (size.height -
             textLayout.getDescent() +
             textLayout.getAscent())/2;
  return origin;
}

...

public void paintComponent(Graphics g) {
  super.paintComponent(g);
  setBackground(Color.white);
  Graphics2D graphics2D = (Graphics2D) g;                
  Point2D origin = computeLayoutOrigin();
  graphics2D.translate(origin.getX(),
                       origin.getY());
                
  // Рисуем textLayout.
  textLayout.draw(graphics2D, 0, 0);
     
  // Получаем фигуры кареток (caret Shapes) для insertionIndex.
  Shape[] carets =
      textLayout.getCaretShapes(insertionIndex);
       
  // Рисуем каретки. carets[0] — сильная (strong)
  // каретка, carets[1] — слабая (weak) каретка.
  graphics2D.setColor(STRONG_CARET_COLOR);
  graphics2D.draw(carets[0]);                
  if (carets[1] != null) {
    graphics2D.setColor(WEAK_CARET_COLOR);
    graphics2D.draw(carets[1]);
  }       
}

...

private class HitTestMouseListener
              extends MouseAdapter {
                
    /**
     * Вычисляет позицию символа по щелчку
     * мышью.
     */     
    public void mouseClicked(MouseEvent e) {
                
      Point2D origin = computeLayoutOrigin();
                
      // Вычисляем местоположение щелчка мышью
      // относительно начала координат textLayout.
      float clickX =
          (float) (e.getX() - origin.getX());
      float clickY =
          (float) (e.getY() - origin.getY());
         
      // Получаем позицию символа по щелчку
      // мышью.
      TextHitInfo currentHit =
          textLayout.hitTestChar(clickX, clickY);
      insertionIndex =
          currentHit.getInsertionIndex();
            
      // Перерисовываем компонент, чтобы новые
      // каретки отобразились.
      hitPane.repaint();
    }
```

## Источник

- [Advanced Topics in Java2D](https://docs.oracle.com/javase/tutorial/2d/advanced/index.html) — официальное руководство Oracle.
- [Transforming Shapes, Text, and Images](https://docs.oracle.com/javase/tutorial/2d/advanced/transforming.html)
- [Clipping the Drawing Region](https://docs.oracle.com/javase/tutorial/2d/advanced/clipping.html)
- [Compositing Graphics](https://docs.oracle.com/javase/tutorial/2d/advanced/compositing.html)
- [Controlling Rendering Quality](https://docs.oracle.com/javase/tutorial/2d/advanced/quality.html)
- [Constructing Complex Shapes from Geometry Primitives](https://docs.oracle.com/javase/tutorial/2d/advanced/complexshapes.html)
- [Supporting User Interaction](https://docs.oracle.com/javase/tutorial/2d/advanced/user.html)
</content>
</invoke>
