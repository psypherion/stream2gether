import subprocess
from typing import Any

class KillProcess:
    def __init__(self, port: str) -> None:
        self.flag: bool = True
        self.port: str = port

    def pid_info(self) -> Any:
        try:
            # Get the process ID (PID) of the process using port 3000/tcp
            pid_info = subprocess.check_output(["fuser", f"{self.port}/tcp"]).decode().strip()
            return pid_info.split()[0]  # Return the first PID
        except subprocess.CalledProcessError:
            self.flag = False  # No process is using the port
            return None
    @staticmethod
    def kill_pid(pid: int) -> None:
        if pid:
            # Kill the process with the given PID
            subprocess.run(["kill", "-9", str(pid)])
            print(f"Process with PID {pid} has been killed.")
        else:
            print("No process found running on the specified port.")

    def kill_process(self) -> None:
        while self.flag:
            pid_info = self.pid_info()
            if pid_info:  # If a process is using the port
                pid = int(pid_info)
                self.kill_pid(pid)
            else:
                print("No process is running on port 3000.")
                break

# Usage
if __name__ == "__main__":
    port_num: str = input("Enter port Number: ")
    killer = KillProcess(port=port_num)
    killer.kill_process()
