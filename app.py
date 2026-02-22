import streamlit as st
import sqlite3
import json
import datetime
from openai import OpenAI
import tempfile
import pandas as pd

st.set_page_config(page_title="🐄 COW — Context Over Words", layout="wide")

# =======================
# ====== CONFIG =========
# =======================
def get_api_key():
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return st.session_state.get("openai_key")

st.sidebar.title("Settings")
if "OPENAI_API_KEY" not in st.secrets:
    st.session_state.openai_key = st.sidebar.text_input("OpenAI API Key", type="password")

model = st.sidebar.selectbox("Model", ["gpt-5.2", "gpt-5", "gpt-5-mini"])

# =======================
# ====== DATABASE =======
# =======================
DB_PATH = "cow.db"

def db_init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        context_fit INTEGER,
        politeness INTEGER,
        clarity INTEGER,
        flexibility INTEGER,
        habit_tags TEXT
    )""")
    conn.commit()
    conn.close()

def save_feedback(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO feedback VALUES(NULL,?,?,?,?,?,?)",
              (datetime.datetime.utcnow().isoformat(),
               data["context_fit_score"],
               data["politeness_score"],
               data["clarity_score"],
               data["flexibility_score"],
               json.dumps(data["habit_tags"])))
    conn.commit()
    conn.close()

def load_feedback():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    return df

db_init()

# =======================
# ===== OPENAI ==========
# =======================
def call_openai_json(prompt):
    key = get_api_key()
    if not key:
        return None, "NO_KEY"
    client = OpenAI(api_key=key)
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return json.loads(res.choices[0].message.content), None
    except Exception as e:
        return None, str(e)

def transcribe_audio(file):
    key = get_api_key()
    if not key:
        return None
    client = OpenAI(api_key=key)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        tmp.flush()
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp.name, "rb")
        )
    return transcript.text

# =======================
# ===== SESSION =========
# =======================
for k in ["structured", "survival", "chat"]:
    if k not in st.session_state:
        st.session_state[k] = None if k != "chat" else []

# =======================
# ====== UI =============
# =======================
st.title("🐄 COW — Context Over Words")

tabs = st.tabs(["Context", "Survival", "Simulation", "Feedback", "History"])

# =======================
# 1️⃣ Context
# =======================
with tabs[0]:
    st.subheader("자유 맥락 입력")
    context = st.text_area("상황을 한국어로 입력하세요")

    audio_file = st.file_uploader("🎤 음성으로 입력 (선택)", type=["wav","mp3","m4a"])
    if audio_file:
        transcript = transcribe_audio(audio_file)
        if transcript:
            st.info(f"인식 결과: {transcript}")
            context = transcript

    if st.button("맥락 분석"):
        if not context:
            st.warning("상황을 입력하세요.")
        else:
            prompt = f"""
            Analyze this situation:
            {context}
            Return JSON with:
            inferred_category, counterpart, relationship,
            goal, formality, cultural_risks
            """
            data, err = call_openai_json(prompt)
            if data:
                st.session_state.structured = data
                st.success("분석 완료")
            else:
                st.error(err)

    if st.session_state.structured:
        s = st.session_state.structured
        st.markdown("### 🔍 분석 결과")
        st.write(f"**관계:** {s['relationship']}")
        st.write(f"**목적:** {s['goal']}")
        st.write(f"**형식:** {s['formality']}")
        st.write(f"**문화 리스크:** {s['cultural_risks']}")

# =======================
# 3️⃣ Survival Script
# =======================
with tabs[1]:
    if not st.session_state.structured:
        st.info("먼저 Context를 분석하세요.")
    else:
        if st.button("생존 발화 생성"):
            prompt = f"""
            Based on context:
            {json.dumps(st.session_state.structured)}
            Generate JSON:
            level1, level2, level3
            """
            data, err = call_openai_json(prompt)
            if data:
                st.session_state.survival = data
            else:
                st.error(err)

        if st.session_state.survival:
            s = st.session_state.survival
            col1, col2, col3 = st.columns(3)
            col1.success(s["level1"])
            col2.info(s["level2"])
            col3.warning(s["level3"])

# =======================
# 4️⃣ Simulation
# =======================
with tabs[2]:
    difficulty = st.selectbox("난이도", ["Easy","Medium","Hard","Chaos"])

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_msg = st.chat_input("말하거나 입력하세요")
    if user_msg:
        st.session_state.chat.append({"role":"user","content":user_msg})

        prompt = f"""
        Roleplay partner.
        Difficulty: {difficulty}
        Context: {json.dumps(st.session_state.structured)}
        Conversation: {st.session_state.chat[-6:]}
        """
        reply, err = call_openai_json(prompt)
        if reply:
            content = reply if isinstance(reply,str) else json.dumps(reply)
            st.session_state.chat.append({"role":"assistant","content":content})

# =======================
# 5️⃣ Feedback
# =======================
with tabs[3]:
    if st.button("피드백 받기"):
        prompt = f"""
        Evaluate conversation:
        {json.dumps(st.session_state.chat)}
        Return JSON:
        context_fit_score,
        politeness_score,
        clarity_score,
        flexibility_score,
        habit_tags
        """
        data, err = call_openai_json(prompt)
        if data:
            save_feedback(data)
            st.json(data)
        else:
            st.error(err)

# =======================
# History
# =======================
with tabs[4]:
    df = load_feedback()
    if not df.empty:
        st.line_chart(df[["context_fit","politeness","clarity","flexibility"]])
        st.dataframe(df)
    else:
        st.info("기록이 없습니다.")
