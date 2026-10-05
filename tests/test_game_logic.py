from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result, _ = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result, _ = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result, _ = check_guess(40, 50)
    assert result == "Too Low"

def test_hint_message_points_toward_secret():
    # Guess above the secret must say go lower; guess below must say go higher
    assert "LOWER" in check_guess(60, 50)[1]
    assert "HIGHER" in check_guess(40, 50)[1]

def test_app_compares_numbers_on_even_attempts():
    # Regression: app.py used to cast the secret to str on even attempts, so "41" < "42" was judged as text
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(Path(__file__).parent.parent / "app.py")).run()
    at.session_state["secret"] = 42
    at.session_state["attempts"] = 3  # the next guess is attempt 4 (even)
    at.text_input(key="guess_input_Normal").set_value("41")
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Go HIGHER!"]  # 41 is below 42
