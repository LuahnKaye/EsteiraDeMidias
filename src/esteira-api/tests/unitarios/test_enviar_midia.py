import pytest
import uuid
from unittest.mock import MagicMock
from src.casos_de_uso.enviar_midia import CasoDeUsoEnviarMidia

@pytest.fixture
def mock_banco():
    return MagicMock()

@pytest.fixture
def mock_mensageria():
    return MagicMock()

def test_deve_lancar_erro_quando_arquivo_exceder_tamanho_maximo(mock_banco, mock_mensageria):
    """
    Garante que arquivos com tamanho maior do que 5MB estouram uma excecao e sao bloqueados.
    """
    caso_de_uso = CasoDeUsoEnviarMidia(mock_banco, mock_mensageria)
    bytes_gigantes = b"0" * (5 * 1024 * 1024 + 10)  # Acima de 5MB
    id_vendedor_valido = uuid.uuid4()
    
    with pytest.raises(ValueError) as erro:
        caso_de_uso.executar(id_vendedor_valido, "imagem_pesada.png", bytes_gigantes)
        
    assert "excede o limite máximo" in str(erro.value)

def test_deve_lancar_erro_quando_assinatura_for_invalida(mock_banco, mock_mensageria):
    """
    Garante que arquivos com Magic Bytes invalidos sejam barrados antes de chegar ao banco de dados.
    """
    caso_de_uso = CasoDeUsoEnviarMidia(mock_banco, mock_mensageria)
    bytes_invalidos = b"texto_falso_fingindo_ser_imagem"
    id_vendedor_valido = uuid.uuid4()
    
    with pytest.raises(ValueError) as erro:
        caso_de_uso.executar(id_vendedor_valido, "falsa.png", bytes_invalidos)
        
    assert "cabecalho fisico do arquivo e invalido" in str(erro.value).lower() or "invalido" in str(erro.value).lower()

def test_deve_processar_e_enfileirar_com_sucesso(mock_banco, mock_mensageria, mocker):
    """
    Valida o fluxo perfeito (Happy Path) isolando dependencias externas (banco, rabbitmq, e sistema de arquivos).
    """
    # Mockamos a escrita no disco para nao sujar o sistema durante os testes
    mocker.patch("builtins.open", mocker.mock_open())
    
    caso_de_uso = CasoDeUsoEnviarMidia(mock_banco, mock_mensageria)
    bytes_validos_png = b"\x89PNG\r\n\x1a\n" + b"dados_corretos"
    id_vendedor_valido = uuid.uuid4()
    
    id_trabalho_gerado = caso_de_uso.executar(id_vendedor_valido, "produto_real.png", bytes_validos_png)
    
    assert isinstance(id_trabalho_gerado, uuid.UUID)
    mock_banco.add.assert_called_once()
    mock_banco.commit.assert_called_once()
    mock_mensageria.publicar_trabalho.assert_called_once()
