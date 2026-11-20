
import time
import math
from smbus2 import SMBus


# MPU6050 Configuration
MPU_ADDRESS = 0x68
I2C_BUS = 1

# MPU6050 Registers
WHO_AM_I = 0x75
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B

# Sensor sensitivity
ACCEL_SCALE = 16384.0
GYRO_SCALE = 131.0

# Calibration and filter settings
CALIBRATION_SAMPLES = 500
COMPLEMENTARY_ALPHA = 0.98


def convert_to_signed(value):
    """Convert raw 16-bit data to signed integer."""
    if value >= 32768:
        value -= 65536
    return value


class MPU6050:

    def __init__(self):
        self.bus = SMBus(I2C_BUS)

        # Verify sensor connection
        identity = self.bus.read_byte_data(
            MPU_ADDRESS, WHO_AM_I
        )

        if identity != 0x68:
            self.bus.close()
            raise RuntimeError(
                f"MPU6050 not detected. WHO_AM_I: 0x{identity:02X}"
            )

        # Wake up sensor
        self.bus.write_byte_data(
            MPU_ADDRESS, PWR_MGMT_1, 0x00
        )
        time.sleep(0.1)

        # Configure sensor
        self.bus.write_byte_data(
            MPU_ADDRESS, SMPLRT_DIV, 0x04
        )
        self.bus.write_byte_data(
            MPU_ADDRESS, CONFIG, 0x03
        )
        self.bus.write_byte_data(
            MPU_ADDRESS, ACCEL_CONFIG, 0x00
        )
        self.bus.write_byte_data(
            MPU_ADDRESS, GYRO_CONFIG, 0x00
        )

        self.gyro_offsets = [0.0, 0.0, 0.0]
        self.roll = 0.0
        self.pitch = 0.0
        self.last_time = None

    def read_sensor(self):
        """Read accelerometer and gyroscope measurements."""

        data = self.bus.read_i2c_block_data(
            MPU_ADDRESS, ACCEL_XOUT_H, 14
        )

        # Accelerometer raw data
        accel_x = convert_to_signed(
            (data[0] << 8) | data[1]
        )
        accel_y = convert_to_signed(
            (data[2] << 8) | data[3]
        )
        accel_z = convert_to_signed(
            (data[4] << 8) | data[5]
        )

        # Gyroscope raw data
        gyro_x = convert_to_signed(
            (data[8] << 8) | data[9]
        )
        gyro_y = convert_to_signed(
            (data[10] << 8) | data[11]
        )
        gyro_z = convert_to_signed(
            (data[12] << 8) | data[13]
        )

        # Convert accelerometer data to g
        ax = accel_x / ACCEL_SCALE
        ay = accel_y / ACCEL_SCALE
        az = accel_z / ACCEL_SCALE

        # Convert gyroscope data to degrees/second
        gx = gyro_x / GYRO_SCALE
        gy = gyro_y / GYRO_SCALE
        gz = gyro_z / GYRO_SCALE

        return ax, ay, az, gx, gy, gz

    def calibrate_gyro(self):
        """Calibrate gyroscope while sensor is stationary."""

        print("\nCalibrating gyroscope...")
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
        print(
            f"Offsets: X={self.gyro_offsets[0]:.3f}, "
            f"Y={self.gyro_offsets[1]:.3f}, "
            f"Z={self.gyro_offsets[2]:.3f}"
        )

        # Initialize orientation from accelerometer
        ax, ay, az, _, _, _ = self.read_sensor()

        self.roll = math.degrees(
            math.atan2(ay, az)
        )

        self.pitch = math.degrees(
            math.atan2(
                -ax,
                math.sqrt(ay * ay + az * az)
            )
        )

        self.last_time = time.monotonic()

    def calculate_angles(self, ax, ay, az, gx, gy):
        """Calculate roll and pitch using a complementary filter."""

        current_time = time.monotonic()

        dt = current_time - self.last_time
        self.last_time = current_time

        dt = min(dt, 0.1)

        # Accelerometer angle calculations
        accel_roll = math.degrees(
            math.atan2(ay, az)
        )

        accel_pitch = math.degrees(
            math.atan2(
                -ax,
                math.sqrt(ay * ay + az * az)
            )
        )

        # Apply gyroscope calibration
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
        """Close I2C connection."""
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

            # Correct gyroscope values
            corrected_gx = gx - sensor.gyro_offsets[0]
            corrected_gy = gy - sensor.gyro_offsets[1]
            corrected_gz = gz - sensor.gyro_offsets[2]

            roll, pitch = sensor.calculate_angles(
                ax, ay, az, gx, gy
            )

            print(
                f"Acceleration (g): "
                f"X={ax:7.3f} Y={ay:7.3f} Z={az:7.3f}"
            )

            print(
                f"Gyroscope (deg/s): "
                f"X={corrected_gx:7.2f} "
                f"Y={corrected_gy:7.2f} "
                f"Z={corrected_gz:7.2f}"
            )

            print(
                f"Orientation: Roll={roll:7.2f}° "
                f"Pitch={pitch:7.2f}°"
            )

            print("------------------------------------------")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")

    except (OSError, RuntimeError) as error:
        print(f"\nSensor error: {error}")

    finally:
        if sensor is not None:
            sensor.close()

        print("I2C connection closed.")


if __name__ == "__main__":
    main()

