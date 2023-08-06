from enum import Enum

from qtpy.QtWidgets import QPushButton
from qtpy.QtWidgets import QHBoxLayout, QWidget, QFileDialog
from qtpy.QtCore import Signal
from typing import List


class FileInputMode(Enum):
    DIRECTORY = "dir"
    FILE = "file"
    CSV = "csv"
    JSONCSV = "jsoncsv"
    JSON = "json"


class FileInput(QWidget):
    """
    A file input Widget that includes a file dialog for selecting a file / directory
    and a text box to display the selected file
    inputs:
        mode (FileInputMode): file dialog selection type to File, Directory, Csv, JSON/Csv, or JSON .
        initial_text (str): text to display in the widget before a file has been selected
    """

    file_selected = Signal(list)
    selected_file: List[str] = None

    def __init__(
        self,
        parent: QWidget = None,
        mode: FileInputMode = FileInputMode.FILE,
        placeholder_text: str = None,
    ):
        super().__init__(parent)
        self._mode = mode

        self._input_btn = QPushButton(placeholder_text)
        self._input_btn.clicked.connect(self._select_file)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._input_btn)
        self.setLayout(layout)

    @property
    def mode(self) -> FileInputMode:
        return self._mode

    def simulate_click(self):
        """Simulate a click event to open the file dialog."""
        self._input_btn.clicked.emit()

    def toggle(self, enabled: bool):
        """
        Enable and un-enable user clicking of the add file button.

        Parameters
        ----------
        enabled : bool
        """
        self._input_btn.setEnabled(enabled)

    def _select_file(self):  # pragma: no-cover
        if self._mode == FileInputMode.FILE:

            file_path, _ = QFileDialog.getOpenFileNames(
                self,
                "Select a file",
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )
        elif self._mode == FileInputMode.DIRECTORY:
            file_path = QFileDialog.getExistingDirectory(
                self,
                "Select a directory",
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )
            if len(file_path) > 0:
                file_path = [file_path]
            else:
                file_path = None
        elif self._mode == FileInputMode.CSV:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Select or create a csv file",
                filter="CSV Files (*.csv)",
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )
            if file_path is None or file_path == "":
                file_path = None
            else:
                file_path = [file_path]
        elif self._mode == FileInputMode.JSON:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Select or create a json file",
                filter="JSON Files (*.json)",
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )
            if file_path is None or file_path == "":
                file_path = None
            else:
                file_path = [file_path]
        else:
            # JSONCSV
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select a .csv or .json file with annotations",
                filter="CSV Files (*.csv) ;; JSON (*.json)",
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )
            if file_path is None or file_path == "":
                file_path = None
            else:
                file_path = [file_path]

        if file_path:
            self.selected_file = file_path
            self.file_selected.emit(file_path)
