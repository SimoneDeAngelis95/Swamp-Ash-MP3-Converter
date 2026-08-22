from PyQt6.QtCore import QThread, pyqtSignal

import json
import os
import platform
import subprocess

import globalVariables as GB


class ConversionThread(QThread):
    completed = pyqtSignal(bool, bool)

    def __init__(self, parent, title, filePath, bitRate, fc, tags, outputPath):
        super().__init__(parent=parent)
        self.title = title
        self.filePath = filePath
        self.bitRate = bitRate
        self.fc = fc
        self.tags = json.loads(tags)
        self.outputPath = outputPath
        self.process = None
        self.cancelRequested = False
        self.outputFile = None

    def cancel(self):
        self.cancelRequested = True
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.terminate()
            except OSError:
                pass

    def forceKill(self):
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.kill()
            except OSError:
                pass

    def _removePartialOutput(self):
        if self.outputFile and os.path.isfile(self.outputFile):
            try:
                os.remove(self.outputFile)
            except OSError:
                pass

    def run(self):
        outPath = os.path.join(self.outputPath, self.title)
        if os.path.exists(outPath + ".mp3"):
            index = 1
            while os.path.exists(f"{outPath} ({index}).mp3"):
                index += 1
            outPath = f"{outPath} ({index})"
        self.outputFile = outPath + ".mp3"

        try:
            bitRate = self.bitRate.split()[0] + "k"
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
                self.outputFile,
            ]

            processOptions = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
            if platform.system() == "Windows":
                processOptions["creationflags"] = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(cmd, **processOptions)
            if self.cancelRequested:
                self.cancel()

            returnCode = self.process.wait()
            wasCancelled = self.cancelRequested
            success = returnCode == 0 and not wasCancelled

            if not success:
                self._removePartialOutput()
            self.completed.emit(success, wasCancelled)
        except Exception:
            self._removePartialOutput()
            self.completed.emit(False, self.cancelRequested)
        finally:
            self.process = None
