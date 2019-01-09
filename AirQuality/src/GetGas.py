import time
import sys
import time
import math
from spidev import SpiDev

def read(pin):
    cmd1 = 4 | 2 | (( pin & 4) >> 2)
    cmd2 = (pin & 3) << 6
    adc = spi.xfer2([cmd1, cmd2, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data

spi = SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000 # 1MHz

RL_VALUE = 5        # define the load resistance on the board, in kilo ohms
RO_CLEAN_AIR_FACTOR = 9.83     # RO_CLEAR_AIR_FACTOR=(Sensor resistance in cle
CALIBARAION_SAMPLE_TIMES = 50       # define how many samples you are going to
CALIBRATION_SAMPLE_INTERVAL = 500      # define the time interal(in milisecond)
READ_SAMPLE_INTERVAL = 50       # define how many samples you are going to t
READ_SAMPLE_TIMES = 5        # define the time interal(in milisecond) betwee
Ro = 10
pin=0
LPGCurve = [2.3,0.21,-0.47]    # two points are taken from the curve. 
COCurve = [2.3,0.72,-0.34]     # two points are taken from the curve. 
SmokeCurve =[2.3,0.53,-0.44]   # two points are taken from the curve. 
#print("Calibrating...")
val = 0.0
raw_adc = 0
for i in range(CALIBARAION_SAMPLE_TIMES):
    while (raw_adc == 0):
        raw_adc = read(pin)
        if (raw_adc != 0):
            val += float(RL_VALUE*(1023.0-raw_adc)/float(raw_adc))
            time.sleep(CALIBRATION_SAMPLE_INTERVAL/1000.0)
    raw_adc = 0

val = val/CALIBARAION_SAMPLE_TIMES
val = val/RO_CLEAN_AIR_FACTOR
Ro = val
val = {}
rs = 0.0
def getgas():
    raw_adc = 0
    rs = 0.0
    for i in range(READ_SAMPLE_TIMES):
        while (raw_adc == 0):
            raw_adc = read(pin)
            if (raw_adc != 0):
                rs += float(RL_VALUE*(1023.0-raw_adc)/float(raw_adc))
                time.sleep(READ_SAMPLE_INTERVAL/1000.0)
        raw_adc = 0

    rs = rs/READ_SAMPLE_TIMES
    rr_ratio = rs/Ro
    val["GAS_LPG"] = (math.pow(10,(((math.log(rr_ratio)-LPGCurve[1])/LPGCurve[2])+LPGCurve[0])))
    val["CO"] = (math.pow(10,(((math.log(rr_ratio)-COCurve[1])/ COCurve[2]) + COCurve[0])))  
    val["SMOKE"] = (math.pow(10,(((math.log(rr_ratio)-SmokeCurve[1])/SmokeCurve[2])+SmokeCurve[0]))) 

    output = '{'
    output += '"LPG":"' + str(val["GAS_LPG"]) + '",'
    output += '"CO":"' + str(val["CO"]) + '",'
    output += '"Smoke":"' + str(val["SMOKE"]) + '"'
    output += '}'
    print(output)
    time.sleep(10)

getgas()
getgas()
#spi.close()
#print(read(pin))
