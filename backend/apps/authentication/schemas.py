from ninja import Schema


class User(Schema):
    username: str
    password: str