#!/usr/bin/env python

#Import things
import cv2 as cv
import numpy as np
import time
import queue

# Define the routines that will be done

def initialize_camera(cameraNumber,width,height):
    camera = cv.VideoCapture(cameraNumber);
    camera.set(3,width); # Width
    camera.set(4,height); # Height
    return camera
#end

def take_frame(camera,frameQueue):
    start = time.time();
    while not frameQueue.full():
        [ret,frame] = camera.read();
        #if ret == 1:
        frameQueue.put_nowait(frame);
            #print(str(time.time()));
            #print('Frame successfully taken');
        #else:
            #print('Frame not successfully taken');
        #end
    #end
    end = time.time()
    return (numberOfFrames/(end-start));
    #print('Calculated frame rate: %f' %(numberOfFrames/(end-start)))
#end

def process_frame(frameQueue,stackCounter):
    start = time.time();
    counter = 0;
    #for i in range(numberOfFrames):
    while not frameQueue.empty():
        frame = frameQueue.get_nowait();
        ret = cv.imwrite('Images\Stack_%i_%i.tiff' % (counter,stackCounter),frame[:,:,1]);
        counter = counter+1;
        #end
    #end
    end = time.time();
    return (end-start)
#end


# Int main
if __name__ == '__main__':

    # Initialize camera and camera resources
    width = 2464;
    height = 2056;

    camera = initialize_camera(1,2464,2056)
    numberOfFrames = 20;

    # Initialize queue that will be used
    frameQueue = queue.Queue(numberOfFrames);

    # Acquire "n" number of stacks
    stackRange = 10;
    for stackCounter in range(stackRange):
        print(str(stackCounter))
        fps = take_frame(camera,frameQueue);
        saveTime = process_frame(frameQueue,stackCounter);
        print(str(fps));
        print(str(saveTime));
    #end


    # Thank the camera for its time
    camera.release();


#end
