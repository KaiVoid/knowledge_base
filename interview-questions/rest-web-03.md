# REST, HTTP и веб-слой — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/17-rest-web.md](../knowledge-base/17-rest-web.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](rest-web-01.md) · [ч.2](rest-web-02.md) · **ч.3**

---
### Вопрос 41. Что такое content negotiation (согласование содержимого) в HTTP? Какую роль играют заголовки Accept и Content-Type, и как Spring MVC определяет медиатип ответа при наличии нескольких подходящих HttpMessageConverter?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Content Negotiation using Spring MVC — Spring Blog](https://spring.io/blog/2013/05/11/content-negotiation-using-spring-mvc/)

Согласование содержимого (content negotiation) — это процесс определения, в каком формате данных вернуть ответ клиенту. Как отмечается в статье: «Определение формата данных для возврата называется согласованием содержимого».

Spring использует `ContentNegotiationManager`, реализующий стратегию PPA (Path extension, Parameter, Accept header), которые проверяются в следующем порядке:

1. **Расширение пути (Path Extension):** URL вида `http://myserver/myapp/accounts/list.json` задаёт формат через суффикс.
2. **URL-параметр (Parameter):** Формат указывается как `?format=json` (по умолчанию отключено).
3. **Заголовок Accept:** Стандартный HTTP-механизм (включён по умолчанию).

Автор отмечает, что «браузеры отправляют крайне запутанные заголовки Accept», поэтому Accept-стратегия по умолчанию имеет наименьший приоритет при наличии альтернатив.

Для работы с несколькими форматами метод контроллера объявляет поддерживаемые типы через атрибут `produces`:

```java
@RequestMapping(value="/accounts", produces={"application/xml", "application/json"})
@ResponseBody
public List<Account> list(Principal principal) {
    return accountManager.getAccounts(principal);
}
```

При наличии Jackson и JAXB2 в classpath Spring MVC автоматически регистрирует соответствующие `HttpMessageConverter`. Согласованный медиатип определяет, какой конвертер сериализует ответ.

Конфигурация через Java Config:

```java
@Override
public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
    configurer.favorPathExtension(true)
              .ignoreAcceptHeader(true)
              .defaultContentType(MediaType.TEXT_HTML)
              .mediaType("json", MediaType.APPLICATION_JSON);
}
```

#### Ответ от Claude

**Что такое content negotiation**

Content negotiation — механизм HTTP, позволяющий клиенту и серверу договориться о формате передаваемых данных. Клиент сообщает о своих предпочтениях, сервер выбирает наиболее подходящий формат из тех, что он умеет отдавать.

**Роли заголовков**

- **`Content-Type`** — описывает формат тела уже отправленного сообщения. При запросе клиент указывает формат тела (`Content-Type: application/json`), при ответе — сервер сообщает, в каком формате отдаёт данные.
- **`Accept`** — клиент перечисляет форматы, которые он готов принять в ответе, с приоритетами через `q`-фактор: `Accept: application/json;q=0.9, application/xml;q=0.8`.

**Как Spring MVC определяет медиатип ответа**

Spring MVC использует `ContentNegotiationManager`, который последовательно применяет зарегистрированные стратегии (`ContentNegotiationStrategy`):

1. **`PathExtensionContentNegotiationStrategy`** — анализирует расширение URL (`.json`, `.xml`). Устарела начиная со Spring 5.3, удалена в Spring 6.
2. **`ParameterContentNegotiationStrategy`** — анализирует параметр запроса (по умолчанию `format`). Отключена по умолчанию.
3. **`HeaderContentNegotiationStrategy`** — анализирует заголовок `Accept`. Включена по умолчанию.
4. **`FixedContentNegotiationStrategy`** — возвращает фиксированный медиатип (используется как `defaultContentType`).

Стратегии проверяются по порядку; первая, вернувшая непустой список медиатипов, выигрывает.

**Алгоритм выбора HttpMessageConverter**

После того как `ContentNegotiationManager` определил список желаемых медиатипов, `AbstractMessageConverterMethodProcessor` перебирает зарегистрированные конвертеры:

```
для каждого желаемого медиатипа (из Accept, по убыванию q):
    для каждого HttpMessageConverter в списке (в порядке регистрации):
        если converter.canWrite(returnType, mediaType) == true:
            использовать этот конвертер → выйти
если ни один конвертер не подошёл → бросить HttpMediaTypeNotAcceptableException (406)
```

**Встроенные конвертеры (всегда зарегистрированы)**

| Конвертер | Медиатипы |
|-----------|-----------|
| `StringHttpMessageConverter` | `text/plain`, `*/*` |
| `ByteArrayHttpMessageConverter` | `application/octet-stream`, `*/*` |
| `ResourceHttpMessageConverter` | `*/*` |
| `MappingJackson2HttpMessageConverter` | `application/json` (если Jackson в classpath) |
| `Jaxb2RootElementHttpMessageConverter` | `application/xml`, `text/xml` (если JAXB2 в classpath) |

**Порядок конвертеров важен.** При нескольких конвертерах, поддерживающих один медиатип (например, `*/*`), побеждает первый в списке. `MappingJackson2HttpMessageConverter` поддерживает `*/*`, поэтому его можно неожиданно использовать вместо `StringHttpMessageConverter`, если добавить его раньше.

**Пример: клиент запрашивает XML**

```http
GET /api/users/1 HTTP/1.1
Accept: application/xml
```

1. `HeaderContentNegotiationStrategy` извлекает `application/xml`.
2. Spring перебирает конвертеры; `Jaxb2RootElementHttpMessageConverter` заявляет поддержку `application/xml` и `canWrite()` возвращает `true`.
3. Конвертер сериализует объект в XML.
4. Ответ содержит `Content-Type: application/xml`.

**Аннотация `produces`**

Атрибут `produces` в `@RequestMapping` ограничивает множество медиатипов, которые метод контроллера готов производить. Если согласованный тип не входит в `produces` — Spring возвращает `406 Not Acceptable` до запуска метода.

**Расхождения между источниками**

Блог Spring (2013) описывает приоритет «расширение > параметр > Accept». В Spring 5.3+ расширение пути как стратегия признана устаревшей из соображений безопасности (path traversal), а в Spring 6 удалена полностью. Актуальный порядок по умолчанию в Spring 6: параметр (отключён) → Accept header → defaultContentType.

---

### Вопрос 42. Как реализовать HATEOAS в Spring Boot с помощью библиотеки Spring HATEOAS? Объясните назначение классов EntityModel, CollectionModel и WebMvcLinkBuilder, и покажите, как добавить ссылки в ответ.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Spring HATEOAS — Reference Documentation](https://docs.spring.io/spring-hateoas/docs/current/reference/html/)

Spring HATEOAS предоставляет иерархию классов для создания ресурсов с поддержкой гипермедиа.

**Иерархия классов представления**

```
RepresentationModel (базовый класс-контейнер для ссылок)
├── EntityModel<T>       — оборачивает одиночный объект
├── CollectionModel<T>   — оборачивает коллекцию объектов
└── PagedModel<T>        — расширение CollectionModel с метаданными пагинации
```

**RepresentationModel** — базовый класс, хранящий коллекцию `Link` и предоставляющий API для их добавления. Возвращает экземпляр `Links` (не `List<Link>`), поддерживает fluent API.

**EntityModel** — удобный тип для оборачивания одиночного доменного объекта без создания пользовательского подкласса:
```java
Person person = new Person("Dave", "Matthews");
EntityModel<Person> model = EntityModel.of(person);
model.add(Link.of("https://myhost/people/42").withSelfRel());
```

**CollectionModel** — для ресурсов, представляющих коллекцию:
```java
Collection<Person> people = Collections.singleton(new Person("Dave", "Matthews"));
CollectionModel<Person> model = CollectionModel.of(people);
model.add(Link.of("/people").withSelfRel());
```

Из-за стирания типов пустые коллекции требуют явного указания типа:
```java
CollectionModel.empty(Person.class)
// или
CollectionModel.of(people).withFallbackType(Person.class);
```

**WebMvcLinkBuilder** — утилита для создания ссылок, указывающих на методы Spring MVC контроллеров, без жёсткого кодирования URI:
```java
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.*;

Link link = linkTo(methodOn(PersonController.class).show(2L)).withSelfRel();
// Результат href: http://localhost:8080/people/2
```

HAL-вывод для `EntityModel`:
```json
{
  "firstname": "Dave",
  "lastname": "Matthews",
  "_links": {
    "self": { "href": "https://myhost/people/42" }
  }
}
```

HAL-вывод для `CollectionModel`:
```json
{
  "_embedded": {
    "personList": [
      { "firstname": "Dave", "_links": { "self": { "href": "/people/1" } } }
    ]
  },
  "_links": {
    "self": { "href": "/people" }
  }
}
```

#### Ответ от Claude

**Что такое HATEOAS**

HATEOAS (Hypermedia As The Engine Of Application State) — принцип REST, при котором клиент взаимодействует с API исключительно через гиперссылки, возвращаемые сервером. Клиент не должен знать URL заранее — он обнаруживает возможные действия из ответов. Spring HATEOAS — библиотека, упрощающая реализацию этого принципа.

**Подключение зависимости**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-hateoas</artifactId>
</dependency>
```

**EntityModel — одиночный ресурс**

`EntityModel<T>` оборачивает доменный объект и добавляет к нему ссылки (`_links` в HAL). Используется для ответов, представляющих один ресурс.

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @GetMapping("/{id}")
    public EntityModel<Order> getOrder(@PathVariable Long id) {
        Order order = orderService.findById(id);

        return EntityModel.of(order,
            linkTo(methodOn(OrderController.class).getOrder(id))
                .withSelfRel(),
            linkTo(methodOn(OrderController.class).getAllOrders())
                .withRel("orders"),
            linkTo(methodOn(OrderController.class).cancelOrder(id))
                .withRel("cancel")
        );
    }
}
```

Результирующий JSON (HAL):
```json
{
  "id": 1,
  "status": "PROCESSING",
  "_links": {
    "self":   { "href": "http://localhost:8080/api/orders/1" },
    "orders": { "href": "http://localhost:8080/api/orders" },
    "cancel": { "href": "http://localhost:8080/api/orders/1/cancel" }
  }
}
```

**CollectionModel — коллекция ресурсов**

`CollectionModel<T>` оборачивает список объектов и добавляет ссылки на уровне всей коллекции.

```java
@GetMapping
public CollectionModel<EntityModel<Order>> getAllOrders() {
    List<EntityModel<Order>> orders = orderService.findAll().stream()
        .map(order -> EntityModel.of(order,
            linkTo(methodOn(OrderController.class).getOrder(order.getId()))
                .withSelfRel()))
        .collect(Collectors.toList());

    return CollectionModel.of(orders,
        linkTo(methodOn(OrderController.class).getAllOrders())
            .withSelfRel());
}
```

Результирующий JSON (HAL):
```json
{
  "_embedded": {
    "orderList": [
      {
        "id": 1,
        "status": "PROCESSING",
        "_links": {
          "self": { "href": "http://localhost:8080/api/orders/1" }
        }
      }
    ]
  },
  "_links": {
    "self": { "href": "http://localhost:8080/api/orders" }
  }
}
```

**WebMvcLinkBuilder — построитель ссылок**

`WebMvcLinkBuilder` генерирует ссылки на основе маппингов Spring MVC контроллеров, а не жёстко заданных строк. При изменении URL в аннотации `@GetMapping` все ссылки обновятся автоматически.

Ключевые методы:

| Метод | Описание |
|-------|----------|
| `linkTo(Class)` | Ссылка на корневой URL класса контроллера |
| `linkTo(methodOn(Cls).method(...))` | Ссылка на конкретный метод с подстановкой параметров |
| `.withSelfRel()` | Устанавливает rel="self" |
| `.withRel("name")` | Устанавливает произвольный rel |
| `.slash(id)` | Добавляет сегмент пути |

```java
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.*;

// Ссылка на класс контроллера
linkTo(OrderController.class).withRel("orders");
// → /api/orders

// Ссылка на метод с параметром
linkTo(methodOn(OrderController.class).getOrder(42L)).withSelfRel();
// → /api/orders/42

// Цепочка через slash
linkTo(OrderController.class).slash(42L).slash("items").withRel("items");
// → /api/orders/42/items
```

**RepresentationModelAssembler — разделение ответственности**

Для сложных ресурсов рекомендуется выносить логику сборки модели в отдельный assembler:

```java
@Component
public class OrderModelAssembler
        implements RepresentationModelAssembler<Order, EntityModel<Order>> {

    @Override
    public EntityModel<Order> toModel(Order order) {
        return EntityModel.of(order,
            linkTo(methodOn(OrderController.class)
                .getOrder(order.getId())).withSelfRel(),
            linkTo(methodOn(OrderController.class)
                .getAllOrders()).withRel("orders"));
    }
}

// В контроллере:
@GetMapping("/{id}")
public EntityModel<Order> getOrder(@PathVariable Long id,
                                   OrderModelAssembler assembler) {
    return assembler.toModel(orderService.findById(id));
}
```

**Имена классов до Spring HATEOAS 1.0 (для понимания старого кода)**

| Старое имя | Новое имя |
|-----------|-----------|
| `ResourceSupport` | `RepresentationModel` |
| `Resource<T>` | `EntityModel<T>` |
| `Resources<T>` | `CollectionModel<T>` |
| `PagedResources<T>` | `PagedModel<T>` |
| `ResourceAssembler` | `RepresentationModelAssembler` |

**Расхождения между источниками**

Официальная документация Spring HATEOAS описывает `EntityModel.of(entity, link1, link2, ...)` как краткую форму. HowToDoInJava показывает вариант через `RepresentationModelAssemblerSupport` с методом `createResource()`, который является устаревшим начиная с версии 1.1 — следует использовать `instantiateModel()`. В актуальной документации рекомендуется `RepresentationModelAssembler` напрямую.
### Вопрос 43. Чем Spring WebFlux отличается от Spring MVC с точки зрения модели выполнения? Когда стоит выбрать WebFlux, а когда достаточно MVC с виртуальными потоками (Java 21+)?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Overview :: Spring Framework — Web on Reactive Stack](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html)

Spring WebFlux появился по двум причинам. Первая — потребность в неблокирующем веб-стеке, способном обрабатывать конкурентные запросы с небольшим числом потоков и меньшими аппаратными ресурсами. Servlet API с его синхронными контрактами (`Filter`, `Servlet`) и блокирующими операциями (`getParameter`, `getPart`) не подходил для этой роли, что потребовало нового общего API. Вторая причина — развитие функционального программирования: лямбда-выражения Java 8 открыли возможности для декларативной компоновки асинхронной логики в стиле `CompletableFuture` и ReactiveX.

**Модель выполнения Spring MVC (блокирующая):**
В Spring MVC предполагается, что приложение может блокировать текущий поток (например, при вызове удалённых сервисов). Поэтому Servlet-контейнеры используют большой пул потоков, чтобы поглощать потенциальные блокировки при обработке запросов.

**Модель выполнения Spring WebFlux (неблокирующая):**
В Spring WebFlux предполагается, что приложение не блокирует потоки. Поэтому неблокирующие серверы используют небольшой пул фиксированного размера (event loop workers) для обработки запросов. Никогда не блокировать текущий поток (опираясь на коллбэки вместо блокировок) означает, что дополнительные потоки не нужны — блокирующих вызовов нет.

**Когда выбирать Spring MVC:**
- Приложение уже работает на Spring MVC и работает корректно — нет смысла менять стек.
- Используются блокирующие API персистентности (JPA, JDBC).
- Большая команда без опыта реактивного программирования — крутая кривая обучения.

**Когда выбирать Spring WebFlux:**
- Нужен неблокирующий стек для высокой конкурентности с малым числом потоков.
- Требуется выполнение нескольких параллельных удалённых вызовов (реактивный `WebClient`).
- Используются реактивные БД (R2DBC) или работа идёт со стриминговыми данными.
- Лёгкие микросервисы, где важна прозрачность и контроль.

#### Ответ от Claude

**Принципиальное различие в модели выполнения**

Spring MVC строится на модели «один поток на запрос» (thread-per-request) поверх Servlet API. Каждый входящий запрос занимает поток из пула Tomcat/Jetty на всё время своей обработки — включая ожидание ответов от БД, внешних сервисов и т.д. При высокой нагрузке с долгими I/O-операциями пул потоков исчерпывается и новые запросы встают в очередь.

Spring WebFlux строится на неблокирующем событийном цикле (event loop). Небольшое число потоков (обычно равное числу CPU-ядер, потоки Netty с именами `reactor-http-nio-*`) мультиплексирует все соединения. Когда происходит I/O, поток не ждёт — он обрабатывает другие события. Callback/реактивные операторы возобновляют обработку при готовности данных.

**Виртуальные потоки Java 21 и Spring MVC**

Project Loom (Java 21) вводит виртуальные потоки — легковесные потоки, создаваемые тысячами без значительных накладных расходов. При блокировке на I/O виртуальный поток «паркуется» без удержания нативного потока ОС. Это делает модель thread-per-request масштабируемой: Spring MVC с виртуальными потоками даёт конкурентность, сопоставимую с WebFlux, без отказа от привычного императивного стиля кода.

Включается в Spring Boot 3.2+ одной строкой в `application.properties`:
```properties
spring.threads.virtual.enabled=true
```

**Практическое руководство по выбору стека**

| Критерий | Spring MVC + Virtual Threads | Spring WebFlux |
|---|---|---|
| Стиль кода | Синхронный, императивный | Реактивный, декларативный |
| Число потоков | Много виртуальных (дёшевы) | Мало реальных (event loop) |
| Блокирующие библиотеки (JPA, JDBC) | Нативная поддержка | Требует обёртки в `subscribeOn` |
| Стриминг данных (SSE, WebSocket) | Ограниченная поддержка | Нативная поддержка через `Flux` |
| Параллельные удалённые вызовы | Требует явного `CompletableFuture` | Нативно через `Mono.zip` |
| Порог входа для команды | Низкий | Высокий |

**Рекомендация:** если приложение работает на Spring MVC и планируется переход на Java 21, виртуальные потоки дают большую часть преимуществ WebFlux без смены парадигмы. WebFlux оправдан при работе с полностью реактивным стеком (R2DBC, реактивные MongoDB/Redis-клиенты), интенсивном стриминге или необходимости тонкого контроля над потоками данных.

Дополнительный источник: [Reactor WebFlux vs Virtual Threads — Baeldung](https://www.baeldung.com/java-reactor-webflux-vs-virtual-threads); [Spring Blog: Runtime efficiency with Spring](https://spring.io/blog/2023/10/16/runtime-efficiency-with-spring/)

---

### Вопрос 44. Что такое Mono и Flux в Project Reactor? Чем они отличаются, и какой из них следует возвращать из метода контроллера WebFlux при получении одного ресурса, а какой — при получении коллекции?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Simple Ways to Create a Flux or Mono :: Reactor Core Reference Guide](https://projectreactor.io/docs/core/release/reference/coreFeatures/simple-ways-to-create-a-flux-or-mono-and-subscribe-to-it.html)

**Flux** — это асинхронная последовательность из 0..N элементов. Он может испустить ноль, один или несколько элементов, после чего завершается сигналом `onComplete` или сигналом ошибки `onError`.

```java
Flux<String> seq1 = Flux.just("foo", "bar", "foobar");
Flux<Integer> numbers = Flux.range(5, 3);
```

**Mono** — это асинхронный результат из 0 или 1 элемента. Испускает не более одного значения через `onNext`, затем завершается.

```java
Mono<String> noData = Mono.empty();
Mono<String> data = Mono.just("foo");
```

**Применение в контроллерах WebFlux:**
- `Mono<T>` — при операциях, дающих один результат (поиск ресурса по ID).
- `Flux<T>` — при операциях, дающих множество элементов (список ресурсов). Элементы передаются потоком по мере появления, без буферизации в памяти.

#### Ответ от Claude

**Иерархия типов: оба реализуют Publisher**

`Mono<T>` и `Flux<T>` оба реализуют интерфейс `Publisher<T>` из спецификации Reactive Streams. Они являются центральными типами библиотеки Project Reactor, на которой внутренне построен Spring WebFlux.

```
Publisher<T>  (Reactive Streams)
├── Mono<T>   — 0 или 1 элемент
└── Flux<T>   — 0..N элементов
```

**Mono**
- Семантически эквивалентен реактивному аналогу `Optional<T>` или `CompletableFuture<T>`.
- Испускает сигналы: `onNext` (0 или 1 раз), затем `onComplete` или `onError`.
- Используется для: поиска по ID, сохранения/обновления сущности, удаления, вызова внешнего сервиса, возвращающего один результат.

**Flux**
- Семантически эквивалентен реактивному `Stream<T>` или `List<T>`.
- Испускает сигналы: `onNext` (0..N раз), затем `onComplete` или `onError`.
- Поддерживает backpressure — подписчик управляет темпом получения элементов через `request(n)`.
- Используется для: списков ресурсов, стриминга событий (SSE), чтения строк из файла, результатов запроса к БД.

**Применение в контроллерах WebFlux**

```java
@RestController
@RequestMapping("/users")
public class UserController {

    // Один ресурс — возвращаем Mono
    @GetMapping("/{id}")
    public Mono<User> getUser(@PathVariable Long id) {
        return userRepository.findById(id);
    }

    // Коллекция — возвращаем Flux
    @GetMapping
    public Flux<User> getAllUsers() {
        return userRepository.findAll();
    }

    // Поиск с возможным отсутствием результата — тоже Mono
    @GetMapping("/by-email")
    public Mono<ResponseEntity<User>> findByEmail(@RequestParam String email) {
        return userRepository.findByEmail(email)
            .map(ResponseEntity::ok)
            .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}
```

**Важный нюанс: Flux vs Mono<List>**

Spring WebFlux поддерживает оба варианта для коллекций, но они ведут себя по-разному:

- `Flux<User>` — элементы стримятся по мере готовности, не буферизуются; эффективно по памяти, но при ошибке в середине потока корректный HTTP-ответ об ошибке уже не отправить (заголовки уже могут быть записаны).
- `Mono<List<User>>` (через `flux.collectList()`) — собирает все элементы в список перед отправкой; требует больше памяти, но позволяет корректно обработать ошибки.

Согласно документации Spring: «Для возвращаемых типов вроде `Flux`, когда ожидается несколько значений, элементы стримятся по мере прихода и не буферизуются, поскольку хранить потенциально большое количество элементов в памяти неэффективно.»

Дополнительный источник: [Return Values :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webflux/controller/ann-methods/return-types.html); [Flux API — Project Reactor](https://projectreactor.io/docs/core/release/api/reactor/core/publisher/Flux.html)

---

### Вопрос 45. Что такое backpressure в реактивном программировании и как Spring WebFlux реализует его через интерфейс Reactive Streams Publisher? Приведите пример сценария, где отсутствие backpressure приводит к проблемам.

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Introduction to Reactive Programming :: Reactor Core Reference Guide](https://projectreactor.io/docs/core/release/reference/reactiveProgramming.html)

Backpressure — это способность потребителя сигнализировать производителю, что темп эмиссии данных слишком высок.

В модели Reactive Streams подписчик (`Subscriber`) может управлять потоком через механизм `request`. Вместо того чтобы источник проталкивал данные с максимальной скоростью, подписчик сигнализирует, что готов принять не более `n` элементов. Этот сигнал запроса распространяется вверх по всей цепочке операторов обратно к источнику-издателю (`Publisher`).

Это превращает традиционную push-модель в гибридную push-pull модель: нижестоящий оператор может извлекать (`pull`) `n` элементов, если они уже доступны, а если нет — верхний оператор проталкивает (`push`) их, когда они производятся.

Промежуточные операторы также могут модифицировать запросы, некоторые реализуют стратегии предвыборки (`prefetch`), чтобы избежать избыточных round-trips с `request(1)`.

#### Ответ от Claude

**Что такое backpressure**

Backpressure (противодавление) — механизм, позволяющий потребителю контролировать скорость поступления данных от производителя. Без него быстрый производитель может переполнить медленного потребителя, что приводит к переполнению буферов, росту потребления памяти и в конечном счёте к сбою системы.

Пример-аналогия из документации Reactor: сборочная линия — если на одном участке возникает затор (упаковка занимает непропорционально много времени), этот участок должен сигнализировать выше по потоку о снижении темпа подачи материала.

**Спецификация Reactive Streams**

Reactive Streams — это спецификация (принята также как `java.util.concurrent.Flow` в Java 9), определяющая четыре интерфейса:

```java
// Производитель данных
public interface Publisher<T> {
    void subscribe(Subscriber<? super T> s);
}

// Потребитель данных
public interface Subscriber<T> {
    void onSubscribe(Subscription s);
    void onNext(T t);
    void onError(Throwable t);
    void onComplete();
}

// Управление подпиской (ключ к backpressure)
public interface Subscription {
    void request(long n);  // запросить n элементов
    void cancel();
}

// Одновременно Publisher и Subscriber (промежуточный оператор)
public interface Processor<T, R> extends Subscriber<T>, Publisher<R> {}
```

**Протокол взаимодействия:**
1. `Publisher.subscribe(subscriber)` — подписчик подключается к издателю.
2. `subscriber.onSubscribe(subscription)` — издатель передаёт подписчику объект `Subscription`.
3. `subscription.request(n)` — подписчик запрашивает `n` элементов (сигнал backpressure).
4. Издатель вызывает `subscriber.onNext(item)` не более `n` раз.
5. По завершении — `subscriber.onComplete()` или `subscriber.onError(e)`.

**Как WebFlux реализует backpressure**

Spring WebFlux принимает на вход любой `Publisher`, внутренне адаптирует его к типам Reactor (`Flux`/`Mono`) и использует механизм `request(n)` из Reactive Streams. WebFlux APIs accept a plain `Publisher` as input, adapt it to Reactor types internally and return either `Flux` or `Mono` as output.

Project Reactor реализует несколько стратегий обработки переполнения (`OverflowStrategy`):
- **BUFFER** — буферизует лишние элементы (риск OOM при неограниченном буфере).
- **DROP** — отбрасывает новые элементы, которые не удаётся обработать.
- **LATEST** — сохраняет только последний элемент, отбрасывая предыдущие необработанные.
- **ERROR** — выбрасывает `MissingBackpressureException` при переполнении.
- **IGNORE** — полностью игнорирует backpressure (небезопасно).

**Пример сценария без backpressure — проблема**

Представьте сервис, читающий данные из Kafka и отправляющий их клиенту. Kafka может отдавать 100 000 сообщений в секунду, а клиент через медленное соединение способен обрабатывать 1 000 в секунду.

```java
// Проблемный вариант — нет контроля давления
Flux.fromIterable(kafkaConsumer.poll(Duration.ofSeconds(1)).records("topic"))
    .map(record -> processRecord(record))
    // .subscribe() без request(n) — все элементы запрашиваются сразу (unbounded)
    .subscribe(result -> sendToSlowClient(result));
```

Без backpressure: производитель выдаёт все 100 000 элементов, они накапливаются в памяти, потребляя всё больше heap, что в итоге приводит к `OutOfMemoryError`.

```java
// Корректный вариант — явное управление давлением
Flux.fromIterable(...)
    .onBackpressureBuffer(1000,          // максимальный буфер
        dropped -> log.warn("Dropped: {}", dropped),
        BufferOverflowStrategy.DROP_OLDEST)
    .subscribe(new BaseSubscriber<Result>() {
        @Override
        protected void hookOnSubscribe(Subscription subscription) {
            request(50);  // запрашиваем начальную порцию
        }
        @Override
        protected void hookOnNext(Result value) {
            sendToClient(value);
            request(1);   // запрашиваем следующий элемент
        }
    });
```

Второй распространённый сценарий — HTTP-стриминг через Server-Sent Events: если клиент читает поток медленнее, чем сервер генерирует данные, WebFlux через TCP flow control и Reactor backpressure автоматически замедляет источник, предотвращая переполнение буферов на стороне сервера.

Дополнительный источник: [Backpressure Mechanism in Spring WebFlux — Baeldung](https://www.baeldung.com/spring-webflux-backpressure); [Java Reactive Streams — Baeldung](https://www.baeldung.com/java-9-reactive-streams)

---
### Вопрос 46. Чем WebClient отличается от RestTemplate и RestClient? Почему RestTemplate помечен как устаревший в Spring Framework 6/7, и какой HTTP-клиент рекомендуется для новых приложений Spring MVC, а какой — для WebFlux?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [REST Clients :: Spring Framework](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html)

Spring предоставляет три основных HTTP-клиента: `RestTemplate`, `RestClient` и `WebClient`.

**RestTemplate** — классический синхронный клиент, реализующий паттерн шаблонного метода. Начиная с Spring Framework 6.1, он больше не является рекомендуемым вариантом для новых разработок. Официальная документация гласит: «As of 6.1, RestClient offers a more modern API for synchronous HTTP access. For asynchronous and streaming scenarios, consider the reactive WebClient». RestTemplate и RestClient используют общую инфраструктуру (фабрики запросов, интерцепторы, конвертеры сообщений), однако именно RestClient является фокусом для новых высокоуровневых возможностей.

**RestClient** — современный синхронный HTTP-клиент с fluent API, появившийся в Spring Framework 6.1. Рекомендуется для новых приложений на базе Spring MVC:

```java
RestClient restClient = RestClient.builder()
    .baseUrl("https://example.com")
    .build();

Pet pet = restClient.get()
    .uri("/pets/{id}", id)
    .accept(APPLICATION_JSON)
    .retrieve()
    .body(Pet.class);
```

**WebClient** — неблокирующий реактивный клиент из Spring WebFlux. Рекомендуется для реактивных приложений и сценариев с потоковой передачей данных:

```java
WebClient webClient = WebClient.create("https://example.com");

Mono<Pet> pet = webClient.get()
    .uri("/pets/{id}", id)
    .retrieve()
    .bodyToMono(Pet.class);
```

**Рекомендации:**
- Spring MVC (блокирующий стек) → `RestClient`
- Spring WebFlux (реактивный стек) → `WebClient`
- Легаси-код → `RestTemplate` (с планом миграции на `RestClient`)

#### Ответ от Claude

**Три HTTP-клиента Spring: ключевые отличия**

| Характеристика | RestTemplate | RestClient | WebClient |
|---|---|---|---|
| Модель I/O | Синхронная, блокирующая | Синхронная, блокирующая | Асинхронная, неблокирующая |
| API-стиль | Шаблонные перегруженные методы | Fluent (цепочки вызовов) | Fluent, реактивный |
| Появился в | Spring 3.0 | Spring Framework 6.1 | Spring Framework 5.0 |
| Статус | Устаревает (не рекомендуется) | Рекомендован для MVC | Рекомендован для WebFlux |

**Почему RestTemplate устаревает**

Согласно официальному блогу Spring («The state of HTTP clients in Spring», сентябрь 2025), шаблонный подход RestTemplate имеет фундаментальные ограничения: большое количество перегруженных методов, сложность добавления современных возможностей (API versioning, streaming). В Spring Framework 6.1 появился RestClient с fluent API, который устраняет эти недостатки, сохраняя ту же инфраструктуру под капотом.

**Официальная хронология устаревания RestTemplate (по данным spring.io):**
- Spring Framework 6.1 (2023): RestClient как рекомендованная альтернатива; RestTemplate — «не рекомендуется для новых проектов»
- Spring Framework 7.1 (ноябрь 2026, плановая дата): формальная аннотация `@Deprecated`
- Spring Framework 8.0 (TBD): удаление класса

**Важное уточнение:** в Spring Framework 7.0.x аннотация `@Deprecated` на классе `RestTemplate` ещё **не проставлена** — только NOTE в Javadoc. Формальная пометка `@Deprecated` запланирована на версию 7.1. Поэтому корректнее говорить не «deprecated», а «не рекомендован для новых проектов, находится на пути к устареванию».

**Ключевые различия RestClient и WebClient**

`RestClient` работает поверх стандартного Java Servlet API (thread-per-request), подходит для классических Spring MVC приложений. Поддерживает настраиваемые HTTP-бэкенды: Apache HttpComponents, Jetty, JDK HttpClient.

`WebClient` основан на реактивном стеке Project Reactor + Netty, обрабатывает больше запросов при меньшем числе потоков за счёт неблокирующего I/O. Возвращает `Mono<T>` и `Flux<T>`. Технически может использоваться и в Spring MVC (блокирующий вызов через `.block()`), но это лишает преимуществ реактивности.

**Рекомендации для новых проектов (Spring Boot 3.x/4.x):**
- Spring MVC — использовать `RestClient` (автоконфигурируется через `RestClient.Builder`)
- Spring WebFlux — использовать `WebClient` (автоконфигурируется через `WebClient.Builder`)
- Декларативные клиенты — `@HttpExchange` + `HttpServiceProxyFactory` (работает поверх обоих)

---

### Вопрос 47. Как обработать ошибки в реактивной цепочке WebFlux? Сравните операторы onErrorReturn, onErrorResume и onErrorMap — когда применяется каждый из них?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Handling Errors :: Reactor Core Reference Guide](https://docs.spring.io/projectreactor/reactor-core/docs/3.7.0-M3/reference/html/coreFeatures/error-handling.html)

В Reactor (и, соответственно, в Spring WebFlux) ошибки являются терминальными событиями: при возникновении ошибки она прекращает выполнение последовательности и передаётся вниз по цепочке до ближайшего обработчика.

**onErrorReturn** — перехватывает ошибку и возвращает статическое значение по умолчанию:

```java
Flux.just(10)
    .map(this::doSomethingDangerous)
    .onErrorReturn("RECOVERED");
```

Эквивалент блока `try/catch`, возвращающего константу. Поддерживает предикат для выборочного перехвата.

**onErrorResume** — переключается на альтернативный Publisher при возникновении ошибки:

```java
Flux.just("key1", "key2")
    .flatMap(k -> callExternalService(k)
        .onErrorResume(e -> getFromCache(k))
    );
```

Позволяет выбирать разные стратегии восстановления в зависимости от типа ошибки:

```java
.onErrorResume(error -> {
    if (error instanceof TimeoutException)
        return getFromCache(k);
    else if (error instanceof UnknownKeyException)
        return registerNewEntry(k, "DEFAULT");
    else
        return Flux.error(error); // пробросить дальше
})
```

**onErrorMap** — трансформирует одно исключение в другое и продолжает распространение ошибки вниз:

```java
Flux.just("timeout1")
    .flatMap(k -> callExternalService(k))
    .onErrorMap(original ->
        new BusinessException("oops, SLA exceeded", original)
    );
```

Эквивалент `catch (e) { throw new BusinessException(e); }` — ошибка не подавляется, а оборачивается.

#### Ответ от Claude

**Модель ошибок в Project Reactor / WebFlux**

В реактивной цепочке ошибка — это терминальный сигнал `onError`. Upstream-последовательность прекращается, и ошибка распространяется вниз до обработчика. Если обработчика нет, она попадает в глобальный `DefaultUncaughtExceptionHandler` или возвращается клиенту (в WebFlux — как HTTP 500).

**Сравнение трёх операторов**

| Оператор | Что делает с ошибкой | Что возвращает | Когда использовать |
|---|---|---|---|
| `onErrorReturn` | Подавляет, заменяет значением | Одиночное значение типа T | Простой фоллбэк-константой |
| `onErrorResume` | Подавляет, заменяет другим Publisher | `Mono<T>` / `Flux<T>` | Сложная логика восстановления, условный фоллбэк |
| `onErrorMap` | Трансформирует, пробрасывает дальше | Новая ошибка | Перевод низкоуровневых исключений в доменные |

**onErrorReturn** — самый простой оператор:

```java
// Если сервис недоступен — вернуть пустой список
webClient.get().uri("/products")
    .retrieve()
    .bodyToFlux(Product.class)
    .onErrorReturn(new ArrayList<>());

// С фильтрацией по типу исключения
.onErrorReturn(WebClientResponseException.ServiceUnavailable.class,
    Collections.emptyList());
```

Под капотом — аналог `catch { return defaultValue; }`. Последовательность завершается нормально (`onComplete`).

**onErrorResume** — наиболее гибкий оператор:

```java
// Фоллбэк к кэшу при ошибке сети
webClient.get().uri("/user/{id}", id)
    .retrieve()
    .bodyToMono(User.class)
    .onErrorResume(WebClientRequestException.class,
        e -> cacheService.getUser(id));

// Условная логика: разные стратегии для разных ошибок
.onErrorResume(e -> {
    if (e instanceof WebClientResponseException ex
            && ex.getStatusCode().is4xxClientError()) {
        return Mono.just(User.anonymous()); // клиентская ошибка — анонимный пользователь
    }
    return Mono.error(e); // серверная ошибка — пробросить
});
```

Принимает `Function<Throwable, Publisher<T>>`, поэтому может возвращать и `Mono.just(value)`, и `Mono.empty()`, и даже `Mono.error(e)` (пробрасывание).

**onErrorMap** — оператор трансляции исключений:

```java
// Перевод технических исключений в доменные
webClient.post().uri("/orders")
    .bodyValue(orderRequest)
    .retrieve()
    .bodyToMono(Order.class)
    .onErrorMap(WebClientResponseException.Conflict.class,
        e -> new OrderAlreadyExistsException("Order conflict", e))
    .onErrorMap(WebClientResponseException.class,
        e -> new ExternalServiceException("HTTP error: " + e.getStatusCode(), e));
```

Ошибка **не подавляется** — она трансформируется и продолжает распространяться. Это ключевое отличие от `onErrorReturn` и `onErrorResume`.

**Комбинирование операторов**

Операторы можно объединять в цепочку:

```java
webClient.get().uri("/data")
    .retrieve()
    .bodyToMono(Data.class)
    .onErrorMap(IOException.class,
        e -> new ServiceUnavailableException(e))  // сначала транслируем
    .onErrorResume(ServiceUnavailableException.class,
        e -> fallbackService.getData());           // затем обрабатываем
```

**Дополнительные операторы для полноты картины**

- `doOnError(Consumer)` — side-effect (логирование) без изменения ошибки
- `onErrorComplete()` — подавляет ошибку и завершает последовательность (`onComplete`)
- `retry(n)` / `retryWhen(spec)` — повторная подписка при ошибке

**Практическое правило выбора:**
1. Нужен простой дефолт без логики → `onErrorReturn`
2. Нужен фоллбэк через другой сервис/кэш или условная логика → `onErrorResume`
3. Нужно обернуть техническое исключение в доменное (не подавляя ошибку) → `onErrorMap`

---

### Вопрос 48. Как работает DispatcherServlet в Spring MVC? Опишите последовательность обработки HTTP-запроса от его получения до отправки ответа.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [DispatcherServlet :: Spring Framework — docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-servlet.html)

`DispatcherServlet` реализует паттерн «фронт-контроллер» (Front Controller): он является центральным сервлетом Spring MVC, который предоставляет общий алгоритм обработки запросов, делегируя фактическую работу настраиваемым компонентам. Последовательность обработки запроса:

1. `WebApplicationContext` привязывается к запросу как атрибут под ключом `DispatcherServlet.WEB_APPLICATION_CONTEXT_ATTRIBUTE`, чтобы контроллеры и другие элементы процесса могли его использовать.
2. К запросу привязывается `LocaleResolver` — для определения локали при рендеринге представлений.
3. Если настроен `MultipartResolver`, запрос проверяется на наличие multipart-содержимого. При обнаружении он оборачивается в `MultipartHttpServletRequest`.
4. Ищется подходящий обработчик (handler). Если обработчик найден, выполняется цепочка исполнения (препроцессоры, постпроцессоры, контроллер) для подготовки модели для рендеринга. В случае аннотированных контроллеров ответ может быть сформирован прямо внутри `HandlerAdapter`.
5. Если возвращается модель — рендерится представление; если нет (из-за перехватчика или препроцессора) — рендеринг не происходит, ответ уже отправлен.

#### Ответ от Claude

**Паттерн фронт-контроллера**

`DispatcherServlet` — это обычный `HttpServlet`, зарегистрированный в контейнере сервлетов (Tomcat, Jetty). Он первым получает все HTTP-запросы, сопоставленные с его URL-паттерном (обычно `/` или `/*`), и оркестрирует их обработку.

**Полная последовательность обработки запроса**

```
Клиент → Tomcat/Jetty
  → [Servlet Filter цепочка]
    → DispatcherServlet.doDispatch(request, response)
      1. Поиск HandlerMapping → HandlerExecutionChain (handler + interceptors)
      2. Поиск HandlerAdapter для найденного handler
      3. Вызов interceptor.preHandle() для каждого перехватчика (в прямом порядке)
      4. HandlerAdapter.handle() → вызов метода контроллера → ModelAndView (или null)
      5. Вызов interceptor.postHandle() (в обратном порядке)
      6. Если ModelAndView != null → ViewResolver.resolveViewName() → View.render()
      7. Вызов interceptor.afterCompletion() (в обратном порядке)
      8. При исключении → HandlerExceptionResolver
```

**Ключевые компоненты (Special Beans)**

| Бин | Роль |
|-----|------|
| `HandlerMapping` | Маппинг запроса на handler + interceptors. По умолчанию `RequestMappingHandlerMapping` (обрабатывает `@RequestMapping`). |
| `HandlerAdapter` | Вызывает handler в нужном формате. `RequestMappingHandlerAdapter` умеет вызывать методы контроллера с аргументами (`@RequestBody`, `@PathVariable` и т.д.). |
| `ViewResolver` | Преобразует логическое имя представления в объект `View`. Не задействуется при `@ResponseBody`/`@RestController`. |
| `HandlerExceptionResolver` | Обрабатывает исключения из handler-методов. `ExceptionHandlerExceptionResolver` — для `@ExceptionHandler`. |
| `LocaleResolver` | Определяет текущую локаль. |
| `MultipartResolver` | Разбирает `multipart/form-data`-запросы. В Spring Boot с встроенным Tomcat настраивается автоматически. |

**Что происходит при `@RestController`**

При наличии `@ResponseBody` (или `@RestController`) шаг рендеринга представления полностью пропускается. `RequestMappingHandlerAdapter` использует `HttpMessageConverter` для сериализации возвращаемого объекта напрямую в тело ответа ещё на шаге 4. `ViewResolver` не вызывается.

**Инициализация DispatcherServlet**

При старте приложения `DispatcherServlet` инициализирует свой `WebApplicationContext` (дочерний от корневого контекста приложения) и выполняет `initStrategies()` — загружает все специальные бины из контекста или дефолтные из `DispatcherServlet.properties`.

---

### Вопрос 49. Для чего используется аннотация @RequestHeader в Spring MVC? Как прочитать один заголовок, несколько заголовков или все заголовки сразу?

**Категория:** REST/Web · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [@RequestHeader :: Spring Framework — docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/requestheader.html)

Аннотация `@RequestHeader` привязывает HTTP-заголовок запроса к параметру метода. При несовпадении типа выполняется автоматическое преобразование. Пример:

```java
@GetMapping("/demo")
public void handle(
    @RequestHeader("Accept-Encoding") String encoding,
    @RequestHeader("Keep-Alive") long keepAlive) {
    //...
}
```

Если параметр имеет тип `Map<String, String>`, `MultiValueMap<String, String>` или `HttpHeaders`, он будет заполнен всеми заголовками запроса. Заголовки с несколькими значениями, разделёнными запятой, могут быть преобразованы в массив или `List<String>`.

#### Ответ от Claude

**Назначение `@RequestHeader`**

Аннотация `@RequestHeader` позволяет извлечь значение HTTP-заголовка запроса и привязать его к параметру метода контроллера. Spring автоматически выполняет преобразование типов (String → int, long и т.д.).

**Чтение одного заголовка**

```java
@GetMapping("/api/data")
public ResponseEntity<Data> getData(
        @RequestHeader("X-API-Key") String apiKey,
        @RequestHeader("Accept-Language") String language) {
    // ...
}
```

Параметры `required` (по умолчанию `true`) и `defaultValue`:

```java
@RequestHeader(name = "X-Correlation-Id", required = false, defaultValue = "unknown")
String correlationId
```

**Чтение нескольких значений одного заголовка**

Некоторые заголовки могут содержать несколько значений через запятую (`Accept`, `Accept-Encoding`). Spring умеет раскладывать их в `List` или массив:

```java
@GetMapping("/headers")
public void handle(@RequestHeader("Accept") List<String> acceptTypes) {
    // Accept: text/html, application/json → [text/html, application/json]
}
```

**Чтение всех заголовков сразу**

```java
// Как Map (только первое значение каждого заголовка)
@RequestHeader Map<String, String> headers

// Как MultiValueMap (все значения каждого заголовка)
@RequestHeader MultiValueMap<String, String> headers

// Как HttpHeaders (типизированный доступ + удобные методы)
@RequestHeader HttpHeaders headers
String contentType = headers.getFirst(HttpHeaders.CONTENT_TYPE);
```

**Сравнение с `@RequestParam`:**

| Характеристика | `@RequestHeader` | `@RequestParam` |
|---|---|---|
| Источник | HTTP-заголовок запроса | Query string или form body |
| Регистрозависимость | Нечувствителен (HTTP-стандарт) | Чувствителен |
| Обязателен по умолчанию | Да (`required = true`) | Да |

**Практические сценарии:**
- Извлечение `Authorization: Bearer <token>` для аутентификации.
- Чтение `X-Correlation-Id` / `X-Request-Id` для трассировки.
- Проверка `Accept-Language` для локализации.
- Чтение `User-Agent` для аналитики клиентов.

---

### Вопрос 50. Как загрузить файл на сервер через Spring MVC REST API? Объясните роль MultipartFile, @RequestPart и MultipartResolver, и как обработать несколько файлов.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Multipart Requests :: Spring Framework — docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/multipart-forms.html)

После включения `MultipartResolver` POST-запросы с Content-Type `multipart/form-data` разбираются и доступны как обычные параметры запроса.

Простейший вариант — через `@RequestParam`:

```java
@PostMapping("/form")
public String handleFormUpload(@RequestParam("name") String name,
        @RequestParam("file") MultipartFile file) {
    if (!file.isEmpty()) {
        byte[] bytes = file.getBytes();
        return "redirect:uploadSuccess";
    }
    return "redirect:uploadFailure";
}
```

Для RESTful-сценариев со смешанным содержимым (JSON-метаданные + файл) используется `@RequestPart`:

```java
@PostMapping("/")
public String handle(@RequestPart("meta-data") MetaData metadata,
        @RequestPart("file-data") MultipartFile file) {
    // metadata автоматически десериализуется из JSON
}
```

`@RequestPart` отличается от `@RequestParam` тем, что использует `HttpMessageConverter` для преобразования части запроса с учётом Content-Type части (например, `application/json`), а не через `String`.

#### Ответ от Claude

**Как работает multipart-загрузка**

HTTP-запрос с `Content-Type: multipart/form-data` содержит несколько частей (parts), разделённых разделителем (boundary). Каждая часть имеет собственные заголовки (`Content-Disposition`, `Content-Type`) и тело (данные файла или текстовые поля).

**MultipartResolver**

В Spring MVC необходимо зарегистрировать бин `MultipartResolver`. Spring Boot с встроенным Tomcat делает это автоматически через `MultipartAutoConfiguration`, регистрируя `StandardServletMultipartResolver`. Размер файла и запроса настраивается через `application.properties`:

```properties
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=50MB
```

**Загрузка одного файла**

```java
@PostMapping("/upload")
public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) {
    if (file.isEmpty()) {
        return ResponseEntity.badRequest().body("Файл пуст");
    }
    String originalName = file.getOriginalFilename();
    long size = file.getSize();
    String contentType = file.getContentType();
    // Сохранение файла
    Files.write(Path.of("/uploads/" + originalName), file.getBytes());
    return ResponseEntity.ok("Загружено: " + originalName);
}
```

**Загрузка нескольких файлов**

```java
@PostMapping("/upload-multiple")
public ResponseEntity<List<String>> uploadMultiple(
        @RequestParam("files") List<MultipartFile> files) {
    List<String> names = files.stream()
        .filter(f -> !f.isEmpty())
        .map(f -> {
            // сохранение каждого файла
            return f.getOriginalFilename();
        })
        .collect(Collectors.toList());
    return ResponseEntity.ok(names);
}
```

**@RequestPart для JSON + файл (REST API паттерн)**

```java
@PostMapping(value = "/documents", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
public ResponseEntity<Document> upload(
        @RequestPart("metadata") DocumentMetadata metadata,  // Jackson десериализует из JSON-части
        @RequestPart("file") MultipartFile file) {
    Document doc = documentService.save(metadata, file);
    return ResponseEntity.created(URI.create("/documents/" + doc.getId())).body(doc);
}
```

Клиент отправляет:
```
Content-Type: multipart/form-data; boundary=----Boundary
------Boundary
Content-Disposition: form-data; name="metadata"
Content-Type: application/json

{"title": "Отчёт", "category": "finance"}
------Boundary
Content-Disposition: form-data; name="file"; filename="report.pdf"
Content-Type: application/pdf

... бинарные данные ...
```

**Разница `@RequestParam` vs `@RequestPart`:**

| Критерий | `@RequestParam` | `@RequestPart` |
|---|---|---|
| Преобразование содержимого | Через String | Через HttpMessageConverter (с учётом Content-Type части) |
| Поддержка JSON-десериализации | Нет | Да |
| Поддержка валидации (`@Valid`) | Нет | Да |
| Типичный сценарий | Простые формы | REST API, смешанный контент |

---

### Вопрос 51. Как работает асинхронная обработка запросов в Spring MVC через DeferredResult и Callable? В чём разница между ними и когда применяется каждый?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Asynchronous Requests :: Spring Framework — docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-async.html)

Spring MVC предоставляет три основных механизма асинхронной обработки.

**DeferredResult** возвращает результат, который будет получен асинхронно из другого потока:

```java
@GetMapping("/quotes")
@ResponseBody
public DeferredResult<String> quotes() {
    DeferredResult<String> deferredResult = new DeferredResult<>();
    // Сохраняем deferredResult где-то...
    return deferredResult;
}

// Из другого потока
deferredResult.setResult(result);
```

Используется, когда результат приходит от внешнего события (JMS, webhook, планировщик).

**Callable** оборачивает задачу для выполнения в отдельном потоке:

```java
@PostMapping
public Callable<String> processUpload(final MultipartFile file) {
    return () -> "someView";
}
```

Задача автоматически отправляется в `AsyncTaskExecutor`. Это самый простой подход для переноса блокирующей работы.

#### Ответ от Claude

**Проблема, которую решает асинхронная обработка**

В обычном Spring MVC каждый запрос занимает поток Tomcat (из пула) на всё время обработки. Если операция занимает несколько секунд (удалённый вызов, долгий запрос к БД), поток простаивает, удерживая ресурсы. Асинхронная обработка освобождает поток сервлет-контейнера на время ожидания.

**Callable — простейший async**

Контроллер возвращает `Callable<T>`. Spring вызывает `request.startAsync()`, задача отправляется в `AsyncTaskExecutor` (`ThreadPoolTaskExecutor`). Поток Tomcat освобождается. Когда `Callable` завершается, Spring возобновляет обработку в контексте запроса.

```java
@GetMapping("/report")
public Callable<Report> generateReport() {
    return () -> {
        // Выполняется в пуле потоков Spring, не в потоке Tomcat
        return reportService.generateHeavyReport(); // блокирующая операция
    };
}
```

Ограничение: задача должна завершиться внутри той же JVM, в собственном потоке Spring.

**DeferredResult — event-driven async**

`DeferredResult<T>` позволяет установить результат из любого потока в любое время, в том числе из обработчика сообщений, вебхука или другого сервиса.

```java
// Хранилище ожидающих запросов
private final Map<String, DeferredResult<Quote>> pendingResults = new ConcurrentHashMap<>();

@GetMapping("/quotes/{symbol}")
public DeferredResult<Quote> getQuote(@PathVariable String symbol) {
    DeferredResult<Quote> result = new DeferredResult<>(30_000L); // таймаут 30 с
    result.onTimeout(() -> result.setErrorResult(
        ResponseEntity.status(503).body("Timeout")));
    pendingResults.put(symbol, result);
    return result;
}

// Из JMS-обработчика или планировщика:
@JmsListener(destination = "quotes")
public void onQuote(Quote quote) {
    DeferredResult<Quote> result = pendingResults.remove(quote.getSymbol());
    if (result != null) {
        result.setResult(quote); // выполняет ответ клиенту
    }
}
```

**Сравнение подходов:**

| Характеристика | `Callable` | `DeferredResult` |
|---|---|---|
| Откуда приходит результат | Из задачи в пуле потоков Spring | Из любого внешнего потока/события |
| Управление потоком | Автоматически (Spring) | Вручную |
| Таймаут | Через `WebAsyncTask` | Конструктор `DeferredResult(timeout)` |
| Типичный сценарий | Перенос блокирующей I/O | Long-polling, JMS, внешние события |
| Колбэки | Нет | `onTimeout`, `onCompletion`, `onError` |

**Конфигурация async support:**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void configureAsyncSupport(AsyncSupportConfigurer configurer) {
        configurer.setDefaultTimeout(30_000);
        configurer.setTaskExecutor(asyncTaskExecutor());
    }
}
```

**Расхождение источников:** Baeldung описывает `DeferredResult` как способ «разгрузить вычисления на другой поток», однако главная ценность `DeferredResult` — не перенос работы, а возможность установить результат из внешней асинхронной системы. Для простого переноса блокирующей работы правильнее использовать `Callable`.

---

### Вопрос 52. Что такое Server-Sent Events (SSE)? Как реализовать стриминг событий с сервера на клиент в Spring MVC через SseEmitter и в Spring WebFlux через Flux?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Asynchronous Requests :: Spring Framework — Spring MVC SseEmitter](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-async.html)

`SseEmitter` — подкласс `ResponseBodyEmitter`, предоставляющий встроенную поддержку Server-Sent Events.

```java
@GetMapping(path="/events", produces=MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter handle() {
    SseEmitter emitter = new SseEmitter();
    // Сохраняем emitter где-то...
    return emitter;
}

// Из другого потока:
emitter.send("Hello once");
emitter.send("Hello again");
emitter.complete();
```

В Spring WebFlux аналогичный результат достигается через возврат `Flux` с медиатипом `text/event-stream`:

```java
@GetMapping(path="/events", produces=MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> handle() {
    // ...
}
```

#### Ответ от Claude

**Что такое Server-Sent Events (SSE)**

SSE — это стандарт HTML5 (`text/event-stream`), позволяющий серверу отправлять клиенту поток событий через одно долгоживущее HTTP-соединение. В отличие от WebSocket (двунаправленный), SSE — однонаправленный (сервер → клиент). Браузер поддерживает SSE через нативный `EventSource` API; при обрыве соединения браузер автоматически переподключается.

Формат события:
```
data: {"temp": 23.5}

event: alert
data: {"message": "Высокая температура"}
id: 42

```

Каждое событие отделяется пустой строкой.

**Spring MVC — SseEmitter**

`SseEmitter` удерживает HTTP-соединение открытым и позволяет отправлять события из другого потока:

```java
@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();

    @GetMapping(produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subscribe() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE); // без таймаута
        emitters.add(emitter);

        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));

        // Отправить приветственное событие
        executor.execute(() -> {
            try {
                emitter.send(SseEmitter.event()
                    .name("connected")
                    .data("{\"status\": \"subscribed\"}"));
            } catch (IOException e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }

    // Широковещательная рассылка события всем подписчикам
    public void broadcast(String eventName, Object data) {
        List<SseEmitter> dead = new ArrayList<>();
        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event().name(eventName).data(data));
            } catch (IOException e) {
                dead.add(emitter);
                emitter.completeWithError(e);
            }
        }
        emitters.removeAll(dead);
    }
}
```

**Spring WebFlux — Flux (рекомендуется)**

В WebFlux SSE реализуется нативно через `Flux` — никаких ручных потоков и управления соединениями:

```java
@RestController
@RequestMapping("/api/stream")
public class StreamController {

    @GetMapping(produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> streamEvents() {
        return Flux.interval(Duration.ofSeconds(1))
            .map(seq -> ServerSentEvent.<String>builder()
                .id(String.valueOf(seq))
                .event("periodic-event")
                .data("Событие #" + seq)
                .build());
    }

    // Или через простой Flux<T>:
    @GetMapping(value = "/simple", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> simpleStream() {
        return Flux.interval(Duration.ofSeconds(1))
            .map(i -> "Данные: " + i)
            .take(10); // ограничить 10 событиями
    }
}
```

**Сравнение подходов:**

| Критерий | Spring MVC + SseEmitter | Spring WebFlux + Flux |
|---|---|---|
| Модель потоков | Один поток на клиента (управляется вручную) | Событийный цикл (non-blocking) |
| Масштабируемость | Ограничена пулом потоков | Тысячи клиентов на небольшом числе потоков |
| Backpressure | Нет | Да (Reactive Streams) |
| Сложность кода | Выше (ручное управление emitter) | Ниже (декларативные операторы) |
| Рекомендация | Лёгкие сценарии или legacy MVC | Новые приложения, высокая нагрузка |

---

### Вопрос 53. Что такое ExchangeFilterFunction в Spring WebFlux WebClient? Как добавить логирование, аутентификацию или retry через фильтры?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [WebClient Filters — Baeldung](https://www.baeldung.com/spring-webclient-filters)

Фильтры `WebClient` позволяют перехватывать, проверять и модифицировать запросы и ответы клиента. Согласно статье: «Фильтр может перехватить, проверить и изменить клиентский запрос (или ответ)».

Фильтры реализуются через функциональный интерфейс `ExchangeFilterFunction`, принимающий два параметра: `ClientRequest` и следующий фильтр в цепочке. Для подключения фильтра необходимо использовать паттерн Builder:

```java
WebClient webClient = WebClient.builder()
    .filter(filterFunction)
    .build();
```

Метод `WebClient.create()` без Builder не поддерживает фильтры. Фильтры идеально подходят для сквозной функциональности, которую нужно применять ко всем запросам в одном месте.

#### Ответ от Claude

**Что такое ExchangeFilterFunction**

`ExchangeFilterFunction` — функциональный интерфейс Spring WebFlux, позволяющий перехватывать и модифицировать HTTP-запросы/ответы, выполняемые через `WebClient`. Это реактивный аналог сервлет-фильтра или `ClientHttpRequestInterceptor` в `RestTemplate`. Фильтры образуют цепочку: каждый фильтр получает запрос, может его изменить и передать следующему через `ExchangeFunction next`.

```java
@FunctionalInterface
public interface ExchangeFilterFunction {
    Mono<ClientResponse> filter(ClientRequest request, ExchangeFunction next);
}
```

**Подключение фильтров к WebClient**

```java
WebClient webClient = WebClient.builder()
    .baseUrl("https://api.example.com")
    .filter(loggingFilter())
    .filter(authFilter())
    .filter(retryFilter())
    .build();
```

**Фильтр логирования запросов**

```java
private ExchangeFilterFunction loggingFilter() {
    return ExchangeFilterFunction.ofRequestProcessor(request -> {
        log.info("Request: {} {}", request.method(), request.url());
        request.headers().forEach((name, values) ->
            values.forEach(value -> log.debug("Header: {}={}", name, value)));
        return Mono.just(request);
    });
}
```

Для логирования и запроса, и ответа:

```java
private ExchangeFilterFunction loggingFilter() {
    return (request, next) -> {
        log.info(">>> {} {}", request.method(), request.url());
        return next.exchange(request)
            .doOnNext(response ->
                log.info("<<< Status: {}", response.statusCode()));
    };
}
```

**Фильтр аутентификации (Bearer Token)**

```java
private ExchangeFilterFunction authFilter(String token) {
    return ExchangeFilterFunction.ofRequestProcessor(request -> {
        ClientRequest authenticatedRequest = ClientRequest.from(request)
            .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
            .build();
        return Mono.just(authenticatedRequest);
    });
}
```

Для Basic Auth доступен встроенный метод:

```java
WebClient.builder()
    .filter(ExchangeFilterFunctions.basicAuthentication("user", "password"))
    .build();
```

**Фильтр retry**

```java
private ExchangeFilterFunction retryFilter() {
    return (request, next) ->
        next.exchange(request)
            .flatMap(response -> {
                if (response.statusCode().is5xxServerError()) {
                    return Mono.error(new RuntimeException("Server error"));
                }
                return Mono.just(response);
            })
            .retry(3);
}
```

Или через `retryWhen` с экспоненциальным backoff:

```java
.retryWhen(Retry.backoff(3, Duration.ofSeconds(1))
    .filter(e -> e instanceof WebClientResponseException ex
        && ex.getStatusCode().is5xxServerError()))
```

**Порядок фильтров**: фильтры применяются в порядке регистрации (первый зарегистрированный — первый в цепочке). Это важно: фильтр логирования лучше регистрировать первым, чтобы видеть финальный запрос после применения всех модификаций.

---

### Вопрос 54. Как документировать REST API в Spring Boot с помощью springdoc-openapi? Какие ключевые аннотации используются и где доступна сгенерированная документация?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [springdoc-openapi — springdoc.org](https://springdoc.org/)

Для интеграции springdoc-openapi в Spring Boot добавьте зависимость:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.17</version>
</dependency>
```

После добавления зависимости документация автоматически генерируется и становится доступна по адресам:
- Swagger UI: `http://server:port/swagger-ui.html`
- JSON-спецификация: `http://server:port/v3/api-docs`
- YAML-спецификация: `http://server:port/v3/api-docs.yaml`

Ключевые аннотации: `@Operation` (описание endpoint), `@ApiResponse` (возможные ответы), `@Schema` (описание модели данных), `@Parameter` (параметры метода), `@Tag` (группировка операций).

#### Ответ от Claude

**Что такое springdoc-openapi**

springdoc-openapi — библиотека, автоматически генерирующая документацию OpenAPI 3.x для Spring Boot приложений, анализируя аннотации Spring MVC/WebFlux (`@RestController`, `@RequestMapping` и т.д.) в runtime. Это самый распространённый инструмент документирования REST API в экосистеме Spring Boot 3.x (преемник Springfox).

**Подключение**

```xml
<!-- Spring Boot 3.x (MVC) -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.17</version>
</dependency>

<!-- Spring Boot 3.x (WebFlux) -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webflux-ui</artifactId>
    <version>2.8.17</version>
</dependency>
```

**Глобальные метаданные API**

```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("User Management API")
                .version("2.0.0")
                .description("REST API для управления пользователями")
                .contact(new Contact().email("api@example.com")))
            .addSecurityItem(new SecurityRequirement().addList("BearerAuth"))
            .components(new Components().addSecuritySchemes("BearerAuth",
                new SecurityScheme().type(SecurityScheme.Type.HTTP)
                    .scheme("bearer").bearerFormat("JWT")));
    }
}
```

**Аннотации на контроллере**

```java
@Tag(name = "Users", description = "Операции с пользователями")
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Operation(summary = "Получить пользователя по ID",
               description = "Возвращает полные данные пользователя")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Пользователь найден",
            content = @Content(schema = @Schema(implementation = User.class))),
        @ApiResponse(responseCode = "404", description = "Пользователь не найден",
            content = @Content(schema = @Schema(implementation = ProblemDetail.class)))
    })
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(
            @Parameter(description = "ID пользователя", example = "42")
            @PathVariable Long id) {
        return ResponseEntity.of(userService.findById(id));
    }
}
```

**Аннотации на модели**

```java
@Schema(description = "Данные пользователя")
public class User {
    @Schema(description = "Уникальный идентификатор", example = "42", readOnly = true)
    private Long id;

    @Schema(description = "Email адрес", example = "user@example.com", required = true)
    @NotBlank
    private String email;
}
```

**Конфигурация через application.properties**

```properties
# Путь к Swagger UI
springdoc.swagger-ui.path=/docs
# Путь к JSON-спецификации
springdoc.api-docs.path=/api-docs
# Сканировать только определённые пакеты
springdoc.packagesToScan=com.example.api
# Отключить документацию в production
springdoc.api-docs.enabled=false
```

**Важно:** springdoc-openapi автоматически распознаёт аннотации Jakarta Validation (`@NotBlank`, `@Size`, `@Min`) и включает ограничения в схемы моделей без дополнительных настроек.

---

### Вопрос 55. Что такое @HttpExchange в Spring Framework 6? Как создать декларативный HTTP-клиент через @GetExchange/@PostExchange и HttpServiceProxyFactory?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [HTTP Interface Clients :: Spring Framework](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html#rest-http-interface)

`@HttpExchange` — аннотация Spring Framework 6, позволяющая объявить HTTP-клиент в виде Java-интерфейса, а не писать boilerplate-код. Конкретные аннотации HTTP-методов: `@GetExchange`, `@PostExchange`, `@PutExchange`, `@PatchExchange`, `@DeleteExchange`.

Пример интерфейса:

```java
public interface RepositoryService {
    @GetExchange("/repos/{owner}/{repo}")
    Repository getRepository(@PathVariable String owner, @PathVariable String repo);
}
```

Создание клиентского прокси через `HttpServiceProxyFactory`:

```java
RestClient restClient = RestClient.create("https://api.github.com/");
RestClientAdapter adapter = RestClientAdapter.create(restClient);
HttpServiceProxyFactory factory = HttpServiceProxyFactory.builderFor(adapter).build();
RepositoryService service = factory.createClient(RepositoryService.class);
```

#### Ответ от Claude

**Концепция декларативных HTTP-клиентов**

`@HttpExchange` (Spring Framework 6, Spring Boot 3) — это аналог Feign/OpenFeign: вместо того чтобы вручную вызывать `WebClient` или `RestClient`, разработчик объявляет интерфейс с аннотированными методами, а Spring создаёт реализацию-прокси автоматически. Декларативный подход уменьшает boilerplate, делает код читаемым и тестируемым.

**Объявление интерфейса**

```java
// Общие атрибуты можно задать на уровне интерфейса
@HttpExchange(url = "https://api.github.com", accept = "application/vnd.github.v3+json")
public interface GitHubService {

    @GetExchange("/repos/{owner}/{repo}")
    Repository getRepository(@PathVariable String owner, @PathVariable String repo);

    @GetExchange("/repos/{owner}/{repo}/issues")
    List<Issue> getIssues(@PathVariable String owner, @PathVariable String repo,
                          @RequestParam(required = false) String state);

    @PostExchange("/repos/{owner}/{repo}/issues")
    Issue createIssue(@PathVariable String owner, @PathVariable String repo,
                      @RequestBody CreateIssueRequest request);

    @DeleteExchange("/repos/{owner}/{repo}/issues/{number}")
    ResponseEntity<Void> deleteIssue(@PathVariable String owner,
                                     @PathVariable String repo,
                                     @PathVariable int number);
}
```

**Создание прокси через RestClient (синхронный стек)**

```java
@Configuration
public class HttpClientsConfig {

    @Bean
    public GitHubService gitHubService() {
        RestClient restClient = RestClient.builder()
            .baseUrl("https://api.github.com")
            .defaultHeader("Authorization", "Bearer " + githubToken)
            .build();
        RestClientAdapter adapter = RestClientAdapter.create(restClient);
        HttpServiceProxyFactory factory = HttpServiceProxyFactory
            .builderFor(adapter).build();
        return factory.createClient(GitHubService.class);
    }
}
```

**Создание прокси через WebClient (реактивный стек)**

```java
@Bean
public GitHubService gitHubServiceReactive() {
    WebClient webClient = WebClient.builder()
        .baseUrl("https://api.github.com")
        .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
        .build();
    WebClientAdapter adapter = WebClientAdapter.create(webClient);
    HttpServiceProxyFactory factory = HttpServiceProxyFactory
        .builderFor(adapter).build();
    return factory.createClient(GitHubService.class);
}
```

**Поддерживаемые параметры методов**

| Аннотация | Источник данных |
|---|---|
| `@PathVariable` | Переменные пути URI |
| `@RequestParam` | Query-параметры или form data |
| `@RequestHeader` | Заголовки запроса |
| `@RequestBody` | Тело запроса |
| `@RequestPart` | Части multipart-запроса |
| `@CookieValue` | Куки |

**Поддерживаемые возвращаемые типы:**

- `void`, `T`, `ResponseEntity<T>` — синхронно (RestClient)
- `Mono<T>`, `Flux<T>`, `Mono<ResponseEntity<T>>` — реактивно (WebClient)

**Сравнение с RestTemplate / RestClient / WebClient:**

| Аспект | Imperative (`RestClient`) | Declarative (`@HttpExchange`) |
|---|---|---|
| Boilerplate | Больше | Минимум |
| Читаемость | Умеренная | Высокая |
| Мок в тестах | Через Mockito MockBean | Стандартный Mockito/Mockbean |
| Гибкость | Максимальная | Ограничена аннотациями |

---

### Вопрос 56. Как работает CSRF-защита в Spring Security для REST API? Когда её следует включать, а когда отключать, и как это влияет на stateless-приложения?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CSRF :: Spring Security](https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html)

CSRF (Cross-Site Request Forgery) — атака, при которой злоумышленник заставляет аутентифицированного пользователя выполнить нежелательное действие на сайте. Spring Security включает CSRF-защиту по умолчанию.

Механизм защиты: сервер генерирует уникальный токен, который включается в каждый HTML-ответ. Клиент обязан включать этот токен в каждый изменяющий состояние запрос (POST, PUT, DELETE, PATCH). Злоумышленник с другого домена не может получить токен — атака невозможна.

Для REST API с JWT-аутентификацией CSRF-защита, как правило, не нужна: злоумышленник не может получить JWT из другого домена (при правильном хранении в памяти или `Authorization` заголовке, а не в cookie). При хранении сессий в cookie CSRF-защита обязательна.

#### Ответ от Claude

**Как работает CSRF-атака**

Сценарий атаки: пользователь аутентифицирован на `bank.com` (сессия в cookie). Злоумышленник заманивает его на `evil.com`, где скрытая форма отправляет POST-запрос на `bank.com/transfer?to=attacker&amount=1000`. Браузер автоматически прикрепляет cookie сессии к запросу — сервер принимает запрос как легитимный.

**Почему это работает:** браузер автоматически отправляет cookie для домена назначения, независимо от источника запроса.

**Механизм защиты Spring Security**

Spring Security использует паттерн Synchronizer Token:
1. При загрузке страницы генерируется случайный `CsrfToken` и сохраняется в сессии (или cookie).
2. Токен вставляется в HTML-форму или передаётся через cookie/заголовок.
3. При каждом изменяющем запросе (POST, PUT, DELETE, PATCH) сервер сравнивает токен из запроса с сохранённым. Злоумышленник не может воспроизвести токен.

**Когда CSRF-защита нужна**

- **Stateful приложения с сессиями в cookie** — веб-приложения на Thymeleaf/JSP, где аутентификация через cookie-сессию. Spring Security автоматически вставляет токен в формы.
- **API, вызываемые браузером** с cookie-аутентификацией.

**Когда CSRF-защиту отключают**

Для **stateless REST API** с JWT-аутентификацией CSRF-защита избыточна:
- JWT передаётся в заголовке `Authorization: Bearer <token>`.
- Браузер не отправляет заголовок `Authorization` автоматически — только cookie.
- Злоумышленник с `evil.com` не может включить чужой JWT в запрос.

Отключение:

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .csrf(AbstractHttpConfigurer::disable) // отключаем для JWT API
        .sessionManagement(session ->
            session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .authorizeHttpRequests(auth ->
            auth.requestMatchers("/api/**").authenticated());
    return http.build();
}
```

**Если REST API использует cookie-сессию (гибридный сценарий)**

Используйте `CookieCsrfTokenRepository` — токен передаётся в cookie (`XSRF-TOKEN`), JavaScript читает его и включает в заголовок (`X-XSRF-TOKEN`):

```java
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
    .csrfTokenRequestHandler(new XorCsrfTokenRequestAttributeHandler()));
```

**Итоговое правило выбора:**

| Тип API | Хранение аутентификации | CSRF нужен? |
|---|---|---|
| Веб-приложение (MVC + Thymeleaf) | Session cookie | Да |
| REST API + JWT | Authorization header | Нет |
| REST API + session cookie | Session cookie | Да |
| REST API + `HttpOnly` cookie с JWT | Cookie | Да |

---

### Вопрос 57. Как настроить HandlerInterceptor в Spring MVC? Чем он отличается от Servlet Filter, и как реализовать логирование времени выполнения запроса?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [HandlerInterceptor — Baeldung](https://www.baeldung.com/spring-mvc-handlerinterceptor)

`HandlerInterceptor` предоставляет три метода жизненного цикла обработки запроса:

1. **`preHandle()`** — выполняется до вызова метода-обработчика. Возвращает `boolean`: `true` продолжает обработку, `false` останавливает.
2. **`postHandle()`** — выполняется после обработчика, но до рендеринга представления. Позволяет добавить атрибуты в `ModelAndView`.
3. **`afterCompletion()`** — срабатывает после завершения запроса и рендеринга представления. Подходит для очистки ресурсов и обработки исключений.

Для регистрации перехватчика нужно переопределить `addInterceptors()` в конфигурационном классе:

```java
@Override
public void addInterceptors(InterceptorRegistry registry) {
    registry.addInterceptor(new LoggerInterceptor());
}
```

`HandlerInterceptorAdapter` устарел с версии 5.3 — следует реализовывать `HandlerInterceptor` напрямую. При нескольких перехватчиках: `preHandle` выполняется в прямом порядке, `postHandle` и `afterCompletion` — в обратном.

#### Ответ от Claude

**HandlerInterceptor vs Servlet Filter**

| Характеристика | Servlet Filter | HandlerInterceptor |
|---|---|---|
| Уровень | Servlet Container (до Spring) | Spring MVC (после DispatcherServlet) |
| Доступ к Spring-контексту | Ограничен (только через `@Autowired` при `DelegatingFilterProxy`) | Полный (это Spring-бин) |
| Знает о handler | Нет | Да (`HandlerMethod`) |
| Доступ к ModelAndView | Нет | Да (в `postHandle`) |
| Типичные задачи | Аутентификация, CORS, кодировка, сжатие | Логирование, авторизация по handler, добавление данных в модель |

**Реализация перехватчика для измерения времени выполнения**

```java
@Component
public class TimingInterceptor implements HandlerInterceptor {

    private static final Logger log = LoggerFactory.getLogger(TimingInterceptor.class);
    private static final String ATTR_START = "requestStart";

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        if (handler instanceof HandlerMethod hm) {
            log.info(">>> {} {} — {}.{}()",
                request.getMethod(), request.getRequestURI(),
                hm.getBeanType().getSimpleName(), hm.getMethod().getName());
        }
        request.setAttribute(ATTR_START, System.currentTimeMillis());
        return true; // продолжаем обработку
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler,
                                Exception ex) {
        Long start = (Long) request.getAttribute(ATTR_START);
        if (start != null) {
            long elapsed = System.currentTimeMillis() - start;
            log.info("<<< {} {} → {} | {}ms",
                request.getMethod(), request.getRequestURI(),
                response.getStatus(), elapsed);
        }
    }
}
```

**Регистрация перехватчика**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final TimingInterceptor timingInterceptor;

    public WebConfig(TimingInterceptor timingInterceptor) {
        this.timingInterceptor = timingInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(timingInterceptor)
            .addPathPatterns("/api/**")           // применять только к /api/**
            .excludePathPatterns("/api/health");  // исключить endpoint здоровья
    }
}
```

**Почему `afterCompletion`, а не `postHandle`, для измерения времени?**

`postHandle` не вызывается, если handler бросил исключение. `afterCompletion` вызывается **всегда** (даже при исключении), что гарантирует запись времени независимо от результата обработки.

**Порядок выполнения при нескольких перехватчиках**

```
preHandle(A) → preHandle(B) → preHandle(C)
    → handler()
postHandle(C) → postHandle(B) → postHandle(A)
afterCompletion(C) → afterCompletion(B) → afterCompletion(A)
```

Если `preHandle(B)` вернул `false`, то `afterCompletion` вызывается только для перехватчиков, чей `preHandle` вернул `true` (A в данном примере).

---

### Вопрос 58. Как реализовать кэширование HTTP-ответов через заголовки ETag и Cache-Control в Spring MVC? Как работает механизм условных запросов?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [HTTP Caching :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-caching.html)

Spring MVC поддерживает HTTP-кэширование через несколько механизмов. Наиболее распространённый — использование `WebRequest.checkNotModified()`:

```java
@GetMapping("/book/{id}")
public ResponseEntity<Book> getBook(@PathVariable Long id, WebRequest request) {
    Book book = bookService.getBook(id);
    String etag = "\"" + book.getVersion() + "\"";
    if (request.checkNotModified(etag)) {
        return null; // Spring вернёт 304 Not Modified
    }
    return ResponseEntity.ok()
        .eTag(etag)
        .cacheControl(CacheControl.maxAge(60, TimeUnit.SECONDS))
        .body(book);
}
```

`CacheControl` предоставляет fluent API для формирования заголовка `Cache-Control`. `ShallowEtagHeaderFilter` (встроенный фильтр) может автоматически генерировать ETag на основе MD5-хеша тела ответа.

#### Ответ от Claude

**Основы HTTP-кэширования**

HTTP-кэширование снижает нагрузку на сервер и уменьшает задержку для клиента. Два основных механизма:

1. **Cache-Control** — определяет политику кэширования (срок жизни, доступность, условия).
2. **ETag / Last-Modified** — условные запросы; клиент проверяет, изменился ли ресурс, прежде чем скачивать его заново.

**Cache-Control в Spring MVC**

```java
@GetMapping("/products")
public ResponseEntity<List<Product>> getProducts() {
    List<Product> products = productService.findAll();
    return ResponseEntity.ok()
        .cacheControl(CacheControl
            .maxAge(5, TimeUnit.MINUTES)   // кэшировать 5 минут
            .cachePublic()                  // разрешить прокси-кэши
            .noTransform())                 // не модифицировать кэш-серверам
        .body(products);
}
```

Ключевые директивы `Cache-Control`:
- `max-age=N` — ресурс актуален N секунд.
- `no-cache` — кэшировать, но перед использованием проверять у сервера.
- `no-store` — не кэшировать вообще.
- `public` — можно кэшировать на прокси.
- `private` — только в браузере пользователя.

**ETag и условные запросы**

ETag — уникальный идентификатор версии ресурса (хеш, версия из БД, timestamp).

**Сценарий работы:**

```
1. Клиент: GET /books/1
   Сервер: 200 OK + ETag: "v42" + Content-Type: ... + body

2. Клиент: GET /books/1
   Заголовок: If-None-Match: "v42"
   → Сервер проверяет: ETag совпадает?
   → Да: 304 Not Modified (без тела → экономия трафика)
   → Нет: 200 OK + ETag: "v43" + новое тело
```

**Реализация через ShallowEtagHeaderFilter (автоматический ETag)**

```java
@Bean
public ShallowEtagHeaderFilter shallowEtagHeaderFilter() {
    return new ShallowEtagHeaderFilter();
}
```

Фильтр автоматически вычисляет MD5-хеш тела ответа и проставляет `ETag`. При совпадении с `If-None-Match` возвращает `304`. Недостаток: тело всё равно генерируется на сервере — экономится только трафик, не вычисления.

**Реализация через WebRequest.checkNotModified() (семантический ETag)**

```java
@GetMapping("/orders/{id}")
public ResponseEntity<Order> getOrder(@PathVariable Long id, WebRequest request) {
    Order order = orderService.findById(id);
    String etag = "\"" + order.getUpdatedAt().toEpochSecond() + "\"";

    // checkNotModified устанавливает нужные заголовки и возвращает true,
    // если клиент уже имеет актуальную версию
    if (request.checkNotModified(etag)) {
        return null; // DispatcherServlet вернёт 304
    }

    return ResponseEntity.ok()
        .eTag(etag)
        .cacheControl(CacheControl.maxAge(10, TimeUnit.MINUTES))
        .body(order);
}
```

Преимущество: `checkNotModified` работает с реальной версией данных — серверные вычисления (запрос к БД) можно пропустить, если ETag совпал ещё на уровне идентификатора.

**Last-Modified и If-Modified-Since**

Альтернатива ETag: сервер возвращает `Last-Modified`, клиент при повторном запросе отправляет `If-Modified-Since`:

```java
if (request.checkNotModified(order.getUpdatedAt().toEpochMilli())) {
    return null; // 304 если не изменился
}
```

---

### Вопрос 59. Что такое @CrossOrigin в Spring MVC? Чем локальная аннотация на контроллере отличается от глобальной конфигурации CORS, и как добавить собственный заголовок в список allowed headers?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CORS :: Spring Framework — @CrossOrigin](https://docs.spring.io/spring-framework/reference/web/webmvc-cors.html)

`@CrossOrigin` на уровне метода или класса контроллера разрешает запросы из других источников для аннотированных обработчиков. По умолчанию `@CrossOrigin` разрешает все источники, методы и заголовки. Атрибуты можно ограничить:

```java
@CrossOrigin(origins = "https://domain2.com", maxAge = 3600)
@RestController
@RequestMapping("/account")
public class AccountController {

    @CrossOrigin("https://domain3.com")
    @GetMapping("/{id}")
    public Account retrieve(@PathVariable Long id) { ... }
}
```

Метод `retrieve()` наследует конфигурацию класса и добавляет свою. Глобальная конфигурация CORS задаётся через `WebMvcConfigurer.addCorsMappings()`.

#### Ответ от Claude

**Как работает CORS в Spring**

CORS (Cross-Origin Resource Sharing) — механизм браузера для контроля запросов к другому домену. Spring MVC обрабатывает CORS через `CorsProcessor` (по умолчанию `DefaultCorsProcessor`), встроенный в `HandlerMapping`. CORS-конфигурация объединяется из нескольких источников.

**@CrossOrigin — локальная конфигурация**

```java
@CrossOrigin(
    origins = {"https://app.example.com", "https://admin.example.com"},
    methods = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT},
    allowedHeaders = {"Authorization", "Content-Type", "X-Custom-Header"},
    exposedHeaders = {"X-Total-Count", "X-Request-Id"},
    allowCredentials = "true",
    maxAge = 3600
)
@RestController
@RequestMapping("/api/products")
public class ProductController { ... }
```

**Глобальная конфигурация через WebMvcConfigurer**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.example.com")
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("Authorization", "Content-Type", "X-Custom-Header")
            .exposedHeaders("X-Total-Count")
            .allowCredentials(true)
            .maxAge(3600);

        // Для публичных эндпоинтов — все источники
        registry.addMapping("/api/public/**")
            .allowedOriginPatterns("*")
            .allowedMethods("GET");
    }
}
```

**Разница между локальной и глобальной конфигурацией:**

| Аспект | `@CrossOrigin` | `addCorsMappings()` |
|---|---|---|
| Область | Один контроллер / метод | Все маппинги (по паттерну) |
| Гибкость | Высокая (на уровне метода) | Высокая (по URL-паттерну) |
| Дублирование | Может быть много аннотаций | Один класс конфигурации |
| Приоритет при совпадении | Объединяется с глобальной | Базовая конфигурация |

Spring **объединяет** локальную и глобальную конфигурации. Например, если глобально разрешены origins `["https://app.com"]`, а метод добавляет `@CrossOrigin("https://admin.com")`, в итоге разрешены оба источника.

**Добавление произвольного заголовка в allowed headers**

```java
// Через @CrossOrigin
@CrossOrigin(allowedHeaders = {"Authorization", "Content-Type", "X-Correlation-Id"})

// Через WebMvcConfigurer
registry.addMapping("/**").allowedHeaders("X-Correlation-Id", "X-API-Version");
```

Важно: заголовки, которые JavaScript должен **читать** из ответа, указываются в `exposedHeaders` (по умолчанию браузер скрывает все нестандартные заголовки ответа):

```java
.exposedHeaders("X-Total-Count", "X-Request-Id", "Location")
```

**Частая ошибка:** использование `allowedOriginPatterns("*")` вместо `allowedOrigins("*")` при включённом `allowCredentials(true)`. Комбинация `allowedOrigins("*") + allowCredentials(true)` нелегальна по спецификации и вызовет ошибку Spring — используйте паттерны.

---

### Вопрос 60. Что такое WebTestClient в Spring? Как его использовать для интеграционного тестирования REST API в Spring Boot — с реальным сервером и без него?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [WebTestClient :: Spring Framework — docs.spring.io](https://docs.spring.io/spring-framework/reference/testing/webtestclient.html)

`WebTestClient` — HTTP-клиент для тестирования веб-серверов. Он является обёрткой над `WebClient`, добавляющей методы для верификации ответов. Используется для end-to-end HTTP-тестирования с реальным сервером или тестирования Spring MVC/WebFlux-приложений через мок-сервер без настоящей HTTP-инфраструктуры.

Три варианта настройки:

1. **Подключение к реальному серверу** (потребуется `spring-test` и `spring-webflux`):
```java
client = WebTestClient.bindToServer()
    .baseUrl("http://localhost:8080")
    .build();
```

2. **Тестирование через RouterFunction (WebFlux):**
```java
RouterFunction<ServerResponse> route = ...
client = WebTestClient.bindToRouterFunction(route).build();
```

3. **Тестирование через ApplicationContext:**
```java
@SpringBootTest
class MyTests {
    @Autowired
    private WebTestClient webTestClient;
}
```

#### Ответ от Claude

**Что такое WebTestClient**

`WebTestClient` (из `spring-webflux`) — специализированный HTTP-клиент для тестирования, объединяющий возможности `WebClient` с fluent API верификации ответов. Подходит как для Spring MVC, так и для Spring WebFlux-приложений.

**Режим 1: MockMvc-подобное тестирование (без HTTP-стека)**

Для Spring MVC приложений — тест через `MockMvc` под капотом, без запуска реального сервера. Самый быстрый режим:

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {

    @Autowired
    private WebApplicationContext context;

    private WebTestClient client;

    @BeforeEach
    void setUp() {
        client = MockMvcWebTestClient.bindToApplicationContext(context)
            .apply(springSecurity()) // подключить Spring Security
            .build();
    }

    @Test
    void getUser_shouldReturn200() {
        client.get().uri("/api/users/{id}", 1L)
            .header("Authorization", "Bearer " + validToken)
            .exchange()
            .expectStatus().isOk()
            .expectHeader().contentType(MediaType.APPLICATION_JSON)
            .expectBody(User.class)
            .value(user -> {
                assertThat(user.getId()).isEqualTo(1L);
                assertThat(user.getEmail()).isNotBlank();
            });
    }
}
```

**Режим 2: Тест с реальным embedded-сервером**

Запускает встроенный Tomcat/Netty на случайном порту — полноценный интеграционный тест:

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserApiIntegrationTest {

    @Autowired
    private WebTestClient client;

    @Test
    void createUser_shouldReturn201WithLocation() {
        CreateUserRequest request = new CreateUserRequest("test@example.com", "Ivan");

        client.post().uri("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .exchange()
            .expectStatus().isCreated()
            .expectHeader().exists("Location")
            .expectBody()
            .jsonPath("$.id").isNotEmpty()
            .jsonPath("$.email").isEqualTo("test@example.com");
    }
}
```

**Проверка тела ответа — ключевые методы**

```java
.expectBody(User.class)
    .value(user -> assertThat(user.getEmail()).endsWith("@example.com"))

// Или через JSON Path
.expectBody()
    .jsonPath("$.items.length()").isEqualTo(3)
    .jsonPath("$.items[0].status").isEqualTo("ACTIVE")

// Список объектов
.expectBodyList(Product.class)
    .hasSize(5)
    .contains(expectedProduct)

// Пустое тело (204 No Content)
.expectBody().isEmpty()
```

**Тестирование ошибок валидации**

```java
@Test
void createUser_withInvalidEmail_shouldReturn400() {
    client.post().uri("/api/users")
        .contentType(MediaType.APPLICATION_JSON)
        .bodyValue(Map.of("email", "not-an-email", "name", "Ivan"))
        .exchange()
        .expectStatus().isBadRequest()
        .expectBody()
        .jsonPath("$.title").isEqualTo("Bad Request")
        .jsonPath("$.violations[0].field").isEqualTo("email");
}
```

**Сравнение подходов тестирования:**

| Подход | Скорость | HTTP-стек | Когда использовать |
|---|---|---|---|
| `MockMvc` (классический) | Быстрый | Нет | Unit-тесты контроллеров |
| `WebTestClient` + MockMvc | Быстрый | Нет | То же, но fluent API WebTestClient |
| `WebTestClient` + embedded server | Медленнее | Да | Интеграционные тесты с реальным HTTP |
| `WebTestClient` + реальный сервер | Самый медленный | Да | E2E тесты |

---
