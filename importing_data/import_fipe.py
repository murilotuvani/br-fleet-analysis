# !pip install pymongo
# !pip install psycopg2-binary
# !pip install kagglehub
# %%
import os
import kagglehub
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import CHAR, VARCHAR, SMALLINT
from sqlalchemy.dialects.mysql import BIGINT  # Para conseguir usar UNSIGNED
from urllib.parse import quote
from pymongo import MongoClient
from pymongo.errors import PyMongoError

print("Downloading FIPE data ...")
# 1. Baixa e descompacta automaticamente o dataset
path = kagglehub.dataset_download("franckepeixoto/tabela-fipe")

# 2. Encontra o arquivo extraído no diretório temporário
arquivos = os.listdir(path)
caminho_csv = os.path.join(path, arquivos[0])

# 3. Carrega no DataFrame do Pandas
fdf = pd.read_csv(caminho_csv)

print(fdf.head())

fdf['modelo_base'] = fdf['modelo'].str.split().str[0]
fdf.drop('Unnamed: 0', axis=1, inplace=True)

df_fipe = fdf[['codigoFipe', 'marca', 'modelo', 'anoModelo', 'modelo_base']].drop_duplicates()

# Importint into MongoDB
mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"
print("Start importing data to databases ...")
try:
    # Cria a conexão com o MongoDB
    client = MongoClient(mongo_url)

    # Acessa o banco de dados 'fleet' e a coleção 'fipe'
    db = client['fleet']
    collection = db['fipe']

    # Remove a coleção existente para substituir os dados (similar ao if_exists='replace')
    collection.drop()

    # Converte o DataFrame para uma lista de dicionários
    records = df_fipe.to_dict('records')

    # Insere os registros
    if records:
        collection.insert_many(records)
        print("Data imported into MongoDB")
except PyMongoError as pe:
    print(f"Erro no MongoDB: {pe}")
except Exception as ex:
    print(f"Erro geral: {ex}")
finally:
    client.close()

# Importint into MySQL
url = "mysql+pymysql://fleet_analyst:%s@127.0.0.1:3306/fleet" % quote("superSecret")
engineMysql = create_engine(url)

dbConnection = engineMysql.connect()
transaction = dbConnection.begin()

dtype_mapping = {
    'index': BIGINT(unsigned=True),
    'codigoFipe': CHAR(10),
    'marca': CHAR(15),
    'modelo': VARCHAR(100),
    'anoModelo': SMALLINT()
}

try:
    df_fipe.to_sql('fipe', con=dbConnection, if_exists='replace', index=True, dtype=dtype_mapping)
    transaction.commit()
except ValueError as vx:
    print(vx)
except Exception as ex:
    print(ex)
else:
    print("Data imported into MySQL")
finally:
    dbConnection.close()

# Importing into PostgreSQL
url = "postgresql+psycopg2://fleet_analyst:%s@127.0.0.1:5432/fleet" % quote("superSecret")
enginePostgres = create_engine(url)

dbConnection = enginePostgres.connect()
transaction = dbConnection.begin()

dtype_mapping = {
    'index': BIGINT(unsigned=True),
    'codigoFipe': CHAR(10),
    'marca': CHAR(15),
    'modelo': VARCHAR(100),
    'anoModelo': SMALLINT()
}

try:
    df_fipe.to_sql('fipe', con=dbConnection, if_exists='replace', index=True, dtype=dtype_mapping)
    transaction.commit()
except ValueError as vx:
    print(vx)
except Exception as ex:
    print(ex)
else:
    print("Data imported into Postgres")
finally:
    dbConnection.close()