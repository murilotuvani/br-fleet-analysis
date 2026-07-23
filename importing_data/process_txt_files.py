#!/usr/bin/env python3
"""
Process TXT files from compressed archives and insert into MongoDB
1. Extract TXT files from ZIP/RAR archives
2. Load as CSV (separator: ;, first line as header)
3. Find corresponding MongoDB record to get 'month' value
4. Add 'month' column to dataframe
5. Insert all records into 'fleet' collection
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pathlib import Path
import zipfile
import rarfile
import pandas as pd
import tempfile
import re
import os

# MongoDB connection
mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

# Download directory
download_dir = Path("/Volumes/dados/fleet")

def process_compressed_files():
    """Process all TXT files from compressed archives"""

    if not download_dir.exists():
        print(f"❌ Directory does not exist: {download_dir}")
        return

    try:
        # Connect to MongoDB
        client = MongoClient(mongo_url)
        db = client['fleet']
        collection_fleet_month = db['fleet_month']
        collection_fleet = db['fleet']

        print(f"📁 Processing files in: {download_dir}\n")
        print("=" * 80)

        # List all compressed files
        compressed_files = sorted([
            f for f in download_dir.iterdir()
            if f.is_file() and f.name.lower().endswith(('.zip', '.rar'))
        ])

        total_records_inserted = 0

        for compressed_file in compressed_files:
            compressed_filename = compressed_file.name
            print(f"\n📦 Processing: {compressed_filename}")

            try:
                # Find month in MongoDB
                # db.fleet_month.find({ datasource_url: { $regex: "\\.compressed_filename$", $options: "i" } });

                pattern = f"{re.escape(compressed_filename)}$"

                month_record = collection_fleet_month.find_one({
                    "datasource_url": {
                        "$regex": pattern,
                        "$options": "i"  # 'i' para case-insensitive
                    }
                })

                if not month_record:
                    print(f"   ⚠️ No record found in fleet_month for: {compressed_filename}")
                    continue

                month = month_record.get('month')
                print(f"   📅 Found month: {month}")

                # Extract and process files based on type
                contained_files = []

                if compressed_filename.lower().endswith('.zip'):
                    try:
                        with zipfile.ZipFile(compressed_file, 'r') as zip_ref:
                            contained_files = zip_ref.namelist()
                    except Exception as e:
                        print(f"   ❌ Error reading ZIP: {e}")
                        continue

                elif compressed_filename.lower().endswith('.rar'):
                    try:
                        with rarfile.RarFile(compressed_file, 'r') as rar_ref:
                            contained_files = rar_ref.namelist()
                    except Exception as e:
                        print(f"   ❌ Error reading RAR: {e}")
                        continue

                # Process TXT files
                txt_files = [f for f in contained_files if f.upper().endswith('.TXT')]

                if not txt_files:
                    print(f"   ℹ️ No TXT files found in archive")
                    continue

                for txt_filename in txt_files:
                    print(f"   📄 Processing TXT: {txt_filename}")

                    try:
                        # Extract and read TXT file
                        with tempfile.TemporaryDirectory() as temp_dir:
                            if compressed_filename.lower().endswith('.zip'):
                                with zipfile.ZipFile(compressed_file, 'r') as zip_ref:
                                    zip_ref.extract(txt_filename, temp_dir)
                            else:
                                with rarfile.RarFile(compressed_file, 'r') as rar_ref:
                                    rar_ref.extract(txt_filename, temp_dir)

                            # Read CSV file
                            txt_path = Path(temp_dir) / txt_filename
                            print(f"      Loading CSV from: {txt_path}")

                            df = pd.read_csv(
                                txt_path,
                                sep=';',
                                header=0
                            )

                            # Add month column
                            df['month'] = month

                            print(f"      ✓ Loaded {len(df)} records")
                            print(f"      Columns: {list(df.columns)}")

                            # Convert dataframe to list of documents
                            records = df.to_dict('records')

                            # Insert into fleet collection
                            if records:
                                result = collection_fleet.insert_many(records)
                                num_inserted = len(result.inserted_ids)
                                total_records_inserted += num_inserted
                                print(f"      ✅ Inserted {num_inserted} records into fleet collection")

                    except Exception as e:
                        print(f"      ❌ Error processing TXT file: {e}")
                        import traceback
                        traceback.print_exc()
                        continue

            except Exception as e:
                print(f"   ❌ Error processing compressed file: {e}")
                import traceback
                traceback.print_exc()
                continue

        print("\n" + "=" * 80)
        print(f"✅ Process completed! Total records inserted: {total_records_inserted}")

    except PyMongoError as pe:
        print(f"❌ MongoDB error: {pe}")
    except Exception as ex:
        print(f"❌ General error: {ex}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            client.close()
        except NameError:
            pass
        except Exception:
            pass

if __name__ == "__main__":
    process_compressed_files()

