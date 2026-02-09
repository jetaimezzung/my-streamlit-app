from datetime import datetime

import streamlit as st
from streamlit import components

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="COW - Context Over Words", layout="centered")

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
        "step",
        "context",
        "clarification",
        "summary",
        "survival_line",
        "transcript",
        "feedback",
        "progress_report",
        "last_entry_key",
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
        return "약속 또는 일정"
    if "가격" in text or "price" in lowered:
        return "가격 또는 선택"
    if "불만" in text or "complaint" in lowered:
        return "불편한 상황"
    if "채용" in text or "interview" in lowered:
        return "면접 또는 소개"
    if "여행" in text or "trip" in lowered:
        return "여행 상황"
    if "친구" in text or "friend" in lowered:
        return "친구와의 대화"
    return "일상 상황"


def generate_summary_and_questions(context_text):
    summary = compact_sentence(context_text)
    topic = extract_topic(context_text)
    lines = [f"우리가 이해한 상황은 이렇습니다: {summary} ({topic})"]
    if needs_more_details(context_text):
        lines.append("상황을 더 정확히 이해하기 위해 다음 항목에 답해주세요:")
        lines.append("- 상대방은 누구인가요?")
        lines.append("- 원하는 결과는 무엇인가요?")
        lines.append("- 감정 상태나 톤은 어떠길 원하나요?")
    return "\n".join(lines)


def generate_survival_line(context_text, clarification_text):
    combined = f"{context_text} {clarification_text}".lower()
    if "미팅" in combined or "meeting" in combined:
        return "Could we set a time to talk about this?"
    if "가격" in combined or "price" in combined:
        return "Can we go over the options together?"
    if "불만" in combined or "complaint" in combined:
        return "I’m sorry that happened. Let’s fix it together."
    if "면접" in combined or "interview" in combined:
        return "Thanks for taking the time to meet me today."
    if "여행" in combined or "trip" in combined:
        return "Could you help me find the best way to get there?"
    if "친구" in combined or "friend" in combined:
        return "I wanted to check in and see how you’re doing."
    return "Let me make sure I understood you correctly."


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
    notes.append("억양을 문장 끝에서 살짝 올리거나 내려 의미를 분명히 해보세요.")
    return " ".join(notes)


def generate_progress_report(history_text):
    entries = [line for line in history_text.splitlines() if line.strip()]
    total = len(entries)
    if total == 0:
        return "아직 누적된 기록이 없습니다."
    return (
        f"총 {total}회 연습 기록이 있습니다. "
        "반복적으로 핵심 문장을 짧게 말하는 경향이 보여요. "
        "다음에는 문장 끝을 또렷하게 마무리하고, 감정을 살려 말하는 연습을 추천합니다."
    )


def render_browser_tts(text, button_label, component_key):
    safe_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("$", "\\$")
        .replace("\n", " ")
    )
    components.html(
        f"""
        <div>
          <button id="{component_key}" style="
              background:#4b60ff;
              color:white;
              border:none;
              padding:8px 14px;
              border-radius:8px;
              font-weight:600;
              cursor:pointer;">
            {button_label}
          </button>
        </div>
        <script>
          const button = document.getElementById("{component_key}");
          button.addEventListener("click", () => {{
            if (!("speechSynthesis" in window)) {{
              alert("이 브라우저에서는 TTS를 지원하지 않습니다.");
              return;
            }}
            const utterance = new SpeechSynthesisUtterance(`{safe_text}`);
            utterance.lang = "en-US";
            window.speechSynthesis.speak(utterance);
          }});
        </script>
        """,
        height=60,
    )


# -------------------------
# UI 스타일
# -------------------------

st.markdown(
    """
    <style>
    .cow-card {
        background: linear-gradient(120deg, #f4f6ff 0%, #f8fbff 100%);
        border-radius: 18px;
        padding: 20px;
        border: 1px solid #e5e9ff;
        box-shadow: 0 12px 30px rgba(76, 101, 255, 0.08);
    }
    .cow-chip {
        display: inline-block;
        padding: 6px 12px;
        background-color: #eff2ff;
        color: #4b60ff;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .cow-step {
        font-size: 14px;
        color: #6c77a8;
    }
    .cow-title {
        font-size: 28px;
        font-weight: 700;
        color: #1a1f36;
    }
    .cow-subtitle {
        color: #495070;
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# UI 헤더
# -------------------------

st.markdown("<div class='cow-card'>", unsafe_allow_html=True)
st.markdown("<div class='cow-title'>🐄 COW</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='cow-subtitle'>Context Over Words · 영어 상황 대응을 위한 실전 코칭</div>",
    unsafe_allow_html=True,
)

with st.expander("⚙️ TTS/STT 설정", expanded=False):
    st.caption("외부 API 없이 브라우저 내장 TTS만 사용합니다.")
    st.caption("음성 인식(STT)은 지원하지 않으며, 직접 입력으로 연습합니다.")

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# -------------------------
# STEP 1: 자유 맥락 입력
# -------------------------
if st.session_state.step == 1:
    st.subheader("STEP 1. 지금 곧 말해야 하는 상황을 써주세요")
    st.write("일상, 여행, 친구, 업무 등 모든 상황에서 사용할 수 있어요.")
    st.session_state.context = st.text_area(
        "예: 해외 여행 중 현지인에게 길을 묻고 싶음",
        value=st.session_state.context,
        height=140,
    )

    col1, col2 = st.columns([1, 1])
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
        height=100,
    )

    col1, col2 = st.columns([1, 1])
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

    tts_col, info_col = st.columns([1, 2])
    with tts_col:
        render_browser_tts(
            st.session_state.survival_line,
            "🔊 문장 듣기",
            "survival-tts-button",
        )

    with info_col:
        st.caption("버튼을 눌러 브라우저 TTS로 문장을 들어보세요.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("말해보기", on_click=next_step)

# -------------------------
# STEP 4: 발화 연습 (Audio In)
# -------------------------
elif st.session_state.step == 4:
    st.subheader("STEP 4. 한번 말해보세요")
    st.write("한번 말해보세요. 완벽하지 않아도 괜찮습니다.")

    st.info("음성 인식은 오프라인 모드에서 지원되지 않습니다. 직접 입력으로 연습하세요.")
    st.session_state.transcript = st.text_input(
        "직접 입력해서 연습하기",
        value=st.session_state.transcript,
    )

    if st.session_state.transcript:
        st.write("📝 인식된 문장:", st.session_state.transcript)

    col1, col2 = st.columns([1, 1])
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

    st.info(f"이번 발화에 대한 피드백입니다. {st.session_state.feedback}")

    render_browser_tts(
        st.session_state.feedback,
        "🔊 피드백 음성 듣기",
        "feedback-tts-button",
    )

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

    col1, col2 = st.columns([1, 1])
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

    report_preview = "\n".join(
        [
            f"• {h['time']} | {h['spoken']}"
            for h in st.session_state.history[-3:]
        ]
    )
    if report_preview:
        st.markdown(
            "<div class='cow-card'><div class='cow-step'>최근 발화 기록</div>"  # noqa: WPS237
            f"<div>{report_preview}</div></div>",
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("처음으로", on_click=reset_flow)
