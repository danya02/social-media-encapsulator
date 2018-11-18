#!/usr/bin/python3
import pygame
import textwrap
import uuid

# from https://stackoverflow.com/a/312464/5936187
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
def write_line(surface,line,data,integer=True,rjust=True):
    '''Write some data to a line on a surface. If integer is true, data is assumed to be an int, else a bitstring.'''
    if integer:
        data=bin(data)[2:]
    if rjust:
        data=data.rjust(surface.get_width(),'0')
    else:
        data=data.ljust(surface.get_width(),'0')
    for x,b in enumerate(data):
        if b=='1':
            surface.set_at((x,line),pygame.Color('white'))

def encode_single_page(item_id,data,width,height, part_num, max_part_num):
    if height<=5:
        raise ValueError('Height must be at least 6.')
    if width*(height-5)<len(data):
        raise IndexError('Height and width not enough for data; increase image size or decrease size of data.')
    bitstring = bin(int(data.hex(),16))[2:]
    pagelength=len(bitstring) # number of bits on this page
    pagelength=bin(pagelength)[2:].rjust(2*width,'0')
    pagelength=textwrap.wrap(pagelength,width)
    bitstring = textwrap.wrap(bitstring,width) # split by lines
    surface = pygame.Surface((width,height))
    write_line(surface, 0, item_id)
    write_line(surface, 1, part_num)
    write_line(surface, 2, max_part_num)
    write_line(surface, 3,pagelength[0],False)
    write_line(surface, 4,pagelength[1],False)
    for n,i in enumerate(bitstring):
        write_line(surface, 5+n, i, integer=False, rjust=False)
    uid=uuid.uuid4().hex
    f=f'/tmp/{uid}.png'
    pygame.image.save(surface,f)
    return f

def read_line(surface,line):
    '''Read a bitstring from a line from a surface.'''
    data=''
    for i in range(surface.get_width()):
        c=surface.get_at((i,line))
        if (c.r+c.g+c.b)>127*3:
            data+='1'
        else:
            data+='0'
    return data

def split_by_ids(files):
    '''Take a list of files and return a dict with keys of ids and values of files that are related to the id.'''
    surfaces={}
    for i in files:
        surfaces.update({i:pygame.image.load(i)})
    items={}
    for i in surfaces:
        id=int(read_line(surfaces[i],0),2)
        items.update({id:items.get(id,[])+[i]})
    return items

def decode_single_page(file):
    surface = pygame.image.load(file)
    id = int(read_line(surface,0),2)
    page_num = int(read_line(surface,1),2)
    last_page_num = int(read_line(surface,2),2)
    piece_len = int(read_line(surface,3)+read_line(surface,4),2)
    bitstring=''
    for n in range(5,surface.get_height()):
        bitstring+=read_line(surface,n)
    bitstring = bitstring[:piece_len]
    data = bytes.fromhex(hex(int(bitstring,2))[2:])
    return id,data,page_num,last_page_num



if __name__=='__main__':
    #files=encode(int('1010101010',2),b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',64,64)
    width,height=input('width and height separated by space: ').split()
    width,height=int(width),int(height)
    id=int(input('message id: '))
    if input('the letter "f" for file, any else for text: ')=='f':
        files=encode(id,open(input('file name: '),'rb').read(),width,height)
    else:
        files=encode(id,bytes(input('text: '),'utf-8'),width,height)
    print(files)
