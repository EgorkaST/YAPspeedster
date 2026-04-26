import os
import vlc

class Player:
    def __init__(self):
        self.instance = vlc.Instance("--audio-filter=scaletempo")
        self.player = self.instance.media_player_new()

    def load(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File {file_path} not found')
        self.media = self.instance.media_new(file_path)
        self.player.set_media(self.media)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def get_pos(self) -> float:
        return self.player.get_position()

    def get_duration(self) -> int:
        return max(0, self.player.get_length())

    def is_playing(self) -> bool:
        return self.player.get_state() == vlc.State.Playing

    def set_speed_rate(self, rate: float):
        rate = max(0, min(3.0, rate))
        self.player.set_rate(rate)

    def set_time(self, ms: int):
        if ms < 0:
            ms = 0

        dur = self.get_duration()
        if 0 < dur < ms:
            ms = dur

        self.player.set_time(ms)

    def get_time(self) -> int:
        return self.player.get_time()