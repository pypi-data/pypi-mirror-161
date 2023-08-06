import mysql.connector.pooling as mysql_pooling
from mysql.connector.errors import *
from dacite import from_dict
import logging
import traceback
import threading
import time
from SKPython import object_mapper

#TODO: none을 null로 만드는 사항 추가
class MysqlManager:
    def __new__(cls, host:str , port: int, user: str, passwd: str, database:str, pool_size:int = 5, pool_name: str = "mysql_conn_pool", callback_connect = None, callback_disconnect = None, callback_error = None):
        if not hasattr(cls, "instance"):
            cls.instance = super(MysqlManager, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, host:str , port: int, user: str, passwd: str, database:str, pool_size:int = 5, pool_name: str = "mysql_conn_pool", callback_connect = None, callback_disconnect = None, callback_error = None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database = database
        self.pool_size = pool_size
        self.pool_name = pool_name
        self.callback_connect = callback_connect
        self.callback_disconnect = callback_disconnect
        self.callback_error = callback_error
        
        self.is_reconnecting = True
        self.retry_connect_seconds = 30
        self.db_pool = None
        
        self._init()
        
    def _reconnect(self):
        self.is_reconnecting = True
        logging.info(f"mysql disconnected. retry next {self.retry_connect_seconds} seconds")
        time.sleep(self.retry_connect_seconds)
        threading.Thread(target=self._init).start()

    def _default_success_connect(self):
        logging.info(f"connected mysql: {self.host}:{self.port}/{self.database}")    
        self.is_reconnecting = False
    
    def _init(self):
        try:
            logging.info(f"{self.host}:{self.port} {self.user}, db: {self.database}")
            dbconfig = {
                "pool_size": self.pool_size,
                "pool_name": self.pool_name,
                "pool_reset_session": True,
                "user": self.user,
                "password": self.passwd,
                "host": self.host,
                "port": self.port,
                "database": self.database
            }
            # pool 개수 최대 32개
            self.db_pool = mysql_pooling.MySQLConnectionPool(**dbconfig)
            self._default_success_connect()
            
            if self.callback_connect is not None:
                self.callback_connect()
                
            return True
        except:
            logging.error(traceback.format_exc())
            
            if self.callback_disconnect is not None:
                self.callback_disconnect()
            
            if self.is_reconnecting:
                logging.info(f"mysql disconnected. retry next {self.retry_connect_seconds} seconds")
                time.sleep(self.retry_connect_seconds)
                self._init()
    
    def get_connection(self):
        try:
            conn = self.db_pool.get_connection()
            return conn
        except InterfaceError as exi:
            logging.error(f"{traceback.format_exc()}")
            if self.is_reconnecting == False:
                self._reconnect()
            raise exi
        except Exception as e:
            raise e

__client__: MysqlManager = None

def init(host:str , port: int, user: str, passwd: str, database:str, pool_size:int = 5, pool_name: str = "mysql_conn_pool", callback_connect = None, callback_disconnect = None, callback_error = None) -> MysqlManager:
    # SSL 관련 오류시 mysql-connector-python 버전 확인할 것 
    # mysql-connector-python 8.0.22 버전 설치 필요
    global __client__
    if __client__ is None:
        __client__ = MysqlManager(host , port, user, passwd, database, pool_size=pool_size, pool_name=pool_name, callback_connect = callback_connect, callback_disconnect = callback_disconnect, callback_error = callback_error)
    return __client__

def select(query):
    conn = None
    try:
        conn = __client__.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception:
        logging.error(traceback.format_exc())
        logging.error(f"error_query: {query}")
        
        if __client__.callback_error != None:
            __client__.callback_error()
        return None
    finally:
        if conn is not None and conn.is_connected() == True :
            cursor.close()
            conn.close()

def select_one(query):
    result = select(query)
    if result is not None and len(result) >= 1:
        return result[0]
    else:
        return None
    
def select_dict(query):
    conn = None
    try:
        conn = __client__.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception:
        logging.error(traceback.format_exc())
        logging.error(f"error_query: {query}")
        if __client__.callback_error != None:
            __client__.callback_error()
        return None
    finally:
        if conn is not None and conn.is_connected() == True :
            cursor.close()
            conn.close()

def select_one_dict(query):
    result = select_dict(query)
    if result is not None and len(result) >= 1:
        return result[0]
    else:
        return None

def select_object(query, data_class: type):
    result = select_dict(query)
    if result is None:
        return None
    return list(map(lambda r: object_mapper.getObject(data_class=data_class, data=r), result))

def select_one_object(query, data_class: type):
    result = select_object(query, data_class)
    if result is not None and len(result) >= 1:
        return result[0]
    else:
        return None

def execute_queries(*queries):
    conn = None
    try:
        conn = __client__.get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        for query in queries:
            if type(query) in (list, tuple, set):
                for q in query:
                    cursor.execute(q)
            else:
                cursor.execute(query)
        conn.commit()
        return True, None
    except Exception as e:
        if conn is not None:
            conn.rollback()
        logging.error(traceback.format_exc())
        logging.error(f"error_query: {query}")
        if __client__.callback_error != None:
            __client__.callback_error()
        
        errorMsg = None
        if IntegrityError == type(e):
            if e.errno == 1062:
                errorMsg = "중복된 pk 입니다."
        return False, errorMsg
    finally:
        if conn is not None and conn.is_connected() == True :
            cursor.close()
            conn.close()
