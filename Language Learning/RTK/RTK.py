from enum import Enum
import pandas as pd

import requests
from bs4 import BeautifulSoup

import Common.filepaths as filepaths
import Common.helper as helper


"""
    Some Comment
"""
class RTKVersion(Enum): # The "Remembering the Kanji" by James Heisig books
    V1 = "https://hochanh.github.io/rtk/rtk1-v6/index.html"
    V3 = "https://hochanh.github.io/rtk/rtk3-remain/index.html"


"""
    Some Comment
"""
def get_kanji_preset(version: RTKVersion) -> []:
    url = version.value
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    symbolElements = soup.find_all("a")[:-2]

    symbolList = []
    for element in symbolElements:
        symbolList.append(element.contents[0])

    return symbolList


"""
    Some Comment
"""
def save_preset_as_csv(version: RTKVersion):
    presetList = get_kanji_preset(version)

    d = {'Kanji': presetList}
    df = pd.DataFrame(data=d)

    filepath = filepaths.GetPath.RTK.value
    df.to_csv(f"{filepath + str(version.name)}.csv", index=False, encoding="utf-8-sig")


"""
    Some Comment
"""
def load_as_list(version: RTKVersion):
    filepath = filepaths.GetPath.RTK.value
    output = pd.read_csv(f"{filepath + str(version.name)}.csv").Kanji.to_list()

    return output


"""
    Some Comment
"""
def load_all_as_list():
    return load_as_list(RTKVersion.V1) + load_as_list(RTKVersion.V3)
