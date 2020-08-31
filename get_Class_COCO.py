mode = 'train' # 'val' # 
list_class = ['motorcycle','bicycle','car','person','bus','truck'] 

from pycocotools.coco import COCO 
from glob import glob 
import requests
import csv
import os 
import json
import random 
import cv2 
import shutil

class CocoDataset():
    def __init__(self, annotation_path):
        self.annotation_path = annotation_path
        
        json_file = open(self.annotation_path)
        self.coco = json.load(json_file)
        json_file.close()
        
        self.process_info()
        self.process_licenses()
        self.process_categories() 
        self.process_segmentations()
     
    def display_image(self, image_id, classes, use_url=False):
            
        tvt_list = []
        for i, segm in enumerate(self.segmentations[image_id]):
            bbox = segm['bbox']
            bbox_points = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1],
                           bbox[0] + bbox[2], bbox[1] + bbox[3], bbox[0], bbox[1] + bbox[3],
                           bbox[0], bbox[1]]
            
            if self.categories[segm['category_id']]['name'] == classes: 
                tvt_bbox = [int(bbox[0]), int(bbox[1]), int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])]
                tvt_list.append(tvt_bbox)
            
        return tvt_list
       
    def process_info(self):
        self.info = self.coco['info']
    
    def process_licenses(self):
        self.licenses = self.coco['licenses']
    
    def process_categories(self):
        self.categories = {}
        self.super_categories = {}
        for category in self.coco['categories']:
            cat_id = category['id']
            super_category = category['supercategory']
            
            # Add category to the categories dict
            if cat_id not in self.categories:
                self.categories[cat_id] = category
            else:
                print("ERROR: Skipping duplicate category id: {}".format(category))

            # Add category to super_categories dict
            if super_category not in self.super_categories:
                self.super_categories[super_category] = {cat_id} # Create a new set with the category id
            else:
                self.super_categories[super_category] |= {cat_id} # Add category id to the set
                
    def process_segmentations(self):
        self.segmentations = {}
        for segmentation in self.coco['annotations']:
            image_id = segmentation['image_id']
            if image_id not in self.segmentations:
                self.segmentations[image_id] = []
            self.segmentations[image_id].append(segmentation)

# -------------------------------------------------------------------------
cwd = os.getcwd()
root = cwd + '/op_dataset/'
if mode == 'train':
    annotation_path = 'annotations/instances_train2017.json' 
else:
    annotation_path = 'annotations/instances_val2017.json' 
coco_dataset = CocoDataset(annotation_path) 
print('================= FIRST INIT DONE ===============')
coco = COCO(annotation_path)
print('================= INIT DONE ===============')

# -------------------------------------------------------------------------   

if mode == 'train':
    file_names = open(root + 'obj.names','w')
number_class = len(list_class)

for indx, classes in enumerate(list_class):
    print('CREATING IMAGE FOR: ', classes,'...')
    directory = 'op_dataset/' + classes
    if not os.path.exists(directory):
        os.makedirs(directory) 
    
    if mode == 'train':    
        file_names.write(classes + os.linesep)
    
    catIds = coco.getCatIds(catNms=[classes])
    imgIds = coco.getImgIds(catIds=catIds )
    images = coco.loadImgs(imgIds)
    
    for im in images:     
        # Copy image
        if mode == 'train':
            src = 'train2017/' + im['file_name']
        else: 
            src = 'val2017/' + im['file_name']
        dst = 'op_dataset/' + classes + '/' + im['file_name']
        shutil.copyfile(src, dst) 
        
        # Get Annotaion
        img = cv2.imread(src)
        hei, wid, _ = img.shape
        
        name_ = im['file_name'][0:(len(im['file_name'])-3)]
        name_ = 'op_dataset/' + classes + '/' + name_ + 'txt'
        
        imgIds=im['id']
        list_Anno = coco_dataset.display_image(imgIds, classes, use_url=True) 
        file_anno = open(name_, 'w')
        for x in list_Anno:  
            centerX = (x[0] + x[2])/2
            centerY = (x[1] + x[3])/2
            width = (x[2] - x[0])
            heigh = (x[3] - x[1])
            
            centerX_ = str(centerX/wid)[0:7]
            centerY_ = str(centerY/hei)[0:7]
            width_   = str(width/wid)[0:7]
            heigh_   = str(heigh/hei)[0:7]
            
            string_final = str(indx) + ' ' + centerX_ + ' ' + centerY_ + ' ' + width_ + ' ' + heigh_
            file_anno.write(string_final + os.linesep)
        file_anno.close() 
    print('=================IMAGE ',classes,' DONE=======================')
if mode == 'train':
    file_names.close() 

#------------------------------------------------------------------------------------

if mode == 'train':
    dataset_dir = 'op_dataset/train/' 
else:
    dataset_dir = 'op_dataset/val/' 
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir) 

if mode == 'train':
    file_data = open(os.path.join(root,'obj.data'),'w')
    file_data.write('classes = ' + str(number_class) + os.linesep) 
    file_data.write('train = ' + os.path.join(root,'train.txt') + os.linesep)
    file_data.write('train = ' + os.path.join(root,'val.txt') + os.linesep)
    file_data.write('names = ' + os.path.join(root,'obj.names') + os.linesep)
    file_data.write('backup = backup/' + os.linesep)
    file_data.write('eval = coco' + os.linesep)
    file_data.close()

for classes in list_class:
    dataset = glob(os.path.join(dataset_dir, '*.txt'))
    img_dirs = glob(os.path.join(root, classes, '*.jpg'))
    for img_dir in img_dirs:        
        name = os.path.basename(img_dir).split('.')[0]
        anno_dir = os.path.join(root, classes, name + '.txt') 
        shutil.move(img_dir, dataset_dir + name + '.jpg')   
        
        is_anno = dataset_dir + name + '.txt'
        if is_anno in dataset:
            f = open(is_anno,'a')
            ff = open(anno_dir,'r')
            text = ff.read()
            ff.close()
            f.write(text) 
            f.close()
            os.remove(anno_dir)
        else:
           shutil.move(anno_dir, dataset_dir)
    os.rmdir(root + classes) 

