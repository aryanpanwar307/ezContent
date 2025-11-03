from flask import Flask, jsonify, request, render_template
from generator import fetch_trends, get_blended_ideas, creator_default
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
load_dotenv()
# Optional: load Gemini API key from env
API_KEY = os.getenv("API_KEY")

@app.route("/")
def home():
    return render_template("sampleContentHelper.html")

@app.route("/generate", methods=["POST"])
def generate_content():
    try:
        data = request.get_json(force=True)
        creator_info = data.get("creator", creator_default)
        n = data.get("n", 5)

        trends = fetch_trends(n)
        if not trends:
            return jsonify({"error": "No trends found"}), 500

        ideas = get_blended_ideas(creator_info, trends, API_KEY)
        return jsonify({
            "trends": trends,
            "results": ideas
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
