from datetime import datetime

class Post():
    def __init__(self, text):
        self.text = text
        self.datetime = datetime.now()
