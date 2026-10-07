from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccessLogRecord:
    ip: str
    timestamp: datetime
    method: str
    url: str
    protocol: str
    status_code: int
    response_size: int
    referer: str
    user_agent: str