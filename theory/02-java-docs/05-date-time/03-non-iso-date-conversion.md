# Урок 3. Преобразование не-ISO дат

**Трейл:** Date-Time APIs · **Оригинал:** [Non-ISO Date Conversion](https://docs.oracle.com/javase/tutorial/datetime/iso/nonIso.html)
**Связанные области:** [[09-modern-java-features]] · **Вопросы:** modern-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

Это руководство не описывает пакет `java.time.chrono` подробно, но стоит отметить, что он
предоставляет несколько предопределённых хронологий (*chronology*), основанных на не-ISO
календарных системах: японской (*Japanese*), хиджры (*Hijrah*), Миньго (*Minguo*) и тайской
буддийской (*Thai Buddhist*). С помощью этого пакета можно также создать собственную
пользовательскую хронологию. Этот раздел показывает, как выполнять преобразование между датой,
основанной на ISO, и датой в одной из других доступных предопределённых хронологий.

## Преобразование в дату на основе не-ISO хронологии

Чтобы преобразовать дату на основе ISO в дату другой хронологии, используйте метод
`from(TemporalAccessor)`, например `JapaneseDate.from(TemporalAccessor)`. Этот метод выбрасывает
исключение `DateTimeException`, если не может успешно преобразовать дату в корректный экземпляр.

В следующих строках выполняется преобразование экземпляра `LocalDateTime` в даты разных
хронологий:

```java
LocalDateTime date = LocalDateTime.of(2013, Month.JULY, 20, 19, 30);
JapaneseDate jdate     = JapaneseDate.from(date);
HijrahDate hdate       = HijrahDate.from(date);
MinguoDate mdate       = MinguoDate.from(date);
ThaiBuddhistDate tdate = ThaiBuddhistDate.from(date);
```

Пример `StringConverter` демонстрирует преобразование из `LocalDate` в `ChronoLocalDate`, затем в
`String` и обратно. Метод `toString` принимает экземпляр `LocalDate` и хронологию (`Chronology`),
а возвращает преобразованную строку, применяя переданную хронологию. Для построения строки,
пригодной для печати даты, используется `DateTimeFormatterBuilder`.

```java
/**
 * Преобразует значение LocalDate (ISO) в дату ChronoLocalDate
 * с помощью переданной хронологии (Chronology), а затем форматирует
 * ChronoLocalDate в строку с помощью DateTimeFormatter с шаблоном
 * SHORT, основанным на хронологии и текущей локали.
 *
 * @param localDate - ISO-дата для преобразования и форматирования.
 * @param chrono - необязательная хронология. Если null, используется IsoChronology.
 */
public static String toString(LocalDate localDate, Chronology chrono) {
    if (localDate != null) {
        Locale locale = Locale.getDefault(Locale.Category.FORMAT);
        ChronoLocalDate cDate;
        if (chrono == null) {
            chrono = IsoChronology.INSTANCE;
        }
        try {
            cDate = chrono.date(localDate);
        } catch (DateTimeException ex) {
            System.err.println(ex);
            chrono = IsoChronology.INSTANCE;
            cDate = localDate;
        }
        DateTimeFormatter dateFormatter =
            DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
                             .withLocale(locale)
                             .withChronology(chrono)
                             .withDecimalStyle(DecimalStyle.of(locale));
        String pattern = "M/d/yyyy GGGGG";
        return dateFormatter.format(cDate);
    } else {
        return "";
    }
}
```

Следующие строки кода выводят дату в нескольких хронологиях:

```java
LocalDate date = LocalDate.of(1996, Month.OCTOBER, 29);
System.out.printf("%s%n",
     StringConverter.toString(date, JapaneseChronology.INSTANCE));
System.out.printf("%s%n",
     StringConverter.toString(date, MinguoChronology.INSTANCE));
System.out.printf("%s%n",
     StringConverter.toString(date, ThaiBuddhistChronology.INSTANCE));
System.out.printf("%s%n",
     StringConverter.toString(date, HijrahChronology.INSTANCE));
```

Этот код выводит следующее:

```
10/29/0008 H
10/29/0085 1
10/29/2539 B.E.
6/16/1417 1
```

## Преобразование в дату на основе ISO

Преобразовать не-ISO дату в экземпляр `LocalDate` можно с помощью статического метода
`LocalDate.from`, как показано в следующем примере:

```java
LocalDate date = LocalDate.from(JapaneseDate.now());
```

Другие классы, основанные на работе со временем (*temporal-based*), также предоставляют этот метод.
Метод выбрасывает исключение `DateTimeException`, если дату не удаётся преобразовать.

Метод `fromString` из примера `StringConverter` разбирает строку (`String`), содержащую не-ISO
дату, и возвращает экземпляр `LocalDate`:

```java
/**
 * Разбирает строку (String) в ChronoLocalDate с помощью DateTimeFormatter
 * с коротким шаблоном, основанным на текущей локали и переданной
 * хронологии (Chronology), а затем преобразует результат в значение
 * LocalDate (ISO).
 *
 * @param text   - входной текст даты в формате SHORT, ожидаемом
 *                 для данной хронологии и текущей локали.
 *
 * @param chrono - необязательная хронология. Если null, используется
 *                 IsoChronology.
 */
public static LocalDate fromString(String text, Chronology chrono) {
    if (text != null && !text.isEmpty()) {
        Locale locale = Locale.getDefault(Locale.Category.FORMAT);
        if (chrono == null) {
           chrono = IsoChronology.INSTANCE;
        }
        String pattern = "M/d/yyyy GGGGG";
        DateTimeFormatter df = new DateTimeFormatterBuilder().parseLenient()
                              .appendPattern(pattern)
                              .toFormatter()
                              .withChronology(chrono)
                              .withDecimalStyle(DecimalStyle.of(locale));
        TemporalAccessor temporal = df.parse(text);
        ChronoLocalDate cDate = chrono.date(temporal);
        return LocalDate.from(cDate);
    }
return null;
}
```

Следующие строки кода разбирают четыре даты разных хронологий и преобразуют их в `LocalDate`:

```java
System.out.printf("%s%n", StringConverter.fromString("10/29/0008 H",
    JapaneseChronology.INSTANCE));
System.out.printf("%s%n", StringConverter.fromString("10/29/0085 1",
    MinguoChronology.INSTANCE));
System.out.printf("%s%n", StringConverter.fromString("10/29/2539 B.E.",
    ThaiBuddhistChronology.INSTANCE));
System.out.printf("%s%n", StringConverter.fromString("6/16/1417 1",
    HijrahChronology.INSTANCE));
```

Этот код выводит следующее:

```
1996-10-29
1996-10-29
1996-10-29
1996-10-29
```

## Источник

- [Non-ISO Date Conversion](https://docs.oracle.com/javase/tutorial/datetime/iso/nonIso.html) — официальное руководство Oracle (The Java Tutorials, JDK 8).
