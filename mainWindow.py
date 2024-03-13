from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from editTagsWindow import EditTagsWindow
import json
import globalVariables as GB
from fileLoadThread import FileLoadThread
from conversionThread import ConversionThread

class mainWindow(QWidget):
    stopConversionSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.uploading = False # variabile che è True durante la fase di caricamento dei file ed è False normalmente
        
        self.setGeometry(0, 0, 900, 600)
        self.setWindowTitle(GB._APP_NAME_)

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

    # ===== SLOTS =====
    def __slot__addToTable(self, row, column, data):
        if(row >= self.tbl_fileList.rowCount()):
            self.tbl_fileList.insertRow(row)

            # REMOVE BUTTON
            self.tbl_fileList.setCellWidget(row, GB._REMOVECOLUMN_, QPushButton())
            self.tbl_fileList.cellWidget(row, GB._REMOVECOLUMN_).setIcon(QIcon(GB._REMOVE_BTN_IMG_PATH_))
            self.tbl_fileList.cellWidget(row, GB._REMOVECOLUMN_).clicked.connect(self.__slot__removeAction)
            self.tbl_fileList.cellWidget(row, GB._REMOVECOLUMN_).clicked.connect(self.__slot__resizeTableAndCheckButtons) # entrambi gli slot sono connessi

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
            self.tbl_fileList.item(row, column).setFlags(Qt.ItemFlag.ItemIsEditable)

        
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

    def __slot__chooseFilesAndAdd(self):
        choosen_files, _ = QFileDialog().getOpenFileNames(filter=GB._FILE_ALLOWED_) # in python si usa una variabile con il nome "_" per indicare una variabile dove buttare la roba, gli scarti, cose che non ci interessano. In questo caso ad esempio ci buttiamo i filtri dei file che a noi non interessano

        if(len(choosen_files) > 0):
            loadThread = FileLoadThread(self, choosen_files, self.tbl_fileList.rowCount())
            loadThread.data.connect(self.__slot__addToTable)
            loadThread.finished.connect(self.__slot__addFilesFinished)
            loadThread.start()

            self.uploading = True
            self.progressBar.show()
            self.tbl_fileList.setDisabled(True)
            self.btn_addFile.setDisabled(True)
            self.btn_clearList.setDisabled(True)
            self.btn_convert.setDisabled(True)
            self.btn_destinationPath.setDisabled(True)
            
    def __slot__openChoosePathDialog(self):
        last_path = self.entry_destinationPath.text()
        new_path = QFileDialog().getExistingDirectory()

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

        # estraggo le coordinate della mainWindow per posizionare la editTagsWindow di conseguenza
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
        self.tagWin.close()
        self.stopConversionSignal.emit()

    # ===== CONVERSIONS SLOTS =====
    def __slot__startConversion(self):
        if(self.tbl_fileList.rowCount() > 0):
            self.btn_addFile.setDisabled(True)
            self.btn_clearList.setDisabled(True)
            self.btn_convert.setDisabled(True)
            self.btn_destinationPath.setDisabled(True)
            self.tbl_fileList.hide()

            self.btn_stopConversion.show()
            #self.btn_clearQueue.show()
            self.btn_done.setDisabled(True)
            
            self.tbl_conversion.show()

            for row in range(self.tbl_fileList.rowCount()):
                self.tbl_conversion.insertRow(row)
                title = self.tbl_fileList.item(row, GB._TITLECOLUMN_).text() + ".mp3"
                self.tbl_conversion.setItem(row, 0, QTableWidgetItem(title))
                self.tbl_conversion.item(row, 0).setFlags(Qt.ItemFlag.ItemIsEditable)
                self.tbl_conversion.item(row, 0).setForeground(QBrush(QColor(0, 0, 0)))

                conversionInProgress = QProgressBar()
                conversionInProgress.setMaximum(0)
                conversionInProgress.setMinimum(0)
                conversionInProgress.setValue(0)

                self.tbl_conversion.setCellWidget(row, 1, conversionInProgress)
                self.tbl_conversion.resizeColumnsToContents()
    
            self.conversionIndex = 0
            self.sendNextItemToConversion()

    def __slot__updateConversionProgress(self, result):
        self.tbl_conversion.removeCellWidget(self.conversionIndex, 1)
        if result:
            strResult = "Done!"
        else:
            strResult = "Error!"
        
        self.tbl_conversion.setItem(self.conversionIndex, 1, QTableWidgetItem(strResult))
        self.tbl_conversion.item(self.conversionIndex, 1).setFlags(Qt.ItemFlag.ItemIsEditable)
        self.tbl_conversion.item(self.conversionIndex, 1).setForeground(QBrush(QColor(0, 0, 0)))
        self.tbl_conversion.item(self.conversionIndex, 1).setFlags(Qt.ItemFlag.ItemIsEditable)
        self.tbl_conversion.item(self.conversionIndex, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conversionIndex = self.conversionIndex + 1
        self.sendNextItemToConversion()

    def sendNextItemToConversion(self):
        if(self.conversionIndex < self.tbl_conversion.rowCount()):
            title = self.tbl_fileList.item(self.conversionIndex, GB._TITLECOLUMN_).text()
            filePath = self.tbl_fileList.item(self.conversionIndex, GB._ORIGINALPATH_).text()
            bitRate = self.tbl_fileList.cellWidget(self.conversionIndex, GB._BITRATE_).currentText()
            fc = self.tbl_fileList.cellWidget(self.conversionIndex, GB._SAMPLERATE_).currentText()
            tags = self.tbl_fileList.item(self.conversionIndex, GB._HIDDENTAGS_).text()

            conversionThread = ConversionThread(self, title, filePath, bitRate, fc, tags, self.entry_destinationPath.text())
            conversionThread.result.connect(self.__slot__updateConversionProgress)
            self.stopConversionSignal.connect(conversionThread.stopFn)
            conversionThread.stopped.connect(self.__slot__conversionStopped)
            conversionThread.start()
        else:
            self.conversionFinished()

    # funzione chiamata dal thread interrotto
    def __slot__conversionStopped(self):
        # NON SI FERMA!
        for row in range(self.tbl_conversion.rowCount()):
            if(not(self.tbl_conversion.item(row, 1))):
                self.tbl_conversion.removeCellWidget(row, 1)
                self.tbl_conversion.setItem(row, 1, QTableWidgetItem("Stopped"))
                self.tbl_conversion.item(row, 1).setFlags(Qt.ItemFlag.ItemIsEditable)
                self.tbl_conversion.item(row, 1).setForeground(QBrush(QColor(0, 0, 0)))
                self.tbl_conversion.item(row, 1).setFlags(Qt.ItemFlag.ItemIsEditable)
                self.tbl_conversion.item(row, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conversionFinished()

    def conversionFinished(self):
        self.btn_stopConversion.hide()
        #self.btn_clearQueue.hide()
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
        self.btn_clearList.setDisabled(False)
        self.btn_convert.setDisabled(False)
        self.btn_destinationPath.setDisabled(False)
        self.tbl_fileList.show()
        self.btn_done.hide()
        self.conversionIndex = 0

    # funzione che interrompe il thread
    def __slot__stopConversion(self):
        self.stopConversionSignal.emit()

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