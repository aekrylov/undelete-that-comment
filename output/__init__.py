from input import Comment, CommentSource


class Notifier:

    def notify(self, comment: Comment):
        raise NotImplementedError()
