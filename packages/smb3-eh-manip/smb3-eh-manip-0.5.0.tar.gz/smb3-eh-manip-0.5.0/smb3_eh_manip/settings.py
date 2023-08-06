from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

NES_FRAMERATE = 60.0988139
NES_MS_PER_FRAME = 1000.0 / NES_FRAMERATE