# Face Recognition implementation in Tensorflow
This is a TensorFlow implementation of the face recognizer base on the paper
["FaceNet: A Unified Embedding for Face Recognition and Clustering"](http://arxiv.org/abs/1503.03832). But i choose the inception-res-v1 as the final inference graph and change the loss function to center loss ["A Discriminative Feature Learning Approach for Deep Face Recognition"](http://ydwen.github.io/papers/WenECCV16.pdf).


## Training data
The [FaceScrub](http://vintage.winklerbros.net/facescrub.html) dataset and the VGG dataset ["Deep Face Recognition"](http://www.robots.ox.ac.uk/~vgg/publications/2015/Parkhi15/parkhi15.pdf). There are about 100,000 image links and 2.2M links in the two sources. But due to the dead links and network situatoin, i downloaded 2M images including some truncate ones in 2 days.

## Pre-processing
The images for cnn are aligned and data-augmented(whitening, flipping, random cropped) ,size : 160*160. Because there are some bad and wrong-classe images images from internet, some scripts are to judge whether the current image is the right one, based on the comparisoin between the bunding box of face detecting algorithm and given one. I tried diffenent solutions for fae alignment : ccv2+dlib and [Multi-task CNN](https://kpzhang93.github.io/MTCNN_face_detection_alignment/index.html). The mtcnn is better

## Performance
My environment ： ubuntu 16 + tensorlow + cuda 8.0 + E3 v5 + gtx 1070. The final size of training dateset is abuot 0.8M , batch size: 64, epoches: 100. It takes about 15 hours to complete the training.The accuracy on LFW for the model reached 98.5%(see roc curve in data/picture_1.png) 

## Inspired
The code is heavly inspired by the project of davidsandberg

## Experiences 
1. VGG net is robust for learning patterns from huge size of images.  2. It is not easy to get a good accuracy on relatively small training dataset(google : 200M).   3. data pre-processing is very time-comsuming  4. the ccelebrities are main occidental and african which have explicit outlines. it will need more work to settle a real online face recognition system.
