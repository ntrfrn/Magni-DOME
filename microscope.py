## PROJECT: MAGNI DOME
## FILE NAME: microscope.py
## VERSION: 1.1.0
## LAST MODIFICATION: 13 APR 2026

# local function for control
import logging
import numpy as np
import cv2
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc
from picamera2 import Picamera2
from libcamera import Transform
from libcamera import controls

# init local parameters for pi cam library
picam2 = Picamera2()
camConfig = picam2.create_preview_configuration(main={"size": (800, 600)}, transform=Transform(vflip=True))
picam2.configure(camConfig)


# scalebar setup
magnification = 4           # default : 4x
if magnification == 4:      # scale bar 100 um
    xLength = 54            # unit in pixel | horizontal length
yLength = 5                 # unit in pixel | vertical length
xStart = 25                 # starting point on x-axis
yStart = 575                # starting point on y-axis
alpha = 0.2                 # opacity | low(brighter) | high(darker)
scaleBar = np.ones((yLength, xLength, 3), dtype="uint8")*255    # create an overlay image

# live streaming function
def livePreview(stopRecord):
    logging.info("microscope.livePreview               : running")     # logging status
    picam2.start()      # starting camera  

    # camera setting
    picam2.set_controls({"ExposureValue": 0.5})     # adjust brightness [-8.0 to 8.0] (default 0.0)
    picam2.set_controls({"Contrast": 1.5})          # adjust contrast [1.0 to 32.0]
    picam2.set_controls({"Saturation": 0.0})        # turning to grayscale
    #picam2.set_controls({"AwbMode": controls.AwbModeEnum.Indoor})   # adjust white balance 
                                                                    # [Auto, Indoor, Tungsten, 
                                                                    #  Fluorescent, Daylight, Cloudy]
    #picam2.set_controls({"AwbEnable": False,
    #                     "ColourGains": (1.2, 1.1)})    # (Red, Blue)

    # init video codec "MPV4" for .mp4 video
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    rec = cv2.VideoWriter("record.mp4", fourcc, 30.0, (800, 600))   # (name, codec, framerate, resolution)

    # setup parameters for recording
    recordStatus = 0
    recordSetup = 0

    while True:
        frame = picam2.capture_array()      # get frame from the camera
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # overlay scalebar
        added_image = cv2.addWeighted(frame[yStart:(yStart+yLength),xStart:(xStart+xLength),:], alpha, 
                                      scaleBar[0:yLength,0:xLength,:],1-alpha,0)
        frame[yStart:(yStart+yLength),xStart:(xStart+xLength)] = added_image

        # starting live
        cv2.imshow("Microscope", frame)

        if not stopRecord():                # start recording
            if recordSetup == 0:
                recordSetup = 1
            rec.write(frame)
            recordStatus = 1

        if recordStatus == 1:               # stop recording
            if stopRecord():
                rec.release()
                recordStatus = 0
                recordSetup = 0
                logging.info("live.liveCam              : stop recording")
        
        # exit on ESC button
        key = cv2.waitKey(20)
        if key == 27:
            break

cv2.destroyAllWindows()
picam2.stop()   # stop streaming
logging.info("livePreview               : stopped streaming")     # logging status