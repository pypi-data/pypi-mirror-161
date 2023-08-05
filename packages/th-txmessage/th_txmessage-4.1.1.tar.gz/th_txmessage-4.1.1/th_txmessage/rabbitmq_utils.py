from threading import Thread
import threading
from time import sleep
import traceback
from typing_extensions import Self
import pika
import retry
import logging
import uuid;
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

    
    def receive_message(self,name):
        def wrap(func):
            self.message_dict[name] = func;
        return wrap;
    

    def callback(self,ch, method, properties, body):
        flag = False;
        uuidOne = str(uuid.uuid1())
        heart_thread = threading.Thread(target=self.heart_thread,args=(self.connection,uuidOne)); 
        self.thread_stop_flag[uuidOne] = False;
        heart_thread.start();
        try:
            flag = self.message_dict[method.routing_key](body.decode(encoding="utf-8"));
        except Exception as e:
            print(e);
        finally:
            self.thread_stop_flag[uuidOne] = True;
        if flag:
            try:
                ch.basic_ack(delivery_tag = method.delivery_tag)
            except Exception as e:
                logging.log(logging.ERROR,e);
        else:

    def heart_thread(self,conn,uuid):
        while True:
            try:
                if  self.thread_stop_flag[uuid]:
                    break;
                else:
                    conn.process_data_events();
            except Exception:
                pass;
            sleep(10);

    @retry.retry((pika.exceptions.AMQPConnectionError), delay=5, jitter=(1, 3))
    def listen(self):
        credentials = pika.PlainCredentials(self.user, self.pwd)  # mq用户名和密码
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(socket_timeout=10,host = self.host,port = 5672,virtual_host = '/',credentials = credentials,heartbeat=30))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        for i in self.message_dict.keys():
                self.channel.basic_consume(i,self.callback);
        self.channel.start_consuming()
        