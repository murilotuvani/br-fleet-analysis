from pymongo import MongoClient
from pymongo.errors import PyMongoError
import pandas as pd
import requests
import zipfile
import rarfile
import io
import os
from pathlib import Path

mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

try:
    # Cria a conexão com o MongoDB
    client = MongoClient(mongo_url)

    # Acessa o banco de dados 'fleet' e a coleção 'fleet_month'
    db = client['fleet']
    collection_fleet_month = db['fleet_month']
    collection_fleet = db['fleet']

    # Busca os dados com o mês
    result_list = list(collection_fleet_month.find(
        {"$expr": {"$in": [{"$month": "$month"}, [12]]}},
        {"month": 1, "datasource_url": 1, "_id": 0}
    ))

    # Para cada URL, faz download, descompacta e processa
    all_dataframes = []

    for record in result_list:
        month = record.get('month')
        url = record.get('datasource_url')

        if not url:
            print(f"⚠️ URL vazia para mês {month}, pulando...")
            continue

        try:
            print(f"📥 Fazendo download de {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            csv_data = None

            # Tentar descompactar como ZIP
            try:
                file_bytes = io.BytesIO(response.content)
                with zipfile.ZipFile(file_bytes) as zf:
                    csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
                    if csv_files:
                        print(f"📦 Arquivo ZIP detectado, extraindo {csv_files[0]}...")
                        csv_content = zf.read(csv_files[0])
                        csv_data = io.StringIO(csv_content.decode('utf-8', errors='ignore'))
            except (zipfile.BadZipFile, Exception) as e:
                print(f"   ZIP falhou: {type(e).__name__}")

            # Se não for ZIP, tentar como RAR
            if csv_data is None:
                try:
                    file_bytes = io.BytesIO(response.content)
                    with rarfile.RarFile(file_bytes) as rf:
                        csv_files = [f for f in rf.namelist() if f.lower().endswith('.csv')]
                        if csv_files:
                            print(f"📦 Arquivo RAR detectado, extraindo {csv_files[0]}...")
                            csv_content = rf.read(csv_files[0])
                            csv_data = io.StringIO(csv_content.decode('utf-8', errors='ignore'))
                except Exception as e:
                    print(f"   RAR falhou: {type(e).__name__}")

            # Se nenhum formato funcionou, tentar como CSV direto
            if csv_data is None:
                print(f"📄 Lendo como CSV direto...")
                csv_data = io.StringIO(response.text)

            # Ler CSV com separador ';', ignorando linhas problemáticas
            df = pd.read_csv(csv_data, sep=';', on_bad_lines='skip', engine='python')

            # Adicionar coluna 'month'
            df['month'] = month

            all_dataframes.append(df)
            print(f"✅ Processado com sucesso: {len(df)} linhas para mês {month}")

        except requests.RequestException as req_err:
            print(f"❌ Erro ao baixar URL {url}: {req_err}")
        except Exception as e:
            print(f"❌ Erro ao processar {url}: {e}")

    # Concatenar todos os dataframes
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"\n📊 Total de {len(final_df)} linhas consolidadas")

        # Inserir na collection 'fleet'
        records_to_insert = final_df.to_dict('records')
        result = collection_fleet.insert_many(records_to_insert)
        print(f"✅ {len(result.inserted_ids)} documentos inseridos na collection 'fleet'")
    else:
        print("⚠️ Nenhum arquivo foi processado com sucesso")

except PyMongoError as pe:
    print(f"❌ Erro no MongoDB: {pe}")
except Exception as ex:
    print(f"❌ Erro geral: {ex}")
finally:
    client.close()
