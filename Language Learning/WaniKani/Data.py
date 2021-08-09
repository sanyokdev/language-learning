import json
import math
from enum import Enum

import numpy as np
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


# TODO: Document this function
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

        hints_offset = ""
        if element.parent.name == "aside":
            hints_offset = "- Hint: "

        for item in element_data:
            if type(item) == Tag:
                item_class = item.get("class")

                if item.name == "span":
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
                        if type(item_content) == Tag:
                            item_tag = f"<reading><jp>{item_content.contents[0]}</jp></reading>"
                        else:
                            item_tag = f"<jp>{item_content}</jp>"

                    mnemonic += item_tag

                elif item.name == "a":
                    sub_item = item.contents[0]
                    if type(sub_item) == Tag:
                        sub_item_class = sub_item.get("class")

                        if sub_item.name == "span":
                            sub_item_content = sub_item.contents[0]
                            sub_item_tag = ""

                            if sub_item_class is not None:
                                if sub_item_class[0] == "radical-highlight":
                                    sub_item_tag = f"<radical>{sub_item_content}</radical>"

                                elif sub_item_class[0] == "kanji-highlight":
                                    sub_item_tag = f"<kanji>{sub_item_content}</kanji>"

                                elif sub_item_class[0] == "vocabulary-highlight":
                                    sub_item_tag = f"<vocabulary>{sub_item_content}</vocabulary>"

                                elif sub_item_class[0] == "reading-highlight":
                                    sub_item_tag = f"<reading>{sub_item_content}</reading>"
                            mnemonic += sub_item_tag
                    else:
                        mnemonic += sub_item

            else:
                mnemonic += item

        spacing = "<br><br>"
        if element == mnemonic_data[-1]:
            spacing = ""

        mnemonic_list.append(hints_offset + mnemonic + spacing)

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

    def get_readings_data(self) -> [[str], [str]]:
        """
        Gets the respective readings for this Kanji alonside showing which is the "primary" one.

        :return: A list of strings containing the "On'yomi", "Kun'yomi" and "Nanori" readings.
        """
        # Find the reading section and get all the available reading elements.
        reading_element = self.page_soup.find("section", {"id": "reading"})
        reading_list = reading_element.find_all("div", {"class": "span4"})

        # Check though all of the reading elements, format and label everything accordingly.
        readings = []
        readings_whitelist = []

        for element in reading_list:
            reading_text = element.find("p").contents[0].replace('\n', '').strip(' ')

            if "muted-content" not in element["class"]:
                readings.append(f"<reading><jp>{reading_text}</jp></reading>")
                readings_whitelist.append(reading_text)
            elif reading_text == "None":
                readings.append("None")
            else:
                readings.append(f"<jp>{reading_text}</jp>")

        return [readings, readings_whitelist]


class Vocabulary(_Common):
    """
    A class with a set of functions used for the "Vocabulary" objects.
    """
    def get_kanji_components(self) -> [[str], [str]]:
        """
        Gets the Kanji (name and symbol) that make up this respective Vocabulary.

        :return: A list containing a list of all the Kanji component names and symbols. [["All Kanji Names"], ["All Kanji Symbols"]]
        """
        # Find the combination section and get all the available kanji elements.
        component_element = self.page_soup.find("section", {"id": "components"})
        kanji_elements = component_element.find_all("li", {"class": "character-item"})

        # Prep ouput lists
        kanji_names = []
        kanji_symbols = []

        # Go though all of the Kanji elements and pull out its respective Name and Symbol into the according lists.
        for element in kanji_elements:
            link_element = element.find("a")

            name_element = link_element.find_all("li")[1]
            kanji_names.append(name_element.contents[0])

            symbol_element = link_element.find("span")
            kanji_symbols.append(symbol_element.contents[0])

        return [kanji_names, kanji_symbols]

    def get_readings_data(self) -> [[str], [str]]:
        """
        Gets the respective readings for this Vocabulary.

        :return: A list of lists containing the respective readings and the readings whitelist.
        """
        # Find the reading section and get all the available reading elements.
        reading_element = self.page_soup.find("section", {"id": "reading"})
        readings_list = reading_element.find_all("div", {"class": "pronunciation-group"})

        # Check though all of the reading elements, format and label everything accordingly.
        readings = []
        readings_whitelist = []

        for element in readings_list:
            reading_text = element.find("p").contents[0]

            readings.append(f"<reading><jp>{reading_text}</jp></reading>")
            readings_whitelist.append(reading_text)

        return [readings, readings_whitelist]

    # TODO: Clean/recode this method or Document it
    def get_audio_reading_data(self) -> ([], []):
        # Find the reading section and get all the available reading elements.
        reading_element = self.page_soup.find("section", {"id": "reading"})
        div_element = reading_element.find("div", {"data-react-class": "Readings/Readings"})

        prop_data = div_element.get("data-react-props")
        json_data = json.loads(prop_data)

        readings_list = []
        audio_pseudo_dict = []  # I HATE DICTIONARIES, WHY ARE YOU SO FINICKY :/

        # Get audio data
        for reading_obj in json_data["readings"]:
            readings_list.append(reading_obj["reading"])
            audio_pseudo_dict.append({"male": "None", "female": "None"})

        for audio_obj in json_data["pronunciationAudios"]:
            url = audio_obj["url"]

            if ".mp3" in url:
                metadata = audio_obj["metadata"]

                reading = metadata["pronunciation"]
                gender = metadata["gender"]

                audio_pseudo_dict[readings_list.index(reading)][gender] = url

        return readings_list, audio_pseudo_dict

    # TODO: Clean/recode this method or Document it
    def get_audio_data(self, audio_reading_data: ([], [])) -> {}:
        readings_list = audio_reading_data[0]
        pseudo_dict = audio_reading_data[1]

        output_data = {"Male": [], "Female": []}

        for reading in readings_list:
            reading_id = readings_list.index(reading)

            genders = ["Male", "Female"]
            for gender in genders:
                if pseudo_dict[reading_id][gender.lower()] != "None":
                    audio_filename = f"[sound:Vocab-{ reading }-{ gender }.mp3]"
                    output_data[gender].append(audio_filename)

                else:
                    output_data[gender].append("None")

        return output_data

    # TODO: Clean/recode this method or Document it
    def download_audio(self, audio_reading_data: ([], [])):
        """

        :param audio_reading_data:
        :return:
        """
        readings_list = audio_reading_data[0]
        pseudo_dict = audio_reading_data[1]

        for i in range(len(pseudo_dict)):
            audio_data = pseudo_dict[i]
            reading = readings_list[i]

            if audio_data["male"] != "None":
                filename = f"Vocab-{ reading }-Male"

                helper.download_site_file(filename, ".mp3", audio_data["male"])
                # print("Dowloaded: " + filename)
                pass

            if audio_data["female"] != "None":
                filename = f"Vocab-{ reading }-Female"

                helper.download_site_file(filename, ".mp3", audio_data["female"])
                # print("Dowloaded: " + filename)
                pass

    def get_context_data(self) -> {}:
        """
        Gets the context (example) sentences for this respective Vocabulary.

        :return: A dict containing 3 context dicts each having a EN and JP sentence (if it exists).
        """
        # Find the context section and get all the available reading elements.
        context_element = self.page_soup.find("section", {"id": "context"})
        text_block_elements = context_element.find_all("div", {"class": "context-sentence-group"})

        # Prepare the output data
        output_data = {
            "Context 1": {"EN": "None", "JP": "None"},
            "Context 2": {"EN": "None", "JP": "None"},
            "Context 3": {"EN": "None", "JP": "None"},
            "Context 4": {"EN": "None", "JP": "None"}
        }

        # Sort through all the context items and pull out the text
        for i in range(len(text_block_elements)):
            block = text_block_elements[i]
            text_elements = block.find_all("p")

            index = i + 1
            for element in text_elements:
                if element.contents:
                    sentence = element.contents[0]

                    if element.get("lang") == "ja":
                        text = f"<jp>{ sentence }</jp>"
                        output_data[f"Context { index }"]["JP"] = text
                    else:
                        output_data[f"Context {index}"]["EN"] = sentence

        return output_data


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
class CustomGridItem:
    """
    A custom grid item.
    Used to test grid functionality
    """
    def __init__(self, name: str, symbol: str, url: str):
        self.name = name
        self.symbol = symbol
        self.url = url

def get_custom_grid_data(item_list: [CustomGridItem], grid_type: GridType) -> (pd.DataFrame, GridType):
    """
    Gets the set of data for each manually placed symbol in the item_list

    :param item_list: A list of custom grid items.
    :param grid_type: The respecive symbol grids/types you can access on the WaniKani site.
    :return: A base set of data use to create all the items in a respective symbol type's grid.
    """
    # Prepare the ouput data preset.
    grid_data = {"Name": [], "Symbol": [], "Url": []}

    for item in item_list:
        # Save all the collected data
        grid_data["Name"].append(item.name)
        grid_data["Symbol"].append(item.symbol)
        grid_data["Url"].append(item.url)

    return pd.DataFrame(data=grid_data), grid_type

def get_grid_data(grid_type: GridType) -> (pd.DataFrame, GridType):
    """
    Gets the base set of data for each symbol in a respective grid_type.

    :param grid_type: The respecive symbol grids/types you can access on the WaniKani site.
    :return: A base set of data use to create all the items in a respective symbol type's grid.
    """
    # Gets the site's session
    site_session = site.get_session()

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


def get_grid_item_data(grid_data: (pd.DataFrame, GridType), CHUNK_MODE=False, MAX_CHUNK_SIZE=500, GET_AUDIO=True):
    """
    Gets the respective data for each symbol item (Radical, Kanji or Vocabulary) in grid_data from their respective pages.

    :param grid_data: A base set of data use to create all the items in a respective symbol type's grid.
    :param CHUNK_MODE: Changes the SPLIT_MODE state of the function (False -> Works like normal, True -> Stops at a specific point). TODO: Update this
    :param MAX_CHUNK_SIZE: If SPLIT_MODE is True, stop the method after SPLIT_SIZE items. TODO: Update this
    :param GET_AUDIO: TODO: Update this
    :return: The contents of each symbol item's data as a Dataframe.
    """
    # Set up the grid data variables
    grid_df = grid_data[0]
    grid_type = grid_data[1]

    total_item_count = len(grid_df)
    print("\033[1;32;40m" + f"Total Item Count: { total_item_count }" + "\033[0m")

    # Set up the default chunk size if disabled
    if CHUNK_MODE is False:
        MAX_CHUNK_SIZE = total_item_count

    # Set up the chunk data
    total_chunk_count = math.ceil(total_item_count / MAX_CHUNK_SIZE)
    all_chunk_item_data = np.array_split(grid_df, total_chunk_count)

    # Go through each chunk and get all its respective item data
    for cur_chunk in range(total_chunk_count):
        print("\033[1;32;40m" + f"Processing Chunk { cur_chunk + 1 } / { total_chunk_count }" + "\033[0m")

        # Gets the item data for the current chunk
        chunk_item_data = all_chunk_item_data[cur_chunk]
        chunk_item_data.reset_index(drop=True, inplace=True)

        chunk_common_items = to_item_list(chunk_item_data)
        chunk_converted_items = [convert_type(common_item, grid_type) for common_item in chunk_common_items]

        # Gets the site settion for this split
        site_session = site.get_session()

        # Set up the progress tracking
        tracker = stats.TimeTracker(total_items=len(chunk_converted_items))

        # Prapare the output template for the respective grid type
        output_data = {}
        if grid_type == GridType.Radical:
            output_data = {
                "Level": [],
                "Symbol": [],
                "Meaning": [],
                "Meaning Mnemonic": []
            }
        elif grid_type == GridType.Kanji:
            output_data = {
                "Level": [],
                "Symbol": [],
                "Meaning": [],
                "Radical Component Name": [],
                "Radical Component Symbol": [],
                "Meaning Mnemonic": [],
                "Reading Onyomi": [],
                "Reading Kunyomi": [],
                "Reading Nanori": [],
                "Reading Whitelist": [],
                "Reading Mnemonic": []
            }
        elif grid_type == GridType.Vocabulary:
            output_data = {
                "Level": [],
                "Symbol": [],
                "Meaning": [],
                "Kanji Component Name": [],
                "Kanji Component Symbol": [],
                "Meaning Mnemonic": [],
                "Word Type": [],
                "Reading": [],
                "Reading Whitelist": [],
                "Reading Mnemonic": [],
                "Reading Audio Male": [],
                "Reading Audio Female": [],
                "Context 1-EN": [],
                "Context 1-JP": [],
                "Context 2-EN": [],
                "Context 2-JP": [],
                "Context 3-EN": [],
                "Context 3-JP": [],
                "Context 4-EN": [],
                "Context 4-JP": []
            }

        # Find and save the respecive data for each symbol in the grid
        for item in chunk_converted_items:
            # Start the time tracking
            tracker.start()

            # Find the respective symbol data inside the page
            if grid_type == GridType.Radical:
                get_radical_data(item, output_data, site_session)

            elif grid_type == GridType.Kanji:
                get_kanji_data(item, output_data, site_session)

            elif grid_type == GridType.Vocabulary:
                get_vocabulary_data(item, output_data, GET_AUDIO, site_session)

            # End the time tracking and print result
            tracker.end()
            tracker.print_progress()
            tracker.print_stats()
            tracker.print_delay()
            print("\n")

        pd.DataFrame(data=output_data).to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data_Chunk_{ cur_chunk + 1 }.csv", index=False, sep="\t")

# region - Item Data
"""
    Some Comment
"""
def get_radical_data(item: Radical, output: {}, site_session: requests.sessions.Session) -> {}:
    """
    Pulls the data needed from the respective Radical's page.

    :param item: The Radical symbol object.
    :param output: Data output templates.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A dict containing all the data pulled from the respective Radical's page.
    """
    print(f"Current Item: Name ({item.name}) | Symbol: {item.symbol}")

    # Sets the Radical object's page soup
    item.set_page_soup(site_session)

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


def get_kanji_data(item: Kanji, output: {}, site_session: requests.sessions.Session) -> {}:
    """
    Pulls the data needed from the respective Kanji's page.

    :param item: The Kanji symbol object.
    :param output: Data output templates.
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A dict containing all the data pulled from the respective Kanji's page.
    """
    print(f"Current Item: Name ({item.name}) | Symbol: {item.symbol}")

    # Sets the Kanji object's page soup
    item.set_page_soup(site_session)

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
    reading_data = item.get_readings_data()
    readings = reading_data[0]
    output["Reading Onyomi"].append(readings[0]) # Gets the On'yomi reading in Hiragana
    output["Reading Kunyomi"].append(readings[1]) # Gets the Kun'yomi reading ""
    output["Reading Nanori"].append(readings[2]) # Gets the Nanori reading ""

    reading_whitelist = ",".join(reading_data[1])
    output["Reading Whitelist"].append(reading_whitelist)

    # Find the Mnemonic to easily remember the Reading
    reading_mnemonic = item.get_mnemonic(MnemonicType.Reading)
    output["Reading Mnemonic"].append(reading_mnemonic)

    return output


def get_vocabulary_data(item: Vocabulary, output: {}, get_audio: bool, site_session: requests.sessions.Session) -> {}:
    """
    Pulls the data needed from the respective Vocabulary's page.

    :param item: The Vocabulary symbol object.
    :param output: Data output templates.
    :param get_audio: # TODO: Update this
    :param site_session: The "logged in" state of the WaniKani site.
    :return: A dict containing all the data pulled from the respective Vocabulary's page.
    """
    print(f"Current Item: Name ({item.name}) | Symbol: {item.symbol}")

    # Sets the Vocabulary object's page soup
    item.set_page_soup(site_session)

    # Find the Level and Symbol
    output["Level"].append(item.get_level()) # (The level at which you learn this Vocabulary)
    output["Symbol"].append(item.symbol) # (a set of Kanji and Hiragana characters)

    # Find the Meanings (i.e. the most common words associated to this Vocabulary)
    # meanings = ",".join(item.get_meanings(MeaningType.Default))
    meaning_data = item.get_meaning_data(MeaningType.Vocabulary)
    meanings = ",".join(meaning_data[:-1])
    output["Meaning"].append(meanings)

    # Find the Kanji that make up this respective Kanji
    kanji_combination = item.get_kanji_components()
    output["Kanji Component Name"].append(",".join(kanji_combination[0]))
    output["Kanji Component Symbol"].append(",".join(kanji_combination[1]))

    # Find the Mnemonic to easily remember the Meaning
    meaning_mnemonic = item.get_mnemonic(MnemonicType.Meaning)
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    # Find the part of speech the Vocabulary belongs to
    output["Word Type"].append(meaning_data[-1])

    # Find the respective readings for this Vocabulary
    reading_data = item.get_readings_data()
    readings = ",".join(reading_data[0])
    output["Reading"].append(readings)

    reading_whitelist = ",".join(reading_data[1])
    output["Reading Whitelist"].append(reading_whitelist)

    # Find the Mnemonic to easily remember the Reading
    reading_mnemonic = item.get_mnemonic(MnemonicType.Reading)
    output["Reading Mnemonic"].append(reading_mnemonic)

    # Find the respective audio for each of this Vocabulary's readings
    # TODO: Clean/recode this method or Document it
    audio_reading_data = item.get_audio_reading_data()
    audio_data = item.get_audio_data(audio_reading_data)
    if get_audio:
        item.download_audio(audio_reading_data)

    output["Reading Audio Male"].append(",".join(audio_data["Male"]))
    output["Reading Audio Female"].append(",".join(audio_data["Female"]))

    # Find the context (examples) in which this Vocabulary is used in
    context_data = item.get_context_data()
    context_1_data = context_data["Context 1"]
    output["Context 1-EN"].append(context_1_data["EN"])
    output["Context 1-JP"].append(context_1_data["JP"])

    context_2_data = context_data["Context 2"]
    output["Context 2-EN"].append(context_2_data["EN"])
    output["Context 2-JP"].append(context_2_data["JP"])

    context_3_data = context_data["Context 3"]
    output["Context 3-EN"].append(context_3_data["EN"])
    output["Context 3-JP"].append(context_3_data["JP"])

    context_4_data = context_data["Context 4"]
    output["Context 4-EN"].append(context_4_data["EN"])
    output["Context 4-JP"].append(context_4_data["JP"])

    return output
# endregion
