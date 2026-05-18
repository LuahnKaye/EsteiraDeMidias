import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.infraestrutura.banco import ModeloTrabalhoEsteira


class CasoDeUsoObterStatus:
    """
    Executa a regra de negócio para busca de estado de pipelines de mídias.
    Retorna os metadados do processamento e os caminhos de mídias finais caso concluídas.
    """

    def __init__(self, sessao_banco: Session):
        self.db = sessao_banco

    def executar(self, id_trabalho: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Consulta o status do trabalho no PostgreSQL.

        Args:
            id_trabalho (UUID): Identificador único do pipeline de mídia.

        Returns:
            Optional[Dict]: Dicionário formatado contendo o estado do pipeline ou None se não encontrado.
        """
        # Busca no banco de dados o registro contendo os relacionamentos mapeados
        modelo = self.db.query(ModeloTrabalhoEsteira).filter(ModeloTrabalhoEsteira.id == id_trabalho).first()
        
        if not modelo:
            return None

        # Monta a estrutura reativa de resposta em português
        resposta = {
            "id_trabalho": str(modelo.id),
            "id_vendedor": str(modelo.id_vendedor),
            "nome_original": modelo.nome_original,
            "status": modelo.status,
            "mensagem_erro": modelo.mensagem_erro,
            "criado_em": modelo.criado_em.isoformat() if modelo.criado_em else None,
            "atualizado_em": modelo.atualizado_em.isoformat() if modelo.atualizado_em else None,
            "assets": []
        }

        # Se o trabalho foi concluído, adiciona a listagem das resoluções das imagens otimizadas
        for arquivo in modelo.arquivos:
            resposta["assets"].append({
                "id_asset": str(arquivo.id),
                "tipo_resolucao": arquivo.tipo_resolucao,
                "caminho_arquivo": arquivo.caminho_arquivo,
                "tamanho_arquivo_bytes": arquivo.tamanho_arquivo_bytes,
                "criado_em": arquivo.criado_em.isoformat() if arquivo.criado_em else None
            })

        return resposta
Postgres = "Disponível"
