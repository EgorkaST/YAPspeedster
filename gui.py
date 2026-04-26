import tkinter as tk
from tkinter import filedialog

from VADAudioController import VADAudioController
from player import Player

class GUI:
    def __init__(self, root):

        #main window
        self.root = root
        self.root.title("YUP speedster")
        self.root.geometry("500x450")

        # const
        self._current_speed = 1.0
        self._is_auto_skip_enabled = tk.BooleanVar(value=True)
        self._is_user_seeking = False
        self._is_auto_seeking = False

        # integration
        self.player = Player()
        self.vad_controller = None

        # ui label
        tk.Label(root, text="File Path").pack()

        self.txt_path = tk.Entry(root, width=200, state="readonly")
        self.txt_path.pack(padx=20, fill="x")

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
        self.speed_scale.pack(fill="x",padx=20, pady=5)

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
        self.vad_scale.pack(fill="x", padx=20, pady=5)

        self.progress_label = tk.Label(root, text="--:-- / --:--")
        self.progress_label.pack(pady=0)

        self.seek_var = tk.DoubleVar(value=0.0)
        self.seek_scale = tk.Scale(
            root,
            from_=0.0, to=1.0, resolution=0.001,
            orient="horizontal",
            variable=self.seek_var,
            command=self._on_seek,
            state="disabled",
            showvalue=False,
        )
        self.seek_scale.pack(fill="x", padx=20, pady=8)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()
        tk.Button(btn_frame, text="play", command=self.player.play, width=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="pause", command=self.player.pause, width=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="stop", command=self.player.stop, width=8).pack(side="left", padx=5)

        tk.Checkbutton(self.root, text="Silence auto skip", variable=self._is_auto_skip_enabled).pack(anchor="w", padx=20, pady=5)
        tk.Button(self.root, text="download", width= 12).pack(side="left", padx=20)

        self._update_progress()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _open_file(self):
        self.txt_path.config(state="normal")

        audio_filepath = filedialog.askopenfilename(title="Select file", filetypes=[("Audio", "*.mp3 *.wav *.m4a *.ogg *.flac")])
        if audio_filepath:
            self.txt_path.delete(0, tk.END)
            self.txt_path.insert(0, audio_filepath)

        self.seek_var.set(0.0)
        self.seek_scale.config(state="normal")

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

        if dur > 0 and not self._is_user_seeking:
            pos_ratio = current_ms / dur
            self.seek_var.set(pos_ratio)
            self.seek_scale.config(state="normal")

        if (self._is_auto_skip_enabled.get() and
            self.vad_controller and
            not self._is_auto_seeking and
            not self._is_user_seeking and
            dur > 0 and
            self.vad_controller.seconds_processed > current_s):

            if self.vad_controller.in_silence_chunk(current_s):
                next_s = self.vad_controller.find_next_speech(current_s) - 0.8

                if next_s > current_s:
                    self._is_auto_seeking = True
                    self.player.set_time(int(next_s * 1000))
                    print(f"SKIP: {current_s:.1f}s → {next_s:.1f}s")
                    self.root.after(400, lambda: setattr(self, '_is_auto_seeking', False))

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

    def _on_seek(self, value: str):
        self._is_user_seeking = True

        try:
            pos_ratio = float(value)
            dur = self.player.get_duration()
            if dur > 0:
                target_ms = int(pos_ratio * dur)
                self.player.set_time(target_ms)
        except Exception as e:
            print(f"Seek error: {e}")

        self.root.after(300, lambda: setattr(self, '_is_user_seeking', False))

    