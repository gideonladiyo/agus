from PIL import Image
import requests
from io import BytesIO

def ppc_type_parse(type: str):
    type_map = {
        "ultimate": 4,
        "advanced": 3
    }
    return type_map.get(type.lower(), None)


def merge_images_horizontal(urls, output_file="merged.png"):
    # Ambil semua gambar dari URL
    images = [Image.open(BytesIO(requests.get(url).content)) for url in urls]

    # Samakan tinggi gambar agar rapi
    heights = [img.height for img in images]
    min_height = min(heights)
    resized = [
        img.resize((int(img.width * min_height / img.height), min_height))
        for img in images
    ]

    # Hitung total ukuran canvas
    total_width = sum(img.width for img in resized)
    new_im = Image.new("RGB", (total_width, min_height))

    # Tempel satu per satu
    x_offset = 0
    for img in resized:
        new_im.paste(img, (x_offset, 0))
        x_offset += img.width

    # Simpan hasil
    new_im.save(output_file)
    return output_file