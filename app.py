import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Teen Patti Tracker",
    page_icon="🃏",
    layout="wide"
)

def initialize_session_state():
    if 'players' not in st.session_state:
        st.session_state.players = {
            '1': {'name': 'Player 1', 'entries': [], 'status': 'playing', 'won_round': False},
            '2': {'name': 'Player 2', 'entries': [], 'status': 'playing', 'won_round': False},
            '3': {'name': 'Player 3', 'entries': [], 'status': 'playing', 'won_round': False},
            '4': {'name': 'Player 4', 'entries': [], 'status': 'playing', 'won_round': False}
        }
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'completed_rounds' not in st.session_state:
        st.session_state.completed_rounds = []

def get_player_page():
    params = st.query_params
    return params.get('player', None)

def add_entry(player_id, amount):
    entry = {
        'round': st.session_state.current_round,
        'amount': amount,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.players[player_id]['entries'].append(entry)

def get_current_round_total(player_id):
    entries = st.session_state.players[player_id]['entries']
    return sum(e['amount'] for e in entries if e['round'] == st.session_state.current_round)

def get_total_spent(player_id):
    return sum(e['amount'] for e in st.session_state.players[player_id]['entries'])

def display_player_page(player_id):
    player = st.session_state.players[player_id]
    
    st.markdown(f"# 🎴 {player['name']}'s Table")
    
    new_name = st.text_input("Your Name", value=player['name'], key=f"name_{player_id}")
    if new_name != player['name']:
        st.session_state.players[player_id]['name'] = new_name
        st.rerun()
    
    st.markdown(f"### Round {st.session_state.current_round}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your Total This Round", f"₹{get_current_round_total(player_id)}")
    with col2:
        st.metric("Total Spent (All Rounds)", f"₹{get_total_spent(player_id)}")
    
    st.markdown("---")
    
    if player['status'] == 'quit':
        st.warning("🚫 You have quit this round")
        if st.button("↩️ Rejoin Round", use_container_width=True):
            st.session_state.players[player_id]['status'] = 'playing'
            st.rerun()
    elif player['won_round']:
        st.success("🏆 You marked yourself as winner!")
        if st.button("❌ Cancel Win", use_container_width=True):
            st.session_state.players[player_id]['won_round'] = False
            st.rerun()
    else:
        st.markdown("### Add Money (multiples of 5)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ ₹5", use_container_width=True):
                add_entry(player_id, 5)
                st.rerun()
        with col2:
            if st.button("➕ ₹10", use_container_width=True):
                add_entry(player_id, 10)
                st.rerun()
        with col3:
            if st.button("➕ ₹15", use_container_width=True):
                add_entry(player_id, 15)
                st.rerun()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ ₹20", use_container_width=True):
                add_entry(player_id, 20)
                st.rerun()
        with col2:
            if st.button("➕ ₹25", use_container_width=True):
                add_entry(player_id, 25)
                st.rerun()
        with col3:
            if st.button("➕ ₹50", use_container_width=True):
                add_entry(player_id, 50)
                st.rerun()
        
        custom_amount = st.number_input(
            "Or enter custom amount (multiples of 5)",
            min_value=5,
            max_value=1000,
            value=5,
            step=5,
            key=f"custom_{player_id}"
        )
        if st.button("➕ Add Custom Amount", use_container_width=True):
            if custom_amount % 5 == 0:
                add_entry(player_id, custom_amount)
                st.rerun()
            else:
                st.error("Amount must be a multiple of 5!")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚫 Quit Round", use_container_width=True, type="secondary"):
                st.session_state.players[player_id]['status'] = 'quit'
                st.rerun()
        with col2:
            if st.button("🏆 I Won!", use_container_width=True, type="primary"):
                st.session_state.players[player_id]['won_round'] = True
                st.rerun()
    
    st.markdown("---")
    st.markdown("### Your Entries This Round")
    
    current_entries = [e for e in player['entries'] if e['round'] == st.session_state.current_round]
    if current_entries:
        for i, entry in enumerate(current_entries, 1):
            st.write(f"{i}. ₹{entry['amount']} at {entry['timestamp']}")
    else:
        st.info("No entries yet this round")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Summary")
    
    total_rounds_played = len(set(e['round'] for e in player['entries']))
    st.write(f"Rounds Played: {total_rounds_played}")
    st.write(f"Total Money Put In: ₹{get_total_spent(player_id)}")
    
    st.markdown("---")
    st.markdown("[🏠 Go to Dashboard](?)")

def display_dashboard():
    st.markdown("# 🃏 Teen Patti Tracker - Dashboard")
    
    st.markdown(f"### Round {st.session_state.current_round}")
    
    st.markdown("---")
    st.markdown("### 🔗 Player Links (Share these!)")
    
    cols = st.columns(4)
    for i, col in enumerate(cols):
        player_id = str(i + 1)
        player = st.session_state.players[player_id]
        with col:
            st.markdown(f"**{player['name']}**")
            st.markdown(f"[Open Player {i+1} Page](?player={player_id})")
            
            status_icon = "🟢" if player['status'] == 'playing' else "🔴"
            if player['won_round']:
                status_icon = "🏆"
            st.write(f"Status: {status_icon}")
    
    st.markdown("---")
    st.markdown("### 💰 Current Round Summary")
    
    total_pot = 0
    winner = None
    
    cols = st.columns(4)
    for i, col in enumerate(cols):
        player_id = str(i + 1)
        player = st.session_state.players[player_id]
        player_total = get_current_round_total(player_id)
        total_pot += player_total
        
        if player['won_round']:
            winner = player_id
        
        with col:
            status = ""
            if player['status'] == 'quit':
                status = " (Quit)"
            elif player['won_round']:
                status = " 🏆"
            
            st.metric(
                f"{player['name']}{status}",
                f"₹{player_total}"
            )
    
    st.markdown(f"### 🎰 Total Pot: ₹{total_pot}")
    
    if winner:
        winner_name = st.session_state.players[winner]['name']
        st.success(f"🏆 {winner_name} claims the win!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Complete Round & Calculate", use_container_width=True, type="primary"):
            round_data = {
                'round_num': st.session_state.current_round,
                'pot': total_pot,
                'winner': winner,
                'player_totals': {
                    pid: get_current_round_total(pid) 
                    for pid in st.session_state.players
                }
            }
            st.session_state.completed_rounds.append(round_data)
            
            st.session_state.current_round += 1
            for pid in st.session_state.players:
                st.session_state.players[pid]['status'] = 'playing'
                st.session_state.players[pid]['won_round'] = False
            
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Everything", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Aggregate Summary (All Rounds)")
    
    if st.session_state.completed_rounds or any(get_total_spent(pid) > 0 for pid in st.session_state.players):
        summary_data = []
        
        for player_id in st.session_state.players:
            player = st.session_state.players[player_id]
            total_spent = get_total_spent(player_id)
            
            total_won = 0
            rounds_won = 0
            for rd in st.session_state.completed_rounds:
                if rd['winner'] == player_id:
                    total_won += rd['pot']
                    rounds_won += 1
            
            net = total_won - total_spent
            
            summary_data.append({
                'Player': player['name'],
                'Total Spent': total_spent,
                'Total Won': total_won,
                'Net': net,
                'Rounds Won': rounds_won
            })
        
        df = pd.DataFrame(summary_data)
        
        cols = st.columns(4)
        for i, col in enumerate(cols):
            data = summary_data[i]
            with col:
                net = data['Net']
                st.markdown(f"### {data['Player']}")
                st.write(f"💸 Spent: ₹{data['Total Spent']}")
                st.write(f"💰 Won: ₹{data['Total Won']}")
                
                if net >= 0:
                    st.success(f"📈 Net: +₹{net}")
                else:
                    st.error(f"📉 Net: ₹{net}")
                
                st.write(f"🏆 Rounds Won: {data['Rounds Won']}")
        
        if len(st.session_state.completed_rounds) > 0:
            st.markdown("---")
            
            fig = px.bar(
                df,
                x='Player',
                y='Net',
                color='Net',
                color_continuous_scale=['#ff4757', '#ffa502', '#00ff88'],
                title='Net Profit/Loss by Player'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Complete some rounds to see the aggregate summary!")
    
    st.markdown("---")
    st.markdown("### 📜 Round History")
    
    if st.session_state.completed_rounds:
        for rd in reversed(st.session_state.completed_rounds):
            winner_name = st.session_state.players[rd['winner']]['name'] if rd['winner'] else "No winner"
            with st.expander(f"Round {rd['round_num']} - Pot: ₹{rd['pot']} - Winner: {winner_name}"):
                for pid, amount in rd['player_totals'].items():
                    player_name = st.session_state.players[pid]['name']
                    is_winner = pid == rd['winner']
                    st.write(f"{'🏆 ' if is_winner else ''}{player_name}: ₹{amount}")
    else:
        st.info("No completed rounds yet")

def main():
    initialize_session_state()
    
    player_page = get_player_page()
    
    if player_page and player_page in st.session_state.players:
        display_player_page(player_page)
    else:
        display_dashboard()

if __name__ == "__main__":
    main()
