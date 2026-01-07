import streamlit as st
import datetime

# ==========================================
# 0. 系統設置 (Layer 1: Physics)
# ==========================================

st.set_page_config(
    page_title="膽曼守護 v1.1",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed" # 預設收起側邊欄，減少干擾
)

# 初始化 Session State
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'selected_symptom' not in st.session_state:
    st.session_state['selected_symptom'] = None

# CSS 優化：針對「選項變多」進行排版優化
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 80px; /* 稍微調低高度以容納更多按鈕 */
        font-size: 24px !important;
        font-weight: bold;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    /* 紅色危急區塊 */
    .critical-header {
        color: white;
        background-color: #d32f2f;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* 黃色警告區塊 */
    .warning-header {
        color: black;
        background-color: #ffeb3b;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* 綠色一般區塊 */
    .normal-header {
        color: white;
        background-color: #2e7d32;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* 地點大字體 */
    .location-text {
        font-size: 36px;
        font-weight: 900;
        color: #1a237e;
        border-bottom: 3px solid #1a237e;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 醫療資源與徵兆資料庫 (Database)
# ==========================================

# 醫院靜態資料 (純文字與電話)
HOSPITALS = {
    "mackay": {
        "name": "台東馬偕醫院",
        "desc": "重度急救 (救命用)",
        "address": "台東市長沙街303巷1號",
        "tel": "089-310150"
    },
    "chenggong": {
        "name": "部立台東成功分院",
        "desc": "一般急診 (外傷/發燒)",
        "address": "成功鎮中山東路32號",
        "tel": "089-854748"
    },
    "health_center": {
        "name": "長濱鄉衛生所",
        "desc": "門診/拿藥 (非急診)",
        "address": "長濱鄉長濱村5鄰13號",
        "tel": "089-831022"
    }
}

# 徵兆分流邏輯 (擴充至上限)
# 格式: "症狀名稱": ("等級", "對應醫院代碼", "現場處理建議")
SYMPTOMS_DB = {
    # --- 頭部/神經 (Head/Neuro) ---
    "嘴歪眼斜/單側無力 (中風)": ("RED", "mackay", ["⛔ 絕對不可餵食/餵藥", "🛌 讓患者側躺防嗆到", "⏱️ 記下發作時間"]),
    "劇烈頭痛 (像雷擊)": ("RED", "mackay", ["🛌 保持安靜躺下", "🚑 立即呼叫救護車"]),
    "意識不清/叫不醒": ("RED", "mackay", ["🗣️ 大聲呼喚檢查反應", "🛌 側躺暢通呼吸道"]),
    "頭暈/天旋地轉": ("GREEN", "health_center", ["🪑 坐下休息防跌倒", "💧 喝溫開水"]),
    
    # --- 胸腹/內科 (Chest/Abdomen) ---
    "胸痛 (像石頭壓/冒冷汗)": ("RED", "mackay", ["⛔ 停止所有活動", "🪑 採半坐臥姿勢", "💊 若有舌下含片可使用"]),
    "呼吸困難/喘不過氣": ("RED", "mackay", ["🪑 端坐呼吸(坐著身體前傾)", "👕 解開衣領鈕扣"]),
    "吐血/解黑便": ("RED", "mackay", ["⛔ 禁止飲食", "🚑 收集嘔吐物供醫師參考"]),
    "肚子劇痛 (按壓會痛)": ("YELLOW", "chenggong", ["⛔ 暫時禁食", "🌡️ 量測體溫"]),
    "嚴重拉肚子/嘔吐": ("YELLOW", "chenggong", ["💧 補充水分/電解質", "💊 攜帶目前用藥"]),
    
    # --- 四肢/外傷 (Limbs/Trauma) ---
    "骨折 (肢體變形)": ("RED", "mackay", ["⛔ 不要移動患肢", "🪵 就地固定(用紙板/木棍)"]),
    "嚴重割傷 (血流不止)": ("YELLOW", "chenggong", ["🩹 直接加壓止血", "✋ 抬高患肢"]),
    "被蛇/動物咬傷": ("YELLOW", "chenggong", ["⛔ 勿切開傷口/勿吸毒", "📸 拍下蛇/動物特徵", "⌚ 取下戒指/手錶"]),
    "跌倒 (無法站起)": ("YELLOW", "chenggong", ["⛔ 不要硬拉起來(怕脊椎傷)", "🚑 呼叫 119 協助搬運"]),
    "跌倒 (可站起/輕微)": ("GREEN", "health_center", ["🧊 冰敷紅腫處", "👀 觀察有無頭暈嘔吐"]),
    
    # --- 其他/慢性 (Others) ---
    "發高燒 (>38.5度)": ("YELLOW", "chenggong", ["💧 多喝水", "👕 穿透氣衣物散熱"]),
    "尿不出來 (脹痛)": ("YELLOW", "chenggong", ["⛔ 勿強壓膀胱", "🏥 需導尿"]),
    "眼睛劇痛/視力模糊": ("YELLOW", "chenggong", ["⛔ 勿揉眼睛", "🕶️ 戴墨鏡保護"]),
    "皮膚紅腫/長疹子": ("GREEN", "health_center", ["📷 拍照記錄", "⛔ 勿抓破"]),
    "慢性拿藥/復健": ("GREEN", "health_center", ["💊 攜帶健保卡", "📅 確認醫生班表"])
}

# ==========================================
# 2. 邏輯處理
# ==========================================

def get_triage_info(symptom_name):
    level, hospital_key, sop_steps = SYMPTOMS_DB.get(symptom_name, ("GREEN", "health_center", []))
    hospital_info = HOSPITALS[hospital_key]
    
    # 定義顯示標題與顏色
    if level == "RED":
        header_html = f'<div class="critical-header">🚨 生命危急 (直送大醫院)</div>'
        action_text = "🚑 立刻叫救護車 (119)"
    elif level == "YELLOW":
        header_html = f'<div class="warning-header">⚠️ 需要急診 (盡快就醫)</div>'
        action_text = "🚗 請親友接送 / 叫車"
    else:
        header_html = f'<div class="normal-header">🟢 一般門診 (觀察/拿藥)</div>'
        action_text = "👨‍⚕️ 前往衛生所 / 預約"
        
    return header_html, hospital_info, action_text, sop_steps

# ==========================================
# 3. 介面呈現
# ==========================================

def page_home():
    st.title("🛡️ 膽曼守護")
    st.write("---")
    
    # 極簡首頁，直接引導至症狀選擇
    col1, col2 = st.columns(2)
    with col1:
        st.info("功能選單")
        # 保留簽到但縮小佔比，或單純作為一個選項
        if st.button("☀️ 報平安 (簽到)"):
            st.toast("✅ 已傳送平安訊號")
    
    with col2:
        st.error("緊急功能")
        # 這是主要入口
        if st.button("🆘 身體不舒服", type="primary"):
            st.session_state['page'] = 'symptom_select'
            st.rerun()

    st.markdown("### 📢 最新公告")
    st.info("本週二下午：高醫眼科巡迴醫療 (衛生所)")

def page_symptom_select():
    st.title("👀 請問是哪一種狀況？")
    if st.button("🔙 返回"):
        st.session_state['page'] = 'home'
        st.rerun()
    
    # 使用 Tabs 分類，避免畫面太長老人滑不到
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 頭部/神經", "🫀 胸腹/內科", "🦵 外傷/骨折", "💊 其他狀況"])
    
    with tab1:
        st.subheader("頭痛、頭暈、意識")
        cols = st.columns(2)
        symptoms = ["嘴歪眼斜/單側無力 (中風)", "劇烈頭痛 (像雷擊)", "意識不清/叫不醒", "頭暈/天旋地轉"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

    with tab2:
        st.subheader("胸口痛、肚子痛、嘔吐")
        cols = st.columns(2)
        symptoms = ["胸痛 (像石頭壓/冒冷汗)", "呼吸困難/喘不過氣", "吐血/解黑便", "肚子劇痛 (按壓會痛)", "嚴重拉肚子/嘔吐"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)
                
    with tab3:
        st.subheader("跌倒、流血、被動物咬")
        cols = st.columns(2)
        symptoms = ["骨折 (肢體變形)", "嚴重割傷 (血流不止)", "被蛇/動物咬傷", "跌倒 (無法站起)", "跌倒 (可站起/輕微)"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)
                
    with tab4:
        st.subheader("發燒、小便、皮膚、拿藥")
        cols = st.columns(2)
        symptoms = ["發高燒 (>38.5度)", "尿不出來 (脹痛)", "眼睛劇痛/視力模糊", "皮膚紅腫/長疹子", "慢性拿藥/復健"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

def go_to_result(symptom):
    st.session_state['selected_symptom'] = symptom
    st.session_state['page'] = 'result'
    st.rerun()

def page_result():
    symptom = st.session_state['selected_symptom']
    header_html, hospital, action, sop = get_triage_info(symptom)
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    st.write("---")
    st.markdown(f"**發生狀況**：{symptom}")
    st.markdown(f"**建議行動**：{action}")
    
    st.write("---")
    st.markdown("### 📍 前往地點")
    # 這裡只顯示純文字地點，不顯示地圖
    st.markdown(f'<div class="location-text">{hospital["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**類別**：{hospital['desc']}")
    st.markdown(f"**地址**：{hospital['address']}")
    st.markdown(f"**電話**：{hospital['tel']}")
    
    st.write("---")
    st.markdown("### 📋 現場處理 (SOP)")
    for step in sop:
        st.markdown(f"### {step}") # 使用 h3 讓字體更大
        
    st.write("---")
    if st.button("🔄 重新選擇"):
        st.session_state['page'] = 'symptom_select'
        st.rerun()
    if st.button("🏠 回首頁"):
        st.session_state['page'] = 'home'
        st.rerun()

# ==========================================
# 主流程
# ==========================================

if st.session_state['page'] == 'home':
    page_home()
elif st.session_state['page'] == 'symptom_select':
    page_symptom_select()
elif st.session_state['page'] == 'result':
    page_result()
