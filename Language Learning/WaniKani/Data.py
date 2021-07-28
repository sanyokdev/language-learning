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
        "Radical Combination": [],
        "Meaning": [],
        "Meaning Mnemonic": [],
        "Reading": [],
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


class Radical(_Common):
    def get_reading(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading'")

    def get_reading_meaning(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading_meaning'")


class Kanji(_Common):
    def get_radical_combination(self, site_soup: BeautifulSoup):
        combination_element = site_soup.find("ul", {"class": "alt-character-list"})
        radical_elements = combination_element.find_all("li")
        radical_list = []
        
        for element in radical_elements:
            radical_tag = element.find("a")

            radical_name = str(radical_tag.contents[2])
            radical_symbol = str(radical_tag.find("span", {"class": "radical-icon"}).contents[0])

            removal_list = [' ', '\n']
            for s in removal_list:
                radical_name = radical_name.replace(s, '')
                radical_symbol = radical_symbol.replace(s, '')

            radical_list.append([radical_name, radical_symbol])

        return radical_list


class Vocabulary(_Common):
    def get_word_type(self, site_soup: BeautifulSoup):
        pass

    def get_en_context_list(self, site_soup: BeautifulSoup):
        pass

    def get_jp_context_list(self, site_soup: BeautifulSoup):
        pass


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
    grid_items = to_item_list(get_grid_data(grid_type, site_session))
    item_list = [convert_type(item, grid_type) for item in grid_items]

    # Set up the progress tracking
    tracker = stats.TimeTracker(delay, total_items=len(item_list))

    # Find and save the respecive data for each symbol in the grid
    output_data = {}

    count = 0
    for item in item_list:
        if count == 10:
            break

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
        count += 1

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
    output["Level"].append(item.get_level(page_soup))
    output["Symbol"].append(item.symbol)

    output["Radical Combination"].append(item.get_radical_combination(page_soup))

    output["Meaning"].append(item.name)
    meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    output["Reading"].append(item.name)
    output["Reading Mnemonic"].append(item.name)
    print(item.name)
    print(output)
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

    output["Context 1-EN"].append(item.name)
    output["Context 1-JP"].append(item.name)

    output["Context 2-EN"].append(item.name)
    output["Context 2-JP"].append(item.name)

    output["Context 3-EN"].append(item.name)
    output["Context 3-JP"].append(item.name)

    # print(output)
    return output
# endregion
