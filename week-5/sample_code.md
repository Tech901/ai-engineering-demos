# Sample code from Ch6 of Azure AI Engineer Study Guide

## 1. Basic NLP Pipeline for Sentiment Analysis

```
from transformers import pipeline
classifier = pipeline("sentiment-analysis")
result = classifier("I love working with Azure AI services!")
print(result)
```

## 2. Azure AI Speech (Text-to-Speech and Speech-to-Text)

```
import os
from azure.cognitiveservices.speech import (
    SpeechConfig,
    SpeechSynthesizer,
    SpeechRecognizer,
    AudioConfig,
    ResultReason,
    CancellationReason
)

speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_REGION")

def text_to_speech(text):
    speech_config = SpeechConfig(
      subscription=speech_key,
      region=service_region
    )
    audio_config = AudioConfig(filename="output.wav")
    synthesizer = SpeechSynthesizer(
      speech_config=speech_config,
      audio_config=audio_config
    )
    result = synthesizer.speak_text_async(text).get()

def speech_to_text():
    speech_config = SpeechConfig(
        subscription=speech_key,
        region=service_region
    )
    speech_recognizer = SpeechRecognizer(speech_config=speech_config)
    print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()

    if result.reason == ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif result.reason == ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

if __name__ == "__main__":
    choice = input("Enter 1 for Text-to-Speech, 2 for Speech-to-Text: ")
    if choice == '1':
        text = input("Enter the text you want to convert to speech: ")
        text_to_speech(text)
    elif choice == '2':
        speech_to_text()
    else:
        print("Invalid choice. Please enter 1 or 2.")
```


## 3. Azure AI Translator (Text Translation)

```
import requests, uuid

subscription_key = "YOUR_SUBSCRIPTION_KEY"
endpoint = "YOUR_ENDPOINT"

path = '/translate?api-version=3.0'
params = '&from=en&to=es&to=fr'
constructed_url = endpoint + path + params

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

body = [{
    'text': 'Hello, how are you?'
}]

response = requests.post(constructed_url, headers=headers, json=body)
result = response.json()

for translation in result['translations']:
    print(f"Translated into {translation['to']}: {translation['text']}")
```


## 4. Azure AI Translator (Speech-to-Speech Translation)

```
import azure.cognitiveservices.speech as speechsdk
import simpleaudio as sa

subscription_key = "YOUR_SUBSCRIPTION_KEY"
service_region = "YOUR_REGION"

translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=subscription_key, region=service_region)

translation_config.speech_recognition_language = 'en-US'
translation_config.add_target_language('es')
translation_config.add_target_language('fr')

translation_config.speech_synthesis_voice_name = 'es-ES-AlvaroNeural'
translation_config.speech_synthesis_voice_name = 'fr-FR-DeniseNeural'

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

translator = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config, audio_config=audio_config)

_last_play = None

def recognizing_handler(evt):
    print(f"Recognizing: {evt.result.text}")

def recognized_handler(evt):
    print(f"Recognized: {evt.result.text}")
    for lang in evt.result.translations:
        translation = evt.result.translations[lang]
        print(f"Translated into {lang}: {translation}")

def canceled_handler(evt):
    print(f"Canceled: {evt.reason}")

def synthesizing_handler(evt):
    if evt.result.reason == speechsdk.ResultReason.TranslatingSpeech:
        print(f"Synthesizing translation audio for {evt.result.translations}")
        audio_data = evt.result.audio
        if audio_data:
            global _last_play
            if _last_play and _last_play.is_playing():
                _last_play.stop()
            _last_play = sa.play_buffer(audio_data, 1, 2, 16000)

translator.recognizing.connect(recognizing_handler)
translator.recognized.connect(recognized_handler)
translator.canceled.connect(canceled_handler)
translator.synthesizing.connect(synthesizing_handler)

print("Speak into your microphone.")
translator.start_continuous_recognition()

try:
    while True:
        pass
except KeyboardInterrupt:
    translator.stop_continuous_recognition()
    print("Translation stopped.")
```


## 5. Custom Translation Solution

```
import requests, uuid, json

# Replace with your Translator resource key and endpoint
subscription_key = 'your_subscription_key'
endpoint = 'your_endpoint' + '/translate?api-version=3.0'
# Replace with your custom model's category ID
params = '&from=en&to=de&category=your_custom_model_category_id'
constructed_url = endpoint + params

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Ocp-Apim-Subscription-Region': 'your_region',
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

body = [{
    'text': 'Your text here for translation'
}]

response = requests.post(constructed_url, headers=headers, json=body).json()

print(json.dumps(response, indent=4, ensure_ascii=False))
```
