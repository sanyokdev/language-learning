import numpy
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from enum import Enum

# region --- Enums

class RTKVersion(Enum): # The "Remembering the Kanji" by James Heisig books
    V1 = "https://hochanh.github.io/rtk/rtk1-v6/index.html"
    V3 = "https://hochanh.github.io/rtk/rtk3-remain/index.html"

class JLPTLvl(Enum): # The "Japanese-Language Proficiency Test" levels
    N5 = 0
    N4 = 1
    N3 = 2
    N2 = 3
    N1 = 4

class DataFilepath(Enum): # The filepath of the data files
    RTK = "Japanese/Data/RTK/"
    JLTP = "Japanese/Data/JLTP/"


# endregion

# region --- Definitions


"""
    Some Comment
"""
def get_element_text(element):
    return str(re.search(r">(.*?)<", str(element)).group(1))


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


# region - RTK


"""
    Some Comment
"""
def get_kanji_rtk_preset(version: RTKVersion):
    url = version.value
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    symbolElements = soup.find_all("a")[:-2]

    symbolList = []
    for element in symbolElements:
        symbolList.append(get_element_text(element))

    return symbolList


"""
    Some Comment
"""
def save_rtk_preset_as_csv(version: RTKVersion):
    presetList = get_kanji_rtk_preset(version)

    d = {'Kanji': presetList}
    df = pd.DataFrame(data=d)

    filepath = DataFilepath.RTK.value
    df.to_csv(f"{filepath + str(version.name)}.csv", index=False, encoding="utf-8-sig")


"""
    Some Comment
"""
def load_rtk_as_list(version: RTKVersion):
    filepath = DataFilepath.RTK.value
    output = pd.read_csv(f"{filepath + str(version.name)}.csv").Kanji.to_list()

    return output


"""
    Some Comment
"""
def load_all_rtk_as_list():
    return load_rtk_as_list(RTKVersion.V1) + load_rtk_as_list(RTKVersion.V3)


# endregion

# region - JLTP

"""
    Some Comment
"""
def get_kanji_for_jlpt_level(level: JLPTLvl):
    url = "https://www.kanshudo.com/collections/jlpt_kanji"
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, "html.parser")

    levelPanels = soup.find_all("div", {"class": "infopanel"})
    symbolElements = levelPanels[level.value].find_all("a")

    symbols = []
    for element in symbolElements:
        symbols.append(get_element_text(element))

    return symbols


# endregion


# endregion

