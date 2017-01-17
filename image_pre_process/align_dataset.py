"""Performs face alignment and stores face thumbnails in the output directory."""

# MIT License
# 
# Copyright (c) 2016 David Sandberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import dlib
import numpy as np
from scipy import misc

import src.image_pre_process.align_dlib as align_dlib


def main ( args ):
    face_size = 192
    use_center_crop =False
    data_path =  r'E:'
    prealigned_scale = ''
    image_size = ''
    prealigned_dir =''



    align = align_dlib.AlignDlib(os.path.join(os.path.abspath('..'), 'data\shape_predictor_68_face_landmarks.dat'))
    landmarkIndices = align_dlib.AlignDlib.OUTER_EYES_AND_NOSE
    a ='alignedFaces'
    b= 'out'
    output_dir = os.path.join(data_path, 'alignedFaces')
    rawfaces_dir = os.path.join(data_path, 'out')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    #src_path,_ = os.path.split(os.path.realpath(__file__))
    #facenet.store_revision_info(src_path, output_dir, ' '.join(sys.argv))

    dataset = get_dataset(rawfaces_dir)
    #random.shuffle(dataset)
    # Scale the image such that the face fills the frame when cropped to crop_size
    #scale = float(args.face_size) / args.image_size
    nrof_images_total = 0
    nrof_images_failed = 0
    nrof_images_passed = 0
    nrof_successfully_aligned = 0

    imgToRec  = {}
    fileList = []
    for fileName in [f for f in os.listdir(os.path.join(data_path, 'links')) if
                     os.path.isfile(os.path.join(os.path.join(data_path, 'links'), f))]:
        fn = fileName.replace('.txt', '')
        fileList.append(fn)
    for fn in fileList:
        # print len(pathTOLinks.keys())
        fp = os.path.join(os.path.join(data_path, 'links'), fn + ".txt")
        _file = open(fp, 'r')
        line = _file.readline()
        while line:
            arr = line.split()
            imgToRec[fn+str(arr[0])] = [int(round(float(f)))  for f in  arr[2:9]]
            line = _file.readline()
        _file.close()



    for cls in dataset:
        output_class_dir = os.path.join(output_dir, cls.name)
        if not os.path.exists(output_class_dir):
            os.makedirs(output_class_dir)
        #random.shuffle(cls.image_paths)
        for image_path in cls.image_paths:
            if nrof_images_total % 1000 == 0:
                print(nrof_images_total)
            nrof_images_total += 1
            filename = os.path.splitext(os.path.split(image_path)[1])[0]
            if (imgToRec[cls.name+str(filename)])[-1] == 0:
                nrof_images_passed += 1
                continue
            output_filename = os.path.join(output_class_dir, filename+'.jpg')
            if not os.path.exists(output_filename):
                try:
                    img = misc.imread(image_path)
                except (IOError, ValueError, IndexError) as e:
                    errorMessage = '{}: {}'.format(image_path, e)
                    print(errorMessage)
                else:
                    if len(img.shape) > 1:
                        if img.shape[-1] != 3:
                            img = to_rgb(img)
                        if use_center_crop:
                            scaled = misc.imresize(img, prealigned_scale, interp='bilinear')
                            sz1 = scaled.shape[1]/2
                            sz2 = image_size/2
                            aligned = scaled[(sz1-sz2):(sz1+sz2),(sz1-sz2):(sz1+sz2),:]
                        else:
                            tmp = (imgToRec[cls.name + filename])[0:4]
                            test =dlib.rectangle(tmp[0],tmp[1],tmp[2],tmp[3])
                            test.top()
                            aligned = align.align(face_size, img, bb=dlib.rectangle(tmp[0],tmp[1],tmp[2],tmp[3]),
                                                  landmarkIndices=landmarkIndices)
                    else:
                        nrof_images_failed +=1
                    if aligned is not None:
                        nrof_successfully_aligned += 1
                        misc.imsave(output_filename, aligned)
                    else:
                        nrof_images_failed +=1
                        print('Unable to align "%s"' % image_path)
                            
    print('Total number of images: %d' % nrof_images_total)
    print('Number of successfully aligned images: %d' % nrof_successfully_aligned)
    print('Number of failed aligned images: %d' % nrof_images_failed)
    print('Number of passed aligned images: %d' % nrof_images_passed)

class ImageClass():
    "Stores the paths to images for a given class"

    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths

    def __str__(self):
        return self.name + ', ' + str(len(self.image_paths)) + ' images'

    def __len__(self):
        return len(self.image_paths)

def get_dataset(path):
    dataset = []
    classes = os.listdir(path)
    classes.sort()
    nrof_classes = len(classes)
    for i in range(nrof_classes):
        class_name = classes[i]
        facedir = os.path.join(path, class_name)
        if os.path.isdir(facedir):
            images = os.listdir(facedir)
            image_paths = [os.path.join(facedir,img) for img in images]
            dataset.append(ImageClass(class_name, image_paths))
    return dataset


def to_rgb(img):

    ret = []
    if len(img.shape) == 2:
        w, h = img.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img
    elif img.shape[-1] >3 :
        w,h,r = img.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 0] = img[:, :, 0]
        ret[:, :, 1] = img[:, :, 1]
        ret[:, :, 2] = img[:, :, 2]
    else:
        w, h, r = img.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 0] = img[:, :, 0]
        ret[:, :, 1] = img[:, :, 0]
        ret[:, :, 2] = img[:, :, 0]
    return ret

if __name__ == '__main__':
    main('')
