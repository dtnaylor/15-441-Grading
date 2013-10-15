#!/usr/bin/python

import os
import shutil

RESULTS_DIR = './results'
NOTES_DIR = './notes'
GRADES_DIR = './grades'
COURSE_DIR = '/afs/andrew/course/15/441-641'

def copy_to_student_dir(file, dir):
    andrewid = file.split('-')[0]
    studir = os.path.join(COURSE_DIR, andrewid)
    srcpath = os.path.join(dir, file)
    dstpath = os.path.join(studir, file)
    print 'Copying %s\tto %s' % (srcpath, dstpath)
    shutil.copyfile(srcpath, dstpath)
    

for file in os.listdir(RESULTS_DIR):
    copy_to_student_dir(file, RESULTS_DIR)

for file in os.listdir(GRADES_DIR):
    copy_to_student_dir(file, GRADES_DIR)

for file in os.listdir(NOTES_DIR):
    copy_to_student_dir(file, NOTES_DIR)
