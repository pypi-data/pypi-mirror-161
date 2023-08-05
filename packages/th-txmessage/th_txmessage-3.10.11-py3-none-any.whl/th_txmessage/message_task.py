from th_txmessage.tx_ms_utils import TxYunMessageUtils
import traceback
import json
import time


class TxyunMessage:
    message_deal_process = {}
    message_deal_process_after = {}
    
    def message_deal(self, messageType):
        def wrap(func):
            self.message_deal_process[messageType] = func
            return func
        return wrap
    
    def message_deal_after(self,messageType):
        def wrap(func):
            self.message_deal_process_after[messageType] = func
            return func
        return wrap
    
    def error_deal(self):
        def wrap(func):
            self.m_error_deal = func
            return func
        return wrap
    
    
    
    def __init__(self, qname, secretId, secretKey) -> None:
        self.qname = qname
        self.secretId = secretId
        self.secretKey = secretKey
        txyunUtils = TxYunMessageUtils(self.secretId, self.secretKey)
        self.txyunUtils = txyunUtils;

    def listent2(self):
        while True:
            try:
                myQueue = self.txyunUtils.getQueue(self.qname)
                recv_msg = myQueue.receive_message(3)
                messageBody = json.loads(recv_msg.msgBody)
                if "lx" not in messageBody.keys() or "data" not in messageBody.keys():
                        myQueue.delete_message(recv_msg.receiptHandle)
                else:
                    self.run(
                            message_type=messageBody["lx"], message_body=messageBody["data"])
                    if messageBody["lx"] in self.message_deal_process_after.keys():
                                self.message_deal_process_after[messageBody["lx"]](myQueue,recv_msg)
            except Exception as e:
                    self.m_error_deal(e)
    
    def listent(self):
        while True:
            try:
                myQueue = self.txyunUtils.getQueue(self.qname)
                recv_msg = myQueue.receive_message(3)
            except Exception as e:
                # time.sleep(30)
                pass
            else:
                try:
                    messageBody = json.loads(recv_msg.msgBody)
                    if "lx" not in messageBody.keys() or "data" not in messageBody.keys():
                        myQueue.delete_message(recv_msg.receiptHandle)
                    else:
                        flag = self.run(
                            message_type=messageBody["lx"], message_body=messageBody["data"])
                        if flag == True:
                            myQueue.delete_message(recv_msg.receiptHandle)
                            # t = 0
                            # while True:
                            #     try:
                            #         myQueue.delete_message(recv_msg.receiptHandle)
                            #     except:
                            #         t += 1
                            #         print(f'消息删除失败==={t}')
                            #         if t > 100:
                            #             break
                            #         time.sleep(0.5)
                            #         continue
                except Exception as e:
                    time.sleep(2)
                    traceback.print_exc()

    def run(self, message_type, message_body):
        if message_type in self.message_deal_process.keys():
            return self.message_deal_process[message_type](message_body)
