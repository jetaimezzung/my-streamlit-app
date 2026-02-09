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
    st.session_state.summary = []
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "survival_line" not in st.session_state:
    st.session_state.survival_line = "I may need a bit more time on my task."
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


def build_summary(context: str) -> list[str]:
    lowered = context.lower()
    if any(keyword in lowered for keyword in ["회의", "미팅", "meeting"]):
        return [
            "대면 비즈니스 요청",
            "회의 중 발언",
            "짧게 말하는 게 안전",
        ]
    if any(keyword in lowered for keyword in ["지연", "delay", "마감"]):
        return [
            "업무 일정 조정 요청",
            "상대는 매니저/팀원",
            "이유는 한 문장으로",
        ]
    if any(keyword in lowered for keyword in ["사과", "미안", "sorry"]):
        return [
            "상황 정리 + 정중한 톤",
            "책임을 과하게 말하지 않기",
            "다음 조치 제안 필요",
        ]
    return [
        "비즈니스 상황",
        "짧고 안전한 표현 필요",
        "한 문장으로 먼저 시작",
    ]

# =========================
# STEP 1: 자유 맥락 입력 (핵심)
# =========================
if st.session_state.step == 1:
    st.markdown("<div class='cow-hero'>", unsafe_allow_html=True)
    st.markdown("<div class='cow-step'>STEP 1 · 자유 맥락 입력</div>", unsafe_allow_html=True)
    st.subheader("곧 직접 말해야 하는 상황을 그대로 적어주세요")
    st.markdown(
        "문장이 엉망이어도 괜찮습니다. **한국어 그대로** 적어도 OK.\n\n"
        "입력하면 바로 다음 단계로 이동합니다.",
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
# STEP 2: 핵심 맥락 요약 (질문 생략)
# =========================
elif st.session_state.step == 2:
    st.markdown("<div class='cow-step'>STEP 2 · AI 핵심 맥락 요약</div>", unsafe_allow_html=True)
    st.subheader("요약만 보여주고 바로 진행합니다")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("**이 상황은**")
    for line in st.session_state.summary:
        st.markdown(f"• {line}")
    st.markdown('</div>', unsafe_allow_html=True)

    if len(st.session_state.context_text.strip()) < 12:
        st.caption("입력이 너무 짧으면 질문 단계가 나타날 수 있습니다.")
    else:
        st.caption("질문 단계는 정말 애매할 때만 등장합니다.")

    if st.button("➡️ 계속하기", use_container_width=True):
        st.session_state.step = 3
        st.rerun()

# =========================
# STEP 3: 생존 발화 1문장 제시
# =========================
elif st.session_state.step == 3:
    st.markdown("<div class='cow-step'>STEP 3 · 생존 발화 바로 제시</div>", unsafe_allow_html=True)
    st.subheader("아래 한 문장만 기억하면 됩니다")

    st.markdown('<div class="cow-survival">', unsafe_allow_html=True)
    st.markdown("**Survival line**")
    st.markdown(f"👉 *{st.session_state.survival_line}*")
    st.markdown("</div>", unsafe_allow_html=True)

    speak_button(st.session_state.survival_line, "🔊 문장 듣기", key="survival")
    st.caption("왜는 설명하지 않습니다. 지금 당장 쓸 수 있는 것만 제시합니다.")

    if st.button("➡️ 말해보기", use_container_width=True):
        st.session_state.step = 4
        st.rerun()

# =========================
# STEP 4: 말해보기 + 최소 피드백
# =========================
elif st.session_state.step == 4:
    st.markdown("<div class='cow-step'>STEP 4 · 말해보기 + 최소 피드백</div>", unsafe_allow_html=True)
    st.subheader("한 번 말해보세요. 완벽하지 않아도 괜찮습니다.")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    practice_text = st.text_input(
        "앱 안내",
        placeholder="여기에 한번 적어보거나, 실제로 말해보세요.",
        label_visibility="visible",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("피드백 받기", use_container_width=True):
        if not practice_text.strip():
            st.warning("한 줄이라도 적어주세요.")
        else:
            st.markdown('<div class="cow-feedback">', unsafe_allow_html=True)
            st.markdown("**피드백**")
            st.markdown("✔️ 전달됨")
            st.markdown("✔️ 너무 길지 않음")
            st.markdown('</div>', unsafe_allow_html=True)

            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "context": st.session_state.context_text.strip(),
            })

            st.caption("이번 훈련은 자동 저장되었습니다. 리포트 화면은 지금 보이지 않습니다.")

            if st.button("🆕 새 상황"):
                st.session_state.step = 1
                st.session_state.context_text = ""
                st.rerun()

# =========================
# STEP 5: 누적 리포트 (조용히 쌓임)
# =========================
st.markdown("<div class='cow-divider'></div>", unsafe_allow_html=True)
st.subheader("✅ COW 간략화 실행 플로우 (MVP)")
st.markdown(
    """
    **핵심 원칙 (3개만 기억)**  
    1. 선택 최소화  
    2. 말 줄이기  
    3. 훈련은 한 번에 하나만
    """
)

with st.expander("앱 구동 시뮬레이션 보기", expanded=False):
    st.markdown(
        """
        **STEP 1** 자유 맥락 입력 → 바로 다음 단계  
        **STEP 2** 핵심 맥락 요약 (질문 생략 가능)  
        **STEP 3** 생존 발화 1문장 바로 제시  
        **STEP 4** 말해보기 + 최소 피드백  
        **STEP 5** 누적 리포트는 백그라운드 자동 저장  
        """
    )

st.subheader("🔥 간략화의 핵심 효과")
st.table(
    {
        "항목": ["사용 시간", "학습 깊이", "진입 장벽", "초보자 체감"],
        "풀 버전": ["5~7분", "깊음", "중간", "배운다"],
        "간략화 MVP": ["1~2분", "알지만 즉각적", "아주 낮음", "살았다"],
    }
)

st.subheader("🎯 간략화 버전의 정체성 문장")
st.markdown(
    """
    > 말을 잘하게 만드는 앱이 아니라, 지금 당장 말할 수 있게 해주는 앱.  
    > 회의 들어가기 2분 전에 켜는 앱.
    """
)

st.subheader("🧭 풀 버전은 어디로 갔나?")
st.markdown(
    """
    - 설정에서 **훈련 모드 ON**  
    - 처음 3~5회 사용 후 자동 해제  
    - 또는 “오늘은 연습할 시간 있어요” 버튼
    """
)

st.subheader("✂️ 의도적으로 뺀 것")
st.markdown(
    """
    - 사고 구조 설명  
    - 문화 텍스트  
    - 여러 선택 문제  
    - 자세한 리포트 즉시 노출  
    """
)

st.caption("말을 줄였더니, 오히려 말할 수 있게 되었습니다.")
