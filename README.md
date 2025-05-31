# 🏏 IPL Prediction Game 2025 – Streamlit Dashboard with Leaderboard

Welcome to the **IPL Prediction Game**, a personalized and competitive prediction league created during the 2025 IPL season. This project brings the thrill of cricket to your friend group through a custom-built Streamlit dashboard that tracks match results, player predictions, and a dynamically updated leaderboard.

---

## 📊 About the Project

This is a fun side project developed to make IPL games even more exciting. Friends predict the match winners for each IPL game, and their predictions are scored and ranked on a leaderboard. The whole experience is powered by a clean and interactive Streamlit dashboard.

---

## 🚀 Features

- ✅ Match result input (manual via CSV)
- 📥 Prediction collection via a basic web interface
- 📈 Dynamic leaderboard with:
  - Total score
  - Accuracy %
  - Bonus point system
- 🔁 Automatic updates based on result entries
- 🔍 Longest win/loss streaks tracked (in code, currently not visualized)

---

## 🛠️ Tech Stack

- **Frontend & UI**: [Streamlit](https://streamlit.io/)
- **Data Storage**: CSV files for match results and predictions
- **Prediction Input**: Basic HTML form/webpage
- **Hosting**: Local or cloud-hosted Streamlit app (manual)

---

## 🧮 Scoring System

- ✅ **Correct prediction**: +10 points  
- 🤝 **Match with No Result (NR)**: +5 points  
- 🧳 **Bonus points for away wins**: +4  
- 📈 **Rank difference bonus**:  
  If a lower-ranked team wins away vs. a higher-ranked team, the difference in their ranks is added to their points.  

  **Example:**
  - 10th place team beats 1st place team away: `10 (win) + 4 (away) + 9 (rank diff) = 23 points`
  - 1st place wins home game: `10 points`

---

## 📁 Folder Structure

- `The Results/Results.csv` — Match outcomes (manually updated)
- `The Gambles/` — Text files with player predictions
- `The Calculated Gambles/` — Text files with updated player predictions (after 3 games of each team) 
- `Dashboard.py` — Main Streamlit app  
- `Other .py files` — Modules for scoring, ranking, and utilities  
- `The Schedule/IPL 2025 bracket.html` — Basic webpage for prediction input  
- `README.md` — This file  

---

## 📊 Leaderboard Insights

- Accuracy % calculated per player  
- Scores update automatically with result updates  
- Longest win/loss streaks tracked in backend (UI integration planned)  

---

## 🧪 How to Run

1. Clone the repo  
```bash
   git clone https://github.com/yourusername/ipl-prediction-game.git
   cd ipl-prediction-game
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app

```bash
streamlit run Dashboard.py
```
