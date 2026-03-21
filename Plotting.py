import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from datetime import datetime


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
        title="Average Wins by Teams",
        labels={"value": "Average Wins", "index": "Teams"},
    )
    fig.update_layout(showlegend=False)
    fig.write_image("The Visuals/Average Win Prediction.png", format="png", scale=4)
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

def plot_home_away_ratio(home_away_ratio_counts, steps=20, delay=0.05):
    """Plot the prediction ratio analysis."""
    container = st.empty()

    # Normalize and prepare data
    df = home_away_ratio_counts.copy().reset_index(drop=True)
    max_counts = df["Count"].max()
    df["Home-Away Ratio"] = df["Home-Away Ratio"].astype(str)  # Ensure it's string for consistent display

    # Animate in 'steps' frames
    for step in range(1, steps + 1):
        progress_ratio = step / steps
        df_animated = df.copy()
        df_animated["Animated Count"] = df["Count"] * progress_ratio

        fig = px.bar(
            df_animated,
            x="Home-Away Ratio",
            y="Animated Count",
            color="Home-Away Ratio",
            color_discrete_sequence=px.colors.qualitative.Set1,
            title="Home-Away Ratio Analysis",
            labels={"Animated Count": "Count"},
            range_y=[0, max_counts * 1.1],  # keep scale fixed
        )

        container.plotly_chart(fig, use_container_width=True)
        time.sleep(delay)

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


def plot_animated_worm_graph(points_progression, delay=0.1):
    """Plot animated worm graph showing points progression with smooth curves."""
    container = st.empty()

    participants = list(points_progression.keys())
    num_matches = len(next(iter(points_progression.values())))
    colorscale = px.colors.qualitative.G10
    color_map = {p: colorscale[i % len(colorscale)] for i, p in enumerate(participants)}
    y_max = max(max(v) for v in points_progression.values())

    for frame in range(1, num_matches + 1):
        fig = go.Figure()

        for p in participants:
            x_vals = list(range(frame))
            y_vals = points_progression[p][:frame]
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name=p,
                line=dict(color=color_map[p], width=3),
                marker=dict(size=6),
                line_shape='spline'
            ))

        fig.update_layout(
            title="📊 Points Progression",
            xaxis_title="Matches",
            yaxis_title="Points",
            yaxis=dict(range=[0, y_max + 5]),
            xaxis=dict(range=[0, num_matches]),
            template="plotly_dark",
            showlegend=True,
            transition=dict(duration=200, easing="cubic-in-out")  # smoother slide
        )

        container.plotly_chart(fig, use_container_width=True)
        time.sleep(delay)

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
    fig.write_image("The Visuals/position_graph.png", format="png", scale=4)
    return fig


def plot_streak_heatmap(leaderboard_df):
    """Heatmap comparing win/loss streaks across all participants."""
    df = leaderboard_df[["Participant", "Longest Winning Streak", "Longest Losing Streak"]].copy()
    df = df.sort_values("Longest Winning Streak", ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="🔥 Win Streak",
        x=df["Participant"],
        y=df["Longest Winning Streak"],
        marker_color="#22c55e",
        text=df["Longest Winning Streak"],
        textposition="auto",
    ))

    fig.add_trace(go.Bar(
        name="❄️ Loss Streak",
        x=df["Participant"],
        y=df["Longest Losing Streak"],
        marker_color="#ef4444",
        text=df["Longest Losing Streak"],
        textposition="auto",
    ))

    fig.update_layout(
        barmode="group",
        title="🏆 Longest Win & Loss Streaks",
        xaxis_title="Participant",
        yaxis_title="Streak Length (Matches)",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_h2h_comparison(h2h_df, p1, p2):
    """Dual line chart showing cumulative points for two participants in H2H."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=h2h_df["Match #"],
        y=h2h_df[f"{p1} Cumulative"],
        mode="lines+markers",
        name=p1,
        line=dict(width=3, shape="spline"),
        marker=dict(size=5),
    ))

    fig.add_trace(go.Scatter(
        x=h2h_df["Match #"],
        y=h2h_df[f"{p2} Cumulative"],
        mode="lines+markers",
        name=p2,
        line=dict(width=3, shape="spline"),
        marker=dict(size=5),
    ))

    fig.update_layout(
        title=f"📈 Cumulative Points: {p1} vs {p2}",
        xaxis_title="Match #",
        yaxis_title="Cumulative Points",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def generate_leaderboard_card(leaderboard_df, output_path="The Visuals/leaderboard_card.png"):
    """
    Generate a high-quality, dark-themed leaderboard summary image.
    Includes a top-3 podium section and a full ranked leaderboard table.
    Saved to output_path and returned as bytes for Streamlit download.
    """
    BG        = "#0e1117"
    CARD_BG   = "#1a1d27"
    ACCENT    = "#262b3d"
    TEXT      = "#f0f2f6"
    SUBTEXT   = "#8b96b0"
    GOLD      = "#FFD700"
    SILVER    = "#C0C0C0"
    BRONZE    = "#CD7F32"
    GREEN     = "#22c55e"
    RED       = "#ef4444"

    medal_colors  = [GOLD, SILVER, BRONZE]
    medal_labels  = ["#1  GOLD", "#2  SILVER", "#3  BRONZE"]
    podium_bg     = ["#2a2200", "#1e1e1e", "#211408"]
    podium_border = [GOLD, SILVER, BRONZE]

    # ── Sort and prepare data ──────────────────────────────────────────────
    lb = leaderboard_df.sort_values("Rank").reset_index(drop=True)
    top3 = lb[lb["Rank"] <= 3].head(3)

    # Strip HTML from Last 5 (just use the text representations)
    def safe_str(val):
        """Return a plain-text version of any value."""
        import re
        return re.sub(r"<[^>]+>", "", str(val)).strip() if val else ""

    last5_raw = lb.get("Last 5 Matches", pd.Series([""] * len(lb)))
    accuracies = lb.get("Accuracy (%)", pd.Series([0.0] * len(lb)))
    streaks_w  = lb.get("Longest Winning Streak", pd.Series([0] * len(lb)))
    streaks_l  = lb.get("Longest Losing Streak", pd.Series([0] * len(lb)))

    # ── Figure setup ──────────────────────────────────────────────────────
    n_rows  = len(lb)
    fig_h   = 4.0 + 0.42 * n_rows   # dynamic height
    fig, ax = plt.subplots(figsize=(16, fig_h), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")

    total_h = 1.0   # normalized height canvas
    y_cursor = 0.99  # starts near top

    # ── Title ─────────────────────────────────────────────────────────────
    title_h = 0.072
    fig.text(0.5, y_cursor - title_h * 0.45,
             "IPL Prediction Game 2025  |  Leaderboard",
             ha="center", va="center", fontsize=26, fontweight="bold",
             color=TEXT, fontfamily="DejaVu Sans")
    fig.text(0.5, y_cursor - title_h * 0.85,
             f"Generated  {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
             ha="center", va="center", fontsize=11, color=SUBTEXT)
    y_cursor -= title_h + 0.01

    # ── Podium Cards (top 3) ───────────────────────────────────────────────
    podium_h   = 0.20
    card_w     = 0.27
    card_gap   = 0.025
    start_x    = 0.5 - (3 * card_w + 2 * card_gap) / 2

    for i, (_, row) in enumerate(top3.iterrows()):
        cx = start_x + i * (card_w + card_gap)
        cy = y_cursor - podium_h

        # Card background
        card = FancyBboxPatch((cx, cy), card_w, podium_h,
                              boxstyle="round,pad=0.01",
                              facecolor=podium_bg[i],
                              edgecolor=podium_border[i],
                              linewidth=2.5,
                              transform=fig.transFigure, clip_on=False)
        fig.add_artist(card)

        cx_mid = cx + card_w / 2

        fig.text(cx_mid, cy + podium_h * 0.82,
                 medal_labels[i], ha="center", va="center",
                 fontsize=15, color=medal_colors[i], fontweight="bold",
                 transform=fig.transFigure)
        fig.text(cx_mid, cy + podium_h * 0.57,
                 row["Participant"], ha="center", va="center",
                 fontsize=17, fontweight="bold", color=TEXT,
                 transform=fig.transFigure)
        fig.text(cx_mid, cy + podium_h * 0.36,
                 f"{int(row['Points'])} pts",
                 ha="center", va="center",
                 fontsize=22, fontweight="black", color=medal_colors[i],
                 transform=fig.transFigure)
        accuracy = accuracies.iloc[i] if i < len(accuracies) else 0
        correct  = int(row.get("Correct Predictions", 0))
        fig.text(cx_mid, cy + podium_h * 0.14,
                 f"{accuracy:.1f}% accuracy  ·  {correct} correct",
                 ha="center", va="center",
                 fontsize=10, color=SUBTEXT, transform=fig.transFigure)

    y_cursor -= podium_h + 0.025

    # ── Full Leaderboard Table ─────────────────────────────────────────────
    col_labels  = ["Rank", "Participant", "Points", "Accuracy", "Last 5", "W-Streak", "L-Streak"]
    col_widths  = [0.06,    0.18,          0.09,     0.10,       0.25,     0.09,        0.09     ]
    col_aligns  = ["center","left",        "center", "center",   "left",   "center",    "center"  ]
    row_h       = 0.048

    # Header
    x_starts = [0.03]
    for w in col_widths[:-1]:
        x_starts.append(x_starts[-1] + w)

    # Header background
    hdr_bg = FancyBboxPatch((0.02, y_cursor - row_h), 0.96, row_h,
                             boxstyle="round,pad=0.005",
                             facecolor=ACCENT, edgecolor="none",
                             transform=fig.transFigure, clip_on=False)
    fig.add_artist(hdr_bg)

    for j, (label, xs, al) in enumerate(zip(col_labels, x_starts, col_aligns)):
        tx = xs if al == "left" else xs + col_widths[j] / 2
        fig.text(tx, y_cursor - row_h * 0.5,
                 label, ha=al, va="center",
                 fontsize=11, fontweight="bold", color=SUBTEXT,
                 transform=fig.transFigure)

    y_cursor -= row_h + 0.004

    # Rows
    for idx, row in lb.iterrows():
        rank      = int(row["Rank"])
        bg_color  = "#1c1f2e" if idx % 2 == 0 else CARD_BG

        row_rect = FancyBboxPatch((0.02, y_cursor - row_h), 0.96, row_h,
                                  boxstyle="round,pad=0.003",
                                  facecolor=bg_color, edgecolor="none",
                                  transform=fig.transFigure, clip_on=False)
        fig.add_artist(row_rect)

        # Rank badge color
        if rank == 1:   rank_col = GOLD
        elif rank == 2: rank_col = SILVER
        elif rank == 3: rank_col = BRONZE
        else:           rank_col = TEXT

        last5_str = safe_str(lb.at[idx, "Last 5 Matches"]) if "Last 5 Matches" in lb.columns else ""
        # Replace emoji with plain text equivalents (emoji fonts not available in matplotlib)
        last5_str = (
            last5_str
            .replace("\u2705", "W")   # ✅ -> W
            .replace("\u274c", "L")   # ❌ -> L
            .replace("\u2796", "D")   # ➖ -> D (draw / NR)
            .replace("\u2764", "-")
        )
        accuracy_val = accuracies.iloc[idx] if idx < len(accuracies) else 0
        wstreak = int(streaks_w.iloc[idx]) if idx < len(streaks_w) else 0
        lstreak = int(streaks_l.iloc[idx]) if idx < len(streaks_l) else 0

        row_data = [
            (str(rank),                   rank_col,  col_aligns[0]),
            (str(row["Participant"]),      TEXT,      col_aligns[1]),
            (str(int(row["Points"])),      TEXT,      col_aligns[2]),
            (f"{accuracy_val:.1f}%",       SUBTEXT,   col_aligns[3]),
            (last5_str,                    TEXT,      col_aligns[4]),
            (str(wstreak),                 GREEN,     col_aligns[5]),
            (str(lstreak),                 RED,       col_aligns[6]),
        ]

        for j, (val, color, align) in enumerate(row_data):
            tx = x_starts[j] if align == "left" else x_starts[j] + col_widths[j] / 2
            fig.text(tx, y_cursor - row_h * 0.5,
                     val, ha=align, va="center",
                     fontsize=11, color=color, fontweight="bold" if j == 0 else "normal",
                     transform=fig.transFigure)

        y_cursor -= row_h + 0.003

    # ── Footer ────────────────────────────────────────────────────────────
    fig.text(0.5, 0.012,
             "IPL Prediction Game 2025  |  Powered by Streamlit",
             ha="center", va="bottom", fontsize=9, color=SUBTEXT,
             transform=fig.transFigure)

    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=180, bbox_inches="tight",
                facecolor=BG, edgecolor="none")

    with open(output_path, "rb") as f:
        img_bytes = f.read()

    plt.close(fig)
    return img_bytes


# ─── New Visuals for Advanced Stats ──────────────────────────────────────────

def plot_team_accuracy_heatmap(matrix_df):
    """Plotly heatmap of Participant × Team accuracy %."""
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Heatmap(
        z=matrix_df.values,
        x=matrix_df.columns,
        y=matrix_df.index,
        colorscale="RdYlGn",
        zmin=0, zmax=100,
        text=matrix_df.round(0).astype(str).values + "%",
        texttemplate="%{text}",
        hoverinfo="x+y+z",
        showscale=True
    ))
    fig.update_layout(
        title="🎯 Team-by-Team Accuracy",
        xaxis_title="Team",
        yaxis_title="Participant",
        template="plotly_dark",
        height=400 + 30 * len(matrix_df),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def plot_match_difficulty(difficulty_df):
    """Horizontal bar chart showing % of participants who got each match right."""
    # Reverse so hardest matches are at the top (lowest % correct)
    df = difficulty_df.sort_values("% Correct", ascending=True).copy()
    
    colors = ["#ef4444" if upset else "#3b82f6" for upset in df["Was Upset"]]
    texts = [f"{c}/{t} ({pct}%)" for c, t, pct in zip(df["Correct"], df["Total"], df["% Correct"])]

    fig = go.Figure(go.Bar(
        x=df["% Correct"],
        y=df["Match"],
        orientation="h",
        marker_color=colors,
        text=texts,
        textposition="auto"
    ))
    fig.update_layout(
        title="🔥 Hardest Matches to Predict (Red = Away team won)",
        xaxis_title="% Correct",
        yaxis_title="Match",
        template="plotly_dark",
        height=300 + 20 * len(df),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(range=[0, 105])
    )
    return fig


def plot_agreement_matrix(agree_df):
    """Symmetric heatmap of participant agreement %."""
    fig = go.Figure(data=go.Heatmap(
        z=agree_df.values,
        x=agree_df.columns,
        y=agree_df.index,
        colorscale="Purples",
        zmin=0, zmax=100,
        text=agree_df.round(0).astype(str).values + "%",
        texttemplate="%{text}",
        hoverinfo="x+y+z",
        showscale=True
    ))
    fig.update_layout(
        title="🤝 Participant Agreement Matrix (% identical picks)",
        xaxis_title="Participant",
        yaxis_title="Participant",
        template="plotly_dark",
        height=400 + 30 * len(agree_df),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def plot_points_distribution(dist_df):
    """Stacked/Grouped bar of 0, 5, 10, 20 pt matches per participant."""
    fig = go.Figure()
    colors = {"0 pts": "#ef4444", "5 pts": "#6b7280", "10 pts": "#3b82f6", "20 pts": "#22c55e"}
    
    for bucket in ["0 pts", "5 pts", "10 pts", "20 pts"]:
        fig.add_trace(go.Bar(
            name=bucket,
            x=dist_df["Participant"],
            y=dist_df[bucket],
            marker_color=colors[bucket],
            text=dist_df[bucket],
            textposition="auto"
        ))
    
    fig.update_layout(
        barmode="stack",
        title="📊 Distribution of Match Scores",
        xaxis_title="Participant",
        yaxis_title="Count of Matches",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_calendar_heatmap(results_df, predictions, schedule_df):
    """Grid of match outcomes: green = majority right, red = majority wrong."""
    completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
    participants = list(predictions.keys())
    
    cells = []
    for i, row in schedule_df.iterrows():
        match_num = int(row.iloc[0])
        idx = match_num - 1
        
        if idx < len(completed):
            actual = completed.iloc[idx]["Winner"]
            if actual == "NR":
                color = "#6b7280"  # Gray
                text = "NR"
            else:
                correct = sum(1 for p in participants if idx < len(predictions[p]) and predictions[p][idx] == actual)
                pct = correct / len(participants)
                color = "#22c55e" if pct >= 0.5 else "#ef4444"
                text = f"{correct}/{len(participants)}"
        else:
            color = "#1f2937"  # Dark gray (not played)
            text = "TBD"
            
        cells.append({
            "Match": match_num,
            "Teams": f"{row.iloc[2][:3]} v {row.iloc[3][:3]}",
            "Color": color,
            "Text": text
        })
        
    df = pd.DataFrame(cells)
    
    # Grid layout: 7 columns (approx 1 week)
    cols = 8
    rows = (len(df) + cols - 1) // cols
    
    z_colors = np.full((rows, cols), np.nan)
    text_grid = np.full((rows, cols), "", dtype=object)
    hover_grid = np.full((rows, cols), "", dtype=object)
    
    # Map colors to numeric for Plotly heatmap
    color_map = {"#1f2937": 0, "#ef4444": 1, "#6b7280": 2, "#22c55e": 3}
    custom_colorscale = [[0, "#1f2937"], [0.33, "#ef4444"], [0.66, "#6b7280"], [1, "#22c55e"]]
    
    for i, r in df.iterrows():
        row_idx = i // cols
        col_idx = i % cols
        z_colors[row_idx, col_idx] = color_map.get(r["Color"], 0)
        text_grid[row_idx, col_idx] = f"<b>M{r['Match']}</b><br>{r['Text']}"
        hover_grid[row_idx, col_idx] = f"Match {r['Match']}<br>{r['Teams']}<br>{r['Text']}"
        
    fig = go.Figure(data=go.Heatmap(
        z=z_colors,
        text=text_grid,
        customdata=hover_grid,
        texttemplate="%{text}",
        hovertemplate="%{customdata}<extra></extra>",
        colorscale=custom_colorscale,
        showscale=False,
        xgap=4, ygap=4
    ))
    
    fig.update_layout(
        title="📅 Season Calendar (Green = Majority Correct, Red = Majority Wrong)",
        template="plotly_dark",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange="reversed"),
        height=100 * rows,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def plot_personality_cards(advanced_df):
    """Return HTML string for the personality cards."""
    html = '<div style="display: flex; flex-wrap: wrap; gap: 20px;">'
    
    personas = [
        {"title": "The Lone Wolf", "metric": "Best Solo Match", "desc": "Scored big when no one else did", "icon": "🐺"},
        {"title": "The Contrarian", "metric": "Contrarian Index (%)", "desc": "Highest % going successfully against the grain", "icon": "🔥", "sort": False},
        {"title": "The Sheep", "metric": "Crowd Follower (%)", "desc": "Always picked with the majority", "icon": "🐑", "sort": False},
        {"title": "The Clutch Player", "metric": "Clutch Rate (%)", "desc": "Most accurate on the tight 50/50 split games", "icon": "🎯", "sort": False},
    ]
    
    for p in personas:
        if p["metric"] in advanced_df.columns:
            if "sort" in p:
                winner_row = advanced_df.sort_values(p["metric"], ascending=p["sort"]).iloc[0]
                val = f"{winner_row[p['metric']]:.1f}%"
            else:
                # Find someone with an actual match, not "—"
                valid = advanced_df[advanced_df[p["metric"]] != "—"]
                if not valid.empty:
                    winner_row = valid.iloc[0]
                    val = winner_row[p["metric"]]
                else:
                    winner_row = advanced_df.iloc[0]
                    val = "None"
                    
            html += (
                f'<div style="flex: 1; min-width: 250px; background: rgba(124,92,255,0.1); border: 1px solid rgba(124,92,255,0.3); border-radius: 12px; padding: 20px;">'
                f'<h3 style="margin: 0 0 10px 0; font-size: 1.2rem; color: #e2e8ff;">{p["icon"]} {p["title"]}</h3>'
                f'<h2 style="margin: 0 0 5px 0; color: #a78bfa; font-size: 1.8rem;">{winner_row["Participant"]}</h2>'
                f'<div style="font-size: 1.1rem; font-weight: bold; color: #fff;">{val}</div>'
                f'<div style="font-size: 0.85rem; color: #8b93b8; margin-top: 8px;">{p["desc"]}</div>'
                f'</div>'
            )
            
    html += '</div>'
    return html