from fastapi import FastAPI
from api.state import router as state_router

app = FastAPI(
    title="MCP client",
)

app.include_router(state_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
