# Урок 5. Алгоритмы

**Трейл:** Collections · **Оригинал:** [Algorithms](https://docs.oracle.com/javase/tutorial/collections/algorithms/index.html)
**Связанные области:** [[03-collections]] · [[12-algorithms-data-structures]] · **Вопросы:** collections

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

Описанные здесь **полиморфные алгоритмы** (*polymorphic algorithms*) — это готовые переиспользуемые
блоки функциональности, предоставляемые платформой Java. Все они находятся в классе
[`Collections`](https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html) и оформлены в
виде статических методов, первым аргументом которых является коллекция, над которой выполняется
операция. Подавляющее большинство алгоритмов, предоставляемых платформой Java, работают с
экземплярами [`List`](https://docs.oracle.com/javase/8/docs/api/java/util/List.html), но некоторые
из них работают с произвольными экземплярами
[`Collection`](https://docs.oracle.com/javase/8/docs/api/java/util/Collection.html). В этом разделе
кратко описываются следующие алгоритмы:

- [Сортировка](#сортировка-sorting)
- [Перемешивание](#перемешивание-shuffling)
- [Рутинная обработка данных](#рутинная-обработка-данных-routine-data-manipulation)
- [Поиск](#поиск-searching)
- [Композиция](#композиция-composition)
- [Поиск экстремальных значений](#поиск-экстремальных-значений-finding-extreme-values)

## Сортировка (Sorting)

Алгоритм `sort` переупорядочивает `List` так, чтобы его элементы располагались по возрастанию в
соответствии с отношением порядка. Предоставляются две формы этой операции. Простая форма
принимает `List` и сортирует его согласно **естественному порядку** (*natural ordering*) его
элементов. Если вам незнакомо понятие естественного порядка, прочитайте раздел
[Object Ordering](https://docs.oracle.com/javase/tutorial/collections/interfaces/order.html).

Операция `sort` использует слегка оптимизированный алгоритм **сортировки слиянием**
(*merge sort*), который быстр и устойчив:

- **Быстрый** (*Fast*): гарантированно работает за время `n log(n)` и существенно быстрее на почти
  отсортированных списках. Эмпирические тесты показали, что он так же быстр, как сильно
  оптимизированная быстрая сортировка (*quicksort*). Быструю сортировку обычно считают быстрее
  сортировки слиянием, но она не устойчива и не гарантирует производительность `n log(n)`.
- **Устойчивый** (*Stable*): он не переупорядочивает равные элементы. Это важно, если вы сортируете
  один и тот же список многократно по разным признакам. Если пользователь почтовой программы
  сортирует входящие сначала по дате отправки, а затем по отправителю, он естественно ожидает,
  что теперь идущий подряд список сообщений от конкретного отправителя будет (по-прежнему)
  отсортирован по дате отправки. Это гарантируется, только если вторая сортировка была устойчивой.

Следующая [тривиальная программа](https://docs.oracle.com/javase/tutorial/collections/algorithms/examples/Sort.java)
выводит свои аргументы в лексикографическом (алфавитном) порядке.

```java
import java.util.*;

public class Sort {
    public static void main(String[] args) {
        List<String> list = Arrays.asList(args);
        Collections.sort(list);
        System.out.println(list);
    }
}
```

Запустим программу.

```
% java Sort i walk the line
```

Получается следующий вывод.

```
[i, line, the, walk]
```

Эта программа была приведена лишь для того, чтобы показать вам, что алгоритмы действительно
настолько просты в использовании, насколько это выглядит.

Вторая форма `sort` принимает, помимо `List`, ещё и
[`Comparator`](https://docs.oracle.com/javase/8/docs/api/java/util/Comparator.html) (компаратор) и
сортирует элементы с помощью этого `Comparator`. Предположим, вы хотите вывести группы анаграмм из
нашего предыдущего примера в обратном порядке по размеру — сначала самую большую группу анаграмм.
Пример ниже показывает, как этого добиться с помощью второй формы метода `sort`.

Напомним, что группы анаграмм хранятся как значения в `Map` в виде экземпляров `List`.
Переработанный код печати проходит по представлению значений `Map`, помещая каждый `List`,
который проходит проверку на минимальный размер, в `List` из `List`-ов. Затем код сортирует этот
`List`, используя `Comparator`, который ожидает экземпляры `List` и реализует упорядочивание по
убыванию размера. Наконец, код проходит по отсортированному `List` и печатает его элементы (группы
анаграмм). Следующий код заменяет код печати в конце метода `main` в примере `Anagrams`.

```java
// Составить List из всех групп анаграмм, превышающих порог размера.
List<List<String>> winners = new ArrayList<List<String>>();
for (List<String> l : m.values())
    if (l.size() >= minGroupSize)
        winners.add(l);

// Отсортировать группы анаграмм по размеру
Collections.sort(winners, new Comparator<List<String>>() {
    public int compare(List<String> o1, List<String> o2) {
        return o2.size() - o1.size();
    }});

// Напечатать группы анаграмм.
for (List<String> l : winners)
    System.out.println(l.size() + ": " + l);
```

Запуск [этой программы](https://docs.oracle.com/javase/tutorial/collections/algorithms/examples/Anagrams2.java)
на [том же словаре](https://docs.oracle.com/javase/tutorial/collections/interfaces/examples/dictionary.txt),
что и в разделе [The Map Interface](https://docs.oracle.com/javase/tutorial/collections/interfaces/map.html),
с тем же минимальным размером группы анаграмм (восемь), даёт следующий вывод.

```
12: [apers, apres, asper, pares, parse, pears, prase,
       presa, rapes, reaps, spare, spear]
11: [alerts, alters, artels, estral, laster, ratels,
       salter, slater, staler, stelar, talers]
10: [least, setal, slate, stale, steal, stela, taels,
       tales, teals, tesla]
9: [estrin, inerts, insert, inters, niters, nitres,
       sinter, triens, trines]
9: [capers, crapes, escarp, pacers, parsec, recaps,
       scrape, secpar, spacer]
9: [palest, palets, pastel, petals, plates, pleats,
       septal, staple, tepals]
9: [anestri, antsier, nastier, ratines, retains, retinas,
       retsina, stainer, stearin]
8: [lapse, leaps, pales, peals, pleas, salep, sepal, spale]
8: [aspers, parses, passer, prases, repass, spares,
       sparse, spears]
8: [enters, nester, renest, rentes, resent, tenser,
       ternes,, treens]
8: [arles, earls, lares, laser, lears, rales, reals, seral]
8: [earings, erasing, gainers, reagins, regains, reginas,
       searing, seringa]
8: [peris, piers, pries, prise, ripes, speir, spier, spire]
8: [ates, east, eats, etas, sate, seat, seta, teas]
8: [carets, cartes, caster, caters, crates, reacts,
       recast,, traces]
```

## Перемешивание (Shuffling)

Алгоритм `shuffle` делает противоположное тому, что делает `sort`: он уничтожает любые следы
порядка, которые могли присутствовать в `List`. То есть этот алгоритм переупорядочивает `List` на
основе данных из источника случайности так, что все возможные перестановки возникают с равной
вероятностью (при условии честного источника случайности). Этот алгоритм полезен при реализации
азартных игр. Например, его можно использовать, чтобы перемешать `List` объектов `Card`,
представляющих колоду. Также он полезен для генерации тестовых случаев.

У этой операции две формы: одна принимает `List` и использует источник случайности по умолчанию, а
другая требует, чтобы вызывающий код предоставил объект
[`Random`](https://docs.oracle.com/javase/8/docs/api/java/util/Random.html) для использования в
качестве источника случайности. Код этого алгоритма используется как пример в
[разделе `List`](https://docs.oracle.com/javase/tutorial/collections/interfaces/list.html#shuffle).

## Рутинная обработка данных (Routine Data Manipulation)

Класс `Collections` предоставляет пять алгоритмов для выполнения рутинной обработки данных над
объектами `List`, все из которых довольно прямолинейны:

- `reverse` — меняет порядок элементов в `List` на обратный.
- `fill` — перезаписывает каждый элемент в `List` указанным значением. Эта операция полезна для
  повторной инициализации `List`.
- `copy` — принимает два аргумента, `List`-приёмник и `List`-источник, и копирует элементы
  источника в приёмник, перезаписывая его содержимое. `List`-приёмник должен быть как минимум такой
  же длины, как источник. Если он длиннее, то оставшиеся элементы в `List`-приёмнике не
  затрагиваются.
- `swap` — меняет местами элементы на указанных позициях в `List`.
- `addAll` — добавляет все указанные элементы в `Collection`. Добавляемые элементы могут быть
  указаны по отдельности или как массив.

## Поиск (Searching)

Алгоритм `binarySearch` ищет указанный элемент в отсортированном `List`. У этого алгоритма две
формы. Первая принимает `List` и элемент для поиска («ключ поиска», *search key*). Эта форма
предполагает, что `List` отсортирован по возрастанию согласно естественному порядку его элементов.
Вторая форма принимает, помимо `List` и ключа поиска, ещё и `Comparator` и предполагает, что `List`
отсортирован по возрастанию согласно указанному `Comparator`. Алгоритм `sort` можно использовать
для сортировки `List` перед вызовом `binarySearch`.

Возвращаемое значение одинаково для обеих форм. Если `List` содержит ключ поиска, возвращается его
индекс. Если нет, возвращаемое значение равно `(-(точка вставки) - 1)`, где точка вставки — это
точка, в которую значение было бы вставлено в `List`, то есть индекс первого элемента, большего
указанного значения, или `list.size()`, если все элементы в `List` меньше указанного значения. Эта
по общему признанию некрасивая формула гарантирует, что возвращаемое значение будет `>= 0` тогда и
только тогда, когда ключ поиска найден. По сути это хак, объединяющий булево значение «найдено»
(*found*) и целочисленный индекс (*index*) в одно возвращаемое значение типа `int`.

Следующая идиома, применимая с обеими формами операции `binarySearch`, ищет указанный ключ поиска
и вставляет его на подходящую позицию, если его там ещё нет.

```java
int pos = Collections.binarySearch(list, key);
if (pos < 0)
   l.add(-pos-1, key);
```

## Композиция (Composition)

Алгоритмы `frequency` и `disjoint` проверяют некоторый аспект состава одной или нескольких
коллекций (`Collections`):

- `frequency` — подсчитывает, сколько раз указанный элемент встречается в указанной коллекции;
- `disjoint` — определяет, являются ли две коллекции (`Collections`) непересекающимися, то есть не
  содержат ли они общих элементов.

## Поиск экстремальных значений (Finding Extreme Values)

Алгоритмы `min` и `max` возвращают, соответственно, минимальный и максимальный элемент,
содержащийся в указанной коллекции (`Collection`). Обе эти операции имеют по две формы. Простая
форма принимает только `Collection` и возвращает минимальный (или максимальный) элемент согласно
естественному порядку элементов. Вторая форма принимает, помимо `Collection`, ещё и `Comparator` и
возвращает минимальный (или максимальный) элемент согласно указанному `Comparator`.

## Источник

- [Algorithms](https://docs.oracle.com/javase/tutorial/collections/algorithms/index.html) — официальное руководство Oracle (The Java Tutorials).
</content>
</invoke>
