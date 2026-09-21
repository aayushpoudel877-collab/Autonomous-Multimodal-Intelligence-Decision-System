import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
def detect_anomalies(values,contamination=.05):
    if len(values)<5:raise ValueError("At least 5 observations are required.")
    x=np.asarray(values,float).reshape(-1,1);m=IsolationForest(contamination=contamination,random_state=42);lab=m.fit_predict(x);score=-m.decision_function(x)
    return {"labels":lab.tolist(),"scores":np.round(score,5).tolist(),"anomaly_indices":np.where(lab==-1)[0].tolist()}
def forecast(values,horizon=5):
    if len(values)<3:raise ValueError("At least 3 observations are required.")
    y=np.asarray(values,float);x=np.arange(len(y)).reshape(-1,1);m=LinearRegression().fit(x,y);fx=np.arange(len(y),len(y)+horizon).reshape(-1,1)
    return {"forecast":np.round(m.predict(fx),4).tolist(),"slope":float(m.coef_[0]),"intercept":float(m.intercept_)}