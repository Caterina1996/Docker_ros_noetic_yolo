#!/usr/bin/env python3.11
import os
import glob
import subprocess
import sys
from natsort import natsorted
from dotenv import load_dotenv
import torch

print(f"CUDA available: {torch.cuda.is_available()}")

# Load environment variables from .env file
load_dotenv()

print("Debugging with:", sys.executable)

# Get ROS container name from environment variables
ROS_CONTAINER = os.getenv("PROJECT_NAME") + "-ros"
print(f"Using ROS container: {ROS_CONTAINER}")

# Parent folder containing the bagfiles to be processed
parent_bagfiles_path = "dataset"

# Output folder
base_out_path = "output"

# Initialize parameters
bagfiles = natsorted(glob.glob(parent_bagfiles_path + "/**/*.bag", recursive=True))
path_to_model = "weights/v11_seg_nano_25c.pt"
conf_thr = 0.15
inference_folder = "inference"
do_preprocess = 0

# Function to run commands in ROS container
def run_in_ros_container(command):
    """
    Execute a command in the ROS container.
    
    Args:
        command: The command to execute in the container
        
    Returns:
        The return code from the command execution
    """
    # Prepare the full docker exec command
    docker_cmd = [
        "docker", "exec", ROS_CONTAINER, 
        "bash", "-c", f"source /opt/ros/noetic/setup.bash && {command}"
    ]
    
    # Use subprocess for better error handling
    process = subprocess.run(
        docker_cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Print output for debugging
    print(f"Command exit code: {process.returncode}")
    if process.stdout:
        print(f"Output: {process.stdout}")
    if process.stderr:
        print(f"Error: {process.stderr}")
    
    return process.returncode

# Process each bagfile
for bagfile in bagfiles:
    ########################## EXTRACT IMAGES ##########################################################
    bagfile_hour = "/".join(bagfile.split("bagfiles/")[-1].split("/")[:-1])
    bagfile_num = bagfile.split("_")[-1].split(".")[0]
    processed_dir = os.path.join(base_out_path, bagfile_hour, bagfile_num)
    extracted_images_path = os.path.join(processed_dir, "original_images")
    
    # Create output directory if it doesn't exist
    os.makedirs(extracted_images_path, exist_ok=True)
    
    # Run Python 3.8 script in ROS container
    # Since both containers mount the same paths, we can use the same paths
    process_bags_cmd = f"python3 src/utils/extract_images_from_bag.py --bagfile_path {bagfile} --output_folder {extracted_images_path} --preprocess {do_preprocess}"
    
    print(f"Running in ROS container: {process_bags_cmd}")
    result = run_in_ros_container(process_bags_cmd)
    
    if result != 0:
        print(f"Error processing bagfile {bagfile}")
        continue
    
    ########################## INFERENCE ##########################################################
    # These commands run in the current container (py311-dev)
    inference_path = os.path.join(processed_dir, inference_folder)
    inference_cmd = f"python3.11 src/utils/inference_offline.py --model_path {path_to_model} --images_path {extracted_images_path} --project_path {processed_dir} --conf {conf_thr} --name {inference_folder}"
    
    print(f"Running locally: {inference_cmd}")
    os.system(inference_cmd)

# Unify CSVs - runs in the current container (py311-dev)
unify_csvs_cmd = f"python3.11 src/utils/unify_offline_process_csvs.py --root_dir {base_out_path}"
print(f"Running locally: {unify_csvs_cmd}")
os.system(unify_csvs_cmd)

print("TEST PASSED!")
