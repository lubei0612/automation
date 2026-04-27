from enum import Enum
from typing import Dict, Set


class CaseState(str, Enum):
    DISCOVERED = "DISCOVERED"
    EXTRACTED = "EXTRACTED"
    PREFLIGHT_PASSED = "PREFLIGHT_PASSED"
    BASELINE_VERIFIED = "BASELINE_VERIFIED"
    AGENT_RUNNING = "AGENT_RUNNING"
    PATCH_VERIFIED = "PATCH_VERIFIED"
    ARTIFACTS_BUILT = "ARTIFACTS_BUILT"
    ACCEPTED = "ACCEPTED"
    INVALID = "INVALID"
    UNRESOLVED = "UNRESOLVED"
    TIMEOUT = "TIMEOUT"
    SYSTEM_ERROR = "SYSTEM_ERROR"


_ALLOWED_TRANSITIONS: Dict[CaseState, Set[CaseState]] = {
    CaseState.DISCOVERED: {
        CaseState.EXTRACTED,
        CaseState.INVALID,
        CaseState.TIMEOUT,
        CaseState.SYSTEM_ERROR,
    },
    CaseState.EXTRACTED: {
        CaseState.PREFLIGHT_PASSED,
        CaseState.INVALID,
        CaseState.TIMEOUT,
        CaseState.SYSTEM_ERROR,
    },
    CaseState.PREFLIGHT_PASSED: {
        CaseState.BASELINE_VERIFIED,
        CaseState.INVALID,
        CaseState.TIMEOUT,
        CaseState.SYSTEM_ERROR,
    },
}


def transition(current: CaseState, target: CaseState) -> CaseState:
    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"invalid transition: {current} -> {target}")
    return target
