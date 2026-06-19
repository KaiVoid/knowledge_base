# Внутреннее устройство коллекций Java

> **Уровень:** Middle / Senior
> **Это углублённое дополнение к области** [[03-collections]] (обзор и иерархия — там).
> **Связанные вопросы:** [Вопросы по коллекциям →](../../../interview-questions/collections-01.md)
> **Связанные области:** [[02-jvm-memory-gc]], [[04-concurrency]], [[12-algorithms-data-structures]]

## Что это и зачем

Понимание того, *как именно* устроены коллекции внутри, объясняет их асимптотику, поведение при росте,
причины `ConcurrentModificationException`, цену вставки/удаления и выбор правильной структуры под задачу.
Ниже — разбор реализаций из пакета `java.util` (и `java.util.concurrent`) с указанием реальных констант
из исходного кода OpenJDK и ссылками на доступные и проверенные источники.

---

## ArrayList — динамический массив

Внутри — обычный массив `Object[] elementData`. `ArrayList` различает **size** (число элементов) и
**capacity** (длину внутреннего массива).

- Конструктор по умолчанию создаёт **пустой** массив; реальная ёмкость `DEFAULT_CAPACITY = 10`
  выделяется лениво — при первом `add()`.
- При нехватке места вызывается `grow()`: новая ёмкость `= oldCapacity + (oldCapacity >> 1)`, то есть
  **рост в 1.5 раза** (10 → 15 → 22 → 33 → …). Происходит `Arrays.copyOf` — копирование в новый массив.
- `add(e)` в конец — амортизированная **O(1)**; `add(i, e)` и `remove(i)` в середину — **O(n)**
  (сдвиг через `System.arraycopy`); `get(i)`/`set(i, e)` — **O(1)** (реализует `RandomAccess`).
- `trimToSize()` ужимает массив до размера; `ensureCapacity(n)` заранее резервирует место.

Источники: [Oracle API — ArrayList](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html) ·
[Baeldung — Capacity of ArrayList vs Size of Array](https://www.baeldung.com/java-list-capacity-array-size) ·
[Исходник OpenJDK — ArrayList.java](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/ArrayList.java)

---

## LinkedList — двусвязный список

Реализует одновременно `List` и `Deque`. Каждый элемент — узел `Node` с тремя полями: `prev`, `item`, `next`.
Класс хранит ссылки на `first` и `last`.

- Вставка/удаление по концам (и через итератор в известной позиции) — **O(1)**.
- Доступ по индексу `get(i)` — **O(n)**: список проходится с ближайшего конца.
- Нет `RandomAccess`. На практике для «списка с произвольным доступом» почти всегда лучше `ArrayList`
  (лучшая локальность памяти, нет накладных расходов на узлы по ~24–40 байт каждый).

Источники: [Oracle API — LinkedList](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html) ·
[Baeldung — Guide to LinkedList](https://www.baeldung.com/java-linkedlist) ·
[Jenkov — Java LinkedList](https://jenkov.com/tutorials/java-collections/linkedlist.html)

---

## ArrayDeque — кольцевой буфер

Двусторонняя очередь на массиве с **головой и хвостом по кругу** (circular array); ёмкость — степень двойки,
индексы маскируются `& (length - 1)`. При заполнении массив удваивается.

- Операции с обоими концами — амортизированная **O(1)**.
- Рекомендуется вместо устаревшего `Stack` (как стек) и вместо `LinkedList` (как очередь): быстрее и без
  накладных расходов на узлы. Не допускает `null`.

Источники: [Oracle API — ArrayDeque](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html) ·
[Baeldung — Guide to ArrayDeque](https://www.baeldung.com/java-array-deque)

---

## HashMap — хэш-таблица с бакетами

Сердце Collections Framework. Внутри — массив бакетов `Node<K,V>[] table`, где `Node` хранит
`hash`, `key`, `value`, `next`.

**Хэширование и выбор бакета:**
- Хэш ключа «перемешивается», чтобы старшие биты влияли на индекс:
  `hash = (h = key.hashCode()) ^ (h >>> 16)`.
- Индекс бакета: `(n - 1) & hash`, где `n` — длина таблицы. Поскольку `n` всегда **степень двойки**,
  это эквивалентно `hash % n`, но быстрее.

**Константы (из исходника):**
- `DEFAULT_INITIAL_CAPACITY = 16`, `DEFAULT_LOAD_FACTOR = 0.75`.
- `threshold = capacity × loadFactor` (для 16×0.75 = 12). При превышении — **resize**: таблица
  увеличивается **вдвое**, элементы перераспределяются.

**Коллизии и treeify:**
- Элементы с одинаковым индексом образуют **связный список** в бакете.
- Начиная с Java 8, если в одном бакете накопилось `TREEIFY_THRESHOLD = 8` узлов **и** размер таблицы
  `≥ MIN_TREEIFY_CAPACITY = 64`, список превращается в **красно-чёрное дерево** (поиск O(n) → O(log n)).
  Если таблица меньше 64 — вместо treeify происходит resize.
- При удалении, когда узлов в дереве становится `≤ UNTREEIFY_THRESHOLD = 6`, дерево снова сворачивается в список.

**Сложность:** `get`/`put` в среднем **O(1)**, в худшем (плохой `hashCode`) — O(log n) благодаря деревьям.
**Важно:** ключи должны корректно реализовывать `equals()`/`hashCode()` и быть неизменяемыми по полям,
участвующим в хэше (см. [[01-core-java-syntax-oop]]).

Источники: [Oracle API — HashMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html) ·
[Baeldung — Java HashMap Load Factor](https://www.baeldung.com/java-hashmap-load-factor) ·
[Baeldung — A Guide to Java HashMap](https://www.baeldung.com/java-hashmap) ·
[Исходник OpenJDK — HashMap.java](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/HashMap.java)

---

## HashSet — это HashMap «под капотом»

`HashSet` — обёртка над `HashMap`: элементы множества хранятся как **ключи** внутренней `HashMap`,
а значением служит общий объект-заглушка `PRESENT`. Поэтому уникальность и сложность операций —
ровно как у `HashMap` (в среднем O(1)).

Источники: [Oracle API — HashSet](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashSet.html) ·
[Baeldung — A Guide to HashSet](https://www.baeldung.com/java-hashset)

---

## LinkedHashMap / LinkedHashSet — порядок обхода

`LinkedHashMap` = `HashMap` + дополнительный **двусвязный список**, связывающий все записи.
Это даёт предсказуемый порядок итерации:
- по умолчанию — **порядок вставки**;
- при `accessOrder = true` — **порядок доступа** (последние использованные — в конце), что позволяет
  построить **LRU-кэш**, переопределив метод `removeEldestEntry(...)`.

`LinkedHashSet` относится к `HashSet` так же, как `LinkedHashMap` к `HashMap`.

Источники: [Oracle API — LinkedHashMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html) ·
[Baeldung — Java LinkedHashMap](https://www.baeldung.com/java-linked-hashmap)

---

## TreeMap / TreeSet — красно-чёрное дерево

`TreeMap` — отсортированное отображение на основе **красно-чёрного дерева** (самобалансирующееся BST).
Порядок задаётся `Comparable` ключей или переданным `Comparator`.

- `get`/`put`/`remove` — **O(log n)**.
- Реализует `NavigableMap`: `firstKey`, `lastKey`, `floorKey`, `ceilingKey`, `headMap`, `tailMap`, `subMap`.
- `TreeSet` построен поверх `TreeMap` (как `HashSet` поверх `HashMap`).
- `null` в качестве ключа недопустим (его нельзя сравнить).

Источники: [Oracle API — TreeMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html) ·
[Baeldung — TreeMap vs HashMap](https://www.baeldung.com/java-treemap-vs-hashmap) ·
[Baeldung — Guide to TreeMap](https://www.baeldung.com/java-treemap)

---

## ConcurrentHashMap (Java 8+) — потокобезопасная хэш-таблица

С Java 8 устроена принципиально иначе, чем раньше: **отказ от сегментов** (segment lock) в пользу
блокировки на уровне отдельного бакета.

- Структура — массив бинов, как у `HashMap` (со своей treeify-логикой).
- **Запись в пустой бин** — без блокировки, через **CAS** (compare-and-swap).
- **Запись в непустой бин** — `synchronized` по **головному узлу именно этого бина** (а не всей карты),
  поэтому разные бины модифицируются параллельно.
- **Чтение — без блокировок**: поля узлов `volatile`, что гарантирует видимость последних изменений.
- `null` в качестве ключа и значения запрещён (иначе нельзя отличить «нет ключа» от «значение null»
  при конкурентном доступе). `size()` приблизителен и считается через counter cells.

Источники: [Oracle API — ConcurrentHashMap](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html) ·
[Baeldung — A Guide to ConcurrentMap](https://www.baeldung.com/java-concurrent-map) ·
[Исходник OpenJDK — ConcurrentHashMap.java](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/ConcurrentHashMap.java)

---

## CopyOnWriteArrayList — копирование при записи

Потокобезопасный список для сценариев «много чтений, мало записей». При **любой модификации**
(`add`/`set`/`remove`) создаётся **полная копия** внутреннего массива; чтения идут по неизменяемому
снимку без блокировок.

- Чтение — O(1), без синхронизации; запись — O(n) (копирование).
- Итератор работает со **снимком** на момент создания и не бросает `ConcurrentModificationException`
  (**fail-safe**), но не видит последующих изменений.

Источники: [Oracle API — CopyOnWriteArrayList](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CopyOnWriteArrayList.html) ·
[Baeldung — A Guide to CopyOnWriteArrayList](https://www.baeldung.com/java-copy-on-write-arraylist)

---

## fail-fast против fail-safe

- **fail-fast** (`ArrayList`, `HashMap`, `HashSet` …): итератор хранит счётчик структурных изменений
  `modCount`. Если коллекция изменена в обход итератора во время обхода — бросается
  `ConcurrentModificationException`. Это **обнаружение ошибки**, а не гарантия (best-effort).
- **fail-safe** (`CopyOnWriteArrayList`, `ConcurrentHashMap`): обход по снимку/без проверки `modCount`,
  исключение не бросается.

Источники: [Baeldung — Fail-Safe vs Fail-Fast Iterator](https://www.baeldung.com/java-fail-safe-vs-fail-fast-iterator)

---

## Сводка по сложности (среднее)

| Коллекция | get/доступ | add/put | remove | Упорядоченность |
|-----------|-----------|---------|--------|-----------------|
| `ArrayList` | O(1) | O(1)* в конец | O(n) | порядок вставки |
| `LinkedList` | O(n) | O(1) по концам | O(1) по концам | порядок вставки |
| `ArrayDeque` | — | O(1)* | O(1)* | порядок вставки |
| `HashMap`/`HashSet` | O(1) | O(1) | O(1) | не определена |
| `LinkedHashMap` | O(1) | O(1) | O(1) | вставки/доступа |
| `TreeMap`/`TreeSet` | O(log n) | O(log n) | O(log n) | сортировка |
| `ConcurrentHashMap` | O(1) | O(1) | O(1) | не определена |

\* — амортизированная (с учётом редких пересозданий/копирований массива).

---

## Достоверные источники (почему им можно доверять)

1. **[Oracle Java SE API Documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/package-summary.html)** —
   официальная документация: контракты и гарантии каждой коллекции из первых рук.
2. **[The Java™ Tutorials — Collections: Implementations](https://docs.oracle.com/javase/tutorial/collections/implementations/index.html)** —
   официальный учебник Oracle: доступное объяснение, какие реализации за что отвечают.
3. **[Baeldung — Java Collections](https://www.baeldung.com/java-collections)** —
   авторитетный ресурс с понятными разборами по каждой структуре и её внутренностям.
4. **[Jenkov — Java Collections](https://jenkov.com/tutorials/java-collections/index.html)** —
   простые, наглядные объяснения с диаграммами.
5. **[Исходный код OpenJDK (java.util)](https://github.com/openjdk/jdk/tree/master/src/java.base/share/classes/java/util)** —
   первоисточник «правды»: реальные константы (`TREEIFY_THRESHOLD`, `DEFAULT_LOAD_FACTOR`, `grow()` и т.д.).
