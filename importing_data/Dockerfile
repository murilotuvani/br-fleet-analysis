FROM python:3.11-slim

# Instala o mdbtools (necessário para ler arquivos .mdb/.accdb no Linux)
RUN apt-get update && apt-get install -y \
    mdbtools \
    && rm -rf /var/lib/apt/lists/*

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir pandas pandas-access

WORKDIR /app