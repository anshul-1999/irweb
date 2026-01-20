import os
from flask import Flask, render_template, request, redirect, url_for
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer

app = Flask(__name__)

# 1. Configuration
INDEX_DIR = "indexdir"  # Where search data is stored

# 2. Define Schema (Title, Content, and URL)
# StemmingAnalyzer helps match "running" with "run"
schema = Schema(
    title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    url=ID(stored=True)
)

# 3. Create or Open the Index
if not os.path.exists(INDEX_DIR):
    os.mkdir(INDEX_DIR)
    ix = create_in(INDEX_DIR, schema)
else:
    ix = open_dir(INDEX_DIR)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query_str = request.args.get('q', '')
    results_data = []
    
    if query_str:
        ix = open_dir(INDEX_DIR)
        with ix.searcher() as searcher:
            # Search in both title and content
            query = QueryParser("content", ix.schema).parse(query_str)
            results = searcher.search(query, limit=10)
            
            for r in results:
                results_data.append({
                    'title': r['title'],
                    'url': r['url'],
                    'score': round(r.score, 2),
                    'snippet': r.highlights("content") # Generates a preview snippet
                })

    return render_template('results.html', results=results_data, query=query_str)

@app.route('/add', methods=['GET', 'POST'])
def add_page():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        content = request.form['content']

        # Add data to the Whoosh index
        ix = open_dir(INDEX_DIR)
        writer = ix.writer()
        writer.add_document(title=title, url=url, content=content)
        writer.commit()
        
        return redirect(url_for('index'))
    
    return render_template('add_page.html')

if __name__ == '__main__':
    app.run(debug=True)