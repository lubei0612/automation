import pytest

from app.state_machine import CaseState, transition


def test_transition_accepts_valid_progression():
    assert transition(CaseState.DISCOVERED, CaseState.EXTRACTED) is CaseState.EXTRACTED


def test_transition_rejects_invalid_jump():
    with pytest.raises(ValueError):
        transition(CaseState.DISCOVERED, CaseState.ACCEPTED)
