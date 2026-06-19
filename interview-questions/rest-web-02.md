# REST, HTTP и веб-слой — часть 2 из 3

> Вопросы 21–40 (в части: 20). Всего в разделе: 60.
> Область знаний: [../theory/01-knowledge-areas/03-backend-ecosystem/17-rest-web.md](../theory/01-knowledge-areas/03-backend-ecosystem/17-rest-web.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](rest-web-01.md) · **ч.2** · [ч.3](rest-web-03.md)

---
### Вопрос 21. В чём разница между PUT и PATCH с точки зрения семантики и идемпотентности? Почему PATCH не всегда идемпотентен — приведите конкретный пример.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [PATCH request method — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PATCH)

**PUT** представляет собой полную замену ресурса и всегда является идемпотентным: повторная отправка одного и того же PUT оставляет ресурс в том же состоянии.

**PATCH** применяет частичные изменения к ресурсу — набор инструкций по модификации его отдельных частей, а не замену целиком. PATCH может быть неидемпотентным, поскольку применяет инструкции, а не устанавливает конечное состояние. Пример неидемпотентного PATCH: ресурс содержит автоинкрементный счётчик; PUT перезапишет счётчик целиком, а PATCH-инструкция вида `{"counter": "+1"}` будет увеличивать счётчик при каждом вызове — первый запрос даст counter=6, второй counter=7, третий counter=8, и т.д.

#### Ответ от Claude

**Семантическая разница:**

| Аспект | PUT | PATCH |
|---|---|---|
| Смысл | Полная замена ресурса | Частичное обновление ресурса |
| Тело запроса | Полное представление ресурса | Набор инструкций (патч) |
| Отсутствующие поля | Удаляются / сбрасываются | Остаются без изменений |
| RFC | RFC 7231, §4.3.4 | RFC 5789 |

Пример: есть пользователь `{"id": 1, "name": "Alice", "email": "alice@example.com"}`.

- `PUT /users/1` с телом `{"id": 1, "name": "Alice", "email": "new@example.com"}` — заменит весь ресурс. Если забыть поле `name`, оно будет удалено или сброшено.
- `PATCH /users/1` с телом `{"email": "new@example.com"}` — изменит только `email`, остальные поля останутся нетронутыми.

**Идемпотентность:**

- **PUT всегда идемпотентен**: тело запроса описывает желаемое конечное состояние. Сколько раз ни выполни `PUT /users/1` с одними и теми же данными — состояние ресурса будет одинаковым.
- **PATCH не гарантированно идемпотентен**: тело запроса описывает инструкцию, а не состояние. RFC 5789 явно предупреждает: *«PATCH is neither safe nor idempotent as defined by RFC 2616»*.

**Конкретный пример неидемпотентного PATCH:**

Используем формат JSON Patch (RFC 6902):

```
PATCH /account/42 HTTP/1.1
Content-Type: application/json-patch+json

[{ "op": "add", "path": "/balance/debit", "value": -1000 }]
```

Если начальный баланс равен 5000:
- 1-й вызов: баланс становится 4000
- 2-й вызов: баланс становится 3000
- 3-й вызов: баланс становится 2000

Каждый повторный запрос меняет состояние ресурса — идемпотентность нарушена.

**Пример идемпотентного PATCH** (для сравнения):

```
PATCH /users/1 HTTP/1.1
Content-Type: application/json

{ "email": "alice@new.com" }
```

Здесь PATCH ведёт себя идемпотентно: многократная отправка одного и того же значения `email` оставит ресурс в одном состоянии. Но это свойство конкретной реализации, а не гарантия протокола.

**Итог:** PUT идемпотентен по спецификации, PATCH — нет. При проектировании API следует явно документировать идемпотентность конкретных PATCH-операций и по возможности предпочитать форматы патчей, устанавливающие конечное значение, а не выполняющие относительные операции.
### Вопрос 22. Когда вернуть 400 Bad Request, а когда 422 Unprocessable Entity? В каких случаях оправдан 409 Conflict?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [HTTP Status Codes: 400 vs 422 — Beeceptor](https://beeceptor.com/docs/concepts/400-vs-422/)

400 Bad Request сигнализирует о синтаксических или структурных проблемах — сервер не может разобрать запрос вообще. 422 Unprocessable Entity означает, что сервер понял формат запроса, но отклоняет его из-за нарушения бизнес-логики или правил валидации.

Когда использовать 400: некорректный синтаксис JSON; отсутствие обязательных заголовков (например, Content-Type); неподдерживаемый медиатип; запрос настолько сломан, что сервер не может его интерпретировать.

Когда использовать 422: нарушение правил валидации (невалидный формат email); нарушение бизнес-правил (бронирование недоступного слота); доменные ошибки (товар закончился на складе).

Примеры из реальных API: GitHub возвращает 400 при некорректной структуре JSON, но 422, если JSON валиден, однако ссылается на несуществующую ветку. Shopify использует 400 при отсутствии заголовка Content-Type и 422 при попытке оформить заказ с товаром не в наличии.

#### Ответ от Claude

**HTTP 400 Bad Request** — ошибка на уровне синтаксиса или структуры запроса. Сервер не способен разобрать (parse) тело запроса или не удовлетворены базовые требования протокола. Типичные сценарии:
- тело запроса содержит невалидный JSON / XML (ошибка десериализации);
- отсутствует обязательный заголовок (Content-Type, Authorization);
- неподдерживаемый тип содержимого;
- нарушен синтаксис query-параметров;
- запрос структурно неполон (отсутствуют обязательные поля верхнего уровня по схеме).

Ключевой критерий: **до валидации бизнес-логики дело не доходит**, потому что запрос нельзя даже прочитать корректно.

**HTTP 422 Unprocessable Entity** — тело запроса успешно разобрано и синтаксически корректно, однако содержит семантические ошибки. Применяется после успешной десериализации:
- поле `email` содержит строку, не являющуюся адресом;
- значение `age: -5` нарушает ограничение `min: 0`;
- дата окончания раньше даты начала;
- ссылка на несуществующую связанную сущность (например, `categoryId` не существует в БД);
- нарушение бизнес-инварианта (бронирование уже занятого слота).

Практический ориентир: если фреймворк смог десериализовать тело без исключения — вы уже в зоне 422, не 400.

**Замечание о расхождении стандартов**: RFC 9110 (HTTP/1.1, 2022) расширил определение 400 — теперь оно покрывает «любую ситуацию, когда сервер считает запрос некорректным». Поэтому ряд API (в том числе некоторые версии Spring Validation) возвращает 400 и для ошибок валидации. Тем не менее семантически точнее и информативнее для клиента использовать 422 для валидационных ошибок — это соглашение принято в JSON:API, GitHub API v3, Stripe API.

---

**HTTP 409 Conflict** оправдан, когда запрос синтаксически и семантически корректен, но **не может быть выполнен из-за текущего состояния ресурса на сервере**. Клиенту даётся понять, что конфликт устраним — нужно разрешить противоречие. Типичные случаи:

1. **Дублирование ресурса** — попытка создать пользователя с уже занятым email (`POST /users` → 409 + описание конфликта).
2. **Оптимистичная блокировка (optimistic concurrency)** — `PUT /document/42` с заголовком `If-Match: "v1"`, когда документ уже обновлён другим клиентом до версии `v2`; сервер возвращает 409 (или 412 Precondition Failed — оба варианта используются).
3. **Конкурентное выполнение задач** — попытка запустить задачу, которая уже выполняется; сервер отвечает 409 с указанием `runningTaskId`.
4. **Нарушение уникальных ограничений** — вставка записи с уже существующим уникальным ключом.
5. **Несовместимое состояние** — перевод сущности в статус, недостижимый из текущего (например, отмена уже доставленного заказа).

**Итоговая шпаргалка:**

| Код | Когда использовать |
|-----|--------------------|
| 400 | Запрос нельзя разобрать: плохой JSON, неверный Content-Type, отсутствующие обязательные заголовки |
| 422 | Запрос разобран, но данные не проходят валидацию или нарушают бизнес-правила |
| 409 | Запрос валиден, но конфликтует с текущим состоянием ресурса (дубликат, concurrent update, несовместимый статус) |

---

### Вопрос 23. Что такое модель зрелости Ричардсона (Richardson Maturity Model)? Опишите уровни 0–3 и чем HATEOAS отличается от REST уровня 2.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Richardson Maturity Model — Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html)

Модель зрелости Ричардсона описывает прогрессию в направлении по-настоящему RESTful веб-сервисов через четыре уровня, разработанные Леонардом Ричардсоном.

**Уровень 0: RPC-туннелирование.** HTTP используется исключительно как транспортный механизм для вызова функций на сервере, аналогично удалённым вызовам процедур (RPC). Единственный URL, только метод POST. Большинство SOAP-сервисов работают на этом уровне.

**Уровень 1: Ресурсы.** Вводится абстракция ресурсов. Для каждого ресурса существует отдельный URI (например, `/users`, `/orders`). Однако по-прежнему используется только один HTTP-метод (как правило, POST) для всех операций.

**Уровень 2: HTTP-глаголы.** Стандартные HTTP-методы обретают семантический смысл: GET для безопасных и кешируемых запросов, POST для создания, PUT для обновления, DELETE для удаления. Также вводятся соответствующие HTTP-коды состояния для коммуникации результатов. Это наиболее распространённый уровень реальных REST API.

**Уровень 3: Гипермедиа-управление (HATEOAS).** Ответы содержат ссылки (`<link>` элементы с типами отношений и URI), сообщающие клиенту, какие действия возможны и по каким адресам. Fowler: «Гиперtext As The Engine Of Application State» — гипермедиа как движок состояния приложения.

**Ключевое различие уровней 2 и 3:** на уровне 2 клиент должен заранее знать шаблоны URI и доступные операции. На уровне 3 сервер сам рекламирует возможности через гипермедиа, что обеспечивает слабую связанность (loose coupling) и позволяет API эволюционировать без поломки клиентов.

#### Ответ от Claude

**Модель зрелости Ричардсона** (Richardson Maturity Model, RMM) — концептуальная шкала, предложенная Леонардом Ричардсоном в 2008 году на QCon и популяризованная Мартином Фаулером. Модель оценивает степень соответствия API принципам REST по трём осям: URI, HTTP-методы, гипермедиа.

---

**Уровень 0 — «Болото POX» (Plain Old XML)**

HTTP используется как тупой транспорт для передачи сообщений (XML, JSON) между клиентом и сервером. Единственный эндпоинт, единственный метод (обычно POST), вся логика закодирована в теле запроса.

Пример (запись к врачу):
```
POST /appointmentService HTTP/1.1
{ "action": "getOpenSlots", "date": "2010-01-04" }
```

Характерный представитель: SOAP/XML-RPC. Ошибки часто возвращаются в теле с кодом 200 OK.

---

**Уровень 1 — Ресурсы**

Появляются отдельные URI для каждого ресурса. Взаимодействие направлено к конкретному объекту, а не к «сервису в эфире». HTTP-методы всё ещё не разграничиваются — всё через POST.

```
POST /doctors/mjones HTTP/1.1
{ "date": "2010-01-04" }
```

---

**Уровень 2 — HTTP-глаголы**

Полноценное использование HTTP-методов в соответствии с их семантикой:
- `GET` — безопасная, идемпотентная выборка (кешируется);
- `POST` — создание, неидемпотентные операции;
- `PUT`/`PATCH` — обновление (PUT идемпотентен);
- `DELETE` — удаление (идемпотентен).

Также используются коды ответа по назначению: 201 Created при создании, 404 при отсутствии ресурса, 405 Method Not Allowed и т.д. Это **текущий отраслевой стандарт** для большинства «REST API».

---

**Уровень 3 — HATEOAS (Hypermedia As The Engine Of Application State)**

Ответы сервера содержат гипермедиа-ссылки на связанные ресурсы и возможные следующие действия. Клиент не хардкодит URI — он следует ссылкам, полученным от сервера.

Пример ответа (HAL-подобный формат):
```json
{
  "appointmentId": "1234",
  "status": "confirmed",
  "_links": {
    "self":   { "href": "/appointments/1234" },
    "cancel": { "href": "/appointments/1234/cancel", "method": "DELETE" },
    "doctor": { "href": "/doctors/mjones" }
  }
}
```

Форматы гипермедиа: HAL (`application/hal+json`), JSON:API, Siren, Collection+JSON, Spring HATEOAS (библиотека).

---

**Чем HATEOAS (уровень 3) отличается от уровня 2:**

| Критерий | Уровень 2 | Уровень 3 (HATEOAS) |
|----------|-----------|----------------------|
| Знание URI клиентом | Хардкодится в клиенте | Получается динамически из ответов |
| Обнаружение операций | Out-of-band документация (Swagger и т.п.) | In-band: ссылки в ответах |
| Связанность | Сильная (клиент знает структуру API) | Слабая (клиент следует ссылкам) |
| Эволюция API | Ломает клиентов при смене URI | Клиент адаптируется автоматически |
| Практическое применение | Повсеместно | Редко в полной мере |

**Практическое замечание:** Рой Филдинг (автор REST) настаивал на том, что без HATEOAS API нельзя называть REST. Тем не менее полноценный уровень 3 крайне редко реализуется в продакшне из-за сложности клиентской логики. Большинство современных «REST API» находятся на уровне 2, что вполне достаточно для практических задач.

---

### Вопрос 24. Чем @Controller отличается от @RestController на уровне внутреннего устройства Spring? Что произойдёт, если поставить @ResponseBody на каждый метод @Controller — это будет эквивалентно @RestController?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [RestController (Spring Framework API) — docs.spring.io](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/bind/annotation/RestController.html)

`@RestController` — convenience annotation (удобная аннотация), которая сама аннотирована `@Controller` и `@ResponseBody`.

Согласно документации: «A convenience annotation that is itself annotated with `@Controller` and `@ResponseBody`.» Все методы, обработчики запросов в классе, аннотированном `@RestController`, автоматически предполагают семантику `@ResponseBody` по умолчанию — возвращаемые значения сериализуются и записываются непосредственно в тело HTTP-ответа, а не интерпретируются как имена представлений (view names). Аннотация появилась в Spring Framework 4.0.

#### Ответ от Claude

**На уровне исходного кода** `@RestController` реализована как мета-аннотация (composed annotation):

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Controller          // <-- включает @Component, регистрирует бин
@ResponseBody        // <-- применяется ко всем методам класса
public @interface RestController {
    @AliasFor(annotation = Controller.class)
    String value() default "";
}
```

`@Controller`, в свою очередь, является мета-аннотацией над `@Component` и регистрирует класс как Spring-бин, обнаруживаемый через component scan. `@ResponseBody` на уровне класса сигнализирует `RequestMappingHandlerAdapter` пропустить фазу разрешения представления (view resolution) и передать возвращаемое значение метода напрямую цепочке `HttpMessageConverter`.

---

**Механизм обработки ответа (внутренний путь):**

1. `DispatcherServlet` получает запрос и делегирует `HandlerAdapter`.
2. `RequestMappingHandlerAdapter` вызывает метод контроллера.
3. `HandlerMethodReturnValueHandlerComposite` выбирает подходящий `ReturnValueHandler`.
4. Если метод или класс помечены `@ResponseBody`, выбирается `RequestResponseBodyMethodProcessor`.
5. `RequestResponseBodyMethodProcessor` использует зарегистрированные `HttpMessageConverter` (например, `MappingJackson2HttpMessageConverter`) для сериализации объекта в JSON/XML и записи в `HttpServletResponse`.

Без `@ResponseBody` (обычный `@Controller`) возвращаемая строка трактуется как имя логического представления, которое `ViewResolver` преобразует в конкретный шаблон (Thymeleaf, JSP и т.д.).

---

**Эквивалентность `@Controller` + `@ResponseBody` на каждом методе и `@RestController`:**

Функционально — **да, эквивалентно**. `@RestController` лишь делает то же самое, что ручное добавление `@ResponseBody` к каждому handler-методу, только на уровне класса. Spring обнаруживает `@ResponseBody` через `AnnotationUtils.findAnnotation`, который поднимается по иерархии аннотаций, поэтому `@ResponseBody` на классе применяется ко всем его методам.

Важные нюансы:

1. **Переопределение в подклассах.** Если вы наследуете `@RestController` и хотите, чтобы один метод возвращал View, сделать это стандартным способом нельзя — `@ResponseBody` унаследован через мета-аннотацию. С `@Controller` + явный `@ResponseBody` на каждом методе такое переопределение возможно.

2. **Инструментальная обработка.** Фреймворки (Spring Security, документирование через SpringDoc/Swagger) различают `@RestController` и `@Controller` именно по наличию составной аннотации. Например, `@ControllerAdvice` с параметром `annotations = RestController.class` будет работать только с контроллерами, аннотированными именно `@RestController`.

3. **Читаемость и намерение.** `@RestController` явно выражает намерение: этот класс — REST API контроллер. `@Controller` — это MVC контроллер для рендеринга представлений. Разница в семантике важна для понимания кода.

**Итог:** `@RestController` = `@Controller` + `@ResponseBody` на уровне класса. Если поставить `@ResponseBody` на каждый handler-метод `@Controller`, поведение при обработке запросов будет идентичным, однако могут быть отличия в поведении фреймворков и инструментов, ориентирующихся на присутствие конкретной аннотации `@RestController`.
### Вопрос 25. В чём разница между ResponseEntity<T> и использованием @ResponseBody + @ResponseStatus? Когда предпочтительнее ResponseEntity?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [ResponseEntity :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/responseentity.html)

`ResponseEntity` представляет полный HTTP-ответ: код статуса, заголовки и тело. Как следствие, с его помощью можно полностью сконфигурировать HTTP-ответ. В отличие от `@ResponseBody`, `ResponseEntity` позволяет также задавать статус и заголовки. Пример использования:

```java
@GetMapping("/something")
public ResponseEntity<String> handle() {
    String body = ...;
    String etag = ...;
    return ResponseEntity.ok().eTag(etag).body(body);
}
```

Документация также показывает, что `ResponseEntity` поддерживает асинхронные сценарии: когда статус/заголовки известны немедленно, а тело — асинхронно (`ResponseEntity<Mono<T>>`), либо когда и то и другое асинхронно (`Mono<ResponseEntity<T>>`).

#### Ответ от Claude

**`@ResponseBody` + `@ResponseStatus`** — это два отдельных аннотационных механизма:

- `@ResponseBody` указывает Spring сериализовать возвращаемое значение метода напрямую в тело HTTP-ответа (через `HttpMessageConverter`). В `@RestController` применяется ко всем методам автоматически.
- `@ResponseStatus` позволяет задать фиксированный HTTP-статус (и опциональный `reason`), который будет использоваться при успешном возврате метода или при выбрасывании исключения.

**Ограничения `@ResponseBody` + `@ResponseStatus`:**

| Возможность | `@ResponseBody` + `@ResponseStatus` | `ResponseEntity<T>` |
|---|---|---|
| Тело ответа | Да | Да |
| HTTP-статус | Только фиксированный (compile-time) | Динамический (runtime) |
| Кастомные заголовки | Нет | Да |
| Гибкость | Низкая | Высокая |

**`ResponseEntity<T>`** — это обёртка над полным HTTP-ответом. Он объединяет в себе возможности `@ResponseBody` и `@ResponseStatus`, добавляя управление заголовками. Тело по-прежнему сериализуется через `HttpMessageConverter`.

**Когда предпочтительнее `ResponseEntity`:**

1. **Динамический статус.** Когда статус ответа зависит от логики времени выполнения — например, `201 Created` при создании и `200 OK` при обновлении одним методом.
2. **Управление заголовками.** Когда нужно выставить `Location`, `ETag`, `Cache-Control`, `WWW-Authenticate` и другие заголовки ответа.
3. **Условные ответы.** Например, возврат `304 Not Modified` при совпадении `ETag` без тела.
4. **Асинхронные сценарии в реактивном стеке.** `ResponseEntity<Mono<T>>` или `Mono<ResponseEntity<T>>`.

**Когда достаточно `@ResponseBody` + `@ResponseStatus`:**

- Статус всегда одинаковый и известен на этапе компиляции.
- Кастомные заголовки не нужны.
- Код должен быть максимально лаконичным (например, простые CRUD-операции в `@RestController`).

**Примечание:** `@ResponseStatus` на методе-обработчике не следует путать с `@ResponseStatus` на классе-исключении — последнее является стандартным способом маппинга исключений на HTTP-статусы через `@ExceptionHandler` или `ResponseStatusExceptionResolver`.

---

### Вопрос 26. Что такое HttpMessageConverter в Spring MVC? Как Spring выбирает нужный конвертер при обработке запроса и ответа — опишите алгоритм content negotiation.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [HTTP Message Conversion :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc/message-converters.html)

`HttpMessageConverter` — это интерфейс в модуле `spring-web`, отвечающий за преобразование тела HTTP-запроса/ответа в Java-объект и обратно. Он работает с `InputStream` и `OutputStream`.

На стороне сервера конвертеры регистрируются в `RequestMappingHandlerAdapter`. Spring автоматически регистрирует набор встроенных конвертеров при наличии соответствующих библиотек в classpath:

- `StringHttpMessageConverter` — типы `text/*`
- `ByteArrayHttpMessageConverter` — `*/*` (пишет как `application/octet-stream`)
- `FormHttpMessageConverter` — `application/x-www-form-urlencoded`, `multipart/form-data`
- `JacksonJsonHttpMessageConverter` — `application/json` (если Jackson в classpath)
- `JacksonXmlHttpMessageConverter` — `application/xml` (если Jackson XML в classpath)
- `SourceHttpMessageConverter` — `text/xml`, `application/xml`
- `ProtobufHttpMessageConverter`, `GsonHttpMessageConverter` и другие — при наличии библиотек

Интерфейс `HttpMessageConverter<T>` определяет методы: `canRead(Class<?>, MediaType)`, `canWrite(Class<?>, MediaType)`, `read(Class<T>, HttpInputMessage)`, `write(T, MediaType, HttpOutputMessage)`.

#### Ответ от Claude

**Что такое `HttpMessageConverter`**

`HttpMessageConverter<T>` — стратегический интерфейс Spring, определяющий двустороннее преобразование объектов Java в тело HTTP-сообщения и обратно. Каждая реализация умеет работать с одним или несколькими медиатипами (`MediaType`).

**Алгоритм выбора конвертера при чтении запроса (`@RequestBody`):**

1. Spring извлекает заголовок `Content-Type` входящего запроса.
2. Определяет целевой тип Java-параметра метода-обработчика.
3. Итерирует по списку зарегистрированных конвертеров в порядке регистрации.
4. Для каждого конвертера вызывает `canRead(targetClass, contentType)`.
5. Использует **первый** конвертер, вернувший `true`, и вызывает у него `read()`.
6. Если ни один конвертер не подходит — выбрасывается `HttpMediaTypeNotSupportedException` (415).

**Алгоритм выбора конвертера при записи ответа (`@ResponseBody` / `ResponseEntity`):**

1. **Content Negotiation** — Spring определяет допустимые медиатипы ответа:
   - Разбирает заголовок `Accept` из запроса клиента.
   - Учитывает атрибут `produces` в `@RequestMapping`, если он задан (сужает допустимые типы).
   - При конфигурации `ContentNegotiationStrategy` могут учитываться параметры запроса (например, `?format=json`) или расширения URL (устаревший способ, не рекомендуется из соображений безопасности — RFD-атаки).
   - По умолчанию используется только заголовок `Accept`.
2. Итерирует по списку конвертеров в порядке регистрации.
3. Для каждого конвертера вызывает `canWrite(returnType, candidateMediaType)` для каждого из допустимых медиатипов.
4. Использует **первый** конвертер/медиатип, для которых `canWrite` вернул `true`.
5. Вызывает `write()` — конвертер сериализует объект в выходной поток ответа и выставляет `Content-Type`.
6. Если ни один конвертер не подходит — выбрасывается `HttpMediaTypeNotAcceptableException` (406).

**Стратегии `ContentNegotiationStrategy` (в порядке приоритета при конфигурировании):**

| Стратегия | Класс | Примечание |
|---|---|---|
| Заголовок `Accept` | `HeaderContentNegotiationStrategy` | Используется по умолчанию |
| Параметр запроса | `ParameterContentNegotiationStrategy` | Например, `?mediaType=json` |
| Путь/расширение | `PathExtensionContentNegotiationStrategy` | Устарело, отключено по умолчанию с Spring 5.3 |
| Фиксированный тип | `FixedContentNegotiationStrategy` | Fallback |

**Порядок регистрации конвертеров важен:** `*/*` (ByteArray, String) регистрируются в конце, чтобы не перехватывать запросы у более специализированных конвертеров.

**Кастомизация через `WebMvcConfigurer`:**

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        converters.add(new CustomProtobufConverter());
    }

    @Override
    public void extendMessageConverters(List<HttpMessageConverter<?>> converters) {
        // extendMessageConverters вызывается ПОСЛЕ регистрации дефолтных,
        // позволяет дополнять или переупорядочивать список
    }
}
```

---

### Вопрос 27. Чем @Valid отличается от @Validated? В каких сценариях @Valid недостаточно и нужна @Validated (например, валидация параметров метода на уровне сервиса)?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Java Bean Validation :: Spring Framework](https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html)

`@Validated` активирует метод-уровневую валидацию через Spring AOP. Чтобы валидировать параметры методов в сервисном слое, нужно аннотировать класс сервиса `@Validated` и разместить `@Valid` на параметре метода — совокупность этих двух аннотаций заставит Spring Boot валидировать объект. В конфигурации необходимо зарегистрировать `MethodValidationPostProcessor`:

```java
@Configuration
public class ApplicationConfiguration {
    @Bean
    public static MethodValidationPostProcessor validationPostProcessor() {
        return new MethodValidationPostProcessor();
    }
}

@Validated
public class MyService {
    void addStudent(@Valid Person person, @Max(2) int degrees) {
        // параметры валидируются через AOP-прокси
    }
}
```

При нарушении ограничений выбрасывается `jakarta.validation.ConstraintViolationException`. Можно настроить `adaptConstraintViolations = true` для выброса `MethodValidationException` вместо него.

`@Validated` также поддерживает группы валидации:

```java
@Validated(UpdateGroup.class)
public class MyService {
    void update(@Valid Person person) { ... }
}
```

#### Ответ от Claude

**Происхождение и стандарт:**

| Аннотация | Источник | Стандарт |
|---|---|---|
| `@Valid` | `jakarta.validation.Valid` (ранее `javax.validation.Valid`) | Jakarta Bean Validation (JSR-380) |
| `@Validated` | `org.springframework.validation.annotation.Validated` | Spring Framework (проприетарное расширение) |

**Что умеет `@Valid`:**

1. **Каскадная валидация** — если объект содержит вложенные объекты, помеченные `@Valid`, они тоже будут провалидированы.
2. **Валидация тела запроса в контроллерах** — `@Valid @RequestBody Dto dto` — Spring MVC / Spring Boot имеет встроенную поддержку этого сценария без AOP.
3. **Не поддерживает группы валидации** — нельзя передать группу через `@Valid`.

**Что добавляет `@Validated`:**

1. **Группы валидации** — можно указать одну или несколько групп: `@Validated(CreateGroup.class)`. Только ограничения, помеченные этой группой, будут применены.
2. **Метод-уровневая валидация через AOP** — при аннотировании класса `@Validated` Spring создаёт AOP-прокси, который перехватывает вызовы методов и валидирует параметры и/или возвращаемые значения.
3. **Валидация примитивных параметров** — `@Max`, `@Min`, `@NotBlank` и другие JSR-380 аннотации могут применяться непосредственно к параметрам метода.

**Когда `@Valid` недостаточно и нужна `@Validated`:**

**Сценарий 1 — Валидация на уровне сервиса:**

В Spring MVC контроллеры имеют встроенный механизм валидации (`DispatcherServlet` / `HandlerMethodArgumentResolver`). Сервисные бины не участвуют в этом механизме — они обычные Spring-бины. Чтобы включить валидацию параметров метода сервиса, нужно:

```java
// 1. Зарегистрировать MethodValidationPostProcessor (в Spring Boot регистрируется автоматически)
@Bean
public static MethodValidationPostProcessor methodValidationPostProcessor() {
    return new MethodValidationPostProcessor();
}

// 2. Аннотировать класс сервиса @Validated
@Service
@Validated
public class OrderService {

    public Order createOrder(@Valid @NotNull OrderRequest request) {
        // При нарушении: ConstraintViolationException
        return ...;
    }

    public Order updateOrder(@Validated(UpdateGroup.class) OrderRequest request) {
        // Применяются только ограничения группы UpdateGroup
        return ...;
    }
}
```

**Сценарий 2 — Группы валидации (частичная валидация):**

```java
public interface CreateGroup {}
public interface UpdateGroup {}

public class UserDto {
    @Null(groups = CreateGroup.class)   // id должен быть null при создании
    @NotNull(groups = UpdateGroup.class) // id обязателен при обновлении
    private Long id;

    @NotBlank
    private String name;
}

@RestController
public class UserController {
    @PostMapping
    public User create(@Validated(CreateGroup.class) @RequestBody UserDto dto) { ... }

    @PutMapping
    public User update(@Validated(UpdateGroup.class) @RequestBody UserDto dto) { ... }
}
```

`@Valid` в этих случаях не подходит, так как не имеет атрибута `groups`.

**Сценарий 3 — Валидация параметров и возвращаемых значений метода:**

```java
@Validated
public class ReportService {

    @NotNull
    public Report generate(@NotBlank String reportName, @Min(1) @Max(12) int month) {
        // Spring AOP провалидирует все параметры перед вызовом
        // и возвращаемое значение после
        return ...;
    }
}
```

**Важные ограничения `@Validated` с AOP:**

- Работает только с Spring-прокси: не работает при вызове метода внутри того же класса (`this.method()`).
- Класс должен быть Spring-бином (управляемым контейнером).
- В Spring Boot `MethodValidationPostProcessor` регистрируется автоматически при наличии `spring-boot-starter-validation` в classpath.

**Исключения при ошибках валидации:**

| Слой | Исключение |
|---|---|
| Контроллер (`@RequestBody` + `@Valid`) | `MethodArgumentNotValidException` |
| Контроллер (параметры метода + `@Validated`) | `ConstraintViolationException` |
| Сервисный слой (`@Validated` + AOP) | `ConstraintViolationException` |

**Итог:** Используйте `@Valid` для каскадной валидации объектов (особенно в теле запроса в контроллерах); используйте `@Validated` когда нужны группы валидации или валидация параметров в сервисном слое через AOP.

---
### Вопрос 28. Что происходит, когда @RequestBody-параметр не проходит валидацию Bean Validation — какое исключение бросает Spring и какой HTTP-статус будет по умолчанию? А если валидация упала на @PathVariable/@RequestParam?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Validation :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html)

Документация Spring чётко разграничивает два сценария валидации:

**Сценарий 1 — @RequestBody:** если параметр метода контроллера аннотирован `@Valid` или `@Validated` и не проходит проверку, бросается `MethodArgumentNotValidException`. Это исключение применяется к «объектам-командам» (command objects), в том числе аргументам `@RequestBody` и `@ModelAttribute`. HTTP-статус по умолчанию — **400 Bad Request**.

**Сценарий 2 — @PathVariable / @RequestParam:** если на параметрах метода объявлены аннотации-ограничения (`@Min`, `@NotBlank`, `@NotNull` и т. д.) напрямую (без обёртки в отдельный объект), бросается `HandlerMethodValidationException`. Этот механизм называется *method validation* и появился как встроенный в Spring Framework 6.1. HTTP-статус по умолчанию также **400 Bad Request**.

#### Ответ от Claude

**@RequestBody — MethodArgumentNotValidException (HTTP 400)**

Когда контроллер объявляет параметр `@RequestBody @Valid Foo body`, Spring вызывает Hibernate Validator (реализацию Bean Validation). При ошибках валидации бросается `MethodArgumentNotValidException` — подкласс `BindException`, реализующий `ErrorResponse`. Через `DefaultHandlerExceptionResolver` (или встроенный обработчик `ResponseEntityExceptionHandler`) это исключение автоматически конвертируется в ответ **HTTP 400 Bad Request**. Тело ответа по умолчанию в Spring Boot — JSON в формате RFC 9457 Problem Detail.

Пример:
```java
@PostMapping("/users")
public ResponseEntity<User> createUser(@RequestBody @Valid UserDto dto) { ... }
```
Если `UserDto` не прошёл валидацию — Spring бросает `MethodArgumentNotValidException`, клиент получает 400.

**@PathVariable / @RequestParam — ConstraintViolationException или HandlerMethodValidationException**

Здесь поведение зависит от версии Spring:

- **Spring 5 / Spring Boot 2:** для активации валидации на `@PathVariable`/`@RequestParam` контроллер должен быть помечен `@Validated` на уровне класса. При ошибке бросается `javax.validation.ConstraintViolationException`. По умолчанию Spring **не** имеет встроенного обработчика для этого исключения, поэтому без дополнительного `@ExceptionHandler` вернётся **HTTP 500 Internal Server Error**. Для корректного поведения нужно явно написать `@ExceptionHandler(ConstraintViolationException.class)` с `@ResponseStatus(HttpStatus.BAD_REQUEST)`.

- **Spring 6.1+ / Spring Boot 3.2+:** введена нативная поддержка *method validation*. Если параметры метода аннотированы ограничениями (`@Min`, `@NotBlank` и т. д.), Spring бросает `HandlerMethodValidationException`, и встроенный `ResponseEntityExceptionHandler` конвертирует его в **HTTP 400 Bad Request** автоматически.

**Итоговая таблица:**

| Аннотация | Исключение (Spring 5/Boot 2) | Исключение (Spring 6.1+/Boot 3.2+) | HTTP-статус по умолчанию |
|---|---|---|---|
| `@RequestBody @Valid` | `MethodArgumentNotValidException` | `MethodArgumentNotValidException` | **400** |
| `@PathVariable` / `@RequestParam` + `@Validated` на классе | `ConstraintViolationException` | `HandlerMethodValidationException` | 500 (Spring 5) / **400** (Spring 6.1+) |

---

### Вопрос 29. Что такое @ControllerAdvice и чем он отличается от @RestControllerAdvice? Если в одном приложении определены и локальный @ExceptionHandler в контроллере, и глобальный @ControllerAdvice для того же типа исключения — какой сработает?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Controller Advice :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-advice.html)

Официальная документация Spring описывает `@ControllerAdvice` как аннотацию, мета-аннотированную `@Component`, позволяющую объявить глобальные методы `@ExceptionHandler`, `@InitBinder` и `@ModelAttribute`, применяемые ко всем контроллерам. По умолчанию область действия — все контроллеры приложения, но её можно сузить через атрибуты `basePackages`, `annotations` или `assignableTypes`.

Документация явно указывает на приоритет:

> «Глобальные методы `@ExceptionHandler`, объявленные в `@ControllerAdvice`, применяются **после** локальных — тех, что объявлены непосредственно в `@Controller`.»

То есть локальный `@ExceptionHandler` в контроллере всегда имеет **более высокий приоритет**.

`@RestControllerAdvice` — это аннотация-«ярлык», объединяющая `@ControllerAdvice` и `@ResponseBody`. Фактически это `@ControllerAdvice`, методы-обработчики которого рендерят результат прямо в тело ответа.

#### Ответ от Claude

**@ControllerAdvice**

`@ControllerAdvice` — это специализация `@Component`, позволяющая централизованно объявить:
- `@ExceptionHandler` — глобальные обработчики исключений;
- `@InitBinder` — глобальная настройка `WebDataBinder`;
- `@ModelAttribute` — глобальное добавление атрибутов в модель.

Методы `@ExceptionHandler` внутри `@ControllerAdvice` могут возвращать как имена представлений (view names), так и объекты. Если нужно вернуть данные в тело ответа, необходимо дополнительно аннотировать метод `@ResponseBody`.

**@RestControllerAdvice**

`@RestControllerAdvice` = `@ControllerAdvice` + `@ResponseBody`. Это удобная аннотация для REST API: все методы `@ExceptionHandler` внутри неё автоматически сериализуют возвращаемое значение в тело ответа (через `HttpMessageConverter`, как правило — в JSON). Добавлять `@ResponseBody` к каждому методу не нужно.

Аналогия: `@RestControllerAdvice` относится к `@ControllerAdvice` так же, как `@RestController` относится к `@Controller`.

**Приоритет: локальный vs глобальный обработчик**

Когда одно и то же исключение может быть обработано и локальным `@ExceptionHandler` в контроллере, и глобальным в `@ControllerAdvice`, Spring выбирает **локальный** — он проверяется первым.

Алгоритм Spring при диспетчеризации исключений (`ExceptionHandlerExceptionResolver`):
1. Ищет `@ExceptionHandler`-методы непосредственно в самом контроллере (или его иерархии).
2. Если не найдено — перебирает все бины `@ControllerAdvice`, отсортированные по `@Order`/`@Priority` (меньшее число = выше приоритет).
3. Берёт первый подходящий метод.

Таким образом, локальный `@ExceptionHandler` всегда побеждает глобальный для того же типа исключения.

**Дополнительные нюансы:**
- Если `@ExceptionHandler` не найден ни локально, ни в `@ControllerAdvice` — исключение обрабатывается `DefaultHandlerExceptionResolver` или выбрасывается как 500.
- При нескольких `@ControllerAdvice`-бинах порядок определяется `@Order`/`Ordered`; совпадение с корневым исключением предпочтительнее совпадения с причиной (`cause`), но бин с более высоким приоритетом перекрывает бин с более низким даже при совпадении по `cause`.

---

### Вопрос 30. Как Jackson сериализует/десериализует объект по умолчанию? Что произойдёт при наличии циклических ссылок между объектами — как это решить без изменения модели данных?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Jackson ObjectMapper — jenkov.com](https://jenkov.com/tutorials/java-json/jackson-objectmapper.html)

По умолчанию Jackson сопоставляет поля JSON-объекта с полями Java-класса через **getter- и setter-методы**, следуя JavaBean-конвенции. Например, JSON-поле `brand` соответствует методам `getBrand()` / `setBrand()`. Фреймворк отрезает префикс `get`/`set` и приводит первую букву к нижнему регистру.

При сериализации Jackson вызывает публичные getter-методы. При десериализации — публичные setter-методы или, при их отсутствии, может использовать публичные поля напрямую. Тип `java.util.Date` сериализуется в миллисекунды (timestamp) по умолчанию. Дополнительные поля в JSON, не имеющие соответствующих setter-методов, по умолчанию игнорируются.

#### Ответ от Claude

**Сериализация по умолчанию**

Jackson `ObjectMapper` при вызове `writeValue()` / `writeValueAsString()` применяет следующие правила по умолчанию:

1. **Источник значений** — публичные getter-методы (JavaBean-конвенция): `getXxx()` → поле `xxx`. Публичные поля без getter также сериализуются. Приватные поля без getter игнорируются.
2. **Имена полей** — из имён getter-методов (strip `get`/`is`, lowercase first char).
3. **Null-поля** — включаются в JSON как `null`.
4. **Даты** — `java.util.Date` / `java.util.Calendar` сериализуются как число миллисекунд (epoch). `java.time.*` требует дополнительного модуля `jackson-datatype-jsr310`.
5. **Видимость** — по умолчанию Jackson видит: `PUBLIC_ONLY` для полей; `PUBLIC_ONLY` для getter-методов (со Spring Boot это стандартно расширено, но ядро Jackson работает именно так).

**Десериализация по умолчанию**

При вызове `readValue()`:
1. Требуется конструктор без аргументов (no-arg constructor) — иначе `InvalidDefinitionException`.
2. Значения устанавливаются через setter-методы или публичные поля.
3. Неизвестные поля в JSON по умолчанию вызывают `UnrecognizedPropertyException` (можно отключить через `DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES = false`).

**Циклические ссылки**

Если объект A ссылается на B, а B ссылается обратно на A, Jackson при попытке сериализации рекурсивно обходит граф объектов и падает с:
```
com.fasterxml.jackson.databind.exc.InvalidDefinitionException:
  Infinite recursion (StackOverflowError)
  (through reference chain: A["b"]->B["a"]->A["b"]->...)
```

**Решения без изменения модели данных**

1. **Jackson MixIn (лучший вариант для сторонних классов)**

   Создаётся абстрактный класс-примесь с аннотациями, который регистрируется в `ObjectMapper`. Исходные классы не трогаются:
   ```java
   abstract class UserMixin {
       @JsonManagedReference
       abstract List<Order> getOrders();
   }
   abstract class OrderMixin {
       @JsonBackReference
       abstract User getUser();
   }
   ObjectMapper mapper = new ObjectMapper();
   mapper.addMixIn(User.class, UserMixin.class);
   mapper.addMixIn(Order.class, OrderMixin.class);
   ```

2. **@JsonIdentityInfo через MixIn**

   Вместо `@JsonManagedReference`/`@JsonBackReference` применяется `@JsonIdentityInfo` — при повторной встрече объекта Jackson записывает только его идентификатор, а не весь объект:
   ```java
   @JsonIdentityInfo(generator = ObjectIdGenerators.IntSequenceGenerator.class, property = "@id")
   abstract class UserMixin {}
   mapper.addMixIn(User.class, UserMixin.class);
   ```
   Результат: `{"@id":1, "name":"Alice", "orders":[{"@id":2, "user":1}]}`.
   Недостаток: формат менее читаем и может быть несовместим с другими клиентами.

3. **Кастомный сериализатор через SimpleModule**

   Регистрируется `JsonSerializer<T>` с полным контролем над выводимыми полями:
   ```java
   SimpleModule module = new SimpleModule();
   module.addSerializer(User.class, new UserSerializer());
   mapper.registerModule(module);
   ```
   Даёт максимальную гибкость, но требует написания сериализатора вручную.

4. **Игнорирование «обратной» стороны через MixIn + @JsonIgnore**

   Если одна сторона цикла не нужна в JSON, её можно игнорировать без изменения модели:
   ```java
   abstract class OrderMixin {
       @JsonIgnore abstract User getUser();
   }
   mapper.addMixIn(Order.class, OrderMixin.class);
   ```
   Самое простое решение, но теряется часть данных.

**Сравнение подходов:**

| Подход | Изменяет модель | Данные сохраняются | Читаемость JSON |
|---|---|---|---|
| MixIn + `@JsonManagedReference`/`@JsonBackReference` | Нет | Частично (back side omitted) | Высокая |
| MixIn + `@JsonIdentityInfo` | Нет | Да | Средняя |
| Кастомный сериализатор | Нет | Управляемо | Высокая |
| MixIn + `@JsonIgnore` | Нет | Теряется | Высокая |

---
### Вопрос 31. Как настроить Jackson ObjectMapper глобально в Spring Boot: через JacksonAutoConfiguration, через Bean ObjectMapper или через Jackson2ObjectMapperBuilderCustomizer? Чем отличаются эти подходы и какой предпочтительнее?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Customizing Jackson in Spring Boot Applications — springcloud.io](https://www.springcloud.io/post/2023-03/springboot-jackson/)

Spring Boot автоматически настраивает Jackson через класс `JacksonAutoConfiguration` — это базовый уровень, который создаёт `ObjectMapper` посредством `Jackson2ObjectMapperBuilder`. Авторы выделяют три подхода:

1. **JacksonAutoConfiguration** — работает «из коробки»: Spring Boot сам формирует `ObjectMapper`, применяя свойства из `spring.jackson.*`. Никакого дополнительного кода не требуется.

2. **Jackson2ObjectMapperBuilderCustomizer** — рекомендуемый подход. Spring Boot собирает все бины, реализующие этот интерфейс, и применяет их к одному `Jackson2ObjectMapperBuilder`. Поддерживает упорядочивание (интерфейс `Ordered`), что позволяет контролировать порядок применения нескольких кастомайзеров.

3. **Прямое объявление бина `ObjectMapper`** — явно не рекомендуется. В статье указано: «В среде Spring Boot 2 не регистрируйте пользовательские объекты `ObjectMapper` в контейнере — это перезапишет исходную конфигурацию `ObjectMapper`!»

Вывод статьи: `Jackson2ObjectMapperBuilderCustomizer` является предпочтительным методом, так как позволяет расширять, а не заменять конфигурацию по умолчанию.

#### Ответ от Claude

**Три подхода к глобальной настройке Jackson ObjectMapper в Spring Boot**

**1. JacksonAutoConfiguration (неявный, «из коробки»)**

`JacksonAutoConfiguration` — авто-конфигурация Spring Boot, которая активируется при наличии Jackson в classpath (`@ConditionalOnClass(ObjectMapper.class)`). Она:
- создаёт бин `ObjectMapper` через `Jackson2ObjectMapperBuilder`;
- автоматически регистрирует все бины типа `com.fasterxml.jackson.databind.Module`;
- позволяет управлять настройками через `application.properties` / `application.yml`:

```yaml
spring:
  jackson:
    serialization:
      write-dates-as-timestamps: false
    deserialization:
      fail-on-unknown-properties: false
    default-property-inclusion: non_null
```

Этот уровень покрывает большинство простых нужд без написания кода.

**2. Jackson2ObjectMapperBuilderCustomizer (рекомендуемый подход)**

Реализация интерфейса `Jackson2ObjectMapperBuilderCustomizer` позволяет дополнить стандартный `ObjectMapper`, не отключая авто-конфигурацию Spring Boot:

```java
@Configuration(proxyBeanMethods = false)
public class JacksonConfig {

    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jsonCustomizer() {
        return builder -> {
            builder.serializationInclusion(JsonInclude.Include.NON_NULL);
            builder.failOnUnknownProperties(false);
            builder.modulesToInstall(new JavaTimeModule());
            builder.dateFormat(new SimpleDateFormat("yyyy-MM-dd"));
        };
    }
}
```

Ключевые преимущества:
- **Не отключает авто-конфигурацию** — работает поверх дефолтных настроек Spring Boot.
- **Компонуемость** — можно зарегистрировать несколько бинов-кастомайзеров; они применяются в порядке, заданном через `@Order` или интерфейс `Ordered` (встроенный кастомайзер Spring Boot имеет порядок `0`).
- **Применяется ко всем** `ObjectMapper`-бинам, создаваемым через `Jackson2ObjectMapperBuilder`, включая `XmlMapper` при наличии Jackson XML.

**3. Прямое объявление бина ObjectMapper (не рекомендуется для большинства случаев)**

```java
@Bean
@Primary
public ObjectMapper objectMapper() {
    ObjectMapper mapper = new ObjectMapper();
    mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    mapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
    return mapper;
}
```

Поведение: **полностью отключает авто-конфигурацию** `ObjectMapper` Spring Boot. Вы теряете:
- автоматическую регистрацию `Module`-бинов;
- интеграцию с `spring.jackson.*` свойствами;
- настройки, добавленные другими `Jackson2ObjectMapperBuilderCustomizer`.

Это оправдано только тогда, когда нужен полный контроль над маппером (например, изолированный маппер для конкретного компонента). В таком случае его не следует помечать как `@Primary` без веской причины.

**Итоговое сравнение**

| Подход | Отключает авто-конфигурацию | Компонуемость | Рекомендуется |
|---|---|---|---|
| `spring.jackson.*` свойства | Нет | — | Да (для простых настроек) |
| `Jackson2ObjectMapperBuilderCustomizer` | Нет | Да (порядок через `@Order`) | **Да (предпочтительный)** |
| Бин `ObjectMapper` | **Да** | Нет | Только для полного контроля |

**Вывод:** `Jackson2ObjectMapperBuilderCustomizer` — золотой стандарт в Spring Boot. Он соответствует принципу «Convention over Configuration»: вы расширяете дефолтное поведение, не ломая его. Прямое объявление `ObjectMapper`-бина следует рассматривать как исключение, требующее осознанного решения.

---

### Вопрос 32. Что такое частичное обновление через PATCH в контексте Jackson? Как корректно обработать ситуацию, когда поле не пришло в JSON вообще (отсутствует) vs пришло явно как null — это разные намерения клиента, как их различить?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [jackson-databind-nullable — OpenAPITools on GitHub](https://github.com/OpenAPITools/jackson-databind-nullable)

Библиотека `jackson-databind-nullable` предоставляет обёртку `JsonNullable<T>`, которая позволяет полям DTO иметь **три состояния**:

1. **Undefined** — поле отсутствует в JSON (`JsonNullable.undefined()`).
2. **Null** — поле явно установлено в `null` (`JsonNullable.of(null)`).
3. **Значение** — поле содержит конкретное значение (`JsonNullable.of("Rex")`).

Типичный вариант использования — реализация JSON Merge Patch, где явный `null` означает «установить поле в null / удалить поле», а отсутствующее поле означает «не изменять значение».

Пример бина:
```java
public class Pet {
    public JsonNullable<String> name = JsonNullable.undefined();
}
```

Результаты сериализации:
```java
mapper.writeValueAsString(new Pet().name(JsonNullable.undefined()))  // {}
mapper.writeValueAsString(new Pet().name(JsonNullable.of(null)))     // {"name":null}
mapper.writeValueAsString(new Pet().name(JsonNullable.of("Rex")))    // {"name":"Rex"}
```

Для подключения нужно зарегистрировать `JsonNullableModule`:
```java
ObjectMapper mapper = new ObjectMapper();
mapper.registerModule(new JsonNullableModule());
```

#### Ответ от Claude

**Проблема: почему стандартный Jackson не различает absent и null**

При стандартной десериализации Jackson оба случая — `{"field": null}` и `{}` — приводят к одинаковому результату: поле Java-объекта равно `null`. Это делает невозможным различение двух семантически разных намерений клиента:

- **Поле отсутствует (`{}`)** — «не трогай это поле, оставь как есть».
- **Поле явно `null` (`{"field": null}`)** — «сбрось значение поля в null / удали его».

**Подход 1: JsonNullable из jackson-databind-nullable (рекомендуемый)**

Библиотека `jackson-databind-nullable` (OpenAPI Tools) предоставляет трёхсостоятельную обёртку:

```xml
<dependency>
    <groupId>org.openapitools</groupId>
    <artifactId>jackson-databind-nullable</artifactId>
    <version>0.2.6</version>
</dependency>
```

```java
public class UpdateUserRequest {
    private JsonNullable<String> name = JsonNullable.undefined();
    private JsonNullable<String> email = JsonNullable.undefined();
    // getters/setters
}
```

Регистрация модуля:
```java
@Bean
public Jackson2ObjectMapperBuilderCustomizer jsonCustomizer() {
    return builder -> builder.modulesToInstall(new JsonNullableModule());
}
```

Обработка в сервисе:
```java
public void patch(Long id, UpdateUserRequest req) {
    User user = userRepository.findById(id).orElseThrow();
    
    if (req.getName().isPresent()) {
        user.setName(req.getName().get()); // может быть null — это намеренно
    }
    // если !isPresent() — поле не трогаем
    
    userRepository.save(user);
}
```

**Подход 2: Кастомная обёртка PatchField / OptionalUpdate**

Можно реализовать собственный трёхсостоятельный тип без сторонних зависимостей:

```java
public class Patch<T> {
    private final boolean present;
    private final T value;

    private Patch(boolean present, T value) {
        this.present = present;
        this.value = value;
    }

    public static <T> Patch<T> absent() {
        return new Patch<>(false, null);
    }

    public static <T> Patch<T> of(T value) {
        return new Patch<>(true, value);
    }

    public boolean isPresent() { return present; }
    public T getValue() { return value; }
}
```

Требуется кастомный `JsonDeserializer`, который вызывает `Patch.absent()` при отсутствии поля (переопределить `getAbsentValue()`) и `Patch.of(null)` или `Patch.of(value)` при десериализации.

**Подход 3: getAbsentValue() в JsonDeserializer (Jackson 2.9+)**

Jackson 2.9 добавил метод `getAbsentValue(DeserializationContext ctxt)` в `JsonDeserializer`. Он вызывается, когда поле **отсутствует** в JSON (в отличие от `getNullValue`, который вызывается при токене `null`). Переопределив оба метода, можно вернуть разные сигнальные значения:

```java
public class ThreeStateDeserializer extends JsonDeserializer<String> {
    public static final String ABSENT_MARKER = "ABSENT";

    @Override
    public String deserialize(JsonParser p, DeserializationContext ctxt)
            throws IOException {
        return p.getValueAsString(); // обычное значение
    }

    @Override
    public String getNullValue(DeserializationContext ctxt) {
        return null; // явный null из JSON
    }

    @Override
    public String getAbsentValue(DeserializationContext ctxt) {
        return ABSENT_MARKER; // поле вообще не пришло
    }
}
```

**Почему не `Optional<T>`?**

`Optional` имеет только два состояния: `Optional.empty()` (аналог null) и `Optional.of(value)`. Он не может различить «поле отсутствует» и «поле явно null» — оба случая могут маппиться в `Optional.empty()`. К тому же `Optional` не предназначен для полей POJO (только как тип возврата методов). Именно поэтому существует `JsonNullable`.

**Итог**

| Состояние JSON | `JsonNullable` результат | Смысл |
|---|---|---|
| Поле отсутствует | `JsonNullable.undefined()` / `!isPresent()` | Не изменять |
| `"field": null` | `JsonNullable.of(null)` / `isPresent() = true, get() = null` | Обнулить |
| `"field": "value"` | `JsonNullable.of("value")` / `isPresent() = true, get() = "value"` | Обновить |

Для production-кода рекомендуется `JsonNullable` из `jackson-databind-nullable` — он хорошо интегрируется с MapStruct и генераторами OpenAPI.

---

### Вопрос 33. Как работает @RequestMapping с параметром produces/consumes? Что произойдёт, если клиент пришлёт Content-Type: application/xml, а в classpath нет JAXB — какой статус вернёт Spring и почему?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [415 Unsupported MediaType in Spring Application — Baeldung](https://www.baeldung.com/spring-415-unsupported-mediatype)

Статус **415 Unsupported Media Type** означает, что origin-сервер отказывается обслуживать запрос, потому что формат тела запроса не поддерживается данным методом на данном ресурсе. Типичная причина — несоответствие между `Content-Type`-заголовком запроса клиента и тем, что объявлено в атрибуте `consumes` аннотации (`@PostMapping(value = "/", consumes = "application/xml")`). Если же у сервера нет зарегистрированного `HttpMessageConverter` для нужного типа (например, XML без JAXB-зависимости), Spring выбрасывает `HttpMediaTypeNotSupportedException`, которое маппится на **HTTP 415**. Решения: добавить несколько типов в `consumes = {"application/xml","application/json"}` или добавить JAXB-зависимость.

#### Ответ от Claude

**Как работают атрибуты consumes и produces в @RequestMapping**

**`consumes`** — ограничивает сопоставление метода по заголовку `Content-Type` входящего запроса:

```java
@PostMapping(value = "/users", consumes = "application/json")
public ResponseEntity<User> createUser(@RequestBody User user) { ... }
```

Если `Content-Type` запроса не совпадает — Spring выбрасывает `HttpMediaTypeNotSupportedException` → **HTTP 415 Unsupported Media Type**.

**`produces`** — ограничивает сопоставление метода по заголовку `Accept` запроса (что клиент хочет получить в ответе):

```java
@GetMapping(value = "/users/{id}", produces = "application/json")
public ResponseEntity<User> getUser(@PathVariable Long id) { ... }
```

Если `Accept`-заголовок клиента не совпадает ни с одним `produces` — Spring выбрасывает `HttpMediaTypeNotAcceptableException` → **HTTP 406 Not Acceptable**.

Оба атрибута поддерживают массивы, шаблоны (`application/*`) и отрицание (`!application/xml`). Настройки на уровне типа (`@RequestMapping` на классе) наследуются всеми методами, а аннотации на методе их переопределяют.

**Что происходит, когда клиент шлёт Content-Type: application/xml, а JAXB нет в classpath**

Цепочка событий в Spring MVC:

1. Запрос приходит с заголовком `Content-Type: application/xml`.
2. Spring ищет `HttpMessageConverter`, способный читать `application/xml` для целевого типа (например, `Jaxb2RootElementHttpMessageConverter`).
3. `Jaxb2RootElementHttpMessageConverter` регистрируется **только если JAXB присутствует в classpath** (условие `@ConditionalOnClass`). Если JAXB нет — конвертер не зарегистрирован.
4. Альтернативный XML-конвертер `MappingJackson2XmlHttpMessageConverter` регистрируется только если присутствует `jackson-dataformat-xml`.
5. Если ни один конвертер не найден — Spring DispatcherServlet получает исключение `HttpMediaTypeNotSupportedException`.
6. `DefaultHandlerExceptionResolver` перехватывает его и устанавливает статус ответа **HTTP 415 Unsupported Media Type**.

Важно: если endpoint не имеет атрибута `consumes`, Spring всё равно вернёт **415**, потому что при разборе тела запроса (`@RequestBody`) ищется конвертер — и не находится. Сам маршрут может совпасть, но десериализация провалится.

**Отличие 415 от 406:**

| Сценарий | Атрибут | Заголовок клиента | HTTP статус |
|---|---|---|---|
| Клиент шлёт XML, сервер не может прочитать | `consumes` / отсутствие конвертера | `Content-Type` | **415** |
| Клиент хочет XML в ответе, сервер не может отдать | `produces` / отсутствие конвертера | `Accept` | **406** |

**Практические рекомендации**

Для поддержки XML в Spring Boot нужно добавить одну из зависимостей:

```xml
<!-- Вариант 1: Jackson XML (рекомендуется для Spring Boot) -->
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
</dependency>

<!-- Вариант 2: Jakarta JAXB (Java 11+) -->
<dependency>
    <groupId>jakarta.xml.bind</groupId>
    <artifactId>jakarta.xml.bind-api</artifactId>
</dependency>
<dependency>
    <groupId>com.sun.xml.bind</groupId>
    <artifactId>jaxb-impl</artifactId>
    <scope>runtime</scope>
</dependency>
```

Без этих зависимостей при получении `Content-Type: application/xml` Spring вернёт **415** независимо от наличия атрибута `consumes` — потому что нет ни одного `HttpMessageConverter`, умеющего читать XML.

---
### Вопрос 34. Какие существуют стратегии версионирования REST API (URI, заголовок, медиатип)? Сравните их плюсы и минусы и объясните, когда какую выбрать.

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [API Versioning :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc-versioning.html)

Spring Framework поддерживает несколько стратегий версионирования REST API.

**1. URI Path Versioning (версия в пути URI)**

Версия включается непосредственно в URL-адрес: `/api/v1/users`, `/api/v2/users`.

Плюсы:
- Наиболее очевидна и понятна клиентам — версия видна прямо в браузерной строке.
- Легко кэшируется на уровне CDN/прокси: каждая версия имеет отдельный URI.
- Просто тестировать вручную (cURL, браузер).

Минусы:
- Нарушает принцип REST: URI должен однозначно идентифицировать ресурс, а не его версию.
- Приводит к дублированию определений эндпоинтов в коде.
- Кэш вынужден хранить несколько копий одного ресурса — по одной на каждую версию API, что снижает hit rate.

**2. Header Versioning (версия в заголовке запроса)**

Клиент передаёт пользовательский заголовок: `API-Version: 2.0`.

Плюсы:
- URI остаётся чистым и ресурсо-ориентированным.
- Соответствует принципам REST.
- Один набор URL обслуживает все версии.

Минусы:
- Не видна в адресной строке браузера.
- Сложнее тестировать вручную.
- Клиент должен явно знать, какой заголовок указывать.
- Потенциальные проблемы с клиентским кэшем (кэш HTTP опирается только на URI).

**3. Media Type / Content Negotiation Versioning (версия в медиатипе)**

Версия передаётся через заголовок `Accept`: `Accept: application/json;version=2.0` или через vendor-тип: `Accept: application/vnd.myapp.v2+json`.

Плюсы:
- Семантически корректно: версия описывает формат представления ресурса.
- URI не изменяется, API остаётся RESTful.
- Используется стандартный механизм согласования содержимого HTTP.

Минусы:
- Для корректного кэширования требуется заголовок `Vary` на стороне сервера.
- Сложнее для клиентов — нужно уметь строить нестандартные `Accept`-заголовки.
- Менее распространено, меньше знакомо разработчикам.
- Сложность обработки переносится в контроллеры.

**4. Query Parameter Versioning (версия в параметре запроса)**

Версия передаётся параметром URL: `/api/users?version=2`.

Плюсы:
- Прост в реализации и тестировании.
- Виден в URL, но не меняет структуру пути.

Минусы:
- Часто считается антипаттерном.
- Проблемы с кэшированием.
- Менее RESTful, чем заголовочный подход.

**Когда что выбирать:**
- **URI versioning** — если важна максимальная очевидность для клиентов, нужна изоляция по деплойменту/кэшированию или API публичное.
- **Header versioning** — для внутренних/партнёрских API, где команды контролируют клиентов; хорошо масштабируется при частых минорных изменениях.
- **Media type versioning** — если строгое следование REST-стандарту принципиально; применяется в сложных системах с разнообразными форматами данных.

#### Ответ от Claude

**Четыре основных стратегии версионирования REST API**

Источники для проверки: [Spring Framework Docs — API Versioning](https://docs.spring.io/spring-framework/reference/web/webmvc-versioning.html), [restfulapi.net — Versioning](https://restfulapi.net/versioning/), [Baeldung — Versioning a REST API](https://www.baeldung.com/rest-versioning).

---

**1. URI Path Versioning**

```
GET /api/v1/users/123
GET /api/v2/users/123
```

| Плюсы | Минусы |
|-------|--------|
| Очевидна для клиентов | Нарушает принцип уникальности URI в REST |
| Кэшируется на CDN без настроек | Дублирует эндпоинты в коде |
| Просто тестировать | Снижает cache hit rate (разные URI для одного ресурса) |
| Отдельный деплой каждой версии | Нет гибкости: любое изменение требует новой версии всего API |

---

**2. Custom Header Versioning**

```
GET /api/users/123
API-Version: 2.0
```

| Плюсы | Минусы |
|-------|--------|
| URI остаётся чистым | Невидима в браузерной строке |
| Соответствует REST | Сложнее тестировать вручную |
| Один URL для всех версий | Клиент должен знать имя заголовка |
| Гибко: можно версионировать отдельные ресурсы | Стандартные HTTP-кэши не учитывают пользовательские заголовки без настройки `Vary` |

---

**3. Media Type (Content Negotiation) Versioning**

```
GET /api/users/123
Accept: application/vnd.myapp.v2+json
```

или через параметр медиатипа:

```
Accept: application/json;version=2.0
```

| Плюсы | Минусы |
|-------|--------|
| Семантически корректно (версия = формат представления) | Клиенту сложно строить заголовки |
| Полностью RESTful | Требует `Vary: Accept` для корректного кэширования |
| URI не меняется | Сложность уходит в контроллеры |
| Стандартный механизм HTTP | Малознакома многим разработчикам |

---

**4. Query Parameter Versioning**

```
GET /api/users/123?version=2
```

Используется редко: удобна для тестирования, но считается антипаттерном из-за проблем с кэшированием и семантикой URL.

---

**Расхождения между источниками:**
- restfulapi.net считает URI versioning наиболее распространённой на практике, несмотря на нарушение REST-принципов.
- Spring Framework документация рекомендует header versioning как баланс между чистотой URI и удобством.
- Baeldung отмечает, что на практике самой популярной остаётся URI-стратегия из-за простоты.

**Итоговые рекомендации:**
- **URI versioning** — публичные API, строгая изоляция версий по деплою, важна простота для сторонних клиентов.
- **Header versioning** — внутренние и партнёрские API, когда клиент подконтролен, нужны чистые URI.
- **Media type versioning** — API с несколькими форматами данных, строгое следование REST-стандарту.
- **Query parameter versioning** — только для прототипирования; избегать в продакшене.

Не смешивать стратегии в одном API — это создаёт конфликты в маршрутизации.

---

### Вопрос 35. Что такое CORS и как работает preflight-запрос? Какие заголовки обязан вернуть сервер в ответе на OPTIONS-запрос, и что произойдёт, если их не будет?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Cross-Origin Resource Sharing (CORS) — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)

**CORS (Cross-Origin Resource Sharing)** — механизм на основе HTTP-заголовков, позволяющий серверу указать браузеру, каким источникам (origins) разрешено читать его ресурсы. Источник (origin) определяется схемой, доменом и портом.

**Как работает preflight-запрос:**

Для «небезопасных» запросов браузер автоматически отправляет предварительный (preflight) запрос методом OPTIONS перед отправкой фактического запроса. Это позволяет серверу подтвердить или отклонить запрос до передачи данных.

Пример: JavaScript с `https://foo.example` делает POST с нестандартным заголовком на `https://bar.other`. Браузер сначала отправляет:

```http
OPTIONS /doc HTTP/1.1
Host: bar.other
Origin: https://foo.example
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type,x-pingother
```

**Заголовки, которые сервер обязан вернуть в ответе на OPTIONS:**

1. `Access-Control-Allow-Origin` — разрешённый источник (или `*`).
2. `Access-Control-Allow-Methods` — список разрешённых HTTP-методов.
3. `Access-Control-Allow-Headers` — список разрешённых пользовательских заголовков.
4. `Access-Control-Max-Age` (опционально) — время кэширования preflight-ответа в секундах.

Пример корректного ответа сервера:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://foo.example
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: X-PINGOTHER, Content-Type
Access-Control-Max-Age: 86400
```

**Что произойдёт, если заголовки отсутствуют:**

Браузер заблокирует ответ. JavaScript-код не получит доступа к ответу. Детали ошибки из соображений безопасности скрыты от кода, но отображаются в консоли разработчика:

```
Access to XMLHttpRequest from origin 'https://foo.example' has been blocked
by CORS policy: No 'Access-Control-Allow-Origin' header is present on the
requested resource.
```

**Простые запросы (Simple Requests) — когда preflight не нужен:**

Preflight пропускается, если запрос удовлетворяет всем условиям:
- Метод: GET, HEAD, или POST.
- Заголовки: только CORS-safelisted (Accept, Accept-Language, Content-Language, Content-Type с ограниченными MIME-типами).
- Content-Type: `application/x-www-form-urlencoded`, `multipart/form-data`, или `text/plain`.

#### Ответ от Claude

**CORS и механизм preflight-запроса**

Источники: [MDN — CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS), [MDN — Preflight request](https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request), [Baeldung CS — CORS Preflight](https://www.baeldung.com/cs/cors-preflight-requests).

---

**Что такое CORS**

CORS — механизм HTTP, позволяющий браузеру выполнять запросы к ресурсам из другого источника (origin). Origin = схема + домен + порт. Запрос считается кросс-доменным, если хотя бы один из этих компонентов отличается.

По умолчанию браузер блокирует кросс-доменные запросы (политика Same-Origin Policy). CORS позволяет серверу явно разрешить доступ с указанных источников через специальные HTTP-заголовки.

---

**Что триггерит preflight**

Preflight-запрос (OPTIONS) отправляется браузером автоматически, если запрос НЕ является «простым»:

| Условие «простого» запроса | Что вызывает preflight |
|---|---|
| Метод GET/HEAD/POST | Методы PUT, DELETE, PATCH и др. |
| Только safelisted-заголовки | Любой пользовательский заголовок (например, `Authorization`, `X-Custom-Header`) |
| Content-Type: `text/plain`, `application/x-www-form-urlencoded`, `multipart/form-data` | Content-Type: `application/json`, `text/xml` и др. |

---

**Структура preflight-запроса**

```http
OPTIONS /api/resource HTTP/1.1
Origin: https://frontend.example.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization, Content-Type
```

Три заголовка, которые браузер отправляет в preflight:
- `Origin` — источник, с которого исходит запрос.
- `Access-Control-Request-Method` — метод, который будет использован в основном запросе.
- `Access-Control-Request-Headers` — нестандартные заголовки основного запроса.

---

**Заголовки, которые сервер ОБЯЗАН вернуть в ответе на OPTIONS**

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://frontend.example.com
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 3600
```

| Заголовок | Обязательность | Описание |
|---|---|---|
| `Access-Control-Allow-Origin` | Обязателен | Разрешённый origin (`*` или конкретный домен) |
| `Access-Control-Allow-Methods` | Обязателен | Перечень разрешённых HTTP-методов |
| `Access-Control-Allow-Headers` | Обязателен, если запрос содержит `Access-Control-Request-Headers` | Разрешённые заголовки |
| `Access-Control-Max-Age` | Опционален | Время кэширования preflight-ответа (секунды) |
| `Access-Control-Allow-Credentials` | Требуется при работе с куками/сессиями | Разрешение на передачу credentials |

**Важно:** при `Access-Control-Allow-Credentials: true` нельзя использовать `Access-Control-Allow-Origin: *` — нужно указывать конкретный origin.

---

**Что происходит при отсутствии CORS-заголовков**

1. Браузер получает ответ на OPTIONS-запрос без `Access-Control-Allow-Origin`.
2. Браузер блокирует основной запрос — он не отправляется вовсе.
3. JavaScript-код получает ошибку сети (не HTTP-статус), детали скрыты из соображений безопасности.
4. В консоли DevTools появляется ошибка вида: `CORS policy: No 'Access-Control-Allow-Origin' header`.
5. Сетевой запрос при этом дошёл до сервера — именно поэтому CORS не является механизмом защиты сервера; это защита браузера от чтения ответа злоумышленным скриптом.

---

**Расхождений между MDN и Baeldung по данной теме не обнаружено** — оба источника согласуются в описании механизма preflight и требуемых заголовков.

---

### Вопрос 36. Как настроить CORS в Spring Boot: через @CrossOrigin, через WebMvcConfigurer и через CorsFilter? Чем эти подходы отличаются и в каком порядке применяются?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CORS :: Spring Framework](https://docs.spring.io/spring-framework/reference/web/webmvc-cors.html)

Spring Framework предоставляет три основных способа конфигурации CORS.

**1. @CrossOrigin — аннотация уровня метода или класса**

```java
@RestController
@RequestMapping("/account")
public class AccountController {

    @CrossOrigin(origins = "https://domain2.com", maxAge = 3600)
    @GetMapping("/{id}")
    public Account retrieve(@PathVariable Long id) {
        // ...
    }
}
```

По умолчанию (без параметров): разрешены все origins, все заголовки, все HTTP-методы, которым сопоставлен метод контроллера; `allowCredentials` отключён; `maxAge` — 30 минут.

**2. Глобальная конфигурация через WebMvcConfigurer**

```java
@Configuration
public class WebConfiguration implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://domain1.com", "https://domain2.com")
            .allowedMethods("GET", "PUT")
            .allowedHeaders("header1", "header2")
            .exposedHeaders("header1", "header2")
            .allowCredentials(true)
            .maxAge(3600);
    }
}
```

**3. CorsFilter — уровень сервлет-фильтра**

```java
CorsConfiguration config = new CorsConfiguration();
config.setAllowCredentials(true);
config.addAllowedOrigin("https://domain1.com");
config.addAllowedHeader("*");
config.addAllowedMethod("*");

UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
source.registerCorsConfiguration("/**", config);

CorsFilter filter = new CorsFilter(source);
```

**Правила объединения конфигураций:**

Глобальная и локальная конфигурации в целом аддитивны. Многозначные атрибуты (origins, methods, headers) объединяются. Одиночные атрибуты (`allowCredentials`, `maxAge`) при конфликте: локальная конфигурация (@CrossOrigin) переопределяет глобальную.

#### Ответ от Claude

**Три способа настройки CORS в Spring Boot**

Источники: [Spring Framework Docs — CORS](https://docs.spring.io/spring-framework/reference/web/webmvc-cors.html), [Spring Security Docs — CORS](https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html), [Baeldung — CORS with Spring](https://www.baeldung.com/spring-cors).

---

**Способ 1: @CrossOrigin (уровень контроллера/метода)**

Наиболее гранулярный подход. Применяется к конкретному методу или всему контроллеру.

```java
// На уровне класса — применяется ко всем методам
@CrossOrigin(origins = "https://frontend.example.com", maxAge = 3600)
@RestController
@RequestMapping("/api/users")
public class UserController {

    // На уровне метода — переопределяет/дополняет настройки класса
    @CrossOrigin("https://admin.example.com")
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) { ... }
}
```

Значения по умолчанию без параметров:
- `origins` — все (`*`).
- `methods` — методы, объявленные в `@RequestMapping`.
- `allowedHeaders` — все.
- `allowCredentials` — `false`.
- `maxAge` — 1800 секунд (30 минут).

Применяется: внутри Spring MVC (через `HandlerMapping`), обрабатывается до передачи запроса в `DispatcherServlet`.

---

**Способ 2: WebMvcConfigurer (глобальная конфигурация MVC)**

Централизованная настройка для всего приложения или набора URL-паттернов.

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://frontend.example.com")
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("Authorization", "Content-Type")
            .exposedHeaders("X-Custom-Header")
            .allowCredentials(true)
            .maxAge(3600);
    }
}
```

Применяется: через `HandlerMapping` в Spring MVC, обрабатывается вместе с `@CrossOrigin` и объединяется с ней (аддитивно для многозначных атрибутов).

---

**Способ 3: CorsFilter (уровень сервлет-фильтра)**

Наиболее низкоуровневый подход. Обрабатывает запросы на уровне Servlet Filter — раньше, чем Spring MVC и Spring Security.

```java
@Bean
public CorsFilter corsFilter() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowCredentials(true);
    config.addAllowedOrigin("https://frontend.example.com");
    config.addAllowedHeader("*");
    config.addAllowedMethod("*");

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);

    return new CorsFilter(source);
}
```

**Критически важно при использовании Spring Security:** preflight OPTIONS-запросы не содержат cookies и сессионных данных. Если Spring Security проверяет аутентификацию до обработки CORS, preflight будет отклонён с 401/403. Поэтому `CorsFilter` должен быть зарегистрирован перед фильтрами Spring Security:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.cors(withDefaults()); // использует существующий CorsFilter или MVC-конфигурацию
    ...
}
```

---

**Порядок применения и приоритет**

Обработка CORS-запроса в Spring Boot (по убыванию приоритета):

```
1. CorsFilter (Servlet Filter уровень)
       |
2. HandlerMapping (Spring MVC)
   ├── @CrossOrigin на методе (наивысший приоритет среди MVC)
   ├── @CrossOrigin на классе
   └── WebMvcConfigurer.addCorsMappings() (глобальная)
```

| Подход | Уровень | Приоритет | Когда использовать |
|---|---|---|---|
| `CorsFilter` | Servlet Filter | Выполняется первым (до Spring MVC и Spring Security) | Нужна CORS-обработка для не-MVC ресурсов или перед Spring Security |
| `WebMvcConfigurer` | Spring MVC | Глобальная MVC-конфигурация | Единые правила для всего приложения |
| `@CrossOrigin` на классе | Spring MVC | Переопределяет глобальную для данного контроллера | Специфические правила для контроллера |
| `@CrossOrigin` на методе | Spring MVC | Наивысший приоритет среди MVC | Специфические правила для одного эндпоинта |

**Правила объединения @CrossOrigin и WebMvcConfigurer:**
- Многозначные атрибуты (`origins`, `methods`, `headers`) — объединяются аддитивно.
- Одиночные атрибуты (`allowCredentials`, `maxAge`) — локальная (`@CrossOrigin`) переопределяет глобальную.

**Расхождение источников:** Spring Framework Docs описывает `CorsFilter` как независимый механизм, не интегрированный с MVC. Spring Security Docs уточняет: при совместном использовании Spring Security `CorsFilter` должен быть явно зарегистрирован перед фильтрами безопасности, иначе preflight-запросы будут отклоняться из-за отсутствия аутентификационных данных.
### Вопрос 37. Почему Spring Security может блокировать CORS-запрос ещё до того, как сработает конфигурация Spring MVC? Как правильно интегрировать CORS с Spring Security?

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [CORS :: Spring Security — docs.spring.io](https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html)

CORS должен быть обработан до Spring Security, потому что предварительный (preflight) запрос не содержит cookies (в частности, `JSESSIONID`). Если в запросе нет cookies, а Spring Security стоит первым в цепочке фильтров, он определяет пользователя как неаутентифицированного и отклоняет запрос. Поэтому CORS-фильтр обязан выполниться раньше, чем фильтры аутентификации и авторизации Spring Security.

Самый простой способ обеспечить этот порядок — использовать `CorsFilter`, зарегистрированный перед `SecurityFilterChain`.

**Вариант 1: подключить CORS через Spring Security с источником конфигурации**

```java
@Bean
UrlBasedCorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOrigins(Arrays.asList("https://example.com"));
    configuration.setAllowedMethods(Arrays.asList("GET", "POST"));
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", configuration);
    return source;
}
```

**Вариант 2 (рекомендованный): делегировать к конфигурации Spring MVC**

Если Spring MVC присутствует в classpath и `CorsConfigurationSource` не объявлен явно, Spring Security автоматически использует CORS-конфигурацию Spring MVC:

```java
@Configuration
@EnableWebSecurity
public class WebSecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(Customizer.withDefaults())
            // остальные настройки
            ;
        return http.build();
    }
}
```

Вызов `.cors(Customizer.withDefaults())` регистрирует `CorsFilter` Spring Security, который встаёт в начало `SecurityFilterChain`. Если в контексте объявлен бин `CorsConfigurationSource`, он используется; если нет — Spring Security ищет конфигурацию CORS, заданную аннотацией `@CrossOrigin` или `WebMvcConfigurer.addCorsMappings()`.

**Вариант 3: разные CORS-политики для разных цепочек фильтров**

```java
@Bean
@Order(0)
public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
    http
        .securityMatcher("/api/**")
        .cors(cors -> cors.configurationSource(apiConfigurationSource()));
    return http.build();
}

@Bean
@Order(1)
public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(webConfigurationSource()));
    return http.build();
}
```

#### Ответ от Claude

**Корень проблемы**

Браузер перед любым cross-origin-запросом с нестандартными заголовками или методами отправляет preflight-запрос методом `OPTIONS`. Этот запрос не несёт credentials: в нём нет сессионных cookies и заголовка `Authorization`. Spring Security обрабатывает все входящие запросы ещё до того, как `DispatcherServlet` передаёт управление Spring MVC. Поэтому, если CORS-логика не вынесена в фильтр, стоящий перед `SecurityFilterChain`, Spring Security видит `OPTIONS`-запрос без аутентификации и возвращает `401 Unauthorized` или `403 Forbidden`, так и не позволив браузеру получить CORS-заголовки.

**Почему Spring MVC CORS-конфигурации недостаточно**

`@CrossOrigin` и `WebMvcConfigurer.addCorsMappings()` работают внутри `DispatcherServlet` — уже после прохождения фильтров безопасности. Если Spring Security отклонит preflight раньше, до `DispatcherServlet` дело просто не дойдёт.

**Правильная интеграция**

1. Вызвать `.cors(Customizer.withDefaults())` в `HttpSecurity`. Spring Security добавит свой `CorsFilter` в начало `SecurityFilterChain` (до фильтров аутентификации).
2. Определить бин `CorsConfigurationSource` (через `UrlBasedCorsConfigurationSource`), чтобы правила были явными и не зависели от Spring MVC-конфигурации.
3. Никогда не использовать `.cors(CorsConfigurer::disable)` в production — это отключает интеграцию Spring Security с CORS, но не убирает защиту браузера.

**Порядок фильтров в цепочке**

```
Входящий запрос
  -> CorsFilter          (проверяет CORS, обрабатывает OPTIONS)
  -> SecurityFilterChain (аутентификация, авторизация)
  -> DispatcherServlet   (Spring MVC, контроллеры)
```

Расхождений между источниками не обнаружено: официальная документация Spring Security и Spring Framework описывают одну и ту же модель.

---

### Вопрос 38. В чём разница между фильтром (Filter/OncePerRequestFilter) и интерцептором (HandlerInterceptor) в Spring MVC? На каком этапе обработки запроса работает каждый из них и какой следует выбрать для конкретных задач?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [HandlerInterceptor (Spring Framework 7.0.7 API) — docs.spring.io](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/servlet/HandlerInterceptor.html)

`HandlerInterceptor` — интерфейс Spring MVC, позволяющий применять сквозную функциональность к обработке HTTP-запросов в определённых точках пайплайна. Входит в состав всех реализаций `HandlerMapping`.

Интерфейс содержит три метода:

- **`preHandle(request, response, handler)`** — выполняется до вызова обработчика (контроллера). Возвращает `boolean`: `true` — продолжить обработку, `false` — прервать цепочку и взять управление на себя.
- **`postHandle(request, response, handler, modelAndView)`** — выполняется после успешного завершения обработчика, но до рендеринга представления. Для методов, аннотированных `@ResponseBody` или возвращающих `ResponseEntity`, ответ уже записан к этому моменту и изменить его невозможно.
- **`afterCompletion(request, response, handler, ex)`** — выполняется после рендеринга представления и завершения всей обработки запроса. Вызывается только если `preHandle()` вернул `true`. Используется для освобождения ресурсов.

Интерцепторы применимы для удобных задач сквозной функциональности в рамках Spring MVC, однако **не подходят в качестве уровня безопасности** из-за потенциального несоответствия при сопоставлении путей аннотированных контроллеров. Для задач безопасности рекомендуется Spring Security или фильтры уровня сервлета.

#### Ответ от Claude

**Этапы обработки запроса**

```
Входящий запрос
  -> Servlet Container (Tomcat/Jetty)
  -> Filter Chain (jakarta.servlet.Filter / OncePerRequestFilter)
  -> DispatcherServlet
       -> HandlerMapping -> определение обработчика
       -> preHandle()    (HandlerInterceptor)
       -> HandlerAdapter -> вызов контроллера
       -> postHandle()   (HandlerInterceptor)
       -> Рендеринг View
       -> afterCompletion() (HandlerInterceptor)
  -> Ответ клиенту
```

**Filter / OncePerRequestFilter**

- Является частью Servlet API (`jakarta.servlet.Filter`), не знает о Spring MVC.
- Выполняется **до** `DispatcherServlet`, то есть до любой обработки Spring.
- `OncePerRequestFilter` — базовый класс Spring, гарантирующий однократное выполнение фильтра за один цикл запроса (исключает повторный вызов при внутреннем `forward`).
- Может заменить объекты `HttpServletRequest`/`HttpServletResponse` обёртками, изменить тело запроса или ответа.
- Применяется для: логирования/трассировки (MDC), CORS, сжатия ответа, аутентификации по токену, rate limiting.

**HandlerInterceptor**

- Часть Spring MVC, работает **внутри** `DispatcherServlet` после определения обработчика.
- Имеет доступ к объекту обработчика (`Object handler`) и `ModelAndView`.
- Позволяет проверить аннотации конкретного метода-контроллера.
- **Важное ограничение:** при использовании `@ResponseBody` / `ResponseEntity` ответ уже зафиксирован внутри `HandlerAdapter` до вызова `postHandle()`, поэтому изменить тело ответа в `postHandle()` невозможно.
- Применяется для: проверки прав на уровне конкретного контроллера/метода, добавления атрибутов модели, аудита вызовов хендлеров.

**Сравнительная таблица**

| Критерий | Filter / OncePerRequestFilter | HandlerInterceptor |
|---|---|---|
| Уровень | Servlet Container | Spring MVC (DispatcherServlet) |
| Точка входа | До DispatcherServlet | После HandlerMapping |
| Доступ к хендлеру | Нет | Да (объект handler) |
| Доступ к ModelAndView | Нет | Да (в postHandle) |
| Замена request/response | Да | Нет |
| Настройка | FilterRegistrationBean / web.xml | WebMvcConfigurer.addInterceptors() |
| Безопасность | Рекомендовано | Не рекомендовано |

**Когда что выбирать**

- Если задача не зависит от Spring MVC (аутентификация, логирование, CORS, сжатие) — использовать `OncePerRequestFilter`.
- Если нужен доступ к информации об обработчике или модели Spring MVC — использовать `HandlerInterceptor`.
- Для задач безопасности всегда предпочтительны фильтры (Spring Security строится на них).

Расхождений между источниками не обнаружено. Официальная документация Spring Framework и Javadoc HandlerInterceptor описывают одну и ту же модель выполнения.

---

### Вопрос 39. Что такое RFC 7807 / RFC 9457 Problem Details for HTTP APIs? Какие обязательные поля определяет спецификация, какой Content-Type используется и как включить эту поддержку в Spring Boot 3?

**Категория:** REST/Web · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [RFC 9457: Problem Details for HTTP APIs — rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9457.html)

RFC 9457 определяет стандартный формат тела ошибочного HTTP-ответа. Спецификация описывает пять полей объекта «problem detail»; все они являются **необязательными**, однако рекомендованными:

- **`type`** — URI-ссылка, идентифицирующая тип проблемы. При отсутствии считается равным `"about:blank"`.
- **`status`** — HTTP-статус-код, применимый к данной проблеме.
- **`title`** — краткое человекочитаемое описание типа проблемы. Не должно меняться между разными вхождениями одного типа.
- **`detail`** — человекочитаемое объяснение конкретного вхождения проблемы.
- **`instance`** — URI-ссылка, идентифицирующая конкретное вхождение проблемы (например, путь запроса).

RFC 9457 пришёл на смену RFC 7807 и отличается от него тремя дополнениями:
1. Введён реестр типов проблем для обеспечения интероперабельности.
2. Добавлены рекомендации по обработке ситуаций с несколькими одновременными проблемами.
3. Расширены рекомендации по использованию неразыменуемых URI в поле `type`.

**Content-Type:** `application/problem+json` (JSON) или `application/problem+xml` (XML).

#### Ответ от Claude

**Что такое RFC 9457**

RFC 9457 (август 2023, заменяет RFC 7807 2016 года) — стандарт IETF, описывающий единый формат тела ошибочных HTTP-ответов. Цель — устранить разнобой в форматах ошибок между разными API и дать клиентам предсказуемую структуру для машинной обработки.

**Поля объекта problem detail**

Спецификация не делит поля на «обязательные» и «необязательные» в смысле схемы: все пять стандартных полей технически необязательны, но практически рекомендованы:

| Поле | Тип | Описание |
|---|---|---|
| `type` | URI string | Тип проблемы. Если отсутствует — подразумевается `"about:blank"` |
| `title` | string | Краткое описание типа (не конкретного случая) |
| `status` | integer | HTTP-статус-код |
| `detail` | string | Описание конкретного вхождения проблемы |
| `instance` | URI string | URI конкретного вхождения (обычно — путь запроса) |

Помимо стандартных полей спецификация допускает расширения: любые дополнительные поля (`extension members`) при сериализации в JSON выводятся на верхний уровень объекта.

Пример ответа:
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Failed",
  "status": 400,
  "detail": "Field 'email' must be a valid email address",
  "instance": "/api/users/register",
  "field": "email"
}
```

**Content-Type**

- JSON: `application/problem+json`
- XML: `application/problem+xml`

**Поддержка в Spring Boot 3 / Spring Framework 6**

Spring Framework 6 (используемый в Spring Boot 3) реализует RFC 9457 через три ключевых класса: `ProblemDetail`, `ErrorResponse` и `ErrorResponseException`.

**Способ 1: включить глобально через свойство**

```properties
# application.properties
spring.mvc.problemdetails.enabled=true
```

При включении `DefaultHandlerExceptionResolver` начинает оборачивать стандартные исключения Spring MVC (`MethodArgumentNotValidException`, `HttpMessageNotReadableException` и др.) в `ProblemDetail`.

**Способ 2: расширить `ResponseEntityExceptionHandler`**

```java
@ControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail detail = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage()
        );
        detail.setType(URI.create("https://api.example.com/errors/not-found"));
        detail.setTitle("Resource Not Found");
        detail.setProperty("resourceId", ex.getResourceId()); // extension field
        return detail;
    }
}
```

**Способ 3: исключение реализует `ErrorResponse`**

```java
public class OutOfStockException extends RuntimeException implements ErrorResponse {

    @Override
    public HttpStatusCode getStatusCode() {
        return HttpStatus.CONFLICT;
    }

    @Override
    public ProblemDetail getBody() {
        return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, getMessage());
    }
}
```

**i18n поддержка**

Spring автоматически ищет сообщения в `MessageSource` по шаблону:
```properties
problemDetail.title.com.example.ResourceNotFoundException=Resource Not Found
problemDetail.detail.com.example.ResourceNotFoundException=Resource {0} not found
```

**Расхождения между источниками:** RFC 9457 не вводит понятия «обязательных полей» в строгом смысле — все поля опциональны. Ряд статей (и некоторые ранние описания RFC 7807) ошибочно называет `type`, `title`, `status` обязательными. Официальный текст RFC 9457 прямо указывает, что все члены объекта необязательны, а `type` при отсутствии подразумевает `"about:blank"`. Spring Framework следует этому поведению: если `type` не задан явно, он не включается в ответ (по умолчанию `about:blank`).

---
### Вопрос 40. Как реализовать поддержку идемпотентности для POST-запросов через заголовок Idempotency-Key? Опишите серверный алгоритм обработки, хранения ключа и обнаружения повторного запроса.

**Категория:** REST/Web · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Idempotency-Key — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Idempotency-Key)

HTTP-заголовок `Idempotency-Key` позволяет клиенту сделать `POST`- и `PATCH`-запросы идемпотентными, присвоив каждому запросу уникальный идентификатор. Это позволяет безопасно повторить запрос при отсутствии ответа, не беспокоясь о дублировании побочных эффектов.

**Серверный алгоритм обработки**

```
1. Получен запрос с заголовком Idempotency-Key:
   
   ЕСЛИ ключ НОВЫЙ:
   ├─ Выполнить операцию в штатном режиме
   ├─ Сохранить ключ и ответ в хранилище
   └─ Вернуть нормальный ответ клиенту
   
   ЕСЛИ ключ УЖЕ СУЩЕСТВУЕТ (запрос завершён):
   ├─ НЕ выполнять операцию повторно
   └─ Вернуть сохранённый ответ
   
   ЕСЛИ ключ ОБРАБАТЫВАЕТСЯ (конкурентный запрос):
   └─ Вернуть 409 Conflict
   
   ЕСЛИ заголовок ОТСУТСТВУЕТ (обязательный endpoint):
   └─ Вернуть 400 Bad Request
```

**Опциональная защита от подмены тела запроса (idempotency fingerprint)**

Сервер может хранить контрольную сумму тела запроса («отпечаток»). При повторном запросе с тем же ключом, но другим телом — сравниваются отпечатки; при несовпадении возвращается `422 Unprocessable Content`.

**Коды ошибок:**

| Код | Условие |
|-----|---------|
| `400 Bad Request` | Заголовок отсутствует на обязательном endpoint |
| `409 Conflict` | Запрос с этим ключом уже обрабатывается |
| `422 Unprocessable Content` | Тот же ключ передан с другим телом |

**Пример запроса и повторной попытки:**

```http
POST /api/payments HTTP/1.1
Idempotency-Key: 9c7d2b4a-0e1f-6c83-5a2d-1b0f4e3c5a7d
Content-Type: application/json

{ "amount": 100, "currency": "USD" }
```

При сетевом сбое клиент повторяет запрос с тем же `Idempotency-Key`. Сервер распознаёт ключ и возвращает ранее сохранённый ответ без повторного списания.

#### Ответ от Claude

**Что такое Idempotency-Key и зачем он нужен**

`POST`-запросы по природе не идемпотентны: повторная отправка создаёт новый ресурс или применяет операцию снова. При сбое сети клиент не знает, дошёл ли запрос. Заголовок `Idempotency-Key` (IETF Draft: `draft-ietf-httpapi-idempotency-key-header`) позволяет клиенту пометить каждый логический запрос уникальным ключом (обычно UUID v4), а серверу — гарантировать однократное выполнение.

**Полный серверный алгоритм**

1. **Валидация входящего запроса.** Если endpoint требует ключа, а заголовок отсутствует — вернуть `400 Bad Request`.

2. **Атомарная проверка в хранилище.** Выполнить атомарную операцию (например, `INSERT ... ON CONFLICT DO NOTHING` в PostgreSQL или `SETNX` в Redis) с составным ключом `(client_id + idempotency_key)`. Это предотвращает race condition между параллельными запросами.

3. **Если ключ новый** — пометить запись как «в обработке» (статус `IN_PROGRESS`), выполнить бизнес-операцию, сохранить HTTP-статус и тело ответа, переключить статус в `COMPLETED`.

4. **Если ключ существует и статус `IN_PROGRESS`** — вернуть `409 Conflict`: параллельный запрос уже обрабатывается.

5. **Если ключ существует и статус `COMPLETED`** — вернуть сохранённый ответ без повторного выполнения.

6. **Опциональная проверка fingerprint.** При получении повторного запроса сравнить контрольную сумму тела (SHA-256 или CRC32) с сохранённой. При несовпадении — `422 Unprocessable Content`.

**Что хранить**

```
idempotency_keys (
  composite_key   TEXT PRIMARY KEY,  -- client_id + ":" + idempotency_key
  status          TEXT,              -- IN_PROGRESS | COMPLETED
  response_status INT,               -- HTTP-статус сохранённого ответа
  response_body   TEXT,              -- тело сохранённого ответа
  fingerprint     TEXT,              -- контрольная сумма тела запроса
  created_at      TIMESTAMP,
  expires_at      TIMESTAMP          -- TTL: обычно 24 ч — 7 дней
)
```

**Срок хранения ключей**

Согласно IETF Draft, сервер должен задокументировать политику истечения. На практике: от 24 часов (платёжные API) до 7 дней, в зависимости от бизнес-требований (Zuplo). Истёкшие ключи следует удалять фоновым процессом.

**Хранилище**

- **Redis** — оптимален для высоконагруженных сценариев: встроенный TTL, атомарная команда `SET NX EX`, низкая латентность.
- **Реляционная БД** — подходит, когда нужна транзакционная согласованность с основными данными (запись ключа и бизнес-данных в одной транзакции).

**Безопасность**

Составной ключ кэша должен включать идентификатор клиента (из токена авторизации), чтобы один клиент не мог перехватить ответ другого, передав угаданный ключ.

**Пример Spring-реализации (фильтр/перехватчик)**

```java
@Component
public class IdempotencyFilter extends OncePerRequestFilter {

    @Autowired
    private IdempotencyStore store;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws IOException, ServletException {
        String key = request.getHeader("Idempotency-Key");
        if (key == null) {
            chain.doFilter(request, response);
            return;
        }
        String compositeKey = resolveClientId(request) + ":" + key;

        IdempotencyRecord record = store.findByKey(compositeKey);
        if (record != null && record.isCompleted()) {
            // Повторный запрос — вернуть сохранённый ответ
            response.setStatus(record.getStatus());
            response.getWriter().write(record.getBody());
            return;
        }
        if (record != null && record.isInProgress()) {
            response.sendError(409, "Request is being processed");
            return;
        }

        store.markInProgress(compositeKey);
        CachingResponseWrapper wrapper = new CachingResponseWrapper(response);
        chain.doFilter(request, wrapper);
        store.complete(compositeKey, wrapper.getStatus(), wrapper.getBody());
    }
}
```

**Расхождения между источниками**

- MDN описывает базовый алгоритм без статуса `IN_PROGRESS`. IETF Draft явно требует возвращать `409 Conflict` при конкурентном запросе — это более строгое и корректное поведение.
- Zuplo рекомендует хранить полный HTTP-ответ (статус + тело), включая ошибочные ответы. MDN подчёркивает то же: сохранённый ответ возвращается даже если оригинальный запрос завершился ошибкой.

---

