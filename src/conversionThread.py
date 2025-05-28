from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
import globalVariables as GB
import subprocess
import platform
import os
import json

class ConversionThread(QThread):
    finished = pyqtSignal()
    result = pyqtSignal(bool)
    stopped = pyqtSignal()

    def __init__(self, parent, title, filePath, bitRate, fc, tags, outputPath):
        super().__init__(parent=parent)
        self.title = title
        self.filePath = filePath
        self.bitRate = bitRate
        self.fc = fc
        self.tags = json.loads(tags)
        self.outputPath = outputPath
        self.stop = False

    def run(self):

        # Manage output path and filename
        outPath = self.outputPath + "/" + self.title
        if os.path.exists(outPath + ".mp3"):
            index = 0
            postFix = ""
            while os.path.exists(outPath + postFix + ".mp3"):
                index += 1
                postFix = " (" + str(index) + ")"
            outPath = self.outputPath + "/" + self.title + postFix
        outPath += ".mp3"

        try:
            bitRate = self.bitRate[:3] + "k"
            cmd = [
                GB._FFMPEG_PATH_,
                "-i", self.filePath,
                "-ar", self.fc,
                "-b:a", bitRate,
                "-metadata", "title=" + self.tags["title"],
                "-metadata", "track=" + self.tags["number"],
                "-metadata", "artist=" + self.tags["artist"],
                "-metadata", "album=" + self.tags["album"],
                "-metadata", "Date=" + self.tags["year"],
                "-metadata", "genre=" + self.tags["genre"],
                outPath
            ]

            if platform.system() == 'Darwin' or platform.system() == 'Linux':
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif platform.system() == 'Windows':
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) # creationflags=subprocess.CREATE_NO_WINDOW needed to avoid opening a console window on Windows, not needed on Linux or MacOS
            
            while process.poll() is None:
                if self.stop == True:
                    process.terminate()
                    os.remove(outPath)
                    self.stopped.emit()
                    break
            
            if self.stop == False:
                self.result.emit(True)
        except:                               # in case of error in subprocess execution, we catch the exception
            self.result.emit(False)

        self.finished.emit()

    def stopFn(self):
        self.stop = True