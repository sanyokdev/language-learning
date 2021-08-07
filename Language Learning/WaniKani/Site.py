import json
import time

import requests
from bs4 import BeautifulSoup


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
        json_data = json.load(f)

        # Create payload
        payload = {
            "user[login]": json_data["username"],
            "user[password]": json_data["password"],
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

    if result.status_code != 200:
        while result.status_code != 200:
            print(f"ERROR: Could not load WaniKani page, status {result.status_code} - Retrying site load (3 sec per retry)")
            result = site_session.get(page_url, headers=dict(referer=page_url))
            time.sleep(3)

    return BeautifulSoup(result.content, "html.parser")
