from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication
from mainWindow import mainWindow
import globalVariables as GB
import sys

app = QApplication(sys.argv)
app.setApplicationName(GB._APP_NAME_)

myWindow = mainWindow()

# per centrare la finestra
screenGeometry = QGuiApplication.primaryScreen().availableGeometry()
windowGeometry = myWindow.frameGeometry()
windowGeometry.moveCenter(screenGeometry.center())
myWindow.move(windowGeometry.topLeft())

myWindow.show()

if __name__ == "__main__":
    app.exec()