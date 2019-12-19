#!/usr/bin/python

import os
import logging
import errno
import commands
import sys
import string
import re
import time

basedir='.'
# Pattern of License header text contained in .license.txt to compare against.
f_lic = '.license.txt'
logfile = 'license_check.log'
lic_pat = ""
file_list = []
err_cnt = 0
scan_all = 1
debug = 0
logger = None

skip_f_list = ['license_check.py', f_lic, logfile, '.gitignore', '.checkpatch.conf', '.gitlab-ci.yml']
skip_d_list = ['.git', 'OBJS', '.ci', 'tools', 'docs']

def logger_init():
  log = logging.getLogger('lic_check')
  if not debug:
    log.setLevel(logging.INFO)
  else:
    log.setLevel(logging.DEBUG)
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(logging.Formatter("%(message)s"))   
  log.addHandler(handler)
  return log                                                        

def file_lic_check(f):
  global lic_pat
  lic_pat_sz = len(lic_pat)
  count = 0
  err = 'OK'

  try:
    with open(f, 'r') as fchk:
      ret = 0
      for l in fchk:
        if count >= lic_pat_sz:
          return
        l = re.sub('[*#\-\/0-9]+', '', l)
        if l != lic_pat[count]:
          err = "FAIL!\nExpected:\n {exp:s}Actual:\n {act:s}".format(exp=lic_pat[count], act=l)
          ret = 1
          break 
        count += 1
      
  except IOError as e:
    logging.error('File {f:s} not found!'.format(f=f))
    ret = 1
  finally:
    logger.info('Checking {f:s} ... {err:s}'.format(f=f, err=err))
    return ret

def create_all_file_list():
  global file_list

  for dirpath, dirnames, files in os.walk(basedir):
    logger.debug('Found directory: {dir:s}'.format(dir=dirpath))
    for file_name in files:
       # Skip files in blacklist
       if file_name in skip_f_list:
         continue
       # Skip directories in blacklist
       skip_dir = 0
       for dd in dirpath.split('/'):
         if dd in skip_d_list:
           skip_dir = 1
           break
       if skip_dir == 1:
         logger.debug('Skipping {d:s} ... '.format(d=dirpath))
         continue
       file_list.append(dirpath + '/' + file_name)

def create_new_committed_file_list():
   global file_list
   cmd = 'git merge-base HEAD origin/master'
   common_commit = commands.getoutput(cmd)
   cmd = 'git rev-list ' + common_commit +'..HEAD'
   commits = commands.getoutput(cmd)
   s = re.split('\n+', commits)
   for ss in s:
     logger.debug('Find new changed files for {commit:s}'.format(commit=ss))
     cmd = 'git diff --name-only {c:s}~1 {c:s}'.format(c=ss)
     commits = commands.getoutput(cmd)
     t = re.split('\n+', commits)
     for tt in t:
       fd = tt.split('/')
       # Skip files in blacklist
       if fd[-1] in skip_f_list:
         continue
       # Skip directories in blacklist
       if fd[0] in skip_d_list:
         continue
       file_list.append(tt)

def main():
  global basedir
  global lic_pat
  global err_cnt
  global scan_all
  global logger

  logger = logger_init()

  try:
    with open(f_lic, 'r') as pat:
      lic_pat = pat.readlines()
      for i in range(0, len(lic_pat)):
        lic_pat[i] = re.sub('[*#\-\/0-9]+', '', lic_pat[i])

  except IOError as e:
    logging.error('File {f:s} not found!'.format(f=f_lic))
    exit(-1)

  if scan_all != 0:
    create_all_file_list()
  else:
    create_new_committed_file_list()

  for fi in file_list:
    err_cnt += file_lic_check(fi)

  logger.info('Found Errors: {errcnt:s}'.format(errcnt=str(err_cnt)))
  if err_cnt != 0:
    exit(-1)
  exit(0)

if __name__ == '__main__':
  sys.exit(main())

