from flask import Flask, request, jsonify, send_file
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

from bs4 import BeautifulSoup
import requests
import csv
import json
import os

@app.route('/', methods=['GET'])
def home():
    return "Vítej, tohle je pokus o vyhledávání přes google."

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
        
        # Načtení meta popisku ze samotné stránky
        try:
            page_response = requests.get(link, headers=headers, timeout=5)
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            meta_tag = page_soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_tag['content'] if meta_tag else 'No meta description'
        except Exception as e:
            meta_description = 'Failed to fetch meta description'

        results.append({
            'title': title,
            'link': link,
            'meta_description': meta_description
        })
    
    # Vytvoření CSV souboru
    file_path = 'results.csv'
    with open(file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Link', 'Meta Description'])
        for result in results:
            writer.writerow([result['title'], result['link'], result['meta_description']])

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

