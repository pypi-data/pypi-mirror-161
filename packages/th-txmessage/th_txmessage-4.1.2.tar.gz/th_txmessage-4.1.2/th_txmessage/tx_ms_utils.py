import logging
from cmq.account import Account
from cmq.queue import Message


class TxYunMessageUtils:
    def __init__(self,secretId,secretKey) -> None:
        self.secretId = secretId;
        self.secretKey = secretKey
        self.my_account = Account("https://cmq-gz.public.tencenttdmq.com",
                            secretId, secretKey, debug=True)

    def getQueue(self,queue_name):
        self.my_account.set_log_level(logging.DEBUG)
        my_queue = self.my_account.get_queue(queue_name)
        return my_queue

    def send_message(self,queue_name,messagebody):
        self.my_account.set_log_level(logging.DEBUG)
        msg_body = messagebody
        msg = Message(msg_body)
        my_queue = self.my_account.get_queue(queue_name)
        my_queue.send_message(msg)