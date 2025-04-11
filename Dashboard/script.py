import gridfs
import pymongo
# import uuid
import os
import psutil
import pandas as pd
import time
import platform
from getmac import get_mac_address
# MongoDB Connection
MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb+srv://mikhiel_25:Bethel@internship.cludxjp.mongodb.net/")
client = pymongo.MongoClient(MONGO_URI)

db = client["Carbon_Record"]
fs = gridfs.GridFS(db)

def generate_filename():
    mac_address = get_mac_address()
    if mac_address:
        mac_address = mac_address.replace(":", "").replace("-", "")
    else:
        mac_address = "unknown_device"
    return f"{mac_address}.csv"

def get_device_specs():
    """Retrieve device specifications."""
    cpu_model = platform.processor()
    total_ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # GB
    storage_type = "SSD" if any("ssd" in d.opts.lower() for d in psutil.disk_partitions()) else "HDD"
    return cpu_model, total_ram, storage_type

def estimate_cpu_power():
    """Estimate CPU power based on CPU model and active cores."""
    cpu_freq = psutil.cpu_freq().max  # Max frequency in MHz
    core_count = psutil.cpu_count(logical=False)  # Physical cores
    return round((core_count * cpu_freq * 0.015), 2) if cpu_freq else round(core_count * 10, 2)

def estimate_memory_power():
    """Estimate memory power consumption."""
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
    return round((total_ram_gb / 8) * 3, 2)

def estimate_disk_power():
    """Estimate disk power usage based on type."""
    return 6 if any("hdd" in d.opts.lower() for d in psutil.disk_partitions()) else 3

def get_energy_source_intensity():
    """Placeholder function for grid carbon intensity (gCO₂/kWh)."""
    return 450  # Placeholder value


def get_network_usage():
    """Retrieve network usage in MB."""
    net_io = psutil.net_io_counters()
    return round((net_io.bytes_sent + net_io.bytes_recv) / (1024 ** 2), 2)  # Convert to MB

def get_number_of_processes():
    """Retrieve the number of running processes."""
    return len(psutil.pids())

CPU_MODEL, TOTAL_RAM, STORAGE_TYPE = get_device_specs()
CPU_POWER = estimate_cpu_power()
MEMORY_POWER = estimate_memory_power()
DISK_POWER = estimate_disk_power()

# def generate_filename():
#     """Generate a unique filename."""
#     mac_address = hex(uuid.getnode())[2:]
#     return f"{mac_address}.csv"

def collect_system_data(output_file, duration=60, interval=1):
    """Collect system usage data."""
    data = []
    start_time = time.time()
    grid_intensity = get_energy_source_intensity()
    mac_address = get_mac_address()

    while time.time() - start_time < duration:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        network_usage = get_network_usage()
        num_processes = get_number_of_processes()

        cpu_power = (cpu_usage / 100) * CPU_POWER
        memory_power = (memory_usage / 100) * MEMORY_POWER
        disk_power = (disk_usage / 100) * DISK_POWER
        total_power = cpu_power + memory_power + disk_power
        carbon_emission = (total_power / 1000)*grid_intensity

        data.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "total_power": total_power,
            "carbon emission": carbon_emission,
            "network_usage": network_usage,
            "grid_intensity": grid_intensity,
            "num_processes": num_processes
        })
        time.sleep(interval)

    df = pd.DataFrame(data)
    df.insert(0, "device_cpu_model", CPU_MODEL)
    df.insert(1, "device_total_ram", TOTAL_RAM)
    df.insert(2, "device_storage_type", STORAGE_TYPE)
    df.insert(3, "mac_address", mac_address)

    df.to_csv(output_file, index=False)
    print(f"System data collected and saved to {output_file}")

def upload_file():
    """Upload collected CSV to MongoDB GridFS."""
    csv_file = generate_filename()
    collect_system_data(csv_file, duration=60, interval=1)
    with open(csv_file, "rb") as file_data:
        file_id = fs.put(file_data, filename=csv_file)
    print(f"File '{csv_file}' uploaded (ID: {file_id})")
    # os.remove(csv_file)
    try:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(download_dir, exist_ok=True)
        local_copy_path = os.path.join(download_dir, csv_file)
        os.rename(csv_file, local_copy_path)
        print(f"Local copy saved to: {local_copy_path}")
    except Exception as e:
        print(f"Could not save to Downloads, keeping file in current directory. Error: {e}")
        # Optionally: keep the file instead of removing it
        # If you want to remove it from current dir after copying, use os.remove(csv_file)
    
    print("MAC Address:", get_mac_address())

if __name__ == "__main__":
    upload_file()