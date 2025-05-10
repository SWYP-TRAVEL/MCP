from fastapi import FastAPI
from api.api import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="MCP client",
)

app.include_router(router=router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
