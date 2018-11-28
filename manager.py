#!/usr/bin/python3
import threading
import common
class TransmissionManager:
    def __init__(self):
        self.transmitters=[]
    def send(self, message):
        method = message.parcellate(self.transmitters)
        for i in method:
            i[0].send(message.id,i[1],i[2],len(method))

class ReceptionManager:
    def __init__(self):
        self.receivers=[]
        self.recv_threads=[]
        self.incomplete={}
    def add_receiver(self,recv):
        recv.callback = self.part_callback
        thread=threading.Thread(target=recv.receive_loop,daemon=True)
        thread.start()
        self.recv_threads.append(thread)
        self.receivers.append(recv)
    def message_callback(self,message):
        print('Received message: ',message)
    def part_callback(self,id,data,part,maxpart):
        if id not in self.incomplete:
            self.incomplete.update({id:[None for i in range(maxpart)]})
        if len(self.incomplete[id])!=maxpart:
            raise ValueError(f'Received part claims message is {maxpart} parts long, but earlier we heard it\'s {len(self.incomplete[id])} parts long')
        self.incomplete[id][part-1]=data
        if None not in self.incomplete[id]:
            m = common.Message(b''.join(self.incomplete[id]),id)
            self.message_callback(m)
