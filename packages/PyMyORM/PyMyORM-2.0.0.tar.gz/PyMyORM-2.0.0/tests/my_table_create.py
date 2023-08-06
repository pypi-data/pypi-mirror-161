from pymyorm.database import Database
from config import db


if __name__ == '__main__':

    Database.connect(**db)

    fp = open('mysql/t_admin.sql', 'r', encoding='utf-8')
    sql = fp.read()
    Database.execute(sql)
    fp.close()

    fp = open('mysql/t_admin_role.sql', 'r', encoding='utf-8')
    sql = fp.read()
    Database.execute(sql)
    fp.close()

    fp = open('mysql/t_admin_auth.sql', 'r', encoding='utf-8')
    sql = fp.read()
    Database.execute(sql)
    fp.close()

