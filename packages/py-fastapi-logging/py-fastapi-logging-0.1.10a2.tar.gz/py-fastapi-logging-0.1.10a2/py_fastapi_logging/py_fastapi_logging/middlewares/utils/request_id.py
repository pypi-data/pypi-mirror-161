from uuid import uuid4

REQUEST_ID_HEADER = "X-Request-Id"
DEFAULT_DELIMITER = "#"


def generate_request_id(*, prefix=None, suffix=None, delimiter=DEFAULT_DELIMITER):
    prefix = f"{prefix}{delimiter}" if prefix else ""
    suffix = f"{delimiter}{suffix}" if suffix else ""
    request_id = "".join((prefix, str(uuid4()), suffix))
    return request_id
