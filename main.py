import tts
import definition

# Verbs
verb_words_file = "Data/Input/Words/Verbs.txt"
verb_meaning_file = "Data/Input/Meaning/Verbs.txt"
verb_sound_base_name = "VerbSND"

tts.convert_file(verb_words_file, verb_sound_base_name, "Data/Output/Audio/Verbs")

"""
definition.convert_file_into_anki_import(
    verb_words_file,
    verb_meaning_file,
    verb_sound_base_name,
    "Data/Output/Anki/VerbsImport.txt",
    "verb"
)
"""
