import time
from enum import Enum

import pandas as pd
import requests

from bs4 import BeautifulSoup, Tag

import Common.stats as stats
import Common.helper as helper
import WaniKani.site as site


class GridType(Enum):
    Radical = "https://www.wanikani.com/lattice/radicals/meaning"
    Kanji = "https://www.wanikani.com/lattice/kanji/combined"
    Vocabulary = "https://www.wanikani.com/lattice/vocabulary/combined"


class DataPresets(Enum):
    RADICAL = {
        "Level": [],
        "Symbol": [],
        "Meaning": [],
        "Meaning Mnemonic": []
    }

    KANJI = {
        "Level": [],
        "Symbol": [],
        "Meaning": [],
        "Radical Component Name": [],
        "Radical Component Symbol": [],
        "Meaning Mnemonic": [],
        "Reading Onyomi": [],
        "Reading Kunyomi": [],
        "Reading Nanori": [],
        "Reading Mnemonic": []
    }

    VOCABULARY = {
        "Level": [],
        "Symbol": [],
        "Meaning": [],
        "Meaning Mnemonic": [],
        "Word Type": [],
        "Reading": [],
        "Reading Mnemonic": [],
        "Reading Audio Female": [],
        "Reading Audio Male": [],
        "Context 1-EN": [],
        "Context 1-JP": [],
        "Context 2-EN": [],
        "Context 2-JP": [],
        "Context 3-EN": [],
        "Context 3-JP": []
    }


# region - Item Types
"""
    Some Comment
"""
class _Common:
    def __init__(self, name: str, symbol: str, url: str):
        self.name = name
        self.symbol = symbol
        self.url = url

    def get_page_soup(self, site_session: requests.sessions.Session):
        return site.get_page(self.url, site_session)

    def get_level(self, site_soup: BeautifulSoup):
        return site_soup.find("a", {"class": "level-icon"}).contents[0]

    def get_meanings(self, site_soup: BeautifulSoup):
        meaning_section = site_soup.find("section", {"id": "meaning"})
        meanings = meaning_section.find_all("div", {"class": "alternative-meaning"})

        return [e.find("p").contents[0].replace(', ', ',') for e in meanings[:-1]]

    def get_readings(self, site_soup: BeautifulSoup):
        reading_element = site_soup.find("section", {"id": "reading"})
        reading_list = reading_element.find_all("div", {"class": "span4"})

        readings = []
        for element in reading_list:
            reading_text = element.find("p").contents[0].replace('\n', '').strip(' ')

            if "muted-content" not in element["class"]:
                readings.append(f"<primary><jp>{reading_text}</jp></primary>")
            elif reading_text == "None":
                readings.append("None")
            else:
                readings.append(f"<jp>{reading_text}</jp>")

        return readings

    def get_mnemonic(self, mnemonic_type: str, site_soup: BeautifulSoup):
        meaning_element = site_soup.find("section", {"id": mnemonic_type})
        mnemonic_element = meaning_element.find("section", {"class": "mnemonic-content"})
        mnemonic_data = mnemonic_element.find_all("p")

        return format_mnemonic(mnemonic_data)


def format_mnemonic(mnemonic_data: []):
    mnemonic_list = []

    for element in mnemonic_data:
        mnemonic = ""
        element_data = element.contents

        for item in element_data:
            if type(item) == Tag:
                item_class = item.get("class")
                item_content = item.contents[0]
                item_tag = ""

                if item_class is not None:
                    if item_class[0] == "radical-highlight":
                        item_tag = f"<radical>{item_content}</radical>"

                    elif item_class[0] == "kanji-highlight":
                        item_tag = f"<kanji>{item_content}</kanji>"

                    elif item_class[0] == "vocabulary-highlight":
                        item_tag = f"<vocabulary>{item_content}</vocabulary>"

                    elif item_class[0] == "reading-highlight":
                        item_tag = f"<reading>{item_content}</reading>"

                else:
                    item_tag = f"<jp>{item_content}</jp>"

                mnemonic += item_tag
            else:
                mnemonic += item

        mnemonic_list.append(mnemonic)

    return "\n\n".join(mnemonic_list)


class Radical(_Common):
    def get_reading(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading'")

    def get_reading_meaning(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading_meaning'")


class Kanji(_Common):
    def get_radical_components(self, site_soup: BeautifulSoup):
        combination_element = site_soup.find("ul", {"class": "alt-character-list"})
        radical_elements = combination_element.find_all("li")

        radical_names = []
        radical_symbols = []

        for element in radical_elements:
            radical_tag = element.find("a")

            name = str(radical_tag.contents[2])
            name = name.strip(' ').strip('\n')

            symbol = str(radical_tag.find("span", {"class": "radical-icon"}).contents[0])
            symbol = symbol.replace(' ', '').replace('\n', '')

            span_tag = radical_tag.find("span", {"class": "radical-icon"})
            img_tag = span_tag.find("img")

            if img_tag is not None:
                symbol = f'<i class="radical-{name.lower().replace(" ", "-")}"></i>'

            radical_names.append(name)
            radical_symbols.append(symbol)

        return [radical_names, radical_symbols]


class Vocabulary(_Common):
    def get_word_type(self, site_soup: BeautifulSoup):
        pass # TODO: Complete the method

    def get_audio_files(self):
        pass # TODO: Complete the method

    def get_en_context_list(self, site_soup: BeautifulSoup):
        pass # TODO: Complete the method

    def get_jp_context_list(self, site_soup: BeautifulSoup):
        pass # TODO: Complete the method


"""
    Some Comment
"""
def to_item_list(data: pd.DataFrame):
    output = []
    for i in range(len(data.Name)):
        output.append(_Common(data.Name[i], data.Symbol[i], data.Url[i]))

    return output



"""
    Some Comment
"""
def convert_type(item: _Common, item_type: GridType):
    if item_type == GridType.Radical:
        return Radical(item.name, item.symbol, item.url)

    elif item_type == GridType.Kanji:
        return Kanji(item.name, item.symbol, item.url)

    else: # GridType.Vocabulary
        return Vocabulary(item.name, item.symbol, item.url)
# endregion


# region - Grid
"""
    Some Comment
"""
def get_grid_data(gridType: GridType, site_session: requests.sessions.Session):
    url = gridType.value
    soup = site.get_page(url, site_session)

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
            nameItem = helper.get_original_title(element["title"])

        gridData["Name"].append(nameItem)
        gridData["Symbol"].append(symbolText)
        gridData["Url"].append("https://www.wanikani.com" + element["href"])

    return pd.DataFrame(data=gridData)


"""
    Some Comment
"""
def get_grid_items(delay: float, grid_type: GridType, site_session: requests.sessions.Session):
    # Get item data from the grid page
    grid_data = {
        "Name":
            [
                "Strict",
                "Daring",
                "Win",
                "Wisteria",
                "Follow",
                "Public Building",
                "Noh Chanting",
                "Urge",
                "Below"
            ],
        "Symbol":
            [
                "厳",
                "敢",
                "勝",
                "藤",
                "追",
                "館",
                "謡",
                "迫",
                "下"
            ],
        "Url":
            [
                "https://www.wanikani.com/kanji/%E5%8E%B3",
                "https://www.wanikani.com/kanji/%E6%95%A2",
                "https://www.wanikani.com/kanji/%E5%8B%9D",
                "https://www.wanikani.com/kanji/%E8%97%A4",
                "https://www.wanikani.com/kanji/%E8%BF%BD",
                "https://www.wanikani.com/kanji/%E9%A4%A8",
                "https://www.wanikani.com/kanji/%E8%AC%A1",
                "https://www.wanikani.com/kanji/%E8%BF%AB",
                "https://www.wanikani.com/kanji/%E4%B8%8B"
            ]
    }
    grid_items = to_item_list(pd.DataFrame(data=grid_data))
    item_list = [convert_type(item, grid_type) for item in grid_items]
    """
    grid_items = to_item_list(get_grid_data(grid_type, site_session))
    item_list = [convert_type(item, grid_type) for item in grid_items]
    """

    # Set up the progress tracking
    tracker = stats.TimeTracker(delay, total_items=len(item_list))

    # Find and save the respecive data for each symbol in the grid
    output_data = {}

    # count = 0 -- DEBUG
    for item in item_list:
        # if count == 10: -- DEBUG
        #     break

        # Start the time tracking
        tracker.start()

        # Find the respective radical data inside the page
        if grid_type == GridType.Radical:
            output_data = get_radical_data(item, site_session)

        elif grid_type == GridType.Kanji:
            output_data = get_kanji_data(item, site_session)

        elif grid_type == GridType.Vocabulary:
            output_data = get_vocabulary_data(item, site_session)

        # End the time tracking and print result
        tracker.end()
        tracker.print_progress()
        tracker.print_stats()
        # count += 1 -- DEBUG

    return pd.DataFrame(data=output_data)
# endregion


# region - Item Data
"""
    Some Comment
"""
def get_radical_data(item: Radical, site_session: requests.sessions.Session):
    page_soup = item.get_page_soup(site_session)
    output = DataPresets.RADICAL.value

    output["Level"].append(item.get_level(page_soup))
    output["Symbol"].append(item.symbol)

    output["Meaning"].append(item.name)
    meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    # print(output)
    return output


def get_kanji_data(item: Kanji, site_session: requests.sessions.Session):
    page_soup = item.get_page_soup(site_session)
    output = DataPresets.KANJI.value
    print(item.name)

    output["Level"].append(item.get_level(page_soup))
    output["Symbol"].append(item.symbol)

    meanings = item.get_meanings(page_soup)
    output["Meaning"].append(",".join(meanings))

    radical_combination = item.get_radical_components(page_soup)
    output["Radical Component Name"].append(",".join(radical_combination[0]))
    output["Radical Component Symbol"].append(",".join(radical_combination[1]))

    meaning_mnemonic = item.get_mnemonic("meaning", page_soup)
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    readings = item.get_readings(page_soup)
    output["Reading Onyomi"].append(readings[0])
    output["Reading Kunyomi"].append(readings[1])
    output["Reading Nanori"].append(readings[2])

    reading_mnemonic = item.get_mnemonic("reading", page_soup)
    output["Reading Mnemonic"].append(reading_mnemonic)

    # print(output)
    return output


def get_vocabulary_data(item: Vocabulary, site_session: requests.sessions.Session):
    page_soup = item.get_page_soup(site_session)
    output = DataPresets.VOCABULARY.value

    output["Level"].append(item.get_level(page_soup))
    output["Symbol"].append(item.symbol)

    output["Meaning"].append(item.name)
    meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    output["Word Type"].append(item.name)

    output["Reading"].append(item.name)
    output["Reading Mnemonic"].append(item.name)

    output["Reading Audio Female"].append(item.name)
    output["Reading Audio Male"].append(item.name)

    output["Context 1-EN"].append(item.name)
    output["Context 1-JP"].append(item.name)

    output["Context 2-EN"].append(item.name)
    output["Context 2-JP"].append(item.name)

    output["Context 3-EN"].append(item.name)
    output["Context 3-JP"].append(item.name)

    # print(output)
    return output
# endregion
