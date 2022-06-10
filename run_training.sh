#!bin/bash
conda env create --name ldif -f environment.yml
source activate ldif
# download_{tiny_subsample, shapenet_chair, full_shapenet}.sh
bash scripts/download_tiny_subsample.sh
# python setup.py build_ext --inplace  # Not needed if only using IoU for metrics

# For training, rename dir
mv ../shapenet/shapenet_ldif/val ../shapenet/shapenet_ldif/train

# Download &unzip checkpoint
wget https://imt-public-datasets.s3.amazonaws.com/pretrained_models/ldif_48shape.zip && unzip ldif_48shape.zip

# Checkpoint uploads to s3
python train.py --batch_size 24 --dataset_directory ../shapenet/shapenet_ldif --experiment_name ldif --model_type ldif --checkpoint_interval 1000
