#!bin/bash
cd ../
mkdir shapenet && cd shapenet

# Download 48 shapes (2 batches of 24) from the ShapeNet chair val set (03001627)
echo "Downloading 48 shapes from the chair val set..."
wget https://imt-public-datasets.s3.amazonaws.com/48_subsample.zip

# Unzip files
for FILE in ./*
do
    echo unzipping $FILE...
    unzip $FILE
    rm $FILE
done
