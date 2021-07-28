from enum import Enum

import requests
from bs4 import BeautifulSoup

import Common.helper as helper

"""
    Some Comment
"""
class GetLvl(Enum): # The "Japanese-Language Proficiency Test" levels
    N5 = 0
    N4 = 1
    N3 = 2
    N2 = 3
    N1 = 4


"""
    Some Comment
"""
def get_kanji_for_level(level: GetLvl):
    url = "https://www.kanshudo.com/collections/jlpt_kanji"
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, "html.parser")

    levelPanels = soup.find_all("div", {"class": "infopanel"})
    symbolElements = levelPanels[level.value].find_all("a")

    symbols = []
    for element in symbolElements:
        symbols.append(helper.get_element_text(element))

    return symbols


"""
    Some Comment
"""
def get_all_joyo_kanji():
    listN5 = get_kanji_for_level(GetLvl.N5)
    listN4 = get_kanji_for_level(GetLvl.N4)
    listN3 = get_kanji_for_level(GetLvl.N3)
    listN2 = get_kanji_for_level(GetLvl.N2)
    listN1 = get_kanji_for_level(GetLvl.N1)

    return listN5 + listN4 + listN3 + listN2 + listN1
