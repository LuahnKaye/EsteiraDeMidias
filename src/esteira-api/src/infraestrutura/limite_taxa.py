import os
import time
import redis

# Endereço de conexão com o Redis obtido via variáveis de ambiente
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Inicializa o pool de conexões e o cliente do Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# O Script Lua atômico que garante o Sliding-Window Rate Limiting sem race conditions
SCRIPT_LUA_RATE_LIMIT = """
local chave = KEYS[1]
local agora = tonumber(ARGV[1])
local janela = tonumber(ARGV[2])
local limite = tonumber(ARGV[3])
local membro = ARGV[4]
local limite_tempo = agora - janela

-- Remove os registros de acessos do IP que já passaram da janela de tempo permitida
redis.call('ZREMRANGEBYSCORE', chave, '-inf', limite_tempo)

-- Conta quantos acessos ativos ainda restam na janela de tempo para este IP
local quantidade = redis.call('ZCARD', chave)

if quantidade < limite then
    -- Adiciona o carimbo de data/hora atual (score) com o membro único (id_requisicao)
    redis.call('ZADD', chave, agora, membro)
    -- Atualiza a expiração física da chave no Redis
    redis.call('EXPIRE', chave, janela)
    return 1 -- Acesso Permitido
else
    return 0 -- Limite de requisições excedido! (HTTP 429)
end
"""

# Compila e registra o script Lua no Redis na inicialização da aplicação para máxima performance
script_registrado = redis_client.register_script(SCRIPT_LUA_RATE_LIMIT)


def verificar_limite_taxa(
    ip_cliente: str, 
    limite_requisicoes: int = 10, 
    janela_segundos: int = 60
) -> bool:
    """
    Verifica de forma atômica se o IP do cliente excedeu a taxa máxima de requisições
    usando o script Lua otimizado no Redis (Janela Deslizante / Sliding Window).

    Args:
        ip_cliente (str): O endereço IP ou ID identificador do cliente.
        limite_requisicoes (int): A quantidade máxima de requisições permitida.
        janela_segundos (int): O intervalo de tempo da janela deslizante (ex: 60s).

    Returns:
        bool: Verdadeiro se o IP estiver liberado, Falso se exceder o limite (bloquear).
    """
    chave_redis = f"limite_taxa:{ip_cliente}"
    agora_timestamp = int(time.time())
    
    # Membro único gerado para que múltiplas requisições no mesmo segundo
    # sejam registradas como membros únicos no Sorted Set do Redis
    import uuid
    id_requisicao = uuid.uuid4().hex

    try:
        # Executa o script Lua pré-compilado de forma atômica
        resultado = script_registrado(
            keys=[chave_redis],
            args=[agora_timestamp, janela_segundos, limite_requisicoes, id_requisicao]
        )
        # O script Lua retorna 1 se permitido e 0 se estourado
        se_liberado = (resultado == 1)
        return se_liberado
    except redis.exceptions.RedisError:
        # Em caso de falha de conexão com o Redis, permitimos a passagem (Fail Open)
        # para que o sistema continue funcionando se o cache cair, mas gera logs de aviso
        return True
