import os
import json
import traceback
import praw
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

def fetch_trends(n=20):
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            read_only=True
        )
        hot_posts = reddit.subreddit("popular").hot(limit=n)
        trends = [post.title for post in hot_posts]
        return trends, None

    except Exception as e:
        print("🔥 Error in fetch_trends:", e)
        traceback.print_exc()
        return None, str(e)

SYSTEM_PROMPT = """
You are an expert social media content strategist and a creative idea generator for a content creator.
Your goal is to blend current, high-traffic national trends with the creator's specific niche to generate engaging, relevant, and original short video ideas.

For EACH trend in the list provided, you MUST return one object with these exact fields:
- original_trend: the original trend title (string)
- is_relevant: true if the trend can be connected to the creator's niche, false otherwise (boolean)
- relevance_score: integer from 0 to 100
- reason: why it is or is not relevant (string)
- blended_topic_idea: a compelling video topic that merges the trend with the creator's niche (string)
- short_video_hook: an attention-grabbing opening line or question for the video (string)
- content_angle: a 2-3 sentence description of how the video should be structured and what angle to take (string)
- suggested_format: one of Tutorial, Commentary, Skit, Vlog, Reaction, Listicle, Interview (string)

Return a JSON object with a single key "content_suggestions" containing an array of these objects.
"""

def get_blended_ideas(creator_info, trends, api_key):
    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        creator_str = json.dumps(creator_info, indent=2)
        trends_str = "\n".join(f"- {t}" for t in trends)

        user_prompt = f"""
Creator profile:
{creator_str}

Top national trends to analyse:
{trends_str}

Return ONLY a valid JSON object with key "content_suggestions" — an array with one entry per trend above.
Each entry must include: original_trend, is_relevant, relevance_score, reason, blended_topic_idea, short_video_hook, content_angle, suggested_format.
"""

        response = model.generate_content(
            user_prompt,
            generation_config=GenerationConfig(
                response_mime_type="application/json"
            )
        )

        raw = response.text.strip()
        print("✅ Raw Gemini response (first 300 chars):", raw[:300])

        parsed = json.loads(raw)

        # Normalise: handle cases where Gemini wraps differently
        if isinstance(parsed, list):
            return {"content_suggestions": parsed}
        if "content_suggestions" not in parsed:
            # Try to find any key that holds a list
            for v in parsed.values():
                if isinstance(v, list):
                    return {"content_suggestions": v}
            return {"error": "Unexpected response shape from AI", "raw": raw[:500]}

        return parsed

    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        traceback.print_exc()
        return {"error": "Failed to generate ideas. Please check server logs."}
