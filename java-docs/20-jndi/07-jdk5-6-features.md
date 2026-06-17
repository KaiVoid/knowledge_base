# Урок 7. Возможности в JDK 5.0 и JDK 6

**Трейл:** JNDI · **Оригинал:** [Features in JDK 5.0 and JDK 6](https://docs.oracle.com/javase/tutorial/jndi/newstuff/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

В этом уроке мы рассмотрим перечисленные ниже новые возможности, которые поддерживаются JNDI и
поставщиком службы LDAP (LDAP Service provider) в выпусках JDK 5.0 и JDK 6.

- [Получение различающегося имени (DN) из результата поиска](#получение-различающегося-имени-distinguished-name).
- [Использование стандартных элементов управления LDAP (standard LDAP controls)](#стандартные-элементы-управления-ldap-standard-ldap-controls).
- [Манипулирование именами LDAP](#манипулирование-ldapname-различающимся-именем).
- [Установка тайм-аута чтения для операций LDAP](#установка-тайм-аута-для-операций-ldap).

## Получение различающегося имени (Distinguished Name)

В выпусках JDK до версии 5.0 не было прямого способа получить различающееся имя (Distinguished
Name, DN) из результатов поиска. Метод `SearchResults.getName()` всегда возвращает имя,
заданное относительно контекста, на котором выполняется поиск. Чтобы получить абсолютное, или
полное, имя записи поиска, требовался определённый учёт (book-keeping) для отслеживания
контекстов-предков. В JDK 5.0 добавлены два новых API (см. ниже) для получения абсолютного имени
из `NameClassPair` всякий раз, когда над контекстом выполняется операция `search`, `list` или
`listBindings`:

- [`NameClassPair.getNameInNameSpace(Name name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NameClassPair.html#getNameInNamespace-Name-)
- [`NameClassPair.getNameInNameSpace(String name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NameClassPair.html#getNameInNamespace-String-)

Вот пример, который извлекает различающиеся имена (DN) из результата LDAP-поиска:

```java
public static void printSearchEnumeration(NamingEnumeration retEnum) {
    try {
        while (retEnum.hasMore()) {
            SearchResult sr = (SearchResult) retEnum.next();
            System.out.println(">>" + sr.getNameInNamespace());
        }
    } catch (NamingException e) {
        e.printStackTrace();
    }
}
```

Полный пример можно получить [здесь](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/FullName.java).
Эта программа выводит следующий результат:

```
>>cn=Jon Ruiz, ou=People, o=JNDITutorial
>>cn=Scott Seligman, ou=People, o=JNDITutorial
>>cn=Samuel Clemens, ou=People, o=JNDITutorial
>>cn=Rosanna Lee, ou=People, o=JNDITutorial
>>cn=Maxine Erlund, ou=People, o=JNDITutorial
>>cn=Niels Bohr, ou=People, o=JNDITutorial
>>cn=Uri Geller, ou=People, o=JNDITutorial
>>cn=Colleen Sullivan, ou=People, o=JNDITutorial
>>cn=Vinnie Ryan, ou=People, o=JNDITutorial
>>cn=Rod Serling, ou=People, o=JNDITutorial
>>cn=Jonathan Wood, ou=People, o=JNDITutorial
>>cn=Aravindan Ranganathan, ou=People, o=JNDITutorial
>>cn=Ian Anderson, ou=People, o=JNDITutorial
>>cn=Lao Tzu, ou=People, o=JNDITutorial
>>cn=Don Knuth, ou=People, o=JNDITutorial
>>cn=Roger Waters, ou=People, o=JNDITutorial
>>cn=Ben Dubin, ou=People, o=JNDITutorial
>>cn=Spuds Mackenzie, ou=People, o=JNDITutorial
>>cn=John Fowler, ou=People, o=JNDITutorial
>>cn=Londo Mollari, ou=People, o=JNDITutorial
>>cn=Ted Geisel, ou=People,o=JNDITutorial
```

## Стандартные элементы управления LDAP (standard LDAP controls)

В LDAP v3 элемент управления (Control) — это сообщение, которое расширяет существующую операцию
LDAP, связывая её с дополнительной информацией, полезной серверу или клиенту. Элемент управления
может быть либо запросным (request control), либо ответным (response control). Запросный элемент
управления отправляется клиентом серверу вместе с LDAP-запросом. Ответный элемент управления
отправляется сервером клиенту вместе с LDAP-ответом. И тот, и другой представлены интерфейсом
[`javax.naming.ldap.Control`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Control.html).

Если вы раньше не программировали с использованием элементов управления, см. урок об элементах
управления (controls) в [руководстве по JNDI (JNDI Tutorial)](https://docs.oracle.com/javase/jndi/tutorial/ldap/ext/).

В этом разделе мы обсудим стандартные элементы управления LDAP, добавленные в JDK 5.0. Необходимые
элементы управления LDAP уже поддерживались в пакете-расширении LDAP Booster Pack, доступном для
поставщика службы JNDI/LDAP в пакете `com.sun.jndi.ldap.ctl`. Элементы управления LDAP,
стандартизированные IETF, теперь доступны в пакете `javax.naming.ldap` JDK через следующие классы:

- [`ManageReferralControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/ManageReferralControl.html) ([RFC 3296](http://www.ietf.org/rfc/rfc3296.txt))
- [`PagedResultsControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/PagedResultsControl.html) ([RFC 2696](http://www.ietf.org/rfc/rfc2696.txt))
- [`PagedResultsResponseControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/PagedResultsResponseControl.html)
- [`SortControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/SortControl.html) ([RFC 2891](http://www.ietf.org/rfc/rfc2891.txt))
- [`SortKey`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/SortKey.html)
- [`SortResponseControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/SortResponseControl.html)
- [`BasicControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/BasicControl.html)

### BasicControl

Класс [`javax.naming.ldap.BasicControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/BasicControl.html),
который реализует интерфейс `javax.naming.ldap.Control`, служит базовой реализацией для расширения
других элементов управления.

### Элемент управления постраничными результатами (Paged Results Control)

Элемент управления постраничными результатами (paged results control) полезен для LDAP-клиентов,
которые хотят получать результаты поиска управляемым образом, ограниченным размером страницы. Размер
страницы может быть настроен клиентом в соответствии с доступностью его ресурсов, таких как полоса
пропускания (bandwidth) и вычислительная мощность.

Сервер использует cookie (по аналогии с механизмом cookie HTTP-сессии) для поддержания состояния
запросов поиска, чтобы отслеживать результаты, отправляемые клиенту. Элемент управления
постраничными результатами специфицирован в [RFC 2696](http://www.ietf.org/rfc/rfc2696.txt).
Приведённые ниже классы предоставляют функциональность, необходимую для поддержки элемента
управления постраничными результатами:

- [`javax.naming.ldap.PagedResultsControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/PagedResultsControl.html)
- [`javax.naming.ldap.PagedResultsResponseControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/PagedResultsResponseControl.html)

#### Как использовать элемент управления постраничными результатами?

Приведённый ниже пример иллюстрирует взаимодействие клиента и сервера в случае, когда клиент
выполняет поиск, запрашивая ограничение размера страницы в 5 записей. Весь набор результатов,
возвращаемый сервером, содержит 21 запись.

1. Клиент отправляет запрос поиска, запрашивая постраничные результаты с размером страницы 5.

   ```java
   // Активировать постраничные результаты
   int pageSize = 5; // 5 записей на страницу
   byte[] cookie = null;
   int total;
   ctx.setRequestControls(new Control[]{
       new PagedResultsControl(pageSize, Control.CRITICAL) });
   // Выполнить поиск
   NamingEnumeration results = ctx.search("", "(objectclass=*)",
                                          new SearchControls());
   ```

2. Сервер отвечает записями вместе с указанием на то, что в результате поиска всего 21 запись, и
   непрозрачным (opaque) cookie, который будет использоваться клиентом при получении последующих
   страниц.

   ```java
   // Перебор пакета результатов поиска, отправленного сервером
   while (results != null && results.hasMore()) {
       // Отобразить запись
       SearchResult entry = (SearchResult)results.next();
       System.out.println(entry.getName());

       // Обработать ответные элементы управления записи (если есть)
       if (entry instanceof HasControls) {
           // ((HasControls)entry).getControls();
       }
   }
   // Изучить ответ элемента управления постраничными результатами
   Control[] controls = ctx.getResponseControls();
   if (controls != null) {
       for (int i = 0; i < controls.length; i++) {
           if (controls[i] instanceof PagedResultsResponseControl) {
               PagedResultsResponseControl prrc =
                   (PagedResultsResponseControl)controls[i];
               total = prrc.getResultSize();
               cookie = prrc.getCookie();
           } else {
               // Обработать другие ответные элементы управления (если есть)
           }
       }
   }
   ```

3. Клиент отправляет идентичный запрос поиска, возвращая непрозрачный cookie, и запрашивает
   следующую страницу.

   ```java
   // Повторно активировать постраничные результаты
   ctx.setRequestControls(new Control[]{
       new PagedResultsControl(pageSize, cookie, Control.CRITICAL) });
   ```

4. Сервер отвечает пятью записями вместе с указанием на то, что есть ещё записи. Клиент повторяет
   поиск, выполненный на шаге 4, до тех пор, пока сервер не вернёт нулевой (null) cookie, что
   означает, что серверу больше нечего отправлять.

Полный пример JNDI можно найти [здесь](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/PagedSearch.java).

> **Примечание.** Элемент управления постраничным поиском (Paged Search Control) поддерживается
> сервером Windows Active Directory. Он не поддерживается сервером Oracle Directory Server
> версии 5.2.

### Элемент управления сортировкой (Sort Control)

Элемент управления сортировкой (sort control) используется, когда клиент хочет, чтобы сервер
отправлял отсортированные результаты поиска. Сортировка на стороне сервера полезна в ситуации,
когда клиенту нужно отсортировать результаты по некоторому критерию, но он не приспособлен
выполнять процесс сортировки самостоятельно. Элемент управления сортировкой специфицирован в
[RFC 2891](http://www.ietf.org/rfc/rfc2891.txt). Приведённые ниже классы предоставляют
функциональность, необходимую для поддержки элемента управления сортировкой:

- [`javax.naming.ldap.SortControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/SortControl.html)
- [`javax.naming.ldap.SortKey`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/SortKey.html)
- [`javax.naming.ldap.SortResponseControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/SortResponseControl.html)

`SortKey` — это упорядоченный список ключей, на основе которых сервер сортирует результат.

#### Как использовать элемент управления сортировкой?

Приведённый ниже пример иллюстрирует взаимодействие клиента и сервера в случае, когда клиент
выполняет поиск, запрашивая сортировку на стороне сервера по атрибуту «cn».

1. Клиент отправляет запрос поиска, запрашивая сортировку:

   ```java
   // Активировать сортировку
   String sortKey = "cn";
   ctx.setRequestControls(new Control[] {
       new SortControl(sortKey, Control.CRITICAL) });

   // Выполнить поиск
   NamingEnumeration results =
       ctx.search("", "(objectclass=*)", new SearchControls());
   ```

2. Сервер отвечает записями, отсортированными на основе атрибута «cn» и соответствующего ему
   правила сопоставления (matching rule).

   ```java
   // Перебор отсортированных результатов поиска
   while (results != null && results.hasMore()) {
       // Отобразить запись
       SearchResult entry = (SearchResult)results.next();
       System.out.println(entry.getName());

       // Обработать ответные элементы управления записи (если есть)
       if (entry instanceof HasControls) {
           // ((HasControls)entry).getControls();
       }
   }
   // Изучить ответ элемента управления сортировкой
   Control[] controls = ctx.getResponseControls();
   if (controls != null) {
       for (int i = 0; i < controls.length; i++) {
           if (controls[i] instanceof SortResponseControl) {
               SortResponseControl src = (SortResponseControl)controls[i];
               if (! src.isSorted()) {
                   throw src.getException();
               }
           } else {
               // Обработать другие ответные элементы управления (если есть)
           }
       }
   }
   ```

Полный пример JNDI можно найти [здесь](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/SortedResults.java).

> **Примечание.** Элемент управления сортировкой поддерживается как сервером Oracle Directory
> Server, так и сервером Windows Active Directory.

### Элемент управления обработкой ссылок-перенаправлений (Manage Referral Control)

Элемент управления Manage Referral ([RFC 3296](http://www.ietf.org/rfc/rfc3296.txt)) позволяет
работать со ссылками-перенаправлениями (referral) и другими специальными объектами как с обычными
объектами при выполнении операции LDAP. Иными словами, элемент управления Manage Referral
указывает LDAP-серверу возвращать записи-перенаправления как обычные записи вместо того, чтобы
возвращать ответы об ошибке «referral» или продолжающие ссылки (continuation references). Новый
класс в JDK 5.0 (см. ниже) позволяет отправлять элемент управления Manage Referral вместе с
LDAP-запросом:

[`javax.naming.ldap.ManageReferralControl`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/ManageReferralControl.html)

Поставщик службы LDAP в JDK будет отправлять этот элемент управления автоматически вместе с любым
запросом. Вы также можете явно включить его, установив свойство окружения `Context.REFERRAL`
в значение «ignore». Дополнительную информацию об обработке ссылок-перенаправлений см. в разделе
[Referrals in the JNDI](https://docs.oracle.com/javase/jndi/tutorial/ldap/referral/jndi.html)
руководства по JNDI.

Вот пример, который отправляет элемент управления Manage Referral вместе с LDAP-запросом:

```java
// Создать начальный контекст
LdapContext ctx = (LdapContext) new InitialDirContext(env);
ctx.setRequestControls(new Control[] { new ManageReferralControl() });

// Задать элементы управления для выполнения поиска по поддереву
SearchControls ctls = new SearchControls();
ctls.setSearchScope(SearchControls.SUBTREE_SCOPE);

// Выполнить поиск
NamingEnumeration answer = ctx.search("", "(objectclass=*)", ctls);

// Вывести ответ
while (answer.hasMore()) {
    System.out.println(">>>" +
        ((SearchResult)answer.next()).getName());
}

// Закрыть контекст по завершении
ctx.close();
```

Полный пример можно найти [здесь](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/ManageReferral.java).

> **Примечание 1.** Приведённый выше пример потребует от вас настроить второй сервер с помощью
> конфигурационного файла [`refserver.ldif`](https://docs.oracle.com/javase/tutorial/jndi/software/config/refserver.ldif).
> Сервер должен поддерживать LDAP v3 и RFC 3296. Если сервер не поддерживает ссылки-перенаправления
> подобным образом, то пример не будет работать так, как показано. Конфигурационный файл содержит
> ссылки-перенаправления, которые указывают на исходный сервер, настроенный вами ранее.
> Предполагается, что исходный сервер работает на порту 389 на локальной машине. Если вы настроили
> сервер на другой машине или порту, то нужно отредактировать записи «ref» в файле refserver.ldif и
> заменить «localhost:389» соответствующим значением. Второй сервер должен быть настроен на порту
> 489 на локальной машине. Если вы настроите второй сервер на другой машине или порту, то нужно
> соответствующим образом скорректировать значение свойства окружения `Context.PROVIDER_URL` для
> начального контекста.
>
> Настройка сервера каталогов обычно выполняется администратором каталогов или системным
> администратором. Дополнительную информацию см. в уроке [Software Setup](https://docs.oracle.com/javase/tutorial/jndi/software/index.html).
>
> **Примечание 2.** Windows Active Directory: поскольку Active Directory не поддерживает элемент
> управления Manage Referral, ни один из примеров этого раздела не будет работать против Active
> Directory.

## Манипулирование LdapName (различающимся именем)

Различающееся имя (Distinguished Name, DN) используется LDAP в его строковом представлении.
Строковый формат, используемый для представления DN, специфицирован в
[RFC 2253](http://www.ietf.org/rfc/rfc2253.txt). DN состоит из компонентов, называемых
относительными различающимися именами (Relative Distinguished Name, RDN). Ниже приведён пример DN:

```
"CN=John Smith, O=Isode Limited, C=GB"
```

Он состоит из следующих RDN:

- CN=John Smith
- O=Isode Limited
- C=GB

Приведённые ниже классы представляют DN и RDN соответственно:

- [`javax.naming.ldap.LdapName`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html)
- [`javax.naming.ldap.Rdn`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html)

Класс `LdapName` реализует интерфейс
[`javax.naming.Name`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Name.html) аналогично
классам [`javax.naming.CompoundName`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Name.html)
и [`javax.naming.CompositeName`](https://docs.oracle.com/javase/8/docs/api/javax/naming/CompositeName.html).

Классы `LdapName` и `Rdn` позволяют легко манипулировать DN и RDN. С помощью этих API легко
сконструировать RDN, объединив имена и значения в пары. DN можно сконструировать из списка RDN.
Аналогично можно извлечь отдельные компоненты DN и RDN из их строкового представления.

### LdapName

`LdapName` можно создать из его строкового представления, как определено в
[RFC 2253](http://www.ietf.org/rfc/rfc2253.txt), или из списка `Rdn`. Когда используется первый
способ, заданная строка разбирается согласно правилам, определённым в RFC 2253. Если строка не
является допустимым DN, выбрасывается исключение
[`InvalidNameException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/InvalidNameException.html).
Вот пример, который использует конструктор для разбора LDAP-имени и печати его компонентов:

```java
String name = "cn=Mango,ou=Fruits,o=Food";
try {
    LdapName dn = new LdapName(name);
    System.out.println(dn + " has " + dn.size() + " RDNs: ");
    for (int i = 0; i < dn.size(); i++) {
        System.out.println(dn.get(i));
    }
} catch (InvalidNameException e) {
    System.out.println("Cannot parse name: " + name);
}
```

Запуск этого примера со входными данными «cn=Mango,ou=Fruits,o=Food» даёт следующий результат:

```
cn=Mango,ou=Fruits,o=Food has 3 RDNs:
o=Food
ou=Fruits
cn=Mango
```

Класс `LdapName` содержит методы для доступа к его компонентам как к RDN и строкам, для изменения
`LdapName`, для сравнения двух `LdapName` на равенство и для получения строкового представления
имени.

#### Доступ к компонентам имени LDAP

Вот методы, которые можно использовать для доступа к компонентам имени как к RDN и строкам:

- [`getRdn(int posn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getRdn-int-)
- [`get(int posn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#get-int-)
- [`getRdns()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getRdns--)
- [`getAll()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getAll--)
- [`getPrefix(int posn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getPrefix-intposn-)
- [`getSuffix(int posn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getSuffix-intposn-)
- [`clone()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#clone--)

Чтобы получить компонент в определённой позиции внутри `LdapName`, используйте `getRdn()` или
`get()`. Предыдущий пример с конструктором показывает пример его использования.
[`getRdns()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getRdns--)
возвращает список всех RDN, а
[`getAll()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getAll--)
возвращает все компоненты `LdapName` в виде перечисления (enumeration).

Самый правый RDN находится по индексу 0, а самый левый RDN — по индексу n-1. Например,
различающееся имя «cn=Mango, ou=Fruits, o=Food» нумеруется в следующей последовательности от 0 до 2:
{o=Food, ou=Fruits, cn=Mango}.

Вы также можете получить суффикс или префикс `LdapName` в виде экземпляра `LdapName`. Вот
[пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/LdapNameSuffixPrefix.java),
который получает суффикс и префикс LDAP-имени:

```java
LdapName dn = new LdapName("cn=Mango, ou=Fruits, o=Food");
Name suffix = dn.getSuffix(1);  // 1 <= index < cn.size()
Name prefix = dn.getPrefix(1);  // 0 <= index < 1
```

Когда вы запускаете эту программу, она генерирует следующий вывод:

```
cn=Mango ou=Fruits
o=Food
```

Чтобы сделать копию `LdapName`, используйте `clone()`.

#### Изменение имени LDAP

Ниже приведены методы, которые можно использовать для изменения имени LDAP:

- [`add(Rdn rdn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#add-Rdn-)
- [`add(String comp)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#add-String-)
- [`add(int posn, String comp)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#add-int-String-)
- [`addAll(List suffixRdns)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#addAll-List-)
- [`addAll(Name suffix)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#addAll-Namesuffix-)
- [`addAll(int posn, List suffixRdns)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#addAll-int-List-)
- [`addAll(int posn, Name suffix)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#addAll-int-Name-)
- [`remove(int posn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#remove-int-)

После создания экземпляра `LdapName` вы можете добавлять и удалять из него компоненты. Вот
[пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/ModifyLdapName.java),
который присоединяет один `LdapName` к существующему `LdapName`, добавляет компоненты в начало и в
конец и удаляет второй компонент:

```java
LdapName dn = new LdapName("ou=Fruits,o=Food");
LdapName dn2 = new LdapName("ou=Summer");
System.out.println(dn.addAll(dn2)); // ou=Summer,ou=Fruits,o=Food
System.out.println(dn.add(0, "o=Resources"));
// ou=Summer,ou=Fruits,o=Food,o=Resources
System.out.println(dn.add("cn=WaterMelon"));
// cn=WaterMelon,ou=Summer,ou=Fruits,o=Food,o=Resources
System.out.println(dn.remove(1));  // o=Food
System.out.println(dn);
// cn=WaterMelon,ou=Summer,ou=Fruits,o=Resources
```

#### Сравнение имени LDAP

Ниже приведены методы, которые можно использовать для сравнения двух имён LDAP:

- [`compareTo(Object name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#compareTo-Object-)
- [`equals(Object name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#equals-Object-)
- [`endsWith(List)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#endsWith-List-)
- [`endsWith(Name name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#endsWith-Name-)
- [`startsWith(List rdns)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#startsWith-iList-)
- [`startsWith(Name name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#startsWith-Name-)
- [`isEmpty()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#isEmpty--)

Вы можете использовать `compareTo()` для сортировки списка экземпляров `LdapName`. Метод `equals()`
позволяет определить, являются ли два `LdapName` синтаксически равными. Два `LdapName` равны, если
оба имеют одинаковые компоненты (сопоставленные с учётом регистра, case-exact) в одинаковом порядке.

С помощью `startsWith()` и `endsWith()` можно узнать, начинается или заканчивается ли `LdapName`
другим `LdapName`; то есть, является ли один `LdapName` суффиксом или префиксом другого `LdapName`.

Удобный метод `isEmpty()` позволяет определить, имеет ли `LdapName` нуль компонентов. Для той же
проверки можно также использовать выражение `size() == 0`.

Вот пример,
[`CompareLdapNames`](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/CompareLdapNames.java),
который использует некоторые из этих методов сравнения:

```java
LdapName one = new LdapName("cn=Vincent Ryan, ou=People, o=JNDITutorial");
LdapName two = new LdapName("cn=Vincent Ryan");
LdapName three = new LdapName("o=JNDITutorial");
LdapName four = new LdapName("");

System.out.println(one.equals(two));        // false
System.out.println(one.startsWith(three));  // true
System.out.println(one.endsWith(two));      // true
System.out.println(one.startsWith(four));   // true
System.out.println(one.endsWith(four));     // true
System.out.println(one.endsWith(three));    // false
System.out.println(one.isEmpty());          // false
System.out.println(four.isEmpty());         // true
System.out.println(four.size() == 0);       // true
```

#### Получение строкового представления

Приведённый ниже метод возвращает строковое представление имени LDAP, отформатированное согласно
синтаксису, заданному в RFC 2253:

- [`toString()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#toString--)

Когда вы используете конструктор `LdapName`, вы передаёте строковое представление имени LDAP и
получаете обратно экземпляр `LdapName`. Чтобы сделать обратное, то есть получить строковое
представление экземпляра `LdapName`, используйте `toString()`. Результат `toString()` можно подать
обратно в конструктор, чтобы получить экземпляр `LdapName`, равный исходному экземпляру `LdapName`.
Вот пример,
[`LdapNametoString`](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/LdapNametoString.java):

```java
LdapName dn = new LdapName(name);
String str = dn.toString();
System.out.println(str);
LdapName dn2 = new LdapName(str);
System.out.println(dn.equals(dn2));  // true
```

#### LdapName как аргумент методов Context

Методы `Context` требуют, чтобы в качестве аргумента им передавалось составное (composite) или
сложное (compound) имя. Следовательно, `LdapName` можно напрямую передать в метод контекста, как
показано в
[`LookupLdapName`](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/LookupLdapName.java):

```java
// Создать начальный контекст
Context ctx = new InitialContext(env);

// Имя LDAP
LdapName dn = new LdapName("ou=People,o=JNDITutorial");

// Выполнить поиск (lookup) с помощью dn
Object obj = ctx.lookup(dn);
```

Аналогично, когда методы `Context` возвращают результаты операций `list()`, `listBindings()` или
`search()`, DN можно получить, вызвав
[`getNameInNamespace()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/LdapName.html#getNameInNamepspace--).
`LdapName` можно сконструировать непосредственно из DN, как показано в примере
[`RetrievingLdapName`](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/RetrievingLdapName.java):

```java
while (answer.hasMore()) {
    SearchResult sr = (SearchResult) answer.next();
    String name = sr.getNameInNamespace();
    System.out.println(name);
    LdapName dn = new LdapName(name);

    // сделать что-нибудь с dn
}
```

### Манипулирование относительным различающимся именем (RDN)

Класс [`javax.naming.ldap.Rdn`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html)
представляет относительное различающееся имя (Relative Distinguished Name, RDN), как специфицировано
в [RFC 2253](http://www.ietf.org/rfc/rfc2253.txt). RDN представляет компонент DN, как объяснено в
разделе [Манипулирование LdapName](#манипулирование-ldapname-различающимся-именем). RDN состоит из
пары (или пар) тип—значение (type and value pair). Примеры RDN:

- OU=Sun
- OU=Sales+CN=J.Smith.
  Приведённый выше пример показывает представление многозначного (multi-valued) RDN.

Класс [`Rdn`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html) предоставляет
методы для доступа к паре (парам) имя/значение RDN, получения его строкового представления,
получения представления в виде
[`Attributes`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/Attributes.html),
сравнения и определения равенства RDN, а также методы для экранирования (escape) и
деэкранирования (unescape) части RDN, содержащей значение.

Класс `Rdn` неизменяемый (immutable).

#### Конструирование Rdn

`Rdn` можно сконструировать с заданной парой имя—значение, если это RDN с единственной парой
имя/значение. Для многозначного RDN следует создать набор атрибутов, состоящий из всех пар
имя/значение, и использовать конструктор, принимающий `Attributes` в качестве аргумента. Вы также
можете создать `Rdn` из его строкового представления, заданного в
[RFC 2253](http://www.ietf.org/rfc/rfc2253.txt). Наконец, вы можете клонировать `Rdn`, используя
его копирующий конструктор. Вот
[пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/RdnConstructors.java),
который создаёт RDN, используя разные типы конструкторов:

```java
Rdn rdn1 = new Rdn("ou= Juicy\\, Fruit");
System.out.println("rdn1:" + rdn1.toString());

Rdn rdn2 = new Rdn(rdn1);
System.out.println("rdn2:" + rdn2.toString());

Attributes attrs = new BasicAttributes();
attrs.put("ou", "Juicy, Fruit");
attrs.put("cn", "Mango");
Rdn rdn3 = new Rdn(attrs);
System.out.println("rdn3:" + rdn3.toString());

Rdn rdn4 = new Rdn("ou", "Juicy, Fruit");
System.out.println("rdn4:" + rdn4.toString());
```

#### Доступ к парам тип/значение RDN

Типы/значения RDN можно получить с помощью приведённых ниже методов:

- [`getType()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#getType--)
- [`getValue()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#getValue--)
- [`toAttributes()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#toAttributes--)

Для RDN, состоящего из единственной пары тип/значение, метод
[`getType()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#getType--)
возвращает тип, а метод
[`getValue()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#getValue--)
возвращает значение RDN. Метод
[`toAttributes()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#toAttributes--)
возвращает представление пар тип/значение в виде атрибутов.
[Пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/RdnGetters.java) ниже
печатает пары тип/значение RDN:

```java
Attributes attrs = new BasicAttributes();
attrs.put("o", "Yellow");
attrs.put("cn", "Mango");

// создать двоичное значение для RDN
byte[] mangoJuice = new byte[6];
for (int i = 0; i < mangoJuice.length; i++) {
    mangoJuice[i] = (byte) i;
}
attrs.put("ou", mangoJuice);
Rdn rdn = new Rdn(attrs);

System.out.println();
System.out.println("size:" + rdn.size());
System.out.println("getType(): " + rdn.getType());
System.out.println("getValue(): " + rdn.getValue());

// проверить toAttributes
System.out.println();
System.out.println("toAttributes(): " + rdn.toAttributes());
```

#### Получение строкового представления RDN

Чтобы получить строковое представление RDN, отформатированное согласно синтаксису, заданному в
[RFC 2253](http://www.ietf.org/rfc/rfc2253.txt), можно использовать:

- [`toString()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#toString--)

Когда вы используете конструктор `Rdn`, принимающий аргумент типа `String`, вы передаёте строковое
представление RDN и получаете обратно экземпляр `Rdn`. Чтобы сделать обратное, то есть получить
строковое представление экземпляра `Rdn`, используйте `toString()`. Результат `toString()` можно
подать обратно в конструктор `Rdn`, чтобы получить экземпляр `Rdn`, равный исходному экземпляру
`Rdn`.

Вот [пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/RdntoString.java):

```java
Rdn rdn = new Rdn("cn=Juicy\\,Fruit");
String str = rdn.toString();
System.out.println(str);
Rdn rdn2 = new Rdn(str);
System.out.println(rdn.equals(rdn2));    // true
```

#### Сравнение RDN

Приведённые ниже методы позволяют сравнивать RDN:

- [`equals(Object Rdn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#equals-Object-)
- [`compareTo(Object Rdn)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#compareTo-Object-)

Вы можете использовать `compareTo()` для сортировки списка экземпляров `Rdn`. `equals()` позволяет
определить, являются ли два `Rdn` синтаксически равными. Два `Rdn` равны, если оба имеют одинаковые
пары тип/значение (сопоставленные с учётом регистра, case-exact). Порядок компонентов в многозначном
RDN не имеет значения.

Вот [пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/CompareRdns.java):

```java
Rdn one = new Rdn("ou=Sales+cn=Bob");
Rdn two = new Rdn("cn=Bob+ou=Sales");
Rdn three = new Rdn("ou=Sales+cn=Bob+c=US");
Rdn four = new Rdn("cn=lowercase");
Rdn five = new Rdn("cn=LowerCASE");
System.out.println(one.equals(two));    // true
System.out.println(two.equals(three));  // false
System.out.println(one.equals(three));  // false
System.out.println(four.equals(five));  // true
```

#### Экранирование и деэкранирование специальных символов

Одно из лучших применений класса `Rdn` — когда приходится иметь дело с DN, содержащими специальные
символы. Он автоматически заботится об экранировании и деэкранировании специальных символов. Такие
символы, как `\` (обратная косая черта, backslash), `,` (запятая, comma), `+` (плюс, plus) и т.д.,
имеют специфическую семантику согласно [RFC 2253](http://www.ietf.org/rfc/rfc2253.txt). Список всех
специальных символов можно найти в RFC 2253. Когда эти символы используются как литералы в DN, они
должны быть экранированы с помощью `\` (обратной косой черты).

Например, рассмотрим RDN: `cn=Juicy, Fruit`. Символ `,` (запятая), стоящий между Juicy и Fruit, —
это специальный символ, который должен быть экранирован с помощью `\` (обратной косой черты).
Получившийся синтаксически отформатированный RDN выглядит так: `cn=Juicy\, Fruit`. Однако сам
символ `\` (обратная косая черта) является специальным символом согласно синтаксису строк языка
Java, и его нужно снова экранировать с помощью `\` (обратной косой черты). И формат строк языка
Java, и [RFC 2253](http://www.ietf.org/rfc/rfc2253.txt) используют `\` (обратную косую черту) для
экранирования специальных символов. И поэтому RDN, отформатированный в формате языка Java, выглядит
так: `cn=Juicy\\, Fruit`. Обратите внимание, что упомянутые выше правила форматирования применяются
только к компоненту значения RDN. Класс `Rdn` предоставляет два статических метода для обработки
автоматического экранирования и деэкранирования значений RDN:

- [`escapeValue()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#escapeValue--)
- [`unescapeValue()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/ldap/Rdn.html#unescapeValue--)

[Пример](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/EscapingDNs.java) ниже
показывает, как получить строковое представление DN, не имея дела с синтаксисом обработки
специальных символов, определённым в [RFC 2253](http://www.ietf.org/rfc/rfc2253.txt):

```java
// DN с ',' (запятой)
String unformatted = "Juicy, Fruit";
String formatted = Rdn.escapeValue(unformatted);
LdapName dn = new LdapName("cn=" + formatted);
System.out.println("dn:" + dn);


unformatted = "true+false";
formatted = Rdn.escapeValue(unformatted);
dn = new LdapName("cn=" + formatted);
System.out.println("dn:" + dn);

// DN с двоичным значением в качестве одного из значений его атрибутов
byte[] bytes = new byte[] {1, 2, 3, 4};
formatted = Rdn.escapeValue(bytes);
System.out.println("Orig val: " + bytes + "Escaped val: " + formatted);
```

Аналогично, используя статический метод `unescapeValue()`, можно получить исходную строку из
отформатированного значения.
[Вот](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/UnescapingValues.java) пример
извлечения исходного значения:

```java
// DN с ',' (запятой)
String unformatted = "Juicy, Fruit";
String formatted = Rdn.escapeValue(unformatted);
System.out.println("Formatted:" + formatted);
Object original = Rdn.unescapeValue(formatted);
System.out.println("Original:" +  original);

// DN с '+' (плюсом)
unformatted = "true+false";
formatted = Rdn.escapeValue(unformatted);
System.out.println("Formatted:" + formatted);
original = Rdn.unescapeValue(formatted);
System.out.println("Original:" +  original);

// DN с двоичным значением в качестве одного из значений его атрибутов
byte[] bytes = new byte[] {1, 2, 3, 4};
formatted = Rdn.escapeValue(bytes);
System.out.println("Formatted:" + formatted);
original = Rdn.unescapeValue(formatted);
System.out.println("Original:" +  original);
```

## Установка тайм-аута для операций LDAP

Когда клиент посылает серверу LDAP-запрос, а сервер по какой-либо причине не отвечает, клиент ждёт
ответа сервера бесконечно, пока не сработает тайм-аут TCP. На стороне клиента то, что испытывает
пользователь, по сути является зависанием процесса. Чтобы управлять LDAP-запросом своевременным
образом, начиная с Java SE 6 для поставщика службы JNDI/LDAP можно настроить тайм-аут чтения
(read timeout).

Новое свойство окружения:

```
com.sun.jndi.ldap.read.timeout
```

можно использовать для задания тайм-аута чтения для операции LDAP. Значением этого свойства является
строковое представление целого числа, представляющего тайм-аут чтения в миллисекундах для операций
LDAP. Если поставщик LDAP не получает LDAP-ответ в течение заданного периода, он прерывает попытку
чтения. Целое число должно быть больше нуля. Целое число, меньшее или равное нулю, означает, что
тайм-аут чтения не задан, что эквивалентно бесконечному ожиданию ответа до его получения и
соответствует исходному поведению.

Если это свойство не задано, по умолчанию ожидание ответа продолжается до его получения.
Например, `env.put("com.sun.jndi.ldap.read.timeout", "5000");` заставляет поставщика службы LDAP
прервать попытку чтения, если сервер не отвечает в течение 5 секунд.

Вот пример,
[`ReadTimeoutTest`](https://docs.oracle.com/javase/tutorial/jndi/newstuff/examples/ReadTimeoutTest.java),
который использует фиктивный (dummy) сервер, не отвечающий на LDAP-запросы, чтобы показать, как ведёт
себя это свойство, когда оно установлено в ненулевое значение:

```java
env.put(Context.INITIAL_CONTEXT_FACTORY,
        "com.sun.jndi.ldap.LdapCtxFactory");
env.put("com.sun.jndi.ldap.read.timeout", "1000");
env.put(Context.PROVIDER_URL, "ldap://localhost:2001");

Server s = new Server();

try {

    // запустить сервер
    s.start();

   // Создать начальный контекст
   DirContext ctx = new InitialDirContext(env);
   System.out.println("LDAP Client: Connected to the Server");
        :
        :
} catch (NamingException e) {
   e.printStackTrace();
}
```

Приведённая выше программа печатает приведённую ниже трассировку стека (stack trace), поскольку
сервер не отвечает даже на LDAP-запрос привязки (bind request) при создании `InitialDirContext`.
Клиент завершается по тайм-ауту, ожидая ответа сервера:

```
Server: Connection accepted
javax.naming.NamingException: LDAP response read timed out, timeout used:1000ms.
:
:

at javax.naming.directory.InitialDirContext.<init>(InitialDirContext.java:82)
at ReadTimeoutTest.main(ReadTimeoutTest.java:32)
```

Обратите внимание, что это свойство отличается от другого свойства окружения
`com.sun.jndi.ldap.connect.timeout`, которое задаёт тайм-аут на подключение к серверу. Тайм-аут
чтения применяется к LDAP-ответу от сервера после того, как с сервером установлено первоначальное
соединение.

## Источник

- [New features in JDK 5.0 and JDK 6 (индекс урока)](https://docs.oracle.com/javase/tutorial/jndi/newstuff/index.html) — официальное руководство Oracle.
- [Retrieving Distinguished Name](https://docs.oracle.com/javase/tutorial/jndi/newstuff/dn.html) — официальное руководство Oracle.
- [Standard LDAP Controls](https://docs.oracle.com/javase/tutorial/jndi/newstuff/controls-std.html) — официальное руководство Oracle.
- [Paged Results Control](https://docs.oracle.com/javase/tutorial/jndi/newstuff/paged-results.html) — официальное руководство Oracle.
- [Sort Control](https://docs.oracle.com/javase/tutorial/jndi/newstuff/sort.html) — официальное руководство Oracle.
- [Manage Referral Control](https://docs.oracle.com/javase/tutorial/jndi/newstuff/mdsaIT.html) — официальное руководство Oracle.
- [Manipulating LdapName (Distinguished Name)](https://docs.oracle.com/javase/tutorial/jndi/newstuff/ldapname.html) — официальное руководство Oracle.
- [Manipulating Relative Distinguished Name (RDN)](https://docs.oracle.com/javase/tutorial/jndi/newstuff/rdn.html) — официальное руководство Oracle.
- [Setting Timeout for Ldap Operations](https://docs.oracle.com/javase/tutorial/jndi/newstuff/readtimeout.html) — официальное руководство Oracle.
</content>
</invoke>
