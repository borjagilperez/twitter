# -*- coding: utf-8 -*-

import os

from tweepy import OAuthHandler, API

class Client:
    
    def __init__(self):
        
        consumer_key = os.environ['TWITTER_API_KEY']
        consumer_secret = os.environ['TWITTER_SECRET_KEY']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
            
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.__api = API(auth)

    def get_api(self):

        return self.__api
        