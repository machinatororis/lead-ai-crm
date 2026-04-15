from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

import os
from dotenv import load_dotenv

from app.api.leads import router as leads_router

load_dotenv()

app = FastAPI(title="Lead AI CRM")

app.include_router(leads_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise RuntimeError(
        "DB_URL environment variable is not set. Create a .env file or provide DB_URL in the environment."
    )


register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
