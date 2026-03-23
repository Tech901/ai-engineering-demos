# AI speech-to-speech translation

## Azure AI Language

See the [Tech901/ai-fundamentals-demo](https://github.com/Tech901/ai-fundamentals-demos/tree/main/05-NLP) repo for examples
of Sentiment Analysis, Named Entity Recognition, Key Phrase Extraction, and PII Redaction.

## Azure AI Speech

The `translator/` directory contains a **real-time speech-to-speech translation** desktop app built with Python and Azure Cognitive Services. Key highlights:

- **GUI** — A tkinter/ttkbootstrap dark-themed window with dropdowns for selecting input and output languages, a translation transcript panel, and a live SDK/HTTP log panel.
- **12 languages** — Supports English, Spanish, French, German, Italian, Portuguese, Chinese (Mandarin), Japanese, Korean, Arabic, Russian, and Hindi, each mapped to an Azure Neural voice for natural-sounding output.
- **Continuous recognition** — Uses Azure's `TranslationRecognizer` with continuous microphone input. Interim (recognizing) and final (recognized) results are displayed in real time.
- **Speech synthesis** — Translated text is automatically spoken back through your speakers using Azure Neural TTS (16 kHz, 16-bit mono PCM playback via `sounddevice`).
- **Thread-safe architecture** — SDK callbacks push events onto a queue that the main GUI thread polls, keeping the UI responsive.
- **Observability** — All SDK events and HTTP traffic are logged with timestamps in a side panel for debugging and demonstration purposes.

## Dependencies

In WSL, there are a number of os packages required

```
sudo apt install libportaudio2
sudo apt-get install -y libpulse0 libasound2-plugins
```
