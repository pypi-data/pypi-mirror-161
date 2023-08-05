import json
import rabbitmq_utils;

mq = rabbitmq_utils.rabbitmq_helper('admin', 'admin2022','106.14.112.246');

for i in range(10):
    message = json.dumps({'OrderId':"1000%s"%i})
    mq.send_message(message,'python-test')