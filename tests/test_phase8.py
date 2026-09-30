from app.calibration import ConfidenceCalibrator
from app.evaluation import ndcg_at_k,recall_at_k,reciprocal_rank
from app.evidence_fusion import fuse_evidence
from app.schemas import Source

def test_retrieval_metrics():
    a=Source(id="a",title="A",content="a",metadata={}); b=Source(id="b",title="B",content="b",metadata={})
    results=[{"source":b},{"source":a}]
    assert recall_at_k(results,["a"],2)==1.0
    assert reciprocal_rank(results,{"a"})==0.5
    assert ndcg_at_k(results,["a"],2)>0

def test_cross_modal_fusion():
    s=Source(id="x",title="x",content="x",metadata={"modality":"document"})
    fused=fuse_evidence([{"source":s,"score":0.7},{"source":s,"score":0.6}])
    assert fused[0]["score"]>0.7 and fused[0]["modalities"]==["document"]

def test_calibrator():
    c=ConfidenceCalibrator().fit([0.9,0.8,0.2,0.1],[1,1,0,0])
    assert 0.0<c.transform(0.9)<1.0
