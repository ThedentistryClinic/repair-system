# --- กรณีที่เป็นช่าง / แอดมิน ---
    elif st.session_state.role == "technician":
        st.markdown("""
            <div class="mb-6 bg-gradient-to-r from-slate-800 to-slate-900 p-6 rounded-2xl text-white shadow-lg">
                <h2 class="text-2xl font-bold">🛠️ ระบบจัดการงานซ่อม (ทีมช่าง)</h2>
                <p class="text-slate-300 text-sm mt-1">ตรวจสอบและอัปเดตสถานะเคสแจ้งซ่อมทั้งหมดจากทุกสาขา</p>
            </div>
        """, unsafe_allow_html=True)
        
        conn = sqlite3.connect("repair_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, reporter, branch, equipment_type, equipment_detail, detail, image_path, status FROM tickets ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            st.markdown(f"<p class='font-bold text-slate-700 mb-4 text-base'>📋 รายการแจ้งซ่อมทั้งหมด ({len(rows)} เคส)</p>", unsafe_allow_html=True)
            for row in rows:
                current_status = row[7] if len(row) > 7 else row[6]
                status_class = (
                    "bg-amber-50 text-amber-700 border-amber-200" if current_status == "รอดำเนินการ" 
                    else ("bg-blue-50 text-blue-700 border-blue-200" if current_status == "กำลังซ่อม" 
                    else "bg-emerald-50 text-emerald-700 border-emerald-200")
                )
                
                # --- ครอบการแสดงผลทั้งหมดให้อยู่ในการ์ด Tailwind สวยงาม ---
                st.markdown(f"""
                    <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm mb-6">
                        <div class="flex justify-between items-center mb-3">
                            <span class="font-bold text-slate-900 text-base">📌 Ticket #{row[0]} | ผู้แจ้ง: <span class="text-blue-600">{row[1]}</span></span>
                            <span class="text-xs px-3 py-1 rounded-full font-bold border {status_class}">สถานะ: {current_status}</span>
                        </div>
                        <div class="grid grid-cols-2 gap-2 text-sm text-slate-600 mb-2">
                            <p><strong>🏢 สาขา:</strong> {row[2]}</p>
                            <p><strong>💻 อุปกรณ์:</strong> {row[3]} ({row[4]})</p>
                        </div>
                        <p class="text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100 mt-2 mb-3"><strong>📝 อาการ:</strong> {row[5]}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # แสดงรูปภาพ (ถ้ามี)
                img_col = row[6] if len(row) > 6 else ""
                if img_col and os.path.exists(img_col):
                    st.image(img_col, caption="รูปภาพหน้างาน", width=250)
                    
                # ส่วนฟอร์มเปลี่ยนสถานะ
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    with col2:
                        status_options = ["รอดำเนินการ", "กำลังซ่อม", "เสร็จสิ้น"]
                        idx = status_options.index(current_status) if current_status in status_options else 0
                        
                        new_status = st.selectbox(f"เปลี่ยนสถานะ #{row[0]}", status_options, index=idx, key=f"status_{row[0]}")
                        if st.button("💾 บันทึกสถานะ", key=f"btn_{row[0]}", use_container_width=True):
                            conn = sqlite3.connect("repair_system.db")
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, row[0]))
                            conn.commit()
                            conn.close()
                            st.success(f"อัปเดต Ticket #{row[0]} สำเร็จ!")
                            st.rerun()
                st.markdown("<div class='my-4 border-b border-slate-200'></div>", unsafe_allow_html=True)
        else:
            st.info("🎉 ยอดเยี่ยม! ตอนนี้ไม่มีเคสแจ้งซ่อมค้างอยู่ในระบบ")
