import streamlit as st
import sqlite3
import os
import requests

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบแจ้งซ่อมออนไลน์", page_icon="🛠️", layout="centered")

# --- แทรก Tailwind CSS ผ่าน CDN เพื่อความสวยงามพรีเมียม ---
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 0.5rem !important;
            border-color: #cbd5e1 !important;
        }
        .stButton button {
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            transition: all 0.2s;
        }
    </style>
""", unsafe_allow_html=True)

# สร้างโฟลเดอร์เก็บรูปภาพถ้ายังไม่มี
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --- ตั้งค่า LINE Messaging API ---
LINE_CHANNEL_ACCESS_TOKEN = "ofPoijMvVBoLRnT8hfl5p7EmJUJtNacpSkJDTK3FeZPQMuHpTjWyXvcfSuwEOyfvlD4dZ83SoiWP642gwLO06kjySJJxbu9Tu5KT6jYM6JXjPzAxa+Jr5mGoq9vwqhOqhdDDf5FN2obie7O8fvKDtQdB04t89/1O/w1cDnyilFU="
LINE_TO_TARGET_ID = "U556cf026d1abbb03baa3831f15a5b1ec"

def send_line_message(message):
    """ฟังก์ชันสำหรับส่งข้อความแจ้งเตือนผ่าน LINE Messaging API"""
    if LINE_CHANNEL_ACCESS_TOKEN == "ofPoijMvVBoLRnT8hfl5p7EmJUJtNacpSkJDTK3FeZPQMuHpTjWyXvcfSuwEOyfvlD4dZ83SoiWP642gwLO06kjySJJxbu9Tu5KT6jYM6JXjPzAxa+Jr5mGoq9vwqhOqhdDDf5FN2obie7O8fvKDtQdB04t89/1O/w1cDnyilFU=":
        return
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": LINE_TO_TARGET_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"LINE API Response: {response.status_code}")
    except Exception as e:
        print(f"LINE Messaging API Error: {e}")

# --- 1. ตั้งค่าฐานข้อมูล SQLite ---
def init_db():
    conn = sqlite3.connect("repair_system.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            name TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter TEXT,
            branch TEXT,
            equipment_type TEXT,
            equipment_detail TEXT,
            detail TEXT,
            image_path TEXT,
            status TEXT
        )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', '1234', 'technician', 'ช่างใหญ่ ประจำอาคาร')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('user', '1234', 'user', 'สมชาย ใจดี (พนักงาน)')")
    
    conn.commit()
    conn.close()

init_db()

# --- 2. จัดการ Session State สำหรับระบบ Login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

# --- 3. หน้าจอ Login และ Register ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="text-center py-6">
            <h1 class="text-3xl font-extrabold text-slate-800">🛠️ ระบบแจ้งซ่อมออนไลน์</h1>
            <p class="text-slate-500 mt-2">แจ้งปัญหาอุปกรณ์ IT ภายในองค์กรได้อย่างรวดเร็วและแม่นยำ</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username_input = st.text_input("Username")
                password_input = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
                
                if submit_login:
                    conn = sqlite3.connect("repair_system.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT role, name FROM users WHERE username = ? AND password = ?", (username_input, password_input))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username_input
                        st.session_state.role = user[0]
                        st.session_state.name = user[1]
                        st.rerun()
                    else:
                        st.error("❌ Username หรือ Password ไม่ถูกต้อง!")
                        
            st.markdown("""
