import time
import RPi.GPIO
import sys
import math
from spidev import SpiDev
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

gpiopin = 4  #dht11 gpio pin
jeffresults = ''
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setwarnings(False)
RPi.GPIO.cleanup()
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
pin=0  #adc channel
LPGCurve = [2.3,0.21,-0.47]    # two points are taken from the curve. 
COCurve = [2.3,0.72,-0.34]     # two points are taken from the curve. 
SmokeCurve =[2.3,0.53,-0.44]   # two points are taken from the curve. 
print("Calibrating")
val = 0.0
raw_adc = 0
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient('basicPubSub')
myAWSIoTMQTTClient.configureEndpoint('a3shu6j73ct23v-ats.iot.us-east-1.amazonaws.com', '8883')
myAWSIoTMQTTClient.configureCredentials('/home/pi/root-CA.crt', '/home/pi/PiTemp1.private.key', '/home/pi/PiTemp1.cert.pem')
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.connect()

def read(pin):
    cmd1 = 4 | 2 | (( pin & 4) >> 2)
    cmd2 = (pin & 3) << 6
    adc = spi.xfer2([cmd1, cmd2, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data

def gettemp():
    th = []
    RPi.GPIO.setup(gpiopin, RPi.GPIO.OUT)
    RPi.GPIO.output(gpiopin, RPi.GPIO.HIGH)
    time.sleep(0.05)
    RPi.GPIO.output(gpiopin, RPi.GPIO.LOW)
    time.sleep(0.02)
    RPi.GPIO.setup(gpiopin, RPi.GPIO.IN, RPi.GPIO.PUD_UP)
    unchanged_count = 0
    max_unchanged_count = 100
    last = -1
    data = []
    while True:
        current = RPi.GPIO.input(gpiopin)
        data.append(current)
        if last != current:
            unchanged_count = 0
            last = current
        else:
            unchanged_count += 1
            if unchanged_count > max_unchanged_count:
                break

    STATE_INIT_PULL_DOWN = 1
    STATE_INIT_PULL_UP = 2
    STATE_DATA_FIRST_PULL_DOWN = 3
    STATE_DATA_PULL_UP = 4
    STATE_DATA_PULL_DOWN = 5
    state = STATE_INIT_PULL_DOWN
    lengths = []
    current_length = 0
    for i in range(len(data)):
        current = data[i]
        current_length += 1

        if state == STATE_INIT_PULL_DOWN:
            if current == RPi.GPIO.LOW:
                state = STATE_INIT_PULL_UP
                continue
            else:
                continue
        if state == STATE_INIT_PULL_UP:
            if current == RPi.GPIO.HIGH:
                state = STATE_DATA_FIRST_PULL_DOWN
                continue
            else:
                continue
        if state == STATE_DATA_FIRST_PULL_DOWN:
            if current == RPi.GPIO.LOW:
                state = STATE_DATA_PULL_UP
                continue
            else:
                continue
        if state == STATE_DATA_PULL_UP:
            if current == RPi.GPIO.HIGH:
                current_length = 0
                state = STATE_DATA_PULL_DOWN
                continue
            else:
                continue
        if state == STATE_DATA_PULL_DOWN:
            if current == RPi.GPIO.LOW:
                lengths.append(current_length)
                state = STATE_DATA_PULL_UP
                continue
            else:
                continue

    if len(lengths) != 40:
        jeffresults = "missing data"
        #print("missing data")
    else:
        bits = []
        shortest_pull_up = 1000
        longest_pull_up = 0

        for i in range(0, len(lengths)):
            length = lengths[i]
            if length < shortest_pull_up:
                shortest_pull_up = length
            if length > longest_pull_up:
                longest_pull_up = length
        halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
        bits = []

        for i in range(0, len(lengths)):
            bit = False
            if lengths[i] > halfway:
                bit = True
            bits.append(bit)
        
        the_bytes = []
        byte = 0

        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                the_bytes.append(byte)
                byte = 0

        checksum = the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3] & 255
        if the_bytes[4] != checksum:
            jeffresults = "Checksum Failed"
            #print(jeffresults)
        else:
            th.append((9.0 / 5.0 * int(the_bytes[2]) + 32))
            th.append(the_bytes[0])
    return th
                #print(9.0 / 5.0 * int(the_bytes[2]) + 32)
                #print(the_bytes[0])


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
    gas = []
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
    #GAS_LPG / CO / SMOKE
    gas.append((math.pow(10,(((math.log(rr_ratio)-LPGCurve[1])/LPGCurve[2])+LPGCurve[0]))))
    gas.append((math.pow(10,(((math.log(rr_ratio)-COCurve[1])/ COCurve[2]) + COCurve[0]))))
    gas.append((math.pow(10,(((math.log(rr_ratio)-SmokeCurve[1])/SmokeCurve[2])+SmokeCurve[0]))))
    return gas

while True:
    gas = []
    th = []
    while (not gas):
        gas = getgas()
    while (not th):
        th = gettemp()
    output = '{'
    output += '"Temperature":' + str(int(th[0])) + ','
    output += '"Humidity":' + str(int(th[1])) + ','
    output += '"TTL":' + str(int(time.time() + 86400)) + ','
    output += '"Timestamp":' + str(int(time.time())) + ','
    output += '"Location":"' + socket.gethostname() + '",'
    output += '"LPG":"' + str(gas[0]) + '",'
    output += '"CO":"' + str(gas[1]) + '",'
    output += '"Smoke":"' + str(gas[2]) + '"'
    output += '}'
    iotresults = False
    while (iotresults == False):
        iotresults = myAWSIoTMQTTClient.publish('sdk/test/Python', output, 1)
        time.sleep(60)
    print(output)
    #print("Posted: " + str(iotresults))
    time.sleep(20)

#getgas()
#gettemp()
#time.sleep(10)
#gettemp()
#getgas()
#time.sleep(10)

#spi.close()
#print(read(pin))
