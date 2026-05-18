# Estágio 1: Construção e compilação de dependências do Python
FROM python:3.10-alpine as construtor

WORKDIR /app

# Instala bibliotecas do sistema necessárias para compilar dependências como psycopg2 e libmagic
RUN apk add --no-cache gcc musl-dev postgresql-dev libffi-dev

COPY requirements.txt .

# Instala os pacotes python em um prefixo isolado para evitar conflito com dependências globais
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Estágio 2: Imagem final leve de execução (Runtime)
FROM python:3.10-alpine

WORKDIR /app

# Instala as dependências runtime dinâmicas do sistema operacional alpine (PostgreSQL e Libmagic)
RUN apk add --no-cache libpq libmagic

# Copia os pacotes python instalados e limpos do estágio anterior
COPY --from=construtor /install /usr/local

# Copia todo o código-fonte da aplicação para o diretório de trabalho
COPY . .

# Garante que os logs do python sejam enviados imediatamente ao stdout/stderr sem buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Comando padrão de inicialização apontando para o app FastAPI
CMD ["uvicorn", "src.interfaces.app:app", "--host", "0.0.0.0", "--port", "8000"]
