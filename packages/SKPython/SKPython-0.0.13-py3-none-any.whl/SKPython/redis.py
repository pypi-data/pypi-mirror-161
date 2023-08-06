import logging
import redis
from redis.sentinel import Sentinel
from redis.exceptions import ReadOnlyError, ConnectionError
import traceback
import time

class RedisManager:
    def __new__(cls, is_sentinel:bool = False, sentinel_host_and_port:str = None, sentinel_master_name:str = "mymaster", single_host:str=None, single_port:int=None, redis_passwd:str=None):
        if not hasattr(cls, "instance"):
            cls.instance = super(RedisManager, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, is_sentinel:bool = False, sentinel_host_and_port:str = None, sentinel_master_name:str = "mymaster", single_host:str=None, single_port:int=None, redis_passwd:str=None):
        self.is_sentinel = is_sentinel
        self.sentinel_host_and_port = sentinel_host_and_port
        self.sentinel_master_name = sentinel_master_name
        self.redis_passwd = redis_passwd
        self.single_host = single_host
        self.single_port = single_port
        self.reconnect_function = None
        self.redis_client = None
        self.reconnect = False
        
        if self.is_sentinel:
            if None in (self.sentinel_host_and_port, self.sentinel_master_name):
                raise Exception(
                    f"redis sentinel 정보를 확인 바랍니다. host: {self.sentinel_host_and_port}, masterName: {self.sentinel_master_name}, passwd: {self.sentinel_passwd}"
                )
            self.reconnect_function = self._connect_sentinel_master
        else:
            if None in (self.single_host, self.single_port):
                raise Exception(
                    f"redis(single) 정보를 확인 바랍니다. host: {self.single_host}, port: {self.single_port}, password: {self.single_passwd}"
                )
            self.reconnect_function = self._connect_single

        self.reconnect_function()

    def _reconnect_redis_master(self):
        if self.reconnect == False:
            self.reconnect = True
            time.sleep(2.5)
            self.reconnect_function()
            self.reconnect = False
        else:
            time.sleep(3)

    def _connect_sentinel_master(self):
        """
        connect redis sentinel

        @param sentinelHostAndPort: ex) 172.21.112.61:26379,172.21.115.40:26379,172.21.115.46:26379
        """
        host_port_list = self._make_host_and_port_tuples(self.sentinel_host_and_port)
        sentinel = Sentinel(host_port_list)
        host, port = sentinel.discover_master(self.sentinel_master_name)
        self.redis_client = redis.StrictRedis(
            host=host,
            port=port,
            password=self.redis_passwd,
            charset="utf-8",
            decode_responses=True,
        )
        logging.info(f"connect redis sentinel master: {host}:{port}")


    def _connect_single(self):
        """
        connect redis single
        """
        pool = redis.ConnectionPool(host=self.single_host, port=self.single_port, db=0)
        self.redis_client = redis.Redis(
            connection_pool=pool, charset="utf-8", decode_responses=True, password=self.redis_passwd
        )
        logging.info(f"connect redis single: {self.single_host}:{self.single_port}")


    def _make_host_and_port_tuples(self, host_and_port):
        host_port_list = []
        csv_list = host_and_port.split(",", -1)
        for host_port in csv_list:
            hosts = host_port.split(":", -1)
            host_port_list.append((hosts[0], int(hosts[1])))

        return host_port_list

__client__: RedisManager = None

def init(is_sentinel:bool = False, sentinel_host_and_port:str = None, sentinel_master_name:str = None, single_host:str=None, single_port:int=None, redis_passwd:str=None) -> RedisManager:
    global __client__
    if __client__ is None:
        __client__ = RedisManager(is_sentinel = is_sentinel, sentinel_host_and_port = sentinel_host_and_port, sentinel_master_name = sentinel_master_name, single_host = single_host, single_port = single_port, redis_passwd = redis_passwd)
    return __client__

def set_ttl(key, value, seconds):
        try:
            return __client__.redis_client.setex(key, seconds, value)
        except (ReadOnlyError, ConnectionError):
            logging.warn(traceback.format_exc())
            __client__.redis_client._reconnect_redis_master()
            return set_ttl(key, value, seconds)

def get_ttl(key):
    try:
        return __client__.redis_client.ttl(key)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return get_ttl(key)

def set(key, value):
    try:
        return __client__.redis_client.set(key, value)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return set(key)

def get(key):
    try:
        return _convert_to_string_from_bytes(__client__.redis_client.get(key))
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return get(key)

def delete(*key):
    try:
        return __client__.redis_client.delete(*key)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return delete(*key)


def hset(hash_name, key, value):
    try:
        return __client__.redis_client.hset(hash_name, key, value)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hset(hash_name, key, value)


def hget(hash_name, key):
    try:
        return _convert_to_string_from_bytes(__client__.redis_client.hget(hash_name, key))
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hget(hash_name, key)


def hdel(hash_name, key):
    try:
        return __client__.redis_client.hdel(hash_name, key)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hdel(hash_name, key)


def hgetall(hash_name):
    try:
        return _convert_to_string_from_bytes(__client__.redis_client.hgetall(hash_name))
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hgetall(hash_name)


def hincr_by(hash_name, key, amount=1):
    try:
        return __client__.redis_client.hincrby(hash_name, key, amount=amount)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hincr_by(hash_name, key, amount)


def hincr_by_float(hash_name, key, amount=1.0):
    try:
        return __client__.redis_client.hincrbyfloat(hash_name, key, amount=amount)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hincr_by_float(hash_name, key, amount)


def lpush(key, *values):
    try:
        return __client__.redis_client.lpush(key, *values)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return lpush(key, *values)


def rpush(key, *values):
    try:
        return __client__.redis_client.rpush(key, *values)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return rpush(key, *values)


def blpop(keys, timeout=None):
    """
    blpop 사용시 timeout을 이용하여 graceful shutdown 구현이 필요함
    timeout이 없을 경우 blpop 무한 대기 중에 pop을 해버릴 가능성이 있음
    redis connection을 다 끊어버리면 현재 동작중인 작업에 문제가 있을 수 있음
    """
    try:
        pop_data = __client__.redis_client.blpop(keys, timeout=timeout)
        if pop_data is None:
            return None
        return _convert_to_string_from_bytes(pop_data[1])
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return blpop(keys, timeout)


async def async_blpop(keys, timeout=None):
    """
    blpop 사용시 timeout을 이용하여 graceful shutdown 구현이 필요함
    timeout이 없을 경우 blpop 무한 대기 중에 pop을 해버릴 가능성이 있음
    redis connection을 다 끊어버리면 현재 동작중인 작업에 문제가 있을 수 있음
    """
    try:
        pop_data = __client__.redis_client.blpop(keys, timeout=timeout)
        if pop_data is None:
            return None
        return _convert_to_string_from_bytes(pop_data[1])
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return await async_blpop(keys, timeout)


def lpop(key, count=None):
    try:
        return _convert_to_string_from_bytes(__client__.redis_client.lpop(key, count))
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return lpop(key)


def brpop(keys, timeout=None):
    """
    brpop 사용시 timeout을 이용하여 graceful shutdown 구현이 필요함
    timeout이 없을 경우 brpop 무한 대기 중에 pop을 해버릴 가능성이 있음
    redis connection을 다 끊어버리면 현재 동작중인 작업에 문제가 있을 수 있음
    """
    try:
        pop_data = __client__.redis_client.brpop(keys, timeout=timeout)
        if pop_data is None:
            return None
        return _convert_to_string_from_bytes(pop_data[1])
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return brpop(keys, timeout)


async def async_brpop(keys, timeout=None):
    """
    brpop 사용시 timeout을 이용하여 graceful shutdown 구현이 필요함
    timeout이 없을 경우 brpop 무한 대기 중에 pop을 해버릴 가능성이 있음
    redis connection을 다 끊어버리면 현재 동작중인 작업에 문제가 있을 수 있음
    """
    try:
        pop_data = __client__.redis_client.brpop(keys, timeout=timeout)
        if pop_data is None:
            return None
        return _convert_to_string_from_bytes(pop_data[1])
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return await async_brpop(keys, timeout)


def rpop(key, count=None):
    try:
        return _convert_to_string_from_bytes(__client__.redis_client.rpop(key, count))
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return rpop(key)


def llen(key):
    try:
        return __client__.redis_client.llen(key)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return llen(key)


def expire(key, seconds=1):
    try:
        return __client__.redis_client.expire(key, seconds)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return expire(key, seconds)


def incr(key, amount=1):
    try:
        return __client__.redis_client.incr(key, amount)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return incr(key)

def incr_and_expire(key, seconds=1):
    count = incr(key)
    if 1 == count:
        expire(key, seconds)
    return count


def incr_and_expire_duplicate(key, seconds=1):
    count = incr(key)
    expire(key, seconds)
    return count


def keys(key):
    try:
        return __client__.redis_client.keys(key)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return keys(key)


def hscan(key, cursor: int, matcher: str, count=100000):
    try:
        return __client__.redis_client.hscan(key, cursor, match=f"{matcher}", count=count)
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return hscan(key, matcher, count)


def lrange(key, start: int, end: int) -> list:
    try:
        result = __client__.redis_client.lrange(key, start, end)
        return list(map(lambda x: x.decode(), result))
    except (ReadOnlyError, ConnectionError):
        logging.warn(traceback.format_exc())
        __client__.redis_client._reconnect_redis_master()
        return lrange(key, start, end)


def _convert_to_string_from_bytes(data):
    if data is None:
        return None
    if isinstance(data, bytes):
        return data.decode()
    elif isinstance(data, dict):
        return _decode_dict(data)
    return data


def _decode_dict(data: dict):
    result = {}
    for d in data.items():
        key = d[0]
        value = d[1]
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(value, bytes):
            value = value.decode()
        result[key] = value
    return result