import tkinter as tk
from tkinter import filedialog

from VADAudioController import VADAudioController
from player import Player

class GUI:
    def __init__(self, root):

        #main window
        self.root = root
        self.root.title("YUP speedster")
        self.root.geometry("500x400")

        # const
        self._current_speed = 1.0

        #player integration
        self.player = Player()

        # ui label
        tk.Label(root, text="File Path").pack()

        self.txt_path = tk.Entry(root, width=200, state="readonly")
        self.txt_path.pack()

        tk.Button(root, text="Select file", command=self._open_file).pack()

        # speed scaler
        self.speed_scale = tk.Scale(
            orient="horizontal",
            from_=0.5,
            to=3.00,
            resolution=0.25,
            tickinterval=0.5,
            digits=3,
            length=100,
            label="Speed",
            command=self._update_speed_rate,
        )
        self.speed_scale.set(self._current_speed)
        self.speed_scale.pack(fill="x", pady=5)

        # vad sensitivity scaler
        self.vad_scale = tk.Scale(
            orient="horizontal",
            from_=0.1,
            to=0.9,
            resolution=0.1,
            tickinterval=0.2,
            digits=2,
            length=100,
            label="VAD sensitivity"
        )
        self.vad_scale.set(0.5)
        self.vad_scale.pack(fill="x", pady=5)

        self.progress_label = tk.Label(root, text="--:-- / --:--")
        self.progress_label.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()
        tk.Button(btn_frame, text="play", command=self.player.play, width=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="pause", command=self.player.pause, width=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="stop", command=self.player.stop, width=8).pack(side="left", padx=5)

        self.vad_controller = None
        self._is_auto_skip_enabled = tk.BooleanVar(value=True)
        self._is_seeking = False

        tk.Checkbutton(self.root, text="Silence auto skip", variable=self._is_auto_skip_enabled).pack(anchor="w", padx=20, pady=5)

        self._update_progress()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _open_file(self):
        self.txt_path.config(state="normal")

        audio_filepath = filedialog.askopenfilename(title="Select file", filetypes=[("Audio", "*.mp3 *.wav *.m4a *.ogg *.flac")])
        if audio_filepath:
            self.txt_path.delete(0, tk.END)
            self.txt_path.insert(0, audio_filepath)

        self.txt_path.config(state="readonly")
        self.vad_controller = VADAudioController(audio_path=audio_filepath, VAD_sensetivity=self.vad_scale.get())
        self.vad_controller.start()
        self.player.load(audio_filepath)

    def _format_time(self, ms: int) -> str:
        if ms <= 0: return "--:--"
        m, s = divmod(ms // 1000, 60)
        return f"{m:02d}:{s:02d}"

    def _update_progress(self):
        dur = self.player.get_duration()
        pos = self.player.get_pos()
        current_ms = self.player.get_time()
        current_s = current_ms / 1000

        if (self._is_auto_skip_enabled.get() and self.vad_controller and not self._is_seeking and dur > 0 and self.vad_controller.seconds_processed > current_s):
            if self.vad_controller.in_silence_chunk(current_s):
                next_s = self.vad_controller.find_next_speech(current_s) - 0.75

                if next_s > current_s:
                    self._is_seeking = True
                    self.player.set_time(int(next_s * 1000))
                    print(f"SKIP")
                    self.root.after(400, lambda: setattr(self, '_is_seeking', False))

        self.progress_label.config(text=f"{self._format_time(int(pos * dur))} / {self._format_time(dur)}")

        self.root.after(50, self._update_progress)

    def _update_speed_rate(self, value):
        new_speed = float(value)

        if abs(new_speed - self._current_speed) > 0.1:
            self.player.set_speed_rate(new_speed)
            self._current_speed = new_speed

    def _on_close(self):
        self.player.stop()
        self.root.destroy()
        print("DESTROYED")

    