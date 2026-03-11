from fastapi import FastAPI

from app.routers.scenarios import router as scenarios_router

app = FastAPI(title="Argos", description="GA4 Audit Tool")
app.include_router(scenarios_router)


@app.get("/")
def root():
    return {"message": "Hello from Argos"}
