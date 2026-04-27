from app.classification import classify_terminal_state
from app.state_machine import CaseState


def test_classify_terminal_state_maps_invalid():
    assert classify_terminal_state(CaseState.INVALID) == "invalid"
