# MovieRecommendation – TMDb Movie Recommendation System (Streamlit)

A modern, visually appealing movie recommendation system built with **Streamlit** and powered by TMDb's comprehensive movie database. Discover your next favorite movie with personalized recommendations based on content-based filtering and an interactive, card-based UI.

## 🎬 Features

- **Modern Card-Based UI**: Responsive grid layout, colorful rating badges, hover effects, and expanders for movie details.
- **Robust Search**: Find movies by title with instant results.
- **Smart Recommendations**: Get similar movies based on content features (genres, cast, keywords).
- **Detailed Movie Info**: View cast, genres, ratings, overview, and more.
- **Graceful Fallbacks**: Handles missing posters and data with placeholders.
- **No Empty Cards**: Only displays as many cards as there are movies in a row.
- **One-Click Navigation**: Click a movie to see details and recommendations, with a "Back" button to return.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run streamlit_app.py
```

### 3. Access the Application
Open your browser to the local Streamlit URL (usually shown in the terminal, e.g. `http://localhost:8501`).

## 📊 Dataset

This system uses the TMDb (The Movie Database) dataset, included in the `data/` folder:
- **tmdb_5000_movies.csv**: Movie metadata
- **tmdb_5000_credits.csv**: Cast and crew info
- **recommender_model.pkl**: Precomputed model for fast recommendations

## 🏗️ Architecture

- **streamlit_app.py**: Main Streamlit app with UI, search, and recommendation logic
- **tmdb_recommender.py**: Content-based recommendation engine
- **data/**: Local dataset and model files

## 🎯 Key Features

- **Search Bar**: Quickly find movies by title
- **Movie Cards**: Show poster, title, rating, and expandable overview
- **Recommendations**: Click a movie to see similar movies
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Modern UI**: Custom CSS for a beautiful, Netflix-inspired look

## 🛠️ Technical Stack

- **Frontend/Backend**: Python, Streamlit
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: scikit-learn (TF-IDF, Cosine Similarity)
- **Styling**: Custom CSS injected via Streamlit

## 📈 Future Enhancements

- User authentication and personalized recommendations
- Collaborative filtering algorithms
- Advanced filtering and sorting options
- Movie watchlist functionality
- User ratings and reviews
- Social features and sharing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **TMDb**: For providing the comprehensive movie database
- **Streamlit**: For the interactive app framework
- **scikit-learn**: For machine learning utilities

---

**Enjoy discovering amazing movies with MovieRecommendation! 🎬✨** 