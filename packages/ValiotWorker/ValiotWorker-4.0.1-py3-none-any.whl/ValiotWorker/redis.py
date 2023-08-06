import pydash as __
import time
from .Logging import LogLevel
from pygqlc import GraphQLClient
from multiprocessing import Event
import redis

DEFAULT_REDIS_CONFIG = {
  "host": 'localhost', 
  "port": 6379,
  "db": 0,
  "url": ""
}

class WorkerRedis():
    def __init__(self):
        self.redisConfig = DEFAULT_REDIS_CONFIG
        self.redis = None
        self.connected = Event()
        self.connected.clear()
        self.startTime = None
        self.redisSubscriptions = []
        self.runningSubscriptions = []
        self.log = None
        self.gql = GraphQLClient()

    def setRedisConfig(self, host='localhost', port=6379, db=0, url=""):
        REDIS_CONFIG = {
            "host": host, 
            "port": port,
            "db": db,
            "url": url
        }
        self.redisConfig = REDIS_CONFIG

    def setRedisConnection(self):
        if self.redisConfig['url']:
            self.redis = redis.Redis.from_url(self.redisConfig['url'])
        else:
            self.redis = redis.Redis(host = self.redisConfig['host'], 
                            port=self.redisConfig['port'], 
                            db=self.redisConfig['db'])

    def setLog(self, log):
        self.log = log

    def getClient(self):
        return self.redis

    def isConnected(self):
        return self.connected.is_set()
        
    def setRedisSubscriptions(self, name=None, subscription=None, key=None, value=None, prefix=None, suffix=None, reconnectionTime=600):
        if name and subscription and key and value:
            sub = {'name': name, 
                   'subscription': subscription, 
                   'key': key, 
                   'value': value,
                   'prefix': prefix,
                   'suffix': suffix,
                   'reconnectionTime': reconnectionTime}
            self.redisSubscriptions.append(sub)

    def createCallbackRedisFunction(self, name, dkey, dvalue, prefix, suffix, expireTime):
        def callbackRedisFunction(message):
            key = __.get(message, dkey, None)
            value = __.get(message, dvalue, None)
            
            if key and (value is not None):
                if prefix:
                    key = prefix + '_' + key
                if suffix:
                    key = key + '_' + suffix
                self.redis.set(key, value)
                self.redis.publish(key, value)
                self.redis.set(name, 'Alive')
                self.redis.expire(name, expireTime)
            else: 
                self.log(LogLevel.ERROR, f'Not {dkey} or {dvalue} in {name} subscription')
        return callbackRedisFunction

    
    def initializeSubscription(self, redisSub):
        callbackRedisFunction = self.createCallbackRedisFunction(redisSub['name'], redisSub['key'], redisSub['value'],
                                                                 redisSub['prefix'], redisSub['suffix'], redisSub['reconnectionTime'])
        unsub = self.gql.subscribe(query=redisSub['subscription'], callback=callbackRedisFunction)
        name =  redisSub['name']
        if (unsub):
            self.log(LogLevel.SUCCESS, f'Initialize Redis subscription: {name}')
            runningSup = {'redisSub': redisSub, 'unsub': unsub}
            self.runningSubscriptions.append(runningSup)
            self.redis.set(redisSub['name'], 'Alive')
            self.redis.expire(redisSub['name'], redisSub['reconnectionTime'])
        else:
            self.log(LogLevel.ERROR, f'ERROR Initialize Redis subscription: {name}')


    def initializeRedis(self):
        self.log(LogLevel.INFO, 'Worker using Redis service')
        self.setRedisConnection()
        try:
            ping = self.redis.ping()
            self.log(LogLevel.SUCCESS, f'Redis ping - {ping}')
        except:
            self.log(LogLevel.ERROR, 'Redis connection error, check connection parameters')
            self.startTime = time.time()
            self.connected.clear()
            return
    
        self.redis.flushall()  

        for redisSub in self.redisSubscriptions:
            self.initializeSubscription(redisSub)
        self.connected.set()
        self.log(LogLevel.SUCCESS, 'Redis Worker is connected')
        
    def monitorRedisSubscriptions(self):
        if not self.isConnected():
            self.waitingRedisConnection()
            return
        
        for idx, sub in enumerate(self.runningSubscriptions):
            isVarRedis = self.redis.exists(sub['redisSub']['name'])
            name = sub['redisSub']['name']
            if not self.redis.exists(sub['redisSub']['name']):
                name = sub['redisSub']['name']
                self.log(LogLevel.WARNING, f'Redis subscription {name} expired time')
                self.gql.resetSubsConnection()
                self.redis.set(name, 'Alive')
                self.redis.expire(name, sub['redisSub']['reconnectionTime'])
                self.log(LogLevel.INFO, f'Connecting Redis subscription: {name} ...')

    def waitingRedisConnection(self):
        waitingTime = time.time() - self.startTime
        if waitingTime > 30:
            self.initializeRedis()

            
