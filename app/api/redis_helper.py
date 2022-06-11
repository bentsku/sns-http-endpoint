from app import user_store as u_store


EXPIRE_LOGS = 3600
EXPIRE_DELETED = 3600 / 4
# time for AWS to delete a pending subscription that hasn't been confirmed
EXPIRE_PENDING = 3600 * 24 * 3
SESSION_LENGTH = 32
ALL_PENDING_KEY = 'global:pending'


def _e(token: str):
    return f"endpoint:{token}"


def _dle(token: str):
    return f"endpoint:{token}:deleted"


def _pe(token: str):
    return f"endpoint:{token}:pending"


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


def add_endpoint_as_pending(token: str):
    r_key = _pe(token)
    pipe = u_store.pipeline()
    pipe.set(r_key, "1", ex=EXPIRE_PENDING).sadd(ALL_PENDING_KEY, token)
    return pipe.execute()


def del_endpoint_as_pending(token: str):
    r_key = _pe(token)
    pipe = u_store.pipeline()
    pipe.delete(r_key).srem(ALL_PENDING_KEY, token)
    return pipe.execute()


def get_all_pending():
    pending_list = [pending_endpoint for pending_endpoint in u_store.sscan_iter(ALL_PENDING_KEY)]
    pipe = u_store.pipeline()
    for pending_endpoint in pending_list:
        pipe.get(_pe(pending_endpoint))

    data_resp = pipe.execute()
    pending_endpoints = []
    expired = []
    for index, pending_endpoint_uid in enumerate(data_resp):
        if pending_endpoint_uid:
            pending_endpoints.append(pending_endpoint_uid)
        else:
            expired.append(pending_list[index])

    if expired:
        u_store.srem(ALL_PENDING_KEY, *expired)

    return pending_endpoints
