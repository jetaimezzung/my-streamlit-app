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
            "bg": "#ffe6f0",
            "accent": "#ff4b91",
            "emoji": "💖"
        }
    },
    "액션/어드벤처": {
        "id": 28,
        "desc": "강한 몰입과 에너지를 즐기는 타입",
        "theme": {
            "bg": "#111111",
            "accent": "#ff4b4b",
            "emoji": "🔥"
        }
    },
    "SF/판타지": {
        "id": 878,
        "desc": "상상력과 세계관에 빠지는 타입",
        "theme": {
            "bg": "#1b1f3b",
            "accent": "#7f7cff",
            "emoji": "🌌"
        }
    },
    "코미디": {
        "id": 35,
        "desc": "웃음과 분위기를 중시하는 타입",
        "theme": {
            "bg": "#fff6cc",
            "accent": "#ffb703",
            "emoji": "😂"
        }
    }
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# -------------------------
# 제목
# -------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문에 답하면, 당신의 영화 취향에 맞는 추천을 해드려요 🍿")
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
# 결과 버튼
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

    # 장르 분석
    counter = Counter(answers)
    total = sum(counter.values())
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
        h1, h2, h3 {{
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
        <div style="
            padding: 30px;
            border-radius: 18px;
            background-color: white;
            text-align: center;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
        ">
            <h2>{theme["emoji"]} 당신에게 딱인 장르는</h2>
            <h1>{main_genre}</h1>
            <p>{genre_info["desc"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -------------------------
    # 취향 분포
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
            f"?api_key={api_key}&with_genres={genre_info['id']}"
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

            with st.expander("상세 정보"):
                st.write(movie["overview"] or "줄거리 정보가 없습니다.")
                st.markdown(
                    f"👉 {main_genre} 성향의 당신에게 잘 맞는 인기 작품이에요."
                )

    st.divider()

    # -------------------------
    # 다시 테스트
    # -------------------------
    if st.button("🔄 다시 테스트하기"):
        st.session_state.show_result = False
        st.experimental_rerun()
