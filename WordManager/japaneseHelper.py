# External
import requests
import pandas as pd


def download_file(site_filename):
    filename = site_filename.split("/")[-1]
    raw_data = requests.get(site_filename, stream=True)

    with open("Output/" + filename, 'wb') as fd:
        for chunk in raw_data.iter_content(chunk_size=1024):
            fd.write(chunk)
    return


def get_kana_sound_files(kana_type):
    data_path = "Japanese/Hiragana/" + str(kana_type) + "/" + str(kana_type) + ".csv"
    column_data = pd.read_csv(data_path)["Kana"].T.values.tolist()

    for val in column_data:
        download_file("https://files.tofugu.com/articles/japanese/2014-06-30-learn-hiragana/" + str(val) + ".mp3")


# Used for Kana Symbol learning
def create_anki_kana_deck(syllabary_type, kana_type, card_type):
    data_path = "Japanese/" + str(syllabary_type) + "/" + str(kana_type) + "/"
    output_path = "Output/Anki_JP_" + str(card_type) + "_" + str(syllabary_type) + "_" + str(kana_type) + ".csv"

    csv_data = pd.read_csv(data_path + str(kana_type) + ".csv")

    romaji_col_data = csv_data["Romaji"].T.values.tolist()
    kana_col_data = csv_data["Kana"].T.values.tolist()
    type_col_data = csv_data["Type"].T.values.tolist()

    row_data = []
    data_length = len(kana_col_data)  # Sort of arbitrary but whatever

    for i in range(data_length):
        kana_data = str(kana_col_data[i])

        if str(card_type) == "Symbol":
            # Columns: | 0 - Romaji | 1 - Kana | 2 - Audio | 3 - Type |
            audio_data = "[sound:" + kana_data + ".mp3]"
            row_data.append([romaji_col_data[i], kana_data, audio_data, type_col_data[i]])

        elif str(card_type) == "Stroke":
            # Columns: | 0 - Romaji | 1 - Image | 2 - Type |
            image_data = "<img src=\'" + kana_data + ".png" + "\'>"
            row_data.append([romaji_col_data[i], image_data, type_col_data[i]])

    output_file = pd.DataFrame(row_data)
    output_file.to_csv(output_path, header=False, index=False, sep=";", encoding="utf-8-sig")

