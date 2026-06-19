# Конкурентные коллекции Java (java.util.concurrent)

> **Уровень:** Middle / Senior
> **Это углублённое дополнение к области** [[04-concurrency]] (общая многопоточность — там).
> **Связанные документы:** [[03-collections-internals]] · обзор [[03-collections]]
> **Связанные вопросы:** [Вопросы по многопоточности →](../../../interview-questions/concurrency-01.md)

## Что это и зачем

Обычные коллекции (`ArrayList`, `HashMap`) **не потокобезопасны**: одновременная модификация из разных
потоков приводит к гонкам, порче структуры и `ConcurrentModificationException`. Исторически проблему
решали обёртками `Collections.synchronizedXxx`, `Hashtable`, `Vector` — они защищают **одной общей
блокировкой на всю коллекцию**, что не масштабируется. Пакет `java.util.concurrent` предлагает коллекции,
спроектированные для конкурентного доступа: тонкая блокировка/неблокирующие алгоритмы, **слабосогласованные
итераторы** и атомарные составные операции.

**Слабосогласованный (weakly consistent) итератор** — ключевое свойство concurrent-коллекций: он обходит
элементы, отражающие состояние коллекции на некоторый момент с момента создания итератора, **не бросает
`ConcurrentModificationException`** и может работать параллельно с изменениями (в отличие от fail-fast у
`java.util`).

Источник: [Oracle — пакет java.util.concurrent (раздел про итераторы)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html)

---

## Синхронизированные обёртки vs конкурентные коллекции

| | `Collections.synchronizedMap` / `Hashtable` | `ConcurrentHashMap` |
|---|---|---|
| Блокировка | одна на всю коллекцию | на уровне бакета (или без блокировки на чтении) |
| Чтение | под общей блокировкой | без блокировок (`volatile`) |
| Итератор | fail-fast (нужна внешняя синхронизация) | слабосогласованный (fail-safe) |
| Масштабируемость | низкая | высокая |

Вывод: для нового кода почти всегда предпочтительны коллекции из `java.util.concurrent`. Общая блокировка
оправдана лишь когда важна строгая согласованность всех операций.

Источник: [Baeldung — Collections.synchronizedMap vs ConcurrentHashMap](https://www.baeldung.com/java-synchronizedmap-vs-concurrenthashmap)

---

## ConcurrentHashMap

Потокобезопасная хэш-таблица (устройство Java 8: массив бинов, CAS на пустой бин + `synchronized` на
голове непустого бина, чтение без блокировок — подробно в [[03-collections-internals]]).

- Запрещает `null` как ключ и значение.
- Предоставляет **атомарные составные операции**: `putIfAbsent`, `computeIfAbsent`, `compute`, `merge` —
  их следует использовать вместо «проверил-потом-вставил», которое в многопоточности не атомарно.
- Итераторы слабосогласованные; `size()` — приблизительный.

Источники: [Oracle API — ConcurrentHashMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html) ·
[Baeldung — A Guide to ConcurrentMap](https://www.baeldung.com/java-concurrent-map)

---

## ConcurrentSkipListMap / ConcurrentSkipListSet

Конкурентный **отсортированный** аналог `TreeMap`/`TreeSet`, построенный на **списке с пропусками
(skip list)** — вероятностной структуре из нескольких «уровней» связанных списков.

- `get`/`put`/`remove`/`containsKey` — в среднем **O(log n)**.
- Реализует `ConcurrentNavigableMap`: `firstKey`, `floorKey`, `ceilingKey`, `subMap` и т.д.
- Потокобезопасен без глобальных блокировок (CAS на узлах); итераторы слабосогласованные.
- Восходящие (ascending) представления и их итераторы быстрее нисходящих.

Используйте, когда нужны **одновременно** потокобезопасность и сортировка по ключу.

Источники: [Oracle API — ConcurrentSkipListMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentSkipListMap.html) ·
[Baeldung — Guide to the ConcurrentSkipListMap](https://www.baeldung.com/java-concurrent-skip-list-map)

---

## CopyOnWriteArrayList / CopyOnWriteArraySet

Список (и множество) для сценариев **«много чтений, мало записей»**. При любой модификации создаётся
**полная копия** внутреннего массива; чтения идут по неизменяемому снимку без блокировок.

- Чтение — O(1) без синхронизации; запись — O(n) (копирование, под общей блокировкой записи).
- Итератор работает со **снимком** на момент создания: не бросает `ConcurrentModificationException`,
  но не видит последующих изменений и не поддерживает `remove()`.
- Не подходит, если записей много (накладные расходы на копирование).

Источники: [Oracle API — CopyOnWriteArrayList](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CopyOnWriteArrayList.html) ·
[Baeldung — A Guide to CopyOnWriteArrayList](https://www.baeldung.com/java-copy-on-write-arraylist)

---

## Неблокирующие очереди: ConcurrentLinkedQueue / ConcurrentLinkedDeque

Потокобезопасные **неблокирующие** очереди на связных узлах, реализующие алгоритм Майкла–Скотта на **CAS**
(без блокировок).

- `ConcurrentLinkedQueue` — неограниченная FIFO-очередь; `ConcurrentLinkedDeque` — двусторонняя.
- Операции `offer`/`poll` — амортизированно O(1); при пустой очереди `poll()` сразу возвращает `null`
  (не блокирует — этим отличается от `BlockingQueue`).
- `size()` — **O(n)** и неточен при конкурентных изменениях, его не стоит использовать для логики.

Источники: [Oracle API — ConcurrentLinkedQueue](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentLinkedQueue.html) ·
[Baeldung — A Guide to Concurrent Queues in Java](https://www.baeldung.com/java-concurrent-queues)

---

## Блокирующие очереди: BlockingQueue

`BlockingQueue` — основа паттерна «производитель–потребитель». Блокирует поток на `put()`, если очередь
полна, и на `take()`, если пуста. Не допускает `null`. Имеет методы с разным поведением:
блокирующие (`put`/`take`), с таймаутом (`offer`/`poll`), мгновенные (`offer`/`poll`) и `add`/`remove`
(бросают исключение).

| Реализация | Граница | Структура / особенности |
|------------|---------|-------------------------|
| `ArrayBlockingQueue` | ограниченная | кольцевой массив, **одна** блокировка на put и take |
| `LinkedBlockingQueue` | опционально ограниченная | связные узлы, **две** блокировки (putLock/takeLock) → выше throughput |
| `PriorityBlockingQueue` | неограниченная | двоичная куча, выдаёт по приоритету (`Comparable`/`Comparator`) |
| `DelayQueue` | неограниченная | элементы доступны только по истечении их задержки (`Delayed`) |
| `SynchronousQueue` | ёмкость 0 | прямая передача: каждый `put` ждёт `take` (handoff без хранения) |
| `LinkedTransferQueue` | неограниченная | метод `transfer()` — ждать, пока элемент заберёт потребитель |
| `LinkedBlockingDeque` | опционально ограниченная | двусторонняя блокирующая очередь (`BlockingDeque`) |

Источники: [Oracle API — BlockingQueue](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/BlockingQueue.html) ·
[Baeldung — Guide to BlockingQueue](https://www.baeldung.com/java-blocking-queue) ·
[Baeldung — ArrayBlockingQueue vs LinkedBlockingQueue](https://www.baeldung.com/java-arrayblockingqueue-vs-linkedblockingqueue) ·
[Jenkov — Java BlockingQueue](https://jenkov.com/tutorials/java-util-concurrent/blockingqueue.html)

---

## Что выбрать

| Задача | Рекомендуемая коллекция |
|--------|--------------------------|
| Потокобезопасная карта | `ConcurrentHashMap` |
| Потокобезопасная **отсортированная** карта | `ConcurrentSkipListMap` |
| Список с редкими записями и частыми чтениями | `CopyOnWriteArrayList` |
| Неблокирующая FIFO-очередь | `ConcurrentLinkedQueue` |
| Producer–consumer с ограничением | `ArrayBlockingQueue` / `LinkedBlockingQueue` |
| Очередь по приоритету (многопоточно) | `PriorityBlockingQueue` |
| Отложенные задачи по времени | `DelayQueue` (или `ScheduledThreadPoolExecutor`) |
| Прямая передача между потоками | `SynchronousQueue` |

---

## Достоверные источники (почему им можно доверять)

1. **[Oracle — пакет java.util.concurrent](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html)** —
   официальная документация: контракты, гарантии памяти и семантика итераторов из первых рук.
2. **[Baeldung — Java Concurrency](https://www.baeldung.com/java-util-concurrent)** —
   авторитетные и доступные практические разборы каждой коллекции с примерами.
3. **[Jenkov — java.util.concurrent](https://jenkov.com/tutorials/java-util-concurrent/index.html)** —
   наглядные объяснения блокирующих очередей и конкурентных структур.
4. **Книга «Java Concurrency in Practice» (Brian Goetz)** — канонический первоисточник по конкурентным
   коллекциям и модели памяти Java.
5. **[Исходный код OpenJDK (java.util.concurrent)](https://github.com/openjdk/jdk/tree/master/src/java.base/share/classes/java/util/concurrent)** —
   первоисточник «правды»: реальные алгоритмы (CAS-очереди, skip list, две блокировки в LinkedBlockingQueue).
