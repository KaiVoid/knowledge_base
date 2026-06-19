# Микросервисная архитектура

> **Уровень:** Senior
> **Связанные вопросы:** [Вопросы по микросервисам →](../../../interview-questions/microservices-01.md)
> **Связанные области:** [[14-spring-boot]], [[21-messaging]], [[22-containers-devops]]

## Что это и зачем

Микросервисная архитектура разбивает приложение на набор небольших независимо развёртываемых сервисов.
Это доминирующий подход в крупных backend-системах. Разработчик уровня Senior должен понимать
принципы декомпозиции, паттерны взаимодействия, обеспечение отказоустойчивости и согласованности
данных в распределённой системе.

По определению Martin Fowler (martinfowler.com), микросервисный стиль — это подход к разработке
единого приложения как набора небольших сервисов, каждый из которых работает в своём процессе
и взаимодействует через легковесные механизмы (HTTP API, очереди сообщений). Сервисы строятся
вокруг бизнес-возможностей, развёртываются независимо и могут использовать разные технологии
и хранилища данных.

Ключевая идея — децентрализация: каждая команда владеет своим сервисом от разработки до
production («build it, run it»). Это снижает координационные издержки, но требует развитой
инфраструктуры и операционной зрелости.

## Ключевые подтемы

### Монолит vs микросервисы

| Критерий | Монолит | Микросервисы |
|---|---|---|
| Развёртывание | Целиком, все компоненты | Независимо, по сервисам |
| Масштабирование | Горизонтальное всего приложения | Точечное — только нагруженных сервисов |
| Изменение схемы БД | Локально, внутри одной БД | Требует версионирования API |
| Технологический стек | Единый | Polyglot (разные языки, БД) |
| Сложность разработки | Низкая при старте | Выше с первого дня |
| Сложность эксплуатации | Ниже | Требует развитого DevOps/observability |
| Отказоустойчивость | Весь монолит падает вместе | Сбой изолирован в сервисе (при правильном CB) |

Fowler выделяет девять характеристик микросервисной архитектуры: компонентизация через сервисы,
организация по бизнес-возможностям, продуктовое мышление («продукты, а не проекты»), умные концы
и простые каналы, децентрализованное управление и данными, автоматизация инфраструктуры,
проектирование на отказ, эволюционный дизайн.

### Декомпозиция: DDD и Bounded Context

Существуют два основных паттерна декомпозиции ([microservices.io — Decompose by business capability](https://microservices.io/patterns/decomposition/decompose-by-business-capability.html),
[Decompose by subdomain](https://microservices.io/patterns/decomposition/decompose-by-subdomain.html)):

**Decompose by Business Capability** — каждый сервис соответствует тому, «что бизнес делает для
создания ценности». Бизнес-возможности стабильны во времени, что даёт устойчивую архитектуру.
Пример для интернет-магазина: Product Catalog Service, Inventory Service, Order Service,
Delivery Service.

**Decompose by Subdomain (DDD)** — декомпозиция по поддоменам предметной области:

- **Core subdomain** — ключевой дифференциатор бизнеса, самая ценная часть, разрабатывается внутри.
- **Supporting subdomain** — вспомогательная область, связанная с бизнесом, но не уникальная;
  может отдаваться на аутсорс.
- **Generic subdomain** — универсальные функции, закрываемые готовыми решениями (аутентификация,
  email-рассылки).

**Bounded Context** — явные границы, внутри которых единственно справедливы конкретные доменные
модели и термины (убиквитарный язык). Граница Bounded Context — это граница микросервиса.
Один микросервис = один Bounded Context.

### Database per Service

[Паттерн Database per Service](https://microservices.io/patterns/data/database-per-service.html)
требует, чтобы персистентные данные каждого сервиса были приватны и доступны только через API
этого сервиса. Это обеспечивает слабую связанность при изменении схемы.

Варианты изоляции данных (от меньшей к большей):

1. **Private tables per service** — отдельные таблицы в общей БД.
2. **Schema per service** — отдельная схема в одном сервере.
3. **Database server per service** — полностью изолированный экземпляр СУБД.

Разные сервисы могут использовать разные типы хранилищ (Polyglot Persistence):
реляционные БД, документные (MongoDB), поисковые (Elasticsearch), графовые (Neo4j).

**Следствия:** распределённые транзакции становятся нетривиальными (CAP-теорема),
JOIN-запросы между сервисами невозможны напрямую — решается через API Composition или CQRS.

### Синхронное взаимодействие: REST и gRPC

**REST over HTTP** — де-факто стандарт для публичных API и межсервисного взаимодействия.
Прост в отладке, широко поддерживается. Минусы: текстовый формат (JSON), нет строгой схемы
по умолчанию, нет нативного стриминга.

**gRPC** — бинарный протокол поверх HTTP/2 от Google. Использует Protocol Buffers для
схемы и сериализации. Даёт сильную типизацию, bi-directional streaming, меньшую задержку
и меньший размер пакетов. Оптимален для внутреннего взаимодействия высоконагруженных сервисов.

```protobuf
// Пример gRPC-контракта
syntax = "proto3";
service OrderService {
  rpc CreateOrder (CreateOrderRequest) returns (OrderResponse);
  rpc GetOrder    (GetOrderRequest)    returns (OrderResponse);
}
message CreateOrderRequest {
  string customer_id = 1;
  repeated OrderItem items = 2;
}
```

### Асинхронное взаимодействие и Event-Driven Architecture

Асинхронная связь через брокеры сообщений (Kafka, RabbitMQ) даёт:
- временну́ю развязку (sender не ждёт ответа),
- буферизацию нагрузки,
- возможность fan-out (одно событие — много потребителей).

**Domain Event** — паттерн публикации событий об изменениях бизнес-сущностей.
Сервис публикует `OrderPlaced`, `PaymentProcessed` и т.д.; другие сервисы подписываются
и реагируют независимо.

**Transactional Outbox** ([microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)) — решение проблемы dual write.
Нельзя атомарно обновить БД и отправить сообщение в брокер. Решение:
сохранять сообщение в таблицу `outbox` в той же транзакции, что и бизнес-данные; отдельный
процесс (Message Relay) читает outbox и публикует в брокер. Гарантия: сообщение отправится
тогда и только тогда, когда транзакция зафиксирована.

```sql
-- Таблица outbox
CREATE TABLE outbox_events (
    id          UUID PRIMARY KEY,
    aggregate_type VARCHAR(255),
    aggregate_id   VARCHAR(255),
    event_type     VARCHAR(255),
    payload        JSONB,
    created_at     TIMESTAMP DEFAULT NOW(),
    published      BOOLEAN DEFAULT FALSE
);
```

Message Relay реализуется через:
- **Polling publisher** — периодический SELECT по `published = false`.
- **Transaction Log Tailing (CDC)** — Debezium читает WAL PostgreSQL / binlog MySQL.

### API Gateway и BFF

[API Gateway](https://microservices.io/patterns/apigateway.html) — единая точка входа для всех
клиентов. Выполняет: маршрутизацию, агрегацию ответов нескольких сервисов, аутентификацию/авторизацию,
rate limiting, преобразование протоколов, SSL termination.

**Backends for Frontends (BFF)** — вариация, при которой для каждого типа клиента (веб, мобильный,
партнёрский API) создаётся отдельный gateway с оптимизацией под его нужды.

**Spring Cloud Gateway** ([docs.spring.io](https://docs.spring.io/spring-cloud-gateway/docs/current/reference/html/))
— реактивный gateway на WebFlux/Netty (Spring Boot 3+). Три ключевых понятия:
- **Route** — правило: ID + URI назначения + predicates + filters.
- **Predicate** — условие совпадения (Path, Method, Header, Host, Query, Weight и др.).
- **Filter** — модификация запроса/ответа (AddRequestHeader, RewritePath, CircuitBreaker,
  RequestRateLimiter, TokenRelay и др.).

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: orders-route
          uri: lb://order-service        # lb:// — балансировка через Spring Cloud LoadBalancer
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1
            - name: CircuitBreaker
              args:
                name: ordersCircuitBreaker
                fallbackUri: forward:/fallback/orders
```

### Service Discovery

В динамической среде (Kubernetes, облако) IP-адреса экземпляров меняются. [Service Registry](https://microservices.io/patterns/service-registry.html) — БД живых экземпляров сервисов.

**Client-side discovery** — клиент сам запрашивает реестр и выбирает экземпляр.
Пример: Eureka + Spring Cloud LoadBalancer (`@LoadBalanced RestTemplate` или `WebClient`).

**Server-side discovery** — клиент обращается к маршрутизатору (load balancer), тот
сам консультируется с реестром. Пример: AWS ALB, Kubernetes Service + kube-proxy.

В Kubernetes роль реестра берёт на себя etcd через kube-dns/CoreDNS; Netflix Eureka и Consul
используются при деплое вне Kubernetes.

### Отказоустойчивость: Circuit Breaker, Retry, Bulkhead, Timeout

[Circuit Breaker](https://microservices.io/patterns/reliability/circuit-breaker.html) — прокси, предотвращающий каскадные сбои. Три состояния:

| Состояние | Поведение |
|---|---|
| **Closed** | Запросы проходят; счётчик ошибок накапливается |
| **Open** | Запросы немедленно отклоняются (fast-fail); запущен таймаут |
| **Half-Open** | Небольшое число пробных запросов; успех → Closed, провал → Open |

Переходы: Closed → Open (порог ошибок превышен); Open → Half-Open (таймаут истёк);
Half-Open → Closed (пробные запросы успешны); Half-Open → Open (повторный сбой).

**Resilience4j** — современная замена Hystrix в экосистеме Spring:

```java
@Service
public class OrderClient {

    private final CircuitBreaker circuitBreaker;
    private final RestClient restClient;

    public OrderClient(CircuitBreakerRegistry registry, RestClient restClient) {
        this.circuitBreaker = registry.circuitBreaker("orderService");
        this.restClient = restClient;
    }

    public Order getOrder(String id) {
        return circuitBreaker.executeSupplier(() ->
            restClient.get()
                      .uri("/orders/{id}", id)
                      .retrieve()
                      .body(Order.class)
        );
    }
}
```

```yaml
resilience4j:
  circuitbreaker:
    instances:
      orderService:
        slidingWindowSize: 10
        failureRateThreshold: 50          # % ошибок для открытия
        waitDurationInOpenState: 10s
        permittedNumberOfCallsInHalfOpenState: 3
```

**Retry** — повторный вызов при временных сбоях (network glitch). Важно: с экспоненциальной
задержкой и jitter, иначе все инстансы одновременно перегрузят упавший сервис.

**Timeout** — жёсткое ограничение времени ожидания. Без timeout система может накапливать
зависшие потоки до исчерпания ресурсов.

**Bulkhead** — ограничение числа одновременных вызовов к одной зависимости, чтобы сбой
одной зависимости не «съел» все потоки.

### Распределённые транзакции: паттерн Saga

[Saga](https://microservices.io/patterns/data/saga.html) — последовательность локальных транзакций.
Каждый шаг обновляет БД своего сервиса и публикует событие (или команду) для следующего.
При бизнес-ошибке выполняются **компенсирующие транзакции** для отмены уже выполненных шагов.

Два подхода координации:

**Хореография (Choreography)** — участники общаются через события без центрального координатора.

```
OrderService  →  [OrderCreated event]  →  PaymentService
PaymentService →  [PaymentReserved event]  →  InventoryService
InventoryService → [StockReserved event] → OrderService (approve)
```

Плюсы: простота, нет единой точки отказа. Минусы: сложно отследить весь процесс,
неявные зависимости между сервисами.

**Оркестрация (Orchestration)** — центральный оркестратор (Saga Orchestrator) явно отправляет
команды каждому участнику и ждёт ответа.

```
OrderSaga (orchestrator)
  → команда "ReserveCredit"  → CustomerService
  ← событие "CreditReserved"
  → команда "ApproveOrder"   → OrderService
```

Плюсы: логика саги в одном месте, легко тестировать. Минусы: оркестратор становится
точкой концентрации логики, риск god-object.

**Ограничения Saga:**
- Нет изоляции (аномалии при параллельных сагах — dirty reads, lost updates).
- Нет автоматического отката — нужно явно проектировать компенсирующие операции.
- Атомарность обновления БД + публикация события решается через Transactional Outbox.

### CQRS и Event Sourcing

**CQRS (Command Query Responsibility Segregation)** — разделение модели записи (Command) и
чтения (Query). Позволяет строить денормализованные read-модели, оптимизированные под конкретные
запросы (например, материализованные представления для аналитики).

**Event Sourcing** — хранение агрегатов не как текущего состояния, а как последовательности
событий. Текущее состояние восстанавливается replay событий. Даёт полный аудит-лог и
упрощает реализацию CQRS + Saga, но усложняет схему (версионирование событий).

### Наблюдаемость: трассировка, метрики, логи

Три столпа observability:

**1. Distributed Tracing** ([паттерн](https://microservices.io/patterns/observability/distributed-tracing.html))
— каждому входящему запросу присваивается уникальный `traceId`, который передаётся во все
дочерние вызовы. Каждый вызов фиксируется как `span` с временными метками. Это позволяет
восстановить полный путь запроса и найти узкие места.

Инструменты: **Micrometer Tracing** (Spring Boot 3+) + **Zipkin** или **Jaeger**.
В Spring Boot 3 Sleuth заменён на Micrometer Tracing.

```yaml
management:
  tracing:
    sampling:
      probability: 1.0    # 100% для dev; в prod ~0.1
```

**2. Метрики** — Micrometer отправляет метрики (счётчики, гистограммы, gauges) в Prometheus,
Atlas и другие системы. Spring Boot Actuator предоставляет стандартные метрики JVM, HTTP,
DataSource из коробки.

**3. Агрегация логов** — структурированные JSON-логи централизуются через ELK (Elasticsearch +
Logstash + Kibana) или Loki + Grafana. Каждый лог должен содержать `traceId` и `spanId`
для корреляции с трассировкой.

**Health Check API** ([паттерн](https://microservices.io/patterns/observability/health-check-api.html))
— эндпоинт `/actuator/health` сообщает liveness/readiness. В Kubernetes используется как
liveness probe и readiness probe.

### Spring Cloud как набор инструментов

[Spring Cloud](https://docs.spring.io/spring-cloud/docs/current/reference/html/) — коллекция
проектов поверх Spring Boot, реализующих облачные паттерны:

| Компонент | Назначение | Статус |
|---|---|---|
| Spring Cloud Gateway | API Gateway, реактивный | Актуален (4.x) |
| Spring Cloud Config | Централизованная конфигурация | Актуален |
| Spring Cloud LoadBalancer | Client-side балансировка | Актуален (заменил Ribbon) |
| Resilience4j | Circuit Breaker, Retry, Bulkhead | Актуален (заменил Hystrix) |
| Spring Cloud Eureka | Service Registry | Актуален (но в K8s не нужен) |
| Spring Cloud OpenFeign | Декларативный HTTP-клиент | Актуален |
| Spring Cloud Stream | Event-driven messaging (Kafka/RabbitMQ) | Актуален |
| Micrometer Tracing | Distributed Tracing (заменил Sleuth) | Актуален в Boot 3+ |

**Spring Cloud Config** хранит конфигурацию в Git-репозитории и отдаёт сервисам через HTTP.
Поддерживает шифрование секретов и динамическое обновление через `@RefreshScope`.

**OpenFeign** позволяет описать HTTP-клиент интерфейсом:

```java
@FeignClient(name = "inventory-service")
public interface InventoryClient {
    @GetMapping("/inventory/{productId}")
    InventoryResponse checkInventory(@PathVariable String productId);
}
```

## Достоверные источники

1. **[microservices.io — Pattern Index (Chris Richardson)](https://microservices.io/patterns/index.html)** —
   авторитетный каталог паттернов микросервисной архитектуры от автора книги «Microservices Patterns».
   Каждый паттерн описан по схеме: проблема, контекст, решение, последствия, примеры.

2. **[Martin Fowler — Microservices (martinfowler.com)](https://martinfowler.com/articles/microservices.html)** —
   основополагающая статья 2014 года, определившая терминологию. Fowler — один из авторов «Refactoring»
   и крупнейший инфлюенсер в Enterprise Architecture.

3. **[Spring Cloud Reference Documentation](https://docs.spring.io/spring-cloud/docs/current/reference/html/)** —
   официальная документация всей экосистемы Spring Cloud. Первичный источник для всего, связанного
   с реализацией паттернов на Java/Spring.

4. **[Spring Cloud Gateway Reference](https://docs.spring.io/spring-cloud-gateway/docs/current/reference/html/)** —
   официальная документация реактивного API Gateway. Описывает predicates, filters, конфигурацию,
   интеграцию с Resilience4j и Rate Limiter.

5. **[Resilience4j User Guide](https://resilience4j.readme.io/docs/getting-started)** —
   официальная документация библиотеки Circuit Breaker, Retry, Bulkhead, TimeLimiter.
   Рекомендована командой Spring как замена Hystrix.

6. **Книга «Microservices Patterns» (Chris Richardson, Manning, 2018)** — признанный
   учебник с детальным разбором паттернов Saga, CQRS, Event Sourcing, Transactional Outbox.
   Автор — создатель microservices.io.
