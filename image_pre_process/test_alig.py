# 52.86 52.86 288.91 288.91
# coding: utf-8
import os

#C:\Program Files\Anaconda2\Lib\site-packages\dlib.pyd
'''

align = align_dlib.AlignDlib(r'D:\jupyter\facenet-master\data\shape_predictor_68_face_landmarks.dat')
img = r'D:\jupyter\facenet-master\data\images\2.jpg'
img = misc.imread(img)
thumbnail =  align.align(512,img)
misc.imsave(r'D:\jupyter\facenet-master\data\images\aliged_512.jpg', thumbnail)
'''

print os.path.splitext(os.path.split(r'D:\jupyter\facenet-master\data\images\aliged_512.jpg')[1])[0]