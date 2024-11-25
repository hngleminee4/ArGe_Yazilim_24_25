import RPi.GPIO as GPIO
import time

button = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)

try:
    while True:
        buton_durum =GPIO.input(button)
        if buton_durum == 0:
            print("1")
            time.sleep(1)

except KeyboardInterrupt:
    pass        
finally:
    GPIO.cleanup()