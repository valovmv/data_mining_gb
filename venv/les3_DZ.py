'''
реализовать SQL структуру хранения данных c следующими таблицами
Post
Comment
Writer
Tag
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

comment_post = Table(
    'comment_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('comment_id', Integer, ForeignKey('comments.id'))
)

'''
1. url страницы материала
2. Заголовок материала
3. Первое изображение материала (Ссылка)
4. Дата публикации (в формате datetime)
5. имя автора материала
6. ссылка на страницу автора материала
7. комментарии в виде (автор комментария и текст комментария)
8. список тегов
'''


class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    image = Column(String, unique=False, nullable=True)
    date = Column(DateTime(timezone=True), unique=False)
    writer_id = Column(Integer, ForeignKey('writers.id'))
    writer = relationship("Writers", back_populates='posts')
    tags = relationship('Tags', secondary=tag_post, back_populates='posts')
    comments = relationship('Comments', secondary=comment_post, back_populates='posts')


class Writers(Base):
    __tablename__ = 'writers'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    posts = relationship("Posts")


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    posts = relationship('Posts', secondary=tag_post)


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    author = Column(String, unique=False, nullable=False)
    comment = Column(String, unique=False, nullable=False)
    posts = relationship('Posts', secondary=comment_post)