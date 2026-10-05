# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The game opened as a simple Streamlit page titled "Game Glitch Investigator" with the caption "An AI-generated guessing game. Something is off." A sidebar let me pick Easy, Normal or Hard, and the main area had a "Developer Debug Info" expander, a text box, and Submit / New Game buttons with a "Show hint" checkbox. On a fresh Normal game the banner already said "Attempts left: 7" even though the sidebar allowed 8. The app never crashed, so every bug showed up as wrong behavior, not an error message.

The most obvious bug was that the hints were backwards: with the secret at 42, guessing 50 told me "Go HIGHER!" and guessing 30 told me "Go LOWER!". The second was that on even-numbered attempts the hints looked random, because app.py turned the secret into a string and compared the numbers alphabetically ("9" counted as bigger than "42"). I also found that New Game stayed stuck on "Game over" after a loss, and that a bad guess like "abc" used up an attempt.

**Bug Reproduction Logs**

Setup for every row: run `python3 -m streamlit run app.py`, open "Developer Debug Info" to read the secret, and use Normal difficulty unless stated. Rows 1-6 were reproduced with secret = 42.

| # | Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|------------|-------------------|-----------------|------------------------|-------------------------|
| 1 | First guess `50`, then `30` (attempts 2 and 3) | `50` gives "Go LOWER!" and `30` gives "Go HIGHER!" | `50` gives "Go HIGHER!" and `30` gives "Go LOWER!". Hints point the wrong way on odd attempts. | none | app.py, `check_guess()`, lines 37-40 (the "Too High" and "Too Low" messages are swapped) |
| 2 | Guess `9`, then `41`, each on an even attempt (4) | Both are below 42, so both should give "Go HIGHER!" | `9` is judged "Too High" (`"9" > "42"`). `41` is judged "Too Low" but shows "Go LOWER!". Hints look random. | none | app.py lines 158-161 (secret cast with `str()` on even attempts), which sends `check_guess()` into its string-comparison `except TypeError` branch, lines 41-47 |
| 3 | Fresh Normal game, then guess wrong numbers until the game ends | 8 attempts, with "Attempts left" starting at 8 | Banner starts at "Attempts left: 7". The game ends after 7 guesses. The banner and Debug Info lag one guess behind. | none | app.py line 96 (`attempts` starts at 1), line 148 (incremented before processing), lines 109-119 (banner and debug drawn before the submit logic at line 147) |
| 4 | Guess `abc`, then submit an empty box | "That is not a number." / "Enter a guess." and no attempt used | The message shows, but each bad guess costs an attempt and is added to the history. | none | app.py line 148 (`attempts += 1` before `parse_guess()` at line 150) and line 153 (bad input appended to history) |
| 5 | Lose a game (7 wrong guesses), then click "New Game 🔁" | A fresh game: playing state, score 0, empty history, new secret | Still shows "Game over. Start a new game to try again." Score (-25) and history carry over. | none | app.py `new_game` block, lines 134-138 (does not reset `status`, `score` or `history`; `st.stop()` at line 145 then blocks play) |
| 6 | Wrong guesses on even attempts (`10`, `90`, `41`), then a win on attempt 7 | Wrong guesses never gain points. A win on attempt 7 pays 30. | Score went up by 5 on some wrong guesses. The attempt-7 win paid 20. | none | app.py, `update_score()`, lines 50-65 (+5 for "Too High" on even attempts at lines 58-59; `attempt_number + 1` at line 52) |
| 7 | Switch to Easy or Hard and read the "Guess a number between..." banner | Banner shows 1-20 (Easy) or 1-50 (Hard) | Banner always says "between 1 and 100". (Secret not re-rolling on a difficulty change is from reading the code, not observed.) | none | app.py line 110 (hardcoded text) and lines 92-93 (secret rolled once) |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

**Tool used:** Claude

**Correct suggestion: always compare numbers, never a string secret.**
- *What it suggested:* delete the `str(st.session_state.secret)` branch on even attempts in app.py (the old lines 158-161) and always pass the int secret to `check_guess`. It also dropped the `except TypeError` string fallback, since that fallback only existed to handle the mismatch.
- *Why it was correct:* on even attempts the secret became `"42"`, so `check_guess` fell into the string branch and compared text, where `"9" > "42"`. That is why hints looked random on even attempts. With ints on both sides the comparison is numeric, and the hint messages were swapped separately in `check_guess`.
- *How I verified:* I traced `9` vs `"42"` by hand, then replayed the game with secret 42. Guess `41` on an even attempt now says "Go HIGHER!" (it said "Go LOWER!" before), and `50` says "Go LOWER!".

**Suggestion not accepted as written: the unit test for the string bug.**
- *What it suggested:* a test named `test_numeric_comparison_not_alphabetical` that asserted `check_guess(9, 42)` returns "Too Low".
- *Why I changed it:* it was a poor fit. The string cast lived in app.py, not in `check_guess`, so the test also passed on the original code and protected nothing.
- *How I verified and what I did instead:* I ran its assertion against the original `check_guess` from git, and it passed. I replaced it with `test_app_compares_numbers_on_even_attempts`, which drives the real app using Streamlit's `AppTest`, forces an even attempt with secret 42, and guesses `41`. It fails against the original app.py and passes now.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

**Bugs fixed so far:** (1) swapped high/low hint messages in `check_guess`, (2) the secret turning into a string on even attempts. The logic was also moved from app.py into logic_utils.py. The other bugs in the Bug Reproduction Logs are not fixed yet.

**How I decided they were fixed**
- I replayed the game with the secret pinned to 42 (read from Developer Debug Info). Every hint now matches the real direction on both odd and even attempts, including `50` ("Go LOWER!"), `30` ("Go HIGHER!"), `41` ("Go HIGHER!") and `99` ("Go LOWER!").
- I ran the new hint test against the original buggy `check_guess` from git and confirmed it fails there. I ran the app-level regression test against the original app.py and confirmed it fails there too, with "Go LOWER!" for `41`.

**Tests run** (`python3 -m pytest -v`, 5 passed)
- Starter tests `test_winning_guess`, `test_guess_too_high` and `test_guess_too_low`. These checked only the outcome string, so they never caught the swapped messages. They also expected a bare string, but `check_guess` returns `(outcome, message)`, so I changed them to unpack the tuple.
- `test_hint_message_points_toward_secret` checks 60 vs 50 says "LOWER" and 40 vs 50 says "HIGHER".
- `test_app_compares_numbers_on_even_attempts` is the regression test for the string cast, described in section 2.

**AI's role in testing:** Claude Code explained why the hints were random (two bugs overlapping: the swapped messages plus the string comparison) and wrote the tests. My first draft of the regression test used guess `9`, which passed on the old app by accident because the two bugs cancelled out. Running the test against the old code caught that, and I switched to `41`.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Every time you click a button or type in a box, Streamlit runs the whole app.py script again from top to bottom, so ordinary variables are rebuilt from scratch on each click. `st.session_state` is a dictionary that survives those reruns, so it is where the game keeps the secret, attempts, score, status and history. That is why app.py wraps each one in `if "secret" not in st.session_state:`, which sets it only the first time. The README warned that the secret might change on every Submit, but I never saw that: it is guarded correctly, and the secret stayed the same across guesses in my tests. Reruns did cause a different problem. The "Attempts left" banner and the Debug Info panel are drawn near the top of the script, before the Submit code runs, so they show the state from before the guess and lag one guess behind.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

**Habit to reuse:** run every new test against the original buggy code to confirm it fails, before trusting that it passes on the fix. This caught two weak tests of mine. One assertion passed on the old code because the bug was in app.py and not in `check_guess`. My first regression test used guess `9`, which passed by accident because two bugs cancelled each other out. Pinning the secret to a known value (42) also made the bugs reproducible.

**Do differently next time:** settle the interface before the AI starts moving code. The starter tests expected `check_guess` to return a bare string, while the stub docstring and app.py use `(outcome, message)`, and I only found the mismatch after the refactor. Next time I would ask the AI to write the failing test first, and I would state the return contract in the prompt.

**How my view changed:** AI-generated code can look tidy and still be wrong in ways that cancel each other out, so a hint that is right on one guess proves little. I now treat its code and its tests as drafts that I have to check by running them, not as answers.
