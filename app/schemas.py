from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field

# ----- Лиды -----

LeadSource = Literal["scanner", "partner", "manual"]
LeadStage = Literal["new", "contacted", "qualified", "transferred", "lost"]
BusinessDomain = Literal["first", "second", "third"]


class LeadCreate(BaseModel):
    """
    То, что менеджер передаёт при создании лида.
    """

    source: LeadSource = Field(..., description="Источник лида")
    business_domain: Optional[BusinessDomain] = Field(
        None,
        description="Бизнес-домен, если известен",
    )


class LeadUpdateStage(BaseModel):
    """
    Запрос на обновление этапа лида.
    """

    stage: LeadStage


class LeadOut(BaseModel):
    """
    Ответ API с полной информацией о лиде.
    """

    id: int
    source: LeadSource
    stage: LeadStage
    business_domain: Optional[BusinessDomain]

    activity_count: int
    ai_score: Optional[float]
    ai_recommendation: Optional[str]
    ai_reason: Optional[str]

    created_at: datetime
