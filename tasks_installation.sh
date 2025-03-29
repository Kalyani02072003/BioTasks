#!/bin/bash

# Set error handling
set -e  # Exit on first error
set -o pipefail  # Exit if any command in a pipeline fails

# Define installation paths
ROOT_DIR="$HOME/BioTasks"
ANTIFOLD_DIR="$ROOT_DIR/AntiFold"
LIGANDMPNN_DIR="$ROOT_DIR/LigandMPNN"
PROTEINMPNN_DDG_DIR="$ROOT_DIR/proteinmpnn_ddg"
TS_DIR="$ROOT_DIR/ThompsonSampling"
FREEWILSON_DIR="$ROOT_DIR/Free-Wilson"  # Free-Wilson directory

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
[[ ! -d "Free-Wilson" ]] && git clone https://github.com/PatWalters/Free-Wilson.git

echo "Repositories cloned successfully."

####### AntiFold Setup ########
echo "=========================="
echo "Setting up AntiFold..."
echo "=========================="
cd $ANTIFOLD_DIR
if ! conda info --envs | grep -q "antifold"; then
    conda create --name antifold python=3.10 -y
fi
conda activate antifold
pip install -U pip
conda install -c conda-forge pytorch -y
pip install .
echo "AntiFold setup complete."

####### LigandMPNN Setup ########
echo "=========================="
echo "Setting up LigandMPNN..."
echo "=========================="
cd $LIGANDMPNN_DIR
if ! conda info --envs | grep -q "ligandmpnn_env"; then
    conda create -n ligandmpnn_env python=3.11 -y
fi
conda activate ligandmpnn_env
pip install -U pip
pip install -r requirements.txt
bash get_model_params.sh "./model_params"
echo "LigandMPNN setup complete."

####### ProteinMPNN-ddG Setup ########
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

####### Thompson Sampling Setup ########
echo "=========================="
echo "Setting up Thompson Sampling..."
echo "=========================="
cd $TS_DIR
if ! conda info --envs | grep -q "ts_env"; then
    conda create --name ts_env python=3.10 -y
fi
conda activate ts_env
pip install -U pip
conda install -c conda-forge rdkit -y
pip install -r requirements.txt
echo "Thompson Sampling setup complete."

####### Free-Wilson Setup ########
echo "=========================="
echo "Setting up Free-Wilson..."
echo "=========================="
cd $FREEWILSON_DIR
if ! conda info --envs | grep -q "freewilson_env"; then
    conda create --name freewilson_env python=3.9 -y
fi
conda activate freewilson_env
pip install -U pip
pip install rdkit tqdm docopt pyfancy sklearn scipy joblib

echo "Free-Wilson setup complete."

echo "=========================="
echo "All installations completed successfully!"
echo "=========================="
