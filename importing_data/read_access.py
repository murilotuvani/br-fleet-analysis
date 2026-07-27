"""
This line is required only once, to build the container image:
docker build -t leitor-mdb .

For each file:

docker run --rm \
  -v "/Volumes/dados/fleet/Quantidade de Veiculos Por UF Municipio e Marca_Modelo_JUL_2013.mdb:/data/arquivo.mdb" \
  -v "$(pwd):/app" \
  leitor-mdb python read_access.py

docker run --rm \
  -v "/Volumes/dados/fleet/I_Frota_por_UF_Municipio_Marca_e_Modelo_Ano_Julho_2019.accdb:/data/arquivo.accdb" \
  -v "$(pwd):/app" \
  leitor-mdb python read_access.py


docker run --rm \
  -v "/Volumes/dados/fleet/I_Frota_por_UF_Municipio_Marca_e_Modelo_Julho_2018.accdb:/data/arquivo.accdb" \
  -v "$(pwd):/app" \
  leitor-mdb python read_access.py
"""

import io
import subprocess
import pandas as pd

from pathlib import Path
import sys

path_mdb = Path("/data/arquivo.mdb")
path_accdb = Path("/data/arquivo.accdb")

if path_mdb.is_file():
    mdb_path = str(path_mdb)
elif path_accdb.is_file():
    mdb_path = str(path_accdb)
else:
    print("No file found")
    sys.exit()

# 1. Lista as tabelas usando mdb-tables com delimitador de quebra de linha (-1)
# Isso impede que o mdbtools se confunda com os espaços no nome da tabela!
output_tables = subprocess.check_output(["mdb-tables", "-1", mdb_path]).decode("utf-8")
tabelas = [t.strip() for t in output_tables.splitlines() if t.strip()]

print("Tabelas reais encontradas:")
print(tabelas)

if tabelas:
    nome_tabela = tabelas[0]
    print(f"\nExportando e carregando a tabela: '{nome_tabela}'...")

    # 2. Executa o mdb-export para converter a tabela diretamente para um fluxo CSV
    csv_bytes = subprocess.check_output(["mdb-export", mdb_path, nome_tabela])

    # 3. Carrega o CSV direto para o DataFrame do pandas sem salvar em disco
    header_row = 1 if mdb_path.lower().endswith('.accdb') else 0 # Se for .accdb, ignora a primeira linha de cabeçalho
    df = pd.read_csv(io.BytesIO(csv_bytes), header=header_row)

    df.rename(
        columns={
            'UF': 'state',
            'MunicÃ\xadpio': 'city',
            'Ano FabricaÃ§Ã£o VeÃ\xadculo CRV': 'makeYear',
            'Qtd. VeÃ\xadculos': 'Qtd. Veículos'
        },
        inplace=True
    )

    df.rename(
        columns={
            'MUNICÍPIO': 'city',
            'MARCA MODELO': 'brandModel',
            'Ano FabricaÃ§Ã£o VeÃ\xadculo CRV': 'makeYear',
            'QT DE VEÍCULOS': 'quantity'
        },
        inplace=True
    )

    df.rename(
        columns={
            'Município': 'city',
            'Marca Modelo': 'brandModel',
            'Ano FabricaÃ§Ã£o VeÃ\xadculo CRV': 'makeYear',
            'QT DE VEÍCULOS': 'quantity'
        },
        inplace=True
    )

    df.rename(
        columns={
            'Município': 'city',
            'Marca Modelo': 'brandModel',
            'Ano Fabricação Veículo CRV': 'makeYear',
            'Qtd. Veículos': 'quantity'
        },
        inplace=True
    )

    if header_row == 1:
        df.drop(columns=['1'], inplace=True)

    print("\nDataFrame carregado com sucesso!")
    print(df.head())
    print(f"\nTotal de linhas: {len(df)}")

    print("\nColumns : ")
    print(df.describe())
    print("\n")

    print("\nColumns : ")
    print(df.columns.tolist())
    print("\n")
