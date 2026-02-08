#!/bin/bash

# mouseReMoCo launcher script
# Activates the mouseremoco conda environment and starts the app
# Can be run from any directory

# Repository location - CHANGE THIS to your mouseReMoCo repository path
REPO_DIR="/path/to/your/mouseReMoCo"

# Get the directory where this script is located (data will be saved here)
WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the Python app entry point
APP_PATH="$REPO_DIR/python/main.py"

echo "================================================"
echo "        mouseReMoCo Launcher"
echo "================================================"
echo ""
echo "Repository: $REPO_DIR"
echo "Data folder: $WORK_DIR"
echo ""

# Check if the app file exists
if [ ! -f "$APP_PATH" ]; then
    echo "❌ Error: Repository not found at $REPO_DIR"
    echo "Please edit this script and update REPO_DIR to the correct path"
    exit 1
fi

echo "✓ Found main.py"
echo ""

# Initialize conda (only needed on first run in fresh shell)
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    eval "$(conda shell.bash hook)"
fi

# Check if mouseremoco environment exists
if ! conda env list | grep -q "^mouseremoco"; then
    echo "❌ Error: 'mouseremoco' conda environment not found"
    echo "Please create it first by running:"
    echo "  cd $REPO_DIR/python"
    echo "  conda env create -f environment.yml"
    exit 1
fi

echo "✓ Found conda environment: mouseremoco"
echo ""
echo "Launching application..."
echo "================================================"
echo ""

# Change to work directory and run the app with unbuffered output
cd "$WORK_DIR"
conda run -n mouseremoco python -u "$APP_PATH"

echo ""
echo "================================================"

# Archive data files with timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
if [ -f "data.csv" ]; then
    cp "data.csv" "data_${TIMESTAMP}.csv"
    echo "✓ Archived: data_${TIMESTAMP}.csv"
fi
if [ -f "marker.csv" ]; then
    cp "marker.csv" "marker_${TIMESTAMP}.csv"
    echo "✓ Archived: marker_${TIMESTAMP}.csv"
fi

echo "================================================"
echo "Application closed"
echo "Data folder: $WORK_DIR"
echo "================================================"
