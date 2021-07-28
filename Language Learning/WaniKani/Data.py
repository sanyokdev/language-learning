from enum import Enum

import pandas as pd
import requests

import LanguageLearning.Common.Stats as Stats
import LanguageLearning.WaniKani.Site as Site
import LanguageLearning.WaniKani.ItemType as ItemType


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


"""
    Some Comment
"""
def get_grid_items(delay: float, grid_type: GridType, site_session: requests.sessions.Session):
    # Get item data from the grid page
    grid_items = ItemType.to_item_list(Site.get_grid_data(grid_type, site_session))
    item_list = [ItemType.convert_type(item, grid_type) for item in grid_items]

    # Set up the progress tracking
    tracker = Stats.TimeTracker(delay, total_items=len(item_list))

    # Find and save the respecive data for each symbol in the grid
    output_data = {}
    for item in item_list:
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

    return pd.DataFrame(data=output_data)


"""
    Some Comment
"""
def get_radical_data(item: ItemType.Radical, site_session: requests.sessions.Session):
    page_soup = item.get_page_soup(site_session)

    output = DataPresets.RADICAL.value
    output["Level"].append(item.get_level(page_soup))
    output["Symbol"].append(item.symbol)

    output["Meaning"].append(item.name)
    meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    print(output)
    return output


def get_kanji_data(item: ItemType.Kanji, site_session: requests.sessions.Session):
    page_soup = item.get_page_soup(site_session)

    output = DataPresets.Kanji.value
    output["Level"].append(item.get_level(page_soup))
    output["Symbol"].append(item.symbol)

    output["Radical Combination"].append(item.name)

    output["Meaning"].append(item.name)
    meaning_mnemonic = "\n".join(item.get_meaning_mnemonic(page_soup))
    output["Meaning Mnemonic"].append(meaning_mnemonic)

    output["Reading"].append(item.name)
    output["Reading Mnemonic"].append(item.name)

    print(output)
    return output


def get_vocabulary_data(item: ItemType.Vocabulary, site_session: requests.sessions.Session):
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

    print(output)
    return output
