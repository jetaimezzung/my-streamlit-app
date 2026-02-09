import uuid
from datetime import datetime

import streamlit as st

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
st.markdown("**Context Over Words**  ·  회의 들어가기 2분 전에 켜는 앱")
st.caption("말을 잘하게 만드는 앱이 아니라, 지금 당장 말할 수 있게 해주는 앱")

# =========================
# Session State
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "scenario" not in st.session_state:
    st.session_state.scenario = "업무 지연 공유"
if "context_audio" not in st.session_state:
    st.session_state.context_audio = None
if "practice_audio" not in st.session_state:
    st.session_state.practice_audio = None
if "history" not in st.session_state:
    st.session_state.history = []


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

# =========================
# STEP 1: 자유 맥락 입력 (핵심)
# =========================
if st.session_state.step == 1:
    st.markdown("<div class='cow-hero'>", unsafe_allow_html=True)
    st.markdown("<div class='cow-step'>STEP 1 · 상황을 말로 입력</div>", unsafe_allow_html=True)
    st.subheader("지금 곧 말해야 하는 상황을 마이크로 녹음하세요")
    st.markdown(
        "타이핑 없이 **음성으로 상황을 남겨주세요.**\n\n"
        "녹음이 끝나면 자동으로 다음 단계 준비가 됩니다.",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown('<div class="cow-card">', unsafe_allow_html=True)
        st.session_state.context_audio = st.audio_input(
            "🎙️ 지금 상황을 말로 남기기",
            key="context_audio_input"
        )
        if st.session_state.context_audio:
            st.success("녹음 완료! 상황 인식 준비가 끝났습니다.")
            st.audio(st.session_state.context_audio)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="cow-card">', unsafe_allow_html=True)
        st.markdown("**상황 유형을 선택하세요**")
        st.session_state.scenario = st.radio(
            "상황 유형",
            ["업무 지연 공유", "요청/설득", "사과/정중한 정리", "일정 조율", "갑작스러운 질문 대응"],
            index=0,
            horizontal=False,
            label_visibility="collapsed",
        )
        st.markdown(
            "<span class='cow-chip'>음성 입력 완료</span>"
            "<span class='cow-chip'>자동 요약</span>"
            "<span class='cow-chip'>즉시 문장 제시</span>",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➡️ 바로 다음", use_container_width=True):
        if not st.session_state.context_audio:
            st.warning("텍스트 대신 음성으로 상황을 입력해 주세요.")
        else:
            st.session_state.step = 2
            st.rerun()

# =========================
# STEP 2: 핵심 맥락 요약 (질문 생략)
# =========================
elif st.session_state.step == 2:
    st.markdown("<div class='cow-step'>STEP 2 · 핵심 맥락 자동 정리</div>", unsafe_allow_html=True)
    st.subheader("방금 말한 내용을 기반으로 즉시 요약합니다")

    scenario_to_summary = {
        "업무 지연 공유": [
            "대면/비대면 비즈니스 상황",
            "일정 지연 설명이 핵심",
            "짧고 안전한 표현이 필요",
        ],
        "요청/설득": [
            "상대에게 협조를 요청",
            "이유는 짧게, 태도는 부드럽게",
            "한 문장으로 마무리 필요",
        ],
        "사과/정중한 정리": [
            "사과 혹은 상황 정리",
            "과하지 않게 책임 인정",
            "빠르게 다음 단계 제안",
        ],
        "일정 조율": [
            "미팅/스케줄 협의",
            "대안 제시가 필요",
            "간단한 질문형 발화",
        ],
        "갑작스러운 질문 대응": [
            "즉답이 어려운 질문",
            "시간 확보와 재확인",
            "짧고 안정적인 회신",
        ],
    }

    summary_lines = scenario_to_summary.get(
        st.session_state.scenario,
        ["핵심 상황 인식", "필요한 의도 정리", "짧은 문장 준비"],
    )
    st.session_state.summary = "\n".join(f"• {line}" for line in summary_lines)

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("**요약된 맥락**")
    st.markdown(st.session_state.summary)
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("모호할 때만 추가 질문이 나옵니다. 지금은 바로 진행합니다.")

    if st.button("➡️ 계속하기", use_container_width=True):
        st.session_state.step = 3
        st.rerun()

# =========================
# STEP 3: 생존 발화 1문장 제시
# =========================
elif st.session_state.step == 3:
    st.markdown("<div class='cow-step'>STEP 3 · 생존 발화 1문장</div>", unsafe_allow_html=True)
    st.subheader("이 문장 하나만 기억하세요")

    scenario_to_line = {
        "업무 지연 공유": "I may need a bit more time on my task.",
        "요청/설득": "Could we go with this option for now?",
        "사과/정중한 정리": "I apologize for the confusion, let me clarify.",
        "일정 조율": "Could we move our meeting to tomorrow?",
        "갑작스러운 질문 대응": "Let me confirm and get back to you shortly.",
    }
    survival_line = scenario_to_line.get(
        st.session_state.scenario,
        "I may need a bit more time on my task.",
    )

    st.markdown('<div class="cow-survival">', unsafe_allow_html=True)
    st.markdown("**Survival Line**")
    st.markdown(f"👉 *{survival_line}*")
    st.markdown("</div>", unsafe_allow_html=True)

    speak_button(survival_line, "🔊 문장 듣기 (Audio Out)", key="survival")
    st.caption("설명은 생략합니다. 지금 당장 쓸 수 있는 것만 제공합니다.")

    if st.button("➡️ 말해보기", use_container_width=True):
        st.session_state.step = 4
        st.rerun()

# =========================
# STEP 4: 말해보기 + 최소 피드백
# =========================
elif st.session_state.step == 4:
    st.markdown("<div class='cow-step'>STEP 4 · 말해보기 + 피드백</div>", unsafe_allow_html=True)
    st.subheader("방금 들은 문장을 말로 연습하세요")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.session_state.practice_audio = st.audio_input(
        "🎙️ Survival Line 따라 말하기",
        key="practice_audio_input",
    )
    if st.session_state.practice_audio:
        st.audio(st.session_state.practice_audio)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("피드백 받기", use_container_width=True):
        if not st.session_state.practice_audio:
            st.warning("말로 한 번 녹음해 주세요.")
        else:
            audio_bytes = st.session_state.practice_audio.getvalue()
            duration_hint = len(audio_bytes) / 32000
            is_short = duration_hint < 0.6
            is_long = duration_hint > 6

            st.markdown('<div class="cow-feedback">', unsafe_allow_html=True)
            st.markdown("**피드백**")
            st.markdown("✔️ 의미 전달됨")
            if is_short:
                st.markdown("⚠️ 조금 더 또박또박 말하면 더 좋습니다")
            elif is_long:
                st.markdown("⚠️ 문장을 짧게 끊어보세요")
            else:
                st.markdown("✔️ 길이가 적절함")
            st.markdown('</div>', unsafe_allow_html=True)

            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "scenario": st.session_state.scenario,
            })

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔁 다시 한 번"):
                    st.session_state.step = 3
                    st.rerun()
            with col2:
                if st.button("🆕 새 상황"):
                    st.session_state.step = 1
                    st.rerun()

# =========================
# STEP 5: 누적 리포트 (조용히 쌓임)
# =========================
st.markdown("<div class='cow-divider'></div>", unsafe_allow_html=True)
st.subheader("📌 최근 연습 기록")

summary_col, streak_col, scenario_col = st.columns(3)
with summary_col:
    st.markdown('<div class="cow-metric">', unsafe_allow_html=True)
    st.markdown(f"총 연습 {len(st.session_state.history)}회")
    st.markdown('</div>', unsafe_allow_html=True)
with streak_col:
    st.markdown('<div class="cow-metric">', unsafe_allow_html=True)
    st.markdown("오늘 목표: 3회")
    st.markdown('</div>', unsafe_allow_html=True)
with scenario_col:
    st.markdown('<div class="cow-metric">', unsafe_allow_html=True)
    st.markdown(f"현재 유형: {st.session_state.scenario}")
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.history:
    for h in reversed(st.session_state.history[-5:]):
        st.markdown(f"- **[{h['time']}]** {h['scenario']}")
else:
    st.caption("아직 저장된 기록이 없습니다.")

st.caption("말을 줄였더니, 오히려 말할 수 있게 되었습니다.")
