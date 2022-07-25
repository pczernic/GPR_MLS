import os


for file in os.listdir():
    new = file.replace('-', '')
    os.rename(file, new)
print(os.listdir)