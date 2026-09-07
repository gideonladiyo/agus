from services.api_service import api_service

class MemoriesService:
    def __init__(self):
        pass
    
    def getMemoris(self):
        res = api_service.get_memories()
        if not res or res.get("status") != "success" or "data" not in res:
            return []
        return res["data"].get("memories", [])
    
    def getMemory(self, slug):
        clean_slug = str(slug).strip().lower().replace(" ", "-")
        res = api_service.get_memory(clean_slug)
        if not res or res.get("status") != "success" or "data" not in res:
            return None
        data = res["data"]
        return {
            "name": data.get("name"),
            "icon": data.get("icons", [{}])[0] if data.get("icons") else {},
            "skills": data.get("skills", []),
            "description": data.get("description"),
            "quality": data.get("quality"),
        }

memories_service = MemoriesService()