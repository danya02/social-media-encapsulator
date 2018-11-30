#!/usr/bin/python3
import os
import qrcode
import pygame
import uuid
import base64

# from https://stackoverflow.com/a/312464/5936187
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def encode_qr(text,output=None):
    qr = qrcode.QRCode()
    qr.add_data(text)
    data=qr.get_matrix()
    s=pygame.Surface((len(data[0]),len(data)))
    s.fill(pygame.Color('white'))
    for y,l in enumerate(data):
        for x,v in enumerate(l):
            if v:
                s.set_at((x,y),pygame.Color('black'))
    s=pygame.transform.scale(s,(800,800))
    if output is None:
        f=f'/tmp/{uuid.uuid4().hex}.png'
    else:
        f=output
    pygame.image.save(s,f)
    return f

def decode_qr(file):
    with os.popen(f'zbarimg --raw "{file}"') as o:
        data=o.read().strip()
    if data=='':
        raise ValueError('Not a valid QR code!')
    return data

def decode_many_qr(files):
    datas=[]
    for i in chunks(files,1024):
        cmd='zbarimg --raw ' + ' '.join([f'"{file}"' for file in i])
        with os.popen(cmd) as o:
            for i in o:
                datas.append(i.strip())
    return datas

def encode(id,data,part,partmax):
    newdata=str(base64.b64encode(data),'utf-8')
    datastr=f'{id}:{part}:{partmax}:{newdata}'
    return encode_qr(datastr)

def decode(file):
    data = decode_qr(file)
    id,part,maxpart,data=data.split(':')
    return id,data,part,maxpart
