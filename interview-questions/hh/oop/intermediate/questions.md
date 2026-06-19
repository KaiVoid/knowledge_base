# OOP — Intermediate (HH)

### Вопрос 1. Какое из утверждений верно?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Класс — это шаблон, определяющий состояние и поведение объектов, объект — это экземпляр класса

#### Ответ от Claude

Это фундаментальное определение ООП: **класс** является шаблоном (blueprint), описывающим структуру (поля/атрибуты — состояние) и поведение (методы) будущих объектов. **Объект** — конкретный экземпляр класса, созданный с помощью оператора `new` (в Java) или аналогичного механизма в других языках. Объект занимает память и содержит конкретные значения полей, определённых в классе.

Источники: [Oracle Java Tutorial — What Is an Object?](https://docs.oracle.com/javase/tutorial/java/concepts/object.html); [Oracle Java Tutorial — What Is a Class?](https://docs.oracle.com/javase/tutorial/java/concepts/class.html).

---

### Вопрос 2. Что из перечисленного — пример классического антипаттерна в ООП?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Использование класса с чрезмерно большим количеством методов, имеющих разное предназначение

#### Ответ от Claude

Описанный антипаттерн называется «Божественный объект» (God Object или God Class) — класс, который знает слишком много или делает слишком много. Такой класс нарушает принцип единственной ответственности (SRP из SOLID) и принцип слабой связанности: он концентрирует несвязанную логику, становясь точкой изменений для множества несвязанных требований. Рефакторинг: декомпозиция на специализированные классы с одной ответственностью каждый.

Источники: [Refactoring Guru — God Object (антипаттерн)](https://refactoring.guru/ru/antipatterns/god-object); Robert C. Martin, «Clean Architecture», глава 7 — SRP.

---

### Вопрос 3. Какое из утверждений верно?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Абстракция может достигаться путём использования интерфейсов, а инкапсуляция — за счёт модификаторов доступа

#### Ответ от Claude

**Абстракция** — сокрытие деталей реализации и предоставление только существенного интерфейса. В Java она реализуется через абстрактные классы и интерфейсы: клиентский код работает с контрактом (интерфейсом), не зная о конкретной реализации. **Инкапсуляция** — сокрытие внутреннего состояния объекта и управление доступом к нему. Реализуется через модификаторы доступа (`private`, `protected`, `public`) и методы-аксессоры (getter/setter). Эти два принципа дополняют друг друга, но решают разные задачи.

Источники: [Oracle Java Tutorial — Interfaces](https://docs.oracle.com/javase/tutorial/java/concepts/interface.html); [Oracle Java Tutorial — Controlling Access to Members of a Class](https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html).

---

### Вопрос 4. Что из перечисленного — пример реализации статического полиморфизма?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Когда в классе есть несколько методов, имеющих одинаковое имя, но разное число параметров одного типа

#### Ответ от Claude

**Статический полиморфизм** (полиморфизм времени компиляции) реализуется через **перегрузку методов** (method overloading): несколько методов с одним именем, но разными сигнатурами (количество, типы или порядок параметров). Компилятор разрешает вызов на этапе компиляции, выбирая подходящую перегрузку. Это отличается от динамического полиморфизма (переопределение методов, runtime dispatch). В Java перегрузка конструкторов — частный случай того же механизма.

Источники: [Oracle Java Tutorial — Defining Methods (overloading)](https://docs.oracle.com/javase/tutorial/java/javaOO/methods.html); [JLS §8.4.9 Overloading](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.4.9).

---

### Вопрос 5. В каком из перечисленных случаев соблюдён принцип единственной ответственности?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Класс OrderStatusControl содержит методы для управления статусом

#### Ответ от Claude

Принцип единственной ответственности (Single Responsibility Principle, SRP) из SOLID гласит: у класса должна быть только одна причина для изменения. Класс `OrderStatusControl`, содержащий только методы управления статусом заказа, имеет одну чётко определённую ответственность. Если бы он также содержал логику расчёта стоимости, отправки уведомлений или работы с базой данных — это нарушало бы SRP, поскольку появлялось бы несколько независимых причин для изменения класса.

Источники: [Refactoring Guru — Single Responsibility Principle](https://refactoring.guru/ru/solid/single-responsibility-principle); Robert C. Martin, «Clean Architecture», глава 7 — The Single Responsibility Principle.

---

### Вопрос 6. В каком случае НЕ выполняется блок finally при обработке исключений?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Если программа была принудительно завершена

#### Ответ от Claude

В Java блок `finally` выполняется практически всегда — даже при возникновении исключения или при использовании `return` внутри `try`/`catch`. Исключения (когда `finally` не выполняется):

1. **Принудительное завершение JVM**: вызов `System.exit()`, `Runtime.halt()` или аварийное завершение процесса (SIGKILL в Linux).
2. **Бесконечный цикл или deadlock** в блоке `try`/`catch` — `finally` не будет достигнут.
3. **Сбой питания / крах операционной системы**.

Обычный `return`, `break`, `continue` и даже необработанное исключение не препятствуют выполнению `finally`.

Источники: [Oracle Java Tutorial — The finally Block](https://docs.oracle.com/javase/tutorial/essential/exceptions/finally.html); [JLS §14.20.2 Execution of try-finally and try-catch-finally](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.20.2).

---

### Вопрос 7. Вы хотите обеспечить доступность полей и методов класса из самого класса, из производного класса, но не из любого места программы. Какой из модификаторов доступа вы будете использовать?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Только protected

#### Ответ от Claude

В Java модификатор `protected` обеспечивает доступ: из самого класса, из классов того же пакета и из подклассов (даже из других пакетов). Это ближайшее соответствие требованию «из самого класса и производного класса, но не из любого места». Следует учитывать, что `protected` в Java также открывает доступ классам того же пакета, что несколько шире требования. Для строгого ограничения «только класс и подклассы» в Java нет отдельного модификатора — `protected` является наиболее подходящим вариантом.

Источники: [Oracle Java Tutorial — Controlling Access to Members](https://docs.oracle.com/javase/tutorial/java/javaOO/accesscontrol.html); [JLS §6.6 Access Control](https://docs.oracle.com/javase/specs/jls/se21/html/jls-6.html#jls-6.6).

---

### Вопрос 8. Вы разрабатываете систему для управления грузоперевозками. У вас есть базовый класс Transport, от которого наследуются классы Truck и Ship. В классе Transport есть метод calculateCost(), который рассчитывает стоимость доставки. При использовании этого метода в классе Ship возникает ошибка, и программа перестаёт работать. Какой принцип ООП мог быть нарушен при разработке этой системы?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Принцип подстановки Барбары Лисков

#### Ответ от Claude

Принцип подстановки Лисков (Liskov Substitution Principle, LSP) из SOLID гласит: объекты подкласса должны быть способны заменить объекты базового класса без нарушения корректности программы. В примере класс `Ship` наследует `Transport`, но метод `calculateCost()` при использовании в `Ship` вызывает ошибку и крах программы. Это нарушение LSP: подкласс не может полноценно заменить базовый класс. Решение — либо изменить иерархию наследования, либо переопределить `calculateCost()` в `Ship` с корректной реализацией для морского транспорта.

Источники: [Refactoring Guru — Liskov Substitution Principle](https://refactoring.guru/ru/solid/liskov-substitution-principle); Barbara Liskov, «Data Abstraction and Hierarchy», SIGPLAN Notices, 1988.

---

### Вопрос 9. В какой из ситуаций корректно применить абстрактные классы, а не интерфейсы?

**Категория:** OOP (HH) · **Уровень:** Intermediate

**Варианты ответа:**
- Когда необходимо уменьшить связанность кода
- Когда нужно создать разноплановые по состоянию классы, но с общим действием (методом)
- Когда нужно использовать множественное наследование
- Когда необходимо хранить общее состояние классов-наследников
- Во всех перечисленных выше случаях

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Когда необходимо хранить общее состояние классов-наследников

#### Ответ от Claude

Абстрактные классы, в отличие от интерфейсов, могут содержать поля (переменные состояния) и конструкторы. Это делает их подходящими для случаев, когда несколько наследников должны разделять общее состояние (например, поля `id` и `createdAt` для всех доменных сущностей). Интерфейсы в Java могут содержать только константы (`static final`), но не переменные состояния экземпляра. Множественное наследование реализуется через интерфейсы (не абстрактные классы). Уменьшение связанности и общие методы без состояния — также задачи интерфейсов.

Источники: [Oracle Java Tutorial — Abstract Methods and Classes](https://docs.oracle.com/javase/tutorial/java/IandI/abstract.html); [Oracle Java Tutorial — Interfaces vs. Abstract Classes](https://docs.oracle.com/javase/tutorial/java/IandI/interfaceDef.html).

---

### Вопрос 10. У вас есть иерархия классов для работы с фигурами: базовый класс Figure и два его дочерних класса — Rectangle и Circle. Класс Rectangle имеет дополнительный метод get_area(), который возвращает площадь прямоугольника. В языках со строгой типизацией, каким образом можно использовать приведение типов для получения площади прямоугольника, используя метод get_area()?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Привести объект класса Figure к типу Rectangle и вызвать метод get_area() на объекте класса Rectangle

#### Ответ от Claude

В языках со строгой типизацией (Java, C#) метод `get_area()`, определённый только в `Rectangle`, недоступен через переменную типа `Figure`. Для вызова необходимо выполнить **нисходящее приведение типов** (downcasting): привести переменную `Figure` к типу `Rectangle` и затем вызвать метод. В Java:

```java
Figure figure = new Rectangle(...);
if (figure instanceof Rectangle rect) {  // Java 16+ pattern matching
    double area = rect.get_area();
}
```

Перед приведением рекомендуется проверка `instanceof` во избежание `ClassCastException`. Downcasting используется, когда конкретный тип заранее известен или проверен.

Источники: [Oracle Java Tutorial — Type Casting](https://docs.oracle.com/javase/tutorial/java/IandI/subclasses.html); [JLS §15.16 Cast Expressions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.16).

---

### Вопрос 11. Параметрический полиморфизм осуществляется в первую очередь через использование…

**Категория:** OOP (HH) · **Уровень:** Intermediate

**Варианты ответа:**
- Ковариантности
- Обобщённых классов
- Виртуальных методов
- Множественного наследования
- Сужения класса

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Обобщённых классов

#### Ответ от Claude

**Параметрический полиморфизм** — вид полиморфизма, при котором код работает единообразно для разных типов, параметризованных при использовании. В Java он реализуется через **обобщённые классы и методы** (Generics, введены в Java 5): `List<T>`, `Map<K, V>`, `Optional<T>` и т.д. Тип-параметр `T` подставляется конкретным типом при использовании класса, что обеспечивает типобезопасность без дублирования кода. Виртуальные методы реализуют динамический полиморфизм (подтиповый), ковариантность — частный аспект системы типов.

Источники: [Oracle Java Tutorial — Generics](https://docs.oracle.com/javase/tutorial/java/generics/index.html); [JLS §8.1.2 Generic Classes and Type Parameters](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.1.2).

---

### Вопрос 12. У вас есть модули, которые зависят друг от друга: если вы меняете один модуль, вы должны внести изменения в зависимые модули. Какой термин используется для описания этой проблемы?

**Категория:** OOP (HH) · **Уровень:** Intermediate

#### Оригинальный ответ из интернета
> Источник: [HH Skill Verification — oop/intermediate.md](https://github.com/Londeren/hh-skill-verifications-quizzes/blob/main/oop/intermediate.md)

**Правильный ответ:** Проблема связанности

#### Ответ от Claude

**Связанность** (coupling) — метрика, характеризующая степень взаимозависимости между модулями (классами, компонентами). Высокая связанность (tight coupling) означает, что изменение одного модуля влечёт изменения в зависимых — именно эта проблема описана в вопросе. В ООП стремятся к **слабой связанности** (loose coupling): модули взаимодействуют через абстракции (интерфейсы), что позволяет изменять реализацию одного без изменения другого. Принцип инверсии зависимостей (DIP из SOLID) — один из ключевых инструментов снижения связанности.

Источники: [Refactoring Guru — Coupling and Cohesion](https://refactoring.guru/ru/refactoring/smells/couplers); Robert C. Martin, «Clean Architecture», глава 14 — Component Coupling.

---
