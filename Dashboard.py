import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


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
    """Calculate leaderboard scores, accuracy, matchwise points, total predicted points, and bonus points."""
    leaderboard = []
    completed_matches = results_df.dropna(subset=["Winner"])  # Consider only completed matches
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


def plot_worm_graph(points_progression):
    """Plot the worm graph showing points progression with smooth curves."""
    fig = go.Figure()
    
    for participant, points in points_progression.items():
        x = np.linspace(0, len(points) - 1, num=len(points))
        fig.add_trace(go.Scatter(x=x, y=points, mode='lines', name=participant, line_shape='spline'))
    
    fig.update_layout(title="Points Progression", xaxis_title="Matches", yaxis_title="Points", template="plotly_dark")
    return fig

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
    leaderboard_df, points_progression = calculate_scores(results_df, predictions)
    matchwise_df = matchwise_predictions(schedule_df, predictions)

    tab1, tab2, tab3 = st.tabs(["Leaderboard", "All Predictions", "Matchwise Predictions"])

    with tab1:         
        st.subheader("Leaderboard")
        st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
        st.markdown("##### Total Possible Match Outcomes for League Matches : **59 lakh crore crore** (59,02,95,81,03,58,70,56,51,712) outcomes")  
        st.subheader("Points Progression (Worm Graph)")
        st.plotly_chart(plot_worm_graph(points_progression), use_container_width=True)

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
