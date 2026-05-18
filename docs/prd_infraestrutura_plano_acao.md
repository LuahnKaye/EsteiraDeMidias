# Documento de Requisitos do Produto (PRD) - Infraestrutura, Observabilidade e Planos de Ação

Este documento estabelece a estratégia de orquestração de containers, o pipeline de entrega contínua (CI/CD), a modelagem de observabilidade e as etapas do cronograma de desenvolvimento para o ecossistema **Esteira de Mídias**.

---

## 1. Orquestração de Infraestrutura Local (Docker Compose)

Para garantir o requisito de "custo zero" e facilidade de deploy em ambientes de desenvolvimento, o projeto utilizará um arquivo `docker-compose.yml` unificado na raiz do repositório. O ecossistema completo poderá ser iniciado com um único comando:

```bash
docker-compose up --build
```

### Serviços Orquestrados e Mapeamento de Portas:

*   `esteira-api`: O container do backend desenvolvido em FastAPI (Porta `8000`).
*   `esteira-worker`: O microsserviço de processamento reativo de imagens Python (executa de forma assíncrona em background).
*   `esteira-ui`: O frontend administrativo em React/Next.js (Porta `3000`).
*   `postgres-db`: Banco de dados relacional PostgreSQL (Porta `5432`) para persistência dos trabalhos da esteira.
*   `redis-cache`: Armazenamento rápido em memória para cache de *Rate Limit* (Porta `6379`).
*   `rabbitmq-broker`: O gerenciador de filas e mensageria (Porta `5672` para conexões internas e `15672` para o painel de gerenciamento Web).
*   `prometheus`: Servidor de monitoramento e telemetria por raspagem de dados (Porta `9090`).
*   `grafana`: Painel visual para exibição das métricas (Porta `3001` - configurado para evitar colisão com o frontend).

---

## 2. Escalonamento em Produção (Diretório `/k8s`)

Embora a aplicação seja desenhada para fácil execução local, o repositório incluirá uma pasta estruturada `/k8s` contendo todos os manifestos de implantação em nuvem pública (compatível com Magalu Cloud):

> [!IMPORTANT]
> *   `deployment.yaml`: Configuração técnica de implantação dos Pods do FastAPI e do Processador de Mídias (Esteira Worker), aplicando regras rígidas de segurança por limite de recursos (`Requests` e `Limits` de CPU/Memória) para evitar gargalos e contenção.
> *   `service.yaml`: Exposição de portas internas entre os microsserviços via `ClusterIP` e acesso externo via balanceador de carga (`LoadBalancer`).
> *   `hpa.yaml` (**Horizontal Pod Autoscaler**): Configurações para escalonamento elástico. O Kubernetes aumentará automaticamente o número de instâncias do `esteira-worker` caso a utilização agregada de CPU ultrapasse **70%** (ideal para Black Friday).
> *   `configmap.yaml` e `secrets.yaml`: Centralização de variáveis globais de ambiente e credenciais criptografadas de banco de dados.

---

## 3. Esteira de Integração e Entrega Contínua (CI/CD)

Criaremos uma automação via **GitHub Actions** (`.github/workflows/ci.yml`) que será disparada a cada *Pull Request* ou *Push* direcionado à ramificação `main`.

A esteira executará sequencialmente as seguintes validações:

```mermaid
graph LR
    Push["[Push / PR]"] --> Lint["[Linting: Ruff / Flake8]"]
    Lint --> TestUnit["[Testes Unitários: Pytest]"]
    TestUnit --> TestIntegration["[Testes de Integração]"]
    TestIntegration --> BuildCheck["[Build Check: Docker]"]
    BuildCheck --> Success["Merge Liberado ✅"]
```

> [!WARNING]
> **Política de Bloqueio Rígida**
> Se o código quebrar alguma regra estilística de linting ou falhar em pelo menos um dos testes automatizados, o GitHub Actions impedirá o *merge*. Isso garante a integridade do código em produção.

---

## 4. Observabilidade, Métricas e Alertas

Para garantir os padrões corporativos de telemetria exigidos:

```mermaid
graph TD
    APICore["API Principal (FastAPI)"] -->|Métricas em /metricas| Prometheus["Prometheus Server"]
    RabbitMQ["RabbitMQ Broker"] -->|Status da Fila| Prometheus
    Prometheus -->|Raspagem (Scraping)| Grafana["Grafana Dashboards"]
    Grafana -->|Visualização de Saúde| Devops["Dashboard de Operações"]
```

*   **API Principal:** Exportará métricas de performance no padrão nativo do Prometheus através do endpoint `/metricas`.
*   **Prometheus:** Realizará a coleta periódica por raspagem (*scraping*) de dados e monitorará o consumo de hardware da API e da fila.
*   **Grafana:** Consumirá a base temporal do Prometheus e renderizará um dashboard de monitoramento em tempo real incluindo:
    *   Taxa agregada de requisições por segundo (RPS).
    *   Tempo médio de resposta no processamento das mídias.
    *   Quantidade de mensagens ativas e pendentes na fila do RabbitMQ.
    *   Frequência de erros HTTP `4xx` e `5xx`.

---

## 5. Cronograma de Execução (Fases de Desenvolvimento)

Para simular o andamento de projetos reais sob metodologias ágeis, a construção do ecossistema será realizada em 5 sprints estruturadas:

| Fase | Foco Principal | Entregáveis Técnicos |
| :--- | :--- | :--- |
| **Fase 1** | **Infraestrutura Base** | Configuração inicial do repositório, escrita e testes do `docker-compose.yml` contendo os containers do PostgreSQL, Redis e RabbitMQ funcionando integrados. |
| **Fase 2** | **Core API & Segurança** | Desenvolvimento dos endpoints da API FastAPI, implementação da validação por *Magic Bytes* (segurança física), controle de *Rate Limit* com Redis e persistência relacional básica (trabalhos e logs). |
| **Fase 3** | **Mensageria & Worker** | Criação do microsserviço de processamento em segundo plano, acoplamento da biblioteca Pillow para otimização de imagens, conversão em WebP e conexões de escrita e leitura no RabbitMQ. |
| **Fase 4** | **Observabilidade & Testes** | Montagem da suíte completa de testes unitários e de integração utilizando Pytest (cobertura mínima de **80%**), setup dos painéis do Prometheus/Grafana e escrita das pipelines de CI/CD. |
| **Fase 5** | **Frontend & Documentação** | Construção da interface Drag-and-Drop, lógica reativa de Polling resiliente, redação dos manifestos Kubernetes (`/k8s`) e escrita de um README de impacto profissional. |
