from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import les3_DZ


class DataBase:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        les3_DZ.Base.metadata.create_all(bind=engine)
        self.session_m = sessionmaker(bind=engine)

    @staticmethod
    def __get_or_create(session, model, **data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = les3_DZ(**data)

        return db_model

    def create_post(self, data):
        session = self.session_m()
        tags = map(lambda tag_data: self.__get_or_create(session, les3_DZ.Tags, **tag_data), data['tags'])
        comments = map(lambda comment_data: self.__get_or_create(session, les3_DZ.Comments, **comment_data), data['comments'])
        writer = self.__get_or_create(session, les3_DZ.Writers, **data['writer'])
        post = self.__get_or_create(session, les3_DZ.Posts, **data['post_data'], writer=writer)
        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()