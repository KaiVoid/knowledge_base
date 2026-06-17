# Урок 6. Доступ к объектам в каталоге

**Трейл:** JNDI · **Оригинал:** [Accessing Objects in the Directory](https://docs.oracle.com/javase/tutorial/jndi/objects/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Урок объединяет
> страницы *Java Objects in the Directory* (index), *Storing and Reading Objects* (store)
> и *Serializable Objects* (serial) трейла **Java Naming and Directory Interface (JNDI)**.

> **Внимание.** Руководство The Java Tutorials написано для JDK 8. Примеры и приёмы,
> описанные на этой странице, не учитывают улучшений, появившихся в более поздних выпусках,
> и могут использовать технологии, которые более недоступны. Актуальные руководства —
> на [Dev.java](https://dev.java/learn/).

## Объекты Java в каталоге

> Традиционно каталоги (*directory*) использовались для хранения данных. Пользователи и
> программисты воспринимают каталог как иерархию записей каталога (*directory entries*), каждая
> из которых содержит набор атрибутов (*attributes*). Вы извлекаете запись из каталога и
> получаете нужный атрибут (или атрибуты).

> В приложениях, написанных на языке программирования Java, объекты Java иногда требуется
> совместно использовать между приложениями. Для таких приложений имеет смысл использовать
> каталог как хранилище (*repository*) объектов Java. Каталог предоставляет централизованно
> администрируемую и, возможно, реплицируемую службу, которой могут пользоваться приложения
> Java, распределённые по сети. Например, сервер приложений (*application server*) может
> использовать каталог для регистрации объектов, представляющих управляемые им службы, чтобы
> клиент позже мог обращаться к каталогу и находить нужные службы по мере необходимости. Пример
> использования JNDI в качестве каталога служб — Apache DS. Подробнее об этом — на сайте
> [Apache Directory](http://directory.apache.org/).

> JNDI предоставляет объектно-ориентированное представление каталога, что позволяет добавлять
> объекты Java в каталог и извлекать их оттуда, не требуя от клиента решать вопросы
> представления данных (*data representation*). Этот урок рассматривает использование каталога
> для хранения и извлечения объектов Java на базовом уровне. JNDI предоставляет так называемые
> фабрики объектов (*object factories*) и фабрики состояний (*state factories*) для создания и
> хранения объектов, извлекаемых из каталога.

### Фабрика объектов (Object Factory)

> Фабрика объектов (*object factory*) — это производитель объектов. Она принимает некоторую
> информацию о том, как создать объект (например, ссылку — *reference*), и возвращает экземпляр
> этого объекта. Подробнее о фабриках объектов и о формате, в котором объекты хранятся в
> каталоге, см. в [JNDI Tutorial](https://docs.oracle.com/javase/jndi/tutorial/objects/factory/index.html).

### Фабрика состояний (State Factory)

> Фабрика состояний (*state factory*) преобразует один объект в другой. На вход подаётся объект
> и необязательные атрибуты, передаваемые в `Context.bind()`, а на выходе получается другой
> объект и необязательные атрибуты, которые будут сохранены в нижележащей службе именования
> (*naming service*) или каталоге. Подробнее о фабриках состояний и о том, как написать свою
> собственную фабрику состояний, см. в
> [JNDI Tutorial](https://docs.oracle.com/javase/jndi/tutorial/objects/state/index.html).

> Следующая часть урока рассказывает о том, как обращаться к объектам в каталоге. В ней описано,
> как сериализуемые объекты могут сохраняться в каталоге и считываться из него. О других типах
> объектов см. [JNDI Tutorial](https://docs.oracle.com/javase/jndi/tutorial/objects/index.html).

## Хранение и чтение объектов

> Приложения и службы могут использовать каталог для хранения и поиска объектов по-разному:
>
> - Хранить (копию) самого объекта.
> - Хранить ссылку (*reference*) на объект.
> - Хранить атрибуты, описывающие объект.

> В общих чертах, сериализованная форма объекта Java содержит состояние объекта, а ссылка на
> объект (*object's reference*) — компактное представление адресной информации, которую можно
> использовать для связи с объектом. Некоторые примеры приведены в уроке
> [Lookup an Object](https://docs.oracle.com/javase/tutorial/jndi/ops/lookup.html). Атрибуты
> объекта — это свойства, используемые для описания объекта; атрибуты могут включать адресную
> информацию и/или информацию о состоянии.

> Какой из этих трёх способов выбрать, зависит от создаваемого приложения/системы и от того, как
> оно должно взаимодействовать с другими приложениями и системами, которые будут совместно
> использовать объекты, хранящиеся в каталоге. Ещё один фактор — поддержка со стороны поставщика
> службы (*service provider*) и нижележащей службы каталогов (*directory service*).

> Программно все приложения при сохранении объектов в каталоге используют один из следующих
> методов:
>
> - [`Context.bind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#bind-javax.naming.Name-java.lang.Object-)
> - [`DirContext.bind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#bind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-)
> - [`Context.rebind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#rebind-javax.naming.Name-java.lang.Object-)
> - [`DirContext.rebind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#rebind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-)

> Приложение передаёт одному из этих методов объект, который требуется сохранить. Затем, в
> зависимости от типов объектов, поддерживаемых поставщиком службы, объект преобразуется в
> представление, приемлемое для нижележащей службы каталогов.

> Этот урок показывает, как сохранять сериализуемые объекты в каталоге. После того как объект
> сохранён, для получения копии объекта обратно из каталога достаточно воспользоваться методом
> [`lookup()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#lookup-javax.naming.Name-),
> независимо от того, какой тип информации был фактически сохранён.

> Получить объект обратно можно не только с помощью `lookup()`, но и при перечислении
> (*[list](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#list-javax.naming.Name-)*)
> контекста, а также при поиске
> (*[search](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#search-javax.naming.Name-)*)
> в контексте или его поддереве. Во всех этих случаях могут задействоваться *фабрики объектов*
> (*object factories*). Фабрики объектов подробно рассматриваются в
> [JNDI Tutorial](https://docs.oracle.com/javase/jndi/tutorial/objects/factory/index.html).

> Для хранения перечисленных ниже типов объектов обратитесь к JNDI Tutorial:
>
> - [Referenceable-объекты и ссылки JNDI (References)](https://docs.oracle.com/javase/jndi/tutorial/objects/storing/reference.html).
>   Примеры использования `bind()` в уроке
>   [Add, Replace or Remove a Binding](https://docs.oracle.com/javase/tutorial/jndi/ops/bind.html)
>   используют Referenceable-объекты.
> - [Объекты с атрибутами (DirContext)](https://docs.oracle.com/javase/jndi/tutorial/objects/storing/dircontext.html).
> - [Объекты RMI (Java Remote Method Invocation), включая использующие IIOP](https://docs.oracle.com/javase/jndi/tutorial/objects/storing/remote.html).
> - [Объекты CORBA](https://docs.oracle.com/javase/jndi/tutorial/objects/storing/corba.html).

> **Прежде чем продолжить.** Чтобы успешно запустить эти примеры, необходимо либо отключить
> проверку схемы (*schema-checking*) на сервере, либо добавить на сервер
> [Java-схему](https://docs.oracle.com/javase/tutorial/jndi/software/config/java.schema),
> прилагаемую к этому руководству. Обычно эту задачу выполняет администратор сервера каталогов.
> Подробнее см. в уроке
> [Software Setup](https://docs.oracle.com/javase/tutorial/jndi/software/content.html#SCHEMA).

> **Windows Active Directory.** Методы
> [`Context.rebind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#rebind-javax.naming.Name-java.lang.Object-)
> и
> [`DirContext.rebind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#rebind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-)
> не работают с Active Directory, потому что они действуют так: считывают атрибуты обновляемой
> записи, удаляют запись, а затем добавляют новую запись с изменёнными атрибутами. Active
> Directory возвращает некоторые атрибуты, которые не могут быть установлены пользователем, из-за
> чего завершающий шаг добавления завершается ошибкой. Обходное решение этой проблемы — с помощью
> [`DirContext.getAttributes()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#getAttributes-javax.naming.Name-)
> получить и сохранить атрибуты, которые вы хотите сохранить. Затем удалить запись и добавить её
> обратно с сохранёнными атрибутами (и любыми другими, которые вы хотите добавить) с помощью
> [`DirContext.bind()`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#bind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-).

## Сериализуемые объекты (Serializable Objects)

> *Сериализовать* (*serialize*) объект — значит преобразовать его состояние в поток байтов
> (*byte stream*), чтобы этот поток байтов можно было снова превратить в копию объекта. Объект
> Java является *сериализуемым* (*serializable*), если его класс или любой из его суперклассов
> реализует интерфейс `java.io.Serializable` либо его подынтерфейс `java.io.Externalizable`.
> *Десериализация* (*deserialization*) — это процесс преобразования сериализованной формы
> объекта обратно в копию объекта.

> Например, класс `java.awt.Button` реализует интерфейс `Serializable`, поэтому вы можете
> сериализовать объект `java.awt.Button` и сохранить это сериализованное состояние в файле.
> Позднее вы можете прочитать сериализованное состояние обратно и десериализовать его в объект
> `java.awt.Button`.

> Платформа Java задаёт способ сериализации сериализуемых объектов по умолчанию. (Java-)класс
> может переопределить эту сериализацию по умолчанию и определить собственный способ сериализации
> объектов этого класса. Подробно сериализация объектов описана в
> [Object Serialization Specification](https://docs.oracle.com/javase/8/docs/technotes/guides/serialization/index.html).

> Когда объект сериализуется, в сериализованный поток записывается информация, идентифицирующая
> его класс. Однако само определение класса («class-файл») при этом не записывается. Определять,
> как найти и загрузить необходимые class-файлы, должна система, которая десериализует объект.
> Например, приложение Java может включать в свой classpath JAR-файл, содержащий class-файлы
> сериализованных объектов, либо загружать определения классов с помощью информации, хранящейся в
> каталоге, как объясняется далее в этом уроке.

### Привязка сериализуемого объекта (Binding a Serializable Object)

> Вы можете сохранить сериализуемый объект в каталоге, если нижележащий поставщик службы
> поддерживает это действие, как, например, поставщик службы LDAP от Oracle.

> Следующий пример вызывает
> [`Context.bind`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#bind-javax.naming.Name-java.lang.Object-),
> чтобы привязать AWT-кнопку (*button*) к имени `"cn=Button"`. Чтобы связать атрибуты с новой
> привязкой (*binding*), используется
> [`DirContext.bind`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#bind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-).
> Чтобы перезаписать существующую привязку, используйте
> [`Context.rebind`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#rebind-javax.naming.Name-java.lang.Object-)
> и
> [`DirContext.rebind`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#rebind-javax.naming.Name-java.lang.Object-javax.naming.directory.Attributes-).

```java
// Создаём объект, который нужно привязать
Button b = new Button("Push me");

// Выполняем привязку
ctx.bind("cn=Button", b);
```

> Затем можно прочитать объект обратно с помощью
> [`Context.lookup`](https://docs.oracle.com/javase/8/docs/api/javax/naming/Context.html#lookup-javax.naming.Name-),
> как показано ниже.

```java
// Проверяем, что объект привязан
Button b2 = (Button)ctx.lookup("cn=Button");
System.out.println(b2);
```

> Запуск [этого примера](https://docs.oracle.com/javase/tutorial/jndi/objects/examples/SerObj.java)
> выводит следующее.

```
# java SerObj
java.awt.Button[button0,0,0,0x0,invalid,label=Push me]
```

### Указание codebase (Specifying a Codebase)

> **Примечание.** Описанные здесь процедуры предназначены для привязки сериализуемого объекта в
> службе каталогов, следующей схеме, определённой в
> [RFC 2713](http://www.ietf.org/rfc/rfc2713.txt). Эти процедуры могут быть в общем случае
> неприменимы к другим службам именования и каталогов, поддерживающим привязку сериализуемого
> объекта с указанным codebase.

> Когда сериализованный объект привязывается в каталоге, как показано в предыдущем примере,
> приложения, читающие сериализованный объект из каталога, должны иметь доступ к определениям
> классов, необходимым для десериализации объекта.

> В качестве альтернативы вы можете записать *codebase* вместе с сериализованным объектом в
> каталоге — либо при привязке объекта, либо позже, добавив атрибут с помощью
> [`DirContext.modifyAttributes`](https://docs.oracle.com/javase/8/docs/api/javax/naming/directory/DirContext.html#modifyAttributes-javax.naming.Name-int-javax.naming.directory.Attributes-).
> Для записи этого codebase можно использовать любой атрибут и затем заставить приложение
> считывать его из каталога и использовать соответствующим образом. Либо вы можете использовать
> атрибут `"javaCodebase"`, заданный в RFC 2713. В последнем случае поставщик службы LDAP от
> Oracle автоматически использует этот атрибут для загрузки определений классов по мере
> необходимости. Атрибут `"javaCodebase"` должен содержать URL каталога-codebase или
> JAR-файла. Если codebase содержит более одного URL, то каждый URL должен отделяться символом
> пробела.

> Следующий пример похож на пример с привязкой `java.awt.Button`. Отличие в том, что он
> использует определённый пользователем сериализуемый класс
> [`Flower`](https://docs.oracle.com/javase/tutorial/jndi/objects/examples/Flower.java)
> и задаёт атрибут `"javaCodebase"`, содержащий местоположение определения класса `Flower`. Вот
> код, выполняющий привязку.

```java
String codebase = ...;

// Создаём объект, который нужно привязать
Flower f = new Flower("rose", "pink");

// Выполняем привязку и указываем codebase
ctx.bind("cn=Flower", f, new BasicAttributes("javaCodebase", codebase));
```

> При запуске [этого примера](https://docs.oracle.com/javase/tutorial/jndi/objects/examples/SerObjWithCodebase.java)
> необходимо указать URL местоположения, в которое был установлен class-файл `Flower.class`.
> Например, если `Flower.class` установлен на веб-сервере `web1` в каталоге `example/classes`,
> то пример запускается так.

```
# java SerObjWithCodebase http://web1/example/classes/
pink rose
```

> После этого вы можете удалить `Flower.class` из своего classpath и запустить любую программу,
> которая ищет (*lookup*) или перечисляет (*list*) этот объект, не ссылаясь напрямую на класс
> `Flower`. Если же ваша программа ссылается на `Flower` напрямую, то необходимо сделать его
> class-файл доступным для компиляции и выполнения.

## Источник

- [Java Objects in the Directory](https://docs.oracle.com/javase/tutorial/jndi/objects/index.html) — официальное руководство Oracle (The Java Tutorials, JDK 8).
- [Storing and Reading Objects](https://docs.oracle.com/javase/tutorial/jndi/objects/store.html) — официальное руководство Oracle.
- [Serializable Objects](https://docs.oracle.com/javase/tutorial/jndi/objects/serial.html) — официальное руководство Oracle.
