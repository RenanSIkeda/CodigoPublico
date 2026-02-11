# Dados capturados a partir da API BrasilAPI para CNPJ, organizados em um DataFrame do Pandas e exportados para um arquivo CSV.
# Link para o site https://brasilapi.com.br/docs#tag/Termos-de-uso
#https://brasilapi.com.br/

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
    "00.000.000/0001-91",  # CNPJ fictício para teste
    "33.000.000/0001-91"   # Outro CNPJ fictício
#Colocar a lista de CNPJ que deseja consultar aqui
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