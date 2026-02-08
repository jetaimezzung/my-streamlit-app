import streamlit as st
import openai

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="COW | Context Over Words",
    page_icon="🐄",
    layout="centered"
)

st.title("🐄 COW : Context Over Words")
st.caption("실전 대화를 미리 훈련하는 언어 앱")

# -----------------------------
# API Key
# -----------------------------
st.sidebar.header("🔑 API 설정")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password"
)

if openai_api_key:
    openai.api_key = openai_api_key

# -----------------------------
# Session State
# -----------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "context" not in st.session_state:
    st.session_state.context = ""

if "details" not in st.session_state:
    st.session_state.details = ""

if "user_sentence" not in st.session_state:
    st.session_state.user_sentence = ""

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# -----------------------------
# Step 1: 자유 맥락 입력
# -----------------------------
if st.session_state.step == 1:
    st.subheader("1️⃣ 상황을 자유롭게 입력하세요")

    st.session_state.context = st.text_area(
        "예시: 해외 바이어와 첫 미팅에서 일정 조율을 해야 함",
        height=120
    )

    if st.button("다음"):
        if not openai_api_key:
            st.warning("OpenAI API Key를 입력해주세요.")
        elif st.session_state.context.strip() == "":
            st.warning("상황을 입력해주세요.")
        else:
            st.session_state.step = 2
            st.experimental_rerun()

# -----------------------------
# Step 2: AI의 되묻기
# -----------------------------
elif st.session_state.step == 2:
    st.subheader("2️⃣ AI가 상황을 구체화합니다")

    with st.spinner("AI가 필요한 정보를 정리 중입니다..."):
        prompt = f"""
        사용자가 다음과 같은 상황을 입력했다:
        "{st.session_state.context}"

        실제 대면 영어 회화를 연습하기 위해
        꼭 필요한 추가 정보 3가지를 항목 형태로 질문해라.
        (예: 상대, 목적, 톤)
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        ai_question = response.choices[0].message.content

    st.markdown("**AI의 질문:**")
    st.write(ai_question)

    st.session_state.details = st.text_area(
        "위 질문에 답해주세요",
        height=120
    )

    if st.button("훈련 시작"):
        if st.session_state.details.strip() == "":
            st.warning("답변을 입력해주세요.")
        else:
            st.session_state.step = 3
            st.experimental_rerun()

# -----------------------------
# Step 3: 발화 생성
# -----------------------------
elif st.session_state.step == 3:
    st.subheader("3️⃣ 실제로 말해볼 문장을 만들어보세요")

    with st.spinner("실전 문장을 생성 중입니다..."):
        prompt = f"""
        상황:
        {st.session_state.context}

        추가 정보:
        {st.session_state.details}

        이 상황에서 실제 대면 비즈니스 영어로
        자연스럽게 말할 수 있는 문장 1개를 제시하라.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        model_sentence = response.choices[0].message.content

    st.markdown("**AI 예시 문장:**")
    st.success(model_sentence)

    st.session_state.user_sentence = st.text_input(
        "이제 직접 말해보세요 (문장 입력)"
    )

    if st.button("피드백 받기"):
        if st.session_state.user_sentence.strip() == "":
            st.warning("문장을 입력해주세요.")
        else:
            st.session_state.step = 4
            st.experimental_rerun()

# -----------------------------
# Step 4: 발화 피드백
# -----------------------------
elif st.session_state.step == 4:
    st.subheader("4️⃣ 발화 피드백")

    with st.spinner("피드백 생성 중..."):
        prompt = f"""
        사용자의 문장:
        "{st.session_state.user_sentence}"

        이 문장을 기준으로 다음을 제공하라:
        1. 자연스러움 평가 (한 줄)
        2. 개선 포인트
        3. 더 자연스러운 대체 문장
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )

        feedback = response.choices[0].message.content

    st.markdown("### 📝 피드백")
    st.write(feedback)

    # 누적 로그 저장
    st.session_state.feedback_log.append({
        "context": st.session_state.context,
        "sentence": st.session_state.user_sentence,
        "feedback": feedback
    })

    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 연습하기"):
            st.session_state.step = 3
            st.experimental_rerun()

    with col2:
        if st.button("새 상황 시작"):
            st.session_state.step = 1
            st.experimental_rerun()

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption("COW는 문장이 아니라 맥락을 훈련합니다.")
