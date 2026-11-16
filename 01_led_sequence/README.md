# Lab 1: LED Running-Light Sequence

Three LEDs controlled from a Raspberry Pi 4 through its GPIO pins, programmed in Python with the `RPi.GPIO` library. Part of the course *Systems and Devices of Applied Artificial Intelligence* at VILNIUS TECH.

## What it does
The LEDs light up one after another (0.5 s each) in an endless loop, creating a running-light effect. Pressing `Ctrl + C` stops the program and resets the GPIO pins with `GPIO.cleanup()`.

## Hardware
- Raspberry Pi 4 Model B
- 3 LEDs
- 3 resistors (220-330 ohm)
- Breadboard and jumper wires

## Wiring
| LED | GPIO pin (BCM) |
|-----|----------------|
| 1   | 14             |
| 2   | 15             |
| 3   | 18             |

Each LED's anode connects to its GPIO pin. Each cathode connects to ground through a resistor, which protects both the LED and the Raspberry Pi from excess current.

## Run
```bash
python3 led_sequence.py
```

## What I learned
- Setting GPIO pins as outputs and driving them HIGH and LOW
- Using BCM pin numbering
- Why LEDs need current-limiting resistors
- Safe shutdown with exception handling and `GPIO.cleanup()`

## Photos
![Circuit setup](images/led_setup.jpg)
![LEDs lit](images/led_lit_1.jpg)
![LEDs lit, close-up](images/led_lit_2.jpg)
