import datetime
import os

class LoggingService:
    def __init__(self, log_file="application.log", level="INFO"):
        self.log_file = log_file
        self.level_map = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        self.set_level(level)

        # Ensure log directory exists if path includes directories
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Created log directory: {log_dir}")

    def set_level(self, level_name):
        """Sets the minimum logging level."""
        level_value = self.level_map.get(level_name.upper())
        if level_value is not None:
            self.current_level = level_value
            print(f"Logging level set to {level_name.upper()}")
        else:
            print(f"Invalid logging level: {level_name}. Keeping current level.")

    def _log(self, level, message):
        """Internal method to write log entries."""
        if self.level_map.get(level.upper(), 0) >= self.current_level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                # print(f"Logged: {log_entry.strip()}") # For immediate console feedback
            except IOError as e:
                print(f"Error writing to log file {self.log_file}: {e}")

    def debug(self, message):
        """Logs a debug message."""
        self._log("DEBUG", message)

    def info(self, message):
        """Logs an info message."""
        self._log("INFO", message)

    def warning(self, message):
        """Logs a warning message."""
        self._log("WARNING", message)

    def error(self, message):
        """Logs an error message."""
        self._log("ERROR", message)

    def critical(self, message):
        """Logs a critical message."""
        self._log("CRITICAL", message)

    def read_log_file(self, num_lines=None):
        """Reads and returns specified number of lines from the log file."""
        if not os.path.exists(self.log_file):
            print(f"Log file '{self.log_file}' does not exist.")
            return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if num_lines:
                    return lines[-num_lines:]
                return lines
        except Exception as e:
            print(f"Error reading log file: {e}")
            return []

if __name__ == "__main__":
    # Clear previous log for a clean run
    if os.path.exists("application.log"):
        os.remove("application.log")
        print("Cleared previous application.log")
    
    # Example usage with INFO level
    logger = LoggingService()
    logger.info("Application started.")
    logger.debug("This debug message will not be logged by default.")
    logger.warning("Configuration file not found, using default settings.")
    logger.error("Failed to connect to database.")
    logger.critical("System crashed due to unhandled exception!")

    print("\n--- Log File Content (INFO level) ---")
    for line in logger.read_log_file(num_lines=5):
        print(line.strip())

    print("\n--- Changing log level to DEBUG ---")
    logger.set_level("DEBUG")
    logger.info("New session started.")
    logger.debug("Detailed processing step X completed.")
    logger.debug("Variable 'x' has value: 123")
    logger.warning("Resource utilization is high.")

    print("\n--- Log File Content (DEBUG level, last 5 lines) ---")
    for line in logger.read_log_file(num_lines=5):
        print(line.strip())

    # Example: Logging to a different directory
    print("\n--- Logging to a subdirectory ---")
    # Clean up previous log for this example too
    if os.path.exists("logs/system.log"):
        os.remove("logs/system.log")
    if os.path.exists("logs") and not os.listdir("logs"): # Remove empty dir
        os.rmdir("logs")

    system_logger = LoggingService("logs/system.log", "WARNING")
    system_logger.info("This info message will NOT be logged.")
    system_logger.warning("Disk space low on /dev/sda1.")
    system_logger.critical("Kernel panic detected.")

    print("\n--- Content of logs/system.log ---")
    for line in system_logger.read_log_file():
        print(line.strip())
