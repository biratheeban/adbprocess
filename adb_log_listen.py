
import subprocess
import time
import requests
import json
import platform
import re

LOG_UPLOAD_URL = 'http://localhost/processattach/save_log.php'
INTERVAL = 2


def get_adb_path():
    current_os = platform.system()
    if current_os == 'Windows':
        return 'C:\\path\\to\\adb.exe'
    elif current_os == 'Darwin':
               return '/Users/biratheebanpanneerchelvam/Library/Android/sdk/platform-tools/adb' 

    elif current_os == 'Linux':
        return '/usr/bin/adb'
    else:
        raise EnvironmentError(f"Unsupported OS: {current_os}")

adb_path = get_adb_path()

def execute_adb_command(command):
    try:
        result = subprocess.run([adb_path] + command, stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Error executing {' '.join(command)}: {result.stderr}")
        return result.stdout
    except FileNotFoundError:
        print(f"adb not found at {adb_path}. Please check the adb path.")
        return None

#memory info
def get_memory_info():
    return execute_adb_command(['shell', 'dumpsys', 'meminfo'])

#CPU info
def get_cpu_info():
    return execute_adb_command(['shell', 'dumpsys', 'cpuinfo'])

#running processes
def get_running_processes():
    return execute_adb_command(['shell', 'ps', '-A'])

#battery info
def get_battery_info():
    return execute_adb_command(['shell', 'dumpsys', 'battery'])

#memory info
def parse_memory_info(memory_info):
    memory_data = []
    pattern = re.compile(r'\s*(\d+,\d+K):\s+([\w\.\:\-\s]+)\(pid\s+(\d+)\)')
    matches = pattern.findall(memory_info)
    for match in matches:
        memory_kb = int(match[0].replace(',', '').replace('K', ''))
        process_name = match[1].strip()
        process_id = int(match[2])
        memory_data.append({'process_name': process_name, 'process_id': process_id, 'memory_kb': memory_kb})
    return memory_data

#CPU info
def parse_cpu_info(cpu_info):
    cpu_data = []
    lines = cpu_info.strip().split('\n')[1:]  # Skip the header line
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) > 2:  # Check if there's enough data
                cpu_data.append({'process_name': parts[2], 'cpu_usage': parts[0]})
    return cpu_data

#running processes
def parse_running_processes(running_processes):
    process_data = []
    lines = running_processes.strip().split('\n')[1:]  # Skip the header line
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) > 8:  # Check if there's enough data
                process_data.append({'pid': parts[1], 'process_name': parts[-1]})
    return process_data

#battery info
def parse_battery_info(battery_info):
    battery_data = {}
    lines = battery_info.strip().split('\n')
    for line in lines:
        if 'level' in line:
            battery_data['level'] = line.split(': ')[1].strip()
        if 'status' in line:
            battery_data['status'] = line.split(': ')[1].strip()
    return battery_data

#send log data to the server
def send_log_to_server(log_data):
    try:
        response = requests.post(LOG_UPLOAD_URL, json=log_data)
        if response.status_code == 200:
            print("Log sent successfully.")
        else:
            print(f"Failed to send log. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending log: {str(e)}")

# send data
def main():
    while True:
        memory_info = get_memory_info()
        cpu_info = get_cpu_info()
        running_processes = get_running_processes()
        battery_info = get_battery_info()

        if not (memory_info and cpu_info and running_processes and battery_info):
            print("Failed to collect data, skipping this cycle.")
            time.sleep(INTERVAL)
            continue

        memory_data = parse_memory_info(memory_info)
        cpu_data = parse_cpu_info(cpu_info)
        processes_data = parse_running_processes(running_processes)
        battery_data = parse_battery_info(battery_info)

        log_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'memory_data': memory_data,
            'cpu_data': cpu_data,
            'running_processes': processes_data,
            'battery_data': battery_data,
        }

        send_log_to_server(log_data)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
