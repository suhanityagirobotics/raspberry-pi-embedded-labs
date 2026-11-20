import time
import board
import busio
import RPi.GPIO as GPIO

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# ---------------- I2C / ADC SETUP ----------------

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, 0)  # Joystick X-axis connected to A0


# ---------------- SERVO SETUP ----------------

SERVO_PIN = 18
SERVO_FREQUENCY = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, SERVO_FREQUENCY)
pwm.start(0)


# ---------------- CONFIGURATION ----------------

MIN_ANGLE = 0
MAX_ANGLE = 180
CENTER_ANGLE = 90

DEADZONE_VOLTAGE = 0.15
ADC_MIN_VOLTAGE = 0.0
ADC_MAX_VOLTAGE = 3.3

SERVO_MIN_DUTY = 2.5
SERVO_MAX_DUTY = 12.5

CALIBRATION_SAMPLES = 50


# ---------------- FUNCTIONS ----------------

def set_angle(angle):
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

    duty = SERVO_MIN_DUTY + (angle / 180.0) * (
        SERVO_MAX_DUTY - SERVO_MIN_DUTY
    )

    pwm.ChangeDutyCycle(duty)
    print(f"Servo Angle: {angle}°")


def calibrate_center():
    print("Keep the joystick centered...")

    readings = []

    for _ in range(CALIBRATION_SAMPLES):
        readings.append(chan.voltage)
        time.sleep(0.02)

    center_voltage = sum(readings) / len(readings)

    print(f"Joystick center voltage: {center_voltage:.3f} V")

    return center_voltage


def map_voltage_to_angle(voltage):
    voltage = max(
        ADC_MIN_VOLTAGE,
        min(ADC_MAX_VOLTAGE, voltage)
    )

    angle = int(
        (voltage / ADC_MAX_VOLTAGE) * 180
    )

    return max(MIN_ANGLE, min(MAX_ANGLE, angle))


# ---------------- MAIN PROGRAM ----------------

try:
    center_voltage = calibrate_center()

    print("Joystick Servo Control Started")
    print("Move joystick left or right.")
    print("Press Ctrl+C to stop.\n")

    while True:

        voltage = chan.voltage

        if abs(voltage - center_voltage) < DEADZONE_VOLTAGE:
            angle = CENTER_ANGLE
        else:
            angle = map_voltage_to_angle(voltage)

        set_angle(angle)

        print(f"Joystick Voltage: {voltage:.3f} V")
        print("-" * 30)

        time.sleep(0.05)


except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleanup completed.")
