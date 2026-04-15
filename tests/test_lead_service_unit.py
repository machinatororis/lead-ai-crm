from types import SimpleNamespace

from app.services.lead_service import (
    can_transfer_to_sales,
    is_valid_stage_transition,
)


def test_valid_stage_transition_new_to_contacted():
    assert is_valid_stage_transition("new", "contacted") is True


def test_valid_stage_transition_contacted_to_qualified():
    assert is_valid_stage_transition("contacted", "qualified") is True


def test_valid_stage_transition_qualified_to_transferred():
    assert is_valid_stage_transition("qualified", "transferred") is True


def test_invalid_stage_transition_cannot_skip_stage():
    assert is_valid_stage_transition("new", "qualified") is False


def test_invalid_stage_transition_from_final_stage():
    assert is_valid_stage_transition("transferred", "contacted") is False
    assert is_valid_stage_transition("lost", "new") is False


def test_transition_to_lost_from_non_final_stage_is_allowed():
    assert is_valid_stage_transition("new", "lost") is True
    assert is_valid_stage_transition("contacted", "lost") is True
    assert is_valid_stage_transition("qualified", "lost") is True


def test_invalid_stage_transition_unknown_target_stage():
    assert is_valid_stage_transition("new", "kyc") is False


def test_can_transfer_to_sales_when_score_is_equal_to_threshold():
    lead = SimpleNamespace(
        business_domain="first",
        ai_score=0.6,
    )

    assert can_transfer_to_sales(lead) is True


def test_can_transfer_to_sales_when_score_is_above_threshold():
    lead = SimpleNamespace(
        business_domain="second",
        ai_score=0.85,
    )

    assert can_transfer_to_sales(lead) is True


def test_cannot_transfer_to_sales_without_business_domain():
    lead = SimpleNamespace(
        business_domain=None,
        ai_score=0.9,
    )

    assert can_transfer_to_sales(lead) is False


def test_cannot_transfer_to_sales_without_ai_score():
    lead = SimpleNamespace(
        business_domain="third",
        ai_score=None,
    )

    assert can_transfer_to_sales(lead) is False


def test_cannot_transfer_to_sales_below_threshold():
    lead = SimpleNamespace(
        business_domain="first",
        ai_score=0.59,
    )

    assert can_transfer_to_sales(lead) is False
