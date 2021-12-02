import os
import re
import subprocess, json
from typing import NewType
import cv2
from pathlib import Path
import numpy as np 
import boto3
import base64
import requests
import json 

import storage_service

interim_store = storage_service.get_interim_store()


DETECTRON2_ENDPOINT = os.environ.get("DETECTRON2_ENDPOINT")

def get_bounding_box_from_torchserve_response(response_json, input_img, orig_dims, small_dims, padding=0):

    # f = open('test_log.txt', 'w')
    # f.write(f'origin dims {orig_dims}\n')
    # f.write(f'small dims {small_dims}\n')

    # if prediction fails, make entire image the bounding box
    if 'boxes' not in response_json.keys() or len(response_json['boxes']) == 0:
        print(f'Bounding box prediction failed. Response: {response_json}')
        return {'x1': 0, 'y1': 0, 'x2': input_img.shape[1], 'y2': input_img.shape[0]}

    # otherwise, find containing box
    x1, y1, x2, y2 = small_dims[1], small_dims[0], 0, 0
    for idx in range(len(response_json['boxes'])):
        _x1, _y1, _x2, _y2 = list(map(int, response_json['boxes'][idx]))
        x1 = min(x1, _x1)
        y1 = min(y1, _y1)
        x2 = max(x2, _x2)
        y2 = max(y2, _y2)

    # f.write(f'small x1 {x1}\n')
    # f.write(f'small x2 {x2}\n')
    # f.write(f'small y1 {y1}\n')
    # f.write(f'small y2 {y2}\n')

    # convert back to image coordinates of the original image
    x1 = int( x1 * orig_dims[1] / small_dims[1])
    x2 = int( x2 * orig_dims[1] / small_dims[1])
    y1 = int( y1 * orig_dims[0] / small_dims[0])
    y2 = int( y2 * orig_dims[0] / small_dims[0])

    # f.write(f'scale_ratio w {orig_dims[1] / small_dims[1]}\n')
    # f.write(f'scale_ratio h {orig_dims[0] / small_dims[0]}\n')

    # f.write(f' x1 {x1}\n')
    # f.write(f' x2 {x2}\n')
    # f.write(f' y1 {y1}\n')
    # f.write(f' y2 {y2}\n')

    # f.close()

    # account for padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(input_img.shape[1], x2 + padding)
    y2 = min(input_img.shape[0], y2 + padding)

    return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}


def image_resize(unique_id, largest_dim = 400, inter = cv2.INTER_AREA):
    
    # READ image.png S3 OBJECT as BYTES

    image_obj = interim_store.read_bytes(unique_id, 'image.png')
    image = cv2.imdecode(np.asarray(bytearray(image_obj)), cv2.IMREAD_COLOR)
  
    (h, w) = image.shape[:2]

    if h >= w:
        max_dim = h
    else:
        max_dim = w

    if max_dim <= largest_dim:
        return image, (h, w), (h, w), image

    scale = largest_dim  / max_dim

    reduced_size = (int( h * scale), int(w * scale))

    resized_img = cv2.resize(image, (reduced_size[1], reduced_size[0]), interpolation = inter)
    
    return resized_img, (h, w), reduced_size, image

def detect_humanoids(unique_id):

    resized_img, orig_dims, small_dims, input_img = image_resize(unique_id)

    _, resized_img_buf  = cv2.imencode('.png', resized_img)

    response = requests.post(url=DETECTRON2_ENDPOINT, data=resized_img_buf.tobytes())

    bb_response = response.json()
    bb = get_bounding_box_from_torchserve_response(bb_response, input_img, orig_dims, small_dims, 25)
    
    # Serializing json  
    json_object = json.dumps(bb, indent = 4) 
    interim_store.write_bytes(unique_id, "bb.json", bytearray(json_object, "ascii"))
    
    cropped_img = input_img[bb['y1']:bb['y2'], bb['x1']:bb['x2'], :]
    interim_store.write_bytes(unique_id, 'cropped_image.png', storage_service.np_to_png_bytes(cropped_img))

