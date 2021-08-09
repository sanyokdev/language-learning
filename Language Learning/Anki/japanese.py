import pandas as pd


def generate_radical_deck():
    radical_data = pd.read_excel("D:\Python Dev\Language-Learning Repo\Japanese Data\Complete\WaniKani_Radical_Data.xlsx")

    output_data = {
        "Level": [],
        "Radical": [],
        "Meaning": [],
        "Meaning Elements": [],
        "Meaning Mnemonic": [],
        "Type": [],
        "DO NOT CHANGE": [],
        "Tags": []
    }

    for i in range(len(radical_data["Level"])):
        output_data["Level"].append(radical_data["Level"][i])
        output_data["Radical"].append(radical_data["Symbol"][i])

        output_data["Meaning"].append(radical_data["Meaning"][i])
        output_data["Meaning Elements"].append(f'<p class="element-item primary">{ radical_data["Meaning"][i] }</p>')

        output_data["Meaning Mnemonic"].append(radical_data["Meaning Mnemonic"][i])

        output_data["Type"].append("Radical")
        output_data["DO NOT CHANGE"].append("-")

        output_data["Tags"].append(f'Radical Level_{ radical_data["Level"][i] }')

    pd.DataFrame(data=output_data).to_csv("-Output/Anki_Radical_Notes.csv", index=False, header=False, sep="\t")


def generate_kanji_meaning_deck():
    kanji_data = pd.read_excel("D:\Python Dev\Language-Learning Repo\Japanese Data\Complete\WaniKani_Kanji_Data.xlsx")

    output_data = {
        "Level": [],
        "Kanji": [],
        "Meaning": [],
        "Meaning Elements": [],
        "Radical Components": [],
        "Meaning Mnemonic": [],
        "Type": [],
        "DO NOT CHANGE": [],
        "Tags": []
    }

    for i in range(len(kanji_data["Level"])):
        output_data["Level"].append(kanji_data["Level"][i])
        output_data["Kanji"].append(kanji_data["Symbol"][i])

        # region Meaning
        output_data["Meaning"].append(kanji_data["Meaning"][i])

        meanings = kanji_data["Meaning"][i].split(",")
        m_elements = ""

        for e_id in range(len(meanings)):
            meaning = meanings[e_id]

            if e_id == 0:
                m_elements += f'<p class="element-item primary"> { meaning } </p>'
            else:
                m_elements += f',<p class="element-item"> { meaning } </p>'

        output_data["Meaning Elements"].append(m_elements)
        # endregion

        # region Components
        component_symbols = kanji_data["Radical Component Symbol"][i].split(",")
        component_names = kanji_data["Radical Component Name"][i].split(",")
        component_items = ""

        for c_id in range(len(component_names)):
            symbol_tag = f'<span><jp-symbol>{ component_symbols[c_id] }</jp-symbol></span>'
            name_tag = f'<p>{ component_names[c_id] }</p>'

            item_tag = f'<radical class="component">{ symbol_tag }{ name_tag }</radical>'
            component_items += item_tag

        component_grid = f'<div class="component-grid">{ component_items }</div>'
        output_data["Radical Components"].append(component_grid)
        # endregion

        output_data["Meaning Mnemonic"].append(kanji_data["Meaning Mnemonic"][i])

        output_data["Type"].append("Kanji Meaning")
        output_data["DO NOT CHANGE"].append("-")

        output_data["Tags"].append(f'Kanji_Meaning Level_{ kanji_data["Level"][i] }')

    pd.DataFrame(data=output_data).to_csv("-Output/Anki_Kanji_Meaning_Notes.csv", index=False, header=False, sep="\t")


def generate_vocabulary_meaning_deck():
    vocabulary_data = pd.read_excel("D:\Python Dev\Language-Learning Repo\Japanese Data\Complete\WaniKani_Vocabulary_Data.xlsx")

    output_data = {
        "Level": [],
        "Vocabulary": [],
        "Word Type": [],
        "Meaning": [],
        "Meaning Elements": [],
        "Kanji Components": [],
        "Meaning Mnemonic": [],
        "Context Elements": [],
        "Type": [],
        "DO NOT CHANGE": [],
        "Tags": []
    }

    for i in range(len(vocabulary_data["Level"])):
        output_data["Level"].append(vocabulary_data["Level"][i])
        output_data["Vocabulary"].append(vocabulary_data["Symbol"][i])
        output_data["Word Type"].append(vocabulary_data["Word Type"][i].replace(",", ", "))

        # region Meaning
        output_data["Meaning"].append(vocabulary_data["Meaning"][i])

        meanings = vocabulary_data["Meaning"][i].split(",")
        m_elements = ""

        for e_id in range(len(meanings)):
            meaning = meanings[e_id]

            if e_id == 0:
                m_elements += f'<p class="element-item primary"> { meaning } </p>'
            else:
                m_elements += f',<p class="element-item"> { meaning } </p>'

        output_data["Meaning Elements"].append(m_elements)
        # endregion

        # region Components
        component_symbols = vocabulary_data["Kanji Component Symbol"][i].split(",")
        component_names = vocabulary_data["Kanji Component Name"][i].split(",")
        component_items = ""

        for c_id in range(len(component_names)):
            symbol_tag = f'<span><jp-symbol>{ component_symbols[c_id] }</jp-symbol></span>'
            name_tag = f'<p>{ component_names[c_id] }</p>'

            item_tag = f'<kanji class="component">{ symbol_tag }{ name_tag }</kanji>'
            component_items += item_tag

        component_grid = f'<div class="component-grid">{ component_items }</div>'
        output_data["Kanji Components"].append(component_grid)
        # endregion

        output_data["Meaning Mnemonic"].append(vocabulary_data["Meaning Mnemonic"][i])

        # region Context
        context_items = ""

        for x in range(1, 5):
            item_title = f'<h1>Context { str(x) }</h1>'
            jp_text = vocabulary_data[f"Context { str(x) }-JP"][i]

            if jp_text != "None":
                en_text = f'<p> { vocabulary_data[f"Context { str(x) }-EN"][i] } </p>'

                context_items += f'<div class="context-item">{ item_title }{ jp_text }{ en_text }</div>'

        context_grid = f'<div class="context-grid">{ context_items }</div>'
        output_data["Context Elements"].append(context_grid)
        # endregion

        output_data["Type"].append("Vocabulary Meaning")
        output_data["DO NOT CHANGE"].append("-")

        output_data["Tags"].append(f'Vocabulary_Meaning Level_{ vocabulary_data["Level"][i] }')

    pd.DataFrame(data=output_data).to_csv("-Output/Anki_Vocabulary_Meaning_Notes.csv", index=False, header=False, sep="\t")


def generate_kanji_reading_deck():
    kanji_data = pd.read_excel("D:\Python Dev\Language-Learning Repo\Japanese Data\Complete\WaniKani_Kanji_Data.xlsx")

    output_data = {
        "Level": [],
        "Kanji": [],
        "Reading Whitelist": [],
        "Reading Elements": [],
        "Reading Mnemonic": [],
        "Type": [],
        "DO NOT CHANGE": [],
        "Tags": []
    }

    for i in range(len(kanji_data["Level"])):
        output_data["Level"].append(kanji_data["Level"][i])
        output_data["Kanji"].append(kanji_data["Symbol"][i])

        # region Reading
        output_data["Reading Whitelist"].append(kanji_data["Reading Whitelist"][i])
        reading_items = [
            f'<div class="reading-item"><h1>On\'yomi</h1>{ kanji_data["Reading Onyomi"][i] }</div>',
            f'<div class="reading-item"><h1>Kun\'yomi</h1>{kanji_data["Reading Kunyomi"][i]}</div>',
            f'<div class="reading-item"><h1>Nanori</h1>{kanji_data["Reading Nanori"][i]}</div>'
        ]

        reading_grid = f'<div class="reading-grid">{ "".join(reading_items) }</div>'
        output_data["Reading Elements"].append(reading_grid)

        output_data["Reading Mnemonic"].append(kanji_data["Reading Mnemonic"][i])
        # endregion

        output_data["Type"].append("Kanji Reading")
        output_data["DO NOT CHANGE"].append("-")

        output_data["Tags"].append(f'Kanji_Reading Level_{ kanji_data["Level"][i] }')

    pd.DataFrame(data=output_data).to_csv("-Output/Anki_Kanji_Reading_Notes.csv", index=False, header=False, sep="\t")

def generate_vocabulary_reading_deck():
    vocabulary_data = pd.read_excel("D:\Python Dev\Language-Learning Repo\Japanese Data\Complete\WaniKani_Vocabulary_Data.xlsx")

    output_data = {
        "Level": [],
        "Vocabulary": [],
        "Word Type": [],
        "Reading Whitelist": [],
        "Reading Elements": [],
        "Reading Mnemonic": [],
        "Type": [],
        "DO NOT CHANGE": [],
        "Tags": []
    }

    for i in range(len(vocabulary_data["Level"])):
        output_data["Level"].append(vocabulary_data["Level"][i])
        output_data["Vocabulary"].append(vocabulary_data["Symbol"][i])
        output_data["Word Type"].append(vocabulary_data["Word Type"][i].replace(",", ", "))

        # region Reading
        output_data["Reading Whitelist"].append(vocabulary_data["Reading Whitelist"][i])
        readings_list = vocabulary_data["Reading"][i].split(",")
        male_audio_list = vocabulary_data["Reading Audio Male"][i].split(",")
        female_audio_list = vocabulary_data["Reading Audio Female"][i].split(",")

        reading_items = []
        for r_id in range(len(readings_list)):
            audio_elements = ""

            m_audio = male_audio_list[r_id]
            if m_audio != "None":
                audio_elements += f'<reading-audio class="audio-male">{ m_audio }</reading-audio>'

            f_audio = female_audio_list[r_id]
            if f_audio != "None":
                audio_elements += f'<reading-audio class="audio-female">{ f_audio }</reading-audio>'

            item_div = f'<div class="reading-item">{ readings_list[r_id] }{ audio_elements }</div>'
            reading_items.append(item_div)

        reading_grid = f'<div class="reading-grid">{ "".join(reading_items) }</div>'
        output_data["Reading Elements"].append(reading_grid)

        output_data["Reading Mnemonic"].append(vocabulary_data["Reading Mnemonic"][i])
        # endregion

        output_data["Type"].append("Vocabulary Reading")
        output_data["DO NOT CHANGE"].append("-")

        output_data["Tags"].append(f'Vocabulary_Reading Level_{ vocabulary_data["Level"][i] }')

    pd.DataFrame(data=output_data).to_csv("-Output/Anki_Vocabulary_Reading_Notes.csv", index=False, header=False, sep="\t")
