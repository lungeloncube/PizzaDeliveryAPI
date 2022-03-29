from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'johndoe',
                'email': 'johndoe@gmail.com',
                'password': 'password',
                'is_staff': False,
                'is_active': True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = '51280b8c470bb4ae1a12551d5ddeb4d22b24edf037bbde450915d4433f8dcd7d'


class LoginModel(BaseModel):
    username: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = 'PENDING'
    pizza_sizes: Optional[str] = 'SMALL'
    user_id: Optional[int]

    class Config:
        orm_mode: True
        schema_extra = {'example': {
            'quantity': 2,
            "pizza_sizes": 'LARGE'

        }}


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = 'PENDING'

    class Config:
        orm_mode: True
        schema_extra = {'example': {
            'order_status': 'PENDING'
        }}
