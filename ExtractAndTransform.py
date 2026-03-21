import streamlit as st
import pandas as pd
import os
from collections import Counter

def load_results(results_path):
    """Load the actual match results."""
    results_file = os.path.join(results_path, "Results.csv")
    df = pd.read_csv(results_file)
    return df

def load_predictions(predictions_path):
    """Load all participant predictions."""
    predictions = {}
    for filename in os.listdir(predictions_path):
        if filename.endswith(".txt"):
            participant = filename.replace(".txt", "")
            with open(os.path.join(predictions_path, filename), "r") as file:
                predictions[participant] = [line.strip() for line in file.readlines()]
    return predictions


def matchwise_predictions(schedule_df, predictions):
    """Generate a matchwise prediction table."""
    matchwise_data = []
    
    for i, row in schedule_df.iterrows():
        match_number = row.iloc[0]  # Ensuring we start from the first match
        home_team = row.iloc[2]
        away_team = row.iloc[3]
        home_predictors = []
        away_predictors = []
        
        for participant, predicted_winners in predictions.items():
            if match_number - 1 < len(predicted_winners):  # Adjusting index to ensure correct mapping
                if predicted_winners[match_number - 1] == home_team:
                    home_predictors.append(participant)
                elif predicted_winners[match_number - 1] == away_team:
                    away_predictors.append(participant)
        
        matchwise_data.append({
            "Date": row.iloc[1],
            "Home Team": home_team,
            "Home Predictors": ", ".join(home_predictors),
            "Away Team": away_team,
            "Away Predictors": ", ".join(away_predictors)
        })
    
    return pd.DataFrame(matchwise_data)


def calculate_scores(results_df, predictions):
    """Calculate leaderboard scores, accuracy, matchwise points, total predicted points, and bonus points."""
    leaderboard = []
    # Reset index so positional iloc lookups in streak period calculation are always safe
    completed_matches = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    total_matches = len(completed_matches)
    points_progression = {participant: [0] for participant in predictions.keys()}
    for participant, predicted_winners in predictions.items():
        score = 0
        correct_predictions = 0
        matchwise_points = []
        total_predicted_points = 0
        total_bonus_points = 0
        last_five_results = []
        longest_winning_streak = 0
        current_winning_streak = 0
        winning_period = ""
        longest_losing_streak = 0
        current_losing_streak = 0
        losing_period = ""

        for i, row in completed_matches.iterrows():
            actual_winner = row["Winner"]
            bonus_points = row.get("Bonus Points", 0)
            points_earned = 0

            if actual_winner == "NR":
                points_earned = 5
                last_five_results.append("➖")
                score += points_earned
                current_winning_streak = 0
                current_losing_streak = 0
            elif i < len(predicted_winners) and predicted_winners[i] == actual_winner:
                points_earned = 10 + bonus_points
                if i < 70:
                    total_predicted_points += 10
                    total_bonus_points += bonus_points
                score += points_earned
                correct_predictions += 1
                last_five_results.append("✅")
                current_winning_streak += 1
                current_losing_streak = 0
                if current_winning_streak >= longest_winning_streak:
                    longest_winning_streak = current_winning_streak
                    start_idx = max(0, i - longest_winning_streak + 1)
                    winning_period = completed_matches.iloc[start_idx]["Date"] + " - " + row["Date"]
            else:
                current_losing_streak += 1
                current_winning_streak = 0
                if current_losing_streak >= longest_losing_streak:
                    longest_losing_streak = current_losing_streak
                    start_idx = max(0, i - longest_losing_streak + 1)
                    losing_period = completed_matches.iloc[start_idx]["Date"] + " - " + row["Date"]
                last_five_results.append("❌")

            matchwise_points.append(points_earned)
            points_progression[participant].append(score)

        accuracy = (correct_predictions / total_matches) * 100 if total_matches > 0 else 0
        leaderboard.append({
            "Participant": participant,
            "Points": score,
            "Accuracy (%)": round(accuracy, 2),
            "Predicted Points": total_predicted_points,
            "Bonus Points": total_bonus_points,
            "Matchwise Points (All)": matchwise_points,
            "Matchwise Points (Last 5)": matchwise_points[-5:],
            "Last 5 Matches": " ".join(last_five_results[-5:]),
            "Longest Winning Streak": longest_winning_streak,
            "Longest Losing Streak": longest_losing_streak,
            "Winning Period": winning_period,
            "Losing Period": losing_period,
            "Correct Predictions": correct_predictions,
        })

    return pd.DataFrame(leaderboard).sort_values(by="Points", ascending=False), points_progression


def get_participant_wise_team_predictions(predictions):
    """Get all team predictions by participants, sorted in descending order of team wins."""
    rows = []
    
    for participant, predicted_winners in predictions.items():
        team_wins = Counter(predicted_winners) 
        sorted_teams = sorted(team_wins.items(), key=lambda x: x[1], reverse=True) 
        
        for team, wins in sorted_teams:
            rows.append((participant, team, wins))

    top_fours_df = pd.DataFrame(rows, columns=["Participant", "Team", "Wins"])
    
    return top_fours_df

def format_outcomes(results_df):
        total_known_results = len(results_df["Winner"].dropna())
        number_of_outcomes = 2 ** (len(results_df) - total_known_results)
        str_number_of_outcomes = f"{number_of_outcomes:,}".split(",")
        if len(str_number_of_outcomes) == 2:
            outcomes_string = str_number_of_outcomes[-2] + " thousand"
        elif len(str_number_of_outcomes) == 3:
            outcomes_string = str(str_number_of_outcomes[-3]) + " million"
        elif len(str_number_of_outcomes) == 4:
            outcomes_string = str(str_number_of_outcomes[-4]) + " billion"
        elif len(str_number_of_outcomes) == 5:
            outcomes_string = str(str_number_of_outcomes[-5]) + " trillion"
        elif len(str_number_of_outcomes) == 6:
            outcomes_string = str_number_of_outcomes[-6] + " quadrillion"
        elif len(str_number_of_outcomes) == 7:
            outcomes_string = str(str_number_of_outcomes[-7]) + " quintillion"
        else:
            outcomes_string = str_number_of_outcomes[-1]
        return number_of_outcomes, outcomes_string

def format_arrow(val):
    if val > 0:
        return f"{abs(val)}🔼"
    elif val < 0:
        return f"{abs(val)}🔽"
    else:
        return f"{val}"


def get_head_to_head(predictions, results_df, p1, p2):
    """Return a match-by-match comparison DataFrame for two participants."""
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    rows = []
    preds1 = predictions.get(p1, [])
    preds2 = predictions.get(p2, [])
    for i, row in completed.iterrows():
        actual = row["Winner"]
        bonus = row.get("Bonus Points", 0)
        pred1 = preds1[i] if i < len(preds1) else "—"
        pred2 = preds2[i] if i < len(preds2) else "—"
        if actual == "NR":
            pts1, pts2 = 5, 5
        else:
            pts1 = (10 + bonus) if pred1 == actual else 0
            pts2 = (10 + bonus) if pred2 == actual else 0
        rows.append({
            "Match #": int(row["Match #"]),
            "Date": row["Date"],
            "Home": row["Home Team"],
            "Away": row["Away Team"],
            "Actual Winner": actual,
            f"{p1} Prediction": pred1,
            f"{p2} Prediction": pred2,
            f"{p1} Points": pts1,
            f"{p2} Points": pts2,
            "Agreement": "✅" if pred1 == pred2 else "❌",
        })
    df = pd.DataFrame(rows)
    df[f"{p1} Cumulative"] = df[f"{p1} Points"].cumsum()
    df[f"{p2} Cumulative"] = df[f"{p2} Points"].cumsum()
    return df


def simulate_leaderboard(results_df, predictions, overrides: dict):
    """Simulate leaderboard with winner overrides. overrides = {match_idx (0-based): winner_team_name}."""
    simulated = results_df.copy()
    for idx, winner in overrides.items():
        simulated.at[idx, "Winner"] = winner
    leaderboard_df, _ = calculate_scores(simulated, predictions)
    return leaderboard_df[["Participant", "Points", "Accuracy (%)", "Correct Predictions"]]


def get_all_match_slots(results_df, schedule_df):
    """Return all matches with their current winner and team options."""
    slots = []
    for i, row in results_df.iterrows():
        slots.append({
            "Index": i,
            "Match #": int(row["Match #"]),
            "Date": row["Date"],
            "Home Team": row["Home Team"],
            "Away Team": row["Away Team"],
            "Current Winner": row["Winner"] if pd.notna(row["Winner"]) else "TBD",
        })
    return slots


def get_advanced_metrics(results_df, predictions):
    """Return advanced per-participant metrics: Consistency, Form, Upset Accuracy,
    Clutch Rate, Contrarian Index, Crowd Follower %, Best Solo Match."""
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    participants = list(predictions.keys())
    n = len(completed)

    # Build majority pick per match
    majority = []
    for i in range(n):
        picks = [predictions[p][i] if i < len(predictions[p]) else None for p in participants]
        picks = [p for p in picks if p is not None]
        from collections import Counter
        majority_pick = Counter(picks).most_common(1)[0][0] if picks else None
        majority.append(majority_pick)

    # Identify upset matches (away team won)
    upset_mask = [
        row["Winner"] == row["Away Team"]
        for _, row in completed.iterrows()
    ]

    # Identify close/split matches: abs difference in predictions <= 1
    home_counts = []
    away_counts = []
    for i in range(n):
        row = completed.iloc[i]
        home_picks = sum(
            1 for p in participants
            if i < len(predictions[p]) and predictions[p][i] == row["Home Team"]
        )
        away_picks = len(participants) - home_picks
        home_counts.append(home_picks)
        away_counts.append(away_picks)

    split_mask = [abs(h - a) <= 1 for h, a in zip(home_counts, away_counts)]

    rows = []
    for participant in participants:
        preds = predictions[participant]
        per_match_correct = []
        per_match_points = []
        for i, row in completed.iterrows():
            actual = row["Winner"]
            bonus = row.get("Bonus Points", 0) or 0
            if i < len(preds):
                correct = (preds[i] == actual) if actual != "NR" else None
                if actual == "NR":
                    pts = 5
                elif correct:
                    pts = 10 + bonus
                else:
                    pts = 0
            else:
                correct = None
                pts = 0
            per_match_correct.append(correct)
            per_match_points.append(pts)

        # Consistency: 100 - std of matchwise points (higher = more consistent)
        import numpy as np
        std_pts = float(np.std(per_match_points))
        consistency = max(0.0, round(100.0 - std_pts, 1))

        # Current Form: exponentially weighted accuracy on last 10 non-NR matches
        non_nr = [(i, c) for i, c in enumerate(per_match_correct) if c is not None]
        last10 = non_nr[-10:]
        if last10:
            weights = np.exp(np.linspace(-1, 0, len(last10)))
            weights /= weights.sum()
            form = round(float(np.dot([int(c) for _, c in last10], weights)) * 100, 1)
        else:
            form = 0.0

        # Upset accuracy
        upset_correct = [c for c, u in zip(per_match_correct, upset_mask) if u and c is not None]
        upset_acc = round(sum(upset_correct) / len(upset_correct) * 100, 1) if upset_correct else 0.0

        # Clutch rate
        clutch_correct = [c for c, s in zip(per_match_correct, split_mask) if s and c is not None]
        clutch_rate = round(sum(clutch_correct) / len(clutch_correct) * 100, 1) if clutch_correct else 0.0

        # Contrarian: went against majority AND was correct
        contrarian_events = [
            c
            for i, (c, maj) in enumerate(zip(per_match_correct, majority))
            if c is not None and i < len(preds) and preds[i] != maj
        ]
        contrarian_idx = round(sum(1 for c in contrarian_events if c) / max(len(contrarian_events), 1) * 100, 1)

        # Crowd follower %
        with_majority = [
            1 for i, maj in enumerate(majority)
            if i < len(preds) and preds[i] == maj
        ]
        crowd_pct = round(sum(with_majority) / max(n, 1) * 100, 1)

        # Best solo match: match where participant was correct and fewest others were
        others_correct_count = []
        for i in range(n):
            if i < len(preds) and per_match_correct[i]:
                others = sum(
                    1 for p2 in participants if p2 != participant
                    and i < len(predictions[p2])
                    and predictions[p2][i] == completed.iloc[i]["Winner"]
                )
                others_correct_count.append((i, others))
        if others_correct_count:
            best_idx, _ = min(others_correct_count, key=lambda x: x[1])
            best_row = completed.iloc[best_idx]
            best_match = f"M{int(best_row['Match #'])}: {best_row['Home Team'][:3]} vs {best_row['Away Team'][:3]}"
        else:
            best_match = "—"

        rows.append({
            "Participant":         participant,
            "Consistency Score":   consistency,
            "Current Form (%)":    form,
            "Upset Accuracy (%)": upset_acc,
            "Clutch Rate (%)":     clutch_rate,
            "Contrarian Index (%)": contrarian_idx,
            "Crowd Follower (%)":  crowd_pct,
            "Best Solo Match":     best_match,
        })

    return pd.DataFrame(rows)


def get_team_accuracy_matrix(results_df, predictions, schedule_df):
    """Return a DataFrame[participant × team] = accuracy % predicting that team's matches."""
    completed = results_df.dropna(subset=["Winner"]).copy()
    schedule_df = schedule_df.copy()
    schedule_df.columns = schedule_df.columns.str.strip()
    participants = list(predictions.keys())

    teams = sorted(set(schedule_df["Home Team"].tolist() + schedule_df["Away Team"].tolist()))
    data = {p: {} for p in participants}

    for i, row in completed.iterrows():
        actual = row["Winner"]
        if actual == "NR":
            continue
        home = row["Home Team"]
        away = row["Away Team"]
        match_idx = int(row["Match #"]) - 1  # 0-based
        for p in participants:
            pred = predictions[p][match_idx] if match_idx < len(predictions[p]) else None
            correct = int(pred == actual) if pred is not None else None
            for team in [home, away]:
                if team not in data[p]:
                    data[p][team] = []
                if correct is not None:
                    data[p][team].append(correct)

    rows = {}
    for p in participants:
        rows[p] = {}
        for team in teams:
            vals = data[p].get(team, [])
            rows[p][team] = round(sum(vals) / len(vals) * 100, 1) if vals else None

    return pd.DataFrame(rows).T  # participants on rows, teams on columns


def get_match_difficulty(results_df, predictions, schedule_df):
    """Return a per-match difficulty DataFrame sorted by % correct ascending."""
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    participants = list(predictions.keys())
    rows = []
    for i, row in completed.iterrows():
        actual = row["Winner"]
        if actual == "NR":
            continue
        match_idx = int(row["Match #"]) - 1
        correct_count = sum(
            1 for p in participants
            if match_idx < len(predictions[p]) and predictions[p][match_idx] == actual
        )
        pct_correct = round(correct_count / len(participants) * 100, 1)
        is_upset = actual == row["Away Team"]
        rows.append({
            "Match #":    int(row["Match #"]),
            "Match":      f"M{int(row['Match #'])}: {row['Home Team'][:3]} vs {row['Away Team'][:3]}",
            "Winner":     actual,
            "Was Upset":  is_upset,
            "% Correct":  pct_correct,
            "Correct":    correct_count,
            "Total":      len(participants),
        })
    return pd.DataFrame(rows).sort_values("% Correct")


def get_agreement_matrix(predictions, results_df):
    """Return symmetric DataFrame[participant × participant] = % match on completed matches."""
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    participants = sorted(predictions.keys())
    n = len(completed)
    matrix = {p1: {} for p1 in participants}
    for p1 in participants:
        for p2 in participants:
            agree = sum(
                1 for i in range(n)
                if i < len(predictions[p1]) and i < len(predictions[p2])
                and predictions[p1][i] == predictions[p2][i]
            )
            total = min(n, len(predictions[p1]), len(predictions[p2]))
            matrix[p1][p2] = round(agree / total * 100, 1) if total else 0
    return pd.DataFrame(matrix)


def get_points_distribution(results_df, predictions):
    """Return a DataFrame[participant × score_bucket] of match counts."""
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    participants = list(predictions.keys())
    rows = []
    for p in participants:
        preds = predictions[p]
        buckets = {"0 pts": 0, "5 pts": 0, "10 pts": 0, "20 pts": 0}
        for i, row in completed.iterrows():
            actual = row["Winner"]
            bonus = int(row.get("Bonus Points", 0) or 0)
            pred = preds[i] if i < len(preds) else None
            if actual == "NR":
                buckets["5 pts"] += 1
            elif pred == actual:
                key = "20 pts" if bonus > 0 else "10 pts"
                buckets[key] += 1
            else:
                buckets["0 pts"] += 1
        rows.append({"Participant": p, **buckets})
    return pd.DataFrame(rows)


def get_stadium_luck(results_df, predictions, schedule_df):
    """Return a DataFrame mapping each IPL stadium to its Lucky and Unlucky predictors."""
    STADIUMS = {
        "Chennai Super Kings": {"Stadium": "M. A. Chidambaram Stadium", "Lat": 13.0628, "Lon": 80.2793},
        "Delhi Capitals": {"Stadium": "Arun Jaitley Stadium", "Lat": 28.6378, "Lon": 77.2432},
        "Gujarat Titans": {"Stadium": "Narendra Modi Stadium", "Lat": 23.0917, "Lon": 72.5975},
        "Kolkata Knight Riders": {"Stadium": "Eden Gardens", "Lat": 22.5646, "Lon": 88.3433},
        "Lucknow Super Giants": {"Stadium": "Ekana Cricket Stadium", "Lat": 26.8115, "Lon": 81.0152},
        "Mumbai Indians": {"Stadium": "Wankhede Stadium", "Lat": 18.9389, "Lon": 72.8256},
        "Punjab Kings": {"Stadium": "M. Yadavindra Singh Stadium", "Lat": 30.7760, "Lon": 76.7589},
        "Rajasthan Royals": {"Stadium": "Sawai Mansingh Stadium", "Lat": 26.8940, "Lon": 75.8033},
        "Royal Challengers Bengaluru": {"Stadium": "M. Chinnaswamy Stadium", "Lat": 12.9788, "Lon": 77.5996},
        "Sunrisers Hyderabad": {"Stadium": "Rajiv Gandhi Intl Stadium", "Lat": 17.4065, "Lon": 78.5505}
    }
    
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    participants = list(predictions.keys())
    
    # Initialize trackers for each team (stadium)
    stadium_stats = {team: {p: {"wins": 0, "losses": 0} for p in participants} for team in STADIUMS.keys()}
    
    for i, row in completed.iterrows():
        actual = row["Winner"]
        if actual == "NR":
            continue
            
        home_team = row.get("Home Team")
        match_idx = int(row["Match #"]) - 1
        
        # If home_team isn't in schedule_df directly, we should get it from schedule
        if pd.isna(home_team) or not home_team:
            sched_row = schedule_df[schedule_df["Match #"].astype(str) == str(row["Match #"])]
            if not sched_row.empty:
                home_team = sched_row.iloc[0]["Home Team"]
                
        if pd.notna(home_team) and home_team in STADIUMS:
            for p in participants:
                if match_idx < len(predictions[p]):
                    if predictions[p][match_idx] == actual:
                        stadium_stats[home_team][p]["wins"] += 1
                    else:
                        stadium_stats[home_team][p]["losses"] += 1

    # Compile the final dataframe
    rows = []
    for team, info in STADIUMS.items():
        stats = stadium_stats[team]
        
        # Find lucky (max wins)
        lucky_p = max(participants, key=lambda p: stats[p]["wins"])
        lucky_wins = stats[lucky_p]["wins"]
        
        # Find unlucky (max losses)
        unlucky_p = max(participants, key=lambda p: stats[p]["losses"])
        unlucky_losses = stats[unlucky_p]["losses"]
        
        # If no matches played yet, handle gracefully
        if lucky_wins == 0 and unlucky_losses == 0:
            lucky_str = "None (0 Wins)"
            unlucky_str = "None (0 Losses)"
        else:
            # Handle ties by joining names
            lucky_ties = [p for p in participants if stats[p]["wins"] == lucky_wins]
            unlucky_ties = [p for p in participants if stats[p]["losses"] == unlucky_losses]
            
            lucky_str = f"{', '.join(lucky_ties)} ({lucky_wins} Wins)" if lucky_wins > 0 else "None"
            unlucky_str = f"{', '.join(unlucky_ties)} ({unlucky_losses} Losses)" if unlucky_losses > 0 else "None"
            
        rows.append({
            "Team": team,
            "Stadium": info["Stadium"],
            "Lat": info["Lat"],
            "Lon": info["Lon"],
            "Lucky Predictor": lucky_str,
            "Unlucky Predictor": unlucky_str
        })
        
    return pd.DataFrame(rows)