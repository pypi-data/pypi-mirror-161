from pymyorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':
    Database.connect(**db)

    all = User.find().select('count(*) as count', 'sum(money) as total') \
        .group('gender') \
        .having('sum(money)', '>', 200) \
        .all()
    for one in all:
        print(one)
