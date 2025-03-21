import gridfs
import pymongo
import uuid
import random
import os
import psutil
import pandas as pd
import time

# MongoDB Connection
# client = pymongo.MongoClient("mongodb://localhost:27017/")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGO_URI)

db = client["mydatabase"]
fs = gridfs.GridFS(db)

CPU_POWER = 35
MEMORY_POWER = 5
DISK_POWER = 2

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
    collect_system_data(csv_file, duration=60, interval=1)  # Collect system data and save to file

    with open(csv_file, "rb") as file_data:
        file_id = fs.put(file_data, filename=csv_file)

    print(f"File '{csv_file}' uploaded as '{csv_file}' (ID: {file_id})")
    os.remove(csv_file)  # Remove local file after upload

if __name__ == "__main__":
    upload_file()  # Automatically collect and upload CSV when script runs
