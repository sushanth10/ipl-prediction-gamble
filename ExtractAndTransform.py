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
    completed_matches = results_df.dropna(subset=["Winner"]) 
    total_matches = len(completed_matches)
    points_progression = {participant: [0] for participant in predictions.keys()} 
    for participant, predicted_winners in predictions.items():
        score = 0
        correct_predictions = 0
        matchwise_points = []
        # total_predicted_points = 0
        # total_bonus_points = 0
        last_five_results = []

        for i, row in completed_matches.iterrows():
            actual_winner = row["Winner"]
            bonus_points = row.get("Bonus Points", 0)
            points_earned = 0

            if actual_winner == "NR":
                points_earned = 5
                last_five_results.append("➖")
            elif i < len(predicted_winners) and predicted_winners[i] == actual_winner:
                points_earned = 10 + bonus_points
                # total_predicted_points += 10
                # total_bonus_points += bonus_points 
                score += points_earned
                correct_predictions += 1
                last_five_results.append("✅")
            else:
                last_five_results.append("❌")
            
            matchwise_points.append(points_earned)
            points_progression[participant].append(score)

        accuracy = (correct_predictions / total_matches) * 100 if total_matches > 0 else 0
        leaderboard.append({
            "Participant": participant,
            "Points": score,
            "Accuracy (%)": round(accuracy, 2),
            # "Total Predicted Points": total_predicted_points,
            # "Bonus Points": total_bonus_points,
            "Matchwise Points (Last 5)": matchwise_points[-5:],
            "Last 5 Matches": " ".join(last_five_results[-5:])
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