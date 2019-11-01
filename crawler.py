import argparse
import shelve
import time
from collections import defaultdict

import settings
from input.vk import VkDiscussionSource
from output.telegram import TelegramNotifier

parser = argparse.ArgumentParser()
parser.add_argument('topic', nargs='+', help='topic identifier in format <group-id>_<topic-id>')
args = parser.parse_args()

topics = [tuple(map(lambda x: abs(int(x)), t.split('_'))) for t in args.topic]

d = shelve.open('data/db2', writeback=True)
d[VkDiscussionSource.__name__] = defaultdict(dict)

sources = [VkDiscussionSource(gid, tid, d[VkDiscussionSource.__name__][(gid, tid)]) for gid, tid in topics]
out = TelegramNotifier(settings.BOT_TOKEN, settings.BOT_CHAT_ID)

try:
    while True:
        for source in sources:
            for comment in source.check():
                print("Found deleted comment", repr(comment))
                out.notify(comment)
            d.sync()
        time.sleep(5)

except KeyboardInterrupt:
    print("Received interrupt")
finally:
    d.close()
