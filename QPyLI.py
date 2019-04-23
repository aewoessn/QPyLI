#!/usr/bin/env python

# Import all of the modules required
import argparse
import queue
import cv2 as cv
import numpy as np
import zaber.serial as zs
import imageio
import matplotlib.pyplot as plt
import time

# Define the function that will be ran
def getArgs():
    parser = argparse.ArgumentParser(description='Interface with a USB camera via OpenCV and Zaber rotary stage. Note: This script requires that OpenCV and numpy are correctly installed. Additionally, if the rotary stage is being used, then zaber.serial must be installed.');

    # Positional input arguments
    #parser.add_argument('startCam',type=int,help='Start index for connecting to cameras (if unsure, set to 1)');
    #parser.add_argument('endCam',type=int,help='End index for connecting to cameras (if unsure, set to 1)');
    parser.add_argument('cameraIndex',type=int,help='Index of the camera to connect (starts at 0)');
    parser.add_argument('framesPerStack',type=int,help='Number of frames to burst acquire');
    parser.add_argument('numberOfStacks',type=int,help='Number of stacks to acquire (0 indicates Inf, Cntrl+C to stop)');
    collect = parser.add_mutually_exclusive_group();
    collect.add_argument('-c','--continuous',help='Continuous collection');
    collect.add_argument('-i','--finite',action='store_true',help='Finite collection');
    # Optional input arguments

    # Camera Controls
    camera = parser.add_argument_group('Camera Controls');
    camera.add_argument('-w','--width',type=int,help='Width (left-right) of each collected image');
    camera.add_argument('-e','--height',type=int,help='Height (top-bottom) of each collected image');
    camera.add_argument('-g','--gain',type=int,help='Gain (in dB) of camera');
    camera.add_argument('-f','--fps',type=int,help='Frames per second of camera (may not be accurate)');
    camera.add_argument('-a','--gamma',type=int,help='Gamma value for camera');
    camera.add_argument('-x','--exposure',type=int,help='Exposure value for camera (-16 is minimum))');
    camera.add_argument('-d','--dir',help='Directory to save images to (Defualt is current directory)');

    # Rotary stage controls
    rotary = parser.add_argument_group('Rotary Stage Controls');
    rotary.add_argument('-z','--zaber',action='store_true',help='Indicate if rotary stage is wanted');
    rotary.add_argument('-p','--port',help='Port of rotary stage (Defualt is "COM4")');
    rotary.add_argument('-v','--velocity',type=int,help='Velocity of rotary stage (in degrees per second, default is 100 degrees per second)');

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

def spoolRotaryStage(device,args):
    if args.velocity:
        velocity = args.velocity
    else:
        velocity = 100; # degrees per second

    velocityUnitScale = 4.551111111111111;
    resolution = int(device.send('get resolution').data); # ustep/step

    # (degrees/sec) * (ustep/degrees) = (ustep/sec) => (ustep/sec) * (1.6384 sec/ustep) = -data-
    data = round(velocityUnitScale*velocity*resolution);
    device.move_vel(data)
    #time.sleep(2);

#end

def translateRotaryStage(device,degreeDelt):
    positionUnitScale = 2.777777777777778;
    resolution = int(device.send('get resolution').data); # ustep/step
    data = round(positionUnitScale*degreeDelt*resolution);
    device.move_rel(data)
#end

def changeSettings(camera,args):
    # Change capture settings on camera
    if args.width:
        camera.set(3,args.width);
    if args.height:
        camera.set(4,args.height);
    if args.gain:
        camera.set(14,args.gain);
    if args.fps:
        camera.set(5,args.fps);
    if args.gamma:
        camera.set(22,args.gamma);
    if args.exposure:
        camera.set(15,args.exposure);
    return camera
#end

def takeFrameFast(camera,frameQueue):
    # Acquire frame or set of frames
    while not frameQueue.full():
        #if device:
        #    print(device.get_position())
        [ret,frame] = camera.read();
        frameQueue.put_nowait(frame);
    return frameQueue
#end

# Process frame(s)
def processFrameFast(frameQueue,stackCounter,args):
    # Export the images in the queue to a location

    # Check to see if directory is specified
    if args.dir:
        directory = args.dir;
    else:
        directory = './';

    # Initialze image write object
    writer = imageio.get_writer(directory + 'ImageStack_' + str(stackCounter+1) +'.tiff');

    # Export the queue
    while not frameQueue.empty():
        writer.append_data(frameQueue.get_nowait()[:,:,1]);

    writer.close();
    return frameQueue
#end

def processFrameSlow(imageMatrix,stackCounter,framesPerStack,args):
    # Check to see if directory is specified
    if args.dir:
        directory = args.dir;
    else:
        directory = './';

    # Initialze image write object
    writer = imageio.get_writer(directory + 'ImageStack_' + str(stackCounter+1) +'.tiff');

    # Export stack
    for i in range(framesPerStack):
        writer.append_data(imageMatrix[:,:,i])

    writer.close();
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
    camera = changeSettings(camera,args);

    if args.finite:
        # Finite collection

        # Initialize the rotary stage (if requested)
        if args.zaber:
            device = initializeRotaryStage(args);

        # Establish a matrix to fill images with
        imageMatrix = np.zeros((int(camera.get(4)),int(camera.get(3)),args.framesPerStack),dtype = 'uint8');

        # Find the amount that the rotary stage has to move in-between images
        degreeDelt = 180/args.framesPerStack;

        # Fill initial matrix with images
        for i in range(args.framesPerStack-1):
            # Move rotary stage
            if args.zaber:
                translateRotaryStage(device,degreeDelt);

            # Acquire image
            [ret,tmp] = camera.read();
            imageMatrix[:,:,i] = tmp[:,:,1];

        plt.figure();

        if args.numberOfStacks == 0:
            # Continue to take frames until Control+C (KeyboardInterrupt) is pressed
            counter = 0;
            try:
                while True:
                    # Acquire a new frame
                    [ret,tmp] = camera.read();
                    imageMatrix[:,:,args.framesPerStack-1] = tmp[:,:,1];

                    # Save the image set
                    processFrameSlow(imageMatrix,counter,args.framesPerStack,args);

                    # Move rotary stage
                    if args.zaber:
                        translateRotaryStage(device,degreeDelt);

                    # Shift the dataset such that the first image is not the last image, that way it can be overwritten
                    imageMatrix = np.roll(imageMatrix,-1,axis=2);

                    counter = counter+1;

                    plt.imshow(np.mean(imageMatrix,axis=2),cmap='gray');
                    plt.draw();
                    plt.pause(0.1);
            except KeyboardInterrupt:
                print(str(counter) + ' stack(s) acquired and saved');

        else:
            # Acquire a certain number of frames
            for i in range(args.numberOfStacks):
                # Acquire a new frame
                [ret,tmp] = camera.read();
                imageMatrix[:,:,args.framesPerStack-1] = tmp[:,:,1];

                # Save the image set
                processFrameSlow(imageMatrix,i,args.framesPerStack,args);

                # Move rotary stage
                if args.zaber:
                    translateRotaryStage(device,degreeDelt);

                # Shift the dataset such that the first image is not the last image, that way it can be overwritten
                imageMatrix = np.roll(imageMatrix,-1,axis=2);

                plt.imshow(np.mean(imageMatrix,axis=2),cmap='gray');
                plt.draw();
                plt.pause(0.1);

            print(str(args.numberOfStacks) + ' stacks(s) acquired and saved');
    else:
        # Continuous collection

        # Initialize the rotary stage (if requested)
        if args.zaber:
            device = initializeRotaryStage(args);

            # Spool up rotary stage
            spoolRotaryStage(device,args);

        # Establish queuing system (first in, first out)
        frameQueue = queue.Queue(args.framesPerStack);

        # Loop and acquire frames
        if args.numberOfStacks == 0:
            # Continue to take frames until Control+C (KeyboardInterrupt) is pressed
            counter = 0;
            try:
                while True:
                    # Fill the queue
                    frameQueue = takeFrameFast(camera,frameQueue);

                    # Export the queue
                    frameQueue = processFrameFast(frameQueue,counter,args);

                    counter = counter+1;
            except KeyboardInterrupt:
                print(str(counter) + ' stack(s) acquired and saved');
        else:
            for i in range(args.numberOfStacks):
                # Fill the queue
                frameQueue = takeFrameFast(camera,frameQueue);

                # Export the queue
                frameQueue = processFrameFast(frameQueue,i,args)
            print(str(args.numberOfStacks) + ' stacks(s) acquired and saved');

    # Close the camera port
    if args.zaber:
        device.stop();
    camera.release();

# Int main
if __name__ == '__main__':
    main();
