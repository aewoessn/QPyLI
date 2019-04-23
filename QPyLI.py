#!/usr/bin/env python

# Import all of the modules required
import argparse
import queue
import cv2 as cv
import numpy as np
import zaber.serial as zs

# Define the function that will be ran
def getArgs():
    parser = argparse.ArgumentParser(description='Interface with a USB camera via OpenCV and Zaber rotary stage. Note: This script requires that OpenCV and numpy are correctly installed. Additionally, if the rotary stage is being used, then zaber.serial must be installed.');

    # Positional input arguments
    #parser.add_argument('startCam',type=int,help='Start index for connecting to cameras (if unsure, set to 1)');
    #parser.add_argument('endCam',type=int,help='End index for connecting to cameras (if unsure, set to 1)');
    parser.add_argument('cameraIndex',type=int,help='Index of the camera to connect (starts at 0)');
    parser.add_argument('framesPerStack',type=int,help='Number of frames to burst acquire');
    parser.add_argument('numberOfStacks',type=int,help='Number of stacks to acquire (0 indicates Inf, Cntrl+C to stop)');

    # Optional input arguments

    # Camera Controls
    camera = parser.add_argument_group('Camera Controls');
    camera.add_argument('-w','--width',type=int,help='Width (left-right) of each collected image');
    camera.add_argument('-e','--height',type=int,help='Height (top-bottom) of each collected image');
    camera.add_argument('-g','--gain',type=int,help='Gain (in dB) of camera');
    camera.add_argument('-f','--fps',type=int,help='Frames per second of camera (may not be accurate)');
    camera.add_argument('-a','--gamma',type=int,help='Gamma value for camera');
    camera.add_argument('-d','--dir',help='Directory to save images to (Defualt is current directory)');

    # Rotary stage controls
    rotary = parser.add_argument_group('Rotary Stage Controls');
    rotary.add_argument('-z','--zaber',action='store_true',help='Indicate if rotary stage is wanted');
    rotary.add_argument('-p','--port',help='Port of rotary stage (Defualt is "COM4")');
    rotary.add_argument('-v','--velocity',help='Velocity of rotary stage (in degrees per second)');

    return(parser.parse_args());

#--Function Definions--
#-------------------------------------------------------------------------------

def initializeCamera(cameraNumber):
    # Initialize the camera
    camera = cv.VideoCapture(cameraNumber);
    return camera
#end

def initializeRotaryStage(args):
    if args.port:
        port = zs.AsciiSerial(args.port.upper());
    else:
        port = zs.AsciiSerial('COM4');

    device = zs.AsciiDevice(port,1);

    return device
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

    # Initialize the rotary stage (if requested)
    if args.zaber:
        device = initializeRotaryStage(args);

    # Establish queuing system (first in, first out)
    frameQueue = queue.Queue(args.framesPerStack);

    # Loop and acquire frames
    if args.numberOfStacks == 0:
        # Continue to take frames until Control+C (KeyboardInterrupt) is pressed
        counter = 0;
        try:
            while True:
                # Fill the queue
                frameQueue = takeFrame(camera,frameQueue);

                # Export the queue
                frameQueue = processFrame(frameQueue,counter,args);

                counter = counter+1;
        except KeyboardInterrupt:
            print(str(counter) + ' stack(s) acquired and saved');
    else:
        for i in range(args.numberOfStacks):
            # Fill the queue
            frameQueue = takeFrame(camera,frameQueue);

            # Export the queue
            frameQueue = processFrame(frameQueue,i,args)
        print(str(args.numberOfStacks) + ' stacks(s) acquired and saved');

    # Close the camera port
    camera.release();

# Int main
if __name__ == '__main__':
    main();
