import os
import praw
import requests
import schedule
import time
import logging
from dotenv import load_dotenv
from groq import Groq


# Load environment variables
load_dotenv(dotenv_path='C:/Users/venka/Desktop/contentbot/keys.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Reddit API Authentication
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Constants
SUBREDDIT_NAME = os.getenv("SUBREDDIT_NAME")
POST_TIME = os.getenv("POST_TIME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def generate_content():
    try:
        # Initialize Groq 
        groq_client = Groq(api_key=GROQ_API_KEY)
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": "Create an insightful post with the title 'Manchester United'"
            }],
            model="llama-3.3-70b-versatile",  
        )
        
        content = chat_completion.choices[0].message.content
        logging.info("Successfully generated content.")
        return content
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return "Fallback content due to API error."


def generate_comment(post_title):
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Create a thoughtful comment for a post titled '{post_title}'"
            }],
            model="llama-3.3-70b-versatile",  
        )
        
        comment = chat_completion.choices[0].message.content
        logging.info("Successfully generated comment.")
        return comment
    except Exception as e:
        logging.error(f"Error generating comment: {e}")
        return "Fallback comment due to API error."

def post_to_reddit():
    content = generate_content()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    try:
        # Submit the post
        post = subreddit.submit(title="Manchester United", selftext=content)
        logging.info(f"Post submitted successfully to r/{SUBREDDIT_NAME}")

        # After posting the content, generate and post a comment
        comment_content = generate_comment("Manchester United")  # title of post is input
        post.reply(comment_content)  # Posting
        logging.info(f"Comment posted on r/{SUBREDDIT_NAME}")
    
    except Exception as e:
        logging.error(f"Error posting to Reddit: {e}")


# Scheduling for daily posting or whenever post is required
schedule.every().day.at(POST_TIME).do(post_to_reddit)

post_to_reddit()

