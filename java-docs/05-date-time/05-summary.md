# Урок 5. Итоги и упражнения

**Трейл:** Date-Time APIs · **Оригинал:** [Summary](https://docs.oracle.com/javase/tutorial/datetime/iso/summary.html)
**Связанные области:** [[09-modern-java-features]] · **Вопросы:** modern-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).
>
> Руководство The Java Tutorials написано для JDK 8. Примеры и практики, описанные на этой
> странице, не учитывают улучшений, появившихся в более поздних выпусках, и могут использовать
> технологии, которые больше недоступны.

## Итоги

> Пакет `java.time` содержит множество классов, которые ваши программы могут использовать для
> представления времени и даты. Это очень богатый API (*API*). Ключевые точки входа для дат на
> основе календаря ISO следующие:
>
> - Класс `Instant` предоставляет машинное представление шкалы времени (*machine view of the timeline*).
> - Классы `LocalDate`, `LocalTime` и `LocalDateTime` предоставляют человеческое представление
>   (*human view*) даты и времени без какой-либо привязки к часовому поясу (*time zone*).
> - Классы `ZoneId`, `ZoneRules` и `ZoneOffset` описывают часовые пояса (*time zones*), смещения
>   часовых поясов (*time zone offsets*) и правила часовых поясов (*time zone rules*).
> - Класс `ZonedDateTime` представляет дату и время вместе с часовым поясом. Классы `OffsetDateTime`
>   и `OffsetTime` представляют дату и время или, соответственно, только время. Эти классы учитывают
>   смещение часового пояса (*time zone offset*).
> - Класс `Duration` измеряет количество времени в секундах и наносекундах.
> - Класс `Period` измеряет количество времени в годах, месяцах и днях.
>
> Другие, неISO-системы летосчисления (*non-ISO calendar systems*) можно представить с помощью
> пакета `java.time.chrono`. Этот пакет выходит за рамки данного руководства, хотя страница
> «Преобразование неISO-даты» (*Non-ISO Date Conversion*) содержит сведения о преобразовании даты
> на основе ISO в другую систему летосчисления.
>
> Date-Time API был разработан в рамках процесса Java Community Process под обозначением JSR 310.
> Дополнительные сведения см. в [JSR 310: Date and Time API](https://jcp.org/en/jsr/detail?id=310).

## Вопросы и упражнения: Date-Time API

> **Оригинал:** [Questions and Exercises: Date-Time API](https://docs.oracle.com/javase/tutorial/datetime/iso/QandE/questions.html)

### Вопросы

> 1. Какой класс вы бы использовали для хранения дня рождения в годах, месяцах, днях, секундах и наносекундах?
>
> 2. Имея произвольную дату, как бы вы нашли дату предыдущего четверга?
>
> 3. В чём разница между `ZoneId` и `ZoneOffset`?
>
> 4. Как преобразовать `Instant` в `ZonedDateTime`? Как преобразовать `ZonedDateTime` в `Instant`?

### Упражнения

> 1. Напишите пример, который для заданного года сообщает длину каждого месяца в этом году.
>
> 2. Напишите пример, который для заданного месяца текущего года перечисляет все понедельники этого месяца.
>
> 3. Напишите пример, который проверяет, выпадает ли заданная дата на пятницу 13-го.

### Ответы

> **Оригинал:** [Answers to Questions and Exercises: Date-Time API](https://docs.oracle.com/javase/tutorial/datetime/iso/QandE/answers.html)

**Ответ на вопрос 1.** Скорее всего, вы бы использовали класс `LocalDateTime`. Чтобы учесть
конкретный часовой пояс, вы бы использовали класс `ZonedDateTime`. Оба класса отслеживают дату и
время с точностью до наносекунды, и оба класса при использовании вместе с `Period` дают результат
в комбинации человеко-ориентированных единиц (*human-based units*), таких как годы, месяцы и дни.

**Ответ на вопрос 2.** Можно использовать метод `previous` из `TemporalAdjuster`:

```java
LocalDate date = ...;
System.out.printf("Предыдущий четверг: %s%n",
          date.with(TemporalAdjuster.previous(DayOfWeek.THURSDAY)));
```

**Ответ на вопрос 3.** И `ZoneId`, и `ZoneOffset` отслеживают смещение относительно времени
Гринвича/UTC, но класс `ZoneOffset` отслеживает только абсолютное смещение относительно
Гринвича/UTC. Класс `ZoneId` дополнительно использует `ZoneRules`, чтобы определить, как смещение
изменяется для конкретного времени года и региона.

**Ответ на вопрос 4.** Преобразовать `Instant` в `ZonedDateTime` можно с помощью метода
`ZonedDateTime.ofInstant`. Также необходимо указать `ZoneId`:

```java
ZonedDateTime zdt = ZonedDateTime.ofInstant(Instant.now(),
                                            ZoneId.systemDefault());
```

Либо можно использовать метод `Instant.atZone`:

```java
ZonedDateTime zdt = Instant.now().atZone(ZoneId.systemDefault());
```

Для преобразования из `ZonedDateTime` в `Instant` можно использовать метод `toInstant` интерфейса
`ChronoZonedDateTime`, реализуемого классом `ZonedDateTime`:

```java
Instant inst = ZonedDateTime.now().toInstant();
```

**Ответ на упражнение 1.** Решение см. в `MonthsInYear.java`.

**Ответ на упражнение 2.** Решение см. в `ListMondays.java`.

**Ответ на упражнение 3.** Решение см. в `Superstitious.java` и `FridayThirteenQuery.java`.

## Источник

- [Summary (The Java Tutorials > Date Time > Standard Calendar)](https://docs.oracle.com/javase/tutorial/datetime/iso/summary.html) — официальное руководство Oracle.
- [Questions and Exercises: Date-Time API](https://docs.oracle.com/javase/tutorial/datetime/iso/QandE/questions.html) — официальное руководство Oracle.
- [Answers to Questions and Exercises: Date-Time API](https://docs.oracle.com/javase/tutorial/datetime/iso/QandE/answers.html) — официальное руководство Oracle.
