import gridfs
import pymongo
import pandas as pd
import os
import io

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27018/")
db = client["mydatabase"]
fs = gridfs.GridFS(db)

EXISTING_CSV_FILE = "merged_data.csv"  # The file to append data

def fetch_and_merge_csv():
    """Fetch all CSV files from MongoDB and append to an existing CSV file."""
    existing_df = pd.DataFrame()

    # If the existing file exists, read it into a DataFrame
    if os.path.exists(EXISTING_CSV_FILE):
        existing_df = pd.read_csv(EXISTING_CSV_FILE)
    
    new_data = []

    # Fetch all files from GridFS
    for file_doc in db.fs.files.find({"filename": {"$regex": r".*\.csv$"}}):
        file_id = file_doc["_id"]
        file_data = fs.get(file_id).read()  # Read file content
        
        # Convert binary content to DataFrame
        df = pd.read_csv(io.StringIO(file_data.decode()))
        new_data.append(df)

        # Delete the file from GridFS after processing
        fs.delete(file_id)

    if new_data:
        combined_df = pd.concat([existing_df] + new_data, ignore_index=True)
        combined_df.to_csv(EXISTING_CSV_FILE, index=False)
        print(f"Updated '{EXISTING_CSV_FILE}' with new data.")
    else:
        print("No new CSV data found in MongoDB.")

if __name__ == "__main__":
    fetch_and_merge_csv()  # Fetch and append when script runs
