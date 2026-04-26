import tkinter as tk
from tkinter import filedialog, messagebox

from VADAudioController import VADAudioController
from player import Player
from pathlib import Path
import threading
from PIL import Image, ImageTk


class GUI:
    def __init__(self, root):

        #main window
        self.root = root
        self.root.title("YUP speedster")
        #ТУТ ИЗМЕНИТЬ ВСЕ ОКНО!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.root.geometry("600x600")

        # const
        self._current_speed = 1.0
        self._is_auto_skip_enabled = tk.BooleanVar(value=True)
        self._is_user_seeking = False
        self._is_auto_seeking = False

        # integration
        self.player = Player()
        self.vad_controller = None

        # ТУТ ИЗМЕНИТЬ КАРТИНКУ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        img = Image.open("C:/Users/Alena/Documents/GitHub/YAPspeedster/meow.jpg")
        photo = ImageTk.PhotoImage(img)

        # ТУТ ИЗМЕНИТЬ КАРТИНКУ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        label = tk.Label(self.root, image=photo, width=580, height=200)
        label.image = photo
        label.pack()

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

        tk.Checkbutton(self.root, text="Silence auto skip", variable=self._is_auto_skip_enabled).pack(padx=20, pady=5)

        tk.Label(root, text="SETTINGS BELOW, (SET BEFORE SELECTING FILE)").pack(padx=20, pady=5)

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

        tk.Label(root, text="Min speech duration").pack(anchor="w", padx=20)
        self.min_speech_var = tk.IntVar(value=250)
        self.min_speech_scale = tk.Scale(
            root, variable=self.min_speech_var,
            from_=250, to=2000, resolution=50,
            orient="horizontal", length=200,
            tickinterval=250,
        )
        self.min_speech_scale.pack(fill="x", padx=20, pady=2)

        tk.Label(root, text="Min silence duration").pack(anchor="w", padx=20)
        self.min_silence_var = tk.IntVar(value=1000)
        self.min_silence_scale = tk.Scale(
            root, variable=self.min_silence_var,
            from_=200, to=3000, resolution=100,
            orient="horizontal", length=200,
            tickinterval= 400
        )
        self.min_silence_scale.pack(fill="x", padx=20, pady=2)

        tk.Button(self.root, text="download chopped file", width= 25, command=self._start_download).pack(side="left", padx=20)

        self.status_label = tk.Label(root, text="", fg="gray")
        self.status_label.pack(pady=2, side="left", padx=20)

        self.how_much_second_chopped = tk.Label(root, text="", fg="green")
        self.how_much_second_chopped.pack(pady=2, side="left", padx=5)

        self._update_progress()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _open_file(self):
        self.txt_path.config(state="normal")

        audio_filepath = filedialog.askopenfilename(title="Select file", filetypes=[("Audio", "*.mp3 *.wav *.m4a *.ogg *.flac")])
        if audio_filepath:
            self.txt_path.delete(0, tk.END)
            self.txt_path.insert(0, audio_filepath)
        else:
            self.txt_path.config(state="readonly")
            return

        self.seek_var.set(0.0)
        self.seek_scale.config(state="normal")

        self.txt_path.config(state="readonly")
        self.vad_controller = VADAudioController(audio_path=audio_filepath, VAD_sensetivity=self.vad_scale.get(), min_speech_duration_ms=self.min_speech_scale.get(), min_silence_duration_ms=self.min_silence_scale.get())
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

            progress = (self.vad_controller.seconds_processed /
                        max(0.1, self.vad_controller.audio_length) * 100)
            self.root.after(0, lambda p=progress:
            self.status_label.config(text=f"Loading: {p:.0f}%"))

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

    def _start_download(self):
        if not self.txt_path.get():
            messagebox.showwarning("Error", "Choose audiofile first!")
            return
        if not self.vad_controller:
            messagebox.showerror("Error", "VAD-controller doesnt initialized")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save chopped file",
            defaultextension=".wav",
            filetypes=[("WAV", "*.wav"), ("MP3", "*.mp3"), ("All", "*.*")],
            initialfile=f"{Path(self.txt_path.get()).stem}_processed.wav"
        )
        if not save_path:
            return

        threading.Thread(
            target=self._download_task,
            args=(save_path,),
            daemon=True
        ).start()

    def _on_download_success(self, path: str):
        self.status_label.config(text=f"Saved: {Path(path).name}", fg="green")
        self.root.after(250, self.how_much_second_chopped.config(
            text=f"{int(self.vad_controller.seconds_skipped)} Seconds skipped"))

    def _on_download_error(self, error_msg: str):
        self.status_label.config(text=f"Error", fg="red")
        messagebox.showerror("Save error", f"Can't save file:\n{error_msg}")

    def _download_task(self, save_path):
        try:
            while self.vad_controller.seconds_processed < self.vad_controller.audio_length:
                # Обновляем статус с прогрессом
                progress = (self.vad_controller.seconds_processed /
                           max(0.1, self.vad_controller.audio_length) * 100)
                self.root.after(0, lambda p=progress:
                    self.status_label.config(text=f"Loading: {p:.0f}%"))

            self.vad_controller.downloadChoppedAudio(save_path)
            self.root.after(0, lambda: self._on_download_success(save_path))
        except Exception as e:
            self.root.after(0, lambda: self._on_download_error(str(e)))

