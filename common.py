#!/usr/bin/python3
import uuid
import random

class Message:
    def __init__(self, data:bytes, id:int=None):
        self.data=data
        self.id=id
        if self.id is None:
            self.id=int(uuid.uuid4().hex,16)

    def __repr__(self):
        return f'Message({self.data}, {self.id})'

    @classmethod
    def from_file(cls,file, id:int=None):
        '''
        Create a message that has this file's data as its own.
        '''
        if isinstance(file,str):
            file = open(file,'rb')
        data=file.read()
        m = cls(data,id)
        return m

    def parcellate(self,transmitters):
        '''
        Split the data this message holds into pieces suitable for each transmitter.

        Returns a list of tuples of (transmitter object, data to send, chunk id starting from 1).
        '''
        random.shuffle(transmitters)
        for i in transmitters:
            if i.get_max_length()<len(self.data):
                return (i,self.data,1)
        transmitters = sorted(transmitters, key=lambda x:x.get_max_length(), reverse=True)
        head=0
        splits=[]
        while not head>=len(self.data):
            for i in transmitters:
                if head>=len(self.data):break
                newdata=self.data[head:head+i.get_max_length()]
                splits+=[(i,newdata,len(splits)+1)]
                head+=i.get_max_length()
        return splits


class Transmitter:
    def __init__(self):
        pass
    def get_max_length(self):
        '''Get maximum length of message this transmitter will accept.'''
        raise NotImplementedError
    def send(self, id:int, data:bytes, part:int, partmax:int):
        '''Transmit the data.

        Returns an ID, unique to this transmitter, that can be used to later remove the transmission,
        or None if the method does not support removing the transmissions.
        '''
        raise NotImplementedError
    def remove(self,id):
        '''Remove a previous transmission by its ID.'''
        raise NotImplementedError

class Receiver:
    def __init__(self):
        self._stop=False
    def stop_loop(self):
        '''Stop a loop previously started with receive_loop.'''
        self._stop = True
    def receive_loop(self):
        '''
        Loop waiting for messages until stop_loop is called.
        When a message part is received, run the callback with the arguments of id, data, part number, maximum part number.

        This is just a convinience function for starting a thread.
        '''
        while not self._stop:
            self.receive_once()
        self._stop=False
    def receive_once(self):
        '''
        Try to get new data once.
        If a message part is received, run the callback with the arguments of id, data, part number, maximum part number.
        '''
    @staticmethod
    def callback(id, data, part, max_part):
        '''Callback for getting data from the receiver. Replace this with your own method.'''
        pass
