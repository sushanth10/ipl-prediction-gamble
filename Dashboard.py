import streamlit as st
import pandas as pd
import os
import Plotting
import ExtractAndTransform
import Analysis

def format_matchwise_points(points_list):
    return "".join(f'<span style="background-color:#444; color:white; padding:5px 8px; border-radius:5px; margin:2px;">{p}</span>' for p in points_list)

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
    predictions_path = os.path.join(base_path, "The Calculated Gambles")
    results_path = os.path.join(base_path, "The Results")

    schedule_df = pd.read_csv(schedule_path)
    
    results_df = ExtractAndTransform.load_results(results_path)
    predictions = ExtractAndTransform.load_predictions(predictions_path)
    leaderboard_df, points_progression = ExtractAndTransform.calculate_scores(results_df, predictions)
    leaderboard_df["Rank"] = leaderboard_df["Points"].rank(method="dense", ascending=False).astype(int)
    col = leaderboard_df.pop("Rank")
    leaderboard_df.insert(0, "Rank", col)
    leaderboard_df = leaderboard_df.sort_values(by="Rank").reset_index(drop=True)
    leaderboard_df["Matchwise Points (Last 5)"] = leaderboard_df["Matchwise Points (Last 5)"].apply(format_matchwise_points)
    matchwise_df = ExtractAndTransform.matchwise_predictions(schedule_df, predictions)

    tab1, tab2, tab3, tab4 = st.tabs(["Leaderboard", "All Predictions", "Matchwise Predictions", "Analysis"])

    with tab1:         
        st.subheader("Leaderboard")
        st.write(leaderboard_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        number_of_outcomes, outcomes_string = ExtractAndTransform.format_outcomes(results_df)
        st.markdown(f'##### Total Possible Outcomes for Remaining League Matches : **{outcomes_string}** ({number_of_outcomes:,}) outcomes') 

        st.write('\n\n')
        st.subheader("Points Progression Worm")
        st.plotly_chart(Plotting.plot_worm_graph(points_progression), use_container_width=True)

    st.write('\n\n')

    with tab2 : 
        st.subheader("All Predictions")
        st.dataframe(predictions, use_container_width=True)

    st.write('\n\n')

    with tab3:
        st.subheader("Matchwise Predictions")
        st.dataframe(matchwise_df, use_container_width=True)

    with tab4:
        st.subheader("Participant-wise Team Win Predictions")
        participant_wise_team_predictions = ExtractAndTransform.get_participant_wise_team_predictions(predictions)
        participants = participant_wise_team_predictions["Participant"].unique()
        num_participants = len(participants)
        cols_per_row = 6
        for i in range(0, num_participants, cols_per_row):
            cols = st.columns(cols_per_row)  # Create 6 columns in the row
            
            for j, col in enumerate(cols):
                if i + j < num_participants: 
                    participant = participants[i + j]
                    with col:  # Place chart in the respective column
                        st.write(f"###### {participant}")
                        fig = Plotting.plot_participant_wise_team_predictions(
                            participant_wise_team_predictions[participant_wise_team_predictions["Participant"] == participant]
                        )
                        fig.update_layout(showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

        st.write('\n\n')
        counts_df = Analysis.prediction_counts_analysis(predictions)
        counts_df_mean = counts_df.mean().sort_values(ascending=False)
        st.plotly_chart(Plotting.avg_wins_plot(counts_df_mean), use_container_width=True)

        st.write('\n\n')
        st.subheader("Prediction Ratio Analysis")
        prediction_ratio_counts, home_away_ratio_counts = Analysis.get_prediction_ratios(matchwise_df)
        st.plotly_chart(Plotting.plot_prediction_ratio(prediction_ratio_counts), use_container_width=True)
        st.plotly_chart(Plotting.plot_home_away_ratio(home_away_ratio_counts), use_container_width=True)
        st.write('\n\n')

        percentage_df = Analysis.home_away_percentage(schedule_df, pd.DataFrame(predictions))
        percentage_df.sort_values(by="Home", ascending=False, inplace=True)
        percentage_df = percentage_df.rename(columns={"Home": "Home %", "Away": "Away %"})
        st.plotly_chart(Plotting.plot_home_away_percentage(percentage_df), use_container_width=True)

if __name__ == "__main__":
    main()
