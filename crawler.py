import argparse
import json
from datetime import datetime

import vk_api
import shelve
import time

import pytz

import requests

import settings

parser = argparse.ArgumentParser()
parser.add_argument('topic', nargs='+', help='topic identifier in format <group-id>_<topic-id>')
args = parser.parse_args()

topics = [tuple(map(lambda x: abs(int(x)), t.split('_'))) for t in args.topic]

session = vk_api.VkApi(app_id=settings.APP_ID, token=settings.APP_TOKEN)

vk = session.get_api()

d = shelve.open('data/db', writeback=True)

MSK = pytz.timezone('Europe/Moscow')


def escape_md(text: str) -> str:
    """Escapes some special Markdown symbols"""
    return text.translate(str.maketrans({
        '_': r'\_',
        '*': r'\*',
        '`': r'\`',
        '[': r'\['
    }))


def notify_telegram(gid, tid, comment):
    from_id = comment['from_id']
    profile_url = 'https://vk.com/id%d' % from_id if from_id > 0 else 'https://vk.com/club%d' % (-from_id)

    resp = requests.post(
        'https://api.telegram.org/bot'+settings.BOT_TOKEN+'/sendMessage',
        {
            'chat_id': settings.BOT_CHAT_ID,
            'text': f'Deleted comment found\n'
                    f'*From*: {profile_url}\n'
                    f'*Date*: `{datetime.fromtimestamp(comment["date"], tz=pytz.UTC).astimezone(MSK)}`\n'
                    f'*Text*: \n{escape_md(comment["text"])}\n',
            'parse_mode': 'Markdown',
            'reply_markup': json.dumps({
                'inline_keyboard': [[{
                    'text': 'Go to discussion',
                    'url': f'https://vk.com/topic-{gid}_{tid}'
                }]]
            })
        }
    )

    if resp.status_code != 200:
        print(resp.text)


for gid, tid in topics:
    if str(gid) not in d:
        d[str(gid)] = {}

try:
    while True:
        for gid, tid in topics:
            m = d[str(gid)]

            last_comments = vk.board.getComments(group_id=gid, topic_id=tid, count=100, sort='desc')['items']
            present_map = {c['id']: c for c in last_comments}
            for comment in last_comments:
                m[comment['id']] = comment

            min_id, max_id = last_comments[-1]['id'], max(last_comments[0]['id'], sorted(m.keys())[-1])
            for i in range(min_id, max_id + 1):
                if i not in present_map and i in m and 'deleted' not in m[i]:
                    print("Found deleted comment", m[i])
                    m[i]['deleted'] = True
                    notify_telegram(gid, tid, m[i])
            d.sync()
        time.sleep(5)

except KeyboardInterrupt:
    print("Received interrupt")
finally:
    d.close()
