import random
import string
from urllib.request import Request, urlopen
import re
import json


def generate_password():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))


def generate_username():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(8))


def generate_date_of_birthday():
    year = str(random.randint(1993, 2003))
    month = str(random.randint(1, 12))
    day = str(random.randint(1, 28))
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    return f'{year}-{month}-{day}'


def get_client_data() -> str:
    """
    Returns the data based on what release channel is provided.
    :param release_channel_args:
    :return:
    """
    client_request = (urlopen(Request(f'https://discord.com/app', headers={'User-Agent': 'Mozilla/5.0'})).read()).decode('utf-8')

    # Regex search filter that gets the JS files
    jsFileRegex = re.compile(r'([a-zA-z0-9]+)\.js', re.I)

    # Gets the asset file which are scrambled after every build update, the last file is always fetched from the array
    asset = jsFileRegex.findall(client_request)[-1]

    assetFileRequest = (urlopen(Request(f'https://discord.com/assets/{asset}.js', headers={'User-Agent': 'Mozilla/5.0'})).read()).decode('utf-8')

    try:
        build_info_regex = re.compile('Build Number: [0-9]+, Version Hash: [A-Za-z0-9]+')
        build_info_strings = build_info_regex.findall(assetFileRequest)[0].replace(' ', '').split(',')
    # Error handling
    except (RuntimeError, TypeError, NameError):
        print(RuntimeError or TypeError or NameError)

    build_num = build_info_strings[0].split(':')[-1]

    build_hash = build_info_strings[1].split(':')[-1]

    build_id = build_hash[:7]

    return build_num
