import os

shapes = {}

for file in os.listdir('ldif/data/basedirs'):
    print(file)
    if not any(x in file for x in ['small', 'tiny', 'all', 'half']):
        with open('ldif/data/basedirs/' + file, 'r') as f:
            for line in f:
                shape = os.path.splitext(line[line.index('/')+1:])[0]  # category/shape
                category = shape[:shape.index('/')]  # category
                if category in shapes:
                    shapes[category].append(shape[shape.index('/')+1:])
                else:
                    shapes[category] = [shape[shape.index('/')+1:]]

total_shapes = 0
os.system(f'mkdir shapes_lists')
for key in shapes:

    # Print official length
    shapes[key] = sorted(shapes[key])
    length = len(shapes[key])
    print(f'Length of {key}: {length}')
    total_shapes += length

    # Echo implementation length
    os.system(f'ls /mnt/h/input_meshes_shapenet_off/shapenet/train/{key}_3_fused | wc -l')

    # Write all included shapes to a file
    os.system(f'rm shapes_lists/{key}_shapes.txt')
    f = open(f"shapes_lists/{key}_shapes.txt", "a")
    for item in shapes[key]:
        f.write(f'{item}\n')
    f.close()

print(f'total shapes: {total_shapes}')


'''
Length of 02691156: 4045
4045  (4045)
Length of 04090263: 2346
2372
Length of 02828884: 1816
1816
Length of 02958343: 7496  (7497 in shapenet)
6427 -- 1069 missing meshes
Length of 02933112: 1572
1572
Length of 03211117: 1091
1095
Length of 04256520: 3173
3173  (3173)
Length of 04401088: 1052  (1052 in shapenet)
834  (834) -- 218 missing meshes
Length of 03691459: 1618
1618
Length of 03001627: 6778  (6778 in shapenet)
4971 -- 1807 missing meshes
Length of 03636649: 2299  (2318 in shapenet)
1093  (1093) -- 1225 missing meshes
Length of 04530566: 1939
1939  (1939)
Length of 04379243: 8509  (8509 in shapenet)
8509  (8490 preprocessed) -- 19 missing meshes
total shapes: 43734

Total missing meshes: 4338
@ 8s/mesh, 11 hours to watertight
Parallelized across 4 instances, probably like 3 hours to preprocess

The problem wasn't Vaisakh. The zips have the right number of shapes.
'''