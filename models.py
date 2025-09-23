class PpcBoss:
    def __init__(self, id, name, imgUrl):
        self.id = id
        self.name = name
        self.imgUrl = imgUrl

    @staticmethod
    def jsonParsing(json):
        return PpcBoss(id=json["id"], name=json["name"], imgUrl=json["icon"])

    def to_dict(self):
        return {"id": self.id, "name": self.name, "imgUrl": self.imgUrl}
