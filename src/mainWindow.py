from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtWidgets import QProgressDialog
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QDragEnterEvent
from PyQt6.QtGui import QDropEvent
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from editTagsWindow import EditTagsWindow
import json
import os
import platform
import globalVariables as GB
from fileLoadThread import FileLoadThread
from conversionThread import ConversionThread
from uppieThread import UpdateCheckThread
from uppieThread import UpdateInstallThread

_UPDATE_AVAILABLE_TITLE = "Update available"
_UPDATE_AVAILABLE_TEXT = "Version {version} of {app_name} is available."
_UPDATE_AVAILABLE_QUESTION = "Would you like to download it and start the installation?"
_UPDATE_ACCEPT = "Download and install"
_UPDATE_LATER = "Later"
_UPDATE_PROGRESS_TITLE = "Update"
_UPDATE_PROGRESS_TEXT = "Downloading the update..."
_UPDATE_SUCCESS_TITLE = "Update downloaded"
_UPDATE_SUCCESS_MACOS = "The DMG has been opened. Close the application and drag it into the Applications folder to complete the update."
_UPDATE_SUCCESS_WINDOWS = "The installer has been started. Swamp Ash MP3 Converter will now close."
_UPDATE_ERROR_TITLE = "Update failed"
_UPDATE_ERROR_TEXT = "The update could not be downloaded or started. Please try again later."
_UPDATE_RUNNING_TITLE = "Update in progress"
_UPDATE_RUNNING_TEXT = "Please wait for the download to finish before closing the application."
_INVALID_FILE_TITLE = "Invalid audio file"
_INVALID_FILE_TEXT = "The selected file could not be read:\n{file_name}"
_INVALID_TITLE_TITLE = "Invalid file name"
_INVALID_TITLE_TEXT = "The output name contains characters that are not allowed:\n{file_name}"

class mainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.uploading = False # variable to check if the user is uploading files or not
        self.converting = False
        self.loadThread = None
        self.conversionThread = None
        self.startNextConversionAfterThread = False
        self.closeRequested = False
        self.pendingUpdater = None
        self.pendingUpdateVersion = ""
        self.updateCheckThread = None
        self.updateInstallThread = None
        self.updateProgressDialog = None
        self.updateProgressTimer = QTimer(self)
        self.updateProgressTimer.setInterval(200)
        self.updateProgressTimer.timeout.connect(self.refreshUpdateProgress)
        
        self.setGeometry(0, 0, 900, 600)
        self.setWindowTitle(GB._APP_NAME_ + " " + GB._APP_VERSION_)

        # ====== ADD FILE BTN ======
        self.btn_addFile = QPushButton(self, text="add file")
        self.btn_addFile.clicked.connect(self.__slot__chooseFilesAndAdd)

        # ===== PROGRESS BAR ======
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.progressBar.hide()

        # ===== CONVERSION TABLE AND BUTTONS =====
        self.conversionIndex = 0

        self.tbl_conversion = QTableWidget(self)
        self.tbl_conversion.setColumnCount(2)
        self.tbl_conversion.setHorizontalHeaderItem(0, QTableWidgetItem("File"))
        self.tbl_conversion.setHorizontalHeaderItem(1, QTableWidgetItem("Status"))
        self.tbl_conversion.hide()

        self.btn_stopConversion = QPushButton(self)
        self.btn_stopConversion.setText("Stop")
        self.btn_stopConversion.hide()
        self.btn_stopConversion.clicked.connect(self.__slot__stopConversion)

        # FUTURE RELEASE
        #self.btn_clearQueue = QPushButton(self)
        #self.btn_clearQueue.setText("Clear Queue")
        #self.btn_clearQueue.hide()
        #self.btn_clearQueue.clicked.connect(self.__slot__clearQueue)

        self.btn_done = QPushButton(self)
        self.btn_done.setText("Done")
        self.btn_done.setDisabled(True)
        self.btn_done.hide()
        self.btn_done.clicked.connect(self.__slot__resetAndStayReady)

        # ====== FILE LIST TABLE ======
        self.tbl_fileList = QTableWidget(self)
        self.tbl_fileList.setColumnCount(10)
        self.tbl_fileList.setHorizontalHeaderItem(GB._REMOVECOLUMN_, QTableWidgetItem("Remove"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._TITLECOLUMN_, QTableWidgetItem("File Name"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._LENGTHCOLUMN_, QTableWidgetItem("Length"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._ORIGINALFORMAT_, QTableWidgetItem("Original Format"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._SAMPLERATE_, QTableWidgetItem("Sample Rate"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._BITRATE_, QTableWidgetItem("Bit Rate"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._COPYSETTINGS_, QTableWidgetItem("Copy Settings For All"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._EDITTAGS_, QTableWidgetItem("Edit Tags"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._ORIGINALPATH_, QTableWidgetItem("Original Path"))
        self.tbl_fileList.setHorizontalHeaderItem(GB._HIDDENTAGS_, QTableWidgetItem("Hidden Tags"))
        self.tbl_fileList.setColumnHidden(GB._HIDDENTAGS_, True)
        self.tbl_fileList.resizeColumnsToContents()
        self.tbl_fileList.itemChanged.connect(self.__slot__resizeTableAndCheckButtons)

        # ====== CLEAR LIST BTN ======
        self.btn_clearList = QPushButton(self, text="Remove All")
        self.btn_clearList.setEnabled(False)
        self.btn_clearList.clicked.connect(self.__slot__clearList)
        
        # ====== DESTINATION PATH ======
        self.entry_destinationPath = QLineEdit(self)
        self.entry_destinationPath.setEnabled(False)
        self.entry_destinationPath.setStyleSheet("color: rgb(0, 0, 0);")
        self.entry_destinationPath.setText(GB._DEFAULT_EXPORT_PATH_)

        # ====== DESTINATION PATH BTN ======
        self.btn_destinationPath = QPushButton(self, text="Choose Destination Path")
        self.btn_destinationPath.clicked.connect(self.__slot__openChoosePathDialog)

        # ====== CONVERT BTN ======
        self.btn_convert = QPushButton(self, text="Start Convertion")
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self.__slot__startConversion)

        # ===== LAYOUTS =====
        self.mainVerticalLayout = QVBoxLayout(self)
        self.mainVerticalLayout.addWidget(self.btn_addFile)
        self.mainVerticalLayout.addWidget(self.progressBar)
        self.mainVerticalLayout.addWidget(self.tbl_fileList)
        self.mainVerticalLayout.addWidget(self.tbl_conversion)

        self.conversionBtnsLayout = QHBoxLayout()
        self.conversionBtnsLayout.addWidget(self.btn_stopConversion)
        #self.conversionBtnsLayout.addWidget(self.btn_clearQueue)
        self.conversionBtnsLayout.addWidget(self.btn_done)

        self.mainVerticalLayout.addLayout(self.conversionBtnsLayout)

        self.mainVerticalLayout.addWidget(self.btn_clearList)
        
        self.mainVerticalLayout.addSpacing(-10)

        self.destinationPathLayout = QHBoxLayout()
        self.destinationPathLayout.addWidget(self.entry_destinationPath)
        self.destinationPathLayout.addWidget(self.btn_destinationPath)
        self.mainVerticalLayout.addLayout(self.destinationPathLayout)

        self.mainVerticalLayout.addSpacing(-10)

        self.mainVerticalLayout.addWidget(self.btn_convert)
        
        # ===== TAG WINDOWS =====
        self.tagWin = EditTagsWindow()
        self.tagWin.updateTags.connect(self.__slot__updateTags)
        self.tagWin.updateTagsForAll.connect(self.__slot__updateTagsForAll)

        # ===== DRAG AND DROP =====
        self.setAcceptDrops(True)
        QTimer.singleShot(1000, self.checkForUpdates)

    # ===== APPLICATION UPDATE =====
    def checkForUpdates(self):
        if self.updateCheckThread is not None:
            return

        self.updateCheckThread = UpdateCheckThread(self)
        self.updateCheckThread.finished.connect(self.updateCheckThreadFinished)
        self.updateCheckThread.finished.connect(self.updateCheckThread.deleteLater)
        self.updateCheckThread.start()

    def updateCheckThreadFinished(self):
        updater = self.updateCheckThread.updater
        updateAvailable = self.updateCheckThread.update_available
        remoteVersion = self.updateCheckThread.remote_version
        self.updateCheckThread = None

        if self.closeRequested:
            QTimer.singleShot(0, self.close)
            return

        if not updateAvailable:
            return

        if self.uploading or self.converting:
            self.pendingUpdater = updater
            self.pendingUpdateVersion = remoteVersion
            return

        self.showUpdateAvailable(updater, remoteVersion)

    def showUpdateAvailable(self, updater, remoteVersion):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(_UPDATE_AVAILABLE_TITLE)
        if remoteVersion:
            msgBox.setText(_UPDATE_AVAILABLE_TEXT.format(version=remoteVersion, app_name=GB._APP_NAME_))
        else:
            msgBox.setText(f"A newer version of {GB._APP_NAME_} is available.")
        msgBox.setInformativeText(_UPDATE_AVAILABLE_QUESTION)
        installButton = msgBox.addButton(_UPDATE_ACCEPT, QMessageBox.ButtonRole.AcceptRole)
        msgBox.addButton(_UPDATE_LATER, QMessageBox.ButtonRole.RejectRole)
        msgBox.exec()

        if msgBox.clickedButton() == installButton:
            self.startUpdate(updater)

    def startUpdate(self, updater):
        self.updateProgressDialog = QProgressDialog(
            _UPDATE_PROGRESS_TEXT,
            "",
            0,
            100,
            self,
        )
        self.updateProgressDialog.setWindowTitle(_UPDATE_PROGRESS_TITLE)
        self.updateProgressDialog.setCancelButton(None)
        self.updateProgressDialog.setAutoClose(False)
        self.updateProgressDialog.setAutoReset(False)
        self.updateProgressDialog.setMinimumDuration(0)
        self.updateProgressDialog.setValue(0)

        self.updateInstallThread = UpdateInstallThread(updater, self)
        self.updateInstallThread.finished.connect(self.updateInstallFinished)
        self.updateInstallThread.finished.connect(self.updateInstallThread.deleteLater)
        self.updateProgressTimer.start()
        self.updateInstallThread.start()

    def refreshUpdateProgress(self):
        if self.updateInstallThread is None or self.updateProgressDialog is None:
            return
        self.updateProgressDialog.setValue(
            self.updateInstallThread.updater.get_progress_percentage()
        )

    def updateInstallFinished(self):
        success = self.updateInstallThread.success
        self.updateProgressTimer.stop()
        if self.updateProgressDialog is not None:
            self.updateProgressDialog.close()
            self.updateProgressDialog = None
        self.updateInstallThread = None

        if not success:
            QMessageBox.warning(self, _UPDATE_ERROR_TITLE, _UPDATE_ERROR_TEXT)
            return

        if platform.system() == "Windows":
            QMessageBox.information(self, _UPDATE_SUCCESS_TITLE, _UPDATE_SUCCESS_WINDOWS)
            QApplication.quit()
        elif platform.system() == "Darwin":
            QMessageBox.information(self, _UPDATE_SUCCESS_TITLE, _UPDATE_SUCCESS_MACOS)

    def showPendingUpdate(self):
        if self.uploading or self.converting or self.pendingUpdater is None:
            return

        updater = self.pendingUpdater
        remoteVersion = self.pendingUpdateVersion
        self.pendingUpdater = None
        self.pendingUpdateVersion = ""
        self.showUpdateAvailable(updater, remoteVersion)

    # ====== DRAG & DROP ======
    def dragEnterEvent(self, event: QDragEnterEvent):          # event that is called when a file (or folder) is dragged over the widget but not yet released
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):                    # the event that is called when a file (or folder) is dropped on the widget
        paths = event.mimeData().urls()
        list_file_path = []

        for path in paths:
            file_path = path.toLocalFile()
            file_extension = os.path.splitext(file_path)[1].lower()
            if not file_extension in GB._ALLOWED_EXTENSIONS_:
                pass
            else:
                list_file_path.append(file_path)
        
        self.startThreadForAddingSongToList(list_file_path)

    # ===== SLOTS =====
    def __slot__addToTable(self, row, column, data):
        if(row >= self.tbl_fileList.rowCount()):
            self.tbl_fileList.insertRow(row)

            # REMOVE BUTTON
            self.tbl_fileList.setCellWidget(row, GB._REMOVECOLUMN_, QPushButton())
            self.tbl_fileList.cellWidget(row, GB._REMOVECOLUMN_).setIcon(QIcon(GB._REMOVE_BTN_IMG_PATH_))
            self.tbl_fileList.cellWidget(row, GB._REMOVECOLUMN_).clicked.connect(self.__slot__removeAction)
            self.tbl_fileList.cellWidget(row, GB._REMOVECOLUMN_).clicked.connect(self.__slot__resizeTableAndCheckButtons) # both the remove button and the resizeTableAndCheckButtons slot are connected to the same signal, so when the button is clicked, both actions are performed

            # SAMPLE RATE
            self.tbl_fileList.setCellWidget(row, GB._SAMPLERATE_, QComboBox())
            for sr in GB._SAMPLERATE_LIST_:
                self.tbl_fileList.cellWidget(row, GB._SAMPLERATE_).addItem(sr)
            
            # BIT RATE
            self.tbl_fileList.setCellWidget(row, GB._BITRATE_, QComboBox())
            for br in GB._BITRATE_LIST_:
                brPlusPrefix = br + " Kbit/s"
                self.tbl_fileList.cellWidget(row, GB._BITRATE_).addItem(brPlusPrefix)

            # COPY SETTINGS FOR ALL
            self.tbl_fileList.setCellWidget(row, GB._COPYSETTINGS_, QPushButton())
            self.tbl_fileList.cellWidget(row, GB._COPYSETTINGS_).setText("Copy for All")
            self.tbl_fileList.cellWidget(row, GB._COPYSETTINGS_).clicked.connect(self.__slot__copySettingsForAll)

            # EDIT TAGS
            self.tbl_fileList.setCellWidget(row, GB._EDITTAGS_, QPushButton())
            self.tbl_fileList.cellWidget(row, GB._EDITTAGS_).setText("Edit Tags")
            self.tbl_fileList.cellWidget(row, GB._EDITTAGS_).clicked.connect(self.__slot__editTags)


        self.tbl_fileList.setItem(row, column, QTableWidgetItem(data))

        if(column != GB._TITLECOLUMN_):
            self.tbl_fileList.item(row, column).setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )

        
        self.tbl_fileList.resizeColumnsToContents()

    def __slot__addFilesFinished(self):
        self.tbl_fileList.setDisabled(False)

        for row in range(self.tbl_fileList.rowCount()):
            self.tbl_fileList.item(row, GB._LENGTHCOLUMN_).setForeground(QBrush(QColor(0, 0, 0)))
            self.tbl_fileList.item(row, GB._LENGTHCOLUMN_).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_fileList.item(row, GB._ORIGINALFORMAT_).setForeground(QBrush(QColor(0, 0, 0)))
            self.tbl_fileList.item(row, GB._ORIGINALFORMAT_).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_fileList.item(row, GB._ORIGINALPATH_).setForeground(QBrush(QColor(0, 0, 0)))

        self.btn_addFile.setDisabled(False)
        self.btn_destinationPath.setDisabled(False)

        if(self.tbl_fileList.rowCount() > 0):
            self.btn_clearList.setDisabled(False)
            self.btn_convert.setDisabled(False)

        self.progressBar.hide()
        self.uploading = False
        QTimer.singleShot(0, self.showPendingUpdate)

    def __slot__invalidFile(self, filePath):
        QMessageBox.warning(
            self,
            _INVALID_FILE_TITLE,
            _INVALID_FILE_TEXT.format(file_name=os.path.basename(filePath)),
        )

    def __slot__loadThreadFinished(self, finishedThread):
        if self.loadThread is finishedThread:
            self.loadThread = None

        if self.closeRequested:
            QTimer.singleShot(0, self.close)

    def __slot__chooseFilesAndAdd(self):
        choosen_files, _ = QFileDialog().getOpenFileNames(filter=GB._FILE_ALLOWED_, directory=GB._DEFAULT_EXPORT_PATH_)
        self.startThreadForAddingSongToList(choosen_files)
            
    def __slot__openChoosePathDialog(self):
        last_path = self.entry_destinationPath.text()
        new_path = QFileDialog().getExistingDirectory(directory=last_path)

        if(new_path != ""):
            self.entry_destinationPath.setText(new_path)
        else:
            self.entry_destinationPath.setText(last_path)

    def __slot__removeAction(self):
        buttonSender = self.sender()
        index = 0
        for index in range(self.tbl_fileList.rowCount()): # scroll all the table to find my check box sender and so spot the row
            if(self.tbl_fileList.cellWidget(index, GB._REMOVECOLUMN_) == buttonSender):
                break
        self.tbl_fileList.removeRow(index)

    def __slot__resizeTableAndCheckButtons(self):
        if(self.uploading == False):
            self.tbl_fileList.resizeColumnsToContents()
        
            if(self.tbl_fileList.rowCount() > 0):
                self.btn_clearList.setDisabled(False)
                self.btn_convert.setDisabled(False)
            else:
                self.btn_clearList.setDisabled(True)
                self.btn_convert.setDisabled(True)

    def __slot__copySettingsForAll(self):
        buttonSender = self.sender()
        index = 0
        for index in range(self.tbl_fileList.rowCount()): # scroll all the table to find my check box sender and so spot the row
            if(self.tbl_fileList.cellWidget(index, GB._COPYSETTINGS_) == buttonSender):
                break
        
        smpRate = self.tbl_fileList.cellWidget(index, GB._SAMPLERATE_).currentText()
        bitRate = self.tbl_fileList.cellWidget(index, GB._BITRATE_).currentText()

        for row in range(self.tbl_fileList.rowCount()):
            self.tbl_fileList.cellWidget(row, GB._SAMPLERATE_).setCurrentText(smpRate)
            self.tbl_fileList.cellWidget(row, GB._BITRATE_).setCurrentText(bitRate)

    def __slot__editTags(self):
        buttonSender = self.sender()
        index = 0
        for index in range(self.tbl_fileList.rowCount()): # scroll all the table to find my check box sender and so spot the row
            if(self.tbl_fileList.cellWidget(index, GB._EDITTAGS_) == buttonSender):
                break

        # get the position of the main window to place the tag window
        mainWinPos = self.mapToGlobal(self.pos())
        x = mainWinPos.x()
        y = mainWinPos.y()

        self.tagWin.init(self.tbl_fileList.item(index, GB._HIDDENTAGS_).text(), x, y, index)
        self.tagWin.show()

    def __slot__updateTags(self, index, newTags):
        self.tbl_fileList.item(index, GB._HIDDENTAGS_).setText(newTags)

    def __slot__updateTagsForAll(self, whatTag, newTag):
        for row in range(self.tbl_fileList.rowCount()):
            tags = json.loads(self.tbl_fileList.item(row, GB._HIDDENTAGS_).text())
            tags[whatTag] = newTag
            json_tags = json.dumps(tags)
            self.tbl_fileList.setItem(row, GB._HIDDENTAGS_, QTableWidgetItem(json_tags))

    def __slot__clearList(self):
        n_of_row = self.tbl_fileList.rowCount()
        for i in range(n_of_row):
            self.tbl_fileList.removeRow(0)
        self.__slot__resizeTableAndCheckButtons()

    # ===== EVENTI =====
    def closeEvent(self, event):
        if self.updateCheckThread is not None:
            self.closeRequested = True
            self.hide()
            event.ignore()
            return
        if self.updateInstallThread is not None:
            QMessageBox.information(self, _UPDATE_RUNNING_TITLE, _UPDATE_RUNNING_TEXT)
            event.ignore()
            return
        if self.loadThread is not None and self.loadThread.isRunning():
            self.closeRequested = True
            self.hide()
            self.loadThread.cancel()
            event.ignore()
            return
        if self.conversionThread is not None and self.conversionThread.isRunning():
            self.closeRequested = True
            self.hide()
            self.conversionThread.cancel()
            QTimer.singleShot(2000, self.__slot__forceStopConversion)
            event.ignore()
            return
        self.tagWin.close()
        event.accept()

    # ===== CONVERSIONS SLOTS =====
    def __slot__startConversion(self):
        if self.tbl_fileList.rowCount() == 0:
            return

        invalidCharacters = set('<>:"/\\|?*')
        for row in range(self.tbl_fileList.rowCount()):
            title = self.tbl_fileList.item(row, GB._TITLECOLUMN_).text().strip()
            if not title or title in (".", "..") or any(char in invalidCharacters for char in title):
                self.tbl_fileList.selectRow(row)
                QMessageBox.warning(
                    self,
                    _INVALID_TITLE_TITLE,
                    _INVALID_TITLE_TEXT.format(file_name=title or "(empty)"),
                )
                return

        self.converting = True
        self.startNextConversionAfterThread = False
        self.btn_addFile.setDisabled(True)
        self.btn_clearList.setDisabled(True)
        self.btn_convert.setDisabled(True)
        self.btn_destinationPath.setDisabled(True)
        self.tbl_fileList.hide()

        self.btn_stopConversion.setDisabled(False)
        self.btn_stopConversion.show()
        self.btn_done.setDisabled(True)
        self.tbl_conversion.show()

        for row in range(self.tbl_fileList.rowCount()):
            self.tbl_conversion.insertRow(row)
            title = self.tbl_fileList.item(row, GB._TITLECOLUMN_).text().strip() + ".mp3"
            self.tbl_conversion.setItem(row, 0, QTableWidgetItem(title))
            self.tbl_conversion.item(row, 0).setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            self.tbl_conversion.item(row, 0).setForeground(QBrush(QColor(0, 0, 0)))

            conversionInProgress = QProgressBar()
            conversionInProgress.setMaximum(0)
            conversionInProgress.setMinimum(0)
            conversionInProgress.setValue(0)
            self.tbl_conversion.setCellWidget(row, 1, conversionInProgress)

        self.tbl_conversion.resizeColumnsToContents()
        self.conversionIndex = 0
        self.sendNextItemToConversion()

    def __slot__updateConversionProgress(self, result, wasCancelled):
        self.tbl_conversion.removeCellWidget(self.conversionIndex, 1)
        if wasCancelled:
            strResult = "Stopped"
        elif result:
            strResult = "Done!"
        else:
            strResult = "Error!"

        self.tbl_conversion.setItem(self.conversionIndex, 1, QTableWidgetItem(strResult))
        self.tbl_conversion.item(self.conversionIndex, 1).setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        )
        self.tbl_conversion.item(self.conversionIndex, 1).setForeground(QBrush(QColor(0, 0, 0)))
        self.tbl_conversion.item(self.conversionIndex, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if wasCancelled:
            for row in range(self.conversionIndex + 1, self.tbl_conversion.rowCount()):
                self.tbl_conversion.removeCellWidget(row, 1)
                self.tbl_conversion.setItem(row, 1, QTableWidgetItem("Stopped"))
                self.tbl_conversion.item(row, 1).setFlags(
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                )
                self.tbl_conversion.item(row, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.startNextConversionAfterThread = False
            self.conversionFinished()
            return

        self.conversionIndex += 1
        self.startNextConversionAfterThread = self.conversionIndex < self.tbl_conversion.rowCount()
        if not self.startNextConversionAfterThread:
            self.conversionFinished()

    def sendNextItemToConversion(self):
        if(self.conversionIndex < self.tbl_conversion.rowCount()):
            title = self.tbl_fileList.item(self.conversionIndex, GB._TITLECOLUMN_).text().strip()
            filePath = self.tbl_fileList.item(self.conversionIndex, GB._ORIGINALPATH_).text()
            bitRate = self.tbl_fileList.cellWidget(self.conversionIndex, GB._BITRATE_).currentText()
            fc = self.tbl_fileList.cellWidget(self.conversionIndex, GB._SAMPLERATE_).currentText()
            tags = self.tbl_fileList.item(self.conversionIndex, GB._HIDDENTAGS_).text()

            self.conversionThread = ConversionThread(self, title, filePath, bitRate, fc, tags, self.entry_destinationPath.text())
            currentThread = self.conversionThread
            currentThread.completed.connect(self.__slot__updateConversionProgress)
            currentThread.finished.connect(lambda: self.__slot__conversionThreadFinished(currentThread))
            currentThread.finished.connect(currentThread.deleteLater)
            currentThread.start()
        else:
            self.conversionFinished()

    def __slot__conversionThreadFinished(self, finishedThread):
        if self.conversionThread is finishedThread:
            self.conversionThread = None

        if self.closeRequested:
            QTimer.singleShot(0, self.close)
            return

        if self.startNextConversionAfterThread:
            self.startNextConversionAfterThread = False
            self.sendNextItemToConversion()
            return

        QTimer.singleShot(0, self.showPendingUpdate)

    def conversionFinished(self):
        self.converting = False
        self.btn_stopConversion.hide()
        self.btn_done.setDisabled(False)
        self.btn_done.show()

    def __slot__resetAndStayReady(self):
        n_of_row = self.tbl_fileList.rowCount()
        for _ in range(n_of_row):
            self.tbl_fileList.removeRow(0)
            self.tbl_conversion.removeRow(0)
        self.__slot__resizeTableAndCheckButtons()

        self.tbl_conversion.hide()
        self.btn_addFile.setDisabled(False)
        self.btn_clearList.setDisabled(True)
        self.btn_convert.setDisabled(True)
        self.btn_destinationPath.setDisabled(False)
        self.tbl_fileList.show()
        self.btn_done.hide()
        self.conversionIndex = 0

    # function that is called when the stop conversion button is clicked
    def __slot__stopConversion(self):
        if self.conversionThread is not None and self.conversionThread.isRunning():
            self.btn_stopConversion.setDisabled(True)
            self.conversionThread.cancel()
            QTimer.singleShot(2000, self.__slot__forceStopConversion)

    def __slot__forceStopConversion(self):
        if self.conversionThread is not None and self.conversionThread.isRunning():
            self.conversionThread.forceKill()

    # start a thread to add the files to the table
    def startThreadForAddingSongToList(self, file_list):
        if len(file_list) > 0:
            self.loadThread = FileLoadThread(self, file_list, self.tbl_fileList.rowCount())
            currentThread = self.loadThread
            currentThread.data.connect(self.__slot__addToTable)
            currentThread.invalidFile.connect(self.__slot__invalidFile)
            currentThread.completed.connect(self.__slot__addFilesFinished)
            currentThread.finished.connect(lambda: self.__slot__loadThreadFinished(currentThread))
            currentThread.finished.connect(currentThread.deleteLater)
            currentThread.start()

            self.uploading = True
            self.progressBar.show()
            self.tbl_fileList.setDisabled(True)
            self.btn_addFile.setDisabled(True)
            self.btn_clearList.setDisabled(True)
            self.btn_convert.setDisabled(True)
            self.btn_destinationPath.setDisabled(True)


    # FUTURE RELEASE
    #def __slot__clearQueue(self):
    #    count = self.tbl_conversion.rowCount()
    #    index = 1
    #    for i in range(count):
    #        try:
    #            if(self.tbl_conversion.item(i, 1).text() == "Done"):
    #                index = index + 1
    #        except:
    #            self.tbl_conversion.removeRow(index)
    #            self.tbl_fileList.removeRow(index)
