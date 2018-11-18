#!/usr/bin/python3
import os
import qrcode
import pygame
import uuid
import base64

def encode_qr(text):
    qr = qrcode.QRCode()
    qr.add_data(text)
    data=qr.get_matrix()
    s=pygame.Surface((len(data[0]),len(data)))
    s.fill(pygame.Color('white'))
    for y,l in enumerate(data):
        for x,v in enumerate(l):
            if v:
                s.set_at((x,y),pygame.Color('black'))
    s=pygame.transform.scale(s,(s.get_width()*8,s.get_height()*8))
    f=f'/tmp/{uuid.uuid4().hex}.png'
    pygame.image.save(s,f)
    return f

def decode_qr(file):
    with os.popen(f'zbarimg "{file}"') as o:
        _,__,data=o.read().partition(':')
    return data

def encode(id,data,part,partmax):
    newdata=str(base64.b64encode(data),'utf-8')
    datastr=f'{id}:{part}:{partmax}:{newdata}'
    return encode_qr(datastr)

def decode(file):
    data = decode_qr(file)
    id,part,maxpart,data=data.split(':')
    return id,data,part,maxpart
