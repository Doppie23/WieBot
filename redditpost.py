import praw
import os
from dotenv import load_dotenv
load_dotenv()

id = os.getenv('CLIENT_ID')
secret = os.getenv('REDDIT_CLIENT_SECRET')

def randomcopypasta():  
    r = praw.Reddit(client_id=id,
                    client_secret=secret,
                    user_agent='/u/Doppie, testing PRAW')  
    posts = r.subreddit('copypasta').random()
    # print(posts.selftext)
    copypasta = posts.selftext
    user = str(posts.author)
    bericht = copypasta + '\n' + '~/u/' + user

    return bericht

def randomshitpost():
    r = praw.Reddit(client_id=id,
                    client_secret=secret,
                    user_agent='/u/Doppie, testing PRAW') 
    posts = r.subreddit('shitposting').random()
    shitposturl = posts.url
    return shitposturl