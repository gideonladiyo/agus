from PIL import Image
import requests
from io import BytesIO

def ppc_type_parse(type: str):
    type_map = {
        "ultimate": 4,
        "advanced": 3
    }
    return type_map.get(type.lower(), None)

def server_map(server):
    servers = {
        "asia": "ap",
        "korea": "kr",
        "china": "cn",
        "japan": "jp" 
    }
    return servers.get(type.lower(), None)


def merge_images_horizontal(urls):
    from PIL import Image
    import requests

    images = [Image.open(BytesIO(requests.get(url).content)) for url in urls]
    min_height = min(img.height for img in images)
    resized = [
        img.resize((int(img.width * min_height / img.height), min_height))
        for img in images
    ]

    total_width = sum(img.width for img in resized)
    new_im = Image.new("RGB", (total_width, min_height))

    x_offset = 0
    for img in resized:
        new_im.paste(img, (x_offset, 0))
        x_offset += img.width

    output = BytesIO()
    new_im.save(output, format="PNG")
    output.seek(0)
    return output
