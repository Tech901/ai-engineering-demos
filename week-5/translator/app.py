"""
Azure Speech-to-Speech Translation GUI (Gradio)
Requires env vars: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
"""

import html as html_lib
import os
import threading
import queue
import struct

import gradio as gr
import numpy as np
import sounddevice as sd
import azure.cognitiveservices.speech as speechsdk

# ---------------------------------------------------------------------------
# Language / voice tables
# ---------------------------------------------------------------------------
# Keys = display name, values = (recognition BCP-47, translation code, neural voice name)
LANGUAGES = {
    "English (US)":       ("en-US", "en",  "en-US-JennyNeural"),
    "Spanish (Spain)":    ("es-ES", "es",  "es-ES-ElviraNeural"),
    "French":             ("fr-FR", "fr",  "fr-FR-DeniseNeural"),
    "German":             ("de-DE", "de",  "de-DE-KatjaNeural"),
    "Italian":            ("it-IT", "it",  "it-IT-ElsaNeural"),
    "Portuguese (BR)":    ("pt-BR", "pt",  "pt-BR-FranciscaNeural"),
    "Chinese (Mandarin)": ("zh-CN", "zh-Hans", "zh-CN-XiaoxiaoNeural"),
    "Japanese":           ("ja-JP", "ja",  "ja-JP-NanamiNeural"),
    "Korean":             ("ko-KR", "ko",  "ko-KR-SunHiNeural"),
    "Arabic (Saudi)":     ("ar-SA", "ar",  "ar-SA-ZariyahNeural"),
    "Russian":            ("ru-RU", "ru",  "ru-RU-SvetlanaNeural"),
    "Hindi":              ("hi-IN", "hi",  "hi-IN-SwaraNeural"),
}

LANG_NAMES = list(LANGUAGES.keys())

TRANSCRIPT_CSS = """\
.transcript-pane {
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 16px;
    border-radius: 8px;
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 15px;
    line-height: 1.6;
}
.transcript-pane .src { color: #5dade2; margin: 2px 0; }
.transcript-pane .tgt { color: #58d68d; margin: 2px 0 12px 0; }
.transcript-pane .sts { color: #aab7b8; margin: 4px 0; }
.transcript-pane .empty { color: #555; }
"""


class TranslatorApp:
    def __init__(self):
        self.recognizer: speechsdk.translation.TranslationRecognizer | None = None
        self.is_running = False
        self.tgt_lang_code = ""
        self.event_queue: queue.Queue = queue.Queue()
        self.transcript_entries: list[tuple[str, str]] = []

    # ------------------------------------------------------------------
    # Start / stop translation
    # ------------------------------------------------------------------
    def start(self, input_lang: str, output_lang: str):
        if self.is_running:
            return

        key = os.environ.get("AZURE_SPEECH_KEY", "")
        region = os.environ.get("AZURE_SPEECH_REGION", "")
        if not key or not region:
            self.event_queue.put(
                ("status", "ERROR: Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION env vars.")
            )
            return

        src = LANGUAGES[input_lang]
        tgt = LANGUAGES[output_lang]
        self.tgt_lang_code = tgt[1]

        cfg = speechsdk.translation.SpeechTranslationConfig(
            subscription=key, region=region,
        )
        cfg.speech_recognition_language = src[0]
        cfg.add_target_language(tgt[1])
        cfg.voice_name = tgt[2]

        audio_cfg = speechsdk.audio.AudioConfig(use_default_microphone=True)

        self.recognizer = speechsdk.translation.TranslationRecognizer(
            translation_config=cfg, audio_config=audio_cfg,
        )

        # Wire events
        self.recognizer.recognizing.connect(self._on_recognizing)
        self.recognizer.recognized.connect(self._on_recognized)
        self.recognizer.synthesizing.connect(self._on_synthesizing)
        self.recognizer.canceled.connect(self._on_canceled)
        self.recognizer.session_started.connect(
            lambda e: self.event_queue.put(("status", "Session started"))
        )
        self.recognizer.session_stopped.connect(
            lambda e: self.event_queue.put(("status", "Session stopped"))
        )

        self.recognizer.start_continuous_recognition_async()
        self.is_running = True

    def stop(self):
        if self.recognizer:
            self.recognizer.stop_continuous_recognition_async()
            self.recognizer = None
        self.is_running = False

    # ------------------------------------------------------------------
    # SDK event handlers (called from SDK threads)
    # ------------------------------------------------------------------
    def _on_recognizing(self, evt):
        translation = evt.result.translations.get(self.tgt_lang_code, "")
        self.event_queue.put(("recognizing", evt.result.text, translation))

    def _on_recognized(self, evt):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            translation = evt.result.translations.get(self.tgt_lang_code, "")
            self.event_queue.put(("recognized", evt.result.text, translation))
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            self.event_queue.put(("recognizing", "(no match)", ""))

    def _on_synthesizing(self, evt):
        if evt.result.reason == speechsdk.ResultReason.SynthesizingAudio:
            audio = evt.result.audio
            if audio and len(audio) > 0:
                self._play_audio(audio)

    def _on_canceled(self, evt):
        self.event_queue.put(("status", f"Canceled: {evt.reason} — {evt.error_details}"))

    # ------------------------------------------------------------------
    # Audio playback (16 kHz, 16-bit mono PCM)
    # ------------------------------------------------------------------
    def _play_audio(self, raw: bytes):
        def _worker():
            try:
                n_samples = len(raw) // 2
                samples = struct.unpack(f"<{n_samples}h", raw[: n_samples * 2])
                arr = np.array(samples, dtype=np.float32) / 32768.0
                sd.play(arr, samplerate=16000, blocksize=1024)
                sd.wait()
            except Exception as exc:
                self.event_queue.put(("status", f"Audio error: {exc}"))

        threading.Thread(target=_worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Queue polling & rendering
    # ------------------------------------------------------------------
    def poll(self) -> tuple[bool, str | None]:
        """Drain the event queue. Returns (transcript_changed, new_status)."""
        changed = False
        status = None

        try:
            while True:
                msg = self.event_queue.get_nowait()
                kind = msg[0]

                if kind == "recognizing":
                    status = f"Hearing: {msg[1][:60]}..."

                elif kind == "recognized":
                    self.transcript_entries.append(("source", msg[1]))
                    self.transcript_entries.append(("target", msg[2]))
                    changed = True

                elif kind == "status":
                    self.transcript_entries.append(("status", msg[1]))
                    status = msg[1]
                    changed = True
        except queue.Empty:
            pass

        return changed, status

    def render_transcript(self) -> str:
        """Build HTML for the transcript pane."""
        if not self.transcript_entries:
            return '<div class="transcript-pane"><span class="empty">Transcript will appear here...</span></div>'

        lines: list[str] = []
        for tag, text in self.transcript_entries:
            escaped = html_lib.escape(text)
            if tag == "source":
                lines.append(f'<div class="src">[SRC] {escaped}</div>')
            elif tag == "target":
                lines.append(f'<div class="tgt">[TGT] {escaped}</div>')
            elif tag == "status":
                lines.append(f'<div class="sts">&mdash; {escaped}</div>')

        return f'<div class="transcript-pane">{"".join(lines)}</div>'

    def clear(self):
        self.transcript_entries.clear()


# ----------------------------------------------------------------------
# Gradio UI
# ----------------------------------------------------------------------
def main():
    app = TranslatorApp()

    with gr.Blocks(
        title="Azure Speech-to-Speech Translator",
        theme=gr.themes.Soft(primary_hue="blue"),
        css=TRANSCRIPT_CSS,
    ) as demo:
        gr.Markdown("# Azure Speech-to-Speech Translator")

        with gr.Row():
            input_lang = gr.Dropdown(
                choices=LANG_NAMES, value="English (US)",
                label="Input Language", scale=2,
            )
            output_lang = gr.Dropdown(
                choices=LANG_NAMES, value="Spanish (Spain)",
                label="Output Language", scale=2,
            )
            start_btn = gr.Button("Start", variant="primary", scale=1)
            clear_btn = gr.Button("Clear", variant="secondary", scale=1)

        transcript = gr.HTML(value=app.render_transcript())
        status = gr.Textbox(value="Ready", label="Status", interactive=False)

        # -- Start / Stop toggle -------------------------------------------
        is_running = gr.State(False)

        def toggle(input_l, output_l, running):
            if running:
                app.stop()
                return gr.update(value="Start", variant="primary"), False, "Stopped"
            else:
                app.start(input_l, output_l)
                return gr.update(value="Stop", variant="stop"), True, "Listening..."

        start_btn.click(
            fn=toggle,
            inputs=[input_lang, output_lang, is_running],
            outputs=[start_btn, is_running, status],
        )

        # -- Clear ---------------------------------------------------------
        def clear_transcript():
            app.clear()
            return app.render_transcript()

        clear_btn.click(fn=clear_transcript, outputs=[transcript])

        # -- Poll for SDK events every 100 ms ------------------------------
        timer = gr.Timer(value=0.1)

        def poll_updates():
            changed, new_status = app.poll()
            html = app.render_transcript() if changed else gr.update()
            st = new_status if new_status else gr.update()
            return html, st

        timer.tick(fn=poll_updates, outputs=[transcript, status])

    demo.launch()


if __name__ == "__main__":
    main()
