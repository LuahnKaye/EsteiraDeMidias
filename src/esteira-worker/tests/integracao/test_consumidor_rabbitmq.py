import pytest
import json
import uuid
from unittest.mock import MagicMock
from src.consumidor.consumidor_rabbitmq import ConsumidorRabbitMQ

def test_deve_processar_mensagem_valida_e_marcar_como_concluido(mocker):
    """
    Simula uma mensagem real chegando do Broker RabbitMQ e testa toda a orquestracao: 
    Conversao WebP, Registro no Banco, e Exclusao Temporaria.
    """
    # 1. Arrange: Mocks para dependencias externas
    mock_db = MagicMock()
    mocker.patch("src.consumidor.consumidor_rabbitmq.obter_sessao_worker", return_value=mock_db)
    
    mock_conversor = MagicMock()
    mock_conversor.otimizar.return_value = {
        "MINIATURA": {"caminho": "miniatura.webp", "tamanho_bytes": 100},
        "MEDIA": {"caminho": "media.webp", "tamanho_bytes": 200},
        "GRANDE": {"caminho": "grande.webp", "tamanho_bytes": 300},
    }
    mocker.patch("src.consumidor.consumidor_rabbitmq.ConversorImagem", return_value=mock_conversor)
    mocker.patch("src.consumidor.consumidor_rabbitmq.os.path.exists", return_value=False)
    
    mock_trabalho_banco = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_trabalho_banco
    
    consumidor = ConsumidorRabbitMQ()
    
    mock_canal = MagicMock()
    mock_metodo = MagicMock()
    mock_propriedades = MagicMock()
    
    id_trabalho = str(uuid.uuid4())
    payload = json.dumps({
        "id_trabalho": id_trabalho,
        "id_vendedor": str(uuid.uuid4()),
        "caminho_temporario": "temp.png"
    }).encode("utf-8")
    
    # 2. Act: Callback do Consumidor 
    consumidor.processar_mensagem(mock_canal, mock_metodo, mock_propriedades, payload)
    
    # 3. Assert: Valida a Mudança de Status
    assert mock_trabalho_banco.status == "CONCLUIDO"
    assert mock_trabalho_banco.mensagem_erro is None
    
    # Valida que o Worker persistiu os Assets Fisicos Otimizados
    assert mock_db.add.call_count == 3
    assert mock_db.commit.called
    
    # Valida a confirmacao Resiliente da Fila
    mock_canal.basic_ack.assert_called_once_with(delivery_tag=mock_metodo.delivery_tag)
