# Lab 2: Servo Motor Control with PWM

A micro servo motor controlled from a Raspberry Pi 4 using PWM (Pulse Width Modulation), programmed in Python with the `RPi.GPIO` library. Part of the course *Systems and Devices of Applied Artificial Intelligence* at VILNIUS TECH.

## What it does
The servo shaft moves through 90°, 180° and 0° in a repeating sequence, pausing 1 second at each position. Pressing `Ctrl + C` stops the PWM signal and resets the GPIO pins.

## How it works
A servo reads the width of a pulse repeated every 20 ms (50 Hz) and rotates its shaft to the matching angle. The `set_angle()` function converts an angle into a duty cycle:

```
duty = 2 + (angle / 18)
```

| Angle | Duty cycle | Pulse width (at 50 Hz) |
|-------|------------|------------------------|
| 0°    | 2 %        | 0.4 ms                 |
| 90°   | 7 %        | 1.4 ms                 |
| 180°  | 12 %       | 2.4 ms                 |

After each move the duty cycle is set to 0 to stop the servo from jittering.

## Hardware
- Raspberry Pi 4 Model B
- Micro servo motor (Tower Pro)
- Jumper wires

## Wiring
| Servo wire | Raspberry Pi  |
|------------|---------------|
| Power      | 5V            |
| Ground     | GND           |
| Signal     | GPIO 15 (BCM) |

## Run
```bash
python3 servo_control.py
```

## What I learned
- Generating a 50 Hz PWM signal with `GPIO.PWM`
- Converting an angle to a PWM duty cycle
- Why servos need time to reach a position
- Safe shutdown with exception handling and `GPIO.cleanup()`

## Photos
![Servo connected to the Raspberry Pi](servo_setup_1.jpg)
![Raspberry Pi 4 and servo, top view](servo_setup_2.jpg)
![Servo wiring](servo_setup_3.jpg)
