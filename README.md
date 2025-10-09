# Docker Development Environment for ROS (with Python 3.8) and Python 3.11

This repository provides a development environment with two Docker containers:
- A container with Python 3.11 to work with up-to-date libraries (e.g., Ultralytics)
- A container with Ubuntu 20.04 and Python 3.8 to work with ROS

Exported images (from rqt_image_view or other sources) can be redirected to the host you are using or directly to your local computer.

In this example, the Python 3.11 container comes with Ultralytics, but you can install any other package as needed.

## Folder Structure

This folder has the following structure:
```
repo
  |___ dataset
  |___ src
  |___ docker-compose.yml
  |___ Dockerfile
  |___ Dockerfile.py311
  |___ README.txt
  |___ requirements_py38.txt
  |___ requirements_py311.txt
  |___ .env
```

It may contain other folders, but this is the basic setup. Here is what each item is for:
`dataset`: Empty folder locally, mapped to the dataset specified in the DATASET_PATH environment variable
`src`: Contains all project code.
`docker-compose.yml`: The file used by docker compose to launch the system. Do not modify it.
`Dockerfile`: The file that builds the ros-noetic image. Do not modify it.
`Dockerfile.py311`: The file that builds the python311 image. Do not modify it.
`requirements_py38.txt`: Python requirements file for the ROS container. If you need more libraries, add them here.
`requirements_py311.txt`: Same as above but for the python311 container.
`.env`: The file where environment variables are defined.

## Initial Setup

To implement this setup in a new project, copy the following items to your project folder:

- `docker-compose.yml`
- `Dockerfile` and `Dockerfile.py311`
- `requirements_py311.txt` and `requirements_py38.txt`
- Environment variables file `.env`
- Empty folder named `dataset`
- `src` folder for your code

## Environment Variables

Configure the `.env` file with the following variables:

- `PROJECT_NAME`: Project name that determines the container names (e.g., if you use `foo`, the containers will be `foo-ros` and `foo-py311`, and the network will be `foo-app-network`)
- `DATASET_PATH`: Path where the dataset is stored on the host (e.g., `/home/azken/bagfiles/CABRERA`). It is mounted as read-only in the containers
- `CONTAINER_DISPLAY`: Value of the DISPLAY variable to export images
  - With AnyDesk: usually `:1`
  - With SSH: Use the host IP address with the port you prefer from 15 to 50 (e.g., `172.28.5.42:30`, example choosing port 30). Remember this choice.

## SSH Configuration for Visualization

If this is your first time setting up this environment:

1. On your local computer, edit `~/.ssh/config` to enable X11 options. Specifically, enable ForwardX11,
ForwardX11Trusted and also remote forward.
For example, to connect to mafalda, it would look like this:
```
Host mafalda_azken
  HostName 172.28.5.42
  User azken
  RemoteForward *:6030 /tmp/.X11-unix/X1
  ForwardX11 yes
  ForwardX11Trusted yes
```
The RemoteForward option as defined is a little bit tricky. See that I'm hardcoding
the port 6030. I'm choosing 6030 because at the last step I chose port 30 at ssh connection.
This must be consistent. So you have to put here 60XX being XX your selected port above.
Furthermore, see that I'm mapping to X1 (at the end of the command). Carefull, if you do
in your local machine `echo $DISPLAY` and the output is :1, then it's ok; if the output
is :0, then choose X0.

2. On the host, verify that `/etc/ssh/sshd_config` has these settings:
```
GatewayPorts yes
X11Forwarding yes
X11DisplayOffset 10  # This is the default value. If it is commented out, that's fine.
X11UseLocalhost no
```
And then restart ssh (`systemctl restart ssh`)

3. Configure the host firewall (ufw) to allow image communication (if ufw is enabled):
```
$ ufw prepend allow proto tcp from 172.16.0.0/12 to any port 6000:6050
```
In the example above, ports 6000 to 6050 from the docker network are enabled. To find
the IP of the docker network, compare the output of `ip addr` with the containers up and down, but this rule covers all current and future Docker networks created by docker-compose so you shouldn't have any problem due to the firewall.

## Using the Development Environment

To start the environment:
```
$ docker compose up -d
```

This creates both containers and the network connecting them. Your project folder
is mounted at `/home/rosuser/project` inside the containers, and the dataset will
be at `/home/rosuser/project/dataset`. You can debug code step by step with VSCode.

To stop the environment:
```
$ docker compose down -v
```

When the system is stopped, the containers are removed, but any changes made are
preserved in the project folder on the host.

## Running Code Between Containers

To run code from the Python 3.11 container that executes in the ROS container, use `docker exec`.

Example:

```
# First, define the command to execute (this calls a script that uses rosbag)
command = f"python3 src/utils/extract_images_from_bag.py --bagfile_path {bagfile} --output_folder {extracted_images_path} --preprocess {do_preprocess}"

# Prepare the docker exec command (note that ROS_CONTAINER is a variable
# containing the name of the ros container)
docker_cmd = [
    "docker", "exec", ROS_CONTAINER, 
    "bash", "-c", f"source /opt/ros/noetic/setup.bash && {command}"
]

# Execute
process = subprocess.run(
    docker_cmd, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True
)
```

For more details, see the full example in `./src/main_test.py`.

