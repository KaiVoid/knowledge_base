# Урок 3. Уведомления JMX

**Трейл:** JMX · **Оригинал:** [Notifications](https://docs.oracle.com/javase/tutorial/jmx/notifs/index.html)
**Связанные области:** [[22-containers-devops]] · **Вопросы:** containers-devops

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8), страница *Lesson: Notifications* трейла Java Management Extensions (JMX).
>
> *Примечание Oracle: руководство написано для JDK 8. Примеры и приёмы, описанные здесь, не учитывают улучшений, появившихся в более поздних выпусках, и могут использовать технологии, которые больше недоступны. Актуальные руководства — на [Dev.java](https://dev.java/learn/).*

API JMX определяет механизм, позволяющий компонентам-управляемым бинам (MBeans) генерировать **уведомления** (*notifications*) — например, чтобы сообщить об изменении состояния, об обнаруженном событии или о проблеме.

## Механизм уведомлений

Чтобы генерировать уведомления, управляемый бин (MBean) должен реализовать интерфейс [`NotificationEmitter`](https://docs.oracle.com/javase/8/docs/api/javax/management/NotificationEmitter.html) (источник уведомлений) или расширить класс [`NotificationBroadcasterSupport`](https://docs.oracle.com/javase/8/docs/api/javax/management/NotificationBroadcasterSupport.html) (вещатель уведомлений). Чтобы отправить уведомление, нужно создать экземпляр класса [`javax.management.Notification`](https://docs.oracle.com/javase/8/docs/api/javax/management/Notification.html) или его подкласса (например, [`AttributeChangeNotification`](https://docs.oracle.com/javase/8/docs/api/javax/management/AttributeChangeNotification.html) — уведомление об изменении атрибута) и передать этот экземпляр в метод [`NotificationBroadcasterSupport.sendNotification`](https://docs.oracle.com/javase/8/docs/api/javax/management/NotificationBroadcasterSupport.html#sendNotification-javax.management.Notification).

У каждого уведомления есть **источник** (*source*). Источник — это объектное имя (object name) управляемого бина, сгенерировавшего уведомление.

У каждого уведомления есть **порядковый номер** (*sequence number*). Этот номер можно использовать для упорядочивания уведомлений, исходящих из одного источника, когда порядок важен и существует риск обработки уведомлений в неверной последовательности. Порядковый номер может быть равен нулю, но предпочтительно, чтобы он увеличивался для каждого уведомления от данного управляемого бина.

### Схема: источник уведомлений → слушатель

<!-- original: none | Авторская схема механизма уведомлений JMX; оригинальная фигура на странице Oracle отсутствует -->
```mermaid
flowchart LR
    MBean["Управляемый бин Hello<br/>(источник уведомлений)<br/>extends NotificationBroadcasterSupport"]
    Notif["Уведомление<br/>(AttributeChangeNotification):<br/>источник · порядковый номер ·<br/>метка времени · сообщение"]
    Server["Сервер управляемых бинов<br/>(MBean server)"]
    Listener["Слушатель уведомлений<br/>(например, JConsole,<br/>подписавшийся клиент)"]

    MBean -->|"sendNotification(n)"| Notif
    Notif --> Server
    Server -->|"доставка подписчикам"| Listener
```

## Полный код управляемого бина Hello

Реализация управляемого бина [`Hello`](https://docs.oracle.com/javase/tutorial/jmx/examples/Hello.java) из урока [Standard MBeans](https://docs.oracle.com/javase/tutorial/jmx/mbeans/standard.html) фактически уже реализует механизм уведомлений. Однако в том уроке этот код был опущен для простоты. Полный код `Hello` приведён ниже.

```java
package com.example;

import javax.management.*;

public class Hello
        extends NotificationBroadcasterSupport
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
        int oldSize = this.cacheSize;
        this.cacheSize = size;

        System.out.println("Cache size now " + this.cacheSize);

        Notification n = new AttributeChangeNotification(this,
                                sequenceNumber++, System.currentTimeMillis(),
                                "CacheSize changed", "CacheSize", "int",
                                oldSize, this.cacheSize);

        sendNotification(n);
    }

    @Override
    public MBeanNotificationInfo[] getNotificationInfo() {
        String[] types = new String[]{
            AttributeChangeNotification.ATTRIBUTE_CHANGE
        };

        String name = AttributeChangeNotification.class.getName();
        String description = "An attribute of this MBean has changed";
        MBeanNotificationInfo info = 
                new MBeanNotificationInfo(types, name, description);
        return new MBeanNotificationInfo[]{info};
    }
    
    private final String name = "Reginald";
    private int cacheSize = DEFAULT_CACHE_SIZE;
    private static final int DEFAULT_CACHE_SIZE = 200;
    private long sequenceNumber = 1;
}
```

Эта реализация управляемого бина `Hello` расширяет класс `NotificationBroadcasterSupport`. Класс `NotificationBroadcasterSupport`, в свою очередь, реализует интерфейс `NotificationEmitter`.

Операции и атрибуты задаются так же, как в примере стандартного управляемого бина, за тем исключением, что метод-сеттер атрибута `CacheSize` теперь определяет значение `oldSize`. Это значение запоминает значение атрибута `CacheSize` до операции присваивания.

Уведомление строится из экземпляра `n` JMX-класса `AttributeChangeNotification`, который расширяет `javax.management.Notification`. Уведомление создаётся внутри определения метода `setCacheSize()` из перечисленной ниже информации. Эта информация передаётся в `AttributeChangeNotification` в качестве параметров:

- объектное имя источника уведомления, а именно управляемого бина `Hello`, представленного ссылкой `this`;
- порядковый номер, а именно `sequenceNumber`, который установлен в 1 и инкрементируется;
- метка времени (*timestamp*);
- содержимое сообщения уведомления;
- имя изменившегося атрибута, в данном случае `CacheSize`;
- тип изменившегося атрибута;
- старое значение атрибута, в данном случае `oldSize`;
- новое значение атрибута, в данном случае `this.cacheSize`.

Затем уведомление `n` передаётся в метод `NotificationBroadcasterSupport.sendNotification()`.

Наконец, экземпляр [`MBeanNotificationInfo`](https://docs.oracle.com/javase/8/docs/api/javax/management/MBeanNotificationInfo.html) определяется для описания характеристик различных экземпляров уведомлений, которые генерирует управляемый бин для данного типа уведомлений. В данном случае отправляемый тип уведомлений — это уведомления `AttributeChangeNotification`.

## Запуск примера с уведомлениями управляемого бина

И снова вы будете использовать JConsole для взаимодействия с управляемым бином `Hello` — на этот раз для отправки и получения уведомлений. Для этого примера требуется версия 6 платформы Java SE.

1. Если вы ещё не сделали этого, сохраните [`jmx_examples.zip`](https://docs.oracle.com/javase/tutorial/jmx/examples/jmx_examples.zip) в свой каталог `work_dir`.

2. Распакуйте набор классов-примеров с помощью следующей команды в окне терминала.

   ```
   unzip jmx_examples.zip
   ```

3. Скомпилируйте классы-примеры Java, находясь в каталоге `work_dir`.

   ```
   javac com/example/*.java
   ```

4. Запустите приложение `Main`.

   ```
   java com.example.Main
   ```

   Появится подтверждение того, что `Main` ожидает наступления некоторого события.

5. Запустите JConsole в другом окне терминала на той же машине.

   ```
   jconsole
   ```

   Отобразится диалоговое окно New Connection (Новое подключение) со списком запущенных JMX-агентов, к которым можно подключиться.

6. В диалоговом окне New Connection выберите из списка `com.example.Main` и нажмите Connect (Подключиться).

   Отобразится сводка текущей активности вашей платформы.

7. Перейдите на вкладку MBeans.

   На этой панели показаны все управляемые бины, которые сейчас зарегистрированы в сервере управляемых бинов (MBean server).

8. В левой части окна разверните узел `com.example` в дереве управляемых бинов.

   Вы увидите управляемый бин-пример `Hello`, который был создан и зарегистрирован классом `Hello`. Если щёлкнуть по `Hello`, в дереве управляемых бинов появится его узел Notifications (Уведомления).

9. Разверните узел Notifications управляемого бина `Hello` в дереве управляемых бинов.

   Обратите внимание, что панель пуста.

10. Нажмите кнопку Subscribe (Подписаться).

    Текущее количество полученных уведомлений (0) отобразится в метке узла Notifications.

11. Разверните узел Attributes (Атрибуты) управляемого бина `Hello` в дереве управляемых бинов и измените значение атрибута `CacheSize` на 150.

    В окне терминала, где вы запустили `Main`, отобразится подтверждение этого изменения атрибута. Обратите внимание, что число полученных уведомлений, показанное в узле Notifications, изменилось на 1.

12. Снова разверните узел Notifications управляемого бина `Hello` в дереве управляемых бинов.

    Отобразятся подробности уведомления.

13. Чтобы закрыть JConsole, выберите Connection -> Exit (Соединение -> Выход).

## Источник

- [Lesson: Notifications](https://docs.oracle.com/javase/tutorial/jmx/notifs/index.html) — официальное руководство Oracle (The Java Tutorials, JDK 8). Урок представлен единой страницей без отдельных подстраниц.
