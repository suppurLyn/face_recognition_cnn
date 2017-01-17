import os
import sys
import imghdr
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, 'out')
if 1==1 :
    count = 0
    print BASE_DIR
    subdir_list=[]
    for root, dirs, files in os.walk(OUT_DIR):
        subdir_list.append(root)
    for subdir in subdir_list[1:len(subdir_list)]:
        for root, dirs, files in os.walk(subdir):
            for file in files:
                picFile = os.path.join(subdir, file)
                if (os.path.getsize(picFile)/1024) < 5 or imghdr.what(picFile) is None:
                    try:
                        os.remove(picFile)
                        count += 1
                        if (count %50) ==0:
                           print count
                    except Exception, e:
                        print e.args
    print 'success!!!!!!!!!!'
    print count
