import streamlit as st
import openai
import os
import tempfile
from datetime import datetime

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="COW - Context Over Words", layout="centered")

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("OPENAI_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

# -------------------------
# 세션 상태 초기화
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "context" not in st.session_state:
    st.session_state.context = ""

if "clarification" not in st.session_state:
    st.session_state.clarification = ""

if "survival_line" not in st.session_state:
    st.session_state.survival_line = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# 공통 함수
# -------------------------
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def gpt(prompt, temperature=0.4):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content

# -------------------------
# UI 헤더
# -------------------------
st.markdown("## 🐄 COW")
st.caption("Context Over Words · 회의 들어가기 2분 전에 켜는 앱")
st.divider()

# -------------------------
# STEP 1: 자유 맥락 입력
# -------------------------
if st.session_state.step == 1:
    st.subheader("STEP 1. 지금 곧 말해야 하는 상황을 써주세요")
    st.session_state.context = st.text_area(
        "예: 해외 바이어와 첫 미팅에서 일정 조율을 해야 함",
        height=120
    )

    if st.button("다음"):
        if st.session_state.context.strip():
            next_step()
        else:
            st.warning("상황을 입력해주세요.")

# -------------------------
# STEP 2: 맥락 해석 + 추가 질문
# -------------------------
elif st.session_state.step == 2:
    st.subheader("STEP 2. 상황 이해")

    prompt = f"""
사용자가 입력한 상황:
{st.session_state.context}

1. 우리가 이해한 상황을 한 문장으로 요약해라.
2. 추가 정보가 꼭 필요하다면 질문 1~2개만 만들어라.
3. 필요 없다면 질문은 생략하라.
"""

    result = gpt(prompt)
    st.markdown(result)

    st.session_state.clarification = st.text_area(
        "추가로 답할 내용이 있다면 입력 (없으면 비워두세요)",
        height=80
    )

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("계속", on_click=next_step)

# -------------------------
# STEP 3: 생존 발화 제시 + TTS
# -------------------------
elif st.session_state.step == 3:
    st.subheader("STEP 3. 지금 쓸 문장 하나")

    prompt = f"""
상황:
{st.session_state.context}
추가 정보:
{st.session_state.clarification}

초보자가 바로 말할 수 있는
가장 안전하고 짧은 영어 문장 1개만 제시하라.
설명은 하지 마라.
"""

    st.session_state.survival_line = gpt(prompt, temperature=0.3)
    st.success(st.session_state.survival_line)

    # TTS
    audio = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=st.session_state.survival_line
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(audio.read())
        st.audio(f.name)

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("말해보기", on_click=next_step)

# -------------------------
# STEP 4: 발화 연습 (Audio In)
# -------------------------
elif st.session_state.step == 4:
    st.subheader("STEP 4. 한번 말해보세요")
    st.caption("완벽하지 않아도 괜찮습니다.")

    audio_input = st.audio_input("🎤 말하기")

    if audio_input:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_input.read())
            audio_path = f.name

        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb")
        )

        user_text = transcript.text
        st.write("📝 인식된 문장:", user_text)

        # -------------------------
        # STEP 5: 피드백
        # -------------------------
        prompt = f"""
사용자가 말한 문장:
{user_text}

목표 문장:
{st.session_state.survival_line}

발음, 억양, 속도, 의도 전달 관점에서
초보자에게 짧게 피드백하라.
"""

        st.session_state.feedback = gpt(prompt)
        st.info(st.session_state.feedback)

        # -------------------------
        # STEP 6: 누적 저장
        # -------------------------
        st.session_state.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "situation": st.session_state.context,
            "sentence": st.session_state.survival_line,
            "feedback": st.session_state.feedback
        })

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("처음으로", on_click=lambda: st.session_state.update(step=1))

# -------------------------
# 누적 리포트 (항상 하단)
# -------------------------
st.divider()
st.subheader("📌 최근 연습 기록")

if st.session_state.history:
    for h in reversed(st.session_state.history[-3:]):
        st.markdown(f"""
**{h['time']}**  
- 상황: {h['situation']}  
- 문장: {h['sentence']}  
- 피드백: {h['feedback']}
""")
else:
    st.caption("아직 기록이 없습니다.")
