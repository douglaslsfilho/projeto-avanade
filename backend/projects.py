from fastapi import APIRouter, HTTPException
from bson import ObjectId
from models import Project, Agent
from db import projects_collection, agents_collection
from agents import PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent
import asyncio

router = APIRouter(prefix="/projects", tags=["Projects"])

# Mapeamento de agentes
agents_map = {
    "Planner": PlannerAgent(),
    "Coder": CoderAgent(),
    "Tester": TesterAgent(),
    "Reviewer": ReviewerAgent(),
}

# Helper para serializar ObjectId
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# --- Chat endpoint ---
@router.post("/{project_id}/chat")
async def chat_with_project(project_id: str, message: dict):
    user_message = message.get("text")
    if not user_message:
        raise HTTPException(400, "Mensagem vazia")

    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(404, "Projeto não encontrado")

    # Inicializa chat_history se não existir
    if "chat_history" not in project:
        project["chat_history"] = []

    # Salvar mensagem do usuário
    chat_entry = {"user": user_message, "responses": []}
    projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$push": {"chat_history": chat_entry}}
    )

    # Simulação de resposta pelos agentes (pode ser expandido para async real)
    # Exemplo: só o Planner responde por enquanto
    planner_provider = project["agents"][0]["model_provider"] if project.get("agents") else "OpenAI"
    planner_reply = await agents_map["Planner"].run(project.get("description", ""), print, task_id=str(project_id), provider=planner_provider)

    projects_collection.update_one(
        {"_id": ObjectId(project_id), "chat_history": {"$exists": True}},
        {"$push": {"chat_history.$.responses": planner_reply}}
    )

    return {"reply": planner_reply}

# --- Listar projetos ---
@router.get("/")
def list_projects():
    projects = list(projects_collection.find())
    return [serialize_doc(p) for p in projects]

# --- Criar projeto ---
@router.post("/")
def create_project(project: Project):
    # Inicializa 4 agentes padrão se não passados
    if not project.agents:
        project.agents = [
            Agent(name="Planner", model_provider="OpenAI"),
            Agent(name="Coder", model_provider="OpenAI"),
            Agent(name="Tester", model_provider="OpenAI"),
            Agent(name="Reviewer", model_provider="OpenAI"),
        ]
    res = projects_collection.insert_one(project.dict())
    return {"id": str(res.inserted_id)}

# --- Atualizar projeto ---
@router.put("/{project_id}")
def update_project(project_id: str, project: Project):
    projects_collection.update_one({"_id": ObjectId(project_id)}, {"$set": project.dict()})
    return {"msg": "Atualizado"}

# --- Deletar projeto ---
@router.delete("/{project_id}")
def delete_project(project_id: str):
    projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"msg": "Deletado"}
