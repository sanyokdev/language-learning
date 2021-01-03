import tts
import definition


def create_audio_files(word_type):
    words_file = "Data/Input/Words/" + str(word_type) + ".txt"
    meaning_file = "Data/Input/Meaning/" + str(word_type) + ".txt"
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
