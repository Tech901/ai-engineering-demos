"""
Azure Speech-to-Speech Translation GUI
Requires env vars: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
"""

import os
import sys
import json
import threading
import queue
import struct
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext

import sounddevice as sd
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger, LogLevel

# ---------------------------------------------------------------------------
# Language / voice tables
# ---------------------------------------------------------------------------
# Keys = display name, values = (recognition BCP-47, translation code, neural voice name)
LANGUAGES = {
    "English (US)":    ("en-US", "en",  "en-US-JennyNeural"),
    "Spanish (Spain)": ("es-ES", "es",  "es-ES-ElviraNeural"),
    "French":          ("fr-FR", "fr",  "fr-FR-DeniseNeural"),
    "German":          ("de-DE", "de",  "de-DE-KatjaNeural"),
    "Italian":         ("it-IT", "it",  "it-IT-ElsaNeural"),
    "Portuguese (BR)": ("pt-BR", "pt",  "pt-BR-FranciscaNeural"),
    "Chinese (Mandarin)": ("zh-CN", "zh-Hans", "zh-CN-XiaoxiaoNeural"),
    "Japanese":        ("ja-JP", "ja",  "ja-JP-NanamiNeural"),
    "Korean":          ("ko-KR", "ko",  "ko-KR-SunHiNeural"),
    "Arabic (Saudi)":  ("ar-SA", "ar",  "ar-SA-ZariyahNeural"),
    "Russian":         ("ru-RU", "ru",  "ru-RU-SvetlanaNeural"),
    "Hindi":           ("hi-IN", "hi",  "hi-IN-SwaraNeural"),
}

LANG_NAMES = list(LANGUAGES.keys())


class TranslatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Azure Speech-to-Speech Translator")
        self.root.geometry("1100x700")
        self.root.minsize(900, 500)

        self.recognizer: speechsdk.translation.TranslationRecognizer | None = None
        self.is_running = False

        # Queue for thread-safe GUI updates
        self.gui_queue: queue.Queue = queue.Queue()

        # Audio playback buffer
        self.audio_bytes = bytearray()

        self._build_ui()
        self._poll_queue()

        # Install SDK event logger to capture HTTP traffic
        self._install_sdk_logger()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Top control bar
        ctrl = ttk.Frame(self.root, padding=8)
        ctrl.pack(fill=tk.X)

        ttk.Label(ctrl, text="Input language:").pack(side=tk.LEFT)
        self.input_lang = ttk.Combobox(ctrl, values=LANG_NAMES, state="readonly", width=20)
        self.input_lang.set("English (US)")
        self.input_lang.pack(side=tk.LEFT, padx=(4, 16))

        ttk.Label(ctrl, text="Output language:").pack(side=tk.LEFT)
        self.output_lang = ttk.Combobox(ctrl, values=LANG_NAMES, state="readonly", width=20)
        self.output_lang.set("Spanish (Spain)")
        self.output_lang.pack(side=tk.LEFT, padx=(4, 16))

        self.start_btn = ttk.Button(ctrl, text="Start", command=self._toggle)
        self.start_btn.pack(side=tk.LEFT, padx=4)

        self.clear_btn = ttk.Button(ctrl, text="Clear", command=self._clear_logs)
        self.clear_btn.pack(side=tk.LEFT, padx=4)

        # Main area: left = transcript, right = HTTP log
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        left = ttk.LabelFrame(paned, text="Translation Transcript", padding=4)
        paned.add(left, weight=1)
        self.transcript = scrolledtext.ScrolledText(left, wrap=tk.WORD, font=("Consolas", 11))
        self.transcript.pack(fill=tk.BOTH, expand=True)
        self.transcript.tag_configure("source", foreground="#1a73e8")
        self.transcript.tag_configure("target", foreground="#0d652d")
        self.transcript.tag_configure("status", foreground="#888888")

        right = ttk.LabelFrame(paned, text="SDK / HTTP Log", padding=4)
        paned.add(right, weight=1)
        self.http_log = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=("Consolas", 9))
        self.http_log.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                  anchor=tk.W, padding=4).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # SDK event logger → HTTP panel
    # ------------------------------------------------------------------
    def _install_sdk_logger(self):
        def _on_log(msg: str):
            self.gui_queue.put(("http", msg))

        EventLogger.set_callback(_on_log)
        EventLogger.set_level(LogLevel.Verbose)

    # ------------------------------------------------------------------
    # Start / stop translation
    # ------------------------------------------------------------------
    def _toggle(self):
        if self.is_running:
            self._stop()
        else:
            self._start()

    def _start(self):
        key = os.environ.get("AZURE_SPEECH_KEY", "")
        region = os.environ.get("AZURE_SPEECH_REGION", "")
        if not key or not region:
            self._append_transcript("[ERROR] Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION env vars.\n", "status")
            return

        src = LANGUAGES[self.input_lang.get()]
        tgt = LANGUAGES[self.output_lang.get()]

        # Build config
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
            lambda e: self.gui_queue.put(("status", "Session started"))
        )
        self.recognizer.session_stopped.connect(
            lambda e: self.gui_queue.put(("status", "Session stopped"))
        )

        self.recognizer.start_continuous_recognition_async()
        self.is_running = True
        self.start_btn.config(text="Stop")
        self.status_var.set("Listening…")
        self.input_lang.config(state="disabled")
        self.output_lang.config(state="disabled")

        self._log_http_entry("START_SESSION", {
            "source_language": src[0],
            "target_language": tgt[1],
            "voice": tgt[2],
            "region": region,
        })

    def _stop(self):
        if self.recognizer:
            self.recognizer.stop_continuous_recognition_async()
            self.recognizer = None
        self.is_running = False
        self.start_btn.config(text="Start")
        self.status_var.set("Stopped")
        self.input_lang.config(state="readonly")
        self.output_lang.config(state="readonly")

    # ------------------------------------------------------------------
    # SDK event handlers (called from SDK threads)
    # ------------------------------------------------------------------
    def _on_recognizing(self, evt):
        tgt_lang = LANGUAGES[self.output_lang.get()][1]
        translation = evt.result.translations.get(tgt_lang, "")
        self.gui_queue.put(("recognizing", evt.result.text, translation))
        self._log_http_entry("RECOGNIZING", {
            "text": evt.result.text,
            "translations": dict(evt.result.translations),
            "result_id": evt.result.result_id,
        })

    def _on_recognized(self, evt):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            tgt_lang = LANGUAGES[self.output_lang.get()][1]
            translation = evt.result.translations.get(tgt_lang, "")
            self.gui_queue.put(("recognized", evt.result.text, translation))
            self._log_http_entry("RECOGNIZED", {
                "reason": "TranslatedSpeech",
                "text": evt.result.text,
                "translations": dict(evt.result.translations),
                "result_id": evt.result.result_id,
                "duration_ticks": evt.result.duration,
                "offset_ticks": evt.result.offset,
            })
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            self.gui_queue.put(("status_inline", "(no match)"))
            self._log_http_entry("NO_MATCH", {
                "reason": "NoMatch",
                "result_id": evt.result.result_id,
            })

    def _on_synthesizing(self, evt):
        if evt.result.reason == speechsdk.ResultReason.SynthesizingAudio:
            audio = evt.result.audio
            if audio and len(audio) > 0:
                self.gui_queue.put(("play_audio", audio))
                self._log_http_entry("SYNTHESIS_AUDIO", {
                    "audio_bytes": len(audio),
                })
        elif evt.result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            self._log_http_entry("SYNTHESIS_COMPLETE", {})

    def _on_canceled(self, evt):
        self.gui_queue.put(("status", f"Canceled: {evt.reason} — {evt.error_details}"))
        self._log_http_entry("CANCELED", {
            "reason": str(evt.reason),
            "error_code": str(evt.error_code),
            "error_details": evt.error_details,
        })

    # ------------------------------------------------------------------
    # Audio playback (16 kHz, 16-bit mono PCM)
    # ------------------------------------------------------------------
    def _play_audio(self, raw: bytes):
        def _worker():
            try:
                # Convert raw PCM bytes to float32 samples for sounddevice
                n_samples = len(raw) // 2
                samples = struct.unpack(f"<{n_samples}h", raw[:n_samples * 2])
                import numpy as np
                arr = np.array(samples, dtype=np.float32) / 32768.0
                sd.play(arr, samplerate=16000, blocksize=1024)
                sd.wait()
            except Exception as exc:
                self.gui_queue.put(("status", f"Audio error: {exc}"))

        threading.Thread(target=_worker, daemon=True).start()

    # ------------------------------------------------------------------
    # GUI queue consumer (runs on main thread)
    # ------------------------------------------------------------------
    def _poll_queue(self):
        try:
            while True:
                msg = self.gui_queue.get_nowait()
                kind = msg[0]

                if kind == "recognizing":
                    self.status_var.set(f"Hearing: {msg[1][:60]}…")

                elif kind == "recognized":
                    src_text, tgt_text = msg[1], msg[2]
                    self._append_transcript(f"[SRC] {src_text}\n", "source")
                    self._append_transcript(f"[TGT] {tgt_text}\n\n", "target")

                elif kind == "status":
                    self._append_transcript(f"— {msg[1]}\n", "status")
                    self.status_var.set(msg[1])

                elif kind == "status_inline":
                    self.status_var.set(msg[1])

                elif kind == "play_audio":
                    self._play_audio(msg[1])

                elif kind == "http":
                    self.http_log.insert(tk.END, msg[1] + "\n")
                    self.http_log.see(tk.END)

        except queue.Empty:
            pass

        self.root.after(50, self._poll_queue)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _append_transcript(self, text: str, tag: str):
        self.transcript.insert(tk.END, text, tag)
        self.transcript.see(tk.END)

    def _log_http_entry(self, event_type: str, payload: dict):
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = {"timestamp": ts, "event": event_type, **payload}
        formatted = json.dumps(entry, indent=2, ensure_ascii=False)
        self.gui_queue.put(("http", f"── {event_type} ──\n{formatted}\n"))

    def _clear_logs(self):
        self.transcript.delete("1.0", tk.END)
        self.http_log.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
