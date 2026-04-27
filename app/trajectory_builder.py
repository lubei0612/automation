from typing import Dict, List

from app.trajectory import count_turns


def build_trajectory_record(
    *,
    instance_id: str,
    instruction: str,
    instance: Dict,
    metadata: Dict,
    trajectory: List[Dict],
) -> Dict:
    return {
        "instance_id": instance_id,
        "instruction": instruction,
        "instance": instance,
        "metadata": metadata,
        "trajectory": trajectory,
        "metrics": {
            "turn_count": count_turns(trajectory),
        },
    }
