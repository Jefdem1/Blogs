import time
import RPi.GPIO
gpiopin = 4
jeffresults = ''
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setwarnings(False)
RPi.GPIO.cleanup()

def gettemp():
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
                print("missing data")
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
                        print(jeffresults)
                else:
                        #print(int(the_bytes[2]))
                        #print(int(the_bytes[0]))
                        print(9.0 / 5.0 * int(the_bytes[2]) + 32)
                        print(the_bytes[0])

gettemp()
time.sleep(10)
gettemp()
