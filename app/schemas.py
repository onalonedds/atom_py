from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    person_name: str
    company_name: str
    email: EmailStr


class ClientCreate(ClientBase):
    password: str


# class ClientResponse(ClientBase):
#     client_id: int
#
#     class Config:
#         from_attributes = True


class ClientResponse(BaseModel):
    email: EmailStr
    person_name: str


class ClientLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
