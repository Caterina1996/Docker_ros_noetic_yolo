# Start from the official ROS Noetic desktop image (with GUI tools)
FROM osrf/ros:noetic-desktop-full

# Set build-time arguments for user and group IDs
ARG UID=1000
ARG GID=1000

# Set environment variables:
# - DEBIAN_FRONTEND=noninteractive: avoid interactive prompts during package
#   install
# - TZ: set timezone
# - ROS_WORKSPACE: default workspace directory
# - QT_X11_NO_MITSHM=1: fix for some Qt/X11 shared memory issues in Docker
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    ROS_WORKSPACE=/home/rosuser/project \
    QT_X11_NO_MITSHM=1

# Install system dependencies:
# - python3-pip: for Python package management
# - X11 and Qt libraries: for GUI and visualization tools
# - x11-xserver-utils, xauth: X11 authentication utilities
# - Clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    python3-pip \
    libx11-xcb1 libxcb1 libxcb-glx0 \
    libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-icccm4 \
    libxcb-sync1 libxcb-xfixes0 libxcb-shape0 libxcb-randr0 \
    libxcb-render-util0 libxcb-render0 libxcb-xinerama0 \
    libxcb-xkb1 libxkbcommon-x11-0 \
    libsm6 libgl1-mesa-glx qt5-default \
    x11-xserver-utils xauth \
    x11-apps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a new user (rosuser) with specified UID/GID,
# create the workspace directory, and set ownership
RUN groupadd -g $GID rosuser && \
    useradd -m -u $UID -g $GID -s /bin/bash rosuser && \
    mkdir -p $ROS_WORKSPACE && \
    chown -R rosuser:rosuser /home/rosuser

# Create a temporary Xauthority file for X11 forwarding,
# set permissions and ownership so the user can access it
RUN touch /tmp/.docker.xauth && \
    chmod 777 /tmp/.docker.xauth && \
    chown rosuser:rosuser /tmp/.docker.xauth

# Copy Python requirements file into the image
COPY requirements_py38.txt /tmp/requirements_py38.txt

# Switch to non-root user for security and proper file permissions
USER rosuser
WORKDIR $ROS_WORKSPACE

# Install Python dependencies as the non-root user
RUN python3 -m pip install --user -r /tmp/requirements_py38.txt

# Add ROS setup and local user bin to the shell initialization file
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc && \
    echo "export PATH=\$PATH:/home/rosuser/.local/bin" >> ~/.bashrc

# Start a Bash shell with ROS environment loaded
CMD ["/bin/bash", "--init-file", "/opt/ros/noetic/setup.bash"]
