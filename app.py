import streamlit as st
from datetime import datetime

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="COW · Context Over Words",
    layout="centered",
)

# -------------------------
# Session State Init
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "context" not in st.session_state:
    st.session_state.context = ""

if "clarification" not in st.session_state:
    st.session_state.clarification = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "questions" not in st.session_state:
    st.session_state.questions = ""

if "survival_line" not in st.session_state:
    st.session_state.survival_line = ""

if "practice_text" not in st.session_state:
    st.session_state.practice_text = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# Navigation Helpers
# -------------------------
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step = max(1, st.session_state.step - 1)

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = 1

# -------------------------
# Mock AI Logic (API-free)
# -------------------------
def mock_summary_and_questions(context):
    summary = f"지금 사용자는 '{context}' 상황에서 영어로 말해야 하는 상황에 처해 있습니다."

    questions = ""
    if len(context) < 25:
        questions = (
            "- 상대방은 누구인가요?\n"
            "- 요청/설명/사과/질문 중 무엇에 가까운가요?"
        )

    return summary, questions


def mock_survival_line(context):
    return "Could you give me a moment to think about that?"


def mock_feedback(user_text, target_text):
    feedback = []
    if len(user_text.split()) > len(target_text.split()) + 5:
        feedback.append("조금 길게 말한 편입니다. 핵심만 줄여도 좋겠습니다.")
    else:
        feedback.append("길이는 적절합니다.")

    if target_text.lower() in user_text.lower():
        feedback.append("의도 전달이 잘 되었습니다.")
    else:
        feedback.append("의도는 전달되었지만 표현을 더 단순화할 수 있습니다.")

    return " ".join(feedback)


def mock_progress_report(history):
    return (
        "최근 기록을 보면, 사용자는 긴 문장보다 짧고 안전한 표현을 점점 더 잘 선택하고 있습니다. "
        "앞으로는 문장 첫 부분을 더 자신 있게 말하는 연습을 해보세요."
    )

# -------------------------
# UI Header
# -------------------------
st.markdown("## 🐄 COW")
st.caption("Context Over Words · 지금 필요한 말부터 훈련하는 영어 앱")
st.divider()

# -------------------------
# STEP 1: Context Input
# -------------------------
if st.session_state.step == 1:
    st.subheader("STEP 1 · 지금 곧 말해야 하는 상황을 써주세요")

    st.session_state.context = st.text_area(
        "예: 처음 만난 외국인에게 길을 물어봐야 하는 상황",
        value=st.session_state.context,
        height=120,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.button("초기화", on_click=reset_app)
    with col2:
        if st.button("다음"):
            if st.session_state.context.strip():
                next_step()
            else:
                st.warning("상황을 입력해주세요.")

# -------------------------
# STEP 2: Context Understanding
# -------------------------
elif st.session_state.step == 2:
    st.subheader("STEP 2 · 상황 이해")

    if not st.session_state.summary:
        summary, questions = mock_summary_and_questions(
            st.session_state.context
        )
        st.session_state.summary = summary
        st.session_state.questions = questions

    st.markdown(f"**우리가 이해한 상황은 이렇습니다:**\n\n{st.session_state.summary}")

    if st.session_state.questions:
        st.markdown(
            "\n**상황을 더 정확히 이해하기 위해 다음 항목에 답해주세요:**\n"
            + st.session_state.questions
        )

        st.session_state.clarification = st.text_area(
            "추가로 답할 내용이 있다면 입력하세요 (선택)",
            value=st.session_state.clarification,
            height=80,
        )

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("계속", on_click=next_step)

# -------------------------
# STEP 3: Survival Line
# -------------------------
elif st.session_state.step == 3:
    st.subheader("STEP 3 · 지금 쓸 문장 하나")

    if not st.session_state.survival_line:
        st.session_state.survival_line = mock_survival_line(
            st.session_state.context
        )

    st.success(st.session_state.survival_line)

    st.caption("이 문장 하나만 기억해도 지금 상황은 넘어갈 수 있습니다.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("말해보기", on_click=next_step)

# -------------------------
# STEP 4: Practice
# -------------------------
elif st.session_state.step == 4:
    st.subheader("STEP 4 · 한번 말해보세요")
    st.caption("완벽하지 않아도 괜찮습니다.")

    st.session_state.practice_text = st.text_area(
        "직접 말한 문장을 적어보세요",
        value=st.session_state.practice_text,
        height=100,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button(
            "피드백 받기",
            on_click=next_step,
            disabled=not st.session_state.practice_text.strip(),
        )

# -------------------------
# STEP 5: Feedback
# -------------------------
elif st.session_state.step == 5:
    st.subheader("STEP 5 · 발화 피드백")

    if not st.session_state.feedback:
        st.session_state.feedback = mock_feedback(
            st.session_state.practice_text,
            st.session_state.survival_line,
        )

        st.session_state.history.append(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "context": st.session_state.context,
                "target": st.session_state.survival_line,
                "practice": st.session_state.practice_text,
                "feedback": st.session_state.feedback,
            }
        )

    st.info(f"이번 발화에 대한 피드백입니다.\n\n{st.session_state.feedback}")

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("리포트 보기", on_click=next_step)

# -------------------------
# STEP 6: Progress Report
# -------------------------
elif st.session_state.step == 6:
    st.subheader("STEP 6 · 누적 리포트")

    if st.session_state.history:
        report = mock_progress_report(st.session_state.history)
        st.success(report)
    else:
        st.write("아직 누적된 기록이 없습니다.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("뒤로", on_click=prev_step)
    with col2:
        st.button("처음으로", on_click=reset_app)
