"""
Lab 1: LED running-light sequence on a Raspberry Pi 4.

Three LEDs are connected to GPIO pins 14, 15 and 18 (BCM numbering),
each through a 220-330 ohm current-limiting resistor to ground.
The LEDs light up one after another in a continuous loop.
Press Ctrl + C to stop the program and reset the GPIO pins.
"""

import RPi.GPIO as GPIO
import time

LED_PINS = [14, 15, 18]   # BCM pin numbers of the three LEDs
ON_TIME = 0.5             # seconds each LED stays on

GPIO.setmode(GPIO.BCM)    # use Broadcom (BCM) pin numbering

for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)   # configure every LED pin as an output

try:
    while True:
        for pin in LED_PINS:
            GPIO.output(pin, GPIO.HIGH)   # LED on
            time.sleep(ON_TIME)
            GPIO.output(pin, GPIO.LOW)    # LED off
except KeyboardInterrupt:
    GPIO.cleanup()                        # reset pins when stopped with Ctrl + C
