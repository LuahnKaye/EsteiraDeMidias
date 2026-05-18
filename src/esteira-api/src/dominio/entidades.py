import uuid
from datetime import datetime
from typing import Optional, List


class AssetProcessado:
    """
    Entidade pura de domínio que representa as versões otimizadas de uma imagem.
    """

    def __init__(
        self,
        id_trabalho: uuid.UUID,
        tipo_resolucao: str,
        caminho_arquivo: str,
        tamanho_arquivo_bytes: int,
        id: Optional[uuid.UUID] = None,
        criado_em: Optional[datetime] = None
    ):
        self.id = id or uuid.uuid4()
        self.id_trabalho = id_trabalho
        self.tipo_resolucao = tipo_resolucao  # MINIATURA, MEDIA, GRANDE
        self.caminho_arquivo = caminho_arquivo
        self.tamanho_arquivo_bytes = tamanho_arquivo_bytes
        self.criado_em = criado_em or datetime.utcnow()


class TrabalhoEsteira:
    """
    Entidade pura de domínio que representa o pipeline de otimização de uma mídia.
    """

    STATUS_PENDENTE = "PENDENTE"
    STATUS_PROCESSANDO = "PROCESSANDO"
    STATUS_CONCLUIDO = "CONCLUIDO"
    STATUS_FALHOU = "FALHOU"

    STATUS_PERMITIDOS = {
        STATUS_PENDENTE,
        STATUS_PROCESSANDO,
        STATUS_CONCLUIDO,
        STATUS_FALHOU
    }

    def __init__(
        self,
        id_vendedor: uuid.UUID,
        nome_original: str,
        id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        mensagem_erro: Optional[str] = None,
        criado_em: Optional[datetime] = None,
        atualizado_em: Optional[datetime] = None,
        arquivos: Optional[List[AssetProcessado]] = None
    ):
        self.id = id or uuid.uuid4()
        self.id_vendedor = id_vendedor
        self.nome_original = nome_original
        self.status = status or self.STATUS_PENDENTE
        self.mensagem_erro = mensagem_erro
        self.criado_em = criado_em or datetime.utcnow()
        self.atualizado_em = atualizado_em or datetime.utcnow()
        self.arquivos = arquivos or []

        if self.status not in self.STATUS_PERMITIDOS:
            raise ValueError(f"Status '{self.status}' é inválido para o trabalho da esteira.")

    def iniciar_processamento(self) -> None:
        """
        Altera o estado do pipeline para em processamento.
        """
        self.status = self.STATUS_PROCESSANDO
        self.atualizado_em = datetime.utcnow()

    def concluir(self, arquivos_otimizados: List[AssetProcessado]) -> None:
        """
        Finaliza o pipeline com sucesso, anexando os arquivos processados correspondentes.
        """
        self.status = self.STATUS_CONCLUIDO
        self.arquivos = arquivos_otimizados
        self.mensagem_erro = None
        self.atualizado_em = datetime.utcnow()

    def falhar(self, motivo: str) -> None:
        """
        Marca o pipeline como falho e registra a causa do erro.
        """
        self.status = self.STATUS_FALHOU
        self.mensagem_erro = motivo
        self.atualizado_em = datetime.utcnow()
