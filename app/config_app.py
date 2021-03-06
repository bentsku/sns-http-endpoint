import os

_REDIS_HOST = os.environ.get('REDIS_HOST') or 'redis-sns-endpoint'
_REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)


class Config(object):
    REDIS_URL = f"redis://{_REDIS_HOST}:{_REDIS_PORT}/0"
    METRICS_MEASUREMENT_NAME = os.environ.get('METRICS_MEASUREMENT_NAME') or 'flask-sns-http'
    SNS_AUTO_SUBSCRIBE = str(os.environ.get('SNS_AUTO_SUBSCRIBE')).lower() == "true"
    STATSD_HOST = os.environ.get('STATSD_HOST') or 'telegraf'
    STATSD_PORT = os.environ.get('STATSD_PORT') or '8125'
