#!/usr/bin/env python3.11

import numpy as np
from ultralytics import YOLO
import torch
import time
import cv2
from PIL import Image
from PIL import *

import os
import shutil
import csv
import argparse


"""
Call Example:

python inference_online.py --model_path /home/azken/caterina/trainings/binary/yv11_small_binary_and_POOL_no_vivo/weights/best.pt \
                           --images_path /home/azken/caterina/DATA/SARMIENTO/SARMIENTO/2023_12_19/21_02_56/3/original_images \
                           --project_path /home/azken/caterina/DATA/SARMIENTO/SARMIENTO/2023_12_19/21_02_56/3/yv11_small_binary_and_POOL_no_vivo/ \
                           --name inferred \
                           --conf 0.3

"""

DEBUG = True  #############################################################################################



# INITIALIZATIONS: --------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--model_path", type=str, help="path to the trained.pt")
parser.add_argument("--images_path",type=str, help="folder where the extracted images are stored")
parser.add_argument("--project_path", type=str, help="folder where the predictions info is stored")
parser.add_argument("--name", type=str, help="folder where the extracted inference are stored", default="inference")
parser.add_argument("--conf", type=float, help="confidence threshold", default=0.5)

args = parser.parse_args()

# Override with debug values when in debug mode
if DEBUG:
    args.model_path = 'weights/v11_seg_nano_25c.pt'  # 'weights/V11_seg_nano_25c.pt'
    args.images_path = 'output/dataset/2024_09_20/15_53_18/0/original_images'
    args.project_path = 'output/dataset/2024_09_20/15_53_18/0'
    args.conf = 0.15
    args.name = 'inference'

# Accessing arguments
model_path = args.model_path
images_path = args.images_path
project_path = args.project_path
name = args.name
conf = args.conf


# Load model
model = YOLO(model_path)

model_classes = model.names

print(model_classes)
inverted_class_dict = {value: key for key, value in model_classes.items()}


bagfile_detection_count = dict.fromkeys(model_classes.values(), 0)

bagfile_detection_count = {"Total_detections": 0, **bagfile_detection_count}

print("Species count initialization: ", bagfile_detection_count)

shape = 1280
frame_info = {}
header_written = False

in_images=os.listdir(images_path)
# results=model.predict(images_path, save=True,save_conf=True,project=project_path,name="inference",conf=0.35,agnostic_nms=True,imgsz=1280)

for img in os.listdir(images_path):
    
    image = os.path.join(images_path,img)

    results = model.predict(image, save=True, project=project_path, conf=conf, agnostic_nms=True, save_txt=True, save_conf=False, line_width=2, exist_ok=True, name=name,imgsz=shape)

    frame_id = img.split(".")[0]


    frame_info = dict.fromkeys(model_classes.values(), 0)
    
    frame_info = {"Num_detections": 0, **frame_info}
    frame_info = {"FrameId": frame_id, **frame_info}
    print("frame info: ", frame_info)

    bboxes= results[0].boxes
    masks= results[0].masks
    number_of_detections = len(bboxes)
    
    if number_of_detections > 0:

        for i in range(number_of_detections):
            # -------------------- CLASS --------------------
            
            cls = model_classes[int(bboxes.cls[i])]
                
            frame_info[cls] += 1
            bagfile_detection_count[cls] += 1

            frame_info["Num_detections"] +=1
            bagfile_detection_count["Total_detections"] +=1
        
    mode = 'w' if not header_written else 'a'

    with open(os.path.join(project_path, 'frame_data.csv'), mode, newline='') as csvfile:
        fieldnames = frame_info.keys()  # Column names
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only for the first iteration
        if not header_written:
            writer.writeheader()
            header_written = True

        # Write data for each iteration
        writer.writerow(frame_info)

with open(os.path.join(project_path, 'bagfile_data.csv'), 'w', newline='') as csvfile:
    fieldnames = ['Class', 'Total Count']  # Column names
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for key, value in bagfile_detection_count.items():
        writer.writerow({'Class': key, 'Total Count':value})


