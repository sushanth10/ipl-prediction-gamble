import streamlit as st
import pandas as pd
import os
import Plotting
import ExtractAndTransform
import Analysis

# ─── Helper: section divider ─────────────────────────────────────────────────
def section_label(icon, text):
    st.markdown(f"""
    <div class="section-label">
        <h3>{icon} {text}</h3>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)


# ─── Helper: matchwise points pill row ───────────────────────────────────────
def format_matchwise_points(points_list):
    return "".join(
        f'<span style="background:rgba(124,92,255,0.18);color:#c4b5fd;'
        f'padding:4px 8px;border-radius:6px;margin:2px;font-weight:700;font-size:0.8rem;">{p}</span>'
        for p in points_list
    )


# ─── Helper: top-3 podium ────────────────────────────────────────────────────
def render_podium(leaderboard_df):
    top3 = leaderboard_df[leaderboard_df["Rank"] <= 3].sort_values("Rank").head(3)
    medals   = ["🥇", "🥈", "🥉"]
    colors   = ["#FFD700", "#C0C0C0", "#CD7F32"]
    borders  = ["#FFD700", "#C0C0C0", "#CD7F32"]
    bgs      = [
        "linear-gradient(135deg,rgba(255,215,0,0.10),rgba(255,215,0,0.04))",
        "linear-gradient(135deg,rgba(192,192,192,0.10),rgba(192,192,192,0.04))",
        "linear-gradient(135deg,rgba(205,127,50,0.10),rgba(205,127,50,0.04))",
    ]

    cols = st.columns(3)
    for col, (_, row), medal, color, bg, border in zip(
        cols, top3.iterrows(), medals, colors, bgs, borders
    ):
        with col:
            acc = row.get("Accuracy (%)", 0)
            correct = int(row.get("Correct Predictions", 0))
            st.markdown(f"""
            <div class="podium-card" style="background:{bg};border-color:{border};">
                <span class="podium-medal">{medal}</span>
                <div class="podium-name" style="color:{color};">{row['Participant']}</div>
                <div class="podium-pts" style="color:{color};">{int(row['Points'])} pts</div>
                <div class="podium-stats">{acc:.1f}% accuracy &bull; {correct} correct</div>
            </div>""", unsafe_allow_html=True)


# ─── Helper: leaderboard HTML table ──────────────────────────────────────────
def render_leaderboard_table(leaderboard_df):
    display_cols = ["Rank", "Participant", "Points", "Change", "Accuracy (%)",
                    "Matchwise Points (Last 5)", "Last 5 Matches",
                    "Predicted Points", "Bonus Points", "Correct Predictions"]
    lb = leaderboard_df[display_cols].copy()

    # Build rows
    rows_html = ""
    for _, row in lb.iterrows():
        rank = int(row["Rank"])
        rank_cls = {1: "rank-1", 2: "rank-2", 3: "rank-3"}.get(rank, "rank-n")
        change_val = str(row.get("Change", ""))
        change_cls = "change-up" if "▲" in change_val or "🔼" in change_val else \
                     "change-down" if "▼" in change_val or "🔽" in change_val else "change-same"

        rows_html += f"""
        <tr>
            <td><span class="rank-badge {rank_cls}">{rank}</span></td>
            <td style="font-weight:600;">{row['Participant']}</td>
            <td style="font-weight:800;color:#f0f0ff;">{int(row['Points'])}</td>
            <td class="{change_cls}">{change_val}</td>
            <td style="color:#8b93b8;">{row['Accuracy (%)']:.1f}%</td>
            <td class="matchwise-points">{row['Matchwise Points (Last 5)']}</td>
            <td style="letter-spacing:2px;">{row.get('Last 5 Matches','')}</td>
            <td style="color:#8b93b8;">{int(row.get('Predicted Points',0))}</td>
            <td style="color:#a78bfa;">{int(row.get('Bonus Points',0))}</td>
            <td style="color:#8b93b8;">{int(row.get('Correct Predictions',0))}</td>
        </tr>"""

    headers = ["Rank", "Participant", "Points", "Chg", "Accuracy",
               "Last 5 Pts", "Last 5", "Pred Pts", "Bonus", "Correct"]
    headers_html = "".join(f"<th>{h}</th>" for h in headers)

    st.markdown(f"""
    <div style="overflow-x:auto;border-radius:14px;border:1px solid rgba(255,255,255,0.07);">
        <table class="lb-table">
            <thead><tr>{headers_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)


# ─── Helper: streak table ─────────────────────────────────────────────────────
def render_streak_table(leaderboard_df):
    cols = ["Participant", "Longest Winning Streak", "Winning Period",
            "Longest Losing Streak", "Losing Period"]
    streak_df = leaderboard_df[cols].copy().sort_values(
        "Longest Winning Streak", ascending=False).reset_index(drop=True)

    def style_row(row):
        styles = []
        max_w = streak_df["Longest Winning Streak"].max() or 1
        max_l = streak_df["Longest Losing Streak"].max() or 1
        for col in streak_df.columns:
            if col == "Longest Winning Streak":
                intensity = min(int((row[col] / max_w) * 160), 160)
                styles.append(f"background-color:rgba(34,197,94,{intensity/255:.2f});color:white;font-weight:700;")
            elif col == "Longest Losing Streak":
                intensity = min(int((row[col] / max_l) * 160), 160)
                styles.append(f"background-color:rgba(239,68,68,{intensity/255:.2f});color:white;font-weight:700;")
            else:
                styles.append("")
        return styles

    st.dataframe(
        streak_df.style.apply(style_row, axis=1),
        use_container_width=True, hide_index=True
    )


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        layout="wide",
        page_title="IPL Prediction Dashboard 2026",
        page_icon="🏏",
    )

    base_path = os.path.dirname(os.path.abspath(__file__))

    # ── Inject CSS ──────────────────────────────────────────────────────────
    with open(os.path.join(base_path, "styles.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # ── Custom Header ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ipl-header">
        <div class="ipl-title">🏏 IPL Prediction Dashboard 2026</div>
        <div class="ipl-subtitle">Track predictions · Compare performances · Explore scenarios</div>
        <span class="ipl-badge">🏆 RCB — Defending Champions</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Data Loading ─────────────────────────────────────────────────────────
    schedule_path        = os.path.join(base_path, "The Schedule/ipl_2026_schedule.csv")
    predictions_path     = os.path.join(base_path, "The 2026 Gambles")
    old_predictions_path = os.path.join(base_path, "The 2026 Gambles")  # same folder — no revision split yet
    results_path         = os.path.join(base_path, "The 2026 Results")

    schedule_df = pd.read_csv(schedule_path)
    schedule_df.columns = schedule_df.columns.str.strip()
    results_df  = ExtractAndTransform.load_results(results_path)

    predictions     = ExtractAndTransform.load_predictions(predictions_path)
    old_predictions = ExtractAndTransform.load_predictions(old_predictions_path)

    # ── Guard: no predictions yet ────────────────────────────────────────────
    if not predictions:
        st.info(
            "📂 **No prediction files found yet in `The 2026 Gambles/` folder.**\n\n"
            "Have everyone fill in the bracket and drop their `.txt` files there to get started!"
        )
        st.stop()

    old_lb, _            = ExtractAndTransform.calculate_scores(results_df, old_predictions)
    leaderboard_df, points_progression = ExtractAndTransform.calculate_scores(results_df, predictions)

    total_lb = pd.merge(old_lb, leaderboard_df, on="Participant")[["Participant", "Points_x", "Points_y"]]
    total_lb["Points Difference"] = total_lb["Points_y"] - total_lb["Points_x"]
    total_lb["Change"] = total_lb["Points Difference"].apply(ExtractAndTransform.format_arrow)
    leaderboard_df = pd.merge(total_lb[["Participant", "Change"]], leaderboard_df, on="Participant")
    leaderboard_df["Rank"] = leaderboard_df["Points"].rank(method="dense", ascending=False).astype(int)
    leaderboard_df = leaderboard_df.sort_values("Rank").reset_index(drop=True)
    leaderboard_df["Matchwise Points (Last 5)"] = leaderboard_df["Matchwise Points (Last 5)"].apply(format_matchwise_points)

    matchwise_df = ExtractAndTransform.matchwise_predictions(schedule_df, predictions)
    prediction_ratio_counts, home_away_ratio_counts = Analysis.get_prediction_ratios(matchwise_df)

    # Calculate advanced metrics
    advanced_metrics_df = ExtractAndTransform.get_advanced_metrics(results_df, predictions)
    team_acc_matrix = ExtractAndTransform.get_team_accuracy_matrix(results_df, predictions, schedule_df)
    difficulty_df = ExtractAndTransform.get_match_difficulty(results_df, predictions, schedule_df)
    agree_matrix = ExtractAndTransform.get_agreement_matrix(predictions, results_df)
    points_dist = ExtractAndTransform.get_points_distribution(results_df, predictions)
    # Merge advanced metrics into main leaderboard for display
    leaderboard_df = pd.merge(leaderboard_df, advanced_metrics_df, on="Participant", how="left")

    # ── Top-level KPIs ───────────────────────────────────────────────────────
    leader = leaderboard_df.iloc[0]
    total_matches = len(results_df)
    avg_accuracy = leaderboard_df["Accuracy (%)"].mean()
    num_participants = len(leaderboard_df)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🥇 Leader", leader["Participant"], f"{int(leader['Points'])} pts")
    k2.metric("📋 Matches Played", total_matches, f"of 70 league")
    k3.metric("👥 Participants", num_participants)
    k4.metric("🎯 Avg Accuracy", f"{avg_accuracy:.1f}%")

    st.write("")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🏆  Leaderboard",
        "📋  All Predictions",
        "🔢  Matchwise",
        "📊  Analysis",
        "⚔️  Head-to-Head",
        "🔮  Scenarios",
        "🎭  Personalities",
        "📅  Calendar",
        "🏟️  Team Intelligence",
    ])

    # ── TAB 1: Leaderboard ──────────────────────────────────────────────────
    with tab1:
        # Shareable leaderboard card
        card_path = os.path.join(base_path, "The Visuals/leaderboard_card.png")
        img_bytes = Plotting.generate_leaderboard_card(leaderboard_df, output_path=card_path, total_matches=total_matches)

        import datetime
        dl_col, prev_col = st.columns([1, 3])
        with dl_col:
            st.download_button(
                label="📥 Download Leaderboard Card",
                data=img_bytes,
                file_name=f"ipl_leaderboard_{datetime.date.today()}.png",
                mime="image/png",
                use_container_width=True,
            )
        with prev_col:
            with st.expander("🖼️ Preview Card", expanded=False):
                st.image(img_bytes, use_column_width=True)

        # ── Podium / medal cards (commented out — re-enable when season is underway) ──
        # section_label("🏅", "Top Predictors")
        # render_podium(leaderboard_df)

        # Full leaderboard
        section_label("📊", "Full Leaderboard")
        
        # We need a custom render function here to include the new columns without breaking the old layout:
        display_cols = ["Rank", "Participant", "Points", "Change", "Accuracy (%)",
                        "Consistency Score", "Current Form (%)", "Upset Accuracy (%)", "Clutch Rate (%)",
                        "Matchwise Points (Last 5)", "Last 5 Matches",
                        "Predicted Points", "Bonus Points", "Correct Predictions"]
        
        lb_disp = leaderboard_df[display_cols].copy()
        
        # Build HTML table manually to have full control over the huge width
        rows_html = ""
        for _, row in lb_disp.iterrows():
            rank = int(row["Rank"])
            rank_cls = {1: "rank-1", 2: "rank-2", 3: "rank-3"}.get(rank, "rank-n")
            change_val = str(row.get("Change", ""))
            change_cls = "change-up" if "▲" in change_val or "🔼" in change_val else "change-down" if "▼" in change_val or "🔽" in change_val else "change-same"

            rows_html += f"""
            <tr>
                <td><span class="rank-badge {rank_cls}">{rank}</span></td>
                <td style="font-weight:600;">{row['Participant']}</td>
                <td style="font-weight:800;color:#f0f0ff;font-size:1.1rem;">{int(row['Points'])}</td>
                <td class="{change_cls}">{change_val}</td>
                <td style="color:#a78bfa;font-weight:700;">{row['Accuracy (%)']:.1f}%</td>
                <td style="color:#c4c9e8;">{row['Consistency Score']:.1f}</td>
                <td style="color:#c4c9e8;">{row['Current Form (%)']:.1f}%</td>
                <td style="color:#c4c9e8;">{row['Upset Accuracy (%)']:.1f}%</td>
                <td style="color:#c4c9e8;">{row['Clutch Rate (%)']:.1f}%</td>
                <td class="matchwise-points">{row['Matchwise Points (Last 5)']}</td>
                <td style="letter-spacing:1px;font-size:0.8rem;">{row.get('Last 5 Matches','')}</td>
                <td style="color:#8b93b8;font-size:0.8rem;">{int(row.get('Predicted Points',0))}</td>
                <td style="color:#8b93b8;font-size:0.8rem;">{int(row.get('Bonus Points',0))}</td>
                <td style="color:#8b93b8;font-size:0.8rem;">{int(row.get('Correct Predictions',0))}</td>
            </tr>"""

        headers = ["Rank", "Name", "Points", "Chg", "Accuracy", "Consist.", "Form", "Upset Acc", "Clutch",
                   "Last 5 Pts", "Last 5", "Pred Pts", "Bonus", "Correct"]
        headers_html = "".join(f"<th style='white-space:nowrap;'>{h}</th>" for h in headers)

        st.markdown(f"""
        <div style="overflow-x:auto;border-radius:14px;border:1px solid rgba(255,255,255,0.07);">
            <table class="lb-table" style="min-width:1200px;">
                <thead><tr>{headers_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>""", unsafe_allow_html=True)

        number_of_outcomes, outcomes_string = ExtractAndTransform.format_outcomes(results_df)
        st.markdown(
            f'<p style="color:#8b93b8;font-size:0.82rem;margin-top:10px;">'
            f'🎲 Remaining possible outcomes: <strong style="color:#a78bfa;">{outcomes_string}</strong> '
            f'({number_of_outcomes:,} combinations)</p>',
            unsafe_allow_html=True
        )

        # Points worm
        section_label("📈", "Points Progression Worm")
        Plotting.plot_animated_worm_graph(points_progression)

        # Streaks
        section_label("🔥", "Win & Loss Streaks")
        render_streak_table(leaderboard_df)
        st.plotly_chart(Plotting.plot_streak_heatmap(leaderboard_df), use_container_width=True)

    # ── TAB 2: All Predictions ───────────────────────────────────────────────
    with tab2:
        section_label("📋", "All Predictions")
        max_len = max(len(v) for v in predictions.values())
        padded = {k: v + [''] * (max_len - len(v)) for k, v in predictions.items()}
        st.dataframe(pd.DataFrame(padded), use_container_width=True, hide_index=True)

    # ── TAB 3: Matchwise Predictions ────────────────────────────────────────
    with tab3:
        section_label("🔢", "Matchwise Predictions")
        st.dataframe(matchwise_df, use_container_width=True, hide_index=True)

    # ── TAB 4: Analysis ─────────────────────────────────────────────────────
    with tab4:
        section_label("🏏", "Participant-wise Team Predictions")
        participant_wise = ExtractAndTransform.get_participant_wise_team_predictions(predictions)
        participants = participant_wise["Participant"].unique()

        for i in range(0, len(participants), 6):
            cols = st.columns(min(6, len(participants) - i))
            for j, col in enumerate(cols):
                participant = participants[i + j]
                with col:
                    st.markdown(f"<p style='font-size:0.8rem;font-weight:700;color:#c4c9e8;'>{participant}</p>",
                                unsafe_allow_html=True)
                    fig = Plotting.plot_participant_wise_team_predictions(
                        participant_wise[participant_wise["Participant"] == participant]
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

        section_label("📊", "Average Team Win Predictions")
        counts_df = Analysis.prediction_counts_analysis(predictions)
        counts_df_mean = counts_df.mean().sort_values(ascending=False)
        st.plotly_chart(Plotting.avg_wins_plot(counts_df_mean), use_container_width=True)

        section_label("⚖️", "Prediction Ratio Analysis")
        prediction_ratio_counts, home_away_ratio_counts = Analysis.get_prediction_ratios(matchwise_df)
        st.plotly_chart(Plotting.plot_prediction_ratio(prediction_ratio_counts), use_container_width=True)
        Plotting.plot_home_away_ratio(home_away_ratio_counts)

        section_label("🏠", "Home / Away Prediction %")
        _max_len = max(len(v) for v in predictions.values())
        _padded = {k: v + [''] * (_max_len - len(v)) for k, v in predictions.items()}
        percentage_df = Analysis.home_away_percentage(schedule_df, pd.DataFrame(_padded))
        percentage_df.sort_values("Home", ascending=False, inplace=True)
        percentage_df = percentage_df.rename(columns={"Home": "Home %", "Away": "Away %"})
        st.plotly_chart(Plotting.plot_home_away_percentage(percentage_df), use_container_width=True)

        section_label("📉", "Position Over Time")
        st.plotly_chart(Plotting.plot_position_graph(points_progression), use_container_width=True)

        points_progression_df = pd.DataFrame(points_progression)[1:].reset_index()
        points_progression_df = points_progression_df.rename(columns={"index": "Match #"})
        st.dataframe(points_progression_df, use_container_width=True, hide_index=True)

    # ── TAB 5: Head-to-Head ─────────────────────────────────────────────────
    with tab5:
        section_label("⚔️", "Head-to-Head Comparison")

        all_participants = sorted(predictions.keys())
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p1 = st.selectbox("Participant 1", all_participants, index=0, key="h2h_p1")
        with col_p2:
            remaining = [p for p in all_participants if p != p1]
            p2 = st.selectbox("Participant 2", remaining, index=0, key="h2h_p2")

        h2h_df = ExtractAndTransform.get_head_to_head(predictions, results_df, p1, p2)

        agree_pct = (h2h_df["Agreement"] == "✅").mean() * 100
        p1_total  = h2h_df[f"{p1} Cumulative"].iloc[-1]
        p2_total  = h2h_df[f"{p2} Cumulative"].iloc[-1]
        p1_wins   = int((h2h_df[f"{p1} Points"] > h2h_df[f"{p2} Points"]).sum())
        p2_wins   = int((h2h_df[f"{p2} Points"] > h2h_df[f"{p1} Points"]).sum())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"🏅 {p1}", f"{p1_total} pts")
        m2.metric(f"🏅 {p2}", f"{p2_total} pts")
        m3.metric("🤝 Agreement", f"{agree_pct:.1f}%")
        m4.metric("⚡ Match Wins", f"{p1} {p1_wins} – {p2_wins} {p2}")

        st.plotly_chart(Plotting.plot_h2h_comparison(h2h_df, p1, p2), use_container_width=True)

        section_label("📋", "Match-by-Match Breakdown")
        display_cols = [
            "Match #", "Date", "Home", "Away", "Actual Winner",
            f"{p1} Prediction", f"{p2} Prediction",
            f"{p1} Points", f"{p2} Points", "Agreement"
        ]
        st.dataframe(h2h_df[display_cols], use_container_width=True, hide_index=True)

    # ── TAB 6: Scenarios ────────────────────────────────────────────────────
    with tab6:
        section_label("🔮", "What-If Scenario Calculator")
        st.markdown(
            '<p style="color:#8b93b8;font-size:0.88rem;margin-bottom:16px;">'
            'Toggle match winners below to see how the leaderboard would have looked. '
            '<em>A fun retrospective tool since the season has concluded.</em></p>',
            unsafe_allow_html=True
        )

        all_match_slots = ExtractAndTransform.get_all_match_slots(results_df, schedule_df)
        completed_slots = [s for s in all_match_slots if s["Current Winner"] != "TBD"]

        with st.expander("🔧 Adjust Match Outcomes", expanded=True):
            overrides = {}
            for i in range(0, len(completed_slots), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(completed_slots):
                        slot = completed_slots[i + j]
                        idx = slot["Index"]
                        teams = [slot["Home Team"], slot["Away Team"], "NR"]
                        current = slot["Current Winner"] if slot["Current Winner"] in teams else teams[0]
                        with col:
                            chosen = st.selectbox(
                                f"M{slot['Match #']}: {slot['Home Team'][:3]} vs {slot['Away Team'][:3]}",
                                teams,
                                index=teams.index(current),
                                key=f"scenario_{idx}",
                            )
                            if chosen != slot["Current Winner"]:
                                overrides[idx] = chosen

        simulated_lb = ExtractAndTransform.simulate_leaderboard(results_df, predictions, overrides)
        simulated_lb["Rank"] = simulated_lb["Points"].rank(method="dense", ascending=False).astype(int)
        simulated_lb = simulated_lb.sort_values("Rank").reset_index(drop=True)

        if overrides:
            st.info(f"⚡ **{len(overrides)} match(es) overridden** — simulated leaderboard below.")
        else:
            st.info("No changes yet — showing actual leaderboard. Toggle some matches above ☝️")

        section_label("📊", "Simulated Leaderboard")
        st.dataframe(simulated_lb, use_container_width=True, hide_index=True)


    # ── TAB 7: Personalities ────────────────────────────────────────────────
    with tab7:
        section_label("🎭", "Participant Personas & Awards")
        st.markdown(
            '<p style="color:#8b93b8;font-size:0.88rem;margin-bottom:20px;">'
            'Fun personality quirks and betting patterns extracted from the season\'s prediction data.</p>',
            unsafe_allow_html=True
        )
        st.markdown(Plotting.plot_personality_cards(advanced_metrics_df), unsafe_allow_html=True)
        
        st.write("\n\n")
        section_label("🧠", "Advanced Metrics Breakdown")
        st.info("""
        **What do these metrics mean?**
        - **Consistency Score**: How steady a predictor is. Lower variance in scoring = higher consistency.
        - **Current Form**: Weighted accuracy over the entire season, with recent matches heavily weighted.
        - **Upset Accuracy**: Win percentage in matches where the away team won.
        - **Clutch Rate**: Win percentage in the hardest-to-predict matches (where the crowd was split 50/50).
        - **Contrarian Index**: How often a participant picked against the majority *and won*.
        - **Crowd Follower %**: How often a participant's pick aligned with the majority of players.
        """)
        st.dataframe(
            advanced_metrics_df.drop("Participant", axis=1).set_index(advanced_metrics_df["Participant"]),
            use_container_width=True
        )


    # ── TAB 8: Calendar ─────────────────────────────────────────────────────
    with tab8:
        section_label("📅", "Season Match Calendar")
        st.markdown(
            '<p style="color:#8b93b8;font-size:0.88rem;margin-bottom:10px;">'
            'A chronological grid of all matches. Green cells mean the majority picked correctly, '
            'Red means the majority got it wrong (Upset). Hover to see exact numbers.</p>',
            unsafe_allow_html=True
        )
        st.plotly_chart(Plotting.plot_calendar_heatmap(results_df, predictions, schedule_df), use_container_width=True)
        
        st.write("\n\n")
        section_label("📉", "Match Difficulty Ranking")
        st.markdown(
            '<p style="color:#8b93b8;font-size:0.88rem;margin-bottom:10px;">'
            'Ranks all completed matches by how many participants correctly predicted the winner. '
            'Matches at the top were the hardest to predict.</p>',
            unsafe_allow_html=True
        )
        st.plotly_chart(Plotting.plot_match_difficulty(difficulty_df), use_container_width=True)


    # ── TAB 9: Team Intelligence ─────────────────────────────────────────────
    with tab9:
        section_label("🎯", "Participant vs Team Accuracy Matrix")
        st.markdown(
            '<p style="color:#8b93b8;font-size:0.88rem;margin-bottom:10px;">'
            'Displays the percentage of times a participant correctly predicted matches involving a specific team. '
            'Use this to see who reads which franchise best!</p>',
            unsafe_allow_html=True
        )
        st.plotly_chart(Plotting.plot_team_accuracy_heatmap(team_acc_matrix), use_container_width=True)
        
        st.write("\n\n")
        section_label("🗺️", "Stadium Luck Map")
        st.markdown(
            '<p style="color:#8b93b8;font-size:0.88rem;margin-bottom:10px;">'
            'An interactive map of India showing all IPL stadiums. Select a participant to see their lucky and unlucky grounds. Larger colored bubbles indicate more wins.</p>',
            unsafe_allow_html=True
        )
        selected_map_user = st.selectbox("Select Participant for Stadium Map", list(predictions.keys()))
        user_stadium_df = ExtractAndTransform.get_user_stadium_stats(results_df, predictions, schedule_df, selected_map_user)
        st.plotly_chart(Plotting.plot_stadium_map(user_stadium_df, selected_map_user), use_container_width=True)

        st.write("\n\n")
        col_pts, col_agree = st.columns([1, 1.2])
        
        with col_pts:
            section_label("📊", "Points Distribution")
            st.plotly_chart(Plotting.plot_points_distribution(points_dist), use_container_width=True)
            
        with col_agree:
            section_label("🤝", "Participant Agreement Matrix")
            st.plotly_chart(Plotting.plot_agreement_matrix(agree_matrix), use_container_width=True)


if __name__ == "__main__":
    main()
