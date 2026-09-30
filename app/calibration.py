import numpy as np

class ConfidenceCalibrator:
    """Temperature scaling for evidence/decision confidence calibration."""
    def __init__(self,temperature=1.0): self.temperature=float(max(0.05,temperature))
    def fit(self,scores,labels,steps=200,learning_rate=0.05):
        x=np.asarray(scores,dtype=float); y=np.asarray(labels,dtype=float)
        if x.size==0 or x.size!=y.size: raise ValueError("scores and labels must be non-empty and equal length")
        p=np.clip(x,1e-6,1-1e-6); logits=np.log(p/(1-p)); log_t=0.0
        for _ in range(steps):
            scaled=logits/np.exp(log_t); probs=1/(1+np.exp(-scaled))
            grad=float(np.mean((probs-y)*(-scaled))); log_t-=learning_rate*grad
        self.temperature=float(np.exp(log_t)); return self
    def transform(self,score):
        p=float(np.clip(score,1e-6,1-1e-6)); logit=np.log(p/(1-p)); scaled=logit/self.temperature
        return float(1/(1+np.exp(-scaled)))
