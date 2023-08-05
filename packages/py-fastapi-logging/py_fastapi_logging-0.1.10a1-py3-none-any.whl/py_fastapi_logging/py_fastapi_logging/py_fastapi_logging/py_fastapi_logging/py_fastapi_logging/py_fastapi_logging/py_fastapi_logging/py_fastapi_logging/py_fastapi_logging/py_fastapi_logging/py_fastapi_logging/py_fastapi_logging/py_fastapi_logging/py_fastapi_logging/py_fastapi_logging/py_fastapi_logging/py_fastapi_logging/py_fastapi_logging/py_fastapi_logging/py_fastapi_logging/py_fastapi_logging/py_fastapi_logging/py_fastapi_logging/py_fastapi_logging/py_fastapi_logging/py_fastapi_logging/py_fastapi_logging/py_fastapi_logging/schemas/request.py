from typing import Optional, TypedDict


class RequestPayload(TypedDict):
    method: str
    path: str
    host: str
    subject_type: Optional[str]
    subject_id: Optional[str]
    params: Optional[dict]
    body: str
