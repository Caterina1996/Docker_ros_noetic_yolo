#!/bin/bash

WORKSPACE_DIR="/home/rosuser/repo/src/DL_utils/ros_dl_ws/"

# Check if workspace needs to be initialized
if [ ! -d "$WORKSPACE_DIR/src" ]; then
    echo "════════════════════════════════════════════════════════════════"
    echo "  Initializing Stonefish workspace (first run only)"
    echo "════════════════════════════════════════════════════════════════"
    
    mkdir -p "$WORKSPACE_DIR/src"
    cd "$WORKSPACE_DIR"
    
    # Initialize catkin workspace
    source /opt/ros/noetic/setup.bash
    echo "Initializing catkin workspace..."
    catkin init
    
    # Clone the repositories
    cd "$WORKSPACE_DIR/src"
    
        
    # Build the workspace
    cd "$WORKSPACE_DIR"
    echo ""
    echo "Building workspace (this may take a few minutes)..."
    catkin build
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Workspace initialized successfully!"
    echo "  Location: $WORKSPACE_DIR"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
else
    echo "Stonefish workspace already exists at $WORKSPACE_DIR"
    echo "Building workspace (this may take a few minutes)..."
    catkin build
fi

# Source ROS environment
source /opt/ros/noetic/setup.bash

# Source the workspace if it exists and is built
if [ -f "$WORKSPACE_DIR/devel/setup.bash" ]; then
    source "$WORKSPACE_DIR/devel/setup.bash"
    echo "Stonefish workspace sourced and ready!"
fi

# Execute the command
exec "$@"
