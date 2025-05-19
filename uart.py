## FILE NAME: uart.py
## VERSION: 1.0.0
## LAST MODIFICATION: 21 MAR 2025

# local function for i2c connection
import logging
import serial
import time

# init all global parameters
MANUAL = 0      # manual control mode
PREDEF = 1      # predefined control mode

ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)    # initial serial port, baudrate, and timeout
time.sleep(1)       # stabilising the connection

logging.info("uart                      : i2c is ready")

# uart communication function
def uartComm(control, uartBuffer):
    if control == MANUAL:
        logging.info("uart.uartComm             : manual control received")
        ser.write(str(0).encode("utf-8"))
        ser.write(str(1).encode("utf-8"))

    if control == PREDEF:
        logging.info("uart.uartComm             : predefined control received")
        ser.write(str(1).encode("utf-8"))
        ser.write(str(0).encode("utf-8"))

    for uartCnt in range(0, 36):
        ser.write(str(uartBuffer[uartCnt]).encode("utf-8"))
    logging.info("uart.uartComm             : msg sent to Arduino")
