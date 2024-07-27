from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from database import Base, engine
from controllers import router
from contextlib import asynccontextmanager


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행될 로직
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 애플리케이션 종료 시 실행될 로직 (필요한 경우)

# FastAPI 애플리케이션을 초기화합니다.
# Swagger UI와 Redoc 도 비활성화합니다.
app = FastAPI(lifespan=app_lifespan, docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.include_router(router)
templates = Jinja2Templates(directory="templates")

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})

    