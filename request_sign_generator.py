import argparse
import hashlib
import time
import random
import logging
import regex as re
import json
import urllib.parse

shell_args_parser = argparse.ArgumentParser(prog='XiaoYoubang-API-Signature-Generator',
                                            description="Generate signature for XiaoYoubang APIs",
                                            epilog="XiaoYoubang API Signature Generator (C) Bobby Gao, " \
                                            "reference to: github.com/gaobobo/Fxxk_XiaoYoubang")

shell_args_parser.add_argument('string',
                               help='Content that need to signature')

shell_args_parser.add_argument('--timestamp',
                               help='The time of signature, default is current time',
                               default=str(int(time.time())) )

shell_args_parser.add_argument('--keys',
                               help='Keys or charset when signature used. Use the key of XiaoYoubang' \
                                    'Student WeChat Mini APP V1.6.39 that decompiled by default',
                               default='5bfAJQgalpsqH4LQg16QZvwbce22mlEgGHIrosd57xtJSTFvw4890KE340mrin')

shell_args_parser.add_argument('--index-string',
                               help="Random select key's subset when not specific. If specific, use " \
                                    "`_` to split index of key. ",
                               default="_".join(str(random.randint(0, 61)) for _ in range(20)) )

shell_args_parser.add_argument('-o', '--outputs',
                               help='Specific output format, default is `text` or plain text',
                               choices=['text', 'json', 'no_header_text'],
                               default='text')

shell_args_parser.add_argument('-v', '--verbose',
                               help='Show details when specific',
                               action='store_true')


shell_args = shell_args_parser.parse_args()

logging.basicConfig(level=logging.INFO if shell_args.verbose else logging.WARNING,
                    format='\x1b[48;5;166m %(asctime)s \x1b[48;5;33m %(levelname)s \x1b[0m %(message)s')
logger = logging.getLogger('signature_generator')


INPUT = shell_args.string
KEY = shell_args.keys
INDEX = shell_args.index_string
TIMESTAMP = shell_args.timestamp
OUTPUT_FORMAT = shell_args.outputs


def get_key(index_str: str = INDEX) -> str:
    return "".join(shell_args.keys[int(i)] for i in index_str.split('_'))


def get_string(text: str = INPUT) -> str:
    # remove CJK Unicode area
    # text = re.sub('[\\u4E00-\\u9FFF]+', '', text)
    # text = re.sub(r'\p{Han}+', '', text)  # decompiled code shows CJK not remove

    # remove punctuation marks
    # text = re.sub(r"[`~!@#$%^&*()+=|{}':;',\[\].<>/?~！@#￥%……&*（）——+|{}【】‘；：”“’。，、？]",
    #               repl='', string=text)
    text = re.sub(r"\p{p}", '', text)

    # remove empty space
    text = re.sub(r"\s+", '', text)

    # remove [<, >, &, -]
    # text = re.sub(r"[<>&-]", '', text)    # completely same as above

    # remove emojis
    # text = re.sub("\uD83C[\uDF00-\uDFFF]|\uD83D[\uDC00-\uDE4F]", '', text)
    text = re.sub(r"\p{Emoji}", '', text)

    return text


def get_signature(input_str: str, timestamp: str, key: str ) -> str:
    binary_string = urllib.parse.quote(clear_string(input_str + timestamp + key), safe='')
    return hashlib.md5(binary_string.encode('utf-8')).hexdigest()


if __name__ == '__main__':
    logger.info('Started.')

    logger.info(f'Key set is: {KEY}')
    logger.info(f'Random index is: {INDEX}')
    logger.info(f'Timestamp is: {TIMESTAMP}')

    logger.info(f'Trying to generate signature...')

    key = get_key()
    source_string = get_string()

    logger.info(f'Your random key is: {key}')
    logger.info(f'Your input string is: {source_string}')

    signature = get_signature(source_string, TIMESTAMP, key)

    logger.info(f'Your signature is: {signature}')
    logger.info(f'Output formated is: {OUTPUT_FORMAT}')

    match OUTPUT_FORMAT:
        case 'text':
            print(f'md5: {signature}')
            print(f'timestamp: {TIMESTAMP}')
            print(f'index: {INDEX}')

        case 'json':
            print(json.dumps({'md5': signature, 'timestamp': TIMESTAMP, 'index': INDEX}))

        case 'no_header_text':
            print(f'{signature}')
            print(f'{TIMESTAMP}')
            print(f'{INDEX}')