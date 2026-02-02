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

# -------------------------
# 장르 & 테마 매핑
# -------------------------
GENRE_MAP = {
    "로맨스/드라마": {
        "id": 18,
        "desc": "감정과 관계에 깊이 공감하는 타입",
        "theme": {
            "bg": "#fff0f5",
            "card": "#ffffff",
            "accent": "#ff6b81",
        },
    },
    "액션/어드벤처": {
        "id": 28,
        "desc": "몰입과 긴장감을 즐기는 에너지형 타입",
        "theme": {
            "bg": "#1e1e1e",
            "card": "#2a2a2a",
            "accent": "#ff4b4b",
        },
    },
    "SF/판타지": {
        "id": 878,
        "desc": "상상력과 세계관에 강하게 끌리는 타입",
        "theme": {
            "bg": "#1b1033",
            "card": "#2e1f5e",
            "accent": "#9d7bff",
        },
    },
    "코미디": {
        "id": 35,
        "desc": "웃음과 분위기를 중시하는 긍정형 타입",
        "theme": {
            "bg": "#fffbe6",
            "card": "#ffffff",
            "accent": "#f4c430",
        },
    },
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# -------------------------
# 제목
# -------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문에 답하면, 당신의 영화 취향에 맞춰 화면 분위기까지 바뀝니다 🍿")
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
    # 장르 분석
    # -------------------------
    counter = Counter(answers)
    main_genre = counter.most_common(1)[0][0]
    genre_info = GENRE_MAP[main_genre]
    theme = genre_info["theme"]

    # -------------------------
    # 🎨 테마 CSS 적용
    # -------------------------
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme["bg"]};
        }}
        .movie-card {{
            background-color: {theme["card"]};
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}
        .accent {{
            color: {theme["accent"]};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # -------------------------
    # 결과 헤더
    # -------------------------
    st.markdown(
        f"""
        <div class="movie-card" style="text-align:center;">
            <h2>🎯 당신에게 딱인 장르는</h2>
            <h1 class="accent">{main_genre}</h1>
            <p>{genre_info["desc"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -------------------------
    # 영화 추천
    # -------------------------
    with st.spinner("🎥 추천 영화를 불러오는 중입니다..."):
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}&with_genres={genre_info['id']}"
            f"&language=ko-KR&sort_by=popularity.desc"
        )
        data = requests.get(url).json()

    movies = data.get("results", [])[:6]
    cols = st.columns(3)

    for idx, movie in enumerate(movies):
        with cols[idx % 3]:
            st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

            if movie.get("poster_path"):
                st.image(
                    POSTER_BASE_URL + movie["poster_path"],
                    use_container_width=True
                )

            st.markdown(f"### 🎬 {movie['title']}")
            st.markdown(f"⭐ <span class='accent'>{movie['vote_average']}</span>", unsafe_allow_html=True)

            with st.expander("상세 정보"):
                st.write(
                    movie["overview"]
                    if movie["overview"]
                    else "줄거리 정보가 없습니다."
                )
                st.write(
                    f"이 영화는 **{main_genre}** 성향의 당신에게 특히 잘 맞는 작품이에요."
                )

            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # -------------------------
    # 다시 테스트
    # -------------------------
    if st.button("🔄 다시 테스트하기"):
        st.session_state.show_result = False
        st.experimental_rerun()
