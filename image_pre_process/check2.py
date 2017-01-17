# -*- coding: utf-8 -*-

import os
import sys
import copy
import urllib
import threading
import time
import imghdr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'out')
FILE_DIR = os.path.join(BASE_DIR, 'in')
LOG_DIR = os.path.join(BASE_DIR, 'failed.log')



def processMy(a, b, c):
        d=1

def myDownload(processMy, path, url):
    try:
                urllib.urlretrieve(url, path, processMy)
                return True, None
    except Exception,e:
		print e.args[0]
		#print url
		#print path
                return False, e




failedLinks = {}
overlapFiles = []
overlapLinks = []
fp = os.path.join(BASE_DIR, "failed.log")
_file = open(fp,'r')
line = _file.readline()
lineNum = 0
while line:
	lineNum += 1
	arr = line.split()
	failedPath = os.path.join(os.path.join(IMG_DIR, arr[0]), arr[1] + ".jpg")
	failedLinks[failedPath] = arr[2]
	if os.path.exists(failedPath):
		overlapFiles.append(failedPath)
		overlapLinks.append(arr[2])
	line = _file.readline()
_file.close()

print  lineNum

successCount = 0
failureCount = 0
downloadFailAndDel = 0
for key in failedLinks.keys():
	if failureCount % 3 ==1:
		print failureCount
		print successCount
	res = myDownload(processMy,key, failedLinks[key])
	if res[0]:
		if (os.path.getsize(key)/1024) < 5 or imghdr.what(key) is None:
			os.remove(key) 
			failureCount = failureCount+1
		else:
			successCount = successCount+1
	else:
		if os.path.exists(key):
			os.remove(key)
			downloadFailAndDel +=1
		failureCount = failureCount+1
			

	
