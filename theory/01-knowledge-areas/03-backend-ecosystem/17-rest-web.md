# REST, HTTP и веб-слой

> **Уровень:** Middle
> **Связанные вопросы:** [Вопросы по REST и web →](../../../interview-questions/rest-web-01.md)
> **Связанные области:** [[14-spring-boot]], [[23-security]], [[20-microservices]]

## Что это и зачем

Большинство современных Java-сервисов общаются по HTTP через REST API. Нужно понимать протокол HTTP
(методы, коды статусов, заголовки), принципы REST, сериализацию JSON, а также реализацию веб-слоя
в Spring (Spring MVC и реактивный WebFlux). Это основной интерфейс взаимодействия микросервисов и
клиентов с backend.

HTTP является протоколом прикладного уровня без сохранения состояния (stateless). Сервер не хранит
информацию о предыдущих запросах клиента — каждый запрос самодостаточен. REST (Representational State
Transfer) — архитектурный стиль, предложенный Роем Филдингом в диссертации 2000 года, который
использует возможности HTTP по назначению: методы для операций, коды статусов для результатов,
заголовки для метаданных.

## Ключевые подтемы

### HTTP-методы: идемпотентность и безопасность

Источник: [MDN — HTTP методы](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods).

Два ключевых свойства метода:

- **Safe (безопасный)** — метод не изменяет состояние сервера. Только чтение.
- **Idempotent (идемпотентный)** — повторный вызов с теми же параметрами даёт тот же результат.

| Метод   | Safe | Idempotent | Cacheable | Типичное применение                              |
|---------|------|------------|-----------|--------------------------------------------------|
| GET     | да   | да         | да        | Получение ресурса или списка                     |
| HEAD    | да   | да         | да        | Проверка существования/метаданных без тела       |
| POST    | нет  | нет        | условно   | Создание ресурса, действие с побочным эффектом   |
| PUT     | нет  | да         | нет       | Полная замена ресурса                            |
| PATCH   | нет  | нет        | условно   | Частичное обновление ресурса                     |
| DELETE  | нет  | да         | нет       | Удаление ресурса                                 |
| OPTIONS | да   | да         | нет       | CORS preflight, узнать доступные методы          |
| CONNECT | нет  | нет        | нет       | Создание туннеля через прокси (HTTPS)            |

Важные нюансы:
- PUT идемпотентен: повторный `PUT /users/42` с теми же данными не создаст второй ресурс.
- PATCH формально не идемпотентен: `PATCH /counter {"increment": 1}` при повторе увеличит значение.
- DELETE идемпотентен: первый вызов возвращает 200/204, повторный — 404, но состояние системы не меняется.
- POST при повторе может создать дубликат — важно проектировать с учётом этого (идемпотентный ключ).

### HTTP-коды статусов

Источник: [MDN — HTTP Status](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).

**2xx — Успех**

| Код | Название          | Когда использовать                                  |
|-----|-------------------|-----------------------------------------------------|
| 200 | OK                | Успешный GET, PUT, PATCH с телом ответа             |
| 201 | Created           | Успешный POST/PUT, создавший новый ресурс           |
| 202 | Accepted          | Запрос принят, обработка асинхронная                |
| 204 | No Content        | Успешный DELETE или PUT/PATCH без тела ответа       |
| 206 | Partial Content   | Ответ на Range-запрос (потоковая отдача файлов)     |

**3xx — Перенаправление**

| Код | Название           | Особенности                                         |
|-----|--------------------|-----------------------------------------------------|
| 301 | Moved Permanently  | Постоянный редирект; браузер кэширует               |
| 302 | Found              | Временный редирект; метод может смениться на GET    |
| 304 | Not Modified       | Кэш актуален; тело не передаётся                   |
| 307 | Temporary Redirect | Временный редирект; метод НЕ меняется               |
| 308 | Permanent Redirect | Постоянный редирект; метод НЕ меняется              |

**4xx — Ошибки клиента**

| Код | Название                  | Когда использовать                                |
|-----|---------------------------|---------------------------------------------------|
| 400 | Bad Request               | Некорректный синтаксис, ошибки валидации          |
| 401 | Unauthorized              | Не аутентифицирован (нет или неверный токен)      |
| 403 | Forbidden                 | Аутентифицирован, но нет прав                     |
| 404 | Not Found                 | Ресурс не найден                                  |
| 405 | Method Not Allowed        | Метод не поддерживается для данного URI           |
| 409 | Conflict                  | Конфликт состояний (дубликат, версия)             |
| 415 | Unsupported Media Type    | Content-Type не поддерживается сервером           |
| 422 | Unprocessable Content     | Синтаксис верен, но семантические ошибки (WebDAV) |
| 429 | Too Many Requests         | Rate limiting                                     |

**5xx — Ошибки сервера**

| Код | Название              | Когда возникает                                  |
|-----|-----------------------|--------------------------------------------------|
| 500 | Internal Server Error | Непредвиденная ошибка на сервере                 |
| 502 | Bad Gateway           | Апстрим вернул некорректный ответ                |
| 503 | Service Unavailable   | Сервис недоступен (перегрузка, обслуживание)     |
| 504 | Gateway Timeout       | Апстрим не ответил вовремя                       |

### HTTP-заголовки

Источник: [MDN — HTTP Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers).

**Управление контентом**

| Заголовок        | Описание                                                    |
|------------------|-------------------------------------------------------------|
| Content-Type     | MIME-тип тела: `application/json`, `text/html; charset=utf-8` |
| Content-Length   | Размер тела в байтах                                        |
| Accept           | Типы, которые клиент готов принять                          |
| Accept-Encoding  | Поддерживаемые алгоритмы сжатия: `gzip`, `br`              |

**Аутентификация**

| Заголовок       | Описание                                                    |
|-----------------|-------------------------------------------------------------|
| Authorization   | Токен или учётные данные: `Bearer <token>`, `Basic <b64>`  |
| WWW-Authenticate| Сервер запрашивает аутентификацию (ответ на 401)           |

**Кэширование**

| Заголовок         | Описание                                                    |
|-------------------|-------------------------------------------------------------|
| Cache-Control     | `max-age=3600`, `no-cache`, `no-store`, `public`, `private`|
| ETag              | Версия ресурса: `"33a64df5"`                               |
| Last-Modified     | Дата последнего изменения ресурса                           |
| If-None-Match     | Условный GET по ETag (клиент → сервер)                     |
| If-Modified-Since | Условный GET по дате (клиент → сервер)                     |

**CORS**

| Заголовок                      | Описание                                        |
|--------------------------------|-------------------------------------------------|
| Origin                         | Источник запроса (браузер добавляет автоматически) |
| Access-Control-Allow-Origin    | Какие источники разрешены (`*` или конкретный) |
| Access-Control-Allow-Methods   | Разрешённые методы для cross-origin             |
| Access-Control-Allow-Headers   | Разрешённые заголовки запроса                   |
| Access-Control-Max-Age         | Время кэширования preflight-ответа (секунды)    |

**Безопасность**

| Заголовок                    | Описание                                          |
|------------------------------|---------------------------------------------------|
| Strict-Transport-Security    | Принудительный HTTPS: `max-age=31536000`          |
| Content-Security-Policy      | Разрешённые источники скриптов, стилей, фреймов   |
| X-Content-Type-Options       | `nosniff` — запрет MIME-sniffing                  |
| X-Frame-Options              | `DENY` / `SAMEORIGIN` — защита от clickjacking    |

### Принципы REST и уровни зрелости Ричардсона

Источник: [Martin Fowler — Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html).

Модель Ричардсона описывает четыре уровня «зрелости» REST API:

- **Уровень 0 — Один URI, один метод (RPC через HTTP)**. Все операции идут через одну точку входа, например `POST /api`. Метаданные HTTP не используются по назначению.
- **Уровень 1 — Ресурсы**. Разные URI для разных ресурсов (`/users`, `/orders/42`), но методы HTTP ещё не семантизированы.
- **Уровень 2 — HTTP-методы и коды статусов**. GET для чтения, POST для создания, DELETE для удаления. Ответы используют корректные коды статусов. Большинство реальных REST API находятся на этом уровне.
- **Уровень 3 — HATEOAS (Hypermedia as the Engine of Application State)**. Ответ содержит ссылки на связанные действия (`_links`), позволяя клиенту «открывать» API динамически. Реализуется через Spring HATEOAS.

Шесть ограничений REST по Филдингу: клиент-сервер, stateless, кэшируемость, единообразный интерфейс, многоуровневость, код по запросу (опционально).

### Spring MVC: контроллеры и маппинг

Источник: [Spring MVC — Annotated Controllers](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller.html).

**Основные аннотации**

`@Controller` + `@ResponseBody` = `@RestController`. Класс, помеченный `@RestController`, автоматически сериализует возвращаемое значение методов в JSON/XML без необходимости указывать `@ResponseBody` на каждом методе.

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDto createUser(@RequestBody @Valid CreateUserRequest req) {
        return userService.create(req);
    }

    @PutMapping("/{id}")
    public UserDto updateUser(@PathVariable Long id,
                              @RequestBody @Valid UpdateUserRequest req) {
        return userService.update(id, req);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

**Параметры методов-обработчиков**

| Аннотация        | Источник                    | Пример                                          |
|------------------|-----------------------------|--------------------------------------------------|
| `@PathVariable`  | Часть URI-пути              | `/users/{id}` → `@PathVariable Long id`         |
| `@RequestParam`  | Query string                | `/search?q=text` → `@RequestParam String q`     |
| `@RequestBody`   | Тело запроса (JSON → Java)  | `@RequestBody UserDto dto`                       |
| `@RequestHeader` | HTTP-заголовок              | `@RequestHeader("Authorization") String auth`   |
| `@CookieValue`   | Cookie                      | `@CookieValue("session") String sid`            |
| `@ModelAttribute`| Form-параметры (MVC-формы)  | `@ModelAttribute UserForm form`                 |

`@RequestParam` поддерживает `required = false` и `defaultValue`:

```java
@GetMapping("/items")
public List<Item> list(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size) { ... }
```

**URI-паттерны и content negotiation**

Источник: [Spring MVC — @RequestMapping](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-requestmapping.html).

```java
// Wildcard и path variable
@GetMapping("/resources/{*path}")   // захватывает весь остаток пути
@GetMapping("/users/{id:[0-9]+}")   // regex ограничение

// Ограничение по Content-Type и Accept
@PostMapping(path = "/data",
             consumes = "application/json",
             produces = "application/json")
```

`consumes` сужает маппинг по заголовку `Content-Type` входящего запроса; `produces` — по заголовку `Accept`.

**ResponseEntity**

`ResponseEntity<T>` даёт полный контроль над ответом: статус, заголовки, тело.

```java
@GetMapping("/{id}")
public ResponseEntity<UserDto> get(@PathVariable Long id) {
    return userService.findById(id)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build());
}

// Ответ с Location-заголовком при создании ресурса
@PostMapping
public ResponseEntity<UserDto> create(@RequestBody @Valid CreateUserRequest req,
                                      UriComponentsBuilder ucb) {
    UserDto created = userService.create(req);
    URI location = ucb.path("/api/v1/users/{id}")
                      .buildAndExpand(created.id()).toUri();
    return ResponseEntity.created(location).body(created);
}
```

### Сериализация JSON с Jackson

Spring MVC использует Jackson для преобразования Java-объектов в JSON и обратно через `HttpMessageConverter`. Ключевые аннотации Jackson:

| Аннотация                      | Назначение                                                    |
|--------------------------------|---------------------------------------------------------------|
| `@JsonProperty("user_name")`   | Имя поля в JSON отличается от имени поля Java                |
| `@JsonIgnore`                  | Поле не участвует в сериализации/десериализации               |
| `@JsonInclude(NON_NULL)`       | Не включать `null`-поля в JSON                               |
| `@JsonFormat(pattern="...")`   | Формат даты/времени                                           |
| `@JsonAlias("...")`            | Альтернативные имена при десериализации                       |
| `@JsonCreator` + `@JsonProperty`| Кастомный конструктор/фабричный метод                        |

Конфигурация ObjectMapper через Spring Boot (`application.yml`):

```yaml
spring:
  jackson:
    default-property-inclusion: non_null
    serialization:
      write-dates-as-timestamps: false
    deserialization:
      fail-on-unknown-properties: false
```

### Обработка ошибок: @ExceptionHandler и ProblemDetail

Источник: [Spring MVC — Error Responses](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html).

**@ExceptionHandler на уровне контроллера** обрабатывает исключения только в рамках одного контроллера. **@ControllerAdvice** — глобальный обработчик для всех контроллеров.

Начиная с Spring Framework 6.0, реализована поддержка **RFC 9457 (Problem Details for HTTP APIs)** через `ProblemDetail` и `ErrorResponse`. Spring Boot активирует её через свойство:

```properties
spring.mvc.problemdetails.enabled=true
```

```java
@ControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    // Обработка конкретного бизнес-исключения
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ProblemDetail> handleUserNotFound(
            UserNotFoundException ex, HttpServletRequest request) {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.NOT_FOUND);
        detail.setTitle("User Not Found");
        detail.setDetail(ex.getMessage());
        detail.setInstance(URI.create(request.getRequestURI()));
        return ResponseEntity.status(404).body(detail);
    }

    // Добавление нестандартных полей
    @ExceptionHandler(OrderConflictException.class)
    public ProblemDetail handleConflict(OrderConflictException ex) {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.CONFLICT);
        detail.setDetail(ex.getMessage());
        detail.setProperty("conflictingOrderId", ex.getConflictingId());
        detail.setProperty("timestamp", Instant.now());
        return detail;
    }
}
```

Ответ в формате `application/problem+json`:

```json
{
  "type": "about:blank",
  "title": "User Not Found",
  "status": 404,
  "detail": "User with id=42 does not exist",
  "instance": "/api/v1/users/42"
}
```

`ResponseEntityExceptionHandler` (базовый класс) уже содержит обработчики для всех стандартных исключений Spring MVC. Достаточно наследоваться от него, чтобы получить корректные ответы для `MethodArgumentNotValidException`, `HttpMessageNotReadableException` и других.

### Валидация запросов (Bean Validation)

Источник: [Spring MVC — Validation](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html).

`@Valid` (jakarta.validation) и `@Validated` (Spring) инициируют валидацию входящего объекта. Разница: `@Validated` поддерживает **группы валидации** (`groups = Create.class`), `@Valid` — нет.

```java
public record CreateUserRequest(
    @NotBlank(message = "Имя обязательно")
    String name,

    @Email
    @NotNull
    String email,

    @Min(18) @Max(120)
    Integer age
) {}

// В контроллере — @Valid перед параметром
@PostMapping
public UserDto create(@RequestBody @Valid CreateUserRequest req) { ... }
```

При нарушении ограничений Spring выбрасывает `MethodArgumentNotValidException`, которое `ResponseEntityExceptionHandler` автоматически превращает в ответ 400. Для получения ошибок в методе контроллера добавьте `BindingResult` следующим параметром:

```java
@PostMapping
public ResponseEntity<?> create(@RequestBody @Valid CreateUserRequest req,
                                 BindingResult result) {
    if (result.hasErrors()) {
        return ResponseEntity.badRequest().body(result.getAllErrors());
    }
    return ResponseEntity.status(201).body(userService.create(req));
}
```

### Spring WebFlux: реактивный стек

Источник: [Spring WebFlux Reference](https://docs.spring.io/spring-framework/reference/web/webflux.html).

Spring WebFlux появился в Spring 5 как неблокирующая альтернатива Spring MVC. Основан на Project Reactor и Reactive Streams.

| Аспект              | Spring MVC                     | Spring WebFlux                        |
|---------------------|--------------------------------|---------------------------------------|
| Модель              | Синхронная, блокирующая        | Асинхронная, неблокирующая            |
| Потоки              | Один поток на запрос (thread-per-request) | Небольшой пул потоков         |
| Серверы             | Tomcat, Jetty (Servlet API)    | Netty, Undertow, Servlet 3.1+         |
| HTTP-клиент         | `RestTemplate` (deprecated) / `RestClient` | `WebClient`              |
| Реактивные типы     | нет (или через адаптеры)       | `Mono<T>` (0..1), `Flux<T>` (0..N)   |

Аннотационная модель WebFlux идентична Spring MVC — те же `@RestController`, `@GetMapping` и т.д., но возвращаемые типы реактивные:

```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    @GetMapping("/{id}")
    public Mono<OrderDto> getOrder(@PathVariable Long id) {
        return orderService.findById(id);
    }

    @GetMapping
    public Flux<OrderDto> listOrders() {
        return orderService.findAll();
    }
}
```

**Когда WebFlux, а когда MVC:**
- WebFlux — при высокой конкурентности с большим числом I/O-операций, работе с реактивными источниками данных (R2DBC, Reactive MongoDB), потоковой передаче данных.
- MVC — для классических CRUD-приложений, при наличии синхронных библиотек, когда команда не знакома с реактивным программированием.

### Версионирование API

Три основных подхода:

| Стратегия           | Пример                                         | Плюсы                     | Минусы                        |
|---------------------|------------------------------------------------|---------------------------|-------------------------------|
| В URI               | `/api/v1/users`, `/api/v2/users`               | Просто, явно, кэшируется  | Нарушает REST (URI = ресурс)  |
| В заголовке         | `Accept: application/vnd.company.v2+json`      | RESTful, гибко            | Сложнее тестировать           |
| Query-параметр      | `/users?version=2`                             | Просто для тестирования   | Засоряет URI                  |

В Spring MVC версионирование через URI реализуется через `@RequestMapping("/api/v2/...")` или через отдельные пакеты контроллеров.

### Документация API: OpenAPI / Swagger

Источник: [springdoc-openapi](https://springdoc.org/).

Библиотека `springdoc-openapi` автоматически генерирует OpenAPI-описание на основе аннотаций Spring MVC. Добавить в `pom.xml`:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.4</version>
</dependency>
```

После добавления зависимости (без дополнительной конфигурации):
- Swagger UI доступен по `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON/YAML — по `http://localhost:8080/v3/api-docs`

Дополнительные аннотации для обогащения документации:

```java
@Operation(summary = "Получить пользователя по ID")
@ApiResponse(responseCode = "200", description = "Пользователь найден")
@ApiResponse(responseCode = "404", description = "Пользователь не найден")
@GetMapping("/{id}")
public ResponseEntity<UserDto> getUser(@PathVariable Long id) { ... }
```

## Достоверные источники

1. **[Spring Framework — Web MVC Reference](https://docs.spring.io/spring-framework/reference/web/webmvc.html)** — официальная документация Spring MVC: контроллеры, обработка ошибок, валидация, WebFlux. Первичный источник.
2. **[Spring MVC — Error Responses (RFC 9457 / ProblemDetail)](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html)** — официальная документация Spring по обработке ошибок и поддержке RFC 9457 (Problem Details for HTTP APIs).
3. **[MDN Web Docs — HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP)** — авторитетный справочник по протоколу HTTP: методы, коды статусов, заголовки. Поддерживается Mozilla.
4. **[Martin Fowler — Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)** — первоисточник описания уровней зрелости REST от признанного авторитета в области архитектуры ПО.
5. **[Spring MVC — Validation](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html)** — официальная документация Spring по Bean Validation в веб-слое.
6. **[springdoc-openapi](https://springdoc.org/)** — официальный сайт библиотеки для генерации OpenAPI-документации в Spring Boot-приложениях.
