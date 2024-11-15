import RPi.GPIO as GPIO
import time

LED = 23
Buton = 24
GPIO.setmode(GPIO.BCM)

GPIO.setup(Buton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED,GPIO.OUT)

try:
    while True:
        buton_durum = GPIO.input(Buton)
        print(buton_durum)
        time.sleep(0.1)
        
        if buton_durum == 0:
            GPIO.output(LED,GPIO.HIGH)
        else:
            GPIO.output(LED,GPIO.LOW)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()