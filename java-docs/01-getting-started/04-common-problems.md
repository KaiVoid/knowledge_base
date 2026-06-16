# Урок 4. Типичные проблемы (и их решения)

**Трейл:** Getting Started · **Оригинал:** [Common Problems (and Their Solutions)](https://docs.oracle.com/javase/tutorial/getStarted/problems/index.html)
**Связанные области:** [[01-core-java-syntax-oop]] · [[18-build-tools]] · **Вопросы:** core-java

> Перевод официального руководства Oracle (The Java Tutorials, JDK 8).

## Проблемы компиляции

### Частые сообщения об ошибках в Microsoft Windows

**`'javac' is not recognized as an internal or external command, operable program or batch file`**

Windows не может найти компилятор `javac`. Можно указать путь явно. Если JDK установлен в
`C:\jdk1.8.0`, выполните:

```
C:\jdk1.8.0\bin\javac HelloWorldApp.java
```

При таком способе придётся каждый раз предварять команды `javac` и `java` префиксом
`C:\jdk1.8.0\bin\`. Чтобы избежать лишнего набора, добавьте каталог в переменную `PATH` (см.
раздел *Updating the PATH variable* в инструкции по установке JDK 8).

**`Class names, 'HelloWorldApp', are only accepted if annotation processing is explicitly requested`**

Вы забыли указать суффикс `.java` при компиляции. Команда должна быть
`javac HelloWorldApp.java`, а не `javac HelloWorldApp`.

### Частые сообщения об ошибках в UNIX

**`javac: Command not found`**

UNIX не может найти компилятор `javac`. Если JDK установлен в `/usr/local/jdk1.8.0`, выполните:

```
/usr/local/jdk1.8.0/javac HelloWorldApp.java
```

Чтобы не вводить путь каждый раз, добавьте его в переменную `PATH` (способ зависит от вашей
оболочки).

**`Class names, 'HelloWorldApp', are only accepted if annotation processing is explicitly requested`**

Вы забыли суффикс `.java`. Команда — `javac HelloWorldApp.java`, а не `javac HelloWorldApp`.

### Синтаксические ошибки (все платформы)

Если вы ошиблись в наборе программы, компилятор может выдать **синтаксическую ошибку**. Сообщение
обычно показывает тип ошибки, номер строки, код этой строки и позицию ошибки. Пример — пропущена
точка с запятой (`;`) в конце оператора:

```
Testing.java:8: error: ';' expected
            count++
                   ^
1 error
```

Если есть ошибки компиляции, программа не скомпилировалась и файл `.class` не создан. Внимательно
проверьте программу, исправьте ошибки и повторите.

### Семантические ошибки

Помимо синтаксиса компилятор проверяет базовую корректность. Например, предупреждает об
использовании неинициализированной переменной:

```
Testing.java:8: error: variable count might not have been initialized
            count++;
            ^
Testing.java:9: error: variable count might not have been initialized
        System.out.println("Input has " + count + " chars.");
                                          ^
2 errors
```

Программа снова не скомпилировалась — исправьте ошибку и попробуйте ещё раз.

## Проблемы времени выполнения

### Сообщения об ошибках в Microsoft Windows

**`Exception in thread "main" java.lang.NoClassDefFoundError: HelloWorldApp`**

`java` не может найти файл байт-кода `HelloWorldApp.class`. Одно из мест поиска — текущий каталог.
Перейдите в каталог с файлом (например, `cd c:\java`), убедитесь командой `dir`, что `.class`
на месте, и снова запустите `java HelloWorldApp`.

Если не помогло, возможно, придётся изменить переменную `CLASSPATH`. Чтобы проверить, очистите её:

```
set CLASSPATH=
```

Если после этого программа заработала, нужно настроить `CLASSPATH` (аналогично `PATH`).

**`Could not find or load main class HelloWorldApp.class`**

Частая ошибка новичков — запускать `java` на файле `.class`. Эта ошибка возникает при
`java HelloWorldApp.class` вместо `java HelloWorldApp`. Аргумент — это **имя класса**, а не имя файла.

**`Exception in thread "main" java.lang.NoSuchMethodError: main`**

Виртуальная машина Java требует, чтобы у запускаемого класса был метод `main`, с которого
начинается выполнение. Подробно метод `main` разобран в
[уроке 3 «Подробный разбор приложения Hello World!»](03-closer-look.md).

### Сообщения об ошибках в UNIX

**`Exception in thread "main" java.lang.NoClassDefFoundError: HelloWorldApp`**

`java` не может найти файл байт-кода. Перейдите в каталог с файлом (например,
`cd /home/jdoe/java`), проверьте наличие файлов командами `pwd` и `ls`, снова запустите
`java HelloWorldApp`. Если не помогло, очистите `CLASSPATH`:

```
unset CLASSPATH
```

и при необходимости настройте её так же, как `PATH`.

**`Exception in thread "main" java.lang.NoClassDefFoundError: HelloWorldApp/class`**

Та же ошибка новичков — запуск `java HelloWorldApp.class` вместо `java HelloWorldApp`. Аргумент —
имя класса, а не имя файла.

**`Exception in thread "main" java.lang.NoSuchMethodError: main`**

У класса нет метода `main`. См. [урок 3](03-closer-look.md).

### Апплет или Java Web Start-приложение заблокировано

Если приложение запускается через браузер и появляются предупреждения безопасности о блокировке,
проверьте:

- атрибуты в манифесте JAR-файла корректны для среды запуска (атрибут `Permissions` обязателен);
- приложение подписано действительным сертификатом, и сертификат находится в хранилище Signer CA;
- для локального апплета настроен веб-сервер для тестирования (либо приложение добавлено в список
  исключений на вкладке «Безопасность» панели управления Java).

## Источник

- [Common Problems (and Their Solutions)](https://docs.oracle.com/javase/tutorial/getStarted/problems/index.html) — официальное руководство Oracle.
