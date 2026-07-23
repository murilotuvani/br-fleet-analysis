from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pathlib import Path
import pandas as pd
import requests

import zipfile
import rarfile

mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

# Diretório de download (crie se não existir)
download_dir = Path("/Volumes/dados/fleet")


def list_files_in_download_dir():
    """List all files in download_dir and contents of compressed files"""

    if not download_dir.exists():
        print(f"❌ Directory does not exist: {download_dir}")
        return

    print(f"📁 Listing files in: {download_dir}\n")
    print("=" * 80)

    # List all files in the directory
    all_files = sorted([f for f in download_dir.iterdir() if f.is_file()])

    if not all_files:
        print("No files found in directory")
        return

    print(f"Total files: {len(all_files)}\n")

    for file_path in all_files:
        filename = file_path.name
        file_size = file_path.stat().st_size

        print(f"📄 {filename} ({file_size} bytes)")

        # Check if it's a zip file
        if filename.lower().endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    for contained_file in sorted(file_list):
                        print(f"   ├─ {filename} contains {contained_file}")
            except Exception as e:
                print(f"   ❌ Error reading ZIP: {e}")

        # Check if it's a rar file
        elif filename.lower().endswith('.rar'):
            try:
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    file_list = rar_ref.namelist()
                    for contained_file in sorted(file_list):
                        print(f"   ├─ {filename} contains {contained_file}")
            except Exception as e:
                print(f"   ❌ Error reading RAR: {e}")

        print()

if __name__ == "__main__":
    list_files_in_download_dir()

