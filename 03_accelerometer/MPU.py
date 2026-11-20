
import time
import math
from smbus2 import SMBus

# MPU6050 Configuration
MPU_ADDRESS = 0x68
BUS_NUMBER = 1

# MPU6050 Registers
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B

# Sensor sensitivity (default configuration)
ACCEL_SCALE = 16384.0  # LSB/g at +/-2g
GYRO_SCALE = 131.0     # LSB/(degree/second) at +/-250 dps

CALIBRATION_SAMPLES = 500
COMPLEMENTARY_ALPHA = 0.98


def convert_to_signed(value):
    """Convert a 16-bit unsigned value into signed format."""
    if value >= 32768:
        value -= 65536
    return value


class MPU6050:

    def __init__(self):
        self.bus = SMBus(BUS_NUMBER)

        # Wake up MPU6050
        self.bus.write_byte_data(
            MPU_ADDRESS, PWR_MGMT_1, 0x00
        )

        time.sleep(0.1)

        # Configure accelerometer and gyroscope
        self.bus.write_byte_data(
            MPU_ADDRESS, SMPLRT_DIV, 0x04
        )
        self.bus.write_byte_data(
            MPU_ADDRESS, CONFIG, 0x03
        )
        self.bus.write_byte_data(
            MPU_ADDRESS, GYRO_CONFIG, 0x00
        )
        self.bus.write_byte_data(
            MPU_ADDRESS, ACCEL_CONFIG, 0x00
        )

        self.gyro_offsets = [0.0, 0.0, 0.0]

        self.roll = 0.0
        self.pitch = 0.0

        self.last_time = time.monotonic()

    def read_sensor(self):
        """Read accelerometer and gyroscope data."""

        data = self.bus.read_i2c_block_data(
            MPU_ADDRESS, ACCEL_XOUT_H, 14
        )

        accel_x = convert_to_signed(
            (data[0] << 8) | data[1]
        )
        accel_y = convert_to_signed(
            (data[2] << 8) | data[3]
        )
        accel_z = convert_to_signed(
            (data[4] << 8) | data[5]
        )

        gyro_x = convert_to_signed(
            (data[8] << 8) | data[9]
        )
        gyro_y = convert_to_signed(
            (data[10] << 8) | data[11]
        )
        gyro_z = convert_to_signed(
            (data[12] << 8) | data[13]
        )

        # Convert raw values into physical units
        ax = accel_x / ACCEL_SCALE
        ay = accel_y / ACCEL_SCALE
        az = accel_z / ACCEL_SCALE

        gx = gyro_x / GYRO_SCALE
        gy = gyro_y / GYRO_SCALE
        gz = gyro_z / GYRO_SCALE

        return ax, ay, az, gx, gy, gz

    def calibrate_gyro(self):
        """Calculate gyroscope offsets while sensor is stationary."""

        print("Calibrating MPU6050...")
        print("Keep the sensor completely still.")

        totals = [0.0, 0.0, 0.0]

        for _ in range(CALIBRATION_SAMPLES):
            _, _, _, gx, gy, gz = self.read_sensor()

            totals[0] += gx
            totals[1] += gy
            totals[2] += gz

            time.sleep(0.005)

        self.gyro_offsets = [
            total / CALIBRATION_SAMPLES
            for total in totals
        ]

        print("Calibration completed!")
        print("Gyroscope offsets:", self.gyro_offsets)

    def calculate_angles(self, ax, ay, az, gx, gy):
        """Calculate roll and pitch using a complementary filter."""

        current_time = time.monotonic()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Prevent unusually large integration steps
        dt = min(dt, 0.1)

        # Accelerometer-based angles
        accel_roll = math.degrees(
            math.atan2(ay, az)
        )

        accel_pitch = math.degrees(
            math.atan2(
                -ax,
                math.sqrt(ay * ay + az * az)
            )
        )

        # Correct gyroscope readings
        gx -= self.gyro_offsets[0]
        gy -= self.gyro_offsets[1]

        # Complementary filter
        self.roll = (
            COMPLEMENTARY_ALPHA *
            (self.roll + gx * dt)
            +
            (1 - COMPLEMENTARY_ALPHA) *
            accel_roll
        )

        self.pitch = (
            COMPLEMENTARY_ALPHA *
            (self.pitch + gy * dt)
            +
            (1 - COMPLEMENTARY_ALPHA) *
            accel_pitch
        )

        return self.roll, self.pitch

    def close(self):
        """Close I2C communication."""
        self.bus.close()


def main():

    sensor = None

    try:
        sensor = MPU6050()

        sensor.calibrate_gyro()

        print("\nMPU6050 Accelerometer Started")
        print("------------------------------------------")

        while True:

            ax, ay, az, gx, gy, gz = sensor.read_sensor()

            roll, pitch = sensor.calculate_angles(
                ax, ay, az, gx, gy
            )

            print(
                f"Accel: X={ax:7.3f}g "
                f"Y={ay:7.3f}g Z={az:7.3f}g"
            )

            print(
                f"Gyro:  X={gx:7.2f} "
                f"Y={gy:7.2f} Z={gz:7.2f} deg/s"
            )

            print(
                f"Orientation: Roll={roll:7.2f}° "
                f"Pitch={pitch:7.2f}°"
            )

            print("------------------------------------------")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")

    except OSError as error:
        print(f"I2C communication error: {error}")

    finally:
        if sensor is not None:
            sensor.close()

        print("MPU6050 connection closed.")


if __name__ == "__main__":
    main()
