from pymongo import MongoClient
from pymongo.errors import PyMongoError

from pathlib import Path
from urllib.parse import urlparse, unquote
import hashlib
import requests


mongo_url = "mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin"

# Diretório de download (crie se não existir)
download_dir = Path("/Volumes/dados/fleet")
download_dir.mkdir(parents=True, exist_ok=True)

def _safe_filename_from_url(url, response_content=None):
    """Generate a safe filename from the URL or response headers."""
    parsed = urlparse(url)
    name = unquote(Path(parsed.path).name)
    if name:
        return name
    # fallback to hash
    h = hashlib.sha256(url.encode('utf-8')).hexdigest()
    return f"file_{h}.dat"

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

    for record in result_list:
        month = record.get('month')
        url = record.get('datasource_url')

        if not url:
            print(f"⚠️ URL vazia para mês {month}, pulando...")
            continue

        try:
            # Determine target file path
            filename = _safe_filename_from_url(url)
            file_path = download_dir / filename

            # If file does not exist, download and save
            if not file_path.exists():
                try:
                    print(f"📥 Baixando {url} para {file_path}...")
                    resp = requests.get(url, timeout=60)
                    resp.raise_for_status()
                    file_path.write_bytes(resp.content)
                    print(f"💾 Salvo em {file_path}")
                except requests.RequestException as req_err:
                    print(f"❌ Erro ao baixar {url}: {req_err}")
                    continue
            else:
                print(f"📁 Arquivo já existe: {file_path}, pulando download")
        except Exception as inner_err:
            print(f"❌ Erro ao processar {url}: {inner_err}")

except PyMongoError as pe:
    print(f"❌ Erro no MongoDB: {pe}")
except Exception as ex:
    print(f"❌ Erro geral: {ex}")
finally:
    # Close client if it was created
    try:
        client.close()
    except NameError:
        # client was never created
        pass
    except Exception:
        pass
