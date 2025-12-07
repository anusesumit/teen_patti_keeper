# Teen Patti Tracker

A multi-player Teen Patti game tracker built with Streamlit and PostgreSQL.

## Overview

This app allows 4 players to separately track their bets during Teen Patti games on their own devices, with data synced in real-time via the database.

## How to Use

### Player Links (Share with each player)
- **Dashboard**: Main page at `/` - shows aggregate data
- **Player 1**: `/?player=1`
- **Player 2**: `/?player=2`
- **Player 3**: `/?player=3`
- **Player 4**: `/?player=4`

### Player Features
Each player can:
- Add money in the doubling sequence: ₹5, ₹10, ₹20, ₹40, ₹80, ₹160, ₹320, ₹640, ₹1280, ₹2560, ₹5120
- Quit the current round
- Mark themselves as the winner
- See their entries and totals

### Dashboard Features
- View all players' current round totals (synced from all devices)
- See who has won/quit
- Complete rounds and calculate pot distribution
- View aggregate summary showing net profit/loss
- See complete round history

## Tech Stack
- Python 3.11
- Streamlit
- PostgreSQL (for real-time data sync)
- Pandas
- Plotly

## Database Tables
- `players`: Player info (name, status, won_round)
- `entries`: Money entries per round
- `game_state`: Current round number
- `completed_rounds`: Finished rounds with pot and winner

## Running the App
```bash
streamlit run app.py --server.port 5000
```
