import logging


class RedisORM:

    def __init__(self, logger: logging, redis):
        self.__logger = logger
        self.__host = None
        self.__port = None
        self.__db_index = 0
        self.__password = None
        self.__connection = None
        self.__redis = redis

    def config(self, host=None, port=None, password=None, db_index=None):
        self.__host = host
        self.__port = port
        self.__password = password
        self.__db_index = db_index
        self.__connection = self.__redis.StrictRedis(host=self.__host,
                                                     port=self.__port,
                                                     password=self.__password,
                                                     decode_responses=True,
                                                     db=self.__db_index)

    def set_value(self, key: str, value: str, ttl=0):
        self.__connection.set(key, value) if not ttl else self.__connection.set(key, value, ex=ttl)
        return True

    def set_hash_from_dict(self, key: str, data: dict):
        p = self.__connection.pipeline()
        p.hset(key, mapping=data)
        p.execute()

    def delete_value(self, key: str):
        self.__connection.delete(key)

    def get_value(self, key: str) -> str:
        return self.__connection.get(key)

    def get_value_by_index(self, key: str, index: str) -> str:
        return self.__connection.hget(key, index)

    def get_all_keys(self) -> list:
        return self.__connection.keys()

    def get_hash_by_key(self, key: str) -> dict:
        return self.__connection.hgetall(key)

    def get_used_memory(self) -> int:
        return self.__connection.info()['used_memory']

    def get_db_size(self) -> int:
        return self.__connection.dbsize()

    def remove_key_from_hash(self, index: str, key: str):
        p = self.__connection.pipeline()
        p.hdel(index, key)
        p.execute()

    def remove_all_data_use_really_carefully(self):
        self.__connection.flushall()

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def db_index(self) -> int:
        return self.__db_index

    @property
    def connection(self):
        return self.__connection

    @property
    def __pipeline(self):
        return self.__connection.pipeline()
