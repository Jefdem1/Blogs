import spidev
import time
import os
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data
def ConvertVolts(data,places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts,places)
    return volts
e = 0
while True:
    l = ReadChannel(1)
    d = l/10
    blnChanged = False
    if (d >= 0 and d < 20):
        if (e != 255):
            blnChanged = True
        e = 255
    elif (d >= 20 and d < 40):
        if (e != 200):
            blnChanged = True
        e = 200
    elif (d >=40 and d < 55):
        if (e != 100):
            blnChanged = True
        e = 100
    elif (d >= 55):
        if (e != 14):
            blnChanged = True
        e = 14
    #print(e)
    c = "sudo bash -c 'echo " + str(e) + " > /sys/class/backlight/rpi_backlight/brightness'"
    print(l)
    os.system(c)
    s = 1
    if (blnChanged == True):
        s = 60
    #print(str(blnChanged))
    #print(str(s))
    time.sleep(s)
