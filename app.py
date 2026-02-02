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
# 사이드바: TMDB API Key 입력
# -------------------------
st.sidebar.header("🔑 TMDB API 설정")
api_key = st.sidebar.text_input("TMDB API Key", type="password")

# -------------------------
# 장르 매핑
# -------------------------
GENRE_MAP = {
    "로맨스/드라마": {"id": 18, "reason": "감정선과 관계에 집중하는 당신에게 어울리는 영화예요."},
    "액션/어드벤처": {"id": 28, "reason": "에너지 넘치고 몰입감 있는 전개를 좋아하는 성향이에요."},
    "SF/판타지": {"id": 878, "reason": "현실을 벗어난 세계관과 상상력을 즐기는 타입이에요."},
    "코미디": {"id": 35, "reason": "웃음과 가벼운 분위기를 중시하는 성향이에요."},
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# -------------------------
# 제목 & 소개
# -------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문에 답하면, 당신에게 딱 맞는 영화와 추천작을 알려드려요 🍿")
st.divider()

# -------------------------
# 질문 UI
# -------------------------
answers = []

answers.append(
    st.radio(
        "Q1. 하루 종일 바빴던 날, 밤에 딱 하나만 보고 잘 수 있다면?",
        ["로맨스/드라마", "액션/어드벤처", "SF/판타지", "코미디"],
    )
)

answers.append(
    st.radio(
        "Q2. 시험이 끝난 직후, 가장 끌리는 약속은?",
        ["로맨스/드라마", "액션/어드벤처", "SF/판타지", "코미디"],
    )
)

answers.append(
    st.radio(
        "Q3. 영화 속 주인공이 된다면?",
        ["로맨스/드라마", "액션/어드벤처", "SF/판타지", "코미디"],
    )
)

answers.append(
    st.radio(
        "Q4. 친구의 영화 추천 멘트 중 가장 끌리는 건?",
        ["로맨스/드라마", "액션/어드벤처", "SF/판타지", "코미디"],
    )
)

answers.append(
    st.radio(
        "Q5. 주말에 혼자 영화를 본다면?",
        ["로맨스/드라마", "액션/어드벤처", "SF/판타지", "코미디"],
    )
)

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

    # 1️⃣ 장르 분석
    genre_counter = Counter(answers)
    selected_genre = genre_counter.most_common(1)[0][0]
    genre_id = GENRE_MAP[selected_genre]["id"]
    reason_text = GENRE_MAP[selected_genre]["reason"]

    st.subheader(f"🎯 당신에게 어울리는 장르: **{selected_genre}**")
    st.write(reason_text)
    st.divider()

    # 2️⃣ TMDB API 호출
    with st.spinner("추천 영화를 불러오는 중입니다... 🎥"):
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}&with_genres={genre_id}&language=ko-KR&sort_by=popularity.desc"
        )
        response = requests.get(url)
        data = response.json()

    movies = data.get("results", [])[:5]

    # 3️⃣ 영화 출력
    for movie in movies:
        col1, col2 = st.columns([1, 2])

        with col1:
            if movie["poster_path"]:
                st.image(POSTER_BASE_URL + movie["poster_path"])
            else:
                st.write("포스터 없음")

        with col2:
            st.markdown(f"### 🎬 {movie['title']}")
            st.write(f"⭐ 평점: {movie['vote_average']}")
            st.write(movie["overview"] if movie["overview"] else "줄거리 정보가 없습니다.")
            st.markdown(
                f"**추천 이유:** {selected_genre} 성향의 당신에게 잘 맞는 인기 작품이에요."
            )

        st.divider()
