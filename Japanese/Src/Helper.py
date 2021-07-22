import re

import numpy


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
