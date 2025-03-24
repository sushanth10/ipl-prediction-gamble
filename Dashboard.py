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

def format_matchwise_points(points_list):
    return "".join(f'<span style="background-color:#444; color:white; padding:5px 8px; border-radius:5px; margin:2px;">{p}</span>' for p in points_list)

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

    st.markdown("""
        <style>
            /* Table Styling */
            .dataframe {
                border-collapse: collapse;
                width: 100%;
                font-size: 14px;
                border-radius: 8px;
                overflow: hidden;
            }
            
            /* Table Header */
            .dataframe th {
                background-color: #1f1f1f;
                color: #ffffff;
                padding: 10px;
                text-align: center;
            }
            
            /* Table Rows */
            .dataframe td {
                padding: 10px;
                text-align: center;
                border-bottom: 1px solid #444;
            }
            
            /* Alternate Row Color */
            .dataframe tr:nth-child(even) {
                background-color: #2b2b2b;
            }
            
            /* Hover Effect */
            .dataframe tr:hover {
                background-color: #3a3a3a;
            }
            
            /* Icons Styling */
            .tick { color: limegreen; font-size: 18px; }
            .cross { color: red; font-size: 18px; }
            .dash { color: grey; font-size: 18px; }
                
            .matchwise-points {
                display: flex;
                gap: 6px;
            }

            .matchwise-points span {
                padding: 4px 12px;
                border-radius: 50px;  /* Makes it a pill */
                font-weight: bold;
                font-size: 14px;
                color: white;
                background-color: #17a2b8; /* Single color (Teal) */
                min-width: 35px;
                text-align: center;
                display: inline-block;
            }

        </style>
        """, unsafe_allow_html=True)

    
    base_path = "/home/sushanth/Github/ipl-prediction-gamble"  # Change this to your actual folder path
    schedule_path = os.path.join(base_path, "The Schedule/ipl_2025_schedule.csv")
    predictions_path = os.path.join(base_path, "The Gambles")
    results_path = os.path.join(base_path, "The Results")

    schedule_df = pd.read_csv(schedule_path)
    
    results_df = load_results(results_path)
    predictions = load_predictions(predictions_path)
    leaderboard_df, points_progression = calculate_scores(results_df, predictions)
    leaderboard_df["Rank"] = leaderboard_df["Points"].rank(method="dense", ascending=False).astype(int)
    leaderboard_df = leaderboard_df.set_index("Rank")
    leaderboard_df["Matchwise Points (Last 5)"] = leaderboard_df["Matchwise Points (Last 5)"].apply(format_matchwise_points)
    matchwise_df = matchwise_predictions(schedule_df, predictions)

    tab1, tab2, tab3 = st.tabs(["Leaderboard", "All Predictions", "Matchwise Predictions"])
    # tab1, tab2, tab3, tab4 = st.tabs(["Leaderboard", "All Predictions", "Matchwise Predictions", "Analysis"])

    with tab1:         
        st.subheader("Leaderboard")
        st.write(leaderboard_df.to_html(escape=False, index=True), use_container_width=True, hide_index=True, unsafe_allow_html=True)
        st.markdown("##### Total Possible Outcomes for Remaining League Matches : **73.7 quintillion** (73,786,976,294,838,206,464) outcomes") 

        st.write('\n\n')
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
