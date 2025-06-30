import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Golf Round & Odds App", layout="wide")
st.title("⛳️ Golf Round + Closest-to-the-Pin Odds")

# ---------------------------
# Session Setup
# ---------------------------
if "round_started" not in st.session_state:
    st.session_state.round_started = False

if "scorecard" not in st.session_state:
    st.session_state.scorecard = {}

# ---------------------------
# Player Setup
# ---------------------------
if not st.session_state.round_started:
    st.subheader("🎯 Add Players & Setup Round")
    num_players = st.number_input("How many players?", min_value=2, max_value=6, value=4)
    players = []

    for i in range(num_players):
        name = st.text_input(f"Player {i+1} Name", value=f"Player {i+1}", key=f"name_{i}")
        skill = st.selectbox(f"{name}'s Skill Level", ["Scratch", "Single-Digit", "Bogey Golfer", "High Handicap"], key=f"skill_{i}")
        drive = st.slider(f"{name}'s Avg Driving Distance", 200, 320, 250, key=f"drive_{i}")
        rounds = st.slider(f"Rounds Played This Year", 0, 100, 20, key=f"rounds_{i}")
        players.append({"name": name, "skill": skill, "drive": drive, "rounds": rounds})

    if st.button("Start Round"):
        st.session_state.round_started = True
        st.session_state.players = players
        st.session_state.scorecard = {p['name']: [] for p in players}
        st.rerun()

# ---------------------------
# Round In Progress
# ---------------------------
if st.session_state.round_started:
    st.subheader("📝 Enter Scores for Each Hole")

    hole = st.number_input("Hole Number", min_value=1, max_value=18, value=1)
    par = st.selectbox("Par for this hole", [3, 4, 5], index=1)

    for player in st.session_state.players:
        score = st.number_input(f"{player['name']}'s score", min_value=1, max_value=10, key=f"score_{player['name']}_{hole}")
        # Auto-fill to the scorecard if not already stored for this hole
        if len(st.session_state.scorecard[player['name']]) < hole:
            st.session_state.scorecard[player['name']].append(score)
        else:
            st.session_state.scorecard[player['name']][hole-1] = score

    if st.button("Next Hole"):
        st.success("Hole scores saved.")
        st.rerun()

    # ---------------------------
    # Leaderboard
    # ---------------------------
    st.subheader("📊 Live Leaderboard")

    leaderboard = {
        name: sum(scores) for name, scores in st.session_state.scorecard.items()
    }
    leaderboard_df = pd.DataFrame.from_dict(leaderboard, orient='index', columns=["Total Score"]).sort_values("Total Score")
    st.dataframe(leaderboard_df)

    # ---------------------------
    # Betting Odds Button
    # ---------------------------
    st.markdown("---")
    if st.button("🎲 Generate Closest to Pin Odds"):
        st.subheader("🎯 Odds Based on Player Profiles")

        skill_map = {
            "Scratch": 12,
            "Single-Digit": 20,
            "Bogey Golfer": 30,
            "High Handicap": 40
        }

        players_stats = {}
        for p in st.session_state.players:
            base_mean = skill_map[p['skill']]
            dist_adj = np.interp(p['drive'], [200, 320], [+4, -2])
            std = np.interp(p['rounds'], [0, 100], [12, 6])
            mean = base_mean + dist_adj
            players_stats[p['name']] = {'mean': mean, 'std': std}

        n = 10000
        results = {
            name: np.random.normal(info['mean'], info['std'], n)
            for name, info in players_stats.items()
        }

        winners = []
        for i in range(n):
            distances = {name: results[name][i] for name in players_stats}
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

        st.dataframe(df)
