#!/bin/bash

process_command=/mnt/c/users/jryan/Documents/GitHub/ldif/ldif/scripts/process_mesh_local.sh

for CATEGORY in ./input_meshes_shapenet_ply/shapenet/train/*
do
    for FILE in $CATEGORY/*
    do
        echo Processing $FILE...
        full_orig_filepath=$(realpath $FILE)
        filename=$(basename -- "$FILE")
        new_filepath=/mnt/c/users/jryan/Documents/GitHub/ldif/shapenet_subsample_ds/shapenet/train/$(basename -- "$CATEGORY")/${filename%.*}
        ldif_in_ldif_dir=/mnt/c/users/jryan/Documents/GitHub/ldif/ldif
        $process_command $full_orig_filepath $new_filepath $ldif_in_ldif_dir
    done
done
