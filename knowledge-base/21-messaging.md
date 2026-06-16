# Брокеры сообщений (Kafka, RabbitMQ)

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по брокерам сообщений →](../interview-questions/messaging-01.md)
> **Связанные области:** [[20-microservices]], [[04-concurrency]]

## Что это и зачем

Брокеры сообщений обеспечивают асинхронное взаимодействие между сервисами, развязывая их во времени
и повышая устойчивость системы. Apache Kafka (распределённый лог событий) и RabbitMQ (классический
брокер сообщений) — самые востребованные технологии. Нужно понимать модели доставки, гарантии и
интеграцию со Spring.

Выбор между Kafka и RabbitMQ определяется требованиями: Kafka подходит для высокотребовательных
потоков событий с возможностью повторной обработки (event sourcing, CDC, аналитика); RabbitMQ — для
гибкой маршрутизации задач, RPC-паттернов и сценариев с разнородными потребителями.

---

## Ключевые подтемы

### Модели обмена: point-to-point и pub/sub

**Point-to-point (очередь):** одно сообщение доставляется ровно одному потребителю. Используется
для распределения задач (work queue). В RabbitMQ реализуется через direct exchange + очередь.

**Publish/Subscribe:** одно сообщение получают все подписчики. В RabbitMQ — fanout exchange;
в Kafka — каждая consumer group получает собственную копию всех сообщений из топика.

---

### Apache Kafka: архитектура и ключевые понятия

Документация: [kafka.apache.org/documentation](https://kafka.apache.org/documentation/)

#### Топик, партиция, смещение (offset)

Данные в Kafka организованы в **топики** (topics), которые разбиты на **партиции** (partitions).
Каждая партиция представляет собой упорядоченный, неизменяемый лог записей. Каждой записи присваивается
монотонно возрастающий числовой идентификатор — **offset**. Offset неизменен и является постоянным
идентификатором позиции в логе (источник: [Kafka Design 4.1](https://kafka.apache.org/41/design/design/)).

Партиция — единица параллелизма: одна партиция в один момент обрабатывается ровно одним потребителем
внутри consumer group. Количество партиций задаётся при создании топика:

```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic my-topic \
  --partitions 12 --replication-factor 3
```

Порядок сообщений гарантируется только **внутри одной партиции**. Для глобального порядка нужна
одна партиция, что убивает параллелизм.

#### Брокеры, репликация и ISR

Kafka-кластер состоит из **брокеров** (brokers). Каждая партиция реплицируется на несколько брокеров
(replication factor). Один брокер является **лидером** (leader) для партиции и обрабатывает все
операции чтения и записи; остальные — **фолловеры** (followers), пассивно реплицирующие данные.

**ISR (In-Sync Replicas)** — динамически поддерживаемый список реплик, которые синхронизированы
с лидером. Запись считается подтверждённой только после получения её всеми ISR-репликами.
Реплика исключается из ISR, если отстаёт дольше порогового значения `replica.lag.time.max.ms`.

При отказе всех ISR-реплик настройка `unclean.leader.election.enable` определяет поведение:
- `false` (умолчание): ждать восстановления ISR (приоритет согласованности);
- `true`: выбрать не-ISR реплику (приоритет доступности, возможна потеря данных).

#### Consumer Group и балансировка

Потребители объединяются в **consumer groups** по общему `group.id`. Kafka распределяет партиции
между участниками группы — каждая партиция назначается ровно одному потребителю. Это даёт
горизонтальное масштабирование: добавление потребителей перераспределяет нагрузку.

При изменении состава группы происходит **rebalance** — перераспределение партиций.
Стратегии назначения (`partition.assignment.strategy`):
- `RangeAssignor` — диапазонный, по умолчанию в старых версиях;
- `RoundRobinAssignor` — циклический;
- `StickyAssignor` — сохраняет предыдущие назначения, меньше перемещений;
- `CooperativeStickyAssignor` — инкрементальный rebalance без полной остановки потребления
  (рекомендован, избегает stop-the-world).

Потребители сами хранят свои смещения и коммитят их в специальный внутренний топик `__consumer_offsets`.
Это позволяет «перемотать» потребление (replay) на любое историческое смещение.

#### Гарантии доставки и acks producer'а

Настройка `acks` у producer'а управляет гарантиями:

| `acks` | Поведение | Гарантия |
|--------|-----------|----------|
| `0` | Не ждёт подтверждения | At-most-once (возможна потеря) |
| `1` | Ждёт подтверждения только от лидера | At-least-once при отказе до репликации — потеря |
| `-1` / `all` | Ждёт подтверждения от всех ISR | Наивысшая надёжность |

Начиная с Kafka 3.0 значения по умолчанию: `acks=all`, `enable.idempotence=true`.

#### Идемпотентный producer и exactly-once

**Идемпотентность** (с версии 0.11): producer получает уникальный `producer ID` (PID) и нумерует
сообщения порядковыми номерами. Брокер отклоняет дубликаты — повторная отправка при сбое не создаёт
дублей. Включается параметром `enable.idempotence=true`.

**Транзакции (KIP-98):** позволяют атомарно записать данные в несколько партиций или топиков.
Для использования задаётся уникальный `transactional.id` (на каждый экземпляр приложения).
Consumer-side при `isolation.level=read_committed` видит только закоммиченные транзакции.

```java
producer.initTransactions();
try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("output-topic", key, value));
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}
```

**Exactly-once** на уровне Kafka Streams включается настройкой `processing.guarantee=exactly_once_v2`
(рекомендован с Kafka 2.5+).

#### Хранение данных: retention и log compaction

**Retention** — политика удаления старых записей:
- По времени: `log.retention.hours` (умолчание 168 ч / 7 дней);
- По размеру: `log.retention.bytes` (умолчание -1, неограниченно).

**Log Compaction** — альтернативная политика: для каждого ключа хранится только последнее
значение, старые версии удаляются. Подходит для хранения актуального состояния (changelog).
Запись с `null`-payload — **tombstone**: маркер удаления ключа.

Настраивается на уровне топика: `cleanup.policy=compact` (или `delete,compact`).

#### Производительность: batching, сжатие, zero-copy

- **Batching:** producer накапливает сообщения (`batch.size`, `linger.ms`) перед отправкой;
- **Сжатие:** `compression.type` = `gzip`, `snappy`, `lz4`, `zstd` — сжатие батчей целиком;
- **Zero-copy:** Kafka использует системный вызов `sendfile`, данные копируются в page cache
  один раз и переиспользуются при каждом consume без лишних копирований в userspace.

---

### RabbitMQ: архитектура и ключевые понятия

Документация: [rabbitmq.com/docs](https://www.rabbitmq.com/docs)

#### Exchange, Queue, Binding, Routing Key

Сообщение публикуется в **exchange**, который по правилам **binding** направляет его в одну или
несколько **queue**. Потребители подключаются к очередям, а не к exchange напрямую.

**Типы exchange** (источник: [rabbitmq.com/docs/exchanges](https://www.rabbitmq.com/docs/exchanges)):

| Тип | Маршрутизация | Когда использовать |
|-----|---------------|-------------------|
| `direct` | Точное совпадение routing key с binding key | Распределение задач по типу |
| `fanout` | Игнорирует routing key, рассылает всем | Широковещательные события |
| `topic` | Паттерн с `*` (одно слово) и `#` (ноль и более слов) | Гибкая подписка по категориям |
| `headers` | По заголовкам сообщения, игнорирует routing key | Сложная фильтрация |

Примеры паттернов для topic exchange:
- `regions.na.cities.*` совпадает с `regions.na.cities.toronto`, но не с `regions.na.cities`;
- `audit.events.#` совпадает с `audit.events` и `audit.events.users.signup`;
- `#` превращает topic exchange в fanout.

#### Типы очередей

**Classic Queues** — традиционный тип. Mirroring (классическое зеркалирование) удалено в RabbitMQ 4.0.

**Quorum Queues** — реплицируемые очереди на основе алгоритма **Raft**, рекомендованы для
критичных данных (источник: [rabbitmq.com/docs/quorum-queues](https://www.rabbitmq.com/docs/quorum-queues)):
- Всегда durable (не могут быть transient);
- Не поддерживают exclusive queues и глобальный QoS prefetch;
- Нельзя давать server-generated имена;
- Подтверждение publisher confirm приходит только после репликации на кворум узлов;
- Рекомендованы для долгоживущих очередей с требованием высокой доступности.

**Streams** — отдельная структура данных (похожа на Kafka): хранит историю, позволяет многократное
чтение с произвольного offset. Подходит для fan-out с большим числом потребителей и replay.

Сравнение по применимости:

| Критерий | Classic Queue | Quorum Queue |
|----------|---------------|--------------|
| Репликация | Нет (mirroring удалён) | Raft-based |
| Durability | Опциональная | Всегда durable |
| Минимальная задержка | Лучше | Хуже (цена за надёжность) |
| Большие бэклоги (5M+) | Приемлемо | Не рекомендуется |
| Критичные данные | Нет | Да |

#### Durability и персистентность

- **Durable queue:** метаданные хранятся на диске и переживают перезапуск ноды;
- **Transient queue:** хранится в памяти, удаляется при перезапуске;
- **Persistent message:** тело сообщения записывается на диск (delivery-mode=2);
- RabbitMQ 4.3.0 по умолчанию deprecated transient non-exclusive classic queues.

Для гарантии сохранности нужна комбинация: durable queue + persistent message + publisher confirms.

#### Consumer Acknowledgements и Publisher Confirms

(источник: [rabbitmq.com/docs/confirms](https://www.rabbitmq.com/docs/confirms))

**Consumer acknowledgements:**
- `basic.ack` — положительное подтверждение обработки;
- `basic.nack` — расширение RabbitMQ, отрицательное подтверждение с опцией requeue;
- `basic.reject` — стандартный AMQP отказ (только одно сообщение);
- **Automatic mode:** сообщение считается доставленным сразу после отправки в сокет.
  Официальная документация характеризует этот режим как «небезопасный» (`unsafe`).

Параметр `multiple=true` в ack/nack подтверждает все сообщения с delivery tag меньше или равным
указанному — снижает количество сетевых round-trip.

**Publisher confirms:** publisher включает режим через `confirm.select`; брокер отвечает `basic.ack`
(успех) или `basic.nack` (ошибка). Для persistent сообщений confirm отправляется только после
записи на диск.

#### Prefetch (QoS)

Настройка `basic.qos` ограничивает количество неподтверждённых сообщений на канале. Официальная
документация рекомендует значения **100–300** для оптимального баланса throughput/latency.
Prefetch=1 существенно снижает throughput, особенно при высоких задержках сети.

#### Dead Letter Exchange (DLX)

(источник: [rabbitmq.com/docs/dlx](https://www.rabbitmq.com/docs/dlx))

Сообщение попадает в DLX при:
1. **Rejection:** `basic.reject` или `basic.nack` с `requeue=false`;
2. **Expiry:** истёк TTL сообщения (`x-message-ttl`);
3. **Queue overflow:** превышен лимит длины очереди (`x-max-length`);
4. **Delivery limit:** (только quorum queues) превышено `x-delivery-limit`.

Настройка через **policy** (рекомендуется, без перезапуска приложений):
```bash
rabbitmqctl set_policy DLX ".*" \
  '{"dead-letter-exchange":"my-dlx"}' --apply-to queues
```

Или через аргументы при объявлении очереди: `x-dead-letter-exchange`, `x-dead-letter-routing-key`.

RabbitMQ отслеживает цепочку смертей в заголовке `x-death` (AMQP 0-9-1) и предотвращает
бесконечные циклы: если цикл не содержит rejection, сообщение дропается.

**At-least-once dead lettering** доступно в Quorum Queues: при включённой опции
`x-dead-letter-strategy=at-least-once` брокер использует внутренние publisher confirms при
перемещении в DLX, исключая потерю сообщений.

#### TTL

- `x-message-ttl` на очереди — TTL для всех сообщений в очереди;
- `expiration` в свойствах сообщения — TTL конкретного сообщения;
- `x-expires` на очереди — TTL самой очереди (автоудаление при неиспользовании).

---

### Гарантии доставки: сравнение Kafka и RabbitMQ

| Гарантия | Kafka (producer) | RabbitMQ |
|----------|------------------|----------|
| At-most-once | `acks=0` | Automatic consumer ack |
| At-least-once | `acks=1` или `acks=all` + retry | Manual ack + publisher confirms |
| Exactly-once | Idempotent producer + транзакции + `read_committed` | Quorum queue + at-least-once DLX (только для DLX) |

Для idempotent потребителей необходимо хранить обработанные идентификаторы (БД, Redis) и
проверять их перед обработкой — независимо от брокера.

---

### Порядок сообщений

**Kafka:** порядок гарантирован внутри партиции. Для строгого глобального порядка — одна партиция
(но тогда параллелизм = 1). Для порядка в рамках сущности используют partitioning key (хэш ключа
определяет партицию).

**RabbitMQ:** очередь FIFO в пределах одного потребителя. Requeue при nack может нарушить порядок.
Quorum queues: порядок строго FIFO, если сообщения не переупорядочиваются requeue.

---

### Интеграция со Spring

#### Spring for Apache Kafka

Зависимость (Spring Boot):
```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

**Отправка сообщений — KafkaTemplate:**
```java
@Component
public class KafkaSender {
    private final KafkaTemplate<String, String> kafkaTemplate;

    public KafkaSender(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void send(String topic, String message) {
        kafkaTemplate.send(topic, message);
    }
}
```

**Получение сообщений — @KafkaListener:**
```java
@KafkaListener(topics = "my-topic", groupId = "my-group", concurrency = "3")
public void listen(
        @Payload String data,
        @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
        @Header(KafkaHeaders.OFFSET) long offset) {
    // обработка
}
```

Настройка в `application.yml`:
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: my-group
      auto-offset-reset: earliest
    producer:
      transaction-id-prefix: tx-  # включает KafkaTransactionManager
```

Транзакционная отправка (при наличии `transaction-id-prefix`): Spring автоматически конфигурирует
`KafkaTransactionManager`. Batch listener включается через `factory.setBatchListener(true)`.

Ручное подтверждение offset (`AckMode.MANUAL`):
```java
@KafkaListener(topics = "my-topic",
    containerFactory = "manualAckFactory")
public void listen(String data, Acknowledgment ack) {
    process(data);
    ack.acknowledge();
}
```

Документация: [docs.spring.io/spring-kafka](https://docs.spring.io/spring-kafka/reference/)

#### Spring AMQP (RabbitMQ)

Зависимость:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

**Отправка — RabbitTemplate:**
```java
rabbitTemplate.convertAndSend("my-exchange", "routing.key", payload);
```

**Получение — @RabbitListener:**
```java
@RabbitListener(queues = "my-queue")
public void handle(MyMessage message) {
    // обработка
}
```

**Декларирование топологии через бины:**
```java
@Bean
public Queue myQueue() {
    return QueueBuilder.durable("my-queue")
        .deadLetterExchange("dlx")
        .ttl(60_000)
        .build();
}

@Bean
public TopicExchange myExchange() {
    return new TopicExchange("my-exchange");
}

@Bean
public Binding binding(Queue myQueue, TopicExchange myExchange) {
    return BindingBuilder.bind(myQueue).to(myExchange).with("order.#");
}
```

Документация: [docs.spring.io/spring-amqp](https://docs.spring.io/spring-amqp/reference/)

---

## Достоверные источники

1. **[Apache Kafka — Documentation (kafka.apache.org)](https://kafka.apache.org/documentation/)** —
   официальная документация проекта Apache Kafka; раздел Design подробно описывает архитектуру,
   репликацию, EOS и производительность. Актуальна для версии 4.x.

2. **[Apache Kafka — Design 4.1 (kafka.apache.org/41/design/design/)](https://kafka.apache.org/41/design/design/)** —
   детальный раздел об архитектурных решениях: ISR, consumer groups, offset management,
   idempotent producer, exactly-once semantics.

3. **[RabbitMQ — Documentation (rabbitmq.com/docs)](https://www.rabbitmq.com/docs)** —
   официальная документация RabbitMQ; включает разделы по exchanges, queues, confirms, DLX,
   quorum queues, streams.

4. **[RabbitMQ — Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms)** —
   официальная страница RabbitMQ, детально объясняющая механизм подтверждений, prefetch,
   режимы ack и рекомендации по надёжности.

5. **[RabbitMQ — Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues)** —
   официальная документация по quorum queues: Raft-репликация, сравнение с classic queues,
   ограничения и рекомендации по применению.

6. **[Spring for Apache Kafka — Reference (docs.spring.io)](https://docs.spring.io/spring-kafka/reference/)** и
   **[Spring Boot Kafka Support](https://docs.spring.io/spring-boot/reference/messaging/kafka.html)** —
   официальная документация Spring; авторитетный источник по @KafkaListener, KafkaTemplate,
   транзакциям и авто-конфигурации Boot.
