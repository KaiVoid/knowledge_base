# Алгоритмы и структуры данных

> **Уровень:** Junior / Middle / Senior
> **Связанные вопросы:** [Вопросы по алгоритмам →](../interview-questions/algorithms-01.md)
> **Связанные области:** [[03-collections]]

## Что это и зачем

База компьютерных наук: структуры данных (массивы, списки, деревья, графы, хэш-таблицы) и алгоритмы
(сортировки, поиск, обходы), а также оценка сложности (Big-O). Это знание необходимо для выбора
правильных коллекций, написания эффективного кода и прохождения алгоритмических секций собеседований
(особенно в крупных компаниях).

Понимание алгоритмов и структур данных напрямую влияет на повседневную работу Java-разработчика:
выбор между `ArrayList` и `LinkedList`, между `HashMap` и `TreeMap`, между рекурсией и итерацией —
всё это прикладные последствия теоретических знаний. Java стандартная библиотека (`java.util`)
реализует большинство классических структур данных, и их Javadoc явно указывает гарантии сложности.

---

## Ключевые подтемы

### Оценка сложности: Big-O

Big-O нотация описывает верхнюю границу роста времени выполнения или объёма памяти алгоритма
в зависимости от размера входных данных. Берётся доминирующий терм, константы отбрасываются.

**Основные классы сложности (от лучшего к худшему):**

| Класс | Название | Пример |
|-------|----------|--------|
| O(1) | Константная | Доступ к элементу массива по индексу, `HashMap.get()` |
| O(log n) | Логарифмическая | Бинарный поиск, операции `TreeMap` |
| O(n) | Линейная | Линейный поиск, обход списка |
| O(n log n) | Линеаритмическая | Merge Sort, Heap Sort, `Arrays.sort()` |
| O(n^2) | Квадратичная | Bubble Sort, вложенные циклы по одному массиву |
| O(2^n) | Экспоненциальная | Перебор всех подмножеств, наивная рекурсия Фибоначчи |
| O(n!) | Факториальная | Перебор всех перестановок |

**Правила вычисления:**
- **Отбрасывание констант:** O(3n) = O(n).
- **Отбрасывание младших членов:** O(n^2 + n) = O(n^2).
- **Правило суммы (последовательные блоки):** O(f(n)) + O(g(n)) = O(max(f(n), g(n))).
- **Правило произведения (вложенные циклы):** O(f(n)) * O(g(n)) = O(f(n) * g(n)).

**Случаи анализа:**
- **Лучший (Omega, Ω)** — оптимистичный сценарий (уже отсортированный массив для Insertion Sort: O(n)).
- **Средний (Theta, Θ)** — ожидаемый сценарий на случайных данных.
- **Худший (Big-O)** — пессимистичный сценарий; именно его принято указывать по умолчанию.

Источник: [GeeksforGeeks — Big-O Analysis](https://www.geeksforgeeks.org/dsa/analysis-algorithms-big-o-analysis/)

---

### Базовые структуры данных

#### Массив (Array)

Непрерывный блок памяти. Доступ по индексу — O(1). Вставка/удаление в середину — O(n) (сдвиг
элементов). В Java: `int[]`, `String[]`, а также `ArrayList` (динамический массив).

```java
int[] arr = {3, 1, 4, 1, 5};
int val = arr[2]; // O(1)
```

#### Связный список (Linked List)

Узлы, связанные указателями. В Java — `java.util.LinkedList` — двусвязный список, реализующий
одновременно `List<E>` и `Deque<E>`.

| Операция | Сложность |
|----------|-----------|
| Добавление/удаление с начала или конца | O(1) |
| Доступ по индексу | O(n) |
| Поиск элемента | O(n) |

> Из Javadoc `LinkedList` (Java 21): операции индексирования обходят список с ближайшего конца
> к указанному индексу. Не потокобезопасен; для многопоточного доступа:
> `Collections.synchronizedList(new LinkedList<>())`.

Источник: [Oracle Javadoc — LinkedList (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html)

#### Стек (Stack) и очередь (Queue)

**Стек (LIFO):** в Java реализуется через `Deque`. `ArrayDeque` — рекомендуемая реализация,
быстрее `Stack` и `LinkedList` для стека.

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);       // addFirst
int top = stack.pop(); // removeFirst
```

**Очередь (FIFO):** также `ArrayDeque` или `LinkedList`.

```java
Queue<Integer> queue = new ArrayDeque<>();
queue.offer(1);        // addLast
int head = queue.poll(); // removeFirst
```

Все операции на `ArrayDeque` при работе с концами — O(1) амортизированная.

#### Хэш-таблица (Hash Table)

В Java — `java.util.HashMap`. Основана на массиве бакетов; коллизии разрешаются цепочками
(с Java 8 — переходом на красно-чёрное дерево при длине цепочки >= 8).

| Операция | Средняя сложность | Худшая сложность |
|----------|-------------------|------------------|
| `get(key)` | O(1) | O(n) |
| `put(key, value)` | O(1) | O(n) |
| `remove(key)` | O(1) | O(n) |
| Итерация | O(n + capacity) | O(n + capacity) |

Ключевые параметры из Javadoc:
- **Initial capacity** — начальный размер таблицы (по умолчанию 16).
- **Load factor** — порог заполнения (по умолчанию 0.75). При превышении `loadFactor * capacity`
  происходит **rehash** с удвоением ёмкости.

> "This implementation provides constant-time performance for the basic operations (get and put),
> assuming the hash function disperses the elements properly among the buckets."
> — Oracle Javadoc, HashMap (Java 21)

```java
// Для заранее известного числа элементов — указывать начальную ёмкость
HashMap<String, Integer> map = new HashMap<>(expectedSize * 4 / 3 + 1);
// Или с Java 19+:
HashMap<String, Integer> map2 = HashMap.newHashMap(expectedMappings);
```

Источник: [Oracle Javadoc — HashMap (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)

---

### Деревья

#### Бинарное дерево поиска (BST)

Для каждого узла все ключи левого поддерева меньше, правого — больше.

| Операция | Сбалансированное | Несбалансированное (вырожденное) |
|----------|------------------|---------------------------------|
| Поиск | O(log n) | O(n) |
| Вставка | O(log n) | O(n) |
| Удаление | O(log n) | O(n) |

В худшем случае (ключи вставляются в возрастающем/убывающем порядке) BST вырождается в связный
список.

Источник: [GeeksforGeeks — BST Data Structure](https://www.geeksforgeeks.org/dsa/binary-search-tree-data-structure/)

#### Сбалансированные деревья: AVL и красно-чёрное (Red-Black Tree)

**AVL-дерево** — строгая балансировка: разница высот левого и правого поддеревьев у каждого
узла не превышает 1. Вставка и удаление требуют ротаций, что даёт более медленную запись, но
чуть более быстрый поиск по сравнению с красно-чёрным деревом.

**Красно-чёрное дерево (Red-Black Tree)** — мягкая балансировка через инварианты окраски узлов
(красный/чёрный). Гарантирует, что высота дерева не превышает 2 * log(n+1). Используется в JDK:

- `java.util.TreeMap` — красно-чёрное дерево, ключи хранятся в отсортированном порядке.
- `java.util.TreeSet` — множество на основе `TreeMap`.
- Бакеты `HashMap` при длине цепочки >= 8 (Java 8+).

> "This implementation provides guaranteed log(n) time cost for the containsKey, get, put and
> remove operations."
> — Oracle Javadoc, TreeMap (Java 21)

```java
// TreeMap — O(log n) для всех ключевых операций, ключи отсортированы
TreeMap<String, Integer> treeMap = new TreeMap<>();
treeMap.put("banana", 2);
treeMap.put("apple", 1);
System.out.println(treeMap.firstKey()); // "apple" — NavigableMap API
```

Источник: [Oracle Javadoc — TreeMap (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html)

#### Куча (Heap) и PriorityQueue

**Куча** — полное бинарное дерево, удовлетворяющее свойству кучи:
- **Min-Heap:** значение каждого родителя <= значений его потомков; минимум — в корне.
- **Max-Heap:** значение каждого родителя >= значений его потомков; максимум — в корне.

В Java — `java.util.PriorityQueue`, реализованная на основе min-heap.

| Операция | Сложность |
|----------|-----------|
| `offer(E)` / `add(E)` | O(log n) |
| `poll()` — извлечь минимум | O(log n) |
| `peek()` — прочитать минимум | O(1) |
| `remove(Object)` | O(n) — линейный поиск |
| `contains(Object)` | O(n) |

```java
// Min-heap по умолчанию
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5);
minHeap.offer(1);
minHeap.offer(3);
System.out.println(minHeap.poll()); // 1

// Max-heap через reverseOrder
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
```

> Итераторы `PriorityQueue` не гарантируют порядок. Для потокобезопасной очереди использовать
> `java.util.concurrent.PriorityBlockingQueue`.

Источник: [Oracle Javadoc — PriorityQueue (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html)

---

### Графы

#### Представление графов

**Матрица смежности (Adjacency Matrix):**
- 2D-массив V×V, `matrix[i][j] = 1` если есть ребро i→j.
- Пространство: O(V^2).
- Проверка наличия ребра: O(1).
- Итерация по соседям вершины: O(V).
- Подходит для **плотных** графов (много рёбер).

**Список смежности (Adjacency List):**
- Массив/список из V списков; каждый хранит соседей вершины.
- Пространство: O(V + E).
- Итерация по соседям вершины: O(degree(v)).
- Подходит для **разреженных** графов.

```java
// Список смежности в Java
int V = 5;
List<List<Integer>> adj = new ArrayList<>();
for (int i = 0; i < V; i++) adj.add(new ArrayList<>());
adj.get(0).add(1); // ребро 0 -> 1
adj.get(0).add(2); // ребро 0 -> 2
```

#### Обходы графа: BFS и DFS

**BFS (Breadth-First Search) — обход в ширину:**
- Использует **очередь (Queue)**.
- Посещает все вершины на расстоянии k до вершин на расстоянии k+1.
- Находит **кратчайший путь** в невзвешенном графе.
- Временная сложность: O(V + E). Пространственная: O(V) (очередь может содержать до V вершин).

```java
void bfs(List<List<Integer>> adj, int start) {
    boolean[] visited = new boolean[adj.size()];
    Queue<Integer> queue = new ArrayDeque<>();
    visited[start] = true;
    queue.offer(start);
    while (!queue.isEmpty()) {
        int v = queue.poll();
        System.out.print(v + " ");
        for (int neighbor : adj.get(v)) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                queue.offer(neighbor);
            }
        }
    }
}
```

**DFS (Depth-First Search) — обход в глубину:**
- Использует **стек (Stack)** (явно или через рекурсию / стек вызовов).
- Уходит как можно глубже перед возвратом.
- Применяется для: топологической сортировки, поиска циклов, компонент связности.
- Временная сложность: O(V + E). Пространственная (рекурсия): O(V) в худшем случае.

```java
void dfs(List<List<Integer>> adj, int v, boolean[] visited) {
    visited[v] = true;
    System.out.print(v + " ");
    for (int neighbor : adj.get(v)) {
        if (!visited[neighbor]) {
            dfs(adj, neighbor, visited);
        }
    }
}
```

| Характеристика | BFS | DFS |
|----------------|-----|-----|
| Структура данных | Очередь | Стек / рекурсия |
| Кратчайший путь (невзвешенный) | Да | Нет |
| Память (худший случай) | O(V) | O(V) |
| Топологическая сортировка | Нет (Kahn's) | Да |
| Применение | Shortest path, level order | Цикл, компоненты, топосорт |

Источник: [GeeksforGeeks — BFS complexity](https://www.geeksforgeeks.org/dsa/time-and-space-complexity-of-dfs-and-bfs-algorithm/)

---

### Алгоритмы сортировки

#### Сравнительная таблица

| Алгоритм | Лучший | Средний | Худший | Память | Стабильный |
|----------|--------|---------|--------|--------|-----------|
| Bubble Sort | O(n) | O(n^2) | O(n^2) | O(1) | Да |
| Selection Sort | O(n^2) | O(n^2) | O(n^2) | O(1) | Нет |
| Insertion Sort | O(n) | O(n^2) | O(n^2) | O(1) | Да |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Да |
| Quick Sort | O(n log n) | O(n log n) | O(n^2) | O(log n) | Нет |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | Нет |

Источник: [GeeksforGeeks — Analysis of Sorting Techniques](https://www.geeksforgeeks.org/dsa/analysis-of-different-sorting-techniques/)

**Практические рекомендации:**
- **Insertion Sort** эффективен на почти отсортированных данных (O(n) в лучшем случае).
- **Merge Sort** — стабильный, гарантированный O(n log n) — предпочтительна при неизвестном входе.
- **Quick Sort** — быстрее на практике благодаря хорошей работе с кешем, но деградирует до O(n^2)
  при плохом выборе опорного элемента.

#### Сортировки в JDK: Arrays.sort и Collections.sort

`Arrays.sort()` использует разные алгоритмы в зависимости от типа данных:

**Для примитивов (`int[]`, `long[]`, ...):**
- **Dual-Pivot Quicksort** (Yaroslavskiy, Bentley, Bloch).
- O(n log n) на всех наборах данных. Не стабилен (для примитивов стабильность несущественна).

**Для объектов (`Object[]`, `List<T>`):**
- **Timsort** — гибрид Merge Sort и Insertion Sort; адаптирован из Python.
- **Стабилен** — равные элементы не меняют относительный порядок.
- O(n log n) в худшем случае; O(n) на почти отсортированных данных.

> "The sorting algorithm is a Dual-Pivot Quicksort by Vladimir Yaroslavskiy, Jon Bentley,
> and Joshua Bloch. This algorithm offers O(n log(n)) performance on all data sets, and is
> typically faster than traditional (one-pivot) Quicksort implementations."
> — Oracle Javadoc, Arrays.sort(int[]) (Java 21)

```java
int[] primitives = {5, 3, 1, 4, 2};
Arrays.sort(primitives); // Dual-Pivot Quicksort, не стабилен

String[] objects = {"banana", "apple", "cherry"};
Arrays.sort(objects);    // Timsort, стабилен

List<String> list = Arrays.asList("banana", "apple", "cherry");
Collections.sort(list);  // Делегирует в Arrays.sort — Timsort
```

Источник: [Oracle Javadoc — Arrays.sort (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html)

---

### Алгоритмические приёмы

#### Два указателя (Two Pointers)

Два индекса, движущихся по одному массиву/строке: навстречу друг другу или в одном направлении
с разными скоростями. Сокращает O(n^2) до O(n).

```java
// Пример: два указателя навстречу для проверки палиндрома
boolean isPalindrome(String s) {
    int left = 0, right = s.length() - 1;
    while (left < right) {
        if (s.charAt(left) != s.charAt(right)) return false;
        left++;
        right--;
    }
    return true;
}
```

Типичные задачи: Two Sum (отсортированный массив), нахождение пар с заданной суммой, удаление
дубликатов из отсортированного массива.

#### Скользящее окно (Sliding Window)

Специализация двух указателей: окно фиксированного или переменного размера перемещается по
массиву/строке. Вычисления переиспользуют результат предыдущего шага, что даёт O(n) вместо O(n*k).

```java
// Максимальная сумма подмассива фиксированной длины k
int maxSumSubarray(int[] arr, int k) {
    int windowSum = 0;
    for (int i = 0; i < k; i++) windowSum += arr[i];
    int maxSum = windowSum;
    for (int i = k; i < arr.length; i++) {
        windowSum += arr[i] - arr[i - k];
        maxSum = Math.max(maxSum, windowSum);
    }
    return maxSum;
}
```

#### Динамическое программирование (Dynamic Programming, DP)

Разбивает задачу на перекрывающиеся подзадачи, кэширует результаты, избегает повторных вычислений.
Сводит экспоненциальную сложность к полиномиальной.

**Два подхода:**
- **Memoization (top-down):** рекурсия с кешем (обычно `Map` или массив).
- **Tabulation (bottom-up):** итеративное заполнение таблицы от малых подзадач к большим.

**Признаки применимости DP:**
1. **Overlapping subproblems** — одни и те же подзадачи решаются многократно.
2. **Optimal substructure** — оптимальное решение задачи включает оптимальные решения подзадач.

```java
// Числа Фибоначчи: memoization
Map<Integer, Long> memo = new HashMap<>();
long fib(int n) {
    if (n <= 1) return n;
    if (memo.containsKey(n)) return memo.get(n);
    long result = fib(n - 1) + fib(n - 2);
    memo.put(n, result);
    return result;
}

// Числа Фибоначчи: tabulation
long fibTabulation(int n) {
    if (n <= 1) return n;
    long[] dp = new long[n + 1];
    dp[1] = 1;
    for (int i = 2; i <= n; i++) dp[i] = dp[i - 1] + dp[i - 2];
    return dp[n];
}
```

Классические задачи DP: Fibonacci, Longest Common Subsequence (LCS), 0/1 Knapsack, Edit Distance,
Coin Change, Longest Increasing Subsequence (LIS).

Источник: [GeeksforGeeks — Dynamic Programming](https://www.geeksforgeeks.org/dsa/dynamic-programming/)

#### Бинарный поиск (Binary Search)

Ищет элемент в **отсортированном** массиве за O(log n), разделяя пространство поиска пополам.

```java
int binarySearch(int[] arr, int target) {
    int left = 0, right = arr.length - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2; // без переполнения
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
```

В JDK: `Arrays.binarySearch()` и `Collections.binarySearch()` — O(log n), требуют отсортированного
ввода.

---

## Достоверные источники

1. **[GeeksforGeeks — DSA Tutorial](https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/)** —
   обширный справочник структур данных и алгоритмов с разбором сложности и примерами кода.
   Авторитетный ресурс в области CS-образования.

2. **[GeeksforGeeks — Big-O Analysis](https://www.geeksforgeeks.org/dsa/analysis-algorithms-big-o-analysis/)** —
   детальный разбор нотации Big-O, классов сложности, правил вычисления и примеров.

3. **[GeeksforGeeks — Analysis of Sorting Techniques](https://www.geeksforgeeks.org/dsa/analysis-of-different-sorting-techniques/)** —
   сравнительная таблица сложности (лучший/средний/худший) и стабильности классических алгоритмов
   сортировки.

4. **[Oracle Javadoc — java.util (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/package-summary.html)** —
   официальная документация JDK: `HashMap`, `TreeMap`, `LinkedList`, `PriorityQueue`, `Arrays`.
   Указывает гарантии сложности операций, что важнее любых учебных источников.

5. **[Oracle Javadoc — Arrays.sort (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html)** —
   официальное описание алгоритмов (Dual-Pivot Quicksort для примитивов, Timsort для объектов),
   гарантий сложности и стабильности.

6. **Книга «Introduction to Algorithms» (Cormen, Leiserson, Rivest, Stein — CLRS)** —
   академический первоисточник: строгие доказательства сложности, псевдокод алгоритмов сортировки,
   обходов графов, DP. Упоминается в Javadoc `TreeMap` как основа реализации.
