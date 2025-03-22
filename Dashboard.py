import streamlit as st
import pandas as pd
import os

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

def calculate_scores(results_df, predictions):
    """Calculate leaderboard scores, accuracy, and matchwise points."""
    leaderboard = []
    completed_matches = results_df.dropna(subset=["Winner"])  # Consider only completed matches
    total_matches = len(completed_matches)
    
    for participant, predicted_winners in predictions.items():
        score = 0
        correct_predictions = 0
        matchwise_points = []
        
        for i, row in completed_matches.iterrows():
            actual_winner = row["Winner"]
            bonus_points = row.get("Bonus Points", 0)
            points_earned = 0
            
            if i < len(predicted_winners) and predicted_winners[i] == actual_winner:
                points_earned = 10 + bonus_points
                score += points_earned
                correct_predictions += 1
            
            matchwise_points.append(points_earned)
        
        accuracy = (correct_predictions / total_matches) * 100 if total_matches > 0 else 0
        leaderboard.append({
            "Participant": participant,
            "Points": score,
            "Accuracy (%)": round(accuracy, 2),
            "Matchwise Points": matchwise_points
        })
    
    return pd.DataFrame(leaderboard).sort_values(by="Points", ascending=False)

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
            "Home Team": home_team,
            "Home Predictors": ", ".join(home_predictors),
            "Away Team": away_team,
            "Away Predictors": ", ".join(away_predictors)
        })
    
    return pd.DataFrame(matchwise_data)

def main():
    st.set_page_config(layout="wide")
    st.title("IPL Match Prediction Leaderboard")
    
    base_path = "/home/sushanth/Github/ipl-prediction-gamble"  # Change this to your actual folder path
    schedule_path = os.path.join(base_path, "The Schedule/ipl_2025_schedule.csv")
    predictions_path = os.path.join(base_path, "The Gambles")
    results_path = os.path.join(base_path, "The Results")

    schedule_df = pd.read_csv(schedule_path)
    
    results_df = load_results(results_path)
    predictions = load_predictions(predictions_path)
    leaderboard_df = calculate_scores(results_df, predictions)
    matchwise_df = matchwise_predictions(schedule_df, predictions)

    tab1, tab2, tab3 = st.tabs(["Leaderboard", "All Predictions", "Matchwise Predictions"])

    with tab1:         
        st.subheader("Leaderboard")
        st.dataframe(leaderboard_df, use_container_width=True)

    st.write('\n\n')

    with tab2 : 
        st.subheader("All Predictions")
        st.dataframe(predictions, use_container_width=True)

    st.write('\n\n')

    with tab3:
        st.subheader("Matchwise Predictions")
        st.dataframe(matchwise_df, use_container_width=True)

if __name__ == "__main__":
    main()
