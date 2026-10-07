import streamlit as st
import sqlite3
import os
import requests

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบแจ้งซ่อมออนไลน์", page_icon="🛠️", layout="centered")

# --- แทรก Tailwind CSS ผ่าน CDN พร้อมสไตล์แต่งเสริม ---
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 0.75rem !important;
            border-color: #cbd5e1 !important;
            padding: 0.65rem 1rem !important;
        }
        .stButton button {
            border-radius: 0.75rem !important;
            font-weight: 600 !important;
            transition: all 0.2s;
            background-color: #2563eb !important;
            color: white !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
        }
        .stButton button:hover {
            background-color: #1d4ed8 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
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
        "messages": [{"type": "text", "text": message}]
    }
    try:
        requests.post(url, headers=headers, json=data, timeout=5)
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
        <div class="max-w-md mx-auto pt-8 pb-4 text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl text-3xl mb-4 shadow-sm">🛠️</div>
            <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">ระบบแจ้งซ่อมออนไลน์</h1>
            <p class="text-slate-500 mt-2 text-sm">แพลตฟอร์มแจ้งและติดตามปัญหาอุปกรณ์ IT ภายในองค์กร</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            with st.container():
                st.markdown('<div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-xl mb-4">', unsafe_allow_html=True)
                with st.form("login_form"):
                    username_input = st.text_input("Username", placeholder="ระบุชื่อผู้ใช้งาน")
                    password_input = st.text_input("Password", type="password", placeholder="••••••••")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    submit_login = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
                    
                    if submit_login:
                        conn = sqlite3.connect("repair_system.db")
                        cursor = conn.cursor()
                        cursor.execute("SELECT role, name FROM users WHERE username = ? AND password = ?", (username_input, password_input))
                        user = cursor.fetchone()
                        conn.close()
