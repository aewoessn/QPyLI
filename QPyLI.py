#!/usr/bin/env python

# Import all of the modules required
import cv2 as cv
import numpy as np
import argparse

# Define the routines that will be done
def parseArgs():
    parser = argparse.ArgumentParser(description='Interface with a USB camera via OpenCV')

    # Positional input arguments

    # Optional input arguments



# Initialize the camera
def initialize_camera(cameraNumber,width,height):
    camera = cv.VideoCapture(cameraNumber);
    camera.set(3,width); # Width
    camera.set(4,height); # Height
    return camera
#end

# Take frame(s)
def take_frame(camera,frameQueue):
    start = time.time();
    while not frameQueue.full():
        [ret,frame] = camera.read();
        frameQueue.put_nowait(frame);
    end = time.time()
    return (numberOfFrames/(end-start));
#end

# Process frame(s)
def process_frame(frameQueue,stackCounter):
    start = time.time();
    counter = 0;
    while not frameQueue.empty():
        frame = frameQueue.get_nowait();
        ret = cv.imwrite('Images\Stack_%i_%i.tiff' % (counter,stackCounter),frame[:,:,1]);
        counter = counter+1;
    end = time.time();
    return (end-start)
#end


def main():
    # Collect input arguments

# Int main
if __name__ == '__main__':
    main();
'''
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
'''
