import os
import time
import json
import uuid
import pika
from src.infraestrutura.banco_worker import obter_sessao_worker, ModeloTrabalhoEsteira, ModeloAssetProcessado
from src.processador.conversor_imagem import ConversorImagem

# Configurações de conexões AMQP obtidas via ambiente
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-broker")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
FILA_TRABALHOS = "fila_trabalhos_esteira"


class ConsumidorRabbitMQ:
    """
    Consumidor reativo responsável por capturar eventos de trabalhos de mídia na fila
    RabbitMQ, orquestrar a otimização de imagens e persistir os resultados no Postgres.
    """

    def __init__(self):
        self.conversor = ConversorImagem()
        self.credenciais = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

    def iniciar_escuta(self):
        """
        Garante a conexão resiliente ao RabbitMQ com loop de reconexão automática
        em caso de quedas físicas do broker de mensagens.
        """
        while True:
            try:
                print(f"[*] Conectando ao Broker RabbitMQ em: {RABBITMQ_HOST}...")
                parametros = pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    credentials=self.credenciais,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                conexao = pika.BlockingConnection(parametros)
                canal = conexao.channel()

                # Declara a fila de forma persistente (durable=True)
                canal.queue_declare(queue=FILA_TRABALHOS, durable=True)

                # Distribuição equilibrada de carga: Processa 1 trabalho por vez por worker
                canal.basic_qos(prefetch_count=1)

                print(f"[+] Conectado com sucesso! Aguardando mensagens na fila '{FILA_TRABALHOS}'...")
                
                canal.basic_consume(
                    queue=FILA_TRABALHOS, 
                    on_message_callback=self.processar_mensagem, 
                    auto_ack=False  # Habilita ACKs manuais explícitos para tolerância a falhas
                )

                canal.start_consuming()

            except pika.exceptions.AMQPConnectionError:
                print("[!] Falha de conexão com o RabbitMQ. Tentando novamente em 5 segundos...")
                time.sleep(5)
            except KeyboardInterrupt:
                print("[*] Consumidor interrompido manualmente pelo usuário.")
                break
            except Exception as erro:
                print(f"[!] Erro inesperado no loop do consumidor: {str(erro)}. Reiniciando em 5 segundos...")
                time.sleep(5)

    def processar_mensagem(self, canal, metodo, propriedades, corpo):
        """
        Callback disparado reativamente ao receber uma mensagem da fila.
        """
        tamanho_payload = len(corpo)
        print(f"\n[+] Nova mensagem recebida da fila ({tamanho_payload} bytes)!")
        
        db = obter_sessao_worker()
        id_trabalho_str = None
        caminho_temporario = None

        try:
            # 1. Decodificação do Payload JSON
            dados_payload = json.loads(corpo.decode("utf-8"))
            id_trabalho_str = dados_payload.get("id_trabalho")
            id_vendedor_str = dados_payload.get("id_vendedor")
            caminho_temporario = dados_payload.get("caminho_temporario")

            if not id_trabalho_str or not id_vendedor_str or not caminho_temporario:
                raise ValueError("Payload JSON incompleto ou malformatado.")

            id_trabalho = uuid.UUID(id_trabalho_str)
            id_vendedor = uuid.UUID(id_vendedor_str)

            print(f"[*] Processando trabalho UUID: {id_trabalho} para o lojista: {id_vendedor}")

            # 2. Transiciona status do banco para "PROCESSANDO"
            trabalho_banco = db.query(ModeloTrabalhoEsteira).filter(ModeloTrabalhoEsteira.id == id_trabalho).first()
            if not trabalho_banco:
                raise FileNotFoundError(f"Trabalho de mídia {id_trabalho} não encontrado no banco PostgreSQL.")

            trabalho_banco.status = "PROCESSANDO"
            db.commit()

            # 3. Executa a otimização de imagem (conversão e redimensionamentos WebP)
            dicionario_assets = self.conversor.otimizar(
                id_vendedor=id_vendedor,
                id_trabalho=id_trabalho,
                caminho_temporario=caminho_temporario
            )

            # 4. Grava os novos assets criados na tabela relacionável
            for tipo_resolucao, dados_asset in dicionario_assets.items():
                novo_asset = ModeloAssetProcessado(
                    id_trabalho=id_trabalho,
                    tipo_resolucao=tipo_resolucao,
                    caminho_arquivo=dados_asset["caminho"],
                    tamanho_arquivo_bytes=dados_asset["tamanho_bytes"]
                )
                db.add(novo_asset)

            # 5. Conclui com absoluto sucesso!
            trabalho_banco.status = "CONCLUIDO"
            trabalho_banco.mensagem_erro = None
            db.commit()

            print(f"[✅] Trabalho {id_trabalho} finalizado com sucesso absoluto! Assets gravados no PostgreSQL.")

        except Exception as erro_processamento:
            db.rollback()
            print(f"[❌] Erro ao processar trabalho: {str(erro_processamento)}")
            
            # Se já conseguimos mapear o ID do trabalho no banco, atualiza com o status de erro
            if id_trabalho_str:
                try:
                    trabalho_banco = db.query(ModeloTrabalhoEsteira).filter(ModeloTrabalhoEsteira.id == uuid.UUID(id_trabalho_str)).first()
                    if trabalho_banco:
                        trabalho_banco.status = "FALHOU"
                        trabalho_banco.mensagem_erro = str(erro_processamento)
                        db.commit()
                        print("[*] Status do trabalho atualizado para 'FALHOU' no PostgreSQL.")
                except Exception as erro_interno_db:
                    print(f"[!] Erro crítico ao atualizar status de falha no banco: {str(erro_interno_db)}")

        finally:
            db.close()

            # 6. Limpeza Física: Exclui o arquivo físico bruto temporário
            if caminho_temporario and os.path.exists(caminho_temporario):
                try:
                    os.remove(caminho_temporario)
                    print(f"[*] Arquivo temporário bruto excluído com sucesso: {caminho_temporario}")
                except Exception as erro_exclusao:
                    print(f"[!] Aviso: Não foi possível excluir o arquivo temporário físico: {str(erro_exclusao)}")

            # 7. Resiliência: Confirma de forma explícita o ACK ao Broker RabbitMQ
            # Isso garante que a mensagem seja expurgada da fila, seja por sucesso ou por
            # falha devidamente tratada, evitando travamentos em loop na esteira.
            canal.basic_ack(delivery_tag=metodo.delivery_tag)


if __name__ == "__main__":
    consumidor = ConsumidorRabbitMQ()
    consumidor.iniciar_escuta()
