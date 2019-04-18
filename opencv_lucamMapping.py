## Hopefully we can get something working
# Load the required modules
import cv2 as cv
import numpy as np
import os

# Lets start small by just loading in the camera(s)
# This actually means that the camera is now **streaming**
camera = cv.VideoCapture(0);

for i in range(1000):
    if camera.get(i) != -1 :
        print( "%i: %f" % (i,camera.get(i)) )

camera.release();

'''
3: Width
4: Height
5: FPS
6: FourCC (Codec)
10: Brightness
11: Contrast
14: Gain
15: Exposure (Looks like global)
22: Gamma
36: Aperature (Iris)
37: Settings
42: Backend
'''
