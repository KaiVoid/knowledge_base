# Контейнеры и DevOps (Docker, Kubernetes, CI/CD)

> **Уровень:** Middle / Senior
> **Связанные вопросы:** [Вопросы по контейнерам и DevOps →](../../../interview-questions/containers-devops-01.md)
> **Связанные области:** [[20-microservices]], [[14-spring-boot]]

## Что это и зачем

Современные Java-приложения упаковываются в контейнеры и разворачиваются в оркестраторах.
Docker позволяет упаковать приложение со всеми зависимостями, Kubernetes — управлять контейнерами в
масштабе. CI/CD автоматизирует сборку, тестирование и доставку. Эти навыки ожидаются от backend-разработчика
в большинстве современных команд.

Контейнеризация решает проблему «работает у меня, не работает в проде»: образ содержит всё необходимое —
JRE, библиотеки, конфиги запуска — и одинаково исполняется в любой среде. Kubernetes берёт на себя
планирование, перезапуск, масштабирование и обновление без простоя. Методология Twelve-Factor App
формализует принципы проектирования cloud-native приложений, которые хорошо живут в контейнерах.

---

## Ключевые подтемы

### Docker: образы, контейнеры и слои

Образ Docker — это неизменяемый стек слоёв, каждый из которых хранит набор изменений файловой системы
(добавление, удаление, модификация файлов). Слои накапливаются поверх друг друга; контейнер добавляет
поверх них тонкий записываемый слой. Такая архитектура, основанная на **Union Filesystem**, позволяет
множеству контейнеров разделять один и тот же базовый образ без дублирования данных на диске.

Ключевые понятия:
- **Image** — шаблон, собранный из инструкций `Dockerfile`.
- **Container** — запущенный экземпляр образа с собственным записываемым слоем.
- **Registry** — хранилище образов (Docker Hub, GHCR, собственный registry).
- **Tag** — метка версии образа (`myapp:1.2.3`, `myapp:latest`).

Официальная документация: [Understanding image layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/)

---

### Dockerfile: инструкции и кеширование

Каждая инструкция в `Dockerfile` создаёт новый слой. Docker использует кеш: если инструкция и её
контекст не изменились, слой берётся из кеша. Изменение любого слоя инвалидирует кеш всех
последующих слоёв — поэтому порядок инструкций критически важен.

**Основные инструкции:**

| Инструкция | Назначение |
|---|---|
| `FROM <image>` | Базовый образ, с которого начинается сборка |
| `WORKDIR <path>` | Рабочая директория внутри образа |
| `COPY <src> <dst>` | Копирование файлов с хоста в образ |
| `RUN <cmd>` | Выполнение команды при сборке (создаёт слой) |
| `ENV <name> <value>` | Переменная окружения (доступна при сборке и запуске) |
| `EXPOSE <port>` | Документирует порт, который слушает контейнер |
| `USER <user>` | Пользователь, от имени которого запускается приложение |
| `CMD ["cmd", "arg"]` | Команда по умолчанию при запуске контейнера |
| `ENTRYPOINT ["cmd"]` | Точка входа; `CMD` передаётся как аргументы |

**Правило оптимизации кеша:** размещайте редко меняющиеся инструкции ближе к началу файла,
а часто меняющиеся (копирование исходников) — ближе к концу. Это позволяет пересобирать
только изменившиеся слои, а не весь образ.

```dockerfile
# Хорошо: зависимости копируются и загружаются до исходников
FROM eclipse-temurin:21-jre-alpine AS runtime
WORKDIR /app
# Сначала только pom.xml — слой с зависимостями будет закеширован
COPY pom.xml .
RUN mvn dependency:go-offline -B
# Теперь исходники — этот слой меняется чаще
COPY src ./src
RUN mvn package -DskipTests
CMD ["java", "-jar", "target/app.jar"]
```

Официальная документация: [Optimizing builds with cache](https://docs.docker.com/build/cache/)

---

### Многоэтапная сборка (multi-stage build)

Многоэтапная сборка ([Multi-stage builds](https://docs.docker.com/build/building/multi-stage/))
позволяет использовать несколько инструкций `FROM` в одном `Dockerfile`. Каждый этап (`AS <name>`)
изолирован: артефакты компилятора, исходники и временные файлы остаются в первом этапе и
**не попадают** в финальный образ. Это радикально уменьшает размер образа.

```dockerfile
# Этап сборки: полный JDK + Maven
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /workspace
COPY pom.xml .
COPY src ./src
RUN mvn package -DskipTests

# Финальный образ: только JRE + собранный JAR
FROM eclipse-temurin:21-jre-alpine AS runtime
WORKDIR /app
# Копируем только результат сборки из предыдущего этапа
COPY --from=build /workspace/target/app.jar app.jar
EXPOSE 8080
USER 1001
CMD ["java", "-jar", "app.jar"]
```

При использовании BuildKit (`DOCKER_BUILDKIT=1`) обрабатываются только этапы, от которых зависит
целевой — неиспользуемые этапы пропускаются. Можно собрать конкретный этап:
`docker build --target build .`

---

### Kubernetes: Pod

**Pod** — наименьшая развёртываемая единица Kubernetes. Pod объединяет один или несколько контейнеров,
которые разделяют:
- общий сетевой namespace (один IP-адрес, контейнеры общаются через `localhost`);
- общие тома (`volumes`).

Поды недолговечны: при перезапуске создаётся новый Pod, IP меняется. Поэтому Pod не создаётся
вручную — он управляется контроллерами.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: myapp
    image: myapp:1.0.0
    ports:
    - containerPort: 8080
```

**Контроллеры для Pod:**

| Контроллер | Назначение |
|---|---|
| `Deployment` | Stateless-приложения, rolling update, rollback |
| `StatefulSet` | Приложения с состоянием (БД), стабильные имена и тома |
| `DaemonSet` | Один Pod на каждый узел (агенты мониторинга, логи) |
| `Job` / `CronJob` | Одноразовые или периодические задачи |

Официальная документация: [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)

---

### Kubernetes: Deployment

`Deployment` — декларативный способ управления Pod-репликами и обновлениями stateless-приложений.
Контроллер Deployment непрерывно сверяет желаемое состояние с текущим и устраняет расхождения.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:1.2.0
        ports:
        - containerPort: 8080
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # сколько Pod сверх replicas можно создать
      maxUnavailable: 0  # сколько Pod может быть недоступно
```

**Стратегии обновления:**
- `RollingUpdate` (по умолчанию) — постепенная замена Pod; приложение остаётся доступным.
- `Recreate` — все старые Pod удаляются, потом создаются новые; образует простой.

**Откат:**
```bash
kubectl rollout undo deployment/myapp              # откат на предыдущую ревизию
kubectl rollout undo deployment/myapp --to-revision=2  # откат на конкретную ревизию
kubectl rollout history deployment/myapp           # история ревизий
```

Официальная документация: [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

### Kubernetes: Service

Service — абстракция над набором Pod-ов. Предоставляет стабильный DNS-адрес и балансировку нагрузки,
независимо от того, сколько Pod-ов запущено и какие у них IP.

**Типы Service:**

| Тип | Доступность | Назначение |
|---|---|---|
| `ClusterIP` (умолч.) | Только внутри кластера | Межсервисное взаимодействие |
| `NodePort` | Внешний: `<NodeIP>:<NodePort>` | Базовый внешний доступ |
| `LoadBalancer` | Внешний: облачный балансировщик | Продакшн-доступ |
| `ExternalName` | CNAME на внешний DNS | Обёртка над внешним сервисом |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  type: ClusterIP
  selector:
    app: myapp          # выбирает Pod по меткам
  ports:
  - protocol: TCP
    port: 80            # порт Service
    targetPort: 8080    # порт контейнера
```

Официальная документация: [Service](https://kubernetes.io/docs/concepts/services-networking/service/)

---

### ConfigMap и Secret

**ConfigMap** хранит неконфиденциальные конфигурационные данные в виде пар ключ-значение.
Ограничение: максимальный размер 1 MiB.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  APP_ENV: production
  LOG_LEVEL: INFO
  application.properties: |
    server.port=8080
    spring.datasource.url=jdbc:postgresql://db:5432/mydb
```

**Два способа подключить ConfigMap к Pod:**

1. Переменные окружения — статические, не обновляются при изменении ConfigMap:
```yaml
env:
- name: LOG_LEVEL
  valueFrom:
    configMapKeyRef:
      name: myapp-config
      key: LOG_LEVEL
```

2. Volume (файл) — обновляются автоматически при изменении ConfigMap:
```yaml
volumeMounts:
- name: config-vol
  mountPath: /etc/config
volumes:
- name: config-vol
  configMap:
    name: myapp-config
```

**Secret** аналогичен ConfigMap, но предназначен для конфиденциальных данных (пароли, токены).
Данные хранятся в base64-encoded виде; в продакшн-кластерах рекомендуется включать шифрование
Secrets at rest и интегрировать внешние хранилища (Vault).

Официальная документация: [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)

---

### Health-пробы: liveness, readiness, startup

Kubernetes использует три типа проб для мониторинга здоровья контейнеров
([Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)):

| Проба | Что делает при ошибке | Когда использовать |
|---|---|---|
| `livenessProbe` | Перезапускает контейнер | Приложение завесло, нужен рестарт |
| `readinessProbe` | Исключает Pod из балансировки | Приложение не готово принимать трафик |
| `startupProbe` | Блокирует liveness/readiness до старта | Медленно стартующее приложение |

**Типы проб:**
- `httpGet` — HTTP GET-запрос; успех при кодах 200–399.
- `tcpSocket` — попытка открыть TCP-соединение.
- `exec` — выполнение команды; успех при коде выхода 0.

```yaml
containers:
- name: myapp
  image: myapp:1.0.0
  startupProbe:
    httpGet:
      path: /actuator/health
      port: 8080
    failureThreshold: 30   # до 300 с на инициализацию
    periodSeconds: 10
  livenessProbe:
    httpGet:
      path: /actuator/health/liveness
      port: 8080
    initialDelaySeconds: 0
    periodSeconds: 10
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /actuator/health/readiness
      port: 8080
    periodSeconds: 5
    failureThreshold: 3
```

Spring Boot Actuator предоставляет эндпоинты `/actuator/health/liveness` и
`/actuator/health/readiness` «из коробки» при добавлении зависимости `spring-boot-starter-actuator`.

---

### Управление ресурсами: requests и limits

Каждый контейнер может и должен объявлять потребности в ресурсах
([Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)):

- `requests` — минимум, который планировщик (`kube-scheduler`) резервирует на узле.
- `limits` — максимум потребления; превышение по CPU даёт троттлинг, по памяти — OOM-kill.

Единицы: CPU в миллиядрах (`500m` = 0.5 ядра), память в байтах (`256Mi`, `1Gi`).

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

**QoS-классы Pod** (назначаются автоматически):

| Класс | Условие | Приоритет выселения |
|---|---|---|
| `Guaranteed` | requests == limits для всех контейнеров | Последний (самый защищённый) |
| `Burstable` | requests < limits | Средний |
| `BestEffort` | requests и limits не заданы | Первый |

---

### HorizontalPodAutoscaler (HPA)

HPA автоматически изменяет число реплик Deployment или StatefulSet на основе метрик.
Работает как control loop с периодом по умолчанию 15 секунд.

Алгоритм:
```
desiredReplicas = ceil(currentReplicas * currentMetricValue / desiredMetricValue)
```

Если отношение отклоняется от 1.0 менее чем на 10% (допуск по умолчанию) — масштабирование
не происходит, чтобы избежать осцилляций. Период стабилизации при масштабировании вниз — 300 с.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

Требует установленного [Metrics Server](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/#metrics-server).

Официальная документация: [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

---

### Twelve-Factor App

Методология [The Twelve-Factor App](https://12factor.net/) определяет 12 принципов построения
cloud-native приложений. Ключевые факторы с точки зрения Java-разработчика:

| # | Фактор | Суть |
|---|---|---|
| I | Codebase | Один репозиторий — много окружений |
| II | Dependencies | Явное объявление зависимостей (Maven/Gradle) |
| III | Config | Конфигурация через переменные окружения, не в коде |
| IV | Backing services | БД, очереди — подключаемые ресурсы, не различаются «локальные» и «внешние» |
| V | Build, Release, Run | Строгое разделение: сборка → релиз → запуск |
| VI | Processes | Stateless-процессы; состояние только во внешних сервисах |
| VII | Port binding | Приложение само экспортирует HTTP-порт |
| VIII | Concurrency | Масштабирование через добавление процессов/контейнеров |
| IX | Disposability | Быстрый старт, graceful shutdown (корректная обработка SIGTERM) |
| X | Dev/Prod parity | Одинаковые инструменты и окружения на всех этапах |
| XI | Logs | Логи как потоки событий в stdout; агрегация — внешняя |
| XII | Admin processes | Задачи администрирования (миграции БД) как одноразовые процессы |

В Kubernetes фактор IX реализуется через `preStop`-хук и `terminationGracePeriodSeconds`,
фактор III — через ConfigMap/Secret, а фактор XI — через стандартные средства сбора логов
(Fluentd, Loki и др.).

---

## Достоверные источники

1. **[Docker Documentation](https://docs.docker.com/)** — официальная документация Docker Inc.
   Охватывает Dockerfile, сборку образов, multi-stage builds, BuildKit, кеширование слоёв.
   Первичный авторитетный источник по всем вопросам Docker.

2. **[Kubernetes Documentation](https://kubernetes.io/docs/home/)** — официальная документация
   CNCF/Kubernetes. Описывает Pod, Deployment, Service, ConfigMap, пробы, HPA, управление
   ресурсами. Единственный авторитетный источник по Kubernetes API и концепциям.

3. **[The Twelve-Factor App](https://12factor.net/)** — методология Адама Уиггинса (Heroku).
   Стандарт де-факто при проектировании cloud-native приложений; напрямую применима
   к Java-сервисам, работающим в Kubernetes.

4. **[Kubernetes: Managing Resources for Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)** —
   официальная страница по requests/limits/QoS. Точные определения и правила расчёта.

5. **[Kubernetes: Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)** —
   официальное руководство по пробам. Все типы, параметры, примеры YAML.

6. **[Baeldung — Dockerizing a Java Application](https://www.baeldung.com/dockerizing-spring-boot-application)** —
   практические примеры контейнеризации Spring Boot. Авторитетный ресурс по Java; статьи
   проходят технический ревью. Дополняет официальную документацию практическими деталями.
