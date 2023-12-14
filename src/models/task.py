from pydantic import BaseModel

from datetime import datetime

class Task(BaseModel):
    title: str
    description: str
    id: int
    link: str
    views: int
    responses: int
    price: int
    data: datetime
