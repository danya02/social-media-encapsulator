#!/usr/bin/python3
import pygame
import gzip

pygame.init()


def get_bytes_from_color(color: pygame.Color) -> bytes:
    return bytes.fromhex(
        hex(color.r)[2:].rjust(2, "0") + hex(color.g)[2:].rjust(2, "0") + hex(color.b)[2:].rjust(2, "0"))


def decode_old(file: pygame.Surface) -> (int, int, bytes, int, int):
    obj = bytes()
    colorline = []
    for y in range(file.get_height() - 1):
        for x in range(file.get_width()):
            colorline.append(file.get_at((x, y + 1)))
    for i in colorline:
        obj += get_bytes_from_color(i)
    lengthline = [file.get_at((i + 16, 0)) for i in range(16)]
    lengthline = [get_bytes_from_color(i) for i in lengthline]
    length = bytes()
    for i in lengthline:
        length += i
    length = int(length.hex(), 16)
    obj = obj[:length - 1]

    idline = [file.get_at((i, 0)) for i in range(8)]
    idline = [get_bytes_from_color(i) for i in idline]
    id = bytes()
    for i in idline:
        id += i
    id = int(id.hex(), 16)

    thispartline = [file.get_at((i + 8, 0)) for i in range(4)]
    thispartline = [get_bytes_from_color(i) for i in thispartline]
    thispart = bytes()
    for i in thispartline:
        thispart += i
    thispart = int(thispart.hex(), 16)

    maxpartline = [file.get_at((i + 12, 0)) for i in range(4)]
    maxpartline = [get_bytes_from_color(i) for i in maxpartline]
    maxpart = bytes()
    for i in maxpartline:
        maxpart += i
    maxpart = int(maxpart.hex(), 16)
    return id, length, obj, thispart, maxpart


def get_line(obj: pygame.Surface, line: int) -> [pygame.Color]:
    outp = []
    for i in range(obj.get_width()):
        outp.append(obj.get_at((i, line)))
    return outp


def binarize_line(obj: [pygame.Color]) -> [bool]:
    outp = []
    for i in obj:
        if (i.r + i.g + i.b) / 3 >= 127:
            outp.append(True)
        else:
            outp.append(False)
    return outp


def list_to_int(obj: [bool]) -> int:
    outp = [str(int(i)) for i in obj]
    outp = "".join(outp)
    return int(outp, 2)


def decode(file: pygame.Surface) -> (int, int, bytes, int, int):
    obj_id = list_to_int(binarize_line(get_line(file, 0)))
    numthis = list_to_int(binarize_line(get_line(file, 1)))
    nummax = list_to_int(binarize_line(get_line(file, 2)))
    length = list_to_int(binarize_line(get_line(file, 3)) + binarize_line(get_line(file, 4)))
    blob = []
    for i in range(file.get_height() - 5):
        blob += binarize_line(get_line(file, i + 5))
    blob = hex(list_to_int(blob))[2:]
    blob = (blob + "0") if len(blob) % 2 == 1 else blob
    blob = bytes.fromhex(blob)
    blob = blob[:length]
    return obj_id, length, blob, numthis, nummax


if __name__ == "__main__":
    obj = decode(pygame.image.load("test.png"))
    if obj[2][0] == 31:
        print(gzip.decompress(obj[2]))
    else:
        print(obj)
