import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Teen Patti Tracker",
    page_icon="🃏",
    layout="wide"
)

st.markdown("""
<style>
    .player-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e94560;
        margin-bottom: 10px;
    }
    .stat-box {
        background: #0f3460;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin: 5px 0;
    }
    .positive { color: #00ff88; }
    .negative { color: #ff4757; }
    .header-title {
        text-align: center;
        color: #e94560;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'players' not in st.session_state:
        st.session_state.players = {
            'Player 1': {'name': 'Player 1', 'rounds': []},
            'Player 2': {'name': 'Player 2', 'rounds': []},
            'Player 3': {'name': 'Player 3', 'rounds': []},
            'Player 4': {'name': 'Player 4', 'rounds': []}
        }
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'game_history' not in st.session_state:
        st.session_state.game_history = []

def get_player_stats(player_key):
    rounds = st.session_state.players[player_key]['rounds']
    if not rounds:
        return {
            'total_hands': 0,
            'hands_won': 0,
            'win_rate': 0,
            'total_chips': 0,
            'blind_plays': 0,
            'seen_plays': 0
        }
    
    df = pd.DataFrame(rounds)
    return {
        'total_hands': len(df),
        'hands_won': df['won'].sum(),
        'win_rate': (df['won'].sum() / len(df) * 100) if len(df) > 0 else 0,
        'total_chips': df['chips'].sum(),
        'blind_plays': df['play_type'].value_counts().get('Blind', 0),
        'seen_plays': df['play_type'].value_counts().get('Seen', 0)
    }

def add_round_data(player_key, chips, won, play_type, hand_rank):
    round_data = {
        'round': st.session_state.current_round,
        'chips': chips,
        'won': won,
        'play_type': play_type,
        'hand_rank': hand_rank,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.players[player_key]['rounds'].append(round_data)

def display_player_form(player_key, col):
    with col:
        player = st.session_state.players[player_key]
        stats = get_player_stats(player_key)
        
        st.markdown(f"### 🎴 {player['name']}")
        
        new_name = st.text_input(
            "Player Name",
            value=player['name'],
            key=f"name_{player_key}"
        )
        if new_name != player['name']:
            st.session_state.players[player_key]['name'] = new_name
        
        st.markdown("---")
        st.markdown("**Add Round Data**")
        
        chips = st.number_input(
            "Chips Won/Lost",
            min_value=-10000,
            max_value=10000,
            value=0,
            step=10,
            key=f"chips_{player_key}",
            help="Positive for won, negative for lost"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            won = st.checkbox("Won Hand", key=f"won_{player_key}")
        with col2:
            play_type = st.selectbox(
                "Play Type",
                ["Blind", "Seen", "Pack"],
                key=f"play_type_{player_key}"
            )
        
        hand_rank = st.selectbox(
            "Hand Rank",
            ["None", "Trail/Set", "Pure Sequence", "Sequence", "Color", "Pair", "High Card"],
            key=f"hand_rank_{player_key}"
        )
        
        if st.button("➕ Add Round", key=f"add_{player_key}", use_container_width=True):
            add_round_data(player_key, chips, won, play_type, hand_rank)
            st.success(f"Round added for {player['name']}!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("**📊 Statistics**")
        
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.metric("Hands Played", stats['total_hands'])
            st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
            st.metric("Blind Plays", stats['blind_plays'])
        
        with stat_col2:
            st.metric("Hands Won", stats['hands_won'])
            chip_delta = stats['total_chips']
            st.metric(
                "Total Chips",
                f"{abs(stats['total_chips'])}",
                delta=f"{'+' if chip_delta >= 0 else ''}{chip_delta}"
            )
            st.metric("Seen Plays", stats['seen_plays'])

def display_comparison_charts():
    st.markdown("## 📈 Player Comparison")
    
    player_data = []
    for player_key in st.session_state.players:
        stats = get_player_stats(player_key)
        player_data.append({
            'Player': st.session_state.players[player_key]['name'],
            'Total Chips': stats['total_chips'],
            'Hands Won': stats['hands_won'],
            'Win Rate': stats['win_rate'],
            'Hands Played': stats['total_hands']
        })
    
    df = pd.DataFrame(player_data)
    
    if df['Hands Played'].sum() > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_chips = px.bar(
                df,
                x='Player',
                y='Total Chips',
                color='Total Chips',
                color_continuous_scale=['#ff4757', '#ffa502', '#00ff88'],
                title='Total Chips Won/Lost'
            )
            fig_chips.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_chips, use_container_width=True)
        
        with col2:
            fig_wins = px.pie(
                df[df['Hands Won'] > 0],
                values='Hands Won',
                names='Player',
                title='Hands Won Distribution',
                color_discrete_sequence=['#e94560', '#0f3460', '#00ff88', '#ffa502']
            )
            fig_wins.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_wins, use_container_width=True)
        
        fig_radar = go.Figure()
        for player_key in st.session_state.players:
            stats = get_player_stats(player_key)
            if stats['total_hands'] > 0:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[stats['win_rate'], stats['blind_plays']*10, stats['seen_plays']*10, 
                       min(stats['total_chips']/10 + 50, 100), stats['hands_won']*10],
                    theta=['Win Rate', 'Blind Plays', 'Seen Plays', 'Chip Score', 'Hands Won'],
                    fill='toself',
                    name=st.session_state.players[player_key]['name']
                ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title='Player Performance Radar',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Add some round data to see comparison charts!")

def display_round_history():
    st.markdown("## 📜 Round History")
    
    all_rounds = []
    for player_key in st.session_state.players:
        player = st.session_state.players[player_key]
        for round_data in player['rounds']:
            all_rounds.append({
                'Player': player['name'],
                'Round': round_data['round'],
                'Chips': round_data['chips'],
                'Won': '✅' if round_data['won'] else '❌',
                'Play Type': round_data['play_type'],
                'Hand': round_data['hand_rank'],
                'Time': round_data['timestamp']
            })
    
    if all_rounds:
        df = pd.DataFrame(all_rounds)
        df = df.sort_values(['Round', 'Time'], ascending=[False, False])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No rounds played yet. Start adding data above!")

def main():
    initialize_session_state()
    
    st.markdown("<h1 class='header-title'>🃏 Teen Patti Tracker</h1>", unsafe_allow_html=True)
    
    col_round, col_next, col_reset = st.columns([2, 1, 1])
    with col_round:
        st.markdown(f"### 🎯 Current Round: {st.session_state.current_round}")
    with col_next:
        if st.button("▶️ Next Round", use_container_width=True):
            st.session_state.current_round += 1
            st.rerun()
    with col_reset:
        if st.button("🔄 Reset Game", use_container_width=True):
            st.session_state.players = {
                'Player 1': {'name': 'Player 1', 'rounds': []},
                'Player 2': {'name': 'Player 2', 'rounds': []},
                'Player 3': {'name': 'Player 3', 'rounds': []},
                'Player 4': {'name': 'Player 4', 'rounds': []}
            }
            st.session_state.current_round = 1
            st.rerun()
    
    st.markdown("---")
    
    tabs = st.tabs(["🎮 Game Entry", "📊 Analytics", "📜 History"])
    
    with tabs[0]:
        st.markdown("### Enter Data for Each Player")
        cols = st.columns(4)
        player_keys = list(st.session_state.players.keys())
        
        for i, col in enumerate(cols):
            display_player_form(player_keys[i], col)
    
    with tabs[1]:
        display_comparison_charts()
    
    with tabs[2]:
        display_round_history()

if __name__ == "__main__":
    main()
