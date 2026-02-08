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

st.title("🐄 COW : Context Over Words")
st.caption("실전 대화를 미리 훈련하는 맥락 중심 언어 앱")

# =========================
# Session State 초기화
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1
if "context" not in st.session_state:
    st.session_state.context = ""
if "details" not in st.session_state:
    st.session_state.details = ""
if "user_sentence" not in st.session_state:
    st.session_state.user_sentence = ""
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# STEP 1: 자유 맥락 입력
# =========================
if st.session_state.step == 1:
    st.subheader("1️⃣ 상황을 자유롭게 입력하세요")
    st.session_state.context = st.text_area(
        "예: 해외 바이어와 첫 미팅에서 일정 조율을 해야 함",
        height=120
    )

    if st.button("다음"):
        if st.session_state.context.strip() == "":
            st.warning("상황을 입력하세요.")
        else:
            st.session_state.step = 2
            st.rerun()

# =========================
# STEP 2: 목적형 되묻기 (API 없이 고정 로직)
# =========================
elif st.session_state.step == 2:
    st.subheader("2️⃣ 상황을 더 정확히 하기 위한 질문")

    st.markdown(
        """
        다음 항목에 답해주세요:
        - **상대는 누구인가요?**  
        - **이 대화의 목적은 무엇인가요?**  
        - **원하는 말의 톤은 어떤가요?** (정중함 / 캐주얼 / 단호함 등)
        """
    )

    st.session_state.details = st.text_area(
        "답변을 입력하세요",
        height=120
    )

    if st.button("훈련 시작"):
        if st.session_state.details.strip() == "":
            st.warning("모든 항목에 대한 답변을 입력하세요.")
        else:
            st.session_state.step = 3
            st.rerun()

# =========================
# STEP 3: 실전 발화 예시 (API 없이 템플릿)
# =========================
elif st.session_state.step == 3:
    st.subheader("3️⃣ 실전에서 사용할 수 있는 문장 예시")

    example_sentence = (
        "I’d like to discuss the schedule and see how we can align our timelines "
        "in a way that works well for both sides."
    )

    st.success(example_sentence)

    st.session_state.user_sentence = st.text_input(
        "이제 직접 말해볼 문장을 입력하세요"
    )

    if st.button("피드백 받기"):
        if st.session_state.user_sentence.strip() == "":
            st.warning("문장을 입력하세요.")
        else:
            st.session_state.step = 4
            st.rerun()

# =========================
# STEP 4: 발화 피드백 (API 없이 규칙 기반)
# =========================
elif st.session_state.step == 4:
    st.subheader("4️⃣ 발화 피드백")

    user_text = st.session_state.user_sentence

    feedback = f"""
    **자연스러움 평가:**  
    의미 전달은 가능하지만, 표현이 다소 직설적이어서 비즈니스 상황에서는 부드럽게 조정할 여지가 있습니다.

    **개선 포인트:**  
    요청 의도를 완곡하게 표현하고, 상대를 배려하는 표현을 추가하면 더 자연스럽습니다.

    **대체 문장 예시:**  
    *I was wondering if we could go over the schedule together and find a timing that works for both of us.*
    """

    st.write(feedback)

    # =========================
    # STEP 5: 누적 리포트용 기록 저장
    # =========================
    st.session_state.history.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "context": st.session_state.context,
        "user_sentence": user_text
    })

    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 연습"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("새 상황"):
            st.session_state.step = 1
            st.rerun()

# =========================
# 누적 연습 리포트 (핵심 기능 5번)
# =========================
st.divider()
st.subheader("📊 나의 발화 연습 기록")

if st.session_state.history:
    for h in reversed(st.session_state.history):
        st.markdown(
            f"- **[{h['time']}]** {h['user_sentence']}"
        )
else:
    st.caption("아직 저장된 연습 기록이 없습니다.")

st.caption("COW는 문장이 아니라 맥락을 훈련합니다.")
