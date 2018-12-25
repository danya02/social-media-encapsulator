#!/usr/bin/python3
import threading
import common
import collections
class TransmissionManager:
    def __init__(self):
        self.transmitters=[]
    def send(self, message):
        method = message.parcellate(self.transmitters)
        for i in method:
            i[0].send(message.id,i[1],i[2],len(method))

# from https://stackoverflow.com/a/40857703/5936187

def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, collections.Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

class ReceptionManager:
    def __init__(self):
        self.receivers=[]
        self.recv_threads=[]
        self.incomplete={}
    def add_receiver(self,recv):
        thread=threading.Thread(target=recv.receive_loop, daemon=True, args=(self,))
        thread.start()
        self.recv_threads.append(thread)
        self.receivers.append(recv)
    def message_callback(self,message):
        print('Received message: ',message)

    def collapse_full(self):
        '''
        Test all incomplete messages for whether they are actually incomplete,
        and calls the callback on completed ones.
        '''
        for i in self.incomplete:
            data=b''
            for q in flatten(self.incomplete[i]):
                if q is None:
                    break
                data+=q
            else:
                m = common.Message(data, i)
                self.message_callback(m)

class Manager:
    def __init__(self):
        self.reception=ReceptionManager()
        self.transmission=TransmissionManager()
        self.seen_messages = []
        self.reception.message_callback = self.test_hash
    def add_receiver(self,recv):
        self.reception.add_receiver(recv)
    def add_transmitter(self,xmit):
        self.transmission.transmitters.append(xmit)
    def send(self,message):
            self.seen_messages.append((message.hash,len(message)))
            self.transmission.send(message)
    def test_hash(self,message):
        group = (message.hash,len(message))
        if group not in self.seen_messages:
            self.seen_messages.append(group)
            self.message_callback(message)
    def message_callback(self,message):
        print('Received message: ',message)
