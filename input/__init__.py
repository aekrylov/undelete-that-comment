import abc
from datetime import datetime


class Comment:
    def __init__(self, user_id, profile_url, discussion, comment_id: int, text: str, date: datetime, deleted: bool = False, profile_name: str = None):
        self.user_id = user_id
        self.profile_url = profile_url
        self.profile_name = profile_name if profile_name else profile_url.split('/')[-1]
        self.discussion = discussion
        self.comment_id = comment_id
        self.text = text
        self.date = date
        self.deleted = deleted

    def __repr__(self) -> str:
        return f'Comment(profile_url={self.profile_url}, text={repr(self.text)}, date={self.date}, ' \
               f'deleted={self.deleted}, discussion_url={self.discussion.url}, )'


class CommentSource:

    def __init__(self, storage):
        self.storage = storage

    def check(self):
        raise NotImplementedError()
