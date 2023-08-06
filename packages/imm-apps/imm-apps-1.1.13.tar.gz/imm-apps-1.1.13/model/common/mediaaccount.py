from pydantic import BaseModel
from typing import Optional

class MediaAccount(BaseModel):
    media:Optional[str]
    account:Optional[str]
    password:Optional[str]
    security_answer:Optional[str]
    remark:Optional[str]
    