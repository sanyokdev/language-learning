import pandas as pd

import requests
from bs4 import BeautifulSoup, Tag

import LanguageLearning.WaniKani.Site as Site
import LanguageLearning.WaniKani.Data as Data


"""
    Some Comment
"""
class _Common:
    def __init__(self, name: str, symbol: str, url: str):
        self.name = name
        self.symbol = symbol
        self.url = url

    def get_page_soup(self, site_session: requests.sessions.Session):
        return Site.get_page(self.url, site_session)

    def get_level(self, site_soup: BeautifulSoup):
        return site_soup.find("a", {"class": "level-icon"}).contents[0]

    def get_meaning_mnemonic(self, site_soup: BeautifulSoup):
        meaning_elements = site_soup.find("section", {"class": "mnemonic-content"}).find_all("p")
        meaning_list = []

        for element in meaning_elements:
            content = element.contents
            content_text = ""

            for item in content:
                if type(item) == Tag:
                    item_class_list = item.get("class")
                    if item_class_list is not None:
                        item_class = item_class_list[0]
                    else:
                        item_class = None

                    item_content = item.contents[0]

                    if item_class == "radical-highlight":
                        item_tag = f"<radical>{item_content}</radical>"
                    elif item_class == "kanji-highlight":
                        item_tag = f"<kanji>{item_content}</kanji>"
                    elif item_class == "vocabulary-highlight":
                        item_tag = f"<vocabulary>{item_content}</vocabulary>"
                    else:
                        item_tag = f"<jp>{item_content}</jp>"

                    content_text += item_tag
                else:
                    content_text += str(item)

            meaning_list.append(content_text)
        return meaning_list

    def get_reading(self, site_soup: BeautifulSoup):
        pass

    def get_reading_meaning(self, site_soup: BeautifulSoup):
        pass


class Radical(_Common):
    def get_reading(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading'")

    def get_reading_meaning(self, site_soup: BeautifulSoup):
        raise NotImplementedError("'Radical' object has no attribute 'get_reading_meaning'")


class Kanji(_Common):
    def get_radical_combination(self, site_soup: BeautifulSoup):
        pass


class Vocabulary(_Common):
    def get_word_type(self, site_soup: BeautifulSoup):
        pass

    def get_en_context_list(self, site_soup: BeautifulSoup):
        pass

    def get_jp_context_list(self, site_soup: BeautifulSoup):
        pass


"""
    Some Comment
"""
def to_item_list(data: pd.DataFrame):
    output = []
    for i in range(len(data.Name)):
        output.append(_Common(data.Name[i], data.Symbol[i], data.Url[i]))
    return output


"""
    Some Comment
"""
def convert_type(item: _Common, item_type: Data.GridType):
    if item_type == Data.GridType.Radical:
        return Radical(item.name, item.symbol, item.url)
    elif item_type == Data.GridType.Kanji:
        return Kanji(item.name, item.symbol, item.url)
    else: # GridType.Vocabulary
        return Vocabulary(item.name, item.symbol, item.url)
