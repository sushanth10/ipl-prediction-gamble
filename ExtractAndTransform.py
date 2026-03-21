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