#!bin/bash
cd ../
mkdir shapenet && cd shapenet

# Download all preprocessed data zip files
declare -a Classes=('02691156' '02828884' '02933112' '02958343' '03001627' '03211117' '03636649' '03691459' '04090263' '04256520' '04379243' '04401088' '04530566')
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
