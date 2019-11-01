import json

import requests

from input import Comment
from output import Notifier
from util import escape_md, MSK


class TelegramNotifier(Notifier):

    def __init__(self, bot_token, target_chat):
        self.target_chat = target_chat
        self.bot_token = bot_token

    def notify(self, comment: Comment):
        resp = requests.post(
            'https://api.telegram.org/bot' + self.bot_token + '/sendMessage',
            {
                'chat_id': self.target_chat,
                'text': f'Deleted comment found\n'
                        f'*From*: {comment.profile_url}\n'
                        f'*Date*: `{comment.date.astimezone(MSK)}`\n'
                        f'*Text*: \n{escape_md(comment.text)}\n',
                'parse_mode': 'Markdown',
                'reply_markup': json.dumps({
                    'inline_keyboard': [[{
                        'text': 'Go to discussion',
                        'url': comment.discussion.url
                    }]]
                })
            }
        )

        if resp.status_code != 200:
            print(resp.text)  # TODO error handling
