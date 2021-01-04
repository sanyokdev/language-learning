import os
from google.cloud import texttospeech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Credentials/mykey.json"


def convert_word(word_id, sound_base_name, input_text, output_path):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(
        {
            "text": str(input_text)
        }
    )

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        {
            "language_code": "pt-PT",
            "name": "pt-PT-Wavenet-C"
        }
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        {
            "audio_encoding": texttospeech.AudioEncoding.MP3
        }
    )

    # Perform the text-to-speech request on the text input with the selected voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open(str(output_path) + "/" + str(sound_base_name) + "_" + str(word_id) + ".mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        # print("Audio content written to file" + str(word_id) + ".mp3")


def convert_file(input_file, sound_base_name, output_folder):
    words = []

    with open(str(input_file), 'r', encoding='utf8') as out:
        words = out.read().splitlines()

    amount_of_words = len(words)

    for i in range(amount_of_words):
        percentage = round(100.0 * i / float(amount_of_words), 1)
        print("Progress: " + str(percentage) + "%")
        convert_word(i, sound_base_name, words[i], str(output_folder))
