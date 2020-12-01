# -*- coding: utf-8 -*-

import io
import json
import logging
import os
import sys
from datetime import datetime
from dateutil import tz

from tweepy import Stream, StreamListener

from mytwitter.tweepy.utils import get_fulltext
from .base import Client

logger = logging.getLogger(__name__)

class MyStreamListener(StreamListener):
    """Override tweepy.StreamListener to add logic to on_status.
    """
    
    def __init__(self, out_path, prefix_fname, out_maxsize, count, verbose, output):
        
        super().__init__()

        self._out_path = out_path
        if prefix_fname:
            self._prefix_fname = prefix_fname if prefix_fname.endswith('_') else prefix_fname + '_'
        else:
            self._prefix_fname = ''
        self._out_maxsize = out_maxsize
        self._count = count
        self._verbose = verbose

        self.__f = io.StringIO()
        self.__s3_client = output['s3_client'] if output else None
        self.__bucket_name = output['bucket_name'] if output else None
    
    def on_status(self, status):
        
        if self._count == 0 or self._count < -1:
            if self._count < -1:
                logger.critical(f"count = {self._count}")
            return False
                
        try:
            decoded = status._json
            data = json.dumps(decoded)

            bytes_file = sys.getsizeof(self.__f.getvalue()) - sys.getsizeof("")
            bytes_data = sys.getsizeof(data) - sys.getsizeof("")
            if bytes_file + bytes_data >= self._out_maxsize:
                now = datetime.now().replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
                year, month, day = now.strftime('%Y'), now.strftime('%m'), now.strftime('%d')
                out_file = f"{self._out_path}/year={year}/month={month}/day={day}/{self._prefix_fname}{str(now).replace(':', '-').replace(' ', '_')}.json"
                if self.__s3_client:
                    self.__s3_client.put_object(self.__f.getvalue() + '\n', self.__bucket_name, out_file)
                    logger.info(f"The next file has been written: {self.__bucket_name}/{out_file}")
                else:
                    if not os.path.exists(os.path.dirname(out_file)):
                        os.makedirs(os.path.dirname(out_file))
                    with io.open(out_file, 'at', encoding='utf-8') as f:
                        f.write(self.__f.getvalue() + '\n')
                    logger.info(f"The next file has been written: {out_file}")
                self.__f.close()
                self.__f = io.StringIO()
            self.__f.write(data + '\n')

            if int(datetime.now().strftime('%M')) % 15 == 0 and int(datetime.now().strftime('%S')) in [0,1,2,3,4,5]:
                logger.info(f"{bytes_file} Bytes buffered")
            if self._verbose:
                logger.info(f"{bytes_file} Bytes buffered")
                logger.info(f"{decoded['created_at']}\n{get_fulltext(decoded)}\n{'='*10}")

            if self._count != -1:
                self._count -= 1

        except Exception as e:
            logger.error(f"{e}")
        finally:
            return True
            
    def on_error(self, status_code):
        
        logger.error(f"status_code {status_code}")
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False
        # returning non-False reconnects the stream, with backoff.
        
    def on_timeout(self):
        
        logger.error("TIMEOUT")
        
class Streaming(Client):
    
    def __init__(self, out_path, prefix_fname=None,
        follow=None, track=None, is_async=False, locations=None, languages=None,
        out_maxsize=2*(1024**3), count=-1, verbose=False,
        output=None):
        
        super().__init__()

        self._follow = follow
        self._track = track
        self._is_async = is_async
        self._locations = locations
        self._languages = languages
        self._my_stream_listener = MyStreamListener(
            out_path, prefix_fname,
            out_maxsize, count, verbose,
            output)
    
    def start(self):
        """https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
        """
        
        self._my_stream = Stream(auth=self.get_api().auth, listener=self._my_stream_listener)
        self._my_stream.filter(follow=self._follow, track=self._track, is_async=self._is_async, locations=self._locations, languages=self._languages)
