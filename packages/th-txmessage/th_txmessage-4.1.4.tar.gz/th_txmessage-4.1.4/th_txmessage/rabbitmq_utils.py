from cmath import log
import functools
from threading import Thread
import threading
from time import sleep
import pika
import retry
import logging
import uuid;
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class rabbitmq_helper():
    message_dict:dict
    thread_stop_flag:dict;
    def __init__(self,user,pwd,host) -> None:
        self.user = user;
        self.pwd  = pwd;
        self.host = host;
        self.message_dict = {};
        self.thread_stop_flag = {};

    def send_message(self,body,quenuName):
        credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = self.host,port = 5672,virtual_host = '/',credentials = credentials,heartbeat=10))
        self.channel = connection.channel()
        self.channel.queue_declare(queue = quenuName,durable = True)
        self.channel.basic_publish(exchange = '',routing_key = quenuName,body = body,properties=pika.BasicProperties(delivery_mode = 2))
        connection.close()

    def ack_message(self,channel, delivery_tag):
        # print(f'ack_message thread id: {threading.get_ident()}')
        logger.info(f'ack_message thread id: {threading.get_ident()}')
        if channel.is_open:
            channel.basic_ack(delivery_tag)
        else:
            # Channel is already closed, so we can't ACK this message;
            # log and/or do something that makes sense for your app in this case.
            pass

    def receive_message(self,name):
        def wrap(func):
            self.message_dict[name] = func;
        return wrap;
    
    def do_work(self,channel, delivery_tag, body,r_k):
        flag = self.message_dict[r_k](body.decode(encoding="utf-8"));
        if flag:
            try:
                cb = functools.partial(self.ack_message,channel, delivery_tag)
                channel.connection.add_callback_threadsafe(cb)
            except Exception as e:
                logger.error(e);

    def callback(self,ch, method, properties, body):
        flag = False;
        try:
            delivery_tag = method.delivery_tag
            r_k = method.routing_key;
            t = threading.Thread(target=self.do_work, args=(ch, delivery_tag, body,r_k))
            t.start()
        except Exception as e:
            print(e);

    def heart_thread(self,conn,uuid):
        while True:
            try:
                if  self.thread_stop_flag[uuid]:
                    break;
                else:
                    conn.process_data_events();
            except Exception:
                pass;
            sleep(5);


    @retry.retry((pika.exceptions.AMQPConnectionError), delay=5, jitter=(1, 3))
    def listen(self):
        if self.__dict__.__contains__("connection"):
           if self.connection.is_open:
                self.connection.close();
        logging.info("开始启动")
        credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(socket_timeout=10,host = self.host,port = 5672,virtual_host = '/',credentials = credentials,heartbeat=5))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.connection.add_callback_threadsafe
        for i in self.message_dict.keys():
                self.channel.basic_consume(i,self.callback);
        try:
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            pass