# Урок 4. Операции именования и каталога

**Трейл:** JNDI · **Оригинал:** [Naming and Directory Operations](https://docs.oracle.com/javase/tutorial/jndi/ops/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок собран из
> страниц трейла *Java Naming and Directory Interface → Lesson: Naming and Directory
> Operations*: вводная и настройка, поиск объекта, перечисление контекста, добавление/замена/
> удаление привязки, переименование, создание и уничтожение подконтекстов, имена атрибутов,
> чтение и изменение атрибутов, привязки с атрибутами и поиск (Search) со всеми элементами
> управления (фильтры, область видимости, ограничение количества и времени), а также советы
> по диагностике.

С помощью JNDI можно выполнять операции именования (*naming operations*), включая операции
чтения и операции обновления пространства имён (*namespace*). В этом уроке описываются следующие
операции:

- поиск объекта (*looking up an object*);
- перечисление содержимого контекста (*listing the contents of a context*);
- добавление, перезапись и удаление привязки (*adding, overwriting, and removing a binding*);
- переименование объекта (*renaming an object*);
- создание и уничтожение подконтекстов (*creating and destroying subcontexts*).

## Настройка (Configuration)

Прежде чем выполнять какую-либо операцию над службой именования или каталога, необходимо получить
**начальный контекст** (*initial context*) — отправную точку в пространстве имён. Это нужно потому,
что все методы служб именования и каталогов выполняются относительно некоторого контекста. Чтобы
получить начальный контекст, выполните следующие шаги.

1. Выберите поставщика службы (*service provider*) той службы, к которой вы хотите обратиться.
2. Задайте конфигурацию, необходимую начальному контексту.
3. Вызовите конструктор `InitialContext`.

### Шаг 1. Выбор поставщика службы для начального контекста

Поставщика службы для начального контекста можно указать, создав набор **свойств окружения**
(*environment properties* — объект `Hashtable`) и добавив в него имя класса поставщика службы.
Свойства окружения подробно описаны в руководстве JNDI Tutorial.

Если вы используете поставщика службы LDAP, входящего в состав JDK, то код будет выглядеть так:

```java
Hashtable<String, Object> env = new Hashtable<String, Object>();
env.put(Context.INITIAL_CONTEXT_FACTORY,
        "com.sun.jndi.ldap.LdapCtxFactory");
```

Чтобы указать поставщика службы файловой системы из JDK, код будет выглядеть так:

```java
Hashtable<String, Object> env = new Hashtable<String, Object>();
env.put(Context.INITIAL_CONTEXT_FACTORY,
        "com.sun.jndi.fscontext.RefFSContextFactory");
```

Также для указания используемого поставщика службы можно применять **системные свойства**
(*system properties*). Подробности — в руководстве JNDI Tutorial.

### Шаг 2. Предоставление информации, необходимой начальному контексту

Клиентам разных каталогов может потребоваться различная информация для связи с каталогом. Например,
может понадобиться указать, на какой машине запущен сервер и какая информация нужна для
идентификации пользователя в каталоге. Такая информация передаётся поставщику службы через свойства
окружения. JNDI задаёт несколько обобщённых свойств окружения, которые поставщики служб могут
использовать. Подробности о том, какая информация требуется для этих свойств, приведены в
документации вашего поставщика службы.

Поставщик LDAP требует, чтобы программа указала расположение LDAP-сервера, а также информацию об
идентификации пользователя. Для этого код будет выглядеть следующим образом:

```java
env.put(Context.PROVIDER_URL, "ldap://ldap.wiz.com:389");
env.put(Context.SECURITY_PRINCIPAL, "joeuser");
env.put(Context.SECURITY_CREDENTIALS, "joepassword");
```

В этом руководстве используется поставщик службы LDAP из JDK. В примерах предполагается, что на
локальной машине настроен сервер на порту 389 с корневым отличительным именем (*root-distinguished
name*) `o=JNDITutorial` и что для обновления каталога аутентификация не требуется. В примеры
включён следующий код настройки окружения:

```java
env.put(Context.PROVIDER_URL, "ldap://localhost:389/o=JNDITutorial");
```

Если вы используете каталог, настроенный иначе, то эти свойства окружения нужно задать
соответствующим образом. Потребуется заменить `localhost` на имя той машины. Эти примеры можно
запускать против любых публичных серверов каталогов или вашего собственного сервера на другой
машине. Нужно будет заменить `localhost` на имя той машины и заменить `o=JNDITutorial` на доступный
контекст именования.

### Шаг 3. Создание начального контекста

Теперь всё готово к созданию начального контекста. Для этого в конструктор `InitialContext`
передаются ранее созданные свойства окружения:

```java
Context ctx = new InitialContext(env);
```

Получив ссылку на объект `Context`, можно начинать работу со службой именования.

Чтобы выполнять операции каталога, нужно использовать `InitialDirContext`. Для этого применяется
один из его конструкторов:

```java
DirContext ctx = new InitialDirContext(env);
```

Этот оператор возвращает ссылку на объект `DirContext` для выполнения операций каталога.

## Поиск объекта (Lookup an Object)

Чтобы найти объект в службе именования, используйте метод
[`Context.lookup()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#lookup-javax.naming.Name-)
и передайте ему имя объекта, который требуется получить. Предположим, что в службе именования есть
объект с именем `cn=Rosanna Lee,ou=People`. Чтобы получить этот объект, нужно написать:

```java
Object obj = ctx.lookup("cn=Rosanna Lee,ou=People");
```

Тип объекта, возвращаемого методом `lookup()`, зависит как от используемой системы именования, так и
от данных, связанных с самим объектом. Система именования может содержать объекты разных типов, и
поиск объекта в разных частях системы может давать объекты разных типов. В этом примере имя
`cn=Rosanna Lee,ou=People` оказывается привязанным к объекту-контексту (`javax.naming.ldap.LdapContext`).
Результат `lookup()` можно привести к целевому классу.

Например, следующий код ищет объект `cn=Rosanna Lee,ou=People` и приводит его к `LdapContext`:

```java
import javax.naming.ldap.LdapContext;
...
LdapContext ctx = (LdapContext) ctx.lookup("cn=Rosanna Lee,ou=People");
```

Полный пример находится в файле `Lookup.java`.

В Java SE 6 появились два новых статических метода для поиска имени:

- [`InitialContext.doLookup(Name name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/InitialContext.html#doLookup-javax.naming.Name-)
- [`InitialContext.doLookup(String name)`](https://docs.oracle.com/javase/8/docs/api/javax/naming/InitialContext.html#doLookup-java.lang.String-)

Эти методы предоставляют сокращённый способ поиска имени без создания экземпляра `InitialContext`.

## Перечисление контекста (List the Context)

Вместо того чтобы получать по одному объекту за раз (как с помощью `Context.lookup()`), можно
перечислить весь контекст одной операцией. Для перечисления контекста существует два метода: один
возвращает привязки (*bindings*), а другой — только пары «имя — имя класса объекта».

### Метод Context.list()

Метод
[`Context.list()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#list-javax.naming.Name-)
возвращает перечисление объектов
[`NameClassPair`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NameClassPair.html). Каждый
`NameClassPair` состоит из имени объекта и имени его класса. Следующий фрагмент кода перечисляет
содержимое каталога `ou=People` (то есть файлы и каталоги, найденные в каталоге `ou=People`):

```java
NamingEnumeration list = ctx.list("ou=People");

while (list.hasMore()) {
    NameClassPair nc = (NameClassPair)list.next();
    System.out.println(nc);
}
```

Запуск этого примера даёт следующий вывод:

```
# java List
cn=Jon Ruiz: javax.naming.directory.DirContext
cn=Scott Seligman: javax.naming.directory.DirContext
cn=Samuel Clemens: javax.naming.directory.DirContext
cn=Rosanna Lee: javax.naming.directory.DirContext
cn=Maxine Erlund: javax.naming.directory.DirContext
cn=Niels Bohr: javax.naming.directory.DirContext
cn=Uri Geller: javax.naming.directory.DirContext
cn=Colleen Sullivan: javax.naming.directory.DirContext
cn=Vinnie Ryan: javax.naming.directory.DirContext
cn=Rod Serling: javax.naming.directory.DirContext
cn=Jonathan Wood: javax.naming.directory.DirContext
cn=Aravindan Ranganathan: javax.naming.directory.DirContext
cn=Ian Anderson: javax.naming.directory.DirContext
cn=Lao Tzu: javax.naming.directory.DirContext
cn=Don Knuth: javax.naming.directory.DirContext
cn=Roger Waters: javax.naming.directory.DirContext
cn=Ben Dubin: javax.naming.directory.DirContext
cn=Spuds Mackenzie: javax.naming.directory.DirContext
cn=John Fowler: javax.naming.directory.DirContext
cn=Londo Mollari: javax.naming.directory.DirContext
cn=Ted Geisel: javax.naming.directory.DirContext
```

### Метод Context.listBindings()

Метод
[`Context.listBindings()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#listBindings-javax.naming.Name-)
возвращает перечисление объектов
[`Binding`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Binding.html). `Binding` —
подкласс `NameClassPair`. Привязка содержит не только имя объекта и имя его класса, но и сам объект.
Следующий код перечисляет контекст `ou=People`, выводя имя и объект каждой привязки:

```java
NamingEnumeration bindings = ctx.listBindings("ou=People");

while (bindings.hasMore()) {
    Binding bd = (Binding)bindings.next();
    System.out.println(bd.getName() + ": " + bd.getObject());
}
```

Запуск этого примера даёт следующий вывод:

```
# java ListBindings
cn=Jon Ruiz: com.sun.jndi.ldap.LdapCtx@1d4c61c
cn=Scott Seligman: com.sun.jndi.ldap.LdapCtx@1a626f
cn=Samuel Clemens: com.sun.jndi.ldap.LdapCtx@34a1fc
cn=Rosanna Lee: com.sun.jndi.ldap.LdapCtx@176c74b
cn=Maxine Erlund: com.sun.jndi.ldap.LdapCtx@11b9fb1
cn=Niels Bohr: com.sun.jndi.ldap.LdapCtx@913fe2
cn=Uri Geller: com.sun.jndi.ldap.LdapCtx@12558d6
cn=Colleen Sullivan: com.sun.jndi.ldap.LdapCtx@eb7859
cn=Vinnie Ryan: com.sun.jndi.ldap.LdapCtx@12a54f9
cn=Rod Serling: com.sun.jndi.ldap.LdapCtx@30e280
cn=Jonathan Wood: com.sun.jndi.ldap.LdapCtx@16672d6
cn=Aravindan Ranganathan: com.sun.jndi.ldap.LdapCtx@fd54d6
cn=Ian Anderson: com.sun.jndi.ldap.LdapCtx@1415de6
cn=Lao Tzu: com.sun.jndi.ldap.LdapCtx@7bd9f2
cn=Don Knuth: com.sun.jndi.ldap.LdapCtx@121cc40
cn=Roger Waters: com.sun.jndi.ldap.LdapCtx@443226
cn=Ben Dubin: com.sun.jndi.ldap.LdapCtx@1386000
cn=Spuds Mackenzie: com.sun.jndi.ldap.LdapCtx@26d4f1
cn=John Fowler: com.sun.jndi.ldap.LdapCtx@1662dc8
cn=Londo Mollari: com.sun.jndi.ldap.LdapCtx@147c5fc
cn=Ted Geisel: com.sun.jndi.ldap.LdapCtx@3eca90
```

### Завершение NamingEnumeration

Перечисление
[`NamingEnumeration`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NamingEnumeration.html)
может быть завершено одним из трёх способов: естественно, явно или непредвиденно.

- Когда
  [`NamingEnumeration.hasMore()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NamingEnumeration.html#hasMore--)
  возвращает `false`, перечисление завершено и фактически прекращено.
- Перечисление можно завершить явно до его окончания, вызвав
  [`NamingEnumeration.close()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NamingEnumeration.html#close--).
  Это даёт подсказку нижележащей реализации освободить все ресурсы, связанные с перечислением.
- Если `hasMore()` или
  [`next()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NamingEnumeration.html#next--)
  выбрасывает
  [`NamingException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NamingException.html),
  то перечисление фактически прекращается.

Независимо от того, как перечисление было завершено, после завершения его больше нельзя использовать.
Вызов метода у завершённого перечисления даёт неопределённый результат.

### Почему два разных метода перечисления?

Метод `list()` предназначен для приложений в стиле обозревателя (*browser-style*), которым нужно
лишь отобразить имена объектов в контексте. Например, обозреватель может перечислить имена в
контексте и подождать, пока пользователь выберет одно или несколько отображённых имён для дальнейших
операций. Таким приложениям обычно не требуется доступ ко всем объектам в контексте.

Метод `listBindings()` предназначен для приложений, которым нужно выполнять операции над объектами
контекста **массово** (*en masse*). Например, приложению резервного копирования может понадобиться
выполнить операцию «получить статистику файла» над всеми объектами в файловом каталоге. Или программа
администрирования принтеров может захотеть перезапустить все принтеры в здании. Чтобы выполнять такие
операции, этим приложениям нужно получить все объекты, привязанные в контексте. Поэтому удобнее, чтобы
объекты возвращались как часть перечисления.

Приложение может использовать либо `list()`, либо потенциально более дорогой `listBindings()` — в
зависимости от того, какая информация ему нужна.

## Добавление, замена или удаление привязки (Add, Replace or Remove a Binding)

Интерфейс `Context` содержит методы для добавления, замены и удаления привязки в контексте.

### Добавление привязки

Метод
[`Context.bind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#bind-javax.naming.Name-java.lang.Object-)
используется для добавления привязки в контекст. Он принимает в качестве аргументов имя объекта и сам
привязываемый объект.

```java
// Создаём объект для привязки
Fruit fruit = new Fruit("orange");

// Выполняем привязку
ctx.bind("cn=Favorite Fruit", fruit);
```

Этот пример создаёт объект класса `Fruit` и привязывает его к имени `cn=Favorite Fruit` в контексте
`ctx`. Если впоследствии выполнить поиск имени `cn=Favorite Fruit` в `ctx`, то вы получите объект
`fruit`. Обратите внимание: для компиляции класса `Fruit` нужен класс `FruitFactory`.

Если запустить этот пример дважды, то вторая попытка завершится исключением
[`NameAlreadyBoundException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NameAlreadyBoundException.html).
Это потому, что имя `cn=Favorite Fruit` уже привязано. Чтобы вторая попытка прошла успешно, нужно
использовать
[`rebind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#rebind-javax.naming.Name-java.lang.Object-).

### Добавление или замена привязки

Метод `rebind()` используется для добавления или замены привязки. Он принимает те же аргументы, что и
`bind()`, но семантика такова: если имя уже привязано, то оно будет отвязано, и будет привязан вновь
переданный объект.

```java
// Создаём объект для привязки
Fruit fruit = new Fruit("lemon");

// Выполняем привязку
ctx.rebind("cn=Favorite Fruit", fruit);
```

При запуске этот пример заменит привязку, созданную примером с `bind()`.

### Удаление привязки

Чтобы удалить привязку, используется метод
[`unbind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#unbind-javax.naming.Name-).

```java
// Удаляем привязку
ctx.unbind("cn=Favorite Fruit");
```

При запуске этот пример удаляет привязку, созданную примером с `bind()` или `rebind()`.

## Переименование (Rename)

Объект в контексте можно переименовать с помощью метода
[`Context.rename()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#rename-javax.naming.Name-javax.naming.Name-).

```java
// Переименовываем в Scott S
ctx.rename("cn=Scott Seligman", "cn=Scott S");
```

Этот пример переименовывает объект, привязанный к `cn=Scott Seligman`, в `cn=Scott S`. Убедившись,
что объект переименован, программа переименовывает его обратно в исходное имя (`cn=Scott Seligman`)
так:

```java
// Переименовываем обратно в Scott Seligman
ctx.rename("cn=Scott S", "cn=Scott Seligman");
```

Дополнительные примеры переименования записей LDAP — в уроке *Advanced Topics for LDAP users*.

## Создание и уничтожение подконтекстов (Create and Destroy Subcontexts)

Интерфейс `Context` содержит методы для создания и уничтожения **подконтекста** (*subcontext*) —
контекста, привязанного внутри другого контекста того же типа.

Описанный здесь пример использует объект, имеющий **атрибуты** (*attributes*), и создаёт подконтекст
в каталоге. Эти методы `DirContext` можно использовать для связывания атрибутов с объектом в момент
добавления привязки или подконтекста в пространство имён. Например, можно создать объект `Person`,
привязать его к пространству имён и одновременно связать с ним атрибуты об этом объекте `Person`.
Эквивалент в именовании (без каталога) не будет иметь атрибутов.

Метод `createSubcontext()` отличается от `bind()` тем, что создаёт новый объект — то есть новый
`Context`, который будет привязан к каталогу, тогда как `bind()` привязывает к каталогу заданный
объект.

### Создание контекста

Чтобы создать контекст именования, передайте методу
[`createSubcontext()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#createSubcontext-javax.naming.Name-)
имя контекста, который нужно создать. Чтобы создать контекст с атрибутами, передайте методу
[`DirContext.createSubcontext()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#createSubcontext-javax.naming.Name-javax.naming.directory.Attributes-)
имя создаваемого контекста и его атрибуты.

```java
// Создаём атрибуты, которые будут связаны с новым контекстом
Attributes attrs = new BasicAttributes(true); // без учёта регистра
Attribute objclass = new BasicAttribute("objectclass");
objclass.add("top");
objclass.add("organizationalUnit");
attrs.put(objclass);

// Создаём контекст
Context result = ctx.createSubcontext("NewOu", attrs);
```

Этот пример создаёт новый контекст `ou=NewOu` с атрибутом `objectclass`, имеющим два значения —
`top` и `organizationalUnit`, в контексте `ctx`.

Вывод:

```
# java Create
ou=Groups: javax.naming.directory.DirContext
ou=People: javax.naming.directory.DirContext
ou=NewOu: javax.naming.directory.DirContext
```

Этот пример создаёт новый контекст `NewOu`, являющийся дочерним по отношению к `ctx`.

### Уничтожение контекста

Чтобы уничтожить контекст, передайте методу
[`destroySubcontext()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#destroySubcontext-javax.naming.Name-)
имя уничтожаемого контекста.

```java
// Уничтожаем контекст
ctx.destroySubcontext("NewOu");
```

Этот пример уничтожает контекст `NewOu` в контексте `ctx`.

## Имена атрибутов (Attribute Names)

Атрибут состоит из **идентификатора атрибута** (*attribute identifier*) и набора **значений атрибута**
(*attribute values*). Идентификатор атрибута, также называемый **именем атрибута** (*attribute name*), —
это строка, идентифицирующая атрибут. **Значение атрибута** — это содержимое атрибута, и его тип не
ограничен строкой. Имя атрибута используется, когда нужно указать конкретный атрибут — для извлечения,
поиска или изменения. Имена также возвращаются операциями, возвращающими атрибуты (например, при чтении
или поиске в каталоге).

Используя имена атрибутов, нужно учитывать некоторые особенности сервера каталогов, чтобы результат не
оказался неожиданным. Эти особенности описаны в следующих подразделах.

### Тип атрибута

В каталогах вроде LDAP имя атрибута идентифицирует **тип атрибута** и часто называется **именем типа
атрибута** (*attribute type name*). Например, имя атрибута `cn` также называется именем типа атрибута.
Определение типа атрибута задаёт синтаксис, который должно иметь значение атрибута, может ли он иметь
несколько значений, а также правила равенства и упорядочивания, используемые при сравнении и
упорядочивании значений атрибута.

### Наследование атрибутов

Некоторые реализации каталогов поддерживают **наследование атрибутов** (*attribute subclassing*), при
котором сервер позволяет определять типы атрибутов в терминах других типов атрибутов. Например, атрибут
`name` может быть суперклассом всех атрибутов, связанных с именами: `commonName` может быть подклассом
`name`. Для реализаций каталогов, поддерживающих это, запрос атрибута `name` может вернуть атрибут
`commonName`.

При обращении к каталогам, поддерживающим наследование атрибутов, нужно учитывать, что сервер может
вернуть атрибуты с именами, отличными от запрошенных. Чтобы минимизировать вероятность этого,
используйте наиболее производный подкласс (*the most derived subclass*).

### Синонимы имён атрибутов

Некоторые реализации каталогов поддерживают синонимы имён атрибутов. Например, `cn` может быть
синонимом `commonName`. Таким образом, запрос атрибута `cn` может вернуть атрибут `commonName`.

При обращении к каталогам, поддерживающим синонимы имён атрибутов, нужно учитывать, что сервер может
вернуть атрибуты с именами, отличными от запрошенных. Чтобы предотвратить это, используйте
**каноническое имя атрибута** (*canonical attribute name*) вместо одного из его синонимов. Каноническое
имя атрибута — это имя, используемое в определении атрибута; синоним — это имя, ссылающееся в своём
определении на каноническое имя атрибута.

### Языковые предпочтения

Расширение LDAP v3 ([RFC 2596](http://www.ietf.org/rfc/rfc2596.txt)) позволяет указывать код языка
вместе с именем атрибута. Это похоже на наследование атрибутов в том, что одно имя атрибута может
представлять несколько разных атрибутов. Пример — атрибут `description`, имеющий два языковых варианта:

```
description: software
description;lang-en: software products
description;lang-de: Softwareprodukte
```

Запрос атрибута `description` вернёт все три атрибута.

При обращении к каталогам, поддерживающим эту возможность, нужно учитывать, что сервер может вернуть
атрибуты с именами, отличными от запрошенных.

## Чтение атрибутов (Read Attributes)

Чтобы прочитать атрибуты объекта из каталога, используйте метод
[`DirContext.getAttributes()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#getAttributes-javax.naming.Name-)
и передайте ему имя объекта, атрибуты которого вы хотите получить. Предположим, что объект в службе
именования имеет имя `cn=Ted Geisel, ou=People`. Чтобы извлечь атрибуты этого объекта, понадобится
код вроде следующего:

```java
Attributes answer = ctx.getAttributes("cn=Ted Geisel, ou=People");
```

Затем содержимое этого ответа можно вывести так:

```java
for (NamingEnumeration ae = answer.getAll(); ae.hasMore();) {
    Attribute attr = (Attribute)ae.next();
    System.out.println("attribute: " + attr.getID());
    /* Выводим каждое значение */
    for (NamingEnumeration e = attr.getAll(); e.hasMore();
         System.out.println("value: " + e.next()))
        ;
}
```

Это даёт следующий вывод:

```
# java GetattrsAll
attribute: sn
value: Geisel
attribute: objectclass
value: top
value: person
value: organizationalPerson
value: inetOrgPerson
attribute: jpegphoto
value: [B@1dacd78b
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: facsimiletelephonenumber
value: +1 408 555 2329
attribute: telephonenumber
value: +1 408 555 5252
attribute: cn
value: Ted Geisel
```

### Возврат выбранных атрибутов

Чтобы прочитать выборочное подмножество атрибутов, передайте массив строк — идентификаторов атрибутов,
которые вы хотите получить.

```java
// Указываем идентификаторы возвращаемых атрибутов
String[] attrIDs = {"sn", "telephonenumber", "golfhandicap", "mail"};

// Получаем запрошенные атрибуты
Attributes answer = ctx.getAttributes("cn=Ted Geisel, ou=People", attrIDs);
```

Этот пример запрашивает атрибуты `sn`, `telephonenumber`, `golfhandicap` и `mail` объекта
`cn=Ted Geisel, ou=People`. У этого объекта есть все атрибуты, кроме `golfhandicap`, поэтому в ответе
возвращаются три атрибута. Ниже приведён вывод примера:

```
# java Getattrs
attribute: sn
value: Geisel
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: telephonenumber
value: +1 408 555 5252
```

## Изменение атрибутов (Modify Attributes)

Интерфейс
[`DirContext`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html)
содержит методы для изменения атрибутов и значений атрибутов объектов в каталоге.

### Использование списка изменений

Один из способов изменить атрибуты объекта — передать список запросов на изменение
([`ModificationItem`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/ModificationItem.html)).
Каждый `ModificationItem` состоит из числовой константы, указывающей тип изменения, и атрибута
([`Attribute`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/Attribute.html)),
описывающего вносимое изменение. Существует три типа изменений:

- [`ADD_ATTRIBUTE`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#ADD_ATTRIBUTE)
- [`REPLACE_ATTRIBUTE`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#REPLACE_ATTRIBUTE)
- [`REMOVE_ATTRIBUTE`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#REMOVE_ATTRIBUTE)

Изменения применяются в том порядке, в котором они идут в списке. Выполняются либо все изменения, либо
ни одного.

Следующий код создаёт список изменений. Он заменяет значение атрибута `mail` значением
`geisel@wizards.com`, добавляет дополнительное значение к атрибуту `telephonenumber` и удаляет атрибут
`jpegphoto`.

```java
// Задаём вносимые изменения
ModificationItem[] mods = new ModificationItem[3];

// Заменяем атрибут "mail" новым значением
mods[0] = new ModificationItem(DirContext.REPLACE_ATTRIBUTE,
    new BasicAttribute("mail", "geisel@wizards.com"));

// Добавляем дополнительное значение к "telephonenumber"
mods[1] = new ModificationItem(DirContext.ADD_ATTRIBUTE,
    new BasicAttribute("telephonenumber", "+1 555 555 5555"));

// Удаляем атрибут "jpegphoto"
mods[2] = new ModificationItem(DirContext.REMOVE_ATTRIBUTE,
    new BasicAttribute("jpegphoto"));
```

**Windows Active Directory.** Active Directory определяет `telephonenumber` как одноз­начный
(*single-valued*) атрибут вопреки [RFC 2256](http://www.ietf.org/rfc/rfc2256.txt). Чтобы этот пример
заработал против Active Directory, нужно либо использовать атрибут, отличный от `telephonenumber`,
либо заменить `DirContext.ADD_ATTRIBUTE` на `DirContext.REPLACE_ATTRIBUTE`.

После создания этого списка изменений его можно передать методу
[`modifyAttributes()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#modifyAttributes-javax.naming.Name-javax.naming.directory.ModificationItem:A-)
следующим образом:

```java
// Выполняем запрошенные изменения над именованным объектом
ctx.modifyAttributes(name, mods);
```

### Использование атрибутов

Альтернативно, изменения можно выполнить, указав тип изменения и атрибуты, к которым его применять.

Например, следующая строка заменяет атрибуты (указанные в `orig`), связанные с `name`, на атрибуты из
`orig`:

```java
ctx.modifyAttributes(name, DirContext.REPLACE_ATTRIBUTE, orig);
```

Все остальные атрибуты `name` остаются без изменений.

Оба этих способа использования `modifyAttributes()` продемонстрированы в примере программы
`ModAttrs.java`. Эта программа изменяет атрибуты с помощью списка изменений, а затем использует вторую
форму `modifyAttributes()` для восстановления исходных атрибутов.

## Привязки с атрибутами (Add, Replace Bindings with Attributes)

В примерах именования рассматривалось использование `bind()` и `rebind()`. Интерфейс
[`DirContext`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html)
содержит перегруженные версии этих методов, принимающие атрибуты. Эти методы `DirContext` можно
использовать для связывания атрибутов с объектом в момент добавления привязки или подконтекста в
пространство имён. Например, можно создать объект `Person`, привязать его к пространству имён и
одновременно связать с ним атрибуты об этом объекте `Person`.

### Добавление привязки с атрибутами

Метод
[`DirContext.bind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#bind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-)
используется для добавления в контекст привязки с атрибутами. Он принимает в качестве аргументов имя
объекта, привязываемый объект и набор атрибутов.

```java
// Создаём объект для привязки
Fruit fruit = new Fruit("orange");

// Создаём атрибуты, которые будут связаны с объектом
Attributes attrs = new BasicAttributes(true); // без учёта регистра
Attribute objclass = new BasicAttribute("objectclass");
objclass.add("top");
objclass.add("organizationalUnit");
attrs.put(objclass);

// Выполняем привязку
ctx.bind("ou=favorite, ou=Fruits", fruit, attrs);
```

Этот пример создаёт объект класса `Fruit` и привязывает его к имени `ou=favorite` в контексте
`ou=Fruits`, относительно `ctx`. У этой привязки есть атрибут `objectclass`. Если впоследствии
выполнить поиск имени `ou=favorite, ou=Fruits` в `ctx`, то вы получите объект `fruit`. Если затем
получить атрибуты `ou=favorite, ou=Fruits`, то вы получите те атрибуты, с которыми объект был создан.
Ниже приведён вывод этого примера:

```
# java Bind
orange
attribute: objectclass
value: top
value: organizationalUnit
value: javaObject
value: javaNamingReference
attribute: javaclassname
value: Fruit
attribute: javafactory
value: FruitFactory
attribute: javareferenceaddress
value: #0#fruit#orange
attribute: ou
value: favorite
```

Показанные дополнительные атрибуты и значения атрибутов используются для хранения информации об объекте
(`fruit`). Эти дополнительные атрибуты подробнее рассматриваются в этом трейле.

Если запустить этот пример дважды, то вторая попытка завершится исключением
[`NameAlreadyBoundException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NameAlreadyBoundException.html).
Это потому, что имя `ou=favorite` уже привязано в контексте `ou=Fruits`. Чтобы вторая попытка прошла
успешно, нужно использовать `rebind()`.

### Замена привязки с атрибутами

Метод
[`DirContext.rebind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#rebind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-)
используется для добавления или замены привязки и её атрибутов. Он принимает те же аргументы, что и
`bind()`. Однако семантика `rebind()` требует, чтобы при уже привязанном имени оно было отвязано, а
вновь переданные объект и атрибуты — привязаны.

```java
// Создаём объект для привязки
Fruit fruit = new Fruit("lemon");

// Создаём атрибуты, которые будут связаны с объектом
Attributes attrs = new BasicAttributes(true); // без учёта регистра
Attribute objclass = new BasicAttribute("objectclass");
objclass.add("top");
objclass.add("organizationalUnit");
attrs.put(objclass);

// Выполняем привязку
ctx.rebind("ou=favorite, ou=Fruits", fruit, attrs);
```

При запуске этот пример заменяет привязку, созданную примером с `bind()`.

```
# java Rebind
lemon
attribute: objectclass
value: top
value: organizationalUnit
value: javaObject
value: javaNamingReference
attribute: javaclassname
value: Fruit
attribute: javafactory
value: FruitFactory
attribute: javareferenceaddress
value: #0#fruit#lemon
attribute: ou
value: favorite
```

## Поиск (Search)

Одна из самых полезных возможностей каталога — служба **«жёлтых страниц»** (*yellow pages*), или
**поиск** (*search*). Можно составить запрос, состоящий из атрибутов искомых записей, и отправить его
каталогу. Каталог в ответ возвращает список записей, удовлетворяющих запросу. Например, можно спросить
у каталога все записи со средним результатом в боулинге больше 200 или все записи, представляющие
человека с фамилией, начинающейся на «Sch».

Интерфейс
[`DirContext`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html)
предоставляет несколько методов поиска по каталогу с возрастающей степенью сложности и мощности.
Различные аспекты поиска по каталогу рассмотрены в следующих разделах:

- базовый поиск (*basic search*);
- фильтры поиска (*Search Filters*);
- элементы управления поиском (*Search Controls*).

### Базовый поиск (Basic Search)

Простейшая форма поиска требует указать набор атрибутов, которые должна иметь запись, и имя целевого
контекста, в котором выполнять поиск.

Следующий код создаёт набор атрибутов `matchAttrs`, имеющий два атрибута — `sn` и `mail`. Он указывает,
что подходящие записи должны иметь атрибут фамилии (`sn`) со значением `Geisel` и атрибут `mail` с
любым значением. Затем он вызывает метод
[`DirContext.search()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#search-javax.naming.Name-javax.naming.directory.Attributes-),
чтобы найти в контексте `ou=People` записи с атрибутами, указанными в `matchAttrs`.

```java
// Указываем атрибуты для сопоставления
// Запрашиваем объекты с атрибутом фамилии ("sn") со значением
// "Geisel" и с атрибутом "mail"

// без учёта регистра имени атрибута
Attributes matchAttrs = new BasicAttributes(true);
matchAttrs.put(new BasicAttribute("sn", "Geisel"));
matchAttrs.put(new BasicAttribute("mail"));

// Ищем объекты, имеющие совпадающие атрибуты
NamingEnumeration answer = ctx.search("ou=People", matchAttrs);
```

Затем результаты можно вывести так:

```java
while (answer.hasMore()) {
    SearchResult sr = (SearchResult)answer.next();
    System.out.println(">>>" + sr.getName());
    printAttrs(sr.getAttributes());
}
```

Метод `printAttrs()` похож на код из примера `getAttributes()`, выводящий набор атрибутов.

Запуск этого примера даёт следующий результат:

```
# java SearchRetAll
>>>cn=Ted Geisel
attribute: sn
value: Geisel
attribute: objectclass
value: top
value: person
value: organizationalPerson
value: inetOrgPerson
attribute: jpegphoto
value: [B@1dacd78b
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: facsimiletelephonenumber
value: +1 408 555 2329
attribute: cn
value: Ted Geisel
attribute: telephonenumber
value: +1 408 555 5252
```

#### Возврат выбранных атрибутов

Предыдущий пример возвращал все атрибуты, связанные с записями, удовлетворяющими указанному запросу.
Возвращаемые атрибуты можно выбрать, передав методу `search()` массив идентификаторов атрибутов,
которые нужно включить в результат. После создания `matchAttrs`, как показано выше, нужно также создать
массив идентификаторов атрибутов:

```java
// Указываем идентификаторы возвращаемых атрибутов
String[] attrIDs = {"sn", "telephonenumber", "golfhandicap", "mail"};

// Ищем объекты, имеющие совпадающие атрибуты
NamingEnumeration answer = ctx.search("ou=People", matchAttrs, attrIDs);
```

Этот пример возвращает атрибуты `sn`, `telephonenumber`, `golfhandicap` и `mail` записей, у которых
есть атрибут `mail` и атрибут `sn` со значением `Geisel`. Этот пример даёт следующий результат. (У
записи нет атрибута `golfhandicap`, поэтому он не возвращается.)

```
# java Search
>>>cn=Ted Geisel
attribute: sn
value: Geisel
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: telephonenumber
value: +1 408 555 5252
```

### Фильтры (Filters)

Помимо задания поиска с помощью набора атрибутов, можно задать поиск в форме **фильтра поиска**
(*search filter*). Фильтр поиска — это поисковый запрос, выраженный в форме логического выражения.
Синтаксис фильтров поиска, принимаемых методом
[`DirContext.search()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#search-javax.naming.Name-java.lang.String-javax.naming.directory.SearchControls-),
описан в [RFC 2254](http://www.ietf.org/rfc/rfc2254.txt).

Следующий фильтр поиска указывает, что подходящие записи должны иметь атрибут `sn` со значением
`Geisel` и атрибут `mail` с любым значением:

```
(&(sn=Geisel)(mail=*))
```

Следующий код создаёт фильтр и `SearchControls` по умолчанию и использует их для выполнения поиска.
Поиск эквивалентен поиску из примера базового поиска.

```java
// Создаём элементы управления поиском по умолчанию
SearchControls ctls = new SearchControls();

// Указываем фильтр поиска для сопоставления
// Запрашиваем объекты с атрибутом "sn" == "Geisel"
// и с атрибутом "mail"
String filter = "(&(sn=Geisel)(mail=*))";

// Ищем объекты с помощью фильтра
NamingEnumeration answer = ctx.search("ou=People", filter, ctls);
```

Запуск этого примера даёт следующий результат:

```
# java SearchWithFilterRetAll
>>>cn=Ted Geisel
attribute: sn
value: Geisel
attribute: objectclass
value: top
value: person
value: organizationalPerson
value: inetOrgPerson
attribute: jpegphoto
value: [B@1dacd75e
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: facsimiletelephonenumber
value: +1 408 555 2329
attribute: cn
value: Ted Geisel
attribute: telephonenumber
value: +1 408 555 5252
```

#### Краткий обзор синтаксиса фильтров поиска

Синтаксис фильтра поиска — это, по сути, логическое выражение в префиксной нотации (то есть логический
оператор стоит перед своими аргументами). В следующей таблице перечислены символы, используемые для
создания фильтров.

| Символ | Описание |
|--------|----------|
| `&` | конъюнкция (то есть *и* — всё в списке должно быть истинным) |
| `\|` | дизъюнкция (то есть *или* — одна или несколько альтернатив должны быть истинными) |
| `!` | отрицание (то есть *не* — отрицаемый элемент не должен быть истинным) |
| `=` | равенство (по правилу сопоставления атрибута) |
| `~=` | приближённое равенство (по правилу сопоставления атрибута) |
| `>=` | больше чем (по правилу сопоставления атрибута) |
| `<=` | меньше чем (по правилу сопоставления атрибута) |
| `=*` | наличие (то есть запись должна иметь атрибут, но его значение неважно) |
| `*` | подстановочный знак (указывает, что в этой позиции может стоять ноль или более символов); используется при задании сопоставляемых значений атрибута |
| `\` | экранирование (для экранирования `*`, `(` или `)`, когда они встречаются внутри значения атрибута) |

Каждый элемент фильтра составляется из идентификатора атрибута и либо значения атрибута, либо символов,
обозначающих значение атрибута. Например, элемент `sn=Geisel` означает, что атрибут `sn` должен иметь
значение `Geisel`, а элемент `mail=*` указывает, что атрибут `mail` должен присутствовать.

Каждый элемент должен быть заключён в скобки, как в `(sn=Geisel)`. Эти элементы составляются с помощью
логических операторов, таких как `&` (конъюнкция), для создания логических выражений, как в
`(& (sn=Geisel) (mail=*))`.

Каждое логическое выражение может далее состоять из других элементов, которые сами являются логическими
выражениями, как в `(| (& (sn=Geisel) (mail=*)) (sn=L*))`. Последний пример запрашивает либо записи,
имеющие одновременно атрибут `sn` со значением `Geisel` и атрибут `mail`, либо записи, у которых
атрибут `sn` начинается с буквы «L».

Полное описание синтаксиса см. в [RFC 2254](http://www.ietf.org/rfc/rfc2254.txt).

#### Возврат выбранных атрибутов

Предыдущий пример возвращал все атрибуты, связанные с записями, удовлетворяющими указанному фильтру.
Возвращаемые атрибуты можно выбрать, задав аргумент элементов управления поиском. Создайте массив
идентификаторов атрибутов, которые нужно включить в результат, и передайте его методу
[`SearchControls.setReturningAttributes()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#setReturningAttributes-java.lang.String:A-).
Пример:

```java
// Указываем идентификаторы возвращаемых атрибутов
String[] attrIDs = {"sn", "telephonenumber", "golfhandicap", "mail"};
SearchControls ctls = new SearchControls();
ctls.setReturningAttributes(attrIDs);
```

Этот пример эквивалентен примеру «Возврат выбранных атрибутов» из раздела базового поиска. Запуск этого
примера даёт следующие результаты. (У записи нет атрибута `golfhandicap`, поэтому он не возвращается.)

```
# java SearchWithFilter
>>>cn=Ted Geisel
attribute: sn
value: Geisel
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: telephonenumber
value: +1 408 555 5252
```

### Область видимости (Scope)

Элементы управления поиском
[`SearchControls`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html)
по умолчанию указывают, что поиск выполняется в именованном контексте
([`SearchControls.ONELEVEL_SCOPE`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#ONELEVEL_SCOPE)).
Это значение по умолчанию используется в примерах раздела «Фильтры поиска».

Помимо этого значения по умолчанию, можно указать, что поиск выполняется во **всём поддереве**
(*entire subtree*) или только в именованном объекте.

#### Поиск в поддереве

Поиск по всему поддереву охватывает именованный объект и всех его потомков. Чтобы заставить поиск вести
себя так, передайте
[`SearchControls.SUBTREE_SCOPE`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#SUBTREE_SCOPE)
методу
[`SearchControls.setSearchScope()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#setSearchScope-int-)
следующим образом:

```java
// Указываем идентификаторы возвращаемых атрибутов
String[] attrIDs = {"sn", "telephonenumber", "golfhandicap", "mail"};
SearchControls ctls = new SearchControls();
ctls.setReturningAttributes(attrIDs);
ctls.setSearchScope(SearchControls.SUBTREE_SCOPE);

// Указываем фильтр поиска для сопоставления
// Запрашиваем объекты с атрибутом "sn" == "Geisel"
// и с атрибутом "mail"
String filter = "(&(sn=Geisel)(mail=*))";

// Ищем объекты в поддереве с помощью фильтра
NamingEnumeration answer = ctx.search("", filter, ctls);
```

Этот пример ищет в поддереве контекста `ctx` записи, удовлетворяющие указанному фильтру. Он находит в
этом поддереве запись `cn=Ted Geisel, ou=People`, удовлетворяющую фильтру.

```
# java SearchSubtree
>>>cn=Ted Geisel, ou=People
attribute: sn
value: Geisel
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: telephonenumber
value: +1 408 555 5252
```

#### Поиск в именованном объекте

Можно также искать в самом именованном объекте. Это полезно, например, для проверки того,
удовлетворяет ли именованный объект фильтру поиска. Чтобы искать в именованном объекте, передайте
[`SearchControls.OBJECT_SCOPE`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#OBJECT_SCOPE)
методу `setSearchScope()`.

```java
// Указываем идентификаторы возвращаемых атрибутов
String[] attrIDs = {"sn", "telephonenumber", "golfhandicap", "mail"};
SearchControls ctls = new SearchControls();
ctls.setReturningAttributes(attrIDs);
ctls.setSearchScope(SearchControls.OBJECT_SCOPE);

// Указываем фильтр поиска для сопоставления
// Запрашиваем объекты с атрибутом "sn" == "Geisel"
// и с атрибутом "mail"
String filter = "(&(sn=Geisel)(mail=*))";

// Ищем объекты в поддереве с помощью фильтра
NamingEnumeration answer =
    ctx.search("cn=Ted Geisel, ou=People", filter, ctls);
```

Этот пример проверяет, удовлетворяет ли объект `cn=Ted Geisel, ou=People` заданному фильтру.

```
# java SearchObject
>>>
attribute: sn
value: Geisel
attribute: mail
value: Ted.Geisel@JNDITutorial.example.com
attribute: telephonenumber
value: +1 408 555 5252
```

Пример нашёл один ответ и вывел его. Обратите внимание, что имя результата — пустая строка. Это потому,
что имя объекта всегда задаётся относительно контекста поиска (в данном случае —
`cn=Ted Geisel, ou=People`).

### Ограничение количества результатов (Result Count)

Иногда запрос может дать слишком много ответов, и нужно ограничить число возвращаемых ответов. Это
можно сделать с помощью элемента управления «ограничение количества» (*count limit*). По умолчанию у
поиска нет ограничения количества — он вернёт все найденные ответы. Чтобы задать ограничение количества
поиска, передайте число методу
[`SearchControls.setCountLimit()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#setCountLimit-long-).

Следующий пример задаёт ограничение количества, равное 1:

```java
// Настраиваем элементы управления поиском так, чтобы ограничить количество до 1
SearchControls ctls = new SearchControls();
ctls.setCountLimit(1);
```

Если программа попытается получить больше результатов, чем задано ограничением количества, будет
выброшено исключение
[`SizeLimitExceededException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/SizeLimitExceededException.html).
Поэтому, если программа задала ограничение количества, она должна либо отличать это исключение от
других
[`NamingException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NamingException.html), либо
отслеживать ограничение количества и не запрашивать больше указанного числа результатов.

Задание ограничения количества для поиска — один из способов контролировать ресурсы (например, память
и пропускную способность сети), потребляемые приложением. Другие способы контроля потребляемых ресурсов:
сузить фильтр поиска (точнее указать искомое), начать поиск в подходящем контексте и использовать
подходящую область видимости.

### Ограничение времени (Time Limit)

Ограничение времени поиска задаёт верхнюю границу времени, в течение которого операция поиска будет
блокироваться в ожидании ответов. Это полезно, когда вы не хотите слишком долго ждать ответа. Если до
завершения операции поиска заданное ограничение времени будет превышено, будет выброшено исключение
[`TimeLimitExceededException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/TimeLimitExceededException.html).

Чтобы задать ограничение времени поиска, передайте число миллисекунд методу
[`SearchControls.setTimeLimit()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/SearchControls.html#setTimeLimit-int-).
Следующий пример задаёт ограничение времени в 1 секунду:

```java
// Ограничиваем время поиска 1 секундой (1000 мс)
SearchControls ctls = new SearchControls();
ctls.setTimeLimit(1000);
```

Чтобы этот конкретный пример превысил своё ограничение времени, нужно перенастроить его на использование
либо медленного сервера, либо сервера с большим числом записей. Также можно применить иные приёмы, чтобы
поиск занимал больше 1 секунды.

Ограничение времени, равное нулю, означает, что ограничение не задано и что вызовы к каталогу будут
ждать ответа неограниченно долго.

## Советы по диагностике (Trouble Shooting Tips)

Ниже перечислены наиболее распространённые проблемы, с которыми можно столкнуться при попытке запустить
успешно скомпилированную программу, использующую классы JNDI.

### 1. Вы получаете NoInitialContextException

**Причина.** Вы не указали, какую реализацию использовать для начального контекста. А именно, свойство
окружения
[`Context.INITIAL_CONTEXT_FACTORY`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#INITIAL_CONTEXT_FACTORY)
не было задано именем класса фабрики, создающей начальный контекст. Либо вы не сделали доступными
программе классы поставщика службы, указанного в `Context.INITIAL_CONTEXT_FACTORY`.

**Решение.** Задайте свойству окружения `Context.INITIAL_CONTEXT_FACTORY` имя класса используемой
реализации начального контекста. Подробности — в разделе «Настройка».

Если свойство было задано, убедитесь, что имя класса не было набрано с ошибкой и что названный класс
доступен программе (в её classpath или установлен в каталоге `jre/lib/ext` среды JRE). Платформа Java
включает поставщиков служб для LDAP, COS naming, DNS и реестра RMI. Все остальные поставщики служб
должны быть установлены и добавлены в среду исполнения.

### 2. Вы получаете CommunicationException с указанием «connection refused»

**Причина.** Сервер и порт, указанные в свойстве окружения `Context.PROVIDER_URL`, не обслуживаются
сервером. Возможно, кто-то отключил или выключил машину, на которой работает сервер. Либо вы ошиблись в
имени сервера или номере порта.

**Решение.** Проверьте, что на этом порту действительно работает сервер, и при необходимости
перезапустите его. Способ проверки зависит от используемого LDAP-сервера. Обычно доступна
административная консоль или инструмент, которым можно администрировать сервер. С его помощью можно
проверить состояние сервера.

### 3. LDAP-сервер отвечает другим утилитам (например, своей административной консоли), но, похоже, не отвечает на запросы вашей программы

**Причина.** Сервер не отвечает на запросы соединения LDAP v3. Некоторые серверы (особенно публичные)
неправильно отвечают на LDAP v3, игнорируя запросы вместо того, чтобы их отклонять. Также у некоторых
серверов LDAP v3 есть проблемы с обработкой управляющего элемента (*control*), который поставщик службы
LDAP от Oracle отправляет автоматически, и они часто возвращают специфичный для сервера код сбоя.

**Решение.** Попробуйте задать свойству окружения `java.naming.ldap.version` значение `2`. Поставщик
службы LDAP по умолчанию пытается соединиться с LDAP-сервером, используя LDAP v3; если это не удаётся,
он использует LDAP v2. Если сервер молча игнорирует запрос v3, то поставщик предполагает, что запрос
сработал. Чтобы обойти такие серверы, нужно явно задать версию протокола для обеспечения корректного
поведения сервера.

Если сервер — это сервер v3, то попробуйте задать следующее свойство окружения перед созданием
начального контекста:

```java
env.put(Context.REFERRAL, "throw");
```

Это отключит управляющий элемент, который поставщик LDAP отправляет автоматически. (Подробности — в
руководстве JNDI Tutorial.)

### 4. Программа зависает

**Причины.** Некоторые серверы (особенно публичные) не отвечают (даже отрицательным ответом), если вы
пытаетесь выполнить поиск, который дал бы слишком много результатов или потребовал бы от сервера
просмотреть слишком много записей для формирования ответа. Такие серверы пытаются ограничить объём
ресурсов, расходуемых на один запрос.

Либо вы попытались использовать Secure Socket Layer (SSL) против сервера/порта, который его не
поддерживает, и наоборот (то есть попытались использовать обычный сокет для связи с SSL-портом).

И наконец, сервер либо отвечает очень медленно из-за высокой нагрузки, либо по какой-то причине вовсе
не отвечает.

**Решение.** Если ваша программа зависает из-за того, что сервер пытается ограничить использование
своих ресурсов, повторите запрос, используя запрос, который вернёт один результат или лишь несколько.
Это поможет определить, жив ли сервер. Если жив, то можно расширить первоначальный запрос и отправить
его снова.

Если программа зависает из-за проблем с SSL, нужно выяснить, является ли порт SSL-портом, и затем
соответствующим образом задать свойство окружения
[`Context.SECURITY_PROTOCOL`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#SECURITY_PROTOCOL).
Если порт — SSL-порт, этому свойству следует присвоить значение `ssl`. Если это не SSL-порт, то это
свойство задавать не следует.

Если программа зависает ни по одной из вышеперечисленных причин, пригодится свойство
`com.sun.jndi.ldap.read.timeout` для задания тайм-аута чтения. Значение этого свойства — строковое
представление целого числа, обозначающего тайм-аут чтения в миллисекундах для операций LDAP. Если
поставщик LDAP не может получить ответ LDAP в течение этого периода, он прерывает попытку чтения. Целое
число должно быть больше нуля. Целое число, меньшее или равное нулю, означает, что тайм-аут чтения не
задан, что эквивалентно бесконечному ожиданию ответа до его получения.

Если это свойство не задано, по умолчанию ожидание ответа продолжается до его получения.

Например:

```java
env.put("com.sun.jndi.ldap.read.timeout", "5000");
```

заставляет поставщика службы LDAP прервать попытку чтения, если сервер не ответит в течение 5 секунд.

### 5. Вы получаете NameNotFoundException

**Причины.** При инициализации начального контекста для LDAP вы указываете корневое отличительное имя
(*root-distinguished name*). Например, если вы задали свойству окружения `Context.PROVIDER_URL`
начального контекста значение `ldap://ldapserver:389/o=JNDITutorial` и затем передали имя вроде
`cn=Joe,c=us`, то полное имя, которое вы передали службе LDAP, было `cn=Joe,c=us,o=JNDITutorial`. Если
именно это имя вы и имели в виду, то проверьте сервер, чтобы убедиться, что он содержит такую запись.

Также Oracle Directory Server возвращает эту ошибку, если вы указываете некорректное отличительное имя
для целей аутентификации. Например, поставщик LDAP выбросит
[`NameNotFoundException`](https://docs.oracle.com/javase/8/docs/api/javax/naming/NameNotFoundException.html),
если вы зададите свойству окружения
[`Context.SECURITY_PRINCIPAL`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#SECURITY_PRINCIPAL)
значение `cn=Admin, o=Tutorial`, а `cn=Admin, o=Tutorial` не является записью на LDAP-сервере. На самом
деле корректной ошибкой Oracle Directory Server должна быть ошибка, связанная с аутентификацией, а не
«имя не найдено».

**Решение.** Проверьте, что указанное вами имя — это имя записи, существующей на сервере. Это можно
сделать, перечислив родительский контекст записи или используя другой инструмент, например
административную консоль сервера каталогов.

---

Ниже перечислены проблемы, с которыми можно столкнуться при попытке развернуть апплет, использующий
классы JNDI.

### 6. Вы получаете AppletSecurityException, когда апплет пытается связаться с сервером каталогов, работающим на машине, отличной от той, с которой был загружен апплет

**Причина.** Ваш апплет не был подписан, поэтому он может соединяться только с той машиной, с которой
был загружен. Либо, если апплет был подписан, браузер не выдал апплету разрешение на соединение с
машиной сервера каталогов.

**Решение.** Если вы хотите позволить апплету соединяться с серверами каталогов, работающими на
произвольных машинах, нужно подписать **как** ваш апплет, **так и** все JAR-файлы JNDI, которые апплет
будет использовать. Информацию о подписи jar-файлов см. в *Signing and Verifying JAR files*.

### 7. Вы получаете AppletSecurityException, когда апплет пытается настроить свойства окружения с помощью системных свойств

**Причина.** Веб-браузеры ограничивают доступ к системным свойствам и выбрасывают `SecurityException`
при попытке их прочитать.

**Решение.** Если вам нужно получить ввод для апплета, попробуйте вместо этого использовать параметры
апплета (*applet params*).

### 8. Вы получаете AppletSecurityException, когда апплет, работающий внутри Firefox, пытается аутентифицироваться с помощью CRAM-MD5 на LDAP-сервере

**Причина.** Firefox отключает доступ к пакетам `java.security`. Поставщик LDAP использовал
функциональность хеширования сообщений, предоставляемую `java.security.MessageDigest`, для реализации
CRAM-MD5.

**Решение.** Используйте Java Plug-in.

## Источник

- [Lesson: Naming and Directory Operations](https://docs.oracle.com/javase/tutorial/jndi/ops/index.html) — официальное руководство Oracle.
- [Lookup an Object](https://docs.oracle.com/javase/tutorial/jndi/ops/lookup.html)
- [List the Context](https://docs.oracle.com/javase/tutorial/jndi/ops/list.html)
- [Add, Replace or Remove a Binding](https://docs.oracle.com/javase/tutorial/jndi/ops/bind.html)
- [Rename](https://docs.oracle.com/javase/tutorial/jndi/ops/rename.html)
- [Create and Destroy Subcontexts](https://docs.oracle.com/javase/tutorial/jndi/ops/create.html)
- [Attribute Names](https://docs.oracle.com/javase/tutorial/jndi/ops/attrnames.html)
- [Read Attributes](https://docs.oracle.com/javase/tutorial/jndi/ops/getattrs.html)
- [Modify Attributes](https://docs.oracle.com/javase/tutorial/jndi/ops/modattrs.html)
- [Add, Replace Bindings with Attributes](https://docs.oracle.com/javase/tutorial/jndi/ops/bindattr.html)
- [Search](https://docs.oracle.com/javase/tutorial/jndi/ops/search.html)
- [Basic Search](https://docs.oracle.com/javase/tutorial/jndi/ops/basicsearch.html)
- [Filters](https://docs.oracle.com/javase/tutorial/jndi/ops/filter.html)
- [Scope](https://docs.oracle.com/javase/tutorial/jndi/ops/scope.html)
- [Result Count](https://docs.oracle.com/javase/tutorial/jndi/ops/countlimit.html)
- [Time Limit](https://docs.oracle.com/javase/tutorial/jndi/ops/timelimit.html)
- [Trouble Shooting Tips](https://docs.oracle.com/javase/tutorial/jndi/ops/faq.html)
