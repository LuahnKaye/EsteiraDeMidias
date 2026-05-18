import os
import uuid
from datetime import datetime
from typing import Generator
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Endereço de conexão com o PostgreSQL obtido via variáveis de ambiente
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@postgres-db:5432/esteira_db"
)

# Configura a engine de conexões com o pool de conexões otimizado
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Valida se a conexão está ativa antes de disparar consultas
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ModeloTrabalhoEsteira(Base):
    """
    Modelo relacional SQLAlchemy mapeando a tabela 'trabalhos_esteira'.
    """
    __tablename__ = "trabalhos_esteira"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_vendedor = Column(UUID(as_uuid=True), nullable=False, index=True)
    nome_original = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="PENDENTE")
    mensagem_erro = Column(Text, nullable=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento cascade: se o trabalho for excluído, os assets também serão
    arquivos = relationship("ModeloAssetProcessado", back_populates="trabalho", cascade="all, delete-orphan")


class ModeloAssetProcessado(Base):
    """
    Modelo relacional SQLAlchemy mapeando a tabela 'assets_processados'.
    """
    __tablename__ = "assets_processados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_trabalho = Column(UUID(as_uuid=True), ForeignKey("trabalhos_esteira.id", ondelete="CASCADE"), nullable=False)
    tipo_resolucao = Column(String(50), nullable=False)  # MINIATURA, MEDIA, GRANDE
    caminho_arquivo = Column(String(512), nullable=False)
    tamanho_arquivo_bytes = Column(Integer, nullable=False)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    trabalho = relationship("ModeloTrabalhoEsteira", back_populates="arquivos")


def inicializar_banco() -> None:
    """
    Cria as tabelas no PostgreSQL no startup da API caso não existam.
    """
    Base.metadata.create_all(bind=engine)


def obter_sessao() -> Generator:
    """
    Dependency injection para obter a sessão de banco de dados por requisição do FastAPI.
    Garante o fechamento automático da conexão no fim do ciclo de vida da chamada.
    """
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()
