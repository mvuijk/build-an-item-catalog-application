import sys

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """ Return object data in easily serializeable format """
        return {
           "name": self.name,
           "id": self.id,
           "email": self.email,
           "picture": self.picture
        }


class CatalogCategory(Base):
    __tablename__ = "catalog_categories"

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        """ Return object data in easily serializeable format """
        return {
            "name": self.name,
            "id": self.id
        }


class CatalogCategoryItem(Base):
    __tablename__ = "catalog_category_items"

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('catalog_categories.id'))
    category = relationship(CatalogCategory)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        """ Return object data in easily serializeable format """
        return {
            "name": self.name,
            "description": self.description
        }

engine = create_engine('sqlite:///catalogCategoryItems.db')

Base.metadata.create_all(engine)
