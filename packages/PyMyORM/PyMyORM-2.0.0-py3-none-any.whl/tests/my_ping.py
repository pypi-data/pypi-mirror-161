
from config import db
from pymyorm.connection_pool import ConnectionPool


if __name__ == '__main__':
    pool = ConnectionPool()
    pool.size(size=3)
    pool.ping(seconds=1)
    pool.create(**db, lazy=False)

    conn = pool.get()
