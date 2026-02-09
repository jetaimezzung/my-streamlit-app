import io
import math
import tempfile
import wave
from datetime import datetime

import streamlit as st

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="COW - Context Over Words", layout="centered")

# 외부 API 없이 로컬에서 동작하도록 구성

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
# 공통 유틸 함수
# -------------------------
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step = max(1, st.session_state.step - 1)

def reset_flow():
    for key in [
        "step", "context", "clarification", "summary",
        "survival_line", "survival_audio",
        "transcript", "feedback", "progress_report",
        "last_entry_key"
    ]:
        st.session_state[key] = "" if isinstance(st.session_state.get(key), str) else None
    st.session_state.step = 1

# -------------------------
# 로컬 기능 함수
# -------------------------
def compact_sentence(text, limit=80):
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "상황이 아직 입력되지 않았습니다."
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[:limit].rstrip()}..."

def needs_more_details(text):
    return len(text.strip()) < 30

def extract_topic(text):
    lowered = text.lower()
    if "미팅" in text or "meeting" in lowered:
        return "미팅 일정 조율"
    if "가격" in text or "price" in lowered:
        return "가격 협상"
    if "불만" in text or "complaint" in lowered:
        return "고객 불만 대응"
    if "채용" in text or "interview" in lowered:
        return "면접 상황"
    return "업무 상황"

def generate_summary_and_questions(context_text):
    summary = compact_sentence(context_text)
    topic = extract_topic(context_text)
    lines = [f"우리가 이해한 상황은 이렇습니다: {summary} ({topic})"]
    if needs_more_details(context_text):
        lines.append("상황을 더 정확히 이해하기 위해 다음 항목에 답해주세요:")
        lines.append("- 상대방은 누구인가요?")
        lines.append("- 원하는 결과는 무엇인가요?")
    return "\n".join(lines)

def generate_survival_line(context_text, clarification_text):
    combined = f"{context_text} {clarification_text}".lower()
    if "미팅" in combined or "meeting" in combined:
        return "Could we set a time to discuss this?"
    if "가격" in combined or "price" in combined:
        return "Can we review the pricing options together?"
    if "불만" in combined or "complaint" in combined:
        return "I’m sorry for the inconvenience. Let me help."
    if "면접" in combined or "interview" in combined:
        return "Thank you for meeting with me today."
    return "Let me confirm the details to avoid mistakes."

def text_to_speech(text):
    sample_rate = 22050
    duration = 1.0 + min(len(text) / 60, 2.0)
    frequency = 440
    total_frames = int(sample_rate * duration)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(total_frames):
            value = int(32767 * 0.2 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wf.writeframesraw(value.to_bytes(2, "little", signed=True))
    buffer.seek(0)
    return buffer.read()

def speech_to_text(audio_path):
    return ""

def generate_feedback(user_text, target_text):
    if not user_text.strip():
        return "발화 내용이 비어 있습니다. 목표 문장을 천천히 따라 읽어보세요."
    target_words = set(target_text.lower().split())
    user_words = set(user_text.lower().split())
    missing = target_words - user_words
    notes = []
    if missing:
        notes.append(f"누락된 단어가 있습니다: {', '.join(sorted(missing))}.")
    if len(user_text.split()) < max(1, len(target_text.split()) - 2):
        notes.append("조금 더 또렷하고 천천히 말해보세요.")
    notes.append("의도는 전달되며, 리듬을 일정하게 유지하면 좋아요.")
    return " ".join(notes)

def generate_progress_report(history_text):
    entries = [line for line in history_text.splitlines() if line.strip()]
    total = len(entries)
    if total == 0:
        return "아직 누적된 기록이 없습니다."
    return (
        f"총 {total}회 연습 기록이 있습니다. "
        "반복적으로 핵심 문장을 짧게 말하는 경향이 보여요. "
        "다음에는 문장 끝을 또렷하게 마무리하는 연습을 추천합니다."
    )

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
        if st.button("다음") and st.session_state.context.strip():
            next_step()

# -------------------------
# STEP 2: 상황 이해
# -------------------------
elif st.session_state.step == 2:
    st.subheader("STEP 2. 상황 이해")

    if not st.session_state.summary:
        st.session_state.summary = generate_summary_and_questions(
            st.session_state.context
        )

    st.markdown(st.session_state.summary)

    st.session_state.clarification = st.text_area(
        "추가로 답할 내용 (없으면 비워두세요)",
        value=st.session_state.clarification,
        height=80,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("계속", on_click=next_step)

# -------------------------
# STEP 3: 생존 발화 + TTS
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
    audio_input = st.audio_input("🎤 말하기")

    if audio_input:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_input.read())
            audio_path = f.name
        st.session_state.transcript = speech_to_text(audio_path)
        st.info("로컬 환경에서는 음성 인식이 지원되지 않아 텍스트 입력을 사용합니다.")

    st.session_state.transcript = st.text_input(
        "직접 입력해서 연습하기",
        value=st.session_state.transcript,
    )

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

    st.info(st.session_state.feedback)

    entry_key = f"{st.session_state.context}|{st.session_state.transcript}"
    if entry_key != st.session_state.last_entry_key:
        st.session_state.history.append(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "context": st.session_state.context,
                "target": st.session_state.survival_line,
                "spoken": st.session_state.transcript,
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
                f"- {h['time']} | 목표: {h['target']} | 발화: {h['spoken']} | 피드백: {h['feedback']}"
                for h in st.session_state.history
            ]
        )
        st.session_state.progress_report = generate_progress_report(history_text)

    if st.session_state.progress_report:
        st.success(st.session_state.progress_report)
    else:
        st.write("아직 누적된 기록이 없습니다.")

    st.button("처음으로", on_click=reset_flow)
