from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
import globalVariables as GB
import subprocess
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

        # GESTIRE CONFLITTI NOME
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
                "-metadata", "tracknumber=" + self.tags["number"],
                "-metadata", "artist=" + self.tags["artist"],
                "-metadata", "album=" + self.tags["album"],
                "-metadata", "Date=" + self.tags["year"],
                "-metadata", "genre=" + self.tags["genre"],
                outPath
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #_ = process.communicate() # devo catturare comunque l'output altrimenti si blocca, ma a quanto pare no
            
            while process.poll() is None:
                if self.stop == True:
                    process.terminate()
                    os.remove(outPath)
                    self.stopped.emit()
                    break
            
            if self.stop == False:
                self.result.emit(True)
            # in caso di errore nel subprocess esso verrà gestito dal try/except e quindi automaticamente emetterà falso, fidati, l'ho testato
        except:
            self.result.emit(False)

        self.finished.emit()

    def stopFn(self):
        self.stop = True