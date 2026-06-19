# Урок 4. Реализация собственного разрешения

**Трейл:** Security · **Оригинал:** [Implementing Your Own Permission](https://docs.oracle.com/javase/tutorial/security/userperm/index.html)
**Связанные области:** [[23-security]] · **Вопросы:** security

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8). Объединяет страницы
> урока *Implementing Your Own Permission*: индекс, *ExampleGame*, *The HighScore Class*,
> *The HighScorePermission Class*, *A Sample Policy File*, *Putting It All Together* и три
> страницы шагов — *Chris*, *Terry*, *Kim*.

Этот урок показывает, как написать класс, который определяет собственное специальное разрешение
(*permission*). Основные составляющие урока:

1. Учебная игра под названием **ExampleGame**.
2. Класс **HighScore**, который игра `ExampleGame` использует для хранения последнего рекорда
   пользователя (*high score*).
3. Класс **HighScorePermission**, который защищает доступ к сохранённому значению рекорда
   пользователя.
4. Файл политики безопасности (*policy file*) пользователя, в котором игре `ExampleGame`
   выдаётся разрешение обновлять рекорд пользователя.

Базовый сценарий выглядит так:

1. Пользователь играет в `ExampleGame`.
2. Если пользователь достигает нового рекорда, `ExampleGame` использует класс `HighScore`,
   чтобы сохранить это новое значение.
3. Класс `HighScore` заглядывает в файл политики безопасности пользователя, чтобы проверить,
   есть ли у `ExampleGame` разрешение обновлять рекорд пользователя.
4. Если у `ExampleGame` есть это разрешение, класс `HighScore` обновляет значение рекорда.

Ниже описаны ключевые моменты каждой из основных составляющих, а затем показан пример запуска.

## ExampleGame

Ниже приведён исходный код игры `ExampleGame`. Для простоты `ExampleGame` на самом деле не
содержит кода самой игры. Она лишь считывает или обновляет рекорд пользователя.

Чтобы посмотреть текущее значение рекорда пользователя, можно выполнить:

```
java ExampleGame get
```

Чтобы установить новое значение рекорда для пользователя, можно выполнить:

```
java ExampleGame set <score>
```

Чтобы получить текущий рекорд пользователя, `ExampleGame` просто создаёт объект `HighScore`
и вызывает его метод `getHighScore`. Чтобы установить новый рекорд, `ExampleGame` создаёт
объект `HighScore` и вызывает `setHighScore`, передавая ему новый рекорд пользователя.

Вот исходный код игры `ExampleGame` (файл `ExampleGame.java`):

```java
package com.gamedev.games;

import java.io.*;
import java.security.*;
import java.util.Hashtable;
import com.scoredev.scores.*;

public class ExampleGame
{
    public static void main(String args[])
	throws Exception 
    {
	HighScore hs = new HighScore("ExampleGame");

	if (args.length == 0)
	    usage();

	if (args[0].equals("set")) {
	    hs.setHighScore(Integer.parseInt(args[1]));
	} else if (args[0].equals("get")) {
	    System.out.println("score = "+ hs.getHighScore());
	} else {
	    usage();
	}
    }

    public static void usage()
    {
	System.out.println("ExampleGame get");
	System.out.println("ExampleGame set <score>");
	System.exit(1);
    }
}
```

## Класс HighScore

Класс `HighScore` хранит рекорд пользователя для игры `ExampleGame` (и любых других игр, которые
к нему обращаются) и защищает доступ к нему. Для простоты этот класс сохраняет значение рекорда
в файл `.highscore` в домашнем каталоге пользователя. Однако, прежде чем позволить `ExampleGame`
считать или обновить рекорд пользователя, класс проверяет, что пользователь выдал игре
`ExampleGame` разрешение на доступ к рекорду в своём файле политики безопасности.

### Проверка того, что у ExampleGame есть HighScorePermission

Чтобы проверить, есть ли у `ExampleGame` разрешение на доступ к рекорду пользователя, класс
`HighScore` должен:

1. Вызвать `System.getSecurityManager()`, чтобы получить установленный в данный момент менеджер
   безопасности (*security manager*).
2. Если результат не `null` (то есть менеджер безопасности *есть*, а не вызывающий код является
   приложением без ограничений), то:
   1. Создать объект `HighScorePermission`, и
   2. Вызвать метод `checkPermission` менеджера безопасности, передав ему вновь созданный объект
      `HighScorePermission`.

Вот код:

```java
SecurityManager sm = System.getSecurityManager();
if (sm != null) {
    sm.checkPermission(
        new HighScorePermission(gameName));
}
```

Метод `checkPermission`, по сути, спрашивает у менеджера безопасности, есть ли у `ExampleGame`
указанное разрешение `HighScorePermission`. Иначе говоря, он спрашивает менеджер безопасности,
есть ли у `ExampleGame` разрешение обновлять рекорд пользователя для указанной игры
(`ExampleGame`). Лежащий в основе механизм безопасности обратится к файлу политики безопасности
пользователя, чтобы выяснить, действительно ли у `ExampleGame` есть это разрешение.

### Полный код HighScore

Ниже приведён полный исходный код класса `HighScore` (файл `HighScore.java`).

> Примечание. Вызовы метода `doPrivileged` нужны для того, чтобы `HighScore` мог временно
> обращаться к ресурсам, доступным ему, но недоступным вызывающему его коду (`ExampleGame`).
> Например, ожидается, что файл политики выдаст `HighScore` разрешение на доступ к файлу
> `.highscore` в домашнем каталоге пользователя, но не выдаст это разрешение играм, таким как
> `ExampleGame`.

```java
/*
 * Copyright (c) 1995, 2008, Oracle and/or its affiliates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - Neither the name of Oracle or the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 

package com.scoredev.scores;

import java.io.*;
import java.security.*;
import java.util.Hashtable;

public class HighScore
{
    private String gameName;
    private File highScoreFile;

    public HighScore(String gameName) 
    {
	this.gameName = gameName;

	AccessController.doPrivileged(new PrivilegedAction() {
	    public Object run() {
		String path = 
		    System.getProperty("user.home") +
		    File.separator + 
		    ".highscore";

		highScoreFile = new File(path);
		return null;
	    }
	});
    }

    public void setHighScore(final int score)
	throws IOException
    {
	// сначала проверяем разрешение
	SecurityManager sm = System.getSecurityManager();
	if (sm != null) {
	    sm.checkPermission(new HighScorePermission(gameName));
	}

	// чтобы работать с файлом, нужен блок doPrivileged
	try {
	    AccessController.doPrivileged(new PrivilegedExceptionAction() {
		public Object run() throws IOException {
		    Hashtable scores = null;
		    // пытаемся открыть существующий файл. Здесь должен быть
		    // протокол блокировки (можно использовать File.createNewFile).
		    try {
			FileInputStream fis = 
			    new FileInputStream(highScoreFile);
			ObjectInputStream ois = new ObjectInputStream(fis);
			scores = (Hashtable) ois.readObject();
		    } catch (Exception e) {
			// игнорируем, пытаемся создать новый файл
		    }

		    // если scores == null, создаём новую хеш-таблицу
		    if (scores == null)
			scores = new Hashtable(13);

		    // обновляем рекорд и сохраняем новый рекорд
		    scores.put(gameName, new Integer(score));
		    FileOutputStream fos = new FileOutputStream(highScoreFile);
		    ObjectOutputStream oos = new ObjectOutputStream(fos);
		    oos.writeObject(scores);
		    oos.close();
		    return null;
		}
	    });
	} catch (PrivilegedActionException pae) {
	    throw (IOException) pae.getException();
	}
    }

    /**
     * получить рекорд. Возвращает -1, если он ещё не был установлен.
     *
     */
    public int getHighScore()
	throws IOException, ClassNotFoundException
    {
	// сначала проверяем разрешение
	SecurityManager sm = System.getSecurityManager();
	if (sm != null) {
	    sm.checkPermission(new HighScorePermission(gameName));
	}

	Integer score = null;

	// чтобы работать с файлом, нужен блок doPrivileged
	try {
	     score = (Integer) AccessController.doPrivileged(
	                                new PrivilegedExceptionAction() {
		public Object run() 
		    throws IOException, ClassNotFoundException 
		{
		    Hashtable scores = null;
		    // пытаемся открыть существующий файл. Здесь должен быть
		    // протокол блокировки (можно использовать File.createNewFile).
		    FileInputStream fis = 
			new FileInputStream(highScoreFile);
		    ObjectInputStream ois = new ObjectInputStream(fis);
		    scores = (Hashtable) ois.readObject();

		    // извлекаем рекорд
		    return scores.get(gameName);
		}
	    });
	} catch (PrivilegedActionException pae) {
	    Exception e = pae.getException();
	    if (e instanceof IOException)
		throw (IOException) e;
	    else
		throw (ClassNotFoundException) e;
	}
	if (score == null)
		return -1;
	else
		return score.intValue();
    }



    public static void main(String args[])
	throws Exception 
    {
	HighScore hs = new HighScore(args[1]);
	if (args[0].equals("set")) {
	    hs.setHighScore(Integer.parseInt(args[2]));
	} else {
	    System.out.println("score = "+ hs.getHighScore());
	}
    }
}
```

## Класс HighScorePermission

Класс `HighScorePermission` определяет разрешение, которое нужно игре `ExampleGame`, чтобы
обновлять рекорд пользователя.

Все классы разрешений должны наследоваться либо от `java.security.Permission`, либо от
`java.security.BasicPermission`. Основное различие между ними в том, что `java.security.Permission`
определяет более сложные разрешения, требующие имени (*name*) и действий (*actions*). Например,
`java.io.FilePermission` наследуется от `java.security.Permission` и требует имени (имя файла)
и действий, разрешённых для этого файла (чтение/запись/удаление — read/write/delete).

В противоположность этому `java.security.BasicPermission` определяет более простые разрешения,
которым нужно только имя. Например, `java.lang.RuntimePermission` наследуется от
`java.security.BasicPermission` и нуждается лишь в имени (например, `"exitVM"`), которое позволяет
программам завершать работу виртуальной машины Java.

Наше разрешение `HighScorePermission` — простое, а значит, может быть унаследовано от
`java.security.BasicPermission`.

Часто реализации методов в самом классе `BasicPermission` не нужно переопределять в его
подклассах. Так обстоит дело и с нашим `HighScorePermission`, поэтому всё, что нам нужно
реализовать, — это конструкторы, которые просто вызывают конструкторы суперкласса, как показано
ниже:

```java
package com.scoredev.scores;

import java.security.*;

public final class HighScorePermission extends BasicPermission {

    public HighScorePermission(String name)
    {
	super(name);
    }

    // обратите внимание: actions игнорируется и не используется,
    // но этот конструктор всё равно нужен
    public HighScorePermission(String name, String actions) 
    {
	super(name, actions);
    }
}
```

## Пример файла политики

Ниже приведён полный файл политики (*policy file*) для пользователя, желающего запустить
`ExampleGame`.

Синтаксис файла политики здесь не описывается; если он вам интересен, см. страницу
[Default Policy Implementation and Policy File Syntax](https://docs.oracle.com/javase/8/docs/technotes/guides/security/PolicyFiles.html).

Знать синтаксис не обязательно: вы всегда можете воспользоваться инструментом Policy Tool для
создания файлов политики, как показано в уроках *Creating a Policy File*, *Quick Tour of
Controlling Applications* и *Signing Code and Granting It Permissions*.

Ниже приведён пример файла политики, а затем описание отдельных записей. Предполагается, что:

* Файл политики находится на компьютере Ким (Kim), и хранилище ключей Ким называется
  `kim.keystore`.
* `ExampleGame` подписана закрытым ключом создателя игры Терри (Terry), а соответствующий
  открытый ключ находится в записи хранилища ключей под псевдонимом (*alias*) `"terry"`.
* Классы `HighScore` и `HighScorePermissions` были подписаны закрытым ключом человека, который
  их реализовал (Криса — Chris), а соответствующий открытый ключ находится в записи хранилища
  ключей под псевдонимом `"chris"`.

Вот файл политики (`kim.policy`):

```
keystore "kim.keystore";

// Здесь разрешение, которое нужно ExampleGame.
// Оно выдаёт коду, подписанному "terry",
// разрешение HighScorePermission, если само
// HighScorePermission было подписано "chris"
grant SignedBy "terry" {
  permission
    com.scoredev.scores.HighScorePermission
      "ExampleGame", signedBy "chris";
};

// Здесь набор разрешений, нужных классу HighScore:
grant SignedBy "chris" {
  // Классу HighScore нужно разрешение читать
  // "user.home", чтобы найти расположение
  // файла рекордов

  permission java.util.PropertyPermission
    "user.home", "read";

  // Ему нужно разрешение читать и записывать
  // сам файл рекордов

  permission java.io.FilePermission
      "${user.home}${/}.highscore", "read,write";

  // Ему нужно получить собственное разрешение,
  // чтобы он мог вызывать checkPermission
  // и проверять, есть ли разрешение у вызывающего его кода.
  // Выдавать это разрешение только в том случае,
  // если оно само было подписано
  // "chris"

  permission
    com.scoredev.scores.HighScorePermission 
      "*", signedBy "chris";
};
```

### Запись хранилища ключей

*Хранилище ключей* (*keystore*) — это репозиторий ключей и сертификатов; оно используется для
поиска открытых ключей подписавших, указанных в файле политики (в этом примере — `"terry"` и
`"chris"`).

Для создания хранилищ ключей и управления ими используется утилита `keytool`.

В этом уроке предполагается, что Ким хотела бы поиграть в `ExampleGame`. Если хранилище ключей
Ким называется `kim.keystore`, то в самом начале файла политики Ким должна быть следующая строка:

```
keystore "kim.keystore";
```

### Запись для ExampleGame

Запись в файле политики задаёт одно или несколько разрешений для кода из определённого
*источника кода* (*code source*) — либо кода из определённого расположения (URL), либо кода,
подписанного определённой стороной, либо и того, и другого.

Нашему файлу политики нужна запись для каждой игры, выдающая коду, подписанному ключом создателя
этой игры, разрешение `HighScorePermission`, имя которого совпадает с названием игры. Это
разрешение позволяет игре вызывать методы `HighScore`, чтобы получить или обновить рекорд
пользователя именно для этой игры.

Запись, необходимая для `ExampleGame`:

```
grant SignedBy "terry" {
    permission
        com.scoredev.scores.HighScorePermission 
            "ExampleGame", signedBy "chris";
};
```

Требование о том, чтобы `ExampleGame` была подписана `"terry"`, позволяет Ким быть уверенной, что
эта игра — действительно та игра, которую разработал Терри. Чтобы это работало, Ким должна уже
сохранить сертификат открытого ключа Терри в `kim.keystore` под псевдонимом `"terry"`.

Обратите внимание, что само разрешение `HighScorePermission` должно быть подписано `"chris"` —
человеком, который фактически реализовал это разрешение. Это гарантирует, что `ExampleGame`
выдаётся именно то разрешение, которое реализовал `"chris"`, а не кто-то другой. Как и прежде,
чтобы это работало, Ким должна уже сохранить сертификат открытого ключа Криса в `kim.keystore`
под псевдонимом `"chris"`.

### Запись для HighScore

Последняя запись в файле политики выдаёт разрешения классу `HighScore`. Точнее, она выдаёт
разрешения коду, подписанному `"chris"`, который создал и подписал этот класс. Требование о том,
чтобы класс был подписан `"chris"`, гарантирует, что, когда `ExampleGame` обращается к этому
классу для обновления рекорда пользователя, `ExampleGame` точно знает, что использует исходный
класс, реализованный `"chris"`.

Чтобы обновлять рекорд пользователя для любых обращающихся к нему игр, классу `HighScore` нужны
три разрешения:

#### 1. Разрешение читать значение свойства `"user.home"`.

Класс `HighScore` хранит рекорды пользователя в файле `.highscore` в домашнем каталоге
пользователя. Поэтому этому классу нужно разрешение `java.util.PropertyPermission`, позволяющее
читать значение свойства `"user.home"`, чтобы выяснить, где именно находится домашний каталог
пользователя:

```
permission java.util.PropertyPermission 
    "user.home", "read";
```

#### 2. Разрешение читать и записывать сам файл рекордов.

Это разрешение нужно для того, чтобы методы `getHighScore` и `setHighScore` класса `HighScore`
могли обращаться к файлу `.highscore` пользователя и, соответственно, получать или устанавливать
текущий рекорд для текущей игры.

Вот требуемое разрешение:

```
permission java.io.FilePermission
    "${user.home}${/}.highscore", "read,write";
```

> Примечание. Запись `${propName}` задаёт значение свойства. Так, `${user.home}` будет заменено
> значением свойства `"user.home"`. Запись `${/}` — это платформенно-независимый способ указать
> разделитель файлов.

#### 3. Все разрешения HighScorePermission (то есть HighScorePermission с любым именем).

Это разрешение нужно для того, чтобы работали проверки `HighScore`, гарантирующие, что вызывающей
игре выдано разрешение `HighScorePermission`, имя которого совпадает с названием игры. То есть
классу `HighScore` *тоже* должно быть выдано это разрешение, поскольку проверка разрешения
требует, чтобы весь код, находящийся в данный момент в стеке вызовов, обладал указанным
разрешением.

Вот требуемое разрешение:

```
permission com.scoredev.scores.HighScorePermission
    "*", signedBy "chris";
```

Как и прежде, само разрешение `HighScorePermission` должно быть подписано `"chris"` — человеком,
который фактически реализовал это разрешение.

## Собираем всё вместе

Здесь мы по очереди выступим в роли разработчика `HighScore` (Криса), разработчика `ExampleGame`
(Терри) и пользователя (Ким), запускающего игру.

Вы можете выполнить все указанные шаги, а затем (как последний шаг Ким) запустить `ExampleGame`.

Шаги приводятся без объяснений. Дополнительные сведения о шагах, которые должны предпринять как
лица, подписывающие код (такие как Крис и Терри), так и получатели такого кода (такие как Ким),
см. в уроке *Signing Code and Granting It Permissions*.

### Шаги для разработчика HighScore (Криса)

Шаги, которые предпринял бы Крис после создания классов `HighScore` и `HighScorePermission`:

**Скомпилировать классы**

```
javac HighScore*.java -d .
```

**Поместить файлы классов в JAR-файл**

```
jar cvf hs.jar com/scoredev/scores/HighScore*.class
```

**Создать хранилище ключей и ключи для подписи**

```
keytool -genkey -keystore chris.keystore -alias signJars
```

Укажите любые пароли и информацию различающегося имени (*distinguished name*) на ваше усмотрение.

**Подписать JAR-файл**

```
jarsigner -keystore chris.keystore hs.jar signJars
```

**Экспортировать сертификат открытого ключа**

```
keytool -export -keystore chris.keystore
    -alias signJars -file Chris.cer
```

**Предоставить файлы и информацию, нужные разработчикам игр и пользователям**

То есть передать им:

* подписанный JAR-файл `hs.jar`;
* файл сертификата открытого ключа `Chris.cer`;
* информацию о том, какие разрешения нужно выдать классам `HighScore` и `HighScorePermission`
  в файле политики, чтобы они работали. Для этого Крис мог бы предоставить точную запись `grant`.

### Шаги для разработчика ExampleGame (Терри)

Шаги, которые предпринял бы Терри после создания игры (`ExampleGame`), вызывающей методы
`getHighScore` и `setHighScore` класса `HighScore` для получения и установки рекордов
пользователя соответственно:

**Скомпилировать класс игры**

```
javac ExampleGame.java -classpath hs.jar -d .
```

**Поместить файл его класса в JAR-файл**

```
jar cvf terry.jar com/gamedev/games/ExampleGame.class
```

**Создать хранилище ключей и ключи для подписи**

```
keytool -genkey -keystore terry.keystore -alias signTJars
```

Укажите любые пароли и информацию различающегося имени на ваше усмотрение.

**Подписать JAR-файл**

```
jarsigner -keystore terry.keystore terry.jar signTJars
```

**Экспортировать сертификат открытого ключа**

```
keytool -export -keystore terry.keystore
    -alias signTJars -file Terry.cer
```

**Предоставить файлы и информацию, нужные пользователям**

То есть передать им:

* подписанный JAR-файл `terry.jar`;
* файл сертификата открытого ключа `Terry.cer`;
* информацию о том, какие разрешения нужны классу `ExampleGame`. Для этого Терри мог бы
  предоставить точную запись `grant`.

Пользователям игры также нужны файлы и информация от Криса. Для их удобства Терри может переслать
им эту информацию:

* подписанный JAR-файл `hs.jar`;
* файл сертификата открытого ключа `Chris.cer`;
* информацию о том, какие разрешения нужно выдать классам `HighScore` и `HighScorePermission`
  в файле политики, чтобы они работали. Это может быть точная запись `grant`.

### Шаги для пользователя, запускающего ExampleGame (Ким)

Шаги, которые предпринял бы пользователь, такой как Ким:

**Импортировать сертификаты как доверенные сертификаты**

```
keytool -import -alias chris -file Chris.cer -keystore kim.keystore
keytool -import -alias terry -file Terry.cer -keystore kim.keystore
```

**Настроить файл политики с требуемыми разрешениями**

Полный файл политики `kim.policy` приведён выше, в разделе «Пример файла политики».

**Запустить ExampleGame**

Чтобы установить рекорд:

```
java -Djava.security.manager 
    -Djava.security.policy=kim.policy
    -classpath hs.jar;terry.jar
    com.gamedev.games.ExampleGame set 456
```

Чтобы получить рекорд:

```
java -Djava.security.manager
    -Djava.security.policy=kim.policy
    -classpath hs.jar;terry.jar
    com.gamedev.games.ExampleGame get
```

Примечания:

* Если не указать `-Djava.security.manager`, приложение будет работать без ограничений (файлы
  политики и разрешения проверяться не будут).
* `-Djava.security.policy=kim.policy` указывает, где находится файл политики. Примечание: есть
  и другие способы указать файл политики. Например, можно добавить в файл свойств безопасности
  (*security properties file*) запись, указывающую на включение `kim.policy`, как обсуждается
  в конце урока *See the Policy File Effects*.
* `-classpath hs.jar;terry.jar` указывает JAR-файлы, содержащие нужные файлы классов. В Windows
  для разделения JAR-файлов используется точка с запятой (`;`); в UNIX — двоеточие (`:`).
* Файл политики `kim.policy` указывает хранилище ключей `kim.keystore`. Поскольку для хранилища
  ключей не задан абсолютный URL-адрес, предполагается, что оно находится в том же каталоге, что
  и файл политики.

## Источник

- [Implementing Your Own Permission](https://docs.oracle.com/javase/tutorial/security/userperm/index.html) — официальное руководство Oracle.
- [ExampleGame](https://docs.oracle.com/javase/tutorial/security/userperm/game.html)
- [The HighScore Class](https://docs.oracle.com/javase/tutorial/security/userperm/highscore.html)
- [The HighScorePermission Class](https://docs.oracle.com/javase/tutorial/security/userperm/perm.html)
- [A Sample Policy File](https://docs.oracle.com/javase/tutorial/security/userperm/policy.html)
- [Putting It All Together](https://docs.oracle.com/javase/tutorial/security/userperm/together.html)
- [Steps for the HighScore Developer (Chris)](https://docs.oracle.com/javase/tutorial/security/userperm/chris.html)
- [Steps for the ExampleGame Developer (Terry)](https://docs.oracle.com/javase/tutorial/security/userperm/terry.html)
- [Steps for a User Running ExampleGame (Kim)](https://docs.oracle.com/javase/tutorial/security/userperm/kim.html)
- [HighScore.java](https://docs.oracle.com/javase/tutorial/security/userperm/examples/com/scoredev/scores/HighScore.java) — полный исходный код класса `HighScore`.
```