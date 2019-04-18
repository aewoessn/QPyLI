## Hopefully we can get something working
# Load the required modules
import cv2 as cv
import numpy as np
import os

# Lets start small by just loading in the camera(s)
# This actually means that the camera is now **streaming**
camera = cv.VideoCapture(0);

# In order to make sure that we have a good frame, elts set the appropriate size of the image
camera.set(3,2464); # Width
camera.set(4,2056); # Height

## How about we take a single image
# Lets print our working directory
print("Current working directory:");
print(os.getcwd());

# Lets grab a frame from the video stream (take an image)
[ret,frame] = camera.read();

if ret == 1:
    print('Frame successfully taken');
else:
    print('Frame was not successfully taken');

# Save only the first slice (red channel) of the frame
# Average out the RGB image
frame2 = np.mean(frame,axis = 2);

# Write the image using imwrite
ret = cv.imwrite('test.tiff',frame2);

if ret == 1:
    print('Frame successfully saved');
else:
    print('Frame was not successfully saved');

# Take 10 images with the camera

# This is the ending statement, which releases the camera
print('Releasing camera');
camera.release();
