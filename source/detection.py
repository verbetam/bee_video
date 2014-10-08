'''
Detection
=========

Implements multiple different types of detection. HAAR, SIFT...
'''

# Local modules
from video_loader import load_local
# System modules
import cv2, os, sys
import numpy as np

# ROI = {"tlcorner": (50, 50), "brcorner":(150, 150)}
ROI = (150, 150)

def cascadeDetect():
    cascade = cv2.CascadeClassifier("../classifier/v1/cascade.xml")

    videos = []
    for filename in os.listdir("../videos"):
        videos.append("../videos/" + filename)

    for videofile in videos:
        video = load_local(videofile)
        ret, frame = video.read()
        while ret:
            # frameGray = cv2.cvtColor(frame, cv2.cv.CV_BGR2GRAY)
            bees = cascade.detectMultiScale(frame, minNeighbors=2)
            for (x, y, w, h) in bees:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

            cv2.rectangle(frame, ROI, (ROI[0]+250, ROI[1]+250), (0, 255, 0), 2)

            cv2.imshow("Video", frame)

            ret, frame = video.read()

            key = cv2.waitKey(10)
            if key == 32: break
            elif key == 27: 
                exit()

def siftDetect():
    videos = []
    for filename in os.listdir("../videos"):
        videos.append("../videos/" + filename)

    for videofile in videos:
        video = load_local(videofile)
        ret, frame = video.read()
        while ret:
            frame = cv2.cvtColor(frame, cv2.cv.CV_BGR2GRAY)
            
            sift = cv2.SIFT()
            kp = sift.detect(frame, None)
            frame = cv2.drawKeypoints(frame, kp)
            cv2.imshow("Keypoints", frame)

            ret, frame = video.read()
            key = cv2.waitKey(10)
            if key == 32: break
            elif key == 27: 
                exit()

def exit():
    cv2.destroyAllWindows()
    sys.exit()

if __name__ == '__main__':
    cascadeDetect()