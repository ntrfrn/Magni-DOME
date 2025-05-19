## FILE NAME: projector.py
## VERSION: 1.0.0
## LAST MODIFICATION: 31 MAR 2025

import logging
import RPi.GPIO as GPIO
import time

# init all global parameters
pwmFwd = None
pwmRev = None

# init GPIO parameters and pwm control function
def initStagePwm():
    # calling global parameters
    global motorFwd, motorRev, pwmFwd, pwmRev

    # define raspberry pi ports
    motorFwd = 12                       # motor forward to port 12
    motorRev = 13                       # motor reverse to port 13

    # setup GPIO pins for raspberry pi
    GPIO.setup(motorFwd, GPIO.OUT)      # setup pin 12 to be output pin
    GPIO.setup(motorRev, GPIO.OUT)      # setup pin 13 to be output pin

    # setup pwm parameters to pins
    pwmFwd = GPIO.PWM(motorFwd, 1000)   # setup pin 12 to be pwm port with 1000 Hz frequency
    pwmRev = GPIO.PWM(motorRev, 1000)   # setup pin 13 to be pwm port with 1000 Hz frequency

    # start pwm function
    pwmFwd.start(0)
    pwmRev.start(0)

    logging.info("stage              : stage control parameters initialised")     # logging status

# z-stage control function
def stageControl(dirr, cycleTime):
    # calling global parameters
    global pwmFwd, pwmRev

    # to move stage up
    if dirr == "up":
        pwmFwd.ChangeDutyCycle(100) # fwd pin activate
        pwmRev.ChangeDutyCycle(0)   # rev pin deactivate
        logging.info("stage.stageControl               : stage up direction")     # logging status

    # to move stage down    
    if dirr == "down":
        pwmRev.ChangeDutyCycle(100) # fwd pin deactivate
        pwmFwd.ChangeDutyCycle(0)   # rev pin activate
        logging.info("stage.stageControl               : stage down direction")     # logging status
    
    time.sleep(cycleTime)           # voltage supply for input time
    
    pwmFwd.ChangeDutyCycle(0)       # fwd pin deactivate
    pwmRev.ChangeDutyCycle(0)       # rev pin deactivate