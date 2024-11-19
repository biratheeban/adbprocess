
def get_android_app_info(package_name):
    try:
        # Find the process ID and app name
        result = subprocess.run(
            ["adb", "shell", f"ps -A | grep {package_name}"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode != 0 or not result.stdout.strip():
            print("No process found for package:", package_name)
            return None

        # Extract PID and app name
        process_line = result.stdout.strip().splitlines()[0]
        process_info = process_line.split()
        pid = process_info[1]  # PID is typically the second column
        app_name = process_info[-1]  # App name is typically the last column

        # Get memory information
        meminfo_result = subprocess.run(
            ["adb", "shell", f"dumpsys meminfo {package_name}"],
            capture_output=True,
            text=True
        )

        if meminfo_result.returncode != 0 or not meminfo_result.stdout.strip():
            print("No memory info available for package:", package_name)
            return {"pid": pid, "name": app_name, "memory_data": {}}

        memory_data = {}
        for line in meminfo_result.stdout.splitlines():
            line = line.strip()
            if any(key in line for key in ["Native Heap", "Dalvik Heap", "Graphics", "Stack", "TOTAL"]):
                parts = line.split()
                try:
                    key = parts[0].replace(":", "").strip()
                    value = int(parts[-2].replace("kB", "").strip())  # Last memory value is typically in kB
                    memory_data[key] = value
                except (ValueError, IndexError):
                    continue

        return {
            "pid": pid,
            "name": app_name,
            "memory_data": memory_data
        }

    except Exception as e:
        print("Error fetching app info:", e)
        return None