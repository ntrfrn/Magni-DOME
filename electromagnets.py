## FILE NAME: electromagnets.py
## VERSION: 1.0.0
## LAST MODIFICATION: 28 MAR 2025

# local function for control
import logging
import uart

# init all global parameters
FORWARD = 0             # forward current direction
REVERSE = 1             # reverse current direction
MANUAL = 0              # manual control mode
PREDEF = 1              # predefined control mode
# all parameters are defined in reference.txt
# for manual control
bufferUart = [0 for bit in range(36)]       # internal uart buffer for AR
bufferLocal = [0 for param in range(4)]     # internal local parameters buffer (for both manual and predef)
uartManual = [0 for bit in range(36)]       # internal uart buffer for AR
bufferManual = [0 for param in range(4)]    # internal parameters buffer
# for predefined control
uartPreDef = [0 for bit in range(28)]       # internal uart buffer for AR
bufferPreDef = [0 for param in range(4)]    # internal parameters buffer

# message packing function
# pack in binary to send to Arduino via uart protocol
def msgPack(control):
    # define control mode
    if control == MANUAL:
        logging.info("electromagnets.msgPack           : manual control packing")
        # store to temporary parameters
        tempCoil0 = abs(bufferLocal[0])
        tempCoil1 = abs(bufferLocal[1])
        tempCoil2 = abs(bufferLocal[2])
        tempCoil3 = abs(bufferLocal[3])

        # calculate binary
        # pack coil power
        for powerCnt in range(0, 8):
            bufferUart[powerCnt] = int(tempCoil0%2)
            tempCoil0 = int(tempCoil0/2)
            bufferUart[8+powerCnt] = int(tempCoil1%2)
            tempCoil1 = int(tempCoil1/2)
            bufferUart[16+powerCnt] = int(tempCoil2%2)
            tempCoil2 = int(tempCoil2/2)
            bufferUart[24+powerCnt] = int(tempCoil3%2)
            tempCoil3 = int(tempCoil3/2)
        # pack coil direction
        for dirCnt in range(0, 4):
            if bufferLocal[dirCnt] < 0:
                bufferUart[32+dirCnt] = REVERSE
            else:
                bufferUart[32+dirCnt] = FORWARD
        
        #"""    debug binary messages (manual)
        print(bufferLocal)
        for i in range(0, 4):
            for j in range(0, 8):
                print(bufferUart[(i*8)+j], end=" ")
            print(" ")
        for k in range(0, 4):
            print(bufferUart[32+k], end=" ")
        print(" ")
        #"""

    if control == PREDEF:
        logging.info("electromagnets.msgPack           : predefined control packing")
        # store to temporary parameters
        tempMode = bufferLocal[0]
        tempField = bufferLocal[1]
        tempFreq = bufferLocal[2]
        tempStep = bufferLocal[3]

        # calculate binary
        # pack result field
        for fieldCnt in range(0, 16):
            bufferUart[fieldCnt] = int(tempField%2)
            tempField = int(tempField/2)
        # pack frequency
        for freqCnt in range(16, 24):
            bufferUart[freqCnt] = int(tempFreq%2)
            tempFreq = int(tempFreq/2)
        # pack angle step
        for stepCnt in range(24, 32):
            bufferUart[stepCnt] = int(tempStep%2)
            tempStep = int(tempStep/2)
        # pack mode
        for modeCnt in range(32, 36):
            bufferUart[modeCnt] = int(tempMode%2)
            tempMode = int(tempMode/2)
    
        #"""    debug binary messages (manual)
        print(bufferLocal)
        for i in range(0, 4):
            for j in range(0, 8):
                print(bufferUart[(i*8)+j], end=" ")
            print(" ")
        for k in range(0, 4):
            print(bufferUart[32+k], end=" ")
        print(" ")
        #"""

# manual control function
def manualControl(manualArray):
    logging.info("electromagnets.manualControl     : receiving manual cmd")   # logging status
    control = MANUAL    # setup msg pack mode
    # store variable
    for i in range(4):
        bufferLocal[i] = manualArray[i]
    
    msgPack(control)                    # pack msg to binary
    uart.uartComm(control, bufferUart)     # start i2c comm to arduino

# predefined contron function
def preDefControl(mode, field, freq):
    logging.info("electromagnets.preDefControl     : receiving predfined cmd")   # logging status
    control = PREDEF    # setup msg pack mode
    if mode == "stop":
        logging.info("electromagnets.preDefControl     : stop running")
        for i in range(4):
            bufferLocal[i] = 0  
    else:
        if mode == "sonic":
            logging.info("electromagnets.preDefControl     : sonicate mode")
            bufferLocal[0] = 1         # 1: sonicate mode
            bufferLocal[3] = 180       # angle step (deg)
        if mode == "vortex":
            logging.info("electromagnets.preDefControl     : vortex mode")
            bufferLocal[0] = 2         # 2: vortex mode
            bufferLocal[3] = 30        # angle step (deg)
        if mode == "xroll":
            logging.info("electromagnets.preDefControl     : x'-axis rolling mode")
            bufferLocal[0] = 3         # 3: x'-axis rolling mode
            bufferLocal[3] = 30        # angle step (deg)
        if mode == "yroll":
            logging.info("electromagnets.preDefControl     : y'-axis rolling mode")
            bufferLocal[0] = 4         # 4: y'-axis rolling mode
            bufferLocal[3] = 30        # angle step (deg)
        if mode == "swim":
            logging.info("electromagnets.preDefControl     : swimming mode")
            bufferLocal[0] = 5         # 5: swimming mode
            bufferLocal[3] = 35        # angle step (deg)
        if mode == "flap":
            logging.info("electromagnets.preDefControl     : flapping mode")
            bufferLocal[0] = 6         # 6: flapping mode
            bufferLocal[3] = 90        # angle step (deg)
        
        bufferLocal[1] = field*(1e3)
        bufferLocal[2] = freq

    msgPack(control)                    # pack msg to binary
    uart.uartComm(control, bufferUart)     # start i2c comm to arduino
