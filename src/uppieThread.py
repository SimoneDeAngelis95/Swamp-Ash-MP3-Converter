from PyQt6.QtCore import QThread
from uppie import Uppie

import globalVariables as GB


class UpdateCheckThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.update_available = False
        self.remote_version = ""
        self.updater = Uppie(
            repo_owner="SimoneDeAngelis95",
            repo_name="Swamp-Ash-MP3-Converter",
            local_version=GB._APP_VERSION_,
        )

    def run(self):
        self.update_available = self.updater.is_update_available()

        if self.update_available and self.updater.latest_release:
            self.remote_version = (
                self.updater.latest_release.get("tag_name")
                or self.updater.latest_release.get("name", "")
            )


class UpdateInstallThread(QThread):
    def __init__(self, updater, parent=None):
        super().__init__(parent=parent)
        self.updater = updater
        self.success = False

    def run(self):
        self.success = self.updater.update()
