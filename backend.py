from flask import Flask, request, jsonify, send_file
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

from bs4 import BeautifulSoup
import requests
import json
import csv
import os

@app.route('/scrape', methods=['POST'])
def scrape_google():
    data = request.get_json()
    keyword = data.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = f"https://www.google.com/search?q={keyword}&num=10"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch results from Google"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3').text if g.find('h3') else 'No title'
        link = g.find('a')['href'] if g.find('a') else 'No link'
        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else 'No snippet'
        results.append({
            'title': title,
            'link': link,
            'snippet': snippet
        })


file_path = 'results.csv'
with open(file_path, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Link', 'Snippet'])  # Hlavička CSV
    for result in results:
        writer.writerow([result['title'], result['link'], result['snippet']])
    
    
    import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    app.run(debug=True)

@app.route('/', methods=['GET'])
def home():
    return "Vítej na Google Scraper API. Use the /scrape endpoint to get results."
