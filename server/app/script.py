import gridfs
import pymongo
import pandas as pd
import os
import io
import re

# MongoDB Connection
<<<<<<< HEAD
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
=======
client = pymongo.MongoClient(
    "mongodb+srv://mikhiel_25:Bethel@internship.cludxjp.mongodb.net/")
db = client["Carbon_Record"]
>>>>>>> 42039ac351db54066a97fb7b9f81136898f01d1c
fs = gridfs.GridFS(db)

EXISTING_CSV_FILE = "merged_data.csv"  # The file to append data


def extract_mac_address(filename):
    """Extracts MAC address from the file name (pattern: {mac_address}_{unique_id}.csv)."""
    print(f"Processing filename: {filename}")  # Debugging print

    # Allow both ':' and '-' as MAC address separators
    match = re.match(r"([0-9A-Fa-f:-]{17})_.*\.csv", filename)

    if match:
        print(f"Extracted MAC: {match.group(1)}")  # Debugging print
        return match.group(1)
    else:
        print("MAC address not found!")  # Debugging print
        return "UNKNOWN_MAC"  # Fallback value


def fetch_and_merge_csv():
    """Fetch all CSV files from MongoDB, append MAC address, merge with an existing CSV file, and delete the files from MongoDB."""
    existing_df = pd.DataFrame()

    # If the existing file exists, read it into a DataFrame
    if os.path.exists(EXISTING_CSV_FILE):
        try:
            existing_df = pd.read_csv(EXISTING_CSV_FILE)
        except Exception as e:
            print(f"Error reading existing CSV: {e}")
            return

    new_data = []
    files_to_delete = []

    # Fetch all files from GridFS
    for file_doc in db.fs.files.find({"filename": {"$regex": r".*\.csv$"}}):
        file_id = file_doc["_id"]
        filename = file_doc["filename"]

        try:
            file_data = fs.get(file_id).read()  # Read file content
            mac_address = extract_mac_address(filename)  # Extract MAC

            # Convert binary content to DataFrame
            df = pd.read_csv(io.StringIO(file_data.decode(errors="replace")))

            # Ensure non-empty DataFrame
            if not df.empty:
                df["MAC Address"] = mac_address
                new_data.append(df)

            # Mark for deletion after processing
            files_to_delete.append(file_id)

        except Exception as e:
            print(f"Error processing file {filename}: {e}")

    # Merge data if new CSVs are found
    if new_data:
        combined_df = pd.concat([existing_df] + new_data, ignore_index=True)
        combined_df.to_csv(EXISTING_CSV_FILE, index=False)
        print(f"Updated '{EXISTING_CSV_FILE}' with new data.")

        # Delete processed files from GridFS
        for file_id in files_to_delete:
            try:
                fs.delete(file_id)
                print(f"Deleted file with ID {file_id} from GridFS.")
            except Exception as e:
                print(f"Error deleting file {file_id}: {e}")
    else:
        print("No new CSV data found in MongoDB.")


if __name__ == "__main__":
    fetch_and_merge_csv()  # Fetch, merge, and delete processed files
