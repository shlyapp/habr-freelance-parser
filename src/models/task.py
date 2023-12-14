from typing import List
from pydantic import BaseModel


class Task(BaseModel):
    title: str
    id: int
    link: str
    views: int
    responses: int
    price: int
    tags: List[str]
