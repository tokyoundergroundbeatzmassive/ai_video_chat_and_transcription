from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.router.routers import router
from dotenv import load_dotenv
from src.config.config import TMP_DIR
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/tmp", StaticFiles(directory=TMP_DIR), name="tmp")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)