## FILE NAME: main.py
## VERSION: 1.0.0
## LAST MODIFICATION: 31 MAR 2025

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
import stage

# input cmd class
class cmdInput(object):
    def __init__(self, cmd = 0):
        self.lock = threading.Lock()
        self.value = cmd            # init default cmd value to 0
    def cmdLock(self, cmd):
        self.lock.acquire()         # lock acquire
        self.value = cmd            # pass through input cmd value
        logging.info("lock acquired             : current cmd: %d", self.value)
        return self.value           # return locked cmd value to main function
    def cmdRelease(self):
        self.value = 0              # reset cmd value to 0
        self.lock.release()         # lock release
        logging.info("lock released             : current cmd: %d", self.value)

# init all local parameters
# general parameters
currentCmd = "NULL"
# manual control function
manualArray = [0, 0, 0, 0]

# setup GPIO pins for raspberry pi
GPIO.cleanup()                      # clean up all GPIO pins
GPIO.setmode(GPIO.BCM)              # using GPIO number to identify GPIO pins

# init GPIO pins for stage control
initStagePwm = threading.Thread(target=stage.initStagePwm, args=())
initStagePwm.start()

# init GPIO pins for projector control
initProj = threading.Thread(target=projector.initProj, args=())
initProj.start()

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

    time.sleep(1)       # stabilising
    logging.info("main                             : main software starting")

    while(True):
        cmd = cmdInput()
        tempCmd = int(input(f">> : "))      # input cmd
        currentCmd = cmd.cmdLock(tempCmd)   # preventing cmd deadlock

        # start recording
        if currentCmd == 1:
            logging.info("main                             : recording started")
            stopRecord = False
            livePreview.join(1)     # without timeout, it will never return to main thread
            cmd.cmdRelease()

        # stop recording
        if currentCmd == 2:
            stopRecording = True
            livePreview.join(1)
            logging.info("main                             : recording stopped")
            cmd.cmdRelease()

        # manually emag control
        if currentCmd == 3:
            # to input all coil
            for coilCnt in range (0, 4):
                print(">> coil", coilCnt+1, end="")
                manualArray[coilCnt] = int(input(f" :"))
            # calling manual control function
            manualControl = threading.Thread(target=electromagnets.manualControl, args=(manualArray, ))
            thread.append(manualControl)
            logging.info("main                      : manual control cmd sent")
            manualControl.start()
            cmd.cmdRelease()
        
        # predefined emag control start
        if currentCmd == 4:
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
            cmd.cmdRelease()
        
        # projector control
        if currentCmd == 5:
            # to input projector command
            print(">> projector: ", end="")
            projCmd = str(input())
            if projCmd == "image":
                print(">> image name: ", end="")
                imgName = str(input())
            else:
                imgName = "NULL"
            projCommand = threading.Thread(target=projector.projCommand, args=(projCmd, 
                                                                               imgName, ))
            thread.append(projCommand)
            logging.info("main                  : projector cmd sent")
            projCommand.start()
            cmd.cmdRelease()

        # z-stage control
        if currentCmd == 6:
            # to input stage direction command
            print(">> dirrection: ", end="")
            dirrCmd = str(input())
            # to input motor moving period
            print(">> period: ", end="")
            period = int(input())
            stageControl = threading.Thread(target=stage.stageControl, args=(dirrCmd,
                                                                             period, ))
            thread.append(stageControl)
            logging.info("main                  : stage control cmd sent")
            stageControl.start()
            cmd.cmdRelease()