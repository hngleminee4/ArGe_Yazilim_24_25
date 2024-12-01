import RPi.GPIO as GPIO


leds = [17, 27, 22, 4, 5]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for led in leds:
    GPIO.setup(led, GPIO.OUT)

def blinking(finger):

    for led in leds:
        GPIO.output(led, GPIO.LOW)


    for i in range(min(number, len(leds))):
        GPIO.output(leds[i], GPIO.HIGH)


def cleanup_gpio():
    GPIO.cleanup()






