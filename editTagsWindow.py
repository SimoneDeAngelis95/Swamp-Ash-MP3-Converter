from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
import json

_WIN_WIDTH_ = 400
_WIN_HEIGHT_ = 200

class EditTagsWindow(QWidget):
    updateTags = pyqtSignal(int, str) # i segnali vanno sempre definiti fuori dall'init, in questo caso invio l'indice della riga e la stringa con i tag aggiornati
    updateTagsForAll = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Edit Tags")

        self.winTitle = QLabel(self)

        # ===== TITLE =====
        self.inp_title = QLineEdit(self)
        self.lbl_title = QLabel(self)
        self.lbl_title.setText("Title: ")
        self.lbl_title.setBuddy(self.inp_title)

        # ===== TRACK NUMBER =====
        self.inp_number = QLineEdit(self)
        self.lbl_number = QLabel(self)
        self.lbl_number.setText("Track Number: ")
        self.lbl_number.setBuddy(self.inp_number)

        # ===== ARTIST =====
        self.inp_artist = QLineEdit(self)
        self.lbl_artist = QLabel(self)
        self.lbl_artist.setText("Artist: ")
        self.lbl_artist.setBuddy(self.inp_artist)
        self.btn_cpyArtist = QPushButton(self)
        self.btn_cpyArtist.setText("Set for All")

        # ===== ALBUM =====
        self.inp_album = QLineEdit(self)
        self.lbl_album = QLabel(self)
        self.lbl_album.setText("Album: ")
        self.lbl_album.setBuddy(self.inp_album)
        self.btn_cpyAlbum = QPushButton(self)
        self.btn_cpyAlbum.setText("Set for All")

        # ===== YEAR =====
        self.inp_year = QLineEdit(self)
        self.lbl_year = QLabel(self)
        self.lbl_year.setText("Year: ")
        self.lbl_year.setBuddy(self.inp_year)
        self.btn_cpyYear = QPushButton(self)
        self.btn_cpyYear.setText("Set for All")

        # ===== GENRE =====
        self.inp_genre = QLineEdit(self)
        self.lbl_genre = QLabel(self)
        self.lbl_genre.setText("Genre: ")
        self.lbl_genre.setBuddy(self.inp_genre)
        self.btn_cpyGenre = QPushButton(self)
        self.btn_cpyGenre.setText("Set for All")

        # ===== CLOSE BUTTON =====
        self.btn_close = QPushButton(self)
        self.btn_close.setText("Close")
        self.btn_close.clicked.connect(self.closeWin)

        # ===== SAVE BUTTON =====
        self.btn_save = QPushButton(self)
        self.btn_save.setText("Save")
        self.btn_save.clicked.connect(self.saveTags)

        # ===== CLEAR ALL =====
        self.btn_clear = QPushButton(self)
        self.btn_clear.setText("Clear All")
        self.btn_clear.clicked.connect(self.clearAll)

        # ===== LAYOUTS =====
        self.mainVerticalLayout = QVBoxLayout(self)
        self.mainVerticalLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mainVerticalLayout.addWidget(self.winTitle)
        self.winTitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.mainGridLayout = QGridLayout()
        self.mainGridLayout.addWidget(self.lbl_title, 0, 0)
        self.mainGridLayout.addWidget(self.inp_title, 0, 1)

        self.mainGridLayout.addWidget(self.lbl_number, 1, 0)
        self.mainGridLayout.addWidget(self.inp_number, 1, 1)

        self.mainGridLayout.addWidget(self.lbl_artist, 2, 0)
        self.mainGridLayout.addWidget(self.inp_artist, 2, 1)
        self.mainGridLayout.addWidget(self.btn_cpyArtist, 2, 2)
        self.btn_cpyArtist.clicked.connect(self.copyOptionForAll)

        self.mainGridLayout.addWidget(self.lbl_album, 3, 0)
        self.mainGridLayout.addWidget(self.inp_album, 3, 1)
        self.mainGridLayout.addWidget(self.btn_cpyAlbum, 3, 2)
        self.btn_cpyAlbum.clicked.connect(self.copyOptionForAll)

        self.mainGridLayout.addWidget(self.lbl_year, 4, 0)
        self.mainGridLayout.addWidget(self.inp_year, 4, 1)
        self.mainGridLayout.addWidget(self.btn_cpyYear, 4, 2)
        self.btn_cpyYear.clicked.connect(self.copyOptionForAll)

        self.mainGridLayout.addWidget(self.lbl_genre, 5, 0)
        self.mainGridLayout.addWidget(self.inp_genre, 5, 1)
        self.mainGridLayout.addWidget(self.btn_cpyGenre, 5, 2)
        self.btn_cpyGenre.clicked.connect(self.copyOptionForAll)

        self.mainGridLayout.addWidget(self.btn_close, 6, 0)
        self.mainGridLayout.addWidget(self.btn_save, 6, 1)
        self.mainGridLayout.addWidget(self.btn_clear, 6, 2)

        self.mainVerticalLayout.addLayout(self.mainGridLayout)

    def init(self, tagString, x, y, indexSender):

        self.indexSender = indexSender # indice della riga che ha chiamato la funzione

        self.setGeometry(x, y, _WIN_WIDTH_, _WIN_HEIGHT_)

        tags = json.loads(tagString)
        self.winTitle.setText("Edit tags for: " + tags["title"])
        self.inp_title.setText(tags["title"])
        self.inp_number.setText(tags["number"])
        self.inp_artist.setText(tags["artist"])
        self.inp_album.setText(tags["album"])
        self.inp_year.setText(tags["year"])
        self.inp_genre.setText(tags["genre"])

    def saveTags(self):
        tags = {"title": self.inp_title.text(),
                "number": self.inp_number.text(),
                "artist": self.inp_artist.text(),
                "album": self.inp_album.text(),
                "year": self.inp_year.text(),
                "genre": self.inp_genre.text()}
        json_tags = json.dumps(tags)
        self.updateTags.emit(self.indexSender, json_tags)
        self.hide()

    def closeWin(self):
        self.hide()

    def clearAll(self):
        self.inp_title.setText("")
        self.inp_number.setText("")
        self.inp_artist.setText("")
        self.inp_album.setText("")
        self.inp_year.setText("")
        self.inp_genre.setText("")

    def copyOptionForAll(self):
        sender = self.sender()
        if(sender == self.btn_cpyArtist):
            self.updateTagsForAll.emit("artist", self.inp_artist.text())
        elif(sender == self.btn_cpyAlbum):
            self.updateTagsForAll.emit("album", self.inp_album.text())
        elif(sender == self.btn_cpyYear):
            self.updateTagsForAll.emit("year", self.inp_year.text())
        elif(sender == self.btn_cpyGenre):
            self.updateTagsForAll.emit("genre", self.inp_genre.text())