import os
import uuid
from sqlalchemy.orm import Session
from src.dominio.entidades import TrabalhoEsteira
from src.dominio.validador_assinatura import validar_assinatura_imagem
from src.infraestrutura.banco import ModeloTrabalhoEsteira
from src.infraestrutura.mensageria import PublicadorMensageria

# Define o caminho da pasta de armazenamento temporário para gravação das mídias brutas
PASTA_TEMPORARIA = os.getenv("PASTA_TEMPORARIA", "./armazenamento_temporario")


class CasoDeUsoEnviarMidia:
    """
    Executa a regra de negócio da aplicação para recebimento e enfileiramento de mídias brutas.
    Foca em segurança física e resiliência transacional (banco e fila).
    """

    def __init__(self, sessao_banco: Session, publicador_mensageria: PublicadorMensageria):
        self.db = sessao_banco
        self.publicador = publicador_mensageria

        # Garante que a pasta temporária de gravação existe fisicamente
        if not os.path.exists(PASTA_TEMPORARIA):
            os.makedirs(PASTA_TEMPORARIA)

    def executar(self, id_vendedor: uuid.UUID, nome_original: str, conteudo_arquivo: bytes) -> uuid.UUID:
        """
        Executa a pipeline de upload primário e postagem na esteira reativa.

        Args:
            id_vendedor (UUID): Identificador único do lojista proprietário.
            nome_original (str): O nome original do arquivo de imagem.
            conteudo_arquivo (bytes): Os bytes físicos brutos da imagem carregada.

        Returns:
            UUID: O id_trabalho identificador do pipeline assíncrono criado.
        """
        # 1. Validação de Tamanho (Máximo 5MB)
        tamanho_maximo = 5 * 1024 * 1024
        if len(conteudo_arquivo) > tamanho_maximo:
            raise ValueError("O arquivo excede o limite máximo de 5MB permitido.")

        # 2. Validação Física por Magic Bytes (Mime-type Security)
        se_valida = validar_assinatura_imagem(conteudo_arquivo)
        if not se_valida:
            raise ValueError("O cabecalho fisico do arquivo e invalido. Apenas imagens legitimas PNG ou JPEG sao aceitas.")

        # 3. Criação da Entidade de Domínio Pura
        entidade_trabalho = TrabalhoEsteira(
            id_vendedor=id_vendedor,
            nome_original=nome_original
        )

        # 4. Gravação física do arquivo bruto no disco local temporário
        # O nome do arquivo temporário será o próprio ID único gerado
        caminho_salvo = os.path.join(PASTA_TEMPORARIA, f"{entidade_trabalho.id}")
        with open(caminho_salvo, "wb") as buffer_arquivo:
            buffer_arquivo.write(conteudo_arquivo)

        # 5. Persistência de Dados (PostgreSQL)
        modelo_banco = ModeloTrabalhoEsteira(
            id=entidade_trabalho.id,
            id_vendedor=entidade_trabalho.id_vendedor,
            nome_original=entidade_trabalho.nome_original,
            status=entidade_trabalho.status
        )
        self.db.add(modelo_banco)
        self.db.commit()

        # 6. Publicação de Mensagem JSON na fila de Mensageria (RabbitMQ)
        dados_payload = {
            "id_trabalho": str(entidade_trabalho.id),
            "id_vendedor": str(entidade_trabalho.id_vendedor),
            "nome_original": entidade_trabalho.nome_original,
            "caminho_temporario": caminho_salvo
        }
        self.publicador.publicar_trabalho(dados_payload)

        return entidade_trabalho.id
