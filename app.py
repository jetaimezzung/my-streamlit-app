import streamlit as st
import requests
from collections import Counter

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="🎬 나와 어울리는 영화는?",
    page_icon="🎬",
    layout="wide"
)

# -------------------------
# 세션 상태
# -------------------------
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# -------------------------
# 사이드바
# -------------------------
st.sidebar.header("🔑 TMDB API 설정")
api_key = st.sidebar.text_input("TMDB API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("🎓 **대학생 대상 영화 심리테스트**")

# -------------------------
# 장르 매핑
# -------------------------
GENRE_MAP = {
    "로맨스/드라마": {
        "id": 18,
        "desc": "감정과 관계의 흐름에 민감한 타입",
    },
    "액션/어드벤처": {
        "id": 28,
        "desc": "에너지와 몰입을 통해 스트레스를 푸는 타입",
    },
    "SF/판타지": {
        "id": 878,
        "desc": "상상력과 세계관에 강하게 끌리는 타입",
    },
    "코미디": {
        "id": 35,
        "desc": "웃음과 분위기를 중요하게 생각하는 타입",
    },
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# -------------------------
# 제목
# -------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("당신의 선택을 바탕으로 영화 취향을 분석하고, 딱 맞는 영화를 추천해드려요 🍿")
st.divider()

# -------------------------
# 질문
# -------------------------
questions = [
    "Q1. 하루 종일 바빴던 날, 밤에 딱 하나만 보고 잘 수 있다면?",
    "Q2. 시험이 끝난 직후, 가장 끌리는 약속은?",
    "Q3. 영화 속 주인공이 된다면?",
    "Q4. 친구의 영화 추천 멘트 중 가장 끌리는 건?",
    "Q5. 주말에 혼자 영화를 본다면?",
]

options = list(GENRE_MAP.keys())
answers = []

for q in questions:
    answers.append(st.radio(q, options))

st.divider()

# -------------------------
# 버튼
# -------------------------
col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    if st.button("🎯 결과 보기"):
        st.session_state.show_result = True

# -------------------------
# 결과 화면
# -------------------------
if st.session_state.show_result:

    if not api_key:
        st.error("❗ 사이드바에 TMDB API Key를 입력해주세요.")
        st.stop()

    # -------------------------
    # 성향 분석
    # -------------------------
    counter = Counter(answers)
    total = sum(counter.values())
    main_genre = counter.most_common(1)[0][0]
    genre_id = GENRE_MAP[main_genre]["id"]

    # -------------------------
    # 결과 헤더 (디자인 강조)
    # -------------------------
    st.markdown(
        f"""
        <div style="
            padding: 20px;
            border-radius: 12px;
            background-color: #f4f6fa;
            text-align: center;
        ">
            <h2>🎯 당신에게 딱인 장르는</h2>
            <h1 style="color:#ff4b4b;">{main_genre}</h1>
            <p>{GENRE_MAP[main_genre]["desc"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -------------------------
    # 성향 퍼센트 표시
    # -------------------------
    st.subheader("📊 나의 영화 취향 분포")
    for genre, count in counter.items():
        percent = int((count / total) * 100)
        st.write(f"{genre} : {percent}%")
        st.progress(percent)

    st.divider()

    # -------------------------
    # 영화 추천
    # -------------------------
    st.subheader("🎥 추천 영화")

    with st.spinner("TMDB에서 영화를 불러오는 중입니다..."):
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}&with_genres={genre_id}"
            f"&language=ko-KR&sort_by=popularity.desc"
        )
        response = requests.get(url)
        data = response.json()

    movies = data.get("results", [])[:6]

    cols = st.columns(3)

    for idx, movie in enumerate(movies):
        with cols[idx % 3]:

            if movie.get("poster_path"):
                st.image(POSTER_BASE_URL + movie["poster_path"], use_container_width=True)
            else:
                st.write("포스터 없음")

            st.markdown(f"### 🎬 {movie['title']}")
            st.markdown(f"⭐ **{movie['vote_average']} / 10**")

            with st.expander("왜 이 영화를 추천하나요?"):
                st.write(
                    movie["overview"]
                    if movie["overview"]
                    else "줄거리 정보가 없습니다."
                )
                st.markdown(
                    f"👉 당신은 **{main_genre}** 선택 비중이 가장 높았어요. "
                    f"이 영화는 해당 장르에서 많은 사람들이 좋아한 작품이에요."
                )

    st.divider()

    # -------------------------
    # 다시 테스트하기
    # -------------------------
    if st.button("🔄 다시 테스트하기"):
        st.session_state.show_result = False
        st.experimental_rerun()
