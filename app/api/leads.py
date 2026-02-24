from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist

from app.models import Lead
from app.schemas import LeadCreate, LeadOut, LeadUpdateStage

router = APIRouter(prefix="/leads", tags=["leads"])


# Правильный порядок стадий холодного лида
COLD_STAGES_ORDER = [
    "new",
    "contacted",
    "qualified",
    "transferred",
]

FINAL_STAGES = ["transferred", "lost"]


def lead_to_schema(lead: Lead) -> LeadOut:
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


def is_valid_stage_transition(current: str, new: str) -> bool:
    """
    Проверяем корректность перехода между стадиями.
    """

    # Если уже финальная стадия — менять нельзя
    if current in FINAL_STAGES:
        return False

    # Разрешаем переход в lost с любой не-финальной стадии
    if new == "lost":
        return True

    # Если новой стадии нет в порядке — запрещаем
    if new not in COLD_STAGES_ORDER:
        return False

    current_index = COLD_STAGES_ORDER.index(current)
    new_index = COLD_STAGES_ORDER.index(new)

    # Разрешаем только шаг вперёд на 1
    return new_index == current_index + 1


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead(payload: LeadCreate) -> LeadOut:
    lead = await Lead.create(
        source=payload.source,
        business_domain=payload.business_domain,
        stage="new",
        activity_count=0,
    )

    lead = await Lead.get(id=lead.id)
    return lead_to_schema(lead)


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int) -> LeadOut:
    try:
        lead = await Lead.get(id=lead_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead_to_schema(lead)


@router.patch("/{lead_id}/stage", response_model=LeadOut)
async def update_stage(lead_id: int, payload: LeadUpdateStage) -> LeadOut:
    try:
        lead = await Lead.get(id=lead_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Lead not found")

    if not is_valid_stage_transition(lead.stage, payload.stage):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage transition from '{lead.stage}' to '{payload.stage}'",
        )

    lead.stage = payload.stage
    await lead.save()

    return lead_to_schema(lead)
