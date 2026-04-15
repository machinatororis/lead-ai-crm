import pytest

from app.services.ai_service import analyze_lead, AIRecommendation


@pytest.mark.asyncio
async def test_analyze_lead_returns_transfer_to_sales_for_strong_lead():
    result = await analyze_lead(
        source="partner",
        stage="qualified",
        activity_count=8,
        business_domain="first",
    )

    assert result.score >= 0.7
    assert result.recommendation == AIRecommendation.TRANSFER_TO_SALES
    assert result.reason


@pytest.mark.asyncio
async def test_analyze_lead_caps_score_at_one():
    result = await analyze_lead(
        source="partner",
        stage="transferred",
        activity_count=100,
        business_domain="first",
    )

    assert result.score == 1.0


@pytest.mark.asyncio
async def test_analyze_lead_caps_score_without_business_domain():
    result = await analyze_lead(
        source="partner",
        stage="qualified",
        activity_count=100,
        business_domain=None,
    )

    assert result.score <= 0.55
    assert result.recommendation == AIRecommendation.CONTINUE_QUALIFICATION


@pytest.mark.asyncio
async def test_analyze_lead_returns_drop_lead_for_weak_lead():
    result = await analyze_lead(
        source="manual",
        stage="lost",
        activity_count=0,
        business_domain=None,
    )

    assert result.score <= 0.3
    assert result.recommendation == AIRecommendation.DROP_LEAD
    assert result.reason == "Низкая вероятность сделки"


@pytest.mark.asyncio
async def test_analyze_lead_returns_continue_qualification_for_middle_case():
    result = await analyze_lead(
        source="manual",
        stage="contacted",
        activity_count=2,
        business_domain="second",
    )

    assert 0.3 < result.score < 0.7
    assert result.recommendation == AIRecommendation.CONTINUE_QUALIFICATION
    assert result.reason == "Требуется дополнительная квалификация"
