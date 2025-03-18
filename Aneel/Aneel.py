import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import time  # Importe a biblioteca time

# URL base da API para consultas SQL
url = "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search_sql"

#SCEE Considera quando for GD

# Consulta SQL
query = """
    SELECT "SigAgente", "DatInicioVigencia", "DatFimVigencia", "DscSubGrupo", "DscModalidadeTarifaria", "VlrTUSD", "VlrTE", "DscUnidadeTerciaria", "NomPostoTarifario", "DscDetalhe"
    FROM "fcf2906c-7c32-4b9b-a637-054e7a5234f4"
    WHERE "DatInicioVigencia" >= '2020-01-01'
    AND (("DscSubGrupo" = 'B3' AND ("DscModalidadeTarifaria" = 'Branca' OR "DscModalidadeTarifaria" = 'Convencional'))
    OR (("DscSubGrupo" = 'A4' OR "DscSubGrupo" = 'A2')
    AND ("DscModalidadeTarifaria" = 'Azul' OR "DscModalidadeTarifaria" = 'Verde')))
    AND ("DscBaseTarifaria" = 'Tarifa de Aplicação')
"""

# Monta a URL com a query
params = {"sql": query}

print("Fazendo a requisição dos dados...")
# Fazendo a requisição
response = requests.get(url, params=params)

# Verifica se a requisição foi bem-sucedida
data = response.json()  # Converte a resposta JSON em um dicionário Python
records = data.get("result", {}).get("records", [])  # Obtém os registros da resposta

print("Criando DataFrame...")
# Cria um DataFrame a partir dos dados
df = pd.DataFrame(records)

print("Convertendo colunas de valores...")
# Converte as colunas de valores para float
df["VlrTUSD"] = df["VlrTUSD"].str.replace(",", ".").astype(float)
df["VlrTE"] = df["VlrTE"].str.replace(",", ".").astype(float)

print("Criando colunas calculadas...")
# Cria colunas calculadas
df["Tarifa Vigente"] = df["VlrTUSD"] + df["VlrTE"]
df["TarifaPisCofinsICMS"] = (df["VlrTUSD"] + df["VlrTE"]) / 0.95

print("Convertendo coluna de data...")
# Converte a coluna DatFimVigencia para datetime
df["DatFimVigencia"] = pd.to_datetime(df["DatFimVigencia"], errors="coerce")

print("Verificando vigência das tarifas...")
# Obtém a data de hoje
data_atual = datetime.today()

# Adiciona uma nova coluna "Alerta" ao DataFrame
df["Alerta"] = df["DatFimVigencia"].apply(lambda x: "Não Vigente" if x < data_atual else "Vigente")

# Exibe alerta no terminal se houver tarifas vencidas
tarifas_vencidas = df[df["Alerta"] == "Não Vigente"]

if not tarifas_vencidas.empty:
    print("ALERTA: Existem tarifas Não Vigentes!")
    print(tarifas_vencidas[["SigAgente", "DatFimVigencia", "Alerta"]])

print("Salvando DataFrame em CSV...")
# Simula um processamento para a barra de progresso (opcional, mas demonstra o uso)
for i in tqdm(range(100), desc="Salvando CSV"):
    time.sleep(0.01)  # Pequena pausa para visualizar a barra

# Salva o DataFrame atualizado em um arquivo CSV
df.to_csv("dados_aneel.csv", index=False, sep=';', decimal=',')
print(f"\nTabela exportada com sucesso para '{"dados_aneel.csv"}'.")

print("Salvando DataFrame em Parquet...")
# Simula outro processamento para a barra de progresso
for i in tqdm(range(100), desc="Salvando Parquet"):
    time.sleep(0.01)

df.to_parquet("BaseAneel.parquet")
print(f"\nTabela exportada com sucesso para '{"BaseAneel.parquet"}'.")

print("Processo concluído!")