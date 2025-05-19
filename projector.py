## FILE NAME: projector.py
## VERSION: 1.0.0
## LAST MODIFICATION: 02 APR 2025

import logging
import RPi.GPIO as GPIO
import time
import subprocess
from smbus2 import SMBus

# init all global parameters
EXPOSURE_TIME = 5                   # UV exposer time
# define raspberry pi ports
projPowerSw = 14                    # projector power switch to port 14
# projector parameters
powerStatus = 0                     # projector power status
ledStatus = 0                       # projector LED status
# image parameters
imgDir = "/home/pi/Desktop/LumaDomeTest/patternImages/"
imgPath = ""

# raspberry pi i2c port setup
bus = SMBus(1)                      # SDA1 / SCL1 open to be used
addr = 0x1b                         # i2c at address 1b
# projector setting byte offset
ledOffset = 0x52                    # projector LED byte offset
flipOffset = 0x14                   # projection image flip byte offset
ledCurrOffset = 0x54                # projector LED current byte offset
# LED byte value
LEDON = 0x07                        # LED on byte
LEDOFF = 0x00                       # LED off byte
# projection flip value
NOFLIP = 0x00                       # no flip
HFLIP = 0x02                        # horizontal flip
VFLIP = 0x04                        # vertical flip
HVFLIP = 0x06                       # horizontal and vertical flip
# LED current byte value
# definition | lowest: 0x00(MSB) 0x5B(LSB) | highest: 0x03(MSB) 0xFF(LSB)
# parameter setting [LSB, MSB] >> 3 LEDs total
LEDCURR = [0x5B, 0x00,
           0x5B, 0x00,
           0x5B, 0x00]

# init GPIO parameters
def initProj():
    global projPowerSw

    # setup GPIO pins for raspberry pi
    GPIO.setup(projPowerSw, GPIO.OUT)   # setup pin 14 to be output pin 

    logging.info("projector                 : projector control parameters initialised")

# receiving command function
def projCommand(projCmd, imgName):
    if projCmd == "on" or "off":
        projPower(projCmd)
    
    if projCmd == "led off" or "screen" or "image":
        projLED(projCmd, imgName)

# projector power function
def projPower(powerCmd):
    # calling global parameters
    global powerStatus, ledStatus

    # projector power on
    if powerCmd == "on":
        if powerStatus == 0:
            GPIO.output(projPowerSw, GPIO.HIGH)
            time.sleep(1)       # warm up
            logging.info("projector.projPower       : projector power on")
            powerStatus = 1     # return power status on
        else:
            logging.info("projector.projPower       : projector is currently on")

    # projector power off
    if powerCmd == "off":
        if powerStatus == 1:
            if ledStatus == 1:
                projLED("off", "NULL")

            if ledStatus == 0:
                GPIO.output(projPowerSw, GPIO.LOW)      # projector power off
                time.sleep(1)       # cool down
                logging.info("projector.projPower       : projector power off")
                powerStatus = 0     # return power status off
        else:
            logging.info("projector.projPower       : projector is currently off")
    
    return powerStatus

# projector LED control function
def projLED(ledCmd, imgName):
    # calling global parameters
    global powerStatus, ledStatus, imgDir, imgPath

    # case projector is off
    if powerStatus == 0:
        logging.info("projector.projLED         : projector is currently off")
    
    if powerStatus == 1:
        # set projector LED off
        if ledCmd == "led off":
            if ledStatus == 1:
                bus.write_byte_data(addr, ledOffset, LEDOFF)
                logging.info("projector.projLED         : LED off")
                ledStatus = 0
            
            if ledStatus == 0:
                logging.info("projector.projLED         : LED is currently off")

        # sharing screen
        if ledCmd == "screen":
            logging.info("projector.projLED         : sharing screen")
            bus.write_byte_data(addr, flipOffset, HFLIP)
            bus.write_byte_data(addr, ledOffset, LEDON)
            ledStatus = 1
            
        # projecting images
        if ledCmd == "image":
            logging.info("projector.projLED         : projecting the image")
            imgPath = f"{imgDir}{imgName}"                  # create image path
            bus.write_i2c_block_data(addr, ledCurrOffset, LEDCURR)
            bus.write_byte_data(addr, flipOffset, HFLIP)
            bus.write_byte_data(addr, ledOffset, LEDON)     # turn on LED
            # run fbi command to switch a projection image to an input image
            subprocess.run(["sudo", "fbi", "-T", "1", "-d", "/dev/fb0", "--noverbose", imgPath], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            time.sleep(EXPOSURE_TIME)                       # exposure time
            bus.write_byte_data(addr, ledOffset, LEDOFF)    # turn off LED
            # switch back to main monitor
            subprocess.run(["sudo", "chvt", "7"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            logging.info("projector.projLED         : finished projection")
            ledStatus = 0
            
    return ledStatus