import json
from enum import Enum

import requests
from bs4 import BeautifulSoup


"""
    Some Comment
"""
class GetURL(Enum):
    Radicals = "https://www.wanikani.com/radicals" # can append "/RADICAL_NAME" to access a specific radical page
    Kanji = "https://www.wanikani.com/kanji" # can append "/KANJI_SYMBOL" to access a specific kanji page
    Vocabulary = "https://www.wanikani.com/vocabulary" # can append "/VOCABULARY_SYMBOL(S)" to access a specific vocabulary page

    RadicalGrid = "https://www.wanikani.com/lattice/radicals/meaning"
    KanjiGrid = "https://www.wanikani.com/lattice/kanji/combined"
    VocabularyGrid = "https://www.wanikani.com/lattice/vocabulary/combined"

    Level = "https://www.wanikani.com/level" # can append "/LEVEL_NUMBER" to access a specific level page


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
