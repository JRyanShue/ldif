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
for key in shapes:
    # Print official length
    length = len(shapes[key])
    print(f'Length of {key}: {length}')
    total_shapes += length
    # Print implementation length
    length = os.system(f'ls /mnt/h/input_meshes_shapenet_off/shapenet/train/{key}_3_fused | wc -l')
    # print(f'  ({length})')

print(f'total shapes: {total_shapes}')


'''
Length of 02691156: 4045
4045
Length of 04090263: 2346
2372
Length of 02828884: 1816
1816
Length of 02958343: 7496
6427
Length of 02933112: 1572
1572
Length of 03211117: 1091
1095
Length of 04256520: 3173
3173
Length of 04401088: 1052
834
Length of 03691459: 1618
1618
Length of 03001627: 6778
4971
Length of 03636649: 2299
1093
Length of 04530566: 1939
1939
Length of 04379243: 8509
8509
total shapes: 43734
'''