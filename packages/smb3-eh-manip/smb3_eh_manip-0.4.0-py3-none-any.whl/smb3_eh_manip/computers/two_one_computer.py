from smb3_eh_manip.computers.opencv_computer import OpencvComputer
from smb3_eh_manip.settings import config


class TwoOneComputer(OpencvComputer):
    def __init__(self):
        super().__init__(
            "twoonevideo",
            config.get("app", "two_one_video_path"),
            config.get("app", "two_one_start_frame_image_path"),
        )