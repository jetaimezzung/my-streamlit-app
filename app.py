import streamlit as st
import requests
from collections import Counter

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(page_title="🎬 나와 어울리는 영화는?", page_icon="🎬")

# -------------------------
# 세션 상태 초기화
# -------------------------
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# -------------------------
# 사이드바: TMDB API Key
# -------------------------
st.sidebar.header("🔑 TMDB API 설정")
api_key = st.sidebar.text_input("TMDB API Key", type="password")

# -------------------------
# 장르 매핑
# -------------------------
GENRE_MAP = {
    "로맨스/드라마": {
        "id": 18,
        "reason": "감정과 관계의 흐름을 중시하는 당신에게 어울리는 장르예요.",
    },
    "액션/어드벤처": {
        "id": 28,
        "reason": "몰입감과 에너지를 통해 스트레스를 해소하는 타입이에요.",
    },
    "SF/판타지": {
        "id": 878,
        "reason": "현실을 벗어난 세계관과 상상력을 즐기는 성향이에요.",
    },
    "코미디": {
        "id": 35,
        "reason": "웃음과 가벼운 분위기를 중요하게 생각하는 타입이에요.",
    },
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# -------------------------
# 제목 & 소개
# -------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문에 답하면, 당신에게 어울리는 영화 장르와 추천작을 알려드려요 🍿")
st.divider()

# -------------------------
# 질문
# -------------------------
answers = []

questions = [
    "Q1. 하루 종일 바빴던 날, 밤에 딱 하나만 보고 잘 수 있다면?",
    "Q2. 시험이 끝난 직후, 가장 끌리는 약속은?",
    "Q3. 영화 속 주인공이 된다면?",
    "Q4. 친구의 영화 추천 멘트 중 가장 끌리는 건?",
    "Q5. 주말에 혼자 영화를 본다면?",
]

options = ["로맨스/드라마", "액션/어드벤처", "SF/판타지", "코미디"]

for q in questions:
    answers.append(st.radio(q, options))

st.divider()

# -------------------------
# 결과 보기 버튼
# -------------------------
if st.button("결과 보기"):
    st.session_state.show_result = True

# -------------------------
# 결과 화면
# -------------------------
if st.session_state.show_result:

    if not api_key:
        st.error("❗ 사이드바에 TMDB API Key를 입력해주세요.")
        st.stop()

    # 장르 분석
    genre_counter = Counter(answers)
    selected_genre = genre_counter.most_common(1)[0][0]
    genre_id = GENRE_MAP[selected_genre]["id"]
    genre_reason = GENRE_MAP[selected_genre]["reason"]

    # 결과 제목
    st.markdown(
        f"## 🎯 당신에게 딱인 장르는: **{selected_genre}**!"
    )
    st.write(genre_reason)
    st.divider()

    # TMDB API 호출
    with st.spinner("🎥 추천 영화를 불러오는 중입니다..."):
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}&with_genres={genre_id}"
            f"&language=ko-KR&sort_by=popularity.desc"
        )
        response = requests.get(url)
        data = response.json()

    movies = data.get("results", [])[:5]

    # -------------------------
    # 영화 카드 (3열)
    # -------------------------
    cols = st.columns(3)

    for idx, movie in enumerate(movies):
        with cols[idx % 3]:

            if movie.get("poster_path"):
                st.image(POSTER_BASE_URL + movie["poster_path"], use_container_width=True)
            else:
                st.write("포스터 없음")

            st.markdown(f"### 🎬 {movie['title']}")
            st.write(f"⭐ 평점: {movie['vote_average']}")

            with st.expander("상세 보기"):
                st.write(
                    movie["overview"]
                    if movie["overview"]
                    else "줄거리 정보가 없습니다."
                )
                st.markdown(
                    f"**이 영화를 추천하는 이유:**\n\n"
                    f"{selected_genre} 성향의 당신에게 잘 맞는 인기 작품이에요."
                )
