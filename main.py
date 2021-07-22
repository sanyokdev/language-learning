from Japanese.Src import WaniKani

"""
characterGrid = soup.find("section", {"class", "lattice-single-character"})
characterElements = characterGrid.find_all("a", href=True)
output = []

total = len(characterElements)
count = 0
for element in characterElements:
    charHref = element["href"]
    characterUrl = "https://www.wanikani.com" + str(charHref)
    charSoup = get_site_wanikani_soup(characterUrl)
    iconElement = charSoup.find("span", {"class", "radical-icon"})

    dataCheck = re.search(r"</?[a-z][\s\S]*>", str(iconElement.contents)) is not None
    display = ""

    if dataCheck:
        output.append(iconElement.contents)
        display = " | " + str(charHref.split("/")[2]).capitalize()

    count += 1
    percent = " | " + str(round((count / total) * 100, 2)) + "% Complete"
    print(str(count) + "/" + str(total) + percent + display)

print(output)
"""

session = WaniKani.get_session()
url = WaniKani.GetURL.VocabularyGrid.value
soup = WaniKani.get_page(url, session)
print(soup)
