import boto3
from speedboat.lazythreadpool import LazyThreadPool
import threading
import logging

logger = logging.getLogger('speedboat.sqs')


class MessageSender:

    def __init__(self, queue_url):
        self.queue_url = queue_url
        self.ltp = LazyThreadPool()
        self.local = threading.local()

    def send_10(self, batch):
        if not hasattr(self.local, 'client'):
            self.local.client = boto3.Session().client('sqs')

        sqs = self.local.client
        entries = [{'Id': str(i), 'MessageBody': elem} for i, elem in enumerate(batch)]

        sqs.send_message_batch(QueueUrl=self.queue_url, Entries=entries)

    def batch_10(self, messages):
        current = []
        for m in messages:
            current.append(m)
            if len(current) == 10:
                yield current
                current = []

        if current:
            yield current

    def send_all(self, messages):
        return self.ltp.submit(self.send_10, self.batch_10(messages))


def send_messages(queue_url, messages):
    ms = MessageSender(queue_url)
    for x in ms.send_all(messages):
        pass
