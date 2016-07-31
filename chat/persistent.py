import redis


class RedisPersistent:
    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
        self.instance = redis.Redis(connection_pool=pool)

    def get_persist_offline_key(self, sender, receiver):
        return sender + ":" + receiver

    def get_message_key(self, sender, receiver, message):
        return sender + ":" + receiver + ":" + message

    def save_persist_offline_messages(self, sender, receiver, message):
        """
        save offline messages for a receiver
        :param sender:
        :param receiver:
        :param message:
        """
        key = self.get_persist_offline_key(receiver, sender)
        self.instance.lpush(key, message)

    def fetch_offline_messages(self, receiver):
        """
        fetches the offline messages stored for a client
        :param receiver:
        :return:
        """
        keys = self.instance.keys(receiver + ":*")
        messages = {}
        for key in keys:
            split = key.split(":")
            sender = split[1]
            message = self.instance.lrange(key, 0 , -1)
            messages.update({sender: message})
            self.instance.delete(key)
        return messages

    def save_message(self, sender, receiver, message):
        """
        Store a key with ttl 5 seconds to check if duplicates are there
        :param sender:
        :param receiver:
        """
        key = self.get_message_key(sender, receiver, message)
        self.instance.set(key, None, ex=5)

    def check_message(self, sender, receiver, message):
        """
        check if the message from sender to receive is in redis
        :param sender:
        :param receiver:
        :param message:
        :return:
        """
        key = self.get_message_key(sender, receiver, message)
        val = self.instance.get(key)
        return val is None
