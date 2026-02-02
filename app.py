import streamlit as st
import requests
from collections import Counter
import base64

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
# SVG 배경 생성
# -------------------------
def svg_bg(svg: str):
    return base64.b64encode(svg.encode()).decode()

HEART_BG = svg_bg("""
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" opacity="0.15">
<text x="40" y="120" font-size="64">💖</text>
</svg>
""")

FIRE_BG = svg_bg("""
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" opacity="0.15">
<text x="40" y="120" font-size="64">🔥</text>
</svg>
""")

SPACE_BG = svg_bg("""
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" opacity="0.15">
<text x="40" y="120" font-size="64">✨</text>
</svg>
""")

COMEDY_BG = svg_bg("""
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" opacity="0.15">
<text x="40" y="120" font-size="64">😂</text>
</svg>
""")

# -------------------------
# 장르 매핑
# -------------------------
GENRE_MAP = {
    "로맨스/드라마": {"id": 18, "bg": HEART_BG, "accent": "#ff4b91", "emoji": "💖"},
    "액션/어드벤처": {"id": 28, "bg": FIRE_BG, "accent": "#ff4b4b", "emoji": "🔥"},
    "SF/판타지": {"id": 878, "bg": SPACE_BG, "accent": "#7f7cff", "emoji": "🌌"},
    "코미디": {"id": 35, "bg": COMEDY_BG, "accent": "#ffb703", "emoji": "😂"},
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# -------------------------
# 기본 CSS (가독성 핵심)
# -------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-repeat: repeat;
    }

    /* 질문 카드 */
    .question-card {
        background: rgba(255, 255, 255, 0.92);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        color: #222;
    }

    /* 라디오 글씨 */
    label, .stRadio > div {
        color: #222 !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# 제목
# -------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("당신의 선택에 따라 영화 취향과 테마가 바뀝니다 🍿")
st.divider()

# -------------------------
# 질문 (카드 적용)
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
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    answers.append(st.radio(q, options, key=q))
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🎯 결과 보기"):
    st.session_state.show_result = True

# -------------------------
# 결과 화면
# -------------------------
if st.session_state.show_result:

    counter = Counter(answers)
    main_genre = counter.most_common(1)[0][0]
    genre = GENRE_MAP[main_genre]

    # 테마 배경 적용
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/svg+xml;base64,{genre['bg']}");
        }}
        h1, h2 {{
            color: {genre['accent']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="question-card" style="text-align:center;">
            <h2>{genre['emoji']} 당신에게 딱인 장르는</h2>
            <h1>{main_genre}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🎥 추천 영화")

    with st.spinner("TMDB에서 영화를 불러오는 중입니다..."):
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}&with_genres={genre['id']}"
            f"&language=ko-KR&sort_by=popularity.desc"
        )
        movies = requests.get(url).json().get("results", [])[:6]

    cols = st.columns(3)
    for i, movie in enumerate(movies):
        with cols[i % 3]:
            if movie.get("poster_path"):
                st.image(POSTER_BASE_URL + movie["poster_path"], use_container_width=True)
            st.markdown(f"### {movie['title']}")
            st.markdown(f"⭐ {movie['vote_average']}")
