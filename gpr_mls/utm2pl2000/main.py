import pyproj

transformer = pyproj.Transformer.from_crs('epsg:32634', 'epsg:2178')

path = r'C:\Users\admin1\Downloads\5 l001_20220601_145148_UTM.txt'
file = open(path, 'r')
file = file.readlines()

new_data = []
for i in range(len(file)):
    file[i] = file[i].replace('\n', '')
    file[i] = file[i].split('\t')


for i in range(len(file)):
    old_x = file[i][0]
    old_y = file[i][1]
    new_x, new_y = transformer.transform(old_x, old_y)
    new_data.append([new_x, new_y, file[i][2], file[i][3]])

print(new_data)

new_file = open(r'C:\Users\admin1\Downloads\5 l001_20220601_145148_PL2000.txt', 'w')
for line in new_data:
    new_file.write('{},{},{},{}\n'.format(line[0], line [1], line[2], line[3]))

