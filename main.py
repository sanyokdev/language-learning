# Internal
from WordManager import verbType
from WordManager import definition
from WordManager import tts

# External
import requests
from bs4 import BeautifulSoup
import yaml
import re


def create_audio_files(word_type):
    words_file = "Data/Input/Words/" + str(word_type) + ".txt"
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


# word_type = "Noun"
# with open("Data/Input/Words/" + str(word_type) + ".txt", mode="r", encoding='utf8') as file:
#     for word in file.read().splitlines():
#         print(word)

# site_soup = verbType.get_site_soup("haver")

# irregular_list = site_soup.find("irreg").contents
# if irregular_list[0] != "exemplo":
#     exit()

# print(verbType.get_translation(site_soup))

# INDICATIVO
# print("INDICATIVO:\n" + yaml.dump(verbType.get_modo_indicativo(site_soup),
#                                    default_flow_style=False, allow_unicode=True, sort_keys=False))

# CONJUNTIVO
# print("CONJUNTIVO:\n" + yaml.dump(verbType.get_modo_conjuntivo(site_soup),
#                                    default_flow_style=False, allow_unicode=True, sort_keys=False))

# IMPERATIVO
# print("IMPERATIVO:\n" + yaml.dump(verbType.get_modo_imperativo(site_soup),
#                                    default_flow_style=False, allow_unicode=True, sort_keys=False))

# INFINITIVO PESSOAL
# print("INFINITIVO PESSOAL:\n" + yaml.dump(verbType.get_modo_infinitivo_pessoal(site_soup),
#                                    default_flow_style=False, allow_unicode=True, sort_keys=False))

# search_word = "conhecimento".lower()
# url = "https://www.linguee.com/english-portuguese/search?source=portuguese&query=" + str(search_word)
# page = requests.get(url)
# site_soup = BeautifulSoup(page.content, "html.parser")

# example_lines = site_soup.find_all(class_="example_lines")
# examples_result_set = BeautifulSoup(str(example_lines), "html.parser").find_all(class_="tag_s")

# all_examples = []
# for item in examples_result_set:
#     filtered_text = re.search(r'\>([^)]+)\<', str(item)).group(1)
#     all_examples.append(filtered_text)

# print(all_examples)

def downloadFile(siteFileName):
    filename = siteFileName.split("/")[-1]
    rawData = requests.get(siteFileName, stream=True)

    with open("Output/" + filename, 'wb') as fd:
        for chunk in rawData.iter_content(chunk_size=1024):
            fd.write(chunk)
    return


kana = "あ"
downloadFile("https://files.tofugu.com/articles/japanese/2014-06-30-learn-hiragana/" + kana + ".mp3")
