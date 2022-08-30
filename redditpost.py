import praw
import random
import os

def randomcopypasta():  
    r = praw.Reddit('bot1', user_agent='/u/Doppie, testing PRAW')  
    posts = r.subreddit('copypasta').random()
    # print(posts.selftext)
    copypasta = posts.selftext
    user = str(posts.author)
    bericht = copypasta + '\n' + '~/u/' + user
    return bericht
