# -*- coding: utf-8 -*-

import os
import sys
import copy
import urllib
import threading
import time
import imghdr

# 设置5秒超时
import socket
socket.setdefaulttimeout(3.0)

reload(sys)
sys.setdefaultencoding('utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'out')
FILE_DIR = os.path.join(BASE_DIR, 'in')
LOG_DIR = os.path.join(BASE_DIR, 'failed.log')

LOCK = threading.Lock()
FILE_LOCK = threading.Lock()
SIZE_LOCK = threading.Lock()
OUTPUT_LOCK = threading.Lock()
FINISH_LOCK = threading.Lock()

SUCCESS_COUNT = [0]
TOTAL_AMOUNT = 0
THREAD_AMOUNT = 400
COST_TIME = [0]
SUCCESS_FILE_SIZE = [0]
FINISH_THREAD_AMOUNT = [0]
DEBUG = False

# 给出待下载的文件名称，将该名称对应的文件内所有的图片下载到IMG_DIR下该名称对应的目录下
class BatchDownloader(threading.Thread):
  # 初始化时将待下载的文件名称传给downloader
  def __init__(self, nm, fl):
    super(BatchDownloader, self).__init__()
    self.name = nm
    self.fileList = copy.deepcopy(fl)

  # 将url指向的文件下载到path中
  def download(self, path, url):
    try:
      urllib.urlretrieve(url, path, process)
      return True, None
    except Exception, e:
      if e.args[0] == 'maximum recursion depth exceeded':
          logger('*****************','%s' % url)
          logger('*********','%s' % path)
      return False, e

  # 以此读取负责的文件中的每一行，并下载该行对应的图片
  # 如果下载失败，则将失败的url写进日志文件中
  def run(self):
    for fn in self.fileList:
      fp = os.path.join(FILE_DIR, fn + ".txt")
      _file = open(fp, 'r')
      line = _file.readline()
      lineNum = 0
      while line:
        lineNum += 1
        arr = line.split()
        res = [True]
        outPath = os.path.join(os.path.join(IMG_DIR, fn), arr[0] + ".jpg")
        if not os.path.exists(outPath):
          url = arr[1]
          res = self.download(outPath, url)
            
        # 如果下载成功，则SUCCESS_COUNT自增1
        if res[0]:
          if (os.path.getsize(outPath)/1024) < 5 or imghdr.what(outPath) is None:
            os.remove(outPath)
            if FILE_LOCK.acquire():
              f = open(LOG_DIR, 'a')
              f.write('%s\t%s\t%s\t%s\n' % (fn, arr[0], arr[1], 'not a picture'))
              f.close()
              FILE_LOCK.release()          
	  elif LOCK.acquire():
            SUCCESS_COUNT[0] += 1
            LOCK.release()
        else:
          if FILE_LOCK.acquire():
            f = open(LOG_DIR, 'a')
            f.write('%s\t%s\t%s\t%s\n' % (fn, arr[0], url, res[1]))
            f.close()
            FILE_LOCK.release()
        line = _file.readline()
      _file.close()
    # logger('DEBUG', self.name + u' 完成')
    if FINISH_LOCK.acquire():
      FINISH_THREAD_AMOUNT[0] += 1
      FINISH_LOCK.release()
      logger('YES', 'one thread is completed')

def logger(tp, msg):
  if OUTPUT_LOCK.acquire():
    if not DEBUG and tp.upper() == 'DEBUG':
      return
    print u'[%s]\t%s' % (tp, msg)
    OUTPUT_LOCK.release()

# 显示单个下载过程的进度
def process(a, b, c):
  d=1



# 显示整个下载进度
def showProcess():
  COST_TIME[0] += 1
  per = '%.2f' % (100 * float(SUCCESS_COUNT[0]) / TOTAL_AMOUNT)
  sys.stdout.write(u'\r[INFO]\t' + str(SUCCESS_COUNT[0]) + '/' + str(TOTAL_AMOUNT) + ' per ' + str(per) + '%, avg: '  + ' time: ' + prettyTime(COST_TIME[0]))
  sys.stdout.flush()
  if FINISH_THREAD_AMOUNT[0] < THREAD_AMOUNT+1:
    global timer
    timer = threading.Timer(1.0, showProcess)
    timer.setDaemon(True)
    timer.start()
timer = threading.Timer(1.0, showProcess)

# 格式化时间
def prettyTime(second):
  hour = 0
  minute = 0
  if second < 60:
    return str(second) + u"s"
  minute = int(second / 60)
  second = second % 60
  if minute < 60:
    return str(minute) + u"m" + str(second) + u"s"
  hour = int(minute / 60)
  minute = minute % 60
  return str(hour) + u"h" + str(minute) + u"m" + str(second) + u"s"

# 获取输入参数
def getParams(args):
  params = ' '.join(args).split('-')
  ret = {}
  for param in params:
    if len(param.strip()) > 0:
      key, val = param.split()
      ret[key] = val
  return ret

if __name__ == "__main__":
  # 从输入参数中获取输入文件的路径以及输出文件的路径
  params = getParams(sys.argv[1:])
  if 'i' in params.keys():
    FILE_DIR = params['i']
  if 'o' in params.keys():
    IMG_DIR = params['o']
  if 'tm' in params.keys():
    THREAD_AMOUNT = int(params['tm'])
  if not os.path.exists(FILE_DIR):
    logger('ERROR', u'输入路径不存在！')
    exit(-1)
  logger('INFO', u'初始化...')
  # 清空日志文件
  open(LOG_DIR, 'w').close()
  # 如果输出路径不存在则创建
  if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)
  logger('INFO', u'file_dir %s' % FILE_DIR)
  logger('INFO', u'out: %s' % IMG_DIR)
  logger('INFO', u'THREAD_AMOUNT: %d ' % THREAD_AMOUNT)
  fileList = []
  for root, dirs, files in os.walk(FILE_DIR):
    for fileName in files:
      fn = fileName.replace('.txt', '')
      fileList.append(fn)
      if not os.path.exists(os.path.join(IMG_DIR, fn)):
        os.makedirs(os.path.join(IMG_DIR, fn))
  logger('INFO', u'files: %d ' % len(fileList))
  logger('INFO', u'waiting..')
  for fn in fileList:
    fp = os.path.join(FILE_DIR, fn + ".txt")
    _file = open(fp, 'r')
    line = _file.readline()
    while line:
      TOTAL_AMOUNT += 1
      line = _file.readline()
  logger('INFO', u'total: %d links' % TOTAL_AMOUNT)
  logger('INFO', u'partition: %d ' % THREAD_AMOUNT)
  sys.stdout.write(u'\r[INFO]\t0/' + str(TOTAL_AMOUNT) )
  sys.stdout.flush()
  pool = []
  diff = len(fileList) / THREAD_AMOUNT
  start = 0
  end = 0
  # 申明downloader
  for i in xrange(0, THREAD_AMOUNT+1):
    start = end
    end = start + diff
    if end > len(fileList):
      end = len(fileList)
    pool.append(BatchDownloader('downloader %d' % i, fileList[start : end]))
    pool[-1].setDaemon(True)
    pool[-1].start()
  # 开始计时
  global timer
  timer.setDaemon(True)
  timer.start()
  try:
    while FINISH_THREAD_AMOUNT[0] < THREAD_AMOUNT+1:
      time.sleep(1)
      pass
  except KeyboardInterrupt:
    logger('\nWARN', u'quit!')
    sys.exit()
  # for downloader in pool:
  #   downloader.join()
  logger('\nINFO', 'done!!!!!!!!')
