import pytest
import uuid
from unittest.mock import patch, MagicMock
from src.processador.conversor_imagem import ConversorImagem

def test_deve_lancar_erro_quando_arquivo_temporario_nao_existir():
    """
    Testa se o Worker acusa o erro fisico caso a API nao tenha salvo o arquivo antes de enfileirar.
    """
    conversor = ConversorImagem()
    id_vendedor = uuid.uuid4()
    id_trabalho = uuid.uuid4()
    
    with pytest.raises(FileNotFoundError) as erro:
        conversor.otimizar(id_vendedor, id_trabalho, "caminho_inexistente.png")
        
    assert "Arquivo temporário não encontrado" in str(erro.value)

@patch("src.processador.conversor_imagem.Image.open")
@patch("src.processador.conversor_imagem.os.path.exists", return_value=True)
@patch("src.processador.conversor_imagem.os.makedirs")
@patch("src.processador.conversor_imagem.os.path.getsize", return_value=1024)
def test_deve_gerar_tres_miniaturas_corretamente(mock_getsize, mock_makedirs, mock_exists, mock_image_open, mocker):
    """
    Testa se a biblioteca Pillow é orquestrada perfeitamente, gerando os tres redimensionamentos.
    """
    conversor = ConversorImagem()
    
    # Mockando a imagem do Pillow (Image.open)
    mock_imagem = MagicMock()
    mock_imagem.mode = "RGB"
    mock_image_open.return_value.__enter__.return_value = mock_imagem
    
    id_vendedor = uuid.uuid4()
    id_trabalho = uuid.uuid4()
    
    resultados = conversor.otimizar(id_vendedor, id_trabalho, "fake_image.png")
    
    # Valida que as tres resolucoes exigidas no PRD estao mapeadas
    assert "MINIATURA" in resultados
    assert "MEDIA" in resultados
    assert "GRANDE" in resultados
    
    # Valida que a aplicacao realizou o processo de save 3 vezes
    assert mock_imagem.save.call_count == 3
    
    # Valida criticamente que a compressao WebP e 80% estao aplicadas conforme regra
    chamadas_save = mock_imagem.save.call_args_list
    for chamada in chamadas_save:
        args, kwargs = chamada
        assert args[1] == "WEBP"
        assert kwargs["quality"] == 80
