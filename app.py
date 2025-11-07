import streamlit as st
import pickle
import pandas as pd
import requests
import json
import logging
import os

# ===================== SPLUNK HEC CONFIGURATION =====================
# Use environment variables instead of hardcoding sensitive values.
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL", "http://splunk-service:8088")
SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN", "changeme-token")
SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "main")

class SplunkHECHandler(logging.Handler):
    def __init__(self, hec_url, token, index="main"):
        super().__init__()
        self.hec_url = hec_url.rstrip("/")
        self.token = token
        self.index = index
        self.headers = {
            "Authorization": f"Splunk {self.token}",
            "Content-Type": "application/json"
        }

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "event": log_entry,
            "sourcetype": "movie_recommender_app",
            "index": self.index
        }
        try:
            # Use HTTP and verify=False only for dev/test (self-signed certs)
            requests.post(
                f"{self.hec_url}/services/collector",
                headers=self.headers,
                data=json.dumps(payload),
                verify=False,
                timeout=5
            )
        except Exception as e:
            print("⚠️ Failed to send log to Splunk:", e)

# ===================== LOGGER INITIALIZATION =====================
if "logger" not in st.session_state:
    logger = logging.getLogger("MovieRecommenderLogger")
    logger.setLevel(logging.INFO)

    if not any(isinstance(h, SplunkHECHandler) for h in logger.handlers):
        handler = SplunkHECHandler(SPLUNK_HEC_URL, SPLUNK_TOKEN, SPLUNK_INDEX)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    st.session_state.logger = logger
else:
    logger = st.session_state.logger

# ===================== LOAD DATA =====================
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)
    similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarity_matrix

movies, similarity = load_data()

# ===================== APP LOGIC =====================
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
        logger.info(f"✅ Recommendations generated for '{movie}': {recommended_movies}")
        return recommended_movies
    except Exception as e:
        logger.error(f"❌ Error generating recommendations for {movie}: {str(e)}")
        return ["Error occurred while fetching recommendations."]

# ===================== STREAMLIT UI =====================
st.title("🎬 Movie Recommender System with Splunk Logging")

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations = recommend(selected_movie_name)
    for movie in recommendations:
        st.write(movie)
