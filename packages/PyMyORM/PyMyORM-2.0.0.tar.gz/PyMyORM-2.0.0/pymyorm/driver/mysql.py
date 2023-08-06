
import time
import logging
import pymysql
import decimal
import datetime
from pymysql import cursors
from pymyorm.batch import Batch


class Connection(object):

    def __init__(self, host, port, user, password, database, charset='utf8', debug=False) -> None:
        self.__source = 'mysql'
        self.__conn = None
        self.__debug = debug
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = database
        self.__charset = charset
        self.__last_ping_time = int(time.time())
        self.__ping = 3600

    def __del__(self):
        self.close()

    def open(self):
        self.close()
        try:
            config = dict(
                host=self.__host,
                port=self.__port,
                user=self.__user,
                password=self.__password,
                database=self.__database,
                charset=self.__charset,
                cursorclass=cursors.DictCursor
            )
            if self.__debug:
                logging.info(msg=str(config))
            self.__conn = pymysql.connect(**config)
            self.__conn.autocommit(True)
            if self.__debug:
                logging.info(f'{self.__source} connect success')
        except Exception as e:
            if self.__debug:
                logging.error(f'{self.__source} connect error')
            raise e

    def close(self):
        if self.__conn is not None:
            if self.__debug:
                logging.info(f'{self.__source} connection closed')
            self.__conn.close()
            self.__conn = None

    def source(self):
        return self.__source

    def set_ping(self, seconds):
        self.__ping = seconds

    def ping(self):
        if self.__conn is None:
            return
        current_time = int(time.time())
        if current_time - self.__last_ping_time > self.__ping:
            try:
                if self.__debug:
                    logging.info('conn ping')
                self.__conn.ping()
            except Exception as e:
                if self.__debug:
                    logging.error(str(e))
        self.__last_ping_time = int(time.time())

    def tables(self):
        sql = f"select table_name from information_schema.tables WHERE table_schema='{self.__database}'"
        all = self.fetchall(sql)
        return [one['table_name'] for one in all]

    def schema(self, table):
        sql = f"select column_name,column_key,data_type,extra,column_comment from information_schema.columns where table_schema='{self.__database}' and table_name='{table}'"
        return self.fetchall(sql)

    def table_exists(self, table):
        sql = f"select table_name from information_schema.tables WHERE table_schema='{self.__database}' and table_name='{table}'"
        one = self.fetchone(sql)
        if one is not None:
            return True
        else:
            return False

    def primary_key(self, table):
        all = self.schema(table)
        for one in all:
            if one['column_key'] == 'PRI':
                return one['column_name']
        return ''

    def fetchone(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            one = cursor.fetchone()
            cursor.close()
            if one is None:
                return None
            for k, v in one.items():
                if isinstance(v, datetime.datetime):
                    one[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, datetime.date):
                    one[k] = v.strftime('%Y-%m-%d')
                elif isinstance(v, decimal.Decimal):
                    one[k] = float(v)
            return one
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def fetchall(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            all = cursor.fetchall()
            cursor.close()
            if all is None:
                return []
            for one in all:
                for k, v in one.items():
                    if isinstance(v, datetime.datetime):
                        one[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(v, datetime.date):
                        one[k] = v.strftime('%Y-%m-%d')
                    elif isinstance(v, decimal.Decimal):
                        one[k] = float(v)
            return all
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def batch(self, sql):
        try:
            if self.__debug:
                logging.info(f"batch sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            return Batch(cursor, self.__source)
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def insert(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            last_insert_id = cursor.lastrowid
            cursor.close()
            return last_insert_id
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def insert_batch(self, sql, data):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.executemany(sql, data)
            last_insert_id = cursor.lastrowid
            cursor.close()
            return last_insert_id
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def execute(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            num = cursor.execute(sql)
            cursor.close()
            return num
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def count(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def sum(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def min(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def max(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def average(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def exists(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total == 1
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def column(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def scalar(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            return result
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def begin(self):
        try:
            sql = "begin"
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            self.__conn.autocommit(False)
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def rollback(self):
        try:
            sql = "rollback"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
            self.__conn.autocommit(True)
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def commit(self):
        try:
            sql = "commit"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
            self.__conn.autocommit(True)
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def savepoint(self, identifier):
        try:
            sql = f"savepoint {identifier}"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def rollback_savepoint(self, identifier):
        try:
            sql = f"rollback to savepoint {identifier}"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()

    def release_savepoint(self, identifier):
        try:
            sql = f"release savepoint {identifier}"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except pymysql.OperationalError as e:
            logging.error(str(e))
            self.open()
