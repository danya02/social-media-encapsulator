#!/usr/bin/python3
import vk_api
import common
import image_coding
import math
import json
import requests
import uuid

class VkWallImageTransmitter(common.Transmitter):
    def __init__(self,connection):
        self.connection = connection
    def send(self,id,data,part,partmax):
        width = max(128,math.ceil(math.sqrt(len(data)))) # make more optimal!
        height = width
        file=image_coding.encode_bw(id,data,width,height,part,partmax)
        uploader = vk_api.upload.VkUpload(self.connection)
        photo_id = uploader.photo_wall(file)[0]
        api = self.connection.get_api()
        post_id = api.wall.post(attachments=f'photo{ photo_id["owner_id"] }_{ photo_id["id"] }')
        return json.dumps({'post':post_id,'photo':photo_id})
    def remove(self,id):
        id = json.loads(id)
        api = self.connection.get_api()
        api.wall.delete(post_id=id['post']['post_id'])
        api.photos.delete(photo_id=id['photo']['id'])

class VkWallImageReciever(common.Receiver):
    def __init__(self,connection,peer_id):
        self.connection = connection
        self.peer = peer_id
        data = self.connection.get_api().wall.get(owner_id=peer_id)
        self.last_received = data['items'][0]['id']
    def receive_once(self):
        api = self.connection.get_api()
        post = api.wall.getById(posts=f'{self.peer}_{self.last_received+1}')
        if post==[]:
            return
        self.last_received+=1
        post=post[0]
        if 'attachments' not in post:
            return
        files=[]
        for i in post['attachments']:
            if i['type']=='photo':
                maxw=0
                targeturl=''
                for q in i['photo']['sizes']:
                    if q['width']>maxw:
                        maxw=q['width']
                        targeturl=q['url']
                files += [f'/tmp/{uuid.uuid4().hex}.jpg']
                with requests.get(targeturl) as r:
                    with open(files[-1],'wb') as o:
                        o.write(r.content)
        for i in files:
            try:
                self.callback(*image_coding.decode_bw(i))
            except:
                pass
