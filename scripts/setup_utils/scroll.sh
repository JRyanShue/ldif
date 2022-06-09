#!bin/bash
counter=0
for FILE in shapenet_watertight_ply/shapenet/train/04379243_3_fused/*
do
  ((counter+=1))
  if ((counter == 2000))
  then
    break
  fi
  cp $FILE shapenet_watertight_ply_1/shapenet/train/04379243_3_fused/
done