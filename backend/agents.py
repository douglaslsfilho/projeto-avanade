import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def call_ai(provider: str, prompt: str) -> str:
    if provider == "OpenAI":
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message['content']
    elif provider == "Gemini":
        # Simulação, ajuste conforme SDK/API Gemini
        return f"[Gemini Response]: {prompt}"
    else:
        return "Provedor de IA desconhecido."

class PlannerAgent:
    name = "Planner"

    async def run(self, scope, logger, task_id, provider):
        logger(f"{task_id} | {self.name}: Recebi escopo, criando subtarefas...")
        prompt = f"Você é um planejador. Divida o seguinte escopo em 3-6 passos:\n{scope}"
        out = await call_ai(provider, prompt)
        steps = [s.strip() for s in out.split("\n") if s.strip()]
        logger(f"{task_id} | {self.name}: Planner gerou {len(steps)} passos.")
        return steps

class CoderAgent:
    name = "Coder"

    async def run(self, step, logger, task_id, provider):
        logger(f"{task_id} | {self.name}: Gerando código para: {step}")
        prompt = f"Escreva um snippet Python que implemente: {step}. Só o código com comentário."
        code = await call_ai(provider, prompt)
        logger(f"{task_id} | {self.name}: Código gerado.")
        return {"code": code}

class TesterAgent:
    name = "Tester"

    async def run(self, payload, logger, task_id, provider):
        logger(f"{task_id} | {self.name}: Gerando casos de teste (simulado).")
        code = payload.get("code","")
        prompt = f"Baseado no código abaixo, sugira 3 testes unitários e explique o que cada teste valida.\n\n{code}"
        tests = await call_ai(provider, prompt)
        logger(f"{task_id} | {self.name}: Testes gerados.")
        return {"tests": tests}

class ReviewerAgent:
    name = "Reviewer"

    async def run(self, payload, logger, task_id, provider):
        logger(f"{task_id} | {self.name}: Fazendo revisão final do artefato.")
        code = payload.get("code","")
        tests = payload.get("tests","")
        prompt = f"Reveja o código e os testes e dê resumo de melhorias e riscos:\nCODE:\n{code}\nTESTS:\n{tests}"
        review = await call_ai(provider, prompt)
        logger(f"{task_id} | {self.name}: Review concluída.")
        return {"review": review}
