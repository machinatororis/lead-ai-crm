# app/services/ai_service.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AIRecommendation(str, Enum):
    TRANSFER_TO_SALES = "transfer_to_sales"
    CONTINUE_QUALIFICATION = "continue_qualification"
    DROP_LEAD = "drop_lead"


@dataclass
class LeadAIResult:
    score: float
    recommendation: AIRecommendation
    reason: str


async def analyze_lead(
    source: str,
    stage: str,
    activity_count: int,
    business_domain: Optional[str],
) -> LeadAIResult:

    # Базовый скор по источнику
    source_score = {
        "scanner": 0.5,
        "partner": 0.7,
        "manual": 0.4,
    }

    score = source_score.get(source, 0.3)

    # Активность
    if activity_count == 0:
        score -= 0.2
    elif activity_count < 3:
        score += 0.05
    elif activity_count < 7:
        score += 0.15
    else:
        score += 0.25

    # Стадия
    stage_bonus = {
        "new": 0.0,
        "contacted": 0.05,
        "qualified": 0.15,
        "transferred": 0.2,
        "lost": -0.4,
    }

    score += stage_bonus.get(stage, 0.0)

    # Бизнес-домен обязателен для высокого скора
    if business_domain:
        score += 0.1
    else:
        score = min(score, 0.55)

    # Нормализация
    score = max(0.0, min(1.0, score))

    # Рекомендация
    if score >= 0.7 and business_domain:
        recommendation = AIRecommendation.TRANSFER_TO_SALES
        reason = "Высокая вероятность сделки, рекомендовано передать в продажи"
    elif score <= 0.3:
        recommendation = AIRecommendation.DROP_LEAD
        reason = "Низкая вероятность сделки"
    else:
        recommendation = AIRecommendation.CONTINUE_QUALIFICATION
        reason = "Требуется дополнительная квалификация"

    return LeadAIResult(score=score, recommendation=recommendation, reason=reason)
