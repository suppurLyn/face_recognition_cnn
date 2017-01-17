# -*- coding: utf-8 -*-

import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'out')
FILE_DIR = os.path.join(BASE_DIR, 'in')
LOG_DIR = os.path.join(BASE_DIR, 'finish.log')
ERROR_DIR = os.path.join(BASE_DIR, 'error.log')

dirList = []
fp = os.path.join(BASE_DIR,  + "ziplist.txt")
_file = open(fp, 'r')
line = _file.readline()
while line:
	if os.path.exists(failedPath):
		dirList.appned(os.path.join(os.path.join(IMG_DIR, line),'*.*'))
	else:
		print 'not exist this directory!!!!'
	line = _file.readline()
_file.close()
print len(dirList)

'''
if 1==1 :
	diff = len(dirList) / 5
	start = 0
	end = 0
	for i in xrange(0, 6):
		start = end
		end = start + diff
		if end > len(dirList):
			end = len(dirList)
		zip_command="rar a " + i+'.rar' + ' '.join(dirList[start : end])
		
	if os.system(zip_command)==0:
		print 'Successful backup to  ' +i+'.rar'
	else:
		print 'Backup FAILED'
'''
			

			