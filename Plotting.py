import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

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

    colorscale = px.colors.qualitative.G10
    participants = list(points_progression.keys())
    color_map = {participants[i]: colorscale[i % len(colorscale)] for i in range(len(participants))}
 
    
    for participant, points in points_progression.items():
        x = np.linspace(0, len(points) - 1, num=len(points))
        fig.add_trace(go.Scatter(x=x, y=points, mode='lines', name=participant,
                                 line=dict(color=color_map[participant], width=2), line_shape='spline'))
    
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

def plot_home_away_percentage(percentage_df):
    """Plot the prediction ratio analysis."""
    avg_home_percentage = percentage_df["Home %"].mean()
    fig = px.bar(
                percentage_df,
                x="Home %", 
                y=percentage_df.index,
                orientation="h", 
                color=percentage_df.index, 
                color_discrete_sequence=px.colors.qualitative.Set1,
                # line_shape='spline',
                title="Home/Away Percentage Analysis",
                labels={"index": "Participant", "value": "Home Percentage"}
                )
    
    fig.add_shape(
        type="line",
        x0=avg_home_percentage, x1=avg_home_percentage,
        y0=-0.5, y1=len(percentage_df.index) - 0.5,
        line=dict(color="white", width=2, dash="dash"),
        name="Average Home Percentage"
    )

    fig.add_annotation(
        x=avg_home_percentage,
        y=-0.5,
        text=f"Average Home Win %: {avg_home_percentage:.2f}%",
        showarrow=False,
        font=dict(color="black", size=12),
        bgcolor="white"
    )
    return fig


def plot_animated_worm_graph(points_progression):
    """Plot animated worm graph showing points progression with smooth curves."""
    participants = list(points_progression.keys())
    num_matches = len(next(iter(points_progression.values())))  # assumes equal length

    colorscale = px.colors.qualitative.G10
    color_map = {participants[i]: colorscale[i % len(colorscale)] for i in range(len(participants))}

    fig = go.Figure()

    for participant in participants:
        fig.add_trace(go.Scatter(
            x=[], y=[], mode='lines', name=participant,
            line=dict(color=color_map[participant], width=2),
            line_shape='spline'
        ))

    frames = []
    for i in range(0, num_matches + 2):
        frame_data = []
        for participant in participants:
            x_vals = list(range(i))
            y_vals = points_progression[participant][:i]
            frame_data.append(go.Scatter(
                x=x_vals,
                y=y_vals
            ))
        frames.append(go.Frame(data=frame_data, name=str(i)))

    fig.frames = frames

    y_max = max(max(points) for points in points_progression.values())
    x_max = num_matches

    fig.update_layout(
        title="Points Progression Over Matches",
        xaxis_title="Matches",
        yaxis_title="Points",
        template="plotly_dark",    
        yaxis=dict(range=[0, y_max + 5]),
        xaxis=dict(range=[0, x_max]),
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 500, "redraw": False}, "fromcurrent": True}]
            }]
        }],
        sliders=[{
            "steps": [{
                "method": "animate",
                "args": [[str(i)], {"mode": "immediate", "frame": {"duration": 100}, "transition": {"duration": 0}}],
                "label": f"Match {i}"
            } for i in range(1, num_matches + 1)]
        }]
    )

    return fig


def plot_bar_chart_race(points_progression) :
    """Plot for bar chart race showing points progression."""
    data = []
    for participant, scores in points_progression.items():
        for match, points in enumerate(scores):
            data.append({"Participant": participant, "Match": match, "Points": points})
    points_progression_df = pd.DataFrame(data)
    points_progression_df["Rank"] = points_progression_df.groupby("Match")["Points"].rank(method="first", ascending=False)
    points_progression_df.sort_values(by=["Match", "Rank"], inplace=True)
    # st.write(points_progression_df.to_html(index=False), unsafe_allow_html=True)

    fig = px.bar(points_progression_df, 
                 orientation="h",
                 x="Points",
                 y="Participant",
                color="Participant",    
                # range_x=[0, points_progression_df["Points"].max() + 10],            
                 color_discrete_sequence=px.colors.qualitative.Set1,
                 title="Points Progression",
                 animation_frame="Match")
    
    fig.update_layout(
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "Play",
                "method": "animate",
                "args": [None, {
                    "frame": {"duration": 1500, "redraw": False},   # Slower animation (1000ms per frame)
                    "fromcurrent": True,
                    "transition": {"duration": 5000}
                }]
            }]
        }]
    )
    
    fig.update_layout(template="plotly_dark", yaxis={"categoryorder": "total ascending"}, )


    return fig



def plot_time_spent_position(time_spent_position_df):
    all_ranks = pd.Series(range(1, 12), name="Rank")

    participants = time_spent_position_df['Participant'].unique()

    colorscale = px.colors.qualitative.Bold
    color_map = {participants[i]: colorscale[i % len(colorscale)] for i in range(len(participants))}

    for participant in time_spent_position_df['Participant'].unique():
        sub_df = time_spent_position_df[time_spent_position_df['Participant'] == participant]
        sub_df = pd.merge(all_ranks, sub_df, on="Rank", how="left").fillna(0)

        x = np.linspace(1, 11, num = 11)

        fig = px.line(
            x = x,
            y = sub_df['Count'],
            line_shape='spline',
            title = f'Time spent by {participant}',
            color_discrete_sequence=[color_map[participant]]
        )

        fig.update_layout(
            xaxis=dict(dtick=1),
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)    

def plot_position_graph(points_progression):
    data = []
    for participant, scores in points_progression.items():
        for match, points in enumerate(scores):
            data.append({"Participant": participant, "Match": match, "Points": points})
    points_progression_df = pd.DataFrame(data)
    points_progression_df = points_progression_df[~points_progression_df["Participant"].isin(["Wanderers", "Homies"])]
    points_progression_df["Rank"] = points_progression_df.groupby("Match")["Points"].rank(method="first", ascending=False)
    fig = px.line(points_progression_df, x="Match", y="Rank", color="Participant", line_shape='spline')
    fig.update_layout(title="Position Graph", xaxis_title="Matches", yaxis_title="Rank", template="plotly_dark")
    fig.update_yaxes(autorange="reversed")
    return fig