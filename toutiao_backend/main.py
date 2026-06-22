from fastapi import FastAPI, APIRouter, Path, Query
import uvicorn
from routers import ai, favorite, history, news, users
from fastapi.middleware.cors import CORSMiddleware
from untils.exception_handlers import register_exception_handlers
from crud.ai import init_ai_tables


app = FastAPI()

# 配置 CORS 中间件，允许所有来源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证（如 cookies）
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
    expose_headers=["X-Session-Id"],
)

#异常处理
register_exception_handlers(app)



@app.get("/")
async def root():
    return {"msg": "Hello World"}


@app.on_event("startup")
async def startup():
    await init_ai_tables()


#挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
