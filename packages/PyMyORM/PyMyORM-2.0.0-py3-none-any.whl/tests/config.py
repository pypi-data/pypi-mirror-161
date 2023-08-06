import logging

db = dict(
    source='mysql',
    host='127.0.0.1',
    port=3306,
    user='root',
    password='password',
    database='test',
    charset='utf8',
    debug=True
)

# db = dict(
#     source='pgsql',
#     host='127.0.0.1',
#     port=5432,
#     user='postgres',
#     password='password',
#     database='postgres',
#     debug=True
# )

logging.basicConfig(level=logging.DEBUG)
