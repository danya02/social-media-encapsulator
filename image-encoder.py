#!/usr/bin/python3
import pygame
import os


def get_color(value: int) -> pygame.Color:
    value = hex(value)[2:]
    value = "0" * (6 - len(value)) + value
    return pygame.Color("#" + value)


def get_string_of_colors(value: int, maxlen: int) -> [pygame.Color]:
    value = bin(value)[2:]
    value = [value[i:i + 2] for i in range(0, len(value), 2)]
    value = [int(i, 16) for i in value]
    value = [value[i:i + 3] for i in range(0, len(value), 3)]
    color_value = []
    for i in value:
        if len(i) == 3:
            color_value.append(pygame.Color(i[0], i[1], i[2]))
        if len(i) == 2:
            color_value.append(pygame.Color(0, i[0], i[1]))
        if len(i) == 1:
            color_value.append(pygame.Color(0, 0, i[0]))

    color_value = ([get_color(0)] * (maxlen - len(color_value))) + color_value
    return color_value


def list_to_hex(value: list) -> str:
    if len(value) == 0:
        return "000000"
    if len(value) == 1:
        return "0000" + hex(value[0])[2:]
    if len(value) == 2:
        return "00" + hex(value[0])[2:] + hex(value[1])[2:]
    if len(value) == 3:
        return hex(value[0])[2:] + hex(value[1])[2:] + hex(value[2])[2:]


def encode(obj_id: int, obj: bin, x: int, y: int, part_this: int, part_max: int) -> pygame.Surface:
    s = pygame.Surface((x, y + 1))
    length = len(obj)
    c_length = get_string_of_colors(length, 16)
    c_obj_id = get_string_of_colors(obj_id, 8)
    c_part_this = get_string_of_colors(part_this, 4)
    c_part_max = get_string_of_colors(part_max, 4)

    for i, j in enumerate(c_obj_id):
        s.set_at((i, 0), j)
    for i, j in enumerate(c_part_this):
        s.set_at((i + 8, 0), j)
    for i, j in enumerate(c_part_max):
        s.set_at((i + 12, 0), j)
    for i, j in enumerate(c_length):
        s.set_at((i + 16, 0), j)

    obj = obj.hex()
    obj = [obj[i:i + 2] for i in range(0, len(obj), 2)]
    obj = [int(i, 16) for i in obj]
    obj = [obj[i:i + 3] for i in range(0, len(obj), 3)]
    obj = [int(list_to_hex(i), 16) for i in obj]

    color_obj = [get_color(i) for i in obj]
    color_obj = [color_obj[i:i + x] for i in range(0, len(color_obj), x)]

    for i, j in enumerate(color_obj):
        for k, l in enumerate(j):
            s.set_at((k, i + 1), l)
    return s


if __name__ == "__main__":
    pygame.image.save(encode(0, os.urandom(16384), 100, 100, 1024, 2048), "test.png")
