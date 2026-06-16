# Контейнеры и DevOps — часть 3 из 3

> Вопросы 41–60 (в части: 20). Всего в разделе: 60.
> Область знаний: [../knowledge-base/22-containers-devops.md](../knowledge-base/22-containers-devops.md)
> Правила: [RULES.md](RULES.md)
> Части: [ч.1](containers-devops-01.md) · [ч.2](containers-devops-02.md) · **ч.3**

---
### Вопрос 41. Что такое PodDisruptionBudget (PDB) в Kubernetes? Чем он отличается от maxUnavailable в Deployment, на какие виды disruptions он влияет и как его правильно настроить для Java-сервиса с 3 репликами, чтобы при обслуживании узла всегда была доступна хотя бы одна реплика?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Specifying a Disruption Budget for your Application | Kubernetes](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)

PodDisruptionBudget ограничивает количество подов реплицированного приложения, которые могут быть одновременно недоступны из-за добровольных (voluntary) нарушений. Например, если сервис требует наличия не менее 80% реплик, вы можете создать PDB, запрещающий одновременную остановку более 20% подов.

PDB не может предотвратить недобровольные (involuntary) нарушения, однако они также учитываются в бюджете.

**Поля PDB:**

- `minAvailable` — минимальное число подов, которые должны оставаться доступными во время нарушения. Может быть задано числом или процентом (например, `"50%"`).
- `maxUnavailable` — максимальное число подов, которые могут быть недоступны. Взаимоисключает с `minAvailable`.

**Пример для приложения с 3 репликами, требующего минимум 2 доступных:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: java-service-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: java-service
```

**Проверка:**

```bash
kubectl get poddisruptionbudgets
NAME               MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
java-service-pdb   2               N/A               1                     7s
```

Поле `ALLOWED DISRUPTIONS` показывает, сколько подов можно прервать прямо сейчас без нарушения бюджета. При 3 доступных и `minAvailable: 2` — допускается 1 одновременное нарушение.

#### Ответ от Claude

**Что такое PodDisruptionBudget**

PodDisruptionBudget (PDB) — объект политики Kubernetes (`policy/v1`), который защищает реплицированные приложения от одновременного выведения из строя нескольких подов во время плановых операций обслуживания кластера. PDB не устраняет недоступность — он регулирует, сколько подов может быть прервано одновременно.

**Виды disruptions (нарушений)**

Kubernetes разделяет нарушения на два типа:

| Тип | Примеры | PDB защищает? |
|-----|---------|---------------|
| Voluntary (добровольные) | `kubectl drain`, обновление узла, масштабирование кластера вниз, прямое удаление пода администратором | Да |
| Involuntary (недобровольные) | Аппаратный сбой, kernel panic, OOM-kill, исчезновение узла из-за сетевого раздела | Нет |

PDB влияет **только на добровольные нарушения**, которые проходят через Eviction API. Eviction API проверяет PDB перед вытеснением пода; если вытеснение нарушило бы бюджет — запрос отклоняется с кодом `429 Too Many Requests`, и операция (например, `kubectl drain`) блокируется до восстановления нужного числа доступных подов.

**Отличие PDB от maxUnavailable в Deployment**

| Параметр | Где задаётся | Что контролирует |
|----------|-------------|-----------------|
| `spec.strategy.rollingUpdate.maxUnavailable` | Deployment | Только процесс rolling update самого Deployment. Не влияет на внешние операции (drain, eviction). |
| PDB `maxUnavailable` / `minAvailable` | Отдельный объект PodDisruptionBudget | Все добровольные вытеснения подов через Eviction API: drain, cluster autoscaler, инструменты управления узлами. |

Таким образом, Deployment `maxUnavailable` и PDB — дополняющие, а не взаимозаменяющие механизмы. Типичная ошибка: настроить `maxUnavailable: 0` в Deployment и думать, что это защитит поды от drain — это не так.

**Настройка PDB для Java-сервиса с 3 репликами**

Задача: при обслуживании узла всегда доступна хотя бы одна реплика.

Вариант 1 — через `minAvailable` (абсолютное число):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: java-service-pdb
  namespace: production
spec:
  minAvailable: 1      # Минимум 1 под должен быть доступен
  selector:
    matchLabels:
      app: java-service
```

При 3 репликах `ALLOWED DISRUPTIONS = 3 - 1 = 2`, то есть можно одновременно вытеснить 2 пода.

Вариант 2 — через `maxUnavailable` (максимально недоступных):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: java-service-pdb
  namespace: production
spec:
  maxUnavailable: 2    # Допускается недоступность максимум 2 подов из 3
  selector:
    matchLabels:
      app: java-service
```

Оба варианта эквивалентны при фиксированном числе реплик = 3. Однако `maxUnavailable` предпочтительнее, если число реплик меняется (например, при горизонтальном масштабировании HPA) — он автоматически пересчитывается.

Если задача строже — «всегда доступны минимум 2 из 3» (рекомендуется для production):

```yaml
spec:
  minAvailable: 2
```

**Как работает взаимодействие с drain:**

1. Администратор выполняет `kubectl drain node-1`.
2. Kubernetes вызывает Eviction API для каждого пода на узле.
3. Eviction API проверяет PDB: если вытеснение снизит `ALLOWED DISRUPTIONS` ниже нуля — возвращает `429`, drain ждёт.
4. Как только Deployment создаёт замещающий под на другом узле и он становится `Ready` — `ALLOWED DISRUPTIONS` восстанавливается, drain продолжается.

**Важные нюансы:**

- `minAvailable: 100%` (или равное числу реплик) делает поды **невытесняемыми** — drain будет заблокирован навсегда. Применять с осторожностью.
- PDB не помогает, если контроллер (Deployment) удалён — у оставшихся подов нет «хозяина», восстанавливающего реплики.
- Поле `unhealthyPodEvictionPolicy: AlwaysAllow` (Kubernetes 1.26+) позволяет вытеснять уже нездоровые поды, не считая их в бюджете, — полезно при зависших приложениях.
- PDB не создаётся автоматически — его необходимо явно объявить для каждого критичного приложения.

---

### Вопрос 42. Что такое NetworkPolicy в Kubernetes? Как она работает «по умолчанию», почему простого создания NetworkPolicy недостаточно без поддерживающего CNI-плагина (Calico, Cilium), и как написать политику, запрещающую все входящие соединения к поду, кроме трафика из конкретного namespace?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Network Policies | Kubernetes](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

NetworkPolicy — объект Kubernetes уровня API-сервера, позволяющий управлять трафиком на уровне IP/порта (OSI L3-L4) между подами и внешними сетями.

**Поведение по умолчанию:**

По умолчанию поды не изолированы ни по ingress, ни по egress — все входящие и исходящие соединения разрешены. Как только какая-либо NetworkPolicy выбирает под в конкретном направлении, этот под становится изолированным: разрешён только трафик, явно описанный в политиках.

**Почему нужен CNI-плагин:**

> "Network policies are implemented by the network plugin. To use network policies, you must be using a networking solution which supports NetworkPolicy. Creating a NetworkPolicy resource without a controller that implements it will have no effect."

То есть сам API-сервер только хранит объекты NetworkPolicy, но не применяет их. Применение — задача CNI-плагина (Calico, Cilium, Weave Net и др.).

**Политика: запретить весь ingress, кроме трафика из конкретного namespace:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-myproject
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          project: myproject
```

- `podSelector: {}` — применяется ко всем подам в namespace `default`.
- `policyTypes: [Ingress]` — изолирует поды по входящему трафику.
- Единственное разрешённое входящее соединение — из namespace с меткой `project: myproject`.
- Весь остальной ingress-трафик блокируется.

#### Ответ от Claude

**Что такое NetworkPolicy**

NetworkPolicy — ресурс Kubernetes (`networking.k8s.io/v1`), описывающий правила сетевого взаимодействия между подами и внешними сетями на уровнях L3-L4 (IP-адреса, порты, протоколы TCP/UDP/SCTP). Концептуально — это межсетевой экран на уровне пода.

**Поведение по умолчанию**

Без каких-либо NetworkPolicy в кластере:

- Поды **не изолированы** — любой под может соединяться с любым другим подом в любом namespace и с внешними адресами.
- Как только в namespace появляется хотя бы одна NetworkPolicy, выбирающая под по `podSelector`, этот под становится **изолированным** в указанном направлении (`Ingress` / `Egress`).
- Изолированный под принимает только трафик, явно разрешённый в правилах `ingress` / `egress` соответствующих политик.
- Несколько политик, выбирающих один и тот же под, **суммируются** (union) — если хоть одна политика разрешает трафик, он проходит.

**Почему NetworkPolicy без CNI-плагина не работает**

Kubernetes API-сервер принимает и хранит объекты NetworkPolicy как обычные Kubernetes-ресурсы, но сам **никакой сетевой фильтрации не реализует**. Применение правил — ответственность CNI (Container Network Interface) плагина, работающего на каждом узле.

Стандартный CNI (например, `kubenet`, используемый в некоторых дистрибутивах по умолчанию) NetworkPolicy **не поддерживает**. В такой конфигурации:

1. Объект NetworkPolicy создаётся без ошибок (`kubectl apply` проходит успешно).
2. Никакой фильтрации не происходит — трафик идёт без ограничений.
3. Нет никакого предупреждения или события, сигнализирующего о неработающих политиках.

Это классическая ловушка: разработчик думает, что настроил изоляцию, но фактически сеть открыта.

**CNI-плагины с поддержкой NetworkPolicy:**

| Плагин | Механизм применения | Дополнительные возможности |
|--------|--------------------|-----------------------------|
| Calico | iptables / eBPF | CalicoNetworkPolicy (L7, FQDN-based) |
| Cilium | eBPF | CiliumNetworkPolicy (L7 HTTP, gRPC), прозрачное шифрование |
| Weave Net | iptables | Стандартный NetworkPolicy |
| Antrea | OVS / eBPF | AntreaNetworkPolicy |

Перед применением политик необходимо убедиться, что используемый CNI поддерживает NetworkPolicy (`kubectl get nodes -o wide` → проверить установленный плагин).

**Политика: запретить весь ingress, кроме трафика из конкретного namespace**

Шаг 1: Убедиться, что целевой namespace имеет нужную метку.

```bash
kubectl label namespace trusted-ns project=myproject
```

Шаг 2: Создать NetworkPolicy.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress-except-trusted-ns
  namespace: production          # Namespace, где живут защищаемые поды
spec:
  podSelector:
    matchLabels:
      app: java-service          # Применяется только к подам с этой меткой
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          project: myproject     # Разрешить входящий трафик только из этого namespace
```

**Разбор политики:**

- `podSelector: matchLabels: app: java-service` — политика применяется только к подам с меткой `app=java-service` в namespace `production`. Если нужно защитить все поды в namespace — использовать `podSelector: {}`.
- `policyTypes: [Ingress]` — изолировать под по входящему трафику. Egress при этом остаётся неограниченным (если нет отдельной egress-политики).
- `ingress.from.namespaceSelector` — разрешить входящие соединения от любого пода из namespace с меткой `project: myproject`.

**Важный нюанс: AND vs OR в `from`**

```yaml
# ЭТО — AND: под должен быть И в нужном namespace И иметь нужную метку
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        project: myproject
    podSelector:
      matchLabels:
        role: frontend

# ЭТО — OR: под в нужном namespace ИЛИ под с нужной меткой (в любом namespace)
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        project: myproject
  - podSelector:
      matchLabels:
        role: frontend
```

Разница — в том, являются ли `namespaceSelector` и `podSelector` элементами **одного объекта** в списке `from` (AND) или **отдельными объектами** (OR).

**Полный пример: deny-all + разрешение из конкретного namespace**

```yaml
# Политика 1: запретить весь ingress (default deny)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
# Политика 2: разрешить ingress только из namespace trusted-ns
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-trusted-ns
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: java-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          project: myproject
```

Такой подход с явным `default-deny` более безопасен: он гарантирует, что любой новый под в namespace `production` по умолчанию изолирован, а трафик разрешается только явными политиками.

**Проверка:**

```bash
# Убедиться, что политика создана
kubectl get networkpolicies -n production

# Проверить метки namespace
kubectl get namespace trusted-ns --show-labels

# Тест с временным подом (curl из разрешённого namespace должен пройти)
kubectl run test-pod --image=curlimages/curl -n trusted-ns --rm -it -- \
  curl http://java-service.production.svc.cluster.local:8080/health
```

**Расхождения между источниками:** Официальная документация Kubernetes (`kubernetes.io`) и документация Cilium единогласны в том, что без поддерживающего CNI-плагина NetworkPolicy не имеет эффекта. Документация Calico добавляет собственный CRD `GlobalNetworkPolicy` с расширенными возможностями (L7, FQDN), которые выходят за пределы стандартного Kubernetes NetworkPolicy API.

---
### Вопрос 43. Как устроены Init-контейнеры в Kubernetes? Чем они отличаются от обычных (app) контейнеров и sidecar-контейнеров? Приведите конкретный сценарий применения Init-контейнера для Java-приложения (например, ожидание готовности БД или выполнение Flyway-миграций).

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Init Containers — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

Init-контейнеры — специализированные контейнеры, которые выполняются до запуска основных (app) контейнеров пода и обязательно завершаются до их старта. Каждый init-контейнер должен успешно завершить работу, прежде чем запустится следующий. Они выполняются последовательно; пока все init-контейнеры не завершатся, основные контейнеры не стартуют.

**Чем отличаются от обычных контейнеров:**

- Init-контейнеры выполняются до завершения (run to completion), а не работают непрерывно.
- Они не поддерживают `lifecycle`-хуки, `livenessProbe`, `readinessProbe` и `startupProbe`.
- При сбое init-контейнера kubelet перезапускает его до успешного завершения (кроме случая `restartPolicy: Never`).

**Типичные задачи:**
- Ожидание готовности сервисов (DNS-lookup в цикле).
- Клонирование Git-репозитория в том.
- Выполнение миграций базы данных.
- Генерация конфигурационных файлов перед запуском приложения.

**Пример из документации:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  initContainers:
  - name: init-myservice
    image: busybox:1.28
    command: ['sh', '-c', "until nslookup myservice.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for myservice; sleep 2; done"]
  - name: init-mydb
    image: busybox:1.28
    command: ['sh', '-c', "until nslookup mydb.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for mydb; sleep 2; done"]
  containers:
  - name: myapp-container
    image: busybox:1.28
    command: ['sh', '-c', 'echo The app is running! && sleep 3600']
```

Оба init-контейнера ждут DNS-записей нужных сервисов, и только после их успешного завершения стартует `myapp-container`.

#### Ответ от Claude

**Что такое Init-контейнеры**

Init-контейнер — это контейнер, который запускается в поде до основных (app) контейнеров, выполняет свою задачу и завершается. Kubelet запускает init-контейнеры строго последовательно: следующий стартует только после успешного завершения предыдущего (exit code 0). Пока хотя бы один init-контейнер не завершился успешно, основные контейнеры не получат управление.

**Отличия от обычных (app) контейнеров**

| Характеристика | Init-контейнер | App-контейнер |
|---|---|---|
| Жизненный цикл | Завершается после выполнения задачи | Работает непрерывно на протяжении всего времени жизни пода |
| Пробы | Не поддерживает `livenessProbe`, `readinessProbe`, `startupProbe`, `lifecycle`-хуки | Поддерживает все пробы и хуки |
| Порядок запуска | Строго последовательный | Запускаются параллельно после завершения всех init-контейнеров |
| Сбой | Kubelet перезапускает до успеха | Поведение зависит от `restartPolicy` |

**Отличия от Sidecar-контейнеров**

Начиная с Kubernetes v1.29 (GA в v1.33) появился нативный тип sidecar-контейнера — это init-контейнер с `restartPolicy: Always`. Sidecar работает параллельно с основными контейнерами на протяжении всей жизни пода, поддерживает пробы (`readinessProbe`, `livenessProbe`) и участвует в определении ready-статуса пода. При завершении основных контейнеров kubelet останавливает sidecar-ы в обратном порядке.

| Характеристика | Init-контейнер | Sidecar-контейнер |
|---|---|---|
| Работает во время жизни пода | Нет, завершается до старта app | Да, работает всё время |
| Пробы | Не поддерживает | Поддерживает |
| Взаимодействие с app-контейнером | Только через том (emptyDir) — однонаправленно | Прямое, через общую сеть и тома |
| Реализация | `initContainers` | `initContainers` + `restartPolicy: Always` |

**Конкретный сценарий для Java-приложения: ожидание готовности БД + Flyway-миграции**

Рекомендуемый подход — два последовательных init-контейнера:

1. Первый ждёт доступности PostgreSQL (TCP-проверка).
2. Второй выполняет Flyway-миграции (отдельный образ с Flyway CLI или специальный jar).

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: java-app
  template:
    metadata:
      labels:
        app: java-app
    spec:
      initContainers:
      # Шаг 1: ждём готовности PostgreSQL
      - name: wait-for-postgres
        image: busybox:1.36
        command:
          - sh
          - -c
          - |
            until nc -z postgres-service 5432; do
              echo "Waiting for PostgreSQL..."; sleep 3
            done
            echo "PostgreSQL is ready"
      # Шаг 2: выполняем Flyway-миграции
      - name: flyway-migrate
        image: flyway/flyway:10-alpine
        args:
          - "-url=jdbc:postgresql://postgres-service:5432/mydb"
          - "-user=$(DB_USER)"
          - "-password=$(DB_PASSWORD)"
          - "migrate"
        env:
          - name: DB_USER
            valueFrom:
              secretKeyRef:
                name: db-secret
                key: username
          - name: DB_PASSWORD
            valueFrom:
              secretKeyRef:
                name: db-secret
                key: password
        volumeMounts:
          - name: migrations
            mountPath: /flyway/sql
      containers:
      - name: java-app
        image: my-java-app:latest
        ports:
          - containerPort: 8080
      volumes:
        - name: migrations
          configMap:
            name: flyway-migrations
```

**Почему именно init-контейнер, а не встроенный Flyway в Spring Boot**

- Init-контейнер гарантирует завершение миграций до того, как Spring Boot начнёт поднимать контекст.
- При горизонтальном масштабировании (несколько реплик) каждый под запускает init-контейнер, но Flyway использует блокировку (`flyway_schema_history`), поэтому миграции выполнятся ровно один раз.
- Flyway CLI в init-контейнере полностью отделён от образа приложения — удобно для отдельного управления версиями миграций.

**Ресурсы и статус**

Ресурсы (CPU, memory) init-контейнера учитываются отдельно: эффективный request/limit пода — это `max(sum app-containers, max init-containers)`. Статус отображается в `.status.initContainerStatuses`; команда `kubectl logs <pod> -c <init-container-name>` позволяет просматривать логи.

---

### Вопрос 44. Что такое Headless Service в Kubernetes и зачем он нужен StatefulSet? Как DNS-записи для Headless Service отличаются от обычного ClusterIP-сервиса, и как Java-приложение (например, Kafka-брокер или Hazelcast) использует эти записи для обнаружения других членов кластера?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [DNS for Services and Pods — Kubernetes Documentation](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)

**ClusterIP-сервис** получает DNS A/AAAA-запись вида `my-svc.my-namespace.svc.cluster-domain.example`, которая разрешается в один виртуальный IP (cluster IP). Весь трафик маршрутизируется через этот IP с балансировкой нагрузки.

**Headless Service** (с `clusterIP: None`) получает DNS A/AAAA-запись с тем же именем, но она разрешается в набор IP-адресов всех подов, выбранных селектором. Клиент получает несколько A-записей и самостоятельно решает, к какому поду обратиться.

**SRV-записи для Headless Service** создаются для именованных портов и разрешаются в несколько ответов — по одному на каждый под. Формат ответа: `hostname.my-svc.my-namespace.svc.cluster-domain.example`.

**DNS для StatefulSet с Headless Service:**

Если StatefulSet называется `web` и использует Headless Service `nginx` в namespace `default`:

| Pod | FQDN |
|---|---|
| web-0 | `web-0.nginx.default.svc.cluster.local` |
| web-1 | `web-1.nginx.default.svc.cluster.local` |
| web-2 | `web-2.nginx.default.svc.cluster.local` |

Каждый под получает стабильную A-запись, указывающую на его IP. Эти имена сохраняются при перезапуске пода (даже если IP меняется).

#### Ответ от Claude

**Что такое Headless Service**

Headless Service — это сервис Kubernetes с явно установленным `clusterIP: None`. В отличие от обычного ClusterIP-сервиса, он не получает виртуального IP и не осуществляет балансировки нагрузки средствами kube-proxy. Вместо этого DNS-подсистема кластера (CoreDNS) возвращает A-записи непосредственно для IP-адресов подов.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-headless-svc
spec:
  clusterIP: None        # Ключевое отличие
  selector:
    app: my-app
  ports:
  - port: 5701
    name: hazelcast
```

**Сравнение DNS-записей**

| Характеристика | ClusterIP Service | Headless Service |
|---|---|---|
| DNS A-запись | Один виртуальный IP сервиса | Набор IP-адресов всех выбранных подов |
| Балансировка | kube-proxy (iptables/ipvs) | На стороне клиента (client-side) |
| SRV-записи | Указывают на endpoint сервиса | Указывают на каждый под отдельно |
| Стабильность имени | Стабильно, IP не меняется | IP меняется при пересоздании пода, имя стабильно |

**Зачем StatefulSet требует Headless Service**

Согласно официальной документации Kubernetes, StatefulSet _требует_ Headless Service для управления сетевой идентичностью подов. Headless Service выполняет две роли:

1. **DNS-домен**: Сервис создаёт DNS-зону, в которой каждый под StatefulSet получает предсказуемое FQDN по схеме `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.
2. **Стабильная идентичность**: Даже если под переScheduled на другой узел и получает новый IP, его DNS-имя остаётся прежним. Приложения могут надёжно обращаться к конкретному экземпляру.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
spec:
  serviceName: "kafka-headless"  # Ссылка на Headless Service
  replicas: 3
  ...
```

При трёх репликах Kafka:
- `kafka-0.kafka-headless.default.svc.cluster.local`
- `kafka-1.kafka-headless.default.svc.cluster.local`
- `kafka-2.kafka-headless.default.svc.cluster.local`

**Как Kafka использует Headless Service**

Брокеры Kafka указывают `advertised.listeners` с использованием стабильных DNS-имён. Каждый брокер знает своё имя и имена соседей заранее (по ординалу), что позволяет выстроить кластер без внешнего service discovery:

```
# В конфигурации kafka-0:
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka-0.kafka-headless.default.svc.cluster.local:9092

# В конфигурации kafka-1:
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka-1.kafka-headless.default.svc.cluster.local:9092
```

Клиенты (Producer/Consumer) подключаются к любому брокеру и получают метаданные о всех участниках кластера через Kafka-протокол.

**Как Hazelcast использует Headless Service**

Hazelcast поддерживает DNS-режим обнаружения: при старте каждый экземпляр выполняет DNS-запрос к имени Headless Service и получает список IP всех активных подов. Это не требует Kubernetes RBAC (в отличие от API-режима):

```java
Config config = new Config();
config.getNetworkConfig().getJoin().getMulticastConfig().setEnabled(false);
config.getNetworkConfig().getJoin().getKubernetesConfig()
      .setEnabled(true)
      .setProperty("service-dns",
          "hazelcast-headless.default.svc.cluster.local");
```

Соответствующий Headless Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hazelcast-headless
spec:
  clusterIP: None
  selector:
    app: hazelcast
  ports:
  - name: hazelcast
    port: 5701
```

При DNS-запросе `hazelcast-headless.default.svc.cluster.local` CoreDNS возвращает A-записи для всех под-IP с меткой `app: hazelcast`. Hazelcast устанавливает соединение с каждым и формирует кластер.

**Итог: зачем Headless Service критичен для StatefulSet**

Без Headless Service StatefulSet не может обеспечить стабильные сетевые идентичности подов. ClusterIP скрывает конкретные поды за одним виртуальным IP, что делает невозможным адресацию конкретного экземпляра — а это критично для баз данных (обращение к primary/replica), брокеров сообщений и распределённых кешей.

---

### Вопрос 45. Что такое BuildKit cache mount (`--mount=type=cache`) в Dockerfile? Чем он отличается от обычного кэширования слоёв, как его использовать для ускорения Maven/Gradle-сборок в CI/CD, и почему remote cache (например, в реестре или S3) критичен для ephemeral CI-агентов?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Optimize cache usage in builds — Docker Documentation](https://docs.docker.com/build/cache/optimize/)

Cache mount — это постоянная директория, которую BuildKit монтирует в контейнер на время выполнения конкретной инструкции `RUN`. В отличие от кэширования слоёв, данные в cache mount не включаются в итоговый образ и накапливаются между сборками.

Ключевое свойство: «Cache mounts let you specify a persistent package cache to be used during builds. The cache is cumulative across builds, so you can read and write to the cache multiple times.»

При изменении входных файлов (например, `pom.xml`) слой перестраивается, но пакетный менеджер скачивает только новые или изменившиеся зависимости — остальные берёт из cache mount на диске.

Для ephemeral CI/CD агентов используется внешний remote cache: «External caches are especially useful for CI/CD pipelines, where the builders are often ephemeral, and build minutes are precious.»

Пример экспорта кэша слоёв в реестр:

```bash
docker buildx build --push -t registry/image:tag \
  --cache-to type=registry,ref=registry/cache-image \
  --cache-from type=registry,ref=registry/cache-image .
```

#### Ответ от Claude

**Что такое BuildKit cache mount**

`--mount=type=cache` — директива синтаксиса BuildKit, которая монтирует в `RUN`-шаг постоянную директорию, не входящую в итоговый образ. Данные в ней накапливаются между последовательными сборками на одном BuildKit-демоне.

Для активации синтаксиса BuildKit в начало Dockerfile добавляется:
```dockerfile
# syntax=docker/dockerfile:1
```

**Чем отличается от обычного кэширования слоёв**

| Характеристика | Кэширование слоёв (layer cache) | Cache mount (`--mount=type=cache`) |
|---|---|---|
| Принцип | Слой переиспользуется целиком, если не изменились инструкция и входные файлы | Директория сохраняется между сборками независимо от инвалидации слоя |
| Инвалидация | Изменение любого входного файла сбрасывает слой и все последующие | Слой пересобирается, но содержимое смонтированной директории остаётся |
| Попадание в образ | Данные слоя входят в итоговый образ | Данные mount НЕ входят в итоговый образ |
| Гранулярность | Всё или ничего | Инкрементальное обновление (только новые зависимости) |

Depot точно описывает это: «A change to `pom.xml` still invalidates the layer cache, but now Maven downloads only the new dependency, pulling the rest from disk in the warm cache mount.»

**Применение для Maven-сборок**

Оптимальная структура Dockerfile (двухэтапная сборка):

```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /app

# Копируем только pom.xml для кэширования зависимостей отдельным слоем
COPY pom.xml .

# Скачиваем зависимости; /root/.m2 монтируется как cache mount
RUN --mount=type=cache,target=/root/.m2 \
    mvn dependency:go-offline -B -q

# Копируем исходный код
COPY src ./src

# Собираем приложение, повторно используя cache mount с зависимостями
RUN --mount=type=cache,target=/root/.m2 \
    mvn clean package -B -DskipTests

FROM eclipse-temurin:21-jre AS runtime
COPY --from=builder /app/target/*.jar /app/app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

Ключевой момент: `pom.xml` копируется отдельно. Если исходный код изменился, но зависимости не менялись, шаг `dependency:go-offline` берётся из layer cache. Если `pom.xml` изменился, слой пересобирается, но Maven скачивает только новые зависимости — остальные уже есть в `/root/.m2`.

**Применение для Gradle-сборок**

```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /app

COPY build.gradle settings.gradle gradlew ./
COPY gradle ./gradle

# Кэшируем Gradle-кэш (wrapper, зависимости, build-cache)
RUN --mount=type=cache,target=/root/.gradle \
    ./gradlew dependencies --no-daemon -q

COPY src ./src

RUN --mount=type=cache,target=/root/.gradle \
    ./gradlew bootJar --no-daemon

FROM eclipse-temurin:21-jre AS runtime
COPY --from=builder /app/build/libs/*.jar /app/app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**Почему remote cache критичен для ephemeral CI-агентов**

Ephemeral CI-агенты (GitLab CI runners, GitHub Actions runners) уничтожаются после каждого запуска. Локальный BuildKit-кэш (включая cache mounts) хранится на диске агента и теряется вместе с ним. Из-за этого:

- Cache mount между запусками недоступен — каждая сборка скачивает все зависимости заново.
- Кэширование слоёв также бесполезно без общего хранилища.

Решение — remote cache backends, поддерживаемые BuildKit:

**1. Registry backend** (наиболее универсальный):
```bash
# Экспорт кэша в реестр после сборки
docker buildx build \
  --cache-to type=registry,ref=registry.example.com/cache/myapp:buildcache,mode=max \
  --cache-from type=registry,ref=registry.example.com/cache/myapp:buildcache \
  --push -t registry.example.com/myapp:latest .
```
Режим `mode=max` кэширует все промежуточные слои (критично для multi-stage сборок), а не только финальный.

**2. S3 backend** (для команд, работающих в AWS):
```bash
docker buildx build \
  --cache-to type=s3,region=us-east-1,bucket=my-build-cache,name=myapp \
  --cache-from type=s3,region=us-east-1,bucket=my-build-cache,name=myapp .
```

**3. GitHub Actions cache**:
```yaml
- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Важное ограничение**: cache mount (`--mount=type=cache`) и remote layer cache (`--cache-to=type=registry`) — это разные механизмы. Remote cache сохраняет слои образа, но не содержимое cache mounts. Для сохранения cache mounts между ephemeral-запусками в GitHub Actions применяется workaround через action `reproducible-containers/buildkit-cache-dance`, которая извлекает данные cache mount и помещает их в GitHub Actions cache.

**Практическая рекомендация**

Для Java-проектов в CI следует комбинировать оба подхода:

1. `--mount=type=cache,target=/root/.m2` — ускоряет сборки на персистентных агентах (самостоятельно управляемые runners, Depot).
2. Remote registry cache (`--cache-to/--cache-from type=registry`) — обеспечивает переиспользование слоёв на ephemeral-агентах.
3. Разделять `COPY pom.xml` и `COPY src` — максимизирует вероятность попадания в layer cache для шага загрузки зависимостей.

---
### Вопрос 46. Как работает blue-green deployment в Kubernetes с использованием только нативных ресурсов (Service + два Deployment)? В чём принципиальное отличие от canary-стратегии, какова механика мгновенного переключения трафика, и какие проблемы возникают при stateful-сессиях или database migrations?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Managing Workloads — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/management/)

Blue-green deployment и canary deployment — два подхода к безопасному выкату новой версии приложения.

**Canary-стратегия** в нативном Kubernetes реализуется через несколько Deployment-объектов с общим label-селектором у Service, а количество реплик в каждом Deployment задаёт долю трафика. Например, если у «стабильного» Deployment 9 реплик, а у «canary» — 1, Service будет направлять примерно 10% запросов в canary. Для разграничения версий используется метка `track`:

```yaml
# Стабильная версия
metadata:
  labels:
    app: guestbook
    track: stable

# Canary-версия
metadata:
  labels:
    app: guestbook
    track: canary
```

Service при этом выбирает поды только по метке `app: guestbook`, объединяя оба Deployment в один пул эндпоинтов.

**Blue-green deployment** использует другую механику: в любой момент времени трафик идёт только в один из двух Deployment, а переключение осуществляется сменой селектора Service. Оба Deployment одновременно присутствуют в кластере (blue — текущая версия, green — новая), но Service указывает лишь на один из них.

#### Ответ от Claude

**Механика blue-green с нативными ресурсами Kubernetes**

Blue-green deployment в Kubernetes без сторонних инструментов строится из трёх компонентов:

1. **Deployment «blue»** — текущая production-версия с меткой `version: blue`.
2. **Deployment «green»** — новая версия с меткой `version: green`, разворачивается параллельно.
3. **Service** — единственный объект, который переключает трафик.

Пример манифестов:

```yaml
# Deployment blue (текущая версия)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:1.0

---
# Deployment green (новая версия)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:2.0

---
# Service — изначально указывает на blue
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue   # <-- здесь происходит переключение
  ports:
  - port: 80
    targetPort: 8080
```

**Механика мгновенного переключения трафика**

Переключение выполняется одной командой:

```bash
kubectl patch service app-service \
  -p '{"spec":{"selector":{"version":"green"}}}'
```

После патча kube-controller-manager немедленно пересчитывает EndpointSlice для Service: из него исчезают поды blue и добавляются поды green. Изменение распространяется на все узлы через kube-proxy (или CNI-плагин). С точки зрения клиентов переключение является атомарным — они продолжают обращаться к тому же ClusterIP/ExternalIP, однако новые соединения уже маршрутизируются к green-подам.

**Принципиальное отличие от canary**

| Характеристика | Blue-Green | Canary |
|---|---|---|
| Распределение трафика | 100% на одну версию в каждый момент | Часть трафика на новую версию (например, 10%) |
| Контроль доли трафика | Через смену селектора Service (всё или ничего) | Через соотношение реплик двух Deployment |
| Точность разбивки трафика | Двоичная (blue или green) | Пропорциональная, но без гарантий процента (зависит от числа реплик) |
| Ресурсоёмкость | Требует двойного объёма ресурсов (два полных Deployment) | Canary-Deployment может иметь 1 реплику |
| Откат | Мгновенный: повторный патч селектора | Постепенный: уменьшение реплик canary до 0 |
| Возможность тестирования до переключения | Да: green доступен внутри кластера до смены селектора | Нет явного разграничения этапов |

Важно: нативный Kubernetes не поддерживает процентное разбиение трафика по весам без сервис-меша (Istio, Linkerd) или Ingress-контроллера с такой функциональностью. В чистом canary через два Deployment трафик делится приблизительно, исходя из числа реплик.

**Проблемы при stateful-сессиях**

При мгновенном переключении селектора активные HTTP-соединения, удерживаемые blue-подами, продолжают работать до завершения (если используется keep-alive). Однако новые соединения уже идут на green. Это создаёт проблемы:

- **Sticky sessions (сессионная привязка):** Если приложение хранит состояние сессии в памяти пода (не во внешнем хранилище), пользователь после переключения Service попадёт на green-под и «потеряет» сессию. Решение — хранить сессии во внешнем хранилище (Redis, БД) до переключения.
- **In-flight транзакции:** Запросы, начатые на blue-поде до переключения, завершатся там же (TCP-соединение уже установлено). Но если клиент использует короткие соединения, он может попасть то на blue, то на green в момент перехода.
- **Нет контроля «слива» трафика:** Нативный Service не поддерживает graceful drain на уровне Session — это задача самого приложения или более высокоуровневого инструмента (Argo Rollouts, Flagger).

**Проблемы при database migrations**

Это наиболее острая проблема blue-green в stateful-контексте:

- Blue и green одновременно работают с одной и той же базой данных.
- Если green-версия требует изменений схемы (добавление колонки, изменение типа), эти изменения должны быть обратно совместимы с blue-версией — иначе blue-поды начнут падать ещё до переключения трафика.
- Рекомендуемый подход — **expand/contract**: сначала выполняется миграция, добавляющая новые структуры (expand), не удаляя старые; после полного переключения трафика на green старые структуры удаляются (contract).
- Немедленные деструктивные миграции (DROP COLUMN, RENAME) несовместимы с blue-green без даунтайма.

---

### Вопрос 47. Чем Helm отличается от Kustomize? В каких случаях предпочтительнее каждый из инструментов, и как они комбинируются (Kustomize поверх Helm)? Каковы ограничения Go-шаблонизации Helm, которые решает Kustomize?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Introducing kustomize; Template-free Configuration Customization for Kubernetes — Kubernetes Blog](https://kubernetes.io/blog/2018/05/29/introducing-kustomize-template-free-configuration-customization-for-kubernetes/)

Kustomize предлагает чисто декларативный подход к настройке конфигурации, который соответствует и опирается на знакомый Kubernetes API.

Ключевая проблема, которую решает Kustomize: при использовании шаблонов (подход Helm) практически каждое поле YAML-манифеста превращается в параметр, которому необходимо присвоить значение. Разные команды хотят разных изменений — поэтому почти каждая спецификация становится параметром. Это приводит к «взрыву параметров», усложняет поддержку и требует изучения нового языка шаблонизации поверх Kubernetes API.

Kustomize вводит понятия **base** (базовая конфигурация) и **overlay** (слой кастомизации):

- **Base** — директория с `kustomization.yaml` и ресурсами; не знает об overlay, переиспользуется в нескольких overlay.
- **Overlay** — директория с `kustomization.yaml`, которая ссылается на base как на исходник и применяет поверх него патчи.

Инструмент читает ссылки на ресурсы Kubernetes из `kustomization.yaml`, применяет декларативные преобразования и направляет результат в stdout, откуда он может быть передан в `kubectl apply` или другие инструменты.

#### Ответ от Claude

**Фундаментальные различия**

Helm и Kustomize решают пересекающиеся, но разные задачи:

| Аспект | Helm | Kustomize |
|---|---|---|
| Роль | Пакетный менеджер (package manager) | Инструмент кастомизации конфигурации |
| Подход | Go-шаблонизация + values | Патчи поверх чистых YAML-манифестов |
| Язык | Шаблоны в синтаксисе Go text/template | Нативные Kubernetes-манифесты |
| Управление релизами | Да: версии, откат, история | Нет: нет понятия «релиз» |
| Packaging & distribution | Да: OCI-репозитории, `helm repo` | Нет: только Git/локальные файлы |
| Зависимости между чартами | Да: `Chart.yaml` → `dependencies` | Ограниченно: через `resources` |
| Нативная интеграция в kubectl | Нет | Да: `kubectl apply -k` с v1.14 |

**Когда предпочтителен Helm**

- Упаковка и дистрибуция приложений как единого артефакта (чарт в OCI-реестре).
- Сложные зависимости между компонентами (subchart).
- Необходимость управления жизненным циклом: `helm upgrade`, `helm rollback` с историей ревизий.
- Использование публичных чартов из Artifact Hub (Prometheus, Grafana, cert-manager и др.) без необходимости поддерживать манифесты самостоятельно.
- Параметризация под множество клиентов или окружений с существенно разными конфигурациями.

**Когда предпочтителен Kustomize**

- Управление environment-specific конфигурацией (dev/staging/prod) поверх единой базы.
- GitOps-подходы (Argo CD, Flux), где важна читаемость и декларативность манифестов.
- Применение точечных изменений к чужим манифестам без их форка (патч нескольких полей).
- Добавление единых аннотаций, лейблов, resource limits ко всем ресурсам окружения.
- Команды, хорошо знакомые с Kubernetes API, но не желающие изучать синтаксис Helm-шаблонов.

**Ограничения Go-шаблонизации Helm**

1. **Whitespace и отступы.** YAML-формат чувствителен к пробелам; шаблонизатор Go сохраняет пробелы вокруг директив `{{ }}` дословно. Для борьбы с этим Helm использует синтаксис `{{-` / `-}}` (удаление пробелов слева/справа). Ошибки в управлении пробелами приводят к невалидному YAML, который обнаруживается только в runtime.

2. **Scope в блоках `with` и `range`.** Внутри блока `with .Values.someSection` переменная `.` переопределяется, и доступ к `.Release.Name` или другим глобальным значениям требует использования переменной `$` или сохранения контекста заранее. Это неочевидно и является частым источником ошибок.

3. **Взрыв параметров.** Если чарт должен поддерживать множество вариантов конфигурации, `values.yaml` разрастается до сотен строк. Любое поле, которое хоть в одном окружении нужно изменить, становится параметром.

4. **Сложность отладки.** Нерендеренные шаблоны нечитаемы; отрендеренный результат получается через `helm template`, но ошибки шаблонизации проявляются как непонятные Go-паники или кривой YAML.

5. **Встроенные условия усложняют поддержку.** Глубоко вложенные `{{- if .Values.feature.enabled }}` блоки внутри YAML-манифестов делают шаблоны похожими на смесь двух языков.

Kustomize устраняет все эти проблемы, работая непосредственно с YAML через два механизма патчей:
- **Strategic Merge Patch** — слияние YAML-словарей с учётом semantics Kubernetes (например, контейнеры идентифицируются по `name`, а не по позиции в массиве).
- **JSON Patch (RFC 6902)** — точечные операции `add`, `remove`, `replace` на конкретных путях.

**Комбинирование: Kustomize поверх Helm**

Существуют три практических способа совместного использования:

1. **`helm template` + `kustomize build`:** Helm рендерит шаблоны в чистый YAML (`helm template myrelease ./chart > base.yaml`), затем Kustomize применяет патчи поверх. Недостаток: теряется управление релизом Helm (нет `helm upgrade`/`helm rollback`).

2. **Helm post-renderer:** Helm поддерживает флаг `--post-renderer`, позволяющий пропустить отрендеренные манифесты через внешнюю программу перед применением. `kustomize build` можно использовать как post-renderer:
   ```bash
   helm upgrade myrelease ./chart --post-renderer ./kustomize-wrapper.sh
   ```
   При этом сохраняется управление релизом Helm, а Kustomize применяет дополнительные патчи (например, добавляет аннотации, изменяет resource limits) без изменения исходного чарта.

3. **`helmCharts` в `kustomization.yaml`:** Kustomize v4+ поддерживает поле `helmCharts`, позволяющее объявить Helm-чарт как источник ресурсов:
   ```yaml
   helmCharts:
   - name: prometheus
     repo: https://prometheus-community.github.io/helm-charts
     version: 25.0.0
     releaseName: prometheus
     valuesFile: values.yaml
   ```
   Сборка выполняется командой `kustomize build --enable-helm`. Официальная документация Kustomize явно указывает, что это ограниченное подмножество функциональности Helm, предназначенное для упрощённого старта, а не полная замена.

Наиболее распространённая production-практика в GitOps: Helm управляет упаковкой и версионированием приложений, Kustomize (или Argo CD ApplicationSets) управляет environment-специфичными патчами поверх отрендеренных манифестов.

---

### Вопрос 48. Как работают Helm-хуки (hooks)? Какие типы хуков существуют (pre-install, post-upgrade, pre-rollback и др.), как управлять порядком их выполнения через hook-weight, и почему `helm rollback` не откатывает database migrations, выполненные pre-upgrade-хуком?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Chart Hooks — Helm Documentation](https://helm.sh/docs/topics/charts_hooks/)

Helm предоставляет механизм хуков, позволяющий вмешаться в определённые точки жизненного цикла релиза. Хуки реализуются как обычные Kubernetes-ресурсы (как правило, Job или Pod), помеченные специальными аннотациями.

**Объявление хука** — добавление аннотации в манифест:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pre-upgrade-migrations
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
```

**Все типы хуков:**

| Хук | Когда выполняется |
|---|---|
| `pre-install` | После рендеринга шаблонов, до создания ресурсов |
| `post-install` | После загрузки всех ресурсов в Kubernetes |
| `pre-upgrade` | После рендеринга шаблонов при апгрейде, до обновления ресурсов |
| `post-upgrade` | После обновления всех ресурсов при апгрейде |
| `pre-rollback` | После рендеринга шаблонов при откате, до отката ресурсов |
| `post-rollback` | После отката всех ресурсов |
| `pre-delete` | При удалении, до удаления ресурсов |
| `post-delete` | После удаления всех ресурсов релиза |
| `test` | При вызове `helm test` |

**Управление порядком через hook-weight:** Helm сортирует хуки по аннотации `helm.sh/hook-weight` в порядке возрастания (от меньшего к большему). Веса — строки, могут быть отрицательными. По умолчанию вес равен 0. При одинаковом весе ресурсы сортируются по типу и имени.

**Политика удаления хуков** (`helm.sh/hook-delete-policy`):
- `before-hook-creation` — удалить предыдущий ресурс хука перед запуском нового (по умолчанию).
- `hook-succeeded` — удалить ресурс после успешного выполнения.
- `hook-failed` — удалить ресурс после неудачного выполнения.

**Критически важное ограничение:** «Ресурсы, создаваемые хуком, в настоящее время не отслеживаются и не управляются как часть релиза» (цитата из документации). Это означает, что `helm uninstall` не удалит Job, созданный хуком, если не задана политика удаления.

#### Ответ от Claude

**Жизненный цикл хуков при различных операциях**

Helm выполняет хуки синхронно и блокирующе: если хук-Job или хук-Pod не завершается успешно, операция прерывается с ошибкой. Для ресурсов типа Job/Pod Helm ожидает завершения с кодом 0; для прочих типов — факта применения в кластере.

Полная последовательность для `helm upgrade`:

1. Рендеринг шаблонов чарта.
2. Проверка и валидация.
3. Запуск `pre-upgrade`-хуков (по возрастанию `hook-weight`).
4. Применение основных ресурсов релиза (Deployment, Service и т.д.).
5. Запуск `post-upgrade`-хуков.
6. Запись новой ревизии в Secret Helm.

Полная последовательность для `helm rollback`:

1. Рендеринг шаблонов целевой ревизии.
2. Запуск `pre-rollback`-хуков.
3. Применение ресурсов из целевой ревизии (откат Kubernetes-ресурсов).
4. Запуск `post-rollback`-хуков.

**Управление порядком через hook-weight**

```yaml
# Этот хук выполнится первым (вес -10)
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "-10"

# Этот хук выполнится вторым (вес 0)
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "0"

# Этот хук выполнится последним (вес 5)
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "5"
```

Веса обязательно указываются строками. Сортировка внутри одного веса — по Kind, затем по имени ресурса.

**Почему `helm rollback` не откатывает database migrations**

Это фундаментальное архитектурное ограничение, обусловленное тремя причинами:

1. **Хуки не являются частью состояния релиза.** Документация Helm прямо указывает: ресурсы, созданные хуками, «не отслеживаются и не управляются как часть релиза». Helm хранит в Secret состояние только основных ресурсов (Deployment, ConfigMap, Service и т.д.). Job, выполнивший миграцию, не входит в «снимок» ревизии.

2. **`helm rollback` оперирует только Kubernetes-ресурсами.** Команда откатывает декларативное состояние Kubernetes-объектов до предыдущей ревизии: пересоздаёт Deployment со старым образом, восстанавливает ConfigMap. Но база данных — это внешнее, stateful хранилище, находящееся вне области ответственности Kubernetes reconciliation loop.

3. **Не-атомарность pre-upgrade хуков.** Как описывает практика (источник: brtkwr.com): `pre-upgrade`-хук выполняется до применения основных манифестов. Если хук завершился успешно, миграция уже применена к БД. После этого, даже если сам `helm upgrade` завершился с ошибкой (например, новые поды не стартовали), данные в БД изменены. При последующем `helm rollback` Kubernetes-ресурсы возвращаются к предыдущей ревизии, но схема БД остаётся в новом состоянии.

**Практические последствия и рекомендации**

При несовместимой с откатом схемой БД возникает split-brain: старые поды (после rollback) работают с новой схемой, для которой они не предназначены.

Стратегии решения:

- **Backward-compatible migrations (expand/contract):** Каждая миграция добавляет новые структуры, не удаляя старые. После стабилизации новой версии запускается отдельная «cleanup»-миграция. Это гарантирует, что и старая, и новая версия приложения работают с одной схемой.

- **Явный `pre-rollback`-хук с down-миграцией:** Парный хук, выполняющий обратную миграцию схемы. Работает только если миграции обратимы (не всегда возможно при удалении колонок с данными).

- **Вынос миграций за пределы Helm:** Управление миграциями отдельным инструментом (Flyway, Liquibase, Atlas) с независимым от Helm жизненным циклом и явным контролем версий схемы.

- **Флаг `--no-hooks`:** При откате можно указать `helm rollback --no-hooks`, чтобы не запускать `pre-rollback`-хуки, если down-миграция может навредить. Но это не решает исходную проблему несовместимости схемы.

**Итог:** `helm rollback` — это откат Kubernetes-манифестов, а не откат состояния приложения. Database migrations, выполненные в `pre-upgrade`-хуке, являются необратимыми с точки зрения Helm, потому что они находятся вне Kubernetes state machine, которой управляет Helm.

---
### Вопрос 49. Что такое VPA (VerticalPodAutoscaler) и чем он принципиально отличается от HPA? Почему нельзя использовать VPA в режиме Auto совместно с HPA, масштабирующим по CPU/memory? Как правильно комбинировать VPA и HPA для Java-сервисов с непредсказуемым потреблением памяти?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Kubernetes VPA: Architecture, Limitations & Best Practices (2026) — ScaleOps](https://scaleops.com/blog/kubernetes-vpa/)

**Принципиальное различие VPA и HPA.**
HPA изменяет количество подов: добавляет или убирает реплики на основе CPU, памяти или пользовательских метрик. VPA изменяет размер каждого пода: обновляет requests и limits CPU и памяти на основе наблюдаемого потребления. Иными словами, HPA решает задачу пропускной способности через добавление реплик, VPA решает задачу эффективности через переразмерение существующих подов.

**Режимы работы VPA.**
- **Off** — VPA рассчитывает рекомендации, но не применяет их; полезен для аудита.
- **Initial** — ресурсы задаются только при создании пода; работающие поды не перезапускаются.
- **Recreate** — VPA активно вытесняет (evict) поды для применения новых requests через пересоздание.
- **InPlaceOrRecreate** (VPA 1.4.0+, K8s 1.35+) — сначала пытается применить live-resize без перезапуска, при неудаче откатывается на Recreate.
- **Auto** был deprecated в VPA 1.4.0 и теперь является псевдонимом для Recreate.

**Почему VPA (Recreate/Auto) нельзя совмещать с HPA по CPU/memory.**
Возникает циклическая обратная связь — «death spiral»:
1. VPA повышает CPU request пода на основе наблюдаемой утилизации.
2. Более высокий request снижает процент утилизации CPU (числитель не изменился, знаменатель вырос).
3. HPA интерпретирует сниженную утилизацию как недозагрузку и уменьшает число реплик.
4. Меньше реплик — нагрузка на оставшиеся поды растёт — утилизация снова высокая — VPA снова поднимает requests.

Возможен и обратный сценарий: VPA снижает requests → утилизация в процентах скачет вверх → HPA резко наращивает реплики → VPA видит меньше потребления на под и снижает requests ещё сильнее. Официальная документация Kubernetes (`known-limitations.md` репозитория `kubernetes/autoscaler`) прямо гласит: «VPA should not be used with the Horizontal Pod Autoscaler (HPA) on the same resource metric (CPU or memory) at this moment».

**Правильная комбинация VPA и HPA для Java-сервисов.**
1. Запустите VPA в режиме **Off** и собирайте рекомендации не менее одной недели, охватив разные уровни нагрузки.
2. Для памяти используйте VPA, а не HPA. У Java-процесса размер heap задаётся флагами JVM при старте (`-Xms`/`-Xmx`); динамическое масштабирование памяти in-place невозможно без перезапуска. VPA в режиме Recreate (или InPlaceOrRecreate) позволяет правильно выставить memory request при перезапуске пода.
3. HPA настраивайте **на другую метрику** — HTTP RPS, latency p99, длину очереди или пользовательскую метрику — но не на CPU/memory. Это устраняет конфликт: два контроллера управляют непересекающимися сигналами.
4. Задайте явные границы `minAllowed` и `maxAllowed` в политике VPA, чтобы исключить слишком агрессивные рекомендации.
5. Для JVM-специфичного потребления памяти (metaspace, GC overhead, off-heap) убедитесь, что memory request включает буфер сверх `-Xmx` — как правило, не менее 20–30% от heap.

#### Ответ от Claude

**Что такое VPA.**
VerticalPodAutoscaler (VPA) — это расширение (add-on) для Kubernetes, не входящее в дистрибутив по умолчанию. Оно автоматически подбирает CPU requests/limits и memory requests/limits для контейнеров в поде на основе реального потребления. VPA состоит из трёх компонентов: Recommender (анализирует метрики и формирует рекомендации), Updater (вытесняет поды, чьи resources расходятся с рекомендациями) и Admission Controller (подставляет рекомендованные resources при создании нового пода).

**Принципиальное отличие от HPA.**
HPA оперирует числом реплик — горизонтальная ось масштабирования. VPA оперирует размером каждого пода — вертикальная ось. HPA предполагает, что поды уже правильно размерены, и добавляет их при росте нагрузки. VPA предполагает, что число реплик зафиксировано или управляется отдельно, и корректирует ресурсы каждого пода. Для VPA требуется установленный Metrics Server, как и для HPA.

**Режимы updateMode.**
| Режим | Поведение |
|---|---|
| Off | Только рекомендации, без изменений |
| Initial | Применяется только при создании нового пода |
| Recreate | Вытесняет работающие поды для пересоздания с новыми resources |
| InPlaceOrRecreate | Live-resize без перезапуска, откат на Recreate при неудаче (K8s 1.35+, VPA 1.4.0+) |

Режим Auto был deprecated в VPA 1.4.0 и стал псевдонимом Recreate.

**Почему VPA (Recreate/Auto) + HPA по CPU/memory — опасная комбинация.**
Оба контроллера реагируют на одни и те же сигналы (CPU utilization, memory utilization), создавая петлю обратной связи:
- VPA поднимает memory request → утилизация памяти в процентах падает → HPA видит «мало нагрузки» и сокращает реплики → нагрузка на оставшиеся поды растёт → VPA снова поднимает request.
- Обратный сценарий столь же возможен.

Официальная документация VPA (`known-limitations.md`) явно запрещает такую конфигурацию: «VPA should not be used with the Horizontal Pod Autoscaler (HPA) on the same resource metric (CPU or memory) at this moment». Допустимо использовать VPA и HPA одновременно только при условии, что они следят за **разными метриками** (например, VPA — память, HPA — число запросов в секунду).

**Расхождения между источниками.** Документация kubernetes.io (раздел «Autoscaling Workloads») говорит «do not use», не уточняя версии. Документация репозитория kubernetes/autoscaler (`known-limitations.md`) добавляет оговорку «at this moment», признавая, что ограничение временное. ScaleOps-блог описывает конкретный «death spiral» с примером числовых значений. В целом источники согласуются: одновременное использование на одних метриках недопустимо.

**Правильная комбинация для Java-сервисов с непредсказуемым потреблением памяти.**

1. **VPA в режиме Off сначала.** Запустите VPA и неделю собирайте рекомендации, ничего не меняя. Для Java важно охватить пиковые сессии GC и прогрев JVM.

2. **VPA управляет памятью, HPA — репликами по внешней метрике.**
   - VPA (режим Recreate или InPlaceOrRecreate) корректирует memory request при перезапуске. Это особенно важно для Java: heap size задаётся флагами JVM `-Xms`/`-Xmx` при старте; без перезапуска пода heap не изменится.
   - HPA реагирует на HTTP RPS, latency, длину очереди (через Prometheus Adapter или KEDA) — но не на CPU/memory utilization.

3. **Явные границы.** В `containerPolicies` VPA задайте `minAllowed` и `maxAllowed`:
   ```yaml
   containerPolicies:
   - containerName: app
     minAllowed:
       memory: 512Mi
     maxAllowed:
       memory: 4Gi
   ```

4. **Буфер для JVM off-heap.** Memory request должен включать не только `-Xmx`, но и overhead: metaspace, thread stacks, code cache, direct buffers. Практическое правило: `memory request = Xmx + 20-30% от Xmx`.

5. **Опциональный режим Off + ручное применение.** Если стабильность важнее автоматики, держите VPA в Off, читайте рекомендации раз в неделю и применяйте вручную через деплой — это исключает нежелательные рестарты в продакшне.

---

### Вопрос 50. Что такое KEDA (Kubernetes Event-Driven Autoscaling) и какую проблему HPA он решает? Как KEDA позволяет масштабировать поды до нуля реплик (scale-to-zero), и как выглядит ScaledObject для Java-потребителя Kafka, который должен простаивать при пустом топике?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [KEDA | Kubernetes Event-driven Autoscaling — официальный сайт](https://keda.sh/)

KEDA — это «single-purpose and lightweight component that can be added into any Kubernetes cluster», позволяющий масштабировать контейнеры на основе числа событий, требующих обработки. Компонент поддерживает масштабирование «to/from zero» — сокращение числа реплик до нуля, когда события отсутствуют. KEDA работает совместно со стандартными компонентами Kubernetes, включая HPA, расширяя его функциональность без перезаписи или дублирования. Поддерживаются более 70 встроенных масштабировщиков: Kafka, RabbitMQ, Azure Service Bus, AWS SQS, PostgreSQL, Redis, Prometheus и другие.

Пример ScaledObject для Apache Kafka с включённым scale-to-zero (из официальной документации KEDA v2.16):

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-scaledobject
  namespace: default
spec:
  scaleTargetRef:
    name: azure-functions-deployment
  minReplicaCount: 0
  maxReplicaCount: 10
  pollingInterval: 30
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: localhost:9092
      consumerGroup: my-group
      topic: test-topic
      lagThreshold: "50"
      offsetResetPolicy: latest
    authenticationRef:
      name: keda-trigger-auth-kafka-credential
```

При `minReplicaCount: 0` KEDA масштабирует деплоймент до нуля реплик, когда лаг топика равен нулю, и поднимает поды обратно при появлении сообщений.

#### Ответ от Claude

**Что такое KEDA и какую проблему HPA он решает.**

Стандартный HPA умеет масштабировать деплойменты только по метрикам CPU и памяти (из Metrics Server) или по пользовательским метрикам (через Custom Metrics API). Он не умеет:
- масштабировать на основе состояния внешних систем (длина очереди в Kafka, RabbitMQ, SQS и т.д.);
- масштабировать до **нуля реплик** — минимум HPA равен 1.

KEDA (Kubernetes Event-Driven Autoscaler) — это CNCF-проект (graduated), который решает обе проблемы. Он добавляет в кластер:
1. **KEDA Operator** (`keda-operator`) — отвечает за фазу активации: поднимает деплоймент с 0 до 1 реплики при появлении событий и опускает обратно до 0 при их отсутствии.
2. **Metrics API Server** (`keda-operator-metrics-apiserver`) — экспонирует метрики из внешних источников как Custom Metrics Kubernetes API; именно эти метрики стандартный HPA использует для масштабирования от 1 до N реплик.
3. **Admission Webhooks** — валидируют конфигурацию ресурсов KEDA.

Таким образом, KEDA не заменяет HPA, а дополняет его: KEDA управляет диапазоном 0↔1 (activation phase), HPA управляет диапазоном 1↔N (scaling phase).

**Как работает scale-to-zero.**

Фаза деактивации (scale to zero): когда KEDA opol опрашивает источник событий (`pollingInterval`) и обнаруживает, что метрика равна нулю (например, лаг Kafka-топика = 0), Operator устанавливает `spec.replicas = 0` у целевого деплоймента. HPA при этом деактивируется — он не может управлять ресурсом с нулём реплик.

Фаза активации (scale from zero): при появлении хотя бы одного события Operator устанавливает `spec.replicas = 1`, HPA снова берёт управление и масштабирует дальше на основе метрик.

Ключевое поле в ScaledObject: `minReplicaCount: 0`. При значении 1 и выше scale-to-zero отключён.

**Компоненты ScaledObject.**

| Поле | Назначение |
|---|---|
| `scaleTargetRef.name` | Имя Deployment или StatefulSet для масштабирования |
| `minReplicaCount` | Минимум реплик; 0 включает scale-to-zero |
| `maxReplicaCount` | Верхняя граница реплик |
| `pollingInterval` | Интервал опроса источника событий в секундах (default 30) |
| `cooldownPeriod` | Задержка перед масштабированием вниз в секундах (default 300) |
| `triggers` | Список источников событий и их параметры |

**ScaledObject для Java-потребителя Kafka с простоем при пустом топике.**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: java-kafka-consumer-scaler
  namespace: production
spec:
  scaleTargetRef:
    name: java-kafka-consumer          # имя Deployment Java-сервиса
  minReplicaCount: 0                   # scale-to-zero при пустом топике
  maxReplicaCount: 20
  pollingInterval: 15                  # опрашивать каждые 15 секунд
  cooldownPeriod: 120                  # 2 минуты перед масштабированием вниз
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka-broker-0.kafka:9092,kafka-broker-1.kafka:9092
      consumerGroup: java-service-consumer-group
      topic: orders-input
      lagThreshold: "10"               # одна реплика на каждые 10 непрочитанных сообщений
      offsetResetPolicy: latest
      allowIdleConsumers: "false"      # не создавать реплики сверх числа партиций
      scaleToZeroOnInvalidOffset: "false"
```

**Пояснение ключевых параметров для Java-сервиса.**

- `lagThreshold: "10"` — KEDA вычисляет желаемое число реплик как `totalLag / lagThreshold`. При лаге 100 сообщений будет 10 реплик (если не превышает maxReplicaCount). Значение подбирается по желаемому времени обработки.
- `cooldownPeriod: 120` — задержка перед тем, как KEDA начнёт опускать реплики вниз после снижения нагрузки. Для Java важно: JVM требует времени на прогрев, поэтому слишком агрессивное масштабирование вниз/вверх вызывает деградацию производительности. Увеличьте cooldownPeriod если наблюдаете частые cold start penalties.
- `allowIdleConsumers: "false"` — число реплик не превысит количество партиций топика, что разумно для Java Kafka consumer (лишние поды просто будут idle без назначенных партиций).
- `minReplicaCount: 0` — при лаге = 0 деплоймент масштабируется до нуля. При появлении первого сообщения KEDA поднимет под. Следует учитывать cold start time JVM: если недопустима задержка обработки первого сообщения, установите `minReplicaCount: 1`.

**Расхождения между источниками.** Документация KEDA (keda.sh) и официальный репозиторий (github.com/kedacore/keda) согласуются в описании архитектуры и ScaledObject. Документация kubernetes.io в разделе «Autoscaling Workloads» упоминает KEDA как отдельный CNCF-проект без детального описания. Документация Azure AKS (learn.microsoft.com/azure/aks/keda-about) совпадает с основной документацией KEDA, добавляя детали установки через AKS add-on.

---

### Вопрос 51. Один из 16 инстансов Java-сервиса в Kubernetes примерно раз в неделю деградирует из-за CPU throttling. С чего начать диагностику и как устранить причину?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Habr — Java-собеседование 2025: разбор вопросов](https://habr.com/ru/articles/1043906/)

В статье предлагается начать с наблюдаемости: дашборд Grafana с метриками CPU, памяти и GC; провести нагрузочное тестирование, чтобы воспроизвести проблему; временно поднять уровень логирования на проблемном инстансе для сбора деталей.

#### Ответ от Claude

**Что происходит:** Kubernetes ограничивает CPU через CFS quota (`cpu.cfs_quota_us`/`cpu.cfs_period_us`, период обычно 100мс). Когда контейнер выбирает квоту, все его потоки **throttling** — простаивают до начала следующего периода, что даёт всплески латентности.

**Диагностика:**
1. Метрики `container_cpu_cfs_throttled_periods_total` и `container_cpu_cfs_periods_total` (доля throttled-периодов), CPU usage vs limit, GC-паузы и число GC-потоков.
2. Сопоставить пик с расписанием (раз в неделю → возможно еженедельный батч/cron, всплеск трафика).
3. Проверить, сколько процессоров «видит» JVM в контейнере — старые JVM могли видеть все ядра ноды и поднимать слишком много GC/ForkJoin-потоков (`-XX:ActiveProcessorCount`, контейнер-aware JVM).

**Устранение:** правильно выставить `requests` по реальному потреблению и `limits` на 20–50% выше (или для критичных сервисов — requests без жёсткого limit, чтобы CFS не throttle'ил при всплесках); ограничить число GC-потоков. См. [Kubernetes — CPU Management](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/) и [Datadog — CPU requests & limits](https://www.datadoghq.com/blog/kubernetes-cpu-requests-limits/).

---

### Вопрос 52. Что такое RBAC в Kubernetes? Чем Role отличается от ClusterRole, а RoleBinding — от ClusterRoleBinding? Почему подам рекомендуется задавать отдельный ServiceAccount с минимальными правами, а не использовать дефолтный?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [RBAC Good Practices — Kubernetes Documentation](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)

RBAC (Role-Based Access Control) — механизм авторизации Kubernetes, управляющий доступом к API-ресурсам. Роли определяют набор разрешённых операций (verbs) над ресурсами (resources); привязки (Bindings) связывают роли с субъектами (users, groups, serviceaccounts).

**Role vs ClusterRole:**
- `Role` действует в пределах одного namespace. `ClusterRole` — кластерный ресурс без namespace.
- Использование `ClusterRole` с `ClusterRoleBinding` даёт права во всех namespace кластера — применять с осторожностью.

**Рекомендации:**
- Назначать минимально необходимые права (principle of least privilege).
- Избегать wildcard (`*`) в `resources` и `verbs` — эквивалент прав администратора.
- Отключать автомонтирование токена ServiceAccount, если поду не нужен доступ к API:

```yaml
spec:
  automountServiceAccountToken: false
```

- Не использовать группу `system:masters` — она обходит все проверки авторизации.

#### Ответ от Claude

**Что такое RBAC и его основные объекты**

RBAC (Role-Based Access Control) — система авторизации Kubernetes, активированная по умолчанию с v1.8. Она управляет доступом к ресурсам Kubernetes API (pods, secrets, deployments и т.д.) на основе ролей, а не индивидуальных разрешений.

Четыре ключевых объекта:

| Объект | Уровень | Назначение |
|--------|---------|------------|
| `Role` | Namespace | Набор правил доступа к ресурсам конкретного namespace |
| `ClusterRole` | Кластер | Набор правил доступа без привязки к namespace (или к не-namespace ресурсам: nodes, pv) |
| `RoleBinding` | Namespace | Привязывает Role или ClusterRole к субъекту в рамках namespace |
| `ClusterRoleBinding` | Кластер | Привязывает ClusterRole к субъекту во всех namespace |

**Важное различие:** ClusterRole можно привязать через RoleBinding к конкретному namespace — это позволяет переиспользовать одну ClusterRole для нескольких namespace без создания дублирующихся Role.

**Структура правил (rules)**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]             # "" — core API group
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]
```

Полная связка Role + RoleBinding + ServiceAccount:

```yaml
# ServiceAccount для Java-сервиса
apiVersion: v1
kind: ServiceAccount
metadata:
  name: java-service-sa
  namespace: production
automountServiceAccountToken: false  # Отключаем если API не нужен

---
# Привязка роли к ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: java-service-pod-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: java-service-sa
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

---
# Указываем ServiceAccount в Deployment
spec:
  template:
    spec:
      serviceAccountName: java-service-sa
```

**Почему нельзя использовать дефолтный ServiceAccount**

По умолчанию каждый namespace содержит ServiceAccount с именем `default`, который автоматически назначается всем подам, не указавшим `serviceAccountName`. Проблемы:

1. **Разделение ответственности отсутствует.** Если одному приложению дать права через `default`, эти права получают все поды namespace.
2. **Автомонтирование токена.** Kubernetes монтирует токен ServiceAccount в каждый под по пути `/var/run/secrets/kubernetes.io/serviceaccount/token`. Если приложение не использует API Kubernetes, этот токен — лишняя поверхность атаки: скомпрометированный под может делать запросы к API-серверу.
3. **Нарушение принципа минимальных привилегий.** Даже если у `default` минимальные права, злоумышленник через смежный под может эксплуатировать их в других приложениях.

**Опасные права, которых следует избегать**

| Право | Риск |
|-------|------|
| `verbs: ["*"]` или `resources: ["*"]` | Аналог admin-доступа |
| `list`/`watch` на Secrets | Раскрывает содержимое всех секретов (не только `get`) |
| `create` для pods/deployments | Позволяет смонтировать любой Secret или Volume в созданный под |
| `nodes/proxy` subresource | Обход audit log, прямой доступ к kubelet API |
| `escalate`, `bind`, `impersonate` | Позволяют повышать собственные привилегии |

**Расхождения между источниками:** Официальная документация Kubernetes и CIS Kubernetes Benchmark согласуются в необходимости принципа least privilege и дефолтного отключения автомонтирования токена. Разногласий по основным рекомендациям нет.

---

### Вопрос 53. Что такое LimitRange и ResourceQuota в Kubernetes? Чем они отличаются, и как их совместное использование защищает кластер от «шумных соседей» в namespace, где работают Java-микросервисы без явных resource requests?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Limit Ranges — Kubernetes Documentation](https://kubernetes.io/docs/concepts/policy/limit-range/)

LimitRange — политика, ограничивающая распределение ресурсов (запросы и лимиты) для объектов в namespace.

LimitRange может:
- Минимальное и максимальное потребление вычислительных ресурсов на Pod или Container.
- Минимальный и максимальный запрос хранилища на PersistentVolumeClaim.
- Соотношение между request и limit для ресурса.
- **Значения по умолчанию** — автоматически подставляются в контейнеры при создании.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-resource-constraint
spec:
  limits:
  - default:          # лимит по умолчанию
      cpu: 500m
    defaultRequest:   # request по умолчанию
      cpu: 500m
    max:
      cpu: "1"
    min:
      cpu: 100m
    type: Container
```

**Важное ограничение:** LimitRange применяется только при создании Pod/Container. Уже существующие объекты не затрагиваются изменением или созданием LimitRange.

#### Ответ от Claude

**LimitRange и ResourceQuota: разные уровни управления ресурсами**

| Аспект | LimitRange | ResourceQuota |
|--------|-----------|---------------|
| Область действия | Отдельный Pod / Container / PVC | Весь namespace (суммарно) |
| Назначение | Ограничивает/задаёт min/max/default для одного объекта | Ограничивает общий пул ресурсов namespace |
| Типичный пример | Один контейнер не может запросить более 2 CPU | Все контейнеры namespace суммарно не могут превысить 20 CPU |
| Момент применения | При создании объекта (admission) | При создании объекта (admission) |

**LimitRange детально**

LimitRange поддерживает четыре поля в `spec.limits[].{}`:

- `default` — лимит, подставляемый если контейнер его не задал.
- `defaultRequest` — request, подставляемый если контейнер его не задал.
- `max` — жёсткий потолок: контейнер не может превысить это значение.
- `min` — жёсткий пол: контейнер не может запросить меньше.

Пример для namespace с Java-микросервисами:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: java-services-limits
  namespace: java-team
spec:
  limits:
  - type: Container
    default:
      cpu: "1"
      memory: 512Mi
    defaultRequest:
      cpu: 200m
      memory: 256Mi
    max:
      cpu: "4"
      memory: 4Gi
    min:
      cpu: 100m
      memory: 128Mi
```

Если разработчик деплоит Pod без указания resources — LimitRange автоматически подставит `defaultRequest` и `default`, и под будет иметь хоть какие-то ограничения.

**ResourceQuota детально**

ResourceQuota задаёт суммарный пул ресурсов для всех объектов namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: java-team-quota
  namespace: java-team
spec:
  hard:
    requests.cpu: "10"          # все pods вместе не могут запросить > 10 CPU
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"                  # не более 50 подов
    persistentvolumeclaims: "10"
    count/deployments.apps: "20"
```

**Критичный момент:** если в namespace установлена ResourceQuota на CPU/memory, каждый новый Pod **обязан** указать `resources.requests` и `resources.limits`. Поды без resources будут отклонены с ошибкой `must specify limits`. Именно поэтому LimitRange и ResourceQuota **должны использоваться вместе** — LimitRange обеспечивает дефолтные значения, ResourceQuota устанавливает суммарный потолок.

**Защита от «шумных соседей» для Java-микросервисов**

Без LimitRange и ResourceQuota Java-приложение, запущенное без `resources`, получает неограниченный доступ к CPU и памяти хост-узла. Это типичная проблема с JVM: если не ограничить heap и GC-потоки, один Java-сервис при утечке памяти или спайке нагрузки может вытеснить все соседние поды на узле.

Совместное использование:

1. LimitRange задаёт дефолтные requests/limits для подов без явной конфигурации — защита от беспечных разработчиков.
2. ResourceQuota ограничивает суммарное потребление namespace — даже если все Java-сервисы потребляют по максимуму, они не «съедают» ресурсы других команд.
3. QoS-класс (`Guaranteed` / `Burstable` / `BestEffort`) определяет очерёдность выселения при нехватке ресурсов. С корректным LimitRange поды получают класс хотя бы `Burstable`, а не `BestEffort`.

---

### Вопрос 54. Что такое taints и tolerations в Kubernetes? Как они отличаются от nodeAffinity? Для чего применяется эффект NoExecute, и как правильно выделить отдельные узлы для memory-intensive Java-приложений?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Taints and Tolerations — Kubernetes Documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)

**Taints** (метки-отталкиватели) — свойства узлов, позволяющие отказывать в размещении подов, которые не имеют соответствующих допусков (tolerations).

**Три эффекта taint:**

| Эффект | Поведение |
|--------|-----------|
| `NoSchedule` | Новые поды без toleration не будут размещены на узле. Существующие поды не вытесняются. |
| `PreferNoSchedule` | Мягкое предпочтение — планировщик постарается не размещать поды без toleration, но гарантии нет. |
| `NoExecute` | Поды без toleration вытесняются немедленно; новые не планируются. |

Добавление taint на узел:
```bash
kubectl taint nodes node1 key1=value1:NoSchedule
```

Toleration в Pod:
```yaml
tolerations:
- key: "key1"
  operator: "Equal"
  value: "value1"
  effect: "NoSchedule"
```

**NoExecute с `tolerationSeconds`:** pod будет вытеснен через заданное число секунд, даже если у него есть toleration:
```yaml
tolerations:
- key: "key1"
  operator: "Equal"
  value: "value1"
  effect: "NoExecute"
  tolerationSeconds: 3600
```

#### Ответ от Claude

**Taints и Tolerations vs Node Affinity**

Оба механизма влияют на планирование подов, но работают по-разному:

| Характеристика | Taints / Tolerations | Node Affinity |
|---|---|---|
| Принцип | «Отталкивание» — узел отвергает поды | «Притяжение» — под ищет нужный узел |
| Точка конфигурации | Taint — на узле; Toleration — в поде | Affinity — в поде |
| Гарантия исключительности | Да: только поды с toleration попадут на tainted-узел | Нет: другие поды тоже могут попасть на этот узел |
| Сочетание | Используют вместе для точного управления | — |

**Таким образом:** чтобы гарантировать, что только memory-intensive Java-приложения попадут на выделенные узлы, нужны оба механизма: taint на узлах отгоняет чужие поды, а nodeAffinity в нужных подах «притягивает» их к этим узлам.

**Три эффекта taint подробнее**

`NoSchedule` — самый распространённый. Новые поды без соответствующего toleration не получат место на узле. Уже запущенные поды продолжают работать — это не ретроактивный эффект.

`PreferNoSchedule` — мягкий вариант. Планировщик использует его как штраф в функции оценки узла. Если других вариантов нет, под всё равно может попасть на узел.

`NoExecute` — самый строгий. Применяется Kubernetes автоматически при проблемах с узлом (taint `node.kubernetes.io/not-ready:NoExecute`, `node.kubernetes.io/unreachable:NoExecute`). Вытесняет уже запущенные поды. Параметр `tolerationSeconds` позволяет задержать вытеснение — полезно для graceful shutdown.

**Выделение узлов для memory-intensive Java-приложений**

Шаг 1: Пометить высокопамятные узлы taint-ом.

```bash
kubectl taint nodes high-mem-node-1 workload=memory-intensive:NoSchedule
kubectl taint nodes high-mem-node-2 workload=memory-intensive:NoSchedule
```

Шаг 2: Пометить узлы меткой для nodeAffinity.

```bash
kubectl label nodes high-mem-node-1 node-type=high-memory
kubectl label nodes high-mem-node-2 node-type=high-memory
```

Шаг 3: Настроить Deployment Java-приложения.

```yaml
spec:
  template:
    spec:
      # Toleration — позволяет под попасть на tainted-узел
      tolerations:
      - key: "workload"
        operator: "Equal"
        value: "memory-intensive"
        effect: "NoSchedule"
      # NodeAffinity — притягивает под к нужным узлам
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-type
                operator: In
                values:
                - high-memory
      containers:
      - name: java-app
        image: my-java-app:latest
        resources:
          requests:
            memory: 8Gi
            cpu: "2"
          limits:
            memory: 12Gi
            cpu: "4"
```

**Почему нужны оба механизма одновременно**

Только taint: под с toleration попадёт на узел, но и другие поды без явного запрета тоже могут туда попасть (если у них есть toleration). Только nodeAffinity: другие поды без affinity всё равно попадут на узел, если планировщику не хватает мест. Оба вместе: taint запрещает «чужих», affinity гарантирует, что «свои» попадут именно сюда.

**Встроенные taints Kubernetes**

Kubernetes автоматически добавляет taints на узлы при проблемах:
- `node.kubernetes.io/not-ready` — узел не готов (например, kubelet не отвечает).
- `node.kubernetes.io/disk-pressure` — нехватка дискового пространства.
- `node.kubernetes.io/memory-pressure` — нехватка памяти.

DaemonSet-поды (например, системные агенты мониторинга) автоматически получают tolerations для этих системных taint-ов, поэтому продолжают работать даже на деградированных узлах.

---

### Вопрос 55. Как устроено хранилище в Kubernetes? Объясните разницу между PersistentVolume, PersistentVolumeClaim и StorageClass. Как StatefulSet использует volumeClaimTemplates для обеспечения индивидуального хранилища каждой реплики (например, PostgreSQL с 3 репликами)?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Persistent Volumes — Kubernetes Documentation](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

**PersistentVolume (PV)** — ресурс кластера, представляющий физическое хранилище (NFS, iSCSI, облачный диск). Его жизненный цикл не зависит от жизненного цикла пода.

**PersistentVolumeClaim (PVC)** — запрос на хранилище от пользователя. PVC привязывается к PV в соотношении один к одному: PVC описывает требования (размер, режим доступа), PV — ресурс, им удовлетворяющий.

**Режимы доступа:**
- `ReadWriteOnce (RWO)` — монтируется как read-write на одном узле.
- `ReadOnlyMany (ROX)` — монтируется как read-only на нескольких узлах.
- `ReadWriteMany (RWX)` — монтируется как read-write на нескольких узлах.
- `ReadWriteOncePod (RWOP)` — монтируется только одним подом во всём кластере.

**volumeClaimTemplates в StatefulSet** автоматически создаёт PVC для каждой реплики:

```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes: [ "ReadWriteOnce" ]
    storageClassName: standard
    resources:
      requests:
        storage: 10Gi
```

#### Ответ от Claude

**Три уровня хранилища в Kubernetes**

```
StorageClass   →  задаёт «класс» хранилища и параметры динамического provisioning
PersistentVolume (PV)  →  реальный том (физический диск, облачный volume)
PersistentVolumeClaim (PVC)  →  запрос на хранилище от приложения
```

**PersistentVolume: что это**

PV — ресурс уровня кластера (не namespace). Создаётся администратором (статически) или автоматически при динамическом provisioning. Lifecycle PV не зависит от подов: даже после удаления пода данные на PV сохраняются (в зависимости от `persistentVolumeReclaimPolicy`):

- `Retain` — данные остаются, PV не освобождается автоматически.
- `Delete` — том удаляется вместе с PVC (поведение для облачных дисков).
- `Recycle` — устарело, не использовать.

**PersistentVolumeClaim: что это**

PVC — запрос на хранилище, аналог того, как Pod запрашивает CPU/memory. PVC описывает требования (размер, режим доступа, StorageClass), Kubernetes ищет подходящий PV и привязывает их. Связь один к одному: один PV может быть привязан только к одному PVC.

**StorageClass: динамический provisioning**

StorageClass позволяет автоматически создавать PV при появлении PVC, не требуя ручного создания томов администратором:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: pd.csi.storage.gke.io     # Cloud provisioner
parameters:
  type: pd-ssd
reclaimPolicy: Delete
allowVolumeExpansion: true
```

**volumeClaimTemplates в StatefulSet для PostgreSQL с 3 репликами**

StatefulSet создаёт PVC для каждой реплики по шаблону `<template-name>-<pod-name>`:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 50Gi
```

Kubernetes создаёт три PVC автоматически:

| Pod | PVC | Назначение |
|-----|-----|------------|
| `postgres-0` | `postgres-data-postgres-0` | Хранилище primary |
| `postgres-1` | `postgres-data-postgres-1` | Хранилище replica-1 |
| `postgres-2` | `postgres-data-postgres-2` | Хранилище replica-2 |

Каждый PVC монтируется только в «свой» под. При удалении пода `postgres-1` Kubernetes пересоздаёт его и присоединяет тот же PVC — данные сохраняются. При удалении StatefulSet PVC **не удаляются** автоматически (защита данных); их нужно удалить явно.

**Ключевые отличия от обычного Deployment**

В Deployment все реплики используют одну и ту же PVC (при ReadWriteMany) или вообще не имеют персистентного хранилища (ReadWriteOnce не позволяет монтировать один том на несколько подов разных узлов). StatefulSet с volumeClaimTemplates — единственный нативный способ дать каждой реплике своё независимое хранилище.

---

### Вопрос 56. Как настроить graceful shutdown Java Spring Boot приложения в Kubernetes? Какую роль играют preStop-хук, terminationGracePeriodSeconds и механизм graceful shutdown в Spring Boot 2.3+, и почему без preStop-хука возможны ошибки 502 при выкате новой версии?

**Категория:** Контейнеры/DevOps · **Уровень:** Middle

#### Оригинальный ответ из интернета
> Источник: [Container Lifecycle Hooks — Kubernetes Documentation](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)

Kubernetes предоставляет два хука жизненного цикла контейнера:

- **postStart** — выполняется сразу после создания контейнера, до перехода в состояние Running.
- **preStop** — вызывается непосредственно перед завершением контейнера; SIGTERM отправляется только после завершения preStop.

**terminationGracePeriodSeconds** (по умолчанию 30 секунд) — период ожидания с момента запроса на завершение до отправки SIGKILL. Таймер начинается **до** выполнения preStop-хука, то есть время preStop + время завершения приложения не должно превышать `terminationGracePeriodSeconds`.

**Типы обработчиков хуков:**
- `exec` — выполнить команду внутри контейнера.
- `httpGet` — выполнить HTTP-запрос к контейнеру.
- `sleep` — пауза заданной длительности.

**Гарантия доставки:** at-least-once (хук может быть вызван несколько раз при перезапуске kubelet).

#### Ответ от Claude

**Почему без preStop-хука возникают 502 при rolling update**

Последовательность событий при замене пода Kubernetes:

1. Kubernetes отправляет сигнал удаления пода.
2. Одновременно (параллельно!) происходят два события:
   - Pod получает SIGTERM и начинает завершение.
   - kube-proxy и Endpoints-контроллер начинают удалять IP пода из EndpointSlice.
3. Обновление EndpointSlice на всех узлах — асинхронный процесс, занимающий 2–5 секунд.
4. В этот промежуток load balancer ещё может направлять новые запросы к поду, который уже получил SIGTERM и прекратил принимать соединения.

**Результат:** клиент получает 502 или connection reset, потому что pod уже «мёртв» с точки зрения приложения, но ещё «жив» с точки зрения сетевой маршрутизации.

**Решение: preStop-хук с паузой**

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
  - name: java-app
    image: my-spring-boot-app:latest
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 10"]
    env:
    - name: SERVER_SHUTDOWN
      value: "graceful"
```

Пауза в `preStop` даёт kube-proxy время обновить правила маршрутизации до того, как контейнер начнёт отказывать в соединениях.

**Spring Boot Graceful Shutdown (с версии 2.3)**

Spring Boot 2.3+ поддерживает встроенный graceful shutdown:

```yaml
# application.yml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

При включённом graceful shutdown:
1. Spring Boot перестаёт принимать новые HTTP-запросы.
2. Ждёт завершения in-flight запросов (не более `timeout-per-shutdown-phase`).
3. Закрывает ApplicationContext: останавливает @Scheduled задачи, закрывает DataSource, consumer'ы очередей.
4. JVM завершается с кодом 0.

**Полная конфигурация graceful shutdown для production**

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 75   # > preStop(10) + Spring shutdown(30) + буфер(35)
      containers:
      - name: java-app
        lifecycle:
          preStop:
            exec:
              command: ["sh", "-c", "sleep 10"]
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 20
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

**Actuator и Kubernetes Probes**

Spring Boot Actuator (с 2.3) интегрируется с Kubernetes-пробами через отдельные health indicators:

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
  health:
    livenessState:
      enabled: true
    readinessState:
      enabled: true
```

При graceful shutdown приложение переводит readiness probe в состояние DOWN — Kubernetes видит это и перестаёт направлять трафик ещё до SIGTERM. Это более чистый подход, чем sleep в preStop, но требует, чтобы readiness probe успела сообщить DOWN до окончания endpoint propagation.

**Итог: рекомендуемая комбинация**

1. `server.shutdown: graceful` + `spring.lifecycle.timeout-per-shutdown-phase: 30s` — Spring Boot завершает in-flight запросы.
2. `preStop: sleep 10` — пауза для распространения endpoint deletion по всем узлам.
3. `terminationGracePeriodSeconds: 60` — достаточный общий бюджет времени.
4. Readiness probe на `/actuator/health/readiness` — ранний сигнал о деградации.

---

### Вопрос 57. Что такое securityContext в Kubernetes? Как правильно настроить его для Java-приложений, чтобы выполнить требования безопасности: запуск от непривилегированного пользователя, запрет на повышение привилегий, файловая система только для чтения?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Configure a Security Context for a Pod or Container — Kubernetes Documentation](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

`securityContext` определяет настройки привилегий и управления доступом для Pod или Container.

**Основные поля контейнерного securityContext:**

- `runAsUser` — UID процесса внутри контейнера.
- `runAsNonRoot` — если `true`, admission controller отклонит контейнер с UID 0.
- `allowPrivilegeEscalation` — контролирует флаг ядра `no_new_privs`; по умолчанию `true`.
- `readOnlyRootFilesystem` — монтирует корневую ФС контейнера как read-only.
- `capabilities` — управление Linux capabilities: `drop: ["ALL"]` убирает все, `add` добавляет конкретные.

**Разница между Pod-level и Container-level:**

Pod-level `securityContext` (в `spec.securityContext`) применяется ко всем контейнерам:
- `runAsUser`, `runAsGroup`, `runAsNonRoot`
- `fsGroup` — GID, под которым монтируются тома (важно для файловых разрешений)
- `supplementalGroups`

Container-level переопределяет Pod-level для конкретного контейнера и добавляет:
- `allowPrivilegeEscalation`
- `readOnlyRootFilesystem`
- `capabilities`

#### Ответ от Claude

**Зачем securityContext для Java-приложений**

По умолчанию Docker-контейнер запускается от root (UID 0). В Kubernetes это означает, что скомпрометированный контейнер потенциально может:
- Читать секреты, смонтированные в других подах на том же узле (через /proc или hostPath).
- Эксплуатировать уязвимости ядра, требующие привилегированного процесса.
- Записывать данные в корневую ФС образа.

**Полная конфигурация securityContext для Java-сервиса**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-secure-app
spec:
  template:
    spec:
      # Pod-level: применяется ко всем контейнерам
      securityContext:
        runAsNonRoot: true        # Запрет запуска от root
        runAsUser: 1000           # UID пользователя приложения
        runAsGroup: 1000          # Основная GID
        fsGroup: 1000             # GID для монтируемых томов
        seccompProfile:
          type: RuntimeDefault    # Ограничение syscalls через seccomp
      containers:
      - name: java-app
        image: my-java-app:latest
        # Container-level: дополняет и переопределяет Pod-level
        securityContext:
          allowPrivilegeEscalation: false   # Запрет повышения привилегий
          readOnlyRootFilesystem: true      # Корневая ФС только для чтения
          capabilities:
            drop:
              - ALL                         # Убираем все Linux capabilities
            # add: NET_BIND_SERVICE         # Добавить если нужен порт < 1024
        volumeMounts:
        # Если нужны writable директории — через emptyDir или PVC
        - name: tmp-dir
          mountPath: /tmp
        - name: logs-dir
          mountPath: /app/logs
      volumes:
      - name: tmp-dir
        emptyDir: {}
      - name: logs-dir
        emptyDir: {}
```

**Как подготовить Dockerfile к non-root**

```dockerfile
FROM eclipse-temurin:21-jre-alpine

# Создаём non-root пользователя
RUN addgroup -S javaapp && adduser -S javaapp -G javaapp -u 1000

# Создаём директории с правами пользователя
RUN mkdir -p /app && chown javaapp:javaapp /app

USER javaapp:javaapp
WORKDIR /app

COPY --chown=javaapp:javaapp target/app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Типичные проблемы при переходе на non-root у Java-приложений**

1. **Порты < 1024.** Непривилегированный процесс не может слушать порты < 1024 по умолчанию. Решение: использовать порт 8080+ (рекомендуется), или добавить capability `NET_BIND_SERVICE`.

2. **readOnlyRootFilesystem + Spring Boot.** Spring Boot создаёт временные файлы в `/tmp`. При `readOnlyRootFilesystem: true` нужно смонтировать `/tmp` как `emptyDir`. Аналогично для логов в `/app/logs`.

3. **fsGroup и volume permissions.** `fsGroup: 1000` гарантирует, что все файлы в примонтированных PVC будут доступны GID 1000. Без этого Java-приложение может не иметь права на чтение/запись volume.

4. **Distroless-образы.** В distroless-образах (`gcr.io/distroless/java21`) нет shell и системных утилит. `allowPrivilegeEscalation: false` и `readOnlyRootFilesystem: true` работают нативно, но отладка усложняется (использовать `:debug` варианты).

**seccompProfile**

`RuntimeDefault` — профиль seccomp по умолчанию, ограничивающий список доступных системных вызовов. JVM (HotSpot) работает корректно с RuntimeDefault. Более строгий профиль `Localhost` требует ручного написания политики.

**Расхождения между источниками:** Официальная документация Kubernetes описывает поля securityContext и их значения. CIS Kubernetes Benchmark v1.9 и NIST SP 800-190 рекомендуют `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `drop: ALL` как обязательный базовый уровень. Dynatrace и Wiz добавляют `readOnlyRootFilesystem: true` и `seccompProfile: RuntimeDefault` в рекомендуемый минимум, но эти поля не являются обязательными в стандартном Kubernetes API.

---

### Вопрос 58. Что такое pod affinity и pod anti-affinity в Kubernetes? Чем topologySpreadConstraints предпочтительнее pod anti-affinity для равномерного распределения Java-реплик по зонам доступности? Как написать конфигурацию, обеспечивающую распределение 6 реплик по трём AZ?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Assigning Pods to Nodes — Kubernetes Documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)

**Pod affinity** позволяет указать, что под должен быть размещён рядом с другими подами (co-located on the same node or topology domain).

**Pod anti-affinity** — противоположное: под не должен попасть на тот же узел или в ту же топологическую зону, что и другие поды с заданными метками.

Оба правила имеют два варианта жёсткости:
- `requiredDuringSchedulingIgnoredDuringExecution` — жёсткое ограничение: если нет подходящего узла, под не будет запланирован.
- `preferredDuringSchedulingIgnoredDuringExecution` — мягкое предпочтение: планировщик постарается соблюсти, но не гарантирует. Поддерживает `weight` (1–100) для приоритизации.

Суффикс `IgnoredDuringExecution` означает: если метки изменятся после планирования, уже запущенные поды не вытесняются.

#### Ответ от Claude

**Pod Affinity vs Pod Anti-Affinity**

Оба механизма оперируют метками **других подов** (а не узлов). Планировщик вычисляет топологическую зону (например, `topology.kubernetes.io/zone`) узла, на котором уже запущены целевые поды, и применяет правила к этой зоне.

**Pod Anti-Affinity: ограничения**

Классический подход для «не более одной реплики на узел»:

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: java-service
      topologyKey: "kubernetes.io/hostname"
```

Проблемы:
- **Бинарность:** либо «ни одного рядом», либо нет ограничений. Нельзя сказать «не более 2 реплик на зону».
- **Непредсказуемость при масштабировании.** Если реплик больше, чем узлов — под не запланируется вообще (при `required`).
- **Не учитывает неравномерность узлов по зонам.** В зоне A может быть 4 узла, в зоне B — 2: anti-affinity не сбалансирует количество реплик между зонами.

**TopologySpreadConstraints: более гибкий подход**

Доступен с Kubernetes v1.19 (GA). Позволяет указать максимальный «перекос» (skew) между топологическими доменами:

```yaml
topologySpreadConstraints:
- maxSkew: 1                              # Разница между макс. и мин. репликами в зоне ≤ 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule        # Жёсткое ограничение
  labelSelector:
    matchLabels:
      app: java-service
```

`maxSkew: 1` при 6 репликах в 3 зонах: каждая зона получит ровно 2 реплики (перекос = 0 ≤ 1). При добавлении 7-й реплики одна зона получит 3 (перекос = 1 ≤ 1) — всё ещё удовлетворяет ограничению.

**Полная конфигурация: 6 реплик Java-сервиса по 3 AZ**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-service
spec:
  replicas: 6
  selector:
    matchLabels:
      app: java-service
  template:
    metadata:
      labels:
        app: java-service
    spec:
      # Равномерно по зонам доступности
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: java-service
      # Дополнительно: не более 1 реплики на конкретный узел
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway  # Мягкое ограничение на уровне нод
        labelSelector:
          matchLabels:
            app: java-service
      containers:
      - name: java-app
        image: my-java-service:latest
```

**Два значения `whenUnsatisfiable`**

| Значение | Поведение |
|----------|-----------|
| `DoNotSchedule` | Жёсткое: если ограничение нарушается — под не планируется |
| `ScheduleAnyway` | Мягкое: планировщик старается минимизировать skew, но разместит под даже при нарушении |

**Сравнение подходов**

| Критерий | Pod Anti-Affinity | TopologySpreadConstraints |
|----------|-------------------|--------------------------|
| Гранулярность | Бинарно (да/нет на узел/зону) | Задаётся maxSkew (числовой порог) |
| Контроль количества реплик на домен | Нет | Да |
| Поведение при масштабировании | Может заблокировать scheduling | Гибко: `ScheduleAnyway` не блокирует |
| Кол-во правил | Одно | Несколько (AND-семантика) |
| Рекомендация Kubernetes | Для конкретных исключений | Предпочтительно для балансировки |

Официальная документация Kubernetes рекомендует использовать `topologySpreadConstraints` как основной инструмент для балансировки реплик, а `podAntiAffinity` оставить для специфических требований (например, «primary и replica не должны быть на одном узле»).

---

### Вопрос 59. Что такое service mesh (на примере Istio)? Как работает автоматическая инъекция sidecar-прокси (Envoy), что такое mutual TLS (mTLS) между сервисами, и какие возможности даёт service mesh Java-микросервисам без изменения кода приложения?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Service Mesh Architecture with Istio — Baeldung](https://www.baeldung.com/ops/istio-service-mesh)

Istio — реализация service mesh, которая «прозрачно накладывается на распределённое приложение» для управления коммуникацией между сервисами. Вместо встраивания логики коммуникации в каждый микросервис Istio предоставляет инфраструктурный уровень управления через сетевые прокси.

**Sidecar injection:** При включении автоматической инъекции (`kubectl label namespace default istio-injection=enabled`) Istio автоматически добавляет прокси Envoy в каждый новый под. Эти прокси перехватывают весь трафик между сервисами, формируя «плоскость данных» (data plane). Компонент `istiod` формирует «плоскость управления» (control plane) и выполняет функции service discovery, управления конфигурацией и certificate management.

**mTLS:** `istiod` выступает в роли Certificate Authority (CA) и генерирует сертификаты для взаимной TLS-аутентификации между сервисами. Это гарантирует зашифрованную и аутентифицированную коммуникацию «из коробки».

**Traffic management** через два ресурса:
- `VirtualService` — определяет правила маршрутизации (куда направлять запрос).
- `DestinationRule` — управляет параметрами соединения с конкретным сервисом (балансировка, circuit breaker).

#### Ответ от Claude

**Что такое service mesh и зачем он нужен**

По мере роста числа Java-микросервисов появляются сквозные задачи: шифрование трафика, аутентификация между сервисами, трассировка запросов, circuit breaker, retry-логика. Без service mesh каждый сервис реализует это самостоятельно (через библиотеки: Resilience4j, Spring Cloud). Service mesh выносит эту логику на уровень инфраструктуры — приложение не меняется.

**Архитектура Istio**

```
Control Plane:  istiod (Pilot + Citadel + Galley → объединены с v1.5)
                  ↓  конфигурация  ↓  сертификаты
Data Plane:     [Envoy sidecar] ←→ [Envoy sidecar]
                [Java Pod A]         [Java Pod B]
```

- **istiod** — единый бинарник control plane. Управляет конфигурацией Envoy-прокси, является CA для выдачи сертификатов mTLS.
- **Envoy** — высокопроизводительный L7-прокси (на C++). Каждый под получает свой экземпляр в качестве sidecar. Перехватывает весь входящий и исходящий трафик через iptables-правила (IP tables intercept).

**Как работает автоматическая инъекция sidecar**

```bash
# Включение auto-injection для namespace
kubectl label namespace java-services istio-injection=enabled
```

После этого Kubernetes Admission Webhook Istio автоматически модифицирует каждый новый Pod: добавляет init-контейнер (настраивает iptables для перехвата трафика) и контейнер `istio-proxy` (Envoy). Java-приложение не знает о существовании прокси — с его точки зрения оно обращается напрямую к другому сервису.

**Mutual TLS (mTLS)**

В обычном TLS только клиент проверяет сервер. mTLS — взаимная аутентификация: оба участника предъявляют сертификаты.

Istio реализует это автоматически:
1. `istiod` выдаёт каждому sidecar-прокси сертификат SPIFFE (формат `spiffe://cluster.local/ns/<namespace>/sa/<serviceaccount>`).
2. Envoy-прокси Pod A использует свой сертификат при соединении с Envoy-прокси Pod B.
3. Оба прокси проверяют цепочку сертификатов через общий CA (`istiod`).

Режимы mTLS в Istio:
- `PERMISSIVE` — принимает и plain-text, и mTLS (для постепенной миграции).
- `STRICT` — только mTLS; plain-text запросы отклоняются.

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: java-services
spec:
  mtls:
    mode: STRICT
```

**Возможности без изменения кода Java-приложения**

| Возможность | Как реализована в Istio |
|-------------|------------------------|
| Шифрование трафика | mTLS между всеми sidecar-прокси |
| Circuit breaker | `DestinationRule.trafficPolicy.outlierDetection` |
| Retry логика | `VirtualService.http.retries` |
| Timeout | `VirtualService.http.timeout` |
| Canary / weighted routing | `VirtualService` с `weight` для разных `DestinationRule` subsets |
| Трассировка (Jaeger/Zipkin) | Envoy автоматически генерирует trace spans |
| Метрики (Prometheus) | Envoy экспортирует `istio_requests_total`, latency гистограммы |
| Авторизация на уровне сервисов | `AuthorizationPolicy` — RBAC для service-to-service |

**Пример: canary deployment через VirtualService**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: java-service
spec:
  hosts:
  - java-service
  http:
  - route:
    - destination:
        host: java-service
        subset: v1
      weight: 90
    - destination:
        host: java-service
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: java-service
spec:
  host: java-service
  subsets:
  - name: v1
    labels:
      version: "1.0"
  - name: v2
    labels:
      version: "2.0"
```

Это позволяет направлять 10% трафика на новую версию с гарантиями точного процентного разбиения — чего невозможно достичь нативными Kubernetes Service (только через число реплик).

**Расхождения между источниками:** Официальная документация Istio (istio.io) и Baeldung согласуются в описании архитектуры. Документация CNCF добавляет, что Istio — graduated проект с 2023 года. Альтернативой является Linkerd (более лёгкий, на Rust), Cilium Service Mesh (на eBPF без sidecar) — выбор зависит от требований к производительности и операционной сложности.

---

### Вопрос 60. Что такое Kubernetes Operator и Custom Resource Definition (CRD)? Как operator-паттерн работает через control loop (reconciliation), и для каких задач Java-команды создают собственные операторы (на примере Java Operator SDK)?

**Категория:** Контейнеры/DevOps · **Уровень:** Senior

#### Оригинальный ответ из интернета
> Источник: [Custom Resources — Kubernetes Documentation](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)

**Custom Resource (CR)** — расширение Kubernetes API, позволяющее хранить структурированные данные в кластере. Custom Resource Definition (CRD) — объект, описывающий схему и область видимости (namespace или кластер) CR.

Создание CRD само по себе не производит никаких действий — Kubernetes рассматривает CR как обычное хранилище данных. Для реакции на CR необходим контроллер (controller), реализующий бизнес-логику.

**Паттерн Operator** = Custom Resource + Controller, управляющий этим ресурсом. Оператор наблюдает за изменениями CR и предпринимает действия для достижения желаемого состояния (desired state), описанного в CR.

#### Ответ от Claude

**Что такое CRD и Custom Resource**

Kubernetes уже содержит встроенные ресурсы: Deployment, Service, ConfigMap, Pod и т.д. CRD позволяет добавить собственные типы ресурсов, которые становятся полноценными гражданами Kubernetes API — их можно создавать через `kubectl apply`, смотреть через `kubectl get`, они хранятся в etcd и поддерживают namespace/cluster scope.

```yaml
# Пример CRD для кастомного ресурса JavaApplication
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: javaapplications.mycompany.io
spec:
  group: mycompany.io
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              image:
                type: string
              replicas:
                type: integer
              jvmArgs:
                type: string
  scope: Namespaced
  names:
    plural: javaapplications
    singular: javaapplication
    kind: JavaApplication
```

После регистрации CRD можно создать экземпляр:

```yaml
apiVersion: mycompany.io/v1
kind: JavaApplication
metadata:
  name: order-service
spec:
  image: order-service:2.1.0
  replicas: 3
  jvmArgs: "-Xmx512m -XX:+UseG1GC"
```

**Control Loop (Reconciliation Loop)**

Оператор реализует паттерн «observe → diff → act»:

1. **Watch** — оператор подписывается на события изменений CR (создание, обновление, удаление) через Kubernetes Watch API.
2. **Compare** — Reconciler сравнивает желаемое состояние (spec CR) с реальным состоянием (что есть в кластере).
3. **Act** — если есть расхождения, оператор выполняет действия: создаёт/обновляет/удаляет зависимые ресурсы (Deployment, Service и т.д.).
4. **Update status** — обновляет `.status` CR с информацией о текущем состоянии.

Цикл выполняется постоянно — это гарантирует, что реальное состояние кластера всегда стремится к желаемому.

**Java Operator SDK**

Java Operator SDK (JOSDK) — CNCF-проект, позволяющий писать операторы на Java без изучения Go:

```java
@ControllerConfiguration
public class JavaApplicationReconciler
    implements Reconciler<JavaApplication> {

  private final KubernetesClient client;

  @Override
  public UpdateControl<JavaApplication> reconcile(
      JavaApplication resource,
      Context<JavaApplication> context) {

    // Желаемый Deployment из spec CR
    Deployment desired = createDeployment(resource);

    // Применяем или обновляем Deployment
    client.apps().deployments()
        .inNamespace(resource.getMetadata().getNamespace())
        .createOrReplace(desired);

    // Обновляем status
    resource.setStatus(new JavaApplicationStatus("Running"));
    return UpdateControl.updateStatus(resource);
  }

  private Deployment createDeployment(JavaApplication app) {
    return new DeploymentBuilder()
        .withNewMetadata()
          .withName(app.getMetadata().getName())
        .endMetadata()
        .withNewSpec()
          .withReplicas(app.getSpec().getReplicas())
          .withNewTemplate()
            .withNewSpec()
              .addNewContainer()
                .withImage(app.getSpec().getImage())
                .addNewEnv()
                  .withName("JAVA_OPTS")
                  .withValue(app.getSpec().getJvmArgs())
                .endEnv()
              .endContainer()
            .endSpec()
          .endTemplate()
        .endSpec()
        .build();
  }
}
```

**Для каких задач Java-команды создают операторы**

| Задача | Что делает оператор |
|--------|---------------------|
| Управление жизненным циклом Kafka-топиков | CR `KafkaTopic` → оператор создаёт топик через Admin API Kafka |
| Database provisioning | CR `PostgresDatabase` → оператор создаёт БД, пользователя, права и Secret с credentials |
| Blue-green deployment | CR `BlueGreenDeployment` → оператор управляет двумя Deployment и переключает Service |
| Управление сертификатами | Cert-manager оперирует CR `Certificate` и автоматически обновляет TLS-секреты |
| Самовосстановление кластера БД | Operator PostgreSQL (Zalando/CNPG) следит за репликацией, выполняет failover при падении primary |

**Отличие оператора от Helm-чарта**

Helm — инструмент для первоначального деплоя шаблонизированных манифестов. Оператор — постоянно работающий контроллер, реагирующий на события и поддерживающий желаемое состояние. Helm не умеет реагировать на «первичный упал — нужно переизбрать primary» или «объём заканчивается — нужно расширить PVC». Оператор — умеет.

**Расхождения между источниками:** Официальная документация Kubernetes (kubernetes.io/docs/concepts/extend-kubernetes) описывает CRD и controller без привязки к языку. Baeldung (baeldung.com/java-kubernetes-operator-sdk) и Red Hat Developer (developers.redhat.com) детально описывают Java Operator SDK и его интеграцию с Quarkus. Источники согласуются в описании reconciliation loop; различаются только в деталях реализации на конкретных фреймворках (JOSDK vs Operator SDK для Go vs Kopf для Python).

---
