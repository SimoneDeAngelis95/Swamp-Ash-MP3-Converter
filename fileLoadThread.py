from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import pathlib
import json
import re
#from pydub import AudioSegment
from audioFileDuration import get_duration
import globalVariables as GB

class FileLoadThread(QThread):
    finished = pyqtSignal()
    data = pyqtSignal(int, int, str)

    def __init__(self, parent, files, lastRowIndex):
        super().__init__(parent=parent)
        self.files = files
        self.lastRowIndex = lastRowIndex

    def run(self):
        current_row = self.lastRowIndex # ridondante, ma era per non riscrivere tutto

        for file in self.files:

            # TITLE
            title = pathlib.Path(file).stem # grazie alla libreria pathlib ottengo il nome del file (.name restituisce anche l'estensione, .stem no)
            self.data.emit(current_row, GB._TITLECOLUMN_, title)

            # LENGTH
            time_string = get_duration(file)
            self.data.emit(current_row, GB._LENGTHCOLUMN_, time_string)

            # FORMAT
            format = pathlib.Path(file).suffix # grazie alla libreria pathlib ottengo l'estensione del file
            format = format.split(".")         # splitto la stringa per ottenere solo l'estensione
            format = format[1]
            self.data.emit(current_row, GB._ORIGINALFORMAT_, format)

            # ORIGINAL PATH
            self.data.emit(current_row, GB._ORIGINALPATH_, file)

            # HIDDEN TAGS
            tags = {"title": title, "number": "", "artist": "", "album": "", "year": "", "genre": ""}
            
            if(format != "mp3"):
                if re.match(r'^\d{2}\s', tags["title"]): # se i primi due caratteri di tags["title"] sono numeri seguiti da uno spazio bianco
                    tags["number"] = tags["title"][:2]   # prendo i primi due caratteri della stringa tags["title"]
            else:

                #MUTAGEN VERSION OF GETTING TAGS FROM MP3
                audio = MP3(file, ID3=EasyID3)
                tagTitle = ", ".join(audio.get("title", [""]))  # Recupera il tag "title"

                if tagTitle != "":
                    tags["title"] = tagTitle

                tags["number"] = ", ".join(audio.get("tracknumber", [""]))  # Recupera il tag "tracknumber"
                tags["artist"] = ", ".join(audio.get("artist", [""]))  # Recupera il tag "artist"
                tags["album"] = ", ".join(audio.get("album", [""]))  # Recupera il tag "album"
                tags["year"] = ", ".join(audio.get("date", [""]))  # Recupera il tag "date"
                tags["genre"] = ", ".join(audio.get("genre", [""]))  # Recupera il tag "genre"

            json_tags = json.dumps(tags)
            self.data.emit(current_row, GB._HIDDENTAGS_, json_tags)
            current_row = current_row + 1
    
        self.finished.emit()