"""Performs face alignment and stores face thumbnails in the output directory."""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import sys
import os
import argparse
import tensorflow as tf
import numpy as np
import facenet
import align.detect_face
import random

def main(args):
  
    output_dir = os.path.expanduser(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    src_path, _ = os.path.split(os.path.realpath(__file__))
    facenet.store_revision_info(src_path, output_dir, ' '.join(sys.argv))
    dataset = facenet.get_dataset(args.input_dir)



    imgToRec  = {}
    fileList = []
    for fileName in [f for f in os.listdir(args.links_dir) if
                     os.path.isfile(os.path.join(args.links_dir, f))]:
        fn = fileName.replace('.txt', '')
        fileList.append(fn)
    for fn in fileList:
        fp = os.path.join(args.links_dir, fn + ".txt")
        _file = open(fp, 'r')
        line = _file.readline()
        while line:
            arr = line.split()
            imgToRec[fn+str(arr[0])] = [int(round(float(f))) for f in arr[2:9]]
            line = _file.readline()
        _file.close()


    print('Creating networks and loading parameters')
    
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=args.gpu_memory_fraction)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = align.detect_face.create_mtcnn(sess, '../../data/')
    
    minsize = 20 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor

    # Add a random key to the filename to allow alignment using multiple processes
    random_key = np.random.randint(0, high=99999)
    bounding_boxes_filename = os.path.join(output_dir, 'bounding_boxes_%05d.txt' % random_key)



    with open(bounding_boxes_filename, "w") as text_file:
        nrof_images_total = 0
        nrof_successfully_aligned = 0
        nrof_passed_aligned = 0
        nrof_failed_aligned = 0
        if args.random_order:
            random.shuffle(dataset)
        for cls in dataset:
            output_class_dir = os.path.join(output_dir, cls.name)
            if not os.path.exists(output_class_dir):
                os.makedirs(output_class_dir)
                if args.random_order:
                    random.shuffle(cls.image_paths)
            for image_path in cls.image_paths:
                default_info = imgToRec[cls.name + os.path.split(image_path)[-1].replace('.jpg', '')]
                if default_info[-1] == 0:
                    nrof_passed_aligned += 1
                    continue
                nrof_images_total += 1
                filename = os.path.splitext(os.path.split(image_path)[1])[0]
                output_filename = os.path.join(output_class_dir, filename+'.jpg')
                if not os.path.exists(output_filename):
                    try:
                        img = misc.imread(image_path)
                    except (IOError, ValueError, IndexError) as e:
                        nrof_failed_aligned += 1
                        errorMessage = '{}: {}'.format(image_path, e)
                        print(errorMessage)
                    else:
                        if img.ndim<2:
                            print('Unable to align "%s"' % image_path)
                            nrof_failed_aligned += 1
                            text_file.write('%s\n' % (output_filename))
                            continue
                        if len(img.shape) > 1 and img.shape[-1] != 3:
                            img = to_rgb(img)
                        img = img[:, :, 0:3]
                        bounding_boxes, _ = align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
                        nrof_faces = bounding_boxes.shape[0]
                        if nrof_faces>0:
                            img_size = np.asarray(img.shape)[0:2]
                            det = bounding_boxes[:, 0:4]
                            rates = [overlap_ratio(x, default_info[0:4]) for x in det.tolist()]
                            if sum([x>0.4 for x in rates]) == 1:
                                index = np.argmax(rates)
                                det = det[index,:]
                                det = np.squeeze(det)
                                bb = np.zeros(4, dtype=np.int32)
                                bb[0] = np.maximum(det[0]-args.margin/2, 0)
                                bb[1] = np.maximum(det[1]-args.margin/2, 0)
                                bb[2] = np.minimum(det[2]+args.margin/2, img_size[1])
                                bb[3] = np.minimum(det[3]+args.margin/2, img_size[0])
                                cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
                                scaled = misc.imresize(cropped, (args.image_size, args.image_size), interp='bilinear')
                                nrof_successfully_aligned += 1
                                misc.imsave(output_filename, scaled)
                                text_file.write('%s %d %d %d %d %d\n' % (output_filename, bb[0], bb[1], bb[2], bb[3],round(max(rates)*100,2)))
                        else:
                            print('Unable to align "%s"' % image_path)
                            text_file.write('%s\n' % (output_filename))
                else:
                    nrof_successfully_aligned += 1
                            
    print('Total number of images: %d' % nrof_images_total)
    print('Number of successfully aligned images: %d' % nrof_successfully_aligned)
    print('Number of  passed images: %d' % nrof_passed_aligned)
    print('Number of  failed images: %d' % nrof_failed_aligned)

def overlap_ratio(rec1, rec2):
    x1 = rec1[0]
    y1 = rec1[1]
    width1 = rec1[2]-rec1[0]
    height1 = rec1[3]-rec1[1]

    x2 = rec2[0]
    y2 = rec2[1]
    width2 = rec2[2]-rec2[0]
    height2 = rec2[3]-rec2[1]

    endx = max(x1 + width1, x2 + width2)
    startx = min(x1, x2)
    width = width1 + width2 - (endx - startx)

    endy = max(y1 + height1, y2 + height2)
    starty = min(y1, y2)
    height = height1 + height2 - (endy - starty)
    if width <= 0 or height <= 0:
        return 0
    else:
        Area = width * height
        Area1 = width1 * height1
        Area2 = width2 * height2
        return float(Area) / min(Area1, Area2)


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


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('input_dir', type=str, help='Directory with unaligned images.')
    parser.add_argument('output_dir', type=str, help='Directory with aligned face thumbnails.')
    parser.add_argument('links_dir', type=str, help='Directory with download links.')
    parser.add_argument('--image_size', type=int,
        help='Image size (height, width) in pixels.', default=182)
    parser.add_argument('--margin', type=int,
        help='Margin for the crop around the bounding box (height, width) in pixels.', default=44)
    parser.add_argument('--random_order', 
        help='Shuffles the order of images to enable alignment using multiple processes.', action='store_true')
    parser.add_argument('--gpu_memory_fraction', type=float,
        help='Upper bound on the amount of GPU memory that will be used by the process.', default=0.9)
    return parser.parse_args(argv)

if __name__ == '__main__':
    sys.argv = [sys.argv[0], r'/media/lyn/DISK_E/facescrub', r'/media/lyn/DISK_E/facescrub_ali_faces_160/',r'/media/lyn/DISK_E/bboxes.txt/']
    main(parse_arguments(sys.argv[1:]))
