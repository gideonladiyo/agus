from config import baseConfig


class PpcBoss:
    def __init__(self, id, name, imgUrl):
        self.id = id
        self.name = name
        self.imgUrl = imgUrl

    @staticmethod
    def parsing_json(json):
        return PpcBoss(
            id=json["id"],
            name=json["name"],
            imgUrl=baseConfig.baseImgUrl + json["icon"] + ".webp",
        )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "imgUrl": self.imgUrl}

class PpcModel:
    def __init__(self, server, activity, start, end, bosses):
        self.server = server
        self.activity = activity
        self.start = (start,)
        self.end = end
        self.bosses = bosses

    @staticmethod
    def parsing_json(json):
        ppc = json["data"]["ppc"]
        return PpcModel(
            server=ppc["server"],
            activity=ppc["activity"],
            start=ppc["start"],
            end=ppc["end"],
            bosses=[PpcBoss.parsing_json(b).to_dict() for b in ppc["bosses"]],
        )

    def to_dict(self):
        return {
            "server": self.server,
            "activity": self.activity,
            "start": self.start,
            "end": self.end,
            "bosses": self.bosses,
        }
