# Teen Patti Tracker

A multi-player Teen Patti game tracker built with Streamlit.

## Overview

This app allows 4 players to separately track their bets during Teen Patti games, with each player having their own dedicated page.

## How to Use

### Player Links
- **Dashboard**: Main page at `/` - shows aggregate data and round summary
- **Player 1**: `/?player=1`
- **Player 2**: `/?player=2`
- **Player 3**: `/?player=3`
- **Player 4**: `/?player=4`

### Player Features
Each player can:
- Enter money in multiples of 5 (quick buttons: ₹5, ₹10, ₹15, ₹20, ₹25, ₹50)
- Enter custom amounts (must be multiples of 5)
- Quit the current round
- Mark themselves as the winner

### Dashboard Features
- View all players' current round totals
- See who has won/quit
- Complete rounds and calculate pot distribution
- View aggregate summary across all rounds
- See round history

## Tech Stack
- Python 3.11
- Streamlit
- Pandas
- Plotly

## Running the App
```bash
streamlit run app.py --server.port 5000
```
