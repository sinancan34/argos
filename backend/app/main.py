from fastapi import FastAPI

app = FastAPI(title="Argos", description="GA4 Audit Tool")


@app.get("/")
def root():
    return {"message": "Hello from Argos"}
