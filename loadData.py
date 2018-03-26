from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databaseSetup import Base, User, CatalogCategory, CatalogCategoryItem

engine = create_engine('sqlite:///catalogCategoryItems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Dummy User
user = User(name="Dummy", email="dummy.user@udacity.com")
session.add(user)
session.commit()

print("added user!")

# Category #1
category1 = CatalogCategory(name="Soccer", user_id=1)

session.add(category1)
session.commit()

# Category #2
category2 = CatalogCategory(name="Basketball", user_id=1)

session.add(category2)
session.commit()

# Category #3
category3 = CatalogCategory(name="Baseball", user_id=1)

session.add(category3)
session.commit()

# Category #4
category4 = CatalogCategory(name="Frisbee", user_id=1)

session.add(category4)
session.commit()

# Category #5
category5 = CatalogCategory(name="Snowboarding", user_id=1)

session.add(category5)
session.commit()

# Category #6
category6 = CatalogCategory(name="Rock Climbing", user_id=1)

session.add(category6)
session.commit()

# Category #7
category7 = CatalogCategory(name="Football", user_id=1)

session.add(category7)
session.commit()

# Category #8
category8 = CatalogCategory(name="Skating", user_id=1)

session.add(category8)
session.commit()

# Category #9
category9 = CatalogCategory(name="Hockey", user_id=1)

session.add(category9)
session.commit()

print("added categories!")

# Item #1
item1 = CatalogCategoryItem(
    name="Helm", description="Helm", category_id=5, user_id=1)
session.add(item1)
session.commit()

# Item #2
item2 = CatalogCategoryItem(
    name="Soccer Cleats",
    description="Soccer Cleats", category_id=1, user_id=1)
session.add(item2)
session.commit()

# Item #3
item3 = CatalogCategoryItem(
    name="Jersey", description="Jersey", category_id=1, user_id=1)
session.add(item3)
session.commit()

# Item #4
item4 = CatalogCategoryItem(
    name="Bat", description="Bat", category_id=3, user_id=1)
session.add(item4)
session.commit()

# Item #5
item5 = CatalogCategoryItem(
    name="Frisbee", description="Frisbee", category_id=4, user_id=1)
session.add(item5)
session.commit()

# Item #6
item6 = CatalogCategoryItem(
    name="Shinguards", description="Shinguards", category_id=1, user_id=1)
session.add(item6)
session.commit()

# Item #7
item7 = CatalogCategoryItem(
    name="Two Shinguards",
    description="Two Shinguards", category_id=1, user_id=1)
session.add(item7)
session.commit()

# Item #8
item8 = CatalogCategoryItem(
    name="Snowboard", description="Snowboard", category_id=5, user_id=1)
session.add(item8)
session.commit()

# Item #9
item9 = CatalogCategoryItem(
    name="Goggles", description="Goggles", category_id=5, user_id=1)
session.add(item9)
session.commit()

# Item #10
item10 = CatalogCategoryItem(
    name="Stick", description="Stick", category_id=9, user_id=1)
session.add(item10)
session.commit()

print("added items!")
