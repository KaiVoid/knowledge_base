# OOP — Basic (HH)

### Вопрос 1. Что такое метод в объектно-ориентированном программировании?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Функция или процедура внутри класса или объекта

#### Ответ от Claude

Метод — это функция (или процедура), определённая внутри класса и описывающая поведение объекта. Методы имеют доступ к полям (состоянию) объекта и могут изменять его. В Java методы объявляются внутри тела класса и могут быть как методами экземпляра (вызываются на объекте), так и статическими (принадлежат классу). Методы формируют публичный интерфейс объекта, через который с ним взаимодействует внешний код.

Источники: [Oracle Java Tutorial — Defining Methods](https://docs.oracle.com/javase/tutorial/java/javaOO/methods.html); [Oracle Java Tutorial — What Is an Object?](https://docs.oracle.com/javase/tutorial/java/concepts/object.html).

---

### Вопрос 2. Выберите вариант, в котором верно перечислены основные принципы объектно-ориентированного программирования.

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Абстракция, инкапсуляция, наследование, полиморфизм

#### Ответ от Claude

Четыре кита ООП: **абстракция** (выделение существенных характеристик объекта, скрытие деталей реализации), **инкапсуляция** (сокрытие внутреннего состояния и управление доступом через интерфейс), **наследование** (создание нового класса на основе существующего с повторным использованием кода) и **полиморфизм** (способность объектов разных типов реагировать на одни и те же сообщения по-разному). Все четыре принципа вместе обеспечивают модульность, гибкость и повторное использование кода в ООП.

Источники: [Oracle Java Tutorial — Object-Oriented Programming Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/index.html).

---

### Вопрос 3. Какое из утверждений НЕ относится к принципам объектно-ориентированного программирования?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Состояние объекта не может быть изменено после того, как объект был создан

#### Ответ от Claude

Утверждение «состояние объекта не может быть изменено после создания» описывает концепцию **иммутабельности** (неизменяемости) — это архитектурное решение или паттерн (например, класс `String` в Java является иммутабельным), но не один из четырёх фундаментальных принципов ООП. Объекты в ООП по умолчанию **изменяемы**: их поля могут меняться в течение жизненного цикла. Основные принципы ООП — абстракция, инкапсуляция, наследование и полиморфизм — не требуют иммутабельности.

Источники: [Oracle Java Tutorial — Object-Oriented Programming Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/index.html); Joshua Bloch, «Effective Java», 3rd ed., Item 17 — Minimize mutability.

---

### Вопрос 4. Имеется класс Еда, подкласс Фрукт и объект Яблоко класса Фрукт. Какую иерархию иллюстрирует этот пример?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Родительский класс > Дочерний класс > Экземпляр класса

#### Ответ от Claude

Пример иллюстрирует трёхуровневую иерархию: **Еда** — родительский (базовый) класс; **Фрукт** — дочерний класс (подкласс `Еды`), наследующий её свойства и расширяющий их; **Яблоко** — конкретный объект (экземпляр) класса `Фрукт`. Иерархия «Родительский класс → Дочерний класс → Экземпляр» отражает принципы наследования (класс Фрукт наследует Еду) и инстанциирования (создание объекта Яблоко из класса Фрукт).

Источники: [Oracle Java Tutorial — Inheritance](https://docs.oracle.com/javase/tutorial/java/IandI/subclasses.html); [Oracle Java Tutorial — Creating Objects](https://docs.oracle.com/javase/tutorial/java/javaOO/objectcreation.html).

---

### Вопрос 5. Вы создаёте класс Собака и задаёте ему приватный (private) метод Лаять и приватный атрибут — Голод. Это пример реализации какого принципа ООП?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Инкапсуляция

#### Ответ от Claude

Объявление метода и атрибута с модификатором `private` — классический пример **инкапсуляции**: внутренние детали реализации класса (как именно собака лает и как отслеживается её голод) скрыты от внешнего кода. Внешний код не может напрямую вызвать `Лаять()` или изменить `Голод` — доступ возможен только через публичный интерфейс класса (если он предоставлен). Инкапсуляция защищает целостность состояния объекта и позволяет изменять внутреннюю реализацию без влияния на внешний код.

Источники: [Oracle Java Tutorial — Controlling Access to Members of a Class](https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html); [Oracle Java Tutorial — What Is Encapsulation?](https://docs.oracle.com/javase/tutorial/java/concepts/).

---

### Вопрос 6. Какая конструкция в ООП используется для обработки исключений?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** try-except

#### Ответ от Claude

Конструкция `try-except` используется для обработки исключений в Python (и ряде других языков). В Java аналогичная конструкция называется `try-catch` (и `try-catch-finally` с необязательным блоком `finally`). Вопрос сформулирован в контексте общего ООП, и `try-except` является правильным ответом для языков Python, Ruby. Принцип одинаков: код в блоке `try` выполняется, при возникновении исключения управление передаётся в блок `catch`/`except`.

Источники: [Oracle Java Tutorial — Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/index.html); [Python docs — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html).

---

### Вопрос 7. Какой из языков программирования НЕ относится к объектно-ориентированным?

**Категория:** OOP (HH) · **Уровень:** Basic

```
Python
Java
C++
PHP
Все перечисленные языки можно отнести к объектно-ориентированным
```

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Все перечисленные языки можно отнести к объектно-ориентированным

#### Ответ от Claude

Все четыре языка поддерживают объектно-ориентированную парадигму: **Java** — чисто объектно-ориентированный язык (всё является объектом, кроме примитивов); **Python** — мультипарадигменный язык с полноценной поддержкой ООП; **C++** — расширение C с поддержкой классов, наследования и полиморфизма; **PHP** — с версии 5+ имеет полноценную объектно-ориентированную модель. Следует отметить, что C++ и Python — мультипарадигменные языки (поддерживают также процедурное и функциональное программирование), но все они **поддерживают ООП**.

Источники: [Oracle Java Tutorial — OOP Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/index.html); [Python docs — Classes](https://docs.python.org/3/tutorial/classes.html).

---

### Вопрос 8. Вы определяете класс Транспорт. Для класса Транспорт вы задаёте атрибуты — Мощность и Габариты. Для атрибута Мощность вы настраиваете модификатор доступа — protected. Затем вы определяете подкласс Автомобиль класса Транспорт, и создаёте объект Ауди класса Автомобиль. Какое из утверждений верно?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** К атрибуту Мощность можно обратиться только из классов Транспорт и Автомобиль, но не из объекта Ауди

#### Ответ от Claude

Модификатор `protected` в Java разрешает доступ из самого класса (`Транспорт`), из подклассов (`Автомобиль`) и из классов того же пакета. Однако объект `Ауди` — это экземпляр класса `Автомобиль`, и к его `protected`-полю можно обратиться **изнутри класса `Автомобиль`**, но **не через экземпляр из произвольного внешнего кода**. То есть код вне иерархии классов не может написать `ауди.мощность` — в этом смысл формулировки «но не из объекта». Доступ к `protected` члену через внешнюю переменную-ссылку закрыт.

Источники: [Oracle Java Tutorial — Controlling Access to Members](https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html); [JLS §6.6.1 Determining Accessibility](https://docs.oracle.com/javase/specs/jls/se21/html/jls-6.html#jls-6.6.1).

---

### Вопрос 9. Когда вызывается конструктор класса?

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** При создании экземпляра класса

#### Ответ от Claude

Конструктор вызывается автоматически в момент создания нового объекта (экземпляра) класса оператором `new` (в Java). Конструктор отвечает за инициализацию объекта: присваивание начальных значений полям, выполнение необходимой настройки. Конструктор не вызывается при обращении к статическим полям/методам, при сериализации/десериализации (если используются специальные механизмы), или при клонировании через `clone()`. Конструктор имеет то же имя, что и класс, и не имеет возвращаемого типа.

Источники: [Oracle Java Tutorial — Providing Constructors for Your Classes](https://docs.oracle.com/javase/tutorial/java/javaOO/constructors.html); [JLS §8.8 Constructor Declarations](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.8).

---

### Вопрос 10. Вы создаёте класс, внутри которого объявлена переменная, содержащая общее количество созданных объектов этого класса. Это пример…

**Категория:** OOP (HH) · **Уровень:** Basic

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/basic.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/basic.md)

**Правильный ответ:** Статического поля

#### Ответ от Claude

**Статическое поле** (поле класса) принадлежит классу, а не отдельному экземпляру, и является общим для всех экземпляров класса. Переменная-счётчик объектов — классический пример: она инкрементируется в конструкторе при каждом создании экземпляра и хранит одно значение для всего класса:

```java
public class MyClass {
    private static int instanceCount = 0;

    public MyClass() {
        instanceCount++;
    }

    public static int getInstanceCount() {
        return instanceCount;
    }
}
```

Статические поля объявляются с модификатором `static` и существуют в единственном экземпляре в памяти JVM.

Источники: [Oracle Java Tutorial — Understanding Instance and Class Members](https://docs.oracle.com/javase/tutorial/java/javaOO/classvars.html); [JLS §8.3.1.1 static Fields](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.3.1.1).

---
