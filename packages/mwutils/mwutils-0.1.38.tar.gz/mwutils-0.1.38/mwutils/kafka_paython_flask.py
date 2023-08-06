from kafka import KafkaProducer
from kafka.errors import kafka_errors
import traceback
import json

class Producer():
    def __init__(self, app=None):
        self.producer_k = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        conf = app.config.get('KAFKA_CONFIG', None)
        assert conf, 'KAFKA_CONFIG 设定不存在！,请在config.py中指定'
        self.producer_k = KafkaProducer(bootstrap_servers=conf['bootstrap.servers'].split(','))

    def send(self, topic, key:str, value:str, partition=None):
        future=self.producer_k.send(topic,
                             key=key.encode(),
                             value=value.encode(),
                             partition=partition
                             )
        future.get(timeout=10)  # 监控是否发送成功
        # 同步写入需flush
        # if flush:
        #     self.producer_k.flush()

    # def flush(self,timeout = None):
    #     self.producer_k.flush(timeout=timeout)

    # def close(self,timeout = None):
    #     self.producer_k.close(timeout)