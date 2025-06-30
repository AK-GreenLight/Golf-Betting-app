import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Golf Side Bet Odds", layout="centered")
st.title("🏌️ Closest to the Pin Odds Generator (v2)")

st.write("Answer 3 simple questions for each player. We'll simulate 10,000 shots and generate betting odds for a closest-to-the-pin contest.")

num_players = st.number_input("How many players?", min_value=2, max_value=6, value=4)
players = {}

for i in range(num_players):
    st.markdown("---")
    name = st.text_input(f"Player {i+1} Name", value=f"Player {i+1}")
    skill = st.selectbox(f"{name}'s Skill Level", ["Scratch", "Single-Digit", "Bogey Golfer", "High Handicap"], key=f"skill_{i}")
    drive_dist = st.slider(f"{name}'s Avg Driving Distance (yards)", 200, 320, 250, key=f"drive_{i}")
    rounds_played = st.slider(f"How many rounds has {name} played this year?", 0, 100, 20, key=f"rounds_{i}")

    # Skill level base
    skill_map = {
        "Scratch": 12,
        "Single-Digit": 20,
        "Bogey Golfer": 30,
        "High Handicap": 40
    }
    base_mean = skill_map[skill]

    # Driving distance adjustment: longer hitters may have better approach angles
    dist_adj = np.interp(drive_dist, [200, 320], [+4, -2])

    # Round frequency adjustment: more rounds = better consistency
    std_dev = np.interp(rounds_played, [0, 100], [12, 6])

    mean = base_mean + dist_adj

    players[name] = {'mean': mean, 'std': std_dev}

if st.button("🎯 Generate Betting Odds"):
    n = 10000
    results = {
        name: np.random.normal(info['mean'], info['std'], n)
        for name, info in players.items()
    }

    winners = []
    for i in range(n):
        distances = {name: results[name][i] for name in players}
        winner = min(distances, key=distances.get)
        winners.append(winner)

    win_counts = pd.Series(winners).value_counts()
    win_probs = (win_counts / n * 100).round(2)

    def to_moneyline(p):
        if p == 0:
            return "∞"
        elif p >= 50:
            return f"-{int(round(100 * p / (100 - p)))}"
        else:
            return f"+{int(round(100 * (100 - p) / p))}"

    odds = win_probs.apply(to_moneyline)

    df = pd.DataFrame({
        "Win %": win_probs,
        "Moneyline Odds": odds
    })

    st.subheader("📊 Odds")
    st.dataframe(df)
