# TODO: Change this back to top 20 news articles later
# get me the top 3 news from google search for the current date and for the United States.
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import anthropic
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from pathlib import Path
import random
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
# This is the location in PythonAnywhere; remove it for local testing
load_dotenv('/home/tudo/.env')

# Initialize the Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")

def get_google_sheets_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def get_top_google_news():
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code != 200:
            print(f"Error: Unable to fetch news. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'xml')
        news_items = soup.find_all('item')

        news = []
        for item in news_items:
            title = item.title.text
            link = item.link.text
            description = item.description.text if item.description else ""
            if not is_political_news(title, description):
                news.append({"title": title, "link": link})
            if len(news) == 10:  # TODO: Change this back to 20 later
                break

        return news
    except requests.RequestException as e:
        print(f"Error: Unable to fetch news. {str(e)}")
        return None

def is_political_news(title, text):
    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            temperature=0,
            system="You are an AI assistant that determines if a news article is political or not. Respond with only 'True' for political news or 'False' for non-political news.",
            messages=[
                {"role": "user", "content": f"Is this news article political? Title: '{title}'\n\nText: {text}"}
            ]
        )
        return response.content[0].text.strip().lower() == 'true'
    except Exception:
        return False  # Default to non-political if classification fails

def get_original_url(google_news_url):
    try:
        response = requests.get(google_news_url, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Error getting original URL: {e}")
        return None

def summarize_article(title, link):
    try:
        original_url = get_original_url(link)
        if not original_url:
            return "Unable to get original URL.", "#News", "", "", ""

        response = requests.get(original_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        article_text = soup.get_text()

        summary_prompt = f"Summarize the following news article in five parts: 1) A brief 5-minute read summary. 2) A relevant hashtag for the article. 3) Educational content related to key terms or concepts in the summary (2-3 paragraphs max). 4) Short summaries of any places, person names, company names, brand names, business names, sports club names, food names, device names, tool names, country names, region names, or geographical feature names mentioned in the summary. 5) A short phrase or a few keywords (1-5 words) that capture the main topic or focus of the article, suitable for a YouTube search. Separate the five parts with '|||'. Title: {title}\n\nArticle content: {article_text[:2000]}..."

        summary_response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            system="You are an AI assistant that summarizes news articles concisely, provides educational context, gives short summaries of important names or entities mentioned, and creates a short phrase or keywords for YouTube search. Always provide five parts in your response, separated by '|||'. Do not include any labels or numbering for the parts.",
            messages=[
                {"role": "user", "content": summary_prompt}
            ]
        )
        parts = summary_response.content[0].text.strip().split('|||')
        if len(parts) != 5:
            print(f"Warning: Expected 5 parts in the summary, but got {len(parts)}. Adjusting...")
            while len(parts) < 5:
                parts.append("N/A")
            parts = parts[:5]
        full_summary, hashtag, educational_content, entity_summaries, youtube_search_phrase = parts

        # Check if youtube_search_phrase is N/A and try to generate one if it is
        if youtube_search_phrase.strip() == "N/A":
            print("YouTube search phrase is N/A. Attempting to generate one...")
            youtube_search_prompt = f"Create a short phrase or a few keywords (1-5 words) that capture the main topic or focus of this article, suitable for a YouTube search. Title: {title}\n\nSummary: {full_summary}"
            youtube_search_response = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=20,
                temperature=0.7,
                system="You are an AI assistant that creates short, relevant phrases or keywords for YouTube searches based on news articles. Provide only the search phrase or keywords without any additional text.",
                messages=[
                    {"role": "user", "content": youtube_search_prompt}
                ]
            )
            youtube_search_phrase = youtube_search_response.content[0].text.strip()

        return full_summary.strip(), hashtag.strip(), educational_content.strip(), entity_summaries.strip(), youtube_search_phrase.strip()
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return "Unable to generate summary.", "#News", "", "", ""

def search_youtube_video(youtube_search_phrase):
    if youtube_search_phrase == "N/A":
        print("YouTube search phrase is N/A. Skipping YouTube search.")
        return None, None, None

    try:
        search_response = youtube.search().list(
            q=youtube_search_phrase,
            type='video',
            part='id,snippet',
            maxResults=1
        ).execute()

        if search_response['items']:
            video = search_response['items'][0]
            video_id = video['id']['videoId']
            video_title = video['snippet']['title']
            video_description = video['snippet']['description']
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            return video_link, video_title, video_description
        else:
            print("No relevant YouTube videos found.")
            return None, None, None
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return None, None, None

def create_blog_post(title, full_summary, hashtag, educational_content, entity_summaries, youtube_search_phrase, video_link):
    blog_post_prompt = f"""
    Create a compelling, engaging, educational, informational, fun, and catchy blog post using the following components:

    Title: {title}
    Summary: {full_summary}
    Hashtag: {hashtag}
    Educational Content: {educational_content}
    Entity Summaries: {entity_summaries}
    YouTube Search Phrase: {youtube_search_phrase}
    Video Link: {video_link}

    The blog post should:

    1. Start with a Hook: Capture the attention of the reader right from the start with a compelling introduction. Use strong, captivating language—whether it's a surprising fact, a powerful statistic, or a thought-provoking question—to immediately draw them in. Consider adding relevant data or a shocking trend to strengthen the hook.

    2. Seamless Integration of Summary and Educational Content: The content should flow smoothly, combining a concise news summary with relevant educational insights. Transition between factual reporting and analysis naturally. Include historical context, industry data, or expert analysis where necessary to enhance understanding and keep the reader engaged.

    3. Keep it Readable: Break complex ideas into short paragraphs or bullet points. This improves readability and ensures the content is easy to digest. Include infographics, charts, emojis, or visual aids where appropriate to break down complex data points. Avoid overwhelming readers with large blocks of text.

    4. Highlight the Significance: Focus on why the news matters. Rather than simply listing facts, explain how the story impacts daily life, society, or the future. Highlight related trends, industry implications, or geographical impact to clarify why this information is exciting or important.

    5. Provide Context: Help readers understand the bigger picture by offering background information. Frame the news within a broader narrative so the audience can appreciate the full scope of the issue. Include comparative case studies, previous developments, or related articles to provide depth and clarity.

    6. Make it Relatable: Use analogies or comparisons to help readers connect with the topic. Relating the news to something familiar makes it easier to grasp. For example, compare a financial crisis to a well-known event or explain technological changes by drawing parallels to everyday experiences.

    7. Incorporate Key Quotes: Include emotional or provocative quotes from the article to humanize the story and add authenticity. Where possible, supplement with expert opinions or social media reactions to bring diverse perspectives into the conversation.

    8. Use Vivid Language: Avoid dry or overly factual language. Instead, use descriptive and dynamic wording to paint a mental picture for the reader. Opt for active voice and strong verbs to bring the story to life. Use storytelling techniques to make complex subjects more engaging.

    9. Add Video Links: Include a video link with a brief description of its importance or relevance to the story. Use multimedia to provide additional context or visual representation. For example, embed news clips, interviews, or explainer videos related to the topic.

    10. Encourage Thought and Action: Ask questions that encourage the reader to think critically or imagine future possibilities. Highlight potential implications or future developments and end with a call to action or thought-provoking statement. Use interactive elements like polls, quizzes, or social media hashtags to prompt reader engagement.

    11. Maintain Flow: Ensure the post maintains a smooth, continuous flow from beginning to end. Avoid abrupt transitions or sections that might break the reader's engagement. Balance narrative structure with clear, concise points to keep the reader interested throughout.

    12. Be Factual: Stay entirely factual throughout the post. Avoid embellishment or adding fictional elements. Accuracy should be prioritized while maintaining an engaging tone. Where necessary, provide links to relevant reports, legal documents, or research papers to substantiate claims.

    The tone should be conversational yet informative, striking a balance that resonates with a wide audience. Be approachable while delivering clear, factual insights.
    Provide the blog post without any additional text.
    """

    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0.7,
            system="You are an AI assistant that creates engaging and informative blog posts based on news articles and related information. Provide the blog post without any additional text.",
            messages=[
                {"role": "user", "content": blog_post_prompt}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error creating blog post: {e}")
        return "Unable to generate blog post."

def rewrite_title(title):
    try:
        new_title_prompt = f"Rewrite the following news title without citing any source, making it catchy and engaging. Provide only the rewritten title without any additional text: '{title}'"
        new_title_response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            temperature=0.7,
            system="You are an AI assistant that rewrites news titles to be catchy and engaging without citing any source. Provide only the rewritten title without any additional text.",
            messages=[
                {"role": "user", "content": new_title_prompt}
            ]
        )
        return new_title_response.content[0].text.strip()
    except Exception as e:
        print(f"Error rewriting title: {e}")
        return title  # Return original title if rewriting fails

def get_top_news():
    news = get_top_google_news()

    if not news:
        print("No news articles found from Google News.")
        return

    sheets_service = get_google_sheets_service()

    for i, article in enumerate(news, 1):
        original_title = article['title']
        link = article['link']

        # Summarize the article with the original title
        full_summary, hashtag, educational_content, entity_summaries, youtube_search_phrase = summarize_article(original_title, link)

        # Rewrite the title for the blog post
        new_title = rewrite_title(original_title)

        # Search for a related YouTube video based on the YouTube search phrase
        video_link, video_title, video_description = search_youtube_video(youtube_search_phrase)

        # Create the blog post
        blog_post = create_blog_post(new_title, full_summary, hashtag, educational_content, entity_summaries, youtube_search_phrase, video_link)

        # Prepare the data for Google Sheets
        row_data = [
            new_title,
            blog_post,
            hashtag,
            youtube_search_phrase if youtube_search_phrase else "",
            video_link if video_link else "No video found"
        ]

        # Append the data to the Google Sheet
        range_name = f'Sheet1!A{i}:E{i}'
        body = {
            'values': [row_data]
        }
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()
        # print(f"Data appended to {current_date}!A{i}:D{i}")
        print(f"Data appended to Sheet1!A{i}:E{i}")


# def detect_ai_content(text):
#     try:
#         response = openai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an AI content detector. Analyze the given text and estimate the likelihood it was generated by AI. Respond with only a percentage between 0 and 100, without any additional text."},
#                 {"role": "user", "content": f"Analyze this text and estimate the likelihood it was generated by AI:\n\n{text}"}
#             ],
#             max_tokens=10,
#             temperature=0
#         )
#         likelihood = float(response.choices[0].message.content.strip())
#         return likelihood
#     except Exception as e:
#         print(f"Error detecting AI content: {e}")
#         return 0  # Assume human-generated if detection fails

# def humanize_content(text):
#     try:
#         response = anthropic_client.messages.create(
#             model="claude-3-sonnet-20240229",
#             max_tokens=1500,
#             temperature=0.7,
#             system="You are an AI assistant that rewrites content to sound more human-like. Maintain all factual information and do not add any fictional elements. Focus on varying sentence structure, using more natural language, and incorporating conversational elements.",
#             messages=[
#                 {"role": "user", "content": f"Rewrite the following content to sound more human-generated, without changing any facts or adding fictional elements:\n\n{text}"}
#             ]
#         )
#         return response.content[0].text.strip()
#     except Exception as e:
#         print(f"Error humanizing content: {e}")
#         return text  # Return original text if humanization fails

if __name__ == "__main__":
    get_top_news()
