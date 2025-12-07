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
    }
    .stat-box {
        background: #0f3460;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .positive { color: #00ff88; }
    .negative { color: #ff4757; }
    .header-title {
        text-align: center;
        color: #e94560;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .round-active {
        background: #1a1a2e;
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'players' not in st.session_state:
        st.session_state.players = {
            'Player 1': {'name': 'Player 1'},
            'Player 2': {'name': 'Player 2'},
            'Player 3': {'name': 'Player 3'},
            'Player 4': {'name': 'Player 4'}
        }
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'current_round_hands' not in st.session_state:
        st.session_state.current_round_hands = {
            'Player 1': [],
            'Player 2': [],
            'Player 3': [],
            'Player 4': []
        }
    if 'completed_rounds' not in st.session_state:
        st.session_state.completed_rounds = []
    if 'round_in_progress' not in st.session_state:
        st.session_state.round_in_progress = True

def get_player_totals(player_key):
    total_bet = 0
    total_won = 0
    rounds_won = 0
    total_rounds = len(st.session_state.completed_rounds)
    blind_count = 0
    seen_count = 0
    pack_count = 0
    
    for round_data in st.session_state.completed_rounds:
        player_hands = round_data['hands'].get(player_key, [])
        for hand in player_hands:
            total_bet += hand['bet_amount']
            if hand['play_type'] == 'Blind':
                blind_count += 1
            elif hand['play_type'] == 'Seen':
                seen_count += 1
            elif hand['play_type'] == 'Pack':
                pack_count += 1
        
        if round_data['winner'] == player_key:
            total_won += round_data['pot_amount']
            rounds_won += 1
    
    return {
        'total_bet': total_bet,
        'total_won': total_won,
        'net': total_won - total_bet,
        'rounds_won': rounds_won,
        'total_rounds': total_rounds,
        'blind_count': blind_count,
        'seen_count': seen_count,
        'pack_count': pack_count
    }

def get_current_round_total(player_key):
    hands = st.session_state.current_round_hands.get(player_key, [])
    return sum(h['bet_amount'] for h in hands)

def add_hand(player_key, bet_amount, play_type):
    hand_data = {
        'hand_num': len(st.session_state.current_round_hands[player_key]) + 1,
        'bet_amount': bet_amount,
        'play_type': play_type,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.current_round_hands[player_key].append(hand_data)

def complete_round(winner_key, pot_amount):
    round_data = {
        'round_num': st.session_state.current_round,
        'hands': dict(st.session_state.current_round_hands),
        'winner': winner_key,
        'winner_name': st.session_state.players[winner_key]['name'],
        'pot_amount': pot_amount,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.completed_rounds.append(round_data)
    
    st.session_state.current_round += 1
    st.session_state.current_round_hands = {
        'Player 1': [],
        'Player 2': [],
        'Player 3': [],
        'Player 4': []
    }

def display_hand_entry():
    st.markdown("### 🎴 Track Hands for Current Round")
    
    cols = st.columns(4)
    player_keys = list(st.session_state.players.keys())
    
    for i, col in enumerate(cols):
        player_key = player_keys[i]
        player = st.session_state.players[player_key]
        
        with col:
            st.markdown(f"#### {player['name']}")
            
            new_name = st.text_input(
                "Name",
                value=player['name'],
                key=f"name_{player_key}",
                label_visibility="collapsed"
            )
            if new_name != player['name']:
                st.session_state.players[player_key]['name'] = new_name
            
            bet_amount = st.number_input(
                "Bet Amount",
                min_value=0,
                max_value=10000,
                value=10,
                step=5,
                key=f"bet_{player_key}"
            )
            
            play_type = st.selectbox(
                "Play Type",
                ["Blind", "Seen", "Pack"],
                key=f"type_{player_key}"
            )
            
            if st.button("➕ Add Hand", key=f"add_{player_key}", use_container_width=True):
                add_hand(player_key, bet_amount, play_type)
                st.rerun()
            
            current_total = get_current_round_total(player_key)
            hands_count = len(st.session_state.current_round_hands[player_key])
            
            st.markdown("---")
            st.metric("Hands This Round", hands_count)
            st.metric("Total Bet", f"₹{current_total}")
            
            if hands_count > 0:
                with st.expander("View Hands"):
                    for hand in st.session_state.current_round_hands[player_key]:
                        st.write(f"Hand {hand['hand_num']}: ₹{hand['bet_amount']} ({hand['play_type']})")

def display_round_completion():
    st.markdown("---")
    st.markdown("### 🏆 Complete Round - Who Won?")
    
    total_pot = sum(
        get_current_round_total(pk) 
        for pk in st.session_state.players.keys()
    )
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        player_options = {
            pk: st.session_state.players[pk]['name'] 
            for pk in st.session_state.players.keys()
        }
        winner = st.selectbox(
            "Round Winner",
            options=list(player_options.keys()),
            format_func=lambda x: player_options[x],
            key="round_winner"
        )
    
    with col2:
        pot_amount = st.number_input(
            "Pot Amount Won",
            min_value=0,
            value=total_pot,
            step=10,
            key="pot_amount",
            help="Auto-calculated from bets, adjust if needed"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Complete Round", type="primary", use_container_width=True):
            if any(len(st.session_state.current_round_hands[pk]) > 0 for pk in st.session_state.players.keys()):
                complete_round(winner, pot_amount)
                st.success(f"Round completed! {st.session_state.players[winner]['name']} won ₹{pot_amount}!")
                st.rerun()
            else:
                st.error("Add at least one hand before completing the round!")

def display_player_stats():
    st.markdown("## 📊 Player Statistics")
    
    cols = st.columns(4)
    player_keys = list(st.session_state.players.keys())
    
    for i, col in enumerate(cols):
        player_key = player_keys[i]
        player = st.session_state.players[player_key]
        stats = get_player_totals(player_key)
        
        with col:
            st.markdown(f"### {player['name']}")
            
            net = stats['net']
            net_color = "🟢" if net >= 0 else "🔴"
            
            st.metric("Net Profit/Loss", f"₹{net}", delta=f"{'+' if net >= 0 else ''}{net}")
            st.metric("Total Bet", f"₹{stats['total_bet']}")
            st.metric("Total Won", f"₹{stats['total_won']}")
            st.metric("Rounds Won", f"{stats['rounds_won']}/{stats['total_rounds']}")
            
            with st.expander("Play Style"):
                st.write(f"🙈 Blind: {stats['blind_count']}")
                st.write(f"👀 Seen: {stats['seen_count']}")
                st.write(f"📦 Pack: {stats['pack_count']}")

def display_charts():
    if not st.session_state.completed_rounds:
        st.info("Complete some rounds to see analytics!")
        return
    
    player_data = []
    for player_key in st.session_state.players:
        stats = get_player_totals(player_key)
        player_data.append({
            'Player': st.session_state.players[player_key]['name'],
            'Net Profit': stats['net'],
            'Total Bet': stats['total_bet'],
            'Total Won': stats['total_won'],
            'Rounds Won': stats['rounds_won']
        })
    
    df = pd.DataFrame(player_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_net = px.bar(
            df,
            x='Player',
            y='Net Profit',
            color='Net Profit',
            color_continuous_scale=['#ff4757', '#ffa502', '#00ff88'],
            title='Net Profit/Loss by Player'
        )
        fig_net.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_net, use_container_width=True)
    
    with col2:
        if df['Rounds Won'].sum() > 0:
            fig_wins = px.pie(
                df[df['Rounds Won'] > 0],
                values='Rounds Won',
                names='Player',
                title='Rounds Won Distribution',
                color_discrete_sequence=['#e94560', '#0f3460', '#00ff88', '#ffa502']
            )
            fig_wins.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_wins, use_container_width=True)

def display_round_history():
    st.markdown("## 📜 Round History")
    
    if not st.session_state.completed_rounds:
        st.info("No completed rounds yet!")
        return
    
    for round_data in reversed(st.session_state.completed_rounds):
        with st.expander(f"Round {round_data['round_num']} - Winner: {round_data['winner_name']} (₹{round_data['pot_amount']})"):
            cols = st.columns(4)
            for i, player_key in enumerate(st.session_state.players.keys()):
                with cols[i]:
                    player_name = st.session_state.players[player_key]['name']
                    hands = round_data['hands'].get(player_key, [])
                    total_bet = sum(h['bet_amount'] for h in hands)
                    
                    is_winner = player_key == round_data['winner']
                    st.markdown(f"**{player_name}** {'🏆' if is_winner else ''}")
                    st.write(f"Hands: {len(hands)}")
                    st.write(f"Total Bet: ₹{total_bet}")
                    
                    if hands:
                        for h in hands:
                            st.caption(f"  • ₹{h['bet_amount']} ({h['play_type']})")

def main():
    initialize_session_state()
    
    st.markdown("<h1 class='header-title'>🃏 Teen Patti Tracker</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 🎯 Round {st.session_state.current_round}")
    with col2:
        total_pot = sum(get_current_round_total(pk) for pk in st.session_state.players.keys())
        st.metric("Current Pot", f"₹{total_pot}")
    with col3:
        if st.button("🔄 Reset All", use_container_width=True):
            for key in ['players', 'current_round', 'current_round_hands', 'completed_rounds', 'round_in_progress']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    tabs = st.tabs(["🎮 Current Round", "📊 Statistics", "📜 History"])
    
    with tabs[0]:
        display_hand_entry()
        display_round_completion()
    
    with tabs[1]:
        display_player_stats()
        display_charts()
    
    with tabs[2]:
        display_round_history()

if __name__ == "__main__":
    main()
