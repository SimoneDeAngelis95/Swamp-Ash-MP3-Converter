from PyQt6.QtCore import QThread, pyqtSignal
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

import json
import pathlib
import re

from audioFileDuration import get_duration
import globalVariables as GB


class FileLoadThread(QThread):
    completed = pyqtSignal()
    data = pyqtSignal(int, int, str)
    invalidFile = pyqtSignal(str)

    def __init__(self, parent, files, lastRowIndex):
        super().__init__(parent=parent)
        self.files = files
        self.lastRowIndex = lastRowIndex
        self.cancelRequested = False

    def cancel(self):
        self.cancelRequested = True

    def run(self):
        currentRow = self.lastRowIndex

        for file in self.files:
            if self.cancelRequested:
                break

            try:
                title = pathlib.Path(file).stem
                timeString = get_duration(file)
                fileFormat = pathlib.Path(file).suffix.lstrip(".").lower()
                tags = {
                    "title": title,
                    "number": "",
                    "artist": "",
                    "album": "",
                    "year": "",
                    "genre": "",
                }

                if fileFormat == "mp3":
                    audio = MP3(file, ID3=EasyID3)
                    tagTitle = ", ".join(audio.get("title", [""]))
                    if tagTitle:
                        tags["title"] = tagTitle
                    tags["number"] = ", ".join(audio.get("tracknumber", [""]))
                    tags["artist"] = ", ".join(audio.get("artist", [""]))
                    tags["album"] = ", ".join(audio.get("album", [""]))
                    tags["year"] = ", ".join(audio.get("date", [""]))
                    tags["genre"] = ", ".join(audio.get("genre", [""]))
                elif re.match(r"^\d{2}\s", title):
                    tags["number"] = title[:2]

                rowData = {
                    GB._TITLECOLUMN_: title,
                    GB._LENGTHCOLUMN_: timeString,
                    GB._ORIGINALFORMAT_: fileFormat,
                    GB._ORIGINALPATH_: file,
                    GB._HIDDENTAGS_: json.dumps(tags),
                }
                for column, value in rowData.items():
                    self.data.emit(currentRow, column, value)
                currentRow += 1
            except Exception:
                self.invalidFile.emit(file)

        self.completed.emit()
