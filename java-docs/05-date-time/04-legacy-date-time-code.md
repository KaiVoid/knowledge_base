# Урок 4. Старый код даты и времени

**Трейл:** Date-Time APIs · **Оригинал:** [Legacy Date-Time Code](https://docs.oracle.com/javase/tutorial/datetime/iso/legacy.html)
**Связанные области:** [[09-modern-java-features]] · **Вопросы:** modern-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

До выпуска Java SE 8 механизм работы с датой и временем в Java обеспечивали классы
[`java.util.Date`](https://docs.oracle.com/javase/8/docs/api/java/util/Date.html),
[`java.util.Calendar`](https://docs.oracle.com/javase/8/docs/api/java/util/Calendar.html) и
[`java.util.TimeZone`](https://docs.oracle.com/javase/8/docs/api/java/util/TimeZone.html), а также
их подклассы — например,
[`java.util.GregorianCalendar`](https://docs.oracle.com/javase/8/docs/api/java/util/GregorianCalendar.html).
У этих классов был ряд недостатков, в том числе:

- Класс `Calendar` не был типобезопасным (type safe).
- Поскольку классы были изменяемыми (mutable), их нельзя было использовать в многопоточных
  (multithreaded) приложениях.
- Ошибки в коде приложений возникали часто из-за необычной нумерации месяцев и отсутствия
  типобезопасности.

## Взаимодействие со старым кодом (Interoperability with Legacy Code)

Возможно, у вас есть устаревший код, использующий классы даты и времени из `java.util`, и вы
хотели бы воспользоваться возможностями `java.time` с минимальными изменениями в своём коде.

В выпуск JDK 8 добавлено несколько методов, которые позволяют выполнять преобразования между
объектами `java.util` и `java.time`:

- [`Calendar.toInstant()`](https://docs.oracle.com/javase/8/docs/api/java/util/Calendar.html#toInstant--)
  преобразует объект `Calendar` в `Instant`.
- [`GregorianCalendar.toZonedDateTime()`](https://docs.oracle.com/javase/8/docs/api/java/util/GregorianCalendar.html#toZonedDateTime--)
  преобразует экземпляр `GregorianCalendar` в `ZonedDateTime`.
- [`GregorianCalendar.from(ZonedDateTime)`](https://docs.oracle.com/javase/8/docs/api/java/util/GregorianCalendar.html#from-java.time.ZonedDateTime-)
  создаёт объект `GregorianCalendar` из экземпляра `ZonedDateTime`, используя локаль по умолчанию.
- [`Date.from(Instant)`](https://docs.oracle.com/javase/8/docs/api/java/util/Date.html#from-java.time.Instant-)
  создаёт объект `Date` из `Instant`.
- [`Date.toInstant()`](https://docs.oracle.com/javase/8/docs/api/java/util/Date.html#toInstant--)
  преобразует объект `Date` в `Instant`.
- [`TimeZone.toZoneId()`](https://docs.oracle.com/javase/8/docs/api/java/util/TimeZone.html#toZoneId--)
  преобразует объект `TimeZone` в `ZoneId`.

В следующем примере экземпляр `Calendar` преобразуется в экземпляр `ZonedDateTime`. Обратите
внимание, что для преобразования из `Instant` в `ZonedDateTime` необходимо указать часовой пояс
(time zone):

```java
Calendar now = Calendar.getInstance();
ZonedDateTime zdt = ZonedDateTime.ofInstant(now.toInstant(), ZoneId.systemDefault()));
```

В следующем примере показано преобразование между `Date` и `Instant`:

```java
Instant inst = date.toInstant();

Date newDate = Date.from(inst);
```

В следующем примере выполняется преобразование из `GregorianCalendar` в `ZonedDateTime`, а затем
из `ZonedDateTime` обратно в `GregorianCalendar`. Другие классы, основанные на времени
(temporal-based), создаются с использованием экземпляра `ZonedDateTime`:

```java
GregorianCalendar cal = ...;

TimeZone tz = cal.getTimeZone();
int tzoffset = cal.get(Calendar.ZONE_OFFSET);

ZonedDateTime zdt = cal.toZonedDateTime();

GregorianCalendar newCal = GregorianCalendar.from(zdt);

LocalDateTime ldt = zdt.toLocalDateTime();
LocalDate date = zdt.toLocalDate();
LocalTime time = zdt.toLocalTime();
```

## Сопоставление функциональности даты и времени `java.util` с `java.time`

Поскольку реализация даты и времени в Java была полностью переработана в выпуске Java SE 8, нельзя
просто заменить один метод другим. Если вы хотите использовать богатую функциональность,
предлагаемую пакетом `java.time`, самое простое решение — применить методы `toInstant` или
`toZonedDateTime`, перечисленные в предыдущем разделе. Однако если вы не хотите использовать этот
подход или его недостаточно для ваших нужд, придётся переписать ваш код работы с датой и временем.

Хорошая отправная точка для оценки того, какие классы `java.time` отвечают вашим потребностям, —
таблица, представленная на странице [Обзор](https://docs.oracle.com/javase/tutorial/datetime/iso/overview.html)
(Overview).

Однозначного соответствия «один к одному» между двумя API нет, но следующая таблица даёт общее
представление о том, какая функциональность классов даты и времени `java.util` соответствует API
`java.time`.

| Функциональность `java.util` | Функциональность `java.time` | Комментарии |
|---|---|---|
| `java.util.Date` | `java.time.Instant` | Классы `Instant` и `Date` похожи. Каждый из них: <br>— представляет мгновенный момент времени на временной шкале (в UTC); <br>— хранит время независимо от часового пояса; <br>— представлен в виде секунд эпохи (epoch-seconds, начиная с 1970-01-01T00:00:00Z) плюс наносекунды. <br>Методы `Date.from(Instant)` и `Date.toInstant()` позволяют выполнять преобразование между этими классами. |
| `java.util.GregorianCalendar` | `java.time.ZonedDateTime` | Класс `ZonedDateTime` является заменой `GregorianCalendar`. Он предоставляет следующую аналогичную функциональность. <br>Представление времени в «человеческом» виде выглядит так: <br>  `LocalDate`: год, месяц, день; <br>  `LocalTime`: часы, минуты, секунды, наносекунды; <br>  `ZoneId`: часовой пояс; <br>  `ZoneOffset`: текущее смещение от GMT. <br>Методы `GregorianCalendar.from(ZonedDateTime)` и `GregorianCalendar.to(ZonedDateTime)` облегчают преобразования между этими классами. |
| `java.util.TimeZone` | `java.time.ZoneId` или `java.time.ZoneOffset` | Класс `ZoneId` задаёт идентификатор часового пояса и имеет доступ к правилам, используемым для каждого часового пояса. Класс `ZoneOffset` задаёт только смещение от Гринвича/UTC. Подробнее см. [Классы часового пояса и смещения](https://docs.oracle.com/javase/tutorial/datetime/iso/timezones.html) (Time Zone and Offset Classes). |
| `GregorianCalendar` с датой, установленной в 1970-01-01 | `java.time.LocalTime` | Код, который устанавливает дату в значение 1970-01-01 в экземпляре `GregorianCalendar`, чтобы использовать компоненты времени, можно заменить экземпляром `LocalTime`. |
| `GregorianCalendar` с временем, установленным в 00:00 | `java.time.LocalDate` | Код, который устанавливает время в значение 00:00 в экземпляре `GregorianCalendar`, чтобы использовать компоненты даты, можно заменить экземпляром `LocalDate`. (Этот подход с `GregorianCalendar` был ошибочным, так как в некоторых странах полночь раз в год не наступает из-за перехода на летнее время.) |

> Примечание о терминах таблицы. В перечне методов выше Oracle называет метод преобразования
> `GregorianCalendar.toZonedDateTime()`; в комментарии к таблице он же упомянут как
> `GregorianCalendar.to(ZonedDateTime)`. Текст приведён дословно по оригиналу; фактическое имя
> метода в JDK 8 — `toZonedDateTime()`.

## Форматирование даты и времени (Date and Time Formatting)

Хотя класс `java.time.format.DateTimeFormatter` предоставляет мощный механизм форматирования
значений даты и времени, вы также можете использовать классы `java.time`, основанные на времени,
напрямую с `java.util.Formatter` и `String.format`, применяя то же форматирование по шаблону
(pattern-based formatting), которое вы используете с классами даты и времени `java.util`.

## Источник

- [Legacy Date-Time Code](https://docs.oracle.com/javase/tutorial/datetime/iso/legacy.html) — официальное руководство Oracle.
