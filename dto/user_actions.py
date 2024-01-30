from pydantic import BaseModel


class UserActionsDTO(BaseModel):
    post_id: int
    action: int
    time: str
    gender: int
    age: int
    country: str
    city: str
    os: str
    source: str
    exp_group: int