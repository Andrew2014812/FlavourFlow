import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class RestartHandler(FileSystemEventHandler):
    def __init__(self, module):
        self.module = module
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

        self.process = subprocess.Popen([sys.executable, "-m", self.module])

    def on_any_event(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith((".py", ".env")):
            print(f"Detected change in {event.src_path}, restarting...")
            self.restart()


if __name__ == "__main__":
    module_to_run = "bot.main"
    event_handler = RestartHandler(module_to_run)
    observer = Observer()
    observer.schedule(event_handler, path="bot", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

        if event_handler.process:
            event_handler.process.terminate()

        print("Stopped")
        observer.join()
