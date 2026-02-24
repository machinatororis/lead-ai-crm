from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

import os
from dotenv import load_dotenv

from app.api.leads import router as leads_router

# Подгружаем переменные окружения из .env (если файл есть)
load_dotenv()

app = FastAPI(title="Lead AI CRM")

app.include_router(leads_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Берём строку подключения из переменной окружения
DB_URL = os.getenv(
    "DB_URL",
    # дефолт - на случай локального запуска без .env или без docker-compose
    "postgres://postgres:postgres@localhost:5432/lead_ai_crm",
)

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
