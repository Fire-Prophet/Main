import time
import random
import datetime

class Sensor:
    def __init__(self, sensor_id, sensor_type="temperature", min_val=0, max_val=100):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.min_val = min_val
        self.max_val = max_val

    def read_value(self):
        """Simulates reading a sensor value within its range."""
        if self.sensor_type == "temperature":
            # Simulate slight fluctuations around a central value
            current_temp = random.uniform(20.0, 30.0) + random.normalvariate(0, 1)
            return round(max(self.min_val, min(self.max_val, current_temp)), 2)
        elif self.sensor_type == "humidity":
            return round(random.uniform(40.0, 70.0), 2)
        elif self.sensor_type == "pressure":
            return round(random.uniform(980.0, 1020.0), 2)
        else:
            return random.uniform(self.min_val, self.max_val)

    def __repr__(self):
        return f"Sensor(ID: {self.sensor_id}, Type: {self.sensor_type})"

class SensorReader:
    def __init__(self, log_file="sensor_data.log"):
        self.sensors = []
        self.log_file = log_file

    def add_sensor(self, sensor):
        """Adds a sensor to be monitored."""
        if isinstance(sensor, Sensor):
            self.sensors.append(sensor)
            print(f"Sensor {sensor.sensor_id} added.")
        else:
            print("Invalid sensor object provided.")

    def read_all_sensors(self):
        """Reads values from all registered sensors."""
        readings = []
        timestamp = datetime.datetime.now().isoformat()
        for sensor in self.sensors:
            value = sensor.read_value()
            reading = {
                "timestamp": timestamp,
                "sensor_id": sensor.sensor_id,
                "sensor_type": sensor.sensor_type,
                "value": value,
                "unit": self._get_unit(sensor.sensor_type)
            }
            readings.append(reading)
            print(f"[{timestamp}] Sensor {sensor.sensor_id} ({sensor.sensor_type}): {value}{reading['unit']}")
        return readings

    def _get_unit(self, sensor_type):
        """Helper to get unit for a given sensor type."""
        if sensor_type == "temperature": return "°C"
        if sensor_type == "humidity": return "%"
        if sensor_type == "pressure": return "hPa"
        return ""

    def log_readings(self, readings):
        """Logs the sensor readings to a file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for reading in readings:
                    f.write(f"{reading['timestamp']},{reading['sensor_id']},{reading['sensor_type']},"
                            f"{reading['value']},{reading['unit']}\n")
            print(f"Logged {len(readings)} readings to {self.log_file}")
        except IOError as e:
            print(f"Error writing to log file {self.log_file}: {e}")

    def simulate_reading(self, interval_seconds=1, num_intervals=5):
        """Simulates continuous sensor reading and logging."""
        print(f"\n--- Simulating sensor readings for {num_intervals} intervals ---")
        for i in range(num_intervals):
            print(f"--- Interval {i+1}/{num_intervals} ---")
            current_readings = self.read_all_sensors()
            self.log_readings(current_readings)
            time.sleep(interval_seconds)
        print("--- Simulation complete ---")

if __name__ == "__main__":
    reader = SensorReader()
    reader.add_sensor(Sensor("T001", "temperature", min_val=-10, max_val=50))
    reader.add_sensor(Sensor("H001", "humidity", min_val=0, max_val=100))
    reader.add_sensor(Sensor("P001", "pressure", min_val=950, max_val=1050))
    reader.add_sensor(Sensor("L001", "light", min_val=0, max_val=1000))

    # Clear previous log for a clean run
    if os.path.exists("sensor_data.log"):
        os.remove("sensor_data.log")
        print("Cleared previous sensor_data.log")

    reader.simulate_reading(interval_seconds=0.5, num_intervals=10)

    print("\nContent of sensor_data.log:")
    with open("sensor_data.log", "r", encoding='utf-8') as f:
        for line in f.readlines()[-5:]: # Print last 5 lines for brevity
            print(line.strip())
