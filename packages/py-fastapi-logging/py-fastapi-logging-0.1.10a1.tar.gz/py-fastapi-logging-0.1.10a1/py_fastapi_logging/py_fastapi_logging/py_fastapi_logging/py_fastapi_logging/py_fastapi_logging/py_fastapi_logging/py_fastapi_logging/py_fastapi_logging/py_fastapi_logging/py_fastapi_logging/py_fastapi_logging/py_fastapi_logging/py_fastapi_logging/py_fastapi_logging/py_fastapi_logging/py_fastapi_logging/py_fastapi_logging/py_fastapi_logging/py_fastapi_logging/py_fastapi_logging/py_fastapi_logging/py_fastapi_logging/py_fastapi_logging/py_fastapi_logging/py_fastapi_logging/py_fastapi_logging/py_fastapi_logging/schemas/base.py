from typing import Optional, TypedDict, Union


class BaseJsonLogSchema(TypedDict):
    level: int
    request_id: Optional[str]
    progname: Optional[str]
    timestamp: str
    exceptions: Union[list[str], str] = None
    tags: Optional[list[str]]
