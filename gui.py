import tkinter as tk
from tkinter import filedialog
from player import Player

class GUI:
    def __init__(self, root):

        #main window
        self.root = root
        self.root.title("YUP speedster")
        self.root.geometry("500x400")

        #player integration
        self.player = Player()

        # ui label
        tk.Label(root, text="File Path").pack()

        self.txt_path = tk.Entry(root, width=200, state="readonly")
        self.txt_path.pack()

        tk.Button(root, text="Select file", command=self._open_file).pack()

        # speed scaler
        speed_scale = tk.Scale(
            orient="horizontal",
            from_=1.00,
            to=3.00,
            resolution=0.25,
            tickinterval=1,
            digits=3,
            length=100,
            label="Speed"
        )
        speed_scale.pack(fill="x", pady=5)

        # vad sensitivity scaler
        vad_scale = tk.Scale(
            orient="horizontal",
            from_=1.00,
            to=3.00,
            resolution=0.25,
            tickinterval=1,
            digits=3,
            length=100,
            label="VAD sensitivity"
        )
        vad_scale.pack(fill="x", pady=5)

        self.progress_label = tk.Label(root, text="--:-- / --:--")
        self.progress_label.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()
        tk.Button(btn_frame, text="play", command=self.player.play, width=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="pause", command=self.player.pause, width=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="stop", command=self.player.stop, width=8).pack(side="left", padx=5)

        self._update_progress()

    def _open_file(self):
        self.txt_path.config(state="normal")

        audio_filepath = filedialog.askopenfilename(title="Select file")
        if audio_filepath:
            self.txt_path.delete(0, tk.END)
            self.txt_path.insert(0, audio_filepath)

        self.txt_path.config(state="readonly")
        self.player.load(audio_filepath)

    def _format_time(self, ms: int) -> str:
        if ms <= 0: return "--:--"
        m, s = divmod(ms // 1000, 60)
        return f"{m:02d}:{s:02d}"

    def _update_progress(self):
        dur = self.player.get_duration()
        pos = self.player.get_pos()
        self.progress_label.config(text=f"{self._format_time(int(pos * dur))} / {self._format_time(dur)}")
        self.root.after(500, self._update_progress)
