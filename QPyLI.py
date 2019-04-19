#!/usr/bin/env python

# Import all of the modules required
import argparse
import queue
import cv2 as cv
import numpy as np


# Define the function that will be ran
def getArgs():
    parser = argparse.ArgumentParser(description='Interface with a USB camera via OpenCV. Note: This script requires that OpenCV and numpy are correctly installed.');

    # Positional input arguments
    #parser.add_argument('startCam',type=int,help='Start index for connecting to cameras (if unsure, set to 1)');
    #parser.add_argument('endCam',type=int,help='End index for connecting to cameras (if unsure, set to 1)');
    parser.add_argument('cameraIndex',type=int,help='Index of the camera to connect (starts at 0)');
    parser.add_argument('framesPerStack',type=int,help='Number of frames to burst acquire');
    parser.add_argument('numberOfStacks',type=int,help='Number of stacks to acquire (0 indicates Inf)');

    # Optional input arguments
    parser.add_argument('-w','--width',type=int,help='Width (left-right) of each collected image');
    parser.add_argument('-e','--height',type=int,help='Height (top-bottom) of each collected image');
    parser.add_argument('-g','--gain',type=int,help='Height (top-bottom) of each collected image');
    parser.add_argument('-f','--fps',type=int,help='Height (top-bottom) of each collected image');
    parser.add_argument('-a','--gamma',type=int,help='Height (top-bottom) of each collected image');
    parser.add_argument('-d','--dir',help='Directory to save images to');
    return(parser.parse_args());

#--Function Definions--
#-------------------------------------------------------------------------------

def initializeCamera(cameraNumber):
    # Initialize the camera
    camera = cv.VideoCapture(cameraNumber);
    return camera
#end

def changeSettings(camera,args):
    # Change capture settings on camera
    if args.width:
        camera.set(3,args.width);
    elif args.height:
        camera.set(4,args.height);
    elif args.gain:
        camera.set(14,args.gain);
    elif args.fps:
        camera.set(5,args.fps);
    elif args.gamma:
        camera.set(22,args.gamma);
#end

def takeFrame(camera,frameQueue):
    # Acquire frame or set of frames
    while not frameQueue.full():
        [ret,frame] = camera.read();
        frameQueue.put_nowait(frame);
    return frameQueue
#end

# Process frame(s)
def processFrame(frameQueue,stackCounter,args):
    # Export the images in the queue to a location

    # Initialize counter
    counter = 1;

    # Check to see if directory is specified
    if args.dir:
        directory = args.dir;
    else:
        directory = './';

    # Export the queue
    while not frameQueue.empty():
        ret = cv.imwrite(directory + 'ImageStack_' + str(stackCounter+1) + '_' + str(counter) + '.tiff',frameQueue.get_nowait());
        counter = counter+1;
    return frameQueue
#end

#--Main Definition--
#-------------------------------------------------------------------------------
def main():
    # Collect input arguments
    args = getArgs();

    # Initialize the camera, and verify that camera object is linked to an actual camera
    camera = initializeCamera(args.cameraIndex);

    if camera.isOpened():
        print('Successfully connected to camera:' + str(args.cameraIndex));
    else:
        print('Could not connect to camera:' + str(args.cameraIndex));

    # Change settings of camera if needed
    changeSettings(camera,args);

    # Establish queuing system (first in, first out)
    frameQueue = queue.Queue(args.framesPerStack);

    # Loop and acquire frames
    for i in range(args.numberOfStacks):
        # Fill the queue
        frameQueue = takeFrame(camera,frameQueue);

        # Export the queue
        frameQueue = processFrame(frameQueue,i,args)

    # Close the camera port
    camera.release();

# Int main
if __name__ == '__main__':
    main();
