from .schemas import Decision
def make_decision(question,signals,evidence):
    risks=[f"Negative signal detected for {k}." for k,v in signals.items() if isinstance(v,(int,float)) and v<0]
    reasoning=[f"Question: {question}"]+[f"Signal {k}={v} was included." for k,v in signals.items()]
    if risks:r="Investigate flagged signals before irreversible action.";c=.68
    elif evidence:r="Proceed with a monitored action supported by the supplied evidence.";c=.74
    else:r="Collect additional evidence before a high-impact decision.";c=.52
    return Decision(recommendation=r,confidence=c,evidence=evidence,reasoning=reasoning,risks=risks or ["Advisory output; human review required."])