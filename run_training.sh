#!bin/bash
conda env create --name ldif -f environment.yml
conda activate ldif
# download_{tiny_subsample, shapenet_chair, full_shapenet}.sh
bash scripts/tiny_subsample.sh
# python setup.py build_ext --inplace  # Not needed if only using IoU for metrics
python train.py --batch_size 24 --dataset_directory /mnt/c/users/jryan/Documents/GitHub/ldif/watertight_ds --experiment_name ldif --model_type ldif
