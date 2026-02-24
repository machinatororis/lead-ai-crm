# app/services/lead_service.py

from tortoise.exceptions import DoesNotExist

from app.models import Lead, Sale
from app.schemas import LeadCreate, LeadUpdateStage
from app.services.ai_service import analyze_lead, LeadAIResult

# Порядок стадий и финальные стадии - бизнес-правило, а не API
COLD_STAGES_ORDER = ["new", "contacted", "qualified", "transferred"]
FINAL_STAGES = ["transferred", "lost"]


class LeadNotFoundError(Exception):
    pass


class InvalidStageTransitionError(Exception):
    def __init__(self, current: str, new: str):
        self.current = current
        self.new = new
        super().__init__(f"Invalid stage transition from '{current}' to '{new}'")


class CannotTransferToSalesError(Exception):
    """
    Лид не удовлетворяет условиям передачи в продажи:
    - ai_score < 0.6 или
    - не указан business_domain
    """

    pass


def is_valid_stage_transition(current: str, new: str) -> bool:
    """
    Бизнес-логика переходов между стадиями лида.
    """

    # Если уже финальная стадия - менять нельзя
    if current in FINAL_STAGES:
        return False

    # Разрешаем переход в lost с любой не-финальной стадии
    if new == "lost":
        return True

    # Если новой стадии нет в порядке - запрещаем
    if new not in COLD_STAGES_ORDER:
        return False

    current_index = COLD_STAGES_ORDER.index(current)
    new_index = COLD_STAGES_ORDER.index(new)

    # Разрешаем только шаг вперёд на 1
    return new_index == current_index + 1


def can_transfer_to_sales(lead: Lead) -> bool:
    """
    Условия ТЗ:
    - AI-оценка ≥ 0.6
    - указан бизнес-домен
    """
    return (
        lead.business_domain is not None
        and lead.ai_score is not None
        and lead.ai_score >= 0.6
    )


async def get_lead(lead_id: int) -> Lead:
    try:
        return await Lead.get(id=lead_id)
    except DoesNotExist:
        raise LeadNotFoundError()


async def create_lead(payload: LeadCreate) -> Lead:
    lead = await Lead.create(
        source=payload.source,
        business_domain=payload.business_domain,
        stage="new",
        activity_count=0,
    )
    # Перечитываем, чтобы были заполнены все поля (created_at и т.п.)
    return await Lead.get(id=lead.id)


async def update_stage(lead_id: int, payload: LeadUpdateStage) -> Lead:
    lead = await get_lead(lead_id)
    new_stage = payload.stage

    if not is_valid_stage_transition(lead.stage, new_stage):
        raise InvalidStageTransitionError(lead.stage, new_stage)

    # Если переводим в продажи - проверяем условия ТЗ и создаём Sale
    if new_stage == "transferred":
        if not can_transfer_to_sales(lead):
            # Не удовлетворяет условиям передачи
            raise CannotTransferToSalesError()

        # Условия выполнены - создаём продажу.
        # Модель Sale - OneToOne к Lead, поэтому дубли не ожидаются:
        await Sale.create(lead=lead)

    lead.stage = new_stage
    await lead.save()
    return lead


async def analyze_lead_and_save(lead_id: int) -> Lead:
    """
    Бизнес-операция: взять лида, отправить в AI, сохранить результат.
    """
    lead = await get_lead(lead_id)

    result: LeadAIResult = await analyze_lead(
        source=lead.source,
        stage=lead.stage,
        activity_count=lead.activity_count,
        business_domain=lead.business_domain,
    )

    lead.ai_score = result.score
    lead.ai_recommendation = result.recommendation.value
    lead.ai_reason = result.reason
    await lead.save()

    return lead
