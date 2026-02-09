import os
import uuid
from datetime import datetime

import streamlit as st
from openai import OpenAI

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="COW : Context Over Words",
    page_icon="🐄",
    layout="wide"
)

# =========================
# Global Style (UI 개선)
# =========================
st.markdown(
    """
    <style>
    :root {
        --cow-bg: #f5f7fb;
        --cow-card: #ffffff;
        --cow-primary: #1f6feb;
        --cow-muted: #6b7280;
        --cow-border: #e5e7eb;
        --cow-accent: #111827;
    }
    .block-container {padding-top: 2.5rem; padding-bottom: 2.5rem;}
    .cow-hero {
        background: radial-gradient(circle at top left, #eef2ff, #f8fafc 55%, #ffffff 100%);
        border: 1px solid var(--cow-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 35px rgba(15, 23, 42, 0.08);
    }
    .cow-card {
        background-color: var(--cow-card);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--cow-border);
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }
    .cow-chip {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.85rem;
        border: 1px solid var(--cow-border);
        color: var(--cow-muted);
        margin-right: 0.5rem;
        margin-bottom: 0.4rem;
    }
    .cow-step {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        background: #eef2ff;
        color: var(--cow-primary);
        margin-bottom: 0.5rem;
    }
    .cow-survival {
        background: linear-gradient(135deg, #eff6ff, #ffffff);
        padding: 1.7rem;
        border-radius: 18px;
        border: 1px solid #dbeafe;
        font-size: 1.2rem;
    }
    .cow-feedback {
        background-color: #f0fdf4;
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #bbf7d0;
    }
    .cow-muted {color: var(--cow-muted); font-size: 0.95rem;}
    .cow-metric {
        background: #111827;
        color: #ffffff;
        padding: 1rem;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
    }
    .cow-divider {
        height: 1px;
        background: var(--cow-border);
        margin: 1.5rem 0;
    }
    .cow-voice-button button {
        background: var(--cow-primary);
        color: white;
        border: none;
        padding: 0.7rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Header
# =========================
st.title("🐄 COW")
st.markdown("**Context Over Words**  ·  영어가 필요한 모든 순간을 위한 앱")
st.caption("말을 잘하게 만드는 앱이 아니라, 지금 당장 말할 수 있게 해주는 앱")

# =========================
# Session State
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1
if "summary" not in st.session_state:
    st.session_state.summary = []
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "survival_line" not in st.session_state:
    st.session_state.survival_line = "I may need a bit more time on my task."
if "history" not in st.session_state:
    st.session_state.history = []
if "question_answers" not in st.session_state:
    st.session_state.question_answers = {}
if "practice_text" not in st.session_state:
    st.session_state.practice_text = ""
if "latest_transcript" not in st.session_state:
    st.session_state.latest_transcript = ""


def speak_button(text: str, label: str, key: str) -> None:
    button_id = f"cow-voice-{key}-{uuid.uuid4()}"
    html = f"""
    <div class="cow-voice-button">
        <button id="{button_id}" type="button">{label}</button>
    </div>
    <script>
        const btn = document.getElementById("{button_id}");
        if (btn) {{
            btn.onclick = () => {{
                const utterance = new SpeechSynthesisUtterance({text!r});
                utterance.lang = "en-US";
                utterance.rate = 0.95;
                speechSynthesis.cancel();
                speechSynthesis.speak(utterance);
            }};
        }}
    </script>
    """
    st.components.v1.html(html, height=55)


def build_summary(context: str) -> list[str]:
    lowered = context.lower()
    if any(keyword in lowered for keyword in ["회의", "미팅", "meeting", "call", "zoom"]):
        return [
            "공식/반공식 대화 상황",
            "짧고 명료한 말투가 안전",
            "상황 신호 후 요청/의견 제시",
        ]
    if any(keyword in lowered for keyword in ["지연", "delay", "마감", "deadline"]):
        return [
            "요청/협의 상황",
            "상대는 협력자/상급자/고객",
            "이유는 한 문장으로 간단히",
        ]
    if any(keyword in lowered for keyword in ["사과", "미안", "sorry", "apology"]):
        return [
            "상황 정리 + 정중한 톤",
            "책임을 과하게 말하지 않기",
            "다음 조치 제안 필요",
        ]
    if any(keyword in lowered for keyword in ["여행", "공항", "hotel", "restaurant", "예약"]):
        return [
            "서비스/여행 상황",
            "요청을 먼저 말하기",
            "필요한 정보만 짧게 전달",
        ]
    if any(keyword in lowered for keyword in ["학교", "수업", "class", "teacher"]):
        return [
            "교육/학습 상황",
            "질문을 한 문장으로",
            "추가 설명은 요청 받을 때",
        ]
    return [
        "일상 또는 업무 상황",
        "짧고 안전한 표현 필요",
        "한 문장으로 먼저 시작",
    ]


def openai_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


@st.cache_data(show_spinner=False)
def generate_tts_audio(text: str) -> bytes | None:
    if not openai_enabled():
        return None
    client = OpenAI()
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )
    return response.read()


def render_tts_block(text: str, key: str) -> None:
    st.markdown("**TTS Audio Out**")
    audio_bytes = generate_tts_audio(text)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.info("TTS 사용을 위해 OPENAI_API_KEY를 설정해 주세요.")

# =========================
# STEP 1: 자유 맥락 입력 (핵심)
# =========================
if st.session_state.step == 1:
    st.markdown("<div class='cow-hero'>", unsafe_allow_html=True)
    st.markdown("<div class='cow-step'>STEP 1 · 자유 맥락 입력</div>", unsafe_allow_html=True)
    st.subheader("곧 직접 말해야 하는 상황을 그대로 적어주세요")
    st.markdown(
        "문장이 엉망이어도 괜찮습니다. **한국어 그대로** 적어도 OK.\n\n"
        "비즈니스뿐 아니라 일상/학업/여행 등 영어가 필요한 모든 상황을 적어주세요.",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.session_state.context_text = st.text_area(
        "앱 화면",
        value=st.session_state.context_text,
        placeholder="곧 직접 말해야 하는 상황을 그냥 써주세요.",
        height=140,
        label_visibility="visible",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        "<span class='cow-chip'>선택 최소화</span>"
        "<span class='cow-chip'>말 줄이기</span>"
        "<span class='cow-chip'>한 번에 하나</span>",
        unsafe_allow_html=True,
    )

    if st.button("➡️ 바로 다음", use_container_width=True):
        if not st.session_state.context_text.strip():
            st.warning("상황을 한 줄이라도 입력해 주세요.")
        else:
            st.session_state.summary = build_summary(st.session_state.context_text)
            st.session_state.step = 2
            st.rerun()

# =========================
# STEP 2: 핵심 맥락 요약
# =========================
elif st.session_state.step == 2:
    st.markdown("<div class='cow-step'>STEP 2 · AI 1차 맥락 해석</div>", unsafe_allow_html=True)
    st.subheader("우리가 이해한 상황을 요약합니다")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("**이 상황은**")
    for line in st.session_state.summary:
        st.markdown(f"• {line}")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➡️ 계속하기", use_container_width=True):
        st.session_state.step = 3
        st.rerun()

# =========================
# STEP 3: AI 추가 질문 (필요한 정보만)
# =========================
elif st.session_state.step == 3:
    st.markdown("<div class='cow-step'>STEP 3 · AI 추가 질문</div>", unsafe_allow_html=True)
    st.subheader("정확한 이해를 위한 핵심 질문만 드립니다")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("**항목 1. 지금 바로 말해야 하나요?**")
    st.session_state.question_answers["timing"] = st.radio(
        "항목 1",
        ["지금 이 자리에서 말해야 함", "조금 있다가 말해도 됨"],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("**항목 2. 이유를 길게 설명할 수 있는 분위기인가요?**")
    st.session_state.question_answers["detail"] = st.radio(
        "항목 2",
        ["간단히만 말해야 함", "설명해도 되는 분위기"],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("➡️ 다음 단계", use_container_width=True):
        st.session_state.step = 6
        st.rerun()

# =========================
# STEP 6: 생존 발화 제시 (메인 기능)
# =========================
elif st.session_state.step == 6:
    st.markdown("<div class='cow-step'>STEP 6 · 생존 발화 제시</div>", unsafe_allow_html=True)
    st.subheader("이 상황에서는 아래 한 문장으로 충분합니다")

    st.markdown('<div class="cow-survival">', unsafe_allow_html=True)
    st.markdown("**Survival version**")
    st.markdown(f"👉 *{st.session_state.survival_line}*")
    st.markdown("</div>", unsafe_allow_html=True)

    speak_button(st.session_state.survival_line, "🔊 문장 듣기", key="survival")
    render_tts_block(st.session_state.survival_line, key="survival-tts")

    st.caption("이유는 질문이 나오면 그때 짧게 덧붙이면 됩니다.")

    if st.button("➡️ 말해보기", use_container_width=True):
        st.session_state.step = 7
        st.rerun()

# =========================
# STEP 7: 발화 연습 + 인터네이션
# =========================
elif st.session_state.step == 7:
    st.markdown("<div class='cow-step'>STEP 7 · 발화 연습 + 인터네이션</div>", unsafe_allow_html=True)
    st.subheader("한 번 말해보세요. 완벽하지 않아도 괜찮습니다.")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.session_state.practice_text = st.text_input(
        "앱 안내",
        value=st.session_state.practice_text,
        placeholder="여기에 한번 적어보거나, 실제로 말해보세요.",
        label_visibility="visible",
    )
    st.markdown("**Audio In**")
    audio_blob = st.audio_input("오디오로 말해보기", label_visibility="collapsed")
    if audio_blob and openai_enabled():
        client = OpenAI()
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=("practice.wav", audio_blob.getvalue()),
        )
        st.session_state.latest_transcript = transcript.text
        st.markdown(f"**인식된 문장:** {st.session_state.latest_transcript}")
    elif audio_blob:
        st.info("음성 인식을 위해 OPENAI_API_KEY를 설정해 주세요.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("피드백 받기", use_container_width=True):
        if not st.session_state.practice_text.strip() and not st.session_state.latest_transcript.strip():
            st.warning("한 줄이라도 적거나, 오디오를 녹음해 주세요.")
        else:
            st.session_state.step = 8
            st.rerun()

# =========================
# STEP 8: 즉각 발화 피드백
# =========================
elif st.session_state.step == 8:
    st.markdown("<div class='cow-step'>STEP 8 · 즉각 발화 피드백</div>", unsafe_allow_html=True)
    st.subheader("이번 발화에 대한 피드백입니다")

    st.markdown('<div class="cow-feedback">', unsafe_allow_html=True)
    st.markdown("✔️ 의도 전달: 충분")
    st.markdown("✔️ 길이: 적절")
    st.markdown("✔️ 회피 없이 요청을 전달함")
    st.markdown("✔️ 생존 발화로 충분함")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➡️ 저장하고 다음", use_container_width=True):
        st.session_state.history.append(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "context": st.session_state.context_text.strip(),
                "practice": st.session_state.practice_text.strip() or st.session_state.latest_transcript,
            }
        )
        st.session_state.step = 9
        st.rerun()

# =========================
# STEP 9: 누적 리포트 반영 (보이지 않게 저장)
# =========================
elif st.session_state.step == 9:
    st.markdown("<div class='cow-step'>STEP 9 · 누적 리포트 반영</div>", unsafe_allow_html=True)
    st.subheader("이번 기록은 조용히 저장됩니다")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("**시스템 기록**")
    st.markdown("• 상황 요약 저장")
    st.markdown("• 생존 발화 선택 기록")
    st.markdown("• 짧은 발화 선호 패턴 기록")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➡️ 리포트 예시 보기", use_container_width=True):
        st.session_state.step = 10
        st.rerun()

# =========================
# STEP 10: 며칠 뒤 누적 리포트 예시
# =========================
elif st.session_state.step == 10:
    st.markdown("<div class='cow-step'>STEP 10 · 며칠 뒤 누적 리포트 예시</div>", unsafe_allow_html=True)
    st.subheader("최근 훈련을 보면")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("• 핵심부터 말하는 선택을 자주 함")
    st.markdown("• 상황 신호를 먼저 제시함")
    st.markdown("• 설명을 줄이는 연습이 누적됨")
    st.markdown("• 다음 포인트: 이유를 한 문장으로 덧붙이기")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🆕 새 상황 시작", use_container_width=True):
        st.session_state.step = 1
        st.session_state.context_text = ""
        st.session_state.practice_text = ""
        st.session_state.latest_transcript = ""
        st.rerun()

else:
    st.session_state.step = 1
    st.rerun()
