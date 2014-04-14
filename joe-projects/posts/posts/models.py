import datetime

from sqlalchemy import Column, Integer, String, DateTime, Sequence

from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, Sequence('post_id_sequence'), primary_key=True)
    title = Column(String(128))
    body = Column(String(1024))
    datetime = Column(DateTime, default=datetime.datetime.now)

    def asDictionary(self):
        post = {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "datetime": self.datetime.isoformat()
        }
        return post
