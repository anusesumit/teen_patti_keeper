import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(
    page_title="Teen Patti Tracker",
    page_icon="🃏",
    layout="wide"
)

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY DEFAULT 1,
            current_round INTEGER DEFAULT 1,
            data JSONB DEFAULT '{}'::jsonb
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100),
            status VARCHAR(20) DEFAULT 'playing',
            won_round BOOLEAN DEFAULT FALSE
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            player_id VARCHAR(10),
            round_num INTEGER,
            amount INTEGER,
            timestamp VARCHAR(20)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS completed_rounds (
            id SERIAL PRIMARY KEY,
            round_num INTEGER,
            pot INTEGER,
            winner VARCHAR(10),
            player_totals JSONB
        )
    ''')
    
    cur.execute("SELECT COUNT(*) FROM game_state")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO game_state (id, current_round) VALUES (1, 1)")
    
    cur.execute("SELECT COUNT(*) FROM players")
    if cur.fetchone()[0] == 0:
        for i in range(1, 5):
            cur.execute(
                "INSERT INTO players (id, name, status, won_round) VALUES (%s, %s, 'playing', FALSE)",
                (str(i), f'Player {i}')
            )
    
    conn.commit()
    cur.close()
    conn.close()

def get_current_round():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_round FROM game_state WHERE id = 1")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else 1

def set_current_round(round_num):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE game_state SET current_round = %s WHERE id = 1", (round_num,))
    conn.commit()
    cur.close()
    conn.close()

def get_player(player_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM players WHERE id = %s", (player_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return dict(result) if result else None

def get_all_players():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM players ORDER BY id")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return {r['id']: dict(r) for r in results}

def update_player(player_id, name=None, status=None, won_round=None):
    conn = get_db_connection()
    cur = conn.cursor()
    updates = []
    values = []
    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if status is not None:
        updates.append("status = %s")
        values.append(status)
    if won_round is not None:
        updates.append("won_round = %s")
        values.append(won_round)
    
    if updates:
        values.append(player_id)
        cur.execute(f"UPDATE players SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    cur.close()
    conn.close()

def add_entry(player_id, amount, round_num):
    conn = get_db_connection()
    cur = conn.cursor()
    timestamp = datetime.now().strftime("%H:%M:%S")
    cur.execute(
        "INSERT INTO entries (player_id, round_num, amount, timestamp) VALUES (%s, %s, %s, %s)",
        (player_id, round_num, amount, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_entries(player_id, round_num=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if round_num:
        cur.execute(
            "SELECT * FROM entries WHERE player_id = %s AND round_num = %s ORDER BY id",
            (player_id, round_num)
        )
    else:
        cur.execute("SELECT * FROM entries WHERE player_id = %s ORDER BY id", (player_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in results]

def get_current_round_total(player_id, round_num):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM entries WHERE player_id = %s AND round_num = %s",
        (player_id, round_num)
    )
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def get_total_spent(player_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM entries WHERE player_id = %s", (player_id,))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def get_total_won(player_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(pot), 0) FROM completed_rounds WHERE winner = %s", (player_id,))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def get_rounds_won(player_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM completed_rounds WHERE winner = %s", (player_id,))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def save_completed_round(round_num, pot, winner, player_totals):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO completed_rounds (round_num, pot, winner, player_totals) VALUES (%s, %s, %s, %s)",
        (round_num, pot, winner, json.dumps(player_totals))
    )
    conn.commit()
    cur.close()
    conn.close()

def get_completed_rounds():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM completed_rounds ORDER BY round_num DESC")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in results]

def reset_all():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries")
    cur.execute("DELETE FROM completed_rounds")
    cur.execute("UPDATE game_state SET current_round = 1 WHERE id = 1")
    cur.execute("UPDATE players SET status = 'playing', won_round = FALSE")
    conn.commit()
    cur.close()
    conn.close()

def reset_for_new_round():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE players SET status = 'playing', won_round = FALSE")
    conn.commit()
    cur.close()
    conn.close()

def get_player_page():
    params = st.query_params
    return params.get('player', None)

def display_player_page(player_id):
    current_round = get_current_round()
    player = get_player(player_id)
    
    st.markdown(f"# 🎴 {player['name']}'s Table")
    
    new_name = st.text_input("Your Name", value=player['name'], key=f"name_{player_id}")
    if new_name != player['name']:
        update_player(player_id, name=new_name)
        st.rerun()
    
    st.markdown(f"### Round {current_round}")
    
    total_spent = get_total_spent(player_id)
    total_won = get_total_won(player_id)
    net = total_won - total_spent
    rounds_won = get_rounds_won(player_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("This Round", f"₹{get_current_round_total(player_id, current_round)}")
    with col2:
        st.metric("Total Spent", f"₹{total_spent}")
    with col3:
        st.metric("Total Won", f"₹{total_won}")
    
    if net >= 0:
        st.success(f"📈 **Net Profit: +₹{net}** | Rounds Won: {rounds_won}")
    else:
        st.error(f"📉 **Net Loss: ₹{net}** | Rounds Won: {rounds_won}")
    
    st.markdown("---")
    
    if player['status'] == 'quit':
        st.warning("🚫 You have quit this round")
        if st.button("↩️ Rejoin Round", use_container_width=True):
            update_player(player_id, status='playing')
            st.rerun()
    elif player['won_round']:
        st.success("🏆 You marked yourself as winner!")
        if st.button("❌ Cancel Win", use_container_width=True):
            update_player(player_id, won_round=False)
            st.rerun()
    else:
        st.markdown("### Add Money")
        
        amounts = [5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120]
        
        row1 = st.columns(4)
        for i, amt in enumerate(amounts[:4]):
            with row1[i]:
                if st.button(f"₹{amt}", key=f"btn_{amt}_{player_id}", use_container_width=True):
                    add_entry(player_id, amt, current_round)
                    st.rerun()
        
        row2 = st.columns(4)
        for i, amt in enumerate(amounts[4:8]):
            with row2[i]:
                if st.button(f"₹{amt}", key=f"btn_{amt}_{player_id}", use_container_width=True):
                    add_entry(player_id, amt, current_round)
                    st.rerun()
        
        row3 = st.columns(3)
        for i, amt in enumerate(amounts[8:]):
            with row3[i]:
                if st.button(f"₹{amt}", key=f"btn_{amt}_{player_id}", use_container_width=True):
                    add_entry(player_id, amt, current_round)
                    st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚫 Quit Round", use_container_width=True, type="secondary"):
                update_player(player_id, status='quit')
                st.rerun()
        with col2:
            if st.button("🏆 I Won!", use_container_width=True, type="primary"):
                update_player(player_id, won_round=True)
                st.rerun()
    
    st.markdown("---")
    st.markdown("### Your Entries This Round")
    
    current_entries = get_entries(player_id, current_round)
    if current_entries:
        for i, entry in enumerate(current_entries, 1):
            st.write(f"{i}. ₹{entry['amount']} at {entry['timestamp']}")
    else:
        st.info("No entries yet this round")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Summary")
    
    all_entries = get_entries(player_id)
    total_rounds_played = len(set(e['round_num'] for e in all_entries)) if all_entries else 0
    st.write(f"Rounds Played: {total_rounds_played}")
    st.write(f"Total Money Put In: ₹{get_total_spent(player_id)}")
    
    st.markdown("---")
    st.markdown("[🏠 Go to Dashboard](?)")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

def display_dashboard():
    current_round = get_current_round()
    players = get_all_players()
    
    st.markdown("# 🃏 Teen Patti Tracker - Dashboard")
    
    col_title, col_refresh = st.columns([3, 1])
    with col_title:
        st.markdown(f"### Round {current_round}")
    with col_refresh:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔗 Player Links (Share these!)")
    
    cols = st.columns(4)
    for i, col in enumerate(cols):
        player_id = str(i + 1)
        player = players.get(player_id, {})
        with col:
            st.markdown(f"**{player.get('name', f'Player {i+1}')}**")
            st.markdown(f"[Open Player {i+1} Page](?player={player_id})")
            
            status_icon = "🟢" if player.get('status') == 'playing' else "🔴"
            if player.get('won_round'):
                status_icon = "🏆"
            st.write(f"Status: {status_icon}")
    
    st.markdown("---")
    st.markdown("### 💰 Current Round Summary")
    
    total_pot = 0
    winner = None
    
    cols = st.columns(4)
    for i, col in enumerate(cols):
        player_id = str(i + 1)
        player = players.get(player_id, {})
        player_total = get_current_round_total(player_id, current_round)
        total_pot += player_total
        
        if player.get('won_round'):
            winner = player_id
        
        with col:
            status = ""
            if player.get('status') == 'quit':
                status = " (Quit)"
            elif player.get('won_round'):
                status = " 🏆"
            
            st.metric(
                f"{player.get('name', f'Player {i+1}')}{status}",
                f"₹{player_total}"
            )
    
    st.markdown(f"### 🎰 Total Pot: ₹{total_pot}")
    
    if winner:
        winner_name = players.get(winner, {}).get('name', 'Unknown')
        st.success(f"🏆 {winner_name} claims the win!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Complete Round & Calculate", use_container_width=True, type="primary"):
            player_totals = {
                pid: get_current_round_total(pid, current_round)
                for pid in ['1', '2', '3', '4']
            }
            save_completed_round(current_round, total_pot, winner, player_totals)
            set_current_round(current_round + 1)
            reset_for_new_round()
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Everything", use_container_width=True):
            reset_all()
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Aggregate Summary (All Rounds)")
    
    completed_rounds = get_completed_rounds()
    
    if completed_rounds or any(get_total_spent(pid) > 0 for pid in ['1', '2', '3', '4']):
        summary_data = []
        
        for player_id in ['1', '2', '3', '4']:
            player = players.get(player_id, {})
            total_spent = get_total_spent(player_id)
            
            total_won = 0
            rounds_won = 0
            for rd in completed_rounds:
                if rd['winner'] == player_id:
                    total_won += rd['pot']
                    rounds_won += 1
            
            net = total_won - total_spent
            
            summary_data.append({
                'Player': player.get('name', f'Player {player_id}'),
                'Total Spent': total_spent,
                'Total Won': total_won,
                'Net': net,
                'Rounds Won': rounds_won
            })
        
        df = pd.DataFrame(summary_data)
        
        cols = st.columns(4)
        for i, col in enumerate(cols):
            d = summary_data[i]
            with col:
                net = d['Net']
                st.markdown(f"### {d['Player']}")
                st.write(f"💸 Spent: ₹{d['Total Spent']}")
                st.write(f"💰 Won: ₹{d['Total Won']}")
                
                if net >= 0:
                    st.success(f"📈 Net: +₹{net}")
                else:
                    st.error(f"📉 Net: ₹{net}")
                
                st.write(f"🏆 Rounds Won: {d['Rounds Won']}")
        
        if len(completed_rounds) > 0:
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
    
    if completed_rounds:
        for rd in completed_rounds:
            winner_name = players.get(rd['winner'], {}).get('name', 'No winner') if rd['winner'] else "No winner"
            with st.expander(f"Round {rd['round_num']} - Pot: ₹{rd['pot']} - Winner: {winner_name}"):
                player_totals = rd['player_totals'] if isinstance(rd['player_totals'], dict) else json.loads(rd['player_totals'])
                for pid, amount in player_totals.items():
                    player_name = players.get(pid, {}).get('name', f'Player {pid}')
                    is_winner = pid == rd['winner']
                    st.write(f"{'🏆 ' if is_winner else ''}{player_name}: ₹{amount}")
    else:
        st.info("No completed rounds yet")

def main():
    init_db()
    
    player_page = get_player_page()
    
    if player_page and player_page in ['1', '2', '3', '4']:
        display_player_page(player_page)
    else:
        display_dashboard()

if __name__ == "__main__":
    main()
