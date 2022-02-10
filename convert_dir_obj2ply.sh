
mkdir

for CATEGORY in input_meshes_shapenet_obj/shapenet/train/*
do 
    for FILE in $CATEGORY/*
    do
        category_name=$(basename -- "$CATEGORY")
        filename=$(basename -- "$FILE")
        mkdir -p ./input_meshes_shapenet_ply/shapenet/train/$category_name
        new_filepath=./input_meshes_shapenet_ply/shapenet/train/$category_name/${filename%.*}.ply
        # echo $FILE
        echo $new_filepath
        ./ldif/gaps/bin/x86_64/msh2msh $FILE $new_filepath
    done
done
