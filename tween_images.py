#!/usr/bin/env python3
# Provided under the MIT License
# Copyright (c) 2016 Ben Wiederhake

from PIL import Image
from math import floor, ceil
from os import path
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
    return tuple((tween_val(comp1, comp2, weight)
                  for comp1, comp2 in zip(col1, col2)))


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


def tween_images(from_image, to_image, frames=5):
    assert frames >= 2
    img_list = [from_image]
    for i in range(max(0, frames - 1)):
        img_list.append(merge(from_image, to_image, (i + 1) / (frames - 1)))
    img_list.append(to_image)
    return img_list


def fmt_defs(fpath, prefix, fmt_dict):
    fmt_dict[prefix] = path.abspath(fpath)
    fmt_dict[prefix + '_dir'] = path.dirname(fmt_dict[prefix])
    base = path.basename(fmt_dict[prefix])
    fmt_dict[prefix + '_base'] = base
    fmt_dict[prefix + '_base_root'], fmt_dict[prefix + '_base_ext'] = \
        path.splitext(base)


def gen_filenames(from_file, to_file, frames, pattern=None):
    if pattern is None:
        pattern = '{to_dir}/{i}_of_{n}_-_{from_base_root}_{to_base_root}{to_base_ext}'

    fmt_args = {'n': frames}
    fmt_defs(from_file, 'from', fmt_args)
    fmt_defs(to_file, 'to', fmt_args)
    for i in range(frames):
        yield pattern.format(i=i, **fmt_args)


def tween_files(from_file, to_file, frames=5, pattern=None):
    """'pattern' may contain any of the following:
    {from}: the abspath() of the from_file
    {from_dir}: the dirname() of the from_file ('/path/to/dir')
    {from_base}: the basename() of the from_file ('myfile.png')
    {from_base_root}: the basename() of the from_file ('myfile')
    {from_base_ext}: the basename() of the from_file ('.png')
    {to*}: same with the to_file
    {i}: index of 'this' file
    {n}: amount of files (remember that 'i/n' is a bad idea)
    The format mini-language is available.
    ( https://docs.python.org/3/library/string.html#formatspec )

    The default pattern is:
        '{to_dir}/{i}_of_{n}_-_{from_base_root}_{to_base_root}{to_base_ext}'
    This should usually do what you expect.
    It is used whenever the 'pattern' argument is 'None'."""
    assert frames >= 2

    from_img = Image.open(from_file)
    to_img = Image.open(to_file)
    for dst_path, img in zip(gen_filenames(from_file, to_file, frames, pattern),
                             tween_images(from_img, to_img, frames)):
        img.save(dst_path)
