import subprocess
import json
import time
from datetime import datetime


def get_android_app_info(package_name):
    try:
        result = subprocess.run(
            ["adb", "shell", "ps -A | grep " + package_name],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode != 0 or not result.stdout.strip():
            print("No process found for package:", package_name)
            return None

        process_line = result.stdout.strip().splitlines()[0]
        process_info = process_line.split()
        pid = process_info[1]  
        app_name = process_info[-1] 

        meminfo_result = subprocess.run(
            ["adb", "shell", "dumpsys meminfo " + package_name],
            capture_output=True,
            text=True
        )
        if meminfo_result.returncode != 0 or not meminfo_result.stdout.strip():
            print("No memory info available for package:", package_name)
            return {"pid": pid, "name": app_name, "memory_data": "N/A"}

        memory_data = {}
        for line in meminfo_result.stdout.splitlines():
            if "TOTAL" in line or "Native Heap" in line or "Dalvik Heap" in line:
                parts = line.split()
                if len(parts) >= 2 and parts[0].isnumeric():
                    key = " ".join(parts[1:]).strip()
                    value = int(parts[0])  # Convert memory value to KB
                    memory_data[key] = value

        return {"pid": pid, "name": app_name, "memory_data": memory_data}

    except Exception as e:
        print("Error fetching app info:", e)
        return None

def free_listen(package_name, output_file, interval=10):
    data_list = []
    try:
        while True:
            app_info = get_android_app_info(package_name)
            if app_info:
                current_time = datetime.now()
                app_info["timestamp"] = current_time.strftime("%H:%M:%S")  
                app_info["date"] = current_time.strftime("%Y-%m-%d") 

                data_list.append(app_info)

                with open(output_file, "w") as f:
                    json.dump(data_list, f, indent=4)

                print(f"App info updated. PID: {app_info['pid']}, Date: {app_info['date']}, Time: {app_info['timestamp']}, Memory types: {list(app_info['memory_data'].keys())}")
            else:
                print("Failed to fetch app info.")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nContinuous listening stopped.")


if __name__ == "__main__":
    package_name = "lk.bi007.safemyphone"
    output_file = "memory_info.json"
    free_listen(package_name, output_file, interval=10)
