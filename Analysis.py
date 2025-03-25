import numpy as np
import pandas as pd
import os
import streamlit as st

def prediction_counts_analysis(predictions):
    counts_df = pd.DataFrame(predictions)
    counts_df = counts_df.apply(pd.Series.value_counts).T.fillna(0).astype(int)
    st.write("Prediction Counts Analysis")
    st.write(counts_df, use_container_width=True)
    return counts_df