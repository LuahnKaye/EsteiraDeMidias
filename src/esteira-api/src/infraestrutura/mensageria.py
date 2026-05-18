import os
import pika
import json
import time
from typing import Dict, Any


class PublicadorMensageria:
    """
    Gerencia a conexão e publicação de eventos de trabalhos na fila do RabbitMQ.
    Implementa um mecanismo resiliente de re-tentativas de conexão em caso de falha.
    """

    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq-broker")
        self.usuario = os.getenv("RABBITMQ_USER", "guest")
        self.senha = os.getenv("RABBITMQ_PASS", "guest")
        self.nome_fila = "fila_trabalhos_esteira"
        self.conexao = None
        self.canal = None

    def conectar(self) -> None:
        """
        Estabelece a conexão física com o Broker RabbitMQ de forma resiliente.
        Tenta reconectar a cada 3 segundos em caso de falha de rede/inicialização inicial.
        """
        credenciais = pika.PlainCredentials(self.usuario, self.senha)
        parametros = pika.ConnectionParameters(
            host=self.host,
            credentials=credenciais,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        tentativas = 10
        for i in range(tentativas):
            try:
                self.conexao = pika.BlockingConnection(parametros)
                self.canal = self.conexao.channel()
                
                # Declara a fila de forma persistente (durable=True) para que sobreviva a restarts do Broker
                self.canal.queue_declare(queue=self.nome_fila, durable=True)
                return
            except pika.exceptions.AMQPConnectionError:
                if i == tentativas - 1:
                    raise RuntimeError("Não foi possível conectar ao Broker RabbitMQ após múltiplas tentativas.")
                time.sleep(3)

    def publicar_trabalho(self, dados_trabalho: Dict[str, Any]) -> None:
        """
        Publica o payload de metadados do trabalho no formato JSON na fila persistente.
        """
        # Garante que a conexão está ativa antes de publicar
        if not self.conexao or self.conexao.is_closed:
            self.conectar()

        payload = json.dumps(dados_trabalho)

        self.canal.basic_publish(
            exchange='',
            routing_key=self.nome_fila,
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=2  # Modo 2: Torna a mensagem persistente em disco no Broker
            )
        )

    def fechar(self) -> None:
        """
        Fecha a conexão ativa com o RabbitMQ.
        """
        if self.conexao and not self.conexao.is_closed:
            self.conexao.close()
