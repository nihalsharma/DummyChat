from unittest import TestCase
import unittest
import redis


class TestChat(TestCase):
    def setUp(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
        self.instance = redis.Redis(connection_pool=pool)

    def tearDown(self):
        pass

    def test_redis_connection(self):
        """
        Simple test to see whether redis is up or not
        """
        assert self.instance.set("key", "value")
        assert self.instance.get("key") == "value"


if __name__ == "__main__":
    unittest.main()
