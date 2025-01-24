import os
import platform

_APP_NAME_ = "Swamp Ash MP3 Converter"

if platform.system() == 'Darwin' or platform.system() == 'Linux':
    _DEFAULT_EXPORT_PATH_ = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    _FFMPEG_PATH_ = "./ffmpeg"
elif platform.system() == 'Windows':
    _DEFAULT_EXPORT_PATH_ = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    _FFMPEG_PATH_ = "./ffmpeg.exe"

_REMOVECOLUMN_ = 0
_TITLECOLUMN_ = 1
_LENGTHCOLUMN_ = 2
_ORIGINALFORMAT_ = 3
_SAMPLERATE_ = 4
_BITRATE_ = 5
_COPYSETTINGS_ = 6
_EDITTAGS_ = 7
_ORIGINALPATH_ = 8
_HIDDENTAGS_ = 9

#_REMOVE_BTN_IMG_PATH_ = "./images/remove.png"
_REMOVE_BTN_IMG_PATH_ = "./remove.png" # Compiled Version

_SAMPLERATE_LIST_ = ["44100", "48000"]
_BITRATE_LIST_ = ["320", "256", "224", "192", "160", "128", "112", "96", "80", "64", "56", "48", "40", "32"]

_FILE_ALLOWED_ = "Audio Files (*.wav *.mp3 *.aac *.wma *.3gpp)"
_ALLOWED_EXTENSIONS_ = [".wav", ".mp3", ".aac", ".wma", ".3gpp"]