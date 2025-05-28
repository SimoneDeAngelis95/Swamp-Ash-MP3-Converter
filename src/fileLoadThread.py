from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import pathlib
import json
import re
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
        current_row = self.lastRowIndex                                      # redundant, but useful for clarity

        for file in self.files:

            # TITLE
            title = pathlib.Path(file).stem                                  # get the file name without extension
            self.data.emit(current_row, GB._TITLECOLUMN_, title)

            # LENGTH
            time_string = get_duration(file)
            self.data.emit(current_row, GB._LENGTHCOLUMN_, time_string)

            # FORMAT
            format = pathlib.Path(file).suffix                               # get the file extension
            format = format.split(".")                                       # split the string to remove the dot
            format = format[1]
            self.data.emit(current_row, GB._ORIGINALFORMAT_, format)

            # ORIGINAL PATH
            self.data.emit(current_row, GB._ORIGINALPATH_, file)

            # HIDDEN TAGS
            tags = {"title": title, "number": "", "artist": "", "album": "", "year": "", "genre": ""}
            
            if(format != "mp3"):
                if re.match(r'^\d{2}\s', tags["title"]):                     # check if the title starts with two digits followed by a space
                    tags["number"] = tags["title"][:2]                       # if it does, set the number tag to the first two digits
            else:

                #MUTAGEN VERSION OF GETTING TAGS FROM MP3
                audio = MP3(file, ID3=EasyID3)
                tagTitle = ", ".join(audio.get("title", [""]))               # get the tag "title"

                if tagTitle != "":
                    tags["title"] = tagTitle

                tags["number"] = ", ".join(audio.get("tracknumber", [""]))   # get the tag "tracknumber"
                tags["artist"] = ", ".join(audio.get("artist", [""]))        # get the tag "artist"
                tags["album"] = ", ".join(audio.get("album", [""]))          # get the tag "album"
                tags["year"] = ", ".join(audio.get("date", [""]))            # get the tag "date"
                tags["genre"] = ", ".join(audio.get("genre", [""]))          # get the tag "genre"

            json_tags = json.dumps(tags)
            self.data.emit(current_row, GB._HIDDENTAGS_, json_tags)
            current_row = current_row + 1
    
        self.finished.emit()