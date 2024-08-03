import wave
from mutagen.mp3 import MP3
from mutagen.aac import AAC
import os

def get_duration(file):
    ext = os.path.splitext(file)[1].lower()
    if ext == '.mp3':
        return get_duration_mp3(file)
    elif ext == '.wav':
        return get_duration_wav(file)
    elif ext == '.aac':
        return get_duration_aac(file)
    elif ext == '.3gpp':
        return get_duration_3gpp(file)
    elif ext == '.wma':
        return get_duration_wma(file)
    else:
        return "N.A."

# tested
def get_duration_mp3(file):
    audio = MP3(file)
    return format_duration(audio.info.length)

def get_duration_wav(file):
    try:
        with wave.open(file, 'rb') as audio:
            duration_seconds = audio.getnframes() / float(audio.getframerate())
            return format_duration(duration_seconds)
    except Exception as e:
        return "N.A."

def get_duration_aac(file):
    audio = AAC(file)
    return format_duration(audio.info.length)

def get_duration_3gpp(file):
    # `mutagen` non ha un supporto diretto per `.3gpp`, quindi restituiamo N.A.
    return "N.A."

def get_duration_wma(file):
    # `mutagen` non supporta `.wma`, quindi restituiamo N.A.
    return "N.A."

def format_duration(duration_seconds):
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes:02}:{seconds:02}"
