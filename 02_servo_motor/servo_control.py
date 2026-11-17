"""
Lab 2: Servo motor control with PWM on a Raspberry Pi 4.

The servo signal wire is connected to GPIO pin 15 (BCM numbering),
the power wire to 5V and the ground wire to GND.
A 50 Hz PWM signal sets the shaft angle (0-180 degrees).
The servo moves through 90, 180 and 0 degrees in a repeating sequence.
Press Ctrl + C to stop the program and reset the GPIO pins.
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)           # use Broadcom (BCM) pin numbering

SERVO_PIN = 15                   # BCM pin connected to the servo signal wire
GPIO.setup(SERVO_PIN, GPIO.OUT)  # configure the servo pin as an output

pwm = GPIO.PWM(SERVO_PIN, 50)    # 50 Hz PWM, the standard frequency for servos
pwm.start(0)                     # start with a 0% duty cycle (no pulse)


def set_angle(angle):
    """Move the servo to the given angle (0-180 degrees)."""
    duty = 2 + (angle / 18)      # convert angle to duty cycle: 0 deg = 2%, 180 deg = 12%
    pwm.ChangeDutyCycle(duty)    # send the pulse to move the shaft
    time.sleep(1)                # give the servo time to reach the position
    pwm.ChangeDutyCycle(0)       # stop the pulse to reduce jitter


try:
    while True:
        set_angle(90)
        set_angle(180)
        set_angle(0)
        set_angle(90)
        set_angle(180)
        set_angle(0)
except KeyboardInterrupt:
    print("Stopping servo")
    pwm.stop()                   # stop the PWM signal
    GPIO.cleanup()               # reset pins when stopped with Ctrl + C
