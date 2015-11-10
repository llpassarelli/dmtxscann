#!/usr/bin/env python

'''
Python Data Matrix Scanner

<llpassarelli@gmail.com>
    
use opencv and libdmtx

   q or ESC - exit
   space - save current image as datamatrix<frame_number>.jpg
'''

import cv2
import numpy as np
import sys
from PIL import Image
import os
import datetime
import time

from pydmtx import DataMatrix

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_squares(img0):
    img = cv2.GaussianBlur(img0, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            _, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.1*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 2000 and cv2.contourArea(cnt) < 30000 and cv2.isContourConvex(cnt):
                    x,y,w,h = cv2.boundingRect(cnt)
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    # print max_cos, cv2.contourArea(cnt)
                    i=10
                    if max_cos < 0.18:
                        squares.append(cnt)
                        roi = img0[y-i:y+h+i, x-i:x+w+i]
                        code = decode(roi)
                        return squares

def data_matrix_demo(cap):
    window_name = "datamatrix webcam scanner by llpassarelli"
    frame_number = 0
    need_to_save = False

    while 1:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        squares = find_squares(frame)
        cv2.drawContours( frame, squares, -1, (0, 250, 0), 1 )
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30)
        c = chr(key & 255)
        if c in ['q', 'Q', chr(27)]:
            break

        if c == ' ':
            need_to_save = True

        if need_to_save and codes:
            filename = ("datamatrix%03d.jpg" % frame_number)
            cv2.imwrite(filename, frame)
            print "Saved frame to " + filename
            need_to_save = False

        frame_number += 1

def decode(imgcv2):
    code = ""
    try:
        img = Image.fromarray(imgcv2)
        dm_read = DataMatrix()
        code = dm_read.decode(img.size[0], img.size[1], buffer(img.tostring()), timeout=120, maxcount=1, corrections=1)
        date = datetime.datetime.now()
        if dm_read.count() == 1:
            print code, date
            cv2.imshow(code, imgcv2)
    except Exception:
        pass
    
    return code

    #if dm_read.count() == 1:
       # os.system("beep -f1296 -l10")



if __name__ == '__main__':
    print __doc__

    if len(sys.argv) == 1:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(sys.argv[1])
        if not cap.isOpened():
            cap = cv2.VideoCapture(int(sys.argv[1]))

    if not cap.isOpened():
        print 'Cannot initialize video capture'
        sys.exit(-1)
    #webcam delay
    print "Inicializando"
    time.sleep(3)
    data_matrix_demo(cap)
