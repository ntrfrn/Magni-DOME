## PROJECT: MAGNI DOME
## FILE NAME: utilities.py
## VERSION: 1.1.0
## LAST MODIFICATION: 20 Nov 2025

import logging
import RPi.GPIO as GPIO
import time

# init all global parameters
# define raspberry pi port
LED_PIN = 18                # LED signal to GPIO18 (pin 12)
STEP_IN1 = 21               # stepping motor input 1 to GPIO21 (pin 40)
STEP_IN2 = 20               # stepping motor input 2 to GPIO20 (pin 38)
STEP_IN3 = 16               # stepping motor input 3 to GPIO16 (pin 36)
STEP_IN4 = 12               # stepping motor input 4 to GPIO12 (pin 32)
LIMIT_IN = 19               # limit switch input pin to GPIO19 (pin 35)
LIMIT_OUT = 26              # limit switch output pin to GPIO26 (pin 37)
# stage parameters
stepHold = 0.001            # stepping motor holding period [increasing for slower speed]
motorPins = [STEP_IN1,      # stepping motor pins for squential run
             STEP_IN2, 
             STEP_IN3, 
             STEP_IN4]
stepSeq = [[1, 0, 0, 1],    # stepping motor sequences
           [1, 0, 0, 0],
           [1, 1, 0, 0],
           [0, 1, 0, 0],
           [0, 1, 1, 0],
           [0, 0, 1, 0],
           [0, 0, 1, 1],
           [0, 0, 0, 1]]

def initUtil():
    global ledPwm

    # setup GPIO pins for raspberry pi
    GPIO.setup(LED_PIN, GPIO.OUT)           # setup GPIO18 to be output
    GPIO.setup(STEP_IN1, GPIO.OUT)          # setup GPIO21 to be output
    GPIO.setup(STEP_IN2, GPIO.OUT)          # setup GPIO20 to be output
    GPIO.setup(STEP_IN3, GPIO.OUT)          # setup GPIO16 to be output
    GPIO.setup(STEP_IN4, GPIO.OUT)          # setup GPIO12 to be output
    GPIO.setup(LIMIT_IN, GPIO.IN)           # setup GPIO19 to be input
    GPIO.setup(LIMIT_OUT, GPIO.OUT)         # setup GPIO26 to be output

    GPIO.output(LIMIT_OUT, GPIO.HIGH)       # assign HIGH to limit switch NC channel
    gpioMotorReset()

    ledPwm = GPIO.PWM(LED_PIN, 1000)        # create PWM at 1000 Hz frequency
    ledPwm.start(0)                         # starting PWM at 0 duty cycle

    logging.info("utilities                 : LED parameters initialised")
    logging.info("utilities                 : stepping motor parameters initialised")

def gpioMotorReset():
    # set stepping motor GPIO output to be low
    GPIO.output(STEP_IN1, GPIO.LOW)
    GPIO.output(STEP_IN2, GPIO.LOW)
    GPIO.output(STEP_IN3, GPIO.LOW)
    GPIO.output(STEP_IN4, GPIO.LOW)

# led control function
def ledControl(ledCmd):
    logging.info("utilities.ledControl      : led control cmd received")
    ledPwm.ChangeDutyCycle(ledCmd)          # changing duty cycle according to input command

def stageControl(dirCmd, disCmd):
    logging.info("utilities.stageControl    : stage control cmd received")
    motorCnt = 0
    #limitSts = 0
    stepCnt = int(((disCmd*1000)/125)*64)       # 4096 steps for 360 deg
                                                # 64 (5.625 deg) steps for 0.125 mm linear distance

    # motor control
    for i in range(stepCnt):
        for pin in range(0, len(motorPins)):
            GPIO.output(motorPins[pin], stepSeq[motorCnt][pin])
        if dirCmd == "up":
            motorCnt = (motorCnt+1)%8
        elif dirCmd == "down":
            motorCnt = (motorCnt-1)%8
        else:
            # do nothing (motor fault prevention)
            logging.info("utilities.stageControl    : fault detected")

        time.sleep(stepHold)

        """
        # LIMIT SWITCH FUNCTION [OVERTRAVELLED PREVENTION]
        # FUTURE IMPROVEMENT FUNCTION [FIX LATER]

        if limitSts == 1:
            break

        # limit switch trigged
        if GPIO.input(LIMIT_IN) == GPIO.LOW:
            limitSts = 1
        #GPIO.add_event_detect(LIMIT_IN, GPIO.FALLING, callback=gpioMotorReset, bouncetime=50)
        #    break           # break for loop // stop all stepping motors
        """

    gpioMotorReset()        # prevent command holding

def fineStageControl(stepCnt):
    logging.info("utilities.fineStageControl    : fine stage control cmd received")
    motorCnt = 0

    # define stage movement direction
    if stepCnt > 0:
        dirCmd = "up"
    elif stepCnt < 0:
        dirCmd = "down"
    else:
        # do nothing
        logging.info("utilities.fineStageControl    : fault detected")

    # changing stepCnt to be absolute number
    stepCnt = abs(stepCnt)

    # motor control
    for i in range(stepCnt):
        for pin in range(0, len(motorPins)):
            GPIO.output(motorPins[pin], stepSeq[motorCnt][pin])
        if dirCmd == "up":
            motorCnt = (motorCnt+1)%8
        elif dirCmd == "down":
            motorCnt = (motorCnt-1)%8
        else:
            # do nothing (motor fault prevention)
            logging.info("utilities.fineStageControl    : fault detected")

        time.sleep(stepHold)

    # reset stepCnt parameter
    stepCnt = 0

    gpioMotorReset()        # prevent command holding