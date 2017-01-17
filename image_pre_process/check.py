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


failedLinks = {}
overlapFiles = []
overlapLinks = []
_file = open(LOG_DIR, 'r')
fp = os.path.join(BASE_DIR, "failed.log")
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

for i in [2*x for x in range(1,10)]:
	print overlapLinks[i]
	print overlapFiles[i]
	print('\t')
