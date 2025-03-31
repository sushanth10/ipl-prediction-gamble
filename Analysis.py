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
    prediction_ratio_counts = matchwise_predictions_df["Prediction Ratio"].value_counts().reset_index()
    prediction_ratio_counts.columns = ["Prediction Ratio", "Count"]
    prediction_ratio_counts = prediction_ratio_counts.sort_values(by="Count", ascending=False)
    home_away_ratio_counts = matchwise_predictions_df["Home-Away Ratio"].value_counts().reset_index()
    home_away_ratio_counts.columns = ["Home-Away Ratio", "Count"]
    home_away_ratio_counts.sort_values(by="Home-Away Ratio", ascending=True, inplace=True)
    return prediction_ratio_counts, home_away_ratio_counts
