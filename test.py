import subprocess
import json

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
        pid = process_info[1]  # Adjust index if ps output changes

        meminfo_result = subprocess.run(
            ["adb", "shell", "dumpsys meminfo " + package_name],
            capture_output=True,
            text=True
        )
        if meminfo_result.returncode != 0 or not meminfo_result.stdout.strip():
            print("No memory info available for package:", package_name)
            return {"pid": pid, "memory_data": "N/A"}

        memory_data = meminfo_result.stdout
        return {"pid": pid, "memory_data": memory_data}

    except Exception as e:
        print("Error fetching app info:", e)
        return None

if __name__ == "__main__":
    package_name = "com.app"
    data = get_android_app_info(package_name)

    if data:
        with open("memory_info.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Memory info saved to memory_info.json")
    else:
        print("No data collected.")
