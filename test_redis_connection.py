import redis

try:
    client = redis.StrictRedis(host='localhost', port=6380, db=0)
    client.ping()
    print("Successfully connected to Redis on port 6380!")
except redis.ConnectionError:
    print("Failed to connect to Redis on port 6380.")
