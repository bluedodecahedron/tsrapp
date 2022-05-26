from ninja import Schema


class UserSchema(Schema):
    username: str
    password: str

    def __str__(self):
        return '{username='+self.username+'}'


