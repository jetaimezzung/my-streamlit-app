import os
import tempfile
from datetime import datetime

import openai
import streamlit as st

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

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "followup_questions" not in st.session_state:
    st.session_state.followup_questions = ""

if "survival_line" not in st.session_state:
    st.session_state.survival_line = ""

if "survival_audio" not in st.session_state:
    st.session_state.survival_audio = None

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "progress_report" not in st.session_state:
    st.session_state.progress_report = ""

if "last_entry_key" not in st.session_state:
    st.session_state.last_entry_key = ""

# -------------------------
# 공통 함수
# -------------------------

def next_step():
    st.session_state.step += 1


def prev_step():
    st.session_state.step = max(1, st.session_state.step - 1)


def reset_flow():
    st.session_state.step = 1
    st.session_state.context = ""
    st.session_state.clarification = ""
    st.session_state.summary = ""
    st.session_state.followup_questions = ""
    st.session_state.survival_line = ""
    st.session_state.survival_audio = None
    st.session_state.transcript = ""
    st.session_state.feedback = ""
    st.session_state.last_entry_key = ""


def gpt(prompt, temperature=0.4):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content


def generate_summary_and_questions(context_text):
    prompt = f"""
사용자가 입력한 상황:
{context_text}

1. 우리가 이해한 상황을 한 문장으로 요약해라.
2. 추가 정보가 꼭 필요하다면 질문 1~2개만 만들어라.
3. 필요 없다면 질문은 생략하라.
4. 출력 형식은 다음을 따르라.

우리가 이해한 상황은 이렇습니다: <요약>
상황을 더 정확히 이해하기 위해 다음 항목에 답해주세요:
- <질문 1>
- <질문 2>

추가 질문이 필요 없다면 질문 섹션은 생략하라.
"""
    return gpt(prompt)


def generate_survival_line(context_text, clarification_text):
    prompt = f"""
상황:
{context_text}
추가 정보:
{clarification_text}

초보자가 바로 말할 수 있는
가장 안전하고 짧은 영어 문장 1개만 제시하라.
설명은 하지 마라.
"""
    return gpt(prompt, temperature=0.3)


def text_to_speech(text):
    audio = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )
    return audio.read()


def speech_to_text(audio_path):
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=open(audio_path, "rb"),
    )
    return transcript.text


def generate_feedback(user_text, target_text):
    prompt = f"""
사용자가 말한 문장:
{user_text}

목표 문장:
{target_text}

발음, 억양, 속도, 의도 전달 관점에서
초보자에게 짧게 피드백하라.
"""
    return gpt(prompt)


def generate_progress_report(history):
    prompt = f"""
아래는 사용자의 누적 발화 기록이다. 이를 바탕으로
영어 습관/특징을 정리하고, 주요 피드백, 개선/연습 조언을 간결하게 작성하라.

발화 기록:
{history}
"""
    return gpt(prompt, temperature=0.3)


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
        value=st.session_state.context,
        height=120,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.button("초기화", on_click=reset_flow)
    with col2:
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

    if not st.session_state.summary:
        result = generate_summary_and_questions(st.session_state.context)
        st.session_state.summary = result

    st.markdown(st.session_state.summary)

    st.session_state.clarification = st.text_area(
        "추가로 답할 내용이 있다면 입력 (없으면 비워두세요)",
        value=st.session_state.clarification,
        height=80,
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

    if not st.session_state.survival_line:
        st.session_state.survival_line = generate_survival_line(
            st.session_state.context,
            st.session_state.clarification,
        )

    st.success(st.session_state.survival_line)

    if st.session_state.survival_audio is None:
        st.session_state.survival_audio = text_to_speech(
            st.session_state.survival_line
        )

    st.audio(st.session_state.survival_audio)

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

        st.session_state.transcript = speech_to_text(audio_path)

    if st.session_state.transcript:
        st.write("📝 인식된 문장:", st.session_state.transcript)

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("피드백 받기", on_click=next_step, disabled=not st.session_state.transcript)

# -------------------------
# STEP 5: 피드백
# -------------------------
elif st.session_state.step == 5:
    st.subheader("STEP 5. 발화 피드백")

    if not st.session_state.feedback:
        st.session_state.feedback = generate_feedback(
            st.session_state.transcript,
            st.session_state.survival_line,
        )

    st.info(f"이번 발화에 대한 피드백입니다.\n\n{st.session_state.feedback}")

    if st.session_state.feedback:
        entry_key = f"{st.session_state.context}|{st.session_state.transcript}|{st.session_state.feedback}"
        if entry_key != st.session_state.last_entry_key:
            st.session_state.history.append(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "situation": st.session_state.context,
                    "sentence": st.session_state.survival_line,
                    "transcript": st.session_state.transcript,
                    "feedback": st.session_state.feedback,
                }
            )
            st.session_state.last_entry_key = entry_key
            st.session_state.progress_report = ""

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("리포트 보기", on_click=next_step)

# -------------------------
# STEP 6: 누적 리포트
# -------------------------
elif st.session_state.step == 6:
    st.subheader("STEP 6. 누적 리포트")

    if st.session_state.history and not st.session_state.progress_report:
        history_text = "\n".join(
            [
                f"- 시간: {item['time']}\n  상황: {item['situation']}\n  목표 문장: {item['sentence']}\n  발화: {item['transcript']}\n  피드백: {item['feedback']}"
                for item in st.session_state.history
            ]
        )
        st.session_state.progress_report = generate_progress_report(history_text)

    if st.session_state.progress_report:
        st.success(st.session_state.progress_report)
    else:
        st.write("아직 누적된 기록이 없습니다.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("처음으로", on_click=reset_flow)
