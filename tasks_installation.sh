#!/bin/bash

# Set error handling
set -e  # Exit on first error
set -o pipefail  # Exit if any command in a pipeline fails

# Define installation paths
ROOT_DIR="$HOME/BioTasks"
ANTIFOLD_DIR="$ROOT_DIR/AntiFold"
LIGANDMPNN_DIR="$ROOT_DIR/LigandMPNN"
PROTEINMPNN_DDG_DIR="$ROOT_DIR/proteinmpnn_ddg"
TS_DIR="$ROOT_DIR/ThompsonSampling"  # Thompson Sampling directory

# Ensure ROOT_DIR exists
mkdir -p $ROOT_DIR

# Activate Conda
echo "=========================="
echo "Activating Conda..."
echo "=========================="
source ~/miniconda3/bin/activate || { echo "Conda activation failed"; exit 1; }
echo "Conda activated."

echo "=========================="
echo "Cloning Repositories..."
echo "=========================="

# Clone repositories if they don't exist
cd $ROOT_DIR
[[ ! -d "AntiFold" ]] && git clone https://github.com/oxpig/AntiFold.git
[[ ! -d "LigandMPNN" ]] && git clone https://github.com/dauparas/LigandMPNN.git
[[ ! -d "proteinmpnn_ddg" ]] && git clone https://github.com/PeptoneLtd/proteinmpnn_ddg.git
[[ ! -d "ThompsonSampling" ]] && git clone https://github.com/PatWalters/TS.git

echo "Repositories cloned successfully."


echo "=========================="
echo "Setting up AntiFold..."
echo "=========================="
cd $ANTIFOLD_DIR
conda create --name antifold python=3.10 -y
source ~/miniconda3/bin/activate antifold  # Activate environment
pip install -U pip
conda install -c conda-forge pytorch -y
pip install .
echo "AntiFold setup complete."


echo "=========================="
echo "Setting up LigandMPNN..."
echo "=========================="
cd $LIGANDMPNN_DIR
conda create -n ligandmpnn_env python=3.11 -y
source ~/miniconda3/bin/activate ligandmpnn_env  # Activate environment
pip install -U pip
pip install -r requirements.txt
bash get_model_params.sh "./model_params"
echo "LigandMPNN setup complete."


echo "=========================="
echo "Setting up ProteinMPNN-ddG..."
echo "=========================="
cd $PROTEINMPNN_DDG_DIR

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker before proceeding."
    exit 1
fi

# Pull the prebuilt Docker image
docker pull ghcr.io/peptoneltd/proteinmpnn_ddg:1.0.0_base
echo "ProteinMPNN-ddG setup complete."


echo "=========================="
echo "Setting up Thompson Sampling..."
echo "=========================="
cd $TS_DIR
conda create --name ts_env python=3.10 -y
source ~/miniconda3/bin/activate ts_env  # Activate environment
pip install -U pip
conda install -c conda-forge rdkit -y
pip install -r requirements.txt

# Optional: Install OpenEye toolkits for ROCS scoring (if needed)
echo "Thompson Sampling setup complete."

echo "=========================="
echo "All installations completed successfully!"
echo "=========================="
