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
    """Plotly heatmap of Time Spent in Each Position."""
    import plotly.graph_objects as go
    
    df_pivot = time_spent_position_df.pivot(index='Participant', columns='Rank', values='Count').fillna(0)
    all_ranks = sorted(df_pivot.columns)
    df_pivot = df_pivot[all_ranks]
    
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale="Viridis",
        text=df_pivot.values,
        texttemplate="%{text}",
        hoverinfo="x+y+z",
        showscale=True
    ))
    
    fig.update_layout(
        title="⏱️ Time Spent in Each Position",
        xaxis_title="Rank",
        yaxis_title="Participant",
        xaxis=dict(dtick=1),
        template="plotly_dark",
        height=400 + 30 * len(df_pivot),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def plot_time_spent_position_line(time_spent_position_df):
    """Plotly smooth multi-line graph of Time Spent in Each Position."""
    import plotly.express as px
    
    df_pivot = time_spent_position_df.pivot(index='Participant', columns='Rank', values='Count').fillna(0)
    all_ranks = sorted(df_pivot.columns)
    df_pivot = df_pivot[all_ranks]
    df_melt = df_pivot.reset_index().melt(id_vars='Participant', value_vars=all_ranks, var_name='Rank', value_name='Count')
    
    fig = px.line(
        df_melt,
        x='Rank',
        y='Count',
        color='Participant',
        line_shape='spline',
        title="📈 Time Spent in Each Position (Line Graph)",
        color_discrete_sequence=px.colors.qualitative.G10
    )
    
    fig.update_layout(
        xaxis_title="Rank",
        yaxis_title="Matches",
        xaxis=dict(dtick=1),
        template="plotly_dark",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

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


def generate_leaderboard_card(leaderboard_df, output_path="The Visuals/leaderboard_card.png", total_matches=0):
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
    last5_pts = lb.get("Matchwise Points (Last 5)", pd.Series([[]] * len(lb)))
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

    # ── Title & Header ────────────────────────────────────────────────────
    # Main Header Text
    fig.text(0.02, y_cursor - 0.03, "IPL Prediction Dashboard 2026", 
             fontsize=28, fontweight="bold", color=TEXT, fontfamily="DejaVu Sans", ha="left")

    # Badge
    badge = FancyBboxPatch((0.025, y_cursor - 0.080), 0.16, 0.025,
                           boxstyle="round,pad=0.005", facecolor="#2c1f38", edgecolor="#4e336b",
                           transform=fig.transFigure, clip_on=False)
    fig.add_artist(badge)
    fig.text(0.03, y_cursor - 0.067, "Niharika \u2014 Defending Champion", fontsize=10, color="#b29ee3", fontweight="bold")
    
    # ── KPIs ───────────────────────────────────────────────────────────────
    if len(lb) > 0:
        leader_name = lb.iloc[0]["Participant"]
        leader_pts  = f"{int(lb.iloc[0]['Points'])} pts"
    else:
        leader_name, leader_pts = "-", "-"
    
    parts   = f"{len(lb)}"
    avg_acc = f"{accuracies.mean() if len(accuracies) > 0 else 0:.1f}%"
    
    # KPI 1. Leader
    fig.text(0.025, y_cursor - 0.15, "LEADER", fontsize=10, color=SUBTEXT, fontweight="bold")
    fig.text(0.025, y_cursor - 0.175, leader_name, fontsize=18, color=TEXT, fontweight="bold")
    fig.text(0.025, y_cursor - 0.198, leader_pts, fontsize=11, color=GREEN)

    # KPI 2. Matches
    fig.text(0.30, y_cursor - 0.15, "MATCHES PLAYED", fontsize=10, color=SUBTEXT, fontweight="bold")
    fig.text(0.30, y_cursor - 0.175, str(total_matches), fontsize=18, color=TEXT, fontweight="bold")
    fig.text(0.30, y_cursor - 0.198, "of 74 league", fontsize=11, color=GREEN)

    # KPI 3. Participants
    fig.text(0.58, y_cursor - 0.15, "PARTICIPANTS", fontsize=10, color=SUBTEXT, fontweight="bold")
    fig.text(0.58, y_cursor - 0.175, parts, fontsize=18, color=TEXT, fontweight="bold")
    
    # KPI 4. Avg Accuracy
    fig.text(0.80, y_cursor - 0.15, "AVG ACCURACY", fontsize=10, color=SUBTEXT, fontweight="bold")
    fig.text(0.80, y_cursor - 0.175, avg_acc, fontsize=18, color=TEXT, fontweight="bold")

    y_cursor -= 0.25

    # ── Full Leaderboard Table ─────────────────────────────────────────────
    col_labels  = ["Rank", "Pos", "Participant", "Points", "Accuracy", "Last 5 Form", "Last 5 Pts", "W-Str", "L-Str"]
    col_widths  = [0.055,   0.05,  0.14,          0.08,     0.09,       0.18,          0.12,         0.075,   0.075  ]
    col_aligns  = ["center","center","left",      "center", "center",   "left",        "left",       "center", "center"]
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

        # Extract Last 5 Points (using regex to strip HTML and space out)
        vals = last5_pts.iloc[idx] if idx < len(last5_pts) else ""
        import re
        pts_str = "  ".join(re.findall(r">(\d+)<", str(vals)))

        # Position delta coloring
        pos_delta = str(lb.at[idx, "Pos \u0394"]) if "Pos \u0394" in lb.columns else "\u2014"
        if pos_delta.startswith("\u25b2"):  pos_col = GREEN
        elif pos_delta.startswith("\u25bc"): pos_col = RED
        else:                               pos_col = SUBTEXT

        row_data = [
            (str(rank),                   rank_col,  col_aligns[0]),
            (pos_delta,                   pos_col,   col_aligns[1]),
            (str(row["Participant"]),      TEXT,      col_aligns[2]),
            (str(int(row["Points"])),      TEXT,      col_aligns[3]),
            (f"{accuracy_val:.1f}%",       SUBTEXT,   col_aligns[4]),
            (last5_str,                    TEXT,      col_aligns[5]),
            (pts_str,                      TEXT,      col_aligns[6]),
            (str(wstreak),                 GREEN,     col_aligns[7]),
            (str(lstreak),                 RED,       col_aligns[8]),
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
             "IPL Prediction Game 2026",
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
    """Stacked bar of 0, 5, 10-14, 15+ pt matches per participant."""
    # Sort participants from least losses to most losses
    dist_df = dist_df.sort_values("0 pts", ascending=True).reset_index(drop=True)
    fig = go.Figure()
    colors = {"0 pts": "#ef4444", "5 pts": "#6b7280", "10-14 pts": "#3b82f6", "15+ pts": "#22c55e"}
    
    for bucket in ["0 pts", "5 pts", "10-14 pts", "15+ pts"]:
        if bucket not in dist_df.columns:
            continue
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


def plot_stadium_map(stadium_df, user_name):
    """Plot an interactive map of India showing stadium wins/losses for a specific predictor."""
    # Create an artificial min-size to ensure 0-win stadiums still appear as a small dot
    stadium_df["Bubble Size"] = stadium_df["Wins"].astype(float) + 0.1
    
    fig = px.scatter_mapbox(
        stadium_df, 
        lat="Lat", 
        lon="Lon", 
        hover_name="Stadium",
        size="Bubble Size",
        color="Win %",
        color_continuous_scale="Viridis",
        hover_data={
            "Lat": False,
            "Lon": False,
            "Bubble Size": False,
            "City": True,
            "Wins": True,
            "Losses": True,
            "Win %": ":.1f"
        },
        zoom=3.8, 
        center={"lat": 22.0, "lon": 79.0},
        height=600
    )
    
    fig.update_layout(
        title=f"🗺️ {user_name}'s Stadium Luck Map",
        mapbox_style="carto-darkmatter",
        template="plotly_dark",
        margin=dict(l=10, r=10, t=50, b=10),
        coloraxis_colorbar=dict(title="Win %")
    )
    
    return fig


def plot_stadium_points_map(stadium_df, user_name):
    """Map sized by total Points earned per stadium, colored by Pts/Match efficiency."""
    stadium_df = stadium_df.copy()
    # Give 0-point stadiums a small dot to stay visible
    stadium_df["Bubble Size"] = stadium_df["Points"].astype(float) + 0.1

    fig = px.scatter_mapbox(
        stadium_df,
        lat="Lat",
        lon="Lon",
        hover_name="Stadium",
        size="Bubble Size",
        color="Pts/Match",
        color_continuous_scale="RdYlGn",
        hover_data={
            "Lat": False,
            "Lon": False,
            "Bubble Size": False,
            "City": True,
            "Points": True,
            "Wins": True,
            "Losses": True,
            "Pts/Match": ":.1f"
        },
        zoom=3.8,
        center={"lat": 22.0, "lon": 79.0},
        height=600
    )

    fig.update_layout(
        title=f"💰 {user_name}'s Points Earned by Stadium",
        mapbox_style="carto-darkmatter",
        template="plotly_dark",
        margin=dict(l=10, r=10, t=50, b=10),
        coloraxis_colorbar=dict(title="Pts/Match")
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  PERSONALIZED PLAYER REPORT CARD
# ═══════════════════════════════════════════════════════════════════════════════

def generate_player_report_card(report_data, output_path="report.png"):
    """
    Render a beautiful, tall infographic (1080×1920) as a dark-themed PNG.
    `report_data` is the dict returned by ExtractAndTransform.get_player_report_data().
    Returns the image as bytes.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch
    import numpy as np
    import textwrap
    import re

    def strip_emoji(text):
        """Remove emoji characters that DejaVu Sans can't render."""
        emoji_pattern = re.compile(
            "[\U0001F300-\U0001FAFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F"
            "\U0000200D\U00002640-\U00002642\U00002600-\U000027BF\U0001F900-\U0001F9FF]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text).strip()

    # ── Color Palette ────────────────────────────────────────────────────────
    BG         = "#0e1117"
    CARD_BG    = "#151822"
    CARD_BG2   = "#1a1f2e"
    ACCENT     = "#262b3d"
    PURPLE     = "#7c5cff"
    PURPLE_L   = "#a78bfa"
    PURPLE_D   = "#4e336b"
    TEXT       = "#f0f2f6"
    SUBTEXT    = "#8b96b0"
    DIM        = "#5a6078"
    GOLD       = "#FFD700"
    SILVER     = "#C0C0C0"
    BRONZE     = "#CD7F32"
    GREEN      = "#22c55e"
    RED        = "#ef4444"
    BLUE       = "#3b82f6"
    ORANGE_A   = "#f97316"

    d = report_data  # shorthand

    # ── Canvas Setup ─────────────────────────────────────────────────────────
    fig_w, fig_h = 10.8, 24.5  # Tall canvas — exactly fits all sections
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=BG, dpi=100)
    ax_main = fig.add_axes([0, 0, 1, 1])
    ax_main.set_xlim(0, fig_w)
    ax_main.set_ylim(0, fig_h)
    ax_main.set_facecolor(BG)
    ax_main.axis("off")

    # Helper to draw rounded cards
    def draw_card(x, y, w, h, color=CARD_BG, radius=0.25, border_color=None):
        card = FancyBboxPatch((x, y), w, h,
                              boxstyle=f"round,pad={radius}",
                              facecolor=color,
                              edgecolor=border_color or "none",
                              linewidth=1.5,
                              transform=ax_main.transData, clip_on=False)
        ax_main.add_patch(card)
        return card

    y = fig_h  # start from top

    # ═══ SECTION 1: HEADER ═══════════════════════════════════════════════════
    header_h = 3.2
    y -= header_h

    # Header gradient card
    draw_card(0.3, y, fig_w - 0.6, header_h - 0.15,
              color="#12101f", border_color=PURPLE_D, radius=0.3)

    # Decorative gradient circle (top-right)
    circle1 = plt.Circle((fig_w - 1.5, y + header_h - 0.8), 1.2,
                          color=PURPLE, alpha=0.08, transform=ax_main.transData)
    ax_main.add_patch(circle1)
    circle2 = plt.Circle((1.5, y + 0.5), 0.8,
                          color=ORANGE_A, alpha=0.06, transform=ax_main.transData)
    ax_main.add_patch(circle2)

    # Rank medal
    medal_map = {1: ("🥇", GOLD), 2: ("🥈", SILVER), 3: ("🥉", BRONZE)}
    medal_emoji, medal_color = medal_map.get(d["rank"], ("", SUBTEXT))

    # Title: "IPL 2026 · SEASON REPORT"
    ax_main.text(0.6, y + header_h - 0.65, "IPL 2026  ·  SEASON REPORT",
                 fontsize=11, fontweight="bold", color=SUBTEXT,
                 fontfamily="DejaVu Sans", ha="left", va="center")

    # Player Name (large)
    ax_main.text(0.6, y + header_h - 1.35, d["participant"],
                 fontsize=36, fontweight="bold", color=TEXT,
                 fontfamily="DejaVu Sans", ha="left", va="center")

    # Rank + Badge line
    rank_text = f"Rank #{d['rank']} of {d['total_participants']}"
    ax_main.text(0.6, y + header_h - 2.0, rank_text,
                 fontsize=16, fontweight="bold", color=medal_color if d["rank"] <= 3 else PURPLE_L,
                 fontfamily="DejaVu Sans", ha="left", va="center")

    # Personality badge
    badge_title, badge_desc = d["primary_badge"]
    badge_clean = strip_emoji(badge_title)
    # Badge pill
    draw_card(0.5, y + 0.25, 5.5, 0.65, color=PURPLE_D, border_color=PURPLE, radius=0.15)
    ax_main.text(0.7, y + 0.57, f"{badge_clean}  //  {badge_desc}",
                 fontsize=11, fontweight="bold", color=PURPLE_L,
                 fontfamily="DejaVu Sans", ha="left", va="center")

    y -= 0.25

    # ═══ SECTION 2: KPI STRIP ════════════════════════════════════════════════
    kpi_h = 1.6
    y -= kpi_h

    kpis = [
        ("POINTS", str(d["points"]), GOLD if d["rank"] == 1 else TEXT),
        ("ACCURACY", f"{d['accuracy']:.1f}%", PURPLE_L),
        ("CORRECT", str(d["correct"]), GREEN),
        ("WRONG", str(d["wrong"]), RED),
        ("BONUS", str(d["bonus_pts"]), ORANGE_A),
    ]

    kpi_w = (fig_w - 0.6 - 0.3 * (len(kpis) - 1)) / len(kpis)
    for i, (label, value, color) in enumerate(kpis):
        kx = 0.3 + i * (kpi_w + 0.3)
        draw_card(kx, y, kpi_w, kpi_h - 0.1, color=CARD_BG, radius=0.15)
        ax_main.text(kx + kpi_w / 2, y + kpi_h - 0.45, label,
                     fontsize=9, fontweight="bold", color=DIM,
                     ha="center", va="center", fontfamily="DejaVu Sans")
        ax_main.text(kx + kpi_w / 2, y + 0.45, value,
                     fontsize=22, fontweight="bold", color=color,
                     ha="center", va="center", fontfamily="DejaVu Sans")

    y -= 0.3

    # ═══ SECTION 3: POINTS JOURNEY SPARKLINE ═════════════════════════════════
    spark_h = 2.4
    y -= spark_h

    draw_card(0.3, y, fig_w - 0.6, spark_h - 0.1, color=CARD_BG, radius=0.2)

    ax_main.text(0.6, y + spark_h - 0.4, "POINTS JOURNEY",
                 fontsize=10, fontweight="bold", color=SUBTEXT,
                 ha="left", va="center", fontfamily="DejaVu Sans")

    # Embed a mini axes for the sparkline
    spark_left = 0.07
    spark_bottom = (y + 0.3) / fig_h
    spark_width = 0.86
    spark_height_frac = (spark_h - 0.9) / fig_h

    ax_spark = fig.add_axes([spark_left, spark_bottom, spark_width, spark_height_frac])
    ax_spark.set_facecolor("none")

    prog = d["progression"]
    x_vals = list(range(len(prog)))
    ax_spark.fill_between(x_vals, prog, alpha=0.15, color=PURPLE)
    ax_spark.plot(x_vals, prog, color=PURPLE_L, linewidth=2.5, solid_capstyle="round")
    ax_spark.scatter([len(prog) - 1], [prog[-1]], color=GOLD if d["rank"] == 1 else PURPLE_L,
                     s=50, zorder=5, edgecolors=TEXT, linewidths=1)

    ax_spark.set_xlim(0, max(len(prog) - 1, 1))
    ax_spark.set_ylim(0, max(prog) * 1.1 if max(prog) > 0 else 10)
    ax_spark.tick_params(colors=DIM, labelsize=7)
    ax_spark.spines["top"].set_visible(False)
    ax_spark.spines["right"].set_visible(False)
    ax_spark.spines["left"].set_color(ACCENT)
    ax_spark.spines["bottom"].set_color(ACCENT)
    ax_spark.set_xlabel("Match #", fontsize=8, color=DIM)

    y -= 0.25

    # ═══ SECTION 4: PERFORMANCE DNA RADAR ════════════════════════════════════
    radar_h = 3.4
    y -= radar_h

    draw_card(0.3, y, fig_w - 0.6, radar_h - 0.1, color=CARD_BG, radius=0.2)

    ax_main.text(0.6, y + radar_h - 0.4, "PERFORMANCE DNA",
                 fontsize=10, fontweight="bold", color=SUBTEXT,
                 ha="left", va="center", fontfamily="DejaVu Sans")

    # Radar chart embedded axes
    radar_center_x = 0.5
    radar_center_y = (y + 0.2) / fig_h
    radar_size = (radar_h - 0.9) / fig_h

    ax_radar = fig.add_axes(
        [radar_center_x - radar_size * 0.65,
         radar_center_y,
         radar_size * 1.3,
         radar_size],
        polar=True
    )
    ax_radar.set_facecolor("none")

    categories = list(d["radar"].keys())
    values = list(d["radar"].values())
    N = len(categories)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += [angles[0]]

    ax_radar.fill(angles, values_plot, color=PURPLE, alpha=0.18)
    ax_radar.plot(angles, values_plot, color=PURPLE_L, linewidth=2.5)
    ax_radar.scatter(angles[:-1], values, color=PURPLE_L, s=40, zorder=5)

    ax_radar.set_thetagrids(np.degrees(angles[:-1]), categories,
                            fontsize=9, fontweight="bold", color=SUBTEXT)
    ax_radar.set_ylim(0, 100)
    ax_radar.set_yticks([25, 50, 75, 100])
    ax_radar.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color=DIM)
    ax_radar.spines["polar"].set_color(ACCENT)
    ax_radar.grid(color=ACCENT, linewidth=0.5)
    ax_radar.tick_params(colors=DIM)

    y -= 0.25

    # ═══ SECTION 5: TEAM LOYALTY ═════════════════════════════════════════════
    team_h = 3.0
    y -= team_h

    draw_card(0.3, y, fig_w - 0.6, team_h - 0.1, color=CARD_BG, radius=0.2)

    ax_main.text(0.6, y + team_h - 0.4, "TEAM LOYALTY",
                 fontsize=10, fontweight="bold", color=SUBTEXT,
                 ha="left", va="center", fontfamily="DejaVu Sans")

    # Embed bar chart axes
    bar_left = 0.08
    bar_bottom = (y + 0.25) / fig_h
    bar_width = 0.84
    bar_height_frac = (team_h - 0.9) / fig_h

    ax_team = fig.add_axes([bar_left, bar_bottom, bar_width, bar_height_frac])
    ax_team.set_facecolor("none")

    ta = d["team_analysis"]
    teams_sorted = sorted(ta.keys(), key=lambda t: ta[t]["predicted"], reverse=True)
    team_labels = [team_initials.get(t, t[:3]) for t in teams_sorted]
    pred_vals = [ta[t]["predicted"] for t in teams_sorted]
    colors_bar = [team_colors.get(t, PURPLE) for t in teams_sorted]

    bars = ax_team.barh(range(len(teams_sorted)), pred_vals, color=colors_bar, height=0.6, alpha=0.85)
    ax_team.set_yticks(range(len(teams_sorted)))
    ax_team.set_yticklabels(team_labels, fontsize=8, fontweight="bold", color=SUBTEXT)
    ax_team.invert_yaxis()
    ax_team.set_xlabel("Times Predicted to Win", fontsize=8, color=DIM)
    ax_team.tick_params(colors=DIM, labelsize=7)
    ax_team.spines["top"].set_visible(False)
    ax_team.spines["right"].set_visible(False)
    ax_team.spines["left"].set_color(ACCENT)
    ax_team.spines["bottom"].set_color(ACCENT)

    # Add count labels
    for i, (bar, val) in enumerate(zip(bars, pred_vals)):
        ax_team.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                     str(val), fontsize=8, fontweight="bold", color=TEXT,
                     va="center")

    y -= 0.25

    # ═══ SECTION 6: STREAKS & HIGHLIGHTS ═════════════════════════════════════
    streak_h = 1.7
    y -= streak_h

    # Two side-by-side cards
    half_w = (fig_w - 0.9) / 2

    # Win streak card
    draw_card(0.3, y, half_w, streak_h - 0.1, color="#0f1a12", border_color="#1a3d1f", radius=0.15)
    ax_main.text(0.55, y + streak_h - 0.35, "BEST WIN STREAK",
                 fontsize=9, fontweight="bold", color=GREEN, ha="left", va="center",
                 fontfamily="DejaVu Sans")
    ax_main.text(0.55, y + streak_h * 0.45, str(d["longest_win_streak"]),
                 fontsize=32, fontweight="bold", color=GREEN, ha="left", va="center",
                 fontfamily="DejaVu Sans")
    ax_main.text(0.55 + 1.2, y + streak_h * 0.45, "matches",
                 fontsize=11, color=SUBTEXT, ha="left", va="center",
                 fontfamily="DejaVu Sans")
    if d["winning_period"]:
        period_text = d["winning_period"].replace(", 2026", "")
        ax_main.text(0.55, y + 0.25, period_text,
                     fontsize=8, color=DIM, ha="left", va="center",
                     fontfamily="DejaVu Sans")

    # Loss streak card
    loss_x = 0.3 + half_w + 0.3
    draw_card(loss_x, y, half_w, streak_h - 0.1, color="#1a0f0f", border_color="#3d1a1a", radius=0.15)
    ax_main.text(loss_x + 0.25, y + streak_h - 0.35, "WORST LOSS STREAK",
                 fontsize=9, fontweight="bold", color=RED, ha="left", va="center",
                 fontfamily="DejaVu Sans")
    ax_main.text(loss_x + 0.25, y + streak_h * 0.45, str(d["longest_loss_streak"]),
                 fontsize=32, fontweight="bold", color=RED, ha="left", va="center",
                 fontfamily="DejaVu Sans")
    ax_main.text(loss_x + 0.25 + 1.2, y + streak_h * 0.45, "matches",
                 fontsize=11, color=SUBTEXT, ha="left", va="center",
                 fontfamily="DejaVu Sans")
    if d["losing_period"]:
        period_text = d["losing_period"].replace(", 2026", "")
        ax_main.text(loss_x + 0.25, y + 0.25, period_text,
                     fontsize=8, color=DIM, ha="left", va="center",
                     fontfamily="DejaVu Sans")

    y -= 0.25

    # ═══ SECTION 7: STADIUMS ═════════════════════════════════════════════════
    stadium_h = 1.2
    y -= stadium_h

    draw_card(0.3, y, fig_w - 0.6, stadium_h - 0.1, color=CARD_BG, radius=0.15)

    ax_main.text(0.6, y + stadium_h - 0.35, "STADIUMS",
                 fontsize=10, fontweight="bold", color=SUBTEXT,
                 ha="left", va="center", fontfamily="DejaVu Sans")

    ax_main.text(0.6, y + 0.4, "Lucky:",
                 fontsize=10, fontweight="bold", color=GREEN,
                 ha="left", va="center", fontfamily="DejaVu Sans")
    ax_main.text(1.8, y + 0.4, d["lucky_stadium"],
                 fontsize=10, color=TEXT, ha="left", va="center",
                 fontfamily="DejaVu Sans")

    ax_main.text(fig_w / 2 + 0.3, y + 0.4, "Unlucky:",
                 fontsize=10, fontweight="bold", color=RED,
                 ha="left", va="center", fontfamily="DejaVu Sans")
    ax_main.text(fig_w / 2 + 1.8, y + 0.4, d["unlucky_stadium"],
                 fontsize=10, color=TEXT, ha="left", va="center",
                 fontfamily="DejaVu Sans")

    y -= 0.25

    # ═══ SECTION 8: FUN STATS ════════════════════════════════════════════════
    fun_stats = d["fun_stats"]
    num_fun = len(fun_stats)
    fun_row_h = 0.42
    fun_h = 0.7 + num_fun * fun_row_h
    y -= fun_h

    draw_card(0.3, y, fig_w - 0.6, fun_h - 0.1, color=CARD_BG2, border_color=PURPLE_D, radius=0.2)

    ax_main.text(0.6, y + fun_h - 0.4, "FUN STATS",
                 fontsize=10, fontweight="bold", color=PURPLE_L,
                 ha="left", va="center", fontfamily="DejaVu Sans")

    bullet_icons = [">", ">", ">", ">", ">", ">", ">"]
    bullet_colors = [PURPLE_L, GREEN, ORANGE_A, BLUE, RED, PURPLE_L, RED]
    for i, stat in enumerate(fun_stats):
        icon = bullet_icons[i] if i < len(bullet_icons) else ">"
        bcolor = bullet_colors[i] if i < len(bullet_colors) else PURPLE_L
        # Colored bullet
        ax_main.text(0.6, y + fun_h - 0.8 - i * fun_row_h,
                     icon, fontsize=11, fontweight="bold", color=bcolor,
                     ha="left", va="center", fontfamily="DejaVu Sans")
        ax_main.text(0.85, y + fun_h - 0.8 - i * fun_row_h,
                     stat, fontsize=10.5, color=TEXT, ha="left", va="center",
                     fontfamily="DejaVu Sans")

    y -= 0.25

    # ═══ SECTION 9: FINAL VERDICT ════════════════════════════════════════════
    verdict_h = 1.1
    y -= verdict_h

    draw_card(0.3, y, fig_w - 0.6, verdict_h - 0.1,
              color="#1a1230", border_color=PURPLE, radius=0.2)

    ax_main.text(fig_w / 2, y + verdict_h - 0.35, "THE VERDICT",
                 fontsize=10, fontweight="bold", color=PURPLE_L,
                 ha="center", va="center", fontfamily="DejaVu Sans")

    # Wrap long verdict text — strip emojis for matplotlib
    verdict_clean = strip_emoji(d["verdict"])
    wrapped = textwrap.fill(verdict_clean, width=50)
    ax_main.text(fig_w / 2, y + 0.35, wrapped,
                 fontsize=14, fontweight="bold", color=TEXT,
                 ha="center", va="center", fontfamily="DejaVu Sans",
                 style="italic")

    # ═══ FOOTER ══════════════════════════════════════════════════════════════
    y -= 0.5
    ax_main.text(fig_w / 2, y, "IPL Prediction Game 2026  ·  Season Report",
                 fontsize=9, color=DIM, ha="center", va="center",
                 fontfamily="DejaVu Sans")


    # ── Save ─────────────────────────────────────────────────────────────────
    plt.savefig(output_path, dpi=200, bbox_inches="tight",
                facecolor=BG, edgecolor="none", pad_inches=0.1)

    with open(output_path, "rb") as f:
        img_bytes = f.read()

    plt.close(fig)
    return img_bytes


def generate_all_player_reports(results_df, predictions, schedule_df,
                                leaderboard_df, advanced_metrics_df,
                                points_progression, agree_matrix_df,
                                output_dir="The Visuals/reports"):
    """
    Batch-generate report card PNGs for all human participants.
    Returns a dict of {participant_name: image_bytes}.
    """
    import os
    import ExtractAndTransform

    os.makedirs(output_dir, exist_ok=True)

    human_players = [p for p in predictions.keys()
                     if p not in ExtractAndTransform.NON_HUMAN_PLAYERS]

    reports = {}
    for participant in human_players:
        report_data = ExtractAndTransform.get_player_report_data(
            participant, results_df, predictions, schedule_df,
            leaderboard_df, advanced_metrics_df, points_progression,
            agree_matrix_df
        )
        out_path = os.path.join(output_dir, f"{participant}_report.png")
        img_bytes = generate_player_report_card(report_data, output_path=out_path)
        reports[participant] = img_bytes

    return reports