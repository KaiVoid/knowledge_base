# Урок 4. Удалённое управление

**Трейл:** JMX · **Оригинал:** [Remote Management](https://docs.oracle.com/javase/tutorial/jmx/remote/index.html)
**Связанные области:** [[22-containers-devops]] · **Вопросы:** containers-devops

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> *Lesson: Remote Management*, *Exposing a Resource for Remote Management By JConsole* и
> *Creating a Custom JMX Client*.

API JMX позволяет выполнять удалённое управление (remote management) вашими ресурсами с помощью
коннекторов на базе технологии JMX (JMX-коннекторов, *JMX connectors*). JMX-коннектор делает сервер
MBean (MBean server) доступным для удалённых клиентов на базе технологии Java. Клиентский конец
коннектора экспортирует, по сути, тот же интерфейс, что и сервер MBean.

JMX-коннектор состоит из клиента коннектора (connector client) и сервера коннектора (connector
server). **Сервер коннектора** присоединён к серверу MBean и слушает запросы на подключение от
клиентов. **Клиент коннектора** отвечает за установление соединения с сервером коннектора. Клиент
коннектора обычно находится в другой виртуальной машине Java (Java VM), нежели сервер коннектора, и
часто работает на другой машине. API JMX определяет стандартный протокол соединения на основе
удалённого вызова методов (Remote Method Invocation, RMI). Этот протокол позволяет подключить
JMX-клиент к MBean на сервере MBean из удалённого расположения и выполнять операции над MBean в
точности так, как если бы эти операции выполнялись локально.

Платформа Java SE предоставляет готовое «из коробки» (out-of-the-box) средство для удалённого
мониторинга приложений с помощью стандартного RMI-коннектора API JMX. Готовый RMI-коннектор
автоматически открывает приложения для удалённого управления, не требуя от вас создавать собственный
выделенный сервер коннектора. Готовый агент удалённого управления активируется запуском Java-приложения
с правильными свойствами (properties). Приложения мониторинга и управления, совместимые с технологией
JMX, могут затем подключаться к таким приложениям и наблюдать за ними удалённо.

## Открытие ресурса для удалённого управления через JConsole

Открыть ваши Java-приложения для удалённого управления с помощью API JMX может быть предельно просто,
если вы используете готовый «из коробки» агент удалённого управления и существующий инструмент
мониторинга и управления, например JConsole.

Чтобы открыть приложение для удалённого управления, нужно запустить его с правильными свойствами. В
этом примере показано, как открыть JMX-агент `Main` для удалённого управления.

> **Замечание о безопасности.** Ради простоты механизмы безопасности — аутентификация и шифрование —
> в этом примере отключены. Однако в реальных окружениях при реализации удалённого управления эти
> механизмы безопасности следует включать. Раздел «Что дальше?» (*What Next?*) даёт указания на другую
> документацию по технологии JMX, где показано, как активировать безопасность.

Этот пример требует версии 6 платформы Java SE. Чтобы наблюдать за JMX-агентом `Main` удалённо,
выполните следующие шаги:

1. Если вы ещё этого не сделали, сохраните `jmx_examples.zip` в каталог `work_dir`.

2. Распакуйте набор примеров классов с помощью следующей команды в окне терминала:

   ```
   unzip jmx_examples.zip
   ```

3. Скомпилируйте примеры Java-классов из каталога `work_dir`:

   ```
   javac com/example/*.java
   ```

4. Запустите приложение `Main`, указав свойства, которые открывают `Main` для удалённого управления.
   (В Windows используйте знак вставки (`^`) вместо обратной косой черты (`\`), чтобы разбить длинную
   команду на несколько строк):

   ```
   java -Dcom.sun.management.jmxremote.port=9999 \
        -Dcom.sun.management.jmxremote.authenticate=false \
        -Dcom.sun.management.jmxremote.ssl=false \
        com.example.Main
   ```

   Появляется подтверждение того, что `Main` ожидает наступления какого-либо события.

5. Запустите JConsole в другом окне терминала на **другой машине**:

   ```
   jconsole
   ```

   Отображается диалоговое окно New Connection («Новое соединение») со списком работающих JMX-агентов,
   к которым можно подключиться локально.

6. Выберите Remote Process («Удалённый процесс») и введите в поле Remote Process следующее:

   ```
   hostname:9999
   ```

   В этом адресе `hostname` — имя удалённой машины, на которой работает приложение `Main`, а 9999 —
   номер порта, на котором будет подключён готовый JMX-коннектор.

7. Нажмите Connect («Подключиться»).

   Отображается сводка текущей активности виртуальной машины Java (Java VM), в которой работает `Main`.

8. Перейдите на вкладку MBeans.

   На этой панели показаны все MBean, которые сейчас зарегистрированы на удалённом сервере MBean.

9. В левой панели разверните узел `com.example` в дереве MBean.

   Вы увидите пример MBean `Hello`, который был создан и зарегистрирован приложением `Main`. Если
   щёлкнуть по `Hello`, в дереве MBean появятся связанные с ним узлы Attributes («Атрибуты») и
   Operations («Операции»), несмотря на то что MBean работает на другой машине.

10. Чтобы закрыть JConsole, выберите Connection -> Exit («Соединение -> Выход»).

## Создание собственного JMX-клиента

Предыдущие уроки этого трейла показали, как создавать MBean и MXBean на базе технологии JMX и
регистрировать их в JMX-агенте. Однако во всех предыдущих примерах использовался существующий
JMX-клиент — JConsole. Этот урок продемонстрирует, как создать собственный JMX-клиент.

Пример собственного JMX-клиента — [`Client`](https://docs.oracle.com/javase/tutorial/jmx/examples/Client.java) — включён в
[`jmx_examples.zip`](https://docs.oracle.com/javase/tutorial/jmx/examples/jmx_examples.zip). Этот JMX-клиент взаимодействует с тем же
MBean, MXBean и JMX-агентом, что рассматривались в предыдущих уроках. Из-за размера класса `Client`
он будет разобран по частям в следующих разделах.

### Импорт классов JMX Remote API

Чтобы иметь возможность создавать соединения с JMX-агентами, работающими удалённо от JMX-клиента,
нужно использовать классы из пакета [`javax.management.remote`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/package-summary.html).

```java
package com.example;
...

import javax.management.remote.JMXConnector;
import javax.management.remote.JMXConnectorFactory;
import javax.management.remote.JMXServiceURL;

public class Client {
...
```

Класс `Client` будет создавать экземпляры [`JMXConnector`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXConnector.html),
для чего ему понадобятся [`JMXConnectorFactory`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXConnectorFactory.html)
и [`JMXServiceURL`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXServiceURL.html).

### Создание слушателя уведомлений

JMX-клиенту нужен обработчик уведомлений (notification handler), чтобы слушать и обрабатывать любые
уведомления, которые могут отправлять MBean, зарегистрированные на сервере MBean JMX-агента.
Обработчик уведомлений JMX-клиента — это экземпляр интерфейса
[`NotificationListener`](https://docs.oracle.com/javase/8/docs/api/javax/management/NotificationListener.html),
как показано ниже.

```java
...

public static class ClientListener implements NotificationListener {

    public void handleNotification(Notification notification,
            Object handback) {
        echo("\nПолучено уведомление:");
        echo("\tClassName: " + notification.getClass().getName());
        echo("\tSource: " + notification.getSource());
        echo("\tType: " + notification.getType());
        echo("\tMessage: " + notification.getMessage());
        if (notification instanceof AttributeChangeNotification) {
            AttributeChangeNotification acn =
                (AttributeChangeNotification) notification;
            echo("\tAttributeName: " + acn.getAttributeName());
            echo("\tAttributeType: " + acn.getAttributeType());
            echo("\tNewValue: " + acn.getNewValue());
            echo("\tOldValue: " + acn.getOldValue());
        }
    }
}
...
```

Этот слушатель уведомлений определяет источник любого полученного им уведомления и извлекает
информацию, сохранённую в уведомлении. Затем он выполняет различные действия с информацией из
уведомления в зависимости от типа полученного уведомления. В данном случае, получив уведомления типа
[`AttributeChangeNotification`](https://docs.oracle.com/javase/8/docs/api/javax/management/AttributeChangeNotification.html),
он получит имя и тип изменившегося атрибута MBean, а также его старое и новое значения, вызвав методы
`getAttributeName`, `getAttributeType`, `getNewValue` и `getOldValue` класса `AttributeChangeNotification`.

Новый экземпляр `ClientListener` создаётся далее в коде.

```java
ClientListener listener = new ClientListener();
```

### Создание клиента RMI-коннектора

Класс `Client` создаёт клиент RMI-коннектора, настроенный на подключение к серверу RMI-коннектора,
который вы запустите при старте JMX-агента `Main`. Это позволит JMX-клиенту взаимодействовать с
JMX-агентом так, как если бы они работали на одной машине.

```java
...

public static void main(String[] args) throws Exception {

echo("\nСоздать клиент RMI-коннектора и " +
    "подключить его к серверу RMI-коннектора");
JMXServiceURL url =
    new JMXServiceURL("service:jmx:rmi:///jndi/rmi://:9999/jmxrmi");
JMXConnector jmxc = JMXConnectorFactory.connect(url, null);
...
```

Как видите, `Client` определяет
[`JMXServiceURL`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXServiceURL.html)
с именем `url`, представляющий местоположение, в котором клиент коннектора ожидает найти сервер
коннектора. Этот URL позволяет клиенту коннектора получить заглушку (stub) сервера RMI-коннектора
`jmxrmi` из реестра RMI (RMI registry), работающего на порту 9999 локального хоста, и подключиться к
серверу RMI-коннектора.

После того как реестр RMI таким образом определён, можно создать клиент коннектора. Клиент коннектора
`jmxc` — это экземпляр интерфейса
[`JMXConnector`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXConnector.html),
создаваемый методом `connect()` класса
[`JMXConnectorFactory`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXConnectorFactory.html).
Методу `connect()` при вызове передаются параметры `url` и пустая (null) карта окружения
(environment map).

### Подключение к удалённому серверу MBean

Когда RMI-соединение установлено, JMX-клиент должен подключиться к удалённому серверу MBean, чтобы
иметь возможность взаимодействовать с различными MBean, зарегистрированными в нём удалённым
JMX-агентом.

```java
...

MBeanServerConnection mbsc =
    jmxc.getMBeanServerConnection();

...
```

Затем создаётся экземпляр
[`MBeanServerConnection`](https://docs.oracle.com/javase/8/docs/api/javax/management/MBeanServerConnection.html)
с именем `mbsc` — вызовом метода `getMBeanServerConnection()` экземпляра `JMXConnector` `jmxc`.

Теперь клиент коннектора подключён к серверу MBean, созданному JMX-агентом, и может регистрировать
MBean и выполнять над ними операции, при этом соединение остаётся полностью прозрачным для обоих
концов.

Для начала клиент определяет несколько простых операций, чтобы получить сведения о MBean, найденных на
сервере MBean агента.

```java
...

echo("\nДомены:");
String domains[] = mbsc.getDomains();
Arrays.sort(domains);
for (String domain : domains) {
    echo("\tDomain = " + domain);
}

...

echo("\nДомен по умолчанию сервера MBean = " + mbsc.getDefaultDomain());

echo("\nКоличество MBean = " +  mbsc.getMBeanCount());
echo("\nЗапрос MBean у сервера MBean:");
Set<ObjectName> names =
    new TreeSet<ObjectName>(mbsc.queryNames(null, null));
for (ObjectName name : names) {
    echo("\tObjectName = " + name);
}

...
```

Клиент вызывает различные методы `MBeanServerConnection`, чтобы получить домены, в которых работают
разные MBean, количество MBean, зарегистрированных на сервере MBean, и имена объектов (object names)
каждого из обнаруженных им MBean.

### Выполнение операций над удалёнными MBean через прокси

Клиент обращается к MBean `Hello` на сервере MBean через соединение с сервером MBean, создавая
**прокси** (*proxy*) для MBean. Этот прокси MBean является локальным для клиента и эмулирует удалённый
MBean.

```java
...

ObjectName mbeanName = new ObjectName("com.example:type=Hello");
HelloMBean mbeanProxy = JMX.newMBeanProxy(mbsc, mbeanName,
                                          HelloMBean.class, true);

echo("\nДобавить слушатель уведомлений...");
mbsc.addNotificationListener(mbeanName, listener, null, null);

echo("\nCacheSize = " + mbeanProxy.getCacheSize());

mbeanProxy.setCacheSize(150);

echo("\nОжидание уведомления...");
sleep(2000);
echo("\nCacheSize = " + mbeanProxy.getCacheSize());
echo("\nВызвать sayHello() в MBean Hello...");
mbeanProxy.sayHello();

echo("\nВызвать add(2, 3) в MBean Hello...");
echo("\nadd(2, 3) = " + mbeanProxy.add(2, 3));

waitForEnterPressed();

...
```

Прокси MBean позволяют обращаться к MBean через Java-интерфейс, давая возможность делать вызовы на
прокси вместо написания объёмного кода для обращения к удалённому MBean. Прокси MBean для `Hello`
создаётся здесь вызовом метода `newMBeanProxy()` класса
[`javax.management.JMX`](https://docs.oracle.com/javase/8/docs/api/javax/management/JMX.html), которому
передаются `MBeanServerConnection` этого MBean, имя объекта, имя класса интерфейса MBean и `true` —
чтобы обозначить, что прокси должен вести себя как
[`NotificationBroadcaster`](https://docs.oracle.com/javase/8/docs/api/javax/management/NotificationBroadcaster.html).
Теперь JMX-клиент может выполнять операции, определённые в `Hello`, как если бы это были операции
локально зарегистрированного MBean. JMX-клиент также добавляет слушатель уведомлений и изменяет
атрибут `CacheSize` этого MBean, чтобы заставить его отправить уведомление.

### Выполнение операций над удалёнными MXBean через прокси

Прокси для MXBean можно создавать точно так же, как и прокси для MBean.

```java
...

ObjectName mxbeanName = new ObjectName ("com.example:type=QueueSampler");
QueueSamplerMXBean mxbeanProxy = JMX.newMXBeanProxy(mbsc,
    mxbeanName,  QueueSamplerMXBean.class);
QueueSample queue1 = mxbeanProxy.getQueueSample();
echo("\nQueueSample.Date = " + queue1.getDate());
echo("QueueSample.Head = " + queue1.getHead());
echo("QueueSample.Size = " + queue1.getSize());
echo("\nВызвать clearQueue() в MXBean QueueSampler...");
mxbeanProxy.clearQueue();

QueueSample queue2 = mxbeanProxy.getQueueSample();
echo("\nQueueSample.Date = " +  queue2.getDate());
echo("QueueSample.Head = " + queue2.getHead());
echo("QueueSample.Size = " + queue2.getSize());

...
```

Как показано выше, чтобы создать прокси для MXBean, всё, что нужно сделать, — это вызвать
[`JMX.newMXBeanProxy`](https://docs.oracle.com/javase/8/docs/api/javax/management/JMX.html#newMXBeanProxy-javax.management.MBeanServerConnection-javax.management.ObjectName-java.lang.Class-)
вместо `newMBeanProxy`. Прокси MXBean `mxbeanProxy` позволяет клиенту вызывать операции MXBean
`QueueSample` так, как если бы это были операции локально зарегистрированного MXBean.

### Закрытие соединения

Как только JMX-клиент получил всю нужную ему информацию и выполнил все требуемые операции над MBean на
сервере MBean удалённого JMX-агента, соединение нужно закрыть.

```java
jmxc.close();
```

Соединение закрывается вызовом метода
[`JMXConnector.close`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/JMXConnector.html#close--).

### Запуск примера собственного JMX-клиента

Этот пример требует версии 6 платформы Java SE. Чтобы наблюдать за JMX-агентом `Main` удалённо с
помощью собственного JMX-клиента [`Client`](https://docs.oracle.com/javase/tutorial/jmx/examples/Client.java),
выполните следующие шаги:

1. Если вы ещё этого не сделали, сохраните
   [`jmx_examples.zip`](https://docs.oracle.com/javase/tutorial/jmx/examples/jmx_examples.zip) в каталог `work_dir`.

2. Распакуйте набор примеров классов с помощью следующей команды в окне терминала:

   ```
   unzip jmx_examples.zip
   ```

3. Скомпилируйте примеры Java-классов из каталога `work_dir`:

   ```
   javac com/example/*.java
   ```

4. Запустите приложение `Main`, указав свойства, которые открывают `Main` для удалённого управления:

   ```
   java -Dcom.sun.management.jmxremote.port=9999 \
        -Dcom.sun.management.jmxremote.authenticate=false \
        -Dcom.sun.management.jmxremote.ssl=false \
        com.example.Main
   ```

   Появляется подтверждение того, что `Main` ожидает наступления какого-либо события.

5. Запустите приложение `Client` в другом окне терминала:

   ```
   java com.example.Client
   ```

   Отображается подтверждение того, что получено соединение `MBeanServerConnection`.

6. Нажмите Enter.

   Отображаются домены, в которых работают все MBean, зарегистрированные на сервере MBean, запущенном
   приложением `Main`.

7. Нажмите Enter ещё раз.

   Отображается количество MBean, зарегистрированных на сервере MBean, а также имена объектов всех этих
   MBean. Среди показанных MBean — все стандартные платформенные MXBean, работающие в Java VM, а также
   MBean `Hello` и MXBean `QueueSampler`, зарегистрированные на сервере MBean приложением `Main`.

8. Нажмите Enter ещё раз.

   `Client` вызывает операции MBean `Hello` со следующими результатами:

   - К `Client` добавляется слушатель уведомлений для прослушивания уведомлений от `Main`.
   - Значение атрибута `CacheSize` изменяется с 200 на 150.
   - В окне терминала, где вы запустили `Main`, отображается подтверждение изменения атрибута `CacheSize`.
   - В окне терминала, где вы запустили `Client`, отображается уведомление от `Main`, информирующее
     `Client` об изменении атрибута `CacheSize`.
   - Вызывается операция `sayHello` MBean `Hello`.
   - В окне терминала, где вы запустили `Main`, отображается сообщение «Hello world».
   - Вызывается операция `add` MBean `Hello` со значениями 2 и 3 в качестве параметров. Результат
     отображается приложением `Client`.

9. Нажмите Enter ещё раз.

   `Client` вызывает операции MXBean `QueueSampler` со следующими результатами:

   - Отображаются значения `date`, `head` и `size` объекта `QueueSample`.
   - Вызывается операция `clearQueue`.

10. Нажмите Enter ещё раз.

    `Client` закрывает соединение с сервером MBean, и отображается подтверждение.

## Источник

- [Lesson: Remote Management](https://docs.oracle.com/javase/tutorial/jmx/remote/index.html) — официальное руководство Oracle.
- [Exposing a Resource for Remote Management By JConsole](https://docs.oracle.com/javase/tutorial/jmx/remote/jconsole.html)
- [Creating a Custom JMX Client](https://docs.oracle.com/javase/tutorial/jmx/remote/custom.html)
