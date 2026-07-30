import pandas as pd
from transformers import pipeline

# -----------------------------
# 1. Create a sample budget dataset
# -----------------------------
data = pd.DataFrame({
    "Department": ["IT", "Finance", "HR", "Sales", "Operations"],
    "Previous_Budget": [120000, 90000, 70000, 150000, 200000],
    "Current_Spending": [135000, 87000, 65000, 162000, 210000],
    "Active_Projects": [5, 3, 2, 6, 8],
    "Employees": [12, 8, 6, 15, 20]
})

# Calculate budget variation
data["Variation_%"] = ((data["Current_Spending"] - data["Previous_Budget"]) / data["Previous_Budget"]) * 100

print("📊 Budget Dataset:\n")
print(data)

# -----------------------------
# 2. Load local lightweight LLM (CPU-based)
# -----------------------------
print("\n⏳ Loading local model...")

# ⚙️ Aqui você pode trocar o nome do modelo abaixo para outras opções recomendadas:
# -------------------------------------------------------------------------------
# 🧩 Modelos LEVES (rodam em CPU com 8 GB RAM):
# "distilgpt2"                        → Muito leve (~300 MB), rápido, mas respostas simples.
# "google/flan-t5-small"              → Segue instruções básicas (melhor que GPT-2).
# "google/flan-t5-base"               → Boa qualidade e compreensão de tarefas.
# "google/gemma-2b-it"                → Novo modelo instruído da Google (bom equilíbrio).
# "pierreguillou/gpt2-small-portuguese" → Versão GPT-2 treinada em português.

# 🚀 Modelos INTERMEDIÁRIOS (melhor texto, exigem 12–16 GB RAM):
# "tiiuae/falcon-7b-instruct"         → Modelo de 7B instruído, entende prompts complexos.
# "mistralai/Mistral-7B-Instruct-v0.1" → Gera textos muito coerentes e corporativos.
# "google/flan-t5-large"              → Alta qualidade, mas mais pesado.
# "google/gemma-7b-it"                → Novo, otimizado para instruções e análise.

# 💼 Modelos AVANÇADOS (precisam de GPU ou 24+ GB RAM):
# "meta-llama/Llama-3.1-8B-Instruct"  → Excelente qualidade e raciocínio, ideal para relatórios.
# "meta-llama/Llama-2-7b-chat-hf"     → Boa alternativa open-source com linguagem natural fluente.
# "NousResearch/Nous-Hermes-2-Mistral-7B" → Ajustado para tarefas de análise corporativa e resposta longa.

model = pipeline(
    "text-generation",
    model="tiiuae/falcon-7b-instruct",  # Troque aqui por qualquer modelo listado acima
    device=-1                           # Força execução em CPU
)

# -----------------------------
# 3. Build the analysis prompt
# -----------------------------
summary = data.to_string(index=False)

prompt = f"""
You are a senior financial analyst.
Review the following budget data and write a short executive report.

Budget data:
{summary}

Include:
1. Departments with budget overruns.
2. Areas with strong financial control.
3. Strategic recommendations.
"""

# -----------------------------
# 4. Generate report using local LLM
# -----------------------------
print("\n🧠 Generating analysis with local model...\n")
response = model(
    prompt,
    max_new_tokens=300,
    temperature=0.5,
    do_sample=True,
    top_p=0.8
)

# -----------------------------
# 5. Display report
# -----------------------------
generated_text = response[0]["generated_text"].replace(prompt, "").strip()

print("🧾 Executive Budget Report:\n")
print(generated_text)
