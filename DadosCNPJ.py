# Dados capturados a partir da API BrasilAPI para CNPJ, organizados em um DataFrame do Pandas e exportados para um arquivo CSV.

import requests
import time
import pandas as pd

def consultar_cnpj(cnpj):
    # Limpando o CNPJ (removendo pontos e traços)
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            return {
                "Empresa": dados.get("razao_social"),
                "CNPJ": dados.get("cnpj"),
                "Tipo Endereço": dados.get("descricao_tipo_de_logradouro"),
                "Endereço": dados.get("logradouro"),
                "Número": dados.get("numero"),
                "Complemento": dados.get("complemento"),
                "Bairro": dados.get("bairro"),
                "Cidade": dados.get("municipio"),
                "UF": dados.get("uf")
            }
        else:
            return {"Erro": f"CNPJ {cnpj} não encontrado ou erro na API."}
    except Exception as e:
        return {"Erro": str(e)}

# Exemplo de uso
lista_cnpjs = [
"02.421.421/0031-37",
"02.421.421/0012-74",
"02.421.421/0020-84",
"02.421.421/0017-89",
"02.421.421/0006-26",
"02.421.421/0026-70",
"02.421.421/0008-98",
"02.421.421/0001-11",
"02.421.421/0129-85",
"02.421.421/0025-99",
"02.421.421/0016-06",
"02.421.421/0023-27",
"02.421.421/0019-40",
"02.421.421/0021-65",
"02.421.421/0015-17",
"02.421.421/0239-10",
"02.421.421/0010-02",
"02.421.421/0011-93",
"02.421.421/0024-08",
"02.421.421/0007-07",
"02.421.421/0009-79",
"02.421.421/0029-12",
"02.421.421/0013-55",
"02.421.421/0028-31"
] # Exemplos: Banco do Brasil e Vale
resultados = []

# 2. Fazendo as consultas e gerando uma lista de dicionários
dados_coletados = []
for c in lista_cnpjs:
    print(f"Buscando: {c}...")
    dados_coletados.append(consultar_cnpj(c))
    time.sleep(1) # Respeitando o limite da API gratuita

# 3. Criando o DataFrame
df = pd.DataFrame(dados_coletados)

# Exibe o DataFrame no console
print("\n--- Resultado Final ---")
print(df)