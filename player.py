import os
import vlc

class Player:
    def __init__(self):
        self.instance = vlc.Instance()
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
        return self.player.position()

    def get_duration(self) -> int:
        return max(0, self.player.duration())

    def is_playing(self) -> bool:
        return self.player.get_state() == vlc.State.Playing