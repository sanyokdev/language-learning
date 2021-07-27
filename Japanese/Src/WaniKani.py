import json
import math
import re
import time
from enum import Enum
import pandas as pd

import requests
from bs4 import BeautifulSoup
from bs4 import Tag

from Japanese.Src import Helper
from Japanese.Src.Helper import DataPresets

"""
    Some Comment
"""
class GridType(Enum):
    Radical = "https://www.wanikani.com/lattice/radicals/meaning"
    Kanji = "https://www.wanikani.com/lattice/kanji/combined"
    Vocabulary = "https://www.wanikani.com/lattice/vocabulary/combined"


"""
    Some Comment
"""
class _Common:
    def __init__(self, name: str, symbol: str, url: str):
        self.name = name
        self.symbol = symbol
        self.url = url

    def get_page_soup(self, site_session: requests.sessions.Session):
        return get_page(self.url, site_session)

    def get_level(self, site_soup: BeautifulSoup):
        return site_soup.find("a", {"class": "level-icon"}).contents[0]

    def get_meaning_mnemonic(self, site_soup: BeautifulSoup):
        meaning_elements = site_soup.find("section", {"class": "mnemonic-content"}).find_all("p")
        meaning_list = []

        for element in meaning_elements:
            content = element.contents
            content_text = ""

            for item in content:
                if type(item) == Tag:
                    item_class_list = item.get("class")
                    if item_class_list is not None:
                        item_class = item_class_list[0]
                    else:
                        item_class = None

                    item_content = item.contents[0]

                    if item_class == "radical-highlight":
                        item_tag = f"<radical>{item_content}</radical>"
                    elif item_class == "kanji-highlight":
                        item_tag = f"<kanji>{item_content}</kanji>"
                    elif item_class == "vocabulary-highlight":
                        item_tag = f"<vocabulary>{item_content}</vocabulary>"
                    else:
                        item_tag = f"<jp>{item_content}</jp>"
                        
                    content_text += item_tag
                else:
                    content_text += str(item)

            meaning_list.append(content_text)
        return meaning_list

    def get_reading(self, site_soup: BeautifulSoup):
        pass

    def get_reading_meaning(self, site_soup: BeautifulSoup):
        pass

"""
    Some Comment
"""
class TimeTracker:
    def __init__(self, delay: float, total_items: int):
        self.delay = delay

        self.total_items = total_items
        self.progress = 0

        self.start_time = time.time()
        self.end_time = self.start_time
        self.prev_times = []
        self.avg_time_per_item = 0

    def start(self):
        self.start_time = time.time()
        self.progress += 1

    def end(self):
        # Delay the function so we don't request more data than the amount allowed (max is 60rpm)
        time.sleep(self.delay)

        self.end_time = time.time()
        self.prev_times.append(self.end_time - self.start_time)
        self.avg_time_per_item = sum(self.prev_times) / len(self.prev_times)

    def print_progress(self):
        time_frac, time_whole = math.modf(round((self.avg_time_per_item * (self.total_items - self.progress)) / 60, 1))
        time_min = int(time_whole)
        time_sec = int(round(time_frac * 60, 2))

        if time_min >= 60:
            time_hour = int(time_min/60)
            time_left_txt = f"Time Left: ({ time_hour }h:{ time_min - (60 * time_hour) }m:{ time_sec }s)"
        else:
            time_left_txt = f"Time Left: ({ time_min }m:{ time_sec }s)"
        prog_txt = f"Progress: ({ self.progress }/{ self.total_items })"

        print(f"{time_left_txt} | {prog_txt}")


    def print_stats(self):
        print(f"- RPM: { int(60 / self.avg_time_per_item) } | TPR: { round(self.avg_time_per_item, 2) }s\n")
        # - RPM "Requests per minute"
        # - TPR "Time per request"


class Radical(_Common):
    def get_reading(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading'")

    def get_reading_meaning(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading_meaning'")


class Kanji(_Common):
    def get_radical_combination(self, site_soup: BeautifulSoup):
        pass


class Vocabulary(_Common):
    def get_word_type(self, site_soup: BeautifulSoup):
        pass

    def get_en_context_list(self, site_soup: BeautifulSoup):
        pass

    def get_jp_context_list(self, site_soup: BeautifulSoup):
        pass


def to_item_list(data: pd.DataFrame):
    output = []
    for i in range(len(data.Name)):
        output.append(_Common(data.Name[i], data.Symbol[i], data.Url[i]))
    return output


def convert_item_type(item: _Common, item_type: GridType):
    if item_type == GridType.Radical:
        return Radical(item.name, item.symbol, item.url)
    elif item_type == GridType.Kanji:
        return Kanji(item.name, item.symbol, item.url)
    else: # GridType.Vocabulary
        return Vocabulary(item.name, item.symbol, item.url)


def get_grid_item_data(delay: float, grid_type: GridType, site_session: requests.sessions.Session):
    # Get item data from the grid page
    grid_items = to_item_list(get_grid_data(grid_type, site_session))
    item_list = [convert_item_type(item, grid_type) for item in grid_items]

    # Set up the progress tracking
    tracker = TimeTracker(delay, total_items=len(item_list))

    # Find and save the respecive data for each symbol in the grid
    output_data = {}
    for item in item_list:
        # Start the time tracking
        tracker.start()

        # Get the respecitve radical page soup
        page_soup = item.get_page_soup(site_session)

        # Find the respective radical data inside the page
        if grid_type == GridType.Radical:
            output_data = DataPresets.RADICAL.value

            output_data["Level"].append(item.get_level(page_soup))
            output_data["Symbol"].append(item.symbol)

            output_data["Meaning"].append(item.name)
            meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
            output_data["Meaning Mnemonic"].append(meaning_mnemonic)


        elif grid_type == GridType.Kanji:
            output_data = DataPresets.KANJI.value

            output_data["Level"].append(item.get_level(page_soup))
            output_data["Symbol"].append(item.symbol)

            output_data["Radical Combination"].append(item.name)

            output_data["Meaning"].append(item.name)
            meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
            output_data["Meaning Mnemonic"].append(meaning_mnemonic)

            output_data["Reading"].append(item.name)
            output_data["Reading Mnemonic"].append(item.name)

        elif grid_type == GridType.Vocabulary:
            output_data = DataPresets.VOCABULARY.value

            output_data["Level"].append(item.get_level(page_soup))
            output_data["Symbol"].append(item.symbol)

            output_data["Meaning"].append(item.name)
            meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
            output_data["Meaning Mnemonic"].append(meaning_mnemonic)

            output_data["Word Type"].append(item.name)

            output_data["Reading"].append(item.name)
            output_data["Reading Mnemonic"].append(item.name)

            output_data["Context 1-EN"].append(item.name)
            output_data["Context 1-JP"].append(item.name)

            output_data["Context 2-EN"].append(item.name)
            output_data["Context 2-JP"].append(item.name)

            output_data["Context 3-EN"].append(item.name)
            output_data["Context 3-JP"].append(item.name)

        # End the time tracking and print result
        tracker.end()
        tracker.print_progress()
        tracker.print_stats()

    return pd.DataFrame(data=output_data)


"""
    Some Comment
"""
def get_session():
    login_url = "https://www.wanikani.com/login"

    site_session = requests.session()

    # Get login authentication token
    result = site_session.get(login_url)
    soup = BeautifulSoup(result.content, "html.parser")
    token_element = soup.find("input", {"name": "authenticity_token"})

    if token_element is not None:
        authenticity_token = token_element["value"]
    else:
        print("ERROR: Could not find the authenticity_token element")
        return None

    with open("Credentials/WaniKaniLogin.json", encoding="utf-8") as f:
        data = json.load(f)

        # Create payload
        payload = {
            "user[login]": data["username"],
            "user[password]": data["password"],
            "authenticity_token": authenticity_token
        }

        # Perform login
        result = site_session.post(login_url, data=payload, headers=dict(referer=login_url))

        if result.ok:
            return site_session
        else:
            print("ERROR: Could not complete WaniKani login")


"""
    Some Comment
"""
def get_page(page_url: str, site_session: requests.sessions.Session):
    if site_session is None:
        print("ERROR: Could not load WaniKani page, session is None")
        return None

    result = site_session.get(page_url, headers=dict(referer=page_url))

    if result.status_code == 404:
        print("ERROR: Could not load WaniKani page, status 404")
        return None

    return BeautifulSoup(result.content, "html.parser")


"""
    Some Comment
"""
def get_grid_data(gridType: GridType, site_session: requests.sessions.Session):
    url = gridType.value
    soup = get_page(url, site_session)

    if gridType == GridType.Vocabulary:
        latticeType = "lattice-multi-character"
    else:
        latticeType = "lattice-single-character"

    itemGrid = soup.find("section", {"class", latticeType})
    itemElements = itemGrid.find_all("a", attrs={"href": True})

    gridData = {"Name": [], "Symbol": [], "Url": []}

    for element in itemElements:
        symbolText = element.text

        if gridType == GridType.Radical:
            nameItem = element["title"]

            imageElement = element.find("img")
            if imageElement is not None:
                symbolText = f'<i class="radical-{nameItem.lower().replace(" ", "-")}"></i>'
        else:
            nameItem = Helper.get_original_title(element["title"])

        gridData["Name"].append(nameItem)
        gridData["Symbol"].append(symbolText)
        gridData["Url"].append("https://www.wanikani.com" + element["href"])

    return pd.DataFrame(data=gridData)
