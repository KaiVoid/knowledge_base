# Многопоточность и concurrency — часть 2 из 4

> Вопросы 21–40 (в части: 20). Всего в разделе: 69.
> Область знаний: [../knowledge-base/04-concurrency.md](../knowledge-base/04-concurrency.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](concurrency-01.md) · **ч.2** · [ч.3](concurrency-03.md) · [ч.4](concurrency-04.md)

---
### Вопрос 21. Может ли возникнуть состояние гонки (race condition) при использовании volatile? Приведите конкретный пример.

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java Volatile Keyword — jenkov.com](https://jenkov.com/tutorials/java-concurrency/volatile.html)

Если поток должен сначала прочитать значение volatile-переменной, а затем на основе этого значения сформировать новое значение для той же общей volatile-переменной, то одного лишь `volatile` уже недостаточно для обеспечения корректной видимости. Короткий промежуток времени между чтением volatile-переменной и записью нового значения создаёт состояние гонки: несколько потоков могут прочитать одно и то же значение, вычислить одинаковое новое значение и при записи обратно в основную память — перезаписать результаты друг друга. Операции чтения и записи `volatile`-переменных являются атомарными, но составные операции типа «прочитать-изменить-записать» (read-modify-write) — нет.

#### Ответ от Claude

**Да, состояние гонки при `volatile` вполне возможно.** `volatile` гарантирует только видимость (visibility): запись одного потока сразу становится видна другим потокам через основную память. Но `volatile` не обеспечивает атомарность составных операций.

**Классический пример — счётчик с инкрементом:**

```java
public class Counter {
    private volatile int count = 0;

    public void increment() {
        count++; // НЕ атомарно! Три шага: read -> increment -> write
    }
}
```

Операция `count++` на уровне байт-кода разворачивается в три шага:
1. Читаем текущее значение `count` из памяти (например, `0`)
2. Увеличиваем на 1 (получаем `1`)
3. Записываем обратно в память

**Сценарий гонки:**
- Поток A читает `count = 0`
- Поток B читает `count = 0` (ещё до записи потока A)
- Поток A записывает `count = 1`
- Поток B записывает `count = 1` (перезаписывает результат потока A)

Итог: вместо `2` получаем `1`. Это классическое состояние гонки.

**Когда `volatile` достаточно:**
- Один поток пишет, остальные только читают
- Флаги завершения работы: `private volatile boolean running = true;`
- Одиночные независимые присваивания

**Решения для составных операций:**
- `synchronized`-блок: гарантирует атомарность всей операции
- `AtomicInteger.incrementAndGet()` из `java.util.concurrent.atomic` — lock-free атомарные операции
- `LongAdder` при высокой конкуренции — ещё лучше по производительности

**Ключевое правило:** `volatile` = видимость. Для атомарности составных операций нужна синхронизация или `Atomic`-классы.

---

### Вопрос 22. Что произойдёт, если поток бросит исключение внутри synchronized-блока — освободится ли монитор?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Intrinsic Locks and Synchronization — docs.oracle.com](https://docs.oracle.com/javase/tutorial/essential/concurrency/locksync.html)

Освобождение блокировки происходит даже в том случае, если выход из synchronized-блока был вызван необработанным исключением. Это поведение гарантируется механизмом синхронизации Java: внутренняя блокировка (intrinsic lock) всегда освобождается при выходе из synchronized-блока, независимо от того, был ли выход нормальным или аварийным.

#### Ответ от Claude

**Монитор освобождается всегда** — как при нормальном завершении блока, так и при выбрасывании исключения. Это жёстко гарантировано спецификацией JVM.

**Механизм на уровне байт-кода (JVM Specification, §6.5):**

Компилятор Java транслирует `synchronized`-блок в инструкции `monitorenter` / `monitorexit`. При этом генерируется не одна, а **две** инструкции `monitorexit`:
1. Для нормального выхода из блока
2. В блоке-обработчике исключений (`exception handler`) — на случай аварийного выхода

Из спецификации JVM: инструкция `athrow` (выброс исключения) при распространении исключения из `synchronized`-метода неявно выполняет `monitorexit`. Таким образом, выход из монитора при аварийном завершении обеспечивается механизмом обработки исключений JVM.

**Пример:**

```java
synchronized (lock) {
    doSomething();    // бросает RuntimeException
    // выход через исключение — монитор ВСЁ РАВНО освобождается
}
// здесь lock уже освобождён, другие потоки могут его захватить
```

В байт-коде это выглядит примерно так:
```
monitorenter
try {
    doSomething();
    monitorexit   // нормальный выход
} catch (Throwable t) {
    monitorexit   // аварийный выход
    athrow        // перебросить исключение дальше
}
```

**Сравнение с `ReentrantLock`:**

С явными блокировками (`Lock`) ситуация иная — там разработчик сам отвечает за освобождение в `finally`:

```java
lock.lock();
try {
    doSomething();
} finally {
    lock.unlock(); // ОБЯЗАТЕЛЬНО в finally, иначе deadlock
}
```

**Практический вывод:** `synchronized`-блоки безопасны с точки зрения освобождения монитора — `try-finally` для этой цели не нужен. Однако исключение продолжает распространяться вверх по стеку после освобождения монитора, поэтому вызывающий код всё равно должен его обработать.

---

### Вопрос 23. В чём разница между методами wait() / notify() и Condition.await() / signal() из ReentrantLock? Почему предпочтительнее использовать Condition?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Condition (Java SE 23 & JDK 23) — docs.oracle.com](https://docs.oracle.com/en/java/javase/23/docs/api/java.base/java/util/concurrent/locks/Condition.html)

`Condition` выделяет методы мониторинга объекта (`wait`, `notify`, `notifyAll`) в отдельные объекты, предоставляя эффект нескольких множеств ожидания (wait-sets) на один объект — за счёт сочетания с произвольными реализациями `Lock`. Там, где `Lock` заменяет использование `synchronized`-методов и операторов, `Condition` заменяет методы мониторинга объекта. Ключевое свойство: при ожидании на условии блокировка атомарно освобождается и текущий поток приостанавливается — точно так же, как `Object.wait`. Кроме того, `Condition` предоставляет богатый API: `awaitNanos(long)`, `awaitUntil(Date)`, `await(long, TimeUnit)` и `awaitUninterruptibly()` для неинтерпретируемого ожидания.

#### Ответ от Claude

**Сводная таблица различий:**

| Характеристика | `Object.wait/notify` | `Condition.await/signal` |
|---|---|---|
| Связь с блокировкой | Неявная (`synchronized`) | Явная (через `Lock.newCondition()`) |
| Множеств ожидания на объект | Одно | Несколько (по числу `Condition`) |
| Таймаут | `wait(long millis)` | `awaitNanos`, `await(time, unit)`, `awaitUntil(Date)` |
| Неинтерпретируемое ожидание | Нет | `awaitUninterruptibly()` |
| Пробуждение | `notify()` — случайный поток | `signal()` — первый в очереди |
| Пробуждение всех | `notifyAll()` | `signalAll()` |

**Ключевое преимущество — несколько множеств ожидания.**

С `Object.wait/notifyAll` все ждущие потоки находятся в одной очереди. При `notifyAll` просыпаются все — даже те, кто ждёт другого условия. Это порождает «эффект стада» (thundering herd).

`Condition` позволяет создать отдельные очереди для каждого условия:

```java
class BoundedBuffer<E> {
    final Lock lock = new ReentrantLock();
    final Condition notFull  = lock.newCondition(); // очередь производителей
    final Condition notEmpty = lock.newCondition(); // очередь потребителей

    public void put(E item) throws InterruptedException {
        lock.lock();
        try {
            while (count == capacity)
                notFull.await();        // ждёт только производитель
            buffer[putIndex] = item;
            count++;
            notEmpty.signal();          // будит только одного потребителя
        } finally {
            lock.unlock();
        }
    }

    public E take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0)
                notEmpty.await();       // ждёт только потребитель
            E item = buffer[takeIndex];
            count--;
            notFull.signal();           // будит только одного производителя
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

С `Object.wait/notifyAll` в аналогичном буфере каждый вызов `notifyAll` будил бы и производителей, и потребителей — всех сразу.

**Другие преимущества `Condition`:**

- **`awaitUninterruptibly()`** — поток не реагирует на прерывание во время ожидания, продолжает ждать сигнала
- **Точные тайм-ауты** — `awaitNanos(long)` возвращает остаток наносекунд, что позволяет строить точные петли ожидания без накопления погрешности
- **Интеграция с `ReentrantLock`** — честная (fair) политика пробуждения: потоки получают сигнал в порядке FIFO, в отличие от случайного выбора в `notify()`

**Когда оставаться на `wait/notify`:** только в очень простом коде с единственным условием и нет нужды в расширенных возможностях — исторически так было проще.

---

### Вопрос 24. Назовите четыре необходимых условия возникновения deadlock. Как их можно обнаружить и предотвратить программно?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Deadlock Prevention — jenkov.com](https://jenkov.com/tutorials/java-concurrency/deadlock-prevention.html)

Deadlock можно предотвратить тремя способами. **Упорядочивание блокировок (Lock Ordering):** если все потоки всегда захватывают блокировки в одном и том же порядке, deadlock не может возникнуть. **Тайм-аут блокировки (Lock Timeout):** поток пытается захватить блокировку в течение заданного времени; если не получается — откатывает все уже захваченные блокировки, ждёт случайное время и повторяет попытку. **Обнаружение deadlock (Deadlock Detection):** система ведёт граф захвата блокировок; когда поток получает отказ на захват, он обходит граф и проверяет наличие цикла. Java-классы `synchronized` не поддерживают тайм-аут — для этого нужен `java.util.concurrent.locks.Lock` с методом `tryLock`.

#### Ответ от Claude

**Четыре условия Коффмана (Coffman Conditions, 1971)** — все четыре должны выполняться одновременно:

1. **Mutual Exclusion (взаимное исключение)** — ресурс может удерживаться только одним потоком одновременно. Пока один поток держит блокировку, другой не может её захватить.

2. **Hold and Wait (удержание и ожидание)** — поток уже удерживает хотя бы один ресурс и при этом ожидает захвата другого ресурса, удерживаемого иным потоком.

3. **No Preemption (невытесняемость)** — ресурс не может быть принудительно отобран у потока; он освобождается только добровольно самим потоком.

4. **Circular Wait (циклическое ожидание)** — существует цепочка потоков T1 → T2 → ... → Tn → T1, где каждый поток ждёт ресурс, удерживаемый следующим.

**Классический пример deadlock:**

```java
Object lock1 = new Object();
Object lock2 = new Object();

// Поток A
synchronized (lock1) {
    synchronized (lock2) { /* ... */ }
}

// Поток B
synchronized (lock2) {        // захватывает в обратном порядке!
    synchronized (lock1) { /* ... */ }
}
```

**Предотвращение:**

**1. Lock Ordering — устраняет circular wait:**
```java
// Все потоки захватывают lock1 перед lock2 — всегда
synchronized (lock1) {
    synchronized (lock2) { /* ... */ }
}
```
Для динамически определяемого порядка используют `System.identityHashCode()`:
```java
if (System.identityHashCode(a) < System.identityHashCode(b)) {
    synchronized (a) { synchronized (b) { /* ... */ } }
} else {
    synchronized (b) { synchronized (a) { /* ... */ } }
}
```

**2. Lock Timeout — устраняет hold and wait / no preemption:**
```java
ReentrantLock lock1 = new ReentrantLock();
ReentrantLock lock2 = new ReentrantLock();

boolean acquired1 = lock1.tryLock(1, TimeUnit.SECONDS);
boolean acquired2 = false;
try {
    if (acquired1) {
        acquired2 = lock2.tryLock(1, TimeUnit.SECONDS);
    }
} finally {
    if (!acquired1 || !acquired2) {
        if (acquired1) lock1.unlock();
        if (acquired2) lock2.unlock();
        // пауза и повтор
    }
}
```
`synchronized`-блоки не поддерживают тайм-аут — нужен явный `Lock`.

**3. Deadlock Detection — обнаружение через граф:**

Ведётся граф «поток → блокировка → поток». При отказе в захвате поток обходит граф в поиске цикла. В случае обнаружения — откат с рандомной паузой или по приоритету. Это затратно, но применяется когда упорядочивание невозможно.

**Инструменты обнаружения в Java:**
- `ThreadMXBean.findDeadlockedThreads()` — находит потоки, заблокированные на `synchronized` или `ReentrantLock`
- `jstack <pid>` — дамп потоков с явным указанием deadlock
- VisualVM, JConsole — мониторинг в реальном времени

```java
ThreadMXBean tmx = ManagementFactory.getThreadMXBean();
long[] deadlockedIds = tmx.findDeadlockedThreads();
if (deadlockedIds != null) {
    ThreadInfo[] infos = tmx.getThreadInfo(deadlockedIds, true, true);
    // логировать и/или завершить зависшие потоки
}
```

**Практический совет:** наиболее надёжная стратегия — комбинировать Lock Ordering (для известных ресурсов) с `tryLock` тайм-аутами (для динамических сценариев).
### Вопрос 25. Чем livelock отличается от deadlock и от starvation? Приведите бытовой аналог и пример в коде.

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Starvation and Livelock — The Java™ Tutorials (docs.oracle.com)](https://docs.oracle.com/javase/tutorial/essential/concurrency/starvelive.html)

**Starvation** — ситуация, когда поток не может получить регулярный доступ к разделяемым ресурсам и не может продвигаться вперёд. Это происходит, когда «жадный» поток надолго занимает ресурс, не позволяя остальным потокам его получить.

**Livelock** — ситуация, когда поток реагирует на действие другого потока, а тот, в свою очередь, реагирует на действие первого. В отличие от дедлока, потоки в ливлоке не заблокированы — они активны, но слишком заняты реагированием друг на друга, чтобы выполнять реальную работу.

**Бытовой аналог (из документации Oracle)** — «Проблема коридора»: Алфонс и Гастон пытаются разойтись в узком коридоре. Алфонс делает шаг влево, Гастон — вправо, они снова стоят напротив друг друга. Алфонс делает шаг вправо, Гастон — влево, и снова оба заблокированы. Оба постоянно двигаются, но никто не проходит.

#### Ответ от Claude

**Три патологии конкурентности и их отличия:**

| Проблема | Состояние потоков | Прогресс | Ресурсы |
|----------|-------------------|----------|---------|
| **Deadlock** | Все заблокированы (BLOCKED/WAITING) | Отсутствует полностью | Удерживаются навсегда |
| **Livelock** | Активны (RUNNABLE) | Отсутствует, но потоки «работают» | Постоянно передаются/меняются |
| **Starvation** | Один/часть заблокированы, другие работают | Есть у «привилегированных» потоков | Монополизированы жадным потоком |

**Deadlock** — взаимная блокировка: поток A ждёт ресурс, захваченный потоком B, а поток B ждёт ресурс, захваченный потоком A. Оба стоят навсегда.

**Livelock** — активная взаимная блокировка: потоки не стоят, они постоянно меняют своё состояние в ответ на действия друг друга, но никогда не достигают прогресса.

**Starvation** — «голодание»: один или несколько потоков никогда не получают доступ к ресурсу, потому что другие («жадные» или высокоприоритетные) постоянно его перехватывают.

**Бытовые аналоги:**
- **Deadlock**: два человека крепко держат по одному инструменту и каждый ждёт, пока другой отдаст свой — никто не уступает.
- **Livelock**: два человека встречаются в дверях и одновременно уступают дорогу в одну сторону, затем в другую — бесконечно.
- **Starvation**: в столовой студент-отличник каждый раз пропускает всех вперёд — он так и не поест.

**Пример Deadlock:**
```java
public class DeadlockExample {
    private final Object lock1 = new Object();
    private final Object lock2 = new Object();

    public void methodA() {
        synchronized (lock1) {
            synchronized (lock2) { // поток A: сначала lock1, потом lock2
                System.out.println("methodA");
            }
        }
    }

    public void methodB() {
        synchronized (lock2) {
            synchronized (lock1) { // поток B: сначала lock2, потом lock1 — DEADLOCK!
                System.out.println("methodB");
            }
        }
    }
}
```

**Пример Livelock:**
```java
public class LivelockExample {
    static volatile boolean resourceTakenByA = false;
    static volatile boolean resourceTakenByB = false;

    public static void main(String[] args) {
        Thread threadA = new Thread(() -> {
            while (true) {
                resourceTakenByA = true;
                System.out.println("A: хочу ресурс");
                if (resourceTakenByB) {
                    System.out.println("A: уступаю B");
                    resourceTakenByA = false; // A отступает...
                    try { Thread.sleep(100); } catch (InterruptedException e) { break; }
                    continue; // ...и сразу пробует снова
                }
                System.out.println("A: использую ресурс");
                resourceTakenByA = false;
                break;
            }
        });

        Thread threadB = new Thread(() -> {
            while (true) {
                resourceTakenByB = true;
                System.out.println("B: хочу ресурс");
                if (resourceTakenByA) {
                    System.out.println("B: уступаю A");
                    resourceTakenByB = false; // B отступает...
                    try { Thread.sleep(100); } catch (InterruptedException e) { break; }
                    continue; // ...и сразу пробует снова
                }
                System.out.println("B: использую ресурс");
                resourceTakenByB = false;
                break;
            }
        });
        threadA.start();
        threadB.start();
        // Оба потока активны (не заблокированы), но не могут пройти вперёд
    }
}
```

**Пример Starvation:**
```java
// Поток с низким приоритетом голодает из-за высокоприоритетных потоков
public class StarvationExample {
    private static final Object lock = new Object();

    public static void main(String[] args) {
        // 5 высокоприоритетных потоков постоянно занимают lock
        for (int i = 0; i < 5; i++) {
            Thread high = new Thread(() -> {
                while (true) {
                    synchronized (lock) {
                        // долгая работа
                        try { Thread.sleep(50); } catch (InterruptedException e) { break; }
                    }
                }
            });
            high.setPriority(Thread.MAX_PRIORITY);
            high.setDaemon(true);
            high.start();
        }

        // Низкоприоритетный поток почти никогда не получает lock
        Thread low = new Thread(() -> {
            synchronized (lock) {
                System.out.println("Low-priority thread finally got the lock!");
            }
        });
        low.setPriority(Thread.MIN_PRIORITY);
        low.start();
    }
}
```

**Как устранить:**
- **Deadlock**: всегда захватывать блокировки в одном и том же порядке; использовать `tryLock()` с таймаутом.
- **Livelock**: вводить случайную задержку перед повторной попыткой (jitter), ограничивать число попыток.
- **Starvation**: использовать честные (`fair=true`) блокировки `ReentrantLock`, не злоупотреблять приоритетами потоков.

---

### Вопрос 26. Как работает ThreadLocal? Где хранятся его значения и почему ThreadLocal может вызвать утечку памяти в пуле потоков?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ThreadLocal Memory Leak in Java web application — Tomcat (javarevisited.blogspot.com)](https://javarevisited.blogspot.com/2013/01/threadlocal-memory-leak-in-java-web.html)

ThreadLocal использует специальную структуру `ThreadLocalMap` для хранения объектов, специфичных для потока. Ключи в этой карте — слабые ссылки (`WeakReference`) на объекты `ThreadLocal`, но **значения** хранятся через **сильные ссылки**. Эта асимметрия — корень проблемы.

Утечка памяти в Tomcat происходит потому, что жизненный цикл рабочих потоков пула длиннее жизненного цикла самого веб-приложения. Когда сервлет создаёт `ThreadLocal`-переменную и не удаляет её после обработки запроса, объект остаётся «привязан» к рабочему потоку. При перезапуске приложения ClassLoader старого веб-приложения не может быть собран сборщиком мусора, потому что активные потоки пула по-прежнему ссылаются на его объекты. После многократных передеплоев это приводит к `java.lang.OutOfMemoryError: PermGen space`.

**Решение** — вызывать `threadLocal.remove()` в блоке `finally` сервлетного фильтра после завершения обработки каждого запроса.

#### Ответ от Claude

**Как работает ThreadLocal:**

`ThreadLocal<T>` предоставляет каждому потоку собственную независимую копию переменной. Обращения к `get()` и `set()` всегда работают с копией текущего потока — без синхронизации между потоками.

**Где хранятся значения (внутренняя архитектура):**

Значения хранятся **внутри самого объекта `Thread`**, в поле `threadLocals` типа `ThreadLocal.ThreadLocalMap`. Структура хранения:

```
Thread
└── threadLocals: ThreadLocalMap
    └── Entry[] table
        └── Entry (WeakReference<ThreadLocal<?>> key → Object value)
```

- Ключ (`key`) — слабая ссылка (`WeakReference`) на объект `ThreadLocal`.
- Значение (`value`) — **сильная ссылка** на хранимый объект.

```java
// Упрощённая схема внутренней реализации
static class ThreadLocalMap {
    static class Entry extends WeakReference<ThreadLocal<?>> {
        Object value; // сильная ссылка на значение!
        Entry(ThreadLocal<?> k, Object v) {
            super(k); // ключ — WeakReference
            value = v;
        }
    }
    private Entry[] table;
}
```

**Почему возникает утечка памяти в пуле потоков:**

В обычном приложении, когда поток завершается, `ThreadLocalMap` уничтожается вместе с ним — утечки нет. Проблема возникает в **пуле потоков** (Tomcat, Spring, любой `ExecutorService`), где потоки **не завершаются**, а возвращаются в пул и переиспользуются снова и снова.

Механизм утечки:

1. Запрос 1 приходит → поток из пула устанавливает значение в `ThreadLocal`.
2. Обработка завершается, поток возвращается в пул, но `remove()` не вызван.
3. Запрос 2 приходит к тому же потоку → старое значение всё ещё живёт в `ThreadLocalMap`.
4. Если класс `ThreadLocal` сам был выгружен (например, при передеплое веб-приложения), его ключ стал `null` (WeakReference собрана GC), но **значение по-прежнему держится сильной ссылкой** из `Entry.value` — GC его не соберёт.
5. При многократных передеплоях объекты накапливаются → `OutOfMemoryError`.

```java
// ОПАСНО: ThreadLocal без cleanup в пуле потоков
private static final ThreadLocal<UserContext> userContext = new ThreadLocal<>();

// В обработчике запроса:
userContext.set(new UserContext(userId)); // устанавливаем
processRequest();
// Забыли вызвать userContext.remove() — утечка!
```

```java
// ПРАВИЛЬНО: всегда удалять в блоке finally
userContext.set(new UserContext(userId));
try {
    processRequest();
} finally {
    userContext.remove(); // обязательно!
}
```

**Почему WeakReference для ключа не спасает полностью:**

Слабая ссылка на `ThreadLocal` позволяет GC собрать сам объект `ThreadLocal`, если на него нет других сильных ссылок. После этого ключ в `Entry` становится `null`. Но `value` в той же `Entry` по-прежнему достижимо через цепочку: `Thread → threadLocals (ThreadLocalMap) → Entry[] → Entry.value`. GC не может собрать `value`, так как есть сильная ссылка. Более того, `ThreadLocalMap` при случайных операциях (`get`/`set`) пытается подчищать такие «осиротевшие» записи с `null`-ключами — но это происходит лишь инцидентально и ненадёжно.

**Итого — правила безопасного использования:**
- Всегда вызывать `remove()` в блоке `finally`.
- Предпочитать `InheritableThreadLocal` только при необходимости наследования в дочерних потоках.
- В Java 21+ рассмотреть `ScopedValue` как современную альтернативу.

---

### Вопрос 27. Чем Callable отличается от Runnable? Как получить результат и исключение из Future, не заблокировав основной поток навсегда?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java Callable and Future Tutorial — CalliCoder (callicoder.com)](https://www.callicoder.com/java-callable-and-future-tutorial/)

Основное отличие `Callable` от `Runnable`: «`Callable` похож на `Runnable`, за исключением того, что он может возвращать результат и выбрасывать проверяемое исключение».

В отличие от `Runnable`, `Callable` позволяет получать результат вычислений из потока через объект `Future`.

Чтобы не блокировать основной поток навсегда, нужно передавать таймаут в метод `get()`:
```java
future.get(1, TimeUnit.SECONDS);
```
Этот метод выбросит `TimeoutException`, если задача не завершится в течение заданного времени.

Также можно использовать метод `isDone()` для неблокирующей проверки готовности задачи — он возвращает `true`, если задача завершена (успешно, с исключением или была отменена). Для отмены задачи используется `cancel(true)`.

#### Ответ от Claude

**Ключевые отличия Callable от Runnable:**

| Характеристика | Runnable | Callable\<V\> |
|----------------|----------|--------------|
| Метод | `void run()` | `V call() throws Exception` |
| Возврат значения | Нет | Да, произвольный тип `V` |
| Проверяемые исключения | Нельзя пробросить, только поймать внутри | Можно пробросить (`throws Exception`) |
| Запуск через `Thread` | Да | Нет (только через `ExecutorService`) |
| Запуск через `ExecutorService.submit()` | Да (`Future<?>`) | Да (`Future<V>`) |

```java
// Runnable — нет результата, нет checked exceptions
Runnable r = () -> System.out.println("fire and forget");

// Callable — есть результат, можно пробрасывать исключения
Callable<Integer> c = () -> {
    // можно throws IOException, SQLException и т.д.
    return 42;
};
```

**Как получить результат из Future:**

`ExecutorService.submit(callable)` возвращает `Future<V>`. Основные способы работы с ним:

```java
ExecutorService executor = Executors.newSingleThreadExecutor();
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(2000);
    return 42;
});

// 1. Блокирующий get() — ОПАСНО, может заблокировать навсегда
// int result = future.get(); // ждёт бесконечно

// 2. get() с таймаутом — ПРАВИЛЬНО
try {
    int result = future.get(3, TimeUnit.SECONDS); // ждёт не более 3 секунд
    System.out.println("Результат: " + result);
} catch (TimeoutException e) {
    System.err.println("Задача не завершилась за 3 секунды");
    future.cancel(true); // отменяем задачу
} catch (ExecutionException e) {
    // исключение из call() оборачивается в ExecutionException
    System.err.println("Задача завершилась с исключением: " + e.getCause());
} catch (InterruptedException e) {
    Thread.currentThread().interrupt(); // восстанавливаем флаг прерывания
}

// 3. Неблокирующая проверка через isDone()
if (future.isDone()) {
    try {
        int result = future.get(); // безопасно — задача уже завершена
    } catch (ExecutionException | InterruptedException e) {
        // обрабатываем
    }
}

executor.shutdown();
```

**Как обрабатываются исключения из Callable:**

Если `call()` выбросил исключение, оно «хранится» внутри `Future`. При вызове `future.get()` оно оборачивается в `ExecutionException`. Если `get()` не вызвать — исключение будет **потеряно молча**.

```java
Future<Integer> failingFuture = executor.submit(() -> {
    throw new RuntimeException("что-то пошло не так");
});

try {
    failingFuture.get(1, TimeUnit.SECONDS);
} catch (ExecutionException e) {
    Throwable cause = e.getCause(); // оригинальное исключение из call()
    System.err.println("Причина: " + cause.getMessage());
}
```

**Стратегии избежать вечной блокировки:**

1. **`get(timeout, unit)`** — главный инструмент. Всегда указывать разумный таймаут.
2. **Polling через `isDone()`** — неблокирующая проверка в цикле с паузой.
3. **`CompletableFuture`** — если нужна реактивная обработка без блокировок (callback-подход через `thenApply`, `exceptionally` и т.д.).
4. **`invokeAll()` с таймаутом** — для пакетного выполнения нескольких `Callable`.

```java
// Современный подход через CompletableFuture — без блокировок
CompletableFuture.supplyAsync(() -> computeResult())
    .orTimeout(3, TimeUnit.SECONDS)      // Java 9+: не блокирует, а завершает future
    .thenAccept(result -> System.out.println("Готово: " + result))
    .exceptionally(e -> { System.err.println("Ошибка: " + e); return null; });
```

---

### Вопрос 28. В чём разница между thenApply(), thenCompose() и thenCombine() в CompletableFuture? Когда каждый из них уместен?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CompletableFuture in Java: Understanding thenApply and thenCompose — codestudy.net](https://www.codestudy.net/blog/completablefuture-thenapply-vs-thencompose/)

**thenApply** — синхронная трансформация результата:
```java
CompletableFuture<Integer> squaredFuture = fetchNumberFuture
    .thenApply(number -> number * number);
```
«Метод `thenApply` используется для **трансформации результата** завершённого `CompletableFuture` с помощью синхронной функции.»

**thenCompose** — композиция зависимых асинхронных операций:
```java
CompletableFuture<List<Order>> userOrdersFuture = fetchUserById("123")
    .thenCompose(user -> fetchOrdersForUser(user));
```
«Метод `thenCompose` используется для **компоновки двух зависимых асинхронных операций**.»

Ключевое различие: `thenApply` принимает `Function<T, R>`, а `thenCompose` — `Function<T, CompletableFuture<R>>`. При использовании `thenApply` для асинхронной операции получится вложенный `CompletableFuture<CompletableFuture<R>>`, тогда как `thenCompose` автоматически «разворачивает» вложенность (аналог `flatMap`).

#### Ответ от Claude

**Три метода цепочки в CompletableFuture:**

Аналогия со Stream API помогает запомнить:
- `thenApply` → как `Stream.map()` — синхронная трансформация значения.
- `thenCompose` → как `Stream.flatMap()` — «разворачивает» вложенный `CompletableFuture`.
- `thenCombine` → объединяет результаты двух **независимых** `CompletableFuture`.

**thenApply — синхронная трансформация (map):**

Принимает `Function<T, R>`. Функция выполняется в том же потоке, что завершил предыдущий этап. Возвращает `CompletableFuture<R>`.

```java
CompletableFuture<String> nameFuture = CompletableFuture.supplyAsync(() -> "  alice  ");

CompletableFuture<String> upperFuture = nameFuture
    .thenApply(String::trim)
    .thenApply(String::toUpperCase);
// Результат: "ALICE"

// ЛОВУШКА: если функция сама возвращает CompletableFuture — получим нежелательную вложенность
CompletableFuture<CompletableFuture<String>> WRONG = nameFuture
    .thenApply(name -> fetchProfileAsync(name)); // CompletableFuture<CompletableFuture<String>>!
```

**Уместен, когда:** функция трансформации простая и синхронная (парсинг, форматирование, математика).

**thenCompose — асинхронная цепочка (flatMap):**

Принимает `Function<T, CompletableFuture<R>>`. «Разворачивает» вложенный Future, возвращая `CompletableFuture<R>` напрямую. Это и есть главное отличие от `thenApply`.

```java
CompletableFuture<User> userFuture = CompletableFuture
    .supplyAsync(() -> "user123")       // CF<String>
    .thenCompose(id -> fetchUser(id));  // fetchUser возвращает CF<User>
                                        // результат: CF<User>, а не CF<CF<User>>

// Цепочка зависимых асинхронных вызовов:
CompletableFuture<Order> orderFuture = fetchUser(userId)
    .thenCompose(user -> fetchCart(user.getCartId()))
    .thenCompose(cart -> createOrder(cart));
```

**Уместен, когда:** следующий шаг сам является асинхронной операцией, которая возвращает `CompletableFuture` (вызов сервиса, запрос к БД, обращение к API).

**thenCombine — объединение двух независимых Future:**

Принимает второй `CompletableFuture<U>` и `BiFunction<T, U, V>`. Оба future выполняются **параллельно и независимо**; когда оба завершены — результаты объединяются через `BiFunction`.

```java
CompletableFuture<User> userFuture = fetchUserAsync(userId);
CompletableFuture<List<Product>> productsFuture = fetchProductsAsync();

// Оба запроса выполняются параллельно
CompletableFuture<Page> pageFuture = userFuture.thenCombine(
    productsFuture,
    (user, products) -> new Page(user, products)
);
```

**Уместен, когда:** нужно параллельно выполнить два независимых асинхронных вычисления и объединить их результаты. Если независимых futures больше двух — используется `CompletableFuture.allOf()`.

**Сравнительная таблица:**

| Метод | Тип функции | Зависимость | Аналог в Stream | Типичный сценарий |
|-------|-------------|-------------|-----------------|-------------------|
| `thenApply(f)` | `Function<T,R>` | Последовательная | `map` | Трансформация данных (парсинг, форматирование) |
| `thenCompose(f)` | `Function<T,CF<R>>` | Последовательная, зависимая | `flatMap` | Цепочка async-вызовов (user → orders → payment) |
| `thenCombine(cf, f)` | `BiFunction<T,U,V>` | Параллельная, независимая | zip (нет прямого) | Параллельные запросы с объединением результатов |

**Обе асинхронные версии:** каждый метод имеет пару `...Async(f, executor)`, которая явно задаёт пул потоков для выполнения функции, а не использует поток завершения предыдущего этапа.

```java
// Принудительно выполняем thenApply в кастомном пуле
CompletableFuture<String> result = future
    .thenApplyAsync(data -> heavyTransform(data), myExecutorService);
```

---
### Вопрос 29. Как CompletableFuture обрабатывает исключения? Чем exceptionally() отличается от handle() и whenComplete()?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [CompletableFuture (Java SE 21 & JDK 21) — docs.oracle.com](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html)

`exceptionally(Function<Throwable, ? extends T> fn)` — возвращает новый `CompletableFuture`, который завершается с тем же значением, что и исходный, если он завершился нормально. Если же исходный завершился с исключением, то переданная функция вызывается с этим исключением и возвращает восстановительное значение типа `T`. Таким образом, метод срабатывает **только** при наличии исключения.

`handle(BiFunction<? super T, Throwable, ? extends U> fn)` — возвращает новый `CompletableFuture<U>`, который **всегда** выполняет переданную функцию — и при нормальном завершении, и при исключении. Функция получает два параметра: результат (или `null`, если было исключение) и исключение (или `null`, если завершилось нормально). Позволяет менять тип результата (`U` может отличаться от `T`).

`whenComplete(BiConsumer<? super T, ? super Throwable> action)` — возвращает новый `CompletableFuture` с тем же типом и результатом, что и исходный. Выполняется **всегда**, но принимает `BiConsumer`, а не функцию — то есть не может преобразовать результат. Используется для побочных эффектов (логирование, метрики). Если сам `action` бросит исключение и исходный future завершился нормально, то новый future завершится с исключением из `action`.

#### Ответ от Claude

**Как CompletableFuture хранит исключения**

Когда задача завершается с исключением, `CompletableFuture` оборачивает его в `CompletionException` (если это ещё не `CompletionException`) и сохраняет как результат. Вызов `get()` на таком future выбрасывает `ExecutionException`, а `join()` — `CompletionException`. Исключение распространяется по цепочке `thenApply` / `thenCompose` вниз, минуя все трансформирующие стадии, до первого обработчика.

**Сравнение трёх методов**

| Критерий | `exceptionally()` | `handle()` | `whenComplete()` |
|---|---|---|---|
| Когда срабатывает | Только при исключении | Всегда | Всегда |
| Тип callback | `Function<Throwable, T>` | `BiFunction<T, Throwable, U>` | `BiConsumer<T, Throwable>` |
| Может изменить тип результата | Нет (только `T → T`) | Да (`T → U`) | Нет |
| Может изменить значение | Да (recovery value) | Да (оба пути) | Нет (side-effects only) |
| Результат при нормальном завершении | Проходит насквозь | Определяется функцией | Проходит насквозь |

**exceptionally()** — аналог блока `catch`: вызывается только тогда, когда что-то пошло не так, и должен вернуть «запасное» значение того же типа.

```java
CompletableFuture<String> result = fetchData()
    .exceptionally(ex -> "default-value"); // только при исключении
```

**handle()** — аналог `try-catch` с возможностью преобразования: позволяет обработать и успех, и ошибку в одном месте, а также изменить тип результата. Важная особенность: если в цепочке уже стоит `handle()`, то расположенный после него `exceptionally()` не получит исходное исключение, поскольку `handle()` его уже «поглотил».

```java
CompletableFuture<Integer> result = fetchString()
    .handle((value, ex) -> {
        if (ex != null) return -1;           // обработка ошибки
        return Integer.parseInt(value);       // трансформация успеха
    });
```

**whenComplete()** — аналог `finally`: не меняет ни результат, ни исключение, используется для логирования, метрик и других побочных эффектов. Если `action` сам выбросит исключение, а исходный future завершился нормально — downstream получит исключение из `action`. Если же исходный future уже завершился с исключением — исключение из `action` подавляется (исходное сохраняется).

```java
CompletableFuture<String> result = fetchData()
    .whenComplete((value, ex) -> {
        if (ex != null) log.error("Failed", ex);
        else metrics.increment("success");
    }); // результат или исключение проходят дальше без изменений
```

**Ключевое правило выбора:** используйте `exceptionally()` для recovery (возврат значения по умолчанию), `handle()` для унифицированной трансформации (в том числе смены типа), `whenComplete()` только для наблюдения без изменения цепочки.

---

### Вопрос 30. Как устроен AbstractQueuedSynchronizer (AQS) внутри? Как на его основе реализованы ReentrantLock и Semaphore?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [AbstractQueuedSynchronizer (Java SE 21 & JDK 21) — docs.oracle.com](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.html)

`AbstractQueuedSynchronizer` — фреймворк для реализации блокирующих блокировок и связанных синхронизаторов (семафоры, события и т. д.), опирающихся на FIFO-очереди ожидания. Предназначен для большинства синхронизаторов, которые полагаются на единственное атомарное `int`-значение для представления состояния.

Подклассы должны определять защищённые методы, изменяющие это состояние: `tryAcquire(int)`, `tryRelease(int)`, `tryAcquireShared(int)`, `tryReleaseShared(int)`. Остальная инфраструктура (постановка в очередь, парковка/распарковка потоков) реализована в самом AQS.

Захват работает так: вызывается хотя бы один раз `tryAcquire(int)`, при успехе захват завершён; иначе поток помещается в очередь и блокируется до тех пор, пока `tryAcquire` не вернёт `true`. Именно на этой основе построены `ReentrantLock`, `Semaphore`, `CountDownLatch`, `ReentrantReadWriteLock` и `SynchronousQueue`.

#### Ответ от Claude

**Структура AQS**

AQS хранит два ключевых поля:

1. **`volatile int state`** — атомарно управляемое целое число; его смысл определяет подкласс:
   - В `ReentrantLock`: `0` — свободно, `N > 0` — захвачено N раз (реентерабельность).
   - В `Semaphore`: количество оставшихся разрешений.
   - В `CountDownLatch`: начальный счётчик.

2. **CLH-очередь (Craig, Landin, and Hagersten)** — двусвязный список узлов `Node`. Каждый `Node` содержит ссылку на поток, статус ожидания (`CANCELLED`, `SIGNAL`, `CONDITION`, `PROPAGATE`) и ссылки на prev/next. Очередь FIFO: голова (head) — фиктивный sentinel-узел; хвост (tail) — последний добавленный.

**Алгоритм захвата (эксклюзивный режим)**

```
acquire(arg):
  if (!tryAcquire(arg)):          // подкласс пробует получить ресурс
    node = enqueue(thread)        // добавить в конец CLH-очереди
    loop:
      if node.prev == head and tryAcquire(arg):
        setHead(node)             // стать новой головой
        return
      LockSupport.park(thread)   // заблокировать поток
```

Парковка (`LockSupport.park`) используется вместо `Object.wait`, что позволяет точечно разбудить конкретный поток без монитора.

**Освобождение (эксклюзивный режим)**

```
release(arg):
  if tryRelease(arg):
    LockSupport.unpark(head.next.thread) // разбудить первый ожидающий поток
```

**Эксклюзивный vs. Разделяемый режим**

- **Exclusive** (`tryAcquire` / `tryRelease`): ресурс может держать только один поток — `ReentrantLock`.
- **Shared** (`tryAcquireShared` / `tryReleaseShared`): несколько потоков могут держать ресурс одновременно — `Semaphore`, `CountDownLatch`. После успешного `releaseShared` может запускаться каскадное пробуждение нескольких ожидающих потоков.

**Как ReentrantLock использует AQS**

`ReentrantLock` содержит внутренний класс `Sync extends AQS`. Реализует два варианта: `NonfairSync` и `FairSync`.

```java
// Упрощённая нечестная реализация
protected boolean tryAcquire(int acquires) {
    int c = getState();
    if (c == 0) {
        // Нет очереди: пробуем захватить напрямую (barging)
        if (compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(currentThread());
            return true;
        }
    } else if (currentThread() == getExclusiveOwnerThread()) {
        // Реентерабельность: увеличиваем счётчик
        setState(c + acquires);
        return true;
    }
    return false;
}

protected boolean tryRelease(int releases) {
    int c = getState() - releases;
    if (currentThread() != getExclusiveOwnerThread())
        throw new IllegalMonitorStateException();
    if (c == 0) setExclusiveOwnerThread(null);
    setState(c);
    return c == 0; // true = полностью освобождено
}
```

`FairSync` отличается тем, что в начале `tryAcquire` проверяет `hasQueuedPredecessors()` — не даёт новому потоку «перепрыгнуть» очередь.

**Как Semaphore использует AQS**

`Semaphore` использует разделяемый режим: `state` = количество разрешений.

```java
protected int tryAcquireShared(int acquires) {
    for (;;) {
        int available = getState();
        int remaining = available - acquires;
        if (remaining < 0 ||
            compareAndSetState(available, remaining))
            return remaining; // < 0 означает "нет разрешений, ждать"
    }
}

protected boolean tryReleaseShared(int releases) {
    for (;;) {
        int current = getState();
        int next = current + releases;
        if (compareAndSetState(current, next))
            return true;
    }
}
```

Если `tryAcquireShared` вернула отрицательное значение — поток встаёт в очередь. После `releaseShared` AQS может последовательно разбудить несколько ожидающих потоков (propagate wake-up).

**Ключевые преимущества AQS**

- Вся сложность (очередь, парковка, CAS) сосредоточена в одном месте; подкласс реализует лишь бизнес-логику в 2–5 методах.
- Встроенная поддержка `Condition` (`ConditionObject`) для эксклюзивных блокировок.
- Поддержка как честного (FIFO), так и нечестного (barging) режима захвата.
- Методы мониторинга: `hasQueuedThreads()`, `getQueueLength()`, `getQueuedThreads()`.

---

### Вопрос 31. Чем StampedLock отличается от ReentrantReadWriteLock? Что такое оптимистичное чтение и почему StampedLock не является реентерабельным?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [StampedLock (Java SE 17 & JDK 17) — docs.oracle.com](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/locks/StampedLock.html)

`StampedLock` — блокировка на основе «штампов» (capability-based lock), появившаяся в Java 8. Поддерживает три режима:

1. **Writing** — эксклюзивный доступ; при захвате все оптимистичные читатели получают неверный штамп.
2. **Reading** — неэксклюзивный; несколько читателей могут держать блокировку одновременно.
3. **Optimistic Reading** (`tryOptimisticRead()`) — сверхлёгкая операция, не требующая захвата блокировки. Возвращает штамп, который затем нужно проверить через `validate(stamp)`. Если за это время никто не делал записи, данные согласованы.

Из документации: «They are not reentrant, so locked bodies should not call other unknown methods that may try to re-acquire locks.» StampedLocks не отслеживают, какой поток держит блокировку: «Unlike Semaphore... StampedLocks have no notion of ownership. Locks acquired in one thread can be released or converted in another.»

#### Ответ от Claude

**Три режима StampedLock**

```java
StampedLock sl = new StampedLock();

// Запись (эксклюзивно)
long stamp = sl.writeLock();
try { /* изменяем данные */ }
finally { sl.unlockWrite(stamp); }

// Чтение (разделяемое)
long stamp = sl.readLock();
try { /* читаем данные */ }
finally { sl.unlockRead(stamp); }

// Оптимистичное чтение (без захвата блокировки)
long stamp = sl.tryOptimisticRead();
double x = this.x, y = this.y;   // читаем поля
if (!sl.validate(stamp)) {        // проверяем: была ли запись?
    stamp = sl.readLock();        // откат к полноценному readLock
    try { x = this.x; y = this.y; }
    finally { sl.unlockRead(stamp); }
}
return Math.sqrt(x*x + y*y);
```

**Что такое оптимистичное чтение**

`tryOptimisticRead()` возвращает штамп немедленно, не блокируя поток и не захватывая никакой блокировки. Идея: в подавляющем большинстве случаев записей нет, поэтому можно читать данные «оптимистично» и затем быстро проверить, не была ли произведена запись за время чтения. Если `validate(stamp)` возвращает `false` — читатель обязан повторить чтение под полноценным `readLock`. Это устраняет накладные расходы на захват/освобождение блокировки при отсутствии записей.

Критически важно: между `tryOptimisticRead()` и `validate()` данные могут быть частично перезаписаны другим потоком — они могут быть **несогласованными**. Нельзя вызывать методы, которые полагаются на корректность прочитанных данных, до успешной валидации.

**Сравнение с ReentrantReadWriteLock**

| Характеристика | StampedLock | ReentrantReadWriteLock |
|---|---|---|
| Оптимистичное чтение | Да | Нет |
| Реентерабельность | Нет | Да |
| Отслеживание владельца | Нет | Да |
| Поддержка `Condition` | Нет | Да (`newCondition()`) |
| Конвертация режимов | Да (`tryConvertToWriteLock`) | Ограниченно |
| Голодание читателей | Меньше (нет fairness guarantee) | Есть при большом числе читателей |
| Голодание писателей | Реализована защита | Есть в нечестном режиме |
| Интерфейсы | Нет `Lock`/`ReadWriteLock` | Реализует `ReadWriteLock` |

`ReentrantReadWriteLock` страдает от starvation writers при непрерывном потоке читателей (режим по умолчанию — нечестный). `StampedLock` решает эту проблему иначе.

**Почему StampedLock не реентерабелен**

Реентерабельность требует, чтобы блокировка знала: «текущий поток уже держит меня». Для этого нужно хранить идентификатор потока-владельца и счётчик вложенности. `StampedLock` намеренно отказался от отслеживания владельца:

1. **Stamp-based design**: штамп — это просто `long`, версия состояния блокировки. В нём нет информации о том, какой поток его получил. Поэтому невозможно обнаружить попытку повторного захвата тем же потоком.

2. **Передача штампов между потоками**: документация явно разрешает освобождать блокировку из другого потока (`Locks acquired in one thread can be released or converted in another`). Это исключает семантику «владения».

3. **Целевое назначение — внутренние утилиты**: StampedLock проектировался для компонентов, где разработчик полностью контролирует код в критической секции и не вызывает из неё методов, способных снова запросить ту же блокировку.

Попытка повторного захвата — **дедлок**:

```java
long s1 = lock.writeLock();
long s2 = lock.writeLock(); // ДЕДЛОК: тот же поток блокируется навсегда
```

Если требуется реентерабельность — используйте `ReentrantReadWriteLock`.

---

### Вопрос 32. Как работает алгоритм work-stealing в ForkJoinPool? Почему он эффективнее обычного ThreadPoolExecutor для рекурсивных задач?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [ForkJoinPool (Java Platform SE 8) — docs.oracle.com](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ForkJoinPool.html)

`ForkJoinPool` отличается от других реализаций `ExecutorService` тем, что использует **алгоритм work-stealing**: все потоки пула пытаются найти и выполнить задачи, отправленные в пул или порождённые активными задачами (в конечном счёте блокируясь в ожидании работы, если её нет).

Каждый рабочий поток ведёт собственную двустороннюю очередь (deque) задач. Хозяин очереди работает с её **вершиной** (LIFO), а похититель крадёт с **хвоста** (FIFO). Это снижает конкуренцию: два потока работают с разными концами очереди.

Параметр `asyncMode = true` меняет порядок для собственных задач потока на FIFO — полезно для event-style задач без `join`.

Настройка пула по умолчанию: `java.util.concurrent.ForkJoinPool.common.parallelism` (по умолчанию равно числу процессоров минус 1).

#### Ответ от Claude

**Проблема ThreadPoolExecutor для рекурсивных задач**

`ThreadPoolExecutor` использует **одну разделяемую очередь** задач. При рекурсивном делении (divide-and-conquer) количество задач растёт экспоненциально — все потоки конкурируют за одну и ту же очередь, что создаёт высокий уровень синхронизации и накладные расходы на захват блокировок. Помимо этого, поток, выполняющий `join()`, блокируется, ничем не занимаясь, пока ждёт завершения подзадач.

**Архитектура ForkJoinPool**

Каждый рабочий поток (`ForkJoinWorkerThread`) имеет свою **deque (двустороннюю очередь)** задач типа `WorkQueue`. Никакой общей очереди — каждый поток работает преимущественно со своей очередью.

```
Поток 1 (занят)         Поток 2 (занят)         Поток 3 (свободен)
┌──────────────────┐    ┌──────────────────┐
│ [T1.1][T1.2][T1.3]│   │ [T2.1][T2.2]     │
└──────────────────┘    └──────────────────┘
  ↑ LIFO (owner)          ↑ LIFO (owner)        ↑ крадёт T2.2 (FIFO)
  добавляет/берёт         добавляет/берёт        с хвоста очереди Потока 2
  с вершины               с вершины
```

**Алгоритм work-stealing**

1. **Fork**: когда задача форкает подзадачи (`task.fork()`), они помещаются в **вершину** собственной deque текущего потока (LIFO).
2. **Join**: поток продолжает работать — он забирает задачи из **вершины** своей deque (LIFO), пока ждёт `join()`. Это называется *task helping* (помощь себе же).
3. **Stealing**: когда поток исчерпал свою deque, он случайно выбирает другой поток и крадёт задачу с **хвоста** чужой очереди (FIFO). Задач с хвоста — более крупные, созданные раньше; выполнение крупных задач позволит «похитителю» сгенерировать новые подзадачи.

**Почему LIFO у хозяина и FIFO у похитителя**

- **LIFO у хозяина** → обеспечивает кэш-локальность: недавно форкнутые задачи с большей вероятностью имеют «горячие» данные в кэше процессора.
- **FIFO у похитителя** → кражи с хвоста (старые, крупные задачи) минимизируют конкуренцию между хозяином и похитителем (они работают с разными концами очереди). Крупная задача при разбивке даст похитителю много новой работы.

**Compensation (компенсация потоков)**

Если поток заблокирован в `join()` и нечем помочь, ForkJoinPool может создать **compensation thread** — временный дополнительный поток, чтобы не терять параллелизм. Это предотвращает дедлок при глубокой рекурсии.

**Почему ForkJoinPool эффективнее для рекурсивных задач**

| Критерий | ThreadPoolExecutor | ForkJoinPool |
|---|---|---|
| Очередь | Одна разделяемая | Per-thread deque |
| Конкуренция за очередь | Высокая | Минимальная (разные концы) |
| Поведение при `join()` | Блокировка потока | Task helping + work-stealing |
| Кэш-локальность | Слабая | Высокая (LIFO у хозяина) |
| Простой поток | Ждёт | Крадёт задачи |
| Масштабируемость для divide-and-conquer | Плохая | Отличная |

**Пример: сортировка слиянием**

```java
class MergeSort extends RecursiveAction {
    protected void compute() {
        if (size <= THRESHOLD) {
            Arrays.sort(data, lo, hi); // базовый случай
            return;
        }
        int mid = (lo + hi) / 2;
        MergeSort left  = new MergeSort(data, lo, mid);
        MergeSort right = new MergeSort(data, mid, hi);
        left.fork();          // добавляется в вершину deque (LIFO)
        right.compute();      // выполняется сразу этим же потоком
        left.join();          // если left не готов — поток помогает другим задачам
        merge(lo, mid, hi);
    }
}
ForkJoinPool pool = new ForkJoinPool();
pool.invoke(new MergeSort(data, 0, data.length));
```

`Arrays.parallelSort()`, параллельные стримы (`Stream.parallel()`) и `CompletableFuture` без указания `Executor` — все используют `ForkJoinPool.commonPool()` внутри.
### Вопрос 33. Что такое виртуальные потоки (Project Loom, JDK 21+)? Что значит «pinning» виртуального потока к carrier-потоку и в каких случаях он возникает?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Virtual Thread Deep Dive — Inside Java Newscast #23 // nipafx.dev](https://nipafx.dev/inside-java-newscast-23/)

Виртуальный поток — экземпляр `java.lang.Thread`, которому для работы с CPU нужен OS-поток, но не тогда, когда он ожидает других ресурсов. JDK назначает виртуальные потоки на carrier-потоки через процесс монтирования и снимает через размонтирование. С точки зрения Java-кода это разделение невидимо: стек-трейсы и thread-local переменные полностью изолированы.

Пиннинг возникает когда виртуальный поток выполняет нативные методы, foreign-функции или код внутри `synchronized`-блоков/методов — в этих ситуациях виртуальный поток прикрепляется к своему carrier-потоку и не размонтируется там, где в ином случае он мог бы. Последствия: OS-поток заблокирован и не может обслуживать другие виртуальные потоки; масштабируемость снижается; дополнительный платформенный поток для компенсации не создаётся. Для минимизации пиннинга рекомендуется заменять `synchronized`-блоки на `ReentrantLock` в критичных секциях с I/O-операциями.

#### Ответ от Claude

**Что такое виртуальные потоки (Project Loom)**

Project Loom — проект OpenJDK, реализовавший виртуальные потоки в JDK 19 (preview) и финализировавший их в JDK 21 через JEP 444. Виртуальные потоки — это лёгковесные потоки, управляемые JVM, а не операционной системой. Их ключевые свойства:

- Создаются через `Thread.ofVirtual().start(runnable)` или `Executors.newVirtualThreadPerTaskExecutor()`
- Реализуют тот же интерфейс `java.lang.Thread`, что и платформенные потоки
- Стоимость создания и переключения контекста на порядки ниже, чем у OS-потоков
- Можно создавать миллионы штук без риска исчерпания памяти
- Основная модель использования: «один виртуальный поток на задачу» вместо thread-pool

**Архитектура: carrier-потоки**

JVM поддерживает небольшой пул платформенных потоков (по умолчанию — `ForkJoinPool` в FIFO-режиме с числом потоков, равным числу доступных процессоров). Эти платформенные потоки называются carrier-потоками. Виртуальные потоки «монтируются» на carrier-поток для выполнения и «размонтируются» при блокировании — тогда carrier освобождается для другого виртуального потока. Это позволяет обслуживать тысячи параллельных I/O-операций силами нескольких OS-потоков.

**Что такое pinning**

Пиннинг — ситуация, когда виртуальный поток не может быть размонтирован с carrier-потока при блокировании. Виртуальный поток «приколот» к своему carrier-потоку и держит его занятым до завершения блокирующей операции. Это уничтожает главное преимущество виртуальных потоков: вместо освобождения carrier-потока для других задач он простаивает.

**Причины пиннинга в JDK 21**

1. **Блокирующая операция внутри `synchronized`-блока или метода.** Важный нюанс: само по себе вхождение в `synchronized` не вызывает пиннинг — он происходит только если внутри `synchronized` выполняется блокирующая операция (I/O, `Thread.sleep()`, сетевые вызовы). Пиннинг нередко скрывается в библиотечном коде: например, `ConcurrentHashMap.computeIfAbsent()` использует `synchronized` внутри, а logging-фреймворки могут делать блокирующие вызовы внутри этого контекста.

2. **Блокирующие нативные вызовы (JNI).** Определённые пути через JNI требуют, чтобы виртуальный поток оставался на carrier-потоке.

3. **Некоторые операции с файловой системой.** `FileInputStream`, операции с каталогами, UDP-сокеты (`DatagramSocket.receive`), DNS-разрешение через `InetSocketAddress` — также могут вызывать пиннинг.

**Диагностика**

В JDK 21 для обнаружения пиннинга используется системное свойство:
```
-Djdk.tracePinnedThreads=full
```

**Изменения в JDK 24 (JEP 491)**

JEP 491 «Synchronize Virtual Threads without Pinning» устранил пиннинг для `synchronized`. В JDK 24+ виртуальные потоки могут захватывать, удерживать и освобождать мониторы независимо от carrier-потоков. Флаг `-Djdk.tracePinnedThreads` был удалён как ставший ненужным. Однако пиннинг через JNI-вызовы остаётся актуальным.

---

### Вопрос 34. Почему использование synchronized внутри виртуальных потоков может свести на нет их преимущества? Что рекомендуется использовать вместо synchronized в контексте Project Loom?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How to solve the pinning problem in Java virtual threads — TheServerSide](https://www.theserverside.com/tip/How-to-solve-the-pinning-problem-in-Java-virtual-threads)

Виртуальные потоки полностью совместимы с использованием `synchronized`-блоков, однако в первом preview-релизе (Java 19) была ограниченность: код, выполняющий блокирующий I/O внутри таких блоков, прикреплялся к OS-потоку (пиннинг), снижая прирост пропускной способности. Если виртуальному потоку нужно выполнить блокирующий код — такой как традиционная синхронизация через `synchronized` или нативные вызовы — он не может просто остановиться и уступить место, как делает при I/O-операциях. Вместо этого виртуальный поток прикрепляется к carrier-потоку.

Проекты, вдумчиво внедряющие Project Loom, будут заменять устаревшие механизмы синхронизации инструментами, позволяющими избежать пиннинга, — такими как `ReentrantLock`. Это позволяет писать неблокирующий код, при котором виртуальные потоки освобождают carrier-потоки во время ожидания, сохраняя преимущества масштабируемости.

#### Ответ от Claude

**Механизм проблемы**

Виртуальные потоки достигают масштабируемости за счёт размонтирования с carrier-потока при блокировании: JVM сохраняет continuation (стек-фреймы), освобождает carrier-поток, и тот может обслуживать другие виртуальные потоки. Если же этот механизм сломан — а именно это происходит при пиннинге — carrier-поток заблокирован, другие виртуальные потоки не могут на нём выполняться, и в итоге 100 000 виртуальных потоков будут выстраиваться в очередь за теми же N carrier-потоками, что и в модели обычных platform threads.

**Почему `synchronized` вызывает пиннинг (в JDK 21)**

Ключевое условие: **не само вхождение в `synchronized`, а блокирующая операция внутри него**. Если в `synchronized`-блоке вызывается I/O, `Thread.sleep()`, сетевой запрос или любой метод, который внутри делает парковку через `LockSupport.park()`, — происходит пиннинг. Особая опасность — скрытый `synchronized` в библиотечном коде. Например:

```java
// ConcurrentHashMap.computeIfAbsent() использует synchronized внутри
map.computeIfAbsent(key, k -> {
    log.info("computing..."); // logging-фреймворк может использовать блокировку
    return expensiveNetworkCall(k); // блокирующий вызов → пиннинг
});
```

Такой код может вызывать пиннинг даже без явного `synchronized` в пользовательском коде.

**Что рекомендуется в JDK 21: `ReentrantLock`**

`java.util.concurrent.locks.ReentrantLock` (и другие блокировки из `java.util.concurrent`) интегрированы с механизмом парковки виртуальных потоков через `LockSupport`. При ожидании на `ReentrantLock` виртуальный поток паркуется и **размонтируется** с carrier-потока без пиннинга.

```java
// Вместо:
synchronized (this) {
    networkCall(); // вызывает пиннинг в JDK 21
}

// Использовать:
lock.lock();
try {
    networkCall(); // виртуальный поток корректно размонтируется
} finally {
    lock.unlock();
}
```

**Другие рекомендации для JDK 21**

- Выносить I/O-операции за пределы `synchronized`-блоков
- Использовать асинхронные/неблокирующие библиотеки
- Диагностировать пиннинг через `-Djdk.tracePinnedThreads=full`
- Для изолированно-короткого кода без I/O — `synchronized` допустим

**Изменение позиции в JDK 24**

JEP 491 устранил пиннинг для `synchronized`. Авторы JEP 491 **больше не рекомендуют** заменять `synchronized` на `ReentrantLock` с целью избежания пиннинга: выбор между ними должен определяться семантикой задачи, а не соображениями производительности виртуальных потоков. Это важное отличие: материалы, написанные до JDK 24, могут категорично утверждать «никогда не используйте `synchronized` с виртуальными потоками» — это было справедливо для JDK 21, но устарело для JDK 24+. На собеседовании стоит упомянуть оба контекста.

---

### Вопрос 35. Как работает CAS (Compare-And-Swap) на уровне железа? В чём заключается проблема ABA и как она решается в AtomicStampedReference?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [AtomicStampedReference — jenkov.com](https://jenkov.com/tutorials/java-util-concurrent/atomicstampedreference.html)

`AtomicStampedReference` хранит одновременно ссылку на объект и числовую метку (stamp). Ссылка и метка могут быть атомарно обменяны в рамках одной CAS-операции через метод `compareAndSet()`. Если другой поток изменил ссылку с A на B, а потом обратно на A, то метка при этом изменится (при условии, что потоки корректно её инкрементируют). Таким образом, сравнение по метке позволяет обнаружить промежуточные изменения, даже если значение вернулось к исходному.

Пример:
```java
AtomicStampedReference<String> ref =
    new AtomicStampedReference<>("A", 0);

boolean success = ref.compareAndSet("A", "B", 0, 1);
// Обновит только если ссылка == "A" И метка == 0
```

#### Ответ от Claude

**CAS на уровне железа**

CAS (Compare-And-Swap) — атомарная инструкция процессора, выполняющая операцию чтение-сравнение-запись как единое неделимое действие. Никакой другой процессор или поток не может вмешаться в её выполнение.

Логика операции:
```
CAS(адрес памяти, ожидаемое_значение, новое_значение) → boolean
  если *адрес == ожидаемое_значение:
      *адрес = новое_значение
      return true
  иначе:
      return false  // значение не изменено
```

**Реализация на разных архитектурах**

- **x86/x86-64**: инструкция `CMPXCHG` (доступна с процессора 80486). На многопроцессорных системах применяется с префиксом `LOCK` для гарантии атомарности через блокировку шины памяти или cache-line.
- **IBM System/370**: CAS существует с 1970 года, широко используется на уровне ОС.
- **Itanium**: реализует `CMPXCHG` и специализированные варианты.
- **ARM**: использует пару инструкций `LDREX`/`STREX` (Load-Link/Store-Conditional — LL/SC), которые семантически эквивалентны CAS.
- **SPARC-V8 и PA-RISC**: не имеют аппаратного CAS, вынуждены использовать спинлоки.

В Java CAS обёрнут в методы `Unsafe.compareAndSwapInt/Long/Object`, которые компилируются JIT в соответствующую нативную инструкцию.

**Проблема ABA**

Проблема возникает в следующем сценарии:

1. Поток T1 читает значение переменной: видит `A`
2. Поток T1 готовится выполнить CAS: `CAS(адрес, A → B)`
3. До того как T1 успевает это сделать, поток T2 меняет значение: `A → B → A`
4. T1 выполняет CAS — он **успешно срабатывает**, так как видит `A`
5. Но промежуточное изменение через `B` полностью проигнорировано

Это критично в структурах данных (например, в lock-free стеках): между чтением и CAS-ом другой поток мог успеть добавить и удалить узел. CAS не обнаружит этого, и алгоритм может повредить структуру данных.

**Решение: `AtomicStampedReference`**

Идея: хранить вместе со значением версионную метку (stamp). CAS теперь проверяет **оба** компонента: `(значение, метка)`. Даже если значение вернулось к `A`, метка изменилась: `(A, 0) → (B, 1) → (A, 2)`. Третий CAS с ожидаемой парой `(A, 0)` провалится, потому что фактическая метка теперь `2`.

```java
AtomicStampedReference<String> ref =
    new AtomicStampedReference<>("A", 0);

// Поток T1 читает текущее состояние:
int[] stampHolder = new int[1];
String value = ref.get(stampHolder);
int stamp = stampHolder[0]; // stamp = 0

// Поток T2 в это время делает: A(0) → B(1) → A(2)

// Поток T1 пытается CAS с ожидаемой парой (A, 0):
boolean success = ref.compareAndSet("A", "B", 0, 1);
// success = false! Фактическая метка = 2, ожидаемая = 0
```

`AtomicMarkableReference` — упрощённый вариант с булевой меткой вместо счётчика; позволяет отметить «логически удалённые» узлы, но не полностью решает ABA (метка может вернуться к исходному значению повторно).

**Ограничения CAS и lock-free алгоритмов**

- **ABA** — описана выше
- **Starvation** — один поток теоретически может бесконечно «проигрывать» CAS
- **Overhead на contention** — при высокой конкуренции CAS-циклы потребляют CPU (spinning); `LongAdder` решает это через striping

---

### Вопрос 36. Можно ли сделать singleton потокобезопасным без synchronized? Объясните идиому double-checked locking и почему без volatile она сломана.

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [The "Double-Checked Locking is Broken" Declaration — cs.umd.edu](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)

Запись, инициализирующая объект `Helper`, и запись в поле `helper` могут быть выполнены или восприняты в произвольном порядке. Компилятор Symantec JIT присваивал ссылку полю `helper` **до** выполнения конструктора — это допускалось старой моделью памяти. Даже без вмешательства компилятора на многопроцессорной системе процессор или подсистема памяти может переупорядочить записи так, как это воспринимается потоком на другом процессоре. Начиная с JDK 5, `volatile` расширены семантикой: запись в volatile-поле не допускает переупорядочивания относительно любой предшествующей записи или чтения; чтение volatile не допускает переупорядочивания относительно любых последующих чтений или записей.

#### Ответ от Claude

**Потокобезопасный singleton без synchronized — возможности**

Да, существует несколько способов:

1. **Eager initialization** — создание при загрузке класса (JVM гарантирует thread-safety при инициализации класса):
```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    public static Singleton getInstance() { return INSTANCE; }
}
```

2. **Initialization-on-demand holder (Билл Пью)** — ленивая инициализация без явного `synchronized`:
```java
public class Singleton {
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() { return Holder.INSTANCE; }
}
```
Внутренний класс `Holder` загружается только при первом вызове `getInstance()`. Инициализация класса в JVM гарантированно потокобезопасна без явной синхронизации.

3. **Enum singleton** (Joshua Bloch, «Effective Java»):
```java
public enum Singleton {
    INSTANCE;
}
```

4. **Double-Checked Locking с `volatile`** — описан ниже.

**Идиома Double-Checked Locking**

```java
public class Singleton {
    private static volatile Singleton instance; // обязательно volatile

    public static Singleton getInstance() {
        if (instance == null) {                 // первая проверка (без блокировки)
            synchronized (Singleton.class) {
                if (instance == null) {         // вторая проверка (с блокировкой)
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

Цель паттерна — избежать дорогостоящего `synchronized` при каждом вызове `getInstance()` после инициализации, сохранив ленивость создания экземпляра.

**Почему без `volatile` паттерн сломан**

Ключевая проблема — **переупорядочивание инструкций**. Выражение `instance = new Singleton()` на уровне байткода раскладывается примерно в три шага:

```
1. memory = allocate()        // выделить память
2. init(memory)               // выполнить конструктор
3. instance = memory          // записать ссылку в поле
```

**JVM и CPU могут переупорядочить шаги 2 и 3.** Это законно с точки зрения однопоточной корректности: пока никто снаружи не видит объект, внутренний порядок инициализации не важен.

Сценарий гонки:

1. Поток T1 заходит в `synchronized`, начинает создавать `Singleton`
2. JIT/CPU переупорядочил инструкции: шаг 3 (запись ссылки) произошёл **до** шага 2 (конструктор не завершён)
3. Поток T2 проходит первую проверку `if (instance == null)` — видит ненулевую ссылку
4. T2 возвращает **частично инициализированный объект** и использует его

**Как `volatile` исправляет ситуацию**

`volatile` в Java 5+ (JSR-133, новая модель памяти JMM) добавляет два эффекта:

1. **Запрет переупорядочивания**: запись в `volatile`-поле не может быть переупорядочена относительно **любых предшествующих** операций. Это гарантирует, что конструктор (`init`) завершится раньше, чем ссылка станет видна другим потокам (`instance = memory`).

2. **Happens-before гарантия**: запись в `volatile`-поле happens-before любого последующего чтения этого поля из другого потока. Поток T2, увидевший ненулевое значение `instance`, гарантированно видит все записи, сделанные T1 до записи в `instance`.

**Почему паттерн был сломан до Java 5**: старая JMM (JDK 1.4 и ранее) не имела достаточно строгой семантики `volatile`, чтобы предотвратить эту проблему. Именно этот баг был задокументирован в знаменитой статье «The "Double-Checked Locking is Broken" Declaration».

**Итог**: для нового кода рекомендуется предпочитать Initialization-on-demand holder или enum-singleton как более простые и надёжные решения. DCL с `volatile` корректен в Java 5+, но избыточно сложен для большинства случаев.

---
### Вопрос 37. Чем CountDownLatch отличается от CyclicBarrier и Phaser? Когда каждый из них предпочтительнее?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [CountDownLatch vs CyclicBarrier vs Phaser — JavaSpecialists Issue 257](https://www.javaspecialists.eu/archive/Issue257-CountDownLatch-vs-CyclicBarrier-vs-Phaser.html)

`CountDownLatch` — одноразовый синхронизатор, счётчик которого никогда не сбрасывается: для каждой новой группы задач нужно создавать новый экземпляр. Работа с прерываниями требует ручного управления: нужно обрабатывать `InterruptedException` в цикле и восстанавливать флаг прерывания. Прост в понимании, но неудобен в использовании.

`CyclicBarrier` переиспользуется в нескольких циклах без пересоздания. Всё ещё требует многословной обработки прерываний и бросает как `InterruptedException`, так и `BrokenBarrierException`. Лучше `CountDownLatch` для повторяющихся точек синхронизации.

`Phaser` (добавлен в Java 7) — наиболее гибкий вариант, при этом сложен в понимании, но прост в использовании. Метод `arriveAndAwaitAdvance()` заменяет весь шаблонный код обработки прерываний. Реализован с поддержкой `ManagedBlocker`, что позволяет ForkJoinPool создавать дополнительные потоки при блокировке. Поддерживает древовидную конфигурацию для снижения contention — недоступную в других синхронизаторах. Хранит номер фазы, что исключает необходимость вручную передавать номер партии.

Рекомендации:
- **CountDownLatch** — для однократных барьеров (например, старт всех потоков одновременно, ожидание завершения инициализации)
- **CyclicBarrier** — для повторяющейся синхронизации с фиксированным числом потоков (при приемлемых накладных расходах на обработку прерываний)
- **Phaser** — для многофазной координации, особенно в контексте ForkJoin-пулов и динамического числа участников

#### Ответ от Claude

**Концептуальное различие**

Все три класса решают задачу барьерной синхронизации, но с разными компромиссами по гибкости и сложности.

| Характеристика | CountDownLatch | CyclicBarrier | Phaser |
|---|---|---|---|
| Повторное использование | Нет (одноразовый) | Да (сбрасывается) | Да (фазы 0..MAX_VALUE) |
| Число участников | Фиксировано | Фиксировано | Динамическое |
| Семантика | N задач → M ожидающих потоков | N потоков ждут друг друга | N участников за фазу |
| Прерывания | Требует ручной обработки | Требует ручной обработки | Обрабатывает прозрачно |
| Доступно с | Java 5 | Java 5 | Java 7 |

**CountDownLatch**

Счётчик уменьшается вызовом `countDown()` (обычно из рабочих потоков или при завершении событий), а один или несколько потоков блокируются на `await()` до обнуления счётчика. Ключевое отличие: `countDown()` вызывают не обязательно те же потоки, которые ждут. Счётчик никогда не сбрасывается — для повторного использования нужен новый экземпляр.

```java
CountDownLatch latch = new CountDownLatch(3);
// в рабочих потоках:
latch.countDown();
// в ожидающем потоке:
latch.await();
```

Когда использовать: однократная синхронизация — ожидание старта всех сервисов, сигнал начала гонки нескольким потокам, ожидание завершения группы операций.

**CyclicBarrier**

Все N потоков вызывают `await()` и блокируются, пока последний не дойдёт до барьера — тогда все одновременно разблокируются. Барьер автоматически сбрасывается для следующего цикла. Поддерживает необязательное действие (`Runnable barrierAction`), выполняемое при срабатывании барьера.

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("Все пришли!"));
// в каждом потоке:
barrier.await();
```

Когда использовать: итерационные алгоритмы, где потоки синхронизируются в конце каждой итерации (параллельные вычисления по шагам, симуляции).

**Phaser**

Наиболее мощный и гибкий. Участники могут регистрироваться и выходить динамически (`register()` / `arriveAndDeregister()`). Поддерживает многофазное выполнение с номером фазы. Позволяет переопределить `onAdvance()` для управления завершением.

```java
Phaser phaser = new Phaser(1); // регистрируем себя
for (Runnable task : tasks) {
    phaser.register();
    new Thread(() -> {
        phaser.arriveAndAwaitAdvance(); // стартовый барьер
        task.run();
    }).start();
}
phaser.arriveAndDeregister(); // даём сигнал старта
```

Максимум 65 535 участников; для большего — поддерживается иерархическая структура (tiered phasers).

Когда использовать:
- Динамическое число участников, меняющееся между фазами
- Многофазные пайплайны (фаза 1 → фаза 2 → ...)
- Работа в ForkJoinPool (использует `ManagedBlocker` для оптимизации)
- Замена `CountDownLatch` там, где число задач известно лишь в рантайме

**Итог выбора**

- `CountDownLatch` — простейший случай: одна точка ожидания, число событий известно заранее
- `CyclicBarrier` — фиксированная группа потоков синхронизируется повторно
- `Phaser` — всё остальное: динамика, многофазность, ForkJoin-контекст; предпочтителен в современном коде на Java 7+

---

### Вопрос 38. Как настроить размер пула потоков для CPU-bound и IO-bound задач? Какие метрики нужно отслеживать, чтобы понять, что пул переполнен или простаивает?

**Категория:** Concurrency · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [How to set an ideal thread pool size — Zalando Engineering Blog](https://engineering.zalando.com/posts/2019/04/how-to-set-an-ideal-thread-pool-size.html)

Базовая формула из книги Брайана Гётца «Java Concurrency in Practice»:

**Число потоков = Число ядер CPU × (1 + Время ожидания / Время работы)**

Расширенная формула с целевой загрузкой CPU:

**Число потоков = Число ядер CPU × Целевая загрузка CPU × (1 + Время ожидания / Время работы)**

Ключевые концепции:
- **Blocking coefficient** (коэффициент блокирования) — отношение времени ожидания к времени полезной работы
- **CPU-bound задачи**: коэффициент близок к 0 → размер пула ≈ числу ядер CPU
- **IO-bound задачи**: коэффициент высок → можно держать значительно больше потоков, чем ядер

Практический пример: микросервис с 50 мс ожидания ответа и 5 мс обработки на двухъядерной машине:
`2 × (1 + 50/5) = 22 потока`

Дополнительно применяется закон Литтла для оценки пропускной способности:
`L = λ × W`, где L — число одновременных запросов, λ — входящий поток (RPS), W — среднее время обработки.

Авторы подчёркивают: формулы дают отправную точку, реальные параметры нужно валидировать нагрузочным тестированием.

#### Ответ от Claude

**Настройка размера пула**

Определение числа доступных ядер в Java:
```java
int cpuCores = Runtime.getRuntime().availableProcessors();
```

**CPU-bound задачи** (вычисления, сжатие, шифрование):
- Потоки не ждут внешних ресурсов, узкое место — сам процессор
- Оптимальный размер пула: **N = количество ядер CPU** (или N+1 по некоторым рекомендациям для компенсации случайных пауз GC)
- Лишние потоки лишь добавляют накладные расходы на переключение контекста и конкуренцию за CPU

```java
int poolSize = Runtime.getRuntime().availableProcessors();
ExecutorService cpuPool = Executors.newFixedThreadPool(poolSize);
```

**IO-bound задачи** (сетевые вызовы, база данных, файловые операции):
- Потоки большую часть времени ожидают — процессор простаивает
- Оптимальный размер пула рассчитывается по формуле Гётца:

```
N = CPU_cores × (1 + W/C)
```

где W (wait time) — время ожидания IO, C (compute time) — время CPU-обработки.

При желании ограничить загрузку CPU:
```
N = CPU_cores × targetCPUUtilization × (1 + W/C)
```

Пример: 8 ядер, задача 90 мс ждёт ответа БД и 10 мс обрабатывает результат:
`N = 8 × (1 + 90/10) = 80 потоков`

**Тип очереди и стратегия отказа**

Выбор очереди влияет на поведение при нагрузке:

| Очередь | Применение | Риск |
|---|---|---|
| `SynchronousQueue` | Обработка взаимозависимых задач | Неограниченный рост числа потоков |
| `LinkedBlockingQueue` (без предела) | Независимые задачи с пиковой нагрузкой | Неограниченный рост очереди и OOM |
| `ArrayBlockingQueue` (ограниченная) | Предсказуемый контроль ресурсов | Сложнее тюнинг |

При насыщении пула следует предпочесть `CallerRunsPolicy` — она создаёт обратное давление (back-pressure), замедляя производителей задач, вместо потери задач (`DiscardPolicy`) или исключения (`AbortPolicy`).

**Метрики для мониторинга**

`ThreadPoolExecutor` предоставляет методы для отслеживания состояния:

```java
ThreadPoolExecutor executor = (ThreadPoolExecutor) threadPool;

// Число потоков в пуле прямо сейчас
executor.getPoolSize();

// Число потоков, активно выполняющих задачи
executor.getActiveCount();

// Максимальный размер пула, достигнутый за всё время
executor.getLargestPoolSize();

// Размер очереди ожидания
executor.getQueue().size();

// Всего задач было поставлено в пул
executor.getTaskCount();

// Всего задач завершено
executor.getCompletedTaskCount();
```

**Признаки переполнения пула (saturated):**
- `getQueue().size()` стабильно растёт или близка к максимуму
- `getActiveCount() == getMaximumPoolSize()` (все потоки заняты)
- Появляются `RejectedExecutionException`
- Latency задач растёт, throughput не растёт
- CPU загружен не полностью при растущей очереди (IO-bound ситуация, не хватает потоков)

**Признаки простоя пула (idle/oversized):**
- `getActiveCount()` постоянно близок к 0 при наличии входящих задач
- `getPoolSize()` >> `getActiveCount()` (большинство потоков простаивают)
- Потоки расходуют память впустую (стек каждого потока ≈ 512 КБ–1 МБ по умолчанию)

**Инструменты мониторинга:**
- **JMX / ThreadMXBean** — встроенный мониторинг JVM
- **Micrometer** — метрики `executor.pool.size`, `executor.active`, `executor.queued`, `executor.completed` с экспортом в Prometheus/Grafana
- **Spring Boot Actuator** — автоматически публикует метрики пулов через `/actuator/metrics`
- **Netflix Spectator** — `ThreadPoolMonitor` с polling в фоне

**Практические рекомендации:**
1. Начинать с формулы Гётца как отправной точки
2. Проводить нагрузочное тестирование с реальным профилем задач
3. Для IO-bound задач рассматривать виртуальные потоки (Java 21 Virtual Threads) — они устраняют необходимость вручную рассчитывать размер пула для IO

---
### Вопрос 39. Чем LongAdder отличается от AtomicLong? Что такое striping (Striped64) и почему LongAdder превосходит AtomicLong при высокой конкуренции?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [LongAdder (Java SE 21 & JDK 21) — Oracle Docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html)

Класс `LongAdder` поддерживает начально-нулевую сумму типа `long`, распределённую по одной или нескольким внутренним переменным. Когда операции обновления (`add(long)`) конкурируют между потоками, набор внутренних переменных динамически увеличивается, чтобы снизить конкуренцию. Метод `sum()` (или, эквивалентно, `longValue()`) возвращает текущую совокупную сумму всех переменных.

Этот класс обычно предпочтителен вместо `AtomicLong`, когда несколько потоков обновляют общую сумму, используемую для целей наподобие сбора статистики, а не для тонкого управления синхронизацией. При низкой конкуренции оба класса характеристики схожи. При высокой конкуренции ожидаемая пропускная способность `LongAdder` значительно выше, однако ценой более высокого потребления памяти.

Практический пример использования — масштабируемые счётчики частоты в `ConcurrentHashMap`:
```java
ConcurrentHashMap<String, LongAdder> freqs = new ConcurrentHashMap<>();
freqs.computeIfAbsent(key, k -> new LongAdder()).increment();
```

`LongAdder` не определяет методы `equals`, `hashCode` и `compareTo`, так как экземпляры изменяемы и не подходят в качестве ключей коллекций.

#### Ответ от Claude

**Архитектурная разница**

`AtomicLong` хранит одно `volatile long`-значение и выполняет атомарные операции через CAS (Compare-And-Swap). При высокой конкуренции многие потоки соревнуются за одно и то же слово в памяти: проигравший CAS вынужден повторять попытку (spin), что ведёт к значительному расходу процессорных циклов.

`LongAdder` (вместе с базовым классом `Striped64`) использует другой подход — **динамическое страйпирование** (dynamic striping):

1. Помимо базовой ячейки (`base`), класс поддерживает массив объектов `Cell`.
2. Каждый `Cell` содержит отдельное `volatile long`-значение и аннотирован `@jdk.internal.vm.annotation.Contended`, что добавляет достаточно заполнения (padding) вокруг каждого состояния, чтобы оно занимало отдельную строку кэша процессора — это предотвращает **false sharing**.
3. При конкуренции поток хешируется к конкретной ячейке и обновляет только её. Разные потоки чаще всего попадают в разные ячейки и не мешают друг другу.
4. Массив растёт вдвое по необходимости (длина всегда степень двойки) вплоть до числа, близкого к количеству процессоров.

**Почему название Striped64**

Класс называется `Striped64` по двум причинам: "64" — потому что работает с 64-битными типами данных; "striped" — потому что реализует идею распределения обновлений по нескольким ячейкам (полосам).

**Метод sum() не атомарен**

Метод `sum()` возвращает снимок (snapshot) суммы всех ячеек и базовой переменной. Поскольку конкурентные обновления могут происходить в момент подсчёта, результат не гарантирует точного значения счётчика в конкретный момент времени — это норма для статистических счётчиков, но неприемлемо для контроля параллелизма.

**Когда что использовать**

| Критерий | `AtomicLong` | `LongAdder` |
|---|---|---|
| Высокая конкуренция | Хуже (spin на CAS) | Значительно лучше |
| Низкая конкуренция | Сопоставимо | Сопоставимо |
| Потребление памяти | Меньше (одна переменная) | Больше (массив Cell) |
| Атомарность результата | Да (`get()` — точное значение) | Нет (`sum()` — снимок) |
| Атомарные операции (compareAndSet и т.п.) | Поддерживает | Не поддерживает |

**Вывод:** используйте `LongAdder` для высококонкурентных счётчиков и статистики; используйте `AtomicLong`, когда нужны точные атомарные операции типа `compareAndSet`, или когда конкуренция невысока.

---

### Вопрос 40. Как работает механизм прерывания потока в Java? В чём разница между interrupt(), isInterrupted() и Thread.interrupted()? Какова правильная стратегия обработки InterruptedException?

**Категория:** Concurrency · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Interrupts — The Java Tutorials (Oracle)](https://docs.oracle.com/javase/tutorial/essential/concurrency/interrupt.html)

Прерывание (interrupt) — это сигнал потоку о том, что ему следует остановить текущую работу и заняться чем-то другим. Решение о том, как именно поток реагирует на прерывание, остаётся за разработчиком, однако обычно поток завершается.

Механизм прерывания реализован через внутренний флаг — статус прерывания (interrupt status). Вызов `Thread.interrupt()` устанавливает этот флаг. Если поток заблокирован вызовом методов `sleep()`, `wait()`, `join()` и т.п., он получает `InterruptedException`, а флаг при этом **сбрасывается**.

**Три метода работы с прерыванием:**

- `interrupt()` — устанавливает флаг прерывания у целевого потока.
- `isInterrupted()` — проверяет флаг конкретного потока **без его сброса**.
- `Thread.interrupted()` (статический) — проверяет флаг текущего потока **и сбрасывает его**.

**Стратегия 1 — поймать и выйти** (когда поток регулярно вызывает блокирующие методы):
```java
for (int i = 0; i < importantInfo.length; i++) {
    try {
        Thread.sleep(4000);
    } catch (InterruptedException e) {
        return; // прерывание получено — завершаем работу
    }
    System.out.println(importantInfo[i]);
}
```

**Стратегия 2 — периодически проверять флаг** (когда поток выполняет длительные операции без вызова блокирующих методов):
```java
for (int i = 0; i < inputs.length; i++) {
    heavyCrunch(inputs[i]);
    if (Thread.interrupted()) {
        return;
    }
}
```

**Стратегия 3 — пробросить `InterruptedException` выше** для централизованной обработки.

#### Ответ от Claude

**Как работает флаг прерывания**

Каждый поток Java имеет внутренний булевый флаг — статус прерывания. Флаг устанавливается в `true` вызовом `interrupt()`. Механизм является **кооперативным**: поток не останавливается принудительно, а лишь получает сигнал, который обязан проверять самостоятельно.

**Три метода: подробное сравнение**

| Метод | Тип | На какой поток | Сбрасывает флаг | Когда использовать |
|---|---|---|---|---|
| `interrupt()` | экземплярный | целевой поток | нет | отправить сигнал другому потоку |
| `isInterrupted()` | экземплярный | любой поток | нет | наблюдать за статусом снаружи |
| `Thread.interrupted()` | статический | только текущий поток | **да** | проверить и сбросить внутри самого потока |

**Важное поведение при блокировке**

Когда поток прерывается в момент блокировки на `sleep()`, `wait()`, `join()`:
1. Флаг прерывания **сбрасывается** (! — это не интуитивно, но задокументировано).
2. Бросается `InterruptedException`.

Для операций на `InterruptibleChannel` (NIO): канал закрывается, флаг устанавливается и бросается `ClosedByInterruptException`.

**Правильные стратегии обработки InterruptedException**

**1. Пробросить исключение выше (предпочтительно):**
```java
public void doWork() throws InterruptedException {
    Thread.sleep(1000); // просто не ловим — пробрасываем
}
```

**2. Восстановить флаг и завершить:**
```java
public void run() {
    try {
        while (!Thread.currentThread().isInterrupted()) {
            doWork();
        }
    } catch (InterruptedException e) {
        // Восстанавливаем флаг: метод sleep() его сбросил при броске исключения
        Thread.currentThread().interrupt();
        // Завершаем работу корректно
    }
}
```

**3. Нельзя делать — "проглотить" исключение:**
```java
// НЕПРАВИЛЬНО: исключение поглощено, вызывающий код не знает о прерывании
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    // пусто или только log — прерывание потеряно
}
```

**Почему восстановление флага важно**

Если поток поймал `InterruptedException` и не пробрасывает его, он обязан вызвать `Thread.currentThread().interrupt()`, чтобы восстановить флаг. Это позволяет вышестоящему коду в стеке вызовов узнать о том, что прерывание произошло. Метод `sleep()` при броске `InterruptedException` автоматически сбрасывает флаг — именно поэтому его надо восстанавливать вручную.

---

