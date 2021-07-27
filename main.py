import re

import pandas as pd
import requests

from Japanese.Src import WaniKani


# """ - Radical Data
session = WaniKani.get_session()
grid_type = WaniKani.GridType.Radical
output_data = WaniKani.get_grid_item_data(0.7, grid_type, session)
print(output_data)
output_data.to_csv(f"Japanese/Output/WaniKani_{str(grid_type)}_Data.csv", index=False)


# session = WaniKani.get_session()
# output_data = WaniKani.get_all_kanji_data(session)
