from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist

from app.models import Lead
from app.schemas import LeadCreate, LeadOut

router = APIRouter(prefix="/leads", tags=["leads"])


def lead_to_schema(lead: Lead) -> LeadOut:
    """
    Явно преобразуем ORM-модель Tortoise в Pydantic-схему.
    """
    return LeadOut(
        id=lead.id,
        source=lead.source,
        stage=lead.stage,
        business_domain=lead.business_domain,
        activity_count=lead.activity_count,
        ai_score=lead.ai_score,
        ai_recommendation=lead.ai_recommendation,
        ai_reason=lead.ai_reason,
        created_at=lead.created_at,
    )


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead(payload: LeadCreate) -> LeadOut:
    """
    Создание лида.
    Менеджер передаёт source и (опционально) business_domain.
    Остальное заполняем по умолчанию.
    """
    # Создаём лида
    lead = await Lead.create(
        source=payload.source,
        business_domain=payload.business_domain,
        stage="new",
        activity_count=0,
    )

    # На всякий случай перечитаем его из БД, чтобы created_at и др. поля точно были заполнены
    lead = await Lead.get(id=lead.id)

    return lead_to_schema(lead)


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int) -> LeadOut:
    """
    Получить одного лида по id.
    """
    try:
        lead = await Lead.get(id=lead_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead_to_schema(lead)
