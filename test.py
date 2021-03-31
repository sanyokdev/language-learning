# Internal
from WordManager import verbType
from WordManager import definition
from WordManager import tts

# External
import requests
from bs4 import BeautifulSoup
import re
import translatepy

transl = translatepy.Translator()


def get_word_example(word):
    url = "https://www.linguee.com/english-portuguese/search?source=portuguese&query=" + str(word)
    page = requests.get(url)
    site_soup = BeautifulSoup(page.content, "html.parser")

    example_lines = site_soup.find_all(class_="example_lines")
    examples_result_set = BeautifulSoup(str(example_lines), "html.parser").find_all(class_="tag_s")

    all_examples = []

    count = 0
    end_amount = 3
    for item in examples_result_set:
        count += 1
        filtered_text = re.search(r'>([^)]+)<', str(item)).group(1)
        all_examples.append(filtered_text)

        if count == end_amount:
            break

    output = []

    for example in all_examples:
        translation = transl.translate(example, "English")
        output.append([example, translation.result])

    return output


search_word = "brincar".lower()
print("--- Search Word: \n" + search_word + "\n")

print("--- Examples :")
for example in get_word_example(search_word):
    print("En : " + example[0])
    print("Pt : " + example[1])
    print()
