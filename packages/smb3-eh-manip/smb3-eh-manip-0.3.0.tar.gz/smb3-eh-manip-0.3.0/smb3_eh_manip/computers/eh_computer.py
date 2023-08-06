from smb3_eh_manip.computers.opencv_computer import OpencvComputer
from smb3_eh_manip.settings import config

VIDEO_OFFSET_FRAMES = 106


class EhComputer(OpencvComputer):
    def __init__(self):
        super().__init__(
            "ehvideo",
            config.get("app", "eh_video_path"),
            config.getint("app", "latency_frames") + VIDEO_OFFSET_FRAMES,
            config.get("app", "eh_start_frame_image_path"),
        )