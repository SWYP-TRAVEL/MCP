from fastapi import FastAPI
from api.create import router as create_router

app = FastAPI(
    title="MCP client",
)

app.include_router(create_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
