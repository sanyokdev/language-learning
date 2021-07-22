import numpy
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from enum import Enum
from urllib.parse import unquote

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

def get_all_joyo_kanji():
    listN5 = get_kanji_for_jlpt_level(JLPTLvl.N5)
    listN4 = get_kanji_for_jlpt_level(JLPTLvl.N4)
    listN3 = get_kanji_for_jlpt_level(JLPTLvl.N3)
    listN2 = get_kanji_for_jlpt_level(JLPTLvl.N2)
    listN1 = get_kanji_for_jlpt_level(JLPTLvl.N1)

    return listN5 + listN4 + listN3 + listN2 + listN1
# endregion


# endregion


# print(len(get_all_joyo_kanji()))

def get_wanikani_link_type(link: str):
    return unquote(link).split("/")[3]


def get_wanikani_link_symbol(link: str):
    return unquote(link).split("/")[4]


def get_site_wanikani_soup(url: str):
    page = requests.get(url, headers={"check the stickie notes ;) - uses private login data"
    })

    return BeautifulSoup(page.content, "html.parser")


soup = get_site_wanikani_soup("https://www.wanikani.com/lattice/radicals/meaning")
characterGrid = soup.find("section", {"class", "lattice-single-character"})
characterElements = characterGrid.find_all("a", href=True)
output = []

total = len(characterElements)
count = 0
for element in characterElements:
    charHref = element["href"]
    characterUrl = "https://www.wanikani.com" + str(charHref)
    charSoup = get_site_wanikani_soup(characterUrl)
    iconElement = charSoup.find("span", {"class", "radical-icon"})

    dataCheck = re.search(r"</?[a-z][\s\S]*>", str(iconElement.contents)) is not None
    display = ""

    if dataCheck:
        output.append(iconElement.contents)
        display = " | " + str(charHref.split("/")[2]).capitalize()

    count += 1
    percent = " | " + str(round((count / total) * 100, 2)) + "% Complete"
    print(str(count) + "/" + str(total) + percent + display)

print(output)

# meaning = get_site_soup("https://www.wanikani.com/vocabulary/留守番").find("section", {"class": "mnemonic-content"}).find("p").contents
# radicalList = get_site_wanikani_soup("https://www.wanikani.com/lattice/radicals/meaning").find("section", {"class", "lattice-single-character"}).find_all("li")
# print(len(radicalList))

# vocabularyList = get_site_wanikani_soup("https://www.wanikani.com/lattice/vocabulary/combined").find("section", {"class", "lattice-multi-character"}).find_all("li")
# print(len(vocabularyList))

# kanjiList = get_site_wanikani_soup("https://www.wanikani.com/lattice/kanji/combined").find("section", {"class", "lattice-single-character"}).find_all("li")
# print(len(kanjiList))
