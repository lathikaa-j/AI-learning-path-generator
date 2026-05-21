import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------------
# EXTRACT NUMBER OF DAYS
# -----------------------------------
def extract_days(goal):

    words = goal.lower().split()

    for i, word in enumerate(words):

        if word.isdigit():

            if i + 1 < len(words):

                next_word = words[i + 1]

                if "day" in next_word:
                    return int(word)

    return 5

# -----------------------------------
# GENERATE LEARNING PATH
# -----------------------------------
def generate_learning_path(goal):

    num_days = extract_days(goal)

    prompt = f"""
Create a {num_days}-day step-by-step learning roadmap for: {goal}

STRICT REQUIREMENTS:

- Return ONLY valid JSON
- Do NOT include markdown
- Do NOT use ```json
- Do NOT add explanations outside JSON
- Generate EXACTLY {num_days} days

Each day must contain:
1. topic
2. focus
3. minimum 4 learning steps
4. one practice task
5. one mini project
6. one youtube search query

JSON FORMAT:

{{
  "roadmap": "short roadmap overview",
  "days": [
    {{
      "day": 1,
      "topic": "Topic Name",
      "focus": "What user learns",
      "steps": [
        "Step 1",
        "Step 2",
        "Step 3",
        "Step 4"
      ],
      "practice": "Practice task",
      "project": "Mini project",
      "youtube_query": "YouTube search query"
    }}
  ]
}}
"""

    try:

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert roadmap generator. "
                        "Return ONLY valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        content = completion.choices[0].message.content.strip()

        print("\nRAW RESPONSE:\n")
        print(content)

        # REMOVE MARKDOWN
        if content.startswith("```"):

            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # FIND JSON
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            return {
                "error": "No valid JSON returned"
            }

        content = content[start:end]

        data = json.loads(content)

        return data

    except Exception as e:

        print("JSON ERROR:", str(e))

        return {
            "error": f"Failed to generate roadmap\n\n{str(e)}"
        }

# -----------------------------------
# YOUTUBE SEARCH
# -----------------------------------
def get_youtube_videos(query):

    try:

        url = "https://www.googleapis.com/youtube/v3/search"

        params = {
            "part": "snippet",
            "q": query,
            "key": YOUTUBE_API_KEY,
            "maxResults": 5,
            "type": "video"
        }

        response = requests.get(
            url,
            params=params
        )

        print("YOUTUBE STATUS:", response.status_code)
        print("YOUTUBE RESPONSE:", response.text)

        data = response.json()

        videos = []

        if "items" in data:

            for item in data["items"]:

                title = item["snippet"]["title"]

                video_id = item["id"]["videoId"]

                video_url = (
                    f"https://youtube.com/watch?v={video_id}"
                )

                videos.append({
                    "title": title,
                    "url": video_url
                })

        return {
            "videos": videos
        }

    except Exception as e:

        return {
            "videos": [],
            "error": str(e)
        }

# -----------------------------------
# SAVE TO NOTION
# -----------------------------------
def send_to_notion(title, content):

    if not NOTION_TOKEN or not NOTION_DATABASE_ID:

        return {
            "error": "Missing Notion credentials"
        }

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {
            "database_id": NOTION_DATABASE_ID
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Content": {
                "rich_text": [
                    {
                        "text": {
                            "content": content[:2000]
                        }
                    }
                ]
            }
        }
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        print("NOTION STATUS:", response.status_code)
        print("NOTION RESPONSE:", response.text)

        if response.status_code in [200, 201]:

            return {
                "success": True
            }

        return {
            "error": response.text
        }

    except Exception as e:

        return {
            "error": str(e)
        }