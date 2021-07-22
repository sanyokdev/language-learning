import re

import pandas as pd
import requests

from Japanese.Src import WaniKani




"""
    TODO: TURN THIS INTO A FUNCTION
"""
session = WaniKani.get_session()

gridData = WaniKani.get_grid_data(WaniKani.GridType.Radical, session)
# with pd.option_context("display.max_rows", None, "display.max_columns", None):
#     print(gridData)

count = 0;
for item in gridData.Symbol:
    test = re.search(r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)", item)
    if test is not None:
        url = test.group(0)
        page = requests.get(url)

        with open("Japanese/Output/" + str(count) + ".png", 'wb') as f:
            f.write(page.content)

        # print(test.group(0))

    count += 1
