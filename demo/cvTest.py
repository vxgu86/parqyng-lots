#!/usr/bin/env python3.6

from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
import numpy as np
import cv2
import curses
import sys

base = BaseOverlay("base.bit")

stdscr = curses.initscr()
stdscr.nodelay(True)

frame_w = 640 
frame_h = 480

Mode = VideoMode(frame_w, frame_h, 24) 
hdmi_out = base.video.hdmi_out
hdmi_out.configure(Mode, PIXEL_BGR)
hdmi_out.start()

cap = cv2.VideoCapture(0)
print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Capture device is open?: " + str(cap.isOpened()))

#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
try:
    first_frame = None
    frame_type = "colo"
    run = True
    while run:
        ret, frame = cap.read()
        check_exit = stdscr.getch()
        if check_exit == ord('q'):
            run = False
        '''
        elif check_exit == ord('c'):
            frame_type = 'colo'
        elif check_exit == ord('g'):
            frame_type = 'gray'
        '''
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if first_frame is None:
            first_frame = gray
            continue

        frame_delta = cv2.absdiff(first_frame, gray)
        ret, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)
        gray = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        '''
        # Uploading commented out, broken code. #Itsahackathonthatsmyexcuse
        (cnts, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            if cv2.contourArea(c) < 10:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        '''
        if ret:
            outframe = hdmi_out.newframe()
            #if frame_type == 'colo':
            outframe[:] = frame
            '''
            elif frame_type == 'gray':
                outframe[:] = gray
            '''
            hdmi_out.writeframe(outframe)
        else:
            raise RuntimeError("Error while reading from camera")
except:
    print("Wait what?")
    print(sys.exc_info()[0])

curses.endwin()
print("Exiting, cleaning up...")
print("Releasing capture...")
cap.release()
print("destroying all windows...")
cv2.destroyAllWindows()
print("Stopping HDMI...")
hdmi_out.stop()
print("Deleting HDMI out...")
del hdmi_out
