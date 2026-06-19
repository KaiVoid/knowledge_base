# JVM, модель памяти и сборка мусора

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по JVM и GC →](../../../interview-questions/jvm-gc-01.md)
> **Связанные области:** [[04-concurrency]], [[01-core-java-syntax-oop]]

## Что это и зачем

Понимание устройства виртуальной машины Java объясняет, как код исполняется и как управляется память.
Сюда входят: загрузка классов (ClassLoader), области данных среды выполнения (heap, stack, metaspace,
PC-регистр), JIT-компиляция, модель памяти Java (JMM) и алгоритмы сборки мусора (GC). Эти знания
критичны для диагностики утечек памяти, настройки производительности и понимания поведения
многопоточного кода (happens-before).

Без понимания JVM-архитектуры невозможно объяснить: почему `OutOfMemoryError` возникает в Metaspace,
а не в heap; почему `volatile` гарантирует видимость, но не атомарность составных операций; почему ZGC
выдаёт субмиллисекундные паузы при heap в несколько гигабайт. Именно поэтому эта область является
обязательной для позиций Middle и Senior.

---

## Ключевые подтемы

### Архитектура JVM: области данных среды выполнения

Согласно [Java Virtual Machine Specification (SE 21), глава 2](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html),
JVM определяет шесть областей данных:

| Область | Область видимости | Создаётся | Уничтожается |
|---|---|---|---|
| PC Register | per-thread | при старте потока | при завершении потока |
| JVM Stack | per-thread | при старте потока | при завершении потока |
| Native Method Stack | per-thread | при старте потока | при завершении потока |
| Heap | общая | при старте JVM | при завершении JVM |
| Method Area | общая | при старте JVM | при завершении JVM |
| Run-Time Constant Pool | per-class | при загрузке класса | при завершении JVM |

**PC Register (program counter register)** — у каждого потока свой регистр. Если выполняется
не-`native` метод, хранит адрес текущей инструкции JVM. Для `native`-методов значение не определено.

**JVM Stack** — стек фреймов вызовов. Каждый фрейм содержит массив локальных переменных, стек
операндов и ссылку на run-time constant pool текущего класса. При рекурсии без базового случая
выбрасывается `StackOverflowError`; если нельзя выделить новый стек — `OutOfMemoryError`.

**Heap** — единственная область, где выделяется память для экземпляров классов и массивов. Объекты
никогда не освобождаются явно — за это отвечает сборщик мусора. Может быть расширяема динамически;
при нехватке — `OutOfMemoryError`.

**Method Area** (в HotSpot реализована как **Metaspace**) — хранит per-class структуры: run-time
constant pool, данные полей и методов, байткод методов. Логически является частью heap, но физически
расположена в нативной (off-heap) памяти начиная с Java 8. Для управления размером:

```
-XX:MetaspaceSize=<size>       # начальный размит; при достижении — Full GC
-XX:MaxMetaspaceSize=<size>    # жёсткий потолок (по умолчанию — не ограничен)
```

> Внимание: `-XX:MetaspaceSize` — это не начальный зарезервированный размер, а порог для первого
> Full GC. Без `-XX:MaxMetaspaceSize` Metaspace может вырасти до исчерпания нативной памяти.

**Compressed Class Space** — при включённых Compressed Oops (`-XX:+UseCompressedClassPointers`,
по умолчанию включено для heap < 32 ГБ) структуры `Klass` хранятся в отдельном
непрерывном регионе памяти (по умолчанию 1 ГБ). Это позволяет использовать 32-битные указатели
на классы вместо 64-битных.

**Compressed Oops** — техника представления managed-указателей как 32-битных смещений от базового
адреса heap. Объекты выравнены на 8 байт, что позволяет адресовать heap до ~32 ГБ с 32-битными
указателями. Включается по умолчанию для heap < 32 ГБ; флаг `-XX:+UseCompressedOops`.

---

### Загрузка классов (ClassLoader)

Процесс загрузки класса согласно [JVMS SE 21, глава 5](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-5.html)
состоит из трёх фаз:

1. **Loading (Загрузка)** — поиск бинарного представления класса (`.class`-файла) и создание
   объекта `Class`. Выполняется конкретным ClassLoader.

2. **Linking (Связывание)** — три подфазы:
   - **Verification** — проверка корректности байткода; при ошибке — `VerifyError`.
   - **Preparation** — создание статических полей с нулевыми/дефолтными значениями; явные
     инициализаторы ещё НЕ выполняются.
   - **Resolution** — преобразование символических ссылок в конкретные (может быть ленивым).

3. **Initialization (Инициализация)** — выполнение статического инициализатора `<clinit>`.
   Триггеры: `new`, `getstatic`, `putstatic`, `invokestatic`, первый вызов определённых
   `MethodHandle`, рефлексивные вызовы через `Class`.

**Иерархия ClassLoader в HotSpot:**

```
Bootstrap ClassLoader (встроен в JVM, загружает java.base и другие platform-модули)
    |
Platform ClassLoader (загружает модули платформы, JDK 9+; раньше — Extension CL)
    |
Application ClassLoader (загружает classpath/modulepath приложения)
    |
User-defined ClassLoaders (OSGi, контейнеры, горячая перезагрузка)
```

**Модель делегирования (parent-first delegation):** перед загрузкой класса загрузчик сначала
делегирует родителю. Это предотвращает подмену системных классов. Нарушение модели возможно
(например, в OSGi), но требует осторожности из-за `LinkageError` при несовместимости версий.

---

### JIT-компиляция в HotSpot

HotSpot сочетает интерпретацию и компиляцию через **Tiered Compilation** (уровневую компиляцию),
включённую по умолчанию начиная с Java 7.

**Уровни компиляции:**

| Уровень | Компилятор | Характеристика |
|---|---|---|
| 0 | Интерпретатор | Медленное выполнение, сбор профиля |
| 1 | C1 (client) | Быстрая компиляция, минимум оптимизаций |
| 2 | C1 | Компиляция с ограниченным профилированием |
| 3 | C1 | Компиляция с полным профилированием |
| 4 | C2 (server) | Агрессивные оптимизации на основе профиля |

Метод сначала проходит уровни 0 → 3 → 4. При достаточной информации профиля C2 применяет
спекулятивные оптимизации (inlining, devirtualization). Если предположение нарушается —
происходит **deoptimization** и возврат к интерпретатору.

**Code Cache** (сегментированный, начиная с Java 9):
- `NonMethod` — внутренний код JVM, интерпретатор (постоянно в кэше); по умолчанию ~3 МБ.
- `Profiled` — слегка оптимизированный код с ограниченным временем жизни (уровни 1–3).
- `NonProfiled` — полностью оптимизированный долгоживущий код (уровень 4).

**Escape Analysis** (включён по умолчанию, Java 6u23+) — анализирует, выходит ли объект за
пределы метода/потока. Если объект не выходит (`NoEscape`), компилятор может:
- Выделить его на стеке вместо heap (stack allocation).
- Провести scalar replacement — разложить на отдельные локальные переменные.
- Устранить синхронизацию через **lock elision** (например, для `StringBuffer` в одном потоке).

---

### Алгоритмы сборки мусора: обзор и сравнение

Согласно [Oracle GC Tuning Guide для Java 21](https://docs.oracle.com/en/java/javase/21/gctuning/available-collectors.html),
в HotSpot доступны четыре поддерживаемых сборщика:

| GC | Флаг | Паузы | Пропускная способность | Heap | Рекомендуется для |
|---|---|---|---|---|---|
| Serial | `-XX:+UseSerialGC` | Stop-the-world | Средняя | до ~100 МБ | однопоточные/embedded |
| Parallel | `-XX:+UseParallelGC` | Stop-the-world | Максимальная | средний/большой | batch-обработка |
| G1 | `-XX:+UseG1GC` | Конкурентный + STW | Хорошая | > 4 ГБ | серверные приложения (default) |
| ZGC | `-XX:+UseZGC` | < 1 мс | Хорошая | 100 МБ — 16 ТБ | low-latency |

> Shenandoah — низкопаузный конкурентный сборщик (не входит в Oracle JDK, доступен в OpenJDK).

**Принцип выбора сборщика** (из официального руководства):
1. Если приложение работает на небольших данных (< 100 МБ) — Serial.
2. Если критична пропускная способность и паузы в секунду приемлемы — Parallel.
3. Если нужен баланс между паузами и пропускной способностью — G1 (выбирается по умолчанию).
4. Если задержка критична и паузы должны быть < 1 мс — ZGC.

---

### Serial и Parallel GC

**Serial GC** использует единственный поток для minor и major коллекций. Нет накладных расходов
на синхронизацию потоков — эффективен для небольших приложений и embedded-систем.

**Parallel GC** (throughput collector) — использует несколько потоков для параллельных stop-the-world
пауз. Поддерживает автоматическую настройку (ergonomics) на основе заданных целей:

```
-XX:MaxGCPauseMillis=<N>    # цель: максимальное время паузы (мс), приоритет наивысший
-XX:GCTimeRatio=<N>         # цель: доля времени GC = 1/(1+N); по умолчанию 99 → 1% на GC
```

Количество потоков GC по умолчанию: при N > 8 ядер — `5/8 * N`; иначе — N. Настраивается:
`-XX:ParallelGCThreads=<N>`.

При превышении 98% времени на GC при освобождении < 2% кучи JVM бросает `OutOfMemoryError`.
Отключить: `-XX:-UseGCOverheadLimit`.

---

### G1 GC (Garbage-First)

[G1](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector1.html)
— сборщик по умолчанию для большинства конфигураций начиная с Java 9. Разбивает heap на равные
**регионы** (по умолчанию ~2048 штук, размер 1–32 МБ), каждый из которых независимо может
быть Eden, Survivor, Old или Humongous.

**Цикл сборки мусора G1 чередует две фазы:**

1. **Young-Only Phase** — только молодое поколение (Eden + Survivor). При достижении порога IHOP
   (`-XX:InitiatingHeapOccupancyPercent=45%`) запускается конкурентное маркирование старого
   поколения.

2. **Space-Reclamation Phase** — Mixed Collections: собирают молодое поколение + выбранные старые
   регионы с наибольшим количеством мусора (принцип "Garbage First").

**Humongous objects** — объекты размером >= половины региона. Выделяются напрямую в Old Generation
как последовательность регионов; освобождаются только в Cleanup-паузе или Full GC.

**Ключевые флаги G1:**

```
-XX:MaxGCPauseTimeMillis=200           # целевое максимальное время паузы (мс)
-XX:InitiatingHeapOccupancyPercent=45  # порог занятости Old Gen для начала маркирования
-XX:G1HeapRegionSize=<size>            # размер региона (1–32 МБ, степень двойки)
-XX:G1NewSizePercent=5                 # минимальный размер Young Gen в % от heap
-XX:G1MaxNewSizePercent=60             # максимальный размер Young Gen в % от heap
-XX:G1MixedGCCountTarget=8            # ожидаемое число Mixed Collections в фазе
-XX:G1HeapWastePercent=5              # не начинать Space-Reclamation если < 5% мусора
-XX:ConcGCThreads=<N>                 # потоки для конкурентного маркирования
```

---

### ZGC (Z Garbage Collector)

[ZGC](https://docs.oracle.com/en/java/javase/21/gctuning/z-garbage-collector.html) — масштабируемый
низкопаузный сборщик. Все дорогостоящие операции (маркирование, перемещение объектов) выполняются
**конкурентно** с приложением. Паузы < 1 мс и не зависят от размера heap.

**Две версии ZGC (Java 21):**
- **Generational ZGC** (рекомендуется): `-XX:+UseZGC -XX:+ZGenerational`
- **Non-generational ZGC**: `-XX:+UseZGC`

**Технические механизмы:**
- **Colored pointers** — биты в 64-битном указателе кодируют метаданные GC (marked, remapped,
  finalizable). Это позволяет read/load barriers принимать решения без обращения к отдельным
  структурам данных.
- **Load barriers** — код, вставляемый JIT при чтении ссылок из heap; обновляет указатели
  «на лету» во время конкурентного перемещения объектов.

**Основные флаги ZGC:**

```
-Xmx<size>                      # главный параметр: задаёт максимальный размер heap
-XX:SoftMaxHeapSize=<size>      # мягкий лимит: ZGC стремится не превышать это значение
-XX:-ZUncommit                  # не возвращать неиспользуемую память ОС
-XX:ZUncommitDelay=<seconds>    # задержка перед возвратом памяти (по умолчанию 300 с)
```

> Для ZGC главный рычаг настройки — размер heap (`-Xmx`). Чем больше heap, тем меньше
> конкуренция между приложением и GC за пространство. Подробная настройка обычно не требуется.

---

### Shenandoah GC

[Shenandoah](https://openjdk.org/jeps/189) — низкопаузный сборщик из OpenJDK (не входит в
Oracle JDK). Как и ZGC, выполняет компактизацию конкурентно с приложением, что делает паузы
независимыми от размера heap.

Ключевое отличие от ZGC: использует **Brooks forwarding pointers** (дополнительный указатель
в заголовке объекта) вместо colored pointers. Это менее эффективно по памяти, но не требует
поддержки 64-битных адресов с цветовыми битами.

Включение: `-XX:+UseShenandoahGC` (требует `-XX:+UnlockExperimentalVMOptions` для некоторых
сборок). Generational Shenandoah (экспериментально): [JEP 404](https://openjdk.org/jeps/404).

---

### Типы ссылок: strong, soft, weak, phantom

JVM поддерживает несколько уровней достижимости объектов:

| Тип ссылки | Класс | Очищается GC | Типичное применение |
|---|---|---|---|
| Strong | обычная ссылка | Никогда | Обычные объекты |
| Soft | `SoftReference<T>` | При нехватке памяти | Кэши |
| Weak | `WeakReference<T>` | При следующем GC | `WeakHashMap`, канонические маппинги |
| Phantom | `PhantomReference<T>` | После финализации | Замена `finalize()`, `Cleaner` API |

**Soft References** — контролируются флагом `-XX:SoftRefLRUPolicyMSPerMB=1000`
(по умолчанию 1000 мс на МБ свободной памяти). На server VM удерживаются дольше, чем на client.

**Finalization** — помечена deprecated с JDK 9, запланирована к удалению (JEP 421 в JDK 18).
Проблемы: непредсказуемое время, возможность "воскресения" объектов, снижение производительности.
Рекомендуемая замена — `Cleaner` API (`java.lang.ref.Cleaner`):

```java
import java.lang.ref.Cleaner;

public class Resource implements AutoCloseable {
    private static final Cleaner CLEANER = Cleaner.create();
    private final Cleaner.Cleanable cleanable;

    public Resource() {
        // State содержит только примитивы/нативные дескрипторы, НЕ ссылку на внешний объект
        cleanable = CLEANER.register(this, new State());
    }

    @Override
    public void close() {
        cleanable.clean();
    }

    private static class State implements Runnable {
        @Override
        public void run() {
            // освобождение нативных ресурсов
        }
    }
}
```

---

### Модель памяти Java (JMM) и happens-before

Java Memory Model определена в [JLS SE 21, глава 17](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html).
JMM не гарантирует sequential consistency — она определяет минимальные правила видимости
через **happens-before**.

**Правила happens-before (hb):**
- Действия одного потока в порядке программы: `hb(x, y)` если x предшествует y.
- Разблокировка монитора → все последующие блокировки того же монитора.
- Запись в `volatile` поле → все последующие чтения того же поля.
- `Thread.start()` → все действия в запущенном потоке.
- Все действия потока → успешный `Thread.join()` на этом потоке.
- Транзитивность: `hb(x,y)` и `hb(y,z)` → `hb(x,z)`.

**volatile** — гарантирует видимость и запрещает переупорядочивание относительно volatile-операции,
но НЕ гарантирует атомарность составных операций (`i++` на volatile — не атомарно):

```java
// Корректный паттерн: double-checked locking с volatile
class Singleton {
    private volatile static Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();  // volatile предотвращает частичную публикацию
                }
            }
        }
        return instance;
    }
}
```

**Data race** — два конкурентных обращения к переменной (хотя бы одно — запись), не упорядоченных
через happens-before. Программа с data race имеет неопределённое поведение в рамках JMM.

**final-поля** — если объект полностью инициализирован до первого обращения, все `final`-поля
гарантированно видны корректно любому потоку без дополнительной синхронизации (freeze action).

---

### Утечки памяти, OutOfMemoryError, анализ heap dump

**Распространённые причины `OutOfMemoryError`:**

| Сообщение OOM | Причина |
|---|---|
| `Java heap space` | Объекты не собираются GC; утечка или недостаточный `-Xmx` |
| `GC overhead limit exceeded` | > 98% времени на GC, < 2% освобождается |
| `Metaspace` | Утечка ClassLoader (например, при горячей перезагрузке без выгрузки) |
| `Unable to create new native thread` | Исчерпание нативной памяти для стеков потоков |
| `Direct buffer memory` | Утечка NIO DirectByteBuffer |

**Получение heap dump для анализа:**
```
# При OOM автоматически:
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heapdump.hprof

# Вручную через jcmd:
jcmd <pid> GC.heap_dump /tmp/heapdump.hprof

# Вручную через jmap:
jmap -dump:live,format=b,file=/tmp/heapdump.hprof <pid>
```

**Анализ:** Eclipse MAT, JDK Mission Control, VisualVM — поиск объектов с наибольшим
retained heap, анализ путей до GC roots.

**Основные JVM-флаги для диагностики:**
```
-verbose:gc                            # вывод событий GC в stderr
-Xlog:gc*:file=gc.log:time,uptime      # структурированный GC лог (JDK 9+)
-XX:+PrintGCDetails                    # детальный лог (устарел в JDK 9)
-XX:NativeMemoryTracking=summary       # отслеживание нативной памяти
jcmd <pid> VM.native_memory summary   # сводка нативной памяти
```

---

## Достоверные источники

1. **[Java Virtual Machine Specification, SE 21](https://docs.oracle.com/javase/specs/jvms/se21/html/)**
   — официальная спецификация Oracle. Первичный источник истины для всех вопросов об областях памяти,
   загрузке классов, байткоде. Нормативный документ, на который ссылаются все остальные.

2. **[HotSpot GC Tuning Guide, Java 21](https://docs.oracle.com/en/java/javase/21/gctuning/)**
   — официальное руководство Oracle по настройке сборщиков мусора. Описывает все поддерживаемые GC,
   их характеристики, флаги и эргономику. Единственный авторитетный источник по выбору и настройке GC.

3. **[Java Language Specification, SE 21, глава 17 — Threads and Locks](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)**
   — официальная спецификация JMM от Oracle. Нормативное определение happens-before, volatile,
   final-полей и корректного выполнения многопоточных программ.

4. **[HotSpot VM Performance Enhancements (Java 22 docs)](https://docs.oracle.com/en/java/javase/22/vm/java-hotspot-virtual-machine-performance-enhancements.html)**
   — официальная документация Oracle о JIT-оптимизациях: tiered compilation, escape analysis,
   compressed oops, segmented code cache. Применима к Java 21 по содержанию.

5. **[OpenJDK JEP 189 — Shenandoah GC](https://openjdk.org/jeps/189)**
   — официальный JEP (Java Enhancement Proposal) от OpenJDK. Первичный источник по архитектуре
   и цели проектирования Shenandoah.

6. **[OpenJDK JEP 387 — Elastic Metaspace](https://openjdk.org/jeps/387)**
   — официальный JEP, описывающий архитектуру Metaspace (commit granules, возврат памяти ОС).
   Единственный достоверный источник по внутренней реализации Metaspace в современных версиях HotSpot.
