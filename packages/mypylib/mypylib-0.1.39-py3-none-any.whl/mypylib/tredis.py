import redis
import threading
from loguru import logger
import traceback


class Tredis(threading.Thread):
    default_port = 6379
    default_db = 0

    class base_tredis_msg_sender:
        def __init__(self):
            self.tredis: Tredis = None

        def redis_msg_sender(self, data):
            print(f'This is what I got: {data}')
            if self.tredis is not None and self.tredis.r is not None:
                ret = self.tredis.r.get(data)
                if ret is not None:
                    print(f'This is what I have found {ret} {type(ret)}')
                else:
                    print(f'Cannot find {data} on server')

    def __init__(self, server, port, db, password, channel, prefix, redis_msg_sender):
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.db = db
        self.password = password
        self.channel = channel
        self.prefix = prefix
        self.redis_msg_sender = redis_msg_sender
        self.r: redis.client.Redis = None
        self.str_thread_exit_magic = 'redis thread exit'

        self.start()

    def run(self):
        t = threading.current_thread()
        # For test
        # r = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
        self.r = redis.StrictRedis(host=self.server,
                                   port=self.port,
                                   db=self.db,
                                   charset="utf-8",
                                   decode_responses=True,
                                   password=self.password)

        logger.info(f'Redis connected to {self.server}, port {self.port}, db: {self.db}')
        sub: redis.client.PubSub = self.r.pubsub()
        logger.info(f'Redis subscribe to channel [{self.channel}]')
        sub.subscribe(self.channel)
        for message in sub.listen():
            if message:
                logger.info(f'REDIS got message: [{message}]')
                try:
                    data = message['data']
                    logger.info(f'redis_working_thread got msg: {data}')

                    if data == self.str_thread_exit_magic:
                        break
                    else:
                        function_send = getattr(self.redis_msg_sender, 'redis_msg_sender', None)
                        if function_send is not None and callable(function_send):
                            function_send(data)
                except Exception as e:
                    traceback.print_exc()
                    logger.exception(f'\033[1;33mredis subscribe\n{message}\n{e}\033[0m')
        logger.info(f'redis thread: {self} stopped.')

    @logger.catch()
    def stop(self):
        t = threading.current_thread()
        self.r.publish(self.channel, self.str_thread_exit_magic)


