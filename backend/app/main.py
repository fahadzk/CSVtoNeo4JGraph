from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router

app = FastAPI(title="CSV to Neo4j Graph")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:5174"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
