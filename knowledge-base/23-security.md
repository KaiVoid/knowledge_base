# Безопасность приложений

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по безопасности →](../interview-questions/security-01.md)
> **Связанные области:** [[17-rest-web]], [[14-spring-boot]]

## Что это и зачем

Безопасность — обязательная составляющая промышленной разработки. Java-разработчик должен понимать
типовые угрозы (OWASP Top 10), механизмы аутентификации и авторизации, работу с токенами (JWT, OAuth2)
и уметь защищать приложения средствами Spring Security. Уязвимости вроде SQL-инъекций и XSS — частая
тема собеседований.

Безопасность строится на принципе «defence in depth» (эшелонированная оборона): несколько независимых
слоёв защиты так, чтобы прорыв одного слоя не означал компрометации всей системы. На практике это
выражается в сочетании проверенных фреймворков (Spring Security), правильных алгоритмов хранения
паролей, валидации входных данных, защищённых HTTP-заголовков и безопасных протоколов передачи.

## Ключевые подтемы

### Аутентификация vs авторизация

**Аутентификация** — проверка личности: «кто ты?». Реализуется через форм-логин, Basic Auth, токены,
сертификаты и т.д.

**Авторизация** — контроль доступа: «что тебе разрешено?». Реализуется через роли (`ROLE_ADMIN`),
полномочия (`permission:read`) и правила на уровне HTTP-запросов или методов.

Важно: авторизация всегда следует после успешной аутентификации, но они концептуально независимы.
Путать их — распространённая ошибка на собеседованиях.

---

### OWASP Top 10 (редакция 2021)

[OWASP Top 10:2021](https://owasp.org/Top10/) — стандарт де-факто для оценки рисков веб-приложений.
Десять категорий в порядке убывания риска:

| Код | Категория | Суть |
|-----|-----------|------|
| A01 | Broken Access Control | Нарушение контроля доступа — наиболее распространённая угроза |
| A02 | Cryptographic Failures | Слабое шифрование, передача данных в открытом виде |
| A03 | Injection | SQL, LDAP, OS-команды, XSS |
| A04 | Insecure Design | Архитектурные просчёты, отсутствие threat modeling |
| A05 | Security Misconfiguration | Дефолтные пароли, ненужные функции, открытые стек-трейсы |
| A06 | Vulnerable and Outdated Components | Зависимости с известными CVE |
| A07 | Identification and Authentication Failures | Слабые пароли, отсутствие MFA, уязвимые сессии |
| A08 | Software and Data Integrity Failures | Небезопасная CI/CD, десериализация |
| A09 | Security Logging and Monitoring Failures | Отсутствие audit-логов и алертов |
| A10 | Server-Side Request Forgery (SSRF) | Принуждение сервера делать запросы к внутренним ресурсам |

---

### SQL-инъекции и защита от них

SQL-инъекция (A03) — атака, при которой пользовательский ввод интерпретируется как часть SQL-запроса.
Пример уязвимого кода:

```java
// НЕБЕЗОПАСНО: конкатенация строк
String query = "SELECT * FROM users WHERE name = '" + userInput + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

Атакующий может передать `' OR '1'='1` и получить все строки таблицы, либо `'; DROP TABLE users; --`
для деструктивных действий.

**Защита 1 — Parameterized Queries (PreparedStatement)**

Наиболее надёжный способ, рекомендованный
[OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).
Параметры передаются отдельно от SQL-кода, СУБД никогда не интерпретирует их как команды:

```java
// БЕЗОПАСНО: параметризованный запрос
String query = "SELECT account_balance FROM user_data WHERE user_name = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, custname);
ResultSet results = pstmt.executeQuery();
```

**Защита 2 — ORM (JPA/Hibernate) с именованными параметрами**

```java
// БЕЗОПАСНО: JPQL с параметром
TypedQuery<User> q = em.createQuery(
    "SELECT u FROM User u WHERE u.name = :name", User.class);
q.setParameter("name", custname);
```

**Защита 3 — принцип минимальных привилегий**

Учётная запись приложения в БД должна иметь только необходимые разрешения (SELECT/INSERT/UPDATE,
но не DROP TABLE или GRANT).

---

### XSS (Cross-Site Scripting)

XSS — внедрение вредоносного JavaScript в страницы, которые видят другие пользователи. Есть три
разновидности: отражённый (Reflected), хранимый (Stored) и DOM-based.

Ключевые меры защиты согласно
[OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html):

- **Output Encoding** — кодировать данные в зависимости от контекста:
  - HTML-контекст: `<` → `&lt;`, `&` → `&amp;`
  - JavaScript-контекст: hex-форма `\xHH`
  - URL-параметры: percent-encoding `%HH`
- **Использовать безопасные DOM-методы**: `.textContent`, `.setAttribute()` вместо `innerHTML`
- **HTML-санитизация** при пользовательском вводе HTML: библиотека DOMPurify (frontend) или OWASP
  Java HTML Sanitizer (backend)
- **Content-Security-Policy** (CSP) заголовок как дополнительный эшелон защиты; не заменяет
  output encoding, но существенно снижает ущерб от XSS
- Не использовать «escape hatches» фреймворков: `dangerouslySetInnerHTML` (React),
  `bypassSecurityTrustAs*` (Angular)

---

### CSRF (Cross-Site Request Forgery)

CSRF вынуждает браузер аутентифицированного пользователя отправить запрос на чужой сайт.
Защищаться следует несколькими способами (OWASP рекомендует комбинировать):

| Метод | Описание |
|-------|----------|
| Synchronizer Token Pattern | Уникальный токен в форме/заголовке; валидируется на сервере |
| SameSite Cookie (`Strict`/`Lax`) | Браузер не отправляет куки в cross-site запросах |
| Double Submit Cookie (HMAC) | Токен и в куке, и в теле; naive-вариант устарел, нужен HMAC |
| Custom Request Header | Заголовки вроде `X-Requested-With` не отправляются cross-origin |

**SameSite=Strict** даёт максимальную защиту, но ломает переходы по внешним ссылкам.
**SameSite=Lax** — компромисс по умолчанию в современных браузерах.

---

### Хэширование паролей

Хранить пароли в открытом виде или в MD5/SHA-1 недопустимо. Используются адаптивные
функции хэширования с солью (соль генерируется автоматически и хранится вместе с хэшем):

| Алгоритм | Рекомендация ([OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)) |
|----------|------------|
| **Argon2id** | Предпочтительный вариант. Минимум: 19 MiB памяти, 2 итерации, параллелизм 1 |
| **scrypt** | Альтернатива при отсутствии Argon2id. CPU/memory cost >= 2^17 |
| **bcrypt** | Для legacy-систем. Work factor >= 10; ограничение 72 байта на пароль |
| **PBKDF2** | При требовании FIPS-140. Work factor >= 600 000, HMAC-SHA-256 |

**Pepper** — дополнительный секрет, хранящийся отдельно от БД (например, в переменных окружения).
Даже при утечке дампа БД атакующий не сможет восстановить пароли без pepper.

Spring Security предоставляет готовые реализации через интерфейс `PasswordEncoder`:

```java
// Рекомендуемый вариант — BCryptPasswordEncoder
PasswordEncoder encoder = new BCryptPasswordEncoder(12); // work factor 12
String hash = encoder.encode(rawPassword);
boolean matches = encoder.matches(rawPassword, hash);

// DelegatingPasswordEncoder — поддерживает несколько алгоритмов одновременно
PasswordEncoder delegating = PasswordEncoderFactories.createDelegatingPasswordEncoder();
// Хранит {bcrypt}$2a$10$... или {argon2}... и выбирает нужный декодер автоматически
```

---

### Сессии vs токены. JWT

**Session-based (stateful):** сервер хранит состояние сессии (в памяти или в Redis), браузер
получает `session_id` в куке. Проще отзывать, но не масштабируется без общего хранилища.

**Token-based (stateless, JWT):** вся информация закодирована в токене. Сервер не хранит состояние,
горизонтально масштабируется без проблем. Отзыв токена требует доп. механизма (blacklist или короткое TTL).

**Структура JWT** ([jwt.io/introduction](https://jwt.io/introduction)):

```
<Header_base64url>.<Payload_base64url>.<Signature_base64url>

Пример:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   <- Header: {"alg":"HS256","typ":"JWT"}
.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Registered claims (стандартные поля payload):**

| Claim | Значение |
|-------|----------|
| `iss` | Издатель токена (Issuer) |
| `sub` | Субъект (обычно userId) |
| `aud` | Аудитория (Resource Server) |
| `exp` | Время истечения (Unix timestamp) |
| `nbf` | Не ранее (Not Before) |
| `iat` | Время выдачи (Issued At) |
| `jti` | Уникальный идентификатор токена |

**Алгоритмы подписи:**
- **HMAC (HS256/HS384/HS512)** — симметричный, один секрет у всех участников
- **RSA (RS256/RS384/RS512)** — асимметричный, public key для проверки, private key для подписи
- **ECDSA (ES256/ES384/ES512)** — асимметричный, более компактная подпись по сравнению с RSA

**Критические уязвимости JWT** (согласно
[OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)):

- **"none" algorithm attack** — некоторые библиотеки принимали `alg: none`, позволяя подделать
  токен без подписи. Всегда явно указывайте ожидаемый алгоритм.
- **Algorithm confusion (RS256 → HS256)** — если сервер принимает оба алгоритма, атакующий может
  взять RSA public key (публичный) и использовать его как HMAC-секрет.
- **Слабый секрет** — при HMAC ключ должен быть >= 64 символов криптографически случайных данных.

```java
// Явное указание алгоритма при верификации (библиотека auth0/java-jwt)
JWTVerifier verifier = JWT.require(Algorithm.HMAC256(secret)).build();
DecodedJWT decoded = verifier.verify(token);
```

**Хранение JWT на клиенте:**
- `sessionStorage` — токен живёт только в рамках вкладки; не переживает перезапуск браузера
- `localStorage` — уязвимо к XSS; если используется, обязательно короткое TTL (15–30 мин) + rotation
- `HttpOnly cookie` — не доступна из JS, защищена от XSS; но требует CSRF-защиты

---

### OAuth 2.0 и OpenID Connect

**OAuth 2.0** — протокол делегированной авторизации (RFC 6749). Клиент получает
ограниченный доступ к ресурсам пользователя без получения его пароля.

Ключевые роли:
- **Resource Owner** — пользователь
- **Client** — приложение, запрашивающее доступ
- **Authorization Server** — выдаёт токены (Keycloak, Okta, Auth0)
- **Resource Server** — хранит защищённые ресурсы, принимает access token

Основные flows:
- **Authorization Code + PKCE** — для публичных клиентов (SPA, мобильные приложения)
- **Client Credentials** — machine-to-machine без участия пользователя
- **Authorization Code** (confidential client) — серверные приложения с client_secret

**OpenID Connect (OIDC)** — надстройка над OAuth 2.0 для аутентификации. Добавляет **ID Token**
(JWT с информацией о пользователе: sub, email, name) и endpoint `/userinfo`.

---

### Spring Security: архитектура фильтров

Источник: [Spring Security — Servlet Architecture](https://docs.spring.io/spring-security/reference/servlet/architecture.html)

Spring Security интегрируется в цепочку Servlet-фильтров через два ключевых компонента:

**DelegatingFilterProxy** — мост между Servlet-контейнером и Spring ApplicationContext.
Позволяет использовать Spring-бины в качестве фильтров, инициализируя их лениво.

**FilterChainProxy** — центральная точка входа Spring Security. Применяет `HttpFirewall`,
очищает `SecurityContext` после запроса, выбирает нужную `SecurityFilterChain` по `RequestMatcher`.

**SecurityFilterChain** — конфигурируемый набор фильтров для заданного паттерна URL.
Только первая совпавшая цепочка выполняется.

Порядок ключевых фильтров в цепочке:

| Фильтр | Назначение |
|--------|-----------|
| `SecurityContextHolderFilter` | Загружает/сохраняет SecurityContext |
| `CsrfFilter` | Проверяет CSRF-токен |
| `LogoutFilter` | Обрабатывает logout |
| `UsernamePasswordAuthenticationFilter` | Form-login |
| `BasicAuthenticationFilter` | HTTP Basic Auth |
| `BearerTokenAuthenticationFilter` | OAuth2 Bearer / JWT |
| `AnonymousAuthenticationFilter` | Выставляет анонимный контекст |
| `AuthorizationFilter` | Проверяет права доступа |

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/public/**").permitAll()
            .anyRequest().authenticated()
        )
        .formLogin(Customizer.withDefaults())
        .csrf(Customizer.withDefaults());
    return http.build();
}
```

---

### Spring Security: аутентификационная архитектура

Источник: [Spring Security — Authentication Architecture](https://docs.spring.io/spring-security/reference/servlet/authentication/architecture.html)

```
SecurityContextHolder
  └── SecurityContext
        └── Authentication
              ├── principal  (UserDetails или JWT claims)
              ├── credentials (пароль; очищается после аутентификации)
              └── authorities (роли/полномочия)
```

**Поток аутентификации (form-login):**

1. Пользователь отправляет логин/пароль
2. `UsernamePasswordAuthenticationFilter` создаёт `UsernamePasswordAuthenticationToken`
3. `ProviderManager` перебирает список `AuthenticationProvider`
4. `DaoAuthenticationProvider` вызывает `UserDetailsService.loadUserByUsername()`
5. Сравнивает пароль через `PasswordEncoder`
6. При успехе — кладёт аутентификацию в `SecurityContextHolder`

```java
// Пример UserDetailsService
@Service
public class CustomUserDetailsService implements UserDetailsService {
    @Autowired
    private UserRepository repo;

    @Override
    public UserDetails loadUserByUsername(String username)
            throws UsernameNotFoundException {
        return repo.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));
    }
}
```

`SecurityContextHolder` по умолчанию использует `ThreadLocal` — контекст изолирован в рамках
одного потока. Для реактивных приложений (WebFlux) используется `ReactiveSecurityContextHolder`
на основе Reactor Context.

---

### Spring Security: авторизация на уровне методов

Источник: [Spring Security — Method Security](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

Включение:

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig { }
```

Основные аннотации:

| Аннотация | Когда срабатывает | Пример |
|-----------|------------------|--------|
| `@PreAuthorize` | До вызова метода | `@PreAuthorize("hasRole('ADMIN')")` |
| `@PostAuthorize` | После вызова, проверяет `returnObject` | `@PostAuthorize("returnObject.owner == authentication.name")` |
| `@PreFilter` | Фильтрует входные коллекции | `@PreFilter("filterObject.owner == authentication.name")` |
| `@PostFilter` | Фильтрует возвращаемую коллекцию | `@PostFilter("filterObject.active == true")` |
| `@Secured` | До вызова (legacy) | `@Secured("ROLE_ADMIN")` |
| `@RolesAllowed` | До вызова (JSR-250) | `@RolesAllowed("ADMIN")` |

`@PostAuthorize` особенно полезен для защиты от IDOR (Insecure Direct Object Reference): метод
выполняется, но результат возвращается только если принадлежит текущему пользователю.

---

### Spring Security: JWT Resource Server

Источник: [Spring Security — JWT Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

Минимальная конфигурация через `application.yml`:

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://idp.example.com/issuer
```

Spring Security автоматически:
1. Запрашивает JWKS-endpoint Authorization Server
2. Валидирует подпись JWT по полученным публичным ключам
3. Проверяет claims `iss`, `exp`, `nbf`

Настройка маппинга authorities:

```java
@Bean
public JwtAuthenticationConverter jwtAuthenticationConverter() {
    JwtGrantedAuthoritiesConverter converter = new JwtGrantedAuthoritiesConverter();
    converter.setAuthoritiesClaimName("roles");   // имя claim в токене
    converter.setAuthorityPrefix("ROLE_");         // префикс для hasRole()
    JwtAuthenticationConverter jwtConverter = new JwtAuthenticationConverter();
    jwtConverter.setJwtGrantedAuthoritiesConverter(converter);
    return jwtConverter;
}
```

Поток обработки запроса с Bearer-токеном:

```
Authorization: Bearer <jwt>
        |
BearerTokenAuthenticationFilter
        |
JwtAuthenticationProvider
        |
JwtDecoder (проверка подписи + claims)
        |
JwtAuthenticationConverter (извлечение authorities)
        |
SecurityContextHolder <- JwtAuthenticationToken
```

---

### HTTPS / TLS

Источник: [OWASP Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)

- **TLS 1.3** — предпочтительная версия. TLS 1.2 допустим для совместимости.
  TLS 1.0 и 1.1 официально устарели (RFC 8996) и должны быть отключены.
- **Cipher suites**: для TLS 1.3 используются AEAD (AES-GCM, ChaCha20-Poly1305).
  Отключить null/anonymous/export-шифры.
- **Сертификаты**: SHA-256, ключи >= 2048 бит (RSA) или >= 256 бит (ECDSA).
- **HSTS** (`Strict-Transport-Security`): заставляет браузер всегда использовать HTTPS,
  включая поддомены. Рекомендуемое значение: `max-age=63072000; includeSubDomains; preload`.
- **Флаг `Secure` на куках**: предотвращает передачу куки по HTTP.

В Spring Boot включение HTTPS:

```yaml
server:
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: ${SSL_KEYSTORE_PASSWORD}
    key-store-type: PKCS12
    protocol: TLS
    enabled-protocols: TLSv1.3,TLSv1.2
```

Перенаправление HTTP → HTTPS:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .requiresChannel(channel -> channel
            .anyRequest().requiresSecure()
        )
        .headers(headers -> headers
            .httpStrictTransportSecurity(hsts -> hsts
                .includeSubDomains(true)
                .maxAgeInSeconds(63072000)
            )
        );
    return http.build();
}
```

---

### CORS (Cross-Origin Resource Sharing)

CORS — механизм браузера, управляющий тем, каким origin разрешено делать запросы к API.
Настройка в Spring Security:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()));
    return http.build();
}

@Bean
CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://app.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

Нельзя совместить `allowCredentials(true)` с `allowedOrigins("*")` — это вызовет исключение
при старте. Используйте конкретные origins.

---

## Достоверные источники

1. **[OWASP Top 10:2021](https://owasp.org/Top10/)** — канонический стандарт классификации
   угроз веб-приложений, поддерживаемый сообществом OWASP. Обновляется раз в несколько лет
   на основе реальных данных о взломах.

2. **[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)** — практические
   руководства по конкретным угрозам и защитам: SQL Injection Prevention, XSS Prevention,
   CSRF Prevention, Password Storage, TLS, JWT и десятки других. Официальный проект OWASP.

3. **[Spring Security Reference (v7)](https://docs.spring.io/spring-security/reference/index.html)** —
   официальная документация Spring Security. Исчерпывающее описание архитектуры, аутентификации,
   авторизации, OAuth2, CSRF, CORS. Актуальна для Spring Boot 3.x.

4. **[jwt.io/introduction](https://jwt.io/introduction)** — официальный обзор JWT от Auth0
   (сопровождают спецификацию). Содержит описание структуры, алгоритмов и рекомендаций по
   безопасному использованию.

5. **[OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)** —
   специализированное руководство по безопасности JWT для Java-разработчиков: атаки на алгоритм,
   хранение токенов, fingerprinting, revocation. Часть официального Cheat Sheet Series.

6. **[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)** —
   текущие рекомендации по алгоритмам хэширования паролей (Argon2id, scrypt, bcrypt, PBKDF2)
   с конкретными параметрами work factor. Единственный официальный источник OWASP по этой теме.
