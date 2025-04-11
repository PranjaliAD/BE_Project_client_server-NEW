import gridfs
import pymongo
import uuid
import random
import os
import psutil
import pandas as pd
import time

# MongoDB Connection
MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb+srv://mikhiel_25:Bethel@internship.cludxjp.mongodb.net/")
client = pymongo.MongoClient(MONGO_URI)

db = client["Carbon_Record"]
fs = gridfs.GridFS(db)


def estimate_cpu_power():
    """Estimate CPU power based on CPU model and active cores."""
    cpu_freq = psutil.cpu_freq().max  # Max frequency in MHz
    core_count = psutil.cpu_count(logical=False)  # Physical cores

    if cpu_freq is None or cpu_freq == 0:
        # Fallback: Assume each core uses ~10W (varies per processor)
        return round(core_count * 10, 2)

    # Approximate power scaling (TDP estimation)
    return round((core_count * cpu_freq * 0.015), 2)  # Example scaling factor


def estimate_memory_power():
    """Estimate memory power consumption."""
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
    # Typical DDR4 module uses ~3W per 8GB
    return round((total_ram_gb / 8) * 3, 2)


def estimate_disk_power():
    """Estimate disk power usage based on type."""
    # Approximate: HDD ~ 6W, SSD ~ 3W (adjust based on usage)
    disk_info = psutil.disk_usage('/')
    # If disk is busy, assume higher power usage
    return 6 if disk_info.percent > 50 else 3


CPU_POWER = estimate_cpu_power()
MEMORY_POWER = estimate_memory_power()
DISK_POWER = estimate_disk_power()

print(f"Estimated CPU Power: {CPU_POWER}W")
print(f"Estimated Memory Power: {MEMORY_POWER}W")
print(f"Estimated Disk Power: {DISK_POWER}W")


def generate_filename():
    """Generate a unique filename using the machine's MAC address and a 3-digit unique ID."""
    mac_address = hex(uuid.getnode())[2:]  # Get MAC address and convert to hex
    unique_id = random.randint(100, 999)   # Generate a 3-digit unique ID
    return f"{mac_address}_{unique_id}.csv"


def collect_system_data(output_file, duration=60, interval=1):
    """Collect system usage data and calculate energy usage."""
    data = []
    start_time = time.time()

    while time.time() - start_time < duration:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        # Calculate power consumption
        cpu_power = (cpu_usage / 100) * CPU_POWER
        memory_power = (memory_usage / 100) * MEMORY_POWER
        disk_power = (disk_usage / 100) * DISK_POWER
        total_power = cpu_power + memory_power + disk_power

        data.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "total_power": total_power
        })

        time.sleep(interval)

    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"System data collected and saved to {output_file}")


def upload_file():
    """Upload the collected CSV file to MongoDB GridFS."""
    csv_file = generate_filename()
    # Collect system data and save to file
    collect_system_data(csv_file, duration=60, interval=1)

    with open(csv_file, "rb") as file_data:
        file_id = fs.put(file_data, filename=csv_file)

    print(f"File '{csv_file}' uploaded as '{csv_file}' (ID: {file_id})")
    os.remove(csv_file)  # Remove local file after upload


if __name__ == "__main__":
    upload_file()  # Automatically collect and upload CSV when script runs
