#!/usr/bin/python3
import pygame

pygame.init()


def get_bytes_from_color(color: pygame.Color) -> bytes:
    return bytes.fromhex(
        hex(color.r)[2:].rjust(2, "0") + hex(color.g)[2:].rjust(2, "0") + hex(color.b)[2:].rjust(2, "0"))


def decode(file: pygame.Surface) -> (int, int, bytes, int, int):
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


if __name__ == "__main__":
    print(decode(pygame.image.load("test.png")))
