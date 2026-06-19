# Урок 5. Программный доступ к сетевым параметрам

**Трейл:** Custom Networking · **Оригинал:** [Programmatic Access to Network Parameters](https://docs.oracle.com/javase/tutorial/networking/nifs/index.html)
**Связанные области:** [[17-rest-web]] · **Вопросы:** rest-web

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

Системы часто работают с несколькими активными сетевыми подключениями, например проводным
Ethernet, `802.11 b/g` (беспроводным) и Bluetooth. Некоторым приложениям может потребоваться
доступ к этой информации, чтобы выполнить конкретную сетевую операцию через определённое
подключение.

Доступ к этой информации предоставляет класс
[`java.net.NetworkInterface`](https://docs.oracle.com/javase/8/docs/api/java/net/NetworkInterface.html).

Этот урок познакомит вас с некоторыми наиболее распространёнными способами применения данного
класса и приведёт примеры, которые перечисляют все сетевые интерфейсы (network interfaces) на
машине, а также их IP-адреса и состояние.

## Что такое сетевой интерфейс?

**Сетевой интерфейс** (*network interface*) — это точка соединения между компьютером и частной
или публичной сетью. Сетевой интерфейс обычно представляет собой сетевую карту
(*network interface card*, NIC), но не обязан иметь физическую форму. Вместо этого сетевой
интерфейс может быть реализован программно. Например, интерфейс обратной петли (loopback) —
`127.0.0.1` для IPv4 и `::1` для IPv6 — это не физическое устройство, а часть программного
обеспечения, моделирующая сетевой интерфейс. Loopback-интерфейс обычно используется в тестовых
средах.

Класс
[`java.net.NetworkInterface`](https://docs.oracle.com/javase/8/docs/api/java/net/NetworkInterface.html)
представляет оба типа интерфейсов.

`NetworkInterface` полезен для **многоинтерфейсной системы** (*multi-homed system*) — системы с
несколькими сетевыми картами (NIC). С помощью `NetworkInterface` можно указать, какую сетевую
карту использовать для конкретной сетевой операции.

Например, предположим, что у вас есть машина с двумя настроенными NIC и вы хотите отправить данные
на сервер. Вы создаёте сокет так:

```java
Socket soc = new java.net.Socket();
soc.connect(new InetSocketAddress(address, port));
```

Чтобы отправить данные, система сама определяет, какой интерфейс использовать. Однако если у вас
есть предпочтение или по иной причине нужно указать конкретную сетевую карту, вы можете запросить
у системы подходящие интерфейсы и найти адрес на том интерфейсе, который хотите использовать. Когда
вы создаёте сокет и привязываете его к этому адресу, система использует связанный с ним интерфейс.
Например:

```java
NetworkInterface nif = NetworkInterface.getByName("bge0");
Enumeration<InetAddress> nifAddresses = nif.getInetAddresses();

Socket soc = new java.net.Socket();
soc.bind(new InetSocketAddress(nifAddresses.nextElement(), 0));
soc.connect(new InetSocketAddress(address, port));
```

Также `NetworkInterface` можно использовать, чтобы указать локальный интерфейс, на котором следует
присоединиться к группе многоадресной рассылки (multicast). Например:

```java
NetworkInterface nif = NetworkInterface.getByName("bge0");
MulticastSocket ms = new MulticastSocket();
ms.joinGroup(new InetSocketAddress(hostname, port), nif);
```

`NetworkInterface` можно использовать с Java API множеством других способов помимо двух описанных
здесь.

## Получение сетевых интерфейсов

У класса `NetworkInterface` нет публичного конструктора. Поэтому нельзя просто создать новый
экземпляр этого класса оператором `new`. Вместо этого доступны следующие статические методы,
позволяющие получить сведения об интерфейсах из системы: `getByInetAddress()`, `getByName()` и
`getNetworkInterfaces()`. Первые два метода используются, когда вы уже знаете IP-адрес или имя
конкретного интерфейса. Третий метод, `getNetworkInterfaces()`, возвращает полный список
интерфейсов на машине.

Сетевые интерфейсы могут быть организованы иерархически. Класс `NetworkInterface` включает два
метода, `getParent()` и `getSubInterfaces()`, относящихся к иерархии сетевых интерфейсов. Метод
`getParent()` возвращает родительский `NetworkInterface` интерфейса. Если сетевой интерфейс
является подынтерфейсом (subinterface), `getParent()` возвращает ненулевое значение. Метод
`getSubInterfaces()` возвращает все подынтерфейсы данного сетевого интерфейса.

Следующая программа-пример перечисляет имена всех сетевых интерфейсов и подынтерфейсов (если они
существуют) на машине.

```java
import java.io.*;
import java.net.*;
import java.util.*;
import static java.lang.System.out;

public class ListNIFs 
{
    public static void main(String args[]) throws SocketException {
        Enumeration<NetworkInterface> nets = NetworkInterface.getNetworkInterfaces();
        
        for (NetworkInterface netIf : Collections.list(nets)) {
            out.printf("Display name: %s\n", netIf.getDisplayName());
            out.printf("Name: %s\n", netIf.getName());
            displaySubInterfaces(netIf);
            out.printf("\n");
        }
    }

    static void displaySubInterfaces(NetworkInterface netIf) throws SocketException {
        Enumeration<NetworkInterface> subIfs = netIf.getSubInterfaces();
        
        for (NetworkInterface subIf : Collections.list(subIfs)) {
            out.printf("\tSub Interface Display name: %s\n", subIf.getDisplayName());
            out.printf("\tSub Interface Name: %s\n", subIf.getName());
        }
     }
}  
```

Ниже приведён пример вывода этой программы:

```
Display name: bge0
Name: bge0
    Sub Interface Display name: bge0:3
    Sub Interface Name: bge0:3
    Sub Interface Display name: bge0:2
    Sub Interface Name: bge0:2
    Sub Interface Display name: bge0:1
    Sub Interface Name: bge0:1

Display name: lo0
Name: lo0
```

## Перечисление адресов сетевого интерфейса

Одна из самых полезных сведений, которые можно получить от сетевого интерфейса, — это список
IP-адресов, назначенных ему. Эту информацию можно получить от экземпляра `NetworkInterface` одним
из двух методов. Первый метод, `getInetAddresses()`, возвращает перечисление (`Enumeration`)
объектов `InetAddress`. Другой метод, `getInterfaceAddresses()`, возвращает список экземпляров
[`java.net.InterfaceAddress`](https://docs.oracle.com/javase/8/docs/api/java/net/InterfaceAddress.html).
Этот метод используется, когда нужно больше информации об адресе интерфейса, чем только его
IP-адрес. Например, вам может понадобиться дополнительная информация о маске подсети (subnet mask)
и широковещательном адресе (broadcast address), когда адрес является адресом IPv4, или о длине
сетевого префикса (network prefix length) в случае адреса IPv6.

Следующая программа-пример перечисляет все сетевые интерфейсы и их адреса на машине:

```java
import java.io.*;
import java.net.*;
import java.util.*;
import static java.lang.System.out;

public class ListNets {

    public static void main(String args[]) throws SocketException {
        Enumeration<NetworkInterface> nets = NetworkInterface.getNetworkInterfaces();
        for (NetworkInterface netint : Collections.list(nets))
            displayInterfaceInformation(netint);
    }

    static void displayInterfaceInformation(NetworkInterface netint) throws SocketException {
        out.printf("Display name: %s\n", netint.getDisplayName());
        out.printf("Name: %s\n", netint.getName());
        Enumeration<InetAddress> inetAddresses = netint.getInetAddresses();
        for (InetAddress inetAddress : Collections.list(inetAddresses)) {
            out.printf("InetAddress: %s\n", inetAddress);
        }
        out.printf("\n");
     }
}
```

Пример вывода:

```
Display name: TCP Loopback interface
Name: lo
InetAddress: /127.0.0.1

Display name: Wireless Network Connection
Name: eth0
InetAddress: /192.0.2.0
```

## Параметры сетевого интерфейса

Помимо имени и назначенных IP-адресов, у сетевого интерфейса можно получить и другие сетевые
параметры.

Узнать, «поднят» ли сетевой интерфейс (то есть работает ли он), можно методом `isUp()`. Следующие
методы указывают тип сетевого интерфейса:

- `isLoopback()` — указывает, является ли сетевой интерфейс интерфейсом обратной петли (loopback).
- `isPointToPoint()` — указывает, является ли интерфейс двухточечным (point-to-point).
- `isVirtual()` — указывает, является ли интерфейс виртуальным (virtual).

Метод `supportsMulticast()` указывает, поддерживает ли сетевой интерфейс многоадресную рассылку
(multicasting). Метод `getHardwareAddress()` возвращает физический аппаратный адрес сетевого
интерфейса, обычно называемый MAC-адресом, когда он доступен. Метод `getMTU()` возвращает
максимальный размер передаваемого блока данных (*Maximum Transmission Unit*, MTU) — наибольший
размер пакета.

Следующий пример расширяет пример из раздела «Перечисление адресов сетевого интерфейса», добавляя
дополнительные сетевые параметры, описанные на этой странице:

```java
import java.io.*;
import java.net.*;
import java.util.*;
import static java.lang.System.out;

public class ListNetsEx {

    public static void main(String args[]) throws SocketException {
        Enumeration<NetworkInterface> nets = NetworkInterface.getNetworkInterfaces();
        for (NetworkInterface netint : Collections.list(nets))
            displayInterfaceInformation(netint);
    }

    static void displayInterfaceInformation(NetworkInterface netint) throws SocketException {
        out.printf("Display name: %s\n", netint.getDisplayName());
        out.printf("Name: %s\n", netint.getName());
        Enumeration<InetAddress> inetAddresses = netint.getInetAddresses();
        
        for (InetAddress inetAddress : Collections.list(inetAddresses)) {
            out.printf("InetAddress: %s\n", inetAddress);
        }
       
        out.printf("Up? %s\n", netint.isUp());
        out.printf("Loopback? %s\n", netint.isLoopback());
        out.printf("PointToPoint? %s\n", netint.isPointToPoint());
        out.printf("Supports multicast? %s\n", netint.supportsMulticast());
        out.printf("Virtual? %s\n", netint.isVirtual());
        out.printf("Hardware address: %s\n",
                    Arrays.toString(netint.getHardwareAddress()));
        out.printf("MTU: %s\n", netint.getMTU());
        out.printf("\n");
     }
}
```

Ниже приведён пример вывода этой программы:

```
Display name: bge0
Name: bge0
InetAddress: /fe80:0:0:0:203:baff:fef2:e99d%2
InetAddress: /129.156.225.59
Up? true
Loopback? false
PointToPoint? false
Supports multicast? false
Virtual? false
Hardware address: [0, 3, 4, 5, 6, 7]
MTU: 1500

Display name: lo0
Name: lo0
InetAddress: /0:0:0:0:0:0:0:1%1
InetAddress: /127.0.0.1
Up? true
Loopback? true
PointToPoint? false
Supports multicast? false
Virtual? false
Hardware address: null
MTU: 8232
```

## Источник

- [Programmatic Access to Network Parameters](https://docs.oracle.com/javase/tutorial/networking/nifs/index.html) — официальное руководство Oracle (обзор урока).
- [What Is a Network Interface?](https://docs.oracle.com/javase/tutorial/networking/nifs/definition.html) — официальное руководство Oracle.
- [Retrieving Network Interfaces](https://docs.oracle.com/javase/tutorial/networking/nifs/retrieving.html) — официальное руководство Oracle.
- [Listing Network Interface Addresses](https://docs.oracle.com/javase/tutorial/networking/nifs/listing.html) — официальное руководство Oracle.
- [Network Interface Parameters](https://docs.oracle.com/javase/tutorial/networking/nifs/parameters.html) — официальное руководство Oracle.
