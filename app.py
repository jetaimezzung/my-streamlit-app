import streamlit as st
from datetime import datetime

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="COW : Context Over Words",
    page_icon="🐄",
    layout="centered"
)

# =========================
# Global Style (UI 개선)
# =========================
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .cow-card {
        background-color: #f7f9fb;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .cow-survival {
        background-color: #eef6ff;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #4a90e2;
        font-size: 1.1rem;
    }
    .cow-feedback {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #34c759;
    }
    .small {color: #666; font-size: 0.9rem;}
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
if "context" not in st.session_state:
    st.session_state.context = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "user_sentence" not in st.session_state:
    st.session_state.user_sentence = ""
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# STEP 1: 자유 맥락 입력 (핵심)
# =========================
if st.session_state.step == 1:
    st.subheader("STEP 1 · 지금 곧 말해야 하는 상황을 써주세요")

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.session_state.context = st.text_area(
        "예: 해외 바이어에게 일정이 조금 늦어질 것 같다고 말해야 함",
        height=120,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➡️ 바로 다음"):
        if st.session_state.context.strip() == "":
            st.warning("상황을 한 줄로라도 써주세요.")
        else:
            st.session_state.step = 2
            st.rerun()

# =========================
# STEP 2: 핵심 맥락 요약 (질문 생략)
# =========================
elif st.session_state.step == 2:
    st.subheader("STEP 2 · 상황 핵심만 정리합니다")

    # API 없이 고정 요약 로직
    st.session_state.summary = (
        "• 대면 비즈니스 상황\n"
        "• 요청 또는 설명이 필요한 발언\n"
        "• 짧고 안전하게 말하는 것이 중요"
    )

    st.markdown('<div class="cow-card">', unsafe_allow_html=True)
    st.markdown("**이 상황은:**")
    st.markdown(st.session_state.summary)
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("질문은 정말 애매할 때만 나옵니다. 지금은 바로 진행합니다.")

    if st.button("➡️ 계속하기"):
        st.session_state.step = 3
        st.rerun()

# =========================
# STEP 3: 생존 발화 1문장 제시
# =========================
elif st.session_state.step == 3:
    st.subheader("STEP 3 · 이 문장 하나만 기억하세요")

    survival_line = "I may need a bit more time on my task."

    st.markdown('<div class="cow-survival">', unsafe_allow_html=True)
    st.markdown("**Survival Line**")
    st.markdown(f"👉 *{survival_line}*")
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("왜 그런지는 설명하지 않습니다. 지금 당장 쓸 수 있는 것만 줍니다.")

    if st.button("➡️ 말해보기"):
        st.session_state.step = 4
        st.rerun()

# =========================
# STEP 4: 말해보기 + 최소 피드백
# =========================
elif st.session_state.step == 4:
    st.subheader("STEP 4 · 한 번 말해보세요")

    st.session_state.user_sentence = st.text_input(
        "지금 입으로 말한다고 생각하고 써보세요",
        label_visibility="collapsed"
    )

    if st.button("피드백 받기"):
        if st.session_state.user_sentence.strip() == "":
            st.warning("한 문장만 써도 충분합니다.")
        else:
            st.markdown('<div class="cow-feedback">', unsafe_allow_html=True)
            st.markdown("**피드백**")
            st.markdown("✔️ 의미 전달됨")
            st.markdown("✔️ 너무 길지 않음")
            st.markdown('</div>', unsafe_allow_html=True)

            # STEP 5: 백그라운드 저장
            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "sentence": st.session_state.user_sentence
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
st.divider()
st.subheader("📌 최근 연습 기록")

if st.session_state.history:
    for h in reversed(st.session_state.history[-5:]):
        st.markdown(f"- **[{h['time']}]** {h['sentence']}")
else:
    st.caption("아직 저장된 기록이 없습니다.")

st.caption("말을 줄였더니, 오히려 말할 수 있게 되었습니다.")
