import re

import numpy
import requests

"""
    Some Comment
"""
def get_element_text(element: str):
    return str(re.search(r">(.*?)<", element).group(1))


def get_original_title(element: str):
    return str(re.search(r".+?(?=<br>)", element).group(0))


"""
    Some Comment
"""
def sort_kanji_to_specific_order(presetData, unsortedData):
    dataID = []

    for item in unsortedData:
        indexID = -1
        if item in presetData:
            indexID = presetData.index(item)

        dataID.append(indexID)

    unsorted = numpy.array(unsortedData)
    dataID = numpy.array(dataID)
    inds = dataID.argsort()
    return unsorted[inds].tolist()


"""
    Some Comment
"""
def download_site_file(filename: str, filetype: str, url: str):
    local_filename = filename + filetype

    r = requests.get(url)

    with open(f"-Output/Audio/{ local_filename }", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
