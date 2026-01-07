import streamlit as st
import datetime
import pandas as pd

# ==========================================
# 0. 系統設置與物理參數 (Layer 1: Physics)
# ==========================================

st.set_page_config(
    page_title="膽曼守護 Danman Guardian",
    page_icon="🛡️",
    layout="centered", # 手機版面模擬
    initial_sidebar_state="expanded"
)

# 模擬資料庫與 Session State 初始化
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'user_status' not in st.session_state:
    st.session_state['user_status'] = '尚未簽到'
if 'last_checkin' not in st.session_state:
    st.session_state['last_checkin'] = None
if 'selected_symptom' not in st.session_state:
    st.session_state['selected_symptom'] = None

# 醫療地理拓撲 (Hard-Coded Triage Logic)
# 經緯度僅為示意，用於地圖導航
HOSPITALS = {
    "chenggong": {
        "name": "衛福部台東醫院-成功分院",
        "type": "地區醫院 (一般急診)",
        "dist": "20 min",
        "lat": 23.100, "lon": 121.370
    },
    "mackay": {
        "name": "台東馬偕紀念醫院",
        "type": "重度級急救責任醫院 (救命)",
        "dist": "75 min",
        "lat": 22.759, "lon": 121.144
    },
    "health_center": {
        "name": "長濱鄉衛生所",
        "type": "基層醫療 (門診)",
        "dist": "10 min",
        "lat": 23.316, "lon": 121.453
    }
}

# CSS 優化：加大按鈕，提高老人可讀性
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 30px !important;
        font-weight: bold;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .red-alert {
        color: white;
        background-color: #d32f2f;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
    }
    .yellow-alert {
        color: black;
        background-color: #ffeb3b;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 邏輯核心：檢傷分類引擎 (Triage Engine)
# ==========================================

def get_triage_result(symptom_category, specific_symptom):
    """
    輸入：症狀
    輸出：策略 (去哪裡、怎麼做)
    邏輯：FP-CRF 物理限制審計
    """
    
    # --- 紅色警戒區 (RED): 致命風險，必須去遠的大醫院 ---
    if specific_symptom in ["講話不清/嘴歪 (中風)", "胸口像石頭壓 (心梗)", "意識不清"]:
        return {
            "level": "RED",
            "hospital": HOSPITALS["mackay"],
            "action": "🚑 立刻叫救護車 (119)",
            "warning": "🚨 禁止前往成功分院！(無設備)",
            "sop": [
                "1. 絕對不要喝水或吃藥",
                "2. 讓患者側躺 (避免嘔吐噎到)",
                "3. 記下現在時間 (黃金3小時)",
                "4. 保持通話，救護車已在路上"
            ]
        }
    
    # --- 黃色警戒區 (YELLOW): 急性但非致命 ---
    elif specific_symptom in ["跌倒 (意識清醒)", "割傷流血", "肚子劇痛", "發高燒"]:
        return {
            "level": "YELLOW",
            "hospital": HOSPITALS["chenggong"],
            "action": "🚗 請親友接送或叫車",
            "warning": "前往最近的急診處理",
            "sop": [
                "1. 攜帶健保卡",
                "2. 若有傷口，用乾淨布加壓止血",
                "3. 準備平時吃的藥袋"
            ]
        }
    
    # --- 綠色觀察區 (GREEN): 慢性/輕微 ---
    else:
        return {
            "level": "GREEN",
            "hospital": HOSPITALS["health_center"],
            "action": "👨‍⚕️ 前往衛生所 / 視訊問診",
            "warning": "不用跑急診，預約門診即可",
            "sop": [
                "1. 查詢巡迴醫療時間",
                "2. 多喝水，多休息",
                "3. 若症狀變嚴重請重按 APP"
            ]
        }

# ==========================================
# 2. 介面層：前端顯示 (User Interface)
# ==========================================

def page_home():
    st.title("🛡️ 膽曼守護")
    st.markdown("### Danman Guardian (長濱鄉)")
    st.markdown("---")
    
    # 顯示當前狀態
    if st.session_state['user_status'] == '已簽到':
        st.success(f"✅ 今天已報平安 ({st.session_state['last_checkin']})")
    else:
        st.warning("⚠️ 今天尚未簽到")

    # 按鈕區 (Grid Layout)
    col1, col2 = st.columns(2)
    
    with col1:
        # Mipaliw 簽到按鈕
        if st.button("☀️\n我很好\n(簽到)"):
            st.session_state['user_status'] = '已簽到'
            st.session_state['last_checkin'] = datetime.datetime.now().strftime("%H:%M")
            st.rerun()
            
    with col2:
        # 求救按鈕
        if st.button("🆘\n不舒服\n(求救)"):
            st.session_state['page'] = 'symptom_check'
            st.rerun()

def page_symptom_check():
    st.title("👀 哪裡不舒服？")
    if st.button("🔙 返回首頁"):
        st.session_state['page'] = 'home'
        st.rerun()
        
    st.markdown("### 請點選身體部位：")
    
    # 這裡模擬「圖像化」選擇，實際 APP 會是用圖片點擊
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🧠 頭部/臉部")
        if st.button("頭暈 / 頭痛"):
            go_to_result("Head", "頭暈 / 頭痛")
        if st.button("講話不清/嘴歪 (中風)"):
            go_to_result("Head", "講話不清/嘴歪 (中風)")
            
    with col2:
        st.info("🫀 胸部/腹部")
        if st.button("胸口像石頭壓 (心梗)"):
            go_to_result("Chest", "胸口像石頭壓 (心梗)")
        if st.button("肚子劇痛"):
            go_to_result("Chest", "肚子劇痛")
            
    col3, col4 = st.columns(2)
    with col3:
        st.info("🦵 四肢/外傷")
        if st.button("跌倒 (意識清醒)"):
            go_to_result("Limb", "跌倒 (意識清醒)")
        if st.button("割傷流血"):
            go_to_result("Limb", "割傷流血")
            
    with col4:
        st.info("💊 其他")
        if st.button("拿藥 / 眼睛癢"):
            go_to_result("Other", "拿藥 / 眼睛癢")

def go_to_result(category, symptom):
    st.session_state['selected_symptom'] = symptom
    st.session_state['page'] = 'result'
    st.rerun()

def page_result():
    symptom = st.session_state['selected_symptom']
    result = get_triage_result("General", symptom)
    
    # 根據等級顯示不同顏色的標頭
    if result['level'] == 'RED':
        st.markdown(f'<div class="red-alert">🚨 {result["action"]}</div>', unsafe_allow_html=True)
    elif result['level'] == 'YELLOW':
        st.markdown(f'<div class="yellow-alert">⚠️ {result["action"]}</div>', unsafe_allow_html=True)
    else:
        st.success(f"✅ {result['action']}")
        
    st.markdown("---")
    
    # 顯示核心決策資訊
    st.markdown(f"### 您的症狀：{symptom}")
    st.markdown(f"### 🏥 建議醫院：**{result['hospital']['name']}**")
    st.markdown(f"**車程預估**：{result['hospital']['dist']}")
    
    if 'warning' in result:
        st.error(f"**注意**：{result['warning']}")
        
    # 現場 SOP 指導
    st.markdown("### 📋 現場該做什麼？")
    for step in result['sop']:
        st.markdown(f"- {step}")
        
    st.markdown("---")
    
    # 模擬地圖 (簡單顯示位置)
    st.markdown("#### 📍 導航地圖")
    map_data = pd.DataFrame([
        {'lat': 23.230, 'lon': 121.480, 'name': '目前位置(膽曼)'}, # 膽曼村約略位置
        {'lat': result['hospital']['lat'], 'lon': result['hospital']['lon'], 'name': '目標醫院'}
    ])
    st.map(map_data, zoom=9)

    if st.button("🔄 重新開始"):
        st.session_state['page'] = 'home'
        st.session_state['selected_symptom'] = None
        st.rerun()

# ==========================================
# 3. 側邊欄：社區戰情室 (Admin/Cloud View)
# ==========================================

with st.sidebar:
    st.header("🏢 社區戰情室")
    st.markdown("*(村長/照服員專用)*")
    
    st.markdown("---")
    st.markdown("**目前全村狀態**")
    st.metric("正常 (已簽到)", "42 人", "+2")
    st.metric("未簽到 (需訪視)", "3 人", "-1", delta_color="inverse")
    
    st.markdown("---")
    st.write("模擬資料串接：")
    st.json({
        "User_ID": "Danman_007",
        "Age": 82,
        "Status": st.session_state['user_status'],
        "Last_Loc": "23.230, 121.480",
        "Network": "4G Online"
    })
    
    if st.button("重置系統"):
        st.session_state['user_status'] = '尚未簽到'
        st.session_state['page'] = 'home'
        st.rerun()

# ==========================================
# 主程式流程控制
# ==========================================

if st.session_state['page'] == 'home':
    page_home()
elif st.session_state['page'] == 'symptom_check':
    page_symptom_check()
elif st.session_state['page'] == 'result':
    page_result()