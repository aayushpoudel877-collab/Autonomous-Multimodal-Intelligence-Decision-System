from .decision import make_decision
def run_agent(goal,context):
    d=make_decision(goal,context.get("signals",{}),context.get("evidence",[]))
    return {"goal":goal,"plan":["parse_goal","assess_evidence","human_review_gate"],"decision":d.model_dump(),"human_review_required":True}