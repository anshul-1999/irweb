from flask import Flask, render_template, request
from search_engine import SocialMediaEngine
import os

app = Flask(__name__)

# To change datasets, comment the active block and uncomment the other

# CHOICE 1: AUTOMOBILES
#URL = "https://raw.githubusercontent.com/datacamp/Brand-Analysis-using-Social-Media-Data-in-R-Live-Training/master/data/tesladf.csv"
#COLS = ['text']
#DATE = 'created_at'

# CHOICE 2: ELECTRONICS (Gadget Reviews)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL = os.path.join(BASE_DIR, "data", "ElectronicsData.csv")
COLS = ["Title", "Feature", "Sub Category"]
DATE = "Price"

# CHOICE 3: AVIATION (Airline Customer Feedback)
# Use this to find trends in flight delays or service quality
#URL = "https://raw.githubusercontent.com/satyajeetkrjha/kaggle-Twitter-US-Airline-Sentiment-/master/Tweets.csv"
#COLS = ['text']
#DATE = 'tweet_created'

# Initialize the engine once when the app starts
engine = SocialMediaEngine(URL, COLS, DATE)

engine = SocialMediaEngine(URL, COLS, DATE)

@app.route('/', methods=['GET', 'POST'])
def home():
    query = request.form.get('user_input') or request.args.get('user_input', "")
    limit = request.args.get('limit', 5, type=int)

    results = []
    trends = {}
    precision_k = 0

    if query:
        results = engine.search(query, top_k=limit)
        trends = engine.get_trends(query)

        # Requirement: IR Evaluation (Precision@K)
        # In this lab, we define 'relevant' as having a similarity score > 0.05
        relevant_docs = [r for r in results if r['score'] > 0.05]
        precision_k = round(len(relevant_docs) / len(results), 2) if results else 0

    return render_template('index.html',
                           results=results,
                           trends=trends,
                           query=query,
                           current_limit=limit,
                           precision=precision_k)

if __name__ == '__main__':
    app.run(debug=True)