# Урок 2. Знакомство с MBean

**Трейл:** JMX · **Оригинал:** [Introducing MBeans](https://docs.oracle.com/javase/tutorial/jmx/mbeans/index.html)
**Связанные области:** [[22-containers-devops]] · **Вопросы:** containers-devops

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8), урок *Introducing MBeans* трейла Java Management Extensions (JMX). Объединяет страницы *Lesson: Introducing MBeans*, *Standard MBeans* и *MXBeans*.
>
> *Примечание Oracle: руководство написано для JDK 8. Примеры и приёмы, описанные здесь, не учитывают улучшений, появившихся в более поздних выпусках, и могут использовать технологии, которые больше недоступны. Актуальные руководства — на [Dev.java](https://dev.java/learn/).*

Этот урок знакомит с фундаментальным понятием API JMX — управляемыми бинами (*managed beans*), или **MBean**.

MBean — это управляемый объект Java, похожий на компонент JavaBeans, который следует шаблонам проектирования, установленным спецификацией JMX. MBean может представлять устройство, приложение или любой ресурс, которым нужно управлять. MBean предоставляет **управляющий интерфейс** (*management interface*), состоящий из следующего:

- набор атрибутов, доступных для чтения, для записи или для того и другого;
- набор вызываемых операций (*invokable operations*);
- самоописание (*self-description*).

Управляющий интерфейс не меняется на протяжении всей жизни экземпляра MBean. Кроме того, MBean могут испускать **уведомления** (*notifications*), когда происходят определённые заранее заданные события.

Спецификация JMX определяет пять типов MBean:

- стандартные MBean (*Standard MBeans*);
- динамические MBean (*Dynamic MBeans*);
- открытые MBean (*Open MBeans*);
- модельные MBean (*Model MBeans*);
- MXBean.

Примеры этого трейла демонстрируют только простейшие типы MBean, а именно стандартные MBean и MXBean.

## Стандартные MBean (Standard MBeans)

В этом разделе представлен пример простого стандартного MBean.

Стандартный MBean определяется написанием Java-интерфейса с именем `SomethingMBean` и Java-класса с именем `Something`, который реализует этот интерфейс. Каждый метод интерфейса задаёт в MBean либо **атрибут** (*attribute*), либо **операцию** (*operation*). По умолчанию каждый метод задаёт операцию. Атрибуты и операции — это методы, следующие определённым шаблонам проектирования. Стандартный MBean состоит из интерфейса MBean и класса. Интерфейс MBean перечисляет методы для всех предоставляемых атрибутов и операций. Класс реализует этот интерфейс и обеспечивает функциональность инструментированного ресурса.

В следующих разделах рассматривается пример стандартного MBean и простого агента JMX (*JMX agent*) с поддержкой технологии JMX, который управляет этим MBean.

### Интерфейс MBean

Пример базового интерфейса MBean, `HelloMBean`, приведён ниже:

```java
package com.example;

public interface HelloMBean {

    public void sayHello();
    public int add(int x, int y);

    public String getName();

    public int getCacheSize();
    public void setCacheSize(int size);
}
```

По соглашению интерфейс MBean получает имя реализующего его Java-класса с добавленным суффиксом *`MBean`*. В данном случае интерфейс называется `HelloMBean`. Класс `Hello`, реализующий этот интерфейс, описан в следующем разделе.

Согласно спецификации JMX, интерфейс MBean состоит из именованных и типизированных атрибутов, доступных для чтения и, возможно, для записи, а также именованных и типизированных операций, которые могут вызываться приложениями, управляемыми этим MBean. Интерфейс `HelloMBean` объявляет две операции: Java-методы `add()` и `sayHello()`.

`HelloMBean` объявляет два атрибута: `Name` — строка только для чтения, а `CacheSize` — целое число, доступное и для чтения, и для записи. Методы-геттеры и сеттеры объявлены для того, чтобы управляемое приложение могло получать доступ к значениям атрибутов и, возможно, изменять их. Как определено спецификацией JMX, **геттер** (*getter*) — это любой публичный метод, который не возвращает void и имя которого начинается с `get`. Геттер позволяет менеджеру читать значение атрибута, тип которого совпадает с типом возвращаемого объекта. **Сеттер** (*setter*) — это любой публичный метод, который принимает один параметр и имя которого начинается с `set`. Сеттер позволяет менеджеру записывать в атрибут новое значение, тип которого совпадает с типом параметра.

Реализация этих операций и атрибутов показана в следующем разделе.

### Реализация MBean

Java-класс `Hello`, приведённый ниже, реализует интерфейс MBean `HelloMBean`:

```java
package com.example;

public class Hello ...
    implements HelloMBean {
    public void sayHello() {
        System.out.println("hello, world");
    }

    public int add(int x, int y) {
        return x + y;
    }

    public String getName() {
        return this.name;
    }

    public int getCacheSize() {
        return this.cacheSize;
    }

    public synchronized void setCacheSize(int size) {
        ...

        this.cacheSize = size;
        System.out.println("Cache size now " + this.cacheSize);
    }
    ...

    private final String name = "Reginald";
    private int cacheSize = DEFAULT_CACHE_SIZE;
    private static final int
        DEFAULT_CACHE_SIZE = 200;
}
```

Простой класс `Hello` предоставляет определения операций и атрибутов, объявленных в `HelloMBean`. Операции `sayHello()` и `add()` крайне просты, но реальные операции могут быть как простыми, так и сколь угодно сложными.

Также определены методы для получения атрибута `Name` и для получения и установки атрибута `CacheSize`. В этом примере значение атрибута `Name` никогда не меняется. Однако в реальном сценарии этот атрибут мог бы меняться по мере работы управляемого ресурса. Например, атрибут мог бы представлять статистику — такую как время работы (*uptime*) или использование памяти. Здесь же это просто имя `Reginald`.

Вызов метода `setCacheSize` позволяет изменить атрибут `CacheSize` относительно объявленного значения по умолчанию, равного 200. В реальном сценарии изменение атрибута `CacheSize` могло бы потребовать выполнения других операций — например, удаления записей или выделения новых. Этот пример лишь печатает сообщение, подтверждающее, что размер кэша изменился. Однако вместо простого вызова `println()` можно было бы определить более сложные операции.

Когда MBean `Hello` и его интерфейс определены таким образом, их можно использовать для управления представляемым ими ресурсом, как показано в следующем разделе.

### Создание агента JMX для управления ресурсом

После того как ресурс инструментирован с помощью MBean, управление этим ресурсом выполняется агентом JMX (*JMX agent*).

Центральный компонент агента JMX — **сервер MBean** (*MBean server*). Сервер MBean — это сервер управляемых объектов, в котором регистрируются MBean. Агент JMX также включает набор служб для управления MBean. Подробности реализации сервера MBean смотрите в документации API интерфейса `MBeanServer`.

Класс `Main`, приведённый ниже, представляет базовый агент JMX:

```java
package com.example;

import java.lang.management.*;
import javax.management.*;

public class Main {

    public static void main(String[] args)
        throws Exception {

        MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
        ObjectName name = new ObjectName("com.example:type=Hello");
        Hello mbean = new Hello();
        mbs.registerMBean(mbean, name);

        ...

        System.out.println("Waiting forever...");
        Thread.sleep(Long.MAX_VALUE);
    }
}
```

Агент JMX `Main` начинает с получения сервера MBean, созданного и инициализированного платформой, вызывая метод `getPlatformMBeanServer()` класса `java.lang.management.ManagementFactory`. Если платформа ещё не создала сервер MBean, то `getPlatformMBeanServer()` создаёт его автоматически, вызывая JMX-метод `MBeanServerFactory.createMBeanServer()`. Экземпляр `MBeanServer`, полученный `Main`, называется `mbs`.

Далее `Main` определяет имя объекта (*object name*) для экземпляра MBean, который он создаст. Каждый MBean в JMX должен иметь имя объекта. Имя объекта — это экземпляр JMX-класса `ObjectName`, который должен соответствовать синтаксису, определённому спецификацией JMX. А именно, имя объекта должно содержать **домен** (*domain*) и список ключей-свойств (*key-properties*). В имени объекта, определённом `Main`, домен — это `com.example` (пакет, в котором содержится MBean из примера). Кроме того, ключ-свойство объявляет, что этот объект имеет тип `Hello`.

Создаётся экземпляр объекта `Hello` с именем `mbean`. Затем объект `Hello` с именем `mbean` регистрируется как MBean в сервере MBean `mbs` под именем объекта `name` — для этого объект и имя объекта передаются в вызов JMX-метода `MBeanServer.registerMBean()`.

После регистрации MBean `Hello` в сервере MBean `Main` просто ожидает выполнения управляющих операций над `Hello`. В этом примере такими управляющими операциями являются вызов `sayHello()` и `add()`, а также получение и установка значений атрибутов.

### Запуск примера стандартного MBean

Рассмотрев классы примера, теперь можно запустить его. В этом примере для взаимодействия с MBean используется JConsole.

Чтобы запустить пример, выполните следующие шаги:

1. Сохраните комплект примеров классов API JMX, `jmx_examples.zip`, в свой рабочий каталог `work_dir`.
2. Распакуйте комплект примеров классов следующей командой в окне терминала:

   ```
   unzip jmx_examples.zip
   ```

3. Скомпилируйте Java-классы примера из каталога `work_dir`:

   ```
   javac com/example/*.java
   ```

4. Если вы используете Java Development Kit (JDK) версии 6, запустите приложение `Main` следующей командой:

   ```
   java com.example.Main
   ```

   Если вы используете версию JDK старше 6, приложение `Main` нужно запустить с указанной ниже опцией, чтобы открыть приложение для мониторинга и управления:

   ```
   java -Dcom.sun.management.jmxremote example.Main
   ```

   Отображается подтверждение того, что `Main` ожидает наступления какого-либо события.

5. Запустите JConsole в другом окне терминала на той же машине:

   ```
   jconsole
   ```

   Отображается диалоговое окно New Connection (Новое подключение) со списком запущенных агентов JMX, к которым можно подключиться.

6. В диалоговом окне New Connection выберите из списка `com.example.Main` и нажмите Connect (Подключить).

   Отображается сводка текущей активности вашей платформы.

7. Перейдите на вкладку MBeans.

   На этой панели показаны все MBean, зарегистрированные в данный момент в сервере MBean.

8. В левом фрейме разверните узел `com.example` в дереве MBean.

   Вы увидите пример MBean `Hello`, созданный и зарегистрированный классом `Main`. Если щёлкнуть `Hello`, отобразятся связанные с ним узлы Attributes (Атрибуты) и Operations (Операции) в дереве MBean.

9. Разверните узел Attributes MBean `Hello` в дереве MBean.

   Отображаются атрибуты MBean, определённые классом `Hello`.

10. Измените значение атрибута `CacheSize` на 150.

    В окне терминала, где запущен `Main`, генерируется подтверждение этого изменения атрибута.

11. Разверните узел Operations MBean `Hello` в дереве MBean.

    Становятся видны две операции, объявленные MBean `Hello`: `sayHello()` и `add()`.

12. Вызовите операцию `sayHello()`, нажав кнопку `sayHello`.

    Диалоговое окно JConsole сообщает, что метод был вызван успешно. Сообщение *"hello, world"* генерируется в окне терминала, где запущен `Main`.

13. Укажите два целых числа для операции `add()`, чтобы сложить их, и нажмите кнопку `add`.

    Ответ отображается в диалоговом окне JConsole.

14. Чтобы закрыть JConsole, выберите Connection -> Exit (Подключение -> Выход).

## MXBean

В этом разделе объясняется особый тип MBean — **MXBean**.

MXBean — это тип MBean, который ссылается только на предопределённый набор типов данных. Благодаря этому вы можете быть уверены, что ваш MBean будет пригоден для использования любым клиентом, включая удалённых клиентов, без требования, чтобы клиент имел доступ к специфичным для модели классам, представляющим типы ваших MBean. MXBean предоставляют удобный способ связать вместе сопутствующие значения, не требуя специальной настройки клиентов для работы с этими наборами.

Так же, как и стандартный MBean, MXBean определяется написанием Java-интерфейса с именем `SomethingMXBean` и Java-класса, который реализует этот интерфейс. Однако, в отличие от стандартных MBean, для MXBean Java-класс не обязан называться `Something`. Каждый метод интерфейса задаёт в MXBean либо атрибут, либо операцию. Для аннотирования Java-интерфейса можно также использовать аннотацию `@MXBean` вместо требования, чтобы имя интерфейса заканчивалось суффиксом MXBean.

MXBean существовали ещё в платформе Java 2 Platform, Standard Edition (J2SE) 5.0 — в пакете [`java.lang.management`](https://docs.oracle.com/javase/8/docs/api/java/lang/management/package-summary.html). Однако теперь пользователи могут определять собственные MXBean в дополнение к стандартному набору, определённому в `java.lang.management`.

Главная идея MXBean состоит в том, что типы, такие как [`java.lang.management.MemoryUsage`](https://docs.oracle.com/javase/8/docs/api/java/lang/management/MemoryUsage.html), на которые ссылается интерфейс MXBean — в данном случае [`java.lang.management.MemoryMXBean`](https://docs.oracle.com/javase/8/docs/api/java/lang/management/MemoryMXBean.html), — отображаются (*mapped*) в стандартный набор типов, так называемые **открытые типы** (*Open Types*), определённые в пакете [`javax.management.openmbean`](https://docs.oracle.com/javase/8/docs/api/javax/management/openmbean/package-summary.html). Точные правила отображения приведены в спецификации MXBean. Однако общий принцип таков: простые типы, такие как int или String, остаются неизменными, тогда как сложные типы, такие как `MemoryUsage`, отображаются в стандартный тип [`CompositeDataSupport`](https://docs.oracle.com/javase/8/docs/api/javax/management/openmbean/CompositeDataSupport.html).

Пример MXBean состоит из следующих файлов, которые находятся в [`jmx_examples.zip`](https://docs.oracle.com/javase/tutorial/jmx/examples/jmx_examples.zip):

- интерфейс `QueueSamplerMXBean`;
- класс `QueueSampler`, реализующий интерфейс MXBean;
- Java-тип `QueueSample`, возвращаемый методом `getQueueSample()` интерфейса MXBean;
- `Main` — программа, которая настраивает и запускает пример.

Пример MXBean использует эти классы для выполнения следующих действий:

- определяет простой MXBean, который управляет ресурсом типа `Queue<String>`;
- объявляет в MXBean геттер `getQueueSample`, который при вызове делает снимок (*snapshot*) очереди и возвращает Java-класс `QueueSample`, связывающий вместе следующие значения:
  - время, когда был сделан снимок;
  - размер очереди;
  - голову очереди (*head*) на данный момент;
- регистрирует MXBean в сервере MBean.

### Интерфейс MXBean

Следующий код показывает пример интерфейса MXBean [`QueueSamplerMXBean`](https://docs.oracle.com/javase/tutorial/jmx/examples/QueueSamplerMXBean.java):

```java
package com.example;

public interface QueueSamplerMXBean {
    public QueueSample getQueueSample();
    public void clearQueue();
}
```

Обратите внимание, что интерфейс MXBean объявляется точно так же, как интерфейс стандартного MBean. Интерфейс `QueueSamplerMXBean` объявляет геттер `getQueueSample` и операцию `clearQueue`.

### Определение операций MXBean

Операции MXBean объявлены в примере класса [`QueueSampler`](https://docs.oracle.com/javase/tutorial/jmx/examples/QueueSampler.java) следующим образом:

```java
package com.example;

import java.util.Date;
import java.util.Queue;

public class QueueSampler
                implements QueueSamplerMXBean {

    private Queue<String> queue;

    public QueueSampler (Queue<String> queue) {
        this.queue = queue;
    }

    public QueueSample getQueueSample() {
        synchronized (queue) {
            return new QueueSample(new Date(),
                           queue.size(), queue.peek());
        }
    }

    public void clearQueue() {
        synchronized (queue) {
            queue.clear();
        }
    }
}
```

`QueueSampler` определяет геттер `getQueueSample()` и операцию `clearQueue()`, которые были объявлены интерфейсом MXBean. Операция `getQueueSample()` возвращает экземпляр Java-типа `QueueSample`, который создаётся со значениями, возвращёнными методами `peek()` и `size()` класса [`java.util.Queue`](https://docs.oracle.com/javase/8/docs/api/java/util/Queue.html), и экземпляром [`java.util.Date`](https://docs.oracle.com/javase/8/docs/api/java/util/Date.html).

### Определение Java-типа, возвращаемого интерфейсом MXBean

Экземпляр `QueueSample`, возвращаемый `QueueSampler`, определён в классе [`QueueSample`](https://docs.oracle.com/javase/tutorial/jmx/examples/QueueSample.java) следующим образом:

```java
package com.example;

import java.beans.ConstructorProperties;
import java.util.Date;

public class QueueSample {

    private final Date date;
    private final int size;
    private final String head;

    @ConstructorProperties({"date", "size", "head"})
    public QueueSample(Date date, int size,
                        String head) {
        this.date = date;
        this.size = size;
        this.head = head;
    }

    public Date getDate() {
        return date;
    }

    public int getSize() {
        return size;
    }

    public String getHead() {
        return head;
    }
}
```

В классе `QueueSample` каркас MXBean (*MXBean framework*) вызывает все геттеры в `QueueSample`, чтобы преобразовать данный экземпляр в экземпляр [`CompositeData`](https://docs.oracle.com/javase/8/docs/api/javax/management/openmbean/CompositeData.html), и использует аннотацию `@ConstructorProperties`, чтобы восстановить экземпляр `QueueSample` из экземпляра `CompositeData`.

### Создание и регистрация MXBean в сервере MBean

К этому моменту определено следующее: интерфейс MXBean и реализующий его класс, а также возвращаемый Java-тип. Далее MXBean необходимо создать и зарегистрировать в сервере MBean. Эти действия выполняются тем же примером агента JMX [`Main`](https://docs.oracle.com/javase/tutorial/jmx/examples/Main.java), который использовался в примере стандартного MBean, но соответствующий код не был показан в уроке [Стандартный MBean](https://docs.oracle.com/javase/tutorial/jmx/mbeans/standard.html).

```java
package com.example;

import java.lang.management.ManagementFactory;
import java.util.Queue;
import java.util.concurrent.ArrayBlockingQueue;
import javax.management.MBeanServer;
import javax.management.ObjectName;

public class Main {

    public static void main(String[] args) throws Exception {
        MBeanServer mbs =
            ManagementFactory.getPlatformMBeanServer();

        ...
        ObjectName mxbeanName = new ObjectName("com.example:type=QueueSampler");

        Queue<String> queue = new ArrayBlockingQueue<String>(10);
        queue.add("Request-1");
        queue.add("Request-2");
        queue.add("Request-3");
        QueueSampler mxbean = new QueueSampler(queue);

        mbs.registerMBean(mxbean, mxbeanName);

        System.out.println("Waiting...");
        Thread.sleep(Long.MAX_VALUE);
    }
}
```

Класс `Main` выполняет следующие действия:

- получает платформенный сервер MBean;
- создаёт имя объекта для MXBean `QueueSampler`;
- создаёт экземпляр `Queue`, который будет обрабатывать MXBean `QueueSampler`;
- передаёт экземпляр `Queue` только что созданному MXBean `QueueSampler`;
- регистрирует MXBean в сервере MBean точно так же, как стандартный MBean.

### Запуск примера MXBean

Пример MXBean использует классы из комплекта [`jmx_examples.zip`](https://docs.oracle.com/javase/tutorial/jmx/examples/jmx_examples.zip), который вы использовали в разделе [Стандартные MBean](https://docs.oracle.com/javase/tutorial/jmx/mbeans/standard.html). Этот пример требует версии 6 платформы Java SE. Чтобы запустить пример MXBeans, выполните следующие шаги:

1. Если вы ещё этого не сделали, сохраните [`jmx_examples.zip`](https://docs.oracle.com/javase/tutorial/jmx/examples/jmx_examples.zip) в каталог `work_dir`.
2. Распакуйте комплект примеров классов следующей командой в окне терминала:

   ```
   unzip jmx_examples.zip
   ```

3. Скомпилируйте Java-классы примера из каталога `work_dir`:

   ```
   javac com/example/*.java
   ```

4. Запустите приложение `Main`. Генерируется подтверждение того, что `Main` ожидает наступления какого-либо события.

   ```
   java com.example.Main
   ```

5. Запустите JConsole в другом окне терминала на той же машине. Отображается диалоговое окно New Connection (Новое подключение) со списком запущенных агентов JMX, к которым можно подключиться.

   ```
   jconsole
   ```

6. В диалоговом окне New Connection выберите из списка `com.example.Main` и нажмите Connect (Подключить).

   Отображается сводка текущей активности вашей платформы.

7. Перейдите на вкладку MBeans.

   На этой панели показаны все MBean, зарегистрированные в данный момент в сервере MBean.

8. В левом фрейме разверните узел `com.example` в дереве MBean.

   Вы увидите пример MBean `QueueSampler`, созданный и зарегистрированный классом `Main`. Если щёлкнуть `QueueSampler`, отобразятся связанные с ним узлы Attributes (Атрибуты) и Operations (Операции) в дереве MBean.

9. Разверните узел Attributes.

   В правой панели появится атрибут `QueueSample` со значением `javax.management.openmbean.CompositeDataSupport`.

10. Дважды щёлкните значение `CompositeDataSupport`.

    Вы увидите значения `QueueSample` — `date`, `head` и `size`, — потому что каркас MXBean преобразовал экземпляр `QueueSample` в `CompositeData`. Если бы вы определили `QueueSampler` как стандартный MBean, а не как MXBean, JConsole не нашла бы класс `QueueSample`, поскольку его не было бы в её пути к классам (*class path*). Если бы `QueueSampler` был стандартным MBean, при получении значения атрибута `QueueSample` вы получили бы сообщение `ClassNotFoundException`. То, что JConsole находит `QueueSampler`, демонстрирует полезность использования MXBean при подключении к агентам JMX через универсальные JMX-клиенты, такие как JConsole.

11. Разверните узел Operations.

    Отображается кнопка для вызова операции `clearQueue`.

12. Нажмите кнопку `clearQueue`.

    Отображается подтверждение того, что метод был вызван успешно.

13. Снова разверните узел Attributes и дважды щёлкните значение `CompositeDataSupport`.

    Значения `head` и `size` были сброшены.

14. Чтобы закрыть JConsole, выберите Connection -> Exit (Подключение -> Выход).

## Источник

- [Lesson: Introducing MBeans](https://docs.oracle.com/javase/tutorial/jmx/mbeans/index.html) — официальное руководство Oracle.
- [Standard MBeans](https://docs.oracle.com/javase/tutorial/jmx/mbeans/standard.html) — официальное руководство Oracle.
- [MXBeans](https://docs.oracle.com/javase/tutorial/jmx/mbeans/mxbeans.html) — официальное руководство Oracle.
