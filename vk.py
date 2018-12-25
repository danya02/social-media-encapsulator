#!/usr/bin/python3
import vk_api
import common
import image_coding
import math
import json
import requests
import uuid
import video_coding
import bs4
import re
import traceback

class VkWallImageTransmitter(common.Transmitter):
    def __init__(self,connection):
        self.connection = connection
    def send(self,id,data,part,partmax):
        width = 2560 # make more optimal!
        height = 2048
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
    def get_max_length(self):
        return 2560*(2048-5)

class VkWallVideoTransmitter(common.Transmitter):
    def __init__(self,connection):
        self.connection = connection
    def send(self,id,data,part,partmax):
        vidpath=video_coding.create_video(id,data,part,partmax)
        upload = vk_api.VkUpload(self.connection)
        vid = upload.video(video_file=vidpath,wallpost=True)

class VkChatImageTransmitter(common.Transmitter):
    def __init__(self,connection,peer_id):
        self.connection = connection
        self.peer_id = peer_id
    def send(self,id,data,part,partmax):
        width = 2560 # make more optimal!
        height = 2048
        file=image_coding.encode_bw(id,data,width,height,part,partmax)
        uploader = vk_api.upload.VkUpload(self.connection)
        photo_id = uploader.photo_messages(file)[0]
        api = self.connection.get_api()
        message_id = api.messages.send(peer_id=self.peer_id,attachment=f'photo{ photo_id["owner_id"] }_{ photo_id["id"] }')
        return json.dumps({'message':message_id,'photo':photo_id})
    def remove(self,id):
        id = json.loads(id)
        api = self.connection.get_api()
        try:
            api.messages.delete(message_ids=str(id['message']),delete_for_all=1)
        except:
            pass
        api.photos.delete(photo_id=id['photo']['id'])
    def get_max_length(self):
        return 2560*(2048-5)


class VkWallImageReciever(common.Receiver):
    def __init__(self,connection,peer_id):
        super().__init__()
        self.connection = connection
        self.peer = peer_id
        data = self.connection.get_api().wall.get(owner_id=peer_id)
        self.last_received = data['items'][0]['id']
    def receive_once(self, manager):
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
                image_coding.decode_bw(i, manager)
            except:
                traceback.print_exc()

class VkWallVideoReceiver(common.Receiver):
    def __init__(self,connection,peer_id):
        super().__init__()
        self.connection = connection
        self.peer = peer_id
        data = self.connection.get_api().wall.get(owner_id=peer_id)
        self.last_received = data['items'][0]['id']
    def receive_once(self, manager):
        print(self.last_received)
        api = self.connection.get_api()
        post = api.wall.getById(posts=f'{self.peer}_{self.last_received+1}')
        if post==[]:
            return
        post=post[0]
        if 'attachments' not in post:
            return
        files=[]
        self.last_received+=1
        for i in post['attachments']:
            if i['type']=='video':
                try:
                    getobj = api.video.get(videos=str(i['video']['owner_id'])+'_'+str(i['video']['id']), extended=1)['items'][0]
                    with requests.get(getobj['player']) as r:
                        page = r.text
                    page = bs4.BeautifulSoup(page)
                    node = page.find("video")
                    urls=[j.get('src') for j in node.find_all('source')]
                    sizes=[(re.findall('videos.+\.\d+\.mp4',j)[0] if re.findall('videos.+\.\d+\.mp4',j) else 'videos/qqq.0.mp4') for j in urls]
                    sizes=[int(j.split('.')[1]) for j in sizes]
                    url=urls[sizes.index(max(sizes))]
                    filepath = f'/tmp/{uuid.uuid4().hex}.mp4'
                    with requests.get(url) as conn, open(filepath,'wb') as outp:
                        outp.write(conn.content)
                    files.append(filepath)
                except:
                    traceback.print_exc()
        for i in files:
            try:
                video_coding.decode_video(i, manager)
            except:
                traceback.print_exc()
        manager.collapse_full()
class VkChatImageReceiver(common.Receiver):
    def __init__(self,connection,peer_id):
        super().__init__()
        self.connection = connection
        self.peer = peer_id
        data = self.connection.get_api().messages.getHistory(peer_id=peer_id)
        self.last_received = data['items'][0]['id']
    def receive_once(self, manager):
        api = self.connection.get_api()
        files=[]
        for i in api.messages.getHistory(peer_id=self.peer)['items']:
            if i['id']>self.last_received:
                self.last_received=i['id']
                if 'attachments' in i:
                    for q in i['attachments']:
                        if q['type']=='photo':
                            maxw=0
                            targeturl=''
                            for n in q['photo']['sizes']:
                                if n['width']>maxw:
                                    maxw=n['width']
                                    targeturl=n['url']
                            files += [f'/tmp/{uuid.uuid4().hex}.jpg']
                            with requests.get(targeturl) as r:
                                with open(files[-1],'wb') as o:
                                    o.write(r.content)
        for i in files:
            try:
                image_coding.decode_bw(i, manager)
            except:
                traceback.print_exc()
