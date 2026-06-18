# Задачи LeetCode — часть 03 (Medium)

### Вопрос 32. LC 3. Длиннейшая подстрока без повторов (Longest Substring Without Repeating Characters)

**Категория:** Алгоритмы и структуры данных · Sliding Window · **Уровень:** Medium

Дана строка `s`. Найдите длину наибольшей подстроки без повторяющихся символов.

**Пример 1.** Вход: `s = "abcabcbb"` → Выход: `3` (подстрока `"abc"`).
**Пример 2.** Вход: `s = "bbbbb"` → Выход: `1` (подстрока `"b"`).
**Пример 3.** Вход: `s = "pwwkew"` → Выход: `3` (подстрока `"wke"`).
**Ограничения:** `0 <= s.length <= 5 * 10^4`, символы из английских букв, цифр и знаков пунктуации.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Longest Substring Without Repeating Characters](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0003.Longest%20Substring%20Without%20Repeating%20Characters/README.md)

Скользящее окно с частотным массивом: правый указатель `r` расширяет окно, добавляя символ. Если частота символа превысила 1, левый указатель `l` сужает окно до устранения дубликата. Ответ — максимальная длина окна. Время O(n), память O(1) (массив из 128 ячеек).

```java
class Solution {
    public int lengthOfLongestSubstring(String s) {
        int[] cnt = new int[128];
        int ans = 0, n = s.length();
        for (int l = 0, r = 0; r < n; ++r) {
            char c = s.charAt(r);
            ++cnt[c];
            while (cnt[c] > 1) {
                --cnt[s.charAt(l++)];
            }
            ans = Math.max(ans, r - l + 1);
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Скользящее окно `[l, r]` поддерживает инвариант: все символы в нём уникальны. Вместо частотного массива используем `HashMap<Character, Integer>` с индексом последней встречи — это позволяет сразу прыгать `l` вперёд, не двигая его по одному.

```java
public int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> lastSeen = new HashMap<>();
    int ans = 0;
    for (int l = 0, r = 0; r < s.length(); r++) {
        char c = s.charAt(r);
        // Если символ уже в окне, сдвигаем l за его предыдущую позицию
        if (lastSeen.containsKey(c) && lastSeen.get(c) >= l) {
            l = lastSeen.get(c) + 1;
        }
        lastSeen.put(c, r);
        ans = Math.max(ans, r - l + 1);
    }
    return ans;
}
```

**Разбор по шагам.** Для каждого `r` проверяем, была ли `c` уже в текущем окне (индекс последней встречи >= `l`). Если да — прыгаем `l` сразу за неё, иначе окно расширяется. `lastSeen` всегда хранит последнюю позицию каждого символа.

**Сложность.** Время O(n), память O(min(n, |алфавит|)).

**Типичные ошибки / альтернативы.** Расхождение с оригиналом: оригинал сдвигает `l` по одному (while-цикл) — корректно, но медленнее для длинных повторов; HashMap-вариант прыгает сразу. Граничный случай: пустая строка должна вернуть 0 — проверьте, что цикл не выполняется и возвращается `0`.

---

### Вопрос 33. LC 15. Сумма трёх (3Sum)

**Категория:** Алгоритмы и структуры данных · Two Pointers · **Уровень:** Medium

Дан целочисленный массив `nums`. Найдите все уникальные тройки `[nums[i], nums[j], nums[k]]` такие, что `i != j != k` и `nums[i] + nums[j] + nums[k] == 0`.

**Пример 1.** Вход: `nums = [-1,0,1,2,-1,-4]` → Выход: `[[-1,-1,2],[-1,0,1]]`.
**Пример 2.** Вход: `nums = [0,1,1]` → Выход: `[]`.
**Пример 3.** Вход: `nums = [0,0,0]` → Выход: `[[0,0,0]]`.
**Ограничения:** `3 <= nums.length <= 3000`, `-10^5 <= nums[i] <= 10^5`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — 3Sum](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0015.3Sum/README.md)

Сортировка + два указателя: фиксируем `nums[i]` (пропускаем дубликаты), затем ищем пару `j, k` с двух концов оставшегося диапазона. При нахождении пары — пропускаем дубликаты с обеих сторон. Время O(n²), память O(log n) для сортировки.

```java
class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> ans = new ArrayList<>();
        int n = nums.length;
        for (int i = 0; i < n - 2 && nums[i] <= 0; ++i) {
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            int j = i + 1, k = n - 1;
            while (j < k) {
                int x = nums[i] + nums[j] + nums[k];
                if (x < 0) {
                    ++j;
                } else if (x > 0) {
                    --k;
                } else {
                    ans.add(List.of(nums[i], nums[j++], nums[k--]));
                    while (j < k && nums[j] == nums[j - 1]) {
                        ++j;
                    }
                    while (j < k && nums[k] == nums[k + 1]) {
                        --k;
                    }
                }
            }
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Сортировка переводит задачу к двум указателям. Фиксируем `i`, ищем `target = -nums[i]` в диапазоне `[i+1, n-1]` двумя указателями. Ключевой момент: пропуск дубликатов на всех трёх позициях обязателен для уникальности.

```java
public List<List<Integer>> threeSum(int[] nums) {
    Arrays.sort(nums);
    List<List<Integer>> result = new ArrayList<>();
    int n = nums.length;
    for (int i = 0; i < n - 2; i++) {
        // Оптимизация: если наименьший элемент > 0, дальше сумма только растёт
        if (nums[i] > 0) break;
        // Пропускаем дубликаты первого элемента
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int left = i + 1, right = n - 1;
        while (left < right) {
            int sum = nums[i] + nums[left] + nums[right];
            if (sum == 0) {
                result.add(Arrays.asList(nums[i], nums[left], nums[right]));
                // Пропускаем дубликаты второго и третьего элементов
                while (left < right && nums[left] == nums[left + 1]) left++;
                while (left < right && nums[right] == nums[right - 1]) right--;
                left++;
                right--;
            } else if (sum < 0) {
                left++;
            } else {
                right--;
            }
        }
    }
    return result;
}
```

**Разбор по шагам.** После сортировки: (1) если `nums[i] > 0`, тройки с нулевой суммой невозможны — выходим; (2) для каждого `i` двигаем `left` и `right` навстречу; (3) при нахождении — сразу пропускаем все одинаковые значения с обеих сторон и двигаем оба указателя.

**Сложность.** Время O(n²), память O(log n) для сортировки.

**Типичные ошибки / альтернативы.** Частая ошибка — пропуск дубликатов только для `i`, но не для `left/right`, что даёт повторные тройки. Альтернатива — HashSet для результатов, но это O(n²) по памяти. Подход с `nums[i] > 0` — оптимизация по сравнению с оригиналом.

---

### Вопрос 34. LC 11. Контейнер с наибольшим объёмом воды (Container With Most Water)

**Категория:** Алгоритмы и структуры данных · Two Pointers · **Уровень:** Medium

Дан массив `height` из `n` целых чисел. Есть `n` вертикальных линий, у i-й линии концы в точках `(i, 0)` и `(i, height[i])`. Найдите две линии, образующие контейнер, который вмещает наибольшее количество воды.

**Пример 1.** Вход: `height = [1,8,6,2,5,4,8,3,7]` → Выход: `49` (линии 1 и 8, высота min(8,7)=7, ширина=7).
**Пример 2.** Вход: `height = [1,1]` → Выход: `1`.
**Ограничения:** `n == height.length`, `2 <= n <= 10^5`, `0 <= height[i] <= 10^4`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Container With Most Water](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0011.Container%20With%20Most%20Water/README.md)

Два указателя с краёв: на каждом шаге вычисляем площадь `min(height[l], height[r]) * (r - l)`. Перемещаем тот указатель, которому соответствует меньшая высота — это единственный способ потенциально увеличить результат. Время O(n), память O(1).

```java
class Solution {
    public int maxArea(int[] height) {
        int l = 0, r = height.length - 1;
        int ans = 0;
        while (l < r) {
            int t = Math.min(height[l], height[r]) * (r - l);
            ans = Math.max(ans, t);
            if (height[l] < height[r]) {
                ++l;
            } else {
                --r;
            }
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Доказательство корректности: если `height[l] < height[r]`, то любой контейнер `(l, x)` при `x < r` даст площадь не больше текущей (ширина меньше, высота ограничена `height[l]`). Значит, двигать `l` — единственный шанс улучшить результат.

```java
public int maxArea(int[] height) {
    int maxWater = 0;
    int left = 0, right = height.length - 1;
    while (left < right) {
        int h = Math.min(height[left], height[right]);
        int w = right - left;
        maxWater = Math.max(maxWater, h * w);
        // Перемещаем указатель с меньшей высотой
        if (height[left] <= height[right]) {
            left++;
        } else {
            right--;
        }
    }
    return maxWater;
}
```

**Разбор по шагам.** Начинаем с максимальной шириной `(0, n-1)`. На каждом шаге жертвуем шириной ради возможного роста высоты, двигая меньший из двух краёв. Площадь вычисляется немедленно, максимум обновляется на ходу.

**Сложность.** Время O(n), память O(1).

**Типичные ошибки / альтернативы.** Два указателя — оптимальный O(n)-алгоритм; его корректность основана на жадном инварианте: если `height[left] < height[right]`, то любой контейнер `(left, x)` при `x < right` не превзойдёт текущий (ширина уменьшается, высота по-прежнему ограничена `height[left]`), поэтому двигать меньший указатель — единственный шанс на улучшение. Базовая альтернатива — перебор всех пар O(n²) — корректна, но неприемлема по времени при `n` до 10^5. Случай равных высот: при `height[left] == height[right]` можно двигать любой указатель — оба варианта корректны, т.к. текущая площадь уже зафиксирована и сохранить оба края одновременно невозможно.

---

### Вопрос 35. LC 424. Длиннейшая замена повторяющихся символов (Longest Repeating Character Replacement)

**Категория:** Алгоритмы и структуры данных · Sliding Window · **Уровень:** Medium

Дана строка `s` из заглавных букв и целое `k`. Можно заменить не более `k` символов строки на любую другую заглавную букву. Найдите длину наибольшей подстроки, в которой все символы одинаковы, после выполнения операций замены.

**Пример 1.** Вход: `s = "ABAB"`, `k = 2` → Выход: `4` (заменяем 2 символа B на A).
**Пример 2.** Вход: `s = "AABABBA"`, `k = 1` → Выход: `4`.
**Ограничения:** `1 <= s.length <= 10^5`, `s` состоит из заглавных букв, `0 <= k <= s.length`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Longest Repeating Character Replacement](https://github.com/doocs/leetcode/blob/main/solution/0400-0499/0424.Longest%20Repeating%20Character%20Replacement/README.md)

Скользящее окно: отслеживаем максимальную частоту `mx` символа в окне. Если `размер окна - mx > k`, окно слишком большое — сдвигаем левый край. Окно никогда не уменьшается (алгоритм ищет максимальную длину). Время O(n), память O(1).

```java
class Solution {
    public int characterReplacement(String s, int k) {
        int[] cnt = new int[26];
        int l = 0, mx = 0;
        int n = s.length();
        for (int r = 0; r < n; ++r) {
            mx = Math.max(mx, ++cnt[s.charAt(r) - 'A']);
            if (r - l + 1 - mx > k) {
                --cnt[s.charAt(l++) - 'A'];
            }
        }
        return n - l;
    }
}
```

#### Ответ от Claude

**Идея.** Инвариант окна: `(длина окна) - (частота доминирующего символа) <= k`. Это равносильно тому, что можно заменить все не-доминирующие символы. Важно: `mx` монотонно растёт — при сужении окна мы не уменьшаем `mx`, так как ищем только лучший результат.

```java
public int characterReplacement(String s, int k) {
    int[] freq = new int[26];
    int left = 0, maxFreq = 0, maxLen = 0;
    for (int right = 0; right < s.length(); right++) {
        int idx = s.charAt(right) - 'A';
        freq[idx]++;
        maxFreq = Math.max(maxFreq, freq[idx]);
        // Сколько символов нужно заменить = размер окна - максимальная частота
        int windowSize = right - left + 1;
        if (windowSize - maxFreq > k) {
            // Сдвигаем левый край, уменьшая частоту ушедшего символа
            freq[s.charAt(left) - 'A']--;
            left++;
        } else {
            maxLen = Math.max(maxLen, right - left + 1);
        }
    }
    return Math.max(maxLen, s.length() - left);
}
```

**Разбор по шагам.** Расширяем окно вправо. Если число замен превышает `k`, сдвигаем левый край на 1 (окно не уменьшается — для ответа нужно только его расширение). `maxFreq` может «устареть» при сдвиге, но это безопасно: устаревшее значение не даст ложного расширения. Финальный `return Math.max(maxLen, s.length() - left)` принципиально важен: если последние итерации цикла только расширяли окно (ветка `else` не срабатывала), то `maxLen` не был обновлён для этого последнего валидного окна — именно `s.length() - left` его фиксирует.

**Сложность.** Время O(n), память O(1).

**Типичные ошибки / альтернативы.** Расхождение: в оригинале `maxFreq` может не отражать реальное значение при сужении — это намеренно, т.к. нас интересует только расширение. Альтернатива — отдельный пересчёт `maxFreq` при каждом сужении даёт O(26·n), но сложнее для понимания.

---

### Вопрос 36. LC 560. Подмассивы с суммой K (Subarray Sum Equals K)

**Категория:** Алгоритмы и структуры данных · Hash Table / Prefix Sum · **Уровень:** Medium

Дан целочисленный массив `nums` и целое `k`. Верните количество непрерывных подмассивов, сумма которых равна `k`.

**Пример 1.** Вход: `nums = [1,1,1]`, `k = 2` → Выход: `2`.
**Пример 2.** Вход: `nums = [1,2,3]`, `k = 3` → Выход: `2`.
**Ограничения:** `1 <= nums.length <= 2 * 10^4`, `-1000 <= nums[i] <= 1000`, `-10^7 <= k <= 10^7`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Subarray Sum Equals K](https://github.com/doocs/leetcode/blob/main/solution/0500-0599/0560.Subarray%20Sum%20Equals%20K/README.md)

Префиксные суммы + хеш-таблица: для каждой позиции `r` с префиксной суммой `s` ищем количество предыдущих позиций с префиксной суммой `s - k`. Инициализация `cnt[0] = 1` учитывает подмассивы от начала. Время O(n), память O(n).

```java
class Solution {
    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> cnt = new HashMap<>();
        cnt.put(0, 1);
        int ans = 0, s = 0;
        for (int x : nums) {
            s += x;
            ans += cnt.getOrDefault(s - k, 0);
            cnt.merge(s, 1, Integer::sum);
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Подмассив `[i+1, j]` имеет сумму `k` тогда и только тогда, когда `prefix[j] - prefix[i] == k`, то есть `prefix[i] == prefix[j] - k`. Хеш-таблица позволяет за O(1) узнать, сколько раз встречалась нужная префиксная сумма.

```java
public int subarraySum(int[] nums, int k) {
    // prefix[0] = 0 встречается ровно 1 раз (пустой префикс)
    Map<Integer, Integer> prefixCount = new HashMap<>();
    prefixCount.put(0, 1);
    int count = 0, prefixSum = 0;
    for (int num : nums) {
        prefixSum += num;
        // Ищем, сколько предыдущих префиксов дают сумму подмассива = k
        count += prefixCount.getOrDefault(prefixSum - k, 0);
        prefixCount.merge(prefixSum, 1, Integer::sum);
    }
    return count;
}
```

**Разбор по шагам.** Добавляем элемент к `prefixSum`. Перед записью текущей суммы в таблицу — проверяем, сколько раз встречалась сумма `prefixSum - k` (это значит, существует подмассив с нужной суммой, заканчивающийся здесь). Порядок важен: сначала запрос, потом вставка.

**Сложность.** Время O(n), память O(n).

**Типичные ошибки / альтернативы.** Массив не гарантированно неотрицательный — скользящее окно не работает. Инициализация `cnt.put(0, 1)` обязательна: без неё пропустим подмассивы с суммой `k`, начинающиеся с индекса 0.

---

### Вопрос 37. LC 19. Удалить N-й с конца узел (Remove Nth Node From End of List)

**Категория:** Алгоритмы и структуры данных · Связные списки / Two Pointers · **Уровень:** Medium

Дан заголовок связного списка. Удалите `n`-й узел с конца и верните заголовок изменённого списка.

**Пример 1.** Вход: `head = [1,2,3,4,5]`, `n = 2` → Выход: `[1,2,3,5]`.
**Пример 2.** Вход: `head = [1]`, `n = 1` → Выход: `[]`.
**Ограничения:** Число узлов в списке — `sz`, `1 <= sz <= 30`, `1 <= n <= sz`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Remove Nth Node From End of List](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0019.Remove%20Nth%20Node%20From%20End%20of%20List/README.md)

Два указателя с фиктивным узлом: быстрый (`fast`) опережает медленного (`slow`) на `n` шагов. Когда `fast` достигает конца, `slow` стоит перед удаляемым узлом. Фиктивный узел упрощает обработку удаления головного элемента. Время O(L), память O(1).

```java
class Solution {
    public ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode dummy = new ListNode(0, head);
        ListNode fast = dummy, slow = dummy;
        while (n-- > 0) {
            fast = fast.next;
        }
        while (fast.next != null) {
            slow = slow.next;
            fast = fast.next;
        }
        slow.next = slow.next.next;
        return dummy.next;
    }
}
```

#### Ответ от Claude

**Идея.** Gap-техника: удерживаем между `fast` и `slow` зазор ровно `n` узлов. Тогда, когда `fast` упрётся в последний узел (а не за конец), `slow` указывает ровно на предшественника удаляемого узла.

```java
public ListNode removeNthFromEnd(ListNode head, int n) {
    ListNode dummy = new ListNode(0);
    dummy.next = head;
    ListNode fast = dummy;
    ListNode slow = dummy;
    // Продвигаем fast на n+1 шаг, чтобы slow оказался перед целевым узлом
    for (int i = 0; i <= n; i++) {
        fast = fast.next;
    }
    while (fast != null) {
        slow = slow.next;
        fast = fast.next;
    }
    // slow стоит перед удаляемым узлом
    slow.next = slow.next.next;
    return dummy.next;
}
```

**Разбор по шагам.** Фиктивный узел делает `slow` всегда предшественником цели. Цикл `for` двигает `fast` на `n+1` шаг (не `n`), чтобы при остановке `fast == null` медленный был перед удаляемым. Затем `slow.next = slow.next.next` убирает нужный узел.

**Сложность.** Время O(L), память O(1).

**Типичные ошибки / альтернативы.** Расхождение: оригинал двигает `fast` на `n` шагов, а затем до `fast.next == null`; данное решение двигает на `n+1` и до `fast == null` — оба варианта корректны, логика симметрична. Без фиктивного узла удаление головы требует отдельной ветки.

---

### Вопрос 38. LC 143. Переупорядочить список (Reorder List)

**Категория:** Алгоритмы и структуры данных · Связные списки · **Уровень:** Medium

Дан заголовок односвязного списка `L0 → L1 → … → Ln-1 → Ln`. Переупорядочите список в вид `L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …`. Нельзя изменять значения узлов — только сами узлы.

**Пример 1.** Вход: `head = [1,2,3,4]` → Выход: `[1,4,2,3]`.
**Пример 2.** Вход: `head = [1,2,3,4,5]` → Выход: `[1,5,2,4,3]`.
**Ограничения:** Число узлов — от 1 до 5 * 10^4, `1 <= Node.val <= 1000`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Reorder List](https://github.com/doocs/leetcode/blob/main/solution/0100-0199/0143.Reorder%20List/README.md)

Три шага: (1) найти середину через медленный/быстрый указатели; (2) развернуть вторую половину; (3) чередующимся слиянием объединить обе половины. Время O(n), память O(1).

```java
class Solution {
    public void reorderList(ListNode head) {
        ListNode fast = head, slow = head;
        while (fast.next != null && fast.next.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        ListNode cur = slow.next;
        slow.next = null;
        ListNode pre = null;
        while (cur != null) {
            ListNode t = cur.next;
            cur.next = pre;
            pre = cur;
            cur = t;
        }
        cur = head;
        while (pre != null) {
            ListNode t = pre.next;
            pre.next = cur.next;
            cur.next = pre;
            cur = pre.next;
            pre = t;
        }
    }
}
```

#### Ответ от Claude

**Идея.** Задача сводится к трём подзадачам: найти середину, перевернуть хвост, перемежать. Ключевой момент: после нахождения середины нужно отрезать список (`slow.next = null`), иначе при слиянии образуется цикл.

```java
public void reorderList(ListNode head) {
    if (head == null || head.next == null) return;

    // Шаг 1: найти середину (slow остановится на конце первой половины)
    ListNode slow = head, fast = head;
    while (fast.next != null && fast.next.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    // Шаг 2: развернуть вторую половину
    ListNode secondHalf = slow.next;
    slow.next = null; // разрезаем список
    ListNode prev = null, curr = secondHalf;
    while (curr != null) {
        ListNode next = curr.next;
        curr.next = prev;
        prev = curr;
        curr = next;
    }
    // prev — голова перевёрнутой второй половины

    // Шаг 3: чередующееся слияние
    ListNode first = head, second = prev;
    while (second != null) {
        ListNode tmp1 = first.next, tmp2 = second.next;
        first.next = second;
        second.next = tmp1;
        first = tmp1;
        second = tmp2;
    }
}
```

**Разбор по шагам.** (1) Медленный/быстрый указатели: `slow` останавливается на конце первой половины. (2) Итеративное разворачивание: `prev` станет головой перевёрнутой второй половины. (3) Слияние: вставляем узлы из `second` между узлами `first` по одному.

**Сложность.** Время O(n), память O(1).

**Типичные ошибки / альтернативы.** Забыть `slow.next = null` — список не разрежется, и при слиянии возникнет бесконечный цикл. Альтернатива: сохранить все узлы в `ArrayList`, затем перестроить ссылки — O(n) памяти, но проще в реализации.

---

### Вопрос 39. LC 141. Цикл в списке (Linked List Cycle)

**Категория:** Алгоритмы и структуры данных · Связные списки / Floyd · **Уровень:** Medium

Дан заголовок связного списка. Определите, есть ли в нём цикл. Цикл существует, если какой-то узел списка достижим снова при последовательном переходе по ссылкам `next`.

**Пример 1.** Вход: `head = [3,2,0,-4]`, `pos = 1` → Выход: `true` (хвост связан с узлом на позиции 1).
**Пример 2.** Вход: `head = [1,2]`, `pos = 0` → Выход: `true`.
**Пример 3.** Вход: `head = [1]`, `pos = -1` → Выход: `false`.
**Ограничения:** Число узлов — от 0 до 10^4, `-10^5 <= Node.val <= 10^5`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Linked List Cycle](https://github.com/doocs/leetcode/blob/main/solution/0100-0199/0141.Linked%20List%20Cycle/README.md)

Два подхода: (1) HashSet — добавляем узлы; повтор означает цикл; O(n) время, O(n) память. (2) Алгоритм Флойда (два указателя) — медленный движется на 1, быстрый на 2 шага; если встретились — цикл есть. O(n) время, O(1) память.

```java
// Алгоритм Флойда
public class Solution {
    public boolean hasCycle(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {
                return true;
            }
        }
        return false;
    }
}
```

#### Ответ от Claude

**Идея.** Алгоритм «черепаха и заяц» (Флойд): если цикл есть, быстрый указатель в итоге догонит медленного внутри цикла. Математически доказывается, что это произойдёт за не более чем `λ + μ` шагов, где `μ` — начало цикла, `λ` — его длина.

```java
public boolean hasCycle(ListNode head) {
    if (head == null || head.next == null) return false;
    ListNode slow = head;
    ListNode fast = head.next; // старт: fast на шаг впереди
    while (slow != fast) {
        if (fast == null || fast.next == null) {
            return false; // конец списка — цикла нет
        }
        slow = slow.next;
        fast = fast.next.next;
    }
    return true; // slow == fast — встретились в цикле
}
```

**Разбор по шагам.** Инициализируем `fast = head.next`, чтобы не проверять `slow == fast` сразу (оба на `head`). В цикле: если `fast` или `fast.next == null` — список конечен, цикла нет. Иначе двигаем оба — при наличии цикла они обязательно встретятся.

**Сложность.** Время O(n), память O(1).

**Типичные ошибки / альтернативы.** Расхождение: оригинал стартует с `slow = fast = head` и проверяет после шага — это эквивалентно, но требует корректного условия цикла `while (fast != null && fast.next != null)`. Для нахождения начала цикла (LC 142) после встречи нужен дополнительный проход.

---

### Вопрос 40. LC 236. Наименьший общий предок (Lowest Common Ancestor of a Binary Tree)

**Категория:** Алгоритмы и структуры данных · Деревья · **Уровень:** Medium

Дано бинарное дерево и два узла `p` и `q`. Найдите наименьшего общего предка (НОП) этих двух узлов. НОП — наиболее глубокий узел, являющийся предком обоих узлов (узел может быть предком самого себя).

**Пример 1.** Вход: `root = [3,5,1,6,2,0,8,null,null,7,4]`, `p = 5`, `q = 1` → Выход: `3`.
**Пример 2.** Вход: `root = [3,5,1,6,2,0,8,null,null,7,4]`, `p = 5`, `q = 4` → Выход: `5`.
**Ограничения:** Число узлов — от 2 до 10^5, все значения уникальны, `p != q`, оба узла гарантированно присутствуют.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Lowest Common Ancestor of a Binary Tree](https://github.com/doocs/leetcode/blob/main/solution/0200-0299/0236.Lowest%20Common%20Ancestor%20of%20a%20Binary%20Tree/README.md)

Рекурсивный обход: если текущий узел `null`, `p` или `q` — возвращаем его. Рекурсивно обходим левое и правое поддеревья. Если оба вернули ненулевое значение — текущий узел и есть НОП. Иначе возвращаем ненулевое из двух. Время O(n), память O(n).

```java
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null || root == p || root == q) {
            return root;
        }
        var left = lowestCommonAncestor(root.left, p, q);
        var right = lowestCommonAncestor(root.right, p, q);
        if (left != null && right != null) {
            return root;
        }
        return left == null ? right : left;
    }
}
```

#### Ответ от Claude

**Идея.** Постордерный обход: сначала ищем в подхеревьях, затем принимаем решение в текущем узле. Логика: если `p` и `q` в разных поддеревьях — НОП здесь; если оба в одном — НОП глубже.

```java
public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
    // Базовый случай: пустой узел или нашли один из искомых
    if (root == null || root == p || root == q) {
        return root;
    }
    // Ищем p и q в левом и правом поддеревьях
    TreeNode leftResult = lowestCommonAncestor(root.left, p, q);
    TreeNode rightResult = lowestCommonAncestor(root.right, p, q);
    // Если нашли в обоих поддеревьях — текущий узел является НОП
    if (leftResult != null && rightResult != null) {
        return root;
    }
    // Иначе возвращаем то поддерево, где что-то нашли
    return leftResult != null ? leftResult : rightResult;
}
```

**Разбор по шагам.** Рекурсия возвращает: `null` (ни `p`, ни `q` не найдены в поддереве), `p` (найден `p`), `q` (найден `q`), или узел НОП. Когда оба `leftResult` и `rightResult` ненулевые — `p` и `q` в разных поддеревьях текущего узла, он и есть ответ.

**Сложность.** Время O(n), память O(n) — стек рекурсии для несбалансированного дерева.

**Типичные ошибки / альтернативы.** Задача чётко отличается от LC 235 (LCA для BST): здесь нельзя использовать свойство BST для навигации. Альтернатива — итеративно с хранением пути от корня до `p` и `q` в `Map<TreeNode, TreeNode>` (родитель): O(n) памяти, нагляднее для отладки.

---

### Вопрос 41. LC 98. Проверка BST (Validate Binary Search Tree)

**Категория:** Алгоритмы и структуры данных · BST / DFS · **Уровень:** Medium

Дан корень бинарного дерева. Проверьте, является ли оно корректным бинарным деревом поиска (BST). BST определяется так: левое поддерево содержит только узлы со значениями меньше корня; правое — только со значениями больше корня; оба поддерева сами являются BST.

**Пример 1.** Вход: `root = [2,1,3]` → Выход: `true`.
**Пример 2.** Вход: `root = [5,1,4,null,null,3,6]` → Выход: `false` (правый ребёнок 4 < 5).
**Ограничения:** Число узлов — от 1 до 10^4, `-2^31 <= Node.val <= 2^31 - 1`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Validate Binary Search Tree](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0098.Validate%20Binary%20Search%20Tree/README.md)

Инордерный обход: в BST он даёт строго возрастающую последовательность. Отслеживаем предыдущий посещённый узел `prev`; если его значение >= текущего — дерево невалидно. Время O(n), память O(n).

```java
class Solution {
    private TreeNode prev;

    public boolean isValidBST(TreeNode root) {
        return dfs(root);
    }

    private boolean dfs(TreeNode root) {
        if (root == null) {
            return true;
        }
        if (!dfs(root.left)) {
            return false;
        }
        if (prev != null && prev.val >= root.val) {
            return false;
        }
        prev = root;
        return dfs(root.right);
    }
}
```

#### Ответ от Claude

**Идея.** Передаём допустимый диапазон `[min, max]` при рекурсии: для каждого узла значение должно быть строго внутри диапазона. При спуске влево — обновляем верхнюю границу, вправо — нижнюю. Это решение избегает изменяемого состояния класса (`prev`).

```java
public boolean isValidBST(TreeNode root) {
    return validate(root, Long.MIN_VALUE, Long.MAX_VALUE);
}

private boolean validate(TreeNode node, long min, long max) {
    if (node == null) return true;
    // Значение должно быть строго внутри диапазона
    if (node.val <= min || node.val >= max) return false;
    // Левое поддерево: верхняя граница — текущее значение
    // Правое поддерево: нижняя граница — текущее значение
    return validate(node.left, min, node.val)
        && validate(node.right, node.val, max);
}
```

**Разбор по шагам.** Используем `long` для границ, чтобы корректно обработать узлы со значениями `Integer.MIN_VALUE` и `Integer.MAX_VALUE`. При спуске вправо новый минимум = `node.val`; при спуске влево новый максимум = `node.val`. Условие строгое (`<`, `>`), что соответствует определению BST без дубликатов.

**Сложность.** Время O(n), память O(n) — стек рекурсии.

**Типичные ошибки / альтернативы.** Расхождение с оригиналом: оригинал использует инордер с изменяемым полем `prev` — оба подхода эквивалентны. Частая ошибка — проверять только прямых детей, а не диапазон: например, `[3,1,4,null,2]` — узел 2 в левом поддереве дерева с корнем 3, но 2 < 3, и наивная проверка это пропустит. Использование `int` вместо `long` для границ — ещё одна типичная ошибка переполнения.

---

### Вопрос 42. LC 230. K-й наименьший в BST (Kth Smallest Element in a BST)

**Категория:** Алгоритмы и структуры данных · BST / inorder · **Уровень:** Medium

Дан корень BST и целое `k`. Верните `k`-й наименьший элемент (1-индексация) среди всех узлов дерева.

**Пример 1.** Вход: `root = [3,1,4,null,2]`, `k = 1` → Выход: `1`.
**Пример 2.** Вход: `root = [5,3,6,2,4,null,null,1]`, `k = 3` → Выход: `3`.
**Ограничения:** Число узлов равно `n`, `1 <= k <= n <= 10^4`, `0 <= Node.val <= 10^4`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Kth Smallest Element in a BST](https://github.com/doocs/leetcode/blob/main/solution/0200-0299/0230.Kth%20Smallest%20Element%20in%20a%20BST/README.md)

Итеративный инордерный обход с явным стеком: обходим узлы в порядке возрастания. Счётчик `k` декрементируется при каждом посещении; когда достигает 0 — возвращаем текущий узел. Время O(k) в лучшем случае, O(n) в худшем, память O(h).

```java
class Solution {
    public int kthSmallest(TreeNode root, int k) {
        Deque<TreeNode> stk = new ArrayDeque<>();
        while (root != null || !stk.isEmpty()) {
            if (root != null) {
                stk.push(root);
                root = root.left;
            } else {
                root = stk.pop();
                if (--k == 0) {
                    return root.val;
                }
                root = root.right;
            }
        }
        return 0;
    }
}
```

#### Ответ от Claude

**Идея.** Инордерный обход BST даёт элементы в порядке возрастания. Рекурсивный вариант с ранним выходом: как только нашли `k`-й, прерываем обход, не обходя остаток дерева.

```java
public int kthSmallest(TreeNode root, int k) {
    int[] counter = {k}; // массив для изменения в лямбде/рекурсии
    int[] result = {0};
    inorder(root, counter, result);
    return result[0];
}

private void inorder(TreeNode node, int[] counter, int[] result) {
    if (node == null || counter[0] == 0) return;
    inorder(node.left, counter, result);
    counter[0]--;
    if (counter[0] == 0) {
        result[0] = node.val;
        return;
    }
    inorder(node.right, counter, result);
}
```

**Разбор по шагам.** Массивы `counter` и `result` позволяют «передавать состояние» через рекурсию без изменяемых полей класса. После посещения узла уменьшаем счётчик; при достижении 0 — сохраняем ответ и выходим. Проверка `counter[0] == 0` в начале — ранний выход из рекурсии.

**Сложность.** Время O(H + k), где H — высота дерева, память O(H).

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует итеративный подход с явным стеком — нагляднее управляет обходом. Рекурсивный подход проще, но может переполнить стек при глубоком дереве (H до 10^4). Если BST часто модифицируется и нужны частые запросы `k`-го, имеет смысл хранить размеры поддеревьев в узлах — тогда O(H) на запрос.

---

### Вопрос 43. LC 33. Поиск в повёрнутом массиве (Search in Rotated Sorted Array)

**Категория:** Алгоритмы и структуры данных · Бинарный поиск · **Уровень:** Medium

Дан целочисленный массив `nums`, отсортированный в порядке возрастания и повёрнутый с неизвестным сдвигом. Дано целое `target`. Если `target` есть в массиве — верните его индекс, иначе верните `-1`. Алгоритм должен работать за O(log n).

**Пример 1.** Вход: `nums = [4,5,6,7,0,1,2]`, `target = 0` → Выход: `4`.
**Пример 2.** Вход: `nums = [4,5,6,7,0,1,2]`, `target = 3` → Выход: `-1`.
**Пример 3.** Вход: `nums = [1]`, `target = 0` → Выход: `-1`.
**Ограничения:** `1 <= nums.length <= 5000`, все элементы уникальны, `nums` повёрнут в случайном месте.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Search in Rotated Sorted Array](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0033.Search%20in%20Rotated%20Sorted%20Array/README.md)

Модифицированный бинарный поиск: определяем, в какой (отсортированной) половине находится `mid`. Если левая часть `[left, mid]` отсортирована и `target` в ней — сужаем вправо, иначе влево. Аналогично для правой части. Время O(log n), память O(1).

```java
class Solution {
    public int search(int[] nums, int target) {
        int n = nums.length;
        int left = 0, right = n - 1;
        while (left < right) {
            int mid = (left + right) >> 1;
            if (nums[0] <= nums[mid]) {
                if (nums[0] <= target && target <= nums[mid]) {
                    right = mid;
                } else {
                    left = mid + 1;
                }
            } else {
                if (nums[mid] < target && target <= nums[n - 1]) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }
        }
        return nums[left] == target ? left : -1;
    }
}
```

#### Ответ от Claude

**Идея.** После поворота ровно одна из двух половин `[left, mid]` и `[mid+1, right]` гарантированно отсортирована. Это ключевое наблюдение позволяет применить бинарный поиск.

```java
public int search(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        // Определяем, какая половина отсортирована
        if (nums[left] <= nums[mid]) {
            // Левая половина [left, mid] отсортирована
            if (target >= nums[left] && target < nums[mid]) {
                right = mid - 1; // target в левой половине
            } else {
                left = mid + 1; // target в правой половине
            }
        } else {
            // Правая половина [mid, right] отсортирована
            if (target > nums[mid] && target <= nums[right]) {
                left = mid + 1; // target в правой половине
            } else {
                right = mid - 1; // target в левой половине
            }
        }
    }
    return -1;
}
```

**Разбор по шагам.** Стандартный бинарный поиск с условием на нахождение отсортированной половины. `nums[left] <= nums[mid]` означает, что левая сторона не содержит точку поворота. Используем `left + (right - left) / 2` во избежание переполнения.

**Сложность.** Время O(log n), память O(1).

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует `nums[0]` вместо `nums[left]` — это другой вариант, работающий при условии уникальности (в данной задаче гарантируется). При дублирующихся элементах (LC 81) логика усложняется. Переполнение при `(left + right) / 2` — типичная ошибка на больших массивах.

---

### Вопрос 44. LC 56. Слияние интервалов (Merge Intervals)

**Категория:** Алгоритмы и структуры данных · Интервалы / сортировка · **Уровень:** Medium

Дан массив `intervals`, где `intervals[i] = [start_i, end_i]`. Объедините все перекрывающиеся интервалы и верните массив неперекрывающихся интервалов, покрывающих все входные.

**Пример 1.** Вход: `intervals = [[1,3],[2,6],[8,10],[15,18]]` → Выход: `[[1,6],[8,10],[15,18]]`.
**Пример 2.** Вход: `intervals = [[1,4],[4,5]]` → Выход: `[[1,5]]` (касающиеся интервалы объединяются).
**Ограничения:** `1 <= intervals.length <= 10^4`, `intervals[i].length == 2`, `0 <= start_i <= end_i <= 10^4`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Merge Intervals](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0056.Merge%20Intervals/README.md)

Сортировка по левой границе, затем линейный проход: если начало нового интервала не превышает конец текущего — расширяем конец; иначе сохраняем текущий и начинаем новый. Время O(n log n), память O(log n) для сортировки.

```java
class Solution {
    public int[][] merge(int[][] intervals) {
        Arrays.sort(intervals, Comparator.comparingInt(a -> a[0]));
        int st = intervals[0][0], ed = intervals[0][1];
        List<int[]> ans = new ArrayList<>();
        for (int i = 1; i < intervals.length; ++i) {
            int s = intervals[i][0], e = intervals[i][1];
            if (ed < s) {
                ans.add(new int[] {st, ed});
                st = s;
                ed = e;
            } else {
                ed = Math.max(ed, e);
            }
        }
        ans.add(new int[] {st, ed});
        return ans.toArray(new int[ans.size()][]);
    }
}
```

#### Ответ от Claude

**Идея.** После сортировки интервалы идут в порядке возрастания левой границы. Последовательно проверяем: если начало следующего <= конец текущего, они перекрываются — расширяем; иначе фиксируем текущий и переходим к следующему.

```java
public int[][] merge(int[][] intervals) {
    Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
    List<int[]> merged = new ArrayList<>();
    int[] current = intervals[0];
    for (int i = 1; i < intervals.length; i++) {
        if (intervals[i][0] <= current[1]) {
            // Интервалы перекрываются (или касаются) — расширяем конец
            current[1] = Math.max(current[1], intervals[i][1]);
        } else {
            // Нет перекрытия — сохраняем текущий, берём следующий
            merged.add(current);
            current = intervals[i];
        }
    }
    merged.add(current); // добавляем последний интервал
    return merged.toArray(new int[merged.size()][]);
}
```

**Разбор по шагам.** Инициализируем `current = intervals[0]`. Для каждого следующего: если `intervals[i][0] <= current[1]` — перекрытие, обновляем правую границу; иначе текущий закончен, добавляем в результат, `current = intervals[i]`. После цикла не забываем добавить последний `current`.

**Сложность.** Время O(n log n), память O(n) для результата.

**Типичные ошибки / альтернативы.** Граничный случай: интервал `[1,4],[4,5]` — начало `4 <= 4` (конец предыдущего), объединяются в `[1,5]`. Избегать `(a[0] - b[0])` в компараторе при больших значениях: возможно переполнение `int`; использовать `Integer.compare`.

---

### Вопрос 45. LC 435. Непересекающиеся интервалы (Non-overlapping Intervals)

**Категория:** Алгоритмы и структуры данных · Интервалы / greedy · **Уровень:** Medium

Дан массив `intervals[i] = [start_i, end_i]`. Верните минимальное количество интервалов, которые нужно удалить, чтобы оставшиеся не пересекались.

**Пример 1.** Вход: `intervals = [[1,2],[2,3],[3,4],[1,3]]` → Выход: `1` (удалить `[1,3]`).
**Пример 2.** Вход: `intervals = [[1,2],[1,2],[1,2]]` → Выход: `2`.
**Пример 3.** Вход: `intervals = [[1,2],[2,3]]` → Выход: `0`.
**Ограничения:** `1 <= intervals.length <= 10^5`, `intervals[i].length == 2`, `-5 * 10^4 <= start_i < end_i <= 5 * 10^4`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Non-overlapping Intervals](https://github.com/doocs/leetcode/blob/main/solution/0400-0499/0435.Non-overlapping%20Intervals/README.md)

Жадный алгоритм: сортируем по правой границе. Жадно оставляем интервал, если его левая граница >= конца последнего принятого. Ответ = общее число − оставленные. Время O(n log n), память O(log n).

```java
class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> a[1] - b[1]);
        int ans = intervals.length;
        int pre = Integer.MIN_VALUE;
        for (var e : intervals) {
            int l = e[0], r = e[1];
            if (pre <= l) {
                --ans;
                pre = r;
            }
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Эквивалентно задаче «максимальное число непересекающихся интервалов» (Activity Selection Problem). Жадная стратегия: всегда выбираем интервал с наименьшим правым краем — это освобождает максимум места для следующих интервалов.

```java
public int eraseOverlapIntervals(int[][] intervals) {
    // Сортируем по правой границе (жадный выбор наименьшего окончания)
    Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));
    int kept = 0; // сколько интервалов оставляем
    int lastEnd = Integer.MIN_VALUE;
    for (int[] interval : intervals) {
        if (interval[0] >= lastEnd) {
            // Нет пересечения с последним оставленным — берём этот
            kept++;
            lastEnd = interval[1];
        }
        // Иначе — интервал пересекается, удаляем (не учитываем)
    }
    return intervals.length - kept;
}
```

**Разбор по шагам.** После сортировки по правой границе: если левый край текущего интервала `>= lastEnd` (конца последнего принятого) — они не пересекаются, берём его. Касание `[1,2],[2,3]` — не пересечение, оба берём. Ответ = total − kept.

**Сложность.** Время O(n log n), память O(1) (не считая сортировки).

**Типичные ошибки / альтернативы.** Расхождение с оригиналом: оригинал считает удаляемые (`ans = n`, декрементирует при принятии), данное решение считает принятые. Использовать `Integer.compare` вместо `a[1] - b[1]` в компараторе — безопаснее при отрицательных значениях. Пересечение: `[1,2]` и `[2,3]` пересекаются только если `start2 < end1` (строго), касание не считается.

---

### Вопрос 46. LC 739. Дневные температуры (Daily Temperatures)

**Категория:** Алгоритмы и структуры данных · Монотонный стек · **Уровень:** Medium

Дан массив `temperatures`, где `temperatures[i]` — температура в день `i`. Верните массив `answer`, где `answer[i]` — количество дней, которое нужно ждать после дня `i` до более тёплого дня. Если более тёплого дня нет, `answer[i] = 0`.

**Пример 1.** Вход: `temperatures = [73,74,75,71,69,72,76,73]` → Выход: `[1,1,4,2,1,1,0,0]`.
**Пример 2.** Вход: `temperatures = [30,40,50,60]` → Выход: `[1,1,1,0]`.
**Ограничения:** `1 <= temperatures.length <= 10^5`, `30 <= temperatures[i] <= 100`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Daily Temperatures](https://github.com/doocs/leetcode/blob/main/solution/0700-0799/0739.Daily%20Temperatures/README.md)

Монотонный стек с обходом справа налево: поддерживаем убывающий стек индексов. Для каждого дня `i` выталкиваем из стека все индексы с температурой <= `temperatures[i]`, затем вычисляем разницу. Время O(n), память O(n).

```java
class Solution {
    public int[] dailyTemperatures(int[] temperatures) {
        int n = temperatures.length;
        Deque<Integer> stk = new ArrayDeque<>();
        int[] ans = new int[n];
        for (int i = n - 1; i >= 0; --i) {
            while (!stk.isEmpty() && temperatures[stk.peek()] <= temperatures[i]) {
                stk.pop();
            }
            if (!stk.isEmpty()) {
                ans[i] = stk.peek() - i;
            }
            stk.push(i);
        }
        return ans;
    }
}
```

#### Ответ от Claude

**Идея.** Монотонный убывающий стек с обходом слева направо: когда видим температуру выше верхушки стека, мы нашли ответ для всех индексов в стеке с меньшей температурой. Это «раскрытие» стека происходит не чаще n раз суммарно — отсюда O(n).

```java
public int[] dailyTemperatures(int[] temperatures) {
    int n = temperatures.length;
    int[] answer = new int[n]; // по умолчанию 0
    Deque<Integer> stack = new ArrayDeque<>(); // стек индексов (убывающий по температуре)
    for (int i = 0; i < n; i++) {
        // Пока стек не пуст и текущая температура выше, чем у вершины стека
        while (!stack.isEmpty() && temperatures[i] > temperatures[stack.peek()]) {
            int prevIdx = stack.pop();
            answer[prevIdx] = i - prevIdx; // нашли ответ для prevIdx
        }
        stack.push(i);
    }
    // Оставшиеся в стеке индексы — answer[i] = 0 (более тёплого дня нет)
    return answer;
}
```

**Разбор по шагам.** Проходим слева направо. Стек хранит индексы дней, для которых ещё не найден более тёплый день (температуры убывают от низа к верху). Как только текущая температура выше верхушки — раскрываем стек, вычисляя разницу индексов.

**Сложность.** Время O(n), память O(n).

**Типичные ошибки / альтернативы.** Расхождение: оригинал идёт справа налево; данный вариант — слева направо. Оба корректны. Левосторонний обход нагляднее: «нашли ответ» прямо в момент обнаружения. Стек хранит индексы, а не значения — это важно для вычисления расстояния.

---

### Вопрос 47. LC 215. K-й по величине элемент (Kth Largest Element in an Array)

**Категория:** Алгоритмы и структуры данных · Heap / Quickselect · **Уровень:** Medium

Дан целочисленный массив `nums` и целое `k`. Верните `k`-й по величине элемент в массиве. Учтите, что это `k`-й по величине в отсортированном порядке, а не `k`-й уникальный.

**Пример 1.** Вход: `nums = [3,2,1,5,6,4]`, `k = 2` → Выход: `5`.
**Пример 2.** Вход: `nums = [3,2,3,1,2,4,5,5,6]`, `k = 4` → Выход: `4`.
**Ограничения:** `1 <= k <= nums.length <= 10^5`, `-10^4 <= nums[i] <= 10^4`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Kth Largest Element in an Array](https://github.com/doocs/leetcode/blob/main/solution/0200-0299/0215.Kth%20Largest%20Element%20in%20an%20Array/README.md)

Quickselect с разбиением Хоара: ищем `(n-k)`-й наименьший. При каждом разбиении рекурсивно углубляемся только в нужную половину. Время O(n) в среднем, O(n²) в худшем, память O(log n).

```java
class Solution {
    private int[] nums;
    private int k;

    public int findKthLargest(int[] nums, int k) {
        this.nums = nums;
        this.k = nums.length - k;
        return quickSort(0, nums.length - 1);
    }

    private int quickSort(int l, int r) {
        if (l == r) {
            return nums[l];
        }
        int i = l - 1, j = r + 1;
        int x = nums[(l + r) >>> 1];
        while (i < j) {
            while (nums[++i] < x) {}
            while (nums[--j] > x) {}
            if (i < j) {
                int t = nums[i];
                nums[i] = nums[j];
                nums[j] = t;
            }
        }
        if (j < k) {
            return quickSort(j + 1, r);
        }
        return quickSort(l, j);
    }
}
```

#### Ответ от Claude

**Идея.** Мин-куча размером `k`: проходим по массиву, поддерживая кучу из `k` наибольших элементов. Когда куча переполняется — вытаскиваем минимум. В конце вершина кучи — `k`-й наибольший.

```java
public int findKthLargest(int[] nums, int k) {
    // Мин-куча: хранит k наибольших элементов, вершина — минимум из них
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();
    for (int num : nums) {
        minHeap.offer(num);
        if (minHeap.size() > k) {
            minHeap.poll(); // удаляем наименьший из k+1 элементов
        }
    }
    return minHeap.peek(); // k-й наибольший
}
```

**Разбор по шагам.** Добавляем каждый элемент в кучу. Если размер > `k`, удаляем минимум — это элемент, не попадающий в `k` наибольших. После прохода в куче ровно `k` наибольших элементов, вершина — `k`-й наибольший.

**Сложность.** Время O(n log k), память O(k).

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует Quickselect — O(n) в среднем, но O(n²) в худшем и модифицирует массив. Куча — O(n log k), но предсказуема и не изменяет входные данные. При k << n куча эффективнее практически. Сортировка — O(n log n) — проще всего, но избыточна.

---

### Вопрос 48. LC 200. Число островов (Number of Islands)

**Категория:** Алгоритмы и структуры данных · Графы / DFS·BFS · **Уровень:** Medium

Дана бинарная матрица `grid` из символов `'1'` (суша) и `'0'` (вода). Остров — максимальная связная область суши (4-связность: вверх, вниз, влево, вправо). Верните количество островов.

**Пример 1.** Вход: 4×5 матрица с тремя кластерами `'1'` → Выход: `3`.
**Пример 2.** Вход: 4×4 матрица, одна большая связная область → Выход: `1`.
**Ограничения:** `1 <= m, n <= 300`, `grid[i][j]` — `'0'` или `'1'`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Number of Islands](https://github.com/doocs/leetcode/blob/main/solution/0200-0299/0200.Number%20of%20Islands/README.md)

DFS с «затоплением»: для каждой ячейки `'1'` запускаем DFS, помечая все связанные клетки суши как `'0'` (посещённые). Количество запусков DFS — количество островов. Время O(m×n), память O(m×n) для стека рекурсии.

```java
class Solution {
    private char[][] grid;
    private int m, n;

    public int numIslands(char[][] grid) {
        m = grid.length; n = grid[0].length;
        this.grid = grid;
        int ans = 0;
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < n; ++j) {
                if (grid[i][j] == '1') {
                    dfs(i, j);
                    ++ans;
                }
            }
        }
        return ans;
    }

    private void dfs(int i, int j) {
        grid[i][j] = '0';
        int[] dirs = {-1, 0, 1, 0, -1};
        for (int k = 0; k < 4; ++k) {
            int x = i + dirs[k], y = j + dirs[k + 1];
            if (x >= 0 && x < m && y >= 0 && y < n && grid[x][y] == '1') {
                dfs(x, y);
            }
        }
    }
}
```

#### Ответ от Claude

**Идея.** BFS-вариант с явной очередью — избегает рекурсивного стека (полезно для больших матриц). Помечаем посещённые клетки как `'0'` прямо при добавлении в очередь, а не при извлечении — это предотвращает дублирование.

```java
public int numIslands(char[][] grid) {
    int m = grid.length, n = grid[0].length;
    int islands = 0;
    int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (grid[i][j] == '1') {
                islands++;
                // BFS: затапливаем весь остров
                Queue<int[]> queue = new LinkedList<>();
                queue.offer(new int[]{i, j});
                grid[i][j] = '0'; // помечаем сразу при добавлении
                while (!queue.isEmpty()) {
                    int[] cell = queue.poll();
                    for (int[] d : dirs) {
                        int ni = cell[0] + d[0], nj = cell[1] + d[1];
                        if (ni >= 0 && ni < m && nj >= 0 && nj < n
                                && grid[ni][nj] == '1') {
                            grid[ni][nj] = '0';
                            queue.offer(new int[]{ni, nj});
                        }
                    }
                }
            }
        }
    }
    return islands;
}
```

**Разбор по шагам.** Внешний цикл ищет незатопленную сушу. При нахождении увеличиваем счётчик и запускаем BFS от этой клетки. Все достижимые клетки `'1'` переводятся в `'0'` — «затапливаем» остров. Следующая `'1'` во внешнем цикле будет уже новым островом.

**Сложность.** Время O(m×n), память O(min(m,n)) для очереди BFS в худшем случае (при узком острове).

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует DFS — проще в коде, но глубина рекурсии до m×n (300×300 = 90000) может переполнить стек JVM. BFS с явной очередью безопаснее. Если нельзя модифицировать матрицу — использовать дополнительный `boolean[][] visited`.

---

### Вопрос 49. LC 207. Расписание курсов (Course Schedule)

**Категория:** Алгоритмы и структуры данных · Графы / топосортировка · **Уровень:** Medium

Вам нужно пройти `numCourses` курсов (от 0 до numCourses-1). Некоторые курсы имеют предпосылки: `prerequisites[i] = [a, b]` означает, что перед `a` нужно пройти `b`. Можно ли пройти все курсы?

**Пример 1.** Вход: `numCourses = 2`, `prerequisites = [[1,0]]` → Выход: `true`.
**Пример 2.** Вход: `numCourses = 2`, `prerequisites = [[1,0],[0,1]]` → Выход: `false` (циклическая зависимость).
**Ограничения:** `1 <= numCourses <= 2000`, `0 <= prerequisites.length <= 5000`.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Course Schedule](https://github.com/doocs/leetcode/blob/main/solution/0200-0299/0207.Course%20Schedule/README.md)

Топологическая сортировка (алгоритм Кана): строим граф зависимостей и массив входящих степеней. Добавляем в очередь вершины с нулевой входящей степенью. При обработке вершины уменьшаем степени соседей — новые нулевые добавляем в очередь. Если обработали все вершины — цикла нет. Время O(n+m), память O(n+m).

```java
class Solution {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        List<Integer>[] g = new List[numCourses];
        Arrays.setAll(g, k -> new ArrayList<>());
        int[] indeg = new int[numCourses];
        for (var p : prerequisites) {
            int a = p[0], b = p[1];
            g[b].add(a);
            ++indeg[a];
        }
        Deque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < numCourses; ++i) {
            if (indeg[i] == 0) {
                q.offer(i);
            }
        }
        while (!q.isEmpty()) {
            int i = q.poll();
            --numCourses;
            for (int j : g[i]) {
                if (--indeg[j] == 0) {
                    q.offer(j);
                }
            }
        }
        return numCourses == 0;
    }
}
```

#### Ответ от Claude

**Идея.** DFS с трёхцветной раскраской: белый (непосещён), серый (в процессе), чёрный (завершён). Если при обходе попадаем в серую вершину — найден цикл, возвращаем `false`.

```java
public boolean canFinish(int numCourses, int[][] prerequisites) {
    List<List<Integer>> graph = new ArrayList<>();
    for (int i = 0; i < numCourses; i++) graph.add(new ArrayList<>());
    for (int[] pre : prerequisites) {
        graph.get(pre[1]).add(pre[0]);
    }
    // 0 = непосещён, 1 = в обходе (серый), 2 = завершён (чёрный)
    int[] state = new int[numCourses];
    for (int i = 0; i < numCourses; i++) {
        if (state[i] == 0 && hasCycle(graph, state, i)) {
            return false;
        }
    }
    return true;
}

private boolean hasCycle(List<List<Integer>> graph, int[] state, int node) {
    state[node] = 1; // помечаем как «в обходе»
    for (int neighbor : graph.get(node)) {
        if (state[neighbor] == 1) return true;  // назад — цикл
        if (state[neighbor] == 0 && hasCycle(graph, state, neighbor)) return true;
    }
    state[node] = 2; // завершили обход вершины
    return false;
}
```

**Разбор по шагам.** Для каждой непосещённой вершины запускаем DFS. Серый цвет означает «сейчас в стеке вызовов» — если встречаем серую вершину, нашли обратное ребро (цикл). Чёрный означает «полностью обработан» — повторно обходить не нужно.

**Сложность.** Время O(n+m), память O(n+m).

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует BFS (алгоритм Кана), данное решение — DFS. Оба эквивалентны. Типичная ошибка с DFS: использовать только `boolean[] visited` вместо трёхцветной схемы — тогда нельзя отличить «в процессе» от «завершён», и алгоритм ошибётся.

---

### Вопрос 50. LC 76. Минимальное окно-подстрока (Minimum Window Substring)

**Категория:** Алгоритмы и структуры данных · Sliding Window · **Уровень:** Medium

Даны строки `s` и `t`. Верните наименьшую подстроку `s`, которая содержит все символы `t` (с учётом повторений). Если такой подстроки нет — верните пустую строку `""`.

**Пример 1.** Вход: `s = "ADOBECODEBANC"`, `t = "ABC"` → Выход: `"BANC"`.
**Пример 2.** Вход: `s = "a"`, `t = "a"` → Выход: `"a"`.
**Пример 3.** Вход: `s = "a"`, `t = "b"` → Выход: `""`.
**Ограничения:** `1 <= s.length, t.length <= 10^5`, `s` и `t` состоят из ASCII-символов.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Minimum Window Substring](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0076.Minimum%20Window%20Substring/README.md)

Скользящее окно с частотными массивами: `need` хранит нужные частоты символов `t`, `window` — текущие. Счётчик `cnt` отслеживает, сколько символов из `t` покрыто. Когда `cnt == |t|` — сжимаем окно слева. Время O(m+n), память O(|Σ|).

```java
class Solution {
    public String minWindow(String s, String t) {
        int[] need = new int[128];
        int[] window = new int[128];
        for (char c : t.toCharArray()) {
            ++need[c];
        }
        int m = s.length(), n = t.length();
        int k = -1, mi = m + 1, cnt = 0;
        for (int l = 0, r = 0; r < m; ++r) {
            char c = s.charAt(r);
            if (++window[c] <= need[c]) {
                ++cnt;
            }
            while (cnt == n) {
                if (r - l + 1 < mi) {
                    mi = r - l + 1;
                    k = l;
                }
                c = s.charAt(l);
                if (window[c] <= need[c]) {
                    --cnt;
                }
                --window[c];
                ++l;
            }
        }
        return k < 0 ? "" : s.substring(k, k + mi);
    }
}
```

#### Ответ от Claude

**Идея.** Скользящее окно с двумя `HashMap`: расширяем вправо, пока не покроем все символы `t`; затем сжимаем слева до минимума. Переменная `formed` отслеживает число уникальных символов, покрытых с нужной частотой.

```java
public String minWindow(String s, String t) {
    if (s.isEmpty() || t.isEmpty()) return "";
    Map<Character, Integer> need = new HashMap<>();
    for (char c : t.toCharArray()) need.merge(c, 1, Integer::sum);
    int required = need.size(); // число уникальных символов в t
    int formed = 0; // сколько уникальных символов покрыто с нужной частотой
    Map<Character, Integer> window = new HashMap<>();
    int left = 0, minLen = Integer.MAX_VALUE, minLeft = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        window.merge(c, 1, Integer::sum);
        // Проверяем, закрыт ли очередной уникальный символ
        if (need.containsKey(c) && window.get(c).equals(need.get(c))) {
            formed++;
        }
        // Сжимаем окно пока все символы покрыты
        while (formed == required) {
            if (right - left + 1 < minLen) {
                minLen = right - left + 1;
                minLeft = left;
            }
            char leftChar = s.charAt(left);
            window.merge(leftChar, -1, Integer::sum);
            if (need.containsKey(leftChar)
                    && window.get(leftChar) < need.get(leftChar)) {
                formed--;
            }
            left++;
        }
    }
    return minLen == Integer.MAX_VALUE ? "" : s.substring(minLeft, minLeft + minLen);
}
```

**Разбор по шагам.** `need` — частоты символов `t`. `formed` — число уникальных символов, у которых частота в окне >= нужной. Когда `formed == required` — нашли валидное окно, пробуем сократить слева. При уменьшении частоты символа ниже нужной — `formed--`, выходим из внутреннего цикла.

**Сложность.** Время O(m+n), память O(|Σ|).

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует массивы `int[128]` вместо HashMap — быстрее и лаконичнее. Подход с `formed` нагляднее для понимания. Сравнение `Integer` объектов через `==` вместо `.equals()` — частая ошибка автоупаковки в Java.

---

### Вопрос 51. LC 23. Слияние k списков (Merge k Sorted Lists)

**Категория:** Алгоритмы и структуры данных · Heap / связные списки · **Уровень:** Medium

Дан массив из `k` отсортированных по возрастанию связных списков. Объедините их в один отсортированный список.

**Пример 1.** Вход: `lists = [[1,4,5],[1,3,4],[2,6]]` → Выход: `[1,1,2,3,4,4,5,6]`.
**Пример 2.** Вход: `lists = []` → Выход: `[]`.
**Пример 3.** Вход: `lists = [[]]` → Выход: `[]`.
**Ограничения:** `k == lists.length`, `0 <= k <= 10^4`, `0 <= lists[i].length <= 500`, общее число узлов до 10^4.

#### Оригинальный ответ из интернета
> Источник: [doocs/leetcode — Merge k Sorted Lists](https://github.com/doocs/leetcode/blob/main/solution/0000-0099/0023.Merge%20k%20Sorted%20Lists/README.md)

Мин-куча из заголовков: добавляем все непустые головы в `PriorityQueue` с компаратором по значению. Извлекаем минимальный узел, добавляем в результат, и если у него есть следующий — добавляем его в кучу. Время O(n log k), память O(k).

```java
class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> a.val - b.val);
        for (ListNode head : lists) {
            if (head != null) {
                pq.offer(head);
            }
        }
        ListNode dummy = new ListNode();
        ListNode cur = dummy;
        while (!pq.isEmpty()) {
            ListNode node = pq.poll();
            if (node.next != null) {
                pq.offer(node.next);
            }
            cur.next = node;
            cur = cur.next;
        }
        return dummy.next;
    }
}
```

#### Ответ от Claude

**Идея.** Классический подход «разделяй и властвуй»: рекурсивно делим массив списков пополам и сливаем попарно. Позволяет избежать изменяемой кучи и хорошо параллелизуется.

```java
public ListNode mergeKLists(ListNode[] lists) {
    if (lists == null || lists.length == 0) return null;
    return mergeRange(lists, 0, lists.length - 1);
}

private ListNode mergeRange(ListNode[] lists, int left, int right) {
    if (left == right) return lists[left];
    int mid = left + (right - left) / 2;
    ListNode l1 = mergeRange(lists, left, mid);
    ListNode l2 = mergeRange(lists, mid + 1, right);
    return mergeTwoLists(l1, l2);
}

private ListNode mergeTwoLists(ListNode l1, ListNode l2) {
    ListNode dummy = new ListNode(0);
    ListNode curr = dummy;
    while (l1 != null && l2 != null) {
        if (l1.val <= l2.val) {
            curr.next = l1;
            l1 = l1.next;
        } else {
            curr.next = l2;
            l2 = l2.next;
        }
        curr = curr.next;
    }
    curr.next = (l1 != null) ? l1 : l2;
    return dummy.next;
}
```

**Разбор по шагам.** `mergeRange` делит `[left, right]` пополам, рекурсивно сливает каждую половину, затем объединяет два результата через `mergeTwoLists`. Базовый случай: один список — возвращаем его. `mergeTwoLists` — стандартное слияние двух отсортированных списков (LC 21).

**Сложность.** Время O(n log k), память O(log k) для стека рекурсии.

**Типичные ошибки / альтернативы.** Расхождение: оригинал использует мин-кучу — O(n log k) время и O(k) память. Подход «разделяй и властвуй» имеет ту же временную сложность, но меньше доп. памяти. Наивное последовательное слияние — O(nk) время. Компаратор `(a, b) -> a.val - b.val` может переполниться при крайних значениях `int`; безопаснее `Integer.compare(a.val, b.val)`.

---
