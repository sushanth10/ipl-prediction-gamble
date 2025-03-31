import plotly.express as px
import plotly.graph_objects as go
import numpy as np

team_colors = {
    'Chennai Super Kings': '#F9CD05',  # Yellow
    'Delhi Capitals': '#17449B',       # Blue
    'Gujarat Titans': '#0A1D56',       # Dark Blue
    'Kolkata Knight Riders': '#2E0854',# Purple
    'Lucknow Super Giants': '#00ADEF', # Light Blue
    'Mumbai Indians': '#045093',       # Blue
    'Punjab Kings': '#D71920',         # Red
    'Rajasthan Royals': '#EA1A84',     # Pink
    'Royal Challengers Bengaluru': '#DA1818', # Red
    'Sunrisers Hyderabad': '#FB643E'   # Orange
}

team_initials = {
    "Lucknow Super Giants": "LSG",
    "Sunrisers Hyderabad": "SRH",
    "Kolkata Knight Riders": "KKR",
    "Mumbai Indians": "MI",
    "Gujarat Titans": "GT",
    "Royal Challengers Bengaluru": "RCB",
    "Chennai Super Kings": "CSK",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR"
}   

def plot_worm_graph(points_progression):
    """Plot the worm graph showing points progression with smooth curves."""
    fig = go.Figure()
    
    for participant, points in points_progression.items():
        x = np.linspace(0, len(points) - 1, num=len(points))
        fig.add_trace(go.Scatter(x=x, y=points, mode='lines', name=participant, line_shape='spline'))
    
    fig.update_layout(title="Points Progression", xaxis_title="Matches", yaxis_title="Points", template="plotly_dark")
    fig.write_image("The Visuals/worm_graph.png", format="png", scale=4)
    return fig

def plot_participant_wise_team_predictions(participant_wise_team_predictions):
    """Plot the top four team predictions by participants."""
    participant_wise_team_predictions['Color'] = participant_wise_team_predictions['Team'].map(team_colors)
    participant_wise_team_predictions['Team Initials'] = participant_wise_team_predictions['Team'].map(team_initials)


    fig = px.bar(
        participant_wise_team_predictions, 
        x="Team Initials", 
        y="Wins", 
        color="Team",
        color_discrete_map=team_colors,
        labels={"Wins": "Wins", "Participant": "Participant"}
    )
    return fig

def avg_wins_plot(mean_counts_df):
    """Plot average wins by teams"""
    fig = px.bar(
        mean_counts_df,
        color=mean_counts_df.index,
        color_discrete_map=team_colors,
        orientation="h",
        title="Average",
        labels={"value": "Average Wins", "index": "Teams"},
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_prediction_ratio(prediction_ratio_counts):
    """Plot the prediction ratio analysis."""
    fig = px.bar(
                prediction_ratio_counts,
                x="Prediction Ratio",
                y="Count",
                 color="Prediction Ratio",
                 color_discrete_sequence=px.colors.qualitative.Set1,
                 title="Prediction Ratio Analysis",
                labels={"index": "Prediction Ratio", "value": "Count"}
                )
    return fig

def plot_home_away_ratio(home_away_ratio_counts):
    """Plot the prediction ratio analysis."""
    fig = px.bar(
                home_away_ratio_counts,
                x="Home-Away Ratio", 
                y="Count", 
                color="Home-Away Ratio", 
                color_discrete_sequence=px.colors.qualitative.Set1,
                # line_shape='spline',
                title="Home-Away Ratio Analysis",
                labels={"index": "Home-Away Ratio", "value": "Count"}
                )
    return fig