from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.router.routers import router
import dotenv
import os
from src.config.config import TMP_DIR

dotenv.load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# /tmp/エンドポイントを通じてtmpディレクトリの内容を提供
app.mount("/tmp", StaticFiles(directory=TMP_DIR), name="tmp")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)