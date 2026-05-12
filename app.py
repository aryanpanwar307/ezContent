from flask import Flask, jsonify, request, render_template
from generator import fetch_trends, get_blended_ideas
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
load_dotenv()
# Load Gemini API key from env and clean it
raw_key = os.getenv("API_KEY", "")
API_KEY = raw_key.strip().replace('"', '').replace("'", "")

if not API_KEY:
    print("⚠️ WARNING: API_KEY not found in .env file!")

@app.route("/")
def home():
    return render_template("sampleContentHelper.html")

@app.route("/generate", methods=["POST"])
def generate_content():
    try:
        data = request.get_json(force=True)
        creator_info = data["creator"]
        n = data.get("n",20)

        trends, err = fetch_trends(n)
        if err:
            print("❌ fetch_trends failed:", err)
            return jsonify({"error": err}), 500

        if not trends:
            return jsonify({"error": "No trends found"}), 404

        ideas = get_blended_ideas(creator_info, trends, API_KEY)
        return jsonify({
            "trends": trends,
            "results": ideas
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
