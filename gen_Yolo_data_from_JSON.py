from glob import glob
import json
import os
import cv2

root = 'Full/'

json_dirs = glob(os.path.join(root, '*.json'))
list_label = ['motorcycle','bicycle','car','person','bus','truck']
def get_indx(name):
    for ind, lab in enumerate(list_label):
        if name == lab:
            return str(ind)
    
for json_file in json_dirs:
    print(json_file)
    name_ = os.path.basename(json_file).split('.')[0]
    name_jpg = os.path.basename(json_file).split('.')[0] + '.jpg'
    im = cv2.imread(root + name_jpg)
    hei, wid, _ = im.shape
    
    f = open(json_file, 'r')
    data = json.load(f) 
    shapes = data['shapes']
    
    f_w = open(root + name_ + '.txt', 'w')
    for shape in shapes:
        name = shape['label']
        x1 = int(shape['points'][0][0])
        y1 = int(shape['points'][0][1])
        x2 = int(shape['points'][1][0])
        y2 = int(shape['points'][1][1])
        print(x1,y1,x2,y2)
        centerX = str(((x1 + x2)//2)/wid)[0:7]
        centerY = str(((y1 + y2)//2)/hei)[0:7]
        height = str((x2 - x1)/wid)[0:7]
        width  = str((y2 - y1)/hei)[0:7]
        f_w.write(get_indx(name) + ' ' + centerX + ' ' + centerY + ' ' + height + ' ' + width + os.linesep)
    f_w.close()
    f.close()
        