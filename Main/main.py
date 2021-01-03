import os
from google.cloud import texttospeech
import requests
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./Credentials/mykey.json"


def convert_to_speech(word_id, input_text, output_path):
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

    # voice = texttospeech.VoiceSelectionParams(
    #     {
    #         "language_code": "en-US",
    #         "name": "en-US-Wavenet-D"
    #     }
    # )

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
    with open("./Data/Output/" + str(output_path) + "/" + str(output_path) + "PT_" + str(word_id) + ".mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        # print("Audio content written to file" + str(word_id) + ".mp3")


def get_word_definition(input_word, word_tense):
    payload = {
        "language": "en",
        "text": str(input_word),
        "pos": str(word_tense)
    }

    url = ""
    with open("./Credentials/dictapiUrl.txt", 'r') as out:
        url = str(out.readline())

    r = requests.get(url, params=payload)

    results = json.loads(r.content)["results"]
    senses = results[0]["senses"]

    output_list = []

    for val in senses:
        definition = str(val.get("definition"))

        if definition != "None":
            output_list.append(val.get("definition"))

    return output_list


def main():
    words = []

    with open("./Data/Input/nounsPT.txt", 'r', encoding='utf8') as out:
        words = out.read().splitlines()

    amount_of_words = len(words)
    print(words)

    for i in range(amount_of_words):
        percentage = round(100.0 * i / float(amount_of_words), 1)
        print("Progress: " + str(percentage) + "%")
        convert_to_speech(i, words[i], "Noun")

    # print(get_word_definition("beautiful", "noun"))

    # print("Word ID?")
    # word_id = str(input())

    # print("Input text?")
    # input_text = str(input())

    # print("Output path?")
    # output_path = str(input())

    # convert_to_speech(word_id, input_text, output_path)
    # print("Converted")


if __name__ == "__main__":
    main()
