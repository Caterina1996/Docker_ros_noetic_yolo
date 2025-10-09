#!/usr/bin/env python3.8

import rosbag
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import argparse
import numpy as np


# INITIALIZATIONS: --------------------------------------------------------------------------
parser = argparse.ArgumentParser()
# parser.add_argument("--bagfile_path", "-bp", type=str, help="path where the bagfile is found",default="/home/azken/caterina/bagfiles/OBSEA_09_2024/selec_TO_PLOME/2024_09_24/10_18_24/stereo_camera_images_2024-09-24-10-18-24_0.bag")
parser.add_argument("--bagfile_path", "-bp", type=str, help="path where the bagfile is found",default='dataset/2024_09_20/15_53_18/stereo_camera_images_2024-09-20-15-53-18_0.bag')
# parser.add_argument("--output_folder", "-out",type=str, help="folder where the extracted images are stored", default="/home/azken/caterina/DATA/OBSEA_09_2024/selec_TO_PLOME/2024_09_24/10_18_24/0/processed_images/")
parser.add_argument("--output_folder", "-out",type=str, help="folder where the extracted images are stored", default='output/dataset/2024_09_20/15_53_18/0/original_images')
parser.add_argument("--preprocess",type=int, help="preprocess images before storing them or not", default=1)
# --------------------------------------------------------------------------------------------

args = parser.parse_args()

# Accessing arguments
bagfile_path = args.bagfile_path
output_folder = args.output_folder
image_processing = args.preprocess

print("APLYING PREPROCESS? ",image_processing)

# image_processing = False

print("APLYING PREPROCESS? ",image_processing)

image_topic="/stereo_ch3/left/image_raw"

bridge = CvBridge()

def preprocess_image_deep_sea(image, n_clahe=2):
  image = np.array(image)

  # Reduce red channel values
  image[:, :, 2] = image[:, :, 2]*0.6

  hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  # Extract the V channel
  v_channel = hsv_image[:, :, 2]

  # Apply CLAHE to V channel
  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
  for _ in range(n_clahe):
      v_channel = clahe.apply(v_channel)

  # Reconstruct image
  hsv_image[:, :, 2] = v_channel

  # Change colorspace to BGR
  image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

  # image = Image.fromarray(image)

  return image

def preprocess_image(image, n_clahe=1):
  image = np.array(image)

  # Reduce red channel values
#   image[:, :, 1] = image[:, :, 1]*0.6

  hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  # Extract the V channel
  v_channel = hsv_image[:, :, 2]

  # Apply CLAHE to V channel
  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
  for _ in range(n_clahe):
      v_channel = clahe.apply(v_channel)

  # Reconstruct image
  hsv_image[:, :, 2] = v_channel

  # Change colorspace to BGR
  image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

  # image = Image.fromarray(image)

  return image



# Abrir el archivo bag
with rosbag.Bag(bagfile_path, 'r') as bag:
    # Iterar sobre todos los mensajes del bagfile
    frame_counter=0
    print("Processing bagfile: ",bagfile_path )
    for topic, msg, t in bag.read_messages(topics=[image_topic]):

        try:

            # # Convert the raw image data to a NumPy array
            # img_array = np.frombuffer(self.images_data[key], dtype=np.uint8)

            # # Reshape the NumPy array to the image dimensions
            # # img_array = img_array.reshape((self.height, self.width))  # RAW image
            # img_array = img_array.reshape((self.height, self.width,3))  # COLOR image

            # if self.image_processing:
            # img_array = preprocess_image(img_array)

            # processed_images_RGB[key] = img_array[..., ::-1].copy()

            # # Convert BGR to RGB
            # img_array = img_array[..., ::-1]

            # # Create a PIL Image from the NumPy array
            # # pil_images.append(PIL.Image.fromarray(img_array, mode='L')) # RAW IMAGE
            # pil_images.append(PIL.Image.fromarray(img_array,mode='RGB')) # COLOR IMAGE


            # Convertir el mensaje de ROS Image a un formato de imagen OpenCV
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            print("Flag is ",image_processing," Is flag True? ",image_processing==1)
            if image_processing==1:
                print("I M PREPROCESSING THE IMAGE!!!")
                img_array = preprocess_image(cv_image)
                processed_images_RGB = img_array[..., ::-1].copy()
                img_array = img_array[..., ::-1]
                cv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # Convert back to BGR for OpenCV


            # Crear el nombre del archivo de salida
            timestamp = str(t.to_nsec())  # Usar el timestamp del mensaje para nombrar la imagen
            
            image_filename = os.path.join(output_folder,timestamp+".jpg")
            # image_filename = os.path.join(output_folder, "frame_"+str(frame_counter)+".jpg")
            
            # Guardar la imagen en un archivo
            cv2.imwrite(image_filename, cv_image)
            print("Saved image", image_filename)
            frame_counter+=1
        
        except Exception as e:
            print("Error when saving image: {}".format(e))
