import RPi.GPIO as GPIO
import time
from time import sleep
from picamera import Picamera

TRIG = 23 # tetikleme pini 23
ECHO = 24 #geri dönüş pini 24

distance_threshold = 7 # mesafe eşiği

GPIO.setmode(GPIO.BMC)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

camera = Picamera()
camera.resolution = (1024, 168)

def distance_measurement(): #mesafe ölçme

    GPIO.output(TRIG, False)
    time.sleep(2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duraction = pulse_end - pulse_start 
    distance = pulse_duraction * 17150
    distance = round(distance, 2)

    return distance

def take_photo() # fotoğraf çekme

    camera.capture('/home/pi/Desktop/fotoğraf.jpg')
    print("photo took")

try:
    while True:
        distance = distance_measurement()
        print ("distance: ", distance, "cm")

        if distance <= distance_threshold:
            print("security limits exceeded")
            take_photo()
            time.sleep(1)
    
        time.sleep(0.5) #her ölçümde bekliycek

except KeyboardInterrup:
    print("programme terminated")
    GPIO.cleanup()
