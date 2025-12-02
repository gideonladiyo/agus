import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin


class GrayRavensScraper:
    def __init__(self):
        self.base_url = "https://grayravens.com"
        self.characters_url = "https://grayravens.com/wiki/Characters"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_character_links(self):
        """Mengambil semua link karakter dari halaman Characters"""
        print("Mengambil daftar karakter...")
        response = self.session.get(self.characters_url)
        soup = BeautifulSoup(response.content, "html.parser")

        character_links = []
        # Mencari semua div dengan class character_icon_div
        character_divs = soup.find_all("div", class_="character_icon_div")

        for div in character_divs:
            link = div.find("a")
            if link and link.get("href"):
                full_url = urljoin(self.base_url, link["href"])
                character_name = link.get("title", "Unknown")
                character_links.append({"name": character_name, "url": full_url})

        print(f"Ditemukan {len(character_links)} karakter")
        return character_links

    def scrape_character_skills(self, soup):
        """Mengambil data Skills & Passives dari halaman karakter"""
        skills_data = []

        # Mencari section Skills & Passives
        skills_header = soup.find(
            ["h2", "h3", "span"], string=lambda text: text and "Skills" in text
        )

        if skills_header:
            # Mencari tabel atau div yang berisi skills
            current = skills_header.find_parent()
            while current:
                current = current.find_next_sibling()
                if not current:
                    break

                # Cek jika menemukan header baru (berhenti)
                if current.name in ["h2", "h3"] and "Skills" not in current.get_text():
                    break

                # Ambil data dari tabel
                tables = (
                    current.find_all("table") if current.name != "table" else [current]
                )
                for table in tables:
                    rows = table.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["td", "th"])
                        if len(cells) >= 2:
                            skill_name = cells[0].get_text(strip=True)
                            skill_desc = cells[-1].get_text(strip=True)
                            if skill_name and skill_desc:
                                skills_data.append(
                                    {"name": skill_name, "description": skill_desc}
                                )

        return skills_data

    def scrape_character_leap(self, soup):
        """Mengambil data Character Leap dari halaman karakter"""
        leap_data = []

        # Mencari section Character Leap
        leap_header = soup.find(
            ["h2", "h3", "span"], string=lambda text: text and "Leap" in text
        )

        if leap_header:
            current = leap_header.find_parent()
            while current:
                current = current.find_next_sibling()
                if not current:
                    break

                # Cek jika menemukan header baru
                if current.name in ["h2", "h3"] and "Leap" not in current.get_text():
                    break

                # Ambil data dari tabel atau list
                tables = (
                    current.find_all("table") if current.name != "table" else [current]
                )
                for table in tables:
                    rows = table.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["td", "th"])
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if any(row_data):  # Jika ada data
                                leap_data.append(row_data)

                # Juga cek list items
                list_items = current.find_all("li")
                for item in list_items:
                    text = item.get_text(strip=True)
                    if text:
                        leap_data.append(text)

        return leap_data

    def scrape_character_page(self, character_info):
        """Scraping data lengkap dari satu halaman karakter"""
        print(f"Scraping: {character_info['name']}...")

        try:
            response = self.session.get(character_info["url"])
            soup = BeautifulSoup(response.content, "html.parser")

            # Ambil skills dan leap data
            skills = self.scrape_character_skills(soup)
            leap = self.scrape_character_leap(soup)

            return {
                "name": character_info["name"],
                "url": character_info["url"],
                "skills_and_passives": skills,
                "character_leap": leap,
            }

        except Exception as e:
            print(f"Error scraping {character_info['name']}: {str(e)}")
            return None

    def scrape_all_characters(self, limit=None):
        """Scraping semua karakter"""
        character_links = self.get_character_links()

        if limit:
            character_links = character_links[:limit]

        all_data = []

        for i, char_info in enumerate(character_links, 1):
            print(f"\n[{i}/{len(character_links)}]")
            data = self.scrape_character_page(char_info)

            if data:
                all_data.append(data)

            # Delay untuk tidak membebani server
            time.sleep(1)

        return all_data

    def save_to_json(self, data, filename="grayravens_data.json"):
        """Menyimpan data ke file JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nData berhasil disimpan ke {filename}")

    def save_to_csv(self, data, filename="grayravens_data.csv"):
        """Menyimpan data ke file CSV"""
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Character Name", "URL", "Skills Count", "Skills", "Character Leap"]
            )

            for char in data:
                skills_text = " | ".join(
                    [
                        f"{s['name']}: {s['description']}"
                        for s in char.get("skills_and_passives", [])
                    ]
                )
                leap_text = " | ".join(
                    [str(item) for item in char.get("character_leap", [])]
                )

                writer.writerow(
                    [
                        char["name"],
                        char["url"],
                        len(char.get("skills_and_passives", [])),
                        skills_text,
                        leap_text,
                    ]
                )

        print(f"Data berhasil disimpan ke {filename}")


def main():
    scraper = GrayRavensScraper()

    print("=== Gray Ravens Character Scraper ===\n")
    print("Pilihan:")
    print("1. Scrape semua karakter")
    print("2. Scrape beberapa karakter pertama (test)")
    print("3. Hanya ambil list karakter")

    choice = input("\nPilih (1/2/3): ").strip()

    if choice == "1":
        data = scraper.scrape_all_characters()
        scraper.save_to_json(data)
        scraper.save_to_csv(data)

    elif choice == "2":
        limit = int(input("Berapa karakter yang ingin di-scrape? "))
        data = scraper.scrape_all_characters(limit=limit)
        scraper.save_to_json(data, "grayravens_sample.json")
        scraper.save_to_csv(data, "grayravens_sample.csv")

    elif choice == "3":
        characters = scraper.get_character_links()
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char['name']} - {char['url']}")

    else:
        print("Pilihan tidak valid")


if __name__ == "__main__":
    main()
