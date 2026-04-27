from app.state_machine import CaseState


def classify_terminal_state(state: CaseState) -> str:
    return {
        CaseState.ACCEPTED: "accepted",
        CaseState.UNRESOLVED: "unresolved",
        CaseState.INVALID: "invalid",
        CaseState.TIMEOUT: "timeout",
        CaseState.SYSTEM_ERROR: "invalid",
    }[state]
