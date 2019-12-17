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
    session = vk_api.VkApi(app_id=settings.APP_ID, token=settings.APP_TOKEN)

    @staticmethod
    def profile_url(user_id):
        return 'https://vk.com/id%d' % user_id if user_id > 0 else 'https://vk.com/club%d' % (-user_id)

    def __init__(self, storage):
        super().__init__(storage)
        self.api = self.session.get_api()


class VkDiscussionSource(VkSourceBase):

    def __init__(self, group_id, topic_id, storage, n_last=100):
        super().__init__(storage)
        self.group_id = group_id
        self.topic_id = topic_id
        self.discussion = VkDiscussion(group_id, topic_id)
        self.n_last = n_last

        self.last_response = None

    def check(self):
        m = self.storage

        params = {'group_id': self.group_id, 'topic_id': self.topic_id, 'count': 100, 'sort': 'desc'}

        # TODO proper exception handling
        # 5xx errors are thrown periodically by VK, that's a known issue
        try:
            resp = self.api.board.getComments(**params)
        except ApiHttpError as e:
            if e.response.status_code < 500:
                raise e
            resp = e.try_method()

        comments = [self._to_object(comment) for comment in resp['items']]
        if self._need_deep_check(resp):
            # NB: this won't work with a service token since it uses the execute method
            results, errors = vk_api.requests_pool.vk_request_one_param_pool(
                self.session, 'board.getComments',
                key='offset', values=list(range(100, self.n_last, 100)), default_values=params
            )
            if len(errors):
                # TODO
                pass

            comments += [self._to_object(comment) for offset, comms in results for comment in comms]
            comments.sort(key=lambda c: c.comment_id)

        self.last_response = resp

        present_map = {c.comment_id: c for c in comments}
        m.update(present_map)

        min_id, max_id = comments[-1].comment_id, max(m.keys())
        for i in range(min_id, max_id + 1):
            if i not in present_map and i in m and not m[i].deleted:
                m[i].deleted = True
                yield m[i]

    def _need_deep_check(self, resp):
        """
        Determine if older comments have changed and should be checked
        :param resp: server response, must be successful
        :return: True if older comments have changed
        """
        items = resp['items']
        last_items = self.last_response['items']
        return self.n_last > 100 and (
                resp['count'] != self.last_response['count']
                or (items[0]['id'], items[-1]['id']) != (last_items[0]['id'], last_items[-1]['id'])
        )

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
