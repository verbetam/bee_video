#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================
Keys
----
ESC - exit
'''

# System
import numpy as np
import cv2
from time import clock
from matplotlib import pyplot

# Project
from tools import model_bg2, morph_openclose, cross, handle_keys
import drawing
import keys

lk_params = dict( winSize  = (30, 30),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
                  minEigThreshold=1e-3)

ROI = (30, 290)
ROI_W = 500
ROI_H = 180

class App:
    def __init__(self, video_src, quiet=False, invisible=False, draw_contours=True, 
                 bgsub_thresh=16):
        self.quiet = quiet
        self.invisible = invisible
        self.drawTracks = True
        self.drawContours = draw_contours
        self.drawFrameNum = False

        self.areas = []

        # Learn the bg
        self.threshold = bgsub_thresh
        self.operator = cv2.BackgroundSubtractorMOG2(2000, self.threshold, True)
        model_bg2(video_src, self.operator)

        self.track_len = 10
        self.detect_interval = 5
        self.tracks = []
        self.cam = cv2.VideoCapture(video_src)
        self.frame_idx = 0
        self.arrivals = self.departures = 0

    def run(self, as_script=True):
        if self.invisible:
            cv2.namedWindow("Control")
        # cv2.waitKey()
        prev_gray = None
        prev_points = None

        
        while True:
            ret, frame = self.cam.read()
            if not ret:
                break
            fg_mask = self.operator.apply(frame, learningRate=-1)
            fg_mask = ((fg_mask == 255) * 255).astype(np.uint8)
            fg_mask = morph_openclose(fg_mask)
            # blob_centers(fg_mask, frame, True)


            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None:
                p0 = np.float32([point for point in prev_points]).reshape(-1, 1, 2)
                if drawing.draw_prev_points(frame, prev_points):
                    p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, frame_gray, p0, None, **lk_params)
                    for p_i, p_f in zip(p0.reshape(-1, 2), p1.reshape(-1, 2)):
                        result = cross(ROI, ROI_W, ROI_H, p_i, p_f)
                        if result is 1:
                            self.arrivals += 1
                            if not self.quiet:
                                print("Arrival")
                        elif result is -1:
                            self.departures += 1
                            if not self.quiet:
                                print("Departure")

                        if self.drawTracks:
                            drawing.draw_line(frame, tuple(p_i), tuple(p_f))

            # if len(self.tracks) > 0:
            #     # Find flow between last points and current points
            #     img0, img1 = prev_gray, frame_gray
            #     p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
            #     p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
            #     for p_i, p_f in zip(p0.reshape(-1, 2), p1.reshape(-1, 2)):
            #         result = cross(ROI, ROI_W, ROI_H, p_i, p_f)
            #         if result > 0:
            #             print("Arrival")
            #         elif result < 0:
            #             print("Departure")
            #         cv2.line(frame, tuple(p_i), tuple(p_f), RED)
            #     # Check for good matches
            #     p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
            #     d = abs(p0-p0r).reshape(-1, 2).max(-1)
            #     good = d < 1
            #     new_tracks = []
            #     for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
            #         if not good_flag:
            #             continue
            #         tr.append((x, y))
            #         if len(tr) > self.track_len:
            #             del tr[0]
            #         new_tracks.append(tr)
            #         # cv2.circle(frame, (x, y), 2, BLUE, -1)
            #     self.tracks = new_tracks
            #     cv2.polylines(frame, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))

            prev_gray = frame_gray
            contours, hier = drawing.draw_contours(frame, fg_mask)
            
            if len(self.areas) < 15000: 
                self.areas += drawing.draw_min_ellipse(contours, frame)

            prev_points = drawing.draw_blob_centers(contours, hier, frame, drawcenters=True)

            self.frame_idx += 1
            if not self.invisible:
                self.draw_overlays(frame, fg_mask)
                cv2.imshow('Tracking', frame)
                cv2.imshow("Mask", fg_mask)
                delay = 100
            else:
                delay = 1
            if handle_keys(delay) == 1:
                break
            
            # Should we continue running or yield some information about the current frame
            if as_script: continue
            else: pass

        return self.areas


    def draw_overlays(self, frame, fg_mask):
        drawing.draw_rectangle(frame, ROI, (ROI[0]+ROI_W, ROI[1]+ROI_H))
        if self.drawFrameNum:
            drawing.draw_frame_num(frame, self.frame_idx)
        if self.drawContours:
            pass
            # drawing.draw_contours(frame, fg_mask)


def main():
    print(__name__)
    clock()
    # video_src = "../videos/whitebg.h264"
    # video_src = "../videos/newhive_noshadow3pm.h264"
    # video_src = "../videos/video1.mkv"
    video_src = "../videos/newhive_shadow2pm.h264"


    app = App(video_src, invisible=False, bgsub_thresh=128-32)
    app.run()
    cv2.destroyAllWindows()

    # h, w = 2, 4
    # f, axarr = pyplot.subplots(h, w)
    # for i in xrange(h):
    #     for j in xrange(w):
    #         app = App(video_src, invisible=True, bgsub_thresh=2**(i*w+j+2))
    #         areas = app.run()

    #         axarr[i, j].set_title(
    #             "Threshold: {0}  Detections: {1}".format(app.threshold, len(areas)))
    #         axarr[i, j].hist(areas, 50, range=(0, 2000))
            
    #         cv2.destroyAllWindows()
    #         print("Arrivals: {0} Departures: {1}".format(app.arrivals, app.departures))
    #         print("{0} seconds elapsed.".format(clock()))
    # pyplot.show()

if __name__ == '__main__':
    main()
