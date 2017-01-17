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
ERROR_DIR = os.path.join(BASE_DIR, 'error.log')
MAX_ERR  = os.path.join(BASE_DIR, 'maxerror.log')


def myDownload(path, url):
    try:
		urllib.urlretrieve(url, path)
		return True, None
    except Exception,e:
		if e.args[0] == 'maximum recursion depth exceeded':
			f = open(MAX_ERR, 'a')
			f.write( '%s\t%s\n' % (url,path))
                        f.close()
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
LINKS_LOCK = threading.Lock()
ERROR_LOCK = threading.Lock()

LINKS_COUNT = [0]
SUCCESS_COUNT = [0]
FAIL_COUNT = [0]
THREAD_AMOUNT = 300
FINISH_THREAD_AMOUNT = [0]

class BatchDownloader(threading.Thread):
  def __init__(self, nm, keys):
    super(BatchDownloader, self).__init__()
    self.nm = nm
    self.subKeys = copy.deepcopy(keys)

  def run(self):
    for key in self.subKeys:
		res =[True]
		url = ''
		if DICT_LOCK.acquire():
			url = needDownLoad[key]
			DICT_LOCK.release()
		if LINKS_LOCK.acquire():
			LINKS_COUNT[0] += 1
			LINKS_LOCK.release()
		if LINKS_COUNT[0] % 1000 ==0:
			print LINKS_COUNT[0]	
		res = myDownload(key,url)
		if res[0]:
			if (os.path.getsize(key)/1024) < 5 or imghdr.what(key) is None:
				os.remove(key) 
				if FAIL_LOCK.acquire():
					FAIL_COUNT[0] = FAIL_COUNT[0]+1
					FAIL_LOCK.release()
			else:
				if SUCCESS_LOCK.acquire():
					SUCCESS_COUNT[0] = SUCCESS_COUNT[0]+1
					SUCCESS_LOCK.release()
		else:
			if FAIL_LOCK.acquire():
				FAIL_COUNT[0] = FAIL_COUNT[0]+1
				FAIL_LOCK.release()
			if ERROR_LOCK.acquire():
				f = open(ERROR_DIR, 'a')
				f.write('%s\t%s\n' % (self.nm,res[1]))
				f.close()
				ERROR_LOCK.release()
		
		
    if FINISH_LOCK.acquire():
		FINISH_THREAD_AMOUNT[0] += 1
		FINISH_LOCK.release()
    if FILE_LOCK.acquire():
		f = open(LOG_DIR, 'a')
		f.write('%s\t%s\t%s\t%s\t%s\n' % (self.nm,FINISH_THREAD_AMOUNT[0],FAIL_COUNT,SUCCESS_COUNT,LINKS_COUNT))
		f.close()
		FILE_LOCK.release()

#finalDict = dict(needDownLoad.items()+failedLinks.items())

print len(needDownLoad.keys())	
if __name__ == '__main__' :
	#print len(finalDict.keys())
	pool = []
	diff = len(needDownLoad.keys()) / THREAD_AMOUNT
	start = 0
	end = 0
	# 申明downloader
	for i in xrange(0, THREAD_AMOUNT+1):
		start = end
		end = start + diff
		if end > len(needDownLoad.keys()):
			end = len(needDownLoad.keys())
		pool.append(BatchDownloader('downloader %d' % i, needDownLoad.keys()[start : end]))
		pool[-1].setDaemon(True)
		pool[-1].start()
	try:
		while FINISH_THREAD_AMOUNT[0] < (THREAD_AMOUNT+1):
			time.sleep(5)
			pass
	except KeyboardInterrupt:	
		sys.exit()

	print 'good job!'

			
			

			
			
	
