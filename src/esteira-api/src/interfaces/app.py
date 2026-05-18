import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from src.infraestrutura.banco import inicializar_banco
from src.interfaces.rotas_midia import roteador

app = FastAPI(
    title="Esteira de Mídias API",
    description="API Principal de gerenciamento reativo e assíncrono de otimização de imagens lojistas",
    version="1.0.0"
)

# ----------------- TELEMETRIA & MÉTRICAS (PROMETHEUS) -----------------
# 1. Contador global de requisições por endpoint e status HTTP
CONTADOR_REQUISICOES = Counter(
    "esteira_requisicoes_total",
    "Quantidade total de chamadas recebidas na API",
    ["metodo", "endpoint", "status"]
)

# 2. Histograma do tempo médio de resposta de processamento HTTP
HISTOGRAMA_LATENCIA = Histogram(
    "esteira_latencia_requisicoes_segundos",
    "Tempo de resposta das chamadas HTTP na API em segundos",
    ["metodo", "endpoint"]
)


@app.middleware("http")
async def interceptador_telemetria(request: Request, call_next):
    """
    Middleware global que intercepta chamadas HTTP, calcula o tempo de resposta
    e popula as métricas do Prometheus para observabilidade em produção.
    """
    # Evita medir o próprio endpoint de telemetria para não poluir os dados
    if request.url.path == "/metricas":
        return await call_next(request)

    inicio_tempo = time.time()
    
    response = await call_next(request)
    
    tempo_duracao = time.time() - inicio_tempo

    # Coleta as variáveis de label em português do Brasil
    metodo = request.method
    endpoint = request.url.path
    status_codigo = str(response.status_code)

    # Popula as métricas nos coletores do Prometheus
    CONTADOR_REQUISICOES.labels(metodo=metodo, endpoint=endpoint, status=status_codigo).inc()
    HISTOGRAMA_LATENCIA.labels(metodo=metodo, endpoint=endpoint).observe(tempo_duracao)

    return response


# Rota oficial de raspagem (scraping) do Prometheus
@app.get("/metricas", summary="Expõe as métricas de telemetria no formato Prometheus")
async def obter_metricas_prometheus():
    """
    Endpoint público consumido pelo servidor do Prometheus a cada 15s.
    Coleta o estado atual das variáveis do sistema e retorna em formato texto nativo.
    """
    dados_metricas = generate_latest()
    return Response(content=dados_metricas, media_type=CONTENT_TYPE_LATEST)


# ----------------- EVENTOS DE INICIALIZAÇÃO -----------------
@app.on_event("startup")
def evento_startup():
    """
    Ação disparada imediatamente na inicialização da aplicação pelo Uvicorn.
    Garante a integridade do banco relacional criando tabelas e índices se necessário.
    """
    inicializar_banco()


# ----------------- MIDDLEWARES E ROTAS -----------------
# Configuração de políticas de CORS para permitir acesso seguro do painel administrativo (UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para o domínio oficial da UI (magalu)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Acopla o grupo de rotas das mídias na árvore da aplicação
app.include_router(roteador)
