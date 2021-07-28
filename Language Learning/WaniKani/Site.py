import json
import pandas as pd

import requests
from bs4 import BeautifulSoup

# import Common.
# import WaniKani.Data as Data


"""
    Some Comment
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
    Some Comment
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
    Some Comment
"""
def get_grid_data(gridType: Data.GridType, site_session: requests.sessions.Session):
    url = gridType.value
    soup = get_page(url, site_session)

    if gridType == Data.GridType.Vocabulary:
        latticeType = "lattice-multi-character"
    else:
        latticeType = "lattice-single-character"

    itemGrid = soup.find("section", {"class", latticeType})
    itemElements = itemGrid.find_all("a", attrs={"href": True})

    gridData = {"Name": [], "Symbol": [], "Url": []}

    for element in itemElements:
        symbolText = element.text

        if gridType == Data.GridType.Radical:
            nameItem = element["title"]

            imageElement = element.find("img")
            if imageElement is not None:
                symbolText = f'<i class="radical-{nameItem.lower().replace(" ", "-")}"></i>'
        else:
            nameItem = Helper.get_original_title(element["title"])

        gridData["Name"].append(nameItem)
        gridData["Symbol"].append(symbolText)
        gridData["Url"].append("https://www.wanikani.com" + element["href"])

    return pd.DataFrame(data=gridData)
