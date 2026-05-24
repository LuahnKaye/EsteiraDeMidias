import pytest
import uuid
from fastapi.testclient import TestClient
from src.interfaces.app import app

cliente_teste = TestClient(app)

def test_deve_bloquear_por_excesso_de_requisicoes_rate_limit(mocker):
    """
    Testa o comportamento de seguranca do Rate Limiting, esperando receber 429.
    """
    # Mockando a resposta do Redis (que a taxa excedeu)
    mocker.patch("src.interfaces.rotas_midia.verificar_limite_taxa", return_value=False)
    
    resposta = cliente_teste.post(
        "/api/v1/midias/enviar",
        data={"id_vendedor": str(uuid.uuid4())},
        files={"arquivo": ("teste.png", b"algum_conteudo_aqui", "image/png")}
    )
    
    assert resposta.status_code == 429
    assert "Limite de requisições excedido" in resposta.json()["detail"]

def test_deve_retornar_202_quando_fluxo_interno_aceitar_a_requisicao(mocker):
    """
    Simula uma postagem correta, isolando dependencias, esperando o aceite (HTTP 202).
    """
    mocker.patch("src.interfaces.rotas_midia.verificar_limite_taxa", return_value=True)
    
    mock_caso_uso = mocker.patch("src.interfaces.rotas_midia.CasoDeUsoEnviarMidia")
    mock_instancia = mock_caso_uso.return_value
    mock_instancia.executar.return_value = uuid.uuid4()
    
    resposta = cliente_teste.post(
        "/api/v1/midias/enviar",
        data={"id_vendedor": str(uuid.uuid4())},
        files={"arquivo": ("foto_boa.png", b"\x89PNG\r\n\x1a\n", "image/png")}
    )
    
    assert resposta.status_code == 202
    assert "id_trabalho" in resposta.json()

def test_deve_retornar_404_para_status_de_trabalho_inexistente(mocker):
    """
    Testa a visualizacao de status garantindo a informacao de erro HTTP 404 apropriada.
    """
    mock_caso_uso = mocker.patch("src.interfaces.rotas_midia.CasoDeUsoObterStatus")
    mock_instancia = mock_caso_uso.return_value
    mock_instancia.executar.return_value = None
    
    resposta = cliente_teste.get(f"/api/v1/midias/status/{str(uuid.uuid4())}")
    
    assert resposta.status_code == 404
    assert "não foi localizado" in resposta.json()["detail"]
