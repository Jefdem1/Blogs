import re
import time
import sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def mid(s, offset, amount):
    return s[offset:offset+amount]

def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'W' or direction == 'S':
        dd *= -1
    return dd;

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    parts = re.split(',', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3])
    return (lat)

temp = '3031.98221,N,09752.69157,W'
parts = re.split(',', temp)
def normalize(dmsin):
    parts2 = str(dmsin).split('.')
    temp2 = int(parts2[0])
    tempseconds = int(parts2[1])
    seconds = left(str(tempseconds),2) + '.' + right(str(tempseconds),len(str(tempseconds))-2)
    degrees = left(str(temp2),2)
    minutes = right(str(temp2),2)
    dms = str(degrees) + ',' + str(minutes) + ',' + str(seconds)
    return dms

dms2 = normalize(parts[0])
dms2 += ',' + str(parts[1])
Latitude = parse_dms(dms2)
dms2 = normalize(parts[2])
dms2 += ',' + str(parts[3])
Longitude = parse_dms(dms2)
#Latitude = parse_dms("30,31,98.221,N" )
#Longitude = parse_dms("97,52,69.157,W" )
#print(Latitude)
#print(Longitude)
a = '/home/pi/root-CA.crt'
b = '/home/pi/PiTemp1.private.key'
c = '/home/pi/PiTemp1.cert.pem'
d = '8883'
e = 'a3shu6j73ct23v-ats.iot.us-east-1.amazonaws.com'
#myAWSIoTMQTTClient = None
#myAWSIoTMQTTClient = AWSIoTMQTTClient('basicPubSub')
#myAWSIoTMQTTClient.configureEndpoint(e, d)
#myAWSIoTMQTTClient.configureCredentials(a, b, c)
#myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
#myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)
#myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
#myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
#myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
#myAWSIoTMQTTClient.connect()

output = '{'
output += '"TTL":' + str(int(time.time() + 86400)) + ','
output += '"Timestamp":' + str(int(time.time())) + ','
output += '"Location":"Outside",'
output += '"Latitude":"' + str(Latitude) + '",'
output += '"Longitude":"' + str(Longitude) + '"'
output += '}'
#iotresults = myAWSIoTMQTTClient.publish('sdk/test/gps', output, 1)
print(output)
