from pathlib import Path

from qtpy.QtWidgets import (
    QListWidgetItem,
    QListWidget,
    QWidget,
    QHBoxLayout,
    QLabel,
    QCheckBox,
)


class FileItem(QListWidgetItem):
    """
    A class used to create custom QListWidgetItems.

    Attributes
    ----------
    file_path: str
        a path to the file.
    Methods
    -------
    get_name() -> str
        returns the basename of the file.
    unhide()
        shows the file name in label.
    """

    def __init__(self, file_path: str, parent: QListWidget, hidden: bool = False):
        QListWidgetItem.__init__(self, parent)
        self._file_path = file_path
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        if hidden:
            self.label = QLabel("Image " + str(parent.row(self) + 1))
        else:
            self.label = QLabel(self._make_display_name())
        self.layout.addWidget(self.label, stretch=19)
        self.check = QCheckBox()
        self.check.setCheckState(False)
        self.check.setCheckable(not hidden)
        self.layout.addWidget(self.check, stretch=1)
        self.layout.addStretch()
        self.layout.setContentsMargins(2, 2, 0, 5)
        self.label.setStyleSheet(
            """
                QLabel{
                    border: 0px solid; 
                }
        """
        )
        self.widget.setLayout(self.layout)
        self.setSizeHint(self.widget.sizeHint())
        if parent is not None:
            parent.setItemWidget(self, self.widget)

    @property
    def file_path(self) -> str:
        return self._file_path

    def get_name(self):
        """Return basename"""
        return Path(self._file_path).stem

    def unhide(self):
        """Display the file name instead of hidden name."""
        self.label.setText(self._make_display_name())
        self.check.setCheckable(True)

    def _make_display_name(self) -> str:
        """
        Truncate long file names

        Returns
        -------
        str
            truncated file name
        """
        # todo change
        path: str = self.get_name()
        if len(path) > 28:
            path = path[0:27] + "..."
        return path

    def highlight(self):
        """highlight item"""
        self.label.setStyleSheet(
            """QLabel{
                            font-weight: bold;
                            text-decoration: underline;
                        }"""
        )

    def unhighlight(self):
        """unhighlight item"""
        self.label.setStyleSheet("""QLabel{}""")

    def __hash__(self):
        return hash(self._file_path)

    def __eq__(self, other):
        """Compares two ListItems file_path attributes"""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._file_path == other._file_path
