from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.scenarios import router as scenarios_router

app = FastAPI(title="Argos", description="Pixel Code Audit Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scenarios_router)


@app.get("/")
def root():
    return {"message": "Hello from Argos"}
