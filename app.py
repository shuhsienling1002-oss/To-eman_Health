import streamlit as st
import random

# ==========================================
# 0. 系統設置 (Layer 0: Design)
# ==========================================

st.set_page_config(
    page_title="守護膽曼",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'selected_symptom' not in st.session_state:
    st.session_state['selected_symptom'] = None

# CSS 樣式表：優化按鈕顯示與字體
st.markdown("""
    <style>
    /* 全局字體 */
    html, body, [class*="css"] {
        font-family: "Microsoft JhengHei", sans-serif;
    }
    
    /* 一般選項按鈕 (徵兆選單用) */
    .stButton>button {
        width: 100%;
        min-height: 70px;
        font-size: 24px !important;
        font-weight: bold;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 2px solid #e0e0e0;
    }

    /* 🚨 紅色救命按鈕 (首頁專用) 🚨 */
    /* 這裡設定高度 120px，字體 36px，確保清楚好按 */
    .stButton>button[kind="primary"] {
        height: 120px !important;
        font-size: 36px !important;
        background-color: #d32f2f !important;
        color: white !important;
        border: 2px solid white !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        animation: pulse 2s infinite;
    }

    /* 呼吸燈動畫 */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    /* 溫馨叮嚀框 */
    .care-message-box {
        background-color: #fff3e0;
        border-left: 6px solid #ff9800;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 20px;
        color: #5d4037;
    }

    /* 結果頁：地點標題 */
    .hospital-title {
        font-size: 40px;
        font-weight: 900;
        color: #1a237e;
        text-align: center;
        border-bottom: 4px solid #1a237e;
        padding-bottom: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    
    /* 警示橫幅 */
    .alert-banner {
        padding: 15px;
        color: white;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .bg-red { background-color: #c62828; }
    .bg-yellow { background-color: #fbc02d; color: black !important; }
    .bg-green { background-color: #2e7d32; }
    
    /* SOP 步驟文字 */
    .sop-text {
        font-size: 24px;
        margin: 5px 0;
        padding: 10px;
        background: #f5f5f5;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 資料庫：徵兆大全 (Layer 1: Content)
# ==========================================

# 醫院資訊
HOSPITALS = {
    "mackay": {
        "name": "台東馬偕醫院",
        "tag": "🔴 救命 (中風/心臟/重創)",
        "addr": "台東市長沙街 303 巷 1 號",
        "tel": "089-310-150"
    },
    "chenggong": {
        "name": "成功分院",
        "tag": "🟡 急診 (一般外傷/發燒)",
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

# 徵兆資料庫 (包含完整急症)
SYMPTOMS_DB = {
    # --- 頭部/神經 (致命) ---
    "嘴歪眼斜/單側無力 (中風)": ("RED", "mackay", ["⛔ 絕對不可餵食/餵藥", "🛌 讓患者側躺防嗆到", "⏱️ 記下發作時間"]),
    "劇烈頭痛 (像被雷打到)": ("RED", "mackay", ["🛌 保持安靜躺下", "🚑 立即呼叫救護車"]),
    "意識不清/叫不醒": ("RED", "mackay", ["🗣️ 大聲呼喚檢查反應", "🛌 側躺暢通呼吸道"]),
    "頭暈/天旋地轉": ("GREEN", "health_center", ["🪑 坐下休息防跌倒", "💧 喝溫開水", "💊 若有高血壓請量血壓"]),
    "突然看不見/視力模糊": ("RED", "mackay", ["⛔ 不要揉眼睛", "🚑 這是中風警訊，快去醫院"]),
    
    # --- 胸部/心臟 (致命) ---
    "胸痛 (像石頭壓/冒冷汗)": ("RED", "mackay", ["⛔ 停止所有活動", "🪑 採半坐臥姿勢", "💊 若有舌下含片可使用"]),
    "心跳很快/心悸": ("YELLOW", "chenggong", ["🪑 坐下深呼吸", "⌚ 測量脈搏"]),
    "呼吸困難/喘不過氣": ("RED", "mackay", ["🪑 端坐呼吸(坐著身體前傾)", "👕 解開衣領鈕扣"]),
    "咳血": ("RED", "mackay", ["🥣 保留檢體", "🚑 立即就醫"]),

    # --- 腹部/消化 ---
    "肚子劇痛 (按壓會痛)": ("YELLOW", "chenggong", ["⛔ 暫時禁食", "🌡️ 量測體溫"]),
    "吐血/解黑便": ("RED", "mackay", ["⛔ 禁止飲食", "🚑 收集嘔吐物/拍照"]),
    "嚴重拉肚子/嘔吐": ("YELLOW", "chenggong", ["💧 補充水分/電解質", "💊 攜帶目前用藥"]),
    "無法排尿 (脹痛)": ("YELLOW", "chenggong", ["⛔ 勿強壓膀胱", "🏥 需導尿"]),
    "誤食農藥/毒物": ("RED", "mackay", ["📸 拍下農藥罐子", "⛔ 不要催吐(除非醫生說)", "🚑 叫救護車"]),

    # --- 四肢/外傷 ---
    "骨折 (肢體變形)": ("RED", "mackay", ["⛔ 不要移動患肢", "🪵 就地固定(用紙板/木棍)"]),
    "嚴重割傷 (血流不止)": ("YELLOW", "chenggong", ["🩹 直接加壓止血", "✋ 抬高患肢"]),
    "一般跌倒 (皮肉傷)": ("GREEN", "health_center", ["🧼 清水沖洗傷口", "🩹 消毒包紮"]),
    "跌倒 (撞到頭/想吐)": ("RED", "mackay", ["⛔ 不要睡著，觀察意識", "🚑 腦震盪警訊"]),
    "被蛇/虎頭蜂咬傷": ("YELLOW", "chenggong", ["📸 記住蛇/蜂的特徵", "⛔ 勿切開傷口/勿吸毒", "⌚ 取下戒指/手錶"]),
    "被狗/動物咬傷": ("YELLOW", "chenggong", ["🧼 大量清水沖洗", "🏥 需打狂犬病疫苗"]),

    # --- 全身/其他 ---
    "發高燒 (>38.5度)": ("YELLOW", "chenggong", ["💧 多喝水", "👕 穿透氣衣物散熱"]),
    "血糖過低 (冒冷汗/手抖)": ("YELLOW", "chenggong", ["🍬 吃糖果/喝果汁", "🛌 休息觀察"]),
    "皮膚紅腫/長疹子": ("GREEN", "health_center", ["📷 拍照記錄", "⛔ 勿抓破"]),
    "慢性病拿藥": ("GREEN", "health_center", ["💊 攜帶健保卡", "📅 確認醫生班表"]),
    "身體痠痛/復健": ("GREEN", "health_center", ["🌡️ 熱敷", "💊 貼布"]),
    "只是覺得怪怪的 (虛弱)": ("GREEN", "health_center", ["🛌 多休息", "📞 打電話給子女聊天"])
}

# ==========================================
# 2. 頁面邏輯
# ==========================================

def page_home():
    st.title("🛡️ 守護膽曼")
    
    # 叮嚀區塊
    care_msgs = [
        "👴 VuVu (長輩)，今天天氣變了，衣服穿暖一點。",
        "💊 藥吃過了嗎？不要忘記喔。",
        "💧 多喝水，慢慢走，不要急。",
        "👵 身體不舒服不要忍耐，按下面的按鈕，我們幫你。"
    ]
    st.markdown(f"""
        <div class="care-message-box">
            <b>💌 給長輩的叮嚀：</b><br>
            {random.choice(care_msgs)}
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") 
    
    st.markdown("<h2 style='text-align: center; color: #d32f2f;'>👇 身體不舒服按這裡 👇</h2>", unsafe_allow_html=True)
    
    # 【關鍵修改】使用 use_container_width=True 讓按鈕寬度撐滿容器
    # 高度由 CSS 控制在 120px，字體 36px，清楚但不誇張
    if st.button("🆘\n救命 / 不舒服", type="primary", use_container_width=True):
        st.session_state['page'] = 'symptom_select'
        st.rerun()

    st.write("---")
    
    # 底部電話簿
    with st.expander("📞 醫院電話 (點我打開)", expanded=True):
        st.markdown("**台東馬偕**：089-310150")
        st.markdown("**成功分院**：089-854748")
        st.markdown("**衛生所**：089-831022")

def page_symptom_select():
    st.title("👀 哪裡不舒服？")
    if st.button("🔙 回首頁"):
        st.session_state['page'] = 'home'
        st.rerun()
    
    st.info("請點選下方的情況 (分類找比較快)")
    
    # 使用 Tabs 分類
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 頭/心臟", "🤢 肚子/內科", "🦴 跌倒/外傷", "💊 發燒/其他"])
    
    with tab1:
        st.subheader("頭痛、中風、心臟")
        cols = st.columns(2)
        symptoms = ["嘴歪眼斜/單側無力 (中風)", "劇烈頭痛 (像被雷打到)", "意識不清/叫不醒", 
                   "胸痛 (像石頭壓/冒冷汗)", "呼吸困難/喘不過氣", "心跳很快/心悸", 
                   "突然看不見/視力模糊", "頭暈/天旋地轉"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

    with tab2:
        st.subheader("肚子痛、吐、大小便")
        cols = st.columns(2)
        symptoms = ["肚子劇痛 (按壓會痛)", "吐血/解黑便", "嚴重拉肚子/嘔吐", 
                   "無法排尿 (脹痛)", "誤食農藥/毒物"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

    with tab3:
        st.subheader("流血、骨折、被咬")
        cols = st.columns(2)
        symptoms = ["骨折 (肢體變形)", "嚴重割傷 (血流不止)", "跌倒 (撞到頭/想吐)", 
                   "被蛇/虎頭蜂咬傷", "被狗/動物咬傷", "一般跌倒 (皮肉傷)"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)
                
    with tab4:
        st.subheader("發燒、慢性病、怪怪的")
        cols = st.columns(2)
        symptoms = ["發高燒 (>38.5度)", "血糖過低 (冒冷汗/手抖)", "皮膚紅腫/長疹子", 
                   "慢性病拿藥", "身體痠痛/復健", "只是覺得怪怪的 (虛弱)"]
        for i, sym in enumerate(symptoms):
            if cols[i % 2].button(sym):
                go_to_result(sym)

def go_to_result(symptom):
    st.session_state['selected_symptom'] = symptom
    st.session_state['page'] = 'result'
    st.rerun()

def page_result():
    symptom = st.session_state['selected_symptom']
    level, hosp_key, sop_list = SYMPTOMS_DB.get(symptom, ("GREEN", "health_center", []))
    info = HOSPITALS[hosp_key]
    
    # 警示條
    if level == "RED":
        st.markdown('<div class="alert-banner bg-red">🚨 生命危急！去大醫院</div>', unsafe_allow_html=True)
    elif level == "YELLOW":
        st.markdown('<div class="alert-banner bg-yellow">⚠️ 需看急診！盡快就醫</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-banner bg-green">🟢 一般門診！不用緊張</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown(f"### 您的狀況：{symptom}")
    st.write("---")
    
    # 核心資訊
    st.markdown("### 📍 請前往這裡：")
    st.markdown(f'<div class="hospital-title">{info["name"]}</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size: 24px; padding: 10px; background-color:#fcfcfc; border-radius:10px;">
    <b>說明</b>：{info['tag']}<br>
    <b>電話</b>：{info['tel']}<br>
    <b>地址</b>：{info['addr']}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # SOP
    st.markdown("### 📋 現場該做什麼？")
    for step in sop_list:
        st.markdown(f'<div class="sop-text">{step}</div>', unsafe_allow_html=True)
        
    st.write("---")
    
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
# 3. 主程式入口 (這個就是你之前漏掉的部分)
# ==========================================

if st.session_state['page'] == 'home':
    page_home()
elif st.session_state['page'] == 'symptom_select':
    page_symptom_select()
elif st.session_state['page'] == 'result':
    page_result()
