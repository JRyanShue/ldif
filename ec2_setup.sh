#!/bin/bash
# Install conda
wget https://repo.continuum.io/archive/Anaconda3-5.3.1-Linux-x86_64.sh
bash Anaconda3-5.3.1-Linux-x86_64.sh
export PATH="/home/ubuntu/anaconda3/bin:$PATH"

# Clone and build ldif
git clone https://github.com/JRyanShue/ldif.git
cd ldif
conda env create --name ldif -f environment.yml