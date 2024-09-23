from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def get_leaderboard():
    # 加载 HTML 文件
    with open("leaderboard.html") as f:
        return f.read()

if __name__ == "__main__":
    # 直接调用 uvicorn.run 方法
    uvicorn.run(app, host="0.0.0.0", port=8000)
