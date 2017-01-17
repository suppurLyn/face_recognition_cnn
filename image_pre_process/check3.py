# -*- coding: utf-8 -*-

import os
import sys
import copy
import urllib
import threading
import time
import imghdr
import socket
socket.setdefaulttimeout(5.0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'out')
FILE_DIR = os.path.join(BASE_DIR, 'in')
LOG_DIR = os.path.join(BASE_DIR, 'finish.log')



def processMy(a, b, c):
        d=1

def myDownload(path, url,processMy):
    try:
		urllib.urlretrieve(url, path, processMy)
		return True, None
    except Exception,e:
		print e.args[0]
		return False, e
 ### all links
fileList =[]
pathTOLinks ={}		
if 1==1:
  for root, dirs, files in os.walk(FILE_DIR):
    for fileName in files:
      fn = fileName.replace('.txt', '')
      fileList.append(fn)
  for fn in fileList:
   # print len(pathTOLinks.keys()) 
    fp = os.path.join(FILE_DIR, fn + ".txt")
    _file = open(fp, 'r')
    line = _file.readline()
    while line:
		arr = line.split()
		pathTOLinks[os.path.join(os.path.join(IMG_DIR, fn), arr[0] + ".jpg")] = arr[1]
		line = _file.readline()
    _file.close()

print  1
#### failedLIinks
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
print 2
needDownLoad  = {}
for key in pathTOLinks.keys():
	if not os.path.exists(key) and not failedLinks.has_key(key):
		needDownLoad[key] = pathTOLinks[key]		

print len(needDownLoad.keys())
print len(failedLinks.keys())
print len(pathTOLinks.keys())

LOCK = threading.Lock()
SUCCESS_LOCK = threading.Lock()
FAIL_LOCK = threading.Lock()
FILE_LOCK = threading.Lock()
DICT_LOCK = threading.Lock()
OUTPUT_LOCK = threading.Lock()
FINISH_LOCK = threading.Lock()



FAIL_COUNT = [0]
THREAD_AMOUNT = 300
FINISH_THREAD_AMOUNT = [0]

class BatchDownloader(threading.Thread):
  def __init__(self, nm, keys):
    super(BatchDownloader, self).__init__()
    self.name = nm
    self.subKeys = copy.deepcopy(keys)

  def run(self):
    for key in self.subKeys:
		res =[True]
		if DICT_LOCK.acquire():
			try:
				url = finalDict[key]
			except Exception, e:
				print e.args[0]
			DICT_LOCK.release()
		res = myDownload(key,url,processMy)
		if res[0]:
			if (os.path.getsize(key)/1024) < 5 or imghdr.what(key) is None:
				os.remove(key) 
				if FAIL_LOCK.acquire():
					FAIL_COUNT[0] = FAIL_COUNT[0]+1
					FAIL_LOCK.release()
		else:
			if FAIL_LOCK.acquire():
				FAIL_COUNT[0] = FAIL_COUNT[0]+1
				FAIL_LOCK.release()
    if FINISH_LOCK.acquire():
	FINISH_THREAD_AMOUNT[0] += 1
	FINISH_LOCK.release()
	if FILE_LOCK.acquire():
		f = open(LOG_DIR, 'a')
		f.write('%s\n' % FINISH_THREAD_AMOUNT[0])
		f.close()
		FILE_LOCK.release()
    print FAIL_COUNT[0]	
finalDict = dict(pathTOLinks.items()+failedLinks.items())	
if __name__ == '__main__' :
	pool = []
	diff = len(finalDict.keys()) / THREAD_AMOUNT
	start = 0
	end = 0
	# 申明downloader
	for i in xrange(0, THREAD_AMOUNT+1):
		start = end
		end = start + diff
		if end > len(fileList):
			end = len(fileList)
		pool.append(BatchDownloader('downloader %d' % i, finalDict.keys()[start : end]))
		pool[-1].setDaemon(True)
		pool[-1].start()
	try:
		while FINISH_THREAD_AMOUNT[0] < (THREAD_AMOUNT+1):
			time.sleep(5)
			pass
	except KeyboardInterrupt:	
		sys.exit()

	print 'good job!'

			
			

			
			
	
