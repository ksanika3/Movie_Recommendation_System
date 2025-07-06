import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import os
import ast
import pickle

class TMDbRecommender:
    def __init__(self):
        self.movies_df = None
        self.credits_df = None
        self.tfidf_matrix = None
        self.indices = None
        self.tfidf = None
        self.model_path = os.path.join('data', 'recommender_model.pkl')

    def load_data(self):
        try:
            self.movies_df = pd.read_csv(os.path.join('data', 'tmdb_5000_movies.csv'))
            self.credits_df = pd.read_csv(os.path.join('data', 'tmdb_5000_credits.csv'))
            self._prepare_data()
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def _prepare_data(self):
        
        self.credits_df.rename(columns={'movie_id': 'id'}, inplace=True)
        self.movies_df = pd.merge(self.movies_df, self.credits_df, on=['id', 'title'])
        
        for col in ['overview', 'genres', 'keywords', 'cast', 'crew']:
            if col in self.movies_df.columns:
                self.movies_df[col] = self.movies_df[col].fillna('[]' if col != 'overview' else '')
       
        self.movies_df['combined_features'] = self.movies_df.apply(self._combine_features, axis=1)
        
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.movies_df['combined_features'])
        self.indices = pd.Series(self.movies_df.index, index=self.movies_df['title']).drop_duplicates()

    def _combine_features(self, row):
        def safe_eval(val):
            try:
                return ast.literal_eval(val) if isinstance(val, str) else []
            except:
                return []
        genres = ' '.join([g['name'] for g in safe_eval(row['genres'])]) if 'genres' in row else ''
        keywords = ' '.join([k['name'] for k in safe_eval(row['keywords'])]) if 'keywords' in row else ''
        cast = ' '.join([c['name'] for c in safe_eval(row['cast'])[:3]]) if 'cast' in row else ''
        crew = ' '.join([c['name'] for c in safe_eval(row['crew']) if c.get('job') == 'Director']) if 'crew' in row else ''
        overview = row['overview'] if 'overview' in row else ''
        return f"{genres} {keywords} {cast} {crew} {overview}"

    def save_model(self):
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'movies_df': self.movies_df,
                    'tfidf_matrix': self.tfidf_matrix,
                    'indices': self.indices,
                    'tfidf': self.tfidf
                }, f)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def load_model(self):
        if not os.path.exists(self.model_path):
            return False
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.movies_df = data['movies_df']
                self.tfidf_matrix = data['tfidf_matrix']
                self.indices = data['indices']
                self.tfidf = data['tfidf']
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def search_movies(self, query, n=10):
       
        results = self.movies_df[self.movies_df['title'].str.contains(query, case=False, na=False)]
        return results.head(n)

    def get_movie_details(self, movie_id):
        movie = self.movies_df[self.movies_df['id'] == movie_id]
        if not movie.empty:
            return movie.iloc[0].to_dict()
        return None

    def get_recommendations(self, title, n=10):
        if title not in self.indices:
            return pd.DataFrame()
        idx = self.indices[title]
        cosine_similarities = linear_kernel(self.tfidf_matrix[idx:idx+1], self.tfidf_matrix).flatten()
        similar_indices = cosine_similarities.argsort()[-n-1:-1][::-1]
        return self.movies_df.iloc[similar_indices][['id', 'title', 'genres', 'overview']]

    def get_popular_movies(self, n=10, genre=None):
        df = self.movies_df
        if genre:
            df = df[df['genres'].str.contains(genre, case=False, na=False)]
        return df.sort_values('popularity', ascending=False).head(n)[['id', 'title', 'genres', 'overview']]

    def get_genres(self):
        genres = set()
        for g_list in self.movies_df['genres']:
            try:
                genres.update([g['name'] for g in ast.literal_eval(g_list)])
            except:
                continue
        return sorted(list(genres)) 