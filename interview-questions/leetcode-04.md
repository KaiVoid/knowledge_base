# Задачи LeetCode — часть 04 (Medium)

### Вопрос 52. LC 124. Максимальная сумма пути в дереве (Binary Tree Maximum Path Sum)

**Категория:** Алгоритмы и структуры данных · Деревья / DFS · **Уровень:** Medium

Дано бинарное дерево. **Путь** — это последовательность узлов, в которой каждая пара соседних узлов
соединена ребром; каждый узел встречается в пути не более одного раза. Путь не обязан проходить
через корень. **Суммой пути** называется сумма значений всех его узлов.
Верните максимальную сумму пути среди всех возможных путей в дереве.

**Пример 1.** Вход: `root = [1,2,3]` → Выход: `6` — оптимальный путь `2 → 1 → 3` с суммой 6.
**Пример 2.** Вход: `root = [-10,9,20,null,null,15,7]` → Выход: `42` — оптимальный путь `15 → 20 → 7`.
**Ограничения:** число узлов в `[1, 3*10^4]`; `-1000 <= Node.val <= 1000`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Binary Tree Maximum Path Sum](https://github.com/doocs/leetcode/blob/main/solution/0100-0199/0124.Binary%20Tree%20Maximum%20Path%20Sum/README.md)

Подход: постобходный DFS. Для каждого узла вычисляем максимальный «однонаправленный» вклад
от левого и правого поддеревьев (не берём отрицательные ветви, заменяем на 0). Через текущий узел
может проходить путь, соединяющий оба поддерева: `ans = max(ans, node.val + left + right)`.
Функция возвращает только лучший однонаправленный вклад (не оба поддерева сразу — иначе путь
нельзя продолжить вверх). Время O(n), память O(n).

```java
class Solution {
    private int ans = -1001;

    public int maxPathSum(TreeNode root) {
        dfs(root);
        return ans;
    }

    private int dfs(TreeNode root) {
        if (root == null) {
            return 0;
        }
        int left = Math.max(0, dfs(root.left));
        int right = Math.max(0, dfs(root.right));
        ans = Math.max(ans, root.val + left + right);
        return root.val + Math.max(left, right);
    }
}
```

#### Ответ от Claude

**Идея.** Классический постобходный DFS с двойным смыслом возвращаемого значения.
Функция `gain(node)` делает две вещи одновременно:
1. Обновляет глобальный максимум, рассматривая `node` как «вершину» пути (соединяя оба поддерева).
2. Возвращает наилучший однонаправленный вклад, который может использовать родительский узел.

Ключевой момент: отрицательные вклады заменяем нулём — лучше не включать поддерево вообще.

```java
public class Solution {
    private int globalMax;

    public int maxPathSum(TreeNode root) {
        globalMax = Integer.MIN_VALUE;
        gain(root);
        return globalMax;
    }

    /**
     * Возвращает наилучший однонаправленный вклад поддерева с корнем node.
     * Побочный эффект: обновляет globalMax, рассматривая node как вершину пути.
     */
    private int gain(TreeNode node) {
        if (node == null) return 0;

        // Отрицательный вклад хуже, чем его отсутствие
        int leftGain  = Math.max(0, gain(node.left));
        int rightGain = Math.max(0, gain(node.right));

        // Путь через этот узел как «вершину»: соединяем оба направления
        int pathThroughNode = node.val + leftGain + rightGain;
        globalMax = Math.max(globalMax, pathThroughNode);

        // Родителю возвращаем только одно направление (иначе путь разветвится)
        return node.val + Math.max(leftGain, rightGain);
    }
}
```

**Разбор по шагам.**
1. Обходим дерево снизу вверх (постфиксный обход).
2. На каждом узле `u`: левый вклад = `max(0, gain(u.left))`, правый = `max(0, gain(u.right))`.
3. Кандидат на ответ через `u`: `u.val + left + right` — обновляем `globalMax`.
4. Родителю возвращаем `u.val + max(left, right)` — только одно направление.
5. Инициализируем `globalMax = Integer.MIN_VALUE`, чтобы корректно обработать дерево
   из одного отрицательного узла.

**Сложность.** Время O(n) — каждый узел посещается ровно один раз. Память O(n) — стек
рекурсии в худшем случае (вырожденное дерево — цепочка).

**Типичные ошибки / альтернативы.**
- Инициализация `globalMax = 0` — ошибка: пропустит дерево из одних отрицательных значений.
- Возврат `leftGain + rightGain` из `gain` — ошибка: разветвлённый путь нельзя продолжить вверх.
- Итеративная реализация через явный стек принципиально сложнее; рекурсия здесь предпочтительна.
- Совпадение: источник doocs использует поле класса `ans = -1001` (минимум при `val >= -1000`);
  решение Claude использует `Integer.MIN_VALUE` — более универсально.

---

### Вопрос 53. LC 297. Сериализация дерева (Serialize and Deserialize Binary Tree)

**Категория:** Алгоритмы и структуры данных · Деревья / дизайн · **Уровень:** Medium

Спроектируйте алгоритм для сериализации и десериализации бинарного дерева.
Сериализация — преобразование дерева в строку. Десериализация — восстановление дерева из строки.
Формат строки выбирайте самостоятельно; главное — чтобы `deserialize(serialize(root))` возвращал
то же дерево.

**Пример 1.** Вход: `root = [1,2,3,null,null,4,5]` → `serialize` → некоторая строка →
`deserialize` → исходное дерево.
**Пример 2.** Вход: `root = []` → Выход: `[]`.
**Ограничения:** число узлов в `[0, 10^4]`; `-1000 <= Node.val <= 1000`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Serialize and Deserialize Binary Tree](https://github.com/doocs/leetcode/blob/main/solution/0200-0299/0297.Serialize%20and%20Deserialize%20Binary%20Tree/README.md)

Подход BFS (обход в ширину): сериализация — стандартный BFS-обход очередью; `null`-узлы
кодируются символом `#`; значения разделяются запятой. Десериализация разбивает строку,
восстанавливает узлы в том же порядке BFS. Время O(n), память O(n).

```java
public class Codec {

    public String serialize(TreeNode root) {
        if (root == null) {
            return null;
        }
        List<String> ans = new ArrayList<>();
        Deque<TreeNode> q = new LinkedList<>();
        q.offer(root);
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            if (node != null) {
                ans.add(node.val + "");
                q.offer(node.left);
                q.offer(node.right);
            } else {
                ans.add("#");
            }
        }
        return String.join(",", ans);
    }

    public TreeNode deserialize(String data) {
        if (data == null) {
            return null;
        }
        String[] vals = data.split(",");
        int i = 0;
        TreeNode root = new TreeNode(Integer.parseInt(vals[i++]));
        Deque<TreeNode> q = new ArrayDeque<>();
        q.offer(root);
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            if (!"#".equals(vals[i])) {
                node.left = new TreeNode(Integer.parseInt(vals[i]));
                q.offer(node.left);
            }
            ++i;
            if (!"#".equals(vals[i])) {
                node.right = new TreeNode(Integer.parseInt(vals[i]));
                q.offer(node.right);
            }
            ++i;
        }
        return root;
    }
}
```

#### Ответ от Claude

**Идея.** Используем предобходный DFS (preorder: корень → лево → право) вместо BFS.
Преимущества: не требует очереди, рекурсивный код компактен, легко читается.
Нулевые поддеревья кодируем маркером `"N"`. При десериализации глобальный индекс
двигается вместе с рекурсией.

```java
public class Codec {

    private static final String NULL_MARKER = "N";
    private static final String SEP = ",";

    // Сериализация: preorder DFS, null -> "N"
    public String serialize(TreeNode root) {
        StringBuilder sb = new StringBuilder();
        encode(root, sb);
        // Убираем trailing запятую
        if (sb.length() > 0) sb.setLength(sb.length() - 1);
        return sb.toString();
    }

    private void encode(TreeNode node, StringBuilder sb) {
        if (node == null) {
            sb.append(NULL_MARKER).append(SEP);
            return;
        }
        sb.append(node.val).append(SEP);
        encode(node.left, sb);
        encode(node.right, sb);
    }

    // Десериализация: тот же preorder, указатель pos в массиве токенов
    public TreeNode deserialize(String data) {
        if (data == null || data.isEmpty()) return null;
        String[] tokens = data.split(SEP, -1);
        int[] pos = {0};
        return decode(tokens, pos);
    }

    private TreeNode decode(String[] tokens, int[] pos) {
        if (pos[0] >= tokens.length) return null;
        String token = tokens[pos[0]++];
        if (NULL_MARKER.equals(token)) return null;
        TreeNode node = new TreeNode(Integer.parseInt(token));
        node.left  = decode(tokens, pos);
        node.right = decode(tokens, pos);
        return node;
    }
}
```

**Разбор по шагам.**
1. `serialize`: обходим дерево в порядке корень → лево → право; узлы записываем как строку с
   числом, `null` — как `"N"`; токены разделяем запятой.
2. `deserialize`: разбиваем строку по `,`; используем массив `pos[0]` как «указатель» (int[]
   вместо объекта позволяет передавать его по ссылке в рекурсию).
3. Если токен `"N"` — возвращаем `null`; иначе создаём узел и рекурсивно строим левое и правое
   поддеревья.
4. Порядок чтения при десериализации совпадает с порядком записи — корректность гарантирована.

**Сложность.** Время O(n) для обеих операций — каждый узел обрабатывается один раз.
Память O(n) — строка/токены и стек рекурсии.

**Типичные ошибки / альтернативы.**
- Разница с источником: источник использует BFS, наше решение — DFS preorder; оба корректны,
  интерфейс `Codec` одинаков.
- BFS удобен для «читабельного» формата (уровни сохраняются как в LeetCode); DFS — для
  компактности реализации.
- Опасность: `split(",")` без флага `-1` отбросит пустые строки в хвосте; у нас пустых не будет,
  но флаг `-1` безопаснее.
- Нельзя кодировать только значения без маркеров `null`: дерево не восстанавливается однозначно.

---

### Вопрос 54. LC 128. Длиннейшая последовательность подряд (Longest Consecutive Sequence)

**Категория:** Алгоритмы и структуры данных · Hash Set · **Уровень:** Medium

Дан неотсортированный целочисленный массив `nums`. Верните длину наидлиннейшей
последовательности подряд идущих целых чисел. Алгоритм должен работать
за O(n) времени.

**Пример 1.** Вход: `nums = [100,4,200,1,3,2]` → Выход: `4` — последовательность `[1,2,3,4]`.
**Пример 2.** Вход: `nums = [0,3,7,2,5,8,4,6,0,1]` → Выход: `9` — последовательность `[0..8]`.
**Ограничения:** `0 <= nums.length <= 10^5`, `-10^9 <= nums[i] <= 10^9`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Longest Consecutive Sequence](https://github.com/doocs/leetcode/blob/main/solution/0100-0199/0128.Longest%20Consecutive%20Sequence/README.md)

Подход: HashSet + запуск последовательности только от «левого конца».
Добавляем все числа в `HashSet`. Перебираем элементы множества: если `x-1` отсутствует —
`x` является началом некоторой последовательности. Идём вправо (`x+1, x+2, ...`) пока значения
присутствуют в множестве. Каждый элемент входит в расширение ровно одной последовательности →
суммарно O(n). Время O(n), память O(n).

```java
class Solution {
    public int longestConsecutive(int[] nums) {
        Set<Integer> s = new HashSet<>();
        for (int x : nums) {
            s.add(x);
        }
        int ans = 0;
        for (int x : s) {
            if (!s.contains(x - 1)) {
                int y = x + 1;
                while (s.contains(y)) {
                    ++y;
                }
                ans = Math.max(ans, y - x);
            }
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Тот же подход «начинаем только от левого края»: если `x-1` в множестве есть —
пропускаем `x` (не является началом). Это гарантирует, что каждый элемент участвует в счёте
максимум один раз → суммарная сложность O(n).

```java
public int longestConsecutive(int[] nums) {
    Set<Integer> set = new HashSet<>(nums.length * 2);
    for (int x : nums) set.add(x);

    int best = 0;

    for (int x : set) {
        // Запускаем цепочку только от «левого конца»
        if (set.contains(x - 1)) continue;

        int length = 1;
        while (set.contains(x + length)) {
            length++;
        }
        best = Math.max(best, length);
    }
    return best;
}
```

**Разбор по шагам.**
1. Загружаем все элементы в `HashSet` за O(n); дубликаты автоматически удаляются.
2. Перебираем элементы множества (порядок произвольный — это нормально).
3. Если `x - 1` есть в множестве — `x` не является левым концом; пропускаем.
4. Иначе считаем длину: проверяем `x+1, x+2, ...` пока они присутствуют в множестве.
5. Обновляем `best`.

**Сложность.** Время O(n) — каждый элемент «расширяет» ровно одну последовательность суммарно.
Память O(n) — HashSet.

**Типичные ошибки / альтернативы.**
- Перебор по исходному массиву (а не по `set`) — корректен, но при дубликатах одна и та же
  последовательность может стартовать несколько раз, хотя проверка `contains(x-1)` всё равно
  отсекает лишние запуски; по сути не влияет на корректность, но перебор по `set` нагляднее.
- Сортировка + линейный проход: O(n log n) время, O(1) доп. память — медленнее по времени,
  зато не требует хеш-таблицы.
- Решение с Union-Find: O(n·α(n)), код сложнее без выигрыша.

---

### Вопрос 55. LC 39. Комбинации суммы (Combination Sum)

**Категория:** Алгоритмы и структуры данных · Backtracking · **Уровень:** Medium

Дан массив **уникальных** целых чисел `candidates` и целое число `target`.
Верните список всех уникальных комбинаций из `candidates`, в которых числа суммируются до `target`.
Один и тот же кандидат может использоваться **неограниченное** число раз.
Порядок в результирующем списке не важен.

**Пример 1.** Вход: `candidates = [2,3,6,7]`, `target = 7` → Выход: `[[2,2,3],[7]]`.
**Пример 2.** Вход: `candidates = [2,3,5]`, `target = 8` → Выход: `[[2,2,2,2],[2,3,3],[3,5]]`.
**Ограничения:** `1 <= candidates.length <= 30`; `2 <= candidates[i] <= 40`; все кандидаты уникальны;
`1 <= target <= 40`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Combination Sum](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0039.Combination%20Sum/README.md)

Подход: backtracking с сортировкой и отсечением.
Кандидаты сортируются; рекурсия стартует с индекса `i`; на каждом уровне можно снова взять
тот же элемент (вызов `dfs(j, s - candidates[j])`). Если оставшаяся сумма `s < candidates[i]` —
прерываемся досрочно (pruning). Время O(2^(target/min)), память O(target/min).

```java
class Solution {
    private List<List<Integer>> ans = new ArrayList<>();
    private List<Integer> t = new ArrayList<>();
    private int[] candidates;

    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        Arrays.sort(candidates);
        this.candidates = candidates;
        dfs(0, target);
        return ans;
    }

    private void dfs(int i, int s) {
        if (s == 0) {
            ans.add(new ArrayList<>(t));
            return;
        }
        if (s < candidates[i]) {
            return;
        }
        for (int j = i; j < candidates.length; ++j) {
            t.add(candidates[j]);
            dfs(j, s - candidates[j]);
            t.remove(t.size() - 1);
        }
    }
}
```

#### Ответ от Claude

**Идея.** Классический backtracking: на каждом шаге решаем, добавить ли следующий кандидат
в текущую комбинацию. Ключевые инварианты:
- Начинаем с индекса `start`, чтобы не допускать перестановок одной комбинации.
- Один и тот же элемент разрешён повторно (`dfs(start, ...)` с тем же `start`).
- Сортировка + ранний выход: если `candidates[j] > remaining` — все последующие тоже больше.

```java
public List<List<Integer>> combinationSum(int[] candidates, int target) {
    Arrays.sort(candidates);
    List<List<Integer>> result = new ArrayList<>();
    backtrack(candidates, target, 0, new ArrayList<>(), result);
    return result;
}

private void backtrack(int[] candidates, int remaining,
                       int start, List<Integer> current,
                       List<List<Integer>> result) {
    if (remaining == 0) {
        result.add(new ArrayList<>(current));
        return;
    }
    for (int i = start; i < candidates.length; i++) {
        int c = candidates[i];
        // Кандидаты отсортированы: если c > remaining, все следующие тоже не подходят
        if (c > remaining) break;
        current.add(c);
        // Разрешаем повторное использование: передаём i, а не i+1
        backtrack(candidates, remaining - c, i, current, result);
        current.remove(current.size() - 1);
    }
}
```

**Разбор по шагам.**
1. Сортируем кандидаты — для корректного pruning и детерминированного порядка результатов.
2. В `backtrack`: перебираем кандидаты начиная с `start`.
3. Если `c > remaining` — прерываем цикл (все последующие кандидаты ещё больше).
4. Добавляем `c` в `current`, уменьшаем `remaining`, рекурсируем с тем же `i` (повтор разрешён).
5. После возврата убираем `c` из `current` — откат состояния.
6. Если `remaining == 0` — нашли комбинацию, копируем в результат.

**Сложность.** Время O(2^(target/min_c)) в худшем случае (все комбинации); на практике
pruning значительно сокращает поиск. Память O(target/min_c) — глубина рекурсии.

**Типичные ошибки / альтернативы.**
- Передача `i+1` вместо `i` при рекурсии → каждый кандидат используется не более одного раза
  (это задача LC 40, Combination Sum II).
- Забыть откатить `current.remove(...)` — текущий список «загрязнится» предыдущими ветвями.
- Отсутствие сортировки: pruning `break` не сработает, придётся заменять на `continue` →
  медленнее из-за лишних ветвей.
- Решение источника использует поля класса (`ans`, `t`) вместо параметров — функционально
  эквивалентно, но менее потокобезопасно.

---

### Вопрос 56. LC 78. Подмножества (Subsets)

**Категория:** Алгоритмы и структуры данных · Backtracking · **Уровень:** Medium

Дан массив уникальных целых чисел `nums`. Верните список всех возможных подмножеств
(множество всех подмножеств, power set). Решение не должно содержать дублирующихся подмножеств.
Порядок результатов не важен.

**Пример 1.** Вход: `nums = [1,2,3]` → Выход: `[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]`.
**Пример 2.** Вход: `nums = [0]` → Выход: `[[],[0]]`.
**Ограничения:** `1 <= nums.length <= 10`; `-10 <= nums[i] <= 10`; все элементы уникальны.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Subsets](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0078.Subsets/README.md)

Подход 1 — DFS (backtracking): на каждом уровне решаем «включить или нет» текущий элемент.
Когда `i == nums.length` — добавляем копию текущего набора в ответ.
Подход 2 — битовая маска: перебираем все маски от `0` до `2^n - 1`; бит `i` означает включение
элемента `nums[i]`. Оба подхода: время O(n * 2^n), память O(n).

```java
// DFS
class Solution {
    private List<List<Integer>> ans = new ArrayList<>();
    private List<Integer> t = new ArrayList<>();
    private int[] nums;

    public List<List<Integer>> subsets(int[] nums) {
        this.nums = nums;
        dfs(0);
        return ans;
    }

    private void dfs(int i) {
        if (i == nums.length) {
            ans.add(new ArrayList<>(t));
            return;
        }
        dfs(i + 1);          // не берём nums[i]
        t.add(nums[i]);
        dfs(i + 1);          // берём nums[i]
        t.remove(t.size() - 1);
    }
}
```

#### Ответ от Claude

**Идея.** Будем строить подмножества итеративно: начинаем с `[[]]` и для каждого нового
элемента копируем все существующие подмножества и добавляем в них новый элемент.
Это «каскадный» подход — наглядный и легко объяснимый.
Дополнительно покажем классический backtracking для полноты.

```java
// Подход 1: итеративный «каскад»
public List<List<Integer>> subsets(int[] nums) {
    List<List<Integer>> result = new ArrayList<>();
    result.add(new ArrayList<>());  // пустое подмножество

    for (int num : nums) {
        int size = result.size();
        // Для каждого существующего подмножества создаём копию + num
        for (int i = 0; i < size; i++) {
            List<Integer> subset = new ArrayList<>(result.get(i));
            subset.add(num);
            result.add(subset);
        }
    }
    return result;
}

// Подход 2: backtracking (для сравнения)
public List<List<Integer>> subsetsBacktrack(int[] nums) {
    List<List<Integer>> result = new ArrayList<>();
    backtrack(nums, 0, new ArrayList<>(), result);
    return result;
}

private void backtrack(int[] nums, int start,
                       List<Integer> current, List<List<Integer>> result) {
    // Добавляем текущее подмножество в любой момент рекурсии
    result.add(new ArrayList<>(current));
    for (int i = start; i < nums.length; i++) {
        current.add(nums[i]);
        backtrack(nums, i + 1, current, result);
        current.remove(current.size() - 1);
    }
}
```

**Разбор по шагам (итеративный подход).**
1. Начинаем с `[[]]`.
2. Для `nums[0] = 1`: копируем `[]` → добавляем `[1]`; итого `[[], [1]]`.
3. Для `nums[1] = 2`: копируем `[]` → `[2]`, копируем `[1]` → `[1,2]`; итого `[[], [1], [2], [1,2]]`.
4. Аналогично для всех оставшихся элементов; после n элементов: 2^n подмножеств.

**Сложность.** Время O(n * 2^n) — генерируем 2^n подмножеств, каждое строим за O(n).
Память O(n * 2^n) — для хранения результата.

**Типичные ошибки / альтернативы.**
- Итеративный подход отличается от источника (DFS): оба корректны, порядок подмножеств в
  результате отличается, но по условию порядок не важен.
- Битовая маска (подход источника 2): элегантна при `n <= 20`; при `n > 30` маска переполняет `int`.
- В backtracking — передаём `i+1` (каждый элемент используется не более одного раза),
  в отличие от Combination Sum, где передаётся `i`.
- Не забывать `new ArrayList<>(current)` при сохранении — иначе все ссылки указывают на
  один изменяемый список.

---

### Вопрос 57. LC 300. Длиннейшая возрастающая подпоследовательность (Longest Increasing Subsequence)

**Категория:** Алгоритмы и структуры данных · DP · **Уровень:** Medium

Дан целочисленный массив `nums`. Верните длину наидлиннейшей строго возрастающей
подпоследовательности.

**Пример 1.** Вход: `nums = [10,9,2,5,3,7,101,18]` → Выход: `4` — подпоследовательность `[2,3,7,101]`.
**Пример 2.** Вход: `nums = [0,1,0,3,2,3]` → Выход: `4`.
**Пример 3.** Вход: `nums = [7,7,7,7,7,7,7]` → Выход: `1`.
**Ограничения:** `1 <= nums.length <= 2500`; `-10^4 <= nums[i] <= 10^4`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Longest Increasing Subsequence](https://github.com/doocs/leetcode/blob/main/solution/0300-0399/0300.Longest%20Increasing%20Subsequence/README.md)

Подход 1 — классическая динамическая программа: `f[i]` = длина LIS, заканчивающейся на `nums[i]`.
Для каждого `i`: `f[i] = max(f[j] + 1)` для всех `j < i` где `nums[j] < nums[i]`.
Время O(n^2), память O(n).

```java
class Solution {
    public int lengthOfLIS(int[] nums) {
        int n = nums.length;
        int[] f = new int[n];
        Arrays.fill(f, 1);
        int ans = 1;
        for (int i = 1; i < n; ++i) {
            for (int j = 0; j < i; ++j) {
                if (nums[j] < nums[i]) {
                    f[i] = Math.max(f[i], f[j] + 1);
                }
            }
            ans = Math.max(ans, f[i]);
        }
        return ans;
    }
}
```

Подход 2 — дискретизация + бинарное индексное дерево (дерево Фенвика): O(n log n).
Значения массива дискретизируются (сжимаются в индексы), после чего для каждого элемента
запрашивается максимальная длина LIS среди меньших значений через BIT, и BIT обновляется.
«Терпеливая сортировка» (patience sorting) в источнике doocs не упоминается.

#### Ответ от Claude

**Идея.** Реализуем O(n log n) алгоритм на основе «терпеливой сортировки» (patience sorting).
Поддерживаем массив `tails`, где `tails[k]` — наименьший возможный хвостовой элемент LIS длины `k+1`.
Для каждого нового элемента:
- Если он больше всех хвостов — расширяем LIS на 1.
- Иначе — заменяем первый хвост, который `>= nums[i]` (бинарный поиск).

Массив `tails` всегда отсортирован, что делает бинарный поиск корректным.

```java
public int lengthOfLIS(int[] nums) {
    // tails[i] = минимальный хвост LIS длины (i+1)
    int[] tails = new int[nums.length];
    int size = 0; // текущая длина tails (= длина LIS)

    for (int num : nums) {
        // Бинарный поиск: найти позицию первого элемента >= num
        int lo = 0, hi = size;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (tails[mid] < num) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        // lo == позиция для замены или расширения
        tails[lo] = num;
        if (lo == size) size++; // num больше всех хвостов -> LIS растёт
    }
    return size;
}
```

**Разбор по шагам.**
Пример: `nums = [10, 9, 2, 5, 3, 7, 101, 18]`.
1. `10`: `tails = [10]`, size=1.
2. `9`: заменяем `tails[0]=10` → `tails = [9]`, size=1.
3. `2`: заменяем `tails[0]=9` → `tails = [2]`, size=1.
4. `5`: `5 > 2`, добавляем → `tails = [2,5]`, size=2.
5. `3`: заменяем `tails[1]=5` → `tails = [2,3]`, size=2.
6. `7`: `7 > 3`, добавляем → `tails = [2,3,7]`, size=3.
7. `101`: добавляем → `tails = [2,3,7,101]`, size=4.
8. `18`: заменяем `tails[3]=101` → `tails = [2,3,7,18]`, size=4.
Ответ: 4.

**Сложность.** Время O(n log n) — для каждого из n элементов бинарный поиск O(log n).
Память O(n) — массив `tails`.

**Типичные ошибки / альтернативы.**
- Отличие от источника: doocs даёт O(n^2) DP (подход 1) и O(n log n) через BIT с дискретизацией
  (подход 2). Решение ниже — самостоятельная альтернатива: O(n log n) на основе «терпеливой
  сортировки» (patience sorting) с массивом хвостов и бинарным поиском. Patience sorting
  в источнике doocs отсутствует.
- `tails` не является самой LIS! Это массив оптимальных хвостов; для восстановления
  конкретной подпоследовательности нужна отдельная таблица parent-указателей.
- Бинарный поиск ищет первый элемент `>= num` (не строго больший), что обеспечивает строгую
  возрастаемость. Для нестрогой (non-decreasing) нужно искать первый `> num`.
- `(lo + hi) >>> 1` вместо `(lo + hi) / 2` — защита от переполнения при больших индексах.

---

### Вопрос 58. LC 416. Разбиение на равные суммы (Partition Equal Subset Sum)

**Категория:** Алгоритмы и структуры данных · DP · **Уровень:** Medium

Дан целочисленный массив `nums`. Верните `true`, если массив можно разбить на **два подмножества**
с равными суммами, и `false` в противном случае.

**Пример 1.** Вход: `nums = [1,5,11,5]` → Выход: `true` — подмножества `[1,5,5]` и `[11]`.
**Пример 2.** Вход: `nums = [1,2,3,5]` → Выход: `false` — нельзя разбить на равные суммы.
**Ограничения:** `1 <= nums.length <= 200`; `1 <= nums[i] <= 100`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Partition Equal Subset Sum](https://github.com/doocs/leetcode/blob/main/solution/0400-0499/0416.Partition%20Equal%20Subset%20Sum/README.md)

Задача сводится к задаче о рюкзаке 0/1: нужно проверить, можно ли набрать ровно `sum/2`
из элементов массива. `f[j]` — можно ли набрать ровно `j` из первых `i` элементов.
Переходы: `f[j] |= f[j - nums[i]]`, итерация `j` от `m` до `x` (чтобы не использовать элемент дважды).
Время O(n*m), память O(m), где `m = sum/2`. Если сумма нечётна — сразу `false`.

```java
class Solution {
    public boolean canPartition(int[] nums) {
        int s = 0;
        for (int x : nums) {
            s += x;
        }
        if (s % 2 == 1) {
            return false;
        }
        int m = s >> 1;
        boolean[] f = new boolean[m + 1];
        f[0] = true;
        for (int x : nums) {
            for (int j = m; j >= x; --j) {
                f[j] |= f[j - x];
            }
        }
        return f[m];
    }
}
```

#### Ответ от Claude

**Идея.** Это задача о рюкзаке 0/1 (knapsack), сведённая к вопросу о достижимости суммы.
Если общая сумма нечётна — ответ сразу `false`. Иначе цель = `total / 2`.
`dp[j]` = можно ли набрать сумму ровно `j`, используя подмножество уже обработанных элементов.
Итерируем `j` от `target` вниз до `x` — это предотвращает повторное использование одного элемента.

```java
public boolean canPartition(int[] nums) {
    int total = 0;
    for (int x : nums) total += x;

    // Нечётная сумма — нельзя разбить ровно пополам
    if ((total & 1) == 1) return false;

    int target = total / 2;
    boolean[] dp = new boolean[target + 1];
    dp[0] = true; // пустое подмножество даёт сумму 0

    for (int x : nums) {
        // Идём справа налево, чтобы не использовать x дважды в одной итерации
        for (int j = target; j >= x; j--) {
            dp[j] = dp[j] || dp[j - x];
        }
        // Ранний выход: если цель достигнута — нет смысла продолжать
        if (dp[target]) return true;
    }
    return dp[target];
}
```

**Разбор по шагам.**
1. Считаем `total`; если нечётное — `false`.
2. `target = total / 2`; нужно проверить, достижима ли эта сумма.
3. `dp[0] = true` — базовый случай: пустое подмножество.
4. Для каждого элемента `x`: проходим `j` от `target` до `x` и обновляем `dp[j] |= dp[j - x]`.
5. Обратный порядок `j` — ключевой инвариант: `dp[j - x]` ссылается на состояние *до* добавления `x`.
6. Ранний выход при `dp[target] == true` экономит время.

**Сложность.** Время O(n * target) = O(n * sum/2). Память O(target) = O(sum/2).
При ограничениях: n <= 200, nums[i] <= 100 → sum <= 20000, target <= 10000; таблица помещается в памяти.

**Типичные ошибки / альтернативы.**
- Итерация `j` слева направо (возрастание) — ошибка: элемент `x` может использоваться несколько
  раз в одной строке DP (это задача о рюкзаке с повторением, Unbounded Knapsack).
- Забыть проверить нечётность суммы — в этом случае `target` будет дробным после `/ 2`
  (в Java целочисленное деление усечёт), и ответ может быть ложноположительным.
- 2D DP `f[i][j]` (как в методе 1 источника) наглядна для понимания переходов, но требует
  O(n * target) памяти; 1D — оптимизация по памяти с сохранением сложности по времени.
- BitSet-оптимизация: `dp` можно хранить как `BitSet`; сдвиг `bs |= (bs << x)` выполняет
  все переходы за одну операцию → ускорение на константу в несколько раз.

---
