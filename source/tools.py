import cv2
import numpy as np
import keys


def model_bg2(video, operator):
    vidcapture = cv2.VideoCapture(video)
    # Initialize from first N frames
    N = 500
    for _ in range(N):
        ret, frame = vidcapture.read()
        if ret:
            operator.apply(frame, learningRate=-1)
        else:
            break
    vidcapture.release()


def morph_openclose(image, kernel_size=3, iterations=1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    new_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    return cv2.morphologyEx(new_image, cv2.MORPH_OPEN, kernel, iterations=iterations)


def handle_keys(delay):
    key = cv2.waitKey(delay)
    if key == keys.SPACE:
        key = cv2.waitKey()
    if key == keys.Q:
        exit()
    if key == keys.ESC:
        return 1


def cross(rect, width, height, pt0, pt1):
        """
        Determines if the points enter or leave the rectangle.
        Returns 1 if the points enter the rect, -1 if it leaves, or 0 if neither.
        """
        x0 = pt0[0]
        y0 = pt0[1]
        x1 = pt1[0]
        y1 = pt1[1]

        p0in = rect[0] < x0 < rect[0] + width and rect[1] < y0 < rect[1] + height
        p1in = rect[0] < x1 < rect[0] + width and rect[1] < y1 < rect[1] + height

        if not p0in and p1in:
            return 1
        elif p0in and not p1in:
            return -1
        else:
            return 0