import os

missing_shapes = {}
have_shapes = {}

basedir = '/content/preprocessed_data/shapenet_preprocessed/train/'
for file in os.listdir(basedir):
  print(file)
  category = file[:file.index('_')]
  have_shapes[category] = os.listdir(f'{basedir}{file}/')

  with open(f'ldif/shapes_lists/{category}_shapes.txt') as r:
    missing_list = []
    for line in r:
      if line[:line.index('\n')] not in have_shapes[category]:
        missing_list.append(line[:line.index('\n')])
    missing_shapes[category] = missing_list

  # Write all missing shapes to a file
  os.system(f'rm ldif/missing_shapes/{category}_shapes.txt')
  f = open(f'ldif/missing_shapes/{category}_shapes.txt', 'a')
  for item in missing_shapes[category]:
    f.write(f'{item}\n')
  f.close()


print(len(missing_shapes['04379243']))
print(len(have_shapes['04379243']))

print(missing_shapes)

