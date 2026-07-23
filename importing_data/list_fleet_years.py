from pymongo import MongoClient
from pymongo.errors import PyMongoError
import pandas as pd

mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

try:
    # Cria a conexão com o MongoDB
    client = MongoClient(mongo_url)

    # Acessa o banco de dados 'fleet' e a coleção 'fleet_month'
    db = client['fleet']
    collection = db['fleet_month']

    result_list = list(collection.find(
        {"$expr": {"$in": [{"$month": "$month"}, [12]]}},
        {"month": 1, "datasource_url": 1, "_id": 0}
    ))
    df = pd.DataFrame(result_list)
    print(df)
except PyMongoError as pe:
    print(f"Erro no MongoDB: {pe}")
except Exception as ex:
    print(f"Erro geral: {ex}")
finally:
    client.close()
