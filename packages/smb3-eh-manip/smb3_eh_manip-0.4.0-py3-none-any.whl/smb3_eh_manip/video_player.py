import vlc
from smb3_eh_manip.settings import config, NES_MS_PER_FRAME


class VideoPlayer:
    def __init__(self, player_video_path, video_offset_frames):
        self.player_seek_to_time = int(
            video_offset_frames * NES_MS_PER_FRAME
        ) + config.getint("app", "latency_ms")
        self.media_player = vlc.MediaPlayer()
        self.media_player.set_media(vlc.Media(player_video_path))
        self.media_player.video_set_scale(
            float(config.get("app", "video_player_scale"))
        )
        self.media_player.play()
        self.media_player.set_pause(True)
        self.media_player.set_time(self.player_seek_to_time)

    def play(self):
        self.media_player.set_pause(False)

    def reset(self):
        self.media_player.set_pause(True)
        self.media_player.set_time(self.player_seek_to_time)

    def terminate(self):
        self.media_player.stop()