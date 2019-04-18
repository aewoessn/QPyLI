# Python program to illustrate
# saving an operated video

# organize imports
import numpy as np
import cv2

# This will return video from the first webcam on your computer.
camera = cv2.VideoCapture(0)

width = 2464;
height = 2056;
camera.set(3,width); # Width
camera.set(4,height); # Height

# Define the codec and create VideoWriter object
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 60.0, (width, height))

# loop runs if capturing has been initialized.
while(True):
    # reads frames from a camera
    # ret checks return at each frame
    ret, frame = camera.read()

    # output the frame
    out.write(frame)

    # The original input frame is shown in the window
    cv2.imshow('Original', frame)

    # Wait for 'a' key to stop the program
    if cv2.waitKey(1) & 0xFF == ord('a'):
        break

# Close the window / Release webcam
camera.release()

# After we release our webcam, we also release the output
out.release()

# De-allocate any associated memory usage
cv2.destroyAllWindows()
