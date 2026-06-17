# Урок 6. Создание интерфейса с помощью FXML

**Трейл:** Creating a JavaFX GUI · **Оригинал:** [Using FXML to Create a User Interface](https://docs.oracle.com/javase/8/javafx/get-started-tutorial/fxml_tutorial.htm)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (JavaFX 8).
>
> Этот урок показывает преимущества FXML — языка на основе XML (*XML-based language*),
> который отделяет структуру пользовательского интерфейса от логики приложения. Здесь заново
> строится приложение входа (*login application*), ранее созданное на «чистом» JavaFX, но теперь
> с использованием FXML — ради более чистого и удобного в сопровождении кода. В уроке
> используется среда разработки NetBeans IDE и платформа JavaFX 8. Готовый интерфейс входа
> показан на рисунке ниже.

## Настройка проекта (Set Up the Project)

> Создайте новый проект типа JavaFX FXML Application в NetBeans:
>
> 1. В меню **File** выберите **New Project**, затем категорию **JavaFX application**,
>    пункт **JavaFX FXML Application** и нажмите **Next**.
> 2. Назовите проект `FXMLExample` и нажмите **Finish**.
> 3. NetBeans создаёт заготовку проекта из трёх файлов:
>    - `FXMLExample.java` — стандартный Java-код для настройки FXML-приложения;
>    - `FXMLDocument.fxml` — XML-файл, описывающий интерфейс;
>    - `FXMLDocumentController.java` — контроллер (*controller*) для обработки ввода.
> 4. Переименуйте `FXMLDocumentController.java` в `FXMLExampleController.java`
>    (правый клик → **Refactor** → **Rename**).
> 5. Переименуйте `FXMLDocument.fxml` в `fxml_example.fxml` (правый клик → **Rename**).

## Загрузка исходного FXML-файла (Load the FXML Source File)

> Файл `FXMLExample.java` настраивает окно (*Stage*) и сцену (*Scene*). Ключевой элемент здесь —
> класс `FXMLLoader`, который загружает FXML-файл и возвращает построенный по нему граф объектов
> (*object graph*).

```java
@Override
public void start(Stage stage) throws Exception {
   Parent root = FXMLLoader.load(getClass().getResource("fxml_example.fxml"));

    Scene scene = new Scene(root, 300, 275);

    stage.setTitle("FXML Welcome");
    stage.setScene(scene);
    stage.show();
}
```

> **Рекомендация.** Всегда задавайте явные ширину и высоту сцены (здесь — 300 × 275), а не
> полагайтесь на значения по умолчанию.

## Изменение операторов импорта (Modify the Import Statements)

> Отредактируйте `fxml_example.fxml`, добавив объявления импорта (*import declarations*) для
> классов JavaFX — аналогично импортам в Java.

```xml
<?xml version="1.0" encoding="UTF-8"?>

<?import java.net.*?>
<?import javafx.geometry.*?>
<?import javafx.scene.control.*?>
<?import javafx.scene.layout.*?>
<?import javafx.scene.text.*?>
```

> Классы можно указывать полностью квалифицированным именем (вместе с именем пакета) либо
> импортировать через объявления `<?import?>`. Поддерживается и точечный (не «по шаблону»,
> *non-wildcard*) импорт отдельных классов.

## Создание разметки на GridPane (Create a GridPane Layout)

> Замените стандартный контейнер `AnchorPane` на компоновку `GridPane`, чтобы получить гибкие
> строки и столбцы для размещения элементов управления.

```xml
<GridPane fx:controller="fxmlexample.FXMLExampleController" 
    xmlns:fx="http://javafx.com/fxml" alignment="center" hgap="10" vgap="10">
<padding><Insets top="25" right="25" bottom="10" left="25"/></padding>

</GridPane>
```

> Пояснение к атрибутам:
>
> - `fx:controller` — задаёт класс контроллера для обработчиков событий (обязателен, когда
>   используются методы контроллера);
> - `xmlns:fx` — объявляет пространство имён (*namespace*) `fx` (требуется всегда);
> - `alignment="center"` — центрирует сетку в сцене (вместо размещения по умолчанию в
>   левом верхнем углу);
> - `hgap="10" vgap="10"` — горизонтальный и вертикальный промежутки между столбцами и строками;
> - `padding` — отступы вокруг краёв сетки (изменяются при изменении размера окна).
>
> При изменении размера окна узлы внутри `GridPane` масштабируются согласно ограничениям
> компоновки (*layout constraints*), а сама сетка остаётся по центру.

## Добавление текстового поля и поля пароля (Add Text and Password Fields)

> Добавьте элементы управления формы входа: заголовок «Welcome», а также поля для имени
> пользователя и пароля. Вставьте этот код перед закрывающим тегом `</GridPane>`.

```xml
<Text text="Welcome" 
        GridPane.columnIndex="0" GridPane.rowIndex="0"
        GridPane.columnSpan="2"/>
 
    <Label text="User Name:"
        GridPane.columnIndex="0" GridPane.rowIndex="1"/>
 
    <TextField 
        GridPane.columnIndex="1" GridPane.rowIndex="1"/>
 
    <Label text="Password:"
        GridPane.columnIndex="0" GridPane.rowIndex="2"/>
 
    <PasswordField fx:id="passwordField" 
        GridPane.columnIndex="1" GridPane.rowIndex="2"/>
```

> Подробности:
>
> - элемент `Text` с текстом «Welcome» в позиции сетки (0, 0); атрибут `columnSpan="2"`
>   растягивает его на два столбца (это понадобится позже для оформления через CSS шрифтом 32pt);
> - метка `Label` «User Name:» в позиции (0, 1);
> - поле `TextField` в позиции (1, 1) — для ввода;
> - метка `Label` «Password:» в позиции (0, 2);
> - поле `PasswordField` в позиции (1, 2); атрибут `fx:id="passwordField"` создаёт ссылку на
>   переменную для использования в контроллере.

> **Совет по отладке.** Чтобы увидеть структуру сетки, добавьте `<gridLinesVisible>true</gridLinesVisible>`
> после элемента `<padding>` — линии сетки станут видимыми.

## Добавление кнопки и текста (Add a Button and Text)

> Добавьте кнопку «Sign In» и элемент `Text` для вывода ответного сообщения при нажатии кнопки.
> Вставьте код перед `</GridPane>`.

```xml
<HBox spacing="10" alignment="bottom_right" 
        GridPane.columnIndex="1" GridPane.rowIndex="4">
        <Button text="Sign In"     
        onAction="#handleSubmitButtonAction"/>
</HBox>

<Text fx:id="actiontarget"
       GridPane.columnIndex="0" GridPane.columnSpan="2"
       GridPane.halignment="RIGHT" GridPane.rowIndex="6"/>
```

> Подробности:
>
> - контейнер `HBox` с `alignment="bottom_right"` размещает кнопку иначе, чем выравнивание
>   `GridPane` по умолчанию; помещён в позицию сетки (1, 4);
> - кнопка `Button` с `text="Sign In"` и `onAction="#handleSubmitButtonAction"` — свойство
>   `onAction` вызывает метод контроллера;
> - элемент `Text` с `fx:id="actiontarget"` (создаёт ссылку на переменную) растянут на два
>   столбца в позиции (0, 6) с выравниванием по правому краю; выводит ответное сообщение.
>
> **Замечание.** FXML описывает структуру интерфейса, но не поведение; реализация обработчика
> события (*event handler*) выполняется в Java-коде.

## Добавление кода обработки события (Add Code to Handle an Event)

> Реализуйте поведение при нажатии кнопки в классе контроллера. Удалите сгенерированный NetBeans
> код и замените его следующим.

```java
package fxmlexample;
 
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.text.Text;
 
public class FXMLExampleController {
    @FXML private Text actiontarget;
    
    @FXML protected void handleSubmitButtonAction(ActionEvent event) {
        actiontarget.setText("Sign in button pressed");
    }

}
```

> Пояснение:
>
> - аннотация `@FXML` помечает поля и методы контроллера как доступные для FXML;
> - поле `actiontarget` ссылается на элемент `Text` с `fx:id="actiontarget"` из FXML-файла;
> - метод `handleSubmitButtonAction(ActionEvent event)` выполняется при нажатии кнопки и
>   устанавливает текст сообщения.
>
> При запуске приложения ввод текста в поля и нажатие «Sign In» выводят сообщение.

## Использование скриптового языка для обработки событий (Use a Scripting Language to Handle Events)

> Альтернативный подход: вместо Java-кода контроллера можно использовать для обработчиков событий
> скриптовый язык (*scripting language*), совместимый с JSR 223 (JavaScript, Groovy, Jython,
> Clojure).
>
> Шаги для использования JavaScript:
>
> 1. Добавьте объявление языка в `fxml_example.fxml` после XML-объявления (*doctype*):

```xml
<?language javascript?>
```

> 2. В разметке кнопки измените вызов в `onAction`:

```xml
onAction="handleSubmitButtonAction(event);"
```

> 3. Удалите атрибут `fx:controller` из тега `GridPane` и добавьте сразу под ним элемент
>    `<fx:script>` с JavaScript-функцией:

```xml
<GridPane xmlns:fx="http://javafx.com/fxml" 
              alignment="center" hgap="10" vgap="10">
         <fx:script>
             function handleSubmitButtonAction() {
                 actiontarget.setText("Calling the JavaScript");
             }
         </fx:script>
```

> Альтернатива: вынести JavaScript-функции в отдельный файл (например, `fxml_example.js`) и
> подключить его:

```xml
<fx:script source="fxml_example.js"/>
```

> **Оговорка.** Отладчик IDE может не поддерживать пошаговое выполнение кода скрипта.

## Оформление приложения с помощью CSS (Style the Application with CSS)

> Примените каскадные таблицы стилей (*Cascading Style Sheets, CSS*), чтобы сделать форму входа
> привлекательной.
>
> Шаги:
>
> 1. **Создайте таблицу стилей:**
>    - в окне Projects щёлкните правой кнопкой папку `fxmlexample` под Source Packages →
>      **New** → **Other**;
>    - выберите **Cascading Style Sheet** → **Next**;
>    - введите имя файла `Login` → **Finish**;
>    - скопируйте содержимое из готового файла `Login.css` (в загружаемом архиве `LoginCSS.zip`).
>
> 2. **Добавьте фоновое изображение:**
>    - скачайте `background.jpg` и сохраните в папку `fxmlexample`.
>
> 3. **Сошлитесь на таблицу стилей в FXML-файле** — добавьте элемент `<stylesheets>` перед
>    закрывающим `</GridPane>`:

```xml
<stylesheets>
    <URL value="@Login.css" />
</stylesheets>

</GridPane>
```

> Символ `@` означает, что CSS-файл находится в том же каталоге, что и FXML-файл.
>
> 4. **Примените корневой стиль к `GridPane`:**

```xml
<GridPane fx:controller="fxmlexample.FXMLExampleController" 
    xmlns:fx="http://javafx.com/fxml" alignment="center" hgap="10" vgap="10" 
    styleClass="root">
```

> Добавьте `styleClass="root"`, чтобы использовать корневой класс стиля из CSS.
>
> 5. **Создайте идентификатор для элемента `Text` «Welcome»:**

```xml
<Text id="welcome-text" text="Welcome" 
        GridPane.columnIndex="0" GridPane.rowIndex="0" 
        GridPane.columnSpan="2"/>
```

> Атрибут `id="welcome-text"` позволяет оформить элемент в CSS-файле через селектор
> `#welcome-text`.
>
> 6. **Запустите приложение**, чтобы увидеть оформленный результат. Полный рабочий код доступен в
>    загружаемом архиве `FXMLExample.zip`.

## Куда двигаться дальше (Where to Go from Here)

> Рекомендации для дальнейшего изучения:
>
> - прочитайте документ «Introduction to FXML» в пакете `javafx.fxml` документации API — там
>   подробнее разобраны возможности языка;
> - попробуйте инструмент JavaFX Scene Builder для визуального проектирования интерфейса: откройте
>   `fxml_example.fxml` в Scene Builder и внесите изменения (учтите, что при сохранении файл может
>   быть переформатирован);
> - обратитесь к руководству «Getting Started with JavaFX Scene Builder» за подробностями;
> - изучите разделы «Skinning with CSS» и «CSS Analyzer» в руководстве пользователя JavaFX Scene
>   Builder, посвящённые приёмам оформления через CSS.

## Источник

- [Using FXML to Create a User Interface](https://docs.oracle.com/javase/8/javafx/get-started-tutorial/fxml_tutorial.htm) — официальное руководство Oracle (JavaFX 8, Getting Started with JavaFX).
