# -*- coding: utf-8 -*-

def get_fulltext(decoded, user_api=False):
    
    if user_api:
        return decoded["full_text"]
    else:
        if "retweeted_status" in decoded and "extended_tweet" in decoded["retweeted_status"]:
            return decoded["retweeted_status"]["extended_tweet"]["full_text"]
        elif "extended_tweet" in decoded:
            return decoded["extended_tweet"]["full_text"]
        else:
            return decoded["text"]
            