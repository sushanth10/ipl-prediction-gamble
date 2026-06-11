import numpy as np
import pandas as pd
import os
import streamlit as st

def prediction_counts_analysis(predictions):
    max_len = max(len(v) for v in predictions.values())
    padded = {k: v + [''] * (max_len - len(v)) for k, v in predictions.items()}
    counts_df = pd.DataFrame(padded)
    counts_df = counts_df.apply(pd.Series.value_counts).T.fillna(0).astype(int)
    return counts_df

def get_prediction_ratios(matchwise_predictions_df):
    def count_valid(col_val):
        """Count non-empty comma-separated entries — empty string gives 0, not 1."""
        return len([x for x in str(col_val).split(",") if x.strip()])

    home_counts = matchwise_predictions_df["Home Predictors"].apply(count_valid)
    away_counts = matchwise_predictions_df["Away Predictors"].apply(count_valid)

    # Prediction ratio: absolute split, format as "max:min" (e.g. 9:3, 6:6)
    def pred_ratio(h, a):
        hi, lo = max(h, a), min(h, a)
        return f"{hi}:{lo}"

    matchwise_predictions_df = matchwise_predictions_df.copy()
    matchwise_predictions_df["Prediction Ratio"] = [
        pred_ratio(h, a) for h, a in zip(home_counts, away_counts)
    ]

    # Home-Away Ratio: directional, format as "H:A" (e.g. 9:3, 3:9)
    matchwise_predictions_df["Home-Away Ratio"] = [
        f"{h}:{a}" for h, a in zip(home_counts, away_counts)
    ]

    prediction_ratio_counts = matchwise_predictions_df["Prediction Ratio"].value_counts().reset_index()
    prediction_ratio_counts.columns = ["Prediction Ratio", "Count"]
    prediction_ratio_counts = prediction_ratio_counts.sort_values(by="Count", ascending=False)

    home_away_ratio_counts = matchwise_predictions_df["Home-Away Ratio"].value_counts().reset_index()
    home_away_ratio_counts.columns = ["Home-Away Ratio", "Count"]
    # Sort by home count numerically
    home_away_ratio_counts["_sort"] = home_away_ratio_counts["Home-Away Ratio"].apply(
        lambda x: int(x.split(":")[0])
    )
    home_away_ratio_counts.sort_values("_sort", ascending=True, inplace=True)
    home_away_ratio_counts.drop(columns=["_sort"], inplace=True)
    home_away_ratio_counts.reset_index(drop=True, inplace=True)

    return prediction_ratio_counts, home_away_ratio_counts


def home_away_percentage(schedule_df, predictions_df):
    matchwise_predictions_df = pd.concat([schedule_df, predictions_df], axis=1)
    for participant in predictions_df.columns:
        matchwise_predictions_df[participant] = np.where( matchwise_predictions_df[participant] == matchwise_predictions_df["Home Team"], "Home", "Away")
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