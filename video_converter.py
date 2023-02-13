# This file contains the logic to convert the video to the proper encoding and resoulution
# It needs the ffmpeg.exe in the video folder
import pathlib

ffmpegPath = pathlib.Path("./ffmpeg.exe")
ffprobePath = pathlib.Path("./ffprobe.exe")

from converter import Converter
conv = Converter(str(ffmpegPath.resolve()), str(ffprobePath.resolve()))

print('test')