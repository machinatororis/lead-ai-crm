# app/api/leads.py
from fastapi import APIRouter, HTTPException

from app.models import Lead
from app.schemas import LeadCreate, LeadOut, LeadUpdateStage
from app.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


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


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead_endpoint(payload: LeadCreate) -> LeadOut:
    try:
        lead = await lead_service.create_lead(payload)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create lead")

    return lead_to_schema(lead)


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead_endpoint(lead_id: int) -> LeadOut:
    try:
        lead = await lead_service.get_lead(lead_id)
    except lead_service.LeadNotFoundError:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead_to_schema(lead)


@router.patch("/{lead_id}/stage", response_model=LeadOut)
async def update_stage_endpoint(lead_id: int, payload: LeadUpdateStage) -> LeadOut:
    try:
        lead = await lead_service.update_stage(lead_id, payload)
    except lead_service.LeadNotFoundError:
        raise HTTPException(status_code=404, detail="Lead not found")
    except lead_service.InvalidStageTransitionError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage transition from '{exc.current}' to '{exc.new}'",
        )

    return lead_to_schema(lead)


@router.post("/{lead_id}/analyze", response_model=LeadOut)
async def analyze_lead_endpoint(lead_id: int) -> LeadOut:
    try:
        lead = await lead_service.analyze_lead_and_save(lead_id)
    except lead_service.LeadNotFoundError:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead_to_schema(lead)
