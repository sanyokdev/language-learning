from enum import Enum

import pandas as pd
import requests

from bs4 import Tag

import Common.stats as stats
import Common.helper as helper
import WaniKani.site as site


class GridType(Enum):
    """
    The respecive symbol grids/types you can access on the WaniKani site.
    """
    Radical = "https://www.wanikani.com/lattice/radicals/meaning"
    Kanji = "https://www.wanikani.com/lattice/kanji/combined"
    Vocabulary = "https://www.wanikani.com/lattice/vocabulary/combined"


class MeaningType(Enum):
    """
    - Radical - "Radical meaning"
    - Kanji - "Kanji meaning"
    - Vocabulary - "Vocab meaning"
    """
    Radical = "information"
    Kanji = "meaning"
    Vocabulary = "meaning"


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
    \n Used in the following data exports:
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

    def set_page_soup(self, site_session: requests.sessions.Session):
        """
        Sets the page soup variable for the respctive symbol object.
        \n Note: This should "always" be run before the other functions in this class and derived from.

        :param site_session: The "logged in" state of the WaniKani site.
        """
        self.page_soup = site.get_page(self.url, site_session)

    def get_level(self) -> str:
        """
        Gets the level at which you learn this radical, kanji or vocab.

        :return: A string of the respective symbol's level
        """
        return self.page_soup.find("a", {"class": "level-icon"}).contents[0]

    def get_meaning_data(self, meaning_type: MeaningType) -> [str]:
        """
        Gets the meaning data from the Meaning/Information sections from the respective symbol pages (depends on meaning_type input).

        - (in) MeaningType.Radical -> (out) ["primary"]
        - (in) MeaningType.Kanji -> (out) ["primary", "alternatives - optional"]
        - (in) MeaningType.Vocabulary -> (out) ["primary", "alternatives - optional", "word type"]

        :param meaning_type: The type of meaning needed.
        :return: List of strings, output depends on meaning_type value.
        """
        # Find the meaning section and get all the available meaning data.
        meaning_section = self.page_soup.find("section", {"id": meaning_type.value})
        meanings = meaning_section.find_all("div", {"class": "alternative-meaning"})

        # Sort though the data and remove user specified meanings.
        meaning_list = []
        for element in meanings:
            text_tag = element.find("p")

            if text_tag is not None:
                meaning_list.append(text_tag.contents[0].replace(', ', ','))

        return meaning_list

    def get_mnemonic(self, mnemonic_type: MnemonicType) -> str:
        """
        Gets the Mnemonic used to easily remember the Meaning or Reading (depends on mnemonic_type input).

        - (in) MnemonicType.Meaning -> (out) "M-eaning mnemonic"
        - (in) MnemonicType.Reading -> (out) "Reading mnemonic"
        - (in) MnemonicType.Info -> (out) "Radical mnemonic" (WaniKani handles radicals separately)

        :param mnemonic_type: The type of mnemonic needed.
        :return:
        """
        # Find the meaning section and get all the available mnemonic content.
        meaning_element = self.page_soup.find("section", {"id": mnemonic_type.value})
        mnemonic_element = meaning_element.find("section", {"class": "mnemonic-content"})
        mnemonic_data = mnemonic_element.find_all("p")

        # Format the mnemonic into text Anki can display properly.
        return format_mnemonic(mnemonic_data)


# TODO: You can have tags inside tags (e.g. <jp><reading>しら</reading></jp> - Source: https://www.wanikani.com/vocabulary/%E7%99%BD%E8%8F%8A)
#       Why... :/
#       - Also, document this entire function
def format_mnemonic(mnemonic_data: []) -> str:
    """
    Formats a list of mnemonic "elements" into a string used Anki can use for either the Meaning or Reading mnemonics.

    :param mnemonic_data: The unformated mnemonic data.
    :return: A formatted string Anki can display properly.
    """
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
    """
    A class with a set of functions used for the "Radical" objects.
    """
    pass


class Kanji(_Common):
    """
    A class with a set of functions used for the "Kanji" objects.
    """
    def get_radical_components(self) -> [[str], [str]]:
        """
        Gets the Radicals (name and symbol) that make up this respective Kanji.

        :return: A list containing a list of all the Radical component names and symbols. [["All Radical Names"], ["All Radical Symbols"]]
        """
        # Find the combination section and get all the available radical elements.
        combination_element = self.page_soup.find("ul", {"class": "alt-character-list"})
        radical_elements = combination_element.find_all("li")

        # Prep ouput lists
        radical_names = []
        radical_symbols = []

        # Go though all of the Radical elements and pull out its respective Name and Symbol into the according lists.
        for element in radical_elements:
            radical_tag = element.find("a")

            name = str(radical_tag.contents[2])
            name = name.strip(' ').strip('\n')

            symbol = str(radical_tag.find("span", {"class": "radical-icon"}).contents[0])
            symbol = symbol.replace(' ', '').replace('\n', '')

            # Check if the symbol element is an image tag meaning the Radical has no character.
            span_tag = radical_tag.find("span", {"class": "radical-icon"})
            img_tag = span_tag.find("img")

            if img_tag is not None:
                # Replace the image with a parsable font icon that Anki can use.
                symbol = f'<i class="radical-{name.lower().replace(" ", "-")}"></i>'

            radical_names.append(name)
            radical_symbols.append(symbol)

        return [radical_names, radical_symbols]

    def get_readings(self) -> [str]:
        """
        Gets the respective readings for this Kanji alonside showing which is the "primary" one.

        :return: A list of strings containing the "On'yomi", "Kun'yomi" and "Nanori" readings.
        """
        # Find the reading section and get all the available reading elements.
        reading_element = self.page_soup.find("section", {"id": "reading"})
        reading_list = reading_element.find_all("div", {"class": "span4"})

        # Check though all of the reading elements, format and label everything accordingly
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


class Vocabulary(_Common):
    """
    A class with a set of functions used for the "Vocabulary" objects.
    """
    # TODO: Complete the method
    def get_readings(self) -> [str]:
        """

        :return:
        """

        pass

    # TODO: Complete the method
    def get_audio_files(self):
        """

        :return:
        """

        pass

    # TODO: Complete the method
    def get_context_list(self):
        """

        :return:
        """

        pass


def to_item_list(data: pd.DataFrame) -> [_Common]:
    """
    Turns a respective symbol's data into a nice package containing that info (Symbol Object).

    :param data: The data that needs to be converted into a Symbol (_Common) item.
    :return: A list of "_Common" objects using the data provided.
    """
    output = []
    for i in range(len(data.Name)):
        output.append(_Common(data.Name[i], data.Symbol[i], data.Url[i]))

    return output


def convert_type(item: _Common, item_type: GridType):
    """
    Converts one item type (derived from _Common) to another.

    :param item: The original item type that will convert (derived from _Common).
    :param item_type: The type of the converted ouput item.
    :return: An item type that has converted (e.g. Radical, Kanji or Vocabulary).
    """
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
    Gets the base set of data for each symbol in a respective grid_type.

    :param grid_type: The respecive symbol grids/types you can access on the WaniKani site.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A base set of data use to create all the items in a respective symbol type's grid.
    """
    # Load the respective grid's page and get its soup.
    url = grid_type.value
    soup = site.get_page(url, site_session)

    # Change the selected lattice class depending on the grid_type.
    if grid_type == GridType.Vocabulary:
        lattice_type = "lattice-multi-character"
    else:
        lattice_type = "lattice-single-character"

    # Find the respective lattice and pull all the a (link) tags from each symbol.
    item_grid = soup.find("section", {"class", lattice_type})
    item_elements = item_grid.find_all("a", attrs={"href": True})

    # Prepare the ouput data preset.
    grid_data = {"Name": [], "Symbol": [], "Url": []}

    # Go through each tag and pull out the respective symbol's Name, Symbol and Url.
    for element in item_elements:
        # If the symbol has a character representing it use it (Blank if it has an image instead).
        item_symbol = element.text

        if grid_type == GridType.Radical:
            item_name = element["title"]

            # Check if the symbol element is an image tag meaning the Radical has no character.
            if element.find("img") is not None:
                # Replace the image with a parsable font icon that Anki can use.
                item_symbol = f'<i class="radical-{item_name.lower().replace(" ", "-")}"></i>'
        else:
            item_name = helper.get_original_title(element["title"])

        # Save all the collected data
        grid_data["Name"].append(item_name)
        grid_data["Symbol"].append(item_symbol)
        grid_data["Url"].append("https://www.wanikani.com" + element["href"])

    return pd.DataFrame(data=grid_data), grid_type


def get_grid_item_data(grid_data: (pd.DataFrame, GridType), site_session: requests.sessions.Session) -> pd.DataFrame:
    """
    Gets the respective data for each symbol item (Radical, Kanji or Vocabulary) in grid_data from their respective pages.

    :param grid_data: A base set of data use to create all the items in a respective symbol type's grid.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: The contents of each symbol item's data as a Dataframe.
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
def get_radical_data(item: Radical, site_session: requests.sessions.Session) -> {}:
    """
    Pulls the data needed from the respective Radical's page.

    :param item: The Radical symbol object.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A dict containing all the data pulled from the respective Radical's page.
    """
    # Sets the Radical object's page soup
    item.set_page_soup(site_session)

    # Prepare the output format
    output = DataPresets.RADICAL.value

    # Find the Level and Symbol
    output["Level"].append(item.get_level()) # (The level at which you learn this Radical)
    output["Symbol"].append(item.symbol) # (either a regular character or icon "used in WaniRadicals")

    # Find the Meaning (i.e. Name)
    meaning = item.get_meaning_data(MeaningType.Radical)[0]
    output["Meaning"].append(meaning)

    # Find the Mnemonic to easily remember the Meaning
    meaning_mnemonic = item.get_mnemonic(MnemonicType.Info)
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    return output


def get_kanji_data(item: Kanji, site_session: requests.sessions.Session) -> {}:
    """
    Pulls the data needed from the respective Kanji's page.

    :param item: The Kanji symbol object.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A dict containing all the data pulled from the respective Kanji's page.
    """
    # Sets the Kanji object's page soup
    item.set_page_soup(site_session)

    # Prepare the output format
    output = DataPresets.KANJI.value

    # Find the Level and Symbol
    output["Level"].append(item.get_level()) # (The level at which you learn this Kanji)
    output["Symbol"].append(item.symbol) # (a regular kanji character)

    # Find the Meanings (i.e. the most common words associated to this Kanji)
    meanings = ",".join(item.get_meaning_data(MeaningType.Kanji))
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


def get_vocabulary_data(item: Vocabulary, site_session: requests.sessions.Session) -> {}:
    """
    Pulls the data needed from the respective Vocabulary's page.

    :param item: The Vocabulary symbol object.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A dict containing all the data pulled from the respective Vocabulary's page.
    """
    # Sets the Vocabulary object's page soup
    item.set_page_soup(site_session)

    # Prepare the output format
    output = DataPresets.VOCABULARY.value

    # Find the Level and Symbol
    output["Level"].append(item.get_level()) # (The level at which you learn this Vocabulary)
    output["Symbol"].append(item.symbol) # (a set of Kanji and Hiragana characters)

    # Find the Meanings (i.e. the most common words associated to this Vocabulary)
    # meanings = ",".join(item.get_meanings(MeaningType.Default))
    meaning_data = item.get_meaning_data(MeaningType.Vocabulary)
    meanings = ",".join(meaning_data[:-1])
    output["Meaning"].append(meanings)

    # Find the Mnemonic to easily remember the Meaning
    meaning_mnemonic = item.get_mnemonic(MnemonicType.Meaning)
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    # Find the part of speech the Vocabulary belongs to
    output["Word Type"].append(meaning_data[-1])

    # Find the respective readings for this Vocabulary
    output["Reading"].append("-") # TODO: Add functionality

    # Find the Mnemonic to easily remember the Reading
    reading_mnemonic = item.get_mnemonic(MnemonicType.Reading)
    output["Reading Mnemonic"].append(reading_mnemonic)

    # Find the respective audio for each of this Vocabulary's readings
    output["Reading Audio Female"].append("-") # TODO: Add functionality
    output["Reading Audio Male"].append("-") # TODO: Add functionality

    # Find the context (examples) in which this Vocabulary is used in
    output["Context 1-EN"].append("-") # TODO: Add functionality
    output["Context 1-JP"].append("-") # TODO: Add functionality

    output["Context 2-EN"].append("-") # TODO: Add functionality
    output["Context 2-JP"].append("-") # TODO: Add functionality

    output["Context 3-EN"].append("-") # TODO: Add functionality
    output["Context 3-JP"].append("-") # TODO: Add functionality

    # print(output)
    return output
# endregion
