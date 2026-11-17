"""
Lab 3: Distance measurement with an HC-SR04 ultrasonic sensor on a Raspberry Pi 4.

The sensor TRIG pin is connected to GPIO 23 and the ECHO pin to GPIO 24
(BCM numbering). The program sends a short trigger pulse, times the echo
and converts the time into a distance in centimetres.
Press Ctrl + C to stop the program and reset the GPIO pins.
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)       # use Broadcom (BCM) pin numbering

TRIG = 23                    # trigger pin (Raspberry Pi output)
ECHO = 24                    # echo pin (Raspberry Pi input)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


def measure_distance():
    """Return the distance to the nearest object in centimetres."""
    # Send a 10 microsecond trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for the echo pin to go HIGH, then record the start time
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for the echo pin to go LOW, then record the end time
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start   # time the sound took to travel there and back

    # Speed of sound is about 34300 cm/s. The sound travels to the object and
    # back, so the distance is time * 34300 / 2 = time * 17150.
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance


try:
    while True:
        dist = measure_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)                          # one reading per second
except KeyboardInterrupt:
    print("Measurement stopped")
    GPIO.cleanup()                             # reset pins when stopped with Ctrl + C
