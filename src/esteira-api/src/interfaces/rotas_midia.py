import uuid
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Request, status
from sqlalchemy.orm import Session
from src.casos_de_uso.enviar_midia import CasoDeUsoEnviarMidia
from src.casos_de_uso.obter_status import CasoDeUsoObterStatus
from src.infraestrutura.banco import obter_sessao
from src.infraestrutura.mensageria import PublicadorMensageria
from src.infraestrutura.limite_taxa import verificar_limite_taxa

roteador = APIRouter(prefix="/api/v1/midias", tags=["Mídias"])

# Instancia o publicador global de mensageria RabbitMQ
publicador_mensageria = PublicadorMensageria()


@roteador.post(
    "/enviar", 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recebe uma imagem bruta para otimização assíncrona na esteira"
)
async def enviar_midia(
    requisicao: Request,
    id_vendedor: uuid.UUID = Form(..., description="ID do lojista dono do recurso"),
    arquivo: UploadFile = File(..., description="Arquivo físico de imagem (PNG ou JPEG, máx 5MB)"),
    db: Session = Depends(obter_sessao)
):
    """
    Recebe um upload de arquivo, valida a taxa de chamadas por IP (Rate Limiting via script Lua),
    executa a validação de assinatura física por Magic Bytes e enfileira o trabalho no RabbitMQ.
    """
    ip_cliente = requisicao.client.host if requisicao.client else "127.0.0.1"

    # 1. Validação de Rate Limiting atômico no Redis
    # Limite padrão: Máximo de 10 requisições por 60 segundos por IP
    se_permitido = verificar_limite_taxa(ip_cliente, limite_requisicoes=10, janela_segundos=60)
    if not se_permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de requisições excedido para o seu IP. Tente novamente em breve."
        )

    # 2. Leitura dos bytes físicos da imagem carregada
    try:
        conteudo_arquivo = await arquivo.read()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível ler o arquivo enviado de forma correta."
        )

    # 3. Execução do Caso de Uso Enviar Mídia
    try:
        caso_de_uso = CasoDeUsoEnviarMidia(db, publicador_mensageria)
        id_trabalho = caso_de_uso.executar(
            id_vendedor=id_vendedor,
            nome_original=arquivo.filename if arquivo.filename else "imagem_sem_nome",
            conteudo_arquivo=conteudo_arquivo
        )
        return {"id_trabalho": str(id_trabalho)}
    except ValueError as erro_validacao:
        # Erro gerado na camada de domínio (tamanho ou cabeçalho inválido)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro_validacao)
        )
    except Exception as erro_interno:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno de processamento na esteira: {str(erro_interno)}"
        )


@roteador.get(
    "/status/{id_trabalho}",
    summary="Consulta o progresso e o status atual do processamento de uma mídia"
)
async def obter_status_midia(
    id_trabalho: uuid.UUID,
    db: Session = Depends(obter_sessao)
):
    """
    Busca o status atualizado do pipeline na tabela de rastreabilidade do PostgreSQL.
    Caso concluído, retorna os links de acesso às 3 miniaturas geradas.
    """
    caso_de_uso = CasoDeUsoObterStatus(db)
    resultado = caso_de_uso.executar(id_trabalho)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O trabalho de mídia solicitado não foi localizado no banco de dados."
        )

    return resultado
Postgres = "Disponível"
