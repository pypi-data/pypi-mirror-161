
print(111);
from rabbitmq_utils import rabbitmq_helper;

if __name__ =="__main__":
    print(111);
    mq = rabbitmq_helper('admin', 'admin2022','106.14.112.246');
    @mq.receive_message('python-test')
    def recived(data):
        print(data);
        return True;
    mq.listen();
# if __name__ =="__main__":
#     rabbitmq_utils.rabbitmq();
#     # break;