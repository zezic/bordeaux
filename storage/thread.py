from .post import Post

class Thread():
    def __init__(self):
        self.posts = []

    def add_post(self, text):
        new_post = Post(text)
        self.posts.append(new_post)
        return new_post
