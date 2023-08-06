from pymyorm.database import Database
from config import db


if __name__ == '__main__':
    Database.connect(**db, lazy=False)
    sql = "select * from t_user"
    num = Database.execute(sql)
    print(num)
