from abc import ABC
from datetime import datetime

import pytz
import vk_api
from vk_api import ApiHttpError

import settings
from input import CommentSource, Comment


class VkDiscussion:
    def __init__(self, group_id, topic_id):
        self.group_id = group_id
        self.topic_id = topic_id
        self.url = f'https://vk.com/topic-{group_id}_{topic_id}'


class VkSourceBase(CommentSource):
    api = vk_api.VkApi(app_id=settings.APP_ID, token=settings.APP_TOKEN).get_api()

    @staticmethod
    def profile_url(user_id):
        return 'https://vk.com/id%d' % user_id if user_id > 0 else 'https://vk.com/club%d' % (-user_id)


class VkDiscussionSource(VkSourceBase):

    def __init__(self, group_id, topic_id, storage):
        super().__init__(storage)
        self.group_id = group_id
        self.topic_id = topic_id
        self.discussion = VkDiscussion(group_id, topic_id)

    def check(self):
        m = self.storage

        # TODO proper exception handling
        # 5xx errors are thrown periodically by VK, that's a known issue
        try:
            resp = self.api.board.getComments(group_id=self.group_id, topic_id=self.topic_id, count=100, sort='desc')
        except ApiHttpError as e:
            if e.response.status_code < 500:
                raise e
            resp = e.try_method()

        last_comments = [self._to_object(comment) for comment in resp['items']]

        present_map = {c.comment_id: c for c in last_comments}
        m.update(present_map)

        min_id, max_id = last_comments[-1].comment_id, max(m.keys())
        for i in range(min_id, max_id + 1):
            if i not in present_map and i in m and not m[i].deleted:
                m[i].deleted = True
                yield m[i]

    def _to_object(self, comment):
        return Comment(user_id=comment['from_id'],
                       profile_url=self.profile_url(comment['from_id']),
                       discussion=self.discussion,
                       comment_id=comment['id'],
                       text=comment['text'],
                       date=datetime.fromtimestamp(comment["date"], tz=pytz.UTC),
                       deleted='deleted' in comment)

    def __hash__(self) -> int:
        return hash((self.group_id, self.topic_id))
