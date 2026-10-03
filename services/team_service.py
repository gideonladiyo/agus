import csv
import io
import re
from urllib.parse import quote

import pymupdf
import requests
from PIL import Image, ImageChops

from config import baseConfig


class TeamNotFound(LookupError):
    pass


class TeamService:
    sheet_name = "meta_team"
    extra_area = "F42:J44"
    section_areas = {"meta": "A1:J44", "f2p": "L1:U44"}
    export_options = {
        "format": "pdf",
        "size": "7",
        "portrait": "false",
        "scale": "4",
        "gridlines": "false",
        "sheetnames": "false",
        "printtitle": "false",
        "pagenum": "UNDEFINED",
        "top_margin": "0",
        "bottom_margin": "0",
        "left_margin": "0",
        "right_margin": "0",
    }

    def _read_team_rows(self):
        url = (
            f"https://docs.google.com/spreadsheets/d/{baseConfig.teamSpreadsheetId}"
            f"/gviz/tq?tqx=out:csv&sheet={quote(self.sheet_name)}"
        )
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text.lstrip("\ufeff")))
        headers = {str(name).strip().lower() for name in (reader.fieldnames or [])}
        if not {"element", "mode", "area"}.issubset(headers):
            raise ValueError("meta_team harus memiliki kolom element, mode, area")
        return list(reader)

    def get_team_image(self, element, mode):
        rows = self._read_team_rows()
        areas = []
        include_extra = False
        for row in rows:
            normalized = {str(key).strip().lower(): value for key, value in row.items() if key}
            if (
                str(normalized.get("element", "")).strip().casefold() == element.strip().casefold()
                and str(normalized.get("mode", "")).strip().casefold() == mode.strip().casefold()
            ):
                areas.extend(
                    area.strip()
                    for area in re.split(r"[;,|]", str(normalized.get("area", "")))
                    if area.strip()
                )
                include_extra |= str(normalized.get("include_extra", "")).strip().casefold() in {
                    "true", "1", "yes", "ya"
                }

        if not areas:
            raise TeamNotFound
        if include_extra:
            areas.append(self.extra_area)

        images = [self._render_area(area) for area in areas]
        width = max(image.width for image in images)
        gap = 12
        height = sum(image.height for image in images) + gap * (len(images) - 1)
        result = Image.new("RGB", (width, height), "white")
        y = 0
        for image in images:
            result.paste(image, ((width - image.width) // 2, y))
            y += image.height + gap

        output = io.BytesIO()
        result.save(output, format="PNG", optimize=True)
        return output.getvalue()

    def get_team_section_image(self, section):
        area = self.section_areas.get(section.strip().casefold())
        if area is None:
            raise TeamNotFound

        output = io.BytesIO()
        self._render_area(area).save(output, format="PNG", optimize=True)
        return output.getvalue()

    def _render_area(self, area):
        match = re.fullmatch(r"\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)", area.upper())
        if not match:
            raise ValueError(f"Range tidak valid di kolom area: {area}")

        start_col, start_row, end_col, end_row = match.groups()
        start_row, end_row = int(start_row), int(end_row)
        start_col, end_col = self._column_number(start_col), self._column_number(end_col)
        if start_row < 1 or end_row < start_row or end_col < start_col:
            raise ValueError(f"Range tidak valid di kolom area: {area}")

        params = {
            **self.export_options,
            "gid": baseConfig.teamSheetGid,
            "range": area.upper(),
            "r1": str(start_row - 1),
            "c1": str(start_col - 1),
            "r2": str(end_row),
            "c2": str(end_col),
        }
        url = f"https://docs.google.com/spreadsheets/d/{baseConfig.teamImageSpreadsheetId}/export"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        if not response.content.startswith(b"%PDF"):
            raise ValueError("Google Sheets tidak mengembalikan PDF; periksa akses spreadsheet.")

        with pymupdf.open(stream=response.content, filetype="pdf") as document:
            if not document.page_count:
                raise ValueError(f"PDF kosong untuk range {area}")
            pixmap = document[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGB")

        difference = ImageChops.difference(image, Image.new("RGB", image.size, "white"))
        content = difference.convert("L").point(lambda pixel: 255 if pixel > 12 else 0)
        bounds = content.getbbox()
        if bounds is None:
            raise ValueError(f"Tidak ada gambar pada range {area}")

        padding = 8
        left, top, right, bottom = bounds
        return image.crop((
            max(0, left - padding),
            max(0, top - padding),
            min(image.width, right + padding),
            min(image.height, bottom + padding),
        ))

    @staticmethod
    def _column_number(column):
        number = 0
        for letter in column:
            number = number * 26 + ord(letter) - ord("A") + 1
        return number


team_service = TeamService()
