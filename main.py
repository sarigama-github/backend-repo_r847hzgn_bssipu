import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Suspect, Case

app = FastAPI(title="Criminal DBMS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Criminal DBMS API running"}

# Generic search helper
class SearchQuery(BaseModel):
    collection: str
    query: Dict[str, Any] = {}
    limit: Optional[int] = 50

@app.post("/api/search")
def search_records(payload: SearchQuery):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    coll = payload.collection
    if coll not in ["suspect", "case"]:
        raise HTTPException(status_code=400, detail="Unsupported collection")
    docs = get_documents(coll, payload.query, payload.limit)
    # Convert ObjectId to string if present
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return {"count": len(docs), "items": docs}

# Create suspect
@app.post("/api/suspects")
def create_suspect(suspect: Suspect):
    try:
        new_id = create_document("suspect", suspect)
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create case
@app.post("/api/cases")
def create_case(case: Case):
    try:
        new_id = create_document("case", case)
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple reports
@app.get("/api/reports/overview")
def reports_overview(limit: int = Query(10, ge=1, le=200)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    suspects = get_documents("suspect", {}, limit)
    cases = get_documents("case", {}, limit)
    return {
        "suspects_sample": len(suspects),
        "cases_sample": len(cases),
        "recent_suspects": [{"_id": str(s.get("_id")), "full_name": s.get("full_name"), "risk_level": s.get("risk_level") } for s in suspects],
        "recent_cases": [{"_id": str(c.get("_id")), "title": c.get("title"), "status": c.get("status")} for c in cases]
    }

@app.get("/test")
def test_database():
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Connected",
        "database_url": None,
        "database_name": None,
        "collections": []
    }
    try:
        if db is not None:
            resp["database"] = "✅ Connected"
            try:
                resp["collections"] = db.list_collection_names()
            except Exception:
                pass
            resp["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            resp["database_name"] = db.name if hasattr(db, 'name') else None
    except Exception as e:
        resp["database"] = f"❌ Error: {str(e)[:80]}"
    return resp

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
