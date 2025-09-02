from pydantic import BaseModel


class DerivTokenRequest(BaseModel):
    token: str
