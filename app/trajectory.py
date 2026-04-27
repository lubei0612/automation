from typing import Dict, List


def count_turns(messages: List[Dict]) -> int:
    return sum(1 for message in messages if message.get("role") == "assistant")
