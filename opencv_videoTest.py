## Hopefully we can get something working
# Load the required modules
import cv2 as cv
import numpy as np
import os
import time

# Lets start small by just loading in the camera(s)
# This actually means that the camera is now **streaming**
camera = cv.VideoCapture(0);

# In order to make sure that we have a good frame, elts set the appropriate size of the image
width = 2464;
height = 2056;
camera.set(3,width); # Width
camera.set(4,height); # Height

## How about we take a video with 10 frames
# Lets print our working directory
print("Current working directory:");
print(os.getcwd());

# Initialze the matrix where frames will be stored
numberOfFrames = 10;
allFrames = np.zeros((height,width,3,numberOfFrames),np.uint8);

# Store frames to matrix
start = time.time()

for i in range(numberOfFrames):
    [ret,allFrames[:,:,:,i]] = camera.read();

end = time.time()
print('Video Took: %f' %(end - start))

# Save just the first channel from each frame
for i in range(numberOfFrames):
    cv.imwrite('test_%i.tiff' % i,allFrames[:,:,1,i])

# This is the ending statement, which releases the camera
print('Releasing camera');
camera.release();
