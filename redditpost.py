import praw
import random
import os

r = praw.Reddit('bot1', user_agent='/u/Doppie, testing PRAW')  
posts = r.subreddit('all').random()
print(posts.url)