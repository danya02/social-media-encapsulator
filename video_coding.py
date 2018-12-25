import qr_coding
import os
import uuid
import base64
import multiprocessing
import string
import gzip
import math

# from https://stackoverflow.com/a/312464/5936187
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def create_video(id,data,part,maxpart):
    datalist=[]
    size = math.ceil(len(data)/256)
    for n,i in enumerate(chunks(data,256)):
        datalist.append(f"{id}:{part}:{n}:{size}:{maxpart}:{str(base64.b64encode(gzip.compress(i,9)),'utf-8')}")
    return create_video_from_data(datalist)

def create_video_from_data(datalist):
    dir=f'/tmp/video/{uuid.uuid4().hex}/'
    os.makedirs(dir)
    q=multiprocessing.Queue()
    files=[f'{dir}{i}.png' for i in range(len(datalist))]
    concat='\n'.join([f"file '{i}'\nduration 1" for i in files])
    with open(f'{dir}concat.txt','w') as o:
        o.write(concat)
        o.write(f"\nfile '{files[-1]}'")
    for i,j in enumerate(datalist):
        q.put((i,j,))
    def qwork(q):
        while not q.empty():
            print(q.qsize())
            i,j=q.get_nowait()
            qr_coding.encode_qr(j,f'{dir}{i}.png')
    ps=[multiprocessing.Process(target=qwork, args=(q,)) for i in range(8)]
    for i in ps:i.start()
    for i in ps:i.join()

    os.popen(f'ffmpeg -f concat -safe 0 -r 10 -i {dir}concat.txt -vsync vfr -r 10 {dir}combined.mp4').read()
    return f'{dir}combined.mp4'

def combine_video(files):
    dir=f'/tmp/video/{uuid.uuid4().hex}/'
    os.makedirs(dir)
    concat='\n'.join([f"file '{i}'\nduration 1" for i in files])
    with open(f'{dir}concat.txt','w') as o:
        o.write(concat)
        o.write(f"\nfile '{files[-1]}'")

    os.popen(f'ffmpeg -f concat -safe 0 -r 10 -i {dir}concat.txt -vsync vfr -r 10 {dir}combined.mp4').read()
    return f'{dir}combined.mp4'

def split_video(video):
    dir=f'/tmp/video/{uuid.uuid4().hex}/'
    os.makedirs(dir)
    os.popen(f'ffmpeg -y -i "{video}" -f image2 {dir}%d.png').read()
    return [(dir+i) for i in sorted(os.listdir(dir),key=lambda x:int(x.split('.')[0]))]

def read_frames(files):
    filearr=qr_coding.decode_many_qr(files)
    print(filearr)
    data=dict()
    id,part,maxpart,vidpart,vidmaxpart,encdata = filearr[0].split(':')
    for i in filearr:
        nid,npart,nmaxpart,vidpart,nvidmaxpart,encdata = i.split(':')
        if nid!=id or npart!=part or nmaxpart!=maxpart or nvidmaxpart!=vidmaxpart:
            raise AssertionError('Value assumed constant inside video changed from first frame') # TODO: Make this not necessary

        data.update({int(vidpart):gzip.decompress(base64.b64decode(bytes(encdata,'utf-8')))}
    datastr=b''
    for i in range(vidmaxpart):
        datastr+=data[i]
    print(id,data,part,maxpart)
    return id,data,part,maxpart

def decode_video(file):
    return read_frames(split_video(file))
