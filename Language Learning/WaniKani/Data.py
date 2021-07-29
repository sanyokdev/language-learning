import time
from enum import Enum

import pandas as pd
import requests

from bs4 import BeautifulSoup, Tag

import Common.stats as stats
import Common.helper as helper
import WaniKani.site as site


class GridType(Enum):
    """
    The respecive symbol grids you can access on the WaniKani site.
    """
    Radical = "https://www.wanikani.com/lattice/radicals/meaning"
    Kanji = "https://www.wanikani.com/lattice/kanji/combined"
    Vocabulary = "https://www.wanikani.com/lattice/vocabulary/combined"


class MeaningType(Enum):
    """
    - Default - "Kanji & Vocab meaning"
    - Info - "Radical meaning" (WaniKani handles radicals separately)
    """
    Default = "meaning"
    Info = "information"


class MnemonicType(Enum):
    """
    - Meaning - "A meaning mnemonic"
    - Reading - "A reading mnemonic"
    - Info - "A radical mnemonic" (WaniKani handles radicals separately)
    """
    Meaning = "meaning"
    Reading = "reading"
    Info = "information"


class DataPresets(Enum):
    """
    Data output templates.
    \n used in the following data exports:
    \n - Radical, Kanji and Vocabulary.
    """

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
class _Common:
    """
    A common class with a set of functions the following symbols classes are derived from:
    \n - Radical, Kanji and Vocabulary
    """
    def __init__(self, name: str, symbol: str, url: str):
        """
        :param name: The symbol's name.
        :param symbol: The symbol character or icon "used in WaniRadicals".
        :param url: The url to the symbol's respective page.
        """
        self.name = name
        self.symbol = symbol
        self.url = url
        self.page_soup = None

    def check_soup(self):
        """
        Checks if the respective symbol has set the site_soup variable.
        """
        if self.page_soup is None:
            raise ValueError(self.name + " symbol's respective page soup is None")

    def set_page_soup(self, site_session: requests.sessions.Session):
        """
        Sets the page soup variable for the respctive symbol object

        :param site_session: The "logged in" state of the WaniKani site
        """
        self.page_soup = site.get_page(self.url, site_session)

    def get_level(self) -> str:
        """
        :return: A string of the respective symbol's level (i.e. The level at which you learn this radical, symbol or vocab)
        """
        return self.page_soup.find("a", {"class": "level-icon"}).contents[0]

    def get_meanings(self, meaning_type: MeaningType) -> [str]:
        """
        :param meaning_type: The type of meaning needed.
        :return:
        """
        meaning_section = self.page_soup.find("section", {"id": meaning_type.value})
        meanings = meaning_section.find_all("div", {"class": "alternative-meaning"})

        return [e.find("p").contents[0].replace(', ', ',') for e in meanings[:-1]]

    def get_readings(self):
        """
        :return:
        """
        reading_element = self.page_soup.find("section", {"id": "reading"})
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

    def get_mnemonic(self, mnemonic_type: MnemonicType):
        """
        :param mnemonic_type:
        :return:
        """
        meaning_element = self.page_soup.find("section", {"id": mnemonic_type.value})
        mnemonic_element = meaning_element.find("section", {"class": "mnemonic-content"})
        mnemonic_data = mnemonic_element.find_all("p")

        return format_mnemonic(mnemonic_data)


def format_mnemonic(mnemonic_data: []) -> str:
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
    def get_reading(self):
        """
        :return:
        """
        raise NotImplementedError("'Radical' object has no attribute 'get_reading'")

    def get_reading_meaning(self):
        """
        :return:
        """
        raise NotImplementedError("'Radical' object has no attribute 'get_reading_meaning'")


class Kanji(_Common):
    def get_radical_components(self):
        combination_element = self.page_soup.find("ul", {"class": "alt-character-list"})
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
    def get_word_type(self):
        """
        :return:
        """
        pass # TODO: Complete the method

    def get_audio_files(self):
        """
        :return:
        """
        pass # TODO: Complete the method

    def get_en_context_list(self):
        """
        :return:
        """
        pass # TODO: Complete the method

    def get_jp_context_list(self):
        """
        :return:
        """
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
def get_grid_data(grid_type: GridType, site_session: requests.sessions.Session) -> (pd.DataFrame, GridType):
    """
    Some Comment
    """
    url = grid_type.value
    soup = site.get_page(url, site_session)

    if grid_type == GridType.Vocabulary:
        lattice_type = "lattice-multi-character"
    else:
        lattice_type = "lattice-single-character"

    item_grid = soup.find("section", {"class", lattice_type})
    item_elements = item_grid.find_all("a", attrs={"href": True})

    grid_data = {"Name": [], "Symbol": [], "Url": []}

    for element in item_elements:
        item_symbol = element.text

        if grid_data == GridType.Radical:
            item_name = element["title"]

            image_element = element.find("img")
            if image_element is not None:
                item_symbol = f'<i class="radical-{item_name.lower().replace(" ", "-")}"></i>'
        else:
            print(element["title"])
            item_name = helper.get_original_title(element["title"])

        grid_data["Name"].append(item_name)
        grid_data["Symbol"].append(item_symbol)
        grid_data["Url"].append("https://www.wanikani.com" + element["href"])

    return pd.DataFrame(data=grid_data), grid_type


"""
    Some Comment
"""
def get_grid_item_data(grid_data: (pd.DataFrame, GridType), site_session: requests.sessions.Session) -> pd.DataFrame:
    """
    :param grid_data:
    :param site_session:
    :return:
    """

    # Get item data from the grid page
    grid_df = grid_data[0]
    grid_type = grid_data[1]

    grid_items = to_item_list(grid_df)
    item_list = [convert_type(item, grid_type) for item in grid_items]

    # Set up the progress tracking
    tracker = stats.TimeTracker(0.7, total_items=len(item_list))

    # Find and save the respecive data for each symbol in the grid
    output_data = {}

    count = 0 # -- DEBUG
    for item in item_list:
        if count == 10: # -- DEBUG
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

        count += 1 # -- DEBUG

    return pd.DataFrame(data=output_data)
# endregion


# region - Item Data
"""
    Some Comment
"""
def get_radical_data(item: Radical, site_session: requests.sessions.Session):
    # Sets the Radical object's page soup
    item.set_page_soup(site_session)

    # Prepare the output format
    output = DataPresets.RADICAL.value

    # Find the Level and Symbol
    output["Level"].append(item.get_level()) # (The level at which you learn this radical)
    output["Symbol"].append(item.symbol) # (either a regular character or icon "used in WaniRadicals")

    # Find the Meaning (i.e. Name)
    meaning = item.get_meanings(MeaningType.Info)[0]
    output["Meaning"].append(meaning)

    # Find the Mnemonic to easily remember the Meaning
    meaning_mnemonic = item.get_mnemonic(MnemonicType.Info)
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    return output


def get_kanji_data(item: Kanji, site_session: requests.sessions.Session):
    # Sets the Kanji object's page soup
    item.set_page_soup(site_session)

    # Prepare the output format
    output = DataPresets.KANJI.value

    # Find the Level and Symbol
    output["Level"].append(item.get_level()) # (The level at which you learn this kanji)
    output["Symbol"].append(item.symbol) # (a regular character)

    # Find the Meanings (i.e. the most common words associated to this Kanji)
    meanings = ",".join(item.get_meanings(MeaningType.Default))
    output["Meaning"].append(meanings)

    # Find the Radicals that make up this respective Kanji
    radical_combination = item.get_radical_components()
    output["Radical Component Name"].append(",".join(radical_combination[0]))
    output["Radical Component Symbol"].append(",".join(radical_combination[1]))

    # Find the Mnemonic to easily remember the Meaning
    meaning_mnemonic = item.get_mnemonic(MnemonicType.Meaning)
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    # Find the respective readings for this Kanji alonside showing which is the "primary" one
    readings = item.get_readings()
    output["Reading Onyomi"].append(readings[0]) # Gets the On'yomi reading in Hiragana
    output["Reading Kunyomi"].append(readings[1]) # Gets the Kun'yomi reading ""
    output["Reading Nanori"].append(readings[2]) # Gets the Nanori reading ""

    # Find the Mnemonic to easily remember the Reading
    reading_mnemonic = item.get_mnemonic(MnemonicType.Reading)
    output["Reading Mnemonic"].append(reading_mnemonic)

    return output


def get_vocabulary_data(item: Vocabulary, site_session: requests.sessions.Session):
    # Sets the Vocabulary object's page soup
    item.set_page_soup(site_session)

    # Prepare the output format
    output = DataPresets.VOCABULARY.value

    """
    output["Level"].append(item.name)
    output["Symbol"].append(item.name)

    output["Meaning"].append(item.name)
    output["Meaning Mnemonic"].append(item.name)

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
    """
    # print(output)
    return output
# endregion
