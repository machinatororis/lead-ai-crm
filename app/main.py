from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI(title="Lead AI CRM")


@app.get("/health")
async def health():
    return {"status": "ok"}


register_tortoise(
    app,
    db_url="postgres://postgres:postgres@localhost:5432/lead_ai_crm",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
