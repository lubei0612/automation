from app.trajectory import count_turns


def test_count_turns_counts_user_assistant_pairs():
    messages = [
        {"role": "user"},
        {"role": "assistant"},
        {"role": "user"},
        {"role": "assistant"},
    ]

    assert count_turns(messages) == 2
