from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key = True)
  name = Column(String(250), nullable = False)
  email = Column(String(250), nullable = False)


class Category(Base):
  __tablename__ = 'categories'
  id = Column(Integer, primary_key = True)
  category_name = Column(String)
  category_image = Column(String)
  user_id = Column(Integer, ForeignKey('users.id'))
  user = relationship(User)

  @property
  def serialize(self):
      #Returns data in easily serializable format
      return {
        'category_name' : self.category_name,
        'category_image'   : self.category_image,
        'id' : self.id,
        'user_id' : self.user_id
      }

class Item(Base):
  __tablename__ = 'items'

  id = Column(Integer, primary_key = True)
  item_name = Column(String)
  item_price = Column(String)
  item_description = Column(String)
  item_image = Column(String)

  category_id = Column(Integer, ForeignKey('categories.id'))
  category = relationship(Category)

  user_id = Column(Integer, ForeignKey('users.id'))
  user = relationship(User)

  @property
  def serialize(self):
      #Returns data in easily serializable format
      return {
        'item_name' : self.item_name,
        'item_image'   : self.item_image,
        'item_price' : self.item_price,
        'item_description' : self.item_description,
        'category_id' : self.category_id,
        'id' : self.id,
        'user_id' : self.user_id
      }

engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
