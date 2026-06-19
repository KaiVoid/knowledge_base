# Collections Framework

> **Уровень:** Junior / Middle
> **Связанные вопросы:** [Вопросы по коллекциям →](../interview-questions/collections-01.md)
> **Углублённо:** [Внутреннее устройство коллекций →](03-collections-internals.md)
> **Связанные области:** [[05-generics]], [[04-concurrency]], [[12-algorithms-data-structures]]

## Что это и зачем

Стандартная библиотека структур данных Java: списки, множества, отображения, очереди и
вспомогательные классы. Это один из самых частых блоков на собеседованиях, потому что выбор
правильной коллекции напрямую влияет на корректность и производительность кода. Нужно понимать
внутреннее устройство (как работает `HashMap`, чем `ArrayList` отличается от `LinkedList`),
сложность операций и потокобезопасные варианты.

Collections Framework появился в Java 2 (JDK 1.2) и с тех пор непрерывно развивается. В
Java 21 добавлены интерфейсы `SequencedCollection`, `SequencedSet`, `SequencedMap`,
стандартизировавшие операции с упорядоченными концевыми элементами (`getFirst()`, `getLast()`,
`reversed()`).

## Ключевые подтемы

### Иерархия интерфейсов

Collections Framework строится на двух независимых ветках наследования:

- **Ветка `Collection`**: `Collection<E>` → `List<E>`, `Set<E>`, `Queue<E>`, `Deque<E>`;
  от `Set` наследует `SortedSet` → `NavigableSet`.
- **Ветка `Map`**: `Map<K,V>` → `SortedMap` → `NavigableMap` (независимая иерархия).

Начиная с Java 21 в иерархию добавлены интерфейсы `SequencedCollection`, `SequencedSet`,
`SequencedMap`, определяющие единообразный API для доступа к первому и последнему элементам
и получения обратного представления (`reversed()`).

```
Collection<E>
  ├── List<E>          — упорядоченная последовательность, допускает дубли
  ├── Set<E>           — нет дублей
  │     └── SortedSet<E> → NavigableSet<E>
  └── Queue<E>         — очередь FIFO / с приоритетом
        └── Deque<E>   — двусторонняя очередь (стек + очередь)

Map<K,V>
  └── SortedMap<K,V> → NavigableMap<K,V>
```

**Ключевые методы `Collection`:**
`add(E)`, `remove(Object)`, `contains(Object)`, `size()`, `isEmpty()`, `iterator()`,
`toArray()`, `stream()`, `forEach(Consumer)`.

Официальная документация: [java.util — package summary](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/package-summary.html)

---

### List: ArrayList и LinkedList

#### ArrayList

`ArrayList` хранит элементы в массиве объектов (`Object[]`). При заполнении массива
создаётся новый массив (~1.5× прежней ёмкости) и данные копируются.

**Характеристики:**
- Начальная ёмкость по умолчанию — 10.
- Можно предварительно зарезервировать место: `new ArrayList<>(expectedSize)` или
  `list.ensureCapacity(n)`.
- После удаления большого числа элементов — `list.trimToSize()` для освобождения памяти.

| Операция | Сложность | Примечание |
|----------|-----------|------------|
| `get(int)`, `set(int, E)` | O(1) | прямой доступ по индексу |
| `add(E)` (в конец) | O(1) амортизированно | иногда требуется копирование массива |
| `add(int, E)`, `remove(int)` | O(n) | сдвиг всех следующих элементов |
| `contains(Object)`, `indexOf` | O(n) | линейный поиск |
| `size()`, `isEmpty()` | O(1) | |

```java
List<String> list = new ArrayList<>(100);
list.add("one");
list.add(0, "zero");   // O(n) — вставка в начало
String s = list.get(1); // O(1)
```

Java 21: реализует `SequencedCollection` — доступны `getFirst()`, `getLast()`,
`addFirst(E)`, `addLast(E)`, `removeFirst()`, `removeLast()`, `reversed()`.

Документация: [ArrayList (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)

#### LinkedList

`LinkedList` — двусвязный список. Каждый узел хранит ссылки на предыдущий и следующий
элементы. Реализует одновременно `List` и `Deque`.

| Операция | Сложность | Примечание |
|----------|-----------|------------|
| `get(int)` | O(n) | обход от начала или конца |
| `add(E)` / `addFirst(E)` / `addLast(E)` | O(1) | изменение ссылок |
| `remove(int)` | O(n) | сначала поиск узла |
| `removeFirst()` / `removeLast()` | O(1) | |

На практике `ArrayList` быстрее `LinkedList` в большинстве сценариев из-за лучшей
локальности кэша. `LinkedList` выигрывает только при очень частых вставках/удалениях
в середину большого списка, когда позиция уже известна через итератор.

---

### Set: HashSet, LinkedHashSet, TreeSet

#### HashSet

`HashSet` построен на `HashMap`: каждый элемент — ключ в скрытой хэш-таблице, значение
всегда одно и то же заглушечное значение `PRESENT`. Гарантирует уникальность элементов,
порядок итерации не определён.

| Операция | Сложность |
|----------|-----------|
| `add`, `remove`, `contains` | O(1) среднее |
| Итерация | O(capacity + size) |

```java
Set<String> set = new HashSet<>();
set.add("apple");
set.add("apple"); // проигнорировано — дубль
System.out.println(set.size()); // 1
```

Допускает один элемент `null`.

#### LinkedHashSet

Расширяет `HashSet` двусвязным списком, поддерживающим порядок вставки. Операции те же
O(1), но итерация всегда в порядке добавления. Полезен, когда нужна уникальность
и предсказуемый порядок.

#### TreeSet

Реализует `NavigableSet` на основе `TreeMap` (красно-чёрное дерево). Элементы хранятся
в отсортированном порядке (естественный или заданный `Comparator`).

| Операция | Сложность |
|----------|-----------|
| `add`, `remove`, `contains` | O(log n) |
| `first()`, `last()` | O(log n) |
| `headSet`, `tailSet`, `subSet` | O(log n) |

Не допускает `null` (если не передан специальный `Comparator`).

```java
TreeSet<Integer> ts = new TreeSet<>();
ts.add(3); ts.add(1); ts.add(2);
System.out.println(ts); // [1, 2, 3]
System.out.println(ts.headSet(3)); // [1, 2]
```

---

### Map: HashMap, LinkedHashMap, TreeMap

#### HashMap

`HashMap` — основная реализация Map; в основе лежит массив «корзин» (buckets). Каждая
корзина содержит связный список (или, начиная с Java 8, красно-чёрное дерево при длинных
цепочках).

**Внутренние параметры:**
- Начальная ёмкость: 16 корзин по умолчанию.
- Коэффициент загрузки (load factor): 0.75 — при превышении `capacity * 0.75` записей
  таблица перехэшируется с удвоением числа корзин.
- Порог «treeify» (Java 8+): цепочка длиннее 8 узлов в корзине преобразуется в
  красно-чёрное дерево для O(log n) вместо O(n) в наихудшем случае.
- Обратное преобразование в список при длине <= 6.

| Операция | Сложность |
|----------|-----------|
| `get`, `put`, `remove`, `containsKey` | O(1) среднее, O(log n) в плохом случае (Java 8+) |
| Итерация | O(capacity + size) |

```java
// Заранее указываем ёмкость, чтобы избежать перехэширований:
Map<String, Integer> map = new HashMap<>(128, 0.75f);

// Java 19+: фабричный метод с оценкой числа элементов:
Map<String, Integer> map2 = HashMap.newHashMap(100);

map.put("a", 1);
map.putIfAbsent("b", 2);
map.computeIfAbsent("c", k -> k.length());
```

Допускает один ключ `null` и значения `null`. **Не потокобезопасен.**

Документация: [HashMap (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)

#### LinkedHashMap

Расширяет `HashMap` двусвязным списком записей. Поддерживает два режима порядка:
- **Порядок вставки** (по умолчанию): элементы итерируются в том порядке, в котором были
  добавлены.
- **Порядок доступа** (`new LinkedHashMap<>(16, 0.75f, true)`): при `get` или `put`
  элемент перемещается в конец — удобно для реализации LRU-кэша.

```java
// Простейший LRU-кэш на 100 элементов:
Map<String, String> lru = new LinkedHashMap<>(128, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
        return size() > 100;
    }
};
```

#### TreeMap

`TreeMap` реализует `NavigableMap` на красно-чёрном дереве. Ключи хранятся в
отсортированном порядке (естественный `Comparable` или переданный `Comparator`).

| Операция | Сложность |
|----------|-----------|
| `get`, `put`, `remove` | O(log n) |
| `firstKey`, `lastKey` | O(log n) |
| `subMap`, `headMap`, `tailMap` | O(log n) |

`NavigableMap`-методы: `ceilingKey(k)` (>= k), `floorKey(k)` (<= k), `higherKey(k)` (> k),
`lowerKey(k)` (< k), `pollFirstEntry()`, `pollLastEntry()`, `descendingMap()`.

Не допускает `null`-ключей. **Не потокобезопасен.**

```java
TreeMap<String, Integer> tm = new TreeMap<>();
tm.put("banana", 2); tm.put("apple", 1); tm.put("cherry", 3);
System.out.println(tm.firstKey());           // apple
System.out.println(tm.subMap("b", "c"));     // {banana=2}
```

Документация: [TreeMap (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html)

---

### Сложность операций — сводная таблица

| Структура | `add` | `get(index/key)` | `contains/get` | `remove` | Порядок |
|-----------|-------|-----------------|----------------|----------|---------|
| `ArrayList` | O(1)*| O(1) | O(n) | O(n) | insertion |
| `LinkedList` | O(1) | O(n) | O(n) | O(1)** | insertion |
| `HashSet` | O(1) | — | O(1) | O(1) | нет |
| `LinkedHashSet` | O(1) | — | O(1) | O(1) | insertion |
| `TreeSet` | O(log n) | — | O(log n) | O(log n) | sorted |
| `HashMap` | O(1) | O(1) | O(1) | O(1) | нет |
| `LinkedHashMap` | O(1) | O(1) | O(1) | O(1) | insertion/access |
| `TreeMap` | O(log n) | O(log n) | O(log n) | O(log n) | sorted |
| `PriorityQueue` | O(log n) | — | O(n) | O(log n) | priority |
| `ArrayDeque` | O(1)* | — | O(n) | O(1) | insertion |

\* амортизированно; \*\* при известном узле через итератор

---

### Итераторы: fail-fast vs fail-safe

**Fail-fast итераторы** (все стандартные коллекции `java.util`) отслеживают число
структурных модификаций через поле `modCount`. Если после создания итератора коллекция
изменяется снаружи (не через `Iterator.remove()`), при следующем вызове `next()` или
`remove()` бросается `ConcurrentModificationException`.

Это поведение на основе усилий (best-effort): документация явно указывает, что **не следует
писать код, рассчитывающий на это исключение** — оно предназначено только для обнаружения
ошибок, а не для гарантированной синхронизации.

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
Iterator<String> it = list.iterator();
list.add("d");       // структурная модификация
it.next();           // ConcurrentModificationException!

// Правильное удаление во время итерации:
it = list.iterator();
while (it.hasNext()) {
    if (it.next().equals("b")) it.remove(); // безопасно
}
```

**Fail-safe итераторы** (классы из `java.util.concurrent`) работают со снимком (snapshot)
данных или не отслеживают `modCount`. `ConcurrentModificationException` не бросают, но
могут не отразить свежие изменения:

- `CopyOnWriteArrayList.iterator()` — итератор по снимку массива на момент создания; метод
  `remove()` не поддерживается.
- `ConcurrentHashMap.entrySet().iterator()` — weakly consistent: отражает состояние в
  некоторый момент без гарантии видимости всех параллельных обновлений.

---

### Потокобезопасные коллекции

Все стандартные коллекции `java.util` (кроме `Vector`, `Hashtable`, `Stack`) **не
потокобезопасны**. Для многопоточного использования есть три подхода:

#### 1. Collections.synchronizedXxx — обёртки

```java
List<String> safe = Collections.synchronizedList(new ArrayList<>());
Map<String, Integer> safeMap = Collections.synchronizedMap(new HashMap<>());
```

Каждый метод синхронизирован по объекту-обёртке. **Итерация требует явной синхронизации:**

```java
synchronized (safe) {
    for (String s : safe) { /* ... */ }
}
```

Подходит для низкой нагрузки; не масштабируется при высокой конкуренции.

#### 2. ConcurrentHashMap

Высокопроизводительная потокобезопасная реализация `Map`. С Java 8 использует
CAS-операции и синхронизацию на уровне отдельных корзин (не таблицы целиком).

- Операции чтения (`get`) **не блокируются** совсем.
- Записи синхронизируются на уровне одной корзины.
- Итераторы weakly consistent — не бросают `ConcurrentModificationException`.
- **Запрещены ключи и значения `null`** (в отличие от `HashMap`).
- Атомарные методы: `putIfAbsent`, `remove(k, v)`, `replace(k, old, new)`,
  `computeIfAbsent`, `merge`.

```java
ConcurrentHashMap<String, Integer> counts = new ConcurrentHashMap<>();
counts.merge("hits", 1, Integer::sum); // атомарный инкремент счётчика
```

Документация: [ConcurrentHashMap (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)

#### 3. CopyOnWriteArrayList / CopyOnWriteArraySet

При каждой мутирующей операции (`add`, `set`, `remove`) создаётся **полная копия внутреннего
массива**. Читатели всегда работают с неизменяемым снимком — без блокировок и без
`ConcurrentModificationException`.

- Чтение: O(1), без синхронизации.
- Запись: O(n) — полное копирование массива. Дорого при высокой частоте изменений.
- Итератор по снимку: не видит изменений после своего создания; `remove()` не поддерживает.

**Когда применять:** списки слушателей/наблюдателей, конфигурационные списки — когда читают
часто, изменяют редко.

```java
CopyOnWriteArrayList<EventListener> listeners = new CopyOnWriteArrayList<>();
// Безопасно итерировать без synchronized-блока:
for (EventListener l : listeners) { l.onEvent(e); }
```

Документация: [CopyOnWriteArrayList (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CopyOnWriteArrayList.html)

#### 4. BlockingQueue

Интерфейс `BlockingQueue` (пакет `java.util.concurrent`) предназначен для
паттерна «производитель — потребитель». Операции:

| Форма | Вставка | Извлечение |
|-------|---------|------------|
| Исключение при невозможности | `add(e)` | `remove()` |
| Специальное значение | `offer(e)` | `poll()` |
| Блокировка | `put(e)` | `take()` |
| С таймаутом | `offer(e, t, u)` | `poll(t, u)` |

`null` не допускается. Основные реализации:
- `ArrayBlockingQueue` — ограниченная очередь на массиве.
- `LinkedBlockingQueue` — опционально ограниченная очередь на связном списке (обычно
  выше пропускная способность).
- `PriorityBlockingQueue` — с приоритетом.
- `SynchronousQueue` — нулевая ёмкость; каждый `put` ждёт `take`.

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);
// Производитель:
queue.put(new Task());   // ждёт, если очередь полна
// Потребитель:
Task t = queue.take();   // ждёт, если очередь пуста
```

Документация: [BlockingQueue (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/BlockingQueue.html)

---

### Comparable vs Comparator

**`Comparable<T>`** (пакет `java.lang`) — «естественный порядок» объекта; реализуется
самим классом через метод `compareTo(T o)`. Например, `String`, `Integer`, `LocalDate`
реализуют `Comparable`.

**`Comparator<T>`** (пакет `java.util`) — внешняя стратегия сравнения; позволяет задать
альтернативный порядок без изменения класса.

```java
// Comparable — класс определяет порядок сам
public class Product implements Comparable<Product> {
    @Override
    public int compareTo(Product other) {
        return Double.compare(this.price, other.price);
    }
}

// Comparator — внешний порядок, можно комбинировать:
Comparator<Product> byName = Comparator.comparing(Product::getName);
Comparator<Product> byPriceThenName =
    Comparator.comparingDouble(Product::getPrice)
              .thenComparing(Product::getName);

list.sort(byPriceThenName);
```

Правило для `TreeMap`/`TreeSet`: порядок, задаваемый `compareTo`/`compare`, должен быть
**согласован с `equals`** — если `a.compareTo(b) == 0`, то `a.equals(b)` должно быть
`true`; нарушение этого приводит к неожиданному поведению.

---

### Вспомогательный класс Collections и фабричные методы

**`Collections`** содержит статические полиморфные алгоритмы:

| Метод | Описание |
|-------|----------|
| `sort(List)` / `sort(List, Comparator)` | стабильная сортировка O(n log n) |
| `binarySearch(List, key)` | бинарный поиск (список должен быть отсортирован) |
| `reverse(List)` | обращение порядка |
| `shuffle(List)` | случайное перемешивание |
| `min(Collection)` / `max(Collection)` | минимум/максимум по естественному порядку |
| `frequency(Collection, obj)` | число вхождений |
| `disjoint(c1, c2)` | `true`, если у коллекций нет общих элементов |
| `fill(List, obj)` | заполнение всех позиций значением |
| `copy(dest, src)` | копирование src в dest |
| `unmodifiableXxx(c)` | обёртка только для чтения |
| `synchronizedXxx(c)` | потокобезопасная обёртка |
| `checkedXxx(c, type)` | типобезопасная обёртка с проверкой в рантайме |
| `singletonList(obj)` / `singleton(obj)` | неизменяемый список/множество из одного элемента |
| `emptyList()` / `emptySet()` / `emptyMap()` | неизменяемые пустые коллекции |
| `nCopies(n, obj)` | неизменяемый список из n копий объекта |

**Фабричные методы `List.of`, `Set.of`, `Map.of` (Java 9+):**

```java
List<String> immutable = List.of("a", "b", "c");
Set<Integer> nums = Set.of(1, 2, 3);
Map<String, Integer> m = Map.of("one", 1, "two", 2);
// Не допускают null и не поддерживают изменения (UnsupportedOperationException)
```

`Map.copyOf(map)`, `List.copyOf(list)`, `Set.copyOf(set)` — создают неизменяемые копии.

---

### Специализированные коллекции

- **`EnumSet<E>`** — битовая маска для enum-значений; O(1) по всем операциям; крайне
  эффективен по памяти. Фабрика: `EnumSet.of(Day.MON, Day.WED)`.
- **`EnumMap<K,V>`** — массив, индексированный порядковым номером enum. Быстрее `HashMap`
  для enum-ключей.
- **`WeakHashMap<K,V>`** — ключи хранятся через `WeakReference`; запись удаляется, когда
  на ключ нет сильных ссылок. Применяется для кэшей без риска утечки памяти.
- **`IdentityHashMap<K,V>`** — сравнивает ключи через `==` вместо `equals`; редко нужен,
  но полезен для реализации сериализации/десериализации и обхода графов объектов.
- **`ArrayDeque<E>`** — кольцевой буфер, реализует `Deque`; рекомендован как замена
  `Stack` и `LinkedList`-в-роли-очереди благодаря лучшей производительности.
- **`PriorityQueue<E>`** — двоичная куча; `poll()` всегда возвращает наименьший элемент
  по порядку. Не потокобезопасен; потокобезопасный аналог — `PriorityBlockingQueue`.

## Достоверные источники

1. **[The Java Tutorials — Collections](https://docs.oracle.com/javase/tutorial/collections/index.html)**
   — официальный учебник Oracle по Collections Framework: интерфейсы, реализации, алгоритмы,
   пользовательские реализации. Основной вводный материал от создателей платформы.

2. **[Java 21 API — java.util package](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/package-summary.html)**
   — JavaDoc со всеми интерфейсами и классами пакета `java.util`, включая новые
   `SequencedCollection`/`SequencedMap`/`SequencedSet`. Первичный источник истины по
   контрактам методов.

3. **[Java 21 API — java.util.concurrent package](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html)**
   — JavaDoc потокобезопасных коллекций: `ConcurrentHashMap`, `CopyOnWriteArrayList`,
   `BlockingQueue` и их реализаций. Официальная документация с гарантиями happens-before.

4. **[HashMap JavaDoc (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)**
   — детальное описание внутреннего устройства: load factor, treeify threshold,
   рекомендации по выбору начальной ёмкости, поведение итераторов.

5. **[Baeldung — Java Collections](https://www.baeldung.com/java-collections)**
   — серия практических статей по отдельным коллекциям с примерами кода. Авторитетный
   ресурс, активно ссылающийся на официальную документацию; полезен для углублённого
   разбора конкретных тем.

6. **[Jenkov — Java Collections Tutorial](https://jenkov.com/tutorials/java-collections/index.html)**
   — структурированный разбор иерархии коллекций с визуализациями. Независимый автор
   (Jakob Jenkov), публикует материалы с 2008 года; статьи регулярно обновляются.
