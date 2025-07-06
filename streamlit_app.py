import streamlit as st
from tmdb_recommender import TMDbRecommender
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_IMG = "https://motivatics.com/assets/images/animes/default_poster.jpg"

st.set_page_config(page_title="Movie Recommender", layout="wide")

# --- Sidebar ---
st.sidebar.title("Movie Recommendation")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Home", "Trending", "Top Rated", "Genres"])
st.sidebar.markdown("---")

# Genre filter
@st.cache_resource(show_spinner=False)
def get_recommender():
    recommender = TMDbRecommender()
    if not recommender.load_model():
        if recommender.load_data():
            recommender.save_model()
        else:
            st.error("Could not load TMDb data.")
            st.stop()
    return recommender

recommender = get_recommender()
genres = recommender.get_genres()
selected_genre = st.sidebar.selectbox("Filter by Genre", ["All"] + genres)

@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
   
    if TMDB_API_KEY:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                poster_path = data.get("poster_path")
                rating = data.get("vote_average")
                genres = ', '.join([g['name'] for g in data.get('genres', [])])
                overview = data.get('overview')
                year = data.get('release_date', '')[:4]
                poster_url = TMDB_IMG_BASE + poster_path if poster_path else PLACEHOLDER_IMG
                
                if data.get('title'):
                    return poster_url, rating, genres, overview, year
        except Exception:
            pass
    # Fallback to local dataset
    row = recommender.movies_df[recommender.movies_df['id'] == movie_id]
    if not row.empty:
        movie = row.iloc[0]
        poster_url = PLACEHOLDER_IMG
        rating = movie.get('vote_average', None)
        genres = ''
        try:
            import ast
            genres_list = ast.literal_eval(movie['genres'])
            genres = ', '.join([g['name'] for g in genres_list])
        except Exception:
            genres = movie.get('genres', '')
        overview = movie.get('overview', '')
        year = str(movie.get('release_date', ''))[:4]
        return poster_url, rating, genres, overview, year
    # If not found at all
    return PLACEHOLDER_IMG, None, None, None, None

#  Session State for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'main'  # 'main' or 'detail'
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None

st.markdown(
    """
    <style>
    .movie-card {
        background: #181818;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        padding: 18px 12px 12px 12px;
        margin-bottom: 24px;
        min-height: 410px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    .movie-card img {
        height: 210px !important;
        width: auto !important;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10);
    }
    .movie-title-btn button {
        width: 100%;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 6px;
        border-radius: 6px;
    }
    .movie-meta {
        color: #b3b3b3;
        font-size: 0.95rem;
        margin-bottom: 4px;
        text-align: center;
    }
    .movie-rating {
        background: #222831;
        color: #ffd700;
        font-weight: bold;
        border-radius: 8px;
        padding: 2px 10px;
        display: inline-block;
        margin-bottom: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Main Grid View ---
def display_movie_grid(movies, n_cols=4):
    if movies.empty:
        st.info("No movies found.")
        return
    movie_list = list(movies.iterrows())
    for i in range(0, len(movie_list), n_cols):
        row_movies = movie_list[i:i+n_cols]
        cols = st.columns(len(row_movies))
        for idx, (index, movie) in enumerate(row_movies):
            with cols[idx]:
                with st.container():
                    poster_url, rating, genres, overview, year = fetch_movie_details(int(movie['id']))
                    st.image(poster_url, width=140)
                    if st.button(movie['title'], key=f"main_{movie['id']}"):
                        st.session_state.selected_movie_id = int(movie['id'])
                        st.session_state.page = 'detail'
                        st.experimental_rerun()
                    meta = f"{genres} {year}" if genres or year else ""
                    if meta.strip():
                        st.markdown(f'<div class="movie-meta">{meta}</div>', unsafe_allow_html=True)
                    if rating is not None:
                        st.markdown(f'<div class="movie-rating">⭐ {rating:.1f}</div>', unsafe_allow_html=True)
                    if overview:
                        with st.expander("Overview"):
                            st.write(overview)

def show_main_grid():
    st.title("🍿 Movie Recommendation System")
   
    search_query = st.text_input("Search for a movie:", "")
 
    if search_query:
        results = recommender.search_movies(search_query, 12)
        st.subheader(f"🔎 Search Results for '{search_query}'")
        movies = results
    else:
        
        st.subheader("🍿 Trending Movies")
        if selected_genre == "All":
            movies = recommender.get_popular_movies(8)
        else:
            movies = recommender.get_popular_movies(8, selected_genre)
    display_movie_grid(movies, n_cols=4)
    
    st.subheader("⭐ Top Rated Movies")
    if selected_genre == "All":
        top_rated = recommender.movies_df.sort_values('vote_average', ascending=False).head(8)
    else:
        top_rated = recommender.movies_df[recommender.movies_df['genres'].str.contains(selected_genre, case=False, na=False)].sort_values('vote_average', ascending=False).head(8)
    display_movie_grid(top_rated, n_cols=4)


def show_movie_detail(movie_id):
    st.button("← Back", on_click=lambda: set_page_main(), key="back_btn")
    poster_url, rating, genres_str, overview, year = fetch_movie_details(movie_id)
    movie_title = recommender.movies_df[recommender.movies_df['id'] == movie_id]['title'].values[0]
    col1, col2 = st.columns([1,2])
    with col1:
        st.image(poster_url, width=300)
    with col2:
        st.markdown(f'<div class="main-movie-title">{movie_title} {f"({year})" if year else ""}</div>', unsafe_allow_html=True)
        if genres_str:
            st.markdown(f'<div class="main-movie-genres">{genres_str}</div>', unsafe_allow_html=True)
        if rating is not None:
            st.markdown(f'<div class="movie-rating">⭐ {rating:.1f}</div>', unsafe_allow_html=True)
        if overview:
            st.markdown(f'<div class="main-movie-overview">{overview}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🎬 Recommended Movies")
    recs = recommender.get_recommendations(movie_title, 8)
    display_movie_grid(recs, n_cols=4)

def set_page_main():
    st.session_state.page = 'main'
    st.session_state.selected_movie_id = None


if st.session_state.page == 'main':
    show_main_grid()
elif st.session_state.page == 'detail' and st.session_state.selected_movie_id:
    show_movie_detail(st.session_state.selected_movie_id)


if not TMDB_API_KEY:
    st.warning("TMDb API key not found. Please create a .env file in your project directory with the line: TMDB_API_KEY=YOUR_ACTUAL_API_KEY_HERE and restart the app.")