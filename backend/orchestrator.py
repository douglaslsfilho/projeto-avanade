from agents import PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent

agents_map = {
    "Planner": PlannerAgent(),
    "Coder": CoderAgent(),
    "Tester": TesterAgent(),
    "Reviewer": ReviewerAgent(),
}

async def run_project(project, logger):
    from copy import deepcopy
    task_id = str(project["_id"])
    steps_output = []

    # 1️⃣ Planner define os passos
    planner = agents_map["Planner"]
    provider = project["agents"][0]["model_provider"] if project.get("agents") else "OpenAI"
    steps = await planner.run(project["description"], logger, task_id, provider=provider)

    # 2️⃣ Para cada passo: Coder -> Tester -> Reviewer
    for step in steps:
        step_data = {"step": step}
        # Coder
        coder_provider = project["agents"][1]["model_provider"] if len(project.get("agents", [])) > 1 else "OpenAI"
        code_out = await agents_map["Coder"].run(step, logger, task_id, provider=coder_provider)
        step_data["coder"] = code_out

        # Tester
        tester_provider = project["agents"][2]["model_provider"] if len(project.get("agents", [])) > 2 else "OpenAI"
        test_out = await agents_map["Tester"].run(code_out, logger, task_id, provider=tester_provider)
        step_data["tester"] = test_out

        # Reviewer
        reviewer_provider = project["agents"][3]["model_provider"] if len(project.get("agents", [])) > 3 else "OpenAI"
        review_out = await agents_map["Reviewer"].run({**code_out, **test_out}, logger, task_id, provider=reviewer_provider)
        step_data["reviewer"] = review_out

        steps_output.append(step_data)

    return steps_output
