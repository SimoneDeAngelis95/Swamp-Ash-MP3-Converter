from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
import pathlib
import json
import re
import taglib
from pydub import AudioSegment
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
            mySong = AudioSegment.from_file(file)
            duration_ms = len(mySong)
            duration_seconds = duration_ms / 1000
            minutes = int(duration_seconds // 60) # In questa riga, stiamo calcolando i minuti dalla durata in secondi. L'operatore // esegue una divisione intera, il che significa che divide duration_seconds per 60 e restituisce la parte intera del risultato, che rappresenta i minuti.
            seconds = int(duration_seconds % 60)  # In questa riga, stiamo calcolando i secondi dalla durata in secondi. L'operatore % calcola il resto della divisione, quindi duration_seconds % 60 restituirà i secondi rimanenti dopo aver estratto i minuti.
            if(minutes < 10):
                minutes = "0" + str(minutes)
            if(seconds < 10):
                seconds = "0" + str(seconds)
            time_string = str(minutes) + ":" + str(seconds)
            self.data.emit(current_row, GB._LENGTHCOLUMN_, time_string)

            # FORMAT
            format = pathlib.Path(file).suffix # grazie alla libreria pathlib ottengo l'estensione del file
            format = format.split(".")
            format = format[1]
            self.data.emit(current_row, GB._ORIGINALFORMAT_, format)

            # ORIGINAL PATH
            self.data.emit(current_row, GB._ORIGINALPATH_, file)

            # HIDDEN TAGS
            if(format != "mp3"):
                tags = {"title": title, "number": "", "artist": "", "album": "", "year": "", "genre": ""}
                if re.match(r'^\d{2}\s', tags["title"]): # se i primi due caratteri di tags["title"] sono numeri seguiti da uno spazio bianco
                    tags["number"] = tags["title"][:2]   # prendo i primi due caratteri della stringa tags["title"]
            else:
                tag_title = ""
                tag_number = ""
                tag_artist = ""
                tag_album = ""
                tag_year = ""
                tag_genre = ""

                song = taglib.File(file)
                try:
                    tag_title = ", ".join(song.tags["TITLE"]) # siccome song.tags[...] restituisce una lista di elementi e li unisco in una lista separati da ", "
                except:
                    pass
                try:
                    tag_number = ", ".join(song.tags["TRACKNUMBER"])
                except:
                    pass
                try:
                    tag_artist = ", ".join(song.tags["ARTIST"])
                except:
                    pass
                try:
                    tag_album = ", ".join(song.tags["ALBUM"])
                except:
                    pass
                try:
                    tag_year = song.tags["DATE"][0] # altrimenti mi restituisce due date
                except:
                    pass
                try:
                    tag_genre = ", ".join(song.tags["GENRE"])
                except:
                    pass

                tags = {"title": tag_title, "number": tag_number, "artist": tag_artist, "album": tag_album, "year": tag_year, "genre": tag_genre}

            json_tags = json.dumps(tags)
            self.data.emit(current_row, GB._HIDDENTAGS_, json_tags)
            current_row = current_row + 1
    
        self.finished.emit()