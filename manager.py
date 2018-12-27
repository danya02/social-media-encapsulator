#!/usr/bin/python3
import threading
import common
import collections
import json

class TransmissionManager:
    def __init__(self, transmitters=[]):
        self.transmitters=transmitters
    def send(self, message):
        method = message.parcellate(self.transmitters)
        for i in method:
            i[0].send(message.id,i[1],i[2],len(method))
    def dump(self):
        return [i.save() for i in self.transmitters]

    @classmethod
    def load(cls, data):
        xmits=[]
        for i in data:
            local = dict()
            exec(i, globals(), local)
            xmits.append(local['transmitter'])
        return cls(xmits)


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
    def __init__(self, receivers=[]):
        self.recv_threads=[]
        self.receivers=[]
        for i in receivers:
            self.add_receiver(i)
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
    def dump(self):
        return [i.save() for i in self.receivers]

    @classmethod
    def load(cls, data):
        recvs = []
        for i in data:
            local = dict()
            exec(i, globals(), local)
            recvs.append(local['receiver'])
        return cls(recvs)


class Manager:
    def __init__(self, config=None):
        self.config = config
        if self.config is None:
            self.config={'transmission':[], 'reception':[]}
        self.transmission = TransmissionManager.load(self.config['transmission'])
        self.reception = ReceptionManager.load(self.config['reception'])

        self.seen_messages = []
        self.reception.message_callback = self.test_hash
    def add_receiver(self,recv):
        s = recv.save()
        if s not in self.config['reception']:
            self.reception.add_receiver(recv)
            self.config['reception'] = self.reception.dump()
    def add_transmitter(self,xmit):
        s = xmit.save()
        if s not in self.config['transmission']:
            self.transmission.transmitters.append(xmit)
            self.config['transmission']=self.transmission.dump()
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
    def dump(self):
        return self.config
    @classmethod
    def load(cls, data):
        return cls(data)
