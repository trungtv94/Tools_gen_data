import cv2
from glob import glob 
import os

cwd = os.getcwd()
root = cwd  + '/val/'

img_dirs = glob(os.path.join(root, '*.jpg'))

f = open('val.txt', 'w')

for im in img_dirs: 
    f.write(im + os.linesep)
