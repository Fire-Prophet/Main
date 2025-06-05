import time
import datetime
import threading

class Task:
    def __init__(self, task_id, name, interval_seconds, callback_func, args=None, kwargs=None):
        self.task_id = task_id
        self.name = name
        self.interval_seconds = interval_seconds
        self.callback_func = callback_func
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}
        self.last_run_time = None
        self.next_run_time = datetime.datetime.now() # Schedule immediately for first run

    def should_run(self):
        """Checks if the task is due to run."""
        return datetime.datetime.now() >= self.next_run_time

    def execute(self):
        """Executes the task's callback function."""
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Executing task: {self.name} (ID: {self.task_id})")
        try:
            self.callback_func(*self.args, **self.kwargs)
            self.last_run_time = datetime.datetime.now()
            self.next_run_time = self.last_run_time + datetime.timedelta(seconds=self.interval_seconds)
            print(f"Task '{self.name}' completed. Next run scheduled for: {self.next_run_time.strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            print(f"Error executing task '{self.name}': {e}")
            return False

class TaskScheduler:
    def __init__(self):
        self.tasks = []
        self.is_running = False
        self.scheduler_thread = None

    def add_task(self, task):
        """Adds a task to the scheduler."""
        if isinstance(task, Task):
            self.tasks.append(task)
            print(f"Task '{task.name}' (ID: {task.task_id}) added to scheduler. Runs every {task.interval_seconds}s.")
        else:
            print("Invalid task object provided.")

    def _run_scheduler_loop(self):
        """The main loop for the scheduler thread."""
        while self.is_running:
            for task in self.tasks:
                if task.should_run():
                    task.execute()
            time.sleep(1) # Check tasks every second

    def start(self):
        """Starts the scheduler in a new thread."""
        if not self.is_running:
            print("Starting task scheduler...")
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler_loop)
            self.scheduler_thread.daemon = True # Allows program to exit even if thread is running
            self.scheduler_thread.start()
            print("Scheduler started.")
        else:
            print("Scheduler is already running.")

    def stop(self):
        """Stops the scheduler."""
        if self.is_running:
            print("Stopping task scheduler...")
            self.is_running = False
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5) # Wait for thread to finish
                if self.scheduler_thread.is_alive():
                    print("Warning: Scheduler thread did not terminate gracefully.")
            print("Scheduler stopped.")
        else:
            print("Scheduler is not running.")

# Dummy functions for tasks
def backup_data(path, verbose=False):
    if verbose:
        print(f"Performing data backup to {path}...")
    time.sleep(0.5) # Simulate work
    print(f"Backup to {path} completed!")

def send_daily_report(recipient):
    print(f"Sending daily report to {recipient}...")
    time.sleep(1) # Simulate network delay
    print(f"Report sent to {recipient}.")

def check_system_health():
    print("Checking system health...")
    health_status = random.choice(["OK", "WARNING", "CRITICAL"])
    print(f"System Health: {health_status}")

if __name__ == "__main__":
    scheduler = TaskScheduler()

    # Add tasks
    scheduler.add_task(Task("BKP001", "Daily Backup", 5, backup_data, args=("C:/backups",), kwargs={"verbose": True}))
    scheduler.add_task(Task("REP001", "Hourly Report", 10, send_daily_report, args=("admin@example.com",)))
    scheduler.add_task(Task("SYS001", "Health Check", 3, check_system_health))

    scheduler.start()

    print("\nScheduler running... will stop in 20 seconds.")
    time.sleep(20) # Let the scheduler run for 20 seconds

    scheduler.stop()
    print("Application finished.")
