
# input_dir=input_meshes_shapenet_obj/shapenet/train/*
# output_dir=input_meshes_shapenet_ply/shapenet/train
input_dir=./shapenet_watertight_off/*
output_dir=shapenet_watertight_ply/shapenet/train
for CATEGORY in $input_dir
do
    for FILE in $CATEGORY/*
    do
        category_name=$(basename -- "$CATEGORY")
        filename=$(basename -- "$FILE")
        mkdir -p ./${output_dir}/${category_name}
        new_filepath=./${output_dir}/${category_name}/${filename%.*}.ply
        echo $CATEGORY
        echo "Moving $FILE to $new_filepath"
        ./ldif/gaps/bin/x86_64/msh2msh $FILE $new_filepath
    done
done
