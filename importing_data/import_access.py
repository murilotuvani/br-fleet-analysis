"""
Run the server with the correct network:
docker network create mongo-net
docker stop mongo
docker network connect mongo-net mongo
docker start mongo

docker run -d --name mongosecondary --net mongo-net -p 27018:27017 -e MONGO_INITDB_ROOT_USERNAME=mongoadmin -e MONGO_INITDB_ROOT_PASSWORD=monster mongo

docker network connect mongo-net mongosecondary
docker exec -it mongosecondary mongosh mongodb://fleet_analyst:superSecret@mongo:27017/


This line is required only once, to build the container image:
docker build -t leitor-mdb .

## Teste conectivity to the databases containers.
docker run --rm -it leitor-mdb /bin/bash

docker run -d --name mongosecondary -p 27018:27017 -e MONGO_INITDB_ROOT_USERNAME=mongoadmin -e MONGO_INITDB_ROOT_PASSWORD=monster mongo
docker exec -it mongosecondary /bin/bash
mongosh mongodb://mongoadmin:secret@mongo:27017/

docker network create mongo-net
docker network rm mongo-net


## Running the process for each file:
docker run --rm --name read-mdb \
  -v "/Users/murilotuvani/Downloads/Quantidade de Veiculos Por UF Municipio e Marca_Modelo_JUL_2013.mdb:/data/arquivo.mdb" \
  -v "$(pwd):/app" \
  --net mongo-net \
  leitor-mdb python import_access.py 2013-07

Result:
% docker run --rm --name read-mdb \
  -v "/Users/murilotuvani/Downloads/Quantidade de Veiculos Por UF Municipio e Marca_Modelo_JUL_2013.mdb:/data/arquivo.mdb" \
  -v "$(pwd):/app" \
  --net mongo-net \
  leitor-mdb python import_access.py 2013-07
Successfully imported 5113446 records for month 2013-07 into the 'fleet' collection.
"""

import io
import subprocess
import pandas as pd
from pymongo import MongoClient
import argparse

# Setup argument parser
parser = argparse.ArgumentParser(description='Import data from an Access database to MongoDB.')
parser.add_argument('month', type=str, help='The month of the data in "yyyy-mm" format.')
args = parser.parse_args()

mdb_path = "/data/arquivo.mdb"
#mongo_url = "mongodb://mongoadmin:secret@127.0.0.1:27017/"
mongo_url = "mongodb://mongoadmin:secret@mongo:27017/"

# 1. List tables using mdb-tables
output_tables = subprocess.check_output(["mdb-tables", "-1", mdb_path]).decode("utf-8")
tables = [t.strip() for t in output_tables.splitlines() if t.strip()]

if tables:
    table_name = tables[0]

    # 2. Export the table to a CSV stream
    csv_bytes = subprocess.check_output(["mdb-export", mdb_path, table_name])

    # 3. Load CSV into a pandas DataFrame
    df = pd.read_csv(io.BytesIO(csv_bytes))

    # 4. Add the 'month' column
    df['month'] = args.month

    # 5. Connect to MongoDB and insert data
    client = MongoClient(mongo_url)
    db = client['fleet']
    collection = db['fleet']
    
    records = df.to_dict('records')
    collection.insert_many(records)
    
    print(f"Successfully imported {len(records)} records for month {args.month} into the 'fleet' collection.")
else:
    print("No tables found in the database.")