def ppc_type_parse(type: str):
    type_map = {
        "ultimate": 4,
        "advanced": 3
    }
    return type_map.get(type.lower(), None)