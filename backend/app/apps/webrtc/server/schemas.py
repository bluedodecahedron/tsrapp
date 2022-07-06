from ninja import Schema


class OfferSchema(Schema):
    sdp: str
    type: str
    video_transform: str

    def __str__(self):
        return '{' + \
               'sdp=' + self.sdp + \
               ', type=' + self.type + \
               ', video_transform=' + self.video_transform + \
               '}'


class AnswerSchema(Schema):
    sdp: str
    type: str

    def __str__(self):
        return '{' + \
               'sdp=' + self.sdp + \
               ', type=' + self.type + \
               '}'


class Detail(Schema):
    detail: str
