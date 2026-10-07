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
        /* ปรับแต่งฟอนต์และกล่องข้อความให้เข้ากับ Tailwind */
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
        return # ถ้ายังไม่ได้ใส่ Token ข้ามไปก่อนเพื่อไม่ให้ติด Error
    
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
                <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl mt-4 text-sm text-slate-700">
                    <p class="font-bold text-blue-900 mb-1">💡 Account ทดสอบระบบ:</p>
                    <p>• <strong>พนักงาน:</strong> <code>user</code> / <code>1234</code></p>
                    <p>• <strong>ช่าง:</strong> <code>admin</code> / <code>1234</code></p>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                reg_name = st.text_input("ชื่อ-นามสกุลจริง", placeholder="เช่น วีระชัย ใจดี")
                reg_user = st.text_input("กำหนด Username", placeholder="เช่น weerachai")
                reg_pass = st.text_input("กำหนด Password", type="password", placeholder="••••••")
                reg_role_choice = st.selectbox("ประเภทผู้ใช้งาน", ["พนักงานทั่วไป (User)", "ช่างซ่อมบำรุง (Technician)"])
                
                submit_reg = st.form_submit_button("ลงทะเบียน", use_container_width=True)
                
                if submit_reg:
                    if not reg_name or not reg_user or not reg_pass:
                        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่องครับ!")
                    else:
                        role_val = "technician" if "ช่าง" in reg_role_choice else "user"
                        conn = sqlite3.connect("repair_system.db")
                        cursor = conn.cursor()
                        try:
                            cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                                           (reg_user, reg_pass, role_val, reg_name))
                            conn.commit()
                            st.success("🎉 สมัครสมาชิกสำเร็จ! สามารถสลับไปแท็บ 'เข้าสู่ระบบ' ได้เลยครับ")
                        except sqlite3.IntegrityError:
                            st.error("❌ Username นี้ถูกใช้งานไปแล้ว กรุณาเปลี่ยนชื่ออื่นครับ")
                        finally:
                            conn.close()

# --- 4. หน้าจอหลัง Login สำเร็จ ---
else:
    st.sidebar.markdown(f"""
        <div class="bg-slate-100 p-4 rounded-xl mb-4 text-center border border-slate-200">
            <p class="text-xs text-slate-500 uppercase tracking-wider">ผู้ใช้งานระบบ</p>
            <p class="text-lg font-bold text-slate-800">{st.session_state.name}</p>
            <span class="inline-block bg-blue-600 text-white text-xs px-2.5 py-1 rounded-full mt-1 font-semibold">{st.session_state.role.upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 ออกจากระบบ", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.sidebar.divider()

    # --- กรณีที่เป็น User ทั่วไป (หน้าแจ้งซ่อม) ---
    if st.session_state.role == "user":
        st.markdown("""
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-slate-800">🛠️ ส่งเรื่องแจ้งซ่อมอุปกรณ์</h2>
                <p class="text-slate-500">กรอกรายละเอียดข้อมูลอุปกรณ์ที่ชำรุดเพื่อให้ทีมช่างเข้าตรวจสอบ</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("repair_form", clear_on_submit=True):
            branch_list = [
                "Rungsit", "Centralnorthvill", "CentralWorld", "Ladprao", 
                "Ekamai", "K-village", "Bangna", "Borwin", "Bangsan", 
                "Sriracha", "Onnut", "Summer hill", "Portobello"
            ]
            selected_branch = st.selectbox("🏢 เลือกสาขาที่ปฏิบัติงาน", branch_list)
            
            equipment_type_list = ["คอมพิวเตอร์", "iPad", "Internet", "Itero", "X-ray", "อื่นๆ"]
            selected_eq_type = st.selectbox("💻 ประเภทอุปกรณ์ที่ชำรุด", equipment_type_list)
            
            equipment_detail = st.text_input("🔍 รายละเอียด/รหัสอุปกรณ์เพิ่มเติม", placeholder="เช่น PC-05 หรือ ปริ้นเตอร์ ชั้น 2")
            detail = st.text_area("📝 รายละเอียดอาการเสีย", placeholder="อธิบายอาการเบื้องต้น เช่น เปิดไม่ติด, เชื่อมต่อเน็ตไม่ได้...")
            
            uploaded_file = st.file_uploader("📸 แนบรูปถ่ายหน้างาน (ถ้ามี)", type=["jpg", "jpeg", "png"])
            
            submitted = st.form_submit_button("🚀 ส่งเรื่องแจ้งซ่อม", use_container_width=True)
            
            if submitted:
                if not equipment_detail or not detail:
                    st.warning("⚠️ กรุณากรอกรหัสอุปกรณ์และรายละเอียดอาการเสียให้ครบถ้วนครับ!")
                else:
                    image_path = ""
                    if uploaded_file is not None:
                        image_path = os.path.join("uploads", uploaded_file.name)
                        with open(image_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # บันทึกลงฐานข้อมูล SQLite
                    conn = sqlite3.connect("repair_system.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO tickets (reporter, branch, equipment_type, equipment_detail, detail, image_path, status) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (st.session_state.name, selected_branch, selected_eq_type, equipment_detail, detail, image_path, "รอดำเนินการ"))
                    
                    ticket_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    # --- ส่งข้อความแจ้งเตือนผ่าน LINE Messaging API ---
                    line_message = (
                        f"🚨 มีแจ้งซ่อมใหม่ (Ticket #{ticket_id})\n"
                        f"----------------------------------\n"
                        f"🏢 สาขา: {selected_branch}\n"
                        f"👤 ผู้แจ้ง: {st.session_state.name}\n"
                        f"💻 อุปกรณ์: {selected_eq_type} ({equipment_detail})\n"
                        f"📝 อาการ: {detail}\n"
                        f"📌 สถานะ: รอดำเนินการ"
                    )
                    send_line_message(line_message)
                    
                    st.success(f"🎉 ส่งเรื่องแจ้งซ่อมสำเร็จ! (Ticket #{ticket_id}) ทีมช่างได้รับเรื่องและแจ้งเตือนผ่าน LINE แล้ว")
                    st.rerun()

        st.divider()
        st.markdown("<h3 class='text-xl font-bold text-slate-800 mb-4'>📋 ประวัติการแจ้งซ่อมของคุณ</h3>", unsafe_allow_html=True)
        conn = sqlite3.connect("repair_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, branch, equipment_type, equipment_detail, detail, image_path, status FROM tickets WHERE reporter = ? ORDER BY id DESC", (st.session_state.name,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            for row in rows:
                status_color = "bg-amber-100 text-amber-800" if row[6] == "รอดำเนินการ" else ("bg-blue-100 text-blue-800" if row[6] == "กำลังซ่อม" else "bg-emerald-100 text-emerald-800")
                st.markdown(f"""
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm mb-4">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-bold text-slate-800">📌 Ticket #{row[0]}</span>
                            <span class="text-xs px-3 py-1 rounded-full font-semibold {status_color}">{row[6]}</span>
                        </div>
                        <p class="text-sm text-slate-600"><strong>🏢 สาขา:</strong> {row[1]}</p>
                        <p class="text-sm text-slate-600"><strong>💻 อุปกรณ์:</strong> {row[2]} ({row[3]})</p>
                        <p class="text-sm text-slate-600 mt-1"><strong>📝 อาการ:</strong> {row[4]}</p>
                    </div>
                """, unsafe_allow_html=True)
                if row[5] and os.path.exists(row[5]):
                    st.image(row[5], caption="รูปภาพหน้างาน", width=250)
        else:
            st.info("คุณยังไม่มีประวัติการแจ้งซ่อม")

    # --- กรณีที่เป็นช่าง / แอดมิน ---
    elif st.session_state.role == "technician":
        st.markdown("""
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-slate-800">🛠️ ระบบจัดการงานซ่อม (ทีมช่าง)</h2>
                <p class="text-slate-500">ตรวจสอบและอัปเดตสถานะเคสแจ้งซ่อมทั้งหมดจากทุกสาขา</p>
            </div>
        """, unsafe_allow_html=True)
        
        conn = sqlite3.connect("repair_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, reporter, branch, equipment_type, equipment_detail, detail, image_path, status FROM tickets ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            st.markdown(f"<p class='font-semibold text-slate-700 mb-4'>📋 รายการแจ้งซ่อมทั้งหมด ({len(rows)} เคส)</p>", unsafe_allow_html=True)
            for row in rows:
                with st.container():
                    current_status = row[7] if len(row) > 7 else row[6]
                    status_color = "bg-amber-100 text-amber-800" if current_status == "รอดำเนินการ" else ("bg-blue-100 text-blue-800" if current_status == "กำลังซ่อม" else "bg-emerald-100 text-emerald-800")
                    
                    st.markdown(f"""
                        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm mb-2">
                            <div class="flex justify-between items-center mb-2">
                                <span class="font-bold text-slate-800">📌 Ticket #{row[0]} | ผู้แจ้ง: {row[1]}</span>
                                <span class="text-xs px-3 py-1 rounded-full font-semibold {status_color}">สถานะ: {current_status}</span>
                            </div>
                            <p class="text-sm text-slate-600"><strong>🏢 สาขา:</strong> {row[2]}</p>
                            <p class="text-sm text-slate-600"><strong>💻 อุปกรณ์:</strong> {row[3]} ({row[4]})</p>
                            <p class="text-sm text-slate-600 mt-1"><strong>📝 อาการ:</strong> {row[5]}</p>
                        </div>
                    
                    
                    img_col = row[6] if len(row) > 6 else ""
                    if img_col and os.path.exists(img_col):
                        st.image(img_col, caption="รูปภาพหน้างาน", width=200)
                        
                    col1, col2 = st.columns([2, 1])
                    with col2:
                        status_options = ["รอดำเนินการ", "กำลังซ่อม", "เสร็จสิ้น"]
                        idx = status_options.index(current_status) if current_status in status_options else 0
                        
                        new_status = st.selectbox(f"เปลี่ยนสถานะ #{row[0]}", status_options, index=idx, key=f"status_{row[0]}")
                        if st.button("อัปเดตสถานะ", key=f"btn_{row[0]}", use_container_width=True):
                            conn = sqlite3.connect("repair_system.db")
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, row[0]))
                            conn.commit()
                            conn.close()
                            st.success(f"อัปเดต Ticket #{row[0]} สำเร็จ!")
                            st.rerun()
                    st.divider()
        else:
            st.info("🎉 ยอดเยี่ยม! ตอนนี้ไม่มีเคสแจ้งซ่อมค้างอยู่ในระบบ")
