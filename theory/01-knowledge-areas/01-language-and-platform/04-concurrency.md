# Многопоточность и concurrency

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по многопоточности →](../../../interview-questions/concurrency-01.md)
> **Углублённо:** [Конкурентные коллекции (java.util.concurrent) →](04-concurrent-collections.md)
> **Связанные области:** [[02-jvm-memory-gc]], [[03-collections]]

## Что это и зачем

Многопоточность позволяет выполнять несколько задач параллельно и эффективно использовать
многоядерные процессоры. Это одна из самых сложных и важных тем для Middle/Senior: нужно понимать
модель памяти, синхронизацию, проблемы конкурентного доступа (гонки данных, взаимоблокировки)
и высокоуровневые средства из `java.util.concurrent`. С Java 21 появились виртуальные потоки,
радикально упрощающие высоконагруженный конкурентный код.

Ошибки многопоточности крайне сложно воспроизводить и отлаживать: они могут проявляться
только под нагрузкой, на конкретном железе или при определённом планировщике потоков.
Правильная работа с concurrency требует понимания Java Memory Model (JMM) — спецификации того,
какие значения переменных видит каждый поток и в каком порядке.

## Ключевые подтемы

---

### Потоки: создание, жизненный цикл, прерывание

Поток (thread) — независимая нить выполнения внутри одного процесса. Все потоки разделяют
heap-память процесса, но каждый имеет собственный стек вызовов.

**Способы создания потока:**

```java
// 1. Наследование Thread
Thread t = new Thread() {
    @Override public void run() { System.out.println("hello"); }
};
t.start();

// 2. Через Runnable (предпочтительно — отделяет задачу от механизма)
Thread t2 = new Thread(() -> System.out.println("hello"));
t2.start();

// 3. Через ExecutorService (рекомендуется в production)
ExecutorService exec = Executors.newFixedThreadPool(4);
exec.submit(() -> System.out.println("hello"));
```

**Жизненный цикл потока** (перечисление `Thread.State`):

| Состояние | Описание |
|-----------|---------|
| `NEW` | Создан, `start()` ещё не вызван |
| `RUNNABLE` | Выполняется или готов к выполнению |
| `BLOCKED` | Ожидает монитор (synchronized) |
| `WAITING` | Ожидает бесконечно (`wait()`, `join()`) |
| `TIMED_WAITING` | Ожидает с таймаутом (`sleep()`, `wait(ms)`) |
| `TERMINATED` | Завершён |

**Прерывание (interruption):** механизм кооперативной остановки потока. Метод
`thread.interrupt()` выставляет флаг прерывания. Поток обязан проверять этот флаг сам:

```java
// Правильная обработка прерывания в цикле
while (!Thread.currentThread().isInterrupted()) {
    doWork();
}

// Блокирующие методы (sleep, wait, join) бросают InterruptedException
// и сбрасывают флаг — нужно либо перебросить, либо восстановить флаг
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt(); // восстанавливаем флаг
}
```

---

### Java Memory Model (JMM) и happens-before

JMM описана в [JLS §17.4](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html).
Это абстрактная спецификация: JVM и процессор могут переупорядочивать инструкции для оптимизации,
и JMM определяет, при каких условиях поток `B` гарантированно увидит запись, сделанную потоком `A`.

**Happens-before (hb):** если действие `x` *happens-before* `y`, то результат `x` виден `y`.
Отношение транзитивно: `hb(x,y)` и `hb(y,z)` => `hb(x,z)`.

**Источники happens-before (JLS §17.4.5):**

| Правило | Пояснение |
|---------|-----------|
| Program order | Внутри одного потока действия упорядочены по коду |
| Monitor unlock → lock | Разблокировка монитора hb следующей блокировке того же монитора |
| Volatile write → read | Запись volatile-поля hb любому последующему чтению того же поля |
| `Thread.start()` | Действия до `start()` hb любому действию в запущенном потоке |
| `Thread.join()` | Все действия потока hb успешному возврату из `join()` |
| Статическая инициализация | Завершение статических инициализаторов hb первому использованию класса |

**Гонка данных (data race):** два конфликтующих обращения к переменной (хотя бы одно — запись)
не упорядочены happens-before. Программа с гонками данных может вести себя непредсказуемо,
демонстрируя «из воздуха» взявшиеся значения.

**Пример незащищённого счётчика:**

```java
// Не потокобезопасно: нет happens-before между потоками
int counter = 0;

// Поток A: counter++;   (read + increment + write — три операции)
// Поток B: counter++;   (может прочитать старое значение)
```

---

### `volatile`: видимость и запрет переупорядочивания

`volatile` — облегчённый механизм синхронизации. Обеспечивает:
1. **Видимость:** запись в `volatile` поле немедленно видна всем потокам.
2. **Запрет переупорядочивания:** JVM не перемещает операции через барьер `volatile`.
3. **Атомарность** чтения/записи `long` и `double` (§17.7 JLS).

`volatile` **не** обеспечивает атомарность составных операций (например, `i++`).

```java
// Корректное использование — флаг остановки
private volatile boolean stopped = false;

// Некорректное использование — не атомарный инкремент
private volatile int counter = 0;
counter++; // Всё ещё race condition! Используйте AtomicInteger.
```

**Типичные применения `volatile`:**
- Флаги остановки/завершения
- Lazy-инициализация с double-checked locking (с осторожностью)
- Публикация неизменяемых объектов

---

### `synchronized`: мониторы и взаимное исключение

Каждый объект в Java имеет ассоциированный монитор. Ключевое слово `synchronized` позволяет
потоку захватить монитор: только один поток удерживает монитор в любой момент времени.

**Формы synchronized:**

```java
// 1. Синхронизированный метод экземпляра — монитор this
public synchronized void increment() {
    count++;
}

// 2. Статический синхронизированный метод — монитор Class-объекта
public static synchronized void register() { ... }

// 3. Синхронизированный блок — явно указанный монитор
public void transfer(Account target, int amount) {
    synchronized (this) {
        this.balance -= amount;
    }
    synchronized (target) {
        target.balance += amount;
    }
}
```

**Гарантии synchronized:**
- Взаимное исключение (только один поток в блоке).
- Happens-before: unlock hb следующему lock того же монитора.
- Видимость: при входе в `synchronized` поток видит все изменения, сделанные до предыдущего unlock.

**Реентерантность:** поток, уже удерживающий монитор, может повторно войти в любой
`synchronized`-блок на том же объекте без блокировки.

---

### Проблемы конкурентного доступа

**Deadlock (взаимоблокировка):** два или более потока ждут ресурсы, захваченные друг другом.
Четыре необходимых условия (условия Коффмана): взаимное исключение, удержание и ожидание,
отсутствие принудительного освобождения, циклическое ожидание.

```java
// Типичный deadlock — разный порядок захвата блокировок
// Поток 1: lock(A) -> lock(B)
// Поток 2: lock(B) -> lock(A)
// Решение: всегда захватывать блокировки в одном порядке
```

**Livelock:** потоки не блокированы, но постоянно реагируют на действия друг друга и не могут
продвинуться. Аналог двух людей в коридоре, постоянно уступающих дорогу.

**Starvation (голодание):** поток никогда не получает ресурс, потому что другие потоки
(возможно, с более высоким приоритетом) всегда опережают его.

**Race condition (гонка данных):** результат программы зависит от порядка планирования потоков.

---

### `java.util.concurrent.locks`: ReentrantLock и Condition

`ReentrantLock` ([API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html))
— явная реализация Lock с расширенными возможностями по сравнению с `synchronized`.

**Сравнение с synchronized:**

| Возможность | `synchronized` | `ReentrantLock` |
|-------------|---------------|-----------------|
| Справедливая блокировка | Нет | `new ReentrantLock(true)` |
| Попытка захвата без блокировки | Нет | `tryLock()` |
| Попытка с таймаутом | Нет | `tryLock(time, unit)` |
| Прерываемое ожидание | Нет | `lockInterruptibly()` |
| Несколько условий | Одно (wait/notify) | `newCondition()` |
| Автоматический unlock | Да | Нет — нужен `finally` |

```java
private final ReentrantLock lock = new ReentrantLock();
private final Condition notEmpty = lock.newCondition();

public void put(Object item) throws InterruptedException {
    lock.lock();
    try {
        while (queue.isEmpty()) {
            notEmpty.await();  // атомарно освобождает блокировку и ждёт
        }
        queue.add(item);
        notEmpty.signal();
    } finally {
        lock.unlock();  // обязателен в finally
    }
}
```

`ReentrantReadWriteLock` разрешает одновременное чтение нескольким потокам, но запись — только
одному (и только при отсутствии читателей).

---

### Атомарные классы и CAS

Пакет `java.util.concurrent.atomic` ([API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/package-summary.html))
предоставляет неблокирующие потокобезопасные операции на основе аппаратных инструкций CAS
(Compare-And-Swap).

**Основные классы:**

| Класс | Назначение |
|-------|-----------|
| `AtomicInteger`, `AtomicLong` | Атомарный счётчик |
| `AtomicBoolean` | Атомарный флаг |
| `AtomicReference<V>` | Атомарная ссылка на объект |
| `AtomicIntegerArray` | Атомарный массив int |
| `LongAdder`, `LongAccumulator` | Высококонкурентные аккумуляторы (Java 8+) |

**CAS (Compare-And-Swap):** атомарная операция — «если текущее значение равно expected,
замени его на update, иначе ничего не делай, верни false». Без блокировок, быстрее `synchronized`
при низкой конкуренции.

```java
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();          // атомарный i++
counter.compareAndSet(5, 10);       // если == 5, поставить 10

// ABA-проблема: используйте AtomicStampedReference если нужна защита
AtomicStampedReference<String> ref =
    new AtomicStampedReference<>("initial", 0);
```

`LongAdder` — более производительная альтернатива `AtomicLong` при высокой конкуренции:
внутренне сегментирует счётчик по ячейкам (striping), снижая конкуренцию.

---

### ExecutorService и пулы потоков

`ExecutorService` ([API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html))
отделяет управление потоками от бизнес-логики задач. Фабричные методы в классе `Executors`:

| Метод | Поведение |
|-------|-----------|
| `newFixedThreadPool(n)` | Фиксированный пул из n потоков |
| `newCachedThreadPool()` | Создаёт потоки по требованию, переиспользует свободные |
| `newSingleThreadExecutor()` | Один поток, последовательное выполнение задач |
| `newScheduledThreadPool(n)` | Поддержка отложенного и периодического запуска |
| `newVirtualThreadPerTaskExecutor()` | По одному виртуальному потоку на задачу (Java 21) |

```java
ExecutorService pool = Executors.newFixedThreadPool(4);

// submit возвращает Future — можно ждать результата
Future<Integer> future = pool.submit(() -> compute());
int result = future.get(); // блокирует до получения результата

// Корректное завершение пула
pool.shutdown();                         // перестаёт принимать задачи
pool.awaitTermination(10, TimeUnit.SECONDS); // ждёт выполнения очереди
```

**`ThreadPoolExecutor` напрямую** даёт полный контроль: размер core/max, keepAlive,
очередь задач (`LinkedBlockingQueue`, `ArrayBlockingQueue`, `SynchronousQueue`),
политика отказа (`RejectedExecutionHandler`).

---

### CompletableFuture: асинхронные цепочки

`CompletableFuture<T>` ([API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html))
— реализация `Future` с поддержкой функционального стиля и цепочек операций.

**Создание:**

```java
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> fetchData());
CompletableFuture<Void>   f2 = CompletableFuture.runAsync(() -> logEvent());
CompletableFuture<String> f3 = CompletableFuture.completedFuture("cached");
```

**Ключевые операции:**

| Метод | Аналог из Stream | Назначение |
|-------|-----------------|-----------|
| `thenApply(f)` | `map` | Преобразовать результат |
| `thenCompose(f)` | `flatMap` | Цепочка зависимых async-операций |
| `thenCombine(other, f)` | — | Объединить результаты двух futures |
| `exceptionally(f)` | — | Обработать исключение, вернуть fallback |
| `handle(f)` | — | Обработать результат или исключение |
| `allOf(fs...)` | — | Ждать все futures |
| `anyOf(fs...)` | — | Ждать первую завершившуюся |
| `orTimeout(t, u)` | — | Завершить исключительно по таймауту |

```java
// Цепочка с обработкой ошибки
CompletableFuture.supplyAsync(() -> fetchUser(id))
    .thenCompose(user -> fetchOrders(user.getId()))
    .thenApply(orders -> formatReport(orders))
    .exceptionally(ex -> "Error: " + ex.getMessage())
    .thenAccept(System.out::println);

// Параллельное выполнение
CompletableFuture<String> a = CompletableFuture.supplyAsync(() -> callServiceA());
CompletableFuture<String> b = CompletableFuture.supplyAsync(() -> callServiceB());
a.thenCombine(b, (ra, rb) -> ra + " " + rb).join();
```

По умолчанию `thenApplyAsync` / `supplyAsync` используют `ForkJoinPool.commonPool()`.
Для production рекомендуется передавать собственный `Executor`.

---

### Примитивы синхронизации

**`CountDownLatch`** — одноразовый барьер: потоки ждут, пока счётчик не достигнет нуля.
Нельзя сбросить после достижения нуля.

```java
CountDownLatch latch = new CountDownLatch(3);
// Три рабочих потока вызывают latch.countDown() после завершения
// Главный поток:
latch.await(); // блокируется до countDown x3
```

**`CyclicBarrier`** — многоразовый барьер: группа потоков ждут друг друга в точке
синхронизации. После прохождения барьер сбрасывается автоматически.

**`Semaphore`** — ограничивает количество потоков, одновременно выполняющих участок кода.
Классическое применение — ограничение числа одновременных подключений к ресурсу.

```java
Semaphore semaphore = new Semaphore(10); // не более 10 одновременно
semaphore.acquire();
try {
    accessResource();
} finally {
    semaphore.release();
}
```

**`Phaser`** (Java 7+) — гибкий аналог `CyclicBarrier` с динамическим числом участников
и поддержкой фаз. Подходит для поэтапных вычислений.

**`Exchanger<V>`** — позволяет двум потокам обменяться объектами в точке встречи.

---

### Fork/Join Framework

`ForkJoinPool` ([API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.html))
— специализированный пул для рекурсивных задач типа «разделяй и властвуй».
Использует **work-stealing**: свободные потоки забирают задачи из очередей занятых потоков.

```java
class SumTask extends RecursiveTask<Long> {
    private final long[] array;
    private final int lo, hi;

    @Override
    protected Long compute() {
        if (hi - lo <= THRESHOLD) {
            return sumDirectly(array, lo, hi);
        }
        int mid = (lo + hi) / 2;
        SumTask left  = new SumTask(array, lo, mid);
        SumTask right = new SumTask(array, mid, hi);
        left.fork();                      // асинхронно в пул
        return right.compute() + left.join(); // join ждёт left
    }
}

ForkJoinPool pool = ForkJoinPool.commonPool();
long sum = pool.invoke(new SumTask(data, 0, data.length));
```

---

### Виртуальные потоки (Project Loom, JEP 444, Java 21)

Виртуальные потоки ([JEP 444](https://openjdk.org/jeps/444)) — лёгкие потоки, управляемые JVM,
а не ОС. Маппируются на небольшое число платформенных потоков (carrier threads) из внутреннего
`ForkJoinPool`.

**Ключевые характеристики:**
- Создание дёшево (миллионы потоков — норма).
- При блокировании (I/O, `sleep`, `lock`) виртуальный поток отсоединяется от carrier-потока,
  не удерживая его.
- Всегда daemon-потоки с приоритетом `NORM_PRIORITY`.
- Поддерживают `ThreadLocal` (в Java 21 без ограничений).

```java
// Создание через Thread.ofVirtual()
Thread vt = Thread.ofVirtual().start(() -> System.out.println("virtual"));

// Через ExecutorService — рекомендуемый способ в production
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1_000_000; i++) {
        executor.submit(() -> handleRequest());
    }
}
```

**Pinning (прикалывание):** виртуальный поток прикрепляется к carrier и не может быть
вытеснен при нахождении внутри `synchronized`-блока или нативного кода. Это снижает
масштабируемость. Решение: заменить `synchronized` на `ReentrantLock` в горячих путях.
JEP 491 (Java 24) решает проблему пиннинга внутри `synchronized`.

**Structured Concurrency** ([JEP 453](https://openjdk.org/jeps/453), Preview в Java 21):
группирует несколько конкурентных задач в единый блок с управляемым временем жизни.

**Когда использовать виртуальные потоки:**
- Высоконагруженные серверы с I/O-bound задачами (REST API, JDBC, gRPC).
- Замена thread-per-request модели без изменения синхронного стиля кода.
- **Не** подходят для CPU-bound задач — там лучше `ForkJoinPool`.

---

### `final` поля и безопасная публикация

По JLS §17.5, после завершения конструктора все потоки гарантированно видят корректно
инициализированные `final` поля объекта — даже без дополнительной синхронизации.
Не-`final` поля такой гарантии не имеют.

```java
class SafePublished {
    final int x;        // гарантированно виден другим потокам
    int y;              // НЕ гарантирован без синхронизации

    SafePublished() { x = 42; y = 100; }
}
```

**Безопасная публикация** объекта: ссылка должна быть опубликована через volatile,
synchronized или через статический инициализатор класса, чтобы другие потоки увидели
полностью инициализированный объект.

---

### Неатомарность `long` и `double` (§17.7 JLS)

Запись/чтение `long` и `double` без `volatile` может быть разбита на две 32-битных
операции на 32-битных платформах. На 64-битных JVM HotSpot атомарность де-факто гарантирована,
но спецификация этого не требует. Для надёжности используйте `volatile long` или `AtomicLong`.

---

## Достоверные источники

1. **[The Java™ Tutorials — Concurrency](https://docs.oracle.com/javase/tutorial/essential/concurrency/index.html)**
   Официальный учебник Oracle, охватывает потоки, синхронизацию, java.util.concurrent.
   Достоверно: первичный официальный источник от Oracle.

2. **[JLS §17 — Threads and Locks](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)**
   Java Language Specification, глава 17: формальное определение Java Memory Model,
   happens-before, volatile, final-семантики, неатомарности long/double.
   Достоверно: нормативный стандарт языка.

3. **[java.util.concurrent — Package Summary (Java 21 API)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html)**
   Полный список классов и интерфейсов пакета с описаниями.
   Достоверно: официальный Javadoc Oracle.

4. **[JEP 444: Virtual Threads](https://openjdk.org/jeps/444)**
   Спецификация виртуальных потоков (Project Loom), вошедших в Java 21.
   Достоверно: официальный JEP от команды OpenJDK.

5. **[Jenkov — Java Concurrency and Multithreading Tutorial](https://jenkov.com/tutorials/java-concurrency/index.html)**
   Системный и подробный разбор всех аспектов конкурентности, включая JMM и lock-free.
   Достоверно: признанный авторитетный ресурс, регулярно обновляется.

6. **Книга «Java Concurrency in Practice» (Brian Goetz et al., 2006)**
   Канонический справочник по конкурентному программированию в Java.
   Достоверно: авторы — члены команды JSR-133 (Java Memory Model Expert Group).
