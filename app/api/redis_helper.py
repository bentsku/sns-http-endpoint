from app import user_store as u_store


EXPIRE_LOGS = 3600
EXPIRE_DELETED = 3600 / 4
SESSION_LENGTH = 32


def _e(token: str):
    return f"endpoint:{token}"


def _dle(token: str):
    return f"endpoint:{token}:deleted"


def get_logs_from_endpoint(token: str):
    r_key = _e(token)
    pipe = u_store.pipeline()
    rv, exp = pipe.lrange(r_key, 0, -1).expire(r_key, EXPIRE_LOGS).execute()
    if not rv:
        return None
    return rv


def add_logs_to_endpoint(token: str, log_data: str):
    r_key = _e(token)
    pipe = u_store.pipeline()
    rv, exp = pipe.rpush(r_key, log_data).expire(r_key, EXPIRE_LOGS).execute()
    if not rv:
        return None
    return rv


def add_deleted_endpoint(token: str):
    r_key = _dle(token)
    return u_store.set(r_key, "1", ex=EXPIRE_DELETED)


def is_deleted_endpoint(token: str):
    r_key = _dle(token)
    return u_store.exists(r_key)
