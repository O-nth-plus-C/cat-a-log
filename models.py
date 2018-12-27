from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
  __tablename__ = 'categories'
  id = Column(Integer, primary_key = True)
  category_name = Column(String)
  category_image = Column(String)

class Item(Base):
  __tablename__ = 'items'

  id = Column(Integer, primary_key = True)
  item_name = Column(String)
  item_price = Column(String)
  item_description = Column(String)
  item_image = Column(String)
  
  category_id = Column(Integer, ForeignKey('categories.id'))
  category = relationship(Category)

engine = create_engine('sqlite:///restaurants.db')


Base.metadata.create_all(engine)
