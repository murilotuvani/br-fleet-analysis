import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import CHAR, VARCHAR, SMALLINT, DATE
from sqlalchemy.dialects.mysql import BIGINT  # Para conseguir usar UNSIGNED
from urllib.parse import quote
from pymongo import MongoClient
from pymongo.errors import PyMongoError

#renavam_file = '/Users/murilotuvani/projects/br-fleet-analysis/datasources/datasources_renavam.xlsx'
renavam_file = '../datasources/datasources_renavam.xlsx'
renavam_df = pd.read_excel(renavam_file)

renavam_df.head()

mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

try:
    # Cria a conexão com o MongoDB
    client = MongoClient(mongo_url)

    # Acessa o banco de dados 'fleet' e a coleção 'fleet_month'
    db = client['fleet']
    collection = db['fleet_month']

    # Remove a coleção existente para substituir os dados
    collection.drop()

    # Converte o DataFrame para uma lista de dicionários
    records = renavam_df.to_dict('records')

    # Insere os registros na collection
    if records:
        collection.insert_many(records)
        print("Tabela renavam importada para o MongoDB com sucesso!")
except PyMongoError as pe:
    print(f"Erro no MongoDB: {pe}")
except Exception as ex:
    print(f"Erro geral: {ex}")
finally:
    client.close()

# Importando no MySQL
url = "mysql+pymysql://fleet_analyst:%s@127.0.0.1:3306/fleet" % quote("superSecret")
engineMysql = create_engine(url)

dbConnection = engineMysql.connect()
transaction = dbConnection.begin()

dtype_mapping_renavam = {
    'month': DATE(),
    'page_url': VARCHAR(255),
    'datasource_url': VARCHAR(255)
}

try:
    renavam_df.to_sql('fleet_month', con=dbConnection, if_exists='replace', index=False, dtype=dtype_mapping_renavam)
    transaction.commit()
except ValueError as vx:
    print(vx)
except Exception as ex:
    print(ex)
else:
    print("Tabela renavam importada para o Postgres com sucesso!")
finally:
    dbConnection.close()

# Importanto no PostgreSQL
url = "postgresql+psycopg2://fleet_analyst:%s@127.0.0.1:5432/fleet" % quote("superSecret")
enginePostgres = create_engine(url)

dbConnection = enginePostgres.connect()
transaction = dbConnection.begin()

dtype_mapping_renavam = {
    'month': DATE(),
    'page_url': VARCHAR(255),
    'datasource_url': VARCHAR(255)
}

try:
    # Salvando no Postgres com os tipos especificados (index=False para não gerar coluna de índice extra)
    renavam_df.to_sql('fleet_month', con=dbConnection, if_exists='replace', index=False, dtype=dtype_mapping_renavam)
    transaction.commit()
except ValueError as vx:
    print(vx)
except Exception as ex:
    print(ex)
else:
    print("Tabela renavam importada para o Postgres com sucesso!")
finally:
    dbConnection.close()