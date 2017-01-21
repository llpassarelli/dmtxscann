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
from PIL import Image
import os
import sys
import datetime
import time
from pydmtx import DataMatrix


def data_matrix_demo(cap):
    window_name = "datamatrix scanner"
    frame_number = 0
    need_to_save = False

    while True:
        e1 = cv2.getTickCount()
        ret, frame = cap.read()
        if not ret:
            break
        imr = cv2.resize(
            frame,
            None,
            fx=0.5,
            fy=0.5,
            interpolation=cv2.INTER_CUBIC)
        try:
            '''MEAN TRIGGER - DETECTA O OBJETO NO CENTRO DA FRAME'''
            roi = imr[80:160, 80:240]
            imdecode = imr.copy()
            # imr[80:160, 80:240] = 255
            means = cv2.mean(roi)
            mean = str("%d" % means[0])
            # print('mean:', mean)
            cv2.rectangle(imr, (80, 80), (240, 160), (255, 255, 255), 1)
            cv2.line(imr, (160, 70), (160, 170), (0, 0, 255), 1)
            cv2.line(imr, (70, 120), (250, 120), (0, 0, 255), 1)
            cv2.putText(imr, mean, (150, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, .4, (255, 0, 0), 1)

            if means[0] > 100 and means[0] < 190:
                cv2.rectangle(imr, (80, 80), (240, 160), (255, 255, 255), 1)
                cv2.line(imr, (160, 80), (160, 160), (0, 255, 0), 1)
                cv2.line(imr, (80, 120), (240, 120), (0, 255, 0), 1)
                code, points = decode(imdecode)
                for i, point in enumerate(points):
                    cv2.line(imr, point, points[i - 1], (0, 255, 0), 1)
                    cv2.putText(
                        imr, code, points[0], cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 250, 0), 1)

        except Exception:
            print "error decode"
            pass

        e2 = cv2.getTickCount()
        t = (e2 - e1) / cv2.getTickFrequency()
        fps = str("%.0f" % (1 / t))
        msg = "fps: " + str(fps)
        t = str("%.3f" % t)
        msg = "time (s): " + str(t)
        cv2.rectangle(imr, (0, 0), (90, 14), (0, 0, 0), -1)
        cv2.putText(imr, t + 's ' + fps + 'fps', (1, 10),
                    cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 250, 0), 1)
        cv2.imshow(window_name, imr)
        key = cv2.waitKey(1)
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
        st = datetime.datetime.now()
        img = Image.fromarray(imgcv2)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        dm_read = DataMatrix()
        code = dm_read.decode(
            img.size[0],
            img.size[1],
            buffer(
                img.tostring()),
            timeout=80,
            maxcount=1,
            corrections=3)
        end = datetime.datetime.now()
        if dm_read.count() == 1:
            # print code, end - st
            time = end - st

            print dm_read.stats(1), "t:", str(time)[6:]
            points = dm_read.stats(1)[1]
            # print "points:", points
            # os.system("beep -f1296 -l10")
    except Exception:
        print "error decode"
        pass

    return code, points

if __name__ == '__main__':
    print __doc__

    if len(sys.argv) == 1:
        cap = cv2.VideoCapture(1)
    else:
        cap = cv2.VideoCapture(sys.argv[1])
        if not cap.isOpened():
            cap = cv2.VideoCapture(int(sys.argv[1]))

    if not cap.isOpened():
        print 'Cannot initialize video capture'
        sys.exit(-1)
    data_matrix_demo(cap)
