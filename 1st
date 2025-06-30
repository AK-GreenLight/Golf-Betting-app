import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Golf Side Bet Odds", layout="centered")
st.title("🏌️ Closest to the Pin - Odds Generator")

st.write("Enter each player’s expected distance from the pin and consistency. We'll simulate who’s most likely to win.")

num_players = st.number_input("How many players?", min_value=2, max_value=6, value=4)
players = {}

for i in range(num_players):
    name = st.text_input(f"Player {i+1} Name", value=f"Player {i+1}")
    mean = st.slider(f"{name} - Avg distance from pin (ft)", 5, 60, 25)
    std = st.slider(f"{name} - Shot variability (std dev)", 2, 20, 8)
    players[name] = {'mean': mean, 'std': std}

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
