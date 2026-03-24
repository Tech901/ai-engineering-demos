# AI speech-to-speech translation

## Azure AI Language

See the [Tech901/ai-fundamentals-demo](https://github.com/Tech901/ai-fundamentals-demos/tree/main/05-NLP) repo for examples
of Sentiment Analysis, Named Entity Recognition, Key Phrase Extraction, and PII Redaction.

## Azure AI Speech

The `translator/` directory contains a **real-time speech-to-speech translation** app built with Python, Gradio, and Azure Cognitive Services. Key highlights:

- **GUI** — A Gradio web interface with dropdowns for selecting input and output languages, a translation transcript panel with color-coded source/target text, and a status bar.
- **12 languages** — Supports English, Spanish, French, German, Italian, Portuguese, Chinese (Mandarin), Japanese, Korean, Arabic, Russian, and Hindi, each mapped to an Azure Neural voice for natural-sounding output.
- **Full Unicode support** — The browser-based UI natively renders all scripts (CJK, Cyrillic, Arabic, Devanagari, etc.) without additional font configuration.
- **Continuous recognition** — Uses Azure's `TranslationRecognizer` with continuous microphone input. Interim (recognizing) and final (recognized) results are displayed in real time.
- **Speech synthesis** — Translated text is automatically spoken back through your speakers using Azure Neural TTS (16 kHz, 16-bit mono PCM playback via `sounddevice`).
- **Thread-safe architecture** — SDK callbacks push events onto a queue that a Gradio timer polls, keeping the UI responsive.

## Running the app

```bash
# Set your Azure credentials
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="your-region"

# Install dependencies and run
uv sync
uv run python translator/app.py
```

The app will open in your browser at `http://localhost:7860`.

## Dependencies

In WSL, there are a number of OS packages required:

```
sudo apt install libportaudio2
sudo apt-get install -y libpulse0 libasound2-plugins
```
