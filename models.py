from config import baseConfig

# ================ PPC =========================

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


# ==================== WARZONE =======================


class Buffs:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def parsing_json(json):
        return [Buffs(id=j["id"], name=j["name"], description=j["description"]) for j in json]

    def to_json(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Weathers:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @staticmethod
    def parsing_json(json):
        return [Weathers(name=j["name"], description=j["description"]) for j in json]

    def to_json(self):
        return {"name": self.name, "description": self.description}


class WarzoneItem:
    def __init__(
        self,
        id,
        name,
        description,
        buff_description,
        element,
        icon,
        buffs: Buffs,
        weathers: Weathers,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.buff_description = buff_description
        self.element = element
        self.icon = icon
        self.buffs = buffs
        self.weathers = weathers

    @staticmethod
    def parsing_json(json):
        return WarzoneItem(
            id=json["id"],
            name=json["name"],
            description=json["description"],
            buff_description=json["buffDescription"],
            element=json["element"],
            icon=json["icon"],
            buffs=Buffs.parsing_json(json["buffs"]),
            weathers=Weathers.parsing_json(json["weathers"]),
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "buff_description": self.buff_description,
            "element": self.element,
            "icon": self.icon,
            "buffs": [b.to_json() for b in self.buffs],
            "weathers": [w.to_json() for w in self.weathers],
        }


class WarzoneWeek:
    def __init__(self, server, activity, area):
        self.server = server
        self.activity = activity
        self.area = area

    @staticmethod
    def parsing_json(json):
        return WarzoneWeek(
            server=json["server"],
            activity=json["activity"],
            area=[WarzoneItem.parsing_json(j) for j in json["area"]["zones"]]
        )

    def to_json(self):
        return {
            "server": self.server,
            "activity": self.activity,
            "area": [a.to_json() for a in self.area],
        }
