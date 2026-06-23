from fastapi import FastAPI, HTTPException

from .models import ResearchRequest, ResearchResponse
from .pipeline import ResearchScout

app = FastAPI(title="Research Scout", version="0.1.0")


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    try:
        return await ResearchScout().research(request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "ok"}

