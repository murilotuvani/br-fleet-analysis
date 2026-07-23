from pymongo import MongoClient
from pymongo.errors import PyMongoError
import pandas as pd
import requests
import zipfile
import rarfile
import io

mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

# Diretório de download (crie se não existir)
download_dir = Path("/Volumes/dados/fleet")