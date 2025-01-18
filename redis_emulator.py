import json
from collections import defaultdict, OrderedDict
import time
import threading


class RedisEmulator:

    def __init__(self, max_memory=100, save_file="data.json"):
        self.max_memory = max_memory

        # replacing (map + linkedlist) by ordered dict
        self.data = OrderedDict()
        self.ttl = defaultdict(int)
        self.max_memory = max_memory
        self.save_file = save_file
        self.data_lock = threading.Lock()
        self.file_lock = threading.Lock()

    def _evict(self):
        while len(self.data) > self.max_memory:
            # reinserting at the back of orderedDict
            key, value = self.data.popitem(last=False)
            if key in self.ttl:
                del self.ttl[key]

    def _get_current_time_in_seconds(self):
        return int(time.time())

    def set(self, key, value, ttl=3000):
        with self.data_lock:
            if key in self.data:
                self.data.move_to_end(key)
            self.data[key] = value
            self.ttl[key] = self._get_current_time_in_seconds() + int(ttl)
            self._evict()
            return value

    def get(self, key):
        current_time = self._get_current_time_in_seconds()
        with self.data_lock:
            if key in self.data and current_time <= self.ttl.get(key, 0):
                self.data.move_to_end(key)
                return self.data[key]

            if key in self.data:
                del self.data[key]
                if key in self.ttl:
                    del self.ttl[key]

            return None

    def delete(self, key):
        with self.data_lock:
            if key in self.data:
                del self.data[key]
                if key in self.ttl:
                    del self.ttl[key]
                return True
            return False

    def hset(self, hname, key, value, expiry=0):
        with self.data_lock:
            if hname not in self.data:
                self.data[hname] = {}
            self.data[hname][key] = value
            ttl_key = hname + "_" + key
            self.ttl[ttl_key] = self._get_current_time_in_seconds() + int(expiry)

    def hget(self, hname, key):
        current_time = self._get_current_time_in_seconds()
        with self.data_lock:
            ttl_key = hname + "_" + key
            if hname in self.data:
                if key in self.data[hname] and current_time <= self.ttl.get(ttl_key, 0):
                    return self.data[hname][key]

                if key in self.data[hname]:
                    del self.data[hname][key]
                    del self.ttl[ttl_key]

            return None

    def save_to_file(self, filepath=None):
        with self.file_lock:
            if not filepath:
                filepath = self.save_file
            content = {
                "data": self.data,
                "ttl": self.ttl,
            }

            try:
                with open(filepath, "w") as f:
                    json.dump(content, f)
                    print(" Successfully saved data to file: " + filepath)
                    return
            except Exception as e:
                print(" Failed to save data to file: " + filepath)
                print(e)

    def load_from_file(self, filepath):
        with self.file_lock:
            if not filepath:
                filepath = self.save_file
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    current_time = self._get_current_time_in_seconds()
                    self.data = OrderedDict(data["data"])
                    self.ttl = {key: ttl for key, ttl in data["ttl"].items() if ttl > current_time}

            except Exception as e:
                print(e)
                self.data = OrderedDict()
                self.ttl = {}


def test_redis_emulator():
    redis = RedisEmulator()
    # Test 1: Basic set and get
    redis.set("name", "Alice")
    assert redis.get("name") == "Alice", "Test 1 Failed: Basic set/get not working"
    assert redis.get("age") is None, "Test 1 Failed: Non-existent key should return None"

    # Test 2: Key expiration
    redis.set("session", "12345", ttl=2)
    time.sleep(3)
    assert redis.get("session") is None, "Test 2 Failed: TTL expiration not working"

    # Test 3: Hash set and get
    redis.hset("user:1000", "name", "Bob")
    redis.hset("user:1000", "age", "30")
    assert redis.hget("user:1000", "name") == "Bob", "Test 3 Failed: Hash set/get not working"
    assert redis.hget("user:1000", "email") is None, "Test 3 Failed: Non-existent field should return None"

    # Test 4: Nested hash (Optional)
    redis.hset("user:1000", "profile", {"city": "New York", "country": "USA"})
    assert redis.hget("user:1000", "profile") == {"city": "New York", "country": "USA"}, "Test 4 Failed: Nested hash not working"


    # Test 5: Memory limit and eviction policy
    redis = RedisEmulator(max_memory=3)
    redis.set("key1", "value1")
    redis.set("key2", "value2")
    redis.set("key3", "value3")
    redis.set("key4", "value4")  # Should evict "key1"
    assert redis.get("key1") is None, "Test 5 Failed: LRU eviction not working"
    assert redis.get("key2") == "value2", "Test 5 Failed: Key should not be evicted incorrectly"

    # Test 6: Persistence
    redis.save_to_file("test_dump.rdb")
    redis.load_from_file("test_dump.rdb")
    assert redis.get("key2") == "value2", "Test 6 Failed: Persistence (load) not working"
    assert redis.get("key1") is None, "Test 6 Failed: Persistence (eviction state) not maintained"

    redis = RedisEmulator()

    def worker(redis_instance, key, value):
        redis_instance.set(key, value)

    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(redis, f"concurrent_key_{i}", f"value_{i}"))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for i in range(5):
        assert redis.get(f"concurrent_key_{i}") == f"value_{i}", f"Test 7 Failed: Concurrency issue with key concurrent_key_{i}"

    print("All tests passed!")