# -*- coding: utf-8 -*-

import argparse
import errno
import logging
import os
import signal
import shlex
import sys
from datetime import datetime, timedelta
from dateutil import tz

from botocore.client import Config

from mytwitter.cloud import S3Client
from mytwitter.tweepy import TweepyStreaming

def __parse_args(replace_argv=None):

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-l', '--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="categorization level in the log file entries")
    parent_parser.add_argument('-v', '--verbose', default=False, action='store_true', help="displays or gets extended information")
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    list_parser = subparsers.add_parser('streaming', parents=[parent_parser],
        help='''
            Tweepy Streaming.
            The following environment variables are required to interact with the Twitter API:
            TWITTER_API_KEY, TWITTER_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET.
            The following environment variables can be used to interact with AWS-S3 or DigitalOcean-Spaces:
            AWS_S3_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, [AWS_S3_REGION_NAME, AWS_S3_SIGNATURE_VERSION]
        ''')
    list_parser.add_argument('out_path')
    list_parser.add_argument('-p', '--prefix-fname')
    list_parser.add_argument('-f', '--follow', nargs='+')
    list_parser.add_argument('-t', '--track', nargs='+')
    list_parser.add_argument('-i', '--in-file-track')
    list_parser.add_argument('-a', '--is-async', default=False, action='store_true')
    list_parser.add_argument('-lo', '--locations', nargs='+')
    list_parser.add_argument('-la', '--languages', nargs='+', help="https://developer.twitter.com/en/docs/developer-utilities/supported-languages/api-reference/get-help-languages")
    list_parser.add_argument('-s', '--out-maxsize', type=int, default=2*(1024**3), help="maximum bytes to write in each file")
    list_parser.add_argument('-c', '--count', type=int, default=-1, help="number of tweets to ingest")
    group_parser = list_parser.add_mutually_exclusive_group()
    group_parser.add_argument('-d', '--date-to', help="YYYY-mm-dd HH:MM:SS")
    group_parser.add_argument('-de', '--delta-to', nargs=4, metavar=('DAYS', 'HOURS', 'MINUTES', 'SECONDS'))
    list_parser.add_argument('-fz', '--from-zone', default='Europe/Madrid', help="(default: 'Europe/Madrid')")
    
    if replace_argv:
        if len(replace_argv) == 0:
            parser.print_help(sys.stderr)
            sys.exit(errno.EAGAIN)
        else:
            args = parser.parse_args(replace_argv)
    else:
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(errno.EAGAIN)
        else:
            args = parser.parse_args()
    return args

def read_track(in_file):
    
    tracks = []
    with open(in_file, 'rt') as f:
        for line in f:
            try:
                track = line[: line.index('#')].strip()
            except:
                track = line.strip()
            if track:
                tracks.append(track)
    return tracks

def main(replace_args=None):

    if replace_args:
        replace_argv = shlex.split(replace_args)
        args = __parse_args(replace_argv)
    else:
        args = __parse_args()
    #kwargs = vars(args)

    logging.basicConfig(level=args.log_level, format='%(asctime)s:::%(levelname)s:::%(name)s:::%(module)s:::%(funcName)s:::%(message)s')
    logger = logging.getLogger()
    logger.info(args)

    def __sigint_handler(signum, frame):

        def __yes_or_no(question):
            
            while True:
                reply = input(f"\n{question} [Y/n] ").strip().lower()
                print(reply)
                if not reply:
                    return 'y'
                elif reply in ['y', 'n']:
                    return reply
            
        signal.signal(signal.SIGINT, original_sigint_handler)
        
        try:
            reply = __yes_or_no("Proceed?")
            if reply == 'y':
                logger.info("sigint_handler: answered yes")
                if args.date_to or args.delta_to:
                    signal.signal(signal.SIGALRM, original_sigalrm_handler)
                os._exit(os.EX_OK)
        except KeyboardInterrupt:
            logger.info(f"sigint_handler, two CTRL+C catched")
            if args.date_to or args.delta_to:
                signal.signal(signal.SIGALRM, original_sigalrm_handler)
            os._exit(os.EX_OK)
            
        signal.signal(signal.SIGINT, __sigint_handler) # restore the exit gracefully handler

    def __sigalrm_handler(signum, frame):

        signal.signal(signal.SIGALRM, original_sigalrm_handler)
        signal.signal(signal.SIGINT, original_sigint_handler)

        logger.info("sigalrm_handler")
        os._exit(os.EX_OK)

    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, __sigint_handler)

    original_sigalrm_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, __sigalrm_handler)

    if args.subparser == 'streaming':
        track = (args.track if args.track else []) + (read_track(args.in_file_track) if args.in_file_track else [])
        track = track if track else None
        logger.info(f"track list = {track}")

        if args.date_to or args.delta_to:
            if args.date_to:
                date_to = datetime.strptime(args.date_to, '%Y-%m-%d %H:%M:%S')
                date_to = date_to.replace(tzinfo=tz.gettz(args.from_zone)).astimezone(tz.tzutc())
                delta_to = date_to - datetime.now().replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
            elif args.delta_to:
                days, hours, minutes, seconds = [int(i) for i in args.delta_to]
                delta_to = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            signal.alarm(int(delta_to.total_seconds()))

        output = None
        if 'AWS_S3_ENDPOINT_URL' in os.environ:
            output = {}
            output['s3_client'] = S3Client(
                region_name=os.environ['AWS_S3_REGION_NAME'] if 'AWS_S3_REGION_NAME' in os.environ else None,
                endpoint_url=os.environ['AWS_S3_ENDPOINT_URL'],
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                config=Config(signature_version=os.environ['AWS_S3_SIGNATURE_VERSION']) if 'AWS_S3_SIGNATURE_VERSION' in os.environ else None)
            output['bucket_name'] = os.environ['AWS_STORAGE_BUCKET_NAME']
            
        client = TweepyStreaming(args.out_path, args.prefix_fname,
            args.follow, track, args.is_async, args.locations, args.languages,
            args.out_maxsize, args.count, args.verbose,
            output)
        client.start()

if __name__ == "__main__":
    
    main()
