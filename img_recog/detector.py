import numpy as np
import cv2
import threading
import time

class Color_Track:
    def __init__(self):
        if not cv2.useOptimized():
            cv2.setUseOptimized(True)
        self.state = None
        # define kernel for gap closing in mask
        self.kernel = np.ones((5, 5), np.uint8)
        try:
            self.cap = cv2.VideoCapture(0)
        except:print("No camera detected")
        # contouring and edge changes:
        self._minVal = 45
        self._maxVal = 50
        # hsv bounds:
        self.lower = np.array([0, 57, 97])
        self.upper = np.array([15, 167, 255])
        self.frame = None
        self.mask = None
        self.cnt = None
        self.approx = None
        self.prev_xy=None
        self.xy = None
        self.thresh = True
        self.has_xy_changed = None

    def _masking(self):
        #Creates mask for color segmentation
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        # threshold of only skin colors:
        # mask=cv2.inRange(frame,lower,upper)chnaged to hsv instead of frame
        self.mask = cv2.inRange(hsv, self.lower, self.upper)
        # intended color:
        res = cv2.bitwise_and(self.frame, self.frame, mask=self.mask)
        self.mask = cv2.GaussianBlur(self.mask, (5, 5), 0)
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_CLOSE, self.kernel)

    def _contouring(self):
        #Finds most fitting contour around the hand
        self._minVal = int(cv2.getTrackbarPos('min_track', 'image'))
        self._maxVal = int( cv2.getTrackbarPos('max_track', 'image'))
        thresh = cv2.Canny(self.mask, self._minVal, self._maxVal)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.frame = cv2.drawContours(self.frame, contours, -1, (0, 255, 0), 3)
        try:
            self.cnt = max(contours, key=lambda x: cv2.contourArea(x))  # (Biggest area contour)
            self.frame = cv2.drawContours(self.frame, self.cnt, -1, (255, 0, 0), 3)
            # approximate the contour:
            epsilon = 0.001 * cv2.arcLength(self.cnt, True)
            self.approx = cv2.approxPolyDP(self.cnt, epsilon, True)
        except:
            print("adjust camera position...")

    def _convex(self):
        #Creates convex around selected contour
        try:
            hull = cv2.convexHull(self.approx, returnPoints=False)
            defects = cv2.convexityDefects(self.approx, hull)
            for i in range(defects.shape[0]):
                start, end, furthest, distance = defects[i, 0]
                start = tuple(self.approx[start][0])
                end = tuple(self.approx[end][0])
                far = tuple(self.approx[furthest][0])
                cv2.line(self.frame, start, end, [0, 255, 0], 2)
                cv2.circle(self.frame, far, 5, [255, 0, 255], -1)
                
            #pointer finger:
            topmost = tuple(self.cnt[self.cnt[:, :, 1].argmin()] [0] )
            self.prev_xy=self.xy
            self.xy = topmost
            cv2.circle(self.frame,topmost,8,[0,0,255],3)
        except:
            print("adjust camera position...")

    def _get_state(self):
        #Returns string of the current mode (DRW,MOV,ERS)
        cnt = self.cnt
        frame = self.frame
        try:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(radius)
            self.frame = cv2.circle(frame, center, radius, (0, 255, 200), 2)
            #area of main countour
            cnt_area = cv2.contourArea(cnt)
            #area of bounding circle
            circle_area = np.pi*(radius)**2
            proportion = (circle_area/cnt_area)
            
            if proportion>50:return("MOV")
            if proportion<50 and proportion>5:return("DRW")
            if proportion<5:return("ERS")
        except:
            pass

    def _get_xy(self):
        """Returns (x,y) pointer coordinates"""
        return self.xy

    def _has_xy_changed(self):
        #Sets boolean value for the event of changing xy coordinates.
        while True:
            prev_xy=self.prev_xy
            time.sleep(0.2)
            try:
                if not (self.xy[0]>(prev_xy[0] + 8) or \
                self.xy[1]>prev_xy[1] +8 or self.xy[0]+ 8<(prev_xy[0] ) or self.xy[1]+8<prev_xy[1] ):
                    self.has_xy_changed = False
                else:self.has_xy_changed = True
            except: pass

    def _rescale_frame(self,frame, percent = 150):
        #Rescales video frame
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    def main_loop(self):
        """Start detection loop"""
        delayer=threading.Thread(target=self._has_xy_changed)
        delayer.start()
        while True:
            _, self.frame = self.cap.read()
            self.frame = cv2.resize(self.frame, (200, 200))
            self.frame = cv2.flip(self.frame, 1)
            self.frame=self._rescale_frame(self.frame,300)

            self._masking()
            self._contouring()
            self._convex()
            position=self._get_xy()
            state=self._get_state()
            result=[position,state]
            if self.has_xy_changed:
                yield result
            cv2.imshow('mask', self.mask)
            cv2.imshow('frame', self.frame)

            if cv2.waitKey(1) == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


c=Color_Track()
for result in c.main_loop():
    try:
        print(result)
    except: pass



    




