import tts
import definition

import requests
from bs4 import BeautifulSoup
import yaml
import re

from wordManager import verbType


def create_audio_files(word_type):
    words_file = "Data/Input/Words/" + str(word_type) + ".txt"
    meaning_file = "Data/Input/Meaning/" + str(word_type) + ".txt"
    sound_base_name = str(word_type).capitalize() + "SND"

    tts.convert_file(words_file, sound_base_name, "Data/Output/Audio/" + str(word_type))


def create_anki_file(word_type):
    words_file = "Data/Input/Words/" + str(word_type) + ".txt"
    meaning_file = "Data/Input/Meaning/" + str(word_type) + ".txt"
    sound_base_name = str(word_type) + "SND"

    definition.convert_file_into_anki_import(
        words_file,
        meaning_file,
        sound_base_name,
        "Data/Output/Anki/" + str(word_type) + "Import.txt",
        str(word_type).lower()
    )


# create_audio_files("Noun")
# create_anki_file("Noun")


search_word = "falar"
url = "https://conjuga-me.net/verbo-" + str(search_word)
page = requests.get(url)
site_soup = BeautifulSoup(page.content, "html.parser")

# INDICATIVO
print("INDICATIVO:\n" + yaml.dump(verbType.get_modo_indicativo(site_soup),
                                  default_flow_style=False, allow_unicode=True, sort_keys=False))

# CONJUNTIVO
print("CONJUNTIVO:\n" + yaml.dump(verbType.get_modo_conjuntivo(site_soup),
                                  default_flow_style=False, allow_unicode=True, sort_keys=False))

# IMPERATIVO
print("IMPERATIVO:\n" + yaml.dump(verbType.get_modo_imperativo(site_soup),
                                  default_flow_style=False, allow_unicode=True, sort_keys=False))

# INFINITIVO PESSOAL
print("INFINITIVO PESSOAL:\n" + yaml.dump(verbType.get_modo_infinitivo_pessoal(site_soup),
                                  default_flow_style=False, allow_unicode=True, sort_keys=False))
