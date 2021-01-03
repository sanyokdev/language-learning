import tts
import definition

# Verbs
verb_file = "Input/Words/Verbs.txt"
tts.convert_file(verb_file, "Output/Audio/Verbs")
definition.convert_file_into_anki_import(verb_file, "Output/Anki/VerbsImport.txt", "verb")
