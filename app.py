import random
import streamlit as st

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
    if raw is None or raw.strip() == "":
        return False, None, "Are you even trying to guess at all?"

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "This is a NUMBER game. Kudos for burning a free attempt!"
    return True, value, None

def check_bounds(guess, low, high):
    """Check if guess is within valid bounds. If out of bounds, return the direction hint."""
    if guess < low or guess > high:
        # Still provide direction hint even when out of bounds
        if guess > high:
            return False, "Out of Bounds! 📉 Go LOWER!"
        else:  # guess < low
            return False, "Out of Bounds! 📈 Go HIGHER!"
    return True, None

def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "� Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 5,
    "Normal": 6,
    "Hard": 8,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# ensure the secret always lives within the current low/high bounds
# whenever the range (difficulty) changes we regenerate the secret and reset the game
current_range = (low, high)
if (
    "secret" not in st.session_state
    or st.session_state.get("last_range") != current_range
):
    st.session_state.secret = random.randint(low, high)
    st.session_state.last_range = current_range
    # Reset game state when difficulty changes
    st.session_state.attempts = 0
    st.session_state.status = "playing"
    st.session_state.score = 0
    st.session_state.history = []

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

if st.session_state.status == "playing":
    with st.form("guess_form", clear_on_submit=True):
        raw_guess = st.text_input("Enter your guess:")
        show_hint = st.checkbox("Show hint", value=True)
        submit = st.form_submit_button("Submit Guess 🚀")

try:
    if submit:
        st.session_state.attempts += 1

        ok, guess_int, err = parse_guess(raw_guess)

        if not ok:
            st.session_state.history.append(raw_guess)
            st.error(err)
        else:
            st.session_state.history.append(guess_int)

            # Check if guess is within bounds
            in_bounds, bounds_message = check_bounds(guess_int, low, high)
            
            if not in_bounds:
                st.error(bounds_message)
            else:
                secret = st.session_state.secret

                outcome, message = check_guess(guess_int, secret)

                if show_hint:
                    st.warning(message)

                st.session_state.score = update_score(
                    current_score=st.session_state.score,
                    outcome=outcome,
                    attempt_number=st.session_state.attempts,
                )

                if outcome == "Win":
                    st.balloons()
                    st.session_state.status = "won"
                    st.success(
                        f"You won! The secret was {st.session_state.secret}. "
                        f"Final score: {st.session_state.score}"
                    )
                else:
                    if st.session_state.attempts >= attempt_limit:
                        st.session_state.status = "lost"
                        st.error(
                            f"Out of attempts! "
                            f"The secret was {st.session_state.secret}. "
                            f"Score: {st.session_state.score}"
                        )
except NameError:
    pass

if st.session_state.status == "playing":
    st.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )

if st.session_state.status == "lost":
    st.error("Game over. Start a new game to try again.")

new_game = st.button("New Game 🔁")

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.last_range = (low, high)
    st.session_state.status = "playing"
    st.session_state.score = 0
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
