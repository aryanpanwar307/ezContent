import requests
import json
import time
from pytrends.request import TrendReq

creator_default = {
    "genre": "Technology",
    "sub_genre": "Software Development, AI tools, Interview Preparation, Resource(Github repositories, Free tools, Websites, Youtube channels/Videos)",
    "audience": "Young professionals, students",
    "location": "India",
    "language": "English"
}

def fetch_trends(n=5):
    try:
        url = "https://www.reddit.com/r/popular.json?limit=20"
        headers = {"User-Agent": "TrendFetcher/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        posts = data["data"]["children"]
        return [post["data"]["title"] for post in posts[:n]]
    except Exception as e:
        print(f"⚠️ Error fetching trends: {e}")
        return []

SYSTEM_PROMPT = """
You are an expert social media content strategist and a creative idea generator for a tech creator.
Your goal is to blend current, high-traffic national trends with the creator's specific niche to generate engaging, relevant, and original short video ideas.
...
"""

JSON_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "content_suggestions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "original_trend": {"type": "STRING"},
                    "is_relevant": {"type": "BOOLEAN"},
                    "relevance_score": {"type": "INTEGER"},
                    "reason": {"type": "STRING"},
                    "blended_topic_idea": {"type": "STRING"},
                    "short_video_hook": {"type": "STRING"},
                    "content_angle": {"type": "STRING"},
                    "suggested_format": {"type": "STRING"}
                },
                "required": ["original_trend", "is_relevant", "relevance_score"]
            }
        }
    },
    "required": ["content_suggestions"]
}

def create_user_prompt(creator_info, trend_list):
    creator_str = json.dumps(creator_info, indent=2)
    trends_str = "\n".join(f"- {t}" for t in trend_list)
    return f"""
    Here is the creator profile:
    {creator_str}

    Here are the top national trends:
    {trends_str}

    Please generate the blended content ideas based on your system instructions.
    """

def get_blended_ideas(creator_info, trends, api_key):
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"
    user_prompt = create_user_prompt(creator_info, trends)
    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": JSON_SCHEMA
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = None
    try:
        for attempt in range(3):
            try:
                response = requests.post(apiUrl, headers=headers, data=json.dumps(payload), timeout=60)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise
        
        result = response.json()
        json_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(json_text)

    except Exception as e:
        print(f"API call failed: {e}")
        if response:
            print(response.text)
        return {"error": str(e)}
