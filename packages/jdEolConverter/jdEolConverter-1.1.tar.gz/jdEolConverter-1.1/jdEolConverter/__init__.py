from PyQt6.QtCore import QThread, pyqtSignal, QCoreApplication, QTranslator, QLocale
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QApplication
from PyQt6.QtGui import QIcon
from typing import Optional
from PyQt6 import uic
import stat
import sys
import os
import re


def is_file_hidden(path: str) -> bool:
    try:
        return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    except AttributeError:
        return os.path.basename(path).startswith(".")


class ConvertThread(QThread):
    set_value = pyqtSignal("int")
    set_max = pyqtSignal("int")
    set_text = pyqtSignal("QString")
    def __init__(self):
        QThread.__init__(self)

    def setup(self, eol: str, path: str, regex: Optional[re.Pattern], skip_hidden: bool, recursive: bool):
        self._eol = eol
        self._path = path
        self._regex = regex
        self._skip_hidden = skip_hidden
        self._recursive = recursive

    def _list_files(self, path: str) -> list[str]:
        self.set_text.emit(QCoreApplication.translate("MainWindow", "Searching {{path}}").replace("{{path}}", path))
        file_list = []
        try:
            for i in os.listdir(path):
                full_path = os.path.join(path, i)
                if self._skip_hidden and is_file_hidden(full_path):
                    continue
                if self._recursive and os.path.isdir(full_path):
                    file_list += self._list_files(full_path)
                else:
                    if self._regex:
                        if not self._regex.match(i):
                            continue
                    file_list.append(full_path)
        except Exception:
            print(QCoreApplication.translate("MainWindow", "Could not read {{path}}").replace("{{path}}", path), file=sys.stderr)
        return file_list

    def run(self):
        file_list = self._list_files(self._path)
        self.set_max.emit(len(file_list) - 1)
        for count, i in enumerate(file_list):
            self.set_value.emit(count)
            self.set_text.emit(QCoreApplication.translate("MainWindow", "Converting {{path}}").replace("{{path}}", i))
            try:
                with open(i, "r", encoding="utf-8") as f:
                    text = f.read()
                with open(i, "w", encoding="utf-8", newline=self._eol) as f:
                    f.write(text)
            except Exception:
                print(QCoreApplication.translate("MainWindow", "Could not convert {{path}}").replace("{{path}}", i), file=sys.stderr)
        self.set_text.emit(QCoreApplication.translate("MainWindow", "Finished"))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "MainWindow.ui"), self)

        self._convert_thread = ConvertThread()
        self._convert_thread.set_value.connect(lambda value: self.progress_bar.setValue(value))
        self._convert_thread.set_max.connect(lambda value: self.progress_bar.setMaximum(value))
        self._convert_thread.set_text.connect(lambda text: self.progress_bar.setFormat(text))
        self._convert_thread.started.connect(lambda: self.button_box.setEnabled(False))
        self._convert_thread.finished.connect(lambda: self.button_box.setEnabled(True))

        self.button_browse.clicked.connect(self._button_browse_clicked)
        self.chk_regex.stateChanged.connect(self._update_regex_widgets_enabled)
        self.button_box.clicked.connect(self._ok_button_clicked)

        self._update_regex_widgets_enabled()

        if len(sys.argv) > 1:
            self.edit_path.setText(sys.argv[1])

    def _button_browse_clicked(self):
        path = QFileDialog.getExistingDirectory(self, directory=self.edit_path.text())
        if path != "":
            self.edit_path.setText(path)

    def _update_regex_widgets_enabled(self):
        enabled = self.chk_regex.isChecked()
        self.label_regex.setEnabled(enabled)
        self.edit_regex.setEnabled(enabled)

    def _ok_button_clicked(self):
        if self.edit_path.text() == "":
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "No Directory"), QCoreApplication.translate("MainWindow", "You have not set a Directory"))
            return

        if not os.path.isdir(self.edit_path.text()):
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Not a Directory"), QCoreApplication.translate("MainWindow", "{{path}} is not a Directory").replace("{{path}}", self.edit_path.text()))
            return

        if self.chk_regex.isChecked():
            if self.edit_regex.text() == "":
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "No RegEx"), QCoreApplication.translate("MainWindow", "You have not set a RegEx"))
                return

            try:
                compiled_regex = re.compile(self.edit_regex.text())
            except re.error as error:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Invalid RegEx"), error.msg)
                return
        else:
            compiled_regex = None

        if self.rad_unix.isChecked():
            eol = "\n"
        elif self.rad_windows.isChecked():
            eol = "\r\n"
        elif self.rad_mac.isChecked():
            eol = "\r"

        self._convert_thread.setup(eol, self.edit_path.text(), compiled_regex, self.chk_skip_hidden.isChecked(), self.chk_recursive.isChecked())
        self._convert_thread.start()


def main():
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Icon.svg")))
    app.setDesktopFileName("com.gitlab.JakobDev.jdEolConverter")
    app.setApplicationName("jdEolConverter")

    translator = QTranslator()
    system_language = QLocale.system().name()
    translator.load(os.path.join(os.path.dirname(__file__), "translations", "jdEolConverter_" + system_language.split("_")[0] + ".qm"))
    translator.load(os.path.join(os.path.dirname(__file__), "translations", "jdEolConverter_" + system_language + ".qm"))
    app.installTranslator(translator)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())
