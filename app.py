import streamlit as st
import random

# ==========================================
# 0. 系統設置與視覺優化 (Layer 0: Design)
# ==========================================

st.set_page_config(
    page_title="守護膽曼",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化狀態
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'selected_symptom' not in st.session_state:
    st.session_state['selected_symptom'] = None

# CSS 樣式表：針對高齡者優化 (修正版：按鈕超大、置中)
st.markdown("""
    <style>
    /* 全局字體設定 */
    html, body, [class*="css"] {
        font-family: "Microsoft JhengHei", sans-serif;
    }
    
    /* 一般按鈕樣式 (選項用) */
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 28px !important;
        font-weight: bold;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 2px solid #ddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* 🚨 紅色救命按鈕專屬樣式 (特大號) 🚨 */
    /* 透過 type="primary" 來鎖定這顆按鈕 */
    .stButton>button[kind="primary"] {
        height: 180px !important;       /* 高度加大 */
        font-size: 50px !important;     /* 字體超大 */
        background-color: #d32f2f !important;
        color: white !important;
        border: 4px solid white !important;
        box-shadow: 0 0 15px rgba(211, 47, 47, 0.6) !important;
        animation: pulse 2s infinite;   /* 呼吸燈動畫 */
    }

    /* 呼吸燈動畫定義 */
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 20px rgba(211, 47, 47, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); }
    }

    /* 溫馨叮嚀區塊 */
    .care-message-box {
        background-color: #fff3e0;
        border-left: 8px solid #ff9800;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        font-size: 24px;
        font-weight: 500;
        color: #5d4037;
        line-height: 1.5;
    }

    /* 結果頁：醫院名稱大標題 */
    .hospital-title {
        font-size: 48px;
        font-weight: 900;
        color: #1a237e;
        text-align: center;
        border: 4px solid #1a237e;
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
        background-color: #e8eaf6;
    }

    /* 警示橫幅 */
    .alert-banner {
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .bg-red { background-color: #c62828; }
    .bg-yellow { background-color: #fbc02d; color: black !important; }
    .bg-green { background-color: #2e7d32; }
    
    /* SOP 步驟 */
    .sop-step {
        font-size: 26px;
        margin-bottom: 12px;
        padding: 15px;
        background-color: #f5f5f5;
        border-left: 5px solid #757575;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 資料庫：叮嚀語與醫療資訊 (Layer 1: Content)
# ==========================================

# 老人的叮嚀語錄
CARE_MESSAGES = [
    "👴 VuVu (阿公/阿嬤)，今天有比較冷喔，衣服多穿一件！",
    "💊 今天的藥吃了嗎？不要忘記喔！",
    "💧 水要多喝一點，不要等到口渴才喝。",
    "🚶 走路慢慢走，不要急，跌倒很痛喔。",
    "👵 身體不舒服不要忍耐，按下面紅色的大按鈕，我們會幫你。"
]

# 醫院資訊 (純文字版)
HOSPITALS = {
    "mackay": {
        "name": "台東馬偕醫院",
        "tag": "🔴 救命用 (中風/心臟)",
        "addr": "台東市長沙街 303 巷 1 號",
        "tel": "089-310-150"
    },
    "chenggong": {
        "name": "成功分院",
        "tag": "🟡 急診 (外傷/發燒)",
        "addr": "成功鎮中山東路 32 號",
        "tel": "089-854-748"
    },
    "health_center": {
        "name": "長濱衛生所",
        "tag": "🟢 門診 (拿藥/看醫生)",
        "addr": "長濱鄉長濱村 5 鄰 13 號",
        "tel": "089-831-022"
    }
}

# 徵兆與分流邏輯
SYMPTOMS_DB = {
    # --- 危急 (馬偕) ---
    "嘴歪眼斜 (中風)": ("RED", "mackay", ["⛔ 絕對不可餵食/餵藥", "🛌 側躺 (怕嘔吐)", "⏱️ 記下發作時間"]),
    "胸口痛 (像石頭壓)": ("RED", "mackay", ["⛔ 停止走動", "🪑 坐著休息", "💊 含舌下片(若有)"]),
    "意識不清/叫不醒": ("RED", "mackay", ["🗣️ 大聲叫他", "🛌 保持側躺"]),
    "嚴重骨折 (變形)": ("RED", "mackay", ["⛔ 不要亂動患肢", "🪵 找東西固定"]),
    
    # --- 緊急 (成功) ---
    "肚子劇痛": ("YELLOW", "chenggong", ["⛔ 暫時不要吃東西", "🌡️ 量體溫"]),
    "割傷流血不止": ("YELLOW", "chenggong", ["🩹 用力按住傷口", "✋ 手舉高"]),
    "嚴重跌倒 (痛)": ("YELLOW", "chenggong", ["⛔ 脊椎痛就不要動", "🚑 叫救護車搬運"]),
    "發高燒 (>38度)": ("YELLOW", "chenggong", ["💧 多喝水", "👕 穿透氣衣服"]),
    "被動物/蛇咬傷": ("YELLOW", "chenggong", ["📸 記住蛇的樣子", "⛔ 不要用嘴吸毒"]),
    
    # --- 一般 (衛生所) ---
    "頭暈/輕微頭痛": ("GREEN", "health_center", ["🪑 坐下休息", "💧 喝溫水"]),
    "眼睛癢/痛": ("GREEN", "health_center", ["⛔ 不要揉眼睛", "🕶️ 戴墨鏡"]),
    "慢性拿藥": ("GREEN", "health_center", ["💊 帶健保卡", "📅 確認醫生時間"]),
    "皮膚癢/紅腫": ("GREEN", "health_center", ["📸 拍照給醫生看", "⛔ 不要抓破"])
}

# ==========================================
# 2. 頁面邏輯 (UI Functions)
# ==========================================

def page_home():
    st.title("🛡️ 守護膽曼")
    
    # 顯示叮嚀的話
    daily_msg = random.choice(CARE_MESSAGES)
    st.markdown(f"""
        <div class="care-message-box">
            <b>💌 給長輩的叮嚀：</b><br>
            {daily_msg}
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") 
    st.write("") 
    
    # 標題指引
    st.markdown("<h2 style='text-align: center; color: #d32f2f; margin-bottom: 10px;'>👇 身體不舒服按這裡 👇</h2>", unsafe_allow_html=True)
    
    # --- 關鍵修改：紅色大按鈕 ---
    # use_container_width=True 會讓按鈕填滿寬度（置中效果）
    # type="primary" 會吃到上面 CSS 定義的紅色大樣式
    if st.button("🆘\n\n救 命 / 不 舒 服", type="primary", use_container_width=True):
        st.session_state['page'] = 'symptom_select'
        st.rerun()

    st.write("")
    st.write("")
    st.write("---")
    
    # 底部靜態電話表
    with st.expander("📞 醫院電話簿 (點擊展開)", expanded=True):
        st.markdown("### **台東馬偕** (救命)：089-310150")
        st.markdown("### **成功分院** (急診)：089-854748")
        st.markdown("### **衛生所** (看病)：089-831022")

def page_symptom_select():
    st.title("👀 哪裡不舒服？")
    
    if st.button("🔙 回首頁 (按錯了)"):
        st.session_state['page'] = 'home'
        st.rerun()
    
    # 分類籤 (Tabs)
    tab1, tab2, tab3 = st.tabs(["🧠 頭/胸/肚子", "🦵 手腳/外傷", "💊 其他/發燒"])
    
    with tab1:
        st.info("頭暈、胸口痛、肚子痛...")
        cols = st.columns(2)
        symptoms = ["嘴歪眼斜 (中風)", "胸口痛 (像石頭壓)", "意識不清/叫不醒", "肚子劇痛", "頭暈/輕微頭痛"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

    with tab2:
        st.info("跌倒、流血、骨折...")
        cols = st.columns(2)
        symptoms = ["嚴重骨折 (變形)", "割傷流血不止", "嚴重跌倒 (痛)", "被動物/蛇咬傷"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)
                
    with tab3:
        st.info("發燒、眼睛、皮膚...")
        cols = st.columns(2)
        symptoms = ["發高燒 (>38度)", "眼睛癢/痛", "皮膚癢/紅腫", "慢性拿藥"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

def go_to_result(symptom):
    st.session_state['selected_symptom'] = symptom
    st.session_state['page'] = 'result'
    st.rerun()

def page_result():
    symptom = st.session_state['selected_symptom']
    # 獲取資料，若無資料則回傳預設值
    level, hosp_key, sop_list = SYMPTOMS_DB.get(symptom, ("GREEN", "health_center", []))
    info = HOSPITALS[hosp_key]
    
    # 顯示頂部警示條
    if level == "RED":
        st.markdown('<div class="alert-banner bg-red">🚨 生命危急！去大醫院</div>', unsafe_allow_html=True)
    elif level == "YELLOW":
        st.markdown('<div class="alert-banner bg-yellow">⚠️ 需看急診！盡快就醫</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-banner bg-green">🟢 一般門診！不用緊張</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown(f"### 您的狀況：{symptom}")
    st.write("---")
    
    # 核心：地點顯示
    st.markdown("### 📍 請前往這裡：")
    st.markdown(f'<div class="hospital-title">{info["name"]}</div>', unsafe_allow_html=True)
    
    # 地址與電話 (加大顯示)
    st.markdown(f"""
    <div style="font-size: 26px; padding: 15px; background-color: #fcfcfc; border-radius: 10px; margin-top: 10px;">
    <b>說明</b>：{info['tag']}<br>
    <b>電話</b>：{info['tel']}<br>
    <b>地址</b>：{info['addr']}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # 現場 SOP
    st.markdown("### 📋 現在該做什麼？")
    for step in sop_list:
        st.markdown(f'<div class="sop-step">{step}</div>', unsafe_allow_html=True)
        
    st.write("---")
    
    # 底部按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 重選"):
            st.session_state['page'] = 'symptom_select'
            st.rerun()
    with col2:
        if st.button("🏠 回首頁"):
            st.session_state['page'] = 'home'
            st.rerun()

# ==========================================
# 3. 主程式入口
# ==========================================

if st.session_state['page'] == 'home':
    page_home()
elif st.session_state['page'] == 'symptom_select':
    page_symptom_select()
elif st.session_state['page'] == 'result':
    page_result()
