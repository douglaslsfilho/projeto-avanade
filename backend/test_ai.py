import requests

API_URL = "http://127.0.0.1:8000"  # ou seu IP público se estiver usando outro host

# ======== CONFIGURAÇÃO INICIAL ========
project_name = "Projeto Teste"
project_description = "Descrição do projeto teste"
message_text = "Mensagem de teste do chat"

print("=== TESTE DE BACKEND ===\n")

# 1️⃣ Criar projeto
try:
    res = requests.post(f"{API_URL}/projects", json={"name": project_name})
    print("Criar Projeto:", res.status_code, res.text)
    if res.status_code == 200:
        project = res.json()
        project_id = project.get("_id") or project.get("id")
        if not project_id:
            raise Exception("ID do projeto não encontrado na resposta")
    else:
        raise Exception("Falha ao criar projeto")
except Exception as e:
    print("Erro no Create Project:", e)
    exit()

# 2️⃣ Atualizar descrição
try:
    res = requests.post(f"{API_URL}/projects/{project_id}/chat", json={"text": project_description})
    print("Atualizar Descrição:", res.status_code, res.text)
except Exception as e:
    print("Erro no Update Description:", e)

# 3️⃣ Rodar projeto (AI)
try:
    res = requests.post(f"{API_URL}/projects/{project_id}/run")
    print("Rodar Projeto:", res.status_code, res.text)
except Exception as e:
    print("Erro no Run Project:", e)

# 4️⃣ Chat no projeto
try:
    res = requests.post(f"{API_URL}/projects/{project_id}/chat", json={"text": message_text})
    print("Chat Projeto:", res.status_code, res.text)
except Exception as e:
    print("Erro no Chat Project:", e)

# 5️⃣ Buscar todos os projetos
try:
    res = requests.get(f"{API_URL}/projects")
    print("Listar Projetos:", res.status_code, res.text)
except Exception as e:
    print("Erro no Get Projects:", e)

# 6️⃣ Deletar projeto
try:
    res = requests.delete(f"{API_URL}/projects/{project_id}")
    print("Deletar Projeto:", res.status_code, res.text)
except Exception as e:
    print("Erro no Delete Project:", e)

print("\n=== TESTE FINALIZADO ===")



