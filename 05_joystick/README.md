import time
import board
import busio
import RPi.GPIO as GPIO

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# ---------------- I2C / ADS1115 SETUP ----------------

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, 0)  # Joystick VRx connected to A0


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

DEADZONE = 0.15  # Voltage deadzone around joystick center

SERVO_MIN_DUTY = 2.5
SERVO_MAX_DUTY = 12.5

ADC_MIN_VOLTAGE = 0.0
ADC_MAX_VOLTAGE = 3.3

CALIBRATION_SAMPLES = 50


# ---------------- FUNCTIONS ----------------

def set_angle(angle):
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

    duty = SERVO_MIN_DUTY + (
        angle / 180.0
    ) * (SERVO_MAX_DUTY - SERVO_MIN_DUTY)

    pwm.ChangeDutyCycle(duty)

    print(f"Servo Angle: {angle}°")


def calibrate_joystick():
    print("Keep the joystick in the CENTER position...")

    readings = []

    for _ in range(CALIBRATION_SAMPLES):
        readings.append(chan.voltage)
        time.sleep(0.02)

    center_voltage = sum(readings) / len(readings)

    print(f"Center Voltage: {center_voltage:.2f} V")
    print("Calibration complete.\n")

    return center_voltage


def joystick_to_angle(voltage, center_voltage):

    # Joystick center deadzone
    if abs(voltage - center_voltage) < DEADZONE:
        return CENTER_ANGLE

    # Joystick moved LEFT
    if voltage < center_voltage:

        ratio = voltage / center_voltage

        angle = ratio * CENTER_ANGLE

    # Joystick moved RIGHT
    else:

        available_voltage = ADC_MAX_VOLTAGE - center_voltage

        if available_voltage <= 0:
            return CENTER_ANGLE

        ratio = (
            voltage - center_voltage
        ) / available_voltage

        angle = CENTER_ANGLE + (
            ratio * (MAX_ANGLE - CENTER_ANGLE)
        )

    angle = int(angle)

    return max(MIN_ANGLE, min(MAX_ANGLE, angle))


# ---------------- MAIN PROGRAM ----------------

try:

    center_voltage = calibrate_joystick()

    print("Joystick Servo Control Started")
    print("Move joystick LEFT or RIGHT")
    print("Press Ctrl+C to stop.\n")

    while True:

        voltage = chan.voltage

        angle = joystick_to_angle(
            voltage,
            center_voltage
        )

        set_angle(angle)

        print(f"Joystick Voltage: {voltage:.2f} V")
        print("-" * 30)

        time.sleep(0.05)


except KeyboardInterrupt:

    print("\nProgram stopped by user.")


finally:

    pwm.stop()
    GPIO.cleanup()

    print("GPIO cleanup completed.")ts in robotics and embedded systems applications.
