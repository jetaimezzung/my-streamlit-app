import streamlit as st
import requests
import json
import sqlite3
import datetime
from typing import Any, Dict, List
from openai import OpenAI

st.set_page_config(page_title="🐄 COW — Context Over Words", page_icon="🐄", layout="wide")

# =========================
# ========== DB ===========
# =========================
DB_PATH = "cow_app.db"

def db_init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS contexts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        raw_context TEXT,
        structured_json TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        context_fit_score INTEGER,
        politeness_score INTEGER,
        clarity_score INTEGER,
        flexibility_score INTEGER,
        habit_tags TEXT,
        raw_json TEXT
    )
    """)
    conn.commit()
    conn.close()

def crud_insert_context(raw, structured):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO contexts(created_at,raw_context,structured_json) VALUES(?,?,?)",
              (datetime.datetime.utcnow().isoformat(), raw, json.dumps(structured)))
    conn.commit()
    conn.close()

def crud_insert_feedback(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    INSERT INTO feedback_logs(
        created_at, context_fit_score, politeness_score, clarity_score, flexibility_score, habit_tags, raw_json
    ) VALUES(?,?,?,?,?,?,?)
    """, (
        datetime.datetime.utcnow().isoformat(),
        data.get("context_fit_score", 0),
        data.get("politeness_score", 0),
        data.get("clarity_score", 0),
        data.get("flexibility_score", 0),
        json.dumps(data.get("habit_tags", [])),
        json.dumps(data)
    ))
    conn.commit()
    conn.close()

def crud_list_feedback(limit=30):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT created_at, context_fit_score, politeness_score, clarity_score, flexibility_score, habit_tags FROM feedback_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def export_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM contexts")
    contexts = c.fetchall()
    c.execute("SELECT * FROM feedback_logs")
    feedback = c.fetchall()
    conn.close()
    return json.dumps({"contexts": contexts, "feedback_logs": feedback}, indent=2)

def import_data(uploaded_json):
    try:
        data = json.load(uploaded_json)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for row in data.get("contexts", []):
            c.execute("INSERT INTO contexts VALUES(?,?,?,?)", row)
        for row in data.get("feedback_logs", []):
            c.execute("INSERT INTO feedback_logs VALUES(?,?,?,?,?,?,?,?)", row)
        conn.commit()
        conn.close()
        return True
    except:
        return False

# =========================
# ========== AI ===========
# =========================
def get_openai_key():
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return st.session_state.get("openai_key")

def get_weather_key():
    if "OPENWEATHER_API_KEY" in st.secrets:
        return st.secrets["OPENWEATHER_API_KEY"]
    return st.session_state.get("weather_key")

def openai_call(prompt, model="gpt-5.2", retry=False):
    key = get_openai_key()
    if not key:
        return None, "NO_KEY"
    try:
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content, None
    except Exception as e:
        if not retry:
            return openai_call(prompt + "\nIMPORTANT: JSON ONLY.", model, retry=True)
        return None, str(e)

def parse_json_safe(text):
    try:
        return json.loads(text)
    except:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except:
            return None

# =========================
# ===== External APIs =====
# =========================
def languagetool_check(text):
    try:
        r = requests.post(
            "https://api.languagetool.org/v2/check",
            data={"text": text, "language": "en-US"},
            timeout=5
        )
        data = r.json()
        return data.get("matches", [])[:3]
    except:
        return None

def weather_fetch(city):
    key = get_weather_key()
    if not key:
        return None
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric",
            timeout=5
        )
        data = r.json()
        return {
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"]
        }
    except:
        return None

# =========================
# ====== Session Init =====
# =========================
db_init()

for k in ["raw_context","structured","survival","chat_history","difficulty"]:
    if k not in st.session_state:
        st.session_state[k] = None if k!="chat_history" else []

# =========================
# ========= Sidebar =======
# =========================
st.sidebar.title("Settings")

if "OPENAI_API_KEY" not in st.secrets:
    st.session_state.openai_key = st.sidebar.text_input("OpenAI API Key", type="password")

if "OPENWEATHER_API_KEY" not in st.secrets:
    st.session_state.weather_key = st.sidebar.text_input("OpenWeather API Key (optional)", type="password")

model = st.sidebar.selectbox("Model", ["gpt-5.2","gpt-5","gpt-5-mini"])

st.sidebar.download_button("Export Data", export_data(), file_name="cow_export.json")

uploaded = st.sidebar.file_uploader("Import JSON")
if uploaded:
    if import_data(uploaded):
        st.sidebar.success("Imported")
    else:
        st.sidebar.error("Import failed")

if st.sidebar.button("Reset Records"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM contexts")
    conn.execute("DELETE FROM feedback_logs")
    conn.commit()
    conn.close()
    st.sidebar.warning("All records deleted")

# =========================
# ========= Main UI =======
# =========================
st.title("🐄 COW — Context Over Words")

tabs = st.tabs(["Context","Survival","Simulation","Feedback","History"])

# ---------- Context ----------
with tabs[0]:
    context = st.text_area("자유 맥락 입력 (한국어)", height=150)
    optional_counterpart = st.text_input("상대 (선택)")
    optional_goal = st.text_input("목적 (선택)")
    optional_tone = st.selectbox("톤 (선택)", ["", "casual","neutral","formal"])

    if st.button("맥락 분석하기"):
        if not context or len(context)<10:
            st.warning("맥락이 너무 짧습니다.")
        else:
            prompt = f"""
            Input context:
            {context}
            Optional:
            counterpart:{optional_counterpart}
            goal:{optional_goal}
            tone:{optional_tone}
            Return JSON with:
            inferred_category, counterpart, relationship, goal, formality,
            constraints, cultural_risks, missing_info_questions
            """
            out, err = openai_call(prompt, model)
            if err:
                st.error(err)
            else:
                data = parse_json_safe(out)
                if not data:
                    st.error("JSON parse failed")
                else:
                    st.session_state.raw_context = context
                    st.session_state.structured = data
                    crud_insert_context(context, data)
                    st.success("분석 완료")

    if st.session_state.structured:
        st.json(st.session_state.structured)

# ---------- Survival ----------
with tabs[1]:
    if not st.session_state.structured:
        st.info("먼저 Context 분석을 진행하세요.")
    else:
        if st.button("생존 발화 생성"):
            prompt = f"""
            Based on structured context:
            {json.dumps(st.session_state.structured)}
            Generate JSON:
            level1, level2, level3,
            avoid(3), alternatives(3),
            template(opening,core,closing)
            """
            out, err = openai_call(prompt, model)
            if err:
                st.error(err)
            else:
                data = parse_json_safe(out)
                if not data:
                    st.error("JSON parse failed")
                else:
                    st.session_state.survival = data

        if st.session_state.survival:
            s = st.session_state.survival
            col1,col2,col3 = st.columns(3)
            col1.success("Level1\n"+s.get("level1",""))
            col2.info("Level2\n"+s.get("level2",""))
            col3.warning("Level3\n"+s.get("level3",""))
            st.write("Avoid:", s.get("avoid"))
            st.write("Alternatives:", s.get("alternatives"))

# ---------- Simulation ----------
with tabs[2]:
    difficulty = st.selectbox("Difficulty",["Easy","Medium","Hard","Chaos"])
    st.session_state.difficulty = difficulty

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Say something...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})

        history = st.session_state.chat_history[-8:]
        prompt = f"""
        Roleplay as counterpart.
        Difficulty:{difficulty}
        Context:{json.dumps(st.session_state.structured)}
        Recent:{history}
        Continue conversation in role.
        """
        out, err = openai_call(prompt, model)
        if not err:
            st.session_state.chat_history.append({"role":"assistant","content":out})

    if user_input:
        matches = languagetool_check(user_input)
        if matches:
            st.info("Grammar Suggestions:")
            for m in matches:
                st.write(m["message"])

# ---------- Feedback ----------
with tabs[3]:
    if st.button("피드백 받기"):
        prompt = f"""
        Evaluate conversation:
        {json.dumps(st.session_state.chat_history)}
        Return JSON:
        context_fit_score, politeness_score,
        clarity_score, flexibility_score,
        top_strengths, top_issues,
        next_try_script, habit_tags
        """
        out, err = openai_call(prompt, model)
        if not err:
            data = parse_json_safe(out)
            if data:
                crud_insert_feedback(data)
                st.json(data)

# ---------- History ----------
with tabs[4]:
    rows = crud_list_feedback(30)
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["date","context_fit","politeness","clarity","flexibility","habit_tags"])
        st.line_chart(df[["context_fit","politeness","clarity","flexibility"]])
        st.dataframe(df)
