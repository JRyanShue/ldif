#!bin/bash

for FILE in ./shapenet_watertight_ply/shapenet/train/04379243_3_fused/*
do
    filesize=$(wc -c $FILE | awk '{print $1}')
    threshold=1000
    if ((filesize < threshold))
    then
        mv $FILE /content/bucket/
    fi
done