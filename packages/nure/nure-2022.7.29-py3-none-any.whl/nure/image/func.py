import math
import os
import struct

import cv2
import numpy as np

from . import annotate


def _apply_mask(matrix, mask, fill_value):
    masked = np.ma.array(matrix, mask=mask, fill_value=fill_value)
    return masked.filled()


def _apply_threshold(matrix, low_value, high_value):
    low_mask = matrix < low_value
    matrix = _apply_mask(matrix, low_mask, low_value)

    high_mask = matrix > high_value
    matrix = _apply_mask(matrix, high_mask, high_value)

    return matrix


def simplest_cb(img, percent):
    assert img.shape[2] == 3
    assert percent > 0 and percent < 100

    half_percent = percent / 200.0

    channels = cv2.split(img)

    out_channels = []
    for channel in channels:
        assert len(channel.shape) == 2
        # find the low and high precentile values (based on the input percentile)
        height, width = channel.shape
        vec_size = width * height
        flat = channel.reshape(vec_size)

        assert len(flat.shape) == 1

        flat = np.sort(flat)

        n_cols = flat.shape[0]

        low_val = flat[math.floor(n_cols * half_percent)]
        high_val = flat[math.ceil(n_cols * (1.0 - half_percent))]

        # saturate below the low percentile and above the high percentile
        thresholded = _apply_threshold(channel, low_val, high_val)
        # scale the channel
        normalized = cv2.normalize(
            thresholded, thresholded.copy(), 0, 255, cv2.NORM_MINMAX)
        out_channels.append(normalized)

    return cv2.merge(out_channels)


def unpad(image):
    pad_color = image[0, 0]
    # top
    top = 0
    while True:
        if not np.all(image[top] == pad_color):
            break
        top += 1

    # left
    left = 0
    while True:
        if not np.all(image[:, left] == pad_color):
            break
        left += 1

    # top
    bottom = -1
    while True:
        if not np.all(image[bottom] == pad_color):
            break
        top -= 1

    # left
    right = -1
    while True:
        if not np.all(image[:, right] == pad_color):
            break
        right -= 1

    return image[top:bottom, left:right, :]


def resize_keep_ratio(image, max_size, interpolation=cv2.INTER_AREA):
    h, w = np.shape(image)[:2]

    if h < w:
        h = int(max_size * h / w)
        w = max_size
    else:
        w = int(max_size * w / h)
        h = max_size

    image = cv2.resize(image, (w, h), interpolation=interpolation)
    return image


def create_mosaic(nImages, list_gt_boxes, list_gt_classes):
    """ create a mosaic image with 4 images and transform their groundtruth boxes
    """
    # the dtype
    image_dtype = nImages[0].dtype
    # compute center and width, hiehgt of combined image
    cy = max(nImages[0].shape[0], nImages[1].shape[0])
    height = cy + max(nImages[2].shape[0], nImages[3].shape[0])
    cx = max(nImages[0].shape[1], nImages[2].shape[1])
    width = cx + max(nImages[1].shape[1], nImages[3].shape[1])

    # paste 4 images into
    nBig = np.zeros((height, width, 3), dtype=image_dtype)
    nBig[cy - nImages[0].shape[0]:cy, cx - nImages[0].shape[1]:cx] = nImages[0]
    nBig[cy - nImages[1].shape[0]:cy, cx:cx + nImages[1].shape[1]] = nImages[1]
    nBig[cy:cy + nImages[2].shape[0], cx - nImages[2].shape[1]:cx] = nImages[2]
    nBig[cy:cy + nImages[3].shape[0], cx:cx + nImages[3].shape[1]] = nImages[3]

    # translate the bboxes according to their possition
    translated_gt_boxes = [
        annotate.translate_boxes(list_gt_boxes[0], (cy - nImages[0].shape[0], cx - nImages[0].shape[1])),
        annotate.translate_boxes(list_gt_boxes[1], (cy - nImages[1].shape[0], cx)),
        annotate.translate_boxes(list_gt_boxes[2], (cy, cx - nImages[2].shape[1])),
        annotate.translate_boxes(list_gt_boxes[3], (cy, cx))
    ]

    # merge bboxes and classes
    merged_gt_boxes = np.concatenate(translated_gt_boxes, axis=0).reshape(-1, 4)
    merged_gt_classes = np.concatenate(list_gt_classes, axis=0)

    return nBig, merged_gt_boxes, merged_gt_classes


def is_joeg(bytes):
    return bytes[:2] == b'\xff\xd8' and bytes[-2:] == b'\xff\xd9'


def get_image_size(file_path):
    """
    Return (width, height) for a given img file content - no external
    dependencies except the os and struct modules from core
    https://raw.githubusercontent.com/scardine/image_size/master/get_image_size.py
    """
    size = os.path.getsize(file_path)

    with open(file_path) as input:
        height = -1
        width = -1
        data = input.read(25)

        if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
            # GIFs
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n') and (data[12:16] == 'IHDR')):
            # PNGs
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
            # older PNGs?
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        elif (size >= 2) and data.startswith('\377\330'):
            # JPEG
            msg = " raised while trying to decode as JPEG."
            input.seek(0)
            input.read(2)
            b = input.read(1)
            try:
                w = 0
                h = 0
                while (b and ord(b) != 0xDA):
                    while (ord(b) != 0xFF):
                        b = input.read(1)
                    while (ord(b) == 0xFF):
                        b = input.read(1)
                    if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                        input.read(3)
                        h, w = struct.unpack(">HH", input.read(4))
                        break
                    else:
                        input.read(int(struct.unpack(">H", input.read(2))[0]) - 2)
                    b = input.read(1)
                width = int(w)
                height = int(h)
            except struct.error:
                raise Exception("StructError" + msg)
            except ValueError:
                raise ValueError("ValueError" + msg)
            except Exception as e:
                raise Exception(e.__class__.__name__ + msg)
        else:
            raise Exception(
                "Sorry, don't know how to get information from this file."
            )

    return width, height
