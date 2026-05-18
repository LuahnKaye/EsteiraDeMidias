import os
import uuid
from PIL import Image

# Diretório base físico das mídias otimizadas definitivas
PASTA_DEFINITIVA = os.getenv("PASTA_DEFINITIVA", "./armazenamento_definitivo")


class ConversorImagem:
    """
    Responsável pelas regras físicas de processamento, redimensionamento e
    otimização das mídias, gerando múltiplas resoluções WebP compactadas.
    """

    RESOLUCOES = {
        "MINIATURA": (150, 150),
        "MEDIA": (640, 640),
        "GRANDE": (1920, 1920)
    }

    def __init__(self):
        # Garante a existência física da pasta de armazenamento definitivo
        if not os.path.exists(PASTA_DEFINITIVA):
            os.makedirs(PASTA_DEFINITIVA)

    def otimizar(self, id_vendedor: uuid.UUID, id_trabalho: uuid.UUID, caminho_temporario: str) -> dict:
        """
        Abre a imagem temporária bruta, gera 3 cópias redimensionadas no formato WebP
        com compressão de 80% de qualidade e salva no diretório definitivo do lojista.

        Args:
            id_vendedor (UUID): Identificador único do vendedor.
            id_trabalho (UUID): Identificador único do pipeline de mídia.
            caminho_temporario (str): Caminho físico no disco do arquivo de imagem temporária bruta.

        Returns:
            dict: Dicionário contendo os caminhos criados e tamanhos físicos de cada versão em bytes.
        """
        if not os.path.exists(caminho_temporario):
            raise FileNotFoundError(f"Arquivo temporário não encontrado: {caminho_temporario}")

        # Cria a árvore física de pastas definitiva: ./armazenamento_definitivo/{id_vendedor}/{id_trabalho}/
        pasta_destino = os.path.join(PASTA_DEFINITIVA, str(id_vendedor), str(id_trabalho))
        os.makedirs(pasta_destino, exist_ok=True)

        resultados = {}

        for tipo_resolucao, (largura_max, altura_max) in self.RESOLUCOES.items():
            # Abrimos a imagem original a cada iteração para evitar distorções sucessivas de escala
            with Image.open(caminho_temporario) as imagem:
                # Converte para RGB caso esteja em RGBA (PNG) para compatibilidade perfeita no salvamento
                if imagem.mode in ("RGBA", "P"):
                    imagem = imagem.convert("RGB")

                # Redimensionamento inteligente mantendo o aspect ratio físico do arquivo original
                imagem.thumbnail((largura_max, altura_max), Image.Resampling.LANCZOS)

                # Define o caminho físico de destino da miniatura correspondente
                nome_arquivo_final = f"{tipo_resolucao.lower()}.webp"
                caminho_final = os.path.join(pasta_destino, nome_arquivo_final)

                # Salva no disco convertendo nativamente para WebP com compressão controlada de 80% de qualidade
                imagem.save(caminho_final, "WEBP", quality=80)

                # Calcula o tamanho real do arquivo físico gravado em bytes
                tamanho_bytes = os.path.getsize(caminho_final)

                resultados[tipo_resolucao] = {
                    "caminho": caminho_final,
                    "tamanho_bytes": tamanho_bytes
                }

        return resultados
