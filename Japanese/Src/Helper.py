from enum import Enum
import re

import numpy


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
def get_element_text(element: str):
    return str(re.search(r">(.*?)<", element).group(1))


def get_original_title(element: str):
    return str(re.search(r".+?(?=<br>)", element).group(0))


"""
    Some Comment
"""
def sort_kanji_to_specific_order(presetData, unsortedData):
    dataID = []

    for item in unsortedData:
        indexID = -1
        if item in presetData:
            indexID = presetData.index(item)

        dataID.append(indexID)

    unsorted = numpy.array(unsortedData)
    dataID = numpy.array(dataID)
    inds = dataID.argsort()
    return unsorted[inds].tolist()
