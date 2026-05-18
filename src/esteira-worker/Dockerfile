# ==========================================
# Estágio 1: Compilação e Preparação (Build)
# ==========================================
FROM python:3.10-alpine AS construtor

WORKDIR /app

# Instala ferramentas necessárias para compilação das bibliotecas C (Pillow e PostgreSQL driver)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    libwebp-dev

COPY requirements.txt .

# Compila e instala as dependências Python de forma isolada
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# Estágio 2: Ambiente de Execução (Runtime)
# ==========================================
FROM python:3.10-alpine

WORKDIR /app

# Instala as dependências compartilhadas nativas de runtime necessárias para rodar
# o Pillow (jpeg, zlib, libwebp) e conexões Postgres (libpq)
RUN apk add --no-cache \
    libpq \
    jpeg \
    zlib \
    libwebp

# Copia as dependências Python pré-compiladas do primeiro estágio
COPY --from=construtor /install /usr/local

# Copia todo o código-fonte do microsserviço
COPY . .

# Variáveis de ambiente padrão para o worker (podem ser sobrescritas no compose)
ENV PYTHONUNBUFFERED=1

# Comando padrão para inicializar o consumidor assíncrono RabbitMQ
CMD ["python", "-m", "src.consumidor.consumidor_rabbitmq"]
