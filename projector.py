## PROJECT: MAGNI DOME
## FILE NAME: projector.py
## VERSION: 1.1.0
## LAST MODIFICATION: 03 SEP 2025

import logging
import RPi.GPIO as GPIO
import time
import subprocess
import numpy as np
from PIL import Image
from smbus2 import SMBus

# init all global parameters
EXPOSURE_TIME = 5                  # UV exposer time (sec)
# define raspberry pi ports
PROJ_POWER = 4                     # projector power switch to GPIO4 (pin 7)
# projector parameters
powerStatus = 0                     # projector power status
ledStatus = 0                       # projector LED status
# image parameters
imgDir = "/home/pi/Desktop/1.1.0beta/patternImages/"
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
# definition | lowest: 0x5B(LSB) 0x00(MSB) | highest: 0xFF(LSB) 0x03(MSB)
# parameter setting [LSB, MSB] >> 3 LEDs total
LEDCURR = [0x5B, 0x00,
           0x5B, 0x00,
           0x5B, 0x00]

# init GPIO parameters
def initProj():
    GPIO.setup(PROJ_POWER, GPIO.OUT)   # setup GPIO4 to be output 
    
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
            GPIO.output(PROJ_POWER, GPIO.HIGH)
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
                GPIO.output(PROJ_POWER, GPIO.LOW)      # projector power off
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
            #img = Image.open(imgPath).convert("RGB")
            #imgNP = np.array(img)

            bus.write_i2c_block_data(addr, ledCurrOffset, LEDCURR)
            bus.write_byte_data(addr, flipOffset, HFLIP)
            bus.write_byte_data(addr, ledOffset, LEDON)     # turn on LED

            """
            # initialise pygame with KMS/DRM framebuffer
            pygame.init()
            pygame.display.init()
            pygame.display.set_mode((imgNP.shape[1], imgNP.shape[0]), 
                                    pygame.NOFRAME | pygame.FULLSCREEN)
            
            # convert numpy array to pygame surface
            surface = pygame.surfarray.make_surface(np.transpose(imgNP, (1, 0, 2)))

            # blit to screen and update
            screen = pygame.display.get_surface()
            screen.blit(surface, (0, 0))
            pygame.display.flip()

            # keep image displayed
            pygame.time.wait(EXPOSURE_TIME * 1000)

            pygame.quit()
            """

            #"""
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
            #"""
            
            logging.info("projector.projLED         : finished projection")

            ledStatus = 0
            
    return ledStatus