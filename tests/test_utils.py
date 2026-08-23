from src.utils import decode_condition, probe_layout, realize_trial, summarize_trials


MATRICES = {
    "1": [
        {
            "pair_id": "p1_a",
            "option_a": "R",
            "option_b": "H",
            "word": ["READ", "HEAD"],
            "pseudoword": ["RABE", "HABE"],
            "illegal_string": ["RQXZ", "HQXZ"],
        },
        {
            "pair_id": "p1_b",
            "option_a": "N",
            "option_b": "C",
            "word": ["NAME", "CAME"],
            "pseudoword": ["NULE", "CULE"],
            "illegal_string": ["NKQZ", "CKQZ"],
        },
    ]
}


def test_decode_condition_preserves_three_scheduled_factors():
    spec = decode_condition("illegal_string_p4_b")
    assert (spec.context, spec.target_position, spec.displayed_variant) == ("illegal_string", 4, "b")


def test_realize_word_and_isolated_letter_share_target_position():
    word = realize_trial("word_p1_a", MATRICES, 0)
    isolated = realize_trial("isolated_letter_p1_a", MATRICES, 0)
    assert word.display_text == "READ"
    assert isolated.display_text == "R|||"
    assert word.target_letter == isolated.target_letter == "R"


def test_probe_sides_reverse_across_blocks():
    spec = realize_trial("word_p1_a", MATRICES, 0)
    first = probe_layout(spec, 0, "f", "j")
    second = probe_layout(spec, 1, "f", "j")
    assert first == {"left_letter": "R", "right_letter": "H", "correct_key": "f"}
    assert second == {"left_letter": "H", "right_letter": "R", "correct_key": "j"}


def test_summary_excludes_omissions_from_accuracy_denominator():
    summary = summarize_trials(
        [
            {"condition": "word_p1_a", "response": "f", "correct": True},
            {"condition": "word_p1_b", "response": "j", "correct": False},
            {"condition": "word_p2_a", "response": None, "correct": False},
        ]
    )
    assert summary == {"trial_count": 3, "answered_count": 2, "correct_count": 1, "accuracy": 0.5}
