from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Category, Items, Base

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Adding Users
User1 = User(name="Nick",
              email="nick@gmail.com",
              picture='https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_640.png')
session.add(User1)
session.commit()

User2 = User(name="Ishita",
              email="ishita@gmail.com",
              picture='https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_640.png')
session.add(User2)
session.commit

User3 = User(name="Ravi",
              email="ravi@gmail.com",
              picture='https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_640.png')
session.add(User3)
session.commit

# Adding categories
Category1 = Category(name="Soccer",
                      user_id=1)
session.add(Category1)
session.commit()

Category2 = Category(name="Basketball",
                      user_id=2)
session.add(Category2)
session.commit

Category3 = Category(name="Baseball",
                      user_id=3)
session.add(Category3)
session.commit()

Category4 = Category(name="Friesbee",
                      user_id=1)
session.add(Category4)
session.commit()

Category5 = Category(name="Snowboarding",
                      user_id=2)
session.add(Category5)
session.commit()

Category6 = Category(name="Hockey",
                      user_id=3)
session.add(Category6)
session.commit()

# Adding Items
Item1 = Items(name="Two shinguards",
               description="Shin guards and socks are required for legal play in nearly all soccer leagues.",
               category_id=1,
               user_id=1)
session.add(Item1)
session.commit()

Item2 = Items(name="Stick",
               description="HockeyMonkey has the worlds largest selection of hockey sticks with a variety from Bauer, CCM, Warrior, and many more! Browse sticks for adults and kids.",
               category_id=6,
               user_id=3)
session.add(Item2)
session.commit()

Item3 = Items(name="Bat",
               description="A baseball bat is a smooth wooden or metal club used in the sport of baseball to hit the ball after it is thrown by the pitcher.",
               category_id=3,
               user_id=3)
session.add(Item3)
session.commit()

Item4 = Items(name="Basketball",
               description="Basketball is a non-contact sport played on a rectangular court",
               category_id=2,
               user_id=2)
session.add(Item4)
session.commit()

Item5 = Items(name="Googles",
               description="Superior color and contrast enhancement comes standard in our lineup of Happy Lens snow goggles, accentuating changes in terrain so you can See Better.",
               category_id=5,
               user_id=2)
session.add(Item5)
session.commit()

Item6 = Items(name="SnowBoard",
               description="Snowboards are boards that are usually the width of one's foot longways, with the ability to glide on snow.",
               category_id=5,
               user_id=2)
session.add(Item6)
session.commit()

Item7 = Items(name="Frisbee",
               description="A frisbee is a gliding toy or sporting item that is generally plastic and roughly 20 to 25 centimetres (8 to 10 in) in diameter with a lip",
               category_id=4,
               user_id=1)
session.add(Item7)
session.commit()
