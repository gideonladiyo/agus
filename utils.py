from PIL import Image
import requests
from io import BytesIO
import aiohttp
import asyncio

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
    return servers.get(server.lower(), None)


async def fetch_image(session, url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return Image.open(BytesIO(await resp.read())).convert("RGBA")
        return None


async def merge_images_horizontal(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url) for url in urls]
        images = await asyncio.gather(*tasks)

    images = [img for img in images if img]

    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    merged = Image.new("RGBA", (total_width, max_height))
    x_offset = 0
    for img in images:
        merged.paste(img, (x_offset, 0))
        x_offset += img.width

    # return BytesIO
    bio = BytesIO()
    merged.save(bio, format="PNG")
    bio.seek(0)
    return bio
