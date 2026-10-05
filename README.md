# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Purpose.** A Streamlit number-guessing game. The player picks a difficulty, guesses the secret number within a limited number of attempts, gets a higher/lower hint after each guess, and earns or loses points.

**Bugs found.** The full reproduction log (input, expected, actual, console output, code location) is in `reflection.md`, section 1. In short:
- The hints were backwards: `check_guess` returned "Go HIGHER!" for a guess that was too high.
- On even-numbered attempts `app.py` turned the secret into a string, so guesses were compared alphabetically (`"9" > "42"`), which made the hints look random.
- Attempts were off by one: `attempts` started at 1, so the banner said 7 left on a fresh Normal game and the game ended after 7 guesses.
- Invalid input such as `abc` used up an attempt.
- New Game after a loss left the game stuck on "Game over", and it did not reset the score or history.
- The score rules paid points for some wrong guesses, and the banner always said "between 1 and 100" whatever the difficulty.

**Fixes applied.**
- Swapped the hint messages in `check_guess`, so a high guess says "Go LOWER!" and a low guess says "Go HIGHER!".
- Removed the `str(secret)` cast in `app.py`, so the secret is always compared as an integer. The string-compare fallback in `check_guess` is gone too.
- Moved `get_range_for_difficulty`, `parse_guess`, `check_guess` and `update_score` into `logic_utils.py` and imported them in `app.py`.
- Added pytest tests, including an `AppTest` regression test for the even-attempt bug.

**Not fixed yet:** the off-by-one attempts, invalid input costing an attempt, the New Game reset, the score rules and the hardcoded range banner.

## 📸 Demo Walkthrough

A sample game on Normal difficulty (range 1 to 100) with the secret set to 42. The secret is visible in "Developer Debug Info". Replayed against the fixed app.

1. The player enters **20**. The game shows "Go HIGHER!" and the score drops to -5.
2. The player enters **70**. The game shows "Go LOWER!" and the score drops to -10.
3. The player enters **41**, on an even-numbered attempt. The game shows "Go HIGHER!" (before the fix it said "Go LOWER!") and the score drops to -15.
4. The player enters **42**. The game shows "Correct!" and "You won! The secret was 42. Final score: 25", then balloons.
5. Any further guess shows "You already won. Start a new game to play again."

The final score of 25 comes from the scoring code as it still stands, which has the bugs listed above.

## 🧪 Test Results

Output of `python3 -m pytest tests/`. These are the starter tests plus my added regression tests, not the Challenge 1 edge-case tests.

```
collected 5 items

tests/test_game_logic.py .....                                           [100%]

============================== 5 passed in 0.28s ===============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
