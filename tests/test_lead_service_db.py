import pytest
import pytest_asyncio
from tortoise import Tortoise

from app.models import Lead, Sale
from app.schemas import LeadCreate, LeadUpdateStage
from app.services.lead_service import (
    CannotTransferToSalesError,
    InvalidStageTransitionError,
    analyze_lead_and_save,
    create_lead,
    update_stage,
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_create_lead_sets_default_values():
    payload = LeadCreate(source="scanner", business_domain="first")

    lead = await create_lead(payload)

    assert lead.id is not None
    assert lead.source == "scanner"
    assert lead.business_domain == "first"
    assert lead.stage == "new"
    assert lead.activity_count == 0
    assert lead.ai_score is None


@pytest.mark.asyncio
async def test_update_stage_successfully_moves_to_next_stage():
    lead = await Lead.create(
        source="scanner",
        business_domain="first",
        stage="new",
        activity_count=0,
    )

    updated = await update_stage(lead.id, LeadUpdateStage(stage="contacted"))

    assert updated.stage == "contacted"


@pytest.mark.asyncio
async def test_update_stage_raises_for_skipped_stage():
    lead = await Lead.create(
        source="scanner",
        business_domain="first",
        stage="new",
        activity_count=0,
    )

    with pytest.raises(InvalidStageTransitionError):
        await update_stage(lead.id, LeadUpdateStage(stage="qualified"))


@pytest.mark.asyncio
async def test_update_stage_creates_sale_on_successful_transfer():
    lead = await Lead.create(
        source="partner",
        business_domain="first",
        stage="qualified",
        activity_count=5,
        ai_score=0.8,
    )

    updated = await update_stage(lead.id, LeadUpdateStage(stage="transferred"))

    sale = await Sale.get(lead_id=lead.id)

    assert updated.stage == "transferred"
    assert sale is not None
    assert sale.stage == "new"


@pytest.mark.asyncio
async def test_update_stage_blocks_transfer_when_ai_score_too_low():
    lead = await Lead.create(
        source="partner",
        business_domain="first",
        stage="qualified",
        activity_count=5,
        ai_score=0.4,
    )

    with pytest.raises(CannotTransferToSalesError):
        await update_stage(lead.id, LeadUpdateStage(stage="transferred"))

    sales_count = await Sale.all().count()
    assert sales_count == 0


@pytest.mark.asyncio
async def test_update_stage_blocks_transfer_without_business_domain():
    lead = await Lead.create(
        source="partner",
        business_domain=None,
        stage="qualified",
        activity_count=5,
        ai_score=0.9,
    )

    with pytest.raises(CannotTransferToSalesError):
        await update_stage(lead.id, LeadUpdateStage(stage="transferred"))

    sales_count = await Sale.all().count()
    assert sales_count == 0


@pytest.mark.asyncio
async def test_analyze_lead_and_save_updates_ai_fields():
    lead = await Lead.create(
        source="partner",
        business_domain="first",
        stage="qualified",
        activity_count=8,
    )

    updated = await analyze_lead_and_save(lead.id)

    assert updated.ai_score is not None
    assert updated.ai_recommendation is not None
    assert updated.ai_reason is not None

    saved = await Lead.get(id=lead.id)
    assert saved.ai_score == updated.ai_score
    assert saved.ai_recommendation == updated.ai_recommendation
    assert saved.ai_reason == updated.ai_reason
