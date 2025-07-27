import numpy as np
import pandas as pd
import os
import streamlit as st

def prediction_counts_analysis(predictions):
    counts_df = pd.DataFrame(predictions)
    counts_df = counts_df.apply(pd.Series.value_counts).T.fillna(0).astype(int)
    return counts_df

def get_prediction_ratios(matchwise_predictions_df):
    prediction_difference_map = {11:'11:0',9: '1:10', 7: '2:9', 5: '3:8', 3: '4:7', 1: '5:6'}
    home_away_ratio_map = {-9:'1:10', -7:'2:9', -5:'3:8', (-3):'4:7', (-1):'5:6',1:'6:5', 3:'7:4', 5:'8:3', 7:'9:2', 9:'10:1'}
    matchwise_predictions_df["Absolute Prediction Difference"] = abs(matchwise_predictions_df['Home Predictors'].str.split(',').apply(len) - matchwise_predictions_df['Away Predictors'].str.split(',').apply(len))
    matchwise_predictions_df["Prediction Difference"] = (matchwise_predictions_df['Home Predictors'].str.split(',').apply(len) - matchwise_predictions_df['Away Predictors'].str.split(',').apply(len))
    matchwise_predictions_df["Prediction Ratio"] = matchwise_predictions_df["Absolute Prediction Difference"].map(prediction_difference_map)
    matchwise_predictions_df["Home-Away Ratio"] = matchwise_predictions_df["Prediction Difference"].map(home_away_ratio_map)
    # major_gen_predictions = matchwise_predictions_df.apply(lambda row: row["Home Team"] if row["Prediction Difference"] > 0 else row["Away Team"], axis=1)
    prediction_ratio_counts = matchwise_predictions_df["Prediction Ratio"].value_counts().reset_index()
    prediction_ratio_counts.columns = ["Prediction Ratio", "Count"]
    prediction_ratio_counts = prediction_ratio_counts.sort_values(by="Count", ascending=False)
    home_away_ratio_counts = matchwise_predictions_df["Home-Away Ratio"].value_counts().reset_index()
    home_away_ratio_counts.columns = ["Home-Away Ratio", "Count"]
    home_away_ratio_counts.sort_values(by="Home-Away Ratio", ascending=True, inplace=True)
    return prediction_ratio_counts, home_away_ratio_counts


def home_away_percentage(schedule_df, predictions_df):
    matchwise_predictions_df = pd.concat([schedule_df, predictions_df], axis=1)
    for participant in predictions_df.columns:
        matchwise_predictions_df[participant] = np.where( matchwise_predictions_df[participant] == matchwise_predictions_df[" Home Team"], "Home", "Away")
    matchwise_predictions_df = matchwise_predictions_df.iloc[:,4:]
    percentage_df = matchwise_predictions_df.apply(lambda col: col.value_counts(normalize=True) * 100).fillna(0).T
    return percentage_df

def get_points_progression_df(points_progression) :
    """Plot for bar chart race showing points progression."""
    data = []
    for participant, scores in points_progression.items():
        for match, points in enumerate(scores):
            data.append({"Participant": participant, "Match": match, "Points": points})
    points_progression_df = pd.DataFrame(data)
    points_progression_df["Rank"] = points_progression_df.groupby("Match")["Points"].rank(method="first", ascending=False)
    points_progression_df.sort_values(by=["Match", "Rank"], inplace=True)
    return points_progression_df

def get_time_spent_position(points_progression_df):
    time_spent_position_df = points_progression_df.groupby(by=['Participant','Rank']).size().reset_index(name="Count")
    return time_spent_position_df