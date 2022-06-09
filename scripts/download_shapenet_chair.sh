#!bin/bash
cd ../
mkdir shapenet && cd shapenet

# Download chair (03001627) subset of ShapeNet
declare -a Classes=('03001627')
for CATEGORY in ${Classes[@]}
do
    echo Downloading $CATEGORY...
    wget https://imt-public-datasets.s3.amazonaws.com/preprocecssed_splits/${CATEGORY}_train.zip
    wget https://imt-public-datasets.s3.amazonaws.com/preprocecssed_splits/${CATEGORY}_test.zip
    wget https://imt-public-datasets.s3.amazonaws.com/preprocecssed_splits/${CATEGORY}_val.zip
done

# Unzip files
for FILE in ./*
do
    echo unzipping $FILE...
    unzip $FILE
    rm $FILE
done
