#!/usr/bin/env python3
# Provided under the MIT License
# Copyright (c) 2016 Ben Wiederhake

from PIL import Image
from math import floor, ceil
import itertools


def get_raw(fp):
    return Image.open(fp)


def tween_val(v1, v2, weight, r=round):
    return r(v1 * (1 - weight) + v2 * weight)


def tween_size(s1, s2, weight):
    w1, h1 = s1
    w2, h2 = s2
    return (tween_val(w1, w2, weight, ceil),
            tween_val(h1, h2, weight, ceil))

def tween_matching(col1, col2, weight):
    return (tween_1(comp1, comp2, weight)
            for comp1, comp2 in zip(col1, col2))


def tween_mode(mode1, mode2):
    # Apparently full list of modes:
    # http://svn.effbot.org/public/tags/pil-1.1.4/libImaging/Unpack.c
    # I don't wanna be able to merge that automatically.
    # So, if there's any conflict, fail.
    # TODO:  Maybe auto-merge to "the longer one"?
    # This way, at least L and RGB and RGBA would work out.
    assert mode1 == mode2, "Only identical modes supported."
    if len(mode1) == 1:
        return (mode1, tween_val)
    else:
        return (mode1, tween_matching)


def tween_get(img, pt):
    """x and y are floating point in the range [0,1]"""
    img_pt = tuple((floor(part * domain) for part, domain in zip(pt, img.size)))
    return img.getpixel(img_pt)


def merge(img1, img2, weight=0.5):
    mode, tween = tween_mode(img1.mode, img2.mode)
    size = tween_size(img1.size, img2.size, weight)
    img = Image.new(mode, size)
    for x, y in itertools.product(range(size[0]), range(size[1])):
        pt = (x / size[0], y / size[1])
        px = tween(tween_get(img1, pt), tween_get(img2, pt), weight)
        img.putpixel((x, y), px)
    return img
