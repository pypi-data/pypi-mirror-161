import os


def get_env_extra():
    res = {
        "request_id": "LOGTMP-X-REQUEST-ID",
        "progname": "LOGTMP-PROGNAME",
    }
    env_extra_str = os.environ.get("LOG_ENV_EXTRA")
    if env_extra_str:
        extra_list = env_extra_str.split(",")
        for extra in extra_list:
            key, val = extra.split(":")
            res[key.strip()] = val.strip()
    return res


def get_extra_from_environ():
    res = {}
    for key, ename in get_env_extra().items():
        value = os.environ.get(ename)
        if value:
            res[key] = value
    return res


def set_extra_to_environ(key, value):
    os.environ[get_env_extra().get(key, key)] = value
