from .store import store

def recent_audit(limit=100):
    return store.audit(limit)
