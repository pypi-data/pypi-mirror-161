from typing import TypedDict


class ResponsePayload(TypedDict):
    status: int
    response_time: str
    response_body: str
