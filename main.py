# Internal
from WordManager import japaneseHelper as jpHelper

# External
import pandas as pd
import requests
import yaml
import re


# jpHelper.get_kana_sound_files("Main")
jpHelper.create_anki_kana_deck("Hiragana", "Main", "Symbol")
jpHelper.create_anki_kana_deck("Hiragana", "Main", "Stroke")
