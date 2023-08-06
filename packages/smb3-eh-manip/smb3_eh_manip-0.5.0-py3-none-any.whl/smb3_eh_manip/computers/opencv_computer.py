import logging
import time

import cv2
import numpy as np
import pyautogui

from smb3_eh_manip.settings import config
from smb3_eh_manip.video_player import VideoPlayer

CLEAR_SIGHTING_DURATION_SECONDS = 10


class OpencvComputer:
    def __init__(
        self,
        player_window_title,
        player_video_path,
        start_frame_image_path,
        video_offset_frames=0,
    ):
        self.player_window_title = player_window_title
        self.start_frame_image_path = start_frame_image_path
        self.show_capture_video = config.getboolean("app", "show_capture_video")
        self.autoreset = config.getboolean("app", "autoreset")
        self.enable_fceux_tas_start = config.getboolean("app", "enable_fceux_tas_start")
        self.write_capture_video = config.getboolean("app", "write_capture_video")
        self.enable_video_player = config.getboolean("app", "enable_video_player")
        self.track_end_stage_clear_text_time = config.getboolean(
            "app", "track_end_stage_clear_text_time"
        )
        self.playing = False
        self.current_time = time.time()
        self.start_time = -1

        if self.track_end_stage_clear_text_time:
            self.last_clear_sighting_time = -1
            self.end_stage_clear_text_template = cv2.imread(
                config.get("app", "end_stage_clear_text_path")
            )
        self.reset_template = cv2.imread(config.get("app", "reset_image_path"))
        self.template = cv2.imread(self.start_frame_image_path)
        self.capture = cv2.VideoCapture(config.getint("app", "video_capture_source"))
        if not self.capture.isOpened():
            logging.info("Cannot open camera")
            exit()
        if self.write_capture_video:
            path = config.get("app", "write_capture_video_path")
            fps = float(self.capture.get(cv2.CAP_PROP_FPS)) or 60
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.output_video = cv2.VideoWriter(
                path, cv2.VideoWriter_fourcc(*"MPEG"), fps, (width, height)
            )
        if self.enable_video_player:
            self.video_player = VideoPlayer(player_video_path, video_offset_frames)

    def tick(self):
        self.current_time = time.time()
        ret, frame = self.capture.read()
        if not ret:
            logging.warn("Can't receive frame (stream end?). Exiting ...")
            exit()
        if self.write_capture_video:
            self.output_video.write(frame)
        if (
            self.track_end_stage_clear_text_time
            and self.playing
            and self.current_time - self.last_clear_sighting_time
            > CLEAR_SIGHTING_DURATION_SECONDS
            and list(
                OpencvComputer.locate_all_opencv(
                    self.end_stage_clear_text_template, frame
                )
            )
        ):
            self.last_clear_sighting_time = self.current_time
            logging.info(
                f"Cleared a level at {self.last_clear_sighting_time-self.start_time}"
            )
        if (
            self.autoreset
            and self.playing
            and list(OpencvComputer.locate_all_opencv(self.reset_template, frame))
        ):
            self.playing = False
            self.start_time = -1
            if self.enable_video_player:
                self.video_player.reset()
            if self.enable_fceux_tas_start:
                pyautogui.press("pause")
                # TODO need to pause, rewind, increment forward TAS
                # time.sleep(0.001)
                # with pyautogui.hold("shift"):
                #    pyautogui.press("pageup")
                # for _i in range(offset):
                #    pyautogui.press("backslash")
            logging.info(f"Detected reset")
        if not self.playing:
            results = list(OpencvComputer.locate_all_opencv(self.template, frame))
            if self.show_capture_video:
                for x, y, needleWidth, needleHeight in results:
                    top_left = (x, y)
                    bottom_right = (x + needleWidth, y + needleHeight)
                    cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 5)
            if results:
                self.playing = True
                self.start_time = time.time()
                if self.enable_fceux_tas_start:
                    pyautogui.press("pause")
                if self.enable_video_player:
                    self.video_player.play()
                logging.info(f"Detected start frame")
        if self.show_capture_video:
            cv2.imshow("capture", frame)
        cv2.waitKey(1)

    def terminate(self):
        self.video_player.terminate()
        if self.write_capture_video:
            self.output_video.release()
        self.capture.release()
        cv2.destroyAllWindows()

    @classmethod
    def locate_all_opencv(
        cls,
        needleImage,
        haystackImage,
        limit=10000,
        region=None,
        step=1,
        confidence=float(config.get("app", "confidence")),
    ):
        """
        TODO - rewrite this
            faster but more memory-intensive than pure python
            step 2 skips every other row and column = ~3x faster but prone to miss;
                to compensate, the algorithm automatically reduces the confidence
                threshold by 5% (which helps but will not avoid all misses).
            limitations:
            - OpenCV 3.x & python 3.x not tested
            - RGBA images are treated as RBG (ignores alpha channel)
        """

        confidence = float(confidence)

        needleHeight, needleWidth = needleImage.shape[:2]

        if region:
            haystackImage = haystackImage[
                region[1] : region[1] + region[3], region[0] : region[0] + region[2]
            ]
        else:
            region = (0, 0)  # full image; these values used in the yield statement
        if (
            haystackImage.shape[0] < needleImage.shape[0]
            or haystackImage.shape[1] < needleImage.shape[1]
        ):
            # avoid semi-cryptic OpenCV error below if bad size
            raise ValueError(
                "needle dimension(s) exceed the haystack image or region dimensions"
            )

        if step == 2:
            confidence *= 0.95
            needleImage = needleImage[::step, ::step]
            haystackImage = haystackImage[::step, ::step]
        else:
            step = 1

        # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
        result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
        match_indices = np.arange(result.size)[(result > confidence).flatten()]
        matches = np.unravel_index(match_indices[:limit], result.shape)

        if len(matches[0]) == 0:
            return

        # use a generator for API consistency:
        matchx = matches[1] * step + region[0]  # vectorized
        matchy = matches[0] * step + region[1]
        for x, y in zip(matchx, matchy):
            yield (x, y, needleWidth, needleHeight)
