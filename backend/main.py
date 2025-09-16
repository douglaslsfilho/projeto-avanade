from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from db import agents_collection, projects_collection
from models import Agent, Project
from orchestrator import run_project
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helpers ---
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# --- AGENTS ---
@app.post("/agents")
async def create_agent(agent: Agent):
    res = agents_collection.insert_one(agent.dict())
    return {"id": str(res.inserted_id)}

@app.get("/agents")
async def list_agents():
    agents = list(agents_collection.find())
    return [serialize_doc(a) for a in agents]

@app.put("/agents/{agent_id}")
async def update_agent(agent_id: str, agent: Agent):
    agents_collection.update_one({"_id": ObjectId(agent_id)}, {"$set": agent.dict()})
    return {"msg":"Atualizado"}

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    agents_collection.delete_one({"_id": ObjectId(agent_id)})
    return {"msg":"Deletado"}

# --- PROJECTS ---
@app.post("/projects")
async def create_project(project: Project):
    # Se agentes não forem passados, inicializa com 4 agentes padrão
    if not project.agents:
        project.agents = [
            Agent(name="Planner", model_provider="OpenAI"),
            Agent(name="Coder", model_provider="OpenAI"),
            Agent(name="Tester", model_provider="OpenAI"),
            Agent(name="Reviewer", model_provider="OpenAI"),
        ]
    res = projects_collection.insert_one(project.dict())
    return {"id": str(res.inserted_id)}

@app.get("/projects")
async def list_projects():
    projects = list(projects_collection.find())
    return [serialize_doc(p) for p in projects]

@app.put("/projects/{project_id}")
async def update_project(project_id: str, project: Project):
    projects_collection.update_one({"_id": ObjectId(project_id)}, {"$set": project.dict()})
    return {"msg":"Atualizado"}

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"msg":"Deletado"}

@app.post("/projects/{project_id}/run")
async def run_project_endpoint(project_id: str):
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    results = await run_project(project, logger=print)
    projects_collection.update_one({"_id": ObjectId(project_id)}, {"$set": {"steps": results}})
    return results

# --- Chat ---
@app.post("/projects/{project_id}/chat")
async def chat_with_project(project_id: str, message: dict):
    user_message = message.get("text")
    if not user_message:
        raise HTTPException(400, "Mensagem vazia")
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(404, "Projeto não encontrado")

    # Salvar chat
    chat_entry = {"user": user_message, "responses": []}
    projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$push": {"chat_history": chat_entry}}
    )

    # Aqui você pode implementar lógica para responder usando agentes
    # Exemplo: Planner responde a perguntas gerais
    # Para simplificação, vamos simular:
    response_text = f"Simulação de resposta para: {user_message}"
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "chat_history": {"$exists": True}},
        {"$push": {"chat_history.$.responses": response_text}}
    )

    return {"reply": response_text}
