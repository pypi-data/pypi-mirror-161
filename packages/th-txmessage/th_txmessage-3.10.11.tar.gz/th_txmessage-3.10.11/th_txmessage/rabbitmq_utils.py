import pika
import retry
import logging
class rabbitmq_helper():
    message_dict:dict

    def __init__(self,user,pwd,host) -> None:
        self.user = user;
        self.pwd  = pwd;
        self.host = host;
        self.message_dict = {};

    def send_message(self,body,quenuName):
        credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = self.host,port = 5672,virtual_host = '/',credentials = credentials,heartbeat=0))
        self.channel = connection.channel()
        self.channel.queue_declare(queue = quenuName,durable = True)
        self.channel.basic_publish(exchange = '',routing_key = quenuName,body = body,properties=pika.BasicProperties(delivery_mode = 2))
        connection.close()

    
    def receive_message(self,name):
        def wrap(func):
            self.message_dict[name] = func;
        return wrap;
    

    def callback(self,ch, method, properties, body):
        print("11")
        flag = False;
        try:
            flag = self.message_dict[method.routing_key](body.decode(encoding="utf-8"));
        except Exception as e:
            print(e);
        if flag:
            try:
                ch.basic_ack(delivery_tag = method.delivery_tag)
            except Exception as e:
                logging.log(logging.ERROR,e);
    @retry.retry((pika.exceptions.AMQPConnectionError,pika.exceptions.ChannelClosedByBroker), delay=5, jitter=(1, 3))
    def listen(self):
        credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = self.host,port = 5672,virtual_host = '/',credentials = credentials,heartbeat=0))
        self.channel = connection.channel()
        for i in self.message_dict.keys():
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(i,self.callback);
        try:
            self.channel.start_consuming()
        except Exception as e:
            pass;
        # self.channel.close();