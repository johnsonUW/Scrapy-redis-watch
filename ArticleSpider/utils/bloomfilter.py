from random import randint
import mmh3
import BitVector
import redis
import math
import time



class BloomFilter():
    #100 seeds.
    SEEDS = []
    for _ in range(100):
        SEEDS.append(randint(0, 1000))

    #capacity
    #error_rate
    #conn
    #key
    def __init__(self, capacity=1000000000, error_rate=0.00000001, conn=None, key='BloomFilter'):
        self.m = math.ceil(capacity*math.log2(math.e)*math.log2(1/error_rate))
        self.k = math.ceil(math.log1p(2)*self.m/capacity)
        self.mem = math.ceil(self.m/8/1024/1024)
        self.blocknum = math.ceil(self.mem/512)
        self.seeds = self.SEEDS[0:self.k]
        self.key = key
        self.N = 2**31-1
        self.redis = conn
        if not self.redis:

            self.bitset = BitVector.BitVector(size=1<<32)
        print(self.mem)
        print(self.k)

    def add(self, value):
        name = self.key + "_" + str(ord(value[0])%self.blocknum)
        hashs = self.get_hashs(value)
        for hash in hashs:
            if self.redis:
                self.redis.setbit(name, hash, 1)
            else:
                self.bitset[hash] = 1

    def is_exist(self, value):
        name = self.key + "_" + str(ord(value[0])%self.blocknum)
        hashs = self.get_hashs(value)
        exist = True
        for hash in hashs:
            if self.redis:
                exist = exist & self.redis.getbit(name, hash)
            else:
                exist = exist & self.bitset[hash]
        return exist

    def get_hashs(self, value):
        hashs = list()
        for seed in self.seeds:
            hash = mmh3.hash(value, seed)
            if hash >= 0:
                hashs.append(hash)
            else:
                hashs.append(self.N - hash)
        return hashs


pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
conn = redis.StrictRedis(connection_pool=pool)

start = time.time()
bf = BloomFilter(conn=conn)
bf.add('test')
bf.add('fsest1')
print(bf.is_exist('qest'))
print(bf.is_exist('testdsad'))
end = time.time()
print(end-start)