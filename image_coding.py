#!/usr/bin/python3
import pygame
import textwrap
import uuid

# from https://stackoverflow.com/a/312464/5936187
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
def write_line_bw(surface,line,data,integer=True,rjust=True):
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

def write_line_color(surface,line,data,integer=True,rjust=True):
    if integer:
        data=bin(data)[2:]
    if rjust:
        data=data.rjust(surface.get_width(),'0')
    else:
        data=data.ljust(surface.get_width(),'0')
    colors={}
    for i in range(8):
        ii=bin(i)[2:].rjust(3,'0')
        colors.update({ii: pygame.Color(int(ii[0])*255,int(ii[1])*255,int(ii[2])*255)})
    for x,b in enumerate(chunks(data,3)):
        surface.set_at((x,line),colors[b.ljust(3,'0')])

def encode_bw(item_id,data,width,height, part_num, max_part_num):
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
    write_line_bw(surface, 0, item_id)
    write_line_bw(surface, 1, part_num)
    write_line_bw(surface, 2, max_part_num)
    write_line_bw(surface, 3,pagelength[0],False)
    write_line_bw(surface, 4,pagelength[1],False)
    for n,i in enumerate(bitstring):
        write_line_bw(surface, 5+n, i, integer=False, rjust=False)
    f=f'/tmp/{uuid.uuid4().hex}.png'
    pygame.image.save(surface,f)
    return f


def encode_color(item_id,data,width,height, part_num, max_part_num):
    if height<=5:
        raise ValueError('Height must be at least 6.')
    if width*(height-5)<len(data):
        raise IndexError('Height and width not enough for data; increase image size or decrease size of data.')
    bitstring = bin(int(data.hex(),16))[2:]
    pagelength=len(bitstring) # number of bits on this page
    pagelength=bin(pagelength)[2:].rjust(3*2*width,'0')
    pagelength=textwrap.wrap(pagelength,width*3)
    bitstring = textwrap.wrap(bitstring,width*3) # split by lines
    surface = pygame.Surface((width,height))
    write_line_color(surface, 0, item_id)
    write_line_color(surface, 1, part_num)
    write_line_color(surface, 2, max_part_num)
    write_line_color(surface, 3,pagelength[0],False)
    write_line_color(surface, 4,pagelength[1],False)
    for n,i in enumerate(bitstring):
        write_line_color(surface, 5+n, i, integer=False, rjust=False)
    f=f'/tmp/{uuid.uuid4().hex}.png'
    pygame.image.save(surface,f)
    return f


def read_line_bw(surface,line):
    '''Read a bitstring from a line from a surface.'''
    data=''
    for i in range(surface.get_width()):
        c=surface.get_at((i,line))
        if (c.r+c.g+c.b)>127*3:
            data+='1'
        else:
            data+='0'
    return data

def read_line_color(surface,line):
    data=''
    for i in range(surface.get_width()):
        c=surface.get_at((i,line))
        for q in [c.r,c.g,c.b]:
            if q>127:
                data+='1'
            else:
                data+='0'
    return data

def decode_bw(file):
    surface = pygame.image.load(file)
    id = int(read_line_bw(surface,0),2)
    page_num = int(read_line_bw(surface,1),2)
    last_page_num = int(read_line_bw(surface,2),2)
    piece_len = int(read_line_bw(surface,3)+read_line_bw(surface,4),2)
    bitstring=''
    for n in range(5,surface.get_height()):
        bitstring+=read_line_bw(surface,n)
    bitstring = bitstring[:piece_len]
    data = bytes.fromhex(hex(int(bitstring,2))[2:])
    return id,data,page_num,last_page_num

def decode_color(file):
    surface = pygame.image.load(file)
    id = int(read_line_color(surface,0),2)
    page_num = int(read_line_bw(surface,1),2)
    last_page_num = int(read_line_color(surface,2),2)
    piece_len = int(read_line_color(surface,3)+read_line_color(surface,4),2)
    bitstring=''
    for n in range(5,surface.get_height()):
        bitstring+=read_line_color(surface,n)
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
