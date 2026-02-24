import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SocialMediaEngine:
    def __init__(self, data_url, text_cols, date_col):
        # Load the dataset while skipping messy lines (Expected fields error fix)
        # We use on_bad_lines='skip' for newer pandas or error_bad_lines=False for older
        try:
            self.df = pd.read_csv(data_url, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
            self.df = pd.read_csv(data_url, encoding='latin1', on_bad_lines='skip')
        except TypeError:
            self.df = pd.read_csv(data_url, encoding='latin1', error_bad_lines=False)

        self.text_cols = text_cols
        self.date_col = date_col

        # Preprocessing: Merge columns and fill missing values
        self.df['search_content'] = self.df[text_cols].fillna('').agg(' '.join, axis=1)

        # Indexing: TF-IDF with Stop-word removal (Requirement: Tokenization)
        self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['search_content'])

    def search(self, query, top_k=5):
        # Vector Space Model: Transform query to vector
        query_vec = self.vectorizer.transform([query])

        # Retrieval: Cosine Similarity
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Ranking: Get top K indices (Requirement: Ranked Results)
        top_indices = scores.argsort()[-top_k:][::-1]

        results = []
        for i in top_indices:
            content = self.df['search_content'].iloc[i]
            # Requirement: Short Snippet (taking first 200 chars)
            snippet = content[:200] + "..." if len(content) > 200 else content

            results.append({
                'content': snippet,
                'score': round(float(scores[i]), 3),
                'date_label': str(self.df[self.date_col].iloc[i])
            })
        return results

    def get_trends(self, query):
        mask = self.df['search_content'].str.contains(query, case=False, na=False)
        # Grouping logic for visualization
        trend_counts = self.df[mask].groupby(self.date_col).size().to_dict()
        return trend_counts