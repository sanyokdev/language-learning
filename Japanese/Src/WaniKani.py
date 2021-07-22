import json
import re
from enum import Enum
import pandas as pd

import requests
from bs4 import BeautifulSoup

from Japanese.Src import Helper

"""
    Some Comment
"""
"""
class GetURL(Enum):
    Radicals = "https://www.wanikani.com/radicals" # can append "/RADICAL_NAME" to access a specific radical page
    Kanji = "https://www.wanikani.com/kanji" # can append "/KANJI_SYMBOL" to access a specific kanji page
    Vocabulary = "https://www.wanikani.com/vocabulary" # can append "/VOCABULARY_SYMBOL(S)" to access a specific vocabulary page

    Level = "https://www.wanikani.com/level" # can append "/LEVEL_NUMBER" to access a specific level page
"""

class GridType(Enum):
    Radical = "https://www.wanikani.com/lattice/radicals/meaning"
    Kanji = "https://www.wanikani.com/lattice/kanji/combined"
    Vocabulary = "https://www.wanikani.com/lattice/vocabulary/combined"


"""
    Some comment
"""
def get_session():
    login_url = "https://www.wanikani.com/login"

    site_session = requests.session()

    # Get login authentication token
    result = site_session.get(login_url)
    soup = BeautifulSoup(result.content, "html.parser")
    token_element = soup.find("input", {"name": "authenticity_token"})

    if token_element is not None:
        authenticity_token = token_element["value"]
    else:
        print("ERROR: Could not find the authenticity_token element")
        return None

    with open("Credentials/WaniKaniLogin.json", encoding="utf-8") as f:
        data = json.load(f)

        # Create payload
        payload = {
            "user[login]": data["username"],
            "user[password]": data["password"],
            "authenticity_token": authenticity_token
        }

        # Perform login
        result = site_session.post(login_url, data=payload, headers=dict(referer=login_url))

        if result.ok:
            return site_session
        else:
            print("ERROR: Could not complete WaniKani login")


"""
    Some comment
"""
def get_page(page_url: str, site_session: requests.sessions.Session):
    if site_session is None:
        print("ERROR: Could not load WaniKani page, session is None")
        return None

    result = site_session.get(page_url, headers=dict(referer=page_url))

    if result.status_code == 404:
        print("ERROR: Could not load WaniKani page, status 404")
        return None

    return BeautifulSoup(result.content, "html.parser")


"""
    Some comment
"""
def get_grid_data(gridType: GridType, site_session: requests.sessions.Session):
    url = gridType.value
    soup = get_page(url, site_session)

    if gridType == GridType.Vocabulary:
        latticeType = "lattice-multi-character"
    else:
        latticeType = "lattice-single-character"

    itemGrid = soup.find("section", {"class", latticeType})
    itemElements = itemGrid.find_all("a", attrs={"href": True})

    gridData = {"Name": [], "Symbol": [], "Href": []}

    for element in itemElements:
        symbolText = element.text

        if gridType == GridType.Radical:
            nameItem = element["title"]

            imageElement = element.find("img")
            if imageElement is not None:
                symbolText = imageElement["src"].replace("medium", "large")
        else:
            nameItem = Helper.get_original_title(element["title"])


        gridData["Name"].append(nameItem)
        gridData["Symbol"].append(symbolText)
        gridData["Href"].append(element["href"])

    return pd.DataFrame(data=gridData)


"""

total = len(characterElements)
count = 0

for element in characterElements:
    charHref = element["href"]
    
    characterUrl = "https://www.wanikani.com" + str(charHref)
    charSoup = get_page(characterUrl, site_session)
    iconElement = charSoup.find("span", {"class", "radical-icon"})
    
    output.append(iconElement.contents)
    display = " | " + str(charHref.split("/")[2]).capitalize()
    
    count += 1
    percent = " | " + str(round((count / total) * 100, 2)) + "% Complete"
    print(str(count) + "/" + str(total) + percent + display)
"""
