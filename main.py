## PROJECT: MAGNI-DOME
## FILE NAME: main.py
## VERSION: 1.1.0
## LAST MODIFICATION: 23 MAY 2025

# main function
# import libraries
import logging
import threading
import time
import RPi.GPIO as GPIO

# import local files
import electromagnets
import microscope
import projector
import utilities

# input cmd class
class cmdInput(object):
    def __init__(self, cmdSts = 0):
        self.lock = threading.Lock()
        self.value = cmdSts             # init default cmd value to 0
    def cmdLock(self, cmdSts):
        self.lock.acquire()             # lock acquire
        self.value = cmdSts             # pass through input cmd value
        logging.info("lock acquired             : current cmd: %d", self.value)
        return self.value               # return locked cmd value to main function
    def cmdRelease(self):
        self.value = 0                  # reset cmd value to 0
        self.lock.release()             # lock release
        logging.info("lock released             : current cmd: %d", self.value)
    def cmdLookup(self, cmdSts):
        cmdList = ["help", "capture", "start record", "stop record", "manual", 
                   "predef", "proj", "stage", "fine stage", "led"]
        if cmdSts in cmdList:
            self.value = cmdList.index(cmdSts)
        return self.value

# init all local parameters
# general parameters
currentCmd = "NULL"
# manual control function
manualArray = [0, 0, 0, 0]
# led control function
ledCmd = 0

# setup GPIO pins for raspberry pi
GPIO.cleanup()                      # clean up all GPIO pins
GPIO.setmode(GPIO.BCM)              # using GPIO number to identify GPIO pins

# main function
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    thread = list()

    # livePreview thread
    # starting live streaming
    logging.info("main                             : start livePreview thread")
    stopRecord = True
    livePreview = threading.Thread(target=microscope.livePreview, args=(lambda : stopRecord, ))
    thread.append(livePreview)
    livePreview.start()

    # init GPIO for projector
    projector.initProj()

    # ledControl thread
    logging.info("main                             : start ledControl thread")
    utilities.initUtil()
    #utilities.ledControl(ledCmd)

    time.sleep(1)       # stabilising
    logging.info("main                             : main software starting")

    while(True):
        cmdSts = cmdInput()
        tempCmd = str(input(f">> main : "))      # input cmd
        lookCmd = cmdSts.cmdLookup(tempCmd)
        currentCmd = cmdSts.cmdLock(lookCmd)   # preventing cmd deadlock

        if currentCmd == 0:
            print("----------command list----------")
            print("start record\t:\tstart recording video\n" \
                  "stop record\t:\tstop recording video\n" \
                  "manual\t\t:\telectromagnets manual control\n" \
                  "predef\t\t:\telectromagnets predefined control\n" \
                  "proj\t\t:\tprojector control\n" \
                  "led\t\t:\tled ring control")

        elif currentCmd == 1:
            logging.info("main                             : image capture")
            # reserve for image capture function

        # start recording
        elif currentCmd == 2:
            logging.info("main                             : recording started")
            stopRecord = False
            livePreview.join(1)     # without timeout, it will never return to main thread
            cmdSts.cmdRelease()

        # stop recording
        elif currentCmd == 3:
            stopRecord = True
            livePreview.join(1)
            logging.info("main                             : recording stopped")
            cmdSts.cmdRelease()

        # manually emag control
        elif currentCmd == 4:
            # to input all coil
            for coilCnt in range (0, 4):
                print(">> coil", coilCnt+1, end="")
                manualArray[coilCnt] = int(input(f" :"))
            # calling manual control function
            manualControl = threading.Thread(target=electromagnets.manualControl, args=(manualArray, ))
            thread.append(manualControl)
            logging.info("main                      : manual control cmd sent")
            manualControl.start()
            cmdSts.cmdRelease()
        
        # predefined emag control start
        elif currentCmd == 5:
            # to input predefined options
            print(">> mode: ", end="")
            mode = str(input())
            if mode == "stop":
                field = 0   # set to 0
                freq = 0    # set to 0
            else:
                print(">> field power: ", end="")
                field = float(input())  # magnetic field at the workspace (mT)
                print(">> frequency: ", end="")
                freq = int(input())     # frequency (Hz)
            # to call predefined control function
            preDefControl = threading.Thread(target=electromagnets.preDefControl, args=(mode,
                                                                                 field,
                                                                                 freq, ))
            logging.info("main                      : predefined control cmd sent")
            preDefControl.start()
            cmdSts.cmdRelease()
        
        # projector control
        elif currentCmd == 6:
            # to input projector command
            print(">> projector: ", end="")
            projCmd = str(input())
            if projCmd == "image":
                print(">> image name: ", end="")
                imgName = str(input())
            else:
                imgName = "NULL"
            projector.projCommand(projCmd, imgName)
            logging.info("main                  : projector cmd sent")
            cmdSts.cmdRelease()

        # z-stage control
        # this function is to control the stage movement by input stage distance
        elif currentCmd == 7:
            # to input stage direction command
            print(">> direction: ", end="")
            dirCmd = str(input())
            # to input motor moving period
            print(">> distance (mm): ", end="")
            disCmd = float(input())  # linear distance (mm)
            stageControl = threading.Thread(target=utilities.stageControl, args=(dirCmd, disCmd))
            thread.append(stageControl)
            stageControl.start()
            logging.info("main                  : stage control cmd sent")
            cmdSts.cmdRelease()

        # fine z-stage control
        # this function is to control the stage movement by input motor step count
        elif currentCmd == 8:
            # to input step count number
            print(">> step count: ", end="")
            stepCnt = int(input())      # (+) : upward direction
                                        # (-) : downward direction
            utilities.fineStageControl(stepCnt)

        # led ring control
        elif currentCmd == 9:
            print(">> led cmd: ", end="")
            ledSts = str(input())
            if ledSts == "off":
                ledCmd = 0
            elif ledSts == "on":
                ledCmd = 100
            elif ledSts == "bright":
                print(">> brightness: ", end="")
                ledBright = int(input())
                if ledBright > 100:
                    logging.info("main                  : brightness exceed 100%")
                else:
                    ledCmd = ledBright
            else:
                logging.info("main                  : led command error")
            utilities.ledControl(ledCmd)
            logging.info("main                  : led control cmd sent")
            cmdSts.cmdRelease()

        else:
            logging.info("main                  : input command error")
            cmdSts.cmdRelease()