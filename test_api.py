from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

# We explicitly tell Flask to look for the 'templates' folder
app = Flask(__name__, template_folder='templates')
CORS(app)

# THE PATTERN: Using verified Jamendo tags for 100% success rate
MOOD_MAP = {
    "red": "rock",
    "yellow": "happy",
    "blue": "chillout",
    "purple": "dark",
    "green": "acoustic"
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_vibe', methods=['GET'])
def get_vibe():
    color = request.args.get('color', 'red').lower()
    tag = MOOD_MAP.get(color, "rock")
    
    # Using 'fuzzytags' and 'boost' to ensure we always get popular results
    params = {
        "client_id": "709fa152", 
        "format": "json",
        "limit": 5,
        "fuzzytags": tag,
        "boost": "popularity_month"
    }
    
    try:
        r = requests.get("https://api.jamendo.com/v3.0/tracks/", params=params)
        data = r.json()
        return jsonify(data.get('results', []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Vibe Engine starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)