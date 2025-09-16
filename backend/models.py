from pydantic import BaseModel
from typing import List, Dict, Optional

class Agent(BaseModel):
    name: str
    model_provider: str  # OpenAI ou Gemini

class Project(BaseModel):
    name: str
    description: str = ""
    agents: Optional[List[Agent]] = []  # Podemos inicializar com os 4 agentes padrão
    steps: List[Dict] = []  # Workflow
    chat_history: List[Dict] = []  # Histórico de mensagens
